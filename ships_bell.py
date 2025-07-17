#!/usr/bin/env python3

"""
A little app that plays ship's bell sounds every 30 minutes.
"""

import argparse
import os
import subprocess
import sys
import threading
import time

# Using macOS native audio player for better background service compatibility
MP3_PLAYER_CALL = "afplay {mp3_file}"


class ShipsBellError(Exception):
    """Custom exception for Ship's Bell errors."""


class ShipsBell(threading.Thread):
    """Ship's bell timer that plays bell sounds every 30 minutes."""
    SECONDS_PER_MINUTE = 60
    MINUTES_PER_HALF_HOUR = 30
    MAX_DOUBLE_STRIKES = 4

    def __init__(self, working_dir, start=0, end=24):
        super().__init__()
        self.daemon = True
        self.working_dir = working_dir
        assert end >= start
        self.start_time = start
        self.end_time = end

    def run(self):  # pragma: no cover
        while True:
            current_time = time.localtime()
            minutes = current_time.tm_min
            hours = current_time.tm_hour
            self.step(hours, minutes)
            time.sleep(self.compute_sleep_time(minutes))

    def step(self, hours, minutes):
        """Check if bell should strike and play appropriate sounds."""
        if (self.start_time <= hours < self.end_time) or (
            hours == self.end_time and minutes == 0
        ):
            # Strike bell at every half or full hour.
            if (minutes % ShipsBell.MINUTES_PER_HALF_HOUR) == 0:
                double_strikes, single_strikes = self.compute_strikes(hours, minutes)
                for _ in range(double_strikes):
                    self.play_double_strike()
                for _ in range(single_strikes):
                    self.play_single_strike()

    @staticmethod
    def compute_strikes(hours, minutes):
        """Calculate number of double and single strikes for given time."""
        # Single strike only on half hour.
        single_strikes = 1 if minutes == ShipsBell.MINUTES_PER_HALF_HOUR else 0
        double_strikes = hours % ShipsBell.MAX_DOUBLE_STRIKES
        if double_strikes == 0 and single_strikes == 0:
            double_strikes = ShipsBell.MAX_DOUBLE_STRIKES
        return (double_strikes, single_strikes)

    @staticmethod
    def compute_sleep_time(minutes):
        """Calculate how long to sleep until next bell check."""
        # Remaining minutes till half or full hour.
        delta_minutes = (
            ShipsBell.MINUTES_PER_HALF_HOUR - minutes % ShipsBell.MINUTES_PER_HALF_HOUR
        )
        # If enough time is left, sleep through half of it.
        if delta_minutes >= 2:
            return delta_minutes / 2.0 * ShipsBell.SECONDS_PER_MINUTE
        # During the last minute, check every second.
        return 1.0

    def play_double_strike(self):
        """Play double strike bell sound."""
        ShipsBell.play_mp3(self.working_dir + "/res/DoubleStrike.mp3")

    def play_single_strike(self):
        """Play single strike bell sound."""
        ShipsBell.play_mp3(self.working_dir + "/res/SingleStrike.mp3")

    @staticmethod
    def play_mp3(path):
        """Play MP3 file at given path using configured player."""
        cmd = MP3_PLAYER_CALL.format(mp3_file=path).split()
        exit_code = subprocess.call(cmd)
        if exit_code != 0:
            raise ShipsBellError("Failed to play " + path)


def handle_args(args):
    """Parse command line arguments and return configured ShipsBell instance."""
    this_script = args[0]
    parser = argparse.ArgumentParser(
        this_script, description="A little ship's bell app"
    )
    parser.add_argument(
        "--from",
        type=int,
        default=0,
        help="Full hour, from which bell sound is emitted (default:0)",
    )
    parser.add_argument(
        "--to",
        type=int,
        default=24,
        help="Full hour, until which bell sound is emitted (default:24)",
    )
    parsed_args = parser.parse_args(args[1:])
    from_hour = getattr(parsed_args, "from")
    to_hour = getattr(parsed_args, "to")
    if from_hour < 0 or from_hour > 24 or to_hour < 0 or to_hour > 24:
        raise ShipsBellError("Hours must be in range 0..24.")
    if from_hour > to_hour:
        raise ShipsBellError(
            "Value of 'to' hour must be greater than or equal to value of 'from' hour."
        )
    script_dir = os.path.dirname(os.path.abspath(this_script))
    return ShipsBell(script_dir, from_hour, to_hour)


if __name__ == "__main__":  # pragma: no cover

    # Now start app.
    try:
        SHIPS_BELL = handle_args(sys.argv)
        # Play double-strike at startup, mainly to detect a missing MP3 player.
        SHIPS_BELL.play_double_strike()
        SHIPS_BELL.start()
        SHIPS_BELL.join()

    except (FileNotFoundError, ShipsBellError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
