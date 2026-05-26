import tempfile
import unittest
from datetime import date
from pathlib import Path

from marketwitness.providers.treasury import (
    TreasuryDataError,
    load_treasury_csv,
    load_treasury_snapshot,
    write_treasury_csv,
)


class TreasuryProviderTests(unittest.TestCase):
    def test_loads_official_shaped_yield_curve_and_calculates_spread(self) -> None:
        records = load_treasury_snapshot(
            Path("data/samples/treasury-yields-synthetic.xml"), date(2026, 5, 25)
        )

        self.assertEqual(len(records), 3)
        self.assertEqual(str(records[1].two_year_pct), "3.92")
        self.assertEqual(str(records[1].ten_year_pct), "4.47")
        self.assertEqual(str(records[1].curve_2s10s_bps), "55.00")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "treasury.csv"
            write_treasury_csv(output, records)
            loaded = load_treasury_csv(output)
        self.assertEqual(loaded, records)

    def test_rejects_rate_after_cutoff(self) -> None:
        with self.assertRaisesRegex(TreasuryDataError, "after observation date"):
            load_treasury_snapshot(
                Path("data/samples/treasury-yields-synthetic.xml"), date(2026, 5, 22)
            )


if __name__ == "__main__":
    unittest.main()
