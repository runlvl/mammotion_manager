@echo off
echo 🚀 Starting Mammotion Web Server...
echo 📍 Server will be available at: http://localhost:8000
echo 🛑 Press Ctrl+C to stop
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ⚠️  Virtual environment not found. Please run setup first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the server
python -m uvicorn src.mammotion_web.app:app --host 0.0.0.0 --port 8000 --reload --log-level info
