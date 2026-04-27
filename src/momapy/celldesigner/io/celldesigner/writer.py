"""CellDesigner XML writer (new, model-first approach)."""

import dataclasses
import math
import os
import typing

import lxml.etree

from momapy.drawing import NoneValue, NoneValueType
from momapy.geometry import get_transformation_for_frame
from momapy.io.core import Writer, WriterResult
from momapy.io.utils import WritingContext
from momapy.utils import check_parent_dir_exists
from momapy.celldesigner.io.celldesigner import _writing
from momapy.celldesigner.io.celldesigner._reading_parsing import (
    _LINK_ANCHOR_POSITION_TO_ANCHOR_NAME,
)
from momapy.celldesigner.io.celldesigner._writing import (
    _ANCHOR_NAME_TO_LINK_ANCHOR_POSITION,
    _CLASS_TO_CD_STRING,
    _CLASS_TO_MODIFIER_TYPE,
    _CLASS_TO_REACTION_TYPE,
    _MODIFICATION_STATE_TO_CD,
    color_to_cd_hex,
    compute_cd_angle,
    encode_name,
    node_to_bounds_attrs,
)
from momapy.celldesigner.elements import CellDesignerNode
from momapy.celldesigner.map import CellDesignerMap
from momapy.celldesigner.model import (
    AndGate,
    AntisenseRNATemplate,
    BooleanLogicGate,
    Catalysis,
    Catalyzer,
    CodingRegion,
    Complex,
    Degraded,
    Dissociation,
    GeneTemplate,
    HeterodimerAssociation,
    Inhibition,
    IonChannelTemplate,
    ModificationSite,
    Modulation,
    NegativeInfluence,
    NotGate,
    OrGate,
    Phenotype,
    PhysicalStimulation,
    PositiveInfluence,
    Product,
    ProteinBindingDomain,
    ProteinTemplate,
    RNATemplate,
    Reactant,
    ReceptorTemplate,
    RegulatoryRegion,
    TranscriptionStartingSiteL,
    TranscriptionStartingSiteR,
    Triggering,
    TruncatedProteinTemplate,
    Truncation,
    UnknownCatalysis,
    UnknownGate,
    UnknownInhibition,
    UnknownModulation,
    UnknownNegativeInfluence,
    UnknownPhysicalStimulation,
    UnknownPositiveInfluence,
    UnknownTriggering,
)
from momapy.celldesigner.layout import (
    AndGateLayout,
    CompartmentCorner,
    CompartmentSide,
    ComplexLayout,
    ConsumptionLayout,
    CornerCompartmentLayout,
    DegradedActiveLayout,
    DegradedLayout,
    LineCompartmentLayout,
    LogicArcLayout,
    ModificationLayout,
    NotGateLayout,
    OrGateLayout,
    OvalCompartmentLayout,
    ProductionLayout,
    ReactionLayout,
    RectangleCompartmentLayout,
    StructuralStateLayout,
    UnknownGateLayout,
)
import momapy.builder

_CD_NS = "http://www.sbml.org/2001/ns/celldesigner"
_SBML_NS = "http://www.sbml.org/sbml/level2/version4"
_XHTML_NS = "http://www.w3.org/1999/xhtml"

_NSMAP = {
    None: _SBML_NS,
    "celldesigner": _CD_NS,
}


def _modulation_reaction_type(modulation):
    """Determine the CellDesigner reaction type for a modulation.

    Rules:
    - Inhibition targeting a non-Phenotype species → NEGATIVE_INFLUENCE
    - Modulation/Triggering/PhysicalStimulation targeting a non-Phenotype
      species → REDUCED_ variant
    - Otherwise → standard type
    """
    target = modulation.target
    is_reduced = target is not None and not isinstance(target, Phenotype)
    _MAP = {
        Catalysis: ("CATALYSIS", None),
        UnknownCatalysis: ("UNKNOWN_CATALYSIS", None),
        Inhibition: ("INHIBITION", "NEGATIVE_INFLUENCE"),
        UnknownInhibition: (
            "UNKNOWN_INHIBITION",
            "UNKNOWN_NEGATIVE_INFLUENCE",
        ),
        PhysicalStimulation: (
            "PHYSICAL_STIMULATION",
            "REDUCED_PHYSICAL_STIMULATION",
        ),
        UnknownPhysicalStimulation: (
            "UNKNOWN_PHYSICAL_STIMULATION",
            "UNKNOWN_REDUCED_PHYSICAL_STIMULATION",
        ),
        Modulation: ("MODULATION", "REDUCED_MODULATION"),
        UnknownModulation: (
            "UNKNOWN_MODULATION",
            "UNKNOWN_REDUCED_MODULATION",
        ),
        Triggering: ("TRIGGER", "REDUCED_TRIGGER"),
        UnknownTriggering: (
            "UNKNOWN_TRIGGER",
            "UNKNOWN_REDUCED_TRIGGER",
        ),
        PositiveInfluence: ("POSITIVE_INFLUENCE", None),
        NegativeInfluence: ("NEGATIVE_INFLUENCE", None),
        UnknownPositiveInfluence: (
            "UNKNOWN_POSITIVE_INFLUENCE",
            None,
        ),
        UnknownNegativeInfluence: (
            "UNKNOWN_NEGATIVE_INFLUENCE",
            None,
        ),
    }
    entry = _MAP.get(type(modulation))
    if entry is None:
        return "MODULATION"
    normal, reduced = entry
    if is_reduced and reduced is not None:
        return reduced
    return normal


@dataclasses.dataclass
class CellDesignerWritingContext(WritingContext):
    """Shared state for the writer."""

    subunit_to_complex: dict = dataclasses.field(default_factory=dict)
    used_metaids: set = dataclasses.field(default_factory=set)
    species_to_id: dict = dataclasses.field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_lxml_element(tag, ns=None, attrs=None, text=None, nsmap=None):
    """Create an lxml element."""
    lxml_tag = f"{{{ns}}}{tag}" if ns is not None else tag
    if nsmap is None:
        nsmap = {}
    if attrs is None:
        attrs = {}
    elem = lxml.etree.Element(lxml_tag, nsmap=nsmap, **attrs)
    if text is not None:
        elem.text = str(text)
    return elem


def _make_celldesigner_element(tag, attrs=None, text=None):
    """Shortcut for CellDesigner-namespaced element."""
    return _make_lxml_element(tag, ns=_CD_NS, attrs=attrs, text=text)


def _make_sbml_element(tag, attrs=None, text=None, nsmap=None):
    """Shortcut for SBML-namespaced element."""
    return _make_lxml_element(tag, ns=_SBML_NS, attrs=attrs, text=text, nsmap=nsmap)


_encode_name = encode_name


def _strip_active(species):
    """Get the CellDesigner XML species ID (strips _active suffixes).

    This is the raw ID derivation, without context-aware canonicalization.
    Used only during bootstrap (building species_to_id).
    """
    if species is None:
        return ""
    id_str = species.id_ or ""
    while id_str.endswith("_active"):
        id_str = id_str[: -len("_active")]
    return id_str


def _get_species_id(species, writing_context=None):
    """Get the canonical species ID for a model species.

    When writing_context is provided, uses the species_to_id mapping built from the
    model tree so that all references to the same model object use a
    consistent ID. Falls back to stripping _active suffixes.
    """
    if species is None:
        return ""
    if writing_context is not None:
        canonical = writing_context.species_to_id.get(id(species))
        if canonical is not None:
            return canonical
    return _strip_active(species)


_color_hex = color_to_cd_hex


def _get_line_attributes(layout, include_type=False):
    """Build attributes dict for a ``<cd:line>`` element from a layout.

    Reads ``path_stroke_width`` and ``path_stroke`` from the layout,
    falling back to sensible defaults.

    Args:
        layout: A layout element with path_stroke / path_stroke_width.
        include_type: Whether to include ``type="Straight"``.

    Returns:
        A dict of XML attributes.
    """
    width = "1.0"
    color = "ff000000"
    if layout is not None:
        if getattr(layout, "path_stroke_width", None) is not None:
            width = str(layout.path_stroke_width)
        stroke = getattr(layout, "path_stroke", None)
        if stroke is not None and not isinstance(stroke, NoneValueType):
            color = _color_hex(stroke)
    attrs = {"width": width, "color": color}
    if include_type:
        attrs["type"] = "Straight"
    return attrs


def _unique_metaid(writing_context, candidate):
    """Return a unique metaid string that is a valid XML ID."""
    # XML ID must start with a letter or underscore
    if candidate and not candidate[0].isalpha() and candidate[0] != "_":
        candidate = f"_{candidate}"
    result = candidate
    counter = 1
    while result in writing_context.used_metaids:
        result = f"{candidate}_{counter}"
        counter += 1
    writing_context.used_metaids.add(result)
    return result


def _mapping(writing_context):
    """Shortcut to access layout_model_mapping."""
    return writing_context.map_.layout_model_mapping


def _sort_modifications_by_layout(writing_context, species):
    """Sort a species' modifications by their layout child order.

    The modification layout children of the species' alias layout
    preserve the original XML order.  We use that to sort the
    frozenset of model modifications.
    """
    modifications = list(species.modifications)
    # Find any alias layout for this species — search both top-level
    # and complex children.
    alias_layout = _find_any_alias_layout(writing_context, species)
    if alias_layout is None:
        return modifications
    # Build residue_id -> position from layout children.
    # The layout id = f"{alias_species_id}_{xml_residue_id}_layout"
    # where alias_species_id may differ from the model species id
    # for subunit aliases.
    residue_order = {}
    suffix = "_layout"
    for i, child in enumerate(alias_layout.layout_elements):
        if isinstance(child, ModificationLayout):
            layout_id = child.id_
            if layout_id.endswith(suffix):
                # Strip the suffix and the species prefix to get residue id
                # The prefix is everything up to the first residue id part
                core = layout_id[: -len(suffix)]
                # Match against known residue ids from the template
                for mod in modifications:
                    if mod.residue is not None:
                        xml_residue_id = _strip_template_prefix(mod.residue, species)
                        if core.endswith(f"_{xml_residue_id}"):
                            residue_order[xml_residue_id] = i
                            break
    # Sort by layout order
    modifications.sort(
        key=lambda m: residue_order.get(
            _strip_template_prefix(m.residue, species) if m.residue else "",
            float("inf"),
        )
    )
    return modifications


def _find_any_alias_layout(writing_context, species):
    """Find any alias layout for a species, including inside complexes."""
    # Try direct lookup first
    for layout_key in _get_layouts(writing_context, species):
        if isinstance(layout_key, frozenset):
            continue
        if isinstance(layout_key, CellDesignerNode):
            return layout_key
    # Search in layout_model_mapping for this species
    mapping = _mapping(writing_context)
    for layout_element in writing_context.map_.layout.layout_elements:
        if not isinstance(layout_element, CellDesignerNode):
            continue
        if not hasattr(layout_element, "layout_elements"):
            continue
        # Search children of complexes
        for child in layout_element.layout_elements:
            if not isinstance(child, CellDesignerNode):
                continue
            model_info = mapping.get_mapping(child)
            if model_info is species:
                return child
            if hasattr(child, "layout_elements"):
                for grandchild in child.layout_elements:
                    if not isinstance(
                        grandchild,
                        CellDesignerNode,
                    ):
                        continue
                    model_info2 = mapping.get_mapping(grandchild)
                    if model_info2 is species:
                        return grandchild
    return None


def _strip_template_prefix(residue_or_region, owner):
    """Strip the template id prefix from a residue or region id.

    Model ids for ModificationResidue and Region are composite:
    ``f"{template_id}_{local_id}"``.  CellDesigner XML expects just
    the local id.  *owner* can be a species (with a `template`
    attribute) or the template itself.
    """
    template = getattr(owner, "template", owner)
    if template is not None and hasattr(template, "id_"):
        prefix = f"{template.id_}_"
        if residue_or_region.id_.startswith(prefix):
            return residue_or_region.id_[len(prefix) :]
    return residue_or_region.id_


def _build_layout_order_index(layout):
    """Build a mapping from layout element id to position index.

    Walks the layout tree recursively so that both top-level and
    nested (complex children) elements get an index reflecting
    their original ordering.
    """
    index = {}
    counter = [0]

    def _walk(elements):
        for element in elements:
            index[element.id_] = counter[0]
            counter[0] += 1
            if hasattr(element, "layout_elements"):
                _walk(element.layout_elements)

    _walk(layout.layout_elements)
    return index


def _sort_aliases_by_layout_order(list_elem, layout_order_index):
    """Sort alias XML children of list_elem by layout element order."""
    _sort_xml_children_by_key(
        list_elem,
        key_func=lambda alias: layout_order_index.get(alias.get("id"), float("inf")),
    )


def _sort_xml_children_by_key(list_elem, key_func):
    """Sort XML children of list_elem using the given key function."""
    children = list(list_elem)
    if len(children) <= 1:
        return
    for child in children:
        list_elem.remove(child)
    children.sort(key=key_func)
    for child in children:
        list_elem.append(child)


def _participant_layout_position(
    writing_context,
    participant,
    reaction,
    frozenset_mapping,
    reaction_layout,
    is_start,
    arc_order,
):
    """Get the layout position for a reaction participant.

    Uses the arc alias order mapping to determine position.
    Falls back to infinity for participants without a layout arc.
    """
    alias_layout = _find_layout_for_participant(
        writing_context,
        participant,
        reaction,
        frozenset_mapping,
        reaction_layout,
        is_start,
    )
    if alias_layout is not None:
        return arc_order.get(alias_layout.id_, float("inf"))
    return float("inf")


def _build_arc_alias_order(writing_context, reaction_layout, arc_cls):
    """Build a mapping from alias id to layout position for arcs of a reaction.

    For each arc of the given class connected to the reaction layout,
    maps the arc's target alias id to its position in the layout.
    """
    order = {}
    for i, element in enumerate(writing_context.map_.layout.layout_elements):
        if (
            isinstance(element, arc_cls)
            and element.source is reaction_layout
            and element.target is not None
        ):
            order[element.target.id_] = i
    return order


def _sort_reactions_by_layout_order(list_elem, layout_order_index):
    """Sort reaction XML children of list_elem by layout element order.

    Each reaction's layout element id follows the pattern
    ``f"{reaction_id}_layout"``, so we derive the sort key from
    the reaction's ``id`` attribute.
    """
    _sort_xml_children_by_key(
        list_elem,
        key_func=lambda reaction: layout_order_index.get(
            f"{reaction.get('id')}_layout", float("inf")
        ),
    )


def _get_layouts(writing_context, model_element):
    """Get layout elements for a model element.

    Returns a list. Items can be single layout elements or frozensets.
    """
    result = _mapping(writing_context).get_mapping(model_element)
    if result is None:
        return []
    if isinstance(result, list):
        return result
    return [result]


def _find_layout_for_species_in_frozenset(writing_context, species, frozenset_mapping):
    """Find the layout element for a species within a reaction frozenset."""
    for elem in frozenset_mapping:
        model = _mapping(writing_context).get_mapping(elem)
        if model is species:
            return elem
    return None


def _find_layout_for_participant(
    writing_context, participant, reaction, frozenset_mapping, reaction_layout, is_start
):
    """Find the alias layout for a specific reaction participant.

    For base participants, the alias is the reaction layout's source
    (reactants) or target (products).  For link participants, the alias
    is resolved via the ConsumptionLayout/ProductionLayout stored in the
    layout-model mapping for the (participant, reaction) tuple.

    Falls back to ``_find_layout_for_species_in_frozenset`` when the
    more precise lookup fails.

    Args:
        writing_context: The writing context.
        participant: The Reactant or Product model element.
        reaction: The reaction model element.
        frozenset_mapping: The frozenset key for this reaction.
        reaction_layout: The ReactionLayout element.
        is_start: True for reactants, False for products.

    Returns:
        The alias layout element, or None.
    """
    if participant.base and reaction_layout is not None:
        result = reaction_layout.source if is_start else reaction_layout.target
        if result is not None:
            return result
    arc_layouts = _mapping(writing_context).get_child_layout_elements(
        participant, reaction
    )
    for arc_layout in arc_layouts:
        if hasattr(arc_layout, "target"):
            if frozenset_mapping is not None and arc_layout not in frozenset_mapping:
                continue
            return arc_layout.target
    species = participant.referred_species
    if frozenset_mapping is not None:
        return _find_layout_for_species_in_frozenset(
            writing_context, species, frozenset_mapping
        )
    return None


def _get_reaction_layout(frozenset_mapping):
    """Extract the ReactionLayout from a frozenset."""
    for elem in frozenset_mapping:
        if isinstance(elem, ReactionLayout):
            return elem
    return None


def _collect_arcs_for_reaction(
    writing_context, reaction_layout, arc_cls, exclude_alias=None
):
    """Collect arc layouts of a given type connected to a reaction layout.

    Args:
        writing_context: The writing context.
        reaction_layout: The ReactionLayout element.
        arc_cls: The arc class to filter (ConsumptionLayout or ProductionLayout).
        exclude_alias: An optional alias layout to exclude (e.g. the base
            reactant/product alias which is already handled separately).

    Returns:
        A list of arc layouts.
    """
    arcs = []
    for layout_element_item in writing_context.map_.layout.layout_elements:
        if (
            isinstance(layout_element_item, arc_cls)
            and layout_element_item.source is reaction_layout
            and (
                exclude_alias is None or layout_element_item.target is not exclude_alias
            )
        ):
            arcs.append(layout_element_item)
    return arcs


def _species_class_string(species):
    """Map a species model class to its CellDesigner class string."""
    return _CLASS_TO_CD_STRING.get(type(species), "UNKNOWN")


def _template_ref_tag(template):
    """Map a template to its XML reference tag name."""
    if isinstance(template, ProteinTemplate):
        return "proteinReference"
    if isinstance(template, GeneTemplate):
        return "geneReference"
    if isinstance(template, RNATemplate):
        return "rnaReference"
    if isinstance(template, AntisenseRNATemplate):
        return "antisensernaReference"
    return "proteinReference"


def _modification_state_string(state):
    """Convert modification state to CellDesigner string."""
    if state is None:
        return "empty"
    name = state.name if hasattr(state, "name") else str(state)
    return _MODIFICATION_STATE_TO_CD.get(name, "empty")


_bounds_attrs = node_to_bounds_attrs


def _anchor_name_to_position(anchor_name):
    """Convert an anchor name to CellDesigner link anchor position string."""
    return _ANCHOR_NAME_TO_LINK_ANCHOR_POSITION.get(anchor_name)


def _compute_target_line_index(reaction_layout, modifier_arc):
    """Compute the CellDesigner targetLineIndex for a modifier.

    The targetLineIndex is "segmentIndex,anchorId" where anchorId identifies
    which corner/side of the reaction rectangle the modifier connects to.
    The reaction rectangle is 10x10 centered on the reaction node, rotated
    by the reaction line angle.

    Anchor positions:
        2=top, 3=bottom, 4=top-left, 5=top-right, 6=bottom-left, 7=bottom-right
    """
    import math

    RECT_HALF = 5.0
    mid = reaction_layout._get_reaction_node_position()
    # Reaction line angle from the center segment
    points = reaction_layout.points()
    n_segments = len(reaction_layout.segments)
    seg_idx = reaction_layout.reaction_node_segment
    if seg_idx < n_segments:
        segment = reaction_layout.segments[seg_idx]
        delta_x = segment.p2.x - segment.p1.x
        delta_y = segment.p2.y - segment.p1.y
    else:
        delta_x = points[-1].x - points[0].x
        delta_y = points[-1].y - points[0].y
    angle = math.atan2(delta_y, delta_x)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    # Build the 6 anchor points (offsets rotated by angle)
    offsets = {
        "2": (0, -RECT_HALF),
        "3": (0, RECT_HALF),
        "4": (-RECT_HALF, -RECT_HALF),
        "5": (RECT_HALF, -RECT_HALF),
        "6": (-RECT_HALF, RECT_HALF),
        "7": (RECT_HALF, RECT_HALF),
    }
    # Modifier arc endpoint (the end closest to the reaction)
    arc_pts = modifier_arc.points()
    end_point = arc_pts[-1]
    best_id = "2"
    best_dist = float("inf")
    for anchor_id, (offset_x, offset_y) in offsets.items():
        rotated_x = mid.x + offset_x * cos_a - offset_y * sin_a
        rotated_y = mid.y + offset_x * sin_a + offset_y * cos_a
        dist = (rotated_x - end_point.x) ** 2 + (rotated_y - end_point.y) ** 2
        if dist < best_dist:
            best_dist = dist
            best_id = anchor_id
    return f"0,{best_id}"


def _infer_anchor_position(species_layout, point, tol=0.5):
    """Find the CellDesigner linkAnchor position for a point on a species."""
    import math

    for (
        cd_position,
        anchor_name,
    ) in _LINK_ANCHOR_POSITION_TO_ANCHOR_NAME.items():
        anchor_point = species_layout.anchor_point(anchor_name)
        if anchor_point is None:
            continue
        if math.isclose(anchor_point.x, point.x, abs_tol=tol) and math.isclose(
            anchor_point.y, point.y, abs_tol=tol
        ):
            return cd_position
    return None


# ---------------------------------------------------------------------------
# Module-level functions (extracted from CellDesignerWriter classmethods)
# ---------------------------------------------------------------------------


def _build_make_sbml_element(writing_context):
    sbml = _make_lxml_element(
        "sbml",
        attrs={"level": "2", "version": "4"},
        nsmap=_NSMAP,
    )
    sbml.append(_make_celldesigner_model(writing_context))
    return sbml


def _make_celldesigner_model(writing_context):
    model_id = writing_context.map_.id_ or "untitled"
    model = _make_lxml_element("model", attrs={"metaid": model_id, "id": model_id})
    # notes
    notes_element = _build_sbml_notes(writing_context, writing_context.map_)
    if notes_element is not None:
        model.append(notes_element)
    # annotation
    annotation = _make_lxml_element("annotation")
    annotation.append(_make_celldesigner_extension(writing_context))
    _append_rdf_to_annotation(
        writing_context, annotation, writing_context.map_, model_id
    )
    model.append(annotation)
    model.append(_make_celldesigner_list_of_compartments(writing_context))
    model.append(_make_celldesigner_list_of_species(writing_context))
    model.append(_make_celldesigner_list_of_reactions(writing_context))
    return model


def _build_sbml_notes(writing_context, model_element):
    """Build a plain ``<notes>`` element for an SBML-namespaced element.

    Returns None when ``with_notes`` is disabled or no notes are stored for
    ``model_element``.
    """
    if not writing_context.with_notes:
        return None
    notes = writing_context.element_to_notes.get(model_element)
    if not notes:
        return None
    notes_element = _make_lxml_element("notes")
    for note in notes:
        try:
            parsed = lxml.etree.fromstring(note)
        except lxml.etree.XMLSyntaxError:
            continue
        notes_element.append(parsed)
        break
    if len(notes_element) == 0:
        return None
    return notes_element


def _append_rdf_to_annotation(
    writing_context, annotation_element, model_element, about_id
):
    """Append an ``<rdf:RDF>`` block to an ``<annotation>`` element.

    No-op when ``with_annotations`` is disabled or the element has no
    annotations.
    """
    if not writing_context.with_annotations:
        return
    annotations = writing_context.element_to_annotations.get(model_element)
    if not annotations:
        return
    rdf_element = _writing.make_rdf_annotation(annotations, about_id)
    if rdf_element is not None:
        annotation_element.append(rdf_element)


# --- Extension (CD annotation) ---


def _make_celldesigner_extension(writing_context):
    extension = _make_celldesigner_element("extension")
    extension.append(_make_celldesigner_element("modelVersion", text="4.0"))
    display_attrs = {
        "sizeX": str(int(writing_context.map_.layout.width)),
        "sizeY": str(int(writing_context.map_.layout.height)),
    }
    extension.append(_make_celldesigner_element("modelDisplay", attrs=display_attrs))
    extension.append(_make_celldesigner_list_of_included_species(writing_context))
    extension.append(_make_celldesigner_list_of_compartment_aliases(writing_context))
    extension.append(
        _make_celldesigner_list_of_complex_species_aliases(writing_context)
    )
    extension.append(_make_celldesigner_list_of_species_aliases(writing_context))
    extension.append(_make_celldesigner_list_of_proteins(writing_context))
    extension.append(_make_celldesigner_list_of_genes(writing_context))
    extension.append(_make_celldesigner_list_of_rnas(writing_context))
    extension.append(_make_celldesigner_list_of_antisense_rnas(writing_context))
    extension.append(_make_celldesigner_element("listOfLayers"))
    return extension


# --- Compartment aliases ---


_COMPARTMENT_LAYOUT_CLASSES = (
    RectangleCompartmentLayout,
    OvalCompartmentLayout,
    CornerCompartmentLayout,
    LineCompartmentLayout,
)


def _compartment_class_name(layout_key):
    if isinstance(layout_key, OvalCompartmentLayout):
        return "OVAL"
    if isinstance(layout_key, CornerCompartmentLayout):
        return f"SQUARE_CLOSEUP_{layout_key.corner.value}"
    if isinstance(layout_key, LineCompartmentLayout):
        return f"SQUARE_CLOSEUP_{layout_key.side.value}"
    return "SQUARE"


def _compartment_closeup_point(layout_key):
    bbox = layout_key.bbox()
    left = bbox.north_west().x
    top = bbox.north_west().y
    right = bbox.south_east().x
    bottom = bbox.south_east().y
    if isinstance(layout_key, CornerCompartmentLayout):
        corner = layout_key.corner
        Corner = CompartmentCorner
        if corner is Corner.NORTHWEST:
            return left, top
        if corner is Corner.NORTHEAST:
            return right, top
        if corner is Corner.SOUTHWEST:
            return left, bottom
        return right, bottom
    side = layout_key.side
    Side = CompartmentSide
    if side is Side.NORTH:
        return layout_key.position.x, top
    if side is Side.SOUTH:
        return layout_key.position.x, bottom
    if side is Side.EAST:
        return right, layout_key.position.y
    return left, layout_key.position.y


def _make_celldesigner_list_of_compartment_aliases(writing_context):
    list_elem = _make_celldesigner_element("listOfCompartmentAliases")
    for comp in sorted(
        writing_context.map_.model.compartments, key=lambda c: c.id_ or ""
    ):
        for layout_key in _get_layouts(writing_context, comp):
            if isinstance(layout_key, frozenset):
                continue
            if isinstance(layout_key, _COMPARTMENT_LAYOUT_CLASSES):
                alias = _make_celldesigner_element(
                    "compartmentAlias",
                    attrs={
                        "id": layout_key.id_,
                        "compartment": comp.id_,
                    },
                )
                class_name = _compartment_class_name(layout_key)
                alias.append(_make_celldesigner_element("class", text=class_name))
                if isinstance(
                    layout_key,
                    (
                        CornerCompartmentLayout,
                        LineCompartmentLayout,
                    ),
                ):
                    px, py = _compartment_closeup_point(layout_key)
                    alias.append(
                        _make_celldesigner_element(
                            "point",
                            attrs={"x": str(px), "y": str(py)},
                        )
                    )
                else:
                    alias.append(
                        _make_celldesigner_element(
                            "bounds", attrs=_bounds_attrs(layout_key)
                        )
                    )
                # namePoint (label position)
                label = getattr(layout_key, "label", None)
                if label is not None:
                    alias.append(
                        _make_celldesigner_element(
                            "namePoint",
                            attrs={
                                "x": str(label.position.x),
                                "y": str(label.position.y),
                            },
                        )
                    )
                # doubleLine
                sep = getattr(layout_key, "sep", None)
                stroke_width = getattr(layout_key, "stroke_width", None)
                inner_stroke_width = getattr(layout_key, "inner_stroke_width", None)
                alias.append(
                    _make_celldesigner_element(
                        "doubleLine",
                        attrs={
                            "thickness": str(sep) if sep else "12.0",
                            "outerWidth": str(stroke_width) if stroke_width else "2.0",
                            "innerWidth": str(inner_stroke_width)
                            if inner_stroke_width
                            else "1.0",
                        },
                    )
                )
                # paint — the reader derives fill as stroke.with_alpha(0.5),
                # so we write back the stroke color directly to preserve
                # the original alpha.
                stroke = getattr(layout_key, "stroke", None)
                if stroke is not None and stroke is not NoneValue:
                    paint_color = _color_hex(stroke)
                else:
                    paint_color = "ffcccccc"
                alias.append(
                    _make_celldesigner_element(
                        "paint", attrs={"color": paint_color, "scheme": "Color"}
                    )
                )
                alias.append(
                    _make_celldesigner_element(
                        "info", attrs={"state": "empty", "angle": "-1.5707963267948966"}
                    )
                )
                list_elem.append(alias)
    return list_elem


# --- Included species (complex subunits) ---


def _make_celldesigner_list_of_included_species(writing_context):
    list_elem = _make_celldesigner_element("listOfIncludedSpecies")
    seen_ids = set()
    for species in sorted(
        writing_context.map_.model.species, key=lambda s: s.id_ or ""
    ):
        if isinstance(species, Complex):
            _collect_included_species(
                writing_context, species, species, list_elem, seen_ids
            )
    return list_elem


def _collect_included_species(
    writing_context, complex_, root_complex, list_elem, seen_ids
):
    """Recursively collect included species from a complex."""
    for sub in sorted(complex_.subunits, key=lambda s: s.id_ or ""):
        sub_id = _get_species_id(sub, writing_context)
        if sub_id not in seen_ids:
            seen_ids.add(sub_id)
            list_elem.append(
                _make_celldesigner_included_species(writing_context, sub, complex_)
            )
        if isinstance(sub, Complex):
            _collect_included_species(
                writing_context, sub, root_complex, list_elem, seen_ids
            )


def _make_celldesigner_included_species(writing_context, species, parent_complex):
    species_id = _get_species_id(species, writing_context)
    species_element = _make_celldesigner_element(
        "species",
        attrs={
            "id": species_id,
            "name": _encode_name(species.name) or "",
        },
    )
    # notes (CellDesigner expects exactly one <html> child)
    notes = _make_celldesigner_element("notes")
    species_notes = (
        writing_context.element_to_notes.get(species, set())
        if writing_context.with_notes
        else set()
    )
    parsed_one = False
    if species_notes:
        for note in species_notes:
            try:
                parsed = lxml.etree.fromstring(note)
                notes.append(parsed)
                parsed_one = True
                break
            except lxml.etree.XMLSyntaxError:
                pass
    if not parsed_one:
        html = lxml.etree.SubElement(notes, f"{{{_XHTML_NS}}}html")
        head = lxml.etree.SubElement(html, f"{{{_XHTML_NS}}}head")
        lxml.etree.SubElement(head, f"{{{_XHTML_NS}}}title")
        lxml.etree.SubElement(html, f"{{{_XHTML_NS}}}body")
    # Included species round-trip their RDF inside <celldesigner:notes>,
    # embedded in the <body> alongside human-readable text.
    if writing_context.with_annotations:
        species_annotations = writing_context.element_to_annotations.get(species)
        if species_annotations:
            rdf_element = _writing.make_rdf_annotation(species_annotations, species_id)
            if rdf_element is not None:
                _writing.inject_rdf_into_celldesigner_notes(notes, rdf_element)
    species_element.append(notes)
    # annotation
    annotation = _make_celldesigner_element("annotation")
    annotation.append(
        _make_celldesigner_element(
            "complexSpecies", text=_get_species_id(parent_complex, writing_context)
        )
    )
    annotation.append(_make_celldesigner_species_identity(writing_context, species))
    species_element.append(annotation)
    return species_element


# --- Species identity ---


def _make_celldesigner_species_identity(writing_context, species):
    identity = _make_celldesigner_element("speciesIdentity")
    identity.append(
        _make_celldesigner_element("class", text=_species_class_string(species))
    )
    template = getattr(species, "template", None)
    if template is not None:
        tag = _template_ref_tag(template)
        ref_id = template.id_
        identity.append(_make_celldesigner_element(tag, text=ref_id))
    identity.append(
        _make_celldesigner_element("name", text=_encode_name(species.name) or "")
    )
    if species.hypothetical:
        identity.append(_make_celldesigner_element("hypothetical", text="true"))
    state = _make_celldesigner_species_state(writing_context, species)
    if state is not None:
        identity.append(state)
    return identity


def _make_celldesigner_species_state(writing_context, species):
    has_mods = hasattr(species, "modifications") and species.modifications
    has_homo = hasattr(species, "homomultimer") and species.homomultimer > 1
    has_struct = hasattr(species, "structural_states") and species.structural_states
    if not has_mods and not has_homo and not has_struct:
        return None
    state = _make_celldesigner_element("state")
    if has_homo:
        state.append(
            _make_celldesigner_element("homodimer", text=str(species.homomultimer))
        )
    if has_struct:
        ss_list = _make_celldesigner_element("listOfStructuralStates")
        for ss in species.structural_states:
            if ss.value is not None:
                ss_list.append(
                    _make_celldesigner_element(
                        "structuralState",
                        attrs={"structuralState": ss.value},
                        text=ss.value,
                    )
                )
        state.append(ss_list)
    if has_mods:
        mod_list = _make_celldesigner_element("listOfModifications")
        # Sort modifications by their layout child order to preserve
        # the original XML order (modifications is a frozenset).
        sorted_mods = _sort_modifications_by_layout(writing_context, species)
        for modification in sorted_mods:
            mod_attrs = {}
            if modification.residue is not None:
                mod_attrs["residue"] = _strip_template_prefix(
                    modification.residue, species
                )
            mod_attrs["state"] = _modification_state_string(modification.state)
            mod_list.append(_make_celldesigner_element("modification", attrs=mod_attrs))
        state.append(mod_list)
    return state


# --- Complex species aliases ---


def _make_celldesigner_list_of_complex_species_aliases(writing_context):
    list_elem = _make_celldesigner_element("listOfComplexSpeciesAliases")
    # Top-level complexes
    for species in writing_context.map_.model.species:
        if not isinstance(species, Complex):
            continue
        _collect_complex_aliases(writing_context, species, list_elem)
    layout_order_index = _build_layout_order_index(writing_context.map_.layout)
    _sort_aliases_by_layout_order(list_elem, layout_order_index)
    return list_elem


def _collect_complex_aliases(writing_context, complex_, list_elem):
    """Collect complex aliases by walking layout containment."""
    for layout_key in _get_layouts(writing_context, complex_):
        if isinstance(layout_key, frozenset):
            continue
        if isinstance(layout_key, ComplexLayout):
            list_elem.append(
                _make_celldesigner_alias(
                    writing_context, layout_key, complex_, "complexSpeciesAlias"
                )
            )
            # Collect nested complex layouts from children
            _collect_nested_complex_aliases(writing_context, layout_key, list_elem)


def _collect_nested_complex_aliases(writing_context, parent_layout, list_elem):
    """Walk layout children and emit complexSpeciesAliases for nested complexes."""
    for child in parent_layout.layout_elements:
        if not isinstance(child, ComplexLayout):
            continue
        model_elem = _mapping(writing_context).get_mapping(child)
        if model_elem is None:
            continue
        list_elem.append(
            _make_celldesigner_alias(
                writing_context,
                child,
                model_elem,
                "complexSpeciesAlias",
                complex_alias_id=parent_layout.id_,
            )
        )
        # Recurse deeper
        _collect_nested_complex_aliases(writing_context, child, list_elem)


# --- Species aliases ---


def _make_celldesigner_list_of_species_aliases(writing_context):
    list_elem = _make_celldesigner_element("listOfSpeciesAliases")
    # Top-level species (non-complex, non-subunit)
    for species in writing_context.map_.model.species:
        if isinstance(species, Complex):
            continue
        if species in writing_context.subunit_to_complex:
            continue
        for layout_key in _get_layouts(writing_context, species):
            if isinstance(layout_key, frozenset):
                continue
            if isinstance(layout_key, CellDesignerNode):
                list_elem.append(
                    _make_celldesigner_alias(
                        writing_context, layout_key, species, "speciesAlias"
                    )
                )
    # Subunit species (inside complexes), recursively
    for species in writing_context.map_.model.species:
        if not isinstance(species, Complex):
            continue
        _collect_subunit_aliases(writing_context, species, list_elem)
    layout_order_index = _build_layout_order_index(writing_context.map_.layout)
    _sort_aliases_by_layout_order(list_elem, layout_order_index)
    return list_elem


def _collect_subunit_aliases(writing_context, complex_, list_elem):
    """Collect species aliases for subunits by walking layout containment.

    Instead of using the mapping (which conflates different
    instances of the same nested complex), walk the complex
    layout's children directly.
    """
    for complex_layout in _get_layouts(writing_context, complex_):
        if isinstance(complex_layout, frozenset):
            continue
        if not isinstance(complex_layout, ComplexLayout):
            continue
        _collect_aliases_from_layout_children(
            writing_context, complex_layout, complex_layout.id_, list_elem
        )


def _collect_aliases_from_layout_children(
    writing_context, parent_layout, complex_alias_id, list_elem
):
    """Walk layout children and emit speciesAliases for non-complex nodes."""
    for child in parent_layout.layout_elements:
        if isinstance(child, ComplexLayout):
            # Recurse into nested complex layouts
            _collect_aliases_from_layout_children(
                writing_context, child, child.id_, list_elem
            )
            continue
        if not isinstance(child, CellDesignerNode):
            continue
        # Skip non-species child layouts (structural states, modifications)
        if isinstance(
            child,
            (
                StructuralStateLayout,
                ModificationLayout,
            ),
        ):
            continue
        model_elem = _mapping(writing_context).get_mapping(child)
        if model_elem is None:
            continue
        list_elem.append(
            _make_celldesigner_alias(
                writing_context,
                child,
                model_elem,
                "speciesAlias",
                complex_alias_id=complex_alias_id,
            )
        )


def _find_compartment_alias_id(writing_context, species_layout):
    """Find the compartment alias containing this species layout."""
    species_center = species_layout.center()
    best_id = None
    best_area = float("inf")
    for comp in writing_context.map_.model.compartments:
        if comp.id_ == "default":
            continue
        for layout_key in _get_layouts(writing_context, comp):
            if isinstance(layout_key, frozenset):
                continue
            if isinstance(layout_key, _COMPARTMENT_LAYOUT_CLASSES):
                bbox = layout_key.bbox()
                north_west = bbox.north_west()
                south_east = bbox.south_east()
                if (
                    north_west.x <= species_center.x <= south_east.x
                    and north_west.y <= species_center.y <= south_east.y
                ):
                    area = bbox.width * bbox.height
                    if area < best_area:
                        best_area = area
                        best_id = layout_key.id_
    return best_id


def _make_celldesigner_alias(
    writing_context, layout, model, tag, complex_alias_id=None
):
    attrs = {
        "id": layout.id_,
        "species": _get_species_id(model, writing_context),
    }
    if complex_alias_id is not None:
        attrs["complexSpeciesAlias"] = complex_alias_id
    elif tag == "speciesAlias" or tag == "complexSpeciesAlias":
        comp_alias = _find_compartment_alias_id(writing_context, layout)
        if comp_alias is not None:
            attrs["compartmentAlias"] = comp_alias
    alias = _make_celldesigner_element(tag, attrs=attrs)
    activity_text = "active" if model.active else "inactive"
    alias.append(_make_celldesigner_element("activity", text=activity_text))
    alias.append(_make_celldesigner_element("bounds", attrs=_bounds_attrs(layout)))
    font_size = "12"
    if layout.label is not None and layout.label.font_size is not None:
        font_size = str(int(layout.label.font_size))
    alias.append(_make_celldesigner_element("font", attrs={"size": font_size}))
    alias.append(_make_celldesigner_element("view", attrs={"state": "usual"}))
    if tag == "complexSpeciesAlias":
        alias.append(
            _make_celldesigner_element("backupSize", attrs={"w": "0.0", "h": "0.0"})
        )
        alias.append(_make_celldesigner_element("backupView", attrs={"state": "none"}))
    # usualView
    usual = _make_celldesigner_element("usualView")
    usual.append(
        _make_celldesigner_element("innerPosition", attrs={"x": "0.0", "y": "0.0"})
    )
    usual.append(
        _make_celldesigner_element(
            "boxSize",
            attrs={
                "width": str(layout.width),
                "height": str(layout.height),
            },
        )
    )
    line_width = "2.0" if tag == "complexSpeciesAlias" else "1.0"
    usual.append(_make_celldesigner_element("singleLine", attrs={"width": line_width}))
    fill = getattr(layout, "fill", None)
    if fill is not None and fill is not NoneValue:
        paint_color = _color_hex(fill)
    else:
        paint_color = "fff7f7f7" if tag == "complexSpeciesAlias" else "ffccffcc"
    usual.append(
        _make_celldesigner_element(
            "paint", attrs={"color": paint_color, "scheme": "Color"}
        )
    )
    alias.append(usual)
    # briefView (same as usualView)
    brief = _make_celldesigner_element("briefView")
    brief.append(
        _make_celldesigner_element("innerPosition", attrs={"x": "0.0", "y": "0.0"})
    )
    brief.append(
        _make_celldesigner_element(
            "boxSize",
            attrs={
                "width": str(layout.width),
                "height": str(layout.height),
            },
        )
    )
    brief.append(_make_celldesigner_element("singleLine", attrs={"width": line_width}))
    brief.append(
        _make_celldesigner_element(
            "paint", attrs={"color": paint_color, "scheme": "Color"}
        )
    )
    alias.append(brief)
    alias.append(
        _make_celldesigner_element(
            "info",
            attrs={
                "state": "empty",
                "angle": "-1.5707963267948966",
            },
        )
    )
    return alias


# --- Proteins (templates) ---


def _make_celldesigner_list_of_proteins(writing_context):
    list_elem = _make_celldesigner_element("listOfProteins")
    for tmpl in sorted(
        writing_context.map_.model.species_templates, key=lambda t: t.id_ or ""
    ):
        if not isinstance(tmpl, ProteinTemplate):
            continue
        protein_type = "GENERIC"
        if isinstance(tmpl, ReceptorTemplate):
            protein_type = "RECEPTOR"
        elif isinstance(tmpl, IonChannelTemplate):
            protein_type = "ION_CHANNEL"
        elif isinstance(tmpl, TruncatedProteinTemplate):
            protein_type = "TRUNCATED"
        attrs = {
            "id": tmpl.id_,
            "name": _encode_name(tmpl.name) or "",
            "type": protein_type,
        }
        protein = _make_celldesigner_element("protein", attrs=attrs)
        if tmpl.modification_residues:
            mr_list = _make_celldesigner_element("listOfModificationResidues")
            for residue in sorted(tmpl.modification_residues, key=lambda r: r.id_):
                mr_attrs = {"id": _strip_template_prefix(residue, tmpl)}
                if residue.name is not None:
                    mr_attrs["name"] = residue.name
                # Compute angle from layout if available
                mr_attrs["angle"] = _find_residue_angle(writing_context, tmpl, residue)
                mr_list.append(
                    _make_celldesigner_element("modificationResidue", attrs=mr_attrs)
                )
            protein.append(mr_list)
        list_elem.append(protein)
    return list_elem


def _find_residue_angle(writing_context, template, residue):
    """Find the CellDesigner angle for a modification residue from layout data.

    Matches ModificationLayout children to residues by comparing the
    layout text label with the residue name. When the residue has no
    name, matches against unnamed ModificationLayouts. Searches both
    top-level species and subunits of complexes.

    Args:
        writing_context: The writing context.
        template: The protein template.
        residue: The modification residue to find the angle for.

    Returns:
        The CellDesigner angle as a string.
    """
    all_species = list(writing_context.map_.model.species)
    for species in writing_context.map_.model.species:
        subunits = getattr(species, "subunits", None)
        if subunits:
            all_species.extend(_collect_subunits(species))
    for species in all_species:
        tmpl = getattr(species, "template", None)
        if tmpl is not template:
            continue
        for layout_key in _get_layouts(writing_context, species):
            if isinstance(layout_key, frozenset):
                continue
            if not isinstance(layout_key, CellDesignerNode):
                continue
            children = getattr(layout_key, "layout_elements", None)
            if not children:
                continue
            # Build a mapping from XML residue id to layout child
            species_id = _get_species_id(species, writing_context)
            for child in children:
                if not isinstance(child, ModificationLayout):
                    continue
                # Match by residue id encoded in the layout id:
                # layout id = f"{species_id}_{xml_residue_id}_layout"
                prefix = f"{species_id}_"
                suffix = "_layout"
                if child.id_.startswith(prefix) and child.id_.endswith(suffix):
                    layout_residue_id = child.id_[len(prefix) : -len(suffix)]
                    xml_residue_id = _strip_template_prefix(residue, template)
                    if layout_residue_id == xml_residue_id:
                        return str(compute_cd_angle(child.position, layout_key))
    return "0.0"


def _collect_subunits(species):
    """Recursively collect all subunits of a species.

    Args:
        species: The parent species.

    Returns:
        A list of all nested subunit species.
    """
    result = []
    subunits = getattr(species, "subunits", None)
    if subunits:
        for subunit in subunits:
            result.append(subunit)
            result.extend(_collect_subunits(subunit))
    return result


# --- Genes, RNAs, AntisenseRNAs (templates) ---


def _make_celldesigner_list_of_genes(writing_context):
    """Build listOfGenes — one entry per GeneTemplate."""
    list_elem = _make_celldesigner_element("listOfGenes")
    for tmpl in sorted(
        writing_context.map_.model.species_templates, key=lambda t: t.id_ or ""
    ):
        if not isinstance(tmpl, GeneTemplate):
            continue
        gene_elem = _make_celldesigner_element(
            "gene",
            attrs={
                "type": "GENE",
                "id": tmpl.id_,
                "name": _encode_name(tmpl.name) or "",
            },
        )
        _append_template_regions(gene_elem, tmpl)
        list_elem.append(gene_elem)
    return list_elem


def _make_celldesigner_list_of_rnas(writing_context):
    """Build listOfRNAs — one entry per RNATemplate."""
    list_elem = _make_celldesigner_element("listOfRNAs")
    for tmpl in sorted(
        writing_context.map_.model.species_templates, key=lambda t: t.id_ or ""
    ):
        if not isinstance(tmpl, RNATemplate):
            continue
        rna_elem = _make_celldesigner_element(
            "RNA",
            attrs={
                "type": "RNA",
                "id": tmpl.id_,
                "name": _encode_name(tmpl.name) or "",
            },
        )
        _append_template_regions(rna_elem, tmpl)
        list_elem.append(rna_elem)
    return list_elem


def _make_celldesigner_list_of_antisense_rnas(writing_context):
    """Build listOfAntisenseRNAs — one entry per AntisenseRNATemplate."""
    list_elem = _make_celldesigner_element("listOfAntisenseRNAs")
    for tmpl in sorted(
        writing_context.map_.model.species_templates, key=lambda t: t.id_ or ""
    ):
        if not isinstance(tmpl, AntisenseRNATemplate):
            continue
        arna_elem = _make_celldesigner_element(
            "antisenseRNA",
            attrs={
                "type": "ANTISENSE_RNA",
                "id": tmpl.id_,
                "name": _encode_name(tmpl.name) or "",
            },
        )
        _append_template_regions(arna_elem, tmpl)
        list_elem.append(arna_elem)
    return list_elem


_REGION_CLASS_TO_CD_TYPE = {
    ModificationSite: "Modification Site",
    RegulatoryRegion: "RegulatoryRegion",
    TranscriptionStartingSiteL: "transcriptionStartingSiteL",
    TranscriptionStartingSiteR: "transcriptionStartingSiteR",
    CodingRegion: "CodingRegion",
    ProteinBindingDomain: "proteinBindingDomain",
}


def _append_template_regions(elem, tmpl):
    """Append listOfRegions to a gene/RNA/antisenseRNA element if regions exist."""
    regions = getattr(tmpl, "regions", None)
    if not regions:
        return
    region_list = _make_celldesigner_element("listOfRegions")
    for region in sorted(regions, key=lambda r: r.id_ or ""):
        region_type = _REGION_CLASS_TO_CD_TYPE.get(type(region), "proteinBindingDomain")
        region_attrs = {
            "id": _strip_template_prefix(region, tmpl),
            "name": region.name or "",
            "size": "0.1",
            "pos": "0.5",
            "type": region_type,
        }
        region_list.append(_make_celldesigner_element("region", attrs=region_attrs))
    elem.append(region_list)


def _all_species_recursive(writing_context):
    """Yield all species including subunits, sorted by id."""
    result = []

    def _collect(species):
        result.append(species)
        if isinstance(species, Complex):
            for sub in species.subunits:
                _collect(sub)

    for species in writing_context.map_.model.species:
        _collect(species)
    return sorted(result, key=lambda s: s.id_ or "")


# --- Compartments ---


def _make_celldesigner_list_of_compartments(writing_context):
    list_elem = _make_lxml_element("listOfCompartments")
    for comp in sorted(
        writing_context.map_.model.compartments, key=lambda c: c.id_ or ""
    ):
        comp_name = _encode_name(comp.name)
        attrs = {
            "id": comp.id_,
            "metaid": comp.id_,
            "size": "1",
            "units": "volume",
        }
        if comp_name is not None:
            attrs["name"] = comp_name
        outside = getattr(comp, "outside", None)
        if outside is not None:
            attrs["outside"] = outside.id_
        compartment_element = _make_lxml_element("compartment", attrs=attrs)
        notes_element = _build_sbml_notes(writing_context, comp)
        if notes_element is not None:
            compartment_element.append(notes_element)
        _append_compartment_annotation(writing_context, compartment_element, comp)
        list_elem.append(compartment_element)
    return list_elem


def _append_compartment_annotation(writing_context, compartment_element, compartment):
    """Append ``<annotation>`` with CD extension + optional RDF to a compartment.

    Every annotated compartment in the CellDesigner corpus carries a
    ``<celldesigner:extension>`` sibling to the ``<rdf:RDF>`` block, with a
    ``<celldesigner:name>`` child when the compartment has a non-empty name.
    We emit this whenever the compartment has annotations or a non-empty
    name, and skip the whole ``<annotation>`` otherwise.
    """
    has_rdf = writing_context.with_annotations and bool(
        writing_context.element_to_annotations.get(compartment)
    )
    comp_name = _encode_name(compartment.name)
    if not has_rdf and not comp_name:
        return
    annotation = _make_lxml_element("annotation")
    extension = _make_celldesigner_element("extension")
    if comp_name:
        extension.append(_make_celldesigner_element("name", text=comp_name))
    annotation.append(extension)
    _append_rdf_to_annotation(writing_context, annotation, compartment, compartment.id_)
    compartment_element.append(annotation)


# --- SBML species ---


def _make_celldesigner_list_of_species(writing_context):
    list_elem = _make_lxml_element("listOfSpecies")
    seen_ids = set()
    for species in sorted(
        writing_context.map_.model.species, key=lambda s: s.id_ or ""
    ):
        # Skip subunits — they are only in listOfIncludedSpecies
        if species in writing_context.subunit_to_complex:
            continue
        species_id = _get_species_id(species, writing_context)
        if species_id in seen_ids:
            continue
        seen_ids.add(species_id)
        list_elem.append(_make_sbml_document_species(writing_context, species))
    return list_elem


def _make_sbml_document_species(writing_context, species):
    species_id = _get_species_id(species, writing_context)
    comp = getattr(species, "compartment", None)
    comp_id = comp.id_ if comp is not None else "default"
    attrs = {
        "metaid": species_id,
        "id": species_id,
        "name": _encode_name(species.name) or "",
        "compartment": comp_id,
        "initialAmount": "0",
        "hasOnlySubstanceUnits": "false",
        "constant": "false",
        "boundaryCondition": "false",
    }
    species_element = _make_lxml_element("species", attrs=attrs)
    # notes
    notes_element = _build_sbml_notes(writing_context, species)
    if notes_element is not None:
        species_element.append(notes_element)
    # annotation with CD extension
    annotation = _make_lxml_element("annotation")
    extension = _make_celldesigner_element("extension")
    extension.append(_make_celldesigner_element("positionToCompartment", text="inside"))
    extension.append(_make_celldesigner_species_identity(writing_context, species))
    # listOfCatalyzedReactions
    catalyzed = _find_catalyzed_reactions(writing_context, species)
    if catalyzed:
        cat_list = _make_celldesigner_element("listOfCatalyzedReactions")
        for rxn_id in catalyzed:
            cat_list.append(
                _make_celldesigner_element("catalyzed", attrs={"reaction": rxn_id})
            )
        extension.append(cat_list)
    annotation.append(extension)
    _append_rdf_to_annotation(writing_context, annotation, species, species_id)
    species_element.append(annotation)
    return species_element


def _find_catalyzed_reactions(writing_context, species):
    """Find reactions catalyzed by this species."""
    result = []
    for reaction in writing_context.map_.model.reactions:
        for modifier in reaction.modifiers:
            if isinstance(modifier, Catalyzer) and modifier.referred_species is species:
                result.append(reaction.id_)
    return sorted(result)


# --- Reactions ---


def _make_celldesigner_list_of_reactions(writing_context):
    list_elem = _make_lxml_element("listOfReactions")
    for reaction in writing_context.map_.model.reactions:
        layout_keys = _get_layouts(writing_context, reaction)
        frozensets = [lk for lk in layout_keys if isinstance(lk, frozenset)]
        if not frozensets:
            list_elem.append(
                _make_celldesigner_reaction(writing_context, reaction, None, None)
            )
        else:
            for frozenset_mapping in frozensets:
                reaction_layout = _get_reaction_layout(frozenset_mapping)
                list_elem.append(
                    _make_celldesigner_reaction(
                        writing_context,
                        reaction,
                        frozenset_mapping,
                        reaction_layout,
                    )
                )
    for modulation in writing_context.map_.model.modulations:
        layout_keys = _get_layouts(writing_context, modulation)
        frozensets = [lk for lk in layout_keys if isinstance(lk, frozenset)]
        if not frozensets:
            mod_rxn = _make_celldesigner_modulation_reaction(
                writing_context, modulation, None
            )
            if mod_rxn is not None:
                list_elem.append(mod_rxn)
        else:
            for frozenset_mapping in frozensets:
                mod_rxn = _make_celldesigner_modulation_reaction(
                    writing_context, modulation, frozenset_mapping
                )
                if mod_rxn is not None:
                    list_elem.append(mod_rxn)
    layout_order_index = _build_layout_order_index(writing_context.map_.layout)
    _sort_reactions_by_layout_order(list_elem, layout_order_index)
    return list_elem


def _make_celldesigner_reaction(
    writing_context, reaction, frozenset_mapping, reaction_layout
):
    # Derive the XML id from the layout when available (supports
    # multiple visual copies of the same reaction).
    if reaction_layout is not None:
        xml_id = reaction_layout.id_.removesuffix("_layout")
    else:
        xml_id = reaction.id_
    attrs = {
        "metaid": xml_id,
        "id": xml_id,
        "reversible": "true" if reaction.reversible else "false",
    }
    reaction_element = _make_lxml_element("reaction", attrs=attrs)

    # notes
    notes_element = _build_sbml_notes(writing_context, reaction)
    if notes_element is not None:
        reaction_element.append(notes_element)

    # CD extension
    annotation = _make_lxml_element("annotation")
    extension = _make_celldesigner_element("extension")
    reaction_type = _CLASS_TO_REACTION_TYPE.get(type(reaction), "STATE_TRANSITION")
    extension.append(_make_celldesigner_element("reactionType", text=reaction_type))

    # Split reactants/products into base + links using the base flag.
    # Sort by layout arc order since reaction.reactants/products are
    # frozensets with no guaranteed iteration order.
    all_reactants = list(reaction.reactants)
    all_products = list(reaction.products)
    if reaction_layout is not None:
        reactant_arc_order = _build_arc_alias_order(
            writing_context,
            reaction_layout,
            ConsumptionLayout,
        )
        product_arc_order = _build_arc_alias_order(
            writing_context,
            reaction_layout,
            ProductionLayout,
        )
        all_reactants.sort(
            key=lambda r: _participant_layout_position(
                writing_context,
                r,
                reaction,
                frozenset_mapping,
                reaction_layout,
                True,
                reactant_arc_order,
            )
        )
        all_products.sort(
            key=lambda p: _participant_layout_position(
                writing_context,
                p,
                reaction,
                frozenset_mapping,
                reaction_layout,
                False,
                product_arc_order,
            )
        )
    base_reactants, link_reactants = _split_base_and_links(all_reactants)
    base_products, link_products = _split_base_and_links(all_products)
    is_left_t = isinstance(reaction, HeterodimerAssociation)
    is_right_t = isinstance(
        reaction,
        (
            Dissociation,
            Truncation,
        ),
    )

    # baseReactants — for left-T with 1 model reactant but 2 visual
    # copies (stoichiometry), use consumption arcs to find all aliases.
    base_reactants_element = _make_celldesigner_element("baseReactants")
    if is_left_t and len(base_reactants) == 1 and reaction_layout is not None:
        base_species = base_reactants[0].referred_species
        for layout_element_item in writing_context.map_.layout.layout_elements:
            if (
                isinstance(layout_element_item, ConsumptionLayout)
                and layout_element_item.source is reaction_layout
            ):
                # Only base arcs: target must map to the base species
                target_model = _mapping(writing_context).get_mapping(
                    layout_element_item.target
                )
                if target_model is not None:
                    if target_model is not base_species:
                        continue
                alias_layout = layout_element_item.target
                base_reactants_element.append(
                    _make_celldesigner_base_participant_from_layout(
                        writing_context,
                        base_species,
                        alias_layout,
                        "baseReactant",
                        reaction_layout,
                        is_start=True,
                    )
                )
    else:
        for reactant in base_reactants:
            base_reactants_element.append(
                _make_celldesigner_base_participant(
                    writing_context,
                    reactant,
                    "baseReactant",
                    frozenset_mapping,
                    reaction_layout,
                    is_start=True,
                    reaction=reaction,
                )
            )
    extension.append(base_reactants_element)

    # baseProducts — same for right-T with 1 model product but 2 aliases.
    base_products_element = _make_celldesigner_element("baseProducts")
    if is_right_t and len(base_products) == 1 and reaction_layout is not None:
        base_species = base_products[0].referred_species
        for layout_element_item in writing_context.map_.layout.layout_elements:
            if (
                isinstance(layout_element_item, ProductionLayout)
                and layout_element_item.source is reaction_layout
            ):
                target_model = _mapping(writing_context).get_mapping(
                    layout_element_item.target
                )
                if target_model is not None:
                    if target_model is not base_species:
                        continue
                alias_layout = layout_element_item.target
                base_products_element.append(
                    _make_celldesigner_base_participant_from_layout(
                        writing_context,
                        base_species,
                        alias_layout,
                        "baseProduct",
                        reaction_layout,
                        is_start=False,
                    )
                )
    else:
        for product in base_products:
            base_products_element.append(
                _make_celldesigner_base_participant(
                    writing_context,
                    product,
                    "baseProduct",
                    frozenset_mapping,
                    reaction_layout,
                    is_start=False,
                    reaction=reaction,
                )
            )
    extension.append(base_products_element)

    # For left-T reactions, compute base reactant aliases to distinguish
    # base arcs from link arcs (both are ConsumptionLayout).
    base_reactant_aliases = set()
    if is_left_t and reaction_layout is not None:
        base_species_set = {r.referred_species for r in base_reactants}
        for arc in writing_context.map_.layout.layout_elements:
            if (
                isinstance(arc, ConsumptionLayout)
                and arc.source is reaction_layout
                and arc.target is not None
            ):
                target_model = _mapping(writing_context).get_mapping(arc.target)
                if target_model is not None and target_model in base_species_set:
                    base_reactant_aliases.add(arc.target)

    # listOfReactantLinks — derive from layout arcs to handle
    # multiple visual copies of the same model element.
    reactant_links_element = _make_celldesigner_element("listOfReactantLinks")
    if reaction_layout is not None:
        if is_left_t:
            link_consumption_arcs = [
                arc
                for arc in _collect_arcs_for_reaction(
                    writing_context,
                    reaction_layout,
                    ConsumptionLayout,
                )
                if arc.target not in base_reactant_aliases
            ]
        else:
            base_reactant_alias = reaction_layout.source
            link_consumption_arcs = _collect_arcs_for_reaction(
                writing_context,
                reaction_layout,
                ConsumptionLayout,
                exclude_alias=base_reactant_alias,
            )
        for arc_layout in link_consumption_arcs:
            reactant_links_element.append(
                _make_celldesigner_participant_link_from_layout(
                    writing_context,
                    arc_layout,
                    "reactantLink",
                    "reactant",
                    reaction_layout,
                )
            )
    else:
        for reactant in link_reactants:
            reactant_links_element.append(
                _make_celldesigner_participant_link(
                    writing_context,
                    reactant,
                    "reactantLink",
                    "reactant",
                    frozenset_mapping,
                    reaction_layout=reaction_layout,
                    reaction=reaction,
                )
            )
    extension.append(reactant_links_element)

    # listOfProductLinks — same arc-driven approach.
    product_links_element = _make_celldesigner_element("listOfProductLinks")
    if reaction_layout is not None:
        if is_right_t:
            # Right-T: exclude all base product arcs by their target alias
            base_product_aliases = set()
            base_product_species_set = {p.referred_species for p in base_products}
            for arc in writing_context.map_.layout.layout_elements:
                if (
                    isinstance(arc, ProductionLayout)
                    and arc.source is reaction_layout
                    and arc.target is not None
                ):
                    target_model = _mapping(writing_context).get_mapping(arc.target)
                    if (
                        target_model is not None
                        and target_model in base_product_species_set
                    ):
                        base_product_aliases.add(arc.target)
            link_production_arcs = [
                arc
                for arc in _collect_arcs_for_reaction(
                    writing_context,
                    reaction_layout,
                    ProductionLayout,
                )
                if arc.target not in base_product_aliases
            ]
        else:
            base_product_alias = reaction_layout.target
            link_production_arcs = _collect_arcs_for_reaction(
                writing_context,
                reaction_layout,
                ProductionLayout,
                exclude_alias=base_product_alias,
            )
        for arc_layout in link_production_arcs:
            product_links_element.append(
                _make_celldesigner_participant_link_from_layout(
                    writing_context,
                    arc_layout,
                    "productLink",
                    "product",
                    reaction_layout,
                )
            )
    else:
        for product in link_products:
            product_links_element.append(
                _make_celldesigner_participant_link(
                    writing_context,
                    product,
                    "productLink",
                    "product",
                    frozenset_mapping,
                    reaction_layout=reaction_layout,
                    reaction=reaction,
                )
            )
    extension.append(product_links_element)

    # connectScheme + editPoints
    _make_celldesigner_connect_scheme(
        writing_context,
        extension,
        reaction,
        reaction_layout,
        frozenset_mapping,
        base_reactants,
        base_products,
        is_left_t,
        is_right_t,
    )

    # listOfModification
    mod_list = _make_celldesigner_element("listOfModification")
    modifiers = sorted(reaction.modifiers, key=lambda m: m.id_ or "")
    for modifier in modifiers:
        species = modifier.referred_species
        if isinstance(species, BooleanLogicGate):
            # Write gate entry + per-input entries
            gate_mods = _make_celldesigner_gate_modifications(
                writing_context, modifier, species, reaction_layout, frozenset_mapping
            )
            for gm in gate_mods:
                mod_list.append(gm)
        else:
            modification_element = _make_celldesigner_modification(
                writing_context, modifier, reaction_layout, frozenset_mapping
            )
            if modification_element is not None:
                mod_list.append(modification_element)
    extension.append(mod_list)

    # line
    extension.append(
        _make_celldesigner_element(
            "line", attrs=_get_line_attributes(reaction_layout, include_type=True)
        )
    )

    annotation.append(extension)
    _append_rdf_to_annotation(writing_context, annotation, reaction, xml_id)
    reaction_element.append(annotation)

    # SBML listOfReactants — base first, then links.
    # For left-T with stoichiometry, duplicate from arcs.
    list_of_reactants = _make_lxml_element("listOfReactants")
    if is_left_t and len(base_reactants) == 1 and reaction_layout is not None:
        base_species = base_reactants[0].referred_species
        for layout_element_item in writing_context.map_.layout.layout_elements:
            if (
                isinstance(layout_element_item, ConsumptionLayout)
                and layout_element_item.source is reaction_layout
            ):
                target_model = _mapping(writing_context).get_mapping(
                    layout_element_item.target
                )
                if target_model is not None:
                    if target_model is not base_species:
                        continue
                sbml_species = writing_context.subunit_to_complex.get(
                    base_species, base_species
                )
                alias_id = (
                    layout_element_item.target.id_ if layout_element_item.target else ""
                )
                species_reference = _make_lxml_element(
                    "speciesReference",
                    attrs={"species": _get_species_id(sbml_species, writing_context)},
                )
                species_reference_annotation = _make_lxml_element("annotation")
                species_reference_extension = _make_celldesigner_element("extension")
                species_reference_extension.append(
                    _make_celldesigner_element("alias", text=alias_id)
                )
                species_reference_annotation.append(species_reference_extension)
                species_reference.append(species_reference_annotation)
                list_of_reactants.append(species_reference)
    else:
        for reactant in base_reactants:
            list_of_reactants.append(
                _make_sbml_document_species_reference(
                    writing_context,
                    reactant,
                    frozenset_mapping,
                    reaction=reaction,
                    reaction_layout=reaction_layout,
                    is_start=True,
                )
            )
    if reaction_layout is not None:
        if is_left_t:
            # Reuse already-computed base reactant aliases to exclude
            for arc_layout in _collect_arcs_for_reaction(
                writing_context,
                reaction_layout,
                ConsumptionLayout,
            ):
                if arc_layout.target not in base_reactant_aliases:
                    list_of_reactants.append(
                        _make_sbml_document_species_reference_from_layout(
                            writing_context,
                            arc_layout,
                        )
                    )
        else:
            base_reactant_alias = reaction_layout.source
            for arc_layout in _collect_arcs_for_reaction(
                writing_context,
                reaction_layout,
                ConsumptionLayout,
                exclude_alias=base_reactant_alias,
            ):
                list_of_reactants.append(
                    _make_sbml_document_species_reference_from_layout(
                        writing_context,
                        arc_layout,
                    )
                )
    else:
        for reactant in link_reactants:
            list_of_reactants.append(
                _make_sbml_document_species_reference(
                    writing_context,
                    reactant,
                    frozenset_mapping,
                    reaction=reaction,
                    reaction_layout=reaction_layout,
                    is_start=True,
                )
            )
    reaction_element.append(list_of_reactants)

    # SBML listOfProducts — same for right-T.
    list_of_products = _make_lxml_element("listOfProducts")
    if is_right_t and len(base_products) == 1 and reaction_layout is not None:
        base_species = base_products[0].referred_species
        for layout_element_item in writing_context.map_.layout.layout_elements:
            if (
                isinstance(layout_element_item, ProductionLayout)
                and layout_element_item.source is reaction_layout
            ):
                target_model = _mapping(writing_context).get_mapping(
                    layout_element_item.target
                )
                if target_model is not None:
                    if target_model is not base_species:
                        continue
                sbml_species = writing_context.subunit_to_complex.get(
                    base_species, base_species
                )
                alias_id = (
                    layout_element_item.target.id_ if layout_element_item.target else ""
                )
                species_reference = _make_lxml_element(
                    "speciesReference",
                    attrs={"species": _get_species_id(sbml_species, writing_context)},
                )
                species_reference_annotation = _make_lxml_element("annotation")
                species_reference_extension = _make_celldesigner_element("extension")
                species_reference_extension.append(
                    _make_celldesigner_element("alias", text=alias_id)
                )
                species_reference_annotation.append(species_reference_extension)
                species_reference.append(species_reference_annotation)
                list_of_products.append(species_reference)
    else:
        for product in base_products:
            list_of_products.append(
                _make_sbml_document_species_reference(
                    writing_context,
                    product,
                    frozenset_mapping,
                    reaction=reaction,
                    reaction_layout=reaction_layout,
                    is_start=False,
                )
            )
    if reaction_layout is not None:
        if is_right_t:
            # Reuse already-computed base product aliases to exclude
            for arc_layout in _collect_arcs_for_reaction(
                writing_context,
                reaction_layout,
                ProductionLayout,
            ):
                if arc_layout.target not in base_product_aliases:
                    list_of_products.append(
                        _make_sbml_document_species_reference_from_layout(
                            writing_context,
                            arc_layout,
                        )
                    )
        else:
            base_product_alias = reaction_layout.target
            for arc_layout in _collect_arcs_for_reaction(
                writing_context,
                reaction_layout,
                ProductionLayout,
                exclude_alias=base_product_alias,
            ):
                list_of_products.append(
                    _make_sbml_document_species_reference_from_layout(
                        writing_context,
                        arc_layout,
                    )
                )
    else:
        for product in link_products:
            list_of_products.append(
                _make_sbml_document_species_reference(
                    writing_context,
                    product,
                    frozenset_mapping,
                    reaction=reaction,
                    reaction_layout=reaction_layout,
                    is_start=False,
                )
            )
    reaction_element.append(list_of_products)

    # SBML listOfModifiers
    if modifiers:
        list_of_modifiers = _make_lxml_element("listOfModifiers")
        for modifier in modifiers:
            species = modifier.referred_species
            if isinstance(species, BooleanLogicGate):
                # Write each input species as a separate modifier
                for inp in sorted(species.inputs, key=lambda s: s.id_ or ""):
                    input_species = inp.element
                    sbml_inp = writing_context.subunit_to_complex.get(
                        input_species, input_species
                    )
                    alias_layout = (
                        _find_layout_for_species_in_frozenset(
                            writing_context, input_species, frozenset_mapping
                        )
                        if frozenset_mapping
                        else None
                    )
                    if alias_layout is None:
                        for layout_key in _get_layouts(writing_context, input_species):
                            if isinstance(layout_key, frozenset):
                                continue
                            if isinstance(layout_key, CellDesignerNode):
                                alias_layout = layout_key
                                break
                    alias_id = alias_layout.id_ if alias_layout else ""
                    modifier_species_reference = _make_lxml_element(
                        "modifierSpeciesReference",
                        attrs={"species": _get_species_id(sbml_inp, writing_context)},
                    )
                    modifier_reference_annotation = _make_lxml_element("annotation")
                    modifier_reference_extension = _make_celldesigner_element(
                        "extension"
                    )
                    modifier_reference_extension.append(
                        _make_celldesigner_element("alias", text=alias_id)
                    )
                    modifier_reference_annotation.append(modifier_reference_extension)
                    modifier_species_reference.append(modifier_reference_annotation)
                    list_of_modifiers.append(modifier_species_reference)
                continue
            sbml_species = writing_context.subunit_to_complex.get(species, species)
            alias_layout = (
                _find_layout_for_species_in_frozenset(
                    writing_context, species, frozenset_mapping
                )
                if frozenset_mapping
                else None
            )
            alias_id = alias_layout.id_ if alias_layout else ""
            modifier_reference_attributes = {
                "species": _get_species_id(sbml_species, writing_context)
            }
            if modifier.metaid is not None:
                modifier_reference_attributes["metaid"] = _unique_metaid(
                    writing_context, modifier.metaid
                )
            modifier_species_reference = _make_lxml_element(
                "modifierSpeciesReference", attrs=modifier_reference_attributes
            )
            modifier_reference_annotation = _make_lxml_element("annotation")
            modifier_reference_extension = _make_celldesigner_element("extension")
            modifier_reference_extension.append(
                _make_celldesigner_element("alias", text=alias_id)
            )
            modifier_reference_annotation.append(modifier_reference_extension)
            modifier_species_reference.append(modifier_reference_annotation)
            list_of_modifiers.append(modifier_species_reference)
        reaction_element.append(list_of_modifiers)

    return reaction_element


def _split_base_and_links(participants):
    """Split participants into base and link using the base flag."""
    base = [p for p in participants if p.base]
    link = [p for p in participants if not p.base]
    return base, link


def _make_sbml_document_species_reference(
    writing_context,
    participant,
    frozenset_mapping,
    reaction=None,
    reaction_layout=None,
    is_start=True,
):
    """Build an SBML speciesReference element."""
    species = participant.referred_species
    sbml_species = writing_context.subunit_to_complex.get(species, species)
    if reaction is not None:
        alias_layout = _find_layout_for_participant(
            writing_context,
            participant,
            reaction,
            frozenset_mapping,
            reaction_layout,
            is_start,
        )
    else:
        alias_layout = (
            _find_layout_for_species_in_frozenset(
                writing_context, species, frozenset_mapping
            )
            if frozenset_mapping
            else None
        )
    alias_id = alias_layout.id_ if alias_layout else ""
    sr_attrs = {"species": _get_species_id(sbml_species, writing_context)}
    # Write the participant id_ as metaid so the reader can recover it.
    # The reader prefers metaid over composite ids for reactant/product ids.
    participant_metaid = participant.metaid or participant.id_
    if participant_metaid:
        sr_attrs["metaid"] = _unique_metaid(writing_context, participant_metaid)
    if participant.stoichiometry is not None:
        sr_attrs["stoichiometry"] = str(participant.stoichiometry)
    species_reference = _make_lxml_element("speciesReference", attrs=sr_attrs)
    species_reference_annotation = _make_lxml_element("annotation")
    species_reference_extension = _make_celldesigner_element("extension")
    species_reference_extension.append(
        _make_celldesigner_element("alias", text=alias_id)
    )
    species_reference_annotation.append(species_reference_extension)
    species_reference.append(species_reference_annotation)
    return species_reference


def _make_sbml_document_species_reference_from_layout(writing_context, arc_layout):
    """Build an SBML speciesReference from a known arc layout.

    Used when deriving link participants from layout arcs rather than
    from model participants (which may have been deduplicated).

    Args:
        writing_context: The writing context.
        arc_layout: The ConsumptionLayout or ProductionLayout arc.

    Returns:
        The lxml speciesReference element.
    """
    alias_layout = arc_layout.target
    alias_id = alias_layout.id_ if alias_layout else ""
    species = _mapping(writing_context).get_mapping(alias_layout)
    sbml_species = writing_context.subunit_to_complex.get(species, species)
    sr_attrs = {"species": _get_species_id(sbml_species, writing_context)}
    arc_model = _mapping(writing_context).get_mapping(arc_layout)
    if arc_model is not None and hasattr(arc_model, "id_"):
        participant_metaid = arc_model.metaid or arc_model.id_
        if participant_metaid:
            sr_attrs["metaid"] = _unique_metaid(writing_context, participant_metaid)
    species_reference = _make_lxml_element("speciesReference", attrs=sr_attrs)
    species_reference_annotation = _make_lxml_element("annotation")
    species_reference_extension = _make_celldesigner_element("extension")
    species_reference_extension.append(
        _make_celldesigner_element("alias", text=alias_id)
    )
    species_reference_annotation.append(species_reference_extension)
    species_reference.append(species_reference_annotation)
    return species_reference


def _make_celldesigner_base_participant_from_layout(
    writing_context, species, alias_layout, tag, reaction_layout, is_start
):
    """Build a baseReactant/baseProduct from a known alias layout."""
    alias_id = alias_layout.id_ if alias_layout else ""
    elem = _make_celldesigner_element(
        tag,
        attrs={
            "species": _get_species_id(species, writing_context),
            "alias": alias_id,
        },
    )
    if reaction_layout is not None and alias_layout is not None:
        ref_point = _find_arc_endpoint_for_species(
            writing_context, reaction_layout, alias_layout, is_start
        )
        if ref_point is not None:
            anchor = _infer_anchor_position(alias_layout, ref_point)
            if anchor is not None:
                elem.append(
                    _make_celldesigner_element("linkAnchor", attrs={"position": anchor})
                )
    return elem


def _make_celldesigner_base_participant(
    writing_context,
    participant,
    tag,
    frozenset_mapping,
    reaction_layout,
    is_start,
    reaction=None,
):
    """Build a baseReactant or baseProduct element."""
    species = participant.referred_species
    if reaction is not None:
        alias_layout = _find_layout_for_participant(
            writing_context,
            participant,
            reaction,
            frozenset_mapping,
            reaction_layout,
            is_start,
        )
    else:
        alias_layout = (
            _find_layout_for_species_in_frozenset(
                writing_context, species, frozenset_mapping
            )
            if frozenset_mapping
            else None
        )
    alias_id = alias_layout.id_ if alias_layout else ""
    elem = _make_celldesigner_element(
        tag,
        attrs={
            "species": _get_species_id(species, writing_context),
            "alias": alias_id,
        },
    )
    if reaction_layout is not None and alias_layout is not None:
        ref_point = _find_arc_endpoint_for_species(
            writing_context, reaction_layout, alias_layout, is_start
        )
        if ref_point is not None:
            anchor = _infer_anchor_position(alias_layout, ref_point)
            if anchor is not None:
                elem.append(
                    _make_celldesigner_element("linkAnchor", attrs={"position": anchor})
                )
    return elem


def _find_arc_endpoint_for_species(
    writing_context, reaction_layout, species_layout, is_start
):
    """Find the arc endpoint connecting a species to a reaction.

    Uses the arc's source/target to find the correct arc for this
    species, then returns the endpoint closest to the species.
    """
    arc_cls = ConsumptionLayout if is_start else ProductionLayout
    # source is always the reaction, target is always the species
    for layout_element_item in writing_context.map_.layout.layout_elements:
        if not isinstance(layout_element_item, arc_cls):
            continue
        if (
            layout_element_item.source is reaction_layout
            and layout_element_item.target is species_layout
        ):
            return (
                layout_element_item.points()[0]
                if is_start
                else layout_element_item.points()[-1]
            )
    # Fallback to reaction path start/end
    points = reaction_layout.points()
    return points[0] if is_start else points[-1]


def _make_celldesigner_connect_scheme(
    writing_context,
    extension,
    reaction,
    reaction_layout,
    frozenset_mapping,
    base_reactants,
    base_products,
    is_left_t,
    is_right_t,
):
    """Build connectScheme and editPoints for a reaction."""
    writing = _writing
    if reaction_layout is None:
        # No layout — write minimal fallback
        connect_scheme = _make_celldesigner_element(
            "connectScheme",
            attrs={
                "connectPolicy": "direct",
                "rectangleIndex": "0",
            },
        )
        line_direction_list = _make_celldesigner_element("listOfLineDirection")
        line_direction_list.append(
            _make_celldesigner_element(
                "lineDirection",
                attrs={
                    "index": "0",
                    "value": "unknown",
                },
            )
        )
        connect_scheme.append(line_direction_list)
        extension.append(connect_scheme)
        return
    if is_left_t:
        # Find base reactant layouts and their consumption arcs
        reactant_layouts = []
        consumption_layouts = []
        base_species_set = {r.referred_species for r in base_reactants}
        for base_reactant in base_reactants:
            br_layout = (
                _find_layout_for_species_in_frozenset(
                    writing_context, base_reactant.referred_species, frozenset_mapping
                )
                if frozenset_mapping
                else None
            )
            if br_layout is None:
                continue
            for layout_element_item in writing_context.map_.layout.layout_elements:
                if (
                    isinstance(layout_element_item, ConsumptionLayout)
                    and layout_element_item.source is reaction_layout
                    and layout_element_item.target is br_layout
                ):
                    reactant_layouts.append(br_layout)
                    consumption_layouts.append(layout_element_item)
                    break
        product_layout = None
        if base_products:
            product_layout = (
                _find_layout_for_species_in_frozenset(
                    writing_context,
                    base_products[0].referred_species,
                    frozenset_mapping,
                )
                if frozenset_mapping
                else None
            )
        computed = False
        if len(reactant_layouts) >= 2 and product_layout is not None:
            # Try both reactant orderings; pick the one whose
            # roundtrip T-junction position is closest.
            t_junction = reaction_layout.points()[0]
            best_result = None
            best_dist = float("inf")
            for perm in [
                (reactant_layouts, consumption_layouts),
                (reactant_layouts[::-1], consumption_layouts[::-1]),
            ]:
                rl, cl = perm
                result = writing.inverse_edit_points_left_t_shape(
                    reaction_layout,
                    rl,
                    product_layout,
                    cl,
                )
                ep = result[0][-1]
                origin = rl[0].center()
                unit_x = rl[1].center()
                unit_y = product_layout.center()
                origin, unit_x, unit_y = writing._make_non_degenerate_frame(
                    origin, unit_x, unit_y
                )
                trans = get_transformation_for_frame(origin, unit_x, unit_y)
                roundtrip = ep.transformed(trans)
                dist = (roundtrip.x - t_junction.x) ** 2 + (
                    roundtrip.y - t_junction.y
                ) ** 2
                if math.isfinite(dist) and dist < best_dist:
                    best_dist = dist
                    best_result = result
            if best_result is None:
                best_result = writing.inverse_edit_points_left_t_shape(
                    reaction_layout,
                    reactant_layouts,
                    product_layout,
                    consumption_layouts,
                )
            (
                all_edit_points,
                num0,
                num1,
                num2,
                t_shape_index,
                product_anchor_name,
                reactant_anchor_names,
            ) = best_result
            connect_scheme = _make_celldesigner_element(
                "connectScheme", attrs={"connectPolicy": "direct"}
            )
            line_direction_list = _make_celldesigner_element("listOfLineDirection")
            for arm_idx, arm_count in enumerate([num0, num1, num2]):
                for i in range(arm_count + 1):
                    line_direction_list.append(
                        _make_celldesigner_element(
                            "lineDirection",
                            attrs={
                                "arm": str(arm_idx),
                                "index": str(i),
                                "value": "unknown",
                            },
                        )
                    )
            connect_scheme.append(line_direction_list)
            extension.append(connect_scheme)
            edit_points_attributes = {
                "num0": str(num0),
                "num1": str(num1),
                "num2": str(num2),
                "tShapeIndex": str(t_shape_index),
            }
            extension.append(
                _make_celldesigner_element(
                    "editPoints",
                    attrs=edit_points_attributes,
                    text=writing.points_to_edit_points_text(all_edit_points),
                )
            )
            computed = True
        if not computed:
            # Fallback
            connect_scheme = _make_celldesigner_element(
                "connectScheme", attrs={"connectPolicy": "direct"}
            )
            line_direction_list = _make_celldesigner_element("listOfLineDirection")
            for arm in range(3):
                line_direction_list.append(
                    _make_celldesigner_element(
                        "lineDirection",
                        attrs={
                            "arm": str(arm),
                            "index": "0",
                            "value": "unknown",
                        },
                    )
                )
            connect_scheme.append(line_direction_list)
            extension.append(connect_scheme)
            extension.append(
                _make_celldesigner_element(
                    "editPoints",
                    attrs={
                        "num0": "0",
                        "num1": "0",
                        "num2": "0",
                        "tShapeIndex": "0",
                    },
                    text="0.5,0.5",
                )
            )
    elif is_right_t:
        reactant_layout = None
        if base_reactants:
            reactant_layout = (
                _find_layout_for_species_in_frozenset(
                    writing_context,
                    base_reactants[0].referred_species,
                    frozenset_mapping,
                )
                if frozenset_mapping
                else None
            )
        product_layouts = []
        production_layouts = []
        for base_product in base_products:
            bp_species = base_product.referred_species
            bp_layout = (
                _find_layout_for_species_in_frozenset(
                    writing_context, bp_species, frozenset_mapping
                )
                if frozenset_mapping
                else None
            )
            if bp_layout is None:
                continue
            # Find the production arc for this product
            for layout_element_item in writing_context.map_.layout.layout_elements:
                if (
                    isinstance(layout_element_item, ProductionLayout)
                    and layout_element_item.source is reaction_layout
                    and layout_element_item.target is bp_layout
                ):
                    product_layouts.append(bp_layout)
                    production_layouts.append(layout_element_item)
                    break
        computed = False
        if reactant_layout is not None and len(product_layouts) >= 2:
            # Try both product orderings; pick the one whose
            # roundtrip T-junction position is closest to the actual one.
            t_junction = reaction_layout.points()[-1]
            best_result = None
            best_dist = float("inf")
            for perm in [
                (product_layouts, production_layouts),
                (product_layouts[::-1], production_layouts[::-1]),
            ]:
                pl, prl = perm
                result = writing.inverse_edit_points_right_t_shape(
                    reaction_layout,
                    reactant_layout,
                    pl,
                    prl,
                )
                # Roundtrip: transform T-junction back to absolute
                ep = result[0][-1]  # last edit point = T-junction in frame
                origin = reactant_layout.center()
                unit_x = pl[0].center()
                unit_y = pl[1].center()
                origin, unit_x, unit_y = writing._make_non_degenerate_frame(
                    origin, unit_x, unit_y
                )
                trans = get_transformation_for_frame(origin, unit_x, unit_y)
                roundtrip = ep.transformed(trans)
                dist = (roundtrip.x - t_junction.x) ** 2 + (
                    roundtrip.y - t_junction.y
                ) ** 2
                if math.isfinite(dist) and dist < best_dist:
                    best_dist = dist
                    best_result = result
            if best_result is None:
                best_result = writing.inverse_edit_points_right_t_shape(
                    reaction_layout,
                    reactant_layout,
                    product_layouts,
                    production_layouts,
                )
            (
                all_edit_points,
                num0,
                num1,
                num2,
                t_shape_index,
                reactant_anchor_name,
                product_anchor_names,
            ) = best_result
            connect_scheme = _make_celldesigner_element(
                "connectScheme", attrs={"connectPolicy": "direct"}
            )
            line_direction_list = _make_celldesigner_element("listOfLineDirection")
            for arm_idx, arm_count in enumerate([num0, num1, num2]):
                for i in range(arm_count + 1):
                    line_direction_list.append(
                        _make_celldesigner_element(
                            "lineDirection",
                            attrs={
                                "arm": str(arm_idx),
                                "index": str(i),
                                "value": "unknown",
                            },
                        )
                    )
            connect_scheme.append(line_direction_list)
            extension.append(connect_scheme)
            edit_points_attributes = {
                "num0": str(num0),
                "num1": str(num1),
                "num2": str(num2),
                "tShapeIndex": str(t_shape_index),
            }
            extension.append(
                _make_celldesigner_element(
                    "editPoints",
                    attrs=edit_points_attributes,
                    text=writing.points_to_edit_points_text(all_edit_points),
                )
            )
            computed = True
        if not computed:
            connect_scheme = _make_celldesigner_element(
                "connectScheme", attrs={"connectPolicy": "direct"}
            )
            line_direction_list = _make_celldesigner_element("listOfLineDirection")
            for arm in range(3):
                line_direction_list.append(
                    _make_celldesigner_element(
                        "lineDirection",
                        attrs={
                            "arm": str(arm),
                            "index": "0",
                            "value": "unknown",
                        },
                    )
                )
            connect_scheme.append(line_direction_list)
            extension.append(connect_scheme)
            extension.append(
                _make_celldesigner_element(
                    "editPoints",
                    attrs={
                        "num0": "0",
                        "num1": "0",
                        "num2": "0",
                        "tShapeIndex": "0",
                    },
                    text="0.5,0.5",
                )
            )
    else:
        # Non-T-shape (1→1)
        # lineDirection count = reactant_arc_segments + product_arc_segments + 1
        reactant_layout = None
        product_layout = None
        consumption_layout = None
        production_layout = None
        if base_reactants:
            reactant_layout = (
                _find_layout_for_species_in_frozenset(
                    writing_context,
                    base_reactants[0].referred_species,
                    frozenset_mapping,
                )
                if frozenset_mapping
                else None
            )
        if base_products:
            product_layout = (
                _find_layout_for_species_in_frozenset(
                    writing_context,
                    base_products[0].referred_species,
                    frozenset_mapping,
                )
                if frozenset_mapping
                else None
            )
        if reactant_layout is not None:
            for layout_element_item in writing_context.map_.layout.layout_elements:
                if (
                    isinstance(layout_element_item, ConsumptionLayout)
                    and layout_element_item.source is reaction_layout
                    and layout_element_item.target is reactant_layout
                ):
                    consumption_layout = layout_element_item
                    break
        if product_layout is not None:
            for layout_element_item in writing_context.map_.layout.layout_elements:
                if (
                    isinstance(layout_element_item, ProductionLayout)
                    and layout_element_item.source is reaction_layout
                    and layout_element_item.target is product_layout
                ):
                    production_layout = layout_element_item
                    break
        computed = False
        if reactant_layout is not None and product_layout is not None:
            reactant_anchor = reactant_layout.anchor_point("center")
            product_anchor = product_layout.anchor_point("center")
            if (
                abs(reactant_anchor.x - product_anchor.x) > 1e-6
                or abs(reactant_anchor.y - product_anchor.y) > 1e-6
            ):
                (
                    edit_points,
                    reactant_anchor_name,
                    product_anchor_name,
                    rectangle_index,
                ) = writing.inverse_edit_points_non_t_shape(
                    reaction_layout,
                    reactant_layout,
                    product_layout,
                )
                # lineDirection count: n_edit_points + 3
                n_line_dirs = len(edit_points) + 3
                connect_scheme = _make_celldesigner_element(
                    "connectScheme",
                    attrs={
                        "connectPolicy": "direct",
                        "rectangleIndex": str(rectangle_index),
                    },
                )
                line_direction_list = _make_celldesigner_element("listOfLineDirection")
                for i in range(n_line_dirs):
                    line_direction_list.append(
                        _make_celldesigner_element(
                            "lineDirection",
                            attrs={
                                "index": str(i),
                                "value": "unknown",
                            },
                        )
                    )
                connect_scheme.append(line_direction_list)
                extension.append(connect_scheme)
                if edit_points:
                    extension.append(
                        _make_celldesigner_element(
                            "editPoints",
                            text=writing.points_to_edit_points_text(edit_points),
                        )
                    )
                computed = True
        if not computed:
            connect_scheme = _make_celldesigner_element(
                "connectScheme",
                attrs={
                    "connectPolicy": "direct",
                    "rectangleIndex": "0",
                },
            )
            line_direction_list = _make_celldesigner_element("listOfLineDirection")
            line_direction_list.append(
                _make_celldesigner_element(
                    "lineDirection",
                    attrs={
                        "index": "0",
                        "value": "unknown",
                    },
                )
            )
            connect_scheme.append(line_direction_list)
            extension.append(connect_scheme)


def _make_celldesigner_participant_link(
    writing_context,
    participant,
    tag,
    attr_name,
    frozenset_mapping,
    reaction_layout=None,
    reaction=None,
):
    """Build a reactantLink or productLink element."""
    writing = _writing
    species = participant.referred_species
    is_start = tag == "reactantLink"
    if reaction is not None:
        alias_layout = _find_layout_for_participant(
            writing_context,
            participant,
            reaction,
            frozenset_mapping,
            reaction_layout,
            is_start,
        )
    else:
        alias_layout = (
            _find_layout_for_species_in_frozenset(
                writing_context, species, frozenset_mapping
            )
            if frozenset_mapping
            else None
        )
    alias_id = alias_layout.id_ if alias_layout else ""
    link = _make_celldesigner_element(
        tag,
        attrs={
            attr_name: _get_species_id(species, writing_context),
            "alias": alias_id,
        },
    )
    # Compute edit points from arc layout
    edit_points = []
    anchor_name = None
    arc_layout = None
    if reaction_layout is not None and alias_layout is not None:
        is_reactant = tag == "reactantLink"
        arc_cls = ConsumptionLayout if is_reactant else ProductionLayout
        for layout_element_item in writing_context.map_.layout.layout_elements:
            if (
                isinstance(layout_element_item, arc_cls)
                and layout_element_item.source is reaction_layout
                and layout_element_item.target is alias_layout
            ):
                arc_layout = layout_element_item
                if is_reactant:
                    edit_points, anchor_name = (
                        writing.inverse_edit_points_reactant_link(
                            layout_element_item,
                            alias_layout,
                            reaction_layout,
                        )
                    )
                else:
                    edit_points, anchor_name = writing.inverse_edit_points_product_link(
                        layout_element_item,
                        alias_layout,
                        reaction_layout,
                    )
                break
    if anchor_name is not None:
        anchor_pos = _anchor_name_to_position(anchor_name)
        if anchor_pos is not None:
            link.append(
                _make_celldesigner_element(
                    "linkAnchor",
                    attrs={
                        "position": anchor_pos,
                    },
                )
            )
    connect_scheme = _make_celldesigner_element(
        "connectScheme", attrs={"connectPolicy": "direct"}
    )
    line_direction_list = _make_celldesigner_element("listOfLineDirection")
    for i in range(len(edit_points) + 1):
        line_direction_list.append(
            _make_celldesigner_element(
                "lineDirection", attrs={"index": str(i), "value": "unknown"}
            )
        )
    connect_scheme.append(line_direction_list)
    link.append(connect_scheme)
    if edit_points:
        link.append(
            _make_celldesigner_element(
                "editPoints",
                text=writing.points_to_edit_points_text(edit_points),
            )
        )
    link.append(
        _make_celldesigner_element(
            "line", attrs=_get_line_attributes(arc_layout, include_type=True)
        )
    )
    return link


def _make_celldesigner_participant_link_from_layout(
    writing_context,
    arc_layout,
    tag,
    attr_name,
    reaction_layout,
):
    """Build a reactantLink or productLink from a known arc layout.

    Used when deriving link participants from layout arcs rather than
    from model participants (which may have been deduplicated).

    Args:
        writing_context: The writing context.
        arc_layout: The ConsumptionLayout or ProductionLayout arc.
        tag: XML tag name ("reactantLink" or "productLink").
        attr_name: Attribute name for the species ("reactant" or "product").
        reaction_layout: The ReactionLayout element.

    Returns:
        The lxml element for the link.
    """
    writing = _writing
    alias_layout = arc_layout.target
    alias_id = alias_layout.id_ if alias_layout else ""
    species = _mapping(writing_context).get_mapping(alias_layout)
    link = _make_celldesigner_element(
        tag,
        attrs={
            attr_name: _get_species_id(species, writing_context),
            "alias": alias_id,
        },
    )
    edit_points = []
    anchor_name = None
    is_reactant = tag == "reactantLink"
    if is_reactant:
        edit_points, anchor_name = writing.inverse_edit_points_reactant_link(
            arc_layout,
            alias_layout,
            reaction_layout,
        )
    else:
        edit_points, anchor_name = writing.inverse_edit_points_product_link(
            arc_layout,
            alias_layout,
            reaction_layout,
        )
    if anchor_name is not None:
        anchor_pos = _anchor_name_to_position(anchor_name)
        if anchor_pos is not None:
            link.append(
                _make_celldesigner_element(
                    "linkAnchor",
                    attrs={
                        "position": anchor_pos,
                    },
                )
            )
    connect_scheme = _make_celldesigner_element(
        "connectScheme", attrs={"connectPolicy": "direct"}
    )
    line_direction_list = _make_celldesigner_element("listOfLineDirection")
    for i in range(len(edit_points) + 1):
        line_direction_list.append(
            _make_celldesigner_element(
                "lineDirection", attrs={"index": str(i), "value": "unknown"}
            )
        )
    connect_scheme.append(line_direction_list)
    link.append(connect_scheme)
    if edit_points:
        link.append(
            _make_celldesigner_element(
                "editPoints",
                text=writing.points_to_edit_points_text(edit_points),
            )
        )
    link.append(
        _make_celldesigner_element(
            "line", attrs=_get_line_attributes(arc_layout, include_type=True)
        )
    )
    return link


def _make_celldesigner_modification(
    writing_context, modifier, reaction_layout, frozenset_mapping
):
    """Build a CD modification element for a reaction modifier."""
    writing = _writing
    species = modifier.referred_species
    if isinstance(species, BooleanLogicGate):
        return None
    alias_layout = (
        _find_layout_for_species_in_frozenset(
            writing_context, species, frozenset_mapping
        )
        if frozenset_mapping
        else None
    )
    alias_id = alias_layout.id_ if alias_layout else ""
    modifier_type = _CLASS_TO_MODIFIER_TYPE.get(type(modifier), "CATALYSIS")
    # Find modifier arc layout and compute edit points
    edit_points = []
    source_anchor_name = None
    modifier_arc = None
    if reaction_layout is not None and alias_layout is not None:
        for layout_element_item in writing_context.map_.layout.layout_elements:
            if (
                hasattr(layout_element_item, "source")
                and hasattr(layout_element_item, "target")
                and layout_element_item.source is alias_layout
                and layout_element_item.target is reaction_layout
            ):
                modifier_arc = layout_element_item
                edit_points, source_anchor_name = writing.inverse_edit_points_modifier(
                    layout_element_item,
                    alias_layout,
                    reaction_layout,
                    has_boolean_input=False,
                )
                break
    target_line_index = "-1,2"
    if modifier_arc is not None and reaction_layout is not None:
        target_line_index = _compute_target_line_index(reaction_layout, modifier_arc)
    attrs = {
        "type": modifier_type,
        "modifiers": _get_species_id(species, writing_context),
        "aliases": alias_id,
        "targetLineIndex": target_line_index,
    }
    if edit_points:
        attrs["editPoints"] = writing.points_to_edit_points_text(edit_points)
    modification_element = _make_celldesigner_element("modification", attrs=attrs)
    # connectScheme
    connect_scheme = _make_celldesigner_element(
        "connectScheme", attrs={"connectPolicy": "direct"}
    )
    line_direction_list = _make_celldesigner_element("listOfLineDirection")
    for i in range(len(edit_points) + 1):
        line_direction_list.append(
            _make_celldesigner_element(
                "lineDirection", attrs={"index": str(i), "value": "unknown"}
            )
        )
    connect_scheme.append(line_direction_list)
    modification_element.append(connect_scheme)
    # linkTarget
    link_target_attributes = {
        "species": _get_species_id(species, writing_context),
        "alias": alias_id,
    }
    link_target = _make_celldesigner_element("linkTarget", attrs=link_target_attributes)
    if source_anchor_name is not None:
        anchor_pos = _anchor_name_to_position(source_anchor_name)
        if anchor_pos is not None:
            link_target.append(
                _make_celldesigner_element("linkAnchor", attrs={"position": anchor_pos})
            )
    modification_element.append(link_target)
    # line
    modification_element.append(
        _make_celldesigner_element(
            "line", attrs=_get_line_attributes(modifier_arc, include_type=True)
        )
    )
    return modification_element


def _make_celldesigner_gate_modifications(
    writing_context, modifier, gate, reaction_layout, frozenset_mapping
):
    """Build CD modification entries for a boolean logic gate modifier.

    Returns a list of modification elements: first the gate entry,
    then one per input species.
    """
    result = []
    modifier_type = _CLASS_TO_MODIFIER_TYPE.get(type(modifier), "CATALYSIS")
    gate_type_map = {
        AndGate: "BOOLEAN_LOGIC_GATE_AND",
        OrGate: "BOOLEAN_LOGIC_GATE_OR",
        NotGate: "BOOLEAN_LOGIC_GATE_NOT",
        UnknownGate: "BOOLEAN_LOGIC_GATE_UNKNOWN",
    }
    gate_type = gate_type_map.get(type(gate), "BOOLEAN_LOGIC_GATE_AND")

    # Find the gate layout in the reaction's frozenset.
    gate_layout = None
    if frozenset_mapping is not None:
        for elem in frozenset_mapping:
            if isinstance(
                elem,
                (
                    AndGateLayout,
                    OrGateLayout,
                    NotGateLayout,
                    UnknownGateLayout,
                ),
            ):
                gate_layout = elem
                break

    # Build list of (model_element, alias_layout) from LogicArcLayouts
    # to resolve the correct alias for each gate input.
    logic_arc_inputs = []
    if gate_layout is not None:
        for layout_element_item in writing_context.map_.layout.layout_elements:
            if (
                isinstance(layout_element_item, LogicArcLayout)
                and layout_element_item.source is gate_layout
            ):
                input_alias_layout = layout_element_item.target
                input_model = _mapping(writing_context).get_mapping(input_alias_layout)
                if input_model is not None:
                    logic_arc_inputs.append((input_model, input_alias_layout))

    # Collect input aliases using LogicArcLayout when available,
    # falling back to frozenset/global lookup.
    input_species_ids = []
    input_alias_ids = []
    for inp in sorted(gate.inputs, key=lambda s: s.id_ or ""):
        input_species = inp.element
        sbml_inp = writing_context.subunit_to_complex.get(input_species, input_species)
        input_species_ids.append(_get_species_id(sbml_inp, writing_context))
        # Try LogicArcLayout first (correct alias for multi-alias species)
        alias_layout = None
        for arc_model, arc_layout in logic_arc_inputs:
            if arc_model is input_species:
                alias_layout = arc_layout
                logic_arc_inputs.remove((arc_model, arc_layout))
                break
        # Fallback: try frozenset, then global
        if alias_layout is None:
            alias_layout = (
                _find_layout_for_species_in_frozenset(
                    writing_context, input_species, frozenset_mapping
                )
                if frozenset_mapping
                else None
            )
        if alias_layout is None:
            for layout_key in _get_layouts(writing_context, input_species):
                if isinstance(layout_key, frozenset):
                    continue
                if isinstance(layout_key, CellDesignerNode):
                    alias_layout = layout_key
                    break
        input_alias_ids.append(alias_layout.id_ if alias_layout else "")
    gate_edit_points = ""
    if gate_layout is not None:
        pos = gate_layout.position
        gate_edit_points = f"{pos.x},{pos.y}"
    gate_attrs = {
        "type": gate_type,
        "modificationType": modifier_type,
        "modifiers": ",".join(input_species_ids),
        "aliases": ",".join(input_alias_ids),
        "targetLineIndex": "-1,2",
    }
    if gate_edit_points:
        gate_attrs["editPoints"] = gate_edit_points
    gate_mod = _make_celldesigner_element("modification", attrs=gate_attrs)
    gate_cs = _make_celldesigner_element(
        "connectScheme", attrs={"connectPolicy": "direct"}
    )
    gate_lld = _make_celldesigner_element("listOfLineDirection")
    gate_lld.append(
        _make_celldesigner_element(
            "lineDirection", attrs={"index": "0", "value": "unknown"}
        )
    )
    gate_cs.append(gate_lld)
    gate_mod.append(gate_cs)
    # Find the gate-to-reaction arc for line attributes
    gate_to_reaction_arc = None
    if gate_layout is not None and reaction_layout is not None:
        for layout_element_item in writing_context.map_.layout.layout_elements:
            if (
                hasattr(layout_element_item, "source")
                and hasattr(layout_element_item, "target")
                and layout_element_item.source is gate_layout
                and layout_element_item.target is reaction_layout
            ):
                gate_to_reaction_arc = layout_element_item
                break
    gate_mod.append(
        _make_celldesigner_element(
            "line", attrs=_get_line_attributes(gate_to_reaction_arc, include_type=True)
        )
    )
    result.append(gate_mod)

    # Per-input entries
    for i, inp in enumerate(sorted(gate.inputs, key=lambda s: s.id_ or "")):
        input_species = inp.element
        sbml_inp = writing_context.subunit_to_complex.get(input_species, input_species)
        inp_attrs = {
            "type": modifier_type,
            "modifiers": _get_species_id(sbml_inp, writing_context),
            "aliases": input_alias_ids[i],
            "targetLineIndex": "-1,2",
        }
        inp_mod = _make_celldesigner_element("modification", attrs=inp_attrs)
        connect_scheme = _make_celldesigner_element(
            "connectScheme", attrs={"connectPolicy": "direct"}
        )
        line_direction_list = _make_celldesigner_element("listOfLineDirection")
        line_direction_list.append(
            _make_celldesigner_element(
                "lineDirection", attrs={"index": "0", "value": "unknown"}
            )
        )
        connect_scheme.append(line_direction_list)
        inp_mod.append(connect_scheme)
        # linkTarget — find the input-to-gate arc for line attributes
        input_to_gate_arc = None
        if input_alias_ids[i]:
            for layout_element_item in writing_context.map_.layout.layout_elements:
                if (
                    hasattr(layout_element_item, "source")
                    and hasattr(layout_element_item, "target")
                    and layout_element_item.target is gate_layout
                    and getattr(layout_element_item.source, "id_", None)
                    == input_alias_ids[i]
                ):
                    input_to_gate_arc = layout_element_item
                    break
        link_target = _make_celldesigner_element(
            "linkTarget",
            attrs={
                "species": _get_species_id(sbml_inp, writing_context),
                "alias": input_alias_ids[i],
            },
        )
        inp_mod.append(link_target)
        inp_mod.append(
            _make_celldesigner_element(
                "line", attrs=_get_line_attributes(input_to_gate_arc, include_type=True)
            )
        )
        result.append(inp_mod)

    return result


def _make_celldesigner_modulation_reaction(
    writing_context, modulation, frozenset_mapping
):
    """Build a modulation as a fake SBML reaction."""
    source = modulation.source
    target = modulation.target

    if isinstance(source, BooleanLogicGate):
        return _make_celldesigner_gate_modulation_reaction(writing_context, modulation)

    # Resolve layouts from the given frozenset
    modulation_layout = None
    source_layout = None
    target_layout = None
    if frozenset_mapping is not None:
        for elem in frozenset_mapping:
            model = _mapping(writing_context).get_mapping(elem)
            if model is modulation:
                modulation_layout = elem
            elif model is source:
                source_layout = elem
            elif model is target:
                target_layout = elem
    else:
        for layout_key in _get_layouts(writing_context, modulation):
            if not isinstance(layout_key, frozenset):
                modulation_layout = layout_key

    # Derive XML id from layout when available
    if modulation_layout is not None:
        xml_id = modulation_layout.id_.removesuffix("_layout")
    else:
        xml_id = modulation.id_
    attrs = {
        "metaid": xml_id,
        "id": xml_id,
        "reversible": "false",
    }
    reaction_element = _make_lxml_element("reaction", attrs=attrs)

    # notes
    notes_element = _build_sbml_notes(writing_context, modulation)
    if notes_element is not None:
        reaction_element.append(notes_element)

    if source_layout is None and source is not None:
        for layout_key in _get_layouts(writing_context, source):
            if isinstance(layout_key, frozenset):
                continue
            if isinstance(layout_key, CellDesignerNode):
                source_layout = layout_key
                break

    if target_layout is None and target is not None:
        for layout_key in _get_layouts(writing_context, target):
            if isinstance(layout_key, frozenset):
                continue
            if isinstance(layout_key, CellDesignerNode):
                target_layout = layout_key
                break

    source_alias = source_layout.id_ if source_layout else ""
    target_alias = target_layout.id_ if target_layout else ""
    source_id = _get_species_id(source, writing_context) if source else ""
    target_id = _get_species_id(target, writing_context) if target else ""

    # CD extension
    annotation = _make_lxml_element("annotation")
    extension = _make_celldesigner_element("extension")
    reaction_type = _modulation_reaction_type(modulation)
    extension.append(_make_celldesigner_element("reactionType", text=reaction_type))

    # Compute edit points for the modulation
    writing = _writing
    edit_points = []
    source_anchor_name = None
    target_anchor_name = None
    if (
        modulation_layout is not None
        and source_layout is not None
        and target_layout is not None
    ):
        edit_points, source_anchor_name, target_anchor_name = (
            writing.inverse_edit_points_modulation(
                modulation_layout,
                source_layout,
                target_layout,
                has_boolean_input=False,
            )
        )

    # baseReactants (source)
    base_reactants_element = _make_celldesigner_element("baseReactants")
    base_reactant = _make_celldesigner_element(
        "baseReactant", attrs={"species": source_id, "alias": source_alias}
    )
    if source_anchor_name is not None:
        anchor_pos = _anchor_name_to_position(source_anchor_name)
        if anchor_pos is not None:
            base_reactant.append(
                _make_celldesigner_element("linkAnchor", attrs={"position": anchor_pos})
            )
    base_reactants_element.append(base_reactant)
    extension.append(base_reactants_element)

    # baseProducts (target)
    base_products_element = _make_celldesigner_element("baseProducts")
    base_product = _make_celldesigner_element(
        "baseProduct", attrs={"species": target_id, "alias": target_alias}
    )
    if target_anchor_name is not None:
        anchor_pos = _anchor_name_to_position(target_anchor_name)
        if anchor_pos is not None:
            base_product.append(
                _make_celldesigner_element("linkAnchor", attrs={"position": anchor_pos})
            )
    base_products_element.append(base_product)
    extension.append(base_products_element)

    extension.append(_make_celldesigner_element("listOfReactantLinks"))
    extension.append(_make_celldesigner_element("listOfProductLinks"))

    # connectScheme — for modulations-as-reactions:
    # ld = n_edit_points + 3, rectangleIndex = n_edit_points
    num_edit_points = len(edit_points)
    connect_scheme = _make_celldesigner_element(
        "connectScheme",
        attrs={
            "connectPolicy": "direct",
            "rectangleIndex": str(num_edit_points),
        },
    )
    line_direction_list = _make_celldesigner_element("listOfLineDirection")
    for i in range(num_edit_points + 3):
        line_direction_list.append(
            _make_celldesigner_element(
                "lineDirection",
                attrs={
                    "index": str(i),
                    "value": "unknown",
                },
            )
        )
    connect_scheme.append(line_direction_list)
    extension.append(connect_scheme)

    if edit_points:
        extension.append(
            _make_celldesigner_element(
                "editPoints",
                text=writing.points_to_edit_points_text(edit_points),
            )
        )

    extension.append(_make_celldesigner_element("listOfModification"))
    extension.append(
        _make_celldesigner_element(
            "line", attrs=_get_line_attributes(modulation_layout, include_type=True)
        )
    )

    annotation.append(extension)
    _append_rdf_to_annotation(writing_context, annotation, modulation, xml_id)
    reaction_element.append(annotation)

    # SBML listOfReactants (use complex ID for subunits)
    sbml_source = (
        writing_context.subunit_to_complex.get(source, source) if source else source
    )
    list_of_reactants = _make_lxml_element("listOfReactants")
    species_reference = _make_lxml_element(
        "speciesReference",
        attrs={
            "species": _get_species_id(sbml_source, writing_context)
            if sbml_source
            else ""
        },
    )
    species_reference_annotation = _make_lxml_element("annotation")
    species_reference_extension = _make_celldesigner_element("extension")
    species_reference_extension.append(
        _make_celldesigner_element("alias", text=source_alias)
    )
    species_reference_annotation.append(species_reference_extension)
    species_reference.append(species_reference_annotation)
    list_of_reactants.append(species_reference)
    reaction_element.append(list_of_reactants)

    # SBML listOfProducts (use complex ID for subunits)
    sbml_target = (
        writing_context.subunit_to_complex.get(target, target) if target else target
    )
    list_of_products = _make_lxml_element("listOfProducts")
    pr = _make_lxml_element(
        "speciesReference",
        attrs={
            "species": _get_species_id(sbml_target, writing_context)
            if sbml_target
            else ""
        },
    )
    product_reference_annotation = _make_lxml_element("annotation")
    product_reference_extension = _make_celldesigner_element("extension")
    product_reference_extension.append(
        _make_celldesigner_element("alias", text=target_alias)
    )
    product_reference_annotation.append(product_reference_extension)
    pr.append(product_reference_annotation)
    list_of_products.append(pr)
    reaction_element.append(list_of_products)

    return reaction_element


def _make_celldesigner_gate_modulation_reaction(writing_context, modulation):
    """Build a boolean gate modulation as a fake SBML reaction.

    Structure: reactionType=BOOLEAN_LOGIC_GATE, baseReactants=gate inputs,
    baseProducts=target, listOfGateMember for gate+per-input entries.
    """
    gate = modulation.source
    target = modulation.target

    gate_type_map = {
        AndGate: "BOOLEAN_LOGIC_GATE_AND",
        OrGate: "BOOLEAN_LOGIC_GATE_OR",
        NotGate: "BOOLEAN_LOGIC_GATE_NOT",
        UnknownGate: "BOOLEAN_LOGIC_GATE_UNKNOWN",
    }
    gate_type = gate_type_map.get(type(gate), "BOOLEAN_LOGIC_GATE_AND")

    # Determine the modification type from the modulation type
    modifier_type = _modulation_reaction_type(modulation)

    attrs = {
        "metaid": modulation.id_,
        "id": modulation.id_,
        "reversible": "false",
    }
    reaction_element = _make_lxml_element("reaction", attrs=attrs)

    # notes
    notes_element = _build_sbml_notes(writing_context, modulation)
    if notes_element is not None:
        reaction_element.append(notes_element)

    # Find the gate layout
    gate_layout = None
    for layout_element_item in writing_context.map_.layout.layout_elements:
        if isinstance(
            layout_element_item,
            (
                AndGateLayout,
                OrGateLayout,
                NotGateLayout,
                UnknownGateLayout,
            ),
        ):
            gate_model = _mapping(writing_context).get_mapping(layout_element_item)
            if gate_model is gate:
                gate_layout = layout_element_item
                break

    # Find inputs via logic arcs (preserves duplicates unlike gate.inputs)
    input_layouts = []
    if gate_layout is not None:
        for layout_element_item in writing_context.map_.layout.layout_elements:
            if (
                isinstance(layout_element_item, LogicArcLayout)
                and layout_element_item.source is gate_layout
            ):
                inp_layout = layout_element_item.target
                model_info = _mapping(writing_context).get_mapping(inp_layout)
                inp_model = (
                    (model_info[0] if isinstance(model_info, tuple) else model_info)
                    if model_info is not None
                    else None
                )
                if inp_model is not None:
                    input_layouts.append((inp_model, inp_layout))
    if not input_layouts:
        # Fallback to gate.inputs if no logic arcs found
        for inp in sorted(gate.inputs, key=lambda s: s.id_ or ""):
            inp_layout = None
            for layout_key in _get_layouts(writing_context, inp.element):
                if isinstance(layout_key, frozenset):
                    continue
                if isinstance(layout_key, CellDesignerNode):
                    inp_layout = layout_key
                    break
            input_layouts.append((inp.element, inp_layout))

    target_layout = None
    if target is not None:
        for layout_key in _get_layouts(writing_context, target):
            if isinstance(layout_key, frozenset):
                continue
            if isinstance(layout_key, CellDesignerNode):
                target_layout = layout_key
                break

    gate_edit_points = ""
    if gate_layout is not None:
        gate_edit_points = f"{gate_layout.position.x},{gate_layout.position.y}"

    target_alias = target_layout.id_ if target_layout else ""
    target_id = _get_species_id(target, writing_context) if target else ""

    # CD extension
    annotation = _make_lxml_element("annotation")
    extension = _make_celldesigner_element("extension")
    extension.append(
        _make_celldesigner_element("reactionType", text="BOOLEAN_LOGIC_GATE")
    )

    # baseReactants (gate inputs)
    base_reactants_element = _make_celldesigner_element("baseReactants")
    for inp, inp_layout in input_layouts:
        sbml_inp = writing_context.subunit_to_complex.get(inp, inp)
        alias_id = inp_layout.id_ if inp_layout else ""
        base_reactant = _make_celldesigner_element(
            "baseReactant",
            attrs={
                "species": _get_species_id(sbml_inp, writing_context),
                "alias": alias_id,
            },
        )
        # Try to find linkAnchor from logic arcs
        if gate_layout is not None and inp_layout is not None:
            for layout_element_item in writing_context.map_.layout.layout_elements:
                if (
                    hasattr(layout_element_item, "source")
                    and hasattr(layout_element_item, "target")
                    and layout_element_item.source is gate_layout
                    and layout_element_item.target is inp_layout
                ):
                    endpoint = layout_element_item.points()[-1]
                    anchor = _infer_anchor_position(inp_layout, endpoint)
                    if anchor is not None:
                        base_reactant.append(
                            _make_celldesigner_element(
                                "linkAnchor", attrs={"position": anchor}
                            )
                        )
                    break
        base_reactants_element.append(base_reactant)
    extension.append(base_reactants_element)

    # baseProducts (target)
    base_products_element = _make_celldesigner_element("baseProducts")
    sbml_target = (
        writing_context.subunit_to_complex.get(target, target) if target else target
    )
    base_product = _make_celldesigner_element(
        "baseProduct",
        attrs={
            "species": _get_species_id(sbml_target, writing_context)
            if sbml_target
            else "",
            "alias": target_alias,
        },
    )
    base_products_element.append(base_product)
    extension.append(base_products_element)

    extension.append(_make_celldesigner_element("listOfReactantLinks"))
    extension.append(_make_celldesigner_element("listOfProductLinks"))

    # Compute editPoints: intermediate points from modulation layout + gate position
    writing = _writing
    modulation_layout = None
    for layout_key in _get_layouts(writing_context, modulation):
        if isinstance(layout_key, frozenset):
            for elem in layout_key:
                model = _mapping(writing_context).get_mapping(elem)
                if model is modulation:
                    modulation_layout = elem
                    break
        elif not isinstance(layout_key, frozenset):
            modulation_layout = layout_key

    edit_points_parts = []
    if (
        gate_layout is not None
        and modulation_layout is not None
        and target_layout is not None
    ):
        mod_edit_points, _, _ = writing.inverse_edit_points_modulation(
            modulation_layout,
            gate_layout,
            target_layout,
            has_boolean_input=True,
        )
        edit_points_parts.extend(f"{p.x},{p.y}" for p in mod_edit_points)
    if gate_edit_points:
        edit_points_parts.append(gate_edit_points)
    edit_points_text = " ".join(edit_points_parts)
    num_edit_points = len(edit_points_parts)

    # connectScheme — gate modulations use rectangleIndex=1
    # and lineDirection count = len(inputs) + 3
    num_line_directions = len(input_layouts) + 3
    connect_scheme = _make_celldesigner_element(
        "connectScheme",
        attrs={
            "connectPolicy": "direct",
            "rectangleIndex": "1",
        },
    )
    line_direction_list = _make_celldesigner_element("listOfLineDirection")
    for i in range(num_line_directions):
        line_direction_list.append(
            _make_celldesigner_element(
                "lineDirection",
                attrs={
                    "index": str(i),
                    "value": "unknown",
                },
            )
        )
    connect_scheme.append(line_direction_list)
    extension.append(connect_scheme)

    # editPoints — always write, even if empty, to avoid reader crash
    extension.append(
        _make_celldesigner_element("editPoints", text=edit_points_text or "0.0,0.0")
    )

    extension.append(_make_celldesigner_element("listOfModification"))

    # listOfGateMember
    gate_member_list = _make_celldesigner_element("listOfGateMember")
    input_alias_ids = [il.id_ if il else "" for _, il in input_layouts]
    # Gate entry
    gate_attrs = {
        "type": gate_type,
        "aliases": ",".join(input_alias_ids),
        "modificationType": modifier_type,
    }
    gate_attrs["editPoints"] = gate_edit_points or "0.0,0.0"
    gate_member = _make_celldesigner_element("GateMember", attrs=gate_attrs)
    gate_member_connect_scheme = _make_celldesigner_element(
        "connectScheme", attrs={"connectPolicy": "direct"}
    )
    gate_member_line_direction_list = _make_celldesigner_element("listOfLineDirection")
    gate_member_line_direction_list.append(
        _make_celldesigner_element(
            "lineDirection",
            attrs={
                "index": "0",
                "value": "unknown",
            },
        )
    )
    gate_member_connect_scheme.append(gate_member_line_direction_list)
    gate_member.append(gate_member_connect_scheme)
    gate_member.append(
        _make_celldesigner_element(
            "line", attrs=_get_line_attributes(modulation_layout, include_type=True)
        )
    )
    gate_member_list.append(gate_member)

    # Per-input entries
    for inp, inp_layout in input_layouts:
        sbml_inp = writing_context.subunit_to_complex.get(inp, inp)
        alias_id = inp_layout.id_ if inp_layout else ""
        inp_member = _make_celldesigner_element(
            "GateMember",
            attrs={
                "type": modifier_type,
                "aliases": alias_id,
            },
        )
        inp_cs = _make_celldesigner_element(
            "connectScheme", attrs={"connectPolicy": "direct"}
        )
        inp_lld = _make_celldesigner_element("listOfLineDirection")
        inp_lld.append(
            _make_celldesigner_element(
                "lineDirection",
                attrs={
                    "index": "0",
                    "value": "unknown",
                },
            )
        )
        inp_cs.append(inp_lld)
        inp_member.append(inp_cs)
        link_target = _make_celldesigner_element(
            "linkTarget",
            attrs={
                "species": _get_species_id(sbml_inp, writing_context),
                "alias": alias_id,
            },
        )
        input_arc_layout = None
        if gate_layout is not None and inp_layout is not None:
            for layout_element_item in writing_context.map_.layout.layout_elements:
                if (
                    hasattr(layout_element_item, "source")
                    and hasattr(layout_element_item, "target")
                    and layout_element_item.source is gate_layout
                    and layout_element_item.target is inp_layout
                ):
                    input_arc_layout = layout_element_item
                    endpoint = layout_element_item.points()[-1]
                    anchor = _infer_anchor_position(inp_layout, endpoint)
                    if anchor is not None:
                        link_target.append(
                            _make_celldesigner_element(
                                "linkAnchor", attrs={"position": anchor}
                            )
                        )
                    break
        inp_member.append(link_target)
        inp_member.append(
            _make_celldesigner_element(
                "line", attrs=_get_line_attributes(input_arc_layout, include_type=True)
            )
        )
        gate_member_list.append(inp_member)

    extension.append(gate_member_list)
    extension.append(
        _make_celldesigner_element(
            "line", attrs=_get_line_attributes(modulation_layout, include_type=True)
        )
    )

    annotation.append(extension)
    _append_rdf_to_annotation(writing_context, annotation, modulation, modulation.id_)
    reaction_element.append(annotation)

    # SBML listOfReactants (gate inputs)
    list_of_reactants = _make_lxml_element("listOfReactants")
    for inp, inp_layout in input_layouts:
        sbml_inp = writing_context.subunit_to_complex.get(inp, inp)
        alias_id = inp_layout.id_ if inp_layout else ""
        species_reference = _make_lxml_element(
            "speciesReference",
            attrs={
                "species": _get_species_id(sbml_inp, writing_context),
            },
        )
        species_reference_annotation = _make_lxml_element("annotation")
        species_reference_extension = _make_celldesigner_element("extension")
        species_reference_extension.append(
            _make_celldesigner_element("alias", text=alias_id)
        )
        species_reference_annotation.append(species_reference_extension)
        species_reference.append(species_reference_annotation)
        list_of_reactants.append(species_reference)
    reaction_element.append(list_of_reactants)

    # SBML listOfProducts (target)
    list_of_products = _make_lxml_element("listOfProducts")
    pr = _make_lxml_element(
        "speciesReference",
        attrs={
            "species": _get_species_id(sbml_target, writing_context)
            if sbml_target
            else "",
        },
    )
    product_reference_annotation = _make_lxml_element("annotation")
    product_reference_extension = _make_celldesigner_element("extension")
    product_reference_extension.append(
        _make_celldesigner_element("alias", text=target_alias)
    )
    product_reference_annotation.append(product_reference_extension)
    pr.append(product_reference_annotation)
    list_of_products.append(pr)
    reaction_element.append(list_of_products)

    return reaction_element


# ---------------------------------------------------------------------------
# Writer class
# ---------------------------------------------------------------------------


def _synthesize_degraded_for_flagged_reactions(obj):
    """Synthesise Degraded model species for reactions with external flags.

    Returns a (potentially) new map where every Reaction with
    ``has_external_source`` or ``has_external_sink`` set has explicit
    ``Degraded`` species + ``Reactant`` / ``Product`` model elements
    derived from the corresponding ``DegradedLayout`` instances. This
    lets the rest of the writer treat them as ordinary participants
    without needing layout-only emission paths.

    The original map is not mutated; a builder copy is built and
    returned. Maps without flagged reactions are returned unchanged.
    """
    if obj.model is None or obj.layout is None:
        return obj
    needs_synthesis = any(
        getattr(reaction, "has_external_source", False)
        or getattr(reaction, "has_external_sink", False)
        for reaction in obj.model.reactions
    )
    if not needs_synthesis:
        return obj

    map_builder = momapy.builder.builder_from_object(obj)
    mapping_builder = map_builder.layout_model_mapping
    model_builder = map_builder.model

    original_reactions = list(obj.model.reactions)
    builder_reactions = list(model_builder.reactions)
    # Reactions iterate by id_ to align frozen and builder views.
    id_to_builder_reaction = {r.id_: r for r in builder_reactions}

    for reaction in original_reactions:
        if not (
            getattr(reaction, "has_external_source", False)
            or getattr(reaction, "has_external_sink", False)
        ):
            continue
        builder_reaction = id_to_builder_reaction.get(reaction.id_)
        if builder_reaction is None:
            continue
        # Find DegradedLayouts attached to this reaction via the frozenset
        # key in the mapping. Use the original (frozen) reaction as the
        # mapping key — builder mapping inherits the same keys.
        degraded_layouts = []
        mapping_result = obj.layout_model_mapping.get_mapping(reaction)
        if mapping_result is None:
            continue
        for entry in mapping_result:
            if isinstance(entry, frozenset):
                for member in entry:
                    if isinstance(member, (DegradedLayout, DegradedActiveLayout)):
                        degraded_layouts.append(member)
        if not degraded_layouts:
            continue
        # Need the reaction layout to determine reactant-vs-product side
        # for each degraded layout via the connecting arc.
        reaction_layout = None
        for entry in mapping_result:
            if isinstance(entry, ReactionLayout):
                reaction_layout = entry
                break
        if reaction_layout is None:
            for entry in mapping_result:
                if isinstance(entry, frozenset):
                    for member in entry:
                        if isinstance(member, ReactionLayout):
                            reaction_layout = member
                            break
                    if reaction_layout is not None:
                        break
        if reaction_layout is None:
            continue
        for degraded_layout in degraded_layouts:
            side = _classify_degraded_arc_side(
                obj.layout, reaction_layout, degraded_layout
            )
            if side is None:
                continue
            degraded_id = f"degraded_{degraded_layout.id_}"
            degraded_species = momapy.builder.new_builder_object(Degraded)
            degraded_species.id_ = degraded_id
            degraded_species.name = ""
            degraded_species.metaid = degraded_id
            built_degraded = momapy.builder.object_from_builder(degraded_species)
            model_builder.species.add(built_degraded)
            participant_cls = Reactant if side == "reactant" else Product
            participant = momapy.builder.new_builder_object(participant_cls)
            participant.id_ = f"{reaction.id_}_{degraded_id}"
            participant.referred_species = built_degraded
            participant.base = True
            built_participant = momapy.builder.object_from_builder(participant)
            if side == "reactant":
                builder_reaction.reactants.add(built_participant)
            else:
                builder_reaction.products.add(built_participant)
            mapping_builder.add_mapping(degraded_layout, built_degraded, replace=True)

    return map_builder.build()


def _classify_degraded_arc_side(layout, reaction_layout, degraded_layout):
    """Return "reactant" or "product" by inspecting the connecting arc.

    Two cases are handled:
    - 1-to-1 reactions where the reaction layout itself acts as the arc:
      its ``source`` is the base reactant and ``target`` is the base
      product.
    - T-shape reactions or link participants where a separate
      ``ConsumptionLayout`` / ``ProductionLayout`` connects the reaction
      layout to the participant.

    Returns None if no connecting arc is found.
    """
    if getattr(reaction_layout, "source", None) is degraded_layout:
        return "reactant"
    if getattr(reaction_layout, "target", None) is degraded_layout:
        return "product"
    for layout_element in layout.layout_elements:
        if isinstance(layout_element, ConsumptionLayout):
            if (
                layout_element.source is reaction_layout
                and layout_element.target is degraded_layout
            ):
                return "reactant"
        elif isinstance(layout_element, ProductionLayout):
            if (
                layout_element.source is reaction_layout
                and layout_element.target is degraded_layout
            ):
                return "product"
    return None


class CellDesignerWriter(Writer):
    """CellDesigner XML writer (model-first approach)."""

    @classmethod
    def write(
        cls,
        obj: CellDesignerMap,
        file_path: str | os.PathLike,
        element_to_annotations: dict | None = None,
        element_to_notes: dict | None = None,
        source_id_to_model_element: dict | None = None,
        source_id_to_layout_element: dict | None = None,
        with_annotations: bool = True,
        with_notes: bool = True,
        **options: typing.Any,
    ) -> WriterResult:
        """Write a CellDesigner map to a file.

        Args:
            obj: A CellDesignerMap instance.
            file_path: Output file path.
            element_to_annotations: Annotations dict from reader result.
            element_to_notes: Notes dict from reader result.
            source_id_to_model_element: Optional source ID to model
                element mapping from ReaderResult.
            source_id_to_layout_element: Optional source ID to layout
                element mapping from ReaderResult.
            with_annotations: Whether to write annotations.
            with_notes: Whether to write notes.

        Returns:
            WriterResult.
        """
        check_parent_dir_exists(file_path)
        if element_to_annotations is None:
            element_to_annotations = {}
        if element_to_notes is None:
            element_to_notes = {}
        # Synthesise Degraded model species for reactions flagged with
        # has_external_source / has_external_sink so the rest of the
        # writer can treat them as ordinary participants.
        obj = _synthesize_degraded_for_flagged_reactions(obj)

        subunit_to_complex = {}
        species_to_id = {}
        if obj.model is not None:

            def _collect(species):
                species_id = _strip_active(species)
                if id(species) not in species_to_id:
                    species_to_id[id(species)] = species_id
                if isinstance(species, Complex):
                    for sub in species.subunits:
                        # Map to top-level ancestor, not immediate parent.
                        # If the parent is itself a subunit, its entry
                        # was already set (parent before children).
                        ancestor = species
                        while ancestor in subunit_to_complex:
                            ancestor = subunit_to_complex[ancestor]
                        subunit_to_complex[sub] = ancestor
                        _collect(sub)

            for species in obj.model.species:
                _collect(species)

        writing_context = CellDesignerWritingContext(
            map_=obj,
            element_to_annotations=element_to_annotations,
            element_to_notes=element_to_notes,
            source_id_to_model_element=source_id_to_model_element,
            source_id_to_layout_element=source_id_to_layout_element,
            with_annotations=with_annotations,
            with_notes=with_notes,
            subunit_to_complex=subunit_to_complex,
            species_to_id=species_to_id,
        )

        sbml = _build_make_sbml_element(writing_context)
        tree = lxml.etree.ElementTree(sbml)
        tree.write(
            file_path,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )
        return WriterResult(obj=obj, file_path=file_path)
