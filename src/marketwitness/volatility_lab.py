from __future__ import annotations

from datetime import date
from statistics import median, pstdev
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

REACTION_SCENARIOS = (
    {
        "key": "vix_rises",
        "label": "VIX rises",
        "headline": "Stress expansion",
        "trigger": "A disclosed upward VIX threshold is crossed.",
        "question": (
            "Did risk-sensitive assets weaken, defensive assets strengthen, "
            "or did the move fail to propagate?"
        ),
        "lenses": (
            {
                "family": "Equities",
                "assets": "SPY / QQQ / XLF",
                "measurement": "Return, drawdown and breadth after the stress event.",
            },
            {
                "family": "Crypto",
                "assets": "BTC / ETH",
                "measurement": "Directional reaction and dispersion versus equities.",
            },
            {
                "family": "Energy / Havens",
                "assets": "WTI / Brent / Gold / USD",
                "measurement": "Whether stress spreads or defensiveness appears.",
            },
            {
                "family": "Evidence Pipeline",
                "assets": "IPO Watch / ETF holdings",
                "measurement": "Listing milestones and permitted holdings evidence nearby.",
            },
        ),
    },
    {
        "key": "vix_cools",
        "label": "VIX cools",
        "headline": "Stress relief",
        "trigger": "A disclosed downward VIX threshold is crossed.",
        "question": (
            "Did risk appetite return across growth assets and listings, "
            "or did the calmer VIX fail to improve broader conditions?"
        ),
        "lenses": (
            {
                "family": "Equities",
                "assets": "SPY / QQQ / XLF",
                "measurement": "Recovery frequency and median forward return.",
            },
            {
                "family": "Crypto",
                "assets": "BTC / ETH",
                "measurement": "Whether digital assets participate in relief.",
            },
            {
                "family": "Energy / Havens",
                "assets": "WTI / Brent / Gold / USD",
                "measurement": "Rotation away from defense or continued caution.",
            },
            {
                "family": "Evidence Pipeline",
                "assets": "IPO Watch / ETF holdings",
                "measurement": "Verified listing progress and allowed ownership context.",
            },
        ),
    },
)

REACTION_HORIZONS = (
    {"key": "same_day", "label": "Same day"},
    {"key": "1_session", "label": "1 session"},
    {"key": "5_sessions", "label": "5 sessions"},
    {"key": "20_sessions", "label": "20 sessions"},
    {"key": "60_sessions", "label": "60 sessions"},
)

VALIDATION_RETURN_PATHS = {
    "vix_rises": {
        "threshold": "VIX close-to-close change >= +10%",
        "same_day": {
            "Equities": (-1.4, -0.6, 0.3, -2.1, -0.9, -1.7),
            "Crypto": (-2.5, -1.3, 0.9, -4.2, -1.4, -3.1),
            "Energy / Havens": (0.4, 0.7, -0.2, 1.2, 0.3, 0.9),
        },
        "1_session": {
            "Equities": (-1.1, -0.2, 0.7, -2.5, -0.3, -1.2),
            "Crypto": (-2.0, -0.8, 2.1, -5.0, -1.0, -2.6),
            "Energy / Havens": (0.6, 1.1, -0.4, 1.6, 0.4, 1.0),
        },
        "5_sessions": {
            "Equities": (-2.8, 1.4, -1.0, -4.0, 0.5, -2.2),
            "Crypto": (-5.6, 3.0, -2.4, -8.3, 1.2, -4.1),
            "Energy / Havens": (1.4, 2.1, -0.8, 2.9, 1.0, 1.8),
        },
        "20_sessions": {
            "Equities": (-3.4, 2.8, 0.9, -6.1, 1.5, -1.8),
            "Crypto": (-7.1, 8.5, 2.3, -12.4, 4.1, -4.0),
            "Energy / Havens": (2.2, 3.0, -1.6, 3.8, 1.2, 2.6),
        },
        "60_sessions": {
            "Equities": (1.2, 6.5, 4.0, -8.2, 2.3, -3.1),
            "Crypto": (3.8, 18.2, 9.6, -22.0, 7.2, -9.1),
            "Energy / Havens": (0.8, 2.4, -2.8, 2.1, -0.4, 1.0),
        },
    },
    "vix_cools": {
        "threshold": "VIX close-to-close change <= -10%",
        "same_day": {
            "Equities": (0.5, 1.0, -0.3, 0.8, 0.4, -0.2),
            "Crypto": (0.9, 1.8, -1.0, 1.2, 0.7, -0.6),
            "Energy / Havens": (-0.1, -0.4, 0.5, -0.2, 0.1, 0.3),
        },
        "1_session": {
            "Equities": (0.9, 1.4, -0.5, 1.1, 0.7, 0.2),
            "Crypto": (1.6, 2.7, -1.4, 2.0, 1.3, 0.1),
            "Energy / Havens": (-0.3, -0.8, 0.7, -0.4, 0.2, 0.4),
        },
        "5_sessions": {
            "Equities": (2.2, 3.5, -1.1, 2.8, 1.7, 0.6),
            "Crypto": (3.7, 6.2, -3.0, 4.4, 2.8, 1.0),
            "Energy / Havens": (-0.8, -1.4, 1.2, -1.0, 0.3, 0.6),
        },
        "20_sessions": {
            "Equities": (4.6, 5.2, -1.7, 3.9, 2.8, 1.6),
            "Crypto": (8.4, 11.0, -5.1, 7.2, 5.7, 2.4),
            "Energy / Havens": (-1.6, -2.7, 2.0, -1.9, 0.7, 1.1),
        },
        "60_sessions": {
            "Equities": (7.5, 8.1, -3.0, 5.9, 4.2, 2.5),
            "Crypto": (14.2, 19.5, -8.4, 10.8, 8.1, 4.5),
            "Energy / Havens": (-2.1, -3.4, 3.2, -2.2, 1.4, 1.8),
        },
    },
}


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
        "product": "VIX Reaction Explorer",
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
        "reaction_explorer": {
            "status": "design_ready_results_pending_rights",
            "prompt": (
                "Choose whether VIX rises or cools, then inspect which assets and "
                "time windows the lab is designed to test."
            ),
            "boundary": (
                "Quantitative validation uses project-authored synthetic episode paths only. "
                "Real observed returns remain unavailable until rights-approved historical "
                "inputs are enabled."
            ),
            "horizons": [dict(item) for item in REACTION_HORIZONS],
            "scenarios": [
                {**item, "lenses": [dict(lens) for lens in item["lenses"]]}
                for item in REACTION_SCENARIOS
            ],
            "validation_sample": {
                "label": "Synthetic validation sample",
                "mode": "project_authored_not_market_observations",
                "episode_count": 6,
                "result_count": len(REACTION_SCENARIOS) * len(REACTION_HORIZONS),
                "method": (
                    "Forward-return paths validate calculations and controls; "
                    "they are not observed historical market episodes."
                ),
                "results": _validation_results(),
            },
        },
        "indicators": indicators,
        "episode_designs": [
            {**item, "windows": list(item["windows"])} for item in EPISODE_DESIGNS
        ],
    }


def _validation_results() -> list[dict[str, Any]]:
    results = []
    for scenario_key, scenario in VALIDATION_RETURN_PATHS.items():
        threshold = scenario["threshold"]
        for horizon in REACTION_HORIZONS:
            horizon_key = horizon["key"]
            lens_results = []
            for family, values in scenario[horizon_key].items():
                lens_results.append(
                    {
                        "family": family,
                        "sample_count": len(values),
                        "median_return_pct": round(float(median(values)), 2),
                        "positive_frequency_pct": round(
                            sum(value > 0 for value in values) / len(values) * 100
                        ),
                        "worst_return_pct": round(min(values), 2),
                        "dispersion_pct": round(pstdev(values), 2),
                    }
                )
            results.append(
                {
                    "scenario_key": scenario_key,
                    "horizon_key": horizon_key,
                    "threshold": threshold,
                    "lens_results": lens_results,
                }
            )
    return results


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
