# LiveScreener

LiveScreener is a per-ticker technical baseline scanner. The current development
baseline is `Live_Scanner_v14_Enhanced.py`; `Live_Scanner_v14.py` is retained as
the unchanged V14 reference. `Live_Scanner_v15.py` is an experimental shadow
engine: it preserves V14 classifications while recording stricter momentum-
quality and entry-quality assessments for validation.

The engine is a screener, not an automated trading system. It reports a
repeatable status for each ticker and expects the end user to perform offline
verification before acting on a candidate.

## Current release

- Release date: 2026-07-25
- Reference baseline: `Live_Scanner_v14.py`
- Current development baseline: `Live_Scanner_v14_Enhanced.py`
- Experimental shadow engine: `Live_Scanner_v15.py`
- Python: 3.10 or later
- Market data: Yahoo Finance through `yfinance`
- Default concurrency: 3 independent ticker workers
- Output: multi-sheet XLSX plus a text execution log

## Quick start

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run a CSV watchlist:

```powershell
python .\Live_Scanner_v14_Enhanced.py `
  -i "D:\path\watchlist.csv" `
  -o "D:\path\scan-output.xlsx" `
  --workers 3
```

Run selected symbols:

```powershell
python .\Live_Scanner_v14_Enhanced.py `
  -c CAT GE RTX UNP DE `
  -o "D:\path\selected-symbols.xlsx"
```

Run historical as-of validation:

```powershell
python .\Live_Scanner_v14_Enhanced.py `
  -c CAT GE RTX UNP DE `
  --as-of-dates 2026-07-22,2026-07-23,2026-07-24 `
  --live-candle-mode completed `
  -o "D:\path\historical-validation.xlsx"
```

Run V15 shadow validation without changing V14 classifications:

```powershell
python .\Live_Scanner_v15.py `
  -i "D:\path\watchlist.csv" `
  --live-candle-mode completed `
  -o "D:\path\v15-shadow-output.xlsx"
```

## Design contract

The engine follows five non-negotiable rules:

1. Every ticker is evaluated independently. Classification cannot depend on the
   input universe, another ticker, sector performance, or thread completion
   order.
2. Thread pooling changes execution speed only.
3. `Max-Count` and `Max-Buys` are optional poll-boundary continuation triggers.
   The complete final poll is retained.
4. The fixed core calculation window determines the signal. Adaptive
   MAX/5Y/1Y history is advisory output only.
5. Currency and market-session handling follow the ticker's listing metadata;
   the scanner is not restricted to U.S. listings.

## Repository contents

- `Live_Scanner_v14.py` — unchanged V14 reference baseline.
- `Live_Scanner_v14_Enhanced.py` — enhanced threaded and historically
  contextual scanner.
- `Live_Scanner_v15.py` — experimental shadow scanner with frozen V14 output
  classifications and separate momentum/entry audit states.
- `docs/ENGINE_V15_SHADOW.md` — V15 hypotheses, thresholds, state logic, and
  activation safeguards.
- `docs/VALIDATION_V15_SHADOW_2026-07-27.md` — V14 parity, unit, and historical
  shadow-state validation.
- `docs/ENGINE_V14_ENHANCED.md` — complete engine and operator documentation.
- `docs/VALIDATION_2026-07-25.md` — XLI regression, full-U.S. run, and
  independent live-feed audit.
- `docs/VALIDATION_P1_HARDENING_2026-07-27.md` — approved volume, U.S.
  liquidity, extreme-extension, and data-through hardening evidence.
- `docs/VALIDATION_POSITIVE_REGIME_2026-07-27.md` — positive-regime scope,
  GLOSTER correction, invariant checks, and historical replay evidence.
- `docs/HANDOVER_AND_SESSION_SIGNOFF_2026-07-25.md` — closure state, runbook,
  hashes, open risks, and restart instructions.
- `CHANGELOG.md` — release history.

## Release status

Implementation and reproducibility validation are complete. The owner-approved
hardening policies now require a `0.60` current-volume floor, require USD
1 million ADV20 turnover for U.S. BUY candidates, and label BUY candidates more
than 5 ATR above EMA50 as `BUY_EXTENDED_REVIEW`.

BUY#4 additionally requires a fresh MACD signal-line crossover above zero with
a positive histogram. Momentum continuation requires a sustained expansion
window with its latest two histogram bars positive. Negative-histogram
improvement cannot qualify or strengthen a signal, and the engine does not
classify pre-bull or pre-bear crossover candidates.

International absolute liquidity thresholds remain intentionally disabled until
currency-aware or exchange-specific policies are defined. Low-liquidity
daily-versus-intraday feed-quality warnings remain a documented future item.
