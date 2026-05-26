from __future__ import annotations

import importlib.util
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from marketwitness.models import Evaluation
from marketwitness.storage import (
    EvaluationRun,
    WarehouseError,
    read_evaluations,
    read_run_assets,
    read_run_summary,
    store_evaluation_run,
)


@unittest.skipUnless(importlib.util.find_spec("duckdb"), "optional DuckDB dependency not installed")
class StorageTests(unittest.TestCase):
    def test_persists_run_results_and_hashed_assets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target_file = root / "targets.csv"
            target_file.write_text("example targets\n", encoding="utf-8")
            database = root / "marketwitness.duckdb"
            evaluations = [
                Evaluation(
                    observation_id="one",
                    ticker="AAA",
                    firm="Example Firm",
                    sector="Financials",
                    published_date="2023-01-02",
                    price_target=Decimal("120"),
                    source_url="https://example.invalid/one",
                    status="evaluated",
                    provider_id="synthetic-demo",
                    direction="up",
                    hit=True,
                    days_to_target=10,
                    strategy_exit_reason="target_hit_limit",
                    strategy_exit_date="2023-01-12",
                    strategy_exit_price=Decimal("120"),
                    strategy_net_return_pct=Decimal("0.18"),
                ),
                Evaluation(
                    observation_id="two",
                    ticker="BBB",
                    firm="Example Firm",
                    sector="Financials",
                    published_date="2023-01-02",
                    price_target=Decimal("100"),
                    source_url="https://example.invalid/two",
                    status="excluded",
                    reason="missing_reference_price",
                ),
            ]

            store_evaluation_run(
                database,
                EvaluationRun(
                    run_id="sample-run",
                    as_of=date(2025, 1, 1),
                    minimum_sample=1,
                    transaction_cost_bps_per_side=Decimal("10"),
                    universe_id="financials-demo",
                    asset_paths={"targets": target_file},
                    asset_provider_ids={"targets": "synthetic-demo"},
                    dataset_label="Auditable fixture",
                ),
                evaluations,
            )

            summary = read_run_summary(database, "sample-run")
            self.assertEqual(summary["observation_count"], 2)
            self.assertEqual(summary["evaluated_count"], 1)
            self.assertEqual(summary["excluded_count"], 1)
            self.assertEqual(summary["methodology_version"], "0.3.3")
            self.assertEqual(summary["dataset_label"], "Auditable fixture")
            self.assertEqual(len(summary["dataset_fingerprint"]), 64)

            import duckdb

            connection = duckdb.connect(str(database), read_only=True)
            try:
                saved_asset = connection.execute(
                    "SELECT asset_role, length(sha256), provider_id FROM run_assets"
                ).fetchone()
                saved_result = connection.execute(
                    "SELECT hit, strategy_net_return_pct, provider_id FROM evaluations "
                    "WHERE observation_id = 'one'"
                ).fetchone()
            finally:
                connection.close()
            self.assertEqual(saved_asset, ("targets", 64, "synthetic-demo"))
            self.assertEqual(
                saved_result, (True, Decimal("0.180000000000"), "synthetic-demo")
            )

    def test_refuses_to_overwrite_existing_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "marketwitness.duckdb"
            run = EvaluationRun(
                run_id="stable-run",
                as_of=date(2025, 1, 1),
                minimum_sample=1,
                transaction_cost_bps_per_side=Decimal("10"),
                universe_id="",
                asset_paths={},
            )
            evaluations = [
                Evaluation(
                    observation_id="one",
                    ticker="AAA",
                    firm="Firm",
                    sector="",
                    published_date="",
                    price_target=None,
                    source_url="",
                    status="excluded",
                    reason="invalid",
                )
            ]

            store_evaluation_run(database, run, evaluations)

            with self.assertRaisesRegex(WarehouseError, "already exists"):
                store_evaluation_run(database, run, evaluations)

    def test_dataset_fingerprint_excludes_generated_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            targets = root / "targets.csv"
            first_output = root / "first-output.csv"
            second_output = root / "second-output.csv"
            targets.write_text("same input\n", encoding="utf-8")
            first_output.write_text("result one\n", encoding="utf-8")
            second_output.write_text("result two\n", encoding="utf-8")
            database = root / "marketwitness.duckdb"
            evaluation = Evaluation(
                observation_id="one",
                ticker="AAA",
                firm="Firm",
                sector="",
                published_date="",
                price_target=None,
                source_url="",
                status="excluded",
                reason="invalid",
            )
            for run_id, output in (("first", first_output), ("second", second_output)):
                store_evaluation_run(
                    database,
                    EvaluationRun(
                        run_id=run_id,
                        as_of=date(2025, 1, 1),
                        minimum_sample=1,
                        transaction_cost_bps_per_side=Decimal("10"),
                        universe_id="",
                        asset_paths={"targets": targets, "evaluations_csv": output},
                    ),
                    [evaluation],
                )

            self.assertEqual(
                read_run_summary(database, "first")["dataset_fingerprint"],
                read_run_summary(database, "second")["dataset_fingerprint"],
            )

    def test_dataset_fingerprint_includes_declared_asset_provider(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            targets = root / "targets.csv"
            targets.write_text("same input\n", encoding="utf-8")
            database = root / "marketwitness.duckdb"
            evaluation = Evaluation(
                observation_id="one",
                ticker="AAA",
                firm="Firm",
                sector="",
                published_date="",
                price_target=None,
                source_url="",
                status="excluded",
                reason="invalid",
            )
            for run_id, provider_id in (("first", "provider-one"), ("second", "provider-two")):
                store_evaluation_run(
                    database,
                    EvaluationRun(
                        run_id=run_id,
                        as_of=date(2025, 1, 1),
                        minimum_sample=1,
                        transaction_cost_bps_per_side=Decimal("10"),
                        universe_id="",
                        asset_paths={"targets": targets},
                        asset_provider_ids={"targets": provider_id},
                    ),
                    [evaluation],
                )

            self.assertNotEqual(
                read_run_summary(database, "first")["dataset_fingerprint"],
                read_run_summary(database, "second")["dataset_fingerprint"],
            )

    def test_reads_existing_database_created_before_provider_lineage_column(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "marketwitness.duckdb"
            run = EvaluationRun(
                run_id="old-schema",
                as_of=date(2025, 1, 1),
                minimum_sample=1,
                transaction_cost_bps_per_side=Decimal("10"),
                universe_id="",
                asset_paths={},
            )
            store_evaluation_run(
                database,
                run,
                [
                    Evaluation(
                        observation_id="legacy",
                        ticker="AAA",
                        firm="Firm",
                        sector="",
                        published_date="2023-01-02",
                        price_target=Decimal("100"),
                        source_url="https://example.invalid/legacy",
                        status="evaluated",
                        provider_id="synthetic-demo",
                    )
                ],
            )

            import duckdb

            connection = duckdb.connect(str(database))
            try:
                connection.execute("ALTER TABLE evaluations DROP COLUMN provider_id")
                connection.execute("ALTER TABLE evaluation_runs DROP COLUMN methodology_version")
                connection.execute("ALTER TABLE evaluation_runs DROP COLUMN dataset_label")
                connection.execute("ALTER TABLE evaluation_runs DROP COLUMN dataset_fingerprint")
            finally:
                connection.close()

            legacy = read_evaluations(database, "old-schema")[0]
            self.assertEqual(legacy.provider_id, "")
            legacy_run = read_run_summary(database, "old-schema")
            self.assertEqual(legacy_run["methodology_version"], "")
            self.assertEqual(legacy_run["dataset_fingerprint"], "")

    def test_reads_run_assets_created_before_asset_provider_lineage_column(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            targets = root / "targets.csv"
            targets.write_text("targets\n", encoding="utf-8")
            database = root / "marketwitness.duckdb"
            store_evaluation_run(
                database,
                EvaluationRun(
                    run_id="legacy-assets",
                    as_of=date(2025, 1, 1),
                    minimum_sample=1,
                    transaction_cost_bps_per_side=Decimal("10"),
                    universe_id="",
                    asset_paths={"targets": targets},
                    asset_provider_ids={"targets": "synthetic-demo"},
                ),
                [
                    Evaluation(
                        observation_id="one",
                        ticker="AAA",
                        firm="Firm",
                        sector="",
                        published_date="2023-01-02",
                        price_target=Decimal("100"),
                        source_url="https://example.invalid/one",
                        status="evaluated",
                        provider_id="synthetic-demo",
                    )
                ],
            )

            import duckdb

            connection = duckdb.connect(str(database))
            try:
                connection.execute("ALTER TABLE run_assets DROP COLUMN provider_id")
            finally:
                connection.close()

            self.assertEqual(read_run_assets(database, "legacy-assets")[0]["provider_id"], "")


if __name__ == "__main__":
    unittest.main()
