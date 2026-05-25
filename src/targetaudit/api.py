from __future__ import annotations

import os
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
from statistics import median
from typing import Optional

from fastapi import FastAPI, HTTPException, Query

from . import METHODOLOGY_VERSION, __version__
from .models import Evaluation
from .reporting import wilson_interval
from .storage import (
    WarehouseError,
    list_run_summaries,
    read_evaluations,
    read_run_assets,
    read_run_summary,
)

DEFAULT_DATABASE_PATH = "build/live/targetaudit.duckdb"


def create_app(database_path: str | Path | None = None) -> FastAPI:
    database = Path(
        database_path or os.environ.get("TARGETAUDIT_DATABASE", DEFAULT_DATABASE_PATH)
    )
    application = FastAPI(
        title="TargetAudit API",
        version=__version__,
        description="Read-only API for auditable analyst target research runs.",
    )

    @application.get("/api/v1/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "service": "targetaudit-api",
            "methodology_version": METHODOLOGY_VERSION,
            "database_available": database.is_file(),
        }

    @application.get("/api/v1/runs")
    def runs() -> list[dict[str, object]]:
        return _warehouse_call(list_run_summaries, database)

    @application.get("/api/v1/runs/{run_id}")
    def run_detail(run_id: str) -> dict[str, object]:
        run = _read_run(database, run_id)
        run["assets"] = [
            {
                "asset_role": item["asset_role"],
                "sha256": item["sha256"],
                "byte_size": item["byte_size"],
            }
            for item in _warehouse_call(read_run_assets, database, run_id)
        ]
        return run

    @application.get("/api/v1/runs/{run_id}/rankings/firms")
    def firm_ranking(
        run_id: str,
        minimum_sample: Optional[int] = Query(default=None, ge=1),
        sector: str = "",
        direction: str = Query(default="", pattern="^(|up|down)$"),
    ) -> dict[str, object]:
        run = _read_run(database, run_id)
        rows = _warehouse_call(read_evaluations, database, run_id, status="evaluated")
        if sector:
            rows = [item for item in rows if item.sector.lower() == sector.lower()]
        if direction:
            rows = [item for item in rows if item.direction == direction]
        threshold = minimum_sample or run["minimum_sample"]
        grouped: defaultdict[str, list[Evaluation]] = defaultdict(list)
        for item in rows:
            grouped[item.firm].append(item)
        ranking = [
            _ranking_row(firm, values)
            for firm, values in grouped.items()
            if len(values) >= threshold
        ]
        ranking.sort(key=lambda row: (-row["hit_rate"], -row["observations"], row["firm"].lower()))
        return {
            "run_id": run_id,
            "methodology_version": METHODOLOGY_VERSION,
            "minimum_sample": threshold,
            "sector": sector or None,
            "direction": direction or None,
            "ranking": ranking,
        }

    @application.get("/api/v1/runs/{run_id}/firms/{firm}")
    def firm_detail(run_id: str, firm: str) -> dict[str, object]:
        run = _read_run(database, run_id)
        rows = _warehouse_call(read_evaluations, database, run_id, firm=firm)
        if not rows:
            raise HTTPException(status_code=404, detail="Firm not found in this run.")
        evaluated = [item for item in rows if item.status == "evaluated"]
        return {
            "run_id": run_id,
            "firm": firm,
            "methodology_version": METHODOLOGY_VERSION,
            "summary": _ranking_row(firm, evaluated) if evaluated else None,
            "statuses": dict(Counter(item.status for item in rows)),
            "observations": [_public_evaluation(item) for item in rows],
            "run_as_of": run["as_of"],
        }

    @application.get("/api/v1/runs/{run_id}/tickers/{ticker}")
    def ticker_detail(run_id: str, ticker: str) -> dict[str, object]:
        _read_run(database, run_id)
        symbol = ticker.upper()
        rows = _warehouse_call(read_evaluations, database, run_id, ticker=symbol)
        if not rows:
            raise HTTPException(status_code=404, detail="Ticker not found in this run.")
        return {
            "run_id": run_id,
            "ticker": symbol,
            "methodology_version": METHODOLOGY_VERSION,
            "statuses": dict(Counter(item.status for item in rows)),
            "observations": [_public_evaluation(item) for item in rows],
        }

    @application.get("/api/v1/runs/{run_id}/audit/exclusions")
    def exclusions(run_id: str) -> dict[str, object]:
        _read_run(database, run_id)
        rows = _warehouse_call(read_evaluations, database, run_id)
        omitted = [item for item in rows if item.status != "evaluated"]
        return {
            "run_id": run_id,
            "methodology_version": METHODOLOGY_VERSION,
            "counts_by_reason": dict(Counter(item.reason for item in omitted)),
            "observations": [_public_evaluation(item) for item in omitted],
        }

    return application


def _read_run(database: Path, run_id: str) -> dict[str, object]:
    try:
        return read_run_summary(database, run_id)
    except WarehouseError as exc:
        if "not found" in str(exc):
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _warehouse_call(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except WarehouseError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _ranking_row(firm: str, rows: list[Evaluation]) -> dict[str, object]:
    hits = sum(item.hit is True for item in rows)
    low, high = wilson_interval(hits, len(rows))
    hit_days = [item.days_to_target for item in rows if item.days_to_target is not None]
    return {
        "firm": firm,
        "observations": len(rows),
        "hits": hits,
        "hit_rate": _decimal_rate(hits, len(rows)),
        "hit_rate_ci_95_low": float(low),
        "hit_rate_ci_95_high": float(high),
        "mean_terminal_absolute_error_pct": _mean_float(
            rows, "terminal_absolute_error_pct"
        ),
        "median_days_to_hit": int(median(hit_days)) if hit_days else None,
        "mean_horizon_excess_return_pct": _mean_float(rows, "excess_return_pct"),
        "mean_net_strategy_return_pct": _mean_float(rows, "strategy_net_return_pct"),
        "mean_net_strategy_excess_return_pct": _mean_float(
            rows, "strategy_net_excess_return_pct"
        ),
    }


def _public_evaluation(item: Evaluation) -> dict[str, object]:
    row = item.to_row()
    row["hit"] = item.hit
    row["days_to_target"] = item.days_to_target
    return row


def _decimal_rate(numerator: int, denominator: int) -> float:
    return float(Decimal(numerator) / Decimal(denominator))


def _mean_float(rows: list[Evaluation], field: str) -> float | None:
    values = [getattr(item, field) for item in rows if getattr(item, field) is not None]
    if not values:
        return None
    return float(sum(values, Decimal("0")) / Decimal(len(values)))


app = create_app()
