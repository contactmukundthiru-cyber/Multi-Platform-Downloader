@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: FLARE DOWNLOAD - FULLY AUTOMATED INSTALLER
:: Works on any Windows PC - Zero technical knowledge required
:: ============================================================================

title Flare Download - Installing...
color 0F
mode con: cols=80 lines=40

echo.
echo  ============================================================
echo.
echo     ███████╗██╗      █████╗ ██████╗ ███████╗
echo     ██╔════╝██║     ██╔══██╗██╔══██╗██╔════╝
echo     █████╗  ██║     ███████║██████╔╝█████╗
echo     ██╔══╝  ██║     ██╔══██║██╔══██╗██╔══╝
echo     ██║     ███████╗██║  ██║██║  ██║███████╗
echo     ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
echo.
echo                      DOWNLOAD
echo.
echo     Multi-Platform Video Downloader
echo     YouTube, TikTok, Instagram, Twitter + 1000 more
echo.
echo  ============================================================
echo.
echo     Please wait while we set everything up for you.
echo     This may take 5-10 minutes on first install.
echo.
echo  ============================================================
echo.

:: ============================================================================
:: CONFIGURATION
:: ============================================================================

set "INSTALL_DIR=%LOCALAPPDATA%\FlareDownload"
set "PYTHON_DIR=%INSTALL_DIR%\python"
set "FFMPEG_DIR=%INSTALL_DIR%\ffmpeg"
set "NODEJS_DIR=%INSTALL_DIR%\node"
set "SCRIPT_DIR=%~dp0"
set "TEMP_DIR=%TEMP%\FlareInstaller_%RANDOM%"

:: Create directories
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: ============================================================================
:: STEP 1: INSTALL PYTHON
:: ============================================================================

echo [Step 1/6] Setting up Python...

:: Check if we already have embedded Python
if exist "%PYTHON_DIR%\python.exe" (
    echo           Python already installed.
    goto :PythonReady
)

echo           Downloading Python 3.11...

:: Download Python embeddable
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-embed-amd64.zip"
set "PYTHON_ZIP=%TEMP_DIR%\python.zip"

powershell -Command "& {$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; try{Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%' -UseBasicParsing}catch{exit 1}}" 2>nul

if not exist "%PYTHON_ZIP%" (
    echo           [!] Download failed. Trying alternate method...
    curl -L -s -o "%PYTHON_ZIP%" "%PYTHON_URL%" 2>nul
)

if not exist "%PYTHON_ZIP%" (
    echo.
    echo  ============================================================
    echo   ERROR: Could not download Python.
    echo   Please check your internet connection and try again.
    echo  ============================================================
    pause
    exit /b 1
)

echo           Extracting Python...
if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"
powershell -Command "& {$ProgressPreference='SilentlyContinue'; Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force}" 2>nul

:: Configure Python for pip
echo           Configuring Python...
(
echo python311.zip
echo .
echo Lib
echo Lib\site-packages
echo import site
) > "%PYTHON_DIR%\python311._pth"

if not exist "%PYTHON_DIR%\Lib" mkdir "%PYTHON_DIR%\Lib"
if not exist "%PYTHON_DIR%\Lib\site-packages" mkdir "%PYTHON_DIR%\Lib\site-packages"

:: Install pip
echo           Installing pip...
set "GET_PIP=%TEMP_DIR%\get-pip.py"
powershell -Command "& {$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%GET_PIP%' -UseBasicParsing}" 2>nul

"%PYTHON_DIR%\python.exe" "%GET_PIP%" --no-warn-script-location -q 2>nul

echo           Python ready.

:PythonReady
set "PYTHON=%PYTHON_DIR%\python.exe"
set "PIP=%PYTHON_DIR%\Scripts\pip.exe"

:: ============================================================================
:: STEP 2: INSTALL NODE.JS (Required for yt-dlp YouTube support)
:: ============================================================================

echo.
echo [Step 2/6] Setting up JavaScript runtime...

if exist "%NODEJS_DIR%\node.exe" (
    echo           Node.js already installed.
    goto :NodeReady
)

echo           Downloading Node.js...

:: Download Node.js (required for yt-dlp to work with YouTube)
set "NODE_URL=https://nodejs.org/dist/v20.10.0/node-v20.10.0-win-x64.zip"
set "NODE_ZIP=%TEMP_DIR%\node.zip"

powershell -Command "& {$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; try{Invoke-WebRequest -Uri '%NODE_URL%' -OutFile '%NODE_ZIP%' -UseBasicParsing}catch{exit 1}}" 2>nul

if exist "%NODE_ZIP%" (
    echo           Extracting Node.js...
    powershell -Command "& {$ProgressPreference='SilentlyContinue'; Expand-Archive -Path '%NODE_ZIP%' -DestinationPath '%TEMP_DIR%\node_temp' -Force}" 2>nul

    if not exist "%NODEJS_DIR%" mkdir "%NODEJS_DIR%"

    :: Copy node.exe
    for /d %%d in ("%TEMP_DIR%\node_temp\node-*") do (
        copy /Y "%%d\node.exe" "%NODEJS_DIR%\" >nul 2>&1
    )

    if exist "%NODEJS_DIR%\node.exe" (
        echo           Node.js ready.
    ) else (
        echo           [!] Node.js setup skipped.
    )

    rmdir /s /q "%TEMP_DIR%\node_temp" 2>nul
) else (
    echo           [!] Node.js download skipped. Some features may be limited.
)

:NodeReady

:: ============================================================================
:: STEP 3: INSTALL FFMPEG
:: ============================================================================

echo.
echo [Step 3/6] Setting up FFmpeg...

if exist "%FFMPEG_DIR%\ffmpeg.exe" (
    echo           FFmpeg already installed.
    goto :FFmpegReady
)

echo           Downloading FFmpeg...

:: Try multiple FFmpeg sources
set "FFMPEG_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
set "FFMPEG_ZIP=%TEMP_DIR%\ffmpeg.zip"

powershell -Command "& {$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; try{Invoke-WebRequest -Uri '%FFMPEG_URL%' -OutFile '%FFMPEG_ZIP%' -UseBasicParsing -TimeoutSec 120}catch{exit 1}}" 2>nul

if exist "%FFMPEG_ZIP%" (
    echo           Extracting FFmpeg...
    if not exist "%FFMPEG_DIR%" mkdir "%FFMPEG_DIR%"
    powershell -Command "& {$ProgressPreference='SilentlyContinue'; Expand-Archive -Path '%FFMPEG_ZIP%' -DestinationPath '%TEMP_DIR%\ffmpeg_temp' -Force}" 2>nul

    :: Find and copy ffmpeg executables
    for /r "%TEMP_DIR%\ffmpeg_temp" %%f in (ffmpeg.exe) do (
        copy /Y "%%f" "%FFMPEG_DIR%\" >nul 2>&1
    )
    for /r "%TEMP_DIR%\ffmpeg_temp" %%f in (ffprobe.exe) do (
        copy /Y "%%f" "%FFMPEG_DIR%\" >nul 2>&1
    )

    rmdir /s /q "%TEMP_DIR%\ffmpeg_temp" 2>nul

    if exist "%FFMPEG_DIR%\ffmpeg.exe" (
        echo           FFmpeg ready.
    ) else (
        echo           [!] FFmpeg extraction failed.
    )
) else (
    echo           [!] FFmpeg download skipped. Video merging may be limited.
)

:FFmpegReady

:: ============================================================================
:: STEP 4: COPY APPLICATION FILES
:: ============================================================================

echo.
echo [Step 4/6] Installing Flare Download...

if exist "%SCRIPT_DIR%youtube_downloader.py" (
    copy /Y "%SCRIPT_DIR%youtube_downloader.py" "%INSTALL_DIR%\" >nul
    copy /Y "%SCRIPT_DIR%version.py" "%INSTALL_DIR%\" >nul 2>&1
    copy /Y "%SCRIPT_DIR%updater.py" "%INSTALL_DIR%\" >nul 2>&1
    copy /Y "%SCRIPT_DIR%requirements.txt" "%INSTALL_DIR%\" >nul 2>&1
    echo           Application files installed.
) else (
    echo.
    echo  ============================================================
    echo   ERROR: Application files not found.
    echo   Please run this installer from the Flare Download folder.
    echo  ============================================================
    pause
    exit /b 1
)

:: ============================================================================
:: STEP 5: INSTALL PYTHON PACKAGES
:: ============================================================================

echo.
echo [Step 5/6] Installing Python packages...
echo           This may take a few minutes...

:: Upgrade pip first
"%PYTHON%" -m pip install --upgrade pip -q 2>nul

:: Install packages one by one for better error handling
echo           Installing customtkinter...
"%PIP%" install customtkinter -q 2>nul
if errorlevel 1 "%PYTHON%" -m pip install customtkinter -q 2>nul

echo           Installing yt-dlp...
"%PIP%" install yt-dlp -q 2>nul
if errorlevel 1 "%PYTHON%" -m pip install yt-dlp -q 2>nul

echo           Installing additional packages...
"%PIP%" install packaging pillow -q 2>nul

echo           Packages installed.

:: ============================================================================
:: STEP 6: CREATE LAUNCHER AND SHORTCUTS
:: ============================================================================

echo.
echo [Step 6/6] Creating shortcuts...

:: Create launcher script
(
echo @echo off
echo setlocal
echo set "PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%FFMPEG_DIR%;%NODEJS_DIR%;%%PATH%%"
echo cd /d "%INSTALL_DIR%"
echo start "" "%PYTHON_DIR%\pythonw.exe" youtube_downloader.py
) > "%INSTALL_DIR%\FlareDownload.bat"

:: Create VBS for silent launch
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.Run """" ^& "%INSTALL_DIR%\FlareDownload.bat" ^& """", 0, False
echo Set WshShell = Nothing
) > "%INSTALL_DIR%\FlareDownload.vbs"

:: Get Desktop path
for /f "usebackq tokens=2*" %%a in (`reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop 2^>nul`) do set "DESKTOP=%%b"
if not defined DESKTOP set "DESKTOP=%USERPROFILE%\Desktop"

:: Create desktop shortcut
set "SHORTCUT_VBS=%TEMP_DIR%\shortcut.vbs"
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo Set oLink = oWS.CreateShortcut^("%DESKTOP%\Flare Download.lnk"^)
echo oLink.TargetPath = "wscript.exe"
echo oLink.Arguments = """%INSTALL_DIR%\FlareDownload.vbs"""
echo oLink.WorkingDirectory = "%INSTALL_DIR%"
echo oLink.Description = "Flare Download - Video Downloader"
echo oLink.Save
) > "%SHORTCUT_VBS%"
cscript //nologo "%SHORTCUT_VBS%" 2>nul

:: Create Start Menu shortcut
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
if exist "%STARTMENU%" (
    (
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo Set oLink = oWS.CreateShortcut^("%STARTMENU%\Flare Download.lnk"^)
    echo oLink.TargetPath = "wscript.exe"
    echo oLink.Arguments = """%INSTALL_DIR%\FlareDownload.vbs"""
    echo oLink.WorkingDirectory = "%INSTALL_DIR%"
    echo oLink.Description = "Flare Download - Video Downloader"
    echo oLink.Save
    ) > "%TEMP_DIR%\startmenu.vbs"
    cscript //nologo "%TEMP_DIR%\startmenu.vbs" 2>nul
)

:: Verify shortcuts
if exist "%DESKTOP%\Flare Download.lnk" (
    echo           Desktop shortcut created.
) else (
    echo           [!] Desktop shortcut may need manual creation.
)

:: ============================================================================
:: CLEANUP AND FINISH
:: ============================================================================

:: Clean up temp files
rmdir /s /q "%TEMP_DIR%" 2>nul

echo.
echo  ============================================================
echo.
echo     INSTALLATION COMPLETE!
echo.
echo     Flare Download has been successfully installed.
echo.
echo     To start the application:
echo       - Double-click "Flare Download" on your Desktop
echo       - Or find it in the Start Menu
echo.
echo     What's included:
echo       - Python 3.11 runtime
echo       - Node.js runtime (for YouTube support)
echo       - FFmpeg (for video processing)
echo       - yt-dlp (video downloader engine)
echo.
echo     Installed to: %INSTALL_DIR%
echo.
echo  ============================================================
echo.
echo     Press any key to close this window...
echo.

pause >nul
exit /b 0
