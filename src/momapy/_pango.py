import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo  # must import like that to use

import momapy.drawing

_cairo_context = None
_pango_font_descriptions = {}
_style_to_pango_style_mapping = {
    momapy.drawing.FontStyle.NORMAL: Pango.Style.NORMAL,
    momapy.drawing.FontStyle.ITALIC: Pango.Style.ITALIC,
    momapy.drawing.FontStyle.OBLIQUE: Pango.Style.OBLIQUE,
}


def make_pango_layout(
    font_family: str,
    font_size: float,
    font_style: momapy.drawing.FontStyle,
    font_weight: momapy.drawing.FontWeight | int,
):
    if isinstance(font_weight, momapy.drawing.FontWeight):
        font_weight = momapy.drawing.FONT_WEIGHT_VALUE_MAPPING.get(font_weight)
        if font_weight is None:
            raise ValueError(
                f"font weight must be a float, {momapy.drawing.FontWeight.NORMAL}, or {momapy.drawing.FontWeight.BOLD}"
            )
    if _cairo_context is None:
        cairo_surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)
        cairo_context = cairo.Context(cairo_surface)
    else:
        cairo_context = _cairo_context
    pango_layout = PangoCairo.create_layout(cairo_context)
    pango_font_description = _pango_font_descriptions.get(
        (font_family, font_size, font_style, font_weight)
    )
    if pango_font_description is None:
        pango_font_description = Pango.FontDescription()
        pango_font_description.set_family(font_family)
        pango_font_description.set_absolute_size(
            Pango.units_from_double(font_size)
        )
        pango_font_description.set_style(
            _style_to_pango_style_mapping[font_style]
        )
        pango_font_description.set_weight(font_weight)
        _pango_font_descriptions[
            (font_family, font_size, font_style, font_weight)
        ] = pango_font_description
    pango_layout.set_font_description(pango_font_description)
    return pango_layout
