import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.global_listings import (
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

        self.assertEqual(len(sources), 5)
        self.assertIn("London Stock Exchange", report)
        self.assertIn("Hong Kong Exchanges and Clearing", report)
        self.assertIn("Live official feeds: `5`", report)
        self.assertIn("Verified snapshots: `0`", report)
        self.assertIn("Beyond Wall Street", page)
        self.assertIn("HKEX, LSE, ASX, TSX and SGX have official ingestion paths", page)
        self.assertIn('href="global-alerts.html"', page)
        self.assertIn('href="hkex-monitor.html"', page)
        self.assertIn('href="lse-upcoming.html"', page)
        self.assertIn('href="lse-fca-check.html"', page)
        self.assertIn('href="asx-monitor.html"', page)
        self.assertIn('href="tsx-monitor.html"', page)
        self.assertIn('href="sgx-monitor.html"', page)
        self.assertIn('href="issuer-confirmations.html"', page)
        self.assertIn('href="source-registry.html"', page)

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
