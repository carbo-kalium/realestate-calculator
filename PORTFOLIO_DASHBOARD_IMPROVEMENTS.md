# Stock Portfolio Dashboard - Improvements Summary

## ✅ Changes Implemented

### 1. **Simplified User Experience**
- ✅ **Removed Data Refresh Tab**: All refresh functionality moved to Dashboard
- ✅ **Auto-fetch on Add**: When adding a new ticker, data is automatically fetched:
  - Price data (2 years)
  - Indicators & returns
  - Sparkline chart
  - News headlines (top 5)
- ✅ **Single Refresh Button**: One "🔄 Refresh All Data" button on Dashboard with progress bar

### 2. **Fixed 1Y Return Calculation**
- ✅ Changed default data fetch from 1 year to **2 years**
- ✅ This ensures 1Y return has enough historical data (needs 252 trading days back)
- ✅ Updated in:
  - `data_fetching.py` - default period='2y'
  - `refresh_data.py` - fetch_price_data period='2y'
  - Dashboard auto-fetch

### 3. **News Improvements**
- ✅ **Top 5 Headlines**: Dashboard now shows top 5 most recent articles (was 2-3)
- ✅ **Clickable Links**: Each headline is a clickable link that opens in new tab
- ✅ **Separate Cron Job**: Created `refresh_news.py` for 3x daily news updates
- ✅ **Rate Limiting**: 6-second delays between requests to respect 10 req/min limit

### 4. **Volume Momentum Explanation**
- ✅ Added expandable info section on Dashboard explaining:
  - Calculation formula: `20-day avg volume / 60-day avg volume`
  - Interpretation guide
  - Examples (1.5x = bullish, 0.8x = declining interest)

### 5. **Rate Limit Compliance**
- ✅ **TickerTick API**: 10 requests per minute limit
- ✅ Implemented 6-second delays between news requests
- ✅ Progress indicators show rate limiting in action
- ✅ Separate news refresh to avoid conflicts with price data refresh

---

## 📋 Updated Workflow

### **Adding a New Ticker**
1. Go to "Manage Portfolio" tab
2. Enter ticker, asset type, description, tags
3. Click "➕ Add Ticker"
4. **Automatic process begins**:
   - Validates ticker
   - Fetches 2 years of price data
   - Computes all indicators
   - Generates sparkline chart
   - Fetches top 5 news headlines
5. Returns to dashboard with ticker ready to view

### **Refreshing All Data**
1. Click "🔄 Refresh All Data" button on Dashboard
2. Progress bar shows 4 steps:
   - Step 1: Fetching price data
   - Step 2: Computing indicators
   - Step 3: Generating sparklines
   - Step 4: Fetching news (with rate limiting)
3. Page auto-refreshes when complete

---

## 🤖 Automated Refresh Setup

### **Two Separate Cron Jobs**

#### **1. Price & Indicators Refresh (Daily after market close)**
**Script**: `refresh_data.py`  
**Schedule**: Once per day at 6:30 PM EST (after market close)  
**What it does**:
- Fetches 2 years of price data
- Computes returns (1D, 5D, 2W, 1M, 3M, 6M, 1Y)
- Calculates volume momentum
- Generates sparkline charts

**Crontab entry**:
```bash
# Run at 6:30 PM EST (11:30 PM UTC) on weekdays
30 23 * * 1-5 cd /path/to/realestate && python refresh_data.py >> /var/log/portfolio_refresh.log 2>&1
```

#### **2. News Refresh (3x daily)**
**Script**: `refresh_news.py`  
**Schedule**: Three times per day
**What it does**:
- Fetches top 5 news headlines for each ticker
- Respects API rate limits (6-second delays)
- Updates local cache

**Crontab entries**:
```bash
# After market close: 6:30 PM EST (11:30 PM UTC) - After price refresh
30 23 * * 1-5 cd /path/to/realestate && python refresh_news.py >> /var/log/portfolio_news.log 2>&1

# Before market open: 6:00 AM EST (11:00 AM UTC)
0 11 * * 1-5 cd /path/to/realestate && python refresh_news.py >> /var/log/portfolio_news.log 2>&1

# During market hours: 1:00 PM EST (6:00 PM UTC)
0 18 * * 1-5 cd /path/to/realestate && python refresh_news.py >> /var/log/portfolio_news.log 2>&1
```

### **Why Separate Jobs?**
1. **Price data** only changes once per day (after market close)
2. **News** is continuously updated throughout the day
3. **Rate limiting**: Separating jobs prevents API conflicts
4. **Efficiency**: Don't re-fetch price data when only news needs updating

---

## 📊 Dashboard Features

### **Main View**
- Sortable by any column (returns, volume momentum, ticker)
- Filter by asset type (Stock/ETF)
- Refresh All button with progress tracking

### **Per Ticker Display**
- Ticker symbol & asset type
- Last close price
- 1-year sparkline chart (color-coded: green=up, red=down)
- Returns: 1D, 5D, 1M, 3M, 6M, 1Y (color-coded)
- Volume momentum ratio
- Exposure tags
- **Top 5 news headlines with clickable links**

### **Volume Momentum Info**
- Expandable explanation section
- Calculation formula
- Interpretation guide
- Real-world examples

---

## 🔧 Technical Details

### **Volume Momentum Calculation**
```python
Volume Momentum = 20-day Avg Volume / 60-day Avg Volume
```

**Interpretation**:
- **> 1.0**: Increasing volume (bullish) - More trading activity recently
- **= 1.0**: Stable volume - Consistent trading activity  
- **< 1.0**: Decreasing volume - Less trading activity recently

**Examples**:
- **1.5x**: Recent volume is 50% higher than 60-day average (strong interest)
- **0.8x**: Recent volume is 20% lower than average (declining interest)

### **Data Fetching**
- **yfinance**: 2 years of daily OHLCV data
- **TickerTick API**: Top 5 news headlines per ticker
- **Rate limit**: 10 requests/minute (6-second delays between requests)
- **Caching**: All data cached locally for fast page loads

### **File Structure**
```
core/portfolio/
├── storage.py           # SQLite + CSV data persistence
├── data_fetching.py     # yfinance (2y period default)
├── indicators.py        # Returns & volume momentum
├── charts.py            # Sparkline generation
└── news.py              # TickerTick API (5 headlines, rate limited)

pages/
└── 3_Stock_Portfolio.py # Dashboard (2 tabs: Dashboard + Manage)

refresh_data.py          # Daily cron: prices + indicators
refresh_news.py          # 3x daily cron: news only
```

---

## 🚀 Testing Locally

1. **Activate your virtual environment**:
   ```bash
   conda activate trader
   ```

2. **Ensure dependencies are installed**:
   ```bash
   pip install yfinance matplotlib requests
   ```

3. **Run the app**:
   ```bash
   cd ~/projects/tradeselect/realestate
   streamlit run app.py --server.headless true --server.port 8501
   ```

4. **Test the improvements**:
   - Add a new ticker (e.g., NVDA) - should auto-fetch all data
   - Click "Refresh All Data" - should show progress bar
   - Check 1Y returns - should now display (not N/A)
   - Click news headlines - should open in new tab
   - Expand "What is Volume Momentum?" - should show explanation

---

## 📝 Next Steps

1. **Test locally** to verify all features work
2. **Set up cron jobs** for automated refresh:
   - `refresh_data.py` - Daily after market close
   - `refresh_news.py` - 3x daily
3. **Deploy to Railway** when ready
4. **Monitor logs** to ensure refresh jobs run successfully

---

## ❓ FAQ

**Q: Why is 1Y return now showing correctly?**  
A: We now fetch 2 years of data instead of 1 year, ensuring enough historical data for 1-year return calculation (needs 252 trading days back).

**Q: How long does news refresh take?**  
A: For 10 tickers: ~60 seconds (6-second delay between each request to respect API limits).

**Q: Can I add more than 10 tickers?**  
A: Yes, but news refresh will take longer due to rate limiting (6 seconds per ticker).

**Q: What if a news fetch fails?**  
A: The script continues with other tickers and uses cached news as fallback. Errors are logged.

**Q: How do I view refresh history?**  
A: Check the SQLite database at `data/portfolio/portfolio.db` - table `refresh_log` contains all refresh events.

---

## 🎉 Summary

All requested improvements have been implemented:
1. ✅ Auto-fetch on ticker addition
2. ✅ Single refresh button with progress
3. ✅ Separate news cron job (3x daily)
4. ✅ Top 5 news with clickable links
5. ✅ Fixed 1Y return calculation
6. ✅ Volume momentum explanation
7. ✅ Rate limit compliance

The dashboard is now more user-friendly, efficient, and respects API limits!
