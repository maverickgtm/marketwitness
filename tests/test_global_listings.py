import tempfile
import unittest
from datetime import date
from pathlib import Path

from marketwitness.global_listings import (
    GlobalListingsDataError,
    load_global_market_sources,
    render_global_listings_html,
    render_global_listings_report,
)


class GlobalListingsTests(unittest.TestCase):
    def test_renders_global_sources_and_priority_connectors(self) -> None:
        sources = load_global_market_sources(Path("data/samples/global_market_sources.csv"))

        report = render_global_listings_report(sources, date(2026, 5, 24))
        page = render_global_listings_html(sources, date(2026, 5, 24))

        self.assertEqual(len(sources), 10)
        self.assertIn("London Stock Exchange", report)
        self.assertIn("Hong Kong Exchanges and Clearing", report)
        self.assertIn("Tokyo Stock Exchange / Japan EDINET", report)
        self.assertIn("JPX New Listings plus FSA EDINET Documents API", report)
        self.assertIn("Brazil CVM Open Data Portal", report)
        self.assertIn("European Union Prospectus Register", report)
        self.assertIn("Korea Exchange / OpenDART", report)
        self.assertIn("Moscow Exchange / Bank of Russia", report)
        self.assertIn("keep MAS OPERA as manual reference only", report)
        self.assertIn("Live official feeds: `9`", report)
        self.assertIn("Verified snapshots: `0`", report)
        self.assertIn("Priority connectors: `0`", report)
        self.assertIn("Restricted research-only markets: `1`", report)
        self.assertIn("Beyond Wall Street", page)
        self.assertIn("0 priority; 0 planned", page)
        self.assertIn("Documented only; no ingestion", page)
        self.assertIn('href="/dashboard/ipo">IPO Watch Center</a>', page)
        self.assertIn("HKEX, LSE, ASX, TSX, JPX, SGX, CVM, ESMA and OpenDART have official ingestion paths", page)
        self.assertIn('href="/dashboard/global-alerts"', page)
        self.assertIn('href="/dashboard/contribute?lang=en"', page)
        self.assertIn("Coverage Grid", page)
        self.assertIn("Open change review", page)
        self.assertIn('href="/dashboard/global/hkex"', page)
        self.assertIn('href="/dashboard/global/lse-upcoming"', page)
        self.assertIn('href="/dashboard/document-checks"', page)
        self.assertIn('href="/dashboard/global/asx"', page)
        self.assertIn('href="/dashboard/global/tsx"', page)
        self.assertIn('href="/dashboard/global/jpx"', page)
        self.assertIn('href="/dashboard/global/edinet"', page)
        self.assertIn('href="/dashboard/global/cvm"', page)
        self.assertIn('href="/dashboard/global/esma"', page)
        self.assertIn('href="/dashboard/global/opendart"', page)
        self.assertIn('href="/dashboard/global/sgx"', page)
        self.assertIn('href="/dashboard/issuer-confirmations"', page)
        self.assertIn('href="/dashboard/etf-regulatory"', page)
        self.assertIn('href="/dashboard/governance"', page)

    def test_rejects_unknown_connector_status(self) -> None:
        path = _csv(
            "market_code,market_name,jurisdiction,connector_status,official_source_name,"
            "official_source_url,signal_type,confirmation_rule,implementation_next\n"
            "LSE,London,UK,live_without_adapter,LSE,https://example.invalid,L,Rule,Build\n"
        )

        with self.assertRaisesRegex(GlobalListingsDataError, "invalid status"):
            load_global_market_sources(path)


def _csv(content: str) -> Path:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "markets.csv"
    path.write_text(content, encoding="utf-8")
    _TEMP_DIRECTORIES.append(directory)
    return path


_TEMP_DIRECTORIES: list[tempfile.TemporaryDirectory] = []


if __name__ == "__main__":
    unittest.main()
