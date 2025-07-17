#!/bin/bash

# Ship's Bell macOS Service Installer

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="com.ike.ships-bell.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
SERVICE_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo "Installing Ship's Bell macOS Service..."

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Copy plist file to LaunchAgents directory
echo "Copying plist file to $SERVICE_PLIST"
cp "$SCRIPT_DIR/$PLIST_FILE" "$SERVICE_PLIST"

# Load the service
echo "Loading service with launchctl..."
launchctl load "$SERVICE_PLIST"

# Check if service is loaded
if launchctl list | grep -q "com.ike.ships-bell"; then
    echo "✅ Ship's Bell service installed and loaded successfully!"
    echo ""
    echo "Service will:"
    echo "  - Start automatically when you log in"
    echo "  - Ring bells every 30 minutes from 9 AM to 8 PM"
    echo "  - Run in the background"
    echo ""
    echo "Logs will be written to:"
    echo "  - Output: $SCRIPT_DIR/ships-bell.log"
    echo "  - Errors: $SCRIPT_DIR/ships-bell.error.log"
    echo ""
    echo "To uninstall, run: ./uninstall-macos-service.sh"
else
    echo "❌ Failed to load service. Check the logs for errors."
    exit 1
fi