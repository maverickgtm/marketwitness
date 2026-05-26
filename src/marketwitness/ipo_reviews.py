from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass, replace
from datetime import date
from html import escape
from pathlib import Path

from .ipo_watch import IpoWatchItem


class IpoReviewDataError(ValueError):
    """Raised when a human review cannot safely update IPO Watch."""


REVIEW_DECISIONS = {
    "confirm_filed_public",
    "confirm_withdrawn",
    "retain_for_review",
    "reject_not_ipo",
}
PUBLIC_FILING_FORMS = {"S-1", "S-1/A", "F-1", "F-1/A", "424B4"}


@dataclass(frozen=True)
class SecAlertEvidence:
    company_name: str
    cik: str
    form: str
    filed_date: date
    source_url: str


@dataclass(frozen=True)
class IpoReviewDecision:
    source_url: str
    cik: str
    decision: str
    display_name: str
    theme: str
    reviewed_on: date
    evidence_level: str
    source_title: str
    next_event: str
    risk_flags: str
    review_note: str


@dataclass(frozen=True)
class IpoReviewOutcome:
    company_name: str
    cik: str
    decision: str
    result: str
    prior_status: str
    current_status: str
    reviewed_on: date
    source_url: str
    review_note: str


def load_alert_evidence(path: str | Path) -> list[SecAlertEvidence]:
    rows = _read_rows(path)
    required = {"company_name", "cik", "form", "filed_date", "source_url"}
    if rows and not required.issubset(rows[0]):
        raise IpoReviewDataError(f"{path}: missing SEC alert evidence fields.")
    evidence: list[SecAlertEvidence] = []
    seen: set[str] = set()
    for row in rows:
        source_url = row["source_url"].strip()
        if not source_url or source_url in seen:
            raise IpoReviewDataError("SEC alert evidence contains blank or duplicate source URLs.")
        seen.add(source_url)
        try:
            filed_date = date.fromisoformat(row["filed_date"].strip())
        except ValueError as exc:
            raise IpoReviewDataError("SEC alert evidence contains an invalid filed date.") from exc
        evidence.append(
            SecAlertEvidence(
                company_name=row["company_name"].strip(),
                cik=row["cik"].strip().zfill(10),
                form=row["form"].strip(),
                filed_date=filed_date,
                source_url=source_url,
            )
        )
    return evidence


def load_review_decisions(path: str | Path) -> list[IpoReviewDecision]:
    rows = _read_rows(path)
    required = {
        "source_url",
        "cik",
        "decision",
        "display_name",
        "theme",
        "reviewed_on",
        "evidence_level",
        "source_title",
        "next_event",
        "risk_flags",
        "review_note",
    }
    if rows and not required.issubset(rows[0]):
        raise IpoReviewDataError(f"{path}: missing manual review fields.")
    decisions: list[IpoReviewDecision] = []
    seen: set[str] = set()
    for row in rows:
        source_url = row["source_url"].strip()
        decision = row["decision"].strip()
        if not source_url or source_url in seen:
            raise IpoReviewDataError("Manual decisions contain blank or duplicate source URLs.")
        if decision not in REVIEW_DECISIONS:
            raise IpoReviewDataError(f"Unknown manual review decision: {decision}.")
        if not row["review_note"].strip():
            raise IpoReviewDataError("Every manual decision requires a review_note.")
        try:
            reviewed_on = date.fromisoformat(row["reviewed_on"].strip())
        except ValueError as exc:
            raise IpoReviewDataError("Manual decisions contain an invalid reviewed_on date.") from exc
        seen.add(source_url)
        decisions.append(
            IpoReviewDecision(
                source_url=source_url,
                cik=row["cik"].strip().zfill(10),
                decision=decision,
                display_name=row["display_name"].strip(),
                theme=row["theme"].strip(),
                reviewed_on=reviewed_on,
                evidence_level=row["evidence_level"].strip(),
                source_title=row["source_title"].strip(),
                next_event=row["next_event"].strip(),
                risk_flags=row["risk_flags"].strip(),
                review_note=row["review_note"].strip(),
            )
        )
    return decisions


def apply_review_decisions(
    registry: list[IpoWatchItem],
    alerts: list[SecAlertEvidence],
    decisions: list[IpoReviewDecision],
    as_of: date,
) -> tuple[list[IpoWatchItem], list[IpoReviewOutcome]]:
    alerts_by_url = {item.source_url: item for item in alerts}
    updated = list(registry)
    outcomes: list[IpoReviewOutcome] = []
    for decision in decisions:
        if decision.reviewed_on > as_of:
            raise IpoReviewDataError("Review date cannot be later than the report date.")
        evidence = alerts_by_url.get(decision.source_url)
        if evidence is None:
            raise IpoReviewDataError("A manual decision does not match a current SEC alert.")
        if evidence.cik != decision.cik:
            raise IpoReviewDataError("A manual decision CIK does not match SEC alert evidence.")
        if decision.reviewed_on < evidence.filed_date:
            raise IpoReviewDataError("Review date cannot predate the SEC filing evidence.")
        index = _find_item(updated, decision, evidence)
        prior = updated[index] if index is not None else None
        prior_status = prior.status if prior else "-"
        current_status = prior_status
        result = "recorded_no_status_change"
        if decision.decision == "confirm_filed_public":
            if evidence.form not in PUBLIC_FILING_FORMS:
                raise IpoReviewDataError("Public filing confirmation requires a registration or final prospectus form.")
            updated_item = _promotion_item(prior, decision, evidence, "filed_public")
            index = _store_item(updated, index, updated_item)
            current_status = updated[index].status
            result = "promoted" if prior_status != current_status else "confirmed_existing"
        elif decision.decision == "confirm_withdrawn":
            if evidence.form != "RW":
                raise IpoReviewDataError("Withdrawal confirmation requires SEC form RW.")
            updated_item = _promotion_item(prior, decision, evidence, "withdrawn")
            index = _store_item(updated, index, updated_item)
            current_status = updated[index].status
            result = "promoted" if prior_status != current_status else "confirmed_existing"
        outcomes.append(
            IpoReviewOutcome(
                company_name=decision.display_name or evidence.company_name,
                cik=evidence.cik,
                decision=decision.decision,
                result=result,
                prior_status=prior_status,
                current_status=current_status,
                reviewed_on=decision.reviewed_on,
                source_url=evidence.source_url,
                review_note=decision.review_note,
            )
        )
    return updated, outcomes


def write_review_outcomes_csv(path: str | Path, outcomes: list[IpoReviewOutcome]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(IpoReviewOutcome.__annotations__))
        writer.writeheader()
        for item in outcomes:
            row = dict(item.__dict__)
            row["reviewed_on"] = item.reviewed_on.isoformat()
            writer.writerow(row)


def render_review_report(
    outcomes: list[IpoReviewOutcome], reviewed_registry: list[IpoWatchItem], as_of: date
) -> str:
    counts = Counter(item.result for item in outcomes)
    lines = [
        "# IPO Watch Manual SEC Reviews",
        "",
        f"- Reviewed as of: `{as_of.isoformat()}`",
        f"- Decisions recorded: `{len(outcomes)}`",
        f"- Status promotions: `{counts['promoted']}`",
        f"- Existing states confirmed: `{counts['confirmed_existing']}`",
        f"- Decisions without status change: `{counts['recorded_no_status_change']}`",
        f"- Companies in resulting IPO Watch registry: `{len(reviewed_registry)}`",
        "",
        "A status change is produced only by a documented manual decision tied to",
        "the same SEC evidence URL and CIK found in SEC IPO Alerts. This review",
        "record does not recommend a position or confirm market trading.",
        "",
        "## Review Decisions",
        "",
        "| Company | Decision | Result | Previous | Current | Reviewed | Review Note | Evidence |",
        "|---|---|---|---|---|---|---|---|",
    ]
    if not outcomes:
        lines.append("| - | - | No decisions submitted | - | - | - | - | - |")
    for item in outcomes:
        lines.append(
            f"| {item.company_name} | `{item.decision}` | `{item.result}` | "
            f"`{item.prior_status}` | `{item.current_status}` | "
            f"{item.reviewed_on.isoformat()} | {item.review_note} | "
            f"[SEC filing]({item.source_url}) |"
        )
    return "\n".join(lines) + "\n"


def write_review_report(
    path: str | Path,
    outcomes: list[IpoReviewOutcome],
    reviewed_registry: list[IpoWatchItem],
    as_of: date,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_review_report(outcomes, reviewed_registry, as_of), encoding="utf-8"
    )


def render_review_html(
    outcomes: list[IpoReviewOutcome], reviewed_registry: list[IpoWatchItem], as_of: date
) -> str:
    counts = Counter(item.result for item in outcomes)
    rows = "".join(
        "<tr>"
        f'<td data-label="Company"><div class="value"><strong>{escape(item.company_name)}</strong>'
        f"<small>CIK {escape(item.cik)}</small></div></td>"
        f'<td data-label="Decision"><div class="value"><span class="badge">{escape(item.decision)}</span></div></td>'
        f'<td data-label="Result"><div class="value"><span class="result {escape(item.result)}">{escape(item.result)}</span></div></td>'
        f'<td data-label="Change"><div class="value">{escape(item.prior_status)} &rarr; {escape(item.current_status)}</div></td>'
        f'<td data-label="Reviewed"><div class="value">{escape(item.reviewed_on.isoformat())}</div></td>'
        f'<td data-label="Review note"><div class="value">{escape(item.review_note)}</div></td>'
        f'<td data-label="Evidence"><div class="value"><a href="{escape(item.source_url)}">SEC</a></div></td>'
        "</tr>"
        for item in outcomes
    )
    if not rows:
        rows = '<tr><td colspan="7">No documented review decisions were submitted.</td></tr>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarketWitness | IPO Watch Reviews</title><style>
:root{{--bg:#081117;--panel:#101d26;--line:#21333d;--text:#ecf0ee;--muted:#9cadb2;--mint:#57dbad;--amber:#f2bf62;--blue:#62a6ff;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);font-size:13px;letter-spacing:.08em;text-transform:uppercase}}h1{{font-size:clamp(36px,5vw,56px);line-height:1.05;margin:40px 0 14px}}.lead{{color:var(--muted);max-width:780px;font-size:17px}}.cards{{display:flex;gap:16px;flex-wrap:wrap;margin:34px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:190px}}.card p{{margin:0;color:var(--muted)}}.card strong{{display:block;font-size:38px;color:var(--mint)}}.notice{{padding:15px 18px;border-left:3px solid var(--amber);color:var(--muted)}}h2{{margin-top:44px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{font-size:12px;color:var(--muted);font-weight:500;text-transform:uppercase}}td small{{display:block;color:var(--muted);margin-top:6px}}a{{color:var(--mint);text-decoration:none}}.badge,.result{{border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}.badge{{color:var(--blue);background:rgba(98,166,255,.12)}}.promoted{{color:var(--mint);background:rgba(87,219,173,.12)}}.confirmed_existing{{color:var(--amber);background:rgba(242,191,98,.12)}}.recorded_no_status_change{{color:var(--muted);background:rgba(156,173,178,.12)}}
@media(max-width:800px){{header,main{{padding:24px 18px}}.cards{{display:block}}.card{{margin-bottom:12px}}.table-wrap{{border:0;background:transparent}}table,tbody,tr,td{{display:block;width:100%}}thead{{display:none}}tr{{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin-bottom:14px;padding:8px 0}}td{{border:0;display:grid;grid-template-columns:104px minmax(0,1fr);gap:10px;padding:9px 14px}}td::before{{content:attr(data-label);color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.06em}}.value,td strong,td small{{min-width:0;overflow-wrap:anywhere}}.badge,.result{{white-space:normal;overflow-wrap:anywhere}}}}
</style></head><body><header><nav><a href="/dashboard/reports">Report Center</a> / <a href="/dashboard/ipo">IPO Watch Center</a> / Manual Reviews</nav>
<h1>Reviewed evidence.<br>Controlled updates.</h1><p class="lead">Documented SEC review decisions applied to a generated IPO Watch registry, with no automatic promotion from a discovered filing.</p>
<p class="meta">Reviewed as of {escape(as_of.isoformat())}</p><section class="cards"><article class="card"><p>Decisions</p><strong>{len(outcomes)}</strong></article><article class="card"><p>Promotions</p><strong>{counts['promoted']}</strong></article><article class="card"><p>Confirmed existing</p><strong>{counts['confirmed_existing']}</strong></article><article class="card"><p>Watchlist records</p><strong>{len(reviewed_registry)}</strong></article></section></header>
<main><p class="notice">A decision is accepted only when its SEC evidence URL and CIK match an alert. This log is research evidence, not a trading recommendation.</p>
<h2>Decision audit</h2><div class="table-wrap"><table><thead><tr><th>Company</th><th>Decision</th><th>Result</th><th>Change</th><th>Reviewed</th><th>Review note</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_review_html(
    path: str | Path,
    outcomes: list[IpoReviewOutcome],
    reviewed_registry: list[IpoWatchItem],
    as_of: date,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_review_html(outcomes, reviewed_registry, as_of), encoding="utf-8"
    )


def _promotion_item(
    prior: IpoWatchItem | None,
    decision: IpoReviewDecision,
    evidence: SecAlertEvidence,
    status: str,
) -> IpoWatchItem:
    display_name = decision.display_name or (prior.company_name if prior else "")
    theme = decision.theme or (prior.theme if prior else "")
    source_title = decision.source_title or evidence.company_name
    evidence_level = decision.evidence_level or "Reviewed SEC filing"
    next_event = decision.next_event or (
        prior.next_event if prior else "Review amendments and official market confirmation."
    )
    risk_flags = decision.risk_flags or (
        prior.risk_flags if prior else "Prospectus risks require review."
    )
    if not display_name or not theme:
        raise IpoReviewDataError("A newly promoted issuer requires display_name and theme.")
    if prior and prior.status == "listed" and status != "listed":
        raise IpoReviewDataError("A reviewed filing cannot downgrade an already listed issuer.")
    if prior:
        return replace(
            prior,
            cik=evidence.cik,
            status=status,
            status_date=evidence.filed_date,
            filing_type=evidence.form,
            evidence_level=evidence_level,
            source_title=source_title,
            source_url=evidence.source_url,
            next_event=next_event,
            risk_flags=risk_flags,
        )
    return IpoWatchItem(
        company_name=display_name,
        cik=evidence.cik,
        theme=theme,
        status=status,
        status_date=evidence.filed_date,
        ticker="",
        exchange="",
        filing_type=evidence.form,
        evidence_level=evidence_level,
        source_title=source_title,
        source_url=evidence.source_url,
        next_event=next_event,
        risk_flags=risk_flags,
    )


def _find_item(
    items: list[IpoWatchItem],
    decision: IpoReviewDecision,
    evidence: SecAlertEvidence,
) -> int | None:
    matching_cik = [
        index for index, item in enumerate(items) if item.cik and item.cik == evidence.cik
    ]
    if len(matching_cik) > 1:
        raise IpoReviewDataError("IPO Watch contains duplicate CIK mappings.")
    if matching_cik:
        return matching_cik[0]
    name = decision.display_name.casefold()
    matching_names = [
        index for index, item in enumerate(items) if name and item.company_name.casefold() == name
    ]
    if matching_names:
        existing = items[matching_names[0]]
        if existing.cik and existing.cik != evidence.cik:
            raise IpoReviewDataError("Manual decision conflicts with an existing company CIK.")
        return matching_names[0]
    return None


def _store_item(
    items: list[IpoWatchItem], index: int | None, item: IpoWatchItem
) -> int:
    if index is None:
        items.append(item)
        return len(items) - 1
    items[index] = item
    return index


def _read_rows(path: str | Path) -> list[dict[str, str]]:
    try:
        with Path(path).open(newline="", encoding="utf-8") as source:
            return list(csv.DictReader(source))
    except OSError as exc:
        raise IpoReviewDataError(f"Unable to read review input {path}: {exc}") from exc
