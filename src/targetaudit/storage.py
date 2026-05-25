from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

from . import METHODOLOGY_VERSION
from .models import Evaluation


class WarehouseError(ValueError):
    """Raised when an analytical warehouse run cannot be persisted safely."""


@dataclass(frozen=True)
class EvaluationRun:
    run_id: str
    as_of: date
    minimum_sample: int
    transaction_cost_bps_per_side: Decimal
    universe_id: str
    asset_paths: dict[str, str | Path]
    methodology_version: str = METHODOLOGY_VERSION
    dataset_label: str = ""


def generated_run_id(as_of: date) -> str:
    return f"evaluate-{as_of.isoformat()}-{uuid4().hex[:12]}"


def store_evaluation_run(
    database_path: str | Path,
    run: EvaluationRun,
    evaluations: list[Evaluation],
) -> None:
    if not evaluations:
        raise WarehouseError("No evaluations were provided for warehouse storage.")
    if not run.run_id.strip():
        raise WarehouseError("Warehouse run ID cannot be blank.")
    if not run.methodology_version.strip():
        raise WarehouseError("Warehouse methodology version cannot be blank.")
    connection = _connect(database_path)
    try:
        _initialize_schema(connection)
        if connection.execute(
            "SELECT 1 FROM evaluation_runs WHERE run_id = ?", [run.run_id]
        ).fetchone():
            raise WarehouseError(f"Warehouse run already exists: {run.run_id}")
        assets = [_asset_row(run.run_id, role, path) for role, path in run.asset_paths.items()]
        dataset_fingerprint = _dataset_fingerprint(assets)
        status_counts = {
            status: sum(item.status == status for item in evaluations)
            for status in ("evaluated", "excluded", "pending")
        }
        connection.execute("BEGIN TRANSACTION")
        connection.execute(
            """
            INSERT INTO evaluation_runs (
                run_id, created_at_utc, as_of, minimum_sample,
                transaction_cost_bps_per_side, universe_id, observation_count,
                evaluated_count, excluded_count, pending_count, methodology_version,
                dataset_label, dataset_fingerprint
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                run.run_id,
                datetime.now(timezone.utc).replace(tzinfo=None),
                run.as_of,
                run.minimum_sample,
                run.transaction_cost_bps_per_side,
                run.universe_id,
                len(evaluations),
                status_counts["evaluated"],
                status_counts["excluded"],
                status_counts["pending"],
                run.methodology_version,
                run.dataset_label,
                dataset_fingerprint,
            ],
        )
        if assets:
            connection.executemany(
                """
                INSERT INTO run_assets (
                    run_id, asset_role, asset_path, sha256, byte_size
                ) VALUES (?, ?, ?, ?, ?)
                """,
                assets,
            )
        connection.executemany(
            f"INSERT INTO evaluations ({', '.join(_EVALUATION_COLUMNS)}) "
            f"VALUES ({', '.join('?' for _ in _EVALUATION_COLUMNS)})",
            [
                _evaluation_row(run.run_id, row_number, item)
                for row_number, item in enumerate(evaluations, start=1)
            ],
        )
        connection.execute("COMMIT")
    except Exception:
        try:
            connection.execute("ROLLBACK")
        except Exception:
            pass
        raise
    finally:
        connection.close()


def read_run_summary(database_path: str | Path, run_id: str) -> dict[str, Any]:
    connection = _connect_reader(database_path)
    try:
        row = connection.execute(
            f"SELECT {', '.join(_run_select_columns(connection))} "
            "FROM evaluation_runs WHERE run_id = ?",
            [run_id],
        ).fetchone()
        if row is None:
            raise WarehouseError(f"Warehouse run not found: {run_id}")
        return _run_summary(row)
    finally:
        connection.close()


def list_run_summaries(database_path: str | Path) -> list[dict[str, Any]]:
    connection = _connect_reader(database_path)
    try:
        rows = connection.execute(
            f"SELECT {', '.join(_run_select_columns(connection))} "
            "FROM evaluation_runs ORDER BY created_at_utc DESC, run_id DESC"
        ).fetchall()
        return [_run_summary(row) for row in rows]
    finally:
        connection.close()


def read_run_assets(database_path: str | Path, run_id: str) -> list[dict[str, Any]]:
    connection = _connect_reader(database_path)
    try:
        rows = connection.execute(
            """
            SELECT asset_role, asset_path, sha256, byte_size
            FROM run_assets
            WHERE run_id = ?
            ORDER BY asset_role
            """,
            [run_id],
        ).fetchall()
        return [
            dict(zip(("asset_role", "asset_path", "sha256", "byte_size"), row))
            for row in rows
        ]
    finally:
        connection.close()


def read_evaluations(
    database_path: str | Path,
    run_id: str,
    *,
    firm: str = "",
    ticker: str = "",
    status: str = "",
) -> list[Evaluation]:
    connection = _connect_reader(database_path)
    try:
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info('evaluations')").fetchall()
        }
        selected_columns = [
            "'' AS provider_id"
            if column == "provider_id" and column not in columns
            else column
            for column in _EVALUATION_COLUMNS[2:]
        ]
        query = f"""
            SELECT {', '.join(selected_columns)}
            FROM evaluations
            WHERE run_id = ?
        """
        parameters = [run_id]
        if firm:
            query += " AND firm = ?"
            parameters.append(firm)
        if ticker:
            query += " AND ticker = ?"
            parameters.append(ticker.upper())
        if status:
            query += " AND status = ?"
            parameters.append(status)
        query += " ORDER BY row_number"
        rows = connection.execute(query, parameters).fetchall()
        return [_evaluation_from_row(row) for row in rows]
    finally:
        connection.close()


def _connect(database_path: str | Path) -> Any:
    try:
        import duckdb
    except ImportError as exc:
        raise WarehouseError(
            "DuckDB support is not installed. Install the optional dependency "
            "with: python3 -m pip install -e '.[warehouse]'"
        ) from exc
    destination = Path(database_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(destination))


def _connect_reader(database_path: str | Path) -> Any:
    try:
        import duckdb
    except ImportError as exc:
        raise WarehouseError(
            "DuckDB support is not installed. Install the optional dependency "
            "with: python3 -m pip install -e '.[warehouse]'"
        ) from exc
    source = Path(database_path)
    if not source.is_file():
        raise WarehouseError(f"Warehouse database not found: {source}")
    try:
        return duckdb.connect(str(source), read_only=True)
    except Exception as exc:
        raise WarehouseError(f"Unable to open warehouse database: {source}") from exc


def _initialize_schema(connection: Any) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluation_runs (
            run_id VARCHAR PRIMARY KEY,
            created_at_utc TIMESTAMP NOT NULL,
            as_of DATE NOT NULL,
            minimum_sample INTEGER NOT NULL,
            transaction_cost_bps_per_side DECIMAL(18, 6) NOT NULL,
            universe_id VARCHAR NOT NULL,
            observation_count INTEGER NOT NULL,
            evaluated_count INTEGER NOT NULL,
            excluded_count INTEGER NOT NULL,
            pending_count INTEGER NOT NULL,
            methodology_version VARCHAR NOT NULL,
            dataset_label VARCHAR NOT NULL,
            dataset_fingerprint VARCHAR NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS run_assets (
            run_id VARCHAR NOT NULL,
            asset_role VARCHAR NOT NULL,
            asset_path VARCHAR NOT NULL,
            sha256 VARCHAR NOT NULL,
            byte_size BIGINT NOT NULL,
            PRIMARY KEY (run_id, asset_role)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluations (
            run_id VARCHAR NOT NULL,
            row_number INTEGER NOT NULL,
            observation_id VARCHAR NOT NULL,
            ticker VARCHAR NOT NULL,
            firm VARCHAR NOT NULL,
            sector VARCHAR NOT NULL,
            published_date DATE,
            price_target DECIMAL(24, 6),
            source_url VARCHAR NOT NULL,
            provider_id VARCHAR NOT NULL,
            status VARCHAR NOT NULL,
            reason VARCHAR NOT NULL,
            direction VARCHAR NOT NULL,
            reference_date DATE,
            reference_price DECIMAL(24, 6),
            entry_date DATE,
            entry_price DECIMAL(24, 6),
            expiry_date DATE,
            terminal_date DATE,
            terminal_price DECIMAL(24, 6),
            hit BOOLEAN,
            hit_date DATE,
            days_to_target INTEGER,
            terminal_absolute_error_pct DECIMAL(24, 12),
            directional_return_pct DECIMAL(24, 12),
            benchmark_symbol VARCHAR NOT NULL,
            benchmark_directional_return_pct DECIMAL(24, 12),
            excess_return_pct DECIMAL(24, 12),
            historical_universe_id VARCHAR NOT NULL,
            historical_universe_source_url VARCHAR NOT NULL,
            superseded_by_observation_id VARCHAR NOT NULL,
            superseded_on DATE,
            strategy_exit_reason VARCHAR NOT NULL,
            strategy_exit_date DATE,
            strategy_exit_price DECIMAL(24, 6),
            strategy_gross_return_pct DECIMAL(24, 12),
            transaction_cost_bps_per_side DECIMAL(18, 6),
            strategy_net_return_pct DECIMAL(24, 12),
            benchmark_strategy_net_return_pct DECIMAL(24, 12),
            strategy_net_excess_return_pct DECIMAL(24, 12),
            PRIMARY KEY (run_id, row_number)
        )
        """
    )
    connection.execute(
        "ALTER TABLE evaluations ADD COLUMN IF NOT EXISTS provider_id VARCHAR DEFAULT ''"
    )
    connection.execute(
        "ALTER TABLE evaluation_runs ADD COLUMN IF NOT EXISTS methodology_version VARCHAR DEFAULT ''"
    )
    connection.execute(
        "ALTER TABLE evaluation_runs ADD COLUMN IF NOT EXISTS dataset_label VARCHAR DEFAULT ''"
    )
    connection.execute(
        "ALTER TABLE evaluation_runs ADD COLUMN IF NOT EXISTS dataset_fingerprint VARCHAR DEFAULT ''"
    )


def _asset_row(run_id: str, role: str, asset_path: str | Path) -> list[Any]:
    path = Path(asset_path)
    if not path.is_file():
        raise WarehouseError(f"Warehouse asset is not a readable file: {path}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return [run_id, role, str(path), digest, path.stat().st_size]


def _dataset_fingerprint(assets: list[list[Any]]) -> str:
    input_assets = sorted(
        (asset[1], asset[3], asset[4])
        for asset in assets
        if asset[1] not in _DERIVED_ASSET_ROLES
    )
    manifest = "\n".join(f"{role}\t{digest}\t{size}" for role, digest, size in input_assets)
    return hashlib.sha256(manifest.encode("utf-8")).hexdigest()


def _optional_date(raw: str) -> date | None:
    return date.fromisoformat(raw) if raw else None


def _evaluation_row(run_id: str, row_number: int, item: Evaluation) -> list[Any]:
    return [
        run_id,
        row_number,
        item.observation_id,
        item.ticker,
        item.firm,
        item.sector,
        _optional_date(item.published_date),
        item.price_target,
        item.source_url,
        item.provider_id,
        item.status,
        item.reason,
        item.direction,
        _optional_date(item.reference_date),
        item.reference_price,
        _optional_date(item.entry_date),
        item.entry_price,
        _optional_date(item.expiry_date),
        _optional_date(item.terminal_date),
        item.terminal_price,
        item.hit,
        _optional_date(item.hit_date),
        item.days_to_target,
        item.terminal_absolute_error_pct,
        item.directional_return_pct,
        item.benchmark_symbol,
        item.benchmark_directional_return_pct,
        item.excess_return_pct,
        item.historical_universe_id,
        item.historical_universe_source_url,
        item.superseded_by_observation_id,
        _optional_date(item.superseded_on),
        item.strategy_exit_reason,
        _optional_date(item.strategy_exit_date),
        item.strategy_exit_price,
        item.strategy_gross_return_pct,
        item.transaction_cost_bps_per_side,
        item.strategy_net_return_pct,
        item.benchmark_strategy_net_return_pct,
        item.strategy_net_excess_return_pct,
    ]


def _run_summary(row: tuple[Any, ...]) -> dict[str, Any]:
    return dict(zip(_RUN_COLUMNS, row))


def _run_select_columns(connection: Any) -> list[str]:
    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info('evaluation_runs')").fetchall()
    }
    optional = {"methodology_version", "dataset_label", "dataset_fingerprint"}
    return [
        f"'' AS {column}" if column in optional and column not in columns else column
        for column in _RUN_COLUMNS
    ]


def _evaluation_from_row(row: tuple[Any, ...]) -> Evaluation:
    values = dict(zip(_EVALUATION_COLUMNS[2:], row))
    for name in (
        "published_date",
        "reference_date",
        "entry_date",
        "expiry_date",
        "terminal_date",
        "hit_date",
        "superseded_on",
        "strategy_exit_date",
    ):
        values[name] = values[name].isoformat() if values[name] is not None else ""
    return Evaluation(**values)


_EVALUATION_COLUMNS = [
    "run_id",
    "row_number",
    "observation_id",
    "ticker",
    "firm",
    "sector",
    "published_date",
    "price_target",
    "source_url",
    "provider_id",
    "status",
    "reason",
    "direction",
    "reference_date",
    "reference_price",
    "entry_date",
    "entry_price",
    "expiry_date",
    "terminal_date",
    "terminal_price",
    "hit",
    "hit_date",
    "days_to_target",
    "terminal_absolute_error_pct",
    "directional_return_pct",
    "benchmark_symbol",
    "benchmark_directional_return_pct",
    "excess_return_pct",
    "historical_universe_id",
    "historical_universe_source_url",
    "superseded_by_observation_id",
    "superseded_on",
    "strategy_exit_reason",
    "strategy_exit_date",
    "strategy_exit_price",
    "strategy_gross_return_pct",
    "transaction_cost_bps_per_side",
    "strategy_net_return_pct",
    "benchmark_strategy_net_return_pct",
    "strategy_net_excess_return_pct",
]

_RUN_COLUMNS = [
    "run_id",
    "created_at_utc",
    "as_of",
    "minimum_sample",
    "transaction_cost_bps_per_side",
    "universe_id",
    "observation_count",
    "evaluated_count",
    "excluded_count",
    "pending_count",
    "methodology_version",
    "dataset_label",
    "dataset_fingerprint",
]

_DERIVED_ASSET_ROLES = {"evaluations_csv", "report_markdown"}
