"""Shared pytest fixtures for momapy tests."""
import pytest
import momapy.geometry
import momapy.coloring
import momapy.core
import momapy.drawing


@pytest.fixture
def sample_point():
    """Create a sample Point for testing."""
    return momapy.geometry.Point(10.0, 20.0)


@pytest.fixture
def sample_bbox():
    """Create a sample BBox for testing."""
    return momapy.geometry.BBox(
        momapy.geometry.Point(0.0, 0.0),
        width=100.0,
        height=50.0
    )


@pytest.fixture
def sample_color():
    """Create a sample color for testing."""
    return momapy.coloring.black


@pytest.fixture
def sample_layout():
    """Create a simple Layout for testing."""
    return momapy.core.Layout(
        position=momapy.geometry.Point(0, 0),
        width=200,
        height=200,
        layout_elements=[]
    )
