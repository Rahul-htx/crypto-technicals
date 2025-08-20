import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class JSONExporter:
    """Export data and results to JSON format."""
    
    def __init__(self, output_dir: Path, config=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.config = config
    
    def export(self, results: Dict[str, Dict[str, Any]], horizon: str) -> None:
        """
        Export results to JSON files.
        
        Args:
            results: Dictionary containing coin data and metadata
            horizon: Time horizon (e.g., 'intraday', 'swing')
        """
        
        # Create horizon-specific directory
        horizon_dir = self.output_dir / horizon
        horizon_dir.mkdir(exist_ok=True)
        
        # Export individual coin files only if explicitly enabled
        if self.config and self.config.should_export_individual_coin_files():
            for coin, data in results.items():
                self._export_coin_data(coin, data, horizon_dir)
            
            # Export summary only if individual files are being created
            self._export_summary(results, horizon, horizon_dir)
        
        # Always export aggregated technical data file
        self._export_aggregated_technicals(results, horizon, horizon_dir)
    
    def _export_coin_data(self, coin: str, data: Dict[str, Any], output_dir: Path) -> None:
        """Export individual coin data to JSON."""
        
        df = data['data']
        metadata = data['metadata']
        
        # Convert DataFrame to records format for JSON serialization
        records = df.reset_index().to_dict('records')
        
        # Convert datetime objects to ISO format strings
        for record in records:
            if 'datetime' in record:
                record['datetime'] = record['datetime'].isoformat()
            # Convert any remaining datetime columns
            for key, value in record.items():
                if isinstance(value, pd.Timestamp):
                    record[key] = value.isoformat()
                elif pd.isna(value):
                    record[key] = None
        
        # Prepare full data structure
        coin_data = {
            'metadata': metadata,
            'data': records,
            'summary': self._generate_summary_stats(df),
            'latest_values': self._get_latest_values(df),
            'export_timestamp': datetime.now().isoformat()
        }
        
        # Write to file
        filename = f"{coin}_{metadata['granularity']}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(coin_data, f, indent=2, default=str)
    
    def _export_summary(self, results: Dict[str, Dict[str, Any]], horizon: str, output_dir: Path) -> None:
        """Export summary of all coins."""
        
        summary = {
            'horizon': horizon,
            'export_timestamp': datetime.now().isoformat(),
            'coins_processed': list(results.keys()),
            'total_coins': len(results),
            'coin_summaries': {}
        }
        
        for coin, data in results.items():
            df = data['data']
            metadata = data['metadata']
            
            summary['coin_summaries'][coin] = {
                'metadata': metadata,
                'latest_price': float(df['close'].iloc[-1]) if not df.empty else None,
                'price_change_pct': self._calculate_price_change_pct(df),
                'total_candles': len(df),
                'date_range': {
                    'start': df.index.min().isoformat() if not df.empty else None,
                    'end': df.index.max().isoformat() if not df.empty else None
                }
            }
        
        # Write summary file
        summary_file = output_dir / f"summary_{horizon}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
    
    def _generate_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for the data."""
        
        if df.empty:
            return {}
        
        stats = {
            'price_stats': {
                'min': float(df['close'].min()),
                'max': float(df['close'].max()),
                'mean': float(df['close'].mean()),
                'std': float(df['close'].std()),
                'current': float(df['close'].iloc[-1])
            },
            'volume_stats': {
                'min': float(df['volume'].min()),
                'max': float(df['volume'].max()),
                'mean': float(df['volume'].mean()),
                'current': float(df['volume'].iloc[-1])
            },
            'total_periods': len(df)
        }
        
        # Add indicator summaries if available
        if 'rsi_14' in df.columns:
            stats['rsi_current'] = float(df['rsi_14'].iloc[-1]) if not pd.isna(df['rsi_14'].iloc[-1]) else None
        
        if 'macd' in df.columns:
            stats['macd_current'] = float(df['macd'].iloc[-1]) if not pd.isna(df['macd'].iloc[-1]) else None
        
        return stats
    
    def _get_latest_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get the latest values for all indicators."""
        
        if df.empty:
            return {}
        
        latest = df.iloc[-1].to_dict()
        
        # Convert any NaN values to None and ensure JSON serializable
        for key, value in latest.items():
            if pd.isna(value):
                latest[key] = None
            elif isinstance(value, (pd.Timestamp, datetime)):
                latest[key] = value.isoformat()
            else:
                latest[key] = float(value) if isinstance(value, (int, float)) else str(value)
        
        return latest
    
    def _calculate_price_change_pct(self, df: pd.DataFrame) -> float:
        """Calculate percentage change from first to last price."""
        
        if df.empty or len(df) < 2:
            return 0.0
        
        first_price = df['close'].iloc[0]
        last_price = df['close'].iloc[-1]
        
        return float(((last_price - first_price) / first_price) * 100)
    
    def _export_aggregated_technicals(self, results: Dict[str, Dict[str, Any]], horizon: str, output_dir: Path) -> None:
        """Export all coins' technical data into a single aggregated file."""
        
        if not results:
            return
        
        # Get granularity from first coin's metadata
        first_coin_data = next(iter(results.values()))
        granularity = first_coin_data['metadata']['granularity']
        
        aggregated_data = {
            'metadata': {
                'horizon': horizon,
                'granularity': granularity,
                'coins': list(results.keys()),
                'total_coins': len(results),
                'export_timestamp': datetime.now().isoformat(),
                'lookback_days': first_coin_data['metadata']['lookback_days'],
                'indicators': first_coin_data['metadata']['indicators']
            },
            'coins': {},
            'cross_coin_analysis': self._generate_cross_coin_analysis(results)
        }
        
        # Add each coin's data and latest values
        for coin, data in results.items():
            df = data['data']
            
            # Convert DataFrame to records for JSON serialization
            records = df.reset_index().to_dict('records')
            
            # Convert datetime objects to ISO format
            for record in records:
                if 'datetime' in record:
                    record['datetime'] = record['datetime'].isoformat()
                for key, value in record.items():
                    if isinstance(value, pd.Timestamp):
                        record[key] = value.isoformat()
                    elif pd.isna(value):
                        record[key] = None
            
            aggregated_data['coins'][coin] = {
                'metadata': data['metadata'],
                'data': records,
                'summary_stats': self._generate_summary_stats(df),
                'latest_values': self._get_latest_values(df)
            }
        
        # Write aggregated file
        filename = f"all_coins_{granularity}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(aggregated_data, f, indent=2, default=str)
    
    def _generate_cross_coin_analysis(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate cross-coin analysis and comparisons."""
        
        if not results:
            return {}
        
        cross_analysis = {
            'price_performance': {},
            'volatility_comparison': {},
            'volume_analysis': {},
            'technical_signals': {}
        }
        
        # Price performance comparison
        for coin, data in results.items():
            df = data['data']
            if not df.empty:
                price_change = self._calculate_price_change_pct(df)
                volatility = float(df['close'].std() / df['close'].mean() * 100) if df['close'].mean() > 0 else 0
                avg_volume = float(df['volume'].mean())
                
                cross_analysis['price_performance'][coin] = price_change
                cross_analysis['volatility_comparison'][coin] = volatility
                cross_analysis['volume_analysis'][coin] = avg_volume
        
        # Sort by performance
        if cross_analysis['price_performance']:
            sorted_performance = sorted(cross_analysis['price_performance'].items(), 
                                      key=lambda x: x[1], reverse=True)
            cross_analysis['performance_ranking'] = [coin for coin, _ in sorted_performance]
        
        return cross_analysis