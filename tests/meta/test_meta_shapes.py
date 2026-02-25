"""Tests for momapy.meta.shapes module."""

import pytest
import momapy.meta.shapes
import momapy.geometry
import momapy.core
import momapy.core.elements


# Simple shapes that only need position, width, height
SIMPLE_SHAPE_CLASSES = [
    momapy.meta.shapes.Rectangle,
    momapy.meta.shapes.Ellipse,
    momapy.meta.shapes.Stadium,
    momapy.meta.shapes.Diamond,
    momapy.meta.shapes.CrossPoint,
]

# Shapes with unique signatures
SHAPE_PARAMS = {
    momapy.meta.shapes.Bar: {"height": 60.0},  # No width
    momapy.meta.shapes.ArcBarb: {
        "width": 100.0,
        "height": 60.0,
        "direction": momapy.core.elements.Direction.RIGHT,
    },
    momapy.meta.shapes.StraightBarb: {
        "width": 100.0,
        "height": 60.0,
        "direction": momapy.core.elements.Direction.RIGHT,
    },
    momapy.meta.shapes.To: {
        "width": 100.0,
        "height": 60.0,
        "direction": momapy.core.elements.Direction.RIGHT,
    },
    momapy.meta.shapes.Hexagon: {
        "width": 100.0,
        "height": 60.0,
        "left_angle": 120,
        "right_angle": 120,
    },
    momapy.meta.shapes.TurnedHexagon: {
        "width": 100.0,
        "height": 60.0,
        "top_angle": 120,
        "bottom_angle": 120,
    },
    momapy.meta.shapes.Triangle: {
        "width": 100.0,
        "height": 60.0,
        "direction": momapy.core.elements.Direction.RIGHT,
    },
    momapy.meta.shapes.Parallelogram: {"width": 100.0, "height": 60.0, "angle": 60},
}

# All shape classes combined
ALL_SHAPE_CLASSES = SIMPLE_SHAPE_CLASSES + list(SHAPE_PARAMS.keys())


def create_shape(shape_class, position, width, height):
    """Helper function to create a shape with appropriate parameters."""
    if shape_class in SHAPE_PARAMS:
        kwargs = {"position": position}
        kwargs.update(SHAPE_PARAMS[shape_class])
    else:
        kwargs = {"position": position, "width": width, "height": height}
    return shape_class(**kwargs)


class TestRectangle:
    """Tests for Rectangle shape."""

    def test_rectangle_creation(self):
        """Test Rectangle shape creation."""
        position = momapy.geometry.Point(50.0, 50.0)
        rectangle = momapy.meta.shapes.Rectangle(
            position=position, width=100.0, height=60.0
        )
        assert rectangle.position == position
        assert rectangle.width == 100.0
        assert rectangle.height == 60.0

    def test_rectangle_joints(self):
        """Test Rectangle joint points."""
        position = momapy.geometry.Point(50.0, 50.0)
        rectangle = momapy.meta.shapes.Rectangle(
            position=position, width=100.0, height=60.0
        )

        # Test that joint methods exist and return points
        joint1 = rectangle.joint1()
        assert isinstance(joint1, momapy.geometry.Point)

        joint2 = rectangle.joint2()
        assert isinstance(joint2, momapy.geometry.Point)

    def test_rectangle_drawing_elements(self):
        """Test Rectangle drawing_elements method."""
        position = momapy.geometry.Point(50.0, 50.0)
        rectangle = momapy.meta.shapes.Rectangle(
            position=position, width=100.0, height=60.0
        )

        elements = rectangle.drawing_elements()
        assert isinstance(elements, list)
        assert len(elements) > 0

    def test_rectangle_with_rounded_corners(self):
        """Test Rectangle with rounded corners."""
        position = momapy.geometry.Point(50.0, 50.0)
        rectangle = momapy.meta.shapes.Rectangle(
            position=position,
            width=100.0,
            height=60.0,
            top_left_rx=5.0,
            top_left_ry=5.0,
            top_right_rx=5.0,
            top_right_ry=5.0,
        )
        assert rectangle.top_left_rx == 5.0
        assert rectangle.top_right_ry == 5.0


@pytest.mark.parametrize("shape_class", ALL_SHAPE_CLASSES)
class TestAllShapes:
    """Parametrized tests for all shape classes."""

    def test_shape_creation(self, shape_class):
        """Test that each shape can be created with valid params."""
        position = momapy.geometry.Point(50.0, 50.0)
        shape = create_shape(shape_class, position, 100.0, 60.0)
        assert shape.position == position
        # Some shapes like Bar don't have width, but all have height or equivalent
        if hasattr(shape, "width"):
            assert shape.width == 100.0
        if hasattr(shape, "height"):
            assert shape.height == 60.0

    def test_shape_drawing_elements_returns_non_empty(self, shape_class):
        """Test that drawing_elements returns non-empty list."""
        position = momapy.geometry.Point(50.0, 50.0)
        shape = create_shape(shape_class, position, 100.0, 60.0)
        elements = shape.drawing_elements()
        assert isinstance(elements, (list, tuple))
        assert len(elements) > 0

    def test_shape_bbox_returns_reasonable_bounds(self, shape_class):
        """Test that bbox returns reasonable bounds."""
        position = momapy.geometry.Point(50.0, 50.0)
        shape = create_shape(shape_class, position, 100.0, 60.0)
        bbox = shape.bbox()
        assert isinstance(bbox, momapy.geometry.Bbox)
        # Some shapes like Bar can have 0 width or height (1D)
        assert bbox.width >= 0
        assert bbox.height >= 0
