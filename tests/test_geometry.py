"""Tests for momapy.geometry module."""

import pytest
import math
import numpy
import momapy.geometry


class TestPoint:
    """Tests for Point class."""

    def test_point_creation(self):
        """Test creating a Point."""
        p = momapy.geometry.Point(10.0, 20.0)
        assert p.x == 10.0
        assert p.y == 20.0

    def test_point_rounding(self):
        """Test that points are rounded on creation."""
        p = momapy.geometry.Point(10.123456789, 20.987654321)
        assert p.x == 10.12  # ROUNDING = 2
        assert p.y == 20.99

    def test_point_addition(self):
        """Test point addition."""
        p1 = momapy.geometry.Point(10.0, 20.0)
        p2 = momapy.geometry.Point(5.0, 3.0)
        result = p1 + p2
        assert result.x == 15.0
        assert result.y == 23.0

        # Test addition with tuple
        result2 = p1 + (5.0, 3.0)
        assert result2.x == 15.0
        assert result2.y == 23.0

    def test_point_subtraction(self):
        """Test point subtraction."""
        p1 = momapy.geometry.Point(10.0, 20.0)
        p2 = momapy.geometry.Point(5.0, 3.0)
        result = p1 - p2
        assert result.x == 5.0
        assert result.y == 17.0

    def test_point_multiplication(self):
        """Test point multiplication by scalar."""
        p = momapy.geometry.Point(10.0, 20.0)
        result = p * 2
        assert result.x == 20.0
        assert result.y == 40.0

    def test_point_division(self):
        """Test point division by scalar."""
        p = momapy.geometry.Point(10.0, 20.0)
        result = p / 2
        assert result.x == 5.0
        assert result.y == 10.0

    def test_point_iteration(self):
        """Test point iteration."""
        p = momapy.geometry.Point(10.0, 20.0)
        coords = list(p)
        assert coords == [10.0, 20.0]

    def test_point_to_tuple(self):
        """Test point to_tuple method."""
        p = momapy.geometry.Point(10.0, 20.0)
        t = p.to_tuple()
        assert t == (10.0, 20.0)

    def test_point_to_matrix(self):
        """Test point to_matrix method."""
        p = momapy.geometry.Point(10.0, 20.0)
        m = p.to_matrix()
        assert isinstance(m, numpy.ndarray)
        assert m[0][0] == 10.0
        assert m[1][0] == 20.0

    def test_point_from_tuple(self):
        """Test creating point from tuple."""
        p = momapy.geometry.Point.from_tuple((10.0, 20.0))
        assert p.x == 10.0
        assert p.y == 20.0

    def test_point_round(self):
        """Test point round method."""
        p = momapy.geometry.Point(10.123, 20.987)
        rounded = p.round(1)
        assert rounded.x == 10.1
        assert rounded.y == 21.0

    def test_point_isnan(self):
        """Test point isnan method."""
        p1 = momapy.geometry.Point(10.0, 20.0)
        assert not p1.isnan()

        p2 = momapy.geometry.Point(float("nan"), 20.0)
        assert p2.isnan()

    def test_point_bbox(self):
        """Test point bbox method."""
        p = momapy.geometry.Point(10.0, 20.0)
        bbox = p.bbox()
        assert isinstance(bbox, momapy.geometry.Bbox)
        assert bbox.width == 0
        assert bbox.height == 0


class TestLine:
    """Tests for Line class."""

    def test_line_creation(self):
        """Test creating a Line."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 10.0)
        line = momapy.geometry.Line(p1, p2)
        assert line.p1 == p1
        assert line.p2 == p2

    def test_line_slope(self):
        """Test line slope calculation."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 10.0)
        line = momapy.geometry.Line(p1, p2)
        assert line.slope() == 1.0

    def test_line_slope_vertical(self):
        """Test vertical line slope (should be NaN)."""
        p1 = momapy.geometry.Point(5.0, 0.0)
        p2 = momapy.geometry.Point(5.0, 10.0)
        line = momapy.geometry.Line(p1, p2)
        assert math.isnan(line.slope())

    def test_line_intercept(self):
        """Test line intercept calculation."""
        p1 = momapy.geometry.Point(0.0, 5.0)
        p2 = momapy.geometry.Point(10.0, 15.0)
        line = momapy.geometry.Line(p1, p2)
        assert line.intercept() == 5.0

    def test_line_to_shapely(self):
        """Test line to_shapely conversion."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 10.0)
        line = momapy.geometry.Line(p1, p2)
        shapely_line = line.to_shapely()
        assert shapely_line is not None


class TestSegment:
    """Tests for Segment class."""

    def test_segment_creation(self):
        """Test creating a Segment."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(3.0, 4.0)
        segment = momapy.geometry.Segment(p1, p2)
        assert segment.p1 == p1
        assert segment.p2 == p2

    def test_segment_length(self):
        """Test segment length calculation."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(3.0, 4.0)
        segment = momapy.geometry.Segment(p1, p2)
        assert segment.length() == 5.0

    def test_segment_to_shapely(self):
        """Test segment to_shapely conversion."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 10.0)
        segment = momapy.geometry.Segment(p1, p2)
        shapely_seg = segment.to_shapely()
        assert shapely_seg is not None

    def test_segment_bbox(self):
        """Test segment bbox method."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 10.0)
        segment = momapy.geometry.Segment(p1, p2)
        bbox = segment.bbox()
        assert isinstance(bbox, momapy.geometry.Bbox)


class TestEllipticalArc:
    """Tests for EllipticalArc class."""

    def test_elliptical_arc_creation(self):
        """Test creating an EllipticalArc."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 0.0)
        arc = momapy.geometry.EllipticalArc(
            p1, p2, rx=5.0, ry=5.0, x_axis_rotation=0.0, arc_flag=0, sweep_flag=1
        )
        assert arc.p1 == p1
        assert arc.p2 == p2
        assert arc.rx == 5.0
        assert arc.ry == 5.0

    def test_elliptical_arc_to_shapely(self):
        """Test elliptical arc to_shapely conversion."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 0.0)
        arc = momapy.geometry.EllipticalArc(
            p1, p2, rx=5.0, ry=5.0, x_axis_rotation=0.0, arc_flag=0, sweep_flag=1
        )
        shapely_arc = arc.to_shapely()
        assert shapely_arc is not None


class TestBbox:
    """Tests for Bbox class."""

    def test_bbox_creation(self):
        """Test creating a Bbox."""
        position = momapy.geometry.Point(50.0, 50.0)
        bbox = momapy.geometry.Bbox(position, 100.0, 60.0)
        assert bbox.position == position
        assert bbox.width == 100.0
        assert bbox.height == 60.0

    def test_bbox_properties(self):
        """Test bbox x and y properties."""
        position = momapy.geometry.Point(50.0, 50.0)
        bbox = momapy.geometry.Bbox(position, 100.0, 60.0)
        assert bbox.x == 50.0
        assert bbox.y == 50.0

    def test_bbox_size(self):
        """Test bbox size method."""
        position = momapy.geometry.Point(50.0, 50.0)
        bbox = momapy.geometry.Bbox(position, 100.0, 60.0)
        size = bbox.size()
        assert size == (100.0, 60.0)

    def test_bbox_center(self):
        """Test bbox center anchor point."""
        position = momapy.geometry.Point(50.0, 50.0)
        bbox = momapy.geometry.Bbox(position, 100.0, 60.0)
        center = bbox.center()
        assert center.x == 50.0
        assert center.y == 50.0

    def test_bbox_north(self):
        """Test bbox north anchor point."""
        position = momapy.geometry.Point(50.0, 50.0)
        bbox = momapy.geometry.Bbox(position, 100.0, 60.0)
        north = bbox.north()
        assert north.x == 50.0
        assert north.y == 20.0  # 50 - 60/2

    def test_bbox_south(self):
        """Test bbox south anchor point."""
        position = momapy.geometry.Point(50.0, 50.0)
        bbox = momapy.geometry.Bbox(position, 100.0, 60.0)
        south = bbox.south()
        assert south.x == 50.0
        assert south.y == 80.0  # 50 + 60/2

    def test_bbox_east(self):
        """Test bbox east anchor point."""
        position = momapy.geometry.Point(50.0, 50.0)
        bbox = momapy.geometry.Bbox(position, 100.0, 60.0)
        east = bbox.east()
        assert east.x == 100.0  # 50 + 100/2
        assert east.y == 50.0

    def test_bbox_west(self):
        """Test bbox west anchor point."""
        position = momapy.geometry.Point(50.0, 50.0)
        bbox = momapy.geometry.Bbox(position, 100.0, 60.0)
        west = bbox.west()
        assert west.x == 0.0  # 50 - 100/2
        assert west.y == 50.0

    def test_bbox_north_east(self):
        """Test bbox north_east anchor point."""
        position = momapy.geometry.Point(50.0, 50.0)
        bbox = momapy.geometry.Bbox(position, 100.0, 60.0)
        ne = bbox.north_east()
        assert ne.x == 100.0
        assert ne.y == 20.0

    def test_bbox_from_bounds(self):
        """Test creating Bbox from bounds."""
        bounds = (0.0, 0.0, 100.0, 60.0)  # (min_x, min_y, max_x, max_y)
        bbox = momapy.geometry.Bbox.from_bounds(bounds)
        assert bbox.position.x == 50.0
        assert bbox.position.y == 30.0
        assert bbox.width == 100.0
        assert bbox.height == 60.0

    def test_bbox_isnan(self):
        """Test bbox isnan method."""
        position = momapy.geometry.Point(50.0, 50.0)
        bbox = momapy.geometry.Bbox(position, 100.0, 60.0)
        assert not bbox.isnan()


class TestTransformations:
    """Tests for Transformation classes."""

    def test_translation_creation(self):
        """Test creating a Translation."""
        trans = momapy.geometry.Translation(10.0, 20.0)
        assert trans.tx == 10.0
        assert trans.ty == 20.0

    def test_translation_to_matrix(self):
        """Test translation to_matrix method."""
        trans = momapy.geometry.Translation(10.0, 20.0)
        m = trans.to_matrix()
        assert isinstance(m, numpy.ndarray)
        assert m[0][2] == 10.0
        assert m[1][2] == 20.0

    def test_rotation_creation(self):
        """Test creating a Rotation."""
        rot = momapy.geometry.Rotation(math.pi / 2)
        assert rot.angle == math.pi / 2

    def test_rotation_to_matrix(self):
        """Test rotation to_matrix method."""
        rot = momapy.geometry.Rotation(math.pi / 2)
        m = rot.to_matrix()
        assert isinstance(m, numpy.ndarray)

    def test_scaling_creation(self):
        """Test creating a Scaling."""
        scale = momapy.geometry.Scaling(2.0, 3.0)
        assert scale.sx == 2.0
        assert scale.sy == 3.0

    def test_scaling_to_matrix(self):
        """Test scaling to_matrix method."""
        scale = momapy.geometry.Scaling(2.0, 3.0)
        m = scale.to_matrix()
        assert isinstance(m, numpy.ndarray)
        assert m[0][0] == 2.0
        assert m[1][1] == 3.0

    def test_transform_point(self):
        """Test transforming a point with translation."""
        p = momapy.geometry.Point(10.0, 20.0)
        trans = momapy.geometry.Translation(5.0, 10.0)
        transformed = momapy.geometry.transform_point(p, trans)
        assert transformed.x == 15.0
        assert transformed.y == 30.0

    def test_point_transformed_method(self):
        """Test point transformed method."""
        p = momapy.geometry.Point(10.0, 20.0)
        trans = momapy.geometry.Translation(5.0, 10.0)
        transformed = p.transformed(trans)
        assert transformed.x == 15.0
        assert transformed.y == 30.0

    def test_transformation_multiplication(self):
        """Test transformation multiplication."""
        trans1 = momapy.geometry.Translation(10.0, 20.0)
        trans2 = momapy.geometry.Translation(5.0, 10.0)
        combined = trans1 * trans2
        assert isinstance(combined, momapy.geometry.MatrixTransformation)

    def test_invert_scaling_reciprocal(self):
        """Test that invert_scaling returns reciprocal, not negation."""
        scaling = momapy.geometry.Scaling(2.0, 3.0)
        inverted = momapy.geometry.invert_scaling(scaling)
        assert inverted.sx == 0.5  # 1/2, not -2
        assert inverted.sy == pytest.approx(1.0 / 3.0)  # 1/3, not -3

    def test_invert_scaling_composition(self):
        """Test that scaling and inverse return to original."""
        p = momapy.geometry.Point(10.0, 20.0)
        scaling = momapy.geometry.Scaling(2.0, 4.0)
        inverted = momapy.geometry.invert_scaling(scaling)

        # Apply scaling then inverse
        scaled = p.transformed(scaling)
        restored = scaled.transformed(inverted)

        assert restored.x == pytest.approx(p.x, rel=1e-10)
        assert restored.y == pytest.approx(p.y, rel=1e-10)


class TestIntersectionFunctions:
    """Tests for intersection functions."""

    def test_intersection_of_perpendicular_lines(self):
        """Test intersection of perpendicular lines."""
        # Horizontal line: y = 5
        line1 = momapy.geometry.Line(
            momapy.geometry.Point(0.0, 5.0), momapy.geometry.Point(10.0, 5.0)
        )
        # Vertical line: x = 3
        line2 = momapy.geometry.Line(
            momapy.geometry.Point(3.0, 0.0), momapy.geometry.Point(3.0, 10.0)
        )

        intersections = momapy.geometry.get_intersection_of_lines(line1, line2)
        assert len(intersections) == 1
        assert isinstance(intersections[0], momapy.geometry.Point)
        assert intersections[0].x == 3.0
        assert intersections[0].y == 5.0

    def test_intersection_of_parallel_lines(self):
        """Test that parallel lines return empty list."""
        line1 = momapy.geometry.Line(
            momapy.geometry.Point(0.0, 0.0), momapy.geometry.Point(10.0, 0.0)
        )
        line2 = momapy.geometry.Line(
            momapy.geometry.Point(0.0, 5.0), momapy.geometry.Point(10.0, 5.0)
        )

        intersections = momapy.geometry.get_intersection_of_lines(line1, line2)
        assert len(intersections) == 0

    def test_intersection_line_and_segment_inside(self):
        """Test intersection when line crosses segment."""
        line = momapy.geometry.Line(
            momapy.geometry.Point(5.0, 0.0), momapy.geometry.Point(5.0, 10.0)
        )
        segment = momapy.geometry.Segment(
            momapy.geometry.Point(0.0, 5.0), momapy.geometry.Point(10.0, 5.0)
        )

        intersections = momapy.geometry.get_intersection_of_line_and_segment(
            line, segment
        )
        assert len(intersections) == 1
        assert isinstance(intersections[0], momapy.geometry.Point)
        assert intersections[0].x == 5.0
        assert intersections[0].y == 5.0

    def test_intersection_line_and_segment_outside(self):
        """Test intersection when line misses segment."""
        line = momapy.geometry.Line(
            momapy.geometry.Point(15.0, 0.0), momapy.geometry.Point(15.0, 10.0)
        )
        segment = momapy.geometry.Segment(
            momapy.geometry.Point(0.0, 5.0), momapy.geometry.Point(10.0, 5.0)
        )

        intersections = momapy.geometry.get_intersection_of_line_and_segment(
            line, segment
        )
        assert len(intersections) == 0


class TestBezierCurve:
    """Tests for BezierCurve class."""

    def test_bezier_curve_creation(self):
        """Test creating a BezierCurve."""
        curve = momapy.geometry.BezierCurve(
            momapy.geometry.Point(0.0, 0.0),
            momapy.geometry.Point(3.0, 0.0),
            control_points=(
                momapy.geometry.Point(1.0, 0.5),
                momapy.geometry.Point(2.0, 0.5),
            ),
        )
        assert curve.p1.x == 0.0
        assert curve.p2.x == 3.0

    def test_bezier_curve_evaluate_start(self):
        """Test evaluate at t=0 returns start point."""
        start = momapy.geometry.Point(0.0, 0.0)
        curve = momapy.geometry.BezierCurve(
            start,
            momapy.geometry.Point(3.0, 0.0),
            control_points=(
                momapy.geometry.Point(1.0, 1.0),
                momapy.geometry.Point(2.0, 1.0),
            ),
        )
        result = curve.evaluate(0.0)
        assert result.x == start.x
        assert result.y == start.y

    def test_bezier_curve_evaluate_end(self):
        """Test evaluate at t=1 returns end point."""
        end = momapy.geometry.Point(3.0, 0.0)
        curve = momapy.geometry.BezierCurve(
            momapy.geometry.Point(0.0, 0.0),
            end,
            control_points=(
                momapy.geometry.Point(1.0, 1.0),
                momapy.geometry.Point(2.0, 1.0),
            ),
        )
        result = curve.evaluate(1.0)
        assert result.x == end.x
        assert result.y == end.y

    def test_bezier_curve_to_shapely(self):
        """Test that bezier curve converts to shapely."""
        curve = momapy.geometry.BezierCurve(
            momapy.geometry.Point(0.0, 0.0),
            momapy.geometry.Point(3.0, 0.0),
            control_points=(
                momapy.geometry.Point(1.0, 1.0),
                momapy.geometry.Point(2.0, 1.0),
            ),
        )
        shapely_obj = curve.to_shapely()
        assert shapely_obj is not None

    def test_bezier_curve_transformed(self):
        """Test transformed bezier curve."""
        curve = momapy.geometry.BezierCurve(
            momapy.geometry.Point(0.0, 0.0),
            momapy.geometry.Point(3.0, 0.0),
            control_points=(
                momapy.geometry.Point(1.0, 1.0),
                momapy.geometry.Point(2.0, 1.0),
            ),
        )
        # Apply translation
        translation = momapy.geometry.Translation(5.0, 10.0)
        transformed = curve.transformed(translation)

        # Check that all points were translated
        assert transformed.p1.x == 5.0
        assert transformed.p1.y == 10.0
        assert transformed.p2.x == 8.0
        assert transformed.p2.y == 10.0

    def test_bezier_curve_reversed(self):
        """Test reversed bezier curve swaps endpoints."""
        start = momapy.geometry.Point(0.0, 0.0)
        end = momapy.geometry.Point(3.0, 0.0)
        curve = momapy.geometry.BezierCurve(
            start,
            end,
            control_points=(
                momapy.geometry.Point(1.0, 1.0),
                momapy.geometry.Point(2.0, 1.0),
            ),
        )
        reversed_curve = curve.reversed()
        assert reversed_curve.p1.x == end.x
        assert reversed_curve.p2.x == start.x


class TestSegmentMethods:
    """Tests for Segment additional methods."""

    def test_segment_get_position_at_fraction_start(self):
        """Test get_position_at_fraction at 0 returns p1."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 10.0)
        segment = momapy.geometry.Segment(p1, p2)
        result = segment.get_position_at_fraction(0.0)
        assert result.x == p1.x
        assert result.y == p1.y

    def test_segment_get_position_at_fraction_end(self):
        """Test get_position_at_fraction at 1 returns p2."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 10.0)
        segment = momapy.geometry.Segment(p1, p2)
        result = segment.get_position_at_fraction(1.0)
        assert result.x == p2.x
        assert result.y == p2.y

    def test_segment_get_position_at_fraction_midpoint(self):
        """Test get_position_at_fraction at 0.5 returns midpoint."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 10.0)
        segment = momapy.geometry.Segment(p1, p2)
        result = segment.get_position_at_fraction(0.5)
        assert result.x == 5.0
        assert result.y == 5.0

    def test_segment_shortened_from_start(self):
        """Test shortening segment from start."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 0.0)
        segment = momapy.geometry.Segment(p1, p2)
        shortened = segment.shortened(length=2.0, start_or_end="start")
        assert shortened.length() == pytest.approx(8.0)

    def test_segment_shortened_from_end(self):
        """Test shortening segment from end."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 0.0)
        segment = momapy.geometry.Segment(p1, p2)
        shortened = segment.shortened(length=2.0, start_or_end="end")
        assert shortened.length() == pytest.approx(8.0)

    def test_segment_reversed(self):
        """Test reversed segment swaps endpoints."""
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 10.0)
        segment = momapy.geometry.Segment(p1, p2)
        reversed_seg = segment.reversed()
        assert reversed_seg.p1.x == p2.x
        assert reversed_seg.p2.x == p1.x


class TestSegmentGetPositionAndAngleAtFraction:
    """Tests for Segment.get_position_and_angle_at_fraction."""

    def test_position_at_start(self):
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 0.0)
        segment = momapy.geometry.Segment(p1, p2)
        position, _ = segment.get_position_and_angle_at_fraction(0.0)
        assert position.x == pytest.approx(0.0, abs=0.01)
        assert position.y == pytest.approx(0.0, abs=0.01)

    def test_position_at_end(self):
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 0.0)
        segment = momapy.geometry.Segment(p1, p2)
        position, _ = segment.get_position_and_angle_at_fraction(1.0)
        assert position.x == pytest.approx(10.0, abs=0.01)
        assert position.y == pytest.approx(0.0, abs=0.01)

    def test_position_at_midpoint(self):
        p1 = momapy.geometry.Point(0.0, 0.0)
        p2 = momapy.geometry.Point(10.0, 0.0)
        segment = momapy.geometry.Segment(p1, p2)
        position, _ = segment.get_position_and_angle_at_fraction(0.5)
        assert position.x == pytest.approx(5.0, abs=0.01)
        assert position.y == pytest.approx(0.0, abs=0.01)

    def test_angle_horizontal_segment(self):
        segment = momapy.geometry.Segment(
            momapy.geometry.Point(0.0, 0.0),
            momapy.geometry.Point(10.0, 0.0),
        )
        _, angle = segment.get_position_and_angle_at_fraction(0.5)
        assert angle == pytest.approx(0.0, abs=0.01)

    def test_angle_diagonal_segment(self):
        segment = momapy.geometry.Segment(
            momapy.geometry.Point(0.0, 0.0),
            momapy.geometry.Point(10.0, 10.0),
        )
        _, angle = segment.get_position_and_angle_at_fraction(0.5)
        assert angle == pytest.approx(math.pi / 4, abs=0.01)


class TestBezierCurveGetPositionAndAngleAtFraction:
    """Tests for BezierCurve.get_position_and_angle_at_fraction.

    Uses a symmetric cubic curve (p1=(0,0), p2=(10,0), cp1=(3,5), cp2=(7,5))
    whose peak is at the arc-length midpoint (by symmetry).
    """

    @pytest.fixture
    def symmetric_curve(self):
        return momapy.geometry.BezierCurve(
            momapy.geometry.Point(0.0, 0.0),
            momapy.geometry.Point(10.0, 0.0),
            control_points=(
                momapy.geometry.Point(3.0, 5.0),
                momapy.geometry.Point(7.0, 5.0),
            ),
        )

    def test_position_at_start(self, symmetric_curve):
        position, _ = symmetric_curve.get_position_and_angle_at_fraction(0.0)
        assert position.x == pytest.approx(0.0, abs=0.01)
        assert position.y == pytest.approx(0.0, abs=0.01)

    def test_position_at_end(self, symmetric_curve):
        position, _ = symmetric_curve.get_position_and_angle_at_fraction(1.0)
        assert position.x == pytest.approx(10.0, abs=0.01)
        assert position.y == pytest.approx(0.0, abs=0.01)

    def test_angle_at_midpoint_is_horizontal(self, symmetric_curve):
        # At the arc-length midpoint of a symmetric curve the tangent is
        # horizontal, i.e. angle == 0 (mod 2π).  Before the _get_angle_at_fraction
        # fix (missing `previous_coord = current_coord` update) this returned
        # a wrong non-zero angle.
        _, angle = symmetric_curve.get_position_and_angle_at_fraction(0.5)
        # Normalise to (-π, π] for comparison
        angle_signed = (angle + math.pi) % (2 * math.pi) - math.pi
        assert angle_signed == pytest.approx(0.0, abs=0.05)


class TestEllipticalArcGetPositionAndAngleAtFraction:
    """Tests for EllipticalArc.get_position_and_angle_at_fraction."""

    @pytest.fixture
    def semicircle(self):
        # Semicircle: centre at (5,0), radius 5, sweeping upward
        return momapy.geometry.EllipticalArc(
            momapy.geometry.Point(0.0, 0.0),
            momapy.geometry.Point(10.0, 0.0),
            rx=5.0,
            ry=5.0,
            x_axis_rotation=0.0,
            arc_flag=0,
            sweep_flag=0,
        )

    def test_position_at_start(self, semicircle):
        position, _ = semicircle.get_position_and_angle_at_fraction(0.0)
        assert position.x == pytest.approx(0.0, abs=0.1)
        assert position.y == pytest.approx(0.0, abs=0.1)

    def test_position_at_end(self, semicircle):
        position, _ = semicircle.get_position_and_angle_at_fraction(1.0)
        assert position.x == pytest.approx(10.0, abs=0.1)
        assert position.y == pytest.approx(0.0, abs=0.1)

    def test_position_at_midpoint_is_bottom_of_arc(self, semicircle):
        # SVG y-axis points down; sweep_flag=0 sweeps downward, so the
        # midpoint of the semicircle is at (5, 5).
        position, _ = semicircle.get_position_and_angle_at_fraction(0.5)
        assert position.x == pytest.approx(5.0, abs=0.1)
        assert position.y == pytest.approx(5.0, abs=0.1)


class TestShapelyBorderAndAnchor:
    """Tests for shapely object border and anchor functions."""

    def test_shapely_object_border(self):
        """Test getting border point of shapely object."""
        import shapely.geometry

        rect = shapely.geometry.Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        north_point = momapy.geometry.Point(5.0, 20.0)
        border = momapy.geometry.get_shapely_object_border(rect, north_point)
        assert border is not None
        assert isinstance(border, momapy.geometry.Point)

    def test_shapely_object_anchor_point(self):
        """Test getting anchor point from shapely object."""
        import shapely.geometry

        rect = shapely.geometry.Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        anchor = momapy.geometry.get_shapely_object_anchor_point(rect, "north")
        assert isinstance(anchor, momapy.geometry.Point)
