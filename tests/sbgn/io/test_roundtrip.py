"""Round-trip tests for SBGN import/export."""

import pytest
import tempfile
import os
import momapy.io.core


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


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestSBGNRoundTrip:
    """Tests for SBGN round-trip import/export."""

    @pytest.mark.parametrize("filename", SBGN_FILES)
    def test_roundtrip_sbgn_file(self, filename, temp_dir):
        """Test round-trip: import -> export -> import and check equality."""
        input_file = os.path.join(SBGN_MAPS_DIR, filename)
        if not os.path.exists(input_file):
            pytest.skip(f"SBGN file {filename} not found")
        result1 = momapy.io.core.read(input_file)
        map1 = result1.obj
        output_file = os.path.join(temp_dir, f"output_{filename}")
        momapy.io.core.write(map1, output_file, writer="sbgnml-0.3")
        result2 = momapy.io.core.read(output_file)
        map2 = result2.obj
        assert map1 == map2
