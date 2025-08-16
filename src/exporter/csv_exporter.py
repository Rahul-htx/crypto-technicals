import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class CSVExporter:
    """Export data to CSV format."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, results: Dict[str, Dict[str, Any]], horizon: str) -> None:
        """
        Export results to CSV files.
        
        Args:
            results: Dictionary containing coin data and metadata
            horizon: Time horizon (e.g., 'intraday', 'swing')
        """
        
        # Create horizon-specific directory
        horizon_dir = self.output_dir / horizon
        horizon_dir.mkdir(exist_ok=True)
        
        # Export each coin's data
        for coin, data in results.items():
            self._export_coin_data(coin, data, horizon_dir)
        
        # Export combined data
        self._export_combined_data(results, horizon, horizon_dir)
    
    def _export_coin_data(self, coin: str, data: Dict[str, Any], output_dir: Path) -> None:
        """Export individual coin data to CSV."""
        
        df = data['data']
        metadata = data['metadata']
        
        if df.empty:
            return
        
        # Reset index to include datetime as column
        export_df = df.reset_index()
        
        # Round numeric columns to appropriate precision
        numeric_columns = export_df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            if col in ['close', 'open', 'high', 'low']:
                export_df[col] = export_df[col].round(8)  # Price precision
            elif 'volume' in col:
                export_df[col] = export_df[col].round(2)  # Volume precision
            else:
                export_df[col] = export_df[col].round(6)  # Indicator precision
        
        # Create filename
        filename = f"{coin}_{metadata['granularity']}.csv"
        filepath = output_dir / filename
        
        # Export to CSV
        export_df.to_csv(filepath, index=False)
        
        # Create metadata file
        metadata_filename = f"{coin}_{metadata['granularity']}_metadata.csv"
        metadata_filepath = output_dir / metadata_filename
        
        metadata_df = pd.DataFrame([metadata])
        metadata_df.to_csv(metadata_filepath, index=False)
    
    def _export_combined_data(self, results: Dict[str, Dict[str, Any]], horizon: str, output_dir: Path) -> None:
        """Export combined data for all coins."""
        
        combined_data = []
        
        for coin, data in results.items():
            df = data['data']
            metadata = data['metadata']
            
            if df.empty:
                continue
            
            # Add coin identifier to the data
            coin_df = df.reset_index().copy()
            coin_df['coin'] = coin
            coin_df['granularity'] = metadata['granularity']
            
            combined_data.append(coin_df)
        
        if not combined_data:
            return
        
        # Combine all data
        combined_df = pd.concat(combined_data, ignore_index=True)
        
        # Reorder columns to put identifiers first
        cols = ['coin', 'granularity', 'datetime'] + [col for col in combined_df.columns if col not in ['coin', 'granularity', 'datetime']]
        combined_df = combined_df[cols]
        
        # Round numeric columns
        numeric_columns = combined_df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            if col in ['close', 'open', 'high', 'low']:
                combined_df[col] = combined_df[col].round(8)
            elif 'volume' in col:
                combined_df[col] = combined_df[col].round(2)
            else:
                combined_df[col] = combined_df[col].round(6)
        
        # Export combined CSV
        combined_filename = f"combined_{horizon}.csv"
        combined_filepath = output_dir / combined_filename
        combined_df.to_csv(combined_filepath, index=False)
        
        # Export summary statistics
        self._export_summary_stats(results, horizon, output_dir)
    
    def _export_summary_stats(self, results: Dict[str, Dict[str, Any]], horizon: str, output_dir: Path) -> None:
        """Export summary statistics as CSV."""
        
        summary_data = []
        
        for coin, data in results.items():
            df = data['data']
            metadata = data['metadata']
            
            if df.empty:
                continue
            
            stats = {
                'coin': coin,
                'granularity': metadata['granularity'],
                'total_candles': len(df),
                'date_start': df.index.min(),
                'date_end': df.index.max(),
                'price_first': df['close'].iloc[0],
                'price_last': df['close'].iloc[-1],
                'price_min': df['close'].min(),
                'price_max': df['close'].max(),
                'price_mean': df['close'].mean(),
                'price_std': df['close'].std(),
                'price_change_pct': ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100,
                'volume_mean': df['volume'].mean(),
                'volume_total': df['volume'].sum()
            }
            
            # Add latest indicator values
            if 'rsi_14' in df.columns:
                stats['rsi_latest'] = df['rsi_14'].iloc[-1] if not pd.isna(df['rsi_14'].iloc[-1]) else None
            
            if 'macd' in df.columns:
                stats['macd_latest'] = df['macd'].iloc[-1] if not pd.isna(df['macd'].iloc[-1]) else None
            
            if 'bb_percent_b' in df.columns:
                stats['bb_percent_b_latest'] = df['bb_percent_b'].iloc[-1] if not pd.isna(df['bb_percent_b'].iloc[-1]) else None
            
            if 'adx_14' in df.columns:
                stats['adx_latest'] = df['adx_14'].iloc[-1] if not pd.isna(df['adx_14'].iloc[-1]) else None
            
            summary_data.append(stats)
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            
            # Round numeric columns
            numeric_columns = summary_df.select_dtypes(include=['float64', 'int64']).columns
            for col in numeric_columns:
                summary_df[col] = summary_df[col].round(6)
            
            # Export summary
            summary_filename = f"summary_{horizon}.csv"
            summary_filepath = output_dir / summary_filename
            summary_df.to_csv(summary_filepath, index=False)