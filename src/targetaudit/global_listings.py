from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

CONNECTOR_STATUSES = {
    "live_official_feed",
    "verified_snapshot",
    "priority_connector",
    "planned_connector",
}
GLOBAL_SOURCE_COLUMNS = {
    "market_code",
    "market_name",
    "jurisdiction",
    "connector_status",
    "official_source_name",
    "official_source_url",
    "signal_type",
    "confirmation_rule",
    "implementation_next",
}


class GlobalListingsDataError(ValueError):
    """Raised when global-listings source configuration is invalid."""


@dataclass(frozen=True)
class GlobalMarketSource:
    market_code: str
    market_name: str
    jurisdiction: str
    connector_status: str
    official_source_name: str
    official_source_url: str
    signal_type: str
    confirmation_rule: str
    implementation_next: str


def load_global_market_sources(path: str | Path) -> list[GlobalMarketSource]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        missing = sorted(GLOBAL_SOURCE_COLUMNS - set(reader.fieldnames or []))
        if missing:
            raise GlobalListingsDataError(
                f"{path}: missing columns: {', '.join(missing)}"
            )
        markets: list[GlobalMarketSource] = []
        seen: set[str] = set()
        for index, row in enumerate(reader, start=2):
            code = row["market_code"].strip().upper()
            status = row["connector_status"].strip()
            if not code or code in seen:
                raise GlobalListingsDataError(
                    f"{path}: blank or duplicate market code on row {index}"
                )
            if status not in CONNECTOR_STATUSES:
                raise GlobalListingsDataError(f"{path}: invalid status on row {index}")
            required_values = [
                row["market_name"].strip(),
                row["jurisdiction"].strip(),
                row["official_source_name"].strip(),
                row["official_source_url"].strip(),
                row["signal_type"].strip(),
                row["confirmation_rule"].strip(),
                row["implementation_next"].strip(),
            ]
            if not all(required_values):
                raise GlobalListingsDataError(f"{path}: missing content on row {index}")
            seen.add(code)
            markets.append(
                GlobalMarketSource(
                    market_code=code,
                    market_name=row["market_name"].strip(),
                    jurisdiction=row["jurisdiction"].strip(),
                    connector_status=status,
                    official_source_name=row["official_source_name"].strip(),
                    official_source_url=row["official_source_url"].strip(),
                    signal_type=row["signal_type"].strip(),
                    confirmation_rule=row["confirmation_rule"].strip(),
                    implementation_next=row["implementation_next"].strip(),
                )
            )
        return markets


def render_global_listings_report(markets: list[GlobalMarketSource], as_of: date) -> str:
    counts = Counter(market.connector_status for market in markets)
    lines = [
        "# Global Listings Watch",
        "",
        f"- Source review date: `{as_of.isoformat()}`",
        f"- Markets mapped: `{len(markets)}`",
        f"- Live official feeds: `{counts['live_official_feed']}`",
        f"- Verified snapshots: `{counts['verified_snapshot']}`",
        f"- Priority connectors: `{counts['priority_connector']}`",
        f"- Planned official connectors: `{counts['planned_connector']}`",
        "",
        "This coverage map defines where official listing signals can be monitored.",
        "Only `live_official_feed` identifies an implemented ingestion path. A",
        "`verified_snapshot` captures official evidence but is not continuous.",
        "",
        "## Coverage Map",
        "",
        "| Market | Jurisdiction | Status | Official Signal | Confirmation Rule |",
        "|---|---|---|---|---|",
    ]
    for market in markets:
        lines.append(
            f"| {market.market_name} | {market.jurisdiction} | "
            f"`{market.connector_status}` | "
            f"[{market.official_source_name}]({market.official_source_url}) | "
            f"{market.confirmation_rule} |"
        )
    lines.extend(["", "## Build Queue", ""])
    for market in markets:
        lines.extend(
            [
                f"### {market.market_name}",
                "",
                f"- Signal type: {market.signal_type}",
                f"- Next implementation: {market.implementation_next}",
                "",
            ]
        )
    return "\n".join(lines)


def write_global_listings_report(
    path: str | Path, markets: list[GlobalMarketSource], as_of: date
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_global_listings_report(markets, as_of), encoding="utf-8")


def render_global_listings_html(markets: list[GlobalMarketSource], as_of: date) -> str:
    counts = Counter(market.connector_status for market in markets)
    cards = [
        ("Mapped markets", len(markets), "Official sources identified"),
        ("Live feeds", counts["live_official_feed"], "LSE and HKEX implemented"),
        ("Verified snapshots", counts["verified_snapshot"], "Official capture, not continuous"),
        ("Expansion queue", counts["planned_connector"], "Official sources to connect"),
    ]
    cards_html = "".join(
        f'<article class="card"><p>{escape(label)}</p><strong>{count}</strong>'
        f"<small>{escape(description)}</small></article>"
        for label, count, description in cards
    )
    rows = "".join(
        "<tr>"
        f"<td><strong>{escape(market.market_name)}</strong><small>{escape(market.jurisdiction)}</small></td>"
        f'<td><span class="badge {escape(market.connector_status)}">{escape(market.connector_status)}</span></td>'
        f"<td>{escape(market.signal_type)}</td>"
        f"<td>{escape(market.confirmation_rule)}</td>"
        f'<td><a href="{escape(market.official_source_url)}">Official source</a></td>'
        "</tr>"
        for market in markets
    )
    queue = "".join(
        "<article class=\"queue-item\">"
        f"<div><h3>{escape(market.market_code)}</h3>"
        f"<span>{escape(market.market_name)}</span></div>"
        f"<p>{escape(market.implementation_next)}</p>"
        "</article>"
        for market in markets
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TargetAudit | Global Listings Watch</title>
  <style>
    :root {{
      --bg:#071016; --panel:#0f1c24; --line:#20343d; --text:#edf1ef;
      --muted:#98abb0; --mint:#56daac; --gold:#f0bc62; --blue:#62a6ff;
    }}
    * {{ box-sizing:border-box; }} body {{ margin:0; background:var(--bg); color:var(--text);
      font:15px/1.5 Inter,Arial,sans-serif; }}
    header, main {{ max-width:1180px; margin:auto; padding:30px 28px; }}
    nav {{ color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:13px; }}
    h1 {{ font-size:clamp(34px,5vw,54px); line-height:1.06; margin:38px 0 14px; }}
    .lead {{ color:var(--muted); max-width:740px; font-size:17px; }}
    .meta {{ color:var(--muted); margin-top:30px; font-size:13px; }}
    .cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:35px 0; }}
    .card,.table-wrap,.queue-item,.notice {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; }}
    .card {{ padding:18px 20px; }} .card p {{ margin:0; color:var(--muted); }}
    .card strong {{ display:block; color:var(--mint); font-size:38px; }}
    .card small {{ color:var(--muted); }}
    .notice {{ border-left:3px solid var(--gold); padding:15px 18px; color:var(--muted); }}
    .monitor-links {{ display:flex; flex-wrap:wrap; gap:12px; margin:20px 0 34px; }}
    .monitor-links a {{ border:1px solid var(--line); border-radius:10px; padding:11px 15px;
      background:var(--panel); font-weight:600; }}
    h2 {{ margin-top:42px; }} .table-wrap {{ overflow:hidden; margin-top:16px; }}
    table {{ width:100%; border-collapse:collapse; }}
    th,td {{ padding:15px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
    th {{ font-size:12px; text-transform:uppercase; color:var(--muted); font-weight:500; }}
    td small {{ display:block; color:var(--muted); }}
    a {{ color:var(--mint); text-decoration:none; }}
    .badge {{ border-radius:999px; padding:5px 9px; font-size:12px; white-space:nowrap; }}
    .priority_connector {{ color:var(--gold); background:rgba(240,188,98,.12); }}
    .planned_connector {{ color:var(--blue); background:rgba(98,166,255,.12); }}
    .live_official_feed {{ color:var(--mint); background:rgba(86,218,172,.12); }}
    .verified_snapshot {{ color:var(--gold); background:rgba(240,188,98,.12); }}
    .queue {{ display:grid; grid-template-columns:repeat(2,1fr); gap:14px; }}
    .queue-item {{ padding:17px; }} .queue-item div {{ display:flex; gap:13px; align-items:baseline; }}
    .queue-item h3 {{ margin:0; color:var(--mint); }} .queue-item span {{ color:var(--muted); }}
    .queue-item p {{ margin:9px 0 0; }}
    @media (max-width:800px) {{ .cards,.queue {{ grid-template-columns:1fr; }}
      .table-wrap {{ overflow-x:auto; }} table {{ min-width:880px; }} }}
  </style>
</head>
<body>
  <header>
    <nav>TargetAudit / Global Listings Watch</nav>
    <h1>Beyond Wall Street.<br>Listings worldwide.</h1>
    <p class="lead">Map official signals for IPOs and new listings across London, Hong Kong and additional exchanges without blending incompatible regulatory evidence.</p>
    <p class="meta">Sources reviewed as of {escape(as_of.isoformat())}</p>
    <section class="cards">{cards_html}</section>
  </header>
  <main>
    <p class="notice">HKEX and LSE now have official JSON ingestion paths. Expected listings still require document-level confirmation before promotion.</p>
    <section class="monitor-links" aria-label="Monitoring pages">
      <a href="hkex-monitor.html">Open HKEX live monitor</a>
      <a href="lse-upcoming.html">Open LSE live monitor</a>
    </section>
    <h2>Official source map</h2>
    <div class="table-wrap"><table>
      <thead><tr><th>Market</th><th>Status</th><th>Signal</th><th>Confirmation rule</th><th>Evidence</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
    <h2>Connector build queue</h2>
    <section class="queue">{queue}</section>
  </main>
</body></html>"""


def write_global_listings_html(
    path: str | Path, markets: list[GlobalMarketSource], as_of: date
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_global_listings_html(markets, as_of), encoding="utf-8")
