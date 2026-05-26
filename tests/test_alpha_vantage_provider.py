import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from marketwitness.csvio import load_prices
from marketwitness.providers.alpha_vantage import (
    AlphaVantageDataError,
    fetch_adjusted_daily,
    load_alpha_vantage_snapshot,
    parse_adjusted_daily_payload,
    render_prices_html,
    render_prices_report,
    write_prices_csv,
)


class AlphaVantageProviderTests(unittest.TestCase):
    def test_normalizes_raw_bounds_with_adjusted_close_factor(self) -> None:
        imported = load_alpha_vantage_snapshot(
            Path("data/samples/alpha-vantage-daily-adjusted.json"), "ACBK"
        )

        self.assertEqual(imported.bars[0].adjusted_high, 101)
        self.assertEqual(imported.bars[0].adjusted_low, 99)
        self.assertEqual(imported.bars[1].adjusted_high, 121)
        report = render_prices_report(imported, date(2026, 5, 24))
        page = render_prices_html(imported, date(2026, 5, 24))
        self.assertIn("adjusted_close / raw_close", report)
        self.assertIn("currently marks this daily-adjusted API as premium", page)
        self.assertIn('href="/dashboard/financials-evidence">Financials Evidence Center</a>', page)

    def test_writes_csv_accepted_by_price_loader(self) -> None:
        imported = load_alpha_vantage_snapshot(
            Path("data/samples/alpha-vantage-daily-adjusted.json"), "ACBK"
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "prices.csv"
            write_prices_csv(output, imported)
            loaded = load_prices(output)

        self.assertEqual(len(loaded["ACBK"]), 3)
        self.assertEqual(loaded["ACBK"][2].adjusted_close, 125)

    def test_rejects_unadjusted_or_missing_series(self) -> None:
        with self.assertRaisesRegex(AlphaVantageDataError, "missing TIME_SERIES_DAILY_ADJUSTED"):
            parse_adjusted_daily_payload({"Time Series (Daily)": {}}, "ACBK", "snapshot")

    def test_cache_hit_does_not_require_key_or_network(self) -> None:
        payload = json.loads(
            Path("data/samples/alpha-vantage-daily-adjusted.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as directory:
            cached = Path(directory) / "ACBK-daily-adjusted.json"
            cached.write_text(json.dumps(payload), encoding="utf-8")
            with patch("marketwitness.providers.alpha_vantage.urlopen") as request:
                imported = fetch_adjusted_daily("ACBK", cache_dir=directory)

        request.assert_not_called()
        self.assertEqual(imported.source_mode, "cache")

    def test_live_request_requires_private_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict("os.environ", {}, clear=True), patch(
                "marketwitness.providers.alpha_vantage.LOCAL_API_KEY_PATH",
                Path(directory) / "missing.txt",
            ):
                with self.assertRaisesRegex(AlphaVantageDataError, "require"):
                    fetch_adjusted_daily("ACBK", cache_dir=directory)


if __name__ == "__main__":
    unittest.main()
