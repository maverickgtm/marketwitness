from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

ASX_SOURCE_URL = "https://www.asx.com.au/listings/upcoming-floats-and-listings"


class AsxDataError(ValueError):
    """Raised when ASX upcoming-listing evidence is unusable."""


@dataclass(frozen=True)
class AsxUpcomingListing:
    company_name: str
    status: str
    listing_date: str
    issue_price: str
    issue_type: str
    security_code: str
    capital_to_be_raised: str
    expected_offer_close_date: str
    observed_on: date
    source_url: str


def fetch_asx_upcoming() -> list[AsxUpcomingListing]:
    request = Request(
        ASX_SOURCE_URL,
        headers={
            "User-Agent": "TargetAudit/0.1 public-research-monitor",
            "Accept": "text/html",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            page = response.read().decode("utf-8", errors="replace")
    except (URLError, TimeoutError, OSError) as exc:
        raise AsxDataError(f"Unable to retrieve ASX upcoming listings: {exc}") from exc
    return parse_asx_html(page, date.today())


def load_asx_snapshot(path: str | Path, observed_on: date) -> list[AsxUpcomingListing]:
    try:
        page = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise AsxDataError(f"Unable to read ASX snapshot {path}: {exc}") from exc
    return parse_asx_html(page, observed_on)


def parse_asx_html(page: str, observed_on: date) -> list[AsxUpcomingListing]:
    parser = _AsxAccordionParser()
    parser.feed(page)
    if not parser.items:
        raise AsxDataError("ASX page does not contain upcoming listing records.")
    listings: list[AsxUpcomingListing] = []
    seen: set[str] = set()
    for title, fields in parser.items:
        company = title.split(" - ", 1)[0].strip()
        listing_date = fields.get("Listing date", "").strip()
        code = fields.get("Security code", "").strip()
        if not company or not listing_date or not code:
            raise AsxDataError("ASX listing record is missing company, date or code.")
        if company.casefold() in seen:
            raise AsxDataError(f"ASX listing record duplicates {company}.")
        seen.add(company.casefold())
        status = "withdrawn" if listing_date.casefold() == "withdrawn" else "anticipated"
        listings.append(
            AsxUpcomingListing(
                company_name=company,
                status=status,
                listing_date=listing_date,
                issue_price=fields.get("Issue price", "-").strip() or "-",
                issue_type=fields.get("Issue type", "-").strip() or "-",
                security_code=code,
                capital_to_be_raised=fields.get("Capital to be raised", "-").strip()
                or "-",
                expected_offer_close_date=fields.get(
                    "Expected offer close date", "-"
                ).strip()
                or "-",
                observed_on=observed_on,
                source_url=ASX_SOURCE_URL,
            )
        )
    return listings


class _AsxAccordionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[tuple[str, dict[str, str]]] = []
        self._depth = 0
        self._title_parts: list[str] = []
        self._fields: dict[str, str] = {}
        self._capture_title = False
        self._in_row = False
        self._in_cell = False
        self._cell_parts: list[str] = []
        self._cells: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        classes = attributes.get("class") or ""
        if tag == "div" and "cmp-accordion__item" in classes:
            if self._depth:
                raise AsxDataError("ASX page contains nested listing records.")
            self._depth = 1
            self._title_parts = []
            self._fields = {}
            return
        if not self._depth:
            return
        if tag == "div":
            self._depth += 1
        if tag == "span" and "cmp-accordion__title" in classes:
            self._capture_title = True
        elif tag == "tr":
            self._in_row = True
            self._cells = []
        elif tag == "td" and self._in_row:
            self._in_cell = True
            self._cell_parts = []

    def handle_data(self, data: str) -> None:
        if self._capture_title:
            self._title_parts.append(data)
        if self._in_cell:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self._depth:
            return
        if tag == "span" and self._capture_title:
            self._capture_title = False
        elif tag == "td" and self._in_cell:
            self._cells.append(_clean_text(" ".join(self._cell_parts)))
            self._in_cell = False
        elif tag == "tr" and self._in_row:
            if len(self._cells) >= 2 and self._cells[0]:
                self._fields[self._cells[0]] = self._cells[1]
            self._in_row = False
        if tag == "div":
            self._depth -= 1
            if not self._depth:
                title = _clean_text(" ".join(self._title_parts))
                if title:
                    self.items.append((title, self._fields))


def _clean_text(value: str) -> str:
    return " ".join(value.split())


def write_asx_csv(path: str | Path, listings: list[AsxUpcomingListing]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(AsxUpcomingListing.__annotations__))
        writer.writeheader()
        for listing in listings:
            row = dict(listing.__dict__)
            row["observed_on"] = listing.observed_on.isoformat()
            writer.writerow(row)


def render_asx_report(listings: list[AsxUpcomingListing], as_of: date) -> str:
    _validate_as_of(listings, as_of)
    counts = Counter(listing.status for listing in listings)
    lines = [
        "# ASX Upcoming Floats And Listings Monitor",
        "",
        f"- Report generated as of: `{as_of.isoformat()}`",
        f"- Official page: <{ASX_SOURCE_URL}>",
        f"- Anticipated listings observed: `{counts['anticipated']}`",
        f"- Withdrawn records observed: `{counts['withdrawn']}`",
        "",
        "ASX states that this page records new listings for which it has received",
        "a formal application. Listing dates and proposed codes remain subject to",
        "change and are not investment instructions.",
        "",
        "## Observed Records",
        "",
        "| Company | State | Listing Date | Code | Issue Price | Capital To Be Raised |",
        "|---|---|---|---|---|---|",
    ]
    for listing in listings:
        lines.append(
            f"| {listing.company_name} | `{listing.status}` | {listing.listing_date} | "
            f"{listing.security_code} | {listing.issue_price} | "
            f"{listing.capital_to_be_raised} |"
        )
    return "\n".join(lines) + "\n"


def write_asx_report(path: str | Path, listings: list[AsxUpcomingListing], as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_asx_report(listings, as_of), encoding="utf-8")


def render_asx_html(listings: list[AsxUpcomingListing], as_of: date) -> str:
    _validate_as_of(listings, as_of)
    counts = Counter(listing.status for listing in listings)
    rows = "".join(
        "<tr>"
        f"<td><strong>{escape(item.company_name)}</strong></td>"
        f'<td><span class="badge {escape(item.status)}">{escape(item.status)}</span></td>'
        f"<td>{escape(item.listing_date)}</td>"
        f"<td>{escape(item.security_code)}</td>"
        f"<td>{escape(item.issue_price)}</td>"
        f"<td>{escape(item.capital_to_be_raised)}</td>"
        "</tr>"
        for item in listings
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | ASX Upcoming Listings</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1120px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:780px}}
.cards{{display:flex;gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:220px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}.badge{{border-radius:999px;padding:5px 9px;font-size:12px}}.anticipated{{color:var(--gold);background:rgba(240,188,98,.12)}}.withdrawn{{color:var(--blue);background:rgba(98,166,255,.12)}}
@media(max-width:800px){{.cards{{display:block}}.card{{margin-bottom:12px}}.table-wrap{{overflow-x:auto}}table{{min-width:760px}}}}
</style></head><body><header><nav><a href="/dashboard/global-listings">Global Listings Watch</a> / ASX</nav>
<h1>Australia.<br>Formal applications.</h1><p class="lead">Upcoming floats and listings observed on the official ASX page after a formal listing application has been received.</p>
<p class="meta">Observed as of {escape(as_of.isoformat())}</p><section class="cards"><article class="card"><p>Anticipated</p><strong>{counts['anticipated']}</strong></article><article class="card"><p>Withdrawn</p><strong>{counts['withdrawn']}</strong></article></section></header>
<main><p class="notice">ASX states that proposed listing dates and security codes can change without notice and must not be relied upon for investment action.</p>
<h2>Observed upcoming listings</h2><div class="table-wrap"><table><thead><tr><th>Company</th><th>State</th><th>Listing date</th><th>Code</th><th>Issue price</th><th>Capital raised</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_asx_html(path: str | Path, listings: list[AsxUpcomingListing], as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_asx_html(listings, as_of), encoding="utf-8")


def _validate_as_of(listings: list[AsxUpcomingListing], as_of: date) -> None:
    future = [item.company_name for item in listings if item.observed_on > as_of]
    if future:
        raise AsxDataError(f"ASX snapshot includes a future observation: {future[0]}")
