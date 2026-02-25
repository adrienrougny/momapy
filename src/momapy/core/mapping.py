"""Layout-model mapping classes."""

import typing
import typing_extensions

import frozendict

import momapy.utils
import momapy.builder
import momapy.core.elements


class LayoutModelMapping(momapy.utils.FrozenSurjectionDict):
    """Class for mappings between model elements and layout elements"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        object.__setattr__(
            self,
            "_singleton_to_key",
            frozendict.frozendict(),
        )

    def get_mapping(
        self,
        map_element: "momapy.core.elements.MapElement | tuple[momapy.core.elements.ModelElement, momapy.core.elements.ModelElement]",
    ) -> "momapy.core.elements.ModelElement | list[momapy.core.elements.LayoutElement]":
        """Return the model element or layout elements mapped to `map_element`.

        Lookup order:
        1. Direct key: `map_element` is a singleton or frozenset key in the
           mapping; returns the associated model element directly.
        2. Inverse: `map_element` is a model element (or tuple thereof);
           returns the list of layout elements (or frozenset keys) that map
           to it.
        3. Anchor fallback: `map_element` was registered as the anchor of a
           frozenset key via the ``anchor`` argument of ``add_mapping``;
           returns the model element stored under that frozenset key.

        Returns ``None`` when no match is found.
        """
        if map_element in self:
            return self[map_element]
        result = self.inverse.get(map_element)
        if result is not None:
            return result
        key = self._singleton_to_key.get(map_element)
        if key is not None:
            return self[key]
        return None

    def is_submapping(self, other) -> bool:
        """Return `true` if the mapping is a submapping of another `LayoutModelMapping`, `false` otherwise"""
        return self.items() <= other.items()


class LayoutModelMappingBuilder(momapy.utils.SurjectionDict, momapy.builder.Builder):
    _cls_to_build: typing.ClassVar[type] = LayoutModelMapping

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._singleton_to_key = {}

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
        anchor=None,
    ):
        """Add a layout-element to model-element entry to the mapping.

        Args:
            layout_element: The layout element (or frozenset of layout
                elements) to use as the key.
            model_element: The model element (or tuple of model elements)
                to associate with the layout element.
            replace: When ``True`` and a mapping for ``model_element``
                already exists, the existing layout elements are re-mapped
                before adding the new entry.
            anchor: When ``layout_element`` is a frozenset and this argument
                is provided, registers ``anchor`` as the anchor of the
                frozenset key. This allows ``get_mapping(anchor)`` to resolve
                to the model element stored under the frozenset key, even when
                the same element participates in other frozensets (e.g. a
                logical operator that is both the anchor of its own gate
                frozenset and a participant in a modulation frozenset).
        """
        if replace:
            existing_layout_elements = self.get_mapping(model_element)
            if existing_layout_elements is not None:
                for existing_layout_element in existing_layout_elements:
                    del self[existing_layout_element]
                    self[existing_layout_element] = model_element
        self[layout_element] = model_element
        if anchor is not None:
            self._singleton_to_key[anchor] = layout_element

    def build(
        self,
        builder_to_object: dict[int, typing.Any] | None = None,
    ):
        mapping = self._cls_to_build(
            {
                momapy.builder.object_from_builder(
                    key, builder_to_object=builder_to_object
                ): momapy.builder.object_from_builder(
                    value, builder_to_object=builder_to_object
                )
                for key, value in self.items()
            }
        )
        singleton_to_key = frozendict.frozendict(
            {
                momapy.builder.object_from_builder(
                    singleton, builder_to_object=builder_to_object
                ): momapy.builder.object_from_builder(
                    key, builder_to_object=builder_to_object
                )
                for singleton, key in self._singleton_to_key.items()
            }
        )
        object.__setattr__(mapping, "_singleton_to_key", singleton_to_key)
        return mapping

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
        builder = cls(items)
        builder._singleton_to_key = {
            momapy.builder.builder_from_object(
                singleton, object_to_builder=object_to_builder
            ): momapy.builder.builder_from_object(
                key, object_to_builder=object_to_builder
            )
            for singleton, key in obj._singleton_to_key.items()
        }
        return builder
