import unittest
from datetime import date
from pathlib import Path

from marketwitness.market_intelligence import build_market_intelligence_snapshot
from marketwitness.source_registry import SourceRegistryDataError, load_source_registry


class MarketIntelligenceTests(unittest.TestCase):
    def test_builds_evidence_first_expansion_without_live_claims(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        snapshot = build_market_intelligence_snapshot(providers, date(2026, 5, 25))

        self.assertEqual(snapshot["module_count"], 8)
        self.assertEqual(snapshot["foundation_count"], 8)
        self.assertEqual(snapshot["planned_connector_count"], 0)
        regimes = next(
            item for item in snapshot["modules"] if item["key"] == "market_regimes"
        )
        self.assertEqual(regimes["priority"], "next")
        self.assertEqual(
            set(regimes["provider_ids"]),
            {"kraken-spot-public", "eia-open-data", "treasury-yield-curve"},
        )
        self.assertIn("does not recommend positions", snapshot["publication_boundary"])
        self.assertIn("not a buy", regimes["claim_limit"])
        self.assertEqual(regimes["route"], "/dashboard/market-context")
        self.assertIn("curve-regime calculations are active", regimes["coverage"])
        volatility = next(
            item for item in snapshot["modules"] if item["key"] == "volatility_lab"
        )
        self.assertEqual(volatility["route"], "/dashboard/volatility")
        self.assertEqual(volatility["title"], "VIX Reaction Explorer")
        self.assertIn("Cboe Volatility Index Family", {item["provider_name"] for item in volatility["sources"]})
        policy_signals = next(
            item for item in snapshot["modules"] if item["key"] == "policy_signal_lab"
        )
        self.assertEqual(policy_signals["route"], "/dashboard/presidential-impact")
        self.assertEqual(policy_signals["title"], "Presidential Impact Lab")
        self.assertIn(
            "Truth Social Public Content",
            {item["provider_name"] for item in policy_signals["sources"]},
        )
        self.assertIn(
            "White House Official News RSS",
            {item["provider_name"] for item in policy_signals["sources"]},
        )
        self.assertIn(
            "White House Presidential Actions RSS",
            {item["provider_name"] for item in policy_signals["sources"]},
        )
        self.assertIn(
            "U.S. Treasury Daily Treasury Par Yield Curve Rates",
            {item["provider_name"] for item in policy_signals["sources"]},
        )
        self.assertIn("Treasury 2Y/10Y", policy_signals["coverage"])
        macro = next(
            item for item in snapshot["modules"] if item["key"] == "macro_calendar"
        )
        self.assertEqual(macro["route"], "/dashboard/macro-calendar")
        self.assertEqual(macro["title"], "Macro Catalyst Calendar")
        self.assertIn("CPI", macro["coverage"])
        cot = next(
            item for item in snapshot["modules"] if item["key"] == "futures_positioning"
        )
        self.assertEqual(cot["title"], "COT Positioning Lab")
        self.assertEqual(cot["route"], "/dashboard/cot-positioning")
        self.assertIn("U.S. Dollar Index", cot["coverage"])
        insider = next(
            item for item in snapshot["modules"] if item["key"] == "insider_activity"
        )
        self.assertEqual(insider["title"], "Insider Activity Lab")
        self.assertEqual(insider["route"], "/dashboard/insider-activity")
        self.assertIn("P/S", insider["coverage"])
        self.assertIn("private transactions", insider["claim_limit"])

    def test_rejects_unknown_source_dependency(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        with self.assertRaisesRegex(SourceRegistryDataError, "registered source"):
            build_market_intelligence_snapshot(
                [item for item in providers if item.provider_id != "cftc-cot"],
                date(2026, 5, 25),
            )


if __name__ == "__main__":
    unittest.main()
