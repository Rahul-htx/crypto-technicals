import pandas as pd
import numpy as np

def calculate_directional_movement(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Directional Movement (+DM and -DM).
    
    Args:
        df: DataFrame with OHLCV data
    
    Returns:
        DataFrame with +DM and -DM columns
    """
    # Calculate price movements
    high_diff = df['high'].diff()
    low_diff = df['low'].diff()
    
    # Calculate +DM and -DM
    plus_dm = pd.Series(np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0), index=df.index)
    minus_dm = pd.Series(np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0), index=df.index)
    
    return pd.DataFrame({
        'plus_dm': plus_dm,
        'minus_dm': minus_dm
    })

def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Calculate ADX (Average Directional Index) and related indicators.
    
    Args:
        df: DataFrame with OHLCV data
        period: Period for ADX calculation (default 14)
    
    Returns:
        DataFrame with ADX, +DI, and -DI
    """
    from .atr import calculate_true_range
    
    # Calculate True Range
    tr = calculate_true_range(df)
    
    # Calculate Directional Movement
    dm_data = calculate_directional_movement(df)
    
    # Smooth the values using exponential moving average
    tr_smooth = tr.ewm(span=period, adjust=False).mean()
    plus_dm_smooth = dm_data['plus_dm'].ewm(span=period, adjust=False).mean()
    minus_dm_smooth = dm_data['minus_dm'].ewm(span=period, adjust=False).mean()
    
    # Calculate Directional Indicators
    plus_di = 100 * (plus_dm_smooth / tr_smooth)
    minus_di = 100 * (minus_dm_smooth / tr_smooth)
    
    # Calculate DX (Directional Index)
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    
    # Calculate ADX (smoothed DX)
    adx = dx.ewm(span=period, adjust=False).mean()
    
    return pd.DataFrame({
        'adx': adx,
        'plus_di': plus_di,
        'minus_di': minus_di,
        'dx': dx
    })

def add_adx_to_dataframe(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Add ADX indicators to the DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
        period: Period for ADX calculation
    
    Returns:
        DataFrame with ADX columns added
    """
    result = df.copy()
    adx_data = calculate_adx(df, period)
    
    for col in adx_data.columns:
        result[f'{col}_{period}'] = adx_data[col]
    
    return result