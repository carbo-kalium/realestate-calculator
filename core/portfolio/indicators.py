"""
Indicators Module for Stock Portfolio Dashboard
===============================================
Computes price returns and volume momentum metrics from daily OHLCV data.

All calculations use Adjusted Close prices where available.

Usage:
    from core.portfolio import compute_all_indicators
    
    indicators_df = compute_all_indicators(storage)
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def compute_returns(df: pd.DataFrame, column: str = 'Adj Close') -> Dict[str, float]:
    """
    Compute price returns over various periods.
    
    Args:
        df: DataFrame with OHLCV data (index should be DatetimeIndex)
        column: Column to use for price ('Adj Close' or 'Close')
    
    Returns:
        Dictionary with returns for each period:
        - return_1d: 1-day return
        - return_5d: 5-day return
        - return_2w: 2-week (10 trading days) return
        - return_1m: 1-month (21 trading days) return
        - return_3m: 3-month (63 trading days) return
        - return_6m: 6-month (126 trading days) return
        - return_1y: 1-year (252 trading days) return
    """
    if df is None or df.empty:
        return {
            'return_1d': None, 'return_5d': None, 'return_2w': None,
            'return_1m': None, 'return_3m': None, 'return_6m': None,
            'return_1y': None
        }
    
    if column not in df.columns:
        column = 'Close' if 'Close' in df.columns else df.columns[0]
    
    prices = df[column].dropna()
    if len(prices) < 2:
        return {
            'return_1d': None, 'return_5d': None, 'return_2w': None,
            'return_1m': None, 'return_3m': None, 'return_6m': None,
            'return_1y': None
        }
    
    current_price = prices.iloc[-1]
    
    periods = {
        'return_1d': 1,
        'return_5d': 5,
        'return_2w': 10,
        'return_1m': 21,
        'return_3m': 63,
        'return_6m': 126,
        'return_1y': 252
    }
    
    returns = {}
    for name, days in periods.items():
        if len(prices) > days:
            past_price = prices.iloc[-days - 1]
            returns[name] = ((current_price - past_price) / past_price) * 100
        else:
            returns[name] = None
    
    return returns


def compute_volume_momentum(df: pd.DataFrame) -> Optional[float]:
    """
    Compute volume momentum metric.
    
    Volume momentum = 20-day avg volume / 60-day avg volume
    
    A ratio > 1 indicates increasing volume (bullish momentum)
    A ratio < 1 indicates decreasing volume
    
    Args:
        df: DataFrame with OHLCV data including 'Volume' column
    
    Returns:
        Volume momentum ratio or None if insufficient data
    """
    if df is None or df.empty or 'Volume' not in df.columns:
        return None
    
    volumes = df['Volume'].dropna()
    
    if len(volumes) < 60:
        return None
    
    avg_20d = volumes.iloc[-20:].mean()
    avg_60d = volumes.iloc[-60:].mean()
    
    if avg_60d == 0:
        return None
    
    return avg_20d / avg_60d


def compute_ticker_indicators(ticker: str, storage) -> Dict[str, Any]:
    """
    Compute all indicators for a single ticker.
    
    Args:
        ticker: Stock/ETF symbol
        storage: PortfolioStorage instance
    
    Returns:
        Dictionary with all computed indicators
    """
    ticker = ticker.upper().strip()
    df = storage.load_price_data(ticker)
    
    returns = compute_returns(df)
    volume_momentum = compute_volume_momentum(df)
    
    last_close = None
    last_date = None
    if df is not None and not df.empty:
        if 'Adj Close' in df.columns:
            last_close = df['Adj Close'].iloc[-1]
        elif 'Close' in df.columns:
            last_close = df['Close'].iloc[-1]
        last_date = df.index[-1].strftime('%Y-%m-%d')
    
    return {
        'ticker': ticker,
        'last_close': last_close,
        'last_date': last_date,
        'volume_momentum': volume_momentum,
        **returns
    }


def compute_all_indicators(storage, save: bool = True) -> pd.DataFrame:
    """
    Compute indicators for all tickers in the portfolio.
    
    Args:
        storage: PortfolioStorage instance
        save: If True, save results to storage
    
    Returns:
        DataFrame with all indicators for all tickers
    """
    tickers_df = storage.get_all_tickers()
    
    if tickers_df.empty:
        logger.info("No tickers in portfolio")
        return pd.DataFrame()
    
    indicators_list = []
    
    for _, row in tickers_df.iterrows():
        ticker = row['ticker']
        try:
            indicators = compute_ticker_indicators(ticker, storage)
            indicators['asset_type'] = row['asset_type']
            indicators['description'] = row['description']
            indicators['exposure_tags'] = row['exposure_tags']
            indicators_list.append(indicators)
            logger.info(f"Computed indicators for {ticker}")
        except Exception as e:
            logger.error(f"Error computing indicators for {ticker}: {e}")
            indicators_list.append({
                'ticker': ticker,
                'asset_type': row['asset_type'],
                'description': row['description'],
                'exposure_tags': row['exposure_tags'],
                'last_close': None,
                'last_date': None,
                'volume_momentum': None,
                'return_1d': None,
                'return_5d': None,
                'return_2w': None,
                'return_1m': None,
                'return_3m': None,
                'return_6m': None,
                'return_1y': None
            })
    
    df = pd.DataFrame(indicators_list)
    
    column_order = [
        'ticker', 'asset_type', 'description', 'exposure_tags',
        'last_close', 'last_date',
        'return_1d', 'return_5d', 'return_2w', 'return_1m', 
        'return_3m', 'return_6m', 'return_1y',
        'volume_momentum'
    ]
    df = df[[c for c in column_order if c in df.columns]]
    
    if save and not df.empty:
        storage.save_indicators(df)
        storage.log_refresh('indicators', None, 'success', 
                            f"Computed indicators for {len(df)} tickers")
    
    return df


def format_return(value: Optional[float], precision: int = 2) -> str:
    """
    Format a return value as a percentage string with color indicator.
    
    Args:
        value: Return percentage (e.g., 5.25 for 5.25%)
        precision: Decimal places
    
    Returns:
        Formatted string (e.g., "+5.25%" or "-2.10%")
    """
    if value is None:
        return "N/A"
    
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.{precision}f}%"


def format_volume_momentum(value: Optional[float]) -> str:
    """
    Format volume momentum ratio.
    
    Args:
        value: Volume momentum ratio
    
    Returns:
        Formatted string (e.g., "1.25x")
    """
    if value is None:
        return "N/A"
    return f"{value:.2f}x"
