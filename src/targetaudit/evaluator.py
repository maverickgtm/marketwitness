from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from .corporate_actions import CorporateAction, has_action_in_observation_window
from .historical_universe import (
    UniverseMembership,
    membership_at_publication,
)
from .models import Evaluation, PriceBar, TargetObservation

MAX_TERMINAL_GAP_DAYS = 7
MAX_ENTRY_GAP_DAYS = 7
MAX_REFERENCE_GAP_DAYS = 7


def evaluate_all(
    observations: list[TargetObservation],
    bars_by_ticker: dict[str, list[PriceBar]],
    as_of: date,
    corporate_actions: list[CorporateAction] | None = None,
    historical_universe: list[UniverseMembership] | None = None,
) -> list[Evaluation]:
    duplicate_ids = _duplicates([observation.observation_id for observation in observations])
    return [
        evaluate(
            observation,
            bars_by_ticker,
            as_of,
            observation.observation_id in duplicate_ids,
            corporate_actions,
            historical_universe,
        )
        for observation in observations
    ]


def evaluate(
    observation: TargetObservation,
    bars_by_ticker: dict[str, list[PriceBar]],
    as_of: date,
    duplicate_id: bool = False,
    corporate_actions: list[CorporateAction] | None = None,
    historical_universe: list[UniverseMembership] | None = None,
) -> Evaluation:
    base = _base_fields(observation)
    invalid_reason = _invalid_reason(observation, duplicate_id)
    if invalid_reason:
        return Evaluation(**base, status="excluded", reason=invalid_reason)

    assert observation.published_date is not None
    assert observation.price_target is not None
    assert observation.horizon_days is not None
    expiry = observation.published_date + timedelta(days=observation.horizon_days)
    if observation.published_date > as_of:
        return Evaluation(**base, status="pending", reason="published_after_as_of")
    if historical_universe is not None:
        membership = membership_at_publication(observation, historical_universe)
        if membership is None:
            return Evaluation(
                **base,
                status="excluded",
                reason="outside_historical_universe",
                expiry_date=expiry.isoformat(),
            )
        base = _base_fields(observation, membership.sector)
        base["historical_universe_id"] = membership.universe_id
        base["historical_universe_source_url"] = membership.source_url
    if expiry > as_of:
        return Evaluation(
            **base, status="pending", reason="horizon_not_mature", expiry_date=expiry.isoformat()
        )
    if corporate_actions and has_action_in_observation_window(
        observation, corporate_actions, as_of
    ):
        return Evaluation(
            **base,
            status="excluded",
            reason="corporate_action_review_required",
            expiry_date=expiry.isoformat(),
        )

    series = bars_by_ticker.get(observation.ticker, [])
    reference = _reference_bar(series, observation.published_date)
    if reference is None or observation.published_date - reference.date > timedelta(
        days=MAX_REFERENCE_GAP_DAYS
    ):
        return Evaluation(
            **base,
            status="excluded",
            reason="missing_reference_price",
            expiry_date=expiry.isoformat(),
        )
    window = _window(series, observation.published_date, expiry)
    if window is None:
        return Evaluation(
            **base,
            status="excluded",
            reason="incomplete_price_window",
            reference_date=reference.date.isoformat(),
            reference_price=reference.adjusted_close,
            expiry_date=expiry.isoformat(),
        )
    entry, period, terminal = window
    if entry.date - observation.published_date > timedelta(days=MAX_ENTRY_GAP_DAYS):
        return Evaluation(
            **base,
            status="excluded",
            reason="delayed_entry_price",
            reference_date=reference.date.isoformat(),
            reference_price=reference.adjusted_close,
            entry_date=entry.date.isoformat(),
            entry_price=entry.adjusted_close,
            expiry_date=expiry.isoformat(),
        )
    if expiry - terminal.date > timedelta(days=MAX_TERMINAL_GAP_DAYS):
        return Evaluation(
            **base,
            status="excluded",
            reason="incomplete_price_window",
            reference_date=reference.date.isoformat(),
            reference_price=reference.adjusted_close,
            entry_date=entry.date.isoformat(),
            entry_price=entry.adjusted_close,
            expiry_date=expiry.isoformat(),
        )

    direction = _direction(observation.price_target, reference.adjusted_close)
    if direction == "flat":
        return Evaluation(
            **base,
            status="excluded",
            reason="flat_target_at_reference",
            direction=direction,
            reference_date=reference.date.isoformat(),
            reference_price=reference.adjusted_close,
            entry_date=entry.date.isoformat(),
            entry_price=entry.adjusted_close,
            expiry_date=expiry.isoformat(),
        )
    if _target_crossed_at_entry(observation.price_target, entry.adjusted_close, direction):
        return Evaluation(
            **base,
            status="excluded",
            reason="target_crossed_before_entry",
            direction=direction,
            reference_date=reference.date.isoformat(),
            reference_price=reference.adjusted_close,
            entry_date=entry.date.isoformat(),
            entry_price=entry.adjusted_close,
            expiry_date=expiry.isoformat(),
        )

    # Entry occurs at the first eligible close, so its intraday range predates
    # the trade and cannot count as a reachable target.
    hit_bar = _first_hit(period[1:], observation.price_target, direction)
    terminal_return = _directional_return(
        entry.adjusted_close, terminal.adjusted_close, direction
    )
    benchmark_return = None
    excess_return = None
    if observation.benchmark_symbol:
        benchmark_window = _window(
            bars_by_ticker.get(observation.benchmark_symbol, []),
            observation.published_date,
            expiry,
        )
        if benchmark_window is None:
            return Evaluation(
                **base,
                status="excluded",
                reason="incomplete_benchmark_window",
                direction=direction,
                reference_date=reference.date.isoformat(),
                reference_price=reference.adjusted_close,
                entry_date=entry.date.isoformat(),
                entry_price=entry.adjusted_close,
                expiry_date=expiry.isoformat(),
            )
        benchmark_entry, _, benchmark_terminal = benchmark_window
        if benchmark_entry.date - observation.published_date > timedelta(
            days=MAX_ENTRY_GAP_DAYS
        ):
            return Evaluation(
                **base,
                status="excluded",
                reason="delayed_benchmark_entry_price",
                direction=direction,
                reference_date=reference.date.isoformat(),
                reference_price=reference.adjusted_close,
                entry_date=entry.date.isoformat(),
                entry_price=entry.adjusted_close,
                expiry_date=expiry.isoformat(),
            )
        if (
            benchmark_entry.date != entry.date
            or benchmark_terminal.date != terminal.date
        ):
            return Evaluation(
                **base,
                status="excluded",
                reason="misaligned_benchmark_window",
                direction=direction,
                reference_date=reference.date.isoformat(),
                reference_price=reference.adjusted_close,
                entry_date=entry.date.isoformat(),
                entry_price=entry.adjusted_close,
                expiry_date=expiry.isoformat(),
            )
        if expiry - benchmark_terminal.date > timedelta(days=MAX_TERMINAL_GAP_DAYS):
            return Evaluation(
                **base,
                status="excluded",
                reason="incomplete_benchmark_window",
                direction=direction,
                entry_date=entry.date.isoformat(),
                entry_price=entry.adjusted_close,
                expiry_date=expiry.isoformat(),
            )
        benchmark_return = _directional_return(
            benchmark_entry.adjusted_close, benchmark_terminal.adjusted_close, direction
        )
        excess_return = terminal_return - benchmark_return

    return Evaluation(
        **base,
        status="evaluated",
        direction=direction,
        reference_date=reference.date.isoformat(),
        reference_price=reference.adjusted_close,
        entry_date=entry.date.isoformat(),
        entry_price=entry.adjusted_close,
        expiry_date=expiry.isoformat(),
        terminal_date=terminal.date.isoformat(),
        terminal_price=terminal.adjusted_close,
        hit=hit_bar is not None,
        hit_date="" if hit_bar is None else hit_bar.date.isoformat(),
        days_to_target=None if hit_bar is None else (hit_bar.date - entry.date).days,
        terminal_absolute_error_pct=abs(
            observation.price_target - terminal.adjusted_close
        )
        / observation.price_target,
        directional_return_pct=terminal_return,
        benchmark_symbol=observation.benchmark_symbol,
        benchmark_directional_return_pct=benchmark_return,
        excess_return_pct=excess_return,
    )


def _base_fields(
    observation: TargetObservation, historical_sector: str | None = None
) -> dict[str, object]:
    return {
        "observation_id": observation.observation_id,
        "ticker": observation.ticker,
        "firm": observation.firm,
        "sector": historical_sector if historical_sector is not None else observation.sector,
        "published_date": ""
        if observation.published_date is None
        else observation.published_date.isoformat(),
        "price_target": observation.price_target,
        "source_url": observation.source_url,
    }


def _invalid_reason(observation: TargetObservation, duplicate_id: bool) -> str:
    if duplicate_id:
        return "duplicate_observation_id"
    required_text = {
        "ticker": observation.ticker,
        "company_name": observation.company_name,
        "firm": observation.firm,
        "source_provider": observation.source_provider,
        "source_url": observation.source_url,
    }
    for field, value in required_text.items():
        if not value:
            return f"missing_{field}"
    if observation.published_date is None:
        return "invalid_published_date"
    if observation.price_target is None or observation.price_target <= 0:
        return "invalid_price_target"
    if observation.horizon_days is None or observation.horizon_days <= 0:
        return "invalid_horizon_days"
    return ""


def _window(
    series: list[PriceBar], published_date: date, expiry: date
) -> tuple[PriceBar, list[PriceBar], PriceBar] | None:
    eligible = [bar for bar in series if published_date < bar.date <= expiry]
    if not eligible:
        return None
    return eligible[0], eligible, eligible[-1]


def _reference_bar(series: list[PriceBar], published_date: date) -> PriceBar | None:
    eligible = [bar for bar in series if bar.date <= published_date]
    return eligible[-1] if eligible else None


def _direction(target: Decimal, entry: Decimal) -> str:
    if target > entry:
        return "up"
    if target < entry:
        return "down"
    return "flat"


def _target_crossed_at_entry(target: Decimal, entry: Decimal, direction: str) -> bool:
    if direction == "up":
        return entry >= target
    return entry <= target


def _first_hit(period: list[PriceBar], target: Decimal, direction: str) -> PriceBar | None:
    for bar in period:
        if direction == "up" and bar.adjusted_high >= target:
            return bar
        if direction == "down" and bar.adjusted_low <= target:
            return bar
    return None


def _directional_return(entry: Decimal, terminal: Decimal, direction: str) -> Decimal:
    raw_return = (terminal - entry) / entry
    return raw_return if direction == "up" else -raw_return


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicate: set[str] = set()
    for value in values:
        if value in seen:
            duplicate.add(value)
        seen.add(value)
    return duplicate
