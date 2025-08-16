import pandas as pd
import numpy as np

def calculate_true_range(df: pd.DataFrame) -> pd.Series:
    """
    Calculate True Range for each period.
    
    Args:
        df: DataFrame with OHLCV data (requires high, low, close columns)
    
    Returns:
        True Range series
    """
    # Current high - current low
    hl = df['high'] - df['low']
    
    # Current high - previous close (absolute value)
    hc = np.abs(df['high'] - df['close'].shift(1))
    
    # Current low - previous close (absolute value)
    lc = np.abs(df['low'] - df['close'].shift(1))
    
    # True Range is the maximum of the three
    true_range = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    
    return true_range

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR).
    
    Args:
        df: DataFrame with OHLCV data
        period: Period for ATR calculation (default 14)
    
    Returns:
        ATR series
    """
    true_range = calculate_true_range(df)
    
    # ATR is the exponential moving average of True Range
    atr = true_range.ewm(span=period, adjust=False).mean()
    
    return atr

def add_atr_to_dataframe(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Add ATR to the DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
        period: Period for ATR calculation
    
    Returns:
        DataFrame with ATR column added
    """
    result = df.copy()
    result[f'atr_{period}'] = calculate_atr(df, period)
    result[f'true_range'] = calculate_true_range(df)
    return result