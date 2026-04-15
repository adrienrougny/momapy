"""Round-trip tests for CellDesigner import/export."""

import pytest
import tempfile
import os
import momapy.io.core

pytestmark = pytest.mark.slow


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
CD_MAPS_DIR = os.path.join(TEST_DIR, "..", "maps")


def get_cd_files():
    """Get all CellDesigner XML files from the maps directory."""
    if not os.path.exists(CD_MAPS_DIR):
        return []
    return [f for f in os.listdir(CD_MAPS_DIR) if f.endswith(".xml")]


CD_FILES = get_cd_files()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestCellDesignerRoundTrip:
    """Tests for CellDesigner round-trip import/export."""

    @pytest.mark.parametrize("filename", CD_FILES)
    def test_roundtrip_cd_file(self, filename, temp_dir):
        """Test round-trip: import -> export -> import and check model equality."""
        input_file = os.path.join(CD_MAPS_DIR, filename)
        if not os.path.exists(input_file):
            pytest.skip(f"CellDesigner file {filename} not found")
        result1 = momapy.io.core.read(input_file)
        map1 = result1.obj
        output_file = os.path.join(temp_dir, f"output_{filename}")
        momapy.io.core.write(map1, output_file, writer="celldesigner")
        result2 = momapy.io.core.read(output_file)
        map2 = result2.obj
        assert map1.model == map2.model
