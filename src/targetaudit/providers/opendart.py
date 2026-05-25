from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from datetime import date, datetime
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

OPENDART_DISCLOSURE_URL = "https://opendart.fss.or.kr/api/list.json"
OPENDART_GUIDE_URL = (
    "https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001"
)
OPENDART_TERMS_URL = "https://engopendart.fss.or.kr/uss/umt/EgovMberInsertView.do"
OPENDART_DOCUMENT_URL = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo={filing_id}"
EQUITY_DISCLOSURE_TYPES = {
    "C001": "equity_securities_registration_review",
    "C006": "small_equity_public_offering_review",
}
EQUITY_DISCLOSURE_LABELS = {
    "C001": "Equity securities registration review",
    "C006": "Small equity public offering review",
}
MARKET_HINTS = {
    "Y": "KOSPI",
    "K": "KOSDAQ",
    "N": "KONEX",
    "E": "Other / unlisted",
}


class OpenDartDataError(ValueError):
    """Raised when OpenDART equity-offering evidence cannot be used safely."""


@dataclass(frozen=True)
class OpenDartEquityFiling:
    company_name: str
    corp_code: str
    stock_code: str
    filing_id: str
    filing_type: str
    report_name: str
    market_hint: str
    status: str
    filing_date: date
    observed_on: date
    source_url: str
    document_url: str


def fetch_opendart_equity_filings(
    since: date,
    observed_on: date,
    api_key: str | None = None,
    page_size: int = 100,
) -> list[OpenDartEquityFiling]:
    if since > observed_on:
        raise OpenDartDataError("OpenDART filing window cannot start after report cutoff.")
    key = (api_key or os.environ.get("TARGETAUDIT_OPENDART_API_KEY", "")).strip()
    if not key:
        raise OpenDartDataError(
            "Live OpenDART collection requires --api-key or TARGETAUDIT_OPENDART_API_KEY."
        )
    filings: list[OpenDartEquityFiling] = []
    for filing_type in EQUITY_DISCLOSURE_TYPES:
        page_no = 1
        while True:
            params = {
                "crtfc_key": key,
                "bgn_de": since.strftime("%Y%m%d"),
                "end_de": observed_on.strftime("%Y%m%d"),
                "last_reprt_at": "Y",
                "pblntf_ty": "C",
                "pblntf_detail_ty": filing_type,
                "sort": "date",
                "sort_mth": "desc",
                "page_no": str(page_no),
                "page_count": str(page_size),
            }
            request = Request(
                f"{OPENDART_DISCLOSURE_URL}?{urlencode(params)}",
                headers={
                    "User-Agent": "TargetAudit/0.1 public-research-monitor",
                    "Accept": "application/json",
                },
            )
            try:
                with urlopen(request, timeout=60) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except (URLError, TimeoutError, OSError, ValueError) as exc:
                raise OpenDartDataError(
                    f"Unable to retrieve OpenDART equity filings: {exc}"
                ) from exc
            filings.extend(
                parse_opendart_payload(payload, filing_type, observed_on, since)
            )
            status = str(payload.get("status", "")).strip() if isinstance(payload, dict) else ""
            if status == "013":
                break
            try:
                total_pages = int(payload["total_page"])
            except (KeyError, TypeError, ValueError) as exc:
                raise OpenDartDataError(
                    "OpenDART response does not include valid paging metadata."
                ) from exc
            if page_no >= total_pages:
                break
            page_no += 1
    return _validate_unique(filings)


def load_opendart_snapshot(
    path: str | Path, observed_on: date, since: date
) -> list[OpenDartEquityFiling]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise OpenDartDataError(f"Unable to read OpenDART snapshot {path}: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("responses"), list):
        raise OpenDartDataError("OpenDART fixture does not include typed responses.")
    filings: list[OpenDartEquityFiling] = []
    for response in payload["responses"]:
        if not isinstance(response, dict):
            raise OpenDartDataError("OpenDART fixture includes an invalid response.")
        filing_type = str(response.get("filing_type", "")).strip()
        filings.extend(
            parse_opendart_payload(response.get("payload"), filing_type, observed_on, since)
        )
    return _validate_unique(filings)


def parse_opendart_payload(
    payload: object, filing_type: str, observed_on: date, since: date
) -> list[OpenDartEquityFiling]:
    if filing_type not in EQUITY_DISCLOSURE_TYPES:
        return []
    if not isinstance(payload, dict):
        raise OpenDartDataError("OpenDART response is not an object.")
    status = str(payload.get("status", "")).strip()
    if status == "013":
        return []
    if status != "000":
        message = str(payload.get("message", "unknown API response")).strip()
        raise OpenDartDataError(f"OpenDART API returned {status or 'unknown'}: {message}.")
    rows = payload.get("list")
    if not isinstance(rows, list):
        raise OpenDartDataError("OpenDART response does not contain a disclosure list.")
    filings: list[OpenDartEquityFiling] = []
    for row in rows:
        if not isinstance(row, dict):
            raise OpenDartDataError("OpenDART response contains an invalid disclosure.")
        filing_date = _parse_filing_date(str(row.get("rcept_dt", "")).strip())
        if filing_date < since:
            continue
        if filing_date > observed_on:
            raise OpenDartDataError("OpenDART snapshot includes a future filing.")
        company = str(row.get("corp_name", "")).strip()
        corp_code = str(row.get("corp_code", "")).strip()
        filing_id = str(row.get("rcept_no", "")).strip()
        report_name = str(row.get("report_nm", "")).strip()
        corp_class = str(row.get("corp_cls", "")).strip()
        if not company or not corp_code or not filing_id or not report_name:
            raise OpenDartDataError("OpenDART equity disclosure is missing required fields.")
        filings.append(
            OpenDartEquityFiling(
                company_name=company,
                corp_code=corp_code,
                stock_code=str(row.get("stock_code", "")).strip() or "-",
                filing_id=filing_id,
                filing_type=filing_type,
                report_name=report_name,
                market_hint=MARKET_HINTS.get(corp_class, "Unknown"),
                status=EQUITY_DISCLOSURE_TYPES[filing_type],
                filing_date=filing_date,
                observed_on=observed_on,
                source_url=OPENDART_GUIDE_URL,
                document_url=OPENDART_DOCUMENT_URL.format(filing_id=filing_id),
            )
        )
    return filings


def write_opendart_csv(path: str | Path, filings: list[OpenDartEquityFiling]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(OpenDartEquityFiling.__annotations__))
        writer.writeheader()
        for filing in filings:
            row = dict(filing.__dict__)
            row["filing_date"] = filing.filing_date.isoformat()
            row["observed_on"] = filing.observed_on.isoformat()
            writer.writerow(row)


def render_opendart_report(
    filings: list[OpenDartEquityFiling], as_of: date, since: date, source_mode: str
) -> str:
    _validate_as_of(filings, as_of)
    label = (
        "Official live OpenDART disclosure query"
        if source_mode == "live"
        else "Synthetic OpenDART-shaped fixture"
    )
    lines = [
        "# Korea OpenDART Equity Offering Watch",
        "",
        f"- Report generated as of: `{as_of.isoformat()}`",
        f"- Filing window starts: `{since.isoformat()}`",
        f"- Source mode: `{source_mode}` - {label}",
        f"- Official disclosure-search guide: <{OPENDART_GUIDE_URL}>",
        f"- Official terms and authentication-key page: <{OPENDART_TERMS_URL}>",
        f"- Equity-offering filing records observed: `{len(filings)}`",
        "",
        "This monitor queries only OpenDART issuance disclosure types `C001`",
        "(equity securities registration) and `C006` (small equity public offering).",
        "A disclosure opens regulatory review; it does not confirm an IPO, KRX",
        "listing, first trading or an investment action.",
        "",
        "## Equity Offering Filing Queue",
        "",
        "| Filed | Issuer | Market Hint | Filing Type | State | Filing |",
        "|---|---|---|---|---|---|",
    ]
    if not filings:
        lines.append("| - | No equity offering filings in selected window | - | - | - | - |")
    for item in sorted(filings, key=lambda filing: filing.filing_date, reverse=True):
        document = (
            f"[DART filing]({item.document_url})"
            if source_mode == "live"
            else "Synthetic identifier only"
        )
        lines.append(
            f"| {item.filing_date.isoformat()} | {item.company_name} | {item.market_hint} | "
            f"`{item.filing_type}` | `{item.status}` | {document} |"
        )
    return "\n".join(lines) + "\n"


def write_opendart_report(
    path: str | Path,
    filings: list[OpenDartEquityFiling],
    as_of: date,
    since: date,
    source_mode: str,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_opendart_report(filings, as_of, since, source_mode), encoding="utf-8"
    )


def render_opendart_html(
    filings: list[OpenDartEquityFiling], as_of: date, since: date, source_mode: str
) -> str:
    _validate_as_of(filings, as_of)
    label = (
        "Official live OpenDART disclosure query"
        if source_mode == "live"
        else "Synthetic reproducible fixture, not official filing evidence"
    )
    rows = "".join(
        "<tr>"
        f"<td>{escape(item.filing_date.isoformat())}</td>"
        f"<td><strong>{escape(item.company_name)}</strong><small>{escape(item.corp_code)}</small></td>"
        f"<td>{escape(item.market_hint)}<small>{escape(item.stock_code)}</small></td>"
        f"<td>{escape(item.report_name)}<small>{escape(item.filing_id)}</small></td>"
        f'<td><span class="badge">{escape(EQUITY_DISCLOSURE_LABELS[item.filing_type])}</span></td>'
        f'<td><a href="{escape(item.source_url)}">OpenDART guide</a></td>'
        "</tr>"
        for item in sorted(filings, key=lambda filing: filing.filing_date, reverse=True)
    )
    if not rows:
        rows = '<tr><td colspan="6">No equity offering filings observed in the selected window.</td></tr>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | Korea OpenDART Equity Offering Watch</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1140px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:820px}}
.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:285px;display:inline-block;margin:35px 0}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}.card small,td small{{display:block;color:var(--muted)}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}a{{color:var(--mint);text-decoration:none}}.badge{{color:var(--gold);background:rgba(240,188,98,.12);border-radius:999px;padding:5px 9px;font-size:12px;display:inline-block}}
@media(max-width:800px){{.table-wrap{{overflow:visible;background:transparent;border:0}}table,tbody,tr,td{{display:block;width:100%}}thead{{display:none}}tr{{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin:12px 0;padding:8px 14px}}td{{border:0;padding:7px 0;overflow-wrap:anywhere}}td::before{{display:block;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px}}td:nth-child(1)::before{{content:"Filed"}}td:nth-child(2)::before{{content:"Issuer"}}td:nth-child(3)::before{{content:"Market hint"}}td:nth-child(4)::before{{content:"Filing evidence"}}td:nth-child(5)::before{{content:"State"}}td:nth-child(6)::before{{content:"Source"}}}}
</style></head><body><header><nav>TargetAudit / Global Listings Watch / OpenDART</nav>
<h1>South Korea.<br>Equity offering filings.</h1><p class="lead">Equity issuance disclosures selected from the official FSS OpenDART disclosure-search API.</p>
<p class="meta">Observed as of {escape(as_of.isoformat())} / filings since {escape(since.isoformat())} / types C001 and C006</p><article class="card"><p>Offering filing records</p><strong>{len(filings)}</strong><small>{escape(label)}</small></article></header>
<main><p class="notice">An OpenDART equity filing starts regulatory review. It does not confirm an IPO, KRX listing or first trading. Live use requires the operator's free authentication key; KRX market data is not republished here while its third-party output restrictions apply.</p>
<h2>Equity offering filing queue</h2><div class="table-wrap"><table><thead><tr><th>Filed</th><th>Issuer</th><th>Market hint</th><th>Filing evidence</th><th>State</th><th>Source</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_opendart_html(
    path: str | Path,
    filings: list[OpenDartEquityFiling],
    as_of: date,
    since: date,
    source_mode: str,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_opendart_html(filings, as_of, since, source_mode), encoding="utf-8"
    )


def _parse_filing_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except ValueError as exc:
        raise OpenDartDataError(f"OpenDART disclosure contains invalid filing date: {value}.") from exc


def _validate_unique(filings: list[OpenDartEquityFiling]) -> list[OpenDartEquityFiling]:
    seen: set[str] = set()
    for item in filings:
        if item.filing_id in seen:
            raise OpenDartDataError(f"OpenDART response duplicates filing ID {item.filing_id}.")
        seen.add(item.filing_id)
    return filings


def _validate_as_of(filings: list[OpenDartEquityFiling], as_of: date) -> None:
    if any(item.observed_on > as_of for item in filings):
        raise OpenDartDataError("OpenDART snapshot includes a future observation.")
