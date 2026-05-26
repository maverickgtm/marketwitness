from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

LSE_SOURCE_URL = "https://www.londonstockexchange.com/live-markets/new-issues"
LSE_API_URL = (
    "https://api.londonstockexchange.com/api/v1/pages"
    "?path=live-markets%2Fnew-issues"
)
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


def fetch_lse_upcoming() -> list[LseUpcomingIssue]:
    request = Request(
        LSE_API_URL,
        headers={
            "User-Agent": "MarketWitness/0.1 public-research-monitor",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise LseDataError(f"Unable to retrieve LSE upcoming issues: {exc}") from exc
    return parse_lse_page_payload(payload, date.today())


def load_lse_page_payload(path: str | Path, observed_on: date) -> list[LseUpcomingIssue]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LseDataError(f"Unable to read LSE page payload {path}: {exc}") from exc
    return parse_lse_page_payload(payload, observed_on)


def parse_lse_page_payload(payload: object, observed_on: date) -> list[LseUpcomingIssue]:
    if not isinstance(payload, dict):
        raise LseDataError("Unexpected LSE page payload.")
    components = payload.get("components")
    if not isinstance(components, list):
        raise LseDataError("LSE page payload is missing components.")
    upcoming = next(
        (
            component
            for component in components
            if isinstance(component, dict) and component.get("type") == "upcoming-issues"
        ),
        None,
    )
    if upcoming is None:
        raise LseDataError("LSE page payload is missing upcoming-issues component.")
    items = _upcoming_items(upcoming)
    issues: list[LseUpcomingIssue] = []
    for item in items:
        if not isinstance(item, dict):
            raise LseDataError("LSE upcoming-issues component contains an invalid row.")
        company = str(item.get("name", "")).strip()
        expected = str(item.get("firsttradingdate", "")).strip()
        link = str(item.get("link", "")).strip()
        if not company or not expected or not link:
            raise LseDataError("LSE upcoming issue is missing name, date or link.")
        issues.append(
            LseUpcomingIssue(
                company_name=company,
                market=str(item.get("market", "")).strip(),
                primary_offer=_display_value(item.get("primaryoffersize")),
                secondary_offer=_display_value(item.get("secondaryoffersize")),
                currency=_display_value(item.get("currency")),
                price_range=_price_range(item.get("minprice"), item.get("maxprice")),
                expected_first_trading=expected,
                instrument_type=str(item.get("type", "")).strip(),
                observed_on=observed_on,
                source_url=link,
            )
        )
    return issues


def _upcoming_items(component: dict[str, object]) -> list[object]:
    for record in component.get("content", []) if isinstance(component.get("content"), list) else []:
        if isinstance(record, dict) and record.get("name") == "upcomingissues":
            value = record.get("value")
            if isinstance(value, dict) and isinstance(value.get("Items"), list):
                return value["Items"]
    raise LseDataError("LSE upcoming-issues component is missing Items.")


def _display_value(value: object) -> str:
    if value is None or str(value).strip() in {"", "-"}:
        return "-"
    return str(value).strip().replace("\u00a3", "GBP ")


def _price_range(minimum: object, maximum: object) -> str:
    if minimum in (None, 0) and maximum in (None, 0):
        return "-"
    return f"{_display_value(minimum)} - {_display_value(maximum)}"


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


def write_lse_csv(path: str | Path, issues: list[LseUpcomingIssue]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(LseUpcomingIssue.__annotations__))
        writer.writeheader()
        for issue in issues:
            row = dict(issue.__dict__)
            row["observed_on"] = issue.observed_on.isoformat()
            writer.writerow(row)


def render_lse_report(
    issues: list[LseUpcomingIssue], as_of: date, source_mode: str = "snapshot"
) -> str:
    _validate_as_of(issues, as_of)
    live = source_mode == "live"
    lines = [
        "# LSE Upcoming Issues Monitor" if live else "# LSE Upcoming Issues Snapshot",
        "",
        (
            f"- Live feed read as of: `{as_of.isoformat()}`"
            if live
            else f"- Snapshot verified as of: `{as_of.isoformat()}`"
        ),
        f"- Upcoming records observed: `{len(issues)}`",
        f"- Official page: <{LSE_SOURCE_URL}>",
    ]
    if live:
        lines.append(f"- Official JSON source: <{LSE_API_URL}>")
    lines.extend(
        [
            "",
            (
            "This monitor reads the London Stock Exchange `Upcoming issues` component"
            if live
            else "This is a traceable capture of the London Stock Exchange `Upcoming issues` table"
            ),
            "from official evidence. Expected trading dates and offer",
            "sizes may change; admission evidence must be reviewed before confirmation.",
            "",
            "## Upcoming Issues",
            "",
            "| Company | Market | Expected First Trading | Primary Offer | Type | Source |",
            "|---|---|---|---|---|---|",
        ]
    )
    for issue in issues:
        lines.append(
            f"| {issue.company_name} | {issue.market} | "
            f"{issue.expected_first_trading} | {issue.primary_offer} | "
            f"{issue.instrument_type} | [LSE]({issue.source_url}) |"
        )
    return "\n".join(lines) + "\n"


def write_lse_report(
    path: str | Path,
    issues: list[LseUpcomingIssue],
    as_of: date,
    source_mode: str = "snapshot",
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_lse_report(issues, as_of, source_mode), encoding="utf-8"
    )


def render_lse_html(
    issues: list[LseUpcomingIssue], as_of: date, source_mode: str = "snapshot"
) -> str:
    _validate_as_of(issues, as_of)
    live = source_mode == "live"
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
<title>MarketWitness | LSE Upcoming Issues</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1120px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:760px}}
.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{margin:35px 0;padding:18px 20px;width:260px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}a{{color:var(--mint);text-decoration:none}}
@media(max-width:800px){{.table-wrap{{overflow-x:auto}}table{{min-width:700px}}}}
</style></head><body><header><nav><a href="/dashboard/global-listings">Global Listings Watch</a> / LSE</nav><h1>London.<br>Upcoming issues.</h1>
<p class="lead">{"A live reading of upcoming equity listings from the official London Stock Exchange page data." if live else "A documented snapshot of upcoming equity listings visible on the official London Stock Exchange page."}</p>
<p class="meta">Observed as of {escape(as_of.isoformat())}</p><article class="card"><p>Upcoming records</p><strong>{len(issues)}</strong><small>{"Official JSON feed" if live else "Official-page snapshot"}</small></article></header>
<main><p class="notice">{"Live official feed." if live else "Snapshot mode."} Dates are expected dates from LSE and still require prospectus or admission verification.</p>
<h2>Observed upcoming issues</h2><div class="table-wrap"><table><thead><tr><th>Company</th><th>Market</th><th>Expected trading</th><th>Primary offer</th><th>Type</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_lse_html(
    path: str | Path,
    issues: list[LseUpcomingIssue],
    as_of: date,
    source_mode: str = "snapshot",
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_lse_html(issues, as_of, source_mode), encoding="utf-8")


def _validate_as_of(issues: list[LseUpcomingIssue], as_of: date) -> None:
    future = [issue.company_name for issue in issues if issue.observed_on > as_of]
    if future:
        raise LseDataError(f"LSE snapshot includes a future observation: {future[0]}")
