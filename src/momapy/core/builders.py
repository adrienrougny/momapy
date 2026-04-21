"""Builder classes and helper functions for core map elements."""

import abc

from momapy.core.elements import (
    LayoutElement,
    MapElement,
    ModelElement,
)
from momapy.core.layout import (
    DoubleHeadedArc,
    Layout,
    Node,
    SingleHeadedArc,
    TextLayout,
)
from momapy.core.map import Map
from momapy.core.mapping import LayoutModelMappingBuilder
from momapy.core.model import Model

import momapy.builder


def _map_element_builder_hash(self):
    return hash(self.id_)


def _map_element_builder_eq(self, other):
    return self.__class__ == other.__class__ and self.id_ == other.id_


MapElementBuilder = momapy.builder.get_or_make_builder_cls(
    MapElement,
    builder_namespace={
        "__hash__": _map_element_builder_hash,
        "__eq__": _map_element_builder_eq,
    },
)

ModelElementBuilder = momapy.builder.get_or_make_builder_cls(ModelElement)
"""Base class for model element builders"""
LayoutElementBuilder = momapy.builder.get_or_make_builder_cls(LayoutElement)
"""Base class for layout element builders"""
NodeBuilder = momapy.builder.get_or_make_builder_cls(Node)
"""Base class for node builders"""
SingleHeadedArcBuilder = momapy.builder.get_or_make_builder_cls(SingleHeadedArc)
"""Base class for single-headed arc builders"""
DoubleHeadedArcBuilder = momapy.builder.get_or_make_builder_cls(DoubleHeadedArc)
"""Base class for double-headed arc builders"""
TextLayoutBuilder = momapy.builder.get_or_make_builder_cls(TextLayout)
"""Class for text layout builders"""


def _model_builder_new_element(self, element_cls, *args, **kwargs):
    if not momapy.builder.issubclass_or_builder(element_cls, ModelElement):
        raise TypeError(
            "element class must be a subclass of ModelElementBuilder or ModelElement"
        )
    return momapy.builder.new_builder_object(element_cls, *args, **kwargs)


ModelBuilder = momapy.builder.get_or_make_builder_cls(
    Model,
    builder_namespace={"new_element": _model_builder_new_element},
)
"""Base class for model builders"""


def _layout_builder_new_element(self, element_cls, *args, **kwargs):
    if not momapy.builder.issubclass_or_builder(element_cls, LayoutElement):
        raise TypeError(
            "element class must be a subclass of LayoutElementBuilder or LayoutElement"
        )
    return momapy.builder.new_builder_object(element_cls, *args, **kwargs)


LayoutBuilder = momapy.builder.get_or_make_builder_cls(
    Layout,
    builder_namespace={"new_element": _layout_builder_new_element},
)
"""Base class for layout builders"""


momapy.builder.register_builder_cls(LayoutModelMappingBuilder)


@abc.abstractmethod
def _map_builder_new_model(self, *args, **kwargs) -> ModelBuilder:
    pass


@abc.abstractmethod
def _map_builder_new_layout(self, *args, **kwargs) -> LayoutBuilder:
    pass


def _map_builder_new_layout_model_mapping(
    self,
) -> LayoutModelMappingBuilder:
    return LayoutModelMappingBuilder()


def _map_builder_new_model_element(
    self, element_cls, *args, **kwargs
) -> ModelElementBuilder:
    model_element = self.model.new_element(element_cls, *args, **kwargs)
    return model_element


def _map_builder_new_layout_element(
    self, element_cls, *args, **kwargs
) -> LayoutElementBuilder:
    layout_element = self.layout.new_element(element_cls, *args, **kwargs)
    return layout_element


def _map_builder_add_mapping(
    self,
    layout_element: "LayoutElement",
    model_element: "ModelElement | tuple[ModelElement, ModelElement]",
):
    self.layout_model_mapping.add_mapping(layout_element, model_element)


def _map_builder_get_mapping(
    self,
    map_element: "MapElement",
) -> "ModelElement | list[LayoutElement]":
    return self.layout_model_mapping.get_mapping(map_element)


MapBuilder = momapy.builder.get_or_make_builder_cls(
    Map,
    builder_namespace={
        "new_model": _map_builder_new_model,
        "new_layout": _map_builder_new_layout,
        "new_layout_model_mapping": _map_builder_new_layout_model_mapping,
        "new_model_element": _map_builder_new_model_element,
        "new_layout_element": _map_builder_new_layout_element,
        "add_mapping": _map_builder_add_mapping,
    },
)
"""Base class for map builders"""
