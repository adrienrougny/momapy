import momapy.drawing
import momapy.geometry
import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
import gi.repository.Pango
import gi.repository.PangoCairo  # must import like that to use

_cairo_context = None
_pango_font_descriptions = {}
_style_to_pango_style_mapping = {
    momapy.drawing.FontStyle.NORMAL: gi.repository.Pango.Style.NORMAL,
    momapy.drawing.FontStyle.ITALIC: gi.repository.Pango.Style.ITALIC,
    momapy.drawing.FontStyle.OBLIQUE: gi.repository.Pango.Style.OBLIQUE,
}


def make_pango_layout(
    font_family: str,
    font_size: float,
    font_style: momapy.drawing.FontStyle,
    font_weight: momapy.drawing.FontWeight | int,
    text: str,
    justify: bool,
    width: float | None = None,
    height: float | None = None,
) -> gi.repository.Pango.Layout:
    if isinstance(font_weight, momapy.drawing.FontWeight):
        font_weight = momapy.drawing.FONT_WEIGHT_TO_VALUE[font_weight]
    if _cairo_context is None:
        cairo_surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)
        cairo_context = cairo.Context(cairo_surface)
    else:
        cairo_context = _cairo_context
    pango_layout = gi.repository.PangoCairo.create_layout(cairo_context)
    pango_font_description = _pango_font_descriptions.get(
        (font_family, font_size, font_style, font_weight)
    )
    if pango_font_description is None:
        pango_font_description = gi.repository.Pango.FontDescription()
        pango_font_description.set_family(font_family)
        pango_font_description.set_absolute_size(
            gi.repository.Pango.units_from_double(font_size)
        )
        pango_font_description.set_style(_style_to_pango_style_mapping[font_style])
        pango_font_description.set_weight(font_weight)
        _pango_font_descriptions[(font_family, font_size, font_style, font_weight)] = (
            pango_font_description
        )
    pango_layout.set_font_description(pango_font_description)
    if width is not None:
        pango_layout.set_width(gi.repository.Pango.units_from_double(width))
    if height is not None:
        pango_layout.set_height(gi.repository.Pango.units_from_double(height))
    pango_layout.set_text(text)
    pango_layout.set_justify(justify)
    return pango_layout


def get_pango_line_text_and_initial_pos(pango_layout, pango_layout_iter, pango_line):
    start_index = pango_line.get_start_index()
    end_index = start_index + pango_line.get_length()
    pos = pango_layout.index_to_pos(start_index)
    x = round(pos.x / gi.repository.Pango.SCALE)
    y = round(gi.repository.Pango.units_to_double(pango_layout_iter.get_baseline()))
    line_text = pango_layout.get_text()[start_index:end_index]
    return line_text, momapy.geometry.Point(x, y)
