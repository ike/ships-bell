#!/usr/bin/env python3

"""
A little app that plays ship's bell sounds every 30 minutes.
"""

import argparse
import os
import sys
import threading
import time


class ShipsBellError(Exception):
    """Custom exception for Ship's Bell errors."""


class ShipsBell(threading.Thread):
    """Ship's bell timer that plays bell sounds every 30 minutes."""

    SECONDS_PER_MINUTE = 60
    MINUTES_PER_HALF_HOUR = 30
    MAX_DOUBLE_STRIKES = 4

    def __init__(self, working_dir=None, start=0, end=24):
        super().__init__()
        self.daemon = True
        # Auto-detect working directory if not provided
        if working_dir is None:
            self.working_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.working_dir = working_dir
        assert end >= start
        self.start_time = start
        self.end_time = end
        self.audio_lock = threading.Lock()

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

                for i in range(double_strikes):
                    if i > 0:
                        time.sleep(0.3)
                    self.play_double_strike()
                if double_strikes > 0 and single_strikes > 0:
                    time.sleep(0.3)
                for i in range(single_strikes):
                    if i > 0:
                        time.sleep(0.3)
                    self.play_single_strike()

                # Play special noon sound after regular bells at 12:00
                if hours == 12 and minutes == 0:
                    time.sleep(1.0)  # Brief pause after bells
                    self.play_noon_sound()

    @staticmethod
    def compute_strikes(hours, minutes):
        """Calculate number of double and single strikes for given time."""
        # Maritime watch system: bells are struck every 30 minutes
        # The number of bells indicates time elapsed since the start of the current watch

        # Map specific times to bell counts based on traditional maritime watch system
        time_to_bells = {
            # First Watch (20:00-24:00)
            (20, 30): 1,
            (21, 0): 2,
            (21, 30): 3,
            (22, 0): 4,
            (22, 30): 5,
            (23, 0): 6,
            (23, 30): 7,
            (0, 0): 8,
            # Middle Watch (00:00-04:00)
            (0, 30): 1,
            (1, 0): 2,
            (1, 30): 3,
            (2, 0): 4,
            (2, 30): 5,
            (3, 0): 6,
            (3, 30): 7,
            (4, 0): 8,
            # Morning Watch (04:00-08:00)
            (4, 30): 1,
            (5, 0): 2,
            (5, 30): 3,
            (6, 0): 4,
            (6, 30): 5,
            (7, 0): 6,
            (7, 30): 7,
            (8, 0): 8,
            # Forenoon Watch (08:00-12:00)
            (8, 30): 1,
            (9, 0): 2,
            (9, 30): 3,
            (10, 0): 4,
            (10, 30): 5,
            (11, 0): 6,
            (11, 30): 7,
            (12, 0): 8,
            # Afternoon Watch (12:00-16:00)
            (12, 30): 1,
            (13, 0): 2,
            (13, 30): 3,
            (14, 0): 4,
            (14, 30): 5,
            (15, 0): 6,
            (15, 30): 7,
            (16, 0): 8,
            # First Dog Watch (16:00-18:00) - only 4 bells max
            (16, 30): 1,
            (17, 0): 2,
            (17, 30): 3,
            (18, 0): 4,
            # Second Dog Watch (18:00-20:00) - only 4 bells max
            (18, 30): 1,
            (19, 0): 2,
            (19, 30): 3,
            (20, 0): 4,
        }

        # Handle 24:00 as equivalent to 0:00
        if hours == 24:
            hours = 0

        total_bells = time_to_bells.get((hours, minutes), 0)

        # Convert total bells to double strikes and single strikes
        # Pattern: each pair of bells = 1 double strike, odd bell = 1 single strike
        double_strikes = total_bells // 2
        single_strikes = total_bells % 2

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
        self.trigger_user_audio("double")

    def play_single_strike(self):
        """Play single strike bell sound."""
        self.trigger_user_audio("single")

    def play_noon_sound(self):
        """Play special noon sound."""
        self.trigger_user_audio("noon")

    def trigger_user_audio(self, strike_type):
        """Trigger audio via file system - completely separate from service process."""
        trigger_dir = os.path.expanduser("~/.local/share/ships-bell/triggers")
        os.makedirs(trigger_dir, exist_ok=True)

        trigger_file = os.path.join(trigger_dir, f"{strike_type}_strike")

        # Create trigger file - watcher process will detect and play audio
        try:
            with open(trigger_file, "w", encoding="utf-8") as f:
                f.write(str(time.time()))
        except Exception as e:
            raise ShipsBellError(f"Failed to create trigger file: {e}") from e


def handle_args(args):
    """Parse command line arguments and return configured ShipsBell instance."""
    this_script = args[0]
    parser = argparse.ArgumentParser(
        this_script, description="A little ship's bell app"
    )
    parser.add_argument(
        "--from",
        type=int,
        default=9,
        help="Full hour, from which bell sound is emitted (default:9)",
    )
    parser.add_argument(
        "--to",
        type=int,
        default=20,
        help="Full hour, until which bell sound is emitted (default:20)",
    )
    parser.add_argument(
        "--working-dir",
        type=str,
        help="Working directory for audio files (auto-detected if not provided)",
    )
    parsed_args = parser.parse_args(args[1:])
    from_hour = getattr(parsed_args, "from")
    to_hour = getattr(parsed_args, "to")
    working_dir = getattr(parsed_args, "working_dir")

    if from_hour < 0 or from_hour > 24 or to_hour < 0 or to_hour > 24:
        raise ShipsBellError("Hours must be in range 0..24.")
    if from_hour > to_hour:
        raise ShipsBellError(
            "Value of 'to' hour must be greater than or equal to value of 'from' hour."
        )

    return ShipsBell(working_dir, from_hour, to_hour)


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
