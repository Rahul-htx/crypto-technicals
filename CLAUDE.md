# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Information - MUST REMEMBER

### OpenAI Models (Post-2024)
The following models are available and MUST be used exactly as specified:
- **o3** - Base reasoning model
- **o3-deep-research** - Optimized for multi-source research  
- **o4-mini-deep-research** - Faster, cheaper "mini" flavor
- **gpt-5** - Latest GPT model

**IMPORTANT**: These models do NOT support custom temperature settings. Only the default temperature (1.0) is allowed.

## Project Overview

CryptoTechnicals is a comprehensive cryptocurrency market intelligence engine that combines technical analysis, fundamental data, market sentiment, and sector rotation analysis. It's designed to feed AI/LLM systems with rich context for cryptocurrency analysis and trading decisions.

### CryptoCortex UI (trader-copilot/)
The project now includes **CryptoCortex**, a sophisticated AI-powered trading assistant with:
- **Persistent Multi-Month Chat History**: 200k token context across months with NDJSON storage
- **Direct OpenAI API Integration**: Native o3, gpt-5, and deep research model support  
- **Real-time Market Data Tools**: Live CoinGecko integration with smart tool calling
- **Investment Thesis Management**: Persistent strategy tracking with AI updates
- **Dynamic Context Loading**: Server-side context safety with token-aware clipping

## Development Commands

### Running the CryptoTechnicals CLI (Backend)
```bash
# Basic run with default configuration
python -m src.cli

# Run with specific coins and horizons
python -m src.cli --coins eth,btc,sol --horizons intraday,swing

# Run with custom configuration
python -m src.cli --config my_config.yaml

# Enable verbose logging
python -m src.cli --verbose

# Override output directory
python -m src.cli --output-dir /path/to/custom/output
```

### Running CryptoCortex UI (Frontend)
```bash
# Navigate to UI directory
cd trader-copilot

# Install dependencies (first time only)
npm install

# Set up environment variables (.env.local)
BASIC_AUTH_TOKEN=dev-secret
PYTHON_CMD=python3
OPENAI_API_KEY=your_openai_api_key
COINGECKO_API_KEY=your_coingecko_api_key

# Start development server
npm run dev

# Access at http://localhost:3000
```

### Testing
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

### Code Quality (Development Dependencies)
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Environment Setup

#### Backend (Python CLI)
- Create virtual environment: `python3 -m venv venv && source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Create `.env` file with `COINGECKO_API_KEY=your_api_key_here`
- Python 3.9+ required

#### Frontend (CryptoCortex UI)
- Node.js 18+ required
- Create `trader-copilot/.env.local` with required API keys (see Running CryptoCortex UI above)
- Install dependencies: `npm install`

## Architecture Overview

### CryptoCortex Full-Stack Architecture
The system consists of two main components working together:

#### Backend: CryptoTechnicals CLI Pipeline
1. **Config Layer** (`src/config_loader.py`) - Handles YAML configuration parsing
2. **Fetch Layer** (`src/fetch/coingecko.py`) - CoinGecko Pro API integration for market data
3. **Indicators Layer** (`src/indicators/`) - Technical analysis calculations (RSI, MACD, EMA, etc.)
4. **Exporter Layer** (`src/exporter/`) - Multiple format outputs (JSON, SQLite, charts)
5. **Pipeline Controller** (`src/pipeline.py`) - Orchestrates the entire data flow

#### Frontend: CryptoCortex UI (trader-copilot/)
1. **Chat System** (`src/components/ChatDirect.tsx`) - Direct OpenAI API streaming chat
2. **Multi-Month History** (`src/lib/chat-store.ts`) - NDJSON-based persistent context with 200k token budget
3. **Market Data Integration** (`src/lib/openai-direct.ts`) - Real-time CoinGecko tools for AI
4. **Thesis Management** (`src/components/ThesisPanel.tsx`) - Persistent investment strategy tracking
5. **Price Display** (`src/components/PriceTicker.tsx`) - Live market overview with manual refresh

### Key Data Flow

#### Backend Data Pipeline
1. CLI parses arguments and loads configuration
2. Pipeline initializes all components (fetchers, exporters)
3. CoinGecko fetcher retrieves OHLCV and market intelligence data
4. Technical indicators are calculated on raw price data
5. Multiple exporters generate outputs in different formats
6. Snapshot exporter creates LLM-optimized combined files

#### Frontend Chat Flow
1. User sends message → Saved to NDJSON history
2. UI loads 200k token context from multiple months
3. Server-side context safety prevents client manipulation
4. AI tools access real-time CoinGecko data on demand
5. Streaming response from OpenAI → Saved to history
6. Persistent thesis updates via AI tool calling

### Market Intelligence System
The system collects comprehensive market data beyond just price:
- **Technical Data**: OHLCV + 8 technical indicators across multiple timeframes
- **Fundamental Data**: Project metadata, tokenomics, development activity
- **Market Context**: Global market cap, dominance analysis, sector rotation
- **Liquidity Analysis**: Exchange listings, trading venues, volume analysis

### Output Structure

#### Backend Data Files
```
data/runs/TIMESTAMP/
├── intraday/all_coins_1h.json (aggregated hourly data)
├── swing/all_coins_1d.json (aggregated daily data)
├── market_context.json (unified market intelligence)
├── *.db (SQLite databases)
└── snapshots/ (LLM-optimized combined files)
```

#### Frontend Persistent Data
```
trader-copilot/data/
├── chat/
│   ├── chat-2025-08.jsonl (current month chat history)
│   ├── chat-2025-07.jsonl (previous months)
│   └── chat-2025-06.jsonl (automatically archived)
└── thesis.json (persistent investment strategy)
```

## Configuration System

### Main Config (`config.yaml`)
- **coins**: List of cryptocurrencies to track
- **horizons**: Time ranges (intraday: 1h/30d, swing: 1d/400d)
- **indicators**: Technical indicators to calculate
- **export**: Output format controls (JSON, SQLite, charts)
- **market_data**: Intelligence collection settings

### Environment Variables
- `COINGECKO_API_KEY`: Required for API access (Pro tier recommended)

## Important Implementation Details

### API Integration
- Uses CoinGecko Pro API (required for reasonable rate limits)
- Implements comprehensive market data collection beyond basic OHLCV
- News collection disabled due to CoinGecko API limitations

### Data Aggregation Strategy
- Generates aggregated files by default (`all_coins_*.json`) instead of individual files
- Provides cross-coin analysis and performance rankings
- Creates LLM-optimized snapshot files combining multiple timeframes

### Modular Exporter System
Each data type has its own exporter class:
- `JSONExporter`: Technical data in JSON format
- `SQLiteExporter`: Database exports for analysis
- `MarketContextExporter`: Unified market intelligence
- `SnapshotExporter`: Combined multi-horizon LLM-ready files

### Testing Infrastructure
- Comprehensive test suite covering indicators, fetching, and pipeline
- Uses pytest with coverage reporting
- Fixtures available for mock data testing