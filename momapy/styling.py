import abc
import dataclasses
import typing
import uuid
import momapy.builder

@dataclasses.dataclass(frozen=True)
class Selector(object):

    @abc.abstractmethod
    def select(self, obj) -> bool:
        pass

@dataclasses.dataclass(frozen=True)
class TypeSelector(Selector):
    cls: typing.Optional[typing.Type] = None

    def select(self, obj):
        return isinstance(
            obj,
            (self.cls, momapy.builder.get_or_make_builder_cls(self.cls))
        )

@dataclasses.dataclass(frozen=True)
class IdSelector(Selector):
    id_: typing.Union[str, uuid.UUID] = None

    def select(self, obj):
        return hasattr(obj, "id") and obj.id == self.id_

def apply_style_collection(layout_element, style_collection):
    for attribute, value in style_collection.items():
        if hasattr(layout_element, attribute):
            setattr(layout_element, attribute, value)

def apply_style_sheet(layout_element, style_sheet):
    if isinstance(layout_element, momapy.builder.MapBuilder):
        layout_element = layout_element.layout
    for sub_layout_element in layout_element.flatten():
        for selector, style_collection in style_sheet.items():
            if selector.select(sub_layout_element):
                apply_style_collection(sub_layout_element, style_collection)
