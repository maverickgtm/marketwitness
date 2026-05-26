from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


URL_PATTERN = re.compile(r"https?://[^\s,<>\]\"'`]+")
CHECKED_SUFFIXES = {".csv", ".idx", ".json", ".md", ".py", ".toml", ".yaml", ".yml"}
SKIP_HOSTS = {"127.0.0.1", "localhost", "example.invalid"}


def tracked_paths() -> list[Path]:
    files = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
    return [
        Path(item)
        for item in files
        if Path(item).suffix.lower() in CHECKED_SUFFIXES
        and (
            item == "README.md"
            or item.startswith("docs/")
            or item.startswith(".github/")
            or item.startswith("data/samples/")
        )
    ]


def collect_urls() -> dict[str, set[str]]:
    urls: dict[str, set[str]] = {}
    for path in tracked_paths():
        for raw in URL_PATTERN.findall(path.read_text(encoding="utf-8", errors="replace")):
            url = raw.rstrip(".,;:)]}")
            urls.setdefault(url, set()).add(str(path))
    return urls


def classify(url: str) -> str:
    lowered = url.lower()
    if "/feed/" in lowered or lowered.endswith(".rss"):
        return "machine_readable_rss"
    if lowered.endswith(".json") or "/resource/" in lowered or "/api/" in lowered:
        return "machine_readable_api"
    if lowered.endswith(".xml") or "xml-feed" in lowered:
        return "machine_readable_xml"
    if lowered.endswith(".zip"):
        return "download_archive"
    return "visual_or_document_page"


def inspect(
    item: tuple[str, set[str]], identified_user_agent: str, timeout: float
) -> dict[str, str]:
    url, paths = item
    host = (urlparse(url).hostname or "").lower()
    classification = classify(url)
    if host in SKIP_HOSTS or url in {"https://...", "https://"}:
        return {
            "url": url,
            "classification": "intentional_placeholder",
            "status": "SKIP",
            "content_type": "",
            "location": "",
            "files": ";".join(sorted(paths)),
        }
    user_agent = (
        identified_user_agent
        if host.endswith("sec.gov") or host.endswith("bls.gov")
        else "MarketWitness/0.1 release-link-audit"
    )
    request = Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": (
                "text/html,application/xhtml+xml,application/json,"
                "application/xml;q=0.9,*/*;q=0.5"
            ),
            "Range": "bytes=0-1023",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return {
                "url": url,
                "classification": classification,
                "status": str(response.status),
                "content_type": response.headers.get("Content-Type", "").split(";", 1)[0],
                "location": response.geturl(),
                "files": ";".join(sorted(paths)),
            }
    except HTTPError as error:
        return {
            "url": url,
            "classification": classification,
            "status": str(error.code),
            "content_type": error.headers.get("Content-Type", "").split(";", 1)[0],
            "location": error.geturl(),
            "files": ";".join(sorted(paths)),
        }
    except (URLError, TimeoutError, OSError) as error:
        return {
            "url": url,
            "classification": classification,
            "status": f"ERROR:{type(error).__name__}",
            "content_type": "",
            "location": "",
            "files": ";".join(sorted(paths)),
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check public documentation and dashboard-registry references before "
            "a MarketWitness release."
        )
    )
    parser.add_argument(
        "--output",
        default="build/audits/public-link-audit.csv",
        help="CSV destination for the audit evidence.",
    )
    parser.add_argument("--timeout", type=float, default=8.0)
    args = parser.parse_args()
    identified_user_agent = os.environ.get("MARKETWITNESS_SEC_USER_AGENT", "")
    if "@" not in identified_user_agent:
        print(
            "Set MARKETWITNESS_SEC_USER_AGENT to an identified request header "
            "before checking SEC/BLS references.",
            file=sys.stderr,
        )
        return 2

    urls = collect_urls()
    with ThreadPoolExecutor(max_workers=12) as pool:
        rows = sorted(
            pool.map(
                lambda item: inspect(item, identified_user_agent, args.timeout),
                urls.items(),
            ),
            key=lambda row: row["url"],
        )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "url",
                "classification",
                "status",
                "content_type",
                "location",
                "files",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    totals: dict[str, int] = {}
    for row in rows:
        totals[row["status"]] = totals.get(row["status"], 0) + 1
    broken = [row for row in rows if row["status"] in {"404", "410"}]
    review = [
        row
        for row in rows
        if row["status"].startswith("ERROR") or row["status"] in {"401", "403", "429"}
    ]
    print(f"Unique URLs: {len(rows)}")
    print("Status totals:", ", ".join(f"{key}={value}" for key, value in sorted(totals.items())))
    print(f"Definite broken (404/410): {len(broken)}")
    for row in broken:
        print("BROKEN", row["status"], row["url"], row["files"])
    print(f"Blocked or timeout review URLs: {len(review)}")
    for row in review:
        print("REVIEW", row["status"], row["url"], row["files"])
    print(f"CSV report: {output}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
