"""Shared pytest fixtures for momapy tests."""

import pytest
import momapy.geometry
import momapy.coloring
import momapy.core
import momapy.core.layout
import momapy.drawing


@pytest.fixture
def sample_point():
    """Create a sample Point for testing."""
    return momapy.geometry.Point(10.0, 20.0)


@pytest.fixture
def sample_bbox():
    """Create a sample BBox for testing."""
    return momapy.geometry.Bbox(
        momapy.geometry.Point(0.0, 0.0), width=100.0, height=50.0
    )


@pytest.fixture
def sample_color():
    """Create a sample color for testing."""
    return momapy.coloring.black


@pytest.fixture
def sample_layout():
    """Create a simple Layout for testing."""
    return momapy.core.layout.Layout(
        position=momapy.geometry.Point(0, 0), width=200, height=200, layout_elements=[]
    )


@pytest.fixture
def sample_node():
    """Create a sample Rectangle node for testing."""
    import momapy.meta.nodes

    return momapy.meta.nodes.Rectangle(
        position=momapy.geometry.Point(50.0, 50.0), width=100.0, height=60.0
    )


@pytest.fixture
def sample_path():
    """Create a sample Path with common actions for testing."""
    return momapy.drawing.Path(
        actions=(
            momapy.drawing.MoveTo(momapy.geometry.Point(0, 0)),
            momapy.drawing.LineTo(momapy.geometry.Point(10, 0)),
            momapy.drawing.LineTo(momapy.geometry.Point(10, 10)),
            momapy.drawing.LineTo(momapy.geometry.Point(0, 10)),
            momapy.drawing.ClosePath(),
        )
    )


@pytest.fixture(scope="session")
def sample_sbgn_map():
    """Load a sample SBGN map for testing (session-scoped to avoid repeated I/O)."""
    import momapy.io
    import pathlib

    # Find a test SBGN file
    test_dir = pathlib.Path(__file__).parent
    sbgn_test_files = list(test_dir.glob("sbgn/io/test_files/*.sbgn"))

    if sbgn_test_files:
        return momapy.io.core.read(sbgn_test_files[0])
    else:
        # Return None if no test files found, tests should skip
        return None
