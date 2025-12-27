@echo off
:: ============================================================================
:: FLARE DOWNLOAD - Complete Installer Builder
:: Creates a professional Windows installer (.exe)
:: ============================================================================
::
:: This script automatically:
::   1. Installs Python dependencies
::   2. Downloads and installs Inno Setup (if not found)
::   3. Builds the standalone .exe using PyInstaller
::   4. Creates the installer using Inno Setup
::
:: Requirements:
::   - Python 3.8+ with pip
::   - Internet connection (for downloading dependencies)
::
:: ============================================================================

setlocal enabledelayedexpansion

echo.
echo    ========================================
echo    FLARE DOWNLOAD - Installer Builder
echo    ========================================
echo.

:: Check Python
echo    [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo    ERROR: Python not found!
    echo.
    echo    Please install Python from https://python.org
    echo    Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo          Python %PYVER% OK

:: Check/Install PyInstaller
echo    [2/6] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo          Installing PyInstaller...
    pip install pyinstaller -q
    if errorlevel 1 (
        echo    ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)
echo          PyInstaller OK

:: Install dependencies
echo    [3/7] Installing dependencies...
pip install customtkinter Pillow yt-dlp -q
if errorlevel 1 (
    echo    WARNING: Some dependencies may have failed to install
)
echo          Dependencies OK

:: Generate icon
echo    [4/7] Generating application icon...
if not exist "icon.ico" (
    python create_icon.py
    if errorlevel 1 (
        echo    WARNING: Could not generate icon, using default
    ) else (
        echo          Icon generated OK
    )
) else (
    echo          Icon exists OK
)

:: Check/Install Inno Setup
echo    [5/7] Checking Inno Setup...

set ISCC=
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if "!ISCC!"=="" (
    echo          Inno Setup not found. Downloading...
    echo.

    :: Create temp directory
    if not exist "temp" mkdir temp

    :: Download Inno Setup using PowerShell
    echo          Downloading Inno Setup 6.2.2...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://jrsoftware.org/download.php/is.exe' -OutFile 'temp\innosetup.exe' -UseBasicParsing}"

    if not exist "temp\innosetup.exe" (
        echo.
        echo    ERROR: Failed to download Inno Setup!
        echo.
        echo    Please download manually from:
        echo    https://jrsoftware.org/isinfo.php
        echo.
        echo    Your standalone executable is ready at:
        echo    dist\Flare Download.exe
        echo.
        pause
        exit /b 1
    )

    echo          Installing Inno Setup (this may take a moment)...
    echo.

    :: Install silently
    temp\innosetup.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-

    :: Wait for installation
    timeout /t 5 /nobreak >nul

    :: Check again
    if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
        set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    ) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
        set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
    )

    :: Cleanup
    if exist "temp\innosetup.exe" del /f /q "temp\innosetup.exe"
    if exist "temp" rmdir /q temp 2>nul

    if "!ISCC!"=="" (
        echo.
        echo    ERROR: Inno Setup installation failed!
        echo.
        echo    Please install manually from:
        echo    https://jrsoftware.org/isinfo.php
        echo.
        echo    Then run this script again.
        echo.
        pause
        exit /b 1
    )

    echo          Inno Setup installed successfully!
) else (
    echo          Inno Setup OK
)

:: Clean old builds
echo    [6/7] Cleaning old builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
for %%f in (*.spec) do del /f /q "%%f" 2>nul
if exist "installer_output" rmdir /s /q installer_output
echo          Clean OK

:: Build with PyInstaller
echo    [7/7] Building executable with PyInstaller...
echo.

:: Check if icon exists
set ICON_PARAM=
if exist "icon.ico" (
    set ICON_PARAM=--icon=icon.ico
    echo          Using custom icon: icon.ico
)

pyinstaller --onefile --windowed --clean ^
    --name="Flare Download" ^
    --add-data="version.py;." ^
    --add-data="updater.py;." ^
    --hidden-import=customtkinter ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=yt_dlp ^
    %ICON_PARAM% ^
    youtube_downloader.py

if not exist "dist\Flare Download.exe" (
    echo.
    echo    ========================================
    echo    ERROR: PyInstaller build failed!
    echo    ========================================
    echo.
    echo    Check the output above for errors.
    echo    Common fixes:
    echo    - Ensure all dependencies are installed
    echo    - Check for syntax errors in the Python code
    echo    - Try running: pip install --upgrade pyinstaller
    echo.
    pause
    exit /b 1
)

echo.
echo    PyInstaller build successful!
echo.

:: Build installer with Inno Setup
echo    Building Windows installer with Inno Setup...
echo.

"!ISCC!" installer.iss

if errorlevel 1 (
    echo.
    echo    ========================================
    echo    ERROR: Inno Setup build failed!
    echo    ========================================
    echo.
    echo    Check the output above for errors.
    echo    Common fixes:
    echo    - Ensure installer.iss has correct paths
    echo    - Check that dist\Flare Download.exe exists
    echo.
    pause
    exit /b 1
)

echo.
echo    ========================================
echo    BUILD COMPLETE!
echo    ========================================
echo.
echo    Files created:
echo.
echo    1. Standalone executable:
echo       dist\Flare Download.exe
echo.
echo    2. Windows installer:
echo       installer_output\FlareDownload_Setup_2.8.4.exe
echo.
echo    ----------------------------------------
echo    Distribution:
echo.
echo    - Upload the installer to GitHub Releases
echo    - Users download and double-click to install
echo    - No Python or dependencies needed!
echo    ========================================
echo.

pause
