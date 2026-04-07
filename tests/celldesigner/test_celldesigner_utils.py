"""Tests for momapy.celldesigner.utils — CellDesigner map utility functions."""

import os

import pytest

import momapy.io.core
import momapy.builder
import momapy.celldesigner.core
import momapy.celldesigner.utils
import momapy.coloring
import momapy.core.layout


ALL_UTILS_FUNCTIONS = [
    "highlight_layout_elements",
    "set_layout_to_fit_content",
    "set_nodes_to_fit_labels",
    "set_compartments_to_fit_content",
    "set_complexes_to_fit_content",
    "set_modifications_to_borders",
    "set_modifications_label_font_size",
    "set_arcs_to_borders",
    "tidy",
]


def _call_function(func_name, map_):
    """Call a utils function by name with appropriate arguments."""
    func = getattr(momapy.celldesigner.utils, func_name)
    if func_name == "highlight_layout_elements":
        layout_elements = list(map_.layout.layout_elements)[:1]
        return func(map_, layout_elements)
    elif func_name == "set_modifications_label_font_size":
        return func(map_, 10.0)
    else:
        return func(map_)


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
    """Utils functions return the correct type depending on input."""

    @pytest.mark.parametrize("func_name", ALL_UTILS_FUNCTIONS)
    def test_returns_cd_map_for_cd_map_input(
        self, representative_map, func_name
    ):
        result = _call_function(func_name, representative_map)
        assert isinstance(
            result, momapy.celldesigner.core.CellDesignerMap
        ), f"{func_name} should return CellDesignerMap when given CellDesignerMap"

    @pytest.mark.parametrize("func_name", ALL_UTILS_FUNCTIONS)
    def test_returns_builder_for_builder_input(
        self, representative_map, func_name
    ):
        builder = momapy.builder.builder_from_object(representative_map)
        result = _call_function(func_name, builder)
        assert not isinstance(
            result, momapy.celldesigner.core.CellDesignerMap
        ), f"{func_name} should not return CellDesignerMap when given a builder"
        assert momapy.builder.isinstance_or_builder(
            result, momapy.celldesigner.core.CellDesignerMap
        ), f"{func_name} should return a builder of CellDesignerMap"


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


class TestSetNodesToFitLabels:
    """set_nodes_to_fit_labels adjusts node dimensions."""

    def test_with_exclude(self, representative_map):
        result = momapy.celldesigner.utils.set_nodes_to_fit_labels(
            representative_map,
            exclude=[momapy.celldesigner.core.ComplexLayout],
        )
        assert isinstance(
            result, momapy.celldesigner.core.CellDesignerMap
        )

    def test_with_restrict_to(self, representative_map):
        result = momapy.celldesigner.utils.set_nodes_to_fit_labels(
            representative_map,
            restrict_to=[momapy.celldesigner.core.ModificationLayout],
        )
        assert isinstance(
            result, momapy.celldesigner.core.CellDesignerMap
        )

    def test_omit_both_returns_early(self, representative_map):
        builder = momapy.builder.builder_from_object(representative_map)
        result = momapy.celldesigner.utils.set_nodes_to_fit_labels(
            builder, omit_width=True, omit_height=True
        )
        assert result is builder


class TestSetModificationsLabelFontSize:
    """set_modifications_label_font_size applies font size."""

    def test_sets_font_size(self, representative_map):
        builder = momapy.builder.builder_from_object(representative_map)
        momapy.celldesigner.utils.set_modifications_label_font_size(
            builder, 8.0
        )
        for layout_element in builder.layout.descendants():
            if momapy.builder.isinstance_or_builder(
                layout_element,
                (
                    momapy.celldesigner.core.ModificationLayout,
                    momapy.celldesigner.core.StructuralStateLayout,
                ),
            ):
                if layout_element.label is not None:
                    assert layout_element.label.font_size == 8.0


class TestSetLayoutToFitContent:
    """set_layout_to_fit_content resizes the layout."""

    def test_with_padding(self, representative_map):
        result = momapy.celldesigner.utils.set_layout_to_fit_content(
            representative_map, xsep=20, ysep=20
        )
        assert isinstance(
            result, momapy.celldesigner.core.CellDesignerMap
        )


class TestTidy:
    """tidy applies all layout optimizations."""

    def test_with_custom_parameters(self, representative_map):
        result = momapy.celldesigner.utils.tidy(
            representative_map,
            nodes_xsep=5,
            nodes_ysep=5,
            complexes_xsep=10,
            complexes_ysep=10,
            compartments_xsep=10,
            compartments_ysep=10,
        )
        assert isinstance(
            result, momapy.celldesigner.core.CellDesignerMap
        )


# ---------------------------------------------------------------------------
# TestNonCrash — smoke tests across ALL CellDesigner files
# ---------------------------------------------------------------------------


class TestNonCrash:
    """All utils functions complete without error on every CD file."""

    def test_highlight_with_first_element(self, cd_map):
        layout_elements = list(cd_map.layout.layout_elements)[:1]
        momapy.celldesigner.utils.highlight_layout_elements(
            cd_map, layout_elements
        )

    def test_highlight_with_no_elements(self, cd_map):
        momapy.celldesigner.utils.highlight_layout_elements(cd_map, [])

    def test_set_layout_to_fit_content(self, cd_map):
        momapy.celldesigner.utils.set_layout_to_fit_content(cd_map)

    def test_set_nodes_to_fit_labels(self, cd_map):
        momapy.celldesigner.utils.set_nodes_to_fit_labels(cd_map)

    def test_set_compartments_to_fit_content(self, cd_map):
        momapy.celldesigner.utils.set_compartments_to_fit_content(cd_map)

    def test_set_complexes_to_fit_content(self, cd_map):
        momapy.celldesigner.utils.set_complexes_to_fit_content(cd_map)

    def test_set_modifications_to_borders(self, cd_map):
        momapy.celldesigner.utils.set_modifications_to_borders(cd_map)

    def test_set_modifications_label_font_size(self, cd_map):
        momapy.celldesigner.utils.set_modifications_label_font_size(
            cd_map, 10.0
        )

    def test_set_arcs_to_borders(self, cd_map):
        momapy.celldesigner.utils.set_arcs_to_borders(cd_map)

    def test_tidy(self, cd_map):
        momapy.celldesigner.utils.tidy(cd_map)
