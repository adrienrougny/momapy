"""Layout-model mapping classes."""

import typing
import typing_extensions

import momapy.utils
import momapy.builder
import momapy.core.elements


class LayoutModelMapping(momapy.utils.FrozenSurjectionDict):
    """Class for mappings between model elements and layout elements"""

    def get_mapping(
        self,
        map_element: "momapy.core.elements.MapElement | tuple[momapy.core.elements.ModelElement, momapy.core.elements.ModelElement]",
    ) -> "momapy.core.elements.ModelElement | list[momapy.core.elements.LayoutElement]":
        if map_element in self:
            return self[map_element]
        return self.inverse.get(map_element)

    def is_submapping(self, other) -> bool:
        """Return `true` if the mapping is a submapping of another `LayoutModelMapping`, `false` otherwise"""
        return self.items() <= other.items()


class LayoutModelMappingBuilder(momapy.utils.SurjectionDict, momapy.builder.Builder):
    _cls_to_build: typing.ClassVar[type] = LayoutModelMapping

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_mapping(
        self,
        map_element: "momapy.core.elements.MapElement | tuple[momapy.core.elements.ModelElement, momapy.core.elements.ModelElement]",
    ):
        if map_element in self:
            return self[map_element]
        return self.inverse.get(map_element)

    def add_mapping(
        self,
        layout_element: "momapy.core.elements.LayoutElement",
        model_element: "momapy.core.elements.ModelElement | tuple[momapy.core.elements.ModelElement, momapy.core.elements.ModelElement]",
        replace=False,
    ):
        if replace:
            existing_layout_elements = self.get_mapping(model_element)
            if existing_layout_elements is not None:
                for existing_layout_element in existing_layout_elements:
                    del self[existing_layout_element]
                    self[existing_layout_element] = model_element
        self[layout_element] = model_element

    def build(
        self,
        builder_to_object: dict[int, typing.Any] | None = None,
    ):
        return self._cls_to_build(
            {
                momapy.builder.object_from_builder(
                    key, builder_to_object=builder_to_object
                ): momapy.builder.object_from_builder(
                    value, builder_to_object=builder_to_object
                )
                for key, value in self.items()
            }
        )

    @classmethod
    def from_object(
        cls,
        obj,
        omit_keys: bool = True,
        object_to_builder: "dict[int, momapy.builder.Builder] | None" = None,
    ) -> typing_extensions.Self:
        items = []
        for key, value in obj.items():
            if isinstance(key, frozenset):
                new_key = frozenset(
                    [
                        momapy.builder.builder_from_object(
                            element, object_to_builder=object_to_builder
                        )
                        for element in key
                    ]
                )
            else:
                new_key = momapy.builder.builder_from_object(
                    key, object_to_builder=object_to_builder
                )
            if isinstance(value, tuple):
                new_value = tuple(
                    [
                        momapy.builder.builder_from_object(
                            element, object_to_builder=object_to_builder
                        )
                        for element in value
                    ]
                )
            else:
                new_value = momapy.builder.builder_from_object(
                    value, object_to_builder=object_to_builder
                )
            items.append(
                (
                    new_key,
                    new_value,
                )
            )
        return cls(items)
