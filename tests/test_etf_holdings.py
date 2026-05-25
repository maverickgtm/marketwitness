import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.etf_holdings import (
    EtfHoldingsDataError,
    compare_holdings,
    load_holdings_snapshot,
    render_holdings_html,
    render_holdings_report,
)


class EtfHoldingsTests(unittest.TestCase):
    def test_compares_published_snapshots_without_calling_changes_trades(self) -> None:
        previous = load_holdings_snapshot(
            Path("data/samples/etf-holdings-previous.csv"), date(2026, 5, 24)
        )
        current = load_holdings_snapshot(
            Path("data/samples/etf-holdings-current.csv"), date(2026, 5, 24)
        )

        changes = compare_holdings(previous, current)
        report = render_holdings_report(previous, current, changes, date(2026, 5, 24))
        page = render_holdings_html(previous, current, changes, date(2026, 5, 24))

        self.assertEqual(
            [change.change_type for change in changes],
            ["new_position", "increased", "decreased", "removed_position", "weight_changed"],
        )
        self.assertIn("not\nconfirmed manager trades", report)
        self.assertIn("Observed changes", page)
        self.assertIn("Demo snapshots are synthetic", page)
        self.assertIn('href="/dashboard/etf/xlf-demo"', page)
        self.assertIn('href="/dashboard/etf/iyf-demo"', page)
        self.assertIn('href="/dashboard/etf/nport-recent"', page)
        self.assertIn('href="/dashboard/etf-regulatory"', page)
        self.assertNotIn("bought", page.lower())
        self.assertNotIn("sold", page.lower())

    def test_rejects_snapshot_captured_after_cutoff(self) -> None:
        with self.assertRaisesRegex(EtfHoldingsDataError, "capture exceeds evidence cutoff"):
            load_holdings_snapshot(
                Path("data/samples/etf-holdings-current.csv"), date(2026, 5, 22)
            )

    def test_rejects_duplicate_position_ticker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.csv"
            content = Path("data/samples/etf-holdings-current.csv").read_text(encoding="utf-8")
            content += content.splitlines()[1] + "\n"
            path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(EtfHoldingsDataError, "duplicate holding ticker"):
                load_holdings_snapshot(path, date(2026, 5, 24))

    def test_rejects_comparison_across_daily_and_regulatory_layers(self) -> None:
        previous = load_holdings_snapshot(
            Path("data/samples/etf-holdings-previous.csv"), date(2026, 5, 24)
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "regulatory.csv"
            content = Path("data/samples/etf-holdings-current.csv").read_text(encoding="utf-8")
            path.write_text(content.replace("synthetic_demo", "regulatory_periodic"), encoding="utf-8")
            current = load_holdings_snapshot(path, date(2026, 5, 24))
            with self.assertRaisesRegex(EtfHoldingsDataError, "same source-frequency layer"):
                compare_holdings(previous, current)


if __name__ == "__main__":
    unittest.main()
