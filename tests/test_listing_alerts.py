import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.listing_alerts import (
    ListingSignal,
    archive_snapshot,
    compare_signals,
    latest_previous_snapshot,
    load_current_signals,
    load_snapshot_directory,
    render_alerts_html,
    render_alerts_report,
)


class ListingAlertsTests(unittest.TestCase):
    def test_compares_new_changed_and_removed_signals_without_promoting_status(self) -> None:
        previous = [
            _signal("ASX", "boresight", "Boresight Ltd", "anticipated", "June 12"),
            _signal("SGX", "3443", "KIN GLOBAL LIMITED", "prospectus_published", "April"),
            _signal("HKEX", "old", "Old Applicant", "active", "May 20"),
        ]
        current = [
            _signal("ASX", "boresight", "Boresight Ltd", "anticipated", "June 10"),
            _signal("SGX", "3443", "KIN GLOBAL LIMITED", "prospectus_published", "April"),
            _signal("SGX", "3444", "JUSTCO HOLDINGS LIMITED", "prospectus_published", "May"),
        ]

        alerts = compare_signals(current, previous)
        report = render_alerts_report(alerts, current, date(2026, 5, 24), "2026-05-23")
        page = render_alerts_html(alerts, current, date(2026, 5, 24), "2026-05-23")

        self.assertEqual(
            [alert.change_type for alert in alerts],
            ["changed", "new", "removed_from_feed_review"],
        )
        self.assertIn("not automatically a withdrawal", report)
        self.assertIn("What changed", page)
        self.assertIn("JUSTCO HOLDINGS LIMITED", page)

    def test_loads_all_previous_market_snapshots(self) -> None:
        signals = load_snapshot_directory(Path("data/samples/global-alerts-previous"))

        self.assertEqual(len(signals), 17)
        self.assertEqual({signal.market for signal in signals}, {"HKEX", "LSE", "ASX", "TSX", "JPX", "SGX"})

    def test_hkex_allows_same_issuer_at_distinct_lifecycle_events(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            current = Path(temporary)
            for source in Path("data/samples/global-alerts-previous").iterdir():
                (current / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            hkex = current / "hkex-monitor.csv"
            content = hkex.read_text(encoding="utf-8")
            content += (
                "Example Removed Applicant Limited,listed,2026-05-23,09999,false,"
                "https://www.hkexnews.hk/ncms/json/eds/applisted_sehk_e.json\n"
            )
            hkex.write_text(content, encoding="utf-8")
            signals = load_current_signals(
                {
                    "HKEX": hkex,
                    "LSE": current / "lse-upcoming.csv",
                    "ASX": current / "asx-monitor.csv",
                    "TSX": current / "tsx-monitor.csv",
                    "JPX": current / "jpx-monitor.csv",
                    "EDINET": current / "edinet-monitor.csv",
                    "SGX": current / "sgx-monitor.csv",
                }
            )

        self.assertEqual(
            len([signal for signal in signals if signal.company_name == "Example Removed Applicant Limited"]),
            2,
        )

    def test_archives_current_csvs_and_selects_latest_earlier_day(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "sources"
            source.mkdir()
            paths = {}
            for market, filename in {
                "HKEX": "hkex-monitor.csv",
                "LSE": "lse-upcoming.csv",
                "ASX": "asx-monitor.csv",
                "TSX": "tsx-monitor.csv",
                "JPX": "jpx-monitor.csv",
                "EDINET": "edinet-monitor.csv",
                "SGX": "sgx-monitor.csv",
            }.items():
                item = source / filename
                item.write_text("header\n", encoding="utf-8")
                paths[market] = item

            archive_snapshot(root / "history", paths, date(2026, 5, 22))
            archive_snapshot(root / "history", paths, date(2026, 5, 23))
            archive_snapshot(root / "history", paths, date(2026, 5, 24))

            previous = latest_previous_snapshot(root / "history", date(2026, 5, 24))

            self.assertEqual(previous.name, "2026-05-23")
            self.assertTrue((root / "history" / "2026-05-24" / "sgx-monitor.csv").exists())
            self.assertTrue((root / "history" / "2026-05-24" / "jpx-monitor.csv").exists())
            self.assertTrue((root / "history" / "2026-05-24" / "edinet-monitor.csv").exists())

    def test_edinet_tracks_documents_without_promoting_a_listing_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            edinet_csv = Path(temporary) / "edinet-monitor.csv"
            edinet_csv.write_text(
                "company_name,edinet_code,security_code,document_id,document_type_code,status,"
                "submitted_at,observed_on,source_url,document_url\n"
                "Demo Co.,E9DEMO1,0001,SYNTHJP0001,030,securities_registration_statement,"
                "2026-05-25 09:10,2026-05-25,https://example.invalid/guide,"
                "https://example.invalid/document\n",
                encoding="utf-8",
            )
            current = load_current_signals(
                {
                    "HKEX": Path("data/samples/global-alerts-previous/hkex-monitor.csv"),
                    "LSE": Path("data/samples/global-alerts-previous/lse-upcoming.csv"),
                    "ASX": Path("data/samples/global-alerts-previous/asx-monitor.csv"),
                    "TSX": Path("data/samples/global-alerts-previous/tsx-monitor.csv"),
                    "JPX": Path("data/samples/global-alerts-previous/jpx-monitor.csv"),
                    "EDINET": edinet_csv,
                    "SGX": Path("data/samples/global-alerts-previous/sgx-monitor.csv"),
                }
            )

        edinet = [signal for signal in current if signal.market == "EDINET"]
        self.assertEqual(edinet[0].entity_key, "SYNTHJP0001")
        self.assertEqual(edinet[0].status, "securities_registration_statement")
        self.assertNotIn("listed", edinet[0].status)
        alerts = compare_signals(edinet, [])
        page = render_alerts_html(alerts, edinet, date(2026, 5, 25), "baseline")
        self.assertIn("Initial registration", page)
        self.assertNotIn("securities_registration_statement", page)


def _signal(
    market: str, key: str, company: str, status: str, detail: str
) -> ListingSignal:
    return ListingSignal(market, key, company, status, detail, "https://example.invalid")


if __name__ == "__main__":
    unittest.main()
