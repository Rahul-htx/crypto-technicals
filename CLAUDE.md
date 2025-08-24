# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CryptoTechnicals is a comprehensive cryptocurrency market intelligence engine that combines technical analysis, fundamental data, market sentiment, and sector rotation analysis. It's designed to feed AI/LLM systems with rich context for cryptocurrency analysis and trading decisions.

## Development Commands

### Running the Application
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
- Create `.env` file with `COINGECKO_API_KEY=your_api_key_here`
- Install dependencies: `pip install -r requirements.txt`
- Python 3.9+ required

## Architecture Overview

### Core Pipeline Architecture
The system follows a modular pipeline architecture with these key components:

1. **Config Layer** (`src/config_loader.py`) - Handles YAML configuration parsing
2. **Fetch Layer** (`src/fetch/coingecko.py`) - CoinGecko Pro API integration for market data
3. **Indicators Layer** (`src/indicators/`) - Technical analysis calculations (RSI, MACD, EMA, etc.)
4. **Exporter Layer** (`src/exporter/`) - Multiple format outputs (JSON, SQLite, charts)
5. **Pipeline Controller** (`src/pipeline.py`) - Orchestrates the entire data flow

### Key Data Flow
1. CLI parses arguments and loads configuration
2. Pipeline initializes all components (fetchers, exporters)
3. CoinGecko fetcher retrieves OHLCV and market intelligence data
4. Technical indicators are calculated on raw price data
5. Multiple exporters generate outputs in different formats
6. Snapshot exporter creates LLM-optimized combined files

### Market Intelligence System
The system collects comprehensive market data beyond just price:
- **Technical Data**: OHLCV + 8 technical indicators across multiple timeframes
- **Fundamental Data**: Project metadata, tokenomics, development activity
- **Market Context**: Global market cap, dominance analysis, sector rotation
- **Liquidity Analysis**: Exchange listings, trading venues, volume analysis

### Output Structure
```
data/runs/TIMESTAMP/
├── intraday/all_coins_1h.json (aggregated hourly data)
├── swing/all_coins_1d.json (aggregated daily data)
├── market_context.json (unified market intelligence)
├── *.db (SQLite databases)
└── snapshots/ (LLM-optimized combined files)
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