"""Geometric primitives and transformations for momapy.

This module provides geometric classes and functions for working with points, lines,
segments, curves, and transformations. It includes support for Bezier curves,
elliptical arcs, and various geometric operations.

Examples:
    >>> from momapy.geometry import Point, Line, Segment, Rotation, Translation
    >>> # Create points
    >>> p1 = Point(0, 0)
    >>> p2 = Point(10, 10)
    >>> # Create a line
    >>> line = Line(p1, p2)
    >>> line.slope()
    1.0
    >>> # Create a segment
    >>> segment = Segment(p1, p2)
    >>> segment.length()
    14.14...
    >>> # Apply transformations
    >>> rotated = p1.transformed(Rotation(math.pi / 2, p2))
"""

import dataclasses
import typing
import typing_extensions
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
    """Abstract base class for all geometry objects."""

    @abc.abstractmethod
    def to_shapely(self) -> shapely.Geometry:
        """Convert to a shapely geometry object.

        Returns:
            A shapely geometry representing this object.
        """
        pass


@dataclasses.dataclass(frozen=True)
class Point(GeometryObject):
    """Represents a 2D point with x and y coordinates.

    Attributes:
        x: The x-coordinate.
        y: The y-coordinate.

    Examples:
        >>> p = Point(10, 20)
        >>> p.x
        10
        >>> p + (5, 5)
        Point(x=15, y=25)
    """

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
        """Convert to a 3x1 numpy matrix for transformation operations.

        Returns:
            A numpy array [[x], [y], [1]].
        """
        m = numpy.array([[self.x], [self.y], [1]], dtype=float)
        return m

    def to_tuple(self) -> tuple[float, float]:
        """Convert to a tuple.

        Returns:
            Tuple (x, y).
        """
        return (
            self.x,
            self.y,
        )

    def get_intersection_with_line(self, line: "Line") -> list["Point"]:
        """Get intersection points with a line.

        Args:
            line: The line to intersect with.

        Returns:
            List of intersection points (empty if no intersection).
        """
        return get_intersection_of_line_and_point(line, self)

    def get_angle_to_horizontal(self) -> float:
        """Get the angle from origin to this point relative to horizontal.

        Returns:
            Angle in radians.
        """
        return get_angle_to_horizontal_of_point(self)

    def transformed(self, transformation: "Transformation") -> "Point":
        """Apply a transformation to this point.

        Args:
            transformation: The transformation to apply.

        Returns:
            A new transformed Point.
        """
        return transform_point(self, transformation)

    def reversed(self) -> "Point":
        """Return a reversed copy (identity for points).

        Returns:
            A copy of the point.
        """
        return reverse_point(self)

    def round(self, ndigits=None):
        """Round coordinates to specified digits.

        Args:
            ndigits: Number of decimal places.

        Returns:
            A new Point with rounded coordinates.
        """
        return Point(round(self.x, ndigits), round(self.y, ndigits))

    def to_shapely(self) -> shapely.Point:
        """Convert to a shapely Point.

        Returns:
            A shapely Point.
        """
        return shapely.Point(self.x, self.y)

    def to_fortranarray(self) -> typing.Any:
        """Convert to a numpy Fortran array.

        Returns:
            A 2x1 Fortran array [[x], [y]].
        """
        return numpy.asfortranarray([[self.x], [self.y]])

    def bbox(self) -> "Bbox":
        """Get the bounding box of this point.

        Returns:
            A Bbox with zero width and height.
        """
        return Bbox(copy.deepcopy(self), 0, 0)

    def isnan(self) -> bool:
        """Check if either coordinate is NaN.

        Returns:
            True if x or y is NaN.
        """
        return math.isnan(self.x) or math.isnan(self.y)

    @classmethod
    def from_shapely(cls, point: shapely.Point) -> typing_extensions.Self:
        """Create a Point from a shapely Point.

        Args:
            point: A shapely Point.

        Returns:
            A new Point.
        """
        return cls(float(point.x), float(point.y))

    @classmethod
    def from_fortranarray(cls, fortranarray: typing.Any) -> typing_extensions.Self:
        """Create a Point from a numpy Fortran array.

        Args:
            fortranarray: A 2x1 array [[x], [y]].

        Returns:
            A new Point.
        """
        return cls(fortranarray[0][0], fortranarray[1][0])

    @classmethod
    def from_tuple(cls, t: tuple[float, float]) -> typing_extensions.Self:
        """Create a Point from a tuple.

        Args:
            t: Tuple (x, y).

        Returns:
            A new Point.
        """
        return cls(t[0], t[1])


@dataclasses.dataclass(frozen=True)
class Line(GeometryObject):
    """Represents an infinite line defined by two points.

    Attributes:
        p1: First point on the line.
        p2: Second point on the line.

    Examples:
        >>> line = Line(Point(0, 0), Point(10, 10))
        >>> line.slope()
        1.0
        >>> line.intercept()
        0.0
    """

    p1: Point
    p2: Point

    def slope(self) -> float:
        """Calculate the slope of the line.

        Returns:
            The slope, or NaN if vertical.
        """
        if self.p1.x != self.p2.x:
            return round((self.p2.y - self.p1.y) / (self.p2.x - self.p1.x), ROUNDING)
        return float("NAN")

    def intercept(self) -> float:
        """Calculate the y-intercept of the line.

        Returns:
            The y-intercept, or NaN if vertical.
        """
        slope = self.slope()
        if not math.isnan(slope):
            return self.p1.y - slope * self.p1.x
        else:
            return float("NAN")

    def get_angle_to_horizontal(self) -> float:
        """Get the angle of the line relative to horizontal.

        Returns:
            Angle in radians.
        """
        return get_angle_to_horizontal_of_line(self)

    def is_parallel_to_line(self, line: "Line") -> bool:
        """Check if this line is parallel to another.

        Args:
            line: The other line.

        Returns:
            True if parallel.
        """
        return are_lines_parallel(self, line)

    def is_coincident_to_line(self, line: "Line") -> bool:
        """Check if this line is coincident with another.

        Args:
            line: The other line.

        Returns:
            True if coincident (same infinite line).
        """
        return are_lines_coincident(self, line)

    def get_intersection_with_line(self, line: "Line") -> list["Line"] | list["Point"]:
        """Get intersection with another line.

        Args:
            line: The other line.

        Returns:
            List containing intersection point(s) or the coincident line.
        """
        return get_intersection_of_lines(self, line)

    def get_distance_to_point(self, point: Point) -> float:
        """Get perpendicular distance from a point to this line.

        Args:
            point: The point to measure from.

        Returns:
            The perpendicular distance.
        """
        return get_distance_between_line_and_point(self, point)

    def has_point(self, point: Point, max_distance: float = 0.01) -> bool:
        """Check if a point lies on this line.

        Args:
            point: The point to check.
            max_distance: Maximum allowed distance from line.

        Returns:
            True if point is on the line within tolerance.
        """
        return line_has_point(self, point, max_distance)

    def transformed(self, transformation: "Transformation") -> "Line":
        """Apply a transformation to this line.

        Args:
            transformation: The transformation to apply.

        Returns:
            A new transformed Line.
        """
        return transform_line(self, transformation)

    def reversed(self) -> "Line":
        """Return a reversed copy of the line.

        Returns:
            A new Line with p1 and p2 swapped.
        """
        return reverse_line(self)

    def to_shapely(self) -> shapely.LineString:
        """Convert to a shapely LineString.

        Returns:
            A shapely LineString.
        """
        return shapely.LineString(
            [
                self.p1.to_tuple(),
                self.p2.to_tuple(),
            ]
        )


@dataclasses.dataclass(frozen=True)
class Segment(GeometryObject):
    """Represents a line segment between two points.

    Attributes:
        p1: Start point.
        p2: End point.

    Examples:
        >>> seg = Segment(Point(0, 0), Point(10, 10))
        >>> seg.length()
        14.14...
        >>> seg.get_position_at_fraction(0.5)
        Point(x=5.0, y=5.0)
    """

    p1: Point
    p2: Point

    def length(self) -> float:
        """Calculate the length of the segment.

        Returns:
            The Euclidean length.
        """
        return math.sqrt((self.p2.x - self.p1.x) ** 2 + (self.p2.y - self.p1.y) ** 2)

    def get_distance_to_point(self, point: Point) -> float:
        """Get shortest distance from a point to this segment.

        Args:
            point: The point to measure from.

        Returns:
            The shortest distance.
        """
        return get_distance_between_segment_and_point(self, point)

    def has_point(self, point: Point, max_distance: float = 0.01) -> bool:
        """Check if a point lies on this segment.

        Args:
            point: The point to check.
            max_distance: Maximum allowed distance.

        Returns:
            True if point is on the segment within tolerance.
        """
        return segment_has_point(self, point, max_distance)

    def get_angle_to_horizontal(self) -> float:
        """Get the angle of the segment relative to horizontal.

        Returns:
            Angle in radians.
        """
        return get_angle_to_horizontal_of_line(self)

    def get_intersection_with_line(self, line: Line) -> list[Point] | list["Segment"]:
        """Get intersection with a line.

        Args:
            line: The line to intersect with.

        Returns:
            List of intersection points or segment if coincident.
        """
        return get_intersection_of_line_and_segment(line, self)

    def get_position_at_fraction(self, fraction: float) -> Point:
        """Get point at a fraction along the segment.

        Args:
            fraction: Fraction from 0 to 1 (0 = start, 1 = end).

        Returns:
            The point at that fraction.
        """
        return get_position_at_fraction_of_segment(self, fraction)

    def get_angle_at_fraction(self, fraction: float) -> float:
        """Get angle at a fraction along the segment.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Angle in radians.
        """
        return get_angle_at_fraction_of_segment(self, fraction)

    def get_position_and_angle_at_fraction(
        self, fraction: float
    ) -> tuple[Point, float]:
        """Get both position and angle at a fraction.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Tuple of (point, angle in radians).
        """
        return get_position_and_angle_at_fraction_of_segment(self, fraction)

    def shortened(
        self,
        length: float,
        start_or_end: typing.Literal["start", "end"] = "end",
    ) -> "Segment":
        """Return a shortened copy of the segment.

        Args:
            length: Amount to shorten by.
            start_or_end: Which end to shorten from.

        Returns:
            A new shortened Segment.
        """
        return shorten_segment(self, length, start_or_end)

    def transformed(self, transformation: "Transformation") -> "Segment":
        """Apply a transformation to this segment.

        Args:
            transformation: The transformation to apply.

        Returns:
            A new transformed Segment.
        """
        return transform_segment(self, transformation)

    def reversed(self) -> "Segment":
        """Return a reversed copy of the segment.

        Returns:
            A new Segment with p1 and p2 swapped.
        """
        return reverse_segment(self)

    def to_shapely(self) -> shapely.LineString:
        """Convert to a shapely LineString.

        Returns:
            A shapely LineString.
        """
        return shapely.LineString(
            [
                self.p1.to_tuple(),
                self.p2.to_tuple(),
            ]
        )

    def bbox(self) -> "Bbox":
        """Get the bounding box of the segment.

        Returns:
            A Bbox enclosing the segment.
        """
        return Bbox.from_bounds(self.to_shapely().bounds)

    @classmethod
    def from_shapely(cls, line_string: shapely.LineString) -> typing_extensions.Self:
        """Create a Segment from a shapely LineString.

        Args:
            line_string: A 2-point LineString.

        Returns:
            A new Segment.
        """
        shapely_points = line_string.boundary.geoms
        return cls(
            Point.from_shapely(shapely_points[0]),
            Point.from_shapely(shapely_points[1]),
        )


@dataclasses.dataclass(frozen=True)
class BezierCurve(GeometryObject):
    """Represents a cubic Bezier curve.

    Attributes:
        p1: Start point.
        p2: End point.
        control_points: Tuple of control points (1 for quadratic, 2 for cubic).

    Examples:
        >>> curve = BezierCurve(
        ...     Point(0, 0),
        ...     Point(10, 0),
        ...     (Point(3, 5), Point(7, 5))
        ... )
        >>> curve.length()
        11.77...
    """

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
        """Calculate the length of the curve.

        Returns:
            The arc length.
        """
        return self._to_bezier().length

    def evaluate(self, s: float) -> Point:
        """Evaluate the curve at parameter s.

        Args:
            s: Parameter value from 0 to 1.

        Returns:
            The point at parameter s.
        """
        evaluation = self._to_bezier().evaluate(s)
        return Point.from_fortranarray(evaluation)

    def evaluate_multi(self, s: numpy.ndarray) -> list[Point]:
        """Evaluate the curve at multiple parameters.

        Args:
            s: Array of parameter values.

        Returns:
            List of points.
        """
        evaluation = self._to_bezier().evaluate_multi(s)
        return [Point(e[0], e[1]) for e in evaluation.T]

    def get_intersection_with_line(self, line: Line) -> list[Point] | list[Segment]:
        """Get intersection with a line.

        Args:
            line: The line to intersect with.

        Returns:
            List of intersection points or segments.
        """
        return get_intersection_of_line_and_bezier_curve(line, self)

    def get_position_at_fraction(self, fraction: float):
        """Get point at a fraction along the curve.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            The point at that fraction.
        """
        return get_position_at_fraction_of_bezier_curve(self, fraction)

    def get_angle_at_fraction(self, fraction: float):
        """Get angle at a fraction along the curve.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Angle in radians.
        """
        return get_angle_at_fraction_of_bezier_curve(self, fraction)

    def get_position_and_angle_at_fraction(self, fraction: float):
        """Get both position and angle at a fraction.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Tuple of (point, angle).
        """
        return get_position_and_angle_at_fraction_of_bezier_curve(self, fraction)

    def shortened(
        self, length: float, start_or_end: typing.Literal["start", "end"] = "end"
    ) -> "BezierCurve":
        """Return a shortened copy of the curve.

        Args:
            length: Amount to shorten by.
            start_or_end: Which end to shorten from.

        Returns:
            A new shortened BezierCurve.
        """
        return shorten_bezier_curve(self, length, start_or_end)

    def transformed(self, transformation):
        """Apply a transformation to this curve.

        Args:
            transformation: The transformation to apply.

        Returns:
            A new transformed BezierCurve.
        """
        return transform_bezier_curve(self, transformation)

    def reversed(self):
        """Return a reversed copy of the curve.

        Returns:
            A new BezierCurve going in reverse direction.
        """
        return reverse_bezier_curve(self)

    def to_shapely(self, n_segs=50):
        """Convert to a shapely LineString.

        Args:
            n_segs: Number of segments to approximate with.

        Returns:
            A shapely LineString.
        """
        points = self.evaluate_multi(
            numpy.arange(0, 1 + 1 / n_segs, 1 / n_segs, dtype="double")
        )
        return shapely.LineString([point.to_tuple() for point in points])

    def bbox(self):
        """Get the bounding box of the curve.

        Returns:
            A Bbox enclosing the curve.
        """
        return Bbox.from_bounds(self.to_shapely().bounds)


@dataclasses.dataclass(frozen=True)
class EllipticalArc(GeometryObject):
    """Represents an elliptical arc.

    Attributes:
        p1: Start point.
        p2: End point.
        rx: X-radius of the ellipse.
        ry: Y-radius of the ellipse.
        x_axis_rotation: Rotation of the x-axis in radians.
        arc_flag: Large arc flag (0 or 1).
        sweep_flag: Sweep flag (0 or 1).

    Examples:
        >>> arc = EllipticalArc(
        ...     Point(0, 0), Point(10, 0), 5, 5, 0, 0, 1
        ... )
    """

    p1: Point
    p2: Point
    rx: float
    ry: float
    x_axis_rotation: float
    arc_flag: int
    sweep_flag: int

    def get_intersection_with_line(self, line: Line) -> list[Point]:
        """Get intersection with a line.

        Args:
            line: The line to intersect with.

        Returns:
            List of intersection points.
        """
        return get_intersection_of_line_and_elliptical_arc(line, self)

    def get_center_parameterization(
        self,
    ) -> tuple[float, float, float, float, float, float, float, float]:
        """Get the center parameterization of the arc.

        Returns:
            Tuple of (cx, cy, rx, ry, sigma, theta1, theta2, delta_theta).
        """
        return get_center_parameterization_of_elliptical_arc(self)

    def get_center(self) -> Point:
        """Get the center point of the ellipse.

        Returns:
            The center point.
        """
        return get_center_of_elliptical_arc(self)

    def get_position_at_fraction(self, fraction: float) -> Point:
        """Get point at a fraction along the arc.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            The point at that fraction.
        """
        return get_position_at_fraction_of_elliptical_arc(self, fraction)

    def get_angle_at_fraction(self, fraction: float) -> float:
        """Get angle at a fraction along the arc.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Angle in radians.
        """
        return get_angle_at_fraction_of_elliptical_arc(self, fraction)

    def get_position_and_angle_at_fraction(
        self, fraction: float
    ) -> tuple[Point, float]:
        """Get both position and angle at a fraction.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Tuple of (point, angle).
        """
        return get_position_and_angle_at_fraction_of_elliptical_arc(self, fraction)

    def to_shapely(self):
        """Convert to a shapely LineString.

        Returns:
            A shapely LineString approximating the arc.
        """

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
        """Get the bounding box of the arc.

        Returns:
            A Bbox enclosing the arc.
        """
        return Bbox.from_bounds(self.to_shapely().bounds)

    def shortened(
        self,
        length: float,
        start_or_end: typing.Literal["start", "end"] = "end",
    ) -> "EllipticalArc":
        """Return a shortened copy of the arc.

        Args:
            length: Amount to shorten by.
            start_or_end: Which end to shorten from.

        Returns:
            A new shortened EllipticalArc.
        """
        return shorten_elliptical_arc(self, length, start_or_end)

    def transformed(self, transformation: "Transformation") -> "EllipticalArc":
        """Apply a transformation to this arc.

        Args:
            transformation: The transformation to apply.

        Returns:
            A new transformed EllipticalArc.
        """
        return transform_elliptical_arc(self, transformation)

    def reversed(self) -> "EllipticalArc":
        """Return a reversed copy of the arc.

        Returns:
            A new EllipticalArc going in reverse direction.
        """
        return reverse_elliptical_arc(self)

    def to_bezier_curves(self) -> BezierCurve:
        """Convert to Bezier curves.

        Returns:
            BezierCurve(s) approximating the arc.
        """
        return transform_elliptical_arc_to_bezier_curves(self)

    def length(self) -> float:
        """Calculate the length of the arc.

        Returns:
            The arc length.
        """
        return self.to_shapely().length


@dataclasses.dataclass(frozen=True)
class Bbox(object):
    """Represents a bounding box.

    Attributes:
        position: Center point.
        width: Width of the box.
        height: Height of the box.

    Examples:
        >>> bbox = Bbox(Point(5, 5), 10, 10)
        >>> bbox.north_west()
        Point(x=0.0, y=0.0)
        >>> bbox.south_east()
        Point(x=10.0, y=10.0)
    """

    position: Point
    width: float
    height: float

    @property
    def x(self) -> float:
        """The x coordinate of the center."""
        return self.position.x

    @property
    def y(self) -> float:
        """The y coordinate of the center."""
        return self.position.y

    def size(self) -> tuple[float, float]:
        """Get the size as (width, height).

        Returns:
            Tuple of (width, height).
        """
        return (self.width, self.height)

    def anchor_point(self, anchor_point: str) -> Point:
        """Get a named anchor point.

        Args:
            anchor_point: Name like 'north', 'south_east', 'center', etc.

        Returns:
            The anchor point.
        """
        return getattr(self, anchor_point)()

    def north_west(self) -> Point:
        """Get the north-west corner."""
        return Point(self.x - self.width / 2, self.y - self.height / 2)

    def north_north_west(self) -> Point:
        """Get the north-north-west point."""
        return Point(self.x - self.width / 4, self.y - self.height / 2)

    def north(self) -> Point:
        """Get the north (top center) point."""
        return Point(self.x, self.y - self.height / 2)

    def north_north_east(self) -> Point:
        """Get the north-north-east point."""
        return Point(self.x + self.width / 4, self.y - self.height / 2)

    def north_east(self) -> Point:
        """Get the north-east corner."""
        return Point(self.x + self.width / 2, self.y - self.height / 2)

    def east_north_east(self) -> Point:
        """Get the east-north-east point."""
        return Point(self.x + self.width / 2, self.y - self.height / 4)

    def east(self) -> Point:
        """Get the east (right center) point."""
        return Point(self.x + self.width / 2, self.y)

    def east_south_east(self) -> Point:
        """Get the east-south-east point."""
        return Point(self.x + self.width / 2, self.y + self.width / 4)

    def south_east(self) -> Point:
        """Get the south-east corner."""
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    def south_south_east(self) -> Point:
        """Get the south-south-east point."""
        return Point(self.x + self.width / 4, self.y + self.height / 2)

    def south(self) -> Point:
        """Get the south (bottom center) point."""
        return Point(self.x, self.y + self.height / 2)

    def south_south_west(self) -> Point:
        """Get the south-south-west point."""
        return Point(self.x - self.width / 4, self.y + self.height / 2)

    def south_west(self) -> Point:
        """Get the south-west corner."""
        return Point(self.x - self.width / 2, self.y + self.height / 2)

    def west_south_west(self) -> Point:
        """Get the west-south-west point."""
        return Point(self.x - self.width / 2, self.y + self.height / 4)

    def west(self) -> Point:
        """Get the west (left center) point."""
        return Point(self.x - self.width / 2, self.y)

    def west_north_west(self) -> Point:
        """Get the west-north-west point."""
        return Point(self.x - self.width / 2, self.y - self.height / 4)

    def center(self) -> Point:
        """Get the center point."""
        return Point(self.x, self.y)

    def isnan(self) -> bool:
        """Check if the position has NaN coordinates.

        Returns:
            True if position has NaN.
        """
        return self.position.isnan()

    @classmethod
    def from_bounds(cls, bounds: tuple[float, float, float, float]):
        """Create a Bbox from shapely bounds.

        Args:
            bounds: Tuple of (min_x, min_y, max_x, max_y).

        Returns:
            A new Bbox.
        """
        return cls(
            Point((bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2),
            bounds[2] - bounds[0],
            bounds[3] - bounds[1],
        )


@dataclasses.dataclass(frozen=True)
class Transformation(abc.ABC):
    """Abstract base class for geometric transformations."""

    @abc.abstractmethod
    def to_matrix(self) -> numpy.typing.NDArray:
        """Convert to a 3x3 transformation matrix.

        Returns:
            A 3x3 numpy array.
        """
        pass

    @abc.abstractmethod
    def inverted(self) -> "Transformation":
        """Get the inverse transformation.

        Returns:
            The inverse transformation.
        """
        pass

    def __mul__(self, other):
        return MatrixTransformation(numpy.matmul(self.to_matrix(), other.to_matrix()))


@dataclasses.dataclass(frozen=True)
class MatrixTransformation(Transformation):
    """Represents a transformation as a 3x3 matrix.

    Attributes:
        m: The 3x3 transformation matrix.
    """

    m: numpy.typing.NDArray

    def to_matrix(self) -> numpy.typing.NDArray:
        """Get the matrix representation.

        Returns:
            The 3x3 matrix.
        """
        return self.m

    def inverted(self) -> Transformation:
        """Get the inverse transformation.

        Returns:
            The inverse matrix transformation.
        """
        return invert_matrix_transformation(self)


@dataclasses.dataclass(frozen=True)
class Rotation(Transformation):
    """Represents a rotation transformation.

    Attributes:
        angle: Rotation angle in radians.
        point: Optional center of rotation (defaults to origin).

    Examples:
        >>> rot = Rotation(math.pi / 2, Point(5, 5))
    """

    angle: float
    point: Point | None = None

    def to_matrix(self) -> numpy.typing.NDArray:
        """Convert to a rotation matrix.

        Returns:
            A 3x3 rotation matrix.
        """
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
        """Get the inverse rotation.

        Returns:
            A rotation by the negative angle.
        """
        return invert_rotation(self)


@dataclasses.dataclass(frozen=True)
class Translation(Transformation):
    """Represents a translation transformation.

    Attributes:
        tx: Translation in x direction.
        ty: Translation in y direction.

    Examples:
        >>> trans = Translation(10, 20)
    """

    tx: float
    ty: float

    def to_matrix(self) -> numpy.typing.NDArray:
        """Convert to a translation matrix.

        Returns:
            A 3x3 translation matrix.
        """
        m = numpy.array([[1, 0, self.tx], [0, 1, self.ty], [0, 0, 1]], dtype=float)
        return m

    def inverted(self) -> Transformation:
        """Get the inverse translation.

        Returns:
            A translation by (-tx, -ty).
        """
        return invert_translation(self)


@dataclasses.dataclass(frozen=True)
class Scaling(Transformation):
    """Represents a scaling transformation.

    Attributes:
        sx: Scale factor in x direction.
        sy: Scale factor in y direction.

    Examples:
        >>> scale = Scaling(2, 2)  # Double size
    """

    sx: float
    sy: float

    def to_matrix(self) -> numpy.typing.NDArray:
        """Convert to a scaling matrix.

        Returns:
            A 3x3 scaling matrix.
        """
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
        """Get the inverse scaling.

        Returns:
            Scaling by (1/sx, 1/sy).
        """
        return invert_scaling(self)


def transform_point(point: Point, transformation: Transformation) -> Point:
    """Transform a point.

    Args:
        point: The point to transform.
        transformation: The transformation to apply.

    Returns:
        The transformed point.
    """
    m = numpy.matmul(transformation.to_matrix(), point.to_matrix())
    return Point(m[0][0], m[1][0])


def transform_line(line: Line, transformation: Transformation) -> Line:
    """Transform a line.

    Args:
        line: The line to transform.
        transformation: The transformation to apply.

    Returns:
        The transformed line.
    """
    return Line(
        transform_point(line.p1, transformation),
        transform_point(line.p2, transformation),
    )


def transform_segment(segment: Segment, transformation: Transformation) -> Segment:
    """Transform a segment.

    Args:
        segment: The segment to transform.
        transformation: The transformation to apply.

    Returns:
        The transformed segment.
    """
    return Segment(
        transform_point(segment.p1, transformation),
        transform_point(segment.p2, transformation),
    )


def transform_bezier_curve(
    bezier_curve: BezierCurve, transformation: Transformation
) -> BezierCurve:
    """Transform a Bezier curve.

    Args:
        bezier_curve: The curve to transform.
        transformation: The transformation to apply.

    Returns:
        The transformed BezierCurve.
    """
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
    """Transform an elliptical arc.

    Args:
        elliptical_arc: The arc to transform.
        transformation: The transformation to apply.

    Returns:
        The transformed EllipticalArc.
    """
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
    """Return a copy of the point (points are directionless).

    Args:
        point: The point.

    Returns:
        A copy of the point.
    """
    return Point(point.x, point.y)


def reverse_line(line: Line) -> Line:
    """Reverse a line (swap endpoints).

    Args:
        line: The line to reverse.

    Returns:
        A new Line with p1 and p2 swapped.
    """
    return Line(line.p2, line.p1)


def reverse_segment(segment):
    """Reverse a segment (swap endpoints).

    Args:
        segment: The segment to reverse.

    Returns:
        A new Segment with p1 and p2 swapped.
    """
    return Segment(segment.p2, segment.p1)


def reverse_bezier_curve(bezier_curve: BezierCurve) -> BezierCurve:
    """Reverse a Bezier curve.

    Args:
        bezier_curve: The curve to reverse.

    Returns:
        A new BezierCurve going in reverse direction.
    """
    return BezierCurve(
        bezier_curve.p2, bezier_curve.p1, bezier_curve.control_points[::-1]
    )


def reverse_elliptical_arc(elliptical_arc: EllipticalArc) -> EllipticalArc:
    """Reverse an elliptical arc.

    Args:
        elliptical_arc: The arc to reverse.

    Returns:
        A new EllipticalArc going in reverse direction.
    """
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
    """Shorten a segment by a given length.

    Args:
        segment: The segment to shorten.
        length: Amount to shorten by.
        start_or_end: Which end to shorten from.

    Returns:
        A new shortened Segment.
    """
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
    """Shorten a Bezier curve by a given length.

    Args:
        bezier_curve: The curve to shorten.
        length: Amount to shorten by.
        start_or_end: Which end to shorten from.

    Returns:
        A new shortened BezierCurve.
    """
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
    """Shorten an elliptical arc by a given length.

    Args:
        elliptical_arc: The arc to shorten.
        length: Amount to shorten by.
        start_or_end: Which end to shorten from.

    Returns:
        A new shortened EllipticalArc.
    """
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
    """Invert a matrix transformation.

    Args:
        matrix_transformation: The transformation to invert.

    Returns:
        The inverse transformation.
    """
    return MatrixTransformation(numpy.linalg.inv(matrix_transformation.m))


def invert_rotation(rotation: Rotation) -> Rotation:
    """Invert a rotation.

    Args:
        rotation: The rotation to invert.

    Returns:
        A rotation by the negative angle.
    """
    return Rotation(-rotation.angle, rotation.point)


def invert_translation(translation: Translation) -> Translation:
    """Invert a translation.

    Args:
        translation: The translation to invert.

    Returns:
        A translation by (-tx, -ty).
    """
    return Translation(-translation.tx, -translation.ty)


def invert_scaling(scaling: Scaling) -> Scaling:
    """Invert a scaling.

    Args:
        scaling: The scaling to invert.

    Returns:
        Scaling by the reciprocal factors.
    """
    return Scaling(1 / scaling.sx, 1 / scaling.sy)


def get_intersection_of_line_and_point(line: Line, point: Point) -> list[Point]:
    """Get intersection of a line and a point.

    Args:
        line: The line.
        point: The point.

    Returns:
        List containing the point if it lies on the line, empty otherwise.
    """
    if line.has_point(point):
        return [point]
    return []


def get_intersection_of_lines(line1: Line, line2: Line) -> list[Line] | list[Point]:
    """Get intersection of two lines.

    Args:
        line1: First line.
        line2: Second line.

    Returns:
        List containing intersection point(s) or coincident line.
    """
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
    """Get intersection of a line and a segment.

    Args:
        line: The line.
        segment: The segment.

    Returns:
        List of intersection points, segment if coincident, or empty.
    """
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
    """Get intersection of a line and a Bezier curve.

    Args:
        line: The line.
        bezier_curve: The Bezier curve.

    Returns:
        List of intersection points or segments.
    """
    shapely_object = bezier_curve.to_shapely()
    return get_intersection_of_line_and_shapely_object(line, shapely_object)


def get_intersection_of_line_and_elliptical_arc(
    line: Line, elliptical_arc: EllipticalArc
) -> list[Point] | list[Segment]:
    """Get intersection of a line and an elliptical arc.

    Args:
        line: The line.
        elliptical_arc: The elliptical arc.

    Returns:
        List of intersection points or segments.
    """
    shapely_object = elliptical_arc.to_shapely()
    return get_intersection_of_line_and_shapely_object(line, shapely_object)


def get_intersection_of_line_and_shapely_object(
    line: Line, shapely_object: shapely.Geometry
) -> list[Point] | list[Segment]:
    """Get intersection of a line with a shapely object.

    Args:
        line: The line.
        shapely_object: A shapely geometry.

    Returns:
        List of intersection points or segments.
    """
    intersection = []
    # Handle both single geometries and collections
    if hasattr(shapely_object, "geoms"):
        geoms = shapely_object.geoms
    else:
        geoms = [shapely_object]
    for shapely_geom in geoms:
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
    """Get the bounding box of a shapely object.

    Args:
        shapely_object: A shapely geometry.

    Returns:
        The bounding box.
    """
    return Bbox.from_bounds(shapely_object.bounds)


def get_shapely_object_border(
    shapely_object: shapely.Geometry, point: Point, center: Point | None = None
) -> Point | None:
    """Get the border point in a given direction.

    Args:
        shapely_object: A shapely geometry.
        point: Direction point.
        center: Optional center point.

    Returns:
        The border point or None.
    """
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
    """Get the border point at a given angle.

    Args:
        shapely_object: A shapely geometry.
        angle: The angle.
        unit: Unit of angle ('degrees' or 'radians').
        center: Optional center point.

    Returns:
        The border point or None.
    """
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
    """Get an anchor point of a shapely object.

    Args:
        shapely_object: A shapely geometry.
        anchor_point: Name of anchor point.
        center: Optional center point.

    Returns:
        The anchor point.
    """
    bbox = get_shapely_object_bbox(shapely_object)
    if center is None:
        center = bbox.center()
    if center.isnan():
        return Point(float("nan"), float("nan"))
    point = bbox.anchor_point(anchor_point)
    return get_shapely_object_border(shapely_object, point, center)


def get_angle_to_horizontal_of_point(point: Point) -> float:
    """Get angle from origin to point relative to horizontal.

    Args:
        point: The point.

    Returns:
        Angle in radians.
    """
    line = Line(Point(0, 0), point)
    return line.get_angle_to_horizontal()


def get_angle_to_horizontal_of_line(line: Line | Segment) -> float:
    """Get angle of a line relative to horizontal.

    Args:
        line: A Line or Segment.

    Returns:
        Angle in radians.
    """
    x1 = line.p1.x
    y1 = line.p1.y
    x2 = line.p2.x
    y2 = line.p2.y
    angle = math.atan2(y2 - y1, x2 - x1)
    return get_normalized_angle(angle)


def are_lines_parallel(line1: Line, line2: Line) -> bool:
    """Check if two lines are parallel.

    Args:
        line1: First line.
        line2: Second line.

    Returns:
        True if parallel.
    """
    slope1 = line1.slope()
    slope2 = line2.slope()
    if math.isnan(slope1) and math.isnan(slope2):
        return True
    return slope1 == slope2


def are_lines_coincident(line1: Line, line2: Line) -> bool:
    """Check if two lines are coincident.

    Args:
        line1: First line.
        line2: Second line.

    Returns:
        True if coincident.
    """
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


def is_angle_in_sector(
    angle: float, center: Point, point1: Point, point2: Point
) -> bool:
    """Check if an angle is within a sector.

    Args:
        angle: The angle to check (radians).
        center: Center of sector.
        point1: First sector boundary.
        point2: Second sector boundary.

    Returns:
        True if angle is in sector.
    """
    angle1 = get_angle_to_horizontal_of_line(Line(center, point1))
    angle2 = get_angle_to_horizontal_of_line(Line(center, point2))
    return is_angle_between(angle, angle1, angle2)


def is_angle_between(angle: float, start_angle: float, end_angle: float) -> bool:
    """Check if an angle is between two angles.

    Args:
        angle: The angle to check (radians).
        start_angle: Start angle (radians).
        end_angle: End angle (radians).

    Returns:
        True if angle is between start and end.
    """
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


def get_normalized_angle(angle: float) -> float:
    """Normalize an angle to [0, 2*pi).

    Args:
        angle: Angle in radians.

    Returns:
        Normalized angle.
    """
    return angle - (angle // (2 * math.pi) * (2 * math.pi))


def _get_position_at_fraction(segment_or_curve, fraction):
    line_string = segment_or_curve.to_shapely()
    shapely_point = line_string.interpolate(fraction, normalized=True)
    return Point.from_shapely(shapely_point)


def get_position_at_fraction_of_segment(
    segment: Segment,
    fraction: float,
) -> Point:
    """Get point at a fraction along a segment.

    Args:
        segment: The segment.
        fraction: Fraction from 0 to 1.

    Returns:
        The point at that fraction.
    """
    return _get_position_at_fraction(segment, fraction)


def get_position_at_fraction_of_bezier_curve(
    bezier_curve: BezierCurve,
    fraction: float,
) -> Point:
    """Get point at a fraction along a Bezier curve.

    Args:
        bezier_curve: The curve.
        fraction: Fraction from 0 to 1.

    Returns:
        The point at that fraction.
    """
    return _get_position_at_fraction(bezier_curve, fraction)


def get_position_at_fraction_of_elliptical_arc(
    elliptical_arc: EllipticalArc,
    fraction: float,
) -> Point:
    """Get point at a fraction along an elliptical arc.

    Args:
        elliptical_arc: The arc.
        fraction: Fraction from 0 to 1.

    Returns:
        The point at that fraction.
    """
    return _get_position_at_fraction(elliptical_arc, fraction)


def get_center_parameterization_of_elliptical_arc(
    elliptical_arc: EllipticalArc,
) -> tuple[float, float, float, float, float, float, float, float]:
    """Get center parameterization of an elliptical arc.

    Args:
        elliptical_arc: The arc.

    Returns:
        Tuple of (cx, cy, rx, ry, sigma, theta1, theta2, delta_theta).
    """
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
    if r < 0:
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
    """Get center of an elliptical arc.

    Args:
        elliptical_arc: The arc.

    Returns:
        The center point.
    """
    cx, cy, *_ = get_center_parameterization_of_elliptical_arc(elliptical_arc)
    return Point(cx, cy)


def transform_elliptical_arc_to_bezier_curves(
    elliptical_arc: EllipticalArc,
) -> list[BezierCurve]:
    """Convert an elliptical arc to Bezier curves.

    Args:
        elliptical_arc: The arc to convert.

    Returns:
        List of BezierCurve approximating the arc.
    """

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
) -> float:
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
        previous_coord = current_coord
    return segment.get_angle_to_horizontal()


def get_angle_at_fraction_of_segment(
    segment: Segment,
    fraction: float,
) -> float:
    """Get angle at a fraction along a segment.

    Args:
        segment: The segment.
        fraction: Fraction from 0 to 1.

    Returns:
        Angle in radians.
    """
    return _get_angle_at_fraction(segment, fraction)


def get_angle_at_fraction_of_bezier_curve(
    bezier_curve: BezierCurve,
    fraction: float,
) -> float:
    """Get angle at a fraction along a Bezier curve.

    Args:
        bezier_curve: The curve.
        fraction: Fraction from 0 to 1.

    Returns:
        Angle in radians.
    """
    return _get_angle_at_fraction(bezier_curve, fraction)


def get_angle_at_fraction_of_elliptical_arc(
    elliptical_arc: EllipticalArc,
    fraction: float,
) -> float:
    """Get angle at a fraction along an elliptical arc.

    Args:
        elliptical_arc: The arc.
        fraction: Fraction from 0 to 1.

    Returns:
        Angle in radians.
    """
    return _get_angle_at_fraction(elliptical_arc, fraction)


def _get_position_and_angle_at_fraction(
    segment_or_curve: Segment | BezierCurve | EllipticalArc,
    fraction: float,
) -> tuple[Point, float]:
    position = _get_position_at_fraction(segment_or_curve, fraction)
    angle = _get_angle_at_fraction(segment_or_curve, fraction)
    return position, angle


def get_position_and_angle_at_fraction_of_segment(
    segment: Segment,
    fraction: float,
) -> tuple[Point, float]:
    """Get position and angle at a fraction along a segment.

    Args:
        segment: The segment.
        fraction: Fraction from 0 to 1.

    Returns:
        Tuple of (point, angle).
    """
    return _get_position_and_angle_at_fraction(segment, fraction)


def get_position_and_angle_at_fraction_of_bezier_curve(
    bezier_curve: BezierCurve,
    fraction: float,
) -> tuple[Point, float]:
    """Get position and angle at a fraction along a Bezier curve.

    Args:
        bezier_curve: The curve.
        fraction: Fraction from 0 to 1.

    Returns:
        Tuple of (point, angle).
    """
    return _get_position_and_angle_at_fraction(bezier_curve, fraction)


def get_position_and_angle_at_fraction_of_elliptical_arc(
    elliptical_arc: EllipticalArc,
    fraction: float,
) -> tuple[Point, float]:
    """Get position and angle at a fraction along an elliptical arc.

    Args:
        elliptical_arc: The arc.
        fraction: Fraction from 0 to 1.

    Returns:
        Tuple of (point, angle).
    """
    return _get_position_and_angle_at_fraction(elliptical_arc, fraction)


def get_angle_between_segments(segment1: Segment, segment2: Segment) -> float:
    """Get angle between two segments.

    Args:
        segment1: First segment.
        segment2: Second segment.

    Returns:
        Angle in radians (range -pi to pi).
    """
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
    """Get distance between two points.

    Args:
        p1: First point.
        p2: Second point.

    Returns:
        The Euclidean distance.
    """
    return Segment(p1, p2).length()


def get_distance_between_line_and_point(line: Line, point: Point) -> float:
    """Get perpendicular distance from a point to a line.

    Args:
        line: The line.
        point: The point.

    Returns:
        The perpendicular distance.
    """
    distance = abs(
        (line.p2.x - line.p1.x) * (line.p1.y - point.y)
        - (line.p1.x - point.x) * (line.p2.y - line.p1.y)
    ) / math.sqrt((line.p2.x - line.p1.x) ** 2 + (line.p2.y - line.p1.y) ** 2)
    return distance


def get_distance_between_segment_and_point(segment: Segment, point: Point) -> float:
    """Get shortest distance from a point to a segment.

    Args:
        segment: The segment.
        point: The point.

    Returns:
        The shortest distance.
    """
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
    """Check if a point lies on a line.

    Args:
        line: The line.
        point: The point.
        max_distance: Maximum allowed distance.

    Returns:
        True if point is on the line within tolerance.
    """
    d = line.get_distance_to_point(point)
    if d <= max_distance:
        return True
    return False


def segment_has_point(
    segment: Segment, point: Point, max_distance: float = 0.01
) -> bool:
    """Check if a point lies on a segment.

    Args:
        segment: The segment.
        point: The point.
        max_distance: Maximum allowed distance.

    Returns:
        True if point is on the segment within tolerance.
    """
    d = segment.get_distance_to_point(point)
    if d <= max_distance:
        return True
    return False


def get_transformation_for_frame(
    origin: Point, unit_x: Point, unit_y: Point
) -> MatrixTransformation:
    """Get transformation for a frame defined by origin and axes.

    Given a frame F defined by its origin, unit x axis vector, and unit y axis
    vector, returns the transformation that converts points from F coordinates
    to reference frame coordinates.

    Args:
        origin: Origin of the frame.
        unit_x: Unit x-axis vector.
        unit_y: Unit y-axis vector.

    Returns:
        The transformation matrix.
    """
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
