from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

CONFIRMATION_EVENTS = {"trading_started", "offering_closed", "listing_confirmed"}
EVIDENCE_LEVELS = {"issuer_official_release"}
CONFIRMATION_COLUMNS = {
    "company_name",
    "market",
    "ticker",
    "event_type",
    "event_date",
    "source_title",
    "source_url",
    "verified_on",
    "evidence_level",
    "research_note",
}


class IssuerConfirmationDataError(ValueError):
    """Raised when issuer listing-confirmation evidence is not auditable."""


@dataclass(frozen=True)
class IssuerListingConfirmation:
    company_name: str
    market: str
    ticker: str
    event_type: str
    event_date: date
    source_title: str
    source_url: str
    verified_on: date
    evidence_level: str
    research_note: str


def load_issuer_confirmations(path: str | Path) -> list[IssuerListingConfirmation]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        missing = sorted(CONFIRMATION_COLUMNS - set(reader.fieldnames or []))
        if missing:
            raise IssuerConfirmationDataError(
                f"{path}: missing columns: {', '.join(missing)}"
            )
        events: list[IssuerListingConfirmation] = []
        seen: set[tuple[str, str, date]] = set()
        for index, row in enumerate(reader, start=2):
            company = row["company_name"].strip()
            event_type = row["event_type"].strip()
            evidence_level = row["evidence_level"].strip()
            if event_type not in CONFIRMATION_EVENTS:
                raise IssuerConfirmationDataError(f"{path}: invalid event type on row {index}")
            if evidence_level not in EVIDENCE_LEVELS:
                raise IssuerConfirmationDataError(f"{path}: invalid evidence level on row {index}")
            try:
                event_date = date.fromisoformat(row["event_date"].strip())
                verified_on = date.fromisoformat(row["verified_on"].strip())
            except ValueError as exc:
                raise IssuerConfirmationDataError(f"{path}: invalid date on row {index}") from exc
            required = [
                company,
                row["market"].strip(),
                row["ticker"].strip(),
                row["source_title"].strip(),
                row["source_url"].strip(),
                row["research_note"].strip(),
            ]
            if not all(required):
                raise IssuerConfirmationDataError(f"{path}: missing evidence on row {index}")
            if not row["source_url"].strip().startswith("https://"):
                raise IssuerConfirmationDataError(f"{path}: non-HTTPS source on row {index}")
            if verified_on < event_date:
                raise IssuerConfirmationDataError(
                    f"{path}: verification precedes event on row {index}"
                )
            key = (company.casefold(), event_type, event_date)
            if key in seen:
                raise IssuerConfirmationDataError(f"{path}: duplicate event on row {index}")
            seen.add(key)
            events.append(
                IssuerListingConfirmation(
                    company_name=company,
                    market=row["market"].strip(),
                    ticker=row["ticker"].strip().upper(),
                    event_type=event_type,
                    event_date=event_date,
                    source_title=row["source_title"].strip(),
                    source_url=row["source_url"].strip(),
                    verified_on=verified_on,
                    evidence_level=evidence_level,
                    research_note=row["research_note"].strip(),
                )
            )
        return events


def render_issuer_confirmations_report(
    events: list[IssuerListingConfirmation], as_of: date
) -> str:
    _validate_as_of(events, as_of)
    counts = Counter(event.event_type for event in events)
    companies = {event.company_name.casefold() for event in events}
    ordered = sorted(events, key=lambda event: event.event_date, reverse=True)
    lines = [
        "# Issuer Listing Confirmations",
        "",
        f"- Verified as of: `{as_of.isoformat()}`",
        f"- Issuers confirmed from official releases: `{len(companies)}`",
        f"- Confirmed milestones: `{len(events)}`",
        f"- Trading started: `{counts['trading_started']}`",
        f"- Offerings closed: `{counts['offering_closed']}`",
        "",
        "This registry records only milestones explicitly stated in official issuer",
        "releases. A listing or offering confirmation is not an investment",
        "recommendation or evidence of future performance.",
        "",
        "## Verified Milestones",
        "",
        "| Event Date | Issuer | Market / Ticker | Event | Evidence | Verified On |",
        "|---|---|---|---|---|---|",
    ]
    for event in ordered:
        lines.append(
            f"| {event.event_date.isoformat()} | {event.company_name} | "
            f"{event.market} / {event.ticker} | `{event.event_type}` | "
            f"[Official issuer release]({event.source_url}) | "
            f"{event.verified_on.isoformat()} |"
        )
    lines.extend(["", "## Review Notes", ""])
    for event in ordered:
        lines.extend(
            [
                f"### {event.company_name} - {event.event_type}",
                "",
                f"- Source title: {event.source_title}",
                f"- Review note: {event.research_note}",
                "",
            ]
        )
    return "\n".join(lines)


def write_issuer_confirmations_report(
    path: str | Path, events: list[IssuerListingConfirmation], as_of: date
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_issuer_confirmations_report(events, as_of), encoding="utf-8")


def render_issuer_confirmations_html(
    events: list[IssuerListingConfirmation], as_of: date
) -> str:
    _validate_as_of(events, as_of)
    counts = Counter(event.event_type for event in events)
    companies = {event.company_name.casefold() for event in events}
    ordered = sorted(events, key=lambda event: event.event_date, reverse=True)
    rows = "".join(
        "<tr>"
        f'<td data-label="Event date">{escape(event.event_date.isoformat())}</td>'
        f'<td data-label="Issuer"><strong>{escape(event.company_name)}</strong><small>{escape(event.market)} / {escape(event.ticker)}</small></td>'
        f'<td data-label="Event"><span class="badge {escape(event.event_type)}">{escape(event.event_type)}</span></td>'
        f'<td data-label="Verified on">{escape(event.verified_on.isoformat())}</td>'
        f'<td data-label="Evidence"><a href="{escape(event.source_url)}">Issuer release</a><small>{escape(event.source_title)}</small></td>'
        "</tr>"
        for event in ordered
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | Issuer Listing Confirmations</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1120px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:820px}}
.cards{{display:flex;flex-wrap:wrap;gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:210px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}td small{{display:block;color:var(--muted);max-width:300px}}a{{color:var(--mint);text-decoration:none}}.badge{{border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}.trading_started{{color:var(--mint);background:rgba(86,218,172,.12)}}.offering_closed{{color:var(--blue);background:rgba(98,166,255,.12)}}.listing_confirmed{{color:var(--gold);background:rgba(240,188,98,.12)}}
@media(max-width:800px){{.table-wrap{{background:transparent;border:0;overflow:visible}}thead{{display:none}}table,tbody,tr,td{{display:block;width:100%}}tr{{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin-bottom:14px;padding:10px 15px}}td{{border:0;padding:9px 0 9px 116px;min-height:39px;position:relative}}td::before{{content:attr(data-label);position:absolute;left:0;top:10px;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.06em}}}}
</style></head><body><header><nav><a href="/dashboard/ipo">IPO Watch Center</a> / Global Listings Watch / Issuer Confirmations</nav>
<h1>Primary evidence.<br>Confirmed milestones.</h1><p class="lead">Listing events stated in official issuer announcements, preserved with event date and verification date.</p>
<p class="meta">Verified as of {escape(as_of.isoformat())}</p><section class="cards"><article class="card"><p>Confirmed issuers</p><strong>{len(companies)}</strong></article><article class="card"><p>Trading started</p><strong>{counts['trading_started']}</strong></article><article class="card"><p>Offerings closed</p><strong>{counts['offering_closed']}</strong></article></section></header>
<main><p class="notice">An official release confirms only the milestone it states. It is not an investment recommendation and does not establish future performance.</p>
<h2>Verified milestones</h2><div class="table-wrap"><table><thead><tr><th>Event date</th><th>Issuer</th><th>Event</th><th>Verified on</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_issuer_confirmations_html(
    path: str | Path, events: list[IssuerListingConfirmation], as_of: date
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_issuer_confirmations_html(events, as_of), encoding="utf-8")


def _validate_as_of(events: list[IssuerListingConfirmation], as_of: date) -> None:
    if any(event.event_date > as_of or event.verified_on > as_of for event in events):
        raise IssuerConfirmationDataError(
            "Issuer confirmation registry includes evidence after the report cutoff."
        )
