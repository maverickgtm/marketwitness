import unittest
from datetime import date
from pathlib import Path

from targetaudit.public_policy import build_public_use_policy
from targetaudit.source_registry import SourceRegistryDataError, load_source_registry


class PublicUsePolicyTests(unittest.TestCase):
    def test_exposes_research_boundary_and_blocked_sources(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        policy = build_public_use_policy(providers, date(2026, 5, 25))

        self.assertEqual(policy["review_status"], "pending_external_legal_review")
        self.assertEqual(policy["tracked_source_count"], 35)
        self.assertEqual(policy["blocked_source_count"], 5)
        self.assertIn("not investment advice", policy["headline"].lower())
        self.assertEqual(
            {item["provider_id"] for item in policy["blocked_sources"]},
            {
                "tipranks-reference",
                "mas-opera-reference",
                "xstocks-backing-api",
                "bybit-xstocks-v5",
                "kraken-xstocks",
            },
        )
        self.assertIn(
            "Do not automatically collect",
            " ".join(policy["publication_rules"]),
        )
        external = next(
            item for item in policy["data_layers"] if item["status"] == "external_display_only"
        )
        self.assertIn("does not store or score", external["description"])

    def test_rejects_sources_reviewed_after_policy_cutoff(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        with self.assertRaisesRegex(SourceRegistryDataError, "policy cutoff"):
            build_public_use_policy(providers, date(2026, 5, 24))


if __name__ == "__main__":
    unittest.main()
