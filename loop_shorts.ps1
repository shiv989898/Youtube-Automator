# Automated YouTube Shorts Generator Loop
# Runs shorts generation every 6 minutes continuously

while ($true) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Starting shorts workflow at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # Run the shorts generation batch file
    & ".\run_shorts.bat"
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Run finished at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow
    Write-Host "Waiting 6 minutes before next run..." -ForegroundColor Yellow
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    # Wait for 6 minutes (360 seconds)
    Start-Sleep -Seconds 360
}
