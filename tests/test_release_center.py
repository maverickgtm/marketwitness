from __future__ import annotations

import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from marketwitness.cli import main
from marketwitness.models import Evaluation
from marketwitness.release_center import (
    build_release_decision,
    render_release_html,
    render_release_report,
)
from marketwitness.source_registry import SourceProvider, load_source_registry
from marketwitness.storage import EvaluationRun, store_evaluation_run


@unittest.skipUnless(importlib.util.find_spec("duckdb"), "optional DuckDB dependency not installed")
class ReleaseCenterTests(unittest.TestCase):
    def test_blocks_complete_demo_run_when_source_rights_and_lineage_are_not_public(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = _stored_run(Path(directory), "synthetic-demo")
            providers = load_source_registry(Path("data/samples/source_registry.csv"))

            snapshot = build_release_decision(
                providers, database, "candidate", date(2026, 5, 25)
            )

            self.assertFalse(snapshot["release_ready"])
            self.assertEqual(snapshot["release_status"], "blocked")
            self.assertEqual(snapshot["source_gate_status"], "blocked")
            self.assertEqual(snapshot["quality_gate_status"], "pass")
            self.assertEqual(snapshot["lineage_gate_status"], "blocked")
            self.assertIn("synthetic-demo", " ".join(snapshot["blockers"]))
            self.assertIn("Release status: `blocked`", render_release_report(snapshot))
            page = render_release_html(snapshot)
            self.assertIn("Release only", page)
            self.assertIn('href="/dashboard/financials-evidence">Financials Evidence Center</a>', page)

    def test_releases_only_with_public_sources_complete_assets_and_matching_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = _stored_run(Path(directory), "targets")
            snapshot = build_release_decision(
                _public_providers(), database, "candidate", date(2026, 5, 24)
            )

            self.assertTrue(snapshot["release_ready"])
            self.assertEqual(snapshot["source_gate_status"], "pass")
            self.assertEqual(snapshot["lineage_gate_status"], "pass")
            self.assertEqual(snapshot["quality_gate_status"], "pass")
            self.assertFalse(snapshot["blockers"])

    def test_cli_writes_blocked_decision_and_fails_required_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = _stored_run(root, "synthetic-demo")
            report = root / "release.md"
            argv = [
                "marketwitness",
                "scorecard-release",
                "--registry",
                "data/samples/source_registry.csv",
                "--database",
                str(database),
                "--run-id",
                "candidate",
                "--report",
                str(report),
                "--require-release-ready",
                "--as-of",
                "2026-05-25",
            ]

            with patch("sys.argv", argv), redirect_stdout(io.StringIO()) as output:
                exit_code = main()

            self.assertEqual(exit_code, 2)
            self.assertIn("Release gate failed", output.getvalue())
            self.assertIn("Source gate: `blocked`", report.read_text(encoding="utf-8"))


def _stored_run(root: Path, provider_id: str) -> Path:
    database = root / "marketwitness.duckdb"
    assets = {}
    for role in ("targets", "prices", "corporate_actions", "universe_membership"):
        path = root / f"{role}.csv"
        path.write_text(f"{role}\n", encoding="utf-8")
        assets[role] = path
    asset_provider_ids = (
        {
            "prices": "prices",
            "corporate_actions": "actions",
            "universe_membership": "universe",
        }
        if provider_id == "targets"
        else {
            "prices": "synthetic-demo",
            "corporate_actions": "synthetic-demo",
            "universe_membership": "synthetic-demo",
        }
    )
    store_evaluation_run(
        database,
        EvaluationRun(
            run_id="candidate",
            as_of=date(2025, 1, 1),
            minimum_sample=1,
            transaction_cost_bps_per_side=Decimal("10"),
            universe_id="financials",
            asset_paths=assets,
            asset_provider_ids=asset_provider_ids,
            dataset_label="Release center fixture",
        ),
        [
            Evaluation(
                observation_id="candidate-target",
                ticker="AAA",
                firm="Example Firm",
                sector="Financials",
                published_date="2023-01-02",
                price_target=Decimal("100"),
                source_url="https://example.invalid/target",
                provider_id=provider_id,
                status="evaluated",
            )
        ],
    )
    return database


def _public_providers() -> list[SourceProvider]:
    return [
        _public_provider("targets", "Analyst targets"),
        _public_provider("prices", "Adjusted price bars"),
        _public_provider("actions", "Corporate actions"),
        _public_provider("universe", "Historical universe membership"),
    ]


def _public_provider(provider_id: str, data_class: str) -> SourceProvider:
    return SourceProvider(
        provider_id=provider_id,
        provider_name=provider_id.title(),
        data_class=data_class,
        access_model="public_endpoint",
        integration_status="implemented",
        license_status="public_access_rules_documented",
        publication_policy="source_link_and_derived_output",
        official_url="https://example.invalid/source",
        reference_url="https://example.invalid/terms",
        reviewed_on=date(2026, 5, 24),
        review_note="Approved publication fixture.",
    )


if __name__ == "__main__":
    unittest.main()
