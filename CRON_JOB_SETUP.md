# Scheduled Cron Jobs Setup for Railway

## Problem

Your portfolio data shows "Last Refresh: Never" because the cron jobs aren't running automatically on Railway. The refresh scripts exist but aren't scheduled.

## Solution: Set Up Scheduled Jobs on Railway

Railway supports scheduled jobs, but the UI varies. Here are the best approaches:

---

## **Option 1: Railway Cron Service (Recommended)**

Create a separate Railway service just for running scheduled jobs.

### **Step 1: Create a New Service in Railway**

1. Go to your Railway project
2. Click **"+ New Service"**
3. Select **"Cron Job"** or **"Scheduled Job"** (if available)
4. Configure:
   - **Command**: `python refresh_data.py`
   - **Schedule**: `30 23 * * 1-5` (6:30 PM EST on weekdays)

### **Step 2: Connect to Your Repository**

1. Link the cron service to your GitHub repo
2. It will use the same `refresh_data.py` script

### **Step 3: Add Environment Variables**

The cron service needs access to the same data directory as your main app:
1. Go to the cron service → **"Variables"**
2. Add: `DATA_DIR=/app/data` (same as your main app)

This ensures the cron job reads/writes to the same volume as your Streamlit app.

---

## **Option 2: GitHub Actions (Alternative)**

If Railway doesn't have a visible cron option, use GitHub Actions to trigger the refresh.

### **Step 1: Create Workflow File**

Create `.github/workflows/refresh-portfolio.yml`:

```yaml
name: Refresh Portfolio Data

on:
  schedule:
    # Run at 6:30 PM EST (23:30 UTC) on weekdays
    - cron: '30 23 * * 1-5'
  workflow_dispatch:  # Allow manual trigger

jobs:
  refresh:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Refresh portfolio data
        run: python refresh_data.py
        env:
          # Add any API keys if needed
          TICKERTICK_API_KEY: ${{ secrets.TICKERTICK_API_KEY }}
```

### **Step 2: Commit and Push**

```bash
mkdir -p .github/workflows
# Create the file above
git add .github/workflows/refresh-portfolio.yml
git commit -m "Add GitHub Actions cron job for portfolio refresh"
git push origin main
```

This will run the refresh script automatically on schedule.

---

## **Option 3: Manual Refresh Button (Temporary)**

Until cron is set up, you can manually refresh:

1. Go to your Stock Portfolio Dashboard
2. Click **"🔄 Refresh All Data"** button
3. Wait for all steps to complete

This fetches fresh data immediately.

---

## **Recommended Schedule**

### **Data Refresh (Prices & Indicators)**
- **When**: 6:30 PM EST (after market close at 4 PM)
- **Frequency**: Weekdays only (Mon-Fri)
- **Cron**: `30 23 * * 1-5`
- **Script**: `refresh_data.py`

### **News Refresh**
- **When**: 3x daily
  - 8:00 AM EST (before market open)
  - 1:00 PM EST (midday)
  - 6:30 PM EST (after market close)
- **Frequency**: Weekdays only
- **Cron**: 
  - `0 13 * * 1-5` (8 AM EST)
  - `0 18 * * 1-5` (1 PM EST)
  - `30 23 * * 1-5` (6:30 PM EST)
- **Script**: `refresh_news.py`

---

## **Time Zone Reference**

| Time | EST | UTC |
|------|-----|-----|
| 8:00 AM | 8:00 | 13:00 |
| 1:00 PM | 13:00 | 18:00 |
| 4:00 PM | 16:00 | 21:00 |
| 6:30 PM | 18:30 | 23:30 |

---

## **Testing the Cron Job**

### **Check if Job Ran**

1. Go to your Stock Portfolio Dashboard
2. Check **"Last Refresh"** timestamp
3. If it shows a recent time, the job ran! ✅

### **Manual Test**

Run locally to verify the script works:

```bash
python refresh_data.py
```

You should see output like:
```
2026-01-30 18:30:00 - refresh_data - INFO - Fetching price data for AAPL...
2026-01-30 18:30:05 - refresh_data - INFO - Computing indicators...
2026-01-30 18:30:10 - refresh_data - INFO - Generating sparklines...
```

---

## **Troubleshooting**

### "Last Refresh still shows Never"

1. Check if cron service is running
2. Check Railway deployment logs for errors
3. Verify `DATA_DIR` environment variable is set
4. Manually click "Refresh All Data" button to test

### "Cron job runs but data doesn't update"

1. Check if the volume is properly mounted
2. Verify the cron job has write access to `/app/data`
3. Check logs for API errors (yfinance, TickerTick)

### "API rate limit errors"

The scripts include rate limiting:
- `refresh_data.py`: Fetches all tickers sequentially
- `refresh_news.py`: 6-second delay between API calls

If you hit limits, increase delays in the scripts.

---

## **Next Steps**

1. **Try Option 1 (Railway Cron Service)** first - it's the most integrated
2. **If not available, use Option 2 (GitHub Actions)** - it's reliable and free
3. **Test with manual "Refresh All Data"** button to verify scripts work

Let me know which approach you want to use and I can help set it up!
