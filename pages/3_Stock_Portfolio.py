"""
Stock Portfolio Dashboard
=========================
A comprehensive dashboard for tracking and analyzing stock/ETF portfolios.

Features:
- Portfolio management (add/edit/remove tickers)
- Price returns across multiple timeframes
- Volume momentum indicators
- 1-year sparkline charts
- News headlines from TickerTick API

Data is designed to be refreshed nightly after market close.
Page load only reads from cached/local data for fast performance.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import base64
from datetime import datetime
import pytz

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.portfolio.storage import PortfolioStorage
from core.portfolio.data_fetching import fetch_price_data, refresh_all_price_data, validate_ticker
from core.portfolio.indicators import compute_all_indicators, format_return, format_volume_momentum
from core.portfolio.charts import generate_sparkline, generate_all_sparklines, get_sparkline_base64
from core.portfolio.news import fetch_ticker_news, refresh_all_news, get_news_summary

st.set_page_config(
    page_title="Stock Portfolio Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_resource
def get_storage():
    """Get cached storage instance."""
    return PortfolioStorage()

storage = get_storage()

@st.cache_data(ttl=300)
def load_cached_indicators():
    """Load indicators from cache with 5-minute TTL."""
    return storage.load_indicators()

def get_return_color(value):
    """Get color for return value display."""
    if value is None:
        return "gray"
    return "#00a86b" if value >= 0 else "#dc3545"

def format_return_html(value):
    """Format return as colored HTML."""
    if value is None:
        return '<span style="color: gray;">N/A</span>'
    color = get_return_color(value)
    sign = "+" if value >= 0 else ""
    return f'<span style="color: {color}; font-weight: bold;">{sign}{value:.2f}%</span>'

st.title("📊 Stock Portfolio Dashboard")

st.markdown("""
Track your stock and ETF portfolio with momentum indicators, price charts, and news.
Data is refreshed nightly after market close for optimal performance.
""")

tab1, tab2 = st.tabs(["📈 Dashboard", "⚙️ Manage Portfolio"])

with tab1:
    st.header("Portfolio Overview")
    
    # Refresh All button with progress
    col_refresh, col_spacer = st.columns([2, 8])
    with col_refresh:
        if st.button("🔄 Refresh All Data", type="primary", help="Refresh prices, indicators, charts, and news for all tickers"):
            tickers = storage.get_all_tickers()
            if tickers.empty:
                st.warning("No tickers to refresh")
            else:
                overall_progress = st.progress(0)
                current_step = st.empty()
                
                ticker_list = tickers['ticker'].tolist()
                
                # Step 1: Fetch price data
                current_step.text(f"Step 1/4: Fetching price data for {len(ticker_list)} tickers...")
                for i, ticker in enumerate(ticker_list):
                    try:
                        df = fetch_price_data(ticker, period='2y')
                        if df is not None:
                            storage.save_price_data(ticker, df)
                    except Exception:
                        pass
                overall_progress.progress(0.25)
                
                # Step 2: Compute indicators
                current_step.text("Step 2/4: Computing indicators...")
                compute_all_indicators(storage, save=True)
                overall_progress.progress(0.50)
                
                # Step 3: Generate sparklines
                current_step.text("Step 3/4: Generating sparklines...")
                generate_all_sparklines(storage, force=True)
                overall_progress.progress(0.75)
                
                # Step 4: Fetch news (with rate limiting)
                current_step.text("Step 4/4: Fetching news (respecting API rate limits)...")
                import time
                for i, ticker in enumerate(ticker_list):
                    try:
                        if i > 0:
                            time.sleep(6)  # Rate limit: 10 req/min
                        fetch_ticker_news(ticker, storage, num_headlines=5, use_cache=False)
                    except Exception:
                        pass
                overall_progress.progress(1.0)
                
                st.cache_data.clear()
                storage.log_refresh('price_data_batch', None, 'success', f"Completed for {len(ticker_list)} tickers")
                
                current_step.empty()
                overall_progress.empty()
                st.success("✅ All data refreshed!")
                st.rerun()
    
    indicators_df = load_cached_indicators()
    
    if indicators_df is None or indicators_df.empty:
        st.warning("No portfolio data available. Please add tickers in the 'Manage Portfolio' tab and refresh data.")
        
        st.markdown("""
        ### Getting Started
        1. Go to the **Manage Portfolio** tab
        2. Add stock/ETF tickers to your portfolio
        3. Go to the **Data Refresh** tab to fetch initial data
        4. Return here to view your dashboard
        """)
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tickers", len(indicators_df))
        with col2:
            stocks = len(indicators_df[indicators_df['asset_type'] == 'Stock'])
            st.metric("Stocks", stocks)
        with col3:
            etfs = len(indicators_df[indicators_df['asset_type'] == 'ETF'])
            st.metric("ETFs", etfs)
        with col4:
            last_refresh = storage.get_last_refresh('price_data_batch')
            if last_refresh:
                # Convert UTC to EST for display
                est = pytz.timezone('US/Eastern')
                if last_refresh.tzinfo is None:
                    last_refresh = pytz.utc.localize(last_refresh)
                last_refresh_est = last_refresh.astimezone(est)
                st.metric("Last Refresh", last_refresh_est.strftime('%b %d, %I:%M %p EST'))
            else:
                st.metric("Last Refresh", "Never")
        
        # Volume Momentum Explanation
        with st.expander("ℹ️ What is Volume Momentum?", expanded=False):
            st.markdown("""
            **Volume Momentum** measures recent trading activity compared to historical levels.
            
            **Calculation:**
            ```
            Volume Momentum = 20-day Avg Volume / 60-day Avg Volume
            ```
            
            **Interpretation:**
            - **> 1.0**: Increasing volume (bullish momentum) - More trading activity recently
            - **= 1.0**: Stable volume - Consistent trading activity
            - **< 1.0**: Decreasing volume - Less trading activity recently
            
            **Examples:**
            - **1.5x**: Recent volume is 50% higher than the 60-day average (strong interest)
            - **0.8x**: Recent volume is 20% lower than average (declining interest)
            
            Higher volume momentum often indicates increased investor interest and can precede price movements.
            """)
        
        st.divider()
        
        st.subheader("🔍 Filters & Sorting")
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            asset_filter = st.selectbox(
                "Asset Type",
                ["All", "Stock", "ETF"],
                index=0
            )
        
        with filter_col2:
            sort_column = st.selectbox(
                "Sort By",
                ["ticker", "return_1d", "return_5d", "return_1m", "return_3m", 
                 "return_6m", "return_1y", "volume_momentum"],
                index=0,
                format_func=lambda x: {
                    'ticker': 'Ticker',
                    'return_1d': '1D Return',
                    'return_5d': '5D Return',
                    'return_1m': '1M Return',
                    'return_3m': '3M Return',
                    'return_6m': '6M Return',
                    'return_1y': '1Y Return',
                    'volume_momentum': 'Volume Momentum'
                }.get(x, x)
            )
        
        with filter_col3:
            sort_order = st.selectbox(
                "Order",
                ["Descending", "Ascending"],
                index=0
            )
        
        filtered_df = indicators_df.copy()
        if asset_filter != "All":
            filtered_df = filtered_df[filtered_df['asset_type'] == asset_filter]
        
        if sort_column in filtered_df.columns:
            ascending = sort_order == "Ascending"
            if sort_column == 'ticker':
                filtered_df = filtered_df.sort_values(sort_column, ascending=ascending)
            else:
                filtered_df = filtered_df.sort_values(
                    sort_column, ascending=ascending, na_position='last'
                )
        
        st.divider()
        st.subheader("📋 Portfolio Table")
        
        for idx, row in filtered_df.iterrows():
            ticker = row['ticker']
            
            with st.container():
                main_cols = st.columns([1.2, 1, 2, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.2])
                
                with main_cols[0]:
                    st.markdown(f"**{ticker}**")
                    st.caption(row.get('asset_type', 'N/A'))
                
                with main_cols[1]:
                    last_close = row.get('last_close')
                    if last_close and pd.notna(last_close):
                        st.markdown(f"${last_close:,.2f}")
                    else:
                        st.markdown("N/A")
                
                with main_cols[2]:
                    sparkline_path = storage.get_sparkline_path(ticker)
                    if sparkline_path.exists():
                        try:
                            with open(sparkline_path, 'rb') as f:
                                img_data = base64.b64encode(f.read()).decode()
                            st.markdown(
                                f'<img src="data:image/png;base64,{img_data}" style="height: 40px; width: 100%;">',
                                unsafe_allow_html=True
                            )
                        except Exception:
                            st.caption("No chart")
                    else:
                        st.caption("No chart")
                
                return_cols = ['return_1d', 'return_5d', 'return_1m', 'return_3m', 'return_6m', 'return_1y']
                col_labels = ['1D', '5D', '1M', '3M', '6M', '1Y']
                
                for i, (col_name, label) in enumerate(zip(return_cols, col_labels)):
                    with main_cols[3 + i]:
                        value = row.get(col_name)
                        if pd.notna(value):
                            st.markdown(format_return_html(value), unsafe_allow_html=True)
                            st.caption(label)
                        else:
                            st.markdown('<span style="color: gray;">N/A</span>', unsafe_allow_html=True)
                            st.caption(label)
                
                with main_cols[9]:
                    vol_mom = row.get('volume_momentum')
                    if pd.notna(vol_mom):
                        color = "#00a86b" if vol_mom >= 1 else "#dc3545"
                        st.markdown(f'<span style="color: {color}; font-weight: bold;">{vol_mom:.2f}x</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="color: gray;">N/A</span>', unsafe_allow_html=True)
                    st.caption("Vol Mom")
                
                detail_cols = st.columns([1, 5])
                
                with detail_cols[0]:
                    # Display tags vertically
                    tags = row.get('exposure_tags', '')
                    if tags and pd.notna(tags):
                        tag_list = [t.strip() for t in str(tags).split(',') if t.strip()]
                        if tag_list:
                            # Render all tags in a single HTML block for better display
                            tags_html = ''.join([
                                f'<div style="background-color: #e0e0e0; padding: 3px 8px; border-radius: 12px; '
                                f'font-size: 0.75em; margin-bottom: 4px; word-wrap: break-word;">{tag}</div>'
                                for tag in tag_list
                            ])
                            st.markdown(tags_html, unsafe_allow_html=True)
                
                with detail_cols[1]:
                    # Display top 5 news with full headlines (no truncation)
                    news_data = storage.load_news(ticker)
                    if news_data:
                        for i, headline in enumerate(news_data[:5]):
                            title = headline.get('title', 'No title')
                            url = headline.get('url', '')
                            source = headline.get('source', '')
                            
                            if url:
                                st.markdown(
                                    f'<div style="font-size: 0.85em; margin-bottom: 4px; line-height: 1.4;">'
                                    f'📰 <a href="{url}" target="_blank" style="color: #1f77b4; text-decoration: none;">{title}</a> '
                                    f'<span style="color: gray; font-size: 0.85em;">({source})</span>'
                                    f'</div>',
                                    unsafe_allow_html=True
                                )
                            else:
                                st.caption(f"📰 {title} ({source})")
                    else:
                        st.caption("No recent news")
                
                st.divider()

with tab2:
    st.header("⚙️ Manage Portfolio")
    
    st.subheader("Add New Ticker")
    
    add_col1, add_col2 = st.columns([1.5, 1])
    
    with add_col1:
        new_ticker = st.text_input("Ticker Symbol", placeholder="e.g., AAPL").upper().strip()
    
    with add_col2:
        new_asset_type = st.selectbox("Asset Type", ["Stock", "ETF"])
    
    # Combined description and tags field
    combined_input = st.text_input(
        "Description & Tags",
        placeholder="e.g., Apple Inc. | Tech, AI, Hardware",
        help="Format: Company Name | Tag1, Tag2, Tag3 (use | to separate description from tags)"
    )
    
    # Parse combined input
    if '|' in combined_input:
        new_description, new_tags = combined_input.split('|', 1)
        new_description = new_description.strip()
        new_tags = new_tags.strip()
    else:
        new_description = combined_input.strip()
        new_tags = ""
    
    if st.button("➕ Add Ticker", type="primary"):
        if not new_ticker:
            st.error("Please enter a ticker symbol")
        else:
            existing = storage.get_ticker(new_ticker)
            if existing:
                st.error(f"{new_ticker} already exists in portfolio")
            else:
                with st.spinner(f"Validating {new_ticker}..."):
                    is_valid = validate_ticker(new_ticker)
                
                if is_valid:
                    success = storage.add_ticker(
                        new_ticker, new_asset_type, new_description, new_tags
                    )
                    if success:
                        st.success(f"✅ Added {new_ticker} to portfolio!")
                        
                        # Auto-fetch data for new ticker
                        progress_container = st.empty()
                        with progress_container.container():
                            st.info(f"🔄 Fetching data for {new_ticker}...")
                            
                            # Fetch price data
                            with st.spinner("Fetching price data..."):
                                df = fetch_price_data(new_ticker, period='2y')
                                if df is not None:
                                    storage.save_price_data(new_ticker, df)
                            
                            # Compute indicators
                            with st.spinner("Computing indicators..."):
                                compute_all_indicators(storage, save=True)
                            
                            # Generate sparkline
                            with st.spinner("Generating chart..."):
                                generate_sparkline(new_ticker, storage)
                            
                            # Fetch news
                            with st.spinner("Fetching news..."):
                                fetch_ticker_news(new_ticker, storage, num_headlines=5, use_cache=False)
                        
                        progress_container.empty()
                        st.success(f"✅ {new_ticker} added and data loaded successfully!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"Failed to add {new_ticker}")
                else:
                    st.error(f"{new_ticker} is not a valid ticker symbol or has no data available")
    
    st.divider()
    
    # Refresh tags button
    refresh_col1, refresh_col2, refresh_col3 = st.columns([2, 2, 2])
    
    with refresh_col1:
        if st.button("🔄 Refresh All Tags", type="secondary", use_container_width=True):
            # Clear cache BEFORE recomputing to ensure fresh load
            st.cache_data.clear()
            with st.spinner("Recomputing indicators with updated tags..."):
                try:
                    compute_all_indicators(storage, save=True)
                    st.success("✅ Tags refreshed! Dashboard will update now.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to refresh tags: {e}")
    
    st.divider()
    
    st.subheader("Current Portfolio")
    
    current_tickers = storage.get_all_tickers()
    
    if current_tickers.empty:
        st.info("No tickers in portfolio yet. Add some above!")
    else:
        for idx, row in current_tickers.iterrows():
            with st.expander(f"**{row['ticker']}** - {row['asset_type']}", expanded=False):
                edit_col1, edit_col2 = st.columns([3, 1])
                
                with edit_col1:
                    # Combined description and tags field
                    current_desc = row.get('description', '')
                    current_tags = row.get('exposure_tags', '')
                    combined_value = f"{current_desc} | {current_tags}" if current_tags else current_desc
                    
                    edit_combined = st.text_input(
                        "Description & Tags",
                        value=combined_value,
                        key=f"combined_{row['ticker']}",
                        help="Format: Company Name | Tag1, Tag2, Tag3"
                    )
                    
                    # Parse combined input
                    if '|' in edit_combined:
                        edit_desc, edit_tags = edit_combined.split('|', 1)
                        edit_desc = edit_desc.strip()
                        edit_tags = edit_tags.strip()
                    else:
                        edit_desc = edit_combined.strip()
                        edit_tags = ""
                    
                    edit_type = st.selectbox(
                        "Asset Type",
                        ["Stock", "ETF"],
                        index=0 if row['asset_type'] == 'Stock' else 1,
                        key=f"type_{row['ticker']}"
                    )
                
                with edit_col2:
                    st.write("")
                    st.write("")
                    if st.button("💾 Save", key=f"save_{row['ticker']}"):
                        storage.update_ticker(
                            row['ticker'],
                            asset_type=edit_type,
                            description=edit_desc,
                            exposure_tags=edit_tags
                        )
                        # Clear cache BEFORE recomputing to ensure fresh load
                        st.cache_data.clear()
                        # Recompute indicators to include updated tags
                        with st.spinner("Updating indicators with new tags..."):
                            compute_all_indicators(storage, save=True)
                        st.success("Updated! Tags will appear on dashboard now.")
                        st.rerun()
                    
                    if st.button("🗑️ Remove", key=f"remove_{row['ticker']}", type="secondary"):
                        storage.remove_ticker(row['ticker'])
                        st.success(f"Removed {row['ticker']}")
                        st.cache_data.clear()
                        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")
tickers_df = storage.get_all_tickers()
st.sidebar.metric("Portfolio Size", len(tickers_df))

last_refresh = storage.get_last_refresh('price_data_batch')
if last_refresh:
    # Convert UTC to EST for display
    est = pytz.timezone('US/Eastern')
    if last_refresh.tzinfo is None:
        last_refresh = pytz.utc.localize(last_refresh)
    last_refresh_est = last_refresh.astimezone(est)
    st.sidebar.caption(f"Last data refresh: {last_refresh_est.strftime('%b %d, %Y %I:%M %p EST')}")
else:
    st.sidebar.caption("Data never refreshed")

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Stock Portfolio Dashboard**  
Part of the Real Estate Investment Suite

📊 Track stocks & ETFs  
📈 Momentum indicators  
📰 News integration
""")
