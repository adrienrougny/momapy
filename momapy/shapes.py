import math
from dataclasses import dataclass, field

from momapy.core import NodeLayoutElement, anchorpoint, Direction
from momapy.drawing import Path, move_to, line_to, close, Group
from momapy.geometry import Point, Line, get_angle_of_line, get_intersection_of_lines, is_angle_in_sector, Bbox, get_normalized_angle

@dataclass(frozen=True)
class Rectangle(NodeLayoutElement):

    def north_west(self):
        return Point(self.x - self.width / 2, self.y - self.height / 2)

    def west(self):
        return Point(self.x - self.width / 2, self.y)

    def south_west(self):
        return Point(self.x - self.width / 2, self.y + self.height / 2)

    def south(self):
        return Point(self.x, self.y + self.height / 2)

    def south_east(self):
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    def east(self):
        return Point(self.x + self.width / 2, self.y)

    def north_east(self):
        return Point(self.x + self.width / 2, self.y - self.height / 2)

    def north(self):
        return Point(self.x, self.y - self.height / 2)

    def center(self):
        return Point(self.x, self.y)

    def background_path(self):
        path = Path(stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        path += move_to(self.north_west()) + \
                line_to(self.north_east()) + \
                line_to(self.south_east()) + \
                line_to(self.south_west()) + \
                close()
        return path

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        angle = -angle
        if unit == "degrees":
            angle = math.radians(angle)
        angle = get_normalized_angle(angle)
        line = Line(self.center(), self.center() + (math.cos(angle), math.sin(angle)))
        sectors = [
            (self.north_east(), self.south_east()),
            (self.south_east(), self.south_west()),
            (self.south_west(), self.north_west()),
            (self.north_west(), self.north_east())
        ]
        for sector in sectors:
            if is_angle_in_sector(angle, self.center(), sector[0], sector[1]):
                p = get_intersection_of_lines(Line(sector[0], sector[1]), line)
                return p
        return self.center()

@dataclass(frozen=True)
class RectangleWithConnectors(NodeLayoutElement):
    left_connector_length: float = 0
    right_connector_length: float = 0
    direction: Direction = Direction.HORIZONTAL

    def north_west(self):
        return Point(self.x - self.width / 2, self.y - self.height / 2)

    def west(self):
        if self.direction == Direction.VERTICAL:
            return Point(self.x - self.width / 2, self.y)
        else:
            return Point(self.x - self.width / 2 - self.left_connector_length, self.y)

    def south_west(self):
        return Point(self.x - self.width / 2, self.y + self.height / 2)

    def south(self):
        if self.direction == Direction.VERTICAL:
            return Point(self.x, self.y + self.height / 2 + self.right_connector_length)
        else:
            return Point(self.x, self.y + self.height / 2)

    def south_east(self):
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    def east(self):
        if self.direction == Direction.VERTICAL:
            return Point(self.x + self.width / 2, self.y)
        else:
            return Point(self.x + self.width / 2 + self.right_connector_length, self.y)

    def north_east(self):
        return Point(self.x + self.width / 2, self.y - self.height / 2)

    def north(self):
        if self.direction == Direction.VERTICAL:
            return Point(self.x, self.y - self.height / 2 - self.left_connector_length)
        else:
            return Point(self.x, self.y - self.height / 2)

    def center(self):
        return Point(self.x, self.y)

    def base_left_connector(self):
        if self.direction == Direction.VERTICAL:
            return Point(self.x, self.y + self.height / 2)
        else:
            return Point(self.x - self.width / 2, self.y)

    def base_right_connector(self):
        if self.direction == Direction.VERTICAL:
            return Point(self.x, self.y - self.height / 2)
        else:
            return Point(self.x + self.width / 2, self.y)

    def background_path(self):
        path = Path(stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        path += move_to(self.north_west()) + \
                line_to(self.north_east()) + \
                line_to(self.south_east()) + \
                line_to(self.south_west()) + \
                close()
        if self.direction == Direction.VERTICAL:
            path += move_to(self.base_left_connector()) + \
                line_to(self.north()) + \
                move_to(self.base_right_connector()) + \
                line_to(self.south())
        else:
            path += move_to(self.base_left_connector()) + \
                line_to(self.west()) + \
                move_to(self.base_right_connector()) + \
                line_to(self.east())
        return path

    def foreground_path(self):
        return None


    def angle(self, angle, unit="degrees"):
        angle = -angle
        if unit == "degrees":
            angle = math.radians(angle)
        line = Line(self.center(), self.center() + Point(math.cos(angle), math.sin(angle)))
        if is_angle_in_sector(angle, self.center(), self.south_east(), self.north_east()):
            p = get_intersection_of_lines(Line(self.south_east(), self.north_east()),
                    line)
        elif is_angle_in_sector(angle, self.center(), self.north_east(), self.north_west()):
            p = get_intersection_of_lines(Line(self.north_east(), self.north_west()),
                    line)
        elif is_angle_in_sector(angle, self.center(), self.north_west(), self.south_west()):
            p = get_intersection_of_lines(Line(self.north_west(), self.south_west()),
                    line)
        elif is_angle_in_sector(angle, self.center(), self.south_west(), self.south_east()):
            p = get_intersection_of_lines(Line(self.south_west(), self.south_east()),
                    line)
        else:
            p = self.center()
        return p
