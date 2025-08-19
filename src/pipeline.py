import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
from pathlib import Path

from .fetch.coingecko import CoinGeckoFetcher
from .indicators import calculate_all_indicators
from .exporter.json_exporter import JSONExporter
from .exporter.csv_exporter import CSVExporter
from .exporter.sqlite_exporter import SQLiteExporter
from .exporter.chart_exporter import ChartExporter
from .exporter.news_exporter import NewsExporter
from .exporter.metadata_exporter import MetadataExporter
from .exporter.categories_exporter import CategoriesExporter
from .exporter.tickers_exporter import TickersExporter
from .exporter.global_exporter import GlobalExporter
from .config_loader import Config

class Pipeline:
    def __init__(self, config: Config, output_dir: str, logger: logging.Logger):
        self.config = config
        self.output_dir = Path(output_dir)
        self.logger = logger
        
        # Initialize components
        self.fetcher = CoinGeckoFetcher(logger)
        self.json_exporter = JSONExporter(self.output_dir)
        self.csv_exporter = CSVExporter(self.output_dir)
        self.sqlite_exporter = SQLiteExporter(self.output_dir)
        self.chart_exporter = ChartExporter(self.output_dir)
        
        # Initialize new exporters
        self.news_exporter = NewsExporter(self.output_dir)
        self.metadata_exporter = MetadataExporter(self.output_dir)
        self.categories_exporter = CategoriesExporter(self.output_dir)
        self.tickers_exporter = TickersExporter(self.output_dir)
        self.global_exporter = GlobalExporter(self.output_dir)
    
    def run(self, coins: List[str], horizon: str) -> None:
        """Run the complete pipeline for given coins and horizon."""
        horizon_config = self.config.get_horizon_config(horizon)
        
        if not horizon_config:
            raise ValueError(f"Horizon '{horizon}' not found in configuration")
        
        lookback_days = horizon_config['lookback_days']
        granularity = horizon_config['granularity']
        
        self.logger.info(f"Starting pipeline: coins={coins}, horizon={horizon}")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        results = {}
        
        for coin in coins:
            self.logger.info(f"Processing {coin.upper()}")
            
            try:
                # Fetch data
                df = self.fetcher.fetch_ohlcv(
                    coin_id=coin,
                    start_date=start_date,
                    end_date=end_date,
                    granularity=granularity
                )
                
                if df.empty:
                    self.logger.warning(f"No data fetched for {coin}")
                    continue
                
                # Calculate indicators
                df_with_indicators = calculate_all_indicators(df, self.config.indicators)
                
                # Store result
                results[coin] = {
                    'data': df_with_indicators,
                    'metadata': {
                        'coin': coin,
                        'horizon': horizon,
                        'granularity': granularity,
                        'lookback_days': lookback_days,
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'indicators': self.config.indicators,
                        'total_candles': len(df_with_indicators)
                    }
                }
                
                self.logger.info(f"Processed {len(df_with_indicators)} candles for {coin.upper()}")
                
            except Exception as e:
                self.logger.error(f"Failed to process {coin}: {str(e)}")
                continue
        
        # Export technical analysis results
        if results:
            self._export_results(results, horizon)
        else:
            self.logger.warning("No technical analysis results to export")
        
        # Collect and export additional market data
        self._collect_and_export_market_data(coins, horizon)
    
    def _export_results(self, results: Dict[str, Dict[str, Any]], horizon: str) -> None:
        """Export results in configured formats."""
        
        # Export JSON
        if self.config.should_export('json'):
            self.json_exporter.export(results, horizon)
            self.logger.info("JSON export completed")
        
        # Export CSV
        if self.config.should_export('csv'):
            self.csv_exporter.export(results, horizon)
            self.logger.info("CSV export completed")
        
        # Export SQLite
        if self.config.should_export('sqlite'):
            self.sqlite_exporter.export(results, horizon)
            self.logger.info("SQLite export completed")
        
        # Export charts
        if self.config.should_export('charts'):
            self.chart_exporter.export(results, horizon)
            self.logger.info("Chart export completed")
    
    def _collect_and_export_market_data(self, coins: List[str], horizon: str) -> None:
        """Collect and export additional market data for comprehensive analysis."""
        
        self.logger.info("Collecting additional market data...")
        
        # 1. Fetch and export news headlines
        if self.config.should_collect_market_data('news'):
            try:
                self.logger.info("Fetching news headlines...")
                news_limit = self.config.get_news_limit()
                news_data = self.fetcher.fetch_news(limit=news_limit)
                self.news_exporter.export(news_data, coins)
                self.logger.info("News data exported")
            except Exception as e:
                self.logger.error(f"Failed to fetch/export news data: {e}")
        else:
            self.logger.info("News collection disabled in configuration")
        
        # 2. Fetch and export global market data
        if self.config.should_collect_market_data('global'):
            try:
                self.logger.info("Fetching global market data...")
                global_data = self.fetcher.fetch_global_data()
                self.global_exporter.export(global_data)
                self.logger.info("Global market data exported")
            except Exception as e:
                self.logger.error(f"Failed to fetch/export global data: {e}")
        else:
            self.logger.info("Global data collection disabled in configuration")
        
        # 3. Fetch and export categories/sectors data
        if self.config.should_collect_market_data('categories'):
            try:
                self.logger.info("Fetching categories and sector data...")
                categories_data = self.fetcher.fetch_categories()
                self.categories_exporter.export(categories_data, coins)
                self.logger.info("Categories data exported")
            except Exception as e:
                self.logger.error(f"Failed to fetch/export categories data: {e}")
        else:
            self.logger.info("Categories data collection disabled in configuration")
        
        # 4. Fetch and export coin metadata (comprehensive)
        if self.config.should_collect_market_data('metadata'):
            try:
                self.logger.info("Fetching coin metadata...")
                metadata_by_coin = {}
                for coin in coins:
                    try:
                        metadata = self.fetcher.fetch_coin_metadata(coin)
                        metadata_by_coin[coin] = metadata
                        self.logger.debug(f"Fetched metadata for {coin}")
                    except Exception as e:
                        self.logger.warning(f"Failed to fetch metadata for {coin}: {e}")
                        metadata_by_coin[coin] = {}
                
                self.metadata_exporter.export(metadata_by_coin)
                self.logger.info("Metadata exported")
            except Exception as e:
                self.logger.error(f"Failed to fetch/export metadata: {e}")
        else:
            self.logger.info("Metadata collection disabled in configuration")
        
        # 5. Fetch and export tickers/exchange data (less frequent)
        if self.config.should_collect_market_data('tickers') and self._should_fetch_tickers(horizon):
            try:
                self.logger.info("Fetching tickers and exchange data...")
                tickers_by_coin = {}
                for coin in coins:
                    try:
                        tickers = self.fetcher.fetch_coin_tickers(coin)
                        tickers_by_coin[coin] = tickers
                        self.logger.debug(f"Fetched tickers for {coin}")
                    except Exception as e:
                        self.logger.warning(f"Failed to fetch tickers for {coin}: {e}")
                        tickers_by_coin[coin] = {}
                
                self.tickers_exporter.export(tickers_by_coin)
                self.logger.info("Tickers data exported")
            except Exception as e:
                self.logger.error(f"Failed to fetch/export tickers data: {e}")
        else:
            self.logger.info("Skipping tickers data (disabled or not needed for this run frequency)")
        
        # 6. Optional: Fetch onchain data for DeFi coins
        if self.config.should_collect_market_data('onchain'):
            self._fetch_onchain_data(coins)
        else:
            self.logger.info("Onchain data collection disabled in configuration")
    
    def _should_fetch_tickers(self, horizon: str) -> bool:
        """Determine if we should fetch ticker data based on frequency needs."""
        # Fetch tickers less frequently - only for swing horizon or every few runs
        return horizon == 'swing'
    
    def _fetch_onchain_data(self, coins: List[str]) -> None:
        """Fetch onchain DEX data for supported DeFi tokens (advanced feature)."""
        
        # Map coins to their primary chains
        coin_chain_mapping = {
            'ethereum': 'ethereum',
            'bitcoin': 'bitcoin',
            'solana': 'solana',
            'chainlink': 'ethereum',  # ERC-20 token
            'cardano': 'cardano',
            # Add more mappings as needed
        }
        
        self.logger.info("Attempting to fetch onchain data...")
        
        for coin in coins:
            chain = coin_chain_mapping.get(coin)
            if chain:
                try:
                    onchain_data = self.fetcher.fetch_onchain_data(chain, coin)
                    if onchain_data:
                        # Could export this data separately if available
                        self.logger.info(f"Fetched onchain data for {coin} on {chain}")
                    else:
                        self.logger.debug(f"No onchain data available for {coin} on {chain}")
                except Exception as e:
                    self.logger.debug(f"Onchain data not available for {coin}: {e}")
            else:
                self.logger.debug(f"No chain mapping available for {coin}")