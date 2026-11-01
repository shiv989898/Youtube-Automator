@echo off
cd /d "%~dp0"
echo Starting YouTube Automator Dashboard...
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" gui.py
) else (
    python gui.py
)
