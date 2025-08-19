import requests
import pandas as pd
from datetime import datetime
import time
import logging
import os
from typing import Optional, Dict, Any
import json

class CoinGeckoFetcher:
    """Fetches cryptocurrency data from CoinGecko Pro API."""
    
    BASE_URL = "https://pro-api.coingecko.com/api/v3"
    RATE_LIMIT_DELAY = 0.1  # seconds between requests (Pro API supports higher rates)
    MAX_RETRIES = 3
    
    # CoinGecko granularity limits
    GRANULARITY_LIMITS = {
        '1h': 30,    # 1-hour data available for last 30 days
        '4h': 30,    # 4-hour data available for last 30 days  
        '1d': 365    # Daily data available for 365+ days
    }
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.session = requests.Session()
        
        # Get API key from environment
        api_key = os.getenv("COINGECKO_API_KEY")
        if not api_key:
            raise ValueError("COINGECKO_API_KEY environment variable is required for Pro API access")
        
        self.session.headers.update({
            'User-Agent': 'CryptoTechnicals/1.0 (Educational Purpose)',
            'x-cg-pro-api-key': api_key
        })
        
        self.logger.info("Initialized CoinGecko Pro API client")
    
    def fetch_ohlcv(
        self, 
        coin_id: str, 
        start_date: datetime, 
        end_date: datetime, 
        granularity: str = '1d'
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data for a coin.
        
        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum')
            start_date: Start date for data
            end_date: End date for data
            granularity: Data granularity ('1h', '4h', '1d')
        
        Returns:
            DataFrame with OHLCV data
        """
        
        # Validate granularity and date range
        days_requested = (end_date - start_date).days
        max_days = self.GRANULARITY_LIMITS.get(granularity, 365)
        
        if days_requested > max_days and granularity in ['1h', '4h']:
            self.logger.warning(
                f"Requested {days_requested} days but {granularity} data only available for {max_days} days. "
                f"Adjusting to daily granularity."
            )
            granularity = '1d'
        
        # Convert to timestamps
        from_timestamp = int(start_date.timestamp())
        to_timestamp = int(end_date.timestamp())
        
        url = f"{self.BASE_URL}/coins/{coin_id}/market_chart/range"
        params = {
            'vs_currency': 'usd',
            'from': from_timestamp,
            'to': to_timestamp
        }
        
        # Add granularity parameter if not daily
        if granularity != '1d':
            # CoinGecko uses 'hourly' for sub-daily data
            if granularity in ['1h', '4h']:
                # CoinGecko automatically determines granularity based on date range
                pass
        
        for attempt in range(self.MAX_RETRIES):
            try:
                self.logger.debug(f"Fetching {coin_id} data (attempt {attempt + 1})")
                
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse the response
                df = self._parse_market_chart_response(data, granularity)
                
                if df.empty:
                    self.logger.warning(f"No data returned for {coin_id}")
                    return df
                
                # Filter to exact date range if needed
                df = df[(df.index >= start_date) & (df.index <= end_date)]
                
                self.logger.info(f"Fetched {len(df)} candles for {coin_id}")
                return df
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed for {coin_id} (attempt {attempt + 1}): {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RATE_LIMIT_DELAY * (attempt + 1))
                else:
                    raise
            except Exception as e:
                self.logger.error(f"Unexpected error fetching {coin_id}: {e}")
                raise
            
            # Rate limiting
            time.sleep(self.RATE_LIMIT_DELAY)
        
        return pd.DataFrame()
    
    def _parse_market_chart_response(self, data: Dict[str, Any], granularity: str) -> pd.DataFrame:
        """Parse CoinGecko market chart response into OHLCV DataFrame."""
        
        if not all(key in data for key in ['prices', 'market_caps', 'total_volumes']):
            raise ValueError("Invalid response format from CoinGecko API")
        
        prices = data['prices']
        volumes = data['total_volumes']
        
        if not prices or not volumes:
            return pd.DataFrame()
        
        # Convert to DataFrame
        price_df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        volume_df = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
        
        # Merge on timestamp
        df = pd.merge(price_df, volume_df, on='timestamp', how='inner')
        
        # Convert timestamp to datetime
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('datetime', inplace=True)
        df.drop('timestamp', axis=1, inplace=True)
        
        # CoinGecko returns price points, not OHLCV candles
        # We need to resample to create OHLCV data
        ohlcv_df = self._resample_to_ohlcv(df, granularity)
        
        return ohlcv_df
    
    def _resample_to_ohlcv(self, df: pd.DataFrame, granularity: str) -> pd.DataFrame:
        """Resample price data to OHLCV format."""
        
        # Map granularity to pandas frequency
        freq_map = {
            '1h': '1H',
            '4h': '4H', 
            '1d': '1D'
        }
        
        freq = freq_map.get(granularity, '1D')
        
        # Resample price data to OHLCV
        ohlcv = df['price'].resample(freq).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last'
        })
        
        # Resample volume data
        volume = df['volume'].resample(freq).sum()
        
        # Combine OHLCV and volume
        result = pd.concat([ohlcv, volume], axis=1)
        
        # Drop rows with NaN values (incomplete candles)
        result.dropna(inplace=True)
        
        # Ensure all values are numeric
        for col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce')
        
        return result
    
    def get_supported_coins(self) -> Dict[str, str]:
        """Get list of supported coins from CoinGecko."""
        
        url = f"{self.BASE_URL}/coins/list"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            coins = response.json()
            return {coin['id']: coin['name'] for coin in coins}
            
        except Exception as e:
            self.logger.error(f"Failed to fetch supported coins: {e}")
            return {}
    
    def validate_coin_id(self, coin_id: str) -> bool:
        """Validate if coin ID exists on CoinGecko."""
        
        url = f"{self.BASE_URL}/coins/{coin_id}"
        
        try:
            response = self.session.get(url, timeout=30)
            return response.status_code == 200
            
        except Exception:
            return False