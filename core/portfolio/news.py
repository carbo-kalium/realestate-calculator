"""
News Module for Stock Portfolio Dashboard
=========================================
Fetches ticker-specific news headlines using the TickerTick API.

API Documentation: https://github.com/hczhu/TickerTick-API
Public API endpoint: https://api.tickertick.com/feed

Usage:
    from core.portfolio import fetch_ticker_news, refresh_all_news
    
    # Fetch news for single ticker
    headlines = fetch_ticker_news('AAPL', storage)
    
    # Refresh all news (run nightly)
    refresh_all_news(storage)
"""

import requests
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

TICKERTICK_API_URL = "https://api.tickertick.com/feed"


def fetch_ticker_news(ticker: str, storage, 
                      num_headlines: int = 5,
                      use_cache: bool = True,
                      cache_max_age_hours: float = 12) -> List[Dict[str, str]]:
    """
    Fetch news headlines for a ticker using TickerTick API.
    
    Note: TickerTick API has rate limit of 10 requests per minute per IP.
    Use with delays between requests in batch operations.
    
    Args:
        ticker: Stock/ETF symbol (e.g., 'AAPL')
        storage: PortfolioStorage instance
        num_headlines: Maximum number of headlines to return (default: 5)
        use_cache: If True, use cached news if available and fresh
        cache_max_age_hours: Maximum age of cache in hours before refresh
    
    Returns:
        List of dictionaries with keys: title, source, url, published
        Returns empty list if fetch fails.
    """
    ticker = ticker.upper().strip()
    
    if use_cache:
        cache_age = storage.get_news_cache_age(ticker)
        if cache_age is not None and cache_age < cache_max_age_hours:
            cached_news = storage.load_news(ticker)
            if cached_news:
                logger.info(f"Using cached news for {ticker} (age: {cache_age:.1f}h)")
                return cached_news[:num_headlines]
    
    try:
        params = {
            'q': f'tt:{ticker}',
            'n': num_headlines * 2
        }
        
        response = requests.get(
            TICKERTICK_API_URL,
            params=params,
            timeout=10,
            headers={'User-Agent': 'StockPortfolioDashboard/1.0'}
        )
        
        if response.status_code != 200:
            logger.warning(f"TickerTick API returned {response.status_code} for {ticker}")
            return _get_fallback_news(ticker, storage, num_headlines)
        
        data = response.json()
        stories = data.get('stories', [])
        
        headlines = []
        for story in stories[:num_headlines]:
            headline = {
                'title': story.get('title', 'No title'),
                'source': story.get('site', 'Unknown'),
                'url': story.get('url', ''),
                'published': _format_timestamp(story.get('time', 0))
            }
            headlines.append(headline)
        
        if headlines:
            storage.save_news(ticker, headlines)
            storage.log_refresh('news', ticker, 'success')
            logger.info(f"Fetched {len(headlines)} headlines for {ticker}")
        
        return headlines
        
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout fetching news for {ticker}")
        return _get_fallback_news(ticker, storage, num_headlines)
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching news for {ticker}: {e}")
        return _get_fallback_news(ticker, storage, num_headlines)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for {ticker}: {e}")
        return _get_fallback_news(ticker, storage, num_headlines)
    except Exception as e:
        logger.error(f"Unexpected error fetching news for {ticker}: {e}")
        return _get_fallback_news(ticker, storage, num_headlines)


def _get_fallback_news(ticker: str, storage, num_headlines: int) -> List[Dict[str, str]]:
    """Return cached news as fallback if API fails."""
    cached_news = storage.load_news(ticker)
    if cached_news:
        logger.info(f"Using stale cache for {ticker} news (API failed)")
        return cached_news[:num_headlines]
    return []


def _format_timestamp(timestamp: int) -> str:
    """
    Format Unix timestamp to human-readable date.
    
    Args:
        timestamp: Unix timestamp in seconds
    
    Returns:
        Formatted date string (e.g., 'Jan 15, 2024')
    """
    if not timestamp:
        return 'Unknown date'
    try:
        dt = datetime.fromtimestamp(timestamp / 1000)
        return dt.strftime('%b %d, %Y')
    except (ValueError, OSError):
        return 'Unknown date'


def refresh_all_news(storage, force: bool = False,
                     cache_max_age_hours: float = 12) -> Dict[str, str]:
    """
    Refresh news for all tickers in the portfolio.
    
    This function is designed to be run as a batch job.
    
    RATE LIMITING: TickerTick API allows 10 requests per minute per IP.
    This function adds 6-second delays between requests to stay under the limit
    (10 requests in 60 seconds = 1 request every 6 seconds).
    
    Args:
        storage: PortfolioStorage instance
        force: If True, refresh even if cache is recent
        cache_max_age_hours: Maximum age of cache before refresh
    
    Returns:
        Dictionary mapping ticker to status ('success', 'failed', 'skipped')
    """
    import time
    
    results = {}
    tickers_df = storage.get_all_tickers()
    
    if tickers_df.empty:
        logger.info("No tickers in portfolio")
        return results
    
    request_count = 0
    start_time = time.time()
    
    for ticker in tickers_df['ticker'].tolist():
        if not force:
            cache_age = storage.get_news_cache_age(ticker)
            if cache_age is not None and cache_age < cache_max_age_hours:
                results[ticker] = 'skipped'
                continue
        
        try:
            # Rate limiting: wait 6 seconds between requests (10 requests/minute max)
            if request_count > 0:
                time.sleep(6)
            
            headlines = fetch_ticker_news(
                ticker, storage,
                num_headlines=5,
                use_cache=False,
                cache_max_age_hours=0
            )
            
            results[ticker] = 'success' if headlines else 'failed'
            request_count += 1
            
        except Exception as e:
            logger.error(f"Error refreshing news for {ticker}: {e}")
            results[ticker] = 'failed'
    
    success_count = sum(1 for v in results.values() if v == 'success')
    storage.log_refresh('news_batch', None, 'success',
                        f"Refreshed news for {success_count} tickers")
    
    return results


def format_news_for_display(headlines: List[Dict[str, str]], 
                            max_title_length: int = 80) -> str:
    """
    Format news headlines for dashboard display.
    
    Args:
        headlines: List of headline dictionaries
        max_title_length: Maximum characters for title before truncation
    
    Returns:
        Formatted HTML string for display
    """
    if not headlines:
        return '<span style="color: gray; font-size: 0.9em;">No recent news</span>'
    
    html_parts = []
    for h in headlines[:3]:
        title = h.get('title', 'No title')
        if len(title) > max_title_length:
            title = title[:max_title_length-3] + '...'
        
        source = h.get('source', '')
        url = h.get('url', '')
        
        if url:
            html_parts.append(
                f'<div style="margin-bottom: 4px; font-size: 0.85em;">'
                f'<a href="{url}" target="_blank" style="color: #1f77b4; text-decoration: none;">{title}</a>'
                f'<span style="color: gray; font-size: 0.9em;"> — {source}</span>'
                f'</div>'
            )
        else:
            html_parts.append(
                f'<div style="margin-bottom: 4px; font-size: 0.85em;">'
                f'{title}'
                f'<span style="color: gray; font-size: 0.9em;"> — {source}</span>'
                f'</div>'
            )
    
    return ''.join(html_parts)


def get_news_summary(ticker: str, storage, num_headlines: int = 3) -> List[str]:
    """
    Get simplified news summary for a ticker.
    
    Args:
        ticker: Stock/ETF symbol
        storage: PortfolioStorage instance
        num_headlines: Number of headlines to return
    
    Returns:
        List of formatted strings: "Title (Source)"
    """
    headlines = storage.load_news(ticker) or []
    
    summaries = []
    for h in headlines[:num_headlines]:
        title = h.get('title', 'No title')
        source = h.get('source', '')
        if len(title) > 60:
            title = title[:57] + '...'
        summaries.append(f"{title} ({source})")
    
    return summaries
