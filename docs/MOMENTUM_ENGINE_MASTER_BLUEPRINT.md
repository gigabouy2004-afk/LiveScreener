# Momentum Engine Master Development Blueprint

Date established: 2026-07-30

Baseline branch: `V17`

Baseline commit: `3586f24cb4e8390e66476e30f895e1a3ce3ff430`

Baseline tag: `baseline-v17-momentum-foundation-2026-07-30`

Status: primary, self-contained development authority

## 1. Purpose of this document

This document contains the complete active foundation for developing the U.S.
Momentum Engine. It is intentionally self-contained: a developer should be
able to use this document in isolation without reading an earlier handover,
working note, validation report or retired file.

It defines:

- what the Momentum Engine is intended to become;
- what is already implemented and validated;
- how daily and current-session timeframes must be handled;
- which data and indicators are retained;
- how research records and future outcomes are constructed;
- how backtesting must be performed;
- what the existing evidence proves and does not prove;
- the required development sequence and promotion gates;
- the interim deliverables and final goals; and
- the safety rules that may not be relaxed.

Material under any `Retired` directory is not part of this specification.

### 1.1 Documentation authority and maintenance

This blueprint is the primary development authority. The other active
documents have narrower supporting roles:

- the engine document specifies calculation mechanics;
- the research protocol and field guide specify panel behavior and terminology;
- the validation records preserve evidence at the time it was measured;
- the handover preserves the tagged foundation state;
- the action plan tracks the ordered execution gates; and
- the changelog records documentation and implementation transitions.

Supporting documents may add detail, but may not contradict this blueprint.
When calculation logic, data contracts, outcomes, gates, goals or activation
status change, the same commit must update:

1. this blueprint;
2. every affected supporting document;
3. the README when entry-point guidance changes; and
4. the changelog with what changed and why.

Validation records remain evidence records. Do not rewrite their measured
results to match a later hypothesis; create a new validation record and update
the current gate status instead.

## 2. Mission and current decision

The mission is to build an evidence-based, stock-level Momentum Engine that:

1. establishes a reproducible momentum foundation from completed daily and
   completed-weekly observations;
2. describes how that foundation is developing using only completed
   observations from the current session;
3. estimates forward outcome probabilities using timestamp-correct,
   point-in-time data;
4. demonstrates stable out-of-sample value after realistic costs across
   multiple market regimes; and
5. remains understandable and auditable to an end user.

The present V17 baseline is research infrastructure. It is not:

- a genuine-momentum classifier;
- a production BUY rule;
- an automated trading system;
- permission to loosen inherited BUY conditions; or
- proof that 1-hour or 4-hour evidence adds predictive value.

The inherited daily rules failed the measured five-year stability gate. They
remain useful only as a benchmark against which a future evidence-based model
can be compared.

## 3. Market and instrument scope

The engine is restricted to provider-verified U.S. equities listed on:

- NYSE; or
- Nasdaq.

The provider must verify both the instrument type and listing venue.

The following are outside the current engine scope:

- NYSE American;
- NYSE Arca;
- ETFs;
- OTC securities;
- India/NSE/BSE securities; and
- all other international markets.

Each security is evaluated independently. A result may not depend on:

- which other tickers are in the watchlist;
- the order in which worker threads complete;
- another stock's indicators or result; or
- a changing cross-sectional input population.

Sector, industry and market information may later provide point-in-time
context, but may not manufacture missing stock-level price history.

## 4. Authoritative time model

### 4.1 Required terminology

| Term | Meaning |
|---|---|
| `1D` or daily | The daily timeframe |
| Previous completed session | The last traded NYSE session before today |
| Current session | Today/now, including premarket, regular hours and after close |
| Next session | The trading session after the current session |

The phrase “D-1” may be used informally, but it always means the previous
completed trading session, not the previous calendar date. Weekends, market
holidays and early closes are resolved with the XNYS exchange calendar.

### 4.2 Daily state transition

| Point in time | Daily foundation | Current-session evidence |
|---|---|---|
| Before today's open | Last traded session before today | None |
| During today's regular session | Last traded session before today | Completed observations from today only |
| After today's close | Last traded session before today | Completed observations from today only |
| When the next trading session begins | Today's completed daily candle | Completed observations from the new session only |

Today remains the current session after the official close. Today's completed
daily candle does not become the daily foundation until the next trading
session begins.

### 4.3 Non-negotiable temporal rules

1. The daily foundation contains completed daily and completed-weekly data only
   through the previous completed session.
2. Premarket, postmarket and partially formed daily candles never enter the
   daily calculation.
3. Only completed 1-hour and 4-hour observations belonging to the current
   session may describe current development.
4. No previous-session 1-hour or 4-hour opinion may be displayed, qualified or
   used as the comparison point for today.
5. Historical lower-timeframe observations may be used only to warm indicator
   calculations.
6. The first completed intraday observation today is a starting observation,
   not an improvement or regression from yesterday.
7. Future prices may be attached only after the feature record has been
   frozen.

These rules apply equally to live execution, historical replay and model-data
generation.

## 5. Completed-daily foundation

### 5.1 Daily and weekly calculations

The completed-daily calculation retains:

| Evidence | Parameters or treatment |
|---|---|
| Daily moving averages | EMA20, EMA50 and EMA200 |
| Completed-weekly moving averages | EMA20 and EMA50 |
| MACD | 12/26/9 plus histogram behavior |
| ADX and directional movement | ADX14, +DI and -DI |
| RSI | RSI14 |
| ATR | ATR14 |
| Stochastic | K9 and D6 |
| Daily volume participation | Completed volume versus the prior 20 completed sessions |
| Historical returns | 5, 10, 20, 60 and 120 sessions where used by the research panel |
| Trend slopes | EMA50 over 20 sessions and EMA200 over 60 sessions in the inherited benchmark |
| Range context | Prior 52-week or post-listing high/low context |
| Extension | ATR-normalized distance from the available trend |
| Turnover | Price/volume liquidity context |

The inherited live baseline requires at least 200 completed daily candles and
50 completed weekly candles. That requirement belongs to the legacy scanner
calculation. It must not exclude younger securities from the research panel.

### 5.2 Inherited daily momentum-quality benchmark

The inherited benchmark assigns one point for each available check:

1. EMA50 20-session slope is positive.
2. EMA200 60-session slope is non-negative.
3. The 20-session return is positive.
4. The 60-session return is positive.
5. The 120-session return is positive.
6. +DI is greater than -DI.
7. ADX is at least 20.
8. Price is at least 85% of the prior 52-week high.
9. Daily volume is at least its prior average.
10. Price is no more than 3 ATR above EMA50.

If the inherited primary regime is absent, the state is `NONE`. If it is
present:

- score 8–10: `LEADER`;
- score 6–7: `DEVELOPING`; and
- score below 6: `WEAK`.

Five-session ADX change is recorded separately. A rising ADX is evidence, but
is not one of the ten score points.

These states and thresholds reproduce the inherited comparison framework.
They are not approved future-model weights or promotion thresholds.

### 5.3 Other inherited implementation parameters

The current balanced implementation also carries these operational values:

| Parameter | Current value |
|---|---:|
| Stochastic BUY ceiling | 80 |
| Mandatory current daily-volume floor | 0.60 of the prior comparison |
| U.S. ADV20 turnover floor | USD 1,000,000 |
| Extreme-extension review threshold | 5 ATR |
| Descriptive strong-ADX band | 20 |
| Stochastic oversold/overbought | 30 / 80 |
| Stochastic middle band | 40–65 |
| Balanced ATR safe/extended bands | 2.2 / 3.0 |
| EMA20 maximum gap | 0.50 ATR |
| Balanced volume multiple | 1.20 |
| Continuation-volume floor | 0.80 |
| Historical-volume percentile support | 60th percentile |

These values are an implementation snapshot for parity and benchmarking. The
five-year evidence does not approve them as a genuine-momentum definition.

## 6. Current-session 1-hour and 4-hour construction

### 6.1 Source data

The intraday source is adjusted, regular-session 30-minute OHLCV requested
with extended hours disabled. A source bar is retained only when its scheduled
end time is at or before the execution cutoff.

Source bars are aggregated within one exchange session:

- `1h`: session-anchored 60-minute observations;
- `4h`: session-anchored 240-minute observations.

No aggregate may cross a session boundary.

### 6.2 Full-duration rule

The normal U.S. regular session is 390 minutes and does not divide evenly into
60- or 240-minute observations.

Therefore:

- the final 30-minute tail is not a full 1-hour observation;
- the final 150-minute tail is not a full 4-hour observation;
- any in-progress bucket is excluded; and
- an early-close session contributes only buckets that reached their full
  scheduled duration.

Short tails are counted and reported, never relabelled as full candles. Every
accepted 1-hour or 4-hour observation records its source count and duration and
must have `bar_is_short = False`.

### 6.3 Intraday evidence vector

Each timeframe calculates, when sufficient history is available:

- latest completed OHLCV and bar return;
- EMA20, EMA50 and EMA200;
- MACD, signal, histogram and one-observation histogram change;
- ADX, +DI, -DI and one-observation ADX change;
- RSI and one-observation RSI change;
- ATR;
- Stochastic K, D, spread, spread change and bullish/bearish crosses;
- volume per minute and same-session-slot volume ratio;
- up to six descriptive support checks;
- availability for every check;
- improved and regressed component lists;
- directional bias;
- within-session progression; and
- relation to the completed daily thesis.

At least four observed support checks are required for a complete indicator
assessment. Missing evidence remains unavailable; it is not counted as
bearish.

### 6.4 Timeframe comparison rules

ADX, RSI, Stochastic and MACD values are interpreted inside their own
timeframe histories. Their raw numeric values are never compared directly
between daily, 4-hour and 1-hour series.

A previous-session lower-timeframe history may warm the mathematics, but it
may not become an exposed prior opinion. Progression is based only on completed
observations from the current session.

### 6.5 Intraday volume normalization

Intraday volume is not:

- compared with full-session ADV20;
- projected linearly to a full session; or
- compared across unlike session buckets.

For each completed intraday observation:

1. divide its volume by its actual duration in minutes;
2. compare that rate with up to 20 prior observations from the same
   session-anchored slot; and
3. report the ratio and its change.

The implementation requires at least five comparable prior slots before this
comparison is treated as available.

## 7. Daily/intraday development states

The daily status and daily momentum state remain authoritative. Intraday
evidence creates a separate descriptive development state:

| State | Meaning |
|---|---|
| `DAILY_UNQUALIFIED` | The completed daily primary regime is absent |
| `INTRADAY_IGNITION_DAILY_UNQUALIFIED` | Both current-session views are supportive, but daily qualification is absent |
| `DAILY_MOMENTUM_INTRADAY_UNAVAILABLE` | Daily momentum exists, but no fresh completed intraday view is available |
| `DAILY_MOMENTUM_REGRESSING` | At least one fresh intraday view is regressing |
| `DAILY_MOMENTUM_PARTIALLY_SUPPORTED` | One fresh intraday view is supportive |
| `DAILY_MOMENTUM_MIXED` | Fresh evidence exists but is not directionally decisive |
| `TRUE_MOMENTUM_CANDIDATE` | Daily qualification passes and both fresh 4-hour and 1-hour views are supportive |

`TRUE_MOMENTUM_CANDIDATE` is a research state, not confirmation.

Until a separate owner-approved activation change:

```text
v17_classification_active = False
v17_true_momentum_confirmed = False
v17_operational_status_unchanged = True
```

## 8. New and young listings

Every valid completed stock/session observation remains in the research panel.

| Available completed sessions | History group | Treatment |
|---:|---|---|
| Fewer than 20 | Observation only | Record data; do not model momentum |
| 20–119 | Young listing | Young-listing research |
| 120–251 | Developing history | Reduced-history research |
| 252 or more | Established history | Standard-history research |

These boundaries are provisional research scaffolding. They are not classifier
thresholds.

Unavailable EMA200, weekly EMA50 and other long-history features remain blank
and have explicit availability fields. Missing evidence is neither positive
nor negative.

Point-in-time sector and industry may support:

- base rates for similar-age securities;
- fixed benchmark-relative strength;
- regime analysis; and
- cautious statistical shrinkage.

They may never create synthetic stock indicators. Any estimate using broader
context must identify the level used and reduce confidence when stock-level
history is limited.

## 9. Point-in-time daily research record

One feature record is created for every valid security/session combination,
not only for inherited BUY rows.

### 9.1 Identity and timing

Every record must identify:

- stable `security_id`;
- point-in-time ticker;
- security name where available;
- listing exchange;
- instrument/ETF identity;
- listing and delisting dates;
- point-in-time sector and industry where available;
- previous completed session;
- hypothetical entry session;
- available completed-session count;
- history group; and
- eligible research track.

### 9.2 Daily features

The record contains:

- completed daily OHLCV;
- EMA, weekly, MACD, ADX/DI, RSI, Stochastic and ATR evidence;
- exact feature-availability fields;
- 5-, 10-, 20-, 60- and 120-session historical returns;
- EMA slopes;
- prior-volume ratio;
- turnover;
- ATR-normalized extension;
- prior 52-week and post-listing range context; and
- plain descriptions of structure, participation and extension.

Descriptions are research aids, not recommendations.

### 9.3 Feature immutability

Features are calculated using information available through the recorded daily
foundation only. Future prices are joined after feature construction.

A change to any later price must not alter an earlier feature record.

## 10. Provisional future-outcome contract

The initial research contract uses:

- hypothetical entry at the open of the trading session immediately following
  the daily foundation;
- forward close-to-entry return over 5, 10 and 20 sessions;
- maximum favourable excursion over each horizon;
- maximum adverse excursion over each horizon; and
- a provisional ten-session path label using +2 ATR and -1 ATR barriers.

The entry session counts as session 1.

Outcome states must distinguish:

- upward barrier first;
- downside barrier first;
- neither barrier;
- both barriers touched in the same daily candle, order unknown;
- ATR unavailable; and
- future window incomplete.

An incomplete outcome is never assumed to be flat, failed or successful. The
ATR path is a distribution-analysis label, not an approved stop or target.

The outcome definition may be changed before research only through a
documented pre-analysis decision. It may not be optimized against the final
holdout.

## 11. Required promotion-quality data

### 11.1 Daily archive

The daily archive must contain:

- stable identifiers across ticker changes;
- point-in-time ticker and NYSE/Nasdaq listing status;
- equity/ETF identity;
- split- and distribution-adjusted daily OHLCV;
- listing and delisting dates;
- inactive and delisted securities;
- delisting return or documented terminal-value treatment;
- point-in-time sector and industry where available;
- corporate-action adjustment provenance; and
- immutable source and version identifiers.

The ingestion schema requires, at minimum:

- ticker or symbol;
- date, session date or timestamp;
- `security_id`;
- `listing_date`;
- `delisting_date`;
- `listing_exchange`;
- either `is_etf` or `instrument_type`; and
- open, high, low, close and volume.

A current-survivor-only archive is acceptable for a mechanical smoke test, but
not for efficacy, model selection or promotion.

### 11.2 Intraday archive

Incremental 1-hour/4-hour validation requires several years of:

- split-adjusted 30-minute OHLCV;
- regular-session timestamps in the exchange timezone;
- identity aligned with the daily archive;
- point-in-time NYSE/Nasdaq coverage;
- inactive and delisted names;
- corporate-action provenance; and
- sufficient pre-period history to warm 4-hour EMA200 and all other
  indicators.

Recent Yahoo intraday data is suitable for live diagnostics and short
mechanical smoke replays only. It is not acceptable multi-year evidence.

### 11.3 Archive acceptance audit

Before momentum results are examined:

1. Verify the schema and data types.
2. Check duplicate security/session rows.
3. Validate ticker-history continuity under stable identifiers.
4. Reconcile price coverage with listing and delisting dates.
5. Verify historical exchange and instrument scope.
6. Sample splits, distributions, ticker changes and delistings.
7. Check OHLC relationships, non-positive values, missing volume, stale prices,
   extreme returns and calendar gaps.
8. Report coverage by year, exchange, active status, history group and sector.
9. Quarantine rejected rows with explicit reasons.
10. Freeze source files, hashes and a dataset manifest.

The manifest must include source, extract/version date, coverage period,
security and row counts, file hashes, adjustment method, timezone, calendar
convention and known limitations.

## 12. Backtesting and validation architecture

### 12.1 General principles

- Use point-in-time data only.
- Prohibit random train/test splitting.
- Never use information later than the recorded decision timestamp.
- Separate feature construction from outcome joining.
- Evaluate multiple bull, bear, high-volatility and low-volatility regimes.
- Disclose costs, spread, slippage, liquidity and overlapping-position effects.
- Keep cohort results distinct from a capital-constrained portfolio result.
- Preserve reproducibility with immutable input versions and configuration.

### 12.2 Chronological research periods

The promotion study must define three ordered periods:

1. training;
2. calibration; and
3. untouched holdout.

If a forward outcome crosses the training or calibration boundary, that row is
excluded from that period. Incomplete holdout outcomes are also excluded.

Actual boundary dates are not yet approved. They must be selected from the
accepted archive's coverage and frozen before final holdout results are
examined.

The feature set, outcome contract, model family, probability-calibration
method, cost assumptions and promotion gates must also be frozen before the
holdout is opened.

### 12.3 Daily-only replay

A daily-only replay tests whether the completed-daily foundation and inherited
conditions are reproducible. It cannot validate the incremental value of
current-session 1-hour/4-hour evidence.

The reference replay used:

- measurement period: 2021-07-29 through 2026-07-29;
- eight requested years for EMA200 and completed-weekly warm-up;
- 3,445 current-master-file NYSE/Nasdaq non-ETF symbols;
- 3,236 processed symbols;
- 208 symbols with insufficient history;
- one symbol with no data;
- entry at the next trading-session open;
- exit at the fifth trading-session close; and
- no overlapping trades for the same symbol.

Because the universe came from a current master file, the replay remains
exposed to survivorship and historical-membership bias.

### 12.4 Multi-timeframe replay

At each historical execution cutoff:

1. expose daily data only through the session before the replay date;
2. expose only current-session 30-minute source bars completed by the cutoff;
3. reconstruct 1-hour and 4-hour observations using the exchange schedule
   known at that timestamp;
4. save the full daily/4-hour/1-hour diagnostic vector;
5. join future outcomes only after that vector is frozen;
6. compare identical daily candidates with and without intraday evidence; and
7. summarize the increment out of sample after costs.

The replay harness currently supports New York cutoffs at 10:30, 13:30, 15:30
and 16:00 and forward horizons of 1, 5, 10 and 20 sessions. These are harness
defaults, not approved final execution cutoffs. Final cutoffs must be frozen
before holdout testing.

## 13. Evidence established so far

### 13.1 Mechanics and temporal integrity

The baseline passed 78 deterministic/regression tests. The tests cover:

- regular-session and post-close daily handling;
- holidays and early closes;
- completed-week handling;
- source-bar completion cutoffs;
- 1-hour/4-hour short-tail exclusion;
- indicator calculations;
- current-session freshness;
- first-current-bar behavior;
- age-aware feature availability;
- future-outcome construction;
- chronological split purging;
- feature immutability; and
- plain-language output boundaries.

All changed Python modules compiled and whitespace checks passed at baseline.

### 13.2 Five-year inherited daily-rule result

| Window | Trades | Win rate | Mean return | Median | Profit factor |
|---|---:|---:|---:|---:|---:|
| 1 year | 8,954 | 50.86% | +0.1836% | +0.1272% | 1.0624 |
| 2 years | 15,124 | 49.66% | +0.0014% | 0.0000% | 1.0005 |
| 3 years | 21,494 | 50.09% | +0.0326% | +0.0177% | 1.0124 |
| 5 years | 30,620 | 49.59% | -0.0627% | -0.0110% | 0.9756 |

The five-year 1st/99th-percentile winsorized mean was -0.0813%. With an
illustrative 20-basis-point round-trip cost, the five-year mean was -0.2627%
and profit factor was 0.9015.

The rule set was negative in 2022, 2023, 2024 and 2025. Positive gross slices
in 2021 and partial 2026 became negative after the illustrative cost.

### 13.3 Inherited signal-family result

| Signal family | Trades | Mean return | Profit factor |
|---|---:|---:|---:|
| Momentum Extension | 25,107 | -0.1004% | 0.9605 |
| Early Momentum | 5,429 | +0.1099% | 1.0413 |
| EMA20 Midrange Recovery | 69 | +0.6107% | 1.2514 |
| Pullback/Oversold Recovery | 15 | -2.4337% | 0.5592 |

Momentum Extension produced 82% of trades and was negative before costs. The
two recovery families are too sparse for a conclusion. Early Momentum's gross
advantage did not survive a 20-basis-point assumption across the full sample.

### 13.4 Indicator cautions

Exploratory slices were heterogeneous and non-monotonic:

- ADX at or above 50: 921 trades, -1.6531% mean;
- RSI at or above 80: 1,999 trades, -0.6045% mean;
- inherited quality score 5: +0.3460% mean;
- inherited quality score 6: -0.3587% mean;
- inherited quality score 8: -0.2580% mean; and
- Early Momentum with volume ratio 1.00–1.20: +0.2613% gross, but only
  +0.0613% after 20 basis points.

These observations show why no single high indicator value, equal-weight score
or exploratory slice may be promoted without chronological calibration and
holdout evidence.

### 13.5 Research-panel smoke

A bounded one-security smoke retained 1,255 daily observations from 2021-07-29
through 2026-07-29 and exercised every history group.

It produced:

- 590 eligible training rows;
- 482 eligible calibration rows;
- 123 eligible holdout rows; and
- 20 boundary/incomplete exclusions in each period.

This proves mechanics only. A one-surviving-security smoke has no predictive
or economic meaning.

## 14. Current gate assessment

| Gate | Current status | Meaning |
|---|---|---|
| Completed-candle and calendar mechanics | Passed | Implementation foundation is reproducible |
| Point-in-time daily archive acceptance | Blocked | No compliant archive is present |
| Inherited daily-rule stability | Failed | Benchmark is negative gross and after costs over five years |
| Frozen chronological research | Not started | Requires an accepted archive and predeclared contract |
| Transparent daily model | Not started | Must follow base-rate and feature-stability research |
| Untouched daily holdout | Not started | Must remain unopened until all gates are frozen |
| Multi-year intraday increment | Blocked | No replayable several-year 30-minute archive |
| Live research-only observation | Not started | Requires a frozen daily and intraday candidate |
| Production activation | Not approved | Confirmation flags remain false |

## 15. Development program and promotion gates

### Phase P0 — Data and research-contract foundation

#### Gate G1: acquire and version the daily archive

Deliver:

- immutable daily files;
- dataset manifest;
- stable identity mapping;
- inactive/delisted coverage; and
- documented terminal-value and corporate-action treatment.

Exit only when identity, scope, provenance and hashes are complete.

#### Gate G2: accept the archive

Deliver:

- schema mapping;
- quality report;
- coverage report;
- exclusion ledger; and
- frozen accepted archive.

Exit only when material data defects and exclusions are quantified.

#### Gate G3: freeze the research contract

Freeze:

- outcome definitions;
- training, calibration and untouched-holdout dates;
- feature-availability rules;
- liquidity and regime definitions;
- transaction-cost and slippage assumptions;
- model families; and
- promotion gates.

Exit before any final holdout result is viewed.

### Phase P1 — Daily panel and benchmark evidence

#### Gate G4: build and reconcile the daily panel

Deliver:

- versioned point-in-time panel;
- build manifest;
- source-to-panel reconciliation;
- coverage by history group; and
- chronological eligibility summary.

Exit only when deterministic checks pass and every count difference is
explained.

#### Gate G5: establish base rates and inherited benchmarks

Measure unconditional 5-, 10- and 20-session outcomes by:

- year;
- broad market regime;
- history group and listing age;
- liquidity and turnover;
- exchange;
- sector/industry when point-in-time data exists; and
- active versus subsequently delisted status.

Then evaluate inherited scanner conditions on the identical eligible rows.
Report sample size, missingness, mean/median return, win rate, MFE, MAE,
barrier outcome and cost sensitivity.

Exit when the report is reproducible and exposes survivorship, regime,
liquidity and young-listing behavior.

### Phase P2 — Daily model research and decision

#### Gate G6: lock the daily candidate

Using training and calibration only:

1. test individual feature stability and monotonicity;
2. quantify missingness behavior;
3. test a small predeclared set of interpretable interactions;
4. build a transparent probability baseline;
5. calibrate its probabilities;
6. compare one nonlinear challenger only after the transparent model is
   stable; and
7. reject features dependent on one regime, sparse cohorts or unstable
   thresholds.

Evaluate calibration, ranking, return/MFE/MAE distributions, turnover and cost
sensitivity rather than relying on a single classification statistic.

Exit only after the feature set, model family, calibration method and
promotion thresholds are locked.

#### Gate G7: execute the untouched daily holdout

Run the locked pipeline once. Compare:

- unconditional base rates;
- inherited scanner rules;
- the transparent probability model; and
- the predeclared challenger.

Report uncertainty and results by regime, history group, liquidity, sector and
delisting status. A failed gate ends promotion work; it does not authorize
holdout threshold tuning.

Exit with either:

- a frozen daily research candidate approved for intraday-increment testing;
  or
- a documented no-promotion decision.

### Phase P3 — Intraday increment and operational observation

#### Gate G8: establish 1-hour/4-hour incremental value

Acquire and audit the multi-year 30-minute archive. Replay the frozen daily
candidate at predeclared cutoffs. Compare identical daily candidates with and
without completed current-session evidence.

Exit only if the increment is timestamp-correct, stable after costs across
regimes and not dependent on incomplete candles or prior-session intraday
opinions.

#### Live research-only gate

Run the frozen candidate in shadow mode and monitor:

- input coverage and data quality;
- probability calibration;
- regime and feature drift;
- candidate turnover;
- provider failures and latency;
- result stability; and
- operational exceptions.

All activation flags remain false throughout the observation period.

## 16. Interim goals and final goals

### 16.1 Completed foundation goal

Already achieved:

- completed-session temporal rules implemented;
- full-duration current-session aggregation implemented;
- point-in-time daily research record implemented;
- age-aware feature availability implemented;
- provisional outcome construction implemented;
- chronological split purging implemented;
- plain-language output implemented; and
- deterministic foundation tests passing.

### 16.2 Immediate interim goal

Acquire, version and audit the promotion-quality point-in-time daily archive.
Until this is complete, model or threshold changes are premature.

### 16.3 Daily research interim goal

Produce a reconciled all-security/all-session panel, unconditional base-rate
report and inherited-rule benchmark without opening the final holdout.

### 16.4 Daily model interim goal

Produce a transparent, calibrated daily probability model that is stable
across time, regimes, liquidity and history groups, then pass the untouched
daily holdout.

### 16.5 Multi-timeframe interim goal

Demonstrate whether completed current-session 1-hour/4-hour evidence adds
measurable value to the exact same frozen daily candidates.

### 16.6 Operational interim goal

Complete a research-only live observation period with stable data quality,
calibration and operations.

### 16.7 Final development goal

The final Momentum Engine should provide a timestamp-correct, explainable,
calibrated stock-level momentum assessment based on:

- an immutable completed-daily foundation;
- optional validated current-session development evidence;
- explicit data and indicator availability;
- stable out-of-sample probabilities;
- cost- and liquidity-aware evidence;
- plain-language explanations; and
- reproducible technical details.

### 16.8 Final activation goal

Production activation may be proposed only when:

1. the daily model passes its locked chronological holdout gates;
2. the intraday increment passes a separate multi-year out-of-sample gate;
3. results remain positive and stable after disclosed costs;
4. live shadow behavior is acceptable;
5. monitoring and rollback controls are defined; and
6. the owner approves a separate activation change.

Until then, no output may be called `TRUE_MOMENTUM_CONFIRMED`.

## 17. User-facing output contract

The visible workbook contains:

- `Summary`: execution totals and data-quality information;
- `Review`: one plain-language row per security; and
- hidden `Technical Data`: reproducibility fields.

The visible review and text log should:

- use previous-session/current-session terminology;
- exclude internal version names and activation flags;
- explain daily structure, participation and extension;
- explain available 4-hour and 1-hour evidence;
- identify missing or incomplete evidence plainly; and
- avoid presenting a research state as a recommendation.

Technical output must retain the complete diagnostic vector needed to
reproduce every displayed conclusion.

## 18. Implementation component map

| Component | Responsibility |
|---|---|
| `Live_Scanner_v17.py` | Live previous-session daily foundation and non-binding current-session review |
| `v17_mtf.py` | U.S. calendar, completed-source filtering, 1-hour/4-hour construction and diagnostics |
| `v17_mtf_replay.py` | Timestamp-correct daily/30-minute cutoff replay |
| `v17_us_daily_backtest.py` | Multi-year inherited completed-daily reference replay |
| `v17_analyze_daily_results.py` | Descriptive daily cohort analysis |
| `momentum_research.py` | Age-aware daily features, future outcomes and chronological splitting |
| `build_momentum_research_panel.py` | Strict long-form archive ingestion and panel writing |
| `validate_momentum_research_panel.py` | Chronological unconditional-outcome audit |
| `plain_language_output.py` | Readable workbook review and formatting |
| `tests` | Deterministic, temporal and regression protection |

## 19. Reproduction and validation commands

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the live research review:

```powershell
python .\Live_Scanner_v17.py `
  -c AAPL MSFT NVDA `
  --live-candle-mode completed `
  -o .\output\Momentum_Review.xlsx
```

Build the daily research panel:

```powershell
python .\build_momentum_research_panel.py `
  D:\path\us_equity_daily_archive.parquet `
  --output-dir .\output\Momentum_Research_Panel
```

Validate the panel after period boundaries are frozen:

```powershell
python .\validate_momentum_research_panel.py `
  .\output\Momentum_Research_Panel\Momentum_Research_Panel.parquet `
  --training-end YYYY-MM-DD `
  --calibration-end YYYY-MM-DD `
  --output-dir .\output\Momentum_Research_Validation
```

Replay multi-timeframe evidence after a compliant archive exists:

```powershell
python .\v17_mtf_replay.py `
  --daily-file D:\path\daily_archive.parquet `
  --intraday-file D:\path\intraday_30m_archive.parquet `
  --cutoff-times 10:30,13:30,15:30,16:00 `
  --forward-sessions 1,5,10,20 `
  --output-dir .\output\Current_Session_Replay
```

Run deterministic validation:

```powershell
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile `
  Live_Scanner_v17.py v17_mtf.py v17_mtf_replay.py `
  momentum_research.py plain_language_output.py `
  build_momentum_research_panel.py `
  validate_momentum_research_panel.py
git diff --check
```

These checks prove implementation consistency, not predictive efficacy.

## 20. Guardrails and stop rules

Do not:

- use random train/test splitting;
- optimize thresholds on the final holdout;
- reopen the holdout after a failed gate to tune the model;
- calculate a feature with information later than its decision timestamp;
- allow incomplete or extended-hours candles into completed-candle logic;
- compare raw indicator levels across different timeframes;
- use yesterday's intraday opinion as today's progression baseline;
- treat missing evidence as positive, negative or zero;
- fill missing stock history with sector-derived price indicators;
- depend on current-survivor-only coverage for efficacy evidence;
- silently repair, discard or recode bad archive rows;
- treat an incomplete outcome as flat, failed or successful;
- confuse a signal-cohort drawdown with portfolio drawdown;
- ignore costs, spread, liquidity or position overlap;
- promote an exploratory diagnostic slice as a gate;
- let watchlist membership change a security's result;
- let concurrency change calculations or classifications; or
- call a present shadow state genuine momentum.

Stop promotion work when a locked gate fails. Record the failure and return to
research with a new future holdout rather than reusing the failed holdout.

## 21. Known limitations

The existing five-year daily replay:

- uses a current master-file universe;
- is exposed to survivorship and point-in-time membership bias;
- is a signal-cohort replay rather than a portfolio simulation;
- does not model spread, slippage, borrow, stops, position sizing or portfolio
  concurrency; and
- cannot prove 1-hour/4-hour incremental value.

The current Yahoo intraday interface:

- supplies only recent history;
- has no native historical 4-hour series; and
- is unsuitable as the several-year activation archive.

## 22. Decisions that remain open

The following must be decided at the specified gate, not assumed now:

- daily and intraday data vendor/source;
- exact accepted archive version;
- training, calibration and holdout dates;
- market-regime definition;
- liquidity buckets;
- cost and slippage assumptions;
- final outcome target or targets;
- final feature set;
- transparent model family;
- nonlinear challenger family;
- probability-calibration method;
- promotion thresholds;
- final replay cutoffs;
- live-shadow duration;
- monitoring tolerances; and
- rollback procedure.

Every such decision must be versioned before the evidence it governs is
examined.

## 23. Immediate continuation instruction

The next session must begin with the promotion-quality daily archive:

1. identify or place the candidate archive;
2. record immutable version information and hashes;
3. map fields to the required schema;
4. run the acceptance audit;
5. produce the quality, coverage and exclusion reports;
6. freeze the research configuration and chronological boundaries; and
7. build the daily panel only after gates G1–G3 pass.

No classifier, threshold or BUY-rule work should begin before this sequence is
complete.
