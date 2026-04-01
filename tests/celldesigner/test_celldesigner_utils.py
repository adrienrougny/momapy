"""Tests for momapy.celldesigner.utils — CellDesigner map utility functions."""

import os

import pytest

import momapy.io.core
import momapy.builder
import momapy.celldesigner.core
import momapy.celldesigner.utils
import momapy.coloring


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
CD_MAPS_DIR = os.path.join(TEST_DIR, "maps")


def _get_cd_files():
    if not os.path.exists(CD_MAPS_DIR):
        return []
    return sorted(f for f in os.listdir(CD_MAPS_DIR) if f.endswith(".xml"))


CD_FILES = _get_cd_files()


@pytest.fixture(scope="session")
def cd_maps():
    """Load all CellDesigner maps once for the entire test session."""
    if not CD_FILES:
        pytest.skip("No CellDesigner test files found")
    maps = {}
    for fname in CD_FILES:
        path = os.path.join(CD_MAPS_DIR, fname)
        result = momapy.io.core.read(path)
        maps[fname] = result.obj
    return maps


@pytest.fixture(params=CD_FILES, ids=CD_FILES)
def cd_map(request, cd_maps):
    """Yield each loaded CellDesigner map in turn (parametrized)."""
    return cd_maps[request.param]


@pytest.fixture
def representative_map(cd_maps):
    """Return a single representative map for non-parametrized tests."""
    return cd_maps[CD_FILES[0]]


# ---------------------------------------------------------------------------
# TestReturnTypes
# ---------------------------------------------------------------------------


class TestReturnTypes:
    """highlight_layout_elements returns the correct type depending on input."""

    def test_returns_cd_map_for_cd_map_input(self, representative_map):
        assert isinstance(
            representative_map, momapy.celldesigner.core.CellDesignerMap
        )
        layout_elements = list(
            representative_map.layout.layout_elements
        )[:1]
        result = momapy.celldesigner.utils.highlight_layout_elements(
            representative_map, layout_elements
        )
        assert isinstance(
            result, momapy.celldesigner.core.CellDesignerMap
        ), "Should return CellDesignerMap when given CellDesignerMap"

    def test_returns_builder_for_builder_input(self, representative_map):
        builder = momapy.builder.builder_from_object(representative_map)
        layout_elements = list(builder.layout.layout_elements)[:1]
        result = momapy.celldesigner.utils.highlight_layout_elements(
            builder, layout_elements
        )
        assert not isinstance(
            result, momapy.celldesigner.core.CellDesignerMap
        ), "Should not return CellDesignerMap when given a builder"
        assert momapy.builder.isinstance_or_builder(
            result, momapy.celldesigner.core.CellDesignerMap
        ), "Should return a builder of CellDesignerMap"


# ---------------------------------------------------------------------------
# TestHighlightLayoutElements
# ---------------------------------------------------------------------------


class TestHighlightLayoutElements:
    """highlight_layout_elements applies correct styling."""

    def test_with_empty_layout_elements(self, representative_map):
        """All elements should be grayed out when no elements are highlighted."""
        result = momapy.celldesigner.utils.highlight_layout_elements(
            representative_map, []
        )
        assert isinstance(
            result, momapy.celldesigner.core.CellDesignerMap
        )


# ---------------------------------------------------------------------------
# TestNonCrash — smoke tests across ALL CellDesigner files
# ---------------------------------------------------------------------------


class TestNonCrash:
    """highlight_layout_elements completes without error on every CD file."""

    def test_highlight_with_first_element(self, cd_map):
        layout_elements = list(cd_map.layout.layout_elements)[:1]
        momapy.celldesigner.utils.highlight_layout_elements(
            cd_map, layout_elements
        )

    def test_highlight_with_no_elements(self, cd_map):
        momapy.celldesigner.utils.highlight_layout_elements(cd_map, [])
