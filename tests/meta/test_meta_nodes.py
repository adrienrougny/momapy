"""Tests for momapy.meta.nodes module."""

import pytest
import momapy.meta.nodes
import momapy.geometry


# List of all node classes to test
NODE_CLASSES = [
    momapy.meta.nodes.Rectangle,
    momapy.meta.nodes.Ellipse,
    momapy.meta.nodes.Stadium,
    momapy.meta.nodes.Hexagon,
    momapy.meta.nodes.TurnedHexagon,
    momapy.meta.nodes.Triangle,
    momapy.meta.nodes.Diamond,
    momapy.meta.nodes.Parallelogram,
    momapy.meta.nodes.CrossPoint,
    momapy.meta.nodes.Bar,
    momapy.meta.nodes.ArcBarb,
    momapy.meta.nodes.StraightBarb,
    momapy.meta.nodes.To,
]


@pytest.mark.parametrize("node_class", NODE_CLASSES)
class TestAllNodes:
    """Parametrized tests for all node classes."""

    def test_node_creation(self, node_class):
        """Test that each node can be created with valid params."""
        position = momapy.geometry.Point(50.0, 50.0)
        node = node_class(position=position, width=100.0, height=60.0)
        assert node.position == position
        assert node.width == 100.0
        assert node.height == 60.0

    def test_node_border_drawing_elements_returns_valid(self, node_class):
        """Test that _border_drawing_elements returns valid elements."""
        position = momapy.geometry.Point(50.0, 50.0)
        node = node_class(position=position, width=100.0, height=60.0)
        elements = node._border_drawing_elements()
        assert isinstance(elements, (list, tuple))

    def test_node_anchor_points_return_points(self, node_class):
        """Test that anchor point methods return Point objects."""
        position = momapy.geometry.Point(50.0, 50.0)
        node = node_class(position=position, width=100.0, height=60.0)

        # Test common anchor points
        center = node.center()
        assert isinstance(center, momapy.geometry.Point)

        # Some nodes may not have all anchor points (e.g., Bar is 1D)
        north = node.north()
        if north is not None:
            assert isinstance(north, momapy.geometry.Point)

        south = node.south()
        if south is not None:
            assert isinstance(south, momapy.geometry.Point)

        east = node.east()
        if east is not None:
            assert isinstance(east, momapy.geometry.Point)

        west = node.west()
        if west is not None:
            assert isinstance(west, momapy.geometry.Point)

    def test_node_bbox_returns_reasonable_bounds(self, node_class):
        """Test that bbox returns reasonable bounds."""
        position = momapy.geometry.Point(50.0, 50.0)
        node = node_class(position=position, width=100.0, height=60.0)
        bbox = node.bbox()
        assert isinstance(bbox, momapy.geometry.Bbox)
        # Some shapes like Bar can have 0 width or height (1D)
        assert bbox.width >= 0
        assert bbox.height >= 0


class TestNodeRectangle:
    """Specific tests for Rectangle node."""

    def test_rectangle_node_anchor_positions(self):
        """Test that Rectangle node anchors are at expected positions."""
        position = momapy.geometry.Point(50.0, 50.0)
        node = momapy.meta.nodes.Rectangle(position=position, width=100.0, height=60.0)

        # Center should be at position
        assert node.center().x == position.x
        assert node.center().y == position.y

        # North should be above center
        assert node.north().y < position.y

        # South should be below center
        assert node.south().y > position.y

        # East should be right of center
        assert node.east().x > position.x

        # West should be left of center
        assert node.west().x < position.x
