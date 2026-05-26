import tempfile
import unittest
from pathlib import Path

from marketwitness.csvio import DataFormatError, load_prices, load_targets


class CsvIoTests(unittest.TestCase):
    def test_non_finite_target_is_loaded_as_invalid_for_audited_exclusion(self) -> None:
        path = _csv(
            "observation_id,ticker,company_name,firm,published_date,price_target,source_provider,source_url\n"
            "one,AAA,AAA Bank,Research Firm,2023-01-02,NaN,source,https://example.invalid/one\n"
        )

        targets = load_targets(path)

        self.assertIsNone(targets[0].price_target)

    def test_duplicate_price_date_is_rejected(self) -> None:
        path = _csv(
            "ticker,date,adjusted_high,adjusted_low,adjusted_close,source_provider\n"
            "AAA,2023-01-03,11,9,10,source\n"
            "AAA,2023-01-03,12,10,11,source\n"
        )

        with self.assertRaisesRegex(DataFormatError, "duplicate ticker/date"):
            load_prices(path)

    def test_price_close_outside_range_is_rejected(self) -> None:
        path = _csv(
            "ticker,date,adjusted_high,adjusted_low,adjusted_close,source_provider\n"
            "AAA,2023-01-03,11,9,12,source\n"
        )

        with self.assertRaisesRegex(DataFormatError, "outside low/high"):
            load_prices(path)


def _csv(content: str) -> Path:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "test.csv"
    path.write_text(content, encoding="utf-8")
    _TEMP_DIRECTORIES.append(directory)
    return path


_TEMP_DIRECTORIES: list[tempfile.TemporaryDirectory] = []


if __name__ == "__main__":
    unittest.main()
