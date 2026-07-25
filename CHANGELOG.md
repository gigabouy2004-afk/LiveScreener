# Changelog

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
