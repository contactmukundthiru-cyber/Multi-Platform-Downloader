#!/usr/bin/env python3
"""
Flare Download Release Builder
Creates distribution packages for GitHub releases
"""

import os
import sys
import shutil
import zipfile
import hashlib
from datetime import datetime
from pathlib import Path

# Import version info
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from version import __version__, __app_name__


class ReleaseBuilder:
    """Builds release packages for distribution"""

    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.dist_dir = os.path.join(self.project_dir, 'dist')
        self.version = __version__

        # Files to include in release
        self.release_files = [
            'youtube_downloader.py',
            'updater.py',
            'version.py',
            'requirements.txt',
            'README.md',
            'LICENSE',
            'install.sh',
            'install.bat',
            'build_installer.bat',
            'installer.iss',
        ]

    def clean_dist(self):
        """Clean the dist directory"""
        if os.path.exists(self.dist_dir):
            shutil.rmtree(self.dist_dir)
        os.makedirs(self.dist_dir)
        print("[+] Cleaned dist directory")

    def create_license(self):
        """Create LICENSE file if it doesn't exist"""
        license_path = os.path.join(self.project_dir, 'LICENSE')
        if not os.path.exists(license_path):
            with open(license_path, 'w') as f:
                f.write(f"""MIT License

Copyright (c) {datetime.now().year} Mukund Thiru

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")
            print("[+] Created LICENSE file")

    def build_source_zip(self):
        """Create source distribution zip"""
        zip_name = f"FlareDownload-v{self.version}-source.zip"
        zip_path = os.path.join(self.dist_dir, zip_name)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename in self.release_files:
                filepath = os.path.join(self.project_dir, filename)
                if os.path.exists(filepath):
                    zf.write(filepath, f"FlareDownload/{filename}")
                    print(f"    Added: {filename}")

        print(f"[+] Created: {zip_name}")
        return zip_path

    def calculate_checksums(self):
        """Calculate SHA256 checksums for all dist files"""
        checksums = {}
        checksum_file = os.path.join(self.dist_dir, 'checksums.txt')

        for filename in os.listdir(self.dist_dir):
            if filename.endswith('.zip') or filename.endswith('.exe'):
                filepath = os.path.join(self.dist_dir, filename)
                with open(filepath, 'rb') as f:
                    sha256 = hashlib.sha256(f.read()).hexdigest()
                checksums[filename] = sha256

        with open(checksum_file, 'w') as f:
            f.write(f"Flare Download v{self.version} - SHA256 Checksums\n")
            f.write("=" * 50 + "\n\n")
            for name, checksum in checksums.items():
                f.write(f"{checksum}  {name}\n")

        print("[+] Generated checksums.txt")
        return checksums

    def create_release_notes(self):
        """Create release notes template"""
        notes_path = os.path.join(self.dist_dir, 'RELEASE_NOTES.md')

        with open(notes_path, 'w') as f:
            f.write(f"""# Flare Download v{self.version} Release

## What's New
- Add your release notes here

## Features
- Multi-platform video downloader (YouTube, TikTok, Instagram, Twitter, and 1000+ sites)
- Cinematic dark UI with animated ember effects
- Video: MP4, WebM, MKV, AVI, MOV
- Audio: MP3, WAV, M4A, FLAC, AAC, Opus
- Quality: 4K to 360p video, 320-96 kbps audio
- Auto-update functionality via GitHub

## Installation

### Windows Installer (Recommended)
1. Download `FlareDownload_Setup_{self.version}.exe`
2. Run the installer
3. Done! Find "Flare Download" in Start Menu

### Manual Install
1. Download `FlareDownload-v{self.version}-source.zip`
2. Extract and run `install.bat` (Windows) or `install.sh` (Linux/Mac)

## Requirements
- Windows 10/11, macOS 10.14+, or Linux
- Internet connection for downloading

## Checksums
See `checksums.txt` for SHA256 verification.
""")

        print("[+] Created RELEASE_NOTES.md")

    def build_all(self):
        """Build all release packages"""
        print("\n" + "=" * 50)
        print(f"  Building Flare Download v{self.version} Release")
        print("=" * 50 + "\n")

        self.clean_dist()
        self.create_license()

        print("\n[*] Building packages...")
        self.build_source_zip()

        print("\n[*] Generating checksums...")
        self.calculate_checksums()

        print("\n[*] Creating release notes...")
        self.create_release_notes()

        print("\n" + "=" * 50)
        print("  BUILD COMPLETE!")
        print("=" * 50)
        print(f"\nRelease files in: {self.dist_dir}")
        print("\nFiles created:")
        for f in os.listdir(self.dist_dir):
            size = os.path.getsize(os.path.join(self.dist_dir, f))
            print(f"  - {f} ({size:,} bytes)")

        print("\n[*] Next steps:")
        print("  1. Review RELEASE_NOTES.md and add changelog")
        print("  2. Build Windows installer: build_installer.bat")
        print("  3. Upload to GitHub Releases:")
        print(f"     git tag v{self.version}")
        print(f"     git push origin v{self.version}")


def main():
    builder = ReleaseBuilder()
    builder.build_all()


if __name__ == "__main__":
    main()
