# Ship's Bell

Count down the half-hours left on your watch with this service that rings the 
well-known [ship's bell](https://en.wikipedia.org/wiki/Ship%27s_bell) maritime 
watch system. Works on MacOS and runs in the background.

## Quick Install (Recommended)

Install Ship's Bell with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/ike/ships-bell/master/install.sh | bash
```

This will:
- Download and install Ship's Bell to `~/.local/share/ships-bell/`
- Set up background services to run automatically
- Configure bells to ring from 9 AM to 8 PM by default

## Bell Schedule

- **Every 30 minutes**: Regular ship's bell chimes that follow the traditional maritime watch system
  - **8 Bells**: 12, 4, 8
  - **1 Bell**: 12:30, 4:30, 8:30
  - **2 Bells**: 1, 5, 9
  - **3 Bells**: 1:30, 5:30, 9:30
  - **4 Bells**: 2, 6, 10
  - **5 Bells**: 2:30, 6:30, 10:30
  - **6 Bells**: 3, 7, 11
  - **7 Bells**: 3:30, 7:30, 11:30
- **Configurable hours**: Default 9 AM to 8 PM, customizable during installation

### Custom Schedule

```bash
# Ring from 8 AM to 10 PM:
START_HOUR=8 END_HOUR=22 curl -fsSL https://raw.githubusercontent.com/ike/ships-bell/master/install.sh | bash
```

## Requirements

- macOS (uses native `afplay` for audio)
- Python 3.3 or later
- curl or wget (for installation)

## Manual Installation

If you prefer to install manually:

```bash
# Clone the repository:
git clone https://github.com/ike/ships-bell.git
cd ships-bell

# Install as background service:
./install-macos-service.sh

# Or run directly:
python3 ./ships_bell.py --help
```

## Basic Usage

```bash
# Show help:
python3 ./ships_bell.py --help

# Bell sounds from 9 AM to 8 PM (default):
python3 ./ships_bell.py

# Custom schedule:
python3 ./ships_bell.py --from 8 --to 22
```

## Background Service

The installation creates two macOS LaunchAgent services:

- **Timer Service** (`{user}.ships-bell`) - Background scheduling
- **Audio Watcher** (`{user}.ships-bell-watcher`) - User session audio playback

This architecture ensures high-quality audio playback by separating timing logic from audio execution.

### Service Management

```bash
# Check service status:
launchctl list | grep ships-bell

# View logs:
tail -f ~/.local/share/ships-bell/logs/ships-bell.log

# Uninstall:
cd ~/.local/share/ships-bell && ./uninstall-macos-service.sh
```

## Architecture

Ship's Bell uses a file-based trigger system to solve macOS LaunchAgent audio quality issues:

1. Background timer service writes trigger files
2. Interactive watcher service monitors files and plays audio
3. Complete separation ensures crystal-clear audio quality

See `LAUNCHAGENT-AUDIO-ISSUE.md` for technical details about this solution.

## Files and Directories

```
~/.local/share/ships-bell/          # Installation directory
├── ships_bell.py                   # Main application
├── ships-bell-watcher              # Audio watcher service
├── audio/                          # Audio files
│   ├── DoubleStrike.mp3
│   ├── SingleStrike.mp3
│   └── sir-thats-noon.mp3
├── logs/                           # Service logs
└── triggers/                       # Runtime trigger files
```

## Troubleshooting

**No audio playing:**
- Check that services are running: `launchctl list | grep ships-bell`
- View logs: `tail ~/.local/share/ships-bell/logs/*.log`
- Verify audio files exist in `~/.local/share/ships-bell/audio/`

**Audio quality issues:**
- The file-based trigger system should prevent this
- See `LAUNCHAGENT-AUDIO-ISSUE.md` for background

**Permission issues:**
- Ensure Python 3 is installed: `python3 --version`
- Check LaunchAgent permissions in System Preferences

## Development

```bash
# Run tests:
make test

# Run linting:
make pylint

# Debug audio issues:
cd audio-debug-tests && ./audio-diagnostics.sh
```

## License

See file LICENSE.

---

*I ate your rat, sir. I am very sorry, and I ask your pardon.*
