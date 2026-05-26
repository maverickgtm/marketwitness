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
        self.public_monitor_reports = root / "public-monitor"
        self.public_monitor_reports.mkdir()
        (self.public_monitor_reports / "public-listings-alerts.csv").write_text(
            "observed_on,market,change_type,company_name,previous_status,current_status,previous_detail,current_detail,review_action,source_url\n"
            "2026-05-26,CVM,new,Brasil Systems S.A.,,offering_recorded,,2026-05-25 / Acoes / Primaria,Review new evidence,https://example.invalid/cvm\n"
            "2026-05-26,ESMA,changed,Europe Systems SE,equity_prospectus_review,secondary_issuance_review,Initial offer,Secondary issue,Review changed evidence,https://example.invalid/esma\n",
            encoding="utf-8",
        )
        (self.public_monitor_reports / "public-listings-alerts.html").write_text(
            "<html><h1>Public Listings Change Log generated page</h1></html>",
            encoding="utf-8",
        )
        (self.reports / "whitehouse-events.csv").write_text(
            "event_id,feed,title,published_at,published_on,category,themes,market_relevance,source_mode,observed_on,source_url\n"
            "event-1,news,American Energy Infrastructure,2026-05-25T16:15:00Z,2026-05-25,Fact Sheets,energy,review_candidate,synthetic_fixture,2026-05-25,https://www.whitehouse.gov/fact-sheets/2026/05/energy/\n"
            "event-2,presidential_actions,Financial Technology Innovation,2026-05-21T19:00:00Z,2026-05-21,Presidential Actions,financial_regulation;technology_ai,review_candidate,synthetic_fixture,2026-05-25,https://www.whitehouse.gov/presidential-actions/2026/05/fintech/\n",
            encoding="utf-8",
        )
        (self.reports / "whitehouse-events.html").write_text(
            "<html><h1>White House Official Event Intake generated page</h1></html>",
            encoding="utf-8",
        )
        (self.reports / "treasury-yields.csv").write_text(
            "rate_date,two_year_pct,ten_year_pct,curve_2s10s_bps,source_mode,observed_on,source_url\n"
            "2026-05-22,3.92,4.47,55.00,synthetic_fixture,2026-05-25,https://home.treasury.gov/feed\n"
            "2026-05-25,3.86,4.39,53.00,synthetic_fixture,2026-05-25,https://home.treasury.gov/feed\n",
            encoding="utf-8",
        )
        (self.reports / "treasury-yields.html").write_text(
            "<html><h1>Treasury Yield Context generated page</h1></html>",
            encoding="utf-8",
        )
        (self.reports / "ipo-watch.html").write_text(
            "<html><h1>IPO Watch generated page</h1></html>", encoding="utf-8"
        )
        (self.reports / "ipo-watch-reviewed.csv").write_text(
            "company_name,cik,theme,status,status_date,ticker,exchange,filing_type,evidence_level,source_title,source_url,next_event,risk_flags\n"
            "SpaceX,0001181412,Space infrastructure,filed_public,2026-05-20,,,S-1,Reviewed SEC filing,SEC filing,https://example.invalid/spacex,Review pricing and listing confirmation,review\n"
            "Cerebras,,AI hardware,listed,2026-05-14,CBRS,Nasdaq,IPO,Issuer confirmation,Issuer release,https://example.invalid/cerebras,Track post-IPO filings,new public issuer\n",
            encoding="utf-8",
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
        (self.reports / "global-alerts.csv").write_text(
            "observed_on,market,change_type,company_name,previous_status,current_status,previous_detail,current_detail,review_action,source_url\n"
            "2026-05-25,HKEX,new,EnjoyGo Technology Limited,,active,,PHIP false,Review new evidence,https://example.invalid/hkex\n"
            "2026-05-25,ASX,changed,Boresight Ltd,anticipated,anticipated,June 12,June 10,Review changed evidence,https://example.invalid/asx\n",
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
                public_monitor_reports_path=self.public_monitor_reports,
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
        self.assertTrue(health.json()["public_monitor_reports_available"])
        self.assertTrue(health.json()["policy_monitor_reports_available"])
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
        self.assertEqual(snapshot.json()["zero_cost_available_count"], 7)
        self.assertEqual(snapshot.json()["offline_ready_count"], 2)
        self.assertEqual(snapshot.json()["public_data_ready_count"], 4)
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

    def test_exposes_global_home_navigation_on_all_dashboard_pages(self) -> None:
        pages = [
            "/",
            "/dashboard/open",
            "/dashboard/reports",
            "/dashboard/extensions",
            "/dashboard/ipo",
            "/dashboard/listings-radar",
            "/dashboard/official-change-log",
            "/dashboard/ipo-watch",
            "/dashboard/sec-discovery",
            "/dashboard/sec-alerts",
            "/dashboard/ipo-reviews",
            "/dashboard/etf",
            "/dashboard/financials-evidence",
            "/dashboard/etf-regulatory",
            "/dashboard/etf/arkk-demo",
            "/dashboard/etf/xlf-demo",
            "/dashboard/etf/iyf-demo",
            "/dashboard/etf/nport-recent",
            "/dashboard/etf/nport-catalog",
            "/dashboard/etf/nport-sync",
            "/dashboard/document-checks",
            "/dashboard/rwa-watch",
            "/dashboard/global-alerts",
            "/dashboard/issuer-confirmations",
            "/dashboard/global-listings",
            "/dashboard/contribute?lang=en",
            "/dashboard/commons",
            "/dashboard/global/hkex",
            "/dashboard/global/lse-upcoming",
            "/dashboard/global/asx",
            "/dashboard/global/tsx",
            "/dashboard/global/jpx",
            "/dashboard/global/edinet",
            "/dashboard/global/cvm",
            "/dashboard/global/esma",
            "/dashboard/global/opendart",
            "/dashboard/global/sgx",
            "/dashboard/audit/target-import",
            "/dashboard/audit/adjusted-prices",
            "/dashboard/audit/corporate-actions",
            "/dashboard/audit/operations-quality",
            "/dashboard/audit/release-decision",
            "/dashboard/governance-report/open-edition",
            "/dashboard/governance-report/licensed-extensions",
            "/dashboard/governance-report/source-registry",
            "/dashboard/governance-report/provider-approvals",
            "/dashboard/governance-report/approval-review",
            "/dashboard/governance-report/scorecard-readiness",
            "/dashboard/market-context",
            "/dashboard/intelligence",
            "/dashboard/volatility",
            "/dashboard/policy-signals",
            "/dashboard/presidential-impact",
            "/dashboard/financials",
            "/dashboard/governance",
            "/dashboard/operations",
            "/dashboard/readiness",
            "/dashboard/release",
            "/dashboard/approvals",
            "/dashboard/policy",
        ]

        for route in pages:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertIn('class="mw-global-navigation"', response.text)
                self.assertIn('href="/dashboard/open"', response.text)
                self.assertIn('href="/dashboard/reports"', response.text)

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
        self.assertIn("Official document metadata may be loaded", snapshot.json()["publication_boundary"])
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
        self.assertIn("Choose the study period", page.text)
        self.assertIn("Apply dates", page.text)
        self.assertIn("Study period", page.text)
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
        filtered = self.client.get(
            "/api/v1/intelligence/volatility?start=2026-01-01&end=2026-05-25"
        )
        self.assertEqual(filtered.status_code, 200)
        self.assertEqual(
            filtered.json()["reaction_explorer"]["validation_sample"]["episode_count"], 2
        )
        self.assertEqual(
            filtered.json()["reaction_explorer"]["validation_sample"]["period"]["episode_dates"],
            ["2026-02-02", "2026-04-06"],
        )

    def test_serves_policy_signal_lab_with_truth_social_collection_disabled(self) -> None:
        page = self.client.get("/dashboard/presidential-impact")
        legacy_page = self.client.get("/dashboard/policy-signals")
        snapshot = self.client.get("/api/v1/intelligence/policy-signals")
        events = self.client.get("/api/v1/intelligence/policy-events")
        treasury = self.client.get("/api/v1/intelligence/policy-treasury-context")
        treasury_report = self.client.get("/dashboard/presidential-impact/treasury-report")
        reactions = self.client.get("/api/v1/intelligence/policy-reactions")
        filtered_reactions = self.client.get(
            "/api/v1/intelligence/policy-reactions?theme=financial_regulation&start=2025-01-20&end=2026-05-25"
        )
        exported = self.client.get("/api/v1/intelligence/policy-events/export.csv")
        report = self.client.get("/dashboard/presidential-impact/events-report")

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
        self.assertEqual(snapshot.json()["official_intake_status"], "implemented_optional_artifact")
        self.assertIn("prohibit automated access", snapshot.json()["publication_boundary"])
        self.assertIn("JPMorgan Volfefe Index", {item["name"] for item in snapshot.json()["prior_art"]})
        self.assertIn("Authorized Intake Map", page.text)
        self.assertIn("Communication Reaction Sandbox", page.text)
        self.assertIn("Synthetic validation only", page.text)
        self.assertIn("/api/v1/intelligence/policy-reactions", page.text)
        self.assertIn("Observed Treasury Context", page.text)
        self.assertIn("/api/v1/intelligence/policy-treasury-context", page.text)
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
        self.assertIn("Official Event Intake Queue", page.text)
        self.assertIn("Show all ${selected.length} archived events", page.text)
        self.assertIn("/api/v1/intelligence/policy-events", page.text)
        self.assertEqual(events.status_code, 200)
        self.assertTrue(events.json()["available"])
        self.assertEqual(events.json()["data_mode"], "Synthetic reproducible RSS fixture")
        self.assertEqual(events.json()["record_count"], 2)
        self.assertIn("does not collect Truth Social", events.json()["publication_boundary"])
        self.assertEqual(treasury.status_code, 200)
        self.assertTrue(treasury.json()["available"])
        self.assertEqual(treasury.json()["latest_rate_date"], "2026-05-25")
        self.assertEqual(treasury.json()["measured_event_count"], 1)
        self.assertEqual(treasury.json()["records"][0]["two_year_change_bps"], "-6.00")
        self.assertIn("after publication", treasury.json()["measurement"])
        self.assertIn("do not prove", treasury.json()["publication_boundary"])
        self.assertEqual(treasury_report.status_code, 200)
        self.assertIn("Treasury Yield Context generated page", treasury_report.text)
        self.assertEqual(reactions.status_code, 200)
        self.assertEqual(reactions.json()["episode_count"], 6)
        self.assertEqual(reactions.json()["mode"], "project_authored_not_market_observations")
        self.assertIn("not assigned", reactions.json()["boundary"])
        self.assertEqual(filtered_reactions.status_code, 200)
        self.assertEqual(filtered_reactions.json()["episode_count"], 2)
        self.assertEqual(
            filtered_reactions.json()["selected_theme"]["key"], "financial_regulation"
        )
        self.assertEqual(exported.status_code, 200)
        self.assertIn("Financial Technology Innovation", exported.text)
        self.assertEqual(report.status_code, 200)
        self.assertIn("White House Official Event Intake generated page", report.text)

    def test_serves_allowlisted_report_center_for_periodic_bundle(self) -> None:
        page = self.client.get("/dashboard/reports")

        self.assertEqual(page.status_code, 200)
        self.assertIn("Reproducible reports.", page.text)
        self.assertIn("Known routes only.", page.text)
        self.assertIn("28 allowlisted pages", page.text)
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
        self.assertIn("/dashboard/official-change-log", page.text)
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
        self.assertIn("Open Listings Radar", page.text)
        self.assertIn("/dashboard/listings-radar", page.text)
        self.assertIn("Official Change Log", page.text)
        self.assertIn("/dashboard/official-change-log", page.text)

    def test_serves_filterable_listings_radar_with_evidence_queue(self) -> None:
        page = self.client.get("/dashboard/listings-radar")
        all_records = self.client.get("/api/v1/listings/radar")
        filtered = self.client.get(
            "/api/v1/listings/radar?stream=global_changes&market=HKEX&start=2026-05-25&end=2026-05-25"
        )
        searched = self.client.get("/api/v1/listings/radar?query=SpaceX")
        exported = self.client.get(
            "/api/v1/listings/radar/export.csv?stream=global_changes&market=HKEX"
        )

        self.assertEqual(page.status_code, 200)
        self.assertIn("Listings Radar", page.text)
        self.assertIn("My Watchlist", page.text)
        self.assertIn("Monitor Status", page.text)
        self.assertIn("Official-source activation", page.text)
        self.assertIn("Export filtered CSV", page.text)
        self.assertIn("Re-read evidence", page.text)
        self.assertIn("Apply filters", page.text)
        self.assertIn("localStorage", page.text)
        self.assertEqual(all_records.status_code, 200)
        self.assertEqual(all_records.json()["record_count"], 4)
        self.assertEqual(all_records.json()["ipo_watch_count"], 2)
        self.assertEqual(all_records.json()["global_change_count"], 2)
        self.assertEqual(
            all_records.json()["operations"]["collection_status"],
            "Scheduled artifact / not live collection",
        )
        self.assertEqual(all_records.json()["operations"]["market_count"], 4)
        self.assertEqual(
            all_records.json()["operations"]["automatic_refresh"],
            "Mondays at 12:17 UTC via GitHub Actions",
        )
        self.assertEqual(
            all_records.json()["operations"]["official_monitor_refresh"],
            "Weekdays at 11:23 UTC / CVM and ESMA retained change log artifact",
        )
        self.assertEqual(all_records.json()["operations"]["automated_market_count"], 2)
        controls = {
            item["market"]: item
            for item in all_records.json()["operations"]["automation_controls"]
        }
        self.assertEqual(controls["CVM"]["activation_state"], "weekdays_official_capture")
        self.assertEqual(controls["ESMA"]["activation_state"], "weekdays_official_capture")
        self.assertEqual(
            controls["US"]["activation_state"], "operator_configuration_required"
        )
        self.assertEqual(controls["MOEX"]["activation_state"], "restricted_research_only")
        self.assertEqual(filtered.json()["record_count"], 1)
        self.assertEqual(
            filtered.json()["records"][0]["company_name"],
            "EnjoyGo Technology Limited",
        )
        self.assertEqual(searched.json()["record_count"], 1)
        self.assertEqual(searched.json()["records"][0]["status"], "filed_public")
        self.assertEqual(exported.status_code, 200)
        self.assertIn("text/csv", exported.headers["content-type"])
        self.assertIn("marketwitness-listings-radar.csv", exported.headers["content-disposition"])
        self.assertIn("EnjoyGo Technology Limited", exported.text)
        self.assertNotIn("Boresight Ltd", exported.text)

    def test_serves_official_public_change_log_artifact_without_trade_claims(self) -> None:
        page = self.client.get("/dashboard/official-change-log")
        snapshot = self.client.get("/api/v1/listings/public-change-log")
        exported = self.client.get("/api/v1/listings/public-change-log/export.csv")
        report = self.client.get("/dashboard/official-change-log/report")

        self.assertEqual(page.status_code, 200)
        self.assertIn("Official Change Log", page.text)
        self.assertIn("No official artifact loaded here yet", page.text)
        self.assertIn("/api/v1/listings/public-change-log", page.text)
        self.assertTrue(snapshot.json()["available"])
        self.assertEqual(snapshot.json()["collection_scope"], "CVM and ESMA only")
        self.assertEqual(snapshot.json()["observation_date"], "2026-05-26")
        self.assertEqual(snapshot.json()["new_count"], 1)
        self.assertEqual(snapshot.json()["changed_count"], 1)
        self.assertIn("do not confirm listing", snapshot.json()["publication_boundary"])
        self.assertEqual(exported.status_code, 200)
        self.assertIn("Brasil Systems S.A.", exported.text)
        self.assertEqual(report.status_code, 200)
        self.assertIn("Public Listings Change Log generated page", report.text)

    def test_reports_when_no_official_public_change_log_artifact_is_loaded(self) -> None:
        from fastapi.testclient import TestClient

        from marketwitness.api import create_app

        missing_public_monitor_reports = Path(self.directory.name) / "missing-public-monitor"
        client = TestClient(
            create_app(
                self.database,
                Path("data/samples/source_registry.csv"),
                Path("data/samples/provider_approval_queue.csv"),
                self.reports,
                public_monitor_reports_path=missing_public_monitor_reports,
            )
        )

        snapshot = client.get("/api/v1/listings/public-change-log")
        exported = client.get("/api/v1/listings/public-change-log/export.csv")

        self.assertEqual(snapshot.status_code, 200)
        self.assertFalse(snapshot.json()["available"])
        self.assertIn("No official monitoring artifact", snapshot.json()["message"])
        self.assertEqual(exported.status_code, 404)

    def test_reports_when_no_presidential_event_artifact_is_loaded(self) -> None:
        from fastapi.testclient import TestClient

        from marketwitness.api import create_app

        missing_policy_monitor_reports = Path(self.directory.name) / "missing-policy-monitor"
        client = TestClient(
            create_app(
                self.database,
                Path("data/samples/source_registry.csv"),
                Path("data/samples/provider_approval_queue.csv"),
                self.reports,
                policy_monitor_reports_path=missing_policy_monitor_reports,
            )
        )

        snapshot = client.get("/api/v1/intelligence/policy-events")
        exported = client.get("/api/v1/intelligence/policy-events/export.csv")

        self.assertEqual(snapshot.status_code, 200)
        self.assertFalse(snapshot.json()["available"])
        self.assertIn("No official event-intake artifact", snapshot.json()["message"])
        self.assertEqual(exported.status_code, 404)

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
