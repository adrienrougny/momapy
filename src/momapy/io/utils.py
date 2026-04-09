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
    model: typing.Any = None
    layout: typing.Any = None
    xml_id_to_model_element: momapy.utils.IdentitySurjectionDict = dataclasses.field(
        default_factory=momapy.utils.IdentitySurjectionDict
    )
    xml_id_to_layout_element: dict[str, momapy.core.elements.MapElement] = (
        dataclasses.field(default_factory=dict)
    )
    xml_id_to_xml_element: dict = dataclasses.field(default_factory=dict)
    map_element_to_annotations: dict = dataclasses.field(default_factory=dict)
    map_element_to_notes: dict = dataclasses.field(default_factory=dict)
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
