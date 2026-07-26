@echo off
REM Builds TUNBEEC-Setup.exe from the python_tunbeec source tree.
REM
REM Run this ON A WINDOWS MACHINE (PyInstaller cannot cross-compile from macOS/Linux to
REM Windows). This script is for the developer building the installer, not for the end
REM user -- the end user only ever double-clicks the resulting TUNBEEC-Setup.exe.
REM
REM Requirements to run this script:
REM   - Python 3.10+ installed and on PATH (https://python.org/downloads, tick "Add to PATH")
REM   - Inno Setup 6 installed (https://jrsoftware.org/isdl.php), default install path
REM
REM Usage: double-click this file, or run it from a cmd prompt in this folder.

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo === TUNBEEC installer build ===

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found on PATH. Install Python 3.10+ from https://python.org/downloads
    echo         and make sure to check "Add python.exe to PATH" during install.
    pause
    exit /b 1
)

echo [1/5] Creating build virtual environment...
if not exist build_venv (
    python -m venv build_venv
)
call build_venv\Scripts\activate.bat

echo [2/5] Installing app dependencies + PyInstaller...
python -m pip install --upgrade pip >nul
pip install -r ..\python_tunbeec\requirements.txt
pip install pyinstaller
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)

echo [3/5] Cleaning previous build output...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo [4/5] Running PyInstaller (this can take a few minutes)...
pyinstaller tunbeec.spec --distpath dist --workpath build --noconfirm
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)

echo [5/5] Building the Setup.exe installer with Inno Setup...
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
    echo [ERROR] Inno Setup Compiler ^(ISCC.exe^) not found.
    echo         Install Inno Setup 6 from https://jrsoftware.org/isdl.php and re-run this script.
    pause
    exit /b 1
)
"%ISCC%" installer.iss
if errorlevel 1 (
    echo [ERROR] Inno Setup compile failed.
    pause
    exit /b 1
)

echo.
echo === Done ===
echo Installer created at: %cd%\installer_output\TUNBEEC-Setup.exe
echo Send that one file to your professor -- double-click, Next, Next, Install, Finish.
pause
