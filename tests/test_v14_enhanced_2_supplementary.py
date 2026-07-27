import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

import Live_Scanner_v14_Enhanced as v14_enhanced
import Live_Scanner_v14_Enhanced_2 as v14_enhanced_2
from Live_Scanner_v14_Enhanced_2 import (
    STATUS_BUY_SIGNAL,
    STATUS_HOLD,
    calculate_supplementary_technical_rating,
    enrich_buy_supplementary,
    parse_analyst_consensus,
    parse_earnings_event,
    rating_category,
    supplementary_field_defaults,
)


def make_price_frame(rows=260):
    index = pd.bdate_range("2025-01-01", periods=rows)
    close = pd.Series(
        np.linspace(100.0, 160.0, rows) + np.sin(np.arange(rows) / 8),
        index=index,
    )
    return pd.DataFrame(
        {
            "high": close + 2.0,
            "low": close - 2.0,
            "close": close,
            "volume": np.linspace(1_000_000, 1_500_000, rows),
        },
        index=index,
    )


class RaisingTicker:
    def _raise(self, *args, **kwargs):
        raise RuntimeError("provider unavailable")

    get_recommendations_summary = _raise
    get_analyst_price_targets = _raise
    get_earnings_dates = _raise

    @property
    def calendar(self):
        raise RuntimeError("provider unavailable")


class ExplodingTicker:
    def __getattribute__(self, name):
        raise AssertionError(f"non-BUY enrichment accessed ticker provider: {name}")


class SupplementaryRatingTests(unittest.TestCase):
    def test_rating_boundaries_match_published_bands(self):
        cases = {
            0.51: "STRONG_BUY",
            0.50: "BUY",
            0.11: "BUY",
            0.10: "NEUTRAL",
            -0.10: "NEUTRAL",
            -0.11: "SELL",
            -0.50: "SELL",
            -0.51: "STRONG_SELL",
            None: "UNKNOWN",
        }
        for score, expected in cases.items():
            with self.subTest(score=score):
                self.assertEqual(rating_category(score), expected)

    def test_technical_composite_has_15_ma_and_11_oscillator_votes(self):
        rating = calculate_supplementary_technical_rating(make_price_frame())

        self.assertNotEqual(rating["technical_rating"], "UNKNOWN")
        self.assertEqual(rating["technical_rating_method"], "TV_LIKE_15_MA_11_OSC")
        self.assertEqual(
            rating["technical_buy_signals"]
            + rating["technical_neutral_signals"]
            + rating["technical_sell_signals"],
            26,
        )

    def test_analyst_consensus_and_targets(self):
        recommendations = pd.DataFrame(
            [{
                "period": "0m",
                "strongBuy": 4,
                "buy": 11,
                "hold": 8,
                "sell": 0,
                "strongSell": 0,
            }]
        )
        targets = {
            "current": 219.25,
            "low": 180.0,
            "mean": 227.27182,
            "median": 236.5,
            "high": 265.0,
        }

        parsed = parse_analyst_consensus(recommendations, targets, 219.25)

        self.assertEqual(parsed["analyst_rating"], "BUY")
        self.assertEqual(parsed["analyst_count"], 23)
        self.assertEqual(parsed["analyst_breakdown"], "SB=4;B=11;H=8;S=0;SS=0")
        self.assertEqual(parsed["analyst_target_upside_pct"], 3.66)

    def test_missing_analyst_consensus_is_unknown_not_error(self):
        parsed = parse_analyst_consensus(pd.DataFrame(), {}, 100.0)

        self.assertEqual(parsed["analyst_rating"], "UNKNOWN")
        self.assertEqual(parsed["analyst_count"], 0)

    def test_upcoming_date_only_earnings_has_unknown_timing(self):
        reference = datetime(2026, 7, 28, 12, tzinfo=ZoneInfo("America/New_York"))
        parsed = parse_earnings_event(
            None,
            {"Earnings Date": [pd.Timestamp("2026-07-30")]},
            reference,
        )

        self.assertEqual(parsed["earnings_event_risk"], "UPCOMING")
        self.assertEqual(parsed["days_to_earnings"], 2)
        self.assertEqual(parsed["earnings_timing"], "UNKNOWN")

    def test_detailed_after_close_earnings_is_labelled_amc(self):
        reference = datetime(2026, 7, 28, 12, tzinfo=ZoneInfo("America/New_York"))
        dates = pd.DataFrame(
            {"Reported EPS": [None]},
            index=[pd.Timestamp("2026-07-29 16:00", tz="America/New_York")],
        )
        parsed = parse_earnings_event(dates, None, reference)

        self.assertEqual(parsed["earnings_event_risk"], "UPCOMING")
        self.assertEqual(parsed["earnings_timing"], "AMC")
        self.assertEqual(parsed["days_to_earnings"], 1)

    def test_recent_earnings_is_reported_without_changing_engine_signal(self):
        reference = datetime(2026, 7, 28, 12, tzinfo=ZoneInfo("America/New_York"))
        dates = pd.DataFrame(
            {"Reported EPS": [1.23]},
            index=[pd.Timestamp("2026-07-25 08:00", tz="America/New_York")],
        )
        parsed = parse_earnings_event(dates, None, reference)

        self.assertEqual(parsed["earnings_event_risk"], "RECENT")
        self.assertEqual(parsed["days_since_earnings"], 3)

    def test_past_only_earnings_does_not_claim_no_event_risk(self):
        reference = datetime(2026, 7, 28, 12, tzinfo=ZoneInfo("America/New_York"))
        dates = pd.DataFrame(
            {"Reported EPS": [1.23]},
            index=[pd.Timestamp("2025-11-07 08:00", tz="America/New_York")],
        )
        parsed = parse_earnings_event(dates, None, reference)

        self.assertEqual(parsed["earnings_event_risk"], "UNKNOWN")
        self.assertIn("Upcoming earnings date unavailable", parsed["earnings_message"])


class SupplementaryIsolationTests(unittest.TestCase):
    def test_core_evaluate_frame_is_identical_to_v14_enhanced(self):
        frames = [
            make_price_frame(),
            make_price_frame().assign(
                high=lambda frame: 202 - frame["low"],
                low=lambda frame: 198 - frame["high"],
                close=lambda frame: 200 - frame["close"],
            ),
        ]
        for frame in frames:
            frame.attrs["weekly_period_complete"] = True
            with self.subTest(final_close=float(frame["close"].iloc[-1])):
                original = v14_enhanced.evaluate_frame(
                    frame.copy(),
                    "TEST",
                    v14_enhanced.get_config("balanced"),
                )
                enhanced_2 = v14_enhanced_2.evaluate_frame(
                    frame.copy(),
                    "TEST",
                    v14_enhanced_2.get_config("balanced"),
                )
                self.assertEqual(enhanced_2, original)

    def test_non_buy_never_accesses_supplementary_provider(self):
        original = {
            **supplementary_field_defaults(),
            "ticker": "TEST",
            "status": STATUS_HOLD,
            "classification": "HOLD",
            "output_signal": "Hold_Wait",
        }

        enriched = enrich_buy_supplementary(
            original,
            make_price_frame(),
            ExplodingTicker(),
            {},
            None,
        )

        self.assertEqual(enriched["status"], STATUS_HOLD)
        self.assertEqual(enriched["classification"], "HOLD")
        self.assertEqual(enriched["supplementary_status"], "NOT_APPLICABLE")

    def test_buy_provider_failure_remains_buy_and_is_partial(self):
        original = {
            **supplementary_field_defaults(),
            "ticker": "TEST",
            "status": STATUS_BUY_SIGNAL,
            "classification": "BUY",
            "output_signal": "Buy_Early_Momentum",
            "price": 160.0,
            "message_details": "Core=unchanged",
        }
        context = {
            "_now_local": datetime(
                2026,
                7,
                28,
                12,
                tzinfo=ZoneInfo("America/New_York"),
            ),
            "_timezone": ZoneInfo("America/New_York"),
        }

        enriched = enrich_buy_supplementary(
            original,
            make_price_frame(),
            RaisingTicker(),
            context,
            None,
        )

        self.assertEqual(enriched["status"], STATUS_BUY_SIGNAL)
        self.assertEqual(enriched["classification"], "BUY")
        self.assertEqual(enriched["output_signal"], "Buy_Early_Momentum")
        self.assertEqual(enriched["supplementary_status"], "PARTIAL")
        self.assertEqual(enriched["analyst_rating"], "UNKNOWN")
        self.assertEqual(enriched["earnings_event_risk"], "UNKNOWN")
        self.assertIn("Core=unchanged", enriched["message_details"])


if __name__ == "__main__":
    unittest.main()
