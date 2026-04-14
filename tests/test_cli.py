"""Tests for momapy CLI module."""

import os
import pathlib
import tempfile
from unittest import mock

import pytest

import momapy.cli


class TestCLIArgumentParsing:
    """Tests for CLI argument parsing."""

    def test_cli_main_with_help(self):
        """Test CLI main with --help shows help."""
        with mock.patch("sys.argv", ["momapy", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                momapy.cli.main()
            # argparse exits with 0 for --help
            assert exc_info.value.code == 0

    def test_cli_render_subcommand_help(self):
        """Test render subcommand shows help."""
        with mock.patch("sys.argv", ["momapy", "render", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                momapy.cli.main()
            assert exc_info.value.code == 0


class TestCLIRenderCommand:
    """Tests for CLI render command."""

    def test_render_with_missing_input_file(self):
        """Test render with non-existent input file."""
        with mock.patch(
            "sys.argv",
            [
                "momapy",
                "render",
                "--input",
                "/nonexistent/file.sbgn",
                "--output",
                "/tmp/output.svg",
            ],
        ):
            with pytest.raises((SystemExit, FileNotFoundError)):
                momapy.cli.main()

    def test_render_with_unsupported_format(self, tmp_path):
        """Test render with unsupported format."""
        # Create a dummy input file
        input_file = tmp_path / "test.sbgn"
        input_file.write_text("<sbgn></sbgn>")
        output_file = tmp_path / "output.unsupported"

        with mock.patch(
            "sys.argv",
            [
                "momapy",
                "render",
                "--input",
                str(input_file),
                "--output",
                str(output_file),
            ],
        ):
            # Should raise an error for unsupported format
            with pytest.raises((SystemExit, ValueError, Exception)):
                momapy.cli.main()


class TestCLIListCommand:
    """Tests for CLI list command."""

    def test_list_subcommand_help(self):
        """Test list subcommand shows help."""
        with mock.patch("sys.argv", ["momapy", "list", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                momapy.cli.main()
            assert exc_info.value.code == 0

    def test_list_readers(self, capsys):
        """Test listing available readers."""
        with mock.patch("sys.argv", ["momapy", "list", "readers"]):
            momapy.cli.main()
        captured = capsys.readouterr()
        assert "sbgnml" in captured.out
        assert "celldesigner" in captured.out

    def test_list_writers(self, capsys):
        """Test listing available writers."""
        with mock.patch("sys.argv", ["momapy", "list", "writers"]):
            momapy.cli.main()
        captured = capsys.readouterr()
        assert "sbgnml" in captured.out

    def test_list_renderers(self, capsys):
        """Test listing available renderers."""
        with mock.patch("sys.argv", ["momapy", "list", "renderers"]):
            momapy.cli.main()
        captured = capsys.readouterr()
        assert "svg-native" in captured.out

    def test_list_invalid_plugin_type(self):
        """Test list with invalid plugin type."""
        with mock.patch("sys.argv", ["momapy", "list", "invalid"]):
            with pytest.raises(SystemExit):
                momapy.cli.main()


class TestCLIMainEntryPoint:
    """Tests for CLI main entry point."""

    def test_cli_module_has_main_function(self):
        """Test that CLI module has a main function."""
        assert hasattr(momapy.cli, "main")
        assert callable(momapy.cli.main)

    def test_cli_module_has_run_function(self):
        """Test that CLI module has a run function."""
        assert hasattr(momapy.cli, "run")
        assert callable(momapy.cli.run)
