@echo off
setlocal enabledelayedexpansion

:: NeonTube Multi-Platform Video Downloader - Windows Installer
:: https://github.com/contactmukundthiru-cyber/Multi-Platform-Downloader

title NeonTube Installer

echo.
echo   _   _                  _____      _
echo  ^| \ ^| ^|                ^|_   _^|    ^| ^|
echo  ^|  \^| ^| ___  ___  _ __   ^| ^|_   _^| ^|__   ___
echo  ^| . ` ^|/ _ \/ _ \^| '_ \  ^| ^| ^| ^| ^| '_ \ / _ \
echo  ^| ^|\  ^|  __/ (_) ^| ^| ^| ^| ^| ^| ^|_^| ^| ^|_) ^|  __/
echo  ^|_^| \_^|\___^|\___/^|_^| ^|_^| \_/\__,_^|_.__/ \___^|
echo.
echo  Multi-Platform Video Downloader
echo  YouTube ^| TikTok ^| Instagram ^| Twitter ^| 1000+ sites
echo.
echo ============================================================

:: Set install directory
set "INSTALL_DIR=%LOCALAPPDATA%\NeonTube"

:: Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo       [ERROR] Python not found!
    echo       Download from: https://python.org
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo       [OK] Python %PYTHON_VERSION% found

:: Create directory
echo.
echo [2/5] Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
echo       [OK] %INSTALL_DIR%

:: Copy files
echo.
echo [3/5] Copying application files...
set "SCRIPT_DIR=%~dp0"

if exist "%SCRIPT_DIR%youtube_downloader.py" (
    copy /Y "%SCRIPT_DIR%youtube_downloader.py" "%INSTALL_DIR%\" >nul
    copy /Y "%SCRIPT_DIR%updater.py" "%INSTALL_DIR%\" >nul 2>&1
    copy /Y "%SCRIPT_DIR%version.py" "%INSTALL_DIR%\" >nul 2>&1
    copy /Y "%SCRIPT_DIR%requirements.txt" "%INSTALL_DIR%\" >nul
    echo       [OK] Files copied
) else (
    echo       [ERROR] Source files not found
    pause
    exit /b 1
)

:: Create virtual environment
echo.
echo [4/5] Setting up Python environment...
if exist "%INSTALL_DIR%\venv" rmdir /s /q "%INSTALL_DIR%\venv"
python -m venv "%INSTALL_DIR%\venv"
call "%INSTALL_DIR%\venv\Scripts\activate.bat"

python -m pip install --upgrade pip -q
pip install -r "%INSTALL_DIR%\requirements.txt" -q
pip install yt-dlp -q
echo       [OK] Dependencies installed

:: Create launcher
echo.
echo [5/5] Creating launcher...

(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo call venv\Scripts\activate.bat
echo pythonw youtube_downloader.py
) > "%INSTALL_DIR%\NeonTube.bat"

:: Create VBS for silent launch
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.Run chr^(34^) ^& "%INSTALL_DIR%\NeonTube.bat" ^& chr^(34^), 0
echo Set WshShell = Nothing
) > "%INSTALL_DIR%\NeonTube.vbs"

:: Create desktop shortcut
echo       Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\NeonTube.lnk'); $Shortcut.TargetPath = 'wscript.exe'; $Shortcut.Arguments = '\"%INSTALL_DIR%\NeonTube.vbs\"'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Multi-Platform Video Downloader'; $Shortcut.Save()"

echo       [OK] Desktop shortcut created

echo.
echo ============================================================
echo.
echo  INSTALLATION COMPLETE!
echo.
echo  To run NeonTube:
echo    - Double-click the desktop shortcut
echo    - Or run: %INSTALL_DIR%\NeonTube.bat
echo.
echo  Supports: YouTube, TikTok, Instagram, Twitter, and 1000+ more!
echo.
echo ============================================================
echo.

pause
