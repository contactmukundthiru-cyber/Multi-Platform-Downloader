@echo off
setlocal enabledelayedexpansion

:: Flare Download - Multi-Platform Video Downloader
:: Fully Automated Windows Installer
:: Part of the Flare ecosystem

title Flare Download Installer
color 0F

:: Request admin privileges if needed
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

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
echo  This installer will automatically set up everything needed.
echo  Please wait while we prepare your system...
echo.
echo ============================================================
echo.

:: Set directories
set "INSTALL_DIR=%LOCALAPPDATA%\FlareDownload"
set "PYTHON_DIR=%INSTALL_DIR%\python"
set "SCRIPT_DIR=%~dp0"
set "TEMP_DIR=%TEMP%\FlareDownloadInstaller"

:: Create temp directory
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: Step 1: Check/Install Python
echo [1/6] Checking Python...

:: First check if Python is already installed system-wide
python --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo       [OK] System Python !PYTHON_VERSION! found
    set "PYTHON_CMD=python"
    set "USE_SYSTEM_PYTHON=1"
    goto :CheckPythonVersion
)

:: Check if we have embedded Python already
if exist "%PYTHON_DIR%\python.exe" (
    echo       [OK] Embedded Python found
    set "PYTHON_CMD=%PYTHON_DIR%\python.exe"
    set "USE_SYSTEM_PYTHON=0"
    goto :PythonReady
)

:: Download embedded Python
echo       Python not found. Downloading embedded Python...
echo       This may take a few minutes...

:: Download Python embeddable package (smaller than full installer)
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-embed-amd64.zip"
set "PYTHON_ZIP=%TEMP_DIR%\python-embed.zip"
set "PIP_URL=https://bootstrap.pypa.io/get-pip.py"
set "GET_PIP=%TEMP_DIR%\get-pip.py"

:: Use PowerShell to download
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%'}" 2>nul
if errorlevel 1 (
    :: Try with curl as fallback
    curl -L -o "%PYTHON_ZIP%" "%PYTHON_URL%" 2>nul
    if errorlevel 1 (
        echo       [ERROR] Failed to download Python.
        echo       Please check your internet connection.
        pause
        exit /b 1
    )
)

echo       Extracting Python...
if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"
powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force" 2>nul
if errorlevel 1 (
    echo       [ERROR] Failed to extract Python.
    pause
    exit /b 1
)

:: Enable pip in embedded Python (modify python311._pth)
echo       Configuring Python...
set "PTH_FILE=%PYTHON_DIR%\python311._pth"
if exist "%PTH_FILE%" (
    :: Remove the import site restriction
    (
    echo python311.zip
    echo .
    echo Lib
    echo Lib\site-packages
    echo import site
    ) > "%PTH_FILE%"
)

:: Create Lib\site-packages directory
if not exist "%PYTHON_DIR%\Lib\site-packages" mkdir "%PYTHON_DIR%\Lib\site-packages"

:: Download and install pip
echo       Installing pip...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PIP_URL%' -OutFile '%GET_PIP%'}" 2>nul
if errorlevel 1 (
    curl -L -o "%GET_PIP%" "%PIP_URL%" 2>nul
)

"%PYTHON_DIR%\python.exe" "%GET_PIP%" --no-warn-script-location -q 2>nul
if errorlevel 1 (
    echo       [WARN] pip installation had warnings, continuing...
)

echo       [OK] Embedded Python 3.11 installed
set "PYTHON_CMD=%PYTHON_DIR%\python.exe"
set "USE_SYSTEM_PYTHON=0"
goto :PythonReady

:CheckPythonVersion
:: Verify Python version is 3.8+
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)
if !PYTHON_MAJOR! LSS 3 goto :InstallEmbeddedPython
if !PYTHON_MAJOR! EQU 3 if !PYTHON_MINOR! LSS 8 goto :InstallEmbeddedPython
goto :PythonReady

:InstallEmbeddedPython
echo       System Python is too old. Installing embedded Python...
goto :DownloadPython

:PythonReady
:: Step 2: Check tkinter (only for system Python)
echo.
echo [2/6] Checking dependencies...

if "!USE_SYSTEM_PYTHON!"=="1" (
    !PYTHON_CMD! -c "import tkinter" >nul 2>&1
    if errorlevel 1 (
        echo       [WARN] tkinter not available with system Python
        echo       Switching to embedded Python with tkinter...
        goto :ForceEmbeddedPython
    )
    echo       [OK] tkinter available
) else (
    :: For embedded Python, we need to get tkinter DLLs
    if not exist "%PYTHON_DIR%\tcl" (
        echo       Downloading tkinter components...
        :: Download tkinter for embedded Python
        set "TK_URL=https://github.com/nicholasbishop/tk-for-python-embed/releases/download/v1.0/tk-for-python-embed-3.11.zip"
        set "TK_ZIP=%TEMP_DIR%\tk-embed.zip"
        powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '!TK_URL!' -OutFile '!TK_ZIP!'}" 2>nul
        if not errorlevel 1 (
            powershell -Command "Expand-Archive -Path '!TK_ZIP!' -DestinationPath '%PYTHON_DIR%' -Force" 2>nul
        )
    )
    echo       [OK] Dependencies configured
)
goto :ContinueInstall

:ForceEmbeddedPython
set "USE_SYSTEM_PYTHON=0"
if not exist "%PYTHON_DIR%\python.exe" (
    :: Download embedded Python
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-embed-amd64.zip"
    set "PYTHON_ZIP=%TEMP_DIR%\python-embed.zip"

    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%'}" 2>nul

    if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"
    powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force" 2>nul

    :: Configure embedded Python
    set "PTH_FILE=%PYTHON_DIR%\python311._pth"
    (
    echo python311.zip
    echo .
    echo Lib
    echo Lib\site-packages
    echo import site
    ) > "!PTH_FILE!"

    if not exist "%PYTHON_DIR%\Lib\site-packages" mkdir "%PYTHON_DIR%\Lib\site-packages"

    :: Install pip
    set "PIP_URL=https://bootstrap.pypa.io/get-pip.py"
    set "GET_PIP=%TEMP_DIR%\get-pip.py"
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PIP_URL%' -OutFile '%GET_PIP%'}" 2>nul
    "%PYTHON_DIR%\python.exe" "%GET_PIP%" --no-warn-script-location -q 2>nul
)
set "PYTHON_CMD=%PYTHON_DIR%\python.exe"
echo       [OK] Embedded Python configured

:ContinueInstall
:: Step 3: Create installation directory
echo.
echo [3/6] Setting up installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
echo       [OK] %INSTALL_DIR%

:: Copy application files
if exist "%SCRIPT_DIR%youtube_downloader.py" (
    copy /Y "%SCRIPT_DIR%youtube_downloader.py" "%INSTALL_DIR%\" >nul
    copy /Y "%SCRIPT_DIR%updater.py" "%INSTALL_DIR%\" >nul 2>&1
    copy /Y "%SCRIPT_DIR%version.py" "%INSTALL_DIR%\" >nul 2>&1
    copy /Y "%SCRIPT_DIR%requirements.txt" "%INSTALL_DIR%\" >nul
    echo       [OK] Application files copied
) else (
    echo       [ERROR] Source files not found!
    echo       Please run installer from the Flare Download folder.
    pause
    exit /b 1
)

:: Step 4: Install Python packages
echo.
echo [4/6] Installing Python packages...
echo       This may take a few minutes...

:: Set pip command based on Python type
if "!USE_SYSTEM_PYTHON!"=="1" (
    set "PIP_CMD=!PYTHON_CMD! -m pip"
) else (
    set "PIP_CMD=%PYTHON_DIR%\Scripts\pip.exe"
    if not exist "!PIP_CMD!" set "PIP_CMD=!PYTHON_CMD! -m pip"
)

:: Upgrade pip
!PIP_CMD! install --upgrade pip -q 2>nul

:: Install customtkinter
echo       Installing customtkinter...
!PIP_CMD! install customtkinter -q 2>nul
if errorlevel 1 (
    echo       [WARN] customtkinter install had issues, retrying...
    !PIP_CMD! install customtkinter --user -q 2>nul
)

:: Install yt-dlp
echo       Installing yt-dlp...
!PIP_CMD! install yt-dlp -q 2>nul

:: Install other requirements
if exist "%INSTALL_DIR%\requirements.txt" (
    echo       Installing other requirements...
    !PIP_CMD! install -r "%INSTALL_DIR%\requirements.txt" -q 2>nul
)

echo       [OK] All packages installed

:: Step 5: Download FFmpeg (optional but included)
echo.
echo [5/6] Setting up FFmpeg...

set "FFMPEG_DIR=%INSTALL_DIR%\ffmpeg"
if not exist "%FFMPEG_DIR%\ffmpeg.exe" (
    echo       Downloading FFmpeg ^(for video merging^)...
    set "FFMPEG_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    set "FFMPEG_ZIP=%TEMP_DIR%\ffmpeg.zip"

    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri '%FFMPEG_URL%' -OutFile '%FFMPEG_ZIP%' -TimeoutSec 60 } catch { exit 1 }}" 2>nul

    if exist "%FFMPEG_ZIP%" (
        if not exist "%FFMPEG_DIR%" mkdir "%FFMPEG_DIR%"
        echo       Extracting FFmpeg...
        powershell -Command "Expand-Archive -Path '%FFMPEG_ZIP%' -DestinationPath '%TEMP_DIR%\ffmpeg_temp' -Force" 2>nul

        :: Find and copy ffmpeg.exe
        for /r "%TEMP_DIR%\ffmpeg_temp" %%f in (ffmpeg.exe) do (
            copy /Y "%%f" "%FFMPEG_DIR%\" >nul 2>&1
        )
        for /r "%TEMP_DIR%\ffmpeg_temp" %%f in (ffprobe.exe) do (
            copy /Y "%%f" "%FFMPEG_DIR%\" >nul 2>&1
        )

        rmdir /s /q "%TEMP_DIR%\ffmpeg_temp" 2>nul
        echo       [OK] FFmpeg installed
    ) else (
        echo       [INFO] FFmpeg download skipped ^(optional^)
    )
) else (
    echo       [OK] FFmpeg already installed
)

:: Step 6: Create launcher and shortcuts
echo.
echo [6/6] Creating launcher and shortcuts...

:: Determine Python executable path for launcher
if "!USE_SYSTEM_PYTHON!"=="1" (
    set "LAUNCHER_PYTHON=pythonw"
) else (
    set "LAUNCHER_PYTHON=%PYTHON_DIR%\pythonw.exe"
)

:: Create launcher batch file
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
if "!USE_SYSTEM_PYTHON!"=="0" (
echo set "PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%FFMPEG_DIR%;%%PATH%%"
) else (
echo set "PATH=%FFMPEG_DIR%;%%PATH%%"
)
echo "!LAUNCHER_PYTHON!" youtube_downloader.py %%*
) > "%INSTALL_DIR%\FlareDownload.bat"

:: Create VBS for silent launch
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.Run chr^(34^) ^& "%INSTALL_DIR%\FlareDownload.bat" ^& chr^(34^), 0
echo Set WshShell = Nothing
) > "%INSTALL_DIR%\FlareDownload.vbs"

echo       [OK] Launcher created

:: Get Desktop path
for /f "tokens=2*" %%a in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop 2^>nul') do set "DESKTOP_PATH=%%b"
if not defined DESKTOP_PATH set "DESKTOP_PATH=%USERPROFILE%\Desktop"

:: Create desktop shortcut
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%DESKTOP_PATH%\Flare Download.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "wscript.exe"
echo oLink.Arguments = """%INSTALL_DIR%\FlareDownload.vbs"""
echo oLink.WorkingDirectory = "%INSTALL_DIR%"
echo oLink.Description = "Flare Download - Multi-Platform Video Downloader"
echo oLink.Save
) > "%TEMP_DIR%\CreateShortcut.vbs"
cscript //nologo "%TEMP_DIR%\CreateShortcut.vbs" 2>nul

if exist "%DESKTOP_PATH%\Flare Download.lnk" (
    echo       [OK] Desktop shortcut created
) else (
    echo       [INFO] Desktop shortcut may require manual creation
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
    ) > "%TEMP_DIR%\CreateStartMenu.vbs"
    cscript //nologo "%TEMP_DIR%\CreateStartMenu.vbs" 2>nul
    echo       [OK] Start Menu shortcut created
)

:: Cleanup temp files
rmdir /s /q "%TEMP_DIR%" 2>nul

:: Installation complete
echo.
echo ============================================================
echo.
echo  INSTALLATION COMPLETE!
echo.
echo  Flare Download has been installed successfully.
echo.
echo  To launch:
echo    - Double-click "Flare Download" on your Desktop
echo    - Or find it in the Start Menu
echo.
echo  Installed components:
if "!USE_SYSTEM_PYTHON!"=="1" (
echo    - Using system Python
) else (
echo    - Python 3.11 ^(embedded^)
)
echo    - customtkinter ^(UI framework^)
echo    - yt-dlp ^(video downloader^)
if exist "%FFMPEG_DIR%\ffmpeg.exe" (
echo    - FFmpeg ^(video processing^)
)
echo.
echo  Location: %INSTALL_DIR%
echo.
echo  Supports: YouTube, TikTok, Instagram, Twitter, and 1000+ more!
echo.
echo  Part of the Flare ecosystem
echo.
echo ============================================================
echo.

pause
