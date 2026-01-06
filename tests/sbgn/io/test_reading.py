"""Tests for SBGN reading functionality."""

import pytest
import os
import momapy.io.core
import momapy.sbgn.core
import frozendict


# Get the directory containing this test file
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SBGN_MAPS_DIR = os.path.join(TEST_DIR, "..", "maps", "pd")

# Discover all .sbgn files in the maps directory
def get_sbgn_files():
    """Get all SBGN files from the maps directory."""
    if not os.path.exists(SBGN_MAPS_DIR):
        return []
    return [f for f in os.listdir(SBGN_MAPS_DIR) if f.endswith('.sbgn')]

SBGN_FILES = get_sbgn_files()


class TestSBGNReadOptionalParameters:
    """Tests for SBGN read function optional parameters."""

    @pytest.fixture
    def test_file(self):
        """Return path to a test SBGN file."""
        if not SBGN_FILES:
            pytest.skip("No SBGN test files found")
        return os.path.join(SBGN_MAPS_DIR, SBGN_FILES[0])

    @pytest.mark.parametrize("return_type,expected_type", [
        ("map", momapy.sbgn.core.SBGNMap),
        ("model", momapy.sbgn.core.SBGNModel),
        ("layout", momapy.core.Layout),
    ])
    def test_return_type_parameter(self, test_file, return_type, expected_type):
        """Test return_type parameter returns correct object type."""
        result = momapy.io.core.read(test_file, return_type=return_type)
        assert isinstance(result.obj, expected_type)

    def test_with_model_true(self, test_file):
        """Test with_model=True includes model in result."""
        result = momapy.io.core.read(test_file, return_type="map", with_model=True)
        assert result.obj is not None
        assert isinstance(result.obj, momapy.sbgn.core.SBGNMap)
        # Verify the map has a model
        assert hasattr(result.obj, 'model')
        assert result.obj.model is not None

    def test_with_model_false(self, test_file):
        """Test with_model=False excludes model from result."""
        result = momapy.io.core.read(test_file, return_type="map", with_model=False)
        assert result.obj is not None
        assert isinstance(result.obj, momapy.sbgn.core.SBGNMap)
        # Verify the map has no model (or model is None)
        assert hasattr(result.obj, 'model')
        assert result.obj.model is None

    def test_with_layout_true(self, test_file):
        """Test with_layout=True includes layout in result."""
        result = momapy.io.core.read(test_file, return_type="map", with_layout=True)
        assert result.obj is not None
        assert isinstance(result.obj, momapy.sbgn.core.SBGNMap)
        # Verify the map has a layout
        assert hasattr(result.obj, 'layout')
        assert result.obj.layout is not None

    def test_with_layout_false(self, test_file):
        """Test with_layout=False excludes layout from result."""
        result = momapy.io.core.read(test_file, return_type="map", with_layout=False)
        assert result.obj is not None
        assert isinstance(result.obj, momapy.sbgn.core.SBGNMap)
        # Verify the map has no layout (or layout is None)
        assert hasattr(result.obj, 'layout')
        assert result.obj.layout is None

    def test_with_annotations_true(self, test_file):
        """Test with_annotations=True includes annotations in result."""
        result = momapy.io.core.read(test_file, with_annotations=True)
        assert hasattr(result, 'annotations')
        assert isinstance(result.annotations, frozendict.frozendict)
        # Annotations may be empty if file has none, but should be a frozendict

    def test_with_annotations_false(self, test_file):
        """Test with_annotations=False excludes annotations from result."""
        result = momapy.io.core.read(test_file, with_annotations=False)
        assert hasattr(result, 'annotations')
        # Should be empty frozendict when with_annotations=False
        assert result.annotations == frozendict.frozendict()

    def test_with_notes_true(self, test_file):
        """Test with_notes=True includes notes in result."""
        result = momapy.io.core.read(test_file, with_notes=True)
        assert hasattr(result, 'notes')
        assert isinstance(result.notes, frozendict.frozendict)
        # Notes may be empty if file has none, but should be a frozendict

    def test_with_notes_false(self, test_file):
        """Test with_notes=False excludes notes from result."""
        result = momapy.io.core.read(test_file, with_notes=False)
        assert hasattr(result, 'notes')
        # Should be empty frozendict when with_notes=False
        assert result.notes == frozendict.frozendict()
