# CryptoTechnicals — Comprehensive Crypto Intelligence Engine

A powerful Python command-line tool that provides **complete cryptocurrency market intelligence** by combining technical analysis, fundamental data, market sentiment, sector rotation analysis, and global market trends. Designed to feed AI/LLM systems with the richest possible context for cryptocurrency analysis and trading decisions.

## 🎯 Purpose & Scope

**CryptoTechnicals** is designed to:
- **Technical Analysis**: Historical OHLCV data + 8 comprehensive technical indicators
- **Fundamental Analysis**: Project metadata, tokenomics, development activity, community metrics
- **Market Intelligence**: Global market trends, sector rotation, dominance analysis (news not available via CoinGecko API)
- **Liquidity Analysis**: Exchange listings, trading venues, CEX/DEX breakdown
- **LLM-Ready Exports**: Structured JSON/CSV/SQLite + visual charts for AI consumption
- **🆕 Combined Snapshots**: Single file containing all timeframes with automatic freshness detection

Perfect for **AI-powered trading systems**, researchers, and analysts who need the **most comprehensive crypto market context** available, all automated and ready for LLM analysis.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Rahul-htx/crypto-technicals.git
cd crypto-technicals

# Install dependencies
pip install -r requirements.txt

# Set up your CoinGecko Pro API key
echo "COINGECKO_API_KEY=your_api_key_here" > .env

# Test installation
python -m src.cli --coins bitcoin --horizons intraday --verbose
```

### Basic Usage

```bash
# Run with default configuration
python -m src.cli

# Specify coins and horizons
python -m src.cli --coins eth,btc,sol --horizons intraday,swing

# Use custom configuration file
python -m src.cli --config my_config.yaml

# Enable verbose logging
python -m src.cli --verbose

# Override output directory
python -m src.cli --output-dir /path/to/custom/output
```

## 📊 Streamlined Data Outputs

### Optimized Market Intelligence Package
Every run generates **aggregated data files** for maximum LLM efficiency:

```
data/runs/20250819_185950/
├── Technical Analysis:
│   ├── intraday/all_coins_1h.json (aggregated hourly data)
│   ├── swing/all_coins_1d.json (aggregated daily data)
│   └── crypto_technicals_*.db (SQLite databases)
│
└── Market Intelligence:
    ├── market_context.json (unified intelligence)
    ├── metadata.json (project fundamentals)
    ├── categories.json (sector rotation)
    ├── global.json (macro trends)
    └── tickers.json (liquidity analysis)
```

### Sample Outputs

**Aggregated Technical Data** (`all_coins_1h.json`):
```json
{
  "metadata": {
    "horizon": "intraday", "granularity": "1h", 
    "coins": ["bitcoin", "ethereum"], "total_coins": 2
  },
  "coins": {
    "bitcoin": {
      "latest_values": { "close": 43250.67, "rsi_14": 58.23, "macd": 125.45 },
      "data": [{ "datetime": "2025-08-19T18:00:00", "close": 43250.67, ... }]
    }
  },
  "cross_coin_analysis": {
    "performance_ranking": ["ethereum", "bitcoin"],
    "volatility_comparison": { "bitcoin": 12.3, "ethereum": 15.7 }
  }
}
```

**Unified Market Context** (`market_context.json`):
```json
{
  "metadata": {
    "coins_tracked": ["bitcoin", "ethereum"],
    "data_sources": ["global_market", "sector_analysis", "coin_fundamentals"],
    "note": "News data not available via CoinGecko Pro API"
  },
  "global_market": {
    "market_overview": { "total_market_cap_usd": 3882142856426.52, "bitcoin_dominance_percentage": 57.94 },
    "dominance_analysis": { "dominance_signals": [...] }
  },
  "market_summary": {
    "market_sentiment": "risk_off",
    "key_insights": ["Bitcoin dominance at 58.0% suggests market seeking safety"],
    "missing_sources": ["liquidity_analysis"]
  }
}
```

**Sector Rotation Analysis**:
```json
{
  "sector_analysis": {
    "top_performers_24h": [
      {"name": "Trading Bots", "market_cap_change_24h": 201.67},
      {"name": "DeFi", "market_cap_change_24h": 15.42}
    ],
    "sector_rotation_signals": [{
      "signal_type": "sector_breakout",
      "strength": "high"
    }]
  }
}
```

### Visual Outputs
- **Multi-panel technical charts** (price + EMAs, RSI, MACD)
- **Sector comparison charts** for rotation analysis
- **High-resolution PNGs** ready for reports and presentations

## ⚙️ Configuration

Edit `config.yaml` to customize your analysis:

```yaml
coins: [ethereum, bitcoin, solana, chainlink, ripple, tron, sui]
horizons:
  intraday:
    lookback_days: 30
    granularity: 1h
  swing:
    lookback_days: 400
    granularity: 1d
indicators: [ema, sma, rsi, macd, bollinger, obv, atr, adx]
export:
  json: true
  csv: false
  sqlite: true
  charts: false                   # Disabled by default for cleaner output
  individual_coin_files: false   # Only export aggregated files by default

# Enhanced Market Intelligence Collection
market_data:
  collect_news: false             # CoinGecko Pro API does not provide reliable news headlines
  collect_metadata: true          # Project fundamentals & dev activity
  collect_categories: true        # Sector rotation analysis
  collect_global: true           # Market cap, dominance, macro trends
  collect_tickers: true          # Exchange listings & liquidity
  collect_onchain: false         # DEX data (advanced, when available)
  
  update_frequencies:            # Control data collection frequency
    # news: "every_run"            # disabled - CoinGecko API limitation
    metadata: "daily"
    categories: "every_run"
    global: "every_run"
    tickers: "weekly"
```

### Comprehensive Data Sources

#### **Technical Analysis**
| Category | Indicators | Parameters |
|----------|------------|------------|
| **Trend** | EMA, SMA | 20, 50, 200 periods |
| **Momentum** | RSI, MACD | RSI(14), MACD(12,26,9) |
| **Volatility** | Bollinger Bands, ATR | BB(20,2), ATR(14) |
| **Trend Strength** | ADX | ADX(14) |
| **Volume** | OBV | OBV + 20-period EMA |

#### **Market Intelligence**
| Data Type | Source | Content |
|-----------|--------|---------|
| **News** | *Not Available* | CoinGecko Pro API does not provide reliable news endpoints |
| **Metadata** | Coin Details API | Project info, tokenomics, dev activity, social metrics |
| **Categories** | Categories API | Sector performance, rotation signals, momentum analysis |
| **Global** | Global Stats API | Market cap, dominance, volume trends, sentiment |
| **Tickers** | Exchange API | Liquidity analysis, CEX/DEX breakdown, trading venues |
| **Onchain** | Onchain API* | DEX data, pool flows (*when available) |

#### **Timeframes**
- **1h**: Hourly data (30 days) for intraday analysis
- **1d**: Daily data (400 days) for swing/position analysis
- **Real-time**: Market intelligence updated every run

## 📁 Optimized Output Structure

```
data/
├── runs/20250819_185950/          # Timestamped run data
│   ├── intraday/
│   │   └── all_coins_1h.json      # Aggregated hourly technical data
│   ├── swing/
│   │   └── all_coins_1d.json      # Aggregated daily technical data  
│   ├── market_context.json        # Unified market intelligence
│   ├── categories.json            # Sector rotation data
│   ├── global.json                # Global market trends
│   ├── metadata.json              # Project fundamentals
│   ├── crypto_technicals_intraday.db  # SQLite database
│   └── logs/
│       └── run_20250819_185950.log
└── snapshots/                     # 🆕 LLM-Optimized Snapshots
    ├── latest_snapshot.json       # Combined multi-horizon snapshot
    ├── snapshot_intraday_2025-08-19T22-25-21Z.json
    └── snapshot_swing_2025-08-19T22-24-53Z.json
```

### 🆕 Combined Snapshot System with Market Intelligence

The **combined snapshot** (`data/snapshots/latest_snapshot.json`) is designed for comprehensive LLM analysis:

```json
{
  "meta": {
    "last_updated": "2025-08-19T22:50:32Z",
    "horizons_present": ["intraday", "swing"],
    "coins_tracked": ["ethereum", "bitcoin", "solana", "chainlink", "ripple", "tron", "sui"]
  },
  "intraday": {
    "meta": { "granularity": "1h", "run_timestamp": "..." },
    "market_overview": {
      "total_market_cap_usd": 3899134713516.64,
      "btc_dominance_pct": 57.95,
      "eth_dominance_pct": 12.84,
      "total_volume_24h_usd": 168189064707.82,
      "market_cap_change_24h_pct": -1.26,
      "sentiment": "risk_off"
    },
    "coins": { 
      "ethereum": { 
        "price": 4150.54,
        "market_cap_usd": 500029793189,
        "circulating_supply": 120707692.09,
        "volume_24h_usd": 41980540031,
        "market_cap_rank": 2,
        "volume_mcap_ratio": 0.084,
        "supply_circulation_pct": 100.0,
        "rsi_14": 35.5, "rsi_state": "neutral",
        "macd_hist": -7.3, "macd_state": "neutral",
        "pct_change": { "1h": 0.32, "24h": -1.94, "7d": -9.48 }
      },
      "bitcoin": {
        "price": 113414.51,
        "market_cap_usd": 2258867654421,
        "max_supply": 21000000.0,
        "supply_inflation_remaining_pct": 5.2,
        "volume_mcap_ratio": 0.0209,
        "trend_strength": "strong"
      }
    }
  }
}
```

**Key Features**:
- **🌍 Global market context**: Total market cap, dominance, volume, sentiment
- **💰 Comprehensive coin metrics**: Market cap, supply dynamics, liquidity ratios
- **📊 Fresh market data**: Real-time supply/market metrics from CoinGecko markets API
- **🔄 Multi-horizon preservation**: Intraday and swing data coexist without conflicts
- **🤖 LLM-optimized**: Categorical signals + raw values + market fundamentals
- **⚡ Smart freshness**: Only updates when crossing meaningful time boundaries
- **📦 Compact**: ~35KB for 7 coins, 2 horizons with full market intelligence

**Key Improvements**:
- **70% fewer files**: Aggregated format reduces clutter
- **Enhanced cross-coin analysis**: Performance ranking and comparative metrics
- **Unified market intelligence**: Single `market_context.json` combines all market data
- **🆕 LLM-optimized snapshots**: Combined multi-horizon file for AI analysis
- **Optional individual files**: Set `individual_coin_files: true` to restore individual coin files

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_indicators.py

# Run with verbose output
pytest -v
```

## 🔧 API Reference

### Command Line Interface

```bash
python -m src.cli [OPTIONS]

Options:
  --coins TEXT        Comma-separated list of coins (e.g., "eth,btc,sol")
  --horizons TEXT     Comma-separated list of horizons (e.g., "intraday,swing")  
  --config PATH       Path to configuration file [default: config.yaml]
  --output-dir TEXT   Override output directory
  --verbose, -v       Enable verbose logging
  --help             Show this message and exit
```

### Programmatic Usage

```python
from src.pipeline import Pipeline
from src.config_loader import Config
from src.utils.logging_utils import setup_logger

# Initialize components
config = Config('config.yaml')
logger = setup_logger()
pipeline = Pipeline(config, 'output/', logger)

# Run analysis
pipeline.run(['bitcoin', 'ethereum'], 'intraday')
```

## 🏗️ Architecture

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

**Key Design Principles:**
- **Stateless**: Each run is atomic with no persistent state
- **Modular**: Easy to swap data sources or add new indicators
- **Configurable**: Flexible configuration for different use cases
- **Fast**: Optimized for batch processing of multiple assets

## 🔍 Performance

**Benchmark Results** (CoinGecko Pro API):
- **7 coins, 2 horizons + market intelligence**: **~40 seconds**
- **22+ API calls** (14 OHLCV + 8+ market data): **No rate limiting**
- **7,805 total data points**: 5,005 hourly + 2,800 daily candles
- **Rich market data**: Market cap, supply metrics, liquidity ratios for all coins
- **Streamlined output**: 4-6 files instead of 20+ files per run
- **Complete market context**: Technical + fundamental + supply + macro data

## 🚧 Known Limitations

1. **CoinGecko Pro Required**: Free tier has severe rate limits (~5 calls before blocking)
2. **No News Data**: CoinGecko Pro API does not provide reliable news endpoints - consider integrating NewsAPI or Alpha Vantage
3. **Onchain Data**: Advanced DEX data may require additional API endpoints
4. **Data Volume**: Full runs generate significant data (~50MB+ for 6 coins with all intelligence)

## 🔮 Future Extensions

- **Real-time Streaming**: WebSocket integration for live market data
- **Advanced AI Integration**: Built-in LLM analysis and trade signal generation
- **DeFi Protocol Data**: TVL, yield farming, liquidity pool analytics
- **Social Sentiment**: Twitter, Reddit, Discord sentiment analysis
- **Portfolio Optimization**: Risk metrics, correlation analysis, position sizing
- **Automated Trading**: Signal execution via exchange APIs

## 📝 Changelog

### v0.3.1 (2025-08-19) - **MARKET & SUPPLY METRICS INTEGRATION**
- **🌍 Global Market Intelligence**: Real-time total market cap, BTC/ETH dominance, volume trends
- **💰 Comprehensive Coin Metrics**: Market cap, circulating/total/max supply, fully diluted valuation
- **📊 Fresh Market Data**: Direct CoinGecko markets API integration for accurate supply metrics
- **⚡ Supply Analytics**: Circulation percentages, inflation remaining, volume/market cap ratios
- **🎯 Expanded Coverage**: Added Tron and Sui to default coin tracking (7 total coins)
- **🔄 Enhanced Snapshots**: Combined multi-horizon files now include full market context
- **📈 LLM-Optimized**: Complete fundamental analysis data alongside technical indicators
- Real-time market data fetching on every snapshot export

### v0.2.1 (2025-08-19) - **PIPELINE OPTIMIZATION**
- **🎯 Streamlined Output Structure**
- **Aggregated technical files**: `all_coins_1h.json`, `all_coins_1d.json` with cross-coin analysis
- **Unified market intelligence**: Single `market_context.json` combining all market data
- **Individual coin files disabled by default** (configurable via `individual_coin_files`)
- **News collection disabled**: CoinGecko API limitation resolved by removing unreliable endpoint
- **70% reduction in output files** while preserving 100% data integrity
- Enhanced cross-coin performance ranking and volatility comparison
- Updated documentation to reflect current capabilities and limitations

### v0.2.0 (2025-08-19) - **MAJOR EXPANSION**  
- **🎯 Comprehensive Market Intelligence Pipeline**
- Added complete project metadata (fundamentals, dev activity, community)
- Added sector rotation analysis with momentum signals
- Added global market trends and dominance analysis
- Added exchange liquidity analysis (CEX/DEX breakdown)
- **CoinGecko Pro API integration** (zero rate limiting)
- **LLM-optimized data exports** for AI analysis
- Enhanced configuration with granular data collection control

### v0.1.0 (2023-12-01)
- Initial technical analysis engine
- Core technical indicators (EMA, SMA, RSI, MACD, Bollinger, ATR, ADX, OBV)
- Multi-format export (JSON, CSV, SQLite, PNG)
- Professional charting capabilities

## 👥 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and add tests
4. Run tests: `pytest`
5. Commit changes: `git commit -am 'Add my feature'`
6. Push branch: `git push origin feature/my-feature`
7. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙋‍♂️ Support

For questions, issues, or feature requests:
- Create an issue on GitHub
- Check existing documentation
- Review test files for usage examples

---

**Author**: Rahul Bijlani  
**Last Updated**: December 2023

*Built with ❤️ for the crypto community*