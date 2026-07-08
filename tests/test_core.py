"""Tests for momapy.core module."""

import dataclasses
import pytest
import momapy.core
import momapy.core.elements
import momapy.core.layout
import momapy.geometry
import momapy.coloring


# Minimal concrete Arc subclass for testing Arc.fraction()
@dataclasses.dataclass(frozen=True, kw_only=True)
class _ConcreteArc(momapy.core.layout.Arc):
    def own_drawing_elements(self):
        return []

    def _arrowhead_border_drawing_elements(self):
        return []


def test_direction_enum():
    """Test Direction enum."""
    assert momapy.core.elements.Direction.UP is not None
    assert momapy.core.elements.Direction.RIGHT is not None
    assert momapy.core.elements.Direction.DOWN is not None
    assert momapy.core.elements.Direction.LEFT is not None


def test_orientation_enum():
    """Test Orientation enum."""
    assert momapy.core.elements.Orientation.HORIZONTAL is not None
    assert momapy.core.elements.Orientation.VERTICAL is not None


def test_halignment_enum():
    """Test HAlignment enum."""
    assert momapy.core.elements.HAlignment.LEFT is not None
    assert momapy.core.elements.HAlignment.CENTER is not None
    assert momapy.core.elements.HAlignment.RIGHT is not None


def test_valignment_enum():
    """Test VAlignment enum."""
    assert momapy.core.elements.VAlignment.TOP is not None
    assert momapy.core.elements.VAlignment.CENTER is not None
    assert momapy.core.elements.VAlignment.BOTTOM is not None


def test_map_element_creation():
    """Test MapElement creation."""
    element = momapy.core.elements.MapElement()
    assert element.id_ is not None
    assert isinstance(element.id_, str)


def test_map_element_with_custom_id():
    """Test MapElement with custom id."""
    element = momapy.core.elements.MapElement(id_="custom_id")
    assert element.id_ == "custom_id"


def test_model_element_creation():
    """Test ModelElement creation."""
    element = momapy.core.elements.ModelElement()
    assert element.id_ is not None
    assert isinstance(element.id_, str)


def test_text_layout_creation(sample_point):
    """Test TextLayout creation."""
    text_layout = momapy.core.layout.TextLayout(
        text="Hello World",
        position=sample_point,
    )
    assert text_layout.text == "Hello World"
    assert text_layout.position == sample_point
    assert text_layout.horizontal_alignment == momapy.core.elements.HAlignment.LEFT
    assert text_layout.vertical_alignment == momapy.core.elements.VAlignment.TOP


def test_text_layout_with_custom_alignment(sample_point):
    """Test TextLayout with custom alignment."""
    text_layout = momapy.core.layout.TextLayout(
        text="Test",
        position=sample_point,
        horizontal_alignment=momapy.core.elements.HAlignment.CENTER,
        vertical_alignment=momapy.core.elements.VAlignment.CENTER,
    )
    assert text_layout.horizontal_alignment == momapy.core.elements.HAlignment.CENTER
    assert text_layout.vertical_alignment == momapy.core.elements.VAlignment.CENTER


def test_layout_creation(sample_point):
    """Test Layout creation."""
    layout = momapy.core.layout.Layout(
        position=sample_point, width=100, height=100, layout_elements=[]
    )
    assert layout.position == sample_point
    assert layout.width == 100
    assert layout.height == 100


def test_layout_with_elements(sample_point):
    """Test Layout with elements."""
    text_layout = momapy.core.layout.TextLayout(
        text="Test",
        position=sample_point,
    )
    layout = momapy.core.layout.Layout(
        position=momapy.geometry.Point(0, 0),
        width=200,
        height=200,
        layout_elements=[text_layout],
    )
    assert len(layout.layout_elements) == 1


class TestArcFraction:
    """Tests for Arc.fraction() across single- and multi-segment arcs.

    Uses two horizontal segments so expected positions are exact integers.
    """

    @pytest.fixture
    def two_equal_segments_arc(self):
        # Two segments of length 10 each: (0,0)→(10,0)→(20,0)
        seg1 = momapy.geometry.Segment(
            momapy.geometry.Point(0.0, 0.0),
            momapy.geometry.Point(10.0, 0.0),
        )
        seg2 = momapy.geometry.Segment(
            momapy.geometry.Point(10.0, 0.0),
            momapy.geometry.Point(20.0, 0.0),
        )
        return _ConcreteArc(segments=(seg1, seg2))

    @pytest.fixture
    def two_unequal_segments_arc(self):
        # Segments of length 6 and 4: (0,0)→(6,0)→(10,0)
        seg1 = momapy.geometry.Segment(
            momapy.geometry.Point(0.0, 0.0),
            momapy.geometry.Point(6.0, 0.0),
        )
        seg2 = momapy.geometry.Segment(
            momapy.geometry.Point(6.0, 0.0),
            momapy.geometry.Point(10.0, 0.0),
        )
        return _ConcreteArc(segments=(seg1, seg2))

    # --- single-segment baseline ---

    def test_single_segment_start(self):
        seg = momapy.geometry.Segment(
            momapy.geometry.Point(0.0, 0.0),
            momapy.geometry.Point(10.0, 0.0),
        )
        arc = _ConcreteArc(segments=(seg,))
        position, _ = arc.fraction(0.0)
        assert position.x == pytest.approx(0.0, abs=0.01)
        assert position.y == pytest.approx(0.0, abs=0.01)

    def test_single_segment_end(self):
        seg = momapy.geometry.Segment(
            momapy.geometry.Point(0.0, 0.0),
            momapy.geometry.Point(10.0, 0.0),
        )
        arc = _ConcreteArc(segments=(seg,))
        position, _ = arc.fraction(1.0)
        assert position.x == pytest.approx(10.0, abs=0.01)
        assert position.y == pytest.approx(0.0, abs=0.01)

    def test_single_segment_midpoint(self):
        seg = momapy.geometry.Segment(
            momapy.geometry.Point(0.0, 0.0),
            momapy.geometry.Point(10.0, 0.0),
        )
        arc = _ConcreteArc(segments=(seg,))
        position, _ = arc.fraction(0.5)
        assert position.x == pytest.approx(5.0, abs=0.01)
        assert position.y == pytest.approx(0.0, abs=0.01)

    # --- two equal-length segments ---

    def test_two_equal_segments_start(self, two_equal_segments_arc):
        position, _ = two_equal_segments_arc.fraction(0.0)
        assert position.x == pytest.approx(0.0, abs=0.01)

    def test_two_equal_segments_end(self, two_equal_segments_arc):
        position, _ = two_equal_segments_arc.fraction(1.0)
        assert position.x == pytest.approx(20.0, abs=0.01)

    def test_two_equal_segments_junction(self, two_equal_segments_arc):
        # fraction 0.5 lands exactly at the junction (10, 0)
        position, _ = two_equal_segments_arc.fraction(0.5)
        assert position.x == pytest.approx(10.0, abs=0.01)

    def test_two_equal_segments_three_quarters(self, two_equal_segments_arc):
        # fraction 0.75 → 15 units along → midpoint of second segment
        # Before the Arc.fraction fix this returned x=17.5 (wrong).
        position, _ = two_equal_segments_arc.fraction(0.75)
        assert position.x == pytest.approx(15.0, abs=0.01)
        assert position.y == pytest.approx(0.0, abs=0.01)

    def test_two_equal_segments_first_quarter(self, two_equal_segments_arc):
        # fraction 0.25 → 5 units along → midpoint of first segment
        position, _ = two_equal_segments_arc.fraction(0.25)
        assert position.x == pytest.approx(5.0, abs=0.01)

    # --- two unequal segments ---

    def test_two_unequal_segments_in_first(self, two_unequal_segments_arc):
        # fraction 0.5 → 5 units along → in segment 1 (length 6) at 5/6
        position, _ = two_unequal_segments_arc.fraction(0.5)
        assert position.x == pytest.approx(5.0, abs=0.01)

    def test_two_unequal_segments_in_second(self, two_unequal_segments_arc):
        # fraction 0.7 → 7 units along → 1 unit into segment 2 (length 4)
        # → segment_fraction = 1/4, x = 6 + 1 = 7
        position, _ = two_unequal_segments_arc.fraction(0.7)
        assert position.x == pytest.approx(7.0, abs=0.01)


class TestArcPoints:
    """Tests for Arc.points() on empty and non-empty arcs."""

    def test_empty_arc_returns_no_points(self):
        # Regression: a segment-less arc previously raised UnboundLocalError.
        arc = _ConcreteArc(segments=())
        assert arc.points() == []

    def test_empty_arc_start_point_raises_index_error(self):
        arc = _ConcreteArc(segments=())
        with pytest.raises(IndexError):
            arc.start_point()


class TestArcPathAction:
    """Tests for Arc._make_path_action_from_segment."""

    def test_elliptical_arc_segment_reads_sweep_flag(self):
        # Regression: an elliptical-arc segment must not raise AttributeError
        # (the builder previously read the misspelled ``segment.seep_flag``).
        segment = momapy.geometry.EllipticalArc(
            momapy.geometry.Point(0.0, 0.0),
            momapy.geometry.Point(10.0, 0.0),
            5.0,
            5.0,
            0.0,
            0,
            1,
        )
        path_action = momapy.core.layout.Arc._make_path_action_from_segment(segment)
        assert path_action.sweep_flag == 1


class TestGroupLayoutOwnBbox:
    """Tests for GroupLayout.own_bbox / own_to_geometry (self-only geometry)."""

    def test_own_bbox_excludes_children(self):
        # Regression: own_bbox/own_to_geometry must reflect only the group's own
        # drawing elements, not the whole subtree (they previously called
        # drawing_elements(), pulling in distant children).
        import momapy.meta.nodes

        child = momapy.meta.nodes.Rectangle(
            position=momapy.geometry.Point(1000, 1000),
            width=20,
            height=20,
        )
        parent = momapy.meta.nodes.Rectangle(
            position=momapy.geometry.Point(0, 0),
            width=20,
            height=20,
            layout_elements=(child,),
        )
        own_bbox = parent.own_bbox()
        assert own_bbox.width == pytest.approx(20.0)
        assert own_bbox.height == pytest.approx(20.0)
        # The full bbox still spans the distant child.
        full_bbox = parent.bbox()
        assert full_bbox.width == pytest.approx(1020.0)
        assert full_bbox.height == pytest.approx(1020.0)
