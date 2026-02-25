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
    - Triangle: Triangles with configurable orientation
    - Diamond: Diamond/rhombus shapes
    - Parallelogram: Parallelograms with configurable angle
    - RectangleWithSlantedSides: Rectangles with slanted sides
    - Pentagon: Pentagon shapes
    - HexagonWithSlantedSides: Hexagons with slanted sides
    - Barrel: Barrel/cylinder shapes
    - BottomRectangleHalfCircle: Composite bottom-rectangle half-circle shape
    - CutRectangle: Rectangles with cut corners
    - TriangleRectangle: Combined triangle and rectangle shapes
    - StadiumWithNotch: Stadium shapes with notches
    - TurnedStadiumWithNotch: Rotated stadium shapes with notches
    - RoundedRectangle: Fully rounded rectangles
    - DefaultShape: Default rectangular shape
    - Line: Simple line shapes

Example:
    >>> from momapy.meta.shapes import Rectangle, Ellipse
    >>> import momapy.geometry
    >>> # Create a rectangle shape at origin
    >>> rectangle_shape = Rectangle(
    ...     position=momapy.geometry.Point(0, 0),
    ...     width=100,
    ...     height=50
    ... )
    >>> # Create an ellipse shape at position (200, 200)
    >>> ellipse_shape = Ellipse(
    ...     position=momapy.geometry.Point(200, 200),
    ...     width=100,
    ...     height=80
    ... )
"""

import math
import dataclasses

import momapy.core
import momapy.core.elements
import momapy.core.layout
import momapy.geometry
import momapy.drawing


@dataclasses.dataclass(frozen=True, kw_only=True)
class Rectangle(momapy.core.layout.Shape):
    """Class for rectangle shapes"""

    position: momapy.geometry.Point
    width: float
    height: float
    top_left_rx: float = 0.0
    top_left_ry: float = 0.0
    top_left_rounded_or_cut: str = "rounded"
    top_right_rx: float = 0.0
    top_right_ry: float = 0.0
    top_right_rounded_or_cut: str = "rounded"
    bottom_right_rx: float = 0.0
    bottom_right_ry: float = 0.0
    bottom_right_rounded_or_cut: str = "rounded"
    bottom_left_rx: float = 0.0
    bottom_left_ry: float = 0.0
    bottom_left_rounded_or_cut: str = "rounded"

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
            momapy.drawing.MoveTo(self.joint1()),
            momapy.drawing.LineTo(self.joint2()),
        ]
        if self.top_right_rx != 0 and self.top_right_ry != 0:
            if self.top_right_rounded_or_cut == "cut":
                actions.append(momapy.drawing.LineTo(self.joint3()))
            elif self.top_right_rounded_or_cut == "rounded":
                (
                    actions.append(
                        momapy.drawing.EllipticalArc(
                            self.joint3(),
                            self.top_right_rx,
                            self.top_right_ry,
                            0,
                            0,
                            1,
                        )
                    ),
                )
        actions.append(momapy.drawing.LineTo(self.joint4()))
        if self.bottom_right_rx != 0 and self.bottom_right_ry != 0:
            if self.bottom_right_rounded_or_cut == "cut":
                actions.append(momapy.drawing.LineTo(self.joint5()))
            elif self.bottom_right_rounded_or_cut == "rounded":
                (
                    actions.append(
                        momapy.drawing.EllipticalArc(
                            self.joint5(),
                            self.bottom_right_rx,
                            self.bottom_right_ry,
                            0,
                            0,
                            1,
                        )
                    ),
                )
        actions.append(momapy.drawing.LineTo(self.joint6()))
        if self.bottom_left_rx != 0 and self.bottom_left_ry != 0:
            if self.bottom_left_rounded_or_cut == "cut":
                actions.append(momapy.drawing.LineTo(self.joint7()))
            elif self.bottom_left_rounded_or_cut == "rounded":
                (
                    actions.append(
                        momapy.drawing.EllipticalArc(
                            self.joint7(),
                            self.bottom_left_rx,
                            self.bottom_left_ry,
                            0,
                            0,
                            1,
                        )
                    ),
                )
        actions.append(momapy.drawing.LineTo(self.joint8()))
        if self.top_left_rx != 0 and self.top_left_ry != 0:
            if self.top_left_rounded_or_cut == "rounded":
                (
                    actions.append(
                        momapy.drawing.EllipticalArc(
                            self.joint1(),
                            self.top_left_rx,
                            self.top_left_ry,
                            0,
                            0,
                            1,
                        )
                    ),
                )
        actions.append(momapy.drawing.ClosePath())
        drawing_element = momapy.drawing.Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Ellipse(momapy.core.layout.Shape):
    """Class for ellipse shapes"""

    position: momapy.geometry.Point
    width: float
    height: float

    def drawing_elements(self):
        drawing_element = momapy.drawing.Ellipse(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Stadium(momapy.core.layout.Shape):
    """Class for stadium shapes"""

    position: momapy.geometry.Point
    width: float
    height: float

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
        drawing_element = momapy.drawing.Rectangle(
            point=self.position - (self.width / 2, self.height / 2),
            height=self.height,
            width=self.width,
            rx=self.height / 2,
            ry=self.height / 2,
        )
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Hexagon(momapy.core.layout.Shape):
    """Class for hexagon shapes"""

    position: momapy.geometry.Point
    width: float
    height: float
    left_angle: float
    right_angle: float

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
            momapy.drawing.MoveTo(self.joint1()),
            momapy.drawing.LineTo(self.joint2()),
            momapy.drawing.LineTo(self.joint3()),
            momapy.drawing.LineTo(self.joint4()),
            momapy.drawing.LineTo(self.joint5()),
            momapy.drawing.LineTo(self.joint6()),
            momapy.drawing.ClosePath(),
        ]
        drawing_element = momapy.drawing.Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class TurnedHexagon(momapy.core.layout.Shape):
    """Class for hexagon turned by 90 degrees shapes"""

    position: momapy.geometry.Point
    width: float
    height: float
    top_angle: float
    bottom_angle: float

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
            momapy.drawing.MoveTo(self.joint1()),
            momapy.drawing.LineTo(self.joint2()),
            momapy.drawing.LineTo(self.joint3()),
            momapy.drawing.LineTo(self.joint4()),
            momapy.drawing.LineTo(self.joint5()),
            momapy.drawing.LineTo(self.joint6()),
            momapy.drawing.ClosePath(),
        ]
        drawing_element = momapy.drawing.Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Parallelogram(momapy.core.layout.Shape):
    """Class for parallelogram shapes"""

    position: momapy.geometry.Point
    width: float
    height: float
    angle: float

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
            momapy.drawing.MoveTo(self.joint1()),
            momapy.drawing.LineTo(self.joint2()),
            momapy.drawing.LineTo(self.joint3()),
            momapy.drawing.LineTo(self.joint4()),
            momapy.drawing.ClosePath(),
        ]
        drawing_element = momapy.drawing.Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class CrossPoint(momapy.core.layout.Shape):
    """Class for cross point shapes"""

    position: momapy.geometry.Point
    width: float
    height: float

    def drawing_elements(self):
        actions = [
            momapy.drawing.MoveTo(self.position - (self.width / 2, 0)),
            momapy.drawing.LineTo(self.position + (self.width / 2, 0)),
        ]
        horizontal_path = momapy.drawing.Path(actions=actions)
        actions = [
            momapy.drawing.MoveTo(self.position - (0, self.height / 2, 0)),
            momapy.drawing.LineTo(self.position + (0, self.height / 2)),
        ]
        vertical_path = momapy.drawing.Path(actions=actions)
        return [horizontal_path, vertical_path]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Triangle(momapy.core.layout.Shape):
    """Class for triangle shapes"""

    position: momapy.geometry.Point
    width: float
    height: float
    direction: momapy.core.elements.Direction

    def joint1(self):
        if (
            self.direction == momapy.core.elements.Direction.RIGHT
            or self.direction == momapy.core.elements.Direction.DOWN
        ):
            p = self.position + (-self.width / 2, -self.height / 2)
        elif self.direction == momapy.core.elements.Direction.UP:
            p = self.position + (0, -self.height / 2)
        elif self.direction == momapy.core.elements.Direction.LEFT:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint2(self):
        if self.direction == momapy.core.elements.Direction.RIGHT:
            p = self.position + (self.width / 2, 0)
        elif (
            self.direction == momapy.core.elements.Direction.UP
            or self.direction == momapy.core.elements.Direction.LEFT
        ):
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == momapy.core.elements.Direction.DOWN:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint3(self):
        if (
            self.direction == momapy.core.elements.Direction.RIGHT
            or self.direction == momapy.core.elements.Direction.UP
        ):
            p = self.position + (-self.width / 2, self.height / 2)
        elif self.direction == momapy.core.elements.Direction.LEFT:
            p = self.position + (-self.width / 2, 0)
        elif self.direction == momapy.core.elements.Direction.DOWN:
            p = self.position + (0, self.height / 2)
        return p

    def drawing_elements(self):
        actions = [
            momapy.drawing.MoveTo(self.joint1()),
            momapy.drawing.LineTo(self.joint2()),
            momapy.drawing.LineTo(self.joint3()),
            momapy.drawing.ClosePath(),
        ]
        drawing_element = momapy.drawing.Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Diamond(momapy.core.layout.Shape):
    """Class for diamond shapes"""

    position: momapy.geometry.Point
    width: float
    height: float

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
            momapy.drawing.MoveTo(self.joint1()),
            momapy.drawing.LineTo(self.joint2()),
            momapy.drawing.LineTo(self.joint3()),
            momapy.drawing.LineTo(self.joint4()),
            momapy.drawing.ClosePath(),
        ]
        drawing_element = momapy.drawing.Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Bar(momapy.core.layout.Shape):
    """Class for bar shapes"""

    position: momapy.geometry.Point
    height: float

    def joint1(self):
        return momapy.geometry.Point(0, -self.height / 2)

    def joint2(self):
        return momapy.geometry.Point(0, self.height / 2)

    def drawing_elements(self):
        actions = [
            momapy.drawing.MoveTo(self.joint1()),
            momapy.drawing.LineTo(self.joint2()),
        ]
        drawing_element = momapy.drawing.Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class ArcBarb(momapy.core.layout.Shape):
    """Class for arc barb shapes"""

    position: momapy.geometry.Point
    width: float
    height: float
    direction: momapy.core.elements.Direction

    def joint1(self):
        if (
            self.direction == momapy.core.elements.Direction.RIGHT
            or self.direction == momapy.core.elements.Direction.DOWN
        ):
            p = self.position + (-self.width / 2, -self.height / 2)
        elif self.direction == momapy.core.elements.Direction.UP:
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == momapy.core.elements.Direction.LEFT:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint2(self):
        if (
            self.direction == momapy.core.elements.Direction.RIGHT
            or self.direction == momapy.core.elements.Direction.UP
        ):
            p = self.position + (-self.width / 2, self.height / 2)
        elif self.direction == momapy.core.elements.Direction.LEFT:
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == momapy.core.elements.Direction.DOWN:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def drawing_elements(self):
        if self.direction == momapy.core.elements.Direction.RIGHT:
            actions = [
                momapy.drawing.MoveTo(self.joint1()),
                momapy.drawing.EllipticalArc(
                    self.joint2(),
                    self.width,
                    self.height / 2,
                    0,
                    0,
                    1,
                ),
            ]
        elif self.direction == momapy.core.elements.Direction.UP:
            actions = [
                momapy.drawing.MoveTo(self.joint1()),
                momapy.drawing.EllipticalArc(
                    self.joint2(),
                    self.width / 2,
                    self.height,
                    0,
                    0,
                    0,
                ),
            ]
        elif self.direction == momapy.core.elements.Direction.LEFT:
            actions = [
                momapy.drawing.MoveTo(self.joint1()),
                momapy.drawing.EllipticalArc(
                    self.joint2(),
                    self.width,
                    self.height / 2,
                    0,
                    0,
                    0,
                ),
            ]
        elif self.direction == momapy.core.elements.Direction.DOWN:
            actions = [
                momapy.drawing.MoveTo(self.joint1()),
                momapy.drawing.EllipticalArc(
                    self.joint2(),
                    self.width / 2,
                    self.height,
                    0,
                    0,
                    0,
                ),
            ]
        drawing_element = momapy.drawing.Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class StraightBarb(momapy.core.layout.Shape):
    """Class for straight barb shapes"""

    position: momapy.geometry.Point
    width: float
    height: float
    direction: momapy.core.elements.Direction

    def joint1(self):
        if (
            self.direction == momapy.core.elements.Direction.RIGHT
            or self.direction == momapy.core.elements.Direction.DOWN
        ):
            p = self.position + (-self.width / 2, -self.height / 2)
        elif self.direction == momapy.core.elements.Direction.UP:
            p = self.position + (0, -self.height / 2)
        elif self.direction == momapy.core.elements.Direction.LEFT:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint2(self):
        if self.direction == momapy.core.elements.Direction.RIGHT:
            p = self.position + (self.width / 2, 0)
        elif (
            self.direction == momapy.core.elements.Direction.UP
            or self.direction == momapy.core.elements.Direction.LEFT
        ):
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == momapy.core.elements.Direction.DOWN:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint3(self):
        if (
            self.direction == momapy.core.elements.Direction.RIGHT
            or self.direction == momapy.core.elements.Direction.UP
        ):
            p = self.position + (-self.width / 2, self.height / 2)
        elif self.direction == momapy.core.elements.Direction.LEFT:
            p = self.position + (-self.width / 2, 0)
        elif self.direction == momapy.core.elements.Direction.DOWN:
            p = self.position + (0, self.height / 2)
        return p

    def drawing_elements(self):
        if self.direction == momapy.core.elements.Direction.RIGHT:
            actions = [
                momapy.drawing.MoveTo(self.joint1()),
                momapy.drawing.LineTo(self.joint2()),
                momapy.drawing.LineTo(self.joint3()),
            ]
        elif self.direction == momapy.core.elements.Direction.UP:
            actions = [
                momapy.drawing.MoveTo(self.joint3()),
                momapy.drawing.LineTo(self.joint1()),
                momapy.drawing.LineTo(self.joint2()),
            ]
        elif self.direction == momapy.core.elements.Direction.LEFT:
            actions = [
                momapy.drawing.MoveTo(self.joint1()),
                momapy.drawing.LineTo(self.joint3()),
                momapy.drawing.LineTo(self.joint2()),
            ]
        elif self.direction == momapy.core.elements.Direction.DOWN:
            actions = [
                momapy.drawing.MoveTo(self.joint1()),
                momapy.drawing.LineTo(self.joint3()),
                momapy.drawing.LineTo(self.joint2()),
            ]
        drawing_element = momapy.drawing.Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class To(momapy.core.layout.Shape):
    """Class for to shapes"""

    position: momapy.geometry.Point
    width: float
    height: float
    direction: momapy.core.elements.Direction

    def joint1(self):
        if (
            self.direction == momapy.core.elements.Direction.RIGHT
            or self.direction == momapy.core.elements.Direction.DOWN
        ):
            p = self.position + (-self.width / 2, -self.height / 2)
        elif self.direction == momapy.core.elements.Direction.UP:
            p = self.position + (0, -self.height / 2)
        elif self.direction == momapy.core.elements.Direction.LEFT:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint2(self):
        if self.direction == momapy.core.elements.Direction.RIGHT:
            p = self.position + (self.width / 2, 0)
        elif (
            self.direction == momapy.core.elements.Direction.UP
            or self.direction == momapy.core.elements.Direction.LEFT
        ):
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == momapy.core.elements.Direction.DOWN:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint3(self):
        if (
            self.direction == momapy.core.elements.Direction.RIGHT
            or self.direction == momapy.core.elements.Direction.UP
        ):
            p = self.position + (-self.width / 2, self.height / 2)
        elif self.direction == momapy.core.elements.Direction.LEFT:
            p = self.position + (-self.width / 2, 0)
        elif self.direction == momapy.core.elements.Direction.DOWN:
            p = self.position + (0, self.height / 2)
        return p

    def drawing_elements(self):
        if self.direction == momapy.core.elements.Direction.RIGHT:
            actions = [
                momapy.drawing.MoveTo(self.joint1()),
                momapy.drawing.EllipticalArc(
                    self.joint2(),
                    self.width,
                    self.height / 2,
                    0,
                    0,
                    0,
                ),
                momapy.drawing.EllipticalArc(
                    self.joint3(),
                    self.width,
                    self.height / 2,
                    0,
                    0,
                    0,
                ),
            ]
        elif self.direction == momapy.core.elements.Direction.UP:
            actions = [
                momapy.drawing.MoveTo(self.joint3()),
                momapy.drawing.EllipticalArc(
                    self.joint1(),
                    self.height,
                    self.width / 2,
                    0,
                    0,
                    0,
                ),
                momapy.drawing.EllipticalArc(
                    self.joint2(),
                    self.height,
                    self.width / 2,
                    0,
                    0,
                    0,
                ),
            ]
        elif self.direction == momapy.core.elements.Direction.LEFT:
            actions = [
                momapy.drawing.MoveTo(self.joint1()),
                momapy.drawing.EllipticalArc(
                    self.joint3(),
                    self.width,
                    self.height / 2,
                    0,
                    0,
                    1,
                ),
                momapy.drawing.EllipticalArc(
                    self.joint2(),
                    self.width,
                    self.height / 2,
                    0,
                    0,
                    1,
                ),
            ]
        elif self.direction == momapy.core.elements.Direction.DOWN:
            actions = [
                momapy.drawing.MoveTo(self.joint1()),
                momapy.drawing.EllipticalArc(
                    self.joint3(),
                    self.height,
                    self.width / 2,
                    0,
                    0,
                    1,
                ),
                momapy.drawing.EllipticalArc(
                    self.joint2(),
                    self.height,
                    self.width / 2,
                    0,
                    0,
                    1,
                ),
            ]

        drawing_element = momapy.drawing.Path(actions=actions)
        return [drawing_element]
