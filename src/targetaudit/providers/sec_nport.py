from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Callable
from urllib.error import URLError
from urllib.request import Request, urlopen

from ..etf_holdings import Holding
from .sec import configured_user_agent

SEC_NPORT_DATASETS_URL = "https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_ARCHIVES_ROOT = "https://www.sec.gov/Archives"
SHARE_UNITS = {"NS", "SH", "SHARES"}
_SYMBOL_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9.:\-]{0,29}$")
_CIK_PATTERN = re.compile(r"^\d{1,10}$")
_ACCESSION_PATTERN = re.compile(r"^\d{10}-\d{2}-\d{6}$")


class SecNportDataError(ValueError):
    """Raised when SEC N-PORT evidence cannot be normalized conservatively."""


@dataclass(frozen=True)
class SecNportImport:
    registrant_name: str
    fund_symbol: str
    fund_name: str
    series_id: str
    effective_date: date
    captured_on: date
    holdings: tuple[Holding, ...]
    reported_investments: int
    omitted_non_share_positions: int
    source_url: str
    source_mode: str


@dataclass(frozen=True)
class SecNportFiling:
    cik: str
    accession_number: str
    form: str
    filed_date: date
    primary_document: str
    source_url: str


@dataclass(frozen=True)
class SecNportCollection:
    filing: SecNportFiling
    imported: SecNportImport
    archived_xml: Path


def submissions_url(cik: str) -> str:
    return SEC_SUBMISSIONS_URL.format(cik=_cik(cik))


def fetch_recent_nport_filings(
    cik: str, user_agent: str | None = None
) -> list[SecNportFiling]:
    source_url = submissions_url(cik)
    request = Request(
        source_url,
        headers={
            "User-Agent": configured_user_agent(user_agent),
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise SecNportDataError(f"Unable to retrieve SEC submissions data: {exc}") from exc
    return parse_recent_nport_filings(payload, cik)


def load_recent_nport_filings(
    path: str | Path,
    cik: str,
    archive_root: str = SEC_ARCHIVES_ROOT,
) -> list[SecNportFiling]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SecNportDataError(f"Unable to read SEC submissions snapshot {path}: {exc}") from exc
    return parse_recent_nport_filings(payload, cik, archive_root)


def parse_recent_nport_filings(
    payload: object,
    cik: str,
    archive_root: str = SEC_ARCHIVES_ROOT,
) -> list[SecNportFiling]:
    normalized_cik = _cik(cik)
    if not archive_root.startswith("https://"):
        raise SecNportDataError("SEC N-PORT filing URLs must use HTTPS.")
    if not isinstance(payload, dict):
        raise SecNportDataError("Unexpected SEC submissions payload.")
    filings = payload.get("filings")
    recent = filings.get("recent") if isinstance(filings, dict) else None
    if not isinstance(recent, dict):
        raise SecNportDataError("SEC submissions payload is missing recent filings.")
    required = ["form", "filingDate", "accessionNumber", "primaryDocument"]
    values = [recent.get(field) for field in required]
    if not all(isinstance(value, list) for value in values):
        raise SecNportDataError("SEC submissions recent filings are missing expected fields.")
    lengths = {len(value) for value in values}
    if len(lengths) != 1:
        raise SecNportDataError("SEC submissions recent filing columns are misaligned.")
    result: list[SecNportFiling] = []
    for form, filed_raw, accession, primary_document in zip(*values):
        if form not in {"NPORT-P", "NPORT-P/A"}:
            continue
        accession = str(accession).strip()
        document = str(primary_document).strip()
        if not _ACCESSION_PATTERN.fullmatch(accession):
            raise SecNportDataError("SEC N-PORT filing has an invalid accession number.")
        document_path = Path(document)
        if (
            not document
            or document_path.is_absolute()
            or ".." in document_path.parts
            or "\\" in document
        ):
            raise SecNportDataError("SEC N-PORT filing has an invalid primary document name.")
        document = _raw_xml_document(document)
        try:
            filed_date = date.fromisoformat(str(filed_raw))
        except ValueError as exc:
            raise SecNportDataError("SEC N-PORT filing has an invalid filing date.") from exc
        archive_path = (
            f"edgar/data/{int(normalized_cik)}/{accession.replace('-', '')}/{document}"
        )
        result.append(
            SecNportFiling(
                cik=normalized_cik,
                accession_number=accession,
                form=str(form),
                filed_date=filed_date,
                primary_document=document,
                source_url=f"{archive_root.rstrip('/')}/{archive_path}",
            )
        )
    return sorted(result, key=lambda filing: filing.filed_date, reverse=True)


def fetch_nport_document(filing: SecNportFiling, user_agent: str | None = None) -> str:
    request = Request(
        filing.source_url,
        headers={
            "User-Agent": configured_user_agent(user_agent),
            "Accept": "application/xml,text/xml",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8")
    except (URLError, TimeoutError, OSError, UnicodeDecodeError) as exc:
        raise SecNportDataError(f"Unable to retrieve SEC N-PORT document: {exc}") from exc


def load_nport_document(path: str | Path) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise SecNportDataError(f"Unable to read SEC N-PORT document {path}: {exc}") from exc


def collect_latest_nport_snapshot(
    filings: list[SecNportFiling],
    series_id: str,
    fund_symbol: str,
    captured_on: date,
    archive_dir: str | Path,
    document_loader: Callable[[SecNportFiling], str],
    synthetic_fixture: bool = False,
) -> SecNportCollection:
    requested_series = series_id.strip().upper()
    if not requested_series.startswith("S") or not requested_series[1:].isalnum():
        raise SecNportDataError(f"Invalid SEC series identifier: {series_id!r}.")
    for filing in filings:
        if filing.filed_date > captured_on:
            continue
        document = document_loader(filing)
        try:
            root = ET.fromstring(document)
        except ET.ParseError as exc:
            raise SecNportDataError(
                f"SEC N-PORT document {filing.accession_number} is not parseable XML."
            ) from exc
        candidate_series = _optional_text(root, "seriesId").upper()
        if candidate_series != requested_series:
            continue
        destination = (
            Path(archive_dir)
            / captured_on.isoformat()
            / requested_series
            / f"{filing.accession_number}.xml"
        )
        imported = _normalize_nport_xml_document(
            document,
            filing.source_url,
            fund_symbol,
            captured_on,
            filing.source_url,
            synthetic_fixture,
        )
        if imported.series_id.upper() != requested_series:
            raise SecNportDataError("Validated N-PORT filing does not match requested series.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(document, encoding="utf-8")
        return SecNportCollection(filing=filing, imported=imported, archived_xml=destination)
    raise SecNportDataError(
        f"No recent public NPORT-P filing matched SEC series {requested_series}."
    )


def load_nport_xml_snapshot(
    path: str | Path,
    fund_symbol: str,
    captured_on: date,
    source_url: str = SEC_NPORT_DATASETS_URL,
    synthetic_fixture: bool = False,
) -> SecNportImport:
    if not source_url.startswith("https://"):
        raise SecNportDataError("N-PORT import requires an HTTPS source URL.")
    try:
        document = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise SecNportDataError(f"Unable to read N-PORT XML snapshot {path}: {exc}") from exc
    return _normalize_nport_xml_document(
        document, path, fund_symbol, captured_on, source_url, synthetic_fixture
    )


def _normalize_nport_xml_document(
    document: str,
    evidence_label: str | Path,
    fund_symbol: str,
    captured_on: date,
    source_url: str,
    synthetic_fixture: bool,
) -> SecNportImport:
    symbol = _symbol(fund_symbol)
    try:
        root = ET.fromstring(document)
    except ET.ParseError as exc:
        raise SecNportDataError(
            f"Unable to read N-PORT XML snapshot {evidence_label}: {exc}"
        ) from exc
    submission_type = _required_text(root, "submissionType", evidence_label)
    if submission_type not in {"NPORT-P", "NPORT-P/A"}:
        raise SecNportDataError(
            f"{evidence_label}: SEC document is not public NPORT-P evidence."
        )
    registrant = _required_text(root, "regName", evidence_label)
    fund_name = _required_text(root, "seriesName", evidence_label)
    series_id = _required_text(root, "seriesId", evidence_label)
    effective_date = _date_text(
        _required_text(root, "repPdEnd", evidence_label), evidence_label
    )
    if captured_on < effective_date:
        raise SecNportDataError(
            f"{evidence_label}: capture precedes the N-PORT reporting period."
        )
    issuer = "TargetAudit Synthetic N-PORT Fixture" if synthetic_fixture else registrant
    source_mode = "synthetic_fixture" if synthetic_fixture else "sec_filing"
    investments = _elements(root, "invstOrSec")
    if not investments:
        raise SecNportDataError(f"{evidence_label}: N-PORT XML contains no investments.")
    holdings: list[Holding] = []
    identifiers: set[str] = set()
    omitted = 0
    for investment in investments:
        units = _optional_text(investment, "units").upper()
        if units not in SHARE_UNITS:
            omitted += 1
            continue
        company = _required_text(investment, "name", evidence_label)
        identifier = _investment_identifier(investment, evidence_label)
        shares = _decimal_text(
            _required_text(investment, "balance", evidence_label),
            "balance",
            evidence_label,
        )
        weight = _decimal_text(
            _required_text(investment, "pctVal", evidence_label),
            "pctVal",
            evidence_label,
        )
        if shares < 0 or weight < 0 or weight > 100:
            raise SecNportDataError(
                f"{evidence_label}: N-PORT share position has invalid amounts."
            )
        if identifier.casefold() in identifiers:
            raise SecNportDataError(
                f"{evidence_label}: duplicate normalized N-PORT holding {identifier}."
            )
        identifiers.add(identifier.casefold())
        holdings.append(
            Holding(
                issuer=issuer,
                fund_symbol=symbol,
                fund_name=fund_name,
                effective_date=effective_date,
                captured_on=captured_on,
                position_ticker=identifier,
                position_name=company,
                shares=shares,
                weight_pct=weight,
                source_frequency="regulatory_periodic",
                source_url=source_url,
            )
        )
    if not holdings:
        raise SecNportDataError(
            f"{evidence_label}: N-PORT XML has no share-denominated holdings."
        )
    return SecNportImport(
        registrant_name=issuer,
        fund_symbol=symbol,
        fund_name=fund_name,
        series_id=series_id,
        effective_date=effective_date,
        captured_on=captured_on,
        holdings=tuple(holdings),
        reported_investments=len(investments),
        omitted_non_share_positions=omitted,
        source_url=source_url,
        source_mode=source_mode,
    )


def write_normalized_holdings(path: str | Path, imported: SecNportImport) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(Holding.__annotations__))
        writer.writeheader()
        for holding in imported.holdings:
            row = dict(holding.__dict__)
            row["effective_date"] = holding.effective_date.isoformat()
            row["captured_on"] = holding.captured_on.isoformat()
            writer.writerow(row)


def render_import_report(imported: SecNportImport) -> str:
    return "\n".join(
        [
            "# SEC N-PORT ETF Holdings Import",
            "",
            f"- Fund: `{imported.fund_symbol}` - {imported.fund_name}",
            f"- Registrant: {imported.registrant_name}",
            f"- Series ID: `{imported.series_id}`",
            f"- Input mode: `{imported.source_mode}`",
            "- Source frequency layer: `regulatory_periodic`",
            f"- Reporting period end: `{imported.effective_date.isoformat()}`",
            f"- Captured on: `{imported.captured_on.isoformat()}`",
            f"- Investments in filing: `{imported.reported_investments}`",
            f"- Share positions normalized: `{len(imported.holdings)}`",
            f"- Non-share positions omitted: `{imported.omitted_non_share_positions}`",
            f"- SEC source: <{imported.source_url}>",
            "",
            "Form N-PORT is a regulatory portfolio report. The SEC data-set page",
            "states that public data are derived from disseminated filings, updated",
            "quarterly, and do not substitute for reviewing the filing itself.",
            "",
            "TargetAudit normalizes only positions reported in share units for this",
            "initial ETF diff layer. It does not treat periodic N-PORT evidence as",
            "a daily holdings feed or as a buy/sell recommendation.",
            "",
        ]
    )


def write_import_report(path: str | Path, imported: SecNportImport) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_import_report(imported), encoding="utf-8")


def render_collection_report(collection: SecNportCollection) -> str:
    return (
        render_import_report(collection.imported)
        + "\n## EDGAR Collection\n\n"
        + f"- Registrant CIK: `{collection.filing.cik}`\n"
        + f"- Accession number: `{collection.filing.accession_number}`\n"
        + f"- Filing date: `{collection.filing.filed_date.isoformat()}`\n"
        + f"- Archived XML: `{collection.archived_xml}`\n\n"
        + "The collector scans recent submissions for the registrant CIK, then\n"
        + "accepts a filing only after its XML confirms the requested `seriesId`.\n"
    )


def write_collection_report(path: str | Path, collection: SecNportCollection) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_collection_report(collection), encoding="utf-8")


def _elements(root: ET.Element, name: str) -> list[ET.Element]:
    return [element for element in root.iter() if _local_name(element.tag) == name]


def _optional_text(root: ET.Element, name: str) -> str:
    matches = _elements(root, name)
    return (matches[0].text or "").strip() if matches else ""


def _required_text(root: ET.Element, name: str, path: str | Path) -> str:
    result = _optional_text(root, name)
    if not result:
        raise SecNportDataError(f"{path}: N-PORT XML is missing {name}.")
    return result


def _investment_identifier(investment: ET.Element, path: str | Path) -> str:
    for element in _elements(investment, "ticker"):
        ticker = (element.attrib.get("value") or element.text or "").strip().upper()
        if ticker:
            return _symbol(ticker)
    cusip = _optional_text(investment, "cusip").upper()
    if cusip:
        return _symbol(f"CUSIP:{cusip}")
    raise SecNportDataError(f"{path}: N-PORT share position lacks ticker or CUSIP.")


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _symbol(value: str) -> str:
    symbol = value.strip().upper()
    if not _SYMBOL_PATTERN.fullmatch(symbol):
        raise SecNportDataError(f"Invalid N-PORT symbol: {value!r}.")
    return symbol


def _cik(value: str) -> str:
    stripped = value.strip()
    if not _CIK_PATTERN.fullmatch(stripped):
        raise SecNportDataError(f"Invalid SEC CIK: {value!r}.")
    return stripped.zfill(10)


def _raw_xml_document(document: str) -> str:
    parts = Path(document).parts
    if len(parts) == 2 and parts[0].startswith("xslFormNPORT-"):
        return parts[1]
    return document


def _date_text(value: str, path: str | Path) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SecNportDataError(f"{path}: invalid N-PORT reporting date.") from exc


def _decimal_text(value: str, name: str, path: str | Path) -> Decimal:
    try:
        result = Decimal(value.replace(",", "").strip())
    except InvalidOperation as exc:
        raise SecNportDataError(f"{path}: invalid N-PORT {name}.") from exc
    if not result.is_finite():
        raise SecNportDataError(f"{path}: invalid N-PORT {name}.")
    return result
