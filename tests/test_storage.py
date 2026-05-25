from __future__ import annotations

import importlib.util
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from targetaudit.models import Evaluation
from targetaudit.storage import EvaluationRun, WarehouseError, read_run_summary, store_evaluation_run


@unittest.skipUnless(importlib.util.find_spec("duckdb"), "optional DuckDB dependency not installed")
class StorageTests(unittest.TestCase):
    def test_persists_run_results_and_hashed_assets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target_file = root / "targets.csv"
            target_file.write_text("example targets\n", encoding="utf-8")
            database = root / "targetaudit.duckdb"
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
                ),
                evaluations,
            )

            summary = read_run_summary(database, "sample-run")
            self.assertEqual(summary["observation_count"], 2)
            self.assertEqual(summary["evaluated_count"], 1)
            self.assertEqual(summary["excluded_count"], 1)

            import duckdb

            connection = duckdb.connect(str(database), read_only=True)
            try:
                saved_asset = connection.execute(
                    "SELECT asset_role, length(sha256) FROM run_assets"
                ).fetchone()
                saved_result = connection.execute(
                    "SELECT hit, strategy_net_return_pct FROM evaluations "
                    "WHERE observation_id = 'one'"
                ).fetchone()
            finally:
                connection.close()
            self.assertEqual(saved_asset, ("targets", 64))
            self.assertEqual(saved_result, (True, Decimal("0.180000000000")))

    def test_refuses_to_overwrite_existing_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "targetaudit.duckdb"
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


if __name__ == "__main__":
    unittest.main()
