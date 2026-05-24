from __future__ import annotations

import csv
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ..etf_holdings import Holding

SEC_NPORT_DATASETS_URL = "https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets"
SHARE_UNITS = {"NS", "SH", "SHARES"}
_SYMBOL_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9.:\-]{0,29}$")


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


def load_nport_xml_snapshot(
    path: str | Path,
    fund_symbol: str,
    captured_on: date,
    source_url: str = SEC_NPORT_DATASETS_URL,
    synthetic_fixture: bool = False,
) -> SecNportImport:
    symbol = _symbol(fund_symbol)
    if not source_url.startswith("https://"):
        raise SecNportDataError("N-PORT import requires an HTTPS source URL.")
    try:
        root = ET.fromstring(Path(path).read_text(encoding="utf-8"))
    except (OSError, ET.ParseError) as exc:
        raise SecNportDataError(f"Unable to read N-PORT XML snapshot {path}: {exc}") from exc
    submission_type = _required_text(root, "submissionType", path)
    if submission_type not in {"NPORT-P", "NPORT-P/A"}:
        raise SecNportDataError(f"{path}: SEC document is not public NPORT-P evidence.")
    registrant = _required_text(root, "regName", path)
    fund_name = _required_text(root, "seriesName", path)
    series_id = _required_text(root, "seriesId", path)
    effective_date = _date_text(_required_text(root, "repPdEnd", path), path)
    if captured_on < effective_date:
        raise SecNportDataError(f"{path}: capture precedes the N-PORT reporting period.")
    issuer = "TargetAudit Synthetic N-PORT Fixture" if synthetic_fixture else registrant
    source_mode = "synthetic_fixture" if synthetic_fixture else "sec_filing"
    investments = _elements(root, "invstOrSec")
    if not investments:
        raise SecNportDataError(f"{path}: N-PORT XML contains no investments.")
    holdings: list[Holding] = []
    identifiers: set[str] = set()
    omitted = 0
    for investment in investments:
        units = _optional_text(investment, "units").upper()
        if units not in SHARE_UNITS:
            omitted += 1
            continue
        company = _required_text(investment, "name", path)
        identifier = _investment_identifier(investment, path)
        shares = _decimal_text(_required_text(investment, "balance", path), "balance", path)
        weight = _decimal_text(_required_text(investment, "pctVal", path), "pctVal", path)
        if shares < 0 or weight < 0 or weight > 100:
            raise SecNportDataError(f"{path}: N-PORT share position has invalid amounts.")
        if identifier.casefold() in identifiers:
            raise SecNportDataError(f"{path}: duplicate normalized N-PORT holding {identifier}.")
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
        raise SecNportDataError(f"{path}: N-PORT XML has no share-denominated holdings.")
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
