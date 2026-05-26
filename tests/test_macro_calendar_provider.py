import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from marketwitness.providers.macro_calendar import (
    MacroCalendarDataError,
    build_macro_calendar_snapshot,
    configured_user_agent,
    load_macro_calendar_csv,
    load_macro_snapshots,
    write_macro_calendar_csv,
)


class MacroCalendarProviderTests(unittest.TestCase):
    def test_normalizes_selected_official_shaped_catalysts(self) -> None:
        events = load_macro_snapshots(
            Path("data/samples/fomc-calendar-synthetic.html"),
            Path("data/samples/bls-release-calendar-synthetic.ics"),
            2026,
            date(2026, 5, 26),
        )
        snapshot = build_macro_calendar_snapshot(events, horizon_days=90)

        self.assertEqual(len(events), 7)
        self.assertEqual(snapshot["upcoming_count"], 6)
        self.assertEqual(snapshot["next_event"]["short_label"], "Payrolls")
        fomc = next(event for event in events if event.short_label == "FOMC")
        self.assertTrue(fomc.has_projections)
        self.assertEqual(fomc.end_date.isoformat(), "2026-06-17")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "macro-calendar.csv"
            write_macro_calendar_csv(output, events)
            loaded = load_macro_calendar_csv(output)
        self.assertEqual(loaded, events)

    def test_filters_by_agency_and_rejects_unknown_horizon(self) -> None:
        events = load_macro_snapshots(
            Path("data/samples/fomc-calendar-synthetic.html"),
            Path("data/samples/bls-release-calendar-synthetic.ics"),
            2026,
            date(2026, 5, 26),
        )
        federal_reserve = build_macro_calendar_snapshot(
            events, horizon_days=180, agency="Federal Reserve"
        )

        self.assertEqual(federal_reserve["upcoming_count"], 2)
        with self.assertRaisesRegex(MacroCalendarDataError, "horizon"):
            build_macro_calendar_snapshot(events, horizon_days=45)

    def test_live_collection_requires_configured_contact_without_publishing_email(self) -> None:
        with patch("marketwitness.providers.macro_calendar.LOCAL_USER_AGENT_PATH", Path("/missing")):
            with patch.dict("os.environ", {}, clear=True):
                with self.assertRaisesRegex(MacroCalendarDataError, "contact email"):
                    configured_user_agent()
                self.assertEqual(
                    configured_user_agent("MarketWitness operator@example.com"),
                    "MarketWitness operator@example.com",
                )


if __name__ == "__main__":
    unittest.main()
