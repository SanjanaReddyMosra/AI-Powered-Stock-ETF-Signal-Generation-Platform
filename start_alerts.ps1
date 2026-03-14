$env:RUN_CONTINUOUS="true"
$env:BYPASS_MARKET_CHECK="false"
$env:ALERT_INTERVAL_SECONDS="1800"

Write-Host "🚀 AlgoSignal AI: Background Alert Engine Started" -ForegroundColor Cyan
Write-Host "📡 Monitoring 10 tickers every 30 minutes during trading hours..."
Write-Host "📍 Press Ctrl+C to stop the engine.`n"

# Using the verified Python 3.10 path
& "C:\Users\sanja\AppData\Local\Python\pythoncore-3.10-64\python.exe" -u alert_job.py
