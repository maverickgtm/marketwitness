from __future__ import annotations

import importlib.util
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

_API_AVAILABLE = bool(
    importlib.util.find_spec("duckdb")
    and importlib.util.find_spec("fastapi")
    and importlib.util.find_spec("httpx")
)


@unittest.skipUnless(_API_AVAILABLE, "optional application dependencies not installed")
class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        from fastapi.testclient import TestClient

        from targetaudit.api import create_app
        from targetaudit.models import Evaluation
        from targetaudit.storage import EvaluationRun, store_evaluation_run

        self.directory = tempfile.TemporaryDirectory()
        root = Path(self.directory.name)
        asset = root / "targets.csv"
        asset.write_text("auditable input\n", encoding="utf-8")
        self.database = root / "targetaudit.duckdb"
        evaluations = [
            Evaluation(
                observation_id="hit",
                ticker="AAA",
                firm="Example Firm",
                sector="Financials",
                published_date="2023-01-02",
                price_target=Decimal("120"),
                source_url="https://example.invalid/hit",
                status="evaluated",
                direction="up",
                hit=True,
                days_to_target=20,
                terminal_absolute_error_pct=Decimal("0.05"),
                excess_return_pct=Decimal("0.03"),
                strategy_net_return_pct=Decimal("0.19"),
                strategy_net_excess_return_pct=Decimal("0.08"),
            ),
            Evaluation(
                observation_id="miss",
                ticker="AAA",
                firm="Other Firm",
                sector="Financials",
                published_date="2023-01-02",
                price_target=Decimal("90"),
                source_url="https://example.invalid/miss",
                status="evaluated",
                direction="down",
                hit=False,
                terminal_absolute_error_pct=Decimal("0.10"),
                excess_return_pct=Decimal("-0.01"),
                strategy_net_return_pct=Decimal("-0.02"),
            ),
            Evaluation(
                observation_id="excluded",
                ticker="BBB",
                firm="Example Firm",
                sector="Financials",
                published_date="2023-01-02",
                price_target=Decimal("100"),
                source_url="https://example.invalid/excluded",
                status="excluded",
                reason="missing_reference_price",
            ),
        ]
        store_evaluation_run(
            self.database,
            EvaluationRun(
                run_id="api-demo",
                as_of=date(2025, 1, 1),
                minimum_sample=1,
                transaction_cost_bps_per_side=Decimal("10"),
                universe_id="financials-demo",
                asset_paths={"targets": asset},
            ),
            evaluations,
        )
        self.client = TestClient(create_app(self.database))

    def tearDown(self) -> None:
        self.directory.cleanup()

    def test_lists_runs_and_assets_without_exposing_local_file_paths(self) -> None:
        health = self.client.get("/api/v1/health")
        run = self.client.get("/api/v1/runs/api-demo")

        self.assertEqual(health.status_code, 200)
        self.assertTrue(health.json()["database_available"])
        self.assertEqual(run.status_code, 200)
        self.assertEqual(run.json()["evaluated_count"], 2)
        self.assertEqual(run.json()["assets"][0]["asset_role"], "targets")
        self.assertNotIn("asset_path", run.json()["assets"][0])

    def test_serves_firm_ranking_using_methodology_outputs(self) -> None:
        response = self.client.get("/api/v1/runs/api-demo/rankings/firms")

        self.assertEqual(response.status_code, 200)
        ranking = response.json()["ranking"]
        self.assertEqual(ranking[0]["firm"], "Example Firm")
        self.assertEqual(ranking[0]["hit_rate"], 1.0)
        self.assertLess(ranking[0]["hit_rate_ci_95_low"], 1.0)
        self.assertEqual(ranking[1]["firm"], "Other Firm")

    def test_serves_firm_ticker_and_exclusion_audit_views(self) -> None:
        firm = self.client.get("/api/v1/runs/api-demo/firms/Example%20Firm")
        ticker = self.client.get("/api/v1/runs/api-demo/tickers/aaa")
        audit = self.client.get("/api/v1/runs/api-demo/audit/exclusions")

        self.assertEqual(firm.json()["statuses"], {"evaluated": 1, "excluded": 1})
        self.assertEqual(ticker.json()["ticker"], "AAA")
        self.assertEqual(len(ticker.json()["observations"]), 2)
        self.assertEqual(audit.json()["counts_by_reason"], {"missing_reference_price": 1})

    def test_unknown_run_and_firm_return_not_found(self) -> None:
        missing_run = self.client.get("/api/v1/runs/not-present")
        missing_firm = self.client.get("/api/v1/runs/api-demo/firms/Unknown")

        self.assertEqual(missing_run.status_code, 404)
        self.assertEqual(missing_firm.status_code, 404)


if __name__ == "__main__":
    unittest.main()
