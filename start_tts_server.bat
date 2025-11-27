@echo off
echo ================================================
echo GPT-SoVITS TTS Server Starting...
echo ================================================
echo.
echo Server will run on: http://localhost:9880
echo API docs available at: http://localhost:9880/docs
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

cd C:\TTs\GPT-SoVITS-v2pro-20250604\GPT-SoVITS-v2pro-20250604
runtime\python.exe api_v2.py --port 9880

pause
