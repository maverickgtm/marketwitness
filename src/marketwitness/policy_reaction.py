from __future__ import annotations

from datetime import date, timedelta
from statistics import median, pstdev
from typing import Any

from .source_registry import SourceRegistryDataError


STUDY_THEMES = (
    {"key": "all", "label": "All tagged themes"},
    {"key": "financial_regulation", "label": "Financial regulation"},
    {"key": "energy", "label": "Energy"},
    {"key": "trade_tariffs", "label": "Trade / tariffs"},
    {"key": "technology_ai", "label": "Technology / AI"},
)

REACTION_WINDOWS = (
    {"key": "same_session", "label": "Same session"},
    {"key": "next_session", "label": "Next session"},
    {"key": "5_sessions", "label": "5 sessions"},
    {"key": "20_sessions", "label": "20 sessions"},
    {"key": "60_sessions", "label": "60 sessions"},
)

VALIDATION_AVAILABLE_START = date(2025, 1, 20)
VALIDATION_EPISODES = (
    {"date": date(2025, 2, 11), "theme": "trade_tariffs"},
    {"date": date(2025, 4, 16), "theme": "trade_tariffs"},
    {"date": date(2025, 6, 9), "theme": "energy"},
    {"date": date(2025, 9, 18), "theme": "financial_regulation"},
    {"date": date(2026, 2, 12), "theme": "technology_ai"},
    {"date": date(2026, 3, 9), "theme": "financial_regulation"},
)

VALIDATION_PATHS = {
    "same_session": {
        "Equity beta": (-0.8, -1.5, 0.3, 0.4, -1.1, 0.8),
        "Volatility proxy": (3.2, 7.4, -1.1, -0.8, 4.7, -2.2),
        "Crypto": (-1.5, -2.8, 0.8, 0.9, -2.4, 1.3),
        "Energy / USD": (0.2, 0.8, 1.9, -0.2, 0.3, -0.1),
    },
    "next_session": {
        "Equity beta": (-0.4, -1.1, 0.7, 0.6, -0.7, 1.0),
        "Volatility proxy": (1.9, 5.5, -1.7, -1.3, 3.2, -2.9),
        "Crypto": (-0.9, -2.0, 1.1, 1.5, -1.2, 2.1),
        "Energy / USD": (0.1, 1.0, 2.4, -0.3, 0.5, -0.2),
    },
    "5_sessions": {
        "Equity beta": (-1.0, -2.8, 1.8, 1.3, -1.5, 2.4),
        "Volatility proxy": (2.7, 9.1, -3.3, -2.5, 4.9, -5.1),
        "Crypto": (-2.1, -5.2, 3.5, 2.8, -3.2, 4.4),
        "Energy / USD": (0.5, 2.0, 4.1, -0.7, 1.0, -0.6),
    },
    "20_sessions": {
        "Equity beta": (0.6, -4.3, 3.1, 2.8, -0.8, 4.0),
        "Volatility proxy": (-2.0, 10.7, -6.4, -4.2, 1.8, -7.0),
        "Crypto": (1.1, -8.2, 6.3, 5.5, -1.7, 8.1),
        "Energy / USD": (0.8, 3.7, 5.8, -1.2, 1.5, -0.9),
    },
    "60_sessions": {
        "Equity beta": (3.4, -6.2, 5.1, 4.7, 2.1, 6.5),
        "Volatility proxy": (-4.3, 8.5, -8.1, -6.2, -2.2, -9.4),
        "Crypto": (6.7, -12.4, 10.1, 9.0, 4.6, 13.2),
        "Energy / USD": (0.5, 4.0, 6.3, -1.7, 1.8, -1.4),
    },
}


def build_policy_reaction_snapshot(
    as_of: date,
    theme: str = "all",
    period_start: date | None = None,
    period_end: date | None = None,
) -> dict[str, Any]:
    allowed_themes = {item["key"] for item in STUDY_THEMES}
    if theme not in allowed_themes:
        raise SourceRegistryDataError(f"Unsupported presidential reaction theme: {theme}.")
    selected_start = period_start or VALIDATION_AVAILABLE_START
    selected_end = period_end or as_of
    if selected_start > selected_end:
        raise SourceRegistryDataError(
            "Presidential reaction period start must be on or before its end."
        )
    if selected_start < VALIDATION_AVAILABLE_START:
        raise SourceRegistryDataError(
            "Presidential reaction validation periods cannot begin before 2025-01-20."
        )
    if selected_end > as_of:
        raise SourceRegistryDataError(
            "Presidential reaction period end cannot be after its review cutoff."
        )
    selected_indices = [
        index
        for index, episode in enumerate(VALIDATION_EPISODES)
        if selected_start <= episode["date"] <= selected_end
        and (theme == "all" or episode["theme"] == theme)
    ]
    selected_label = next(item["label"] for item in STUDY_THEMES if item["key"] == theme)
    return {
        "product": "Communication Reaction Sandbox",
        "as_of": as_of.isoformat(),
        "mode": "project_authored_not_market_observations",
        "selected_theme": {"key": theme, "label": selected_label},
        "themes": [dict(item) for item in STUDY_THEMES],
        "windows": [dict(item) for item in REACTION_WINDOWS],
        "formula": (
            "Forward move (%) = ((value at selected horizon / value at event close) - 1) x 100. "
            "Medians and frequencies are calculated only across included authored checkpoints."
        ),
        "boundary": (
            "This calculation sandbox validates filters and event-study statistics with "
            "project-authored paths. Official White House events are not assigned these "
            "results; observed market reactions require rights-approved price inputs."
        ),
        "period": {
            "start": selected_start.isoformat(),
            "end": selected_end.isoformat(),
            "available_start": VALIDATION_AVAILABLE_START.isoformat(),
            "available_end": as_of.isoformat(),
            "presets": _period_presets(as_of),
        },
        "episode_count": len(selected_indices),
        "included_checkpoints": [
            {
                "date": VALIDATION_EPISODES[index]["date"].isoformat(),
                "theme": VALIDATION_EPISODES[index]["theme"],
            }
            for index in selected_indices
        ],
        "results": _reaction_results(selected_indices),
    }


def _period_presets(as_of: date) -> list[dict[str, str]]:
    return [
        {
            "key": "full",
            "label": "Full sample",
            "start": VALIDATION_AVAILABLE_START.isoformat(),
            "end": as_of.isoformat(),
        },
        {
            "key": "year_2025",
            "label": "2025",
            "start": VALIDATION_AVAILABLE_START.isoformat(),
            "end": min(as_of, date(2025, 12, 31)).isoformat(),
        },
        {
            "key": "year_2026_ytd",
            "label": "2026 YTD",
            "start": date(2026, 1, 1).isoformat(),
            "end": as_of.isoformat(),
        },
        {
            "key": "trailing_180",
            "label": "Last 180 days",
            "start": max(VALIDATION_AVAILABLE_START, as_of - timedelta(days=180)).isoformat(),
            "end": as_of.isoformat(),
        },
    ]


def _reaction_results(selected_indices: list[int]) -> list[dict[str, Any]]:
    results = []
    for window in REACTION_WINDOWS:
        lens_results = []
        for lens, values in VALIDATION_PATHS[window["key"]].items():
            selected_values = [values[index] for index in selected_indices]
            if not selected_values:
                continue
            lens_results.append(
                {
                    "lens": lens,
                    "sample_count": len(selected_values),
                    "median_move_pct": round(float(median(selected_values)), 2),
                    "positive_frequency_pct": round(
                        sum(value > 0 for value in selected_values)
                        / len(selected_values)
                        * 100
                    ),
                    "worst_move_pct": round(min(selected_values), 2),
                    "dispersion_pct": round(pstdev(selected_values), 2),
                }
            )
        results.append({"window_key": window["key"], "lens_results": lens_results})
    return results
