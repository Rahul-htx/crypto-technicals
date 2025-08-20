# Snapshot Exporter – Design & Implementation Plan  
_Designed 2025-08-20_

---

## 1. Purpose  

Create a **single, fixed-schema “snapshot” JSON artefact** that always lives at  
`data/snapshots/latest_snapshot.json` (with a timestamped copy kept alongside).  
This file contains only the information an LLM needs to craft real-time, technically-driven trading recommendations while remaining compact enough to fit comfortably inside a 200 k-token context window.

---

## 2. High-level Requirements  

| # | Requirement |
|---|-------------|
| R1 | Same schema on every run (no branching on horizon). |
| R2 | Sections may be _empty_ but never missing → parsers stay simple. |
| R3 | 3 population “modes” (5-min, hourly, daily) toggle **how much** data, not **shape**. |
| R4 | Always overwrite `latest_snapshot.json`; also write `snapshot_<ISO-timestamp>.json`. |
| R5 | Integrate with existing `Pipeline` _after_ all other exporters. |
| R6 | No scheduler work yet; CLI args decide the mode. |

---

## 3. Combined Snapshot JSON Schema  

**Single file containing all horizons to eliminate confusion and data loss:**

```jsonc
{
  "meta": {
    "last_updated":       "2025-08-20T14:35:00Z",
    "horizons_present":   ["intraday", "swing"],
    "coins_tracked":      ["btc","eth","sol","link","xrp","trx"]
  },

  "intraday": {
    "meta": {
      "run_timestamp":      "2025-08-20T14:35:00Z",
      "horizon":            "intraday",
      "granularity":        "1h",
      "history_last_updated":    "2025-08-20T13:35:00Z",
      "long_stats_last_updated": "2025-08-20T00:00:00Z",
      "data_completeness": {
        "price":        true,
        "indicators":   true,
        "news":         false
      }
    },
    "market_overview": {
      "btc_dominance_pct":      52.3,
      "total_market_cap_usd":   2.145e12,
      "sentiment":              "risk_off",
      "sector_leaders_24h": [
        {"name":"AI","perf_pct":7.8},
        {"name":"L2","perf_pct":4.4}
      ]
    },
    "cross_coin": {
      "top_momentum_24h":   ["sol","link","eth"],
      "top_volume":         ["btc","eth"],
      "lowest_volatility":  ["btc","xrp","trx"]
    },
    "coins": {
      "<symbol>": {
        "price": 64254.33,
        "pct_change": { "1h":-0.3, "24h":-1.1, "7d":3.2 },
        "rsi_14": 48.7, "rsi_state": "neutral",
        "macd_hist": -0.15, "macd_state": "bearish_cross",
        // ... all indicators with categorical signals
        // Optional: "price_history", "indicator_history" arrays
      }
    },
    "news": { "headline_count": 0, "by_coin": {}, "global_sentiment": "neutral" }
  },

  "swing": {
    "meta": {
      "run_timestamp":      "2025-08-20T14:30:00Z",
      "horizon":            "swing", 
      "granularity":        "1d",
      "history_last_updated":    "2025-08-20T12:00:00Z",
      "long_stats_last_updated": "2025-08-19T00:00:00Z",
      "data_completeness": { "price": true, "indicators": true, "news": false }
    },
    // Same structure as intraday but with daily data
    "market_overview": { /* daily market view */ },
    "cross_coin": { /* daily rankings */ },
    "coins": { /* daily candle data & indicators */ },
    "news": { /* shared or daily-specific news */ }
  }
}
```

---

## 4. Indicator → Categorical Signal Thresholds  

| Indicator | Field | Logic |
|-----------|-------|-------|
| RSI-14 | `rsi_state` | `>70` → `overbought`, `<30` → `oversold`, else `neutral` |
| MACD Hist | `macd_state` | sign flips ↑ → `bullish_cross`, sign flips ↓ → `bearish_cross`, else `neutral` |
| EMA 50/200 | `ema_50_200` | above/below/crossing_up/crossing_down |
| %-Bollinger | `bb_state` | `>1` `above_band`, `<0` `below_band`, else `inside` |
| ADX-14 | `trend_strength` | `>25` strong, else weak |
| OBV slope | `obv_trend` | regression slope sign over last 20 periods |

---

## 5. Automatic Freshness Detection  

The exporter automatically determines what data to include based on **data boundaries** crossed since last update:

| Data Type | Update Logic | Rationale |
|-----------|--------------|-----------|
| Core snapshot | Every run | Always updated (price, latest indicators, cross-coin rankings) |
| History arrays | **Data boundary crossed** | Include if we've crossed a meaningful time boundary for the granularity |
| Long-horizon stats | **Daily boundary crossed** | Include if we've crossed a day boundary (00:00 UTC) |

**Boundary Detection Logic:**
- **Hourly data (1h, 4h)**: Update history if `last_run.hour != current_run.hour`
- **Daily data (1d)**: Update history if `last_run.date() != current_run.date()`
- **Long stats**: Always update if `last_run.date() != current_run.date()`

**Edge Case Example:**
- 11:55 PM run → normal update
- 12:05 AM run → `include_history=True` (crossed hour/day boundary, new API data available!)

**Override flags** (optional):
- `--force-hourly`: Force include history arrays regardless of boundaries
- `--force-daily`: Force include long-horizon stats regardless of boundaries

---

## 6. File & Directory Layout  

```
data/
└─ snapshots/
   ├─ snapshot_2025-08-20T14-35-00Z.json   (timestamped backup)
   └─ latest_snapshot.json                 (combined file with all horizons)
```

**Key Changes:**
- `latest_snapshot.json` now contains **all horizons** in separate sections
- Each horizon run patches only its own section, preserving others
- No more data loss when multiple horizons run back-to-back
- LLM can access both `snapshot["intraday"]` and `snapshot["swing"]` from one file

---

## 7. Implementation Steps  

### 7.1  SnapshotExporter (Modified)

* Location: `src/exporter/snapshot_exporter.py`  
* Public method: `export(results: Dict[str,Any], horizon: str, force_hourly: bool, force_daily: bool)`  
* **New Responsibilities:**
  1. Load existing `latest_snapshot.json` if it exists
  2. Build horizon-specific payload using existing helper methods  
  3. Patch `combined_snapshot[horizon] = new_payload`
  4. Update top-level meta (last_updated, horizons_present)
  5. Write both timestamped backup and combined latest file

### 7.2  Integration (Unchanged)

1. Already instantiated in `Pipeline.__init__`  
2. Already called after existing exporters
3. **No changes needed** - just modify the exporter internals  

### 7.3  CLI additions  

```
python -m src.cli                    # default - auto-detects freshness
python -m src.cli --force-hourly     # force include history arrays
python -m src.cli --force-daily      # force include long-horizon stats
```

* The CLI passes override flags to `Pipeline.run()` but freshness detection is automatic.  

---

## 8. Out-of-Scope (for this PR)  

* Actual scheduling / cron / APScheduler integration.  
* CryptoPanic news fetcher (placeholder section will stay empty).  
* Back-propagating snapshot data into persistent DBs.  

---

## 9. Acceptance Criteria  

1. **Combined file structure**: `latest_snapshot.json` contains all horizons in separate sections
2. **No data loss**: Running intraday then swing preserves intraday data in combined file  
3. **Boundary logic**: Each horizon section updates only when data boundaries are crossed
4. **Backward compatibility**: Timestamped files still created for audit trail
5. **Schema validation**: Combined JSON validates against new schema structure
6. **LLM ready**: Can access `snapshot["intraday"]["coins"]["btc"]["price"]` vs `snapshot["swing"]["coins"]["btc"]["price"]`  

---

## 10. Future Extensions  

* Merge CryptoPanic headlines into the `"news"` section every 30 minutes.  
* Add an `"llm_recommendations"` section so the agent can write back its reasoning & signals.  
* Optionally store snapshots in SQLite/Parquet for analytics beyond the LLM.

---
