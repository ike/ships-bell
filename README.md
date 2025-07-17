# Ship's Bell
A little Python 3 app that plays the well-known [ship's bell](https://en.wikipedia.org/wiki/Ship%27s_bell) sounds every half an hour.

## Requirements
1. Standard Python installation, version >= 3.3
2. macOS (uses native `afplay` for audio)

## Basic usage
```
# Show help:
python3 ./ships_bell.py --help

# Bell sounds from 00:00 to 24:00:
python3 ./ships_bell.py

# No bell sounds before 9:00 and after 20:00:
python3 ./ships_bell.py  --from 9 --to 20
```

## macOS Background Service
To run as a background service that starts automatically:

```bash
# Install the service (runs 9 AM to 8 PM):
./install-macos-service.sh

# Uninstall the service:
./uninstall-macos-service.sh
```

The service will:
- Start automatically when you log in
- Ring bells every 30 minutes during configured hours
- Run silently in the background
- Write logs to `ships-bell.log` and `ships-bell.error.log`
## License
See file LICENSE.

