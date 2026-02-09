"""Subpackage for rendering."""

from __future__ import annotations

import typing

import momapy.plugins.registry

if typing.TYPE_CHECKING:
    import momapy.rendering.core


_renderer_registry = momapy.plugins.registry.PluginRegistry(
    entry_point_group="momapy.renderers",
)


def get_renderer(name: str) -> type[momapy.rendering.core.Renderer]:
    """Get a renderer class by name"""
    renderer = _renderer_registry.get(name)
    if renderer is None:
        available = _renderer_registry.list_available()
        raise ValueError(
            f"No renderer named '{name}'. Available renderers: {', '.join(available)}"
        )
    return renderer


def list_renderers() -> list[str]:
    """List all available renderer names"""
    return _renderer_registry.list_available()


def register_renderer(name: str, cls: type[momapy.rendering.core.Renderer]) -> None:
    """Register a renderer class"""
    _renderer_registry.register(name, cls)


def register_lazy_renderer(name: str, import_path: str) -> None:
    """Register a renderer class"""
    _renderer_registry.register_lazy(name, import_path)


for name, import_path in [
    ("svg-native", "momapy.rendering.svg_native:SVGNativeRenderer"),
    ("svg-native-compat", "momapy.rendering.svg_native:SVGNativeCompatRenderer"),
    ("skia", "momapy.rendering.skia:SkiaRenderer"),
    ("cairo", "momapy.rendering.cairo:CairoRenderer"),
]:
    register_lazy_renderer(name, import_path)
