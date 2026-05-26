from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ESMA_HELP_URL = "https://registers.esma.europa.eu/publication/helpApp"
ESMA_LEGAL_URL = "https://registers.esma.europa.eu/publication/legalNoticePage"
ESMA_SECURITIES_URL = (
    "https://registers.esma.europa.eu/solr/esma_registers_priii_securities/select"
)
SUPPORTED_STATES = {"DE": "Germany", "NL": "Netherlands", "IT": "Italy"}
OFFERING_STATUS = {
    "IRMT": "initial_admission_regulated_market_review",
    "IMTF": "initial_admission_mtf_review",
    "IOWA": "initial_offer_without_admission_review",
    "SIRM": "secondary_issuance_review",
    "SOWA": "secondary_offer_without_admission_review",
}


class EsmaDataError(ValueError):
    """Raised when ESMA equity-prospectus evidence cannot be used safely."""


@dataclass(frozen=True)
class EsmaEquityProspectus:
    company_name: str
    isin: str
    document_id: str
    jurisdiction: str
    security_type: str
    offer_admission_type: str
    status: str
    filing_date: date
    updated_at: str
    observed_on: date
    source_url: str


def fetch_esma_equity_prospectuses(
    since: date, observed_on: date, page_size: int = 100
) -> list[EsmaEquityProspectus]:
    if since > observed_on:
        raise EsmaDataError("ESMA filing window cannot start after report cutoff.")
    query = (
        f"sec_approvalFilingDate:[{since.isoformat()}T00:00:00Z TO "
        f"{observed_on.isoformat()}T23:59:59Z]"
    )
    documents: list[object] = []
    start = 0
    while True:
        params = {
            "q": query,
            "fq": ["sec_homeMemberStateCode:(DE OR NL OR IT)", "sec_securitiesType:SHRS"],
            "sort": "sec_approvalFilingDate desc",
            "rows": str(page_size),
            "start": str(start),
            "wt": "json",
        }
        url = f"{ESMA_SECURITIES_URL}?{urlencode(params, doseq=True)}"
        request = Request(
            url,
            headers={
                "User-Agent": "MarketWitness/0.1 public-research-monitor",
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            raise EsmaDataError(f"Unable to retrieve ESMA prospectuses: {exc}") from exc
        try:
            response_payload = payload["response"]
            page = response_payload["docs"]
            total = int(response_payload["numFound"])
        except (KeyError, TypeError, ValueError) as exc:
            raise EsmaDataError("ESMA payload does not include paging metadata.") from exc
        if not isinstance(page, list):
            raise EsmaDataError("ESMA payload documents are not a list.")
        documents.extend(page)
        start += len(page)
        if not page or start >= total:
            break
    return parse_esma_payload({"response": {"docs": documents}}, observed_on, since)


def load_esma_snapshot(
    path: str | Path, observed_on: date, since: date
) -> list[EsmaEquityProspectus]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise EsmaDataError(f"Unable to read ESMA snapshot {path}: {exc}") from exc
    return parse_esma_payload(payload, observed_on, since)


def parse_esma_payload(
    payload: dict[str, object], observed_on: date, since: date
) -> list[EsmaEquityProspectus]:
    try:
        rows = payload["response"]["docs"]  # type: ignore[index]
    except (KeyError, TypeError) as exc:
        raise EsmaDataError("ESMA payload does not include response documents.") from exc
    if not isinstance(rows, list):
        raise EsmaDataError("ESMA payload documents are not a list.")
    prospectuses: list[EsmaEquityProspectus] = []
    for row in rows:
        if not isinstance(row, dict):
            raise EsmaDataError("ESMA response contains an invalid document row.")
        if row.get("sec_securitiesType") != "SHRS":
            continue
        jurisdiction_code = str(row.get("sec_homeMemberStateCode", "")).strip()
        if jurisdiction_code not in SUPPORTED_STATES:
            continue
        filing_date = _date_field(row, "sec_approvalFilingDate")
        if filing_date < since:
            continue
        if filing_date > observed_on:
            raise EsmaDataError("ESMA snapshot includes a prospectus filed after observation date.")
        company = str(row.get("sec_issuerNameList", "")).strip()
        isin = str(row.get("sec_isin", "")).strip()
        document_id = str(row.get("sec_natDocId", "")).strip()
        offer_type = str(row.get("sec_offerAdmType", "")).strip()
        security_type = str(row.get("sec_securitiesTypeDesc", "")).strip()
        if not company or not isin or not document_id or not offer_type or not security_type:
            raise EsmaDataError("ESMA shares record is missing required evidence fields.")
        prospectuses.append(
            EsmaEquityProspectus(
                company_name=company,
                isin=isin,
                document_id=document_id,
                jurisdiction=SUPPORTED_STATES[jurisdiction_code],
                security_type=security_type,
                offer_admission_type=str(row.get("sec_offerAdmTypeDesc", "")).strip()
                or offer_type,
                status=OFFERING_STATUS.get(offer_type, "equity_prospectus_review"),
                filing_date=filing_date,
                updated_at=str(row.get("sec_docLastUpdateDate", "")).strip() or "-",
                observed_on=observed_on,
                source_url=ESMA_HELP_URL,
            )
        )
    return _validate_unique(prospectuses)


def write_esma_csv(path: str | Path, prospectuses: list[EsmaEquityProspectus]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(EsmaEquityProspectus.__annotations__))
        writer.writeheader()
        for item in prospectuses:
            row = dict(item.__dict__)
            row["filing_date"] = item.filing_date.isoformat()
            row["observed_on"] = item.observed_on.isoformat()
            writer.writerow(row)


def render_esma_report(
    prospectuses: list[EsmaEquityProspectus], as_of: date, since: date, source_mode: str
) -> str:
    _validate_as_of(prospectuses, as_of)
    label = (
        "Official live ESMA A2A query"
        if source_mode == "live"
        else "Synthetic ESMA-shaped fixture"
    )
    lines = [
        "# ESMA Equity Prospectus Watch",
        "",
        f"- Report generated as of: `{as_of.isoformat()}`",
        f"- Filing window starts: `{since.isoformat()}`",
        f"- Source mode: `{source_mode}` - {label}",
        f"- Official A2A documentation: <{ESMA_HELP_URL}>",
        f"- Official reuse notice: <{ESMA_LEGAL_URL}>",
        f"- Equity prospectus records observed: `{len(prospectuses)}`",
        "",
        "This monitor selects records officially classified as shares in the ESMA",
        "Prospectus III securities register for Germany, Netherlands and Italy.",
        "An ESMA record is prospectus or admission-review evidence; it does not",
        "confirm first trading, investment suitability or an investment action.",
        "",
        "## Equity Prospectus Queue",
        "",
        "| Filing Date | Jurisdiction | Issuer | ISIN | Offer / Admission Evidence | State |",
        "|---|---|---|---|---|---|",
    ]
    if not prospectuses:
        lines.append("| - | - | No equity prospectuses in selected window | - | - | - |")
    for item in sorted(prospectuses, key=lambda entry: entry.filing_date, reverse=True):
        lines.append(
            f"| {item.filing_date.isoformat()} | {item.jurisdiction} | {item.company_name} | "
            f"{item.isin} | {item.offer_admission_type} | `{item.status}` |"
        )
    return "\n".join(lines) + "\n"


def write_esma_report(
    path: str | Path,
    prospectuses: list[EsmaEquityProspectus],
    as_of: date,
    since: date,
    source_mode: str,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_esma_report(prospectuses, as_of, since, source_mode), encoding="utf-8"
    )


def render_esma_html(
    prospectuses: list[EsmaEquityProspectus], as_of: date, since: date, source_mode: str
) -> str:
    _validate_as_of(prospectuses, as_of)
    label = (
        "Official live ESMA A2A query"
        if source_mode == "live"
        else "Synthetic reproducible fixture, not official prospectus evidence"
    )
    rows = "".join(
        "<tr>"
        f"<td>{escape(item.filing_date.isoformat())}</td>"
        f"<td>{escape(item.jurisdiction)}</td>"
        f"<td><strong>{escape(item.company_name)}</strong><small>{escape(item.isin)}</small></td>"
        f"<td>{escape(item.offer_admission_type)}<small>{escape(item.document_id)}</small></td>"
        f'<td><span class="badge">{escape(_display_status(item.status))}</span></td>'
        f'<td><a href="{escape(item.source_url)}">ESMA register</a></td>'
        "</tr>"
        for item in sorted(prospectuses, key=lambda entry: entry.filing_date, reverse=True)
    )
    if not rows:
        rows = '<tr><td colspan="6">No share prospectuses observed in the selected filing window.</td></tr>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarketWitness | ESMA Equity Prospectus Watch</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1140px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:800px}}
.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:270px;display:inline-block;margin:35px 0}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}.card small,td small{{display:block;color:var(--muted)}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}a{{color:var(--mint);text-decoration:none}}.badge{{color:var(--gold);background:rgba(240,188,98,.12);border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}
@media(max-width:800px){{.table-wrap{{overflow:visible;background:transparent;border:0}}table,tbody,tr,td{{display:block;width:100%}}thead{{display:none}}tr{{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin:12px 0;padding:8px 14px}}td{{border:0;padding:7px 0;overflow-wrap:anywhere}}td::before{{display:block;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px}}td:nth-child(1)::before{{content:"Filed"}}td:nth-child(2)::before{{content:"Jurisdiction"}}td:nth-child(3)::before{{content:"Issuer"}}td:nth-child(4)::before{{content:"Event evidence"}}td:nth-child(5)::before{{content:"State"}}td:nth-child(6)::before{{content:"Source"}}.badge{{display:inline-block;white-space:normal}}}}
</style></head><body><header><nav><a href="/dashboard/global-listings">Global Listings Watch</a> / ESMA</nav>
<h1>Europe.<br>Equity prospectuses.</h1><p class="lead">Share records selected from the official ESMA Prospectus III securities register.</p>
<p class="meta">Observed as of {escape(as_of.isoformat())} / filings since {escape(since.isoformat())} / Germany, Netherlands, Italy</p><article class="card"><p>Equity prospectus records</p><strong>{len(prospectuses)}</strong><small>{escape(label)}</small></article></header>
<main><p class="notice">An ESMA prospectus or admission record opens regulatory review. It does not confirm first trading or an investment decision. Transformed register metadata is attributed under the <a href="{escape(ESMA_LEGAL_URL)}">official ESMA legal notice</a>.</p>
<h2>Prospectus queue</h2><div class="table-wrap"><table><thead><tr><th>Filed</th><th>Jurisdiction</th><th>Issuer</th><th>Event evidence</th><th>State</th><th>Source</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_esma_html(
    path: str | Path,
    prospectuses: list[EsmaEquityProspectus],
    as_of: date,
    since: date,
    source_mode: str,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_esma_html(prospectuses, as_of, since, source_mode), encoding="utf-8"
    )


def _date_field(row: dict[str, object], key: str) -> date:
    raw = str(row.get(key, "")).strip()
    if not raw:
        raise EsmaDataError(f"ESMA shares record is missing {key}.")
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
    except ValueError as exc:
        raise EsmaDataError(f"ESMA shares record contains invalid date: {raw}.") from exc


def _validate_unique(prospectuses: list[EsmaEquityProspectus]) -> list[EsmaEquityProspectus]:
    seen: set[tuple[str, str]] = set()
    for item in prospectuses:
        key = (item.document_id, item.isin)
        if key in seen:
            raise EsmaDataError(
                f"ESMA response duplicates document/instrument pair {item.document_id} / {item.isin}."
            )
        seen.add(key)
    return prospectuses


def _validate_as_of(prospectuses: list[EsmaEquityProspectus], as_of: date) -> None:
    if any(item.observed_on > as_of for item in prospectuses):
        raise EsmaDataError("ESMA snapshot includes a future observation.")


def _display_status(status: str) -> str:
    return {
        "initial_admission_regulated_market_review": "Initial regulated-market admission review",
        "initial_admission_mtf_review": "Initial MTF admission review",
        "initial_offer_without_admission_review": "Initial offer review",
        "secondary_issuance_review": "Secondary issuance review",
        "secondary_offer_without_admission_review": "Secondary offer review",
        "equity_prospectus_review": "Equity prospectus review",
    }.get(status, status)
