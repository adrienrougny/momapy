"""Shared fixtures for rendering tests."""
import pytest
import tempfile
import os
import momapy.io.core


# Get the directory containing this conftest file
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SBGN_MAPS_DIR = os.path.join(TEST_DIR, "..", "sbgn", "maps", "pd")


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


@pytest.fixture
def sample_map():
    """Load a sample SBGN map for rendering tests."""
    if not SBGN_FILES:
        pytest.skip("No SBGN files found for testing")
    # Use the first available SBGN file
    input_file = os.path.join(SBGN_MAPS_DIR, SBGN_FILES[0])
    result = momapy.io.core.read(input_file)
    return result.obj
