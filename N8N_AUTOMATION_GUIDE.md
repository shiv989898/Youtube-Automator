# N8N Automation Workflow for YouTube Shorts Creation

## Overview
This document provides complete instructions for creating an n8n automation workflow that automatically generates and uploads YouTube Shorts videos. The workflow uses Python scripts to create AI-powered video content with voiceovers, captions, visuals, and background music.

---

## Prerequisites

### 1. System Requirements
- **n8n** installed and running (self-hosted or n8n cloud)
- **Python 3.11+** installed on the system where n8n runs
- **Git** for cloning the repository
- **FFmpeg** for video processing (required by MoviePy)

### 2. Required API Keys
Collect these API keys before starting:
- **Google Gemini API Key** - For AI script generation (https://makersuite.google.com/app/apikey)
- **ElevenLabs API Key** - For human-like voiceover (https://elevenlabs.io/)
- **Pexels API Key** - For video visuals (https://www.pexels.com/api/)
- **YouTube API Credentials** - For video uploads (https://console.cloud.google.com/)
  - OAuth 2.0 Client ID
  - Client Secret
  - Download `client_secret.json` file

### 3. Repository Setup
- Repository URL: `https://github.com/shiv989898/Youtube-Automator`
- Branch: `main`
- Local path: `/path/to/yt workflow/` (adjust for your system)

---

## Project Structure

```
yt workflow/
├── .env                          # Environment variables (API keys)
├── .venv/                        # Python virtual environment
├── client_secret.json            # YouTube OAuth credentials
├── token.pickle                  # YouTube authentication token (auto-generated)
├── main.py                       # Main orchestrator script
├── topic_finder.py               # Finds trending topics
├── script_generator.py           # Generates AI scripts (Gemini)
├── voiceover.py                  # Creates voiceover (ElevenLabs)
├── music_finder.py               # Downloads copyright-free music
├── visuals.py                    # Downloads stock videos (Pexels)
├── caption_generator.py          # Creates video captions
├── video_creator.py              # Assembles final video
├── youtube_uploader.py           # Uploads to YouTube
├── requirements.txt              # Python dependencies
├── final_video.mp4               # Output video (auto-generated)
└── N8N_AUTOMATION_GUIDE.md       # This documentation
```

---

## Step-by-Step N8N Workflow Setup

### STEP 1: Create New Workflow in N8N

1. Open n8n interface
2. Click **"New Workflow"**
3. Name it: `"YouTube Shorts Auto Generator"`
4. Save the workflow

---

### STEP 2: Add Schedule Trigger Node

**Node Type:** `Schedule Trigger`

**Configuration:**
```json
{
  "rule": {
    "interval": [
      {
        "field": "hours",
        "hoursInterval": 6
      }
    ]
  }
}
```

**Purpose:** Runs the workflow every 6 hours to create a new YouTube Short

**Alternative Schedule Options:**
- Daily at specific time: Use "Days" interval with hour set to desired time
- Multiple times per day: Use "Hours" with 4, 6, 8, or 12-hour intervals
- Once per week: Use "Weeks" interval

---

### STEP 3: Add Execute Command Node (Setup Environment)

**Node Type:** `Execute Command`
**Node Name:** `Setup Python Environment`

**Configuration:**
```json
{
  "command": "cd /path/to/yt workflow && source .venv/bin/activate || .venv\\Scripts\\activate",
  "cwd": "/path/to/yt workflow"
}
```

**For Windows:**
```powershell
cd "C:\Users\shivg\OneDrive\Desktop\yt workflow" && .venv\Scripts\activate
```

**For Linux/Mac:**
```bash
cd /path/to/yt workflow && source .venv/bin/activate
```

**Purpose:** Activates the Python virtual environment

---

### STEP 4: Add Execute Command Node (Run Main Script)

**Node Type:** `Execute Command`
**Node Name:** `Generate and Upload YouTube Short`

**Configuration:**

**For Windows:**
```json
{
  "command": "python",
  "arguments": "main.py",
  "cwd": "C:\\Users\\shivg\\OneDrive\\Desktop\\yt workflow"
}
```

**For Linux/Mac:**
```json
{
  "command": "python3",
  "arguments": "main.py",
  "cwd": "/path/to/yt workflow"
}
```

**Advanced Settings:**
- **Timeout:** `600000` (10 minutes - video creation takes time)
- **Environment Variables:** Add if needed (or use .env file)

**Purpose:** Runs the main Python script that generates and uploads the video

---

### STEP 5: Add IF Node (Check Success)

**Node Type:** `IF`
**Node Name:** `Check Video Creation Success`

**Configuration:**
```json
{
  "conditions": {
    "boolean": [
      {
        "value1": "={{ $json.code }}",
        "operation": "equal",
        "value2": 0
      }
    ]
  }
}
```

**Purpose:** Checks if the Python script executed successfully (exit code 0)

---

### STEP 6A: Add Notification Node (Success Path)

**Node Type:** `Email` or `Discord` or `Slack` or `Telegram`
**Node Name:** `Send Success Notification`

**Connect from:** IF node → TRUE output

**Email Configuration Example:**
```json
{
  "fromEmail": "your-email@gmail.com",
  "toEmail": "your-email@gmail.com",
  "subject": "✅ YouTube Short Published Successfully",
  "text": "A new YouTube Short has been created and uploaded!\n\nWorkflow: {{ $workflow.name }}\nExecution Time: {{ $now }}\nVideo ID: Check YouTube Studio",
  "html": "<h2>✅ Success!</h2><p>Your automated YouTube Short has been published.</p>"
}
```

**Discord Configuration Example:**
```json
{
  "webhookUrl": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL",
  "content": "✅ New YouTube Short published successfully! Check your channel."
}
```

---

### STEP 6B: Add Notification Node (Error Path)

**Node Type:** `Email` or `Discord` or `Slack` or `Telegram`
**Node Name:** `Send Error Notification`

**Connect from:** IF node → FALSE output

**Configuration:**
```json
{
  "subject": "❌ YouTube Short Creation Failed",
  "text": "The YouTube Shorts automation encountered an error.\n\nError Details:\n{{ $json.stderr }}\n\nPlease check the logs.",
  "toEmail": "your-email@gmail.com"
}
```

---

### STEP 7: Add Error Trigger Node (Optional)

**Node Type:** `Error Trigger`
**Node Name:** `Catch Workflow Errors`

**Configuration:**
- This node catches any unhandled errors in the workflow
- Connect it to a notification node to alert you of critical failures

---

## Environment Variables Setup (.env file)

Create or update the `.env` file in the project directory with all API keys:

```env
# YouTube API
YOUTUBE_API_KEY="YOUR_YOUTUBE_API_KEY"
CLIENT_SECRETS_FILE="client_secret.json"

# Pexels API (for video visuals)
PEXELS_API_KEY="YOUR_PEXELS_API_KEY"

# Pixabay API (fallback for visuals)
PIXABAY_API_KEY="YOUR_PIXABAY_API_KEY"

# Gemini API (for script generation)
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# ElevenLabs API (for human-like voiceover)
ELEVENLABS_API_KEY="YOUR_ELEVENLABS_API_KEY"
```

**Security Notes:**
- Never commit `.env` file to Git (already in .gitignore)
- Keep API keys secure
- Rotate keys regularly
- Use environment-specific keys for testing vs production

---

## Python Dependencies Installation

Before running the workflow, ensure all Python packages are installed:

```bash
# Navigate to project directory
cd "C:\Users\shivg\OneDrive\Desktop\yt workflow"

# Create virtual environment (if not exists)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Requirements.txt contents:**
```txt
pytrends
pyttsx3
moviepy==1.0.3
Pillow==9.5.0
imageio-ffmpeg==0.4.9
requests
google-api-python-client
google-auth-oauthlib
python-dotenv
google-generativeai
numpy
```

---

## YouTube API Setup (Critical)

### 1. Create Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Create new project: "YouTube Shorts Automation"
3. Enable APIs:
   - YouTube Data API v3
   - YouTube Analytics API (optional)

### 2. Create OAuth 2.0 Credentials
1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth 2.0 Client ID**
3. Application type: **Desktop app**
4. Name: "YouTube Shorts Automation"
5. Download `client_secret.json`
6. Place file in project root directory

### 3. Configure OAuth Consent Screen
1. Go to **APIs & Services → OAuth consent screen**
2. User Type: **External**
3. Add your email as a test user
4. Add scopes:
   - `https://www.googleapis.com/auth/youtube.upload`
   - `https://www.googleapis.com/auth/youtube`

### 4. First-Time Authentication
The first run will open a browser for authentication:
1. Run the workflow manually first
2. Browser will open asking for permissions
3. Grant access to your YouTube account
4. A `token.pickle` file will be created
5. Subsequent runs will use this token automatically

**Important:** The `token.pickle` file must remain in the project directory for automated uploads.

---

## N8N Workflow JSON Configuration

Here's the complete workflow in JSON format that can be imported into n8n:

```json
{
  "name": "YouTube Shorts Auto Generator",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "hours",
              "hoursInterval": 6
            }
          ]
        }
      },
      "name": "Schedule Every 6 Hours",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "command": "python main.py",
        "cwd": "C:\\Users\\shivg\\OneDrive\\Desktop\\yt workflow"
      },
      "name": "Generate YouTube Short",
      "type": "n8n-nodes-base.executeCommand",
      "typeVersion": 1,
      "position": [450, 300],
      "timeout": 600000
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.code }}",
              "operation": "equal",
              "value2": 0
            }
          ]
        }
      },
      "name": "Check Success",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [650, 300]
    },
    {
      "parameters": {
        "authentication": "oauth2",
        "select": "channel",
        "channelId": "",
        "content": "✅ New YouTube Short published successfully at {{ $now.format('YYYY-MM-DD HH:mm:ss') }}!"
      },
      "name": "Success Notification",
      "type": "n8n-nodes-base.discord",
      "typeVersion": 1,
      "position": [850, 200]
    },
    {
      "parameters": {
        "authentication": "oauth2",
        "select": "channel",
        "channelId": "",
        "content": "❌ YouTube Short creation failed!\nError: {{ $json.stderr }}"
      },
      "name": "Error Notification",
      "type": "n8n-nodes-base.discord",
      "typeVersion": 1,
      "position": [850, 400]
    }
  ],
  "connections": {
    "Schedule Every 6 Hours": {
      "main": [
        [
          {
            "node": "Generate YouTube Short",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Generate YouTube Short": {
      "main": [
        [
          {
            "node": "Check Success",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Check Success": {
      "main": [
        [
          {
            "node": "Success Notification",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "Error Notification",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": true,
  "settings": {},
  "id": "1"
}
```

---

## Workflow Execution Flow

```
1. SCHEDULE TRIGGER (Every 6 hours)
   ↓
2. EXECUTE COMMAND (Run Python script)
   ↓
   - Find trending topic
   - Generate AI script (30-40 seconds)
   - Create voiceover with ElevenLabs
   - Download copyright-free music
   - Download stock video clips
   - Generate captions
   - Assemble video with MoviePy
   - Upload to YouTube
   ↓
3. CHECK IF SUCCESS (Exit code = 0?)
   ↓
   ├─→ TRUE: Send Success Notification
   └─→ FALSE: Send Error Notification
```

---

## Testing the Workflow

### Manual Test Run
1. In n8n, click **"Execute Workflow"** button
2. Watch the execution progress
3. Check each node for output/errors
4. Verify video uploaded to YouTube
5. Check for notifications

### Debugging Steps
1. **Check Python execution:**
   ```bash
   cd "C:\Users\shivg\OneDrive\Desktop\yt workflow"
   .venv\Scripts\activate
   python main.py
   ```

2. **Check API keys:**
   - Verify all keys in `.env` file
   - Test each API individually

3. **Check file permissions:**
   - n8n must have read/write access to project directory
   - Check Python virtual environment activation

4. **Check logs:**
   - n8n execution logs
   - Python script output
   - YouTube API quota usage

---

## Advanced Configuration Options

### 1. Customize Video Schedule
Modify the Schedule Trigger to match your posting strategy:
- **Optimal times:** 12 PM, 6 PM, 9 PM (when audiences are active)
- **Frequency:** 2-4 times per day for maximum reach
- **Time zones:** Set based on target audience location

### 2. Add Video Analytics Tracking
Add a node after upload to:
- Log video ID to database
- Track performance metrics
- Create analytics reports

### 3. Content Moderation
Add a node before upload to:
- Check script for inappropriate content
- Verify video length (under 60 seconds)
- Ensure copyright-free music was used

### 4. Batch Processing
Modify workflow to:
- Generate multiple videos in one run
- Queue uploads throughout the day
- Distribute topics across categories

### 5. Backup and Recovery
Add nodes to:
- Save video files to cloud storage
- Backup `.env` and configuration
- Create restore points

---

## Common Issues and Solutions

### Issue 1: YouTube Upload Fails
**Symptoms:** "Upload limit exceeded" error
**Solution:**
- YouTube API has daily quota limits
- Default quota: 10,000 units/day
- Video upload: ~1,600 units
- Max ~6 uploads per day
- Request quota increase if needed

### Issue 2: Python Environment Not Found
**Symptoms:** "python: command not found"
**Solution:**
- Verify Python installation: `python --version`
- Check virtual environment path
- Use full path to Python executable
- Windows: `C:\Users\shivg\OneDrive\Desktop\yt workflow\.venv\Scripts\python.exe`

### Issue 3: API Key Errors
**Symptoms:** "API key invalid" or "Unauthorized"
**Solution:**
- Verify all API keys in `.env`
- Check for extra spaces or quotes
- Regenerate keys if expired
- Ensure billing is enabled (for paid APIs)

### Issue 4: Video Creation Timeout
**Symptoms:** Node execution times out
**Solution:**
- Increase timeout in Execute Command node
- Recommended: 600000ms (10 minutes)
- Optimize video processing (lower resolution if needed)

### Issue 5: Music Download Fails
**Symptoms:** "Could not find background music"
**Solution:**
- Music sources may timeout occasionally
- Video will still be created without music
- Check internet connection
- Try different music source URLs

### Issue 6: Caption Errors
**Symptoms:** "Could not add captions"
**Solution:**
- Captions use PIL/Pillow library
- Verify Pillow is installed: `pip install Pillow`
- Check font availability on system
- Video will continue without captions if they fail

---

## Monitoring and Maintenance

### Daily Checks
- [ ] Verify videos are uploading successfully
- [ ] Check YouTube Studio for new shorts
- [ ] Monitor API quota usage
- [ ] Review any error notifications

### Weekly Maintenance
- [ ] Update trending topics list if needed
- [ ] Check ElevenLabs character usage
- [ ] Review video performance metrics
- [ ] Test voice quality and adjust settings

### Monthly Tasks
- [ ] Update Python dependencies: `pip install --upgrade -r requirements.txt`
- [ ] Rotate API keys for security
- [ ] Review and optimize video content strategy
- [ ] Check for n8n updates

---

## Production Deployment Checklist

Before running in production:

- [ ] All API keys configured in `.env`
- [ ] YouTube OAuth completed (`token.pickle` exists)
- [ ] Python virtual environment activated
- [ ] All dependencies installed
- [ ] Test run completed successfully
- [ ] Notifications configured
- [ ] Schedule set to desired frequency
- [ ] Error handling tested
- [ ] Backup strategy in place
- [ ] Monitoring alerts configured

---

## Security Best Practices

1. **API Key Management:**
   - Store keys in `.env` file only
   - Never commit `.env` to version control
   - Use different keys for dev/prod environments
   - Rotate keys every 90 days

2. **Access Control:**
   - Limit n8n access to authorized users only
   - Use strong passwords for n8n admin
   - Enable 2FA where available
   - Restrict file system permissions

3. **Data Privacy:**
   - Don't log sensitive information
   - Secure webhook URLs
   - Use HTTPS for all API calls
   - Comply with YouTube's Terms of Service

4. **Backup:**
   - Regular backups of `.env` file (secure location)
   - Backup `token.pickle` file
   - Export n8n workflow regularly
   - Version control for Python scripts (excluding secrets)

---

## Performance Optimization

### Video Generation Speed
- Current: ~3-5 minutes per video
- Factors:
  - API response times (Gemini, ElevenLabs)
  - Video download speed (Pexels)
  - Video rendering (MoviePy)
  - Upload speed to YouTube

### Optimization Tips
1. Use faster internet connection
2. Optimize video resolution (1080x1920 is sufficient)
3. Reduce number of caption segments
4. Use SSD for faster file I/O
5. Consider GPU acceleration for rendering

### Resource Usage
- CPU: Moderate (video rendering)
- RAM: 2-4GB recommended
- Disk: 500MB per video (temporary)
- Network: ~50-100MB per video

---

## Scaling the Workflow

### Running Multiple Instances
To create more videos:
1. Duplicate the workflow in n8n
2. Use different schedules (stagger times)
3. Ensure YouTube API quota can handle volume
4. Monitor for duplicate content

### Multi-Channel Support
To post to multiple YouTube channels:
1. Create separate workflows per channel
2. Use different `client_secret.json` files
3. Generate separate `token.pickle` files
4. Organize by folder structure

### Content Variety
Enhance content diversity:
1. Add more topics to `topic_finder.py`
2. Use different voice IDs in `voiceover.py`
3. Vary music tracks
4. Experiment with caption styles

---

## Support and Resources

### Documentation Links
- n8n Documentation: https://docs.n8n.io/
- YouTube API: https://developers.google.com/youtube/v3
- ElevenLabs API: https://elevenlabs.io/docs
- Google Gemini: https://ai.google.dev/docs
- Pexels API: https://www.pexels.com/api/documentation/

### Python Libraries
- MoviePy: https://zulko.github.io/moviepy/
- Pillow: https://pillow.readthedocs.io/
- Google API Client: https://github.com/googleapis/google-api-python-client

### Community
- n8n Community: https://community.n8n.io/
- YouTube Creators: https://www.youtube.com/creators/

---

## Conclusion

This workflow automates the entire YouTube Shorts creation and publishing process:
- **Generates** unique AI-powered scripts
- **Creates** realistic voiceovers with emotions
- **Adds** professional captions and visuals
- **Includes** copyright-free background music
- **Uploads** automatically to YouTube
- **Notifies** you of success or failures

The system runs unattended, creating engaging 30-40 second YouTube Shorts on schedule, helping you maintain a consistent posting schedule without manual effort.

---

## Version History

- **v1.0** (2025-11-12): Initial documentation
  - Complete n8n workflow setup
  - All API integrations
  - Error handling and notifications
  - Security best practices

---

## License and Attribution

- **Project Repository:** https://github.com/shiv989898/Youtube-Automator
- **Music Attribution:** Uses Creative Commons licensed music from Free Music Archive
- **Video Clips:** From Pexels (free for commercial use)
- **AI Services:** Powered by Google Gemini and ElevenLabs

---

**END OF DOCUMENTATION**
