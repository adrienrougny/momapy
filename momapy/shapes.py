import math
from dataclasses import dataclass, field

import momapy.core
import momapy.drawing
import momapy.geometry

@dataclass(frozen=True)
class Rectangle(momapy.core.NodeLayoutElement):

    def north_west(self):
        return momapy.geometry.Point(
            self.x - self.width/2, self.y - self.height/2)

    def west(self):
        return momapy.geometry.Point(
            self.x - self.width/2, self.y)

    def south_west(self):
        return momapy.geometry.Point(
            self.x - self.width/2, self.y + self.height/2)

    def south(self):
        return momapy.geometry.Point(
            self.x, self.y + self.height/2)

    def south_east(self):
        return momapy.geometry.Point(
            self.x + self.width/2, self.y + self.height/2)

    def east(self):
        return momapy.geometry.Point(
            self.x + self.width/2, self.y)

    def north_east(self):
        return momapy.geometry.Point(
            self.x + self.width/2, self.y - self.height/2)

    def north(self):
        return momapy.geometry.Point(self.x, self.y - self.height/2)

    def center(self):
        return momapy.geometry.Point(self.x, self.y)

    def background_path(self):
        rectangle = momapy.drawing.Rectangle(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            point=self.north_west(),
            height=self.height,
            width=self.width,
            rx=0,
            ry=0
        )
        return rectangle

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        angle = -angle
        if unit == "degrees":
            angle = math.radians(angle)
        angle = momapy.geometry.get_normalized_angle(angle)
        line = momapy.geometry.Line(
            self.center(),
            self.center() + (math.cos(angle), math.sin(angle))
        )
        sectors = [
            (self.north_east(), self.south_east()),
            (self.south_east(), self.south_west()),
            (self.south_west(), self.north_west()),
            (self.north_west(), self.north_east())
        ]
        for sector in sectors:
            if momapy.geometry.is_angle_in_sector(
                    angle, self.center(), sector[0], sector[1]):
                p = momapy.geometry.get_intersection_of_lines(
                        momapy.geometry.Line(sector[0], sector[1]), line)
                return p
        return self.center()

@dataclass(frozen=True)
class RectangleWithRoundedCorners(momapy.core.NodeLayoutElement):
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

    def background_path(self):
        rectangle = momapy.drawing.Rectangle(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            point=momapy.geometry.Point(
                self.x - self.width/2,
                self.y - self.height/2
            ),
            height=self.height,
            width=self.width,
            rx=self.rounded_corners,
            ry=self.rounded_corners
        )
        return rectangle

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)


@dataclass(frozen=True)
class RectangleWithConnectors(momapy.core.NodeLayoutElement):
    left_connector_length: float = 0
    right_connector_length: float = 0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL

    def north_west(self):
        return momapy.geometry.Point(
            self.x - self.width/2, self.y - self.height/2)

    def west(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x - self.width/2, self.y)
        else:
            return momapy.geometry.Point(
                self.x - self.width/2 - self.left_connector_length, self.y)

    def south_west(self):
        return momapy.geometry.Point(
            self.x - self.width/2, self.y + self.height/2)

    def south(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y + self.height/2 + self.right_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y + self.height/2)

    def south_east(self):
        return momapy.geometry.Point(
            self.x + self.width/2, self.y + self.height/2)

    def east(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x + self.width/2, self.y)
        else:
            return momapy.geometry.Point(
                self.x + self.width/2 + self.right_connector_length, self.y)

    def north_east(self):
        return momapy.geometry.Point(
            self.x + self.width/2, self.y - self.height/2)

    def north(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y - self.height/2 - self.left_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y - self.height/2)

    def center(self):
        return momapy.geometry.Point(self.x, self.y)

    def base_left_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y - self.height/2)
        else:
            return momapy.geometry.Point(self.x - self.width/2, self.y)

    def base_right_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y + self.height/2)
        else:
            return momapy.geometry.Point(self.x + self.width/2, self.y)

    def background_path(self):
        path = momapy.drawing.Path(
            stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        path += (momapy.drawing.move_to(self.north_west())
                    + momapy.drawing.line_to(self.north_east())
                    + momapy.drawing.line_to(self.south_east())
                    + momapy.drawing.line_to(self.south_west())
                    + momapy.drawing.close()
        )
        if self.direction == momapy.core.Direction.VERTICAL:
            path += (momapy.drawing.move_to(self.base_left_connector())
                        + momapy.drawing.line_to(self.north())
                        + momapy.drawing.move_to(self.base_right_connector())
                        + momapy.drawing.line_to(self.south())
            )
        else:
            path += (momapy.drawing.move_to(self.base_left_connector())
                        + momapy.drawing.line_to(self.west())
                        + momapy.drawing.move_to(self.base_right_connector())
                        + momapy.drawing.line_to(self.east())
            )
        return path

    def foreground_path(self):
        return None


    def angle(self, angle, unit="degrees"):
        return Rectangle.angle(self, angle, unit)

@dataclass(frozen=True)
class Ellipse(momapy.core.NodeLayoutElement):

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

    def background_path(self):
        ellipse = momapy.drawing.Ellipse(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            point=self.position,
            rx=self.width/2,
            ry=self.height/2
        )
        return ellipse


    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)


@dataclass(frozen=True)
class RectangleWithCutCorners(momapy.core.NodeLayoutElement):
    cut_corners: float = 0

    def north_west(self):
        return self.self_bbox().north_west()

    def west(self):
        return self.position - (self.width/2, 0)

    def south_west(self):
        return self.self_bbox().south_west()

    def south(self):
        return self.position + (0, self.height/2)

    def south_east(self):
        return self.self_bbox().south_east()

    def east(self):
        return self.position + (self.width/2, 0)

    def north_east(self):
        return self.self_bbox().north_east()

    def north(self):
        return self.position - (0, self.height/2)

    def center(self):
        return self.position

    def north_north_west(self):
        return self.north() + (self.cut_corners - self.width/2, 0)

    def north_north_east(self):
        return self.north() + (self.width/2 - self.cut_corners, 0)

    def east_north_east(self):
        return self.east() + (0, self.cut_corners - self.height/2, 0)

    def east_south_east(self):
        return self.east() + (0, self.height/2 - self.cut_corners)

    def south_south_east(self):
        return self.south() + (self.width/2 - self.cut_corners, 0)

    def south_south_west(self):
        return self.south() + (self.cut_corners - self.width/2, 0)

    def south_south_west(self):
        return self.south() + (self.cut_corners - self.width/2, 0)

    def west_south_west(self):
        return self.west() + (0, self.height/2 - self.cut_corners, 0)

    def west_north_west(self):
        return self.west() + (0, self.cut_corners - self.height/2, 0)


    def background_path(self):
        path = momapy.drawing.Path(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
        )
        path += (momapy.drawing.move_to(self.north_north_west())
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

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class Stadium(momapy.core.NodeLayoutElement):

    def north_west(self):
        return self.self_bbox().north_west() + (self.height/2, 0)

    def west(self):
        return self.self_bbox().west()

    def south_west(self):
        return self.self_bbox().south_west() + (self.height/2, 0)

    def south(self):
        return self.self_bbox().south()

    def south_east(self):
        return self.self_bbox().south_east() - (self.height/2, 0)

    def east(self):
        return self.self_bbox().east()

    def north_east(self):
        return self.self_bbox().north_east() - (self.height/2, 0)

    def north(self):
        return self.self_bbox().north()

    def center(self):
        return momapy.geometry.Point(self.x, self.y)

    def background_path(self):
        path = momapy.drawing.Path(
            stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        path += (momapy.drawing.move_to(self.north_west())
                    + momapy.drawing.line_to(self.north_east())
                    + momapy.drawing.arc(
                        self.north_east() + (0, self.height/2), self.height/2,
                        -math.pi/2, math.pi/2)
                    + momapy.drawing.line_to(self.south_west())
                    + momapy.drawing.arc(
                        self.south_west() - (0, self.height/2), self.height/2,
                        math.pi/2, 3*math.pi/2)
                    + momapy.drawing.close()
        )
        return path

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class RectangleWithBottomRoundedCorners(momapy.core.NodeLayoutElement):
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

    def background_path(self):
        path = momapy.drawing.Path(
            stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        path += (momapy.drawing.move_to(self.north_west())
                 + momapy.drawing.line_to(self.north_east())
                 + momapy.drawing.line_to(self.east_south_east())
                 + momapy.drawing.arc(
                     self.east_south_east() - (self.rounded_corners, 0),
                     self.rounded_corners, 0, math.pi/2)
                 + momapy.drawing.line_to(self.south_south_west())
                 + momapy.drawing.arc(
                     self.south_south_west() - (0, self.rounded_corners),
                     self.rounded_corners, math.pi/2, math.pi)
                 + momapy.drawing.close()
        )
        return path

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class CircleWithDiagonalBar(momapy.core.NodeLayoutElement):

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

    def background_path(self):
        circle = momapy.drawing.Ellipse(
            point=self.position, rx=self.width/2, ry=self.height/2)
        bar = momapy.drawing.Path()
        bar += (momapy.drawing.move_to(self.self_bbox().south_west())
                + momapy.drawing.line_to(self.self_bbox().north_east()))
        elements = (circle, bar)
        group = momapy.drawing.Group(
            stroke=self.stroke, fill=self.fill,
            stroke_width=self.stroke_width, elements=elements)
        return group


    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)


        path = momapy.drawing.Path(
            stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        path += (momapy.drawing.move_to(self.north_west())
                 + momapy.drawing.line_to(self.north_east())
                 + momapy.drawing.line_to(self.east_south_east())
                 + momapy.drawing.arc(
                     self.east_south_east() - (self.rounded_corners, 0),
                     self.rounded_corners, 0, math.pi/2)
                 + momapy.drawing.line_to(self.south_south_west())
                 + momapy.drawing.arc(
                     self.south_south_west() - (0, self.rounded_corners),
                     self.rounded_corners, math.pi/2, math.pi)
                 + momapy.drawing.close()
        )
        return path

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class CircleWithConnectorsAndText(momapy.core.NodeLayoutElement):
    left_connector_length: float = 0
    right_connector_length: float = 0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL
    text: str = ""

    def north_west(self):
        return self.self_bbox().north_west()

    def west(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x - self.width/2, self.y)
        else:
            return momapy.geometry.Point(
                self.x - self.width/2 - self.left_connector_length, self.y)

    def south_west(self):
        return self.self_bbox().south_west()

    def south(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y + self.height/2 + self.right_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y + self.height/2)

    def south_east(self):
        return self.self_bbox().south_east()

    def east(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x + self.width/2, self.y)
        else:
            return momapy.geometry.Point(
                self.x + self.width/2 + self.right_connector_length, self.y)

    def north_east(self):
        return self.self_bbox().north_east()

    def north(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y - self.height/2 - self.left_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y - self.height/2)

    def center(self):
        return self.position

    def base_left_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y - self.height/2)
        else:
            return momapy.geometry.Point(self.x - self.width/2, self.y)

    def base_right_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y + self.height/2)
        else:
            return momapy.geometry.Point(self.x + self.width/2, self.y)

    def background_path(self):
        circle = momapy.drawing.Ellipse(
            point=self.position, rx=self.width/2, ry=self.height/2)
        left_connector = momapy.drawing.Path()
        left_connector += momapy.drawing.move_to(self.base_left_connector())
        right_connector = momapy.drawing.Path()
        right_connector += momapy.drawing.move_to(self.base_right_connector())
        if self.direction == momapy.core.Direction.VERTICAL:
            left_connector += momapy.drawing.line_to(self.north())
            right_connector += momapy.drawing.line_to(self.south())
        else:
            left_connector += momapy.drawing.line_to(self.west())
            right_connector += momapy.drawing.line_to(self.east())
        font_size=self.width/4
        font_description=f"Arial {font_size}"
        text = momapy.drawing.Text(
            text=self.text, position=self.position, width=self.width,
            height=self.height, font_description=font_description
        )
        elements = (circle, left_connector, right_connector, text)
        group = momapy.drawing.Group(
            stroke=self.stroke, fill=self.fill,
            stroke_width=self.stroke_width, elements=elements
        )
        return group

    def foreground_path(self):
        return None


    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(self, angle, unit)


@dataclass(frozen=True)
class Hexagon(momapy.core.NodeLayoutElement):
    top_left_angle: float = 50
    top_right_angle: float = 50
    bottom_left_angle: float = 50
    bottom_right_angle: float = 50

    def north_west(self):
        angle = math.radians(self.top_left_angle)
        side_length = abs(self.height / (2*math.sin(angle)))
        p = momapy.geometry.Point(
            self.west().x + side_length * math.cos(angle),
            self.west().y - self.height/2
        )
        return p

    def west(self):
        return self.position - (self.width/2, 0)

    def south_west(self):
        angle = math.radians(self.bottom_left_angle)
        side_length = self.height / (2*math.sin(angle))
        p = momapy.geometry.Point(
            self.west().x + side_length * math.cos(angle),
            self.west().y + self.height/2
        )
        return p

    def south(self):
        return self.position + (0, self.height/2)

    def south_east(self):
        angle = math.radians(self.bottom_right_angle)
        side_length = self.height / (2*math.sin(angle))
        p = momapy.geometry.Point(
            self.east().x - side_length * math.cos(angle),
            self.east().y + self.height/2
        )
        return p

    def east(self):
        return self.position + (self.width/2, 0)

    def north_east(self):
        angle = math.radians(self.top_right_angle)
        side_length = self.height / (2*math.sin(angle))
        p = momapy.geometry.Point(
            self.east().x - side_length * math.cos(angle),
            self.east().y - self.height/2
        )
        return p

    def north(self):
        return self.position - (0, self.height/2)

    def center(self):
        return self.position

    def background_path(self):
        path = momapy.drawing.Path(
            stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        path += (momapy.drawing.move_to(self.north_west())
                 + momapy.drawing.line_to(self.north_east())
                 + momapy.drawing.line_to(self.east())
                 + momapy.drawing.line_to(self.south_east())
                 + momapy.drawing.line_to(self.south_west())
                 + momapy.drawing.line_to(self.west())
                 + momapy.drawing.close()
        )
        return path

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleRectangleWithRoundedCorners(momapy.core.NodeLayoutElement):
    rounded_corners: float = 10
    offset: float = 10

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

    def background_path(self):
        bottom_rectangle = RectangleWithRoundedCorners(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        top_rectangle = RectangleWithRoundedCorners(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        elements = (
            bottom_rectangle.background_path(),
            top_rectangle.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleRectangleWithCutCorners(momapy.core.NodeLayoutElement):
    cut_corners: float = 10
    offset: float = 10

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

    def background_path(self):
        bottom_rectangle = RectangleWithCutCorners(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            cut_corners=self.cut_corners
        )
        top_rectangle = RectangleWithCutCorners(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            cut_corners=self.cut_corners
        )
        elements = (
            bottom_rectangle.background_path(),
            top_rectangle.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleRectangleWithBottomRoundedCorners(momapy.core.NodeLayoutElement):
    rounded_corners: float = 10
    offset: float = 10

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

    def background_path(self):
        bottom_rectangle = RectangleWithBottomRoundedCorners(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        top_rectangle = RectangleWithBottomRoundedCorners(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        elements = (
            bottom_rectangle.background_path(),
            top_rectangle.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleStadium(momapy.core.NodeLayoutElement):
    offset: float = 10

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

    def background_path(self):
        bottom_stadium = Stadium(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
        )
        top_stadium = Stadium(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
        )
        elements = (
            bottom_stadium.background_path(),
            top_stadium.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class RectangleWithConnectorsAndText(momapy.core.NodeLayoutElement):
    left_connector_length: float = 0
    right_connector_length: float = 0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL
    text: str = ""

    def north_west(self):
        return self.self_bbox().north_west()

    def west(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x - self.width/2, self.y)
        else:
            return momapy.geometry.Point(
                self.x - self.width/2 - self.left_connector_length, self.y)

    def south_west(self):
        return self.self_bbox().south_west()

    def south(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y + self.height/2 + self.right_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y + self.height/2)

    def south_east(self):
        return self.self_bbox().south_east()

    def east(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x + self.width/2, self.y)
        else:
            return momapy.geometry.Point(
                self.x + self.width/2 + self.right_connector_length, self.y)

    def north_east(self):
        return self.self_bbox().north_east()

    def north(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y - self.height/2 - self.left_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y - self.height/2)

    def center(self):
        return self.position

    def base_left_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y - self.height/2)
        else:
            return momapy.geometry.Point(self.x - self.width/2, self.y)

    def base_right_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y + self.height/2)
        else:
            return momapy.geometry.Point(self.x + self.width/2, self.y)

    def background_path(self):
        rectangle = momapy.drawing.Path(
            stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        rectangle += (momapy.drawing.move_to(self.north_west())
                    + momapy.drawing.line_to(self.north_east())
                    + momapy.drawing.line_to(self.south_east())
                    + momapy.drawing.line_to(self.south_west())
                    + momapy.drawing.close()
        )
        left_connector = momapy.drawing.Path()
        left_connector += momapy.drawing.move_to(self.base_left_connector())
        right_connector = momapy.drawing.Path()
        right_connector += momapy.drawing.move_to(self.base_right_connector())
        if self.direction == momapy.core.Direction.VERTICAL:
            left_connector += momapy.drawing.line_to(self.north())
            right_connector += momapy.drawing.line_to(self.south())
        else:
            left_connector += momapy.drawing.line_to(self.west())
            right_connector += momapy.drawing.line_to(self.east())
        font_size=self.width/2
        font_description=f"Arial {font_size}"
        text = momapy.drawing.Text(
            text=self.text, position=self.position, width=self.width,
            height=self.height, font_description=font_description
        )
        elements = (rectangle, left_connector, right_connector, text)
        group = momapy.drawing.Group(
            stroke=self.stroke, fill=self.fill,
            stroke_width=self.stroke_width, elements=elements
        )
        return group

    def foreground_path(self):
        return None


    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(self, angle, unit)


@dataclass(frozen=True)
class Hexagon(momapy.core.NodeLayoutElement):
    top_left_angle: float = 50
    top_right_angle: float = 50
    bottom_left_angle: float = 50
    bottom_right_angle: float = 50

    def north_west(self):
        angle = math.radians(self.top_left_angle)
        side_length = abs(self.height / (2*math.sin(angle)))
        p = momapy.geometry.Point(
            self.west().x + side_length * math.cos(angle),
            self.west().y - self.height/2
        )
        return p

    def west(self):
        return self.position - (self.width/2, 0)

    def south_west(self):
        angle = math.radians(self.bottom_left_angle)
        side_length = self.height / (2*math.sin(angle))
        p = momapy.geometry.Point(
            self.west().x + side_length * math.cos(angle),
            self.west().y + self.height/2
        )
        return p

    def south(self):
        return self.position + (0, self.height/2)

    def south_east(self):
        angle = math.radians(self.bottom_right_angle)
        side_length = self.height / (2*math.sin(angle))
        p = momapy.geometry.Point(
            self.east().x - side_length * math.cos(angle),
            self.east().y + self.height/2
        )
        return p

    def east(self):
        return self.position + (self.width/2, 0)

    def north_east(self):
        angle = math.radians(self.top_right_angle)
        side_length = self.height / (2*math.sin(angle))
        p = momapy.geometry.Point(
            self.east().x - side_length * math.cos(angle),
            self.east().y - self.height/2
        )
        return p

    def north(self):
        return self.position - (0, self.height/2)

    def center(self):
        return self.position

    def background_path(self):
        path = momapy.drawing.Path(
            stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        path += (momapy.drawing.move_to(self.north_west())
                 + momapy.drawing.line_to(self.north_east())
                 + momapy.drawing.line_to(self.east())
                 + momapy.drawing.line_to(self.south_east())
                 + momapy.drawing.line_to(self.south_west())
                 + momapy.drawing.line_to(self.west())
                 + momapy.drawing.close()
        )
        return path

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleRectangleWithRoundedCorners(momapy.core.NodeLayoutElement):
    rounded_corners: float = 10
    offset: float = 10

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

    def background_path(self):
        bottom_rectangle = RectangleWithRoundedCorners(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        top_rectangle = RectangleWithRoundedCorners(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        elements = (
            bottom_rectangle.background_path(),
            top_rectangle.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleRectangleWithCutCorners(momapy.core.NodeLayoutElement):
    cut_corners: float = 10
    offset: float = 10

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

    def background_path(self):
        bottom_rectangle = RectangleWithCutCorners(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            cut_corners=self.cut_corners
        )
        top_rectangle = RectangleWithCutCorners(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            cut_corners=self.cut_corners
        )
        elements = (
            bottom_rectangle.background_path(),
            top_rectangle.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleRectangleWithBottomRoundedCorners(momapy.core.NodeLayoutElement):
    rounded_corners: float = 10
    offset: float = 10

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

    def background_path(self):
        bottom_rectangle = RectangleWithBottomRoundedCorners(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        top_rectangle = RectangleWithBottomRoundedCorners(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        elements = (
            bottom_rectangle.background_path(),
            top_rectangle.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleStadium(momapy.core.NodeLayoutElement):
    offset: float = 10

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

    def background_path(self):
        bottom_stadium = Stadium(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
        )
        top_stadium = Stadium(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
        )
        elements = (
            bottom_stadium.background_path(),
            top_stadium.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class CircleWithConnectors(momapy.core.NodeLayoutElement):
    left_connector_length: float = 0
    right_connector_length: float = 0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL

    def north_west(self):
        return self.self_bbox().north_west()

    def west(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x - self.width/2, self.y)
        else:
            return momapy.geometry.Point(
                self.x - self.width/2 - self.left_connector_length, self.y)

    def south_west(self):
        return self.self_bbox().south_west()

    def south(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y + self.height/2 + self.right_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y + self.height/2)

    def south_east(self):
        return self.self_bbox().south_east()

    def east(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x + self.width/2, self.y)
        else:
            return momapy.geometry.Point(
                self.x + self.width/2 + self.right_connector_length, self.y)

    def north_east(self):
        return self.self_bbox().north_east()

    def north(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y - self.height/2 - self.left_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y - self.height/2)

    def center(self):
        return self.position

    def base_left_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y - self.height/2)
        else:
            return momapy.geometry.Point(self.x - self.width/2, self.y)

    def base_right_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y + self.height/2)
        else:
            return momapy.geometry.Point(self.x + self.width/2, self.y)

    def background_path(self):
        circle = momapy.drawing.Ellipse(
            point=self.position, rx=self.width/2, ry=self.height/2)
        left_connector = momapy.drawing.Path()
        left_connector += momapy.drawing.move_to(self.base_left_connector())
        right_connector = momapy.drawing.Path()
        right_connector += momapy.drawing.move_to(self.base_right_connector())
        if self.direction == momapy.core.Direction.VERTICAL:
            left_connector += momapy.drawing.line_to(self.north())
            right_connector += momapy.drawing.line_to(self.south())
        else:
            left_connector += momapy.drawing.line_to(self.west())
            right_connector += momapy.drawing.line_to(self.east())
        elements = (circle, left_connector, right_connector)
        group = momapy.drawing.Group(
            stroke=self.stroke, fill=self.fill,
            stroke_width=self.stroke_width, elements=elements
        )
        return group

    def foreground_path(self):
        return None


    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(self, angle, unit)

@dataclass(frozen=True)
class CircleInsideCircleWithConnectors(momapy.core.NodeLayoutElement):
    left_connector_length: float = 0
    right_connector_length: float = 0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL
    sep: float = 2

    def north_west(self):
        return self.self_bbox().north_west()

    def west(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x - self.width/2, self.y)
        else:
            return momapy.geometry.Point(
                self.x - self.width/2 - self.left_connector_length, self.y)

    def south_west(self):
        return self.self_bbox().south_west()

    def south(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y + self.height/2 + self.right_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y + self.height/2)

    def south_east(self):
        return self.self_bbox().south_east()

    def east(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x + self.width/2, self.y)
        else:
            return momapy.geometry.Point(
                self.x + self.width/2 + self.right_connector_length, self.y)

    def north_east(self):
        return self.self_bbox().north_east()

    def north(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y - self.height/2 - self.left_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y - self.height/2)

    def center(self):
        return self.position

    def base_left_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y - self.height/2)
        else:
            return momapy.geometry.Point(self.x - self.width/2, self.y)

    def base_right_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y + self.height/2)
        else:
            return momapy.geometry.Point(self.x + self.width/2, self.y)

    def background_path(self):
        outer_circle = momapy.drawing.Ellipse(
            point=self.position, rx=self.width/2, ry=self.height/2)
        inner_circle = momapy.drawing.Ellipse(
            point=self.position, rx=self.width/2 - self.sep,
            ry=self.height/2 - self.sep)
        left_connector = momapy.drawing.Path()
        left_connector += momapy.drawing.move_to(self.base_left_connector())
        right_connector = momapy.drawing.Path()
        right_connector += momapy.drawing.move_to(self.base_right_connector())
        if self.direction == momapy.core.Direction.VERTICAL:
            left_connector += momapy.drawing.line_to(self.north())
            right_connector += momapy.drawing.line_to(self.south())
        else:
            left_connector += momapy.drawing.line_to(self.west())
            right_connector += momapy.drawing.line_to(self.east())
        elements = (outer_circle, inner_circle, left_connector, right_connector)
        group = momapy.drawing.Group(
            stroke=self.stroke, fill=self.fill,
            stroke_width=self.stroke_width, elements=elements
        )
        return group

    def foreground_path(self):
        return None


    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(self, angle, unit)


@dataclass(frozen=True)
class Hexagon(momapy.core.NodeLayoutElement):
    top_left_angle: float = 50
    top_right_angle: float = 50
    bottom_left_angle: float = 50
    bottom_right_angle: float = 50

    def north_west(self):
        angle = math.radians(self.top_left_angle)
        side_length = abs(self.height / (2*math.sin(angle)))
        p = momapy.geometry.Point(
            self.west().x + side_length * math.cos(angle),
            self.west().y - self.height/2
        )
        return p

    def west(self):
        return self.position - (self.width/2, 0)

    def south_west(self):
        angle = math.radians(self.bottom_left_angle)
        side_length = self.height / (2*math.sin(angle))
        p = momapy.geometry.Point(
            self.west().x + side_length * math.cos(angle),
            self.west().y + self.height/2
        )
        return p

    def south(self):
        return self.position + (0, self.height/2)

    def south_east(self):
        angle = math.radians(self.bottom_right_angle)
        side_length = self.height / (2*math.sin(angle))
        p = momapy.geometry.Point(
            self.east().x - side_length * math.cos(angle),
            self.east().y + self.height/2
        )
        return p

    def east(self):
        return self.position + (self.width/2, 0)

    def north_east(self):
        angle = math.radians(self.top_right_angle)
        side_length = self.height / (2*math.sin(angle))
        p = momapy.geometry.Point(
            self.east().x - side_length * math.cos(angle),
            self.east().y - self.height/2
        )
        return p

    def north(self):
        return self.position - (0, self.height/2)

    def center(self):
        return self.position

    def background_path(self):
        path = momapy.drawing.Path(
            stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        path += (momapy.drawing.move_to(self.north_west())
                 + momapy.drawing.line_to(self.north_east())
                 + momapy.drawing.line_to(self.east())
                 + momapy.drawing.line_to(self.south_east())
                 + momapy.drawing.line_to(self.south_west())
                 + momapy.drawing.line_to(self.west())
                 + momapy.drawing.close()
        )
        return path

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleRectangleWithRoundedCorners(momapy.core.NodeLayoutElement):
    rounded_corners: float = 10
    offset: float = 10

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

    def background_path(self):
        bottom_rectangle = RectangleWithRoundedCorners(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        top_rectangle = RectangleWithRoundedCorners(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        elements = (
            bottom_rectangle.background_path(),
            top_rectangle.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleRectangleWithCutCorners(momapy.core.NodeLayoutElement):
    cut_corners: float = 10
    offset: float = 10

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

    def background_path(self):
        bottom_rectangle = RectangleWithCutCorners(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            cut_corners=self.cut_corners
        )
        top_rectangle = RectangleWithCutCorners(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            cut_corners=self.cut_corners
        )
        elements = (
            bottom_rectangle.background_path(),
            top_rectangle.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleRectangleWithBottomRoundedCorners(momapy.core.NodeLayoutElement):
    rounded_corners: float = 10
    offset: float = 10

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

    def background_path(self):
        bottom_rectangle = RectangleWithBottomRoundedCorners(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        top_rectangle = RectangleWithBottomRoundedCorners(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        elements = (
            bottom_rectangle.background_path(),
            top_rectangle.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleStadium(momapy.core.NodeLayoutElement):
    offset: float = 10

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

    def background_path(self):
        bottom_stadium = Stadium(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
        )
        top_stadium = Stadium(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
        )
        elements = (
            bottom_stadium.background_path(),
            top_stadium.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class RectangleWithConnectorsAndText(momapy.core.NodeLayoutElement):
    left_connector_length: float = 0
    right_connector_length: float = 0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL
    text: str = ""

    def north_west(self):
        return self.self_bbox().north_west()

    def west(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x - self.width/2, self.y)
        else:
            return momapy.geometry.Point(
                self.x - self.width/2 - self.left_connector_length, self.y)

    def south_west(self):
        return self.self_bbox().south_west()

    def south(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y + self.height/2 + self.right_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y + self.height/2)

    def south_east(self):
        return self.self_bbox().south_east()

    def east(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x + self.width/2, self.y)
        else:
            return momapy.geometry.Point(
                self.x + self.width/2 + self.right_connector_length, self.y)

    def north_east(self):
        return self.self_bbox().north_east()

    def north(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y - self.height/2 - self.left_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y - self.height/2)

    def center(self):
        return self.position

    def base_left_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y - self.height/2)
        else:
            return momapy.geometry.Point(self.x - self.width/2, self.y)

    def base_right_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y + self.height/2)
        else:
            return momapy.geometry.Point(self.x + self.width/2, self.y)

    def background_path(self):
        rectangle = momapy.drawing.Path(
            stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        rectangle += (momapy.drawing.move_to(self.north_west())
                    + momapy.drawing.line_to(self.north_east())
                    + momapy.drawing.line_to(self.south_east())
                    + momapy.drawing.line_to(self.south_west())
                    + momapy.drawing.close()
        )
        left_connector = momapy.drawing.Path()
        left_connector += momapy.drawing.move_to(self.base_left_connector())
        right_connector = momapy.drawing.Path()
        right_connector += momapy.drawing.move_to(self.base_right_connector())
        if self.direction == momapy.core.Direction.VERTICAL:
            left_connector += momapy.drawing.line_to(self.north())
            right_connector += momapy.drawing.line_to(self.south())
        else:
            left_connector += momapy.drawing.line_to(self.west())
            right_connector += momapy.drawing.line_to(self.east())
        font_size=self.width/2
        font_description=f"Arial {font_size}"
        text = momapy.drawing.Text(
            text=self.text, position=self.position, width=self.width,
            height=self.height, font_description=font_description
        )
        elements = (rectangle, left_connector, right_connector, text)
        group = momapy.drawing.Group(
            stroke=self.stroke, fill=self.fill,
            stroke_width=self.stroke_width, elements=elements
        )
        return group

    def foreground_path(self):
        return None


    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(self, angle, unit)


@dataclass(frozen=True)
class Hexagon(momapy.core.NodeLayoutElement):
    top_left_angle: float = 50
    top_right_angle: float = 50
    bottom_left_angle: float = 50
    bottom_right_angle: float = 50

    def north_west(self):
        angle = math.radians(self.top_left_angle)
        side_length = abs(self.height / (2*math.sin(angle)))
        p = momapy.geometry.Point(
            self.west().x + side_length * math.cos(angle),
            self.west().y - self.height/2
        )
        return p

    def west(self):
        return self.position - (self.width/2, 0)

    def south_west(self):
        angle = math.radians(self.bottom_left_angle)
        side_length = self.height / (2*math.sin(angle))
        p = momapy.geometry.Point(
            self.west().x + side_length * math.cos(angle),
            self.west().y + self.height/2
        )
        return p

    def south(self):
        return self.position + (0, self.height/2)

    def south_east(self):
        angle = math.radians(self.bottom_right_angle)
        side_length = self.height / (2*math.sin(angle))
        p = momapy.geometry.Point(
            self.east().x - side_length * math.cos(angle),
            self.east().y + self.height/2
        )
        return p

    def east(self):
        return self.position + (self.width/2, 0)

    def north_east(self):
        angle = math.radians(self.top_right_angle)
        side_length = self.height / (2*math.sin(angle))
        p = momapy.geometry.Point(
            self.east().x - side_length * math.cos(angle),
            self.east().y - self.height/2
        )
        return p

    def north(self):
        return self.position - (0, self.height/2)

    def center(self):
        return self.position

    def background_path(self):
        path = momapy.drawing.Path(
            stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        path += (momapy.drawing.move_to(self.north_west())
                 + momapy.drawing.line_to(self.north_east())
                 + momapy.drawing.line_to(self.east())
                 + momapy.drawing.line_to(self.south_east())
                 + momapy.drawing.line_to(self.south_west())
                 + momapy.drawing.line_to(self.west())
                 + momapy.drawing.close()
        )
        return path

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleRectangleWithRoundedCorners(momapy.core.NodeLayoutElement):
    rounded_corners: float = 10
    offset: float = 10

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

    def background_path(self):
        bottom_rectangle = RectangleWithRoundedCorners(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        top_rectangle = RectangleWithRoundedCorners(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        elements = (
            bottom_rectangle.background_path(),
            top_rectangle.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleRectangleWithCutCorners(momapy.core.NodeLayoutElement):
    cut_corners: float = 10
    offset: float = 10

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

    def background_path(self):
        bottom_rectangle = RectangleWithCutCorners(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            cut_corners=self.cut_corners
        )
        top_rectangle = RectangleWithCutCorners(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            cut_corners=self.cut_corners
        )
        elements = (
            bottom_rectangle.background_path(),
            top_rectangle.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleRectangleWithBottomRoundedCorners(momapy.core.NodeLayoutElement):
    rounded_corners: float = 10
    offset: float = 10

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

    def background_path(self):
        bottom_rectangle = RectangleWithBottomRoundedCorners(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        top_rectangle = RectangleWithBottomRoundedCorners(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            rounded_corners=self.rounded_corners
        )
        elements = (
            bottom_rectangle.background_path(),
            top_rectangle.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)

@dataclass(frozen=True)
class DoubleStadium(momapy.core.NodeLayoutElement):
    offset: float = 10

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

    def background_path(self):
        bottom_stadium = Stadium(
            position=self.position + (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
        )
        top_stadium = Stadium(
            position=self.position - (self.offset, self.offset),
            width=self.width - self.offset,
            height=self.height - self.offset,
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
        )
        elements = (
            bottom_stadium.background_path(),
            top_stadium.background_path()
        )
        group = momapy.drawing.Group(
            stroke=self.stroke,
            fill=self.fill,
            stroke_width=self.stroke_width,
            elements=elements
        )
        return group

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        return self.self_bbox().angle(angle, unit)
