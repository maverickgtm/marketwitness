import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.providers.sec_nport_catalog import (
    SecNportDatasetRelease,
    SecNportDownloadedDataset,
)
from targetaudit.providers.sec_nport import SecNportDataError
from targetaudit.providers.sec_nport_dataset import REQUIRED_TABLES
from targetaudit.providers.sec_nport_sync import (
    render_sync_html,
    render_sync_report,
    sync_dataset_releases,
)


class SecNportSyncProviderTests(unittest.TestCase):
    def test_initializes_catalog_baseline_without_downloading_history(self) -> None:
        called = []
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sync = sync_dataset_releases(
                _releases("2026q1", "2025q4"),
                root / "state.csv",
                root / "datasets",
                date(2026, 5, 24),
                downloader=lambda *args: called.append(args),
            )
            state = (root / "state.csv").read_text(encoding="utf-8")
            report = render_sync_report(sync, root / "state.csv")
            page = render_sync_html(sync)

        self.assertTrue(sync.initialized_baseline)
        self.assertEqual(called, [])
        self.assertEqual(sync.downloaded, ())
        self.assertIn("baseline_not_downloaded", state)
        self.assertIn("initialized the baseline without automatically downloading", report)
        self.assertIn("New quarters.", page)
        self.assertIn("not daily ETF portfolio activity", page)
        self.assertIn("baseline_not_downloaded", page)
        self.assertIn('href="/dashboard/etf">ETF Evidence Center</a>', page)

    def test_downloads_only_release_first_observed_after_baseline(self) -> None:
        downloads = []
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / "state.csv"
            storage = root / "datasets"
            sync_dataset_releases(
                _releases("2025q4"),
                state,
                storage,
                date(2026, 4, 1),
                downloader=_unexpected_download,
            )

            def downloader(release, target, user_agent, force):
                downloads.append(release.quarter)
                return _create_local_dataset(release, Path(target))

            sync = sync_dataset_releases(
                _releases("2026q1", "2025q4"),
                state,
                storage,
                date(2026, 5, 24),
                downloader=downloader,
            )
            report = render_sync_report(sync, state)

        self.assertFalse(sync.initialized_baseline)
        self.assertEqual(downloads, ["2026q1"])
        self.assertEqual(sync.newly_published, ("2026q1",))
        self.assertEqual(len(sync.available_dirs), 1)
        self.assertIn("downloaded_new_release", report)

    def test_recognizes_already_downloaded_dataset_during_initialization(self) -> None:
        release = _releases("2026q1")[0]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _create_local_dataset(release, root / "datasets")
            sync = sync_dataset_releases(
                [release],
                root / "state.csv",
                root / "datasets",
                date(2026, 5, 24),
                downloader=_unexpected_download,
            )

        self.assertEqual(sync.entries[0].status, "available_local")
        self.assertEqual(len(sync.available_dirs), 1)

    def test_rejects_unknown_status_in_persistent_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "state.csv").write_text(
                "quarter,download_url,first_seen_on,last_seen_on,status,archive_path,extracted_dir\n"
                "2025q4,https://www.sec.gov/example.zip,2026-04-01,2026-04-01,untrusted,,\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(SecNportDataError, "unknown status"):
                sync_dataset_releases(
                    _releases("2025q4"),
                    root / "state.csv",
                    root / "datasets",
                    date(2026, 5, 24),
                    downloader=_unexpected_download,
                )


def _releases(*quarters):
    return [
        SecNportDatasetRelease(
            quarter,
            f"https://www.sec.gov/files/dera/data/form-n-port-data-sets/{quarter}_nport.zip",
        )
        for quarter in quarters
    ]


def _unexpected_download(*args):
    raise AssertionError("No download was expected.")


def _create_local_dataset(
    release: SecNportDatasetRelease, storage: Path
) -> SecNportDownloadedDataset:
    root = storage / release.quarter
    archive = root / f"{release.quarter}_nport.zip"
    extracted = root / "extracted"
    extracted.mkdir(parents=True)
    archive.write_bytes(b"fixture archive")
    for filename in REQUIRED_TABLES:
        (extracted / filename).write_text("fixture\n", encoding="utf-8")
    return SecNportDownloadedDataset(release, archive, extracted)


if __name__ == "__main__":
    unittest.main()
