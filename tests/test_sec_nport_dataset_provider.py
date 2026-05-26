import tempfile
import unittest
from datetime import date
from pathlib import Path

from marketwitness.etf_holdings import compare_holdings, load_holdings_snapshot
from marketwitness.providers.sec_nport import SecNportDataError
from marketwitness.providers.sec_nport_dataset import (
    load_nport_dataset_backfill,
    render_backfill_report,
    write_backfill_manifest,
    write_backfill_snapshots,
)


class SecNportDatasetProviderTests(unittest.TestCase):
    def test_normalizes_selected_series_across_dataset_periods(self) -> None:
        backfill = _backfill()
        report = render_backfill_report(backfill)

        self.assertEqual(len(backfill.snapshots), 2)
        self.assertEqual(backfill.snapshots[0].import_result.effective_date, date(2025, 12, 31))
        self.assertEqual(len(backfill.snapshots[1].import_result.holdings), 3)
        self.assertEqual(backfill.snapshots[1].import_result.omitted_non_share_positions, 1)
        self.assertIn("duplicate reporting periods", report)

    def test_outputs_snapshots_manifest_and_comparable_changes(self) -> None:
        backfill = _backfill()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs = write_backfill_snapshots(root / "snapshots", backfill)
            manifest = root / "manifest.csv"
            write_backfill_manifest(manifest, backfill)
            changes = compare_holdings(
                load_holdings_snapshot(outputs[0], date(2026, 5, 24)),
                load_holdings_snapshot(outputs[1], date(2026, 5, 24)),
            )
            manifest_text = manifest.read_text(encoding="utf-8")

        self.assertEqual([path.name for path in outputs], ["xlf-reg-demo-2025-12-31.csv", "xlf-reg-demo-2026-03-31.csv"])
        self.assertEqual(
            [change.change_type for change in changes],
            ["new_position", "increased", "decreased", "removed_position"],
        )
        self.assertIn("2025-Q4 to 2026-Q1 synthetic fixtures", manifest_text)

    def test_rejects_duplicate_period_requiring_amendment_review(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            source = Path("data/samples/nport-dataset/2025q4")
            for item in source.iterdir():
                text = item.read_text(encoding="utf-8")
                if item.name == "SUBMISSION.tsv":
                    text = text.replace("2025-12-31\t2025-12-31", "2026-03-31\t2026-03-31")
                (target / item.name).write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(SecNportDataError, "duplicate periods"):
                load_nport_dataset_backfill(
                    [target, Path("data/samples/nport-dataset/2026q1")],
                    "S000DEMO01",
                    "XLF-REG-DEMO",
                    date(2026, 5, 24),
                    "amended period synthetic fixture",
                    "https://example.invalid/sec/nport-dataset.zip",
                    synthetic_fixture=True,
                )

    def test_rejects_overlapping_periods_across_extracted_quarters(self) -> None:
        source = Path("data/samples/nport-dataset/2025q4")
        with self.assertRaisesRegex(SecNportDataError, "duplicate periods"):
            load_nport_dataset_backfill(
                [source, source],
                "S000DEMO01",
                "XLF-REG-DEMO",
                date(2026, 5, 24),
                "duplicate quarter selection",
                "https://example.invalid/sec/nport-dataset.zip",
                synthetic_fixture=True,
            )


def _backfill():
    return load_nport_dataset_backfill(
        [
            Path("data/samples/nport-dataset/2025q4"),
            Path("data/samples/nport-dataset/2026q1"),
        ],
        "S000DEMO01",
        "XLF-REG-DEMO",
        date(2026, 5, 24),
        "2025-Q4 to 2026-Q1 synthetic fixtures",
        "https://example.invalid/sec/nport-dataset.zip",
        synthetic_fixture=True,
    )


if __name__ == "__main__":
    unittest.main()
