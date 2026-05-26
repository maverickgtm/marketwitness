from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

IPO_WATCH_STATUSES = {"candidate_unverified", "filed_public", "listed", "withdrawn"}
IPO_WATCH_COLUMNS = {
    "company_name",
    "theme",
    "status",
    "status_date",
    "ticker",
    "exchange",
    "filing_type",
    "evidence_level",
    "source_title",
    "source_url",
    "next_event",
    "risk_flags",
}
IPO_WATCH_FIELDNAMES = [
    "company_name",
    "cik",
    "theme",
    "status",
    "status_date",
    "ticker",
    "exchange",
    "filing_type",
    "evidence_level",
    "source_title",
    "source_url",
    "next_event",
    "risk_flags",
]


class IpoWatchDataError(ValueError):
    """Raised when an IPO watch registry is not auditable."""


@dataclass(frozen=True)
class IpoWatchItem:
    company_name: str
    cik: str
    theme: str
    status: str
    status_date: date
    ticker: str
    exchange: str
    filing_type: str
    evidence_level: str
    source_title: str
    source_url: str
    next_event: str
    risk_flags: str

    @property
    def research_action(self) -> str:
        actions = {
            "candidate_unverified": "Wait for a primary-source filing or issuer announcement.",
            "filed_public": "Review prospectus, amendments, pricing and listing confirmation.",
            "listed": "Track post-IPO filings and market history before any scored analysis.",
            "withdrawn": "Monitor only for a new registration statement.",
        }
        return actions[self.status]


def load_ipo_watch(path: str | Path) -> list[IpoWatchItem]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        present = set(reader.fieldnames or [])
        missing = sorted(IPO_WATCH_COLUMNS - present)
        if missing:
            raise IpoWatchDataError(f"{path}: missing columns: {', '.join(missing)}")
        items: list[IpoWatchItem] = []
        seen: set[str] = set()
        for index, row in enumerate(reader, start=2):
            company = row["company_name"].strip()
            status = row["status"].strip()
            if not company or company.casefold() in seen:
                raise IpoWatchDataError(f"{path}: blank or duplicate company on row {index}")
            if status not in IPO_WATCH_STATUSES:
                raise IpoWatchDataError(f"{path}: invalid status on row {index}")
            try:
                status_date = date.fromisoformat(row["status_date"].strip())
            except ValueError as exc:
                raise IpoWatchDataError(f"{path}: invalid status date on row {index}") from exc
            if not row["source_title"].strip() or not row["source_url"].strip():
                raise IpoWatchDataError(f"{path}: missing source on row {index}")
            if status == "listed" and not (
                row["ticker"].strip() and row["exchange"].strip()
            ):
                raise IpoWatchDataError(
                    f"{path}: listed company requires ticker and exchange on row {index}"
                )
            seen.add(company.casefold())
            items.append(
                IpoWatchItem(
                    company_name=company,
                    cik=row.get("cik", "").strip().zfill(10) if row.get("cik", "").strip() else "",
                    theme=row["theme"].strip(),
                    status=status,
                    status_date=status_date,
                    ticker=row["ticker"].strip().upper(),
                    exchange=row["exchange"].strip(),
                    filing_type=row["filing_type"].strip(),
                    evidence_level=row["evidence_level"].strip(),
                    source_title=row["source_title"].strip(),
                    source_url=row["source_url"].strip(),
                    next_event=row["next_event"].strip(),
                    risk_flags=row["risk_flags"].strip(),
                )
            )
        return items


def render_ipo_watch_report(items: list[IpoWatchItem], as_of: date) -> str:
    _validate_as_of(items, as_of)
    counts = Counter(item.status for item in items)
    order = {"filed_public": 0, "listed": 1, "candidate_unverified": 2, "withdrawn": 3}
    items = sorted(items, key=lambda item: (order[item.status], item.company_name.lower()))
    lines = [
        "# IPO Watch",
        "",
        f"- Verified as of: `{as_of.isoformat()}`",
        f"- Companies monitored: `{len(items)}`",
        f"- Public filing confirmed: `{counts['filed_public']}`",
        f"- Already listed: `{counts['listed']}`",
        f"- Candidate, not confirmed by public filing: `{counts['candidate_unverified']}`",
        "",
        "This watchlist records verifiable IPO milestones and research tasks. It does",
        "not produce buy, sell or position-size instructions.",
        "",
        "## Status Board",
        "",
        "| Company | Theme | Status | Verified Date | Ticker | Evidence | Research Action |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in items:
        symbol = item.ticker or "-"
        lines.append(
            f"| {item.company_name} | {item.theme} | `{item.status}` | "
            f"{item.status_date.isoformat()} | {symbol} | {item.evidence_level} | "
            f"{item.research_action} |"
        )
    lines.extend(["", "## Events To Monitor", ""])
    for item in items:
        lines.extend(
            [
                f"### {item.company_name}",
                "",
                f"- Next verifiable event: {item.next_event or 'No event defined.'}",
                f"- Risk flags: {item.risk_flags or 'To be documented.'}",
                f"- Source: [{item.source_title}]({item.source_url})",
                "",
            ]
        )
    lines.extend(
        [
            "## Research Rule",
            "",
            "A company moves from `candidate_unverified` to `filed_public` only when a",
            "public registration statement or primary issuer announcement can be cited.",
            "A company moves to `listed` only after trading is confirmed by the exchange,",
            "issuer or a filed final prospectus.",
            "",
        ]
    )
    return "\n".join(lines)


def write_ipo_watch_report(
    path: str | Path, items: list[IpoWatchItem], as_of: date
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_ipo_watch_report(items, as_of), encoding="utf-8")


def render_ipo_watch_html(items: list[IpoWatchItem], as_of: date) -> str:
    _validate_as_of(items, as_of)
    counts = Counter(item.status for item in items)
    order = {"filed_public": 0, "listed": 1, "candidate_unverified": 2, "withdrawn": 3}
    items = sorted(items, key=lambda item: (order[item.status], item.company_name.lower()))
    cards = [
        ("Public filing", counts["filed_public"], "S-1 or equivalent confirmed"),
        ("Already listed", counts["listed"], "Trading confirmed"),
        ("Candidates", counts["candidate_unverified"], "Primary confirmation pending"),
    ]
    card_html = "".join(
        f'<article class="card"><p>{escape(label)}</p><strong>{count}</strong>'
        f"<small>{escape(detail)}</small></article>"
        for label, count, detail in cards
    )
    rows = "".join(
        "<tr>"
        f"<td><strong>{escape(item.company_name)}</strong><small>{escape(item.theme)}</small></td>"
        f'<td><span class="badge {escape(item.status)}">{escape(item.status)}</span></td>'
        f"<td>{escape(item.status_date.isoformat())}</td>"
        f"<td>{escape(item.ticker or '-')}</td>"
        f"<td>{escape(item.next_event)}</td>"
        f'<td><a href="{escape(item.source_url)}">Source</a></td>'
        "</tr>"
        for item in items
    )
    timeline = "".join(
        "<article class=\"watch-item\">"
        f"<div><h3>{escape(item.company_name)}</h3>"
        f'<span class="badge {escape(item.status)}">{escape(item.status)}</span></div>'
        f"<p class=\"event\">Next: {escape(item.next_event)}</p>"
        f"<p class=\"risk\">Risk flags: {escape(item.risk_flags)}</p>"
        f"<p class=\"action\">Research action: {escape(item.research_action)}</p>"
        "</article>"
        for item in items
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MarketWitness | IPO Watch</title>
  <style>
    :root {{
      --bg: #081117;
      --panel: #101d26;
      --line: #21333d;
      --text: #ecf0ee;
      --muted: #9cadb2;
      --mint: #57dbad;
      --amber: #f2bf62;
      --blue: #62a6ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; background: var(--bg); color: var(--text);
      font: 15px/1.5 Inter, Arial, sans-serif;
    }}
    header, main {{ max-width: 1180px; margin: auto; padding: 30px 28px; }}
    nav {{ color: var(--muted); font-size: 13px; letter-spacing: .08em; text-transform: uppercase; }}
    h1 {{ font-size: clamp(36px, 5vw, 56px); line-height: 1.05; margin: 40px 0 14px; }}
    .lead {{ color: var(--muted); max-width: 720px; font-size: 17px; margin-bottom: 30px; }}
    .meta {{ color: var(--muted); font-size: 13px; }}
    .cards {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 34px 0; }}
    .card, .watch-item, .table-wrap {{
      background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
    }}
    .card {{ padding: 18px 20px; }}
    .card p {{ margin: 0; color: var(--muted); }}
    .card strong {{ display: block; font-size: 38px; color: var(--mint); }}
    .card small {{ color: var(--muted); }}
    h2 {{ margin-top: 45px; font-size: 22px; }}
    .table-wrap {{ overflow: hidden; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{ text-align: left; color: var(--muted); font-weight: 500; font-size: 12px; text-transform: uppercase; }}
    th, td {{ padding: 15px 16px; border-bottom: 1px solid var(--line); vertical-align: top; }}
    td small {{ color: var(--muted); display: block; }}
    a {{ color: var(--mint); text-decoration: none; }}
    .badge {{ font-size: 12px; border-radius: 999px; padding: 5px 9px; white-space: nowrap; }}
    .filed_public {{ color: var(--amber); background: rgba(242, 191, 98, .12); }}
    .listed {{ color: var(--mint); background: rgba(87, 219, 173, .12); }}
    .candidate_unverified {{ color: var(--blue); background: rgba(98, 166, 255, .12); }}
    .timeline {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }}
    .watch-item {{ padding: 18px; }}
    .watch-item div {{ display: flex; justify-content: space-between; gap: 10px; align-items: center; }}
    .watch-item h3 {{ margin: 0; font-size: 17px; }}
    .event {{ margin-bottom: 6px; }}
    .risk, .action {{ color: var(--muted); font-size: 13px; margin: 7px 0 0; }}
    .notice {{ border-left: 3px solid var(--amber); padding: 15px 18px; color: var(--muted); background: var(--panel); }}
    @media (max-width: 800px) {{
      .cards, .timeline {{ grid-template-columns: 1fr; }}
      .table-wrap {{ overflow-x: auto; }}
      table {{ min-width: 820px; }}
    }}
  </style>
</head>
<body>
  <header>
    <nav><a href="/dashboard/reports">Report Center</a> / <a href="/dashboard/ipo">IPO Watch Center</a> / Status Board</nav>
    <h1>Upcoming listings,<br>verified first.</h1>
    <p class="lead">Track high-interest public listings through filings and issuer confirmations. Rumors remain candidates until a primary source confirms them.</p>
    <p class="meta">Verified as of {escape(as_of.isoformat())} / {len(items)} companies monitored</p>
    <section class="cards">{card_html}</section>
  </header>
  <main>
    <p class="notice">Research dashboard only. This page does not recommend buying, selling, or sizing a position.</p>
    <p class="notice"><a href="/dashboard/sec-alerts">Open SEC filing review queue</a> to inspect newly discovered public filing evidence before changing any company status.</p>
    <p class="notice"><a href="/dashboard/ipo-reviews">Open documented review audit</a> to verify which manual SEC decisions produced this generated registry.</p>
    <h2>Status board</h2>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Company</th><th>Status</th><th>Verified</th><th>Ticker</th><th>Next event</th><th>Evidence</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    <h2>Monitoring queue</h2>
    <section class="timeline">{timeline}</section>
  </main>
</body>
</html>
"""


def write_ipo_watch_html(path: str | Path, items: list[IpoWatchItem], as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_ipo_watch_html(items, as_of), encoding="utf-8")


def write_ipo_watch_csv(path: str | Path, items: list[IpoWatchItem]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=IPO_WATCH_FIELDNAMES)
        writer.writeheader()
        for item in items:
            row = dict(item.__dict__)
            row["status_date"] = item.status_date.isoformat()
            writer.writerow(row)


def _validate_as_of(items: list[IpoWatchItem], as_of: date) -> None:
    future = [item.company_name for item in items if item.status_date > as_of]
    if future:
        names = ", ".join(sorted(future))
        raise IpoWatchDataError(f"Report as-of date predates status evidence for: {names}")
