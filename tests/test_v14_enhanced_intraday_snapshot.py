import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from Live_Scanner_v14_Enhanced import (
    calculate_session_paced_volume_ratios,
    regular_session_elapsed_fraction,
)


class RegularSessionElapsedFractionTests(unittest.TestCase):
    def setUp(self):
        market_tz = ZoneInfo("America/New_York")
        self.context = {
            "phase": "REGULAR",
            "_regular_start": datetime(2026, 7, 28, 9, 30, tzinfo=market_tz),
            "_regular_end": datetime(2026, 7, 28, 16, 0, tzinfo=market_tz),
            "_now_local": datetime(2026, 7, 28, 14, 30, tzinfo=market_tz),
        }

    def test_regular_session_fraction_uses_exchange_session_bounds(self):
        fraction = regular_session_elapsed_fraction(self.context)
        self.assertAlmostEqual(fraction, 5.0 / 6.5)

    def test_fraction_is_capped_at_full_session(self):
        market_tz = ZoneInfo("America/New_York")
        fraction = regular_session_elapsed_fraction(
            self.context,
            datetime(2026, 7, 28, 17, 0, tzinfo=market_tz),
        )
        self.assertEqual(fraction, 1.0)

    def test_non_regular_session_is_not_normalized(self):
        context = {**self.context, "phase": "POSTMARKET"}
        self.assertIsNone(regular_session_elapsed_fraction(context))


class SessionPacedVolumeRatioTests(unittest.TestCase):
    def test_partial_volume_is_scaled_by_elapsed_session_fraction(self):
        raw_ratio, paced_ratio = calculate_session_paced_volume_ratios(
            current_volume=450_000,
            average_daily_volume=1_000_000,
            session_elapsed_fraction=0.75,
        )
        self.assertAlmostEqual(raw_ratio, 0.45)
        self.assertAlmostEqual(paced_ratio, 0.60)

    def test_completed_volume_uses_raw_daily_ratio(self):
        raw_ratio, paced_ratio = calculate_session_paced_volume_ratios(
            current_volume=900_000,
            average_daily_volume=1_000_000,
            session_elapsed_fraction=1.0,
        )
        self.assertAlmostEqual(raw_ratio, 0.90)
        self.assertAlmostEqual(paced_ratio, 0.90)

    def test_missing_volume_does_not_create_a_ratio(self):
        raw_ratio, paced_ratio = calculate_session_paced_volume_ratios(
            current_volume=None,
            average_daily_volume=1_000_000,
            session_elapsed_fraction=0.75,
        )
        self.assertIsNone(raw_ratio)
        self.assertIsNone(paced_ratio)


if __name__ == "__main__":
    unittest.main()
