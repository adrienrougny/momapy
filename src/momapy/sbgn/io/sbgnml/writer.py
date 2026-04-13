"""SBGN-ML writer classes.

Model-first approach: iterates model collections in dependency order,
looking up layout elements via layout_model_mapping.
"""

import dataclasses
import typing

import lxml.etree

import momapy.core.elements
import momapy.core.layout
import momapy.io.core
import momapy.sbgn.core
import momapy.sbgn.pd
import momapy.sbgn.af
import momapy.sbgn.io.sbgnml._writing
import momapy.sbgn.io.sbgnml._writing_classification


@dataclasses.dataclass
class WritingContext:
    """Bundles the shared state passed across all writer methods."""

    map_: typing.Any
    annotations: dict
    notes: dict
    ids: dict
    with_annotations: bool
    with_notes: bool


# ---------------------------------------------------------------------------
# Helpers for layout lookup
# ---------------------------------------------------------------------------


def _get_layout_elements(writing_context, model_element):
    """Get all layout elements for a model element.

    Returns only non-frozenset items from the inverse mapping lookup.

    Args:
        writing_context: The current writing context.
        model_element: The model element to look up.

    Returns:
        A list of layout elements (may be empty).
    """
    result = writing_context.map_.layout_model_mapping.get_mapping(
        model_element
    )
    if result is None or not isinstance(result, list):
        return []
    return [item for item in result if not isinstance(item, frozenset)]


def _get_frozenset_keys(writing_context, model_element):
    """Get all frozenset mapping keys for a process, modulation or operator.

    Args:
        writing_context: The current writing context.
        model_element: The model element to look up.

    Returns:
        A list of frozenset keys (may be empty).
    """
    result = writing_context.map_.layout_model_mapping.get_mapping(
        model_element
    )
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
    result = writing_context.map_.layout_model_mapping.get_mapping(
        (child_model, parent_model)
    )
    if result is None:
        return None
    if isinstance(result, list):
        for item in result:
            if not isinstance(item, frozenset):
                return item
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
    sbgnml_id = momapy.sbgn.io.sbgnml._writing.get_sbgnml_id(
        layout_element, writing_context.ids
    )
    sbgnml_class = (
        momapy.sbgn.io.sbgnml._writing_classification.CLASS_TO_SBGNML_CLASS[
            type(layout_element)
        ]
    )
    attributes = {"id": sbgnml_id, "class": sbgnml_class}
    direction = getattr(layout_element, "direction", None)
    if direction is not None:
        sbgnml_orientation = (
            momapy.sbgn.io.sbgnml._writing_classification.DIRECTION_TO_SBGNML_ORIENTATION[
                direction
            ]
        )
        attributes["orientation"] = sbgnml_orientation
    if model_element is not None and isinstance(
        model_element,
        (momapy.sbgn.pd.EntityPool, momapy.sbgn.af.Activity),
    ):
        compartment = model_element.compartment
        if compartment is not None:
            compartment_id = momapy.sbgn.io.sbgnml._writing.get_sbgnml_id(
                compartment, writing_context.ids
            )
            attributes["compartmentRef"] = compartment_id
    sbgnml_glyph = momapy.sbgn.io.sbgnml._writing.make_lxml_element(
        "glyph", attributes=attributes
    )
    sbgnml_bbox = momapy.sbgn.io.sbgnml._writing.make_sbgnml_bbox_from_node(
        layout_element
    )
    sbgnml_glyph.append(sbgnml_bbox)
    if layout_element.label is not None:
        if isinstance(layout_element, momapy.sbgn.pd.StateVariableLayout):
            sbgnml_state = momapy.sbgn.io.sbgnml._writing.make_sbgnml_state(
                layout_element.label
            )
            sbgnml_glyph.append(sbgnml_state)
        else:
            sbgnml_label = momapy.sbgn.io.sbgnml._writing.make_sbgnml_label(
                layout_element.label
            )
            sbgnml_glyph.append(sbgnml_label)
    for side, attr in [
        ("left", "left_connector_tip"),
        ("right", "right_connector_tip"),
    ]:
        if hasattr(layout_element, attr):
            connector_tip = getattr(layout_element, attr)()
            sbgnml_port = momapy.sbgn.io.sbgnml._writing.make_sbgnml_port(
                connector_tip, port_id=f"{sbgnml_id}_{side}"
            )
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
    sbgnml_id = momapy.sbgn.io.sbgnml._writing.get_sbgnml_id(
        arc_layout, writing_context.ids
    )
    sbgnml_class = (
        momapy.sbgn.io.sbgnml._writing_classification.CLASS_TO_SBGNML_CLASS[
            type(arc_layout)
        ]
    )
    attributes = {"id": sbgnml_id, "class": sbgnml_class}
    points = arc_layout.points()
    sbgnml_source_id = momapy.sbgn.io.sbgnml._writing.get_sbgnml_id(
        arc_layout.source, writing_context.ids
    )
    sbgnml_target_id = momapy.sbgn.io.sbgnml._writing.get_sbgnml_id(
        arc_layout.target, writing_context.ids
    )
    if isinstance(
        arc_layout,
        momapy.sbgn.io.sbgnml._writing_classification.REVERSED_ARC_TYPES,
    ):
        attributes["source"] = sbgnml_target_id
        attributes["target"] = sbgnml_source_id
        points.reverse()
    else:
        attributes["source"] = sbgnml_source_id
        attributes["target"] = sbgnml_target_id
    sbgnml_arc = momapy.sbgn.io.sbgnml._writing.make_lxml_element(
        "arc", attributes=attributes
    )
    sbgnml_points = momapy.sbgn.io.sbgnml._writing.make_sbgnml_points(points)
    for sbgnml_point in sbgnml_points:
        sbgnml_arc.append(sbgnml_point)
    return sbgnml_arc


def _make_sbgnml_child_glyphs(
    writing_context, layout_element, model_element
):
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
        if isinstance(child_layout, momapy.core.layout.Node):
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
    is_pd = isinstance(model, momapy.sbgn.pd.SBGNPDModel)

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
            momapy.sbgn.io.sbgnml._writing.add_annotations_and_notes(
                writing_context, sbgnml_glyph, compartment
            )
            _register(layout_el, sbgnml_glyph)

    # 2. Entity pools (PD) or Activities (AF)
    if is_pd:
        for entity_pool in model.entity_pools:
            for layout_el in _get_layout_elements(
                writing_context, entity_pool
            ):
                sbgnml_glyph = _make_sbgnml_glyph(
                    writing_context, layout_el, model_element=entity_pool
                )
                for child_glyph in _make_sbgnml_child_glyphs(
                    writing_context, layout_el, entity_pool
                ):
                    sbgnml_glyph.append(child_glyph)
                momapy.sbgn.io.sbgnml._writing.add_annotations_and_notes(
                    writing_context, sbgnml_glyph, entity_pool
                )
                _register(layout_el, sbgnml_glyph)
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
                momapy.sbgn.io.sbgnml._writing.add_annotations_and_notes(
                    writing_context, sbgnml_glyph, activity
                )
                _register(layout_el, sbgnml_glyph)

    # 3. Logical operators (with logic arcs)
    singleton_to_key = (
        writing_context.map_.layout_model_mapping._singleton_to_key
    )
    for logical_operator in model.logical_operators:
        for frozenset_key in _get_frozenset_keys(
            writing_context, logical_operator
        ):
            operator_layout = None
            arc_layouts = []
            for item in frozenset_key:
                if isinstance(
                    item,
                    (
                        momapy.sbgn.pd.LogicArcLayout,
                        momapy.sbgn.af.LogicArcLayout,
                    ),
                ):
                    arc_layouts.append(item)
                elif (
                    isinstance(item, momapy.core.layout.Node)
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
            momapy.sbgn.io.sbgnml._writing.add_annotations_and_notes(
                writing_context, sbgnml_glyph, logical_operator
            )
            _register(operator_layout, sbgnml_glyph)
            for arc_layout in arc_layouts:
                sbgnml_arc = _make_sbgnml_arc_element(
                    writing_context, arc_layout
                )
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
            momapy.sbgn.io.sbgnml._writing.add_annotations_and_notes(
                writing_context, sbgnml_glyph, submap
            )
            _register(layout_el, sbgnml_glyph)
        if hasattr(submap, "terminals"):
            for terminal in submap.terminals:
                if (
                    hasattr(terminal, "reference")
                    and terminal.reference is not None
                ):
                    reference_layout = _get_child_layout_element(
                        writing_context, terminal.reference, terminal
                    )
                    if reference_layout is not None and isinstance(
                        reference_layout,
                        (
                            momapy.core.layout.SingleHeadedArc,
                            momapy.core.layout.DoubleHeadedArc,
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
            momapy.sbgn.io.sbgnml._writing.add_annotations_and_notes(
                writing_context, sbgnml_glyph, tag
            )
            _register(layout_el, sbgnml_glyph)
        if hasattr(tag, "reference") and tag.reference is not None:
            reference_layout = _get_child_layout_element(
                writing_context, tag.reference, tag
            )
            if reference_layout is not None and isinstance(
                reference_layout,
                (
                    momapy.core.layout.SingleHeadedArc,
                    momapy.core.layout.DoubleHeadedArc,
                ),
            ):
                sbgnml_arc = _make_sbgnml_arc_element(
                    writing_context, reference_layout
                )
                _register(reference_layout, sbgnml_arc)

    # 6. Processes
    if is_pd:
        for process in model.processes:
            if isinstance(process, momapy.sbgn.pd.Phenotype):
                for layout_el in _get_layout_elements(
                    writing_context, process
                ):
                    sbgnml_glyph = _make_sbgnml_glyph(
                        writing_context, layout_el, model_element=process
                    )
                    for child_glyph in _make_sbgnml_child_glyphs(
                        writing_context, layout_el, process
                    ):
                        sbgnml_glyph.append(child_glyph)
                    momapy.sbgn.io.sbgnml._writing.add_annotations_and_notes(
                        writing_context, sbgnml_glyph, process
                    )
                    _register(layout_el, sbgnml_glyph)
            elif isinstance(process, momapy.sbgn.pd.StoichiometricProcess):
                for frozenset_key in _get_frozenset_keys(
                    writing_context, process
                ):
                    process_layout = None
                    arc_layouts = []
                    for item in frozenset_key:
                        if isinstance(
                            item,
                            (
                                momapy.sbgn.pd.ConsumptionLayout,
                                momapy.sbgn.pd.ProductionLayout,
                            ),
                        ):
                            arc_layouts.append(item)
                        elif (
                            isinstance(item, momapy.core.layout.Node)
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
                    momapy.sbgn.io.sbgnml._writing.add_annotations_and_notes(
                        writing_context, sbgnml_glyph, process
                    )
                    _register(process_layout, sbgnml_glyph)
                    for arc_layout in arc_layouts:
                        sbgnml_arc = _make_sbgnml_arc_element(
                            writing_context, arc_layout
                        )
                        _register(arc_layout, sbgnml_arc)

    # 7. Modulations (PD) or Influences (AF)
    modulations = model.modulations if is_pd else model.influences
    for modulation in modulations:
        for frozenset_key in _get_frozenset_keys(
            writing_context, modulation
        ):
            arc_layout = None
            for item in frozenset_key:
                if singleton_to_key.get(item) == frozenset_key:
                    arc_layout = item
                    break
            if arc_layout is None:
                continue
            sbgnml_arc = _make_sbgnml_arc_element(
                writing_context, arc_layout
            )
            momapy.sbgn.io.sbgnml._writing.add_annotations_and_notes(
                writing_context, sbgnml_arc, modulation
            )
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
    language = (
        momapy.sbgn.io.sbgnml._writing_classification.CLASS_TO_SBGNML_CLASS[
            type(map_)
        ]
    )
    id_ = writing_context.ids.get(map_)
    if id_ is None:
        id_ = map_.id_
    else:
        id_ = id_[0]
    attributes = {"id": id_, "language": language}
    sbgnml_map = momapy.sbgn.io.sbgnml._writing.make_lxml_element(
        "map", attributes=attributes
    )
    sbgnml_bbox = momapy.sbgn.io.sbgnml._writing.make_sbgnml_bbox_from_node(
        map_.layout
    )
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


class _SBGNMLWriter(momapy.io.core.Writer):
    """Base SBGN-ML writer.

    All serialization logic lives in module-level functions.  This class
    only provides the ``write`` entry point.
    """

    @classmethod
    def write(
        cls,
        obj: momapy.sbgn.core.SBGNMap,
        file_path,
        annotations=None,
        notes=None,
        ids=None,
        with_render_information=True,
        with_annotations=True,
        with_notes=True,
    ):
        """Write an SBGN map to an SBGN-ML file.

        Args:
            obj: The SBGN map to serialize.
            file_path: Destination file path.
            annotations: Optional per-element annotation dict.
            notes: Optional per-element notes dict.
            ids: Optional per-element id overrides dict.
            with_render_information: Ignored (kept for API compat).
            with_annotations: Whether to write annotations.
            with_notes: Whether to write notes.
        """
        if annotations is None:
            annotations = {}
        if notes is None:
            notes = {}
        if ids is None:
            ids = {}
        writing_context = WritingContext(
            map_=obj,
            annotations=annotations,
            notes=notes,
            ids=ids,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        sbgnml_sbgn = momapy.sbgn.io.sbgnml._writing.make_lxml_element(
            "sbgn", nsmap=momapy.sbgn.io.sbgnml._writing.NSMAP
        )
        sbgnml_map = make_sbgnml_map(writing_context)
        sbgnml_sbgn.append(sbgnml_map)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(
                lxml.etree.tostring(
                    sbgnml_sbgn, pretty_print=True, xml_declaration=True
                ).decode()
            )


class SBGNML0_3Writer(_SBGNMLWriter):
    """Class for SBGN-ML 0.3 writer objects."""

    pass
