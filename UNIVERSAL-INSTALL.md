# Universal Installation System

Ship's Bell now supports universal installation on any Mac with a single command.

## What Changed

### Before (User-Specific)
- Hardcoded paths to `/Users/ike/`
- Required manual file editing for different users
- Installation scattered across multiple directories
- Complex setup process

### After (Universal)
- Dynamic path detection and user resolution
- One-command installation from GitHub
- Self-contained in `~/.local/share/ships-bell/`
- Template-based configuration

## Installation Methods

### 1. One-Command Install (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/ike/ships-bell/master/install.sh | bash
```

### 2. Custom Schedule
```bash
START_HOUR=8 END_HOUR=22 curl -fsSL .../install.sh | bash
```

### 3. Manual Install
```bash
git clone https://github.com/ike/ships-bell.git
cd ships-bell
./install-macos-service.sh
```

## Technical Implementation

### Dynamic Path Resolution
- `ships_bell.py` auto-detects its working directory
- Template-based plist files with variable substitution
- User-specific service names (`{user}.ships-bell`)

### Self-Contained Architecture
```
~/.local/share/ships-bell/          # Everything in one place
├── ships_bell.py                   # Main application
├── ships-bell-watcher              # Audio watcher
├── audio/                          # Audio files
├── logs/                           # Service logs
└── triggers/                       # Runtime communication
```

### Template System
- `*.plist.template` files with `{{VARIABLE}}` placeholders
- Installation script substitutes actual values
- Supports custom users, paths, and schedules

## Key Features

✅ **Universal Compatibility**
- Works on any Mac with Python 3
- No hardcoded usernames or paths
- Automatic user detection

✅ **One-Command Install**
- Download and install from GitHub
- Handles dependencies and prerequisites
- Configurable via environment variables

✅ **Self-Contained**
- All files in single directory
- Easy backup and migration
- Clean uninstall

✅ **Robust Architecture**
- File-based trigger system
- Proper LaunchAgent separation
- High-quality audio playback

## Migration from Old System

The new installer automatically handles migration:
1. Detects and removes old installations
2. Preserves user preferences
3. Migrates to new directory structure
4. Updates service configurations

## Testing

Comprehensive testing ensures reliability:
- Dynamic path detection
- Template substitution
- Service loading and unloading
- Audio quality verification
- Cross-user compatibility

## Future Enhancements

The universal system enables:
- Package manager distribution (Homebrew)
- Automated updates
- Configuration management
- Multi-user installations

---

*This universal installation system makes Ship's Bell accessible to any Mac user with a single command.*
