import unittest
from datetime import date
from pathlib import Path

from targetaudit.policy_signal_lab import build_policy_signal_lab_snapshot
from targetaudit.source_registry import SourceRegistryDataError, load_source_registry


class PolicySignalLabTests(unittest.TestCase):
    def test_exposes_a_terms_controlled_presidential_communication_study(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        snapshot = build_policy_signal_lab_snapshot(providers, date(2026, 5, 25))

        self.assertEqual(snapshot["coverage_start"], "2025-01-20")
        self.assertEqual(snapshot["proposed_measure"], "Policy Signal Impact Trace")
        self.assertIn("disabled_pending_written_permission", snapshot["live_feed_status"])
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

    def test_rejects_missing_communication_source_control(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        with self.assertRaisesRegex(SourceRegistryDataError, "truth-social-public-content"):
            build_policy_signal_lab_snapshot(
                [item for item in providers if item.provider_id != "truth-social-public-content"],
                date(2026, 5, 25),
            )


if __name__ == "__main__":
    unittest.main()
