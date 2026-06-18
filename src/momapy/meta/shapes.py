"""Geometric shape classes for drawing and layout.

This module provides various geometric shapes that can be used as borders
or standalone drawing elements. Shapes include basic geometric forms like
rectangles, ellipses, and polygons, as well as more complex shapes with
configurable corners and orientations.

Available shapes:
    - Rectangle: Rectangles with customizable rounded or cut corners
    - Ellipse: Ellipses and circles
    - Stadium: Rounded rectangles
    - Hexagon: Regular hexagons with configurable orientation
    - TurnedHexagon: Rotated hexagons
    - Parallelogram: Parallelograms with configurable angle
    - CrossPoint: Crossing-point shapes
    - Triangle: Triangles with configurable orientation
    - Diamond: Diamond/rhombus shapes
    - Bar: Bar or line shapes
    - ArcBarb: Arc-barb (curved barb) shapes
    - StraightBarb: Straight-barb shapes
    - To: Arrow-tip ("to") shapes

Examples:
    ```python
    from momapy.meta.shapes import Rectangle, Ellipse
    import momapy.geometry

    # Create a rectangle shape at origin
    rectangle_shape = Rectangle(
        position=Point(0, 0),
        width=100,
        height=50
    )

    # Create an ellipse shape at position (200, 200)
    ellipse_shape = Ellipse(
        position=Point(200, 200),
        width=100,
        height=80
    )
    ```
"""

import math
import dataclasses

from momapy.core.elements import Direction
from momapy.core.layout import Shape
from momapy.geometry import Point
from momapy.drawing import ClosePath
from momapy.drawing import Ellipse as EllipseDrawing
from momapy.drawing import EllipticalArc
from momapy.drawing import LineTo
from momapy.drawing import MoveTo
from momapy.drawing import Path
from momapy.drawing import Rectangle as RectangleDrawing


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
class Rectangle(Shape):
    """Rectangle shape.

    A rectangle whose four corners can each be independently rounded or cut.
    """

    position: Point = dataclasses.field(
        metadata={"description": "The position of the center of the shape."}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width of the shape."}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the shape."}
    )
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

    def joint1(self):
        return self.position + (
            -self.width / 2 + self.top_left_rx,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2 - self.top_right_rx,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2,
            -self.height / 2 + self.top_right_ry,
        )

    def joint4(self):
        return self.position + (
            self.width / 2,
            self.height / 2 - self.bottom_right_ry,
        )

    def joint5(self):
        return self.position + (
            self.width / 2 - self.bottom_right_rx,
            self.height / 2,
        )

    def joint6(self):
        return self.position + (
            -self.width / 2 + self.bottom_left_rx,
            self.height / 2,
        )

    def joint7(self):
        return self.position + (
            -self.width / 2,
            self.height / 2 - self.bottom_left_ry,
        )

    def joint8(self):
        return self.position + (
            -self.width / 2,
            -self.height / 2 + self.top_left_ry,
        )

    def drawing_elements(self):
        actions = [
            MoveTo(self.joint1()),
            LineTo(self.joint2()),
        ]
        if self.top_right_rx != 0 and self.top_right_ry != 0:
            if self.top_right_rounded_or_cut == "cut":
                actions.append(LineTo(self.joint3()))
            elif self.top_right_rounded_or_cut == "rounded":
                (
                    actions.append(
                        EllipticalArc(
                            self.joint3(),
                            self.top_right_rx,
                            self.top_right_ry,
                            0,
                            0,
                            1,
                        )
                    ),
                )
        actions.append(LineTo(self.joint4()))
        if self.bottom_right_rx != 0 and self.bottom_right_ry != 0:
            if self.bottom_right_rounded_or_cut == "cut":
                actions.append(LineTo(self.joint5()))
            elif self.bottom_right_rounded_or_cut == "rounded":
                (
                    actions.append(
                        EllipticalArc(
                            self.joint5(),
                            self.bottom_right_rx,
                            self.bottom_right_ry,
                            0,
                            0,
                            1,
                        )
                    ),
                )
        actions.append(LineTo(self.joint6()))
        if self.bottom_left_rx != 0 and self.bottom_left_ry != 0:
            if self.bottom_left_rounded_or_cut == "cut":
                actions.append(LineTo(self.joint7()))
            elif self.bottom_left_rounded_or_cut == "rounded":
                (
                    actions.append(
                        EllipticalArc(
                            self.joint7(),
                            self.bottom_left_rx,
                            self.bottom_left_ry,
                            0,
                            0,
                            1,
                        )
                    ),
                )
        actions.append(LineTo(self.joint8()))
        if self.top_left_rx != 0 and self.top_left_ry != 0:
            if self.top_left_rounded_or_cut == "rounded":
                (
                    actions.append(
                        EllipticalArc(
                            self.joint1(),
                            self.top_left_rx,
                            self.top_left_ry,
                            0,
                            0,
                            1,
                        )
                    ),
                )
        actions.append(ClosePath())
        drawing_element = Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Ellipse(Shape):
    """Ellipse shape.

    An ellipse (or circle) fitting the given width and height.
    """

    position: Point = dataclasses.field(
        metadata={"description": "The position of the center of the shape."}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width of the shape."}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the shape."}
    )

    def drawing_elements(self):
        drawing_element = EllipseDrawing(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Stadium(Shape):
    """Stadium shape.

    A stadium (rounded rectangle) with fully rounded left and right ends.
    """

    position: Point = dataclasses.field(
        metadata={"description": "The position of the center of the shape."}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width of the shape."}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the shape."}
    )

    def __post_init__(self):
        if self.width < self.height:
            object.__setattr__(self, "width", self.height)

    def joint1(self):
        return self.position + (
            self.height / 2 - self.width / 2,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2 - self.height / 2,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2 - self.height / 2,
            self.height / 2,
        )

    def joint4(self):
        return self.position + (
            self.height / 2 - self.width / 2,
            self.height / 2,
        )

    def drawing_elements(self):
        drawing_element = RectangleDrawing(
            point=self.position - (self.width / 2, self.height / 2),
            height=self.height,
            width=self.width,
            rx=self.height / 2,
            ry=self.height / 2,
        )
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Hexagon(Shape):
    """Hexagon shape.

    A hexagon whose left and right vertex angles are configurable.
    """

    position: Point = dataclasses.field(
        metadata={"description": "The position of the center of the shape."}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width of the shape."}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the shape."}
    )
    left_angle: float = dataclasses.field(
        metadata={"description": "The angle of the left vertex, in degrees."}
    )
    right_angle: float = dataclasses.field(
        metadata={"description": "The angle of the right vertex, in degrees."}
    )

    def joint1(self):
        if self.left_angle > 90:
            return self.position + (-self.width / 2, -self.height / 2)
        angle = math.radians(self.left_angle)
        side_length = abs(self.height / (math.tan(angle)))
        return self.position + (
            -self.width / 2 + side_length,
            -self.height / 2,
        )

    def joint2(self):
        if self.right_angle > 90:
            return self.position + (self.width / 2, -self.height / 2)
        angle = math.radians(self.right_angle)
        side_length = abs(self.height / (math.tan(angle)))
        return self.position + (self.width / 2 - side_length, -self.height / 2)

    def joint3(self):
        if self.right_angle <= 90:
            return self.position + (self.width / 2, 0)
        angle = math.radians(180 - self.right_angle)
        side_length = abs(self.height / (math.tan(angle)))
        return self.position + (self.width / 2 - side_length, 0)

    def joint4(self):
        if self.right_angle > 90:
            return self.position + (self.width / 2, self.height / 2)
        angle = math.radians(self.right_angle)
        side_length = abs(self.height / (math.tan(angle)))
        return self.position + (self.width / 2 - side_length, self.height / 2)

    def joint5(self):
        if self.left_angle > 90:
            return self.position + (-self.width / 2, self.height / 2)
        angle = math.radians(self.left_angle)
        side_length = abs(self.height / (math.tan(angle)))
        return self.position + (-self.width / 2 + side_length, self.height / 2)

    def joint6(self):
        if self.left_angle <= 90:
            return self.position + (-self.width / 2, 0)
        angle = math.radians(180 - self.left_angle)
        side_length = abs(self.height / (math.tan(angle)))
        return self.position + (-self.width / 2 + side_length, 0)

    def drawing_elements(self):
        actions = [
            MoveTo(self.joint1()),
            LineTo(self.joint2()),
            LineTo(self.joint3()),
            LineTo(self.joint4()),
            LineTo(self.joint5()),
            LineTo(self.joint6()),
            ClosePath(),
        ]
        drawing_element = Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class TurnedHexagon(Shape):
    """Turned hexagon shape.

    A hexagon turned by 90 degrees, with configurable top and bottom vertex angles.
    """

    position: Point = dataclasses.field(
        metadata={"description": "The position of the center of the shape."}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width of the shape."}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the shape."}
    )
    top_angle: float = dataclasses.field(
        metadata={"description": "The angle of the top vertex, in degrees."}
    )
    bottom_angle: float = dataclasses.field(
        metadata={"description": "The angle of the bottom vertex, in degrees."}
    )

    def joint1(self):
        if self.top_angle >= 90:
            p = self.position + (-self.width / 2, -self.height / 2)
        else:
            p = self.position + (0, -self.height / 2)
        return p

    def joint2(self):
        if self.top_angle >= 90:
            angle = math.radians(180 - self.top_angle)
            side_length = abs(self.width / (math.tan(angle)))
            p = self.position + (0, -self.height / 2 + side_length)
        else:
            angle = math.radians(self.top_angle)
            side_length = abs(self.width / (math.tan(angle)))
            p = self.position + (
                self.width / 2,
                -self.height / 2 + side_length,
            )
        return p

    def joint3(self):
        if self.top_angle >= 90:
            p = self.position + (self.width / 2, -self.height / 2)
        else:
            if self.bottom_angle >= 90:
                p = self.position + (self.width / 2, self.height / 2)
            else:
                angle = math.radians(self.top_angle)
                side_length = abs(self.width / (math.tan(angle)))
                p = self.position + (
                    self.width / 2,
                    self.height / 2 - side_length,
                )
        return p

    def joint4(self):
        if self.top_angle >= 90:
            if self.bottom_angle >= 90:
                p = self.position + (self.width / 2, self.height / 2)
            else:
                angle = math.radians(self.bottom_angle)
                side_length = abs(self.width / (math.tan(angle)))
                p = self.position + (
                    self.width / 2,
                    self.height / 2 - side_length,
                )
        else:
            if self.bottom_angle >= 90:
                angle = math.radians(180 - self.bottom_angle)
                side_length = abs(self.width / (math.tan(angle)))
                p = self.position + (
                    0,
                    self.height / 2 - side_length,
                )
            else:
                p = self.position + (0, self.height / 2)

        return p

    def joint5(self):
        if self.top_angle >= 90:
            if self.bottom_angle >= 90:
                angle = math.radians(180 - self.top_angle)
                side_length = abs(self.width / (math.tan(angle)))
                p = self.position + (0, self.height / 2 - side_length)
            else:
                p = self.position + (0, self.height / 2)
        else:
            if self.bottom_angle >= 90:
                p = self.position + (-self.width / 2, self.height / 2)
            else:
                angle = math.radians(self.bottom_angle)
                side_length = abs(self.width / (math.tan(angle)))
                p = self.position + (
                    -self.width / 2,
                    self.height / 2 - side_length,
                )
        return p

    def joint6(self):
        if self.top_angle >= 90:
            if self.bottom_angle >= 90:
                return self.position + (-self.width / 2, self.height / 2)
            else:
                angle = math.radians(180 - self.bottom_angle)
                side_length = abs(self.width / (math.tan(angle)))
                p = self.position + (
                    -self.width / 2,
                    self.height / 2 - side_length,
                )
        else:
            angle = math.radians(self.top_angle)
            side_length = abs(self.width / (math.tan(angle)))
            p = self.position + (
                -self.width / 2,
                -self.height / 2 + side_length,
            )
        return p

    def drawing_elements(self):
        actions = [
            MoveTo(self.joint1()),
            LineTo(self.joint2()),
            LineTo(self.joint3()),
            LineTo(self.joint4()),
            LineTo(self.joint5()),
            LineTo(self.joint6()),
            ClosePath(),
        ]
        drawing_element = Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Parallelogram(Shape):
    """Parallelogram shape.

    A parallelogram whose slant angle is configurable.
    """

    position: Point = dataclasses.field(
        metadata={"description": "The position of the center of the shape."}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width of the shape."}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the shape."}
    )
    angle: float = dataclasses.field(
        metadata={"description": "The angle of the slanted sides, in degrees."}
    )

    def joint1(self):
        if self.angle >= 90:
            return self.position + (-self.width / 2, -self.height / 2)
        angle = math.radians(self.angle)
        side_length = abs(self.height / math.tan(angle))
        return self.position + (
            -self.width / 2 + side_length,
            -self.height / 2,
        )

    def joint2(self):
        if self.angle <= 90:
            return self.position + (self.width / 2, -self.height / 2)
        angle = math.radians(180 - self.angle)
        side_length = abs(self.height / math.tan(angle))
        return self.position + (self.width / 2 - side_length, -self.height / 2)

    def joint3(self):
        if self.angle > 90:
            return self.position + (self.width / 2, self.height / 2)
        angle = math.radians(self.angle)
        side_length = abs(self.height / math.tan(angle))
        return self.position + (self.width / 2 - side_length, self.height / 2)

    def joint4(self):
        if self.angle <= 90:
            return self.position + (-self.width / 2, self.height / 2)
        angle = math.radians(180 - self.angle)
        side_length = abs(self.height / math.tan(angle))
        return self.position + (-self.width / 2 + side_length, self.height / 2)

    def drawing_elements(self):
        actions = [
            MoveTo(self.joint1()),
            LineTo(self.joint2()),
            LineTo(self.joint3()),
            LineTo(self.joint4()),
            ClosePath(),
        ]
        drawing_element = Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class CrossPoint(Shape):
    """Cross-point shape.

    A crossing pair of horizontal and vertical line segments.
    """

    position: Point = dataclasses.field(
        metadata={"description": "The position of the center of the shape."}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width of the shape."}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the shape."}
    )

    def drawing_elements(self):
        actions = [
            MoveTo(self.position - (self.width / 2, 0)),
            LineTo(self.position + (self.width / 2, 0)),
        ]
        horizontal_path = Path(actions=actions)
        actions = [
            MoveTo(self.position - (0, self.height / 2)),
            LineTo(self.position + (0, self.height / 2)),
        ]
        vertical_path = Path(actions=actions)
        return [horizontal_path, vertical_path]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Triangle(Shape):
    """Triangle shape.

    A triangle pointing in a configurable direction.
    """

    position: Point = dataclasses.field(
        metadata={"description": "The position of the center of the shape."}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width of the shape."}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the shape."}
    )
    direction: Direction = dataclasses.field(
        metadata={"description": "The direction the triangle points towards."}
    )

    def joint1(self):
        if self.direction == Direction.RIGHT or self.direction == Direction.DOWN:
            p = self.position + (-self.width / 2, -self.height / 2)
        elif self.direction == Direction.UP:
            p = self.position + (0, -self.height / 2)
        elif self.direction == Direction.LEFT:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint2(self):
        if self.direction == Direction.RIGHT:
            p = self.position + (self.width / 2, 0)
        elif self.direction == Direction.UP or self.direction == Direction.LEFT:
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == Direction.DOWN:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint3(self):
        if self.direction == Direction.RIGHT or self.direction == Direction.UP:
            p = self.position + (-self.width / 2, self.height / 2)
        elif self.direction == Direction.LEFT:
            p = self.position + (-self.width / 2, 0)
        elif self.direction == Direction.DOWN:
            p = self.position + (0, self.height / 2)
        return p

    def drawing_elements(self):
        actions = [
            MoveTo(self.joint1()),
            LineTo(self.joint2()),
            LineTo(self.joint3()),
            ClosePath(),
        ]
        drawing_element = Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Diamond(Shape):
    """Diamond shape.

    A diamond (rhombus) with vertices at the midpoints of its sides.
    """

    position: Point = dataclasses.field(
        metadata={"description": "The position of the center of the shape."}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width of the shape."}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the shape."}
    )

    def joint1(self):
        return self.position + (0, -self.height / 2)

    def joint2(self):
        return self.position + (self.width / 2, 0)

    def joint3(self):
        return self.position + (0, self.height / 2)

    def joint4(self):
        return self.position + (-self.width / 2, 0)

    def drawing_elements(self):
        actions = [
            MoveTo(self.joint1()),
            LineTo(self.joint2()),
            LineTo(self.joint3()),
            LineTo(self.joint4()),
            ClosePath(),
        ]
        drawing_element = Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Bar(Shape):
    """Bar shape.

    A single vertical bar segment spanning the given height.
    """

    position: Point = dataclasses.field(
        metadata={"description": "The position of the center of the shape."}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the shape."}
    )

    def joint1(self):
        return Point(0, -self.height / 2)

    def joint2(self):
        return Point(0, self.height / 2)

    def drawing_elements(self):
        actions = [
            MoveTo(self.joint1()),
            LineTo(self.joint2()),
        ]
        drawing_element = Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class ArcBarb(Shape):
    """Arc-barb shape.

    A curved (arc) barb pointing in a configurable direction.
    """

    position: Point = dataclasses.field(
        metadata={"description": "The position of the center of the shape."}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width of the shape."}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the shape."}
    )
    direction: Direction = dataclasses.field(
        metadata={"description": "The direction the barb points towards."}
    )

    def joint1(self):
        if self.direction == Direction.RIGHT or self.direction == Direction.DOWN:
            p = self.position + (-self.width / 2, -self.height / 2)
        elif self.direction == Direction.UP:
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == Direction.LEFT:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint2(self):
        if self.direction == Direction.RIGHT or self.direction == Direction.UP:
            p = self.position + (-self.width / 2, self.height / 2)
        elif self.direction == Direction.LEFT:
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == Direction.DOWN:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def drawing_elements(self):
        if self.direction == Direction.RIGHT:
            actions = [
                MoveTo(self.joint1()),
                EllipticalArc(
                    self.joint2(),
                    self.width,
                    self.height / 2,
                    0,
                    0,
                    1,
                ),
            ]
        elif self.direction == Direction.UP:
            actions = [
                MoveTo(self.joint1()),
                EllipticalArc(
                    self.joint2(),
                    self.width / 2,
                    self.height,
                    0,
                    0,
                    0,
                ),
            ]
        elif self.direction == Direction.LEFT:
            actions = [
                MoveTo(self.joint1()),
                EllipticalArc(
                    self.joint2(),
                    self.width,
                    self.height / 2,
                    0,
                    0,
                    0,
                ),
            ]
        elif self.direction == Direction.DOWN:
            actions = [
                MoveTo(self.joint1()),
                EllipticalArc(
                    self.joint2(),
                    self.width / 2,
                    self.height,
                    0,
                    0,
                    0,
                ),
            ]
        drawing_element = Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class StraightBarb(Shape):
    """Straight-barb shape.

    A straight barb pointing in a configurable direction.
    """

    position: Point = dataclasses.field(
        metadata={"description": "The position of the center of the shape."}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width of the shape."}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the shape."}
    )
    direction: Direction = dataclasses.field(
        metadata={"description": "The direction the barb points towards."}
    )

    def joint1(self):
        if self.direction == Direction.RIGHT or self.direction == Direction.DOWN:
            p = self.position + (-self.width / 2, -self.height / 2)
        elif self.direction == Direction.UP:
            p = self.position + (0, -self.height / 2)
        elif self.direction == Direction.LEFT:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint2(self):
        if self.direction == Direction.RIGHT:
            p = self.position + (self.width / 2, 0)
        elif self.direction == Direction.UP or self.direction == Direction.LEFT:
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == Direction.DOWN:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint3(self):
        if self.direction == Direction.RIGHT or self.direction == Direction.UP:
            p = self.position + (-self.width / 2, self.height / 2)
        elif self.direction == Direction.LEFT:
            p = self.position + (-self.width / 2, 0)
        elif self.direction == Direction.DOWN:
            p = self.position + (0, self.height / 2)
        return p

    def drawing_elements(self):
        if self.direction == Direction.RIGHT:
            actions = [
                MoveTo(self.joint1()),
                LineTo(self.joint2()),
                LineTo(self.joint3()),
            ]
        elif self.direction == Direction.UP:
            actions = [
                MoveTo(self.joint3()),
                LineTo(self.joint1()),
                LineTo(self.joint2()),
            ]
        elif self.direction == Direction.LEFT:
            actions = [
                MoveTo(self.joint1()),
                LineTo(self.joint3()),
                LineTo(self.joint2()),
            ]
        elif self.direction == Direction.DOWN:
            actions = [
                MoveTo(self.joint1()),
                LineTo(self.joint3()),
                LineTo(self.joint2()),
            ]
        drawing_element = Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class To(Shape):
    """To shape.

    An arrow-tip ("to") shape pointing in a configurable direction.
    """

    position: Point = dataclasses.field(
        metadata={"description": "The position of the center of the shape."}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width of the shape."}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the shape."}
    )
    direction: Direction = dataclasses.field(
        metadata={"description": "The direction the arrow tip points towards."}
    )

    def joint1(self):
        if self.direction == Direction.RIGHT or self.direction == Direction.DOWN:
            p = self.position + (-self.width / 2, -self.height / 2)
        elif self.direction == Direction.UP:
            p = self.position + (0, -self.height / 2)
        elif self.direction == Direction.LEFT:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint2(self):
        if self.direction == Direction.RIGHT:
            p = self.position + (self.width / 2, 0)
        elif self.direction == Direction.UP or self.direction == Direction.LEFT:
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == Direction.DOWN:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint3(self):
        if self.direction == Direction.RIGHT or self.direction == Direction.UP:
            p = self.position + (-self.width / 2, self.height / 2)
        elif self.direction == Direction.LEFT:
            p = self.position + (-self.width / 2, 0)
        elif self.direction == Direction.DOWN:
            p = self.position + (0, self.height / 2)
        return p

    def drawing_elements(self):
        if self.direction == Direction.RIGHT:
            actions = [
                MoveTo(self.joint1()),
                EllipticalArc(
                    self.joint2(),
                    self.width,
                    self.height / 2,
                    0,
                    0,
                    0,
                ),
                EllipticalArc(
                    self.joint3(),
                    self.width,
                    self.height / 2,
                    0,
                    0,
                    0,
                ),
            ]
        elif self.direction == Direction.UP:
            actions = [
                MoveTo(self.joint3()),
                EllipticalArc(
                    self.joint1(),
                    self.height,
                    self.width / 2,
                    0,
                    0,
                    0,
                ),
                EllipticalArc(
                    self.joint2(),
                    self.height,
                    self.width / 2,
                    0,
                    0,
                    0,
                ),
            ]
        elif self.direction == Direction.LEFT:
            actions = [
                MoveTo(self.joint1()),
                EllipticalArc(
                    self.joint3(),
                    self.width,
                    self.height / 2,
                    0,
                    0,
                    1,
                ),
                EllipticalArc(
                    self.joint2(),
                    self.width,
                    self.height / 2,
                    0,
                    0,
                    1,
                ),
            ]
        elif self.direction == Direction.DOWN:
            actions = [
                MoveTo(self.joint1()),
                EllipticalArc(
                    self.joint3(),
                    self.height,
                    self.width / 2,
                    0,
                    0,
                    1,
                ),
                EllipticalArc(
                    self.joint2(),
                    self.height,
                    self.width / 2,
                    0,
                    0,
                    1,
                ),
            ]

        drawing_element = Path(actions=actions)
        return [drawing_element]
