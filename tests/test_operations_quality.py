from __future__ import annotations

import importlib.util
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from targetaudit.models import Evaluation
from targetaudit.operations_quality import (
    build_quality_snapshot,
    render_quality_html,
    render_quality_report,
)
from targetaudit.storage import EvaluationRun, store_evaluation_run


@unittest.skipUnless(importlib.util.find_spec("duckdb"), "optional DuckDB dependency not installed")
class OperationsQualityTests(unittest.TestCase):
    def test_flags_high_exclusion_rate_without_blocking_complete_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "targetaudit.duckdb"
            assets = _assets(root)
            store_evaluation_run(
                database,
                EvaluationRun(
                    run_id="quality-pass",
                    as_of=date(2025, 1, 1),
                    minimum_sample=1,
                    transaction_cost_bps_per_side=Decimal("10"),
                    universe_id="financials",
                    asset_paths=assets,
                    dataset_label="Complete dataset",
                ),
                [_evaluation("pass", "evaluated", "synthetic-demo")],
            )
            store_evaluation_run(
                database,
                EvaluationRun(
                    run_id="review-exclusions",
                    as_of=date(2025, 1, 1),
                    minimum_sample=1,
                    transaction_cost_bps_per_side=Decimal("10"),
                    universe_id="financials",
                    asset_paths=assets,
                    dataset_label="Guarded dataset",
                ),
                [
                    _evaluation("scored", "evaluated", "synthetic-demo"),
                    _evaluation("excluded-one", "excluded", "synthetic-demo"),
                    _evaluation("excluded-two", "excluded", "synthetic-demo"),
                ],
            )

            snapshot = build_quality_snapshot(database, Decimal("0.50"))

            self.assertEqual(snapshot["run_count"], 2)
            self.assertEqual(snapshot["quality_pass_count"], 1)
            self.assertEqual(snapshot["review_required_count"], 1)
            review = next(run for run in snapshot["runs"] if run["run_id"] == "review-exclusions")
            self.assertEqual(review["quality_status"], "review_required")
            self.assertIn("excluded_rate_high", [finding["code"] for finding in review["findings"]])

    def test_blocks_missing_required_inputs_and_provider_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "targetaudit.duckdb"
            targets = root / "targets.csv"
            targets.write_text("targets\n", encoding="utf-8")
            store_evaluation_run(
                database,
                EvaluationRun(
                    run_id="blocked",
                    as_of=date(2025, 1, 1),
                    minimum_sample=1,
                    transaction_cost_bps_per_side=Decimal("10"),
                    universe_id="",
                    asset_paths={"targets": targets},
                    dataset_label="Incomplete dataset",
                ),
                [_evaluation("unlinked", "evaluated", "")],
            )

            snapshot = build_quality_snapshot(database)
            run = snapshot["runs"][0]

            self.assertEqual(run["quality_status"], "blocked")
            self.assertEqual(run["unlinked_observation_count"], 1)
            self.assertEqual(
                {finding["code"] for finding in run["findings"]},
                {"required_input_missing", "provider_lineage_missing"},
            )

    def test_renders_reproducible_quality_report_and_html(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "targetaudit.duckdb"
            store_evaluation_run(
                database,
                EvaluationRun(
                    run_id="render",
                    as_of=date(2025, 1, 1),
                    minimum_sample=1,
                    transaction_cost_bps_per_side=Decimal("10"),
                    universe_id="financials",
                    asset_paths=_assets(root),
                    dataset_label="Rendered quality fixture",
                ),
                [_evaluation("scored", "evaluated", "synthetic-demo")],
            )

            snapshot = build_quality_snapshot(database)
            report = render_quality_report(snapshot, date(2026, 5, 24))
            page = render_quality_html(snapshot, date(2026, 5, 24))

            self.assertIn("# Operations Quality Monitor", report)
            self.assertIn("`quality_pass`", report)
            self.assertIn("does not grant data publication rights", report)
            self.assertIn("Ship evidence,", page)
            self.assertIn("quality_pass", page)

    def test_rejects_invalid_exclusion_threshold(self) -> None:
        with self.assertRaisesRegex(ValueError, "between zero and one"):
            build_quality_snapshot("not-used.duckdb", Decimal("1.01"))


def _assets(root: Path) -> dict[str, Path]:
    targets = root / "targets.csv"
    prices = root / "prices.csv"
    targets.write_text("targets\n", encoding="utf-8")
    prices.write_text("prices\n", encoding="utf-8")
    return {"targets": targets, "prices": prices}


def _evaluation(identifier: str, status: str, provider_id: str) -> Evaluation:
    return Evaluation(
        observation_id=identifier,
        ticker="AAA",
        firm="Example Firm",
        sector="Financials",
        published_date="2023-01-02",
        price_target=Decimal("100"),
        source_url=f"https://example.invalid/{identifier}",
        provider_id=provider_id,
        status=status,
        reason="corporate_action_in_window" if status == "excluded" else "",
    )


if __name__ == "__main__":
    unittest.main()
