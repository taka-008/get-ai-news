@echo off
chcp 65001 > nul
echo Starting AI News Dashboard...
echo.

cd /d "%~dp0"

set PYTHON_CMD=
if exist "C:\Users\Takashi Mizuno\anaconda3\python.exe" set PYTHON_CMD=C:\Users\Takashi Mizuno\anaconda3\python.exe
if exist "C:\ProgramData\anaconda3\python.exe" set PYTHON_CMD=C:\ProgramData\anaconda3\python.exe

if "%PYTHON_CMD%"=="" (
    set PYTHON_CMD=python
)

echo Python: %PYTHON_CMD%
echo Access: http://localhost:5000
echo Press Ctrl+C to stop.
echo.

"%PYTHON_CMD%" app.py
pause
