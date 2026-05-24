import unittest
from datetime import date
from decimal import Decimal

from targetaudit.evaluator import evaluate_all
from targetaudit.models import PriceBar, TargetObservation


class EvaluatorTests(unittest.TestCase):
    def test_upward_target_hit_and_benchmark_excess_return(self) -> None:
        observation = _target("up", "AAA", Decimal("120"), "SPY")
        prices = {
            "AAA": [
                _bar("AAA", "2023-01-03", "101", "99", "100"),
                _bar("AAA", "2023-06-01", "121", "110", "118"),
                _bar("AAA", "2024-01-02", "116", "113", "115"),
            ],
            "SPY": [
                _bar("SPY", "2023-01-03", "101", "99", "100"),
                _bar("SPY", "2024-01-02", "111", "109", "110"),
            ],
        }

        result = evaluate_all([observation], prices, date(2025, 1, 1))[0]

        self.assertEqual(result.status, "evaluated")
        self.assertEqual(result.direction, "up")
        self.assertTrue(result.hit)
        self.assertEqual(result.days_to_target, 149)
        self.assertEqual(result.directional_return_pct, Decimal("0.15"))
        self.assertEqual(result.excess_return_pct, Decimal("0.05"))

    def test_downward_target_can_miss_but_return_positive(self) -> None:
        observation = _target("down", "BBB", Decimal("80"), "")
        prices = {
            "BBB": [
                _bar("BBB", "2023-01-03", "101", "99", "100"),
                _bar("BBB", "2024-01-02", "92", "88", "90"),
            ]
        }

        result = evaluate_all([observation], prices, date(2025, 1, 1))[0]

        self.assertEqual(result.status, "evaluated")
        self.assertEqual(result.direction, "down")
        self.assertFalse(result.hit)
        self.assertEqual(result.directional_return_pct, Decimal("0.1"))

    def test_entry_day_intraday_high_is_not_counted_as_a_hit(self) -> None:
        observation = _target("no-look-ahead", "AAA", Decimal("120"), "")
        prices = {
            "AAA": [
                _bar("AAA", "2023-01-03", "121", "99", "100"),
                _bar("AAA", "2024-01-02", "119", "110", "115"),
            ]
        }

        result = evaluate_all([observation], prices, date(2025, 1, 1))[0]

        self.assertEqual(result.status, "evaluated")
        self.assertFalse(result.hit)

    def test_missing_source_is_excluded(self) -> None:
        observation = _target("missing-source", "AAA", Decimal("120"), "")
        observation = TargetObservation(**{**observation.__dict__, "source_url": ""})

        result = evaluate_all([observation], {}, date(2025, 1, 1))[0]

        self.assertEqual(result.status, "excluded")
        self.assertEqual(result.reason, "missing_source_url")

    def test_unexpired_observation_is_pending(self) -> None:
        observation = _target("pending", "AAA", Decimal("120"), "")

        result = evaluate_all([observation], {}, date(2023, 6, 1))[0]

        self.assertEqual(result.status, "pending")
        self.assertEqual(result.reason, "horizon_not_mature")


def _target(identifier: str, ticker: str, target: Decimal, benchmark: str) -> TargetObservation:
    return TargetObservation(
        observation_id=identifier,
        ticker=ticker,
        company_name=f"{ticker} Company",
        sector="Technology",
        firm="Example Firm",
        analyst="",
        published_date=date(2023, 1, 2),
        price_target=target,
        rating="Buy",
        horizon_days=365,
        benchmark_symbol=benchmark,
        source_provider="synthetic",
        source_url=f"https://example.invalid/{identifier}",
    )


def _bar(ticker: str, day: str, high: str, low: str, close: str) -> PriceBar:
    return PriceBar(
        ticker=ticker,
        date=date.fromisoformat(day),
        adjusted_high=Decimal(high),
        adjusted_low=Decimal(low),
        adjusted_close=Decimal(close),
        source_provider="synthetic",
    )


if __name__ == "__main__":
    unittest.main()
