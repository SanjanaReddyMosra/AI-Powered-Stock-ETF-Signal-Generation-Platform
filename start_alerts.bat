@echo off
set RUN_CONTINUOUS=true
set BYPASS_MARKET_CHECK=false
set ALERT_INTERVAL_SECONDS=1800

echo 🚀 AlgoSignal AI: Background Alert Engine Started
echo 📡 Monitoring 10 tickers every 30 minutes during trading hours...
echo 📍 Press Ctrl+C to stop the engine.

"C:\Users\sanja\AppData\Local\Python\pythoncore-3.10-64\python.exe" -u alert_job.py
pause
