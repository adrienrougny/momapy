import math
from dataclasses import dataclass, field

import momapy.core
import momapy.drawing
import momapy.geometry


@dataclass(frozen=True)
class Rectangle(momapy.core.NodeLayout):
    def north_west(self):
        return momapy.core.NodeLayout.north_west(self)

    def north(self):
        return momapy.core.NodeLayout.north(self)

    def north_east(self):
        return momapy.core.NodeLayout.north_east(self)

    def east(self):
        return momapy.core.NodeLayout.east(self)

    def south_east(self):
        return momapy.core.NodeLayout.south_east(self)

    def south(self):
        return momapy.core.NodeLayout.south(self)

    def south_west(self):
        return momapy.core.NodeLayout.south_west(self)

    def west(self):
        return momapy.core.NodeLayout.west(self)

    def center(self):
        return momapy.core.NodeLayout.center(self)

    def label_center(self):
        return momapy.core.NodeLayout.label_center(self)

    def joint1(self):
        return self.position - (self.width / 2, self.height / 2)

    def joint2(self):
        return self.position + (self.width / 2, -self.height / 2)

    def joint3(self):
        return self.position + (self.width / 2, self.height / 2)

    def joint4(self):
        return self.position - (self.width / 2, -self.height / 2)

    def border_drawing_element(self):
        rectangle = momapy.drawing.Rectangle(
            point=self.joint1(),
            height=self.height,
            width=self.width,
            rx=0,
            ry=0,
        )
        return rectangle


@dataclass(frozen=True)
class RectangleWithRoundedCorners(momapy.core.NodeLayout):
    rounded_corners: float = 10

    def north_west(self):
        return momapy.core.NodeLayout.north_west(self)

    def west(self):
        return momapy.core.NodeLayout.west(self)

    def south_west(self):
        return momapy.core.NodeLayout.south_west(self)

    def south(self):
        return momapy.core.NodeLayout.south(self)

    def south_east(self):
        return momapy.core.NodeLayout.south_east(self)

    def east(self):
        return momapy.core.NodeLayout.east(self)

    def north_east(self):
        return momapy.core.NodeLayout.north_east(self)

    def north(self):
        return momapy.core.NodeLayout.north(self)

    def center(self):
        return momapy.core.NodeLayout.center(self)

    def label_center(self):
        return momapy.core.NodeLayout.label_center(self)

    def joint1(self):
        return self.position - (
            self.width / 2 - self.rounded_corners,
            self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2 - self.rounded_corners,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def joint4(self):
        return self.position + (
            self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint5(self):
        return self.position + (
            self.width / 2 - self.rounded_corners,
            self.height / 2,
        )

    def joint6(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            self.height / 2,
        )

    def joint7(self):
        return self.position - (
            self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def joint8(self):
        return self.position - (
            self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def border_drawing_element(self):
        rectangle = momapy.drawing.Rectangle(
            point=self.position - (self.width / 2, self.height / 2),
            height=self.height,
            width=self.width,
            rx=self.rounded_corners,
            ry=self.rounded_corners,
        )
        return rectangle


@dataclass(frozen=True)
class Ellipse(momapy.core.NodeLayout):
    def north_west(self):
        return momapy.core.NodeLayout.north_west(self)

    def west(self):
        return momapy.core.NodeLayout.west(self)

    def south_west(self):
        return momapy.core.NodeLayout.south_west(self)

    def south(self):
        return momapy.core.NodeLayout.south(self)

    def south_east(self):
        return momapy.core.NodeLayout.south_east(self)

    def east(self):
        return momapy.core.NodeLayout.east(self)

    def north_east(self):
        return momapy.core.NodeLayout.north_east(self)

    def north(self):
        return momapy.core.NodeLayout.north(self)

    def center(self):
        return momapy.geometry.Point(self.x, self.y)

    def label_center(self):
        return self.center()

    def border_drawing_element(self):
        ellipse = momapy.drawing.Ellipse(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        return ellipse


@dataclass(frozen=True)
class RectangleWithCutCorners(momapy.core.NodeLayout):
    cut_corners: float = 0

    def north_west(self):
        return momapy.core.NodeLayout.north_west(self)

    def west(self):
        return momapy.core.NodeLayout.west(self)

    def south_west(self):
        return momapy.core.NodeLayout.south_west(self)

    def south(self):
        return momapy.core.NodeLayout.south(self)

    def south_east(self):
        return momapy.core.NodeLayout.south_east(self)

    def east(self):
        return momapy.core.NodeLayout.east(self)

    def north_east(self):
        return momapy.core.NodeLayout.north_east(self)

    def north(self):
        return momapy.core.NodeLayout.north(self)

    def center(self):
        return momapy.core.NodeLayout.center(self)

    def label_center(self):
        return momapy.core.NodeLayout.label_center(self)

    def joint1(self):
        return self.position - (
            self.width / 2 - self.cut_corners,
            self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2 - self.cut_corners,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2,
            self.cut_corners - self.height / 2,
        )

    def joint4(self):
        return self.position + (
            self.width / 2,
            self.height / 2 - self.cut_corners,
        )

    def joint5(self):
        return self.position + (
            self.width / 2 - self.cut_corners,
            self.height / 2,
        )

    def joint6(self):
        return self.position + (
            self.cut_corners - self.width / 2,
            self.height / 2,
        )

    def joint7(self):
        return self.position - (
            self.width / 2,
            self.cut_corners - self.height / 2,
        )

    def joint8(self):
        return self.position - (
            self.width / 2,
            self.height / 2 - self.cut_corners,
        )

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.joint1())
            + momapy.drawing.line_to(self.joint2())
            + momapy.drawing.line_to(self.joint3())
            + momapy.drawing.line_to(self.joint4())
            + momapy.drawing.line_to(self.joint5())
            + momapy.drawing.line_to(self.joint6())
            + momapy.drawing.line_to(self.joint7())
            + momapy.drawing.line_to(self.joint8())
            + momapy.drawing.close()
        )
        return path


@dataclass(frozen=True)
class Stadium(momapy.core.NodeLayout):
    def north_west(self):
        return momapy.core.NodeLayout.north_west(self)

    def west(self):
        return momapy.core.NodeLayout.west(self)

    def south_west(self):
        return momapy.core.NodeLayout.south_west(self)

    def south(self):
        return momapy.core.NodeLayout.south(self)

    def south_east(self):
        return momapy.core.NodeLayout.south_east(self)

    def east(self):
        return momapy.core.NodeLayout.east(self)

    def north_east(self):
        return momapy.core.NodeLayout.north_east(self)

    def north(self):
        return momapy.core.NodeLayout.north(self)

    def center(self):
        return momapy.core.NodeLayout.center(self)

    def label_center(self):
        return momapy.core.NodeLayout.label_center(self)

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

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.joint1())
            + momapy.drawing.line_to(self.joint2())
            + momapy.drawing.elliptical_arc(
                self.joint3(),
                self.height / 2,
                self.height / 2,
                0,
                0,
                1,
            )
            + momapy.drawing.line_to(self.joint4())
            + momapy.drawing.elliptical_arc(
                self.joint1(),
                self.height / 2,
                self.height / 2,
                0,
                0,
                1,
            )
            + momapy.drawing.close()
        )
        return path


@dataclass(frozen=True)
class RectangleWithBottomRoundedCorners(momapy.core.NodeLayout):
    rounded_corners: float = 0

    def north_west(self):
        return momapy.core.NodeLayout.north_west(self)

    def west(self):
        return momapy.core.NodeLayout.west(self)

    def south_west(self):
        return momapy.core.NodeLayout.south_west(self)

    def south(self):
        return momapy.core.NodeLayout.south(self)

    def south_east(self):
        return momapy.core.NodeLayout.south_east(self)

    def east(self):
        return momapy.core.NodeLayout.east(self)

    def north_east(self):
        return momapy.core.NodeLayout.north_east(self)

    def north(self):
        return momapy.core.NodeLayout.north(self)

    def center(self):
        return momapy.core.NodeLayout.center(self)

    def label_center(self):
        return self.center()

    def joint1(self):
        return self.position - (
            self.width / 2,
            self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint4(self):
        return self.position + (
            self.width / 2 - self.rounded_corners,
            self.height / 2,
        )

    def joint5(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            self.height / 2,
        )

    def joint6(self):
        return self.position - (
            self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.joint1())
            + momapy.drawing.line_to(self.joint2())
            + momapy.drawing.line_to(self.joint3())
            + momapy.drawing.elliptical_arc(
                self.joint4(),
                self.rounded_corners,
                self.rounded_corners,
                0,
                0,
                1,
            )
            + momapy.drawing.line_to(self.joint5())
            + momapy.drawing.elliptical_arc(
                self.joint6(),
                self.rounded_corners,
                self.rounded_corners,
                0,
                0,
                1,
            )
            + momapy.drawing.close()
        )
        return path


@dataclass(frozen=True)
class CircleWithDiagonalBar(momapy.core.NodeLayout):
    def north_west(self):
        return momapy.core.NodeLayout.north_west(self)

    def west(self):
        return momapy.core.NodeLayout.west(self)

    def south_west(self):
        return momapy.core.NodeLayout.south_west(self)

    def south(self):
        return momapy.core.NodeLayout.south(self)

    def south_east(self):
        return momapy.core.NodeLayout.south_east(self)

    def east(self):
        return momapy.core.NodeLayout.east(self)

    def north_east(self):
        return momapy.core.NodeLayout.north_east(self)

    def north(self):
        return momapy.core.NodeLayout.north(self)

    def center(self):
        return momapy.core.NodeLayout.center(self)

    def label_center(self):
        return self.center()

    def border_drawing_element(self):
        circle = momapy.drawing.Ellipse(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        bar = momapy.drawing.Path()
        bar += momapy.drawing.move_to(
            self.position - (self.width / 2, -self.height / 2)
        ) + momapy.drawing.line_to(
            self.position + (self.width / 2, -self.height / 2)
        )
        elements = (circle, bar)
        group = momapy.drawing.Group(elements=elements)
        return group


@dataclass(frozen=True)
class Hexagon(momapy.core.NodeLayout):
    top_left_angle: float = 50.0
    top_right_angle: float = 50.0
    bottom_left_angle: float = 50.0
    bottom_right_angle: float = 50.0

    def north_west(self):
        return momapy.core.NodeLayout.north_west(self)

    def north(self):
        return momapy.core.NodeLayout.north(self)

    def north_east(self):
        return momapy.core.NodeLayout.north_east(self)

    def east(self):
        return momapy.core.NodeLayout.east(self)

    def south_east(self):
        return momapy.core.NodeLayout.south_east(self)

    def south(self):
        return momapy.core.NodeLayout.south(self)

    def south_west(self):
        return momapy.core.NodeLayout.south_west(self)

    def west(self):
        return momapy.core.NodeLayout.west(self)

    def center(self):
        return momapy.core.NodeLayout.center(self)

    def label_center(self):
        return momapy.core.NodeLayout.label_center(self)

    def joint1(self):
        angle = math.radians(self.top_left_angle)
        side_length = abs(self.height / (2 * math.sin(angle)))
        p = momapy.geometry.Point(
            self.joint6().x + side_length * math.cos(angle),
            self.joint6().y - self.height / 2,
        )
        return p

    def joint2(self):
        angle = math.radians(self.top_right_angle)
        side_length = self.height / (2 * math.sin(angle))
        p = momapy.geometry.Point(
            self.joint3().x - side_length * math.cos(angle),
            self.joint3().y - self.height / 2,
        )
        return p

    def joint3(self):
        return self.position + (self.width / 2, 0)

    def joint4(self):
        angle = math.radians(self.bottom_right_angle)
        side_length = self.height / (2 * math.sin(angle))
        p = momapy.geometry.Point(
            self.joint3().x - side_length * math.cos(angle),
            self.joint3().y + self.height / 2,
        )
        return p

    def joint5(self):
        angle = math.radians(self.bottom_left_angle)
        side_length = self.height / (2 * math.sin(angle))
        p = momapy.geometry.Point(
            self.joint6().x + side_length * math.cos(angle),
            self.joint6().y + self.height / 2,
        )
        return p

    def joint6(self):
        return self.position - (self.width / 2, 0)

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.joint1())
            + momapy.drawing.line_to(self.joint2())
            + momapy.drawing.line_to(self.joint3())
            + momapy.drawing.line_to(self.joint4())
            + momapy.drawing.line_to(self.joint5())
            + momapy.drawing.line_to(self.joint6())
            + momapy.drawing.close()
        )
        return path


@dataclass(frozen=True)
class InvertedHexagon(momapy.core.NodeLayout):
    top_left_angle: float = 50.0
    top_right_angle: float = 50.0
    bottom_left_angle: float = 50.0
    bottom_right_angle: float = 50.0

    def north_west(self):
        return momapy.core.NodeLayout.north_west(self)

    def north(self):
        return momapy.core.NodeLayout.north(self)

    def north_east(self):
        return momapy.core.NodeLayout.north_east(self)

    def east(self):
        return momapy.core.NodeLayout.east(self)

    def south_east(self):
        return momapy.core.NodeLayout.south_east(self)

    def south(self):
        return momapy.core.NodeLayout.south(self)

    def south_west(self):
        return momapy.core.NodeLayout.south_west(self)

    def west(self):
        return momapy.core.NodeLayout.west(self)

    def center(self):
        return momapy.core.NodeLayout.center(self)

    def label_center(self):
        return momapy.core.NodeLayout.label_center(self)

    def joint1(self):
        return self.position - (self.width / 2, self.height / 2)

    def joint2(self):
        return self.position + (self.width / 2, -self.height / 2)

    def joint3(self):
        d = 100
        top_right_angle = math.radians(self.top_right_angle)
        bottom_right_angle = math.radians(self.bottom_right_angle)
        top_right_line = momapy.geometry.Line(
            self.joint2(),
            self.joint2()
            + (-d * math.cos(top_right_angle), d * math.sin(top_right_angle)),
        )
        bottom_right_line = momapy.geometry.Line(
            self.joint4(),
            self.joint4()
            - (
                d * math.cos(bottom_right_angle),
                d * math.sin(bottom_right_angle),
            ),
        )
        return momapy.geometry.get_intersection_of_lines(
            top_right_line, bottom_right_line
        )[0]

    def joint4(self):
        return self.position + (self.width / 2, self.height / 2)

    def joint5(self):
        return self.position + (-self.width / 2, self.height / 2)

    def joint6(self):
        d = 100
        top_left_angle = math.radians(self.top_left_angle)
        bottom_left_angle = math.radians(self.bottom_left_angle)
        top_left_line = momapy.geometry.Line(
            self.joint1(),
            self.joint1()
            + (d * math.cos(top_left_angle), d * math.sin(top_left_angle)),
        )
        bottom_left_line = momapy.geometry.Line(
            self.joint5(),
            self.joint5()
            + (
                d * math.cos(bottom_left_angle),
                -d * math.sin(bottom_left_angle),
            ),
        )
        return momapy.geometry.get_intersection_of_lines(
            top_left_line, bottom_left_line
        )[0]

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.joint1())
            + momapy.drawing.line_to(self.joint2())
            + momapy.drawing.line_to(self.joint3())
            + momapy.drawing.line_to(self.joint4())
            + momapy.drawing.line_to(self.joint5())
            + momapy.drawing.line_to(self.joint6())
            + momapy.drawing.close()
        )
        return path


@dataclass(frozen=True)
class CircleWithInsideCircle(momapy.core.NodeLayout):
    sep: float = 2

    def north_west(self):
        return momapy.core.NodeLayout.north_west(self)

    def west(self):
        return momapy.core.NodeLayout.west(self)

    def south_west(self):
        return momapy.core.NodeLayout.south_west(self)

    def south(self):
        return momapy.core.NodeLayout.south(self)

    def south_east(self):
        return momapy.core.NodeLayout.south_east(self)

    def east(self):
        return momapy.core.NodeLayout.east(self)

    def north_east(self):
        return momapy.core.NodeLayout.north_east(self)

    def north(self):
        return momapy.core.NodeLayout.north(self)

    def center(self):
        return momapy.core.NodeLayout.center(self)

    def label_center(self):
        return momapy.core.NodeLayout.label_center(self)

    def border_drawing_element(self):
        outer_circle = momapy.drawing.Ellipse(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        inner_circle = momapy.drawing.Ellipse(
            point=self.position,
            rx=self.width / 2 - self.sep,
            ry=self.height / 2 - self.sep,
        )
        elements = (outer_circle, inner_circle)
        group = momapy.drawing.Group(elements=elements)
        return group


@dataclass(frozen=True)
class Pointer(momapy.core.NodeLayout):
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    top_angle: float = 50.0
    bottom_angle: float = 50.0

    def north_west(self):
        return momapy.core.NodeLayout.north_west(self)

    def west(self):
        return momapy.core.NodeLayout.west(self)

    def south_west(self):
        return momapy.core.NodeLayout.south_west(self)

    def south(self):
        return momapy.core.NodeLayout.south(self)

    def south_east(self):
        return momapy.core.NodeLayout.south_east(self)

    def east(self):
        return momapy.core.NodeLayout.east(self)

    def north_east(self):
        return momapy.core.NodeLayout.north_east(self)

    def north(self):
        return momapy.core.NodeLayout.north(self)

    def center(self):
        return momapy.core.NodeLayout.center(self)

    def label_center(self):
        return momapy.core.NodeLayout.label_center(self)

    def joint1(self):
        if self.direction == momapy.core.Direction.UP:
            return self.position - (0, self.height / 2)
        elif self.direction == momapy.core.Direction.LEFT:
            angle = math.radians(self.top_angle)
            side_length = abs(self.height / (2 * math.sin(angle)))
            return self.position + (
                -self.width / 2 + side_length * math.cos(angle),
                -self.height / 2,
            )
        else:  # case down, right, or ill defined
            return self.position - (self.width / 2, self.height / 2)

    def joint2(self):
        if self.direction == momapy.core.Direction.UP:
            angle = math.radians(self.top_angle)
            side_length = abs(self.width / (2 * math.sin(angle)))
            return self.position + (
                self.width / 2,
                -self.height / 2 + side_length * math.cos(angle),
            )
        elif (
            self.direction == momapy.core.Direction.DOWN
            or self.direction == momapy.core.Direction.LEFT
        ):
            return self.position + (self.width / 2, -self.height / 2)
        else:  # case right or ill defined
            angle = math.radians(self.top_angle)
            side_length = abs(self.height / (2 * math.sin(angle)))
            return self.position + (
                self.width / 2 - side_length * math.cos(angle),
                -self.height / 2,
            )

    def joint3(self):
        if (
            self.direction == momapy.core.Direction.UP
            or self.direction == momapy.core.Direction.LEFT
        ):
            return self.position + (self.width / 2, self.height / 2)
        elif self.direction == momapy.core.Direction.DOWN:
            angle = math.radians(self.bottom_angle)
            side_length = abs(self.width / (2 * math.sin(angle)))
            return self.position + (
                self.width / 2,
                self.height / 2 - side_length * math.cos(angle),
            )
        else:  # case right or ill defined
            return self.position + (self.width / 2, 0)

    def joint4(self):
        if self.direction == momapy.core.Direction.UP:
            return self.position + (-self.width / 2, self.height / 2)
        elif self.direction == momapy.core.Direction.DOWN:
            return self.position + (0, self.height / 2)
        elif self.direction == momapy.core.Direction.LEFT:
            angle = math.radians(self.bottom_angle)
            side_length = abs(self.height / (2 * math.sin(angle)))
            return self.position + (
                -self.width / 2 + side_length * math.cos(angle),
                self.height / 2,
            )
        else:  # case right or ill defined
            angle = math.radians(self.bottom_angle)
            side_length = abs(self.height / (2 * math.sin(angle)))
            return self.position + (
                self.width / 2 - side_length * math.cos(angle),
                self.height / 2,
            )

    def joint5(self):
        if self.direction == momapy.core.Direction.UP:
            angle = math.radians(self.top_angle)
            side_length = abs(self.width / (2 * math.sin(angle)))
            return self.position + (
                -self.width / 2,
                -self.height / 2 + side_length * math.cos(angle),
            )
        elif self.direction == momapy.core.Direction.DOWN:
            angle = math.radians(self.bottom_angle)
            side_length = abs(self.width / (2 * math.sin(angle)))
            return self.position + (
                -self.width / 2,
                +self.height / 2 - side_length * math.cos(angle),
            )
        elif self.direction == momapy.core.Direction.LEFT:
            return self.position + (-self.width / 2, 0)
        else:  # case right or ill defined
            return self.position + (-self.width / 2, self.height / 2)

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.joint1())
            + momapy.drawing.line_to(self.joint2())
            + momapy.drawing.line_to(self.joint3())
            + momapy.drawing.line_to(self.joint4())
            + momapy.drawing.line_to(self.joint5())
            + momapy.drawing.close()
        )
        return path


class CrossPoint(momapy.core.NodeLayout):
    def border_drawing_element(self):
        horizontal_path = momapy.drawing.Path()
        horizontal_path += momapy.drawing.move_to(
            self.position - (self.width / 2, 0)
        ) + momapy.drawing.move_to(self.position + (self.width / 2, 0))
        vertical_path = momapy.drawing.Path()
        vertical_path += momapy.drawing.move_to(
            self.position - (0, self.height / 2, 0)
        ) + momapy.drawing.move_to(self.position + (0, self.height / 2))
        elements = (horizontal_path, vertical_path)
        group = momapy.drawing.Group(elements=elements)
        return group
