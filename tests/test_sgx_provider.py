import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from marketwitness.providers.sgx import (
    SgxDataError,
    fetch_sgx_prospectuses,
    load_sgx_snapshot,
    parse_sgx_records,
    render_sgx_html,
    render_sgx_report,
)


class SgxProviderTests(unittest.TestCase):
    def test_loads_official_prospectus_snapshot(self) -> None:
        prospectuses = load_sgx_snapshot(
            Path("data/samples/sgx-ipo-prospectus.json"), date(2026, 5, 24)
        )

        report = render_sgx_report(prospectuses, date(2026, 5, 24))
        page = render_sgx_html(prospectuses, date(2026, 5, 24))

        self.assertEqual(len(prospectuses), 3)
        self.assertEqual(prospectuses[0].company_name, "JUSTCO HOLDINGS LIMITED")
        self.assertEqual(prospectuses[0].closing_date, "2026-05-20 12:00 SGT")
        self.assertEqual(prospectuses[1].closing_date, "-")
        self.assertIn("prospectus_published", report)
        self.assertIn("Singapore", page)
        self.assertIn('href="/dashboard/global-listings">Global Listings Watch</a>', page)

    def test_rejects_invalid_closing_date(self) -> None:
        record = {
            "name": "Issuer",
            "id": "1",
            "status": "Completed",
            "url": "https://links.sgx.com/document",
            "closing_date": "bad",
        }
        with self.assertRaisesRegex(SgxDataError, "invalid closing date"):
            parse_sgx_records([record], date(2026, 5, 24))

    def test_rejects_future_snapshot_in_report(self) -> None:
        prospectuses = load_sgx_snapshot(
            Path("data/samples/sgx-ipo-prospectus.json"), date(2026, 5, 24)
        )
        with self.assertRaisesRegex(SgxDataError, "future observation"):
            render_sgx_report(prospectuses, date(2026, 5, 23))

    @patch("marketwitness.providers.sgx.date")
    @patch("marketwitness.providers.sgx._fetch_json")
    def test_fetch_uses_sgx_page_numbers(self, fetch_json, provider_date) -> None:
        provider_date.today.return_value = date(2026, 5, 24)
        record = {
            "name": "Issuer",
            "id": "1",
            "status": "Completed",
            "url": "https://links.sgx.com/document",
            "closing_date": None,
        }
        fetch_json.side_effect = [
            {"count": 251},
            {"data": [dict(record, id=str(index)) for index in range(250)]},
            {"data": [dict(record, id="250")]},
        ]

        results = fetch_sgx_prospectuses()

        self.assertEqual(len(results), 251)
        self.assertIn("pagestart=0", fetch_json.call_args_list[1].args[0])
        self.assertIn("pagestart=1", fetch_json.call_args_list[2].args[0])


if __name__ == "__main__":
    unittest.main()
