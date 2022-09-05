from dataclasses import dataclass
from typing import Optional, Any, Callable, Union

import math

def anchorpoint(anchor_func):
    anchor_func.__anchor__ = True
    return property(anchor_func)

@dataclass(frozen=True)
class Point(object):
    x: Optional[float] = None
    y: Optional[float] = None

    def __add__(self, xy):
        if isinstance(xy, Point):
            xy = (xy.x, xy.y)
        return Point(self.x + xy[0], self.y + xy[1])

    def __sub__(self, xy):
        if isinstance(xy, Point):
            xy = (xy.x, xy.y)
        return Point(self.x - xy[0], self.y - xy[1])

    def __iter__(self):
        yield self.x
        yield self.y

@dataclass(frozen=True)
class Bbox(object):
    position: Point
    width: float
    height: float

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    def size(self):
        return (self.width, self.height)

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
class Line(object):
    p1: Point
    p2: Point

    @property
    def slope(self):
        return (self.p2.y - self.p1.y)/(self.p2.x - self.p1.x)

    @property
    def intercept(self):
        return self.p1.y - self.slope()*self.p1.x

    def get_angle(self):
        return get_angle_of_line(self)

    def is_parallel_to_line(self, line):
        return are_lines_parallel(self, line)

    def get_intersection_with_line(self, line):
        return get_intersection_of_lines(self, line)

@dataclass(frozen=True)
class Segment(object):
    p1: Point
    p2: Point

    def length(self):
        return math.sqrt(
            (self.p2.x - self.p1.x)**2
            + (self.p2.y - self.p1.y)**2
        )

def get_intersection_of_lines(line1, line2):
    if (line1.slope() == line2.slope()
            and line1.intercept() == line2.intercept()):
        return line1
    elif are_lines_parallel(line1, line2):
        return None
    x1 = line1.p1.x
    y1 = line1.p1.y
    x2 = line1.p2.x
    y2 = line1.p2.y
    x3 = line2.p1.x
    y3 = line2.p1.y
    x4 = line2.p2.x
    y4 = line2.p2.y
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4))/d
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4))/d
    return Point(px, py)

#angle in radians
def get_angle_of_line(line):
    x1 = line.p1.x
    y1 = line.p1.y
    x2 = line.p2.x
    y2 = line.p2.y
    angle = math.atan2(y2 - y1, x2 - x1)
    return get_normalized_angle(angle)

def are_lines_parallel(line1, line2):
    return line1.slope() == line2.slope()

#angle in radians
def is_angle_in_sector(angle, center, point1, point2):
    angle1 = get_angle_of_line(Line(center, point1))
    angle2 = get_angle_of_line(Line(center, point2))
    if angle1 < angle2:
        if angle >= angle1 and angle <= angle2:
            return True
    else:
        if angle >= angle1 and angle <= 2 * math.pi or angle >= 0 and angle <= angle2:
            return True
    return False

#angle is in radians
def get_normalized_angle(angle):
    while angle > 2 * math.pi:
        angle -= 2 * math.pi
    while angle < 0:
        angle += 2 * math.pi
    return angle


def get_position_and_angle_at_fraction(segment, fraction):
    px = segment.p1.x + fraction * (segment.p2.x - segment.p1.x)
    py = segment.p1.y + fraction * (segment.p2.y - segment.p1.y)
    angle = get_angle_of_line(segment)
    return Point(px, py), angle

#angle in radians
def rotate_point(point, angle):
    px = point.x * math.cos(angle) + point.y * math.sin(angle)
    py = -point.x * math.sin(angle) + point.y * math.cos(angle)
    return Point(px, py)

#angle is in radians between -pi and pi
def get_angle_between_segments(segment1, segment2):
    p1 = segment1.p2 - segment1.p1
    p2 = segment2.p2 - segment2.p1
    scalar_prod = p1.x * p2.x + p1.y * p2.y
    angle = math.acos(scalar_prod / (segment1.length() * segment2.length()))
    sign = p1.x * p2.y - p1.y * p2.x
    if sign < 0:
        angle = -angle
    return angle
