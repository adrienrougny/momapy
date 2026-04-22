"""Tests for momapy CLI module."""

import json
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


class TestCLIInfoCommand:
    """Tests for CLI info command."""

    SBGN_MAP_PATH = os.path.join(
        os.path.dirname(__file__),
        "sbgn",
        "maps",
        "pd",
        "glycolysis.sbgn",
    )

    def test_info_subcommand_help(self):
        """Test info subcommand shows help."""
        with mock.patch("sys.argv", ["momapy", "info", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                momapy.cli.main()
            assert exc_info.value.code == 0

    def test_info_text_output(self, capsys):
        """Test info command text output."""
        with mock.patch("sys.argv", ["momapy", "info", self.SBGN_MAP_PATH]):
            momapy.cli.main()
        captured = capsys.readouterr()
        assert "SBGN Process Description" in captured.out
        assert "entity pools:" in captured.out
        assert "dimensions:" in captured.out

    def test_info_json_output(self, capsys):
        """Test info command JSON output."""
        with mock.patch(
            "sys.argv",
            ["momapy", "info", self.SBGN_MAP_PATH, "--format", "json"],
        ):
            momapy.cli.main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["map_type"] == "SBGN Process Description"
        assert "model" in data
        assert "layout" in data
        assert "entity_pools" in data["model"]
        assert "width" in data["layout"]

    def test_info_output_to_file(self, tmp_path):
        """Test info command writes to file when -o is given."""
        output_file = tmp_path / "info.txt"
        with mock.patch(
            "sys.argv",
            ["momapy", "info", self.SBGN_MAP_PATH, "-o", str(output_file)],
        ):
            momapy.cli.main()
        content = output_file.read_text()
        assert "SBGN Process Description" in content
        assert "entity pools:" in content


class TestCLIExportCommand:
    """Tests for CLI export command."""

    SBGN_MAP_PATH = os.path.join(
        os.path.dirname(__file__),
        "sbgn",
        "maps",
        "pd",
        "glycolysis.sbgn",
    )

    def test_export_to_stdout(self, capsys):
        """Test export command outputs XML to stdout when stdout is a TTY."""
        with (
            mock.patch("sys.argv", ["momapy", "export", self.SBGN_MAP_PATH]),
            mock.patch("sys.stdout.isatty", return_value=True),
        ):
            momapy.cli.main()
        captured = capsys.readouterr()
        assert "<?xml" in captured.out
        assert "<sbgn" in captured.out

    def test_export_to_file(self, tmp_path):
        """Test export command writes to file when -o is given."""
        output_file = tmp_path / "output.sbgn"
        with mock.patch(
            "sys.argv",
            ["momapy", "export", self.SBGN_MAP_PATH, "-o", str(output_file)],
        ):
            momapy.cli.main()
        content = output_file.read_text()
        assert "<?xml" in content
        assert "<sbgn" in content


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
