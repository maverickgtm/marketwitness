from __future__ import annotations

import csv
import shutil
from collections import Counter
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

from .ipo_watch import IpoWatchItem
from .providers.sec_ipo import SecIpoFiling


class SecAlertsDataError(ValueError):
    """Raised when SEC filing history cannot be compared safely."""


@dataclass(frozen=True)
class SecFilingAlert:
    company_name: str
    cik: str
    form: str
    filed_date: date
    review_state: str
    alert_type: str
    watch_company: str
    watch_status: str
    source_url: str
    review_action: str


def load_discovered_filings(path: str | Path) -> list[SecIpoFiling]:
    try:
        with Path(path).open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
    except OSError as exc:
        raise SecAlertsDataError(f"Unable to read SEC discovery CSV {path}: {exc}") from exc
    required = {
        "cik",
        "company_name",
        "form",
        "filed_date",
        "archive_path",
        "source_url",
        "review_state",
    }
    if rows and not required.issubset(rows[0]):
        raise SecAlertsDataError(f"{path}: missing normalized SEC discovery fields.")
    filings: list[SecIpoFiling] = []
    seen: set[str] = set()
    for row in rows:
        source_url = row["source_url"].strip()
        try:
            filed_date = date.fromisoformat(row["filed_date"].strip())
        except ValueError as exc:
            raise SecAlertsDataError("SEC discovery CSV contains an invalid date.") from exc
        if not source_url or source_url in seen:
            raise SecAlertsDataError("SEC discovery CSV contains blank or duplicate filing evidence.")
        seen.add(source_url)
        filings.append(
            SecIpoFiling(
                cik=row["cik"].strip().zfill(10),
                company_name=row["company_name"].strip(),
                form=row["form"].strip(),
                filed_date=filed_date,
                archive_path=row["archive_path"].strip(),
                source_url=source_url,
                review_state=row["review_state"].strip(),
            )
        )
    return filings


def known_source_urls(history_dir: str | Path, as_of: date) -> set[str]:
    history = Path(history_dir)
    known: set[str] = set()
    if not history.exists():
        return known
    for child in history.iterdir():
        if not child.is_dir():
            continue
        try:
            observed_on = date.fromisoformat(child.name)
        except ValueError:
            continue
        if observed_on <= as_of:
            snapshot = child / "sec-ipo-discovery.csv"
            if snapshot.exists():
                known.update(filing.source_url for filing in load_discovered_filings(snapshot))
    return known


def archive_discovery(
    history_dir: str | Path, source: str | Path, as_of: date
) -> Path:
    destination = Path(history_dir) / as_of.isoformat()
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / "sec-ipo-discovery.csv"
    try:
        shutil.copyfile(source, target)
    except OSError as exc:
        raise SecAlertsDataError(f"Unable to archive SEC discovery CSV: {exc}") from exc
    return target


def build_filing_alerts(
    filings: list[SecIpoFiling],
    watchlist: list[IpoWatchItem],
    already_seen: set[str],
) -> list[SecFilingAlert]:
    watched_by_cik = {item.cik: item for item in watchlist if item.cik}
    alerts: list[SecFilingAlert] = []
    for filing in filings:
        if filing.source_url in already_seen:
            continue
        watched = watched_by_cik.get(filing.cik)
        if watched:
            alert_type = "watchlist_filing_review"
            action = "Review new SEC evidence before changing the monitored status."
        else:
            alert_type = "new_filing_review"
            action = "Read filing to determine whether it is an IPO-related event."
        alerts.append(
            SecFilingAlert(
                company_name=filing.company_name,
                cik=filing.cik,
                form=filing.form,
                filed_date=filing.filed_date,
                review_state=filing.review_state,
                alert_type=alert_type,
                watch_company=watched.company_name if watched else "",
                watch_status=watched.status if watched else "",
                source_url=filing.source_url,
                review_action=action,
            )
        )
    return sorted(alerts, key=lambda item: (item.alert_type, item.company_name.casefold()))


def write_sec_alerts_csv(path: str | Path, alerts: list[SecFilingAlert]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(SecFilingAlert.__annotations__))
        writer.writeheader()
        for item in alerts:
            row = dict(item.__dict__)
            row["filed_date"] = item.filed_date.isoformat()
            writer.writerow(row)


def render_sec_alerts_report(
    alerts: list[SecFilingAlert],
    filings: list[SecIpoFiling],
    as_of: date,
    known_count: int,
) -> str:
    counts = Counter(item.alert_type for item in alerts)
    lines = [
        "# SEC IPO Alerts",
        "",
        f"- Observation date: `{as_of.isoformat()}`",
        f"- Candidate filings in current index: `{len(filings)}`",
        f"- Previously archived filing documents: `{known_count}`",
        f"- New filings requiring review: `{counts['new_filing_review']}`",
        f"- New filings matching IPO Watch by CIK: `{counts['watchlist_filing_review']}`",
        "",
        "This queue detects new SEC filing evidence. Matching a watched company by",
        "CIK improves routing, but does not automatically confirm an IPO, pricing,",
        "withdrawal, listing or investment action.",
        "",
        "## Filing Review Queue",
        "",
        "| Alert | Company | Form | Filed | IPO Watch Link | Review State | Source |",
        "|---|---|---|---|---|---|---|",
    ]
    if not alerts:
        lines.append("| - | No newly discovered filing evidence | - | - | - | - | - |")
    for item in alerts:
        watched = (
            f"{item.watch_company} (`{item.watch_status}`)"
            if item.watch_company
            else "-"
        )
        lines.append(
            f"| `{item.alert_type}` | {item.company_name} | `{item.form}` | "
            f"{item.filed_date.isoformat()} | {watched} | `{item.review_state}` | "
            f"[SEC filing]({item.source_url}) |"
        )
    return "\n".join(lines) + "\n"


def write_sec_alerts_report(
    path: str | Path,
    alerts: list[SecFilingAlert],
    filings: list[SecIpoFiling],
    as_of: date,
    known_count: int,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_sec_alerts_report(alerts, filings, as_of, known_count), encoding="utf-8"
    )


def render_sec_alerts_html(
    alerts: list[SecFilingAlert],
    filings: list[SecIpoFiling],
    as_of: date,
    known_count: int,
) -> str:
    counts = Counter(item.alert_type for item in alerts)
    rows = "".join(
        "<tr>"
        f'<td><span class="badge {escape(item.alert_type)}">{escape(item.alert_type)}</span></td>'
        f"<td><strong>{escape(item.company_name)}</strong><small>CIK {escape(item.cik)}</small></td>"
        f"<td>{escape(item.form)}</td><td>{escape(item.filed_date.isoformat())}</td>"
        f"<td>{escape(item.watch_company or '-')}<small>{escape(item.watch_status)}</small></td>"
        f"<td>{escape(item.review_action)}</td>"
        f'<td><a href="{escape(item.source_url)}">SEC</a></td>'
        "</tr>"
        for item in alerts
    )
    if not rows:
        rows = '<tr><td colspan="7">No newly discovered SEC filing evidence in this comparison.</td></tr>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | SEC IPO Alerts</title><style>
:root{{--bg:#081117;--panel:#101d26;--line:#21333d;--text:#ecf0ee;--muted:#9cadb2;--mint:#57dbad;--amber:#f2bf62;--blue:#62a6ff;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1180px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);font-size:13px;letter-spacing:.08em;text-transform:uppercase}}h1{{font-size:clamp(36px,5vw,56px);line-height:1.05;margin:40px 0 14px}}.lead{{color:var(--muted);max-width:790px;font-size:17px}}
.cards{{display:flex;gap:16px;margin:34px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:230px}}.card p{{margin:0;color:var(--muted)}}.card strong{{display:block;font-size:38px;color:var(--mint)}}.notice{{border-left:3px solid var(--amber);padding:15px 18px;color:var(--muted)}}h2{{margin-top:44px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{font-size:12px;text-transform:uppercase;color:var(--muted);font-weight:500}}td small{{display:block;color:var(--muted)}}a{{color:var(--mint);text-decoration:none}}.badge{{border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}.watchlist_filing_review{{color:var(--amber);background:rgba(242,191,98,.12)}}.new_filing_review{{color:var(--blue);background:rgba(98,166,255,.12)}}
@media(max-width:800px){{.cards{{display:block}}.card{{margin-bottom:12px}}.table-wrap{{overflow-x:auto}}table{{min-width:960px}}}}
</style></head><body><header><nav>TargetAudit / IPO Watch / SEC Alerts</nav>
<h1>Public filings.<br>Review before promotion.</h1><p class="lead">New SEC filing evidence routed into a review queue, with CIK matches to companies already followed in IPO Watch.</p>
<p class="meta">Observed {escape(as_of.isoformat())}</p><section class="cards"><article class="card"><p>Current filings</p><strong>{len(filings)}</strong></article><article class="card"><p>New reviews</p><strong>{counts['new_filing_review']}</strong></article><article class="card"><p>Watchlist matches</p><strong>{counts['watchlist_filing_review']}</strong></article></section></header>
<main><p class="notice">CIK matching identifies evidence for review; it never automatically changes IPO Watch status or recommends a position.</p>
<h2>Filing review queue</h2><div class="table-wrap"><table><thead><tr><th>Alert</th><th>Issuer</th><th>Form</th><th>Filed</th><th>Monitored item</th><th>Review step</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_sec_alerts_html(
    path: str | Path,
    alerts: list[SecFilingAlert],
    filings: list[SecIpoFiling],
    as_of: date,
    known_count: int,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_sec_alerts_html(alerts, filings, as_of, known_count), encoding="utf-8"
    )
