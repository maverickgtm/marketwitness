import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.ipo_reviews import (
    IpoReviewDataError,
    apply_review_decisions,
    load_alert_evidence,
    load_review_decisions,
    render_review_html,
    render_review_report,
)
from targetaudit.ipo_watch import load_ipo_watch
from targetaudit.sec_alerts import (
    build_filing_alerts,
    known_source_urls,
    load_discovered_filings,
    write_sec_alerts_csv,
)


class IpoReviewTests(unittest.TestCase):
    def test_promotes_new_issuer_only_after_documented_matching_decision(self) -> None:
        alerts = _alerts()
        decisions = load_review_decisions(
            _csv(
                "source_url,cik,decision,display_name,theme,reviewed_on,evidence_level,"
                "source_title,next_event,risk_flags,review_note\n"
                "https://www.sec.gov/Archives/edgar/data/6666666/000000000026000003/"
                "example-spac-s1.htm,0006666666,confirm_filed_public,Example Acquisition,"
                "SPAC candidate,2026-05-20,Reviewed SEC filing,Reviewed S-1,"
                "Review amendments,Blank-check structure requires study,"
                "Document manually reviewed as a public registration.\n"
            )
        )

        reviewed, outcomes = apply_review_decisions(
            load_ipo_watch("data/samples/ipo_watch.csv"),
            alerts,
            decisions,
            date(2026, 5, 20),
        )
        promoted = next(item for item in reviewed if item.company_name == "Example Acquisition")

        self.assertEqual(promoted.status, "filed_public")
        self.assertEqual(promoted.cik, "0006666666")
        self.assertEqual(outcomes[0].result, "promoted")
        self.assertIn("Status promotions: `1`", render_review_report(outcomes, reviewed, date(2026, 5, 20)))
        page = render_review_html(outcomes, reviewed, date(2026, 5, 20))
        self.assertIn("Controlled updates", page)
        self.assertIn('href="/dashboard/ipo">IPO Watch Center</a>', page)

    def test_records_non_promotion_decision_without_changing_registry(self) -> None:
        decisions = load_review_decisions(
            _csv(
                "source_url,cik,decision,display_name,theme,reviewed_on,evidence_level,"
                "source_title,next_event,risk_flags,review_note\n"
                "https://www.sec.gov/Archives/edgar/data/6666666/000000000026000003/"
                "example-spac-s1.htm,0006666666,retain_for_review,Example Acquisition,"
                "SPAC candidate,2026-05-20,,,,,Name signal alone is insufficient.\n"
            )
        )
        registry = load_ipo_watch("data/samples/ipo_watch.csv")

        reviewed, outcomes = apply_review_decisions(
            registry, _alerts(), decisions, date(2026, 5, 20)
        )

        self.assertEqual(reviewed, registry)
        self.assertEqual(outcomes[0].result, "recorded_no_status_change")

    def test_rejects_decision_without_matching_sec_alert(self) -> None:
        decisions = load_review_decisions(Path("data/samples/sec-review-decisions.csv"))

        with self.assertRaisesRegex(IpoReviewDataError, "does not match"):
            apply_review_decisions(
                load_ipo_watch("data/samples/ipo_watch.csv"),
                [],
                decisions,
                date(2026, 5, 20),
            )

    def test_rejects_review_dated_before_sec_filing(self) -> None:
        decisions = load_review_decisions(
            _csv(
                "source_url,cik,decision,display_name,theme,reviewed_on,evidence_level,"
                "source_title,next_event,risk_flags,review_note\n"
                "https://www.sec.gov/Archives/edgar/data/6666666/000000000026000003/"
                "example-spac-s1.htm,0006666666,retain_for_review,Example Acquisition,"
                "SPAC candidate,2026-05-19,,,,,Impossible review date.\n"
            )
        )

        with self.assertRaisesRegex(IpoReviewDataError, "predate"):
            apply_review_decisions(
                load_ipo_watch("data/samples/ipo_watch.csv"),
                _alerts(),
                decisions,
                date(2026, 5, 20),
            )


def _alerts():
    filings = load_discovered_filings(Path("data/samples/sec-ipo-discovery.csv"))
    watchlist = load_ipo_watch(Path("data/samples/ipo_watch.csv"))
    seen = known_source_urls(Path("data/samples/sec-alerts-history"), date(2026, 5, 20))
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "alerts.csv"
        write_sec_alerts_csv(path, build_filing_alerts(filings, watchlist, seen))
        return load_alert_evidence(path)


def _csv(content: str) -> Path:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "decisions.csv"
    path.write_text(content, encoding="utf-8")
    _TEMP_DIRECTORIES.append(directory)
    return path


_TEMP_DIRECTORIES: list[tempfile.TemporaryDirectory] = []


if __name__ == "__main__":
    unittest.main()
