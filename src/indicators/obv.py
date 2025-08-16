import pandas as pd
import numpy as np

def calculate_obv(df: pd.DataFrame) -> pd.Series:
    """
    Calculate On-Balance Volume (OBV).
    
    Args:
        df: DataFrame with OHLCV data (requires close and volume columns)
    
    Returns:
        OBV series
    """
    # Calculate price changes
    price_change = df['close'].diff()
    
    # Determine volume direction based on price change
    volume_direction = pd.Series(np.where(price_change > 0, df['volume'],
                                         np.where(price_change < 0, -df['volume'], 0)), 
                                 index=df.index)
    
    # Calculate cumulative OBV
    obv = volume_direction.cumsum()
    
    return obv

def calculate_obv_ema(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    Calculate EMA of OBV for smoothing.
    
    Args:
        df: DataFrame with OHLCV data
        period: Period for EMA calculation
    
    Returns:
        OBV EMA series
    """
    obv = calculate_obv(df)
    return obv.ewm(span=period, adjust=False).mean()

def add_obv_to_dataframe(df: pd.DataFrame, ema_period: int = 20) -> pd.DataFrame:
    """
    Add OBV and OBV EMA to the DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
        ema_period: Period for OBV EMA calculation
    
    Returns:
        DataFrame with OBV columns added
    """
    result = df.copy()
    
    obv = calculate_obv(df)
    obv_ema = calculate_obv_ema(df, ema_period)
    
    result['obv'] = obv
    result[f'obv_ema_{ema_period}'] = obv_ema
    
    # Calculate volume moving average for comparison
    result[f'volume_ma_{ema_period}'] = df['volume'].rolling(window=ema_period).mean()
    
    return result