import tempfile
import unittest
from pathlib import Path

from marketwitness.historical_universe import (
    HistoricalUniverseDataError,
    load_historical_universe,
)


class HistoricalUniverseTests(unittest.TestCase):
    def test_loads_point_in_time_membership_fixture(self) -> None:
        memberships = load_historical_universe(Path("data/samples/historical_universe.csv"))

        self.assertEqual(len(memberships), 3)
        self.assertEqual(memberships[0].universe_id, "us-financials-demo")
        self.assertEqual(memberships[0].sector, "Financials")

    def test_rejects_overlapping_windows_for_same_ticker(self) -> None:
        path = _csv(
            "universe_id,ticker,company_name,sector,member_from,member_to,"
            "source_provider,source_url,verified_on\n"
            "demo,AAA,AAA Bank,Financials,2020-01-01,2023-06-30,synthetic,"
            "https://example.invalid/one,2023-01-01\n"
            "demo,AAA,AAA Bank,Financials,2023-01-01,,synthetic,"
            "https://example.invalid/two,2023-01-01\n"
        )

        with self.assertRaisesRegex(HistoricalUniverseDataError, "overlapping"):
            load_historical_universe(path)

def _csv(content: str) -> Path:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "historical-universe.csv"
    path.write_text(content, encoding="utf-8")
    _TEMP_DIRECTORIES.append(directory)
    return path


_TEMP_DIRECTORIES: list[tempfile.TemporaryDirectory] = []


if __name__ == "__main__":
    unittest.main()
