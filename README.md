# YouTube Automator

An automated YouTube Shorts and long-form video creation pipeline. The system fetches curated educational topics, generates AI scripts and voiceovers, sources royalty-free visuals and music, assembles everything with MoviePy, and uploads straight to YouTube.

## Features
- **Topic engine:** Offline curated list with 1000+ educational prompts (no Google Trends dependency).
- **AI scripting:** Uses Gemini to expand each topic into a short or long-form script.
- **Voiceover generation:** Microsoft Jenny Neural via `edge-tts` for natural narration.
- **Visual sourcing:** Pulls landscape or vertical clips from Pexels automatically.
- **Music selection:** Randomized pool of 30+ royalty-free tracks with retry logic.
- **Video assembly:** MoviePy pipeline optimized for memory usage (720×1280 @ 24fps for shorts, 1920×1080 for long-form) plus stylized captions for shorts.
- **Auto upload:** YouTube Data API handles publishing with configurable titles, tags, and privacy.
- **Automation hooks:** Batch files, PowerShell loop, and Windows Task Scheduler tasks for hands-free generation.

## Quick Start
1. **Install dependencies**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Configure API keys**
   - Place your `client_secret.json` for YouTube OAuth in the repo root.
   - Populate any required environment variables in `.env` (see `EASY_DEPLOYMENT.md`).
3. **Run Shorts workflow**
   ```powershell
   .\run_shorts.bat
   ```
4. **Run Long-form workflow**
   ```powershell
   .\run_long.bat
   ```

Outputs land in the repo root as `final_video.mp4` / `final_long_video.mp4` plus generated subtitles for long-form.

## Automation Options
- **Continuous loop:** Execute `loop_shorts.ps1` to trigger `run_shorts.bat` every six minutes in an infinite loop.
- **Task Scheduler:**
  - `YouTubeShortsRunner` runs `run_shorts.bat` every 30 minutes.
  - `YouTubeLongRunner` runs `run_long.bat` on the same cadence.
  Use `schtasks /Query /TN "YouTubeShortsRunner"` to verify on Windows.

## Project Structure (highlights)
- `main.py` / `main_long.py`: Orchestrators tying the pipeline together.
- `script_generator.py` / `script_generator_long.py`: Prompts Gemini for scripts.
- `voiceover.py` / `voiceover_long.py`: Handles `edge-tts` voice generation.
- `video_creator.py` / `long_video_creator.py`: Build the final composites.
- `music_finder.py`: Downloads and validates royalty-free music.
- `topic_finder.py`: Supplies curated topics only (no external API calls).
- `run_shorts.bat`, `run_long.bat`: Entry points for automation.

## Deployment Notes
For cloud or CI options, see:
- `QUICK_SETUP.md` for local bootstrap instructions.
- `GITHUB_ACTIONS_SETUP.md`, `EASY_DEPLOYMENT.md`, `FLY_DEPLOYMENT.md`, `RENDER_DEPLOYMENT.md`, and `RAILWAY_SETUP.md` for hosted runtimes.

## Troubleshooting
- **Memory errors**: Shorts render at 720×1280 with vignette disabled; ensure plenty of disk space for temp files.
- **Stuck during long-form creation**: MoviePy may appear idle while it loads all horizontal clips—allow a few minutes.
- **YouTube auth prompts**: Delete `token.pickle` to force a fresh OAuth flow if uploads fail.

## License / Usage
This project automates content creation; ensure your usage complies with the terms of the APIs (Pexels, Google, Microsoft) and that you respect Creative Commons licenses for the bundled music list.
