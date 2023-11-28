#!/bin/python

import argparse
import collections
import dataclasses
import importlib
import typing

import momapy.coloring
import momapy.core

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
    "font_family",
    "font_size",
    "font_style",
    "font_weight",
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

ARC_ATTR_NAMES = [
    "arrowhead_bar_height",
    "arrowhead_fill",
    "arrowhead_filter",
    "arrowhead_height",
    "arrowhead_stroke",
    "arrowhead_stroke_dasharray",
    "arrowhead_stroke_dashoffset",
    "arrowhead_stroke_width",
    "arrowhead_transform",
    "arrowhead_triangle_height",
    "arrowhead_triangle_width",
    "arrowhead_sep",
    "arrowhead_width",
    "end_arrowhead_fill",
    "end_arrowhead_filter",
    "end_arrowhead_stroke",
    "end_arrowhead_stroke_dashend_array",
    "end_arrowhead_stroke_dashoffset",
    "end_arrowhead_stroke_width",
    "end_arrowhead_transform",
    "end_shorten",
    "fill",
    "filter",
    "font_family",
    "font_size",
    "font_style",
    "font_weight",
    "path_fill",
    "path_filter",
    "path_stroke",
    "path_stroke_dashstart_array",
    "path_stroke_dashoffset",
    "path_stroke_width",
    "path_transform",
    "start_arrowhead_fill",
    "start_arrowhead_filter",
    "start_arrowhead_stroke",
    "start_arrowhead_stroke_dashstart_array",
    "start_arrowhead_stroke_dashoffset",
    "start_arrowhead_stroke_width",
    "start_arrowhead_transform",
    "start_shorten",
    "stroke",
    "stroke_dasharray",
    "stroke_dashoffset",
    "stroke_width",
    "transform",
]


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


def has_type(type_1, type_2):  # checks if type_1 == type_2 or type_2 in type_1
    sub_types = typing.get_args(type_1)
    if not sub_types:
        return type_1 == type_2
    else:
        if type_2 in sub_types:
            return True
        else:
            for sub_type in sub_types:
                if has_type(sub_type, type_2):
                    return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Tool for generating a CSS template file from one or more modules"
    )
    parser.add_argument(
        "-c",
        "--color-scheme",
        action="store_true",
        default=False,
        help="Consider only attributes whose values are colors",
    )
    parser.add_argument(
        "-n",
        "--no-color-scheme",
        action="store_true",
        default=False,
        help="Consider only attributes whose values are not colors",
    )

    parser.add_argument("module", nargs="+")
    args = parser.parse_args()
    run(args)


def run(args):
    no_color_scheme_only = args.no_color_scheme
    color_scheme_only = args.color_scheme
    d = {}
    for module_name in args.module:
        module = importlib.import_module(module_name)
        for cls_name in dir(module):
            cls = getattr(module, cls_name)
            if (
                not cls_name.startswith("_")
                and isinstance(cls, type)
                and (
                    issubclass(cls, momapy.core.Node)
                    or issubclass(cls, momapy.core.Arc)
                )
            ):
                if cls_name not in d:
                    d[cls_name] = {}
                fields = dataclasses.fields(cls)
                if issubclass(cls, momapy.core.Node):
                    attr_names = NODE_ATTR_NAMES
                else:
                    attr_names = ARC_ATTR_NAMES
                for attr_name in attr_names:
                    for field in fields:
                        if field.name == attr_name:
                            attr_default_value = field.default
                            if attr_default_value != dataclasses.MISSING:
                                if not (
                                    color_scheme_only
                                    and not has_type(
                                        field.type, momapy.coloring.Color
                                    )
                                    or no_color_scheme_only
                                    and has_type(
                                        field.type, momapy.coloring.Color
                                    )
                                ):
                                    attr_default_value = (
                                        transform_attr_default_value(
                                            attr_default_value
                                        )
                                    )
                                    attr_name = attr_name.replace("_", "-")
                                    if attr_name not in d[cls_name]:
                                        d[cls_name][attr_name] = str(
                                            attr_default_value
                                        )
                            break
    l = []
    for cls_name in sorted(d.keys()):
        l.append(f"{cls_name} {{")
        for attr_name in sorted(d[cls_name].keys()):
            l.append(f"\t{attr_name}: {d[cls_name][attr_name]};")
        l.append("}")
        l.append("\n")
    if l:
        l.pop()
    output_string = "\n".join(l)
    print(output_string, end="")


if __name__ == "__main__":
    main()
