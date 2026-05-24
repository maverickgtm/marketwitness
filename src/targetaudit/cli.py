from __future__ import annotations

import argparse
from datetime import date

from .csvio import DataFormatError, load_prices, load_targets, write_evaluations
from .evaluator import evaluate_all
from .ipo_watch import (
    IpoWatchDataError,
    load_ipo_watch,
    write_ipo_watch_html,
    write_ipo_watch_report,
)
from .providers.sec import SecDataError, fetch_company_ticker_map, write_company_ticker_map
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
        required=True,
        help='Declared SEC user agent, for example "TargetAudit contact@example.com".',
    )
    sec_parser.add_argument("--output", required=True, help="Output CSV path.")
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
    args = parser.parse_args()

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
