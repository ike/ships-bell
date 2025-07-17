#!/bin/bash

# Ship's Bell macOS Service Uninstaller

set -e

PLIST_FILE="com.ike.ships-bell.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
SERVICE_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo "Uninstalling Ship's Bell macOS Service..."

# Check if service is loaded and unload it
if launchctl list | grep -q "com.ike.ships-bell"; then
    echo "Unloading service..."
    launchctl unload "$SERVICE_PLIST"
else
    echo "Service is not currently loaded."
fi

# Remove plist file
if [ -f "$SERVICE_PLIST" ]; then
    echo "Removing plist file..."
    rm "$SERVICE_PLIST"
    echo "✅ Ship's Bell service uninstalled successfully!"
else
    echo "Plist file not found at $SERVICE_PLIST"
fi

# Check if service is still listed
if launchctl list | grep -q "com.ike.ships-bell"; then
    echo "⚠️  Service may still be running. Try logging out and back in."
else
    echo "✅ Service completely removed."
fi