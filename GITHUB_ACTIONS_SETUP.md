# GitHub Actions Automation Setup Guide

This guide will help you set up automated YouTube Shorts generation that runs every 6 hours (4 times per day) on GitHub's servers - **completely free** and **no need to keep your PC on**.

---

## ✅ Benefits

- **Free**: GitHub Actions provides 2,000 free minutes/month (more than enough)
- **No PC required**: Runs on GitHub's cloud servers
- **Automatic**: Executes every 6 hours without manual intervention
- **Reliable**: GitHub's infrastructure is very stable
- **Easy monitoring**: View logs and results in GitHub Actions tab

---

## 📋 Step-by-Step Setup

### Step 1: Push Your Code to GitHub

Your repository is already connected to GitHub: `https://github.com/shiv989898/Youtube-Automator`

Make sure all latest changes are pushed:

```powershell
cd "C:\Users\shivg\OneDrive\Desktop\yt workflow"
git add .
git commit -m "Add GitHub Actions automation workflow"
git push origin main
```

---

### Step 2: Add Secrets to GitHub Repository

Go to your repository settings and add these secrets:

**Repository → Settings → Secrets and variables → Actions → New repository secret**

Add the following secrets (one by one):

#### 1. API Keys:

- **Name**: `GEMINI_API_KEY`
  - **Value**: Your Gemini API key from `.env` file

- **Name**: `PEXELS_API_KEY`
  - **Value**: Your Pexels API key from `.env` file

- **Name**: `PIXABAY_API_KEY`
  - **Value**: Your Pixabay API key from `.env` file

- **Name**: `YOUTUBE_API_KEY`
  - **Value**: Your YouTube API key from `.env` file (if you have one)

#### 2. YouTube OAuth Files:

- **Name**: `CLIENT_SECRET_JSON`
  - **Value**: Copy the ENTIRE contents of `client_secret.json` file

- **Name**: `TOKEN_PICKLE_BASE64`
  - **Value**: Run this command to get the base64 encoded token:
  
  ```powershell
  [Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Users\shivg\OneDrive\Desktop\yt workflow\token.pickle"))
  ```
  
  Copy the output and paste it as the secret value.

---

### Step 3: Verify GitHub Actions is Enabled

1. Go to your repository on GitHub
2. Click on **"Actions"** tab
3. If you see a message about workflows being disabled, click **"I understand my workflows, go ahead and enable them"**
4. You should see the workflow: **"YouTube Shorts Automation"**

---

### Step 4: Test the Workflow Manually (Optional)

Before waiting 6 hours, test it manually:

1. Go to **Actions** tab
2. Click on **"YouTube Shorts Automation"** workflow
3. Click **"Run workflow"** button (top right)
4. Select branch: `main`
5. Click green **"Run workflow"** button

Watch the workflow execute in real-time! It will:
- Set up Python environment
- Install dependencies
- Generate a YouTube Short
- Upload to your channel

---

### Step 5: Check the Schedule

The workflow is configured to run automatically at:
- **00:00 UTC** (7:30 AM IST / 5:00 PM PST)
- **06:00 UTC** (11:30 AM IST / 11:00 PM PST)
- **12:00 UTC** (5:30 PM IST / 5:00 AM PST)
- **18:00 UTC** (11:30 PM IST / 11:00 AM PST)

**Total**: 4 videos per day, automatically!

---

## 📊 Monitoring

### View Execution Logs:
1. Go to **Actions** tab
2. Click on any workflow run
3. Click on the job name to see detailed logs
4. You'll see output from script generation, voice creation, video assembly, and upload

### Check for Errors:
- If a workflow fails, GitHub will show a red ❌
- Click on it to see what went wrong
- Common issues: API quota limits, authentication expiry

---

## 🔧 Customization

### Change Schedule:

Edit `.github/workflows/youtube-automation.yml` and modify the cron schedule:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
  # - cron: '0 */4 * * *'  # Every 4 hours (6 videos/day)
  # - cron: '0 */8 * * *'  # Every 8 hours (3 videos/day)
  # - cron: '0 9,15,21 * * *'  # At 9 AM, 3 PM, 9 PM UTC (3 videos/day)
```

Cron format: `minute hour day month weekday`
- `*/6` = every 6 hours
- `*` = every day, every month, every weekday

Tool to test cron schedules: https://crontab.guru/

---

## ⚠️ Important Notes

### API Quotas:
- **YouTube**: ~6 uploads per day max (free tier)
- **ElevenLabs**: Not needed (using edge-tts now)
- **Pexels**: 200 requests/hour (plenty for 4 videos/day)
- **Gemini**: Check your quota at https://makersuite.google.com/

### GitHub Actions Limits:
- **Free tier**: 2,000 minutes/month
- **Each run**: ~5-8 minutes per video
- **4 videos/day**: ~20-32 minutes/day = ~600-960 minutes/month
- **You're well within the free limit!** ✅

### Token Expiry:
- YouTube `token.pickle` may expire after ~7 days
- If uploads fail, you'll need to re-authenticate and update the `TOKEN_PICKLE_BASE64` secret
- To prevent this, consider using a service account (more advanced setup)

---

## 🚀 Alternative: Deploy to Heroku/Railway/Render (Advanced)

If you want even more control and don't want to worry about token expiry, you can deploy to a cloud platform:

### Option A: Railway (Recommended - Easy)
1. Sign up at https://railway.app/
2. Connect your GitHub repository
3. Add environment variables (API keys)
4. Add a cron job service
5. Free tier: $5 credit/month (usually enough)

### Option B: Render
1. Sign up at https://render.com/
2. Create a "Background Worker" service
3. Connect GitHub repository
4. Add cron job
5. Free tier available

### Option C: Google Cloud Run + Cloud Scheduler
1. Deploy as a container
2. Use Cloud Scheduler to trigger every 6 hours
3. More complex but very reliable
4. Free tier: 2 million requests/month

I can help you set up any of these if GitHub Actions doesn't work for your needs!

---

## 📝 Quick Command Reference

### View your secrets (locally, not actual values):
```powershell
cd "C:\Users\shivg\OneDrive\Desktop\yt workflow"
Get-Content .env
```

### Generate TOKEN_PICKLE_BASE64:
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("token.pickle"))
```

### Test locally before pushing:
```powershell
.\.venv\Scripts\python.exe main.py
```

### Push changes to GitHub:
```powershell
git add .
git commit -m "Update automation settings"
git push origin main
```

---

## 🎉 You're All Set!

Once you complete the setup, GitHub Actions will automatically:
1. ✅ Generate 4 YouTube Shorts per day
2. ✅ Use diverse topics from the 60+ topic pool
3. ✅ Create high-quality voiceovers with edge-tts
4. ✅ Add attractive transparent captions
5. ✅ Include royalty-free background music
6. ✅ Upload to your YouTube channel
7. ✅ Use engaging titles with emojis

All without your PC being on! 🚀

---

**Need help?** If you encounter any issues during setup, let me know which step you're on and I'll help troubleshoot!
