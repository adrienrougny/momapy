import collections.abc
import dataclasses
import uuid
import types

import colorama
import frozendict

import momapy


# code adapted from https://stackoverflow.com/a/21894086 authored by Basj
class SurjectionDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._inverse = {}
        for key, value in self.items():
            self._inverse.setdefault(value, []).append(key)

    def __setitem__(self, key, value):
        if key in self:
            self._inverse[self[key]].remove(key)
        super(SurjectionDict, self).__setitem__(key, value)
        self._inverse.setdefault(value, []).append(key)

    def __delitem__(self, key):
        value = self[key]  # throws expected KeyError if key not in self
        super().__delitem__(key)
        # we know key was in self, hence value is expected to be in self.inverse
        self._inverse[value].remove(key)
        if not self._inverse[value]:
            del self._inverse[value]

    @property
    def inverse(self):
        return frozendict.frozendict(self._inverse)


class FrozenSurjectionDict(frozendict.frozendict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inverse = {}
        for key, value in self.items():
            inverse.setdefault(value, []).append(key)
        object.__setattr__(self, "_inverse", frozendict.frozendict(inverse))

    @property
    def inverse(self):
        return self._inverse


def pretty_print(obj, max_depth=0, exclude_cls=None, _depth=0, _indent=0):
    def _print_with_indent(s, indent):
        print(f"{'  ' * indent}{s}")

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
    if issubclass(obj_typing, tuple(exclude_cls)):
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
                if (
                    not isinstance(attr_value, (str, float, int, bool, types.NoneType))
                    and attr_value
                ):
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


def add_or_replace_element_in_set(element, set_, func=None):
    existing_element = get_element_from_collection(element, set_)
    if existing_element is None:
        set_.add(element)
        return element
    # Replaces existing element by input element if func(element, existing_element) is True
    elif func is not None and func(element, existing_element):
        set_.remove(existing_element)
        set_.add(element)
        return element
    return existing_element


def make_uuid4_as_str():
    return str(uuid.uuid4())
