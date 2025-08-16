import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

from src.pipeline import Pipeline
from src.config_loader import Config

class TestPipeline:
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        return Mock()

    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration."""
        config = Mock(spec=Config)
        config.get_horizon_config.return_value = {
            'lookback_days': 30,
            'granularity': '1h'
        }
        config.indicators = ['ema', 'rsi', 'macd']
        config.should_export.return_value = True
        return config

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_ohlcv_data(self):
        """Create sample OHLCV data."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='1H')
        
        np.random.seed(42)
        base_price = 100
        prices = []
        
        for i in range(100):
            trend = i * 0.01
            random_change = np.random.normal(0, 0.5)
            price = base_price + trend + random_change
            prices.append(max(price, 1))
        
        data = {
            'open': [p * np.random.uniform(0.99, 1.01) for p in prices],
            'high': [p * np.random.uniform(1.005, 1.02) for p in prices],
            'low': [p * np.random.uniform(0.98, 0.995) for p in prices],
            'close': prices,
            'volume': [np.random.uniform(1000, 10000) for _ in range(100)]
        }
        
        df = pd.DataFrame(data, index=dates)
        
        # Ensure OHLC relationships
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)
        
        return df

    @pytest.fixture
    def pipeline(self, sample_config, temp_output_dir, mock_logger):
        """Create a Pipeline instance."""
        return Pipeline(sample_config, temp_output_dir, mock_logger)

    def test_pipeline_init(self, sample_config, temp_output_dir, mock_logger):
        """Test Pipeline initialization."""
        pipeline = Pipeline(sample_config, temp_output_dir, mock_logger)
        
        assert pipeline.config == sample_config
        assert pipeline.output_dir == Path(temp_output_dir)
        assert pipeline.logger == mock_logger
        assert pipeline.fetcher is not None
        assert pipeline.json_exporter is not None
        assert pipeline.csv_exporter is not None
        assert pipeline.sqlite_exporter is not None
        assert pipeline.chart_exporter is not None

    @patch('src.pipeline.calculate_all_indicators')
    def test_run_single_coin_success(self, mock_calculate_indicators, pipeline, sample_ohlcv_data):
        """Test successful pipeline run for single coin."""
        # Mock the indicator calculation
        indicators_df = sample_ohlcv_data.copy()
        indicators_df['ema_20'] = indicators_df['close'].ewm(span=20).mean()
        indicators_df['rsi_14'] = 50.0  # Simple mock RSI
        mock_calculate_indicators.return_value = indicators_df
        
        # Mock the fetcher
        pipeline.fetcher.fetch_ohlcv = Mock(return_value=sample_ohlcv_data)
        
        # Mock exporters
        pipeline.json_exporter.export = Mock()
        pipeline.csv_exporter.export = Mock()
        pipeline.sqlite_exporter.export = Mock()
        pipeline.chart_exporter.export = Mock()
        
        # Run pipeline
        pipeline.run(['bitcoin'], 'intraday')
        
        # Verify fetcher was called
        pipeline.fetcher.fetch_ohlcv.assert_called_once()
        
        # Verify indicator calculation was called
        mock_calculate_indicators.assert_called_once()
        
        # Verify exporters were called
        pipeline.json_exporter.export.assert_called_once()
        pipeline.csv_exporter.export.assert_called_once()
        pipeline.sqlite_exporter.export.assert_called_once()
        pipeline.chart_exporter.export.assert_called_once()

    def test_run_multiple_coins(self, pipeline, sample_ohlcv_data):
        """Test pipeline run with multiple coins."""
        # Mock the fetcher to return data for each coin
        pipeline.fetcher.fetch_ohlcv = Mock(return_value=sample_ohlcv_data)
        
        # Mock exporters
        pipeline.json_exporter.export = Mock()
        pipeline.csv_exporter.export = Mock()
        pipeline.sqlite_exporter.export = Mock()
        pipeline.chart_exporter.export = Mock()
        
        with patch('src.pipeline.calculate_all_indicators') as mock_calc:
            mock_calc.return_value = sample_ohlcv_data
            pipeline.run(['bitcoin', 'ethereum'], 'intraday')
        
        # Fetcher should be called twice (once per coin)
        assert pipeline.fetcher.fetch_ohlcv.call_count == 2

    def test_run_empty_data(self, pipeline):
        """Test pipeline run with empty data."""
        # Mock fetcher to return empty DataFrame
        pipeline.fetcher.fetch_ohlcv = Mock(return_value=pd.DataFrame())
        
        # Mock exporters
        pipeline.json_exporter.export = Mock()
        pipeline.csv_exporter.export = Mock()
        pipeline.sqlite_exporter.export = Mock()
        pipeline.chart_exporter.export = Mock()
        
        pipeline.run(['bitcoin'], 'intraday')
        
        # Exporters should not be called with empty results
        pipeline.json_exporter.export.assert_not_called()

    def test_run_fetch_error(self, pipeline):
        """Test pipeline run with fetch error."""
        # Mock fetcher to raise an exception
        pipeline.fetcher.fetch_ohlcv = Mock(side_effect=Exception("API Error"))
        
        # Mock exporters
        pipeline.json_exporter.export = Mock()
        
        # Should not raise exception, but log error
        pipeline.run(['bitcoin'], 'intraday')
        
        # Logger should have logged an error
        pipeline.logger.error.assert_called()

    def test_run_invalid_horizon(self, pipeline):
        """Test pipeline run with invalid horizon."""
        pipeline.config.get_horizon_config.return_value = None
        
        with pytest.raises(ValueError, match="Horizon 'invalid' not found"):
            pipeline.run(['bitcoin'], 'invalid')

    def test_export_results_selective(self, pipeline, sample_ohlcv_data):
        """Test selective export based on configuration."""
        # Configure which exports to enable
        def mock_should_export(format_type):
            return format_type in ['json', 'sqlite']
        
        pipeline.config.should_export = Mock(side_effect=mock_should_export)
        
        # Mock exporters
        pipeline.json_exporter.export = Mock()
        pipeline.csv_exporter.export = Mock()
        pipeline.sqlite_exporter.export = Mock()
        pipeline.chart_exporter.export = Mock()
        
        # Create sample results
        results = {
            'bitcoin': {
                'data': sample_ohlcv_data,
                'metadata': {
                    'coin': 'bitcoin',
                    'horizon': 'intraday',
                    'granularity': '1h',
                    'lookback_days': 30,
                    'indicators': ['ema', 'rsi'],
                    'total_candles': len(sample_ohlcv_data)
                }
            }
        }
        
        pipeline._export_results(results, 'intraday')
        
        # Only JSON and SQLite should be called
        pipeline.json_exporter.export.assert_called_once()
        pipeline.csv_exporter.export.assert_not_called()
        pipeline.sqlite_exporter.export.assert_called_once()
        pipeline.chart_exporter.export.assert_not_called()

    @patch('src.pipeline.calculate_all_indicators')
    def test_metadata_generation(self, mock_calculate_indicators, pipeline, sample_ohlcv_data):
        """Test that metadata is correctly generated."""
        indicators_df = sample_ohlcv_data.copy()
        mock_calculate_indicators.return_value = indicators_df
        
        pipeline.fetcher.fetch_ohlcv = Mock(return_value=sample_ohlcv_data)
        
        # Capture the results passed to exporters
        exported_results = {}
        
        def capture_export(results, horizon):
            exported_results.update(results)
        
        pipeline.json_exporter.export = Mock(side_effect=capture_export)
        pipeline.csv_exporter.export = Mock()
        pipeline.sqlite_exporter.export = Mock()
        pipeline.chart_exporter.export = Mock()
        
        pipeline.run(['bitcoin'], 'intraday')
        
        # Check metadata structure
        assert 'bitcoin' in exported_results
        metadata = exported_results['bitcoin']['metadata']
        
        assert metadata['coin'] == 'bitcoin'
        assert metadata['horizon'] == 'intraday'
        assert metadata['granularity'] == '1h'
        assert metadata['lookback_days'] == 30
        assert metadata['total_candles'] == len(sample_ohlcv_data)
        assert 'start_date' in metadata
        assert 'end_date' in metadata
        assert 'indicators' in metadata

    def test_date_range_calculation(self, pipeline):
        """Test that date ranges are calculated correctly."""
        pipeline.fetcher.fetch_ohlcv = Mock(return_value=pd.DataFrame())
        
        with patch('src.pipeline.datetime') as mock_datetime:
            mock_now = datetime(2023, 6, 15, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            
            pipeline.run(['bitcoin'], 'intraday')
            
            # Check that fetcher was called with correct date range
            call_args = pipeline.fetcher.fetch_ohlcv.call_args[1]
            start_date = call_args['start_date']
            end_date = call_args['end_date']
            
            # Should be 30 days apart (based on config)
            assert (end_date - start_date).days == 30