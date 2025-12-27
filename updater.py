#!/usr/bin/env python3
"""
Flare Download - Update Checker
Checks GitHub for new versions and handles updates.
Part of the Flare ecosystem.
"""

import os
import sys
import json
import shutil
import tempfile
import threading
import subprocess
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from typing import Optional, Tuple, Callable

try:
    from version import __version__, GITHUB_API_URL, GITHUB_REPO, GITHUB_RAW_URL
except ImportError:
    __version__ = "2.8.2"
    GITHUB_REPO = "contactmukundthiru-cyber/Multi-Platform-Downloader"
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"


class Updater:
    """Handles application updates from GitHub"""

    def __init__(self, callback: Optional[Callable] = None):
        self.current_version = __version__
        self.latest_version = None
        self.download_url = None
        self.release_notes = None
        self.callback = callback

    def _log(self, message: str):
        """Log message via callback if available"""
        if self.callback:
            self.callback(message)

    def parse_version(self, version_str: str) -> Tuple[int, ...]:
        """Parse version string to tuple for comparison"""
        version_str = version_str.lstrip('v')
        try:
            return tuple(int(x) for x in version_str.split('.'))
        except ValueError:
            return (0, 0, 0)

    def check_for_updates(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check GitHub for new releases.
        Returns: (update_available, latest_version, release_notes)
        """
        try:
            self._log("Checking for updates...")

            # Try GitHub API first
            request = Request(
                GITHUB_API_URL,
                headers={'User-Agent': 'FlareDownload-Updater'}
            )

            try:
                with urlopen(request, timeout=10) as response:
                    data = json.loads(response.read().decode())

                self.latest_version = data.get('tag_name', '').lstrip('v')
                self.release_notes = data.get('body', 'No release notes available.')
                self.download_url = f"https://github.com/{GITHUB_REPO}/releases/latest"

            except HTTPError:
                # Fall back to checking version.py directly
                request = Request(
                    f"{GITHUB_RAW_URL}/version.py",
                    headers={'User-Agent': 'FlareDownload-Updater'}
                )
                with urlopen(request, timeout=10) as response:
                    content = response.read().decode()

                for line in content.split('\n'):
                    if line.startswith('__version__'):
                        self.latest_version = line.split('=')[1].strip().strip('"\'')
                        break

                self.release_notes = "Check GitHub for details."
                self.download_url = f"https://github.com/{GITHUB_REPO}"

            if not self.latest_version:
                return False, None, None

            # Compare versions
            current = self.parse_version(self.current_version)
            latest = self.parse_version(self.latest_version)

            update_available = latest > current

            if update_available:
                self._log(f"New version available: {self.latest_version}")
            else:
                self._log(f"You have the latest version ({self.current_version})")

            return update_available, self.latest_version, self.release_notes

        except URLError as e:
            self._log(f"Connection error: {e.reason}")
            return False, None, None
        except Exception as e:
            self._log(f"Update check failed: {str(e)}")
            return False, None, None

    def check_async(self, callback: Callable[[bool, Optional[str], Optional[str]], None]):
        """
        Check for updates asynchronously.
        Calls callback with (update_available, latest_version, release_notes).
        """
        def _check():
            result = self.check_for_updates()
            callback(*result)

        thread = threading.Thread(target=_check, daemon=True)
        thread.start()

    def download_and_apply_update(self, progress_callback: Optional[Callable] = None) -> bool:
        """
        Download and apply the update from GitHub.
        Returns True on success.
        """
        try:
            self._log("Downloading update...")

            # Get the application directory
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.abspath(__file__))

            # Files to update
            update_files = [
                'youtube_downloader.py',
                'updater.py',
                'version.py'
            ]

            for filename in update_files:
                url = f"{GITHUB_RAW_URL}/{filename}"
                request = Request(url, headers={'User-Agent': 'FlareDownload-Updater'})

                try:
                    with urlopen(request, timeout=30) as response:
                        content = response.read().decode('utf-8')

                    filepath = os.path.join(app_dir, filename)

                    # Backup current file
                    if os.path.exists(filepath):
                        backup = filepath + '.backup'
                        try:
                            shutil.copy2(filepath, backup)
                        except:
                            pass

                    # Write new file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)

                    self._log(f"Updated: {filename}")

                except Exception as e:
                    self._log(f"Failed to update {filename}: {e}")

            self._log("Update complete! Please restart the application.")
            return True

        except Exception as e:
            self._log(f"Update failed: {str(e)}")
            return False

    def get_update_info(self) -> dict:
        """Get information about available update."""
        return {
            'current_version': self.current_version,
            'latest_version': self.latest_version,
            'update_available': self.latest_version is not None and
                               self.parse_version(self.latest_version) > self.parse_version(self.current_version),
            'download_url': self.download_url or f"https://github.com/{GITHUB_REPO}",
            'release_notes': self.release_notes or ""
        }


def check_for_updates_sync() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Convenience function to check for updates.
    Returns: (update_available, latest_version, release_notes)
    """
    updater = Updater()
    return updater.check_for_updates()


def update_yt_dlp() -> bool:
    """Update yt-dlp to latest version"""
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp', '-q'],
            check=True,
            capture_output=True
        )
        return True
    except Exception:
        return False


if __name__ == "__main__":
    print(f"Flare Download v{__version__}")
    print("Checking for updates...")
    print()

    updater = Updater(callback=print)
    has_update, version, notes = updater.check_for_updates()

    if has_update:
        print(f"\nNew version available: v{version}")
        print(f"\nRelease notes:\n{notes}")
        print(f"\nDownload: {updater.download_url}")
    else:
        print("\nYou have the latest version!")
