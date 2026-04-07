"""CellDesigner XML writer (new, model-first approach)."""

import dataclasses
import typing

import lxml.etree

import momapy.coloring
import momapy.drawing
import momapy.geometry
import momapy.io.core
import momapy.celldesigner.core
import momapy.celldesigner.io.celldesigner._reading_parsing
import momapy.celldesigner.io.celldesigner._writing
import momapy.sbml.core

_CD_NS = "http://www.sbml.org/2001/ns/celldesigner"
_SBML_NS = "http://www.sbml.org/sbml/level2/version4"
_XHTML_NS = "http://www.w3.org/1999/xhtml"

_NSMAP = {
    None: _SBML_NS,
    "celldesigner": _CD_NS,
}

_writing = momapy.celldesigner.io.celldesigner._writing

_CLASS_TO_CD_STRING = _writing._CLASS_TO_CD_STRING
_CLASS_TO_REACTION_TYPE = _writing._CLASS_TO_REACTION_TYPE
_CLASS_TO_MODIFIER_TYPE = _writing._CLASS_TO_MODIFIER_TYPE


def _modulation_reaction_type(modulation):
    """Determine the CellDesigner reaction type for a modulation.

    Rules:
    - Inhibition targeting a non-Phenotype species → NEGATIVE_INFLUENCE
    - Modulation/Triggering/PhysicalStimulation targeting a non-Phenotype
      species → REDUCED_ variant
    - Otherwise → standard type
    """
    target = modulation.target
    is_reduced = (
        target is not None
        and not isinstance(target, momapy.celldesigner.core.Phenotype)
    )
    _MAP = {
        momapy.celldesigner.core.Catalysis: ("CATALYSIS", None),
        momapy.celldesigner.core.UnknownCatalysis: ("UNKNOWN_CATALYSIS", None),
        momapy.celldesigner.core.Inhibition: ("INHIBITION", "NEGATIVE_INFLUENCE"),
        momapy.celldesigner.core.UnknownInhibition: ("UNKNOWN_INHIBITION", "UNKNOWN_NEGATIVE_INFLUENCE"),
        momapy.celldesigner.core.PhysicalStimulation: ("PHYSICAL_STIMULATION", "REDUCED_PHYSICAL_STIMULATION"),
        momapy.celldesigner.core.UnknownPhysicalStimulation: ("UNKNOWN_PHYSICAL_STIMULATION", "UNKNOWN_REDUCED_PHYSICAL_STIMULATION"),
        momapy.celldesigner.core.Modulation: ("MODULATION", "REDUCED_MODULATION"),
        momapy.celldesigner.core.UnknownModulation: ("UNKNOWN_MODULATION", "UNKNOWN_REDUCED_MODULATION"),
        momapy.celldesigner.core.Triggering: ("TRIGGER", "REDUCED_TRIGGER"),
        momapy.celldesigner.core.UnknownTriggering: ("UNKNOWN_TRIGGER", "UNKNOWN_REDUCED_TRIGGER"),
        momapy.celldesigner.core.PositiveInfluence: ("POSITIVE_INFLUENCE", None),
        momapy.celldesigner.core.NegativeInfluence: ("NEGATIVE_INFLUENCE", None),
        momapy.celldesigner.core.UnknownPositiveInfluence: ("UNKNOWN_POSITIVE_INFLUENCE", None),
        momapy.celldesigner.core.UnknownNegativeInfluence: ("UNKNOWN_NEGATIVE_INFLUENCE", None),
    }
    entry = _MAP.get(type(modulation))
    if entry is None:
        return "MODULATION"
    normal, reduced = entry
    if is_reduced and reduced is not None:
        return reduced
    return normal

_MODIFICATION_STATE_TO_CD = _writing._MODIFICATION_STATE_TO_CD


@dataclasses.dataclass
class WritingContext:
    """Shared state for the writer."""

    map_: typing.Any
    annotations: dict
    notes: dict
    ids: dict
    with_annotations: bool
    with_notes: bool
    subunit_to_complex: dict = dataclasses.field(default_factory=dict)
    used_metaids: set = dataclasses.field(default_factory=set)
    species_to_id: dict = dataclasses.field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _el(tag, ns=None, attrs=None, text=None, nsmap=None):
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


def _cd(tag, attrs=None, text=None):
    """Shortcut for CellDesigner-namespaced element."""
    return _el(tag, ns=_CD_NS, attrs=attrs, text=text)


def _sbml(tag, attrs=None, text=None, nsmap=None):
    """Shortcut for SBML-namespaced element."""
    return _el(tag, ns=_SBML_NS, attrs=attrs, text=text, nsmap=nsmap)


_encode_name = _writing.encode_name


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


def _get_species_id(species, ctx=None):
    """Get the canonical species ID for a model species.

    When ctx is provided, uses the species_to_id mapping built from the
    model tree so that all references to the same model object use a
    consistent ID. Falls back to stripping _active suffixes.
    """
    if species is None:
        return ""
    if ctx is not None:
        canonical = ctx.species_to_id.get(id(species))
        if canonical is not None:
            return canonical
    return _strip_active(species)


_color_hex = _writing.color_to_cd_hex


def _unique_metaid(ctx, candidate):
    """Return a unique metaid string."""
    result = candidate
    counter = 1
    while result in ctx.used_metaids:
        result = f"{candidate}_{counter}"
        counter += 1
    ctx.used_metaids.add(result)
    return result


def _mapping(ctx):
    """Shortcut to access layout_model_mapping."""
    return ctx.map_.layout_model_mapping


def _get_layouts(ctx, model_element):
    """Get layout elements for a model element.

    Returns a list. Items can be single layout elements or frozensets.
    Also handles subunits, whose mapping is keyed by (subunit, complex).
    """
    result = _mapping(ctx).get_mapping(model_element)
    if result is None and model_element in ctx.subunit_to_complex:
        result = _mapping(ctx).get_mapping(
            (model_element, ctx.subunit_to_complex[model_element])
        )
    if result is None:
        return []
    if isinstance(result, list):
        return result
    return [result]


def _find_layout_for_species_in_frozenset(ctx, species, fset):
    """Find the layout element for a species within a reaction frozenset."""
    for elem in fset:
        model = _mapping(ctx).get_mapping(elem)
        if model is species:
            return elem
        if isinstance(model, tuple) and model[0] is species:
            return elem
    return None


def _get_reaction_layout(fset):
    """Extract the ReactionLayout from a frozenset."""
    for elem in fset:
        if isinstance(elem, momapy.celldesigner.core.ReactionLayout):
            return elem
    return None


def _species_class_string(species):
    """Map a species model class to its CellDesigner class string."""
    return _CLASS_TO_CD_STRING.get(type(species), "UNKNOWN")


def _template_ref_tag(template):
    """Map a template to its XML reference tag name."""
    if isinstance(template, momapy.celldesigner.core.ProteinTemplate):
        return "proteinReference"
    if isinstance(template, momapy.celldesigner.core.GeneTemplate):
        return "geneReference"
    if isinstance(template, momapy.celldesigner.core.RNATemplate):
        return "rnaReference"
    if isinstance(template, momapy.celldesigner.core.AntisenseRNATemplate):
        return "antisensernaReference"
    return "proteinReference"


def _modification_state_string(state):
    """Convert modification state to CellDesigner string."""
    if state is None:
        return "empty"
    name = state.name if hasattr(state, "name") else str(state)
    return _MODIFICATION_STATE_TO_CD.get(name, "empty")


_bounds_attrs = _writing.node_to_bounds_attrs


def _anchor_name_to_position(anchor_name):
    """Convert an anchor name to CellDesigner link anchor position string."""
    return _writing._ANCHOR_NAME_TO_LINK_ANCHOR_POSITION.get(anchor_name)


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
    pts = reaction_layout.points()
    n_segments = len(reaction_layout.segments)
    seg_idx = reaction_layout.reaction_node_segment
    if seg_idx < n_segments:
        seg = reaction_layout.segments[seg_idx]
        dx = seg.p2.x - seg.p1.x
        dy = seg.p2.y - seg.p1.y
    else:
        dx = pts[-1].x - pts[0].x
        dy = pts[-1].y - pts[0].y
    angle = math.atan2(dy, dx)
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
    for anchor_id, (ox, oy) in offsets.items():
        rx = mid.x + ox * cos_a - oy * sin_a
        ry = mid.y + ox * sin_a + oy * cos_a
        dist = (rx - end_point.x) ** 2 + (ry - end_point.y) ** 2
        if dist < best_dist:
            best_dist = dist
            best_id = anchor_id
    return f"0,{best_id}"


def _infer_anchor_position(species_layout, point, tol=5.0):
    """Find the CellDesigner linkAnchor position for a point on a species."""
    import math
    for cd_position, anchor_name in (
        momapy.celldesigner.io.celldesigner._reading_parsing
        ._LINK_ANCHOR_POSITION_TO_ANCHOR_NAME.items()
    ):
        anchor_point = species_layout.anchor_point(anchor_name)
        if anchor_point is None:
            continue
        if math.isclose(anchor_point.x, point.x, abs_tol=tol) and math.isclose(
            anchor_point.y, point.y, abs_tol=tol
        ):
            return cd_position
    return None


# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------


class CellDesignerWriter(momapy.io.core.Writer):
    """CellDesigner XML writer (model-first approach)."""

    @classmethod
    def write(
        cls,
        obj,
        file_path,
        annotations=None,
        notes=None,
        ids=None,
        with_annotations=True,
        with_notes=True,
        **options,
    ):
        """Write a CellDesigner map to a file.

        Args:
            obj: A CellDesignerMap instance.
            file_path: Output file path.
            annotations: Annotations dict from reader result.
            notes: Notes dict from reader result.
            ids: IDs mapping from reader result.
            with_annotations: Whether to write annotations.
            with_notes: Whether to write notes.

        Returns:
            WriterResult.
        """
        if annotations is None:
            annotations = {}
        if notes is None:
            notes = {}
        if ids is None:
            ids = {}

        subunit_to_complex = {}
        species_to_id = {}
        if obj.model is not None:
            def _collect(species):
                sid = _strip_active(species)
                if id(species) not in species_to_id:
                    species_to_id[id(species)] = sid
                if isinstance(species, momapy.celldesigner.core.Complex):
                    for sub in species.subunits:
                        subunit_to_complex[sub] = species
                        _collect(sub)
            for species in obj.model.species:
                _collect(species)

        ctx = WritingContext(
            map_=obj,
            annotations=annotations,
            notes=notes,
            ids=ids,
            with_annotations=with_annotations,
            with_notes=with_notes,
            subunit_to_complex=subunit_to_complex,
            species_to_id=species_to_id,
        )

        sbml = cls._build_sbml(ctx)
        tree = lxml.etree.ElementTree(sbml)
        tree.write(
            file_path,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )
        return momapy.io.core.WriterResult(obj=obj, file_path=file_path)

    # --- Top-level structure ---

    @classmethod
    def _build_sbml(cls, ctx):
        sbml = _el(
            "sbml",
            attrs={"level": "2", "version": "4"},
            nsmap=_NSMAP,
        )
        sbml.append(cls._build_model(ctx))
        return sbml

    @classmethod
    def _build_model(cls, ctx):
        model_id = ctx.map_.id_ or "untitled"
        model = _el("model", attrs={"metaid": model_id, "id": model_id})
        # notes
        model_notes = ctx.notes.get(ctx.map_, set())
        if model_notes:
            notes_elem = _el("notes")
            for note in model_notes:
                try:
                    parsed = lxml.etree.fromstring(note)
                    notes_elem.append(parsed)
                except lxml.etree.XMLSyntaxError:
                    pass
            model.append(notes_elem)
        # annotation
        annotation = _el("annotation")
        annotation.append(cls._build_extension(ctx))
        model.append(annotation)
        model.append(cls._build_list_of_compartments(ctx))
        model.append(cls._build_list_of_species(ctx))
        model.append(cls._build_list_of_reactions(ctx))
        return model

    # --- Extension (CD annotation) ---

    @classmethod
    def _build_extension(cls, ctx):
        ext = _cd("extension")
        ext.append(_cd("modelVersion", text="4.0"))
        display_attrs = {
            "sizeX": str(int(ctx.map_.layout.width)),
            "sizeY": str(int(ctx.map_.layout.height)),
        }
        ext.append(_cd("modelDisplay", attrs=display_attrs))
        ext.append(cls._build_list_of_included_species(ctx))
        ext.append(cls._build_list_of_compartment_aliases(ctx))
        ext.append(cls._build_list_of_complex_species_aliases(ctx))
        ext.append(cls._build_list_of_species_aliases(ctx))
        ext.append(cls._build_list_of_proteins(ctx))
        ext.append(cls._build_list_of_genes(ctx))
        ext.append(cls._build_list_of_rnas(ctx))
        ext.append(cls._build_list_of_antisense_rnas(ctx))
        ext.append(_cd("listOfLayers"))
        return ext

    # --- Compartment aliases ---

    @classmethod
    def _build_list_of_compartment_aliases(cls, ctx):
        list_elem = _cd("listOfCompartmentAliases")
        for comp in sorted(ctx.map_.model.compartments, key=lambda c: c.id_):
            for layout_key in _get_layouts(ctx, comp):
                if isinstance(layout_key, frozenset):
                    continue
                if isinstance(
                    layout_key,
                    (
                        momapy.celldesigner.core.RectangleCompartmentLayout,
                        momapy.celldesigner.core.OvalCompartmentLayout,
                    ),
                ):
                    alias = _cd(
                        "compartmentAlias",
                        attrs={
                            "id": layout_key.id_,
                            "compartment": comp.id_,
                        },
                    )
                    class_name = (
                        "OVAL"
                        if isinstance(
                            layout_key,
                            momapy.celldesigner.core.OvalCompartmentLayout,
                        )
                        else "SQUARE"
                    )
                    alias.append(
                        _cd("class", text=class_name)
                    )
                    alias.append(_cd("bounds", attrs=_bounds_attrs(layout_key)))
                    # namePoint (label position)
                    label = getattr(layout_key, "label", None)
                    if label is not None:
                        alias.append(
                            _cd(
                                "namePoint",
                                attrs={
                                    "x": str(label.position.x),
                                    "y": str(label.position.y),
                                },
                            )
                        )
                    # doubleLine
                    sep = getattr(layout_key, "sep", None)
                    sw = getattr(layout_key, "stroke_width", None)
                    isw = getattr(layout_key, "inner_stroke_width", None)
                    alias.append(
                        _cd(
                            "doubleLine",
                            attrs={
                                "thickness": str(sep) if sep else "12.0",
                                "outerWidth": str(sw) if sw else "2.0",
                                "innerWidth": str(isw) if isw else "1.0",
                            },
                        )
                    )
                    # paint — reader sets alpha=0.5 for rendering,
                    # but CellDesigner expects full opacity
                    fill = getattr(layout_key, "fill", None)
                    if fill is not None and fill is not momapy.drawing.NoneValue:
                        paint_color = _color_hex(fill.with_alpha(1.0))
                    else:
                        paint_color = "ffcccccc"
                    alias.append(
                        _cd("paint", attrs={"color": paint_color, "scheme": "Color"})
                    )
                    alias.append(
                        _cd("info", attrs={"state": "empty", "angle": "-1.5707963267948966"})
                    )
                    list_elem.append(alias)
        return list_elem

    # --- Included species (complex subunits) ---

    @classmethod
    def _build_list_of_included_species(cls, ctx):
        list_elem = _cd("listOfIncludedSpecies")
        seen_ids = set()
        for species in sorted(ctx.map_.model.species, key=lambda s: s.id_):
            if isinstance(species, momapy.celldesigner.core.Complex):
                cls._collect_included_species(
                    ctx, species, species, list_elem, seen_ids
                )
        return list_elem

    @classmethod
    def _collect_included_species(
        cls, ctx, complex_, root_complex, list_elem, seen_ids
    ):
        """Recursively collect included species from a complex."""
        for sub in sorted(complex_.subunits, key=lambda s: s.id_):
            sub_id = _get_species_id(sub, ctx)
            if sub_id not in seen_ids:
                seen_ids.add(sub_id)
                list_elem.append(
                    cls._build_included_species(ctx, sub, complex_)
                )
            if isinstance(sub, momapy.celldesigner.core.Complex):
                cls._collect_included_species(
                    ctx, sub, root_complex, list_elem, seen_ids
                )

    @classmethod
    def _build_included_species(cls, ctx, species, parent_complex):
        sp = _cd(
            "species",
            attrs={
                "id": _get_species_id(species, ctx),
                "name": _encode_name(species.name) or "",
            },
        )
        # notes (CellDesigner expects exactly one <html> child)
        notes = _cd("notes")
        species_notes = ctx.notes.get(species, set())
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
        sp.append(notes)
        # annotation
        ann = _cd("annotation")
        ann.append(
            _cd("complexSpecies", text=_get_species_id(parent_complex, ctx))
        )
        ann.append(cls._build_species_identity(ctx, species))
        sp.append(ann)
        return sp

    # --- Species identity ---

    @classmethod
    def _build_species_identity(cls, ctx, species):
        identity = _cd("speciesIdentity")
        identity.append(_cd("class", text=_species_class_string(species)))
        template = getattr(species, "template", None)
        if template is not None:
            tag = _template_ref_tag(template)
            # For genes/RNAs/antisenseRNAs, the reference ID is per-species
            # (not the shared template ID), matching the listOfGenes entries.
            if isinstance(species, momapy.celldesigner.core.Gene):
                ref_id = "g_" + _get_species_id(species, ctx)
            elif isinstance(species, momapy.celldesigner.core.RNA):
                ref_id = "rna_" + _get_species_id(species, ctx)
            elif isinstance(species, momapy.celldesigner.core.AntisenseRNA):
                ref_id = "ar_" + _get_species_id(species, ctx)
            else:
                ref_id = template.id_
            identity.append(_cd(tag, text=ref_id))
        identity.append(_cd("name", text=_encode_name(species.name) or ""))
        state = cls._build_species_state(ctx, species)
        if state is not None:
            identity.append(state)
        return identity

    @classmethod
    def _build_species_state(cls, ctx, species):
        has_mods = hasattr(species, "modifications") and species.modifications
        has_homo = hasattr(species, "homomultimer") and species.homomultimer > 1
        has_struct = (
            hasattr(species, "structural_states")
            and species.structural_states
        )
        if not has_mods and not has_homo and not has_struct:
            return None
        state = _cd("state")
        if has_homo:
            state.append(_cd("homodimer", text=str(species.homomultimer)))
        if has_struct:
            ss_list = _cd("listOfStructuralStates")
            for ss in species.structural_states:
                if ss.value is not None:
                    ss_list.append(
                        _cd(
                            "structuralState",
                            attrs={"structuralState": ss.value},
                            text=ss.value,
                        )
                    )
            state.append(ss_list)
        if has_mods:
            mod_list = _cd("listOfModifications")
            for mod in sorted(
                species.modifications,
                key=lambda m: m.residue.id_ if m.residue else "",
            ):
                mod_attrs = {}
                if mod.residue is not None:
                    parts = mod.residue.id_.split("_", 1)
                    mod_attrs["residue"] = parts[1] if len(parts) > 1 else mod.residue.id_
                mod_attrs["state"] = _modification_state_string(mod.state)
                mod_list.append(_cd("modification", attrs=mod_attrs))
            state.append(mod_list)
        return state

    # --- Complex species aliases ---

    @classmethod
    def _build_list_of_complex_species_aliases(cls, ctx):
        list_elem = _cd("listOfComplexSpeciesAliases")
        # Top-level complexes
        for species in sorted(ctx.map_.model.species, key=lambda s: s.id_):
            if not isinstance(species, momapy.celldesigner.core.Complex):
                continue
            cls._collect_complex_aliases(ctx, species, list_elem)
        return list_elem

    @classmethod
    def _collect_complex_aliases(cls, ctx, complex_, list_elem):
        """Collect complex aliases by walking layout containment."""
        for layout_key in _get_layouts(ctx, complex_):
            if isinstance(layout_key, frozenset):
                continue
            if isinstance(layout_key, momapy.celldesigner.core.ComplexLayout):
                list_elem.append(
                    cls._build_alias(
                        ctx, layout_key, complex_, "complexSpeciesAlias"
                    )
                )
                # Collect nested complex layouts from children
                cls._collect_nested_complex_aliases(ctx, layout_key, list_elem)

    @classmethod
    def _collect_nested_complex_aliases(cls, ctx, parent_layout, list_elem):
        """Walk layout children and emit complexSpeciesAliases for nested complexes."""
        for child in sorted(
            parent_layout.layout_elements, key=lambda e: e.id_
        ):
            if not isinstance(child, momapy.celldesigner.core.ComplexLayout):
                continue
            model_info = _mapping(ctx).get_mapping(child)
            if model_info is None:
                continue
            model_elem = model_info[0] if isinstance(model_info, tuple) else model_info
            list_elem.append(
                cls._build_alias(ctx, child, model_elem, "complexSpeciesAlias")
            )
            # Recurse deeper
            cls._collect_nested_complex_aliases(ctx, child, list_elem)

    # --- Species aliases ---

    @classmethod
    def _build_list_of_species_aliases(cls, ctx):
        list_elem = _cd("listOfSpeciesAliases")
        # Top-level species (non-complex, non-subunit)
        for species in sorted(ctx.map_.model.species, key=lambda s: s.id_):
            if isinstance(species, momapy.celldesigner.core.Complex):
                continue
            if species in ctx.subunit_to_complex:
                continue
            for layout_key in _get_layouts(ctx, species):
                if isinstance(layout_key, frozenset):
                    continue
                if isinstance(
                    layout_key, momapy.celldesigner.core.CellDesignerNode
                ):
                    list_elem.append(
                        cls._build_alias(
                            ctx, layout_key, species, "speciesAlias"
                        )
                    )
        # Subunit species (inside complexes), recursively
        for species in sorted(ctx.map_.model.species, key=lambda s: s.id_):
            if not isinstance(species, momapy.celldesigner.core.Complex):
                continue
            cls._collect_subunit_aliases(ctx, species, list_elem)
        return list_elem

    @classmethod
    def _collect_subunit_aliases(cls, ctx, complex_, list_elem):
        """Collect species aliases for subunits by walking layout containment.

        Instead of using the mapping (which conflates different
        instances of the same nested complex), walk the complex
        layout's children directly.
        """
        for complex_layout in _get_layouts(ctx, complex_):
            if isinstance(complex_layout, frozenset):
                continue
            if not isinstance(
                complex_layout, momapy.celldesigner.core.ComplexLayout
            ):
                continue
            cls._collect_aliases_from_layout_children(
                ctx, complex_layout, complex_layout.id_, list_elem
            )

    @classmethod
    def _collect_aliases_from_layout_children(
        cls, ctx, parent_layout, complex_alias_id, list_elem
    ):
        """Walk layout children and emit speciesAliases for non-complex nodes."""
        for child in sorted(
            parent_layout.layout_elements, key=lambda e: e.id_
        ):
            if isinstance(child, momapy.celldesigner.core.ComplexLayout):
                # Recurse into nested complex layouts
                cls._collect_aliases_from_layout_children(
                    ctx, child, child.id_, list_elem
                )
                continue
            if not isinstance(
                child, momapy.celldesigner.core.CellDesignerNode
            ):
                continue
            # Get the model element for this layout
            model_info = _mapping(ctx).get_mapping(child)
            if model_info is None:
                continue
            model_elem = model_info[0] if isinstance(model_info, tuple) else model_info
            list_elem.append(
                cls._build_alias(
                    ctx,
                    child,
                    model_elem,
                    "speciesAlias",
                    complex_alias_id=complex_alias_id,
                )
            )

    @classmethod
    def _find_compartment_alias_id(cls, ctx, species_layout):
        """Find the compartment alias containing this species layout."""
        species_center = species_layout.center()
        best_id = None
        best_area = float("inf")
        for comp in ctx.map_.model.compartments:
            if comp.id_ == "default":
                continue
            for layout_key in _get_layouts(ctx, comp):
                if isinstance(layout_key, frozenset):
                    continue
                if isinstance(
                    layout_key,
                    (
                        momapy.celldesigner.core.RectangleCompartmentLayout,
                        momapy.celldesigner.core.OvalCompartmentLayout,
                    ),
                ):
                    bbox = layout_key.bbox()
                    nw = bbox.north_west()
                    se = bbox.south_east()
                    if (nw.x <= species_center.x <= se.x
                            and nw.y <= species_center.y <= se.y):
                        area = bbox.width * bbox.height
                        if area < best_area:
                            best_area = area
                            best_id = layout_key.id_
        return best_id

    @classmethod
    def _build_alias(cls, ctx, layout, model, tag, complex_alias_id=None):
        attrs = {
            "id": layout.id_,
            "species": _get_species_id(model, ctx),
        }
        if complex_alias_id is not None:
            attrs["complexSpeciesAlias"] = complex_alias_id
        elif tag == "speciesAlias" or tag == "complexSpeciesAlias":
            comp_alias = cls._find_compartment_alias_id(ctx, layout)
            if comp_alias is not None:
                attrs["compartmentAlias"] = comp_alias
        alias = _cd(tag, attrs=attrs)
        alias.append(_cd("activity", text="inactive"))
        alias.append(_cd("bounds", attrs=_bounds_attrs(layout)))
        alias.append(_cd("font", attrs={"size": "12"}))
        alias.append(_cd("view", attrs={"state": "usual"}))
        if tag == "complexSpeciesAlias":
            alias.append(_cd("backupSize", attrs={"w": "0.0", "h": "0.0"}))
            alias.append(_cd("backupView", attrs={"state": "none"}))
        # usualView
        usual = _cd("usualView")
        usual.append(_cd("innerPosition", attrs={"x": "0.0", "y": "0.0"}))
        usual.append(
            _cd(
                "boxSize",
                attrs={
                    "width": str(layout.width),
                    "height": str(layout.height),
                },
            )
        )
        line_width = "2.0" if tag == "complexSpeciesAlias" else "1.0"
        usual.append(_cd("singleLine", attrs={"width": line_width}))
        fill = getattr(layout, "fill", None)
        if fill is not None and fill is not momapy.drawing.NoneValue:
            paint_color = _color_hex(fill)
        else:
            paint_color = "fff7f7f7" if tag == "complexSpeciesAlias" else "ffccffcc"
        usual.append(
            _cd("paint", attrs={"color": paint_color, "scheme": "Color"})
        )
        alias.append(usual)
        # briefView (same as usualView)
        brief = _cd("briefView")
        brief.append(_cd("innerPosition", attrs={"x": "0.0", "y": "0.0"}))
        brief.append(
            _cd(
                "boxSize",
                attrs={
                    "width": str(layout.width),
                    "height": str(layout.height),
                },
            )
        )
        brief.append(_cd("singleLine", attrs={"width": line_width}))
        brief.append(
            _cd("paint", attrs={"color": paint_color, "scheme": "Color"})
        )
        alias.append(brief)
        alias.append(
            _cd(
                "info",
                attrs={
                    "state": "empty",
                    "angle": "-1.5707963267948966",
                },
            )
        )
        return alias

    # --- Proteins (templates) ---

    @classmethod
    def _build_list_of_proteins(cls, ctx):
        list_elem = _cd("listOfProteins")
        for tmpl in sorted(ctx.map_.model.species_templates, key=lambda t: t.id_):
            if not isinstance(tmpl, momapy.celldesigner.core.ProteinTemplate):
                continue
            protein_type = "GENERIC"
            if isinstance(tmpl, momapy.celldesigner.core.ReceptorTemplate):
                protein_type = "RECEPTOR"
            elif isinstance(tmpl, momapy.celldesigner.core.IonChannelTemplate):
                protein_type = "ION_CHANNEL"
            elif isinstance(tmpl, momapy.celldesigner.core.TruncatedProteinTemplate):
                protein_type = "TRUNCATED"
            attrs = {
                "id": tmpl.id_,
                "name": _encode_name(tmpl.name) or "",
                "type": protein_type,
            }
            protein = _cd("protein", attrs=attrs)
            if tmpl.modification_residues:
                mr_list = _cd("listOfModificationResidues")
                for residue in sorted(
                    tmpl.modification_residues, key=lambda r: r.id_
                ):
                    parts = residue.id_.split("_", 1)
                    res_id = parts[1] if len(parts) > 1 else residue.id_
                    mr_attrs = {"id": res_id}
                    if residue.name is not None:
                        mr_attrs["name"] = residue.name
                    # Compute angle from layout if available
                    mr_attrs["angle"] = cls._find_residue_angle(ctx, tmpl, residue)
                    mr_attrs["side"] = "none"
                    mr_list.append(_cd("modificationResidue", attrs=mr_attrs))
                protein.append(mr_list)
            list_elem.append(protein)
        return list_elem

    @classmethod
    def _find_residue_angle(cls, ctx, template, residue):
        """Find the angle for a modification residue from layout data."""
        # Search species that use this template for a ModificationLayout
        for species in ctx.map_.model.species:
            tmpl = getattr(species, "template", None)
            if tmpl is not template:
                continue
            for layout_key in _get_layouts(ctx, species):
                if isinstance(layout_key, frozenset):
                    continue
                if not isinstance(
                    layout_key, momapy.celldesigner.core.CellDesignerNode
                ):
                    continue
                children = getattr(layout_key, "layout_elements", None)
                if not children:
                    continue
                for child in children:
                    if isinstance(
                        child, momapy.celldesigner.core.ModificationLayout
                    ):
                        child_model = _mapping(ctx).get_mapping(child)
                        if child_model is not None:
                            mod = child_model[0] if isinstance(child_model, tuple) else child_model
                            if hasattr(mod, "residue") and mod.residue is residue:
                                # Compute angle from positions
                                species_center = layout_key.center()
                                mod_pos = child.position
                                import math
                                angle = math.atan2(
                                    mod_pos.y - species_center.y,
                                    mod_pos.x - species_center.x,
                                )
                                return str(angle)
        return "0.0"

    # --- Genes, RNAs, AntisenseRNAs (templates) ---

    @classmethod
    def _build_list_of_genes(cls, ctx):
        """Build listOfGenes — one entry per Gene species, not per template."""
        list_elem = _cd("listOfGenes")
        for species in cls._all_species_recursive(ctx):
            if not isinstance(species, momapy.celldesigner.core.Gene):
                continue
            tmpl = getattr(species, "template", None)
            gene_id = "g_" + _get_species_id(species, ctx)
            name = _encode_name(tmpl.name if tmpl else species.name) or ""
            list_elem.append(
                _cd("gene", attrs={"type": "GENE", "id": gene_id, "name": name})
            )
        return list_elem

    @classmethod
    def _build_list_of_rnas(cls, ctx):
        """Build listOfRNAs — one entry per RNA species."""
        list_elem = _cd("listOfRNAs")
        for species in cls._all_species_recursive(ctx):
            if not isinstance(species, momapy.celldesigner.core.RNA):
                continue
            tmpl = getattr(species, "template", None)
            rna_id = "rna_" + _get_species_id(species, ctx)
            name = _encode_name(tmpl.name if tmpl else species.name) or ""
            list_elem.append(
                _cd("RNA", attrs={"type": "RNA", "id": rna_id, "name": name})
            )
        return list_elem

    @classmethod
    def _build_list_of_antisense_rnas(cls, ctx):
        """Build listOfAntisenseRNAs — one entry per AntisenseRNA species."""
        list_elem = _cd("listOfAntisenseRNAs")
        for species in cls._all_species_recursive(ctx):
            if not isinstance(species, momapy.celldesigner.core.AntisenseRNA):
                continue
            tmpl = getattr(species, "template", None)
            arna_id = "ar_" + _get_species_id(species, ctx)
            name = _encode_name(tmpl.name if tmpl else species.name) or ""
            list_elem.append(
                _cd("antisenseRNA", attrs={"type": "ANTISENSE_RNA", "id": arna_id, "name": name})
            )
        return list_elem

    @classmethod
    def _all_species_recursive(cls, ctx):
        """Yield all species including subunits, sorted by id."""
        result = []
        def _collect(species):
            result.append(species)
            if isinstance(species, momapy.celldesigner.core.Complex):
                for sub in species.subunits:
                    _collect(sub)
        for species in ctx.map_.model.species:
            _collect(species)
        return sorted(result, key=lambda s: s.id_)

    # --- Compartments ---

    @classmethod
    def _build_list_of_compartments(cls, ctx):
        list_elem = _el("listOfCompartments")
        for comp in sorted(ctx.map_.model.compartments, key=lambda c: c.id_):
            attrs = {
                "id": comp.id_,
                "metaid": comp.id_,
                "name": _encode_name(comp.name) or "",
                "size": "1",
                "units": "volume",
            }
            outside = getattr(comp, "outside", None)
            if outside is not None:
                attrs["outside"] = outside.id_
            list_elem.append(_el("compartment", attrs=attrs))
        return list_elem

    # --- SBML species ---

    @classmethod
    def _build_list_of_species(cls, ctx):
        list_elem = _el("listOfSpecies")
        seen_ids = set()
        for species in sorted(ctx.map_.model.species, key=lambda s: s.id_):
            # Skip subunits — they are only in listOfIncludedSpecies
            if species in ctx.subunit_to_complex:
                continue
            species_id = _get_species_id(species, ctx)
            if species_id in seen_ids:
                continue
            seen_ids.add(species_id)
            list_elem.append(cls._build_sbml_species(ctx, species))
        return list_elem

    @classmethod
    def _build_sbml_species(cls, ctx, species):
        species_id = _get_species_id(species, ctx)
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
        sp = _el("species", attrs=attrs)
        # annotation with CD extension
        ann = _el("annotation")
        ext = _cd("extension")
        ext.append(_cd("positionToCompartment", text="inside"))
        ext.append(cls._build_species_identity(ctx, species))
        # listOfCatalyzedReactions
        catalyzed = cls._find_catalyzed_reactions(ctx, species)
        if catalyzed:
            cat_list = _cd("listOfCatalyzedReactions")
            for rxn_id in catalyzed:
                cat_list.append(_cd("catalyzed", attrs={"reaction": rxn_id}))
            ext.append(cat_list)
        ann.append(ext)
        sp.append(ann)
        return sp

    @classmethod
    def _find_catalyzed_reactions(cls, ctx, species):
        """Find reactions catalyzed by this species."""
        result = []
        for reaction in ctx.map_.model.reactions:
            for modifier in reaction.modifiers:
                if (
                    isinstance(modifier, momapy.celldesigner.core.Catalyzer)
                    and modifier.referred_species is species
                ):
                    result.append(reaction.id_)
        return sorted(result)

    # --- Reactions ---

    @classmethod
    def _build_list_of_reactions(cls, ctx):
        list_elem = _el("listOfReactions")
        for reaction in sorted(ctx.map_.model.reactions, key=lambda r: r.id_):
            list_elem.append(cls._build_reaction(ctx, reaction))
        for modulation in sorted(ctx.map_.model.modulations, key=lambda m: m.id_):
            mod_rxn = cls._build_modulation_as_reaction(ctx, modulation)
            if mod_rxn is not None:
                list_elem.append(mod_rxn)
        return list_elem

    @classmethod
    def _build_reaction(cls, ctx, reaction):
        attrs = {
            "metaid": reaction.id_,
            "id": reaction.id_,
            "reversible": "false",
        }
        rxn = _el("reaction", attrs=attrs)

        # Find the frozenset for this reaction
        fset = None
        reaction_layout = None
        for layout_key in _get_layouts(ctx, reaction):
            if isinstance(layout_key, frozenset):
                fset = layout_key
                reaction_layout = _get_reaction_layout(layout_key)
                break

        # CD extension
        ann = _el("annotation")
        ext = _cd("extension")
        reaction_type = _CLASS_TO_REACTION_TYPE.get(
            type(reaction), "STATE_TRANSITION"
        )
        ext.append(_cd("reactionType", text=reaction_type))

        # Split reactants/products into base + links using the base flag.
        all_reactants = sorted(reaction.reactants, key=lambda r: r.id_)
        all_products = sorted(reaction.products, key=lambda p: p.id_)
        base_reactants, link_reactants = cls._split_base_and_links(
            all_reactants
        )
        base_products, link_products = cls._split_base_and_links(
            all_products
        )
        is_left_t = isinstance(
            reaction, momapy.celldesigner.core.HeterodimerAssociation
        )
        is_right_t = isinstance(
            reaction,
            (
                momapy.celldesigner.core.Dissociation,
                momapy.celldesigner.core.Truncation,
            ),
        )

        # baseReactants — for left-T with 1 model reactant but 2 visual
        # copies (stoichiometry), use consumption arcs to find all aliases.
        br_elem = _cd("baseReactants")
        if is_left_t and len(base_reactants) == 1 and reaction_layout is not None:
            base_species = base_reactants[0].referred_species
            for le in ctx.map_.layout.layout_elements:
                if (
                    isinstance(le, momapy.celldesigner.core.ConsumptionLayout)
                    and le.source is reaction_layout
                ):
                    # Only base arcs: target must map to the base species
                    target_model = _mapping(ctx).get_mapping(le.target)
                    if target_model is not None:
                        tm = target_model[0] if isinstance(target_model, tuple) else target_model
                        if tm is not base_species:
                            continue
                    alias_layout = le.target
                    br_elem.append(
                        cls._build_base_participant_from_layout(
                            ctx, base_species, alias_layout,
                            "baseReactant", reaction_layout, is_start=True,
                        )
                    )
        else:
            for reactant in base_reactants:
                br_elem.append(
                    cls._build_base_participant(
                        ctx, reactant, "baseReactant", fset,
                        reaction_layout, is_start=True,
                    )
                )
        ext.append(br_elem)

        # baseProducts — same for right-T with 1 model product but 2 aliases.
        bp_elem = _cd("baseProducts")
        if is_right_t and len(base_products) == 1 and reaction_layout is not None:
            base_species = base_products[0].referred_species
            for le in ctx.map_.layout.layout_elements:
                if (
                    isinstance(le, momapy.celldesigner.core.ProductionLayout)
                    and le.source is reaction_layout
                ):
                    target_model = _mapping(ctx).get_mapping(le.target)
                    if target_model is not None:
                        tm = target_model[0] if isinstance(target_model, tuple) else target_model
                        if tm is not base_species:
                            continue
                    alias_layout = le.target
                    bp_elem.append(
                        cls._build_base_participant_from_layout(
                            ctx, base_species, alias_layout,
                            "baseProduct", reaction_layout, is_start=False,
                        )
                    )
        else:
            for product in base_products:
                bp_elem.append(
                    cls._build_base_participant(
                        ctx, product, "baseProduct", fset,
                        reaction_layout, is_start=False,
                    )
                )
        ext.append(bp_elem)

        # listOfReactantLinks
        rl_elem = _cd("listOfReactantLinks")
        for reactant in link_reactants:
            rl_elem.append(
                cls._build_participant_link(
                    ctx, reactant, "reactantLink", "reactant", fset,
                    reaction_layout=reaction_layout,
                )
            )
        ext.append(rl_elem)

        # listOfProductLinks
        pl_elem = _cd("listOfProductLinks")
        for product in link_products:
            pl_elem.append(
                cls._build_participant_link(
                    ctx, product, "productLink", "product", fset,
                    reaction_layout=reaction_layout,
                )
            )
        ext.append(pl_elem)

        # connectScheme + editPoints
        cls._build_reaction_connect_scheme(
            ctx, ext, reaction, reaction_layout, fset,
            base_reactants, base_products,
            is_left_t, is_right_t,
        )

        # listOfModification
        mod_list = _cd("listOfModification")
        modifiers = sorted(reaction.modifiers, key=lambda m: m.id_)
        for modifier in modifiers:
            species = modifier.referred_species
            if isinstance(species, momapy.celldesigner.core.BooleanLogicGate):
                # Write gate entry + per-input entries
                gate_mods = cls._build_boolean_gate_modifications(
                    ctx, modifier, species, reaction_layout, fset
                )
                for gm in gate_mods:
                    mod_list.append(gm)
            else:
                mod_elem = cls._build_reaction_modification(
                    ctx, modifier, reaction_layout, fset
                )
                if mod_elem is not None:
                    mod_list.append(mod_elem)
        ext.append(mod_list)

        # line
        ext.append(_cd("line", attrs={"width": "1.0", "color": "ff000000", "type": "Straight"}))

        ann.append(ext)
        rxn.append(ann)

        # SBML listOfReactants — base first, then links.
        # For left-T with stoichiometry, duplicate from arcs.
        lor = _el("listOfReactants")
        if is_left_t and len(base_reactants) == 1 and reaction_layout is not None:
            base_species = base_reactants[0].referred_species
            for le in ctx.map_.layout.layout_elements:
                if (
                    isinstance(le, momapy.celldesigner.core.ConsumptionLayout)
                    and le.source is reaction_layout
                ):
                    target_model = _mapping(ctx).get_mapping(le.target)
                    if target_model is not None:
                        tm = target_model[0] if isinstance(target_model, tuple) else target_model
                        if tm is not base_species:
                            continue
                    sbml_species = ctx.subunit_to_complex.get(base_species, base_species)
                    alias_id = le.target.id_ if le.target else ""
                    sr = _el("speciesReference", attrs={"species": _get_species_id(sbml_species, ctx)})
                    sr_ann = _el("annotation")
                    sr_ext = _cd("extension")
                    sr_ext.append(_cd("alias", text=alias_id))
                    sr_ann.append(sr_ext)
                    sr.append(sr_ann)
                    lor.append(sr)
        else:
            for reactant in base_reactants:
                lor.append(
                    cls._build_sbml_species_reference(ctx, reactant, fset)
                )
        for reactant in link_reactants:
            lor.append(
                cls._build_sbml_species_reference(ctx, reactant, fset)
            )
        rxn.append(lor)

        # SBML listOfProducts — same for right-T.
        lop = _el("listOfProducts")
        if is_right_t and len(base_products) == 1 and reaction_layout is not None:
            base_species = base_products[0].referred_species
            for le in ctx.map_.layout.layout_elements:
                if (
                    isinstance(le, momapy.celldesigner.core.ProductionLayout)
                    and le.source is reaction_layout
                ):
                    target_model = _mapping(ctx).get_mapping(le.target)
                    if target_model is not None:
                        tm = target_model[0] if isinstance(target_model, tuple) else target_model
                        if tm is not base_species:
                            continue
                    sbml_species = ctx.subunit_to_complex.get(base_species, base_species)
                    alias_id = le.target.id_ if le.target else ""
                    sr = _el("speciesReference", attrs={"species": _get_species_id(sbml_species, ctx)})
                    sr_ann = _el("annotation")
                    sr_ext = _cd("extension")
                    sr_ext.append(_cd("alias", text=alias_id))
                    sr_ann.append(sr_ext)
                    sr.append(sr_ann)
                    lop.append(sr)
        else:
            for product in base_products:
                lop.append(
                    cls._build_sbml_species_reference(ctx, product, fset)
                )
        for product in link_products:
            lop.append(
                cls._build_sbml_species_reference(ctx, product, fset)
            )
        rxn.append(lop)

        # SBML listOfModifiers
        if modifiers:
            lom = _el("listOfModifiers")
            for modifier in modifiers:
                species = modifier.referred_species
                if isinstance(species, momapy.celldesigner.core.BooleanLogicGate):
                    # Write each input species as a separate modifier
                    for inp in sorted(species.inputs, key=lambda s: s.id_):
                        sbml_inp = ctx.subunit_to_complex.get(inp, inp)
                        alias_layout = (
                            _find_layout_for_species_in_frozenset(ctx, inp, fset)
                            if fset else None
                        )
                        if alias_layout is None:
                            for lk in _get_layouts(ctx, inp):
                                if isinstance(lk, frozenset):
                                    continue
                                if isinstance(lk, momapy.celldesigner.core.CellDesignerNode):
                                    alias_layout = lk
                                    break
                        alias_id = alias_layout.id_ if alias_layout else ""
                        msr = _el("modifierSpeciesReference", attrs={"species": _get_species_id(sbml_inp, ctx)})
                        msr_ann = _el("annotation")
                        msr_ext = _cd("extension")
                        msr_ext.append(_cd("alias", text=alias_id))
                        msr_ann.append(msr_ext)
                        msr.append(msr_ann)
                        lom.append(msr)
                    continue
                sbml_species = ctx.subunit_to_complex.get(species, species)
                alias_layout = (
                    _find_layout_for_species_in_frozenset(ctx, species, fset)
                    if fset
                    else None
                )
                alias_id = alias_layout.id_ if alias_layout else ""
                msr_attrs = {"species": _get_species_id(sbml_species, ctx)}
                if modifier.id_:
                    msr_attrs["metaid"] = _unique_metaid(ctx, modifier.id_)
                msr = _el("modifierSpeciesReference", attrs=msr_attrs)
                msr_ann = _el("annotation")
                msr_ext = _cd("extension")
                msr_ext.append(_cd("alias", text=alias_id))
                msr_ann.append(msr_ext)
                msr.append(msr_ann)
                lom.append(msr)
            rxn.append(lom)

        return rxn

    @classmethod
    def _split_base_and_links(cls, participants):
        """Split participants into base and link using the base flag."""
        base = [p for p in participants if p.base]
        link = [p for p in participants if not p.base]
        return base, link

    @classmethod
    def _build_sbml_species_reference(cls, ctx, participant, fset):
        """Build an SBML speciesReference element."""
        species = participant.referred_species
        sbml_species = ctx.subunit_to_complex.get(species, species)
        alias_layout = (
            _find_layout_for_species_in_frozenset(ctx, species, fset)
            if fset else None
        )
        alias_id = alias_layout.id_ if alias_layout else ""
        sr_attrs = {"species": _get_species_id(sbml_species, ctx)}
        if participant.metaid:
            sr_attrs["metaid"] = _unique_metaid(ctx, participant.metaid)
        sr = _el("speciesReference", attrs=sr_attrs)
        sr_ann = _el("annotation")
        sr_ext = _cd("extension")
        sr_ext.append(_cd("alias", text=alias_id))
        sr_ann.append(sr_ext)
        sr.append(sr_ann)
        return sr

    @classmethod
    def _build_base_participant_from_layout(
        cls, ctx, species, alias_layout, tag, reaction_layout, is_start
    ):
        """Build a baseReactant/baseProduct from a known alias layout."""
        alias_id = alias_layout.id_ if alias_layout else ""
        elem = _cd(
            tag,
            attrs={
                "species": _get_species_id(species, ctx),
                "alias": alias_id,
            },
        )
        if reaction_layout is not None and alias_layout is not None:
            ref_point = cls._find_arc_endpoint_for_species(
                ctx, reaction_layout, alias_layout, is_start
            )
            if ref_point is not None:
                anchor = _infer_anchor_position(alias_layout, ref_point)
                if anchor is not None:
                    elem.append(_cd("linkAnchor", attrs={"position": anchor}))
        return elem

    @classmethod
    def _build_base_participant(
        cls, ctx, participant, tag, fset, reaction_layout, is_start
    ):
        """Build a baseReactant or baseProduct element."""
        species = participant.referred_species
        alias_layout = (
            _find_layout_for_species_in_frozenset(ctx, species, fset)
            if fset else None
        )
        alias_id = alias_layout.id_ if alias_layout else ""
        elem = _cd(
            tag,
            attrs={
                "species": _get_species_id(species, ctx),
                "alias": alias_id,
            },
        )
        if reaction_layout is not None and alias_layout is not None:
            ref_point = cls._find_arc_endpoint_for_species(
                ctx, reaction_layout, alias_layout, is_start
            )
            if ref_point is not None:
                anchor = _infer_anchor_position(alias_layout, ref_point)
                if anchor is not None:
                    elem.append(_cd("linkAnchor", attrs={"position": anchor}))
        return elem

    @classmethod
    def _find_arc_endpoint_for_species(cls, ctx, reaction_layout, species_layout, is_start):
        """Find the arc endpoint connecting a species to a reaction.

        Uses the arc's source/target to find the correct arc for this
        species, then returns the endpoint closest to the species.
        """
        arc_cls = (
            momapy.celldesigner.core.ConsumptionLayout
            if is_start
            else momapy.celldesigner.core.ProductionLayout
        )
        # source is always the reaction, target is always the species
        for le in ctx.map_.layout.layout_elements:
            if not isinstance(le, arc_cls):
                continue
            if le.source is reaction_layout and le.target is species_layout:
                return le.points()[0] if is_start else le.points()[-1]
        # Fallback to reaction path start/end
        pts = reaction_layout.points()
        return pts[0] if is_start else pts[-1]

    @classmethod
    def _build_reaction_connect_scheme(
        cls, ctx, ext, reaction, reaction_layout, fset,
        base_reactants, base_products, is_left_t, is_right_t,
    ):
        """Build connectScheme and editPoints for a reaction."""
        writing = _writing
        if reaction_layout is None:
            # No layout — write minimal fallback
            cs = _cd("connectScheme", attrs={
                "connectPolicy": "direct", "rectangleIndex": "0",
            })
            lld = _cd("listOfLineDirection")
            lld.append(_cd("lineDirection", attrs={
                "index": "0", "value": "unknown",
            }))
            cs.append(lld)
            ext.append(cs)
            return
        if is_left_t:
            # Find base reactant layouts and their consumption arcs
            reactant_layouts = []
            consumption_layouts = []
            base_species_set = {r.referred_species for r in base_reactants}
            for br in base_reactants:
                br_layout = _find_layout_for_species_in_frozenset(
                    ctx, br.referred_species, fset
                ) if fset else None
                if br_layout is None:
                    continue
                for le in ctx.map_.layout.layout_elements:
                    if (
                        isinstance(le, momapy.celldesigner.core.ConsumptionLayout)
                        and le.source is reaction_layout
                        and le.target is br_layout
                    ):
                        reactant_layouts.append(br_layout)
                        consumption_layouts.append(le)
                        break
            product_layout = None
            if base_products:
                product_layout = _find_layout_for_species_in_frozenset(
                    ctx, base_products[0].referred_species, fset
                ) if fset else None
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
                        reaction_layout, rl, product_layout, cl,
                    )
                    ep = result[0][-1]
                    origin = rl[0].center()
                    unit_x = rl[1].center()
                    unit_y = product_layout.center()
                    if writing._are_collinear(unit_x, unit_y, origin):
                        origin = momapy.geometry.Point(
                            origin.x + 1, origin.y + 1
                        )
                    trans = momapy.geometry.get_transformation_for_frame(
                        origin, unit_x, unit_y
                    )
                    roundtrip = ep.transformed(trans)
                    dist = (
                        (roundtrip.x - t_junction.x) ** 2
                        + (roundtrip.y - t_junction.y) ** 2
                    )
                    if dist < best_dist:
                        best_dist = dist
                        best_result = result
                (
                    all_edit_points, num0, num1, num2, t_shape_index,
                    product_anchor_name, reactant_anchor_names,
                ) = best_result
                cs = _cd("connectScheme", attrs={"connectPolicy": "direct"})
                lld = _cd("listOfLineDirection")
                for arm_idx, arm_count in enumerate([num0, num1, num2]):
                    for i in range(arm_count + 1):
                        lld.append(_cd("lineDirection", attrs={
                            "arm": str(arm_idx), "index": str(i),
                            "value": "unknown",
                        }))
                cs.append(lld)
                ext.append(cs)
                ep_attrs = {
                    "num0": str(num0), "num1": str(num1),
                    "num2": str(num2),
                    "tShapeIndex": str(t_shape_index),
                }
                ext.append(_cd(
                    "editPoints", attrs=ep_attrs,
                    text=writing.points_to_edit_points_text(
                        all_edit_points
                    ),
                ))
                computed = True
            if not computed:
                # Fallback
                cs = _cd("connectScheme", attrs={"connectPolicy": "direct"})
                lld = _cd("listOfLineDirection")
                for arm in range(3):
                    lld.append(_cd("lineDirection", attrs={
                        "arm": str(arm), "index": "0", "value": "unknown",
                    }))
                cs.append(lld)
                ext.append(cs)
                ext.append(_cd("editPoints", attrs={
                    "num0": "0", "num1": "0", "num2": "0",
                    "tShapeIndex": "0",
                }, text="0.5,0.5"))
        elif is_right_t:
            reactant_layout = None
            if base_reactants:
                reactant_layout = _find_layout_for_species_in_frozenset(
                    ctx, base_reactants[0].referred_species, fset
                ) if fset else None
            product_layouts = []
            production_layouts = []
            for bp in base_products:
                bp_species = bp.referred_species
                bp_layout = _find_layout_for_species_in_frozenset(
                    ctx, bp_species, fset
                ) if fset else None
                if bp_layout is None:
                    continue
                # Find the production arc for this product
                for le in ctx.map_.layout.layout_elements:
                    if (
                        isinstance(le, momapy.celldesigner.core.ProductionLayout)
                        and le.source is reaction_layout
                        and le.target is bp_layout
                    ):
                        product_layouts.append(bp_layout)
                        production_layouts.append(le)
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
                        reaction_layout, reactant_layout, pl, prl,
                    )
                    # Roundtrip: transform T-junction back to absolute
                    ep = result[0][-1]  # last edit point = T-junction in frame
                    origin = reactant_layout.center()
                    unit_x = pl[0].center()
                    unit_y = pl[1].center()
                    if writing._are_collinear(unit_x, unit_y, origin):
                        origin = momapy.geometry.Point(
                            origin.x + 1, origin.y + 1
                        )
                    trans = momapy.geometry.get_transformation_for_frame(
                        origin, unit_x, unit_y
                    )
                    roundtrip = ep.transformed(trans)
                    dist = (
                        (roundtrip.x - t_junction.x) ** 2
                        + (roundtrip.y - t_junction.y) ** 2
                    )
                    if dist < best_dist:
                        best_dist = dist
                        best_result = result
                (
                    all_edit_points, num0, num1, num2, t_shape_index,
                    reactant_anchor_name, product_anchor_names,
                ) = best_result
                cs = _cd("connectScheme", attrs={"connectPolicy": "direct"})
                lld = _cd("listOfLineDirection")
                for arm_idx, arm_count in enumerate([num0, num1, num2]):
                    for i in range(arm_count + 1):
                        lld.append(_cd("lineDirection", attrs={
                            "arm": str(arm_idx), "index": str(i),
                            "value": "unknown",
                        }))
                cs.append(lld)
                ext.append(cs)
                ep_attrs = {
                    "num0": str(num0), "num1": str(num1),
                    "num2": str(num2),
                    "tShapeIndex": str(t_shape_index),
                }
                ext.append(_cd(
                    "editPoints", attrs=ep_attrs,
                    text=writing.points_to_edit_points_text(
                        all_edit_points
                    ),
                ))
                computed = True
            if not computed:
                cs = _cd("connectScheme", attrs={"connectPolicy": "direct"})
                lld = _cd("listOfLineDirection")
                for arm in range(3):
                    lld.append(_cd("lineDirection", attrs={
                        "arm": str(arm), "index": "0", "value": "unknown",
                    }))
                cs.append(lld)
                ext.append(cs)
                ext.append(_cd("editPoints", attrs={
                    "num0": "0", "num1": "0", "num2": "0",
                    "tShapeIndex": "0",
                }, text="0.5,0.5"))
        else:
            # Non-T-shape (1→1)
            # lineDirection count = reactant_arc_segments + product_arc_segments + 1
            reactant_layout = None
            product_layout = None
            consumption_layout = None
            production_layout = None
            if base_reactants:
                reactant_layout = _find_layout_for_species_in_frozenset(
                    ctx, base_reactants[0].referred_species, fset
                ) if fset else None
            if base_products:
                product_layout = _find_layout_for_species_in_frozenset(
                    ctx, base_products[0].referred_species, fset
                ) if fset else None
            if reactant_layout is not None:
                for le in ctx.map_.layout.layout_elements:
                    if (
                        isinstance(le, momapy.celldesigner.core.ConsumptionLayout)
                        and le.source is reaction_layout
                        and le.target is reactant_layout
                    ):
                        consumption_layout = le
                        break
            if product_layout is not None:
                for le in ctx.map_.layout.layout_elements:
                    if (
                        isinstance(le, momapy.celldesigner.core.ProductionLayout)
                        and le.source is reaction_layout
                        and le.target is product_layout
                    ):
                        production_layout = le
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
                        edit_points, reactant_anchor_name,
                        product_anchor_name, rectangle_index,
                    ) = writing.inverse_edit_points_non_t_shape(
                        reaction_layout, reactant_layout, product_layout,
                    )
                    # lineDirection count: n_edit_points + 3
                    n_line_dirs = len(edit_points) + 3
                    cs = _cd("connectScheme", attrs={
                        "connectPolicy": "direct",
                        "rectangleIndex": str(rectangle_index),
                    })
                    lld = _cd("listOfLineDirection")
                    for i in range(n_line_dirs):
                        lld.append(_cd("lineDirection", attrs={
                            "index": str(i), "value": "unknown",
                        }))
                    cs.append(lld)
                    ext.append(cs)
                    if edit_points:
                        ext.append(_cd(
                            "editPoints",
                            text=writing.points_to_edit_points_text(
                                edit_points
                            ),
                        ))
                    computed = True
            if not computed:
                cs = _cd("connectScheme", attrs={
                    "connectPolicy": "direct", "rectangleIndex": "0",
                })
                lld = _cd("listOfLineDirection")
                lld.append(_cd("lineDirection", attrs={
                    "index": "0", "value": "unknown",
                }))
                cs.append(lld)
                ext.append(cs)

    @classmethod
    def _build_participant_link(
        cls, ctx, participant, tag, attr_name, fset, reaction_layout=None,
    ):
        """Build a reactantLink or productLink element."""
        writing = _writing
        species = participant.referred_species
        alias_layout = (
            _find_layout_for_species_in_frozenset(ctx, species, fset)
            if fset else None
        )
        alias_id = alias_layout.id_ if alias_layout else ""
        link = _cd(
            tag,
            attrs={
                attr_name: _get_species_id(species, ctx),
                "alias": alias_id,
            },
        )
        # Compute edit points from arc layout
        edit_points = []
        anchor_name = None
        if reaction_layout is not None and alias_layout is not None:
            is_reactant = tag == "reactantLink"
            arc_cls = (
                momapy.celldesigner.core.ConsumptionLayout
                if is_reactant
                else momapy.celldesigner.core.ProductionLayout
            )
            for le in ctx.map_.layout.layout_elements:
                if (
                    isinstance(le, arc_cls)
                    and le.source is reaction_layout
                    and le.target is alias_layout
                ):
                    if is_reactant:
                        edit_points, anchor_name = (
                            writing.inverse_edit_points_reactant_link(
                                le, alias_layout, reaction_layout,
                            )
                        )
                    else:
                        edit_points, anchor_name = (
                            writing.inverse_edit_points_product_link(
                                le, alias_layout, reaction_layout,
                            )
                        )
                    break
        if anchor_name is not None:
            anchor_pos = _anchor_name_to_position(anchor_name)
            if anchor_pos is not None:
                link.append(_cd("linkAnchor", attrs={
                    "position": anchor_pos,
                }))
        cs = _cd("connectScheme", attrs={"connectPolicy": "direct"})
        lld = _cd("listOfLineDirection")
        for i in range(len(edit_points) + 1):
            lld.append(
                _cd("lineDirection", attrs={"index": str(i), "value": "unknown"})
            )
        cs.append(lld)
        link.append(cs)
        if edit_points:
            link.append(_cd(
                "editPoints",
                text=writing.points_to_edit_points_text(edit_points),
            ))
        link.append(_cd("line", attrs={"width": "1.0", "color": "ff000000", "type": "Straight"}))
        return link

    @classmethod
    def _build_reaction_modification(cls, ctx, modifier, reaction_layout, fset):
        """Build a CD modification element for a reaction modifier."""
        writing = _writing
        species = modifier.referred_species
        if isinstance(species, momapy.celldesigner.core.BooleanLogicGate):
            return None
        alias_layout = (
            _find_layout_for_species_in_frozenset(ctx, species, fset)
            if fset
            else None
        )
        alias_id = alias_layout.id_ if alias_layout else ""
        mod_type = _CLASS_TO_MODIFIER_TYPE.get(type(modifier), "CATALYSIS")
        # Find modifier arc layout and compute edit points
        edit_points = []
        source_anchor_name = None
        modifier_arc = None
        if reaction_layout is not None and alias_layout is not None:
            for le in ctx.map_.layout.layout_elements:
                if (
                    hasattr(le, "source") and hasattr(le, "target")
                    and le.source is alias_layout
                    and le.target is reaction_layout
                ):
                    modifier_arc = le
                    edit_points, source_anchor_name = (
                        writing.inverse_edit_points_modifier(
                            le, alias_layout, reaction_layout,
                            has_boolean_input=False,
                        )
                    )
                    break
        target_line_index = "-1,2"
        if modifier_arc is not None and reaction_layout is not None:
            target_line_index = _compute_target_line_index(
                reaction_layout, modifier_arc
            )
        attrs = {
            "type": mod_type,
            "modifiers": _get_species_id(species, ctx),
            "aliases": alias_id,
            "targetLineIndex": target_line_index,
        }
        if edit_points:
            attrs["editPoints"] = writing.points_to_edit_points_text(
                edit_points
            )
        mod_elem = _cd("modification", attrs=attrs)
        # connectScheme
        cs = _cd("connectScheme", attrs={"connectPolicy": "direct"})
        lld = _cd("listOfLineDirection")
        for i in range(len(edit_points) + 1):
            lld.append(
                _cd("lineDirection", attrs={"index": str(i), "value": "unknown"})
            )
        cs.append(lld)
        mod_elem.append(cs)
        # linkTarget
        lt_attrs = {
            "species": _get_species_id(species, ctx),
            "alias": alias_id,
        }
        lt = _cd("linkTarget", attrs=lt_attrs)
        if source_anchor_name is not None:
            anchor_pos = _anchor_name_to_position(source_anchor_name)
            if anchor_pos is not None:
                lt.append(_cd("linkAnchor", attrs={"position": anchor_pos}))
        mod_elem.append(lt)
        # line
        mod_elem.append(
            _cd("line", attrs={"width": "1.0", "color": "ff000000", "type": "Straight"})
        )
        return mod_elem

    @classmethod
    def _build_boolean_gate_modifications(cls, ctx, modifier, gate, reaction_layout, fset):
        """Build CD modification entries for a boolean logic gate modifier.

        Returns a list of modification elements: first the gate entry,
        then one per input species.
        """
        result = []
        mod_type = _CLASS_TO_MODIFIER_TYPE.get(type(modifier), "CATALYSIS")
        gate_type_map = {
            momapy.celldesigner.core.AndGate: "BOOLEAN_LOGIC_GATE_AND",
            momapy.celldesigner.core.OrGate: "BOOLEAN_LOGIC_GATE_OR",
            momapy.celldesigner.core.NotGate: "BOOLEAN_LOGIC_GATE_NOT",
            momapy.celldesigner.core.UnknownGate: "BOOLEAN_LOGIC_GATE_UNKNOWN",
        }
        gate_type = gate_type_map.get(type(gate), "BOOLEAN_LOGIC_GATE_AND")

        # Collect input aliases — gate inputs are NOT in the reaction
        # frozenset, so look them up globally via the mapping.
        input_species_ids = []
        input_alias_ids = []
        for inp in sorted(gate.inputs, key=lambda s: s.id_):
            sbml_inp = ctx.subunit_to_complex.get(inp, inp)
            input_species_ids.append(_get_species_id(sbml_inp, ctx))
            # Try frozenset first, then global
            alias_layout = (
                _find_layout_for_species_in_frozenset(ctx, inp, fset)
                if fset else None
            )
            if alias_layout is None:
                for lk in _get_layouts(ctx, inp):
                    if isinstance(lk, frozenset):
                        continue
                    if isinstance(lk, momapy.celldesigner.core.CellDesignerNode):
                        alias_layout = lk
                        break
            input_alias_ids.append(alias_layout.id_ if alias_layout else "")

        # Gate entry — editPoints is the gate layout position.
        # The gate layout is in the reaction's frozenset, not directly mapped.
        gate_layout = None
        if fset is not None:
            for elem in fset:
                if isinstance(
                    elem,
                    (
                        momapy.celldesigner.core.AndGateLayout,
                        momapy.celldesigner.core.OrGateLayout,
                        momapy.celldesigner.core.NotGateLayout,
                        momapy.celldesigner.core.UnknownGateLayout,
                    ),
                ):
                    gate_layout = elem
                    break
        gate_edit_points = ""
        if gate_layout is not None:
            pos = gate_layout.position
            gate_edit_points = f"{pos.x},{pos.y}"
        gate_attrs = {
            "type": gate_type,
            "modificationType": mod_type,
            "modifiers": ",".join(input_species_ids),
            "aliases": ",".join(input_alias_ids),
            "targetLineIndex": "-1,2",
        }
        if gate_edit_points:
            gate_attrs["editPoints"] = gate_edit_points
        gate_mod = _cd("modification", attrs=gate_attrs)
        gate_cs = _cd("connectScheme", attrs={"connectPolicy": "direct"})
        gate_lld = _cd("listOfLineDirection")
        gate_lld.append(
            _cd("lineDirection", attrs={"index": "0", "value": "unknown"})
        )
        gate_cs.append(gate_lld)
        gate_mod.append(gate_cs)
        gate_mod.append(
            _cd("line", attrs={"width": "1.0", "color": "ff000000", "type": "Straight"})
        )
        result.append(gate_mod)

        # Per-input entries
        for i, inp in enumerate(sorted(gate.inputs, key=lambda s: s.id_)):
            sbml_inp = ctx.subunit_to_complex.get(inp, inp)
            inp_attrs = {
                "type": mod_type,
                "modifiers": _get_species_id(sbml_inp, ctx),
                "aliases": input_alias_ids[i],
                "targetLineIndex": "-1,2",
            }
            inp_mod = _cd("modification", attrs=inp_attrs)
            cs = _cd("connectScheme", attrs={"connectPolicy": "direct"})
            lld = _cd("listOfLineDirection")
            lld.append(
                _cd("lineDirection", attrs={"index": "0", "value": "unknown"})
            )
            cs.append(lld)
            inp_mod.append(cs)
            # linkTarget
            lt = _cd(
                "linkTarget",
                attrs={
                    "species": _get_species_id(sbml_inp, ctx),
                    "alias": input_alias_ids[i],
                },
            )
            inp_mod.append(lt)
            inp_mod.append(
                _cd("line", attrs={"width": "1.0", "color": "ff000000", "type": "Straight"})
            )
            result.append(inp_mod)

        return result

    @classmethod
    def _build_modulation_as_reaction(cls, ctx, modulation):
        """Build a modulation as a fake SBML reaction."""
        source = modulation.source
        target = modulation.target

        if isinstance(source, momapy.celldesigner.core.BooleanLogicGate):
            return cls._build_gate_modulation_as_reaction(ctx, modulation)

        attrs = {
            "metaid": modulation.id_,
            "id": modulation.id_,
            "reversible": "false",
        }
        rxn = _el("reaction", attrs=attrs)

        # Find layout via mapping — modulation layout may be in a frozenset
        modulation_layout = None
        source_layout = None
        target_layout = None
        fset = None
        for layout_key in _get_layouts(ctx, modulation):
            if isinstance(layout_key, frozenset):
                fset = layout_key
                for elem in layout_key:
                    model = _mapping(ctx).get_mapping(elem)
                    if model is modulation:
                        modulation_layout = elem
                    elif model is source:
                        source_layout = elem
                    elif model is target:
                        target_layout = elem
                    elif isinstance(model, tuple):
                        if model[0] is source:
                            source_layout = elem
                        elif model[0] is target:
                            target_layout = elem
            else:
                modulation_layout = layout_key

        if source_layout is None and source is not None:
            for layout_key in _get_layouts(ctx, source):
                if isinstance(layout_key, frozenset):
                    continue
                if isinstance(layout_key, momapy.celldesigner.core.CellDesignerNode):
                    source_layout = layout_key
                    break

        if target_layout is None and target is not None:
            for layout_key in _get_layouts(ctx, target):
                if isinstance(layout_key, frozenset):
                    continue
                if isinstance(layout_key, momapy.celldesigner.core.CellDesignerNode):
                    target_layout = layout_key
                    break

        source_alias = source_layout.id_ if source_layout else ""
        target_alias = target_layout.id_ if target_layout else ""
        source_id = _get_species_id(source, ctx) if source else ""
        target_id = _get_species_id(target, ctx) if target else ""

        # CD extension
        ann = _el("annotation")
        ext = _cd("extension")
        reaction_type = _modulation_reaction_type(modulation)
        ext.append(_cd("reactionType", text=reaction_type))

        # Compute edit points for the modulation
        writing = _writing
        edit_points = []
        source_anchor_name = None
        target_anchor_name = None
        if modulation_layout is not None and source_layout is not None and target_layout is not None:
            edit_points, source_anchor_name, target_anchor_name = (
                writing.inverse_edit_points_modulation(
                    modulation_layout, source_layout, target_layout,
                    has_boolean_input=False,
                )
            )

        # baseReactants (source)
        br_elem = _cd("baseReactants")
        br = _cd("baseReactant", attrs={"species": source_id, "alias": source_alias})
        if source_anchor_name is not None:
            anchor_pos = _anchor_name_to_position(source_anchor_name)
            if anchor_pos is not None:
                br.append(_cd("linkAnchor", attrs={"position": anchor_pos}))
        br_elem.append(br)
        ext.append(br_elem)

        # baseProducts (target)
        bp_elem = _cd("baseProducts")
        bp = _cd("baseProduct", attrs={"species": target_id, "alias": target_alias})
        if target_anchor_name is not None:
            anchor_pos = _anchor_name_to_position(target_anchor_name)
            if anchor_pos is not None:
                bp.append(_cd("linkAnchor", attrs={"position": anchor_pos}))
        bp_elem.append(bp)
        ext.append(bp_elem)

        ext.append(_cd("listOfReactantLinks"))
        ext.append(_cd("listOfProductLinks"))

        # connectScheme — for modulations-as-reactions:
        # ld = n_edit_points + 3, rectangleIndex = n_edit_points
        n_ep = len(edit_points)
        cs = _cd("connectScheme", attrs={
            "connectPolicy": "direct",
            "rectangleIndex": str(n_ep),
        })
        lld = _cd("listOfLineDirection")
        for i in range(n_ep + 3):
            lld.append(_cd("lineDirection", attrs={
                "index": str(i), "value": "unknown",
            }))
        cs.append(lld)
        ext.append(cs)

        if edit_points:
            ext.append(_cd(
                "editPoints",
                text=writing.points_to_edit_points_text(edit_points),
            ))

        ext.append(_cd("listOfModification"))
        ext.append(_cd("line", attrs={"width": "1.0", "color": "ff000000", "type": "Straight"}))

        ann.append(ext)
        rxn.append(ann)

        # SBML listOfReactants (use complex ID for subunits)
        sbml_source = ctx.subunit_to_complex.get(source, source) if source else source
        lor = _el("listOfReactants")
        sr = _el("speciesReference", attrs={"species": _get_species_id(sbml_source, ctx) if sbml_source else ""})
        sr_ann = _el("annotation")
        sr_ext = _cd("extension")
        sr_ext.append(_cd("alias", text=source_alias))
        sr_ann.append(sr_ext)
        sr.append(sr_ann)
        lor.append(sr)
        rxn.append(lor)

        # SBML listOfProducts (use complex ID for subunits)
        sbml_target = ctx.subunit_to_complex.get(target, target) if target else target
        lop = _el("listOfProducts")
        pr = _el("speciesReference", attrs={"species": _get_species_id(sbml_target, ctx) if sbml_target else ""})
        pr_ann = _el("annotation")
        pr_ext = _cd("extension")
        pr_ext.append(_cd("alias", text=target_alias))
        pr_ann.append(pr_ext)
        pr.append(pr_ann)
        lop.append(pr)
        rxn.append(lop)

        return rxn

    @classmethod
    def _build_gate_modulation_as_reaction(cls, ctx, modulation):
        """Build a boolean gate modulation as a fake SBML reaction.

        Structure: reactionType=BOOLEAN_LOGIC_GATE, baseReactants=gate inputs,
        baseProducts=target, listOfGateMember for gate+per-input entries.
        """
        gate = modulation.source
        target = modulation.target

        gate_type_map = {
            momapy.celldesigner.core.AndGate: "BOOLEAN_LOGIC_GATE_AND",
            momapy.celldesigner.core.OrGate: "BOOLEAN_LOGIC_GATE_OR",
            momapy.celldesigner.core.NotGate: "BOOLEAN_LOGIC_GATE_NOT",
            momapy.celldesigner.core.UnknownGate: "BOOLEAN_LOGIC_GATE_UNKNOWN",
        }
        gate_type = gate_type_map.get(type(gate), "BOOLEAN_LOGIC_GATE_AND")

        # Determine the modification type from the modulation type
        mod_type = _modulation_reaction_type(modulation)

        attrs = {
            "metaid": modulation.id_,
            "id": modulation.id_,
            "reversible": "false",
        }
        rxn = _el("reaction", attrs=attrs)

        # Find the gate layout
        gate_layout = None
        for le in ctx.map_.layout.layout_elements:
            if isinstance(le, (
                momapy.celldesigner.core.AndGateLayout,
                momapy.celldesigner.core.OrGateLayout,
                momapy.celldesigner.core.NotGateLayout,
                momapy.celldesigner.core.UnknownGateLayout,
            )):
                gate_model = _mapping(ctx).get_mapping(le)
                if gate_model is gate:
                    gate_layout = le
                    break

        # Find inputs via logic arcs (preserves duplicates unlike gate.inputs)
        input_layouts = []
        if gate_layout is not None:
            for le in ctx.map_.layout.layout_elements:
                if (
                    hasattr(le, "source") and hasattr(le, "target")
                    and le.source is gate_layout
                ):
                    inp_layout = le.target
                    model_info = _mapping(ctx).get_mapping(inp_layout)
                    inp_model = (
                        model_info[0]
                        if isinstance(model_info, tuple)
                        else model_info
                    ) if model_info is not None else None
                    if inp_model is not None:
                        input_layouts.append((inp_model, inp_layout))
        if not input_layouts:
            # Fallback to gate.inputs if no logic arcs found
            for inp in sorted(gate.inputs, key=lambda s: s.id_):
                inp_layout = None
                for lk in _get_layouts(ctx, inp):
                    if isinstance(lk, frozenset):
                        continue
                    if isinstance(lk, momapy.celldesigner.core.CellDesignerNode):
                        inp_layout = lk
                        break
                input_layouts.append((inp, inp_layout))

        target_layout = None
        if target is not None:
            for lk in _get_layouts(ctx, target):
                if isinstance(lk, frozenset):
                    continue
                if isinstance(lk, momapy.celldesigner.core.CellDesignerNode):
                    target_layout = lk
                    break

        gate_edit_points = ""
        if gate_layout is not None:
            gate_edit_points = f"{gate_layout.position.x},{gate_layout.position.y}"

        target_alias = target_layout.id_ if target_layout else ""
        target_id = _get_species_id(target, ctx) if target else ""

        # CD extension
        ann = _el("annotation")
        ext = _cd("extension")
        ext.append(_cd("reactionType", text="BOOLEAN_LOGIC_GATE"))

        # baseReactants (gate inputs)
        br_elem = _cd("baseReactants")
        for inp, inp_layout in input_layouts:
            sbml_inp = ctx.subunit_to_complex.get(inp, inp)
            alias_id = inp_layout.id_ if inp_layout else ""
            br = _cd("baseReactant", attrs={
                "species": _get_species_id(sbml_inp, ctx),
                "alias": alias_id,
            })
            # Try to find linkAnchor from logic arcs
            if gate_layout is not None and inp_layout is not None:
                for le in ctx.map_.layout.layout_elements:
                    if (hasattr(le, "source") and hasattr(le, "target")
                            and le.source is gate_layout
                            and le.target is inp_layout):
                        endpoint = le.points()[-1]
                        anchor = _infer_anchor_position(inp_layout, endpoint)
                        if anchor is not None:
                            br.append(_cd("linkAnchor", attrs={"position": anchor}))
                        break
            br_elem.append(br)
        ext.append(br_elem)

        # baseProducts (target)
        bp_elem = _cd("baseProducts")
        sbml_target = ctx.subunit_to_complex.get(target, target) if target else target
        bp = _cd("baseProduct", attrs={
            "species": _get_species_id(sbml_target, ctx) if sbml_target else "",
            "alias": target_alias,
        })
        bp_elem.append(bp)
        ext.append(bp_elem)

        ext.append(_cd("listOfReactantLinks"))
        ext.append(_cd("listOfProductLinks"))

        # Compute editPoints: intermediate points from modulation layout + gate position
        writing = _writing
        modulation_layout = None
        for lk in _get_layouts(ctx, modulation):
            if isinstance(lk, frozenset):
                for elem in lk:
                    model = _mapping(ctx).get_mapping(elem)
                    if model is modulation:
                        modulation_layout = elem
                        break
            elif not isinstance(lk, frozenset):
                modulation_layout = lk

        ep_parts = []
        if gate_layout is not None and modulation_layout is not None and target_layout is not None:
            mod_edit_points, _, _ = writing.inverse_edit_points_modulation(
                modulation_layout,
                gate_layout,
                target_layout,
                has_boolean_input=True,
            )
            ep_parts.extend(
                f"{p.x},{p.y}" for p in mod_edit_points
            )
        if gate_edit_points:
            ep_parts.append(gate_edit_points)
        ep_text = " ".join(ep_parts)
        n_ep = len(ep_parts)

        # connectScheme — gate modulations use rectangleIndex=1
        # and lineDirection count = len(inputs) + 3
        n_ld = len(input_layouts) + 3
        cs = _cd("connectScheme", attrs={
            "connectPolicy": "direct",
            "rectangleIndex": "1",
        })
        lld = _cd("listOfLineDirection")
        for i in range(n_ld):
            lld.append(_cd("lineDirection", attrs={
                "index": str(i), "value": "unknown",
            }))
        cs.append(lld)
        ext.append(cs)

        # editPoints
        if ep_text:
            ext.append(_cd("editPoints", text=ep_text))

        ext.append(_cd("listOfModification"))

        # listOfGateMember
        gm_list = _cd("listOfGateMember")
        input_alias_ids = [il.id_ if il else "" for _, il in input_layouts]
        # Gate entry
        gate_attrs = {
            "type": gate_type,
            "aliases": ",".join(input_alias_ids),
            "modificationType": mod_type,
        }
        if gate_edit_points:
            gate_attrs["editPoints"] = gate_edit_points
        gate_member = _cd("GateMember", attrs=gate_attrs)
        gm_cs = _cd("connectScheme", attrs={"connectPolicy": "direct"})
        gm_lld = _cd("listOfLineDirection")
        gm_lld.append(_cd("lineDirection", attrs={
            "index": "0", "value": "unknown",
        }))
        gm_cs.append(gm_lld)
        gate_member.append(gm_cs)
        gate_member.append(_cd("line", attrs={
            "width": "1.0", "color": "FF000000", "type": "Straight",
        }))
        gm_list.append(gate_member)

        # Per-input entries
        for inp, inp_layout in input_layouts:
            sbml_inp = ctx.subunit_to_complex.get(inp, inp)
            alias_id = inp_layout.id_ if inp_layout else ""
            inp_member = _cd("GateMember", attrs={
                "type": mod_type,
                "aliases": alias_id,
            })
            inp_cs = _cd("connectScheme", attrs={"connectPolicy": "direct"})
            inp_lld = _cd("listOfLineDirection")
            inp_lld.append(_cd("lineDirection", attrs={
                "index": "0", "value": "unknown",
            }))
            inp_cs.append(inp_lld)
            inp_member.append(inp_cs)
            lt = _cd("linkTarget", attrs={
                "species": _get_species_id(sbml_inp, ctx),
                "alias": alias_id,
            })
            if gate_layout is not None and inp_layout is not None:
                for le in ctx.map_.layout.layout_elements:
                    if (hasattr(le, "source") and hasattr(le, "target")
                            and le.source is gate_layout
                            and le.target is inp_layout):
                        endpoint = le.points()[-1]
                        anchor = _infer_anchor_position(inp_layout, endpoint)
                        if anchor is not None:
                            lt.append(_cd("linkAnchor", attrs={"position": anchor}))
                        break
            inp_member.append(lt)
            inp_member.append(_cd("line", attrs={
                "width": "1.0", "color": "FF000000", "type": "Straight",
            }))
            gm_list.append(inp_member)

        ext.append(gm_list)
        ext.append(_cd("line", attrs={"width": "1.0", "color": "ff000000", "type": "Straight"}))

        ann.append(ext)
        rxn.append(ann)

        # SBML listOfReactants (gate inputs)
        lor = _el("listOfReactants")
        for inp, inp_layout in input_layouts:
            sbml_inp = ctx.subunit_to_complex.get(inp, inp)
            alias_id = inp_layout.id_ if inp_layout else ""
            sr = _el("speciesReference", attrs={
                "species": _get_species_id(sbml_inp, ctx),
            })
            sr_ann = _el("annotation")
            sr_ext = _cd("extension")
            sr_ext.append(_cd("alias", text=alias_id))
            sr_ann.append(sr_ext)
            sr.append(sr_ann)
            lor.append(sr)
        rxn.append(lor)

        # SBML listOfProducts (target)
        lop = _el("listOfProducts")
        pr = _el("speciesReference", attrs={
            "species": _get_species_id(sbml_target, ctx) if sbml_target else "",
        })
        pr_ann = _el("annotation")
        pr_ext = _cd("extension")
        pr_ext.append(_cd("alias", text=target_alias))
        pr_ann.append(pr_ext)
        pr.append(pr_ann)
        lop.append(pr)
        rxn.append(lop)

        return rxn
