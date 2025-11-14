@echo off
REM YouTube Shorts Automation Script
REM This script runs the YouTube Shorts generation workflow

echo ========================================
echo YouTube Shorts Automation
echo Starting at %date% %time%
echo ========================================

cd /d "C:\Users\shivg\OneDrive\Desktop\yt workflow"

REM Activate virtual environment and run main.py
".venv\Scripts\python.exe" main.py

echo.
echo ========================================
echo Finished at %date% %time%
echo ========================================

REM Log the execution
echo [%date% %time%] Workflow executed >> automation_log.txt
