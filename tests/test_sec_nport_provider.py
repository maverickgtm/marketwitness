import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.etf_holdings import compare_holdings, load_holdings_snapshot
from targetaudit.providers.sec_nport import (
    SecNportDataError,
    load_nport_xml_snapshot,
    render_import_report,
    write_normalized_holdings,
)


class SecNportProviderTests(unittest.TestCase):
    def test_normalizes_share_positions_and_omits_cash_fixture(self) -> None:
        imported = load_nport_xml_snapshot(
            Path("data/samples/nport-xlf-current.xml"),
            "XLF-REG-DEMO",
            date(2026, 5, 24),
            "https://example.invalid/sec/nport-xlf-current.xml",
            synthetic_fixture=True,
        )
        report = render_import_report(imported)

        self.assertEqual(len(imported.holdings), 3)
        self.assertEqual(imported.omitted_non_share_positions, 1)
        self.assertEqual(imported.holdings[0].issuer, "TargetAudit Synthetic N-PORT Fixture")
        self.assertEqual(imported.holdings[0].source_frequency, "regulatory_periodic")
        self.assertIn("does not treat periodic N-PORT evidence as", report)

    def test_writes_snapshots_that_compare_in_etf_engine(self) -> None:
        previous = load_nport_xml_snapshot(
            Path("data/samples/nport-xlf-previous.xml"),
            "XLF-REG-DEMO",
            date(2026, 5, 24),
            "https://example.invalid/sec/nport-xlf-previous.xml",
            synthetic_fixture=True,
        )
        current = load_nport_xml_snapshot(
            Path("data/samples/nport-xlf-current.xml"),
            "XLF-REG-DEMO",
            date(2026, 5, 24),
            "https://example.invalid/sec/nport-xlf-current.xml",
            synthetic_fixture=True,
        )
        with tempfile.TemporaryDirectory() as temporary:
            prior_path = Path(temporary) / "previous.csv"
            current_path = Path(temporary) / "current.csv"
            write_normalized_holdings(prior_path, previous)
            write_normalized_holdings(current_path, current)
            changes = compare_holdings(
                load_holdings_snapshot(prior_path, date(2026, 5, 24)),
                load_holdings_snapshot(current_path, date(2026, 5, 24)),
            )

        self.assertEqual(
            [change.change_type for change in changes],
            ["new_position", "increased", "decreased", "removed_position"],
        )

    def test_rejects_non_public_submission_type(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "private.xml"
            content = Path("data/samples/nport-xlf-current.xml").read_text(encoding="utf-8")
            path.write_text(content.replace("NPORT-P", "NPORT-NP"), encoding="utf-8")
            with self.assertRaisesRegex(SecNportDataError, "not public NPORT-P"):
                load_nport_xml_snapshot(path, "XLF", date(2026, 5, 24))


if __name__ == "__main__":
    unittest.main()
