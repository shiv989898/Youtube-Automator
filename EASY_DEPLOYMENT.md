# Free Cron Trigger for GitHub Actions

## The Problem:
- GitHub Actions: 3000 minutes/month limit exceeded

## The Solution:
Use a free external cron service to trigger your GitHub Actions workflow via repository dispatch.

---

## Setup (10 minutes):

### Step 1: Update GitHub Workflow

Add repository dispatch trigger to `.github/workflows/youtube-automation.yml`:

```yaml
on:
  repository_dispatch:
    types: [trigger-short, trigger-long]
  schedule:
    - cron: '0 * * * *'
```

### Step 2: Create Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Select scopes: `repo` (full control)
4. Copy token (save it!)

### Step 3: Use cron-job.org (FREE)

1. Go to https://cron-job.org/en/
2. Sign up (free account)
3. Create 2 cron jobs:

**Job 1 - Trigger Shorts (Every hour at :00):**
- URL: `https://api.github.com/repos/shiv989898/Youtube-Automator/dispatches`
- Method: `POST`
- Headers:
  ```
  Authorization: Bearer YOUR_GITHUB_TOKEN
  Accept: application/vnd.github.v3+json
  Content-Type: application/json
  ```
- Body:
  ```json
  {"event_type": "trigger-short"}
  ```
- Schedule: `0 * * * *`

**Job 2 - Trigger Long Videos (Every hour at :30):**
- Same URL
- Same headers
- Body: `{"event_type": "trigger-long"}`
- Schedule: `30 * * * *`

### Step 4: Update Workflow Logic

Modify `.github/workflows/youtube-automation.yml` to handle dispatch events.

---

## Alternative: Use EasyCron (FREE)

1. Go to https://www.easycron.com
2. Sign up (100 cron jobs free)
3. Create jobs same as above

---

## Or Just Use Your LOCAL Computer + Task Scheduler

**Windows Task Scheduler** (Completely FREE, no limits):

1. Open Task Scheduler
2. Create Basic Task → "YouTube Shorts Generator"
3. Trigger: Daily, repeat every 1 hour
4. Action: Start a program
   - Program: `C:\Users\shivg\OneDrive\Desktop\yt workflow\.venv\Scripts\python.exe`
   - Arguments: `main.py`
   - Start in: `C:\Users\shivg\OneDrive\Desktop\yt workflow`
5. Create another task for `main_long.py` offset by 30 minutes

**This runs on YOUR computer when it's on - completely free, no cloud needed!**

---

## Best Option Based on Your Needs:

| Option | Free? | Setup | Best For |
|--------|-------|-------|----------|
| **Windows Task Scheduler** | ✅ Forever | 5 min | Computer always on |
| **cron-job.org + GitHub** | ✅ Forever | 10 min | Want cloud automation |
| **Railway.app** | $5/month | 5 min | Easy cloud solution |
| **Oracle Cloud VM** | ✅ Forever | 30 min | Full control |

---

Which would you prefer?
