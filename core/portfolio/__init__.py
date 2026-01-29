"""
Stock Portfolio Dashboard Module
================================
This module provides functionality for tracking and analyzing a stock/ETF portfolio.

Submodules:
- storage: Local data persistence (CSV/SQLite)
- data_fetching: yfinance integration for OHLCV data
- indicators: Price returns and volume momentum calculations
- charts: Sparkline chart generation
- news: TickerTick API integration for news headlines
"""

from .storage import PortfolioStorage
from .data_fetching import fetch_price_data, refresh_all_price_data
from .indicators import compute_all_indicators
from .charts import generate_sparkline, generate_all_sparklines
from .news import fetch_ticker_news, refresh_all_news

__all__ = [
    'PortfolioStorage',
    'fetch_price_data',
    'refresh_all_price_data',
    'compute_all_indicators',
    'generate_sparkline',
    'generate_all_sparklines',
    'fetch_ticker_news',
    'refresh_all_news',
]
