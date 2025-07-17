"""Tests for Ship's Bell installer scripts."""

import os
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch


class TestInstallers(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Test cases for installer scripts."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_install_macos_service_script_exists(self):
        """Test that install-macos-service.sh exists and is executable."""
        script_path = os.path.join(self.script_dir, "install-macos-service.sh")
        self.assertTrue(os.path.exists(script_path))
        self.assertTrue(os.access(script_path, os.X_OK))

    def test_install_script_exists(self):
        """Test that install.sh exists and is executable."""
        script_path = os.path.join(self.script_dir, "install.sh")
        self.assertTrue(os.path.exists(script_path))
        self.assertTrue(os.access(script_path, os.X_OK))

    def test_uninstall_script_exists(self):
        """Test that uninstall-macos-service.sh exists and is executable."""
        script_path = os.path.join(self.script_dir, "uninstall-macos-service.sh")
        self.assertTrue(os.path.exists(script_path))
        self.assertTrue(os.access(script_path, os.X_OK))

    def test_install_macos_service_dry_run(self):
        """Test install-macos-service.sh with dry run (syntax check)."""
        script_path = os.path.join(self.script_dir, "install-macos-service.sh")

        # Test bash syntax
        result = subprocess.run(
            ["bash", "-n", script_path], capture_output=True, text=True, check=False
        )
        self.assertEqual(
            result.returncode,
            0,
            f"Syntax error in install-macos-service.sh: {result.stderr}",
        )

    def test_install_script_dry_run(self):
        """Test install.sh with dry run (syntax check)."""
        script_path = os.path.join(self.script_dir, "install.sh")

        # Test bash syntax
        result = subprocess.run(
            ["bash", "-n", script_path], capture_output=True, text=True, check=False
        )
        self.assertEqual(
            result.returncode, 0, f"Syntax error in install.sh: {result.stderr}"
        )

    def test_uninstall_script_dry_run(self):
        """Test uninstall-macos-service.sh with dry run (syntax check)."""
        script_path = os.path.join(self.script_dir, "uninstall-macos-service.sh")

        # Test bash syntax
        result = subprocess.run(
            ["bash", "-n", script_path], capture_output=True, text=True, check=False
        )
        self.assertEqual(
            result.returncode,
            0,
            f"Syntax error in uninstall-macos-service.sh: {result.stderr}",
        )

    def test_template_files_exist(self):
        """Test that plist template files exist."""
        bell_template = os.path.join(
            self.script_dir, "com.ike.ships-bell.plist.template"
        )
        watcher_template = os.path.join(
            self.script_dir, "com.ike.ships-bell-watcher.plist.template"
        )

        self.assertTrue(os.path.exists(bell_template))
        self.assertTrue(os.path.exists(watcher_template))

    def test_template_substitution_variables(self):
        """Test that template files contain expected substitution variables."""
        bell_template = os.path.join(
            self.script_dir, "com.ike.ships-bell.plist.template"
        )
        watcher_template = os.path.join(
            self.script_dir, "com.ike.ships-bell-watcher.plist.template"
        )

        with open(bell_template, "r", encoding="utf-8") as f:
            bell_content = f.read()

        with open(watcher_template, "r", encoding="utf-8") as f:
            watcher_content = f.read()

        # Check for required template variables
        self.assertIn("{{USER}}", bell_content)
        self.assertIn("{{INSTALL_DIR}}", bell_content)
        self.assertIn("{{START_HOUR}}", bell_content)
        self.assertIn("{{END_HOUR}}", bell_content)

        self.assertIn("{{USER}}", watcher_content)
        self.assertIn("{{INSTALL_DIR}}", watcher_content)

    @patch.dict(
        os.environ,
        {"INSTALL_DIR": "/test/install", "START_HOUR": "8", "END_HOUR": "22"},
    )
    @patch("subprocess.run")
    @patch("os.makedirs")
    @patch("shutil.copy")
    @patch("shutil.copytree")
    def test_install_macos_service_environment_variables(
        self, mock_copytree, mock_copy, mock_makedirs, mock_run  # pylint: disable=unused-argument
    ):
        """Test that install-macos-service.sh respects environment variables."""
        script_path = os.path.join(self.script_dir, "install-macos-service.sh")

        # Mock successful execution
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # We can't easily test the full script execution without side effects,
        # but we can verify the script reads environment variables correctly
        # by checking the script content
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()

        # Verify environment variable usage
        self.assertIn(
            'INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/share/ships-bell}"',
            script_content,
        )
        self.assertIn('START_HOUR="${START_HOUR:-9}"', script_content)
        self.assertIn('END_HOUR="${END_HOUR:-20}"', script_content)

    def test_script_error_handling(self):
        """Test that scripts have proper error handling."""
        scripts = [
            "install-macos-service.sh",
            "install.sh",
            "uninstall-macos-service.sh",
        ]

        for script_name in scripts:
            script_path = os.path.join(self.script_dir, script_name)
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for 'set -e' (exit on error)
            self.assertIn(
                "set -e",
                content,
                f"{script_name} should have 'set -e' for error handling",
            )

    def test_install_script_prerequisites_check(self):
        """Test that install.sh checks for required tools."""
        script_path = os.path.join(self.script_dir, "install.sh")

        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for prerequisite checks
        self.assertIn("python3", content)
        self.assertIn("curl", content)
        self.assertIn("wget", content)
        self.assertIn("command -v", content)

    def test_uninstall_script_safety_checks(self):
        """Test that uninstall script has safety checks."""
        script_path = os.path.join(self.script_dir, "uninstall-macos-service.sh")

        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for user confirmation before removing files
        self.assertIn("read -p", content)
        self.assertIn("Remove installation directory", content)

    def test_script_output_messages(self):
        """Test that scripts have informative output messages."""
        scripts = [
            (
                "install-macos-service.sh",
                ["Installing Ship's Bell", "Installation complete"],
            ),
            ("install.sh", ["One-Command Installer", "Installation complete"]),
            (
                "uninstall-macos-service.sh",
                ["Uninstalling Ship's Bell", "uninstallation complete"],
            ),
        ]

        for script_name, expected_messages in scripts:
            script_path = os.path.join(self.script_dir, script_name)
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()

            for message in expected_messages:
                self.assertIn(
                    message, content, f"{script_name} should contain message: {message}"
                )

    def test_install_script_github_integration(self):
        """Test that install.sh has GitHub download functionality."""
        script_path = os.path.join(self.script_dir, "install.sh")

        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for GitHub-related functionality
        self.assertIn("REPO_URL", content)
        self.assertIn("github.com", content)
        self.assertIn("archive/master.tar.gz", content)
        self.assertIn("git clone", content)

    def test_plist_template_validity(self):
        """Test that plist templates are valid XML structure."""
        templates = [
            "com.ike.ships-bell.plist.template",
            "com.ike.ships-bell-watcher.plist.template",
        ]

        for template_name in templates:
            template_path = os.path.join(self.script_dir, template_name)
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Basic XML structure checks
            self.assertIn("<?xml", content)
            self.assertIn("<plist", content)
            self.assertIn("</plist>", content)
            self.assertIn("<dict>", content)
            self.assertIn("</dict>", content)

            # LaunchAgent specific keys
            self.assertIn("<key>Label</key>", content)
            self.assertIn("<key>ProgramArguments</key>", content)

    def test_directory_structure_creation(self):
        """Test that installer creates proper directory structure."""
        script_path = os.path.join(self.script_dir, "install-macos-service.sh")

        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for directory creation commands
        expected_dirs = [
            "$INSTALL_DIR",
            "$INSTALL_DIR/logs",
            "$INSTALL_DIR/audio",
            "$INSTALL_DIR/triggers",
        ]

        for directory in expected_dirs:
            self.assertIn(f'mkdir -p "{directory}"', content)

    def test_file_permissions(self):
        """Test that scripts set proper file permissions."""
        scripts = ["install-macos-service.sh", "install.sh"]

        for script_name in scripts:
            script_path = os.path.join(self.script_dir, script_name)
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for chmod commands
            self.assertIn("chmod +x", content)

    def test_launchctl_integration(self):
        """Test that macOS service scripts use launchctl properly."""
        # Test install script
        install_script = os.path.join(self.script_dir, "install-macos-service.sh")
        with open(install_script, "r", encoding="utf-8") as f:
            install_content = f.read()

        self.assertIn("launchctl", install_content)
        self.assertIn("launchctl load", install_content)

        # Test uninstall script
        uninstall_script = os.path.join(self.script_dir, "uninstall-macos-service.sh")
        with open(uninstall_script, "r", encoding="utf-8") as f:
            uninstall_content = f.read()

        self.assertIn("launchctl", uninstall_content)
        self.assertIn("launchctl unload", uninstall_content)

    def test_error_recovery(self):
        """Test that scripts handle common error conditions."""
        script_path = os.path.join(self.script_dir, "install.sh")

        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for fallback mechanisms
        self.assertIn("git clone", content)  # Fallback if curl fails
        self.assertIn("wget", content)  # Alternative to curl

    def test_user_feedback(self):
        """Test that scripts provide good user feedback."""
        scripts = [
            "install-macos-service.sh",
            "install.sh",
            "uninstall-macos-service.sh",
        ]

        for script_name in scripts:
            script_path = os.path.join(self.script_dir, script_name)
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for status indicators
            self.assertIn("✅", content)  # Success indicators

            # Check for informative echo statements
            echo_count = content.count("echo")
            self.assertGreater(
                echo_count,
                5,
                f"{script_name} should have multiple echo statements for user feedback",
            )


if __name__ == "__main__":
    unittest.main()
