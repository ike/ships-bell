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

        # 4 double-strikes at 00:00.
        sb.play_single_strike.reset_mock()
        sb.play_double_strike.reset_mock()
        sb.step(0, 0)
        self.assertEqual(4, sb.play_double_strike.call_count)
        self.assertEqual(0, sb.play_single_strike.call_count)

        # 4 double-strikes at 24:00 (actually 24:00 is impossible)
        sb.play_single_strike.reset_mock()
        sb.play_double_strike.reset_mock()
        sb.step(24, 0)
        self.assertEqual(4, sb.play_double_strike.call_count)
        self.assertEqual(0, sb.play_single_strike.call_count)

        # 0 double-strikes, 1 single-strike at 00:30
        sb.play_single_strike.reset_mock()
        sb.play_double_strike.reset_mock()
        sb.step(0, 30)
        self.assertEqual(0, sb.play_double_strike.call_count)
        self.assertEqual(1, sb.play_single_strike.call_count)

    def test_strike_computation(self):
        """Test strike calculation logic."""
        sb = ShipsBell(".")
        # Full hours.
        self.assertEqual((1, 0), sb.compute_strikes(1, 0))
        self.assertEqual((2, 0), sb.compute_strikes(2, 0))
        self.assertEqual((3, 0), sb.compute_strikes(3, 0))
        self.assertEqual((4, 0), sb.compute_strikes(4, 0))
        self.assertEqual((1, 0), sb.compute_strikes(5, 0))
        self.assertEqual((2, 0), sb.compute_strikes(6, 0))

        # Half hours.
        self.assertEqual((1, 1), sb.compute_strikes(1, 30))
        self.assertEqual((1, 0), sb.compute_strikes(1, 31))
        self.assertEqual((1, 0), sb.compute_strikes(1, 29))

        self.assertEqual((4, 0), sb.compute_strikes(0, 0))
        self.assertEqual((0, 1), sb.compute_strikes(0, 30))
        self.assertEqual((3, 1), sb.compute_strikes(23, 30))
        self.assertEqual((4, 0), sb.compute_strikes(24, 0))
        self.assertEqual((4, 0), sb.compute_strikes(0, 0))
        self.assertEqual((0, 1), sb.compute_strikes(0, 30))

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
    def test_trigger_files_created(self, mock_makedirs, mock_open):  # pylint: disable=unused-argument
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
    def test_trigger_file_error_handling(self, mock_makedirs, mock_open):  # pylint: disable=unused-argument
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

        # Double-strike at 9:00.
        sb.play_single_strike.reset_mock()
        sb.play_double_strike.reset_mock()
        sb.step(9, 0)
        self.assertEqual(1, sb.play_double_strike.call_count)
        self.assertEqual(0, sb.play_single_strike.call_count)

        # Double-strike at 17:00.
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
