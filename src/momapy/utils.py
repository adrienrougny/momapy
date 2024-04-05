import frozendict
import collections.abc
import dataclasses

import colorama
import numpy

import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo  # must import like that to use

import momapy.drawing


def pretty_print(obj, max_depth=0, exclude_cls=None, _depth=0, _indent=0):
    def _print_with_indent(s, indent):
        print(f"{'  '*indent}{s}")

    def _get_value_string(attr_value, max_len=30):
        s = str(attr_value)
        if len(s) > max_len:
            s = f"{s[:max_len]}..."
        return s

    if _depth > max_depth:
        return
    if exclude_cls is None:
        exclude_cls = []
    obj_typing = type(obj)
    if obj_typing in exclude_cls:
        return
    obj_value_string = _get_value_string(obj)
    obj_string = f"{colorama.Fore.GREEN}{obj_typing}{colorama.Fore.RED}: {obj_value_string}{colorama.Style.RESET_ALL}"
    _print_with_indent(obj_string, _indent)
    if dataclasses.is_dataclass(type(obj)):
        for field in dataclasses.fields(obj):
            attr_name = field.name
            if not attr_name.startswith("_"):
                attr_value = getattr(obj, attr_name)
                attr_typing = field.type
                attr_value_string = _get_value_string(attr_value)
                attr_string = f"{colorama.Fore.BLUE}* {attr_name}{colorama.Fore.MAGENTA}: {attr_typing} = {colorama.Fore.RED}{attr_value_string}{colorama.Style.RESET_ALL}"
                _print_with_indent(attr_string, _indent + 1)
                pretty_print(
                    attr_value,
                    max_depth=max_depth,
                    exclude_cls=exclude_cls,
                    _depth=_depth + 1,
                    _indent=_indent + 2,
                )
    if isinstance(obj, collections.abc.Iterable) and not isinstance(
        obj, (str, bytes, bytearray)
    ):
        for i, elem_value in enumerate(obj):
            elem_typing = type(elem_value)
            elem_value_string = _get_value_string(elem_value)
            elem_string = f"{colorama.Fore.BLUE}- {i}{colorama.Fore.MAGENTA}: {elem_typing} = {colorama.Fore.RED}{elem_value_string}{colorama.Style.RESET_ALL}"
            _print_with_indent(elem_string, _indent + 1)
            pretty_print(
                elem_value,
                max_depth=max_depth,
                exclude_cls=exclude_cls,
                _depth=_depth + 1,
                _indent=_indent + 2,
            )


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


def make_node(cls, position):
    if isinstance(position, tuple):
        position = momapy.geometry.Point.from_tuple(position)
    if not issubclass(cls, momapy.builder.Builder):
        builder_cls = momapy.builder.get_or_make_builder_cls(cls)
    node = builder_cls(position=position)
    return node


def make_arc(cls, points):
    segments = []
    new_points = []
    for point in points:
        if isinstance(point, tuple):
            point = momapy.geometry.Point.from_tuple(point)
        new_points.append(point)
    for start_point, end_point in zip(new_points, new_points[1:]):
        segment = momapy.geometry.Segment(start_point, end_point)
        segments.append(segment)
    if not issubclass(cls, momapy.builder.Builder):
        builder_cls = momapy.builder.get_or_make_builder_cls(cls)
    arc = builder_cls(segments=segments)
    return arc


def get_element_from_collection(element, collection):
    for e in collection:
        if e == element:
            return e
    return None


def get_or_return_element_from_collection(element, collection):
    existing_element = get_element_from_collection(element, collection)
    if existing_element is not None:
        return existing_element
    return element
