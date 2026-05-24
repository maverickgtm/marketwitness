import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from targetaudit.etf_holdings import load_holdings_snapshot
from targetaudit.providers.spdr import (
    SpdrHoldingsDataError,
    load_spdr_holdings_snapshot,
    render_import_report,
    write_normalized_holdings,
)


class SpdrHoldingsProviderTests(unittest.TestCase):
    def test_normalizes_xlf_shaped_fixture_as_synthetic_evidence(self) -> None:
        imported = load_spdr_holdings_snapshot(
            Path("data/samples/spdr-xlf-holdings-current.csv"),
            "XLF-DEMO",
            "Synthetic Financials ETF",
            date(2026, 5, 23),
            "https://example.invalid/spdr-demo/2026-05-23",
            synthetic_fixture=True,
        )
        report = render_import_report(imported)

        self.assertEqual(len(imported.holdings), 4)
        self.assertEqual(imported.holdings[0].weight_pct, Decimal("4.60"))
        self.assertEqual(imported.source_frequency, "synthetic_demo")
        self.assertEqual(imported.holdings[0].issuer, "TargetAudit Synthetic SPDR-format Fixture")
        self.assertIn("synthetic only", report)

    def test_writes_snapshot_accepted_by_etf_activity_engine(self) -> None:
        imported = load_spdr_holdings_snapshot(
            Path("data/samples/spdr-xlf-holdings-current.csv"),
            "XLF-DEMO",
            "Synthetic Financials ETF",
            date(2026, 5, 23),
            "https://example.invalid/spdr-demo/2026-05-23",
            synthetic_fixture=True,
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "normalized.csv"
            write_normalized_holdings(output, imported)
            loaded = load_holdings_snapshot(output, date(2026, 5, 24))

        self.assertEqual(loaded[0].fund_symbol, "XLF-DEMO")
        self.assertEqual(loaded[3].position_ticker, "NEWF")

    def test_rejects_mismatched_fund_symbol(self) -> None:
        with self.assertRaisesRegex(SpdrHoldingsDataError, "not requested fund"):
            load_spdr_holdings_snapshot(
                Path("data/samples/spdr-xlf-holdings-current.csv"),
                "XLK",
                "Technology Select Sector SPDR ETF",
                date(2026, 5, 23),
            )


if __name__ == "__main__":
    unittest.main()
