from datetime import datetime, timedelta, timezone
import pandas as pd
from typing import Union, Optional

def parse_date_string(date_str: str) -> datetime:
    """
    Parse various date string formats to datetime object.
    
    Args:
        date_str: Date string in various formats
    
    Returns:
        Parsed datetime object
    """
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%d/%m/%Y',
        '%m/%d/%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date string: {date_str}")

def get_date_range(
    end_date: Optional[datetime] = None,
    days_back: int = 30
) -> tuple[datetime, datetime]:
    """
    Get start and end dates for a given number of days back.
    
    Args:
        end_date: End date (default: now)
        days_back: Number of days to go back
    
    Returns:
        Tuple of (start_date, end_date)
    """
    if end_date is None:
        end_date = datetime.now(timezone.utc)
    
    start_date = end_date - timedelta(days=days_back)
    
    return start_date, end_date

def round_to_timeframe(dt: datetime, timeframe: str) -> datetime:
    """
    Round datetime to the nearest timeframe boundary.
    
    Args:
        dt: Datetime to round
        timeframe: Timeframe ('1h', '4h', '1d')
    
    Returns:
        Rounded datetime
    """
    if timeframe == '1h':
        return dt.replace(minute=0, second=0, microsecond=0)
    elif timeframe == '4h':
        hour = (dt.hour // 4) * 4
        return dt.replace(hour=hour, minute=0, second=0, microsecond=0)
    elif timeframe == '1d':
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        return dt

def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    """
    Validate that date range is logical.
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        True if valid, False otherwise
    """
    return start_date < end_date and end_date <= datetime.now(timezone.utc)

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable format.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def get_market_hours_filter(df: pd.DataFrame, market_hours_only: bool = False) -> pd.DataFrame:
    """
    Filter DataFrame to market hours only (if requested).
    
    Args:
        df: DataFrame with datetime index
        market_hours_only: Whether to filter to market hours
    
    Returns:
        Filtered DataFrame
    """
    if not market_hours_only:
        return df
    
    # Crypto markets are 24/7, but traditional market hours are 9:30 AM to 4:00 PM EST
    # This can be useful for comparison with traditional assets
    market_start = 9.5  # 9:30 AM
    market_end = 16.0   # 4:00 PM
    
    # Convert index to EST and filter
    df_est = df.copy()
    df_est.index = df_est.index.tz_convert('US/Eastern')
    
    # Filter to market hours
    hour_filter = (df_est.index.hour >= market_start) & (df_est.index.hour < market_end)
    weekday_filter = df_est.index.weekday < 5  # Monday=0, Friday=4
    
    return df_est[hour_filter & weekday_filter]

def resample_ohlcv(df: pd.DataFrame, target_freq: str) -> pd.DataFrame:
    """
    Resample OHLCV data to different timeframe.
    
    Args:
        df: DataFrame with OHLCV data
        target_freq: Target frequency ('1H', '4H', '1D', etc.)
    
    Returns:
        Resampled DataFrame
    """
    if df.empty:
        return df
    
    # Define aggregation rules
    agg_rules = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }
    
    # Only resample OHLCV columns
    ohlcv_cols = [col for col in ['open', 'high', 'low', 'close', 'volume'] if col in df.columns]
    
    if not ohlcv_cols:
        return df
    
    # Resample OHLCV data
    resampled = df[ohlcv_cols].resample(target_freq).agg(agg_rules)
    
    # Handle other columns (indicators) by taking the last value
    other_cols = [col for col in df.columns if col not in ohlcv_cols]
    if other_cols:
        other_resampled = df[other_cols].resample(target_freq).last()
        resampled = pd.concat([resampled, other_resampled], axis=1)
    
    # Drop rows with NaN values
    resampled.dropna(inplace=True)
    
    return resampled