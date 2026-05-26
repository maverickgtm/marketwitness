from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date, datetime
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

JPX_SOURCE_URL = "https://www.jpx.co.jp/english/listing/stocks/new/index.html"
_DATE_PAIR = re.compile(
    r"(?P<listing>[A-Z][a-z]{2}\.?\s+\d{1,2},\s+\d{4})\s*"
    r"\((?P<approval>[A-Z][a-z]{2}\.?\s+\d{1,2},\s+\d{4})\)"
)


class JpxDataError(ValueError):
    """Raised when JPX new-listing evidence is unusable."""


@dataclass(frozen=True)
class JpxNewListing:
    company_name: str
    security_code: str
    market_segment: str
    approval_date: date
    listing_date: date
    status: str
    observed_on: date
    source_url: str
    outline_url: str


def fetch_jpx_new_listings() -> list[JpxNewListing]:
    request = Request(
        JPX_SOURCE_URL,
        headers={
            "User-Agent": "MarketWitness/0.1 public-research-monitor",
            "Accept": "text/html",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            page = response.read().decode("utf-8", errors="replace")
    except (URLError, TimeoutError, OSError) as exc:
        raise JpxDataError(f"Unable to retrieve JPX new listings: {exc}") from exc
    return parse_jpx_html(page, date.today())


def load_jpx_snapshot(path: str | Path, observed_on: date) -> list[JpxNewListing]:
    try:
        page = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise JpxDataError(f"Unable to read JPX snapshot {path}: {exc}") from exc
    return parse_jpx_html(page, observed_on)


def parse_jpx_html(page: str, observed_on: date) -> list[JpxNewListing]:
    parser = _JpxListingsParser()
    parser.feed(page)
    listings: list[JpxNewListing] = []
    seen: set[tuple[str, date]] = set()
    for index, (cells, pdf_links) in enumerate(parser.rows):
        if not cells:
            continue
        match = _DATE_PAIR.search(cells[0])
        if not match:
            continue
        if len(cells) < 3 or index + 1 >= len(parser.rows):
            raise JpxDataError("JPX listing is missing required table cells.")
        following_cells, _ = parser.rows[index + 1]
        if not following_cells or not pdf_links:
            raise JpxDataError("JPX listing is missing market segment or outline evidence.")
        listing_date = _parse_date(match.group("listing"))
        approval_date = _parse_date(match.group("approval"))
        company_name = cells[1].strip()
        security_code = cells[2].strip()
        market_segment = following_cells[0].strip()
        key = (security_code, listing_date)
        if not company_name or not security_code or not market_segment or key in seen:
            raise JpxDataError("JPX listing contains blank or duplicate identity fields.")
        seen.add(key)
        listings.append(
            JpxNewListing(
                company_name=company_name,
                security_code=security_code,
                market_segment=market_segment,
                approval_date=approval_date,
                listing_date=listing_date,
                status=(
                    "listed"
                    if listing_date <= observed_on
                    else "approved_pending_listing"
                ),
                observed_on=observed_on,
                source_url=JPX_SOURCE_URL,
                outline_url=urljoin(JPX_SOURCE_URL, pdf_links[0]),
            )
        )
    if not listings:
        raise JpxDataError("JPX page does not contain new-listing rows.")
    return listings


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value.replace(".", ""), "%b %d, %Y").date()
    except ValueError as exc:
        raise JpxDataError(f"JPX listing contains invalid date: {value}") from exc


class _JpxListingsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[tuple[list[str], list[str]]] = []
        self._in_table = False
        self._in_row = False
        self._in_cell = False
        self._cells: list[str] = []
        self._cell_parts: list[str] = []
        self._pdf_links: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        if tag == "table" and "widetable" in (attributes.get("class") or ""):
            self._in_table = True
        elif self._in_table and tag == "tr":
            self._in_row = True
            self._cells = []
            self._pdf_links = []
        elif self._in_row and tag == "td":
            self._in_cell = True
            self._cell_parts = []
        elif self._in_cell and tag == "a":
            href = attributes.get("href") or ""
            if href.casefold().endswith(".pdf"):
                self._pdf_links.append(href)

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._in_cell:
            self._cells.append(" ".join(" ".join(self._cell_parts).split()))
            self._in_cell = False
        elif tag == "tr" and self._in_row:
            if self._cells:
                self.rows.append((self._cells, self._pdf_links))
            self._in_row = False
        elif tag == "table" and self._in_table:
            self._in_table = False


def write_jpx_csv(path: str | Path, listings: list[JpxNewListing]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(JpxNewListing.__annotations__))
        writer.writeheader()
        for listing in listings:
            row = dict(listing.__dict__)
            row["approval_date"] = listing.approval_date.isoformat()
            row["listing_date"] = listing.listing_date.isoformat()
            row["observed_on"] = listing.observed_on.isoformat()
            writer.writerow(row)


def render_jpx_report(listings: list[JpxNewListing], as_of: date) -> str:
    _validate_as_of(listings, as_of)
    latest = sorted(listings, key=lambda item: item.listing_date, reverse=True)
    lines = [
        "# JPX New Listings Monitor",
        "",
        f"- Report generated as of: `{as_of.isoformat()}`",
        f"- Official page: <{JPX_SOURCE_URL}>",
        f"- New-listing records observed: `{len(listings)}`",
        "",
        "This monitor reads the official Tokyo Stock Exchange New Listings table.",
        "An approval is an official listing milestone; it is not an investment",
        "recommendation and does not replace EDINET offering-document review.",
        "",
        "## Listing Confirmations",
        "",
        "| Listing Date | Approval Date | Issuer | Code | Segment | State | Evidence |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in latest:
        lines.append(
            f"| {item.listing_date.isoformat()} | {item.approval_date.isoformat()} | "
            f"{item.company_name} | {item.security_code} | {item.market_segment} | "
            f"`{item.status}` | [JPX outline]({item.outline_url}) |"
        )
    return "\n".join(lines) + "\n"


def write_jpx_report(
    path: str | Path, listings: list[JpxNewListing], as_of: date
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_jpx_report(listings, as_of), encoding="utf-8")


def render_jpx_html(listings: list[JpxNewListing], as_of: date) -> str:
    _validate_as_of(listings, as_of)
    latest = sorted(listings, key=lambda item: item.listing_date, reverse=True)
    rows = "".join(
        "<tr>"
        f"<td>{escape(item.listing_date.isoformat())}<small>Approved {escape(item.approval_date.isoformat())}</small></td>"
        f"<td><strong>{escape(item.company_name)}</strong></td>"
        f"<td>{escape(item.security_code)}</td>"
        f"<td>{escape(item.market_segment)}</td>"
        f'<td><span class="badge">{escape(item.status)}</span></td>'
        f'<td><a href="{escape(item.outline_url)}">JPX outline</a></td>'
        "</tr>"
        for item in latest
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarketWitness | JPX New Listings</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1120px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:780px}}
.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:220px;display:inline-block;margin:35px 0}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}td small{{display:block;color:var(--muted)}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}a{{color:var(--mint);text-decoration:none}}.badge{{color:var(--mint);background:rgba(86,218,172,.12);border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}
@media(max-width:800px){{.table-wrap{{overflow-x:auto}}table{{min-width:820px}}}}
</style></head><body><header><nav><a href="/dashboard/global-listings">Global Listings Watch</a> / JPX</nav>
<h1>Tokyo.<br>New listings.</h1><p class="lead">Listing approvals and scheduled or completed listings observed in the official JPX table.</p>
<p class="meta">Observed as of {escape(as_of.isoformat())}</p><article class="card"><p>Official records</p><strong>{len(listings)}</strong></article></header>
<main><p class="notice">A JPX listing approval is a verified exchange milestone, not a trading instruction. EDINET offering-document collection remains a separate next step.</p>
<h2>Listing confirmations</h2><div class="table-wrap"><table><thead><tr><th>Listing date</th><th>Issuer</th><th>Code</th><th>Segment</th><th>State</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_jpx_html(path: str | Path, listings: list[JpxNewListing], as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_jpx_html(listings, as_of), encoding="utf-8")


def _validate_as_of(listings: list[JpxNewListing], as_of: date) -> None:
    if any(item.observed_on > as_of for item in listings):
        raise JpxDataError("JPX snapshot includes a future observation.")
