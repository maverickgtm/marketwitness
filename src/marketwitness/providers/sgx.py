from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

SGX_SOURCE_URL = "https://www.sgx.com/securities/ipo-prospectus"
SGX_API_URL = "https://api.sgx.com/ipoprospectus/v1.0/"
SGX_FIELDS = "closing_date,name,id,modified_date,url,status"
SGX_TIMEZONE = ZoneInfo("Asia/Singapore")


class SgxDataError(ValueError):
    """Raised when SGX IPO-prospectus evidence is unusable."""


@dataclass(frozen=True)
class SgxProspectus:
    company_name: str
    document_id: str
    status: str
    closing_date: str
    modified_date: str
    prospectus_url: str
    observed_on: date
    source_url: str


def fetch_sgx_prospectuses() -> list[SgxProspectus]:
    count_payload = _fetch_json(f"{SGX_API_URL}count?{urlencode({'params': SGX_FIELDS})}")
    try:
        count = int(count_payload["count"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SgxDataError("SGX count response does not contain a valid count.") from exc
    records: list[dict[str, object]] = []
    page_size = 250
    total_pages = (count + page_size - 1) // page_size
    for page_start in range(total_pages):
        query = urlencode(
            {"params": SGX_FIELDS, "pagesize": page_size, "pagestart": page_start}
        )
        payload = _fetch_json(f"{SGX_API_URL}?{query}")
        records.extend(_records_from_payload(payload))
    if len(records) != count:
        raise SgxDataError(
            f"SGX returned {len(records)} prospectuses but advertised {count}."
        )
    return parse_sgx_records(records, date.today())


def load_sgx_snapshot(path: str | Path, observed_on: date) -> list[SgxProspectus]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SgxDataError(f"Unable to read SGX snapshot {path}: {exc}") from exc
    return parse_sgx_records(_records_from_payload(payload), observed_on)


def parse_sgx_records(
    records: list[dict[str, object]], observed_on: date
) -> list[SgxProspectus]:
    if not records:
        raise SgxDataError("SGX response does not contain IPO prospectus records.")
    prospectuses: list[SgxProspectus] = []
    seen: set[str] = set()
    for record in records:
        name = str(record.get("name") or "").strip()
        document_id = str(record.get("id") or "").strip()
        raw_status = str(record.get("status") or "").strip()
        document_url = str(record.get("url") or "").strip()
        if not name or not document_id or not raw_status or not document_url:
            raise SgxDataError("SGX prospectus is missing required document fields.")
        if document_id in seen:
            raise SgxDataError(f"SGX response duplicates document ID {document_id}.")
        seen.add(document_id)
        prospectuses.append(
            SgxProspectus(
                company_name=name,
                document_id=document_id,
                status="prospectus_published",
                closing_date=_format_closing_date(record.get("closing_date")),
                modified_date=str(record.get("modified_date") or "-").strip() or "-",
                prospectus_url=document_url,
                observed_on=observed_on,
                source_url=SGX_SOURCE_URL,
            )
        )
    return prospectuses


def _records_from_payload(payload: object) -> list[dict[str, object]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise SgxDataError("SGX response does not contain a data list.")
    records = payload["data"]
    if not all(isinstance(record, dict) for record in records):
        raise SgxDataError("SGX data list contains an invalid record.")
    return records


def _fetch_json(url: str) -> dict[str, object]:
    request = Request(
        url,
        headers={
            "User-Agent": "MarketWitness/0.1 public-research-monitor",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise SgxDataError(f"Unable to retrieve SGX prospectus records: {exc}") from exc
    if not isinstance(payload, dict):
        raise SgxDataError("SGX API returned a non-object response.")
    return payload


def _format_closing_date(value: object) -> str:
    if value is None:
        return "-"
    try:
        moment = datetime.fromtimestamp(int(value) / 1000, timezone.utc).astimezone(
            SGX_TIMEZONE
        )
    except (TypeError, ValueError, OSError, OverflowError) as exc:
        raise SgxDataError("SGX prospectus contains an invalid closing date.") from exc
    return moment.strftime("%Y-%m-%d %H:%M SGT")


def write_sgx_csv(path: str | Path, prospectuses: list[SgxProspectus]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(SgxProspectus.__annotations__))
        writer.writeheader()
        for prospectus in prospectuses:
            row = dict(prospectus.__dict__)
            row["observed_on"] = prospectus.observed_on.isoformat()
            writer.writerow(row)


def render_sgx_report(prospectuses: list[SgxProspectus], as_of: date) -> str:
    _validate_as_of(prospectuses, as_of)
    lines = [
        "# SGX IPO Prospectus Monitor",
        "",
        f"- Report generated as of: `{as_of.isoformat()}`",
        f"- Official page: <{SGX_SOURCE_URL}>",
        f"- Published prospectus records observed: `{len(prospectuses)}`",
        "",
        "This monitor records IPO prospectus documents published in SGX's official",
        "catalogue. Publication is documentary evidence requiring review; it does",
        "not by itself confirm completed admission, trading or an investment action.",
        "",
        "## Latest Prospectus Records",
        "",
        "| Issuer | State | Closing Date (SGT) | Modified Date | Document |",
        "|---|---|---|---|---|",
    ]
    for item in prospectuses:
        lines.append(
            f"| {item.company_name} | `{item.status}` | {item.closing_date} | "
            f"{item.modified_date} | [SGX prospectus]({item.prospectus_url}) |"
        )
    return "\n".join(lines) + "\n"


def write_sgx_report(
    path: str | Path, prospectuses: list[SgxProspectus], as_of: date
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_sgx_report(prospectuses, as_of), encoding="utf-8")


def render_sgx_html(prospectuses: list[SgxProspectus], as_of: date) -> str:
    _validate_as_of(prospectuses, as_of)
    rows = "".join(
        "<tr>"
        f"<td><strong>{escape(item.company_name)}</strong></td>"
        f'<td><span class="badge">{escape(item.status)}</span></td>'
        f"<td>{escape(item.closing_date)}</td>"
        f"<td>{escape(item.modified_date)}</td>"
        f'<td><a href="{escape(item.prospectus_url)}">Document</a></td>'
        "</tr>"
        for item in prospectuses
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarketWitness | SGX IPO Prospectus</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1120px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:780px}}
.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:220px;display:inline-block;margin:35px 0}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}a{{color:var(--mint);text-decoration:none}}.badge{{color:var(--mint);background:rgba(86,218,172,.12);border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}
@media(max-width:800px){{.table-wrap{{overflow-x:auto}}table{{min-width:780px}}}}
</style></head><body><header><nav><a href="/dashboard/global-listings">Global Listings Watch</a> / SGX</nav>
<h1>Singapore.<br>IPO prospectuses.</h1><p class="lead">Documents observed in the official SGX IPO Prospectus catalogue.</p>
<p class="meta">Observed as of {escape(as_of.isoformat())}</p><article class="card"><p>Published records</p><strong>{len(prospectuses)}</strong></article></header>
<main><p class="notice">A published prospectus is a document signal requiring review. It is not proof of completed listing or a trading instruction.</p>
<h2>Prospectus catalogue</h2><div class="table-wrap"><table><thead><tr><th>Issuer</th><th>State</th><th>Closing date (SGT)</th><th>Modified date</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_sgx_html(path: str | Path, prospectuses: list[SgxProspectus], as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_sgx_html(prospectuses, as_of), encoding="utf-8")


def _validate_as_of(prospectuses: list[SgxProspectus], as_of: date) -> None:
    if any(item.observed_on > as_of for item in prospectuses):
        raise SgxDataError("SGX snapshot includes a future observation.")
