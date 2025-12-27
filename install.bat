@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: FLARE DOWNLOAD - Complete Installer
:: Install, Repair, Update, or Uninstall
:: ============================================================================

title Flare Download - Setup

:: Set UTF-8 code page
chcp 65001 >nul 2>&1

:: Set directories
set "INSTALL_DIR=%LOCALAPPDATA%\FlareDownload"
set "DESKTOP=%USERPROFILE%\Desktop"
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
set "GITHUB_RAW=https://raw.githubusercontent.com/contactmukundthiru-cyber/Multi-Platform-Downloader/main"

:: ============================================================================
:: MAIN MENU
:: ============================================================================
:menu
cls
echo.
echo    ======================================================
echo.
echo        FLARE DOWNLOAD - Setup
echo.
echo    ======================================================
echo.
echo        [1] Install / Reinstall
echo.
echo        [2] Update (Check for new version)
echo.
echo        [3] Repair (Fix broken installation)
echo.
echo        [4] Uninstall (Remove completely)
echo.
echo        [5] Exit
echo.
echo    ======================================================
echo.
set /p CHOICE="    Enter choice (1-5): "

if "%CHOICE%"=="1" goto :install
if "%CHOICE%"=="2" goto :update
if "%CHOICE%"=="3" goto :repair
if "%CHOICE%"=="4" goto :uninstall
if "%CHOICE%"=="5" exit
goto :menu

:: ============================================================================
:: INSTALL
:: ============================================================================
:install
cls
echo.
echo    FLARE DOWNLOAD - Installing...
echo    ======================================================
echo.

:: Clean up ALL old installations
call :cleanup_all

echo    [1/5] Downloading Python...
call :install_python
if errorlevel 1 goto :error

echo.
echo    [2/5] Downloading FFmpeg...
call :install_ffmpeg

echo.
echo    [3/5] Installing components...
call :install_dependencies

echo.
echo    [4/5] Downloading application...
call :download_app
if errorlevel 1 goto :error

echo.
echo    [5/5] Creating shortcuts...
call :create_shortcuts

goto :success

:: ============================================================================
:: UPDATE
:: ============================================================================
:update
cls
echo.
echo    FLARE DOWNLOAD - Checking for Updates...
echo    ======================================================
echo.

if not exist "%INSTALL_DIR%\version.py" (
    echo    ERROR: Flare Download is not installed.
    echo    Please install first.
    pause
    goto :menu
)

:: Get current version
for /f "tokens=2 delims==" %%a in ('findstr /c:"__version__" "%INSTALL_DIR%\version.py"') do (
    set "CURRENT_VER=%%a"
)
set "CURRENT_VER=%CURRENT_VER: =%"
set "CURRENT_VER=%CURRENT_VER:"=%"

echo    Current version: %CURRENT_VER%
echo    Checking GitHub for updates...
echo.

:: Download latest version.py to temp
set "TEMP_VER=%TEMP%\flare_version_check.py"
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/version.py', '%TEMP_VER%')}" 2>nul

if not exist "%TEMP_VER%" (
    echo    ERROR: Could not connect to GitHub.
    echo    Check your internet connection.
    pause
    goto :menu
)

:: Get latest version
for /f "tokens=2 delims==" %%a in ('findstr /c:"__version__" "%TEMP_VER%"') do (
    set "LATEST_VER=%%a"
)
set "LATEST_VER=%LATEST_VER: =%"
set "LATEST_VER=%LATEST_VER:"=%"
del "%TEMP_VER%" 2>nul

echo    Latest version: %LATEST_VER%
echo.

if "%CURRENT_VER%"=="%LATEST_VER%" (
    echo    You have the latest version!
    echo.
    pause
    goto :menu
)

echo    Update available!
echo.
set /p DO_UPDATE="    Download and install update? (Y/N): "
if /i not "%DO_UPDATE%"=="Y" goto :menu

echo.
echo    Downloading update...

:: Download updated files
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/youtube_downloader.py', '%INSTALL_DIR%\youtube_downloader.py')}" 2>nul
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/version.py', '%INSTALL_DIR%\version.py')}" 2>nul
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/updater.py', '%INSTALL_DIR%\updater.py')}" 2>nul

echo.
echo    ======================================================
echo    UPDATE COMPLETE!
echo    ======================================================
echo.
echo    Updated from %CURRENT_VER% to %LATEST_VER%
echo.
pause
goto :menu

:: ============================================================================
:: REPAIR
:: ============================================================================
:repair
cls
echo.
echo    FLARE DOWNLOAD - Repairing Installation...
echo    ======================================================
echo.

if not exist "%INSTALL_DIR%" (
    echo    ERROR: Flare Download is not installed.
    echo    Please install first.
    pause
    goto :menu
)

echo    Reinstalling components...
echo.

:: Reinstall Python packages
if exist "%INSTALL_DIR%\python\python.exe" (
    echo    Reinstalling customtkinter...
    "%INSTALL_DIR%\python\python.exe" -m pip install --upgrade customtkinter --no-warn-script-location -q 2>nul

    echo    Reinstalling yt-dlp...
    "%INSTALL_DIR%\python\python.exe" -m pip install --upgrade yt-dlp --no-warn-script-location -q 2>nul

    echo    Reinstalling Pillow...
    "%INSTALL_DIR%\python\python.exe" -m pip install --upgrade Pillow --no-warn-script-location -q 2>nul
)

:: Re-download application files
echo    Re-downloading application files...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/youtube_downloader.py', '%INSTALL_DIR%\youtube_downloader.py')}" 2>nul
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/version.py', '%INSTALL_DIR%\version.py')}" 2>nul
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/updater.py', '%INSTALL_DIR%\updater.py')}" 2>nul

:: Recreate shortcuts
echo    Recreating shortcuts...
call :create_shortcuts

echo.
echo    ======================================================
echo    REPAIR COMPLETE!
echo    ======================================================
echo.
pause
goto :menu

:: ============================================================================
:: UNINSTALL
:: ============================================================================
:uninstall
cls
echo.
echo    FLARE DOWNLOAD - Uninstall
echo    ======================================================
echo.
echo    This will completely remove Flare Download from your
echo    computer, including:
echo.
echo      - Application files
echo      - Desktop shortcut
echo      - Start Menu shortcut
echo.
set /p CONFIRM="    Are you sure? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto :menu

echo.
echo    Removing Flare Download...

call :cleanup_all

echo.
echo    ======================================================
echo    UNINSTALL COMPLETE!
echo    ======================================================
echo.
echo    Flare Download has been removed from your computer.
echo.
pause
exit

:: ============================================================================
:: HELPER FUNCTIONS
:: ============================================================================

:cleanup_all
:: Remove all old installations and shortcuts
if exist "%INSTALL_DIR%" (
    echo    Removing installation folder...
    rmdir /s /q "%INSTALL_DIR%" 2>nul
)

:: Remove all possible desktop shortcuts
if exist "%DESKTOP%\Flare Download.lnk" del /f /q "%DESKTOP%\Flare Download.lnk" 2>nul
if exist "%DESKTOP%\FlareDownload.lnk" del /f /q "%DESKTOP%\FlareDownload.lnk" 2>nul
if exist "%DESKTOP%\NeonTube.lnk" del /f /q "%DESKTOP%\NeonTube.lnk" 2>nul
if exist "%DESKTOP%\YouTube Downloader.lnk" del /f /q "%DESKTOP%\YouTube Downloader.lnk" 2>nul

:: Remove all Start Menu shortcuts
if exist "%STARTMENU%\Flare Download.lnk" del /f /q "%STARTMENU%\Flare Download.lnk" 2>nul
if exist "%STARTMENU%\FlareDownload.lnk" del /f /q "%STARTMENU%\FlareDownload.lnk" 2>nul
if exist "%STARTMENU%\NeonTube.lnk" del /f /q "%STARTMENU%\NeonTube.lnk" 2>nul

:: Remove old installation folders
if exist "%LOCALAPPDATA%\NeonTube" rmdir /s /q "%LOCALAPPDATA%\NeonTube" 2>nul
if exist "%LOCALAPPDATA%\YouTubeDownloader" rmdir /s /q "%LOCALAPPDATA%\YouTubeDownloader" 2>nul

ping -n 2 127.0.0.1 >nul
mkdir "%INSTALL_DIR%" 2>nul
goto :eof

:install_python
set "PYTHON_DIR=%INSTALL_DIR%\python"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"

if exist "%PYTHON_EXE%" (
    echo    [OK] Python already installed
    goto :eof
)

echo    Downloading Python 3.11...
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
set "PYTHON_ZIP=%INSTALL_DIR%\python.zip"

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { (New-Object Net.WebClient).DownloadFile('%PYTHON_URL%', '%PYTHON_ZIP%') } catch { exit 1 }}" 2>nul

if not exist "%PYTHON_ZIP%" (
    echo    ERROR: Download failed. Check internet connection.
    exit /b 1
)

echo    Extracting Python...
mkdir "%PYTHON_DIR%" 2>nul
powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force" 2>nul
del "%PYTHON_ZIP%" 2>nul

:: Enable pip
set "PTH_FILE=%PYTHON_DIR%\python311._pth"
if exist "%PTH_FILE%" (
    echo python311.zip> "%PTH_FILE%"
    echo .>> "%PTH_FILE%"
    echo Lib\site-packages>> "%PTH_FILE%"
    echo import site>> "%PTH_FILE%"
)

echo    Installing pip...
set "GETPIP=%INSTALL_DIR%\get-pip.py"
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('https://bootstrap.pypa.io/get-pip.py', '%GETPIP%')}" 2>nul
"%PYTHON_EXE%" "%GETPIP%" --no-warn-script-location >nul 2>&1
del "%GETPIP%" 2>nul

echo    [OK] Python installed
goto :eof

:install_ffmpeg
set "FFMPEG_DIR=%INSTALL_DIR%\ffmpeg"
set "FFMPEG_EXE=%FFMPEG_DIR%\ffmpeg.exe"

if exist "%FFMPEG_EXE%" (
    echo    [OK] FFmpeg already installed
    goto :eof
)

echo    Downloading FFmpeg...
set "FFMPEG_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
set "FFMPEG_ZIP=%INSTALL_DIR%\ffmpeg.zip"

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { (New-Object Net.WebClient).DownloadFile('%FFMPEG_URL%', '%FFMPEG_ZIP%') } catch { exit 1 }}" 2>nul

if not exist "%FFMPEG_ZIP%" (
    echo    [!] FFmpeg download failed (optional)
    goto :eof
)

echo    Extracting FFmpeg...
mkdir "%FFMPEG_DIR%" 2>nul
powershell -Command "Expand-Archive -Path '%FFMPEG_ZIP%' -DestinationPath '%INSTALL_DIR%\ffmpeg_temp' -Force" 2>nul
for /d %%i in ("%INSTALL_DIR%\ffmpeg_temp\ffmpeg-*") do (
    xcopy "%%i\bin\*.*" "%FFMPEG_DIR%\" /Y /Q >nul 2>&1
)
rmdir /s /q "%INSTALL_DIR%\ffmpeg_temp" 2>nul
del "%FFMPEG_ZIP%" 2>nul

echo    [OK] FFmpeg installed
goto :eof

:install_dependencies
set "PYTHON_EXE=%INSTALL_DIR%\python\python.exe"

echo    Installing customtkinter...
"%PYTHON_EXE%" -m pip install customtkinter --no-warn-script-location -q 2>nul

echo    Installing yt-dlp...
"%PYTHON_EXE%" -m pip install yt-dlp --no-warn-script-location -q 2>nul

echo    Installing Pillow...
"%PYTHON_EXE%" -m pip install Pillow --no-warn-script-location -q 2>nul

echo    Installing requests...
"%PYTHON_EXE%" -m pip install requests --no-warn-script-location -q 2>nul

echo    [OK] All components installed
goto :eof

:download_app
echo    Downloading Flare Download...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/youtube_downloader.py', '%INSTALL_DIR%\youtube_downloader.py')}" 2>nul
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/version.py', '%INSTALL_DIR%\version.py')}" 2>nul
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%GITHUB_RAW%/updater.py', '%INSTALL_DIR%\updater.py')}" 2>nul

if not exist "%INSTALL_DIR%\youtube_downloader.py" (
    echo    ERROR: Download failed. Check internet connection.
    exit /b 1
)

echo    [OK] Application downloaded
goto :eof

:create_shortcuts
set "PYTHON_EXE=%INSTALL_DIR%\python\python.exe"
set "PYTHON_DIR=%INSTALL_DIR%\python"
set "FFMPEG_DIR=%INSTALL_DIR%\ffmpeg"
set "APP_FILE=%INSTALL_DIR%\youtube_downloader.py"

:: Create launcher batch
set "LAUNCHER=%INSTALL_DIR%\FlareDownload.bat"
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo set "PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%FFMPEG_DIR%;%%PATH%%"
echo start "" "%PYTHON_EXE%" "%APP_FILE%"
echo exit
) > "%LAUNCHER%"

:: Create VBS wrapper (hides console)
set "VBS_LAUNCHER=%INSTALL_DIR%\FlareDownload.vbs"
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.Run chr^(34^) ^& "%LAUNCHER%" ^& chr^(34^), 0
echo Set WshShell = Nothing
) > "%VBS_LAUNCHER%"

:: Create Desktop shortcut
set "SHORTCUT=%DESKTOP%\Flare Download.lnk"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%VBS_LAUNCHER%'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = 'Multi-Platform Video Downloader'; $s.Save()" 2>nul

:: Create Start Menu shortcut
set "STARTMENU_SHORTCUT=%STARTMENU%\Flare Download.lnk"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTMENU_SHORTCUT%'); $s.TargetPath = '%VBS_LAUNCHER%'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = 'Multi-Platform Video Downloader'; $s.Save()" 2>nul

echo    [OK] Shortcuts created
goto :eof

:: ============================================================================
:: SUCCESS / ERROR
:: ============================================================================

:success
cls
echo.
echo    ======================================================
echo.
echo        FLARE DOWNLOAD
echo.
echo        Installation Complete!
echo.
echo    ======================================================
echo.
echo    How to use:
echo.
echo      1. Double-click "Flare Download" on your Desktop
echo      2. Paste a video URL
echo      3. Click DOWNLOAD
echo.
echo    ======================================================
echo.
set /p LAUNCH="    Launch Flare Download now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    start "" "%INSTALL_DIR%\FlareDownload.vbs"
)
echo.
echo    Thank you for using Flare Download!
echo.
pause
exit

:error
echo.
echo    ======================================================
echo    INSTALLATION FAILED
echo    ======================================================
echo.
echo    Please check your internet connection and try again.
echo.
pause
goto :menu
