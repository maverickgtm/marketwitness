import unittest
import tempfile
from datetime import date
from pathlib import Path

from marketwitness.lse_upcoming import (
    LseDataError,
    load_lse_page_payload,
    load_lse_upcoming,
    render_lse_html,
    render_lse_report,
    write_lse_csv,
)


class LseUpcomingTests(unittest.TestCase):
    def test_renders_official_upcoming_snapshot(self) -> None:
        issues = load_lse_upcoming(Path("data/samples/lse_upcoming_issues.csv"))

        report = render_lse_report(issues, date(2026, 5, 24))
        page = render_lse_html(issues, date(2026, 5, 24))

        self.assertEqual(len(issues), 3)
        self.assertIn("Lansdowne Oil and Gas plc", report)
        self.assertIn("LSE Upcoming Issues Snapshot", report)
        self.assertIn("London", page)
        self.assertIn("Snapshot mode", page)
        self.assertIn('href="/dashboard/global-listings">Global Listings Watch</a>', page)

    def test_rejects_snapshot_after_report_date(self) -> None:
        issues = load_lse_upcoming(Path("data/samples/lse_upcoming_issues.csv"))

        with self.assertRaisesRegex(LseDataError, "future observation"):
            render_lse_report(issues, date(2026, 5, 23))

    def test_parses_official_json_feed_and_renders_live_mode(self) -> None:
        issues = load_lse_page_payload(
            Path("data/samples/lse-new-issues-page.json"), date(2026, 5, 24)
        )

        report = render_lse_report(issues, date(2026, 5, 24), "live")
        page = render_lse_html(issues, date(2026, 5, 24), "live")

        self.assertEqual(len(issues), 3)
        self.assertEqual(issues[1].primary_offer, "GBP 2m")
        self.assertIn("LSE Upcoming Issues Monitor", report)
        self.assertIn("Official JSON source", report)
        self.assertIn("Live official feed", page)

    def test_rejects_page_payload_without_upcoming_component(self) -> None:
        with self.assertRaisesRegex(LseDataError, "missing upcoming-issues"):
            from marketwitness.lse_upcoming import parse_lse_page_payload

            parse_lse_page_payload({"components": []}, date(2026, 5, 24))

    def test_writes_normalized_csv_for_history_comparison(self) -> None:
        issues = load_lse_page_payload(
            Path("data/samples/lse-new-issues-page.json"), date(2026, 5, 24)
        )
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "lse.csv"
            write_lse_csv(destination, issues)
            reloaded = load_lse_upcoming(destination)

        self.assertEqual(reloaded[0].company_name, "Coastal Africa Group Limited")


if __name__ == "__main__":
    unittest.main()
