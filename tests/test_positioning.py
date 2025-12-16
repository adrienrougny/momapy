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
