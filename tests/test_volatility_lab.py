import unittest
from datetime import date
from pathlib import Path

from targetaudit.source_registry import SourceRegistryDataError, load_source_registry
from targetaudit.volatility_lab import build_volatility_lab_snapshot


class VolatilityLabTests(unittest.TestCase):
    def test_maps_stress_families_without_claiming_real_episode_results(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        snapshot = build_volatility_lab_snapshot(providers, date(2026, 5, 25))

        self.assertEqual(snapshot["indicator_group_count"], 7)
        self.assertEqual(snapshot["episode_design_count"], 4)
        self.assertEqual(
            snapshot["phase_1"], ["VIX", "VIX1D / VIX9D / VIX3M", "VXN", "MOVE"]
        )
        self.assertIn("does not ingest Cboe or ICE", snapshot["publication_boundary"])
        move = next(item for item in snapshot["indicators"] if item["symbol"] == "MOVE")
        self.assertEqual(move["source"]["provider_id"], "ice-move-index")
        tech = next(item for item in snapshot["episode_designs"] if item["key"] == "technology_stress_gap")
        self.assertIn("Technology listings", tech["comparison"])

    def test_rejects_missing_volatility_source(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        with self.assertRaisesRegex(SourceRegistryDataError, "registered source"):
            build_volatility_lab_snapshot(
                [item for item in providers if item.provider_id != "cboe-volatility-family"],
                date(2026, 5, 25),
            )


if __name__ == "__main__":
    unittest.main()
