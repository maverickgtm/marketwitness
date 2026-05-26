import unittest
from datetime import date
from pathlib import Path

from marketwitness.source_registry import SourceRegistryDataError, load_source_registry
from marketwitness.volatility_lab import build_volatility_lab_snapshot


class VolatilityLabTests(unittest.TestCase):
    def test_maps_stress_families_without_claiming_real_episode_results(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        snapshot = build_volatility_lab_snapshot(providers, date(2026, 5, 25))

        self.assertEqual(snapshot["product"], "VIX Reaction Explorer")
        self.assertEqual(snapshot["indicator_group_count"], 7)
        self.assertEqual(snapshot["episode_design_count"], 4)
        self.assertEqual(
            snapshot["phase_1"], ["VIX", "VIX1D / VIX9D / VIX3M", "VXN", "MOVE"]
        )
        self.assertIn("does not ingest Cboe or ICE", snapshot["publication_boundary"])
        explorer = snapshot["reaction_explorer"]
        self.assertEqual(
            [item["key"] for item in explorer["scenarios"]],
            ["vix_rises", "vix_cools"],
        )
        self.assertEqual(explorer["horizons"][2]["key"], "5_sessions")
        self.assertIn("Real observed returns", explorer["boundary"])
        rise = explorer["scenarios"][0]
        self.assertIn("BTC / ETH", {item["assets"] for item in rise["lenses"]})
        validation = explorer["validation_sample"]
        self.assertEqual(validation["mode"], "project_authored_not_market_observations")
        self.assertEqual(validation["episode_count"], 6)
        self.assertEqual(validation["result_count"], 10)
        self.assertEqual(validation["period"]["start"], "2025-01-20")
        self.assertEqual(validation["period"]["end"], "2026-05-25")
        self.assertEqual(len(validation["period"]["episode_dates"]), 6)
        self.assertEqual(
            [item["key"] for item in validation["period"]["presets"]],
            ["full", "year_2025", "year_2026_ytd", "trailing_180"],
        )
        rises_five = next(
            result
            for result in validation["results"]
            if result["scenario_key"] == "vix_rises"
            and result["horizon_key"] == "5_sessions"
        )
        cools_twenty = next(
            result
            for result in validation["results"]
            if result["scenario_key"] == "vix_cools"
            and result["horizon_key"] == "20_sessions"
        )
        rise_equities = next(
            item for item in rises_five["lens_results"] if item["family"] == "Equities"
        )
        cool_equities = next(
            item for item in cools_twenty["lens_results"] if item["family"] == "Equities"
        )
        self.assertEqual(rise_equities["median_return_pct"], -1.6)
        self.assertEqual(rise_equities["positive_frequency_pct"], 33)
        self.assertEqual(cool_equities["median_return_pct"], 3.35)
        self.assertGreater(cool_equities["positive_frequency_pct"], rise_equities["positive_frequency_pct"])
        move = next(item for item in snapshot["indicators"] if item["symbol"] == "MOVE")
        self.assertEqual(move["source"]["provider_id"], "ice-move-index")
        tech = next(item for item in snapshot["episode_designs"] if item["key"] == "technology_stress_gap")
        self.assertIn("Technology listings", tech["comparison"])

    def test_filters_authored_validation_checkpoints_by_calendar_period(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        snapshot = build_volatility_lab_snapshot(
            providers,
            date(2026, 5, 25),
            date(2026, 1, 1),
            date(2026, 5, 25),
        )

        validation = snapshot["reaction_explorer"]["validation_sample"]
        self.assertEqual(validation["episode_count"], 2)
        self.assertEqual(
            validation["period"]["episode_dates"], ["2026-02-02", "2026-04-06"]
        )
        cools_one = next(
            result
            for result in validation["results"]
            if result["scenario_key"] == "vix_cools"
            and result["horizon_key"] == "1_session"
        )
        cool_equities = next(
            item for item in cools_one["lens_results"] if item["family"] == "Equities"
        )
        self.assertEqual(cool_equities["sample_count"], 2)
        self.assertEqual(cool_equities["median_return_pct"], 0.45)
        self.assertEqual(cool_equities["positive_frequency_pct"], 100)

    def test_rejects_missing_volatility_source(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        with self.assertRaisesRegex(SourceRegistryDataError, "registered source"):
            build_volatility_lab_snapshot(
                [item for item in providers if item.provider_id != "cboe-volatility-family"],
                date(2026, 5, 25),
            )

    def test_rejects_validation_period_after_review_cutoff(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        with self.assertRaisesRegex(SourceRegistryDataError, "after its review cutoff"):
            build_volatility_lab_snapshot(
                providers,
                date(2026, 5, 25),
                date(2026, 1, 1),
                date(2026, 5, 26),
            )


if __name__ == "__main__":
    unittest.main()
