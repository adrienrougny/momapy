"""Tests for momapy.drawing module."""

import pytest
import momapy.drawing
import momapy.coloring


def test_none_value_singleton():
    """Test NoneValue singleton."""
    assert momapy.drawing.NoneValue is not None
    assert isinstance(momapy.drawing.NoneValue, momapy.drawing.NoneValueType)


def test_none_value_copy():
    """Test NoneValue copy operations."""
    import copy

    nv1 = momapy.drawing.NoneValue
    nv2 = copy.copy(nv1)
    nv3 = copy.deepcopy(nv1)

    assert nv1 is nv2
    assert nv1 is nv3


def test_none_value_equality():
    """Test NoneValue equality."""
    nv1 = momapy.drawing.NoneValue
    nv2 = momapy.drawing.NoneValue

    assert nv1 == nv2
    assert not (nv1 != nv2)


def test_drop_shadow_effect_creation():
    """Test creating a DropShadowEffect."""
    effect = momapy.drawing.DropShadowEffect(
        dx=5.0,
        dy=5.0,
        std_deviation=2.0,
        flood_opacity=0.5,
        flood_color=momapy.coloring.black,
    )

    assert effect.dx == 5.0
    assert effect.dy == 5.0
    assert effect.std_deviation == 2.0
    assert effect.flood_opacity == 0.5


def test_drop_shadow_effect_to_compat():
    """Test DropShadowEffect to_compat method."""
    effect = momapy.drawing.DropShadowEffect(
        dx=5.0,
        dy=5.0,
        std_deviation=2.0,
    )

    compat_effects = effect.to_compat()

    assert isinstance(compat_effects, list)
    assert len(compat_effects) > 0
    # Should return multiple effects
    assert all(isinstance(e, momapy.drawing.FilterEffect) for e in compat_effects)


def test_filter_effect_input_enum():
    """Test FilterEffectInput enum."""
    assert momapy.drawing.FilterEffectInput.SOURCE_GRAPHIC is not None
    assert momapy.drawing.FilterEffectInput.SOURCE_ALPHA is not None
    assert isinstance(
        momapy.drawing.FilterEffectInput.SOURCE_GRAPHIC,
        momapy.drawing.FilterEffectInput,
    )


def test_composition_operator_enum():
    """Test CompositionOperator enum."""
    assert momapy.drawing.CompositionOperator.OVER is not None
    assert momapy.drawing.CompositionOperator.IN is not None
    assert isinstance(
        momapy.drawing.CompositionOperator.OVER, momapy.drawing.CompositionOperator
    )


def test_composite_effect_creation():
    """Test creating a CompositeEffect."""
    effect = momapy.drawing.CompositeEffect(
        in_=momapy.drawing.FilterEffectInput.SOURCE_GRAPHIC,
        in2=momapy.drawing.FilterEffectInput.SOURCE_ALPHA,
        operator=momapy.drawing.CompositionOperator.IN,
    )

    assert effect.in_ == momapy.drawing.FilterEffectInput.SOURCE_GRAPHIC
    assert effect.in2 == momapy.drawing.FilterEffectInput.SOURCE_ALPHA
    assert effect.operator == momapy.drawing.CompositionOperator.IN


class TestPath:
    """Tests for Path class."""

    def test_path_creation_with_move_to_line_to(self):
        """Test creating a Path with MoveTo and LineTo."""
        path = momapy.drawing.Path(
            actions=(
                momapy.drawing.MoveTo(momapy.geometry.Point(0, 0)),
                momapy.drawing.LineTo(momapy.geometry.Point(10, 10)),
            )
        )
        assert len(path.actions) == 2
        assert isinstance(path.actions[0], momapy.drawing.MoveTo)
        assert isinstance(path.actions[1], momapy.drawing.LineTo)

    def test_path_to_shapely_produces_geometry(self):
        """Test that Path.to_shapely() produces valid geometry."""
        path = momapy.drawing.Path(
            actions=(
                momapy.drawing.MoveTo(momapy.geometry.Point(0, 0)),
                momapy.drawing.LineTo(momapy.geometry.Point(10, 0)),
                momapy.drawing.LineTo(momapy.geometry.Point(10, 10)),
                momapy.drawing.LineTo(momapy.geometry.Point(0, 10)),
                momapy.drawing.ClosePath(),
            )
        )
        shapely_geom = path.to_shapely()
        assert shapely_geom is not None
        assert not shapely_geom.is_empty

    def test_path_transformed_with_translation(self):
        """Test Path.transformed() shifts coordinates correctly."""
        path = momapy.drawing.Path(
            actions=(
                momapy.drawing.MoveTo(momapy.geometry.Point(0, 0)),
                momapy.drawing.LineTo(momapy.geometry.Point(10, 10)),
            )
        )
        translation = momapy.geometry.Translation(5, 10)
        transformed = path.transformed(translation)

        # Check that the move_to point was translated
        assert transformed.actions[0].point.x == 5.0
        assert transformed.actions[0].point.y == 10.0
        # Check that the line_to point was translated
        assert transformed.actions[1].point.x == 15.0
        assert transformed.actions[1].point.y == 20.0

    def test_path_bbox(self):
        """Test Path.bbox() returns reasonable bounds."""
        path = momapy.drawing.Path(
            actions=(
                momapy.drawing.MoveTo(momapy.geometry.Point(0, 0)),
                momapy.drawing.LineTo(momapy.geometry.Point(10, 10)),
            )
        )
        bbox = path.bbox()
        assert isinstance(bbox, momapy.geometry.Bbox)
        assert bbox.width > 0
        assert bbox.height > 0


class TestPathActions:
    """Tests for PathAction classes."""

    def test_move_to_creation(self):
        """Test creating a MoveTo action."""
        move = momapy.drawing.MoveTo(momapy.geometry.Point(5, 10))
        assert move.point.x == 5.0
        assert move.point.y == 10.0

    def test_line_to_creation(self):
        """Test creating a LineTo action."""
        line = momapy.drawing.LineTo(momapy.geometry.Point(15, 20))
        assert line.point.x == 15.0
        assert line.point.y == 20.0

    def test_line_to_to_shapely(self):
        """Test LineTo.to_shapely() produces LineString."""
        line = momapy.drawing.LineTo(momapy.geometry.Point(10, 10))
        current_point = momapy.geometry.Point(0, 0)
        shapely_line = line.to_shapely(current_point)
        assert shapely_line is not None

    def test_close_path_creation(self):
        """Test creating a ClosePath action."""
        close = momapy.drawing.ClosePath()
        assert isinstance(close, momapy.drawing.ClosePath)


class TestRectangle:
    """Tests for Rectangle drawing element."""

    def test_rectangle_creation(self):
        """Test creating a Rectangle."""
        rect = momapy.drawing.Rectangle(
            point=momapy.geometry.Point(0, 0),
            width=10,
            height=5,
            rx=0,
            ry=0,
        )
        assert rect.width == 10
        assert rect.height == 5

    def test_rectangle_to_path(self):
        """Test Rectangle.to_path() produces valid Path."""
        rect = momapy.drawing.Rectangle(
            point=momapy.geometry.Point(0, 0),
            width=10,
            height=5,
            rx=0,
            ry=0,
        )
        path = rect.to_path()
        assert isinstance(path, momapy.drawing.Path)
        assert len(path.actions) > 0

    def test_rectangle_to_shapely(self):
        """Test Rectangle.to_shapely() produces valid geometry."""
        rect = momapy.drawing.Rectangle(
            point=momapy.geometry.Point(0, 0),
            width=10,
            height=5,
            rx=0,
            ry=0,
        )
        shapely_geom = rect.to_shapely()
        assert shapely_geom is not None


class TestEllipse:
    """Tests for Ellipse drawing element."""

    def test_ellipse_creation(self):
        """Test creating an Ellipse."""
        ellipse = momapy.drawing.Ellipse(
            point=momapy.geometry.Point(5, 5),
            rx=10,
            ry=5,
        )
        assert ellipse.rx == 10
        assert ellipse.ry == 5

    def test_ellipse_to_path(self):
        """Test Ellipse.to_path() produces valid Path."""
        ellipse = momapy.drawing.Ellipse(
            point=momapy.geometry.Point(5, 5),
            rx=10,
            ry=5,
        )
        path = ellipse.to_path()
        assert isinstance(path, momapy.drawing.Path)
        assert len(path.actions) > 0


class TestText:
    """Tests for Text drawing element."""

    def test_text_creation(self):
        """Test creating a Text element."""
        text = momapy.drawing.Text(
            text="Hello World",
            point=momapy.geometry.Point(10, 20),
        )
        assert text.text == "Hello World"
        assert text.point.x == 10.0
        assert text.point.y == 20.0

    def test_text_with_font_properties(self):
        """Test Text with font properties."""
        text = momapy.drawing.Text(
            text="Test",
            point=momapy.geometry.Point(10, 20),
            font_size=14.0,
            font_family="Arial",
        )
        assert text.font_size == 14.0
        assert text.font_family == "Arial"

    def test_text_to_shapely(self):
        """Test Text.to_shapely() produces geometry."""
        text = momapy.drawing.Text(
            text="Test",
            point=momapy.geometry.Point(10, 20),
        )
        shapely_geom = text.to_shapely()
        assert shapely_geom is not None


class TestGroup:
    """Tests for Group drawing element."""

    def test_group_creation(self):
        """Test creating a Group."""
        rect = momapy.drawing.Rectangle(
            point=momapy.geometry.Point(0, 0),
            width=10,
            height=5,
            rx=0,
            ry=0,
        )
        group = momapy.drawing.Group(elements=(rect,))
        assert len(group.elements) == 1

    def test_group_to_shapely_aggregates_children(self):
        """Test Group.to_shapely() aggregates children."""
        rect = momapy.drawing.Rectangle(
            point=momapy.geometry.Point(0, 0),
            width=10,
            height=5,
            rx=0,
            ry=0,
        )
        ellipse = momapy.drawing.Ellipse(
            point=momapy.geometry.Point(20, 20),
            rx=5,
            ry=3,
        )
        group = momapy.drawing.Group(elements=(rect, ellipse))
        shapely_geom = group.to_shapely()
        assert shapely_geom is not None
        # GeometryCollection should contain both shapes
        assert len(shapely_geom.geoms) >= 2
