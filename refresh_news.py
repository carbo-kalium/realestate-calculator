#!/usr/bin/env python3
"""
News Refresh Script for Stock Portfolio Dashboard
=================================================

This script is designed to be run 3 times daily to keep news headlines fresh:
1. After market close (6:30 PM EST) - After price data refresh
2. Before market open (6:00 AM EST) - Morning update
3. During market hours (1:00 PM EST) - Afternoon update

This is separate from the main data refresh to allow more frequent news updates.

Usage:
    python refresh_news.py

Scheduling with Cron (3x daily):
    # After market close (6:30 PM EST = 11:30 PM UTC)
    30 23 * * 1-5 cd /path/to/realestate && python refresh_news.py >> /var/log/portfolio_news.log 2>&1
    
    # Before market open (6:00 AM EST = 11:00 AM UTC)
    0 11 * * 1-5 cd /path/to/realestate && python refresh_news.py >> /var/log/portfolio_news.log 2>&1
    
    # During market hours (1:00 PM EST = 6:00 PM UTC)
    0 18 * * 1-5 cd /path/to/realestate && python refresh_news.py >> /var/log/portfolio_news.log 2>&1

RATE LIMITING:
    TickerTick API allows 10 requests per minute per IP.
    This script adds 6-second delays between requests to stay within limits.
    For a portfolio of 10 tickers, this takes ~60 seconds.
"""

import sys
import logging
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.portfolio.storage import PortfolioStorage
from core.portfolio.news import fetch_ticker_news

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def refresh_news():
    """
    Refresh news headlines for all tickers in the portfolio.
    
    Respects TickerTick API rate limit of 10 requests per minute.
    """
    start_time = datetime.now()
    logger.info(f"Starting news refresh at {start_time.isoformat()}")
    
    storage = PortfolioStorage()
    
    tickers_df = storage.get_all_tickers()
    
    if tickers_df.empty:
        logger.warning("No tickers in portfolio. Nothing to refresh.")
        return
    
    ticker_list = tickers_df['ticker'].tolist()
    logger.info(f"Refreshing news for {len(ticker_list)} tickers: {ticker_list}")
    
    results = {'success': 0, 'failed': 0, 'total': len(ticker_list)}
    
    for i, ticker in enumerate(ticker_list):
        try:
            # Rate limiting: 6 seconds between requests (10 req/min max)
            if i > 0:
                logger.info(f"  Rate limit: waiting 6 seconds before next request...")
                time.sleep(6)
            
            logger.info(f"  [{i+1}/{len(ticker_list)}] Fetching news for {ticker}...")
            
            headlines = fetch_ticker_news(
                ticker, 
                storage, 
                num_headlines=5,
                use_cache=False,
                cache_max_age_hours=0
            )
            
            if headlines:
                logger.info(f"  {ticker}: ✅ Success - fetched {len(headlines)} headlines")
                results['success'] += 1
            else:
                logger.warning(f"  {ticker}: ⚠️ No headlines found")
                results['failed'] += 1
                
        except Exception as e:
            logger.error(f"  {ticker}: ❌ Failed - {e}")
            results['failed'] += 1
    
    storage.log_refresh('news_batch', None, 'success',
                        f"Refreshed {results['success']}/{results['total']} tickers")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("=" * 50)
    logger.info("NEWS REFRESH COMPLETE")
    logger.info("=" * 50)
    logger.info(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    logger.info(f"Tickers processed: {results['total']}")
    logger.info(f"Success: {results['success']}")
    logger.info(f"Failed: {results['failed']}")
    logger.info(f"Success rate: {results['success']/results['total']*100:.1f}%")


if __name__ == '__main__':
    try:
        refresh_news()
    except Exception as e:
        logger.error(f"News refresh failed with error: {e}")
        sys.exit(1)
