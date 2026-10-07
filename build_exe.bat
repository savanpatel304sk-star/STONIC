@echo off
setlocal EnableExtensions
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python 3.10+ was not found. Install Python from python.org first.
  exit /b 1
)

python -m pip install --upgrade pip
if errorlevel 1 exit /b 1
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1

python -m PyInstaller --noconfirm --clean --onedir --windowed ^
  --name STONIC ^
  --collect-all psutil ^
  --collect-submodules agents ^
  --add-data "ui\web;ui\web" ^
  launcher.py
if errorlevel 1 (
  echo PyInstaller failed. Review the output above.
  exit /b 1
)

copy /Y .env.example dist\STONIC\.env.example >nul
if errorlevel 1 exit /b 1

echo.
echo Build created: %CD%\dist\STONIC\STONIC.exe
echo This is a portable folder build; keep the adjacent _internal files.
echo Configure OPENAI_API_KEY in %%LOCALAPPDATA%%\STONIC\.env before using online AI.
endlocal
