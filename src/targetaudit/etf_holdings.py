from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from html import escape
from pathlib import Path

HOLDING_COLUMNS = {
    "issuer",
    "fund_symbol",
    "fund_name",
    "effective_date",
    "captured_on",
    "position_ticker",
    "position_name",
    "shares",
    "weight_pct",
    "source_frequency",
    "source_url",
}
SOURCE_FREQUENCIES = {
    "daily_official",
    "official_snapshot",
    "regulatory_periodic",
    "synthetic_demo",
}


class EtfHoldingsDataError(ValueError):
    """Raised when ETF holdings evidence cannot be compared safely."""


@dataclass(frozen=True)
class Holding:
    issuer: str
    fund_symbol: str
    fund_name: str
    effective_date: date
    captured_on: date
    position_ticker: str
    position_name: str
    shares: Decimal
    weight_pct: Decimal
    source_frequency: str
    source_url: str


@dataclass(frozen=True)
class HoldingChange:
    issuer: str
    fund_symbol: str
    fund_name: str
    previous_effective_date: date
    current_effective_date: date
    position_ticker: str
    position_name: str
    previous_shares: Decimal | None
    current_shares: Decimal | None
    shares_change: Decimal
    previous_weight_pct: Decimal | None
    current_weight_pct: Decimal | None
    weight_change_pct: Decimal | None
    change_type: str
    source_frequency: str
    source_url: str


def load_holdings_snapshot(path: str | Path, as_of: date) -> list[Holding]:
    try:
        with Path(path).open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            missing = sorted(HOLDING_COLUMNS - set(reader.fieldnames or []))
            if missing:
                raise EtfHoldingsDataError(
                    f"{path}: missing columns: {', '.join(missing)}"
                )
            rows = [_parse_holding(path, row, index, as_of) for index, row in enumerate(reader, 2)]
    except OSError as exc:
        raise EtfHoldingsDataError(f"Unable to read ETF snapshot {path}: {exc}") from exc
    if not rows:
        raise EtfHoldingsDataError(f"{path}: snapshot contains no holdings")
    identity = {
        (
            row.issuer,
            row.fund_symbol,
            row.fund_name,
            row.effective_date,
            row.captured_on,
            row.source_frequency,
            row.source_url,
        )
        for row in rows
    }
    if len(identity) != 1:
        raise EtfHoldingsDataError(
            f"{path}: one snapshot must contain one fund, date and source layer"
        )
    seen: set[str] = set()
    for row in rows:
        ticker = row.position_ticker.casefold()
        if ticker in seen:
            raise EtfHoldingsDataError(
                f"{path}: duplicate holding ticker {row.position_ticker}"
            )
        seen.add(ticker)
    return rows


def compare_holdings(previous: list[Holding], current: list[Holding]) -> list[HoldingChange]:
    old_head, new_head = previous[0], current[0]
    if (old_head.issuer, old_head.fund_symbol, old_head.fund_name) != (
        new_head.issuer,
        new_head.fund_symbol,
        new_head.fund_name,
    ):
        raise EtfHoldingsDataError("ETF snapshots must describe the same fund")
    if new_head.effective_date <= old_head.effective_date:
        raise EtfHoldingsDataError("Current ETF snapshot must be newer than previous snapshot")
    if new_head.source_frequency != old_head.source_frequency:
        raise EtfHoldingsDataError("ETF snapshots must use the same source-frequency layer")
    old_map = {item.position_ticker.casefold(): item for item in previous}
    new_map = {item.position_ticker.casefold(): item for item in current}
    changes: list[HoldingChange] = []
    for ticker in sorted(set(old_map) | set(new_map)):
        old = old_map.get(ticker)
        new = new_map.get(ticker)
        old_shares = old.shares if old else None
        new_shares = new.shares if new else None
        old_weight = old.weight_pct if old else None
        new_weight = new.weight_pct if new else None
        share_delta = (new_shares or Decimal("0")) - (old_shares or Decimal("0"))
        weight_delta = (
            new_weight - old_weight
            if old_weight is not None and new_weight is not None
            else None
        )
        if old and new and share_delta == 0 and weight_delta == 0:
            continue
        if old is None:
            change_type = "new_position"
        elif new is None:
            change_type = "removed_position"
        elif share_delta > 0:
            change_type = "increased"
        elif share_delta < 0:
            change_type = "decreased"
        else:
            change_type = "weight_changed"
        evidence = new or old
        assert evidence is not None
        changes.append(
            HoldingChange(
                issuer=new_head.issuer,
                fund_symbol=new_head.fund_symbol,
                fund_name=new_head.fund_name,
                previous_effective_date=old_head.effective_date,
                current_effective_date=new_head.effective_date,
                position_ticker=evidence.position_ticker,
                position_name=evidence.position_name,
                previous_shares=old_shares,
                current_shares=new_shares,
                shares_change=share_delta,
                previous_weight_pct=old_weight,
                current_weight_pct=new_weight,
                weight_change_pct=weight_delta,
                change_type=change_type,
                source_frequency=new_head.source_frequency,
                source_url=new_head.source_url,
            )
        )
    priority = {
        "new_position": 0,
        "increased": 1,
        "decreased": 2,
        "removed_position": 3,
        "weight_changed": 4,
    }
    return sorted(changes, key=lambda change: (priority[change.change_type], change.position_ticker))


def write_changes_csv(path: str | Path, changes: list[HoldingChange]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(HoldingChange.__annotations__))
        writer.writeheader()
        for change in changes:
            row = dict(change.__dict__)
            row["previous_effective_date"] = change.previous_effective_date.isoformat()
            row["current_effective_date"] = change.current_effective_date.isoformat()
            writer.writerow(row)


def render_holdings_report(
    previous: list[Holding], current: list[Holding], changes: list[HoldingChange], as_of: date
) -> str:
    head = current[0]
    counts = Counter(change.change_type for change in changes)
    lines = [
        "# ETF Holdings Activity",
        "",
        f"- Report cutoff: `{as_of.isoformat()}`",
        f"- Fund: `{head.fund_symbol}` - {head.fund_name}",
        f"- Issuer: {head.issuer}",
        f"- Previous effective date: `{previous[0].effective_date.isoformat()}`",
        f"- Current effective date: `{head.effective_date.isoformat()}`",
        f"- Source frequency: `{head.source_frequency}`",
        f"- Observed changed positions: `{len(changes)}`",
        "",
        "These are observed holdings changes between published snapshots, not",
        "confirmed manager trades. Differences can reflect creations/redemptions,",
        "corporate actions, derivatives, cash or publication adjustments.",
        "",
        "## Change Summary",
        "",
        " / ".join(
            f"{label}: `{counts[key]}`"
            for label, key in (
                ("New", "new_position"),
                ("Increased", "increased"),
                ("Decreased", "decreased"),
                ("Removed", "removed_position"),
                ("Weight-only", "weight_changed"),
            )
        ),
        "",
        "## Observed Positions",
        "",
        "| Change | Position | Previous Shares | Current Shares | Share Delta | Previous Weight | Current Weight | Weight Delta |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    if not changes:
        lines.append("| - | No changed positions detected | - | - | - | - | - | - |")
    for item in changes:
        lines.append(
            f"| `{item.change_type}` | {item.position_ticker} - {item.position_name} | "
            f"{_number(item.previous_shares)} | {_number(item.current_shares)} | "
            f"{_signed(item.shares_change)} | {_percent(item.previous_weight_pct)} | "
            f"{_percent(item.current_weight_pct)} | {_signed_percent(item.weight_change_pct)} |"
        )
    lines.extend(["", f"Source link for current snapshot: [{head.source_url}]({head.source_url})"])
    return "\n".join(lines) + "\n"


def write_holdings_report(
    path: str | Path,
    previous: list[Holding],
    current: list[Holding],
    changes: list[HoldingChange],
    as_of: date,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_holdings_report(previous, current, changes, as_of), encoding="utf-8"
    )


def render_holdings_html(
    previous: list[Holding], current: list[Holding], changes: list[HoldingChange], as_of: date
) -> str:
    head = current[0]
    counts = Counter(change.change_type for change in changes)
    cards = "".join(
        f'<article class="card {key}"><p>{label}</p><strong>{counts[key]}</strong></article>'
        for label, key in (
            ("New positions", "new_position"),
            ("Increased", "increased"),
            ("Decreased", "decreased"),
            ("Removed", "removed_position"),
        )
    )
    rows = "".join(
        "<tr>"
        f'<td><span class="badge {escape(item.change_type)}">{escape(item.change_type)}</span></td>'
        f"<td><strong>{escape(item.position_ticker)}</strong><small>{escape(item.position_name)}</small></td>"
        f"<td>{escape(_number(item.previous_shares))}</td>"
        f"<td>{escape(_number(item.current_shares))}</td>"
        f"<td>{escape(_signed(item.shares_change))}</td>"
        f"<td>{escape(_percent(item.previous_weight_pct))}</td>"
        f"<td>{escape(_percent(item.current_weight_pct))}</td>"
        f"<td>{escape(_signed_percent(item.weight_change_pct))}</td>"
        "</tr>"
        for item in changes
    )
    if not rows:
        rows = '<tr><td colspan="8">No changed positions detected in these snapshots.</td></tr>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | ETF Holdings Activity</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;--rose:#f48687;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:820px}}
.cards{{display:flex;gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:175px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}.decreased strong,.removed_position strong{{color:var(--rose)}}.meta span{{margin-right:18px}}
.views{{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}}.views a{{border:1px solid var(--line);border-radius:999px;padding:8px 13px;background:var(--panel)}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}td small{{display:block;color:var(--muted)}}.badge{{border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}.new_position{{color:var(--mint);background:rgba(86,218,172,.12)}}.increased{{color:var(--blue);background:rgba(98,166,255,.12)}}.decreased,.removed_position{{color:var(--rose);background:rgba(244,134,135,.12)}}.weight_changed{{color:var(--gold);background:rgba(240,188,98,.12)}}a{{color:var(--mint);text-decoration:none}}
@media(max-width:800px){{.cards{{display:block}}.card{{margin-bottom:12px}}.table-wrap{{overflow-x:auto}}table{{min-width:980px}}}}
</style></head><body><header><nav>TargetAudit / ETF Holdings Activity</nav>
<h1>ETF holdings.<br>Observed changes.</h1>
<p class="lead">Compare published fund holdings snapshots with effective dates and source frequency shown up front.</p>
<p class="meta"><span>{escape(head.fund_symbol)} / {escape(head.issuer)}</span><span>Current {head.effective_date.isoformat()}</span><span>Previous {previous[0].effective_date.isoformat()}</span><span>{escape(head.source_frequency)}</span></p>
<section class="cards">{cards}</section></header>
<main><p class="notice">Observed holdings changes are not confirmed manager trades. They can reflect creations/redemptions, corporate actions, derivatives, cash or publication adjustments. Demo snapshots are synthetic until an approved official connector is enabled.</p>
<nav class="views" aria-label="ETF evidence views"><a href="/dashboard/etf/xlf-demo">XLF sandbox</a><a href="/dashboard/etf/iyf-demo">IYF sandbox</a><a href="/dashboard/etf/nport-recent">N-PORT recent</a><a href="/dashboard/etf-regulatory">N-PORT history</a></nav>
<h2>Changed positions</h2><div class="table-wrap"><table><thead><tr><th>Change</th><th>Holding</th><th>Previous shares</th><th>Current shares</th><th>Delta</th><th>Previous weight</th><th>Current weight</th><th>Delta</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="meta">Report cutoff {as_of.isoformat()} / <a href="{escape(head.source_url)}">current snapshot source</a></p></main></body></html>"""


def write_holdings_html(
    path: str | Path,
    previous: list[Holding],
    current: list[Holding],
    changes: list[HoldingChange],
    as_of: date,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_holdings_html(previous, current, changes, as_of), encoding="utf-8"
    )


def _parse_holding(path: str | Path, row: dict[str, str], index: int, as_of: date) -> Holding:
    required = [row.get(column, "").strip() for column in HOLDING_COLUMNS]
    if not all(required):
        raise EtfHoldingsDataError(f"{path}: incomplete holding row {index}")
    try:
        effective_date = date.fromisoformat(row["effective_date"].strip())
        captured_on = date.fromisoformat(row["captured_on"].strip())
        shares = Decimal(row["shares"].strip())
        weight_pct = Decimal(row["weight_pct"].strip())
    except (ValueError, InvalidOperation) as exc:
        raise EtfHoldingsDataError(f"{path}: invalid numeric or date value on row {index}") from exc
    if not shares.is_finite() or not weight_pct.is_finite() or shares < 0:
        raise EtfHoldingsDataError(f"{path}: invalid holding amount on row {index}")
    if weight_pct < 0 or weight_pct > 100:
        raise EtfHoldingsDataError(f"{path}: invalid holding weight on row {index}")
    if captured_on > as_of:
        raise EtfHoldingsDataError(f"{path}: holding capture exceeds evidence cutoff on row {index}")
    frequency = row["source_frequency"].strip()
    if frequency not in SOURCE_FREQUENCIES:
        raise EtfHoldingsDataError(f"{path}: unsupported source frequency on row {index}")
    source_url = row["source_url"].strip()
    if not source_url.startswith("https://"):
        raise EtfHoldingsDataError(f"{path}: non-HTTPS source URL on row {index}")
    return Holding(
        issuer=row["issuer"].strip(),
        fund_symbol=row["fund_symbol"].strip(),
        fund_name=row["fund_name"].strip(),
        effective_date=effective_date,
        captured_on=captured_on,
        position_ticker=row["position_ticker"].strip(),
        position_name=row["position_name"].strip(),
        shares=shares,
        weight_pct=weight_pct,
        source_frequency=frequency,
        source_url=source_url,
    )


def _number(value: Decimal | None) -> str:
    return "-" if value is None else f"{value:,.0f}"


def _signed(value: Decimal) -> str:
    return f"{value:+,.0f}"


def _percent(value: Decimal | None) -> str:
    return "-" if value is None else f"{value:.2f}%"


def _signed_percent(value: Decimal | None) -> str:
    return "-" if value is None else f"{value:+.2f}%"
