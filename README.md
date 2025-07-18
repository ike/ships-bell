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

Ship's Bell follows the traditional maritime watch system with seven distinct watch periods, including the famous "dogwatches" that break the cycle to ensure crew rotation.

### Traditional Maritime Watch System

| Bells | Pattern | First (20:00-24:00) | Middle (00:00-04:00) | Morning (04:00-08:00) | Forenoon (08:00-12:00) | Afternoon (12:00-16:00) | First Dog (16:00-18:00) | Second Dog (18:00-20:00) |
|-------|---------|---------------------|----------------------|----------------------|------------------------|-------------------------|-------------------------|--------------------------|
| One   | 1       | 20:30               | 00:30                | 04:30                | 08:30                  | 12:30                   | 16:30                   | 18:30                    |
| Two   | 2       | 21:00               | 01:00                | 05:00                | 09:00                  | 13:00                   | 17:00                   | 19:00                    |
| Three | 2,1     | 21:30               | 01:30                | 05:30                | 09:30                  | 13:30                   | 17:30                   | 19:30                    |
| Four  | 2,2     | 22:00               | 02:00                | 06:00                | 10:00                  | 14:00                   | 18:00                   | 20:00                    |
| Five  | 2,2,1   | 22:30               | 02:30                | 06:30                | 10:30                  | 14:30                   | -                       | -                        |
| Six   | 2,2,2   | 23:00               | 03:00                | 07:00                | 11:00                  | 15:00                   | -                       | -                        |
| Seven | 2,2,2,1 | 23:30               | 03:30                | 07:30                | 11:30                  | 15:30                   | -                       | -                        |
| Eight | 2,2,2,2 | 00:00               | 04:00                | 08:00                | 12:00                  | 16:00                   | -                       | -                        |

### Watch Periods Explained

- **First Watch** (20:00-24:00): Evening watch from 8 PM to midnight
- **Middle Watch** (00:00-04:00): Night watch from midnight to 4 AM  
- **Morning Watch** (04:00-08:00): Dawn watch from 4 AM to 8 AM
- **Forenoon Watch** (08:00-12:00): Morning watch from 8 AM to noon
- **Afternoon Watch** (12:00-16:00): Day watch from noon to 4 PM
- **First Dog Watch** (16:00-18:00): Short evening watch from 4 PM to 6 PM
- **Second Dog Watch** (18:00-20:00): Short evening watch from 6 PM to 8 PM

### The Dogwatch System

The two "dogwatches" are only 2 hours each (instead of the standard 4 hours), which serves an important purpose: it prevents the same crew members from always standing the same watches. Without dogwatches, sailors would be stuck with the same schedule every day. The dogwatches rotate the schedule, ensuring fair distribution of the less desirable night watches.

### Bell Patterns

- **Single Strike** (1): One bell sound
- **Double Strike** (2): Two bell sounds struck quickly together  
- **Pattern** shows the sequence: "2,2,1" means two double strikes followed by one single strike

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
