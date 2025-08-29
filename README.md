Absolutely. Here’s a full reorganization of your README, applying the structure and principles above. This version preserves all substantive content, but dramatically improves scanability, separation of concerns, and initial approachability. All sections are renamed for action and clarity. I have used collapsible <details> blocks where verbosity is high, and you can adapt these further for your preferred renderer.

⸻


# CryptoTechnicals — Comprehensive Crypto Intelligence Engine

A powerful Python command-line tool that provides **complete cryptocurrency market intelligence** by combining technical analysis, fundamental data, market sentiment, sector rotation analysis, and global market trends.  
**Perfect for AI-powered trading systems, researchers, and analysts who need the most comprehensive crypto market context—automated and LLM-ready.**

---

## 🚀 TL;DR

- Instantly generate technical, fundamental, and market intelligence snapshots for any crypto asset.
- Aggregated, LLM-optimized outputs (JSON, SQLite) with live spot prices, sector rotation, liquidity, and more.
- Designed for seamless AI integration, advanced human workflows, and pro-grade research.

---

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [Key Features](#key-features)
3. [Usage Examples](#usage-examples)
4. [Understanding the Data Outputs](#understanding-the-data-outputs)
5. [Configuration](#configuration)
6. [How to Read/Interpret the Data](#how-to-readinterpret-the-data)
7. [Front-End UI (CryptoCortex)](#front-end-ui-cryptocortex)
8. [Developer Guide](#developer-guide)
9. [Performance & Benchmarks](#performance--benchmarks)
10. [Known Limitations](#known-limitations)
11. [Changelog](#changelog)
12. [Contributing](#contributing)
13. [License & Author](#license--author)
14. [Support](#support)

---

## 🏁 Quick Start

**Installation**

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

Basic Usage

python -m src.cli                           # Default config, all outputs
python -m src.cli --coins eth,btc,sol       # Specify coins
python -m src.cli --horizons intraday,swing # Specify timeframes
python -m src.cli --config my_config.yaml   # Custom config
python -m src.cli --verbose                 # Verbose logging
python -m src.cli --output-dir /my/output   # Custom output directory


⸻

🗝️ Key Features
	•	Technical Analysis: OHLCV + 8 indicators
	•	Fundamental Analysis: Tokenomics, dev activity, social metrics
	•	Market Intelligence: Macro trends, sector rotation, dominance, liquidity
	•	Real-Time Pricing: Live spot prices (<30s latency)
	•	LLM-Ready Exports: Structured JSON/CSV/SQLite for AI, visual charts
	•	Combined Snapshots: Multi-timeframe, freshness-aware files
	•	Persistent Chat History: NDJSON, 200k-token multi-month memory (for UI)

⸻

💡 Usage Examples
	•	“Analyze current ETH technicals and provide entry points”
	•	“Compare BTC and SOL momentum indicators”
	•	“What’s the overall market sentiment based on dominance?”
	•	“Show me the latest snapshot for just Bitcoin”
	•	“Update my thesis: focusing on Layer 1 scaling solutions”
	•	“Refresh market data and analyze changes”

⸻

🗃️ Understanding the Data Outputs

Every run generates aggregated files for efficient LLM and human use.
Sample Output Structure:

data/
├── runs/20250819_185950/              # Timestamped run data
│   ├── intraday/
│   │   └── all_coins_1h.json          # Hourly technical data
│   ├── swing/
│   │   └── all_coins_1d.json          # Daily technical data  
│   ├── market_context.json            # Unified market intelligence
│   ├── categories.json                # Sector rotation
│   ├── global.json                    # Macro trends
│   ├── metadata.json                  # Project fundamentals
│   ├── crypto_technicals_intraday.db  # SQLite database
│   └── logs/
│       └── run_*.log
├── snapshots/
│   ├── latest_snapshot.json           # Combined, all-horizon snapshot
└── chat/
    └── chat-YYYY-MM.jsonl             # Multi-month chat history

<details>
<summary>📈 <b>See Sample Output JSON</b></summary>


Technical Data Example (all_coins_1h.json):

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

</details>


<details>
<summary>🌍 <b>Unified Market Context</b> (`market_context.json`)</summary>


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

</details>



⸻

⚙️ Configuration

Edit config.yaml to customize coins, timeframes, and outputs.

<details>
<summary>📝 <b>Click for Example</b></summary>


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
  charts: false
  individual_coin_files: false

market_data:
  collect_news: false     # CoinGecko Pro API does not provide reliable news
  collect_metadata: true
  collect_categories: true
  collect_global: true
  collect_tickers: true
  collect_onchain: false

  update_frequencies:
    metadata: "daily"
    categories: "every_run"
    global: "every_run"
    tickers: "weekly"

</details>



⸻

🧐 How to Read/Interpret the Data
	•	Technical indicators: Standard values (e.g. RSI, MACD, EMA, etc.) for each coin, each period.
	•	Cross-coin analysis: Ranking by performance, volatility comparison, sector rotation.
	•	Market intelligence: Sentiment regime, macro trends, dominance metrics.
	•	Real-time spot prices: Always prioritized; transparent fallback to recent candles.
	•	Aggregated files: Designed for AI/LMM consumption, not just human reading.

⸻

🖥️ Front-End UI (CryptoCortex)

CryptoCortex is a Next.js/TypeScript web UI for CryptoTechnicals, featuring:
	•	Dual-channel memory: LLM chat + heavy data snapshots.
	•	Streaming AI analysis: Direct OpenAI API integration.
	•	Persistent chat history: Survives browser/server restarts.
	•	Security: Basic Auth, local-first deployment.

<details>
<summary>🌐 <b>Setup Instructions</b></summary>


# Python CLI Backend
cd ..
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set API keys in .env

# Next.js Frontend
cd trader-copilot
npm install
npm run dev
# Open http://localhost:3000 (auth required)

</details>



⸻

🛠️ Developer Guide

Programmatic Usage

from src.pipeline import Pipeline
from src.config_loader import Config
from src.utils.logging_utils import setup_logger

config = Config('config.yaml')
logger = setup_logger()
pipeline = Pipeline(config, 'output/', logger)
pipeline.run(['bitcoin', 'ethereum'], 'intraday')

Code Structure

┌──────────┐      ┌──────────────┐      ┌──────────────┐
│  config   │───►│  fetch layer  │───►│  indicator    │
└──────────┘      │  (CoinGecko) │      │  calculator  │
                  └──────────────┘      └──────────────┘
                          │                     │
                          ▼                     ▼
                 ┌────────────────┐    ┌────────────────┐
                 │ JSON / SQLite  │    │ chart exporter │
                 └────────────────┘    └────────────────┘

Testing

pytest             # Run all tests
pytest --cov=src   # With coverage
pytest -v          # Verbose


⸻

⚡ Performance & Benchmarks
	•	7 coins, 2 horizons + market intelligence: ~45 seconds/run
	•	22+ API calls: No rate limiting (Pro tier)
	•	7,805 total data points: 5,005 hourly + 2,800 daily
	•	Aggregated output: 4–6 files instead of 20+
	•	Rich context: Technical, fundamental, supply, macro data

⸻

🚧 Known Limitations
	1.	CoinGecko Pro Required: Free tier is severely rate limited.
	2.	No News Data: CoinGecko Pro API has no reliable news endpoint.
	3.	Onchain Data: DEX info limited; needs additional APIs.
	4.	Data Volume: Large runs (~50MB+ for 6 coins).

⸻

📝 Changelog

<details>
<summary>Click to expand full changelog</summary>


v0.4.1 (2025-08-25) - Dynamic Multi-Month Chat History
	•	Persistent chat (NDJSON), 200k-token context, cross-session
	•	Dynamic context loading, performance-optimized

v0.3.1 (2025-08-19) - Market & Supply Metrics Integration
	•	Real-time macro intelligence
	•	Enhanced supply/circulation stats
	•	Combined snapshot exports

v0.2.1 (2025-08-19) - Pipeline Optimization
	•	Aggregated outputs, single market context file
	•	File count -70%, same data
	•	Cross-coin ranking, volatility, perf

v0.2.0 (2025-08-19) - Major Expansion
	•	Full project metadata
	•	Sector rotation, global trends, liquidity, LLM optimization

v0.1.0 (2023-12-01)
	•	Initial release

</details>



⸻

🤝 Contributing
	1.	Fork the repository
	2.	Create a feature branch: git checkout -b feature/my-feature
	3.	Make changes and add tests
	4.	Run tests: pytest
	5.	Commit: git commit -am 'Add my feature'
	6.	Push: git push origin feature/my-feature
	7.	Submit pull request

⸻

📄 License & Author

MIT License – see LICENSE file for details.

Author: Rahul Bijlani
Documentation last updated: 2025-08-25

⸻

🙋‍♂️ Support
	•	Create a GitHub issue
	•	Review documentation and test files for examples

⸻


---

### Notes

- You may wish to use [doctoc](https://github.com/thlorenz/doctoc) or similar tools to auto-generate/upkeep the Table of Contents.
- I recommend using `<details>` for especially long config and output examples in the live file to keep the top-level scanability tight.
- If you want this version as an updated file, let me know, and I’ll produce the `oboe` tool call for an instant patch.