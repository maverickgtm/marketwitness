import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.provider_approval_reviews import (
    ProviderApprovalDecision,
    ProviderApprovalReviewDataError,
    apply_provider_approval_decisions,
    load_provider_approval_decisions,
    render_provider_review_html,
    render_provider_review_report,
)
from targetaudit.provider_approvals import build_approval_queue, load_provider_approvals
from targetaudit.source_registry import load_source_registry


class ProviderApprovalReviewTests(unittest.TestCase):
    def test_records_pending_review_without_promoting_source(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))
        approvals = load_provider_approvals(Path("data/samples/provider_approval_queue.csv"))
        decisions = load_provider_approval_decisions(
            Path("data/samples/provider_approval_decisions.csv")
        )

        reviewed_providers, reviewed_approvals, outcomes = apply_provider_approval_decisions(
            providers, approvals, decisions, date(2026, 5, 24)
        )
        alpha = next(item for item in reviewed_approvals if item.provider_id == "alpha-vantage-prices")

        self.assertEqual(outcomes[0].result, "pending_recorded")
        self.assertEqual(alpha.approval_status, "pending_written_permission")
        self.assertEqual(reviewed_providers, providers)
        self.assertIn("Pending reviews recorded: `1`", render_provider_review_report(outcomes, date(2026, 5, 24)))
        self.assertIn("Evidence in.", render_provider_review_html(outcomes, date(2026, 5, 24)))

    def test_approved_decision_generates_coherent_public_source_and_dossier(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))
        approvals = load_provider_approvals(Path("data/samples/provider_approval_queue.csv"))
        decision = ProviderApprovalDecision(
            provider_id="alpha-vantage-prices",
            decision="approve_public_output",
            reviewed_on=date(2026, 5, 24),
            evidence_url="https://example.invalid/approved-license",
            evidence_summary="Signed permission permits public derived scorecard outputs.",
            new_integration_status="implemented",
            review_note="Written permission reviewed and adapter verified.",
        )

        reviewed_providers, reviewed_approvals, outcomes = apply_provider_approval_decisions(
            providers, approvals, [decision], date(2026, 5, 24)
        )
        alpha = next(
            item for item in reviewed_providers if item.provider_id == "alpha-vantage-prices"
        )
        queue = build_approval_queue(reviewed_providers, reviewed_approvals, date(2026, 5, 24))
        price_control = next(
            item for item in queue["controls"] if item["data_class"] == "Adjusted price bars"
        )

        self.assertEqual(alpha.deployment_state, "usable_with_policy")
        self.assertEqual(outcomes[0].result, "promoted_public_output")
        self.assertEqual(price_control["status"], "approved")
        self.assertFalse(queue["public_activation_ready"])

    def test_loader_rejects_approval_without_verified_integration(self) -> None:
        path = _csv(
            "provider_id,decision,reviewed_on,evidence_url,evidence_summary,"
            "new_integration_status,review_note\n"
            "benzinga-targets,approve_public_output,2026-05-24,"
            "https://example.invalid/permission,Signed permission,,Review note.\n"
        )

        with self.assertRaisesRegex(ProviderApprovalReviewDataError, "verified integration"):
            load_provider_approval_decisions(path)

    def test_rejects_decision_for_provider_outside_approval_queue(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))
        approvals = load_provider_approvals(Path("data/samples/provider_approval_queue.csv"))
        decision = ProviderApprovalDecision(
            provider_id="sec-edgar",
            decision="retain_pending",
            reviewed_on=date(2026, 5, 24),
            evidence_url="https://www.sec.gov/",
            evidence_summary="Source not queued for this decision workflow.",
            new_integration_status="",
            review_note="No dossier exists.",
        )

        with self.assertRaisesRegex(ProviderApprovalReviewDataError, "without one approval"):
            apply_provider_approval_decisions(providers, approvals, [decision], date(2026, 5, 24))


def _csv(content: str) -> Path:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "decisions.csv"
    path.write_text(content, encoding="utf-8")
    _TEMP_DIRECTORIES.append(directory)
    return path


_TEMP_DIRECTORIES: list[tempfile.TemporaryDirectory] = []


if __name__ == "__main__":
    unittest.main()
