"""
Charts Module for Stock Portfolio Dashboard
===========================================
Generates sparkline images for price history visualization.

Each sparkline is a small PNG (300x80) showing 1-year price history.
Images are stored locally and reused in the dashboard.

Usage:
    from core.portfolio import generate_sparkline, generate_all_sparklines
    
    # Generate single sparkline
    generate_sparkline('AAPL', storage)
    
    # Generate all sparklines
    generate_all_sparklines(storage)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def generate_sparkline(ticker: str, storage, 
                       width: int = 300, height: int = 80,
                       color: str = '#1f77b4', 
                       positive_color: str = '#00a86b',
                       negative_color: str = '#dc3545') -> Optional[Path]:
    """
    Generate a sparkline PNG image for a ticker's 1-year price history.
    
    The sparkline color is determined by the overall return:
    - Green if price is higher than 1 year ago
    - Red if price is lower than 1 year ago
    
    Args:
        ticker: Stock/ETF symbol
        storage: PortfolioStorage instance
        width: Image width in pixels
        height: Image height in pixels
        color: Default line color (hex)
        positive_color: Color for positive returns (hex)
        negative_color: Color for negative returns (hex)
    
    Returns:
        Path to generated image or None if generation fails
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        ticker = ticker.upper().strip()
        df = storage.load_price_data(ticker)
        
        if df is None or df.empty:
            logger.warning(f"No price data for {ticker}")
            return None
        
        price_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
        prices = df[price_col].dropna()
        
        if len(prices) < 10:
            logger.warning(f"Insufficient data for {ticker} sparkline")
            return None
        
        first_price = prices.iloc[0]
        last_price = prices.iloc[-1]
        line_color = positive_color if last_price >= first_price else negative_color
        
        dpi = 100
        fig_width = width / dpi
        fig_height = height / dpi
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
        
        ax.plot(range(len(prices)), prices.values, 
                color=line_color, linewidth=1.5, antialiased=True)
        
        ax.fill_between(range(len(prices)), prices.values, 
                        alpha=0.1, color=line_color)
        
        ax.axis('off')
        ax.set_xlim(0, len(prices) - 1)
        
        y_min, y_max = prices.min(), prices.max()
        y_padding = (y_max - y_min) * 0.1
        ax.set_ylim(y_min - y_padding, y_max + y_padding)
        
        plt.tight_layout(pad=0)
        
        output_path = storage.get_sparkline_path(ticker)
        fig.savefig(output_path, format='png', 
                    bbox_inches='tight', pad_inches=0,
                    transparent=True, dpi=dpi)
        plt.close(fig)
        
        logger.info(f"Generated sparkline for {ticker}")
        return output_path
        
    except ImportError:
        logger.error("matplotlib is required for sparkline generation")
        return None
    except Exception as e:
        logger.error(f"Error generating sparkline for {ticker}: {e}")
        return None


def generate_all_sparklines(storage, force: bool = False) -> dict:
    """
    Generate sparklines for all tickers in the portfolio.
    
    Args:
        storage: PortfolioStorage instance
        force: If True, regenerate even if sparkline exists
    
    Returns:
        Dictionary mapping ticker to status ('success', 'failed', 'skipped')
    """
    results = {}
    tickers_df = storage.get_all_tickers()
    
    if tickers_df.empty:
        logger.info("No tickers in portfolio")
        return results
    
    for ticker in tickers_df['ticker'].tolist():
        if not force and storage.sparkline_exists(ticker):
            results[ticker] = 'skipped'
            continue
        
        try:
            path = generate_sparkline(ticker, storage)
            results[ticker] = 'success' if path else 'failed'
        except Exception as e:
            logger.error(f"Error generating sparkline for {ticker}: {e}")
            results[ticker] = 'failed'
    
    storage.log_refresh('sparklines', None, 'success',
                        f"Generated {sum(1 for v in results.values() if v == 'success')} sparklines")
    
    return results


def get_sparkline_base64(ticker: str, storage) -> Optional[str]:
    """
    Get sparkline image as base64-encoded string for embedding in HTML.
    
    Args:
        ticker: Stock/ETF symbol
        storage: PortfolioStorage instance
    
    Returns:
        Base64-encoded PNG string or None
    """
    import base64
    
    ticker = ticker.upper().strip()
    sparkline_path = storage.get_sparkline_path(ticker)
    
    if not sparkline_path.exists():
        path = generate_sparkline(ticker, storage)
        if not path:
            return None
    
    try:
        with open(sparkline_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error reading sparkline for {ticker}: {e}")
        return None


def create_sparkline_html(ticker: str, storage) -> str:
    """
    Create HTML img tag for sparkline.
    
    Args:
        ticker: Stock/ETF symbol
        storage: PortfolioStorage instance
    
    Returns:
        HTML string with embedded base64 image
    """
    base64_img = get_sparkline_base64(ticker, storage)
    
    if base64_img:
        return f'<img src="data:image/png;base64,{base64_img}" alt="{ticker} sparkline" style="height: 40px;">'
    return '<span style="color: gray;">No chart</span>'
