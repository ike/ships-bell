#!/bin/bash

# Ship's Bell macOS Service Installer - Universal Version

set -e

# Configuration
CURRENT_USER=$(whoami)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/share/ships-bell}"
START_HOUR="${START_HOUR:-9}"
END_HOUR="${END_HOUR:-20}"

# Derived paths
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
SERVICE_PLIST="$LAUNCH_AGENTS_DIR/${CURRENT_USER}.ships-bell.plist"
WATCHER_PLIST="$LAUNCH_AGENTS_DIR/${CURRENT_USER}.ships-bell-watcher.plist"

echo "🔔 Installing Ship's Bell macOS Service..."
echo "User: $CURRENT_USER"
echo "Install directory: $INSTALL_DIR"
echo "Schedule: ${START_HOUR}:00 to ${END_HOUR}:00"
echo ""

# Create installation directory structure
echo "Creating installation directory structure..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/audio"
mkdir -p "$INSTALL_DIR/triggers"

# Copy files to installation directory if not already there
if [[ "$SCRIPT_DIR" != "$INSTALL_DIR" ]]; then
    echo "Copying files to installation directory..."
    cp "$SCRIPT_DIR/ships_bell.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/ships-bell-watcher" "$INSTALL_DIR/"
    cp -r "$SCRIPT_DIR/audio/"* "$INSTALL_DIR/audio/" 2>/dev/null || echo "No audio files to copy"
    chmod +x "$INSTALL_DIR/ships-bell-watcher"
fi

# Create LaunchAgents directory
mkdir -p "$LAUNCH_AGENTS_DIR"

# Generate plist files from templates
echo "Generating service configuration files..."

# Generate main service plist
sed "s|{{USER}}|$CURRENT_USER|g; s|{{INSTALL_DIR}}|$INSTALL_DIR|g; s|{{START_HOUR}}|$START_HOUR|g; s|{{END_HOUR}}|$END_HOUR|g" \
    "$SCRIPT_DIR/com.ike.ships-bell.plist.template" > "$SERVICE_PLIST"

# Generate watcher service plist
sed "s|{{USER}}|$CURRENT_USER|g; s|{{INSTALL_DIR}}|$INSTALL_DIR|g" \
    "$SCRIPT_DIR/com.ike.ships-bell-watcher.plist.template" > "$WATCHER_PLIST"

# Load the services
echo "Loading services with launchctl..."
launchctl load "$SERVICE_PLIST" 2>/dev/null || echo "Service may already be loaded"
launchctl load "$WATCHER_PLIST" 2>/dev/null || echo "Watcher may already be loaded"

# Wait a moment for services to start
sleep 2

# Check if services are loaded
BELL_LOADED=$(launchctl list | grep -q "${CURRENT_USER}.ships-bell" && echo "yes" || echo "no")
WATCHER_LOADED=$(launchctl list | grep -q "${CURRENT_USER}.ships-bell-watcher" && echo "yes" || echo "no")

if [[ "$BELL_LOADED" == "yes" && "$WATCHER_LOADED" == "yes" ]]; then
    echo "✅ Ship's Bell services installed and loaded successfully!"
    echo ""
    echo "Services will:"
    echo "  - Start automatically when you log in"
    echo "  - Ring bells every 30 minutes from ${START_HOUR}:00 to ${END_HOUR}:00"
    echo "  - Run in the background with proper audio quality"
    echo ""
    echo "Installation details:"
    echo "  - Installation directory: $INSTALL_DIR"
    echo "  - Bell timer service: ${CURRENT_USER}.ships-bell (background scheduling)"
    echo "  - Audio watcher service: ${CURRENT_USER}.ships-bell-watcher (user session audio)"
    echo ""
    echo "Logs will be written to:"
    echo "  - Bell service: $INSTALL_DIR/logs/ships-bell.log"
    echo "  - Watcher service: $INSTALL_DIR/logs/ships-bell-watcher.log"
    echo "  - Errors: $INSTALL_DIR/logs/ships-bell*.error.log"
    echo ""
    echo "To uninstall, run: ./uninstall-macos-service.sh"
    echo ""
    echo "🎵 Installation complete! The ship's bell will start chiming automatically."
else
    echo "❌ Failed to load one or more services. Check the logs for errors."
    echo "Bell service loaded: $BELL_LOADED"
    echo "Watcher service loaded: $WATCHER_LOADED"
    echo ""
    echo "Troubleshooting:"
    echo "  - Check logs in: $INSTALL_DIR/logs/"
    echo "  - Verify Python 3 is installed: python3 --version"
    echo "  - Check LaunchAgent permissions"
    exit 1
fi