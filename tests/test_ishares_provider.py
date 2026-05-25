import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from targetaudit.etf_holdings import compare_holdings, load_holdings_snapshot
from targetaudit.providers.ishares import (
    IsharesHoldingsDataError,
    load_ishares_holdings_snapshot,
    render_import_report,
    write_normalized_holdings,
)


class IsharesHoldingsProviderTests(unittest.TestCase):
    def test_normalizes_iyf_shaped_fixture_and_omits_cash(self) -> None:
        imported = _import(Path("data/samples/ishares-iyf-holdings-current.csv"))
        report = render_import_report(imported)

        self.assertEqual(imported.effective_date, date(2026, 5, 23))
        self.assertEqual(len(imported.holdings), 3)
        self.assertEqual(imported.omitted_non_equity_positions, 1)
        self.assertEqual(imported.holdings[0].weight_pct, Decimal("4.60"))
        self.assertEqual(imported.source_frequency, "synthetic_demo")
        self.assertIn("No automated iShares download", report)

    def test_outputs_snapshots_accepted_by_activity_engine(self) -> None:
        previous = _import(Path("data/samples/ishares-iyf-holdings-previous.csv"))
        current = _import(Path("data/samples/ishares-iyf-holdings-current.csv"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            previous_path = root / "previous.csv"
            current_path = root / "current.csv"
            write_normalized_holdings(previous_path, previous)
            write_normalized_holdings(current_path, current)
            changes = compare_holdings(
                load_holdings_snapshot(previous_path, date(2026, 5, 24)),
                load_holdings_snapshot(current_path, date(2026, 5, 24)),
            )

        self.assertEqual(
            [change.change_type for change in changes],
            ["new_position", "increased", "decreased", "removed_position"],
        )

    def test_labels_real_manual_file_as_official_snapshot_not_daily_feed(self) -> None:
        imported = load_ishares_holdings_snapshot(
            Path("data/samples/ishares-iyf-holdings-current.csv"),
            "IYF",
            "iShares U.S. Financials ETF",
            date(2026, 5, 24),
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "normalized.csv"
            write_normalized_holdings(output, imported)
            loaded = load_holdings_snapshot(output, date(2026, 5, 24))

        self.assertEqual(imported.source_frequency, "official_snapshot")
        self.assertEqual(loaded[0].source_frequency, "official_snapshot")

    def test_rejects_holdings_date_after_capture(self) -> None:
        with self.assertRaisesRegex(IsharesHoldingsDataError, "after the capture date"):
            load_ishares_holdings_snapshot(
                Path("data/samples/ishares-iyf-holdings-current.csv"),
                "IYF",
                "iShares U.S. Financials ETF",
                date(2026, 5, 22),
            )

    def test_rejects_download_without_holdings_date(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "missing-date.csv"
            path.write_text(
                "Ticker,Name,Asset Class,Weight (%),Shares\n"
                "ACBK,Atlantic Community Bank,Equity,4.6,1200\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(IsharesHoldingsDataError, "holdings-as-of date"):
                _import(path)


def _import(path: Path):
    return load_ishares_holdings_snapshot(
        path,
        "IYF-DEMO",
        "Synthetic iShares Financials ETF",
        date(2026, 5, 24),
        "https://example.invalid/ishares/iyf",
        synthetic_fixture=True,
    )


if __name__ == "__main__":
    unittest.main()
