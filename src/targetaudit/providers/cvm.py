from __future__ import annotations

import csv
import io
import unicodedata
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

CVM_DATASET_URL = "https://dados.cvm.gov.br/dataset/oferta-distrib"
CVM_RESOURCE_URL = (
    "https://dados.cvm.gov.br/dados/OFERTA/DISTRIB/DADOS/oferta_distribuicao.zip"
)
CVM_SOURCE_FILES = ("oferta_distribuicao.csv", "oferta_resolucao_160.csv")


class CvmDataError(ValueError):
    """Raised when CVM equity-offering evidence is unusable."""


@dataclass(frozen=True)
class CvmEquityOffering:
    company_name: str
    offering_id: str
    security_type: str
    offering_type: str
    procedure: str
    status: str
    filing_date: date
    registration_date: str
    observed_on: date
    source_url: str
    resource_url: str


def fetch_cvm_equity_offerings(
    since: date, observed_on: date | None = None
) -> list[CvmEquityOffering]:
    request = Request(
        CVM_RESOURCE_URL,
        headers={
            "User-Agent": "TargetAudit/0.1 public-research-monitor",
            "Accept": "application/zip",
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            archive = zipfile.ZipFile(io.BytesIO(response.read()))
    except (URLError, TimeoutError, OSError, zipfile.BadZipFile) as exc:
        raise CvmDataError(f"Unable to retrieve CVM offerings: {exc}") from exc
    results: list[CvmEquityOffering] = []
    try:
        names = set(archive.namelist())
        missing = [name for name in CVM_SOURCE_FILES if name not in names]
        if missing:
            raise CvmDataError(f"CVM ZIP is missing expected CSV: {', '.join(missing)}.")
        for name in CVM_SOURCE_FILES:
            with archive.open(name) as raw:
                content = raw.read().decode("latin-1")
            results.extend(
                parse_cvm_csv(
                    content,
                    observed_on or date.today(),
                    since,
                    resource_url=CVM_RESOURCE_URL,
                )
            )
    finally:
        archive.close()
    return _validate_unique(results)


def load_cvm_snapshot(
    path: str | Path, observed_on: date, since: date
) -> list[CvmEquityOffering]:
    try:
        content = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise CvmDataError(f"Unable to read CVM snapshot {path}: {exc}") from exc
    return parse_cvm_csv(content, observed_on, since, resource_url=CVM_RESOURCE_URL)


def parse_cvm_csv(
    content: str,
    observed_on: date,
    since: date,
    resource_url: str = CVM_RESOURCE_URL,
) -> list[CvmEquityOffering]:
    reader = csv.DictReader(io.StringIO(content), delimiter=";")
    fields = set(reader.fieldnames or [])
    if "Numero_Processo" not in fields:
        raise CvmDataError("CVM CSV does not contain an offering process identifier.")
    if "Tipo_Ativo" in fields:
        normalizer = _main_dataset_record
    elif "Valor_Mobiliario" in fields:
        normalizer = _resolution_160_record
    else:
        raise CvmDataError("CVM CSV schema is not a supported offering dataset.")
    offerings: list[CvmEquityOffering] = []
    for row in reader:
        item = normalizer(row, observed_on, since, resource_url)
        if item:
            offerings.append(item)
    return _validate_unique(offerings)


def _main_dataset_record(
    row: dict[str, str], observed_on: date, since: date, resource_url: str
) -> CvmEquityOffering | None:
    security = row.get("Tipo_Ativo", "").strip()
    if not _is_equity_security(security):
        return None
    company = row.get("Nome_Emissor", "").strip()
    identifier = (
        row.get("Numero_Registro_Oferta", "").strip()
        or row.get("Numero_Processo", "").strip()
    )
    filing_date = _optional_date(row, "Data_Protocolo", "Data_Abertura_Processo")
    if filing_date is None or filing_date < since:
        return None
    return _offering(
        company,
        identifier,
        security,
        row.get("Tipo_Oferta", "").strip(),
        row.get("Rito_Oferta", "").strip(),
        _status_from_values(
            row.get("Data_Encerramento_Oferta", ""),
            row.get("Modalidade_Registro", ""),
        ),
        filing_date,
        row.get("Data_Registro_Oferta", "").strip(),
        observed_on,
        resource_url,
    )


def _resolution_160_record(
    row: dict[str, str], observed_on: date, since: date, resource_url: str
) -> CvmEquityOffering | None:
    security = row.get("Valor_Mobiliario", "").strip()
    if not _is_equity_security(security):
        return None
    filing_date = _optional_date(row, "Data_requerimento", "Data_Registro")
    if filing_date is None or filing_date < since:
        return None
    return _offering(
        row.get("Nome_Emissor", "").strip(),
        row.get("Numero_Processo", "").strip()
        or row.get("Numero_Requerimento", "").strip(),
        security,
        row.get("Tipo_Oferta", "").strip(),
        row.get("Rito_Requerimento", "").strip(),
        _status_from_values(
            row.get("Data_Encerramento", ""),
            row.get("Status_Requerimento", ""),
        ),
        filing_date,
        row.get("Data_Registro", "").strip(),
        observed_on,
        resource_url,
    )


def _offering(
    company_name: str,
    offering_id: str,
    security_type: str,
    offering_type: str,
    procedure: str,
    status: str,
    filing_date: date,
    registration_date: str,
    observed_on: date,
    resource_url: str,
) -> CvmEquityOffering:
    if not company_name or not offering_id or not offering_type or not procedure:
        raise CvmDataError("CVM equity offering is missing required identity fields.")
    if filing_date > observed_on:
        raise CvmDataError("CVM snapshot includes an offering filed after observation date.")
    return CvmEquityOffering(
        company_name=company_name,
        offering_id=offering_id,
        security_type=security_type,
        offering_type=offering_type,
        procedure=procedure,
        status=status,
        filing_date=filing_date,
        registration_date=registration_date or "-",
        observed_on=observed_on,
        source_url=CVM_DATASET_URL,
        resource_url=resource_url,
    )


def _is_equity_security(value: str) -> bool:
    normalized = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().strip().upper()
    )
    return (
        normalized in {"ACAO", "ACOES"}
        or normalized.startswith("ACAO ")
        or normalized.startswith("ACOES ")
    )


def _optional_date(row: dict[str, str], *keys: str) -> date | None:
    for key in keys:
        raw = row.get(key, "").strip()
        if raw:
            return _parse_date(raw)
    return None


def _parse_date(value: str) -> date:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise CvmDataError(f"CVM offering contains invalid date: {value}.")


def _status_from_values(closing_date: str, raw_status: str) -> str:
    if closing_date.strip():
        return "offering_closed"
    normalized = unicodedata.normalize("NFKD", raw_status).encode("ascii", "ignore").decode()
    if "CANCEL" in normalized.upper() or "DESIST" in normalized.upper():
        return "offering_cancelled_or_withdrawn"
    return "offering_recorded"


def _validate_unique(offerings: list[CvmEquityOffering]) -> list[CvmEquityOffering]:
    seen: set[str] = set()
    for item in offerings:
        if item.offering_id in seen:
            raise CvmDataError(f"CVM response duplicates offering ID {item.offering_id}.")
        seen.add(item.offering_id)
    return offerings


def write_cvm_csv(path: str | Path, offerings: list[CvmEquityOffering]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(CvmEquityOffering.__annotations__))
        writer.writeheader()
        for item in offerings:
            row = dict(item.__dict__)
            row["filing_date"] = item.filing_date.isoformat()
            row["observed_on"] = item.observed_on.isoformat()
            writer.writerow(row)


def render_cvm_report(
    offerings: list[CvmEquityOffering], as_of: date, since: date, source_mode: str
) -> str:
    _validate_as_of(offerings, as_of)
    label = "Official live CVM ZIP" if source_mode == "live" else "Synthetic CVM-shaped fixture"
    lines = [
        "# CVM Equity Offering Watch",
        "",
        f"- Report generated as of: `{as_of.isoformat()}`",
        f"- Filing window starts: `{since.isoformat()}`",
        f"- Source mode: `{source_mode}` - {label}",
        f"- Official dataset: <{CVM_DATASET_URL}>",
        f"- Equity-offering records observed: `{len(offerings)}`",
        "",
        "This monitor selects share offerings from CVM public-distribution records.",
        "A CVM offering record is Brazilian regulatory evidence; it does not",
        "confirm a B3 listing, first trading or an investment action.",
        "",
        "## Equity Offering Queue",
        "",
        "| Filing Date | Issuer | Security | Offering | Procedure | State |",
        "|---|---|---|---|---|---|",
    ]
    if not offerings:
        lines.append("| - | No equity offerings in selected window | - | - | - | - |")
    for item in sorted(offerings, key=lambda entry: entry.filing_date, reverse=True):
        lines.append(
            f"| {item.filing_date.isoformat()} | {item.company_name} | {item.security_type} | "
            f"{item.offering_type} | {item.procedure} | `{item.status}` |"
        )
    return "\n".join(lines) + "\n"


def write_cvm_report(
    path: str | Path,
    offerings: list[CvmEquityOffering],
    as_of: date,
    since: date,
    source_mode: str,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_cvm_report(offerings, as_of, since, source_mode), encoding="utf-8"
    )


def render_cvm_html(
    offerings: list[CvmEquityOffering], as_of: date, since: date, source_mode: str
) -> str:
    _validate_as_of(offerings, as_of)
    label = (
        "Official live CVM ZIP"
        if source_mode == "live"
        else "Synthetic reproducible fixture, not official offering evidence"
    )
    rows = "".join(
        "<tr>"
        f"<td>{escape(item.filing_date.isoformat())}</td>"
        f"<td><strong>{escape(item.company_name)}</strong><small>{escape(item.offering_id)}</small></td>"
        f"<td>{escape(item.security_type)}</td>"
        f"<td>{escape(item.offering_type)}<small>{escape(item.procedure)}</small></td>"
        f'<td><span class="badge">{escape(_display_status(item.status))}</span></td>'
        f'<td><a href="{escape(item.source_url)}">CVM dataset</a></td>'
        "</tr>"
        for item in sorted(offerings, key=lambda entry: entry.filing_date, reverse=True)
    )
    if not rows:
        rows = '<tr><td colspan="6">No equity offerings observed in the selected filing window.</td></tr>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | CVM Equity Offering Watch</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1140px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:800px}}
.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:260px;display:inline-block;margin:35px 0}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}.card small,td small{{display:block;color:var(--muted)}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}a{{color:var(--mint);text-decoration:none}}.badge{{color:var(--gold);background:rgba(240,188,98,.12);border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}
@media(max-width:800px){{.table-wrap{{overflow:visible;background:transparent;border:0}}table,tbody,tr,td{{display:block;width:100%}}thead{{display:none}}tr{{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin:12px 0;padding:8px 14px}}td{{border:0;padding:7px 0;overflow-wrap:anywhere}}td::before{{display:block;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px}}td:nth-child(1)::before{{content:"Filed"}}td:nth-child(2)::before{{content:"Issuer"}}td:nth-child(3)::before{{content:"Security"}}td:nth-child(4)::before{{content:"Offer"}}td:nth-child(5)::before{{content:"State"}}td:nth-child(6)::before{{content:"Evidence"}}.badge{{display:inline-block;white-space:normal}}}}
</style></head><body><header><nav><a href="/dashboard/global-listings">Global Listings Watch</a> / CVM</nav>
<h1>Brazil.<br>Equity offerings.</h1><p class="lead">Share-offering records selected from CVM public-distribution open data.</p>
<p class="meta">Observed as of {escape(as_of.isoformat())} / filings since {escape(since.isoformat())}</p><article class="card"><p>Equity offering records</p><strong>{len(offerings)}</strong><small>{escape(label)}</small></article></header>
<main><p class="notice">A CVM offering record opens Brazilian regulatory review. It does not confirm B3 listing, trading or an investment decision.</p>
<h2>Offering queue</h2><div class="table-wrap"><table><thead><tr><th>Filed</th><th>Issuer</th><th>Security</th><th>Offer</th><th>State</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def write_cvm_html(
    path: str | Path,
    offerings: list[CvmEquityOffering],
    as_of: date,
    since: date,
    source_mode: str,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_cvm_html(offerings, as_of, since, source_mode), encoding="utf-8"
    )


def _validate_as_of(offerings: list[CvmEquityOffering], as_of: date) -> None:
    if any(item.observed_on > as_of for item in offerings):
        raise CvmDataError("CVM snapshot includes a future observation.")


def _display_status(status: str) -> str:
    return {
        "offering_recorded": "Offering recorded",
        "offering_closed": "Offering closed",
        "offering_cancelled_or_withdrawn": "Offering cancelled or withdrawn",
    }.get(status, status)
