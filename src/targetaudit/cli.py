from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal
from pathlib import Path

from .corporate_actions import (
    CorporateActionDataError,
    find_affected_observations,
    load_corporate_actions,
    write_affected_observations_csv,
    write_corporate_actions_html,
    write_corporate_actions_report,
)
from .csvio import DataFormatError, load_prices, load_targets, write_evaluations
from .evaluator import evaluate_all
from .etf_holdings import (
    EtfHoldingsDataError,
    compare_holdings,
    load_holdings_snapshot,
    write_changes_csv,
    write_holdings_html,
    write_holdings_report,
)
from .historical_universe import HistoricalUniverseDataError, load_historical_universe
from .global_listings import (
    GlobalListingsDataError,
    load_global_market_sources,
    write_global_listings_html,
    write_global_listings_report,
)
from .ipo_watch import (
    IpoWatchDataError,
    load_ipo_watch,
    write_ipo_watch_csv,
    write_ipo_watch_html,
    write_ipo_watch_report,
)
from .ipo_reviews import (
    IpoReviewDataError,
    apply_review_decisions,
    load_alert_evidence,
    load_review_decisions,
    write_review_outcomes_csv,
    write_review_html,
    write_review_report,
)
from .issuer_confirmations import (
    IssuerConfirmationDataError,
    load_issuer_confirmations,
    write_issuer_confirmations_html,
    write_issuer_confirmations_report,
)
from .lse_upcoming import (
    LseDataError,
    fetch_lse_upcoming,
    load_lse_page_payload,
    load_lse_upcoming,
    write_lse_csv,
    write_lse_html,
    write_lse_report,
)
from .listing_alerts import (
    ListingAlertsDataError,
    archive_snapshot,
    compare_signals,
    latest_previous_snapshot,
    load_current_signals,
    load_snapshot_directory,
    write_alerts_csv,
    write_alerts_html,
    write_alerts_report,
)
from .providers.hkex import (
    HkexDataError,
    fetch_hkex_feeds,
    load_hkex_snapshot,
    write_hkex_csv,
    write_hkex_html,
    write_hkex_report,
)
from .providers.fca_nsm import (
    FcaNsmDataError,
    check_lse_issues,
    load_nsm_fixture,
    write_lse_fca_csv,
    write_lse_fca_html,
    write_lse_fca_report,
)
from .providers.asx import (
    AsxDataError,
    fetch_asx_upcoming,
    load_asx_snapshot,
    write_asx_csv,
    write_asx_html,
    write_asx_report,
)
from .providers.alpha_vantage import (
    AlphaVantageDataError,
    fetch_adjusted_daily,
    load_alpha_vantage_snapshot,
    write_prices_csv,
    write_prices_html,
    write_prices_report,
)
from .providers.ark import (
    ARK_DOCUMENTS_URL,
    ArkHoldingsDataError,
    load_ark_holdings_snapshot,
    write_import_report as write_ark_import_report,
    write_normalized_holdings as write_ark_normalized_holdings,
)
from .providers.spdr import (
    SPDR_XLF_URL,
    SpdrHoldingsDataError,
    load_spdr_holdings_snapshot,
    write_import_report as write_spdr_import_report,
    write_normalized_holdings as write_spdr_normalized_holdings,
)
from .providers.tsx import (
    TsxDataError,
    fetch_tsx_new_listings,
    load_tsx_snapshot,
    write_tsx_csv,
    write_tsx_html,
    write_tsx_report,
)
from .providers.sgx import (
    SgxDataError,
    fetch_sgx_prospectuses,
    load_sgx_snapshot,
    write_sgx_csv,
    write_sgx_html,
    write_sgx_report,
)
from .providers.sec import SecDataError, fetch_company_ticker_map, write_company_ticker_map
from .providers.sec_nport import (
    SEC_ARCHIVES_ROOT,
    SEC_NPORT_DATASETS_URL,
    SecNportDataError,
    collect_latest_nport_snapshot,
    fetch_nport_document,
    fetch_recent_nport_filings,
    load_nport_document,
    load_nport_xml_snapshot,
    load_recent_nport_filings,
    write_collection_report as write_nport_collection_report,
    write_import_report as write_nport_import_report,
    write_normalized_holdings as write_nport_normalized_holdings,
)
from .providers.sec_nport_dataset import (
    load_nport_dataset_backfill,
    write_backfill_manifest,
    write_backfill_report,
    write_backfill_snapshots,
)
from .providers.sec_ipo import (
    fetch_daily_master_index,
    load_master_index,
    parse_ipo_candidate_filings,
    write_discovered_filings,
    write_discovery_report,
)
from .sec_alerts import (
    SecAlertsDataError,
    archive_discovery,
    build_filing_alerts,
    known_source_urls,
    load_discovered_filings,
    write_sec_alerts_csv,
    write_sec_alerts_html,
    write_sec_alerts_report,
)
from .source_registry import (
    SourceRegistryDataError,
    load_source_registry,
    write_source_registry_html,
    write_source_registry_report,
)
from .target_imports import (
    TargetImportDataError,
    import_authorized_targets,
    load_target_import_manifest,
    write_import_audit,
    write_import_html,
    write_import_report,
    write_normalized_targets,
)
from .reporting import write_markdown_report


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="targetaudit",
        description="Evaluate auditable analyst price-target observations.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate_parser = subparsers.add_parser(
        "evaluate", help="Evaluate targets against adjusted price bars."
    )
    evaluate_parser.add_argument("--targets", required=True, help="Input targets CSV.")
    evaluate_parser.add_argument("--prices", required=True, help="Input adjusted prices CSV.")
    evaluate_parser.add_argument(
        "--corporate-actions",
        help="Optional audited split and ticker-change registry used to block affected scoring.",
    )
    evaluate_parser.add_argument(
        "--universe-membership",
        help="Optional point-in-time membership CSV used to restrict the scored universe.",
    )
    evaluate_parser.add_argument("--output", required=True, help="Evaluation output CSV.")
    evaluate_parser.add_argument("--report", required=True, help="Markdown report path.")
    evaluate_parser.add_argument(
        "--minimum-sample",
        type=int,
        default=50,
        help="Minimum evaluated observations for a firm ranking (default: 50).",
    )
    evaluate_parser.add_argument(
        "--transaction-cost-bps",
        type=Decimal,
        default=Decimal("10"),
        help="Simulated transaction cost in bps per side (default: 10).",
    )
    evaluate_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Calculation cutoff in YYYY-MM-DD format.",
    )
    sec_parser = subparsers.add_parser(
        "sec-company-map", help="Download SEC ticker/CIK reference data."
    )
    sec_parser.add_argument(
        "--user-agent",
        required=False,
        help='Declared SEC user agent, for example "TargetAudit contact@example.com".',
    )
    sec_parser.add_argument("--output", required=True, help="Output CSV path.")
    discover_parser = subparsers.add_parser(
        "sec-ipo-discover",
        help="Scan a SEC daily master index for potential IPO-related filings.",
    )
    discover_parser.add_argument("--date", required=True, help="SEC filing date YYYY-MM-DD.")
    discover_parser.add_argument("--output", required=True, help="Discovery queue CSV path.")
    discover_parser.add_argument("--report", required=True, help="Markdown report path.")
    discover_parser.add_argument(
        "--user-agent",
        help="SEC contact user agent; alternatively set TARGETAUDIT_SEC_USER_AGENT.",
    )
    discover_parser.add_argument(
        "--index-file",
        help="Read an already downloaded SEC master index instead of requesting SEC.",
    )
    sec_alerts_parser = subparsers.add_parser(
        "sec-ipo-alerts",
        help="Archive SEC IPO discovery output and generate a new-filing review queue.",
    )
    sec_alerts_parser.add_argument(
        "--discovery", required=True, help="Normalized SEC discovery CSV for this run."
    )
    sec_alerts_parser.add_argument(
        "--watchlist", required=True, help="IPO Watch registry CSV for CIK matching."
    )
    sec_alerts_parser.add_argument(
        "--history-dir", required=True, help="Directory for dated SEC discovery snapshots."
    )
    sec_alerts_parser.add_argument(
        "--previous-history-dir",
        help="Optional separate history directory used only as the comparison baseline.",
    )
    sec_alerts_parser.add_argument("--output", required=True, help="Alert output CSV path.")
    sec_alerts_parser.add_argument("--report", required=True, help="Markdown report path.")
    sec_alerts_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    sec_alerts_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Observation date in YYYY-MM-DD format.",
    )
    review_parser = subparsers.add_parser(
        "ipo-watch-review",
        help="Apply documented manual SEC review decisions to an IPO Watch registry copy.",
    )
    review_parser.add_argument("--alerts", required=True, help="SEC IPO Alerts CSV input.")
    review_parser.add_argument("--registry", required=True, help="IPO Watch registry CSV input.")
    review_parser.add_argument(
        "--decisions", required=True, help="Documented manual review decisions CSV."
    )
    review_parser.add_argument(
        "--output-registry", required=True, help="Updated IPO Watch registry CSV output."
    )
    review_parser.add_argument("--output", required=True, help="Review audit CSV output.")
    review_parser.add_argument("--report", required=True, help="Review audit Markdown report.")
    review_parser.add_argument("--html", help="Optional review audit HTML dashboard page.")
    review_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Review cutoff in YYYY-MM-DD format.",
    )
    ipo_parser = subparsers.add_parser(
        "ipo-watch", help="Generate an auditable IPO monitoring report."
    )
    ipo_parser.add_argument("--registry", required=True, help="IPO watch registry CSV.")
    ipo_parser.add_argument("--report", required=True, help="Markdown report path.")
    ipo_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    ipo_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Verification cutoff in YYYY-MM-DD format.",
    )
    global_parser = subparsers.add_parser(
        "global-listings", help="Generate global listing-source coverage dashboard."
    )
    global_parser.add_argument("--sources", required=True, help="Official markets CSV.")
    global_parser.add_argument("--report", required=True, help="Markdown report path.")
    global_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    global_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Source review cutoff in YYYY-MM-DD format.",
    )
    confirmations_parser = subparsers.add_parser(
        "issuer-confirmations",
        help="Generate verified listing milestones from official issuer releases.",
    )
    confirmations_parser.add_argument(
        "--registry", required=True, help="Curated official issuer-release CSV."
    )
    confirmations_parser.add_argument("--report", required=True, help="Markdown report path.")
    confirmations_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    confirmations_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Verification cutoff in YYYY-MM-DD format.",
    )
    corporate_parser = subparsers.add_parser(
        "corporate-actions-check",
        help="Audit targets that span documented splits or ticker changes.",
    )
    corporate_parser.add_argument("--targets", required=True, help="Input targets CSV.")
    corporate_parser.add_argument(
        "--actions", required=True, help="Documented corporate actions CSV."
    )
    corporate_parser.add_argument("--output", required=True, help="Affected targets CSV path.")
    corporate_parser.add_argument("--report", required=True, help="Markdown report path.")
    corporate_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    corporate_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Evidence cutoff in YYYY-MM-DD format.",
    )
    sources_parser = subparsers.add_parser(
        "source-registry",
        help="Generate provider access, license-review and publication controls.",
    )
    sources_parser.add_argument("--registry", required=True, help="Provider registry CSV.")
    sources_parser.add_argument("--report", required=True, help="Markdown report path.")
    sources_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    sources_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Governance review cutoff in YYYY-MM-DD format.",
    )
    etf_parser = subparsers.add_parser(
        "etf-holdings-activity",
        help="Compare ETF holdings snapshots and render observed changes.",
    )
    etf_parser.add_argument("--previous", required=True, help="Prior normalized holdings CSV.")
    etf_parser.add_argument("--current", required=True, help="Current normalized holdings CSV.")
    etf_parser.add_argument("--output", required=True, help="Observed changes CSV path.")
    etf_parser.add_argument("--report", required=True, help="Markdown report path.")
    etf_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    etf_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Evidence cutoff in YYYY-MM-DD format.",
    )
    ark_parser = subparsers.add_parser(
        "ark-holdings-import",
        help="Normalize a downloaded ARK ETF holdings CSV for local comparison.",
    )
    ark_parser.add_argument("--snapshot", required=True, help="Downloaded ARK holdings CSV.")
    ark_parser.add_argument("--fund-symbol", required=True, help="ARK fund symbol in the CSV.")
    ark_parser.add_argument("--fund-name", required=True, help="Readable ARK fund name.")
    ark_parser.add_argument("--captured-on", required=True, help="Capture date in YYYY-MM-DD.")
    ark_parser.add_argument(
        "--source-url",
        default=ARK_DOCUMENTS_URL,
        help="Official download page or evidence URL retained with normalized rows.",
    )
    ark_parser.add_argument(
        "--synthetic-fixture",
        action="store_true",
        help="Mark project-authored format fixtures as synthetic instead of official evidence.",
    )
    ark_parser.add_argument("--output", required=True, help="Normalized ETF holdings CSV path.")
    ark_parser.add_argument("--report", required=True, help="Import audit Markdown report path.")
    spdr_parser = subparsers.add_parser(
        "spdr-holdings-import",
        help="Normalize a downloaded State Street SPDR holdings CSV for local comparison.",
    )
    spdr_parser.add_argument("--snapshot", required=True, help="Downloaded SPDR holdings CSV.")
    spdr_parser.add_argument("--fund-symbol", required=True, help="SPDR fund symbol in the CSV.")
    spdr_parser.add_argument("--fund-name", required=True, help="Readable SPDR fund name.")
    spdr_parser.add_argument("--captured-on", required=True, help="Capture date in YYYY-MM-DD.")
    spdr_parser.add_argument(
        "--source-url",
        default=SPDR_XLF_URL,
        help="Official fund page or evidence URL retained with normalized rows.",
    )
    spdr_parser.add_argument(
        "--synthetic-fixture",
        action="store_true",
        help="Mark project-authored format fixtures as synthetic instead of official evidence.",
    )
    spdr_parser.add_argument("--output", required=True, help="Normalized ETF holdings CSV path.")
    spdr_parser.add_argument("--report", required=True, help="Import audit Markdown report path.")
    nport_parser = subparsers.add_parser(
        "sec-nport-import",
        help="Normalize a public SEC NPORT-P XML filing for periodic ETF comparison.",
    )
    nport_parser.add_argument("--snapshot", required=True, help="Downloaded public NPORT-P XML.")
    nport_parser.add_argument("--fund-symbol", required=True, help="Fund symbol for the series.")
    nport_parser.add_argument("--captured-on", required=True, help="Capture date in YYYY-MM-DD.")
    nport_parser.add_argument(
        "--source-url",
        default=SEC_NPORT_DATASETS_URL,
        help="SEC filing or dataset evidence URL retained with normalized rows.",
    )
    nport_parser.add_argument(
        "--synthetic-fixture",
        action="store_true",
        help="Mark project-authored XML fixtures as synthetic evidence.",
    )
    nport_parser.add_argument("--output", required=True, help="Normalized ETF holdings CSV path.")
    nport_parser.add_argument("--report", required=True, help="Import audit Markdown report path.")
    nport_collect_parser = subparsers.add_parser(
        "sec-nport-collect",
        help="Collect the latest public NPORT-P XML for an SEC fund series.",
    )
    nport_collect_parser.add_argument("--cik", required=True, help="SEC registrant CIK.")
    nport_collect_parser.add_argument("--series-id", required=True, help="SEC fund series ID.")
    nport_collect_parser.add_argument("--fund-symbol", required=True, help="Fund symbol.")
    nport_collect_parser.add_argument(
        "--captured-on", required=True, help="Collection date in YYYY-MM-DD."
    )
    nport_collect_parser.add_argument(
        "--archive-dir", required=True, help="Private directory for collected filing XML."
    )
    nport_collect_parser.add_argument("--output", required=True, help="Normalized holdings CSV.")
    nport_collect_parser.add_argument("--report", required=True, help="Collection audit report.")
    nport_collect_parser.add_argument(
        "--user-agent",
        help="SEC contact user agent; alternatively set TARGETAUDIT_SEC_USER_AGENT.",
    )
    nport_collect_parser.add_argument(
        "--submissions-file",
        help="Read an already downloaded SEC submissions JSON instead of requesting SEC.",
    )
    nport_collect_parser.add_argument(
        "--document-dir",
        help="Directory containing locally saved primary documents listed by fixture JSON.",
    )
    nport_collect_parser.add_argument(
        "--synthetic-fixture",
        action="store_true",
        help="Mark project-authored submissions/documents as synthetic evidence.",
    )
    nport_backfill_parser = subparsers.add_parser(
        "sec-nport-backfill",
        help="Normalize historical periods from an extracted SEC N-PORT quarterly dataset.",
    )
    nport_backfill_parser.add_argument(
        "--dataset-dir",
        required=True,
        action="append",
        help="Directory containing extracted SEC TSV tables; repeat for additional quarters.",
    )
    nport_backfill_parser.add_argument("--series-id", required=True, help="SEC fund series ID.")
    nport_backfill_parser.add_argument("--fund-symbol", required=True, help="Fund symbol.")
    nport_backfill_parser.add_argument(
        "--captured-on", required=True, help="Collection cutoff in YYYY-MM-DD."
    )
    nport_backfill_parser.add_argument(
        "--data-set-label", required=True, help="Quarterly dataset label retained in audit output."
    )
    nport_backfill_parser.add_argument(
        "--source-url",
        default=SEC_NPORT_DATASETS_URL,
        help="Official SEC dataset page or ZIP evidence URL.",
    )
    nport_backfill_parser.add_argument(
        "--synthetic-fixture",
        action="store_true",
        help="Mark project-authored TSV fixtures as synthetic evidence.",
    )
    nport_backfill_parser.add_argument(
        "--output-dir", required=True, help="Output directory for per-period holdings CSVs."
    )
    nport_backfill_parser.add_argument("--manifest", required=True, help="Output period manifest.")
    nport_backfill_parser.add_argument("--report", required=True, help="Backfill audit report.")
    prices_parser = subparsers.add_parser(
        "alpha-vantage-prices",
        help="Normalize adjusted daily price evidence through a cache-first adapter.",
    )
    prices_parser.add_argument("--ticker", required=True, help="Equity symbol to import.")
    prices_parser.add_argument(
        "--snapshot", help="Read a saved Alpha Vantage JSON fixture instead of requesting data."
    )
    prices_parser.add_argument(
        "--cache-dir",
        default="data/raw/prices/alpha-vantage",
        help="Private raw-response cache directory.",
    )
    prices_parser.add_argument(
        "--refresh",
        action="store_true",
        help="Spend a new API request even when a cached response is available.",
    )
    prices_parser.add_argument(
        "--api-key",
        help="Alpha Vantage key; prefer TARGETAUDIT_ALPHA_VANTAGE_API_KEY or private file.",
    )
    prices_parser.add_argument("--output", required=True, help="Normalized adjusted prices CSV.")
    prices_parser.add_argument("--report", required=True, help="Markdown audit report path.")
    prices_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    prices_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Price evidence cutoff in YYYY-MM-DD format.",
    )
    target_import_parser = subparsers.add_parser(
        "targets-import",
        help="Normalize a licensed or otherwise authorized analyst-target export.",
    )
    target_import_parser.add_argument("--export", required=True, help="Provider export CSV.")
    target_import_parser.add_argument(
        "--manifest", required=True, help="Authorization and field-map JSON manifest."
    )
    target_import_parser.add_argument("--output", required=True, help="Normalized targets CSV.")
    target_import_parser.add_argument("--audit", required=True, help="Row audit CSV output.")
    target_import_parser.add_argument("--report", required=True, help="Markdown import report.")
    target_import_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    target_import_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Import audit cutoff in YYYY-MM-DD format.",
    )
    alerts_parser = subparsers.add_parser(
        "global-alerts",
        help="Compare normalized international listing feeds and preserve snapshots.",
    )
    alerts_parser.add_argument("--hkex", required=True, help="Current HKEX monitor CSV.")
    alerts_parser.add_argument("--lse", required=True, help="Current LSE upcoming CSV.")
    alerts_parser.add_argument("--asx", required=True, help="Current ASX monitor CSV.")
    alerts_parser.add_argument("--tsx", required=True, help="Current TSX monitor CSV.")
    alerts_parser.add_argument("--sgx", required=True, help="Current SGX monitor CSV.")
    alerts_parser.add_argument(
        "--previous-dir",
        help="Explicit previous snapshot directory for a reproducible comparison.",
    )
    alerts_parser.add_argument(
        "--history-dir",
        help="Archive current CSVs by date and compare with the latest earlier snapshot.",
    )
    alerts_parser.add_argument("--output", required=True, help="Alert output CSV path.")
    alerts_parser.add_argument("--report", required=True, help="Markdown report path.")
    alerts_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    alerts_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Observation date in YYYY-MM-DD format.",
    )
    lse_parser = subparsers.add_parser(
        "lse-upcoming", help="Read official LSE upcoming-issues data."
    )
    lse_input = lse_parser.add_mutually_exclusive_group()
    lse_input.add_argument("--snapshot", help="Observed LSE issues CSV fallback.")
    lse_input.add_argument("--page-file", help="Saved official LSE page JSON fixture.")
    lse_parser.add_argument("--output", help="Optional normalized output CSV path.")
    lse_parser.add_argument("--report", required=True, help="Markdown report path.")
    lse_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    lse_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Snapshot cutoff in YYYY-MM-DD format.",
    )
    fca_parser = subparsers.add_parser(
        "lse-fca-check",
        help="Cross-check LSE upcoming issues against FCA NSM documents.",
    )
    fca_input = fca_parser.add_mutually_exclusive_group()
    fca_input.add_argument("--lse-snapshot", help="Observed LSE issues CSV fallback.")
    fca_input.add_argument("--lse-page-file", help="Saved official LSE page JSON fixture.")
    fca_parser.add_argument(
        "--nsm-fixture",
        help="Saved FCA NSM response fixture; omit for public live searches.",
    )
    fca_parser.add_argument("--output", help="Optional normalized FCA check CSV path.")
    fca_parser.add_argument("--report", required=True, help="Markdown report path.")
    fca_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    fca_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Check cutoff in YYYY-MM-DD format.",
    )
    asx_parser = subparsers.add_parser(
        "asx-monitor", help="Read official ASX upcoming floats and listings."
    )
    asx_parser.add_argument("--output", required=True, help="Normalized output CSV path.")
    asx_parser.add_argument("--report", required=True, help="Markdown report path.")
    asx_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    asx_parser.add_argument(
        "--snapshot", help="Read a saved official ASX HTML page instead of requesting ASX."
    )
    asx_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Report cutoff in YYYY-MM-DD format.",
    )
    tsx_parser = subparsers.add_parser(
        "tsx-monitor", help="Read official TSX New Company Listings records."
    )
    tsx_parser.add_argument("--output", required=True, help="Normalized output CSV path.")
    tsx_parser.add_argument("--report", required=True, help="Markdown report path.")
    tsx_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    tsx_parser.add_argument(
        "--snapshot", help="Read a saved official TSX HTML page instead of requesting TSX."
    )
    tsx_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Report cutoff in YYYY-MM-DD format.",
    )
    sgx_parser = subparsers.add_parser(
        "sgx-monitor", help="Read official SGX IPO Prospectus records."
    )
    sgx_parser.add_argument("--output", required=True, help="Normalized output CSV path.")
    sgx_parser.add_argument("--report", required=True, help="Markdown report path.")
    sgx_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    sgx_parser.add_argument(
        "--snapshot", help="Read a saved official SGX JSON response instead of requesting SGX."
    )
    sgx_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Report cutoff in YYYY-MM-DD format.",
    )
    hkex_parser = subparsers.add_parser(
        "hkex-monitor", help="Read official HKEXnews listing-status JSON feeds."
    )
    hkex_parser.add_argument("--output", required=True, help="Normalized output CSV path.")
    hkex_parser.add_argument("--report", required=True, help="Markdown report path.")
    hkex_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    hkex_parser.add_argument(
        "--snapshot-dir",
        help="Read JSON fixtures in a local directory instead of requesting HKEXnews.",
    )
    hkex_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Report cutoff in YYYY-MM-DD format.",
    )
    args = parser.parse_args()

    if args.command == "hkex-monitor":
        try:
            as_of = date.fromisoformat(args.as_of)
            if args.snapshot_dir:
                listings, update_dates = load_hkex_snapshot(args.snapshot_dir)
            else:
                listings, update_dates = fetch_hkex_feeds()
            write_hkex_csv(args.output, listings)
            write_hkex_report(args.report, listings, update_dates, as_of)
            if args.html:
                write_hkex_html(args.html, listings, update_dates, as_of)
        except (HkexDataError, ValueError) as exc:
            parser.error(str(exc))
        print(f"Wrote HKEX monitor for {len(listings)} official records to {args.report}.")
        return 0

    if args.command == "lse-upcoming":
        try:
            as_of = date.fromisoformat(args.as_of)
            source_mode = "snapshot"
            if args.snapshot:
                issues = load_lse_upcoming(args.snapshot)
            elif args.page_file:
                issues = load_lse_page_payload(args.page_file, as_of)
                source_mode = "live"
            else:
                issues = fetch_lse_upcoming()
                source_mode = "live"
            if args.output:
                write_lse_csv(args.output, issues)
            write_lse_report(args.report, issues, as_of, source_mode)
            if args.html:
                write_lse_html(args.html, issues, as_of, source_mode)
        except (LseDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Wrote LSE {source_mode} report for {len(issues)} upcoming issues "
            f"to {args.report}."
        )
        return 0

    if args.command == "lse-fca-check":
        try:
            as_of = date.fromisoformat(args.as_of)
            if args.lse_snapshot:
                issues = load_lse_upcoming(args.lse_snapshot)
            elif args.lse_page_file:
                issues = load_lse_page_payload(args.lse_page_file, as_of)
            else:
                issues = fetch_lse_upcoming()
            lookup = load_nsm_fixture(args.nsm_fixture) if args.nsm_fixture else None
            checks = (
                check_lse_issues(issues, lookup)
                if lookup is not None
                else check_lse_issues(issues)
            )
            if args.output:
                write_lse_fca_csv(args.output, checks)
            write_lse_fca_report(args.report, checks, as_of)
            if args.html:
                write_lse_fca_html(args.html, checks, as_of)
        except (FcaNsmDataError, LseDataError, ValueError) as exc:
            parser.error(str(exc))
        matches = sum(bool(check.documents) for check in checks)
        print(
            f"Checked {len(checks)} LSE upcoming issues; found FCA documents "
            f"for {matches} issuers. Report written to {args.report}."
        )
        return 0

    if args.command == "asx-monitor":
        try:
            as_of = date.fromisoformat(args.as_of)
            listings = (
                load_asx_snapshot(args.snapshot, as_of)
                if args.snapshot
                else fetch_asx_upcoming()
            )
            write_asx_csv(args.output, listings)
            write_asx_report(args.report, listings, as_of)
            if args.html:
                write_asx_html(args.html, listings, as_of)
        except (AsxDataError, ValueError) as exc:
            parser.error(str(exc))
        print(f"Wrote ASX monitor for {len(listings)} official records to {args.report}.")
        return 0

    if args.command == "tsx-monitor":
        try:
            as_of = date.fromisoformat(args.as_of)
            listings = (
                load_tsx_snapshot(args.snapshot, as_of)
                if args.snapshot
                else fetch_tsx_new_listings()
            )
            write_tsx_csv(args.output, listings)
            write_tsx_report(args.report, listings, as_of)
            if args.html:
                write_tsx_html(args.html, listings, as_of)
        except (TsxDataError, ValueError) as exc:
            parser.error(str(exc))
        print(f"Wrote TSX monitor for {len(listings)} official records to {args.report}.")
        return 0

    if args.command == "sgx-monitor":
        try:
            as_of = date.fromisoformat(args.as_of)
            prospectuses = (
                load_sgx_snapshot(args.snapshot, as_of)
                if args.snapshot
                else fetch_sgx_prospectuses()
            )
            write_sgx_csv(args.output, prospectuses)
            write_sgx_report(args.report, prospectuses, as_of)
            if args.html:
                write_sgx_html(args.html, prospectuses, as_of)
        except (SgxDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Wrote SGX monitor for {len(prospectuses)} official prospectus "
            f"records to {args.report}."
        )
        return 0

    if args.command == "global-listings":
        try:
            as_of = date.fromisoformat(args.as_of)
            markets = load_global_market_sources(args.sources)
            write_global_listings_report(args.report, markets, as_of)
            if args.html:
                write_global_listings_html(args.html, markets, as_of)
        except (GlobalListingsDataError, ValueError) as exc:
            parser.error(str(exc))
        print(f"Wrote global listings coverage for {len(markets)} markets to {args.report}.")
        return 0

    if args.command == "issuer-confirmations":
        try:
            as_of = date.fromisoformat(args.as_of)
            events = load_issuer_confirmations(args.registry)
            write_issuer_confirmations_report(args.report, events, as_of)
            if args.html:
                write_issuer_confirmations_html(args.html, events, as_of)
        except (IssuerConfirmationDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Wrote issuer confirmations for {len(events)} official milestones "
            f"to {args.report}."
        )
        return 0

    if args.command == "corporate-actions-check":
        try:
            as_of = date.fromisoformat(args.as_of)
            targets = load_targets(args.targets)
            actions = load_corporate_actions(args.actions)
            affected = find_affected_observations(targets, actions, as_of)
            write_affected_observations_csv(args.output, affected)
            write_corporate_actions_report(args.report, actions, affected, as_of)
            if args.html:
                write_corporate_actions_html(args.html, actions, affected, as_of)
        except (CorporateActionDataError, DataFormatError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Wrote corporate-action audit for {len(affected)} affected targets "
            f"across {len(actions)} documented actions to {args.report}."
        )
        return 0

    if args.command == "source-registry":
        try:
            as_of = date.fromisoformat(args.as_of)
            providers = load_source_registry(args.registry)
            write_source_registry_report(args.report, providers, as_of)
            if args.html:
                write_source_registry_html(args.html, providers, as_of)
        except (SourceRegistryDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Wrote source governance for {len(providers)} providers "
            f"to {args.report}."
        )
        return 0

    if args.command == "etf-holdings-activity":
        try:
            as_of = date.fromisoformat(args.as_of)
            previous = load_holdings_snapshot(args.previous, as_of)
            current = load_holdings_snapshot(args.current, as_of)
            changes = compare_holdings(previous, current)
            write_changes_csv(args.output, changes)
            write_holdings_report(args.report, previous, current, changes, as_of)
            if args.html:
                write_holdings_html(args.html, previous, current, changes, as_of)
        except (EtfHoldingsDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Wrote ETF holdings activity for {len(changes)} observed changes "
            f"to {args.report}."
        )
        return 0

    if args.command == "ark-holdings-import":
        try:
            captured_on = date.fromisoformat(args.captured_on)
            imported = load_ark_holdings_snapshot(
                args.snapshot,
                args.fund_symbol,
                args.fund_name,
                captured_on,
                args.source_url,
                args.synthetic_fixture,
            )
            write_ark_normalized_holdings(args.output, imported)
            write_ark_import_report(args.report, imported)
        except (ArkHoldingsDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Imported {len(imported.holdings)} ARK-format holdings for "
            f"{imported.fund_symbol} to {args.output}."
        )
        return 0

    if args.command == "spdr-holdings-import":
        try:
            captured_on = date.fromisoformat(args.captured_on)
            imported = load_spdr_holdings_snapshot(
                args.snapshot,
                args.fund_symbol,
                args.fund_name,
                captured_on,
                args.source_url,
                args.synthetic_fixture,
            )
            write_spdr_normalized_holdings(args.output, imported)
            write_spdr_import_report(args.report, imported)
        except (SpdrHoldingsDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Imported {len(imported.holdings)} SPDR-format holdings for "
            f"{imported.fund_symbol} to {args.output}."
        )
        return 0

    if args.command == "sec-nport-import":
        try:
            captured_on = date.fromisoformat(args.captured_on)
            imported = load_nport_xml_snapshot(
                args.snapshot,
                args.fund_symbol,
                captured_on,
                args.source_url,
                args.synthetic_fixture,
            )
            write_nport_normalized_holdings(args.output, imported)
            write_nport_import_report(args.report, imported)
        except (SecNportDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Imported {len(imported.holdings)} share positions from N-PORT "
            f"for {imported.fund_symbol} to {args.output}."
        )
        return 0

    if args.command == "sec-nport-collect":
        try:
            captured_on = date.fromisoformat(args.captured_on)
            if bool(args.submissions_file) != bool(args.document_dir):
                parser.error("--submissions-file and --document-dir must be used together.")
            if args.synthetic_fixture and not args.submissions_file:
                parser.error("--synthetic-fixture requires --submissions-file.")
            if args.submissions_file:
                archive_root = (
                    "https://example.invalid/sec-nport-fixture"
                    if args.synthetic_fixture
                    else SEC_ARCHIVES_ROOT
                )
                filings = load_recent_nport_filings(
                    args.submissions_file, args.cik, archive_root
                )
                loader = lambda filing: load_nport_document(
                    Path(args.document_dir) / filing.primary_document
                )
            else:
                filings = fetch_recent_nport_filings(args.cik, args.user_agent)
                loader = lambda filing: fetch_nport_document(filing, args.user_agent)
            collection = collect_latest_nport_snapshot(
                filings,
                args.series_id,
                args.fund_symbol,
                captured_on,
                args.archive_dir,
                loader,
                args.synthetic_fixture,
            )
            write_nport_normalized_holdings(args.output, collection.imported)
            write_nport_collection_report(args.report, collection)
        except (SecNportDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Collected SEC N-PORT filing {collection.filing.accession_number} "
            f"for {collection.imported.fund_symbol} to {args.output}."
        )
        return 0

    if args.command == "sec-nport-backfill":
        try:
            captured_on = date.fromisoformat(args.captured_on)
            backfill = load_nport_dataset_backfill(
                args.dataset_dir,
                args.series_id,
                args.fund_symbol,
                captured_on,
                args.data_set_label,
                args.source_url,
                args.synthetic_fixture,
            )
            outputs = write_backfill_snapshots(args.output_dir, backfill)
            write_backfill_manifest(args.manifest, backfill)
            write_backfill_report(args.report, backfill)
        except (SecNportDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Backfilled {len(outputs)} SEC N-PORT periods for "
            f"{backfill.fund_symbol} to {args.output_dir}."
        )
        return 0

    if args.command == "alpha-vantage-prices":
        try:
            as_of = date.fromisoformat(args.as_of)
            imported = (
                load_alpha_vantage_snapshot(args.snapshot, args.ticker)
                if args.snapshot
                else fetch_adjusted_daily(
                    args.ticker, args.api_key, args.cache_dir, args.refresh
                )
            )
            write_prices_csv(args.output, imported)
            write_prices_report(args.report, imported, as_of)
            if args.html:
                write_prices_html(args.html, imported, as_of)
        except (AlphaVantageDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Wrote {len(imported.bars)} adjusted bars for {imported.ticker} "
            f"from {imported.source_mode} evidence to {args.output}."
        )
        return 0

    if args.command == "targets-import":
        try:
            as_of = date.fromisoformat(args.as_of)
            manifest = load_target_import_manifest(args.manifest)
            observations, decisions = import_authorized_targets(
                args.export, manifest, as_of
            )
            write_normalized_targets(args.output, observations)
            write_import_audit(args.audit, decisions)
            write_import_report(args.report, manifest, decisions, as_of)
            if args.html:
                write_import_html(args.html, manifest, decisions, as_of)
        except (TargetImportDataError, ValueError) as exc:
            parser.error(str(exc))
        rejected = sum(decision.status == "rejected" for decision in decisions)
        print(
            f"Imported {len(observations)} target observations; rejected {rejected} "
            f"rows to {args.audit}."
        )
        return 0

    if args.command == "global-alerts":
        try:
            as_of = date.fromisoformat(args.as_of)
            paths = {
                "HKEX": args.hkex,
                "LSE": args.lse,
                "ASX": args.asx,
                "TSX": args.tsx,
                "SGX": args.sgx,
            }
            current = load_current_signals(paths)
            previous = None
            baseline_label = "first recorded snapshot"
            if args.previous_dir:
                previous = load_snapshot_directory(args.previous_dir)
                baseline_label = str(args.previous_dir)
            elif args.history_dir:
                prior_path = latest_previous_snapshot(args.history_dir, as_of)
                if prior_path:
                    previous = load_snapshot_directory(prior_path)
                    baseline_label = prior_path.name
            alerts = compare_signals(current, previous)
            if args.history_dir:
                archive_snapshot(args.history_dir, paths, as_of)
            write_alerts_csv(args.output, alerts)
            write_alerts_report(args.report, alerts, current, as_of, baseline_label)
            if args.html:
                write_alerts_html(args.html, alerts, current, as_of, baseline_label)
        except (ListingAlertsDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Wrote global alerts for {len(alerts)} changes across "
            f"{len(current)} current records to {args.report}."
        )
        return 0

    if args.command == "ipo-watch":
        try:
            as_of = date.fromisoformat(args.as_of)
            items = load_ipo_watch(args.registry)
            write_ipo_watch_report(args.report, items, as_of)
            if args.html:
                write_ipo_watch_html(args.html, items, as_of)
        except (IpoWatchDataError, ValueError) as exc:
            parser.error(str(exc))
        print(f"Wrote IPO watch report for {len(items)} companies to {args.report}.")
        return 0

    if args.command == "ipo-watch-review":
        try:
            as_of = date.fromisoformat(args.as_of)
            alerts = load_alert_evidence(args.alerts)
            items = load_ipo_watch(args.registry)
            decisions = load_review_decisions(args.decisions)
            reviewed_items, outcomes = apply_review_decisions(items, alerts, decisions, as_of)
            write_ipo_watch_csv(args.output_registry, reviewed_items)
            write_review_outcomes_csv(args.output, outcomes)
            write_review_report(args.report, outcomes, reviewed_items, as_of)
            if args.html:
                write_review_html(args.html, outcomes, reviewed_items, as_of)
        except (IpoReviewDataError, IpoWatchDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Applied {len(outcomes)} documented SEC review decisions; "
            f"wrote {len(reviewed_items)} IPO Watch records to {args.output_registry}."
        )
        return 0

    if args.command == "sec-ipo-alerts":
        try:
            as_of = date.fromisoformat(args.as_of)
            filings = load_discovered_filings(args.discovery)
            items = load_ipo_watch(args.watchlist)
            seen_urls = known_source_urls(args.previous_history_dir or args.history_dir, as_of)
            alerts = build_filing_alerts(filings, items, seen_urls)
            archive_discovery(args.history_dir, args.discovery, as_of)
            write_sec_alerts_csv(args.output, alerts)
            write_sec_alerts_report(args.report, alerts, filings, as_of, len(seen_urls))
            if args.html:
                write_sec_alerts_html(args.html, alerts, filings, as_of, len(seen_urls))
        except (SecAlertsDataError, IpoWatchDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Wrote SEC IPO alerts for {len(alerts)} new filing reviews "
            f"from {len(filings)} current filings to {args.report}."
        )
        return 0

    if args.command == "sec-company-map":
        try:
            rows = fetch_company_ticker_map(args.user_agent)
            write_company_ticker_map(args.output, rows)
        except SecDataError as exc:
            parser.error(str(exc))
        print(f"Wrote {len(rows)} SEC company mappings to {args.output}.")
        return 0

    if args.command == "sec-ipo-discover":
        try:
            filing_date = date.fromisoformat(args.date)
            if args.index_file:
                index_text, source_url = load_master_index(args.index_file)
            else:
                index_text, source_url = fetch_daily_master_index(
                    filing_date, args.user_agent
                )
            filings = parse_ipo_candidate_filings(index_text)
            write_discovered_filings(args.output, filings)
            write_discovery_report(args.report, filings, filing_date, source_url)
        except (SecDataError, ValueError) as exc:
            parser.error(str(exc))
        print(
            f"Discovered {len(filings)} SEC filings requiring IPO review "
            f"for {filing_date.isoformat()}."
        )
        return 0

    try:
        as_of = date.fromisoformat(args.as_of)
        if args.minimum_sample < 1:
            parser.error("--minimum-sample must be positive.")
        targets = load_targets(args.targets)
        prices = load_prices(args.prices)
        actions = (
            load_corporate_actions(args.corporate_actions)
            if args.corporate_actions
            else None
        )
        universe = (
            load_historical_universe(args.universe_membership)
            if args.universe_membership
            else None
        )
        evaluations = evaluate_all(
            targets, prices, as_of, actions, universe, args.transaction_cost_bps
        )
        write_evaluations(args.output, evaluations)
        write_markdown_report(
            args.report,
            evaluations,
            as_of,
            args.minimum_sample,
            universe[0].universe_id if universe else "",
            args.transaction_cost_bps,
        )
    except (
        CorporateActionDataError,
        DataFormatError,
        HistoricalUniverseDataError,
        ValueError,
    ) as exc:
        parser.error(str(exc))

    evaluated = sum(result.status == "evaluated" for result in evaluations)
    excluded = sum(result.status == "excluded" for result in evaluations)
    pending = sum(result.status == "pending" for result in evaluations)
    print(
        f"Evaluated {evaluated}; excluded {excluded}; pending {pending}. "
        f"Report written to {args.report}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
