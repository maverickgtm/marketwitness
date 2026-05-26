import unittest
from datetime import date
from pathlib import Path

from marketwitness.providers.tsx import (
    TsxDataError,
    load_tsx_snapshot,
    parse_tsx_html,
    render_tsx_html,
    render_tsx_report,
)


class TsxProviderTests(unittest.TestCase):
    def test_loads_official_new_listing_snapshot(self) -> None:
        listings = load_tsx_snapshot(
            Path("data/samples/tsx-new-listings.html"), date(2026, 5, 24)
        )

        report = render_tsx_report(listings, date(2026, 5, 24))
        page = render_tsx_html(listings, date(2026, 5, 24))

        self.assertEqual(len(listings), 3)
        self.assertEqual(listings[0].symbols, "PDI")
        self.assertEqual(listings[0].status, "listed")
        self.assertIn("confirm listed companies", report)
        self.assertIn("Canada", page)
        self.assertIn('href="/dashboard/global-listings">Global Listings Watch</a>', page)

    def test_rejects_invalid_listing_date(self) -> None:
        page = (
            '<table class="two-columns-list"><tr><td>Not a date</td><td>'
            '<a href="/details">Example Ltd (EX)</a></td></tr></table>'
        )
        with self.assertRaisesRegex(TsxDataError, "invalid date"):
            parse_tsx_html(page, date(2026, 5, 24))

    def test_rejects_future_snapshot_in_report(self) -> None:
        listings = load_tsx_snapshot(
            Path("data/samples/tsx-new-listings.html"), date(2026, 5, 24)
        )
        with self.assertRaisesRegex(TsxDataError, "future observation"):
            render_tsx_report(listings, date(2026, 5, 23))


if __name__ == "__main__":
    unittest.main()
