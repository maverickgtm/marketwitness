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

EDINET_DOCUMENTS_URL = "https://api.edinet-fsa.go.jp/api/v2/documents.json"
EDINET_DOCUMENT_URL = "https://api.edinet-fsa.go.jp/api/v2/documents/{doc_id}"
EDINET_GUIDE_URL = (
    "https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html"
)
OFFERING_DOCUMENT_TYPES = {
    "030": "securities_registration_statement",
    "040": "amended_securities_registration_statement",
    "050": "registration_withdrawal_request",
}
OFFERING_DISPLAY_STATES = {
    "030": "Initial registration",
    "040": "Amendment",
    "050": "Withdrawal request",
}


class EdinetDataError(ValueError):
    """Raised when EDINET offering-document evidence is unusable."""


@dataclass(frozen=True)
class EdinetOfferingFiling:
    company_name: str
    edinet_code: str
    security_code: str
    document_id: str
    document_type_code: str
    status: str
    submitted_at: str
    observed_on: date
    source_url: str
    document_url: str


def fetch_edinet_offering_filings(
    filing_date: date, api_key: str | None = None
) -> list[EdinetOfferingFiling]:
    key = (api_key or os.environ.get("TARGETAUDIT_EDINET_API_KEY", "")).strip()
    if not key:
        raise EdinetDataError(
            "Live EDINET collection requires --api-key or TARGETAUDIT_EDINET_API_KEY."
        )
    query = urlencode(
        {"date": filing_date.isoformat(), "type": "2", "Subscription-Key": key}
    )
    request = Request(
        f"{EDINET_DOCUMENTS_URL}?{query}",
        headers={
            "User-Agent": "TargetAudit/0.1 public-research-monitor",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise EdinetDataError(f"Unable to retrieve EDINET documents: {exc}") from exc
    return parse_edinet_payload(payload, filing_date)


def load_edinet_snapshot(
    path: str | Path, observed_on: date
) -> list[EdinetOfferingFiling]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EdinetDataError(f"Unable to read EDINET snapshot {path}: {exc}") from exc
    return parse_edinet_payload(payload, observed_on)


def parse_edinet_payload(
    payload: object, observed_on: date
) -> list[EdinetOfferingFiling]:
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise EdinetDataError("EDINET response does not contain a results list.")
    filings: list[EdinetOfferingFiling] = []
    seen: set[str] = set()
    for record in payload["results"]:
        if not isinstance(record, dict):
            raise EdinetDataError("EDINET results contain an invalid document record.")
        document_type = str(record.get("docTypeCode") or "").strip()
        if document_type not in OFFERING_DOCUMENT_TYPES:
            continue
        document_id = str(record.get("docID") or "").strip()
        company_name = str(record.get("filerName") or "").strip()
        edinet_code = str(record.get("edinetCode") or "").strip()
        submitted_at = str(record.get("submitDateTime") or "").strip()
        if not document_id or not company_name or not edinet_code or not submitted_at:
            raise EdinetDataError("EDINET offering document is missing required fields.")
        if document_id in seen:
            raise EdinetDataError(f"EDINET response duplicates document ID {document_id}.")
        _validate_submitted_at(submitted_at, observed_on)
        seen.add(document_id)
        filings.append(
            EdinetOfferingFiling(
                company_name=company_name,
                edinet_code=edinet_code,
                security_code=str(record.get("secCode") or "-").strip() or "-",
                document_id=document_id,
                document_type_code=document_type,
                status=OFFERING_DOCUMENT_TYPES[document_type],
                submitted_at=submitted_at,
                observed_on=observed_on,
                source_url=EDINET_GUIDE_URL,
                document_url=EDINET_DOCUMENT_URL.format(doc_id=document_id),
            )
        )
    return filings


def _validate_submitted_at(value: str, observed_on: date) -> None:
    try:
        submitted = datetime.strptime(value[:10], "%Y-%m-%d").date()
    except ValueError as exc:
        raise EdinetDataError(f"EDINET document contains invalid submission date: {value}") from exc
    if submitted > observed_on:
        raise EdinetDataError("EDINET snapshot includes a future filing.")


def write_edinet_csv(path: str | Path, filings: list[EdinetOfferingFiling]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(EdinetOfferingFiling.__annotations__))
        writer.writeheader()
        for filing in filings:
            row = dict(filing.__dict__)
            row["observed_on"] = filing.observed_on.isoformat()
            writer.writerow(row)


def render_edinet_report(
    filings: list[EdinetOfferingFiling], as_of: date, source_mode: str
) -> str:
    _validate_as_of(filings, as_of)
    label = "Official live EDINET response" if source_mode == "live" else "Synthetic EDINET-shaped fixture"
    lines = [
        "# EDINET Offering Filing Watch",
        "",
        f"- Report generated as of: `{as_of.isoformat()}`",
        f"- Source mode: `{source_mode}` - {label}",
        f"- Official API guide: <{EDINET_GUIDE_URL}>",
        f"- Offering-document records observed: `{len(filings)}`",
        "",
        "This monitor filters official EDINET document types `030`, `040` and",
        "`050`: securities registration statements, amendments and withdrawal",
        "requests. A filing starts documentary review; it does not confirm a",
        "JPX listing or constitute an investment recommendation.",
        "",
        "## Document Queue",
        "",
        "| Submitted | Issuer | EDINET Code | Security Code | State | Document |",
        "|---|---|---|---|---|---|",
    ]
    if not filings:
        lines.append("| - | No offering filings found for the requested date | - | - | - | - |")
    for item in sorted(filings, key=lambda filing: filing.submitted_at, reverse=True):
        evidence = (
            f"[EDINET API endpoint (key required)]({item.document_url})"
            if source_mode == "live"
            else "Synthetic identifier only"
        )
        lines.append(
            f"| {item.submitted_at} | {item.company_name} | {item.edinet_code} | "
            f"{item.security_code} | `{item.status}` | "
            f"{evidence} |"
        )
    return "\n".join(lines) + "\n"


def write_edinet_report(
    path: str | Path,
    filings: list[EdinetOfferingFiling],
    as_of: date,
    source_mode: str,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_edinet_report(filings, as_of, source_mode), encoding="utf-8"
    )


def render_edinet_html(
    filings: list[EdinetOfferingFiling], as_of: date, source_mode: str
) -> str:
    _validate_as_of(filings, as_of)
    mode_label = (
        "Official live EDINET response"
        if source_mode == "live"
        else "Synthetic reproducible fixture, not public filing evidence"
    )
    rows = ""
    for item in sorted(filings, key=lambda filing: filing.submitted_at, reverse=True):
        evidence = (
            f'<a href="{escape(item.document_url)}">API endpoint (key required)</a>'
            if source_mode == "live"
            else "Synthetic identifier"
        )
        rows += (
            "<tr>"
            f"<td>{escape(item.submitted_at)}</td>"
            f"<td><strong>{escape(item.company_name)}</strong><small>{escape(item.edinet_code)}</small></td>"
            f"<td>{escape(item.security_code)}</td>"
            f'<td><span class="badge">{escape(OFFERING_DISPLAY_STATES[item.document_type_code])}</span></td>'
            f"<td>{evidence}</td>"
            "</tr>"
        )
    if not rows:
        rows = '<tr><td colspan="5">No offering documents found for the requested filing date.</td></tr>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | EDINET Offering Filing Watch</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1140px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:800px}}
.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:250px;display:inline-block;margin:35px 0}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}.card small{{color:var(--muted)}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}td small{{display:block;color:var(--muted)}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}a{{color:var(--mint);text-decoration:none}}.badge{{color:var(--gold);background:rgba(240,188,98,.12);border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}
@media(max-width:800px){{table{{table-layout:fixed}}th,td{{padding:12px 8px;overflow-wrap:anywhere}}.badge{{display:inline-block;white-space:normal}}}}
</style></head><body><header><nav><a href="/dashboard/global-listings">Global Listings Watch</a> / EDINET</nav>
<h1>Japan.<br>Offering filings.</h1><p class="lead">Securities registration statements, amendments and withdrawal requests selected from Japan FSA EDINET document metadata.</p>
<p class="meta">Observed as of {escape(as_of.isoformat())}</p><article class="card"><p>Document records</p><strong>{len(filings)}</strong><small>{escape(mode_label)}</small></article></header>
<main><p class="notice">An EDINET filing opens documentary review. Only JPX evidence can confirm an approved or completed exchange listing; neither source is a trading instruction.</p>
<h2>Offering document queue</h2><div class="table-wrap"><table><thead><tr><th>Submitted</th><th>Issuer</th><th>Security code</th><th>State</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_edinet_html(
    path: str | Path,
    filings: list[EdinetOfferingFiling],
    as_of: date,
    source_mode: str,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_edinet_html(filings, as_of, source_mode), encoding="utf-8"
    )


def _validate_as_of(filings: list[EdinetOfferingFiling], as_of: date) -> None:
    if any(item.observed_on > as_of for item in filings):
        raise EdinetDataError("EDINET snapshot includes a future observation.")
