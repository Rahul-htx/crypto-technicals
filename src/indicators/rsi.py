import pandas as pd
import numpy as np

def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        data: Price series (typically close prices)
        period: Period for RSI calculation (default 14)
    
    Returns:
        RSI series (0-100 scale)
    """
    delta = data.diff()
    
    # Separate gains and losses
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    
    # Calculate average gains and losses using exponential moving average
    avg_gains = gains.ewm(alpha=1/period, adjust=False).mean()
    avg_losses = losses.ewm(alpha=1/period, adjust=False).mean()
    
    # Calculate RSI
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def add_rsi_to_dataframe(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Add RSI to the DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
        period: Period for RSI calculation
    
    Returns:
        DataFrame with RSI column added
    """
    result = df.copy()
    result[f'rsi_{period}'] = calculate_rsi(df['close'], period)
    return result