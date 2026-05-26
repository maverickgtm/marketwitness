import tempfile
import unittest
from datetime import date
from pathlib import Path

from marketwitness.providers.cftc import (
    CftcDataError,
    build_cftc_snapshot,
    load_cftc_csv,
    load_cftc_snapshots,
    write_cftc_csv,
)


class CftcProviderTests(unittest.TestCase):
    def test_normalizes_benchmark_contracts_and_calculates_net_context(self) -> None:
        records = load_cftc_snapshots(
            Path("data/samples/cftc-disaggregated-synthetic.json"),
            Path("data/samples/cftc-financial-synthetic.json"),
            date(2026, 5, 26),
        )
        wti = build_cftc_snapshot(records, "wti", weeks=1)
        usd = build_cftc_snapshot(records, "usd-index", weeks=1)

        self.assertEqual(len(records), 6)
        self.assertEqual(wti["latest"]["primary_label"], "Managed Money")
        self.assertEqual(wti["latest"]["primary_net"], 98219)
        self.assertEqual(wti["latest"]["primary_net_pct_oi"], "4.90")
        self.assertEqual(wti["comparison"]["primary_net_change"], 25418)
        self.assertEqual(usd["latest"]["primary_label"], "Leveraged Money")
        self.assertEqual(usd["latest"]["primary_net"], -11716)
        self.assertEqual(usd["comparison"]["primary_net_change"], -6965)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cftc.csv"
            write_cftc_csv(path, records)
            loaded = load_cftc_csv(path)
        self.assertEqual(loaded, records)

    def test_rejects_invalid_market_and_window(self) -> None:
        records = load_cftc_snapshots(
            Path("data/samples/cftc-disaggregated-synthetic.json"),
            Path("data/samples/cftc-financial-synthetic.json"),
            date(2026, 5, 26),
        )
        with self.assertRaisesRegex(CftcDataError, "market"):
            build_cftc_snapshot(records, "silver", weeks=1)
        with self.assertRaisesRegex(CftcDataError, "window"):
            build_cftc_snapshot(records, "wti", weeks=2)


if __name__ == "__main__":
    unittest.main()
