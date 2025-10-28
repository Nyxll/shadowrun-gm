# Force restart the game server
Write-Host "Stopping all Python processes running game-server..."
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*game-server*" } | Stop-Process -Force
Start-Sleep -Seconds 2

Write-Host "Starting game server..."
Start-Process python -ArgumentList "game-server.py" -NoNewWindow
Start-Sleep -Seconds 3

Write-Host "Server restarted!"
