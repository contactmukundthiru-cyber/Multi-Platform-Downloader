# Flare Download - Multi-Platform Video Downloader

Part of the **Flare ecosystem**. Download videos from YouTube, TikTok, Instagram, Twitter, and 1000+ other sites.

![Version](https://img.shields.io/badge/version-2.8.2-ff4500)
![Python](https://img.shields.io/badge/python-3.8+-ff6b35)
![License](https://img.shields.io/badge/license-MIT-ff8c00)
![Build](https://img.shields.io/github/actions/workflow/status/contactmukundthiru-cyber/Multi-Platform-Downloader/build.yml?label=build)

---

## Super Easy Installation (No Technical Knowledge Needed!)

### Windows - Download the Installer

**Option 1: Windows Installer (Recommended)**
1. Go to [Releases](https://github.com/contactmukundthiru-cyber/Multi-Platform-Downloader/releases)
2. Download `FlareDownload_Setup_2.8.2.exe`
3. Run the installer
4. Done! Find "Flare Download" in your Start Menu and Desktop

**Option 2: Portable Script**
1. Download the ZIP from this page
2. Extract and double-click `install.bat`
3. A "Flare Download" shortcut will appear on your Desktop

The installer provides: Install, Repair, Update, and Uninstall functionality.

---

### macOS - Just Download & Double-Click!

1. **Download** the ZIP from this page
2. **Extract** the ZIP file
3. **Double-click** `Install Flare Download.command`
4. If prompted, click "Open" to allow the installer
5. **Done!** Find "Flare Download" in your Applications folder

---

### Linux

```bash
curl -sSL https://raw.githubusercontent.com/contactmukundthiru-cyber/Multi-Platform-Downloader/main/install.sh | bash
```

Or download and run `install.sh` directly.

---

## Supported Platforms

| Platform | Videos | Audio | Stories/Reels |
|----------|--------|-------|---------------|
| YouTube | Yes | Yes | Yes (Shorts) |
| TikTok | Yes | Yes | Yes |
| Instagram | Yes | Yes | Yes |
| Twitter/X | Yes | Yes | Yes |
| Facebook | Yes | Yes | Yes |
| Vimeo | Yes | Yes | - |
| Reddit | Yes | Yes | - |
| Twitch | Yes | Yes | Clips |
| SoundCloud | - | Yes | - |
| Spotify | - | Yes | - |
| **+ 1000 more** | | | |

## Features

- **Multi-Platform**: Download from 1000+ websites
- **Cinematic UI**: Clean dark theme with subtle animations
- **Auto-Updates**: Checks GitHub for new versions automatically
- **Video Formats**: MP4, WebM, MKV, MOV, AVI
- **Audio Formats**: MP3, M4A, WAV, FLAC, Opus, AAC
- **Quality Options**: 4K, 1080p, 720p, 480p, 360p
- **Audio Bitrates**: 320k, 256k, 192k, 128k, 96k
- **Progress Bar**: Clean animated progress indicator
- **Clean Uninstall**: Removes all files and shortcuts

## How to Use

1. **Open** Flare Download (double-click the shortcut)
2. **Paste** any video URL (or click PASTE button)
3. **Select** Video or Audio
4. **Choose** Format and Quality
5. **Click** DOWNLOAD

## Auto-Updates

Flare Download automatically checks for updates when launched. You can also manually check by clicking "Check Updates" in the footer.

When a new version is available:
1. You'll see a notification in the app
2. Click to open the download page
3. Download and run the new installer
4. The installer automatically removes old versions

---

## For Developers

### Building the Windows Installer

The build script automatically downloads and installs all required tools.

**Requirements:**
- Windows 10/11
- Python 3.8+
- Internet connection

**Build Steps:**

```batch
# Just run this - it handles everything automatically
build_installer.bat
```

This will:
1. Install PyInstaller and Python dependencies
2. Download and install Inno Setup (if not found)
3. Build `dist\Flare Download.exe` (standalone executable)
4. Create `installer_output\FlareDownload_Setup_2.8.2.exe` (installer)

### Manual Build

```batch
# Step 1: Install dependencies
pip install pyinstaller customtkinter Pillow yt-dlp

# Step 2: Build with PyInstaller
pyinstaller --onefile --windowed --name="Flare Download" ^
    --add-data="version.py;." --add-data="updater.py;." ^
    --hidden-import=customtkinter --hidden-import=PIL ^
    --hidden-import=yt_dlp youtube_downloader.py

# Step 3: Build installer with Inno Setup
# Open installer.iss in Inno Setup and click Build > Compile
```

### CI/CD with GitHub Actions

The repository includes automated builds via GitHub Actions:

- **Every push to main**: Builds and uploads artifacts
- **Tagged releases (v*)**: Automatically creates a GitHub Release with installer attached

**To release a new version:**

```bash
# 1. Update version in version.py and installer.iss
# 2. Commit and push
git add .
git commit -m "Release v2.9.0"
git push

# 3. Create and push tag
git tag v2.9.0
git push origin v2.9.0
```

GitHub Actions will automatically build and attach the installer to the release.

### Project Structure

```
flare-download/
├── youtube_downloader.py  # Main application
├── version.py             # Version info and GitHub config
├── updater.py             # Auto-update functionality
├── installer.iss          # Inno Setup installer script
├── build_installer.bat    # Windows build script
├── install.bat            # User installation script
├── .github/
│   └── workflows/
│       └── build.yml      # GitHub Actions workflow
└── README.md
```

## Troubleshooting

### App won't open
- Ensure Python 3.8+ is installed with tkinter
- Run from terminal to see error messages: `python youtube_downloader.py`

### Paste button doesn't work
- Copy a URL to clipboard first
- Try Ctrl+V directly in the URL field

### Download fails
- Check your internet connection
- Some sites may require cookies or authentication
- Try updating yt-dlp: `pip install --upgrade yt-dlp`

### Build fails
- Ensure Python is in PATH
- Try: `pip install --upgrade pyinstaller customtkinter Pillow yt-dlp`
- Check for syntax errors: `python -m py_compile youtube_downloader.py`

## Part of Flare

Flare Download is part of the Flare ecosystem - a suite of modern, fire-themed applications.

## License

MIT License

---

Made by Mukund Thiru
