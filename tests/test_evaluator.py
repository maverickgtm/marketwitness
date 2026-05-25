from __future__ import annotations

import unittest
from datetime import date
from decimal import Decimal

from targetaudit.corporate_actions import CorporateAction
from targetaudit.evaluator import evaluate_all
from targetaudit.historical_universe import UniverseMembership
from targetaudit.models import PriceBar, TargetObservation


class EvaluatorTests(unittest.TestCase):
    def test_upward_target_hit_and_benchmark_excess_return(self) -> None:
        observation = _target("up", "AAA", Decimal("120"), "SPY")
        prices = {
            "AAA": [
                _bar("AAA", "2022-12-30", "101", "99", "100"),
                _bar("AAA", "2023-01-03", "101", "99", "100"),
                _bar("AAA", "2023-06-01", "121", "110", "118"),
                _bar("AAA", "2024-01-02", "116", "113", "115"),
            ],
            "SPY": [
                _bar("SPY", "2023-01-03", "101", "99", "100"),
                _bar("SPY", "2023-06-01", "106", "104", "105"),
                _bar("SPY", "2024-01-02", "111", "109", "110"),
            ],
        }

        result = evaluate_all([observation], prices, date(2025, 1, 1))[0]

        self.assertEqual(result.status, "evaluated")
        self.assertEqual(result.provider_id, "synthetic-demo")
        self.assertEqual(result.direction, "up")
        self.assertTrue(result.hit)
        self.assertEqual(result.days_to_target, 149)
        self.assertEqual(result.directional_return_pct, Decimal("0.15"))
        self.assertEqual(result.excess_return_pct, Decimal("0.05"))
        self.assertEqual(result.strategy_exit_reason, "target_hit_limit")
        self.assertEqual(result.strategy_exit_date, "2023-06-01")
        self.assertEqual(result.strategy_exit_price, Decimal("120"))
        self.assertEqual(result.strategy_gross_return_pct, Decimal("0.2"))
        self.assertEqual(result.strategy_net_return_pct, Decimal("0.198"))
        self.assertEqual(result.benchmark_strategy_net_return_pct, Decimal("0.048"))
        self.assertEqual(result.strategy_net_excess_return_pct, Decimal("0.150"))

    def test_downward_target_can_miss_but_return_positive(self) -> None:
        observation = _target("down", "BBB", Decimal("80"), "")
        prices = {
            "BBB": [
                _bar("BBB", "2022-12-30", "101", "99", "100"),
                _bar("BBB", "2023-01-03", "101", "99", "100"),
                _bar("BBB", "2024-01-02", "92", "88", "90"),
            ]
        }

        result = evaluate_all([observation], prices, date(2025, 1, 1))[0]

        self.assertEqual(result.status, "evaluated")
        self.assertEqual(result.direction, "down")
        self.assertFalse(result.hit)
        self.assertEqual(result.directional_return_pct, Decimal("0.1"))
        self.assertEqual(result.strategy_exit_reason, "horizon_close")
        self.assertEqual(result.strategy_exit_date, "2024-01-02")
        self.assertEqual(result.strategy_net_return_pct, Decimal("0.098"))

    def test_net_strategy_excess_requires_benchmark_bar_on_early_exit_date(self) -> None:
        observation = _target("unmatched-exit", "AAA", Decimal("120"), "SPY")
        prices = {
            "AAA": [
                _bar("AAA", "2022-12-30", "101", "99", "100"),
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
        self.assertEqual(result.strategy_net_return_pct, Decimal("0.198"))
        self.assertIsNone(result.strategy_net_excess_return_pct)

    def test_entry_day_intraday_high_is_not_counted_as_a_hit(self) -> None:
        observation = _target("no-look-ahead", "AAA", Decimal("120"), "")
        prices = {
            "AAA": [
                _bar("AAA", "2022-12-30", "101", "99", "100"),
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

    def test_price_entry_too_far_after_publication_is_excluded(self) -> None:
        observation = _target("late-entry", "AAA", Decimal("120"), "")
        prices = {
            "AAA": [
                _bar("AAA", "2022-12-30", "101", "99", "100"),
                _bar("AAA", "2023-02-03", "101", "99", "100"),
                _bar("AAA", "2024-01-02", "120", "110", "115"),
            ]
        }

        result = evaluate_all([observation], prices, date(2025, 1, 1))[0]

        self.assertEqual(result.status, "excluded")
        self.assertEqual(result.reason, "delayed_entry_price")

    def test_direction_is_based_on_published_date_reference_not_later_entry(self) -> None:
        observation = _target("crossed-entry", "AAA", Decimal("120"), "")
        prices = {
            "AAA": [
                _bar("AAA", "2023-01-02", "101", "99", "100"),
                _bar("AAA", "2023-01-03", "126", "123", "125"),
                _bar("AAA", "2024-01-02", "130", "125", "128"),
            ]
        }

        result = evaluate_all([observation], prices, date(2025, 1, 1))[0]

        self.assertEqual(result.status, "excluded")
        self.assertEqual(result.direction, "up")
        self.assertEqual(result.reason, "target_crossed_before_entry")

    def test_missing_reference_price_is_excluded(self) -> None:
        observation = _target("no-reference", "AAA", Decimal("120"), "")
        prices = {
            "AAA": [
                _bar("AAA", "2023-01-03", "101", "99", "100"),
                _bar("AAA", "2024-01-02", "119", "110", "115"),
            ]
        }

        result = evaluate_all([observation], prices, date(2025, 1, 1))[0]

        self.assertEqual(result.status, "excluded")
        self.assertEqual(result.reason, "missing_reference_price")

    def test_misaligned_benchmark_window_is_excluded(self) -> None:
        observation = _target("misaligned-benchmark", "AAA", Decimal("120"), "XLF")
        prices = {
            "AAA": [
                _bar("AAA", "2022-12-30", "101", "99", "100"),
                _bar("AAA", "2023-01-03", "101", "99", "100"),
                _bar("AAA", "2024-01-02", "116", "113", "115"),
            ],
            "XLF": [
                _bar("XLF", "2023-01-04", "41", "39", "40"),
                _bar("XLF", "2024-01-02", "46", "44", "45"),
            ],
        }

        result = evaluate_all([observation], prices, date(2025, 1, 1))[0]

        self.assertEqual(result.status, "excluded")
        self.assertEqual(result.reason, "misaligned_benchmark_window")

    def test_documented_split_routes_target_out_of_scoring(self) -> None:
        observation = _target("split-review", "AAA", Decimal("120"), "")
        action = CorporateAction(
            action_id="split-1",
            company_name="AAA Company",
            prior_ticker="AAA",
            current_ticker="AAA",
            action_type="stock_split",
            effective_date=date(2023, 6, 1),
            split_ratio_new=Decimal("2"),
            split_ratio_old=Decimal("1"),
            evidence_level="exchange_notice",
            source_title="Official split notice",
            source_url="https://example.invalid/split-1",
            verified_on=date(2023, 6, 1),
            review_note="Review adjusted target basis.",
        )
        prices = {
            "AAA": [
                _bar("AAA", "2022-12-30", "101", "99", "100"),
                _bar("AAA", "2023-01-03", "101", "99", "100"),
                _bar("AAA", "2024-01-02", "116", "113", "115"),
            ]
        }

        result = evaluate_all([observation], prices, date(2025, 1, 1), [action])[0]

        self.assertEqual(result.status, "excluded")
        self.assertEqual(result.reason, "corporate_action_review_required")

    def test_target_outside_historical_universe_is_excluded(self) -> None:
        observation = _target("outside-universe", "AAA", Decimal("120"), "")

        result = evaluate_all(
            [observation],
            {},
            date(2025, 1, 1),
            historical_universe=[_membership("BBB", "Financials")],
        )[0]

        self.assertEqual(result.status, "excluded")
        self.assertEqual(result.reason, "outside_historical_universe")

    def test_target_published_after_membership_end_is_excluded(self) -> None:
        observation = _target("former-member", "AAA", Decimal("120"), "")

        result = evaluate_all(
            [observation],
            {},
            date(2025, 1, 1),
            historical_universe=[
                _membership("AAA", "Financials", member_to=date(2022, 12, 31))
            ],
        )[0]

        self.assertEqual(result.status, "excluded")
        self.assertEqual(result.reason, "outside_historical_universe")

    def test_historical_universe_sector_drives_segmented_reporting(self) -> None:
        observation = _target("historical-sector", "AAA", Decimal("80"), "")
        prices = {
            "AAA": [
                _bar("AAA", "2022-12-30", "101", "99", "100"),
                _bar("AAA", "2023-01-03", "101", "99", "100"),
                _bar("AAA", "2024-01-02", "92", "88", "90"),
            ]
        }

        result = evaluate_all(
            [observation],
            prices,
            date(2025, 1, 1),
            historical_universe=[_membership("AAA", "Financials")],
        )[0]

        self.assertEqual(result.status, "evaluated")
        self.assertEqual(result.sector, "Financials")
        self.assertEqual(result.historical_universe_id, "historical-demo")
        self.assertIn("/universe/aaa", result.historical_universe_source_url)

    def test_later_target_by_same_firm_and_ticker_supersedes_open_target(self) -> None:
        original = _target("original", "AAA", Decimal("120"), "")
        revision = TargetObservation(
            **{
                **_target("revision", "AAA", Decimal("115"), "").__dict__,
                "published_date": date(2023, 6, 1),
            }
        )

        results = evaluate_all([original, revision], {}, date(2025, 1, 1))

        self.assertEqual(results[0].status, "excluded")
        self.assertEqual(results[0].reason, "superseded_by_later_target")
        self.assertEqual(results[0].superseded_by_observation_id, "revision")
        self.assertEqual(results[0].superseded_on, "2023-06-01")

    def test_invalid_later_target_does_not_supersede_valid_target(self) -> None:
        original = _target("original", "AAA", Decimal("120"), "")
        revision = TargetObservation(
            **{
                **_target("revision", "AAA", Decimal("115"), "").__dict__,
                "published_date": date(2023, 6, 1),
                "source_url": "",
            }
        )
        prices = {
            "AAA": [
                _bar("AAA", "2022-12-30", "101", "99", "100"),
                _bar("AAA", "2023-01-03", "101", "99", "100"),
                _bar("AAA", "2023-06-01", "121", "110", "118"),
                _bar("AAA", "2024-01-02", "116", "113", "115"),
            ]
        }

        results = evaluate_all([original, revision], prices, date(2025, 1, 1))

        self.assertEqual(results[0].status, "evaluated")
        self.assertEqual(results[1].reason, "missing_source_url")

    def test_target_from_different_firm_does_not_supersede_signal(self) -> None:
        original = _target("original", "AAA", Decimal("120"), "")
        other_firm = TargetObservation(
            **{
                **_target("other", "AAA", Decimal("115"), "").__dict__,
                "firm": "Different Firm",
                "published_date": date(2023, 6, 1),
            }
        )
        prices = {
            "AAA": [
                _bar("AAA", "2022-12-30", "101", "99", "100"),
                _bar("AAA", "2023-01-03", "101", "99", "100"),
                _bar("AAA", "2023-06-01", "121", "110", "118"),
                _bar("AAA", "2024-01-02", "116", "113", "115"),
            ]
        }

        results = evaluate_all([original, other_firm], prices, date(2025, 1, 1))

        self.assertEqual(results[0].status, "evaluated")

    def test_configurable_transaction_cost_changes_net_strategy_return(self) -> None:
        observation = _target("cost", "AAA", Decimal("120"), "")
        prices = {
            "AAA": [
                _bar("AAA", "2022-12-30", "101", "99", "100"),
                _bar("AAA", "2023-01-03", "101", "99", "100"),
                _bar("AAA", "2023-06-01", "121", "110", "118"),
                _bar("AAA", "2024-01-02", "116", "113", "115"),
            ]
        }

        result = evaluate_all(
            [observation],
            prices,
            date(2025, 1, 1),
            transaction_cost_bps_per_side=Decimal("25"),
        )[0]

        self.assertEqual(result.transaction_cost_bps_per_side, Decimal("25"))
        self.assertEqual(result.strategy_net_return_pct, Decimal("0.195"))

    def test_negative_transaction_cost_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-negative"):
            evaluate_all(
                [],
                {},
                date(2025, 1, 1),
                transaction_cost_bps_per_side=Decimal("-1"),
            )


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
        provider_id="synthetic-demo",
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


def _membership(
    ticker: str, sector: str, member_to: date | None = None
) -> UniverseMembership:
    return UniverseMembership(
        universe_id="historical-demo",
        ticker=ticker,
        company_name=f"{ticker} Company",
        sector=sector,
        member_from=date(2020, 1, 1),
        member_to=member_to,
        source_provider="synthetic",
        source_url=f"https://example.invalid/universe/{ticker.lower()}",
        verified_on=date(2023, 1, 1),
    )


if __name__ == "__main__":
    unittest.main()
