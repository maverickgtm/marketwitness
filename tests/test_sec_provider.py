import unittest
import os
from unittest.mock import patch
from urllib.error import URLError

from marketwitness.providers.sec import (
    SecDataError,
    configured_user_agent,
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
            fetch_company_ticker_map("MarketWitness")

    @patch.dict(
        os.environ, {"MARKETWITNESS_SEC_USER_AGENT": "MarketWitness owner@example.com"}
    )
    @patch("marketwitness.providers.sec.urlopen")
    def test_reads_user_agent_from_environment(self, request_mock) -> None:
        request_mock.return_value.__enter__.return_value = _JsonResponse(
            {"fields": ["cik", "name", "ticker", "exchange"], "data": []}
        )

        result = fetch_company_ticker_map()

        self.assertEqual(result, [])
        request = request_mock.call_args.args[0]
        self.assertEqual(request.headers["User-agent"], "MarketWitness owner@example.com")

    @patch.dict(os.environ, {}, clear=True)
    def test_reads_user_agent_from_local_private_file(self) -> None:
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sec_user_agent.txt"
            path.write_text("MarketWitness local@example.com\n", encoding="utf-8")
            with patch("marketwitness.providers.sec.LOCAL_USER_AGENT_PATH", path):
                self.assertEqual(
                    configured_user_agent(), "MarketWitness local@example.com"
                )

    @patch("marketwitness.providers.sec.urlopen", side_effect=URLError("offline"))
    def test_network_error_becomes_provider_error(self, unused_request) -> None:
        with self.assertRaisesRegex(SecDataError, "Unable to retrieve"):
            fetch_company_ticker_map("MarketWitness contact@example.com")


if __name__ == "__main__":
    unittest.main()


class _JsonResponse:
    def __init__(self, payload) -> None:
        self.payload = payload

    def read(self) -> bytes:
        import json

        return json.dumps(self.payload).encode("utf-8")
