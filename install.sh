#!/bin/bash

# Flare Download - Multi-Platform Video Downloader
# Robust Installation Script
# Part of the Flare ecosystem

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
ORANGE='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

# Banner
echo ""
echo -e "${RED}${BOLD}"
echo "  ███████╗██╗      █████╗ ██████╗ ███████╗"
echo "  ██╔════╝██║     ██╔══██╗██╔══██╗██╔════╝"
echo "  █████╗  ██║     ███████║██████╔╝█████╗  "
echo "  ██╔══╝  ██║     ██╔══██║██╔══██╗██╔══╝  "
echo "  ██║     ███████╗██║  ██║██║  ██║███████╗"
echo "  ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝"
echo -e "${NC}"
echo -e "${ORANGE}${BOLD}DOWNLOAD${NC} - Multi-Platform Video Downloader"
echo -e "${YELLOW}YouTube | TikTok | Instagram | Twitter | 1000+ sites${NC}"
echo ""
echo "=================================================="
echo ""

# Determine install directory
if [ -n "$1" ]; then
    INSTALL_DIR="$1"
else
    INSTALL_DIR="$HOME/.local/share/flare-download"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"

# Function to check command existence
check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[*]${NC} $1"
}

# Step 1: Check Python
echo -e "${ORANGE}[1/6]${NC} Checking Python installation..."

if check_command python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_status "Python $PYTHON_VERSION found"

    # Check version
    PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8 or higher is required (found $PYTHON_VERSION)"
        echo ""
        echo "Please upgrade Python:"
        echo "  Ubuntu/Debian: sudo apt install python3.10"
        echo "  macOS: brew install python@3.10"
        exit 1
    fi
else
    print_error "Python 3 is not installed!"
    echo ""
    echo "Please install Python 3.8+:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS: brew install python3"
    exit 1
fi

# Step 2: Check pip
echo ""
echo -e "${ORANGE}[2/6]${NC} Checking pip..."

if python3 -m pip --version &> /dev/null; then
    PIP_VERSION=$(python3 -m pip --version | awk '{print $2}')
    print_status "pip $PIP_VERSION found"
else
    print_warning "pip not found, attempting to install..."
    if check_command apt; then
        sudo apt install -y python3-pip
    elif check_command brew; then
        brew install pip3
    else
        print_error "Could not install pip. Please install manually."
        exit 1
    fi
fi

# Step 3: Check/Install tkinter (system dependency)
echo ""
echo -e "${ORANGE}[3/6]${NC} Checking system dependencies..."

# Check if tkinter is available
if python3 -c "import tkinter" 2>/dev/null; then
    print_status "tkinter found"
else
    print_warning "tkinter not found, attempting to install..."

    # Detect OS and install
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        print_info "Detected Debian/Ubuntu, installing python3-tk..."
        sudo apt update && sudo apt install -y python3-tk
    elif [ -f /etc/redhat-release ]; then
        # RHEL/CentOS/Fedora
        print_info "Detected RHEL/Fedora, installing python3-tkinter..."
        sudo dnf install -y python3-tkinter 2>/dev/null || sudo yum install -y python3-tkinter
    elif [ -f /etc/arch-release ]; then
        # Arch Linux
        print_info "Detected Arch Linux, installing tk..."
        sudo pacman -S --noconfirm tk
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_info "Detected macOS, installing python-tk..."
        brew install python-tk@3.12 || brew install python-tk
    else
        print_error "Could not auto-install tkinter. Please install manually:"
        echo "  Ubuntu/Debian: sudo apt install python3-tk"
        echo "  Fedora: sudo dnf install python3-tkinter"
        echo "  Arch: sudo pacman -S tk"
        echo "  macOS: brew install python-tk"
        exit 1
    fi

    # Verify installation
    if python3 -c "import tkinter" 2>/dev/null; then
        print_status "tkinter installed successfully"
    else
        print_error "tkinter installation failed. Please install manually."
        exit 1
    fi
fi

# Check FFmpeg (optional but recommended)
if check_command ffmpeg; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1 | awk '{print $3}')
    print_status "FFmpeg $FFMPEG_VERSION found (optional, for video merging)"
else
    print_warning "FFmpeg not found (optional, recommended for video merging)"
    print_info "To install: sudo apt install ffmpeg (Linux) or brew install ffmpeg (macOS)"
fi

# Step 4: Create installation directory
echo ""
echo -e "${ORANGE}[4/6]${NC} Setting up installation directory..."

mkdir -p "$INSTALL_DIR"
print_status "Created: $INSTALL_DIR"

# Copy or download files
if [ -f "$SCRIPT_DIR/youtube_downloader.py" ]; then
    cp "$SCRIPT_DIR/youtube_downloader.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/updater.py" "$INSTALL_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR/version.py" "$INSTALL_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true
    print_status "Application files copied"
else
    print_info "Downloading from GitHub..."
    GITHUB_RAW="https://raw.githubusercontent.com/contactmukundthiru-cyber/Multi-Platform-Downloader/main"

    if check_command curl; then
        curl -sSL "$GITHUB_RAW/youtube_downloader.py" -o "$INSTALL_DIR/youtube_downloader.py"
        curl -sSL "$GITHUB_RAW/updater.py" -o "$INSTALL_DIR/updater.py"
        curl -sSL "$GITHUB_RAW/version.py" -o "$INSTALL_DIR/version.py"
        curl -sSL "$GITHUB_RAW/requirements.txt" -o "$INSTALL_DIR/requirements.txt"
    elif check_command wget; then
        wget -q "$GITHUB_RAW/youtube_downloader.py" -O "$INSTALL_DIR/youtube_downloader.py"
        wget -q "$GITHUB_RAW/updater.py" -O "$INSTALL_DIR/updater.py"
        wget -q "$GITHUB_RAW/version.py" -O "$INSTALL_DIR/version.py"
        wget -q "$GITHUB_RAW/requirements.txt" -O "$INSTALL_DIR/requirements.txt"
    else
        print_error "Neither curl nor wget found. Please install one."
        exit 1
    fi
    print_status "Files downloaded"
fi

# Step 5: Create virtual environment and install dependencies
echo ""
echo -e "${ORANGE}[5/6]${NC} Setting up Python environment..."

# Check for venv module
if ! python3 -m venv --help &> /dev/null; then
    print_warning "venv module not found, installing..."
    if [ -f /etc/debian_version ]; then
        sudo apt install -y python3-venv
    fi
fi

# Remove old venv if exists
if [ -d "$INSTALL_DIR/venv" ]; then
    print_info "Removing old virtual environment..."
    rm -rf "$INSTALL_DIR/venv"
fi

# Create new venv
python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"

print_info "Upgrading pip..."
pip install --upgrade pip -q

print_info "Installing dependencies..."
pip install -r "$INSTALL_DIR/requirements.txt" -q

print_info "Installing yt-dlp..."
pip install yt-dlp -q

print_status "All dependencies installed"

# Step 6: Create launcher and shortcuts
echo ""
echo -e "${ORANGE}[6/6]${NC} Creating launcher..."

# Create launcher script
cat > "$INSTALL_DIR/flare-download" << 'LAUNCHER'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
source venv/bin/activate
python3 youtube_downloader.py "$@"
LAUNCHER

chmod +x "$INSTALL_DIR/flare-download"
print_status "Launcher created"

# Create symlink in ~/.local/bin
mkdir -p "$HOME/.local/bin"
ln -sf "$INSTALL_DIR/flare-download" "$HOME/.local/bin/flare-download"
print_status "Symlink created in ~/.local/bin"

# Create desktop entry
if [ -d "$HOME/.local/share/applications" ]; then
    cat > "$HOME/.local/share/applications/flare-download.desktop" << EOF
[Desktop Entry]
Name=Flare Download
Comment=Multi-Platform Video Downloader - Part of Flare
Exec=$INSTALL_DIR/flare-download
Icon=video-x-generic
Terminal=false
Type=Application
Categories=Network;AudioVideo;
Keywords=youtube;tiktok;instagram;video;download;flare;
EOF
    print_status "Desktop entry created"
fi

# Create desktop shortcut
if [ -d "$HOME/Desktop" ]; then
    cp "$HOME/.local/share/applications/flare-download.desktop" "$HOME/Desktop/" 2>/dev/null || true
    chmod +x "$HOME/Desktop/flare-download.desktop" 2>/dev/null || true
    print_status "Desktop shortcut created"
fi

# Installation complete
echo ""
echo "=================================================="
echo ""
echo -e "${GREEN}${BOLD}Installation Complete!${NC}"
echo ""
echo -e "To run Flare Download:"
echo -e "  ${ORANGE}flare-download${NC}                      (if ~/.local/bin is in PATH)"
echo -e "  ${ORANGE}$INSTALL_DIR/flare-download${NC}"
echo ""

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "${YELLOW}Note:${NC} Add ~/.local/bin to your PATH for the 'flare-download' command:"
    echo '  echo '\''export PATH="$HOME/.local/bin:$PATH"'\'' >> ~/.bashrc'
    echo ""
fi

echo -e "Or find ${BOLD}Flare Download${NC} in your applications menu."
echo ""
echo -e "${RED}Part of the Flare ecosystem${NC}"
echo ""
