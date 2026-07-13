"""Rendering subpackage for exporting maps to various formats.

Provides functions and registries for rendering molecular maps to
images (SVG, PDF, PNG, JPEG, WebP, PS) using different backends
(Skia, Cairo, and native SVG).

Examples:
    ```python
    from momapy.rendering import get_renderer, list_renderers
    renderer = get_renderer("skia")
    list_renderers()
    ```
"""

from momapy.rendering.core import get_renderer as get_renderer
from momapy.rendering.core import list_renderers as list_renderers
from momapy.rendering.core import register_lazy_renderer as register_lazy_renderer
from momapy.rendering.core import register_renderer as register_renderer
from momapy.rendering.core import render_layout_element as render_layout_element
from momapy.rendering.core import render_layout_elements as render_layout_elements
from momapy.rendering.core import render_map as render_map
from momapy.rendering.core import render_maps as render_maps
from momapy.rendering.core import Renderer as Renderer
from momapy.rendering.core import renderer_registry as renderer_registry
from momapy.rendering.core import StatefulRenderer as StatefulRenderer
from momapy.rendering.core import SupportsFileOutput as SupportsFileOutput


__all__ = [
    "get_renderer",
    "list_renderers",
    "register_lazy_renderer",
    "register_renderer",
    "render_layout_element",
    "render_layout_elements",
    "render_map",
    "render_maps",
    "Renderer",
    "renderer_registry",
    "StatefulRenderer",
    "SupportsFileOutput",
]


for name, import_path in [
    ("svg-native", "momapy.rendering.svg_native:SVGNativeRenderer"),
    ("svg-native-compat", "momapy.rendering.svg_native:SVGNativeCompatRenderer"),
    ("skia", "momapy.rendering.skia:SkiaRenderer"),
    ("cairo", "momapy.rendering.cairo:CairoRenderer"),
]:
    register_lazy_renderer(name, import_path)

del name, import_path
