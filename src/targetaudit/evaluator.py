from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from .models import Evaluation, PriceBar, TargetObservation

MAX_TERMINAL_GAP_DAYS = 7


def evaluate_all(
    observations: list[TargetObservation],
    bars_by_ticker: dict[str, list[PriceBar]],
    as_of: date,
) -> list[Evaluation]:
    duplicate_ids = _duplicates([observation.observation_id for observation in observations])
    return [
        evaluate(observation, bars_by_ticker, as_of, observation.observation_id in duplicate_ids)
        for observation in observations
    ]


def evaluate(
    observation: TargetObservation,
    bars_by_ticker: dict[str, list[PriceBar]],
    as_of: date,
    duplicate_id: bool = False,
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
    if expiry > as_of:
        return Evaluation(
            **base, status="pending", reason="horizon_not_mature", expiry_date=expiry.isoformat()
        )

    series = bars_by_ticker.get(observation.ticker, [])
    window = _window(series, observation.published_date, expiry)
    if window is None:
        return Evaluation(
            **base,
            status="excluded",
            reason="incomplete_price_window",
            expiry_date=expiry.isoformat(),
        )
    entry, period, terminal = window
    if expiry - terminal.date > timedelta(days=MAX_TERMINAL_GAP_DAYS):
        return Evaluation(
            **base,
            status="excluded",
            reason="incomplete_price_window",
            entry_date=entry.date.isoformat(),
            entry_price=entry.adjusted_close,
            expiry_date=expiry.isoformat(),
        )

    direction = _direction(observation.price_target, entry.adjusted_close)
    if direction == "flat":
        return Evaluation(
            **base,
            status="excluded",
            reason="flat_target_at_entry",
            direction=direction,
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
                entry_date=entry.date.isoformat(),
                entry_price=entry.adjusted_close,
                expiry_date=expiry.isoformat(),
            )
        benchmark_entry, _, benchmark_terminal = benchmark_window
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


def _base_fields(observation: TargetObservation) -> dict[str, object]:
    return {
        "observation_id": observation.observation_id,
        "ticker": observation.ticker,
        "firm": observation.firm,
        "sector": observation.sector,
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


def _direction(target: Decimal, entry: Decimal) -> str:
    if target > entry:
        return "up"
    if target < entry:
        return "down"
    return "flat"


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
