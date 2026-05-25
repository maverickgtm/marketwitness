from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .models import Evaluation, PriceBar, TargetObservation

TARGET_COLUMNS = {
    "observation_id",
    "ticker",
    "company_name",
    "firm",
    "published_date",
    "price_target",
    "source_provider",
    "source_url",
}
PRICE_COLUMNS = {
    "ticker",
    "date",
    "adjusted_high",
    "adjusted_low",
    "adjusted_close",
    "source_provider",
}


class DataFormatError(ValueError):
    """Raised when an input CSV cannot be interpreted safely."""


def load_targets(path: str | Path) -> list[TargetObservation]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        _ensure_columns(path, reader.fieldnames, TARGET_COLUMNS)
        rows = []
        for index, row in enumerate(reader, start=2):
            rows.append(
                TargetObservation(
                    observation_id=row["observation_id"].strip() or f"row-{index}",
                    ticker=row["ticker"].strip().upper(),
                    company_name=row["company_name"].strip(),
                    sector=row.get("sector", "").strip(),
                    firm=row["firm"].strip(),
                    analyst=row.get("analyst", "").strip(),
                    published_date=_optional_date(row["published_date"]),
                    price_target=_optional_decimal(row["price_target"]),
                    rating=row.get("rating", "").strip(),
                    horizon_days=_optional_int(row.get("horizon_days", ""), default=365),
                    benchmark_symbol=row.get("benchmark_symbol", "").strip().upper(),
                    source_provider=row["source_provider"].strip(),
                    source_url=row["source_url"].strip(),
                    provider_id=row.get("provider_id", "").strip(),
                )
            )
        return rows


def load_prices(path: str | Path) -> dict[str, list[PriceBar]]:
    bars: defaultdict[str, list[PriceBar]] = defaultdict(list)
    seen_dates: set[tuple[str, date]] = set()
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        _ensure_columns(path, reader.fieldnames, PRICE_COLUMNS)
        for index, row in enumerate(reader, start=2):
            try:
                bar = PriceBar(
                    ticker=row["ticker"].strip().upper(),
                    date=date.fromisoformat(row["date"].strip()),
                    adjusted_high=Decimal(row["adjusted_high"].strip()),
                    adjusted_low=Decimal(row["adjusted_low"].strip()),
                    adjusted_close=Decimal(row["adjusted_close"].strip()),
                    source_provider=row["source_provider"].strip(),
                )
            except (InvalidOperation, ValueError) as exc:
                raise DataFormatError(f"{path}: invalid price data on row {index}") from exc
            values = (bar.adjusted_high, bar.adjusted_low, bar.adjusted_close)
            if (
                not bar.ticker
                or not bar.source_provider
                or not all(value.is_finite() for value in values)
                or min(values) <= 0
            ):
                raise DataFormatError(f"{path}: invalid price data on row {index}")
            if not bar.adjusted_low <= bar.adjusted_close <= bar.adjusted_high:
                raise DataFormatError(f"{path}: close is outside low/high on row {index}")
            key = (bar.ticker, bar.date)
            if key in seen_dates:
                raise DataFormatError(f"{path}: duplicate ticker/date on row {index}")
            seen_dates.add(key)
            bars[bar.ticker].append(bar)
    for ticker in bars:
        bars[ticker].sort(key=lambda bar: bar.date)
    return dict(bars)


def write_evaluations(path: str | Path, evaluations: list[Evaluation]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = [evaluation.to_row() for evaluation in evaluations]
    if not rows:
        raise DataFormatError("No evaluations were generated.")
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _ensure_columns(
    path: str | Path, fieldnames: list[str] | None, required: set[str]
) -> None:
    present = set(fieldnames or [])
    missing = sorted(required - present)
    if missing:
        raise DataFormatError(f"{path}: missing columns: {', '.join(missing)}")


def _optional_date(raw: str) -> date | None:
    try:
        return date.fromisoformat(raw.strip())
    except ValueError:
        return None


def _optional_decimal(raw: str) -> Decimal | None:
    try:
        value = Decimal(raw.strip())
    except InvalidOperation:
        return None
    return value if value.is_finite() else None


def _optional_int(raw: str, default: int) -> int | None:
    if not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return None
