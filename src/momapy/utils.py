"""Utility classes and functions for momapy.

This module provides general-purpose utilities including bidirectional mappings,
pretty printing for dataclasses, and collection manipulation helpers.
"""

import collections.abc
import dataclasses
import uuid
import types

import colorama
import frozendict

import momapy


class SurjectionDict(dict):
    """A dictionary that maintains an inverse mapping from values to keys.

    A surjection (onto mapping) where each value maps back to one or more keys.
    The inverse is automatically maintained as the dict is modified.

    Note:
        Code adapted from https://stackoverflow.com/a/21894086 by Basj.

    Example:
        >>> d = SurjectionDict({'a': 1, 'b': 1, 'c': 2})
        >>> d.inverse
        frozendict.frozendict({1: ['a', 'b'], 2: ['c']})
        >>> d['d'] = 1
        >>> d.inverse
        frozendict.frozendict({1: ['a', 'b', 'd'], 2: ['c']})
    """

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
        """Get the inverse mapping from values to keys.

        Returns:
            A frozendict mapping each value to a list of keys that map to it.
        """
        return frozendict.frozendict(self._inverse)


class FrozenSurjectionDict(frozendict.frozendict):
    """An immutable version of SurjectionDict.

    A frozen dictionary that maintains an inverse mapping from values to keys.
    The inverse is computed once at initialization and cannot be modified.

    Example:
        >>> d = FrozenSurjectionDict({'a': 1, 'b': 1, 'c': 2})
        >>> d.inverse
        frozendict.frozendict({1: ['a', 'b'], 2: ['c']})
    """

    def __init__(self, *args, **kwargs):
        inverse = {}
        for key, value in self.items():
            inverse.setdefault(value, []).append(key)
        object.__setattr__(self, "_inverse", frozendict.frozendict(inverse))

    @property
    def inverse(self):
        """Get the inverse mapping from values to keys.

        Returns:
            A frozendict mapping each value to a list of keys that map to it.
        """
        return self._inverse


def pretty_print(obj, max_depth=0, exclude_cls=None, _depth=0, _indent=0):
    """Pretty print a dataclass or iterable object with colors.

    Recursively prints the structure of dataclasses and iterables with
    type information and color coding for better readability.

    Args:
        obj: The object to print (dataclass, iterable, or other).
        max_depth: Maximum recursion depth. 0 means unlimited. Defaults to 0.
        exclude_cls: List of classes to exclude from recursive printing.
        _depth: Internal parameter for tracking current depth.
        _indent: Internal parameter for tracking current indentation.

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class Point:
        ...     x: float
        ...     y: float
        >>>
        >>> p = Point(x=1.0, y=2.0)
        >>> pretty_print(p)
        <Point: Point(x=1.0, y=2.0)>
          * x: <class 'float'> = 1.0
          * y: <class 'float'> = 2.0
    """

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
    """Find and return an element from a collection using equality.

    Args:
        element: The element to search for.
        collection: An iterable collection to search in.

    Returns:
        The existing element from the collection if found, None otherwise.

    Example:
        >>> items = [1, 2, 3]
        >>> get_element_from_collection(2, items)
        2
        >>> get_element_from_collection(4, items) is None
        True
    """
    for e in collection:
        if e == element:
            return e
    return None


def get_or_return_element_from_collection(element, collection):
    """Get existing element from collection or return the input element.

    Args:
        element: The element to search for.
        collection: An iterable collection to search in.

    Returns:
        The existing element from the collection if found, otherwise
        the input element.

    Example:
        >>> items = [1, 2, 3]
        >>> get_or_return_element_from_collection(2, items)
        2
        >>> get_or_return_element_from_collection(4, items)
        4
    """
    existing_element = get_element_from_collection(element, collection)
    if existing_element is not None:
        return existing_element
    return element


def add_or_replace_element_in_set(element, set_, func=None, cache=None):
    """Add element to set or replace existing element based on condition.

    If the element doesn't exist in the set, it is added. If it exists
    and a comparison function is provided, the existing element may be
    replaced if the function returns True.

    Args:
        element: The element to add or replace with.
        set_: The set to modify.
        func: Optional comparison function func(new, existing) that returns
            True if the new element should replace the existing one.
        cache: Optional dict mapping elements to themselves. When provided,
            uses O(1) dict lookup instead of O(n) linear scan. The cache
            is kept in sync with the set on add/replace.

    Returns:
        The element that is now in the set (either the existing or new one).

    Example:
        >>> s = {1, 2, 3}
        >>> add_or_replace_element_in_set(4, s)
        4
        >>> 4 in s
        True
        >>>
        >>> # Replace only if new value is greater
        >>> add_or_replace_element_in_set(2, s, lambda new, old: new > old)
        2  # Not replaced since 2 is not > 2
    """
    if cache is not None:
        existing_element = cache.get(element)
    else:
        existing_element = get_element_from_collection(element, set_)
    if existing_element is None:
        set_.add(element)
        if cache is not None:
            cache[element] = element
        return element
    # Replaces existing element by input element if func(element, existing_element) is True
    elif func is not None and func(element, existing_element):
        set_.remove(existing_element)
        set_.add(element)
        if cache is not None:
            del cache[existing_element]
            cache[element] = element
        return element
    return existing_element


def make_uuid4_as_str():
    """Generate a UUID4 as a string.

    Returns:
        A string representation of a random UUID (version 4).

    Example:
        >>> uuid_str = make_uuid4_as_str()
        >>> isinstance(uuid_str, str)
        True
        >>> len(uuid_str)  # Standard UUID string length
        36
    """
    return str(uuid.uuid4())
