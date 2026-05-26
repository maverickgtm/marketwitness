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
    "restricted_research_only",
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
        f"- Restricted research-only markets: `{counts['restricted_research_only']}`",
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
    expansion_count = counts["priority_connector"] + counts["planned_connector"]
    cards = [
        ("Mapped markets", len(markets), "Official sources identified"),
        ("Live feeds", counts["live_official_feed"], "LSE, HKEX, ASX, TSX, JPX, SGX, CVM, ESMA and OpenDART implemented"),
        ("Verified snapshots", counts["verified_snapshot"], "Official capture, not continuous"),
        (
            "Restricted",
            counts["restricted_research_only"],
            "Documented only; no ingestion",
        ),
        (
            "Expansion queue",
            expansion_count,
            f"{counts['priority_connector']} priority; {counts['planned_connector']} planned",
        ),
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
        f'<td><a href="{escape(market.official_source_url)}" target="_blank" rel="noopener">Official source</a></td>'
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
    coverage_grid = "".join(
        f'<article class="market-node {escape(market.connector_status)}">'
        f"<strong>{escape(market.market_code)}</strong>"
        f"<small>{escape(market.jurisdiction)}</small></article>"
        for market in markets
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>MarketWitness | Global Listings Watch</title>
  <style>
    :root {{
      --bg:#060b13; --panel:#101a27; --panel2:#142131; --line:#223246; --text:#f2f6f7;
      --muted:#96aab8; --mint:#38dfad; --gold:#f3bf66; --blue:#62a6ff; --rose:#f48687;
      --shadow:0 22px 68px rgba(0,0,0,.24);
    }}
    * {{ box-sizing:border-box; }} body {{ margin:0; color:var(--text);
      background:radial-gradient(circle at 88% 0%,rgba(56,223,173,.12),transparent 28%),var(--bg);
      font:15px/1.5 Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; }}
    header, main {{ max-width:1370px; margin:auto; padding:23px 28px; }}
    nav,.eyebrow {{ color:var(--muted); text-transform:uppercase; letter-spacing:.12em; font-size:11px; }}
    .top {{ display:flex; justify-content:space-between; align-items:center; gap:18px; margin-bottom:32px; }}
    .back {{ color:var(--text); border:1px solid var(--line); border-radius:10px; padding:9px 14px; font-weight:600; }}
    .hero {{ display:grid; grid-template-columns:minmax(480px,1.03fr) minmax(420px,.97fr); gap:18px; }}
    .hero-copy,.coverage-panel,.card,.table-wrap,.queue-item,.notice {{ background:var(--panel); border:1px solid var(--line); border-radius:18px; }}
    .hero-copy {{ padding:32px 34px; box-shadow:var(--shadow); }}
    h1 {{ font-size:clamp(42px,5vw,62px); letter-spacing:-.045em; line-height:1.04; margin:14px 0; }}
    h1 span {{ color:var(--mint); }}
    .lead {{ color:var(--muted); max-width:630px; font-size:17px; }}
    .meta {{ color:var(--muted); margin-top:27px; font-size:12px; text-transform:uppercase; letter-spacing:.1em; }}
    .hero-links {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:27px; }}
    .hero-links a {{ border:1px solid var(--line); padding:10px 14px; border-radius:10px; font-weight:600; }}
    .hero-links .primary {{ color:#061117; background:var(--mint); border-color:var(--mint); }}
    .coverage-panel {{ padding:21px; box-shadow:var(--shadow); }}
    .coverage-head {{ display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:18px; }}
    .coverage-head strong {{ font-size:17px; }} .coverage-head span {{ color:var(--mint); background:rgba(56,223,173,.12); border-radius:999px; padding:5px 9px; font-size:11px; }}
    .coverage-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:9px; }}
    .market-node {{ border-radius:12px; background:var(--panel2); border:1px solid transparent; padding:12px; min-height:71px; }}
    .market-node strong {{ display:block; font-size:15px; margin-bottom:4px; }} .market-node small {{ display:block; color:var(--muted); font-size:11px; }}
    .market-node.live_official_feed {{ border-color:rgba(56,223,173,.25); }} .market-node.live_official_feed strong {{ color:var(--mint); }}
    .market-node.restricted_research_only {{ border-color:rgba(244,134,135,.25); }} .market-node.restricted_research_only strong {{ color:var(--rose); }}
    .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:13px; margin:18px 0 0; }}
    .card {{ padding:16px 18px; border-radius:16px; }} .card p {{ margin:0; color:var(--muted); }}
    .card strong {{ display:block; color:var(--mint); letter-spacing:-.04em; font-size:35px; }}
    .card small {{ color:var(--muted); }}
    .notice {{ border-left:3px solid var(--gold); padding:15px 18px; color:var(--muted); border-radius:15px; }}
    .monitor-links {{ display:flex; flex-wrap:wrap; gap:12px; margin:20px 0 34px; }}
    .monitor-links a {{ border:1px solid var(--line); border-radius:10px; padding:10px 14px;
      background:var(--panel); font-weight:600; }}
    h2 {{ margin-top:39px; letter-spacing:-.02em; }} .table-wrap {{ overflow:hidden; margin-top:16px; }}
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
    .restricted_research_only {{ color:var(--rose); background:rgba(244,134,135,.12); }}
    .queue {{ display:grid; grid-template-columns:repeat(2,1fr); gap:13px; }}
    .queue-item {{ padding:17px; }} .queue-item div {{ display:flex; gap:13px; align-items:baseline; }}
    .queue-item h3 {{ margin:0; color:var(--mint); }} .queue-item span {{ color:var(--muted); }}
    .queue-item p {{ margin:9px 0 0; }}
    @media (max-width:1060px) {{ .hero {{ grid-template-columns:1fr; }} }}
    @media (max-width:800px) {{ header,main {{ padding:18px 14px; }} .top {{ align-items:flex-start; flex-direction:column; }}
      .coverage-grid {{ grid-template-columns:repeat(2,1fr); }} .cards,.queue {{ grid-template-columns:1fr; }}
      .hero-copy {{ padding:25px 20px; }}
      .table-wrap {{ overflow-x:auto; }} table {{ min-width:880px; }} }}
  </style>
</head>
<body>
  <header>
    <div class="top"><nav>MarketWitness / <a href="/dashboard/open">Open Edition</a> / <a href="/dashboard/ipo">IPO Watch Center</a> / Global Listings Watch</nav><a class="back" href="/dashboard/open">Back to terminal</a></div>
    <section class="hero">
      <article class="hero-copy">
        <p class="eyebrow">International evidence network</p>
        <h1>Beyond Wall Street.<br><span>Listings worldwide.</span></h1>
        <p class="lead">Map official signals for IPOs and new listings across London, Hong Kong and additional exchanges without blending incompatible regulatory evidence.</p>
        <p class="meta">Sources reviewed as of {escape(as_of.isoformat())}</p>
        <div class="hero-links"><a class="primary" href="/dashboard/global-alerts">Open change review</a><a href="/dashboard/contribute?lang=en">Contribute source</a></div>
      </article>
      <article class="coverage-panel">
        <div class="coverage-head"><strong>Coverage Grid</strong><span>Official paths</span></div>
        <section class="coverage-grid">{coverage_grid}</section>
      </article>
    </section>
    <section class="cards">{cards_html}</section>
  </header>
  <main>
    <p class="notice">HKEX, LSE, ASX, TSX, JPX, SGX, CVM, ESMA and OpenDART have official ingestion paths. CVM, ESMA and OpenDART evidence open regulatory review; they are not proof of trading. A separate issuer-release registry preserves confirmed milestones without turning them into investment conclusions.</p>
    <section class="monitor-links" aria-label="Monitoring pages">
      <a href="/dashboard/contribute?lang=en">Contribute an official source</a>
      <a href="/dashboard/global-alerts">Open daily change review</a>
      <a href="/dashboard/global/hkex">Open HKEX live monitor</a>
      <a href="/dashboard/global/lse-upcoming">Open LSE live monitor</a>
      <a href="/dashboard/document-checks">Open LSE / FCA check</a>
      <a href="/dashboard/global/asx">Open ASX live monitor</a>
      <a href="/dashboard/global/tsx">Open TSX listing confirmations</a>
      <a href="/dashboard/global/jpx">Open JPX listing confirmations</a>
      <a href="/dashboard/global/edinet">Open EDINET offering filings</a>
      <a href="/dashboard/global/cvm">Open CVM equity offerings</a>
      <a href="/dashboard/global/esma">Open ESMA equity prospectuses</a>
      <a href="/dashboard/global/opendart">Open Korea equity filings</a>
      <a href="/dashboard/global/sgx">Open SGX prospectus monitor</a>
      <a href="/dashboard/issuer-confirmations">Open issuer confirmations</a>
      <a href="/dashboard/etf-regulatory">Open ETF regulatory holdings</a>
      <a href="/dashboard/governance">Open source governance</a>
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
