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

        from marketwitness.api import create_app
        from marketwitness.models import Evaluation
        from marketwitness.storage import EvaluationRun, store_evaluation_run

        self.directory = tempfile.TemporaryDirectory()
        root = Path(self.directory.name)
        asset = root / "targets.csv"
        asset.write_text("auditable input\n", encoding="utf-8")
        prices = root / "prices.csv"
        prices.write_text("auditable prices\n", encoding="utf-8")
        self.database = root / "marketwitness.duckdb"
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
        (self.reports / "sec-ipo-discovery.html").write_text(
            "<html><h1>SEC IPO Discovery Queue generated page</h1></html>",
            encoding="utf-8",
        )
        (self.reports / "sec-alerts.html").write_text(
            "<html><h1>SEC IPO Alerts generated page</h1></html>", encoding="utf-8"
        )
        (self.reports / "sec-review-outcomes.html").write_text(
            "<html><h1>IPO Review Outcomes generated page</h1></html>",
            encoding="utf-8",
        )
        (self.reports / "etf-holdings-regulatory-history.html").write_text(
            "<html><h1>ETF Regulatory Holdings generated page</h1></html>",
            encoding="utf-8",
        )
        for filename, title in (
            ("etf-holdings-ark-activity.html", "ARKK Holdings Sandbox generated page"),
            ("etf-holdings-activity.html", "XLF Holdings Sandbox generated page"),
            ("etf-holdings-iyf-activity.html", "IYF Holdings Sandbox generated page"),
            ("etf-holdings-regulatory-activity.html", "N-PORT Recent Filing generated page"),
            ("nport-dataset-catalog.html", "N-PORT Dataset Catalog generated page"),
            ("nport-sync.html", "N-PORT Sync Status generated page"),
        ):
            (self.reports / filename).write_text(
                f"<html><h1>{title}</h1></html>", encoding="utf-8"
            )
        (self.reports / "lse-fca-check.html").write_text(
            "<html><h1>Public Document Checks generated page</h1></html>",
            encoding="utf-8",
        )
        (self.reports / "rwa-watch.html").write_text(
            "<html><h1>RWA Watch Sandbox generated page</h1></html>",
            encoding="utf-8",
        )
        (self.reports / "global-alerts.html").write_text(
            "<html><h1>Global Listings Alerts generated page</h1></html>",
            encoding="utf-8",
        )
        (self.reports / "issuer-confirmations.html").write_text(
            "<html><h1>Issuer Confirmations generated page</h1></html>",
            encoding="utf-8",
        )
        for filename, title in (
            ("global-listings.html", "Global Listings Watch generated page"),
            ("hkex-monitor.html", "HKEX Monitor generated page"),
            ("lse-upcoming.html", "LSE Upcoming generated page"),
            ("asx-monitor.html", "ASX Monitor generated page"),
            ("tsx-monitor.html", "TSX Monitor generated page"),
            ("jpx-monitor.html", "JPX Monitor generated page"),
            ("edinet-monitor.html", "EDINET Monitor generated page"),
            ("cvm-monitor.html", "CVM Monitor generated page"),
            ("esma-monitor.html", "ESMA Monitor generated page"),
            ("opendart-monitor.html", "OpenDART Monitor generated page"),
            ("sgx-monitor.html", "SGX Monitor generated page"),
        ):
            (self.reports / filename).write_text(
                f"<html><h1>{title}</h1></html>", encoding="utf-8"
            )
        for filename, title in (
            ("authorized-targets-import.html", "Target Import Audit generated page"),
            ("alpha-vantage-prices.html", "Adjusted Price Evidence generated page"),
            ("corporate-actions.html", "Corporate Actions Audit generated page"),
            ("operations-quality.html", "Operations Quality Snapshot generated page"),
            ("scorecard-release.html", "Release Decision Snapshot generated page"),
        ):
            (self.reports / filename).write_text(
                f"<html><h1>{title}</h1></html>", encoding="utf-8"
            )
        for filename, title in (
            ("open-edition.html", "Open Edition Snapshot generated page"),
            ("licensed-extensions.html", "Licensed Extensions Snapshot generated page"),
            ("source-registry.html", "Source Registry Snapshot generated page"),
            ("provider-approvals.html", "Provider Approvals Snapshot generated page"),
            ("provider-approval-review-outcomes.html", "Approval Review Outcomes generated page"),
            ("scorecard-readiness.html", "Scorecard Readiness Snapshot generated page"),
        ):
            (self.reports / filename).write_text(
                f"<html><h1>{title}</h1></html>", encoding="utf-8"
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
        self.assertIn("/dashboard/financials-evidence", page.text)
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
        self.assertEqual(snapshot.json()["zero_cost_available_count"], 6)
        self.assertEqual(snapshot.json()["offline_ready_count"], 2)
        self.assertEqual(snapshot.json()["public_data_ready_count"], 3)
        self.assertEqual(snapshot.json()["attributed_widget_count"], 1)
        self.assertEqual(snapshot.json()["optional_extension_count"], 1)
        self.assertIn("/dashboard/reports", page.text)
        self.assertIn("/dashboard/policy", page.text)
        self.assertIn("/dashboard/market-context", page.text)
        self.assertIn("/dashboard/intelligence", page.text)
        self.assertIn("/dashboard/commons", page.text)
        self.assertIn("/dashboard/volatility", page.text)
        self.assertIn("/dashboard/presidential-impact", page.text)
        self.assertIn("/dashboard/rwa-watch", page.text)
        self.assertIn("Tokenized Assets / RWA", page.text)
        self.assertIn("Analyst Scorecards", page.text)
        self.assertIn("Contribute Connectors", page.text)
        self.assertIn('aria-label="Quick navigation"', page.text)
        self.assertIn("What Makes MarketWitness Different", page.text)
        self.assertIn("VIX Reaction Explorer", page.text)
        self.assertIn("Trump Communication Impact", page.text)
        self.assertIn("Global IPO Radar", page.text)
        self.assertIn("Evidence Commons", page.text)
        self.assertIn("Core Departments", page.text)
        self.assertIn("Market Pulse", page.text)
        self.assertIn("TradingView display", page.text)
        self.assertIn("embed-widget-ticker-tape.js", page.text)
        self.assertIn("embed-widget-market-overview.js", page.text)
        self.assertIn("does not store widget data", page.text)
        self.assertIn("Loads with Internet access", page.text)
        self.assertIn("overflow-y:auto", page.text)
        self.assertIn("overscroll-behavior:contain", page.text)

    def test_serves_market_intelligence_blueprint_without_live_data_claims(self) -> None:
        page = self.client.get("/dashboard/intelligence")
        snapshot = self.client.get("/api/v1/intelligence/modules")

        self.assertEqual(page.status_code, 200)
        self.assertIn("Events. Context.", page.text)
        self.assertIn("/api/v1/intelligence/modules", page.text)
        self.assertIn("Source-first expansion blueprint", page.text)
        self.assertEqual(snapshot.status_code, 200)
        self.assertEqual(snapshot.json()["module_count"], 8)
        self.assertEqual(snapshot.json()["foundation_count"], 4)
        self.assertEqual(snapshot.json()["planned_connector_count"], 4)
        self.assertIn("no newly collected live values", snapshot.json()["publication_boundary"])
        keys = {item["key"] for item in snapshot.json()["modules"]}
        self.assertIn("market_regimes", keys)
        self.assertIn("insider_activity", keys)
        self.assertIn("futures_positioning", keys)
        self.assertIn("volatility_lab", keys)
        self.assertIn("policy_signal_lab", keys)
        self.assertIn("/dashboard/volatility", page.text)
        self.assertIn("/dashboard/presidential-impact", page.text)
        self.assertIn("VIX Reaction Explorer", page.text)

    def test_serves_volatility_research_lab_without_implying_a_trading_signal(self) -> None:
        page = self.client.get("/dashboard/volatility")
        snapshot = self.client.get("/api/v1/intelligence/volatility")

        self.assertEqual(page.status_code, 200)
        self.assertIn("When VIX moves", page.text)
        self.assertIn("what reacts?", page.text)
        self.assertIn("VIX Reaction Explorer", page.text)
        self.assertIn("Real results gated / validation live", page.text)
        self.assertIn("Forward Reaction Statistics", page.text)
        self.assertIn("Median return", page.text)
        self.assertIn("Synthetic validation sample", page.text)
        self.assertIn("VIXCLS", page.text)
        self.assertIn("via FRED", page.text)
        self.assertIn("External VIX display unavailable", page.text)
        self.assertIn("/api/v1/intelligence/volatility", page.text)
        self.assertEqual(snapshot.status_code, 200)
        self.assertEqual(snapshot.json()["indicator_group_count"], 7)
        self.assertEqual(snapshot.json()["episode_design_count"], 4)
        self.assertEqual(snapshot.json()["reaction_explorer"]["validation_sample"]["result_count"], 10)
        self.assertEqual(
            snapshot.json()["reaction_explorer"]["validation_sample"]["mode"],
            "project_authored_not_market_observations",
        )
        self.assertEqual(
            [scenario["key"] for scenario in snapshot.json()["reaction_explorer"]["scenarios"]],
            ["vix_rises", "vix_cools"],
        )
        self.assertIn("VXN", snapshot.json()["phase_1"])
        self.assertIn("MOVE", snapshot.json()["phase_1"])
        self.assertIn("does not ingest Cboe or ICE", snapshot.json()["publication_boundary"])

    def test_serves_policy_signal_lab_with_truth_social_collection_disabled(self) -> None:
        page = self.client.get("/dashboard/presidential-impact")
        legacy_page = self.client.get("/dashboard/policy-signals")
        snapshot = self.client.get("/api/v1/intelligence/policy-signals")

        self.assertEqual(page.status_code, 200)
        self.assertEqual(legacy_page.status_code, 200)
        self.assertIn("Trump communications.", page.text)
        self.assertIn("Market fingerprints.", page.text)
        self.assertIn("Presidential Impact Lab", page.text)
        self.assertIn("VIXCLS", page.text)
        self.assertIn("/api/v1/intelligence/policy-signals", page.text)
        self.assertEqual(snapshot.status_code, 200)
        self.assertEqual(snapshot.json()["product"], "Presidential Impact Lab")
        self.assertEqual(snapshot.json()["case_study"], "Donald Trump / Truth Social communications")
        self.assertEqual(snapshot.json()["coverage_start"], "2025-01-20")
        self.assertIn("disabled_pending_written_permission", snapshot.json()["live_feed_status"])
        self.assertEqual(snapshot.json()["official_intake_status"], "eligible_for_connector_implementation")
        self.assertIn("prohibit automated access", snapshot.json()["publication_boundary"])
        self.assertIn("JPMorgan Volfefe Index", {item["name"] for item in snapshot.json()["prior_art"]})
        self.assertIn("Authorized Intake Map", page.text)
        self.assertIn("Browse official page", page.text)
        self.assertIn("RSS feed (machine-readable)", page.text)
        self.assertIn(
            "https://www.whitehouse.gov/news/feed/",
            {item["url"] for item in snapshot.json()["approved_intake_candidates"]},
        )
        news_channel = next(
            item
            for item in snapshot.json()["approved_intake_candidates"]
            if item["name"] == "White House News RSS"
        )
        self.assertEqual(news_channel["page_url"], "https://www.whitehouse.gov/news/")
        self.assertEqual(news_channel["url"], "https://www.whitehouse.gov/news/feed/")

    def test_serves_allowlisted_report_center_for_periodic_bundle(self) -> None:
        page = self.client.get("/dashboard/reports")

        self.assertEqual(page.status_code, 200)
        self.assertIn("Reproducible reports.", page.text)
        self.assertIn("Known routes only.", page.text)
        self.assertIn("27 allowlisted pages", page.text)
        self.assertIn("/dashboard/ipo-watch", page.text)
        self.assertIn("/dashboard/sec-discovery", page.text)
        self.assertIn("/dashboard/sec-alerts", page.text)
        self.assertIn("/dashboard/ipo-reviews", page.text)
        self.assertIn('href="/dashboard/ipo"', page.text)
        self.assertIn("IPO Watch Center", page.text)
        self.assertIn("/dashboard/etf/arkk-demo", page.text)
        self.assertIn("/dashboard/etf/xlf-demo", page.text)
        self.assertIn("/dashboard/etf/iyf-demo", page.text)
        self.assertIn("/dashboard/etf/nport-recent", page.text)
        self.assertIn("/dashboard/etf-regulatory", page.text)
        self.assertIn("/dashboard/etf/nport-catalog", page.text)
        self.assertIn("/dashboard/etf/nport-sync", page.text)
        self.assertIn('href="/dashboard/etf"', page.text)
        self.assertIn("ETF Evidence Center", page.text)
        self.assertIn("/dashboard/document-checks", page.text)
        self.assertIn("/dashboard/rwa-watch", page.text)
        self.assertIn("/dashboard/global-listings", page.text)
        self.assertIn("/dashboard/global-alerts", page.text)
        self.assertIn("/dashboard/issuer-confirmations", page.text)
        self.assertIn("/dashboard/contribute?lang=en", page.text)
        self.assertIn("Global Contributors", page.text)
        self.assertIn("/dashboard/commons", page.text)
        self.assertIn("Evidence Passport Commons", page.text)
        self.assertIn("/dashboard/audit/target-import", page.text)
        self.assertIn("/dashboard/audit/adjusted-prices", page.text)
        self.assertIn("/dashboard/audit/corporate-actions", page.text)
        self.assertIn("/dashboard/audit/operations-quality", page.text)
        self.assertIn("/dashboard/audit/release-decision", page.text)
        self.assertIn('href="/dashboard/financials-evidence"', page.text)
        self.assertIn("Financials Evidence Center", page.text)
        self.assertIn("/dashboard/governance-report/open-edition", page.text)
        self.assertIn("/dashboard/governance-report/licensed-extensions", page.text)
        self.assertIn("/dashboard/governance-report/source-registry", page.text)
        self.assertIn("/dashboard/governance-report/provider-approvals", page.text)
        self.assertIn("/dashboard/governance-report/approval-review", page.text)
        self.assertIn("/dashboard/governance-report/scorecard-readiness", page.text)
        self.assertIn("not live market alerts", page.text)

    def test_serves_financials_evidence_center_without_real_analyst_claims(self) -> None:
        page = self.client.get("/dashboard/financials-evidence")

        self.assertEqual(page.status_code, 200)
        self.assertIn("Audit before ranking.", page.text)
        for route in (
            "/dashboard/audit/target-import",
            "/dashboard/audit/adjusted-prices",
            "/dashboard/audit/corporate-actions",
            "/dashboard/audit/operations-quality",
            "/dashboard/audit/release-decision",
            "/dashboard/financials",
            "/dashboard/readiness",
            "/dashboard/release",
            "/dashboard/governance",
            "/dashboard/approvals",
            "/dashboard/operations",
        ):
            self.assertIn(route, page.text)
        self.assertIn("does not publish real analyst track records", page.text)
        self.assertIn("Public real-data scorecard", page.text)

    def test_serves_localized_global_contributor_gateway_with_rights_boundary(self) -> None:
        localized_markers = {
            "en": "Bring your market.",
            "ja": "市場の知識を。",
            "pt-BR": "Traga seu mercado.",
            "zh-Hant": "帶來你的市場",
            "ko": "시장을 제안하고",
        }

        for language, marker in localized_markers.items():
            with self.subTest(language=language):
                page = self.client.get(f"/dashboard/contribute?lang={language}")
                self.assertEqual(page.status_code, 200)
                self.assertIn(marker, page.text)
                self.assertIn("/dashboard/global-listings", page.text)
                self.assertIn("/dashboard/commons", page.text)
                self.assertIn("Data Source Proposal", page.text)

        fallback = self.client.get("/dashboard/contribute?lang=xx")
        self.assertIn("Bring your market.", fallback.text)
        self.assertIn("not publication permission", fallback.text)

    def test_serves_ipo_watch_center_without_promoting_discovered_evidence(self) -> None:
        page = self.client.get("/dashboard/ipo")

        self.assertEqual(page.status_code, 200)
        self.assertIn("Confirm before status.", page.text)
        self.assertIn("/dashboard/sec-discovery", page.text)
        self.assertIn("/dashboard/sec-alerts", page.text)
        self.assertIn("/dashboard/ipo-reviews", page.text)
        self.assertIn("/dashboard/ipo-watch", page.text)
        self.assertIn("/dashboard/global-listings", page.text)
        self.assertIn("/dashboard/global-alerts", page.text)
        self.assertIn("/dashboard/issuer-confirmations", page.text)
        self.assertIn("does not confirm an IPO", page.text)
        self.assertIn("Required paid data", page.text)
        self.assertIn("Verification Ladder", page.text)
        self.assertIn("Open status board", page.text)

    def test_serves_etf_evidence_center_with_separated_frequency_layers(self) -> None:
        page = self.client.get("/dashboard/etf")

        self.assertEqual(page.status_code, 200)
        self.assertIn("Frequency first.", page.text)
        self.assertIn("/dashboard/etf/arkk-demo", page.text)
        self.assertIn("/dashboard/etf/xlf-demo", page.text)
        self.assertIn("/dashboard/etf/iyf-demo", page.text)
        self.assertIn("/dashboard/etf/nport-recent", page.text)
        self.assertIn("/dashboard/etf-regulatory", page.text)
        self.assertIn("/dashboard/etf/nport-catalog", page.text)
        self.assertIn("/dashboard/etf/nport-sync", page.text)
        self.assertIn("not confirmed manager trades", page.text)
        self.assertIn("Required paid data", page.text)
        self.assertIn("Evidence Layers", page.text)
        self.assertIn("Open regulatory view", page.text)

    def test_serves_attributed_market_context_without_a_data_endpoint(self) -> None:
        page = self.client.get("/dashboard/market-context")

        self.assertEqual(page.status_code, 200)
        self.assertIn("Crypto. Energy. Metals.", page.text)
        self.assertIn("BINANCE:BTCUSDT", page.text)
        self.assertIn("BINANCE:ETHUSDT", page.text)
        self.assertIn("TVC:GOLD", page.text)
        self.assertIn("TVC:USOIL", page.text)
        self.assertIn("FX:EURUSD", page.text)
        self.assertIn("by TradingView", page.text)
        self.assertIn("embed-widget-advanced-chart.js", page.text)
        self.assertIn("embed-widget-ticker-tape.js", page.text)
        self.assertIn("embed-widget-market-overview.js", page.text)
        self.assertIn("Asset Watchlists", page.text)
        self.assertIn("Loading BTC chart from TradingView", page.text)
        self.assertIn("MarketWitness-collected data", page.text)

    def test_serves_public_use_policy_with_blocked_source_boundaries(self) -> None:
        page = self.client.get("/dashboard/policy")
        policy = self.client.get("/api/v1/policy/public-use")

        self.assertEqual(page.status_code, 200)
        self.assertIn("Research evidence.", page.text)
        self.assertIn("/api/v1/policy/public-use", page.text)
        self.assertEqual(policy.status_code, 200)
        self.assertEqual(policy.json()["review_status"], "pending_external_legal_review")
        self.assertEqual(policy.json()["tracked_source_count"], 49)
        self.assertEqual(policy.json()["blocked_source_count"], 6)
        self.assertIn(
            "mas-opera-reference",
            {item["provider_id"] for item in policy.json()["blocked_sources"]},
        )

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
        sec_discovery = self.client.get("/dashboard/sec-discovery")
        sec_alerts = self.client.get("/dashboard/sec-alerts")
        ipo_reviews = self.client.get("/dashboard/ipo-reviews")
        etf = self.client.get("/dashboard/etf-regulatory")
        documents = self.client.get("/dashboard/document-checks")
        rwa = self.client.get("/dashboard/rwa-watch")
        global_alerts = self.client.get("/dashboard/global-alerts")
        issuer_confirmations = self.client.get("/dashboard/issuer-confirmations")

        self.assertIn("IPO Watch generated page", ipo.text)
        self.assertIn("SEC IPO Discovery Queue generated page", sec_discovery.text)
        self.assertIn("SEC IPO Alerts generated page", sec_alerts.text)
        self.assertIn("IPO Review Outcomes generated page", ipo_reviews.text)
        self.assertIn("ETF Regulatory Holdings generated page", etf.text)
        self.assertIn("Public Document Checks generated page", documents.text)
        self.assertIn("RWA Watch Sandbox generated page", rwa.text)
        self.assertIn("Global Listings Alerts generated page", global_alerts.text)
        self.assertIn("Issuer Confirmations generated page", issuer_confirmations.text)

    def test_serves_only_allowlisted_global_monitor_pages(self) -> None:
        pages = {
            "/dashboard/global-listings": "Global Listings Watch generated page",
            "/dashboard/global/hkex": "HKEX Monitor generated page",
            "/dashboard/global/lse-upcoming": "LSE Upcoming generated page",
            "/dashboard/global/asx": "ASX Monitor generated page",
            "/dashboard/global/tsx": "TSX Monitor generated page",
            "/dashboard/global/jpx": "JPX Monitor generated page",
            "/dashboard/global/edinet": "EDINET Monitor generated page",
            "/dashboard/global/cvm": "CVM Monitor generated page",
            "/dashboard/global/esma": "ESMA Monitor generated page",
            "/dashboard/global/opendart": "OpenDART Monitor generated page",
            "/dashboard/global/sgx": "SGX Monitor generated page",
        }

        for route, marker in pages.items():
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertIn(marker, response.text)

        self.assertEqual(self.client.get("/dashboard/global/not-configured").status_code, 404)

    def test_serves_only_allowlisted_etf_activity_pages(self) -> None:
        pages = {
            "/dashboard/etf/arkk-demo": "ARKK Holdings Sandbox generated page",
            "/dashboard/etf/xlf-demo": "XLF Holdings Sandbox generated page",
            "/dashboard/etf/iyf-demo": "IYF Holdings Sandbox generated page",
            "/dashboard/etf/nport-recent": "N-PORT Recent Filing generated page",
            "/dashboard/etf/nport-catalog": "N-PORT Dataset Catalog generated page",
            "/dashboard/etf/nport-sync": "N-PORT Sync Status generated page",
        }

        for route, marker in pages.items():
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertIn(marker, response.text)

        self.assertEqual(self.client.get("/dashboard/etf/not-configured").status_code, 404)

    def test_serves_only_allowlisted_financials_audit_pages(self) -> None:
        pages = {
            "/dashboard/audit/target-import": "Target Import Audit generated page",
            "/dashboard/audit/adjusted-prices": "Adjusted Price Evidence generated page",
            "/dashboard/audit/corporate-actions": "Corporate Actions Audit generated page",
            "/dashboard/audit/operations-quality": "Operations Quality Snapshot generated page",
            "/dashboard/audit/release-decision": "Release Decision Snapshot generated page",
        }

        for route, marker in pages.items():
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertIn(marker, response.text)

        self.assertEqual(self.client.get("/dashboard/audit/not-configured").status_code, 404)

    def test_serves_only_allowlisted_governance_snapshot_pages(self) -> None:
        pages = {
            "/dashboard/governance-report/open-edition": "Open Edition Snapshot generated page",
            "/dashboard/governance-report/licensed-extensions": "Licensed Extensions Snapshot generated page",
            "/dashboard/governance-report/source-registry": "Source Registry Snapshot generated page",
            "/dashboard/governance-report/provider-approvals": "Provider Approvals Snapshot generated page",
            "/dashboard/governance-report/approval-review": "Approval Review Outcomes generated page",
            "/dashboard/governance-report/scorecard-readiness": "Scorecard Readiness Snapshot generated page",
        }

        for route, marker in pages.items():
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertIn(marker, response.text)

        self.assertEqual(
            self.client.get("/dashboard/governance-report/not-configured").status_code, 404
        )

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
        self.assertEqual(sources.json()["provider_count"], 49)
        self.assertGreater(sources.json()["open_review_count"], 0)
        self.assertEqual(sources.json()["blocked_count"], 6)
        self.assertEqual(
            {item["provider_id"] for item in blocked.json()["sources"]},
            {
                "tipranks-reference",
                "mas-opera-reference",
                "xstocks-backing-api",
                "bybit-xstocks-v5",
                "kraken-xstocks",
                "truth-social-public-content",
            },
        )
        self.assertEqual(len(holdings.json()["sources"]), 3)
        self.assertIn("publication_policy", sources.json()["sources"][0])
        self.assertIn(
            "edinet-offerings",
            {item["provider_id"] for item in sources.json()["sources"]},
        )
        self.assertIn(
            "cvm-equity-offerings",
            {item["provider_id"] for item in sources.json()["sources"]},
        )
        self.assertIn(
            "esma-equity-prospectuses",
            {item["provider_id"] for item in sources.json()["sources"]},
        )
        self.assertIn(
            "opendart-equity-offerings",
            {item["provider_id"] for item in sources.json()["sources"]},
        )
        self.assertIn(
            "mas-opera-reference",
            {item["provider_id"] for item in sources.json()["sources"]},
        )

    def test_serves_evidence_passport_commons_and_machine_readable_registry(self) -> None:
        page = self.client.get("/dashboard/commons")
        passports = self.client.get("/api/v1/commons/passports")

        self.assertEqual(page.status_code, 200)
        self.assertIn("Every signal needs", page.text)
        self.assertIn("Passport Protocol", page.text)
        self.assertIn("/api/v1/commons/passports", page.text)
        self.assertIn("Developer access", page.text)
        self.assertIn("This is raw data, not a visual dashboard page.", page.text)
        self.assertIn('download="marketwitness-evidence-passports.json"', page.text)
        self.assertNotIn("Developer API (JSON)", page.text)
        self.assertIn("/dashboard/contribute?lang=en", page.text)
        self.assertEqual(passports.status_code, 200)
        self.assertEqual(passports.json()["passport_version"], "0.1")
        self.assertEqual(
            passports.json()["protocol_status"],
            "source_and_rights_published_cadence_enrichment_open",
        )
        self.assertEqual(passports.json()["passport_count"], 49)
        self.assertEqual(passports.json()["states"]["blocked"], 6)
        passport = passports.json()["passports"][0]
        self.assertIn("source", passport)
        self.assertIn("rights", passport)
        self.assertIn("publication_policy", passport["rights"])
        self.assertIn("not an investment recommendation", passports.json()["publication_boundary"])

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
            'filename="marketwitness-api-demo-evaluations.csv"',
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
