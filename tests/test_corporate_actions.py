import tempfile
import unittest
from datetime import date
from pathlib import Path

from targetaudit.corporate_actions import (
    CorporateActionDataError,
    find_affected_observations,
    load_corporate_actions,
    render_corporate_actions_html,
    render_corporate_actions_report,
    write_affected_observations_csv,
)
from targetaudit.csvio import load_targets


class CorporateActionsTests(unittest.TestCase):
    def test_flags_targets_spanning_split_and_ticker_change(self) -> None:
        targets = load_targets(Path("data/samples/targets.csv"))
        actions = load_corporate_actions(Path("data/samples/corporate_actions.csv"))

        affected = find_affected_observations(targets, actions, date(2026, 5, 24))
        report = render_corporate_actions_report(actions, affected, date(2026, 5, 24))
        page = render_corporate_actions_html(actions, affected, date(2026, 5, 24))
        output = _TEMP_OUTPUT_DIRECTORY / "affected.csv"
        write_affected_observations_csv(output, affected)

        self.assertEqual(len(affected), 2)
        self.assertIn("demo-up-001", report)
        self.assertIn("`stock_split`", report)
        self.assertIn("`ticker_change`", report)
        self.assertIn("Affected observations are excluded", page)
        self.assertIn("Evidence", page)
        self.assertIn('href="/dashboard/financials-evidence">Financials Evidence Center</a>', page)
        self.assertIn("corporate-actions/demo-symbol-001", output.read_text(encoding="utf-8"))

    def test_rejects_split_without_ratio(self) -> None:
        path = _csv(
            "action_id,company_name,prior_ticker,current_ticker,action_type,"
            "effective_date,split_ratio_new,split_ratio_old,evidence_level,source_title,"
            "source_url,verified_on,review_note\n"
            "a-1,Issuer,AAA,AAA,stock_split,2023-06-01,,,synthetic_demo,Notice,"
            "https://example.invalid/notice,2023-06-01,Reviewed\n"
        )

        with self.assertRaisesRegex(CorporateActionDataError, "split requires"):
            load_corporate_actions(path)

    def test_rejects_evidence_after_report_cutoff(self) -> None:
        actions = load_corporate_actions(Path("data/samples/corporate_actions.csv"))

        with self.assertRaisesRegex(CorporateActionDataError, "after the report cutoff"):
            find_affected_observations([], actions, date(2023, 5, 31))


def _csv(content: str) -> Path:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "corporate-actions.csv"
    path.write_text(content, encoding="utf-8")
    _TEMP_DIRECTORIES.append(directory)
    return path


_TEMP_DIRECTORIES: list[tempfile.TemporaryDirectory] = []
_TEMP_OUTPUT_DIRECTORY_HANDLE = tempfile.TemporaryDirectory()
_TEMP_OUTPUT_DIRECTORY = Path(_TEMP_OUTPUT_DIRECTORY_HANDLE.name)


if __name__ == "__main__":
    unittest.main()
