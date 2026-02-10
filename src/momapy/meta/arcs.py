"""Arc classes with predefined arrowheads for connecting nodes.

This module provides arc classes that use specific arrowhead shapes from the
meta.shapes module. These arcs can be used directly in map layouts to
connect nodes with various arrowhead styles.

Available arc types:
    - PolyLine: Straight lines without arrowheads
    - Triangle: Lines with triangular arrowheads
    - ReversedTriangle: Lines with reversed triangular arrowheads
    - Diamond: Lines with diamond-shaped arrowheads
    - ReversedDiamond: Lines with reversed diamond arrowheads
    - Bar: Lines with bar-shaped arrowheads
    - Rectangle: Lines with rectangular arrowheads
    - Circle: Lines with circular arrowheads
    - DoubleTriangle: Lines with double triangular arrowheads
    - DoubleTriangleNoStraight: Lines with double triangular arrowheads (angled)
    - Ellipse: Lines with elliptical arrowheads
    - DoubleTriangleBar: Lines with double triangle and bar arrowheads

Example:
    >>> from momapy.meta.arcs import Triangle, Diamond
    >>> import momapy.geometry
    >>> # Create nodes with Point positions
    >>> node1 = Rectangle(position=momapy.geometry.Point(100, 100), width=50, height=30)
    >>> node2 = Rectangle(position=momapy.geometry.Point(300, 100), width=50, height=30)
    >>> # Create arc with segments defining the path
    >>> segment = momapy.geometry.Segment(
    ...     momapy.geometry.Point(125, 100),
    ...     momapy.geometry.Point(275, 100)
    ... )
    >>> arc1 = Triangle(segments=(segment,))
    >>> arc2 = Diamond(segments=(segment,))
"""

from dataclasses import dataclass

import momapy.core
import momapy.meta.shapes
import momapy.drawing
import momapy.geometry


@dataclass(frozen=True, kw_only=True)
class PolyLine(momapy.core.SingleHeadedArc):
    """Class for single-headed arcs with no arrowhead"""

    def _arrowhead_border_drawing_elements(self):
        return []


@dataclass(frozen=True, kw_only=True)
class Triangle(momapy.core.SingleHeadedArc):
    """Class for single-headed arcs with a triangle arrowhead"""

    arrowhead_width: float = 10.0
    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        shape = momapy.meta.shapes.Triangle(
            position=momapy.geometry.Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
            direction=momapy.core.Direction.RIGHT,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class ReversedTriangle(momapy.core.SingleHeadedArc):
    """Class for single-headed arcs with a reversed triangle arrowhead"""

    arrowhead_width: float = 10.0
    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        shape = momapy.meta.shapes.Triangle(
            position=momapy.geometry.Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
            direction=momapy.core.Direction.LEFT,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class Rectangle(momapy.core.SingleHeadedArc):
    """Class for single-headed arcs with a rectangle arrowhead"""

    arrowhead_width: float = 10.0
    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        shape = momapy.meta.shapes.Rectangle(
            position=momapy.geometry.Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class Ellipse(momapy.core.SingleHeadedArc):
    """Class for single-headed arcs with an ellipse arrowhead"""

    arrowhead_width: float = 10.0
    arrowhead_height: float = 5.0

    def _arrowhead_border_drawing_elements(self):
        shape = momapy.meta.shapes.Ellipse(
            position=momapy.geometry.Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class Diamond(momapy.core.SingleHeadedArc):
    """Class for single-headed arcs with a diamond arrowhead"""

    arrowhead_width: float = 10.0
    arrowhead_height: float = 5.0

    def _arrowhead_border_drawing_elements(self):
        shape = momapy.meta.shapes.Diamond(
            position=momapy.geometry.Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class Bar(momapy.core.SingleHeadedArc):
    """Class for single-headed arcs with a bar arrowhead"""

    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        shape = momapy.meta.shapes.Bar(
            position=momapy.geometry.Point(0, 0),
            height=self.arrowhead_height,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class ArcBarb(momapy.core.SingleHeadedArc):
    """Class for single-headed arcs with an arc barb arrowhead"""

    arrowhead_width: float = 5.0
    arrowhead_height: float = 10.0
    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )

    def _arrowhead_border_drawing_elements(self):
        shape = momapy.meta.shapes.ArcBarb(
            position=momapy.geometry.Point(-self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
            direction=momapy.core.Direction.RIGHT,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class StraightBarb(momapy.core.SingleHeadedArc):
    """Class for single-headed arcs with a straight barb arrowhead"""

    arrowhead_width: float = 10.0
    arrowhead_height: float = 10.0
    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )

    def _arrowhead_border_drawing_elements(self):
        shape = momapy.meta.shapes.StraightBarb(
            position=momapy.geometry.Point(-self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
            direction=momapy.core.Direction.RIGHT,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class To(momapy.core.SingleHeadedArc):
    """Class for single-headed arcs with a to arrowhead"""

    arrowhead_width: float = 5.0
    arrowhead_height: float = 10.0
    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )

    def _arrowhead_border_drawing_elements(self):
        shape = momapy.meta.shapes.To(
            position=momapy.geometry.Point(-self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
            direction=momapy.core.Direction.RIGHT,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class DoubleTriangle(momapy.core.DoubleHeadedArc):
    """Class for double-headed arcs with triangle arrowheads"""

    start_arrowhead_width: float = 10.0
    start_arrowhead_height: float = 10.0
    end_arrowhead_width: float = 10.0
    end_arrowhead_height: float = 10.0

    def _start_arrowhead_border_drawing_elements(self):
        shape = momapy.meta.shapes.Triangle(
            position=momapy.geometry.Point(-self.start_arrowhead_width / 2, 0),
            width=self.start_arrowhead_width,
            height=self.start_arrowhead_height,
            direction=momapy.core.Direction.LEFT,
        )
        return shape.drawing_elements()

    def _end_arrowhead_border_drawing_elements(self):
        shape = momapy.meta.shapes.Triangle(
            position=momapy.geometry.Point(self.end_arrowhead_width / 2, 0),
            width=self.end_arrowhead_width,
            height=self.end_arrowhead_height,
            direction=momapy.core.Direction.RIGHT,
        )
        return shape.drawing_elements()
