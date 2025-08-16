import numpy as np
import pandas as pd
from typing import Union, List, Optional

def safe_divide(numerator: Union[float, pd.Series], denominator: Union[float, pd.Series]) -> Union[float, pd.Series]:
    """
    Safely divide two numbers or series, handling division by zero.
    
    Args:
        numerator: Numerator value(s)
        denominator: Denominator value(s)
    
    Returns:
        Division result with NaN for division by zero
    """
    if isinstance(denominator, pd.Series):
        return numerator / denominator.replace(0, np.nan)
    else:
        return numerator / denominator if denominator != 0 else np.nan

def calculate_percentage_change(current: float, previous: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        current: Current value
        previous: Previous value
    
    Returns:
        Percentage change
    """
    if previous == 0:
        return np.nan
    return ((current - previous) / previous) * 100

def normalize_to_range(data: pd.Series, min_val: float = 0, max_val: float = 1) -> pd.Series:
    """
    Normalize data to a specific range.
    
    Args:
        data: Data series to normalize
        min_val: Minimum value of target range
        max_val: Maximum value of target range
    
    Returns:
        Normalized data series
    """
    data_min = data.min()
    data_max = data.max()
    
    if data_max == data_min:
        return pd.Series([min_val] * len(data), index=data.index)
    
    normalized = (data - data_min) / (data_max - data_min)
    return normalized * (max_val - min_val) + min_val

def calculate_volatility(returns: pd.Series, window: int = 30, annualize: bool = True) -> pd.Series:
    """
    Calculate rolling volatility of returns.
    
    Args:
        returns: Return series
        window: Rolling window size
        annualize: Whether to annualize volatility
    
    Returns:
        Volatility series
    """
    vol = returns.rolling(window=window).std()
    
    if annualize:
        # Assuming daily data, annualize by multiplying by sqrt(365)
        vol = vol * np.sqrt(365)
    
    return vol

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02, window: int = 252) -> pd.Series:
    """
    Calculate rolling Sharpe ratio.
    
    Args:
        returns: Return series
        risk_free_rate: Risk-free rate (annualized)
        window: Rolling window size
    
    Returns:
        Sharpe ratio series
    """
    excess_returns = returns - (risk_free_rate / 252)  # Convert to daily
    
    mean_excess = excess_returns.rolling(window=window).mean()
    std_excess = excess_returns.rolling(window=window).std()
    
    sharpe = safe_divide(mean_excess, std_excess) * np.sqrt(252)  # Annualize
    
    return sharpe

def calculate_max_drawdown(prices: pd.Series) -> pd.Series:
    """
    Calculate rolling maximum drawdown.
    
    Args:
        prices: Price series
    
    Returns:
        Maximum drawdown series
    """
    # Calculate running maximum
    running_max = prices.expanding().max()
    
    # Calculate drawdown
    drawdown = (prices - running_max) / running_max
    
    return drawdown

def exponential_smoothing(data: pd.Series, alpha: float) -> pd.Series:
    """
    Apply exponential smoothing to data.
    
    Args:
        data: Data series
        alpha: Smoothing parameter (0 < alpha <= 1)
    
    Returns:
        Smoothed series
    """
    if not 0 < alpha <= 1:
        raise ValueError("Alpha must be between 0 and 1")
    
    return data.ewm(alpha=alpha, adjust=False).mean()

def detect_outliers(data: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
    """
    Detect outliers in data series.
    
    Args:
        data: Data series
        method: Detection method ('iqr', 'zscore')
        threshold: Threshold for outlier detection
    
    Returns:
        Boolean series indicating outliers
    """
    if method == 'iqr':
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return (data < lower_bound) | (data > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs((data - data.mean()) / data.std())
        return z_scores > threshold
    
    else:
        raise ValueError("Method must be 'iqr' or 'zscore'")

def rolling_correlation(x: pd.Series, y: pd.Series, window: int) -> pd.Series:
    """
    Calculate rolling correlation between two series.
    
    Args:
        x: First series
        y: Second series
        window: Rolling window size
    
    Returns:
        Rolling correlation series
    """
    return x.rolling(window=window).corr(y)

def calculate_beta(asset_returns: pd.Series, market_returns: pd.Series, window: int = 252) -> pd.Series:
    """
    Calculate rolling beta of an asset relative to market.
    
    Args:
        asset_returns: Asset return series
        market_returns: Market return series
        window: Rolling window size
    
    Returns:
        Beta series
    """
    # Calculate covariance and variance
    covariance = asset_returns.rolling(window=window).cov(market_returns)
    market_variance = market_returns.rolling(window=window).var()
    
    beta = safe_divide(covariance, market_variance)
    
    return beta

def smooth_series(data: pd.Series, method: str = 'sma', window: int = 5) -> pd.Series:
    """
    Smooth a data series using various methods.
    
    Args:
        data: Data series to smooth
        method: Smoothing method ('sma', 'ema', 'median')
        window: Window size for smoothing
    
    Returns:
        Smoothed series
    """
    if method == 'sma':
        return data.rolling(window=window).mean()
    elif method == 'ema':
        return data.ewm(span=window, adjust=False).mean()
    elif method == 'median':
        return data.rolling(window=window).median()
    else:
        raise ValueError("Method must be 'sma', 'ema', or 'median'")

def calculate_information_ratio(portfolio_returns: pd.Series, benchmark_returns: pd.Series, window: int = 252) -> pd.Series:
    """
    Calculate rolling information ratio.
    
    Args:
        portfolio_returns: Portfolio return series
        benchmark_returns: Benchmark return series
        window: Rolling window size
    
    Returns:
        Information ratio series
    """
    excess_returns = portfolio_returns - benchmark_returns
    tracking_error = excess_returns.rolling(window=window).std()
    
    # Annualize tracking error
    tracking_error_annual = tracking_error * np.sqrt(252)
    
    # Calculate average excess return
    avg_excess_return = excess_returns.rolling(window=window).mean() * 252
    
    information_ratio = safe_divide(avg_excess_return, tracking_error_annual)
    
    return information_ratio