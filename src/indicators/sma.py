import pandas as pd
import numpy as np

def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA).
    
    Args:
        data: Price series (typically close prices)
        period: Period for SMA calculation
    
    Returns:
        SMA series
    """
    return data.rolling(window=period).mean()

def calculate_multiple_smas(df: pd.DataFrame, periods: list = [20, 50, 200]) -> pd.DataFrame:
    """
    Calculate multiple SMAs and add them to the DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
        periods: List of periods to calculate SMAs for
    
    Returns:
        DataFrame with SMA columns added
    """
    result = df.copy()
    
    for period in periods:
        result[f'sma_{period}'] = calculate_sma(df['close'], period)
    
    return result