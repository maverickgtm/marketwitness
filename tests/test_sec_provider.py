import unittest
from unittest.mock import patch
from urllib.error import URLError

from targetaudit.providers.sec import (
    SecDataError,
    fetch_company_ticker_map,
    parse_company_ticker_payload,
)


class SecProviderTests(unittest.TestCase):
    def test_parses_company_ticker_rows_and_pads_cik(self) -> None:
        payload = {
            "fields": ["cik", "name", "ticker", "exchange"],
            "data": [[320193, "Apple Inc.", "AAPL", "Nasdaq"]],
        }

        result = parse_company_ticker_payload(payload)

        self.assertEqual(result[0]["cik"], "0000320193")
        self.assertEqual(result[0]["ticker"], "AAPL")
        self.assertEqual(result[0]["source_provider"], "sec")

    def test_rejects_unknown_payload_shape(self) -> None:
        with self.assertRaises(SecDataError):
            parse_company_ticker_payload({"data": []})

    def test_requires_contact_email_in_user_agent(self) -> None:
        with self.assertRaisesRegex(SecDataError, "contact email"):
            fetch_company_ticker_map("TargetAudit")

    @patch("targetaudit.providers.sec.urlopen", side_effect=URLError("offline"))
    def test_network_error_becomes_provider_error(self, unused_request) -> None:
        with self.assertRaisesRegex(SecDataError, "Unable to retrieve"):
            fetch_company_ticker_map("TargetAudit contact@example.com")


if __name__ == "__main__":
    unittest.main()
