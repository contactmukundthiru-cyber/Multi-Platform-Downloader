@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: FLARE DOWNLOAD - One-Click Windows Installer
:: For people who have never used a command line before
:: Just double-click this file and everything will be set up automatically!
:: ============================================================================

title Flare Download - Installing...

:: Set colors
color 0C

:: Check if running as admin (not required but helpful)
net session >nul 2>&1
if %errorLevel% == 0 (
    set "ADMIN=1"
) else (
    set "ADMIN=0"
)

:: Set install directory (user's local app data - no admin needed)
set "INSTALL_DIR=%LOCALAPPDATA%\FlareDownload"
set "DESKTOP=%USERPROFILE%\Desktop"
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"

:: Create install directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: ============================================================================
:: BANNER
:: ============================================================================
cls
echo.
echo   [91m ███████╗██╗      █████╗ ██████╗ ███████╗[0m
echo   [91m ██╔════╝██║     ██╔══██╗██╔══██╗██╔════╝[0m
echo   [91m █████╗  ██║     ███████║██████╔╝█████╗  [0m
echo   [91m ██╔══╝  ██║     ██╔══██║██╔══██╗██╔══╝  [0m
echo   [91m ██║     ███████╗██║  ██║██║  ██║███████╗[0m
echo   [91m ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝[0m
echo.
echo   [93mDOWNLOAD[0m - Multi-Platform Video Downloader
echo.
echo   ══════════════════════════════════════════════════════
echo.
echo   [96mThis installer will set up everything automatically.[0m
echo   [96mNo technical knowledge required![0m
echo.
echo   ══════════════════════════════════════════════════════
echo.
echo   Press any key to start installation...
pause >nul

:: ============================================================================
:: STEP 1: Download Python (Embedded/Portable)
:: ============================================================================
cls
echo.
echo   [93m[1/5][0m Downloading Python...
echo.

set "PYTHON_DIR=%INSTALL_DIR%\python"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"

if exist "%PYTHON_EXE%" (
    echo   [92m✓[0m Python already installed
    goto :step2
)

echo   [96m→[0m Downloading Python 3.11 (this may take a minute)...

:: Download Python embeddable
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
set "PYTHON_ZIP=%INSTALL_DIR%\python.zip"

:: Try PowerShell download
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { (New-Object Net.WebClient).DownloadFile('%PYTHON_URL%', '%PYTHON_ZIP%') } catch { exit 1 }}" 2>nul

if not exist "%PYTHON_ZIP%" (
    echo.
    echo   [91m✗ Download failed.[0m
    echo.
    echo   Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo   [96m→[0m Extracting Python...
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
echo   [96m→[0m Installing pip...
set "GETPIP=%INSTALL_DIR%\get-pip.py"
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://bootstrap.pypa.io/get-pip.py', '%GETPIP%')}" 2>nul

"%PYTHON_EXE%" "%GETPIP%" --no-warn-script-location >nul 2>&1
del "%GETPIP%" 2>nul

echo   [92m✓[0m Python installed successfully
echo.

:step2
:: ============================================================================
:: STEP 2: Download FFmpeg
:: ============================================================================
cls
echo.
echo   [93m[2/5][0m Downloading FFmpeg...
echo.

set "FFMPEG_DIR=%INSTALL_DIR%\ffmpeg"
set "FFMPEG_EXE=%FFMPEG_DIR%\ffmpeg.exe"

if exist "%FFMPEG_EXE%" (
    echo   [92m✓[0m FFmpeg already installed
    goto :step3
)

echo   [96m→[0m Downloading FFmpeg (for video processing)...

:: Download FFmpeg essentials build
set "FFMPEG_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
set "FFMPEG_ZIP=%INSTALL_DIR%\ffmpeg.zip"

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { (New-Object Net.WebClient).DownloadFile('%FFMPEG_URL%', '%FFMPEG_ZIP%') } catch { exit 1 }}" 2>nul

if not exist "%FFMPEG_ZIP%" (
    echo   [93m![0m FFmpeg download failed (optional, continuing...)
    goto :step3
)

echo   [96m→[0m Extracting FFmpeg...
mkdir "%FFMPEG_DIR%" 2>nul
powershell -Command "Expand-Archive -Path '%FFMPEG_ZIP%' -DestinationPath '%INSTALL_DIR%\ffmpeg_temp' -Force" 2>nul

:: Move files from nested folder
for /d %%i in ("%INSTALL_DIR%\ffmpeg_temp\ffmpeg-*") do (
    xcopy "%%i\bin\*.*" "%FFMPEG_DIR%\" /Y /Q >nul 2>&1
)
rmdir /s /q "%INSTALL_DIR%\ffmpeg_temp" 2>nul
del "%FFMPEG_ZIP%" 2>nul

echo   [92m✓[0m FFmpeg installed successfully
echo.

:step3
:: ============================================================================
:: STEP 3: Install Python Dependencies
:: ============================================================================
cls
echo.
echo   [93m[3/5][0m Installing components...
echo.

set "PIP_EXE=%PYTHON_DIR%\Scripts\pip.exe"

echo   [96m→[0m Installing customtkinter (GUI library)...
"%PYTHON_EXE%" -m pip install customtkinter --no-warn-script-location -q 2>nul
if errorlevel 1 (
    echo   [93m![0m Retrying...
    "%PYTHON_EXE%" -m pip install customtkinter --no-warn-script-location 2>nul
)

echo   [96m→[0m Installing yt-dlp (video downloader)...
"%PYTHON_EXE%" -m pip install yt-dlp --no-warn-script-location -q 2>nul

echo   [96m→[0m Installing Pillow (image processing)...
"%PYTHON_EXE%" -m pip install Pillow --no-warn-script-location -q 2>nul

echo   [92m✓[0m All components installed
echo.

:step4
:: ============================================================================
:: STEP 4: Download Application
:: ============================================================================
cls
echo.
echo   [93m[4/5][0m Downloading Flare Download...
echo.

set "APP_FILE=%INSTALL_DIR%\youtube_downloader.py"
set "VERSION_FILE=%INSTALL_DIR%\version.py"

set "GITHUB_RAW=https://raw.githubusercontent.com/contactmukundthiru-cyber/Multi-Platform-Downloader/main"

echo   [96m→[0m Downloading application files...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/youtube_downloader.py', '%APP_FILE%')}" 2>nul
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/version.py', '%VERSION_FILE%')}" 2>nul

if not exist "%APP_FILE%" (
    echo.
    echo   [91m✗ Download failed.[0m
    echo.
    echo   Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo   [92m✓[0m Application downloaded
echo.

:step5
:: ============================================================================
:: STEP 5: Create Shortcuts
:: ============================================================================
cls
echo.
echo   [93m[5/5][0m Creating shortcuts...
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
echo Set WshShell = CreateObject("WScript.Shell"^)
echo WshShell.Run chr(34^) ^& "%LAUNCHER%" ^& chr(34^), 0
echo Set WshShell = Nothing
) > "%VBS_LAUNCHER%"

:: Create Desktop Shortcut using PowerShell
echo   [96m→[0m Creating desktop shortcut...
set "SHORTCUT=%DESKTOP%\Flare Download.lnk"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%VBS_LAUNCHER%'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = 'Premium Multi-Platform Video Downloader'; $s.Save()" 2>nul

if exist "%SHORTCUT%" (
    echo   [92m✓[0m Desktop shortcut created
) else (
    echo   [93m![0m Could not create desktop shortcut
)

:: Create Start Menu Shortcut
echo   [96m→[0m Creating Start Menu shortcut...
set "STARTMENU_SHORTCUT=%STARTMENU%\Flare Download.lnk"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTMENU_SHORTCUT%'); $s.TargetPath = '%VBS_LAUNCHER%'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = 'Premium Multi-Platform Video Downloader'; $s.Save()" 2>nul

if exist "%STARTMENU_SHORTCUT%" (
    echo   [92m✓[0m Start Menu shortcut created
)

echo.

:: ============================================================================
:: DONE!
:: ============================================================================
cls
echo.
echo   [92m ███████╗██╗      █████╗ ██████╗ ███████╗[0m
echo   [92m ██╔════╝██║     ██╔══██╗██╔══██╗██╔════╝[0m
echo   [92m █████╗  ██║     ███████║██████╔╝█████╗  [0m
echo   [92m ██╔══╝  ██║     ██╔══██║██╔══██╗██╔══╝  [0m
echo   [92m ██║     ███████╗██║  ██║██║  ██║███████╗[0m
echo   [92m ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝[0m
echo.
echo   [92m══════════════════════════════════════════════════════[0m
echo.
echo   [92m  ✓ INSTALLATION COMPLETE![0m
echo.
echo   [92m══════════════════════════════════════════════════════[0m
echo.
echo   [97mHow to use Flare Download:[0m
echo.
echo   [96m  1.[0m Double-click [93m"Flare Download"[0m on your Desktop
echo.
echo   [96m  2.[0m Paste a video URL (YouTube, TikTok, etc.)
echo.
echo   [96m  3.[0m Click [93mDOWNLOAD[0m
echo.
echo   [92m══════════════════════════════════════════════════════[0m
echo.
echo   Would you like to launch Flare Download now? (Y/N)
echo.
set /p LAUNCH="   > "
if /i "%LAUNCH%"=="Y" (
    start "" "%VBS_LAUNCHER%"
)

echo.
echo   Thank you for installing Flare Download!
echo   Part of the Flare ecosystem.
echo.
timeout /t 3 >nul
exit
