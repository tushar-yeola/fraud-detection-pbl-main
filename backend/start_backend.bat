@echo off
echo ===============================================
echo   TransactGuard Backend Startup
echo ===============================================

cd /d "%~dp0"

echo [1/2] Installing requirements (if needed)...
"C:\Users\Vishwajeet\AppData\Local\Programs\Python\Python311\python.exe" -m pip install -r requirements.txt --quiet

echo.
echo [2/2] Starting FastAPI backend on http://localhost:8000
echo KEEP THIS WINDOW OPEN!
echo.

"C:\Users\Vishwajeet\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn main:app --reload --port 8000 --host 127.0.0.1
