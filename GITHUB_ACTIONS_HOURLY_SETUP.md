# GitHub Actions Setup - YouTube Shorts Automation (Every 1 Hour)

This workflow automatically generates and uploads YouTube Shorts **every 1 hour** using GitHub Actions - completely free with no API keys exposed in your code.

---

## 🔒 Security Features

✅ **All API keys stored as GitHub Secrets** (never in code)  
✅ **Credentials auto-deleted after each run**  
✅ **No sensitive data in logs or commits**  
✅ **.env file excluded from repository**

---

## 📋 Setup Instructions

### Step 1: Push Code to GitHub

```powershell
cd "C:\Users\shivg\OneDrive\Desktop\yt workflow"
git add .
git commit -m "Add GitHub Actions workflow for hourly shorts"
git push origin main
```

---

### Step 2: Add Repository Secrets

Go to your GitHub repository:  
**Settings → Secrets and variables → Actions → New repository secret**

Add these secrets **one by one**:

#### Required Secrets:

| Secret Name | How to Get the Value |
|-------------|----------------------|
| `GEMINI_API_KEYS` | Copy from your `.env` file (line 15) - the full comma-separated list |
| `PEXELS_API_KEY` | Copy from your `.env` file (line 9) |
| `PIXABAY_API_KEY` | Copy from your `.env` file (line 12) |
| `BING_AUTH_COOKIE` | Copy from your `.env` file (line 6) |
| `ELEVENLABS_API_KEY` | Copy from your `.env` file (line 20) |
| `YOUTUBE_API_KEY` | Copy from your `.env` file (line 2) |
| `CLIENT_SECRET_JSON` | Copy **entire contents** of `client_secret.json` file |
| `TOKEN_PICKLE_BASE64` | Run the command below to generate |

#### To Generate TOKEN_PICKLE_BASE64:

**On Windows PowerShell:**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Users\shivg\OneDrive\Desktop\yt workflow\token.pickle"))
```

**On Linux/Mac:**
```bash
base64 -w 0 token.pickle
```

Copy the output and add it as `TOKEN_PICKLE_BASE64` secret.

---

### Step 3: Verify Workflow

1. Go to **Actions** tab in your GitHub repository
2. Enable workflows if prompted
3. You should see: **"YouTube Shorts Automation"**
4. Click **"Run workflow"** to test it manually (optional)

---

## ⏰ Schedule

- **Frequency**: Every 1 hour (at minute 0 of each hour)
- **Cron Expression**: `0 * * * *`
- **Example Times**: 1:00 AM, 2:00 AM, 3:00 AM, etc.

---

## 🔧 Customize Schedule

To change the frequency, edit `.github/workflows/youtube-shorts-automation.yml`:

```yaml
schedule:
  - cron: '0 * * * *'    # Every 1 hour
  # - cron: '0 */2 * * *'  # Every 2 hours
  # - cron: '0 */6 * * *'  # Every 6 hours
  # - cron: '0 9,15,21 * * *'  # At 9 AM, 3 PM, 9 PM
```

---

## 📊 Monitor Workflow

### View Runs:
1. Go to **Actions** tab
2. Click on **"YouTube Shorts Automation"**
3. See all past and current runs

### Check Logs:
1. Click on any workflow run
2. Click on **"generate-and-upload-short"** job
3. Expand steps to see detailed logs

### Download Logs:
- Logs are automatically saved as artifacts
- Available for 7 days after each run
- Download from the workflow run page

---

## ⚠️ Important Notes

### GitHub Actions Free Tier:
- **2,000 minutes/month** for free
- Each run takes ~5-10 minutes
- **1 hour schedule** = 720 runs/month ≈ 3,600-7,200 minutes
- ⚠️ **This may exceed the free tier!**

### Recommended Schedules for Free Tier:
- **Every 2 hours**: `0 */2 * * *` → 360 runs/month ≈ 1,800-3,600 minutes
- **Every 3 hours**: `0 */3 * * *` → 240 runs/month ≈ 1,200-2,400 minutes ✅ Safe
- **Every 6 hours**: `0 */6 * * *` → 120 runs/month ≈ 600-1,200 minutes ✅ Very Safe

### API Rate Limits:
- YouTube API: 10,000 units/day (1-2 uploads = ~1,600 units each)
- Gemini API: Check your quota
- Pexels API: 200 requests/hour

---

## 🛠️ Troubleshooting

### Workflow not running?
- Check if GitHub Actions is enabled (Actions tab)
- Verify all secrets are added correctly
- Check workflow file syntax

### Upload failed?
- Verify `TOKEN_PICKLE_BASE64` is correct
- Check YouTube API quota
- Review error logs in Actions tab

### Out of GitHub Actions minutes?
- Reduce frequency (every 3-6 hours)
- Check usage: Settings → Billing → Actions minutes

---

## 🔐 Security Checklist

- [x] .env file is in .gitignore
- [x] No API keys in code
- [x] All secrets use GitHub Secrets
- [x] Credentials deleted after each run
- [x] No sensitive data in logs

---

## 📝 Manual Trigger

You can manually trigger the workflow anytime:

1. Go to **Actions** tab
2. Select **"YouTube Shorts Automation"**
3. Click **"Run workflow"**
4. Select branch: `main`
5. Click green **"Run workflow"** button

---

**Your shorts will now be published automatically every hour! 🎉**
