@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Infinite loop to run the shorts automation every 5 minutes

:loop
    echo.
    echo ========================================
    echo Starting shorts automation at %DATE% %TIME%
    echo ========================================

    call "%~dp0run_shorts.bat"

    echo.
    echo ========================================
    echo Run finished at %DATE% %TIME%
    echo Waiting 5 minutes before next run...
    echo ========================================

    
    goto loop
