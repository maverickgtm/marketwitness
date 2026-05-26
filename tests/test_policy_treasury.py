import unittest
from datetime import date
from pathlib import Path

from marketwitness.policy_treasury import build_policy_treasury_context
from marketwitness.providers.treasury import load_treasury_snapshot
from marketwitness.providers.whitehouse import load_whitehouse_snapshots


class PolicyTreasuryTests(unittest.TestCase):
    def test_matches_themed_event_to_observed_session_pair_without_causal_claim(self) -> None:
        events = load_whitehouse_snapshots(
            Path("data/samples/whitehouse-news-rss-synthetic.xml"),
            Path("data/samples/whitehouse-actions-rss-synthetic.xml"),
            date(2026, 5, 25),
        )
        yields = load_treasury_snapshot(
            Path("data/samples/treasury-yields-synthetic.xml"), date(2026, 5, 25)
        )

        snapshot = build_policy_treasury_context(events, yields)

        self.assertEqual(snapshot["data_mode"], "Synthetic reproducible Treasury fixture")
        self.assertEqual(snapshot["latest_rate_date"], "2026-05-25")
        self.assertEqual(snapshot["measured_event_count"], 1)
        self.assertEqual(snapshot["pending_event_count"], 2)
        record = next(item for item in snapshot["records"] if "Sanctions" in item["title"])
        self.assertIn("Sanctions", record["title"])
        self.assertEqual(record["reference_date"], "2026-05-22")
        self.assertEqual(record["following_date"], "2026-05-25")
        self.assertEqual(record["two_year_change_bps"], "-6.00")
        self.assertIn("after publication", snapshot["measurement"])
        self.assertIn("do not prove", snapshot["publication_boundary"])


if __name__ == "__main__":
    unittest.main()
