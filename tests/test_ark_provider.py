import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.etf_holdings import load_holdings_snapshot
from targetaudit.providers.ark import (
    ArkHoldingsDataError,
    load_ark_holdings_snapshot,
    render_import_report,
    write_normalized_holdings,
)


class ArkHoldingsProviderTests(unittest.TestCase):
    def test_normalizes_ark_shaped_fixture_without_labeling_it_official(self) -> None:
        imported = load_ark_holdings_snapshot(
            Path("data/samples/ark-holdings-current.csv"),
            "ARKK-DEMO",
            "Synthetic ARK-format ETF",
            date(2026, 5, 23),
            "https://example.invalid/ark-demo/2026-05-23",
            synthetic_fixture=True,
        )
        report = render_import_report(imported)

        self.assertEqual(len(imported.holdings), 4)
        self.assertEqual(imported.holdings[0].shares, 1200)
        self.assertEqual(imported.source_frequency, "synthetic_demo")
        self.assertEqual(imported.holdings[0].issuer, "TargetAudit Synthetic ARK-format Fixture")
        self.assertIn("synthetic only", report)

    def test_writes_snapshot_accepted_by_etf_activity_engine(self) -> None:
        imported = load_ark_holdings_snapshot(
            Path("data/samples/ark-holdings-current.csv"),
            "ARKK-DEMO",
            "Synthetic ARK-format ETF",
            date(2026, 5, 23),
            "https://example.invalid/ark-demo/2026-05-23",
            synthetic_fixture=True,
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "normalized.csv"
            write_normalized_holdings(output, imported)
            loaded = load_holdings_snapshot(output, date(2026, 5, 24))

        self.assertEqual(loaded[3].position_ticker, "NEWF")

    def test_rejects_rows_for_a_different_fund(self) -> None:
        with self.assertRaisesRegex(ArkHoldingsDataError, "not requested fund"):
            load_ark_holdings_snapshot(
                Path("data/samples/ark-holdings-current.csv"),
                "ARKW",
                "ARK Next Generation Internet ETF",
                date(2026, 5, 23),
            )

    def test_accepts_next_trading_day_effective_date_after_capture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            snapshot = Path(temporary) / "next-day.csv"
            content = Path("data/samples/ark-holdings-current.csv").read_text(encoding="utf-8")
            snapshot.write_text(content.replace("05/23/2026", "05/26/2026"), encoding="utf-8")
            imported = load_ark_holdings_snapshot(
                snapshot,
                "ARKK-DEMO",
                "Synthetic ARK-format ETF",
                date(2026, 5, 23),
                "https://example.invalid/ark-demo/2026-05-23",
                synthetic_fixture=True,
            )

        self.assertEqual(imported.effective_date, date(2026, 5, 26))
        self.assertEqual(imported.captured_on, date(2026, 5, 23))


if __name__ == "__main__":
    unittest.main()
