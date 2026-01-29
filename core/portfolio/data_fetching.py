"""
Data Fetching Module for Stock Portfolio Dashboard
=================================================
Handles fetching OHLCV data from yfinance.

Design: Batch-style fetching meant to run AFTER market close.
Not intended for real-time fetching on page load.

Usage:
    # Fetch single ticker
    df = fetch_price_data('AAPL', period='1y')
    
    # Refresh all tickers (run nightly after market close)
    refresh_all_price_data(storage)

NIGHTLY REFRESH INSTRUCTIONS:
-----------------------------
To set up automated nightly refresh, create a cron job or scheduled task:

1. Create a refresh script (e.g., refresh_data.py):
    ```python
    from core.portfolio import PortfolioStorage, refresh_all_price_data
    
    storage = PortfolioStorage()
    refresh_all_price_data(storage)
    ```

2. Schedule via cron (Linux/Mac) to run at 6 PM EST after market close:
    0 18 * * 1-5 cd /path/to/realestate && python refresh_data.py

3. Or use Railway's scheduled jobs feature for cloud deployment.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def fetch_price_data(ticker: str, period: str = '2y', 
                     interval: str = '1d') -> Optional[pd.DataFrame]:
    """
    Fetch OHLCV data for a single ticker using yfinance.
    
    Note: Fetches 2 years of data by default to ensure 1Y returns can be calculated.
    
    Args:
        ticker: Stock/ETF symbol (e.g., 'AAPL')
        period: Data period ('2y', '5y', 'max') - default 2y for 1Y return calculation
        interval: Data interval ('1d', '1wk', '1mo')
    
    Returns:
        DataFrame with columns: Open, High, Low, Close, Adj Close, Volume
        Returns None if fetch fails.
    """
    try:
        import yfinance as yf
        
        ticker = ticker.upper().strip()
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        
        if df.empty:
            logger.warning(f"No data returned for {ticker}")
            return None
        
        df.index = pd.to_datetime(df.index)
        df.index = df.index.tz_localize(None)
        
        if 'Adj Close' not in df.columns and 'Close' in df.columns:
            df['Adj Close'] = df['Close']
        
        logger.info(f"Fetched {len(df)} rows for {ticker}")
        return df
        
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return None


def fetch_ticker_info(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch basic info for a ticker.
    
    Args:
        ticker: Stock/ETF symbol
    
    Returns:
        Dictionary with ticker info or None if fetch fails.
    """
    try:
        import yfinance as yf
        
        ticker = ticker.upper().strip()
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            'name': info.get('shortName', info.get('longName', ticker)),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 0),
            'quote_type': info.get('quoteType', 'Unknown')
        }
        
    except Exception as e:
        logger.error(f"Error fetching info for {ticker}: {e}")
        return None


def refresh_all_price_data(storage, force: bool = False) -> Dict[str, str]:
    """
    Refresh price data for all tickers in the portfolio.
    
    This function is designed to be run as a batch job after market close.
    It fetches 2 years of daily OHLCV data for each ticker (for 1Y return calculation).
    
    Args:
        storage: PortfolioStorage instance
        force: If True, refresh even if cache is recent
    
    Returns:
        Dictionary mapping ticker to status ('success', 'failed', 'skipped')
    """
    results = {}
    tickers_df = storage.get_all_tickers()
    
    if tickers_df.empty:
        logger.info("No tickers in portfolio to refresh")
        return results
    
    for ticker in tickers_df['ticker'].tolist():
        cache_age = storage.get_price_cache_age(ticker)
        
        if not force and cache_age is not None and cache_age < 12:
            logger.info(f"Skipping {ticker} - cache is only {cache_age:.1f} hours old")
            results[ticker] = 'skipped'
            continue
        
        try:
            df = fetch_price_data(ticker, period='2y')
            
            if df is not None and not df.empty:
                storage.save_price_data(ticker, df)
                storage.log_refresh('price_data', ticker, 'success')
                results[ticker] = 'success'
                logger.info(f"Successfully refreshed {ticker}")
            else:
                storage.log_refresh('price_data', ticker, 'failed', 'No data returned')
                results[ticker] = 'failed'
                
        except Exception as e:
            storage.log_refresh('price_data', ticker, 'failed', str(e))
            results[ticker] = 'failed'
            logger.error(f"Failed to refresh {ticker}: {e}")
    
    storage.log_refresh('price_data_batch', None, 'success', 
                        f"Refreshed {sum(1 for v in results.values() if v == 'success')} tickers")
    
    return results


def validate_ticker(ticker: str) -> bool:
    """
    Validate that a ticker symbol exists and has data.
    
    Args:
        ticker: Stock/ETF symbol to validate
    
    Returns:
        True if ticker is valid and has data
    """
    try:
        import yfinance as yf
        
        ticker = ticker.upper().strip()
        stock = yf.Ticker(ticker)
        hist = stock.history(period='5d')
        
        return not hist.empty
        
    except Exception:
        return False


def get_latest_price(ticker: str, storage) -> Optional[float]:
    """
    Get the latest closing price for a ticker from cache.
    
    Args:
        ticker: Stock/ETF symbol
        storage: PortfolioStorage instance
    
    Returns:
        Latest adjusted close price or None
    """
    df = storage.load_price_data(ticker)
    if df is not None and not df.empty:
        if 'Adj Close' in df.columns:
            return float(df['Adj Close'].iloc[-1])
        elif 'Close' in df.columns:
            return float(df['Close'].iloc[-1])
    return None
