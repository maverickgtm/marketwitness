from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class TargetObservation:
    observation_id: str
    ticker: str
    company_name: str
    sector: str
    firm: str
    analyst: str
    published_date: date | None
    price_target: Decimal | None
    rating: str
    horizon_days: int | None
    benchmark_symbol: str
    source_provider: str
    source_url: str


@dataclass(frozen=True)
class PriceBar:
    ticker: str
    date: date
    adjusted_high: Decimal
    adjusted_low: Decimal
    adjusted_close: Decimal
    source_provider: str


@dataclass(frozen=True)
class Evaluation:
    observation_id: str
    ticker: str
    firm: str
    sector: str
    published_date: str
    price_target: Decimal | None
    source_url: str
    status: str
    reason: str = ""
    direction: str = ""
    reference_date: str = ""
    reference_price: Decimal | None = None
    entry_date: str = ""
    entry_price: Decimal | None = None
    expiry_date: str = ""
    terminal_date: str = ""
    terminal_price: Decimal | None = None
    hit: bool | None = None
    hit_date: str = ""
    days_to_target: int | None = None
    terminal_absolute_error_pct: Decimal | None = None
    directional_return_pct: Decimal | None = None
    benchmark_symbol: str = ""
    benchmark_directional_return_pct: Decimal | None = None
    excess_return_pct: Decimal | None = None
    historical_universe_id: str = ""
    historical_universe_source_url: str = ""
    superseded_by_observation_id: str = ""
    superseded_on: str = ""
    strategy_exit_reason: str = ""
    strategy_exit_date: str = ""
    strategy_exit_price: Decimal | None = None
    strategy_gross_return_pct: Decimal | None = None
    transaction_cost_bps_per_side: Decimal | None = None
    strategy_net_return_pct: Decimal | None = None
    benchmark_strategy_net_return_pct: Decimal | None = None
    strategy_net_excess_return_pct: Decimal | None = None

    def to_row(self) -> dict[str, str]:
        return {
            "observation_id": self.observation_id,
            "ticker": self.ticker,
            "firm": self.firm,
            "sector": self.sector,
            "published_date": self.published_date,
            "price_target": _decimal_text(self.price_target),
            "source_url": self.source_url,
            "status": self.status,
            "reason": self.reason,
            "direction": self.direction,
            "reference_date": self.reference_date,
            "reference_price": _decimal_text(self.reference_price),
            "entry_date": self.entry_date,
            "entry_price": _decimal_text(self.entry_price),
            "expiry_date": self.expiry_date,
            "terminal_date": self.terminal_date,
            "terminal_price": _decimal_text(self.terminal_price),
            "hit": "" if self.hit is None else str(self.hit).lower(),
            "hit_date": self.hit_date,
            "days_to_target": "" if self.days_to_target is None else str(self.days_to_target),
            "terminal_absolute_error_pct": _decimal_text(self.terminal_absolute_error_pct),
            "directional_return_pct": _decimal_text(self.directional_return_pct),
            "benchmark_symbol": self.benchmark_symbol,
            "benchmark_directional_return_pct": _decimal_text(
                self.benchmark_directional_return_pct
            ),
            "excess_return_pct": _decimal_text(self.excess_return_pct),
            "historical_universe_id": self.historical_universe_id,
            "historical_universe_source_url": self.historical_universe_source_url,
            "superseded_by_observation_id": self.superseded_by_observation_id,
            "superseded_on": self.superseded_on,
            "strategy_exit_reason": self.strategy_exit_reason,
            "strategy_exit_date": self.strategy_exit_date,
            "strategy_exit_price": _decimal_text(self.strategy_exit_price),
            "strategy_gross_return_pct": _decimal_text(self.strategy_gross_return_pct),
            "transaction_cost_bps_per_side": _decimal_text(
                self.transaction_cost_bps_per_side
            ),
            "strategy_net_return_pct": _decimal_text(self.strategy_net_return_pct),
            "benchmark_strategy_net_return_pct": _decimal_text(
                self.benchmark_strategy_net_return_pct
            ),
            "strategy_net_excess_return_pct": _decimal_text(
                self.strategy_net_excess_return_pct
            ),
        }


def _decimal_text(value: Decimal | None) -> str:
    if value is None:
        return ""
    return format(value.quantize(Decimal("0.000001")), "f")
