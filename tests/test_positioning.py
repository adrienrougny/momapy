"""Tests for momapy.positioning module."""

import pytest
import momapy.positioning
import momapy.geometry


def test_right_of_point():
    """Test right_of with a Point."""
    point = momapy.geometry.Point(10.0, 20.0)
    result = momapy.positioning.right_of(point, 5.0)
    assert result.x == 15.0
    assert result.y == 20.0


def test_left_of_point():
    """Test left_of with a Point."""
    point = momapy.geometry.Point(10.0, 20.0)
    result = momapy.positioning.left_of(point, 5.0)
    assert result.x == 5.0
    assert result.y == 20.0


def test_above_of_point():
    """Test above_of with a Point."""
    point = momapy.geometry.Point(10.0, 20.0)
    result = momapy.positioning.above_of(point, 5.0)
    assert result.x == 10.0
    assert result.y == 15.0


def test_below_of_point():
    """Test below_of with a Point."""
    point = momapy.geometry.Point(10.0, 20.0)
    result = momapy.positioning.below_of(point, 5.0)
    assert result.x == 10.0
    assert result.y == 25.0


def test_above_left_of_point():
    """Test above_left_of with a Point."""
    point = momapy.geometry.Point(10.0, 20.0)
    result = momapy.positioning.above_left_of(point, 5.0, 3.0)
    assert result.x == 7.0  # 10 - 3
    assert result.y == 15.0  # 20 - 5


def test_above_left_of_point_single_distance():
    """Test above_left_of with single distance."""
    point = momapy.geometry.Point(10.0, 20.0)
    result = momapy.positioning.above_left_of(point, 5.0)
    assert result.x == 5.0  # 10 - 5
    assert result.y == 15.0  # 20 - 5


def test_above_right_of_point():
    """Test above_right_of with a Point."""
    point = momapy.geometry.Point(10.0, 20.0)
    result = momapy.positioning.above_right_of(point, 5.0, 3.0)
    assert result.x == 13.0  # 10 + 3
    assert result.y == 15.0  # 20 - 5


def test_below_left_of_point():
    """Test below_left_of with a Point."""
    point = momapy.geometry.Point(10.0, 20.0)
    result = momapy.positioning.below_left_of(point, 5.0, 3.0)
    assert result.x == 7.0  # 10 - 3
    assert result.y == 25.0  # 20 + 5


def test_below_right_of_point():
    """Test below_right_of with a Point."""
    point = momapy.geometry.Point(10.0, 20.0)
    result = momapy.positioning.below_right_of(point, 5.0, 3.0)
    assert result.x == 13.0  # 10 + 3
    assert result.y == 25.0  # 20 + 5


def test_right_of_with_node():
    """Test right_of with a Node (via meta.nodes.Rectangle)."""
    import momapy.meta.nodes

    node = momapy.meta.nodes.Rectangle(
        position=momapy.geometry.Point(10.0, 20.0), width=20.0, height=10.0
    )
    result = momapy.positioning.right_of(node, 5.0)
    assert isinstance(result, momapy.geometry.Point)
    # Result should be to the right of the node's east anchor
    assert result.x > 10.0


def test_left_of_with_node():
    """Test left_of with a Node (via meta.nodes.Rectangle)."""
    import momapy.meta.nodes

    node = momapy.meta.nodes.Rectangle(
        position=momapy.geometry.Point(10.0, 20.0), width=20.0, height=10.0
    )
    result = momapy.positioning.left_of(node, 5.0)
    assert isinstance(result, momapy.geometry.Point)
    # Result should be to the left of the node's west anchor
    assert result.x < 10.0


def test_mid_of_two_points():
    """Test mid_of returns midpoint between two positions."""
    p1 = momapy.geometry.Point(0.0, 0.0)
    p2 = momapy.geometry.Point(10.0, 20.0)
    result = momapy.positioning.mid_of(p1, p2)
    assert result.x == 5.0
    assert result.y == 10.0


def test_fit_single_point():
    """Test fit with single point."""
    point = momapy.geometry.Point(10.0, 20.0)
    bbox = momapy.positioning.fit([point])
    assert isinstance(bbox, momapy.geometry.Bbox)
    assert bbox.position.x == 10.0
    assert bbox.position.y == 20.0


def test_fit_multiple_points():
    """Test fit with multiple points."""
    points = [
        momapy.geometry.Point(0.0, 0.0),
        momapy.geometry.Point(10.0, 20.0),
        momapy.geometry.Point(5.0, 15.0),
    ]
    bbox = momapy.positioning.fit(points)
    assert isinstance(bbox, momapy.geometry.Bbox)
    assert bbox.width > 0
    assert bbox.height > 0
