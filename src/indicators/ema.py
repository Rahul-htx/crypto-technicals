import pandas as pd
import numpy as np

def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA).
    
    Args:
        data: Price series (typically close prices)
        period: Period for EMA calculation
    
    Returns:
        EMA series
    """
    return data.ewm(span=period, adjust=False).mean()

def calculate_multiple_emas(df: pd.DataFrame, periods: list = [20, 50, 200]) -> pd.DataFrame:
    """
    Calculate multiple EMAs and add them to the DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
        periods: List of periods to calculate EMAs for
    
    Returns:
        DataFrame with EMA columns added
    """
    result = df.copy()
    
    for period in periods:
        result[f'ema_{period}'] = calculate_ema(df['close'], period)
    
    return result