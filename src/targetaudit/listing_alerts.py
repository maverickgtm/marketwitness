from __future__ import annotations

import csv
import shutil
from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

MARKETS = ("HKEX", "LSE", "ASX", "TSX", "JPX", "EDINET", "CVM", "ESMA", "SGX")
SNAPSHOT_FILENAMES = {
    "HKEX": "hkex-monitor.csv",
    "LSE": "lse-upcoming.csv",
    "ASX": "asx-monitor.csv",
    "TSX": "tsx-monitor.csv",
    "JPX": "jpx-monitor.csv",
    "EDINET": "edinet-monitor.csv",
    "CVM": "cvm-monitor.csv",
    "ESMA": "esma-monitor.csv",
    "SGX": "sgx-monitor.csv",
}
EDINET_STATUS_LABELS = {
    "securities_registration_statement": "Initial registration",
    "amended_securities_registration_statement": "Amendment",
    "registration_withdrawal_request": "Withdrawal request",
}
CVM_STATUS_LABELS = {
    "offering_recorded": "Offering recorded",
    "offering_closed": "Offering closed",
    "offering_cancelled_or_withdrawn": "Offering cancelled or withdrawn",
}
ESMA_STATUS_LABELS = {
    "initial_admission_regulated_market_review": "Initial regulated-market admission review",
    "initial_admission_mtf_review": "Initial MTF admission review",
    "initial_offer_without_admission_review": "Initial offer review",
    "secondary_issuance_review": "Secondary issuance review",
    "secondary_offer_without_admission_review": "Secondary offer review",
    "equity_prospectus_review": "Equity prospectus review",
}


class ListingAlertsDataError(ValueError):
    """Raised when global listing snapshots cannot be compared safely."""


@dataclass(frozen=True)
class ListingSignal:
    market: str
    entity_key: str
    company_name: str
    status: str
    event_detail: str
    source_url: str


@dataclass(frozen=True)
class ListingAlert:
    market: str
    change_type: str
    company_name: str
    previous_status: str
    current_status: str
    previous_detail: str
    current_detail: str
    review_action: str
    source_url: str


def load_current_signals(paths: dict[str, str | Path]) -> list[ListingSignal]:
    signals: list[ListingSignal] = []
    for market in MARKETS:
        try:
            path = paths[market]
        except KeyError as exc:
            raise ListingAlertsDataError(f"Missing current CSV for {market}.") from exc
        signals.extend(_load_market_csv(market, path))
    return signals


def load_snapshot_directory(path: str | Path) -> list[ListingSignal]:
    directory = Path(path)
    if not directory.exists():
        raise ListingAlertsDataError(f"Previous snapshot directory does not exist: {path}")
    return load_current_signals(
        {
            market: directory / filename
            for market, filename in SNAPSHOT_FILENAMES.items()
        }
    )


def latest_previous_snapshot(history_dir: str | Path, as_of: date) -> Path | None:
    history = Path(history_dir)
    if not history.exists():
        return None
    candidates: list[tuple[date, Path]] = []
    for child in history.iterdir():
        if not child.is_dir():
            continue
        try:
            observed_on = date.fromisoformat(child.name)
        except ValueError:
            continue
        if observed_on < as_of:
            candidates.append((observed_on, child))
    return max(candidates, default=(None, None))[1]


def archive_snapshot(
    history_dir: str | Path, paths: dict[str, str | Path], as_of: date
) -> Path:
    destination = Path(history_dir) / as_of.isoformat()
    destination.mkdir(parents=True, exist_ok=True)
    for market, filename in SNAPSHOT_FILENAMES.items():
        source = Path(paths[market])
        if not source.exists():
            raise ListingAlertsDataError(f"Cannot archive missing {market} CSV: {source}")
        shutil.copyfile(source, destination / filename)
    return destination


def compare_signals(
    current: list[ListingSignal], previous: list[ListingSignal] | None
) -> list[ListingAlert]:
    if previous is None:
        return []
    current_map = _signal_map(current)
    previous_map = _signal_map(previous)
    alerts: list[ListingAlert] = []
    for key, item in current_map.items():
        old = previous_map.get(key)
        if old is None:
            alerts.append(_alert("new", None, item))
        elif (item.status, item.event_detail) != (old.status, old.event_detail):
            alerts.append(_alert("changed", old, item))
    for key, old in previous_map.items():
        if key not in current_map:
            alerts.append(_alert("removed_from_feed_review", old, None))
    priority = {"changed": 0, "new": 1, "removed_from_feed_review": 2}
    return sorted(
        alerts,
        key=lambda item: (
            priority[item.change_type],
            item.market,
            item.company_name.casefold(),
        ),
    )


def write_alerts_csv(path: str | Path, alerts: list[ListingAlert]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(ListingAlert.__annotations__))
        writer.writeheader()
        for alert in alerts:
            writer.writerow(alert.__dict__)


def render_alerts_report(
    alerts: list[ListingAlert],
    current: list[ListingSignal],
    as_of: date,
    baseline_label: str,
) -> str:
    counts = Counter(alert.change_type for alert in alerts)
    market_counts = Counter(signal.market for signal in current)
    lines = [
        "# Global Listings Alerts",
        "",
        f"- Observation date: `{as_of.isoformat()}`",
        f"- Compared against: `{baseline_label}`",
        f"- New records: `{counts['new']}`",
        f"- Changed records: `{counts['changed']}`",
        f"- Records no longer in current feed, requiring review: `{counts['removed_from_feed_review']}`",
        "",
        "This change log compares normalized evidence snapshots. A record disappearing",
        "from an upcoming or documentary feed is not automatically a withdrawal,",
        "listing completion or investment signal; it requires source review. Demo",
        "fixtures explicitly labelled synthetic are not public filing evidence.",
        "",
        "## Current Coverage",
        "",
    ]
    lines.append(
        " / ".join(f"{market}: `{market_counts[market]}`" for market in MARKETS)
    )
    lines.extend(
        [
            "",
            "## Review Queue",
            "",
            "| Market | Change | Company | Previous State | Current State | Review Action |",
            "|---|---|---|---|---|---|",
        ]
    )
    if not alerts:
        lines.append("| - | - | No comparable changes detected | - | - | Continue monitoring |")
    for alert in alerts:
        lines.append(
            f"| {alert.market} | `{alert.change_type}` | {alert.company_name} | "
            f"{alert.previous_status or '-'} | {alert.current_status or '-'} | "
            f"{alert.review_action} |"
        )
    return "\n".join(lines) + "\n"


def write_alerts_report(
    path: str | Path,
    alerts: list[ListingAlert],
    current: list[ListingSignal],
    as_of: date,
    baseline_label: str,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_alerts_report(alerts, current, as_of, baseline_label), encoding="utf-8"
    )


def render_alerts_html(
    alerts: list[ListingAlert],
    current: list[ListingSignal],
    as_of: date,
    baseline_label: str,
) -> str:
    counts = Counter(alert.change_type for alert in alerts)
    market_counts = Counter(signal.market for signal in current)
    cards = "".join(
        f'<article class="card"><p>{label}</p><strong>{counts[key]}</strong></article>'
        for label, key in (
            ("New", "new"),
            ("Changed", "changed"),
            ("Review removals", "removed_from_feed_review"),
        )
    )
    coverage = "".join(
        f'<span class="market"><strong>{market}</strong> {market_counts[market]}</span>'
        for market in MARKETS
    )
    rows = "".join(
        "<tr>"
        f"<td>{escape(item.market)}</td>"
        f'<td><span class="badge {escape(item.change_type)}">{escape(item.change_type)}</span></td>'
        f"<td><strong>{escape(item.company_name)}</strong><small>{escape(item.current_detail or item.previous_detail)}</small></td>"
        f"<td>{escape(_display_status(item.market, item.previous_status))}</td>"
        f"<td>{escape(_display_status(item.market, item.current_status))}</td>"
        f"<td>{escape(item.review_action)}</td>"
        f'<td><a href="{escape(item.source_url)}">Source</a></td>'
        "</tr>"
        for item in alerts
    )
    if not rows:
        rows = '<tr><td colspan="7">No comparable changes detected. Continue monitoring official sources.</td></tr>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | Global Listings Alerts</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;--rose:#f48687;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:800px}}
.cards{{display:flex;gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:200px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}
.coverage{{display:flex;flex-wrap:wrap;gap:12px;margin:28px 0}}.market{{background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:7px 13px;color:var(--muted)}}.market strong{{color:var(--text);margin-right:7px}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}td small{{display:block;color:var(--muted)}}a{{color:var(--mint);text-decoration:none}}.badge{{border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}.new{{color:var(--mint);background:rgba(86,218,172,.12)}}.changed{{color:var(--gold);background:rgba(240,188,98,.12)}}.removed_from_feed_review{{color:var(--rose);background:rgba(244,134,135,.12)}}
@media(max-width:800px){{.cards{{display:block}}.card{{margin-bottom:12px}}.table-wrap{{overflow:visible;background:transparent;border:0}}table,tbody,tr,td{{display:block;width:100%}}thead{{display:none}}tr{{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin:12px 0;padding:8px 14px}}td{{border:0;padding:7px 0;overflow-wrap:anywhere}}td::before{{display:block;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px}}td:nth-child(1)::before{{content:"Market"}}td:nth-child(2)::before{{content:"Change"}}td:nth-child(3)::before{{content:"Issuer"}}td:nth-child(4)::before{{content:"Previous"}}td:nth-child(5)::before{{content:"Current"}}td:nth-child(6)::before{{content:"Next step"}}td:nth-child(7)::before{{content:"Evidence"}}.badge{{display:inline-block;white-space:normal}}}}
</style></head><body><header><nav>TargetAudit / Global Listings Watch / Alerts</nav>
<h1>What changed.<br>What needs review.</h1><p class="lead">Daily differences across listing and regulatory-document evidence feeds, preserved as an auditable research queue.</p>
<p class="meta">Observed {escape(as_of.isoformat())} / baseline {escape(baseline_label)}</p><section class="cards">{cards}</section>
<section class="coverage">{coverage}</section></header>
<main><p class="notice">Disappearance from a feed does not prove withdrawal, admission or trading. EDINET filings, CVM offerings and ESMA prospectuses open review; only corresponding exchange evidence confirms listing milestones. Synthetic demo evidence is not a public filing.</p>
<h2>Review queue</h2><div class="table-wrap"><table><thead><tr><th>Market</th><th>Change</th><th>Issuer</th><th>Previous</th><th>Current</th><th>Next step</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_alerts_html(
    path: str | Path,
    alerts: list[ListingAlert],
    current: list[ListingSignal],
    as_of: date,
    baseline_label: str,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_alerts_html(alerts, current, as_of, baseline_label), encoding="utf-8"
    )


def _load_market_csv(market: str, path: str | Path) -> list[ListingSignal]:
    try:
        with Path(path).open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
    except OSError as exc:
        raise ListingAlertsDataError(f"Unable to read {market} CSV {path}: {exc}") from exc
    signals = [_normalize_row(market, row) for row in rows]
    _signal_map(signals)
    return signals


def _normalize_row(market: str, row: dict[str, str]) -> ListingSignal:
    company = row.get("company_name", "").strip()
    if not company:
        raise ListingAlertsDataError(f"{market} CSV contains a blank company.")
    if market == "HKEX":
        status = row.get("status", "").strip()
        event_date = row.get("event_date", "").strip()
        stock_code = row.get("stock_code", "").strip()
        detail = f"{event_date} / code {stock_code or '-'} / PHIP {row.get('has_phip', '').strip()}"
        source = row.get("source_url", "").strip()
        # HKEX lifecycle feeds legitimately repeat an issuer across stages.
        key = "|".join((company.casefold(), status, event_date, stock_code))
    elif market == "LSE":
        status = "upcoming_issue"
        detail = f"{row.get('expected_first_trading', '').strip()} / {row.get('market', '').strip()}"
        source = row.get("source_url", "").strip()
        key = company.casefold()
    elif market == "ASX":
        status = row.get("status", "").strip()
        detail = f"{row.get('listing_date', '').strip()} / {row.get('security_code', '').strip()}"
        source = row.get("source_url", "").strip()
        key = company.casefold()
    elif market == "TSX":
        status = row.get("status", "").strip()
        detail = f"{row.get('listing_date', '').strip()} / {row.get('symbols', '').strip()}"
        source = row.get("detail_url", "").strip() or row.get("source_url", "").strip()
        key = company.casefold()
    elif market == "JPX":
        status = row.get("status", "").strip()
        security_code = row.get("security_code", "").strip()
        detail = (
            f"{row.get('listing_date', '').strip()} / approved "
            f"{row.get('approval_date', '').strip()} / {row.get('market_segment', '').strip()}"
        )
        source = row.get("outline_url", "").strip() or row.get("source_url", "").strip()
        key = security_code
    elif market == "EDINET":
        status = row.get("status", "").strip()
        document_id = row.get("document_id", "").strip()
        detail = (
            f"{row.get('submitted_at', '').strip()} / EDINET "
            f"{row.get('edinet_code', '').strip()} / security {row.get('security_code', '').strip()}"
        )
        # Document retrieval endpoints require the user's API key; link the official guide.
        source = row.get("source_url", "").strip()
        key = document_id
    elif market == "CVM":
        status = row.get("status", "").strip()
        offering_id = row.get("offering_id", "").strip()
        detail = (
            f"{row.get('filing_date', '').strip()} / {row.get('security_type', '').strip()} / "
            f"{row.get('offering_type', '').strip()}"
        )
        source = row.get("source_url", "").strip()
        key = offering_id
    elif market == "ESMA":
        status = row.get("status", "").strip()
        document_id = row.get("document_id", "").strip()
        isin = row.get("isin", "").strip()
        detail = (
            f"{row.get('filing_date', '').strip()} / {row.get('jurisdiction', '').strip()} / "
            f"{row.get('offer_admission_type', '').strip()}"
        )
        source = row.get("source_url", "").strip()
        key = f"{document_id}|{isin}"
    elif market == "SGX":
        status = row.get("status", "").strip()
        document_id = row.get("document_id", "").strip()
        detail = f"{row.get('closing_date', '').strip()} / modified {row.get('modified_date', '').strip()}"
        source = row.get("prospectus_url", "").strip()
        key = document_id
    else:
        raise ListingAlertsDataError(f"Unknown market for alerts: {market}")
    if not status or not key or not source:
        raise ListingAlertsDataError(f"{market} CSV contains incomplete evidence for {company}.")
    return ListingSignal(market, key, company, status, detail, source)


def _signal_map(signals: list[ListingSignal]) -> dict[tuple[str, str], ListingSignal]:
    result: dict[tuple[str, str], ListingSignal] = {}
    for signal in signals:
        key = (signal.market, signal.entity_key)
        if key in result:
            raise ListingAlertsDataError(
                f"{signal.market} CSV duplicates monitored entity {signal.company_name}."
            )
        result[key] = signal
    return result


def _alert(
    change_type: str, previous: ListingSignal | None, current: ListingSignal | None
) -> ListingAlert:
    item = current or previous
    assert item is not None
    actions = {
        "new": "Review new evidence and classify its milestone.",
        "changed": "Review changed evidence before updating status.",
        "removed_from_feed_review": "Confirm reason for removal in primary sources.",
    }
    return ListingAlert(
        market=item.market,
        change_type=change_type,
        company_name=item.company_name,
        previous_status=previous.status if previous else "",
        current_status=current.status if current else "",
        previous_detail=previous.event_detail if previous else "",
        current_detail=current.event_detail if current else "",
        review_action=actions[change_type],
        source_url=item.source_url,
    )


def _display_status(market: str, status: str) -> str:
    if not status:
        return "-"
    if market == "EDINET":
        return EDINET_STATUS_LABELS.get(status, status)
    if market == "CVM":
        return CVM_STATUS_LABELS.get(status, status)
    if market == "ESMA":
        return ESMA_STATUS_LABELS.get(status, status)
    return status
