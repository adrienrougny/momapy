import math
from dataclasses import dataclass, field

import momapy.core
import momapy.drawing
import momapy.geometry


@dataclass(frozen=True, kw_only=True)
class Rectangle(momapy.core.NodeLayout):
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


@dataclass(frozen=True, kw_only=True)
class RectangleWithRoundedCorners(momapy.core.NodeLayout):
    rounded_corners: float

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


@dataclass(frozen=True, kw_only=True)
class Ellipse(momapy.core.NodeLayout):
    def border_drawing_element(self):
        ellipse = momapy.drawing.Ellipse(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        return ellipse


@dataclass(frozen=True, kw_only=True)
class RectangleWithCutCorners(momapy.core.NodeLayout):
    cut_corners: float

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


@dataclass(frozen=True, kw_only=True)
class Stadium(momapy.core.NodeLayout):
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
        rectangle = momapy.drawing.Rectangle(
            point=self.position - (self.width / 2, self.height / 2),
            height=self.height,
            width=self.width,
            rx=self.height / 2,
            ry=self.height / 2,
        )
        return rectangle


@dataclass(frozen=True, kw_only=True)
class RectangleWithBottomRoundedCorners(momapy.core.NodeLayout):
    rounded_corners: float

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


@dataclass(frozen=True, kw_only=True)
class CircleWithDiagonalBar(momapy.core.NodeLayout):
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


@dataclass(frozen=True, kw_only=True)
class Hexagon(momapy.core.NodeLayout):
    top_left_angle: float
    top_right_angle: float
    bottom_left_angle: float
    bottom_right_angle: float

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


@dataclass(frozen=True, kw_only=True)
class InvertedHexagon(momapy.core.NodeLayout):
    top_left_angle: float
    top_right_angle: float
    bottom_left_angle: float
    bottom_right_angle: float

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
        return momapy.geometry.get_intersection_of_object_and_line(
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
        return momapy.geometry.get_intersection_of_object_and_line(
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


@dataclass(frozen=True, kw_only=True)
class Parallelogram(momapy.core.NodeLayout):
    angle: float

    def joint1(self):
        angle = math.radians(self.angle)
        offset = abs(self.height / math.tan(angle))
        return self.position + (offset - self.width / 2, -self.height / 2)

    def joint2(self):
        return self.position + (self.width / 2, -self.height / 2)

    def joint3(self):
        angle = math.radians(self.angle)
        offset = abs(self.height / math.tan(angle))
        return self.position + (self.width / 2 - offset, self.height / 2)

    def joint4(self):
        return self.position + (-self.width / 2, self.height / 2)

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.joint1())
            + momapy.drawing.line_to(self.joint2())
            + momapy.drawing.line_to(self.joint3())
            + momapy.drawing.line_to(self.joint4())
            + momapy.drawing.close()
        )
        return path


@dataclass(frozen=True, kw_only=True)
class InvertedParallelogram(momapy.core.NodeLayout):
    angle: float

    def joint1(self):
        return self.position - (self.width / 2, self.height / 2)

    def joint2(self):
        angle = math.radians(self.angle)
        offset = abs(self.height / math.tan(angle))
        return self.position + (self.width / 2 - offset, -self.height / 2)

    def joint3(self):
        return self.position + (self.width / 2, self.height / 2)

    def joint4(self):
        angle = math.radians(self.angle)
        offset = abs(self.height / math.tan(angle))
        return self.position + (offset - self.width / 2, self.height / 2)

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.joint1())
            + momapy.drawing.line_to(self.joint2())
            + momapy.drawing.line_to(self.joint3())
            + momapy.drawing.line_to(self.joint4())
            + momapy.drawing.close()
        )
        return path


@dataclass(frozen=True, kw_only=True)
class CircleWithInsideCircle(momapy.core.NodeLayout):
    sep: float

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


@dataclass(frozen=True, kw_only=True)
class Pointer(momapy.core.NodeLayout):
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    top_angle: float
    bottom_angle: float

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


@dataclass(frozen=True, kw_only=True)
class RectangleWithRoundedCornersAlongsideRectangleWithRoundedCorners(
    momapy.core.NodeLayout
):
    rounded_corners: float
    right_rectangle_width: float

    def joint1(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width - self.rounded_corners,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.rounded_corners - self.height / 2,
        )

    def joint4(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.height / 2 - self.rounded_corners,
        )

    def joint5(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width - self.rounded_corners,
            self.height / 2,
        )

    def joint6(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            self.height / 2,
        )

    def joint7(self):
        return self.position + (
            -self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint8(self):
        return self.position + (
            -self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def joint9(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width + self.rounded_corners,
            self.height / 2,
        )

    def joint10(self):
        return self.position + (
            self.width / 2 - self.rounded_corners,
            -self.height / 2,
        )

    def joint11(self):
        return self.position + (
            self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def joint12(self):
        return self.position + (
            self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint13(self):
        return self.position + (
            self.width / 2 - self.rounded_corners,
            self.height / 2,
        )

    def joint14(self):
        return self.position + (
            self.rounded_corners + self.width / 2 - self.right_rectangle_width,
            self.height / 2,
        )

    def joint15(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.height / 2 - self.rounded_corners,
        )

    def joint16(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.rounded_corners - self.height / 2,
        )

    def border_drawing_element(self):
        left_rectangle = momapy.drawing.Rectangle(
            point=self.position - (self.width / 2, self.height / 2),
            height=self.height,
            width=self.width - self.right_rectangle_width,
            rx=self.rounded_corners,
            ry=self.rounded_corners,
        )
        right_rectangle = momapy.drawing.Rectangle(
            point=self.position
            + (self.width / 2 - self.right_rectangle_width, -self.height / 2),
            height=self.height,
            width=self.right_rectangle_width,
            rx=self.rounded_corners,
            ry=self.rounded_corners,
        )
        group = momapy.drawing.Group(elements=(left_rectangle, right_rectangle))
        return group

    def label_center(self):
        return self.position - (self.right_rectangle_width / 2, 0)


@dataclass(frozen=True, kw_only=True)
class TruncatedRectangleWithLeftRoundedCorners(momapy.core.NodeLayout):
    rounded_corners: float
    vertical_truncation: float  # proportion of total height, number in ]0, 1[
    horizontal_truncation: float  # proportion of total width number in ]0, 1[

    def joint1(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2,
            self.height / 2 - self.vertical_truncation * self.height,
        )

    def joint4(self):
        return self.position + (
            self.width / 2 - self.horizontal_truncation * self.width,
            self.vertical_truncation * self.height - self.height / 2,
        )

    def joint5(self):
        return self.position + (
            self.width / 2 - self.horizontal_truncation * self.width,
            self.height / 2,
        )

    def joint6(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            self.height / 2,
        )

    def joint7(self):
        return self.position + (
            -self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint8(self):
        return self.position + (
            -self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.joint1())
            + momapy.drawing.line_to(self.joint2())
            + momapy.drawing.line_to(self.joint3())
            + momapy.drawing.line_to(self.joint4())
            + momapy.drawing.line_to(self.joint5())
            + momapy.drawing.line_to(self.joint5())
            + momapy.drawing.line_to(self.joint6())
            + momapy.drawing.elliptical_arc(
                self.joint7(),
                self.rounded_corners,
                self.rounded_corners,
                0,
                0,
                1,
            )
            + momapy.drawing.line_to(self.joint8())
            + momapy.drawing.elliptical_arc(
                self.joint1(),
                self.rounded_corners,
                self.rounded_corners,
                0,
                0,
                1,
            )
            + momapy.drawing.close()
        )
        return path


@dataclass(frozen=True, kw_only=True)
class FoxHead(momapy.core.NodeLayout):
    vertical_truncation: float  # proportion of total height, number in ]0, 1[

    def joint1(self):
        return self.position + (
            -self.width / 2,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            0,
            self.vertical_truncation * self.height - self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2,
            -self.height / 2,
        )

    def joint4(self):
        return self.position + (
            self.width / 2,
            self.height / 2 - self.vertical_truncation * self.height,
        )

    def joint5(self):
        return self.position + (0, self.height / 2)

    def joint6(self):
        return self.position + (
            -self.width / 2,
            self.height / 2 - self.vertical_truncation * self.height,
        )

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.joint1())
            + momapy.drawing.line_to(self.joint2())
            + momapy.drawing.line_to(self.joint3())
            + momapy.drawing.line_to(self.joint4())
            + momapy.drawing.line_to(self.joint5())
            + momapy.drawing.line_to(self.joint5())
            + momapy.drawing.line_to(self.joint6())
            + momapy.drawing.close()
        )
        return path


@dataclass(frozen=True, kw_only=True)
class StadiumWithEllipsesWithInsideStadiumWithEllipses(momapy.core.NodeLayout):
    horizontal_proportion: float  # ]0, 0.5[
    sep: float

    def joint1(self):
        return self.position + (
            -self.width / 2 + self.horizontal_proportion * self.width,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2 - self.horizontal_proportion * self.width,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2 - self.horizontal_proportion * self.width,
            self.height / 2,
        )

    def joint4(self):
        return self.position + (
            -self.width / 2 + self.horizontal_proportion * self.width,
            self.height / 2,
        )

    def border_drawing_element(self):
        outer_stadium = momapy.drawing.Path()
        outer_stadium += (
            momapy.drawing.move_to(self.joint1())
            + momapy.drawing.line_to(self.joint2())
            + momapy.drawing.elliptical_arc(
                self.joint3(),
                self.horizontal_proportion * self.width,
                self.height / 2,
                0,
                0,
                1,
            )
            + momapy.drawing.line_to(self.joint4())
            + momapy.drawing.elliptical_arc(
                self.joint1(),
                self.horizontal_proportion * self.width,
                self.height / 2,
                0,
                0,
                1,
            )
            + momapy.drawing.close()
        )
        inner_joint1 = self.joint1() + (0, self.sep)
        inner_joint2 = self.joint2() + (0, self.sep)
        inner_joint3 = self.joint3() + (0, -self.sep)
        inner_joint4 = self.joint4() + (0, -self.sep)
        inner_rx = self.horizontal_proportion * self.width - self.sep
        inner_ry = self.height / 2 - self.sep
        inner_stadium = momapy.drawing.Path()
        inner_stadium += (
            momapy.drawing.move_to(inner_joint1)
            + momapy.drawing.line_to(inner_joint2)
            + momapy.drawing.elliptical_arc(
                inner_joint3,
                inner_rx,
                inner_ry,
                0,
                0,
                1,
            )
            + momapy.drawing.line_to(inner_joint4)
            + momapy.drawing.elliptical_arc(
                inner_joint1,
                inner_rx,
                inner_ry,
                0,
                0,
                1,
            )
            + momapy.drawing.close()
        )
        group = momapy.drawing.Group(elements=(outer_stadium, inner_stadium))
        return group


@dataclass(frozen=True, kw_only=True)
class CrossPoint(momapy.core.NodeLayout):
    def border_drawing_element(self):
        horizontal_path = momapy.drawing.Path()
        horizontal_path += momapy.drawing.move_to(
            self.position - (self.width / 2, 0)
        ) + momapy.drawing.line_to(self.position + (self.width / 2, 0))
        vertical_path = momapy.drawing.Path()
        vertical_path += momapy.drawing.move_to(
            self.position - (0, self.height / 2, 0)
        ) + momapy.drawing.line_to(self.position + (0, self.height / 2))
        elements = (horizontal_path, vertical_path)
        group = momapy.drawing.Group(elements=elements)
        return group
