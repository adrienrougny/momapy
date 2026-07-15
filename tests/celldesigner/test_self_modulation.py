"""Regression tests for reading CellDesigner self-modulations.

A self-modulation is an influence whose base reactant and base product are the
same species alias (e.g. a protein that inhibits itself). Its reactant->product
frame is degenerate, so the reader must perturb it the same way the writer does
(``make_non_degenerate_frame``) instead of collapsing every edit point onto the
species center, which would leave the arc with ``None`` segment endpoints.
"""

import os

import momapy.io.core

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_SELF_MODULATION = os.path.join(_TEST_DIR, "fixtures", "self_modulation.xml")


def _self_modulation_arc(map_):
    """Return the single modulation arc (source == target) of the map."""
    for layout_element in map_.layout.layout_elements:
        segments = getattr(layout_element, "segments", None)
        source = getattr(layout_element, "source", None)
        target = getattr(layout_element, "target", None)
        if segments and source is not None and source is target:
            return layout_element
    return None


def test_self_modulation_has_no_none_endpoints():
    """Every segment of the self-modulation arc has real endpoints."""
    map_ = momapy.io.core.read(_SELF_MODULATION).obj
    arc = _self_modulation_arc(map_)
    assert arc is not None
    assert arc.segments
    for segment in arc.segments:
        assert segment.p1 is not None
        assert segment.p2 is not None


def test_self_modulation_bbox_does_not_raise():
    """Computing the layout bbox of a self-modulation map does not crash."""
    map_ = momapy.io.core.read(_SELF_MODULATION).obj
    bbox = map_.layout.bbox()
    assert bbox is not None
