"""Reader output is pinned to the public default font-size constants.

These guard the single-source-of-truth contract: the font sizes the SBGN-ML
reader injects into labels must equal the public constants exposed on
``momapy.sbgn`` (so code building maps programmatically reproduces the look).
"""

import os

import momapy.io.core
import momapy.sbgn
from momapy.sbgn.pd import MacromoleculeLayout
from momapy.sbgn.pd import StateVariableLayout
from momapy.sbgn.pd import UnitOfInformationLayout


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_FILE = os.path.join(TEST_DIR, "..", "maps", "pd", "mapk_cascade.sbgn")

_AUXILIARY_UNIT_LAYOUTS = (StateVariableLayout, UnitOfInformationLayout)


def _walk(elements):
    """Yield every layout element reachable from ``elements`` (depth-first)."""
    for element in elements:
        yield element
        yield from _walk(element.children())


class TestSBGNDefaultFontSizes:
    """The reader's label font sizes match the public constants."""

    def _layout_elements(self):
        result = momapy.io.core.read(MAP_FILE)
        return list(_walk(result.obj.layout.layout_elements))

    def test_auxiliary_unit_font_size(self):
        """State variable / unit-of-information labels use the aux-unit size."""
        checked = 0
        for element in self._layout_elements():
            if (
                isinstance(element, _AUXILIARY_UNIT_LAYOUTS)
                and element.label is not None
            ):
                assert (
                    element.label.font_size
                    == momapy.sbgn.DEFAULT_AUXILIARY_UNIT_FONT_SIZE
                )
                checked += 1
        assert checked > 0, "no labelled auxiliary unit found in the fixture"

    def test_entity_pool_font_size(self):
        """Macromolecule (entity pool) labels use the general glyph size."""
        checked = 0
        for element in self._layout_elements():
            if isinstance(element, MacromoleculeLayout) and element.label is not None:
                assert element.label.font_size == momapy.sbgn.DEFAULT_FONT_SIZE
                checked += 1
        assert checked > 0, "no labelled macromolecule found in the fixture"
