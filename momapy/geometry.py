from dataclasses import dataclass, field, replace
from typing import Optional, Any, Callable, Union
from abc import ABC, abstractmethod

import math
import numpy
import decimal
import copy

import shapely

import momapy.builder

import bezier.curve

ROUNDING = 2
decimal.getcontext().prec = ROUNDING


@dataclass(frozen=True)
class GeometryObject(ABC):
    @abstractmethod
    def to_shapely(self):
        pass


@dataclass(frozen=True)
class Point(GeometryObject):
    x: float
    y: float

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

    def to_tuple(self):
        return (
            self.x,
            self.y,
        )

    def get_intersection_with_line(self, line):
        return get_intersection_of_object_and_line(self, line)

    def get_angle(self):
        line = Line(Point(0, 0), self)
        return line.get_angle()

    def transformed(self, transformation):
        return transform_point(self, transformation)

    def reversed(self):
        return reverse_point(self)

    def to_shapely(self):
        return shapely.Point(self.x, self.y)

    def to_fortranarray(self):
        return numpy.asfortranarray([[self.x], [self.y]])

    def bbox(self):
        return Bbox(copy.deepcopy(self), 0, 0)

    @classmethod
    def from_shapely(cls, point: shapely.Point):
        return cls(point.x, point.y)

    @classmethod
    def from_fortranarray(cls, fortranarray):
        return cls(fortranarray[0][0], fortranarray[1][1])

    @classmethod
    def from_tuple(cls, t):
        return cls(t[0], t[1])


@dataclass(frozen=True)
class Line(GeometryObject):
    p1: Point
    p2: Point

    def slope(self):
        if self.p1.x != self.p2.x:
            return round(
                (self.p2.y - self.p1.y) / (self.p2.x - self.p1.x), ROUNDING
            )
        return float("NAN")  # infinite slope

    def intercept(self):
        slope = self.slope()
        if not math.isnan(slope):
            return self.p1.y - slope * self.p1.x
        else:
            return float("NAN")

    def get_angle(self):
        return get_angle_of_line(self)

    def is_parallel_to_line(self, line):
        return are_lines_parallel(self, line)

    def is_coincident_to_line(self, line):
        return are_lines_coincident(self, line)

    def get_intersection_with_line(self, line):
        return get_intersection_of_object_and_line(self, line)

    def has_point(self, point):
        slope = self.slope()
        if not math.isnan(slope):
            return point.y == slope * point.x + self.intercept()
        else:
            return self.p1.x == point.x

    def transformed(self, transformation):
        return transform_line(self, transformation)

    def reversed(self):
        return reverse_line(self)

    def to_shapely(self):
        return shapely.LineString([self.p1.to_tuple(), self.p2.to_tuple()])


@dataclass(frozen=True)
class Segment(GeometryObject):
    p1: Point
    p2: Point

    def length(self):
        return math.sqrt(
            (self.p2.x - self.p1.x) ** 2 + (self.p2.y - self.p1.y) ** 2
        )

    def contains(self, point, max_distance=0.01):
        distance = self.to_shapely().distance(point.to_shapely())
        if distance <= max_distance:
            return True
        return False

    def get_angle(self):
        return get_angle_of_line(self)

    def get_intersection_with_line(self, line):
        return get_intersection_of_object_and_line(line, self)

    def get_position_at_fraction(self, fraction):
        return get_position_at_fraction(self, fraction)

    def get_angle_at_fraction(self, fraction):
        return get_angle_at_fraction(self, fraction)

    def get_position_and_angle_at_fraction(self, fraction):
        return get_position_and_angle_at_fraction(self, fraction)

    def shortened(self, length, start_or_end="end"):
        return shorten_segment(self, length, start_or_end)

    def transformed(self, transformation):
        return transform_segment(self, transformation)

    def reversed(self):
        return reverse_segment(self)

    def to_shapely(self):
        return shapely.LineString([self.p1.to_tuple(), self.p2.to_tuple()])

    def bbox(self):
        return Bbox.from_bounds(self.to_shapely().bounds)

    @classmethod
    def from_shapely(cls, line_string: shapely.LineString):
        shapely_points = line_string.boundary.geoms
        return cls(
            Point.from_shapely(shapely_points[0]),
            Point.from_shapely(shapely_points[1]),
        )


@dataclass(frozen=True)
class BezierCurve(GeometryObject):
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
        points = [Point.from_tuple(t) for t in bezier_curve.nodes.T]
        return cls(points[0], points[-1], points[1:-1])

    def length(self):
        return self._to_bezier().length

    def evaluate(self, s):
        evaluation = self._to_bezier().evaluate(s)
        return Point.from_fortranarray(evaluation)

    def evaluate_multi(self, s):
        evaluation = self._to_bezier().evaluate_multi(s)
        return [Point(e[0], e[1]) for e in evaluation.T]

    def get_intersection_with_line(self, line):
        return get_intersection_of_object_and_line(line, self)

    def get_position_at_fraction(self, fraction):
        return get_position_at_fraction(self, fraction)

    def get_angle_at_fraction(self, fraction):
        return get_angle_at_fraction(self, fraction)

    def get_position_and_angle_at_fraction(self, fraction):
        return get_position_and_angle_at_fraction(self, fraction)

    def shortened(self, length, start_or_end="end"):
        return shorten_bezier_curve(self, length, start_or_end)

    def transformed(self, transformation):
        return transform_bezier_curve(self, transformation)

    def reversed(self):
        return reverse_bezier_curve(self)

    def to_shapely(self, n_segs=50):
        points = self.evaluate_multi(
            numpy.arange(0, 1 + 1 / n_segs, 1 / n_segs, dtype="double")
        )
        return shapely.LineString([point.to_tuple() for point in points])

    def bbox(self):
        return Bbox.from_bounds(self.to_shapely().bounds)


@dataclass(frozen=True)
class EllipticalArc(GeometryObject):
    p1: Point
    p2: Point
    rx: float
    ry: float
    x_axis_rotation: float
    arc_flag: int
    sweep_flag: int

    def get_intersection_with_line(self, line):
        return get_intersection_of_object_and_line(self, line)

    def to_arc_and_transformation(self):
        x1, y1 = self.p1.x, self.p1.y
        sigma = self.x_axis_rotation
        x2, y2 = self.p2.x, self.p2.y
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

    def center(self):
        x1, y1 = self.p1.x, self.p1.y
        sigma = self.x_axis_rotation
        x2, y2 = self.p2.x, self.p2.y
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
        return Point(cx, cy)

    def get_position_at_fraction(self, fraction):
        return get_position_at_fraction(self, fraction)

    def get_angle_at_fraction(self, fraction):
        return get_angle_at_fraction(self, fraction)

    def get_position_and_angle_at_fraction(self, fraction):
        return get_position_and_angle_at_fraction(self, fraction)

    def to_shapely(self):
        def _split_line_string(
            line_string: shapely.LineString,
            point: Point,
            max_distance: float = 0.02,
        ):
            left_coords = []
            right_coords = []
            passed = False
            left_coords.append(line_string.coords[0])
            for i, current_coord in enumerate(line_string.coords[1:]):
                previous_coord = line_string.coords[i]
                if not passed:
                    previous_point = Point.from_tuple(previous_coord)
                    current_point = Point.from_tuple(current_coord)
                    segment = Segment(previous_point, current_point)
                    if segment.contains(point, max_distance):
                        left_coords.append(previous_coord)
                        left_coords.append(point.to_tuple())
                        right_coords.append(point.to_tuple())
                        right_coords.append(current_coord)
                        passed = True
                    else:
                        left_coords.append(current_coord)
                else:
                    right_coords.append(current_coord)
            if right_coords:
                return shapely.GeometryCollection(
                    [
                        shapely.LineString(left_coords),
                        shapely.LineString(right_coords),
                    ]
                )
            else:
                return line_string

        origin = shapely.Point(0, 0)
        circle = origin.buffer(1.0).boundary
        ellipse = shapely.affinity.scale(circle, self.rx, self.ry)
        ellipse = shapely.affinity.rotate(ellipse, self.x_axis_rotation)
        center = self.center()
        ellipse = shapely.affinity.translate(ellipse, center.x, center.y)
        if self.p1 != Point.from_tuple(ellipse.coords[0]):
            first_point = self.p1
            second_point = self.p2
        else:
            first_point = self.p2
            second_point = self.p1
        first_split = _split_line_string(ellipse, first_point)
        if second_point == Point.from_tuple(first_split.geoms[0].coords[0]):
            arcs = first_split
        else:
            multi_line = shapely.MultiLineString(
                [first_split.geoms[1], first_split.geoms[0]]
            )
            line_string = shapely.ops.linemerge(multi_line)
            arcs = _split_line_string(line_string, second_point)
        arcs = list(arcs.geoms)
        if arcs[0].length == arcs[1].length:
            if first_point == self.p1:
                return arcs[self.sweep_flag]
            return arcs[abs(self.sweep_flag - 1)]
        arcs.sort(key=lambda arc: arc.length)
        return arcs[self.arc_flag]

    def bbox(self):
        return Bbox.from_bounds(self.to_shapely().bounds)

    def shortened(self, length, start_or_end="end"):
        return shorten_elliptical_arc(self, length, start_or_end)

    def transformed(self, transformation):
        return transform_elliptical_arc(self, transformation)

    def reversed(self):
        return reverse_elliptical_arc(self)


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

    @classmethod
    def from_bounds(cls, bounds):  # (min_x, min_y, max_x, max_y)
        return cls(
            momapy.geometry.Point(
                (bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2
            ),
            bounds[2] - bounds[0],
            bounds[3] - bounds[1],
        )


@dataclass(frozen=True)
class Transformation(ABC):
    pass

    @abstractmethod
    def to_matrix(self):
        pass

    @abstractmethod
    def inverted(self):
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

    def inverted(self):
        return invert_matrix_transformation(self)


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
                translation.inverted().to_matrix(),
            )
        return m

    def inverted(self):
        return invert_rotation(self)


@dataclass(frozen=True)
class Translation(Transformation):
    tx: float
    ty: float

    def to_matrix(self):
        m = numpy.array(
            [[1, 0, self.tx], [0, 1, self.ty], [0, 0, 1]], dtype=float
        )
        return m

    def inverted(self):
        return invert_translation(self)


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

    def inverted(self):
        return invert_scaling(self)


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


def transform_elliptical_arc(elliptical_arc, transformation):
    east = momapy.geometry.Point(
        math.cos(self.x_axis_rotation) * self.rx,
        math.sin(self.x_axis_rotation) * self.rx,
    )
    north = momapy.geometry.Point(
        math.cos(self.x_axis_rotation) * self.ry,
        math.sin(self.x_axis_rotation) * self.ry,
    )
    new_center = momapy.geometry.transform_point(
        momapy.geometry.Point(0, 0), transformation
    )
    new_east = momapy.geometry.transform_point(east, transformation)
    new_north = momapy.geometry.transform_point(north, transformation)
    new_rx = momapy.geometry.Segment(new_center, new_east).length()
    new_ry = momapy.geometry.Segment(new_center, new_north).length()
    new_start_point = momapy.geometry.transform_point(self.p1, transformation)
    new_end_point = momapy.geometry.transform_point(self.p2, transformation)
    new_x_axis_rotation = math.degrees(
        momapy.geometry.get_angle_of_line(
            momapy.geometry.Line(new_center, new_east)
        )
    )
    return EllipticalArc(
        new_end_point,
        new_rx,
        new_ry,
        new_x_axis_rotation,
        self.arc_flag,
        self.sweep_flag,
    )


def reverse_point(point):
    return Point(point.x, point.y)


def reverse_line(line):
    return Line(line.p2, line.p1)


def reverse_segment(segment):
    return Segment(segment.p2, segment.p1)


def reverse_bezier_curve(bezier_curve):
    return BezierCurve(
        bezier_curve.p2, bezier_curve.p1, bezier_curve.control_points[::-1]
    )


def reverse_elliptical_arc(elliptical_arc):
    return EllipticalArc(
        elliptical_arc.p2,
        elliptical_arc.p1,
        elliptical_arc.rx,
        elliptical_arc.ry,
        elliptical_arc.x_axis_rotation,
        elliptical_arc.arc_flag,
        abs(elliptical_arc.sweep_flag - 1),
    )


def shorten_segment(segment, length, start_or_end="end"):
    if length == 0:
        shortened_segment = copy.deepcopy(segment)
    else:
        if start_or_end == "start":
            shortened_segment = segment.reversed().shortened(length).reversed()
        else:
            fraction = 1 - length / segment.length()
            point = segment.get_position_at_fraction(fraction)
            shortened_segment = Segment(segment.p1, point)
    return shortened_segment


def shorten_bezier_curve(bezier_curve, length, start_or_end="end"):
    if length == 0:
        shortened_bezier_curve = copy.deepcopy(bezier_curve)
    else:
        if start_or_end == "start":
            shortened_bezier_curve = (
                bezier_curve.reversed().shortened(length).reversed()
            )
        else:
            lib_bezier_curve = bezier_curve._to_bezier()
            total_length = lib_bezier_curve.length
            if length > total_length:
                length = total_length
            fraction = 1 - length / total_length
            point = bezier_curve.get_position_at_fraction(fraction)
            horizontal_line = BezierCurve(
                point - (5, 0), point + (5, 0)
            )._to_bezier()
            s = lib_bezier_curve.intersect(horizontal_line)[0][0]
            lib_shortened_bezier_curve = lib_bezier_curve.specialize(0, s)
            shortened_bezier_curve = BezierCurve._from_bezier(
                lib_shortened_bezier_curve
            )
    return shortened_bezier_curve


def shorten_elliptical_arc(elliptical_arc, length, start_or_end="end"):
    if length == 0:
        shortened_elliptical_arc = copy.deepcopy(elliptical_arc)
    else:
        if start_or_end == "start":
            shortened_elliptical_arc = (
                elliptical_arc.reversed().shortened(length).reversed()
            )
        else:
            fraction = 1 - length / elliptical_arc.length()
            point = elliptical_arc.get_position_at_fraction(fraction)
            shortened_elliptical_arc = replace(elliptical_arc, p2=point)
    return shortened_elliptical_arc


def invert_matrix_transformation(matrix_transformation):
    return MatrixTransformation(numpy.linalg.inv(matrix_transformation.m))


def invert_rotation(rotation):
    return Rotation(-rotation.angle, rotation.point)


def invert_translation(translation):
    return Translation(-translation.tx, -translation.ty)


def invert_scaling(scaling):
    return Scaling(-scaling.sx, -scaling.sy)


def get_intersection_of_object_and_line(
    obj: Union[
        GeometryObject,
        "momapy.core.LayoutElement",
        "momapy.drawing.DrawingElement",
        shapely.Geometry,
    ],
    line: Line,
):
    if isinstance(obj, Line):
        slope1 = obj.slope()
        intercept1 = obj.intercept()
        slope2 = line.slope()
        intercept2 = line.intercept()
        if line.is_coincident_to_line(obj):
            intersection = [copy.deepcopy(obj)]
        elif line.is_parallel_to_line(obj):
            intersection = []
        elif math.isnan(slope1):
            intersection = [Point(obj.p1.x, slope2 * obj.p1.x + intercept2)]
        elif math.isnan(slope2):
            intersection = [Point(line.p1.x, slope1 * line.p1.x + intercept1)]
        else:
            d = (line.p1.x - line.p2.x) * (obj.p1.y - obj.p2.y) - (
                line.p1.y - line.p2.y
            ) * (obj.p1.x - obj.p2.x)
            px = (
                (line.p1.x * line.p2.y - line.p1.y * line.p2.x)
                * (obj.p1.x - obj.p2.x)
                - (line.p1.x - line.p2.x)
                * (obj.p1.x * obj.p2.y - obj.p1.y * obj.p2.x)
            ) / d
            py = (
                (line.p1.x * line.p2.y - line.p1.y * line.p2.x)
                * (obj.p1.y - obj.p2.y)
                - (line.p1.y - line.p2.y)
                * (obj.p1.x * obj.p2.y - obj.p1.y * obj.p2.x)
            ) / d
            intersection = [Point(px, py)]
    else:
        if isinstance(obj, shapely.Geometry):
            bbox = Bbox.from_bounds(obj.bounds)
        else:
            bbox = obj.bbox()
            obj = obj.to_shapely()
        points = []
        anchors = ["north_west", "north_east", "south_east", "south_west"]
        line_string = None
        for i, current_anchor in enumerate(anchors):
            if i < len(anchors) - 1:
                next_anchor = anchors[i + 1]
            else:
                next_anchor = anchors[0]
            bbox_line = Line(
                getattr(bbox, current_anchor)(), getattr(bbox, next_anchor)()
            )
            bbox_line_intersection = line.get_intersection_with_line(bbox_line)
            if (
                len(bbox_line_intersection) > 0
            ):  # intersection is not empty => intersection has one element
                bbox_line_intersection = bbox_line_intersection.pop()
                if isinstance(
                    bbox_line_intersection, Line
                ):  # intersection is the line
                    line_string = line.to_shapely()
                    break
                else:  # intersection is a point
                    points.append(bbox_line_intersection)
        if line_string is None:
            points = sorted([point.to_tuple() for point in points])
            line_string = shapely.LineString(points)
        shapely_intersection = line_string.intersection(obj)
        intersection = []
        if not hasattr(shapely_intersection, "geoms"):
            shapely_intersection = [shapely_intersection]
        else:
            shapely_intersection = shapely_intersection.geoms
        for shapely_obj in shapely_intersection:
            if isinstance(shapely_obj, shapely.Point):
                intersection_obj = Point.from_shapely(shapely_obj)
            elif isinstance(shapely_obj, shapely.LineString):
                intersection_obj = Segment.from_shapely(shapely_obj)
            intersection.append(intersection_obj)
    return intersection


# angle in radians
def get_angle_of_line(line):
    x1 = line.p1.x
    y1 = line.p1.y
    x2 = line.p2.x
    y2 = line.p2.y
    angle = math.atan2(y2 - y1, x2 - x1)
    return get_normalized_angle(angle)


def are_lines_parallel(line1, line2):
    slope1 = line1.slope()
    slope2 = line2.slope()
    if math.isnan(slope1) and math.isnan(slope2):
        return True
    return slope1 == slope2


def are_lines_coincident(line1, line2):
    slope1 = line1.slope()
    intercept1 = line1.intercept()
    slope2 = line2.slope()
    intercept2 = line2.intercept()
    return (
        math.isnan(slope1)
        and math.isnan(slope2)
        and line1.p1.x == line2.p1.x
        or slope1 == slope2
        and intercept1 == intercept2
    )


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


# angle is in radians; return angle between 0 and 2 * pi
def get_normalized_angle(angle):
    while angle > 2 * math.pi:
        angle -= 2 * math.pi
    while angle < 0:
        angle += 2 * math.pi
    return angle


def get_position_at_fraction(
    segment_or_curve: Union[Segment, BezierCurve, EllipticalArc],
    fraction: float,
) -> Point:  # fraction in [0, 1]
    line_string = segment_or_curve.to_shapely()
    shapely_point = line_string.interpolate(fraction, normalized=True)
    return Point.from_shapely(shapely_point)


def get_angle_at_fraction(
    segment_or_curve: Union[Segment, BezierCurve, EllipticalArc],
    fraction: float,
) -> Point:  # fraction in [0, 1]
    line_string = segment_or_curve.to_shapely()
    total_length = line_string.length
    current_length = 0
    previous_coord = line_string.coords[0]
    for current_coord in line_string.coords[1:]:
        segment = Segment(
            Point.from_tuple(previous_coord),
            Point.from_tuple(current_coord),
        )
        current_length += segment.length()
        if current_length / total_length >= fraction:
            return segment.get_angle()
    return segment.get_angle()


def get_position_and_angle_at_fraction(
    segment_or_curve: Union[Segment, BezierCurve, EllipticalArc],
    fraction: float,
) -> Point:  # fraction in [0, 1]
    position = get_position_at_fraction(segment_or_curve, fraction)
    angle = get_angle_at_fraction(segment_or_curve, fraction)
    return position, angle


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
