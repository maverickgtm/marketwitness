import unittest
from datetime import date
from pathlib import Path

from targetaudit.licensed_extensions import (
    LicensedExtensionDataError,
    build_licensed_extensions_snapshot,
    load_licensed_extensions,
    render_licensed_extensions_html,
    render_licensed_extensions_report,
)


class LicensedExtensionTests(unittest.TestCase):
    def test_catalogs_user_funded_options_without_public_output_permission(self) -> None:
        extensions = load_licensed_extensions(Path("data/samples/licensed_extensions.csv"))

        snapshot = build_licensed_extensions_snapshot(extensions, date(2026, 5, 24))

        self.assertEqual(snapshot["extension_count"], 6)
        self.assertEqual(snapshot["listed_price_count"], 3)
        self.assertEqual(snapshot["individual_option_count"], 3)
        self.assertEqual(snapshot["public_output_approved_count"], 0)
        massive = next(
            item
            for item in snapshot["items"]
            if item["extension_id"] == "benzinga-massive-analyst-ratings"
        )
        self.assertEqual(massive["price_display"], "USD 99/month")
        self.assertEqual(massive["status"], "available_byol")
        marketbeat = next(
            item for item in snapshot["items"] if item["extension_id"] == "marketbeat-all-access"
        )
        self.assertEqual(marketbeat["price_display"], "USD 249/year or USD 29/month")
        self.assertIn("six months", marketbeat["coverage"])
        self.assertIn("not require these providers", snapshot["policy_note"])
        self.assertIn("USD 99/month", render_licensed_extensions_report(snapshot))
        self.assertIn("MarketBeat All Access", render_licensed_extensions_report(snapshot))
        self.assertIn("Bring your own", render_licensed_extensions_html(snapshot))

    def test_rejects_a_review_after_the_catalog_cutoff(self) -> None:
        extensions = load_licensed_extensions(Path("data/samples/licensed_extensions.csv"))

        with self.assertRaisesRegex(LicensedExtensionDataError, "after the report cutoff"):
            build_licensed_extensions_snapshot(extensions, date(2026, 5, 23))


if __name__ == "__main__":
    unittest.main()
