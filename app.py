"""
Real Estate Investment Simulator - Main Entry Point
Multi-scenario analysis and comparison tool
"""
import streamlit as st
import sys
import os
import pandas as pd

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

st.set_page_config(
    page_title="Real Estate Investment Simulator",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Main page
st.markdown('<div class="main-header">🏠 Real Estate Investment Simulator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Scenario Analysis & Comparison Tool</div>', unsafe_allow_html=True)

st.markdown("---")

# Introduction
st.header("Welcome to the Real Estate Investment Simulator!")

st.markdown("""
This tool helps you compare real estate investment strategies with stock market investments using detailed financial modeling, tax calculations, and visual analytics.

### 📊 Available Calculators

Use the sidebar to explore two investment comparison scenarios:
1. **Buy & Rent** - Compare buying a rental property vs investing in stocks
2. **Buy & Live** - Compare buying a home to live in vs renting and investing in stocks
""")

st.markdown("---")

# Features overview
st.header("🎯 Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 📊 Comprehensive Analysis
    - Month-by-month simulation
    - Tax-aware calculations
    - Multiple time horizons
    - Inflation adjustments
    """)

with col2:
    st.markdown("""
    #### 📈 Interactive Visualizations
    - Dynamic Plotly charts
    - Equity buildup tracking
    - Cashflow waterfalls
    - Comparison dashboards
    """)

with col3:
    st.markdown("""
    #### 💾 Export & Share
    - CSV data exports
    - Annual summaries
    - Detailed breakdowns
    - Print-ready reports
    """)

st.markdown("---")

# How it works
st.header("📖 How The Calculation Works")

st.markdown("""
### Rental Property Investment

**Day of Purchase:**
- Pay down payment + closing costs
- Down payment → builds equity
- Closing costs → unrecoverable

**Monthly:**
- True Cost = Unrecoverable costs - Rental income × (1 - vacancy rate)
- Unrecoverable costs = Interest + Property tax + Insurance + HOA + Maintenance
- Rental income accounts for vacancy (e.g., 8.3% = 1 month/year vacant)

**Annual Tax Event:**
- Operating income (rental) is taxed: Tax = Rental income × tax bracket
- Tax benefit from deductions: Benefit = (Property tax + Interest) × (1 - tax bracket)
- Surplus cash = Tax benefit - Tax on rental income - Tax on dividends
- Surplus invested in stock portfolio with same return/dividend rates

**Net Proceeds:**
- Property value (with appreciation) - Closing costs at sale - Remaining mortgage + Stock portfolio value

### Stock Investment Strategy

**Day of Purchase:**
- Invest same amount (down payment + closing costs) in stock portfolio

**Monthly:**
- Contribution = Rental property's (true cost + principal payment)
- This ensures equal cash outflow between strategies
- Dividends reinvested monthly

**Annual Tax Event:**
- Tax on cumulative dividends for the year
- Tax = Total dividends × tax bracket

**Net Proceeds:**
- Total stock portfolio value
""")

st.markdown("---")

# Quick start guide
st.header("🚀 Quick Start Guide")

st.markdown("""
1. **Click "Buy and Rent"** in the sidebar navigation
2. **Configure Parameters** using the sliders:
   - Property details (price, down payment, closing costs)
   - Mortgage details (rate, term)
   - Property costs (taxes, HOA, insurance, maintenance)
   - Rental income (monthly rent, vacancy rate)
   - Market assumptions (appreciation, stock returns, dividends, tax bracket)
3. **View Results** automatically updated as you adjust parameters
4. **Analyze Charts** showing net proceeds, costs, and operating income over time
5. **Review Summary** to see which strategy performs better

### 💡 Tips for Best Results

- **Start with realistic numbers** based on your local market
- **Adjust one variable at a time** to understand impact
- **Consider vacancy rate** carefully (8.3% = 1 month vacant per year)
- **Use realistic appreciation rates** (historical average ~3-4%)
- **Account for all costs** (don't forget HOA, insurance, maintenance)

### 📚 Understanding the Metrics

- **Net Proceeds**: Total wealth at end of investment period
- **True Cost**: Monthly out-of-pocket cost after rental income
- **Operating Income**: Rental income + dividends from stock portfolio
- **Cumulative Cost**: Sum of all monthly costs over time
- **Stock Portfolio**: Value of invested tax surplus over time
""")

st.markdown("---")

# Footer
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p>Real Estate Investment Simulator v1.0</p>
        <p style='font-size: 0.9rem;'>
            Built with Streamlit | Data-driven investment analysis
        </p>
        <p style='font-size: 0.8rem; margin-top: 1rem;'>
            ⚠️ Disclaimer: This tool is for educational purposes only. 
            Consult with financial and tax professionals before making investment decisions.
        </p>
    </div>
""", unsafe_allow_html=True)
