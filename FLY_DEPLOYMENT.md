# Fly.io Deployment - FREE Forever (No Credit Card)

## Why Fly.io?
- ✅ **No credit card required**
- ✅ 3 free VMs forever
- ✅ 160GB bandwidth/month
- ✅ Perfect for your automation
- ✅ Easy deployment

---

## Step 1: Install Fly CLI

### Windows:
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

Restart your terminal after installation.

### Verify installation:
```powershell
fly version
```

---

## Step 2: Sign Up (No Credit Card)

```powershell
fly auth signup
```

- Use GitHub to sign up (easiest)
- No credit card needed!

---

## Step 3: Prepare Your App

### 3.1: Add credentials to environment

Create `.env` file if not exists:
```powershell
cd "C:\Users\shivg\OneDrive\Desktop\yt workflow"
```

Make sure your `.env` has:
```
PEXELS_API_KEY=your_key
PIXABAY_API_KEY=your_key
GEMINI_API_KEY=your_key
YOUTUBE_API_KEY=your_key
```

### 3.2: Set secrets in Fly:
```powershell
# Set API keys
fly secrets set PEXELS_API_KEY="your_key"
fly secrets set PIXABAY_API_KEY="your_key"
fly secrets set GEMINI_API_KEY="your_key"
fly secrets set YOUTUBE_API_KEY="your_key"

# Set credentials (use output from encode_credentials.py)
fly secrets set CLIENT_SECRET_BASE64="your_base64_string"
fly secrets set TOKEN_PICKLE_BASE64="your_base64_string"
```

---

## Step 4: Deploy Shorts App

```powershell
cd "C:\Users\shivg\OneDrive\Desktop\yt workflow"
fly launch --name youtube-automator-shorts --region iad --no-deploy
```

Answer:
- Copy configuration? **Yes**
- Deploy now? **No**

Edit `fly.toml` to use the cron process:
```toml
[processes]
  cron = "while true; do python main.py && sleep 3600; done"
```

Deploy:
```powershell
fly deploy
```

---

## Step 5: Deploy Long Videos App

Create a second app:
```powershell
fly launch --name youtube-automator-long --region iad --no-deploy
```

Edit the new `fly.toml`:
```toml
[processes]
  cron = "while true; do sleep 1800 && python main_long.py && sleep 1800; done"
```

Set secrets for second app:
```powershell
fly secrets set -a youtube-automator-long PEXELS_API_KEY="your_key"
fly secrets set -a youtube-automator-long PIXABAY_API_KEY="your_key"
fly secrets set -a youtube-automator-long GEMINI_API_KEY="your_key"
fly secrets set -a youtube-automator-long YOUTUBE_API_KEY="your_key"
fly secrets set -a youtube-automator-long CLIENT_SECRET_BASE64="your_base64_string"
fly secrets set -a youtube-automator-long TOKEN_PICKLE_BASE64="your_base64_string"
```

Deploy:
```powershell
fly deploy -a youtube-automator-long
```

---

## Step 6: Monitor

### Check status:
```powershell
fly status
fly status -a youtube-automator-long
```

### View logs:
```powershell
fly logs
fly logs -a youtube-automator-long
```

### Check both apps:
```powershell
fly apps list
```

---

## How It Works:

1. **Shorts app** runs in infinite loop:
   - Execute `main.py`
   - Sleep 3600 seconds (1 hour)
   - Repeat

2. **Long app** runs in infinite loop:
   - Sleep 1800 seconds (30 min offset)
   - Execute `main_long.py`
   - Sleep 1800 seconds
   - Repeat (total 1 hour cycle)

---

## Troubleshooting:

### "Out of memory"
Increase memory in `fly.toml`:
```toml
[[vm]]
  memory_mb = 512
```
(Still free tier)

### "App crashed"
Check logs:
```powershell
fly logs
```

### Update app:
```powershell
fly deploy
```

### Stop app:
```powershell
fly apps stop youtube-automator-shorts
```

### Restart app:
```powershell
fly apps restart youtube-automator-shorts
```

---

## Cost Breakdown:

- **2 apps × 256MB RAM** = FREE ✅
- **Your bandwidth usage** = ~50GB/month = FREE ✅
- **Always-on VMs** = FREE ✅

**Total: $0/month forever**

---

## Commands Cheat Sheet:

```powershell
# Deploy
fly deploy

# View logs (live)
fly logs

# Check status
fly status

# SSH into machine
fly ssh console

# Scale (if needed)
fly scale memory 512

# List all apps
fly apps list

# Destroy app
fly apps destroy youtube-automator-shorts
```

---

## Next Steps:

1. Install Fly CLI
2. Sign up (no credit card)
3. Run encode_credentials.py to get base64 strings
4. Deploy both apps
5. Monitor logs
6. Videos upload automatically every hour!

---

## Advantages over other platforms:

| Feature | Fly.io | Render | Railway | Oracle |
|---------|--------|--------|---------|--------|
| No credit card | ✅ | ❌ | ❌ | ❌ |
| Free forever | ✅ | ⚠️ Limited | ❌ | ✅ |
| Easy setup | ✅ | ✅ | ✅ | ❌ |
| Unlimited execution | ✅ | ❌ | ❌ | ✅ |
| No server management | ✅ | ✅ | ✅ | ❌ |

**Fly.io is your best option!**
