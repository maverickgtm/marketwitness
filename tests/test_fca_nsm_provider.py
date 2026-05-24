import unittest
from datetime import date
from pathlib import Path

from targetaudit.lse_upcoming import load_lse_page_payload
from targetaudit.providers.fca_nsm import (
    FcaNsmDataError,
    check_lse_issues,
    load_nsm_fixture,
    parse_nsm_search_payload,
    render_lse_fca_html,
    render_lse_fca_report,
)


class FcaNsmProviderTests(unittest.TestCase):
    def test_parses_nsm_document_match(self) -> None:
        documents = parse_nsm_search_payload(
            {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "company": "EXAMPLE PLC",
                                "headline": "Admission Document",
                                "type": "Prospectus",
                                "submitted_date": "2026-05-22T11:27:40Z",
                                "publication_date": "2026-05-22T11:27:40Z",
                                "disclosure_id": "abc-123",
                                "download_link": "NSM/FCA/abc-123.pdf",
                            }
                        }
                    ]
                }
            }
        )

        self.assertEqual(documents[0].headline, "Admission Document")
        self.assertIn(
            "data.fca.org.uk/artefacts/NSM/FCA/abc-123.pdf",
            documents[0].document_url,
        )

    def test_marks_document_match_and_unmatched_issuers_from_fixture(self) -> None:
        issues = load_lse_page_payload(
            Path("data/samples/lse-new-issues-page.json"), date(2026, 5, 24)
        )
        lookup = load_nsm_fixture(Path("data/samples/fca-nsm-results.json"))

        checks = check_lse_issues(issues, lookup)
        report = render_lse_fca_report(checks, date(2026, 5, 24))
        page = render_lse_fca_html(checks, date(2026, 5, 24))

        self.assertEqual(len(checks), 3)
        self.assertEqual(checks[0].status, "document_found_review_required")
        self.assertEqual(checks[1].status, "no_document_found")
        self.assertIn("FCA NSM Corroboration Monitor", report)
        self.assertIn("Announcement of Intention to Float on AIM", report)
        self.assertIn("NSM evidence is not real-time", page)

    def test_rejects_nsm_document_missing_identity(self) -> None:
        with self.assertRaisesRegex(FcaNsmDataError, "missing identity"):
            parse_nsm_search_payload(
                {"hits": {"hits": [{"_source": {"submitted_date": "2026-05-22T00:00:00Z"}}]}}
            )


if __name__ == "__main__":
    unittest.main()
