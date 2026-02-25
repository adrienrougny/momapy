"""Builder classes and helper functions for core map elements."""

import abc

import momapy.builder
import momapy.core.elements
import momapy.core.layout
import momapy.core.model
import momapy.core.mapping
import momapy.core.map


def _map_element_builder_hash(self):
    return hash(self.id_)


def _map_element_builder_eq(self, other):
    return self.__class__ == other.__class__ and self.id_ == other.id_


MapElementBuilder = momapy.builder.get_or_make_builder_cls(
    momapy.core.elements.MapElement,
    builder_namespace={
        "__hash__": _map_element_builder_hash,
        "__eq__": _map_element_builder_eq,
    },
)

ModelElementBuilder = momapy.builder.get_or_make_builder_cls(
    momapy.core.elements.ModelElement
)
"""Base class for model element builders"""
LayoutElementBuilder = momapy.builder.get_or_make_builder_cls(
    momapy.core.elements.LayoutElement
)
"""Base class for layout element builders"""
NodeBuilder = momapy.builder.get_or_make_builder_cls(momapy.core.layout.Node)
"""Base class for node builders"""
SingleHeadedArcBuilder = momapy.builder.get_or_make_builder_cls(
    momapy.core.layout.SingleHeadedArc
)
"""Base class for single-headed arc builders"""
DoubleHeadedArcBuilder = momapy.builder.get_or_make_builder_cls(
    momapy.core.layout.DoubleHeadedArc
)
"""Base class for double-headed arc builders"""
TextLayoutBuilder = momapy.builder.get_or_make_builder_cls(
    momapy.core.layout.TextLayout
)
"""Class for text layout builders"""


def _model_builder_new_element(self, element_cls, *args, **kwargs):
    if not momapy.builder.issubclass_or_builder(
        element_cls, momapy.core.elements.ModelElement
    ):
        raise TypeError(
            "element class must be a subclass of ModelElementBuilder or ModelElement"
        )
    return momapy.builder.new_builder_object(element_cls, *args, **kwargs)


ModelBuilder = momapy.builder.get_or_make_builder_cls(
    momapy.core.model.Model,
    builder_namespace={"new_element": _model_builder_new_element},
)
"""Base class for model builders"""


def _layout_builder_new_element(self, element_cls, *args, **kwargs):
    if not momapy.builder.issubclass_or_builder(
        element_cls, momapy.core.elements.LayoutElement
    ):
        raise TypeError(
            "element class must be a subclass of LayoutElementBuilder or LayoutElement"
        )
    return momapy.builder.new_builder_object(element_cls, *args, **kwargs)


LayoutBuilder = momapy.builder.get_or_make_builder_cls(
    momapy.core.layout.Layout,
    builder_namespace={"new_element": _layout_builder_new_element},
)
"""Base class for layout builders"""


momapy.builder.register_builder_cls(momapy.core.mapping.LayoutModelMappingBuilder)


@abc.abstractmethod
def _map_builder_new_model(self, *args, **kwargs) -> ModelBuilder:
    pass


@abc.abstractmethod
def _map_builder_new_layout(self, *args, **kwargs) -> LayoutBuilder:
    pass


def _map_builder_new_layout_model_mapping(
    self,
) -> momapy.core.mapping.LayoutModelMappingBuilder:
    return momapy.core.mapping.LayoutModelMappingBuilder()


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
    layout_element: "momapy.core.elements.LayoutElement",
    model_element: "momapy.core.elements.ModelElement | tuple[momapy.core.elements.ModelElement, momapy.core.elements.ModelElement]",
):
    self.layout_model_mapping.add_mapping(layout_element, model_element)


def _map_builder_get_mapping(
    self,
    map_element: "momapy.core.elements.MapElement",
) -> "momapy.core.elements.ModelElement | list[momapy.core.elements.LayoutElement]":
    return self.layout_model_mapping.get_mapping(map_element)


MapBuilder = momapy.builder.get_or_make_builder_cls(
    momapy.core.map.Map,
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
