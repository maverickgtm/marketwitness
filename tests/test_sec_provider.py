import unittest

from targetaudit.providers.sec import SecDataError, parse_company_ticker_payload


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


if __name__ == "__main__":
    unittest.main()
