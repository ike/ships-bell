#!/bin/bash

# Ship's Bell macOS Service Uninstaller

set -e

PLIST_FILE="com.ike.ships-bell.plist"
WATCHER_PLIST_FILE="com.ike.ships-bell-watcher.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
SERVICE_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_FILE"
WATCHER_PLIST="$LAUNCH_AGENTS_DIR/$WATCHER_PLIST_FILE"

echo "Uninstalling Ship's Bell macOS Services..."

# Check if bell service is loaded and unload it
if launchctl list | grep -q "com.ike.ships-bell"; then
    echo "Unloading bell service..."
    launchctl unload "$SERVICE_PLIST"
else
    echo "Bell service is not currently loaded."
fi

# Check if watcher service is loaded and unload it
if launchctl list | grep -q "com.ike.ships-bell-watcher"; then
    echo "Unloading watcher service..."
    launchctl unload "$WATCHER_PLIST"
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

# Remove user scripts
if [ -f "$HOME/.local/bin/ships-bell-play" ]; then
    echo "Removing user audio script..."
    rm "$HOME/.local/bin/ships-bell-play"
fi

if [ -f "$HOME/.local/bin/ships-bell-watcher" ]; then
    echo "Removing watcher script..."
    rm "$HOME/.local/bin/ships-bell-watcher"
fi

# Remove trigger directory
if [ -d "$HOME/.local/share/ships-bell" ]; then
    echo "Removing trigger directory..."
    rm -rf "$HOME/.local/share/ships-bell"
fi

# Check if services are still listed
BELL_STILL_RUNNING=$(launchctl list | grep -q "com.ike.ships-bell" && echo "yes" || echo "no")
WATCHER_STILL_RUNNING=$(launchctl list | grep -q "com.ike.ships-bell-watcher" && echo "yes" || echo "no")

if [[ "$BELL_STILL_RUNNING" == "yes" || "$WATCHER_STILL_RUNNING" == "yes" ]]; then
    echo "⚠️  Some services may still be running. Try logging out and back in."
else
    echo "✅ Ship's Bell services completely removed."
fi