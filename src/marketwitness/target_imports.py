from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from .models import TargetObservation

REQUIRED_FIELDS = {
    "record_id",
    "ticker",
    "company_name",
    "firm",
    "published_date",
    "price_target",
    "source_url",
}
OPTIONAL_FIELDS = {"analyst", "rating", "sector", "horizon_days", "benchmark_symbol"}


class TargetImportDataError(ValueError):
    """Raised when an authorized target export cannot be audited safely."""


@dataclass(frozen=True)
class TargetImportManifest:
    provider_id: str
    provider_name: str
    source_provider: str
    exported_on: date
    obtained_via: str
    license_reference: str
    authorized_for_internal_research: bool
    authorized_for_public_output: bool
    field_map: dict[str, str]
    defaults: dict[str, str]

    @property
    def public_state(self) -> str:
        return "declared_allowed" if self.authorized_for_public_output else "internal_only"


@dataclass(frozen=True)
class TargetImportDecision:
    export_record_id: str
    observation_id: str
    ticker: str
    firm: str
    status: str
    reason: str
    source_url: str


def load_target_import_manifest(path: str | Path) -> TargetImportManifest:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TargetImportDataError(f"Unable to read import manifest {path}.") from exc
    if not isinstance(payload, dict):
        raise TargetImportDataError("Target import manifest must be a JSON object.")
    required = {
        "provider_id",
        "provider_name",
        "source_provider",
        "exported_on",
        "obtained_via",
        "license_reference",
        "authorized_for_internal_research",
        "authorized_for_public_output",
        "field_map",
        "defaults",
    }
    if not required.issubset(payload):
        raise TargetImportDataError("Target import manifest is missing required controls.")
    if payload["authorized_for_internal_research"] is not True:
        raise TargetImportDataError("Import manifest does not authorize internal research use.")
    if not isinstance(payload["authorized_for_public_output"], bool):
        raise TargetImportDataError("Manifest public-output declaration must be boolean.")
    field_map = payload["field_map"]
    defaults = payload["defaults"]
    if not isinstance(field_map, dict) or not REQUIRED_FIELDS.issubset(field_map):
        raise TargetImportDataError("Import manifest is missing required field mappings.")
    if not isinstance(defaults, dict):
        raise TargetImportDataError("Import manifest defaults must be an object.")
    try:
        exported_on = date.fromisoformat(str(payload["exported_on"]))
    except ValueError as exc:
        raise TargetImportDataError("Import manifest has an invalid export date.") from exc
    text_values = [
        str(payload[key]).strip()
        for key in (
            "provider_id",
            "provider_name",
            "source_provider",
            "obtained_via",
            "license_reference",
        )
    ]
    if not all(text_values) or not _is_https(text_values[-1]):
        raise TargetImportDataError("Import manifest requires provider data and HTTPS license reference.")
    mapped = {str(key): str(value).strip() for key, value in field_map.items()}
    if any(not column for column in mapped.values()):
        raise TargetImportDataError("Import manifest contains a blank field mapping.")
    return TargetImportManifest(
        provider_id=text_values[0],
        provider_name=text_values[1],
        source_provider=text_values[2],
        exported_on=exported_on,
        obtained_via=text_values[3],
        license_reference=text_values[4],
        authorized_for_internal_research=True,
        authorized_for_public_output=payload["authorized_for_public_output"],
        field_map=mapped,
        defaults={str(key): str(value).strip() for key, value in defaults.items()},
    )


def import_authorized_targets(
    export_path: str | Path, manifest: TargetImportManifest, as_of: date
) -> tuple[list[TargetObservation], list[TargetImportDecision]]:
    if manifest.exported_on > as_of:
        raise TargetImportDataError("Import manifest export date is after the report cutoff.")
    try:
        source = Path(export_path).open(newline="", encoding="utf-8")
    except OSError as exc:
        raise TargetImportDataError(f"Unable to read target export {export_path}.") from exc
    with source:
        reader = csv.DictReader(source)
        columns = set(reader.fieldnames or [])
        mapped_columns = {manifest.field_map[key] for key in REQUIRED_FIELDS}
        missing = sorted(mapped_columns - columns)
        if missing:
            raise TargetImportDataError(
                f"{export_path}: missing mapped export columns: {', '.join(missing)}"
            )
        observations: list[TargetObservation] = []
        decisions: list[TargetImportDecision] = []
        seen: set[str] = set()
        for row in reader:
            record_id = _field(row, manifest, "record_id")
            observation_id = f"{manifest.provider_id}:{record_id}" if record_id else ""
            ticker = _field(row, manifest, "ticker").upper()
            firm = _field(row, manifest, "firm")
            source_url = _field(row, manifest, "source_url")
            reason = _invalid_reason(row, manifest, record_id, seen)
            if reason:
                decisions.append(
                    TargetImportDecision(
                        record_id,
                        observation_id,
                        ticker,
                        firm,
                        "rejected",
                        reason,
                        source_url,
                    )
                )
                if record_id:
                    seen.add(record_id)
                continue
            seen.add(record_id)
            observation = TargetObservation(
                observation_id=observation_id,
                ticker=ticker,
                company_name=_field(row, manifest, "company_name"),
                sector=_field_or_default(row, manifest, "sector"),
                firm=firm,
                analyst=_field_or_default(row, manifest, "analyst"),
                published_date=date.fromisoformat(_field(row, manifest, "published_date")),
                price_target=Decimal(_field(row, manifest, "price_target")),
                rating=_field_or_default(row, manifest, "rating"),
                horizon_days=int(_field_or_default(row, manifest, "horizon_days") or "365"),
                benchmark_symbol=_field_or_default(row, manifest, "benchmark_symbol").upper(),
                source_provider=manifest.source_provider,
                source_url=source_url,
                provider_id=manifest.provider_id,
            )
            observations.append(observation)
            decisions.append(
                TargetImportDecision(
                    record_id,
                    observation_id,
                    ticker,
                    firm,
                    "accepted",
                    "",
                    source_url,
                )
            )
    return observations, decisions


def _invalid_reason(
    row: dict[str, str], manifest: TargetImportManifest, record_id: str, seen: set[str]
) -> str:
    if not record_id:
        return "missing_record_id"
    if record_id in seen:
        return "duplicate_record_id"
    if not _field(row, manifest, "ticker"):
        return "missing_ticker"
    if not _field(row, manifest, "company_name"):
        return "missing_company_name"
    if not _field(row, manifest, "firm"):
        return "missing_firm"
    try:
        published = date.fromisoformat(_field(row, manifest, "published_date"))
    except ValueError:
        return "invalid_published_date"
    if published > manifest.exported_on:
        return "published_after_export"
    try:
        target = Decimal(_field(row, manifest, "price_target"))
    except InvalidOperation:
        return "invalid_price_target"
    if not target.is_finite() or target <= 0:
        return "invalid_price_target"
    if not _is_https(_field(row, manifest, "source_url")):
        return "missing_or_invalid_source_url"
    horizon = _field_or_default(row, manifest, "horizon_days") or "365"
    try:
        if int(horizon) <= 0:
            return "invalid_horizon_days"
    except ValueError:
        return "invalid_horizon_days"
    return ""


def write_normalized_targets(path: str | Path, observations: list[TargetObservation]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "observation_id",
        "ticker",
        "company_name",
        "sector",
        "firm",
        "analyst",
        "published_date",
        "price_target",
        "rating",
        "horizon_days",
        "benchmark_symbol",
        "source_provider",
        "source_url",
        "provider_id",
    ]
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=columns)
        writer.writeheader()
        for item in observations:
            writer.writerow(
                {
                    "observation_id": item.observation_id,
                    "ticker": item.ticker,
                    "company_name": item.company_name,
                    "sector": item.sector,
                    "firm": item.firm,
                    "analyst": item.analyst,
                    "published_date": item.published_date.isoformat()
                    if item.published_date
                    else "",
                    "price_target": str(item.price_target) if item.price_target is not None else "",
                    "rating": item.rating,
                    "horizon_days": item.horizon_days or "",
                    "benchmark_symbol": item.benchmark_symbol,
                    "source_provider": item.source_provider,
                    "source_url": item.source_url,
                    "provider_id": item.provider_id,
                }
            )


def write_import_audit(path: str | Path, decisions: list[TargetImportDecision]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(TargetImportDecision.__annotations__))
        writer.writeheader()
        for item in decisions:
            writer.writerow(item.__dict__)


def render_import_report(
    manifest: TargetImportManifest, decisions: list[TargetImportDecision], as_of: date
) -> str:
    counts = Counter(item.status for item in decisions)
    lines = [
        "# Authorized Target Export Import",
        "",
        f"- Provider declared: `{manifest.provider_name}`",
        f"- Exported on: `{manifest.exported_on.isoformat()}`",
        f"- Imported as of: `{as_of.isoformat()}`",
        f"- Rows accepted: `{counts['accepted']}`",
        f"- Rows rejected: `{counts['rejected']}`",
        f"- Public output declaration: `{manifest.public_state}`",
        f"- License reference: <{manifest.license_reference}>",
        "",
        "This importer accepts a supplied provider export only when its manifest",
        "declares internal research authorization and identifies a license",
        "reference. It does not prove redistribution rights or acquire data.",
        "",
        "## Row Audit",
        "",
        "| Export Record | Ticker | Firm | Status | Reason | Evidence |",
        "|---|---|---|---|---|---|",
    ]
    for item in decisions:
        evidence = f"[Source]({item.source_url})" if item.source_url else "-"
        lines.append(
            f"| {item.export_record_id or '-'} | {item.ticker or '-'} | "
            f"{item.firm or '-'} | `{item.status}` | `{item.reason or '-'}` | {evidence} |"
        )
    return "\n".join(lines) + "\n"


def write_import_report(
    path: str | Path,
    manifest: TargetImportManifest,
    decisions: list[TargetImportDecision],
    as_of: date,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_import_report(manifest, decisions, as_of), encoding="utf-8")


def render_import_html(
    manifest: TargetImportManifest, decisions: list[TargetImportDecision], as_of: date
) -> str:
    counts = Counter(item.status for item in decisions)
    rows = "".join(
        "<tr>"
        f'<td data-label="Record / Ticker"><strong>{escape(item.export_record_id or "-")}</strong><small>{escape(item.ticker or "-")}</small></td>'
        f'<td data-label="Firm">{escape(item.firm or "-")}</td>'
        f'<td data-label="Result"><span class="badge {escape(item.status)}">{escape(item.status)}</span></td>'
        f'<td data-label="Reason">{escape(item.reason or "Validated and normalized")}</td>'
        "</tr>"
        for item in decisions
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarketWitness | Target Import Audit</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--red:#ff7d72;--blue:#62a6ff;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1120px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:800px}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:34px;color:var(--mint);display:block}}.card .restricted{{color:var(--gold);font-size:25px}}.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}td small{{display:block;color:var(--muted)}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}.badge{{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px}}.accepted{{color:var(--mint);background:rgba(86,218,172,.12)}}.rejected{{color:var(--red);background:rgba(255,125,114,.12)}}a{{color:var(--mint)}}
@media(max-width:720px){{.cards{{grid-template-columns:1fr}}.table-wrap{{background:transparent;border:0;overflow:visible}}thead{{display:none}}table,tbody,tr,td{{display:block;width:100%}}tr{{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin-bottom:14px;padding:10px 15px}}td{{border:0;padding:9px 0 9px 132px;min-height:39px;position:relative;overflow-wrap:anywhere}}td::before{{content:attr(data-label);position:absolute;left:0;top:10px;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.06em}}}}
</style></head><body><header><nav><a href="/dashboard/reports">Report Center</a> / <a href="/dashboard/financials-evidence">Financials Evidence Center</a> / Target Import</nav>
<h1>Authorized input.<br>Audited rows.</h1><p class="lead">A controlled import from <strong>{escape(manifest.provider_name)}</strong>, retaining evidence and rejecting unusable observations before scoring.</p>
<p class="meta">Exported {manifest.exported_on.isoformat()} / Reviewed {as_of.isoformat()}</p><section class="cards"><article class="card"><p>Accepted</p><strong>{counts['accepted']}</strong></article><article class="card"><p>Rejected</p><strong>{counts['rejected']}</strong></article><article class="card"><p>Public output</p><strong class="restricted">{escape(manifest.public_state)}</strong></article></section></header>
<main><p class="notice">A manifest declaration permits this import for its stated purpose; it does not itself prove permission to publish provider data or public rankings. License review remains required before public use.</p>
<h2>Row audit</h2><div class="table-wrap"><table><thead><tr><th>Record / Ticker</th><th>Firm</th><th>Result</th><th>Reason</th></tr></thead><tbody>{rows}</tbody></table></div>
<p><a href="{escape(manifest.license_reference)}">Declared license reference</a></p></main></body></html>"""


def write_import_html(
    path: str | Path,
    manifest: TargetImportManifest,
    decisions: list[TargetImportDecision],
    as_of: date,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_import_html(manifest, decisions, as_of), encoding="utf-8")


def _field(row: dict[str, str], manifest: TargetImportManifest, key: str) -> str:
    return row.get(manifest.field_map[key], "").strip()


def _field_or_default(
    row: dict[str, str], manifest: TargetImportManifest, key: str
) -> str:
    column = manifest.field_map.get(key)
    value = row.get(column, "").strip() if column else ""
    return value or manifest.defaults.get(key, "")


def _is_https(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)
