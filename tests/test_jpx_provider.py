import unittest
from datetime import date
from pathlib import Path

from targetaudit.providers.jpx import (
    JpxDataError,
    load_jpx_snapshot,
    parse_jpx_html,
    render_jpx_html,
    render_jpx_report,
)


class JpxProviderTests(unittest.TestCase):
    def test_loads_official_new_listing_snapshot(self) -> None:
        listings = load_jpx_snapshot(
            Path("data/samples/jpx-new-listings.html"), date(2026, 5, 25)
        )

        report = render_jpx_report(listings, date(2026, 5, 25))
        page = render_jpx_html(listings, date(2026, 5, 25))

        self.assertEqual(len(listings), 2)
        self.assertEqual(listings[0].security_code, "584A")
        self.assertEqual(listings[0].market_segment, "Growth")
        self.assertEqual(listings[0].status, "approved_pending_listing")
        self.assertIn("EDINET offering-document review", report)
        self.assertIn("Tokyo", page)

    def test_changes_state_after_listing_date(self) -> None:
        listings = load_jpx_snapshot(
            Path("data/samples/jpx-new-listings.html"), date(2026, 7, 1)
        )
        self.assertEqual(listings[0].status, "listed")

    def test_rejects_rows_without_outline_evidence(self) -> None:
        page = (
            '<table class="widetable"><tr><td>Jun. 23, 2026 (May 21, 2026)</td>'
            "<td>Example</td><td>000A</td></tr><tr><td>Growth</td></tr></table>"
        )
        with self.assertRaisesRegex(JpxDataError, "outline evidence"):
            parse_jpx_html(page, date(2026, 5, 25))

    def test_rejects_future_snapshot_in_report(self) -> None:
        listings = load_jpx_snapshot(
            Path("data/samples/jpx-new-listings.html"), date(2026, 5, 25)
        )
        with self.assertRaisesRegex(JpxDataError, "future observation"):
            render_jpx_report(listings, date(2026, 5, 24))


if __name__ == "__main__":
    unittest.main()
