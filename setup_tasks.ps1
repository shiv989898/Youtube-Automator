# YouTube Automation - Task Scheduler Setup Script
# Run this script as Administrator in PowerShell

Write-Host "Setting up YouTube automation tasks..." -ForegroundColor Cyan

# Task 1: YouTube Shorts (runs hourly at :00)
Write-Host "`nCreating YouTube Shorts task..." -ForegroundColor Yellow
$action1 = New-ScheduledTaskAction -Execute "C:\Users\shivg\OneDrive\Desktop\yt workflow\run_shorts.bat"
$trigger1 = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Hours 1)
$principal1 = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest
$settings1 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask -TaskName "YouTube-Shorts-Hourly" -Action $action1 -Trigger $trigger1 -Principal $principal1 -Settings $settings1 -Description "Generates YouTube Shorts every hour" -Force | Out-Null

Write-Host "SUCCESS: YouTube Shorts task created!" -ForegroundColor Green

# Task 2: YouTube Long Videos (runs hourly at :30)
Write-Host "`nCreating YouTube Long Videos task..." -ForegroundColor Yellow
$action2 = New-ScheduledTaskAction -Execute "C:\Users\shivg\OneDrive\Desktop\yt workflow\run_long.bat"
$startTime = (Get-Date).Date.AddMinutes(30)
$trigger2 = New-ScheduledTaskTrigger -Once -At $startTime -RepetitionInterval (New-TimeSpan -Hours 1)
$principal2 = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest
$settings2 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask -TaskName "YouTube-Long-Hourly" -Action $action2 -Trigger $trigger2 -Principal $principal2 -Settings $settings2 -Description "Generates long-form videos every hour" -Force | Out-Null

Write-Host "SUCCESS: YouTube Long Videos task created!" -ForegroundColor Green

# Verify tasks were created
Write-Host "`nVerification - Scheduled Tasks:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

Get-ScheduledTask -TaskName "YouTube-Shorts-Hourly" | Format-Table TaskName, State, NextRunTime -AutoSize
Get-ScheduledTask -TaskName "YouTube-Long-Hourly" | Format-Table TaskName, State, NextRunTime -AutoSize

Write-Host "`nSetup complete! Both tasks will run automatically every hour when your PC is on." -ForegroundColor Green
Write-Host "`nTo test immediately, run:" -ForegroundColor Yellow
Write-Host '  Start-ScheduledTask -TaskName "YouTube-Shorts-Hourly"' -ForegroundColor White
Write-Host '  Start-ScheduledTask -TaskName "YouTube-Long-Hourly"' -ForegroundColor White
