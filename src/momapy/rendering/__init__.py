"""Subpackage for rendering"""

import momapy.rendering.core
import momapy.rendering.svg_native

momapy.rendering.core.register_renderer(
    "svg-native", momapy.rendering.svg_native.SVGNativeRenderer
)
momapy.rendering.core.register_renderer(
    "svg-native-compat", momapy.rendering.svg_native.SVGNativeCompatRenderer
)
