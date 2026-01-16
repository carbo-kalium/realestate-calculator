# Deployment Guide - Real Estate Investment Simulator

## Overview

This guide provides options for deploying your Streamlit app to make it accessible from anywhere, 24/7, without sleep mode issues.

---

## 🚀 Recommended Free Deployment Options

### Option 1: Streamlit Community Cloud (Recommended)
**Best for: Quick deployment, zero configuration**

#### Pros:
- ✅ **100% Free** for public apps
- ✅ **Official Streamlit hosting**
- ✅ **Auto-deploys from GitHub**
- ✅ **Custom domain support**
- ✅ **Always-on** (no sleep mode for active apps)
- ✅ **Built-in secrets management**
- ✅ **Easy updates** (just push to GitHub)

#### Cons:
- ⚠️ Apps may sleep after 7 days of inactivity
- ⚠️ Limited resources (1 GB RAM, 1 CPU core)
- ⚠️ Must be public repository (or pay for private)

#### Steps:
1. **Push your code to GitHub**
   ```bash
   cd /home/chinmay/projects/tradeselect/realestate
   git init
   git add .
   git commit -m "Initial commit - Real Estate Investment Simulator"
   git remote add origin https://github.com/YOUR_USERNAME/realestate-calculator.git
   git push -u origin main
   ```

2. **Create requirements.txt**
   ```bash
   pip freeze | grep -E "streamlit|pandas|plotly|numpy" > requirements.txt
   ```

3. **Sign up at Streamlit Community Cloud**
   - Go to: https://streamlit.io/cloud
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Click "Deploy"

4. **Access your app**
   - URL: `https://YOUR_USERNAME-realestate-calculator.streamlit.app`
   - Share this link with anyone!

#### Keeping It Awake:
- Use a free uptime monitor like UptimeRobot (https://uptimerobot.com)
- Ping your app every 5 minutes to prevent sleep
- Free tier: 50 monitors, 5-minute intervals

---

### Option 2: Hugging Face Spaces
**Best for: ML/Data apps, generous free tier**

#### Pros:
- ✅ **100% Free** for public spaces
- ✅ **Always-on** (no sleep mode)
- ✅ **More resources** (2 GB RAM, 2 CPU cores)
- ✅ **Git-based deployment**
- ✅ **Custom domain support**
- ✅ **Built-in CI/CD**

#### Cons:
- ⚠️ Requires creating a Space-specific structure
- ⚠️ Less Streamlit-specific features

#### Steps:
1. **Create account at Hugging Face**
   - Go to: https://huggingface.co
   - Sign up for free

2. **Create a new Space**
   - Click "New Space"
   - Name: `realestate-calculator`
   - SDK: Select "Streamlit"
   - Visibility: Public

3. **Clone and push your code**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/realestate-calculator
   cd realestate-calculator
   cp -r /home/chinmay/projects/tradeselect/realestate/* .
   git add .
   git commit -m "Initial deployment"
   git push
   ```

4. **Access your app**
   - URL: `https://huggingface.co/spaces/YOUR_USERNAME/realestate-calculator`

---

### Option 3: Railway.app
**Best for: Full control, generous free tier**

#### Pros:
- ✅ **$5/month free credit** (enough for small apps)
- ✅ **Always-on** (no sleep mode)
- ✅ **Custom domains**
- ✅ **Environment variables**
- ✅ **Automatic HTTPS**
- ✅ **Database support** (if needed later)

#### Cons:
- ⚠️ Free credit may run out for high-traffic apps
- ⚠️ Requires credit card (not charged unless you exceed free tier)

#### Steps:
1. **Sign up at Railway**
   - Go to: https://railway.app
   - Sign up with GitHub

2. **Create new project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure deployment**
   - Railway auto-detects Streamlit
   - Add environment variables if needed
   - Deploy!

4. **Access your app**
   - Railway provides a URL: `https://YOUR_APP.railway.app`

---

### Option 4: Render.com
**Best for: Professional deployment, free tier**

#### Pros:
- ✅ **Free tier** for web services
- ✅ **Always-on** (no sleep mode on paid tier)
- ✅ **Custom domains**
- ✅ **Automatic HTTPS**
- ✅ **Environment variables**

#### Cons:
- ⚠️ Free tier spins down after 15 minutes of inactivity
- ⚠️ Slower cold starts

#### Steps:
1. **Sign up at Render**
   - Go to: https://render.com
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub repository

3. **Configure**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment

---

### Option 5: Self-Hosted (VPS)
**Best for: Full control, no limitations**

#### Pros:
- ✅ **Complete control**
- ✅ **No sleep mode**
- ✅ **Custom domain**
- ✅ **Unlimited resources** (based on VPS)

#### Cons:
- ⚠️ Requires technical knowledge
- ⚠️ Costs money (but cheap: $5-10/month)
- ⚠️ You manage everything

#### Recommended Providers:
- **DigitalOcean** - $6/month droplet
- **Linode** - $5/month
- **Vultr** - $5/month
- **AWS Lightsail** - $3.50/month

---

## 📊 Comparison Table

| Feature | Streamlit Cloud | Hugging Face | Railway | Render | Self-Hosted |
|---------|----------------|--------------|---------|--------|-------------|
| **Cost** | Free | Free | $5/mo credit | Free tier | $5-10/mo |
| **Always-on** | ⚠️ With monitor | ✅ Yes | ✅ Yes | ⚠️ Paid only | ✅ Yes |
| **Setup Time** | 5 minutes | 10 minutes | 10 minutes | 15 minutes | 1-2 hours |
| **Resources** | 1GB RAM | 2GB RAM | Varies | 512MB RAM | Your choice |
| **Custom Domain** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Auto-deploy** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Manual |
| **Difficulty** | ⭐ Easy | ⭐⭐ Easy | ⭐⭐ Easy | ⭐⭐ Medium | ⭐⭐⭐⭐ Hard |

---

## 🎯 My Recommendation

### For Your Use Case:
**Use Streamlit Community Cloud + UptimeRobot**

**Why:**
1. **100% Free** - No costs at all
2. **Easy Setup** - 5 minutes to deploy
3. **Always Accessible** - UptimeRobot keeps it awake
4. **Auto-updates** - Push to GitHub, app updates automatically
5. **Official Support** - Built for Streamlit apps

**Setup Steps:**

### Step 1: Prepare Your Repository
```bash
cd /home/chinmay/projects/tradeselect/realestate

# Create requirements.txt
cat > requirements.txt << EOF
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
numpy>=1.24.0
EOF

# Create .gitignore
cat > .gitignore << EOF
__pycache__/
*.py[cod]
*$py.class
.env
.venv
venv/
*.log
.DS_Store
EOF

# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit - Real Estate Investment Simulator"
```

### Step 2: Push to GitHub
```bash
# Create repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/realestate-calculator.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Streamlit Cloud
1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `YOUR_USERNAME/realestate-calculator`
5. Main file path: `app.py`
6. Click "Deploy"
7. Wait 2-3 minutes for deployment

### Step 4: Keep It Awake (Optional)
1. Go to https://uptimerobot.com
2. Sign up for free
3. Add new monitor:
   - Type: HTTP(s)
   - URL: Your Streamlit app URL
   - Interval: 5 minutes
4. Save

**Your app is now live 24/7!** 🎉

---

## 🔒 Security Considerations

### For Public Deployment:
- ✅ No sensitive data in code
- ✅ No API keys hardcoded
- ✅ No database credentials
- ✅ All calculations client-side

**Your app is safe to deploy publicly!**

---

## 📱 Custom Domain (Optional)

### Using Streamlit Cloud:
1. Go to app settings
2. Click "Custom domain"
3. Add your domain (e.g., `calculator.yourdomain.com`)
4. Update DNS records as instructed
5. Wait for SSL certificate (automatic)

### Cost:
- Domain: ~$10-15/year (from Namecheap, Google Domains, etc.)
- Hosting: Free (Streamlit Cloud)

---

## 🔄 Updating Your App

### With Streamlit Cloud:
```bash
# Make changes locally
git add .
git commit -m "Update calculations"
git push

# App automatically redeploys in 1-2 minutes!
```

---

## 📊 Monitoring & Analytics

### Free Options:
1. **Streamlit Cloud Dashboard** - Built-in usage stats
2. **Google Analytics** - Add to your app
3. **UptimeRobot** - Uptime monitoring
4. **GitHub Insights** - Repository traffic

---

## ❓ FAQ

### Q: Will my app sleep?
**A:** With UptimeRobot pinging every 5 minutes, no.

### Q: Can I use a custom domain?
**A:** Yes, Streamlit Cloud supports custom domains for free.

### Q: What if I exceed free tier limits?
**A:** Unlikely for this app. If you do, upgrade to Streamlit Cloud Teams ($250/mo) or switch to Railway/Render.

### Q: Can I make it private?
**A:** Yes, but requires paid plan. For free, app must be public.

### Q: How do I add authentication?
**A:** Use `streamlit-authenticator` package or deploy to Railway/Render with custom auth.

---

## 🚀 Quick Start Command

```bash
# One-command setup for Streamlit Cloud
cd /home/chinmay/projects/tradeselect/realestate && \
echo "streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
numpy>=1.24.0" > requirements.txt && \
echo "__pycache__/
*.py[cod]
.env
venv/" > .gitignore && \
git init && \
git add . && \
git commit -m "Initial commit" && \
echo "Now create GitHub repo and run: git remote add origin YOUR_REPO_URL && git push -u origin main"
```

---

## 📞 Support

- **Streamlit Docs**: https://docs.streamlit.io
- **Community Forum**: https://discuss.streamlit.io
- **GitHub Issues**: Create in your repository

---

**Recommendation: Start with Streamlit Community Cloud. It's free, easy, and perfect for your use case!** 🎯
