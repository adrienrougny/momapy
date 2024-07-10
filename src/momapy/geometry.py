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
        return get_intersection_of_line_and_point(line, self)

    def get_angle_to_horizontal(self):
        return get_angle_to_horizontal_of_point(self)

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

    def get_angle_to_horizontal(self):
        return get_angle_to_horizontal_of_line(self)

    def is_parallel_to_line(self, line):
        return are_lines_parallel(self, line)

    def is_coincident_to_line(self, line):
        return are_lines_coincident(self, line)

    def get_intersection_with_line(self, line):
        return get_intersection_of_lines(self, line)

    def get_distance_to_point(self, point):
        return get_distance_between_line_and_point(self, point)

    def has_point(self, point, max_distance=0.01):
        return line_has_point(self, point, max_distance)

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

    def get_distance_to_point(self, point):
        return get_distance_between_segment_and_point(self, point)

    def has_point(self, point, max_distance=0.01):
        return segment_has_point(self, point, max_distance)

    def get_angle_to_horizontal(self):
        return get_angle_to_horizontal_of_line(self)

    def get_intersection_with_line(self, line):
        return get_intersection_of_line_and_segment(line, self)

    def get_position_at_fraction(self, fraction):
        return get_position_at_fraction_of_segment(self, fraction)

    def get_angle_at_fraction(self, fraction):
        return get_angle_at_fraction_of_segment(self, fraction)

    def get_position_and_angle_at_fraction(self, fraction):
        return get_position_and_angle_at_fraction_of_segment(self, fraction)

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
        return get_intersection_of_line_and_bezier_curve(line, self)

    def get_position_at_fraction(self, fraction):
        return get_position_at_fraction_of_bezier_curve(self, fraction)

    def get_angle_at_fraction(self, fraction):
        return get_angle_at_fraction_of_bezier_curve(self, fraction)

    def get_position_and_angle_at_fraction(self, fraction):
        return get_position_and_angle_at_fraction_of_bezier_curve(
            self, fraction
        )

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
        return get_intersection_of_line_and_elliptical_arc(self, line)

    def get_center_parameterization(self):
        return get_center_parameterization_of_elliptical_arc(self)

    def get_center(self):
        return get_center_of_elliptical_arc(self)

    def get_position_at_fraction(self, fraction):
        return get_position_at_fraction_of_elliptical_arc(self, fraction)

    def get_angle_at_fraction(self, fraction):
        return get_angle_at_fraction_of_elliptical_arc(self, fraction)

    def get_position_and_angle_at_fraction(self, fraction):
        return get_position_and_angle_at_fraction_of_elliptical_arc(
            self, fraction
        )

    def to_shapely(self):
        def _split_line_string(
            line_string: shapely.LineString,
            point: Point,
        ):
            segment = Segment(
                Point.from_tuple(line_string.coords[0]),
                Point.from_tuple(line_string.coords[1]),
            )
            min_distance = segment.get_distance_to_point(point)
            min_i = 0
            for i, current_coord in enumerate(line_string.coords[2:]):
                previous_coord = line_string.coords[i + 1]
                segment = Segment(
                    Point.from_tuple(previous_coord),
                    Point.from_tuple(current_coord),
                )
                distance = segment.get_distance_to_point(point)
                if distance <= min_distance:
                    min_distance = distance
                    min_i = i
            left_coords = line_string.coords[0 : min_i + 1] + [
                point.to_shapely()
            ]
            right_coords = [point.to_shapely()] + line_string.coords[
                min_i + 1 :
            ]
            left_line_string = shapely.LineString(left_coords)
            right_line_string = shapely.LineString(right_coords)
            return [left_line_string, right_line_string]

        origin = shapely.Point(0, 0)
        circle = origin.buffer(1.0).boundary
        ellipse = shapely.affinity.scale(circle, self.rx, self.ry)
        ellipse = shapely.affinity.rotate(ellipse, self.x_axis_rotation)
        center = self.get_center()
        ellipse = shapely.affinity.translate(ellipse, center.x, center.y)
        line1 = Line(center, Point.from_tuple(ellipse.coords[0]))
        angle1 = get_angle_to_horizontal_of_line(line1)
        line2 = Line(center, Point.from_tuple(ellipse.coords[-2]))
        angle2 = get_angle_to_horizontal_of_line(line2)
        angle = angle1 - angle2
        if angle >= 0:
            sweep = 1
        else:
            sweep = 0
        if sweep != self.sweep_flag:
            ellipse = shapely.LineString(ellipse.coords[::-1])
        if ellipse.coords[0] == self.p1.to_tuple():
            ellipse = shapely.LineString(
                ellipse.coords[1:] + [ellipse.coords[0]]
            )
        first_split = _split_line_string(ellipse, self.p1)
        multi_line = shapely.MultiLineString([first_split[1], first_split[0]])
        line_string = shapely.ops.linemerge(multi_line)
        second_split = _split_line_string(line_string, self.p2)
        shapely_arc = second_split[0]
        return shapely_arc

    def bbox(self):
        return Bbox.from_bounds(self.to_shapely().bounds)

    def shortened(self, length, start_or_end="end"):
        return shorten_elliptical_arc(self, length, start_or_end)

    def transformed(self, transformation):
        return transform_elliptical_arc(self, transformation)

    def reversed(self):
        return reverse_elliptical_arc(self)

    def to_bezier_curves(self):
        return transform_elliptical_arc_to_bezier_curves(self)


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

    def north_north_west(self):
        return Point(self.x - self.width / 4, self.y - self.height / 2)

    def north(self):
        return Point(self.x, self.y - self.height / 2)

    def north_north_east(self):
        return Point(self.x + self.width / 4, self.y - self.height / 2)

    def north_east(self):
        return Point(self.x + self.width / 2, self.y - self.height / 2)

    def east_north_east(self):
        return Point(self.x + self.width / 2, self.y - self.height / 4)

    def east(self):
        return Point(self.x + self.width / 2, self.y)

    def east_south_east(self):
        return Point(self.x + self.width / 2, self.y + self.width / 4)

    def south_east(self):
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    def south_south_east(self):
        return Point(self.x + self.width / 4, self.y + self.height / 2)

    def south(self):
        return Point(self.x, self.y + self.height / 2)

    def south_south_west(self):
        return Point(self.x - self.width / 4, self.y + self.height / 2)

    def south_west(self):
        return Point(self.x - self.width / 2, self.y + self.height / 2)

    def west_south_west(self):
        return Point(self.x - self.width / 2, self.y + self.height / 4)

    def west(self):
        return Point(self.x - self.width / 2, self.y)

    def west_north_west(self):
        return Point(self.x - self.width / 2, self.y - self.height / 4)

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
        transform_point(bezier_curve.p1, transformation),
        transform_point(bezier_curve.p2, transformation),
        tuple(
            [
                transform_point(point, transformation)
                for point in bezier_curve.control_points
            ]
        ),
    )


def transform_elliptical_arc(elliptical_arc, transformation):
    east = momapy.geometry.Point(
        math.cos(elliptical_arc.x_axis_rotation) * elliptical_arc.rx,
        math.sin(elliptical_arc.x_axis_rotation) * elliptical_arc.rx,
    )
    north = momapy.geometry.Point(
        math.cos(elliptical_arc.x_axis_rotation) * elliptical_arc.ry,
        math.sin(elliptical_arc.x_axis_rotation) * elliptical_arc.ry,
    )
    new_center = momapy.geometry.transform_point(
        momapy.geometry.Point(0, 0), transformation
    )
    new_east = momapy.geometry.transform_point(east, transformation)
    new_north = momapy.geometry.transform_point(north, transformation)
    new_rx = momapy.geometry.Segment(new_center, new_east).length()
    new_ry = momapy.geometry.Segment(new_center, new_north).length()
    new_start_point = momapy.geometry.transform_point(
        elliptical_arc.p1, transformation
    )
    new_end_point = momapy.geometry.transform_point(
        elliptical_arc.p2, transformation
    )
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
        elliptical_arc.arc_flag,
        elliptical_arc.sweep_flag,
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
    if length == 0 or segment.length() == 0:
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
    if length == 0 or bezier_curve.length() == 0:
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
    if length == 0 or elliptical_arc.length() == 0:
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


def get_intersection_of_line_and_point(line, point):
    if line.has_point(point):
        return [point]
    return []


def get_intersection_of_lines(line1, line2):
    slope1 = line1.slope()
    intercept1 = line1.intercept()
    slope2 = line2.slope()
    intercept2 = line2.intercept()
    if line1.is_coincident_to_line(line2):
        intersection = [copy.deepcopy(line1)]
    elif line1.is_parallel_to_line(line2):
        intersection = []
    elif math.isnan(slope1):
        intersection = [Point(line1.p1.x, slope2 * line1.p1.x + intercept2)]
    elif math.isnan(slope2):
        intersection = [Point(line2.p1.x, slope1 * line2.p1.x + intercept1)]
    else:
        d = (line1.p1.x - line1.p2.x) * (line2.p1.y - line2.p2.y) - (
            line1.p1.y - line1.p2.y
        ) * (line2.p1.x - line2.p2.x)
        px = (
            (line1.p1.x * line1.p2.y - line1.p1.y * line1.p2.x)
            * (line2.p1.x - line2.p2.x)
            - (line1.p1.x - line1.p2.x)
            * (line2.p1.x * line2.p2.y - line2.p1.y * line2.p2.x)
        ) / d
        py = (
            (line1.p1.x * line1.p2.y - line1.p1.y * line1.p2.x)
            * (line2.p1.y - line2.p2.y)
            - (line1.p1.y - line1.p2.y)
            * (line2.p1.x * line2.p2.y - line2.p1.y * line2.p2.x)
        ) / d
        intersection = [Point(px, py)]
    return intersection


def get_intersection_of_line_and_segment(line, segment):
    line2 = momapy.geometry.Line(segment.p1, segment.p2)
    intersection = line.get_intersection_with_line(line2)
    if len(intersection) > 0 and isinstance(intersection[0], Point):
        if not segment.has_point(intersection[0]):
            intersection = []
    elif len(intersection) > 0:
        intersection = [segment]
    return intersection


def get_intersection_of_line_and_bezier_curve(line, bezier_curve):
    shapely_object = bezier_curve.to_shapely()
    return get_intersection_of_line_and_shapely_object(line, shapely_object)


def get_intersection_of_line_and_elliptical_arc(line, elliptical_arc):
    shapely_object = elliptical_arc.to_shapely()
    return get_intersection_of_line_and_shapely_object(line, shapely_object)


def get_intersection_of_line_and_shapely_object(line, shapely_object):
    bbox = Bbox.from_bounds(shapely_object.bounds)
    bbox = Bbox(bbox.position, bbox.width + 10, bbox.height + 10)
    line_string = None
    points = []
    anchors = ["north_west", "north_east", "south_east", "south_west"]
    for i, current_anchor in enumerate(anchors):
        if i < len(anchors) - 1:
            next_anchor = anchors[i + 1]
        else:
            next_anchor = anchors[0]
        bbox_segment = Segment(
            getattr(bbox, current_anchor)(), getattr(bbox, next_anchor)()
        )
        bbox_intersection = bbox_segment.get_intersection_with_line(line)
        if (
            len(bbox_intersection) > 0
        ):  # intersection is not empty => intersection has one element
            if isinstance(
                bbox_intersection, Segment
            ):  # intersection is the line
                line_string = bbox_intersection[0].to_shapely()
                break
            else:  # intersection is a point
                points += bbox_intersection
    if line_string is None:
        points = [point.to_shapely() for point in points]
        line_string = shapely.LineString(points)
    shapely_intersection = line_string.intersection(shapely_object)
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


def get_intersection_of_line_and_layout_element(line, layout_element):
    shapely_object = layout_element.to_shapely()
    return get_intersection_of_line_and_shapely_object(line, shapely_object)


def get_intersection_of_line_and_drawing_element(line, drawing_element):
    shapely_object = drawing_element.to_shapely()
    return get_intersection_of_line_and_shapely_object(line, shapely_object)


def get_angle_to_horizontal_of_point(point):
    line = Line(Point(0, 0), point)
    return line.get_angle_to_horizontal()


# angle in radians
def get_angle_to_horizontal_of_line(line):
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
    angle1 = get_angle_to_horizontal_of_line(Line(center, point1))
    angle2 = get_angle_to_horizontal_of_line(Line(center, point2))
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
    return angle - (angle // (2 * math.pi) * (2 * math.pi))


def _get_position_at_fraction(segment_or_curve, fraction):
    line_string = segment_or_curve.to_shapely()
    shapely_point = line_string.interpolate(fraction, normalized=True)
    return Point.from_shapely(shapely_point)


def get_position_at_fraction_of_segment(
    segment,
    fraction: float,
) -> Point:  # fraction in [0, 1]
    return _get_position_at_fraction(segment, fraction)


def get_position_at_fraction_of_bezier_curve(
    bezier_curve,
    fraction: float,
) -> Point:  # fraction in [0, 1]
    return _get_position_at_fraction(bezier_curve, fraction)


def get_position_at_fraction_of_elliptical_arc(
    elliptical_arc,
    fraction: float,
) -> Point:  # fraction in [0, 1]
    return _get_position_at_fraction(elliptical_arc, fraction)


def get_center_parameterization_of_elliptical_arc(elliptical_arc):
    x1, y1 = elliptical_arc.p1.x, elliptical_arc.p1.y
    sigma = elliptical_arc.x_axis_rotation
    x2, y2 = elliptical_arc.p2.x, elliptical_arc.p2.y
    rx = elliptical_arc.rx
    ry = elliptical_arc.ry
    fa = elliptical_arc.arc_flag
    fs = elliptical_arc.sweep_flag
    x1p = math.cos(sigma) * ((x1 - x2) / 2) + math.sin(sigma) * ((y1 - y2) / 2)
    y1p = -math.sin(sigma) * ((x1 - x2) / 2) + math.cos(sigma) * (
        (y1 - y2) / 2
    )
    l = x1p**2 / rx**2 + y1p**2 / ry**2
    if l > 1:
        rx = math.sqrt(l) * rx
        ry = math.sqrt(l) * ry
    r = rx**2 * ry**2 - rx**2 * y1p**2 - ry**2 * x1p**2
    if r < 0:  # due to imprecision? to fix later
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
    return cx, cy, rx, ry, sigma, theta1, theta2, delta_theta


def get_center_of_elliptical_arc(elliptical_arc):
    cx, cy, *_ = get_center_parameterization_of_elliptical_arc(elliptical_arc)
    return Point(cx, cy)


def transform_elliptical_arc_to_bezier_curves(elliptical_arc):
    def _make_angles(angles):
        new_angles = [angles[0]]
        for theta1, theta2 in zip(angles, angles[1:]):
            delta_theta = theta2 - theta1
            if delta_theta > math.pi / 2:
                new_angles.append(theta1 + delta_theta / 2)
            new_angles.append(theta2)
        if len(new_angles) != len(angles):
            new_angles = _make_angles(new_angles)
        return new_angles

    bezier_curves = []
    (
        cx,
        cy,
        rx,
        ry,
        sigma,
        theta1,
        theta2,
        delta_theta,
    ) = get_center_parameterization_of_elliptical_arc(elliptical_arc)
    translation = Translation(cx, cy)
    scaling = Scaling(rx, ry)
    rotation = Rotation(sigma)
    transformation = translation * rotation * scaling
    angles = _make_angles([theta1, theta2])
    for theta1, theta2 in zip(angles, angles[1:]):
        x1 = math.cos(theta1)
        y1 = math.sin(theta1)
        x2 = math.cos(theta2)
        y2 = math.sin(theta2)
        ax = x1
        ay = y1
        bx = x2
        by = y2
        q1 = ax * ax + ay * ay
        q2 = q1 + ax * bx + ay * by
        k2 = (4 / 3) * (math.sqrt(2 * q1 * q2) - q2) / (ax * by - ay * bx)
        cp1x = ax - k2 * ay
        cp1y = ay + k2 * ax
        cp2x = bx + k2 * by
        cp2y = by - k2 * bx
        p1 = Point(x1, y1)
        p2 = Point(x2, y2)
        control_point1 = Point(cp1x, cp1y)
        control_point2 = Point(cp2x, cp2y)
        bezier_curve = BezierCurve(
            p1=p1, p2=p2, control_points=[control_point1, control_point2]
        ).transformed(transformation)
        bezier_curves.append(bezier_curve)
    return bezier_curves


def _get_angle_at_fraction(
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
            break
    return segment.get_angle_to_horizontal()


def get_angle_at_fraction_of_segment(
    segment,
    fraction: float,
) -> Point:  # fraction in [0, 1]
    return _get_angle_at_fraction(segment, fraction)


def get_angle_at_fraction_of_bezier_curve(
    bezier_curve,
    fraction: float,
) -> Point:  # fraction in [0, 1]
    return _get_angle_at_fraction(segment, fraction)


def get_angle_at_fraction_of_elliptical_arc(
    elliptical_arc,
    fraction: float,
) -> Point:  # fraction in [0, 1]
    return _get_angle_at_fraction(segment, fraction)


def _get_position_and_angle_at_fraction(
    segment_or_curve: Union[Segment, BezierCurve, EllipticalArc],
    fraction: float,
) -> Point:  # fraction in [0, 1]
    position = _get_position_at_fraction(segment_or_curve, fraction)
    angle = _get_angle_at_fraction(segment_or_curve, fraction)
    return position, angle


def get_position_and_angle_at_fraction_of_segment(
    segment,
    fraction: float,
) -> Point:  # fraction in [0, 1]
    return _get_position_and_angle_at_fraction(segment, fraction)


def get_position_and_angle_at_fraction_of_bezier_curve(
    bezier_curve,
    fraction: float,
) -> Point:  # fraction in [0, 1]
    return _get_position_angle_at_fraction(segment, fraction)


def get_position_and_angle_at_fraction_of_elliptical_arc(
    elliptical_arc,
    fraction: float,
) -> Point:  # fraction in [0, 1]
    return _get_position_and_angle_at_fraction(segment, fraction)


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


def get_distance_between_line_and_point(line, point):
    distance = abs(
        (line.p2.x - line.p1.x) * (line.p1.y - point.y)
        - (line.p1.x - point.x) * (line.p2.y - line.p1.y)
    ) / math.sqrt((line.p2.x - line.p1.x) ** 2 + (line.p2.y - line.p1.y) ** 2)
    return distance


def get_distance_between_segment_and_point(segment, point):
    a = point.x - segment.p1.x
    b = point.y - segment.p1.y
    c = segment.p2.x - segment.p1.x
    d = segment.p2.y - segment.p1.y
    dot = a * c + b * d
    len_sq = c**2 + d**2
    if len_sq != 0:
        param = dot / len_sq
    else:
        param = -1
    if param < 0:
        xx = segment.p1.x
        yy = segment.p1.y
    elif param > 1:
        xx = segment.p2.x
        yy = segment.p2.y
    else:
        xx = segment.p1.x + param * c
        yy = segment.p1.y + param * d
    dx = point.x - xx
    dy = point.y - yy
    distance = math.sqrt(dx**2 + dy**2)
    return distance


def line_has_point(line, point, max_distance=0.01):
    d = line.get_distance_to_point(point)
    if d <= max_distance:
        return True
    return False


def segment_has_point(segment, point, max_distance=0.01):
    d = segment.get_distance_to_point(point)
    if d <= max_distance:
        return True
    return False


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
