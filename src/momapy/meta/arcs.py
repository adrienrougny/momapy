"""Arc classes with predefined arrowheads for connecting nodes.

This module provides arc classes that use specific arrowhead shapes from the
meta.shapes module. These arcs can be used directly in map layouts to
connect nodes with various arrowhead styles.

Available arc types:
    Single-headed (one arrowhead):
    - PolyLine: Straight lines without arrowheads
    - Triangle: Lines with triangular arrowheads
    - ReversedTriangle: Lines with reversed triangular arrowheads
    - Rectangle: Lines with rectangular arrowheads
    - Ellipse: Lines with elliptical arrowheads
    - Diamond: Lines with diamond-shaped arrowheads
    - Bar: Lines with bar-shaped arrowheads
    - ArcBarb: Lines with an arc-barb arrowhead
    - StraightBarb: Lines with a straight-barb arrowhead
    - To: Lines with an arrow-tip ("to") arrowhead

    Double-headed (two arrowheads):
    - DoubleTriangle: Lines with double triangular arrowheads

Examples:
    ```python
    from momapy.meta.arcs import Triangle, Diamond
    from momapy.meta.nodes import Rectangle
    import momapy.geometry

    # Create nodes with Point positions
    source_node = Rectangle(
        position=Point(100, 100),
        width=50,
        height=30
    )
    target_node = Rectangle(
        position=Point(300, 100),
        width=50,
        height=30
    )

    # Create arc with segments defining the path
    segment = momapy.geometry.Segment(
        Point(125, 100),
        Point(275, 100)
    )
    arc1 = Triangle(segments=(segment,))
    arc2 = Diamond(segments=(segment,))
    ```
"""

from dataclasses import dataclass

from momapy.coloring import Color
from momapy.core.elements import Direction
from momapy.core.layout import DoubleHeadedArc
from momapy.core.layout import SingleHeadedArc
from momapy.drawing import NoneValue
from momapy.drawing import NoneValueType
from momapy.geometry import Point
from momapy.meta.shapes import ArcBarb as ArcBarbShape
from momapy.meta.shapes import Bar as BarShape
from momapy.meta.shapes import Diamond as DiamondShape
from momapy.meta.shapes import Ellipse as EllipseShape
from momapy.meta.shapes import Rectangle as RectangleShape
from momapy.meta.shapes import StraightBarb as StraightBarbShape
from momapy.meta.shapes import To as ToShape
from momapy.meta.shapes import Triangle as TriangleShape


@dataclass(frozen=True, kw_only=True)
class PolyLine(SingleHeadedArc):
    """Class for single-headed arcs with no arrowhead"""

    def _arrowhead_border_drawing_elements(self):
        return []


@dataclass(frozen=True, kw_only=True)
class Triangle(SingleHeadedArc):
    """Class for single-headed arcs with a triangle arrowhead"""

    arrowhead_width: float = 10.0
    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        shape = TriangleShape(
            position=Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
            direction=Direction.RIGHT,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class ReversedTriangle(SingleHeadedArc):
    """Class for single-headed arcs with a reversed triangle arrowhead"""

    arrowhead_width: float = 10.0
    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        shape = TriangleShape(
            position=Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
            direction=Direction.LEFT,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class Rectangle(SingleHeadedArc):
    """Class for single-headed arcs with a rectangle arrowhead"""

    arrowhead_width: float = 10.0
    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        shape = RectangleShape(
            position=Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class Ellipse(SingleHeadedArc):
    """Class for single-headed arcs with an ellipse arrowhead"""

    arrowhead_width: float = 10.0
    arrowhead_height: float = 5.0

    def _arrowhead_border_drawing_elements(self):
        shape = EllipseShape(
            position=Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class Diamond(SingleHeadedArc):
    """Class for single-headed arcs with a diamond arrowhead"""

    arrowhead_width: float = 10.0
    arrowhead_height: float = 5.0

    def _arrowhead_border_drawing_elements(self):
        shape = DiamondShape(
            position=Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class Bar(SingleHeadedArc):
    """Class for single-headed arcs with a bar arrowhead"""

    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        shape = BarShape(
            position=Point(0, 0),
            height=self.arrowhead_height,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class ArcBarb(SingleHeadedArc):
    """Class for single-headed arcs with an arc barb arrowhead"""

    arrowhead_width: float = 5.0
    arrowhead_height: float = 10.0
    arrowhead_fill: NoneValueType | Color | None = NoneValue

    def _arrowhead_border_drawing_elements(self):
        shape = ArcBarbShape(
            position=Point(-self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
            direction=Direction.RIGHT,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class StraightBarb(SingleHeadedArc):
    """Class for single-headed arcs with a straight barb arrowhead"""

    arrowhead_width: float = 10.0
    arrowhead_height: float = 10.0
    arrowhead_fill: NoneValueType | Color | None = NoneValue

    def _arrowhead_border_drawing_elements(self):
        shape = StraightBarbShape(
            position=Point(-self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
            direction=Direction.RIGHT,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class To(SingleHeadedArc):
    """Class for single-headed arcs with a to arrowhead"""

    arrowhead_width: float = 5.0
    arrowhead_height: float = 10.0
    arrowhead_fill: NoneValueType | Color | None = NoneValue

    def _arrowhead_border_drawing_elements(self):
        shape = ToShape(
            position=Point(-self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
            direction=Direction.RIGHT,
        )
        return shape.drawing_elements()


@dataclass(frozen=True, kw_only=True)
class DoubleTriangle(DoubleHeadedArc):
    """Class for double-headed arcs with triangle arrowheads"""

    start_arrowhead_width: float = 10.0
    start_arrowhead_height: float = 10.0
    end_arrowhead_width: float = 10.0
    end_arrowhead_height: float = 10.0

    def _start_arrowhead_border_drawing_elements(self):
        shape = TriangleShape(
            position=Point(-self.start_arrowhead_width / 2, 0),
            width=self.start_arrowhead_width,
            height=self.start_arrowhead_height,
            direction=Direction.LEFT,
        )
        return shape.drawing_elements()

    def _end_arrowhead_border_drawing_elements(self):
        shape = TriangleShape(
            position=Point(self.end_arrowhead_width / 2, 0),
            width=self.end_arrowhead_width,
            height=self.end_arrowhead_height,
            direction=Direction.RIGHT,
        )
        return shape.drawing_elements()
