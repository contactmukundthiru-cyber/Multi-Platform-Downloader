@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: FLARE DOWNLOAD - One-Click Windows Installer
:: For people who have never used a command line before
:: Just double-click this file and everything will be set up automatically!
:: ============================================================================

title Flare Download - Installing...

:: Set UTF-8 code page for proper display
chcp 65001 >nul 2>&1

:: Set install directory (user's local app data - no admin needed)
set "INSTALL_DIR=%LOCALAPPDATA%\FlareDownload"
set "DESKTOP=%USERPROFILE%\Desktop"
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"

:: Clean up old installation if exists (fresh start)
if exist "%INSTALL_DIR%" (
    echo    Removing old installation for clean update...
    rmdir /s /q "%INSTALL_DIR%" 2>nul
    ping -n 3 127.0.0.1 >nul
)

:: Create fresh install directory
mkdir "%INSTALL_DIR%"

:: ============================================================================
:: BANNER
:: ============================================================================
cls
echo.
echo    ______   __          ___      _______   ________
echo   /  ____^| /  ^|        /   ^|    /  ___  ^| /  _____/
echo  /  /___  /  /        / /^| ^|   /  /__^| ^|/  /____
echo /  ____/ /  /        / /_^| ^|  /  _   _^|/  _____/
echo /  /    /  /____    / ___  ^| /  / ^|  ^|/  /_____
echo /__/   /________^|  /_/   ^|_^|/__/  ^|__^|/_________/
echo.
echo    DOWNLOAD - Multi-Platform Video Downloader
echo.
echo    ========================================================
echo.
echo    This installer will set up everything automatically.
echo    No technical knowledge required!
echo.
echo    ========================================================
echo.
echo    Press any key to start installation...
pause >nul

:: ============================================================================
:: STEP 1: Download Python (Embedded/Portable)
:: ============================================================================
cls
echo.
echo    [1/5] Downloading Python...
echo.

set "PYTHON_DIR=%INSTALL_DIR%\python"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"

if exist "%PYTHON_EXE%" (
    echo    [OK] Python already installed
    goto :step2
)

echo    [..] Downloading Python 3.11 (this may take a minute)...

:: Download Python embeddable
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
set "PYTHON_ZIP=%INSTALL_DIR%\python.zip"

:: Try PowerShell download
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { (New-Object Net.WebClient).DownloadFile('%PYTHON_URL%', '%PYTHON_ZIP%') } catch { exit 1 }}" 2>nul

if not exist "%PYTHON_ZIP%" (
    echo.
    echo    [ERROR] Download failed.
    echo.
    echo    Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo    [..] Extracting Python...
mkdir "%PYTHON_DIR%" 2>nul
powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force" 2>nul
del "%PYTHON_ZIP%" 2>nul

:: Enable pip in embedded Python
set "PTH_FILE=%PYTHON_DIR%\python311._pth"
if exist "%PTH_FILE%" (
    echo python311.zip> "%PTH_FILE%"
    echo .>> "%PTH_FILE%"
    echo Lib\site-packages>> "%PTH_FILE%"
    echo import site>> "%PTH_FILE%"
)

:: Download get-pip.py
echo    [..] Installing pip...
set "GETPIP=%INSTALL_DIR%\get-pip.py"
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://bootstrap.pypa.io/get-pip.py', '%GETPIP%')}" 2>nul

"%PYTHON_EXE%" "%GETPIP%" --no-warn-script-location >nul 2>&1
del "%GETPIP%" 2>nul

echo    [OK] Python installed successfully
echo.

:step2
:: ============================================================================
:: STEP 2: Download FFmpeg
:: ============================================================================
cls
echo.
echo    [2/5] Downloading FFmpeg...
echo.

set "FFMPEG_DIR=%INSTALL_DIR%\ffmpeg"
set "FFMPEG_EXE=%FFMPEG_DIR%\ffmpeg.exe"

if exist "%FFMPEG_EXE%" (
    echo    [OK] FFmpeg already installed
    goto :step3
)

echo    [..] Downloading FFmpeg (for video processing)...

:: Download FFmpeg essentials build
set "FFMPEG_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
set "FFMPEG_ZIP=%INSTALL_DIR%\ffmpeg.zip"

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { (New-Object Net.WebClient).DownloadFile('%FFMPEG_URL%', '%FFMPEG_ZIP%') } catch { exit 1 }}" 2>nul

if not exist "%FFMPEG_ZIP%" (
    echo    [!] FFmpeg download failed (optional, continuing...)
    goto :step3
)

echo    [..] Extracting FFmpeg...
mkdir "%FFMPEG_DIR%" 2>nul
powershell -Command "Expand-Archive -Path '%FFMPEG_ZIP%' -DestinationPath '%INSTALL_DIR%\ffmpeg_temp' -Force" 2>nul

:: Move files from nested folder
for /d %%i in ("%INSTALL_DIR%\ffmpeg_temp\ffmpeg-*") do (
    xcopy "%%i\bin\*.*" "%FFMPEG_DIR%\" /Y /Q >nul 2>&1
)
rmdir /s /q "%INSTALL_DIR%\ffmpeg_temp" 2>nul
del "%FFMPEG_ZIP%" 2>nul

echo    [OK] FFmpeg installed successfully
echo.

:step3
:: ============================================================================
:: STEP 3: Install Python Dependencies
:: ============================================================================
cls
echo.
echo    [3/5] Installing components...
echo.

set "PIP_EXE=%PYTHON_DIR%\Scripts\pip.exe"

echo    [..] Installing customtkinter (GUI library)...
"%PYTHON_EXE%" -m pip install customtkinter --no-warn-script-location -q 2>nul
if errorlevel 1 (
    echo    [!] Retrying...
    "%PYTHON_EXE%" -m pip install customtkinter --no-warn-script-location 2>nul
)

echo    [..] Installing yt-dlp (video downloader)...
"%PYTHON_EXE%" -m pip install yt-dlp --no-warn-script-location -q 2>nul

echo    [..] Installing Pillow (image processing)...
"%PYTHON_EXE%" -m pip install Pillow --no-warn-script-location -q 2>nul

echo    [..] Installing requests (for updates)...
"%PYTHON_EXE%" -m pip install requests --no-warn-script-location -q 2>nul

echo    [OK] All components installed
echo.

:step4
:: ============================================================================
:: STEP 4: Download Application
:: ============================================================================
cls
echo.
echo    [4/5] Downloading Flare Download...
echo.

set "APP_FILE=%INSTALL_DIR%\youtube_downloader.py"
set "VERSION_FILE=%INSTALL_DIR%\version.py"
set "UPDATER_FILE=%INSTALL_DIR%\updater.py"

set "GITHUB_RAW=https://raw.githubusercontent.com/contactmukundthiru-cyber/Multi-Platform-Downloader/main"

echo    [..] Downloading application files...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/youtube_downloader.py', '%APP_FILE%')}" 2>nul
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/version.py', '%VERSION_FILE%')}" 2>nul
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/updater.py', '%UPDATER_FILE%')}" 2>nul

if not exist "%APP_FILE%" (
    echo.
    echo    [ERROR] Download failed.
    echo.
    echo    Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo    [OK] Application downloaded
echo.

:step5
:: ============================================================================
:: STEP 5: Create Shortcuts
:: ============================================================================
cls
echo.
echo    [5/5] Creating shortcuts...
echo.

:: Create launcher batch file
set "LAUNCHER=%INSTALL_DIR%\FlareDownload.bat"
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo set "PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%FFMPEG_DIR%;%%PATH%%"
echo start "" "%PYTHON_EXE%" "%APP_FILE%"
echo exit
) > "%LAUNCHER%"

:: Create VBS wrapper (hides command window)
set "VBS_LAUNCHER=%INSTALL_DIR%\FlareDownload.vbs"
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.Run chr^(34^) ^& "%LAUNCHER%" ^& chr^(34^), 0
echo Set WshShell = Nothing
) > "%VBS_LAUNCHER%"

:: Create Desktop Shortcut using PowerShell
echo    [..] Creating desktop shortcut...
set "SHORTCUT=%DESKTOP%\Flare Download.lnk"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%VBS_LAUNCHER%'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = 'Premium Multi-Platform Video Downloader'; $s.Save()" 2>nul

if exist "%SHORTCUT%" (
    echo    [OK] Desktop shortcut created
) else (
    echo    [!] Could not create desktop shortcut
)

:: Create Start Menu Shortcut
echo    [..] Creating Start Menu shortcut...
set "STARTMENU_SHORTCUT=%STARTMENU%\Flare Download.lnk"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTMENU_SHORTCUT%'); $s.TargetPath = '%VBS_LAUNCHER%'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = 'Premium Multi-Platform Video Downloader'; $s.Save()" 2>nul

if exist "%STARTMENU_SHORTCUT%" (
    echo    [OK] Start Menu shortcut created
)

echo.

:: ============================================================================
:: DONE!
:: ============================================================================
cls
echo.
echo    ========================================================
echo.
echo    FLARE DOWNLOAD
echo.
echo    ========================================================
echo.
echo    INSTALLATION COMPLETE!
echo.
echo    ========================================================
echo.
echo    How to use Flare Download:
echo.
echo    1. Double-click "Flare Download" on your Desktop
echo.
echo    2. Paste a video URL (YouTube, TikTok, etc.)
echo.
echo    3. Click DOWNLOAD
echo.
echo    ========================================================
echo.
echo    Would you like to launch Flare Download now? (Y/N)
echo.
set /p LAUNCH="   > "
if /i "%LAUNCH%"=="Y" (
    start "" "%VBS_LAUNCHER%"
)

echo.
echo    Thank you for installing Flare Download!
echo    Part of the Flare ecosystem.
echo.
timeout /t 3 >nul
exit
