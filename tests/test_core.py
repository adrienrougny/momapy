"""Tests for momapy.core module."""
import dataclasses
import math
import pytest
import momapy.core
import momapy.geometry
import momapy.coloring


# Minimal concrete Arc subclass for testing Arc.fraction()
@dataclasses.dataclass(frozen=True, kw_only=True)
class _ConcreteArc(momapy.core.Arc):
    def self_drawing_elements(self):
        return []

    def _arrowhead_border_drawing_elements(self):
        return []


def test_direction_enum():
    """Test Direction enum."""
    assert momapy.core.Direction.HORIZONTAL is not None
    assert momapy.core.Direction.VERTICAL is not None
    assert momapy.core.Direction.UP is not None
    assert momapy.core.Direction.RIGHT is not None
    assert momapy.core.Direction.DOWN is not None
    assert momapy.core.Direction.LEFT is not None


def test_halignment_enum():
    """Test HAlignment enum."""
    assert momapy.core.HAlignment.LEFT is not None
    assert momapy.core.HAlignment.CENTER is not None
    assert momapy.core.HAlignment.RIGHT is not None


def test_valignment_enum():
    """Test VAlignment enum."""
    assert momapy.core.VAlignment.TOP is not None
    assert momapy.core.VAlignment.CENTER is not None
    assert momapy.core.VAlignment.BOTTOM is not None


def test_map_element_creation():
    """Test MapElement creation."""
    element = momapy.core.MapElement()
    assert element.id_ is not None
    assert isinstance(element.id_, str)


def test_map_element_with_custom_id():
    """Test MapElement with custom id."""
    element = momapy.core.MapElement(id_="custom_id")
    assert element.id_ == "custom_id"


def test_model_element_creation():
    """Test ModelElement creation."""
    element = momapy.core.ModelElement()
    assert element.id_ is not None
    assert isinstance(element.id_, str)


def test_text_layout_creation(sample_point):
    """Test TextLayout creation."""
    text_layout = momapy.core.TextLayout(
        text="Hello World",
        position=sample_point,
    )
    assert text_layout.text == "Hello World"
    assert text_layout.position == sample_point
    assert text_layout.horizontal_alignment == momapy.core.HAlignment.LEFT
    assert text_layout.vertical_alignment == momapy.core.VAlignment.TOP


def test_text_layout_with_custom_alignment(sample_point):
    """Test TextLayout with custom alignment."""
    text_layout = momapy.core.TextLayout(
        text="Test",
        position=sample_point,
        horizontal_alignment=momapy.core.HAlignment.CENTER,
        vertical_alignment=momapy.core.VAlignment.CENTER,
    )
    assert text_layout.horizontal_alignment == momapy.core.HAlignment.CENTER
    assert text_layout.vertical_alignment == momapy.core.VAlignment.CENTER


def test_layout_creation(sample_point):
    """Test Layout creation."""
    layout = momapy.core.Layout(
        position=sample_point,
        width=100,
        height=100,
        layout_elements=[]
    )
    assert layout.position == sample_point
    assert layout.width == 100
    assert layout.height == 100


def test_layout_with_elements(sample_point):
    """Test Layout with elements."""
    text_layout = momapy.core.TextLayout(
        text="Test",
        position=sample_point,
    )
    layout = momapy.core.Layout(
        position=momapy.geometry.Point(0, 0),
        width=200,
        height=200,
        layout_elements=[text_layout]
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
