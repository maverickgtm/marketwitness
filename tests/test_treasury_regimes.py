import unittest
from datetime import date
from pathlib import Path

from marketwitness.providers.treasury import load_treasury_snapshot
from marketwitness.treasury_regimes import build_treasury_regime_snapshot


class TreasuryRegimeTests(unittest.TestCase):
    def test_exposes_curve_state_and_session_change_without_trade_claim(self) -> None:
        yields = load_treasury_snapshot(
            Path("data/samples/treasury-yields-synthetic.xml"), date(2026, 5, 25)
        )

        snapshot = build_treasury_regime_snapshot(yields, sessions=1)

        self.assertEqual(snapshot["latest_rate_date"], "2026-05-25")
        self.assertEqual(snapshot["curve_regime"]["key"], "upward_sloping")
        self.assertTrue(snapshot["comparison_available"])
        self.assertEqual(snapshot["comparison"]["reference_date"], "2026-05-22")
        self.assertEqual(snapshot["comparison"]["two_year_change_bps"], "-6.00")
        self.assertEqual(snapshot["comparison"]["curve_shift"], "Broadly stable")
        self.assertIn("do not predict returns", snapshot["publication_boundary"])

    def test_reports_unavailable_longer_window_without_inventing_history(self) -> None:
        yields = load_treasury_snapshot(
            Path("data/samples/treasury-yields-synthetic.xml"), date(2026, 5, 25)
        )

        snapshot = build_treasury_regime_snapshot(yields, sessions=20)

        self.assertFalse(snapshot["comparison_available"])
        self.assertIsNone(snapshot["comparison"])

    def test_rejects_unsupported_window(self) -> None:
        with self.assertRaisesRegex(ValueError, "1, 5, 20 or 60"):
            build_treasury_regime_snapshot([], sessions=2)


if __name__ == "__main__":
    unittest.main()
