import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.ipo_watch import (
    IpoWatchDataError,
    load_ipo_watch,
    render_ipo_watch_html,
    render_ipo_watch_report,
)


class IpoWatchTests(unittest.TestCase):
    def test_report_distinguishes_filed_listed_and_unverified_candidates(self) -> None:
        items = load_ipo_watch(Path("data/samples/ipo_watch.csv"))

        report = render_ipo_watch_report(items, date(2026, 5, 24))

        self.assertIn("| SpaceX | Space and AI infrastructure | `filed_public`", report)
        self.assertIn("| Cerebras Systems | AI hardware | `listed`", report)
        self.assertIn("| Anthropic | Foundation models | `candidate_unverified`", report)
        self.assertIn("not produce buy, sell or position-size instructions", report)

    def test_html_dashboard_renders_cards_and_source_link(self) -> None:
        items = load_ipo_watch(Path("data/samples/ipo_watch.csv"))

        page = render_ipo_watch_html(items, date(2026, 5, 24))

        self.assertIn("Upcoming listings", page)
        self.assertIn("SpaceX", page)
        self.assertIn("Research dashboard only", page)
        self.assertIn('href="/dashboard/ipo">IPO Watch Center</a>', page)
        self.assertIn('href="/dashboard/sec-alerts"', page)
        self.assertIn('href="/dashboard/ipo-reviews"', page)
        self.assertIn("https://www.sec.gov/Archives/edgar/data/1181412", page)

    def test_loads_optional_cik_for_sec_matching(self) -> None:
        items = load_ipo_watch(Path("data/samples/ipo_watch.csv"))

        self.assertEqual(items[0].cik, "0001181412")

    def test_listed_company_requires_ticker_and_exchange(self) -> None:
        path = _csv(
            "company_name,theme,status,status_date,ticker,exchange,filing_type,"
            "evidence_level,source_title,source_url,next_event,risk_flags\n"
            "Missing Symbol,AI hardware,listed,2026-05-14,,,IPO,Issuer,"
            "Release,https://example.invalid/release,Filings,Volatility\n"
        )

        with self.assertRaisesRegex(IpoWatchDataError, "requires ticker and exchange"):
            load_ipo_watch(path)

    def test_unknown_status_is_rejected(self) -> None:
        path = _csv(
            "company_name,theme,status,status_date,ticker,exchange,filing_type,"
            "evidence_level,source_title,source_url,next_event,risk_flags\n"
            "Rumor Corp,AI,definitely_soon,2026-05-24,,,none,Candidate,"
            "Mention,https://example.invalid/source,Wait,Rumor\n"
        )

        with self.assertRaisesRegex(IpoWatchDataError, "invalid status"):
            load_ipo_watch(path)

    def test_report_rejects_status_after_as_of_date(self) -> None:
        items = load_ipo_watch(Path("data/samples/ipo_watch.csv"))

        with self.assertRaisesRegex(IpoWatchDataError, "predates status evidence"):
            render_ipo_watch_report(items, date(2026, 5, 19))


def _csv(content: str) -> Path:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "ipo.csv"
    path.write_text(content, encoding="utf-8")
    _TEMP_DIRECTORIES.append(directory)
    return path


_TEMP_DIRECTORIES: list[tempfile.TemporaryDirectory] = []


if __name__ == "__main__":
    unittest.main()
