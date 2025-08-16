import pandas as pd
import numpy as np

def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
    """
    Calculate Bollinger Bands.
    
    Args:
        data: Price series (typically close prices)
        period: Period for moving average calculation (default 20)
        std_dev: Standard deviation multiplier (default 2.0)
    
    Returns:
        DataFrame with upper band, middle band (SMA), and lower band
    """
    # Calculate middle band (Simple Moving Average)
    middle_band = data.rolling(window=period).mean()
    
    # Calculate standard deviation
    std = data.rolling(window=period).std()
    
    # Calculate upper and lower bands
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    # Calculate %B (position within bands)
    percent_b = (data - lower_band) / (upper_band - lower_band)
    
    # Calculate bandwidth (volatility measure)
    bandwidth = (upper_band - lower_band) / middle_band
    
    return pd.DataFrame({
        'bb_upper': upper_band,
        'bb_middle': middle_band,
        'bb_lower': lower_band,
        'bb_percent_b': percent_b,
        'bb_bandwidth': bandwidth
    })

def add_bollinger_bands_to_dataframe(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
    """
    Add Bollinger Bands to the DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
        period: Period for moving average calculation
        std_dev: Standard deviation multiplier
    
    Returns:
        DataFrame with Bollinger Bands columns added
    """
    result = df.copy()
    bb_data = calculate_bollinger_bands(df['close'], period, std_dev)
    
    for col in bb_data.columns:
        result[col] = bb_data[col]
    
    return result