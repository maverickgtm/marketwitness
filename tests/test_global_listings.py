import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.global_listings import (
    GlobalListingsDataError,
    load_global_market_sources,
    render_global_listings_html,
    render_global_listings_report,
)


class GlobalListingsTests(unittest.TestCase):
    def test_renders_global_sources_and_priority_connectors(self) -> None:
        sources = load_global_market_sources(Path("data/samples/global_market_sources.csv"))

        report = render_global_listings_report(sources, date(2026, 5, 24))
        page = render_global_listings_html(sources, date(2026, 5, 24))

        self.assertEqual(len(sources), 5)
        self.assertIn("London Stock Exchange", report)
        self.assertIn("Hong Kong Exchanges and Clearing", report)
        self.assertIn("Priority connectors: `2`", report)
        self.assertIn("Beyond Wall Street", page)
        self.assertIn("Priority connectors are not live monitors", page)

    def test_rejects_unknown_connector_status(self) -> None:
        path = _csv(
            "market_code,market_name,jurisdiction,connector_status,official_source_name,"
            "official_source_url,signal_type,confirmation_rule,implementation_next\n"
            "LSE,London,UK,live_without_adapter,LSE,https://example.invalid,L,Rule,Build\n"
        )

        with self.assertRaisesRegex(GlobalListingsDataError, "invalid status"):
            load_global_market_sources(path)


def _csv(content: str) -> Path:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "markets.csv"
    path.write_text(content, encoding="utf-8")
    _TEMP_DIRECTORIES.append(directory)
    return path


_TEMP_DIRECTORIES: list[tempfile.TemporaryDirectory] = []


if __name__ == "__main__":
    unittest.main()
