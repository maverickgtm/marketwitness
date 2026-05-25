import unittest
from datetime import date
from pathlib import Path

from targetaudit.scorecard_readiness import (
    build_scorecard_readiness,
    render_readiness_html,
    render_readiness_report,
)
from targetaudit.source_registry import SourceProvider, load_source_registry


class ScorecardReadinessTests(unittest.TestCase):
    def test_blocks_public_release_until_production_sources_are_approved(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        snapshot = build_scorecard_readiness(providers, date(2026, 5, 24))

        self.assertFalse(snapshot["public_release_ready"])
        self.assertFalse(snapshot["internal_research_ready"])
        self.assertEqual(snapshot["public_ready_count"], 0)
        self.assertEqual(snapshot["internal_only_count"], 1)
        self.assertEqual(snapshot["integration_pending_count"], 2)
        targets = snapshot["requirements"][0]
        self.assertEqual(targets["status"], "integration_pending")
        fixture = next(
            provider for provider in targets["providers"] if provider["provider_id"] == "authorized-demo"
        )
        self.assertFalse(fixture["production_eligible"])

        report = render_readiness_report(snapshot)
        page = render_readiness_html(snapshot)
        self.assertIn("Public release ready: `false`", report)
        self.assertIn("demo only", report)
        self.assertIn("Earn the right", page)

    def test_approves_release_only_with_public_ready_production_controls(self) -> None:
        providers = [
            _public_provider("targets", "Analyst targets"),
            _public_provider("prices", "Adjusted price bars"),
            _public_provider("actions", "Corporate actions"),
        ]

        snapshot = build_scorecard_readiness(providers, date(2026, 5, 24))

        self.assertTrue(snapshot["public_release_ready"])
        self.assertTrue(snapshot["internal_research_ready"])
        self.assertEqual(snapshot["public_ready_count"], 3)
        self.assertFalse(snapshot["blockers"])


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
        review_note="Approved policy fixture.",
    )


if __name__ == "__main__":
    unittest.main()
