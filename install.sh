#!/bin/bash

# Ship's Bell - One-Command Installer
# Can be run directly from GitHub: curl -fsSL https://raw.githubusercontent.com/ike/ships-bell/master/install.sh | bash

set -e

# Configuration
REPO_URL="https://github.com/ike/ships-bell"
INSTALL_DIR="$HOME/.local/share/ships-bell"
START_HOUR="${START_HOUR:-9}"
END_HOUR="${END_HOUR:-20}"

echo "🔔 Ship's Bell - One-Command Installer"
echo "======================================"
echo ""
echo "This will install Ship's Bell to: $INSTALL_DIR"
echo "Schedule: ${START_HOUR}:00 to ${END_HOUR}:00"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check for download tools
if command -v curl >/dev/null 2>&1; then
    DOWNLOAD_CMD="curl"
elif command -v wget >/dev/null 2>&1; then
    DOWNLOAD_CMD="wget"
else
    echo "❌ Neither curl nor wget found. Please install one of them."
    exit 1
fi

echo "✅ Download tool: $DOWNLOAD_CMD"

# Create installation directory
echo ""
echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Download and extract project
echo "Downloading Ship's Bell from GitHub..."

if [[ "$DOWNLOAD_CMD" == "curl" ]]; then
    if curl -fsSL "${REPO_URL}/archive/master.tar.gz" | tar -xz --strip-components=1 -C "$INSTALL_DIR"; then
        echo "✅ Downloaded and extracted successfully"
    else
        echo "❌ Failed to download from GitHub. Trying git clone..."
        if command -v git >/dev/null 2>&1; then
            rm -rf "$INSTALL_DIR"
            git clone "$REPO_URL.git" "$INSTALL_DIR"
            echo "✅ Cloned repository successfully"
        else
            echo "❌ Git not available. Please install git or curl and try again."
            exit 1
        fi
    fi
else
    # wget fallback
    if wget -qO- "${REPO_URL}/archive/master.tar.gz" | tar -xz --strip-components=1 -C "$INSTALL_DIR"; then
        echo "✅ Downloaded and extracted successfully"
    else
        echo "❌ Failed to download. Please check your internet connection."
        exit 1
    fi
fi

# Run the installation
echo ""
echo "Running installation script..."
cd "$INSTALL_DIR"

# Make scripts executable
chmod +x install-macos-service.sh
chmod +x ships-bell-watcher

# Set environment variables for the installer
export INSTALL_DIR="$INSTALL_DIR"
export START_HOUR="$START_HOUR"
export END_HOUR="$END_HOUR"

# Run the installer
./install-macos-service.sh

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Ship's Bell is now installed and running. You should hear bell chimes"
echo "every 30 minutes between ${START_HOUR}:00 and ${END_HOUR}:00."
echo ""
echo "Installation location: $INSTALL_DIR"
echo ""
echo "To customize the schedule, you can set environment variables:"
echo "  START_HOUR=8 END_HOUR=22 curl -fsSL .../install.sh | bash"
echo ""
echo "To uninstall:"
echo "  cd $INSTALL_DIR && ./uninstall-macos-service.sh"
echo ""
echo "🔔 Enjoy your ship's bell!"
