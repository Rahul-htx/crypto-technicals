# CryptoTechnicals — Technical Analysis Data Engine

A lightweight Python command-line tool that pulls historical price/volume data from the CoinGecko API, automatically computes a standardized bundle of technical indicators, and exports both machine-readable summaries (JSON/CSV/SQLite) and ready-to-share charts (PNG) for a watchlist of crypto assets.

## 🎯 Purpose & Scope

**CryptoTechnicals** is designed to:
- Fetch historical cryptocurrency data from CoinGecko API
- Calculate comprehensive technical indicators automatically
- Export data in multiple formats for analysis and AI consumption
- Generate publication-ready charts without manual intervention
- Provide consistent, structured data for algorithmic trading research

Perfect for traders, researchers, and developers who need clean, analyzed crypto data without the hassle of manual data gathering and indicator calculation.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd crypto_technicals

# Install dependencies
pip install -r requirements.txt

# Or install with development dependencies
pip install -e ".[dev]"
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

## 📊 Sample Outputs

### JSON Export
```json
{
  "metadata": {
    "coin": "bitcoin",
    "horizon": "intraday", 
    "granularity": "1h",
    "lookback_days": 30,
    "total_candles": 720
  },
  "latest_values": {
    "close": 43250.67,
    "rsi_14": 58.23,
    "macd": 125.45,
    "bb_percent_b": 0.67
  },
  "summary": {
    "price_change_pct": 2.34,
    "volume_mean": 1250000000
  }
}
```

### Chart Output
- **3-panel PNG charts** showing price + EMAs, RSI, and MACD
- **Multi-coin comparison charts** for relative analysis
- **High-resolution outputs** suitable for reports and presentations

## ⚙️ Configuration

Edit `config.yaml` to customize your analysis:

```yaml
coins: [eth, btc, sol, link, ada]
horizons:
  intraday:
    lookback_days: 30
    granularity: 1h
  swing:
    lookback_days: 400
    granularity: 1d
indicators: [ema, sma, rsi, macd, bollinger, atr, adx, obv]
export:
  json: true
  csv: false
  sqlite: true
  charts: true
output_dir: data/runs
```

### Supported Indicators

| Category | Indicators | Parameters |
|----------|------------|------------|
| **Trend** | EMA, SMA | 20, 50, 200 periods |
| **Momentum** | RSI, MACD | RSI(14), MACD(12,26,9) |
| **Volatility** | Bollinger Bands, ATR | BB(20,2), ATR(14) |
| **Trend Strength** | ADX | ADX(14) |
| **Volume** | OBV | OBV + 20-period EMA |

### Supported Timeframes

- **1h**: Hourly data (available for last 30 days)
- **4h**: 4-hour data (available for last 30 days)  
- **1d**: Daily data (available for 365+ days)

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

**Benchmark Results** (MacBook Pro M1):
- 20 coins, 90-day hourly data: **< 60 seconds**
- 5 coins, 400-day daily data: **< 30 seconds**  
- Full indicator suite calculation: **< 5 seconds per coin**

## 🚧 Known Limitations

1. **CoinGecko Rate Limits**: 1.2 second delays between requests
2. **Granularity Constraints**: Hourly data limited to 30 days via API
3. **No Real-time Data**: Historical data only, no streaming capabilities
4. **Chart Dependencies**: Requires matplotlib and seaborn for visualization

## 🔮 Future Extensions

- **Exchange Integration**: Direct Binance/Coinbase Pro API support
- **On-chain Metrics**: Glassnode integration for network indicators  
- **Real-time Streaming**: WebSocket connections for live data
- **Advanced Analytics**: ML-based pattern recognition
- **Portfolio Tracking**: Multi-asset correlation analysis

## 📝 Changelog

### v0.1.0 (2023-12-01)
- Initial release
- Core technical indicators implemented
- Multi-format export support
- Comprehensive charting capabilities
- Full test coverage

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