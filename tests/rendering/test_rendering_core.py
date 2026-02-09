"""Tests for momapy.rendering.core module."""

import momapy.rendering
import momapy.rendering.core


def test_renderer_registry_exists():
    """Test that renderer registry exists."""
    assert hasattr(momapy.rendering, "renderer_registry")


def test_register_renderer():
    """Test register_renderer function."""

    class DummyRenderer(momapy.rendering.core.Renderer):
        pass

    # Save original state
    original_renderers = momapy.rendering.renderer_registry.list_loaded()

    try:
        momapy.rendering.register_renderer("test_renderer", DummyRenderer)
        assert momapy.rendering.renderer_registry.is_available("test_renderer")
        assert momapy.rendering.renderer_registry.get("test_renderer") == DummyRenderer
    finally:
        # Restore original state - remove test renderer
        if "test_renderer" in momapy.rendering.renderer_registry.list_loaded():
            del momapy.rendering.renderer_registry._loaded_plugins["test_renderer"]


def test_render_layout_element_exists():
    """Test that render_layout_element function exists."""
    assert hasattr(momapy.rendering.core, "render_layout_element")
    assert callable(momapy.rendering.core.render_layout_element)


def test_render_layout_elements_exists():
    """Test that render_layout_elements function exists."""
    assert hasattr(momapy.rendering.core, "render_layout_elements")
    assert callable(momapy.rendering.core.render_layout_elements)
