import unittest
from datetime import date
from decimal import Decimal

from targetaudit.models import Evaluation
from targetaudit.reporting import render_markdown_report


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

        self.assertIn("| Example Firm | 1 | 100.00%", result)
        self.assertIn("## Direction Breakdown", result)
        self.assertIn("| up | 1 | 100.00%", result)
        self.assertIn("`missing_source_url`", result)


if __name__ == "__main__":
    unittest.main()
