"""Classes and functions for geometry"""

import dataclasses
import typing
import abc
import math
import copy

import numpy
import shapely
import shapely.ops
import bezier.curve

import momapy.builder


ROUNDING = 2


@dataclasses.dataclass(frozen=True)
class GeometryObject(abc.ABC):
    """Base class for geometry objects"""

    @abc.abstractmethod
    def to_shapely(self) -> shapely.Geometry:
        """Compute and return a shapely geometry object that reproduces the geometry object"""
        pass


@dataclasses.dataclass(frozen=True)
class Point(GeometryObject):
    """Class for points"""

    x: float
    y: float

    def __post_init__(self):
        object.__setattr__(self, "x", round(self.x, ROUNDING))
        object.__setattr__(self, "y", round(self.y, ROUNDING))

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

    def __truediv__(self, scalar):
        return Point(self.x / scalar, self.y / scalar)

    def __iter__(self):
        yield self.x
        yield self.y

    def to_matrix(self) -> numpy.ndarray:
        """Return a `numpy.array` representation of the point"""
        m = numpy.array([[self.x], [self.y], [1]], dtype=float)
        return m

    def to_tuple(self) -> tuple[float, float]:
        """Return a tuple representation of the point"""
        return (
            self.x,
            self.y,
        )

    def get_intersection_with_line(self, line: "Line") -> list["Point"]:
        """Compute and return a list of the intersections of the point and a given line"""
        return get_intersection_of_line_and_point(line, self)

    def get_angle_to_horizontal(self) -> float:
        """Return the angle in radians formed by the line passing through the origin and the point and the horizontal"""
        return get_angle_to_horizontal_of_point(self)

    def transformed(self, transformation: "Transformation") -> "Point":
        """Return a copy of the the point transformed by the given transformation"""
        return transform_point(self, transformation)

    def reversed(self) -> "Point":
        """Return a reversed copy of the point"""
        return reverse_point(self)

    def round(self, ndigits=None):
        return Point(round(self.x, ndigits), round(self.y, ndigits))

    def to_shapely(self) -> shapely.Point:
        """Return a shapely point that reproduces the point"""
        return shapely.Point(self.x, self.y)

    def to_fortranarray(self) -> typing.Any:
        """Return a numpy fortran array representation of the point"""
        return numpy.asfortranarray([[self.x], [self.y]])

    def bbox(self) -> "Bbox":
        """Return the bounding box of the point"""
        return Bbox(copy.deepcopy(self), 0, 0)

    def isnan(self) -> bool:
        """Return `true` if the point has a nan coordinate, `false` otherwise"""
        return math.isnan(self.x) or math.isnan(self.y)

    @classmethod
    def from_shapely(cls, point: shapely.Point) -> typing.Self:
        """Return a point reproducing a given shapely point"""
        return cls(float(point.x), float(point.y))

    @classmethod
    def from_fortranarray(cls, fortranarray: typing.Any) -> typing.Self:
        """Return a point from a numpy fortran array representation"""
        return cls(fortranarray[0][0], fortranarray[1][1])

    @classmethod
    def from_tuple(cls, t: tuple[float, float]) -> typing.Self:
        """Return a point from a tuple representation"""
        return cls(t[0], t[1])


@dataclasses.dataclass(frozen=True)
class Line(GeometryObject):
    """Class for lines"""

    p1: Point
    p2: Point

    def slope(self) -> float:
        """Return the slope of the line"""
        if self.p1.x != self.p2.x:
            return round((self.p2.y - self.p1.y) / (self.p2.x - self.p1.x), ROUNDING)
        return float("NAN")  # infinite slope

    def intercept(self) -> float:
        """Return the intercept of the line"""
        slope = self.slope()
        if not math.isnan(slope):
            return self.p1.y - slope * self.p1.x
        else:
            return float("NAN")

    def get_angle_to_horizontal(self) -> float:
        """Return the angle in radians formed by the line and the horizontal"""
        return get_angle_to_horizontal_of_line(self)

    def is_parallel_to_line(self, line: "Line") -> bool:
        """Return `true` if the line is parallel to another given line, and `false` otherwise"""
        return are_lines_parallel(self, line)

    def is_coincident_to_line(self, line: "Line") -> bool:
        """Return `true` if the line is coincident to another given line, and `false` otherwise"""
        return are_lines_coincident(self, line)

    def get_intersection_with_line(self, line: "Line") -> list["Line"] | list["Point"]:
        """Compute and return the instersection of the line with another given line"""
        return get_intersection_of_lines(self, line)

    def get_distance_to_point(self, point: Point) -> float:
        """Compute and return the distance of a given point to the line"""
        return get_distance_between_line_and_point(self, point)

    def has_point(self, point: Point, max_distance: float = 0.01) -> bool:
        """Return `true` if a given point is on the line, `false` otherwise"""
        return line_has_point(self, point, max_distance)

    def transformed(self, transformation: "Transformation") -> "Line":
        """Return a copy of the line transformed with the given transformation"""
        return transform_line(self, transformation)

    def reversed(self) -> "Line":
        """Return a reversed copy of the line"""
        return reverse_line(self)

    def to_shapely(self) -> shapely.LineString:
        """Return a shapeply line string reproducing the line"""
        return shapely.LineString(
            [
                self.p1.to_tuple(),
                self.p2.to_tuple(),
            ]
        )


@dataclasses.dataclass(frozen=True)
class Segment(GeometryObject):
    """Class for segments"""

    p1: Point
    p2: Point

    def length(self) -> float:
        """Return the length of the segment"""
        return math.sqrt((self.p2.x - self.p1.x) ** 2 + (self.p2.y - self.p1.y) ** 2)

    def get_distance_to_point(self, point: Point) -> float:
        """Return the distance of a given point to the segment"""
        return get_distance_between_segment_and_point(self, point)

    def has_point(self, point: Point, max_distance: float = 0.01) -> bool:
        """Return `true` if the given point is on the segment, `false` otherwise"""
        return segment_has_point(self, point, max_distance)

    def get_angle_to_horizontal(self) -> float:
        """Compute and return the angle formed by the segment and the horizontal"""
        return get_angle_to_horizontal_of_line(self)

    def get_intersection_with_line(self, line: Line) -> list[Point] | list["Segment"]:
        """Compute and return the intersection of the segment with a given line"""
        return get_intersection_of_line_and_segment(line, self)

    def get_position_at_fraction(self, fraction: float) -> Point:
        """Compute and return the position on the segment at a given fraction (of the total length)"""
        return get_position_at_fraction_of_segment(self, fraction)

    def get_angle_at_fraction(self, fraction: float) -> float:
        """Compute and return the angle in radians formed by the segment and the horizontal at a given fraction (of the total length)"""
        return get_angle_at_fraction_of_segment(self, fraction)

    def get_position_and_angle_at_fraction(
        self, fraction: float
    ) -> tuple[Point, float]:
        """Compute and return the position on the segment at a given fraction and the angle in radians formed of the segment and the horizontal at that position"""
        return get_position_and_angle_at_fraction_of_segment(self, fraction)

    def shortened(
        self,
        length: float,
        start_or_end: typing.Literal["start", "end"] = "end",
    ) -> "Segment":
        """Compute and return a copy of the segment shortened by a given length"""
        return shorten_segment(self, length, start_or_end)

    def transformed(self, transformation: "Transformation") -> "Segment":
        """Compute and return a copy of the segment transformed with a given transformation"""
        return transform_segment(self, transformation)

    def reversed(self) -> "Segment":
        """Compute and return a reversed copy of the segment"""
        return reverse_segment(self)

    def to_shapely(self) -> shapely.LineString:
        """Return a shapely line string reproducing the segment"""
        return shapely.LineString(
            [
                self.p1.to_tuple(),
                self.p2.to_tuple(),
            ]
        )

    def bbox(self) -> "Bbox":
        """Compute and return the bounding box of the segment"""
        return Bbox.from_bounds(self.to_shapely().bounds)

    @classmethod
    def from_shapely(cls, line_string: shapely.LineString) -> typing.Self:
        """Compute and return the segment reproducing a shapely line string"""
        shapely_points = line_string.boundary.geoms
        return cls(
            Point.from_shapely(shapely_points[0]),
            Point.from_shapely(shapely_points[1]),
        )


@dataclasses.dataclass(frozen=True)
class BezierCurve(GeometryObject):
    """Class for bezier curves"""

    p1: Point
    p2: Point
    control_points: tuple[Point, ...] = dataclasses.field(default_factory=tuple)

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
        return cls(points[0], points[-1], tuple(points[1:-1]))

    def length(self) -> float:
        """Compute and return the length of the bezier curve"""
        return self._to_bezier().length

    def evaluate(self, s: float) -> Point:
        """Compute and return the point at a given parameter value"""
        evaluation = self._to_bezier().evaluate(s)
        return Point.from_fortranarray(evaluation)

    def evaluate_multi(self, s: numpy.ndarray) -> list[Point]:
        """Compute and return the points at given parameter values"""
        evaluation = self._to_bezier().evaluate_multi(s)
        return [Point(e[0], e[1]) for e in evaluation.T]

    def get_intersection_with_line(self, line: Line) -> list[Point] | list[Segment]:
        """Compute and return the intersection of the bezier curve with a given line"""
        return get_intersection_of_line_and_bezier_curve(line, self)

    def get_position_at_fraction(self, fraction: float):
        """Compute and return the position on the bezier curve at a given fraction (of the total length)"""

        return get_position_at_fraction_of_bezier_curve(self, fraction)

    def get_angle_at_fraction(self, fraction: float):
        """Compute and return the angle in radians formed by the tangent of the bezier curve and the horizontal at a given fraction (of the total length)"""
        return get_angle_at_fraction_of_bezier_curve(self, fraction)

    def get_position_and_angle_at_fraction(self, fraction: float):
        """Compute and return the position on the bezier curve at a given fraction and the angle in radians formed of the tangent of the bezier curve and the horizontal at that position"""
        return get_position_and_angle_at_fraction_of_bezier_curve(self, fraction)

    def shortened(
        self, length: float, start_or_end: typing.Literal["start", "end"] = "end"
    ) -> "BezierCurve":
        """Compute and return a copy of the bezier curve shortened by a given length"""
        return shorten_bezier_curve(self, length, start_or_end)

    def transformed(self, transformation):
        """Compute and return a copy of the bezier curve transformed with a given transformation"""
        return transform_bezier_curve(self, transformation)

    def reversed(self):
        """Compute and return a reversed copy of the bezier curve"""
        return reverse_bezier_curve(self)

    def to_shapely(self, n_segs=50):
        """Compute and return a shapely line string reproducing the bezier curve"""

        points = self.evaluate_multi(
            numpy.arange(0, 1 + 1 / n_segs, 1 / n_segs, dtype="double")
        )
        return shapely.LineString([point.to_tuple() for point in points])

    def bbox(self):
        """Compute and return the bounding box of the bezier curve"""
        return Bbox.from_bounds(self.to_shapely().bounds)


@dataclasses.dataclass(frozen=True)
class EllipticalArc(GeometryObject):
    """Class for elliptical arcs"""

    p1: Point
    p2: Point
    rx: float
    ry: float
    x_axis_rotation: float
    arc_flag: int
    sweep_flag: int

    def get_intersection_with_line(self, line: Line) -> list[Point]:
        """Compute and return the intersection of the elliptical arc with a given line"""
        return get_intersection_of_line_and_elliptical_arc(line, self)

    def get_center_parameterization(
        self,
    ) -> tuple[float, float, float, float, float, float, float, float]:
        """Compute and return the center paramaterizaion of the elliptical arc (cx, cy, rx, ry, sigma, theta1, theta2, delta_theta)"""
        return get_center_parameterization_of_elliptical_arc(self)

    def get_center(self) -> Point:
        """Compute and return the center of the elliptical arc"""
        return get_center_of_elliptical_arc(self)

    def get_position_at_fraction(self, fraction: float) -> Point:
        """Compute and return the position on the elliptical arc at a given fraction (of the total length)"""
        return get_position_at_fraction_of_elliptical_arc(self, fraction)

    def get_angle_at_fraction(self, fraction: float) -> float:
        """Compute and return the angle in radians formed by the tangent of the elliptical arc and the horizontal at a given fraction (of the total length)"""
        return get_angle_at_fraction_of_elliptical_arc(self, fraction)

    def get_position_and_angle_at_fraction(
        self, fraction: float
    ) -> tuple[Point, float]:
        """Compute and return the position on the elliptical arc at a given fraction and the angle in radians formed of the tangent of the bezier curve at that position and the horizontal"""
        return get_position_and_angle_at_fraction_of_elliptical_arc(self, fraction)

    def to_shapely(self):
        """Compute and return a shapely linestring reproducing the elliptical arc"""

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
            left_coords = line_string.coords[0 : min_i + 1] + [point.to_shapely()]
            right_coords = [point.to_shapely()] + line_string.coords[min_i + 1 :]
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
            ellipse = shapely.LineString(ellipse.coords[1:] + [ellipse.coords[0]])
        first_split = _split_line_string(ellipse, self.p1)
        multi_line = shapely.MultiLineString([first_split[1], first_split[0]])
        line_string = shapely.ops.linemerge(multi_line)
        second_split = _split_line_string(line_string, self.p2)
        shapely_arc = second_split[0]
        return shapely_arc

    def bbox(self) -> "Bbox":
        """Compute and return the bounding box of the elliptical arc"""
        return Bbox.from_bounds(self.to_shapely().bounds)

    def shortened(
        self,
        length: float,
        start_or_end: typing.Literal["start", "end"] = "end",
    ) -> "EllipticalArc":
        """Compute and return a copy of the elliptical arc shortened by a given length"""
        return shorten_elliptical_arc(self, length, start_or_end)

    def transformed(self, transformation: "Transformation") -> "EllipticalArc":
        """Compute and return a copy of the elliptical arc transformed by a given transformation"""
        return transform_elliptical_arc(self, transformation)

    def reversed(self) -> "EllipticalArc":
        """Compute and return a reversed copy of the elliptical arc"""
        return reverse_elliptical_arc(self)

    def to_bezier_curves(self) -> BezierCurve:
        """Compute and return a bezier curve reproducing the elliptical arc"""
        return transform_elliptical_arc_to_bezier_curves(self)

    def length(self) -> float:
        return self.to_shapely().length


@dataclasses.dataclass(frozen=True)
class Bbox(object):
    """Class for bounding boxes"""

    position: Point
    width: float
    height: float

    @property
    def x(self) -> float:
        """The x coordinate of the bounding box"""
        return self.position.x

    @property
    def y(self) -> float:
        """The y coordinate of the bounding box"""
        return self.position.y

    def size(self) -> tuple[float, float]:
        """The size of the bounding box"""
        return (self.width, self.height)

    def anchor_point(self, anchor_point: str) -> Point:
        """Return a given anchor point of the bounding box"""
        return getattr(self, anchor_point)()

    def north_west(self) -> Point:
        """Return the north west anchor point of the bounding box"""
        return Point(self.x - self.width / 2, self.y - self.height / 2)

    def north_north_west(self) -> Point:
        """Return the north north west anchor point of the bounding box"""
        return Point(self.x - self.width / 4, self.y - self.height / 2)

    def north(self) -> Point:
        """Return the north anchor point of the bounding box"""
        return Point(self.x, self.y - self.height / 2)

    def north_north_east(self) -> Point:
        """Return the north north east anchor point of the bounding box"""
        return Point(self.x + self.width / 4, self.y - self.height / 2)

    def north_east(self) -> Point:
        """Return the north east anchor point of the bounding box"""
        return Point(self.x + self.width / 2, self.y - self.height / 2)

    def east_north_east(self) -> Point:
        """Return the east north east anchor point of the bounding box"""
        return Point(self.x + self.width / 2, self.y - self.height / 4)

    def east(self) -> Point:
        """Return the east anchor point of the bounding box"""
        return Point(self.x + self.width / 2, self.y)

    def east_south_east(self) -> Point:
        """Return the east south east anchor point of the bounding box"""
        return Point(self.x + self.width / 2, self.y + self.width / 4)

    def south_east(self) -> Point:
        """Return the south east anchor point of the bounding box"""
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    def south_south_east(self) -> Point:
        """Return the south south east anchor point of the bounding box"""
        return Point(self.x + self.width / 4, self.y + self.height / 2)

    def south(self) -> Point:
        """Return the south anchor point of the bounding box"""
        return Point(self.x, self.y + self.height / 2)

    def south_south_west(self) -> Point:
        """Return the south south west anchor point of the bounding box"""
        return Point(self.x - self.width / 4, self.y + self.height / 2)

    def south_west(self) -> Point:
        """Return the south west anchor point of the bounding box"""
        return Point(self.x - self.width / 2, self.y + self.height / 2)

    def west_south_west(self) -> Point:
        """Return the west south west anchor point of the bounding box"""
        return Point(self.x - self.width / 2, self.y + self.height / 4)

    def west(self) -> Point:
        """Return the west anchor point of the bounding box"""
        return Point(self.x - self.width / 2, self.y)

    def west_north_west(self) -> Point:
        """Return the west north west anchor point of the bounding box"""
        return Point(self.x - self.width / 2, self.y - self.height / 4)

    def center(self) -> Point:
        """Return the center anchor point of the bounding box"""
        return Point(self.x, self.y)

    def isnan(self) -> bool:
        """Return `true` if the position of the bounding box has a `nan` coordinate, `false` otherwise"""
        return self.position.isnan()

    @classmethod
    def from_bounds(cls, bounds: tuple[float, float, float, float]):
        """Create and return a bounding box from shaply bounds (min_x, min_y, max_x, max_y)"""
        return cls(
            Point((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2),
            bounds[2] - bounds[0],
            bounds[3] - bounds[1],
        )


@dataclasses.dataclass(frozen=True)
class Transformation(abc.ABC):
    """Base class for transformations"""

    @abc.abstractmethod
    def to_matrix(self) -> numpy.typing.NDArray:
        """Return a matrix representation of the transformation"""
        pass

    @abc.abstractmethod
    def inverted(self) -> "Transformation":
        """Compute and return the inverse transformation"""
        pass

    def __mul__(self, other):
        return MatrixTransformation(numpy.matmul(self.to_matrix(), other.to_matrix()))


@dataclasses.dataclass(frozen=True)
class MatrixTransformation(Transformation):
    """Class for matrix transformations"""

    m: numpy.typing.NDArray

    def to_matrix(self) -> numpy.typing.NDArray:
        """Return a matrix representation of the matrix transformation"""
        return self.m

    def inverted(self) -> Transformation:
        """Compute and return the inverse of the matrix transformation"""
        return invert_matrix_transformation(self)


@dataclasses.dataclass(frozen=True)
class Rotation(Transformation):
    """Class for rotations"""

    angle: float
    point: Point | None = None

    def to_matrix(self) -> numpy.typing.NDArray:
        """Compute and return a matrix representation of the rotation"""
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

    def inverted(self) -> Transformation:
        """Compute and return the inverse of the rotation"""
        return invert_rotation(self)


@dataclasses.dataclass(frozen=True)
class Translation(Transformation):
    """Class for translations"""

    tx: float
    ty: float

    def to_matrix(self) -> numpy.typing.NDArray:
        """Return a matrix representation of the translation"""
        m = numpy.array([[1, 0, self.tx], [0, 1, self.ty], [0, 0, 1]], dtype=float)
        return m

    def inverted(self) -> Transformation:
        """Compute and return the inverse of the translation"""
        return invert_translation(self)


@dataclasses.dataclass(frozen=True)
class Scaling(Transformation):
    """Class for scalings"""

    sx: float
    sy: float

    def to_matrix(self) -> numpy.typing.NDArray:
        """Return a matrix representation of the scaling"""
        m = numpy.array(
            [
                [self.sx, 0, 0],
                [0, self.sy, 0],
                [0, 0, 1],
            ],
            dtype=float,
        )
        return m

    def inverted(self) -> Transformation:
        """Compute and return the inverse of the scaling"""
        return invert_scaling(self)


def transform_point(point: Point, transformation: Transformation) -> Point:
    m = numpy.matmul(transformation.to_matrix(), point.to_matrix())
    return Point(m[0][0], m[1][0])


def transform_line(line: Line, transformation: Transformation) -> Line:
    return Line(
        transform_point(line.p1, transformation),
        transform_point(line.p2, transformation),
    )


def transform_segment(segment: Segment, transformation: Transformation) -> Segment:
    return Segment(
        transform_point(segment.p1, transformation),
        transform_point(segment.p2, transformation),
    )


def transform_bezier_curve(
    bezier_curve: BezierCurve, transformation: Transformation
) -> BezierCurve:
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


def transform_elliptical_arc(
    elliptical_arc: EllipticalArc, transformation: Transformation
) -> EllipticalArc:
    east = Point(
        math.cos(elliptical_arc.x_axis_rotation) * elliptical_arc.rx,
        math.sin(elliptical_arc.x_axis_rotation) * elliptical_arc.rx,
    )
    north = Point(
        math.cos(elliptical_arc.x_axis_rotation) * elliptical_arc.ry,
        math.sin(elliptical_arc.x_axis_rotation) * elliptical_arc.ry,
    )
    new_center = transform_point(Point(0, 0), transformation)
    new_east = transform_point(east, transformation)
    new_north = transform_point(north, transformation)
    new_rx = Segment(new_center, new_east).length()
    new_ry = Segment(new_center, new_north).length()
    new_start_point = transform_point(elliptical_arc.p1, transformation)
    new_end_point = transform_point(elliptical_arc.p2, transformation)
    new_x_axis_rotation = math.degrees(
        get_angle_to_horizontal_of_line(Line(new_center, new_east))
    )
    return EllipticalArc(
        p1=new_start_point,
        p2=new_end_point,
        rx=new_rx,
        ry=new_ry,
        x_axis_rotation=new_x_axis_rotation,
        arc_flag=elliptical_arc.arc_flag,
        sweep_flag=elliptical_arc.sweep_flag,
    )


def reverse_point(point: Point) -> Point:
    return Point(point.x, point.y)


def reverse_line(line: Line) -> Line:
    return Line(line.p2, line.p1)


def reverse_segment(segment):
    return Segment(segment.p2, segment.p1)


def reverse_bezier_curve(bezier_curve: BezierCurve) -> BezierCurve:
    return BezierCurve(
        bezier_curve.p2, bezier_curve.p1, bezier_curve.control_points[::-1]
    )


def reverse_elliptical_arc(elliptical_arc: EllipticalArc) -> EllipticalArc:
    return EllipticalArc(
        elliptical_arc.p2,
        elliptical_arc.p1,
        elliptical_arc.rx,
        elliptical_arc.ry,
        elliptical_arc.x_axis_rotation,
        elliptical_arc.arc_flag,
        abs(elliptical_arc.sweep_flag - 1),
    )


def shorten_segment(
    segment: Segment,
    length: float,
    start_or_end: typing.Literal["start", "end"] = "end",
) -> Segment:
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


def shorten_bezier_curve(
    bezier_curve: BezierCurve,
    length: float,
    start_or_end: typing.Literal["start", "end"] = "end",
) -> BezierCurve:
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
            horizontal_line = BezierCurve(point - (5, 0), point + (5, 0))._to_bezier()
            s = lib_bezier_curve.intersect(horizontal_line)[0][0]
            lib_shortened_bezier_curve = lib_bezier_curve.specialize(0, s)
            shortened_bezier_curve = BezierCurve._from_bezier(
                lib_shortened_bezier_curve
            )
    return shortened_bezier_curve


def shorten_elliptical_arc(
    elliptical_arc: EllipticalArc,
    length: float,
    start_or_end: typing.Literal["start", "end"] = "end",
):
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
            shortened_elliptical_arc = dataclasses.replace(elliptical_arc, p2=point)
    return shortened_elliptical_arc


def invert_matrix_transformation(
    matrix_transformation: MatrixTransformation,
) -> MatrixTransformation:
    return MatrixTransformation(numpy.linalg.inv(matrix_transformation.m))


def invert_rotation(rotation: Rotation) -> Rotation:
    return Rotation(-rotation.angle, rotation.point)


def invert_translation(translation: Translation) -> Translation:
    return Translation(-translation.tx, -translation.ty)


def invert_scaling(scaling: Scaling) -> Scaling:
    return Scaling(-scaling.sx, -scaling.sy)


def get_intersection_of_line_and_point(line: Line, point: Point) -> list[Point]:
    if line.has_point(point):
        return [point]
    return []


def get_intersection_of_lines(line1: Line, line2: Line) -> list[Line] | list[Point]:
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


def get_intersection_of_line_and_segment(
    line: Line, segment: Segment
) -> list[Point] | list[Segment] | list[Line]:
    line2 = Line(segment.p1, segment.p2)
    intersection = line.get_intersection_with_line(line2)
    if len(intersection) > 0 and isinstance(intersection[0], Point):
        sorted_xs = sorted([segment.p1.x, segment.p2.x])
        sorted_ys = sorted([segment.p1.y, segment.p2.y])
        if not (
            intersection[0].x >= sorted_xs[0]
            and intersection[0].x <= sorted_xs[-1]
            and intersection[0].y >= sorted_ys[0]
            and intersection[0].y <= sorted_ys[-1]
        ):
            intersection = []
    elif len(intersection) > 0:
        intersection = [segment]
    return intersection


def get_intersection_of_line_and_bezier_curve(
    line: Line, bezier_curve: BezierCurve
) -> list[Point] | list[Segment]:
    shapely_object = bezier_curve.to_shapely()
    return get_intersection_of_line_and_shapely_object(line, shapely_object)


def get_intersection_of_line_and_elliptical_arc(
    line: Line, elliptical_arc: EllipticalArc
) -> list[Point] | list[Segment]:
    shapely_object = elliptical_arc.to_shapely()
    return get_intersection_of_line_and_shapely_object(line, shapely_object)


def get_intersection_of_line_and_shapely_object(
    line: Line, shapely_object: shapely.Geometry
) -> list[Point] | list[Segment]:
    intersection = []
    for shapely_geom in shapely_object.geoms:
        bbox = Bbox.from_bounds(shapely_object.bounds)
        slope = line.slope()
        north_west = bbox.north_west()
        south_east = bbox.south_east()
        offset = 100.0
        if not math.isnan(slope):
            intercept = line.intercept()
            left_x = north_west.x - offset
            left_y = slope * left_x + intercept
            right_x = south_east.x + offset
            right_y = slope * right_x + intercept
        else:
            left_x = line.p1.x
            left_y = north_west.y - offset
            right_x = line.p1.x
            right_y = south_east.y + offset
        left_point = Point(left_x, left_y)
        right_point = Point(right_x, right_y)
        line_string = shapely.LineString(
            [left_point.to_shapely(), right_point.to_shapely()]
        )
        shapely_intersection = line_string.intersection(shapely_geom)
        if not hasattr(shapely_intersection, "geoms"):
            shapely_intersection = [shapely_intersection]
        else:
            shapely_intersection = shapely_intersection.geoms
        for shapely_obj in shapely_intersection:
            if not shapely.is_empty(shapely_obj):
                if isinstance(shapely_obj, shapely.Point):
                    intersection_obj = Point.from_shapely(shapely_obj)
                elif isinstance(shapely_obj, shapely.LineString):
                    intersection_obj = Segment.from_shapely(shapely_obj)
                intersection.append(intersection_obj)
    return intersection


def get_shapely_object_bbox(shapely_object: shapely.Geometry) -> Bbox:
    return Bbox.from_bounds(shapely_object.bounds)


def get_shapely_object_border(
    shapely_object: shapely.Geometry, point: Point, center: Point | None = None
) -> Point | None:
    if center is None:
        bbox = get_shapely_object_bbox(shapely_object)
        center = bbox.center()
    if center.isnan():
        return Point(float("nan"), float("nan"))
    line = Line(center, point)
    intersection = get_intersection_of_line_and_shapely_object(line, shapely_object)
    candidate_points = []
    for intersection_obj in intersection:
        if isinstance(intersection_obj, Segment):
            candidate_points.append(intersection_obj.p1)
            candidate_points.append(intersection_obj.p2)
        elif isinstance(intersection_obj, Point):
            candidate_points.append(intersection_obj)
    intersection_point = None
    max_d = -1
    ok_direction_exists = False
    d1 = get_distance_between_points(point, center)
    for candidate_point in candidate_points:
        d2 = get_distance_between_points(candidate_point, point)
        d3 = get_distance_between_points(candidate_point, center)
        candidate_ok_direction = not d2 > d1 or d2 < d3
        if candidate_ok_direction or not ok_direction_exists:
            if candidate_ok_direction and not ok_direction_exists:
                ok_direction_exists = True
                max_d = -1
            if d3 > max_d:
                max_d = d3
                intersection_point = candidate_point
    return intersection_point


def get_shapely_object_angle(
    shapely_object: shapely.Geometry,
    angle: float,
    unit: typing.Literal["degrees", "radians"] = "degrees",
    center: Point | None = None,
) -> Point | None:
    if unit == "degrees":
        angle = math.radians(angle)
    angle = -angle
    d = 100
    if center is None:
        bbox = get_shapely_object_bbox(shapely_object)
        center = bbox.center()
        if center.isnan():
            return Point(float("nan"), float("nan"))
    point = center + (d * math.cos(angle), d * math.sin(angle))
    return get_shapely_object_border(shapely_object, point, center)


def get_shapely_object_anchor_point(
    shapely_object: shapely.Geometry,
    anchor_point: str,
    center: Point | None = None,
) -> Point:
    bbox = get_shapely_object_bbox(shapely_object)
    if center is None:
        center = bbox.center()
    if center.isnan():
        return Point(float("nan"), float("nan"))
    point = bbox.anchor_point(anchor_point)
    return get_shapely_object_border(shapely_object, point, center)


def get_angle_to_horizontal_of_point(point: Point) -> float:
    line = Line(Point(0, 0), point)
    return line.get_angle_to_horizontal()


# angle in radians
def get_angle_to_horizontal_of_line(line: Line | Segment) -> float:
    x1 = line.p1.x
    y1 = line.p1.y
    x2 = line.p2.x
    y2 = line.p2.y
    angle = math.atan2(y2 - y1, x2 - x1)
    return get_normalized_angle(angle)


def are_lines_parallel(line1: Line, line2: Line) -> bool:
    slope1 = line1.slope()
    slope2 = line2.slope()
    if math.isnan(slope1) and math.isnan(slope2):
        return True
    return slope1 == slope2


def are_lines_coincident(line1: Line, line2: Line) -> bool:
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
def is_angle_in_sector(
    angle: float, center: Point, point1: Point, point2: Point
) -> bool:
    angle1 = get_angle_to_horizontal_of_line(Line(center, point1))
    angle2 = get_angle_to_horizontal_of_line(Line(center, point2))
    return is_angle_between(angle, angle1, angle2)


# angles in radians
def is_angle_between(angle: float, start_angle: float, end_angle: float) -> bool:
    angle = get_normalized_angle(angle)
    start_angle = get_normalized_angle(start_angle)
    end_angle = get_normalized_angle(end_angle)
    if start_angle < end_angle:
        if angle >= start_angle and angle <= end_angle:
            return True
    else:
        if start_angle <= angle <= 2 * math.pi or angle >= 0 and angle <= end_angle:
            return True
    return False


# angle is in radians; return angle between 0 and 2 * pi
def get_normalized_angle(angle: float) -> float:
    return angle - (angle // (2 * math.pi) * (2 * math.pi))


def _get_position_at_fraction(segment_or_curve, fraction):
    line_string = segment_or_curve.to_shapely()
    shapely_point = line_string.interpolate(fraction, normalized=True)
    return Point.from_shapely(shapely_point)


def get_position_at_fraction_of_segment(
    segment: Segment,
    fraction: float,
) -> Point:  # fraction in [0, 1]
    return _get_position_at_fraction(segment, fraction)


def get_position_at_fraction_of_bezier_curve(
    bezier_curve: BezierCurve,
    fraction: float,
) -> Point:  # fraction in [0, 1]
    return _get_position_at_fraction(bezier_curve, fraction)


def get_position_at_fraction_of_elliptical_arc(
    elliptical_arc: EllipticalArc,
    fraction: float,
) -> Point:  # fraction in [0, 1]
    return _get_position_at_fraction(elliptical_arc, fraction)


def get_center_parameterization_of_elliptical_arc(
    elliptical_arc: EllipticalArc,
) -> tuple[float, float, float, float, float, float, float, float]:
    x1, y1 = elliptical_arc.p1.x, elliptical_arc.p1.y
    sigma = elliptical_arc.x_axis_rotation
    x2, y2 = elliptical_arc.p2.x, elliptical_arc.p2.y
    rx = elliptical_arc.rx
    ry = elliptical_arc.ry
    fa = elliptical_arc.arc_flag
    fs = elliptical_arc.sweep_flag
    x1p = math.cos(sigma) * ((x1 - x2) / 2) + math.sin(sigma) * ((y1 - y2) / 2)
    y1p = -math.sin(sigma) * ((x1 - x2) / 2) + math.cos(sigma) * ((y1 - y2) / 2)
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


def get_center_of_elliptical_arc(elliptical_arc: EllipticalArc) -> Point:
    cx, cy, *_ = get_center_parameterization_of_elliptical_arc(elliptical_arc)
    return Point(cx, cy)


def transform_elliptical_arc_to_bezier_curves(
    elliptical_arc: EllipticalArc,
) -> list[BezierCurve]:
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
            p1=p1, p2=p2, control_points=tuple([control_point1, control_point2])
        ).transformed(transformation)
        bezier_curves.append(bezier_curve)
    return bezier_curves


def _get_angle_at_fraction(
    segment_or_curve: Segment | BezierCurve | EllipticalArc,
    fraction: float,
) -> float:  # fraction in [0, 1]
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
    segment: Segment,
    fraction: float,
) -> float:  # fraction in [0, 1]
    return _get_angle_at_fraction(segment, fraction)


def get_angle_at_fraction_of_bezier_curve(
    bezier_curve: BezierCurve,
    fraction: float,
) -> float:  # fraction in [0, 1]
    return _get_angle_at_fraction(bezier_curve, fraction)


def get_angle_at_fraction_of_elliptical_arc(
    elliptical_arc: EllipticalArc,
    fraction: float,
) -> float:  # fraction in [0, 1]
    return _get_angle_at_fraction(elliptical_arc, fraction)


def _get_position_and_angle_at_fraction(
    segment_or_curve: Segment | BezierCurve | EllipticalArc,
    fraction: float,
) -> tuple[Point, float]:  # fraction in [0, 1]
    position = _get_position_at_fraction(segment_or_curve, fraction)
    angle = _get_angle_at_fraction(segment_or_curve, fraction)
    return position, angle


def get_position_and_angle_at_fraction_of_segment(
    segment: Segment,
    fraction: float,
) -> tuple[Point, float]:  # fraction in [0, 1]
    return _get_position_and_angle_at_fraction(segment, fraction)


def get_position_and_angle_at_fraction_of_bezier_curve(
    bezier_curve: BezierCurve,
    fraction: float,
) -> tuple[Point, float]:  # fraction in [0, 1]
    return _get_position_and_angle_at_fraction(bezier_curve, fraction)


def get_position_and_angle_at_fraction_of_elliptical_arc(
    elliptical_arc: EllipticalArc,
    fraction: float,
) -> tuple[Point, float]:  # fraction in [0, 1]
    return _get_position_and_angle_at_fraction(elliptical_arc, fraction)


# angle is in radians between -pi and pi
def get_angle_between_segments(segment1: Segment, segment2: Segment) -> float:
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


def get_distance_between_points(p1: Point, p2: Point) -> float:
    return Segment(p1, p2).length()


def get_distance_between_line_and_point(line: Line, point: Point) -> float:
    distance = abs(
        (line.p2.x - line.p1.x) * (line.p1.y - point.y)
        - (line.p1.x - point.x) * (line.p2.y - line.p1.y)
    ) / math.sqrt((line.p2.x - line.p1.x) ** 2 + (line.p2.y - line.p1.y) ** 2)
    return distance


def get_distance_between_segment_and_point(segment: Segment, point: Point) -> float:
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


def line_has_point(line: Line, point: Point, max_distance: float = 0.01) -> bool:
    d = line.get_distance_to_point(point)
    if d <= max_distance:
        return True
    return False


def segment_has_point(
    segment: Segment, point: Point, max_distance: float = 0.01
) -> bool:
    d = segment.get_distance_to_point(point)
    if d <= max_distance:
        return True
    return False


# Given a frame F defined in another reference frame by its origin,
# unit x axis vector, and unit y axis vector, returns the transformation
# that must be applied to a point defined in F to obtain its coordinates
# in the reference frame.
def get_transformation_for_frame(
    origin: Point, unit_x: Point, unit_y: Point
) -> MatrixTransformation:
    m = numpy.array(
        [
            [
                unit_x.x - origin.x,
                unit_y.x - origin.x,
                origin.x,
            ],
            [
                unit_x.y - origin.y,
                unit_y.y - origin.y,
                origin.y,
            ],
            [0, 0, 1],
        ],
        dtype=float,
    )
    return MatrixTransformation(m)


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


def _point_builder_post_init(self):
    object.__setattr__(self, "x", round(self.x, ROUNDING))
    object.__setattr__(self, "y", round(self.y, ROUNDING))


PointBuilder = momapy.builder.get_or_make_builder_cls(
    Point,
    builder_namespace={
        "__add__": _point_builder_add,
        "__sub__": _point_builder_sub,
        "__mul__": _point_builder_mul,
        "__div__": _point_builder_div,
        "__iter__": _point_builder_iter,
        "__post_init__": _point_builder_post_init,
    },
)

momapy.builder.register_builder_cls(PointBuilder)

BboxBuilder = momapy.builder.get_or_make_builder_cls(Bbox)

momapy.builder.register_builder_cls(BboxBuilder)
