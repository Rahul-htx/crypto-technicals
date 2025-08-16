

# CryptoTechnicals — Technical Analysis Data Engine

## 🧠 Human‑Readable Summary

### Intent
Build a lightweight Python command‑line tool that **pulls historical price/volume data from the CoinGecko API, automatically computes a standardized bundle of technical indicators, and dumps both machine‑readable summaries (JSON / CSV / SQLite) and ready‑to‑share charts (PNG) for a watch‑list of crypto assets**. The output feeds ChatGPT (or your own LLM) so it can surface high‑conviction trade setups without manual screenshots.

### Expected Outcomes
- Produce up‑to‑date indicator snapshots for every selected coin and timeframe.
- Export compressed JSON (and optional CSV / SQLite) plus PNG charts per run.
- Finish a 20‑coin, 90‑day 1‑h + multi‑year daily run in < 2 min on a MacBook Pro.
- Require **no** manual screenshots or GUI interaction.

### High‑Level Design
```
┌──────────┐      ┌──────────────┐      ┌──────────────┐
│  config   │───►│  fetch layer  │───►│  indicator    │
└──────────┘      │  (CoinGecko) │      │  calculator  │
                  └──────────────┘      └──────────────┘
                          │                     │
                          ▼                     ▼
                 ┌────────────────┐    ┌────────────────┐
                 │ JSON / SQLite  │    │ chart exporter │
                 └────────────────┘    └────────────────┘
```
- **Stateless**: each run is atomic; no Redis or websockets.
- **Modular**: swap the fetcher for an exchange API later if finer granularity is required.
- **Python‑native**: `requests`, `pandas`, `ta‑lib`, `matplotlib`.

### Core Algorithms
| Category        | Algorithm & Params                     | Use‑case                               |
|-----------------|----------------------------------------|----------------------------------------|
| **Trend**       | EMA(20/50/200), SMA(20/50/200)         | Regime detection                       |
| **Momentum**    | RSI(14), Stochastic(14,3,3), MACD(12,26,9) | Entry/exit timing                      |
| **Volatility**  | Bollinger Bands(20,2), ATR(14)         | Stop sizing, squeeze detection         |
| **Trend Strength** | ADX(14)                             | Filter sideways chop                   |
| **Volume**      | OBV, 20‑period Vol‑MA                  | Confirm breakouts                      |
| **Rel‑Strength**| Close/BTC & Close/ETH ratios + EMA(50/200) | Asset rotation                         |

---

## 🔧 Technical Specification

### File Structure
```
crypto_technicals/
├── src/
│   ├── cli.py
│   ├── config_loader.py
│   ├── fetch/
│   │   ├── coingecko.py
│   │   └── __init__.py
│   ├── indicators/
│   │   ├── ema.py
│   │   ├── sma.py
│   │   ├── rsi.py
│   │   ├── macd.py
│   │   ├── bollinger.py
│   │   ├── atr.py
│   │   ├── adx.py
│   │   ├── obv.py
│   │   └── __init__.py
│   ├── exporter/
│   │   ├── json_exporter.py
│   │   ├── csv_exporter.py
│   │   ├── sqlite_exporter.py
│   │   ├── chart_exporter.py
│   │   └── __init__.py
│   ├── pipeline.py
│   └── utils/
│       ├── time_utils.py
│       ├── math_utils.py
│       └── logging_utils.py
├── tests/
│   ├── test_fetch.py
│   ├── test_indicators.py
│   ├── test_pipeline.py
│   └── fixtures/
├── devlogs/
├── data/
│   └── runs/<timestamp>/
├── README.md
├── config.yaml
├── requirements.txt
└── pyproject.toml
```

### Key Modules
- **`cli.py`** — entry point (`python -m crypto_technicals --coins eth,btc --horizons intraday,swing`)
- **`fetch/coingecko.py`** — wraps `/market_chart/range`, handles retries & auto‑granularity limits.
- **`pipeline.py`** — orchestrates fetch → resample → indicator calc → export.
- **`exporter/chart_exporter.py`** — renders a 3‑pane PNG (price+EMAs, RSI, MACD).

### Configuration (`config.yaml`)
```yaml
coins: [eth, btc, sol, link]
horizons:
  intraday:
    lookback_days: 30
    granularity: 1h
  swing:
    lookback_days: 400   # ≈1.1 y
    granularity: 1d
indicators: [ema, rsi, macd, bollinger, atr, adx, obv]
export:
  json: true
  csv: false
  sqlite: true
  charts: true
output_dir: data/runs
```

### Testing Strategy
- **Unit**: validate each indicator against TA‑Lib reference values.
- **Integration**: full BTC pipeline smoke‑test.
- **Performance**: 20‑coin run must finish < 120 s on 8‑core CPU.

---

## ✅ Required Best Practices

(Sections below reproduced verbatim from the project template) fileciteturn0file0L1-L120

---

## Known Limitations & Future Extensions
1. **CoinGecko auto‑granularity**: ≤ 30 d fine; > 30 d locked to daily. Swap in Binance API for 4 h candles > 30 d if needed.
2. **Analytics‑only**: no order execution; hook into brokers later.
3. **On‑chain metrics**: not covered; could add Glassnode interface.

---

## 📘 README Must Include
- Purpose & scope
- Installation steps
- Quick‑start example
- Sample JSON + chart outputs
- Changelog & timestamp

---

**Author**: Rahul Bijlani  
**Date**: _auto‑inserted by commit hook_