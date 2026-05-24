from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ..etf_holdings import Holding

ARK_DOCUMENTS_URL = "https://www.ark-funds.com/download-fund-materials"
ARK_FREQUENCY_REFERENCE_URL = (
    "https://helpcenter.ark-funds.com/"
    "can-you-explain-the-date-listed-on-the-ark-etf-holdings-documents"
)
ARK_REQUIRED_COLUMNS = {
    "date",
    "fund",
    "company",
    "ticker",
    "cusip",
    "shares",
    "weight(%)",
}
_SYMBOL_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9.\-]{0,19}$")


class ArkHoldingsDataError(ValueError):
    """Raised when an ARK holdings CSV cannot be normalized safely."""


@dataclass(frozen=True)
class ArkHoldingsImport:
    fund_symbol: str
    fund_name: str
    holdings: tuple[Holding, ...]
    effective_date: date
    captured_on: date
    source_frequency: str
    source_url: str
    source_mode: str


def load_ark_holdings_snapshot(
    path: str | Path,
    fund_symbol: str,
    fund_name: str,
    captured_on: date,
    source_url: str = ARK_DOCUMENTS_URL,
    synthetic_fixture: bool = False,
) -> ArkHoldingsImport:
    symbol = _symbol(fund_symbol)
    if not fund_name.strip():
        raise ArkHoldingsDataError("ARK import requires a fund name.")
    if not source_url.startswith("https://"):
        raise ArkHoldingsDataError("ARK import requires an HTTPS source URL.")
    try:
        with Path(path).open(newline="", encoding="utf-8-sig") as source:
            reader = csv.DictReader(source)
            headings = {_column_key(field) for field in (reader.fieldnames or [])}
            missing = sorted(ARK_REQUIRED_COLUMNS - headings)
            if missing:
                raise ArkHoldingsDataError(
                    f"{path}: missing ARK columns: {', '.join(missing)}"
                )
            rows = list(reader)
    except OSError as exc:
        raise ArkHoldingsDataError(f"Unable to read ARK holdings snapshot {path}: {exc}") from exc
    if not rows:
        raise ArkHoldingsDataError(f"{path}: ARK snapshot contains no holdings.")
    frequency = "synthetic_demo" if synthetic_fixture else "daily_official"
    issuer = (
        "TargetAudit Synthetic ARK-format Fixture"
        if synthetic_fixture
        else "ARK Investment Management LLC"
    )
    holdings: list[Holding] = []
    effective_dates: set[date] = set()
    identifiers: set[str] = set()
    for index, row in enumerate(rows, start=2):
        normalized = {_column_key(key): (value or "").strip() for key, value in row.items()}
        row_symbol = _symbol(normalized["fund"])
        if row_symbol != symbol:
            raise ArkHoldingsDataError(
                f"{path}: row {index} describes {row_symbol}, not requested fund {symbol}."
            )
        effective_date = _date_value(normalized["date"], path, index)
        shares = _decimal_value(normalized["shares"], "shares", path, index)
        weight = _decimal_value(normalized["weight(%)"].rstrip("%"), "weight", path, index)
        if shares < 0 or weight < 0 or weight > 100:
            raise ArkHoldingsDataError(f"{path}: row {index} contains invalid holding amounts.")
        company = normalized["company"].strip()
        cusip = normalized["cusip"].strip()
        ticker = normalized["ticker"].strip().upper()
        identifier = ticker or (f"CUSIP:{cusip}" if cusip else "")
        if not company or not identifier:
            raise ArkHoldingsDataError(f"{path}: row {index} lacks holding identity.")
        if identifier.casefold() in identifiers:
            raise ArkHoldingsDataError(f"{path}: duplicate normalized holding {identifier}.")
        identifiers.add(identifier.casefold())
        effective_dates.add(effective_date)
        holdings.append(
            Holding(
                issuer=issuer,
                fund_symbol=symbol,
                fund_name=fund_name.strip(),
                effective_date=effective_date,
                captured_on=captured_on,
                position_ticker=identifier,
                position_name=company,
                shares=shares,
                weight_pct=weight,
                source_frequency=frequency,
                source_url=source_url,
            )
        )
    if len(effective_dates) != 1:
        raise ArkHoldingsDataError(f"{path}: ARK snapshot contains multiple effective dates.")
    return ArkHoldingsImport(
        fund_symbol=symbol,
        fund_name=fund_name.strip(),
        holdings=tuple(holdings),
        effective_date=effective_dates.pop(),
        captured_on=captured_on,
        source_frequency=frequency,
        source_url=source_url,
        source_mode="synthetic_fixture" if synthetic_fixture else "official_download",
    )


def write_normalized_holdings(path: str | Path, imported: ArkHoldingsImport) -> None:
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


def render_import_report(imported: ArkHoldingsImport) -> str:
    return "\n".join(
        [
            "# ARK ETF Holdings Import",
            "",
            f"- Fund: `{imported.fund_symbol}` - {imported.fund_name}",
            f"- Input mode: `{imported.source_mode}`",
            f"- Source frequency layer: `{imported.source_frequency}`",
            f"- Effective date listed in file: `{imported.effective_date.isoformat()}`",
            f"- Captured on: `{imported.captured_on.isoformat()}`",
            f"- Normalized positions: `{len(imported.holdings)}`",
            f"- Source page: <{imported.source_url}>",
            f"- Date interpretation reference: <{ARK_FREQUENCY_REFERENCE_URL}>",
            "",
            "ARK states that ETF holdings are updated daily and that the date in",
            "its holdings CSV corresponds to the next trading day. TargetAudit",
            "preserves that date as the effective date of this snapshot.",
            "",
            "This adapter imports a downloaded CSV into the local evidence layer.",
            "Redistribution of official ARK holdings remains disabled until data-use",
            "permission is resolved; the included project demo is synthetic only.",
            "",
        ]
    )


def write_import_report(path: str | Path, imported: ArkHoldingsImport) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_import_report(imported), encoding="utf-8")


def _column_key(value: str | None) -> str:
    return (value or "").strip().lower().replace(" ", "")


def _symbol(value: str) -> str:
    symbol = value.strip().upper()
    if not _SYMBOL_PATTERN.fullmatch(symbol):
        raise ArkHoldingsDataError(f"Invalid ARK fund symbol: {value!r}.")
    return symbol


def _date_value(value: str, path: str | Path, index: int) -> date:
    for pattern in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, pattern).date()
        except ValueError:
            pass
    raise ArkHoldingsDataError(f"{path}: invalid ARK date on row {index}.")


def _decimal_value(value: str, label: str, path: str | Path, index: int) -> Decimal:
    try:
        result = Decimal(value.replace(",", "").replace("$", "").strip())
    except InvalidOperation as exc:
        raise ArkHoldingsDataError(
            f"{path}: invalid ARK {label} on row {index}."
        ) from exc
    if not result.is_finite():
        raise ArkHoldingsDataError(f"{path}: invalid ARK {label} on row {index}.")
    return result
