import unittest
from datetime import date
from pathlib import Path

from marketwitness.providers.sec_ipo import (
    daily_master_index_url,
    load_master_index,
    parse_ipo_candidate_filings,
    render_discovery_html,
    render_discovery_report,
)


class SecIpoDiscoveryTests(unittest.TestCase):
    def test_constructs_quarterly_daily_master_index_url(self) -> None:
        result = daily_master_index_url(date(2026, 5, 20))

        self.assertEqual(
            result,
            "https://www.sec.gov/Archives/edgar/daily-index/2026/QTR2/master.20260520.idx",
        )

    def test_filters_discovery_forms_from_complete_daily_index(self) -> None:
        text, source = load_master_index(Path("data/samples/sec-master-sample.idx"))

        filings = parse_ipo_candidate_filings(text)
        report = render_discovery_report(filings, date(2026, 5, 20), source)
        page = render_discovery_html(filings, date(2026, 5, 20), source)

        self.assertEqual(len(filings), 4)
        self.assertIn("EXAMPLE INTERNATIONAL LTD.", [filing.company_name for filing in filings])
        self.assertIn("EXAMPLE ACQUISITION CORP.", [filing.company_name for filing in filings])
        self.assertIn("SPACE EXPLORATION TECHNOLOGIES CORP.", report)
        self.assertNotIn("APPLE INC.", report)
        self.assertIn("not a confirmed IPO calendar", report)
        self.assertIn("Universal intake.", page)
        self.assertIn("not a confirmed IPO calendar", page)
        self.assertIn("SPACE EXPLORATION TECHNOLOGIES CORP.", page)
        self.assertIn("Bundled SEC-shaped index fixture", page)
        self.assertIn('href="/dashboard/ipo">IPO Watch Center</a>', page)
        self.assertNotIn("file:", page)

    def test_accepts_iso_date_from_normalized_import(self) -> None:
        filings = parse_ipo_candidate_filings(
            "1|Example Corp|S-1|2026-05-20|edgar/data/1/example.txt"
        )

        self.assertEqual(filings[0].filed_date, date(2026, 5, 20))


if __name__ == "__main__":
    unittest.main()
