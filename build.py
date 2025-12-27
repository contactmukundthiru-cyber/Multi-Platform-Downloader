#!/usr/bin/env python3
"""
Flare Download - Build Script
Creates standalone executables for Windows, macOS, and Linux.

Usage:
    python build.py          # Build for current platform
    python build.py --all    # Build for all platforms (requires each OS)

Requirements:
    pip install pyinstaller
"""

import os
import sys
import shutil
import subprocess
import platform

# Build configuration
APP_NAME = "Flare Download"
SCRIPT_NAME = "youtube_downloader.py"
ICON_NAME = "icon.ico"  # Optional - create if you have one
VERSION = "2.6.1"

# Files to include
DATA_FILES = [
    "version.py",
    "updater.py",
]

def clean_build():
    """Remove old build artifacts."""
    dirs_to_remove = ["build", "dist", "__pycache__"]
    files_to_remove = ["*.spec"]

    for d in dirs_to_remove:
        if os.path.exists(d):
            print(f"Removing {d}/")
            shutil.rmtree(d)

    for pattern in files_to_remove:
        import glob
        for f in glob.glob(pattern):
            print(f"Removing {f}")
            os.remove(f)

def check_dependencies():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        return True

def build_executable():
    """Build the executable using PyInstaller."""

    system = platform.system().lower()
    print(f"\nBuilding for {platform.system()} ({platform.machine()})...")

    # Base PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # Single executable
        "--windowed",          # No console window (GUI app)
        "--clean",             # Clean cache
        f"--name={APP_NAME}",
    ]

    # Add data files
    for data_file in DATA_FILES:
        if os.path.exists(data_file):
            separator = ";" if system == "windows" else ":"
            cmd.append(f"--add-data={data_file}{separator}.")

    # Add icon if exists
    if os.path.exists(ICON_NAME):
        cmd.append(f"--icon={ICON_NAME}")

    # Hidden imports (modules that PyInstaller might miss)
    hidden_imports = [
        "customtkinter",
        "tkinter",
        "PIL",
        "PIL._tkinter_finder",
    ]
    for imp in hidden_imports:
        cmd.append(f"--hidden-import={imp}")

    # Add the main script
    cmd.append(SCRIPT_NAME)

    print(f"\nRunning: {' '.join(cmd)}\n")

    # Run PyInstaller
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)

        # Find the output
        if system == "windows":
            exe_path = os.path.join("dist", f"{APP_NAME}.exe")
        elif system == "darwin":
            exe_path = os.path.join("dist", f"{APP_NAME}.app")
        else:
            exe_path = os.path.join("dist", APP_NAME)

        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) if os.path.isfile(exe_path) else 0
            size_mb = size / (1024 * 1024)
            print(f"\nOutput: {exe_path}")
            if size > 0:
                print(f"Size: {size_mb:.1f} MB")

        print("\nTo distribute:")
        print(f"  1. Copy '{exe_path}' to users")
        print("  2. They just double-click to run!")
        print("  3. No Python or installation needed")
        print("=" * 60)
        return True
    else:
        print("\nBuild failed!")
        return False

def create_spec_file():
    """Create a custom .spec file for more control."""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{SCRIPT_NAME}'],
    pathex=[],
    binaries=[],
    datas=[
        ('version.py', '.'),
        ('updater.py', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'tkinter',
        'PIL',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''

    with open(f"{APP_NAME}.spec", "w") as f:
        f.write(spec_content)

    print(f"Created {APP_NAME}.spec")

def main():
    print("=" * 60)
    print(f"FLARE DOWNLOAD - Build Script v{VERSION}")
    print("=" * 60)

    # Check we're in the right directory
    if not os.path.exists(SCRIPT_NAME):
        print(f"Error: {SCRIPT_NAME} not found in current directory")
        print("Run this script from the project root")
        sys.exit(1)

    # Clean old builds
    if "--clean" in sys.argv or "-c" in sys.argv:
        clean_build()
        print("Cleaned build artifacts")
        return

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Clean and build
    clean_build()

    if build_executable():
        print("\nDone!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
