import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from marketwitness.etf_holdings import compare_holdings, load_holdings_snapshot
from marketwitness.providers.sec_nport import (
    SecNportDataError,
    collect_latest_nport_snapshot,
    fetch_recent_nport_filings,
    load_nport_document,
    load_nport_xml_snapshot,
    load_recent_nport_filings,
    parse_recent_nport_filings,
    render_collection_report,
    render_import_report,
    submissions_url,
    write_normalized_holdings,
)


class SecNportProviderTests(unittest.TestCase):
    def test_constructs_submissions_endpoint_and_filters_nport_filings(self) -> None:
        filings = load_recent_nport_filings(
            Path("data/samples/sec-nport-submissions.json"),
            "1",
            "https://example.invalid/sec-nport-fixture",
        )

        self.assertEqual(submissions_url("1"), "https://data.sec.gov/submissions/CIK0000000001.json")
        self.assertEqual(len(filings), 2)
        self.assertEqual(filings[0].accession_number, "0000000001-26-000002")
        self.assertEqual(
            filings[0].source_url,
            "https://example.invalid/sec-nport-fixture/edgar/data/1/"
            "000000000126000002/nport-xlf-current.xml",
        )

    @patch("marketwitness.providers.sec_nport.urlopen")
    def test_fetch_uses_declared_sec_user_agent(self, request_mock) -> None:
        content = Path("data/samples/sec-nport-submissions.json").read_bytes()
        request_mock.return_value.__enter__.return_value = _Response(content)

        filings = fetch_recent_nport_filings("1", "MarketWitness owner@example.com")

        self.assertEqual(len(filings), 2)
        request = request_mock.call_args.args[0]
        self.assertEqual(request.headers["User-agent"], "MarketWitness owner@example.com")

    def test_normalizes_sec_xsl_display_path_to_raw_xml_document(self) -> None:
        payload = json.loads(
            Path("data/samples/sec-nport-submissions.json").read_text(encoding="utf-8")
        )
        payload["filings"]["recent"]["primaryDocument"][0] = (
            "xslFormNPORT-P_X01/primary_doc.xml"
        )

        filings = parse_recent_nport_filings(payload, "1064641")

        self.assertEqual(filings[0].primary_document, "primary_doc.xml")
        self.assertTrue(filings[0].source_url.endswith("/primary_doc.xml"))
        self.assertNotIn("xslFormNPORT-P_X01", filings[0].source_url)

    def test_collects_latest_matching_series_and_archives_xml(self) -> None:
        filings = load_recent_nport_filings(
            Path("data/samples/sec-nport-submissions.json"),
            "1",
            "https://example.invalid/sec-nport-fixture",
        )
        with tempfile.TemporaryDirectory() as temporary:
            collection = collect_latest_nport_snapshot(
                filings,
                "S000DEMO01",
                "XLF-REG-DEMO",
                date(2026, 5, 24),
                temporary,
                lambda filing: load_nport_document(
                    Path("data/samples") / filing.primary_document
                ),
                synthetic_fixture=True,
            )
            report = render_collection_report(collection)

            self.assertTrue(collection.archived_xml.exists())
            self.assertEqual(collection.filing.accession_number, "0000000001-26-000002")
            self.assertIn("accepts a filing only after its XML confirms", report)

    def test_skips_newer_filing_for_another_series(self) -> None:
        filings = load_recent_nport_filings(
            Path("data/samples/sec-nport-submissions.json"),
            "1",
            "https://example.invalid/sec-nport-fixture",
        )

        def documents(filing):
            content = load_nport_document(Path("data/samples") / filing.primary_document)
            if filing.primary_document == "nport-xlf-current.xml":
                return content.replace("S000DEMO01", "S000OTHER01")
            return content

        with tempfile.TemporaryDirectory() as temporary:
            collection = collect_latest_nport_snapshot(
                filings,
                "S000DEMO01",
                "XLF-REG-DEMO",
                date(2026, 5, 24),
                temporary,
                documents,
                synthetic_fixture=True,
            )

        self.assertEqual(collection.filing.accession_number, "0000000001-26-000001")

    def test_does_not_archive_filing_that_fails_temporal_validation(self) -> None:
        filings = load_recent_nport_filings(
            Path("data/samples/sec-nport-submissions.json"),
            "1",
            "https://example.invalid/sec-nport-fixture",
        )

        def future_document(filing):
            content = load_nport_document(Path("data/samples") / filing.primary_document)
            return content.replace("2026-03-31", "2026-09-30")

        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(SecNportDataError, "capture precedes"):
                collect_latest_nport_snapshot(
                    filings[:1],
                    "S000DEMO01",
                    "XLF-REG-DEMO",
                    date(2026, 5, 24),
                    temporary,
                    future_document,
                    synthetic_fixture=True,
                )
            archived = list(Path(temporary).rglob("*.xml"))

        self.assertEqual(archived, [])

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
        self.assertEqual(imported.holdings[0].issuer, "MarketWitness Synthetic N-PORT Fixture")
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


class _Response:
    def __init__(self, content: bytes) -> None:
        self.content = content

    def read(self) -> bytes:
        return self.content
