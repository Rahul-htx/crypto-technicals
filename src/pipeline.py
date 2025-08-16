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
        
        # Export results
        if results:
            self._export_results(results, horizon)
        else:
            self.logger.warning("No results to export")
    
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