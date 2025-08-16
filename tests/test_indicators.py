import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.indicators.ema import calculate_ema, calculate_multiple_emas
from src.indicators.sma import calculate_sma, calculate_multiple_smas
from src.indicators.rsi import calculate_rsi, add_rsi_to_dataframe
from src.indicators.macd import calculate_macd, add_macd_to_dataframe
from src.indicators.bollinger import calculate_bollinger_bands, add_bollinger_bands_to_dataframe
from src.indicators.atr import calculate_atr, add_atr_to_dataframe
from src.indicators.obv import calculate_obv, add_obv_to_dataframe
from src.indicators import calculate_all_indicators

@pytest.fixture
def sample_ohlcv_data():
    """Create sample OHLCV data for testing."""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='1D')
    
    # Generate synthetic price data with some trend and volatility
    np.random.seed(42)
    base_price = 100
    prices = []
    
    for i in range(100):
        # Add trend and random walk
        trend = i * 0.1
        random_change = np.random.normal(0, 2)
        price = base_price + trend + random_change
        prices.append(max(price, 1))  # Ensure positive prices
    
    # Create OHLCV data
    data = {
        'open': [p * np.random.uniform(0.98, 1.02) for p in prices],
        'high': [p * np.random.uniform(1.01, 1.05) for p in prices],
        'low': [p * np.random.uniform(0.95, 0.99) for p in prices],
        'close': prices,
        'volume': [np.random.uniform(1000, 10000) for _ in range(100)]
    }
    
    df = pd.DataFrame(data, index=dates)
    
    # Ensure OHLC relationships are correct
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)
    
    return df

class TestEMA:
    def test_calculate_ema(self, sample_ohlcv_data):
        """Test EMA calculation."""
        ema = calculate_ema(sample_ohlcv_data['close'], 20)
        
        assert len(ema) == len(sample_ohlcv_data)
        assert not ema.isna().all()
        assert ema.iloc[-1] is not np.nan

    def test_calculate_multiple_emas(self, sample_ohlcv_data):
        """Test multiple EMA calculation."""
        result = calculate_multiple_emas(sample_ohlcv_data, [10, 20, 50])
        
        assert 'ema_10' in result.columns
        assert 'ema_20' in result.columns
        assert 'ema_50' in result.columns
        assert len(result) == len(sample_ohlcv_data)

class TestSMA:
    def test_calculate_sma(self, sample_ohlcv_data):
        """Test SMA calculation."""
        sma = calculate_sma(sample_ohlcv_data['close'], 20)
        
        assert len(sma) == len(sample_ohlcv_data)
        # First 19 values should be NaN
        assert sma.iloc[:19].isna().all()
        assert not sma.iloc[19:].isna().any()

    def test_calculate_multiple_smas(self, sample_ohlcv_data):
        """Test multiple SMA calculation."""
        result = calculate_multiple_smas(sample_ohlcv_data, [10, 20, 50])
        
        assert 'sma_10' in result.columns
        assert 'sma_20' in result.columns
        assert 'sma_50' in result.columns

class TestRSI:
    def test_calculate_rsi(self, sample_ohlcv_data):
        """Test RSI calculation."""
        rsi = calculate_rsi(sample_ohlcv_data['close'], 14)
        
        assert len(rsi) == len(sample_ohlcv_data)
        # RSI should be between 0 and 100
        assert (rsi.dropna() >= 0).all()
        assert (rsi.dropna() <= 100).all()

    def test_add_rsi_to_dataframe(self, sample_ohlcv_data):
        """Test adding RSI to DataFrame."""
        result = add_rsi_to_dataframe(sample_ohlcv_data, 14)
        
        assert 'rsi_14' in result.columns
        assert len(result) == len(sample_ohlcv_data)

class TestMACD:
    def test_calculate_macd(self, sample_ohlcv_data):
        """Test MACD calculation."""
        macd_data = calculate_macd(sample_ohlcv_data['close'])
        
        assert 'macd' in macd_data.columns
        assert 'macd_signal' in macd_data.columns
        assert 'macd_histogram' in macd_data.columns
        assert len(macd_data) == len(sample_ohlcv_data)

    def test_add_macd_to_dataframe(self, sample_ohlcv_data):
        """Test adding MACD to DataFrame."""
        result = add_macd_to_dataframe(sample_ohlcv_data)
        
        assert 'macd' in result.columns
        assert 'macd_signal' in result.columns
        assert 'macd_histogram' in result.columns

class TestBollingerBands:
    def test_calculate_bollinger_bands(self, sample_ohlcv_data):
        """Test Bollinger Bands calculation."""
        bb_data = calculate_bollinger_bands(sample_ohlcv_data['close'])
        
        assert 'bb_upper' in bb_data.columns
        assert 'bb_middle' in bb_data.columns
        assert 'bb_lower' in bb_data.columns
        assert 'bb_percent_b' in bb_data.columns
        assert 'bb_bandwidth' in bb_data.columns
        
        # Upper band should be >= lower band
        valid_data = bb_data.dropna()
        assert (valid_data['bb_upper'] >= valid_data['bb_lower']).all()

    def test_add_bollinger_bands_to_dataframe(self, sample_ohlcv_data):
        """Test adding Bollinger Bands to DataFrame."""
        result = add_bollinger_bands_to_dataframe(sample_ohlcv_data)
        
        assert 'bb_upper' in result.columns
        assert 'bb_middle' in result.columns
        assert 'bb_lower' in result.columns

class TestATR:
    def test_calculate_atr(self, sample_ohlcv_data):
        """Test ATR calculation."""
        atr = calculate_atr(sample_ohlcv_data, 14)
        
        assert len(atr) == len(sample_ohlcv_data)
        # ATR should be positive
        assert (atr.dropna() >= 0).all()

    def test_add_atr_to_dataframe(self, sample_ohlcv_data):
        """Test adding ATR to DataFrame."""
        result = add_atr_to_dataframe(sample_ohlcv_data, 14)
        
        assert 'atr_14' in result.columns
        assert 'true_range' in result.columns

class TestOBV:
    def test_calculate_obv(self, sample_ohlcv_data):
        """Test OBV calculation."""
        obv = calculate_obv(sample_ohlcv_data)
        
        assert len(obv) == len(sample_ohlcv_data)
        # OBV is cumulative, so it should be monotonic in trend

    def test_add_obv_to_dataframe(self, sample_ohlcv_data):
        """Test adding OBV to DataFrame."""
        result = add_obv_to_dataframe(sample_ohlcv_data, 20)
        
        assert 'obv' in result.columns
        assert 'obv_ema_20' in result.columns
        assert 'volume_ma_20' in result.columns

class TestAllIndicators:
    def test_calculate_all_indicators(self, sample_ohlcv_data):
        """Test calculating all indicators together."""
        indicators = ['ema', 'sma', 'rsi', 'macd', 'bollinger', 'atr', 'obv']
        result = calculate_all_indicators(sample_ohlcv_data, indicators)
        
        # Check that various indicators are present
        assert 'ema_20' in result.columns
        assert 'sma_20' in result.columns
        assert 'rsi_14' in result.columns
        assert 'macd' in result.columns
        assert 'bb_upper' in result.columns
        assert 'atr_14' in result.columns
        assert 'obv' in result.columns
        
        # Check data integrity
        assert len(result) == len(sample_ohlcv_data)
        assert not result[['open', 'high', 'low', 'close', 'volume']].isna().any().any()

    def test_unknown_indicator(self, sample_ohlcv_data):
        """Test handling of unknown indicator."""
        indicators = ['unknown_indicator', 'rsi']
        result = calculate_all_indicators(sample_ohlcv_data, indicators)
        
        # Should still work with known indicators
        assert 'rsi_14' in result.columns
        # Should not crash on unknown indicator