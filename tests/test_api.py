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
        prices = root / "prices.csv"
        prices.write_text("auditable prices\n", encoding="utf-8")
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
                provider_id="synthetic-demo",
                direction="up",
                reference_date="2023-01-03",
                reference_price=Decimal("100"),
                entry_date="2023-01-04",
                entry_price=Decimal("101"),
                expiry_date="2024-01-03",
                terminal_date="2024-01-03",
                terminal_price=Decimal("118"),
                hit=True,
                hit_date="2023-02-01",
                days_to_target=20,
                terminal_absolute_error_pct=Decimal("0.05"),
                excess_return_pct=Decimal("0.03"),
                strategy_exit_date="2023-02-01",
                strategy_exit_price=Decimal("120"),
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
                provider_id="synthetic-demo",
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
                provider_id="synthetic-demo",
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
                asset_paths={"targets": asset, "prices": prices},
                dataset_label="API fixture",
            ),
            evaluations,
        )
        alternate_asset = root / "targets-alternate.csv"
        alternate_asset.write_text("alternate auditable input\n", encoding="utf-8")
        self.reports = root / "reports"
        self.reports.mkdir()
        (self.reports / "ipo-watch.html").write_text(
            "<html><h1>IPO Watch generated page</h1></html>", encoding="utf-8"
        )
        (self.reports / "etf-holdings-regulatory-history.html").write_text(
            "<html><h1>ETF Regulatory Holdings generated page</h1></html>",
            encoding="utf-8",
        )
        (self.reports / "lse-fca-check.html").write_text(
            "<html><h1>Public Document Checks generated page</h1></html>",
            encoding="utf-8",
        )
        (self.reports / "rwa-watch.html").write_text(
            "<html><h1>RWA Watch Sandbox generated page</h1></html>",
            encoding="utf-8",
        )
        store_evaluation_run(
            self.database,
            EvaluationRun(
                run_id="api-alternate",
                as_of=date(2025, 1, 1),
                minimum_sample=1,
                transaction_cost_bps_per_side=Decimal("10"),
                universe_id="financials-demo",
                asset_paths={"targets": alternate_asset, "prices": prices},
                dataset_label="Alternate API fixture",
            ),
            evaluations,
        )
        self.client = TestClient(
            create_app(
                self.database,
                Path("data/samples/source_registry.csv"),
                Path("data/samples/provider_approval_queue.csv"),
                self.reports,
            )
        )

    def tearDown(self) -> None:
        self.directory.cleanup()

    def test_lists_runs_and_assets_without_exposing_local_file_paths(self) -> None:
        health = self.client.get("/api/v1/health")
        run = self.client.get("/api/v1/runs/api-demo")

        self.assertEqual(health.status_code, 200)
        self.assertTrue(health.json()["database_available"])
        self.assertTrue(health.json()["source_registry_available"])
        self.assertTrue(health.json()["provider_approvals_available"])
        self.assertTrue(health.json()["generated_reports_available"])
        self.assertTrue(health.json()["licensed_extensions_available"])
        self.assertEqual(run.status_code, 200)
        self.assertEqual(run.json()["evaluated_count"], 2)
        self.assertEqual(run.json()["methodology_version"], "0.3.3")
        self.assertEqual(run.json()["dataset_label"], "API fixture")
        self.assertEqual(len(run.json()["dataset_fingerprint"]), 64)
        self.assertEqual(
            {asset["asset_role"] for asset in run.json()["assets"]},
            {"prices", "targets"},
        )
        self.assertNotIn("asset_path", run.json()["assets"][0])
        self.assertIn("provider_id", run.json()["assets"][0])

    def test_serves_firm_ranking_using_methodology_outputs(self) -> None:
        response = self.client.get("/api/v1/runs/api-demo/rankings/firms")

        self.assertEqual(response.status_code, 200)
        ranking = response.json()["ranking"]
        self.assertEqual(ranking[0]["firm"], "Example Firm")
        self.assertEqual(ranking[0]["hit_rate"], 1.0)
        self.assertLess(ranking[0]["hit_rate_ci_95_low"], 1.0)
        self.assertEqual(ranking[1]["firm"], "Other Firm")

    def test_serves_financials_dashboard_and_filter_facets(self) -> None:
        page = self.client.get("/dashboard/financials")
        facets = self.client.get("/api/v1/runs/api-demo/facets")

        self.assertEqual(page.status_code, 200)
        self.assertIn("Price targets,", page.text)
        self.assertIn("/api/v1", page.text)
        self.assertIn("evidenceHref", page.text)
        self.assertIn("Export observations CSV", page.text)
        self.assertIn("renderTimeline", page.text)
        self.assertIn("Compare Stored Runs", page.text)
        self.assertEqual(facets.status_code, 200)
        self.assertEqual(facets.json()["sectors"], ["Financials"])
        self.assertEqual(facets.json()["tickers"], ["AAA", "BBB"])

    def test_serves_open_edition_as_the_zero_cost_home_page(self) -> None:
        home = self.client.get("/")
        page = self.client.get("/dashboard/open")
        snapshot = self.client.get("/api/v1/open-edition")

        self.assertEqual(home.status_code, 200)
        self.assertIn("No paid data required", home.text)
        self.assertEqual(page.status_code, 200)
        self.assertIn("/api/v1/open-edition", page.text)
        self.assertEqual(snapshot.status_code, 200)
        self.assertEqual(snapshot.json()["zero_cost_available_count"], 5)
        self.assertEqual(snapshot.json()["offline_ready_count"], 2)
        self.assertEqual(snapshot.json()["public_data_ready_count"], 3)
        self.assertEqual(snapshot.json()["optional_extension_count"], 1)

    def test_serves_optional_licensed_extensions_without_enabling_public_rankings(self) -> None:
        page = self.client.get("/dashboard/extensions")
        snapshot = self.client.get("/api/v1/extensions/licensed")

        self.assertEqual(page.status_code, 200)
        self.assertIn("Bring your own", page.text)
        self.assertIn("Freemium API warning", page.text)
        self.assertIn("/api/v1/extensions/licensed", page.text)
        self.assertEqual(snapshot.status_code, 200)
        self.assertEqual(snapshot.json()["extension_count"], 8)
        self.assertEqual(snapshot.json()["listed_price_count"], 3)
        self.assertEqual(snapshot.json()["public_output_approved_count"], 0)
        self.assertEqual(snapshot.json()["items"][0]["price_display"], "USD 99/month")
        self.assertEqual(snapshot.json()["items"][1]["extension_id"], "marketbeat-all-access")

    def test_serves_generated_open_edition_monitor_pages(self) -> None:
        ipo = self.client.get("/dashboard/ipo-watch")
        etf = self.client.get("/dashboard/etf-regulatory")
        documents = self.client.get("/dashboard/document-checks")
        rwa = self.client.get("/dashboard/rwa-watch")

        self.assertIn("IPO Watch generated page", ipo.text)
        self.assertIn("ETF Regulatory Holdings generated page", etf.text)
        self.assertIn("Public Document Checks generated page", documents.text)
        self.assertIn("RWA Watch Sandbox generated page", rwa.text)

    def test_compares_run_methodology_and_evidence_fingerprints(self) -> None:
        response = self.client.get(
            "/api/v1/runs/compare?left_run_id=api-demo&right_run_id=api-alternate"
        )

        self.assertEqual(response.status_code, 200)
        comparison = response.json()
        self.assertTrue(comparison["same_methodology"])
        self.assertFalse(comparison["same_dataset"])
        self.assertEqual(
            comparison["comparability"], "same_methodology_different_dataset"
        )
        self.assertEqual(comparison["deltas"]["evaluated_count"], 0)

    def test_serves_operations_quality_monitor_and_dashboard(self) -> None:
        response = self.client.get("/api/v1/operations/quality")
        selected = self.client.get("/api/v1/operations/quality?run_id=api-demo")
        release = self.client.get(
            "/api/v1/operations/quality?run_id=api-demo&public_release=true"
        )
        missing = self.client.get("/api/v1/operations/quality?run_id=not-present")
        page = self.client.get("/dashboard/operations")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["run_count"], 2)
        self.assertEqual(response.json()["quality_pass_count"], 2)
        self.assertEqual(response.json()["blocked_count"], 0)
        self.assertIn("does not grant data publication rights", response.json()["publication_note"])
        self.assertEqual(selected.status_code, 200)
        self.assertEqual(selected.json()["selected_run_id"], "api-demo")
        self.assertEqual(selected.json()["run_count"], 1)
        self.assertEqual(release.json()["quality_scope"], "public_release")
        self.assertEqual(release.json()["blocked_count"], 1)
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(page.status_code, 200)
        self.assertIn("Ship evidence,", page.text)
        self.assertIn("operations/quality", page.text)
        self.assertIn("public_release", page.text)

    def test_serves_governance_dashboard_and_filtered_source_controls(self) -> None:
        page = self.client.get("/dashboard/governance")
        sources = self.client.get("/api/v1/governance/sources")
        blocked = self.client.get(
            "/api/v1/governance/sources?deployment_state=blocked"
        )
        holdings = self.client.get(
            "/api/v1/governance/sources?data_class=ETF%20holdings"
        )

        self.assertEqual(page.status_code, 200)
        self.assertIn("Open code.", page.text)
        self.assertIn("Run Exclusions And Pending", page.text)
        self.assertIn("Provider Control", page.text)
        self.assertEqual(sources.json()["provider_count"], 26)
        self.assertGreater(sources.json()["open_review_count"], 0)
        self.assertEqual(sources.json()["blocked_count"], 2)
        self.assertEqual(
            {item["provider_id"] for item in blocked.json()["sources"]},
            {"tipranks-reference", "xstocks-backing-api"},
        )
        self.assertEqual(len(holdings.json()["sources"]), 3)
        self.assertIn("publication_policy", sources.json()["sources"][0])

    def test_serves_public_scorecard_readiness_without_treating_demo_as_production(self) -> None:
        readiness = self.client.get("/api/v1/readiness/scorecard")
        page = self.client.get("/dashboard/readiness")

        self.assertEqual(readiness.status_code, 200)
        self.assertFalse(readiness.json()["public_release_ready"])
        self.assertEqual(readiness.json()["public_ready_count"], 0)
        self.assertEqual(readiness.json()["requirement_count"], 4)
        targets = readiness.json()["requirements"][0]
        self.assertEqual(targets["status"], "integration_pending")
        self.assertFalse(targets["providers"][0]["production_eligible"])
        self.assertEqual(page.status_code, 200)
        self.assertIn("Earn the right", page.text)
        self.assertIn("/api/v1/readiness/scorecard", page.text)

    def test_serves_provider_approval_queue_and_dashboard(self) -> None:
        approvals = self.client.get("/api/v1/governance/approvals")
        page = self.client.get("/dashboard/approvals")

        self.assertEqual(approvals.status_code, 200)
        self.assertEqual(approvals.json()["queue_count"], 7)
        self.assertEqual(approvals.json()["critical_open_count"], 4)
        self.assertEqual(approvals.json()["approved_count"], 0)
        self.assertFalse(approvals.json()["public_activation_ready"])
        self.assertEqual(
            {item["provider_id"] for item in approvals.json()["items"]},
            {
                "benzinga-targets",
                "alpha-vantage-prices",
                "nasdaq-daily-list",
                "nyse-actions",
                "sp-dji-constituents",
                "finnhub-targets",
                "fmp-targets",
            },
        )
        self.assertEqual(page.status_code, 200)
        self.assertIn("Permission before", page.text)
        self.assertIn("/api/v1/governance/approvals", page.text)

    def test_serves_combined_release_decision_and_release_center(self) -> None:
        decision = self.client.get("/api/v1/releases/scorecard?run_id=api-demo")
        missing = self.client.get("/api/v1/releases/scorecard?run_id=not-present")
        page = self.client.get("/dashboard/release")

        self.assertEqual(decision.status_code, 200)
        self.assertFalse(decision.json()["release_ready"])
        self.assertEqual(decision.json()["release_status"], "blocked")
        self.assertEqual(decision.json()["source_gate_status"], "blocked")
        self.assertEqual(decision.json()["quality_gate_status"], "blocked")
        self.assertEqual(decision.json()["lineage_gate_status"], "blocked")
        self.assertEqual(decision.json()["asset_lineage_gate_status"], "blocked")
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(page.status_code, 200)
        self.assertIn("Release only", page.text)
        self.assertIn("/api/v1/releases/scorecard", page.text)

    def test_serves_firm_ticker_and_exclusion_audit_views(self) -> None:
        firm = self.client.get("/api/v1/runs/api-demo/firms/Example%20Firm")
        ticker = self.client.get("/api/v1/runs/api-demo/tickers/aaa")
        audit = self.client.get("/api/v1/runs/api-demo/audit/exclusions")

        self.assertEqual(firm.json()["statuses"], {"evaluated": 1, "excluded": 1})
        self.assertEqual(ticker.json()["ticker"], "AAA")
        self.assertEqual(len(ticker.json()["observations"]), 2)
        self.assertEqual(audit.json()["counts_by_reason"], {"missing_reference_price": 1})
        self.assertEqual(audit.json()["observations"][0]["provider_id"], "synthetic-demo")

    def test_serves_ticker_evidence_timeline_without_claiming_daily_prices(self) -> None:
        response = self.client.get("/api/v1/runs/api-demo/tickers/aaa/timeline")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["series_type"], "evaluation_evidence_points")
        self.assertIn("not a daily", data["limitation"])
        points = data["observations"][0]["points"]
        self.assertEqual(points[0]["label"], "Reference close")
        self.assertTrue(any("Strategy exit" in point["label"] for point in points))

    def test_exports_observations_and_filtered_ranking_as_csv(self) -> None:
        observations = self.client.get("/api/v1/runs/api-demo/export/evaluations.csv")
        ranking = self.client.get(
            "/api/v1/runs/api-demo/export/rankings-firms.csv?direction=up&minimum_sample=1"
        )

        self.assertEqual(observations.status_code, 200)
        self.assertIn("text/csv", observations.headers["content-type"])
        self.assertIn(
            'filename="targetaudit-api-demo-evaluations.csv"',
            observations.headers["content-disposition"],
        )
        self.assertIn("observation_id", observations.text)
        self.assertIn("provider_id", observations.text)
        self.assertIn("synthetic-demo", observations.text)
        self.assertIn("hit", observations.text)
        self.assertIn("Example Firm", ranking.text)
        self.assertNotIn("Other Firm", ranking.text)

    def test_unknown_run_and_firm_return_not_found(self) -> None:
        missing_run = self.client.get("/api/v1/runs/not-present")
        missing_firm = self.client.get("/api/v1/runs/api-demo/firms/Unknown")

        self.assertEqual(missing_run.status_code, 404)
        self.assertEqual(missing_firm.status_code, 404)


if __name__ == "__main__":
    unittest.main()
