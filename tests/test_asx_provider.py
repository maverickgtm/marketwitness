import unittest
from datetime import date
from pathlib import Path

from marketwitness.providers.asx import (
    AsxDataError,
    load_asx_snapshot,
    parse_asx_html,
    render_asx_html,
    render_asx_report,
)


class AsxProviderTests(unittest.TestCase):
    def test_loads_official_html_snapshot_and_withdrawal(self) -> None:
        listings = load_asx_snapshot(Path("data/samples/asx-upcoming.html"), date(2026, 5, 24))

        report = render_asx_report(listings, date(2026, 5, 24))
        page = render_asx_html(listings, date(2026, 5, 24))

        self.assertEqual(len(listings), 3)
        self.assertEqual(listings[0].security_code, "BST")
        self.assertEqual(listings[2].status, "withdrawn")
        self.assertIn("formal application", report)
        self.assertIn("Australia", page)
        self.assertIn('href="/dashboard/global-listings">Global Listings Watch</a>', page)

    def test_rejects_missing_required_listing_field(self) -> None:
        with self.assertRaisesRegex(AsxDataError, "missing company, date or code"):
            parse_asx_html(
                '<div class="cmp-accordion__item"><span class="cmp-accordion__title">'
                "Missing Code Ltd - Withdrawn</span><table><tr><td>Listing date</td>"
                "<td>Withdrawn</td></tr></table></div>",
                date(2026, 5, 24),
            )

    def test_rejects_future_snapshot_in_report(self) -> None:
        listings = load_asx_snapshot(Path("data/samples/asx-upcoming.html"), date(2026, 5, 24))
        with self.assertRaisesRegex(AsxDataError, "future observation"):
            render_asx_report(listings, date(2026, 5, 23))


if __name__ == "__main__":
    unittest.main()
