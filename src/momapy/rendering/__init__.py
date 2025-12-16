"""Subpackage for rendering"""

_registered = False


def _ensure_registered():
    global _registered
    if not _registered:
        import momapy.rendering.core
        import momapy.rendering.svg_native

        momapy.rendering.core.register_renderer(
            "svg-native", momapy.rendering.svg_native.SVGNativeRenderer
        )
        momapy.rendering.core.register_renderer(
            "svg-native-compat", momapy.rendering.svg_native.SVGNativeCompatRenderer
        )
