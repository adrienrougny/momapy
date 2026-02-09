"""Tests for the plugin system."""

import pytest

import momapy.plugins.registry


class TestPluginRegistry:
    """Tests for PluginRegistry class."""

    def test_get_returns_none_for_nonexistent_plugin(self):
        """Test that get() returns None when plugin is not found."""
        registry = momapy.plugins.registry.PluginRegistry()
        result = registry.get("nonexistent")
        assert result is None

    def test_is_available_returns_false_for_nonexistent_plugin(self):
        """Test that is_available() returns False when plugin is not found."""
        registry = momapy.plugins.registry.PluginRegistry()
        result = registry.is_available("nonexistent")
        assert result is False

    def test_register_and_get_plugin(self):
        """Test that we can register and retrieve a plugin."""
        registry = momapy.plugins.registry.PluginRegistry()

        class TestPlugin:
            pass

        registry.register("test", TestPlugin)
        result = registry.get("test")

        assert result is TestPlugin

    def test_is_available_returns_true_for_registered_plugin(self):
        """Test that is_available() returns True for registered plugin."""
        registry = momapy.plugins.registry.PluginRegistry()

        class TestPlugin:
            pass

        registry.register("test", TestPlugin)
        result = registry.is_available("test")

        assert result is True

    def test_list_available_returns_registered_plugins(self):
        """Test that list_available() returns all registered plugin names."""
        registry = momapy.plugins.registry.PluginRegistry()

        class TestPlugin1:
            pass

        class TestPlugin2:
            pass

        registry.register("plugin1", TestPlugin1)
        registry.register("plugin2", TestPlugin2)

        result = registry.list_available()

        assert result == ["plugin1", "plugin2"]

    def test_list_loaded_returns_loaded_plugins(self):
        """Test that list_loaded() returns only loaded plugin names."""
        registry = momapy.plugins.registry.PluginRegistry()

        class TestPlugin:
            pass

        registry.register("test", TestPlugin)
        result = registry.list_loaded()

        assert result == ["test"]


class TestIOPluginGetters:
    """Tests for IO plugin getter functions."""

    def test_get_reader_returns_reader_for_valid_name(self):
        """Test that get_reader() returns a reader class for valid name."""
        import momapy.io

        reader = momapy.io.get_reader("sbgnml")
        assert reader is not None

    def test_get_reader_raises_for_invalid_name(self):
        """Test that get_reader() raises ValueError for invalid name."""
        import momapy.io

        with pytest.raises(ValueError, match="No reader named 'nonexistent'"):
            momapy.io.get_reader("nonexistent")

    def test_get_writer_returns_writer_for_valid_name(self):
        """Test that get_writer() returns a writer class for valid name."""
        import momapy.io

        writer = momapy.io.get_writer("sbgnml")
        assert writer is not None

    def test_get_writer_raises_for_invalid_name(self):
        """Test that get_writer() raises ValueError for invalid name."""
        import momapy.io

        with pytest.raises(ValueError, match="No writer named 'nonexistent'"):
            momapy.io.get_writer("nonexistent")


class TestRenderingPluginGetters:
    """Tests for rendering plugin getter functions."""

    def test_get_svg_native_renderer(self):
        """Test that get_renderer() returns svg-native renderer."""
        import momapy.rendering

        renderer = momapy.rendering.get_renderer("svg-native")
        assert renderer is not None

    def test_get_skia_renderer(self):
        """Test that get_renderer() returns skia renderer."""
        import momapy.rendering

        if not momapy.rendering.renderer_registry.is_available("skia"):
            pytest.skip("skia-python not installed")

        try:
            renderer = momapy.rendering.get_renderer("skia")
            assert renderer is not None
        except (ImportError, ModuleNotFoundError):
            pytest.skip("skia-python not installed")

    def test_get_cairo_renderer(self):
        """Test that get_renderer() returns cairo renderer."""
        import momapy.rendering

        if not momapy.rendering.renderer_registry.is_available("cairo"):
            pytest.skip("pycairo not installed")

        try:
            renderer = momapy.rendering.get_renderer("cairo")
            assert renderer is not None
        except (ImportError, ModuleNotFoundError):
            pytest.skip("pycairo not installed")

    def test_get_renderer_raises_for_invalid_name(self):
        """Test that get_renderer() raises ValueError for invalid name."""
        import momapy.rendering

        with pytest.raises(ValueError, match="No renderer named 'nonexistent'"):
            momapy.rendering.get_renderer("nonexistent")
