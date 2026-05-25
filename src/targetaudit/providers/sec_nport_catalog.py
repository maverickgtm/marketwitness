from __future__ import annotations

import csv
import re
import shutil
import zipfile
from dataclasses import dataclass
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
