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

        result = render_markdown_report(evaluations, date(2025, 1, 1), 1)

        self.assertIn("Methodology version: `0.2`", result)
        self.assertIn("| Example Firm | 1 | 100.00% | 20.65% to 100.00%", result)
        self.assertIn("## Direction Breakdown", result)
        self.assertIn("| up | 1 | 100.00% | 20.65% to 100.00%", result)
        self.assertIn("95% Wilson score interval", result)
        self.assertIn("`missing_source_url`", result)

    def test_wilson_interval_exposes_small_sample_uncertainty(self) -> None:
        low, high = wilson_interval(1, 2)

        self.assertEqual(f"{low * Decimal('100'):.2f}%", "9.45%")
        self.assertEqual(f"{high * Decimal('100'):.2f}%", "90.55%")

    def test_wilson_interval_rejects_invalid_counts(self) -> None:
        with self.assertRaisesRegex(ValueError, "hits between zero and total"):
            wilson_interval(2, 1)


if __name__ == "__main__":
    unittest.main()
