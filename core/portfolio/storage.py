"""
Storage Module for Stock Portfolio Dashboard
============================================
Handles local data persistence using SQLite for portfolio metadata
and CSV for cached price/indicator data.

Usage:
    storage = PortfolioStorage()
    storage.add_ticker('AAPL', 'Stock', 'Apple Inc.', 'Tech, AI')
    tickers = storage.get_all_tickers()
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import csv


class PortfolioStorage:
    """Manages portfolio data storage using SQLite and CSV files."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize storage with data directory.
        
        Args:
            data_dir: Directory for storing data files. Defaults to ./data/portfolio/
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            if data_dir is None:
                data_dir = Path(__file__).parent.parent.parent / 'data' / 'portfolio'
            
            self.data_dir = Path(data_dir)
            logger.info(f"Creating data directory: {self.data_dir}")
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            self.db_path = self.data_dir / 'portfolio.db'
            self.price_cache_dir = self.data_dir / 'price_cache'
            self.sparkline_dir = self.data_dir / 'sparklines'
            self.news_cache_dir = self.data_dir / 'news_cache'
            self.indicators_path = self.data_dir / 'indicators.csv'
            
            logger.info(f"Creating subdirectories in {self.data_dir}")
            self.price_cache_dir.mkdir(exist_ok=True)
            self.sparkline_dir.mkdir(exist_ok=True)
            self.news_cache_dir.mkdir(exist_ok=True)
            
            logger.info(f"Initializing database at {self.db_path}")
            self._init_db()
            logger.info("PortfolioStorage initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PortfolioStorage: {e}")
            logger.error(f"Data directory: {data_dir}")
            logger.error(f"Current working directory: {Path.cwd()}")
            raise
    
    def _init_db(self):
        """Initialize SQLite database with portfolio table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tickers (
                    ticker TEXT PRIMARY KEY,
                    asset_type TEXT NOT NULL,
                    description TEXT,
                    exposure_tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS refresh_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    refresh_type TEXT NOT NULL,
                    ticker TEXT,
                    status TEXT NOT NULL,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def add_ticker(self, ticker: str, asset_type: str, 
                   description: str = '', exposure_tags: str = '') -> bool:
        """
        Add a new ticker to the portfolio.
        
        Args:
            ticker: Stock/ETF symbol (e.g., 'AAPL')
            asset_type: 'Stock' or 'ETF'
            description: Brief description of the asset
            exposure_tags: Comma-separated tags (e.g., 'AI, Tech, Growth')
        
        Returns:
            True if added successfully, False if ticker already exists
        """
        ticker = ticker.upper().strip()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO tickers (ticker, asset_type, description, exposure_tags)
                    VALUES (?, ?, ?, ?)
                ''', (ticker, asset_type, description, exposure_tags))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def update_ticker(self, ticker: str, asset_type: Optional[str] = None,
                      description: Optional[str] = None, 
                      exposure_tags: Optional[str] = None) -> bool:
        """
        Update an existing ticker's metadata.
        
        Args:
            ticker: Stock/ETF symbol to update
            asset_type: New asset type (optional)
            description: New description (optional)
            exposure_tags: New exposure tags (optional)
        
        Returns:
            True if updated successfully
        """
        ticker = ticker.upper().strip()
        updates = []
        values = []
        
        if asset_type is not None:
            updates.append('asset_type = ?')
            values.append(asset_type)
        if description is not None:
            updates.append('description = ?')
            values.append(description)
        if exposure_tags is not None:
            updates.append('exposure_tags = ?')
            values.append(exposure_tags)
        
        if not updates:
            return False
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        values.append(ticker)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f'''
                UPDATE tickers SET {', '.join(updates)}
                WHERE ticker = ?
            ''', values)
            conn.commit()
            return cursor.rowcount > 0
    
    def remove_ticker(self, ticker: str) -> bool:
        """
        Remove a ticker from the portfolio.
        
        Args:
            ticker: Stock/ETF symbol to remove
        
        Returns:
            True if removed successfully
        """
        ticker = ticker.upper().strip()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('DELETE FROM tickers WHERE ticker = ?', (ticker,))
            conn.commit()
            
            if cursor.rowcount > 0:
                self._cleanup_ticker_cache(ticker)
                return True
            return False
    
    def _cleanup_ticker_cache(self, ticker: str):
        """Remove cached data for a ticker."""
        price_file = self.price_cache_dir / f'{ticker}.csv'
        sparkline_file = self.sparkline_dir / f'{ticker}.png'
        news_file = self.news_cache_dir / f'{ticker}.json'
        
        for f in [price_file, sparkline_file, news_file]:
            if f.exists():
                f.unlink()
    
    def get_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get a single ticker's metadata."""
        ticker = ticker.upper().strip()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                'SELECT * FROM tickers WHERE ticker = ?', (ticker,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_tickers(self) -> pd.DataFrame:
        """
        Get all tickers in the portfolio.
        
        Returns:
            DataFrame with columns: ticker, asset_type, description, exposure_tags
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(
                'SELECT ticker, asset_type, description, exposure_tags FROM tickers ORDER BY ticker',
                conn
            )
        return df
    
    def save_price_data(self, ticker: str, df: pd.DataFrame):
        """Save price data to CSV cache."""
        ticker = ticker.upper().strip()
        df.to_csv(self.price_cache_dir / f'{ticker}.csv')
    
    def load_price_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """Load price data from CSV cache."""
        ticker = ticker.upper().strip()
        cache_file = self.price_cache_dir / f'{ticker}.csv'
        if cache_file.exists():
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        return None
    
    def get_price_cache_age(self, ticker: str) -> Optional[float]:
        """Get age of price cache in hours."""
        ticker = ticker.upper().strip()
        cache_file = self.price_cache_dir / f'{ticker}.csv'
        if cache_file.exists():
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            return (datetime.now() - mtime).total_seconds() / 3600
        return None
    
    def save_indicators(self, df: pd.DataFrame):
        """Save computed indicators to CSV."""
        df.to_csv(self.indicators_path, index=False, quoting=csv.QUOTE_ALL)
    
    def load_indicators(self) -> Optional[pd.DataFrame]:
        """Load computed indicators from CSV."""
        if self.indicators_path.exists():
            df = pd.read_csv(self.indicators_path, quoting=csv.QUOTE_ALL, quotechar='"')
            # Ensure exposure_tags column is treated as string (not NaN)
            if 'exposure_tags' in df.columns:
                df['exposure_tags'] = df['exposure_tags'].fillna('').astype(str)
            return df
        return None
    
    def get_sparkline_path(self, ticker: str) -> Path:
        """Get path to sparkline image for a ticker."""
        ticker = ticker.upper().strip()
        return self.sparkline_dir / f'{ticker}.png'
    
    def sparkline_exists(self, ticker: str) -> bool:
        """Check if sparkline image exists for a ticker."""
        return self.get_sparkline_path(ticker).exists()
    
    def save_news(self, ticker: str, news_data: List[Dict]):
        """Save news data to JSON cache."""
        import json
        ticker = ticker.upper().strip()
        news_file = self.news_cache_dir / f'{ticker}.json'
        with open(news_file, 'w') as f:
            json.dump({
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'headlines': news_data
            }, f, indent=2)
    
    def load_news(self, ticker: str) -> Optional[List[Dict]]:
        """Load news data from JSON cache."""
        import json
        ticker = ticker.upper().strip()
        news_file = self.news_cache_dir / f'{ticker}.json'
        if news_file.exists():
            with open(news_file, 'r') as f:
                data = json.load(f)
                return data.get('headlines', [])
        return None
    
    def get_news_cache_age(self, ticker: str) -> Optional[float]:
        """Get age of news cache in hours."""
        ticker = ticker.upper().strip()
        news_file = self.news_cache_dir / f'{ticker}.json'
        if news_file.exists():
            mtime = datetime.fromtimestamp(news_file.stat().st_mtime)
            return (datetime.now() - mtime).total_seconds() / 3600
        return None
    
    def log_refresh(self, refresh_type: str, ticker: Optional[str], 
                    status: str, message: str = ''):
        """Log a refresh operation."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO refresh_log (refresh_type, ticker, status, message)
                VALUES (?, ?, ?, ?)
            ''', (refresh_type, ticker, status, message))
            conn.commit()
    
    def get_last_refresh(self, refresh_type: str) -> Optional[datetime]:
        """Get timestamp of last successful refresh."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT timestamp FROM refresh_log 
                WHERE refresh_type = ? AND status = 'success'
                ORDER BY timestamp DESC LIMIT 1
            ''', (refresh_type,))
            row = cursor.fetchone()
            if row:
                return datetime.fromisoformat(row[0])
        return None
