import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from typing import Optional
from unittest.mock import patch

from targetaudit.providers.sec_nport import SecNportDataError
from targetaudit.providers.sec_nport_catalog import (
    SecNportDatasetRelease,
    download_dataset_release,
    fetch_dataset_catalog,
    load_dataset_catalog,
    render_catalog_report,
    select_dataset_release,
)


class SecNportCatalogProviderTests(unittest.TestCase):
    def test_reads_official_shaped_quarterly_catalog(self) -> None:
        releases = load_dataset_catalog(Path("data/samples/sec-nport-catalog.html"))
        report = render_catalog_report(releases)

        self.assertEqual([release.quarter for release in releases], ["2026q1", "2025q4", "2025q3"])
        self.assertTrue(releases[0].download_url.endswith("/2026q1_nport.zip"))
        self.assertIn("not a daily holdings feed", report)

    def test_selects_requested_published_quarter(self) -> None:
        releases = load_dataset_catalog(Path("data/samples/sec-nport-catalog.html"))

        selected = select_dataset_release(releases, "2025Q4")

        self.assertEqual(selected.quarter, "2025q4")
        with self.assertRaisesRegex(SecNportDataError, "does not publish"):
            select_dataset_release(releases, "2024q1")

    @patch("targetaudit.providers.sec_nport_catalog.urlopen")
    def test_fetch_catalog_uses_declared_sec_user_agent(self, request_mock) -> None:
        page = Path("data/samples/sec-nport-catalog.html").read_bytes()
        request_mock.return_value.__enter__.return_value = _BytesResponse(page)

        releases = fetch_dataset_catalog("TargetAudit owner@example.com")

        self.assertEqual(len(releases), 3)
        request = request_mock.call_args.args[0]
        self.assertEqual(request.headers["User-agent"], "TargetAudit owner@example.com")

    @patch("targetaudit.providers.sec_nport_catalog.urlopen")
    def test_downloads_and_extracts_selected_dataset_locally(self, request_mock) -> None:
        request_mock.return_value.__enter__.return_value = _BytesResponse(_zip_bytes())
        release = SecNportDatasetRelease(
            "2026q1",
            "https://www.sec.gov/files/dera/data/form-n-port-data-sets/2026q1_nport.zip",
        )
        with tempfile.TemporaryDirectory() as temporary:
            downloaded = download_dataset_release(
                release, temporary, "TargetAudit owner@example.com"
            )
            extracted = {path.name for path in downloaded.extracted_dir.iterdir()}
            report = render_catalog_report([release], downloaded)

        self.assertIn("SUBMISSION.tsv", extracted)
        self.assertIn("IDENTIFIERS.tsv", extracted)
        self.assertNotIn("UNUSED_TABLE.tsv", extracted)
        self.assertIn("Downloaded Locally", report)
        request = request_mock.call_args.args[0]
        self.assertEqual(request.headers["User-agent"], "TargetAudit owner@example.com")

    @patch("targetaudit.providers.sec_nport_catalog.urlopen")
    def test_rejects_zip_with_unsafe_path(self, request_mock) -> None:
        request_mock.return_value.__enter__.return_value = _BytesResponse(
            _zip_bytes(extra_name="../escape.tsv")
        )
        release = SecNportDatasetRelease(
            "2026q1",
            "https://www.sec.gov/files/dera/data/form-n-port-data-sets/2026q1_nport.zip",
        )
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(SecNportDataError, "unsafe path"):
                download_dataset_release(
                    release, temporary, "TargetAudit owner@example.com"
                )
            archives = list(Path(temporary).rglob("*.zip"))

        self.assertEqual(archives, [])

def _zip_bytes(extra_name: Optional[str] = None) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name in [
            "SUBMISSION.tsv",
            "REGISTRANT.tsv",
            "FUND_REPORTED_INFO.tsv",
            "FUND_REPORTED_HOLDING.tsv",
            "IDENTIFIERS.tsv",
        ]:
            archive.writestr(name, "field\n")
        archive.writestr("UNUSED_TABLE.tsv", "ignored\n")
        if extra_name is not None:
            archive.writestr(extra_name, "invalid\n")
    return buffer.getvalue()


class _BytesResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *unused):
        self.close()


if __name__ == "__main__":
    unittest.main()
