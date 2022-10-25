import math
from dataclasses import dataclass, field

import momapy.core
import momapy.drawing
import momapy.geometry


@dataclass(frozen=True)
class Rectangle(momapy.core.NodeLayout):
    def north_west(self):
        return momapy.geometry.Point(
            self.x - self.width / 2, self.y - self.height / 2
        )

    def west(self):
        return momapy.geometry.Point(self.x - self.width / 2, self.y)

    def south_west(self):
        return momapy.geometry.Point(
            self.x - self.width / 2, self.y + self.height / 2
        )

    def south(self):
        return momapy.geometry.Point(self.x, self.y + self.height / 2)

    def south_east(self):
        return momapy.geometry.Point(
            self.x + self.width / 2, self.y + self.height / 2
        )

    def east(self):
        return momapy.geometry.Point(self.x + self.width / 2, self.y)

    def north_east(self):
        return momapy.geometry.Point(
            self.x + self.width / 2, self.y - self.height / 2
        )

    def north(self):
        return momapy.geometry.Point(self.x, self.y - self.height / 2)

    def center(self):
        return momapy.geometry.Point(self.x, self.y)

    def label_center(self):
        return self.center()

    def border_drawing_element(self):
        rectangle = momapy.drawing.Rectangle(
            point=self.north_west(),
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
        return self.self_bbox().north_west()

    def west(self):
        return self.self_bbox().west()

    def south_west(self):
        return self.self_bbox().south_west()

    def south(self):
        return self.self_bbox().south()

    def south_east(self):
        return self.self_bbox().south_east()

    def east(self):
        return self.self_bbox().east()

    def north_east(self):
        return self.self_bbox().north_east()

    def north(self):
        return self.self_bbox().north()

    def center(self):
        return self.self_bbox().center()

    def label_center(self):
        return self.center()

    def border_drawing_element(self):
        rectangle = momapy.drawing.Rectangle(
            point=momapy.geometry.Point(
                self.x - self.width / 2, self.y - self.height / 2
            ),
            height=self.height,
            width=self.width,
            rx=self.rounded_corners,
            ry=self.rounded_corners,
        )
        return rectangle


@dataclass(frozen=True)
class Ellipse(momapy.core.NodeLayout):
    def north_west(self):
        return self.self_bbox().north_west()

    def west(self):
        return self.self_bbox().west()

    def south_west(self):
        return self.self_bbox().south_west()

    def south(self):
        return self.self_bbox().south()

    def south_east(self):
        return self.self_bbox().south_east()

    def east(self):
        return self.self_bbox().east()

    def north_east(self):
        return self.self_bbox().north_east()

    def north(self):
        return self.self_bbox().north()

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
        return self.self_bbox().north_west()

    def west(self):
        return self.position - (self.width / 2, 0)

    def south_west(self):
        return self.self_bbox().south_west()

    def south(self):
        return self.position + (0, self.height / 2)

    def south_east(self):
        return self.self_bbox().south_east()

    def east(self):
        return self.position + (self.width / 2, 0)

    def north_east(self):
        return self.self_bbox().north_east()

    def north(self):
        return self.position - (0, self.height / 2)

    def center(self):
        return self.position

    def label_center(self):
        return self.center()

    def north_north_west(self):
        return self.north() + (self.cut_corners - self.width / 2, 0)

    def north_north_east(self):
        return self.north() + (self.width / 2 - self.cut_corners, 0)

    def east_north_east(self):
        return self.east() + (0, self.cut_corners - self.height / 2, 0)

    def east_south_east(self):
        return self.east() + (0, self.height / 2 - self.cut_corners)

    def south_south_east(self):
        return self.south() + (self.width / 2 - self.cut_corners, 0)

    def south_south_west(self):
        return self.south() + (self.cut_corners - self.width / 2, 0)

    def west_south_west(self):
        return self.west() + (0, self.height / 2 - self.cut_corners, 0)

    def west_north_west(self):
        return self.west() + (0, self.cut_corners - self.height / 2, 0)

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.north_north_west())
            + momapy.drawing.line_to(self.north_north_east())
            + momapy.drawing.line_to(self.east_north_east())
            + momapy.drawing.line_to(self.east_south_east())
            + momapy.drawing.line_to(self.south_south_east())
            + momapy.drawing.line_to(self.south_south_west())
            + momapy.drawing.line_to(self.west_south_west())
            + momapy.drawing.line_to(self.west_north_west())
            + momapy.drawing.close()
        )
        return path


@dataclass(frozen=True)
class Stadium(momapy.core.NodeLayout):
    def north_west(self):
        return self.self_bbox().north_west() + (self.height / 2, 0)

    def west(self):
        return self.self_bbox().west()

    def south_west(self):
        return self.self_bbox().south_west() + (self.height / 2, 0)

    def south(self):
        return self.self_bbox().south()

    def south_east(self):
        return self.self_bbox().south_east() - (self.height / 2, 0)

    def east(self):
        return self.self_bbox().east()

    def north_east(self):
        return self.self_bbox().north_east() - (self.height / 2, 0)

    def north(self):
        return self.self_bbox().north()

    def center(self):
        return momapy.geometry.Point(self.x, self.y)

    def label_center(self):
        return self.center()

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.north_west())
            + momapy.drawing.line_to(self.north_east())
            + momapy.drawing.elliptical_arc(
                self.south_east(), self.height / 2, self.height / 2, 0, 0, 1
            )
            + momapy.drawing.line_to(self.south_west())
            + momapy.drawing.elliptical_arc(
                self.north_west(), self.height / 2, self.height / 2, 0, 0, 1
            )
            + momapy.drawing.close()
        )
        return path


@dataclass(frozen=True)
class RectangleWithBottomRoundedCorners(momapy.core.NodeLayout):
    rounded_corners: float = 0

    def north_west(self):
        return self.self_bbox().north_west()

    def west(self):
        return self.self_bbox().west()

    def south_west(self):
        return self.self_bbox().south_west()

    def south(self):
        return self.self_bbox().south()

    def south_east(self):
        return self.self_bbox().south_east()

    def east(self):
        return self.self_bbox().east()

    def north_east(self):
        return self.self_bbox().north_east()

    def north(self):
        return self.self_bbox().north()

    def east_south_east(self):
        return self.south_east() - (0, self.rounded_corners)

    def south_south_east(self):
        return self.south_east() - (self.rounded_corners, 0)

    def south_south_west(self):
        return self.south_west() + (self.rounded_corners, 0)

    def west_south_west(self):
        return self.south_west() - (0, self.rounded_corners)

    def center(self):
        return self.self_bbox().center()

    def label_center(self):
        return self.center()

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.north_west())
            + momapy.drawing.line_to(self.north_east())
            + momapy.drawing.line_to(self.east_south_east())
            + momapy.drawing.elliptical_arc(
                self.south_south_east(),
                self.rounded_corners,
                self.rounded_corners,
                0,
                0,
                1,
            )
            + momapy.drawing.line_to(self.south_south_west())
            + momapy.drawing.elliptical_arc(
                self.west_south_west(),
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
        return self.self_bbox().north_west()

    def west(self):
        return self.self_bbox().west()

    def south_west(self):
        return self.self_bbox().south_west()

    def south(self):
        return self.self_bbox().south()

    def south_east(self):
        return self.self_bbox().south_east()

    def east(self):
        return self.self_bbox().east()

    def north_east(self):
        return self.self_bbox().north_east()

    def north(self):
        return self.self_bbox().north()

    def center(self):
        return self.self_bbox().center()

    def label_center(self):
        return self.center()

    def border_drawing_element(self):
        circle = momapy.drawing.Ellipse(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        bar = momapy.drawing.Path()
        bar += momapy.drawing.move_to(
            self.self_bbox().south_west()
        ) + momapy.drawing.line_to(self.self_bbox().north_east())
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
        angle = math.radians(self.top_left_angle)
        side_length = abs(self.height / (2 * math.sin(angle)))
        p = momapy.geometry.Point(
            self.west().x + side_length * math.cos(angle),
            self.west().y - self.height / 2,
        )
        return p

    def west(self):
        return self.position - (self.width / 2, 0)

    def south_west(self):
        angle = math.radians(self.bottom_left_angle)
        side_length = self.height / (2 * math.sin(angle))
        p = momapy.geometry.Point(
            self.west().x + side_length * math.cos(angle),
            self.west().y + self.height / 2,
        )
        return p

    def south(self):
        return self.position + (0, self.height / 2)

    def south_east(self):
        angle = math.radians(self.bottom_right_angle)
        side_length = self.height / (2 * math.sin(angle))
        p = momapy.geometry.Point(
            self.east().x - side_length * math.cos(angle),
            self.east().y + self.height / 2,
        )
        return p

    def east(self):
        return self.position + (self.width / 2, 0)

    def north_east(self):
        angle = math.radians(self.top_right_angle)
        side_length = self.height / (2 * math.sin(angle))
        p = momapy.geometry.Point(
            self.east().x - side_length * math.cos(angle),
            self.east().y - self.height / 2,
        )
        return p

    def north(self):
        return self.position - (0, self.height / 2)

    def center(self):
        return self.position

    def label_center(self):
        return self.center()

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.north_west())
            + momapy.drawing.line_to(self.north_east())
            + momapy.drawing.line_to(self.east())
            + momapy.drawing.line_to(self.south_east())
            + momapy.drawing.line_to(self.south_west())
            + momapy.drawing.line_to(self.west())
            + momapy.drawing.close()
        )
        return path


@dataclass(frozen=True)
class InvertedHexagon(momapy.core.NodeLayout):
    top_left_angle: float = 50.0
    top_right_angle: float = 50.0
    bottom_left_angle: float = 50.0
    bottom_right_angle: float = 50.0

    def inner_left(self):
        d = 100
        top_left_angle = math.radians(self.top_left_angle)
        bottom_left_angle = math.radians(self.bottom_left_angle)
        top_left_line = momapy.geometry.Line(
            self.north_west(),
            self.north_west()
            + (d * math.cos(top_left_angle), d * math.sin(top_left_angle)),
        )
        bottom_left_line = momapy.geometry.Line(
            self.south_west(),
            self.south_west()
            + (
                d * math.cos(bottom_left_angle),
                -d * math.sin(bottom_left_angle),
            ),
        )
        return momapy.geometry.get_intersection_of_lines(
            top_left_line, bottom_left_line
        )[0]

    def inner_right(self):
        d = 100
        top_right_angle = math.radians(self.top_right_angle)
        bottom_right_angle = math.radians(self.bottom_right_angle)
        top_right_line = momapy.geometry.Line(
            self.north_east(),
            self.north_east()
            + (-d * math.cos(top_right_angle), d * math.sin(top_right_angle)),
        )
        bottom_right_line = momapy.geometry.Line(
            self.south_east(),
            self.south_east()
            - (
                d * math.cos(bottom_right_angle),
                d * math.sin(bottom_right_angle),
            ),
        )
        return momapy.geometry.get_intersection_of_lines(
            top_right_line, bottom_right_line
        )[0]

    def north_west(self):
        return self.position - (self.width / 2, self.height / 2)

    def west(self):
        return self.position - (self.width / 2, 0)

    def south_west(self):
        return self.position + (-self.width / 2, self.height / 2)

    def south(self):
        return self.position + (0, self.height / 2)

    def south_east(self):
        return self.position + (self.width / 2, self.height / 2)

    def east(self):
        return self.position + (self.width / 2, 0)

    def north_east(self):
        return self.position + (self.width / 2, -self.height / 2)

    def north(self):
        return self.position - (0, self.height / 2)

    def center(self):
        return self.position

    def label_center(self):
        return self.center()

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.north_west())
            + momapy.drawing.line_to(self.north_east())
            + momapy.drawing.line_to(self.inner_right())
            + momapy.drawing.line_to(self.south_east())
            + momapy.drawing.line_to(self.south_west())
            + momapy.drawing.line_to(self.inner_left())
            + momapy.drawing.close()
        )
        return path


@dataclass(frozen=True)
class CircleWithInsideCircle(momapy.core.NodeLayout):
    sep: float = 2

    def north_west(self):
        return self.self_bbox().north_west()

    def west(self):
        return self.self_bbox().west()

    def south_west(self):
        return self.self_bbox().south_west()

    def south(self):
        return self.self_bbox().south()

    def south_east(self):
        return self.self_bbox().south_east()

    def east(self):
        return self.self_bbox().east()

    def north_east(self):
        return self.self_bbox().north_east()

    def north(self):
        return self.self_bbox().north()

    def center(self):
        return self.position

    def label_center(self):
        return self.center()

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
        if self.direction == momapy.core.Direction.UP:
            angle = math.radians(self.top_angle)
            side_length = abs(self.width / (2 * math.sin(angle)))
            return self.position + (
                -self.width / 2,
                -self.height / 2 + side_length * math.cos(angle),
            )
        elif self.direction == momapy.core.Direction.LEFT:
            angle = math.radians(self.top_angle)
            side_length = abs(self.height / (2 * math.sin(angle)))
            return self.position + (
                -self.width / 2 + side_length * math.cos(angle),
                -self.height / 2,
            )
        else:
            return self.position - (self.width / 2, self.height / 2)

    def west(self):
        return momapy.geometry.Point(self.x - self.width / 2, self.y)

    def south_west(self):
        if self.direction == momapy.core.Direction.DOWN:
            angle = math.radians(self.bottom_angle)
            side_length = abs(self.width / (2 * math.sin(angle)))
            return self.position + (
                -self.width / 2,
                +self.height / 2 - side_length * math.cos(angle),
            )
        elif self.direction == momapy.core.Direction.LEFT:
            angle = math.radians(self.bottom_angle)
            side_length = abs(self.height / (2 * math.sin(angle)))
            return self.position + (
                -self.width / 2 + side_length * math.cos(angle),
                self.height / 2,
            )
        else:
            return self.position + (-self.width / 2, self.height / 2)

    def south(self):
        return momapy.geometry.Point(self.x, self.y + self.height / 2)

    def south_east(self):
        if self.direction == momapy.core.Direction.DOWN:
            angle = math.radians(self.bottom_angle)
            side_length = abs(self.width / (2 * math.sin(angle)))
            return self.position + (
                self.width / 2,
                self.height / 2 - side_length * math.cos(angle),
            )
        elif (
            self.direction == momapy.core.Direction.UP
            or self.direction == momapy.core.Direction.LEFT
        ):
            return self.position + (self.width / 2, self.height / 2)
        else:
            angle = math.radians(self.bottom_angle)
            side_length = abs(self.height / (2 * math.sin(angle)))
            return self.position + (
                self.width / 2 - side_length * math.cos(angle),
                self.height / 2,
            )

    def east(self):
        return momapy.geometry.Point(self.x + self.width / 2, self.y)

    def north_east(self):
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
        else:
            angle = math.radians(self.top_angle)
            side_length = abs(self.height / (2 * math.sin(angle)))
            return self.position + (
                self.width / 2 - side_length * math.cos(angle),
                -self.height / 2,
            )

    def north(self):
        return momapy.geometry.Point(self.x, self.y - self.height / 2)

    def center(self):
        return self.position

    def label_center(self):
        return self.center()

    def border_drawing_element(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.north_west())
            + momapy.drawing.line_to(self.north())
            + momapy.drawing.line_to(self.north_east())
            + momapy.drawing.line_to(self.east())
            + momapy.drawing.line_to(self.south_east())
            + momapy.drawing.line_to(self.south())
            + momapy.drawing.line_to(self.south_west())
            + momapy.drawing.line_to(self.west())
            + momapy.drawing.close()
        )
        return path
