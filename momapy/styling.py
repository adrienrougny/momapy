import abc
import dataclasses
import typing
import uuid
import pyparsing as pp
import frozendict
import copy


import momapy.coloring
import momapy.drawing
import momapy.core


class StyleCollection(dict):
    pass


class StyleSheet(dict):
    def __or__(self, other):
        d = copy.deepcopy(self)
        for key, value in other.items():
            if key in d:
                d[key] |= value
            else:
                d[key] = value
        return StyleSheet(d)

    def __ior__(self, other):
        return self.__or__(other)


@dataclasses.dataclass(frozen=True)
class Selector(object):
    @abc.abstractmethod
    def select(self, obj, ancestors) -> bool:
        pass


@dataclasses.dataclass(frozen=True)
class TypeSelector(Selector):
    class_name: str

    def select(self, obj, ancestors):
        obj_cls_name = type(obj).__name__
        return (
            obj_cls_name == self.class_name
            or obj_cls_name == f"{self.class_name}Builder"
        )


@dataclasses.dataclass(frozen=True)
class ClassSelector(Selector):
    class_name: str

    def select(self, obj, ancestors):
        for cls in type(obj).__mro__:
            cls_name = cls.__name__
            if (
                cls_name == self.class_name
                or cls_name == f"{self.class_name}Builder"
            ):
                return True
        return False


@dataclasses.dataclass(frozen=True)
class IdSelector(Selector):
    id_: typing.Union[str, uuid.UUID]

    def select(self, obj, ancestors):
        return hasattr(obj, "id") and obj.id == self.id_


@dataclasses.dataclass(frozen=True)
class ChildSelector(Selector):
    parent_selector: Selector
    child_selector: Selector

    def select(self, obj, ancestors):
        if not ancestors:
            return False
        return self.child_selector.select(
            obj, ancestors
        ) and self.parent_selector.select(ancestors[-1], ancestors[:-1])


@dataclasses.dataclass(frozen=True)
class DescendantSelector(Selector):
    ancestor_selector: Selector
    descendant_selector: Selector

    def select(self, obj, ancestors):
        if not ancestors:
            return False
        return self.descendant_selector.select(obj, ancestors) and any(
            [
                self.ancestor_selector.select(ancestor, ancestors[:i])
                for i, ancestor in enumerate(ancestors)
            ]
        )


@dataclasses.dataclass(frozen=True)
class OrSelector(Selector):
    selectors: tuple[Selector]

    def select(self, obj, ancestors):
        return any(
            [selector.select(obj, ancestors) for selector in self.selectors]
        )


def join_style_sheets(style_sheets):
    if not style_sheets:
        return None
    output_style_sheet = style_sheets[0]
    for style_sheet in style_sheets[1:]:
        output_style_sheet |= style_sheet
    return output_style_sheet


def apply_style_collection(layout_element, style_collection, strict=True):
    for attribute, value in style_collection.items():
        if hasattr(layout_element, attribute):
            setattr(layout_element, attribute, value)
        else:
            if strict:
                raise AttributeError(
                    f"{type(layout_element)} object has no "
                    f"attribute '{attribute}'"
                )


def apply_style_sheet(layout_element, style_sheet, strict=True, ancestors=None):
    if isinstance(layout_element, momapy.core.MapBuilder):
        layout_element = layout_element.layout
    if style_sheet is not None:
        if ancestors is None:
            ancestors = []
        for selector, style_collection in style_sheet.items():
            if selector.select(layout_element, ancestors):
                apply_style_collection(layout_element, style_collection, strict)
        ancestors = ancestors + [layout_element]
        for child in layout_element.children():
            apply_style_sheet(child, style_sheet, strict, ancestors)


def read_string(s):
    style_sheet = _css_style_sheet.parse_string(s, parse_all=True)[0]
    return style_sheet


def read_file(file_or_file_name):
    style_sheet = _css_style_sheet.parse_file(
        file_or_file_name, parse_all=True
    )[0]
    return style_sheet


_css_unset_value = pp.Literal("unset")
_css_none_value = pp.Literal("none")
_css_float_value = pp.Combine(
    pp.Word(pp.nums) + pp.Literal(".") + pp.Word(pp.nums)
)
_css_string_value = pp.quoted_string
_css_color_name_value = pp.Word(pp.alphas + "_")
_css_color_value = _css_color_name_value
_css_int_value = pp.Word(pp.nums)
_css_drop_shadow_filter_value = (
    pp.Literal("drop-shadow(")
    + _css_float_value
    + pp.Literal(",")
    + _css_float_value
    + pp.Literal(",")
    + _css_float_value
    + pp.Literal(",")
    + _css_float_value
    + pp.Literal(",")
    + _css_color_value
    + pp.Literal(")")
)
_css_filter_value = _css_drop_shadow_filter_value
_css_simple_value = (
    _css_drop_shadow_filter_value
    | _css_unset_value
    | _css_none_value
    | _css_float_value
    | _css_string_value
    | _css_color_value
    | _css_int_value
)
_css_list_value = pp.Group(pp.delimited_list(_css_simple_value, ",", min=2))
_css_attribute_value = _css_list_value | _css_simple_value
_css_attribute_name = pp.Word(pp.alphas + "_", pp.alphanums + "_" + "-")
_css_style = (
    _css_attribute_name
    + pp.Literal(":")
    + _css_attribute_value
    + pp.Literal(";")
)
_css_style_collection = (
    pp.Literal("{") + pp.Group(_css_style[1, ...]) + pp.Literal("}")
)
_css_id = pp.Word(pp.printables, exclude_chars=",")
_css_id_selector = pp.Literal("#") + _css_id
_css_class_name = pp.Word(pp.alphas + "_", pp.alphanums + "_")
_css_type_selector = _css_class_name
_css_class_selector = pp.Literal(".") + _css_class_name
_css_elementary_selector = (
    _css_class_selector | _css_type_selector | _css_id_selector
)
_css_child_selector = (
    _css_elementary_selector + pp.Literal(">") + _css_elementary_selector
)
_css_descendant_selector = (
    _css_elementary_selector
    + pp.OneOrMore(pp.White())
    + _css_elementary_selector
)
_css_or_selector = pp.Group(
    pp.delimited_list(_css_elementary_selector, ",", min=2)
)
_css_selector = (
    _css_child_selector
    | _css_descendant_selector
    | _css_or_selector
    | _css_elementary_selector
)
_css_rule = _css_selector + _css_style_collection
_css_style_sheet = pp.Group(_css_rule[1, ...])


@_css_unset_value.set_parse_action
def _resolve_css_unset_value(results):
    return results[0]


@_css_none_value.set_parse_action
def _resolve_css_none_value(results):
    return momapy.drawing.NoneValue


@_css_float_value.set_parse_action
def _resolve_css_float_value(results):
    return float(results[0])


@_css_string_value.set_parse_action
def _resolve_css_string_value(results):
    return str(results[0][1:-1])


@_css_int_value.set_parse_action
def _resolve_css_int_value(results):
    return int(results[0])


@_css_color_name_value.set_parse_action
def _resolve_css_color_name_value(results):
    if not momapy.coloring.has_color(results[0]):
        raise ValueError(f"{results[0]} is not a valid color name")
    return getattr(momapy.coloring, results[0])


@_css_drop_shadow_filter_value.set_parse_action
def _resolve_css_drop_shadow_filter_value(results):
    filter_effect = momapy.builder.get_or_make_builder_cls(
        momapy.drawing.DropShadowEffect
    )(
        dx=results[1],
        dy=results[3],
        std_deviation=results[5],
        flood_opacity=results[7],
        flood_color=results[9],
    )
    filter = momapy.builder.get_or_make_builder_cls(momapy.drawing.Filter)(
        effects=momapy.core.TupleBuilder([filter_effect])
    )
    return filter


# Issue: the function cannot return None (pyparsing bug?) otherwise it simply
# does not apply the function
@_css_simple_value.set_parse_action
def _resolve_css_simple_value(results):
    return results[0]


@_css_list_value.set_parse_action
def _resolve_css_list_value(results):
    return [momapy.core.TupleBuilder(results[0])]


@_css_attribute_value.set_parse_action
def _resolve_css_attribute_value(results):
    # see above
    if results[0] == "unset":
        results[0] = None
    return results


@_css_attribute_name.set_parse_action
def _resolve_css_attribute_name(results):
    return results[0].replace("-", "_")


@_css_style.set_parse_action
def _resolve_css_style(results):
    return (
        results[0],
        results[2],
    )


@_css_style_collection.set_parse_action
def _resolve_css_style_collection(results):
    return StyleCollection(dict(list(results[1])))


@_css_id.set_parse_action
def _resolve_css_id(results):
    return results[0]


@_css_id_selector.set_parse_action
def _resolve_id_selector(results):
    return IdSelector(results[1])


@_css_class_name.set_parse_action
def _resolve_css_class_name(results):
    return results[0]


@_css_type_selector.set_parse_action
def _resolve_css_type_selector(results):
    return TypeSelector(results[0])


@_css_class_selector.set_parse_action
def _resolve_css_class_selector(results):
    return ClassSelector(results[1])


@_css_elementary_selector.set_parse_action
def _resolve_css_elementary_selector(results):
    return results[0]


@_css_child_selector.set_parse_action
def _resolve_css_child_selector(results):
    return ChildSelector(results[0], results[2])


@_css_descendant_selector.set_parse_action
def _resolve_css_descendant_selector(results):
    return DescendantSelector(results[0], results[2])


@_css_or_selector.set_parse_action
def _resolve_css_or_selector(results):
    return OrSelector(tuple(results[0]))


@_css_rule.set_parse_action
def _resolve_css_rule(results):
    return (
        results[0],
        results[1],
    )


@_css_style_sheet.set_parse_action
def _resolve_css_style_sheet(results):
    return StyleSheet(dict(list(results[0])))
