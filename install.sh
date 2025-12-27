#!/bin/bash

# NeonTube Multi-Platform Video Downloader - Installation Script
# https://github.com/contactmukundthiru-cyber/Multi-Platform-Downloader

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'
BOLD='\033[1m'

# Banner
echo -e "${CYAN}"
echo "  _   _                  _____      _          "
echo " | \ | |                |_   _|    | |         "
echo " |  \| | ___  ___  _ __   | |_   _| |__   ___ "
echo " | . \` |/ _ \/ _ \| '_ \  | | | | | '_ \ / _ \\"
echo " | |\  |  __/ (_) | | | | | | |_| | |_) |  __/"
echo " |_| \_|\___|\___/|_| |_| \_/\__,_|_.__/ \___|"
echo -e "${NC}"
echo -e "${BOLD}Multi-Platform Video Downloader${NC}"
echo -e "${PURPLE}YouTube | TikTok | Instagram | Twitter | 1000+ sites${NC}"
echo ""

# Determine install directory
if [ -n "$1" ]; then
    INSTALL_DIR="$1"
else
    INSTALL_DIR="$HOME/.local/share/neontube"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"

echo -e "${YELLOW}[1/5]${NC} Checking Python installation..."
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
echo -e "${YELLOW}[2/5]${NC} Creating installation directory..."
mkdir -p "$INSTALL_DIR"
echo -e "      ${GREEN}Directory: $INSTALL_DIR${NC}"

# Copy or download files
echo ""
echo -e "${YELLOW}[3/5]${NC} Installing application files..."

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
echo -e "${YELLOW}[4/5]${NC} Setting up Python environment..."
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
echo -e "${YELLOW}[5/5]${NC} Creating launcher..."

cat > "$INSTALL_DIR/neontube" << 'LAUNCHER'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
source venv/bin/activate
python3 youtube_downloader.py "$@"
LAUNCHER

chmod +x "$INSTALL_DIR/neontube"

# Create symlink in ~/.local/bin
mkdir -p "$HOME/.local/bin"
ln -sf "$INSTALL_DIR/neontube" "$HOME/.local/bin/neontube"

# Create desktop entry
if [ -d "$HOME/.local/share/applications" ]; then
    cat > "$HOME/.local/share/applications/neontube.desktop" << EOF
[Desktop Entry]
Name=NeonTube
Comment=Multi-Platform Video Downloader
Exec=$INSTALL_DIR/neontube
Icon=video-x-generic
Terminal=false
Type=Application
Categories=Network;AudioVideo;
Keywords=youtube;tiktok;instagram;video;download;
EOF
    echo -e "      ${GREEN}Desktop entry created${NC}"
fi

# Create desktop shortcut
if [ -d "$HOME/Desktop" ]; then
    cp "$HOME/.local/share/applications/neontube.desktop" "$HOME/Desktop/" 2>/dev/null || true
    chmod +x "$HOME/Desktop/neontube.desktop" 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}${BOLD}Installation Complete!${NC}"
echo ""
echo -e "To run NeonTube:"
echo -e "  ${CYAN}neontube${NC}                    (if ~/.local/bin is in PATH)"
echo -e "  ${CYAN}$INSTALL_DIR/neontube${NC}"
echo ""
echo -e "Or find ${BOLD}NeonTube${NC} in your applications menu."
echo ""
echo -e "${PURPLE}Supports: YouTube, TikTok, Instagram, Twitter, and 1000+ more sites!${NC}"
echo ""
