from __future__ import annotations

from decimal import Decimal
from typing import Any

from .providers.treasury import TreasuryYield
from .providers.whitehouse import WhiteHouseEvent


def build_policy_treasury_context(
    events: list[WhiteHouseEvent], yields: list[TreasuryYield]
) -> dict[str, Any]:
    candidates = [
        event for event in events if event.market_relevance == "review_candidate"
    ]
    measured = []
    pending = []
    for event in sorted(candidates, key=lambda item: item.published_on, reverse=True):
        # Use sessions strictly after publication so an evening communication
        # cannot be compared against a yield already observed earlier that day.
        eligible_yields = [item for item in yields if item.rate_date > event.published_on]
        if len(eligible_yields) < 2:
            pending.append(
                {
                    "title": event.title,
                    "published_on": event.published_on.isoformat(),
                    "themes": event.themes,
                    "source_url": event.source_url,
                    "reason": "Awaiting two Treasury sessions after publication.",
                }
            )
            continue
        reference, following = eligible_yields[:2]
        measured.append(
            {
                "title": event.title,
                "published_on": event.published_on.isoformat(),
                "themes": event.themes,
                "source_url": event.source_url,
                "reference_date": reference.rate_date.isoformat(),
                "following_date": following.rate_date.isoformat(),
                "two_year_reference_pct": str(reference.two_year_pct),
                "ten_year_reference_pct": str(reference.ten_year_pct),
                "two_year_change_bps": _basis_point_change(
                    reference.two_year_pct, following.two_year_pct
                ),
                "ten_year_change_bps": _basis_point_change(
                    reference.ten_year_pct, following.ten_year_pct
                ),
                "curve_change_bps": _basis_point_change(
                    reference.curve_2s10s_bps, following.curve_2s10s_bps, Decimal("1")
                ),
            }
        )
    modes = {item.source_mode for item in yields}
    return {
        "product": "Official Treasury Session Context",
        "available": True,
        "data_mode": (
            "Synthetic reproducible Treasury fixture"
            if modes == {"synthetic_fixture"}
            else "Official U.S. Treasury daily yields"
            if modes == {"official_live_xml"}
            else "Mixed Treasury validation archive"
        ),
        "observation_date": max(
            (item.observed_on.isoformat() for item in yields), default=None
        ),
        "latest_rate_date": max(
            (item.rate_date.isoformat() for item in yields), default=None
        ),
        "yield_observation_count": len(yields),
        "candidate_event_count": len(candidates),
        "measured_event_count": len(measured),
        "pending_event_count": len(pending),
        "measurement": (
            "For each thematic official communication, compare the first available "
            "Treasury daily observation after publication with the next available session."
        ),
        "publication_boundary": (
            "Changes are observed temporal context in basis points. They do not prove "
            "that a presidential communication caused a rate move or support a trade."
        ),
        "records": measured,
        "pending": pending,
    }


def _basis_point_change(
    before: Decimal, after: Decimal, multiplier: Decimal = Decimal("100")
) -> str:
    value = (after - before) * multiplier
    return f"{value:+.2f}"
