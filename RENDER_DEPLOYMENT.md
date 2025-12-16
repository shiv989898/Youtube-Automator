# Deploy YouTube Automator to Render.com

## Why Render.com?
- **Free Tier**: 750 hours/month of compute time
- **Cron Jobs**: Built-in scheduled task support
- **Easy Setup**: Connect directly to GitHub
- **Persistent Storage**: Keep credentials and generated files

## Prerequisites
- GitHub account with your repository
- Render.com account (sign up at https://render.com)
- All your API keys and credentials ready

---

## Step 1: Prepare Your Repository

### 1.1 Create `render.yaml` in your project root

This file tells Render how to deploy your app.

```yaml
services:
  - type: cron
    name: youtube-shorts-automator
    env: python
    schedule: "0 * * * *"  # Every hour at minute 0
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python main.py"
    
  - type: cron
    name: youtube-long-automator
    env: python
    schedule: "30 * * * *"  # Every hour at minute 30
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python main_long.py"
```

### 1.2 Update `requirements.txt` to include all dependencies

Make sure your `requirements.txt` has:
```txt
requests
python-dotenv
urllib3<2.0.0
pytrends
moviepy
Pillow
google-auth-oauthlib
google-auth
google-api-python-client
edge-tts
gTTS
pyttsx3
google-generativeai
imageio-ffmpeg
```

### 1.3 Push changes to GitHub
```bash
cd "C:\Users\shivg\OneDrive\Desktop\yt workflow"
git add render.yaml requirements.txt
git commit -m "Add Render.com deployment config"
git push origin main
```

---

## Step 2: Create Render.com Account

1. Go to https://render.com
2. Click **"Get Started"**
3. Sign up with GitHub (recommended for easy repo connection)
4. Authorize Render to access your GitHub repositories

---

## Step 3: Deploy Cron Jobs on Render

### 3.1 Create First Cron Job (Shorts - Hourly)

1. From Render Dashboard, click **"New +"** → **"Cron Job"**

2. **Connect Repository**:
   - Select your GitHub account
   - Choose `Youtube-Automator` repository
   - Click **"Connect"**

3. **Configure Job**:
   - **Name**: `youtube-shorts-hourly`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Schedule**: `0 * * * *` (every hour)

4. Click **"Advanced"** and add environment variables (see Step 4)

5. Click **"Create Cron Job"**

### 3.2 Create Second Cron Job (Long Videos)

Repeat the same process:
1. Click **"New +"** → **"Cron Job"**
2. Connect same repository
3. **Configure Job**:
   - **Name**: `youtube-long-hourly`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main_long.py`
   - **Schedule**: `30 * * * *` (every hour at :30)
4. Add same environment variables
5. Click **"Create Cron Job"**

---

## Step 4: Configure Environment Variables

For **EACH** cron job, add these environment variables:

### How to Add Variables:
1. Go to your cron job dashboard
2. Click **"Environment"** tab
3. Add each variable below:

### Required Variables:

| Variable Name | Description | Example |
|--------------|-------------|---------|
| `PEXELS_API_KEY` | Your Pexels API key | `abc123...` |
| `PIXABAY_API_KEY` | Your Pixabay API key | `123456...` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `YOUTUBE_API_KEY` | YouTube Data API key | `AIza...` |

### 4.1 Add Google OAuth Credentials (client_secret.json)

Since `client_secret.json` is a file, you need to:

**Option A: Use Secret File (Recommended)**
1. In Environment tab, click **"Add Secret File"**
2. **Filename**: `client_secret.json`
3. Paste your entire `client_secret.json` content
4. Click **"Save"**

**Option B: Base64 Encode (Alternative)**
```bash
# On your local machine:
base64 client_secret.json
```
Then add as environment variable:
- Variable: `CLIENT_SECRET_BASE64`
- Value: (paste base64 output)

Modify your code to decode:
```python
import base64
import os

if os.getenv('CLIENT_SECRET_BASE64'):
    secret_content = base64.b64decode(os.getenv('CLIENT_SECRET_BASE64'))
    with open('client_secret.json', 'wb') as f:
        f.write(secret_content)
```

### 4.2 Add YouTube OAuth Token (token.pickle)

Since you already have `token.pickle`:

1. Base64 encode it:
```bash
base64 token.pickle
```

2. Add environment variable:
   - Variable: `TOKEN_PICKLE_BASE64`
   - Value: (paste base64 output)

3. Modify your code to decode it on startup (add to `main.py` and `main_long.py`):

```python
import base64
import os

# Decode token.pickle if provided as env var
if os.getenv('TOKEN_PICKLE_BASE64'):
    token_content = base64.b64decode(os.getenv('TOKEN_PICKLE_BASE64'))
    with open('token.pickle', 'wb') as f:
        f.write(token_content)
```

---

## Step 5: Install System Dependencies (FFmpeg)

Render's Python environment needs FFmpeg for MoviePy.

### Update your Build Command:

Instead of just `pip install -r requirements.txt`, use:

```bash
apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt
```

Or create `render-build.sh`:
```bash
#!/bin/bash
apt-get update
apt-get install -y ffmpeg fonts-dejavu-core
pip install -r requirements.txt
```

Make it executable and update Render config:
```bash
chmod +x render-build.sh
```

**Build Command**: `./render-build.sh`

---

## Step 6: Handle File Persistence

Render cron jobs are **ephemeral** (temporary). Files don't persist between runs.

### Solutions:

**Option A: Use Render Disk (Paid - $1/GB/month)**
1. In your cron job settings
2. Add a **Persistent Disk**
3. Mount path: `/data`
4. Update your code to save files to `/data/`

**Option B: Accept Ephemeral (Recommended for your use case)**
Since you upload videos immediately, you don't need persistence. Each run:
1. Downloads visuals
2. Creates video
3. Uploads to YouTube
4. Deletes everything

No changes needed!

---

## Step 7: Test Your Deployment

### 7.1 Manual Test Run
1. Go to your cron job in Render dashboard
2. Click **"Trigger Run"** (forces immediate execution)
3. Watch the **Logs** tab for output
4. Check YouTube for uploaded video

### 7.2 Check Logs
- Click **"Logs"** tab in your cron job
- See real-time output
- Debug any errors

### 7.3 Verify Schedule
- First run happens at next scheduled time (e.g., top of the hour)
- Check **"Events"** tab for execution history

---

## Step 8: Monitor and Maintain

### View Usage:
1. Render Dashboard → **"Account Settings"** → **"Usage"**
2. Monitor free tier hours (750/month)
3. Each video generation takes ~15-30 minutes

### Expected Usage:
- 2 jobs × 24 runs/day × 30 min/run = 1,440 hours/month
- **You'll exceed free tier** with hourly runs

### Optimization Options:

**Option 1: Reduce Frequency**
Change schedule to every 2 hours:
```yaml
schedule: "0 */2 * * *"  # Shorts every 2 hours
schedule: "30 */2 * * *"  # Long every 2 hours offset
```
Usage: 720 hours/month (within free tier)

**Option 2: Alternating (Single Job)**
Create one job that alternates:
```python
import datetime
hour = datetime.datetime.now().hour
if hour % 2 == 0:
    # Run shorts
    exec(open('main.py').read())
else:
    # Run long
    exec(open('main_long.py').read())
```
Schedule: `0 * * * *` (every hour)
Usage: 720 hours/month

**Option 3: Upgrade**
- Starter plan: $7/month for 600 hours
- Combine with free tier: 1,350 hours/month total

---

## Step 9: Alternative Schedule Patterns

### Daily Instead of Hourly:
```yaml
# Once per day at 9 AM UTC
schedule: "0 9 * * *"

# Twice per day (9 AM and 9 PM UTC)
schedule: "0 9,21 * * *"

# Every 6 hours
schedule: "0 */6 * * *"
```

### Weekdays Only:
```yaml
# Monday-Friday at 9 AM
schedule: "0 9 * * 1-5"
```

---

## Troubleshooting

### Issue: "Module not found"
- Check `requirements.txt` includes all dependencies
- Verify Build Command runs successfully
- Check logs during build phase

### Issue: "client_secret.json not found"
- Ensure you added it as Secret File or environment variable
- Check file decoding code runs before authentication

### Issue: "FFmpeg not found"
- Update Build Command to install FFmpeg
- Use: `apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt`

### Issue: Videos not uploading
- Check `token.pickle` is decoded correctly
- Verify YouTube API credentials are valid
- Check quota limits on YouTube API

### Issue: Out of memory
- Reduce video resolution in `long_video_creator.py`
- Lower `TARGET_W` and `TARGET_H` to 960x540
- Reduce number of visuals processed

---

## Summary Checklist

- [ ] Create `render.yaml` configuration
- [ ] Update `requirements.txt` with all dependencies
- [ ] Push changes to GitHub
- [ ] Create Render.com account
- [ ] Create cron job for shorts
- [ ] Create cron job for long videos
- [ ] Add all environment variables
- [ ] Add `client_secret.json` as secret file
- [ ] Add `token.pickle` as base64 env variable
- [ ] Update build command to install FFmpeg
- [ ] Trigger manual test run
- [ ] Verify first scheduled run
- [ ] Monitor usage and adjust schedule if needed

---

## Cost Comparison

| Platform | Free Tier | Your Usage | Status |
|----------|-----------|------------|--------|
| **GitHub Actions** | 2,000-3,000 min/month | Exceeded | ❌ Over limit |
| **Render.com** | 750 hours/month | ~1,440 hours | ⚠️ Over (need to reduce frequency) |
| **GitLab CI/CD** | 400 min/month | ~1,440 min | ❌ Would exceed |
| **Railway.app** | 500 hours + $5 credit | ~1,440 hours | ⚠️ Over free tier |
| **Oracle Cloud (VM)** | 2 VMs forever free | Unlimited cron | ✅ Best for 24/7 |

**Recommendation**: 
- For hourly runs: **Oracle Cloud VM** with cron (free forever)
- For reduced schedule (every 2-3 hours): **Render.com** works within free tier
- For simplicity: **Render.com** with reduced frequency

---

## Next Steps After Deployment

1. Let it run for 24 hours
2. Check YouTube channel for uploads
3. Monitor Render logs for any errors
4. Adjust schedule based on usage
5. Consider Oracle Cloud VM if you want true hourly runs for free

Need help with any step? Let me know!
