from __future__ import annotations

import argparse
from datetime import date

from .csvio import DataFormatError, load_prices, load_targets, write_evaluations
from .evaluator import evaluate_all
from .global_listings import (
    GlobalListingsDataError,
    load_global_market_sources,
    write_global_listings_html,
    write_global_listings_report,
)
from .ipo_watch import (
    IpoWatchDataError,
    load_ipo_watch,
    write_ipo_watch_html,
    write_ipo_watch_report,
)
from .lse_upcoming import (
    LseDataError,
    load_lse_upcoming,
    write_lse_html,
    write_lse_report,
)
from .providers.hkex import (
    HkexDataError,
    fetch_hkex_feeds,
    load_hkex_snapshot,
    write_hkex_csv,
    write_hkex_html,
    write_hkex_report,
)
from .providers.sec import SecDataError, fetch_company_ticker_map, write_company_ticker_map
from .providers.sec_ipo import (
    fetch_daily_master_index,
    load_master_index,
    parse_ipo_candidate_filings,
    write_discovered_filings,
    write_discovery_report,
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
    evaluate_parser.add_argument("--output", required=True, help="Evaluation output CSV.")
    evaluate_parser.add_argument("--report", required=True, help="Markdown report path.")
    evaluate_parser.add_argument(
        "--minimum-sample",
        type=int,
        default=50,
        help="Minimum evaluated observations for a firm ranking (default: 50).",
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
    lse_parser = subparsers.add_parser(
        "lse-upcoming", help="Generate an LSE upcoming-issues snapshot report."
    )
    lse_parser.add_argument("--snapshot", required=True, help="Observed LSE issues CSV.")
    lse_parser.add_argument("--report", required=True, help="Markdown report path.")
    lse_parser.add_argument("--html", help="Optional HTML dashboard page output path.")
    lse_parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Snapshot cutoff in YYYY-MM-DD format.",
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
            issues = load_lse_upcoming(args.snapshot)
            write_lse_report(args.report, issues, as_of)
            if args.html:
                write_lse_html(args.html, issues, as_of)
        except (LseDataError, ValueError) as exc:
            parser.error(str(exc))
        print(f"Wrote LSE snapshot for {len(issues)} upcoming issues to {args.report}.")
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
        evaluations = evaluate_all(targets, prices, as_of)
        write_evaluations(args.output, evaluations)
        write_markdown_report(args.report, evaluations, as_of, args.minimum_sample)
    except (DataFormatError, ValueError) as exc:
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
