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

        self.assertEqual(len(alerts), 3)
        spacex = next(item for item in alerts if item.watch_company == "SpaceX")
        self.assertEqual(spacex.alert_type, "watchlist_filing_review")
        self.assertEqual(spacex.triage_category, "watchlist_match")
        spac = next(item for item in alerts if item.company_name == "EXAMPLE ACQUISITION CORP.")
        self.assertEqual(spac.triage_category, "possible_spac_name_signal")
        self.assertEqual(spac.review_priority, "medium")
        self.assertNotIn("EXAMPLE INTERNATIONAL LTD.", report)
        self.assertIn("neither mechanism automatically confirms an IPO", report)
        self.assertIn("Public filings", page)
        self.assertIn("SPAC name signals", page)
        self.assertIn('href="/dashboard/ipo">IPO Watch Center</a>', page)

    def test_archive_suppresses_same_document_on_repeated_run(self) -> None:
        filings = load_discovered_filings(Path("data/samples/sec-ipo-discovery.csv"))
        watchlist = load_ipo_watch(Path("data/samples/ipo_watch.csv"))
        with tempfile.TemporaryDirectory() as temporary:
            history = Path(temporary)
            archive_discovery(history, Path("data/samples/sec-ipo-discovery.csv"), date(2026, 5, 20))
            seen = known_source_urls(history, date(2026, 5, 20))
            alerts = build_filing_alerts(filings, watchlist, seen)

        self.assertEqual(alerts, [])
        self.assertEqual(len(seen), 4)

    def test_marks_etf_name_signal_as_low_priority(self) -> None:
        filings = load_discovered_filings(Path("data/samples/sec-ipo-discovery.csv"))
        filing = filings[0].__class__(
            cik="0000000123",
            company_name="EXAMPLE FUTURE ETF",
            form="S-1",
            filed_date=date(2026, 5, 20),
            archive_path="edgar/data/123/etf.txt",
            source_url="https://www.sec.gov/Archives/edgar/data/123/etf.txt",
            review_state="initial_registration_review",
        )

        alerts = build_filing_alerts([filing], [], set())

        self.assertEqual(alerts[0].triage_category, "fund_or_etf_name_signal")
        self.assertEqual(alerts[0].review_priority, "low")


if __name__ == "__main__":
    unittest.main()
