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
        """Test round-trip: import -> export -> import and check equality."""
        input_file = os.path.join(DEMO_DIR, filename)

        # Skip if file doesn't exist
        if not os.path.exists(input_file):
            pytest.skip(f"Demo file {filename} not found")

        # First import
        result1 = momapy.io.core.read(input_file)
        map1 = result1.obj
        assert map1 is not None

        # Export to temp file
        output_file = os.path.join(temp_dir, f"output_{filename}")
        momapy.io.core.write(map1, output_file, writer="sbgnml-0.3")

        # Second import (read the exported file)
        result2 = momapy.io.core.read(output_file)
        map2 = result2.obj
        assert map2 is not None

        # Test equality
        assert map1 == map2
