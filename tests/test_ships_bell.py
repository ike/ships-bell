"""Tests for Ship's Bell application."""

import unittest
from unittest.mock import Mock, patch

from ships_bell import ShipsBell, ShipsBellError, handle_args

# Tests may use long method names.
# pylint:disable=invalid-name


class TestShipsBell(unittest.TestCase):
    """Test cases for ShipsBell class."""

    def test_step_happy_path(self):
        """Test normal bell striking behavior."""
        sb = ShipsBell(".", 0, 24)
        sb.play_single_strike = Mock()
        sb.play_double_strike = Mock()

        # No strike at 11:22.
        sb.play_single_strike.reset_mock()
        sb.play_double_strike.reset_mock()
        sb.step(11, 22)
        self.assertEqual(0, sb.play_double_strike.call_count)
        self.assertEqual(0, sb.play_single_strike.call_count)

        # 4 double-strikes at 04:00.
        sb.play_single_strike.reset_mock()
        sb.play_double_strike.reset_mock()
        sb.step(4, 0)
        self.assertEqual(4, sb.play_double_strike.call_count)
        self.assertEqual(0, sb.play_single_strike.call_count)

    def test_step_striking_boundary_cases(self):
        """Test bell striking at boundary times."""
        sb = ShipsBell(".", 0, 24)
        sb.play_single_strike = Mock()
        sb.play_double_strike = Mock()

        # 4 double-strikes at 00:00 (8 bells - midnight).
        sb.play_single_strike.reset_mock()
        sb.play_double_strike.reset_mock()
        sb.step(0, 0)
        self.assertEqual(4, sb.play_double_strike.call_count)
        self.assertEqual(0, sb.play_single_strike.call_count)

        # 4 double-strikes at 24:00 (hour 24 wraps to hour 0)
        sb.play_single_strike.reset_mock()
        sb.play_double_strike.reset_mock()
        sb.step(24, 0)
        self.assertEqual(4, sb.play_double_strike.call_count)
        self.assertEqual(0, sb.play_single_strike.call_count)

        # 0 double-strikes, 1 single-strike at 00:30 (1 bell)
        sb.play_single_strike.reset_mock()
        sb.play_double_strike.reset_mock()
        sb.step(0, 30)
        self.assertEqual(0, sb.play_double_strike.call_count)
        self.assertEqual(1, sb.play_single_strike.call_count)

    def test_strike_computation(self):
        """Test strike calculation logic for traditional maritime watch system."""
        sb = ShipsBell(".")

        # Test First Watch (20:00-24:00 / 8pm-midnight)
        self.assertEqual((0, 1), sb.compute_strikes(20, 30))  # 1 bell - 20:30
        self.assertEqual((1, 0), sb.compute_strikes(21, 0))  # 2 bells - 21:00
        self.assertEqual((1, 1), sb.compute_strikes(21, 30))  # 3 bells - 21:30
        self.assertEqual((2, 0), sb.compute_strikes(22, 0))  # 4 bells - 22:00
        self.assertEqual((2, 1), sb.compute_strikes(22, 30))  # 5 bells - 22:30
        self.assertEqual((3, 0), sb.compute_strikes(23, 0))  # 6 bells - 23:00
        self.assertEqual((3, 1), sb.compute_strikes(23, 30))  # 7 bells - 23:30
        self.assertEqual((4, 0), sb.compute_strikes(0, 0))  # 8 bells - 00:00 (midnight)

        # Test Middle Watch (00:00-04:00 / midnight-4am)
        self.assertEqual((0, 1), sb.compute_strikes(0, 30))  # 1 bell - 00:30
        self.assertEqual((1, 0), sb.compute_strikes(1, 0))  # 2 bells - 01:00
        self.assertEqual((1, 1), sb.compute_strikes(1, 30))  # 3 bells - 01:30
        self.assertEqual((2, 0), sb.compute_strikes(2, 0))  # 4 bells - 02:00
        self.assertEqual((2, 1), sb.compute_strikes(2, 30))  # 5 bells - 02:30
        self.assertEqual((3, 0), sb.compute_strikes(3, 0))  # 6 bells - 03:00
        self.assertEqual((3, 1), sb.compute_strikes(3, 30))  # 7 bells - 03:30
        self.assertEqual((4, 0), sb.compute_strikes(4, 0))  # 8 bells - 04:00

        # Test Morning Watch (04:00-08:00 / 4am-8am)
        self.assertEqual((0, 1), sb.compute_strikes(4, 30))  # 1 bell - 04:30
        self.assertEqual((1, 0), sb.compute_strikes(5, 0))  # 2 bells - 05:00
        self.assertEqual((1, 1), sb.compute_strikes(5, 30))  # 3 bells - 05:30
        self.assertEqual((2, 0), sb.compute_strikes(6, 0))  # 4 bells - 06:00
        self.assertEqual((2, 1), sb.compute_strikes(6, 30))  # 5 bells - 06:30
        self.assertEqual((3, 0), sb.compute_strikes(7, 0))  # 6 bells - 07:00
        self.assertEqual((3, 1), sb.compute_strikes(7, 30))  # 7 bells - 07:30
        self.assertEqual((4, 0), sb.compute_strikes(8, 0))  # 8 bells - 08:00

        # Test Forenoon Watch (08:00-12:00 / 8am-noon)
        self.assertEqual((0, 1), sb.compute_strikes(8, 30))  # 1 bell - 08:30
        self.assertEqual((1, 0), sb.compute_strikes(9, 0))  # 2 bells - 09:00
        self.assertEqual((1, 1), sb.compute_strikes(9, 30))  # 3 bells - 09:30
        self.assertEqual((2, 0), sb.compute_strikes(10, 0))  # 4 bells - 10:00
        self.assertEqual((2, 1), sb.compute_strikes(10, 30))  # 5 bells - 10:30
        self.assertEqual((3, 0), sb.compute_strikes(11, 0))  # 6 bells - 11:00
        self.assertEqual((3, 1), sb.compute_strikes(11, 30))  # 7 bells - 11:30
        self.assertEqual((4, 0), sb.compute_strikes(12, 0))  # 8 bells - 12:00 (noon)

        # Test Afternoon Watch (12:00-16:00 / noon-4pm)
        self.assertEqual((0, 1), sb.compute_strikes(12, 30))  # 1 bell - 12:30
        self.assertEqual((1, 0), sb.compute_strikes(13, 0))  # 2 bells - 13:00
        self.assertEqual((1, 1), sb.compute_strikes(13, 30))  # 3 bells - 13:30
        self.assertEqual((2, 0), sb.compute_strikes(14, 0))  # 4 bells - 14:00
        self.assertEqual((2, 1), sb.compute_strikes(14, 30))  # 5 bells - 14:30
        self.assertEqual((3, 0), sb.compute_strikes(15, 0))  # 6 bells - 15:00
        self.assertEqual((3, 1), sb.compute_strikes(15, 30))  # 7 bells - 15:30
        self.assertEqual((4, 0), sb.compute_strikes(16, 0))  # 8 bells - 16:00

        # Test First Dog Watch (16:00-18:00 / 4pm-6pm) - only goes to 4 bells
        self.assertEqual((0, 1), sb.compute_strikes(16, 30))  # 1 bell - 16:30
        self.assertEqual((1, 0), sb.compute_strikes(17, 0))  # 2 bells - 17:00
        self.assertEqual((1, 1), sb.compute_strikes(17, 30))  # 3 bells - 17:30
        self.assertEqual(
            (2, 0), sb.compute_strikes(18, 0)
        )  # 4 bells - 18:00 (end of First Dog)

        # Test Second Dog Watch (18:00-20:00 / 6pm-8pm) - only goes to 4 bells
        self.assertEqual((0, 1), sb.compute_strikes(18, 30))  # 1 bell - 18:30
        self.assertEqual((1, 0), sb.compute_strikes(19, 0))  # 2 bells - 19:00
        self.assertEqual((1, 1), sb.compute_strikes(19, 30))  # 3 bells - 19:30
        self.assertEqual((2, 0), sb.compute_strikes(20, 0))  # 4 bells - 20:00

    def test_dogwatch_periods(self):
        """Test that dogwatches are properly limited to 4 bells maximum."""
        sb = ShipsBell(".")

        # First Dog Watch times - should not exceed 4 bells (2 hours)
        # Note: 16:00 is 8 bells (end of Afternoon Watch), so start checking from 16:30
        for hour, minute in [(16, 30), (17, 0), (17, 30), (18, 0)]:
            double, single = sb.compute_strikes(hour, minute)
            total_bells = double * 2 + single
            self.assertLessEqual(
                total_bells,
                4,
                f"First Dog Watch exceeded 4 bells at {hour:02d}:{minute:02d}",
            )

        # Second Dog Watch times - should not exceed 4 bells (2 hours)
        # Note: 20:00 is 4 bells (end of Second Dog Watch), so it's included
        for hour, minute in [(18, 30), (19, 0), (19, 30), (20, 0)]:
            double, single = sb.compute_strikes(hour, minute)
            total_bells = double * 2 + single
            self.assertLessEqual(
                total_bells,
                4,
                f"Second Dog Watch exceeded 4 bells at {hour:02d}:{minute:02d}",
            )

    def test_watch_transitions(self):
        """Test transitions between watch periods."""
        sb = ShipsBell(".")

        # Test transition from First Dog to Second Dog
        self.assertEqual(
            (2, 0), sb.compute_strikes(18, 0)
        )  # End of First Dog (4 bells)
        self.assertEqual(
            (0, 1), sb.compute_strikes(18, 30)
        )  # Start of Second Dog (1 bell)

        # Test transition from Second Dog to First Watch
        self.assertEqual(
            (2, 0), sb.compute_strikes(20, 0)
        )  # End of Second Dog (4 bells)
        self.assertEqual(
            (0, 1), sb.compute_strikes(20, 30)
        )  # Start of First Watch (1 bell)

        # Test transition from First Watch to Middle Watch (across midnight)
        self.assertEqual(
            (4, 0), sb.compute_strikes(0, 0)
        )  # End of First Watch (8 bells)
        self.assertEqual(
            (0, 1), sb.compute_strikes(0, 30)
        )  # Start of Middle Watch (1 bell)

    def test_sleep_time_computation(self):
        """Test sleep time calculation."""
        sb = ShipsBell(".")
        self.assertAlmostEqual(30.0 / 2.0 * 60.0, sb.compute_sleep_time(30))
        self.assertAlmostEqual(30.0 / 2.0 * 60.0, sb.compute_sleep_time(0))
        self.assertAlmostEqual((30.0 - 22.0) / 2.0 * 60.0, sb.compute_sleep_time(22))
        self.assertAlmostEqual((30.0 - 28.0) / 2.0 * 60.0, sb.compute_sleep_time(28))
        self.assertAlmostEqual(1.0, sb.compute_sleep_time(29))
        self.assertAlmostEqual(1.0, sb.compute_sleep_time(59))
        self.assertAlmostEqual(60.0, sb.compute_sleep_time(28))
        self.assertAlmostEqual(60.0, sb.compute_sleep_time(58))

    @patch("builtins.open", create=True)
    @patch("os.makedirs")
    def test_trigger_files_created(
        self, mock_makedirs, mock_open
    ):  # pylint: disable=unused-argument
        """Test that trigger files are created for audio playback."""
        sb = ShipsBell(".", 0, 24)
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        sb.play_single_strike()
        mock_open.assert_called()
        mock_file.write.assert_called()

        mock_open.reset_mock()
        mock_file.reset_mock()

        sb.play_double_strike()
        mock_open.assert_called()
        mock_file.write.assert_called()

    @patch("builtins.open", create=True)
    @patch("os.makedirs")
    def test_trigger_file_error_handling(
        self, mock_makedirs, mock_open
    ):  # pylint: disable=unused-argument
        """Test trigger file creation error handling."""
        sb = ShipsBell(".", 0, 24)
        mock_open.side_effect = IOError("Permission denied")

        with self.assertRaises(ShipsBellError):
            sb.play_single_strike()

    def test_respect_silent_period(self):
        """Test silent period functionality."""
        sb = ShipsBell(".", 9, 17)

        sb.play_single_strike = Mock()
        sb.play_double_strike = Mock()

        # No strike at 8:30.
        sb.play_single_strike.reset_mock()
        sb.play_double_strike.reset_mock()
        sb.step(8, 30)
        self.assertEqual(0, sb.play_double_strike.call_count)
        self.assertEqual(0, sb.play_single_strike.call_count)

        # No strike at 17:30.
        sb.play_single_strike.reset_mock()
        sb.play_double_strike.reset_mock()
        sb.step(17, 30)
        self.assertEqual(0, sb.play_double_strike.call_count)
        self.assertEqual(0, sb.play_single_strike.call_count)

        # 2 bells (1 double-strike) at 9:00.
        sb.play_single_strike.reset_mock()
        sb.play_double_strike.reset_mock()
        sb.step(9, 0)
        self.assertEqual(1, sb.play_double_strike.call_count)
        self.assertEqual(0, sb.play_single_strike.call_count)

        # 2 bells (1 double-strike) at 17:00.
        sb.play_single_strike.reset_mock()
        sb.play_double_strike.reset_mock()
        sb.step(17, 0)
        self.assertEqual(1, sb.play_double_strike.call_count)
        self.assertEqual(0, sb.play_single_strike.call_count)

    def test_handle_args_no_explicit_args(self):
        """Test argument parsing with defaults."""
        args1 = ["this_script"]
        sb = handle_args(args1)
        self.assertEqual(9, sb.start_time)
        self.assertEqual(20, sb.end_time)

    def test_handle_args_from_to(self):
        """Test argument parsing with custom times."""
        args1 = ["this_script", "--from", "9", "--to", "17"]
        sb = handle_args(args1)
        self.assertEqual(9, sb.start_time)
        self.assertEqual(17, sb.end_time)

    def test_handle_args_bad_cases(self):
        """Test argument parsing error cases."""
        # Outside 0..24 range.
        with self.assertRaises(ShipsBellError):
            _ = handle_args(["this_script", "--from", "99"])
        with self.assertRaises(ShipsBellError):
            _ = handle_args(["this_script", "--to", "99"])
        with self.assertRaises(ShipsBellError):
            _ = handle_args(["this_script", "--to", "-9"])
        # 'from' greater or equal to 'to'.
        with self.assertRaises(ShipsBellError):
            _ = handle_args(["this_script", "--from", "12", "--to", "9"])
        # 'from' greater to 'to'.
        with self.assertRaises(ShipsBellError):
            _ = handle_args(["this_script", "--from", "13", "--to", "12"])
