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

import collections.abc
import dataclasses
import typing
import typing_extensions
import abc
import math
import copy

import numpy

import momapy.builder


ROUNDING = 4
ROUNDING_TOLERANCE = 10**-ROUNDING
ZERO_TOLERANCE = 1e-12
PARAMETER_TOLERANCE = 1e-10
CONVERGENCE_TOLERANCE = 1e-8


@dataclasses.dataclass(frozen=True)
class GeometryObject(abc.ABC):
    """Abstract base class for all geometry objects."""

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
        if line.has_point(self):
            return [self]
        return []

    def get_angle_to_horizontal(self) -> float:
        """Get the angle from origin to this point relative to horizontal.

        Returns:
            Angle in radians.
        """
        angle = math.atan2(self.y, self.x)
        return get_normalized_angle(angle)

    def transformed(self, transformation: "Transformation") -> "Point":
        """Apply a transformation to this point.

        Args:
            transformation: The transformation to apply.

        Returns:
            A new transformed Point.
        """
        m = numpy.matmul(transformation.to_matrix(), self.to_matrix())
        return Point(m[0][0], m[1][0])

    def reversed(self) -> "Point":
        """Return a reversed copy (identity for points).

        Returns:
            A copy of the point.
        """
        return Point(self.x, self.y)

    def round(self, ndigits=None):
        """Round coordinates to specified digits.

        Args:
            ndigits: Number of decimal places.

        Returns:
            A new Point with rounded coordinates.
        """
        return Point(round(self.x, ndigits), round(self.y, ndigits))

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
            return round(self.p1.y - slope * self.p1.x, ROUNDING)
        return float("NAN")

    def get_angle_to_horizontal(self) -> float:
        """Get the angle of the line relative to horizontal.

        Returns:
            Angle in radians.
        """
        angle = math.atan2(self.p2.y - self.p1.y, self.p2.x - self.p1.x)
        return get_normalized_angle(angle)

    def is_parallel_to_line(self, line: "Line") -> bool:
        """Check if this line is parallel to another.

        Args:
            line: The other line.

        Returns:
            True if parallel.
        """
        slope1 = self.slope()
        slope2 = line.slope()
        if math.isnan(slope1) and math.isnan(slope2):
            return True
        return slope1 == slope2

    def is_coincident_to_line(self, line: "Line") -> bool:
        """Check if this line is coincident with another.

        Args:
            line: The other line.

        Returns:
            True if coincident (same infinite line).
        """
        slope1 = self.slope()
        intercept1 = self.intercept()
        slope2 = line.slope()
        intercept2 = line.intercept()
        return (
            math.isnan(slope1)
            and math.isnan(slope2)
            and self.p1.x == line.p1.x
            or slope1 == slope2
            and intercept1 == intercept2
        )

    def get_intersection_with_line(self, line: "Line") -> list["Line"] | list[Point]:
        """Get intersection with another line.

        Args:
            line: The other line.

        Returns:
            List containing intersection point(s) or the coincident line.
        """
        slope1 = self.slope()
        intercept1 = self.intercept()
        slope2 = line.slope()
        intercept2 = line.intercept()
        if self.is_coincident_to_line(line):
            intersection = [copy.deepcopy(self)]
        elif self.is_parallel_to_line(line):
            intersection = []
        elif math.isnan(slope1):
            intersection = [Point(self.p1.x, slope2 * self.p1.x + intercept2)]
        elif math.isnan(slope2):
            intersection = [Point(line.p1.x, slope1 * line.p1.x + intercept1)]
        else:
            d = (self.p1.x - self.p2.x) * (line.p1.y - line.p2.y) - (
                self.p1.y - self.p2.y
            ) * (line.p1.x - line.p2.x)
            px = (
                (self.p1.x * self.p2.y - self.p1.y * self.p2.x)
                * (line.p1.x - line.p2.x)
                - (self.p1.x - self.p2.x)
                * (line.p1.x * line.p2.y - line.p1.y * line.p2.x)
            ) / d
            py = (
                (self.p1.x * self.p2.y - self.p1.y * self.p2.x)
                * (line.p1.y - line.p2.y)
                - (self.p1.y - self.p2.y)
                * (line.p1.x * line.p2.y - line.p1.y * line.p2.x)
            ) / d
            intersection = [Point(px, py)]
        return intersection

    def get_distance_to_point(self, point: Point) -> float:
        """Get perpendicular distance from a point to this line.

        Args:
            point: The point to measure from.

        Returns:
            The perpendicular distance.
        """
        return abs(
            (self.p2.x - self.p1.x) * (self.p1.y - point.y)
            - (self.p1.x - point.x) * (self.p2.y - self.p1.y)
        ) / math.sqrt((self.p2.x - self.p1.x) ** 2 + (self.p2.y - self.p1.y) ** 2)

    def has_point(self, point: Point, max_distance: float = ROUNDING_TOLERANCE) -> bool:
        """Check if a point lies on this line.

        Args:
            point: The point to check.
            max_distance: Maximum allowed distance from line.

        Returns:
            True if point is on the line within tolerance.
        """
        return self.get_distance_to_point(point) <= max_distance

    def transformed(self, transformation: "Transformation") -> "Line":
        """Apply a transformation to this line.

        Args:
            transformation: The transformation to apply.

        Returns:
            A new transformed Line.
        """
        return Line(
            self.p1.transformed(transformation),
            self.p2.transformed(transformation),
        )

    def reversed(self) -> "Line":
        """Return a reversed copy of the line.

        Returns:
            A new Line with p1 and p2 swapped.
        """
        return Line(self.p2, self.p1)


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
        a = point.x - self.p1.x
        b = point.y - self.p1.y
        c = self.p2.x - self.p1.x
        d = self.p2.y - self.p1.y
        dot = a * c + b * d
        len_sq = c**2 + d**2
        if len_sq != 0:
            param = dot / len_sq
        else:
            param = -1
        if param < 0:
            xx = self.p1.x
            yy = self.p1.y
        elif param > 1:
            xx = self.p2.x
            yy = self.p2.y
        else:
            xx = self.p1.x + param * c
            yy = self.p1.y + param * d
        dx = point.x - xx
        dy = point.y - yy
        return math.sqrt(dx**2 + dy**2)

    def has_point(self, point: Point, max_distance: float = ROUNDING_TOLERANCE) -> bool:
        """Check if a point lies on this segment.

        Args:
            point: The point to check.
            max_distance: Maximum allowed distance.

        Returns:
            True if point is on the segment within tolerance.
        """
        return self.get_distance_to_point(point) <= max_distance

    def get_angle_to_horizontal(self) -> float:
        """Get the angle of the segment relative to horizontal.

        Returns:
            Angle in radians.
        """
        angle = math.atan2(self.p2.y - self.p1.y, self.p2.x - self.p1.x)
        return get_normalized_angle(angle)

    def get_intersection_with_line(self, line: Line) -> list[Point] | list["Segment"]:
        """Get intersection with a line.

        Args:
            line: The line to intersect with.

        Returns:
            List of intersection points or segment if coincident.
        """
        line2 = Line(self.p1, self.p2)
        line_intersection = line.get_intersection_with_line(line2)
        result: list[Point] | list[Segment] = []
        if len(line_intersection) > 0 and isinstance(line_intersection[0], Point):
            sorted_xs = sorted([self.p1.x, self.p2.x])
            sorted_ys = sorted([self.p1.y, self.p2.y])
            if (
                line_intersection[0].x >= sorted_xs[0]
                and line_intersection[0].x <= sorted_xs[-1]
                and line_intersection[0].y >= sorted_ys[0]
                and line_intersection[0].y <= sorted_ys[-1]
            ):
                result = [line_intersection[0]]
        elif len(line_intersection) > 0:
            result = [self]
        return result

    def get_position_at_fraction(self, fraction: float) -> Point:
        """Get point at a fraction along the segment.

        Args:
            fraction: Fraction from 0 to 1 (0 = start, 1 = end).

        Returns:
            The point at that fraction.
        """
        x = self.p1.x + fraction * (self.p2.x - self.p1.x)
        y = self.p1.y + fraction * (self.p2.y - self.p1.y)
        return Point(x, y)

    def get_angle_at_fraction(self, fraction: float) -> float:
        """Get angle at a fraction along the segment.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Angle in radians.
        """
        return self.get_angle_to_horizontal()

    def get_position_and_angle_at_fraction(
        self, fraction: float
    ) -> tuple[Point, float]:
        """Get both position and angle at a fraction.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Tuple of (point, angle in radians).
        """
        return (
            self.get_position_at_fraction(fraction),
            self.get_angle_at_fraction(fraction),
        )

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
        if length == 0 or self.length() == 0:
            return copy.deepcopy(self)
        if start_or_end == "start":
            return self.reversed().shortened(length).reversed()
        fraction = 1 - length / self.length()
        point = self.get_position_at_fraction(fraction)
        return Segment(self.p1, point)

    def transformed(self, transformation: "Transformation") -> "Segment":
        """Apply a transformation to this segment.

        Args:
            transformation: The transformation to apply.

        Returns:
            A new transformed Segment.
        """
        return Segment(
            self.p1.transformed(transformation),
            self.p2.transformed(transformation),
        )

    def reversed(self) -> "Segment":
        """Return a reversed copy of the segment.

        Returns:
            A new Segment with p1 and p2 swapped.
        """
        return Segment(self.p2, self.p1)

    def bbox(self) -> "Bbox":
        """Get the bounding box of the segment.

        Returns:
            A Bbox enclosing the segment.
        """
        return Bbox.around_points([self.p1, self.p2])


# Precomputed 16-point Gauss-Legendre nodes and weights on [-1, 1]
_GL_NODES_16 = [
    -0.9894009349916499,
    -0.9445750230732326,
    -0.8656312023878318,
    -0.7554044083550030,
    -0.6178762444026438,
    -0.4580167776572274,
    -0.2816035507792589,
    -0.0950125098376374,
    0.0950125098376374,
    0.2816035507792589,
    0.4580167776572274,
    0.6178762444026438,
    0.7554044083550030,
    0.8656312023878318,
    0.9445750230732326,
    0.9894009349916499,
]
_GL_WEIGHTS_16 = [
    0.0271524594117541,
    0.0622535239386479,
    0.0951585116824928,
    0.1246289712555339,
    0.1495959888165767,
    0.1691565193950025,
    0.1826034150449236,
    0.1894506104550685,
    0.1894506104550685,
    0.1826034150449236,
    0.1691565193950025,
    0.1495959888165767,
    0.1246289712555339,
    0.0951585116824928,
    0.0622535239386479,
    0.0271524594117541,
]


def _arc_length(derivative_function, t0: float, t1: float) -> float:
    """Gauss-Legendre quadrature of |derivative(t)| from t0 to t1.

    Args:
        derivative_function: Function returning (dx, dy) at parameter t.
        t0: Start parameter.
        t1: End parameter.

    Returns:
        The arc length between t0 and t1.
    """
    mid = (t0 + t1) / 2
    half = (t1 - t0) / 2
    total = 0.0
    for node, weight in zip(_GL_NODES_16, _GL_WEIGHTS_16):
        t = mid + half * node
        dx, dy = derivative_function(t)
        total += weight * math.sqrt(dx * dx + dy * dy)
    return total * half


def _find_t_at_arc_length_fraction(
    derivative_function,
    total_length: float,
    fraction: float,
    tolerance: float = CONVERGENCE_TOLERANCE,
) -> float:
    """Binary search for t such that arc_length(0, t) / total_length ~ fraction.

    Args:
        derivative_function: Function returning (dx, dy) at parameter t.
        total_length: Total arc length of the curve.
        fraction: Target fraction of total length.
        tolerance: Tolerance (unused, kept for API).

    Returns:
        Parameter t corresponding to the fraction.
    """
    target = fraction * total_length
    low, high = 0.0, 1.0
    for _ in range(64):
        mid = (low + high) / 2
        if _arc_length(derivative_function, 0.0, mid) < target:
            low = mid
        else:
            high = mid
    return (low + high) / 2


@dataclasses.dataclass(frozen=True)
class QuadraticBezierCurve(GeometryObject):
    """Represents a quadratic Bezier curve.

    Attributes:
        p1: Start point.
        p2: End point.
        control_point: The single control point.

    Examples:
        >>> curve = QuadraticBezierCurve(
        ...     Point(0, 0),
        ...     Point(10, 0),
        ...     Point(5, 5)
        ... )
    """

    p1: Point
    p2: Point
    control_point: Point

    def evaluate(self, t: float) -> Point:
        """Evaluate the curve at parameter t.

        Args:
            t: Parameter value from 0 to 1.

        Returns:
            The point at parameter t.
        """
        return self.evaluate_multi([t])[0]

    def evaluate_multi(
        self, t_sequence: collections.abc.Sequence[float]
    ) -> list[Point]:
        """Evaluate the curve at multiple parameters.

        Args:
            t_sequence: Sequence of parameter values.

        Returns:
            List of points.
        """
        t = numpy.asarray(t_sequence, dtype="double")
        u = 1 - t
        x = u * u * self.p1.x + 2 * u * t * self.control_point.x + t * t * self.p2.x
        y = u * u * self.p1.y + 2 * u * t * self.control_point.y + t * t * self.p2.y
        return [Point(float(xi), float(yi)) for xi, yi in zip(x, y)]

    def derivative(self, t: float) -> tuple[float, float]:
        """Compute the derivative at parameter t.

        Args:
            t: Parameter value from 0 to 1.

        Returns:
            Tuple of (dx/dt, dy/dt).
        """
        u = 1 - t
        dx = 2 * u * (self.control_point.x - self.p1.x) + 2 * t * (
            self.p2.x - self.control_point.x
        )
        dy = 2 * u * (self.control_point.y - self.p1.y) + 2 * t * (
            self.p2.y - self.control_point.y
        )
        return (dx, dy)

    def split(self, t: float) -> tuple["QuadraticBezierCurve", "QuadraticBezierCurve"]:
        """Split the curve at parameter t using De Casteljau subdivision.

        Args:
            t: Parameter value from 0 to 1.

        Returns:
            Tuple of two QuadraticBezierCurves.
        """
        u = 1 - t
        m0x = u * self.p1.x + t * self.control_point.x
        m0y = u * self.p1.y + t * self.control_point.y
        m1x = u * self.control_point.x + t * self.p2.x
        m1y = u * self.control_point.y + t * self.p2.y
        mx = u * m0x + t * m1x
        my = u * m0y + t * m1y
        mid = Point(mx, my)
        left = QuadraticBezierCurve(self.p1, mid, Point(m0x, m0y))
        right = QuadraticBezierCurve(mid, self.p2, Point(m1x, m1y))
        return (left, right)

    def length(self) -> float:
        """Calculate the arc length of the curve.

        Returns:
            The arc length.
        """
        return _arc_length(self.derivative, 0.0, 1.0)

    def bbox(self) -> "Bbox":
        """Get the bounding box of the curve.

        Returns:
            A Bbox enclosing the curve.
        """
        # Extrema candidates: endpoints + roots of derivative
        xs = [self.p1.x, self.p2.x]
        ys = [self.p1.y, self.p2.y]
        # dx/dt = 2(1-t)(cp-p1) + 2t(p2-cp) = 0 => t = (p1-cp)/(p1-2cp+p2)
        for values, lst in [
            ((self.p1.x, self.control_point.x, self.p2.x), xs),
            ((self.p1.y, self.control_point.y, self.p2.y), ys),
        ]:
            a, b, c = values
            denominator = a - 2 * b + c
            if abs(denominator) > ZERO_TOLERANCE:
                t = (a - b) / denominator
                if 0 < t < 1:
                    point = self.evaluate(t)
                    lst.append(point.x if lst is xs else point.y)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return Bbox(
            Point(min_x, min_y),
            max_x - min_x,
            max_y - min_y,
        )

    def get_position_at_fraction(self, fraction: float) -> Point:
        """Get point at a fraction of the arc length.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            The point at that fraction.
        """
        if fraction <= 0:
            return Point(self.p1.x, self.p1.y)
        if fraction >= 1:
            return Point(self.p2.x, self.p2.y)
        total = self.length()
        t = _find_t_at_arc_length_fraction(self.derivative, total, fraction)
        return self.evaluate(t)

    def get_angle_at_fraction(self, fraction: float) -> float:
        """Get angle at a fraction of the arc length.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Angle in radians.
        """
        total = self.length()
        if fraction <= 0:
            t = 0.0
        elif fraction >= 1:
            t = 1.0
        else:
            t = _find_t_at_arc_length_fraction(self.derivative, total, fraction)
        dx, dy = self.derivative(t)
        return math.atan2(dy, dx)

    def get_position_and_angle_at_fraction(
        self, fraction: float
    ) -> tuple[Point, float]:
        """Get both position and angle at a fraction of the arc length.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Tuple of (point, angle_in_radians).
        """
        total = self.length()
        if fraction <= 0:
            t = 0.0
        elif fraction >= 1:
            t = 1.0
        else:
            t = _find_t_at_arc_length_fraction(self.derivative, total, fraction)
        pos = self.evaluate(t)
        dx, dy = self.derivative(t)
        angle = math.atan2(dy, dx)
        return (pos, angle)

    def get_intersection_with_line(self, line: Line) -> list[Point] | list[Segment]:
        """Get intersection with a line.

        Args:
            line: The line to intersect with.

        Returns:
            List of intersection points or segments.
        """
        # Line equation: a*x + b*y + c = 0
        a = line.p2.y - line.p1.y
        b = line.p1.x - line.p2.x
        c = line.p2.x * line.p1.y - line.p1.x * line.p2.y
        # Bezier: B(t) = (1-t)^2 * p0 + 2(1-t)t * p1 + t^2 * p2
        p0x, p0y = self.p1.x, self.p1.y
        p1x, p1y = self.control_point.x, self.control_point.y
        p2x, p2y = self.p2.x, self.p2.y
        # Substitute into line equation: A*t^2 + B*t + C = 0
        ax_coeff = a * (p0x - 2 * p1x + p2x) + b * (p0y - 2 * p1y + p2y)
        bx_coeff = a * (-2 * p0x + 2 * p1x) + b * (-2 * p0y + 2 * p1y)
        cx_coeff = a * p0x + b * p0y + c
        roots = []
        if abs(ax_coeff) < ZERO_TOLERANCE:
            if abs(bx_coeff) > ZERO_TOLERANCE:
                roots.append(-cx_coeff / bx_coeff)
        else:
            disc = bx_coeff * bx_coeff - 4 * ax_coeff * cx_coeff
            if disc >= 0:
                sqrt_disc = math.sqrt(disc)
                roots.append((-bx_coeff + sqrt_disc) / (2 * ax_coeff))
                roots.append((-bx_coeff - sqrt_disc) / (2 * ax_coeff))
        result = []
        for t in roots:
            if -PARAMETER_TOLERANCE <= t <= 1 + PARAMETER_TOLERANCE:
                t = max(0.0, min(1.0, t))
                result.append(self.evaluate(t))
        return result

    def shortened(
        self, length: float, start_or_end: typing.Literal["start", "end"] = "end"
    ) -> "QuadraticBezierCurve":
        """Return a shortened copy of the curve.

        Args:
            length: Amount to shorten by.
            start_or_end: Which end to shorten from.

        Returns:
            A new shortened QuadraticBezierCurve.
        """
        if length == 0 or self.length() == 0:
            return copy.deepcopy(self)
        if start_or_end == "start":
            return self.reversed().shortened(length).reversed()
        total_length = self.length()
        if length > total_length:
            length = total_length
        fraction = 1 - length / total_length
        t = _find_t_at_arc_length_fraction(self.derivative, total_length, fraction)
        left, _ = self.split(t)
        return left

    def reversed(self) -> "QuadraticBezierCurve":
        """Return a reversed copy of the curve.

        Returns:
            A new QuadraticBezierCurve going in reverse direction.
        """
        return QuadraticBezierCurve(self.p2, self.p1, self.control_point)

    def transformed(self, transformation) -> "QuadraticBezierCurve":
        """Apply a transformation to this curve.

        Args:
            transformation: The transformation to apply.

        Returns:
            A new transformed QuadraticBezierCurve.
        """
        return QuadraticBezierCurve(
            self.p1.transformed(transformation),
            self.p2.transformed(transformation),
            self.control_point.transformed(transformation),
        )


@dataclasses.dataclass(frozen=True)
class CubicBezierCurve(GeometryObject):
    """Represents a cubic Bezier curve.

    Attributes:
        p1: Start point.
        p2: End point.
        control_point1: First control point.
        control_point2: Second control point.

    Examples:
        >>> curve = CubicBezierCurve(
        ...     Point(0, 0),
        ...     Point(10, 0),
        ...     Point(3, 5),
        ...     Point(7, 5)
        ... )
    """

    p1: Point
    p2: Point
    control_point1: Point
    control_point2: Point

    def evaluate(self, t: float) -> Point:
        """Evaluate the curve at parameter t.

        Args:
            t: Parameter value from 0 to 1.

        Returns:
            The point at parameter t.
        """
        return self.evaluate_multi([t])[0]

    def evaluate_multi(
        self, t_sequence: collections.abc.Sequence[float]
    ) -> list[Point]:
        """Evaluate the curve at multiple parameters.

        Args:
            t_sequence: Sequence of parameter values.

        Returns:
            List of points.
        """
        t = numpy.asarray(t_sequence, dtype="double")
        u = 1 - t
        u2 = u * u
        t2 = t * t
        x = (
            u2 * u * self.p1.x
            + 3 * u2 * t * self.control_point1.x
            + 3 * u * t2 * self.control_point2.x
            + t2 * t * self.p2.x
        )
        y = (
            u2 * u * self.p1.y
            + 3 * u2 * t * self.control_point1.y
            + 3 * u * t2 * self.control_point2.y
            + t2 * t * self.p2.y
        )
        return [Point(float(xi), float(yi)) for xi, yi in zip(x, y)]

    def derivative(self, t: float) -> tuple[float, float]:
        """Compute the derivative at parameter t.

        Args:
            t: Parameter value from 0 to 1.

        Returns:
            Tuple of (dx/dt, dy/dt).
        """
        u = 1 - t
        dx = (
            3 * u * u * (self.control_point1.x - self.p1.x)
            + 6 * u * t * (self.control_point2.x - self.control_point1.x)
            + 3 * t * t * (self.p2.x - self.control_point2.x)
        )
        dy = (
            3 * u * u * (self.control_point1.y - self.p1.y)
            + 6 * u * t * (self.control_point2.y - self.control_point1.y)
            + 3 * t * t * (self.p2.y - self.control_point2.y)
        )
        return (dx, dy)

    def split(self, t: float) -> tuple["CubicBezierCurve", "CubicBezierCurve"]:
        """Split the curve at parameter t using De Casteljau subdivision.

        Args:
            t: Parameter value from 0 to 1.

        Returns:
            Tuple of two CubicBezierCurves.
        """
        u = 1 - t
        # Level 1
        m0x = u * self.p1.x + t * self.control_point1.x
        m0y = u * self.p1.y + t * self.control_point1.y
        m1x = u * self.control_point1.x + t * self.control_point2.x
        m1y = u * self.control_point1.y + t * self.control_point2.y
        m2x = u * self.control_point2.x + t * self.p2.x
        m2y = u * self.control_point2.y + t * self.p2.y
        # Level 2
        n0x = u * m0x + t * m1x
        n0y = u * m0y + t * m1y
        n1x = u * m1x + t * m2x
        n1y = u * m1y + t * m2y
        # Level 3 (point on curve)
        px = u * n0x + t * n1x
        py = u * n0y + t * n1y
        mid = Point(px, py)
        left = CubicBezierCurve(self.p1, mid, Point(m0x, m0y), Point(n0x, n0y))
        right = CubicBezierCurve(mid, self.p2, Point(n1x, n1y), Point(m2x, m2y))
        return (left, right)

    def length(self) -> float:
        """Calculate the arc length of the curve.

        Returns:
            The arc length.
        """
        return _arc_length(self.derivative, 0.0, 1.0)

    def bbox(self) -> "Bbox":
        """Get the bounding box of the curve.

        Returns:
            A Bbox enclosing the curve.
        """
        xs = [self.p1.x, self.p2.x]
        ys = [self.p1.y, self.p2.y]
        for values, candidates in [
            (
                (self.p1.x, self.control_point1.x, self.control_point2.x, self.p2.x),
                xs,
            ),
            (
                (self.p1.y, self.control_point1.y, self.control_point2.y, self.p2.y),
                ys,
            ),
        ]:
            p0, p1, p2, p3 = values
            a = -3 * p0 + 9 * p1 - 9 * p2 + 3 * p3
            b = 6 * p0 - 12 * p1 + 6 * p2
            c = -3 * p0 + 3 * p1
            if abs(a) < ZERO_TOLERANCE:
                if abs(b) > ZERO_TOLERANCE:
                    t = -c / b
                    if 0 < t < 1:
                        point = self.evaluate(t)
                        candidates.append(point.x if candidates is xs else point.y)
            else:
                disc = b * b - 4 * a * c
                if disc >= 0:
                    sqrt_disc = math.sqrt(disc)
                    for t in [(-b + sqrt_disc) / (2 * a), (-b - sqrt_disc) / (2 * a)]:
                        if 0 < t < 1:
                            point = self.evaluate(t)
                            candidates.append(point.x if candidates is xs else point.y)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return Bbox(
            Point(min_x, min_y),
            max_x - min_x,
            max_y - min_y,
        )

    def get_position_at_fraction(self, fraction: float) -> Point:
        """Get point at a fraction of the arc length.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            The point at that fraction.
        """
        if fraction <= 0:
            return Point(self.p1.x, self.p1.y)
        if fraction >= 1:
            return Point(self.p2.x, self.p2.y)
        total = self.length()
        t = _find_t_at_arc_length_fraction(self.derivative, total, fraction)
        return self.evaluate(t)

    def get_angle_at_fraction(self, fraction: float) -> float:
        """Get angle at a fraction of the arc length.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Angle in radians.
        """
        total = self.length()
        if fraction <= 0:
            t = 0.0
        elif fraction >= 1:
            t = 1.0
        else:
            t = _find_t_at_arc_length_fraction(self.derivative, total, fraction)
        dx, dy = self.derivative(t)
        return math.atan2(dy, dx)

    def get_position_and_angle_at_fraction(
        self, fraction: float
    ) -> tuple[Point, float]:
        """Get both position and angle at a fraction of the arc length.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Tuple of (point, angle_in_radians).
        """
        total = self.length()
        if fraction <= 0:
            t = 0.0
        elif fraction >= 1:
            t = 1.0
        else:
            t = _find_t_at_arc_length_fraction(self.derivative, total, fraction)
        pos = self.evaluate(t)
        dx, dy = self.derivative(t)
        angle = math.atan2(dy, dx)
        return (pos, angle)

    def get_intersection_with_line(self, line: Line) -> list[Point] | list[Segment]:
        """Get intersection with a line.

        Args:
            line: The line to intersect with.

        Returns:
            List of intersection points or segments.
        """
        a = line.p2.y - line.p1.y
        b = line.p1.x - line.p2.x
        c = line.p2.x * line.p1.y - line.p1.x * line.p2.y
        p0x, p0y = self.p1.x, self.p1.y
        p1x, p1y = self.control_point1.x, self.control_point1.y
        p2x, p2y = self.control_point2.x, self.control_point2.y
        p3x, p3y = self.p2.x, self.p2.y
        c3x = -p0x + 3 * p1x - 3 * p2x + p3x
        c2x = 3 * p0x - 6 * p1x + 3 * p2x
        c1x = -3 * p0x + 3 * p1x
        c0x = p0x
        c3y = -p0y + 3 * p1y - 3 * p2y + p3y
        c2y = 3 * p0y - 6 * p1y + 3 * p2y
        c1y = -3 * p0y + 3 * p1y
        c0y = p0y
        coeff3 = a * c3x + b * c3y
        coeff2 = a * c2x + b * c2y
        coeff1 = a * c1x + b * c1y
        coeff0 = a * c0x + b * c0y + c
        roots = numpy.roots([coeff3, coeff2, coeff1, coeff0])
        result = []
        for root in roots:
            if abs(root.imag) < CONVERGENCE_TOLERANCE:
                t = root.real
                if -PARAMETER_TOLERANCE <= t <= 1 + PARAMETER_TOLERANCE:
                    t = max(0.0, min(1.0, t))
                    result.append(self.evaluate(t))
        return result

    def shortened(
        self, length: float, start_or_end: typing.Literal["start", "end"] = "end"
    ) -> "CubicBezierCurve":
        """Return a shortened copy of the curve.

        Args:
            length: Amount to shorten by.
            start_or_end: Which end to shorten from.

        Returns:
            A new shortened CubicBezierCurve.
        """
        if length == 0 or self.length() == 0:
            return copy.deepcopy(self)
        if start_or_end == "start":
            return self.reversed().shortened(length).reversed()
        total_length = self.length()
        if length > total_length:
            length = total_length
        fraction = 1 - length / total_length
        t = _find_t_at_arc_length_fraction(self.derivative, total_length, fraction)
        left, _ = self.split(t)
        return left

    def reversed(self) -> "CubicBezierCurve":
        """Return a reversed copy of the curve.

        Returns:
            A new CubicBezierCurve going in reverse direction.
        """
        return CubicBezierCurve(
            self.p2, self.p1, self.control_point2, self.control_point1
        )

    def transformed(self, transformation) -> "CubicBezierCurve":
        """Apply a transformation to this curve.

        Args:
            transformation: The transformation to apply.

        Returns:
            A new transformed CubicBezierCurve.
        """
        return CubicBezierCurve(
            self.p1.transformed(transformation),
            self.p2.transformed(transformation),
            self.control_point1.transformed(transformation),
            self.control_point2.transformed(transformation),
        )


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

    def __post_init__(self):
        object.__setattr__(self, "rx", round(self.rx, ROUNDING))
        object.__setattr__(self, "ry", round(self.ry, ROUNDING))

    def get_intersection_with_line(self, line: Line) -> list[Point]:
        """Get intersection with a line.

        Args:
            line: The line to intersect with.

        Returns:
            List of intersection points.
        """
        result = []
        for bezier_curve in self.to_bezier_curves():
            result.extend(bezier_curve.get_intersection_with_line(line))
        return result

    def get_center_parameterization(
        self,
    ) -> tuple[float, float, float, float, float, float, float, float]:
        """Get the center parameterization of the arc.

        Returns:
            Tuple of (cx, cy, rx, ry, sigma, theta1, theta2, delta_theta).
        """
        x1, y1 = self.p1.x, self.p1.y
        sigma = self.x_axis_rotation
        x2, y2 = self.p2.x, self.p2.y
        rx = self.rx
        ry = self.ry
        fa = self.arc_flag
        fs = self.sweep_flag
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
        theta1 = _get_angle_between_segments(
            Segment(Point(0, 0), Point(1, 0)),
            Segment(Point(0, 0), Point((x1p - cxp) / rx, (y1p - cyp) / ry)),
        )
        delta_theta = _get_angle_between_segments(
            Segment(Point(0, 0), Point((x1p - cxp) / rx, (y1p - cyp) / ry)),
            Segment(Point(0, 0), Point(-(x1p + cxp) / rx, -(y1p + cyp) / ry)),
        )
        if fs == 0 and delta_theta > 0:
            delta_theta -= 2 * math.pi
        elif fs == 1 and delta_theta < 0:
            delta_theta += 2 * math.pi
        theta2 = theta1 + delta_theta
        return cx, cy, rx, ry, sigma, theta1, theta2, delta_theta

    def get_center(self) -> Point:
        """Get the center point of the ellipse.

        Returns:
            The center point.
        """
        cx, cy, *_ = self.get_center_parameterization()
        return Point(cx, cy)

    def evaluate(self, t: float) -> Point:
        """Evaluate the arc at parameter t using center parameterization.

        Args:
            t: Parameter value from 0 to 1.

        Returns:
            The point at parameter t.
        """
        cx, cy, rx, ry, sigma, theta1, theta2, delta_theta = (
            self.get_center_parameterization()
        )
        theta = theta1 + t * delta_theta
        cos_sigma = math.cos(sigma)
        sin_sigma = math.sin(sigma)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        x = cx + rx * cos_theta * cos_sigma - ry * sin_theta * sin_sigma
        y = cy + rx * cos_theta * sin_sigma + ry * sin_theta * cos_sigma
        return Point(x, y)

    def get_position_at_fraction(self, fraction: float) -> Point:
        """Get point at a fraction along the arc.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            The point at that fraction.
        """
        if fraction <= 0:
            return Point(self.p1.x, self.p1.y)
        if fraction >= 1:
            return Point(self.p2.x, self.p2.y)
        bezier_curves = self.to_bezier_curves()
        if not bezier_curves:
            return Point(self.p1.x, self.p1.y)
        bezier_curve_lengths = [bezier_curve.length() for bezier_curve in bezier_curves]
        total_length = sum(bezier_curve_lengths)
        if total_length == 0:
            return Point(self.p1.x, self.p1.y)
        target = fraction * total_length
        cumulative = 0.0
        for bezier_curve, bezier_curve_length in zip(
            bezier_curves, bezier_curve_lengths
        ):
            if cumulative + bezier_curve_length >= target:
                local_fraction = (
                    (target - cumulative) / bezier_curve_length
                    if bezier_curve_length > 0
                    else 0
                )
                return bezier_curve.get_position_at_fraction(local_fraction)
            cumulative += bezier_curve_length
        return bezier_curves[-1].get_position_at_fraction(1.0)

    def get_angle_at_fraction(self, fraction: float) -> float:
        """Get angle at a fraction along the arc.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Angle in radians.
        """
        bezier_curves = self.to_bezier_curves()
        if not bezier_curves:
            return 0.0
        bezier_curve_lengths = [bezier_curve.length() for bezier_curve in bezier_curves]
        total_length = sum(bezier_curve_lengths)
        if total_length == 0:
            return 0.0
        target = fraction * total_length
        cumulative = 0.0
        for bezier_curve, bezier_curve_length in zip(
            bezier_curves, bezier_curve_lengths
        ):
            if cumulative + bezier_curve_length >= target:
                local_fraction = (
                    (target - cumulative) / bezier_curve_length
                    if bezier_curve_length > 0
                    else 0
                )
                return bezier_curve.get_angle_at_fraction(local_fraction)
            cumulative += bezier_curve_length
        return bezier_curves[-1].get_angle_at_fraction(1.0)

    def get_position_and_angle_at_fraction(
        self, fraction: float
    ) -> tuple[Point, float]:
        """Get both position and angle at a fraction.

        Args:
            fraction: Fraction from 0 to 1.

        Returns:
            Tuple of (point, angle).
        """
        bezier_curves = self.to_bezier_curves()
        if not bezier_curves:
            return (Point(self.p1.x, self.p1.y), 0.0)
        bezier_curve_lengths = [bezier_curve.length() for bezier_curve in bezier_curves]
        total_length = sum(bezier_curve_lengths)
        if total_length == 0:
            return (Point(self.p1.x, self.p1.y), 0.0)
        target = fraction * total_length
        cumulative = 0.0
        for bezier_curve, bezier_curve_length in zip(
            bezier_curves, bezier_curve_lengths
        ):
            if cumulative + bezier_curve_length >= target:
                local_fraction = (
                    (target - cumulative) / bezier_curve_length
                    if bezier_curve_length > 0
                    else 0
                )
                return bezier_curve.get_position_and_angle_at_fraction(local_fraction)
            cumulative += bezier_curve_length
        return bezier_curves[-1].get_position_and_angle_at_fraction(1.0)

    def bbox(self) -> "Bbox":
        """Get the bounding box of the arc.

        Returns:
            A Bbox enclosing the arc.
        """
        bezier_curves = self.to_bezier_curves()
        if not bezier_curves:
            return Bbox(self.p1, 0, 0)
        bboxes = [bezier_curve.bbox() for bezier_curve in bezier_curves]
        return Bbox.union(bboxes)

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
        if length == 0 or self.length() == 0:
            return copy.deepcopy(self)
        if start_or_end == "start":
            return self.reversed().shortened(length).reversed()
        fraction = 1 - length / self.length()
        point = self.get_position_at_fraction(fraction)
        return dataclasses.replace(self, p2=point)

    def transformed(self, transformation: "Transformation") -> "EllipticalArc":
        """Apply a transformation to this arc.

        Args:
            transformation: The transformation to apply.

        Returns:
            A new transformed EllipticalArc.
        """
        east = Point(
            math.cos(self.x_axis_rotation) * self.rx,
            math.sin(self.x_axis_rotation) * self.rx,
        )
        north = Point(
            math.cos(self.x_axis_rotation) * self.ry,
            math.sin(self.x_axis_rotation) * self.ry,
        )
        new_center = Point(0, 0).transformed(transformation)
        new_east = east.transformed(transformation)
        new_north = north.transformed(transformation)
        new_rx = Segment(new_center, new_east).length()
        new_ry = Segment(new_center, new_north).length()
        new_start_point = self.p1.transformed(transformation)
        new_end_point = self.p2.transformed(transformation)
        new_x_axis_rotation = math.degrees(
            Line(new_center, new_east).get_angle_to_horizontal()
        )
        return EllipticalArc(
            p1=new_start_point,
            p2=new_end_point,
            rx=new_rx,
            ry=new_ry,
            x_axis_rotation=new_x_axis_rotation,
            arc_flag=self.arc_flag,
            sweep_flag=self.sweep_flag,
        )

    def reversed(self) -> "EllipticalArc":
        """Return a reversed copy of the arc.

        Returns:
            A new EllipticalArc going in reverse direction.
        """
        return EllipticalArc(
            self.p2,
            self.p1,
            self.rx,
            self.ry,
            self.x_axis_rotation,
            self.arc_flag,
            abs(self.sweep_flag - 1),
        )

    def to_bezier_curves(self) -> list[CubicBezierCurve]:
        """Convert to cubic Bezier curves.

        Returns:
            List of CubicBezierCurve approximating the arc.
        """

        def _make_angles(angles):
            new_angles = [angles[0]]
            for theta1, theta2 in zip(angles, angles[1:]):
                delta_theta = theta2 - theta1
                if abs(delta_theta) > math.pi / 2:
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
        ) = self.get_center_parameterization()
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
            bezier_curve = CubicBezierCurve(
                p1=p1,
                p2=p2,
                control_point1=control_point1,
                control_point2=control_point2,
            ).transformed(transformation)
            bezier_curves.append(bezier_curve)
        return bezier_curves

    def length(self) -> float:
        """Calculate the length of the arc.

        Returns:
            The arc length.
        """
        return sum(bc.length() for bc in self.to_bezier_curves())


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

    def __post_init__(self):
        object.__setattr__(self, "width", round(self.width, ROUNDING))
        object.__setattr__(self, "height", round(self.height, ROUNDING))

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
    def around_points(cls, points: collections.abc.Iterable[Point]) -> "Bbox":
        """Create a minimal Bbox enclosing all given points.

        Args:
            points: An iterable of Point objects.

        Returns:
            A new Bbox that tightly encloses all input points.

        Raises:
            ValueError: If the iterable is empty.
        """
        it = iter(points)
        try:
            first = next(it)
        except StopIteration:
            raise ValueError("points must contain at least one point")
        min_x = max_x = first.x
        min_y = max_y = first.y
        for p in it:
            if p.x < min_x:
                min_x = p.x
            elif p.x > max_x:
                max_x = p.x
            if p.y < min_y:
                min_y = p.y
            elif p.y > max_y:
                max_y = p.y
        return cls(
            Point((min_x + max_x) / 2, (min_y + max_y) / 2),
            max_x - min_x,
            max_y - min_y,
        )

    @classmethod
    def union(cls, bboxes: list["Bbox"]) -> "Bbox":
        """Create a Bbox enclosing all given bounding boxes.

        Args:
            bboxes: List of Bbox objects to merge.

        Returns:
            A new Bbox enclosing all input bboxes.
        """
        if not bboxes:
            return cls(Point(0, 0), 0, 0)
        corners = []
        for bbox in bboxes:
            corners.append(bbox.north_west())
            corners.append(bbox.south_east())
        return cls.around_points(corners)


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
        return MatrixTransformation(numpy.linalg.inv(self.m))


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
        return Rotation(-self.angle, self.point)


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
        return Translation(-self.tx, -self.ty)


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
        return Scaling(1 / self.sx, 1 / self.sy)


def _intersect_line_with_primitive(
    line: Line,
    primitive: "Segment | QuadraticBezierCurve | CubicBezierCurve | EllipticalArc",
) -> list[Point]:
    """Get intersection of a line with a geometry primitive.

    Args:
        line: The line.
        primitive: A geometry primitive.

    Returns:
        List of intersection points.
    """
    result = primitive.get_intersection_with_line(line)
    points = []
    for obj in result:
        if isinstance(obj, Point):
            points.append(obj)
        elif isinstance(obj, Segment):
            points.append(obj.p1)
            points.append(obj.p2)
    return points


def get_primitives_border(
    primitives: list[Segment | QuadraticBezierCurve | CubicBezierCurve | EllipticalArc],
    point: Point,
    center: Point | None = None,
) -> Point | None:
    """Get the border point of geometry primitives in a given direction.

    Args:
        primitives: List of geometry primitives.
        point: Direction point.
        center: Optional center point. Defaults to bbox center.

    Returns:
        The border point or None.
    """
    if not primitives:
        return None
    if center is None:
        bboxes = [p.bbox() for p in primitives]
        bbox = Bbox.union(bboxes)
        center = bbox.center()
    if center.isnan():
        return None
    line = Line(center, point)
    candidate_points = []
    for primitive in primitives:
        candidate_points.extend(_intersect_line_with_primitive(line, primitive))
    intersection_point = None
    max_d = -1
    ok_direction_exists = False
    d1 = Segment(point, center).length()
    for candidate_point in candidate_points:
        d2 = Segment(candidate_point, point).length()
        d3 = Segment(candidate_point, center).length()
        candidate_ok_direction = not d2 > d1 or d2 < d3
        if candidate_ok_direction or not ok_direction_exists:
            if candidate_ok_direction and not ok_direction_exists:
                ok_direction_exists = True
                max_d = -1
            if d3 > max_d:
                max_d = d3
                intersection_point = candidate_point
    return intersection_point


def get_primitives_angle(
    primitives: list[Segment | QuadraticBezierCurve | CubicBezierCurve | EllipticalArc],
    angle: float,
    unit: typing.Literal["degrees", "radians"] = "degrees",
    center: Point | None = None,
) -> Point | None:
    """Get the border point at a given angle.

    Args:
        primitives: List of geometry primitives.
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
        bboxes = [p.bbox() for p in primitives]
        bbox = Bbox.union(bboxes)
        center = bbox.center()
        if center.isnan():
            return None
    point = center + (d * math.cos(angle), d * math.sin(angle))
    return get_primitives_border(primitives, point, center)


def get_primitives_anchor_point(
    primitives: list[
        "Segment | QuadraticBezierCurve | CubicBezierCurve | EllipticalArc"
    ],
    anchor_point: str,
    center: Point | None = None,
) -> Point | None:
    """Get an anchor point of geometry primitives.

    Args:
        primitives: List of geometry primitives.
        anchor_point: Name of anchor point.
        center: Optional center point.

    Returns:
        The anchor point or None.
    """
    bboxes = [p.bbox() for p in primitives]
    bbox = Bbox.union(bboxes)
    if center is None:
        center = bbox.center()
    if center.isnan():
        return None
    point = bbox.anchor_point(anchor_point)
    return get_primitives_border(primitives, point, center)


def get_normalized_angle(angle: float) -> float:
    """Normalize an angle to [0, 2*pi).

    Args:
        angle: Angle in radians.

    Returns:
        Normalized angle.
    """
    return angle - (angle // (2 * math.pi) * (2 * math.pi))


def _get_angle_between_segments(segment1: Segment, segment2: Segment) -> float:
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
