import tempfile
import unittest
from datetime import date
from pathlib import Path

from marketwitness.lse_upcoming import load_lse_page_payload
from marketwitness.providers.fca_nsm import (
    FcaNsmDataError,
    check_lse_issues,
    load_nsm_fixture,
    parse_nsm_search_payload,
    render_lse_fca_html,
    render_lse_fca_report,
    write_lse_fca_csv,
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
        self.assertEqual(checks[0].evidence_class, "intention_to_float_notice")
        self.assertEqual(checks[1].evidence_class, "no_document_found")
        self.assertEqual(checks[2].evidence_class, "no_document_found")
        self.assertIn("FCA NSM Corroboration Monitor", report)
        self.assertIn("Announcement of Intention to Float on AIM", report)
        self.assertIn("Intention-to-float notices: `1`", report)
        self.assertIn("NSM evidence is not real-time", page)
        self.assertIn("intention_to_float_notice", page)
        self.assertIn('href="/dashboard/global-listings">Global Listings Watch</a>', page)

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "checks.csv"
            write_lse_fca_csv(output, checks)
            csv_text = output.read_text(encoding="utf-8")

        self.assertIn("evidence_class", csv_text)
        self.assertIn("FCA document type contains Intention to Float.", csv_text)

    def test_classifies_prospectus_and_admission_document_signals(self) -> None:
        documents = parse_nsm_search_payload(
            {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "company": "EXAMPLE PROSPECTUS PLC",
                                "headline": "Prospectus Published",
                                "type": "Prospectus",
                                "submitted_date": "2026-05-22T11:27:40Z",
                                "disclosure_id": "sample-prospectus",
                            }
                        },
                        {
                            "_source": {
                                "company": "EXAMPLE ADMISSION PLC",
                                "headline": "Admission Document",
                                "type": "Admission Document - AIM",
                                "submitted_date": "2026-05-22T11:27:40Z",
                                "disclosure_id": "sample-admission",
                            }
                        },
                    ]
                }
            }
        )

        self.assertEqual(documents[0].evidence_class, "prospectus_document_signal")
        self.assertEqual(documents[1].evidence_class, "admission_document_signal")

    def test_classifies_unidentified_document_for_review(self) -> None:
        documents = parse_nsm_search_payload(
            {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "company": "EXAMPLE PLC",
                                "headline": "Results of General Meeting",
                                "type": "Company announcement",
                                "submitted_date": "2026-05-22T11:27:40Z",
                                "publication_date": "2026-05-22T11:27:40Z",
                                "disclosure_id": "abc-124",
                            }
                        }
                    ]
                }
            }
        )

        self.assertEqual(documents[0].evidence_class, "other_document_review")

    def test_headline_alone_does_not_create_prospectus_signal(self) -> None:
        documents = parse_nsm_search_payload(
            {
                "hits": {
                    "hits": [
                        {
                            "_source": {
                                "company": "EXAMPLE PLC",
                                "headline": "No Prospectus Required",
                                "type": "Company announcement",
                                "submitted_date": "2026-05-22T11:27:40Z",
                                "disclosure_id": "abc-125",
                            }
                        }
                    ]
                }
            }
        )

        self.assertEqual(documents[0].evidence_class, "other_document_review")

    def test_rejects_nsm_document_missing_identity(self) -> None:
        with self.assertRaisesRegex(FcaNsmDataError, "missing identity"):
            parse_nsm_search_payload(
                {"hits": {"hits": [{"_source": {"submitted_date": "2026-05-22T00:00:00Z"}}]}}
            )


if __name__ == "__main__":
    unittest.main()
