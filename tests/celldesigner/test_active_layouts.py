"""Tests for CellDesigner active layout border behaviour.

Active species nodes have a dashed active border added as a child
``layout_element``.  When routing arcs, ``own_border()`` (which only
considers the node's own drawing elements) must be used so that arcs
connect to the inner shape, not the outer dashed border returned by
``border()`` (which includes children).
"""

import math

import pytest

import momapy.builder
import momapy.celldesigner.core
import momapy.coloring
import momapy.geometry

_ACTIVE_XSEP = momapy.celldesigner.core._ACTIVE_XSEP
_ACTIVE_YSEP = momapy.celldesigner.core._ACTIVE_YSEP


def _dist(a, b):
    """Euclidean distance between two Points."""
    return math.hypot(a.x - b.x, a.y - b.y)

# Representative subset of layout / active-layout pairs to test.
_LAYOUT_PAIRS = [
    (
        momapy.celldesigner.core.GenericProteinLayout,
        momapy.celldesigner.core.GenericProteinActiveLayout,
    ),
    (
        momapy.celldesigner.core.SimpleMoleculeLayout,
        momapy.celldesigner.core.SimpleMoleculeActiveLayout,
    ),
    (
        momapy.celldesigner.core.ComplexLayout,
        momapy.celldesigner.core.ComplexActiveLayout,
    ),
    (
        momapy.celldesigner.core.GeneLayout,
        momapy.celldesigner.core.GeneActiveLayout,
    ),
]


def _build_species_with_active_child(layout_cls, active_cls, width=60.0, height=30.0):
    """Build a frozen species node with an active child element.

    Mirrors the logic in ``_layout.make_species`` when ``active=True``.
    """
    position = momapy.geometry.Point(100.0, 100.0)

    node_builder = momapy.builder.new_builder_object(layout_cls)
    node_builder.position = position
    node_builder.width = width
    node_builder.height = height
    node_builder.n = 1

    active_builder = momapy.builder.new_builder_object(active_cls)
    active_builder.position = position
    active_builder.width = width + _ACTIVE_XSEP * 2
    active_builder.height = height + _ACTIVE_YSEP * 2
    active_builder.n = 1

    active_element = momapy.builder.object_from_builder(active_builder)
    node_builder.layout_elements.append(active_element)

    return momapy.builder.object_from_builder(node_builder)


class TestActiveLayoutStructure:
    """Tests that active species nodes are structured correctly."""

    @pytest.mark.parametrize("layout_cls,active_cls", _LAYOUT_PAIRS,
                             ids=[c[0].__name__ for c in _LAYOUT_PAIRS])
    def test_active_child_is_present(self, layout_cls, active_cls):
        """An active species node has exactly one layout_element child
        that is an instance of the active layout class."""
        node = _build_species_with_active_child(layout_cls, active_cls)
        active_children = [
            le for le in node.layout_elements
            if isinstance(le, active_cls)
        ]
        assert len(active_children) == 1

    @pytest.mark.parametrize("layout_cls,active_cls", _LAYOUT_PAIRS,
                             ids=[c[0].__name__ for c in _LAYOUT_PAIRS])
    def test_active_child_dimensions(self, layout_cls, active_cls):
        """The active child is wider/taller by 2 * _ACTIVE_XSEP/YSEP."""
        node = _build_species_with_active_child(layout_cls, active_cls)
        active_child = node.layout_elements[0]
        assert active_child.width == pytest.approx(node.width + _ACTIVE_XSEP * 2)
        assert active_child.height == pytest.approx(node.height + _ACTIVE_YSEP * 2)

    @pytest.mark.parametrize("layout_cls,active_cls", _LAYOUT_PAIRS,
                             ids=[c[0].__name__ for c in _LAYOUT_PAIRS])
    def test_active_child_shares_position(self, layout_cls, active_cls):
        """The active child is centred on the same position as its parent."""
        node = _build_species_with_active_child(layout_cls, active_cls)
        active_child = node.layout_elements[0]
        assert active_child.position == node.position


class TestSelfBorderVsBorder:
    """Tests that ``own_border`` ignores the active child while
    ``border`` includes it."""

    @pytest.mark.parametrize("layout_cls,active_cls", _LAYOUT_PAIRS,
                             ids=[c[0].__name__ for c in _LAYOUT_PAIRS])
    def test_own_border_is_closer_to_center_than_border(self, layout_cls, active_cls):
        """``own_border()`` should return a point on the inner shape
        (closer to center) while ``border()`` returns a point on the
        outer active border (farther from center)."""
        node = _build_species_with_active_child(layout_cls, active_cls)
        # A point far to the right — the border intersection should lie
        # between center and this point.
        far_point = momapy.geometry.Point(300.0, 100.0)

        own_border_pt = node.own_border(far_point)
        border_pt = node.border(far_point)

        center = node.center()
        dist_self = _dist(center,own_border_pt)
        dist_full = _dist(center,border_pt)

        # The outer (full) border must be strictly farther out
        assert dist_full > dist_self

    @pytest.mark.parametrize("layout_cls,active_cls", _LAYOUT_PAIRS,
                             ids=[c[0].__name__ for c in _LAYOUT_PAIRS])
    def test_own_border_matches_node_without_active_child(self, layout_cls, active_cls):
        """``own_border()`` on a node with an active child should give
        the same result as ``border()`` on the same node without one."""
        position = momapy.geometry.Point(100.0, 100.0)
        width, height = 60.0, 30.0

        # Node with active child
        node_active = _build_species_with_active_child(
            layout_cls, active_cls, width=width, height=height
        )

        # Identical node without active child
        builder = momapy.builder.new_builder_object(layout_cls)
        builder.position = position
        builder.width = width
        builder.height = height
        builder.n = 1
        node_plain = momapy.builder.object_from_builder(builder)

        far_point = momapy.geometry.Point(300.0, 100.0)

        own_border_pt = node_active.own_border(far_point)
        plain_border_pt = node_plain.border(far_point)

        assert own_border_pt.x == pytest.approx(plain_border_pt.x, abs=1e-6)
        assert own_border_pt.y == pytest.approx(plain_border_pt.y, abs=1e-6)

    @pytest.mark.parametrize("layout_cls,active_cls", _LAYOUT_PAIRS,
                             ids=[c[0].__name__ for c in _LAYOUT_PAIRS])
    def test_own_border_from_multiple_directions(self, layout_cls, active_cls):
        """``own_border()`` is strictly inside ``border()`` from several
        approach angles."""
        node = _build_species_with_active_child(layout_cls, active_cls)
        center = node.center()

        far_points = [
            momapy.geometry.Point(300.0, 100.0),   # right
            momapy.geometry.Point(-100.0, 100.0),   # left
            momapy.geometry.Point(100.0, 300.0),    # below
            momapy.geometry.Point(100.0, -100.0),   # above
        ]

        for far_point in far_points:
            own_border_pt = node.own_border(far_point)
            border_pt = node.border(far_point)

            dist_self = _dist(center,own_border_pt)
            dist_full = _dist(center,border_pt)

            assert dist_full > dist_self, (
                f"border() should be farther than own_border() "
                f"for far_point={far_point}"
            )


class TestNodeWithoutActiveChild:
    """When there is no active child, ``own_border`` and ``border``
    should agree (aside from the label, which produces no border
    geometry)."""

    @pytest.mark.parametrize("layout_cls,active_cls", _LAYOUT_PAIRS,
                             ids=[c[0].__name__ for c in _LAYOUT_PAIRS])
    def test_own_border_equals_border_without_active(self, layout_cls, active_cls):
        """For a plain (non-active) node, ``own_border`` ≈ ``border``."""
        builder = momapy.builder.new_builder_object(layout_cls)
        builder.position = momapy.geometry.Point(100.0, 100.0)
        builder.width = 60.0
        builder.height = 30.0
        builder.n = 1
        node = momapy.builder.object_from_builder(builder)

        far_point = momapy.geometry.Point(300.0, 100.0)

        own_border_pt = node.own_border(far_point)
        border_pt = node.border(far_point)

        assert own_border_pt.x == pytest.approx(border_pt.x, abs=1e-6)
        assert own_border_pt.y == pytest.approx(border_pt.y, abs=1e-6)
