from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from html import escape
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

WHITEHOUSE_NEWS_FEED_URL = "https://www.whitehouse.gov/news/feed/"
WHITEHOUSE_ACTIONS_FEED_URL = "https://www.whitehouse.gov/presidential-actions/feed/"
WHITEHOUSE_COPYRIGHT_URL = "https://www.whitehouse.gov/copyright/"
FEED_PRIORITY = {"presidential_actions": 0, "news": 1}
TOPIC_RULES = (
    ("financial_regulation", ("financial", "bank", "fintech", "crypto", "digital asset", "treasury")),
    ("energy", ("energy", "oil", "gas", "nuclear", "pipeline", "refrigerant")),
    ("trade_tariffs", ("tariff", "trade", "import", "export")),
    ("fiscal_spending", ("tax", "budget", "appropriation", "spending", "retirement")),
    ("technology_ai", ("technology", "artificial intelligence", " ai ", "semiconductor")),
    ("sanctions_geopolitics", ("sanction", "national security", "foreign policy", "cuba", "china")),
)
KNOWN_TOPICS = {topic for topic, _ in TOPIC_RULES} | {"other"}


class WhiteHouseDataError(ValueError):
    """Raised when official White House event metadata cannot be used safely."""


@dataclass(frozen=True)
class WhiteHouseEvent:
    event_id: str
    feed: str
    title: str
    published_at: str
    published_on: date
    category: str
    themes: str
    market_relevance: str
    source_mode: str
    observed_on: date
    source_url: str


def fetch_whitehouse_events(observed_on: date) -> list[WhiteHouseEvent]:
    events: list[WhiteHouseEvent] = []
    for feed, url in (("news", WHITEHOUSE_NEWS_FEED_URL), ("presidential_actions", WHITEHOUSE_ACTIONS_FEED_URL)):
        request = Request(
            url,
            headers={
                "User-Agent": "MarketWitness/0.1 public-research-monitor",
                "Accept": "application/rss+xml",
            },
        )
        try:
            with urlopen(request, timeout=60) as response:
                content = response.read()
        except (URLError, TimeoutError, OSError) as exc:
            raise WhiteHouseDataError(f"Unable to retrieve White House {feed} RSS: {exc}") from exc
        events.extend(parse_whitehouse_rss(content, feed, observed_on, "official_live_rss"))
    return _deduplicate_events(events)


def load_whitehouse_snapshots(
    news_path: str | Path, actions_path: str | Path, observed_on: date
) -> list[WhiteHouseEvent]:
    events: list[WhiteHouseEvent] = []
    for feed, path in (("news", news_path), ("presidential_actions", actions_path)):
        try:
            content = Path(path).read_bytes()
        except OSError as exc:
            raise WhiteHouseDataError(f"Unable to read White House RSS snapshot {path}: {exc}") from exc
        events.extend(parse_whitehouse_rss(content, feed, observed_on, "synthetic_fixture"))
    return _deduplicate_events(events)


def parse_whitehouse_rss(
    content: bytes | str, feed: str, observed_on: date, source_mode: str = "official_live_rss"
) -> list[WhiteHouseEvent]:
    if feed not in FEED_PRIORITY:
        raise WhiteHouseDataError(f"Unsupported White House RSS channel: {feed}.")
    if source_mode not in {"synthetic_fixture", "official_live_rss"}:
        raise WhiteHouseDataError(f"Unsupported White House source mode: {source_mode}.")
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise WhiteHouseDataError(f"White House {feed} RSS is invalid XML: {exc}") from exc
    channel = root.find("channel")
    if channel is None:
        raise WhiteHouseDataError(f"White House {feed} RSS does not contain a channel.")
    events: list[WhiteHouseEvent] = []
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        source_url = (item.findtext("link") or "").strip()
        raw_published = (item.findtext("pubDate") or "").strip()
        guid = (item.findtext("guid") or source_url).strip()
        category = (item.findtext("category") or "Official communication").strip()
        if not title or not source_url or not raw_published:
            raise WhiteHouseDataError(f"White House {feed} RSS item is missing title, URL or date.")
        if not source_url.startswith("https://www.whitehouse.gov/"):
            raise WhiteHouseDataError(f"White House {feed} RSS item links outside the official site.")
        try:
            published = parsedate_to_datetime(raw_published).astimezone(timezone.utc)
        except (TypeError, ValueError) as exc:
            raise WhiteHouseDataError(f"White House {feed} RSS item contains an invalid date.") from exc
        if published.date() > observed_on:
            raise WhiteHouseDataError("White House RSS contains an item after the observation date.")
        themes = classify_title(title)
        events.append(
            WhiteHouseEvent(
                event_id=guid or source_url,
                feed=feed,
                title=title,
                published_at=published.isoformat().replace("+00:00", "Z"),
                published_on=published.date(),
                category=category,
                themes=";".join(themes),
                market_relevance="review_candidate" if themes != ["other"] else "context_only",
                source_mode=source_mode,
                observed_on=observed_on,
                source_url=source_url,
            )
        )
    return _deduplicate_events(events)


def classify_title(title: str) -> list[str]:
    normalized = f" {title.casefold()} "
    themes = [
        topic
        for topic, keywords in TOPIC_RULES
        if any(keyword in normalized for keyword in keywords)
    ]
    return themes or ["other"]


def load_event_archive(path: str | Path) -> list[WhiteHouseEvent]:
    source = Path(path)
    if not source.is_file():
        return []
    try:
        with source.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        raise WhiteHouseDataError(f"Unable to read White House event archive {path}: {exc}") from exc
    events: list[WhiteHouseEvent] = []
    required = set(WhiteHouseEvent.__annotations__)
    for row in rows:
        missing = required - set(row)
        if missing:
            raise WhiteHouseDataError(f"White House event archive is missing columns: {', '.join(sorted(missing))}.")
        try:
            published_on = date.fromisoformat(row["published_on"].strip())
            observed_on = date.fromisoformat(row["observed_on"].strip())
        except ValueError as exc:
            raise WhiteHouseDataError("White House event archive contains an invalid date.") from exc
        events.append(
            WhiteHouseEvent(
                event_id=row["event_id"].strip(),
                feed=row["feed"].strip(),
                title=row["title"].strip(),
                published_at=row["published_at"].strip(),
                published_on=published_on,
                category=row["category"].strip(),
                themes=row["themes"].strip(),
                market_relevance=row["market_relevance"].strip(),
                source_mode=row["source_mode"].strip(),
                observed_on=observed_on,
                source_url=row["source_url"].strip(),
            )
        )
        if events[-1].market_relevance not in {"review_candidate", "context_only"}:
            raise WhiteHouseDataError("White House event archive contains an unknown relevance state.")
        if set(events[-1].themes.split(";")) - KNOWN_TOPICS:
            raise WhiteHouseDataError("White House event archive contains an unknown topic tag.")
        if events[-1].source_mode not in {"synthetic_fixture", "official_live_rss"}:
            raise WhiteHouseDataError("White House event archive contains an unknown source mode.")
    return _deduplicate_events(events)


def merge_event_archive(
    prior: list[WhiteHouseEvent], observed: list[WhiteHouseEvent]
) -> tuple[list[WhiteHouseEvent], int]:
    prior_urls = {event.source_url for event in prior}
    merged = _deduplicate_events(prior + observed)
    return merged, sum(event.source_url not in prior_urls for event in _deduplicate_events(observed))


def write_events_csv(path: str | Path, events: list[WhiteHouseEvent]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(WhiteHouseEvent.__annotations__))
        writer.writeheader()
        for event in events:
            row = dict(event.__dict__)
            row["published_on"] = event.published_on.isoformat()
            row["observed_on"] = event.observed_on.isoformat()
            writer.writerow(row)


def render_events_report(
    events: list[WhiteHouseEvent], observed_on: date, new_count: int, source_mode: str
) -> str:
    relevant = sum(event.market_relevance == "review_candidate" for event in events)
    lines = [
        "# White House Official Event Intake",
        "",
        f"- Observed on: `{observed_on.isoformat()}`",
        f"- Source mode: `{source_mode}`",
        f"- Archived unique events: `{len(events)}`",
        f"- New in this observation: `{new_count}`",
        f"- Market-theme review candidates: `{relevant}`",
        "",
        "This queue preserves titles, timestamps, source links and rule-based topics",
        "from official White House News and Presidential Actions RSS only. It does",
        "not collect Truth Social posts, calculate market reaction or recommend trades.",
        "",
        "## Event Queue",
        "",
        "| Published UTC | Channel | Title | Topics | Relevance |",
        "|---|---|---|---|---|",
    ]
    for event in events:
        lines.append(
            f"| {event.published_at} | {event.feed} | [{event.title}]({event.source_url}) | "
            f"{event.themes} | `{event.market_relevance}` |"
        )
    return "\n".join(lines) + "\n"


def write_events_report(
    path: str | Path, events: list[WhiteHouseEvent], observed_on: date, new_count: int, source_mode: str
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_events_report(events, observed_on, new_count, source_mode), encoding="utf-8"
    )


def render_events_html(
    events: list[WhiteHouseEvent], observed_on: date, new_count: int, source_mode: str
) -> str:
    relevant = sum(event.market_relevance == "review_candidate" for event in events)
    rows = "".join(
        "<article class=\"event\">"
        f"<p class=\"meta\">{escape(event.published_at)} / {escape(event.feed.replace('_', ' '))}</p>"
        f"<h3>{escape(event.title)}</h3>"
        f"<p><span class=\"tag\">{escape(event.themes.replace(';', ' / '))}</span> "
        f"<span class=\"state\">{escape(event.market_relevance.replace('_', ' '))}</span></p>"
        f"<a href=\"{escape(event.source_url)}\">Open official source</a>"
        "</article>"
        for event in events
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MarketWitness | White House Official Event Intake</title><style>
:root{{--bg:#070a12;--panel:#111827;--line:#29354a;--text:#f2f5f8;--muted:#98a7ba;--mint:#58dfb0;--amber:#ffcc68;}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.48 Inter,Arial,sans-serif}}header,main{{max-width:1120px;margin:auto;padding:30px 24px}}
a{{color:var(--mint);text-decoration:none}}nav,.meta{{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}}h1{{font-size:clamp(35px,5vw,55px);line-height:1.05;margin:35px 0 12px}}.lead,.notice{{color:var(--muted)}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;margin:30px 0}}.card,.event,.notice{{background:var(--panel);border:1px solid var(--line);border-radius:15px;padding:17px}}.card strong{{display:block;color:var(--mint);font-size:37px}}.notice{{border-left:3px solid var(--amber)}}.queue{{display:grid;gap:12px;margin-top:18px}}.event h3{{font-size:18px;margin:9px 0 13px}}.tag,.state{{display:inline-block;border-radius:999px;padding:5px 9px;margin-bottom:12px;font-size:12px;background:rgba(88,223,176,.1);color:var(--mint)}}.state{{background:rgba(255,204,104,.11);color:var(--amber)}}@media(max-width:700px){{.cards{{grid-template-columns:1fr}}}}
</style></head><body><header><nav><a href="/dashboard/presidential-impact">Presidential Impact Lab</a> / Official event intake</nav>
<h1>Official communications.<br>Research queue.</h1><p class="lead">Archived title-and-link metadata from White House News and Presidential Actions RSS.</p>
<p class="meta">Observed {escape(observed_on.isoformat())} / {escape(source_mode)}</p>
<section class="cards"><article class="card"><p>Archived events</p><strong>{len(events)}</strong></article><article class="card"><p>New this run</p><strong>{new_count}</strong></article><article class="card"><p>Theme candidates</p><strong>{relevant}</strong></article></section>
<p class="notice">Rule-based topic tagging opens investigation only. This artifact does not collect Truth Social posts, calculate market reaction, establish causation or recommend trades. See the <a href="{WHITEHOUSE_COPYRIGHT_URL}">White House copyright policy</a>.</p></header>
<main><h2>Event queue</h2><section class="queue">{rows}</section></main></body></html>"""


def write_events_html(
    path: str | Path, events: list[WhiteHouseEvent], observed_on: date, new_count: int, source_mode: str
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        render_events_html(events, observed_on, new_count, source_mode), encoding="utf-8"
    )


def _deduplicate_events(events: list[WhiteHouseEvent]) -> list[WhiteHouseEvent]:
    selected: dict[str, WhiteHouseEvent] = {}
    for event in events:
        if event.feed not in FEED_PRIORITY:
            raise WhiteHouseDataError("White House event archive contains an unsupported channel.")
        if not event.source_url.startswith("https://www.whitehouse.gov/"):
            raise WhiteHouseDataError("White House event archive contains a non-official source URL.")
        existing = selected.get(event.source_url)
        if existing is None or FEED_PRIORITY[event.feed] < FEED_PRIORITY[existing.feed]:
            selected[event.source_url] = event
    return sorted(
        selected.values(),
        key=lambda event: (event.published_at, -FEED_PRIORITY[event.feed], event.title),
        reverse=True,
    )
