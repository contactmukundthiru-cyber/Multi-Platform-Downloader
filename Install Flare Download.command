#!/bin/bash

# ============================================================================
# FLARE DOWNLOAD - One-Click macOS Installer
# Just double-click this file to install!
# ============================================================================

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'
BOLD='\033[1m'

# Install directory
INSTALL_DIR="$HOME/Applications/FlareDownload"

clear
echo ""
echo -e "${RED}${BOLD}"
echo "  ███████╗██╗      █████╗ ██████╗ ███████╗"
echo "  ██╔════╝██║     ██╔══██╗██╔══██╗██╔════╝"
echo "  █████╗  ██║     ███████║██████╔╝█████╗  "
echo "  ██╔══╝  ██║     ██╔══██║██╔══██╗██╔══╝  "
echo "  ██║     ███████╗██║  ██║██║  ██║███████╗"
echo "  ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝"
echo -e "${NC}"
echo -e "  ${YELLOW}${BOLD}DOWNLOAD${NC} - Multi-Platform Video Downloader"
echo ""
echo "  ══════════════════════════════════════════════════════"
echo ""
echo -e "  ${CYAN}This installer will set up everything automatically.${NC}"
echo -e "  ${CYAN}No technical knowledge required!${NC}"
echo ""
echo "  ══════════════════════════════════════════════════════"
echo ""
echo -e "  Press ${WHITE}ENTER${NC} to start installation..."
read

# ============================================================================
# Check for Homebrew and Python
# ============================================================================
echo ""
echo -e "  ${YELLOW}[1/4]${NC} ${BOLD}Checking Python...${NC}"
echo ""

# Check if Python 3 exists
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION found"
else
    echo -e "  ${BLUE}→${NC} Python not found, checking for Homebrew..."

    if ! command -v brew &> /dev/null; then
        echo -e "  ${BLUE}→${NC} Installing Homebrew (this may take a few minutes)..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        # Add Homebrew to PATH
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    fi

    echo -e "  ${BLUE}→${NC} Installing Python..."
    brew install python@3.11
fi

# Check for tkinter
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo -e "  ${YELLOW}!${NC} Installing tkinter..."
    brew install python-tk@3.11 2>/dev/null || brew install python-tk 2>/dev/null || brew install tcl-tk
fi

echo ""

# ============================================================================
# Install FFmpeg
# ============================================================================
echo -e "  ${YELLOW}[2/4]${NC} ${BOLD}Checking FFmpeg...${NC}"
echo ""

if command -v ffmpeg &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} FFmpeg found"
else
    echo -e "  ${BLUE}→${NC} Installing FFmpeg..."
    brew install ffmpeg 2>/dev/null || echo -e "  ${YELLOW}!${NC} FFmpeg not installed (optional)"
fi

echo ""

# ============================================================================
# Install Python packages
# ============================================================================
echo -e "  ${YELLOW}[3/4]${NC} ${BOLD}Installing components...${NC}"
echo ""

echo -e "  ${BLUE}→${NC} Installing customtkinter..."
pip3 install customtkinter --quiet 2>/dev/null || pip3 install customtkinter --user --quiet

echo -e "  ${BLUE}→${NC} Installing yt-dlp..."
pip3 install yt-dlp --quiet 2>/dev/null || pip3 install yt-dlp --user --quiet

echo -e "  ${GREEN}✓${NC} All components installed"
echo ""

# ============================================================================
# Download and setup app
# ============================================================================
echo -e "  ${YELLOW}[4/4]${NC} ${BOLD}Setting up Flare Download...${NC}"
echo ""

mkdir -p "$INSTALL_DIR"

GITHUB_RAW="https://raw.githubusercontent.com/contactmukundthiru-cyber/Multi-Platform-Downloader/main"

echo -e "  ${BLUE}→${NC} Downloading application..."
curl -sSL "$GITHUB_RAW/youtube_downloader.py" -o "$INSTALL_DIR/youtube_downloader.py"
curl -sSL "$GITHUB_RAW/version.py" -o "$INSTALL_DIR/version.py" 2>/dev/null || true

# Create launcher
cat > "$INSTALL_DIR/Flare Download" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 youtube_downloader.py
EOF
chmod +x "$INSTALL_DIR/Flare Download"

# Create .app bundle for Dock/Launchpad
APP_DIR="$HOME/Applications/Flare Download.app"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

cat > "$APP_DIR/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>FlareDownload</string>
    <key>CFBundleIdentifier</key>
    <string>com.flare.download</string>
    <key>CFBundleName</key>
    <string>Flare Download</string>
    <key>CFBundleVersion</key>
    <string>2.6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
EOF

cat > "$APP_DIR/Contents/MacOS/FlareDownload" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 youtube_downloader.py
EOF
chmod +x "$APP_DIR/Contents/MacOS/FlareDownload"

echo -e "  ${GREEN}✓${NC} Application installed"
echo ""

# ============================================================================
# Done!
# ============================================================================
clear
echo ""
echo -e "${GREEN}${BOLD}"
echo "  ███████╗██╗      █████╗ ██████╗ ███████╗"
echo "  ██╔════╝██║     ██╔══██╗██╔══██╗██╔════╝"
echo "  █████╗  ██║     ███████║██████╔╝█████╗  "
echo "  ██╔══╝  ██║     ██╔══██║██╔══██╗██╔══╝  "
echo "  ██║     ███████╗██║  ██║██║  ██║███████╗"
echo "  ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝"
echo -e "${NC}"
echo ""
echo -e "  ${GREEN}══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}${BOLD}✓ INSTALLATION COMPLETE!${NC}"
echo ""
echo -e "  ${GREEN}══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${WHITE}${BOLD}How to use Flare Download:${NC}"
echo ""
echo -e "  ${CYAN}1.${NC} Open ${YELLOW}Flare Download${NC} from Launchpad or ~/Applications"
echo ""
echo -e "  ${CYAN}2.${NC} Paste a video URL (YouTube, TikTok, etc.)"
echo ""
echo -e "  ${CYAN}3.${NC} Click ${YELLOW}DOWNLOAD${NC}"
echo ""
echo -e "  ${GREEN}══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Launch Flare Download now? (y/n)"
read -n 1 LAUNCH
echo ""

if [[ "$LAUNCH" == "y" || "$LAUNCH" == "Y" ]]; then
    open "$APP_DIR"
fi

echo ""
echo -e "  ${RED}Part of the Flare ecosystem${NC}"
echo ""
