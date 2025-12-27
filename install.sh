#!/bin/bash

# ============================================================================
# FLARE DOWNLOAD - Robust Installation Script
# Part of the Flare ecosystem
# ============================================================================
# This installer is designed to work for complete beginners.
# It handles all dependencies automatically with clear error messages.
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
ORANGE='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'

# Banner
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
echo -e "${ORANGE}${BOLD}  DOWNLOAD${NC} ${DIM}v2.6.0${NC}"
echo ""
echo -e "  ${CYAN}Premium Multi-Platform Video Downloader${NC}"
echo -e "  ${DIM}YouTube • TikTok • Instagram • Twitter • 1000+ sites${NC}"
echo ""
echo -e "${DIM}══════════════════════════════════════════════════════${NC}"
echo ""

# Determine install directory
if [ -n "$1" ]; then
    INSTALL_DIR="$1"
else
    INSTALL_DIR="$HOME/.local/share/flare-download"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

check_command() {
    command -v "$1" &> /dev/null
}

print_step() {
    echo -e "${ORANGE}[$1/7]${NC} ${BOLD}$2${NC}"
}

print_ok() {
    echo -e "  ${GREEN}✓${NC} $1"
}

print_fail() {
    echo -e "  ${RED}✗${NC} $1"
}

print_warn() {
    echo -e "  ${YELLOW}!${NC} $1"
}

print_info() {
    echo -e "  ${BLUE}→${NC} $1"
}

print_error_box() {
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║${NC} ${BOLD}ERROR: $1${NC}"
    echo -e "${RED}╠════════════════════════════════════════════════════════╣${NC}"
    shift
    for line in "$@"; do
        echo -e "${RED}║${NC} $line"
    done
    echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# ============================================================================
# STEP 1: Check Python
# ============================================================================
echo ""
print_step "1" "Checking Python installation..."

PYTHON_CMD=""
for cmd in python3 python; do
    if check_command "$cmd"; then
        ver=$($cmd -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
        major=$($cmd -c 'import sys; print(sys.version_info.major)' 2>/dev/null)
        minor=$($cmd -c 'import sys; print(sys.version_info.minor)' 2>/dev/null)

        if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
            PYTHON_CMD="$cmd"
            print_ok "Python $ver found ($cmd)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    print_error_box "Python 3.8+ is required" \
        "" \
        "Install Python 3.8 or higher:" \
        "  Ubuntu/Debian:  sudo apt install python3 python3-pip python3-venv" \
        "  Fedora:         sudo dnf install python3 python3-pip" \
        "  macOS:          brew install python@3.11" \
        "  Arch:           sudo pacman -S python python-pip"
    exit 1
fi

# ============================================================================
# STEP 2: Check pip
# ============================================================================
echo ""
print_step "2" "Checking pip..."

if $PYTHON_CMD -m pip --version &> /dev/null; then
    PIP_VER=$($PYTHON_CMD -m pip --version | awk '{print $2}')
    print_ok "pip $PIP_VER found"
else
    print_warn "pip not found, attempting to install..."

    if check_command apt; then
        sudo apt update && sudo apt install -y python3-pip
    elif check_command dnf; then
        sudo dnf install -y python3-pip
    elif check_command pacman; then
        sudo pacman -S --noconfirm python-pip
    elif check_command brew; then
        # pip comes with brew python
        :
    else
        print_error_box "Could not install pip" \
            "" \
            "Please install pip manually:" \
            "  Ubuntu/Debian:  sudo apt install python3-pip" \
            "  Fedora:         sudo dnf install python3-pip" \
            "  macOS:          brew install python"
        exit 1
    fi

    if $PYTHON_CMD -m pip --version &> /dev/null; then
        print_ok "pip installed successfully"
    else
        print_error_box "pip installation failed" \
            "Please install pip manually and try again"
        exit 1
    fi
fi

# ============================================================================
# STEP 3: Check tkinter (system dependency)
# ============================================================================
echo ""
print_step "3" "Checking tkinter (GUI library)..."

if $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
    print_ok "tkinter found"
else
    print_warn "tkinter not found, attempting to install..."

    if [ -f /etc/debian_version ]; then
        print_info "Detected Debian/Ubuntu..."
        sudo apt update && sudo apt install -y python3-tk
    elif [ -f /etc/redhat-release ]; then
        print_info "Detected RHEL/Fedora..."
        sudo dnf install -y python3-tkinter 2>/dev/null || sudo yum install -y python3-tkinter
    elif [ -f /etc/arch-release ]; then
        print_info "Detected Arch Linux..."
        sudo pacman -S --noconfirm tk
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_info "Detected macOS..."
        brew install python-tk@3.12 2>/dev/null || brew install python-tk 2>/dev/null || brew install tcl-tk
    else
        print_error_box "Could not install tkinter" \
            "" \
            "Please install tkinter manually:" \
            "  Ubuntu/Debian:  sudo apt install python3-tk" \
            "  Fedora:         sudo dnf install python3-tkinter" \
            "  Arch:           sudo pacman -S tk" \
            "  macOS:          brew install python-tk"
        exit 1
    fi

    if $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
        print_ok "tkinter installed successfully"
    else
        print_error_box "tkinter installation failed" \
            "" \
            "Please install tkinter manually and try again"
        exit 1
    fi
fi

# ============================================================================
# STEP 4: Check FFmpeg (optional)
# ============================================================================
echo ""
print_step "4" "Checking FFmpeg (optional)..."

if check_command ffmpeg; then
    FFMPEG_VER=$(ffmpeg -version 2>&1 | head -n1 | awk '{print $3}')
    print_ok "FFmpeg $FFMPEG_VER found"
else
    print_warn "FFmpeg not found (optional, for video merging)"
    print_info "To install: sudo apt install ffmpeg (Linux) or brew install ffmpeg (macOS)"
fi

# ============================================================================
# STEP 5: Create installation directory
# ============================================================================
echo ""
print_step "5" "Setting up installation directory..."

mkdir -p "$INSTALL_DIR"
print_ok "Created: $INSTALL_DIR"

# Copy or download files
if [ -f "$SCRIPT_DIR/youtube_downloader.py" ]; then
    cp "$SCRIPT_DIR/youtube_downloader.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/updater.py" "$INSTALL_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR/version.py" "$INSTALL_DIR/" 2>/dev/null || true
    cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true
    print_ok "Application files copied"
else
    print_info "Downloading from GitHub..."
    GITHUB_RAW="https://raw.githubusercontent.com/contactmukundthiru-cyber/Multi-Platform-Downloader/main"

    if check_command curl; then
        curl -sSL "$GITHUB_RAW/youtube_downloader.py" -o "$INSTALL_DIR/youtube_downloader.py" || exit 1
        curl -sSL "$GITHUB_RAW/updater.py" -o "$INSTALL_DIR/updater.py" 2>/dev/null || true
        curl -sSL "$GITHUB_RAW/version.py" -o "$INSTALL_DIR/version.py" 2>/dev/null || true
        curl -sSL "$GITHUB_RAW/requirements.txt" -o "$INSTALL_DIR/requirements.txt" || exit 1
    elif check_command wget; then
        wget -q "$GITHUB_RAW/youtube_downloader.py" -O "$INSTALL_DIR/youtube_downloader.py" || exit 1
        wget -q "$GITHUB_RAW/updater.py" -O "$INSTALL_DIR/updater.py" 2>/dev/null || true
        wget -q "$GITHUB_RAW/version.py" -O "$INSTALL_DIR/version.py" 2>/dev/null || true
        wget -q "$GITHUB_RAW/requirements.txt" -O "$INSTALL_DIR/requirements.txt" || exit 1
    else
        print_error_box "Neither curl nor wget found" \
            "Please install curl or wget and try again"
        exit 1
    fi
    print_ok "Files downloaded from GitHub"
fi

# ============================================================================
# STEP 6: Create virtual environment and install dependencies
# ============================================================================
echo ""
print_step "6" "Setting up Python environment..."

# Check for venv module
if ! $PYTHON_CMD -m venv --help &> /dev/null; then
    print_warn "venv module not found, installing..."
    if [ -f /etc/debian_version ]; then
        sudo apt install -y python3-venv
    elif [ -f /etc/redhat-release ]; then
        sudo dnf install -y python3-venv 2>/dev/null || true
    fi
fi

# Remove old venv if exists
if [ -d "$INSTALL_DIR/venv" ]; then
    print_info "Removing old virtual environment..."
    rm -rf "$INSTALL_DIR/venv"
fi

# Create new venv
print_info "Creating virtual environment..."
$PYTHON_CMD -m venv "$INSTALL_DIR/venv"

# Activate and install
print_info "Installing dependencies..."
source "$INSTALL_DIR/venv/bin/activate"

pip install --upgrade pip -q 2>/dev/null

# Install from requirements or individually
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    pip install -r "$INSTALL_DIR/requirements.txt" -q 2>/dev/null || {
        print_warn "Some packages failed, installing individually..."
        pip install customtkinter -q
    }
fi

# Always ensure these are installed
pip install customtkinter yt-dlp -q 2>/dev/null

print_ok "All dependencies installed"

# ============================================================================
# STEP 7: Create launcher and shortcuts
# ============================================================================
echo ""
print_step "7" "Creating launcher and shortcuts..."

# Create launcher script
cat > "$INSTALL_DIR/flare-download" << 'LAUNCHER'
#!/bin/bash
# Flare Download Launcher
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
source venv/bin/activate
python3 youtube_downloader.py "$@"
LAUNCHER

chmod +x "$INSTALL_DIR/flare-download"
print_ok "Launcher created"

# Create symlink in ~/.local/bin
mkdir -p "$HOME/.local/bin"
ln -sf "$INSTALL_DIR/flare-download" "$HOME/.local/bin/flare-download"
print_ok "Command 'flare-download' added to ~/.local/bin"

# Create desktop entry (Linux)
if [ -d "$HOME/.local/share/applications" ]; then
    cat > "$HOME/.local/share/applications/flare-download.desktop" << EOF
[Desktop Entry]
Name=Flare Download
Comment=Premium Multi-Platform Video Downloader
Exec=$INSTALL_DIR/flare-download
Icon=video-x-generic
Terminal=false
Type=Application
Categories=Network;AudioVideo;
Keywords=youtube;tiktok;instagram;video;download;flare;
EOF
    print_ok "Desktop entry created"
fi

# Create desktop shortcut
if [ -d "$HOME/Desktop" ]; then
    cp "$HOME/.local/share/applications/flare-download.desktop" "$HOME/Desktop/" 2>/dev/null || true
    chmod +x "$HOME/Desktop/flare-download.desktop" 2>/dev/null || true
    print_ok "Desktop shortcut created"
fi

# ============================================================================
# DONE
# ============================================================================
echo ""
echo -e "${DIM}══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}${BOLD}  ✓ Installation Complete!${NC}"
echo ""
echo -e "  ${BOLD}To run Flare Download:${NC}"
echo ""

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
    echo -e "    ${ORANGE}flare-download${NC}"
else
    echo -e "    ${ORANGE}$INSTALL_DIR/flare-download${NC}"
    echo ""
    echo -e "  ${YELLOW}Tip:${NC} Add ~/.local/bin to your PATH:"
    echo -e "    ${DIM}echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc${NC}"
    echo -e "    ${DIM}source ~/.bashrc${NC}"
fi

echo ""
echo -e "  Or find ${BOLD}Flare Download${NC} in your applications menu."
echo ""
echo -e "${DIM}══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${RED}Part of the Flare ecosystem${NC}"
echo ""
