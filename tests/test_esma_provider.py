import json
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

from targetaudit.providers.esma import (
    EsmaDataError,
    fetch_esma_equity_prospectuses,
    load_esma_snapshot,
    parse_esma_payload,
    render_esma_html,
    render_esma_report,
)


class EsmaProviderTests(unittest.TestCase):
    def test_filters_official_share_type_from_synthetic_fixture(self) -> None:
        records = load_esma_snapshot(
            Path("data/samples/esma-equity-prospectuses-synthetic.json"),
            date(2026, 5, 25),
            date(2026, 5, 1),
        )
        report = render_esma_report(
            records, date(2026, 5, 25), date(2026, 5, 1), "synthetic_fixture"
        )
        page = render_esma_html(
            records, date(2026, 5, 25), date(2026, 5, 1), "synthetic_fixture"
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].status, "initial_admission_regulated_market_review")
        self.assertEqual(records[1].status, "secondary_issuance_review")
        self.assertNotIn("Excluded Fund Demo", report)
        self.assertNotIn("Excluded Derivative Demo", report)
        self.assertIn("Synthetic ESMA-shaped fixture", report)
        self.assertIn("not official prospectus evidence", page)
        self.assertIn("does not confirm first trading", page)
        self.assertIn("Secondary issuance review", page)
        self.assertNotIn("secondary_issuance_review", page)
        self.assertIn("official ESMA legal notice", page)

    def test_rejects_future_share_prospectus(self) -> None:
        payload = {
            "response": {
                "docs": [
                    _share_row("SYNTH-FUTURE", "DE000FUTURE", "DE", "2026-05-26T00:00:00Z")
                ]
            }
        }

        with self.assertRaisesRegex(EsmaDataError, "after observation date"):
            parse_esma_payload(payload, date(2026, 5, 25), date(2026, 5, 1))

    def test_ignores_shares_outside_supported_jurisdictions(self) -> None:
        payload = {"response": {"docs": [_share_row("SYNTH-FR", "FR000TEST", "FR")]}}

        records = parse_esma_payload(payload, date(2026, 5, 25), date(2026, 5, 1))

        self.assertEqual(records, [])

    def test_rejects_duplicate_document_instrument_pair(self) -> None:
        row = _share_row("SYNTH-DUP", "IT000DUP", "IT")
        payload = {"response": {"docs": [row, row]}}

        with self.assertRaisesRegex(EsmaDataError, "duplicates document/instrument pair"):
            parse_esma_payload(payload, date(2026, 5, 25), date(2026, 5, 1))

    @patch("targetaudit.providers.esma.urlopen")
    def test_live_fetch_paginates_without_dropping_share_records(self, urlopen) -> None:
        first = _response({"response": {"numFound": 2, "docs": [_share_row("DOC-1", "DE000ONE", "DE")]}})
        second = _response({"response": {"numFound": 2, "docs": [_share_row("DOC-2", "IT000TWO", "IT")]}})
        urlopen.side_effect = [first, second]

        records = fetch_esma_equity_prospectuses(
            date(2026, 5, 1), date(2026, 5, 25), page_size=1
        )

        self.assertEqual([record.document_id for record in records], ["DOC-1", "DOC-2"])
        self.assertIn("start=0", urlopen.call_args_list[0].args[0].full_url)
        self.assertIn("start=1", urlopen.call_args_list[1].args[0].full_url)


def _share_row(
    document_id: str,
    isin: str,
    jurisdiction: str,
    filing_date: str = "2026-05-20T00:00:00Z",
) -> dict[str, str]:
    return {
        "sec_isin": isin,
        "sec_securitiesType": "SHRS",
        "sec_securitiesTypeDesc": "Shares",
        "sec_offerAdmType": "IRMT",
        "sec_offerAdmTypeDesc": "Initial admission to trading on regulated market",
        "sec_natDocId": document_id,
        "sec_docLastUpdateDate": "2026-05-21T00:00:00Z",
        "sec_homeMemberStateCode": jurisdiction,
        "sec_approvalFilingDate": filing_date,
        "sec_issuerNameList": "Demo Equity SE - SYNTHLEI",
    }


def _response(payload: dict[str, object]) -> MagicMock:
    response = MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps(payload).encode("utf-8")
    return response


if __name__ == "__main__":
    unittest.main()
