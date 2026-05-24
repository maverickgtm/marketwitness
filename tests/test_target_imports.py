import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.csvio import load_targets
from targetaudit.target_imports import (
    TargetImportDataError,
    import_authorized_targets,
    load_target_import_manifest,
    render_import_html,
    render_import_report,
    write_normalized_targets,
)


class TargetImportsTests(unittest.TestCase):
    def test_normalizes_accepted_rows_and_audits_rejection(self) -> None:
        manifest = load_target_import_manifest(
            Path("data/samples/authorized-target-export-manifest.json")
        )
        observations, decisions = import_authorized_targets(
            Path("data/samples/authorized-target-export.csv"), manifest, date(2026, 5, 24)
        )

        self.assertEqual(len(observations), 3)
        self.assertEqual(observations[0].observation_id, "authorized-demo:exp-001")
        self.assertEqual(observations[0].benchmark_symbol, "XLF")
        self.assertEqual(decisions[3].reason, "missing_or_invalid_source_url")
        self.assertIn("Rows rejected: `1`", render_import_report(manifest, decisions, date(2026, 5, 24)))
        self.assertIn("internal_only", render_import_html(manifest, decisions, date(2026, 5, 24)))

    def test_writes_targets_compatible_with_evaluator_input(self) -> None:
        manifest = load_target_import_manifest(
            Path("data/samples/authorized-target-export-manifest.json")
        )
        observations, _ = import_authorized_targets(
            Path("data/samples/authorized-target-export.csv"), manifest, date(2026, 5, 24)
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "targets.csv"
            write_normalized_targets(output, observations)
            imported = load_targets(output)

        self.assertEqual(len(imported), 3)
        self.assertEqual(imported[1].source_provider, "authorized_demo_export")

    def test_rejects_manifest_without_internal_research_authorization(self) -> None:
        payload = json.loads(
            Path("data/samples/authorized-target-export-manifest.json").read_text(encoding="utf-8")
        )
        payload["authorized_for_internal_research"] = False
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(TargetImportDataError, "does not authorize"):
                load_target_import_manifest(path)

    def test_rejects_duplicate_export_identifiers_row_by_row(self) -> None:
        manifest = load_target_import_manifest(
            Path("data/samples/authorized-target-export-manifest.json")
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.csv"
            path.write_text(
                "provider_record,symbol,issuer,publisher,analyst_name,announced_on,target_value,recommendation,evidence_link\n"
                "dup,ACBK,Acme,Research,,2023-01-02,120,Buy,https://example.invalid/one\n"
                "dup,ACBK,Acme,Research,,2023-01-02,121,Buy,https://example.invalid/two\n",
                encoding="utf-8",
            )
            observations, decisions = import_authorized_targets(path, manifest, date(2026, 5, 24))

        self.assertEqual(len(observations), 1)
        self.assertEqual(decisions[1].reason, "duplicate_record_id")


if __name__ == "__main__":
    unittest.main()
