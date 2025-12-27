@echo off
:: ============================================================================
:: FLARE DOWNLOAD - Windows Build Script
:: Creates a standalone .exe file that requires no installation
:: ============================================================================

echo.
echo    FLARE DOWNLOAD - Build Script
echo    ==============================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo    ERROR: Python not found!
    echo    Please install Python from python.org
    pause
    exit /b 1
)

:: Install PyInstaller if needed
echo    Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo    Installing PyInstaller...
    pip install pyinstaller
)

:: Install dependencies
echo    Installing dependencies...
pip install customtkinter Pillow -q

:: Clean old builds
echo    Cleaning old builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del /f /q *.spec

:: Build
echo.
echo    Building executable...
echo.

pyinstaller --onefile --windowed --clean ^
    --name="Flare Download" ^
    --add-data="version.py;." ^
    --add-data="updater.py;." ^
    --hidden-import=customtkinter ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    youtube_downloader.py

if exist "dist\Flare Download.exe" (
    echo.
    echo    ========================================
    echo    BUILD SUCCESSFUL!
    echo    ========================================
    echo.
    echo    Your executable is ready:
    echo    dist\Flare Download.exe
    echo.
    echo    Just copy this file to any Windows PC
    echo    and double-click to run!
    echo.
    echo    No Python or installation needed.
    echo    ========================================
) else (
    echo.
    echo    Build failed!
)

pause
