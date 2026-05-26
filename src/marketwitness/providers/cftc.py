from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


CFTC_COT_HOME_URL = "https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm"
CFTC_API_GUIDE_URL = "https://publicreporting.cftc.gov/stories/s/User-s-Guide/p2fg-u73y/"
CFTC_RESOURCE_ROOT = "https://publicreporting.cftc.gov/resource"
TRACKED_MARKETS = {
    "wti": {
        "label": "WTI Crude Oil",
        "contract_code": "067651",
        "dataset": "72hh-3qpy",
        "report_family": "Disaggregated Futures Only",
        "primary_label": "Managed Money",
        "primary_long": "m_money_positions_long_all",
        "primary_short": "m_money_positions_short_all",
        "secondary_label": "Producer / Merchant",
        "secondary_long": "prod_merc_positions_long",
        "secondary_short": "prod_merc_positions_short",
    },
    "gold": {
        "label": "Gold",
        "contract_code": "088691",
        "dataset": "72hh-3qpy",
        "report_family": "Disaggregated Futures Only",
        "primary_label": "Managed Money",
        "primary_long": "m_money_positions_long_all",
        "primary_short": "m_money_positions_short_all",
        "secondary_label": "Producer / Merchant",
        "secondary_long": "prod_merc_positions_long",
        "secondary_short": "prod_merc_positions_short",
    },
    "usd-index": {
        "label": "U.S. Dollar Index",
        "contract_code": "098662",
        "dataset": "gpe5-46if",
        "report_family": "Traders in Financial Futures Only",
        "primary_label": "Leveraged Money",
        "primary_long": "lev_money_positions_long",
        "primary_short": "lev_money_positions_short",
        "secondary_label": "Asset Manager",
        "secondary_long": "asset_mgr_positions_long",
        "secondary_short": "asset_mgr_positions_short",
    },
}
FIELDNAMES = (
    "market_key",
    "market_label",
    "contract_market_code",
    "contract_name",
    "report_family",
    "report_date",
    "open_interest",
    "primary_label",
    "primary_long",
    "primary_short",
    "primary_net",
    "secondary_label",
    "secondary_long",
    "secondary_short",
    "secondary_net",
    "source_mode",
    "observed_on",
    "source_url",
)


class CftcDataError(ValueError):
    """Raised when official CFTC COT observations cannot be validated."""


@dataclass(frozen=True)
class CftcPosition:
    market_key: str
    market_label: str
    contract_market_code: str
    contract_name: str
    report_family: str
    report_date: date
    open_interest: int
    primary_label: str
    primary_long: int
    primary_short: int
    primary_net: int
    secondary_label: str
    secondary_long: int
    secondary_short: int
    secondary_net: int
    source_mode: str
    observed_on: date
    source_url: str


def fetch_cftc_positions(observed_on: date, limit: int = 60) -> list[CftcPosition]:
    records: list[CftcPosition] = []
    for market_key, definition in TRACKED_MARKETS.items():
        query = urlencode(
            {
                "$limit": str(limit),
                "$order": "report_date_as_yyyy_mm_dd DESC",
                "$where": f"cftc_contract_market_code='{definition['contract_code']}'",
            }
        )
        url = f"{CFTC_RESOURCE_ROOT}/{definition['dataset']}.json?{query}"
        request = Request(
            url,
            headers={
                "User-Agent": "MarketWitness/0.1 public-research-monitor",
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=60) as response:
                payload = json.load(response)
        except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            raise CftcDataError(f"Unable to retrieve CFTC COT data for {market_key}: {exc}") from exc
        records.extend(
            parse_cftc_payload(payload, market_key, observed_on, "official_live_json", url)
        )
    return _validate_collection(records)


def load_cftc_snapshots(
    disaggregated_path: str | Path, financial_path: str | Path, observed_on: date
) -> list[CftcPosition]:
    try:
        disaggregated = json.loads(Path(disaggregated_path).read_text(encoding="utf-8"))
        financial = json.loads(Path(financial_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CftcDataError(f"Unable to read CFTC COT fixture: {exc}") from exc
    records = parse_cftc_payload(disaggregated, "wti", observed_on, "synthetic_fixture", "")
    records.extend(parse_cftc_payload(disaggregated, "gold", observed_on, "synthetic_fixture", ""))
    records.extend(
        parse_cftc_payload(financial, "usd-index", observed_on, "synthetic_fixture", "")
    )
    return _validate_collection(records)


def parse_cftc_payload(
    payload: object,
    market_key: str,
    observed_on: date,
    source_mode: str,
    source_url: str,
) -> list[CftcPosition]:
    if market_key not in TRACKED_MARKETS:
        raise CftcDataError(f"Unsupported CFTC tracked market: {market_key}.")
    if source_mode not in {"official_live_json", "synthetic_fixture"}:
        raise CftcDataError(f"Unsupported CFTC source mode: {source_mode}.")
    if not isinstance(payload, list):
        raise CftcDataError("CFTC COT response is not a JSON array.")
    definition = TRACKED_MARKETS[market_key]
    canonical_url = (
        source_url
        or f"{CFTC_RESOURCE_ROOT}/{definition['dataset']}.json"
    )
    records: list[CftcPosition] = []
    for row in payload:
        if not isinstance(row, dict) or row.get("cftc_contract_market_code") != definition["contract_code"]:
            continue
        try:
            report_date = date.fromisoformat(str(row["report_date_as_yyyy_mm_dd"]).split("T", 1)[0])
            open_interest = int(row["open_interest_all"])
            primary_long = int(row[definition["primary_long"]])
            primary_short = int(row[definition["primary_short"]])
            secondary_long = int(row[definition["secondary_long"]])
            secondary_short = int(row[definition["secondary_short"]])
        except (KeyError, ValueError, TypeError) as exc:
            raise CftcDataError(f"CFTC COT row for {market_key} has invalid required fields.") from exc
        if report_date > observed_on:
            raise CftcDataError("CFTC COT data contains a report after observation date.")
        records.append(
            CftcPosition(
                market_key=market_key,
                market_label=definition["label"],
                contract_market_code=definition["contract_code"],
                contract_name=str(row.get("market_and_exchange_names", "")).strip(),
                report_family=definition["report_family"],
                report_date=report_date,
                open_interest=open_interest,
                primary_label=definition["primary_label"],
                primary_long=primary_long,
                primary_short=primary_short,
                primary_net=primary_long - primary_short,
                secondary_label=definition["secondary_label"],
                secondary_long=secondary_long,
                secondary_short=secondary_short,
                secondary_net=secondary_long - secondary_short,
                source_mode=source_mode,
                observed_on=observed_on,
                source_url=canonical_url,
            )
        )
    if not records:
        raise CftcDataError(f"CFTC COT response contains no rows for {definition['label']}.")
    return records


def load_cftc_csv(path: str | Path) -> list[CftcPosition]:
    try:
        with Path(path).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        raise CftcDataError(f"Unable to read CFTC positioning CSV: {exc}") from exc
    records: list[CftcPosition] = []
    for row in rows:
        if not set(FIELDNAMES).issubset(row):
            raise CftcDataError("CFTC positioning CSV is missing required fields.")
        try:
            records.append(
                CftcPosition(
                    market_key=row["market_key"].strip(),
                    market_label=row["market_label"].strip(),
                    contract_market_code=row["contract_market_code"].strip(),
                    contract_name=row["contract_name"].strip(),
                    report_family=row["report_family"].strip(),
                    report_date=date.fromisoformat(row["report_date"]),
                    open_interest=int(row["open_interest"]),
                    primary_label=row["primary_label"].strip(),
                    primary_long=int(row["primary_long"]),
                    primary_short=int(row["primary_short"]),
                    primary_net=int(row["primary_net"]),
                    secondary_label=row["secondary_label"].strip(),
                    secondary_long=int(row["secondary_long"]),
                    secondary_short=int(row["secondary_short"]),
                    secondary_net=int(row["secondary_net"]),
                    source_mode=row["source_mode"].strip(),
                    observed_on=date.fromisoformat(row["observed_on"]),
                    source_url=row["source_url"].strip(),
                )
            )
        except ValueError as exc:
            raise CftcDataError("CFTC positioning CSV has an invalid row.") from exc
    return _validate_collection(records)


def write_cftc_csv(path: str | Path, records: list[CftcPosition]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    **record.__dict__,
                    "report_date": record.report_date.isoformat(),
                    "observed_on": record.observed_on.isoformat(),
                }
            )


def build_cftc_snapshot(
    records: list[CftcPosition], market: str = "wti", weeks: int = 1
) -> dict[str, object]:
    if market not in TRACKED_MARKETS:
        raise CftcDataError("CFTC market must be wti, gold or usd-index.")
    if weeks not in {1, 4, 12, 52}:
        raise CftcDataError("CFTC comparison window must be 1, 4, 12 or 52 weeks.")
    selected = sorted(
        (item for item in records if item.market_key == market),
        key=lambda item: item.report_date,
    )
    if not selected:
        raise CftcDataError(f"CFTC artifact has no observations for {market}.")
    latest = selected[-1]
    prior = selected[-weeks - 1] if len(selected) > weeks else None
    modes = {item.source_mode for item in records}
    comparison = None
    if prior:
        comparison = {
            "weeks": weeks,
            "reference_date": prior.report_date.isoformat(),
            "latest_date": latest.report_date.isoformat(),
            "primary_net_change": latest.primary_net - prior.primary_net,
            "secondary_net_change": latest.secondary_net - prior.secondary_net,
            "open_interest_change": latest.open_interest - prior.open_interest,
        }
    return {
        "available": True,
        "product": "COT Positioning Lab",
        "data_mode": (
            "Official CFTC weekly COT observations"
            if modes == {"official_live_json"}
            else "Synthetic reproducible COT fixture"
            if modes == {"synthetic_fixture"}
            else "Mixed validation positioning archive"
        ),
        "as_of": max(item.observed_on for item in records).isoformat(),
        "selected_market": market,
        "selected_weeks": weeks,
        "market_label": latest.market_label,
        "contract_name": latest.contract_name,
        "report_family": latest.report_family,
        "latest_report_date": latest.report_date.isoformat(),
        "latest": _position_payload(latest),
        "comparison_available": comparison is not None,
        "comparison": comparison,
        "history": [_position_payload(item) for item in reversed(selected[-12:])],
        "covered_markets": [
            {"key": key, "label": definition["label"]}
            for key, definition in TRACKED_MARKETS.items()
        ],
        "publication_boundary": (
            "CFTC Commitments of Traders observations are weekly, delayed and aggregated by "
            "participant category. Net positioning is context only; it does not identify "
            "individual trades, price direction or a position to take."
        ),
    }


def write_cftc_report(
    path: str | Path, records: list[CftcPosition], observed_on: date, source_mode: str
) -> None:
    lines = [
        "# CFTC Commitments Of Traders Positioning",
        "",
        f"- Observed: `{observed_on.isoformat()}`",
        f"- Source mode: `{source_mode}`",
        f"- Normalized weekly observations: `{len(records)}`",
        "- Coverage: `WTI Crude Oil`, `Gold`, and `U.S. Dollar Index` benchmark contracts only.",
        "",
        "CFTC observations are weekly, delayed and aggregated. They are context, not trade recommendations.",
        "",
        "| Market | Report date | Primary category | Net contracts | Net / open interest |",
        "|---|---|---|---:|---:|",
    ]
    for market in TRACKED_MARKETS:
        latest = build_cftc_snapshot(records, market)["latest"]
        lines.append(
            f"| {latest['market_label']} | {latest['report_date']} | {latest['primary_label']} | "
            f"{latest['primary_net']:,} | {latest['primary_net_pct_oi']}% |"
        )
    lines.extend(["", f"Official documentation: {CFTC_API_GUIDE_URL}", ""])
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines), encoding="utf-8")


def write_cftc_html(
    path: str | Path, records: list[CftcPosition], observed_on: date, source_mode: str
) -> None:
    rows = ""
    for key in TRACKED_MARKETS:
        item = build_cftc_snapshot(records, key)["latest"]
        rows += (
            f"<tr><td>{escape(str(item['market_label']))}</td><td>{item['report_date']}</td>"
            f"<td>{escape(str(item['primary_label']))}</td><td>{item['primary_net']:,}</td>"
            f"<td>{item['primary_net_pct_oi']}%</td></tr>"
        )
    page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>MarketWitness | CFTC COT Positioning</title>
<style>body{{margin:0;background:#070d16;color:#e9f0f5;font:15px Arial,sans-serif}}header,main{{max-width:1040px;margin:auto;padding:32px}}h1{{font-size:44px;margin:10px 0}}p{{color:#9fb0c0;line-height:1.6}}strong{{color:#58dfb0}}table{{width:100%;border-collapse:collapse;background:#121d2c;border-radius:14px;overflow:hidden}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #27364b}}th{{color:#9fb0c0}}a{{color:#58dfb0}}</style>
<header><p>OFFICIAL WEEKLY POSITIONING CONTEXT</p><h1>CFTC COT.<br>Benchmark positioning.</h1><p>WTI, Gold and U.S. Dollar Index participant-category net positions. Aggregated and delayed data are not a trading recommendation.</p><p>Collected on <strong>{observed_on.isoformat()}</strong> / {escape(source_mode)} / <a href="{CFTC_API_GUIDE_URL}">Official API guide</a></p></header>
<main><table><thead><tr><th>Market</th><th>Report date</th><th>Category</th><th>Net contracts</th><th>Net / OI</th></tr></thead><tbody>{rows}</tbody></table></main></html>"""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page, encoding="utf-8")


def _position_payload(record: CftcPosition) -> dict[str, object]:
    return {
        "market_key": record.market_key,
        "market_label": record.market_label,
        "contract_name": record.contract_name,
        "report_date": record.report_date.isoformat(),
        "open_interest": record.open_interest,
        "primary_label": record.primary_label,
        "primary_long": record.primary_long,
        "primary_short": record.primary_short,
        "primary_net": record.primary_net,
        "primary_net_pct_oi": str(
            (Decimal(record.primary_net) / Decimal(record.open_interest) * Decimal("100")).quantize(
                Decimal("0.01")
            )
        ),
        "secondary_label": record.secondary_label,
        "secondary_net": record.secondary_net,
        "source_url": record.source_url,
    }


def _validate_collection(records: list[CftcPosition]) -> list[CftcPosition]:
    if not records:
        raise CftcDataError("CFTC positioning collection contains no observations.")
    seen: set[tuple[str, date]] = set()
    present = {item.market_key for item in records}
    if present != set(TRACKED_MARKETS):
        raise CftcDataError("CFTC positioning collection must contain all tracked benchmark markets.")
    for record in records:
        if record.source_mode not in {"official_live_json", "synthetic_fixture"}:
            raise CftcDataError("CFTC positioning collection has an unsupported source mode.")
        if record.report_date > record.observed_on:
            raise CftcDataError("CFTC COT data contains a report after observation date.")
        if record.primary_net != record.primary_long - record.primary_short:
            raise CftcDataError("CFTC positioning primary net does not match its source positions.")
        if record.secondary_net != record.secondary_long - record.secondary_short:
            raise CftcDataError("CFTC positioning secondary net does not match its source positions.")
        marker = (record.market_key, record.report_date)
        if marker in seen:
            raise CftcDataError("CFTC positioning collection contains duplicate observations.")
        seen.add(marker)
    return sorted(records, key=lambda item: (item.market_key, item.report_date))
