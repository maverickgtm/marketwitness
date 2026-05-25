from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass, replace
from datetime import date
from html import escape
from pathlib import Path

from .provider_approvals import (
    APPROVAL_COLUMNS,
    ProviderApprovalDataError,
    ProviderApprovalRecord,
    build_approval_queue,
)
from .source_registry import SOURCE_COLUMNS, SourceProvider

DECISION_COLUMNS = {
    "provider_id",
    "decision",
    "reviewed_on",
    "evidence_url",
    "evidence_summary",
    "new_integration_status",
    "review_note",
}
DECISIONS = {"retain_pending", "approve_public_output", "reject_public_output"}
APPROVABLE_INTEGRATIONS = {"implemented", "manual_verified"}


class ProviderApprovalReviewDataError(ValueError):
    """Raised when a manual provider decision cannot be safely applied."""


@dataclass(frozen=True)
class ProviderApprovalDecision:
    provider_id: str
    decision: str
    reviewed_on: date
    evidence_url: str
    evidence_summary: str
    new_integration_status: str
    review_note: str


@dataclass(frozen=True)
class ProviderApprovalOutcome:
    provider_id: str
    provider_name: str
    decision: str
    result: str
    prior_approval_status: str
    current_approval_status: str
    prior_deployment_state: str
    current_deployment_state: str
    reviewed_on: date
    evidence_url: str
    evidence_summary: str
    review_note: str


def load_provider_approval_decisions(
    path: str | Path,
) -> list[ProviderApprovalDecision]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        missing = sorted(DECISION_COLUMNS - set(reader.fieldnames or []))
        if missing:
            raise ProviderApprovalReviewDataError(
                f"{path}: missing columns: {', '.join(missing)}"
            )
        decisions: list[ProviderApprovalDecision] = []
        seen: set[str] = set()
        for index, row in enumerate(reader, start=2):
            provider_id = row["provider_id"].strip()
            decision = row["decision"].strip()
            evidence_url = row["evidence_url"].strip()
            evidence_summary = row["evidence_summary"].strip()
            review_note = row["review_note"].strip()
            integration = row["new_integration_status"].strip()
            if not provider_id or provider_id in seen:
                raise ProviderApprovalReviewDataError(
                    f"{path}: blank or duplicate provider id on row {index}"
                )
            if decision not in DECISIONS:
                raise ProviderApprovalReviewDataError(
                    f"{path}: unknown provider decision on row {index}"
                )
            if not evidence_url.startswith("https://"):
                raise ProviderApprovalReviewDataError(
                    f"{path}: evidence URL must be HTTPS on row {index}"
                )
            if not evidence_summary or not review_note:
                raise ProviderApprovalReviewDataError(
                    f"{path}: evidence summary and review note required on row {index}"
                )
            if decision == "approve_public_output" and integration not in APPROVABLE_INTEGRATIONS:
                raise ProviderApprovalReviewDataError(
                    f"{path}: approved provider requires a verified integration on row {index}"
                )
            if decision != "approve_public_output" and integration:
                raise ProviderApprovalReviewDataError(
                    f"{path}: only an approval can declare a new integration state on row {index}"
                )
            try:
                reviewed_on = date.fromisoformat(row["reviewed_on"].strip())
            except ValueError as exc:
                raise ProviderApprovalReviewDataError(
                    f"{path}: invalid review date on row {index}"
                ) from exc
            seen.add(provider_id)
            decisions.append(
                ProviderApprovalDecision(
                    provider_id=provider_id,
                    decision=decision,
                    reviewed_on=reviewed_on,
                    evidence_url=evidence_url,
                    evidence_summary=evidence_summary,
                    new_integration_status=integration,
                    review_note=review_note,
                )
            )
        return decisions


def apply_provider_approval_decisions(
    providers: list[SourceProvider],
    approvals: list[ProviderApprovalRecord],
    decisions: list[ProviderApprovalDecision],
    as_of: date,
) -> tuple[list[SourceProvider], list[ProviderApprovalRecord], list[ProviderApprovalOutcome]]:
    updated_providers = list(providers)
    updated_approvals = list(approvals)
    outcomes: list[ProviderApprovalOutcome] = []
    for decision in decisions:
        if decision.reviewed_on > as_of:
            raise ProviderApprovalReviewDataError(
                "Provider review date cannot be later than the report date."
            )
        provider_index = _find_provider(updated_providers, decision.provider_id)
        approval_index = _find_approval(updated_approvals, decision.provider_id)
        provider = updated_providers[provider_index]
        approval = updated_approvals[approval_index]
        if decision.reviewed_on < max(provider.reviewed_on, approval.reviewed_on):
            raise ProviderApprovalReviewDataError(
                "Provider decision cannot predate existing governance evidence."
            )
        prior_status = approval.approval_status
        prior_deployment = provider.deployment_state
        result = "pending_recorded"
        if decision.decision == "approve_public_output":
            provider = replace(
                provider,
                integration_status=decision.new_integration_status,
                license_status="public_access_rules_documented",
                publication_policy="source_link_and_derived_output",
                reference_url=decision.evidence_url,
                reviewed_on=decision.reviewed_on,
                review_note=decision.review_note,
            )
            approval = replace(
                approval,
                approval_status="approved_public_output",
                evidence_url=decision.evidence_url,
                reviewed_on=decision.reviewed_on,
                review_note=decision.review_note,
            )
            result = "promoted_public_output"
        elif decision.decision == "reject_public_output":
            approval = replace(
                approval,
                approval_status="rejected_public_output",
                evidence_url=decision.evidence_url,
                reviewed_on=decision.reviewed_on,
                review_note=decision.review_note,
            )
            result = "rejected_public_output"
        else:
            approval = replace(
                approval,
                evidence_url=decision.evidence_url,
                reviewed_on=decision.reviewed_on,
                review_note=decision.review_note,
            )
        updated_providers[provider_index] = provider
        updated_approvals[approval_index] = approval
        outcomes.append(
            ProviderApprovalOutcome(
                provider_id=provider.provider_id,
                provider_name=provider.provider_name,
                decision=decision.decision,
                result=result,
                prior_approval_status=prior_status,
                current_approval_status=approval.approval_status,
                prior_deployment_state=prior_deployment,
                current_deployment_state=provider.deployment_state,
                reviewed_on=decision.reviewed_on,
                evidence_url=decision.evidence_url,
                evidence_summary=decision.evidence_summary,
                review_note=decision.review_note,
            )
        )
    try:
        build_approval_queue(updated_providers, updated_approvals, as_of)
    except ProviderApprovalDataError as exc:
        raise ProviderApprovalReviewDataError(str(exc)) from exc
    return updated_providers, updated_approvals, outcomes


def write_reviewed_source_registry(path: str | Path, providers: list[SourceProvider]) -> None:
    _write_records(path, sorted(SOURCE_COLUMNS), providers)


def write_reviewed_approval_queue(
    path: str | Path, approvals: list[ProviderApprovalRecord]
) -> None:
    _write_records(path, sorted(APPROVAL_COLUMNS), approvals)


def write_provider_review_outcomes_csv(
    path: str | Path, outcomes: list[ProviderApprovalOutcome]
) -> None:
    _write_records(path, list(ProviderApprovalOutcome.__annotations__), outcomes)


def render_provider_review_report(
    outcomes: list[ProviderApprovalOutcome], as_of: date
) -> str:
    counts = Counter(item.result for item in outcomes)
    lines = [
        "# Provider Approval Manual Reviews",
        "",
        f"- Reviewed as of: `{as_of.isoformat()}`",
        f"- Decisions recorded: `{len(outcomes)}`",
        f"- Public-output promotions: `{counts['promoted_public_output']}`",
        f"- Pending reviews recorded: `{counts['pending_recorded']}`",
        f"- Public-output rejections: `{counts['rejected_public_output']}`",
        "",
        "A provider is promoted only by a documented approval with HTTPS evidence",
        "and a verified production integration. Generated registry files must pass",
        "Scorecard Readiness and Release Center before public results can ship.",
        "",
        "## Review Decisions",
        "",
        "| Provider | Decision | Result | Approval Change | Source State Change | Evidence | Review Note |",
        "|---|---|---|---|---|---|---|",
    ]
    if not outcomes:
        lines.append("| - | - | No decisions submitted | - | - | - | - |")
    for item in outcomes:
        lines.append(
            f"| {item.provider_name} | `{item.decision}` | `{item.result}` | "
            f"`{item.prior_approval_status}` to `{item.current_approval_status}` | "
            f"`{item.prior_deployment_state}` to `{item.current_deployment_state}` | "
            f"[Evidence]({item.evidence_url}) | {item.review_note} |"
        )
    return "\n".join(lines) + "\n"


def write_provider_review_report(
    path: str | Path, outcomes: list[ProviderApprovalOutcome], as_of: date
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_provider_review_report(outcomes, as_of), encoding="utf-8")


def render_provider_review_html(
    outcomes: list[ProviderApprovalOutcome], as_of: date
) -> str:
    counts = Counter(item.result for item in outcomes)
    rows = "".join(
        "<tr>"
        f"<td><strong>{escape(item.provider_name)}</strong><small>{escape(item.provider_id)}</small></td>"
        f"<td><span class=\"pill {escape(item.result)}\">{escape(item.result)}</span></td>"
        f"<td>{escape(item.prior_approval_status)} to {escape(item.current_approval_status)}</td>"
        f"<td>{escape(item.prior_deployment_state)} to {escape(item.current_deployment_state)}</td>"
        f"<td><a href=\"{escape(item.evidence_url)}\">Evidence</a><small>{escape(item.evidence_summary)}</small></td>"
        "</tr>"
        for item in outcomes
    ) or '<tr><td colspan="5">No documented decisions were submitted.</td></tr>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | Provider Approval Reviews</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--red:#ff7d72;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1160px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(36px,5vw,56px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:870px}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:36px;color:var(--mint);display:block}}.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}td small{{display:block;color:var(--muted)}}a{{color:var(--mint);text-decoration:none}}.pill{{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px}}.pending_recorded{{color:var(--gold);background:rgba(240,188,98,.12)}}.promoted_public_output{{color:var(--mint);background:rgba(86,218,172,.12)}}.rejected_public_output{{color:var(--red);background:rgba(255,125,114,.12)}}.table-wrap{{overflow:hidden;margin-top:18px}}@media(max-width:820px){{.cards{{grid-template-columns:1fr}}.table-wrap{{overflow-x:auto}}table{{min-width:760px}}}}
</style></head><body><header><nav>TargetAudit / Governance / Provider Review Decisions</nav><h1>Evidence in.<br>Promotion controlled.</h1>
<p class="lead">Manual approval decisions applied to generated provider-governance files, leaving the base register unchanged.</p>
<p class="meta">Reviewed as of {escape(as_of.isoformat())}</p><section class="cards"><article class="card"><p>Decisions</p><strong>{len(outcomes)}</strong></article><article class="card"><p>Promotions</p><strong>{counts['promoted_public_output']}</strong></article><article class="card"><p>Pending recorded</p><strong>{counts['pending_recorded']}</strong></article></section></header>
<main><p class="notice">Permission evidence and a verified connector are both required for promotion. This audit does not authorize a scorecard release by itself.</p><h2>Decision Audit</h2><div class="table-wrap"><table><thead><tr><th>Provider</th><th>Result</th><th>Approval</th><th>Source State</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_provider_review_html(
    path: str | Path, outcomes: list[ProviderApprovalOutcome], as_of: date
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_provider_review_html(outcomes, as_of), encoding="utf-8")


def _find_provider(providers: list[SourceProvider], provider_id: str) -> int:
    indexes = [index for index, provider in enumerate(providers) if provider.provider_id == provider_id]
    if len(indexes) != 1:
        raise ProviderApprovalReviewDataError(
            f"Decision references an unknown or duplicate provider: {provider_id}."
        )
    return indexes[0]


def _find_approval(approvals: list[ProviderApprovalRecord], provider_id: str) -> int:
    indexes = [index for index, approval in enumerate(approvals) if approval.provider_id == provider_id]
    if len(indexes) != 1:
        raise ProviderApprovalReviewDataError(
            f"Decision references a provider without one approval dossier: {provider_id}."
        )
    return indexes[0]


def _write_records(path: str | Path, fieldnames: list[str], records: list[object]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = {
                key: value.isoformat() if isinstance(value, date) else value
                for key, value in record.__dict__.items()
            }
            writer.writerow({field: row[field] for field in fieldnames})
