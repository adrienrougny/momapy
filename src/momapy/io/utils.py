"""Internal utilities for map readers.

These functions handle model element deduplication and stale reference
remapping during the read process.  They are not part of the public API.
"""

import dataclasses
import typing

import frozendict

import momapy.core.elements
import momapy.utils


@dataclasses.dataclass
class ReadingContext:
    """Base reading context shared by all format-specific readers.

    Holds the mappings and caches needed for model element registration,
    deduplication, and layout-model wiring.  Format-specific readers
    subclass this and add their own fields.
    """

    xml_root: typing.Any = None
    map_key: str | None = None
    model: typing.Any = None
    layout: typing.Any = None
    xml_id_to_model_element: momapy.utils.IdentitySurjectionDict = dataclasses.field(
        default_factory=momapy.utils.IdentitySurjectionDict
    )
    xml_id_to_layout_element: dict[str, momapy.core.elements.MapElement] = (
        dataclasses.field(default_factory=dict)
    )
    xml_id_to_xml_element: dict = dataclasses.field(default_factory=dict)
    element_to_annotations: dict = dataclasses.field(default_factory=dict)
    element_to_notes: dict = dataclasses.field(default_factory=dict)
    layout_model_mapping: typing.Any = None
    with_annotations: bool = True
    with_notes: bool = True
    model_element_cache: dict[
        momapy.core.elements.ModelElement, momapy.core.elements.ModelElement
    ] = dataclasses.field(default_factory=dict)
    model_element_remap: momapy.utils.IdentitySurjectionDict = dataclasses.field(
        default_factory=momapy.utils.IdentitySurjectionDict
    )
    """Maps id(evicted_object) -> surviving_object.  Uses
    IdentitySurjectionDict so chaining (finding all entries whose
    surviving element was itself evicted) is O(k) via inverse lookup."""
    evicted_elements: dict[int, momapy.core.elements.ModelElement] = dataclasses.field(
        default_factory=dict
    )
    """Maps id(evicted_object) -> evicted_object.  Keeps evicted objects
    alive to prevent Python from reusing their memory address."""


def collect_model_elements(
    model_element: momapy.core.elements.ModelElement,
) -> dict[str, momapy.core.elements.ModelElement]:
    """Recursively collect all model elements reachable via frozenset fields.

    Traverses the model element and its children (stored in frozenset
    and tuple fields) to build a mapping from momapy ``id_`` to element.

    Args:
        model_element: The root model element (typically the model itself).

    Returns:
        A dict mapping ``element.id_`` to element for all reachable
        model elements.
    """
    result: dict[str, momapy.core.elements.ModelElement] = {}

    def _collect(element):
        if not isinstance(element, momapy.core.elements.ModelElement):
            return
        if element.id_ in result:
            return
        result[element.id_] = element
        if not dataclasses.is_dataclass(element):
            return
        for field in dataclasses.fields(type(element)):
            value = getattr(element, field.name)
            if isinstance(value, (frozenset, tuple)):
                for child in value:
                    _collect(child)

    _collect(model_element)
    return result


def build_id_mappings(
    reading_context: "ReadingContext",
    frozen_obj: momapy.core.elements.MapElement,
    frozen_model: momapy.core.elements.ModelElement | None,
    frozen_layout: momapy.core.elements.LayoutElement | None,
    real_source_ids: set[str] | None = None,
) -> tuple[
    frozendict.frozendict,
    momapy.utils.FrozenSurjectionDict | None,
    momapy.utils.FrozenSurjectionDict | None,
]:
    """Build the three ID mapping dicts for a ReaderResult.

    Args:
        reading_context: The reading context with ``xml_id_to_model_element``
            and ``xml_id_to_layout_element`` (containing builder objects).
        frozen_obj: The frozen map/model/layout object.
        frozen_model: The frozen model, or None.
        frozen_layout: The frozen layout, or None.
        real_source_ids: If given, only source IDs in this set are
            included in the ``source_id_to_*`` dicts.  When None, all
            IDs from the reading context are treated as real.

    Returns:
        A tuple of ``(id_to_element, source_id_to_model_element,
        source_id_to_layout_element)``.
    """
    # 1. Build id_ → frozen element for all elements.
    id_to_element: dict[str, momapy.core.elements.MapElement] = {}
    if frozen_model is not None:
        id_to_element.update(collect_model_elements(frozen_model))
    if frozen_layout is not None:
        id_to_element[frozen_layout.id_] = frozen_layout
        for layout_element in frozen_layout.descendants():
            id_to_element[layout_element.id_] = layout_element
    # Include the top-level object itself (the map).
    if hasattr(frozen_obj, "id_"):
        id_to_element[frozen_obj.id_] = frozen_obj

    # 2. Build source_id → frozen model element.
    if frozen_model is not None:
        source_id_to_model: dict[str, momapy.core.elements.ModelElement] = {}
        for source_id, builder_element in reading_context.xml_id_to_model_element.items():
            if real_source_ids is not None and source_id not in real_source_ids:
                continue
            frozen_element = id_to_element.get(builder_element.id_)
            if frozen_element is not None:
                source_id_to_model[source_id] = frozen_element
        frozen_source_id_to_model = momapy.utils.FrozenSurjectionDict(
            source_id_to_model
        )
    else:
        frozen_source_id_to_model = None

    # 3. Build source_id → frozen layout element.
    if frozen_layout is not None:
        source_id_to_layout: dict[str, momapy.core.elements.LayoutElement] = {}
        for source_id, builder_element in reading_context.xml_id_to_layout_element.items():
            if real_source_ids is not None and source_id not in real_source_ids:
                continue
            frozen_element = id_to_element.get(builder_element.id_)
            if frozen_element is not None:
                source_id_to_layout[source_id] = frozen_element
        frozen_source_id_to_layout = momapy.utils.FrozenSurjectionDict(
            source_id_to_layout
        )
    else:
        frozen_source_id_to_layout = None

    return (
        frozendict.frozendict(id_to_element),
        frozen_source_id_to_model,
        frozen_source_id_to_layout,
    )


def remap_model_element(
    reading_context: ReadingContext,
    evicted_element: momapy.core.elements.ModelElement,
    surviving_element: momapy.core.elements.ModelElement,
) -> None:
    """Remap an evicted element and its children to the surviving ones.

    Scans reading_context.xml_id_to_model_element for entries pointing
    to the evicted element (by identity) and updates them.  Recurses
    into frozenset fields to remap children.  Accumulates remap in
    reading_context.model_element_remap for the final
    layout_model_mapping pass.

    Args:
        reading_context: The reading context holding all shared state.
        evicted_element: The element that lost deduplication.
        surviving_element: The element that won deduplication.
    """
    # Fix stale entries in xml_id_to_model_element via identity inverse.
    for xml_id in list(
        reading_context.xml_id_to_model_element.inverse.get(id(evicted_element), ())
    ):
        reading_context.xml_id_to_model_element[xml_id] = surviving_element
    # Chain: if earlier A→B and now B→C, update A→C.
    # Uses the remap's identity inverse to find all entries whose
    # surviving element is the current evicted element.
    for evicted_id in list(
        reading_context.model_element_remap.inverse.get(id(evicted_element), ())
    ):
        reading_context.model_element_remap[evicted_id] = surviving_element
    # Record this eviction.
    reading_context.model_element_remap[id(evicted_element)] = surviving_element
    reading_context.evicted_elements[id(evicted_element)] = evicted_element
    # Recurse into children stored in collection fields.
    if not dataclasses.is_dataclass(surviving_element):
        return
    for field in dataclasses.fields(type(surviving_element)):
        surviving_value = getattr(surviving_element, field.name)
        evicted_value = getattr(evicted_element, field.name)
        if isinstance(surviving_value, (frozenset, tuple)):
            for evicted_child in evicted_value:
                for surviving_child in surviving_value:
                    if (
                        evicted_child == surviving_child
                        and evicted_child is not surviving_child
                    ):
                        remap_model_element(
                            reading_context,
                            evicted_child,
                            surviving_child,
                        )
                        break
        elif isinstance(surviving_value, frozendict.frozendict):
            for evicted_child in evicted_value.values():
                for surviving_child in surviving_value.values():
                    if (
                        evicted_child == surviving_child
                        and evicted_child is not surviving_child
                    ):
                        remap_model_element(
                            reading_context,
                            evicted_child,
                            surviving_child,
                        )
                        break


def resolve_remap(
    element: momapy.core.elements.ModelElement,
    reading_context: ReadingContext,
) -> momapy.core.elements.ModelElement:
    """Return the surviving element if element was evicted, else element.

    Uses the evicted_elements dict to verify identity (prevents false
    matches from id() address reuse after garbage collection).

    Args:
        element: The element to resolve.
        reading_context: The reading context holding the remap.

    Returns:
        The surviving element if element was evicted, else element.
    """
    evicted_object = reading_context.evicted_elements.get(id(element))
    if evicted_object is not None and element is evicted_object:
        return reading_context.model_element_remap[id(element)]
    return element


def apply_remap_to_layout_model_mapping(
    reading_context: ReadingContext,
) -> None:
    """Update layout_model_mapping values that point to evicted elements.

    Args:
        reading_context: The reading context holding the remap and
            layout_model_mapping.
    """
    layout_model_mapping = reading_context.layout_model_mapping
    for layout_element in list(layout_model_mapping):
        model_element_key = layout_model_mapping[layout_element]
        if isinstance(model_element_key, tuple):
            new_model_element_key = tuple(
                resolve_remap(model_element, reading_context)
                for model_element in model_element_key
            )
            if any(
                new_model_element is not old_model_element
                for new_model_element, old_model_element in zip(
                    new_model_element_key, model_element_key
                )
            ):
                layout_model_mapping[layout_element] = new_model_element_key
        else:
            new_model_element_key = resolve_remap(model_element_key, reading_context)
            if new_model_element_key is not model_element_key:
                layout_model_mapping[layout_element] = new_model_element_key


def register_model_element(
    reading_context: ReadingContext,
    model_element: momapy.core.elements.ModelElement,
    collection: set,
    id_: str,
) -> momapy.core.elements.ModelElement:
    """Register a model element with incremental deduplication.

    If an equal element already exists in the collection, keeps the
    one with the smallest id_ and remaps stale references.
    Accumulates a remap for the final layout_model_mapping pass.

    Args:
        reading_context: The reading context holding all shared state.
        model_element: The element to register.
        collection: The model collection (e.g., model.species).
        id_: The XML id to register the element under.

    Returns:
        The surviving element (either the new one or the previously
        registered one, whichever has the smallest id_).
    """
    existing_element = reading_context.model_element_cache.get(model_element)
    surviving_element = momapy.utils.add_or_replace_element_in_set(
        model_element,
        collection,
        func=lambda new, old: new.id_ < old.id_,
        cache=reading_context.model_element_cache,
    )
    reading_context.xml_id_to_model_element[id_] = surviving_element
    if existing_element is not None:
        evicted_element = (
            model_element
            if model_element is not surviving_element
            else existing_element
        )
        remap_model_element(reading_context, evicted_element, surviving_element)
    return surviving_element
