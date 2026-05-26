from __future__ import annotations

from datetime import date
from typing import Any

from .source_registry import SourceProvider, SourceRegistryDataError


INDICATORS = (
    {
        "symbol": "VIX",
        "family": "Equity stress",
        "role": "Expected 30-day S&P 500 volatility; anchor for stress episodes.",
        "priority": "phase_1",
        "provider_id": "cboe-volatility-family",
        "linked_context": "SPY, XLF and broad IPO conditions",
    },
    {
        "symbol": "VIX1D / VIX9D / VIX3M",
        "family": "Term structure",
        "role": "Distinguishes immediate event shocks from persistent uncertainty.",
        "priority": "phase_1",
        "provider_id": "cboe-volatility-family",
        "linked_context": "FOMC, CPI, listings and withdrawal windows",
    },
    {
        "symbol": "VXN",
        "family": "Technology stress",
        "role": "Nasdaq-100 volatility context for technology and AI-listing research.",
        "priority": "phase_1",
        "provider_id": "cboe-volatility-family",
        "linked_context": "QQQ and technology IPO pipeline",
    },
    {
        "symbol": "MOVE",
        "family": "Rates stress",
        "role": "Bond-market volatility context for funding and valuation conditions.",
        "priority": "phase_1",
        "provider_id": "ice-move-index",
        "linked_context": "Treasury curve, USD and IPO financing climate",
    },
    {
        "symbol": "VVIX / SKEW",
        "family": "Tail risk",
        "role": "Volatility-of-volatility and extreme downside-risk context.",
        "priority": "phase_2",
        "provider_id": "cboe-volatility-family",
        "linked_context": "Shock persistence and hidden protection demand",
    },
    {
        "symbol": "OVX / GVZ",
        "family": "Commodity stress",
        "role": "Oil and gold implied-volatility context for cross-asset propagation.",
        "priority": "phase_2",
        "provider_id": "cboe-volatility-family",
        "linked_context": "WTI, Brent and defensiveness research",
    },
    {
        "symbol": "VIX6M / VIX1Y",
        "family": "Structural horizon",
        "role": "Longer-horizon volatility context after the short curve is proven useful.",
        "priority": "phase_3",
        "provider_id": "cboe-volatility-family",
        "linked_context": "Long-duration listings climate",
    },
)

EPISODE_DESIGNS = (
    {
        "key": "vix_shock",
        "trigger": "VIX daily increase exceeds a disclosed threshold",
        "comparison": "SPY, QQQ, XLF, BTC, ETH, WTI, Brent, USD and Treasury rates",
        "windows": ("same_day", "1_session", "5_sessions", "20_sessions", "60_sessions"),
        "output": "Median reaction, directional frequency, dispersion and drawdown.",
    },
    {
        "key": "technology_stress_gap",
        "trigger": "VXN rises materially relative to VIX",
        "comparison": "Technology listings, QQQ and monitored AI/technology candidates",
        "windows": ("5_sessions", "20_sessions", "60_sessions"),
        "output": "Tech-specific stress overlay around verified listing milestones.",
    },
    {
        "key": "rates_before_equities",
        "trigger": "MOVE stress precedes a VIX stress regime",
        "comparison": "Treasury curve, USD, filings and listing outcomes",
        "windows": ("5_sessions", "20_sessions", "60_sessions"),
        "output": "Funding-stress sequence; observation only, never causation.",
    },
    {
        "key": "commodity_propagation",
        "trigger": "OVX or GVZ stress co-occurs with equity volatility",
        "comparison": "Energy and defensive-asset context",
        "windows": ("1_session", "5_sessions", "20_sessions"),
        "output": "Cross-asset propagation map after rights-approved data exists.",
    },
)


def build_volatility_lab_snapshot(
    providers: list[SourceProvider], as_of: date
) -> dict[str, Any]:
    if any(provider.reviewed_on > as_of for provider in providers):
        raise SourceRegistryDataError(
            "Source registry includes a provider review after the Volatility Lab cutoff."
        )
    providers_by_id = {provider.provider_id: provider for provider in providers}
    indicators = [_indicator_payload(item, providers_by_id) for item in INDICATORS]
    return {
        "product": "Volatility Intelligence Lab",
        "as_of": as_of.isoformat(),
        "research_status": "methodology_and_display_ready_real_series_pending_rights",
        "indicator_group_count": len(indicators),
        "episode_design_count": len(EPISODE_DESIGNS),
        "phase_1": ["VIX", "VIX1D / VIX9D / VIX3M", "VXN", "MOVE"],
        "research_question": (
            "When volatility stress appears in equities, technology, rates or commodities, "
            "what happened next to monitored assets and verified listing events?"
        ),
        "publication_boundary": (
            "The current page uses attributed external VIX display and publishes the study "
            "design only. It does not ingest Cboe or ICE series, calculate real episode "
            "results, or recommend a position."
        ),
        "indicators": indicators,
        "episode_designs": [
            {**item, "windows": list(item["windows"])} for item in EPISODE_DESIGNS
        ],
    }


def _indicator_payload(
    definition: dict[str, Any], providers_by_id: dict[str, SourceProvider]
) -> dict[str, Any]:
    provider = providers_by_id.get(definition["provider_id"])
    if provider is None:
        raise SourceRegistryDataError(
            f"Volatility Lab requires registered source: {definition['provider_id']}."
        )
    return {
        **definition,
        "source": {
            "provider_id": provider.provider_id,
            "provider_name": provider.provider_name,
            "official_url": provider.official_url,
            "deployment_state": provider.deployment_state,
            "publication_policy": provider.publication_policy,
        },
    }
