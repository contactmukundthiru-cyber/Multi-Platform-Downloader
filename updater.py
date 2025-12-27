#!/usr/bin/env python3
"""
NeonTube Updater Module
Handles version checking and automatic updates
"""

import os
import sys
import json
import shutil
import zipfile
import tempfile
import threading
import subprocess
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from typing import Optional, Tuple, Callable

from version import __version__, GITHUB_API_URL, GITHUB_REPO


class Updater:
    """Handles application updates from GitHub releases"""

    def __init__(self, callback: Optional[Callable] = None):
        self.current_version = __version__
        self.latest_version = None
        self.download_url = None
        self.release_notes = None
        self.callback = callback  # For progress updates

    def _log(self, message: str):
        """Log message via callback if available"""
        if self.callback:
            self.callback(message)
        print(message)

    def parse_version(self, version_str: str) -> Tuple[int, ...]:
        """Parse version string to tuple for comparison"""
        # Remove 'v' prefix if present
        version_str = version_str.lstrip('v')
        try:
            return tuple(int(x) for x in version_str.split('.'))
        except ValueError:
            return (0, 0, 0)

    def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check GitHub for new releases
        Returns: (update_available, latest_version, release_notes)
        """
        try:
            self._log("Checking for updates...")

            request = Request(
                GITHUB_API_URL,
                headers={'User-Agent': 'NeonTube-Updater'}
            )

            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode())

            self.latest_version = data.get('tag_name', '').lstrip('v')
            self.release_notes = data.get('body', 'No release notes available.')

            # Find download URL for the zip asset
            assets = data.get('assets', [])
            for asset in assets:
                if asset['name'].endswith('.zip'):
                    self.download_url = asset['browser_download_url']
                    break

            # If no zip asset, use source code zip
            if not self.download_url:
                self.download_url = data.get('zipball_url')

            # Compare versions
            current = self.parse_version(self.current_version)
            latest = self.parse_version(self.latest_version)

            update_available = latest > current

            if update_available:
                self._log(f"New version available: {self.latest_version}")
            else:
                self._log(f"You're running the latest version ({self.current_version})")

            return update_available, self.latest_version, self.release_notes

        except HTTPError as e:
            self._log(f"HTTP Error: {e.code}")
            return False, None, None
        except URLError as e:
            self._log(f"Connection error: {e.reason}")
            return False, None, None
        except Exception as e:
            self._log(f"Update check failed: {str(e)}")
            return False, None, None

    def download_update(self, progress_callback: Optional[Callable] = None) -> Optional[str]:
        """
        Download the latest release
        Returns: Path to downloaded file or None on failure
        """
        if not self.download_url:
            self._log("No download URL available")
            return None

        try:
            self._log(f"Downloading update from {self.download_url}...")

            request = Request(
                self.download_url,
                headers={'User-Agent': 'NeonTube-Updater'}
            )

            # Create temp file
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, 'neontube_update.zip')

            with urlopen(request, timeout=60) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                block_size = 8192

                with open(zip_path, 'wb') as f:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        downloaded += len(buffer)
                        f.write(buffer)

                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)

            self._log(f"Download complete: {zip_path}")
            return zip_path

        except Exception as e:
            self._log(f"Download failed: {str(e)}")
            return None

    def apply_update(self, zip_path: str) -> bool:
        """
        Apply the downloaded update
        Returns: True on success, False on failure
        """
        try:
            self._log("Applying update...")

            # Get the application directory
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.abspath(__file__))

            # Extract to temp location
            temp_extract = tempfile.mkdtemp()

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract)

            # Find the extracted folder (GitHub adds a folder with repo-name-version)
            extracted_items = os.listdir(temp_extract)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_extract, extracted_items[0])):
                source_dir = os.path.join(temp_extract, extracted_items[0])
            else:
                source_dir = temp_extract

            # Backup current files
            backup_dir = os.path.join(app_dir, '.backup')
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            os.makedirs(backup_dir)

            # Files to update
            update_files = [
                'youtube_downloader.py',
                'updater.py',
                'version.py',
                'requirements.txt'
            ]

            for filename in update_files:
                src = os.path.join(source_dir, filename)
                dst = os.path.join(app_dir, filename)
                backup = os.path.join(backup_dir, filename)

                if os.path.exists(dst):
                    shutil.copy2(dst, backup)

                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    self._log(f"Updated: {filename}")

            # Cleanup
            shutil.rmtree(temp_extract)
            os.remove(zip_path)

            self._log("Update applied successfully!")
            return True

        except Exception as e:
            self._log(f"Update failed: {str(e)}")
            return False

    def update_dependencies(self) -> bool:
        """Update Python dependencies after an update"""
        try:
            self._log("Updating dependencies...")

            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.abspath(__file__))

            requirements_path = os.path.join(app_dir, 'requirements.txt')

            if os.path.exists(requirements_path):
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '-r', requirements_path, '-q'],
                    check=True
                )
                self._log("Dependencies updated successfully!")
                return True
            return False

        except Exception as e:
            self._log(f"Dependency update failed: {str(e)}")
            return False


def check_yt_dlp_update() -> Tuple[bool, str]:
    """Check if yt-dlp needs updating"""
    try:
        result = subprocess.run(
            ['yt-dlp', '--version'],
            capture_output=True,
            text=True
        )
        current_version = result.stdout.strip()

        # Check for update
        result = subprocess.run(
            ['pip', 'index', 'versions', 'yt-dlp'],
            capture_output=True,
            text=True
        )

        return True, current_version
    except Exception:
        return False, "Unknown"


def update_yt_dlp() -> bool:
    """Update yt-dlp to latest version"""
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'],
            check=True
        )
        return True
    except Exception:
        return False


if __name__ == "__main__":
    # Test the updater
    updater = Updater(callback=print)
    has_update, version, notes = updater.check_for_updates()

    if has_update:
        print(f"\nNew version: {version}")
        print(f"Release notes:\n{notes}")
