import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.source_registry import (
    SourceRegistryDataError,
    load_source_registry,
    render_source_registry_html,
    render_source_registry_report,
)


class SourceRegistryTests(unittest.TestCase):
    def test_renders_provider_controls_and_blocks_restricted_collection(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        report = render_source_registry_report(providers, date(2026, 5, 25))
        page = render_source_registry_html(providers, date(2026, 5, 25))

        self.assertEqual(len(providers), 33)
        self.assertIn("Authorized Demo Export", report)
        self.assertIn("Alpha Vantage Daily Adjusted", report)
        self.assertIn("S&P DJI Constituent Data", report)
        self.assertIn("ARK ETF holdings downloads", report)
        self.assertIn("State Street SPDR XLF holdings", report)
        self.assertIn("iShares IYF U.S. Financials holdings", report)
        self.assertIn("SEC Form N-PORT public filings", report)
        self.assertIn("SEC EDGAR daily indexes", report)
        self.assertIn("JPX New Listings", report)
        self.assertIn("FSA EDINET Documents API", report)
        self.assertIn("Brazil CVM Public Distribution Offerings Open Data", report)
        self.assertIn("ESMA Prospectus III Securities Register", report)
        self.assertIn("`license_required`", report)
        self.assertIn("`manual_only`", report)
        self.assertIn("TipRanks", report)
        self.assertIn("Finnhub Enterprise Redistribution", report)
        self.assertIn("Financial Modeling Prep Data Display License", report)
        self.assertIn("xStocks / Backed Public API", report)
        self.assertIn("Ondo Global Markets", report)
        self.assertIn("Bybit xStocks V5 Market Data", report)
        self.assertIn("Kraken xStocks", report)
        self.assertIn("Gate Tokenized Stocks", report)
        self.assertIn("Bitget Ondo Tokenized Stocks", report)
        self.assertIn("Blocked from automated collection: `4`", report)
        self.assertIn("market data intended for display", report)
        self.assertIn("Public accessibility is not a license", page)
        self.assertIn("blocked", page)

    def test_rejects_restricted_implemented_provider(self) -> None:
        path = _csv(
            "provider_id,provider_name,data_class,access_model,integration_status,"
            "license_status,publication_policy,official_url,reference_url,reviewed_on,"
            "review_note\n"
            "bad,Bad Provider,Targets,manual_reference,implemented,restricted_no_collection,"
            "source_link_only,https://example.invalid,https://example.invalid/terms,"
            "2026-05-24,Do not collect\n"
        )

        with self.assertRaisesRegex(SourceRegistryDataError, "restricted provider"):
            load_source_registry(path)

    def test_rejects_review_after_cutoff(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        with self.assertRaisesRegex(SourceRegistryDataError, "after the report cutoff"):
            render_source_registry_report(providers, date(2026, 5, 23))


def _csv(content: str) -> Path:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "source-registry.csv"
    path.write_text(content, encoding="utf-8")
    _TEMP_DIRECTORIES.append(directory)
    return path


_TEMP_DIRECTORIES: list[tempfile.TemporaryDirectory] = []


if __name__ == "__main__":
    unittest.main()
