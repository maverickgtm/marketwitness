from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path

LSE_SOURCE_URL = "https://www.londonstockexchange.com/live-markets/new-issues"
LSE_COLUMNS = {
    "company_name",
    "market",
    "primary_offer",
    "secondary_offer",
    "currency",
    "price_range",
    "expected_first_trading",
    "instrument_type",
    "observed_on",
    "source_url",
}


class LseDataError(ValueError):
    """Raised when an LSE upcoming-issues snapshot is invalid."""


@dataclass(frozen=True)
class LseUpcomingIssue:
    company_name: str
    market: str
    primary_offer: str
    secondary_offer: str
    currency: str
    price_range: str
    expected_first_trading: str
    instrument_type: str
    observed_on: date
    source_url: str


def load_lse_upcoming(path: str | Path) -> list[LseUpcomingIssue]:
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        missing = sorted(LSE_COLUMNS - set(reader.fieldnames or []))
        if missing:
            raise LseDataError(f"{path}: missing columns: {', '.join(missing)}")
        issues: list[LseUpcomingIssue] = []
        seen: set[str] = set()
        for index, row in enumerate(reader, start=2):
            company = row["company_name"].strip()
            if not company or company.casefold() in seen:
                raise LseDataError(f"{path}: blank or duplicate company on row {index}")
            try:
                observed_on = date.fromisoformat(row["observed_on"].strip())
            except ValueError as exc:
                raise LseDataError(f"{path}: invalid observed date on row {index}") from exc
            if not row["expected_first_trading"].strip() or not row["source_url"].strip():
                raise LseDataError(f"{path}: missing expected trading date or source")
            seen.add(company.casefold())
            issues.append(
                LseUpcomingIssue(
                    company_name=company,
                    market=row["market"].strip(),
                    primary_offer=row["primary_offer"].strip(),
                    secondary_offer=row["secondary_offer"].strip(),
                    currency=row["currency"].strip(),
                    price_range=row["price_range"].strip(),
                    expected_first_trading=row["expected_first_trading"].strip(),
                    instrument_type=row["instrument_type"].strip(),
                    observed_on=observed_on,
                    source_url=row["source_url"].strip(),
                )
            )
        return issues


def render_lse_report(issues: list[LseUpcomingIssue], as_of: date) -> str:
    _validate_as_of(issues, as_of)
    lines = [
        "# LSE Upcoming Issues Snapshot",
        "",
        f"- Snapshot verified as of: `{as_of.isoformat()}`",
        f"- Upcoming records captured: `{len(issues)}`",
        f"- Official page: <{LSE_SOURCE_URL}>",
        "",
        "This is a traceable capture of the London Stock Exchange `Upcoming issues`",
        "table, not yet an automated live connector. Expected trading dates and offer",
        "sizes may change; admission evidence must be reviewed before confirmation.",
        "",
        "## Upcoming Issues",
        "",
        "| Company | Market | Expected First Trading | Primary Offer | Type | Source |",
        "|---|---|---|---|---|---|",
    ]
    for issue in issues:
        lines.append(
            f"| {issue.company_name} | {issue.market} | "
            f"{issue.expected_first_trading} | {issue.primary_offer} | "
            f"{issue.instrument_type} | [LSE]({issue.source_url}) |"
        )
    return "\n".join(lines) + "\n"


def write_lse_report(path: str | Path, issues: list[LseUpcomingIssue], as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_lse_report(issues, as_of), encoding="utf-8")


def render_lse_html(issues: list[LseUpcomingIssue], as_of: date) -> str:
    _validate_as_of(issues, as_of)
    rows = "".join(
        "<tr>"
        f"<td><strong>{escape(issue.company_name)}</strong></td>"
        f"<td>{escape(issue.market)}</td>"
        f"<td>{escape(issue.expected_first_trading)}</td>"
        f"<td>{escape(issue.primary_offer)}</td>"
        f"<td>{escape(issue.instrument_type)}</td>"
        f'<td><a href="{escape(issue.source_url)}">LSE</a></td>'
        "</tr>"
        for issue in issues
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | LSE Upcoming Issues</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1120px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:760px}}
.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{margin:35px 0;padding:18px 20px;width:260px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}a{{color:var(--mint);text-decoration:none}}
@media(max-width:800px){{.table-wrap{{overflow-x:auto}}table{{min-width:700px}}}}
</style></head><body><header><nav>TargetAudit / Global Listings Watch / LSE</nav><h1>London.<br>Upcoming issues.</h1>
<p class="lead">A documented snapshot of upcoming equity listings visible on the official London Stock Exchange page.</p>
<p class="meta">Observed as of {escape(as_of.isoformat())}</p><article class="card"><p>Upcoming records</p><strong>{len(issues)}</strong><small>Official-page snapshot</small></article></header>
<main><p class="notice">Snapshot mode. Dates are expected dates from LSE and still require prospectus or admission verification.</p>
<h2>Observed upcoming issues</h2><div class="table-wrap"><table><thead><tr><th>Company</th><th>Market</th><th>Expected trading</th><th>Primary offer</th><th>Type</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_lse_html(path: str | Path, issues: list[LseUpcomingIssue], as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_lse_html(issues, as_of), encoding="utf-8")


def _validate_as_of(issues: list[LseUpcomingIssue], as_of: date) -> None:
    future = [issue.company_name for issue in issues if issue.observed_on > as_of]
    if future:
        raise LseDataError(f"LSE snapshot includes a future observation: {future[0]}")
