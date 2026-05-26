from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ..etf_holdings import Holding

ISHARES_IYF_URL = (
    "https://www.ishares.com/us/products/overview-v3-ishares-fund-data"
    "?portfolioId=239508&seoSlug=ishares-us-financials-etf"
)
ISHARES_TERMS_URL = "https://www.blackrock.com/corporate/compliance/terms-and-conditions"
_SYMBOL_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9.\-]{0,29}$")


class IsharesHoldingsDataError(ValueError):
    """Raised when an iShares holdings download is not safely importable."""


@dataclass(frozen=True)
class IsharesHoldingsImport:
    fund_symbol: str
    fund_name: str
    holdings: tuple[Holding, ...]
    omitted_non_equity_positions: int
    effective_date: date
    captured_on: date
    source_frequency: str
    source_url: str
    source_mode: str


def load_ishares_holdings_snapshot(
    path: str | Path,
    fund_symbol: str,
    fund_name: str,
    captured_on: date,
    source_url: str = ISHARES_IYF_URL,
    synthetic_fixture: bool = False,
) -> IsharesHoldingsImport:
    symbol = _symbol(fund_symbol)
    if not fund_name.strip():
        raise IsharesHoldingsDataError("iShares import requires a fund name.")
    if not source_url.startswith("https://"):
        raise IsharesHoldingsDataError("iShares import requires an HTTPS source URL.")
    try:
        with Path(path).open(newline="", encoding="utf-8-sig") as source:
            rows = list(csv.reader(source))
    except OSError as exc:
        raise IsharesHoldingsDataError(
            f"Unable to read iShares holdings snapshot {path}: {exc}"
        ) from exc
    effective_date = _effective_date(rows, path)
    if effective_date > captured_on:
        raise IsharesHoldingsDataError(
            f"{path}: iShares holdings date is after the capture date."
        )
    fields, data_rows = _holdings_table(rows, path)
    frequency = "synthetic_demo" if synthetic_fixture else "official_snapshot"
    issuer = (
        "MarketWitness Synthetic iShares-format Fixture"
        if synthetic_fixture
        else "BlackRock Fund Advisors"
    )
    holdings = []
    omitted = 0
    identifiers = set()
    for index, row in enumerate(data_rows, start=1):
        record = {field: (value or "").strip() for field, value in zip(fields, row)}
        asset_class = record.get("assetclass", "equity").strip().casefold()
        if asset_class not in {"equity", "stock"}:
            omitted += 1
            continue
        ticker = _symbol(_field(record, ("ticker",), path, index))
        if ticker.casefold() in identifiers:
            raise IsharesHoldingsDataError(
                f"{path}: duplicate normalized holding {ticker}."
            )
        identifiers.add(ticker.casefold())
        company = _field(record, ("name",), path, index)
        shares = _decimal_value(
            _field(record, ("shares", "quantity"), path, index), "shares", path, index
        )
        weight = _decimal_value(
            _field(record, ("weight",), path, index).rstrip("%"), "weight", path, index
        )
        if shares < 0 or weight < 0 or weight > 100:
            raise IsharesHoldingsDataError(
                f"{path}: row {index} contains invalid holding amounts."
            )
        holdings.append(
            Holding(
                issuer=issuer,
                fund_symbol=symbol,
                fund_name=fund_name.strip(),
                effective_date=effective_date,
                captured_on=captured_on,
                position_ticker=ticker,
                position_name=company,
                shares=shares,
                weight_pct=weight,
                source_frequency=frequency,
                source_url=source_url,
            )
        )
    if not holdings:
        raise IsharesHoldingsDataError(f"{path}: iShares snapshot contains no equity holdings.")
    return IsharesHoldingsImport(
        fund_symbol=symbol,
        fund_name=fund_name.strip(),
        holdings=tuple(holdings),
        omitted_non_equity_positions=omitted,
        effective_date=effective_date,
        captured_on=captured_on,
        source_frequency=frequency,
        source_url=source_url,
        source_mode="synthetic_fixture" if synthetic_fixture else "official_manual_download",
    )


def write_normalized_holdings(path: str | Path, imported: IsharesHoldingsImport) -> None:
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


def render_import_report(imported: IsharesHoldingsImport) -> str:
    return "\n".join(
        [
            "# iShares ETF Holdings Import",
            "",
            f"- Fund: `{imported.fund_symbol}` - {imported.fund_name}",
            f"- Input mode: `{imported.source_mode}`",
            f"- Source frequency layer: `{imported.source_frequency}`",
            f"- Holdings effective date: `{imported.effective_date.isoformat()}`",
            f"- Captured on: `{imported.captured_on.isoformat()}`",
            f"- Equity positions normalized: `{len(imported.holdings)}`",
            f"- Non-equity positions omitted: `{imported.omitted_non_equity_positions}`",
            f"- Official fund page: <{imported.source_url}>",
            f"- Terms reference: <{ISHARES_TERMS_URL}>",
            "",
            "The official IYF page identifies the fund as U.S. financial-sector",
            "equity exposure and publishes a holdings table with shares and weight.",
            "MarketWitness preserves it as a dated official snapshot, not as a daily",
            "feed, and imports a manually downloaded file into local evidence only.",
            "",
            "BlackRock terms prohibit automated agents from monitoring or copying",
            "site materials without permission. No automated iShares download is",
            "implemented, and official holdings are not redistributed by this project.",
            "",
        ]
    )


def write_import_report(path: str | Path, imported: IsharesHoldingsImport) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_import_report(imported), encoding="utf-8")


def _effective_date(rows: list[list[str]], path: str | Path) -> date:
    for row in rows:
        if row and "holdings as of" in row[0].strip().casefold():
            for value in row[1:]:
                if value.strip():
                    return _date_value(value.strip(), path)
    raise IsharesHoldingsDataError(f"{path}: iShares snapshot lacks a holdings-as-of date.")


def _holdings_table(
    rows: list[list[str]], path: str | Path
) -> tuple[list[str], list[list[str]]]:
    for index, row in enumerate(rows):
        fields = [_column_key(field) for field in row]
        if {"ticker", "name", "weight"}.issubset(set(fields)) and (
            "shares" in fields or "quantity" in fields
        ):
            data_rows = [values for values in rows[index + 1 :] if any(values)]
            if data_rows:
                return fields, data_rows
    raise IsharesHoldingsDataError(f"{path}: iShares holdings table was not found.")


def _field(record: dict[str, str], aliases: tuple[str, ...], path: str | Path, index: int) -> str:
    for alias in aliases:
        value = record.get(alias, "")
        if value:
            return value
    raise IsharesHoldingsDataError(
        f"{path}: missing iShares field {aliases[0]} on holding row {index}."
    )


def _column_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.strip().lower())


def _symbol(value: str) -> str:
    symbol = value.strip().upper()
    if not _SYMBOL_PATTERN.fullmatch(symbol):
        raise IsharesHoldingsDataError(f"Invalid iShares symbol: {value!r}.")
    return symbol


def _date_value(value: str, path: str | Path) -> date:
    for pattern in ("%b %d, %Y", "%B %d, %Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, pattern).date()
        except ValueError:
            pass
    raise IsharesHoldingsDataError(f"{path}: invalid iShares holdings date.")


def _decimal_value(value: str, label: str, path: str | Path, index: int) -> Decimal:
    try:
        result = Decimal(value.replace(",", "").replace("$", "").strip())
    except InvalidOperation as exc:
        raise IsharesHoldingsDataError(
            f"{path}: invalid iShares {label} on holding row {index}."
        ) from exc
    if not result.is_finite():
        raise IsharesHoldingsDataError(
            f"{path}: invalid iShares {label} on holding row {index}."
        )
    return result
