# YouTube Automator

YouTube Automator is a Python workflow that can generate and upload both YouTube Shorts and long-form educational videos. It picks a topic, writes a script with Gemini, generates voiceover audio, downloads royalty-free visuals and music, renders the final video with MoviePy, and uploads it to YouTube.

This README is written to help someone clone the repository on a new computer and run it successfully from scratch.

## What this project does

The pipeline supports two flows:

- **Shorts flow** via [main.py](main.py)
- **Long-form flow** via [main_long.py](main_long.py)

Typical output files:

- `final_video.mp4` for Shorts
- `final_long_video.mp4` for long-form videos
- `final_long_video.srt` for long-form subtitles

## Features

- Topic generation for educational/fact-style content
- AI script generation using Gemini
- Voice generation with `edge-tts`, plus fallback to `gTTS` and `pyttsx3`
- Stock video selection from Pexels and Pixabay
- Music download and background audio support
- Automatic video rendering with MoviePy
- Automatic YouTube upload through the YouTube Data API
- Windows automation helpers via batch files and PowerShell scripts

## Requirements

Before running this project on any PC, make sure you have:

- **Python 3.10 or 3.11** installed
- **Git** installed
- A stable internet connection
- A Google account with access to YouTube uploads
- Your own API credentials for the services you want to use

## Required accounts and API access

To run the full project, you should prepare these:

1. **Google Gemini API key**
   - Used for script generation
   - Stored in `.env` as `GEMINI_API_KEY` or `GEMINI_API_KEYS`

2. **Pexels API key**
   - Used for stock video downloads
   - Stored in `.env` as `PEXELS_API_KEY`

3. **Pixabay API key**
   - Used as a fallback source for stock videos
   - Stored in `.env` as `PIXABAY_API_KEY`

4. **YouTube OAuth credentials**
   - Download your OAuth desktop app credentials JSON from Google Cloud
   - Save it in the repository root as `client_secret.json`

## Exact setup instructions for a new PC

### 1) Clone the repository

Windows / macOS / Linux:

```bash
git clone https://github.com/shiv989898/Youtube-Automator.git
cd Youtube-Automator
```

### 2) Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once in a PowerShell window:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**Windows (Command Prompt):**

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Create your environment file

Copy the example file:

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Windows (Command Prompt):**

```bat
copy .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

Then edit `.env` and add your real values.

Example:

```env
GEMINI_API_KEY=your_gemini_key_here
PEXELS_API_KEY=your_pexels_key_here
PIXABAY_API_KEY=your_pixabay_key_here
YOUTUBE_API_KEY=optional_if_needed
```

### 5) Add your YouTube OAuth file

Place your Google OAuth desktop app credentials file in the project root as:

```text
client_secret.json
```

This file is required for uploading videos to YouTube.

### 6) First-time YouTube authentication

On the first successful upload attempt:

- A browser window will open
- You will log in to your Google account
- You will approve YouTube upload access
- The project will save `token.pickle` locally for future uploads

You do **not** need to create `token.pickle` manually. It is generated automatically.

## How to run the project

You can run the project either with Python directly or with the included launcher scripts.

### Option A: Run directly with Python

This is the most reliable option on any PC.

#### Run Shorts

```bash
python main.py
```

#### Run long-form

```bash
python main_long.py
```

On macOS or Linux, if `python` does not point to the virtual environment interpreter, use:

```bash
python3 main.py
python3 main_long.py
```

### Option B: Use the included Windows launcher files

These now work relative to the repository folder and are safe to use on any Windows PC after setup.

#### Run Shorts on Windows

```bat
run_shorts.bat
```

#### Run long-form on Windows

```bat
run_long.bat
```

## What happens when you run it

### Shorts flow

When you run [main.py](main.py), the project will:

1. Pick a topic
2. Generate a short script
3. Clean the script for narration
4. Generate voiceover audio
5. Calculate voiceover duration
6. Download matching visuals
7. Download background music
8. Render a Short
9. Upload it to YouTube

### Long-form flow

When you run [main_long.py](main_long.py), the project will:

1. Pick a topic
2. Generate a long-form script
3. Clean the script for narration
4. Generate voiceover audio
5. Calculate voiceover duration
6. Download landscape visuals
7. Download background music
8. Render a long-form video
9. Generate subtitles
10. Upload it to YouTube

## Output files

After a successful run, you should typically see files like:

- `voiceover.mp3`
- `voiceover_long.mp3`
- `visual_0.mp4`, `visual_1.mp4`, etc.
- `long_visual_0.mp4`, `long_visual_1.mp4`, etc.
- `final_video.mp4`
- `final_long_video.mp4`
- `final_long_video.srt`

## Exact quick-start commands by operating system

### Windows PowerShell

```powershell
git clone https://github.com/shiv989898/Youtube-Automator.git
cd Youtube-Automator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
# Add your API keys to .env
# Put client_secret.json in the repo root
python main.py
```

### Windows Command Prompt

```bat
git clone https://github.com/shiv989898/Youtube-Automator.git
cd Youtube-Automator
python -m venv .venv
.venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
notepad .env
python main.py
```

### macOS / Linux

```bash
git clone https://github.com/shiv989898/Youtube-Automator.git
cd Youtube-Automator
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
nano .env
# Add your API keys
# Put client_secret.json in the repo root
python3 main.py
```

## Running without YouTube upload

If you only want to test generation locally, you can still run the project, but the YouTube step requires valid `client_secret.json` and successful OAuth login.

If you want a true local-only mode later, that can be added as a feature.

## Troubleshooting

### `ModuleNotFoundError`

Your virtual environment is probably not activated, or dependencies were not installed.

Fix:

```bash
pip install -r requirements.txt
```

### PowerShell says script execution is disabled

Run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### `client_secret.json` not found

Make sure the file exists in the repository root.

### YouTube upload fails or asks for auth again

Delete `token.pickle` and rerun the script to trigger a fresh Google login.

### Voice generation fails

The project tries `edge-tts` first, then `gTTS`, then `pyttsx3` as a fallback.

### Video generation feels slow

This is normal for MoviePy, especially on long-form runs.

### Pexels or Pixabay returns weak results

Check that your API keys are valid and not rate-limited.

## Automation options

- Windows batch launchers: [run_shorts.bat](run_shorts.bat), [run_long.bat](run_long.bat)
- Windows looping script: `loop_shorts.ps1`
- Task Scheduler setup: see [TASK_SCHEDULER_SETUP.md](TASK_SCHEDULER_SETUP.md)
- Cloud/CI options: [EASY_DEPLOYMENT.md](EASY_DEPLOYMENT.md), [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md), [FLY_DEPLOYMENT.md](FLY_DEPLOYMENT.md), [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md), [RAILWAY_SETUP.md](RAILWAY_SETUP.md)

## Project structure

- [main.py](main.py): Shorts workflow entry point
- [main_long.py](main_long.py): Long-form workflow entry point
- [script_generator.py](script_generator.py): Shorts script generation
- [script_generator_long.py](script_generator_long.py): Long-form script generation
- [voiceover.py](voiceover.py): Voice generation
- [visuals.py](visuals.py): Shorts visual collection
- [visuals_long.py](visuals_long.py): Long-form visual collection
- [video_creator.py](video_creator.py): Shorts video rendering
- [long_video_creator.py](long_video_creator.py): Long-form video rendering
- [youtube_uploader.py](youtube_uploader.py): Shorts upload
- [youtube_uploader_long.py](youtube_uploader_long.py): Long-form upload

## Open source

- [LICENSE](LICENSE)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)

Please do not commit:

- `.env`
- `client_secret.json`
- `token.pickle`
- generated media files
- personal credentials of any kind

## License and responsible use

This project is licensed under the MIT License. See [LICENSE](LICENSE).

You are responsible for complying with the terms of the APIs and content providers you use, including Google, Pexels, Pixabay, Microsoft, and any music or media sources referenced by the project.
