import tempfile
import unittest
from datetime import date
from pathlib import Path

from marketwitness.providers.whitehouse import (
    WhiteHouseDataError,
    classify_title,
    load_event_archive,
    load_whitehouse_snapshots,
    merge_event_archive,
    render_events_html,
    render_events_report,
    write_events_csv,
)


class WhiteHouseProviderTests(unittest.TestCase):
    def test_loads_official_shaped_feeds_deduplicates_and_classifies_titles(self) -> None:
        events = load_whitehouse_snapshots(
            Path("data/samples/whitehouse-news-rss-synthetic.xml"),
            Path("data/samples/whitehouse-actions-rss-synthetic.xml"),
            date(2026, 5, 25),
        )
        report = render_events_report(events, date(2026, 5, 25), 3, "synthetic_fixture")
        page = render_events_html(events, date(2026, 5, 25), 3, "synthetic_fixture")

        self.assertEqual(len(events), 3)
        fintech = next(event for event in events if "Financial Technology" in event.title)
        self.assertEqual(fintech.feed, "presidential_actions")
        self.assertIn("financial_regulation", fintech.themes)
        self.assertIn("energy", {topic for event in events for topic in event.themes.split(";")})
        self.assertIn("Truth Social posts", report)
        self.assertIn("Official communications.", page)
        self.assertIn("White House copyright policy", page)

    def test_merges_archive_and_counts_only_new_urls(self) -> None:
        events = load_whitehouse_snapshots(
            Path("data/samples/whitehouse-news-rss-synthetic.xml"),
            Path("data/samples/whitehouse-actions-rss-synthetic.xml"),
            date(2026, 5, 25),
        )
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "events.csv"
            write_events_csv(archive, events[:1])
            prior = load_event_archive(archive)
            merged, new_count = merge_event_archive(prior, events)

        self.assertEqual(len(merged), 3)
        self.assertEqual(new_count, 2)

    def test_rejects_external_rss_link(self) -> None:
        content = """<rss><channel><item><title>External</title><link>https://example.com/post</link><pubDate>Mon, 25 May 2026 16:15:00 +0000</pubDate></item></channel></rss>"""
        from marketwitness.providers.whitehouse import parse_whitehouse_rss

        with self.assertRaisesRegex(WhiteHouseDataError, "outside the official site"):
            parse_whitehouse_rss(content, "news", date(2026, 5, 25))

    def test_rejects_unsupported_source_mode(self) -> None:
        content = Path("data/samples/whitehouse-news-rss-synthetic.xml").read_bytes()
        from marketwitness.providers.whitehouse import parse_whitehouse_rss

        with self.assertRaisesRegex(WhiteHouseDataError, "source mode"):
            parse_whitehouse_rss(content, "news", date(2026, 5, 25), "unverified_scrape")

    def test_topic_rules_remain_explainable(self) -> None:
        self.assertEqual(classify_title("Presidential Message on Memorial Day"), ["other"])
        self.assertIn("trade_tariffs", classify_title("New tariff action on imports"))


if __name__ == "__main__":
    unittest.main()
