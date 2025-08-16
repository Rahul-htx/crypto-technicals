import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import json

from src.fetch.coingecko import CoinGeckoFetcher

class TestCoinGeckoFetcher:
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        return Mock()

    @pytest.fixture
    def fetcher(self, mock_logger):
        """Create a CoinGeckoFetcher instance."""
        return CoinGeckoFetcher(mock_logger)

    @pytest.fixture
    def sample_api_response(self):
        """Create sample API response data."""
        base_time = datetime(2023, 1, 1).timestamp() * 1000  # Convert to milliseconds
        
        prices = []
        volumes = []
        for i in range(100):
            timestamp = base_time + (i * 3600000)  # Hourly data
            price = 100 + np.random.normal(0, 5)  # Random price around 100
            volume = 1000000 + np.random.normal(0, 100000)  # Random volume
            
            prices.append([timestamp, price])
            volumes.append([timestamp, volume])
        
        return {
            'prices': prices,
            'market_caps': volumes,  # Using volumes as placeholder
            'total_volumes': volumes
        }

    def test_init(self, mock_logger):
        """Test CoinGeckoFetcher initialization."""
        fetcher = CoinGeckoFetcher(mock_logger)
        
        assert fetcher.logger == mock_logger
        assert fetcher.session is not None
        assert fetcher.BASE_URL == "https://api.coingecko.com/api/v3"

    def test_parse_market_chart_response(self, fetcher, sample_api_response):
        """Test parsing of market chart response."""
        df = fetcher._parse_market_chart_response(sample_api_response, '1h')
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'open' in df.columns
        assert 'high' in df.columns
        assert 'low' in df.columns
        assert 'close' in df.columns
        assert 'volume' in df.columns
        
        # Check that OHLC relationships are maintained
        assert (df['high'] >= df['low']).all()
        assert (df['high'] >= df['open']).all()
        assert (df['high'] >= df['close']).all()
        assert (df['low'] <= df['open']).all()
        assert (df['low'] <= df['close']).all()

    def test_parse_empty_response(self, fetcher):
        """Test parsing of empty response."""
        empty_response = {
            'prices': [],
            'market_caps': [],
            'total_volumes': []
        }
        
        df = fetcher._parse_market_chart_response(empty_response, '1h')
        assert df.empty

    def test_parse_invalid_response(self, fetcher):
        """Test parsing of invalid response."""
        invalid_response = {'invalid': 'data'}
        
        with pytest.raises(ValueError):
            fetcher._parse_market_chart_response(invalid_response, '1h')

    def test_resample_to_ohlcv_hourly(self, fetcher):
        """Test resampling to hourly OHLCV."""
        # Create sample price data
        dates = pd.date_range(start='2023-01-01', periods=100, freq='15T')
        prices = [100 + i * 0.1 + np.random.normal(0, 1) for i in range(100)]
        volumes = [1000 + np.random.normal(0, 100) for _ in range(100)]
        
        df = pd.DataFrame({
            'price': prices,
            'volume': volumes
        }, index=dates)
        
        result = fetcher._resample_to_ohlcv(df, '1h')
        
        assert isinstance(result, pd.DataFrame)
        assert 'open' in result.columns
        assert 'high' in result.columns
        assert 'low' in result.columns
        assert 'close' in result.columns
        assert 'volume' in result.columns
        
        # Should have fewer rows due to resampling
        assert len(result) < len(df)

    @patch('src.fetch.coingecko.requests.Session.get')
    def test_fetch_ohlcv_success(self, mock_get, fetcher, sample_api_response):
        """Test successful OHLCV fetch."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 10)
        
        df = fetcher.fetch_ohlcv('bitcoin', start_date, end_date, '1h')
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'open' in df.columns
        assert 'high' in df.columns
        assert 'low' in df.columns
        assert 'close' in df.columns
        assert 'volume' in df.columns

    @patch('src.fetch.coingecko.requests.Session.get')
    def test_fetch_ohlcv_api_error(self, mock_get, fetcher):
        """Test handling of API errors."""
        # Mock API error
        mock_get.side_effect = Exception("API Error")
        
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 10)
        
        with pytest.raises(Exception):
            fetcher.fetch_ohlcv('bitcoin', start_date, end_date, '1h')

    @patch('src.fetch.coingecko.requests.Session.get')
    def test_fetch_ohlcv_empty_response(self, mock_get, fetcher):
        """Test handling of empty API response."""
        # Mock empty response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'prices': [],
            'market_caps': [],
            'total_volumes': []
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 10)
        
        df = fetcher.fetch_ohlcv('bitcoin', start_date, end_date, '1h')
        
        assert df.empty

    def test_granularity_adjustment(self, fetcher, mock_logger):
        """Test automatic granularity adjustment for long periods."""
        # Test that requesting too long a period with hourly data adjusts to daily
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)  # 365 days - should force daily
        
        with patch.object(fetcher.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'prices': [[1672531200000, 100]],  # Single data point
                'market_caps': [[1672531200000, 1000000]],
                'total_volumes': [[1672531200000, 50000]]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            fetcher.fetch_ohlcv('bitcoin', start_date, end_date, '1h')
            
            # Should log a warning about granularity adjustment
            mock_logger.warning.assert_called()

    @patch('src.fetch.coingecko.requests.Session.get')
    def test_get_supported_coins(self, mock_get, fetcher):
        """Test getting supported coins."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'id': 'bitcoin', 'name': 'Bitcoin'},
            {'id': 'ethereum', 'name': 'Ethereum'}
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        coins = fetcher.get_supported_coins()
        
        assert isinstance(coins, dict)
        assert 'bitcoin' in coins
        assert 'ethereum' in coins
        assert coins['bitcoin'] == 'Bitcoin'

    @patch('src.fetch.coingecko.requests.Session.get')
    def test_validate_coin_id_valid(self, mock_get, fetcher):
        """Test validation of valid coin ID."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        assert fetcher.validate_coin_id('bitcoin') == True

    @patch('src.fetch.coingecko.requests.Session.get')
    def test_validate_coin_id_invalid(self, mock_get, fetcher):
        """Test validation of invalid coin ID."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        assert fetcher.validate_coin_id('invalid_coin') == False

    @patch('src.fetch.coingecko.requests.Session.get')
    def test_rate_limiting(self, mock_get, fetcher):
        """Test that rate limiting delay is applied."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'prices': [[1672531200000, 100]],
            'market_caps': [[1672531200000, 1000000]],
            'total_volumes': [[1672531200000, 50000]]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 2)
        
        with patch('time.sleep') as mock_sleep:
            fetcher.fetch_ohlcv('bitcoin', start_date, end_date, '1h')
            
            # Should call sleep for rate limiting
            mock_sleep.assert_called_with(fetcher.RATE_LIMIT_DELAY)