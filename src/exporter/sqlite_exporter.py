import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class SQLiteExporter:
    """Export data to SQLite database."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, results: Dict[str, Dict[str, Any]], horizon: str) -> None:
        """
        Export results to SQLite database.
        
        Args:
            results: Dictionary containing coin data and metadata
            horizon: Time horizon (e.g., 'intraday', 'swing')
        """
        
        # Create database file
        db_filename = f"crypto_technicals_{horizon}.db"
        db_path = self.output_dir / db_filename
        
        with sqlite3.connect(db_path) as conn:
            # Create tables and insert data
            self._create_tables(conn)
            self._insert_data(conn, results, horizon)
            self._create_indexes(conn)
    
    def _create_tables(self, conn: sqlite3.Connection) -> None:
        """Create database tables."""
        
        # Main data table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ohlcv_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT NOT NULL,
                datetime TEXT NOT NULL,
                granularity TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Technical indicators table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT NOT NULL,
                datetime TEXT NOT NULL,
                granularity TEXT NOT NULL,
                indicator_name TEXT NOT NULL,
                indicator_value REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Metadata table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS run_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT NOT NULL,
                horizon TEXT NOT NULL,
                granularity TEXT NOT NULL,
                lookback_days INTEGER,
                start_date TEXT,
                end_date TEXT,
                total_candles INTEGER,
                indicators_calculated TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Summary statistics table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS summary_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT NOT NULL,
                horizon TEXT NOT NULL,
                granularity TEXT NOT NULL,
                price_first REAL,
                price_last REAL,
                price_min REAL,
                price_max REAL,
                price_mean REAL,
                price_std REAL,
                price_change_pct REAL,
                volume_mean REAL,
                volume_total REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
    
    def _insert_data(self, conn: sqlite3.Connection, results: Dict[str, Dict[str, Any]], horizon: str) -> None:
        """Insert data into tables."""
        
        for coin, data in results.items():
            df = data['data']
            metadata = data['metadata']
            
            if df.empty:
                continue
            
            # Insert OHLCV data
            self._insert_ohlcv_data(conn, coin, df, metadata['granularity'])
            
            # Insert indicators data
            self._insert_indicators_data(conn, coin, df, metadata['granularity'])
            
            # Insert metadata
            self._insert_metadata(conn, coin, metadata, horizon)
            
            # Insert summary statistics
            self._insert_summary_stats(conn, coin, df, metadata, horizon)
    
    def _insert_ohlcv_data(self, conn: sqlite3.Connection, coin: str, df: pd.DataFrame, granularity: str) -> None:
        """Insert OHLCV data."""
        
        ohlcv_data = []
        for idx, row in df.iterrows():
            ohlcv_data.append((
                coin,
                idx.isoformat(),
                granularity,
                float(row['open']),
                float(row['high']),
                float(row['low']),
                float(row['close']),
                float(row['volume'])
            ))
        
        conn.executemany("""
            INSERT INTO ohlcv_data (coin, datetime, granularity, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ohlcv_data)
    
    def _insert_indicators_data(self, conn: sqlite3.Connection, coin: str, df: pd.DataFrame, granularity: str) -> None:
        """Insert technical indicators data."""
        
        indicator_data = []
        
        # Get all indicator columns (exclude OHLCV columns)
        base_columns = ['open', 'high', 'low', 'close', 'volume']
        indicator_columns = [col for col in df.columns if col not in base_columns]
        
        for idx, row in df.iterrows():
            datetime_str = idx.isoformat()
            
            for indicator_col in indicator_columns:
                value = row[indicator_col]
                if pd.notna(value):  # Only insert non-NaN values
                    indicator_data.append((
                        coin,
                        datetime_str,
                        granularity,
                        indicator_col,
                        float(value)
                    ))
        
        if indicator_data:
            conn.executemany("""
                INSERT INTO indicators (coin, datetime, granularity, indicator_name, indicator_value)
                VALUES (?, ?, ?, ?, ?)
            """, indicator_data)
    
    def _insert_metadata(self, conn: sqlite3.Connection, coin: str, metadata: Dict[str, Any], horizon: str) -> None:
        """Insert run metadata."""
        
        indicators_str = ','.join(metadata.get('indicators', []))
        
        conn.execute("""
            INSERT INTO run_metadata (
                coin, horizon, granularity, lookback_days, start_date, end_date, 
                total_candles, indicators_calculated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            coin,
            horizon,
            metadata['granularity'],
            metadata['lookback_days'],
            metadata['start_date'],
            metadata['end_date'],
            metadata['total_candles'],
            indicators_str
        ))
    
    def _insert_summary_stats(self, conn: sqlite3.Connection, coin: str, df: pd.DataFrame, metadata: Dict[str, Any], horizon: str) -> None:
        """Insert summary statistics."""
        
        if df.empty:
            return
        
        price_change_pct = ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
        
        conn.execute("""
            INSERT INTO summary_stats (
                coin, horizon, granularity, price_first, price_last, price_min, price_max,
                price_mean, price_std, price_change_pct, volume_mean, volume_total
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            coin,
            horizon,
            metadata['granularity'],
            float(df['close'].iloc[0]),
            float(df['close'].iloc[-1]),
            float(df['close'].min()),
            float(df['close'].max()),
            float(df['close'].mean()),
            float(df['close'].std()),
            float(price_change_pct),
            float(df['volume'].mean()),
            float(df['volume'].sum())
        ))
    
    def _create_indexes(self, conn: sqlite3.Connection) -> None:
        """Create database indexes for better performance."""
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_ohlcv_coin_datetime ON ohlcv_data(coin, datetime)",
            "CREATE INDEX IF NOT EXISTS idx_ohlcv_granularity ON ohlcv_data(granularity)",
            "CREATE INDEX IF NOT EXISTS idx_indicators_coin_datetime ON indicators(coin, datetime)",
            "CREATE INDEX IF NOT EXISTS idx_indicators_name ON indicators(indicator_name)",
            "CREATE INDEX IF NOT EXISTS idx_metadata_coin_horizon ON run_metadata(coin, horizon)",
            "CREATE INDEX IF NOT EXISTS idx_summary_coin_horizon ON summary_stats(coin, horizon)"
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
        
        conn.commit()