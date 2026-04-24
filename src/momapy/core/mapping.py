"""Layout-model mapping classes."""

import typing
import typing_extensions

import momapy.utils
import momapy.builder
import momapy.core.elements


class LayoutModelMapping(momapy.utils.FrozenSurjectionDict):
    """Mapping between model elements and layout elements.

    A [Map][momapy.core.Map] can draw the same model element several
    times, so the relation between layouts and model elements is a
    many-to-one mapping whose keys are layout elements and whose values
    are model elements. Two kinds of keys are used:

    - **Singleton key** — a single [LayoutElement][momapy.core.LayoutElement]
      that represents a model element on its own (a macromolecule
      glyph, a compartment, a state variable, a modulation arc when
      no cluster is needed).
    - **Frozenset key** — a ``frozenset`` of several layout elements
      that *jointly* represent one model element. Used whenever a
      model concept is drawn as a cluster of shapes: a process and
      its participant arcs and target layouts, a logical operator and
      its input arcs and targets, a modulation arc with its source and
      target clusters, a tag or terminal with its reference arcs.

    When the key is a frozenset, it is useful to designate one of the
    layouts as the **anchor** — the element that stands for the cluster
    on its own. The anchor is typically the "central" layout (the
    process glyph for a process, the operator glyph for a logical
    operator, the modulation arc for a modulation, the tag glyph for a
    tag). Anchors are registered through the ``anchor`` argument of
    [add_mapping][momapy.core.mapping.LayoutModelMappingBuilder.add_mapping]. Once registered,
    [get_mapping][momapy.core.mapping.LayoutModelMapping.get_mapping] resolves the anchor back to the model element
    stored under the frozenset key, and other composite keys can
    reference the cluster by its anchor rather than by the whole
    frozenset.

    See the SBGN-PD, SBGN-AF, and CellDesigner module documentation for
    the per-model-element catalogue of key shapes and anchors.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        object.__setattr__(
            self,
            "_singleton_to_key",
            momapy.utils.FrozenSurjectionDict(),
        )

    def get_mapping(
        self,
        map_element: "momapy.core.elements.MapElement",
    ) -> "momapy.core.elements.ModelElement | list[momapy.core.elements.LayoutElement]":
        """Return the model element or layout elements mapped to `map_element`.

        Lookup order:
        1. Direct key: `map_element` is a singleton or frozenset key in the
           mapping; returns the associated model element directly.
        2. Inverse: `map_element` is a model element; returns the list of
           layout elements (or frozenset keys) that map to it.
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

    def get_child_layout_elements(
        self,
        child_model_element: "momapy.core.elements.ModelElement",
        parent_model_element: "momapy.core.elements.ModelElement",
    ) -> "list[momapy.core.elements.LayoutElement]":
        """Return the layout elements representing ``child_model_element`` under ``parent_model_element``.

        Computes the intersection of two sets:

        - ``S1``: layouts that belong under ``parent_model_element`` — the
          children of each container layout mapped to the parent, plus the
          members of each frozenset key mapped to the parent.
        - ``S2``: layouts that represent ``child_model_element`` — each
          singleton layout mapped to the child, plus the anchors of each
          frozenset key mapped to the child.
        """
        child_s2 = set()
        for key in self.inverse.get(child_model_element, []):
            if isinstance(key, frozenset):
                for anchor in self._singleton_to_key.inverse.get(key, []):
                    child_s2.add(anchor)
            else:
                child_s2.add(key)
        parent_s1 = set()
        for parent_layout in self.inverse.get(parent_model_element, []):
            if isinstance(parent_layout, frozenset):
                parent_s1 |= parent_layout
            elif hasattr(parent_layout, "layout_elements"):
                parent_s1.update(parent_layout.layout_elements)
        return list(parent_s1 & child_s2)

    def is_submapping(self, other) -> bool:
        """Return `true` if the mapping is a submapping of another `LayoutModelMapping`, `false` otherwise"""
        return self.items() <= other.items()

    def __reduce__(self):
        """Pickle hook that preserves `_singleton_to_key` across round-trips.

        The inherited `frozendict.__reduce__` only serialises the dict
        contents, which drops the anchor table added by this subclass.
        """
        return (
            type(self),
            (dict(self),),
            {"_singleton_to_key": dict(self._singleton_to_key)},
        )

    def __setstate__(self, state):
        """Restore `_singleton_to_key` after `__reduce__`-driven unpickle."""
        object.__setattr__(
            self,
            "_singleton_to_key",
            momapy.utils.FrozenSurjectionDict(state["_singleton_to_key"]),
        )


class LayoutModelMappingBuilder(momapy.utils.SurjectionDict, momapy.builder.Builder):
    _cls_to_build: typing.ClassVar[type] = LayoutModelMapping

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._singleton_to_key = momapy.utils.SurjectionDict()

    def get_mapping(
        self,
        map_element: "momapy.core.elements.MapElement",
    ):
        if map_element in self:
            return self[map_element]
        return self.inverse.get(map_element)

    def get_child_layout_elements(
        self,
        child_model_element: "momapy.core.elements.ModelElement",
        parent_model_element: "momapy.core.elements.ModelElement",
    ) -> "list[momapy.core.elements.LayoutElement]":
        """Return the layout elements representing ``child_model_element`` under ``parent_model_element``."""
        child_s2 = set()
        for key in self.inverse.get(child_model_element, []):
            if isinstance(key, frozenset):
                for anchor in self._singleton_to_key.inverse.get(key, []):
                    child_s2.add(anchor)
            else:
                child_s2.add(key)
        parent_s1 = set()
        for parent_layout in self.inverse.get(parent_model_element, []):
            if isinstance(parent_layout, frozenset):
                parent_s1 |= parent_layout
            elif hasattr(parent_layout, "layout_elements"):
                parent_s1.update(parent_layout.layout_elements)
        return list(parent_s1 & child_s2)

    def add_mapping(
        self,
        layout_element: "momapy.core.elements.LayoutElement",
        model_element: "momapy.core.elements.ModelElement",
        replace: bool = False,
        anchor: "momapy.core.elements.LayoutElement | None" = None,
    ):
        """Add a layout-element to model-element entry to the mapping.

        Args:
            layout_element: The layout element (or frozenset of layout
                elements) to use as the key.
            model_element: The model element to associate with the layout
                element.
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
        singleton_to_key = momapy.utils.FrozenSurjectionDict(
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

    def __reduce__(self):
        """Pickle hook that preserves `_singleton_to_key` across round-trips.

        The default `dict`-subclass pickle emits SETITEMS before BUILD, so
        `SurjectionDict.__setitem__` fires before `_inverse` exists and
        crashes. Routing through `__init__` fixes both that and the
        `_singleton_to_key` loss.
        """
        return (
            type(self),
            (dict(self),),
            {"_singleton_to_key": dict(self._singleton_to_key)},
        )

    def __setstate__(self, state):
        """Restore `_singleton_to_key` after `__reduce__`-driven unpickle."""
        self._singleton_to_key = momapy.utils.SurjectionDict(state["_singleton_to_key"])

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
        singleton_to_key_items = {}
        for singleton, key in obj._singleton_to_key.items():
            new_singleton = momapy.builder.builder_from_object(
                singleton, object_to_builder=object_to_builder
            )
            if isinstance(key, frozenset):
                new_key = frozenset(
                    momapy.builder.builder_from_object(
                        element, object_to_builder=object_to_builder
                    )
                    for element in key
                )
            else:
                new_key = momapy.builder.builder_from_object(
                    key, object_to_builder=object_to_builder
                )
            singleton_to_key_items[new_singleton] = new_key
        builder._singleton_to_key = momapy.utils.SurjectionDict(singleton_to_key_items)
        return builder


momapy.builder.register_builder_cls(LayoutModelMappingBuilder)
