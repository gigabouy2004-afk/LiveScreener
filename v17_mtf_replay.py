#!/usr/bin/env python
"""Timestamp-correct replay harness for V17 completed-D1/4H/1H diagnostics.

The harness can download a recent Yahoo smoke window or consume long-form
daily and 30-minute archive files.  Archive mode is the intended path for the
required several-year V17 validation.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

import Live_Scanner_v17 as engine
import v17_mtf


NY = ZoneInfo("America/New_York")
DEFAULT_CUTOFF_TIMES = "10:30,13:30,15:30,16:00"
DEFAULT_FORWARD_SESSIONS = "1,5,10,20"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Replay V17 completed-D1 plus completed 4H/1H diagnostics at "
            "historical U.S. execution cutoffs."
        )
    )
    parser.add_argument("--daily-file")
    parser.add_argument("--intraday-file")
    parser.add_argument(
        "--symbols",
        nargs="*",
        default=None,
        help="Recent Yahoo smoke symbols when archive files are not supplied.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path("output") / "V17_MTF_Replay"),
    )
    parser.add_argument(
        "--cutoff-times",
        default=DEFAULT_CUTOFF_TIMES,
        help="Comma-separated New York execution cutoffs.",
    )
    parser.add_argument(
        "--forward-sessions",
        default=DEFAULT_FORWARD_SESSIONS,
        help="Comma-separated forward daily-session outcome horizons.",
    )
    parser.add_argument(
        "--max-sessions",
        type=int,
        default=0,
        help="Optional most-recent session cap for a smoke replay.",
    )
    parser.add_argument("--preset", choices=sorted(engine.PRESETS), default="balanced")
    return parser.parse_args()


def parse_positive_ints(raw: str) -> list[int]:
    return sorted({
        int(value.strip())
        for value in str(raw or "").split(",")
        if value.strip() and int(value.strip()) > 0
    })


def parse_cutoff_times(raw: str) -> list[tuple[int, int]]:
    output = []
    for value in str(raw or "").split(","):
        text = value.strip()
        if not text:
            continue
        hour_text, minute_text = text.split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError(f"Invalid cutoff time: {text}")
        output.append((hour, minute))
    if not output:
        raise ValueError("At least one cutoff time is required.")
    return sorted(set(output))


def normalize_ohlcv(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    output.columns = [str(column).strip().lower() for column in output.columns]
    required = ["open", "high", "low", "close", "volume"]
    if not set(required).issubset(output.columns):
        raise ValueError(f"OHLCV columns required: {required}")
    output = output[required].apply(pd.to_numeric, errors="coerce")
    output = output.dropna(subset=["open", "high", "low", "close"])
    output["volume"] = output["volume"].fillna(0.0)
    output = output[~output.index.duplicated(keep="last")].sort_index()
    return output


def load_long_market_file(path: str) -> dict[str, pd.DataFrame]:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Market-data file not found: {source}")
    if source.suffix.lower() in {".parquet", ".pq"}:
        frame = pd.read_parquet(source)
    else:
        frame = pd.read_csv(source)
    frame.columns = [str(column).strip().lower() for column in frame.columns]
    timestamp_column = next(
        (
            column
            for column in ("timestamp", "datetime", "date")
            if column in frame.columns
        ),
        None,
    )
    if timestamp_column is None:
        raise ValueError(f"{source} needs a timestamp, datetime, or date column.")
    frame[timestamp_column] = pd.to_datetime(
        frame[timestamp_column],
        errors="raise",
    )
    ticker_column = next(
        (column for column in ("ticker", "symbol") if column in frame.columns),
        None,
    )
    if ticker_column is None:
        raise ValueError(f"{source} needs a ticker or symbol column.")

    output = {}
    for ticker, group in frame.groupby(ticker_column):
        symbol = engine.normalize_ticker_symbol(ticker)
        values = group.drop(columns=[ticker_column]).set_index(timestamp_column)
        output[symbol] = normalize_ohlcv(values)
    return output


def download_recent(symbols: list[str]) -> tuple[dict, dict]:
    daily = {}
    intraday = {}
    for raw_symbol in symbols:
        symbol = engine.normalize_ticker_symbol(raw_symbol)
        ticker = engine.yf.Ticker(symbol)
        try:
            metadata = ticker.get_history_metadata() or {}
        except Exception as exc:
            print(
                f"{symbol}: skipped; listing metadata unavailable ({exc})",
                flush=True,
            )
            continue
        listing_scope = v17_mtf.validate_us_listing(symbol, metadata)
        if not listing_scope["in_scope"]:
            print(
                f"{symbol}: skipped; listing out of scope "
                f"({listing_scope['basis']})",
                flush=True,
            )
            continue
        daily_frame = ticker.history(
            period="5y",
            interval="1d",
            prepost=False,
            auto_adjust=True,
        )
        intraday_frame = ticker.history(
            period=v17_mtf.SOURCE_PERIOD,
            interval="30m",
            prepost=False,
            auto_adjust=True,
        )
        if daily_frame is not None and not daily_frame.empty:
            daily[symbol] = normalize_ohlcv(daily_frame)
        if intraday_frame is not None and not intraday_frame.empty:
            intraday[symbol] = normalize_ohlcv(intraday_frame)
    return daily, intraday


def daily_prefix_for_cutoff(
    daily_frame: pd.DataFrame,
    cutoff: pd.Timestamp,
) -> tuple[pd.DataFrame, str | None]:
    context = v17_mtf.us_market_context(cutoff)
    completed_date = pd.Timestamp(context["latest_completed_session_date"])
    index_dates = pd.DatetimeIndex(daily_frame.index)
    if index_dates.tz is not None:
        index_dates = index_dates.tz_convert(NY).tz_localize(None)
    normalized_dates = index_dates.normalize()
    keep = normalized_dates <= completed_date
    prefix = daily_frame.loc[keep].copy()
    if prefix.empty:
        return prefix, None

    last_date = pd.Timestamp(prefix.index[-1]).date()
    prefix.attrs["weekly_period_complete"] = (
        v17_mtf.is_completed_us_trading_week(last_date)
    )
    return prefix, last_date.isoformat()


def scalar_daily_fields(result: dict) -> dict:
    output = {}
    for key, value in result.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            output[f"d1_{key}"] = value
    return output


def forward_outcomes(
    daily_frame: pd.DataFrame,
    *,
    cutoff: pd.Timestamp,
    reference_price: float | None,
    horizons: list[int],
) -> dict:
    output = {}
    if reference_price is None or not math.isfinite(reference_price) or reference_price <= 0:
        return output

    index = pd.DatetimeIndex(daily_frame.index)
    if index.tz is not None:
        local_dates = index.tz_convert(NY).tz_localize(None).normalize()
    else:
        local_dates = index.normalize()
    future = daily_frame.loc[local_dates > pd.Timestamp(cutoff.date())].copy()
    for horizon in horizons:
        key = f"fwd_{horizon}s"
        if len(future) < horizon:
            output[f"{key}_return_pct"] = None
            output[f"{key}_mfe_pct"] = None
            output[f"{key}_mae_pct"] = None
            continue
        window = future.iloc[:horizon]
        close_value = float(window["close"].iloc[-1])
        output[f"{key}_return_pct"] = round(
            (close_value / reference_price - 1.0) * 100.0,
            4,
        )
        output[f"{key}_mfe_pct"] = round(
            (float(window["high"].max()) / reference_price - 1.0) * 100.0,
            4,
        )
        output[f"{key}_mae_pct"] = round(
            (float(window["low"].min()) / reference_price - 1.0) * 100.0,
            4,
        )
    return output


def build_cutoffs(
    intraday_frame: pd.DataFrame,
    cutoff_times: list[tuple[int, int]],
    max_sessions: int,
) -> list[pd.Timestamp]:
    index = pd.DatetimeIndex(intraday_frame.index)
    if index.tz is None:
        index = index.tz_localize(NY)
    else:
        index = index.tz_convert(NY)
    session_dates = sorted(set(index.date))
    if max_sessions > 0:
        session_dates = session_dates[-max_sessions:]
    cutoffs = []
    for session_date in session_dates:
        bounds = v17_mtf.us_session_bounds(session_date)
        if bounds is None:
            continue
        open_at, close_at = bounds
        for hour, minute in cutoff_times:
            cutoff = pd.Timestamp(
                datetime(
                    session_date.year,
                    session_date.month,
                    session_date.day,
                    hour,
                    minute,
                    tzinfo=NY,
                )
            )
            if open_at < cutoff <= close_at:
                cutoffs.append(cutoff)
    return cutoffs


def replay_symbol(
    ticker: str,
    daily_frame: pd.DataFrame,
    intraday_frame: pd.DataFrame,
    *,
    config: dict,
    cutoff_times: list[tuple[int, int]],
    horizons: list[int],
    max_sessions: int,
) -> list[dict]:
    rows = []
    cutoffs = build_cutoffs(intraday_frame, cutoff_times, max_sessions)
    for cutoff in cutoffs:
        daily_prefix, baseline_date = daily_prefix_for_cutoff(
            daily_frame,
            cutoff,
        )
        if len(daily_prefix) < engine.EMA_SLOW_PERIOD:
            continue
        daily_result = engine.evaluate_frame(
            daily_prefix,
            ticker,
            config,
        )
        mtf_output, frames = v17_mtf.evaluate_mtf_source(
            intraday_frame,
            daily_result=daily_result,
            cutoff=cutoff,
        )
        completed_source = frames["source_completed_30m"]
        reference_price = (
            float(completed_source["close"].iloc[-1])
            if not completed_source.empty
            else None
        )
        reference_timestamp = (
            pd.Timestamp(completed_source.index[-1]).isoformat()
            if not completed_source.empty
            else None
        )
        rows.append({
            "ticker": ticker,
            "cutoff": cutoff.isoformat(),
            "daily_baseline_session_date": baseline_date,
            "reference_price": reference_price,
            "reference_source_bar_start": reference_timestamp,
            **scalar_daily_fields(daily_result),
            **mtf_output,
            **forward_outcomes(
                daily_frame,
                cutoff=cutoff,
                reference_price=reference_price,
                horizons=horizons,
            ),
        })
    return rows


def grouped_outcome_summary(
    panel: pd.DataFrame,
    group_field: str,
    horizons: list[int],
) -> dict:
    output = {}
    if panel.empty or group_field not in panel.columns:
        return output
    for group_name, group in panel.groupby(group_field, dropna=False):
        metrics = {"observations": int(len(group))}
        for horizon in horizons:
            field = f"fwd_{horizon}s_return_pct"
            values = pd.to_numeric(group.get(field), errors="coerce").dropna()
            metrics[field] = {
                "count": int(len(values)),
                "win_rate_pct": (
                    round(float(values.gt(0).mean() * 100.0), 2)
                    if len(values)
                    else 0.0
                ),
                "average_pct": (
                    round(float(values.mean()), 4) if len(values) else 0.0
                ),
                "median_pct": (
                    round(float(values.median()), 4) if len(values) else 0.0
                ),
            }
        output[str(group_name)] = metrics
    return output


def main() -> int:
    args = parse_args()
    cutoff_times = parse_cutoff_times(args.cutoff_times)
    horizons = parse_positive_ints(args.forward_sessions)
    if args.daily_file or args.intraday_file:
        if not args.daily_file or not args.intraday_file:
            raise ValueError("Archive mode requires both --daily-file and --intraday-file.")
        daily_by_ticker = load_long_market_file(args.daily_file)
        intraday_by_ticker = load_long_market_file(args.intraday_file)
        source_mode = "SUPPLIED_ARCHIVE"
    else:
        symbols = args.symbols or ["AAPL", "MSFT", "NVDA"]
        daily_by_ticker, intraday_by_ticker = download_recent(symbols)
        source_mode = "YAHOO_RECENT_SMOKE"

    common = sorted(set(daily_by_ticker).intersection(intraday_by_ticker))
    config = engine.get_config(args.preset)
    rows = []
    for ticker in common:
        rows.extend(
            replay_symbol(
                ticker,
                daily_by_ticker[ticker],
                intraday_by_ticker[ticker],
                config=config,
                cutoff_times=cutoff_times,
                horizons=horizons,
                max_sessions=max(0, args.max_sessions),
            )
        )
        print(f"{ticker}: {len(rows):,} cumulative replay rows", flush=True)

    panel = pd.DataFrame(rows)
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    panel_path = output_dir / "V17_MTF_Replay_Panel.parquet"
    csv_path = output_dir / "V17_MTF_Replay_Panel.csv"
    summary_path = output_dir / "V17_MTF_Replay_Summary.json"
    panel.to_parquet(panel_path, index=False)
    panel.to_csv(csv_path, index=False)

    summary = {
        "engine": "V17_D1_MTF_SHADOW",
        "classification_active": False,
        "source_mode": source_mode,
        "symbols": common,
        "rows": int(len(panel)),
        "cutoff_times_new_york": [
            f"{hour:02d}:{minute:02d}" for hour, minute in cutoff_times
        ],
        "forward_session_horizons": horizons,
        "development_state_outcomes": grouped_outcome_summary(
            panel,
            "v17_current_development_state",
            horizons,
        ),
        "daily_momentum_state_outcomes": grouped_outcome_summary(
            panel,
            "d1_momentum_state",
            horizons,
        ),
        "method_notes": [
            "Daily context is limited to the latest fully completed XNYS session at each cutoff.",
            "Only completed regular-session 30-minute source bars enter 1H/4H diagnostics.",
            "The same observation can appear at several daily cutoffs; inferential analysis must account for repeated ticker/session observations.",
            (
                "YAHOO_RECENT_SMOKE is a mechanics check only. Several-year "
                "claims require SUPPLIED_ARCHIVE data and out-of-sample splits."
            ),
        ],
        "artifacts": {
            "panel_parquet": str(panel_path),
            "panel_csv": str(csv_path),
        },
    }
    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
