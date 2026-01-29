#!/usr/bin/env python3
"""
Nightly Data Refresh Script for Stock Portfolio Dashboard
=========================================================

This script is designed to be run as a scheduled job (cron, Railway, GitHub Actions)
after market close to refresh all portfolio data.

Usage:
    python refresh_data.py [--force]

Options:
    --force    Force refresh even if cache is recent

Scheduling Examples:

1. Cron (Linux/Mac) - Run at 6:30 PM EST on weekdays:
   30 18 * * 1-5 cd /path/to/realestate && python refresh_data.py >> /var/log/portfolio_refresh.log 2>&1

2. Railway - Create a scheduled job with cron expression:
   30 23 * * 1-5  (11:30 PM UTC = 6:30 PM EST)

3. GitHub Actions - Add workflow file .github/workflows/refresh.yml
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.portfolio.storage import PortfolioStorage
from core.portfolio.data_fetching import fetch_price_data
from core.portfolio.indicators import compute_all_indicators
from core.portfolio.charts import generate_all_sparklines
from core.portfolio.news import fetch_ticker_news

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def refresh_all_data(force: bool = False):
    """
    Refresh all portfolio data: prices, indicators, charts, and news.
    
    Args:
        force: If True, refresh even if cache is recent
    """
    start_time = datetime.now()
    logger.info(f"Starting data refresh at {start_time.isoformat()}")
    
    storage = PortfolioStorage()
    
    tickers_df = storage.get_all_tickers()
    
    if tickers_df.empty:
        logger.warning("No tickers in portfolio. Nothing to refresh.")
        return
    
    ticker_list = tickers_df['ticker'].tolist()
    logger.info(f"Found {len(ticker_list)} tickers to refresh: {ticker_list}")
    
    logger.info("=" * 50)
    logger.info("STEP 1/4: Fetching price data from Yahoo Finance")
    logger.info("=" * 50)
    
    price_results = {'success': 0, 'failed': 0, 'skipped': 0}
    
    for ticker in ticker_list:
        try:
            cache_age = storage.get_price_cache_age(ticker)
            
            if not force and cache_age is not None and cache_age < 12:
                logger.info(f"  {ticker}: Skipped (cache age: {cache_age:.1f}h)")
                price_results['skipped'] += 1
                continue
            
            df = fetch_price_data(ticker, period='2y')
            
            if df is not None and not df.empty:
                storage.save_price_data(ticker, df)
                logger.info(f"  {ticker}: Success ({len(df)} rows)")
                price_results['success'] += 1
            else:
                logger.warning(f"  {ticker}: Failed (no data)")
                price_results['failed'] += 1
                
        except Exception as e:
            logger.error(f"  {ticker}: Failed ({e})")
            price_results['failed'] += 1
    
    storage.log_refresh('price_data_batch', None, 'success', 
                        f"Success: {price_results['success']}, Failed: {price_results['failed']}")
    
    logger.info(f"Price refresh complete: {price_results}")
    
    logger.info("=" * 50)
    logger.info("STEP 2/4: Computing indicators")
    logger.info("=" * 50)
    
    try:
        indicators_df = compute_all_indicators(storage, save=True)
        logger.info(f"Computed indicators for {len(indicators_df)} tickers")
    except Exception as e:
        logger.error(f"Failed to compute indicators: {e}")
    
    logger.info("=" * 50)
    logger.info("STEP 3/4: Generating sparkline charts")
    logger.info("=" * 50)
    
    try:
        chart_results = generate_all_sparklines(storage, force=force)
        success = sum(1 for v in chart_results.values() if v == 'success')
        logger.info(f"Generated {success} sparklines")
    except Exception as e:
        logger.error(f"Failed to generate sparklines: {e}")
    
    logger.info("=" * 50)
    logger.info("NOTE: News refresh is separate. Use refresh_news.py for 3x daily news updates.")
    logger.info("Skipping news refresh in this script to respect API rate limits.")
    
    # News is now handled by separate refresh_news.py script (3x daily)
    # This avoids rate limiting issues and allows more frequent news updates
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("=" * 50)
    logger.info("REFRESH COMPLETE")
    logger.info("=" * 50)
    logger.info(f"Duration: {duration:.1f} seconds")
    logger.info(f"Tickers processed: {len(ticker_list)}")
    logger.info(f"Price data: {price_results}")
    logger.info(f"News: {news_results}")
    
    storage.log_refresh('full_refresh', None, 'success',
                        f"Completed in {duration:.1f}s for {len(ticker_list)} tickers")


if __name__ == '__main__':
    force_refresh = '--force' in sys.argv
    
    if force_refresh:
        logger.info("Force refresh enabled - ignoring cache age")
    
    try:
        refresh_all_data(force=force_refresh)
    except Exception as e:
        logger.error(f"Refresh failed with error: {e}")
        sys.exit(1)
