import unittest
from datetime import date
from pathlib import Path

from targetaudit.providers.hkex import (
    HkexDataError,
    load_hkex_snapshot,
    parse_hkex_payload,
    render_hkex_html,
    render_hkex_report,
)


class HkexProviderTests(unittest.TestCase):
    def test_loads_official_feed_snapshot_and_renders_statuses(self) -> None:
        listings, updates = load_hkex_snapshot(Path("data/samples/hkex"))

        report = render_hkex_report(listings, updates, date(2026, 5, 24))
        page = render_hkex_html(listings, updates, date(2026, 5, 24))

        self.assertEqual(len(listings), 5)
        self.assertIn("Active applications: `1`", report)
        self.assertIn("Active applications with PHIP: `1`", report)
        self.assertIn("TenNor Therapeutics", report)
        self.assertIn("Official listing signals", page)
        self.assertIn("EnjoyGo Technology Limited", page)
        self.assertIn("Active / PHIP", page)

    def test_maps_returned_date_and_rejects_invalid_update_date(self) -> None:
        listings, updated = parse_hkex_payload(
            {"uDate": "22/05/2026", "app": [{"a": "Issuer", "rd": "20/05/2026"}]},
            "returned",
            "https://example.invalid/feed.json",
        )

        self.assertEqual(updated, "22/05/2026")
        self.assertEqual(listings[0].event_date, date(2026, 5, 20))

        with self.assertRaisesRegex(HkexDataError, "invalid update date"):
            parse_hkex_payload({"uDate": "bad", "app": []}, "active", "feed")

    def test_refuses_future_event_in_report(self) -> None:
        listings, updates = load_hkex_snapshot(Path("data/samples/hkex"))
        with self.assertRaisesRegex(HkexDataError, "after report date"):
            render_hkex_report(listings, updates, date(2026, 5, 1))


if __name__ == "__main__":
    unittest.main()
