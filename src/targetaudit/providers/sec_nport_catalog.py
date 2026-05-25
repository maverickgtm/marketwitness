from __future__ import annotations

import csv
import re
import shutil
import zipfile
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from .sec import configured_user_agent
from .sec_nport import SEC_NPORT_DATASETS_URL, SecNportDataError

_ZIP_PATTERN = re.compile(r"(?P<quarter>\d{4}q[1-4])_nport\.zip$", re.IGNORECASE)
_REQUIRED_TABLES = {
    "SUBMISSION.TSV": "SUBMISSION.tsv",
    "REGISTRANT.TSV": "REGISTRANT.tsv",
    "FUND_REPORTED_INFO.TSV": "FUND_REPORTED_INFO.tsv",
    "FUND_REPORTED_HOLDING.TSV": "FUND_REPORTED_HOLDING.tsv",
    "IDENTIFIERS.TSV": "IDENTIFIERS.tsv",
}


@dataclass(frozen=True)
class SecNportDatasetRelease:
    quarter: str
    download_url: str


@dataclass(frozen=True)
class SecNportDownloadedDataset:
    release: SecNportDatasetRelease
    archive_path: Path
    extracted_dir: Path


def fetch_dataset_catalog(user_agent: str | None = None) -> list[SecNportDatasetRelease]:
    request = Request(
        SEC_NPORT_DATASETS_URL,
        headers={
            "User-Agent": configured_user_agent(user_agent),
            "Accept": "text/html",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            page = response.read().decode("utf-8")
    except (URLError, TimeoutError, OSError, UnicodeDecodeError) as exc:
        raise SecNportDataError(f"Unable to retrieve SEC N-PORT catalog: {exc}") from exc
    return parse_dataset_catalog(page)


def load_dataset_catalog(path: str | Path) -> list[SecNportDatasetRelease]:
    try:
        page = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise SecNportDataError(f"Unable to read SEC N-PORT catalog snapshot: {exc}") from exc
    return parse_dataset_catalog(page)


def parse_dataset_catalog(page: str) -> list[SecNportDatasetRelease]:
    parser = _CatalogLinkParser()
    parser.feed(page)
    releases = {}
    for href in parser.hrefs:
        match = _ZIP_PATTERN.search(href)
        if not match:
            continue
        quarter = match.group("quarter").lower()
        download_url = urljoin(SEC_NPORT_DATASETS_URL, href)
        existing = releases.get(quarter)
        if existing is not None and existing.download_url != download_url:
            raise SecNportDataError(f"SEC N-PORT catalog duplicates release {quarter}.")
        releases[quarter] = SecNportDatasetRelease(
            quarter=quarter,
            download_url=download_url,
        )
    if not releases:
        raise SecNportDataError("SEC N-PORT catalog contains no quarterly ZIP links.")
    return sorted(releases.values(), key=lambda release: release.quarter, reverse=True)


def select_dataset_release(
    releases: list[SecNportDatasetRelease], quarter: str
) -> SecNportDatasetRelease:
    requested = quarter.strip().lower()
    if not re.fullmatch(r"\d{4}q[1-4]", requested):
        raise SecNportDataError(f"Invalid SEC N-PORT quarter: {quarter!r}.")
    for release in releases:
        if release.quarter == requested:
            return release
    raise SecNportDataError(f"SEC N-PORT catalog does not publish quarter {requested}.")


def download_dataset_release(
    release: SecNportDatasetRelease,
    storage_dir: str | Path,
    user_agent: str | None = None,
    force: bool = False,
) -> SecNportDownloadedDataset:
    root = Path(storage_dir) / release.quarter
    filename = Path(release.download_url).name
    archive = root / filename
    temporary_archive = archive.with_suffix(archive.suffix + ".part")
    extracted = root / "extracted"
    if (archive.exists() or extracted.exists()) and not force:
        raise SecNportDataError(
            f"SEC N-PORT dataset {release.quarter} already exists; use --force to replace it."
        )
    request = Request(
        release.download_url,
        headers={
            "User-Agent": configured_user_agent(user_agent),
            "Accept": "application/zip",
        },
    )
    root.mkdir(parents=True, exist_ok=True)
    temporary_archive.unlink(missing_ok=True)
    try:
        with urlopen(request, timeout=120) as response, temporary_archive.open("wb") as target:
            shutil.copyfileobj(response, target)
        _extract_dataset_archive(temporary_archive, extracted, force)
        temporary_archive.replace(archive)
    except SecNportDataError:
        temporary_archive.unlink(missing_ok=True)
        raise
    except (URLError, TimeoutError, OSError, zipfile.BadZipFile) as exc:
        temporary_archive.unlink(missing_ok=True)
        raise SecNportDataError(
            f"Unable to download/extract SEC N-PORT dataset {release.quarter}: {exc}"
        ) from exc
    return SecNportDownloadedDataset(
        release=release,
        archive_path=archive,
        extracted_dir=extracted,
    )


def write_catalog_csv(path: str | Path, releases: list[SecNportDatasetRelease]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=["quarter", "download_url"])
        writer.writeheader()
        for release in releases:
            writer.writerow(
                {"quarter": release.quarter, "download_url": release.download_url}
            )


def render_catalog_report(
    releases: list[SecNportDatasetRelease],
    downloaded: SecNportDownloadedDataset | None = None,
) -> str:
    lines = [
        "# SEC N-PORT Quarterly Data Sets",
        "",
        f"- Published releases detected: `{len(releases)}`",
        f"- Catalog source: <{SEC_NPORT_DATASETS_URL}>",
        "- Intended use: `regulatory_periodic` historical backfill",
        "",
        "The SEC publishes quarterly ZIP data sets derived from disseminated",
        "Form N-PORT filings. These files are not a daily holdings feed.",
        "",
        "## Releases",
        "",
        "| Quarter | ZIP Source |",
        "|---|---|",
    ]
    for release in releases:
        lines.append(f"| `{release.quarter}` | [Download ZIP]({release.download_url}) |")
    if downloaded is not None:
        lines.extend(
            [
                "",
                "## Downloaded Locally",
                "",
                f"- Quarter: `{downloaded.release.quarter}`",
                f"- ZIP path: `{downloaded.archive_path}`",
                f"- Extracted tables: `{downloaded.extracted_dir}`",
                "",
                "Downloaded files remain local evidence under `data/raw/` and are not",
                "intended to be committed to the public repository.",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def write_catalog_report(
    path: str | Path,
    releases: list[SecNportDatasetRelease],
    downloaded: SecNportDownloadedDataset | None = None,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_catalog_report(releases, downloaded), encoding="utf-8")


def render_catalog_html(
    releases: list[SecNportDatasetRelease],
    downloaded: SecNportDownloadedDataset | None = None,
) -> str:
    rows = "".join(
        "<tr>"
        f"<td><strong>{escape(release.quarter.upper())}</strong></td>"
        f'<td><a href="{escape(release.download_url)}">Official ZIP</a></td>'
        "<td>regulatory_periodic</td>"
        "</tr>"
        for release in releases
    )
    local_note = ""
    if downloaded is not None:
        local_note = (
            '<p class="notice local"><strong>Downloaded locally:</strong> '
            f"{escape(downloaded.release.quarter.upper())} was extracted for local "
            "backfill evidence. Local file paths are intentionally not published.</p>"
        )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TargetAudit | SEC N-PORT Dataset Catalog</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1120px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}a{{color:var(--mint);text-decoration:none}}h1{{font-size:clamp(36px,5vw,56px);line-height:1.06;margin:38px 0 14px}}h2{{margin-top:42px}}.lead{{color:var(--muted);font-size:17px;max-width:840px}}.cards{{display:flex;gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px;min-width:250px}}.card p{{margin:0;color:var(--muted)}}.card strong{{display:block;color:var(--mint);font-size:38px}}.notice{{padding:15px 18px;border-left:3px solid var(--gold);color:var(--muted)}}.local{{margin-top:16px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left}}th{{color:var(--muted);font-size:12px;text-transform:uppercase;font-weight:500}}@media(max-width:760px){{.cards{{display:block}}.card{{margin-bottom:12px}}}}
</style></head><body><header><nav><a href="/dashboard/reports">Report Center</a> / <a href="/dashboard/etf">ETF Evidence Center</a> / SEC N-PORT Catalog</nav>
<h1>Quarterly holdings.<br>Official catalog.</h1>
<p class="lead">Published SEC Form N-PORT ZIP releases available for historical regulatory backfill of fund positions.</p>
<section class="cards"><article class="card"><p>Published releases detected</p><strong>{len(releases)}</strong></article><article class="card"><p>Evidence frequency</p><strong>Quarterly</strong></article></section></header>
<main><p class="notice">N-PORT data sets are periodic regulatory evidence. They are not daily portfolio updates, confirmed manager trades or real-time market signals.</p>{local_note}
<h2>Available Data Sets</h2><div class="table-wrap"><table><thead><tr><th>Quarter</th><th>SEC source</th><th>Layer</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="meta">Source: <a href="{escape(SEC_NPORT_DATASETS_URL)}">SEC Form N-PORT Data Sets</a></p></main></body></html>"""


def write_catalog_html(
    path: str | Path,
    releases: list[SecNportDatasetRelease],
    downloaded: SecNportDownloadedDataset | None = None,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_catalog_html(releases, downloaded), encoding="utf-8")


def _extract_dataset_archive(archive: Path, extracted: Path, force: bool) -> None:
    with zipfile.ZipFile(archive) as source:
        selected_members = {}
        for info in source.infolist():
            member = Path(info.filename)
            if member.is_absolute() or ".." in member.parts:
                raise SecNportDataError("SEC N-PORT ZIP contains an unsafe path.")
            if info.is_dir():
                continue
            canonical = _REQUIRED_TABLES.get(member.name.upper())
            if canonical is not None:
                selected_members[canonical] = info
        if set(selected_members) != set(_REQUIRED_TABLES.values()):
            raise SecNportDataError("SEC N-PORT ZIP is missing tables required for backfill.")
        if extracted.exists() and force:
            shutil.rmtree(extracted)
        extracted.mkdir(parents=True, exist_ok=True)
        for canonical, info in selected_members.items():
            target = extracted / canonical
            with source.open(info) as raw, target.open("wb") as output:
                shutil.copyfileobj(raw, output)


class _CatalogLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attributes = dict(attrs)
        href = attributes.get("href")
        if href:
            self.hrefs.append(href)
