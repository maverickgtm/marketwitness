import unittest
from datetime import date
from pathlib import Path

from targetaudit.lse_upcoming import (
    LseDataError,
    load_lse_upcoming,
    render_lse_html,
    render_lse_report,
)


class LseUpcomingTests(unittest.TestCase):
    def test_renders_official_upcoming_snapshot(self) -> None:
        issues = load_lse_upcoming(Path("data/samples/lse_upcoming_issues.csv"))

        report = render_lse_report(issues, date(2026, 5, 24))
        page = render_lse_html(issues, date(2026, 5, 24))

        self.assertEqual(len(issues), 3)
        self.assertIn("Lansdowne Oil and Gas plc", report)
        self.assertIn("not yet an automated live connector", report)
        self.assertIn("London", page)
        self.assertIn("Snapshot mode", page)

    def test_rejects_snapshot_after_report_date(self) -> None:
        issues = load_lse_upcoming(Path("data/samples/lse_upcoming_issues.csv"))

        with self.assertRaisesRegex(LseDataError, "future observation"):
            render_lse_report(issues, date(2026, 5, 23))


if __name__ == "__main__":
    unittest.main()
