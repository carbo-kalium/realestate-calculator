#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
Run this to diagnose import/dependency issues.
"""

import sys
from pathlib import Path

print("Python version:", sys.version)
print("Python path:", sys.executable)
print()

# Test core imports
print("Testing core imports...")
try:
    import streamlit
    print("✓ streamlit")
except Exception as e:
    print(f"✗ streamlit: {e}")

try:
    import pandas
    print("✓ pandas")
except Exception as e:
    print(f"✗ pandas: {e}")

try:
    import numpy
    print("✓ numpy")
except Exception as e:
    print(f"✗ numpy: {e}")

try:
    import plotly
    print("✓ plotly")
except Exception as e:
    print(f"✗ plotly: {e}")

try:
    import matplotlib
    print("✓ matplotlib")
except Exception as e:
    print(f"✗ matplotlib: {e}")

try:
    import yfinance
    print("✓ yfinance")
except Exception as e:
    print(f"✗ yfinance: {e}")

try:
    import requests
    print("✓ requests")
except Exception as e:
    print(f"✗ requests: {e}")

try:
    import pytz
    print("✓ pytz")
except Exception as e:
    print(f"✗ pytz: {e}")

try:
    import csv
    print("✓ csv (stdlib)")
except Exception as e:
    print(f"✗ csv: {e}")

print()
print("Testing portfolio module imports...")

sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.portfolio.storage import PortfolioStorage
    print("✓ PortfolioStorage")
except Exception as e:
    print(f"✗ PortfolioStorage: {e}")
    import traceback
    traceback.print_exc()

try:
    from core.portfolio.data_fetching import fetch_price_data
    print("✓ data_fetching")
except Exception as e:
    print(f"✗ data_fetching: {e}")
    import traceback
    traceback.print_exc()

try:
    from core.portfolio.indicators import compute_all_indicators
    print("✓ indicators")
except Exception as e:
    print(f"✗ indicators: {e}")
    import traceback
    traceback.print_exc()

try:
    from core.portfolio.charts import generate_all_sparklines
    print("✓ charts")
except Exception as e:
    print(f"✗ charts: {e}")
    import traceback
    traceback.print_exc()

try:
    from core.portfolio.news import fetch_ticker_news
    print("✓ news")
except Exception as e:
    print(f"✗ news: {e}")
    import traceback
    traceback.print_exc()

print()
print("Testing storage initialization...")
try:
    storage = PortfolioStorage()
    print("✓ PortfolioStorage initialized successfully")
    print(f"  Data directory: {storage.data_dir}")
    print(f"  Database: {storage.db_path}")
except Exception as e:
    print(f"✗ PortfolioStorage initialization failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("All tests completed!")
