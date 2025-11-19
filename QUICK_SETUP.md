# 🚀 Quick Setup - GitHub Actions Automation

## ⚡ 3-Minute Setup

### Step 1: Add Secrets to GitHub (5 secrets needed)

Go to: https://github.com/shiv989898/Youtube-Automator/settings/secrets/actions

Click **"New repository secret"** and add these one by one:

---

#### Secret 1: GEMINI_API_KEY
```
Get from your .env file - look for: GEMINI_API_KEY=
```

#### Secret 2: PEXELS_API_KEY
```
Get from your .env file - look for: PEXELS_API_KEY=
```

#### Secret 3: PIXABAY_API_KEY
```
Get from your .env file - look for: PIXABAY_API_KEY=
```

#### Secret 4: CLIENT_SECRET_JSON
```powershell
# Run this to get the value:
Get-Content "C:\Users\shivg\OneDrive\Desktop\yt workflow\client_secret.json" -Raw
```
Copy the ENTIRE output (all the JSON text)

#### Secret 5: TOKEN_PICKLE_BASE64
```
gASVBAQAAAAAAACMGWdvb2dsZS5vYXV0aDIuY3JlZGVudGlhbHOUjAtDcmVkZW50aWFsc5STlCmBlH2UKIwFdG9rZW6UjP55YTI5LmEwQVRpNksydV9MalJjOTNaZFdpV0dCMzMwTTNHclpUV0gzQnpjU1ZWdFExdmlZQncyVjhnQTdlNFlyMGZZcEZmTkl2cWpvemhnLUd2ZGtIZVRZVTJKcWhuMl9ENk5iZVJhSndWaFNRU2hNQWFRLWtEaVNRLXh0Y2loSTVxeVU4ZzdUZEVBT0pOM2xWNEE4cnJRb1VHUWRsWDI2eDhkSWhjWmxPY3h2MUNDd296MUxsN3NaYzRwUjJPdDl3MEtXVzljdmxqMC1jVDNhQ2dZS0Fac1NBUkVTRlFIR1gyTWk0MTZ3LWtvVGdXbFhlRGFXMjJGMTd3MDIwN5SMBmV4cGlyeZSMCGRhdGV0aW1llIwIZGF0ZXRpbWWUk5RDCgfpCw4SOAAGvk+UhZRSlIwOX3JlZnJlc2hfdG9rZW6UjGcxLy8wZ0Q5ZHBuSU5DRUJvQ2dZSUFSQUFHQkFTTndGLUw5SXJZY1VNZDI0bjdfLUxZYXVSUlYwM1VTaEh3bjcyRHRnWFB5dFVEU2tlRmN1TFpNYzJXbGVXNjh1bDFvdU5nOUNjb3RZlIwJX2lkX3Rva2VulE6MB19zY29wZXOUXZSMLmh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL2F1dGgveW91dHViZS51cGxvYWSUYYwPX2RlZmF1bHRfc2NvcGVzlE6MD19ncmFudGVkX3Njb3Blc5RdlIwuaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vYXV0aC95b3V0dWJlLnVwbG9hZJRhjApfdG9rZW5fdXJplIwjaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW6UjApfY2xpZW50X2lklIxINDYyNTExOTIzNzIxLTlhZHFnajZwdnF2M3A3ajdvZjU4cnR1NDkzdnNyNjJjLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tlIwOX2NsaWVudF9zZWNyZXSUjCNHT0NTUFgtcUZOVE1SU3Vrc0Vid0Uta05ZZmZfNlE2UC1rN5SMEV9xdW90YV9wcm9qZWN0X2lklE6MC19yYXB0X3Rva2VulE6MFl9lbmFibGVfcmVhdXRoX3JlZnJlc2iUiYwPX3RydXN0X2JvdW5kYXJ5lE6MEF91bml2ZXJzZV9kb21haW6UjA5nb29nbGVhcGlzLmNvbZSMD19jcmVkX2ZpbGVfcGF0aJROjBlfdXNlX25vbl9ibG9ja2luZ19yZWZyZXNolImMCF9hY2NvdW50lIwAlHViLg==
```
Copy this ENTIRE text above (it's already generated for you!)

---

### Step 2: Enable GitHub Actions

1. Go to: https://github.com/shiv989898/Youtube-Automator/actions
2. If prompted, click **"I understand my workflows, go ahead and enable them"**

---

### Step 3: Test It! (Manual Run)

1. Go to: https://github.com/shiv989898/Youtube-Automator/actions
2. Click **"YouTube Shorts Automation"** (left sidebar)
3. Click **"Run workflow"** dropdown (top right)
4. Click green **"Run workflow"** button
5. Watch it run! Takes ~5-8 minutes

---

## ✅ Done! Your automation will now run automatically:

- **Every 6 hours** (4 times per day)
- **Times**: 00:00, 06:00, 12:00, 18:00 UTC
- **No PC needed** - runs on GitHub's servers
- **Completely FREE** - within GitHub's free tier

---

## 📊 Check Results

- **View logs**: https://github.com/shiv989898/Youtube-Automator/actions
- **Your channel**: Check for new videos every 6 hours!

---

## 🔧 Troubleshooting

### If workflow fails:
1. Check the error in Actions tab
2. Most common: API quota exceeded (wait and retry)
3. Token expired: Re-run this command and update TOKEN_PICKLE_BASE64:
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\Users\shivg\OneDrive\Desktop\yt workflow\token.pickle"))
   ```

---

**That's it! You're automated! 🎉**
