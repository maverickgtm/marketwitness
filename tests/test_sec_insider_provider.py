import tempfile
import unittest
from datetime import date
from pathlib import Path

from marketwitness.providers.sec_insider import (
    SecInsiderDataError,
    build_insider_snapshot,
    load_insider_csv,
    load_insider_dataset,
    parse_insider_tables,
    write_insider_csv,
)


class SecInsiderProviderTests(unittest.TestCase):
    def test_classifies_only_priced_purchase_and_sale_codes_in_totals(self) -> None:
        records = load_insider_dataset(
            Path("data/samples/sec-insider"), date(2026, 5, 26), synthetic_fixture=True
        )
        snapshot = build_insider_snapshot(records, days=30)

        self.assertEqual(len(records), 4)
        self.assertEqual(snapshot["transaction_count"], 2)
        self.assertEqual(snapshot["purchase_count"], 1)
        self.assertEqual(snapshot["sale_count"], 1)
        self.assertEqual(snapshot["purchase_value"], "200000.00")
        self.assertEqual(snapshot["sale_value"], "315000.00")
        self.assertEqual(snapshot["net_declared_value"], "-115000.00")
        self.assertEqual(snapshot["other_nonderivative_count"], 2)
        self.assertEqual(snapshot["post_filing_dated_count"], 0)
        self.assertEqual(snapshot["value_review_required_count"], 0)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "insider.csv"
            write_insider_csv(path, records)
            self.assertEqual(load_insider_csv(path), records)

    def test_supports_company_search_and_rejects_unknown_window(self) -> None:
        records = load_insider_dataset(
            Path("data/samples/sec-insider"), date(2026, 5, 26), synthetic_fixture=True
        )
        apple = build_insider_snapshot(records, days=30, query="AAPL")
        self.assertEqual(apple["purchase_count"], 1)
        self.assertEqual(apple["sale_count"], 0)
        owner = build_insider_snapshot(records, days=365, query="Example Officer")
        self.assertEqual(owner["sale_count"], 1)
        self.assertIn("private transactions", owner["publication_boundary"])
        with self.assertRaisesRegex(SecInsiderDataError, "window"):
            build_insider_snapshot(records, days=45)

    def test_holds_post_filing_and_extraordinary_value_rows_out_of_totals(self) -> None:
        root = Path("data/samples/sec-insider")
        tables = {
            name: (root / name).read_text(encoding="utf-8")
            for name in ("SUBMISSION.tsv", "REPORTINGOWNER.tsv", "NONDERIV_TRANS.tsv")
        }
        tables["NONDERIV_TRANS.tsv"] = (
            tables["NONDERIV_TRANS.tsv"]
            .replace("30-MAR-2026", "02-APR-2026", 1)
            .replace("\t420.00\t", "\t20000000.00\t", 1)
        )
        records = parse_insider_tables(
            tables,
            date(2026, 5, 26),
            "synthetic_fixture",
            "https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets",
        )
        snapshot = build_insider_snapshot(records, days=90)

        self.assertEqual(snapshot["transaction_count"], 0)
        self.assertEqual(snapshot["post_filing_dated_count"], 1)
        self.assertEqual(snapshot["value_review_required_count"], 1)
        self.assertEqual(snapshot["purchase_value"], "0")
        self.assertEqual(snapshot["sale_value"], "0")


if __name__ == "__main__":
    unittest.main()
