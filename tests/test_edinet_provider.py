import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from targetaudit.providers.edinet import (
    EdinetDataError,
    fetch_edinet_offering_filings,
    load_edinet_snapshot,
    parse_edinet_payload,
    render_edinet_html,
    render_edinet_report,
)


class EdinetProviderTests(unittest.TestCase):
    def test_filters_offering_document_types_from_synthetic_fixture(self) -> None:
        filings = load_edinet_snapshot(
            Path("data/samples/edinet-offering-filings-synthetic.json"),
            date(2026, 5, 25),
        )

        report = render_edinet_report(filings, date(2026, 5, 25), "synthetic_fixture")
        page = render_edinet_html(filings, date(2026, 5, 25), "synthetic_fixture")

        self.assertEqual(len(filings), 2)
        self.assertEqual(filings[0].status, "securities_registration_statement")
        self.assertEqual(filings[1].status, "amended_securities_registration_statement")
        self.assertNotIn("Ignored Annual", report)
        self.assertIn("Synthetic EDINET-shaped fixture", report)
        self.assertIn("not public filing evidence", page)
        self.assertIn("Synthetic identifier", page)
        self.assertIn("Amendment", page)
        self.assertIn('href="/dashboard/global-listings">Global Listings Watch</a>', page)
        self.assertNotIn("api.edinet-fsa.go.jp/api/v2/documents/SYNTH", page)

    @patch.dict("os.environ", {}, clear=True)
    def test_live_collection_requires_user_api_key(self) -> None:
        with self.assertRaisesRegex(EdinetDataError, "requires --api-key"):
            fetch_edinet_offering_filings(date(2026, 5, 25))

    def test_rejects_future_filing(self) -> None:
        payload = {
            "results": [
                {
                    "docID": "SYNTHFUTURE",
                    "edinetCode": "E9FUTURE",
                    "filerName": "Future Demo Co.",
                    "docTypeCode": "030",
                    "submitDateTime": "2026-05-26 09:00",
                }
            ]
        }
        with self.assertRaisesRegex(EdinetDataError, "future filing"):
            parse_edinet_payload(payload, date(2026, 5, 25))

    def test_rejects_duplicate_document_id(self) -> None:
        row = {
            "docID": "SYNTHDUP",
            "edinetCode": "E9DUP",
            "filerName": "Duplicate Demo Co.",
            "docTypeCode": "030",
            "submitDateTime": "2026-05-25 09:00",
        }
        with self.assertRaisesRegex(EdinetDataError, "duplicates document ID"):
            parse_edinet_payload({"results": [row, row]}, date(2026, 5, 25))


if __name__ == "__main__":
    unittest.main()
