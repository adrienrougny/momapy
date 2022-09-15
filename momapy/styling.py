import abc
import dataclasses
import typing
import uuid
import momapy.builder

@dataclasses.dataclass(frozen=True)
class Selector(object):

    @abc.abstractmethod
    def select(self, obj, ancestors) -> bool:
        pass

@dataclasses.dataclass(frozen=True)
class ClassSelector(Selector):
    cls: typing.Optional[typing.Type] = None

    def select(self, obj, ancestors):
        return isinstance(
            obj,
            (self.cls, momapy.builder.get_or_make_builder_cls(self.cls))
        )

@dataclasses.dataclass(frozen=True)
class ParentSelector(Selector):
    parent_selector: Selector
    child_selector: Selector

    def select(self, obj, ancestors):
        if len(ancestors) == 0:
            return False
        return (self.child_selector.select(obj, ancestors)
                and self.parent_selector.select(ancestors[-1], ancestors[:-1]))


@dataclasses.dataclass(frozen=True)
class AncestorSelector(Selector):
    ancestor_selector: Selector
    child_selector: Selector

    def select(self, obj, ancestors):
        if len(ancestors) == 0:
            return False
        return (self.child_selector.select(obj, ancestors)
                and any([self.ancestor_selector.select(ancestor, ancestors[:i])
                         for i, ancestor in enumerate(ancestors)])
               )


@dataclasses.dataclass(frozen=True)
class IdSelector(Selector):
    id_: typing.Union[str, uuid.UUID] = None

    def select(self, obj, ancestors):
        return hasattr(obj, "id") and obj.id == self.id_

def apply_style_collection(layout_element, style_collection):
    for attribute, value in style_collection.items():
        if hasattr(layout_element, attribute):
            setattr(layout_element, attribute, value)

def apply_style_sheet(layout_element, style_sheet, ancestors=None):
    if ancestors is None:
        ancestors = []
    for selector, style_collection in style_sheet.items():
        if selector.select(layout_element, ancestors):
            apply_style_collection(layout_element, style_collection)
    ancestors = ancestors + [layout_element]
    for child in layout_element.children():
        apply_style_sheet(child, style_sheet, ancestors)
