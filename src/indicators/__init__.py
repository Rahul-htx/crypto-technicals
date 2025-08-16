import pandas as pd
from typing import List

from .ema import calculate_multiple_emas
from .sma import calculate_multiple_smas
from .rsi import add_rsi_to_dataframe
from .macd import add_macd_to_dataframe
from .bollinger import add_bollinger_bands_to_dataframe
from .atr import add_atr_to_dataframe
from .adx import add_adx_to_dataframe
from .obv import add_obv_to_dataframe

def calculate_all_indicators(df: pd.DataFrame, indicators: List[str]) -> pd.DataFrame:
    """
    Calculate all requested technical indicators for the given DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
        indicators: List of indicator names to calculate
    
    Returns:
        DataFrame with all indicators added
    """
    result = df.copy()
    
    # Calculate each indicator based on the list
    for indicator in indicators:
        if indicator == 'ema':
            result = calculate_multiple_emas(result, periods=[20, 50, 200])
        elif indicator == 'sma':
            result = calculate_multiple_smas(result, periods=[20, 50, 200])
        elif indicator == 'rsi':
            result = add_rsi_to_dataframe(result, period=14)
        elif indicator == 'macd':
            result = add_macd_to_dataframe(result, fast_period=12, slow_period=26, signal_period=9)
        elif indicator == 'bollinger':
            result = add_bollinger_bands_to_dataframe(result, period=20, std_dev=2.0)
        elif indicator == 'atr':
            result = add_atr_to_dataframe(result, period=14)
        elif indicator == 'adx':
            result = add_adx_to_dataframe(result, period=14)
        elif indicator == 'obv':
            result = add_obv_to_dataframe(result, ema_period=20)
        else:
            print(f"Warning: Unknown indicator '{indicator}' skipped")
    
    return result

# Export individual functions for direct use
__all__ = [
    'calculate_all_indicators',
    'calculate_multiple_emas',
    'calculate_multiple_smas', 
    'add_rsi_to_dataframe',
    'add_macd_to_dataframe',
    'add_bollinger_bands_to_dataframe',
    'add_atr_to_dataframe',
    'add_adx_to_dataframe',
    'add_obv_to_dataframe'
]