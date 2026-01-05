"""Tests for momapy.core module."""
import pytest
import momapy.core
import momapy.geometry
import momapy.coloring


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
