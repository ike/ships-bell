#!/bin/bash

# Ship's Bell macOS Service Installer

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="com.ike.ships-bell.plist"
WATCHER_PLIST_FILE="com.ike.ships-bell-watcher.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
SERVICE_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_FILE"
WATCHER_PLIST="$LAUNCH_AGENTS_DIR/$WATCHER_PLIST_FILE"

echo "Installing Ship's Bell macOS Service..."

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Create ~/.local/bin directory if it doesn't exist
mkdir -p "$HOME/.local/bin"

# Install user-space audio script
echo "Installing user-space audio script..."
cat > "$HOME/.local/bin/ships-bell-play" << 'EOF'
#!/bin/bash

# Ships Bell Audio Player - User Space Script
# This script runs in user session with proper audio access

SHIPS_BELL_DIR="$SCRIPT_DIR"

play_audio() {
    local audio_file="$1"
    if [[ -f "$audio_file" ]]; then
        # Kill any existing afplay processes to prevent overlap
        pkill -f afplay 2>/dev/null || true
        sleep 0.1
        
        # Play audio with proper user session access
        /usr/bin/afplay "$audio_file"
    else
        echo "Error: Audio file not found: $audio_file" >&2
        exit 1
    fi
}

case "$1" in
    "double")
        play_audio "$SHIPS_BELL_DIR/res/DoubleStrike.mp3"
        ;;
    "single")
        play_audio "$SHIPS_BELL_DIR/res/SingleStrike.mp3"
        ;;
    *)
        echo "Usage: $0 {double|single}" >&2
        exit 1
        ;;
esac
EOF

# Replace $SCRIPT_DIR with actual path
sed -i '' "s|\$SCRIPT_DIR|$SCRIPT_DIR|g" "$HOME/.local/bin/ships-bell-play"

# Make script executable
chmod +x "$HOME/.local/bin/ships-bell-play"

# Install watcher script
echo "Installing audio watcher script..."
cat > "$HOME/.local/bin/ships-bell-watcher" << 'EOF'
#!/usr/bin/env python3

"""
Ships Bell Audio Watcher - User Space Process
Watches for trigger files and plays audio in proper user session
"""

import os
import time
import subprocess
import sys

SHIPS_BELL_DIR = "$SCRIPT_DIR"
TRIGGER_DIR = os.path.expanduser("~/.local/share/ships-bell")

def play_audio(audio_file):
    """Play audio file with proper user session access."""
    if os.path.exists(audio_file):
        # Kill any existing afplay processes to prevent overlap
        subprocess.run(["pkill", "-f", "afplay"], capture_output=True)
        time.sleep(0.1)
        
        # Play audio in user session
        subprocess.run(["/usr/bin/afplay", audio_file])
    else:
        print(f"Error: Audio file not found: {audio_file}", file=sys.stderr)

def watch_triggers():
    """Watch for trigger files and play corresponding audio."""
    os.makedirs(TRIGGER_DIR, exist_ok=True)
    
    print("Ships Bell Watcher started - watching for audio triggers...")
    
    while True:
        try:
            # Check for trigger files
            double_trigger = os.path.join(TRIGGER_DIR, "double_strike")
            single_trigger = os.path.join(TRIGGER_DIR, "single_strike")
            noon_trigger = os.path.join(TRIGGER_DIR, "noon_strike")
            
            if os.path.exists(double_trigger):
                os.remove(double_trigger)
                play_audio(f"{SHIPS_BELL_DIR}/res/DoubleStrike.mp3")
                
            if os.path.exists(single_trigger):
                os.remove(single_trigger)
                play_audio(f"{SHIPS_BELL_DIR}/res/SingleStrike.mp3")
                
            if os.path.exists(noon_trigger):
                os.remove(noon_trigger)
                play_audio(f"{SHIPS_BELL_DIR}/res/sir-thats-noon.mp3")
                
            time.sleep(0.1)  # Check every 100ms
            
        except KeyboardInterrupt:
            print("\nShips Bell Watcher stopped")
            break
        except Exception as e:
            print(f"Error in watcher: {e}", file=sys.stderr)
            time.sleep(1)

if __name__ == "__main__":
    watch_triggers()
EOF

# Replace $SCRIPT_DIR with actual path in watcher script
sed -i '' "s|\$SCRIPT_DIR|$SCRIPT_DIR|g" "$HOME/.local/bin/ships-bell-watcher"

# Make watcher script executable
chmod +x "$HOME/.local/bin/ships-bell-watcher"

# Copy plist files to LaunchAgents directory
echo "Copying service plist to $SERVICE_PLIST"
cp "$SCRIPT_DIR/$PLIST_FILE" "$SERVICE_PLIST"

echo "Copying watcher plist to $WATCHER_PLIST"
cp "$SCRIPT_DIR/$WATCHER_PLIST_FILE" "$WATCHER_PLIST"

# Load the services
echo "Loading bell service with launchctl..."
launchctl load "$SERVICE_PLIST"

echo "Loading watcher service with launchctl..."
launchctl load "$WATCHER_PLIST"

# Check if services are loaded
BELL_LOADED=$(launchctl list | grep -q "com.ike.ships-bell" && echo "yes" || echo "no")
WATCHER_LOADED=$(launchctl list | grep -q "com.ike.ships-bell-watcher" && echo "yes" || echo "no")

if [[ "$BELL_LOADED" == "yes" && "$WATCHER_LOADED" == "yes" ]]; then
    echo "✅ Ship's Bell services installed and loaded successfully!"
    echo ""
    echo "Services will:"
    echo "  - Start automatically when you log in"
    echo "  - Ring bells every 30 minutes from 9 AM to 8 PM"
    echo "  - Run in the background with proper audio quality"
    echo ""
    echo "Two services are now running:"
    echo "  - Bell timer service (background scheduling)"
    echo "  - Audio watcher service (user session audio playback)"
    echo ""
    echo "Logs will be written to:"
    echo "  - Bell service: $SCRIPT_DIR/ships-bell.log"
    echo "  - Watcher service: $SCRIPT_DIR/ships-bell-watcher.log"
    echo "  - Errors: $SCRIPT_DIR/ships-bell*.error.log"
    echo ""
    echo "To uninstall, run: ./uninstall-macos-service.sh"
else
    echo "❌ Failed to load one or more services. Check the logs for errors."
    echo "Bell service loaded: $BELL_LOADED"
    echo "Watcher service loaded: $WATCHER_LOADED"
    exit 1
fi