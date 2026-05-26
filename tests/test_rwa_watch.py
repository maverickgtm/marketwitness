import tempfile
import unittest
from datetime import date
from pathlib import Path

from marketwitness.rwa_watch import (
    RwaWatchDataError,
    build_rwa_snapshot,
    load_rwa_observations,
    render_rwa_html,
    render_rwa_report,
)


class RwaWatchTests(unittest.TestCase):
    def test_renders_synthetic_issuer_first_monitor_without_live_claims(self) -> None:
        observations = load_rwa_observations(
            Path("data/samples/rwa-watch-synthetic.csv"), date(2026, 5, 24)
        )
        snapshot = build_rwa_snapshot(observations, date(2026, 5, 24))
        report = render_rwa_report(snapshot)
        page = render_rwa_html(snapshot)

        self.assertEqual(snapshot["observation_count"], 4)
        self.assertEqual(snapshot["network_count"], 3)
        self.assertEqual(snapshot["venue_count"], 3)
        self.assertEqual(snapshot["flagged_count"], 2)
        self.assertIn("project-authored synthetic data only", report)
        self.assertIn("RWA Watch Sandbox", page)
        self.assertIn("Synthetic data only", page)
        self.assertIn("live ingestion remains blocked", page)
        self.assertNotIn("recommend buying", page.lower())

    def test_rejects_real_or_unapproved_rwa_layer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "live.csv"
            content = Path("data/samples/rwa-watch-synthetic.csv").read_text(
                encoding="utf-8"
            )
            path.write_text(
                content.replace("synthetic_demo", "public_endpoint", 1),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RwaWatchDataError, "rejects non-synthetic"):
                load_rwa_observations(path, date(2026, 5, 24))

    def test_rejects_future_observation(self) -> None:
        with self.assertRaisesRegex(RwaWatchDataError, "exceeds evidence cutoff"):
            load_rwa_observations(
                Path("data/samples/rwa-watch-synthetic.csv"), date(2026, 5, 22)
            )


if __name__ == "__main__":
    unittest.main()
