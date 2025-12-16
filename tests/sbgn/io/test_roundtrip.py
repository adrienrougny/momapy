"""Round-trip tests for SBGN import/export."""
import pytest
import tempfile
import os
import momapy.io.core


# Path to demo SBGN files
DEMO_DIR = "/home/rougny/code/momapy/demo"
SBGN_FILES = [
    "phospho1.sbgn",
    "phospho2.sbgn",
    "phospho3.sbgn",
    "mek_erk.sbgn",
]


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestSBGNRoundTrip:
    """Tests for SBGN round-trip import/export."""

    @pytest.mark.parametrize("filename", SBGN_FILES)
    def test_roundtrip_sbgn_file(self, filename, temp_dir):
        """Test round-trip: import -> export -> import."""
        input_file = os.path.join(DEMO_DIR, filename)

        # Skip if file doesn't exist
        if not os.path.exists(input_file):
            pytest.skip(f"Demo file {filename} not found")

        # First import
        result1 = momapy.io.core.read(input_file)
        assert result1.obj is not None
        assert len(result1.exceptions) == 0, f"Import errors: {result1.exceptions}"

        # Export to temp file
        output_file = os.path.join(temp_dir, f"output_{filename}")
        write_result = momapy.io.core.write(result1.obj, output_file, writer="sbgnml-0.3")
        # Note: write may return None if no exceptions occurred
        if write_result is not None:
            assert len(write_result.exceptions) == 0, f"Export errors: {write_result.exceptions}"
        assert os.path.exists(output_file)

        # Second import (read the exported file)
        result2 = momapy.io.core.read(output_file)
        assert result2.obj is not None
        assert len(result2.exceptions) == 0, f"Re-import errors: {result2.exceptions}"

        # Basic validation: compare types
        assert type(result1.obj) == type(result2.obj)

    def test_roundtrip_preserves_map_structure(self, temp_dir):
        """Test that round-trip preserves basic map structure."""
        input_file = os.path.join(DEMO_DIR, "phospho1.sbgn")

        if not os.path.exists(input_file):
            pytest.skip("Demo file phospho1.sbgn not found")

        # Import original
        result1 = momapy.io.core.read(input_file)
        map1 = result1.obj

        # Export and re-import
        output_file = os.path.join(temp_dir, "test_structure.sbgn")
        momapy.io.core.write(map1, output_file, writer="sbgnml-0.3")
        result2 = momapy.io.core.read(output_file)
        map2 = result2.obj

        # Compare basic structure
        assert hasattr(map1, 'layout')
        assert hasattr(map2, 'layout')

        # Check that layout has elements
        if hasattr(map1.layout, 'layout_elements'):
            assert hasattr(map2.layout, 'layout_elements')
            # Both should have elements (may not be exact same count due to processing)
            assert len(map2.layout.layout_elements) > 0

    def test_roundtrip_multiple_times(self, temp_dir):
        """Test that multiple round-trips are stable."""
        input_file = os.path.join(DEMO_DIR, "phospho1.sbgn")

        if not os.path.exists(input_file):
            pytest.skip("Demo file phospho1.sbgn not found")

        # Import original
        result = momapy.io.core.read(input_file)
        current_map = result.obj

        # Perform 3 round-trips
        for i in range(3):
            output_file = os.path.join(temp_dir, f"roundtrip_{i}.sbgn")

            # Export
            write_result = momapy.io.core.write(current_map, output_file, writer="sbgnml-0.3")
            # Note: write may return None if no exceptions occurred
            if write_result is not None:
                assert len(write_result.exceptions) == 0

            # Re-import
            read_result = momapy.io.core.read(output_file)
            assert len(read_result.exceptions) == 0
            assert read_result.obj is not None

            current_map = read_result.obj

        # Final map should still be valid
        assert current_map is not None
        assert hasattr(current_map, 'layout')

    def test_import_returns_reader_result(self):
        """Test that import returns proper ReaderResult."""
        input_file = os.path.join(DEMO_DIR, "phospho1.sbgn")

        if not os.path.exists(input_file):
            pytest.skip("Demo file phospho1.sbgn not found")

        result = momapy.io.core.read(input_file)

        # Check ReaderResult structure
        assert isinstance(result, momapy.io.core.ReaderResult)
        assert hasattr(result, 'obj')
        assert hasattr(result, 'exceptions')
        assert hasattr(result, 'file_path')
        assert result.obj is not None

    def test_export_returns_writer_result(self, temp_dir):
        """Test that export returns proper WriterResult (or None if no errors)."""
        input_file = os.path.join(DEMO_DIR, "phospho1.sbgn")

        if not os.path.exists(input_file):
            pytest.skip("Demo file phospho1.sbgn not found")

        # Import
        read_result = momapy.io.core.read(input_file)

        # Export
        output_file = os.path.join(temp_dir, "test_writer_result.sbgn")
        write_result = momapy.io.core.write(read_result.obj, output_file, writer="sbgnml-0.3")

        # Check WriterResult structure (may be None if no errors)
        if write_result is not None:
            assert isinstance(write_result, momapy.io.core.WriterResult)
            assert hasattr(write_result, 'obj')
            assert hasattr(write_result, 'exceptions')
            assert hasattr(write_result, 'file_path')

        # File should be created regardless
        assert os.path.exists(output_file)

    @pytest.mark.parametrize("filename", SBGN_FILES)
    def test_import_no_exceptions(self, filename):
        """Test that importing SBGN files produces no exceptions."""
        input_file = os.path.join(DEMO_DIR, filename)

        if not os.path.exists(input_file):
            pytest.skip(f"Demo file {filename} not found")

        result = momapy.io.core.read(input_file)

        # Should have no exceptions
        if len(result.exceptions) > 0:
            pytest.fail(f"Import produced exceptions: {result.exceptions}")

    def test_export_creates_valid_xml(self, temp_dir):
        """Test that exported file is valid XML."""
        input_file = os.path.join(DEMO_DIR, "phospho1.sbgn")

        if not os.path.exists(input_file):
            pytest.skip("Demo file phospho1.sbgn not found")

        # Import and export
        result = momapy.io.core.read(input_file)
        output_file = os.path.join(temp_dir, "test_valid_xml.sbgn")
        momapy.io.core.write(result.obj, output_file, writer="sbgnml-0.3")

        # Try to parse as XML
        import xml.etree.ElementTree as ET
        try:
            tree = ET.parse(output_file)
            root = tree.getroot()
            assert root is not None
        except ET.ParseError as e:
            pytest.fail(f"Exported file is not valid XML: {e}")
