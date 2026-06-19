"""Node classes with predefined shapes for map layouts.

This module provides node classes that use specific shapes from the
meta.shapes module. These nodes can be used directly in map layouts
without needing to define custom shapes.

Available node types:
    - Rectangle: Rectangular nodes with optional rounded corners
    - Ellipse: Elliptical or circular nodes
    - Stadium: Stadium-shaped (rounded rectangle) nodes
    - Hexagon: Hexagonal nodes
    - TurnedHexagon: Rotated hexagonal nodes
    - Parallelogram: Parallelogram-shaped nodes
    - CrossPoint: Crossing-point nodes
    - Triangle: Triangular nodes
    - Diamond: Diamond-shaped nodes
    - Bar: Bar or line-shaped nodes
    - ArcBarb: Arc-barb (curved barb) nodes
    - StraightBarb: Straight-barb nodes
    - To: Arrow-tip ("to") nodes

Examples:
    ```python
    from momapy.meta.nodes import Rectangle, Ellipse
    import momapy.geometry

    # Create a rectangle node at position (100, 100)
    rectangle_node = Rectangle(
        position=momapy.geometry.Point(100, 100),
        width=200,
        height=100
    )

    # Create a circular node at position (300, 300)
    circle_node = Ellipse(
        position=momapy.geometry.Point(300, 300),
        width=150,
        height=150
    )
    ```
"""

import dataclasses

from momapy.core.elements import Direction
from momapy.core.layout import Node
from momapy.drawing import DrawingElement
from momapy.meta.shapes import ArcBarb as ArcBarbShape
from momapy.meta.shapes import Bar as BarShape
from momapy.meta.shapes import CrossPoint as CrossPointShape
from momapy.meta.shapes import Diamond as DiamondShape
from momapy.meta.shapes import Ellipse as EllipseShape
from momapy.meta.shapes import Hexagon as HexagonShape
from momapy.meta.shapes import Parallelogram as ParallelogramShape
from momapy.meta.shapes import Rectangle as RectangleShape
from momapy.meta.shapes import Stadium as StadiumShape
from momapy.meta.shapes import StraightBarb as StraightBarbShape
from momapy.meta.shapes import To as ToShape
from momapy.meta.shapes import Triangle as TriangleShape
from momapy.meta.shapes import TurnedHexagon as TurnedHexagonShape


__all__ = [
    "Rectangle",
    "Ellipse",
    "Stadium",
    "Hexagon",
    "TurnedHexagon",
    "Parallelogram",
    "CrossPoint",
    "Triangle",
    "Diamond",
    "Bar",
    "ArcBarb",
    "StraightBarb",
    "To",
]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Rectangle(Node):
    """Rectangle node.

    A rectangular node whose four corners can each be independently rounded or cut.
    """

    top_left_rx: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The x-radius of the top-left corner."},
    )
    top_left_ry: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The y-radius of the top-left corner."},
    )
    top_left_rounded_or_cut: str = dataclasses.field(
        default="rounded",
        metadata={"description": "Whether the top-left corner is rounded or cut."},
    )
    top_right_rx: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The x-radius of the top-right corner."},
    )
    top_right_ry: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The y-radius of the top-right corner."},
    )
    top_right_rounded_or_cut: str = dataclasses.field(
        default="rounded",
        metadata={"description": "Whether the top-right corner is rounded or cut."},
    )
    bottom_right_rx: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The x-radius of the bottom-right corner."},
    )
    bottom_right_ry: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The y-radius of the bottom-right corner."},
    )
    bottom_right_rounded_or_cut: str = dataclasses.field(
        default="rounded",
        metadata={"description": "Whether the bottom-right corner is rounded or cut."},
    )
    bottom_left_rx: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The x-radius of the bottom-left corner."},
    )
    bottom_left_ry: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The y-radius of the bottom-left corner."},
    )
    bottom_left_rounded_or_cut: str = dataclasses.field(
        default="rounded",
        metadata={"description": "Whether the bottom-left corner is rounded or cut."},
    )

    def _border_drawing_elements(self) -> list[DrawingElement]:
        shape = RectangleShape(
            position=self.position,
            width=self.width,
            height=self.height,
            top_left_rx=self.top_left_rx,
            top_left_ry=self.top_left_ry,
            top_left_rounded_or_cut=self.top_left_rounded_or_cut,
            top_right_rx=self.top_right_rx,
            top_right_ry=self.top_right_ry,
            top_right_rounded_or_cut=self.top_right_rounded_or_cut,
            bottom_left_rx=self.bottom_left_rx,
            bottom_left_ry=self.bottom_left_ry,
            bottom_left_rounded_or_cut=self.bottom_left_rounded_or_cut,
            bottom_right_rx=self.bottom_right_rx,
            bottom_right_ry=self.bottom_right_ry,
            bottom_right_rounded_or_cut=self.bottom_right_rounded_or_cut,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Ellipse(Node):
    """Ellipse node.

    An elliptical (or circular) node fitting the node's width and height.
    """

    def _border_drawing_elements(self) -> list[DrawingElement]:
        shape = EllipseShape(
            position=self.position,
            width=self.width,
            height=self.height,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Stadium(Node):
    """Stadium node.

    A stadium-shaped (rounded-rectangle) node with fully rounded left and right ends.
    """

    def _border_drawing_elements(self) -> list[DrawingElement]:
        shape = StadiumShape(
            position=self.position,
            width=self.width,
            height=self.height,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Hexagon(Node):
    """Hexagon node.

    A hexagonal node whose left and right vertex angles are configurable.
    """

    left_angle: float = dataclasses.field(
        default=60.0,
        metadata={"description": "The angle of the left vertex, in degrees."},
    )
    right_angle: float = dataclasses.field(
        default=60.0,
        metadata={"description": "The angle of the right vertex, in degrees."},
    )

    def _border_drawing_elements(self) -> list[DrawingElement]:
        shape = HexagonShape(
            position=self.position,
            width=self.width,
            height=self.height,
            left_angle=self.left_angle,
            right_angle=self.right_angle,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class TurnedHexagon(Node):
    """Turned hexagon node.

    A hexagonal node turned by 90 degrees, with configurable top and bottom vertex angles.
    """

    top_angle: float = dataclasses.field(
        default=80.0,
        metadata={"description": "The angle of the top vertex, in degrees."},
    )
    bottom_angle: float = dataclasses.field(
        default=80.0,
        metadata={"description": "The angle of the bottom vertex, in degrees."},
    )

    def _border_drawing_elements(self) -> list[DrawingElement]:
        shape = TurnedHexagonShape(
            position=self.position,
            width=self.width,
            height=self.height,
            top_angle=self.top_angle,
            bottom_angle=self.bottom_angle,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Parallelogram(Node):
    """Parallelogram node.

    A parallelogram-shaped node whose slant angle is configurable.
    """

    angle: float = dataclasses.field(
        default=60.0,
        metadata={"description": "The angle of the slanted sides, in degrees."},
    )

    def _border_drawing_elements(self) -> list[DrawingElement]:
        shape = ParallelogramShape(
            position=self.position,
            width=self.width,
            height=self.height,
            angle=self.angle,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class CrossPoint(Node):
    """Cross-point node.

    A node drawn as a crossing pair of horizontal and vertical line segments.
    """

    def _border_drawing_elements(self) -> list[DrawingElement]:
        shape = CrossPointShape(
            position=self.position,
            width=self.width,
            height=self.height,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Triangle(Node):
    """Triangle node.

    A triangular node pointing in a configurable direction.
    """

    direction: Direction = dataclasses.field(
        default=Direction.RIGHT,
        metadata={"description": "The direction the triangle points towards."},
    )

    def _border_drawing_elements(self) -> list[DrawingElement]:
        shape = TriangleShape(
            position=self.position,
            width=self.width,
            height=self.height,
            direction=self.direction,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Diamond(Node):
    """Diamond node.

    A diamond-shaped (rhombus) node with vertices at the midpoints of its sides.
    """

    def _border_drawing_elements(self) -> list[DrawingElement]:
        shape = DiamondShape(
            position=self.position,
            width=self.width,
            height=self.height,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Bar(Node):
    """Bar node.

    A node drawn as a single vertical bar segment spanning the node's height.
    """

    def _border_drawing_elements(self) -> list[DrawingElement]:
        shape = BarShape(
            position=self.position,
            height=self.height,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class ArcBarb(Node):
    """Arc-barb node.

    A node drawn as a curved (arc) barb pointing in a configurable direction.
    """

    direction: Direction = dataclasses.field(
        default=Direction.RIGHT,
        metadata={"description": "The direction the barb points towards."},
    )

    def _border_drawing_elements(self) -> list[DrawingElement]:
        shape = ArcBarbShape(
            position=self.position,
            width=self.width,
            height=self.height,
            direction=self.direction,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class StraightBarb(Node):
    """Straight-barb node.

    A node drawn as a straight barb pointing in a configurable direction.
    """

    direction: Direction = dataclasses.field(
        default=Direction.RIGHT,
        metadata={"description": "The direction the barb points towards."},
    )

    def _border_drawing_elements(self) -> list[DrawingElement]:
        shape = StraightBarbShape(
            position=self.position,
            width=self.width,
            height=self.height,
            direction=self.direction,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class To(Node):
    """To node.

    A node drawn as an arrow-tip ("to") shape pointing in a configurable direction.
    """

    direction: Direction = dataclasses.field(
        default=Direction.RIGHT,
        metadata={"description": "The direction the arrow tip points towards."},
    )

    def _border_drawing_elements(self) -> list[DrawingElement]:
        shape = ToShape(
            position=self.position,
            width=self.width,
            height=self.height,
            direction=self.direction,
        )
        return shape.drawing_elements()
