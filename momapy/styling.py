import abc
import dataclasses
import typing
import uuid
import pyparsing as pp

import momapy.builder
import momapy.coloring

@dataclasses.dataclass(frozen=True)
class Selector(object):

    @abc.abstractmethod
    def select(self, obj, ancestors) -> bool:
        pass

@dataclasses.dataclass(frozen=True)
class TypeSelector(Selector):
    class_name: str = None

    def select(self, obj, ancestors):
        obj_class = type(obj).__name__
        if not self.class_name.endswith("Builder"):
            return (obj_class == self.class_name
                    or obj_class == f"{self.class_name}Builder")
        return obj_class == self.class_name

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
        if len(ancestors) == 0:
            return False
        return (self.child_selector.select(obj, ancestors)
                and self.parent_selector.select(ancestors[-1], ancestors[:-1]))

@dataclasses.dataclass(frozen=True)
class DescendantSelector(Selector):
    ancestor_selector: Selector
    descendant_selector: Selector

    def select(self, obj, ancestors):
        if len(ancestors) == 0:
            return False
        return (self.descendant_selector.select(obj, ancestors)
                and any([self.ancestor_selector.select(ancestor, ancestors[:i])
                         for i, ancestor in enumerate(ancestors)])
               )

@dataclasses.dataclass(frozen=True)
class OrSelector(Selector):
    selectors: tuple[Selector]

    def select(self, obj, ancestors):
        return any([selector.select(obj, ancestors)
                    for selector in self.selectors])

def apply_style_collection(layout_element, style_collection):
    for attribute, value in style_collection.items():
        if hasattr(layout_element, attribute):
            setattr(layout_element, attribute, value)

def apply_style_sheet(layout_element, style_sheet, descendants=None):
    if descendants is None:
        descendants = []
    for selector, style_collection in style_sheet.items():
        if selector.select(layout_element, descendants):
            apply_style_collection(layout_element, style_collection)
    descendants = descendants + [layout_element]
    for child in layout_element.children():
        apply_style_sheet(child, style_sheet, descendants)

def read_string(s):
    style_sheet = _css_style_sheet.parse_string(s, parse_all=True)[0]
    return style_sheet

def read_file(file):
    style_sheet = _css_style_sheet.parse_file(file, parse_all=True)[0]
    return style_sheet

_css_none_value = pp.Literal("none")
_css_float_value = pp.Combine(pp.Word(pp.nums) + pp.Literal(".") + pp.Word(pp.nums))
_css_string_value = pp.quoted_string
_css_color_name_value = pp.Word(pp.alphas+"_")
_css_color_value = _css_color_name_value
_css_int_value = pp.Word(pp.nums)
_css_attribute_value = _css_none_value | _css_float_value | _css_string_value | _css_color_value | _css_int_value
_css_attribute_name = pp.Word(pp.alphas+"_", pp.alphanums+"_")
_css_style = _css_attribute_name + pp.Literal(":") + _css_attribute_value + pp.Literal(";")
_css_style_collection = pp.Literal("{") + pp.Group(_css_style[1, ...]) + pp.Literal("}")
_css_id = pp.Word(pp.printables)
_css_id_selector = pp.Literal("#") + _css_id
_css_type_selector = pp.Word(pp.alphas+"_", pp.alphanums+"_")
_css_elementary_selector = _css_type_selector | _css_id_selector
_css_child_selector = _css_elementary_selector + pp.Literal(">") + _css_elementary_selector
_css_descendant_selector = _css_elementary_selector + pp.OneOrMore(pp.White()) + _css_elementary_selector
_css_or_selector = pp.Group(pp.delimited_list(_css_elementary_selector, ","))
_css_selector = _css_child_selector | _css_descendant_selector | _css_or_selector | _css_elementary_selector
_css_rule = _css_selector + _css_style_collection
_css_style_sheet = pp.Group(_css_rule[1, ...])

@_css_none_value.set_parse_action
def _resolve_css_none_value(results):
    return None

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
    if not momapy.coloring.colors.has_color(results[0]):
        raise ValueError(f"{results[0]} is not a valid color name")
    return getattr(momapy.coloring.colors, results[0])

@_css_attribute_value.set_parse_action
def _resolve_css_attribute_value(results):
    return results[0]

@_css_attribute_name.set_parse_action
def _resolve_css_attribute_name(results):
    return results[0]

@_css_style.set_parse_action
def _resolve_css_style(results):
    return (results[0], results[2],)

@_css_style_collection.set_parse_action
def _resolve_css_style_collection(results):
    return dict(list(results[1]))

@_css_id.set_parse_action
def _resolve_css_id(results):
    return results[0]

@_css_id_selector.set_parse_action
def _resolve_id_selector(results):
    return IdSelector(results[1])

@_css_type_selector.set_parse_action
def _resolve_css_type_selector(results):
    return TypeSelector(results[0])

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
    return (results[0], results[1],)

@_css_style_sheet.set_parse_action
def _resolve_css_style_sheet(results):
    return dict(list(results[0]))
