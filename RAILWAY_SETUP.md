# Railway.app Deployment Guide

## Step 1: Push Code to GitHub
```bash
git add .
git commit -m "Add Railway configuration"
git push origin main
```

## Step 2: Deploy on Railway

1. Go to https://railway.app
2. Click "Login" → Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose "Youtube-Automator"
6. Railway will automatically deploy

## Step 3: Add Environment Variables

In Railway dashboard:
1. Click your project
2. Go to "Variables" tab
3. Add these:

```
PEXELS_API_KEY=your_key
PIXABAY_API_KEY=your_key
GEMINI_API_KEY=your_key
YOUTUBE_API_KEY=your_key
CLIENT_SECRET_BASE64=your_base64_string
TOKEN_PICKLE_BASE64=your_base64_string
```

## Step 4: Create Cron Jobs

### Method A: Use Railway Cron (New Feature)
1. In your service, click "Settings"
2. Under "Deploy Triggers", add cron schedules
3. Add two triggers:
   - Shorts: `0 * * * *` → Command: `python main.py`
   - Long: `30 * * * *` → Command: `python main_long.py`

### Method B: Use GitHub Actions + Railway Webhook
1. In Railway, go to service → "Settings" → "Webhooks"
2. Copy webhook URL
3. Add to GitHub Secrets as `RAILWAY_WEBHOOK_SHORTS` and `RAILWAY_WEBHOOK_LONG`
4. Keep your existing GitHub Actions workflow to trigger Railway

### Method C: External Cron Service (cron-job.org)
1. Go to https://cron-job.org (free)
2. Create account
3. Get Railway webhook URL
4. Create two cron jobs:
   - Hourly: Call Railway webhook for shorts
   - Hourly offset: Call Railway webhook for long

## Step 5: Monitor

- View logs in Railway dashboard
- Check YouTube for uploads
- Monitor usage in "Usage" tab

## Costs:
- Free: $5 credits/month
- Execution: ~$0.02/hour
- Your usage: ~$10/month (16 hours/day × 30 days × $0.02)
- **You'll need to add $5/month after trial**

## Alternative Free Options if Railway Costs Too Much:

1. **Fly.io**: 3 VMs free, better for 24/7
2. **Koyeb**: 2 services free
3. **Google Cloud Run**: 2M requests/month free
