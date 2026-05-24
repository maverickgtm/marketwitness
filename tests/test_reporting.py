import unittest
from datetime import date
from decimal import Decimal

from targetaudit.models import Evaluation
from targetaudit.reporting import render_markdown_report, wilson_interval


class ReportingTests(unittest.TestCase):
    def test_report_includes_ranked_firm_and_exclusion_reason(self) -> None:
        evaluations = [
            Evaluation(
                observation_id="one",
                ticker="AAA",
                firm="Example Firm",
                sector="Tech",
                published_date="2023-01-02",
                price_target=Decimal("120"),
                source_url="https://example.invalid/one",
                status="evaluated",
                direction="up",
                hit=True,
                days_to_target=20,
                terminal_absolute_error_pct=Decimal("0.05"),
                excess_return_pct=Decimal("0.03"),
            ),
            Evaluation(
                observation_id="two",
                ticker="BBB",
                firm="Example Firm",
                sector="Tech",
                published_date="2023-01-02",
                price_target=Decimal("80"),
                source_url="",
                status="excluded",
                reason="missing_source_url",
            ),
        ]

        result = render_markdown_report(
            evaluations, date(2025, 1, 1), 1, "us-financials-historical"
        )

        self.assertIn("Methodology version: `0.3.2`", result)
        self.assertIn("Historical universe control: `us-financials-historical`", result)
        self.assertIn("| Example Firm | 1 | 100.00% | 20.65% to 100.00%", result)
        self.assertIn("## Firm Ranking By Sector", result)
        self.assertIn("### Tech", result)
        self.assertIn("## Firm Ranking By Direction", result)
        self.assertIn("### up", result)
        self.assertIn("## Direction Breakdown", result)
        self.assertIn("| up | 1 | 100.00% | 20.65% to 100.00%", result)
        self.assertIn("95% Wilson score interval", result)
        self.assertIn("`missing_source_url`", result)

    def test_report_exposes_superseded_target_exclusion(self) -> None:
        evaluation = Evaluation(
            observation_id="original",
            ticker="AAA",
            firm="Example Firm",
            sector="Financials",
            published_date="2023-01-02",
            price_target=Decimal("120"),
            source_url="https://example.invalid/original",
            status="excluded",
            reason="superseded_by_later_target",
            superseded_by_observation_id="revision",
            superseded_on="2023-06-01",
        )

        result = render_markdown_report([evaluation], date(2025, 1, 1), 1)

        self.assertIn("`superseded_by_later_target`", result)
        self.assertIn("### Superseded Target Audit", result)
        self.assertIn("| original | Example Firm | AAA | revision | 2023-06-01 |", result)

    def test_wilson_interval_exposes_small_sample_uncertainty(self) -> None:
        low, high = wilson_interval(1, 2)

        self.assertEqual(f"{low * Decimal('100'):.2f}%", "9.45%")
        self.assertEqual(f"{high * Decimal('100'):.2f}%", "90.55%")

    def test_wilson_interval_rejects_invalid_counts(self) -> None:
        with self.assertRaisesRegex(ValueError, "hits between zero and total"):
            wilson_interval(2, 1)

    def test_segmented_ranking_applies_minimum_sample_inside_each_segment(self) -> None:
        evaluations = [
            _evaluated("one", "up", True),
            _evaluated("two", "down", False),
        ]

        result = render_markdown_report(evaluations, date(2025, 1, 1), 2)

        self.assertIn("| Example Firm | 2 | 50.00%", result)
        self.assertIn("### Financials", result)
        self.assertIn("No firm-direction segment meets the configured minimum sample.", result)

    def test_blank_sector_is_reported_as_unclassified(self):
        evaluation = _evaluated("one", "up", True)
        evaluation = Evaluation(**{**evaluation.__dict__, "sector": ""})

        result = render_markdown_report([evaluation], date(2025, 1, 1), 1)

        self.assertIn("Historical universe control: `not supplied`", result)
        self.assertIn("### Unclassified", result)


def _evaluated(identifier: str, direction: str, hit: bool) -> Evaluation:
    return Evaluation(
        observation_id=identifier,
        ticker=identifier.upper(),
        firm="Example Firm",
        sector="Financials",
        published_date="2023-01-02",
        price_target=Decimal("100"),
        source_url=f"https://example.invalid/{identifier}",
        status="evaluated",
        direction=direction,
        hit=hit,
        terminal_absolute_error_pct=Decimal("0.1"),
        excess_return_pct=Decimal("0.01"),
    )


if __name__ == "__main__":
    unittest.main()
