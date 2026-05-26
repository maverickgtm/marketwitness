from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from typing import Callable, Optional

from .sec_nport import SEC_NPORT_DATASETS_URL, SecNportDataError
from .sec_nport_catalog import (
    SecNportDatasetRelease,
    SecNportDownloadedDataset,
    download_dataset_release,
)
from .sec_nport_dataset import REQUIRED_TABLES

_STATE_FIELDS = [
    "quarter",
    "download_url",
    "first_seen_on",
    "last_seen_on",
    "status",
    "archive_path",
    "extracted_dir",
]
_BASELINE_STATUS = "baseline_not_downloaded"
_LOCAL_STATUS = "available_local"
_NEW_STATUS = "downloaded_new_release"
_STATUSES = {_BASELINE_STATUS, _LOCAL_STATUS, _NEW_STATUS}


@dataclass(frozen=True)
class SecNportSyncEntry:
    quarter: str
    download_url: str
    first_seen_on: date
    last_seen_on: date
    status: str
    archive_path: str
    extracted_dir: str


@dataclass(frozen=True)
class SecNportSyncRun:
    observed_on: date
    initialized_baseline: bool
    entries: tuple[SecNportSyncEntry, ...]
    newly_published: tuple[str, ...]
    downloaded: tuple[SecNportDownloadedDataset, ...]
    available_dirs: tuple[Path, ...]


def sync_dataset_releases(
    releases: list[SecNportDatasetRelease],
    state_path: str | Path,
    storage_dir: str | Path,
    observed_on: date,
    user_agent: Optional[str] = None,
    downloader: Callable[
        [SecNportDatasetRelease, str | Path, Optional[str], bool],
        SecNportDownloadedDataset,
    ] = download_dataset_release,
) -> SecNportSyncRun:
    state = Path(state_path)
    existing = _load_state(state)
    initialized_baseline = not state.exists()
    storage = Path(storage_dir)
    entries: dict[str, SecNportSyncEntry] = dict(existing)
    newly_published = []
    downloaded = []

    for release in releases:
        prior = existing.get(release.quarter)
        local = _available_local_dataset(release, storage)
        if prior is None:
            if initialized_baseline and local is None:
                entry = _entry(release, observed_on, observed_on, _BASELINE_STATUS)
            elif local is not None:
                entry = _local_entry(release, observed_on, observed_on, local, _LOCAL_STATUS)
                if not initialized_baseline:
                    newly_published.append(release.quarter)
            else:
                newly_published.append(release.quarter)
                local = downloader(release, storage, user_agent, False)
                downloaded.append(local)
                entry = _local_entry(release, observed_on, observed_on, local, _NEW_STATUS)
        elif local is not None and prior.status == _BASELINE_STATUS:
            entry = _local_entry(
                release, prior.first_seen_on, observed_on, local, _LOCAL_STATUS
            )
        else:
            entry = SecNportSyncEntry(
                quarter=prior.quarter,
                download_url=release.download_url,
                first_seen_on=prior.first_seen_on,
                last_seen_on=observed_on,
                status=prior.status,
                archive_path=prior.archive_path,
                extracted_dir=prior.extracted_dir,
            )
        entries[release.quarter] = entry

    ordered = tuple(sorted(entries.values(), key=lambda entry: entry.quarter, reverse=True))
    _write_state(state, ordered)
    available_dirs = tuple(
        Path(entry.extracted_dir)
        for entry in ordered
        if entry.extracted_dir and _has_required_tables(Path(entry.extracted_dir))
    )
    return SecNportSyncRun(
        observed_on=observed_on,
        initialized_baseline=initialized_baseline,
        entries=ordered,
        newly_published=tuple(newly_published),
        downloaded=tuple(downloaded),
        available_dirs=available_dirs,
    )


def render_sync_report(sync: SecNportSyncRun, state_path: str | Path) -> str:
    lines = [
        "# SEC N-PORT Incremental Synchronization",
        "",
        f"- Checked on: `{sync.observed_on.isoformat()}`",
        f"- Catalog source: <{SEC_NPORT_DATASETS_URL}>",
        f"- Releases tracked in local state: `{len(sync.entries)}`",
        f"- New releases in this run: `{len(sync.newly_published)}`",
        f"- ZIPs downloaded in this run: `{len(sync.downloaded)}`",
        f"- Locally usable extracted quarters: `{len(sync.available_dirs)}`",
        f"- Local state: `{state_path}`",
        "",
        "This synchronization tracks quarterly regulatory evidence, not real-time",
        "ETF trading activity. Only a quarter newly observed after initialization",
        "is downloaded automatically; historical backfill remains an explicit task.",
    ]
    if sync.initialized_baseline:
        lines.extend(
            [
                "",
                "This run initialized the baseline without automatically downloading",
                "older releases already present in the SEC catalog.",
            ]
        )
    lines.extend(
        [
            "",
            "## Releases",
            "",
            "| Quarter | Status | First Seen | Last Seen |",
            "|---|---|---|---|",
        ]
    )
    for entry in sync.entries:
        lines.append(
            f"| `{entry.quarter}` | `{entry.status}` | "
            f"{entry.first_seen_on.isoformat()} | {entry.last_seen_on.isoformat()} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_sync_report(path: str | Path, sync: SecNportSyncRun, state_path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_sync_report(sync, state_path), encoding="utf-8")


def render_sync_html(sync: SecNportSyncRun) -> str:
    rows = "".join(
        "<tr>"
        f"<td><strong>{escape(entry.quarter.upper())}</strong></td>"
        f'<td><span class="pill {escape(entry.status)}">{escape(entry.status)}</span></td>'
        f"<td>{escape(entry.first_seen_on.isoformat())}</td>"
        f"<td>{escape(entry.last_seen_on.isoformat())}</td>"
        "</tr>"
        for entry in sync.entries
    )
    baseline_note = (
        "<p class=\"notice\">This run initialized a local baseline without "
        "automatically downloading historical releases already present in the SEC catalog.</p>"
        if sync.initialized_baseline
        else ""
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarketWitness | SEC N-PORT Sync Status</title><style>
:root{{--bg:#071016;--panel:#0f1c24;--line:#20343d;--text:#edf1ef;--muted:#98abb0;--mint:#56daac;--gold:#f0bc62;--blue:#62a6ff;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Arial,sans-serif}}header,main{{max-width:1140px;margin:auto;padding:30px 28px}}nav,.meta{{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:13px}}a{{color:var(--mint);text-decoration:none}}h1{{font-size:clamp(36px,5vw,56px);line-height:1.06;margin:38px 0 14px}}h2{{margin-top:42px}}.lead{{color:var(--muted);font-size:17px;max-width:860px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:35px 0}}.card,.notice,.table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:14px}}.card{{padding:18px 20px}}.card p{{margin:0;color:var(--muted)}}.card strong{{display:block;color:var(--mint);font-size:36px}}.notice{{padding:15px 18px;border-left:3px solid var(--gold);color:var(--muted);margin-bottom:16px}}.table-wrap{{overflow:hidden;margin-top:16px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left}}th{{color:var(--muted);font-size:12px;text-transform:uppercase;font-weight:500}}.pill{{display:inline-block;border-radius:999px;padding:5px 9px;font-size:12px}}.baseline_not_downloaded{{color:var(--blue);background:rgba(98,166,255,.12)}}.available_local,.downloaded_new_release{{color:var(--mint);background:rgba(86,218,172,.12)}}@media(max-width:850px){{.cards{{grid-template-columns:repeat(2,1fr)}}.table-wrap{{overflow-x:auto}}table{{min-width:660px}}}}
</style></head><body><header><nav><a href="/dashboard/reports">Report Center</a> / <a href="/dashboard/etf">ETF Evidence Center</a> / SEC N-PORT Sync</nav>
<h1>New quarters.<br>Controlled downloads.</h1>
<p class="lead">Incremental state for SEC N-PORT quarterly releases: establish a baseline, then acquire only newly observed publications for local backfill.</p>
<p class="meta">Observed on {escape(sync.observed_on.isoformat())}</p>
<section class="cards"><article class="card"><p>Tracked releases</p><strong>{len(sync.entries)}</strong></article><article class="card"><p>New this run</p><strong>{len(sync.newly_published)}</strong></article><article class="card"><p>Downloaded</p><strong>{len(sync.downloaded)}</strong></article><article class="card"><p>Locally usable</p><strong>{len(sync.available_dirs)}</strong></article></section></header>
<main><p class="notice">This monitor tracks quarterly regulatory evidence, not daily ETF portfolio activity or trading instructions. Downloads remain local evidence outside the published dataset.</p>{baseline_note}
<h2>Tracked Releases</h2><div class="table-wrap"><table><thead><tr><th>Quarter</th><th>Status</th><th>First seen</th><th>Last seen</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="meta">Source: <a href="{escape(SEC_NPORT_DATASETS_URL)}">SEC Form N-PORT Data Sets</a></p></main></body></html>"""


def write_sync_html(path: str | Path, sync: SecNportSyncRun) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_sync_html(sync), encoding="utf-8")


def _load_state(path: Path) -> dict[str, SecNportSyncEntry]:
    if not path.exists():
        return {}
    try:
        with path.open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)
            if reader.fieldnames != _STATE_FIELDS:
                raise SecNportDataError("SEC N-PORT sync state has unexpected columns.")
            entries = {}
            for row in reader:
                quarter = row["quarter"].strip().lower()
                if quarter in entries:
                    raise SecNportDataError("SEC N-PORT sync state duplicates a quarter.")
                entry = SecNportSyncEntry(
                    quarter=quarter,
                    download_url=row["download_url"],
                    first_seen_on=date.fromisoformat(row["first_seen_on"]),
                    last_seen_on=date.fromisoformat(row["last_seen_on"]),
                    status=row["status"],
                    archive_path=row["archive_path"],
                    extracted_dir=row["extracted_dir"],
                )
                if not re.fullmatch(r"\d{4}q[1-4]", entry.quarter):
                    raise SecNportDataError("SEC N-PORT sync state has an invalid quarter.")
                if not entry.download_url.startswith("https://"):
                    raise SecNportDataError("SEC N-PORT sync state has an invalid download URL.")
                if entry.status not in _STATUSES:
                    raise SecNportDataError("SEC N-PORT sync state has an unknown status.")
                if entry.first_seen_on > entry.last_seen_on:
                    raise SecNportDataError("SEC N-PORT sync state has invalid observation dates.")
                entries[quarter] = entry
    except (OSError, ValueError) as exc:
        raise SecNportDataError(f"Unable to read SEC N-PORT sync state: {exc}") from exc
    return entries


def _write_state(path: Path, entries: tuple[SecNportSyncEntry, ...]) -> None:
    temporary = path.with_suffix(path.suffix + ".part")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary.open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(target, fieldnames=_STATE_FIELDS)
            writer.writeheader()
            for entry in entries:
                writer.writerow(
                    {
                        "quarter": entry.quarter,
                        "download_url": entry.download_url,
                        "first_seen_on": entry.first_seen_on.isoformat(),
                        "last_seen_on": entry.last_seen_on.isoformat(),
                        "status": entry.status,
                        "archive_path": entry.archive_path,
                        "extracted_dir": entry.extracted_dir,
                    }
                )
        temporary.replace(path)
    except OSError as exc:
        temporary.unlink(missing_ok=True)
        raise SecNportDataError(f"Unable to write SEC N-PORT sync state: {exc}") from exc


def _entry(
    release: SecNportDatasetRelease, first_seen: date, last_seen: date, status: str
) -> SecNportSyncEntry:
    return SecNportSyncEntry(
        quarter=release.quarter,
        download_url=release.download_url,
        first_seen_on=first_seen,
        last_seen_on=last_seen,
        status=status,
        archive_path="",
        extracted_dir="",
    )


def _local_entry(
    release: SecNportDatasetRelease,
    first_seen: date,
    last_seen: date,
    downloaded: SecNportDownloadedDataset,
    status: str,
) -> SecNportSyncEntry:
    return SecNportSyncEntry(
        quarter=release.quarter,
        download_url=release.download_url,
        first_seen_on=first_seen,
        last_seen_on=last_seen,
        status=status,
        archive_path=str(downloaded.archive_path),
        extracted_dir=str(downloaded.extracted_dir),
    )


def _available_local_dataset(
    release: SecNportDatasetRelease, storage_dir: Path
) -> Optional[SecNportDownloadedDataset]:
    root = storage_dir / release.quarter
    archive = root / Path(release.download_url).name
    extracted = root / "extracted"
    if archive.exists() and _has_required_tables(extracted):
        return SecNportDownloadedDataset(release, archive, extracted)
    return None


def _has_required_tables(directory: Path) -> bool:
    return directory.exists() and all(
        (directory / filename).exists() for filename in REQUIRED_TABLES
    )
