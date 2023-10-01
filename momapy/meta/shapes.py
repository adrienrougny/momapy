import math
import dataclasses
import copy

import momapy.core
import momapy.geometry
import momapy.drawing


@dataclasses.dataclass(frozen=True, kw_only=True)
class Shape(momapy.core.LayoutElement):
    def childless(self):
        return copy.deepcopy(self)

    def children(self):
        return []


@dataclasses.dataclass(frozen=True, kw_only=True)
class Rectangle(Shape):
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
        actions.append(momapy.drawing.LineTo(self.joint4()))
        if self.bottom_right_rx != 0 and self.bottom_right_ry != 0:
            if self.bottom_right_rounded_or_cut == "cut":
                actions.append(momapy.drawing.LineTo(self.joint5()))
            elif self.bottom_right_rounded_or_cut == "rounded":
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
        actions.append(momapy.drawing.LineTo(self.joint6()))
        if self.bottom_left_rx != 0 and self.bottom_left_ry != 0:
            if self.bottom_left_rounded_or_cut == "cut":
                actions.append(momapy.drawing.LineTo(self.joint7()))
            elif self.bottom_left_rounded_or_cut == "rounded":
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
        actions.append(momapy.drawing.LineTo(self.joint8()))
        if self.top_left_rx != 0 and self.top_left_ry != 0:
            if self.top_left_rounded_or_cut == "rounded":
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
        actions.append(momapy.drawing.ClosePath())
        drawing_element = momapy.drawing.Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Ellipse(Shape):
    position: momapy.geometry.Point
    width: float
    height: float

    def drawing_elements(self):
        drawing_element = momapy.drawing.Ellipse(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Stadium(Shape):
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
class Hexagon(Shape):
    position: momapy.geometry.Point
    width: float
    height: float
    left_angle: float = 45.0
    right_angle: float = 45.0

    def joint1(self):
        if self.left_angle > 90:
            return self.position + (-self.width / 2, -self.height / 2)
        angle = math.radians(self.left_angle)
        side_length = abs(self.height / (math.tan(angle)))
        return self.position + (-self.width / 2 + side_length, -self.height / 2)

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
        return p

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
class TurnedHexagon(Shape):
    position: momapy.geometry.Point
    width: float
    height: float

    top_angle: float = 45.0
    bottom_angle: float = 45.0

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
class Parallelogram(Shape):
    position: momapy.geometry.Point
    width: float
    height: float

    angle: float  # degrees

    def joint1(self):
        if self.angle >= 90:
            return self.position + (-self.width / 2, -self.height / 2)
        angle = math.radians(self.angle)
        side_length = abs(self.height / math.tan(angle))
        return self.position + (-self.width / 2 + side_length, -self.height / 2)

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
class CrossPoint(Shape):
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
class Triangle(Shape):
    position: momapy.geometry.Point
    width: float
    height: float
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT

    def joint1(self):
        if (
            self.direction == momapy.core.Direction.RIGHT
            or self.direction == momapy.core.Direction.DOWN
        ):
            p = self.position + (-self.width / 2, -self.height / 2)
        elif self.direction == momapy.core.Direction.UP:
            p = self.position + (0, -self.height / 2)
        elif self.direction == momapy.core.Direction.LEFT:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint2(self):
        if self.direction == momapy.core.Direction.RIGHT:
            p = self.position + (self.width / 2, 0)
        elif (
            self.direction == momapy.core.Direction.UP
            or self.direction == momapy.core.Direction.LEFT
        ):
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == momapy.core.Direction.DOWN:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint3(self):
        if (
            self.direction == momapy.core.Direction.RIGHT
            or self.direction == momapy.core.Direction.UP
        ):
            p = self.position + (-self.width / 2, self.height / 2)
        elif self.direction == momapy.core.Direction.LEFT:
            p = self.position + (-self.width / 2, 0)
        elif self.direction == momapy.core.Direction.DOWN:
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
class Diamond(Shape):
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
class Bar(Shape):
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
class ArcBarb(Shape):
    position: momapy.geometry.Point
    width: float
    height: float
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT

    def joint1(self):
        if (
            self.direction == momapy.core.Direction.RIGHT
            or self.direction == momapy.core.Direction.DOWN
        ):
            p = self.position + (-self.width / 2, -self.height / 2)
        elif self.direction == momapy.core.Direction.UP:
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == momapy.core.Direction.LEFT:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint2(self):
        if (
            self.direction == momapy.core.Direction.RIGHT
            or self.direction == momapy.core.Direction.UP
        ):
            p = self.position + (-self.width / 2, self.height / 2)
        elif self.direction == momapy.core.Direction.LEFT:
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == momapy.core.Direction.DOWN:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def drawing_elements(self):
        if self.direction == momapy.core.Direction.RIGHT:
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
        elif self.direction == momapy.core.Direction.UP:
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
        elif self.direction == momapy.core.Direction.LEFT:
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
        elif self.direction == momapy.core.Direction.DOWN:
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
class StraightBarb(Shape):
    position: momapy.geometry.Point
    width: float
    height: float
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT

    def joint1(self):
        if (
            self.direction == momapy.core.Direction.RIGHT
            or self.direction == momapy.core.Direction.DOWN
        ):
            p = self.position + (-self.width / 2, -self.height / 2)
        elif self.direction == momapy.core.Direction.UP:
            p = self.position + (0, -self.height / 2)
        elif self.direction == momapy.core.Direction.LEFT:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint2(self):
        if self.direction == momapy.core.Direction.RIGHT:
            p = self.position + (self.width / 2, 0)
        elif (
            self.direction == momapy.core.Direction.UP
            or self.direction == momapy.core.Direction.LEFT
        ):
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == momapy.core.Direction.DOWN:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint3(self):
        if (
            self.direction == momapy.core.Direction.RIGHT
            or self.direction == momapy.core.Direction.UP
        ):
            p = self.position + (-self.width / 2, self.height / 2)
        elif self.direction == momapy.core.Direction.LEFT:
            p = self.position + (-self.width / 2, 0)
        elif self.direction == momapy.core.Direction.DOWN:
            p = self.position + (0, self.height / 2)
        return p

    def drawing_elements(self):
        if self.direction == momapy.core.Direction.RIGHT:
            actions = [
                momapy.drawing.MoveTo(self.joint1()),
                momapy.drawing.LineTo(self.joint2()),
                momapy.drawing.LineTo(self.joint3()),
            ]
        elif self.direction == momapy.core.Direction.UP:
            actions = [
                momapy.drawing.MoveTo(self.joint3()),
                momapy.drawing.LineTo(self.joint1()),
                momapy.drawing.LineTo(self.joint2()),
            ]
        elif self.direction == momapy.core.Direction.LEFT:
            actions = [
                momapy.drawing.MoveTo(self.joint1()),
                momapy.drawing.LineTo(self.joint3()),
                momapy.drawing.LineTo(self.joint2()),
            ]
        elif self.direction == momapy.core.Direction.DOWN:
            actions = [
                momapy.drawing.MoveTo(self.joint1()),
                momapy.drawing.LineTo(self.joint3()),
                momapy.drawing.LineTo(self.joint2()),
            ]
        drawing_element = momapy.drawing.Path(actions=actions)
        return [drawing_element]


@dataclasses.dataclass(frozen=True, kw_only=True)
class To(Shape):
    position: momapy.geometry.Point
    width: float
    height: float
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT

    def joint1(self):
        if (
            self.direction == momapy.core.Direction.RIGHT
            or self.direction == momapy.core.Direction.DOWN
        ):
            p = self.position + (-self.width / 2, -self.height / 2)
        elif self.direction == momapy.core.Direction.UP:
            p = self.position + (0, -self.height / 2)
        elif self.direction == momapy.core.Direction.LEFT:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint2(self):
        if self.direction == momapy.core.Direction.RIGHT:
            p = self.position + (self.width / 2, 0)
        elif (
            self.direction == momapy.core.Direction.UP
            or self.direction == momapy.core.Direction.LEFT
        ):
            p = self.position + (self.width / 2, self.height / 2)
        elif self.direction == momapy.core.Direction.DOWN:
            p = self.position + (self.width / 2, -self.height / 2)
        return p

    def joint3(self):
        if (
            self.direction == momapy.core.Direction.RIGHT
            or self.direction == momapy.core.Direction.UP
        ):
            p = self.position + (-self.width / 2, self.height / 2)
        elif self.direction == momapy.core.Direction.LEFT:
            p = self.position + (-self.width / 2, 0)
        elif self.direction == momapy.core.Direction.DOWN:
            p = self.position + (0, self.height / 2)
        return p

    def drawing_elements(self):
        if self.direction == momapy.core.Direction.RIGHT:
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
        elif self.direction == momapy.core.Direction.UP:
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
        elif self.direction == momapy.core.Direction.LEFT:
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
        elif self.direction == momapy.core.Direction.DOWN:
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
