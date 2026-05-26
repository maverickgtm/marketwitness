from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

HKEX_SOURCE_URL = "https://www.hkexnews.hk/app/appindex.html"
HKEX_JSON_BASE_URL = "https://www.hkexnews.hk/ncms/json/eds"
HKEX_FEEDS = {
    "active": "appactive_app_sehk_e.json",
    "active_phip": "appactive_appphip_sehk_e.json",
    "inactive": "appinactive_sehk_e.json",
    "listed": "applisted_sehk_e.json",
    "returned": "appreturned_sehk_e.json",
}


class HkexDataError(ValueError):
    """Raised when an HKEX listing feed is not usable."""


@dataclass(frozen=True)
class HkexListing:
    company_name: str
    status: str
    event_date: date
    stock_code: str
    has_phip: bool
    source_url: str


def feed_url(status: str) -> str:
    try:
        return f"{HKEX_JSON_BASE_URL}/{HKEX_FEEDS[status]}"
    except KeyError as exc:
        raise HkexDataError(f"Unknown HKEX status: {status}") from exc


def fetch_hkex_feeds() -> tuple[list[HkexListing], dict[str, str]]:
    listings: list[HkexListing] = []
    update_dates: dict[str, str] = {}
    for status in HKEX_FEEDS:
        source_url = feed_url(status)
        request = Request(
            source_url,
            headers={
                "User-Agent": "MarketWitness/0.1 public-research-monitor",
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
        except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            raise HkexDataError(f"Unable to retrieve HKEX {status} feed: {exc}") from exc
        parsed, updated = parse_hkex_payload(payload, status, source_url)
        listings.extend(parsed)
        update_dates[status] = updated
    return listings, update_dates


def load_hkex_snapshot(path: str | Path) -> tuple[list[HkexListing], dict[str, str]]:
    directory = Path(path)
    listings: list[HkexListing] = []
    update_dates: dict[str, str] = {}
    for status, filename in HKEX_FEEDS.items():
        source = directory / filename
        try:
            payload = json.loads(source.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise HkexDataError(f"Unable to read HKEX snapshot {source}: {exc}") from exc
        parsed, updated = parse_hkex_payload(payload, status, feed_url(status))
        listings.extend(parsed)
        update_dates[status] = updated
    return listings, update_dates


def parse_hkex_payload(
    payload: object, status: str, source_url: str
) -> tuple[list[HkexListing], str]:
    if status not in HKEX_FEEDS or not isinstance(payload, dict):
        raise HkexDataError("Unexpected HKEX feed payload.")
    rows = payload.get("app")
    updated = payload.get("uDate")
    if not isinstance(rows, list) or not isinstance(updated, str):
        raise HkexDataError("HKEX feed is missing app rows or update date.")
    try:
        datetime.strptime(updated, "%d/%m/%Y")
    except ValueError as exc:
        raise HkexDataError("HKEX feed contains an invalid update date.") from exc
    listings: list[HkexListing] = []
    for row in rows:
        if not isinstance(row, dict):
            raise HkexDataError("HKEX feed contains an invalid listing row.")
        name = str(row.get("a", "")).strip()
        raw_date = str(row.get("rd" if status == "returned" else "d", "")).strip()
        if not name or not raw_date:
            raise HkexDataError("HKEX feed row is missing company or date.")
        try:
            event_date = datetime.strptime(raw_date, "%d/%m/%Y").date()
        except ValueError as exc:
            raise HkexDataError("HKEX feed row contains an invalid event date.") from exc
        listings.append(
            HkexListing(
                company_name=name,
                status=status,
                event_date=event_date,
                stock_code=str(row.get("st", "")).strip(),
                has_phip=bool(row.get("hasPhip", False)),
                source_url=source_url,
            )
        )
    return listings, updated


def write_hkex_csv(path: str | Path, listings: list[HkexListing]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=[
                "company_name",
                "status",
                "event_date",
                "stock_code",
                "has_phip",
                "source_url",
            ],
        )
        writer.writeheader()
        for listing in listings:
            writer.writerow(
                {
                    "company_name": listing.company_name,
                    "status": listing.status,
                    "event_date": listing.event_date.isoformat(),
                    "stock_code": listing.stock_code,
                    "has_phip": str(listing.has_phip).lower(),
                    "source_url": listing.source_url,
                }
            )


def render_hkex_report(
    listings: list[HkexListing], update_dates: dict[str, str], as_of: date
) -> str:
    _validate_hkex_as_of(listings, as_of)
    counts = Counter(item.status for item in listings)
    latest = sorted(listings, key=lambda item: (item.event_date, item.company_name), reverse=True)
    lines = [
        "# HKEX Listing Monitor",
        "",
        f"- Report generated as of: `{as_of.isoformat()}`",
        f"- Official page: <{HKEX_SOURCE_URL}>",
        f"- Active applications: `{counts['active']}`",
        f"- Active applications with PHIP: `{counts['active_phip']}`",
        f"- Inactive applications: `{counts['inactive']}`",
        f"- Listed records: `{counts['listed']}`",
        f"- Returned applications: `{counts['returned']}`",
        "",
        "The monitor reads official HKEXnews AP and PHIP JSON feeds. `Active` and",
        "`PHIP` are regulatory milestones, not an investment recommendation or a",
        "guarantee that a security will begin trading.",
        "",
        "## Feed Updates",
        "",
    ]
    for status in HKEX_FEEDS:
        lines.append(f"- `{status}`: `{update_dates.get(status, 'unknown')}`")
    lines.extend(
        [
            "",
            "## Latest Observed Events",
            "",
            "| Company | State | Event Date | Stock Code | PHIP Flag | Source |",
            "|---|---|---|---|---|---|",
        ]
    )
    for item in latest[:20]:
        lines.append(
            f"| {item.company_name} | `{item.status}` | {item.event_date.isoformat()} | "
            f"{item.stock_code or '-'} | {'yes' if item.has_phip else 'no'} | "
            f"[JSON feed]({item.source_url}) |"
        )
    return "\n".join(lines) + "\n"


def write_hkex_report(
    path: str | Path,
    listings: list[HkexListing],
    update_dates: dict[str, str],
    as_of: date,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_hkex_report(listings, update_dates, as_of), encoding="utf-8"
    )


def render_hkex_html(
    listings: list[HkexListing], update_dates: dict[str, str], as_of: date
) -> str:
    _validate_hkex_as_of(listings, as_of)
    counts = Counter(item.status for item in listings)
    latest = sorted(listings, key=lambda item: (item.event_date, item.company_name), reverse=True)
    labels = {"active_phip": "Active / PHIP"}
    cards = "".join(
        f'<article class="card {status}"><p>{escape(labels.get(status, status.title()))}</p>'
        f"<strong>{counts[status]}</strong><small>Updated {escape(update_dates.get(status, 'unknown'))}</small></article>"
        for status in HKEX_FEEDS
    )
    rows = "".join(
        "<tr>"
        f"<td><strong>{escape(item.company_name)}</strong></td>"
        f'<td><span class="badge {escape(item.status)}">{escape(item.status)}</span></td>'
        f"<td>{escape(item.event_date.isoformat())}</td>"
        f"<td>{escape(item.stock_code or '-')}</td>"
        f"<td>{'yes' if item.has_phip else 'no'}</td>"
        f'<td><a href="{escape(item.source_url)}">JSON</a></td>'
        "</tr>"
        for item in latest[:20]
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarketWitness | HKEX Listing Monitor</title>
<style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}
header,main{{max-width:1180px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}
h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{max-width:760px;color:var(--muted);font-size:17px}}
.cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:15px;margin:35px 0}}.card,.table-wrap,.notice{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}
.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{display:block;font-size:38px;color:var(--mint)}}.card small{{color:var(--muted)}}
.notice{{padding:15px 18px;border-left:3px solid var(--gold);color:var(--muted)}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:14px 15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{font-size:12px;text-transform:uppercase;color:var(--muted);font-weight:500}}
a{{color:var(--mint);text-decoration:none}}.badge{{border-radius:999px;padding:5px 9px;font-size:12px}}.active,.active_phip{{color:var(--gold)}}.listed{{color:var(--mint)}}.inactive,.returned{{color:var(--blue)}}
@media(max-width:820px){{.cards{{grid-template-columns:1fr 1fr}}.table-wrap{{overflow-x:auto}}table{{min-width:720px}}}}
</style></head><body><header><nav><a href="/dashboard/global-listings">Global Listings Watch</a> / HKEX</nav>
<h1>Hong Kong.<br>Official listing signals.</h1>
<p class="lead">Application Proof, PHIP and lifecycle status observations read from official HKEXnews JSON feeds.</p>
<p class="meta">Generated as of {escape(as_of.isoformat())}</p><section class="cards">{cards}</section></header>
<main><p class="notice">Regulatory monitoring only. An active application or PHIP is not a trading instruction and does not guarantee listing.</p>
<h2>Latest observed events</h2><div class="table-wrap"><table><thead><tr><th>Company</th><th>Status</th><th>Date</th><th>Stock code</th><th>PHIP</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div>
</main></body></html>"""


def write_hkex_html(
    path: str | Path,
    listings: list[HkexListing],
    update_dates: dict[str, str],
    as_of: date,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_hkex_html(listings, update_dates, as_of), encoding="utf-8"
    )


def _validate_hkex_as_of(listings: list[HkexListing], as_of: date) -> None:
    future = [item.company_name for item in listings if item.event_date > as_of]
    if future:
        raise HkexDataError(
            f"HKEX feed includes an event after report date: {future[0]}"
        )
