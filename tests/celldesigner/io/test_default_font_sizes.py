"""Reader output is pinned to the public default font-size constants.

These guard the single-source-of-truth contract: the font sizes the CellDesigner
reader injects into the labels it generates itself (compartment names,
modifications, structural states) must equal the public constants exposed on
``momapy.celldesigner``. Species labels are excluded on purpose: their font size
is taken from the CellDesigner file, not from a momapy default.
"""

import os

import pytest

import momapy.io.core
import momapy.celldesigner
from momapy.celldesigner.layout import CornerCompartmentLayout
from momapy.celldesigner.layout import LineCompartmentLayout
from momapy.celldesigner.layout import ModificationLayout
from momapy.celldesigner.layout import OvalCompartmentLayout
from momapy.celldesigner.layout import RectangleCompartmentLayout
from momapy.celldesigner.layout import StructuralStateLayout


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
MAPS_DIR = os.path.join(TEST_DIR, "..", "maps")

_MODIFICATION_LAYOUTS = (ModificationLayout, StructuralStateLayout)
_COMPARTMENT_LAYOUTS = (
    OvalCompartmentLayout,
    RectangleCompartmentLayout,
    CornerCompartmentLayout,
    LineCompartmentLayout,
)


def _map_files():
    if not os.path.exists(MAPS_DIR):
        return []
    return [f for f in os.listdir(MAPS_DIR) if f.endswith(".xml")]


def _walk(elements):
    """Yield every layout element reachable from ``elements`` (depth-first)."""
    for element in elements:
        yield element
        yield from _walk(element.children())


def _all_layout_elements():
    for filename in _map_files():
        result = momapy.io.core.read(os.path.join(MAPS_DIR, filename))
        yield from _walk(result.obj.layout.layout_elements)


class TestCellDesignerDefaultFontSizes:
    """The reader's generated-label font sizes match the public constants."""

    def test_modification_font_size(self):
        """Modification / structural-state labels use the modification size."""
        checked = 0
        for element in _all_layout_elements():
            if isinstance(element, _MODIFICATION_LAYOUTS) and element.label is not None:
                assert (
                    element.label.font_size
                    == momapy.celldesigner.DEFAULT_MODIFICATION_FONT_SIZE
                )
                checked += 1
        if checked == 0:
            pytest.skip("no labelled modification/structural state in the fixtures")

    def test_compartment_font_size(self):
        """Compartment name labels use the general font size."""
        checked = 0
        for element in _all_layout_elements():
            if isinstance(element, _COMPARTMENT_LAYOUTS) and element.label is not None:
                assert element.label.font_size == momapy.celldesigner.DEFAULT_FONT_SIZE
                checked += 1
        if checked == 0:
            pytest.skip("no labelled compartment in the fixtures")
