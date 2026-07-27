# Changelog

## Unreleased - V15 shadow momentum quality

### Added

- Independent `Live_Scanner_v15.py` entry point based on validated V14 Enhanced
  commit `20641f5`.
- Non-binding `LEADER`, `DEVELOPING`, `WEAK`, and `NONE` momentum-quality
  states.
- Non-binding entry states that distinguish confirmed candidates from ADX,
  volume, extension, leadership, and V14-trigger waits.
- Shadow measurements for EMA50/EMA200 slopes, 20/60/120-session returns,
  positive/negative directional movement, five-session ADX change, proximity
  to the prior 52-week high, volume confirmation, and ATR extension.
- Explicit shadow summaries in terminal, log, and workbook output.
- Focused unit coverage for quality scoring, entry-state precedence, and the
  frozen-classification contract.
- Approval-ready V14-to-V15 handover covering engine intent, checks and
  balances, input/output and messaging contracts, local/GitHub manifests,
  Phase 2 boundaries, and explicit owner signoff.
- Focused regression coverage for compact and spaced comma-separated direct
  code strings, mixed argument segments, normalization, and duplicate removal.

### Safety

- V15 shadow fields do not modify `status`, `classification`, or
  `output_signal`.
- V14 files remain unchanged and continue to be the operational baseline.
- Benchmark-relative strength is intentionally deferred until exchange-to-
  benchmark mappings and historical evidence are agreed.

## 2026-07-27 - V14 Enhanced positive-regime scope correction

- Removed pre-bull/pre-bear crossover concepts from V14 Enhanced classification.
- Removed the generic one-bar histogram-improvement shortcut from continuation,
  pullback, confidence scoring, and HOLD labels.
- Required MACD, signal, and histogram to confirm an established positive MACD
  regime before any pullback BUY path can qualify.
- Required the configured histogram window to be strictly expanding, with its
  latest two bars positive, for momentum-continuation BUY eligibility.
- Added strict HOLD outcomes for positive price trends whose MACD momentum is
  unconfirmed or whose MACD zero gate is not met.
- Gated ADX, volume, price-response, and recovery score contributions behind
  daily trend, weekly trend, and established positive MACD confirmation.
- Added boundary tests covering negative histogram improvement, negative-to-
  positive transitions, non-sustained one-bar improvement, and positive cooling.
- Applied the live BUY quality-policy layer during built-in historical replay so
  backtest classifications match live/as-of engine policy.

### Validation

- Original and enhanced engines compile.
- 24/24 focused unit tests pass.
- GLOSTERLTD.NS on 2026-07-24 is strict HOLD/NO_BUY with a capped 4/10 setup
  score.
- XLI regression BUY counts are 0, 2, and 3 for 2026-07-22 through 2026-07-24.
- The 19-symbol audit produces 3 BUY, 11 HOLD, 2 IGNORE, and 3 ERROR rows.
- All retained BUYs pass the positive EMA/MACD/histogram invariants.
- A three-year, five-session XLI replay produces 124 trades, a 52.42% win rate,
  and a 0.43% average return before costs and execution assumptions.

## Unreleased

### Added

- Prominent `DataThrough` reporting in per-run messages, terminal/log summaries,
  and the workbook Summary sheet.
- Approved P1 quality fields for the mandatory volume floor, U.S. ADV20
  liquidity floor, and extreme-extension review state.
- Unit coverage for single-session, mixed-market, and all-error data-through
  summaries, plus boundary coverage for all three P1 policies.

### Changed

- Detail rows now report the actual final daily session included in the
  evaluation frame instead of repeating a weekend, holiday, or requested
  historical as-of label.
- BUY#4 now requires a fresh bullish MACD signal-line crossover with both lines
  above zero and a positive histogram. Negative-histogram improvement is outside
  the engine's signal mandate and receives no pre-crossover classification.
- Current volume ratio must be at least `0.60` before the immediate-ratio or
  one-year-percentile volume-support paths can qualify a BUY.
- U.S. BUY candidates must have at least USD 1 million prior-20-session average
  daily turnover; candidates below the floor become HOLD/`NO_BUY`.
- BUY candidates more than 5 ATR above EMA50 retain BUY status but are labeled
  `BUY_EXTENDED_REVIEW`.
- Detail output expanded from 107 to 113 columns for explicit policy audit
  fields.

## 2026-07-25 — V14 Enhanced handover

### Added

- Bounded concurrent polling with deterministic input-order result retention.
- Poll-boundary `Max-Count` and `Max-Buys` continuation triggers.
- Independent per-ticker one-year RSI, ADX, stochastic, price, and volume
  context.
- Advisory adaptive historical guidance:
  - 100 or fewer input tickers: maximum available history.
  - 101–1,000 input tickers: five years.
  - More than 1,000 input tickers: one year.
- Positive-phase early-momentum and momentum-continuation signal paths.
- Previous-positive-session stochastic relaxation after a BUY is detected.
- Multi-market session and listing-currency metadata in the output.
- Historical as-of and multi-date validation modes.
- Workbook output expanded to 107 columns.
- Engine guide, validation report, and session handover/signoff documentation.

### Changed

- RSI and ADX upper values are historical context rather than universal hard
  rejection limits.
- ADX current value versus the ticker's prior maximum is reported as confidence
  context and is not a qualification gate.
- Volume support may come from either the current 20-day volume ratio or the
  ticker's one-year absolute-volume percentile.
- Price and indicator historical guidance is calculated without including the
  current candle.

### Validation

- XLI top-ten regression produced 2, 5, and 3 BUYs on 2026-07-22,
  2026-07-23, and 2026-07-24 respectively.
- Full U.S. scan processed 3,636 symbols in 19 minutes 14 seconds.
- Independent fresh-data audit reproduced all 19 sampled statuses, signals,
  prices, and indicator values.

### Known limitations

- The current volume-support OR rule can qualify a ticker even when its current
  volume is materially below its 20-day average.
- No minimum average daily turnover or minimum local-currency price gate is
  enabled.
- Highly extended momentum can remain a BUY with an elevated risk label.
- The run-level `AsOf` label can be a non-trading date; use `session_date` and
  `candle_state` to identify the actual data-through session.
- Sparse/low-liquidity Yahoo daily bars can disagree with intraday quote data.
