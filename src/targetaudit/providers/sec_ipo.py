from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from .sec import SecDataError, configured_user_agent

DISCOVERY_FORMS = {
    "S-1": "initial_registration_review",
    "S-1/A": "registration_amendment_review",
    "S-1MEF": "additional_securities_review",
    "F-1": "initial_registration_review",
    "F-1/A": "registration_amendment_review",
    "F-1MEF": "additional_securities_review",
    "424B4": "final_prospectus_review",
    "RW": "withdrawal_review",
}


@dataclass(frozen=True)
class SecIpoFiling:
    cik: str
    company_name: str
    form: str
    filed_date: date
    archive_path: str
    source_url: str
    review_state: str


def daily_master_index_url(filing_date: date) -> str:
    quarter = ((filing_date.month - 1) // 3) + 1
    stamp = filing_date.strftime("%Y%m%d")
    return (
        "https://www.sec.gov/Archives/edgar/daily-index/"
        f"{filing_date.year}/QTR{quarter}/master.{stamp}.idx"
    )


def fetch_daily_master_index(
    filing_date: date, user_agent: str | None = None
) -> tuple[str, str]:
    source_url = daily_master_index_url(filing_date)
    request = Request(
        source_url,
        headers={
            "User-Agent": configured_user_agent(user_agent),
            "Accept": "text/plain",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return response.read().decode("latin-1"), source_url
    except (URLError, TimeoutError, OSError) as exc:
        raise SecDataError(f"Unable to retrieve SEC daily index: {exc}") from exc


def load_master_index(path: str | Path) -> tuple[str, str]:
    source = Path(path).resolve()
    return source.read_text(encoding="latin-1"), source.as_uri()


def parse_ipo_candidate_filings(index_text: str) -> list[SecIpoFiling]:
    filings: list[SecIpoFiling] = []
    for raw in index_text.splitlines():
        if raw.count("|") != 4:
            continue
        cik, company_name, form, filed_raw, archive_path = [
            value.strip() for value in raw.split("|", maxsplit=4)
        ]
        if form not in DISCOVERY_FORMS:
            continue
        try:
            filed_date = _parse_filed_date(filed_raw)
        except ValueError as exc:
            raise SecDataError("SEC daily index contains an invalid filing date.") from exc
        filings.append(
            SecIpoFiling(
                cik=cik.zfill(10),
                company_name=company_name,
                form=form,
                filed_date=filed_date,
                archive_path=archive_path,
                source_url=f"https://www.sec.gov/Archives/{archive_path}",
                review_state=DISCOVERY_FORMS[form],
            )
        )
    return sorted(filings, key=lambda filing: (filing.filed_date, filing.company_name))


def _parse_filed_date(raw: str) -> date:
    if "-" in raw:
        return date.fromisoformat(raw)
    return datetime.strptime(raw, "%Y%m%d").date()


def write_discovered_filings(path: str | Path, filings: list[SecIpoFiling]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=[
                "cik",
                "company_name",
                "form",
                "filed_date",
                "archive_path",
                "source_url",
                "review_state",
            ],
        )
        writer.writeheader()
        for filing in filings:
            writer.writerow(
                {
                    "cik": filing.cik,
                    "company_name": filing.company_name,
                    "form": filing.form,
                    "filed_date": filing.filed_date.isoformat(),
                    "archive_path": filing.archive_path,
                    "source_url": filing.source_url,
                    "review_state": filing.review_state,
                }
            )


def render_discovery_report(
    filings: list[SecIpoFiling], filing_date: date, source_url: str
) -> str:
    lines = [
        "# SEC IPO Discovery Queue",
        "",
        f"- Filing date scanned: `{filing_date.isoformat()}`",
        f"- Potential registration/prospectus events: `{len(filings)}`",
        f"- Index source: <{source_url}>",
        "",
        "This is a discovery queue, not a confirmed IPO calendar. Forms such as",
        "`S-1` and `F-1` can relate to transactions other than an initial public",
        "offering and must be reviewed before promotion to IPO Watch.",
        "",
        "## Filings Requiring Review",
        "",
        "| Company | Form | Filed | Review State | Source |",
        "|---|---|---|---|---|",
    ]
    for filing in filings:
        lines.append(
            f"| {filing.company_name} | `{filing.form}` | "
            f"{filing.filed_date.isoformat()} | `{filing.review_state}` | "
            f"[Open SEC filing]({filing.source_url}) |"
        )
    if not filings:
        lines.append("| - | - | - | No monitored forms in this index | - |")
    lines.extend(
        [
            "",
            "## Promotion Rule",
            "",
            "A discovered filing must be read and verified as an IPO registration,",
            "pricing prospectus, listing confirmation or withdrawal before it changes",
            "the public IPO Watch status board.",
            "",
        ]
    )
    return "\n".join(lines)


def write_discovery_report(
    path: str | Path, filings: list[SecIpoFiling], filing_date: date, source_url: str
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_discovery_report(filings, filing_date, source_url), encoding="utf-8"
    )


def render_discovery_html(
    filings: list[SecIpoFiling], filing_date: date, source_url: str
) -> str:
    counts = Counter(filing.review_state for filing in filings)
    source_detail = (
        f'<a href="{escape(source_url)}">SEC daily master index</a>'
        if source_url.startswith("https://")
        else "Bundled SEC-shaped index fixture"
    )
    rows = "".join(
        "<tr>"
        f"<td><strong>{escape(filing.company_name)}</strong><small>CIK {escape(filing.cik)}</small></td>"
        f"<td>{escape(filing.form)}</td>"
        f'<td><span class="pill {escape(filing.review_state)}">{escape(filing.review_state)}</span></td>'
        f'<td><a href="{escape(filing.source_url)}">SEC filing</a></td>'
        "</tr>"
        for filing in filings
    )
    if not rows:
        rows = '<tr><td colspan="4">No potential IPO-related forms found in this daily index.</td></tr>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | SEC IPO Discovery Queue</title><style>
:root{{--bg:#081117;--panel:#101d26;--line:#21333d;--text:#ecf0ee;--muted:#9cadb2;--mint:#57dbad;--amber:#f2bf62;--blue:#62a6ff;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1160px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);font-size:13px;letter-spacing:.08em;text-transform:uppercase}}a{{color:var(--mint);text-decoration:none}}h1{{font-size:clamp(36px,5vw,56px);line-height:1.05;margin:40px 0 14px}}h2{{margin-top:44px}}.lead{{color:var(--muted);max-width:820px;font-size:17px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:34px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{display:block;font-size:36px;color:var(--mint)}}.notice{{border-left:3px solid var(--amber);padding:15px 18px;color:var(--muted)}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{font-size:12px;text-transform:uppercase;color:var(--muted);font-weight:500}}td small{{display:block;color:var(--muted);margin-top:6px}}.pill{{border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}.initial_registration_review,.registration_amendment_review{{color:var(--blue);background:rgba(98,166,255,.12)}}.final_prospectus_review{{color:var(--mint);background:rgba(87,219,173,.12)}}.withdrawal_review{{color:var(--amber);background:rgba(242,191,98,.12)}}@media(max-width:860px){{.cards{{grid-template-columns:repeat(2,1fr)}}.table-wrap{{overflow-x:auto}}table{{min-width:760px}}}}
</style></head><body><header><nav><a href="/dashboard/reports">Report Center</a> / IPO Watch / SEC Discovery</nav>
<h1>Daily index.<br>Universal intake.</h1>
<p class="lead">Potential registration, prospectus and withdrawal forms found in a SEC daily master index before triage or manual promotion.</p>
<p class="meta">Filing date scanned {escape(filing_date.isoformat())}</p>
<section class="cards"><article class="card"><p>Candidate filings</p><strong>{len(filings)}</strong></article><article class="card"><p>Initial registrations</p><strong>{counts['initial_registration_review']}</strong></article><article class="card"><p>Final prospectuses</p><strong>{counts['final_prospectus_review']}</strong></article><article class="card"><p>Withdrawals</p><strong>{counts['withdrawal_review']}</strong></article></section></header>
<main><p class="notice">This is a discovery queue, not a confirmed IPO calendar. A filing must be reviewed before it changes IPO Watch status or informs any investment study.</p>
<h2>Filings Requiring Review</h2><div class="table-wrap"><table><thead><tr><th>Company</th><th>Form</th><th>Review state</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="meta">Index source: {source_detail}</p></main></body></html>"""


def write_discovery_html(
    path: str | Path, filings: list[SecIpoFiling], filing_date: date, source_url: str
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_discovery_html(filings, filing_date, source_url), encoding="utf-8"
    )
