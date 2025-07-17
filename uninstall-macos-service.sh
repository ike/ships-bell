#!/bin/bash

# Ship's Bell macOS Service Uninstaller - Universal Version

set -e

# Configuration
CURRENT_USER=$(whoami)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/share/ships-bell}"

# Derived paths
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
SERVICE_PLIST="$LAUNCH_AGENTS_DIR/${CURRENT_USER}.ships-bell.plist"
WATCHER_PLIST="$LAUNCH_AGENTS_DIR/${CURRENT_USER}.ships-bell-watcher.plist"

echo "🗑️  Uninstalling Ship's Bell macOS Services..."
echo "User: $CURRENT_USER"
echo "Installation directory: $INSTALL_DIR"
echo ""

# Check if bell service is loaded and unload it
if launchctl list | grep -q "${CURRENT_USER}.ships-bell"; then
    echo "Unloading bell service..."
    launchctl unload "$SERVICE_PLIST" 2>/dev/null || echo "Failed to unload bell service"
else
    echo "Bell service is not currently loaded."
fi

# Check if watcher service is loaded and unload it
if launchctl list | grep -q "${CURRENT_USER}.ships-bell-watcher"; then
    echo "Unloading watcher service..."
    launchctl unload "$WATCHER_PLIST" 2>/dev/null || echo "Failed to unload watcher service"
else
    echo "Watcher service is not currently loaded."
fi

# Remove plist files
if [ -f "$SERVICE_PLIST" ]; then
    echo "Removing bell service plist..."
    rm "$SERVICE_PLIST"
fi

if [ -f "$WATCHER_PLIST" ]; then
    echo "Removing watcher service plist..."
    rm "$WATCHER_PLIST"
fi

# Remove legacy user scripts (from old installation method)
if [ -f "$HOME/.local/bin/ships-bell-play" ]; then
    echo "Removing legacy user audio script..."
    rm "$HOME/.local/bin/ships-bell-play"
fi

if [ -f "$HOME/.local/bin/ships-bell-watcher" ]; then
    echo "Removing legacy watcher script..."
    rm "$HOME/.local/bin/ships-bell-watcher"
fi

# Ask user if they want to remove the installation directory
echo ""
read -p "Remove installation directory ($INSTALL_DIR)? [y/N]: " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "$INSTALL_DIR" ]; then
        echo "Removing installation directory..."
        rm -rf "$INSTALL_DIR"
        echo "✅ Installation directory removed."
    else
        echo "Installation directory not found."
    fi
else
    echo "Installation directory preserved at: $INSTALL_DIR"
    echo "You can manually remove it later if desired."
fi

# Check if services are still listed
BELL_STILL_RUNNING=$(launchctl list | grep -q "${CURRENT_USER}.ships-bell" && echo "yes" || echo "no")
WATCHER_STILL_RUNNING=$(launchctl list | grep -q "${CURRENT_USER}.ships-bell-watcher" && echo "yes" || echo "no")

echo ""
if [[ "$BELL_STILL_RUNNING" == "yes" || "$WATCHER_STILL_RUNNING" == "yes" ]]; then
    echo "⚠️  Some services may still be running. Try logging out and back in."
    echo "Bell service running: $BELL_STILL_RUNNING"
    echo "Watcher service running: $WATCHER_STILL_RUNNING"
else
    echo "✅ Ship's Bell services completely removed."
fi

echo ""
echo "🔔 Ship's Bell uninstallation complete."
echo ""
echo "To reinstall, you can run:"
echo "  curl -fsSL https://raw.githubusercontent.com/user/ships-bell/master/install.sh | bash"
