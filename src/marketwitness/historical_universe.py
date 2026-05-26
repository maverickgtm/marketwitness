from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .models import TargetObservation

UNIVERSE_COLUMNS = {
    "universe_id",
    "ticker",
    "company_name",
    "sector",
    "member_from",
    "member_to",
    "source_provider",
    "source_url",
    "verified_on",
}


class HistoricalUniverseDataError(ValueError):
    """Raised when universe membership cannot support point-in-time scoring."""


@dataclass(frozen=True)
class UniverseMembership:
    universe_id: str
    ticker: str
    company_name: str
    sector: str
    member_from: date
    member_to: date | None
    source_provider: str
    source_url: str
    verified_on: date


def load_historical_universe(path: str | Path) -> list[UniverseMembership]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        missing = sorted(UNIVERSE_COLUMNS - set(reader.fieldnames or []))
        if missing:
            raise HistoricalUniverseDataError(
                f"{path}: missing columns: {', '.join(missing)}"
            )
        memberships: list[UniverseMembership] = []
        universe_ids: set[str] = set()
        for index, row in enumerate(reader, start=2):
            required = [
                row["universe_id"].strip(),
                row["ticker"].strip(),
                row["company_name"].strip(),
                row["sector"].strip(),
                row["source_provider"].strip(),
                row["source_url"].strip(),
            ]
            if not all(required):
                raise HistoricalUniverseDataError(
                    f"{path}: missing membership evidence on row {index}"
                )
            if not row["source_url"].strip().startswith("https://"):
                raise HistoricalUniverseDataError(
                    f"{path}: non-HTTPS source on row {index}"
                )
            try:
                member_from = date.fromisoformat(row["member_from"].strip())
                member_to = (
                    date.fromisoformat(row["member_to"].strip())
                    if row["member_to"].strip()
                    else None
                )
                verified_on = date.fromisoformat(row["verified_on"].strip())
            except ValueError as exc:
                raise HistoricalUniverseDataError(
                    f"{path}: invalid date on row {index}"
                ) from exc
            if member_to is not None and member_to < member_from:
                raise HistoricalUniverseDataError(
                    f"{path}: membership ends before it begins on row {index}"
                )
            universe_ids.add(row["universe_id"].strip())
            memberships.append(
                UniverseMembership(
                    universe_id=row["universe_id"].strip(),
                    ticker=row["ticker"].strip().upper(),
                    company_name=row["company_name"].strip(),
                    sector=row["sector"].strip(),
                    member_from=member_from,
                    member_to=member_to,
                    source_provider=row["source_provider"].strip(),
                    source_url=row["source_url"].strip(),
                    verified_on=verified_on,
                )
            )
    if not memberships:
        raise HistoricalUniverseDataError(f"{path}: universe membership is empty")
    if len(universe_ids) != 1:
        raise HistoricalUniverseDataError(
            f"{path}: evaluation requires exactly one universe_id"
        )
    _reject_overlapping_memberships(path, memberships)
    return memberships


def membership_at_publication(
    observation: TargetObservation, memberships: list[UniverseMembership]
) -> UniverseMembership | None:
    if observation.published_date is None:
        return None
    for membership in memberships:
        if (
            membership.ticker == observation.ticker
            and membership.member_from <= observation.published_date
            and (
                membership.member_to is None
                or observation.published_date <= membership.member_to
            )
        ):
            return membership
    return None


def _reject_overlapping_memberships(
    path: str | Path, memberships: list[UniverseMembership]
) -> None:
    by_ticker: dict[str, list[UniverseMembership]] = {}
    for membership in memberships:
        by_ticker.setdefault(membership.ticker, []).append(membership)
    for ticker, rows in by_ticker.items():
        rows.sort(key=lambda item: item.member_from)
        for previous, current in zip(rows, rows[1:]):
            if previous.member_to is None or current.member_from <= previous.member_to:
                raise HistoricalUniverseDataError(
                    f"{path}: overlapping membership windows for {ticker}"
                )
