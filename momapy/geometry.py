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

@dataclass(frozen=True)
class Line(object):
    p1: Point
    p2: Point

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
        return math.sqrt((self.p2.x - self.p1.x) ** 2 + (self.p2.y - self.p1.y) ** 2)

# def get_intersection_of_lines(linex1, y1, x2, y2, x3, y3, x4, y4):
def get_intersection_of_lines(line1, line2):
    x1 = line1.p1.x
    y1 = line1.p1.y
    x2 = line1.p2.x
    y2 = line1.p2.y
    x3 = line2.p1.x
    y3 = line2.p1.y
    x4 = line2.p2.x
    y4 = line2.p2.y
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / d
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / d
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
    x1 = line1.p1.x
    y1 = line1.p1.y
    x2 = line1.p2.x
    y2 = line1.p2.y
    x3 = line2.p1.x
    y3 = line2.p1.y
    x4 = line2.p2.x
    y4 = line2.p2.y
    if x2 - x1 == 0 or x4 - x3 == 0:
        return x2 - x1 == x4 - x3
    a1 = (y2 - y1) / (x2 - x1)
    a2 = (y4 - y3) / (x4 - x3)
    return a1 == a2

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


def get_position_at_fraction(segment, fraction):
    px = segment.p1.x + fraction * (segment.p2.x - segment.p1.x)
    py = segment.p1.y + fraction * (segment.p2.y - segment.p1.y)
    return Point(px, py)

#angle in radians
def rotate_point(point, angle):
    px = point.x * math.cos(angle) + point.y * math.sin(angle)
    py = -point.x * math.sin(angle) + point.y * math.cos(angle)
    return Point(px, py)
