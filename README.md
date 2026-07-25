# LiveScreener

LiveScreener is a per-ticker technical baseline scanner. The current development
baseline is `Live_Scanner_v14_Enhanced.py`; `Live_Scanner_v14.py` is retained as
the unchanged V14 reference.

The engine is a screener, not an automated trading system. It reports a
repeatable status for each ticker and expects the end user to perform offline
verification before acting on a candidate.

## Current release

- Release date: 2026-07-25
- Reference baseline: `Live_Scanner_v14.py`
- Current development baseline: `Live_Scanner_v14_Enhanced.py`
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
- `docs/ENGINE_V14_ENHANCED.md` — complete engine and operator documentation.
- `docs/VALIDATION_2026-07-25.md` — XLI regression, full-U.S. run, and
  independent live-feed audit.
- `docs/HANDOVER_AND_SESSION_SIGNOFF_2026-07-25.md` — closure state, runbook,
  hashes, open risks, and restart instructions.
- `CHANGELOG.md` — release history.

## Release status

Implementation and reproducibility validation are complete. Production-quality
signal signoff remains conditional on the owner deciding how to handle
low-liquidity candidates and highly extended momentum candidates. These known
limitations are documented; they were not silently changed during handover.
