from dataclasses import dataclass, field
from typing import Optional, Any, Callable, Union
from abc import ABC, abstractmethod

import math
import numpy
import decimal

import momapy.builder

import bezier.curve

ROUNDING = 2
decimal.getcontext().prec = ROUNDING


@dataclass(frozen=True)
class Point(object):
    x: Optional[float] = None
    y: Optional[float] = None

    def __add__(self, xy):
        if momapy.builder.isinstance_or_builder(xy, Point):
            xy = (xy.x, xy.y)
        return Point(self.x + xy[0], self.y + xy[1])

    def __sub__(self, xy):
        if momapy.builder.isinstance_or_builder(xy, Point):
            xy = (xy.x, xy.y)
        return Point(self.x - xy[0], self.y - xy[1])

    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):
        return Point(self.x / scalar, self.y / scalar)

    def __iter__(self):
        yield self.x
        yield self.y

    def to_matrix(self):
        m = numpy.array([[self.x], [self.y], [1]], dtype=float)
        return m

    def get_intersection_with_line(self, line):
        return get_intersection_of_line_and_point(line, self)

    def get_angle(self):
        line = Line(Point(0, 0), self)
        return line.get_angle()

    def transformed(self, transformation):
        return transform_point(self, transformation)


@dataclass(frozen=True)
class Transformation(ABC):
    pass

    @abstractmethod
    def to_matrix(self):
        pass

    @abstractmethod
    def get_inverse(self):
        pass

    def __mul__(self, other):
        return MatrixTransformation(
            numpy.matmul(self.to_matrix(), other.to_matrix())
        )


@dataclass(frozen=True)
class MatrixTransformation(Transformation):
    m: numpy.array

    def to_matrix(self):
        return self.m

    def get_inverse(self):
        return MatrixTransformation(numpy.linalg.inv(self.m))


@dataclass(frozen=True)
class Rotation(Transformation):
    angle: float
    point: Optional[Point] = None

    def to_matrix(self):
        m = numpy.array(
            [
                [math.cos(self.angle), -math.sin(self.angle), 0],
                [math.sin(self.angle), math.cos(self.angle), 0],
                [0, 0, 1],
            ],
            dtype=float,
        )
        if self.point is not None:
            translation = Translation(self.point.x, self.point.y)
            m = numpy.matmul(
                numpy.matmul(translation.to_matrix(), m),
                translation.get_inverse().to_matrix(),
            )
        return m

    def get_inverse(self):
        return Rotation(-self.angle, self.point)


@dataclass(frozen=True)
class Translation(Transformation):
    tx: float
    ty: float

    def to_matrix(self):
        m = numpy.array(
            [[1, 0, self.tx], [0, 1, self.ty], [0, 0, 1]], dtype=float
        )
        return m

    def get_inverse(self):
        return Translation(-self.tx, -self.ty)


@dataclass(frozen=True)
class Scaling(Transformation):
    sx: float
    sy: float

    def to_matrix(self):
        m = numpy.array(
            [
                [self.sx, 0, 0],
                [0, self.sy, 0],
                [0, 0, 1],
            ],
            dtype=float,
        )
        return m

    def get_inverse(self):
        return Scaling(-self.sx, -self.sy)


def transform_point(point, transformation):
    m = numpy.matmul(transformation.to_matrix(), point.to_matrix())
    return Point(m[0][0], m[1][0])


def transform_line(line, transformation):
    return Line(
        transform_point(line.p1, transformation),
        transform_point(line.p2, transformation),
    )


def transform_segment(segment, transformation):
    return Segment(
        transform_point(segment.p1, transformation),
        transform_point(segment.p2, transformation),
    )


def transform_bezier_curve(bezier_curve, transformation):
    return BezierCurve(
        transform_point(bezier_curve.p1),
        transform_point(bezier_curve.p2),
        tuple(
            [transform_point(point) for point in bezier_curve.control_points]
        ),
    )


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

    def slope(self):
        if self.p1.x != self.p2.x:
            return round(
                (self.p2.y - self.p1.y) / (self.p2.x - self.p1.x), ROUNDING
            )
        return None  # infinite slope

    def intercept(self):
        if self.slope() is not None:
            return self.p1.y - self.slope() * self.p1.x
        else:
            return None

    def get_angle(self):
        return get_angle_of_line(self)

    def is_parallel_to_line(self, line):
        return are_lines_parallel(self, line)

    def get_intersection_with_line(self, line):
        return get_intersection_of_lines(self, line)

    def has_point(self, point):
        if self.slope() is not None:
            return point.y == self.slope() * point.x + self.intercept()
        else:
            return self.p1.x == point.x

    def transformed(self, transformation):
        return transform_line(self, transformation)


@dataclass(frozen=True)
class Segment(object):
    p1: Point
    p2: Point

    def length(self):
        return math.sqrt(
            (self.p2.x - self.p1.x) ** 2 + (self.p2.y - self.p1.y) ** 2
        )

    def has_point(self, point):
        d1 = get_distance_between_points(self.p1, point)
        d2 = get_distance_between_points(self.p2, point)
        line = Line(self.p1, self.p2)
        return (
            d1 <= self.length()
            and d2 <= self.length()
            and line.has_point(point)
        )

    def get_angle(self):
        return get_angle_of_line(self)

    def get_intersection_with_line(self, line):
        return get_intersection_of_line_and_segment(line, self)

    def shortened(self, length):
        fraction = 1 - length / self.length()
        p, _ = get_position_and_angle_at_fraction(self, fraction)
        return Segment(self.p1, p)

    def transformed(self, transformation):
        return transform_segment(self, transformation)


@dataclass(frozen=True)
class BezierCurve(object):
    p1: Point
    p2: Point
    control_points: tuple[Point] = field(default_factory=tuple)

    def _to_bezier(self):
        x = []
        y = []
        x.append(self.p1.x)
        y.append(self.p1.y)
        for point in self.control_points:
            x.append(point.x)
            y.append(point.y)
        x.append(self.p2.x)
        y.append(self.p2.y)
        nodes = [x, y]
        return bezier.curve.Curve.from_nodes(nodes)

    @classmethod
    def _from_bezier(cls, bezier_curve):
        points = [Point(e[0], e[1]) for e in bezier_curve.nodes.T]
        return cls(points[0], points[-1], points[1:-1])

    def length(self):
        return self._to_bezier().length

    def get_intersection_with_line(self, line):
        return get_intersection_of_line_and_bezier_curve(line, self)

    def shortened(self, length):
        bezier_curve = self._to_bezier()
        fraction = 1 - length / bezier_curve.length
        shortened_bezier_curve = bezier_curve.specialize(0, fraction)
        return BezierCurve._from_bezier(shortened_bezier_curve)

    def transformed(self, transformation):
        return transform_bezier_curve(self, transformation)


@dataclass(frozen=True)
class Circle(object):
    point: Point
    radius: float

    def get_intersection_with_line(self, line):
        return get_intersection_of_line_and_circle(line, self)


@dataclass(frozen=True)
class Arc(object):
    point: Point
    radius: float
    start_angle: float
    end_angle: float

    def start_point(self):
        px = self.point.x + math.cos(self.start_angle) * self.radius
        py = self.point.y + math.sin(self.start_angle) * self.radius
        return Point(px, py)

    def end_point(self):
        px = self.point.x + math.cos(self.end_angle) * self.radius
        py = self.point.y + math.sin(self.end_angle) * self.radius
        return Point(px, py)

    def get_intersection_with_line(self, line):
        return get_intersection_of_line_and_arc(line, self)


@dataclass(frozen=True)
class Ellipse(object):
    point: Point
    rx: float
    ry: float

    def get_intersection_with_line(self, line):
        return get_intersection_of_line_and_ellipse(line, self)


@dataclass(frozen=True)
class EllipticalArc(object):
    start_point: Point
    end_point: Point
    rx: float
    ry: float
    x_axis_rotation: float
    arc_flag: int
    sweep_flag: int

    def get_intersection_with_line(self, line):
        return get_intersection_of_line_and_elliptical_arc(line, self)

    def to_arc_and_transformation(self):
        x1, y1 = self.start_point.x, self.start_point.y
        sigma = self.x_axis_rotation
        x2, y2 = self.end_point.x, self.end_point.y
        rx = self.rx
        ry = self.ry
        fa = self.arc_flag
        fs = self.sweep_flag
        x1p = math.cos(sigma) * ((x1 - x2) / 2) + math.sin(sigma) * (
            (y1 - y2) / 2
        )
        y1p = -math.sin(sigma) * ((x1 - x2) / 2) + math.cos(sigma) * (
            (y1 - y2) / 2
        )
        l = x1p**2 / rx**2 + y1p**2 / ry**2
        if l > 1:
            rx = math.sqrt(l) * rx
            ry = math.sqrt(l) * ry
        r = rx**2 * ry**2 - rx**2 * y1p**2 - ry**2 * x1p**2
        if r < 0:  # dure to imprecision? to fix later
            r = 0
        a = math.sqrt(r / (rx**2 * y1p**2 + ry**2 * x1p**2))
        if fa == fs:
            a = -a
        cxp = a * rx * y1p / ry
        cyp = -a * ry * x1p / rx
        cx = math.cos(sigma) * cxp - math.sin(sigma) * cyp + (x1 + x2) / 2
        cy = math.sin(sigma) * cxp + math.cos(sigma) * cyp + (y1 + y2) / 2
        theta1 = get_angle_between_segments(
            Segment(Point(0, 0), Point(1, 0)),
            Segment(Point(0, 0), Point((x1p - cxp) / rx, (y1p - cyp) / ry)),
        )
        delta_theta = get_angle_between_segments(
            Segment(Point(0, 0), Point((x1p - cxp) / rx, (y1p - cyp) / ry)),
            Segment(Point(0, 0), Point(-(x1p + cxp) / rx, -(y1p + cyp) / ry)),
        )
        if fs == 0 and delta_theta > 0:
            delta_theta -= 2 * math.pi
        elif fs == 1 and delta_theta < 0:
            delta_theta += 2 * math.pi
        theta2 = theta1 + delta_theta
        translation = Translation(cx, cy)
        rotation = Rotation(sigma)
        scaling = Scaling(rx, ry)
        transformation = translation * rotation * scaling
        arc = Arc(Point(0, 0), 1, theta1, theta2)
        return arc, transformation


def get_intersection_of_lines(line1, line2):
    if line1.slope() is None:
        if line2.slope() is None:
            if line1.p1.x == line2.p2.x:
                return [line1]
            return None
        else:
            return [
                Point(
                    line1.p1.x, line2.slope() * line1.p1.x + line2.intercept()
                )
            ]
    else:
        if line2.slope() is None:
            return [
                Point(
                    line2.p1.x, line1.slope() * line2.p1.x + line1.intercept()
                )
            ]
        if (
            line1.slope() == line2.slope()
            and line1.intercept() == line2.intercept()
        ):
            return [line1]
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
        px = (
            (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
        ) / d
        py = (
            (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
        ) / d
        return [Point(px, py)]


def get_intersection_of_line_and_arc(line, arc):
    circle = Circle(arc.point, arc.radius)
    circle_intersection = get_intersection_of_line_and_circle(line, circle)
    if circle_intersection is None:
        return None
    intersection = []
    for point in circle_intersection:
        angle = get_angle_of_line(Line(arc.point, point))
        if is_angle_between(angle, arc.start_angle, arc.end_angle):
            intersection.append(point)
    return intersection


def get_intersection_of_line_and_circle(line, circle):
    line = Line(line.p1 - circle.point, line.p2 - circle.point)
    dx = line.p2.x - line.p1.x
    dy = line.p2.y - line.p1.y
    dr = math.sqrt(dx**2 + dy**2)
    d = line.p1.x * line.p2.y - line.p2.x * line.p1.y
    delta = circle.radius**2 * dr**2 - d**2
    if delta < 0:
        return None
    intersection = []
    sign = -1 if dy < 0 else 1
    px1 = (
        d * dy + sign * dx * math.sqrt(circle.radius**2 * dr**2 - d**2)
    ) / dr**2 + circle.point.x
    py1 = (
        -d * dx + abs(dy) * math.sqrt(circle.radius**2 * dr**2 - d**2)
    ) / dr**2 + circle.point.y
    intersection.append(Point(px1, py1))
    if delta > 0:
        px2 = (
            d * dy
            - sign * dx * math.sqrt(circle.radius**2 * dr**2 - d**2)
        ) / dr**2 + circle.point.x
        py2 = (
            -d * dx - abs(dy) * math.sqrt(circle.radius**2 * dr**2 - d**2)
        ) / dr**2 + circle.point.y
        intersection.append(Point(px2, py2))
    return intersection


def get_intersection_of_line_and_ellipse(line, ellipse):
    circle = Circle(Point(0, 0), 1)
    translation = Translation(ellipse.point.x, ellipse.point.y)
    scaling = Scaling(ellipse.rx, ellipse.ry)
    transformation = translation * scaling
    inverse_transformation = transformation.get_inverse()
    line = transform_line(line, inverse_transformation)
    circle_intersection = get_intersection_of_line_and_circle(line, circle)
    if circle_intersection is None:
        return None
    intersection = []
    for point in circle_intersection:
        point = transform_point(point, transformation)
        intersection.append(point)
    return intersection


def get_intersection_of_line_and_elliptical_arc(line, elliptical_arc):
    arc, transformation = elliptical_arc.to_arc_and_transformation()
    inverse_transformation = transformation.get_inverse()
    line = transform_line(line, inverse_transformation)
    arc_intersection = arc.get_intersection_with_line(line)
    if arc_intersection is None:
        return None
    intersection = []
    for point in arc_intersection:
        point = transform_point(point, transformation)
        intersection.append(point)
    return intersection


def get_intersection_of_line_and_point(line, point):
    if line.has_point(point):
        return [point]
    return None


def get_intersection_of_line_and_segment(line, segment):
    line_intersection = Line(segment.p1, segment.p2).get_intersection_with_line(
        line
    )
    if line_intersection is None:
        return None
    intersection = line_intersection[0]
    if isinstance(intersection, Line):
        return [segment.p1, segment.p2]
    d1 = get_distance_between_points(segment.p1, intersection)
    d2 = get_distance_between_points(segment.p2, intersection)
    if d1 <= segment.length() and d2 <= segment.length():
        return [intersection]
    return None


def get_intersection_of_line_and_bezier_curve(line, bezier_curve):
    bezier_curve = bezier_curve._to_bezier()
    line = bezier.curve.Curve([line.p1, line.p2])
    intersection = bezier_curve.intersect(line).T
    return [Point(x, y) for x, y in intersection]


# angle in radians
def get_angle_of_line(line):
    x1 = line.p1.x
    y1 = line.p1.y
    x2 = line.p2.x
    y2 = line.p2.y
    angle = math.atan2(y2 - y1, x2 - x1)
    return get_normalized_angle(angle)


# angle in radians
def get_angle_of_bezier_curve(bezier_curve, s):
    bezier_curve = bezier_curve._to_bezier()
    hodograph = bezier_curve.evaluate_hodograph(s)
    point = Point(hodograph[0][0], hodograph[1][0])
    line = Line(Point(0, 0), point)
    return get_angle_of_line(line)


def are_lines_parallel(line1, line2):
    return line1.slope() == line2.slope()


# angle in radians
def is_angle_in_sector(angle, center, point1, point2):
    angle1 = get_angle_of_line(Line(center, point1))
    angle2 = get_angle_of_line(Line(center, point2))
    return is_angle_between(angle, angle1, angle2)


# angles in radians
def is_angle_between(angle, start_angle, end_angle):
    angle = get_normalized_angle(angle)
    start_angle = get_normalized_angle(start_angle)
    end_angle = get_normalized_angle(end_angle)
    if start_angle < end_angle:
        if angle >= start_angle and angle <= end_angle:
            return True
    else:
        if (
            start_angle <= angle <= 2 * math.pi
            or angle >= 0
            and angle <= end_angle
        ):
            return True
    return False


# angle is in radians
def get_normalized_angle(angle):
    while angle > 2 * math.pi:
        angle -= 2 * math.pi
    while angle < 0:
        angle += 2 * math.pi
    return angle


def get_position_and_angle_at_fraction(segment_or_bezier_curve, fraction):
    if momapy.builder.isinstance_or_builder(segment_or_bezier_curve, Segment):
        px = segment_or_bezier_curve.p1.x + fraction * (
            segment_or_bezier_curve.p2.x - segment_or_bezier_curve.p1.x
        )
        py = segment_or_bezier_curve.p1.y + fraction * (
            segment_or_bezier_curve.p2.y - segment_or_bezier_curve.p1.y
        )
        point = Point(px, py)
        angle = get_angle_of_line(segment_or_bezier_curve)
    elif momapy.builder.isinstance_or_builder(
        segment_or_bezier_curve, BezierCurve
    ):
        bezier_curve = segment_or_bezier_curve._to_bezier()
        evaluation = bezier_curve.evaluate(fraction)
        point = Point(evaluation[0][0], evaluation[1][0])
        angle = get_angle_of_bezier_curve(segment_or_bezier_curve, fraction)
    return point, angle


# angle is in radians between -pi and pi
def get_angle_between_segments(segment1, segment2):
    p1 = segment1.p2 - segment1.p1
    p2 = segment2.p2 - segment2.p1
    scalar_prod = p1.x * p2.x + p1.y * p2.y
    angle = math.acos(
        round(scalar_prod / (segment1.length() * segment2.length()), ROUNDING)
    )
    sign = p1.x * p2.y - p1.y * p2.x
    if sign < 0:
        angle = -angle
    return angle


def get_distance_between_points(p1, p2):
    return Segment(p1, p2).length()


def _point_builder_add(self, xy):
    if momapy.builder.isinstance_or_builder(xy, Point):
        xy = (xy.x, xy.y)
    return PointBuilder(self.x + xy[0], self.y + xy[1])


def _point_builder_sub(self, xy):
    if momapy.builder.isinstance_or_builder(xy, Point):
        xy = (xy.x, xy.y)
    return PointBuilder(self.x - xy[0], self.y - xy[1])


def _point_builder_mul(self, scalar):
    return PointBuilder(self.x * scalar, self.y * scalar)


def _point_builder_div(self, scalar):
    return PointBuilder(self.x / scalar, self.y / scalar)


def _point_builder_iter(self):
    yield self.x
    yield self.y


PointBuilder = momapy.builder.get_or_make_builder_cls(
    Point,
    builder_namespace={
        "__add__": _point_builder_add,
        "__sub__": _point_builder_sub,
        "__mul__": _point_builder_mul,
        "__div__": _point_builder_div,
        "__iter__": _point_builder_iter,
    },
)

momapy.builder.register_builder(PointBuilder)

BboxBuilder = momapy.builder.get_or_make_builder_cls(Bbox)

momapy.builder.register_builder(BboxBuilder)
