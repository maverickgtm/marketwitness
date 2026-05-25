from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

ACCESS_MODELS = {
    "public_endpoint",
    "public_web_page",
    "public_filing",
    "official_release",
    "commercial_api_candidate",
    "freemium_api",
    "manual_reference",
    "synthetic_demo",
}
INTEGRATION_STATUSES = {"implemented", "manual_verified", "candidate", "excluded"}
LICENSE_STATUSES = {
    "public_access_rules_documented",
    "terms_review_required",
    "manual_download_only",
    "restricted_no_collection",
    "project_owned_synthetic",
}
PUBLICATION_POLICIES = {
    "source_link_and_derived_output",
    "derived_output_pending_terms_review",
    "internal_evaluation_pending_license",
    "source_link_only",
    "synthetic_redistributable",
}
SOURCE_COLUMNS = {
    "provider_id",
    "provider_name",
    "data_class",
    "access_model",
    "integration_status",
    "license_status",
    "publication_policy",
    "official_url",
    "reference_url",
    "reviewed_on",
    "review_note",
}


class SourceRegistryDataError(ValueError):
    """Raised when provider-governance metadata is incomplete or inconsistent."""


@dataclass(frozen=True)
class SourceProvider:
    provider_id: str
    provider_name: str
    data_class: str
    access_model: str
    integration_status: str
    license_status: str
    publication_policy: str
    official_url: str
    reference_url: str
    reviewed_on: date
    review_note: str

    @property
    def deployment_state(self) -> str:
        if self.license_status == "restricted_no_collection":
            return "blocked"
        if self.license_status == "manual_download_only":
            return "manual_only"
        if self.publication_policy == "internal_evaluation_pending_license":
            return "license_required"
        if self.license_status == "terms_review_required":
            return "review_required"
        return "usable_with_policy"


def load_source_registry(path: str | Path) -> list[SourceProvider]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        missing = sorted(SOURCE_COLUMNS - set(reader.fieldnames or []))
        if missing:
            raise SourceRegistryDataError(
                f"{path}: missing columns: {', '.join(missing)}"
            )
        providers: list[SourceProvider] = []
        seen: set[str] = set()
        for index, row in enumerate(reader, start=2):
            provider_id = row["provider_id"].strip()
            access = row["access_model"].strip()
            integration = row["integration_status"].strip()
            license_status = row["license_status"].strip()
            publication = row["publication_policy"].strip()
            if not provider_id or provider_id in seen:
                raise SourceRegistryDataError(
                    f"{path}: blank or duplicate provider id on row {index}"
                )
            if access not in ACCESS_MODELS:
                raise SourceRegistryDataError(f"{path}: invalid access model on row {index}")
            if integration not in INTEGRATION_STATUSES:
                raise SourceRegistryDataError(
                    f"{path}: invalid integration status on row {index}"
                )
            if license_status not in LICENSE_STATUSES:
                raise SourceRegistryDataError(f"{path}: invalid license status on row {index}")
            if publication not in PUBLICATION_POLICIES:
                raise SourceRegistryDataError(
                    f"{path}: invalid publication policy on row {index}"
                )
            try:
                reviewed_on = date.fromisoformat(row["reviewed_on"].strip())
            except ValueError as exc:
                raise SourceRegistryDataError(f"{path}: invalid review date on row {index}") from exc
            required = [
                row["provider_name"].strip(),
                row["data_class"].strip(),
                row["official_url"].strip(),
                row["reference_url"].strip(),
                row["review_note"].strip(),
            ]
            if not all(required):
                raise SourceRegistryDataError(f"{path}: missing content on row {index}")
            if not row["official_url"].strip().startswith("https://") or not row[
                "reference_url"
            ].strip().startswith("https://"):
                raise SourceRegistryDataError(f"{path}: non-HTTPS URL on row {index}")
            if integration == "implemented" and license_status == "restricted_no_collection":
                raise SourceRegistryDataError(
                    f"{path}: restricted provider cannot be implemented on row {index}"
                )
            if access == "synthetic_demo" and (
                license_status != "project_owned_synthetic"
                or publication != "synthetic_redistributable"
            ):
                raise SourceRegistryDataError(
                    f"{path}: synthetic data requires project-owned policy on row {index}"
                )
            seen.add(provider_id)
            providers.append(
                SourceProvider(
                    provider_id=provider_id,
                    provider_name=row["provider_name"].strip(),
                    data_class=row["data_class"].strip(),
                    access_model=access,
                    integration_status=integration,
                    license_status=license_status,
                    publication_policy=publication,
                    official_url=row["official_url"].strip(),
                    reference_url=row["reference_url"].strip(),
                    reviewed_on=reviewed_on,
                    review_note=row["review_note"].strip(),
                )
            )
        return providers


def render_source_registry_report(providers: list[SourceProvider], as_of: date) -> str:
    _validate_as_of(providers, as_of)
    integration = Counter(provider.integration_status for provider in providers)
    deployment = Counter(provider.deployment_state for provider in providers)
    lines = [
        "# Source Governance Registry",
        "",
        f"- Reviewed as of: `{as_of.isoformat()}`",
        f"- Providers recorded: `{len(providers)}`",
        f"- Implemented integrations: `{integration['implemented']}`",
        f"- Terms or license reviews outstanding: `{deployment['review_required'] + deployment['license_required']}`",
        f"- Manual-download-only integrations: `{deployment['manual_only']}`",
        f"- Blocked from automated collection: `{deployment['blocked']}`",
        "",
        "This registry controls ingestion and publication decisions. A public URL",
        "does not by itself grant redistribution rights. Records marked for terms",
        "or license review cannot supply a public real-data scorecard yet.",
        "",
        "## Provider Controls",
        "",
        "| Provider | Data Class | Integration | Deployment State | Publication Policy | Source |",
        "|---|---|---|---|---|---|",
    ]
    for provider in providers:
        lines.append(
            f"| {provider.provider_name} | {provider.data_class} | "
            f"`{provider.integration_status}` | `{provider.deployment_state}` | "
            f"`{provider.publication_policy}` | "
            f"[Source]({provider.official_url}) |"
        )
    lines.extend(["", "## Review Notes", ""])
    for provider in providers:
        lines.extend(
            [
                f"### {provider.provider_name}",
                "",
                f"- Access model: `{provider.access_model}`",
                f"- License status: `{provider.license_status}`",
                f"- Reference: [{provider.reference_url}]({provider.reference_url})",
                f"- Note: {provider.review_note}",
                "",
            ]
        )
    return "\n".join(lines)


def write_source_registry_report(
    path: str | Path, providers: list[SourceProvider], as_of: date
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_source_registry_report(providers, as_of), encoding="utf-8")


def render_source_registry_html(providers: list[SourceProvider], as_of: date) -> str:
    _validate_as_of(providers, as_of)
    integration = Counter(provider.integration_status for provider in providers)
    deployment = Counter(provider.deployment_state for provider in providers)
    rows = "".join(
        "<tr>"
        f'<td data-label="Provider"><strong>{escape(provider.provider_name)}</strong><small>{escape(provider.data_class)}</small></td>'
        f'<td data-label="Integration"><span class="badge {escape(provider.integration_status)}">{escape(provider.integration_status)}</span></td>'
        f'<td data-label="Release state"><span class="state {escape(provider.deployment_state)}">{escape(provider.deployment_state)}</span></td>'
        f'<td data-label="Publication"><small>{escape(provider.publication_policy)}</small></td>'
        f'<td data-label="Evidence"><a href="{escape(provider.official_url)}">Source</a><small><a href="{escape(provider.reference_url)}">Policy / reference</a></small></td>'
        "</tr>"
        for provider in providers
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | Source Governance</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;--red:#ff7d72;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1200px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:840px}}.cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}td small{{display:block;color:var(--muted);max-width:250px}}a{{color:var(--mint);text-decoration:none}}.badge,.state{{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}.implemented,.usable_with_policy{{color:var(--mint);background:rgba(86,218,172,.12)}}.manual_verified,.review_required,.manual_only{{color:var(--gold);background:rgba(240,188,98,.12)}}.candidate,.license_required{{color:var(--blue);background:rgba(98,166,255,.12)}}.excluded,.blocked{{color:var(--red);background:rgba(255,125,114,.12)}}
@media(max-width:840px){{.cards{{grid-template-columns:repeat(2,1fr)}}.table-wrap{{background:transparent;border:0;overflow:visible}}thead{{display:none}}table,tbody,tr,td{{display:block;width:100%}}tr{{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin-bottom:14px;padding:10px 15px}}td{{border:0;padding:9px 0 9px 120px;min-height:39px;position:relative}}td::before{{content:attr(data-label);position:absolute;left:0;top:10px;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.06em}}}}
</style></head><body><header><nav>TargetAudit / Governance / Sources</nav>
<h1>Open code.<br>Controlled data.</h1><p class="lead">A registry of the providers considered by TargetAudit, showing what is connected and what still requires terms or license review before public use.</p>
<p class="meta">Reviewed as of {escape(as_of.isoformat())}</p><section class="cards"><article class="card"><p>Providers</p><strong>{len(providers)}</strong></article><article class="card"><p>Implemented</p><strong>{integration['implemented']}</strong></article><article class="card"><p>Reviews open</p><strong>{deployment['review_required'] + deployment['license_required']}</strong></article><article class="card"><p>Manual only</p><strong>{deployment['manual_only']}</strong></article><article class="card"><p>Blocked</p><strong>{deployment['blocked']}</strong></article></section></header>
<main><p class="notice">Public accessibility is not a license to republish a dataset. Sources marked review_required or license_required cannot supply a public real-data scorecard until their use is approved; manual_only sources cannot be automatically collected.</p>
<h2>Provider controls</h2><div class="table-wrap"><table><thead><tr><th>Provider</th><th>Integration</th><th>Release state</th><th>Publication</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_source_registry_html(
    path: str | Path, providers: list[SourceProvider], as_of: date
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_source_registry_html(providers, as_of), encoding="utf-8")


def _validate_as_of(providers: list[SourceProvider], as_of: date) -> None:
    if any(provider.reviewed_on > as_of for provider in providers):
        raise SourceRegistryDataError(
            "Source registry includes a provider review after the report cutoff."
        )
