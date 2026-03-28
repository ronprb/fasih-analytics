@echo off
cd /d "%~dp0"

call "%~dp0venv\Scripts\activate.bat"

echo.
echo ========================================
echo    fasih-analytics
echo ========================================
echo.

set /p relogin="Force fresh login? (y/N): "
echo.

if /i "%relogin%"=="y" (
    python main.py --relogin
) else (
    python main.py
)

echo.
echo ========================================
echo    Done. Press any key to close.
echo ========================================
pause >nul
