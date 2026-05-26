import unittest
from datetime import date

from marketwitness.policy_reaction import build_policy_reaction_snapshot
from marketwitness.source_registry import SourceRegistryDataError


class PolicyReactionTests(unittest.TestCase):
    def test_exposes_calculated_authored_paths_with_explicit_boundary(self) -> None:
        snapshot = build_policy_reaction_snapshot(date(2026, 5, 25))

        self.assertEqual(snapshot["product"], "Communication Reaction Sandbox")
        self.assertEqual(snapshot["mode"], "project_authored_not_market_observations")
        self.assertEqual(snapshot["episode_count"], 6)
        self.assertEqual(len(snapshot["results"]), 5)
        self.assertIn("Official White House events are not assigned", snapshot["boundary"])
        five_session = next(
            result for result in snapshot["results"] if result["window_key"] == "5_sessions"
        )
        equities = next(
            result for result in five_session["lens_results"] if result["lens"] == "Equity beta"
        )
        self.assertEqual(equities["median_move_pct"], 0.15)
        self.assertEqual(equities["positive_frequency_pct"], 50)

    def test_filters_by_theme_and_calendar_window(self) -> None:
        snapshot = build_policy_reaction_snapshot(
            date(2026, 5, 25),
            "financial_regulation",
            date(2025, 1, 20),
            date(2026, 5, 25),
        )

        self.assertEqual(snapshot["episode_count"], 2)
        self.assertEqual(
            [item["date"] for item in snapshot["included_checkpoints"]],
            ["2025-09-18", "2026-03-09"],
        )
        next_session = next(
            result for result in snapshot["results"] if result["window_key"] == "next_session"
        )
        equities = next(
            result for result in next_session["lens_results"] if result["lens"] == "Equity beta"
        )
        self.assertEqual(equities["median_move_pct"], 0.8)
        self.assertEqual(equities["positive_frequency_pct"], 100)

    def test_rejects_unknown_theme_or_future_period(self) -> None:
        with self.assertRaisesRegex(SourceRegistryDataError, "Unsupported"):
            build_policy_reaction_snapshot(date(2026, 5, 25), "unknown")
        with self.assertRaisesRegex(SourceRegistryDataError, "after its review cutoff"):
            build_policy_reaction_snapshot(
                date(2026, 5, 25),
                "all",
                date(2026, 1, 1),
                date(2026, 5, 26),
            )


if __name__ == "__main__":
    unittest.main()
