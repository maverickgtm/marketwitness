from __future__ import annotations

import csv
import io
import os
import re
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path
from statistics import median
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response

from . import METHODOLOGY_VERSION, __version__
from .dashboard_web import (
    financials_scorecard_html,
    operations_quality_html,
    release_center_html,
    scorecard_readiness_html,
    source_governance_html,
)
from .models import Evaluation
from .operations_quality import build_quality_snapshot
from .release_center import build_release_decision
from .reporting import wilson_interval
from .scorecard_readiness import build_scorecard_readiness
from .source_registry import SourceProvider, SourceRegistryDataError, load_source_registry
from .storage import (
    WarehouseError,
    list_run_summaries,
    read_evaluations,
    read_run_assets,
    read_run_summary,
)

DEFAULT_DATABASE_PATH = "build/live/targetaudit.duckdb"
DEFAULT_SOURCE_REGISTRY_PATH = "data/samples/source_registry.csv"


def create_app(
    database_path: str | Path | None = None,
    source_registry_path: str | Path | None = None,
) -> FastAPI:
    database = Path(
        database_path or os.environ.get("TARGETAUDIT_DATABASE", DEFAULT_DATABASE_PATH)
    )
    registry = Path(
        source_registry_path
        or os.environ.get("TARGETAUDIT_SOURCE_REGISTRY", DEFAULT_SOURCE_REGISTRY_PATH)
    )
    application = FastAPI(
        title="TargetAudit API",
        version=__version__,
        description="Read-only API for auditable analyst target research runs.",
    )

    @application.get("/", response_class=HTMLResponse, include_in_schema=False)
    def scorecard_home() -> str:
        return financials_scorecard_html()

    @application.get(
        "/dashboard/financials", response_class=HTMLResponse, include_in_schema=False
    )
    def scorecard() -> str:
        return financials_scorecard_html()

    @application.get(
        "/dashboard/governance", response_class=HTMLResponse, include_in_schema=False
    )
    def source_governance() -> str:
        return source_governance_html()

    @application.get(
        "/dashboard/operations", response_class=HTMLResponse, include_in_schema=False
    )
    def operations_quality() -> str:
        return operations_quality_html()

    @application.get(
        "/dashboard/readiness", response_class=HTMLResponse, include_in_schema=False
    )
    def scorecard_readiness() -> str:
        return scorecard_readiness_html()

    @application.get(
        "/dashboard/release", response_class=HTMLResponse, include_in_schema=False
    )
    def release_center() -> str:
        return release_center_html()

    @application.get("/api/v1/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "service": "targetaudit-api",
            "methodology_version": METHODOLOGY_VERSION,
            "database_available": database.is_file(),
            "source_registry_available": registry.is_file(),
        }

    @application.get("/api/v1/governance/sources")
    def governance_sources(
        deployment_state: str = "",
        data_class: str = "",
    ) -> dict[str, object]:
        providers = _read_sources(registry)
        all_providers = providers
        if deployment_state:
            providers = [
                item for item in providers if item.deployment_state == deployment_state
            ]
        if data_class:
            providers = [
                item for item in providers if item.data_class.lower() == data_class.lower()
            ]
        deployment = Counter(item.deployment_state for item in all_providers)
        integration = Counter(item.integration_status for item in all_providers)
        return {
            "reviewed_as_of": max(item.reviewed_on for item in all_providers).isoformat()
            if all_providers
            else None,
            "provider_count": len(all_providers),
            "implemented_count": integration["implemented"],
            "open_review_count": (
                deployment["review_required"] + deployment["license_required"]
            ),
            "manual_only_count": deployment["manual_only"],
            "blocked_count": deployment["blocked"],
            "deployment_states": sorted({item.deployment_state for item in all_providers}),
            "data_classes": sorted({item.data_class for item in all_providers}),
            "sources": [_public_source(item) for item in providers],
        }

    @application.get("/api/v1/readiness/scorecard")
    def readiness_scorecard() -> dict[str, object]:
        providers = _read_sources(registry)
        try:
            as_of = max((item.reviewed_on for item in providers), default=date.today())
            return build_scorecard_readiness(providers, as_of)
        except SourceRegistryDataError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @application.get("/api/v1/runs")
    def runs() -> list[dict[str, object]]:
        return _warehouse_call(list_run_summaries, database)

    @application.get("/api/v1/operations/quality")
    def quality_monitor(
        maximum_excluded_rate: Decimal = Query(default=Decimal("0.50"), ge=0, le=1),
        run_id: str = "",
        public_release: bool = False,
    ) -> dict[str, object]:
        if run_id:
            _read_run(database, run_id)
        return _warehouse_call(
            build_quality_snapshot, database, maximum_excluded_rate, run_id, public_release
        )

    @application.get("/api/v1/releases/scorecard")
    def release_scorecard(
        run_id: str,
        maximum_excluded_rate: Decimal = Query(default=Decimal("0.50"), ge=0, le=1),
    ) -> dict[str, object]:
        _read_run(database, run_id)
        providers = _read_sources(registry)
        try:
            as_of = max((item.reviewed_on for item in providers), default=date.today())
            return _warehouse_call(
                build_release_decision,
                providers,
                database,
                run_id,
                as_of,
                maximum_excluded_rate,
            )
        except SourceRegistryDataError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @application.get("/api/v1/runs/compare")
    def compare_runs(left_run_id: str, right_run_id: str) -> dict[str, object]:
        left = _read_run(database, left_run_id)
        right = _read_run(database, right_run_id)
        same_methodology = bool(
            left["methodology_version"]
            and left["methodology_version"] == right["methodology_version"]
        )
        same_dataset = bool(
            left["dataset_fingerprint"]
            and left["dataset_fingerprint"] == right["dataset_fingerprint"]
        )
        if same_methodology and same_dataset:
            comparability = "same_evidence_and_methodology"
        elif same_methodology:
            comparability = "same_methodology_different_dataset"
        else:
            comparability = "methodology_changed"
        return {
            "left": left,
            "right": right,
            "same_methodology": same_methodology,
            "same_dataset": same_dataset,
            "comparability": comparability,
            "deltas": {
                key: right[key] - left[key]
                for key in ("observation_count", "evaluated_count", "excluded_count", "pending_count")
            },
        }

    @application.get("/api/v1/runs/{run_id}")
    def run_detail(run_id: str) -> dict[str, object]:
        run = _read_run(database, run_id)
        run["assets"] = [
            {
                "asset_role": item["asset_role"],
                "sha256": item["sha256"],
                "byte_size": item["byte_size"],
                "provider_id": item["provider_id"],
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
        return _firm_ranking_payload(database, run_id, minimum_sample, sector, direction)

    @application.get("/api/v1/runs/{run_id}/export/evaluations.csv")
    def evaluations_export(run_id: str) -> Response:
        _read_run(database, run_id)
        rows = _warehouse_call(read_evaluations, database, run_id)
        exported = [_public_evaluation(item) for item in rows]
        return _csv_download(
            f"targetaudit-{_safe_filename(run_id)}-evaluations.csv",
            exported,
            list(exported[0]) if exported else [],
        )

    @application.get("/api/v1/runs/{run_id}/export/rankings-firms.csv")
    def firm_ranking_export(
        run_id: str,
        minimum_sample: Optional[int] = Query(default=None, ge=1),
        sector: str = "",
        direction: str = Query(default="", pattern="^(|up|down)$"),
    ) -> Response:
        result = _firm_ranking_payload(database, run_id, minimum_sample, sector, direction)
        rows = result["ranking"]
        fields = [
            "firm",
            "observations",
            "hits",
            "hit_rate",
            "hit_rate_ci_95_low",
            "hit_rate_ci_95_high",
            "mean_terminal_absolute_error_pct",
            "median_days_to_hit",
            "mean_horizon_excess_return_pct",
            "mean_net_strategy_return_pct",
            "mean_net_strategy_excess_return_pct",
        ]
        return _csv_download(
            f"targetaudit-{_safe_filename(run_id)}-firm-ranking.csv", rows, fields
        )

    @application.get("/api/v1/runs/{run_id}/facets")
    def facets(run_id: str) -> dict[str, object]:
        run = _read_run(database, run_id)
        rows = _warehouse_call(read_evaluations, database, run_id)
        return {
            "run_id": run_id,
            "methodology_version": run["methodology_version"],
            "sectors": sorted({item.sector or "Unclassified" for item in rows}),
            "directions": sorted({item.direction for item in rows if item.direction}),
            "firms": sorted({item.firm for item in rows}),
            "tickers": sorted({item.ticker for item in rows}),
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
            "methodology_version": run["methodology_version"],
            "summary": _ranking_row(firm, evaluated) if evaluated else None,
            "statuses": dict(Counter(item.status for item in rows)),
            "observations": [_public_evaluation(item) for item in rows],
            "run_as_of": run["as_of"],
        }

    @application.get("/api/v1/runs/{run_id}/tickers/{ticker}")
    def ticker_detail(run_id: str, ticker: str) -> dict[str, object]:
        run = _read_run(database, run_id)
        symbol = ticker.upper()
        rows = _warehouse_call(read_evaluations, database, run_id, ticker=symbol)
        if not rows:
            raise HTTPException(status_code=404, detail="Ticker not found in this run.")
        return {
            "run_id": run_id,
            "ticker": symbol,
            "methodology_version": run["methodology_version"],
            "statuses": dict(Counter(item.status for item in rows)),
            "observations": [_public_evaluation(item) for item in rows],
        }

    @application.get("/api/v1/runs/{run_id}/tickers/{ticker}/timeline")
    def ticker_timeline(run_id: str, ticker: str) -> dict[str, object]:
        run = _read_run(database, run_id)
        symbol = ticker.upper()
        rows = _warehouse_call(read_evaluations, database, run_id, ticker=symbol)
        if not rows:
            raise HTTPException(status_code=404, detail="Ticker not found in this run.")
        return {
            "run_id": run_id,
            "ticker": symbol,
            "methodology_version": run["methodology_version"],
            "series_type": "evaluation_evidence_points",
            "limitation": (
                "Retained evaluation milestones only; this is not a daily "
                "market-price series."
            ),
            "observations": [_timeline_observation(item) for item in rows],
        }

    @application.get("/api/v1/runs/{run_id}/audit/exclusions")
    def exclusions(run_id: str) -> dict[str, object]:
        run = _read_run(database, run_id)
        rows = _warehouse_call(read_evaluations, database, run_id)
        omitted = [item for item in rows if item.status != "evaluated"]
        return {
            "run_id": run_id,
            "methodology_version": run["methodology_version"],
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


def _read_sources(registry: Path) -> list[SourceProvider]:
    try:
        return load_source_registry(registry)
    except (OSError, SourceRegistryDataError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _public_source(item: SourceProvider) -> dict[str, object]:
    return {
        "provider_id": item.provider_id,
        "provider_name": item.provider_name,
        "data_class": item.data_class,
        "access_model": item.access_model,
        "integration_status": item.integration_status,
        "license_status": item.license_status,
        "publication_policy": item.publication_policy,
        "deployment_state": item.deployment_state,
        "official_url": item.official_url,
        "reference_url": item.reference_url,
        "reviewed_on": item.reviewed_on.isoformat(),
        "review_note": item.review_note,
    }


def _firm_ranking_payload(
    database: Path,
    run_id: str,
    minimum_sample: Optional[int],
    sector: str,
    direction: str,
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
        "methodology_version": run["methodology_version"],
        "minimum_sample": threshold,
        "sector": sector or None,
        "direction": direction or None,
        "ranking": ranking,
    }


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


def _timeline_observation(item: Evaluation) -> dict[str, object]:
    milestones = [
        ("Reference close", item.reference_date, item.reference_price, "reference"),
        ("Entry close", item.entry_date, item.entry_price, "entry"),
        ("Target hit", item.hit_date, item.price_target if item.hit else None, "hit"),
        (
            "Strategy exit",
            item.strategy_exit_date,
            item.strategy_exit_price,
            "exit",
        ),
        ("Terminal close", item.terminal_date, item.terminal_price, "terminal"),
    ]
    points: list[dict[str, object]] = []
    for label, dated, value, kind in milestones:
        if not dated or value is None:
            continue
        existing = next(
            (
                point
                for point in points
                if point["date"] == dated and point["value"] == float(value)
            ),
            None,
        )
        if existing:
            existing["label"] = f'{existing["label"]} / {label}'
            if kind == "hit":
                existing["kind"] = kind
        else:
            points.append(
                {"label": label, "date": dated, "value": float(value), "kind": kind}
            )
    return {
        "observation_id": item.observation_id,
        "firm": item.firm,
        "status": item.status,
        "reason": item.reason,
        "published_date": item.published_date,
        "price_target": float(item.price_target) if item.price_target is not None else None,
        "target_end_date": item.expiry_date or item.terminal_date,
        "points": points,
    }


def _safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-") or "run"


def _csv_download(
    filename: str, rows: list[dict[str, object]], fieldnames: list[str]
) -> Response:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    if fieldnames:
        writer.writeheader()
        writer.writerows(rows)
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _decimal_rate(numerator: int, denominator: int) -> float:
    return float(Decimal(numerator) / Decimal(denominator))


def _mean_float(rows: list[Evaluation], field: str) -> float | None:
    values = [getattr(item, field) for item in rows if getattr(item, field) is not None]
    if not values:
        return None
    return float(sum(values, Decimal("0")) / Decimal(len(values)))


app = create_app()
