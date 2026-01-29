# Railway Volume Setup for Persistent Storage

## Problem Solved ✅

Railway containers are ephemeral - data resets on every deployment. By attaching a volume, your portfolio data persists across all deployments.

## Setup Steps

### **Step 1: Attach Volume in Railway Dashboard**

1. Go to your Railway project canvas
2. **Right-click** on your app service
3. Select **"Attach Volume"**
4. When prompted for **"Mount path"**, enter:
   ```
   /app/data
   ```
5. Click **"Create"** or **"Attach"**

Railway will automatically redeploy your service with the volume attached.

### **Step 2: Clear Old Cached Data (One-Time)**

Since Railway currently has old cached data with the broken CSV format, delete the old indicators file:

```bash
railway run bash
rm -f /app/data/portfolio/indicators.csv
exit
```

Or simply click **"Refresh All Data"** in your dashboard to regenerate everything.

### **Step 3: Test It Works**

1. Add a ticker with multiple tags: `"Tech, AI, Hardware"`
2. Verify all 3 tags display correctly
3. Make a small code change and push to GitHub
4. After Railway redeploys, your ticker should still be there ✅

---

## What Gets Persisted

The volume at `/app/data` stores:

```
/app/data/portfolio/
├── portfolio.db          # ✅ SQLite database (ticker metadata)
├── indicators.csv        # ✅ Computed metrics (returns, volume momentum)
├── price_cache/          # ✅ OHLCV price data per ticker
├── sparklines/           # ✅ Chart images
└── news_cache/           # ✅ News headlines
```

All of this now survives deployments!

---

## Deployment Workflow

After volume is attached:

1. **Make code changes** locally
2. **Test locally**: `streamlit run app.py`
3. **Commit and push**:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```
4. **Railway auto-deploys** - Your data persists! ✅
5. **No need to re-add tickers** - Everything is preserved

---

## Troubleshooting

### "Volume not showing up after attaching"

Check Railway deployment logs:
1. Go to your service → **"Deployments"**
2. Click current deployment
3. Check logs for volume mount errors

### "Data still resets after attaching volume"

Verify the mount path is exactly `/app/data`:
1. Go to your service → **"Settings"**
2. Look for **"Volumes"** section
3. Confirm mount path is `/app/data`

### "Tags still show one tag"

After volume is attached:
1. Delete old indicators: `railway run bash && rm -f /app/data/portfolio/indicators.csv && exit`
2. Click **"Refresh All Data"** in dashboard
3. This regenerates indicators with proper CSV quoting

### "Volume is using too much space"

Check current usage:
```bash
railway run bash
du -sh /app/data/*
exit
```

Typical usage for 50 tickers: ~10-20 MB (well within Railway limits)

---

## Summary

✅ **Attach volume** at `/app/data` via right-click menu  
✅ **Clear old cache** (one-time)  
✅ **Data persists** across all deployments  
✅ **No more re-adding tickers** after each push  
✅ **Production-ready** setup  

Your portfolio is now safe from Railway deployments! 🚀
