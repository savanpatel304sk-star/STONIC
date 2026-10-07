@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3.10 or newer is required.
  pause
  exit /b 1
)
python bootstrap.py
if errorlevel 1 pause
endlocal
