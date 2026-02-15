@echo off
echo ========================================
echo VMF Spawner - Dependency Installation
echo ========================================
echo.

echo Checking Python...
python --version
if errorlevel 1 (
    echo [ERROR] Python not found! Install Python 3.11+
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Installation completed!
echo ========================================
echo.
echo Run the application with: python main.py
echo.
pause
