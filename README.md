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
- **⚡ Real-Time Pricing**: Live spot prices with <30s latency, automatic fallback to candle data

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

```text
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

### Real-Time Price Enhancement

**Live Spot Pricing**: Prices are now sourced from CoinGecko's real-time markets endpoint with transparent fallback:

```json
{
  "ethereum": {
    "price": 4945.81,
    "price_source": "spot",
    "price_timestamp": "2025-08-24T19:21:32.546844Z",
    "latest_data": {
      "close": 4768.69  // 1-hour candle close (fallback)
    }
  }
}
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

```text
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
├── snapshots/                     # 🆕 LLM-Optimized Snapshots
│   ├── latest_snapshot.json       # Combined multi-horizon snapshot
│   ├── snapshot_intraday_2025-08-19T22-25-21Z.json
│   └── snapshot_swing_2025-08-19T22-24-53Z.json
└── chat/                          # 🗂️ Persistent Chat History
    └── chat-YYYY-MM.jsonl         # one file per month (append-only)
```

### 🆕 Combined Snapshot System with Real-Time Intelligence

The **combined snapshot** (`data/snapshots/latest_snapshot.json`) provides comprehensive LLM analysis with live pricing:

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
        "price": 4945.81,
        "price_source": "spot",
        "price_timestamp": "2025-08-24T19:21:32.546844Z",
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
- **📊 Real-time pricing**: Live spot prices with <30s latency + transparent fallback to candle data
- **🔄 Multi-horizon preservation**: Intraday and swing data coexist without conflicts
- **🤖 LLM-optimized**: Categorical signals + raw values + market fundamentals
- **⚡ Smart freshness**: Only updates when crossing meaningful time boundaries
- **📦 Compact**: ~35KB for 7 coins, 2 horizons with full market intelligence

**Key Improvements**:

- **🗂️ Persistent Chat History**: NDJSON logs, 200k-token multi-month context, survives server & browser restarts
- **70% fewer files**: Aggregated format reduces clutter
- **Enhanced cross-coin analysis**: Performance ranking and comparative metrics
- **Real-time price accuracy**: Eliminated 0-59 minute price lag with live spot pricing
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

```text
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

- **7 coins, 2 horizons + market intelligence**: **≈45 seconds**
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

## Front-End (CryptoCortex / Trader-Copilot UI)

**CryptoCortex** is a sophisticated dual-channel memory trading assistant that bridges the CryptoTechnicals data engine with an AI-powered chat interface. The system combines continuous market data generation with intelligent LLM analysis, creating a real-time trading intelligence platform.

### Key Features

- **🧠 Dual-Channel Memory Architecture**: Lightweight chat history + heavy market data via tools
- **🤖 Direct OpenAI API Integration**: Native support for o3, gpt-5, and latest models
- **🔬 Deep Research Models**: o3-deep-research, o4-mini-deep-research with real-time progress streaming
- **💬 AI Trading Assistant**: Conversational market analysis with real-time tool calling
- **📊 Real-time Market Data**: Live snapshots with intelligent data sectioning
- **📝 Persistent Investment Thesis**: Strategy tracking across sessions
- **🔄 Auto/Manual Polling Control**: Configurable UI refresh modes
- **🎯 Intelligent Data Retrieval**: market/coin/full data access patterns
- **🔐 Basic Authentication**: Secure single-user operation
- **⚡ Streaming Responses**: Real-time AI responses with tool execution visibility
- **📖 Rich Content Formatting**: Markdown rendering with clickable links and proper spacing
- **🗂️ Persistent Chat History**: NDJSON logs, 200k-token multi-month context, survives server & browser restarts

### Quick Start

#### Prerequisites

1. **Python CLI Backend Setup**: Set up the CryptoTechnicals CLI backend:

   ```bash
   # Navigate to root directory
   cd ..
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create .env file with API keys
   cp .env.example .env
   # Edit .env and add your COINGECKO_API_KEY
   ```

2. **Environment Variables**: Create `.env.local` file in trader-copilot directory:

   ```bash
   BASIC_AUTH_TOKEN=dev-secret
   PYTHON_CMD=python3
   OPENAI_API_KEY=your_openai_api_key_here
   COINGECKO_API_KEY=your_coingecko_api_key_here
   ```

#### Installation & Setup

1. **Install Dependencies**:

   ```bash
   cd trader-copilot
   npm install
   ```

2. **Run Development Server**:

   ```bash
   npm run dev
   ```

3. **Open Browser**: Navigate to [http://localhost:3000](http://localhost:3000)

4. **Authentication**: The app uses basic auth with the `BASIC_AUTH_TOKEN` from `.env.local`

### Architecture Overview

#### Dual-Channel Memory System

**Channel 1 (Chat)**: Conversation history stored in LLM prompts (lightweight)
**Channel 2 (Snapshots)**: Heavy market data accessed via tool calls (cost-optimized)

```text
Manual Refresh → Python CLI → Snapshot Files → KV Cache → Next.js API → OpenAI
                     ↑                             ↑
                Data Generation            Tool Access via Chat
```

#### Component Structure

- **Chat Interface**: Streaming AI conversations with tool calling
- **Thesis Panel**: Persistent investment strategy management  
- **Price Ticker**: Real-time market overview display
- **Model Picker**: OpenAI model selection (o3, gpt-5, gpt-4o, gpt-4o-mini)
- **Snapshot Viewer**: Direct access to latest market intelligence

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat-direct` | POST | Direct OpenAI API streaming with tool calling |
| `/api/snapshot` | GET | Market data access (dual-channel) |
| `/api/thesis` | GET/POST | Investment strategy management |
| `/api/refresh` | POST | Manual market data refresh |
| `/api/control` | GET/POST | Auto-polling control |
| `/api/status` | GET | Data freshness detection |
| `/api/chat-history` | GET/POST/DELETE | Multi-month chat history management |

### Configuration

#### Market Data Sections

- **`market`** (default): Market overview only - minimal tokens
- **`coin`**: Specific coin data - focused analysis  
- **`full`**: Complete snapshot - comprehensive analysis

#### OpenAI Models

- **o3**: Latest reasoning model for advanced analysis
- **gpt-5**: Next-generation model with enhanced capabilities
- **gpt-4o**: Maximum capability for complex analysis
- **gpt-4o-mini**: Cost-optimized for routine queries
- **o3-deep-research**: Multi-step research with web search (3-5 min response time)
- **o4-mini-deep-research**: Cost-optimized deep research model

### Data Pipeline Integration

CryptoCortex integrates with the CryptoTechnicals engine:

1. **Manual Refresh** triggers Python CLI to generate fresh snapshots
2. **KV Store** caches data with hash-based change detection  
3. **API Layer** provides intelligent data sectioning
4. **AI Tools** access market data on-demand via chat tools
5. **UI Components** display market overview and enable refresh control

**Note**: The system uses on-demand data generation triggered by manual refresh button or chat queries, rather than continuous background polling.

### Persistent Chat History

CryptoCortex features a sophisticated **multi-month chat history system** that preserves conversation context across sessions:

#### Dynamic Context Loading

- **Context Budget**: 200,000 tokens (configurable via `CONTEXT_BUDGET_TOKENS`)
- **System Reserve**: 4,000 tokens reserved for system prompts and tools
- **Multi-Month Spanning**: Automatically loads conversation history across multiple months
- **Smart Clipping**: Walks files from newest to oldest, loading messages until token budget is reached

#### Storage Architecture

- **NDJSON Format**: One file per month (`chat-2025-08.jsonl`) for efficient append-only writes
- **Reverse Traversal**: Reads files bottom-to-top (newest messages first) for optimal performance
- **Automatic Rotation**: New month = new file, old conversations automatically archived
- **Human Readable**: Files can be opened and read with any text editor

#### Chat History API

- `GET /api/chat-history?mode=context` - Multi-month context-aware loading (default)
- `GET /api/chat-history?mode=recent&limitTokens=50000` - Legacy single-month loading
- `GET /api/chat-history?mode=stats` - Chat history statistics
- `POST /api/chat-history` - Append new message
- `DELETE /api/chat-history` - Clear current month (testing only)

#### Benefits

- **Seamless Continuity**: Chat survives browser refreshes, server restarts, model switches
- **Context Preservation**: AI can reference conversations from weeks or months ago
- **Token Efficient**: Only loads what fits in the model's context window
- **Performance Optimized**: O(1) append operations, efficient tail reads
- **Future Proof**: Easily adjustable when model context windows increase

### Security Features

- **Basic Authentication**: Environment-based user credentials
- **API Protection**: All endpoints secured with auth middleware
- **Local Deployment**: Designed for secure single-user operation
- **No External Dependencies**: Self-contained authentication system

### Development Status

#### ✅ Completed Features

- Complete Next.js 14 frontend with TypeScript
- Dual-channel memory architecture with KV store
- **Direct OpenAI API integration** (bypassing AI SDK compatibility issues)
- Auto/manual polling control with UI toggle
- Basic authentication system
- File-based NextJS ↔ Python CLI coordination
- Streaming responses with real-time tool execution
- Thesis management system
- **v0.4.1**: Dynamic Multi-Month Chat History with 200k token budget

#### ✅ Fully Functional (Validated)

- **AI Function Calling**: Native tool calling with o3, gpt-5, and latest models
- **Market Data Access**: Live crypto data via smart tool selection (market/coin/full)
- **Thesis Management**: AI can update investment strategy via `update_thesis` tool  
- **Real-time Analysis**: Complete dual-channel architecture with token efficiency
- **Deep Research Models**: o3-deep-research, o4-mini-deep-research with progress streaming
- **Rich Content Display**: Clickable links, markdown formatting, proper spacing
- **Progress Visibility**: Real-time workflow tracking for long-running tasks
- **Persistent Chat History**: Multi-month conversation context with 200k token budget

#### 🔮 Next Priorities

1. Advanced trading tools (position sizing, risk management)
2. Chart integration for visual analysis
3. Portfolio tracking and performance analytics
4. Multi-timeframe analysis tools

### Usage Examples

#### Market Analysis

- "Analyze current ETH technicals and provide entry points"
- "Compare BTC and SOL momentum indicators"
- "What's the overall market sentiment based on dominance?"

#### Strategy Management

- "Update my thesis: focusing on Layer 1 scaling solutions"
- "Review my current thesis against market conditions"
- "Adjust risk parameters for current volatility regime"

#### Data Exploration

- "Show me the latest snapshot for just Bitcoin"
- "Get full market overview with all coins"
- "Refresh market data and analyze changes"

#### Deep Research Queries

- "Research the latest developments in Layer 2 scaling solutions"
- "Analyze Peter Thiel's cryptocurrency investment strategy with sources"
- "Deep dive into DeFi protocol revenue models with market data"

**Note**: Deep research models (o3-deep-research, o4-mini-deep-research) provide comprehensive analysis with web search and take 3-5 minutes. Progress is shown in real-time.

---

**Built with**: Next.js 14, TypeScript, Tailwind CSS, Direct OpenAI API, shadcn/ui  
**Integration**: CryptoTechnicals Python CLI backend  
**Version**: 0.4.1 - Dynamic Multi-Month Chat History  

## 🔮 Future Extensions

- **Real-time Streaming**: WebSocket integration for live market data
- **Advanced AI Integration**: Built-in LLM analysis and trade signal generation
- **DeFi Protocol Data**: TVL, yield farming, liquidity pool analytics
- **Social Sentiment**: Twitter, Reddit, Discord sentiment analysis
- **Portfolio Optimization**: Risk metrics, correlation analysis, position sizing
- **Automated Trading**: Signal execution via exchange APIs

## 📝 Changelog

### v0.4.1 (2025-08-25) - **Dynamic Multi-Month Chat History**

- **🗂️ Persistent Chat History**: NDJSON logs, 200k-token multi-month context, survives server & browser restarts
- **📊 Dynamic Context Loading**: Reverse file traversal algorithm with token budget management
- **🔄 Cross-Session Continuity**: Chat conversations preserved across browser refreshes and model switches
- **⚡ Performance Optimized**: O(1) append operations, efficient tail reads
- **📈 Token Efficient**: Only loads what fits in model's context window (200k budget, 4k system reserve)

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
**Documentation updated**: **2025-08-25**  
**Last Updated**: Aug 25 2025
