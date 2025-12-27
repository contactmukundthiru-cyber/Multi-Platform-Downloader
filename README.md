# NeonTube - Multi-Platform Video Downloader

A futuristic video downloader with a stunning dark-themed UI. Download from YouTube, TikTok, Instagram, Twitter, and 1000+ other sites.

![Version](https://img.shields.io/badge/version-2.2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-purple)

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
| **+ 1000 more sites** | | | |

## Features

### Core Features
- **Multi-Platform**: Download from 1000+ websites
- **Futuristic UI**: Dark theme with neon cyan/purple accents
- **Video Formats**: MP4, WebM, MKV, AVI, MOV
- **Audio Formats**: MP3, WAV, M4A, FLAC, AAC, Opus, OGG
- **Quality Options**: 8K, 4K, 2K, 1080p, 720p, 480p, 360p, 240p, 144p
- **Audio Bitrates**: 320, 256, 192, 128, 96, 64 kbps

### Advanced Features
- **Auto-Update**: Built-in update checker
- **Video Info Preview**: See details before downloading
- **Subtitle Download**: Auto-download subtitles
- **Thumbnail Download**: Save video thumbnails
- **Metadata Embedding**: Embed title, artist, album info
- **Cancel Downloads**: Stop downloads in progress
- **Real-time Progress**: Speed, ETA, and percentage display

## Quick Install

### One-Line Install (Linux/macOS)
```bash
curl -sSL https://raw.githubusercontent.com/contactmukundthiru-cyber/Multi-Platform-Downloader/main/install.sh | bash
```

### Windows
1. Download the latest release
2. Run `install.bat`
3. Double-click `NeonTube.bat` to launch

### Manual Installation
```bash
git clone https://github.com/contactmukundthiru-cyber/Multi-Platform-Downloader.git
cd Multi-Platform-Downloader
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python youtube_downloader.py
```

### GUI Installer
```bash
python installer_gui.py
```

## Requirements

- Python 3.8+
- FFmpeg (optional, for video merging)

### Installing FFmpeg

**Linux:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

## Usage

1. Launch NeonTube
2. Paste any video URL (YouTube, TikTok, Instagram, etc.)
3. Select Media Type (Video/Audio)
4. Choose Format and Quality
5. Click **DOWNLOAD**

## Screenshots

The application features:
- Glowing neon title animation
- Multi-platform support indicator
- Video/Audio toggle with format options
- Advanced options panel
- Real-time download progress with speed/ETA
- Console-style log viewer

## Building Releases

```bash
python build_release.py
```

This creates:
- `dist/NeonTube-vX.X.X-source.zip` - Full source
- `dist/NeonTube-vX.X.X-installer.zip` - Installer package
- `dist/NeonTube-vX.X.X-premium.zip` - Gumroad package
- `dist/checksums.txt` - SHA256 checksums
- `dist/RELEASE_NOTES.md` - Release notes template

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - See [LICENSE](LICENSE) file

## Support

- **GitHub Issues**: [Report bugs](https://github.com/contactmukundthiru-cyber/Multi-Platform-Downloader/issues)
- **Gumroad**: [Premium Support](https://gumroad.com)

---

Made with love by Mukund Thiru
