"""Tests for momapy.meta.shapes module."""
import pytest
import momapy.meta.shapes
import momapy.geometry


def test_rectangle_creation():
    """Test Rectangle shape creation."""
    position = momapy.geometry.Point(50.0, 50.0)
    rectangle = momapy.meta.shapes.Rectangle(
        position=position,
        width=100.0,
        height=60.0
    )
    assert rectangle.position == position
    assert rectangle.width == 100.0
    assert rectangle.height == 60.0


def test_rectangle_joints():
    """Test Rectangle joint points."""
    position = momapy.geometry.Point(50.0, 50.0)
    rectangle = momapy.meta.shapes.Rectangle(
        position=position,
        width=100.0,
        height=60.0
    )

    # Test that joint methods exist and return points
    joint1 = rectangle.joint1()
    assert isinstance(joint1, momapy.geometry.Point)

    joint2 = rectangle.joint2()
    assert isinstance(joint2, momapy.geometry.Point)


def test_rectangle_drawing_elements():
    """Test Rectangle drawing_elements method."""
    position = momapy.geometry.Point(50.0, 50.0)
    rectangle = momapy.meta.shapes.Rectangle(
        position=position,
        width=100.0,
        height=60.0
    )

    elements = rectangle.drawing_elements()
    assert isinstance(elements, list)
    assert len(elements) > 0


def test_rectangle_with_rounded_corners():
    """Test Rectangle with rounded corners."""
    position = momapy.geometry.Point(50.0, 50.0)
    rectangle = momapy.meta.shapes.Rectangle(
        position=position,
        width=100.0,
        height=60.0,
        top_left_rx=5.0,
        top_left_ry=5.0,
        top_right_rx=5.0,
        top_right_ry=5.0
    )
    assert rectangle.top_left_rx == 5.0
    assert rectangle.top_right_ry == 5.0
