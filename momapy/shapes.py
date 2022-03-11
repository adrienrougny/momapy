import math
from dataclasses import dataclass, field

import momapy.core
import momapy.drawing
import momapy.geometry

@dataclass(frozen=True)
class Rectangle(momapy.core.NodeLayoutElement):

    def north_west(self):
        return momapy.geometry.Point(self.x - self.width / 2, self.y - self.height / 2)

    def west(self):
        return momapy.geometry.Point(self.x - self.width / 2, self.y)

    def south_west(self):
        return momapy.geometry.Point(self.x - self.width / 2, self.y + self.height / 2)

    def south(self):
        return momapy.geometry.Point(self.x, self.y + self.height / 2)

    def south_east(self):
        return momapy.geometry.Point(self.x + self.width / 2, self.y + self.height / 2)

    def east(self):
        return momapy.geometry.Point(self.x + self.width / 2, self.y)

    def north_east(self):
        return momapy.geometry.Point(self.x + self.width / 2, self.y - self.height / 2)

    def north(self):
        return momapy.geometry.Point(self.x, self.y - self.height / 2)

    def center(self):
        return momapy.geometry.Point(self.x, self.y)

    def background_path(self):
        path = momapy.drawing.Path(stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        path += momapy.drawing.move_to(self.north_west()) + \
                momapy.drawing.line_to(self.north_east()) + \
                momapy.drawing.line_to(self.south_east()) + \
                momapy.drawing.line_to(self.south_west()) + \
                momapy.drawing.close()
        return path

    def foreground_path(self):
        return None

    def angle(self, angle, unit="degrees"):
        angle = -angle
        if unit == "degrees":
            angle = math.radians(angle)
        angle = momapy.geometry.get_normalized_angle(angle)
        line = momapy.geometry.Line(self.center(), self.center() + (math.cos(angle), math.sin(angle)))
        sectors = [
            (self.north_east(), self.south_east()),
            (self.south_east(), self.south_west()),
            (self.south_west(), self.north_west()),
            (self.north_west(), self.north_east())
        ]
        for sector in sectors:
            if momapy.geometry.is_angle_in_sector(angle, self.center(), sector[0], sector[1]):
                p = momapy.geometry.get_intersection_of_lines(momapy.geometry.Line(sector[0], sector[1]), line)
                return p
        return self.center()

@dataclass(frozen=True)
class RectangleWithConnectors(momapy.core.NodeLayoutElement):
    left_connector_length: float = 0
    right_connector_length: float = 0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL

    def north_west(self):
        return momapy.geometry.Point(self.x - self.width / 2, self.y - self.height / 2)

    def west(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x - self.width / 2, self.y)
        else:
            return momapy.geometry.Point(self.x - self.width / 2 - self.left_connector_length, self.y)

    def south_west(self):
        return momapy.geometry.Point(self.x - self.width / 2, self.y + self.height / 2)

    def south(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y + self.height / 2 + self.right_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y + self.height / 2)

    def south_east(self):
        return momapy.geometry.Point(self.x + self.width / 2, self.y + self.height / 2)

    def east(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x + self.width / 2, self.y)
        else:
            return momapy.geometry.Point(self.x + self.width / 2 + self.right_connector_length, self.y)

    def north_east(self):
        return momapy.geometry.Point(self.x + self.width / 2, self.y - self.height / 2)

    def north(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y - self.height / 2 - self.left_connector_length)
        else:
            return momapy.geometry.Point(self.x, self.y - self.height / 2)

    def center(self):
        return momapy.geometry.Point(self.x, self.y)

    def base_left_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y + self.height / 2)
        else:
            return momapy.geometry.Point(self.x - self.width / 2, self.y)

    def base_right_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y - self.height / 2)
        else:
            return momapy.geometry.Point(self.x + self.width / 2, self.y)

    def background_path(self):
        path = momapy.drawing.Path(stroke=self.stroke, fill=self.fill, stroke_width=self.stroke_width)
        path += momapy.drawing.move_to(self.north_west()) + \
                momapy.drawing.line_to(self.north_east()) + \
                momapy.drawing.line_to(self.south_east()) + \
                momapy.drawing.line_to(self.south_west()) + \
                momapy.drawing.close()
        if self.direction == momapy.core.Direction.VERTICAL:
            path += momapy.drawing.move_to(self.base_left_connector()) + \
                momapy.drawing.line_to(self.north()) + \
                momapy.drawing.move_to(self.base_right_connector()) + \
                momapy.drawing.line_to(self.south())
        else:
            path += momapy.drawing.move_to(self.base_left_connector()) + \
                momapy.drawing.line_to(self.west()) + \
                momapy.drawing.move_to(self.base_right_connector()) + \
                momapy.drawing.line_to(self.east())
        return path

    def foreground_path(self):
        return None


    def angle(self, angle, unit="degrees"):
        return Rectangle.angle(self, angle, unit)
