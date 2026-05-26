from __future__ import annotations

from decimal import Decimal
from typing import Any

from .providers.treasury import TreasuryYield


SUPPORTED_WINDOWS = (1, 5, 20, 60)


def build_treasury_regime_snapshot(
    yields: list[TreasuryYield], sessions: int = 1
) -> dict[str, Any]:
    if sessions not in SUPPORTED_WINDOWS:
        raise ValueError("Treasury comparison window must be 1, 5, 20 or 60 sessions.")
    if not yields:
        raise ValueError("Treasury regime analysis requires at least one observation.")

    ordered = sorted(yields, key=lambda item: item.rate_date)
    latest = ordered[-1]
    reference = ordered[-(sessions + 1)] if len(ordered) > sessions else None
    modes = {item.source_mode for item in ordered}
    source_mode = (
        "Synthetic reproducible Treasury fixture"
        if modes == {"synthetic_fixture"}
        else "Official U.S. Treasury daily yields"
        if modes == {"official_live_xml"}
        else "Mixed Treasury validation archive"
    )
    result = {
        "product": "Treasury Curve Regime Explorer",
        "available": True,
        "data_mode": source_mode,
        "observation_date": max(item.observed_on.isoformat() for item in ordered),
        "latest_rate_date": latest.rate_date.isoformat(),
        "observation_count": len(ordered),
        "selected_sessions": sessions,
        "curve_regime": _curve_regime(latest.curve_2s10s_bps),
        "latest": _yield_payload(latest),
        "comparison_available": reference is not None,
        "comparison": None,
        "history": [_yield_payload(item) for item in reversed(ordered[-20:])],
        "publication_boundary": (
            "Official Treasury observations describe the yield-curve environment. "
            "They do not predict returns, explain moves in external charts or recommend a trade."
        ),
    }
    if reference is not None:
        curve_change = latest.curve_2s10s_bps - reference.curve_2s10s_bps
        result["comparison"] = {
            "reference_date": reference.rate_date.isoformat(),
            "latest_date": latest.rate_date.isoformat(),
            "sessions": sessions,
            "two_year_change_bps": _change_bps(reference.two_year_pct, latest.two_year_pct),
            "ten_year_change_bps": _change_bps(reference.ten_year_pct, latest.ten_year_pct),
            "curve_change_bps": _fixed(curve_change),
            "curve_shift": _curve_shift(curve_change),
        }
    return result


def _yield_payload(item: TreasuryYield) -> dict[str, str]:
    return {
        "rate_date": item.rate_date.isoformat(),
        "two_year_pct": str(item.two_year_pct),
        "ten_year_pct": str(item.ten_year_pct),
        "curve_2s10s_bps": _fixed(item.curve_2s10s_bps),
        "source_url": item.source_url,
    }


def _change_bps(before: Decimal, after: Decimal) -> str:
    return _fixed((after - before) * Decimal("100"))


def _fixed(value: Decimal) -> str:
    return f"{value:+.2f}"


def _curve_regime(spread: Decimal) -> dict[str, str]:
    if spread < 0:
        return {
            "key": "inverted",
            "label": "Inverted curve",
            "interpretation": "2Y yield is above 10Y yield; rates context signals inversion.",
        }
    if spread <= Decimal("25"):
        return {
            "key": "near_flat",
            "label": "Near-flat curve",
            "interpretation": "2Y and 10Y yields are separated by no more than 25 basis points.",
        }
    return {
        "key": "upward_sloping",
        "label": "Upward-sloping curve",
        "interpretation": "10Y yield is more than 25 basis points above 2Y yield.",
    }


def _curve_shift(change: Decimal) -> str:
    if change > Decimal("2"):
        return "Steepening"
    if change < Decimal("-2"):
        return "Flattening"
    return "Broadly stable"
