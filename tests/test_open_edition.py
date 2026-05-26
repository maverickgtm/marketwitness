import unittest
from datetime import date
from pathlib import Path

from marketwitness.open_edition import (
    build_open_edition_snapshot,
    render_open_edition_html,
    render_open_edition_report,
)
from marketwitness.source_registry import SourceProvider, SourceRegistryDataError, load_source_registry


class OpenEditionTests(unittest.TestCase):
    def test_exposes_a_useful_no_paid_subscription_product(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))

        snapshot = build_open_edition_snapshot(providers, date(2026, 5, 25))

        self.assertEqual(snapshot["zero_cost_available_count"], 7)
        self.assertEqual(snapshot["offline_ready_count"], 2)
        self.assertEqual(snapshot["public_data_ready_count"], 4)
        self.assertEqual(snapshot["attributed_widget_count"], 1)
        self.assertEqual(snapshot["optional_extension_count"], 1)
        rankings = next(
            item for item in snapshot["capabilities"] if item["key"] == "real_analyst_rankings"
        )
        self.assertEqual(rankings["status"], "bring_authorized_data")
        self.assertEqual(rankings["route"], "/dashboard/extensions")
        self.assertIn("no licensed target dataset", rankings["limitation"])
        page = render_open_edition_html(snapshot)
        report = render_open_edition_report(snapshot)
        self.assertIn("No paid data required", page)
        self.assertIn('href="/dashboard/financials">Open view</a>', page)
        self.assertIn('href="/dashboard/ipo-watch">Open view</a>', page)
        self.assertIn('href="/dashboard/etf-regulatory">Open view</a>', page)
        self.assertIn('href="/dashboard/extensions">Open view</a>', page)
        self.assertIn("[Open view](/dashboard/rwa-watch)", report)
        rwa = next(
            item for item in snapshot["capabilities"] if item["key"] == "rwa_watch_sandbox"
        )
        self.assertEqual(rwa["route"], "/dashboard/rwa-watch")
        self.assertIn("No live token data", rwa["limitation"])
        context = next(
            item for item in snapshot["capabilities"] if item["key"] == "market_context_widget"
        )
        self.assertEqual(context["route"], "/dashboard/market-context")
        self.assertEqual(context["status"], "attributed_external_widget")
        self.assertEqual(context["title"], "Cross-Asset Markets")
        self.assertIn("crypto", context["output"])
        self.assertIn("not stored", context["limitation"])
        self.assertIn("Available without paid data subscriptions: `7`", report)
        events = next(
            item for item in snapshot["capabilities"] if item["key"] == "presidential_event_intake"
        )
        self.assertEqual(events["status"], "public_source_no_key")
        self.assertEqual(events["route"], "/dashboard/presidential-impact")

    def test_rejects_a_public_capability_if_its_free_source_becomes_unavailable(self) -> None:
        providers = load_source_registry(Path("data/samples/source_registry.csv"))
        sec = next(item for item in providers if item.provider_id == "sec-edgar")
        blocked_sec = SourceProvider(
            **{
                **sec.__dict__,
                "license_status": "terms_review_required",
                "publication_policy": "derived_output_pending_terms_review",
            }
        )
        modified = [
            blocked_sec if item.provider_id == "sec-edgar" else item for item in providers
        ]

        with self.assertRaisesRegex(SourceRegistryDataError, "unavailable source"):
            build_open_edition_snapshot(modified, date(2026, 5, 25))


if __name__ == "__main__":
    unittest.main()
