import frozendict
import collections.abc
import dataclasses
import uuid

import colorama
import numpy


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
        obj, (str, bytes, bytearray, momapy.geometry.Point)
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


def get_uuid4_as_str():
    return str(uuid.uuid4())
