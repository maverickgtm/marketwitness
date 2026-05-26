from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ..etf_holdings import Holding

SPDR_XLF_URL = (
    "https://www.ssga.com/us/en/intermediary/etfs/"
    "state-street-financial-select-sector-spdr-etf-xlf"
)
_SYMBOL_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9.\-]{0,19}$")


class SpdrHoldingsDataError(ValueError):
    """Raised when a State Street SPDR holdings CSV is not safely importable."""


@dataclass(frozen=True)
class SpdrHoldingsImport:
    fund_symbol: str
    fund_name: str
    holdings: tuple[Holding, ...]
    effective_date: date
    captured_on: date
    source_frequency: str
    source_url: str
    source_mode: str


def load_spdr_holdings_snapshot(
    path: str | Path,
    fund_symbol: str,
    fund_name: str,
    captured_on: date,
    source_url: str = SPDR_XLF_URL,
    synthetic_fixture: bool = False,
) -> SpdrHoldingsImport:
    symbol = _symbol(fund_symbol)
    if not fund_name.strip():
        raise SpdrHoldingsDataError("SPDR import requires a fund name.")
    if not source_url.startswith("https://"):
        raise SpdrHoldingsDataError("SPDR import requires an HTTPS source URL.")
    try:
        with Path(path).open(newline="", encoding="utf-8-sig") as source:
            rows = list(csv.DictReader(source))
    except OSError as exc:
        raise SpdrHoldingsDataError(f"Unable to read SPDR holdings snapshot {path}: {exc}") from exc
    if not rows:
        raise SpdrHoldingsDataError(f"{path}: SPDR snapshot contains no holdings.")
    frequency = "synthetic_demo" if synthetic_fixture else "daily_official"
    issuer = (
        "MarketWitness Synthetic SPDR-format Fixture"
        if synthetic_fixture
        else "State Street Investment Management"
    )
    holdings: list[Holding] = []
    effective_dates: set[date] = set()
    identifiers: set[str] = set()
    for index, row in enumerate(rows, start=2):
        fields = {_column_key(key): (value or "").strip() for key, value in row.items()}
        row_symbol = _symbol(_field(fields, ("fundticker", "fund"), path, index))
        if row_symbol != symbol:
            raise SpdrHoldingsDataError(
                f"{path}: row {index} describes {row_symbol}, not requested fund {symbol}."
            )
        effective_date = _date_value(_field(fields, ("asof", "date"), path, index), path, index)
        position_ticker = _symbol(_field(fields, ("ticker", "symbol"), path, index))
        company = _field(fields, ("name", "company"), path, index)
        shares = _decimal_value(
            _field(fields, ("sharesheld", "shares"), path, index), "shares", path, index
        )
        weight = _decimal_value(
            _field(fields, ("weight", "weightpct"), path, index).rstrip("%"),
            "weight",
            path,
            index,
        )
        if shares < 0 or weight < 0 or weight > 100:
            raise SpdrHoldingsDataError(f"{path}: row {index} contains invalid holding amounts.")
        if position_ticker.casefold() in identifiers:
            raise SpdrHoldingsDataError(
                f"{path}: duplicate normalized holding {position_ticker}."
            )
        identifiers.add(position_ticker.casefold())
        effective_dates.add(effective_date)
        holdings.append(
            Holding(
                issuer=issuer,
                fund_symbol=symbol,
                fund_name=fund_name.strip(),
                effective_date=effective_date,
                captured_on=captured_on,
                position_ticker=position_ticker,
                position_name=company,
                shares=shares,
                weight_pct=weight,
                source_frequency=frequency,
                source_url=source_url,
            )
        )
    if len(effective_dates) != 1:
        raise SpdrHoldingsDataError(f"{path}: SPDR snapshot contains multiple effective dates.")
    return SpdrHoldingsImport(
        fund_symbol=symbol,
        fund_name=fund_name.strip(),
        holdings=tuple(holdings),
        effective_date=effective_dates.pop(),
        captured_on=captured_on,
        source_frequency=frequency,
        source_url=source_url,
        source_mode="synthetic_fixture" if synthetic_fixture else "official_download",
    )


def write_normalized_holdings(path: str | Path, imported: SpdrHoldingsImport) -> None:
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


def render_import_report(imported: SpdrHoldingsImport) -> str:
    return "\n".join(
        [
            "# State Street SPDR Holdings Import",
            "",
            f"- Fund: `{imported.fund_symbol}` - {imported.fund_name}",
            f"- Input mode: `{imported.source_mode}`",
            f"- Source frequency layer: `{imported.source_frequency}`",
            f"- Holdings effective date: `{imported.effective_date.isoformat()}`",
            f"- Captured on: `{imported.captured_on.isoformat()}`",
            f"- Normalized positions: `{len(imported.holdings)}`",
            f"- Official fund page: <{imported.source_url}>",
            "",
            "State Street labels the complete holdings download as daily and the",
            "XLF fund page identifies fund holdings with shares held and weight.",
            "MarketWitness imports a downloaded CSV into local evidence only.",
            "",
            "The official page states that holdings are subject to change and are",
            "not a recommendation to buy or sell any security. Redistribution of",
            "official holdings remains disabled pending written-permission review;",
            "the project fixture is synthetic only.",
            "",
        ]
    )


def write_import_report(path: str | Path, imported: SpdrHoldingsImport) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_import_report(imported), encoding="utf-8")


def _field(
    fields: dict[str, str], aliases: tuple[str, ...], path: str | Path, index: int
) -> str:
    for alias in aliases:
        value = fields.get(alias, "")
        if value:
            return value
    raise SpdrHoldingsDataError(f"{path}: missing SPDR field {aliases[0]} on row {index}.")


def _column_key(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").strip().lower())


def _symbol(value: str) -> str:
    symbol = value.strip().upper()
    if not _SYMBOL_PATTERN.fullmatch(symbol):
        raise SpdrHoldingsDataError(f"Invalid SPDR symbol: {value!r}.")
    return symbol


def _date_value(value: str, path: str | Path, index: int) -> date:
    for pattern in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, pattern).date()
        except ValueError:
            pass
    raise SpdrHoldingsDataError(f"{path}: invalid SPDR date on row {index}.")


def _decimal_value(value: str, label: str, path: str | Path, index: int) -> Decimal:
    try:
        result = Decimal(value.replace(",", "").replace("$", "").strip())
    except InvalidOperation as exc:
        raise SpdrHoldingsDataError(
            f"{path}: invalid SPDR {label} on row {index}."
        ) from exc
    if not result.is_finite():
        raise SpdrHoldingsDataError(f"{path}: invalid SPDR {label} on row {index}.")
    return result
