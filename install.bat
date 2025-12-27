@echo off
setlocal enabledelayedexpansion

:: Flare Download - Multi-Platform Video Downloader
:: Robust Windows Installer
:: Part of the Flare ecosystem

title Flare Download Installer

:: Set colors
color 0F

echo.
echo  ███████╗██╗      █████╗ ██████╗ ███████╗
echo  ██╔════╝██║     ██╔══██╗██╔══██╗██╔════╝
echo  █████╗  ██║     ███████║██████╔╝█████╗
echo  ██╔══╝  ██║     ██╔══██║██╔══██╗██╔══╝
echo  ██║     ███████╗██║  ██║██║  ██║███████╗
echo  ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
echo.
echo  DOWNLOAD - Multi-Platform Video Downloader
echo  YouTube ^| TikTok ^| Instagram ^| Twitter ^| 1000+ sites
echo.
echo ============================================================
echo.

:: Set install directory
set "INSTALL_DIR=%LOCALAPPDATA%\FlareDownload"

:: Step 1: Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo       [ERROR] Python not found!
    echo.
    echo       Please install Python 3.8 or higher:
    echo       1. Download from: https://python.org/downloads
    echo       2. IMPORTANT: Check "Add Python to PATH" during installation
    echo       3. Restart this installer after installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo       [OK] Python %PYTHON_VERSION% found

:: Check Python version (must be 3.8+)
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)
if %PYTHON_MAJOR% LSS 3 (
    echo       [ERROR] Python 3.8 or higher is required!
    echo       Current version: %PYTHON_VERSION%
    pause
    exit /b 1
)
if %PYTHON_MAJOR% EQU 3 if %PYTHON_MINOR% LSS 8 (
    echo       [ERROR] Python 3.8 or higher is required!
    echo       Current version: %PYTHON_VERSION%
    pause
    exit /b 1
)

:: Step 2: Check pip
echo.
echo [2/6] Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo       [WARN] pip not found, installing...
    python -m ensurepip --default-pip
    if errorlevel 1 (
        echo       [ERROR] Failed to install pip
        pause
        exit /b 1
    )
)
for /f "tokens=2" %%i in ('python -m pip --version 2^>^&1') do set PIP_VERSION=%%i
echo       [OK] pip %PIP_VERSION% found

:: Step 3: Check tkinter
echo.
echo [3/6] Checking system dependencies...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo       [ERROR] tkinter not found!
    echo.
    echo       tkinter should be included with Python on Windows.
    echo       Please reinstall Python from python.org and make sure
    echo       to select "tcl/tk and IDLE" in the optional features.
    echo.
    pause
    exit /b 1
)
echo       [OK] tkinter found

:: Check for FFmpeg (optional)
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo       [INFO] FFmpeg not found ^(optional, for video merging^)
    echo       To install: Download from https://ffmpeg.org/download.html
) else (
    echo       [OK] FFmpeg found ^(optional^)
)

:: Step 4: Create installation directory
echo.
echo [4/6] Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
echo       [OK] %INSTALL_DIR%

:: Copy files
set "SCRIPT_DIR=%~dp0"

if exist "%SCRIPT_DIR%youtube_downloader.py" (
    copy /Y "%SCRIPT_DIR%youtube_downloader.py" "%INSTALL_DIR%\" >nul
    copy /Y "%SCRIPT_DIR%updater.py" "%INSTALL_DIR%\" >nul 2>&1
    copy /Y "%SCRIPT_DIR%version.py" "%INSTALL_DIR%\" >nul 2>&1
    copy /Y "%SCRIPT_DIR%requirements.txt" "%INSTALL_DIR%\" >nul
    copy /Y "%SCRIPT_DIR%README.md" "%INSTALL_DIR%\" >nul 2>&1
    echo       [OK] Files copied
) else (
    echo       [ERROR] Source files not found in %SCRIPT_DIR%
    echo       Please run this installer from the Flare Download folder.
    pause
    exit /b 1
)

:: Step 5: Create virtual environment and install dependencies
echo.
echo [5/6] Setting up Python environment...
echo       This may take a few minutes...

:: Remove old venv if exists
if exist "%INSTALL_DIR%\venv" (
    echo       Removing old virtual environment...
    rmdir /s /q "%INSTALL_DIR%\venv"
)

:: Create new venv
echo       Creating virtual environment...
python -m venv "%INSTALL_DIR%\venv"
if errorlevel 1 (
    echo       [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

:: Activate and install
call "%INSTALL_DIR%\venv\Scripts\activate.bat"

echo       Upgrading pip...
python -m pip install --upgrade pip -q
if errorlevel 1 (
    echo       [WARN] Failed to upgrade pip, continuing...
)

echo       Installing dependencies...
pip install -r "%INSTALL_DIR%\requirements.txt" -q
if errorlevel 1 (
    echo       [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo       Installing yt-dlp...
pip install yt-dlp -q
if errorlevel 1 (
    echo       [WARN] Failed to install yt-dlp, continuing...
)

echo       [OK] All dependencies installed

:: Step 6: Create launcher
echo.
echo [6/6] Creating launcher and shortcuts...

:: Create launcher batch file
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo call venv\Scripts\activate.bat
echo pythonw youtube_downloader.py %%*
) > "%INSTALL_DIR%\FlareDownload.bat"

:: Create VBS for silent launch (no console window)
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.Run chr^(34^) ^& "%INSTALL_DIR%\FlareDownload.bat" ^& chr^(34^), 0
echo Set WshShell = Nothing
) > "%INSTALL_DIR%\FlareDownload.vbs"

echo       [OK] Launcher created

:: Create desktop shortcut
echo       Creating desktop shortcut...

:: Get Desktop path from registry (more reliable than %USERPROFILE%\Desktop)
for /f "tokens=2*" %%a in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop 2^>nul') do set "DESKTOP_PATH=%%b"

if not defined DESKTOP_PATH (
    set "DESKTOP_PATH=%USERPROFILE%\Desktop"
)

:: Create shortcut using VBScript
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%DESKTOP_PATH%\Flare Download.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "wscript.exe"
echo oLink.Arguments = """%INSTALL_DIR%\FlareDownload.vbs"""
echo oLink.WorkingDirectory = "%INSTALL_DIR%"
echo oLink.Description = "Flare Download - Multi-Platform Video Downloader"
echo oLink.Save
) > "%INSTALL_DIR%\CreateShortcut.vbs"

cscript //nologo "%INSTALL_DIR%\CreateShortcut.vbs" 2>nul
del "%INSTALL_DIR%\CreateShortcut.vbs" 2>nul

:: Verify shortcut
if exist "%DESKTOP_PATH%\Flare Download.lnk" (
    echo       [OK] Desktop shortcut created
) else (
    echo       [WARN] Could not create desktop shortcut
    echo       You can run: %INSTALL_DIR%\FlareDownload.bat
)

:: Create Start Menu shortcut
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
if exist "%START_MENU%" (
    (
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo sLinkFile = "%START_MENU%\Flare Download.lnk"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
    echo oLink.TargetPath = "wscript.exe"
    echo oLink.Arguments = """%INSTALL_DIR%\FlareDownload.vbs"""
    echo oLink.WorkingDirectory = "%INSTALL_DIR%"
    echo oLink.Description = "Flare Download - Multi-Platform Video Downloader"
    echo oLink.Save
    ) > "%INSTALL_DIR%\CreateStartMenuShortcut.vbs"
    cscript //nologo "%INSTALL_DIR%\CreateStartMenuShortcut.vbs" 2>nul
    del "%INSTALL_DIR%\CreateStartMenuShortcut.vbs" 2>nul
    echo       [OK] Start Menu shortcut created
)

:: Installation complete
echo.
echo ============================================================
echo.
echo  INSTALLATION COMPLETE!
echo.
echo  To run Flare Download:
echo    - Double-click the desktop shortcut "Flare Download"
echo    - Or find it in the Start Menu
echo    - Or run: %INSTALL_DIR%\FlareDownload.bat
echo.
echo  Supports: YouTube, TikTok, Instagram, Twitter, and 1000+ more!
echo.
echo  Part of the Flare ecosystem
echo.
echo ============================================================
echo.

pause
