from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
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
