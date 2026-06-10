@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Infinite loop to run the long video automation

:loop
    echo.
    echo ========================================
    echo Starting long video automation at %DATE% %TIME%
    echo ========================================

    call "%~dp0run_long.bat"

    echo.
    echo ========================================
    echo Run finished at %DATE% %TIME%
    echo Waiting 1 hour before next run...
    echo ========================================
    
    timeout /t 3600 /nobreak
    
    goto loop