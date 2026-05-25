import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.issuer_confirmations import (
    IssuerConfirmationDataError,
    load_issuer_confirmations,
    render_issuer_confirmations_html,
    render_issuer_confirmations_report,
)


class IssuerConfirmationTests(unittest.TestCase):
    def test_renders_official_issuer_confirmation_milestones(self) -> None:
        events = load_issuer_confirmations(
            Path("data/samples/issuer_listing_confirmations.csv")
        )

        report = render_issuer_confirmations_report(events, date(2026, 5, 24))
        page = render_issuer_confirmations_html(events, date(2026, 5, 24))

        self.assertEqual(len(events), 2)
        self.assertIn("Cerebras Systems", report)
        self.assertIn("`trading_started`", report)
        self.assertIn("`offering_closed`", report)
        self.assertIn("Issuer release", page)
        self.assertIn("not an investment recommendation", page)
        self.assertIn('href="/dashboard/ipo">IPO Watch Center</a>', page)
        self.assertIn('href="/dashboard/global-listings">Global Listings Watch</a>', page)

    def test_rejects_confirmation_without_market_or_ticker(self) -> None:
        path = _csv(
            "company_name,market,ticker,event_type,event_date,source_title,source_url,"
            "verified_on,evidence_level,research_note\n"
            "Issuer,,SYM,trading_started,2026-05-14,Official,"
            "https://issuer.example/release,2026-05-15,issuer_official_release,Reviewed\n"
        )

        with self.assertRaisesRegex(IssuerConfirmationDataError, "missing evidence"):
            load_issuer_confirmations(path)

    def test_rejects_future_evidence_at_report_cutoff(self) -> None:
        events = load_issuer_confirmations(
            Path("data/samples/issuer_listing_confirmations.csv")
        )

        with self.assertRaisesRegex(IssuerConfirmationDataError, "after the report cutoff"):
            render_issuer_confirmations_report(events, date(2026, 5, 14))


def _csv(content: str) -> Path:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "issuer-confirmations.csv"
    path.write_text(content, encoding="utf-8")
    _TEMP_DIRECTORIES.append(directory)
    return path


_TEMP_DIRECTORIES: list[tempfile.TemporaryDirectory] = []


if __name__ == "__main__":
    unittest.main()
