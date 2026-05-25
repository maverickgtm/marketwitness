import json
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

from targetaudit.providers.opendart import (
    OpenDartDataError,
    fetch_opendart_equity_filings,
    load_opendart_snapshot,
    parse_opendart_payload,
    render_opendart_html,
    render_opendart_report,
)


class OpenDartProviderTests(unittest.TestCase):
    def test_filters_equity_issuance_disclosures_from_synthetic_fixture(self) -> None:
        filings = load_opendart_snapshot(
            Path("data/samples/opendart-equity-filings-synthetic.json"),
            date(2026, 5, 25),
            date(2026, 5, 1),
        )
        report = render_opendart_report(
            filings, date(2026, 5, 25), date(2026, 5, 1), "synthetic_fixture"
        )
        page = render_opendart_html(
            filings, date(2026, 5, 25), date(2026, 5, 1), "synthetic_fixture"
        )

        self.assertEqual(len(filings), 2)
        self.assertEqual(filings[0].status, "equity_securities_registration_review")
        self.assertEqual(filings[1].status, "small_equity_public_offering_review")
        self.assertNotIn("Excluded Debt", report)
        self.assertIn("Synthetic OpenDART-shaped fixture", report)
        self.assertIn("not official filing evidence", page)
        self.assertIn("does not confirm an IPO", page)
        self.assertIn("Equity securities registration review", page)

    @patch.dict("os.environ", {}, clear=True)
    def test_live_collection_requires_user_api_key(self) -> None:
        with self.assertRaisesRegex(OpenDartDataError, "requires --api-key"):
            fetch_opendart_equity_filings(date(2026, 5, 1), date(2026, 5, 25))

    def test_rejects_future_equity_filing(self) -> None:
        payload = _payload([_row("20260526000001", "20260526")])

        with self.assertRaisesRegex(OpenDartDataError, "future filing"):
            parse_opendart_payload(payload, "C001", date(2026, 5, 25), date(2026, 5, 1))

    def test_ignores_non_equity_disclosure_type(self) -> None:
        filings = parse_opendart_payload(
            _payload([_row("20260521000001", "20260521")]),
            "C002",
            date(2026, 5, 25),
            date(2026, 5, 1),
        )

        self.assertEqual(filings, [])

    @patch("targetaudit.providers.opendart.urlopen")
    def test_live_fetch_queries_both_equity_types_and_paginates(self, urlopen) -> None:
        urlopen.side_effect = [
            _response(_payload([_row("20260521000001", "20260521")], total_page=2)),
            _response(_payload([_row("20260522000002", "20260522")], page_no=2, total_page=2)),
            _response({"status": "013", "message": "No data."}),
        ]

        filings = fetch_opendart_equity_filings(
            date(2026, 5, 1), date(2026, 5, 25), api_key="test-key", page_size=1
        )

        self.assertEqual(len(filings), 2)
        urls = [call.args[0].full_url for call in urlopen.call_args_list]
        self.assertIn("pblntf_detail_ty=C001", urls[0])
        self.assertIn("page_no=2", urls[1])
        self.assertIn("pblntf_detail_ty=C006", urls[2])


def _row(filing_id: str, filing_date: str) -> dict[str, str]:
    return {
        "corp_cls": "K",
        "corp_name": "Demo Korea Co., Ltd.",
        "corp_code": "01000001",
        "stock_code": "900001",
        "report_nm": "Synthetic Equity Securities Registration Statement",
        "rcept_no": filing_id,
        "rcept_dt": filing_date,
    }


def _payload(rows: list[dict[str, str]], page_no: int = 1, total_page: int = 1) -> dict[str, object]:
    return {
        "status": "000",
        "message": "Normal",
        "page_no": page_no,
        "page_count": 100,
        "total_count": len(rows),
        "total_page": total_page,
        "list": rows,
    }


def _response(payload: dict[str, object]) -> MagicMock:
    response = MagicMock()
    response.__enter__.return_value.read.return_value = json.dumps(payload).encode("utf-8")
    return response


if __name__ == "__main__":
    unittest.main()
