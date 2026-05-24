import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.ipo_watch import load_ipo_watch
from targetaudit.sec_alerts import (
    archive_discovery,
    build_filing_alerts,
    known_source_urls,
    load_discovered_filings,
    render_sec_alerts_html,
    render_sec_alerts_report,
)


class SecAlertsTests(unittest.TestCase):
    def test_routes_new_sec_filing_to_watched_company_by_cik(self) -> None:
        filings = load_discovered_filings(Path("data/samples/sec-ipo-discovery.csv"))
        watchlist = load_ipo_watch(Path("data/samples/ipo_watch.csv"))
        seen = known_source_urls(Path("data/samples/sec-alerts-history"), date(2026, 5, 20))

        alerts = build_filing_alerts(filings, watchlist, seen)
        report = render_sec_alerts_report(alerts, filings, date(2026, 5, 20), len(seen))
        page = render_sec_alerts_html(alerts, filings, date(2026, 5, 20), len(seen))

        self.assertEqual(len(alerts), 2)
        spacex = next(item for item in alerts if item.watch_company == "SpaceX")
        self.assertEqual(spacex.alert_type, "watchlist_filing_review")
        self.assertNotIn("EXAMPLE INTERNATIONAL LTD.", report)
        self.assertIn("does not automatically confirm an IPO", report)
        self.assertIn("Public filings", page)

    def test_archive_suppresses_same_document_on_repeated_run(self) -> None:
        filings = load_discovered_filings(Path("data/samples/sec-ipo-discovery.csv"))
        watchlist = load_ipo_watch(Path("data/samples/ipo_watch.csv"))
        with tempfile.TemporaryDirectory() as temporary:
            history = Path(temporary)
            archive_discovery(history, Path("data/samples/sec-ipo-discovery.csv"), date(2026, 5, 20))
            seen = known_source_urls(history, date(2026, 5, 20))
            alerts = build_filing_alerts(filings, watchlist, seen)

        self.assertEqual(alerts, [])
        self.assertEqual(len(seen), 3)


if __name__ == "__main__":
    unittest.main()
