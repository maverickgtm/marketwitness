import unittest
from datetime import date
from pathlib import Path

from marketwitness.policy_signal_lab import build_policy_signal_lab_snapshot
from marketwitness.source_registry import SourceRegistryDataError, load_source_registry


class PolicySignalLabTests(unittest.TestCase):
    def test_exposes_a_terms_controlled_presidential_communication_study(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        snapshot = build_policy_signal_lab_snapshot(providers, date(2026, 5, 25))

        self.assertEqual(snapshot["product"], "Presidential Impact Lab")
        self.assertEqual(snapshot["coverage_start"], "2025-01-20")
        self.assertEqual(snapshot["proposed_measure"], "Policy Signal Impact Trace")
        self.assertIn("disabled_pending_written_permission", snapshot["live_feed_status"])
        self.assertEqual(snapshot["official_intake_status"], "implemented_optional_artifact")
        self.assertIn("prohibit automated access", snapshot["publication_boundary"])
        self.assertEqual(len(snapshot["event_windows"]), 5)
        self.assertEqual(len(snapshot["asset_lenses"]), 4)
        self.assertIn("JPMorgan Volfefe Index", {item["name"] for item in snapshot["prior_art"]})
        truth = next(
            item
            for item in snapshot["source_controls"]
            if item["provider_id"] == "truth-social-public-content"
        )
        self.assertEqual(truth["deployment_state"], "blocked")
        whitehouse = next(
            item
            for item in snapshot["source_controls"]
            if item["provider_id"] == "whitehouse-official-news-rss"
        )
        self.assertEqual(whitehouse["deployment_state"], "usable_with_policy")
        self.assertEqual(whitehouse["integration_status"], "implemented")
        presidential_actions = next(
            item
            for item in snapshot["source_controls"]
            if item["provider_id"] == "whitehouse-presidential-actions-rss"
        )
        self.assertEqual(presidential_actions["deployment_state"], "usable_with_policy")
        self.assertEqual(presidential_actions["integration_status"], "implemented")
        channels = {item["name"]: item for item in snapshot["approved_intake_candidates"]}
        self.assertEqual(
            channels["White House News RSS"]["page_url"],
            "https://www.whitehouse.gov/news/",
        )
        self.assertEqual(
            channels["Presidential Actions RSS"]["page_url"],
            "https://www.whitehouse.gov/presidential-actions/",
        )
        self.assertEqual(
            channels["White House Wire RSS"]["page_url"],
            "https://www.whitehouse.gov/wire/",
        )
        self.assertEqual(
            channels["White House Wire RSS"]["url"],
            "https://www.whitehouse.gov/wire/feed/",
        )
        self.assertEqual(
            {item["state"] for item in snapshot["approved_intake_candidates"]},
            {"eligible", "metadata_only", "blocked_without_permission"},
        )

    def test_rejects_missing_communication_source_control(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        with self.assertRaisesRegex(SourceRegistryDataError, "truth-social-public-content"):
            build_policy_signal_lab_snapshot(
                [item for item in providers if item.provider_id != "truth-social-public-content"],
                date(2026, 5, 25),
            )


if __name__ == "__main__":
    unittest.main()
