from __future__ import annotations

import csv
import os
import re
from dataclasses import dataclass
from datetime import date, datetime
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


FOMC_CALENDAR_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
BLS_CALENDAR_URL = "https://www.bls.gov/schedule/news_release/bls.ics"
BLS_SCHEDULE_URL = "https://www.bls.gov/schedule/"
LOCAL_USER_AGENT_PATH = Path("data/private/sec_user_agent.txt")
BLS_RELEASES = {
    "Consumer Price Index": ("Inflation", "CPI"),
    "Producer Price Index": ("Inflation", "PPI"),
    "Employment Situation": ("Labor Markets", "Payrolls"),
    "Job Openings and Labor Turnover Survey": ("Labor Markets", "JOLTS"),
}
FIELDNAMES = (
    "event_id",
    "agency",
    "category",
    "short_label",
    "title",
    "start_date",
    "end_date",
    "time_et",
    "has_projections",
    "source_mode",
    "observed_on",
    "source_url",
)


class MacroCalendarDataError(ValueError):
    """Raised when an official macro calendar cannot be validated."""


@dataclass(frozen=True)
class MacroEvent:
    event_id: str
    agency: str
    category: str
    short_label: str
    title: str
    start_date: date
    end_date: date
    time_et: str
    has_projections: bool
    source_mode: str
    observed_on: date
    source_url: str


def fetch_macro_calendar(
    year: int, observed_on: date, user_agent: str | None = None
) -> list[MacroEvent]:
    configured_agent = configured_user_agent(user_agent)
    return _merge_events(
        parse_fomc_html(
            _download(FOMC_CALENDAR_URL, "text/html", configured_agent),
            year,
            observed_on,
            "official_live_html",
        ),
        parse_bls_ical(
            _download(BLS_CALENDAR_URL, "text/calendar", configured_agent),
            year,
            observed_on,
            "official_live_ical",
        ),
    )


def load_macro_snapshots(
    fomc_path: str | Path, bls_path: str | Path, year: int, observed_on: date
) -> list[MacroEvent]:
    try:
        fomc = Path(fomc_path).read_text(encoding="utf-8")
        bls = Path(bls_path).read_text(encoding="utf-8")
    except OSError as exc:
        raise MacroCalendarDataError(f"Unable to read macro calendar fixture: {exc}") from exc
    return _merge_events(
        parse_fomc_html(fomc, year, observed_on, "synthetic_fixture"),
        parse_bls_ical(bls, year, observed_on, "synthetic_fixture"),
    )


def parse_bls_ical(
    content: bytes | str, year: int, observed_on: date, source_mode: str
) -> list[MacroEvent]:
    _validate_mode(source_mode)
    text = content.decode("utf-8") if isinstance(content, bytes) else content
    if "BEGIN:VCALENDAR" not in text:
        raise MacroCalendarDataError("BLS calendar is not a valid iCalendar feed.")
    unfolded = text.replace("\r\n ", "").replace("\n ", "")
    events: list[MacroEvent] = []
    for raw in re.findall(r"BEGIN:VEVENT\s*(.*?)\s*END:VEVENT", unfolded, flags=re.S):
        values: dict[str, str] = {}
        for line in raw.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            values[key.split(";", 1)[0].strip()] = value.strip()
        title = values.get("SUMMARY", "")
        if title not in BLS_RELEASES:
            continue
        try:
            event_at = datetime.strptime(values["DTSTART"][:15], "%Y%m%dT%H%M%S")
        except (KeyError, ValueError) as exc:
            raise MacroCalendarDataError("BLS calendar has an invalid release date.") from exc
        if event_at.year != year:
            continue
        category, short_label = BLS_RELEASES[title]
        events.append(
            MacroEvent(
                event_id=f"bls-{short_label.casefold()}-{event_at.date().isoformat()}",
                agency="BLS",
                category=category,
                short_label=short_label,
                title=title,
                start_date=event_at.date(),
                end_date=event_at.date(),
                time_et=event_at.strftime("%H:%M ET"),
                has_projections=False,
                source_mode=source_mode,
                observed_on=observed_on,
                source_url=BLS_SCHEDULE_URL,
            )
        )
    if not events:
        raise MacroCalendarDataError(f"BLS calendar contains no selected releases for {year}.")
    return sorted(events, key=lambda item: (item.start_date, item.title))


def parse_fomc_html(
    content: bytes | str, year: int, observed_on: date, source_mode: str
) -> list[MacroEvent]:
    _validate_mode(source_mode)
    text = content.decode("utf-8") if isinstance(content, bytes) else content
    parser = _FomcMeetingParser(year)
    parser.feed(text)
    if not parser.meetings:
        raise MacroCalendarDataError(f"Federal Reserve page contains no FOMC meetings for {year}.")
    events = []
    for month, raw_days in parser.meetings:
        clean_days = raw_days.replace("*", "").strip()
        has_projections = "*" in raw_days
        match = re.fullmatch(r"(\d{1,2})(?:-(\d{1,2}))?", clean_days)
        if not match or "/" in month:
            raise MacroCalendarDataError("FOMC calendar contains an unsupported meeting date.")
        try:
            month_number = datetime.strptime(month, "%B").month
            start = date(year, month_number, int(match.group(1)))
            end = date(year, month_number, int(match.group(2) or match.group(1)))
        except ValueError as exc:
            raise MacroCalendarDataError("FOMC calendar contains an invalid meeting date.") from exc
        events.append(
            MacroEvent(
                event_id=f"fomc-{end.isoformat()}",
                agency="Federal Reserve",
                category="Monetary Policy",
                short_label="FOMC",
                title="FOMC meeting and policy decision",
                start_date=start,
                end_date=end,
                time_et="Decision date",
                has_projections=has_projections,
                source_mode=source_mode,
                observed_on=observed_on,
                source_url=FOMC_CALENDAR_URL,
            )
        )
    return sorted(events, key=lambda item: item.start_date)


def load_macro_calendar_csv(path: str | Path) -> list[MacroEvent]:
    try:
        with Path(path).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        raise MacroCalendarDataError(f"Unable to read macro calendar CSV: {exc}") from exc
    events: list[MacroEvent] = []
    for row in rows:
        if not set(FIELDNAMES).issubset(row):
            raise MacroCalendarDataError("Macro calendar CSV is missing required fields.")
        try:
            event = MacroEvent(
                event_id=row["event_id"].strip(),
                agency=row["agency"].strip(),
                category=row["category"].strip(),
                short_label=row["short_label"].strip(),
                title=row["title"].strip(),
                start_date=date.fromisoformat(row["start_date"]),
                end_date=date.fromisoformat(row["end_date"]),
                time_et=row["time_et"].strip(),
                has_projections=row["has_projections"].strip() == "true",
                source_mode=row["source_mode"].strip(),
                observed_on=date.fromisoformat(row["observed_on"]),
                source_url=row["source_url"].strip(),
            )
        except ValueError as exc:
            raise MacroCalendarDataError("Macro calendar CSV has an invalid row.") from exc
        _validate_event(event)
        events.append(event)
    if not events:
        raise MacroCalendarDataError("Macro calendar CSV contains no events.")
    return _merge_events(events)


def write_macro_calendar_csv(path: str | Path, events: list[MacroEvent]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for event in events:
            writer.writerow(
                {
                    **event.__dict__,
                    "start_date": event.start_date.isoformat(),
                    "end_date": event.end_date.isoformat(),
                    "has_projections": str(event.has_projections).lower(),
                    "observed_on": event.observed_on.isoformat(),
                }
            )


def build_macro_calendar_snapshot(
    events: list[MacroEvent], horizon_days: int = 90, agency: str = "all"
) -> dict[str, object]:
    if horizon_days not in {30, 90, 180, 365}:
        raise MacroCalendarDataError("Calendar horizon must be 30, 90, 180 or 365 days.")
    if agency not in {"all", "BLS", "Federal Reserve"}:
        raise MacroCalendarDataError("Calendar agency must be all, BLS or Federal Reserve.")
    as_of = max(event.observed_on for event in events)
    upcoming = [
        event
        for event in sorted(events, key=lambda item: (item.start_date, item.title))
        if event.end_date >= as_of
        and (event.start_date - as_of).days <= horizon_days
        and (agency == "all" or event.agency == agency)
    ]
    modes = {event.source_mode for event in events}
    return {
        "available": True,
        "product": "Macro Catalyst Calendar",
        "data_mode": (
            "Official Federal Reserve and BLS schedules"
            if modes <= {"official_live_html", "official_live_ical"}
            else "Synthetic reproducible schedule fixture"
            if modes == {"synthetic_fixture"}
            else "Mixed validation calendar"
        ),
        "as_of": as_of.isoformat(),
        "selected_horizon_days": horizon_days,
        "selected_agency": agency,
        "scheduled_event_count": len(events),
        "upcoming_count": len(upcoming),
        "next_event": _payload(upcoming[0], as_of) if upcoming else None,
        "agency_counts": {
            name: sum(event.agency == name for event in upcoming)
            for name in ("BLS", "Federal Reserve")
        },
        "events": [_payload(event, as_of) for event in upcoming],
        "publication_boundary": (
            "Scheduled releases and meetings identify known catalyst times only. "
            "They do not forecast outcomes, predict price direction or recommend positions."
        ),
    }


def write_macro_calendar_report(
    path: str | Path, events: list[MacroEvent], observed_on: date, source_mode: str
) -> None:
    snapshot = build_macro_calendar_snapshot(events, horizon_days=365)
    lines = [
        "# Macro Catalyst Calendar",
        "",
        f"- Observed: `{observed_on.isoformat()}`",
        f"- Source mode: `{source_mode}`",
        f"- Scheduled events normalized: `{len(events)}`",
        "",
        snapshot["publication_boundary"],
        "",
        "| Date | Agency | Catalyst | Time / Detail | Source |",
        "|---|---|---|---|---|",
    ]
    for event in snapshot["events"]:
        lines.append(
            f"| {event['date_range']} | {event['agency']} | {event['title']} | "
            f"{event['detail']} | [Official source]({event['source_url']}) |"
        )
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_macro_calendar_html(
    path: str | Path, events: list[MacroEvent], observed_on: date, source_mode: str
) -> None:
    snapshot = build_macro_calendar_snapshot(events, horizon_days=365)
    rows = "".join(
        f"<tr><td>{escape(str(item['date_range']))}</td><td>{escape(str(item['agency']))}</td>"
        f"<td>{escape(str(item['title']))}</td><td>{escape(str(item['detail']))}</td>"
        f'<td><a href="{escape(str(item["source_url"]))}">Official source</a></td></tr>'
        for item in snapshot["events"]
    )
    page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>MarketWitness | Macro Catalyst Calendar</title>
<style>body{{margin:0;background:#070d16;color:#e9f0f5;font:15px Arial,sans-serif}}header,main{{max-width:1120px;margin:auto;padding:32px}}h1{{font-size:44px;margin:10px 0}}p{{color:#9fb0c0;line-height:1.6}}.cards{{display:flex;gap:12px;margin:24px 0}}.card{{background:#121d2c;border:1px solid #27364b;border-radius:14px;padding:16px 20px}}strong{{font-size:28px;color:#58dfb0}}table{{width:100%;border-collapse:collapse;background:#121d2c;border-radius:14px;overflow:hidden}}th,td{{text-align:left;padding:12px;border-bottom:1px solid #27364b}}th{{color:#9fb0c0}}a{{color:#58dfb0}}</style>
<header><p>OFFICIAL SCHEDULE CONTEXT</p><h1>Known catalysts.<br>Official dates.</h1><p>Federal Reserve meeting dates and selected BLS release times, normalized from official schedules. A scheduled event is not an investment signal.</p><div class="cards"><div class="card"><p>Upcoming in year</p><strong>{snapshot["upcoming_count"]}</strong></div><div class="card"><p>Observed on</p><strong>{escape(observed_on.isoformat())}</strong></div><div class="card"><p>Source mode</p><strong>{escape(source_mode)}</strong></div></div></header>
<main><table><thead><tr><th>Date</th><th>Agency</th><th>Catalyst</th><th>Detail</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></main></html>"""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page, encoding="utf-8")


def _payload(event: MacroEvent, as_of: date) -> dict[str, object]:
    date_range = event.start_date.isoformat()
    if event.end_date != event.start_date:
        date_range = f"{date_range} to {event.end_date.isoformat()}"
    detail = event.time_et
    if event.has_projections:
        detail += " / Economic projections scheduled"
    return {
        "event_id": event.event_id,
        "agency": event.agency,
        "category": event.category,
        "short_label": event.short_label,
        "title": event.title,
        "start_date": event.start_date.isoformat(),
        "end_date": event.end_date.isoformat(),
        "date_range": date_range,
        "days_until": max((event.start_date - as_of).days, 0),
        "detail": detail,
        "source_url": event.source_url,
    }


def configured_user_agent(user_agent: str | None = None) -> str:
    saved_agent = (
        LOCAL_USER_AGENT_PATH.read_text(encoding="utf-8").strip()
        if LOCAL_USER_AGENT_PATH.exists()
        else ""
    )
    declared = (
        user_agent
        or os.environ.get("MARKETWITNESS_MACRO_USER_AGENT", "")
        or os.environ.get("MARKETWITNESS_SEC_USER_AGENT", "")
        or saved_agent
    ).strip()
    if "@" not in declared:
        raise MacroCalendarDataError(
            "Official BLS/FOMC collection requires --user-agent, "
            "MARKETWITNESS_MACRO_USER_AGENT or a local SEC User-Agent file "
            "containing a monitored contact email."
        )
    return declared


def _download(url: str, accept: str, user_agent: str) -> bytes:
    request = Request(url, headers={"User-Agent": user_agent, "Accept": accept})
    try:
        with urlopen(request, timeout=60) as response:
            return response.read()
    except (URLError, TimeoutError, OSError) as exc:
        raise MacroCalendarDataError(f"Unable to retrieve official macro calendar: {exc}") from exc


def _validate_mode(source_mode: str) -> None:
    if source_mode not in {"synthetic_fixture", "official_live_html", "official_live_ical"}:
        raise MacroCalendarDataError(f"Unsupported macro calendar source mode: {source_mode}.")


def _validate_event(event: MacroEvent) -> None:
    _validate_mode(event.source_mode)
    if event.end_date < event.start_date:
        raise MacroCalendarDataError("Macro calendar event ends before it starts.")
    if event.agency not in {"BLS", "Federal Reserve"}:
        raise MacroCalendarDataError("Macro calendar event has an unknown agency.")


def _merge_events(*event_groups: list[MacroEvent]) -> list[MacroEvent]:
    merged: dict[str, MacroEvent] = {}
    for event in [event for group in event_groups for event in group]:
        _validate_event(event)
        merged[event.event_id] = event
    return sorted(merged.values(), key=lambda item: (item.start_date, item.agency, item.title))


class _FomcMeetingParser(HTMLParser):
    def __init__(self, year: int) -> None:
        super().__init__()
        self.year = year
        self.active = False
        self.fields: list[str | None] = []
        self.month = ""
        self.days = ""
        self.meetings: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "div":
            return
        classes = dict(attrs).get("class") or ""
        field = None
        if self.active and "fomc-meeting__month" in classes:
            field = "month"
            self.month = ""
        elif self.active and "fomc-meeting__date" in classes:
            field = "date"
            self.days = ""
        self.fields.append(field)

    def handle_endtag(self, tag: str) -> None:
        if tag != "div" or not self.fields:
            return
        field = self.fields.pop()
        if field == "date" and self.month.strip() and self.days.strip():
            self.meetings.append((self.month.strip(), self.days.strip()))
            self.month = ""
            self.days = ""

    def handle_data(self, data: str) -> None:
        normalized = " ".join(data.split())
        if normalized.endswith("FOMC Meetings") and normalized[:4].isdigit():
            self.active = normalized == f"{self.year} FOMC Meetings"
        if not self.active or not self.fields:
            return
        if self.fields[-1] == "month":
            self.month += data
        elif self.fields[-1] == "date":
            self.days += data
