from __future__ import annotations

import csv
import io
import re
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from .sec import configured_user_agent


SEC_INSIDER_DATASETS_URL = (
    "https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets"
)
SEC_INSIDER_README_URL = "https://www.sec.gov/files/insider_transactions_readme.pdf"
_ZIP_PATTERN = re.compile(r"(?P<quarter>\d{4}q[1-4])_form345\.zip$", re.IGNORECASE)
_REQUIRED_TABLES = ("SUBMISSION.tsv", "REPORTINGOWNER.tsv", "NONDERIV_TRANS.tsv")
# Public summary totals hold extraordinary per-row values for filing review.
PUBLIC_TOTAL_REVIEW_THRESHOLD = Decimal("10000000000")
FIELDNAMES = (
    "accession_number",
    "filing_date",
    "transaction_date",
    "issuer_cik",
    "issuer_name",
    "ticker",
    "document_type",
    "reporting_owners",
    "owner_relationships",
    "security_title",
    "transaction_code",
    "transaction_class",
    "shares",
    "price_per_share",
    "transaction_value",
    "aff10b5one",
    "source_mode",
    "observed_on",
    "source_url",
)


class SecInsiderDataError(ValueError):
    """Raised when SEC insider-transaction evidence cannot be normalized."""


@dataclass(frozen=True)
class SecInsiderRelease:
    quarter: str
    download_url: str


@dataclass(frozen=True)
class InsiderTransaction:
    accession_number: str
    filing_date: date
    transaction_date: date
    issuer_cik: str
    issuer_name: str
    ticker: str
    document_type: str
    reporting_owners: str
    owner_relationships: str
    security_title: str
    transaction_code: str
    transaction_class: str
    shares: Decimal | None
    price_per_share: Decimal | None
    transaction_value: Decimal | None
    aff10b5one: str
    source_mode: str
    observed_on: date
    source_url: str


def fetch_insider_transactions(
    observed_on: date,
    quarter: str | None = None,
    user_agent: str | None = None,
) -> tuple[list[InsiderTransaction], SecInsiderRelease]:
    agent = configured_user_agent(user_agent)
    releases = fetch_insider_catalog(agent)
    selected = select_insider_release(releases, quarter or releases[0].quarter)
    request = Request(
        selected.download_url,
        headers={"User-Agent": agent, "Accept": "application/zip"},
    )
    try:
        with urlopen(request, timeout=120) as response:
            content = response.read()
    except (URLError, TimeoutError, OSError) as exc:
        raise SecInsiderDataError(f"Unable to retrieve SEC insider ZIP: {exc}") from exc
    return parse_insider_zip(
        content, observed_on, "official_quarterly_dataset", selected.download_url
    ), selected


def fetch_insider_catalog(user_agent: str | None = None) -> list[SecInsiderRelease]:
    request = Request(
        SEC_INSIDER_DATASETS_URL,
        headers={
            "User-Agent": configured_user_agent(user_agent),
            "Accept": "text/html",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            page = response.read().decode("utf-8")
    except (URLError, TimeoutError, OSError, UnicodeDecodeError) as exc:
        raise SecInsiderDataError(f"Unable to retrieve SEC insider catalog: {exc}") from exc
    return parse_insider_catalog(page)


def load_insider_catalog(path: str | Path) -> list[SecInsiderRelease]:
    try:
        return parse_insider_catalog(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise SecInsiderDataError(f"Unable to read SEC insider catalog snapshot: {exc}") from exc


def parse_insider_catalog(page: str) -> list[SecInsiderRelease]:
    parser = _CatalogLinkParser()
    parser.feed(page)
    releases: dict[str, SecInsiderRelease] = {}
    for href in parser.hrefs:
        match = _ZIP_PATTERN.search(href)
        if not match:
            continue
        quarter = match.group("quarter").lower()
        release = SecInsiderRelease(quarter, urljoin(SEC_INSIDER_DATASETS_URL, href))
        if quarter in releases and releases[quarter] != release:
            raise SecInsiderDataError(f"SEC insider catalog duplicates release {quarter}.")
        releases[quarter] = release
    if not releases:
        raise SecInsiderDataError("SEC insider catalog contains no quarterly ZIP links.")
    return sorted(releases.values(), key=lambda item: item.quarter, reverse=True)


def select_insider_release(
    releases: list[SecInsiderRelease], quarter: str
) -> SecInsiderRelease:
    requested = quarter.strip().lower()
    if not re.fullmatch(r"\d{4}q[1-4]", requested):
        raise SecInsiderDataError(f"Invalid SEC insider quarter: {quarter!r}.")
    for release in releases:
        if release.quarter == requested:
            return release
    raise SecInsiderDataError(f"SEC insider catalog does not publish quarter {requested}.")


def load_insider_dataset(
    directory: str | Path, observed_on: date, synthetic_fixture: bool = False
) -> list[InsiderTransaction]:
    root = Path(directory)
    try:
        tables = {name: (root / name).read_text(encoding="utf-8") for name in _REQUIRED_TABLES}
    except OSError as exc:
        raise SecInsiderDataError(f"Unable to read SEC insider dataset tables: {exc}") from exc
    mode = "synthetic_fixture" if synthetic_fixture else "official_quarterly_dataset"
    return parse_insider_tables(tables, observed_on, mode, SEC_INSIDER_DATASETS_URL)


def parse_insider_zip(
    content: bytes, observed_on: date, source_mode: str, source_url: str
) -> list[InsiderTransaction]:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            members = {Path(name).name.upper(): name for name in archive.namelist()}
            if not all(name.upper() in members for name in _REQUIRED_TABLES):
                raise SecInsiderDataError("SEC insider ZIP is missing required tables.")
            tables = {
                name: archive.read(members[name.upper()]).decode("utf-8")
                for name in _REQUIRED_TABLES
            }
    except (zipfile.BadZipFile, UnicodeDecodeError) as exc:
        raise SecInsiderDataError(f"Unable to read SEC insider ZIP: {exc}") from exc
    return parse_insider_tables(tables, observed_on, source_mode, source_url)


def parse_insider_tables(
    tables: dict[str, str],
    observed_on: date,
    source_mode: str,
    source_url: str,
) -> list[InsiderTransaction]:
    if source_mode not in {"synthetic_fixture", "official_quarterly_dataset"}:
        raise SecInsiderDataError(f"Unsupported SEC insider source mode: {source_mode}.")
    submissions: dict[str, dict[str, str]] = {}
    for row in _rows(tables["SUBMISSION.tsv"]):
        accession = _required(row, "ACCESSION_NUMBER")
        if accession in submissions:
            raise SecInsiderDataError("SEC insider submissions contain duplicate accession numbers.")
        submissions[accession] = row
    owners: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in _rows(tables["REPORTINGOWNER.tsv"]):
        owners[_required(row, "ACCESSION_NUMBER")].append(row)
    records: list[InsiderTransaction] = []
    seen: set[tuple[str, str]] = set()
    for row in _rows(tables["NONDERIV_TRANS.tsv"]):
        accession = _required(row, "ACCESSION_NUMBER")
        submission = submissions.get(accession)
        if submission is None:
            raise SecInsiderDataError("SEC insider transaction lacks a matching submission.")
        identifier = (accession, _required(row, "NONDERIV_TRANS_SK"))
        if identifier in seen:
            raise SecInsiderDataError("SEC insider dataset contains duplicate transactions.")
        seen.add(identifier)
        filing_date = _sec_date(_required(submission, "FILING_DATE"))
        transaction_date = _sec_date(_required(row, "TRANS_DATE"))
        if filing_date > observed_on:
            raise SecInsiderDataError("SEC insider dataset contains a filing after observation date.")
        code = row.get("TRANS_CODE", "").strip().upper() or "UNSPECIFIED"
        shares = _optional_decimal(row.get("TRANS_SHARES", ""))
        price = _optional_decimal(row.get("TRANS_PRICEPERSHARE", ""))
        transaction_class = (
            "post_filing_dated_nonderivative"
            if transaction_date > filing_date
            else _transaction_class(code, shares, price)
        )
        value = shares * price if transaction_class in {
            "reported_purchase",
            "reported_sale",
        } else None
        if value is not None and value > PUBLIC_TOTAL_REVIEW_THRESHOLD:
            transaction_class = f"{transaction_class}_review_required"
        owner_rows = owners.get(accession, [])
        records.append(
            InsiderTransaction(
                accession_number=accession,
                filing_date=filing_date,
                transaction_date=transaction_date,
                issuer_cik=_required(submission, "ISSUERCIK").zfill(10),
                issuer_name=_required(submission, "ISSUERNAME"),
                ticker=submission.get("ISSUERTRADINGSYMBOL", "").strip().upper() or "N/A",
                document_type=_required(submission, "DOCUMENT_TYPE"),
                reporting_owners="; ".join(
                    sorted({_required(item, "RPTOWNERNAME") for item in owner_rows})
                )
                or "Unspecified reporting owner",
                owner_relationships="; ".join(
                    sorted(
                        {
                            item.get("RPTOWNER_RELATIONSHIP", "").strip()
                            for item in owner_rows
                            if item.get("RPTOWNER_RELATIONSHIP", "").strip()
                        }
                    )
                )
                or "Not stated",
                security_title=_required(row, "SECURITY_TITLE"),
                transaction_code=code,
                transaction_class=transaction_class,
                shares=shares,
                price_per_share=price,
                transaction_value=value,
                aff10b5one=submission.get("AFF10B5ONE", "").strip().lower(),
                source_mode=source_mode,
                observed_on=observed_on,
                source_url=source_url,
            )
        )
    if not records:
        raise SecInsiderDataError("SEC insider dataset contains no non-derivative transactions.")
    return sorted(records, key=lambda item: (item.transaction_date, item.ticker, item.accession_number))


def write_insider_csv(path: str | Path, records: list[InsiderTransaction]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for item in records:
            writer.writerow(
                {
                    **item.__dict__,
                    "filing_date": item.filing_date.isoformat(),
                    "transaction_date": item.transaction_date.isoformat(),
                    "shares": item.shares if item.shares is not None else "",
                    "price_per_share": (
                        item.price_per_share if item.price_per_share is not None else ""
                    ),
                    "transaction_value": (
                        item.transaction_value if item.transaction_value is not None else ""
                    ),
                    "observed_on": item.observed_on.isoformat(),
                }
            )


def load_insider_csv(path: str | Path) -> list[InsiderTransaction]:
    try:
        with Path(path).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        raise SecInsiderDataError(f"Unable to read SEC insider CSV: {exc}") from exc
    records = []
    for row in rows:
        if not set(FIELDNAMES).issubset(row):
            raise SecInsiderDataError("SEC insider CSV is missing required fields.")
        records.append(
            InsiderTransaction(
                accession_number=row["accession_number"],
                filing_date=date.fromisoformat(row["filing_date"]),
                transaction_date=date.fromisoformat(row["transaction_date"]),
                issuer_cik=row["issuer_cik"],
                issuer_name=row["issuer_name"],
                ticker=row["ticker"],
                document_type=row["document_type"],
                reporting_owners=row["reporting_owners"],
                owner_relationships=row["owner_relationships"],
                security_title=row["security_title"],
                transaction_code=row["transaction_code"],
                transaction_class=row["transaction_class"],
                shares=_optional_decimal(row["shares"]),
                price_per_share=_optional_decimal(row["price_per_share"]),
                transaction_value=_optional_decimal(row["transaction_value"]),
                aff10b5one=row["aff10b5one"],
                source_mode=row["source_mode"],
                observed_on=date.fromisoformat(row["observed_on"]),
                source_url=row["source_url"],
            )
        )
    if not records:
        raise SecInsiderDataError("SEC insider CSV contains no observations.")
    return records


def build_insider_snapshot(
    records: list[InsiderTransaction],
    days: int = 30,
    side: str = "all",
    query: str = "",
) -> dict[str, object]:
    if days not in {30, 60, 90, 365}:
        raise SecInsiderDataError("Insider window must be 30, 60, 90 or 365 days.")
    if side not in {"all", "purchase", "sale"}:
        raise SecInsiderDataError("Insider side must be all, purchase or sale.")
    observed_records = [item for item in records if item.transaction_date <= item.filing_date]
    if not observed_records:
        raise SecInsiderDataError("SEC insider artifact has no transactions observed by its cutoff.")
    latest = max(item.transaction_date for item in observed_records)
    start = latest - timedelta(days=days - 1)
    searchable = query.strip().casefold()
    scoped = [
        item
        for item in observed_records
        if item.transaction_date >= start
        and (
            not searchable
            or searchable in item.ticker.casefold()
            or searchable in item.issuer_name.casefold()
            or searchable in item.reporting_owners.casefold()
        )
    ]
    declared = [
        item
        for item in scoped
        if item.transaction_class in {"reported_purchase", "reported_sale"}
        and (
            side == "all"
            or (side == "purchase" and item.transaction_class == "reported_purchase")
            or (side == "sale" and item.transaction_class == "reported_sale")
        )
    ]
    purchases = [item for item in declared if item.transaction_class == "reported_purchase"]
    sales = [item for item in declared if item.transaction_class == "reported_sale"]
    purchase_value = sum((item.transaction_value or Decimal("0") for item in purchases), Decimal("0"))
    sale_value = sum((item.transaction_value or Decimal("0") for item in sales), Decimal("0"))
    issuer_totals: dict[tuple[str, str], dict[str, Decimal | int]] = defaultdict(
        lambda: {"purchases": Decimal("0"), "sales": Decimal("0"), "transactions": 0}
    )
    for item in declared:
        key = (item.ticker, item.issuer_name)
        issuer_totals[key]["transactions"] = int(issuer_totals[key]["transactions"]) + 1
        key_value = "purchases" if item.transaction_class == "reported_purchase" else "sales"
        issuer_totals[key][key_value] = Decimal(issuer_totals[key][key_value]) + (
            item.transaction_value or Decimal("0")
        )
    issuers = sorted(
        (
            {
                "ticker": key[0],
                "issuer_name": key[1],
                "purchase_value": str(value["purchases"]),
                "sale_value": str(value["sales"]),
                "net_declared_value": str(Decimal(value["purchases"]) - Decimal(value["sales"])),
                "transaction_count": value["transactions"],
            }
            for key, value in issuer_totals.items()
        ),
        key=lambda item: abs(Decimal(str(item["net_declared_value"]))),
        reverse=True,
    )
    modes = {item.source_mode for item in records}
    return {
        "available": True,
        "product": "Insider Activity Lab",
        "data_mode": (
            "Official SEC quarterly Form 3/4/5 dataset"
            if modes == {"official_quarterly_dataset"}
            else "Synthetic reproducible SEC-shaped fixture"
        ),
        "as_of": max(item.observed_on for item in records).isoformat(),
        "latest_transaction_date": latest.isoformat(),
        "period_start": start.isoformat(),
        "selected_days": days,
        "selected_side": side,
        "query": query,
        "transaction_count": len(declared),
        "purchase_count": len(purchases),
        "sale_count": len(sales),
        "purchase_value": str(purchase_value),
        "sale_value": str(sale_value),
        "net_declared_value": str(purchase_value - sale_value),
        "public_total_review_threshold": str(PUBLIC_TOTAL_REVIEW_THRESHOLD),
        "other_nonderivative_count": sum(
            item.transaction_class
            in {"other_nonderivative", "unpriced_purchase", "unpriced_sale"}
            for item in scoped
        ),
        "value_review_required_count": sum(
            item.transaction_class
            in {"reported_purchase_review_required", "reported_sale_review_required"}
            for item in scoped
        ),
        "post_filing_dated_count": sum(
            item.transaction_class == "post_filing_dated_nonderivative" for item in records
        ),
        "issuers": issuers[:12],
        "transactions": [_payload(item) for item in reversed(declared[-30:])],
        "publication_boundary": (
            "This view totals priced non-derivative SEC transaction codes P and S only. "
            "Those codes cover reported purchases or sales and may include private "
            "transactions; they are not assumed to be open-market trades. Awards, gifts, "
            "other codes, rows dated after their filing and declared values above US$10 billion per row are excluded for review. The quarterly as-filed dataset must be checked "
            "against the original filing before any investment decision."
        ),
    }


def write_insider_report(
    path: str | Path, records: list[InsiderTransaction], observed_on: date, source_mode: str
) -> None:
    snapshot = build_insider_snapshot(records, days=90)
    lines = [
        "# SEC Insider Activity Lab",
        "",
        f"- Observed: `{observed_on.isoformat()}`",
        f"- Source mode: `{source_mode}`",
        f"- Non-derivative transaction records: `{len(records)}`",
        f"- Priced P/S purchase/sale records in latest 90-day dataset window: `{snapshot['transaction_count']}`",
        f"- Excluded other non-derivative codes in selected window: `{snapshot['other_nonderivative_count']}`",
        f"- Extraordinary declared-value rows held for review: `{snapshot['value_review_required_count']}`",
        f"- Rows dated after their filing excluded from observed totals: `{snapshot['post_filing_dated_count']}`",
        "",
        snapshot["publication_boundary"],
        "",
        "| Ticker | Issuer | Priced P-code value | Priced S-code value | Net declared value |",
        "|---|---|---:|---:|---:|",
    ]
    for item in snapshot["issuers"]:
        lines.append(
            f"| {item['ticker']} | {item['issuer_name']} | {_format_money(item['purchase_value'])} | "
            f"{_format_money(item['sale_value'])} | {_format_money(item['net_declared_value'])} |"
        )
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_insider_html(
    path: str | Path, records: list[InsiderTransaction], observed_on: date, source_mode: str
) -> None:
    snapshot = build_insider_snapshot(records, days=90)
    rows = "".join(
        f"<tr><td>{escape(str(item['ticker']))}</td><td>{escape(str(item['issuer_name']))}</td>"
        f"<td>{escape(_format_money(item['purchase_value']))}</td><td>{escape(_format_money(item['sale_value']))}</td>"
        f"<td>{escape(_format_money(item['net_declared_value']))}</td></tr>"
        for item in snapshot["issuers"]
    )
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>MarketWitness | SEC Insider Activity</title>
<style>body{{margin:0;background:#070d16;color:#e9f0f5;font:15px Arial,sans-serif}}header,main{{max-width:1080px;margin:auto;padding:32px}}h1{{font-size:44px;margin:10px 0}}p{{color:#9fb0c0;line-height:1.6}}strong,a{{color:#58dfb0}}table{{width:100%;border-collapse:collapse;background:#121d2c;border-radius:14px;overflow:hidden}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #27364b}}th{{color:#9fb0c0}}</style>
<header><p>OFFICIAL QUARTERLY OWNERSHIP DISCLOSURE</p><h1>Insider activity.<br>Classified, not assumed.</h1><p>SEC Forms 3, 4 and 5 non-derivative records. Totals include only priced P/S purchase or sale codes; those codes may include private transactions.</p><p>Collected on <strong>{observed_on.isoformat()}</strong> / {escape(source_mode)} / <a href="{SEC_INSIDER_DATASETS_URL}">SEC dataset source</a></p></header>
<main><p>{escape(str(snapshot['publication_boundary']))}</p><table><thead><tr><th>Ticker</th><th>Issuer</th><th>Purchases</th><th>Sales</th><th>Net declared value</th></tr></thead><tbody>{rows}</tbody></table></main></html>""",
        encoding="utf-8",
    )


def _rows(content: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(content), delimiter="\t"))


def _required(row: dict[str, str], key: str) -> str:
    value = row.get(key, "").strip()
    if not value:
        raise SecInsiderDataError(f"SEC insider row is missing {key}.")
    return value


def _sec_date(value: str) -> date:
    try:
        return (
            date.fromisoformat(value)
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)
            else datetime.strptime(value.upper(), "%d-%b-%Y").date()
        )
    except ValueError as exc:
        raise SecInsiderDataError(f"SEC insider row has invalid date: {value}.") from exc


def _optional_decimal(value: str) -> Decimal | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise SecInsiderDataError(f"SEC insider row has invalid numeric value: {value}.") from exc


def _transaction_class(
    code: str, shares: Decimal | None, price: Decimal | None
) -> str:
    if code == "P":
        return "reported_purchase" if shares is not None and price is not None else "unpriced_purchase"
    if code == "S":
        return "reported_sale" if shares is not None and price is not None else "unpriced_sale"
    return "other_nonderivative"


def _payload(item: InsiderTransaction) -> dict[str, object]:
    return {
        "accession_number": item.accession_number,
        "filing_date": item.filing_date.isoformat(),
        "transaction_date": item.transaction_date.isoformat(),
        "ticker": item.ticker,
        "issuer_name": item.issuer_name,
        "reporting_owners": item.reporting_owners,
        "owner_relationships": item.owner_relationships,
        "security_title": item.security_title,
        "transaction_code": item.transaction_code,
        "transaction_class": item.transaction_class,
        "shares": str(item.shares) if item.shares is not None else None,
        "price_per_share": str(item.price_per_share) if item.price_per_share is not None else None,
        "transaction_value": str(item.transaction_value) if item.transaction_value is not None else None,
        "aff10b5one": item.aff10b5one,
        "source_url": item.source_url,
    }


def _format_money(value: object) -> str:
    amount = Decimal(str(value))
    sign = "-" if amount < 0 else ""
    return f"{sign}${abs(amount):,.2f}"


class _CatalogLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)
