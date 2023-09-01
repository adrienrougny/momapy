import frozendict
import collections.abc
import dataclasses
import colorama


def pretty_print(obj, max_depth=0, _depth=0, _indent=0):
    def _print_with_indent(s, indent):
        print(f"{'  '*indent}{s}")

    def _get_value_string(attr_value, max_len=30):
        s = str(attr_value)
        if len(s) > max_len:
            s = f"{s[:max_len]}..."
        return s

    if _depth > max_depth:
        return
    obj_typing = type(obj)
    obj_value_string = _get_value_string(obj)
    obj_string = f"{colorama.Fore.BLACK}{obj_typing}{colorama.Fore.RED}: {obj_value_string}{colorama.Style.RESET_ALL}"
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
                    _depth=_depth + 1,
                    _indent=_indent + 2,
                )
    if isinstance(obj, collections.abc.Iterable):
        for i, elem_value in enumerate(obj):
            elem_typing = type(elem_value)
            elem_value_string = _get_value_string(elem_value)
            elem_string = f"{colorama.Fore.BLUE}- {i}{colorama.Fore.MAGENTA}: {elem_typing} = {colorama.Fore.RED}{elem_value_string}{colorama.Style.RESET_ALL}"
            _print_with_indent(elem_string, _indent + 1)
            pretty_print(
                elem_value,
                max_depth=max_depth,
                _depth=_depth + 1,
                _indent=_indent + 2,
            )


def print_classes(obj):
    for cls in type(obj).__mro__:
        print(cls)
