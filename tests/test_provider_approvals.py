import unittest
from datetime import date
from pathlib import Path

from targetaudit.provider_approvals import (
    ProviderApprovalDataError,
    ProviderApprovalRecord,
    build_approval_queue,
    load_provider_approvals,
    render_approval_html,
    render_approval_report,
)
from targetaudit.source_registry import SourceProvider, load_source_registry


class ProviderApprovalTests(unittest.TestCase):
    def test_tracks_open_approvals_without_enabling_public_activation(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))
        approvals = load_provider_approvals(Path("data/samples/provider_approval_queue.csv"))

        snapshot = build_approval_queue(providers, approvals, date(2026, 5, 25))

        self.assertEqual(snapshot["queue_count"], 7)
        self.assertEqual(snapshot["critical_open_count"], 4)
        self.assertEqual(snapshot["approved_count"], 0)
        self.assertFalse(snapshot["public_activation_ready"])
        self.assertTrue(
            all(control["status"] == "pending_approval" for control in snapshot["controls"])
        )
        self.assertIn("Benzinga Analyst Ratings API via Massive", render_approval_report(snapshot))
        self.assertIn("Finnhub Enterprise Redistribution", render_approval_report(snapshot))
        self.assertIn("Permission before", render_approval_html(snapshot))

    def test_approves_activation_only_when_governance_and_dossiers_both_pass(self) -> None:
        providers = [
            _public_provider("targets", "Analyst targets"),
            _public_provider("prices", "Adjusted price bars"),
            _public_provider("actions", "Corporate actions"),
            _public_provider("universe", "Historical universe membership"),
        ]
        approvals = [_approved(provider.provider_id) for provider in providers]

        snapshot = build_approval_queue(providers, approvals, date(2026, 5, 24))

        self.assertTrue(snapshot["public_activation_ready"])
        self.assertEqual(snapshot["approved_count"], 4)
        self.assertEqual(snapshot["critical_open_count"], 0)

    def test_rejects_an_approval_that_conflicts_with_source_governance(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        with self.assertRaisesRegex(ProviderApprovalDataError, "conflicts"):
            build_approval_queue(
                providers,
                [_approved("alpha-vantage-prices")],
                date(2026, 5, 25),
            )

    def test_rejects_public_permission_for_a_source_without_verified_integration(self) -> None:
        providers = [
            SourceProvider(
                provider_id="candidate",
                provider_name="Candidate",
                data_class="Analyst targets",
                access_model="commercial_api_candidate",
                integration_status="candidate",
                license_status="public_access_rules_documented",
                publication_policy="source_link_and_derived_output",
                official_url="https://example.invalid/source",
                reference_url="https://example.invalid/terms",
                reviewed_on=date(2026, 5, 24),
                review_note="Rights approved but connector remains pending.",
            )
        ]

        with self.assertRaisesRegex(ProviderApprovalDataError, "integration state"):
            build_approval_queue(providers, [_approved("candidate")], date(2026, 5, 24))

    def test_rejects_demo_providers_from_production_approval_queue(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        with self.assertRaisesRegex(ProviderApprovalDataError, "Demo-only"):
            build_approval_queue(
                providers,
                [_approved("synthetic-demo")],
                date(2026, 5, 25),
            )


def _approved(provider_id: str) -> ProviderApprovalRecord:
    return ProviderApprovalRecord(
        provider_id=provider_id,
        approval_status="approved_public_output",
        priority="critical",
        requested_use="Public scorecard derived results.",
        required_evidence="Documented right to publish derived results.",
        promotion_criteria="Governance record accepts public output.",
        evidence_url="https://example.invalid/permission",
        reviewed_on=date(2026, 5, 24),
        review_note="Approved fixture.",
    )


def _public_provider(provider_id: str, data_class: str) -> SourceProvider:
    return SourceProvider(
        provider_id=provider_id,
        provider_name=provider_id.title(),
        data_class=data_class,
        access_model="public_endpoint",
        integration_status="implemented",
        license_status="public_access_rules_documented",
        publication_policy="source_link_and_derived_output",
        official_url="https://example.invalid/source",
        reference_url="https://example.invalid/terms",
        reviewed_on=date(2026, 5, 24),
        review_note="Approved fixture.",
    )


if __name__ == "__main__":
    unittest.main()
