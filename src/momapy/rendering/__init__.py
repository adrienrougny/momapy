"""Rendering subpackage for exporting maps to various formats.

Provides functions and registries for rendering molecular maps to
images (PNG, PDF, SVG) using different backends (Skia, Cairo, SVG).

Example:
    >>> from momapy.rendering import get_renderer, list_renderers
    >>> renderer = get_renderer("skia")
    >>> list_renderers()
    ['cairo', 'skia', 'svg-native']
"""

from __future__ import annotations

import typing

import momapy.plugins.registry

if typing.TYPE_CHECKING:
    import momapy.rendering.core


renderer_registry = momapy.plugins.registry.PluginRegistry(
    entry_point_group="momapy.renderers",
)


def get_renderer(name: str) -> type[momapy.rendering.core.Renderer]:
    """Get a renderer class by name.

    Args:
        name: Renderer name (e.g., "skia", "cairo", "svg-native").

    Returns:
        Renderer class for the specified backend.

    Raises:
        ValueError: If no renderer with that name exists.

    Example:
        >>> from momapy.rendering import get_renderer
        >>> renderer = get_renderer("skia")
    """
    renderer = renderer_registry.get(name)
    if renderer is None:
        available = renderer_registry.list_available()
        raise ValueError(
            f"No renderer named '{name}'. Available renderers: {', '.join(available)}"
        )
    return renderer


def list_renderers() -> list[str]:
    """List all available renderer names.

    Returns:
        Sorted list of available renderer names.

    Example:
        >>> from momapy.rendering import list_renderers
        >>> list_renderers()
        ['cairo', 'skia', 'svg-native']
    """
    return renderer_registry.list_available()


def register_renderer(name: str, cls: type[momapy.rendering.core.Renderer]) -> None:
    """Register a renderer class.

    Args:
        name: Name to register the renderer under.
        cls: Renderer class (must inherit from Renderer).

    Example:
        >>> from momapy.rendering import register_renderer
        >>> register_renderer("myrenderer", MyRenderer)
    """
    renderer_registry.register(name, cls)


def register_lazy_renderer(name: str, import_path: str) -> None:
    """Register a renderer for lazy loading.

    Args:
        name: Name to register the renderer under.
        import_path: Import path in format "module.path:ClassName".

    Example:
        >>> from momapy.rendering import register_lazy_renderer
        >>> register_lazy_renderer("myrenderer", "mymodule.rendering:MyRenderer")
    """
    renderer_registry.register_lazy(name, import_path)


for name, import_path in [
    ("svg-native", "momapy.rendering.svg_native:SVGNativeRenderer"),
    ("svg-native-compat", "momapy.rendering.svg_native:SVGNativeCompatRenderer"),
    ("skia", "momapy.rendering.skia:SkiaRenderer"),
    ("cairo", "momapy.rendering.cairo:CairoRenderer"),
]:
    register_lazy_renderer(name, import_path)
