import pandas as pd
import numpy as np

def calculate_macd(data: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        data: Price series (typically close prices)
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
        signal_period: Signal line EMA period (default 9)
    
    Returns:
        DataFrame with MACD line, signal line, and histogram
    """
    # Calculate EMAs
    ema_fast = data.ewm(span=fast_period, adjust=False).mean()
    ema_slow = data.ewm(span=slow_period, adjust=False).mean()
    
    # MACD line
    macd_line = ema_fast - ema_slow
    
    # Signal line (EMA of MACD line)
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # MACD histogram
    histogram = macd_line - signal_line
    
    return pd.DataFrame({
        'macd': macd_line,
        'macd_signal': signal_line,
        'macd_histogram': histogram
    })

def add_macd_to_dataframe(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
    """
    Add MACD indicators to the DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal line EMA period
    
    Returns:
        DataFrame with MACD columns added
    """
    result = df.copy()
    macd_data = calculate_macd(df['close'], fast_period, slow_period, signal_period)
    
    result['macd'] = macd_data['macd']
    result['macd_signal'] = macd_data['macd_signal']
    result['macd_histogram'] = macd_data['macd_histogram']
    
    return result