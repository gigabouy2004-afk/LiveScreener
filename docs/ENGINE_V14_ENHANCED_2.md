# V14 Enhanced 2 Supplementary Context

## Purpose

`Live_Scanner_v14_Enhanced_2.py` is a separate, opt-in variant of V14
Enhanced. It preserves the existing Setup/Trend/Momentum classifier and adds
supplementary information only after a ticker has already survived all core
rules and is classified `BUY`.

The following scripts remain unchanged and independently runnable:

- `Live_Scanner_v14.py`
- `Live_Scanner_v14_Enhanced.py`

## Non-regression contract

V14 Enhanced 2 does not use a supplementary rating, analyst opinion, price
target, or earnings date to:

- create a BUY;
- convert BUY to HOLD/IGNORE/ERROR;
- promote a HOLD to BUY;
- change BUY#3 versus BUY#4;
- change confidence, risk, or signal score; or
- change EMA, MACD, stochastic, ADX, volume, liquidity, or extension policy.

Only rows whose final core `status` is `BUY` contact the supplementary
providers. Non-BUY rows receive `supplementary_status=NOT_APPLICABLE`.

If any supplementary calculation or provider call fails, the core row is
retained. The supplementary fields report `UNKNOWN`, `PARTIAL`, or
`UNAVAILABLE`; the scanner does not produce an `ERROR` for that failure.

## Supplementary technical rating

The technical rating is an independent 1-day calculation from the exact OHLCV
frame already used by the scanner. It follows the broad structure of
TradingView's published technical-rating method:

- 15 moving-average/filter votes; and
- 11 oscillator votes.

Each vote is `-1`, `0`, or `+1`. Scores are normalized to `-1..+1` and mapped
to:

- `STRONG_BUY` above `+0.50`;
- `BUY` above `+0.10` through `+0.50`;
- `NEUTRAL` from `-0.10` through `+0.10`;
- `SELL` from `-0.50` through below `-0.10`; and
- `STRONG_SELL` below `-0.50`.

The output is labelled `TV_LIKE_15_MA_11_OSC`. It is not scraped TradingView
data and may differ because the price feed, candle state, and calculation
details differ.

Key fields are:

- `technical_rating`, `technical_rating_score`;
- `technical_ma_rating`, `technical_ma_score`;
- `technical_oscillator_rating`, `technical_oscillator_score`; and
- `technical_buy_signals`, `technical_neutral_signals`,
  `technical_sell_signals`.

Published method reference:
`https://www.tradingview.com/support/solutions/43000614331-technical-ratings/`

## Analyst consensus

Current analyst counts and price targets come from Yahoo Finance through
`yfinance`. The current `0m` recommendation counts are retained in
`analyst_breakdown`:

`SB=<strong buy>;B=<buy>;H=<hold>;S=<sell>;SS=<strong sell>`

The independent normalized score weights the categories as:

- Strong Buy `+1.0`;
- Buy `+0.5`;
- Hold `0`;
- Sell `-0.5`; and
- Strong Sell `-1.0`.

No available current consensus becomes `analyst_rating=UNKNOWN`, not an engine
error. Price-target fields include low, mean, median, high, and mean-target
upside from the scanner's current price.

This is Yahoo consensus, not TradingView's proprietary/FactSet analyst rating.

## Earnings event context

Detailed Yahoo earnings timestamps are preferred; the Yahoo calendar date is a
fallback. The default warning windows are:

- `UPCOMING`: earnings today or within 7 calendar days;
- `RECENT`: earnings reported today or within the last 5 calendar days;
- `NONE`: a known future date exists outside the warning window; and
- `UNKNOWN`: no reliable future date is available.

Known timestamps are labelled:

- `BMO`: before market open;
- `AMC`: at or after market close;
- `MARKET_HOURS`: during the exchange session; or
- `UNKNOWN`: the source supplied a date without a reliable time.

A historical earnings record without a future date does not prove the absence
of event risk. It therefore remains `UNKNOWN`.

## Existing stochastic policy disclosure

The core policy is unchanged:

- base BUY stochastic limit: `80`;
- previous-positive-session Early Momentum allowance: `90`; and
- previous-positive-session Momentum Continuation allowance: `100`.

V14 Enhanced 2 only makes these existing limits explicit in the terminal and
log summary.

## Input and output

Comma-separated direct codes remain valid without inserted spaces:

```powershell
python "D:\Tools\07_LiveScanner\Live_Scanner_v14_Enhanced_2.py" `
  -c RTX,ITW,TXT,NEU,SIF,GEF-B `
  --live-candle-mode auto `
  -o "D:\TMP\V14_Enhanced_2_Result.xlsx"
```

The workbook continues to contain `Summary` and `Details` sheets. Enhanced 2
adds 32 supplementary columns to `Details` and four BUY-only summary lines.

## Validation

The full automated suite contains 41 passing tests:

- 30 inherited V14 Enhanced tests;
- rating boundary and 15/11 vote-count checks;
- analyst and earnings parsing checks;
- missing/stale-data behavior;
- proof that non-BUY rows do not contact supplementary providers;
- proof that provider failures leave BUY classification unchanged; and
- deterministic same-frame equality between the original and Enhanced 2 core
  `evaluate_frame` output.

The 2026-07-27 U.S. intraday parity run used:

`RTX,ITW,TXT,NEU,SIF,GEF-B`

Both scripts returned six BUYs, zero errors, and the same breakup:

- 5 `Buy_Momentum_Extension`;
- 1 `Buy_Early_Momentum`.

The generated validation workbooks are:

- `D:\TMP\28-07-2026-V14Enhanced-Parity-Industrial.xlsx`
- `D:\TMP\28-07-2026-V14Enhanced2-Parity-Industrial.xlsx`
