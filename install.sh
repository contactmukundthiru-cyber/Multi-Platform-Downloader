#!/bin/bash

# Flare Download - Multi-Platform Video Downloader - Installation Script
# Part of the Flare ecosystem
# https://github.com/contactmukundthiru-cyber/Multi-Platform-Downloader

set -e

# Colors - Flare fire theme
ORANGE='\033[0;33m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
BOLD='\033[1m'

# Banner
echo -e "${RED}"
echo "  ______ _                  "
echo " |  ____| |                 "
echo " | |__  | | __ _ _ __ ___   "
echo " |  __| | |/ _\` | '__/ _ \  "
echo " | |    | | (_| | | |  __/  "
echo " |_|    |_|\__,_|_|  \___|  "
echo -e "${NC}"
echo -e "${ORANGE}${BOLD}DOWNLOAD${NC}"
echo -e "${YELLOW}Multi-Platform Video Downloader${NC}"
echo -e "YouTube | TikTok | Instagram | Twitter | 1000+ sites"
echo ""

# Determine install directory
if [ -n "$1" ]; then
    INSTALL_DIR="$1"
else
    INSTALL_DIR="$HOME/.local/share/flare-download"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"

echo -e "${ORANGE}[1/5]${NC} Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "      ${GREEN}Python $PYTHON_VERSION found${NC}"
else
    echo -e "      ${RED}Python 3 is not installed!${NC}"
    echo "      Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "      ${RED}Python 3.8 or higher is required${NC}"
    exit 1
fi

# Create installation directory
echo ""
echo -e "${ORANGE}[2/5]${NC} Creating installation directory..."
mkdir -p "$INSTALL_DIR"
echo -e "      ${GREEN}Directory: $INSTALL_DIR${NC}"

# Copy or download files
echo ""
echo -e "${ORANGE}[3/5]${NC} Installing application files..."

# If running from source directory
if [ -f "$SCRIPT_DIR/youtube_downloader.py" ]; then
    cp "$SCRIPT_DIR/youtube_downloader.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/updater.py" "$INSTALL_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR/version.py" "$INSTALL_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true
    echo -e "      ${GREEN}Files copied from source${NC}"
else
    # Download from GitHub
    echo "      Downloading from GitHub..."
    GITHUB_RAW="https://raw.githubusercontent.com/contactmukundthiru-cyber/Multi-Platform-Downloader/main"
    curl -sSL "$GITHUB_RAW/youtube_downloader.py" -o "$INSTALL_DIR/youtube_downloader.py"
    curl -sSL "$GITHUB_RAW/updater.py" -o "$INSTALL_DIR/updater.py"
    curl -sSL "$GITHUB_RAW/version.py" -o "$INSTALL_DIR/version.py"
    curl -sSL "$GITHUB_RAW/requirements.txt" -o "$INSTALL_DIR/requirements.txt"
    echo -e "      ${GREEN}Files downloaded${NC}"
fi

# Create virtual environment
echo ""
echo -e "${ORANGE}[4/5]${NC} Setting up Python environment..."
if [ -d "$INSTALL_DIR/venv" ]; then
    echo "      Removing old virtual environment..."
    rm -rf "$INSTALL_DIR/venv"
fi

python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"

pip install --upgrade pip -q
pip install -r "$INSTALL_DIR/requirements.txt" -q
pip install yt-dlp -q

echo -e "      ${GREEN}Dependencies installed${NC}"

# Create launcher
echo ""
echo -e "${ORANGE}[5/5]${NC} Creating launcher..."

cat > "$INSTALL_DIR/flare-download" << 'LAUNCHER'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
source venv/bin/activate
python3 youtube_downloader.py "$@"
LAUNCHER

chmod +x "$INSTALL_DIR/flare-download"

# Create symlink in ~/.local/bin
mkdir -p "$HOME/.local/bin"
ln -sf "$INSTALL_DIR/flare-download" "$HOME/.local/bin/flare-download"

# Create desktop entry
if [ -d "$HOME/.local/share/applications" ]; then
    cat > "$HOME/.local/share/applications/flare-download.desktop" << EOF
[Desktop Entry]
Name=Flare Download
Comment=Multi-Platform Video Downloader
Exec=$INSTALL_DIR/flare-download
Icon=video-x-generic
Terminal=false
Type=Application
Categories=Network;AudioVideo;
Keywords=youtube;tiktok;instagram;video;download;flare;
EOF
    echo -e "      ${GREEN}Desktop entry created${NC}"
fi

# Create desktop shortcut
if [ -d "$HOME/Desktop" ]; then
    cp "$HOME/.local/share/applications/flare-download.desktop" "$HOME/Desktop/" 2>/dev/null || true
    chmod +x "$HOME/Desktop/flare-download.desktop" 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}${BOLD}Installation Complete!${NC}"
echo ""
echo -e "To run Flare Download:"
echo -e "  ${ORANGE}flare-download${NC}                    (if ~/.local/bin is in PATH)"
echo -e "  ${ORANGE}$INSTALL_DIR/flare-download${NC}"
echo ""
echo -e "Or find ${BOLD}Flare Download${NC} in your applications menu."
echo ""
echo -e "${RED}Part of the Flare ecosystem${NC}"
echo ""
