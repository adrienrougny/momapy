#!/bin/python

import sys
import importlib
import dataclasses

import momapy.core
import momapy.coloring

NODE_ATTR_NAMES = [
    "border_fill",
    "border_filter",
    "border_stroke",
    "border_stroke_dasharray",
    "border_stroke_dashoffset",
    "border_stroke_width",
    "border_transform",
    "cut_corners",
    "fill",
    "filter",
    "height",
    "left_connector_fill",
    "left_connector_filter",
    "left_connector_length",
    "left_connector_stroke",
    "left_connector_stroke_dasharray",
    "left_connector_stroke_dashoffset",
    "left_connector_stroke_width",
    "offset",
    "right_connector_fill",
    "right_connector_filter",
    "right_connector_length",
    "right_connector_stroke",
    "right_connector_stroke_dasharray",
    "right_connector_stroke_dashoffset",
    "right_connector_stroke_width",
    "rounded_corners",
    "stroke",
    "stroke_dasharray",
    "stroke_dashoffset",
    "stroke_width",
    "subunits_fill",
    "subunits_filter",
    "subunits_stroke",
    "subunits_stroke_dasharray",
    "subunits_stroke_dashoffset",
    "subunits_stroke_width",
    "subunits_transform",
    "transform",
    "width",
]

module = importlib.import_module(sys.argv[1])


def color_to_name(color):
    for color_name, color_def in momapy.coloring.list_colors():
        if color == color_def:
            return color_name
    return None


def transform_attr_default_value(value):
    if isinstance(value, momapy.coloring.Color):
        value = color_to_name(value)
    elif value == momapy.drawing.NoneValue:
        value = "none"
    elif value is None:
        return "unset"
    return value


l = []
for cls_name in dir(module):
    cls = getattr(module, cls_name)
    if (
        not cls_name.startswith("_")
        and isinstance(cls, type)
        and issubclass(cls, momapy.core.Node)
    ):
        l.append(f"{cls_name} {{")
        fields = dataclasses.fields(cls)
        for attr_name in NODE_ATTR_NAMES:
            for field in fields:
                if field.name == attr_name:
                    attr_default_value = field.default
                    if attr_default_value != dataclasses.MISSING:
                        attr_default_value = transform_attr_default_value(
                            attr_default_value
                        )
                        l.append(f"\t{attr_name}: {str(attr_default_value)};")
                    break
        l.append("}")
        l.append("\n")
if l:
    l.pop()
print("\n".join(l))
