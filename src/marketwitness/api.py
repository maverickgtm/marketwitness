from __future__ import annotations

import csv
import io
import os
import re
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path
from statistics import median
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response

from . import METHODOLOGY_VERSION, __version__
from .dashboard_web import (
    evidence_commons_html,
    etf_evidence_center_html,
    financials_evidence_center_html,
    financials_scorecard_html,
    global_contributors_html,
    ipo_watch_center_html,
    licensed_extensions_html,
    listings_radar_html,
    macro_calendar_html,
    cot_positioning_html,
    insider_activity_html,
    market_intelligence_html,
    market_context_html,
    open_edition_html,
    operations_quality_html,
    official_change_log_html,
    policy_signal_lab_html,
    provider_approvals_html,
    public_use_policy_html,
    report_center_html,
    release_center_html,
    scorecard_readiness_html,
    source_governance_html,
    volatility_lab_html,
)
from .licensed_extensions import (
    LicensedExtensionDataError,
    build_licensed_extensions_snapshot,
    load_licensed_extensions,
)
from .models import Evaluation
from .market_intelligence import build_market_intelligence_snapshot
from .open_edition import build_open_edition_snapshot
from .operations_quality import build_quality_snapshot
from .policy_reaction import build_policy_reaction_snapshot
from .policy_signal_lab import build_policy_signal_lab_snapshot
from .policy_treasury import build_policy_treasury_context
from .providers.treasury import TreasuryDataError, load_treasury_csv
from .providers.macro_calendar import (
    MacroCalendarDataError,
    build_macro_calendar_snapshot,
    load_macro_calendar_csv,
)
from .providers.cftc import CftcDataError, build_cftc_snapshot, load_cftc_csv
from .providers.sec_insider import (
    SecInsiderDataError,
    build_insider_snapshot,
    load_insider_csv,
)
from .providers.whitehouse import WhiteHouseDataError, load_event_archive
from .provider_approvals import (
    ProviderApprovalDataError,
    build_approval_queue,
    load_provider_approvals,
)
from .public_policy import build_public_use_policy
from .release_center import build_release_decision
from .reporting import wilson_interval
from .scorecard_readiness import build_scorecard_readiness
from .source_registry import SourceProvider, SourceRegistryDataError, load_source_registry
from .storage import (
    WarehouseError,
    list_run_summaries,
    read_evaluations,
    read_run_assets,
    read_run_summary,
)
from .treasury_regimes import build_treasury_regime_snapshot
from .volatility_lab import build_volatility_lab_snapshot

DEFAULT_DATABASE_PATH = "build/live/marketwitness.duckdb"
DEFAULT_SOURCE_REGISTRY_PATH = "data/samples/source_registry.csv"
DEFAULT_PROVIDER_APPROVALS_PATH = "data/samples/provider_approval_queue.csv"
DEFAULT_GENERATED_REPORTS_PATH = "build/demo"
DEFAULT_PUBLIC_MONITOR_REPORTS_PATH = "build/public-monitor"
DEFAULT_LICENSED_EXTENSIONS_PATH = "data/samples/licensed_extensions.csv"
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="#38dfad"/><stop offset="1" stop-color="#25a9db"/></linearGradient></defs>
<rect width="64" height="64" rx="18" fill="url(#g)"/>
<path fill="#061117" d="M14 17h9l9 17 9-17h9v30h-8V31l-7 13h-6l-7-13v16h-8z"/>
</svg>"""
GLOBAL_MONITOR_REPORTS = {
    "hkex": "hkex-monitor.html",
    "lse-upcoming": "lse-upcoming.html",
    "asx": "asx-monitor.html",
    "tsx": "tsx-monitor.html",
    "jpx": "jpx-monitor.html",
    "edinet": "edinet-monitor.html",
    "cvm": "cvm-monitor.html",
    "esma": "esma-monitor.html",
    "opendart": "opendart-monitor.html",
    "sgx": "sgx-monitor.html",
}
ETF_ACTIVITY_REPORTS = {
    "arkk-demo": "etf-holdings-ark-activity.html",
    "xlf-demo": "etf-holdings-activity.html",
    "iyf-demo": "etf-holdings-iyf-activity.html",
    "nport-recent": "etf-holdings-regulatory-activity.html",
    "nport-catalog": "nport-dataset-catalog.html",
    "nport-sync": "nport-sync.html",
}
LISTING_AUTOMATION_CONTROLS = (
    ("CVM", "Brazil CVM", "cvm-equity-offerings", "weekdays_official_capture"),
    ("ESMA", "European Union", "esma-equity-prospectuses", "weekdays_official_capture"),
    ("US", "SEC EDGAR", "sec-edgar", "operator_configuration_required"),
    ("LSE", "London Stock Exchange", "lse-new-issues", "rights_review_required"),
    ("HKEX", "Hong Kong Exchange", "hkex-news", "rights_review_required"),
    ("ASX", "Australian Securities Exchange", "asx-upcoming", "rights_review_required"),
    ("TSX", "Toronto Stock Exchange", "tsx-listings", "rights_review_required"),
    ("SGX", "Singapore Exchange", "sgx-prospectus", "rights_review_required"),
    ("JPX", "Tokyo Stock Exchange", "jpx-new-listings", "rights_review_required"),
    ("KRX", "South Korea OpenDART", "opendart-equity-offerings", "rights_review_required"),
)
FINANCIALS_AUDIT_REPORTS = {
    "target-import": "authorized-targets-import.html",
    "adjusted-prices": "alpha-vantage-prices.html",
    "corporate-actions": "corporate-actions.html",
    "operations-quality": "operations-quality.html",
    "release-decision": "scorecard-release.html",
}
GOVERNANCE_SNAPSHOT_REPORTS = {
    "open-edition": "open-edition.html",
    "licensed-extensions": "licensed-extensions.html",
    "source-registry": "source-registry.html",
    "provider-approvals": "provider-approvals.html",
    "approval-review": "provider-approval-review-outcomes.html",
    "scorecard-readiness": "scorecard-readiness.html",
}
GLOBAL_NAV_MARKER = "mw-global-navigation"
GLOBAL_NAV_STYLE = """
<style id="mw-global-navigation-style">
  body { padding-bottom:76px !important; }
  .mw-global-navigation { position:fixed; z-index:10000; right:20px; bottom:20px;
    display:flex; gap:9px; padding:7px; border:1px solid rgba(122,154,185,.25);
    border-radius:14px; background:rgba(8,14,23,.92); backdrop-filter:blur(14px);
    box-shadow:0 16px 42px rgba(0,0,0,.3); font:600 13px/1.2 Inter,-apple-system,
    BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; }
  .mw-global-navigation a { display:inline-flex; align-items:center; gap:7px;
    border-radius:9px; padding:10px 13px; color:#adbecb !important;
    text-decoration:none !important; border:1px solid transparent; }
  .mw-global-navigation a:first-child { color:#071016 !important;
    background:#38dfad; }
  .mw-global-navigation a:last-child { border-color:rgba(122,154,185,.2); }
  .mw-global-navigation a:focus-visible { outline:2px solid #62a6ff;
    outline-offset:2px; }
  @media (max-width:700px) {
    body { padding-bottom:82px !important; }
    .mw-global-navigation { left:12px; right:12px; bottom:12px; }
    .mw-global-navigation a { flex:1; justify-content:center; }
  }
</style>
"""
GLOBAL_NAV_HTML = """
<nav class="mw-global-navigation" aria-label="Global application navigation">
  <a href="/dashboard/open" aria-label="Return to MarketWitness home">Home</a>
  <a href="/dashboard/reports">All views</a>
</nav>
"""


def create_app(
    database_path: str | Path | None = None,
    source_registry_path: str | Path | None = None,
    provider_approvals_path: str | Path | None = None,
    generated_reports_path: str | Path | None = None,
    licensed_extensions_path: str | Path | None = None,
    public_monitor_reports_path: str | Path | None = None,
    policy_monitor_reports_path: str | Path | None = None,
) -> FastAPI:
    database = Path(
        database_path or os.environ.get("MARKETWITNESS_DATABASE", DEFAULT_DATABASE_PATH)
    )
    registry = Path(
        source_registry_path
        or os.environ.get("MARKETWITNESS_SOURCE_REGISTRY", DEFAULT_SOURCE_REGISTRY_PATH)
    )
    approval_queue = Path(
        provider_approvals_path
        or os.environ.get("MARKETWITNESS_PROVIDER_APPROVALS", DEFAULT_PROVIDER_APPROVALS_PATH)
    )
    reports = Path(
        generated_reports_path
        or os.environ.get("MARKETWITNESS_GENERATED_REPORTS", DEFAULT_GENERATED_REPORTS_PATH)
    )
    licensed_extensions = Path(
        licensed_extensions_path
        or os.environ.get("MARKETWITNESS_LICENSED_EXTENSIONS", DEFAULT_LICENSED_EXTENSIONS_PATH)
    )
    public_monitor_reports = Path(
        public_monitor_reports_path
        or os.environ.get(
            "MARKETWITNESS_PUBLIC_MONITOR_REPORTS", DEFAULT_PUBLIC_MONITOR_REPORTS_PATH
        )
    )
    policy_monitor_reports = Path(
        policy_monitor_reports_path
        or os.environ.get("MARKETWITNESS_POLICY_MONITOR_REPORTS", reports)
    )
    application = FastAPI(
        title="MarketWitness API",
        version=__version__,
        description=(
            "Read-only API for evidence-first market intelligence workflows "
            "and auditable research artifacts."
        ),
    )

    @application.get("/", response_class=HTMLResponse, include_in_schema=False)
    def open_home() -> str:
        return _dashboard_html(open_edition_html())

    @application.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        return Response(
            content=FAVICON_SVG,
            media_type="image/svg+xml",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    @application.get(
        "/dashboard/open", response_class=HTMLResponse, include_in_schema=False
    )
    def open_edition() -> str:
        return _dashboard_html(open_edition_html())

    @application.get(
        "/dashboard/reports", response_class=HTMLResponse, include_in_schema=False
    )
    def report_center() -> str:
        return _dashboard_html(report_center_html())

    @application.get(
        "/dashboard/extensions", response_class=HTMLResponse, include_in_schema=False
    )
    def licensed_extension_page() -> str:
        return _dashboard_html(licensed_extensions_html())

    @application.get(
        "/dashboard/ipo", response_class=HTMLResponse, include_in_schema=False
    )
    def ipo_watch_center() -> str:
        return _dashboard_html(ipo_watch_center_html())

    @application.get(
        "/dashboard/listings-radar", response_class=HTMLResponse, include_in_schema=False
    )
    def listings_radar_page() -> str:
        return _dashboard_html(listings_radar_html())

    @application.get(
        "/dashboard/official-change-log", response_class=HTMLResponse, include_in_schema=False
    )
    def official_change_log_page() -> str:
        return _dashboard_html(official_change_log_html())

    @application.get(
        "/dashboard/ipo-watch", response_class=HTMLResponse, include_in_schema=False
    )
    def ipo_watch_report() -> str:
        return _generated_html(reports, "ipo-watch.html")

    @application.get(
        "/dashboard/sec-discovery", response_class=HTMLResponse, include_in_schema=False
    )
    def sec_discovery_report() -> str:
        return _generated_html(reports, "sec-ipo-discovery.html")

    @application.get(
        "/dashboard/sec-alerts", response_class=HTMLResponse, include_in_schema=False
    )
    def sec_alerts_report() -> str:
        return _generated_html(reports, "sec-alerts.html")

    @application.get(
        "/dashboard/ipo-reviews", response_class=HTMLResponse, include_in_schema=False
    )
    def ipo_reviews_report() -> str:
        return _generated_html(reports, "sec-review-outcomes.html")

    @application.get(
        "/dashboard/etf", response_class=HTMLResponse, include_in_schema=False
    )
    def etf_evidence_center() -> str:
        return _dashboard_html(etf_evidence_center_html())

    @application.get(
        "/dashboard/financials-evidence", response_class=HTMLResponse, include_in_schema=False
    )
    def financials_evidence_center() -> str:
        return _dashboard_html(financials_evidence_center_html())

    @application.get(
        "/dashboard/etf-regulatory", response_class=HTMLResponse, include_in_schema=False
    )
    def etf_regulatory_report() -> str:
        return _generated_html(reports, "etf-holdings-regulatory-history.html")

    @application.get(
        "/dashboard/etf/{view}", response_class=HTMLResponse, include_in_schema=False
    )
    def etf_activity_report(view: str) -> str:
        filename = ETF_ACTIVITY_REPORTS.get(view)
        if filename is None:
            raise HTTPException(
                status_code=404, detail="ETF activity report is not allowlisted."
            )
        return _generated_html(reports, filename)

    @application.get(
        "/dashboard/document-checks", response_class=HTMLResponse, include_in_schema=False
    )
    def document_checks_report() -> str:
        return _generated_html(reports, "lse-fca-check.html")

    @application.get(
        "/dashboard/rwa-watch", response_class=HTMLResponse, include_in_schema=False
    )
    def rwa_watch_report() -> str:
        return _generated_html(reports, "rwa-watch.html")

    @application.get(
        "/dashboard/global-alerts", response_class=HTMLResponse, include_in_schema=False
    )
    def global_listing_alerts_report() -> str:
        return _generated_html(reports, "global-alerts.html")

    @application.get(
        "/dashboard/issuer-confirmations", response_class=HTMLResponse, include_in_schema=False
    )
    def issuer_confirmations_report() -> str:
        return _generated_html(reports, "issuer-confirmations.html")

    @application.get(
        "/dashboard/global-listings", response_class=HTMLResponse, include_in_schema=False
    )
    def global_listings_report() -> str:
        return _generated_html(reports, "global-listings.html")

    @application.get(
        "/dashboard/contribute", response_class=HTMLResponse, include_in_schema=False
    )
    def global_contributors(lang: str = Query(default="en", max_length=10)) -> str:
        return _dashboard_html(global_contributors_html(lang))

    @application.get(
        "/dashboard/commons", response_class=HTMLResponse, include_in_schema=False
    )
    def evidence_commons() -> str:
        return _dashboard_html(evidence_commons_html())

    @application.get(
        "/dashboard/global/{monitor}", response_class=HTMLResponse, include_in_schema=False
    )
    def global_monitor_report(monitor: str) -> str:
        filename = GLOBAL_MONITOR_REPORTS.get(monitor)
        if filename is None:
            raise HTTPException(
                status_code=404, detail="Global monitor report is not allowlisted."
            )
        return _generated_html(reports, filename)

    @application.get(
        "/dashboard/audit/{report}", response_class=HTMLResponse, include_in_schema=False
    )
    def financials_audit_report(report: str) -> str:
        filename = FINANCIALS_AUDIT_REPORTS.get(report)
        if filename is None:
            raise HTTPException(
                status_code=404, detail="Financials audit report is not allowlisted."
            )
        return _generated_html(reports, filename)

    @application.get(
        "/dashboard/governance-report/{snapshot}",
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    def governance_snapshot_report(snapshot: str) -> str:
        filename = GOVERNANCE_SNAPSHOT_REPORTS.get(snapshot)
        if filename is None:
            raise HTTPException(
                status_code=404, detail="Governance snapshot report is not allowlisted."
            )
        return _generated_html(reports, filename)

    @application.get(
        "/dashboard/market-context", response_class=HTMLResponse, include_in_schema=False
    )
    def market_context_page() -> str:
        return _dashboard_html(market_context_html())

    @application.get(
        "/dashboard/intelligence", response_class=HTMLResponse, include_in_schema=False
    )
    def market_intelligence_page() -> str:
        return _dashboard_html(market_intelligence_html())

    @application.get(
        "/dashboard/macro-calendar", response_class=HTMLResponse, include_in_schema=False
    )
    def macro_calendar_page() -> str:
        return _dashboard_html(macro_calendar_html())

    @application.get(
        "/dashboard/cot-positioning", response_class=HTMLResponse, include_in_schema=False
    )
    def cot_positioning_page() -> str:
        return _dashboard_html(cot_positioning_html())

    @application.get(
        "/dashboard/insider-activity", response_class=HTMLResponse, include_in_schema=False
    )
    def insider_activity_page() -> str:
        return _dashboard_html(insider_activity_html())

    @application.get(
        "/dashboard/volatility", response_class=HTMLResponse, include_in_schema=False
    )
    def volatility_lab_page() -> str:
        return _dashboard_html(volatility_lab_html())

    @application.get(
        "/dashboard/policy-signals", response_class=HTMLResponse, include_in_schema=False
    )
    def policy_signal_lab_page() -> str:
        return _dashboard_html(policy_signal_lab_html())

    @application.get(
        "/dashboard/presidential-impact", response_class=HTMLResponse, include_in_schema=False
    )
    def presidential_impact_lab_page() -> str:
        return _dashboard_html(policy_signal_lab_html())

    @application.get(
        "/dashboard/financials", response_class=HTMLResponse, include_in_schema=False
    )
    def scorecard() -> str:
        return _dashboard_html(financials_scorecard_html())

    @application.get(
        "/dashboard/governance", response_class=HTMLResponse, include_in_schema=False
    )
    def source_governance() -> str:
        return _dashboard_html(source_governance_html())

    @application.get(
        "/dashboard/operations", response_class=HTMLResponse, include_in_schema=False
    )
    def operations_quality() -> str:
        return _dashboard_html(operations_quality_html())

    @application.get(
        "/dashboard/readiness", response_class=HTMLResponse, include_in_schema=False
    )
    def scorecard_readiness() -> str:
        return _dashboard_html(scorecard_readiness_html())

    @application.get(
        "/dashboard/release", response_class=HTMLResponse, include_in_schema=False
    )
    def release_center() -> str:
        return _dashboard_html(release_center_html())

    @application.get(
        "/dashboard/approvals", response_class=HTMLResponse, include_in_schema=False
    )
    def provider_approval_page() -> str:
        return _dashboard_html(provider_approvals_html())

    @application.get(
        "/dashboard/policy", response_class=HTMLResponse, include_in_schema=False
    )
    def public_policy_page() -> str:
        return _dashboard_html(public_use_policy_html())

    @application.get("/api/v1/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "service": "marketwitness-api",
            "methodology_version": METHODOLOGY_VERSION,
            "database_available": database.is_file(),
            "source_registry_available": registry.is_file(),
            "provider_approvals_available": approval_queue.is_file(),
            "generated_reports_available": reports.is_dir(),
            "licensed_extensions_available": licensed_extensions.is_file(),
            "public_monitor_reports_available": public_monitor_reports.is_dir(),
            "policy_monitor_reports_available": policy_monitor_reports.is_dir(),
        }

    @application.get("/api/v1/governance/sources")
    def governance_sources(
        deployment_state: str = "",
        data_class: str = "",
    ) -> dict[str, object]:
        providers = _read_sources(registry)
        all_providers = providers
        if deployment_state:
            providers = [
                item for item in providers if item.deployment_state == deployment_state
            ]
        if data_class:
            providers = [
                item for item in providers if item.data_class.lower() == data_class.lower()
            ]
        deployment = Counter(item.deployment_state for item in all_providers)
        integration = Counter(item.integration_status for item in all_providers)
        return {
            "reviewed_as_of": max(item.reviewed_on for item in all_providers).isoformat()
            if all_providers
            else None,
            "provider_count": len(all_providers),
            "implemented_count": integration["implemented"],
            "open_review_count": (
                deployment["review_required"] + deployment["license_required"]
            ),
            "manual_only_count": deployment["manual_only"],
            "blocked_count": deployment["blocked"],
            "deployment_states": sorted({item.deployment_state for item in all_providers}),
            "data_classes": sorted({item.data_class for item in all_providers}),
            "sources": [_public_source(item) for item in providers],
        }

    @application.get("/api/v1/commons/passports")
    def evidence_passports() -> dict[str, object]:
        providers = _read_sources(registry)
        states = Counter(item.deployment_state for item in providers)
        return {
            "passport_version": "0.1",
            "protocol_status": "source_and_rights_published_cadence_enrichment_open",
            "reviewed_as_of": max(item.reviewed_on for item in providers).isoformat()
            if providers
            else None,
            "passport_count": len(providers),
            "states": dict(states),
            "publication_boundary": (
                "A passport documents available evidence and output rights; "
                "it is not an investment recommendation or listing confirmation."
            ),
            "passports": [_evidence_passport(item) for item in providers],
        }

    @application.get("/api/v1/readiness/scorecard")
    def readiness_scorecard() -> dict[str, object]:
        providers = _read_sources(registry)
        try:
            as_of = max((item.reviewed_on for item in providers), default=date.today())
            return build_scorecard_readiness(providers, as_of)
        except SourceRegistryDataError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @application.get("/api/v1/open-edition")
    def open_edition_snapshot() -> dict[str, object]:
        providers = _read_sources(registry)
        try:
            as_of = max((item.reviewed_on for item in providers), default=date.today())
            return build_open_edition_snapshot(providers, as_of)
        except SourceRegistryDataError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @application.get("/api/v1/listings/radar")
    def listings_radar_snapshot(
        query: str = "",
        stream: str = Query(default="", pattern="^(|ipo_watch|global_changes)$"),
        market: str = "",
        status: str = "",
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> dict[str, object]:
        if start and end and start > end:
            raise HTTPException(status_code=422, detail="Start date must be on or before end date.")
        all_rows = _read_listing_radar_rows(reports)
        selected = _filter_listing_radar_rows(
            all_rows, query, stream, market, status, start, end
        )
        latest_evidence = max((str(item["event_date"]) for item in all_rows), default=None)
        automation_controls = _listing_automation_controls(_read_sources(registry))
        return {
            "as_of": latest_evidence,
            "record_count": len(selected),
            "total_record_count": len(all_rows),
            "ipo_watch_count": sum(item["stream"] == "ipo_watch" for item in selected),
            "global_change_count": sum(item["stream"] == "global_changes" for item in selected),
            "review_required_count": sum(
                item["stream"] == "global_changes"
                or item["status"] in {"candidate_unverified", "filed_public"}
                for item in selected
            ),
            "markets": sorted({str(item["market"]) for item in all_rows}),
            "statuses": sorted({str(item["status"]) for item in all_rows}),
            "publication_boundary": (
                "Records are evidence-review tasks and verified milestones, not investment "
                "recommendations or confirmation of trading unless the cited evidence states it."
            ),
            "operations": {
                "data_mode": "Reproducible fixture bundle",
                "collection_status": "Scheduled artifact / not live collection",
                "latest_evidence_date": latest_evidence,
                "automatic_refresh": "Mondays at 12:17 UTC via GitHub Actions",
                "official_monitor_refresh": (
                    "Weekdays at 11:23 UTC / CVM and ESMA retained change log artifact"
                ),
                "manual_refresh": "Run make verify to rebuild the local evidence bundle",
                "market_count": len({str(item["market"]) for item in all_rows}),
                "streams": [
                    {
                        "name": "U.S. IPO Watch",
                        "record_count": sum(
                            item["stream"] == "ipo_watch" for item in all_rows
                        ),
                    },
                    {
                        "name": "Global changes",
                        "record_count": sum(
                            item["stream"] == "global_changes" for item in all_rows
                        ),
                    },
                ],
                "automation_controls": automation_controls,
                "automated_market_count": sum(
                    item["activation_state"] == "weekdays_official_capture"
                    for item in automation_controls
                ),
            },
            "records": selected,
        }

    @application.get("/api/v1/listings/radar/export.csv")
    def listings_radar_export(
        query: str = "",
        stream: str = Query(default="", pattern="^(|ipo_watch|global_changes)$"),
        market: str = "",
        status: str = "",
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> Response:
        if start and end and start > end:
            raise HTTPException(status_code=422, detail="Start date must be on or before end date.")
        selected = _filter_listing_radar_rows(
            _read_listing_radar_rows(reports), query, stream, market, status, start, end
        )
        output = io.StringIO()
        fieldnames = [
            "event_date",
            "stream",
            "market",
            "company_name",
            "status",
            "detail",
            "next_action",
            "evidence_level",
            "source_url",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(selected)
        return Response(
            output.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": 'attachment; filename="marketwitness-listings-radar.csv"'
            },
        )

    @application.get("/api/v1/listings/public-change-log")
    def public_listings_change_log() -> dict[str, object]:
        csv_path = public_monitor_reports / "public-listings-alerts.csv"
        if not csv_path.is_file():
            return {
                "available": False,
                "data_mode": "Official weekday artifact",
                "collection_scope": "CVM and ESMA only",
                "schedule": "Weekdays at 11:23 UTC via GitHub Actions",
                "message": (
                    "No official monitoring artifact is loaded in this runtime. "
                    "Download an artifact from GitHub Actions or run the permitted "
                    "CVM/ESMA monitoring workflow locally."
                ),
                "records": [],
            }
        rows = _read_public_change_log_rows(csv_path)
        observation_date = max(
            (str(item["observed_on"]) for item in rows), default=None
        )
        counts = Counter(str(item["change_type"]) for item in rows)
        return {
            "available": True,
            "data_mode": "Official weekday artifact",
            "collection_scope": "CVM and ESMA only",
            "schedule": "Weekdays at 11:23 UTC via GitHub Actions",
            "observation_date": observation_date,
            "record_count": len(rows),
            "new_count": counts["new"],
            "changed_count": counts["changed"],
            "review_removal_count": counts["removed_from_feed_review"],
            "markets": sorted({str(item["market"]) for item in rows}),
            "publication_boundary": (
                "Changes are review tasks from official offering or prospectus evidence; "
                "they do not confirm listing, trading or an investment position."
            ),
            "records": rows,
        }

    @application.get("/api/v1/listings/public-change-log/export.csv")
    def public_listings_change_log_export() -> Response:
        path = public_monitor_reports / "public-listings-alerts.csv"
        if not path.is_file():
            raise HTTPException(status_code=404, detail="Official change log artifact is not loaded.")
        return Response(
            path.read_text(encoding="utf-8"),
            media_type="text/csv",
            headers={
                "Content-Disposition": (
                    'attachment; filename="marketwitness-public-listings-alerts.csv"'
                )
            },
        )

    @application.get(
        "/dashboard/official-change-log/report",
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    def public_listings_change_log_report() -> str:
        return _generated_html(public_monitor_reports, "public-listings-alerts.html")

    @application.get("/api/v1/intelligence/modules")
    def market_intelligence_snapshot() -> dict[str, object]:
        providers = _read_sources(registry)
        try:
            as_of = max((item.reviewed_on for item in providers), default=date.today())
            return build_market_intelligence_snapshot(providers, as_of)
        except SourceRegistryDataError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @application.get("/api/v1/intelligence/volatility")
    def volatility_lab_snapshot(
        period_start: Optional[date] = Query(default=None, alias="start"),
        period_end: Optional[date] = Query(default=None, alias="end"),
    ) -> dict[str, object]:
        providers = _read_sources(registry)
        try:
            as_of = max((item.reviewed_on for item in providers), default=date.today())
            return build_volatility_lab_snapshot(providers, as_of, period_start, period_end)
        except SourceRegistryDataError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @application.get("/api/v1/intelligence/treasury-regimes")
    def treasury_regime_snapshot(sessions: int = Query(default=1)) -> dict[str, object]:
        path = policy_monitor_reports / "treasury-yields.csv"
        if not path.is_file():
            return {
                "available": False,
                "data_mode": "Optional official Treasury artifact",
                "message": (
                    "Load a Treasury yield artifact to inspect official 2Y/10Y curve regimes."
                ),
            }
        try:
            return build_treasury_regime_snapshot(
                load_treasury_csv(path), sessions=sessions
            )
        except (TreasuryDataError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @application.get("/api/v1/intelligence/macro-calendar")
    def macro_calendar_snapshot(
        horizon_days: int = Query(default=90),
        agency: str = Query(default="all"),
    ) -> dict[str, object]:
        path = policy_monitor_reports / "macro-calendar.csv"
        if not path.is_file():
            return {
                "available": False,
                "data_mode": "Optional official schedule artifact",
                "message": (
                    "Load the official Federal Reserve and BLS calendar artifact "
                    "to inspect known upcoming macro catalysts."
                ),
                "events": [],
            }
        try:
            return build_macro_calendar_snapshot(
                load_macro_calendar_csv(path), horizon_days=horizon_days, agency=agency
            )
        except MacroCalendarDataError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @application.get("/api/v1/intelligence/cot-positioning")
    def cot_positioning_snapshot(
        market: str = Query(default="wti"),
        weeks: int = Query(default=1),
    ) -> dict[str, object]:
        path = policy_monitor_reports / "cftc-positioning.csv"
        if not path.is_file():
            return {
                "available": False,
                "data_mode": "Optional official CFTC artifact",
                "message": (
                    "Load the official CFTC COT artifact to inspect delayed weekly "
                    "positioning context for WTI, Gold and U.S. Dollar Index."
                ),
                "history": [],
            }
        try:
            return build_cftc_snapshot(load_cftc_csv(path), market=market, weeks=weeks)
        except CftcDataError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @application.get("/api/v1/intelligence/insider-activity")
    def insider_activity_snapshot(
        days: int = Query(default=90),
        side: str = Query(default="all"),
        query: str = Query(default=""),
    ) -> dict[str, object]:
        path = policy_monitor_reports / "sec-insider-activity.csv"
        if not path.is_file():
            return {
                "available": False,
                "data_mode": "Optional official SEC quarterly artifact",
                "message": (
                    "Load the official SEC Form 3/4/5 artifact to inspect priced "
                    "P/S purchase or sale codes separately from other transactions."
                ),
                "issuers": [],
                "transactions": [],
            }
        try:
            return build_insider_snapshot(
                load_insider_csv(path), days=days, side=side, query=query
            )
        except SecInsiderDataError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @application.get("/api/v1/intelligence/policy-signals")
    def policy_signal_lab_snapshot() -> dict[str, object]:
        providers = _read_sources(registry)
        try:
            as_of = max((item.reviewed_on for item in providers), default=date.today())
            return build_policy_signal_lab_snapshot(providers, as_of)
        except SourceRegistryDataError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @application.get("/api/v1/intelligence/policy-reactions")
    def policy_reaction_snapshot(
        theme: str = Query(default="all"),
        period_start: Optional[date] = Query(default=None, alias="start"),
        period_end: Optional[date] = Query(default=None, alias="end"),
    ) -> dict[str, object]:
        providers = _read_sources(registry)
        try:
            as_of = max((item.reviewed_on for item in providers), default=date.today())
            return build_policy_reaction_snapshot(as_of, theme, period_start, period_end)
        except SourceRegistryDataError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @application.get("/api/v1/intelligence/policy-events")
    def policy_event_intake() -> dict[str, object]:
        path = policy_monitor_reports / "whitehouse-events.csv"
        if not path.is_file():
            return {
                "available": False,
                "data_mode": "Optional official RSS artifact",
                "collection_scope": "White House News and Presidential Actions RSS only",
                "message": (
                    "No official event-intake artifact is loaded in this runtime. "
                    "Run the authorized White House RSS workflow or load its artifact."
                ),
                "records": [],
            }
        try:
            events = load_event_archive(path)
        except WhiteHouseDataError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        topic_counts: Counter[str] = Counter()
        for event in events:
            topic_counts.update(event.themes.split(";"))
        modes = {event.source_mode for event in events}
        data_mode = (
            "Synthetic reproducible RSS fixture"
            if modes == {"synthetic_fixture"}
            else "Official RSS event archive"
            if modes == {"official_live_rss"}
            else "Mixed validation archive"
        )
        return {
            "available": True,
            "data_mode": data_mode,
            "collection_scope": "White House News and Presidential Actions RSS only",
            "observation_date": max(
                (event.observed_on.isoformat() for event in events), default=None
            ),
            "record_count": len(events),
            "review_candidate_count": sum(
                event.market_relevance == "review_candidate" for event in events
            ),
            "channel_counts": dict(Counter(event.feed for event in events)),
            "topic_counts": dict(topic_counts),
            "publication_boundary": (
                "This archive stores official title/link metadata and transparent topic tags only; "
                "it does not collect Truth Social, calculate market reaction or recommend trades."
            ),
            "records": [
                {
                    **event.__dict__,
                    "published_on": event.published_on.isoformat(),
                    "observed_on": event.observed_on.isoformat(),
                }
                for event in events
            ],
        }

    @application.get("/api/v1/intelligence/policy-events/export.csv")
    def policy_event_intake_export() -> Response:
        path = policy_monitor_reports / "whitehouse-events.csv"
        if not path.is_file():
            raise HTTPException(status_code=404, detail="Official event-intake artifact is not loaded.")
        try:
            load_event_archive(path)
        except WhiteHouseDataError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return Response(
            path.read_text(encoding="utf-8"),
            media_type="text/csv",
            headers={
                "Content-Disposition": (
                    'attachment; filename="marketwitness-whitehouse-events.csv"'
                )
            },
        )

    @application.get("/api/v1/intelligence/policy-treasury-context")
    def policy_treasury_context() -> dict[str, object]:
        event_path = policy_monitor_reports / "whitehouse-events.csv"
        treasury_path = policy_monitor_reports / "treasury-yields.csv"
        if not event_path.is_file() or not treasury_path.is_file():
            return {
                "available": False,
                "data_mode": "Optional official Treasury artifact",
                "message": (
                    "Load both official White House event intake and Treasury yield "
                    "artifacts to view observed session context."
                ),
                "records": [],
                "pending": [],
            }
        try:
            events = load_event_archive(event_path)
            yields = load_treasury_csv(treasury_path)
        except (WhiteHouseDataError, TreasuryDataError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return build_policy_treasury_context(events, yields)

    @application.get(
        "/dashboard/market-context/treasury-report",
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    def market_context_treasury_report() -> str:
        return _generated_html(policy_monitor_reports, "treasury-yields.html")

    @application.get(
        "/dashboard/macro-calendar/report",
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    def macro_calendar_report() -> str:
        return _generated_html(policy_monitor_reports, "macro-calendar.html")

    @application.get(
        "/dashboard/cot-positioning/report",
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    def cot_positioning_report() -> str:
        return _generated_html(policy_monitor_reports, "cftc-positioning.html")

    @application.get(
        "/dashboard/insider-activity/report",
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    def insider_activity_report() -> str:
        return _generated_html(policy_monitor_reports, "sec-insider-activity.html")

    @application.get(
        "/dashboard/presidential-impact/treasury-report",
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    def policy_treasury_report() -> str:
        return _generated_html(policy_monitor_reports, "treasury-yields.html")

    @application.get(
        "/dashboard/presidential-impact/events-report",
        response_class=HTMLResponse,
        include_in_schema=False,
    )
    def policy_event_intake_report() -> str:
        return _generated_html(policy_monitor_reports, "whitehouse-events.html")

    @application.get("/api/v1/policy/public-use")
    def public_use_policy_snapshot() -> dict[str, object]:
        providers = _read_sources(registry)
        try:
            as_of = max((item.reviewed_on for item in providers), default=date.today())
            return build_public_use_policy(providers, as_of)
        except SourceRegistryDataError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @application.get("/api/v1/extensions/licensed")
    def licensed_extension_snapshot() -> dict[str, object]:
        try:
            extensions = load_licensed_extensions(licensed_extensions)
            as_of = max(
                (extension.reviewed_on for extension in extensions), default=date.today()
            )
            return build_licensed_extensions_snapshot(extensions, as_of)
        except (LicensedExtensionDataError, OSError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @application.get("/api/v1/governance/approvals")
    def governance_approvals() -> dict[str, object]:
        providers = _read_sources(registry)
        try:
            approvals = load_provider_approvals(approval_queue)
            as_of = max(
                [item.reviewed_on for item in providers]
                + [item.reviewed_on for item in approvals],
                default=date.today(),
            )
            return build_approval_queue(providers, approvals, as_of)
        except (ProviderApprovalDataError, SourceRegistryDataError, OSError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @application.get("/api/v1/runs")
    def runs() -> list[dict[str, object]]:
        return _warehouse_call(list_run_summaries, database)

    @application.get("/api/v1/operations/quality")
    def quality_monitor(
        maximum_excluded_rate: Decimal = Query(default=Decimal("0.50"), ge=0, le=1),
        run_id: str = "",
        public_release: bool = False,
    ) -> dict[str, object]:
        if run_id:
            _read_run(database, run_id)
        return _warehouse_call(
            build_quality_snapshot, database, maximum_excluded_rate, run_id, public_release
        )

    @application.get("/api/v1/releases/scorecard")
    def release_scorecard(
        run_id: str,
        maximum_excluded_rate: Decimal = Query(default=Decimal("0.50"), ge=0, le=1),
    ) -> dict[str, object]:
        _read_run(database, run_id)
        providers = _read_sources(registry)
        try:
            as_of = max((item.reviewed_on for item in providers), default=date.today())
            return _warehouse_call(
                build_release_decision,
                providers,
                database,
                run_id,
                as_of,
                maximum_excluded_rate,
            )
        except SourceRegistryDataError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @application.get("/api/v1/runs/compare")
    def compare_runs(left_run_id: str, right_run_id: str) -> dict[str, object]:
        left = _read_run(database, left_run_id)
        right = _read_run(database, right_run_id)
        same_methodology = bool(
            left["methodology_version"]
            and left["methodology_version"] == right["methodology_version"]
        )
        same_dataset = bool(
            left["dataset_fingerprint"]
            and left["dataset_fingerprint"] == right["dataset_fingerprint"]
        )
        if same_methodology and same_dataset:
            comparability = "same_evidence_and_methodology"
        elif same_methodology:
            comparability = "same_methodology_different_dataset"
        else:
            comparability = "methodology_changed"
        return {
            "left": left,
            "right": right,
            "same_methodology": same_methodology,
            "same_dataset": same_dataset,
            "comparability": comparability,
            "deltas": {
                key: right[key] - left[key]
                for key in ("observation_count", "evaluated_count", "excluded_count", "pending_count")
            },
        }

    @application.get("/api/v1/runs/{run_id}")
    def run_detail(run_id: str) -> dict[str, object]:
        run = _read_run(database, run_id)
        run["assets"] = [
            {
                "asset_role": item["asset_role"],
                "sha256": item["sha256"],
                "byte_size": item["byte_size"],
                "provider_id": item["provider_id"],
            }
            for item in _warehouse_call(read_run_assets, database, run_id)
        ]
        return run

    @application.get("/api/v1/runs/{run_id}/rankings/firms")
    def firm_ranking(
        run_id: str,
        minimum_sample: Optional[int] = Query(default=None, ge=1),
        sector: str = "",
        direction: str = Query(default="", pattern="^(|up|down)$"),
    ) -> dict[str, object]:
        return _firm_ranking_payload(database, run_id, minimum_sample, sector, direction)

    @application.get("/api/v1/runs/{run_id}/export/evaluations.csv")
    def evaluations_export(run_id: str) -> Response:
        _read_run(database, run_id)
        rows = _warehouse_call(read_evaluations, database, run_id)
        exported = [_public_evaluation(item) for item in rows]
        return _csv_download(
            f"marketwitness-{_safe_filename(run_id)}-evaluations.csv",
            exported,
            list(exported[0]) if exported else [],
        )

    @application.get("/api/v1/runs/{run_id}/export/rankings-firms.csv")
    def firm_ranking_export(
        run_id: str,
        minimum_sample: Optional[int] = Query(default=None, ge=1),
        sector: str = "",
        direction: str = Query(default="", pattern="^(|up|down)$"),
    ) -> Response:
        result = _firm_ranking_payload(database, run_id, minimum_sample, sector, direction)
        rows = result["ranking"]
        fields = [
            "firm",
            "observations",
            "hits",
            "hit_rate",
            "hit_rate_ci_95_low",
            "hit_rate_ci_95_high",
            "mean_terminal_absolute_error_pct",
            "median_days_to_hit",
            "mean_horizon_excess_return_pct",
            "mean_net_strategy_return_pct",
            "mean_net_strategy_excess_return_pct",
        ]
        return _csv_download(
            f"marketwitness-{_safe_filename(run_id)}-firm-ranking.csv", rows, fields
        )

    @application.get("/api/v1/runs/{run_id}/facets")
    def facets(run_id: str) -> dict[str, object]:
        run = _read_run(database, run_id)
        rows = _warehouse_call(read_evaluations, database, run_id)
        return {
            "run_id": run_id,
            "methodology_version": run["methodology_version"],
            "sectors": sorted({item.sector or "Unclassified" for item in rows}),
            "directions": sorted({item.direction for item in rows if item.direction}),
            "firms": sorted({item.firm for item in rows}),
            "tickers": sorted({item.ticker for item in rows}),
        }

    @application.get("/api/v1/runs/{run_id}/firms/{firm}")
    def firm_detail(run_id: str, firm: str) -> dict[str, object]:
        run = _read_run(database, run_id)
        rows = _warehouse_call(read_evaluations, database, run_id, firm=firm)
        if not rows:
            raise HTTPException(status_code=404, detail="Firm not found in this run.")
        evaluated = [item for item in rows if item.status == "evaluated"]
        return {
            "run_id": run_id,
            "firm": firm,
            "methodology_version": run["methodology_version"],
            "summary": _ranking_row(firm, evaluated) if evaluated else None,
            "statuses": dict(Counter(item.status for item in rows)),
            "observations": [_public_evaluation(item) for item in rows],
            "run_as_of": run["as_of"],
        }

    @application.get("/api/v1/runs/{run_id}/tickers/{ticker}")
    def ticker_detail(run_id: str, ticker: str) -> dict[str, object]:
        run = _read_run(database, run_id)
        symbol = ticker.upper()
        rows = _warehouse_call(read_evaluations, database, run_id, ticker=symbol)
        if not rows:
            raise HTTPException(status_code=404, detail="Ticker not found in this run.")
        return {
            "run_id": run_id,
            "ticker": symbol,
            "methodology_version": run["methodology_version"],
            "statuses": dict(Counter(item.status for item in rows)),
            "observations": [_public_evaluation(item) for item in rows],
        }

    @application.get("/api/v1/runs/{run_id}/tickers/{ticker}/timeline")
    def ticker_timeline(run_id: str, ticker: str) -> dict[str, object]:
        run = _read_run(database, run_id)
        symbol = ticker.upper()
        rows = _warehouse_call(read_evaluations, database, run_id, ticker=symbol)
        if not rows:
            raise HTTPException(status_code=404, detail="Ticker not found in this run.")
        return {
            "run_id": run_id,
            "ticker": symbol,
            "methodology_version": run["methodology_version"],
            "series_type": "evaluation_evidence_points",
            "limitation": (
                "Retained evaluation milestones only; this is not a daily "
                "market-price series."
            ),
            "observations": [_timeline_observation(item) for item in rows],
        }

    @application.get("/api/v1/runs/{run_id}/audit/exclusions")
    def exclusions(run_id: str) -> dict[str, object]:
        run = _read_run(database, run_id)
        rows = _warehouse_call(read_evaluations, database, run_id)
        omitted = [item for item in rows if item.status != "evaluated"]
        return {
            "run_id": run_id,
            "methodology_version": run["methodology_version"],
            "counts_by_reason": dict(Counter(item.reason for item in omitted)),
            "observations": [_public_evaluation(item) for item in omitted],
        }

    return application


def _read_run(database: Path, run_id: str) -> dict[str, object]:
    try:
        return read_run_summary(database, run_id)
    except WarehouseError as exc:
        if "not found" in str(exc):
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _warehouse_call(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except WarehouseError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _read_sources(registry: Path) -> list[SourceProvider]:
    try:
        return load_source_registry(registry)
    except (OSError, SourceRegistryDataError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _read_listing_radar_rows(directory: Path) -> list[dict[str, object]]:
    ipo_path = directory / "ipo-watch-reviewed.csv"
    alert_path = directory / "global-alerts.csv"
    if not ipo_path.is_file() or not alert_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Listings Radar data is not available. Run the demo pipeline first.",
        )
    rows: list[dict[str, object]] = []
    try:
        with ipo_path.open(newline="", encoding="utf-8") as source:
            for index, item in enumerate(csv.DictReader(source), start=1):
                rows.append(
                    {
                        "record_id": f"ipo-{index}-{_safe_filename(item['company_name'])}",
                        "stream": "ipo_watch",
                        "market": item["exchange"].strip() or "US",
                        "company_name": item["company_name"].strip(),
                        "status": item["status"].strip(),
                        "event_date": item["status_date"].strip(),
                        "detail": " / ".join(
                            value
                            for value in (
                                item["theme"].strip(),
                                item["filing_type"].strip(),
                                item["ticker"].strip(),
                            )
                            if value
                        ),
                        "next_action": item["next_event"].strip(),
                        "source_url": item["source_url"].strip(),
                        "evidence_level": item["evidence_level"].strip(),
                    }
                )
        with alert_path.open(newline="", encoding="utf-8") as source:
            for index, item in enumerate(csv.DictReader(source), start=1):
                observed_on = item.get("observed_on", "").strip()
                if not observed_on:
                    raise ValueError("global alert rows require observed_on")
                rows.append(
                    {
                        "record_id": f"global-{index}-{_safe_filename(item['company_name'])}",
                        "stream": "global_changes",
                        "market": item["market"].strip(),
                        "company_name": item["company_name"].strip(),
                        "status": item["change_type"].strip(),
                        "event_date": observed_on,
                        "detail": item["current_detail"].strip() or item["previous_detail"].strip(),
                        "next_action": item["review_action"].strip(),
                        "source_url": item["source_url"].strip(),
                        "evidence_level": "Normalized official-source change",
                    }
                )
        for row in rows:
            date.fromisoformat(str(row["event_date"]))
    except (OSError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=f"Listings Radar data is invalid: {exc}") from exc
    return rows


def _filter_listing_radar_rows(
    rows: list[dict[str, object]],
    query: str,
    stream: str,
    market: str,
    status: str,
    start: Optional[date],
    end: Optional[date],
) -> list[dict[str, object]]:
    normalized_query = query.strip().casefold()
    selected = []
    for row in rows:
        row_date = date.fromisoformat(str(row["event_date"]))
        if normalized_query and normalized_query not in " ".join(
            str(row[key]).casefold()
            for key in ("company_name", "market", "status", "detail", "next_action")
        ):
            continue
        if stream and row["stream"] != stream:
            continue
        if market and row["market"].casefold() != market.casefold():
            continue
        if status and row["status"] != status:
            continue
        if start and row_date < start:
            continue
        if end and row_date > end:
            continue
        selected.append(row)
    selected.sort(
        key=lambda item: (str(item["event_date"]), str(item["company_name"])),
        reverse=True,
    )
    return selected


def _listing_automation_controls(providers: list[SourceProvider]) -> list[dict[str, object]]:
    providers_by_id = {provider.provider_id: provider for provider in providers}
    controls = []
    for market, name, provider_id, requested_state in LISTING_AUTOMATION_CONTROLS:
        provider = providers_by_id.get(provider_id)
        if provider is None:
            activation_state = "unavailable"
            reason = "Required source passport is not registered."
        elif requested_state == "weekdays_official_capture" and provider.deployment_state == "usable_with_policy":
            activation_state = requested_state
            reason = (
                "Official evidence captured and compared with retained prior "
                "observations by the no-cost weekday GitHub Action."
            )
        elif requested_state == "operator_configuration_required":
            activation_state = requested_state
            reason = "Connector is permitted but live SEC collection requires an identified private User-Agent."
        else:
            activation_state = "rights_review_required"
            reason = "Connector exists, but public live-output terms remain under review."
        controls.append(
            {
                "market": market,
                "name": name,
                "provider_id": provider_id,
                "activation_state": activation_state,
                "deployment_state": provider.deployment_state if provider else "unavailable",
                "reason": reason,
            }
        )
    controls.append(
        {
            "market": "MOEX",
            "name": "Moscow Exchange / Bank of Russia",
            "provider_id": "",
            "activation_state": "restricted_research_only",
            "deployment_state": "blocked",
            "reason": "Automation is not activated pending sanctions and licensing review.",
        }
    )
    return controls


def _read_public_change_log_rows(path: Path) -> list[dict[str, str]]:
    try:
        required = {
            "observed_on",
            "market",
            "change_type",
            "company_name",
            "previous_status",
            "current_status",
            "previous_detail",
            "current_detail",
            "review_action",
            "source_url",
        }
        with path.open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            missing = required - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"missing columns: {', '.join(sorted(missing))}")
            rows = list(reader)
        for row in rows:
            date.fromisoformat(row["observed_on"].strip())
            if row["market"].strip() not in {"CVM", "ESMA"}:
                raise ValueError("official public change log contains an unapproved market")
            if row["change_type"].strip() not in {
                "new",
                "changed",
                "removed_from_feed_review",
            }:
                raise ValueError("official public change log contains an unknown change type")
            if not row["source_url"].strip().startswith("https://"):
                raise ValueError("official public change log source URLs must use HTTPS")
        return [
            {key: value.strip() for key, value in row.items()}
            for row in rows
        ]
    except (OSError, ValueError) as exc:
        raise HTTPException(
            status_code=503, detail=f"Official change log data is invalid: {exc}"
        ) from exc


def _generated_html(directory: Path, filename: str) -> str:
    path = directory / filename
    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Generated report not available: {filename}. Run the demo pipeline first.",
        )
    try:
        return _dashboard_html(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _dashboard_html(page: str) -> str:
    if GLOBAL_NAV_MARKER in page:
        return page
    decorated = (
        page.replace("</head>", f"{GLOBAL_NAV_STYLE}</head>", 1)
        if "</head>" in page
        else f"{GLOBAL_NAV_STYLE}{page}"
    )
    if "</body>" in decorated:
        return decorated.replace("</body>", f"{GLOBAL_NAV_HTML}</body>", 1)
    return f"{decorated}{GLOBAL_NAV_HTML}"


def _public_source(item: SourceProvider) -> dict[str, object]:
    return {
        "provider_id": item.provider_id,
        "provider_name": item.provider_name,
        "data_class": item.data_class,
        "access_model": item.access_model,
        "integration_status": item.integration_status,
        "license_status": item.license_status,
        "publication_policy": item.publication_policy,
        "deployment_state": item.deployment_state,
        "official_url": item.official_url,
        "reference_url": item.reference_url,
        "reviewed_on": item.reviewed_on.isoformat(),
        "review_note": item.review_note,
    }


def _evidence_passport(item: SourceProvider) -> dict[str, object]:
    return {
        "passport_id": item.provider_id,
        "source": {
            "name": item.provider_name,
            "official_url": item.official_url,
            "reference_url": item.reference_url,
        },
        "evidence": {
            "data_class": item.data_class,
            "access_model": item.access_model,
            "integration_status": item.integration_status,
        },
        "rights": {
            "license_status": item.license_status,
            "publication_policy": item.publication_policy,
            "deployment_state": item.deployment_state,
        },
        "review": {
            "reviewed_on": item.reviewed_on.isoformat(),
            "note": item.review_note,
        },
    }


def _firm_ranking_payload(
    database: Path,
    run_id: str,
    minimum_sample: Optional[int],
    sector: str,
    direction: str,
) -> dict[str, object]:
    run = _read_run(database, run_id)
    rows = _warehouse_call(read_evaluations, database, run_id, status="evaluated")
    if sector:
        rows = [item for item in rows if item.sector.lower() == sector.lower()]
    if direction:
        rows = [item for item in rows if item.direction == direction]
    threshold = minimum_sample or run["minimum_sample"]
    grouped: defaultdict[str, list[Evaluation]] = defaultdict(list)
    for item in rows:
        grouped[item.firm].append(item)
    ranking = [
        _ranking_row(firm, values)
        for firm, values in grouped.items()
        if len(values) >= threshold
    ]
    ranking.sort(key=lambda row: (-row["hit_rate"], -row["observations"], row["firm"].lower()))
    return {
        "run_id": run_id,
        "methodology_version": run["methodology_version"],
        "minimum_sample": threshold,
        "sector": sector or None,
        "direction": direction or None,
        "ranking": ranking,
    }


def _ranking_row(firm: str, rows: list[Evaluation]) -> dict[str, object]:
    hits = sum(item.hit is True for item in rows)
    low, high = wilson_interval(hits, len(rows))
    hit_days = [item.days_to_target for item in rows if item.days_to_target is not None]
    return {
        "firm": firm,
        "observations": len(rows),
        "hits": hits,
        "hit_rate": _decimal_rate(hits, len(rows)),
        "hit_rate_ci_95_low": float(low),
        "hit_rate_ci_95_high": float(high),
        "mean_terminal_absolute_error_pct": _mean_float(
            rows, "terminal_absolute_error_pct"
        ),
        "median_days_to_hit": int(median(hit_days)) if hit_days else None,
        "mean_horizon_excess_return_pct": _mean_float(rows, "excess_return_pct"),
        "mean_net_strategy_return_pct": _mean_float(rows, "strategy_net_return_pct"),
        "mean_net_strategy_excess_return_pct": _mean_float(
            rows, "strategy_net_excess_return_pct"
        ),
    }


def _public_evaluation(item: Evaluation) -> dict[str, object]:
    row = item.to_row()
    row["hit"] = item.hit
    row["days_to_target"] = item.days_to_target
    return row


def _timeline_observation(item: Evaluation) -> dict[str, object]:
    milestones = [
        ("Reference close", item.reference_date, item.reference_price, "reference"),
        ("Entry close", item.entry_date, item.entry_price, "entry"),
        ("Target hit", item.hit_date, item.price_target if item.hit else None, "hit"),
        (
            "Strategy exit",
            item.strategy_exit_date,
            item.strategy_exit_price,
            "exit",
        ),
        ("Terminal close", item.terminal_date, item.terminal_price, "terminal"),
    ]
    points: list[dict[str, object]] = []
    for label, dated, value, kind in milestones:
        if not dated or value is None:
            continue
        existing = next(
            (
                point
                for point in points
                if point["date"] == dated and point["value"] == float(value)
            ),
            None,
        )
        if existing:
            existing["label"] = f'{existing["label"]} / {label}'
            if kind == "hit":
                existing["kind"] = kind
        else:
            points.append(
                {"label": label, "date": dated, "value": float(value), "kind": kind}
            )
    return {
        "observation_id": item.observation_id,
        "firm": item.firm,
        "status": item.status,
        "reason": item.reason,
        "published_date": item.published_date,
        "price_target": float(item.price_target) if item.price_target is not None else None,
        "target_end_date": item.expiry_date or item.terminal_date,
        "points": points,
    }


def _safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-") or "run"


def _csv_download(
    filename: str, rows: list[dict[str, object]], fieldnames: list[str]
) -> Response:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    if fieldnames:
        writer.writeheader()
        writer.writerows(rows)
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _decimal_rate(numerator: int, denominator: int) -> float:
    return float(Decimal(numerator) / Decimal(denominator))


def _mean_float(rows: list[Evaluation], field: str) -> float | None:
    values = [getattr(item, field) for item in rows if getattr(item, field) is not None]
    if not values:
        return None
    return float(sum(values, Decimal("0")) / Decimal(len(values)))


app = create_app()
