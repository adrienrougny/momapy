"""SBGN-ML writer classes.

Model-first approach: iterates model collections in dependency order,
looking up layout elements via layout_model_mapping.
"""

import os
import typing

import lxml.etree

from momapy.core.layout import DoubleHeadedArc
from momapy.core.layout import Node
from momapy.core.layout import SingleHeadedArc
from momapy.io.core import Writer
from momapy.io.core import WriterResult
from momapy.io.utils import WritingContext
from momapy.io.utils import make_unique_xml_id
from momapy.utils import check_parent_dir_exists
from momapy.sbgn import SBGNMap
from momapy.sbgn.pd import ConsumptionLayout
from momapy.sbgn.pd import EmptySetLayout
from momapy.sbgn.pd import EntityPool
from momapy.sbgn.pd import LogicArcLayout as PDLogicArcLayout
from momapy.sbgn.pd import Phenotype
from momapy.sbgn.pd import ProductionLayout
from momapy.sbgn.pd import SBGNPDModel
from momapy.sbgn.pd import StateVariableLayout
from momapy.sbgn.pd import StoichiometricProcess
from momapy.sbgn.af import Activity
from momapy.sbgn.af import LogicArcLayout as AFLogicArcLayout
from momapy.sbgn.io.sbgnml._writing import NSMAP
from momapy.sbgn.io.sbgnml._writing import add_annotations_and_notes
from momapy.sbgn.io.sbgnml._writing import ensure_ncname
from momapy.sbgn.io.sbgnml._writing import make_lxml_element
from momapy.sbgn.io.sbgnml._writing import make_sbgnml_bbox_from_node
from momapy.sbgn.io.sbgnml._writing import make_sbgnml_entity
from momapy.sbgn.io.sbgnml._writing import make_sbgnml_label
from momapy.sbgn.io.sbgnml._writing import make_sbgnml_points
from momapy.sbgn.io.sbgnml._writing import make_sbgnml_port
from momapy.sbgn.io.sbgnml._writing import make_sbgnml_state
from momapy.sbgn.io.sbgnml._writing_classification import CLASS_TO_SBGNML_CLASS
from momapy.sbgn.io.sbgnml._writing_classification import CLASS_TO_SBGNML_ENTITY_NAME
from momapy.sbgn.io.sbgnml._writing_classification import (
    DIRECTION_TO_SBGNML_ORIENTATION,
)
from momapy.sbgn.io.sbgnml._writing_classification import REVERSED_ARC_TYPES


# ---------------------------------------------------------------------------
# Id projection
# ---------------------------------------------------------------------------


def _reserve_source_xml_ids(writing_context):
    """Reserve grammar-valid source ids before any projection (phase 1).

    For every layout element that carries a source id, reserve that id
    verbatim in ``element_to_xml_id`` (and mark it used) when it is
    already a valid NCName.  Reserving up front, *without* deduplication,
    preserves round-trip fidelity and lets several elements that share a
    source id keep sharing the emitted id.  Must run before any id is
    emitted.

    Args:
        writing_context: The current writing context.
    """
    source_map = writing_context.source_id_to_layout_element
    if source_map is None:
        return
    element_id_to_source_ids = {}
    for source_id, layout_element in source_map.items():
        if not source_id:
            continue
        element_id_to_source_ids.setdefault(id(layout_element), set()).add(source_id)
    for element_id, source_ids in element_id_to_source_ids.items():
        chosen = min(source_ids, key=lambda source_id: (len(source_id), source_id))
        if ensure_ncname(chosen) == chosen:
            writing_context.element_to_xml_id[element_id] = chosen
            writing_context.used_xml_ids.add(chosen)


def _get_xml_id(writing_context, element):
    """Return the unique, valid NCName id to emit for ``element`` (phase 2).

    Hits the phase-1 memo first (source ids reserved verbatim); on a
    miss, projects ``id_`` to NCName, makes it unique, and memoises so
    every definition and reference of the element agree.  This single
    chokepoint is what enforces id uniqueness and consistency.

    Args:
        writing_context: The current writing context.
        element: Any map element with an ``id_`` (layout element or map).

    Returns:
        The XML id string to emit.
    """
    element_id = id(element)
    existing = writing_context.element_to_xml_id.get(element_id)
    if existing is not None:
        return existing
    projected = ensure_ncname(element.id_)
    final = make_unique_xml_id(projected, writing_context.used_xml_ids)
    writing_context.element_to_xml_id[element_id] = final
    return final


# ---------------------------------------------------------------------------
# Helpers for layout lookup
# ---------------------------------------------------------------------------


def _get_layout_elements(writing_context, model_element):
    """Get all layout elements for a model element.

    Returns singleton layouts plus the anchors of any frozenset keys
    mapped to the model element. Duplicates are removed while preserving
    order.

    Args:
        writing_context: The current writing context.
        model_element: The model element to look up.

    Returns:
        A list of layout elements (may be empty).
    """
    mapping = writing_context.map_.layout_model_mapping
    result = mapping.get_mapping(model_element)
    if result is None or not isinstance(result, list):
        return []
    layout_elements = []
    seen = set()
    for item in result:
        if isinstance(item, frozenset):
            for anchor in mapping._singleton_to_key.inverse.get(item, []):
                if anchor not in seen:
                    seen.add(anchor)
                    layout_elements.append(anchor)
        else:
            if item not in seen:
                seen.add(item)
                layout_elements.append(item)
    return layout_elements


def _get_frozenset_keys(writing_context, model_element):
    """Get all frozenset mapping keys for a process, modulation or operator.

    Args:
        writing_context: The current writing context.
        model_element: The model element to look up.

    Returns:
        A list of frozenset keys (may be empty).
    """
    result = writing_context.map_.layout_model_mapping.get_mapping(model_element)
    if result is None or not isinstance(result, list):
        return []
    return [item for item in result if isinstance(item, frozenset)]


def _get_child_layout_element(writing_context, child_model, parent_model):
    """Get the layout element for a child model element.

    Args:
        writing_context: The current writing context.
        child_model: The child model element.
        parent_model: The parent model element.

    Returns:
        The layout element, or ``None``.
    """
    layout_elements = (
        writing_context.map_.layout_model_mapping.get_child_layout_elements(
            child_model, parent_model
        )
    )
    if layout_elements:
        return layout_elements[0]
    return None


# ---------------------------------------------------------------------------
# Core glyph/arc builders
# ---------------------------------------------------------------------------


def _make_sbgnml_glyph(writing_context, layout_element, model_element=None):
    """Create a ``<glyph>`` XML element from a layout element.

    Handles id, class, orientation, compartmentRef, bbox, label/state,
    and ports.

    Args:
        writing_context: The current writing context.
        layout_element: The layout element to serialize.
        model_element: Optional associated model element (for compartmentRef).

    Returns:
        The lxml ``<glyph>`` element.
    """
    sbgnml_id = _get_xml_id(writing_context, layout_element)
    sbgnml_class = CLASS_TO_SBGNML_CLASS[type(layout_element)]
    attributes = {"id": sbgnml_id, "class": sbgnml_class}
    direction = getattr(layout_element, "direction", None)
    if direction is not None:
        sbgnml_orientation = DIRECTION_TO_SBGNML_ORIENTATION[direction]
        attributes["orientation"] = sbgnml_orientation
    if model_element is not None and isinstance(
        model_element,
        (EntityPool, Activity),
    ):
        compartment = model_element.compartment
        if compartment is not None:
            compartment_layout_elements = _get_layout_elements(
                writing_context, compartment
            )
            if compartment_layout_elements:
                compartment_id = _get_xml_id(
                    writing_context, compartment_layout_elements[0]
                )
                attributes["compartmentRef"] = compartment_id
    sbgnml_glyph = make_lxml_element("glyph", attributes=attributes)
    entity_name = CLASS_TO_SBGNML_ENTITY_NAME.get(type(layout_element))
    if entity_name is not None:
        sbgnml_entity = make_sbgnml_entity(entity_name)
        sbgnml_glyph.append(sbgnml_entity)
    sbgnml_bbox = make_sbgnml_bbox_from_node(layout_element)
    sbgnml_glyph.append(sbgnml_bbox)
    if layout_element.label is not None:
        if isinstance(layout_element, StateVariableLayout):
            sbgnml_state = make_sbgnml_state(layout_element.label)
            sbgnml_glyph.append(sbgnml_state)
        else:
            sbgnml_label = make_sbgnml_label(layout_element.label)
            sbgnml_glyph.append(sbgnml_label)
    for side, attr in [
        ("left", "left_connector_tip"),
        ("right", "right_connector_tip"),
    ]:
        if hasattr(layout_element, attr):
            connector_tip = getattr(layout_element, attr)()
            sbgnml_port = make_sbgnml_port(connector_tip, port_id=f"{sbgnml_id}_{side}")
            sbgnml_glyph.append(sbgnml_port)
    return sbgnml_glyph


def _make_sbgnml_arc_element(writing_context, arc_layout):
    """Create an ``<arc>`` XML element from an arc layout element.

    Handles id, class, source, target, points, and direction reversal
    for arc types whose direction is inverted in momapy.

    Args:
        writing_context: The current writing context.
        arc_layout: The arc layout element.

    Returns:
        The lxml ``<arc>`` element.
    """
    sbgnml_id = _get_xml_id(writing_context, arc_layout)
    sbgnml_class = CLASS_TO_SBGNML_CLASS[type(arc_layout)]
    attributes = {"id": sbgnml_id, "class": sbgnml_class}
    points = arc_layout.points()
    sbgnml_source_id = _get_xml_id(writing_context, arc_layout.source)
    sbgnml_target_id = _get_xml_id(writing_context, arc_layout.target)
    if isinstance(
        arc_layout,
        REVERSED_ARC_TYPES,
    ):
        attributes["source"] = sbgnml_target_id
        attributes["target"] = sbgnml_source_id
        points.reverse()
    else:
        attributes["source"] = sbgnml_source_id
        attributes["target"] = sbgnml_target_id
    sbgnml_arc = make_lxml_element("arc", attributes=attributes)
    sbgnml_points = make_sbgnml_points(points)
    for sbgnml_point in sbgnml_points:
        sbgnml_arc.append(sbgnml_point)
    return sbgnml_arc


def _make_sbgnml_child_glyphs(writing_context, layout_element, model_element):
    """Create child ``<glyph>`` elements for auxiliary units (state vars,
    UOIs, subunits, terminals) of a node.

    This walks the ``layout_elements`` of the *layout_element* and creates
    sub-glyphs for each child node.

    Args:
        writing_context: The current writing context.
        layout_element: The parent layout element.
        model_element: The parent model element (used for mapping lookups).

    Returns:
        A list of child glyph lxml elements.
    """
    child_glyphs = []
    for child_layout in layout_element.layout_elements:
        if isinstance(child_layout, Node):
            child_glyph = _make_sbgnml_glyph(
                writing_context, child_layout, model_element=None
            )
            # Recursively add grandchildren (e.g., subunit auxiliary units)
            sub_children = _make_sbgnml_child_glyphs(
                writing_context, child_layout, model_element
            )
            for sub_child in sub_children:
                child_glyph.append(sub_child)
            child_glyphs.append(child_glyph)
    return child_glyphs


# ---------------------------------------------------------------------------
# Map orchestrator
# ---------------------------------------------------------------------------


def _collect_model_elements(writing_context):
    """Build a dict mapping layout elements to their serialized XML elements.

    Iterates model collections in dependency order, serializes each
    model element via the appropriate ``make_sbgnml_*`` function, and
    collects the resulting XML elements keyed by the layout element
    they originate from.

    Args:
        writing_context: The current writing context.

    Returns:
        A dict ``{layout_element: [lxml_element, ...]}``.
    """
    layout_to_xml = {}
    model = writing_context.map_.model
    is_pd = isinstance(model, SBGNPDModel)

    def _register(layout_el, sbgnml_el):
        layout_to_xml.setdefault(layout_el, []).append(sbgnml_el)

    # 1. Compartments
    for compartment in model.compartments:
        for layout_el in _get_layout_elements(writing_context, compartment):
            sbgnml_glyph = _make_sbgnml_glyph(
                writing_context, layout_el, model_element=compartment
            )
            for child_glyph in _make_sbgnml_child_glyphs(
                writing_context, layout_el, compartment
            ):
                sbgnml_glyph.append(child_glyph)
            add_annotations_and_notes(writing_context, sbgnml_glyph, compartment)
            _register(layout_el, sbgnml_glyph)

    # 2. Entity pools (PD) or Activities (AF)
    if is_pd:
        for entity_pool in model.entity_pools:
            for layout_el in _get_layout_elements(writing_context, entity_pool):
                sbgnml_glyph = _make_sbgnml_glyph(
                    writing_context, layout_el, model_element=entity_pool
                )
                for child_glyph in _make_sbgnml_child_glyphs(
                    writing_context, layout_el, entity_pool
                ):
                    sbgnml_glyph.append(child_glyph)
                add_annotations_and_notes(writing_context, sbgnml_glyph, entity_pool)
                _register(layout_el, sbgnml_glyph)
        # 2b. Empty sets — no model element. Driven by the
        # has_external_source / has_external_sink flags on processes:
        # find every EmptySetLayout in a flagged process's frozenset key
        # and emit a glyph for it.
        seen_empty_set_layouts = set()
        for process in model.processes:
            if not isinstance(process, StoichiometricProcess):
                continue
            if not (process.has_external_source or process.has_external_sink):
                continue
            for frozenset_key in _get_frozenset_keys(writing_context, process):
                for item in frozenset_key:
                    if isinstance(item, EmptySetLayout):
                        if item in seen_empty_set_layouts:
                            continue
                        seen_empty_set_layouts.add(item)
                        sbgnml_glyph = _make_sbgnml_glyph(
                            writing_context, item, model_element=None
                        )
                        _register(item, sbgnml_glyph)
    else:
        for activity in model.activities:
            for layout_el in _get_layout_elements(writing_context, activity):
                sbgnml_glyph = _make_sbgnml_glyph(
                    writing_context, layout_el, model_element=activity
                )
                for child_glyph in _make_sbgnml_child_glyphs(
                    writing_context, layout_el, activity
                ):
                    sbgnml_glyph.append(child_glyph)
                add_annotations_and_notes(writing_context, sbgnml_glyph, activity)
                _register(layout_el, sbgnml_glyph)

    # 3. Logical operators (with logic arcs)
    singleton_to_key = writing_context.map_.layout_model_mapping._singleton_to_key
    for logical_operator in model.logical_operators:
        for frozenset_key in _get_frozenset_keys(writing_context, logical_operator):
            operator_layout = None
            arc_layouts = []
            for item in frozenset_key:
                if isinstance(
                    item,
                    (
                        PDLogicArcLayout,
                        AFLogicArcLayout,
                    ),
                ):
                    arc_layouts.append(item)
                elif (
                    isinstance(item, Node)
                    and singleton_to_key.get(item) == frozenset_key
                ):
                    operator_layout = item
            if operator_layout is None:
                continue
            sbgnml_glyph = _make_sbgnml_glyph(
                writing_context,
                operator_layout,
                model_element=logical_operator,
            )
            add_annotations_and_notes(writing_context, sbgnml_glyph, logical_operator)
            _register(operator_layout, sbgnml_glyph)
            for arc_layout in arc_layouts:
                sbgnml_arc = _make_sbgnml_arc_element(writing_context, arc_layout)
                _register(arc_layout, sbgnml_arc)

    # 4. Submaps (with terminals and equivalence arcs)
    for submap in model.submaps:
        for layout_el in _get_layout_elements(writing_context, submap):
            sbgnml_glyph = _make_sbgnml_glyph(
                writing_context, layout_el, model_element=submap
            )
            for child_glyph in _make_sbgnml_child_glyphs(
                writing_context, layout_el, submap
            ):
                sbgnml_glyph.append(child_glyph)
            add_annotations_and_notes(writing_context, sbgnml_glyph, submap)
            _register(layout_el, sbgnml_glyph)
        if hasattr(submap, "terminals"):
            for terminal in submap.terminals:
                if (
                    hasattr(terminal, "referred_element")
                    and terminal.referred_element is not None
                ):
                    reference_layout = _get_child_layout_element(
                        writing_context, terminal.referred_element, terminal
                    )
                    if reference_layout is not None and isinstance(
                        reference_layout,
                        (
                            SingleHeadedArc,
                            DoubleHeadedArc,
                        ),
                    ):
                        sbgnml_arc = _make_sbgnml_arc_element(
                            writing_context, reference_layout
                        )
                        _register(reference_layout, sbgnml_arc)

    # 5. Tags (with equivalence arcs)
    for tag in model.tags:
        for layout_el in _get_layout_elements(writing_context, tag):
            sbgnml_glyph = _make_sbgnml_glyph(
                writing_context, layout_el, model_element=tag
            )
            for child_glyph in _make_sbgnml_child_glyphs(
                writing_context, layout_el, tag
            ):
                sbgnml_glyph.append(child_glyph)
            add_annotations_and_notes(writing_context, sbgnml_glyph, tag)
            _register(layout_el, sbgnml_glyph)
        if hasattr(tag, "referred_element") and tag.referred_element is not None:
            reference_layout = _get_child_layout_element(
                writing_context, tag.referred_element, tag
            )
            if reference_layout is not None and isinstance(
                reference_layout,
                (
                    SingleHeadedArc,
                    DoubleHeadedArc,
                ),
            ):
                sbgnml_arc = _make_sbgnml_arc_element(writing_context, reference_layout)
                _register(reference_layout, sbgnml_arc)

    # 6. Processes
    if is_pd:
        for process in model.processes:
            if isinstance(process, Phenotype):
                for layout_el in _get_layout_elements(writing_context, process):
                    sbgnml_glyph = _make_sbgnml_glyph(
                        writing_context, layout_el, model_element=process
                    )
                    for child_glyph in _make_sbgnml_child_glyphs(
                        writing_context, layout_el, process
                    ):
                        sbgnml_glyph.append(child_glyph)
                    add_annotations_and_notes(writing_context, sbgnml_glyph, process)
                    _register(layout_el, sbgnml_glyph)
            elif isinstance(process, StoichiometricProcess):
                for frozenset_key in _get_frozenset_keys(writing_context, process):
                    process_layout = None
                    arc_layouts = []
                    for item in frozenset_key:
                        if isinstance(
                            item,
                            (
                                ConsumptionLayout,
                                ProductionLayout,
                            ),
                        ):
                            arc_layouts.append(item)
                        elif (
                            isinstance(item, Node)
                            and singleton_to_key.get(item) == frozenset_key
                        ):
                            process_layout = item
                    if process_layout is None:
                        continue
                    sbgnml_glyph = _make_sbgnml_glyph(
                        writing_context,
                        process_layout,
                        model_element=process,
                    )
                    for child_glyph in _make_sbgnml_child_glyphs(
                        writing_context, process_layout, process
                    ):
                        sbgnml_glyph.append(child_glyph)
                    add_annotations_and_notes(writing_context, sbgnml_glyph, process)
                    _register(process_layout, sbgnml_glyph)
                    for arc_layout in arc_layouts:
                        sbgnml_arc = _make_sbgnml_arc_element(
                            writing_context, arc_layout
                        )
                        _register(arc_layout, sbgnml_arc)

    # 7. Modulations (PD) or Influences (AF)
    modulations = model.modulations if is_pd else model.influences
    for modulation in modulations:
        for frozenset_key in _get_frozenset_keys(writing_context, modulation):
            arc_layout = None
            for item in frozenset_key:
                if singleton_to_key.get(item) == frozenset_key:
                    arc_layout = item
                    break
            if arc_layout is None:
                continue
            sbgnml_arc = _make_sbgnml_arc_element(writing_context, arc_layout)
            add_annotations_and_notes(writing_context, sbgnml_arc, modulation)
            _register(arc_layout, sbgnml_arc)

    return layout_to_xml


def make_sbgnml_map(writing_context):
    """Build the ``<map>`` XML element using a model-first traversal.

    Phase 1: iterates model collections in dependency order, serializes
    each model element and collects XML keyed by layout element.
    Phase 2: iterates ``layout.layout_elements`` in order and appends
    the collected XML to the ``<map>``, preserving the original ordering.

    Args:
        writing_context: The current writing context.

    Returns:
        The lxml ``<map>`` element.
    """
    map_ = writing_context.map_
    _reserve_source_xml_ids(writing_context)
    language = CLASS_TO_SBGNML_CLASS[type(map_)]
    id_ = _get_xml_id(writing_context, map_)
    attributes = {"id": id_, "language": language}
    sbgnml_map = make_lxml_element("map", attributes=attributes)
    sbgnml_bbox = make_sbgnml_bbox_from_node(map_.layout)
    sbgnml_map.append(sbgnml_bbox)

    # Phase 1: model-first serialization
    layout_to_xml = _collect_model_elements(writing_context)

    # Phase 2: output in layout order
    for layout_element in map_.layout.layout_elements:
        xml_elements = layout_to_xml.get(layout_element)
        if xml_elements is not None:
            for xml_el in xml_elements:
                sbgnml_map.append(xml_el)

    return sbgnml_map


# ---------------------------------------------------------------------------
# Writer classes
# ---------------------------------------------------------------------------


class _SBGNMLWriter(Writer):
    """Base SBGN-ML writer.

    All serialization logic lives in module-level functions.  This class
    only provides the ``write`` entry point.
    """

    @classmethod
    def write(
        cls,
        obj: SBGNMap,
        file_path: str | os.PathLike,
        element_to_annotations: dict | None = None,
        element_to_notes: dict | None = None,
        source_id_to_model_element: dict | None = None,
        source_id_to_layout_element: dict | None = None,
        source_id_to_annotations: dict | None = None,
        source_id_to_notes: dict | None = None,
        with_annotations: bool = True,
        with_notes: bool = True,
        **options: typing.Any,
    ) -> WriterResult:
        """Write an SBGN map to an SBGN-ML file.

        Args:
            obj: The SBGN map to serialize.
            file_path: Destination file path.
            element_to_annotations: Optional per-element annotation dict.
            element_to_notes: Optional per-element notes dict.
            source_id_to_model_element: Optional source ID to model
                element mapping from ReaderResult.
            source_id_to_layout_element: Optional source ID to layout
                element mapping from ReaderResult.
            source_id_to_annotations: Optional per-source-id annotations
                from ReaderResult.
            source_id_to_notes: Optional per-source-id notes from
                ReaderResult.
            with_annotations: Whether to write annotations.
            with_notes: Whether to write notes.
            options: Additional options (accepted and ignored).

        Returns:
            WriterResult containing the written object and file path.
        """
        check_parent_dir_exists(file_path)
        if element_to_annotations is None:
            element_to_annotations = {}
        if element_to_notes is None:
            element_to_notes = {}
        writing_context = WritingContext(
            map_=obj,
            element_to_annotations=element_to_annotations,
            element_to_notes=element_to_notes,
            source_id_to_model_element=source_id_to_model_element,
            source_id_to_layout_element=source_id_to_layout_element,
            source_id_to_annotations=source_id_to_annotations,
            source_id_to_notes=source_id_to_notes,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        sbgnml_sbgn = make_lxml_element("sbgn", nsmap=NSMAP)
        sbgnml_map = make_sbgnml_map(writing_context)
        sbgnml_sbgn.append(sbgnml_map)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(
                lxml.etree.tostring(
                    sbgnml_sbgn, pretty_print=True, xml_declaration=True
                ).decode()
            )
        return WriterResult(obj=obj, file_path=file_path)


class SBGNML0_3Writer(_SBGNMLWriter):
    """Class for SBGN-ML 0.3 writer objects."""

    pass
