# CryptoTechnicals — Comprehensive Crypto Intelligence Engine

A powerful Python command-line tool that provides **complete cryptocurrency market intelligence** by combining technical analysis, fundamental data, market sentiment, sector rotation analysis, and global market trends. Designed to feed AI/LLM systems with the richest possible context for cryptocurrency analysis and trading decisions.

## 🎯 Purpose & Scope

**CryptoTechnicals** is designed to:
- **Technical Analysis**: Historical OHLCV data + 8 comprehensive technical indicators
- **Fundamental Analysis**: Project metadata, tokenomics, development activity, community metrics
- **Market Intelligence**: Global market trends, sector rotation, dominance analysis
- **Sentiment Analysis**: News headlines with sentiment extraction and coin mentions
- **Liquidity Analysis**: Exchange listings, trading venues, CEX/DEX breakdown
- **LLM-Ready Exports**: Structured JSON/CSV/SQLite + visual charts for AI consumption

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

## 📊 Comprehensive Data Outputs

### Complete Market Intelligence Package
Every run generates **6 categories of market data** for maximum LLM context:

```
data/runs/20250819_182216/
├── Technical Analysis:
│   ├── intraday/ & swing/ (OHLCV + 8 indicators)
│   ├── crypto_technicals_*.db (SQLite databases)
│   └── charts/ (technical analysis PNGs)
│
└── Market Intelligence:
    ├── news.json (sentiment catalysts)
    ├── metadata.json (project fundamentals)
    ├── categories.json (sector rotation)
    ├── global.json (macro trends)
    └── tickers.json (liquidity analysis)
```

### Sample Outputs

**Technical Data** (per coin):
```json
{
  "latest_values": {
    "close": 43250.67, "rsi_14": 58.23, "macd": 125.45,
    "bb_percent_b": 0.67, "adx_14": 32.1, "obv": 1.2e9
  }
}
```

**Global Market Intelligence**:
```json
{
  "market_overview": {
    "total_market_cap_usd": 3882142856426.52,
    "bitcoin_dominance_percentage": 57.94,
    "ethereum_dominance_percentage": 12.80
  },
  "dominance_analysis": {
    "dominance_signals": [{
      "type": "btc_dominance_high",
      "description": "Bitcoin dominance at 57.9% suggests market seeking safety",
      "implication": "bearish_for_alts"
    }]
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
coins: [ethereum, bitcoin, solana, chainlink, ripple, cardano]
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
  charts: true

# Enhanced Market Intelligence Collection
market_data:
  collect_news: true              # News headlines for sentiment
  collect_metadata: true          # Project fundamentals & dev activity
  collect_categories: true        # Sector rotation analysis
  collect_global: true           # Market cap, dominance, macro trends
  collect_tickers: true          # Exchange listings & liquidity
  collect_onchain: false         # DEX data (advanced, when available)
  
  news_limit: 20                 # Headlines per run
  
  update_frequencies:            # Control data collection frequency
    news: "every_run"
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
| **News** | CoinGecko News API | Headlines, sentiment extraction, coin mentions |
| **Metadata** | Coin Details API | Project info, tokenomics, dev activity, social metrics |
| **Categories** | Categories API | Sector performance, rotation signals, momentum analysis |
| **Global** | Global Stats API | Market cap, dominance, volume trends, sentiment |
| **Tickers** | Exchange API | Liquidity analysis, CEX/DEX breakdown, trading venues |
| **Onchain** | Onchain API* | DEX data, pool flows (*when available) |

#### **Timeframes**
- **1h**: Hourly data (30 days) for intraday analysis
- **1d**: Daily data (400 days) for swing/position analysis
- **Real-time**: Market intelligence updated every run

## 📁 Output Structure

```
data/runs/20231201_143022/
├── intraday/
│   ├── charts/
│   │   ├── bitcoin_1h_chart.png
│   │   ├── ethereum_1h_chart.png
│   │   └── comparison_intraday.png
│   ├── bitcoin_1h.json
│   ├── ethereum_1h.json
│   └── summary_intraday.json
├── swing/
│   ├── charts/
│   │   ├── bitcoin_1d_chart.png
│   │   └── comparison_swing.png
│   ├── bitcoin_1d.json
│   └── crypto_technicals_swing.db
└── logs/
    └── run_20231201_143022.log
```

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
- **6 coins, 2 horizons + full market intelligence**: **~35 seconds**
- **24 API calls** (12 OHLCV + 12 market data): **No rate limiting**
- **6,690 total data points**: 4,290 hourly + 2,400 daily candles
- **Comprehensive market context**: Technical + fundamental + sentiment + macro data

## 🚧 Known Limitations

1. **CoinGecko Pro Required**: Free tier has severe rate limits (~5 calls before blocking)
2. **News API Limitations**: News endpoint may have limited availability on some Pro plans
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

### v0.2.0 (2025-08-19) - **MAJOR EXPANSION**
- **🎯 Comprehensive Market Intelligence Pipeline**
- Added news sentiment analysis with coin mention detection
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