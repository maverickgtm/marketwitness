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

TSX_SOURCE_URL = "https://www.tsx.com/en/news/new-company-listings"


class TsxDataError(ValueError):
    """Raised when TSX new-company-listing evidence is unusable."""


@dataclass(frozen=True)
class TsxNewListing:
    company_name: str
    symbols: str
    listing_date: date
    status: str
    observed_on: date
    source_url: str
    detail_url: str


def fetch_tsx_new_listings() -> list[TsxNewListing]:
    request = Request(
        TSX_SOURCE_URL,
        headers={
            "User-Agent": "TargetAudit/0.1 public-research-monitor",
            "Accept": "text/html",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            page = response.read().decode("utf-8", errors="replace")
    except (URLError, TimeoutError, OSError) as exc:
        raise TsxDataError(f"Unable to retrieve TSX new listings: {exc}") from exc
    return parse_tsx_html(page, date.today())


def load_tsx_snapshot(path: str | Path, observed_on: date) -> list[TsxNewListing]:
    try:
        page = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise TsxDataError(f"Unable to read TSX snapshot {path}: {exc}") from exc
    return parse_tsx_html(page, observed_on)


def parse_tsx_html(page: str, observed_on: date) -> list[TsxNewListing]:
    parser = _TsxListingsParser()
    parser.feed(page)
    if not parser.rows:
        raise TsxDataError("TSX page does not contain new-company listing rows.")
    listings: list[TsxNewListing] = []
    seen: set[tuple[str, date]] = set()
    for raw_date, label, detail_href in parser.rows:
        try:
            listing_date = datetime.strptime(raw_date, "%B %d, %Y").date()
        except ValueError as exc:
            raise TsxDataError(f"TSX listing contains invalid date: {raw_date}") from exc
        company, symbols = _split_label(label)
        key = (company.casefold(), listing_date)
        if not company or key in seen:
            raise TsxDataError("TSX listing contains blank or duplicate company.")
        seen.add(key)
        listings.append(
            TsxNewListing(
                company_name=company,
                symbols=symbols,
                listing_date=listing_date,
                status="listed",
                observed_on=observed_on,
                source_url=TSX_SOURCE_URL,
                detail_url=urljoin(TSX_SOURCE_URL, detail_href),
            )
        )
    return listings


def _split_label(label: str) -> tuple[str, str]:
    clean = " ".join(label.split())
    match = re.match(r"^(?P<company>.+?)\s+\((?P<symbols>[^()]*)\)$", clean)
    if not match:
        return clean, "-"
    return match.group("company").strip(), match.group("symbols").strip() or "-"


class _TsxListingsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[tuple[str, str, str]] = []
        self._in_table = False
        self._in_row = False
        self._in_cell = False
        self._cells: list[str] = []
        self._cell_parts: list[str] = []
        self._href = ""

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        if tag == "table" and "two-columns-list" in (attributes.get("class") or ""):
            self._in_table = True
        elif self._in_table and tag == "tr":
            self._in_row = True
            self._cells = []
            self._href = ""
        elif self._in_row and tag == "td":
            self._in_cell = True
            self._cell_parts = []
        elif self._in_cell and tag == "a":
            self._href = attributes.get("href") or ""

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._in_cell:
            self._cells.append(" ".join(" ".join(self._cell_parts).split()))
            self._in_cell = False
        elif tag == "tr" and self._in_row:
            if len(self._cells) >= 2 and self._href:
                self.rows.append((self._cells[0], self._cells[1], self._href))
            self._in_row = False
        elif tag == "table" and self._in_table:
            self._in_table = False


def write_tsx_csv(path: str | Path, listings: list[TsxNewListing]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(TsxNewListing.__annotations__))
        writer.writeheader()
        for listing in listings:
            row = dict(listing.__dict__)
            row["listing_date"] = listing.listing_date.isoformat()
            row["observed_on"] = listing.observed_on.isoformat()
            writer.writerow(row)


def render_tsx_report(listings: list[TsxNewListing], as_of: date) -> str:
    _validate_as_of(listings, as_of)
    latest = sorted(listings, key=lambda listing: listing.listing_date, reverse=True)
    lines = [
        "# TSX New Company Listings Monitor",
        "",
        f"- Report generated as of: `{as_of.isoformat()}`",
        f"- Official page: <{TSX_SOURCE_URL}>",
        f"- Listed records observed: `{len(listings)}`",
        "",
        "This monitor reads the official TSX New Company Listings table. Its",
        "records confirm listed companies shown by TSX; it is not a queue of",
        "upcoming applications or an investment recommendation.",
        "",
        "## Latest Listings",
        "",
        "| Listing Date | Company | Symbol(s) | State | Source |",
        "|---|---|---|---|---|",
    ]
    for listing in latest:
        lines.append(
            f"| {listing.listing_date.isoformat()} | {listing.company_name} | "
            f"{listing.symbols} | `{listing.status}` | "
            f"[TSX]({listing.detail_url}) |"
        )
    return "\n".join(lines) + "\n"


def write_tsx_report(path: str | Path, listings: list[TsxNewListing], as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_tsx_report(listings, as_of), encoding="utf-8")


def render_tsx_html(listings: list[TsxNewListing], as_of: date) -> str:
    _validate_as_of(listings, as_of)
    latest = sorted(listings, key=lambda listing: listing.listing_date, reverse=True)
    rows = "".join(
        "<tr>"
        f"<td>{escape(item.listing_date.isoformat())}</td>"
        f"<td><strong>{escape(item.company_name)}</strong></td>"
        f"<td>{escape(item.symbols)}</td>"
        f'<td><span class="badge">{escape(item.status)}</span></td>'
        f'<td><a href="{escape(item.detail_url)}">TSX</a></td>'
        "</tr>"
        for item in latest
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | TSX New Company Listings</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1120px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:780px}}
.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:220px;display:inline-block;margin:35px 0}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}a{{color:var(--mint);text-decoration:none}}.badge{{color:var(--mint);background:rgba(86,218,172,.12);border-radius:999px;padding:5px 9px;font-size:12px}}
@media(max-width:800px){{.table-wrap{{overflow-x:auto}}table{{min-width:700px}}}}
</style></head><body><header><nav>TargetAudit / Global Listings Watch / TSX</nav>
<h1>Canada.<br>New listings.</h1><p class="lead">Companies observed in the official Toronto Stock Exchange New Company Listings table.</p>
<p class="meta">Observed as of {escape(as_of.isoformat())}</p><article class="card"><p>Listed records</p><strong>{len(listings)}</strong></article></header>
<main><p class="notice">This is confirmation of completed listings published by TSX, not a forward-looking IPO signal or a trading instruction.</p>
<h2>Latest listings</h2><div class="table-wrap"><table><thead><tr><th>Date</th><th>Company</th><th>Symbol(s)</th><th>State</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_tsx_html(path: str | Path, listings: list[TsxNewListing], as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_tsx_html(listings, as_of), encoding="utf-8")


def _validate_as_of(listings: list[TsxNewListing], as_of: date) -> None:
    if any(item.observed_on > as_of for item in listings):
        raise TsxDataError("TSX snapshot includes a future observation.")
