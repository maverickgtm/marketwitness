from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

from .scorecard_readiness import NON_PRODUCTION_PROVIDER_IDS, REQUIREMENTS
from .source_registry import SourceProvider

APPROVAL_COLUMNS = {
    "provider_id",
    "approval_status",
    "priority",
    "requested_use",
    "required_evidence",
    "promotion_criteria",
    "evidence_url",
    "reviewed_on",
    "review_note",
}
APPROVAL_STATUSES = {
    "pending_terms_review",
    "pending_license_quote",
    "pending_written_permission",
    "approved_public_output",
    "rejected_public_output",
}
PRIORITIES = {"critical", "high", "normal"}
SCORECARD_DATA_CLASSES = {requirement.data_class for requirement in REQUIREMENTS}


class ProviderApprovalDataError(ValueError):
    """Raised when a provider approval record cannot support a governed decision."""


@dataclass(frozen=True)
class ProviderApprovalRecord:
    provider_id: str
    approval_status: str
    priority: str
    requested_use: str
    required_evidence: str
    promotion_criteria: str
    evidence_url: str
    reviewed_on: date
    review_note: str


def load_provider_approvals(path: str | Path) -> list[ProviderApprovalRecord]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        missing = sorted(APPROVAL_COLUMNS - set(reader.fieldnames or []))
        if missing:
            raise ProviderApprovalDataError(
                f"{path}: missing columns: {', '.join(missing)}"
            )
        records: list[ProviderApprovalRecord] = []
        seen: set[str] = set()
        for index, row in enumerate(reader, start=2):
            provider_id = row["provider_id"].strip()
            status = row["approval_status"].strip()
            priority = row["priority"].strip()
            if not provider_id or provider_id in seen:
                raise ProviderApprovalDataError(
                    f"{path}: blank or duplicate provider id on row {index}"
                )
            if status not in APPROVAL_STATUSES:
                raise ProviderApprovalDataError(
                    f"{path}: invalid approval status on row {index}"
                )
            if priority not in PRIORITIES:
                raise ProviderApprovalDataError(
                    f"{path}: invalid approval priority on row {index}"
                )
            content = [
                row["requested_use"].strip(),
                row["required_evidence"].strip(),
                row["promotion_criteria"].strip(),
                row["evidence_url"].strip(),
                row["review_note"].strip(),
            ]
            if not all(content):
                raise ProviderApprovalDataError(f"{path}: missing content on row {index}")
            if not row["evidence_url"].strip().startswith("https://"):
                raise ProviderApprovalDataError(
                    f"{path}: evidence URL must be HTTPS on row {index}"
                )
            try:
                reviewed_on = date.fromisoformat(row["reviewed_on"].strip())
            except ValueError as exc:
                raise ProviderApprovalDataError(
                    f"{path}: invalid review date on row {index}"
                ) from exc
            seen.add(provider_id)
            records.append(
                ProviderApprovalRecord(
                    provider_id=provider_id,
                    approval_status=status,
                    priority=priority,
                    requested_use=content[0],
                    required_evidence=content[1],
                    promotion_criteria=content[2],
                    evidence_url=content[3],
                    reviewed_on=reviewed_on,
                    review_note=content[4],
                )
            )
        return records


def build_approval_queue(
    providers: list[SourceProvider],
    approvals: list[ProviderApprovalRecord],
    as_of: date,
) -> dict[str, Any]:
    providers_by_id = {provider.provider_id: provider for provider in providers}
    items = []
    for approval in approvals:
        if approval.reviewed_on > as_of:
            raise ProviderApprovalDataError(
                "Provider approval includes a review after the queue cutoff."
            )
        provider = providers_by_id.get(approval.provider_id)
        if provider is None:
            raise ProviderApprovalDataError(
                f"Approval references unknown provider: {approval.provider_id}."
            )
        if provider.provider_id in NON_PRODUCTION_PROVIDER_IDS:
            raise ProviderApprovalDataError(
                "Demo-only providers cannot enter the production approval queue."
            )
        if (
            approval.approval_status == "approved_public_output"
            and (
                provider.deployment_state != "usable_with_policy"
                or provider.integration_status not in {"implemented", "manual_verified"}
            )
        ):
            raise ProviderApprovalDataError(
                f"Approval for {provider.provider_id} conflicts with source governance or integration state."
            )
        items.append(_queue_item(provider, approval))
    counts = Counter(item["approval_status"] for item in items)
    critical_open = sum(
        item["priority"] == "critical" and not item["promotion_ready"]
        for item in items
    )
    controls = [
        _requirement_control(requirement.label, requirement.data_class, items)
        for requirement in REQUIREMENTS
    ]
    activation_ready = all(control["status"] == "approved" for control in controls)
    return {
        "market_focus": "U.S. Financials",
        "as_of": as_of.isoformat(),
        "queue_count": len(items),
        "critical_open_count": critical_open,
        "approved_count": counts["approved_public_output"],
        "pending_count": sum(
            item["approval_status"].startswith("pending_") for item in items
        ),
        "public_activation_ready": activation_ready,
        "publication_note": (
            "Approval records document required permission work; they do not change "
            "source governance automatically. Public activation requires at least one "
            "approved provider for every scorecard control."
        ),
        "controls": controls,
        "items": sorted(items, key=_queue_sort_key),
    }


def _queue_item(
    provider: SourceProvider, approval: ProviderApprovalRecord
) -> dict[str, Any]:
    promotion_ready = (
        approval.approval_status == "approved_public_output"
        and provider.deployment_state == "usable_with_policy"
        and provider.integration_status in {"implemented", "manual_verified"}
    )
    return {
        "provider_id": provider.provider_id,
        "provider_name": provider.provider_name,
        "data_class": provider.data_class,
        "deployment_state": provider.deployment_state,
        "integration_status": provider.integration_status,
        "license_status": provider.license_status,
        "approval_status": approval.approval_status,
        "priority": approval.priority,
        "requested_use": approval.requested_use,
        "required_evidence": approval.required_evidence,
        "promotion_criteria": approval.promotion_criteria,
        "evidence_url": approval.evidence_url,
        "reviewed_on": approval.reviewed_on.isoformat(),
        "review_note": approval.review_note,
        "scorecard_critical": provider.data_class in SCORECARD_DATA_CLASSES,
        "promotion_ready": promotion_ready,
    }


def _requirement_control(
    label: str, data_class: str, items: list[dict[str, Any]]
) -> dict[str, Any]:
    candidates = [item for item in items if item["data_class"] == data_class]
    approved = [item for item in candidates if item["promotion_ready"]]
    if approved:
        status = "approved"
        blocker = ""
    elif candidates:
        status = "pending_approval"
        blocker = f"{label} has no provider approved for public output."
    else:
        status = "missing_queue_record"
        blocker = f"{label} has no tracked approval candidate."
    return {
        "label": label,
        "data_class": data_class,
        "status": status,
        "candidate_count": len(candidates),
        "blocker": blocker,
    }


def _queue_sort_key(item: dict[str, Any]) -> tuple[int, str, str]:
    priority = {"critical": 0, "high": 1, "normal": 2}
    return priority[item["priority"]], item["data_class"], item["provider_name"]


def render_approval_report(snapshot: dict[str, Any]) -> str:
    lines = [
        "# Provider Approval Queue",
        "",
        f"- Market focus: `{snapshot['market_focus']}`",
        f"- Reviewed as of: `{snapshot['as_of']}`",
        f"- Approval records: `{snapshot['queue_count']}`",
        f"- Critical approvals open: `{snapshot['critical_open_count']}`",
        f"- Approved for public output: `{snapshot['approved_count']}`",
        f"- Public activation ready: `{str(snapshot['public_activation_ready']).lower()}`",
        "",
        snapshot["publication_note"],
        "",
        "## Scorecard Controls",
        "",
        "| Control | Status | Candidates | Blocker |",
        "|---|---|---:|---|",
    ]
    for control in snapshot["controls"]:
        lines.append(
            f"| {control['label']} | `{control['status']}` | "
            f"{control['candidate_count']} | {control['blocker'] or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Approval Work Queue",
            "",
            "| Priority | Provider | Data Class | Approval Status | Required Evidence |",
            "|---|---|---|---|---|",
        ]
    )
    for item in snapshot["items"]:
        lines.append(
            f"| `{item['priority']}` | {item['provider_name']} | {item['data_class']} | "
            f"`{item['approval_status']}` | {item['required_evidence']} |"
        )
    return "\n".join(lines)


def write_approval_report(path: str | Path, snapshot: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_approval_report(snapshot), encoding="utf-8")


def render_approval_html(snapshot: dict[str, Any]) -> str:
    rows = "".join(
        "<tr>"
        f"<td><span class=\"priority {escape(item['priority'])}\">{escape(item['priority'])}</span></td>"
        f"<td><strong>{escape(item['provider_name'])}</strong><small>{escape(item['data_class'])}</small></td>"
        f"<td><span class=\"pill {escape(item['approval_status'])}\">{escape(item['approval_status'])}</span></td>"
        f"<td>{escape(item['required_evidence'])}</td>"
        "</tr>"
        for item in snapshot["items"]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | Provider Approval Queue</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;--red:#ff7d72;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1160px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(36px,5vw,56px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:850px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:34px;color:var(--mint);display:block}}.no{{color:var(--red)!important}}.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}td small{{display:block;color:var(--muted)}}.priority,.pill{{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px}}.critical{{color:var(--red);background:rgba(255,125,114,.12)}}.high,.pending_terms_review,.pending_license_quote,.pending_written_permission{{color:var(--gold);background:rgba(240,188,98,.12)}}.approved_public_output{{color:var(--mint);background:rgba(86,218,172,.12)}}.rejected_public_output{{color:var(--red);background:rgba(255,125,114,.12)}}.table-wrap{{overflow:hidden;margin-top:18px}}@media(max-width:820px){{.cards{{grid-template-columns:repeat(2,1fr)}}}}
</style></head><body><header><nav>TargetAudit / Governance / Provider Approvals</nav><h1>Permission before<br>production data.</h1>
<p class="lead">A documented review queue for providers that could unlock the public U.S. Financials scorecard.</p>
<p class="meta">Reviewed as of {escape(snapshot['as_of'])}</p>
<section class="cards"><article class="card"><p>Tracked</p><strong>{snapshot['queue_count']}</strong></article><article class="card"><p>Critical open</p><strong>{snapshot['critical_open_count']}</strong></article><article class="card"><p>Approved</p><strong>{snapshot['approved_count']}</strong></article><article class="card"><p>Activation ready</p><strong class="{'no' if not snapshot['public_activation_ready'] else ''}">{'Yes' if snapshot['public_activation_ready'] else 'No'}</strong></article></section></header>
<main><p class="notice">{escape(snapshot['publication_note'])}</p><h2>Approval Work Queue</h2><div class="table-wrap"><table><thead><tr><th>Priority</th><th>Provider</th><th>Approval Status</th><th>Required Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_approval_html(path: str | Path, snapshot: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_approval_html(snapshot), encoding="utf-8")
