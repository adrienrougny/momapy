"""Tests for momapy.rendering.core module."""
import momapy.rendering.core


def test_renderers_dict_exists():
    """Test that renderers dictionary exists."""
    assert isinstance(momapy.rendering.core.renderers, dict)


def test_register_renderer():
    """Test register_renderer function."""
    class DummyRenderer:
        pass

    momapy.rendering.core.register_renderer("test_renderer", DummyRenderer)
    assert "test_renderer" in momapy.rendering.core.renderers
    assert momapy.rendering.core.renderers["test_renderer"] == DummyRenderer


def test_render_layout_element_exists():
    """Test that render_layout_element function exists."""
    assert hasattr(momapy.rendering.core, 'render_layout_element')
    assert callable(momapy.rendering.core.render_layout_element)


def test_render_layout_elements_exists():
    """Test that render_layout_elements function exists."""
    assert hasattr(momapy.rendering.core, 'render_layout_elements')
    assert callable(momapy.rendering.core.render_layout_elements)
