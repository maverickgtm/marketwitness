from __future__ import annotations

import csv
import json
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from ..lse_upcoming import LseUpcomingIssue

FCA_NSM_PORTAL_URL = "https://data.fca.org.uk/#/nsm/nationalstoragemechanism"
FCA_NSM_GUIDANCE_URL = (
    "https://www.fca.org.uk/markets/primary-markets/regulatory-disclosures/"
    "national-storage-mechanism"
)
FCA_NSM_SEARCH_URL = (
    "https://api.data.fca.org.uk/search?index=fca-nsm-searchdata"
)
FCA_DOCUMENT_BASE_URL = "https://data.fca.org.uk/artefacts/"


class FcaNsmDataError(ValueError):
    """Raised when FCA NSM evidence cannot be parsed or retrieved."""


@dataclass(frozen=True)
class FcaNsmDocument:
    company_name: str
    headline: str
    category: str
    submitted_at: datetime
    publication_at: datetime | None
    disclosure_id: str
    document_url: str

    @property
    def evidence_class(self) -> str:
        category = self.category.upper()
        if "PROSPECTUS" in category:
            return "prospectus_document_signal"
        if "ADMISSION DOCUMENT" in category:
            return "admission_document_signal"
        if "INTENTION TO FLOAT" in category:
            return "intention_to_float_notice"
        return "other_document_review"

    @property
    def classification_basis(self) -> str:
        basis = {
            "prospectus_document_signal": "FCA document type contains Prospectus.",
            "admission_document_signal": "FCA document type contains Admission Document.",
            "intention_to_float_notice": "FCA document type contains Intention to Float.",
            "other_document_review": "FCA document type does not identify a prospectus or admission document.",
        }
        return basis[self.evidence_class]


@dataclass(frozen=True)
class LseFcaCheck:
    issue: LseUpcomingIssue
    documents: tuple[FcaNsmDocument, ...]

    @property
    def status(self) -> str:
        if self.documents:
            return "document_found_review_required"
        return "no_document_found"

    @property
    def evidence_class(self) -> str:
        if not self.documents:
            return "no_document_found"
        return self.evidence_document.evidence_class

    @property
    def evidence_document(self) -> FcaNsmDocument:
        priority = {
            "prospectus_document_signal": 0,
            "admission_document_signal": 1,
            "intention_to_float_notice": 2,
            "other_document_review": 3,
        }
        return min(self.documents, key=lambda item: priority[item.evidence_class])


def fetch_nsm_documents(company_name: str, limit: int = 5) -> list[FcaNsmDocument]:
    if limit < 1 or limit > 50:
        raise FcaNsmDataError("FCA NSM result limit must be between 1 and 50.")
    body = json.dumps(_search_payload(company_name, limit)).encode("utf-8")
    request = Request(
        FCA_NSM_SEARCH_URL,
        data=body,
        method="POST",
        headers={
            "User-Agent": "TargetAudit/0.1 public-research-monitor",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise FcaNsmDataError(
            f"Unable to retrieve FCA NSM evidence for {company_name}: {exc}"
        ) from exc
    return parse_nsm_search_payload(payload)


def _search_payload(company_name: str, limit: int) -> dict[str, object]:
    return {
        "from": 0,
        "size": limit,
        "sort": "submitted_date",
        "sortorder": "desc",
        "criteriaObj": {
            "criteria": [
                {
                    "name": "company_lei",
                    "value": [company_name, None, "disclose_org", "related_org"],
                },
                {"name": "latest_flag", "value": "Y"},
            ],
            "dateCriteria": None,
        },
    }


def parse_nsm_search_payload(payload: object) -> list[FcaNsmDocument]:
    if not isinstance(payload, dict):
        raise FcaNsmDataError("Unexpected FCA NSM response.")
    hits = payload.get("hits")
    rows = hits.get("hits") if isinstance(hits, dict) else None
    if not isinstance(rows, list):
        raise FcaNsmDataError("FCA NSM response is missing search hits.")
    documents: list[FcaNsmDocument] = []
    for row in rows:
        source = row.get("_source") if isinstance(row, dict) else None
        if not isinstance(source, dict):
            raise FcaNsmDataError("FCA NSM response contains an invalid document.")
        company = str(source.get("company", "")).strip()
        headline = str(source.get("headline", "")).strip()
        disclosure_id = str(source.get("disclosure_id", "")).strip()
        submitted = _parse_timestamp(source.get("submitted_date"), required=True)
        if not company or not headline or not disclosure_id:
            raise FcaNsmDataError("FCA NSM document is missing identity fields.")
        link = str(source.get("download_link", "")).strip()
        documents.append(
            FcaNsmDocument(
                company_name=company,
                headline=headline,
                category=str(source.get("type", "")).strip(),
                submitted_at=submitted,
                publication_at=_parse_timestamp(source.get("publication_date")),
                disclosure_id=disclosure_id,
                document_url=(
                    f"{FCA_DOCUMENT_BASE_URL}{link.lstrip('/')}" if link else FCA_NSM_PORTAL_URL
                ),
            )
        )
    return documents


def _parse_timestamp(value: object, required: bool = False) -> datetime | None:
    raw = str(value or "").strip()
    if not raw and not required:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise FcaNsmDataError("FCA NSM document contains an invalid timestamp.") from exc


def check_lse_issues(
    issues: list[LseUpcomingIssue],
    lookup: Callable[[str], list[FcaNsmDocument]] = fetch_nsm_documents,
) -> list[LseFcaCheck]:
    return [
        LseFcaCheck(issue=issue, documents=tuple(lookup(issue.company_name)))
        for issue in issues
    ]


def load_nsm_fixture(path: str | Path) -> Callable[[str], list[FcaNsmDocument]]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FcaNsmDataError(f"Unable to read FCA NSM fixture {path}: {exc}") from exc
    responses = payload.get("responses") if isinstance(payload, dict) else None
    if not isinstance(responses, dict):
        raise FcaNsmDataError("FCA NSM fixture is missing responses.")
    normalized = {
        str(company).casefold(): parse_nsm_search_payload(response)
        for company, response in responses.items()
    }

    def lookup(company_name: str) -> list[FcaNsmDocument]:
        try:
            return normalized[company_name.casefold()]
        except KeyError as exc:
            raise FcaNsmDataError(
                f"FCA NSM fixture does not contain {company_name}."
            ) from exc

    return lookup


def render_lse_fca_report(checks: list[LseFcaCheck], as_of: date) -> str:
    found = sum(bool(check.documents) for check in checks)
    classifications = Counter(check.evidence_class for check in checks)
    lines = [
        "# LSE / FCA NSM Corroboration Monitor",
        "",
        f"- Check generated as of: `{as_of.isoformat()}`",
        f"- LSE upcoming issues checked: `{len(checks)}`",
        f"- Issuers with FCA documents found: `{found}`",
        f"- Prospectus document signals: `{classifications['prospectus_document_signal']}`",
        f"- Admission document signals: `{classifications['admission_document_signal']}`",
        f"- Intention-to-float notices: `{classifications['intention_to_float_notice']}`",
        f"- FCA NSM portal: <{FCA_NSM_PORTAL_URL}>",
        f"- FCA guidance: <{FCA_NSM_GUIDANCE_URL}>",
        "",
        "Classification uses visible FCA metadata to route document review. A document",
        "signal is not proof of completed admission, trading or an investment action.",
        "The FCA states that NSM is not real-time.",
        "",
        "## Checks",
        "",
        "| LSE Issuer | Expected Trading | Evidence Class | FCA Status | Document |",
        "|---|---|---|---|---|",
    ]
    for check in checks:
        evidence = "-"
        if check.documents:
            document = check.evidence_document
            evidence = (
                f"[{document.headline}]({document.document_url}) "
                f"({document.submitted_at.date().isoformat()})"
            )
        lines.append(
            f"| {check.issue.company_name} | {check.issue.expected_first_trading} | "
            f"`{check.evidence_class}` | `{check.status}` | {evidence} |"
        )
    return "\n".join(lines) + "\n"


def write_lse_fca_report(path: str | Path, checks: list[LseFcaCheck], as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_lse_fca_report(checks, as_of), encoding="utf-8")


def write_lse_fca_csv(path: str | Path, checks: list[LseFcaCheck]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "company_name",
        "expected_first_trading",
        "status",
        "evidence_class",
        "classification_basis",
        "document_headline",
        "document_category",
        "document_date",
        "document_url",
        "source_url",
    ]
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        for check in checks:
            document = check.evidence_document if check.documents else None
            writer.writerow(
                {
                    "company_name": check.issue.company_name,
                    "expected_first_trading": check.issue.expected_first_trading,
                    "status": check.status,
                    "evidence_class": check.evidence_class,
                    "classification_basis": (
                        document.classification_basis if document else "No FCA document found."
                    ),
                    "document_headline": document.headline if document else "",
                    "document_category": document.category if document else "",
                    "document_date": (
                        document.submitted_at.date().isoformat() if document else ""
                    ),
                    "document_url": document.document_url if document else "",
                    "source_url": FCA_NSM_PORTAL_URL,
                }
            )


def render_lse_fca_html(checks: list[LseFcaCheck], as_of: date) -> str:
    found = sum(bool(check.documents) for check in checks)
    classifications = Counter(check.evidence_class for check in checks)
    rows = "".join(
        "<tr>"
        f'<td data-label="Issuer"><div class="value"><strong>{escape(check.issue.company_name)}</strong></div></td>'
        f'<td data-label="Expected trading"><div class="value">{escape(check.issue.expected_first_trading)}</div></td>'
        f'<td data-label="Document signal"><div class="value"><span class="badge {escape(check.evidence_class)}">{escape(check.evidence_class)}</span>{_basis_html(check)}</div></td>'
        f'<td data-label="FCA state"><div class="value">{escape(check.status)}</div></td>'
        f'<td data-label="Evidence"><div class="value">{_evidence_html(check)}</div></td>'
        "</tr>"
        for check in checks
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | LSE FCA NSM Check</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1120px;margin:auto;padding:30px 28px}}
nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}h1{{font-size:clamp(34px,5vw,54px);line-height:1.06;margin:38px 0 14px}}.lead{{color:var(--muted);font-size:17px;max-width:780px}}
.cards{{display:flex;gap:16px;margin:35px 0;flex-wrap:wrap}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:190px}}.card p{{margin:0;color:var(--muted)}}.card strong{{font-size:38px;color:var(--mint);display:block}}
.notice{{border-left:3px solid var(--gold);color:var(--muted);padding:15px 18px}}h2{{margin-top:42px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{text-transform:uppercase;font-size:12px;color:var(--muted);font-weight:500}}td small{{display:block;color:var(--muted);margin-top:6px;max-width:290px}}a{{color:var(--mint);text-decoration:none}}.badge{{border-radius:999px;padding:5px 9px;font-size:12px;white-space:nowrap}}.no_document_found{{color:var(--blue);background:rgba(98,166,255,.12)}}.intention_to_float_notice{{color:var(--gold);background:rgba(240,188,98,.12)}}.prospectus_document_signal,.admission_document_signal{{color:var(--mint);background:rgba(86,218,172,.12)}}.other_document_review{{color:var(--muted);background:rgba(152,171,176,.12)}}
@media(max-width:800px){{header,main{{padding:24px 18px}}.cards{{display:block}}.card{{margin-bottom:12px}}.table-wrap{{border:0;background:transparent}}table,tbody,tr,td{{display:block;width:100%}}thead{{display:none}}tr{{background:var(--panel);border:1px solid var(--line);border-radius:14px;margin-bottom:14px;padding:8px 0}}td{{border:0;display:grid;grid-template-columns:108px minmax(0,1fr);gap:10px;padding:9px 14px}}td::before{{content:attr(data-label);color:var(--muted);font-size:11px;letter-spacing:.06em;text-transform:uppercase}}.value,td strong,td small{{min-width:0;overflow-wrap:anywhere}}.badge{{white-space:normal;overflow-wrap:anywhere}}}}
</style></head><body><header><nav>TargetAudit / Global Listings Watch / LSE / FCA NSM</nav>
<h1>London.<br>Document check.</h1><p class="lead">Upcoming LSE issues cross-checked against public FCA National Storage Mechanism documents.</p>
<p class="meta">Checked as of {escape(as_of.isoformat())}</p><section class="cards"><article class="card"><p>LSE issues checked</p><strong>{len(checks)}</strong></article><article class="card"><p>FCA matches</p><strong>{found}</strong></article><article class="card"><p>Prospectus signals</p><strong>{classifications['prospectus_document_signal']}</strong></article><article class="card"><p>Admission signals</p><strong>{classifications['admission_document_signal']}</strong></article></section></header>
<main><p class="notice">Classification is based on FCA metadata. NSM evidence is not real-time and does not by itself confirm completed admission or support an investment decision.</p>
<h2>Corroboration results</h2><div class="table-wrap"><table><thead><tr><th>LSE issuer</th><th>Expected trading</th><th>Document signal</th><th>FCA state</th><th>Document</th></tr></thead><tbody>{rows}</tbody></table></div></main></body></html>"""


def _evidence_html(check: LseFcaCheck) -> str:
    if not check.documents:
        return "-"
    document = check.evidence_document
    return (
        f'<a href="{escape(document.document_url)}">{escape(document.headline)}</a>'
        f"<small> {escape(document.submitted_at.date().isoformat())}</small>"
    )


def _basis_html(check: LseFcaCheck) -> str:
    if not check.documents:
        return "<small>No FCA document found.</small>"
    return f"<small>{escape(check.evidence_document.classification_basis)}</small>"


def write_lse_fca_html(path: str | Path, checks: list[LseFcaCheck], as_of: date) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_lse_fca_html(checks, as_of), encoding="utf-8")
