from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


TREASURY_XML_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml"
    "?data=daily_treasury_yield_curve&field_tdr_date_value={year}"
)
TREASURY_FEED_GUIDE_URL = "https://home.treasury.gov/treasury-daily-interest-rate-xml-feed"
ATOM_NS = "http://www.w3.org/2005/Atom"
DATA_NS = "http://schemas.microsoft.com/ado/2007/08/dataservices"
METADATA_NS = "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
FIELDNAMES = (
    "rate_date",
    "two_year_pct",
    "ten_year_pct",
    "curve_2s10s_bps",
    "source_mode",
    "observed_on",
    "source_url",
)


class TreasuryDataError(ValueError):
    """Raised when an official Treasury yield observation cannot be validated."""


@dataclass(frozen=True)
class TreasuryYield:
    rate_date: date
    two_year_pct: Decimal
    ten_year_pct: Decimal
    curve_2s10s_bps: Decimal
    source_mode: str
    observed_on: date
    source_url: str


def fetch_treasury_yields(year: int, observed_on: date) -> list[TreasuryYield]:
    url = TREASURY_XML_URL.format(year=year)
    request = Request(
        url,
        headers={
            "User-Agent": "MarketWitness/0.1 public-research-monitor",
            "Accept": "application/xml",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            content = response.read()
    except (URLError, TimeoutError, OSError) as exc:
        raise TreasuryDataError(f"Unable to retrieve Treasury yield XML: {exc}") from exc
    return parse_treasury_xml(content, observed_on, "official_live_xml", url)


def load_treasury_snapshot(path: str | Path, observed_on: date) -> list[TreasuryYield]:
    try:
        content = Path(path).read_bytes()
    except OSError as exc:
        raise TreasuryDataError(f"Unable to read Treasury XML snapshot {path}: {exc}") from exc
    return parse_treasury_xml(
        content,
        observed_on,
        "synthetic_fixture",
        "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml",
    )


def parse_treasury_xml(
    content: bytes | str, observed_on: date, source_mode: str, source_url: str
) -> list[TreasuryYield]:
    if source_mode not in {"synthetic_fixture", "official_live_xml"}:
        raise TreasuryDataError(f"Unsupported Treasury source mode: {source_mode}.")
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise TreasuryDataError(f"Treasury yield feed is invalid XML: {exc}") from exc
    records: list[TreasuryYield] = []
    seen: set[date] = set()
    for entry in root.findall(f"{{{ATOM_NS}}}entry"):
        properties = entry.find(
            f"{{{ATOM_NS}}}content/{{{METADATA_NS}}}properties"
        )
        if properties is None:
            raise TreasuryDataError("Treasury yield feed entry lacks properties.")
        raw_date = properties.findtext(f"{{{DATA_NS}}}NEW_DATE", "").split("T", 1)[0]
        raw_two_year = properties.findtext(f"{{{DATA_NS}}}BC_2YEAR", "")
        raw_ten_year = properties.findtext(f"{{{DATA_NS}}}BC_10YEAR", "")
        try:
            rate_date = date.fromisoformat(raw_date)
            two_year = Decimal(raw_two_year)
            ten_year = Decimal(raw_ten_year)
        except (ValueError, InvalidOperation) as exc:
            raise TreasuryDataError("Treasury yield feed entry has invalid date or yield.") from exc
        if rate_date > observed_on:
            raise TreasuryDataError("Treasury yield feed contains a rate after observation date.")
        if rate_date in seen:
            raise TreasuryDataError("Treasury yield feed contains a duplicate rate date.")
        seen.add(rate_date)
        records.append(
            TreasuryYield(
                rate_date=rate_date,
                two_year_pct=two_year,
                ten_year_pct=ten_year,
                curve_2s10s_bps=(ten_year - two_year) * Decimal("100"),
                source_mode=source_mode,
                observed_on=observed_on,
                source_url=source_url,
            )
        )
    if not records:
        raise TreasuryDataError("Treasury yield feed contains no observations.")
    return sorted(records, key=lambda item: item.rate_date)


def load_treasury_csv(path: str | Path) -> list[TreasuryYield]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not set(FIELDNAMES).issubset(reader.fieldnames):
            raise TreasuryDataError(f"{path}: Treasury context CSV is missing required fields.")
        records: list[TreasuryYield] = []
        for row in reader:
            try:
                record = TreasuryYield(
                    rate_date=date.fromisoformat(row["rate_date"]),
                    two_year_pct=Decimal(row["two_year_pct"]),
                    ten_year_pct=Decimal(row["ten_year_pct"]),
                    curve_2s10s_bps=Decimal(row["curve_2s10s_bps"]),
                    source_mode=row["source_mode"].strip(),
                    observed_on=date.fromisoformat(row["observed_on"]),
                    source_url=row["source_url"].strip(),
                )
            except (ValueError, InvalidOperation) as exc:
                raise TreasuryDataError(f"{path}: invalid Treasury context row.") from exc
            if record.source_mode not in {"synthetic_fixture", "official_live_xml"}:
                raise TreasuryDataError(f"{path}: unsupported Treasury context source mode.")
            if record.rate_date > record.observed_on:
                raise TreasuryDataError(f"{path}: Treasury rate is after observation date.")
            records.append(record)
    if len({item.rate_date for item in records}) != len(records):
        raise TreasuryDataError(f"{path}: duplicate Treasury context date.")
    return sorted(records, key=lambda item: item.rate_date)


def write_treasury_csv(path: str | Path, records: list[TreasuryYield]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for item in records:
            writer.writerow(
                {
                    "rate_date": item.rate_date.isoformat(),
                    "two_year_pct": item.two_year_pct,
                    "ten_year_pct": item.ten_year_pct,
                    "curve_2s10s_bps": item.curve_2s10s_bps,
                    "source_mode": item.source_mode,
                    "observed_on": item.observed_on.isoformat(),
                    "source_url": item.source_url,
                }
            )


def write_treasury_report(
    path: str | Path, records: list[TreasuryYield], observed_on: date, source_mode: str
) -> None:
    lines = [
        "# Official Treasury Yield Context",
        "",
        f"- Observed: `{observed_on.isoformat()}`",
        f"- Source mode: `{source_mode}`",
        f"- Daily observations: `{len(records)}`",
        "- Measures: `2Y`, `10Y`, and calculated `2s10s` curve in basis points.",
        "- Boundary: These are official daily yields for temporal context, not proof that a communication caused a rate movement.",
        "",
        "| Date | 2Y | 10Y | 2s10s (bps) |",
        "|---|---:|---:|---:|",
    ]
    for item in reversed(records[-15:]):
        lines.append(
            f"| {item.rate_date.isoformat()} | {item.two_year_pct}% | "
            f"{item.ten_year_pct}% | {item.curve_2s10s_bps} |"
        )
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_treasury_html(
    path: str | Path, records: list[TreasuryYield], observed_on: date, source_mode: str
) -> None:
    rows = "".join(
        f"<tr><td>{item.rate_date.isoformat()}</td><td>{escape(str(item.two_year_pct))}%</td>"
        f"<td>{escape(str(item.ten_year_pct))}%</td><td>{escape(str(item.curve_2s10s_bps))}</td></tr>"
        for item in reversed(records[-20:])
    )
    page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>MarketWitness | Treasury Yield Context</title>
<style>body{{margin:0;background:#070d16;color:#e9f0f5;font:15px Arial,sans-serif}}header,main{{max-width:1040px;margin:auto;padding:32px}}h1{{font-size:44px;margin:10px 0}}p{{color:#9fb0c0;line-height:1.6}}.cards{{display:flex;gap:12px;margin:24px 0}}.card{{background:#121d2c;border:1px solid #27364b;border-radius:14px;padding:16px 20px}}strong{{font-size:28px;color:#58dfb0}}table{{width:100%;border-collapse:collapse;background:#121d2c;border-radius:14px;overflow:hidden}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #27364b}}th{{color:#9fb0c0}}a{{color:#58dfb0}}</style>
<header><p>OFFICIAL MARKET CONTEXT</p><h1>Treasury yields.<br>Observed context.</h1><p>Official daily 2Y and 10Y par yield curve observations. Temporal proximity is not causal evidence or investment advice.</p><div class="cards"><div class="card"><p>Observations</p><strong>{len(records)}</strong></div><div class="card"><p>Latest rate date</p><strong>{escape(records[-1].rate_date.isoformat())}</strong></div><div class="card"><p>Collected on</p><strong>{escape(observed_on.isoformat())}</strong></div></div><p>Source mode: {escape(source_mode)} / <a href="{TREASURY_FEED_GUIDE_URL}">Treasury XML documentation</a></p></header>
<main><table><thead><tr><th>Date</th><th>2Y</th><th>10Y</th><th>2s10s (bps)</th></tr></thead><tbody>{rows}</tbody></table></main></html>"""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page, encoding="utf-8")
