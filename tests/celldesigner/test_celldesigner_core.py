"""Tests for momapy.celldesigner.core module."""
import pytest
import os
import momapy.io.core


# Get the directory containing this test file
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
CELLDESIGNER_MAPS_DIR = os.path.join(TEST_DIR, "maps")

# Discover all .xml files in the maps directory
def get_celldesigner_files():
    """Get all CellDesigner XML files from the maps directory."""
    if not os.path.exists(CELLDESIGNER_MAPS_DIR):
        return []
    return [f for f in os.listdir(CELLDESIGNER_MAPS_DIR) if f.endswith('.xml')]

CELLDESIGNER_FILES = get_celldesigner_files()


def test_celldesigner_core_import():
    """Test that celldesigner.core module can be imported."""
    import momapy.celldesigner.core
    assert momapy.celldesigner.core is not None


def test_celldesigner_io_import():
    """Test that celldesigner.io module can be imported."""
    try:
        import momapy.celldesigner.io
        assert momapy.celldesigner.io is not None
    except ImportError:
        # Module might not have __init__.py
        import momapy.celldesigner.io.celldesigner
        assert momapy.celldesigner.io.celldesigner is not None


class TestCellDesignerReading:
    """Tests for reading CellDesigner files."""

    @pytest.mark.parametrize("filename", CELLDESIGNER_FILES)
    def test_read_celldesigner_file(self, filename):
        """Test reading CellDesigner XML files."""
        input_file = os.path.join(CELLDESIGNER_MAPS_DIR, filename)
        if not os.path.exists(input_file):
            pytest.skip(f"CellDesigner file {filename} not found")
        result = momapy.io.core.read(input_file)
        assert result is not None
        assert result.obj is not None
        # Verify we got a map object
        assert hasattr(result.obj, 'layout')
