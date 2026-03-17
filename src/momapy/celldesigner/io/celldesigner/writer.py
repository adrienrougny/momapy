"""CellDesigner XML writer class."""

import dataclasses
import typing

import lxml.etree

import momapy.coloring
import momapy.drawing
import momapy.geometry
import momapy.io.core
import momapy.builder
import momapy.celldesigner.core
import momapy.sbml.core
import momapy.sbml.io.sbml._qualifiers
import momapy.core.layout

import momapy.celldesigner.io.celldesigner._writing
import momapy.celldesigner.io.celldesigner._layout


_CD_NS = momapy.celldesigner.io.celldesigner._writing._CD_NAMESPACE
_SBML_NS = "http://www.sbml.org/sbml/level2/version4"
_RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
_BQBIOL_NS = "http://biomodels.net/biology-qualifiers/"
_BQMODEL_NS = "http://biomodels.net/model-qualifiers/"
_XHTML_NS = "http://www.w3.org/1999/xhtml"
_DC_NS = "http://purl.org/dc/elements/1.1/"
_DCTERMS_NS = "http://purl.org/dc/terms/"
_VCARD_NS = "http://www.w3.org/2001/vcard-rdf/3.0#"

_NSMAP = {
    None: _SBML_NS,
    "celldesigner": _CD_NS,
}

_RDF_NSMAP = {
    "rdf": _RDF_NS,
    "dc": _DC_NS,
    "dcterms": _DCTERMS_NS,
    "vCard": _VCARD_NS,
    "bqbiol": _BQBIOL_NS,
    "bqmodel": _BQMODEL_NS,
}

_make = momapy.celldesigner.io.celldesigner._writing.make_cd_element
_writing = momapy.celldesigner.io.celldesigner._writing
_sid = momapy.celldesigner.io.celldesigner._writing.ensure_sbml_sid
_xmlid = momapy.celldesigner.io.celldesigner._writing.ensure_xml_id


@dataclasses.dataclass
class WritingContext:
    """Bundles the shared state passed across all writer methods."""

    map_: typing.Any
    annotations: dict
    notes: dict
    ids: dict
    with_annotations: bool
    with_notes: bool
    model_element_to_layout_elements: dict
    layout_to_model: dict
    layout_element_to_id: dict
    used_metaids: set = dataclasses.field(default_factory=set)


def _build_reverse_lookups(map_):
    """Build model->layout and layout->model reverse lookup dicts.

    Args:
        map_: A CellDesignerMap instance.

    Returns:
        Tuple of (model_element_to_layout_elements, layout_to_model,
        layout_element_to_id).
    """
    model_to_layouts = {}
    layout_to_model = {}
    layout_element_to_id = {}
    if map_.layout_model_mapping is not None:
        # First pass: direct (non-frozenset) mappings take priority
        for key, value in map_.layout_model_mapping.items():
            if not isinstance(key, frozenset):
                layout_to_model[key] = value
            model_elem = value
            if isinstance(model_elem, tuple):
                model_elem = model_elem[0]
            model_to_layouts.setdefault(model_elem, []).append(key)
        # Second pass: frozenset mappings, only if not already mapped
        for key, value in map_.layout_model_mapping.items():
            if isinstance(key, frozenset):
                for layout_elem in key:
                    if layout_elem not in layout_to_model:
                        layout_to_model[layout_elem] = value
    return model_to_layouts, layout_to_model, layout_element_to_id


def _unique_metaid(ctx, metaid):
    """Return a unique metaid, appending a numeric suffix if needed.

    Args:
        ctx: The WritingContext.
        metaid: The candidate metaid string (already XML-ID-sanitized).

    Returns:
        A unique metaid string.
    """
    candidate = metaid
    counter = 1
    while candidate in ctx.used_metaids:
        candidate = f"{metaid}_{counter}"
        counter += 1
    ctx.used_metaids.add(candidate)
    return candidate


class CellDesignerWriter(momapy.io.core.Writer):
    """Class for CellDesigner writer objects."""

    # Reverse mappings built from CellDesignerReader._KEY_TO_CLASS
    # We import it lazily to avoid circular imports
    _CLASS_TO_KEY = None

    @classmethod
    def _ensure_class_to_key(cls):
        if cls._CLASS_TO_KEY is not None:
            return
        import momapy.celldesigner.io.celldesigner.reader

        cls._CLASS_TO_KEY = {}
        for (
            key,
            value,
        ) in momapy.celldesigner.io.celldesigner.reader.CellDesignerReader._KEY_TO_CLASS.items():
            if isinstance(value, tuple):
                model_cls, layout_cls = value
                cls._CLASS_TO_KEY[model_cls] = key
            else:
                cls._CLASS_TO_KEY[value] = key

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
    ):
        """Write a CellDesignerMap to an XML file.

        Args:
            obj: A CellDesignerMap instance.
            file_path: Output file path.
            annotations: Optional dict mapping model elements to annotations.
            notes: Optional dict mapping model elements to notes.
            ids: Optional dict mapping elements to custom IDs.
            with_annotations: Whether to write annotations.
            with_notes: Whether to write notes.

        Returns:
            WriterResult instance.
        """
        cls._ensure_class_to_key()
        if annotations is None:
            annotations = {}
        if notes is None:
            notes = {}
        if ids is None:
            ids = {}
        model_to_layouts, layout_to_model, layout_element_to_id = (
            _build_reverse_lookups(obj)
        )
        ctx = WritingContext(
            map_=obj,
            annotations=annotations,
            notes=notes,
            ids=ids,
            with_annotations=with_annotations,
            with_notes=with_notes,
            model_element_to_layout_elements=model_to_layouts,
            layout_to_model=layout_to_model,
            layout_element_to_id=layout_element_to_id,
        )
        sbml = cls._make_sbml(ctx)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(
                lxml.etree.tostring(
                    sbml,
                    pretty_print=True,
                    xml_declaration=True,
                    encoding="UTF-8",
                ).decode("utf-8")
            )
        return momapy.io.core.WriterResult(obj=obj, file_path=file_path)

    @classmethod
    def _make_sbml(cls, ctx):
        sbml = lxml.etree.Element("sbml", nsmap=_NSMAP)
        sbml.set("level", "2")
        sbml.set("version", "4")
        model = cls._make_model(ctx)
        sbml.append(model)
        return sbml

    @classmethod
    def _make_model(cls, ctx):
        model_id = ctx.map_.model.id_ if ctx.map_.model is not None else "model"
        model_attrs = {}
        if model_id is not None:
            model_attrs["id"] = _sid(model_id)
        if ctx.map_.model is not None and ctx.map_.model.metaid is not None:
            model_attrs["metaid"] = _unique_metaid(ctx, _xmlid(ctx.map_.model.metaid))
        model_elem = lxml.etree.SubElement(
            lxml.etree.Element("dummy"), "model", **model_attrs
        )
        model_elem = _make("model", attributes=model_attrs)
        # notes
        if ctx.with_notes:
            notes_elem = cls._make_notes_for_element(ctx, ctx.map_)
            if notes_elem is not None:
                model_elem.append(notes_elem)
        # annotation containing extension + rdf
        annotation = _make("annotation")
        extension = cls._make_extension(ctx)
        annotation.append(extension)
        if ctx.with_annotations:
            rdf = cls._make_rdf_for_element(ctx, ctx.map_)
            if rdf is not None:
                annotation.append(rdf)
        model_elem.append(annotation)
        # listOfCompartments
        compartments_elem = cls._make_list_of_compartments(ctx)
        if compartments_elem is not None:
            model_elem.append(compartments_elem)
        # listOfSpecies
        species_elem = cls._make_list_of_species(ctx)
        if species_elem is not None:
            model_elem.append(species_elem)
        # listOfReactions
        reactions_elem = cls._make_list_of_reactions(ctx)
        if reactions_elem is not None:
            model_elem.append(reactions_elem)
        return model_elem

    @classmethod
    def _make_extension(cls, ctx):
        ext = _make("extension", ns=_CD_NS)
        # modelVersion
        version = _make("modelVersion", ns=_CD_NS, text="4.0")
        ext.append(version)
        # modelDisplay
        display_attrs = {}
        if ctx.map_.layout is not None:
            display_attrs["sizeX"] = str(int(ctx.map_.layout.width))
            display_attrs["sizeY"] = str(int(ctx.map_.layout.height))
        display = _make("modelDisplay", ns=_CD_NS, attributes=display_attrs)
        ext.append(display)
        # listOfIncludedSpecies
        included = cls._make_list_of_included_species(ctx)
        if included is not None:
            ext.append(included)
        # listOfCompartmentAliases
        comp_aliases = cls._make_list_of_compartment_aliases(ctx)
        ext.append(comp_aliases)
        # listOfComplexSpeciesAliases
        complex_aliases = cls._make_list_of_complex_species_aliases(ctx)
        ext.append(complex_aliases)
        # listOfSpeciesAliases
        species_aliases = cls._make_list_of_species_aliases(ctx)
        ext.append(species_aliases)
        # listOfProteins, listOfGenes, listOfRNAs, listOfAntisenseRNAs
        for list_tag, template_cls, item_tag in [
            ("listOfProteins", momapy.celldesigner.core.ProteinTemplate, "protein"),
            ("listOfGenes", momapy.celldesigner.core.GeneTemplate, "gene"),
            ("listOfRNAs", momapy.celldesigner.core.RNATemplate, "RNA"),
            (
                "listOfAntisenseRNAs",
                momapy.celldesigner.core.AntisenseRNATemplate,
                "AntisenseRNA",
            ),
        ]:
            list_elem = cls._make_list_of_templates(
                ctx, list_tag, template_cls, item_tag
            )
            ext.append(list_elem)
        ext.append(_make("listOfLayers", ns=_CD_NS))
        return ext

    @classmethod
    def _make_list_of_templates(cls, ctx, list_tag, template_cls, item_tag):
        list_elem = _make(list_tag, ns=_CD_NS)
        if ctx.map_.model is not None:
            for template in sorted(
                ctx.map_.model.species_templates,
                key=lambda t: t.id_ or "",
            ):
                if isinstance(template, template_cls):
                    item = cls._make_species_template(ctx, template, item_tag)
                    list_elem.append(item)
        return list_elem

    @classmethod
    def _make_species_template(cls, ctx, template, item_tag):
        key = cls._CLASS_TO_KEY.get(type(template))
        template_type = key[1] if key is not None else "GENERIC"
        attrs = {
            "id": _sid(template.id_),
            "name": _writing.encode_name(template.name),
            "type": template_type,
        }
        item = _make(item_tag, ns=_CD_NS, attributes=attrs)
        # modification residues
        if (
            hasattr(template, "modification_residues")
            and template.modification_residues
        ):
            mod_list = _make("listOfModificationResidues", ns=_CD_NS)
            sorted_residues = sorted(
                template.modification_residues, key=lambda r: r.id_ or ""
            )
            for residue in sorted_residues:
                # residue.id_ is "templateId_residueId"
                parts = residue.id_.split("_", 1)
                residue_xml_id = parts[1] if len(parts) > 1 else residue.id_
                mod_attrs = {"id": _sid(residue_xml_id)}
                if residue.name is not None:
                    mod_attrs["name"] = residue.name
                # Compute angle from layout if possible
                angle = cls._find_modification_angle(ctx, residue, template)
                if angle is not None:
                    mod_attrs["angle"] = str(angle)
                mod_elem = _make("modificationResidue", ns=_CD_NS, attributes=mod_attrs)
                mod_list.append(mod_elem)
            item.append(mod_list)
        # regions
        if hasattr(template, "regions") and template.regions:
            region_list = _make("listOfRegions", ns=_CD_NS)
            for region in sorted(template.regions, key=lambda r: r.id_ or ""):
                parts = region.id_.split("_", 1)
                region_xml_id = parts[1] if len(parts) > 1 else region.id_
                region_key = cls._CLASS_TO_KEY.get(type(region))
                region_type = (
                    region_key[1] if region_key is not None else "Modification Site"
                )
                region_attrs = {
                    "id": _sid(region_xml_id),
                    "type": region_type,
                }
                if region.name is not None:
                    region_attrs["name"] = region.name
                if region.active:
                    region_attrs["active"] = "true"
                region_elem = _make("region", ns=_CD_NS, attributes=region_attrs)
                region_list.append(region_elem)
            item.append(region_list)
        return item

    @classmethod
    def _make_list_of_compartment_aliases(cls, ctx):
        list_elem = _make("listOfCompartmentAliases", ns=_CD_NS)
        if ctx.map_.layout is not None:
            for layout_element in ctx.map_.layout.layout_elements:
                if isinstance(
                    layout_element,
                    (
                        momapy.celldesigner.core.OvalCompartmentLayout,
                        momapy.celldesigner.core.RectangleCompartmentLayout,
                    ),
                ):
                    alias = cls._make_compartment_alias(ctx, layout_element)
                    list_elem.append(alias)
        return list_elem

    @classmethod
    def _make_compartment_alias(cls, ctx, layout_element):
        model_element = cls._get_model_element(ctx, layout_element)
        compartment_id = _sid(model_element.id_) if model_element is not None else ""
        attrs = {
            "id": _sid(layout_element.id_),
            "compartment": compartment_id,
        }
        alias = _make("compartmentAlias", ns=_CD_NS, attributes=attrs)
        # class
        if isinstance(layout_element, momapy.celldesigner.core.OvalCompartmentLayout):
            cls_text = "OVAL"
        else:
            cls_text = "SQUARE"
        class_elem = _make("class", ns=_CD_NS, text=cls_text)
        alias.append(class_elem)
        # bounds
        bounds = _make(
            "bounds",
            ns=_CD_NS,
            attributes=_writing.node_to_bounds_attrs(layout_element),
        )
        alias.append(bounds)
        # namePoint
        if layout_element.label is not None:
            name_point = _make(
                "namePoint",
                ns=_CD_NS,
                attributes={
                    "x": str(layout_element.label.position.x),
                    "y": str(layout_element.label.position.y),
                },
            )
            alias.append(name_point)
        # doubleLine
        double_line = _make(
            "doubleLine",
            ns=_CD_NS,
            attributes={
                "thickness": str(layout_element.sep),
                "outerWidth": str(layout_element.stroke_width),
                "innerWidth": str(layout_element.inner_stroke_width),
            },
        )
        alias.append(double_line)
        # paint
        stroke_color = layout_element.stroke
        if stroke_color is not None and not stroke_color is momapy.drawing.NoneValue:
            paint = _make(
                "paint",
                ns=_CD_NS,
                attributes={
                    "color": _writing.color_to_cd_hex(stroke_color),
                    "scheme": "Color",
                },
            )
            alias.append(paint)
        return alias

    @classmethod
    def _make_list_of_complex_species_aliases(cls, ctx):
        list_elem = _make("listOfComplexSpeciesAliases", ns=_CD_NS)
        if ctx.map_.layout is not None:
            for layout_element in ctx.map_.layout.layout_elements:
                if isinstance(layout_element, momapy.celldesigner.core.ComplexLayout):
                    alias = cls._make_species_alias(
                        ctx, layout_element, "complexSpeciesAlias"
                    )
                    list_elem.append(alias)
                    cls._add_nested_complex_aliases(ctx, layout_element, list_elem)
                elif isinstance(
                    layout_element, momapy.celldesigner.core.ComplexActiveLayout
                ):
                    for child in layout_element.layout_elements:
                        if isinstance(child, momapy.celldesigner.core.ComplexLayout):
                            alias = cls._make_species_alias(
                                ctx, layout_element, "complexSpeciesAlias"
                            )
                            list_elem.append(alias)
                            cls._add_nested_complex_aliases(
                                ctx, layout_element, list_elem
                            )
                            break
        return list_elem

    @classmethod
    def _add_nested_complex_aliases(cls, ctx, parent_layout, list_elem):
        """Recursively add nested ComplexLayout children as complexSpeciesAliases."""
        for child in parent_layout.layout_elements:
            if isinstance(child, momapy.celldesigner.core.ComplexLayout):
                alias = cls._make_species_alias(
                    ctx,
                    child,
                    "complexSpeciesAlias",
                    complex_alias_id=parent_layout.id_,
                )
                list_elem.append(alias)
                cls._add_nested_complex_aliases(ctx, child, list_elem)

    @classmethod
    def _make_list_of_species_aliases(cls, ctx):
        list_elem = _make("listOfSpeciesAliases", ns=_CD_NS)
        if ctx.map_.layout is not None:
            for layout_element in ctx.map_.layout.layout_elements:
                if cls._is_species_layout(layout_element) and not isinstance(
                    layout_element,
                    (
                        momapy.celldesigner.core.ComplexLayout,
                        momapy.celldesigner.core.ComplexActiveLayout,
                    ),
                ):
                    alias = cls._make_species_alias(ctx, layout_element, "speciesAlias")
                    list_elem.append(alias)
            # Also add included species aliases (children of complex layouts)
            cls._add_included_species_aliases(ctx, list_elem)
        return list_elem

    @classmethod
    def _add_included_species_aliases(cls, ctx, list_elem):
        if ctx.map_.layout is None:
            return
        for layout_element in ctx.map_.layout.layout_elements:
            if isinstance(
                layout_element,
                (
                    momapy.celldesigner.core.ComplexLayout,
                    momapy.celldesigner.core.ComplexActiveLayout,
                ),
            ):
                cls._add_included_aliases_recursive(ctx, layout_element, list_elem)

    @classmethod
    def _add_included_aliases_recursive(cls, ctx, parent_layout, list_elem):
        for child in parent_layout.layout_elements:
            if cls._is_species_layout(child):
                # Nested ComplexLayouts are handled by
                # _add_nested_complex_aliases as complexSpeciesAliases;
                # do not duplicate them here as speciesAliases.
                is_complex = isinstance(
                    child,
                    (
                        momapy.celldesigner.core.ComplexLayout,
                        momapy.celldesigner.core.ComplexActiveLayout,
                    ),
                )
                if not is_complex:
                    complex_alias_id = parent_layout.id_
                    alias = cls._make_species_alias(
                        ctx, child, "speciesAlias", complex_alias_id
                    )
                    list_elem.append(alias)
                else:
                    cls._add_included_aliases_recursive(ctx, child, list_elem)

    @classmethod
    def _is_species_layout(cls, layout_element):
        return (
            isinstance(layout_element, momapy.celldesigner.core.CellDesignerNode)
            and not isinstance(
                layout_element,
                (
                    momapy.celldesigner.core.OvalCompartmentLayout,
                    momapy.celldesigner.core.RectangleCompartmentLayout,
                    momapy.celldesigner.core.ModificationLayout,
                    momapy.celldesigner.core.StructuralStateLayout,
                ),
            )
            and not isinstance(
                layout_element,
                tuple(
                    momapy.celldesigner.io.celldesigner._layout._LAYOUT_TO_ACTIVE_LAYOUT.values()
                ),
            )
        )

    @classmethod
    def _make_species_alias(cls, ctx, layout_element, tag, complex_alias_id=None):
        model_element = cls._get_model_element(ctx, layout_element)
        species_id = ""
        if model_element is not None:
            me = model_element[0] if isinstance(model_element, tuple) else model_element
            species_id = _writing.get_cd_species_id(me)
        attrs = {
            "id": _sid(layout_element.id_),
            "species": species_id,
        }
        if complex_alias_id is not None:
            attrs["complexSpeciesAlias"] = _sid(complex_alias_id)
        else:
            # Find compartment alias
            compartment_alias_id = cls._find_compartment_alias_id(ctx, model_element)
            if compartment_alias_id is not None:
                attrs["compartmentAlias"] = _sid(compartment_alias_id)
        alias = _make(tag, ns=_CD_NS, attributes=attrs)
        # activity
        active = False
        if model_element is not None:
            me = model_element[0] if isinstance(model_element, tuple) else model_element
            if hasattr(me, "active"):
                active = me.active
        activity_text = "active" if active else "inactive"
        activity = _make("activity", ns=_CD_NS, text=activity_text)
        alias.append(activity)
        # bounds
        bounds = _make(
            "bounds",
            ns=_CD_NS,
            attributes=_writing.node_to_bounds_attrs(layout_element),
        )
        alias.append(bounds)
        # font
        font_size = "14"
        if layout_element.label is not None:
            font_size = str(int(layout_element.label.font_size))
        font = _make("font", ns=_CD_NS, attributes={"size": font_size})
        alias.append(font)
        # view
        view = _make("view", ns=_CD_NS, attributes={"state": "usual"})
        alias.append(view)
        # usualView
        usual_view = cls._make_usual_view(layout_element)
        alias.append(usual_view)
        # briefView (same as usualView with different singleLine width)
        brief_view = cls._make_brief_view(layout_element)
        alias.append(brief_view)
        # structural state (for complex aliases)
        if model_element is not None:
            me = model_element[0] if isinstance(model_element, tuple) else model_element
            if hasattr(me, "structural_states") and me.structural_states:
                for ss in me.structural_states:
                    ss_elem = _make(
                        "structuralState",
                        ns=_CD_NS,
                        attributes={"angle": "1.5707963267948966"},
                    )
                    alias.append(ss_elem)
                    break
        return alias

    @classmethod
    def _make_usual_view(cls, layout_element):
        usual_view = _make("usualView", ns=_CD_NS)
        inner_pos = _make("innerPosition", ns=_CD_NS, attributes={"x": "0", "y": "0"})
        usual_view.append(inner_pos)
        box_size = _make(
            "boxSize",
            ns=_CD_NS,
            attributes={
                "width": str(layout_element.width),
                "height": str(layout_element.height),
            },
        )
        usual_view.append(box_size)
        stroke_width = getattr(layout_element, "stroke_width", 1.0) or 1.0
        single_line = _make(
            "singleLine",
            ns=_CD_NS,
            attributes={"width": str(stroke_width)},
        )
        usual_view.append(single_line)
        fill = getattr(layout_element, "fill", None)
        if fill is not None and fill is not momapy.drawing.NoneValue:
            color_hex = _writing.color_to_cd_hex(fill)
        else:
            color_hex = "FFF7F7F7"
        paint = _make(
            "paint", ns=_CD_NS, attributes={"color": color_hex, "scheme": "Color"}
        )
        usual_view.append(paint)
        return usual_view

    @classmethod
    def _make_brief_view(cls, layout_element):
        brief_view = _make("briefView", ns=_CD_NS)
        inner_pos = _make("innerPosition", ns=_CD_NS, attributes={"x": "0", "y": "0"})
        brief_view.append(inner_pos)
        box_size = _make(
            "boxSize",
            ns=_CD_NS,
            attributes={
                "width": str(layout_element.width),
                "height": str(layout_element.height),
            },
        )
        brief_view.append(box_size)
        # briefView singleLine width = the node width for complexes, 1.0 for others
        if isinstance(
            layout_element,
            (
                momapy.celldesigner.core.ComplexLayout,
                momapy.celldesigner.core.ComplexActiveLayout,
            ),
        ):
            brief_line_width = str(layout_element.width)
        else:
            brief_line_width = str(getattr(layout_element, "stroke_width", 1.0) or 1.0)
        single_line = _make(
            "singleLine",
            ns=_CD_NS,
            attributes={"width": brief_line_width},
        )
        brief_view.append(single_line)
        fill = getattr(layout_element, "fill", None)
        if fill is not None and fill is not momapy.drawing.NoneValue:
            color_hex = _writing.color_to_cd_hex(fill)
        else:
            color_hex = "FFF7F7F7"
        paint = _make(
            "paint", ns=_CD_NS, attributes={"color": color_hex, "scheme": "Color"}
        )
        brief_view.append(paint)
        return brief_view

    @classmethod
    def _find_compartment_alias_id(cls, ctx, model_element):
        if model_element is None:
            return None
        me = model_element[0] if isinstance(model_element, tuple) else model_element
        compartment = getattr(me, "compartment", None)
        if compartment is None:
            return None
        # Find the compartment layout alias
        if ctx.map_.layout is not None:
            for layout_element in ctx.map_.layout.layout_elements:
                if isinstance(
                    layout_element,
                    (
                        momapy.celldesigner.core.OvalCompartmentLayout,
                        momapy.celldesigner.core.RectangleCompartmentLayout,
                    ),
                ):
                    comp_model = cls._get_model_element(ctx, layout_element)
                    if comp_model is not None and comp_model.id_ == compartment.id_:
                        return _sid(layout_element.id_)
        return None

    @classmethod
    def _find_canonical_species(cls, ctx, species):
        """Find the canonical model species (the one in model.species).

        The mapping may contain species objects that are structurally
        equal to a model species but have a different id_.  This returns
        the actual object from model.species so that the written ID is
        consistent.

        Args:
            ctx: WritingContext.
            species: A species model element.

        Returns:
            The canonical model species, or the input if not found.
        """
        if ctx.map_.model is None:
            return species
        for s in ctx.map_.model.species:
            if s is species:
                return s
            if s == species:
                return s
        return species

    @classmethod
    def _make_list_of_included_species(cls, ctx):
        if ctx.map_.model is None:
            return None
        # Find species that are subunits of complexes (from model)
        included_species = []
        for species in ctx.map_.model.species:
            if isinstance(species, momapy.celldesigner.core.Complex):
                for subunit in species.subunits:
                    included_species.append((subunit, species))
        # Also find included species from the mapping (some may not be in
        # model.species.subunits due to reader deduplication)
        if ctx.map_.layout_model_mapping is not None:
            for key, value in ctx.map_.layout_model_mapping.items():
                if isinstance(value, tuple) and len(value) == 2:
                    species_model, complex_model = value
                    if isinstance(
                        complex_model, momapy.celldesigner.core.Complex
                    ) and not isinstance(
                        species_model, momapy.celldesigner.core.Complex
                    ):
                        # Resolve to canonical model species for consistent IDs
                        canonical_complex = cls._find_canonical_species(
                            ctx, complex_model
                        )
                        included_species.append((species_model, canonical_complex))
        if not included_species:
            return None
        list_elem = _make("listOfIncludedSpecies", ns=_CD_NS)
        seen_ids = set()
        for subunit, parent_complex in included_species:
            cd_id = _writing.get_cd_species_id(subunit)
            if cd_id in seen_ids:
                continue
            seen_ids.add(cd_id)
            sp_elem = cls._make_included_species(ctx, subunit, parent_complex)
            list_elem.append(sp_elem)
        return list_elem

    @classmethod
    def _make_included_species(cls, ctx, species, parent_complex):
        cd_id = _writing.get_cd_species_id(species)
        attrs = {
            "id": cd_id,
            "name": _writing.encode_name(species.name) or "",
        }
        sp_elem = _make("species", ns=_CD_NS, attributes=attrs)
        # notes with annotations (CellDesigner stores annotations inside notes
        # for included species; always write notes element for compatibility)
        cd_notes = _make("notes", ns=_CD_NS)
        html = lxml.etree.SubElement(cd_notes, f"{{{_XHTML_NS}}}html")
        head = lxml.etree.SubElement(html, f"{{{_XHTML_NS}}}head")
        lxml.etree.SubElement(head, f"{{{_XHTML_NS}}}title")
        body = lxml.etree.SubElement(html, f"{{{_XHTML_NS}}}body")
        # Text notes
        species_notes = ctx.notes.get(species, set())
        if species_notes:
            body.text = "\n".join(species_notes)
        # RDF annotations inside body
        if ctx.with_annotations:
            rdf = cls._make_rdf_for_element(ctx, species)
            if rdf is not None:
                body.append(rdf)
        sp_elem.append(cd_notes)
        # annotation
        cd_annotation = _make("annotation", ns=_CD_NS)
        complex_species = _make(
            "complexSpecies", ns=_CD_NS, text=_writing.get_cd_species_id(parent_complex)
        )
        cd_annotation.append(complex_species)
        identity = cls._make_species_identity(ctx, species)
        cd_annotation.append(identity)
        sp_elem.append(cd_annotation)
        return sp_elem

    @classmethod
    def _make_species_identity(cls, ctx, species):
        identity = _make("speciesIdentity", ns=_CD_NS)
        key = cls._CLASS_TO_KEY.get(type(species))
        if key is not None:
            class_text = key[1]
        else:
            class_text = "UNKNOWN"
        # Map GENERIC -> PROTEIN, etc. for species class element
        species_class_map = {
            "GENERIC": "PROTEIN",
            "ION_CHANNEL": "PROTEIN",
            "RECEPTOR": "PROTEIN",
            "TRUNCATED": "PROTEIN",
        }
        class_elem = _make(
            "class", ns=_CD_NS, text=species_class_map.get(class_text, class_text)
        )
        identity.append(class_elem)
        # reference to template
        template = getattr(species, "template", None)
        if template is not None:
            if isinstance(template, momapy.celldesigner.core.ProteinTemplate):
                ref_tag = "proteinReference"
            elif isinstance(template, momapy.celldesigner.core.GeneTemplate):
                ref_tag = "geneReference"
            elif isinstance(template, momapy.celldesigner.core.RNATemplate):
                ref_tag = "rnaReference"
            elif isinstance(template, momapy.celldesigner.core.AntisenseRNATemplate):
                ref_tag = "antisensernaReference"
            else:
                ref_tag = "proteinReference"
            ref = _make(ref_tag, ns=_CD_NS, text=_sid(template.id_))
            identity.append(ref)
        # name
        name_elem = _make("name", ns=_CD_NS, text=_writing.encode_name(species.name))
        identity.append(name_elem)
        # state (modifications, structural states, homodimer)
        state = cls._make_species_state(ctx, species)
        if state is not None:
            identity.append(state)
        return identity

    @classmethod
    def _make_species_state(cls, ctx, species):
        has_modifications = hasattr(species, "modifications") and species.modifications
        has_structural_states = (
            hasattr(species, "structural_states") and species.structural_states
        )
        has_homodimer = hasattr(species, "homomultimer") and species.homomultimer > 1
        if not has_modifications and not has_structural_states and not has_homodimer:
            return None
        state = _make("state", ns=_CD_NS)
        # homodimer
        if has_homodimer:
            homodimer = _make("homodimer", ns=_CD_NS, text=str(species.homomultimer))
            state.append(homodimer)
        # listOfModifications
        if has_modifications:
            mod_list = _make("listOfModifications", ns=_CD_NS)
            for modification in sorted(
                species.modifications,
                key=lambda m: m.residue.id_ if m.residue is not None else "",
            ):
                mod_attrs = {}
                if modification.residue is not None:
                    # residue id is "templateId_residueId", we need just residueId
                    parts = modification.residue.id_.split("_", 1)
                    mod_attrs["residue"] = _sid(
                        parts[1] if len(parts) > 1 else modification.residue.id_
                    )
                if modification.state is not None:
                    # Convert enum name to CellDesigner state string
                    state_str = modification.state.name.lower().replace("_", " ")
                    # Handle special case DON_T_CARE -> "don't care"
                    if (
                        modification.state
                        == momapy.celldesigner.core.ModificationState.DON_T_CARE
                    ):
                        state_str = "don't care"
                    mod_attrs["state"] = state_str
                else:
                    mod_attrs["state"] = "empty"
                mod_elem = _make("modification", ns=_CD_NS, attributes=mod_attrs)
                mod_list.append(mod_elem)
            state.append(mod_list)
        # listOfStructuralStates
        if has_structural_states:
            ss_list = _make("listOfStructuralStates", ns=_CD_NS)
            for ss in species.structural_states:
                ss_attrs = {}
                if ss.value is not None:
                    ss_attrs["structuralState"] = ss.value
                ss_elem = _make("structuralState", ns=_CD_NS, attributes=ss_attrs)
                ss_list.append(ss_elem)
            state.append(ss_list)
        return state

    @classmethod
    def _make_list_of_compartments(cls, ctx):
        if ctx.map_.model is None:
            return None
        list_elem = _make("listOfCompartments")
        for compartment in sorted(
            ctx.map_.model.compartments, key=lambda c: c.id_ or ""
        ):
            comp = cls._make_compartment(ctx, compartment)
            list_elem.append(comp)
        return list_elem

    @classmethod
    def _make_compartment(cls, ctx, compartment):
        attrs = {
            "id": _sid(compartment.id_ or ""),
            "name": _writing.encode_name(compartment.name) or "",
            "size": "1",
            "units": "volume",
        }
        if compartment.metaid is not None:
            attrs["metaid"] = _unique_metaid(ctx, _xmlid(compartment.metaid))
        if compartment.outside is not None:
            attrs["outside"] = _sid(compartment.outside.id_)
        comp = _make("compartment", attributes=attrs)
        # notes
        if ctx.with_notes:
            notes = cls._make_notes_for_element(ctx, compartment)
            if notes is not None:
                comp.append(notes)
        # annotation with extension + rdf
        annotation = _make("annotation")
        cd_ext = _make("extension", ns=_CD_NS)
        cd_name = _make("name", ns=_CD_NS, text=_writing.encode_name(compartment.name))
        cd_ext.append(cd_name)
        annotation.append(cd_ext)
        if ctx.with_annotations:
            rdf = cls._make_rdf_for_element(ctx, compartment)
            if rdf is not None:
                annotation.append(rdf)
        comp.append(annotation)
        return comp

    @classmethod
    def _make_list_of_species(cls, ctx):
        if ctx.map_.model is None:
            return None
        list_elem = _make("listOfSpecies")
        seen_ids = set()
        for species in sorted(
            ctx.map_.model.species,
            key=lambda s: _writing.get_cd_species_id(s),
        ):
            cd_id = _writing.get_cd_species_id(species)
            if cd_id in seen_ids:
                continue
            seen_ids.add(cd_id)
            sp = cls._make_sbml_species(ctx, species)
            list_elem.append(sp)
        return list_elem

    @classmethod
    def _make_sbml_species(cls, ctx, species):
        cd_id = _writing.get_cd_species_id(species)
        attrs = {
            "id": cd_id,
            "name": _writing.encode_name(species.name) or "",
            "initialAmount": "0.0",
            "hasOnlySubstanceUnits": "false",
            "constant": "false",
            "boundaryCondition": "false",
        }
        if species.metaid is not None:
            attrs["metaid"] = _unique_metaid(ctx, _xmlid(species.metaid))
        if species.compartment is not None:
            attrs["compartment"] = _sid(species.compartment.id_)
        sp = _make("species", attributes=attrs)
        # notes
        if ctx.with_notes:
            notes = cls._make_notes_for_element(ctx, species)
            if notes is not None:
                sp.append(notes)
        # annotation with extension containing speciesIdentity + rdf
        annotation = _make("annotation")
        cd_ext = _make("extension", ns=_CD_NS)
        pos_to_compartment = _make("positionToCompartment", ns=_CD_NS, text="inside")
        cd_ext.append(pos_to_compartment)
        identity = cls._make_species_identity(ctx, species)
        cd_ext.append(identity)
        annotation.append(cd_ext)
        if ctx.with_annotations:
            rdf = cls._make_rdf_for_element(ctx, species)
            if rdf is not None:
                annotation.append(rdf)
        sp.append(annotation)
        return sp

    @classmethod
    def _make_list_of_reactions(cls, ctx):
        if ctx.map_.model is None:
            return None
        list_elem = _make("listOfReactions")
        # True reactions
        for reaction in sorted(ctx.map_.model.reactions, key=lambda r: r.id_ or ""):
            rxn = cls._make_reaction(ctx, reaction)
            list_elem.append(rxn)
        # Modulations (false reactions)
        for modulation in sorted(ctx.map_.model.modulations, key=lambda m: m.id_ or ""):
            rxn = cls._make_modulation_as_reaction(ctx, modulation)
            list_elem.append(rxn)
        return list_elem

    @classmethod
    def _make_reaction(cls, ctx, reaction):
        attrs = {
            "id": _sid(reaction.id_ or ""),
            "reversible": "true" if reaction.reversible else "false",
        }
        if reaction.metaid is not None:
            attrs["metaid"] = _unique_metaid(ctx, _xmlid(reaction.metaid))
        rxn = _make("reaction", attributes=attrs)
        reaction_layout = cls._find_reaction_layout(ctx, reaction)
        fset = None
        if reaction_layout is not None:
            fset = cls._find_frozenset_for_layout(ctx, reaction_layout)
        annotation = _make("annotation")
        cd_ext = cls._make_reaction_extension(ctx, reaction, reaction_layout, fset)
        annotation.append(cd_ext)
        if ctx.with_annotations:
            rdf = cls._make_rdf_for_element(ctx, reaction)
            if rdf is not None:
                annotation.append(rdf)
        rxn.append(annotation)
        reactants_elem = _make("listOfReactants")
        for reactant in sorted(reaction.reactants, key=lambda r: r.id_ or ""):
            sr = cls._make_species_reference(
                ctx, reactant, "speciesReference", frozenset_scope=fset
            )
            reactants_elem.append(sr)
        rxn.append(reactants_elem)
        products_elem = _make("listOfProducts")
        for product in sorted(reaction.products, key=lambda p: p.id_ or ""):
            sr = cls._make_species_reference(
                ctx, product, "speciesReference", frozenset_scope=fset
            )
            products_elem.append(sr)
        rxn.append(products_elem)
        if reaction.modifiers:
            modifiers_elem = _make("listOfModifiers")
            # Order SBML modifiers to match CD listOfModification order
            # (CellDesigner matches them by index).
            ordered_modifiers = cls._order_modifiers_by_layout(
                ctx, reaction, reaction_layout
            )
            for modifier in ordered_modifiers:
                species_ref = modifier.referred_species
                if isinstance(species_ref, momapy.celldesigner.core.BooleanLogicGate):
                    continue
                mod_attrs = {"species": _writing.get_cd_species_id(species_ref)}
                if modifier.id_ is not None:
                    mod_attrs["metaid"] = _unique_metaid(ctx, _xmlid(modifier.id_))
                msr = _make("modifierSpeciesReference", attributes=mod_attrs)
                mod_ann = _make("annotation")
                mod_ext = _make("extension", ns=_CD_NS)
                alias_id = cls._find_alias_id_for_species(
                    ctx, species_ref, frozenset_scope=fset
                )
                alias_elem = _make("alias", ns=_CD_NS, text=alias_id or "")
                mod_ext.append(alias_elem)
                mod_ann.append(mod_ext)
                msr.append(mod_ann)
                modifiers_elem.append(msr)
            rxn.append(modifiers_elem)
        return rxn

    @classmethod
    def _make_reaction_extension(cls, ctx, reaction, reaction_layout, fset=None):
        cd_ext = _make("extension", ns=_CD_NS)
        # reactionType
        key = cls._CLASS_TO_KEY.get(type(reaction))
        reaction_type = key[1] if key is not None else "STATE_TRANSITION"
        rt = _make("reactionType", ns=_CD_NS, text=reaction_type)
        cd_ext.append(rt)
        # Determine T-shape from reaction type:
        # - HeterodimerAssociation: left-T (2 base reactants, 1 base product)
        # - Dissociation: right-T (1 base reactant, 2 base products)
        # - Everything else: non-T (1 base reactant, 1 base product)
        is_left_t = isinstance(
            reaction, momapy.celldesigner.core.HeterodimerAssociation
        )
        is_right_t = isinstance(reaction, momapy.celldesigner.core.Dissociation)
        is_non_t = not is_left_t and not is_right_t
        all_reactants = sorted(reaction.reactants, key=lambda r: r.id_ or "")
        all_products = sorted(reaction.products, key=lambda p: p.id_ or "")
        if is_left_t:
            n_base_r, n_base_p = 2, 1
        elif is_right_t:
            n_base_r, n_base_p = 1, 2
        else:
            n_base_r, n_base_p = 1, 1
        base_reactants, link_reactants = cls._split_base_and_links(
            ctx, all_reactants, reaction_layout, n_base_r, is_reactant=True
        )
        base_products, link_products = cls._split_base_and_links(
            ctx, all_products, reaction_layout, n_base_p, is_reactant=False
        )
        # Build base reactants/products with link anchors
        if reaction_layout is not None and is_non_t:
            edit_points, r_anchor, p_anchor, rect_index = (
                _writing.inverse_edit_points_non_t_shape(
                    reaction_layout,
                    cls._find_species_layout_for_participant(ctx, base_reactants[0]),
                    cls._find_species_layout_for_participant(ctx, base_products[0]),
                )
            )
            # baseReactants
            br_elem = _make("baseReactants", ns=_CD_NS)
            br = cls._make_base_participant(
                ctx,
                base_reactants[0],
                "baseReactant",
                r_anchor,
                frozenset_scope=fset,
            )
            br_elem.append(br)
            cd_ext.append(br_elem)
            bp_elem = _make("baseProducts", ns=_CD_NS)
            bp = cls._make_base_participant(
                ctx,
                base_products[0],
                "baseProduct",
                p_anchor,
                frozenset_scope=fset,
            )
            bp_elem.append(bp)
            cd_ext.append(bp_elem)
            cd_ext.append(
                cls._make_reactant_links(ctx, reaction, reaction_layout, base_reactants)
            )
            cd_ext.append(
                cls._make_product_links(ctx, reaction, reaction_layout, base_products)
            )
            cs = _make(
                "connectScheme",
                ns=_CD_NS,
                attributes={
                    "connectPolicy": "direct",
                    "rectangleIndex": str(rect_index),
                },
            )
            lld = _make("listOfLineDirection", ns=_CD_NS)
            for i in range(len(edit_points) + 3):
                ld = _make(
                    "lineDirection",
                    ns=_CD_NS,
                    attributes={"index": str(i), "value": "unknown"},
                )
                lld.append(ld)
            cs.append(lld)
            cd_ext.append(cs)
            # editPoints (only if there are intermediate points)
            if edit_points:
                ep = _make(
                    "editPoints",
                    ns=_CD_NS,
                    text=_writing.points_to_edit_points_text(edit_points),
                )
                cd_ext.append(ep)
        elif reaction_layout is not None and is_left_t:
            reactant_layouts = [
                cls._find_species_layout_for_participant(ctx, r) for r in base_reactants
            ]
            product_layout = cls._find_species_layout_for_participant(
                ctx, base_products[0]
            )
            consumption_layouts = cls._find_base_consumption_layouts(
                ctx, reaction_layout, base_reactants
            )
            (
                all_edit_points,
                num0,
                num1,
                num2,
                t_shape_index,
                p_anchor,
                r_anchors,
            ) = _writing.inverse_edit_points_left_t_shape(
                reaction_layout,
                reactant_layouts,
                product_layout,
                consumption_layouts,
            )
            # baseReactants
            br_elem = _make("baseReactants", ns=_CD_NS)
            for i, reactant in enumerate(base_reactants):
                anchor = r_anchors[i] if i < len(r_anchors) else "center"
                br = cls._make_base_participant(
                    ctx,
                    reactant,
                    "baseReactant",
                    anchor,
                    frozenset_scope=fset,
                )
                br_elem.append(br)
            cd_ext.append(br_elem)
            bp_elem = _make("baseProducts", ns=_CD_NS)
            bp = cls._make_base_participant(
                ctx,
                base_products[0],
                "baseProduct",
                p_anchor,
                frozenset_scope=fset,
            )
            bp_elem.append(bp)
            cd_ext.append(bp_elem)
            cd_ext.append(
                cls._make_reactant_links(ctx, reaction, reaction_layout, base_reactants)
            )
            cd_ext.append(
                cls._make_product_links(ctx, reaction, reaction_layout, base_products)
            )
            cs = _make(
                "connectScheme",
                ns=_CD_NS,
                attributes={"connectPolicy": "direct"},
            )
            lld = _make("listOfLineDirection", ns=_CD_NS)
            for arm_idx, arm_count in enumerate([num0, num1, num2]):
                for idx in range(arm_count + 1):
                    ld = _make(
                        "lineDirection",
                        ns=_CD_NS,
                        attributes={
                            "arm": str(arm_idx),
                            "index": str(idx),
                            "value": "unknown",
                        },
                    )
                    lld.append(ld)
            cs.append(lld)
            cd_ext.append(cs)
            # editPoints with num0, num1, num2, tShapeIndex
            ep_attrs = {
                "num0": str(num0),
                "num1": str(num1),
                "num2": str(num2),
                "tShapeIndex": str(t_shape_index),
            }
            ep = _make(
                "editPoints",
                ns=_CD_NS,
                attributes=ep_attrs,
                text=_writing.points_to_edit_points_text(all_edit_points),
            )
            cd_ext.append(ep)
        elif reaction_layout is not None and is_right_t:
            reactant_layout = cls._find_species_layout_for_participant(
                ctx, base_reactants[0]
            )
            product_layouts = [
                cls._find_species_layout_for_participant(ctx, p) for p in base_products
            ]
            production_layouts = cls._find_base_production_layouts(
                ctx, reaction_layout, base_products
            )
            (
                all_edit_points,
                num0,
                num1,
                num2,
                t_shape_index,
                r_anchor,
                p_anchors,
            ) = _writing.inverse_edit_points_right_t_shape(
                reaction_layout,
                reactant_layout,
                product_layouts,
                production_layouts,
            )
            # baseReactants
            br_elem = _make("baseReactants", ns=_CD_NS)
            br = cls._make_base_participant(
                ctx,
                base_reactants[0],
                "baseReactant",
                r_anchor,
                frozenset_scope=fset,
            )
            br_elem.append(br)
            cd_ext.append(br_elem)
            bp_elem = _make("baseProducts", ns=_CD_NS)
            for i, product in enumerate(base_products):
                anchor = p_anchors[i] if i < len(p_anchors) else "center"
                bp = cls._make_base_participant(
                    ctx,
                    product,
                    "baseProduct",
                    anchor,
                    frozenset_scope=fset,
                )
                bp_elem.append(bp)
            cd_ext.append(bp_elem)
            cd_ext.append(
                cls._make_reactant_links(ctx, reaction, reaction_layout, base_reactants)
            )
            cd_ext.append(
                cls._make_product_links(ctx, reaction, reaction_layout, base_products)
            )
            cs = _make(
                "connectScheme",
                ns=_CD_NS,
                attributes={"connectPolicy": "direct"},
            )
            lld = _make("listOfLineDirection", ns=_CD_NS)
            for arm_idx, arm_count in enumerate([num0, num1, num2]):
                for idx in range(arm_count + 1):
                    ld = _make(
                        "lineDirection",
                        ns=_CD_NS,
                        attributes={
                            "arm": str(arm_idx),
                            "index": str(idx),
                            "value": "unknown",
                        },
                    )
                    lld.append(ld)
            cs.append(lld)
            cd_ext.append(cs)
            ep_attrs = {
                "num0": str(num0),
                "num1": str(num1),
                "num2": str(num2),
                "tShapeIndex": str(t_shape_index),
            }
            ep = _make(
                "editPoints",
                ns=_CD_NS,
                attributes=ep_attrs,
                text=_writing.points_to_edit_points_text(all_edit_points),
            )
            cd_ext.append(ep)
        else:
            # Fallback: write minimal structure
            br_elem = _make("baseReactants", ns=_CD_NS)
            for reactant in base_reactants:
                br = cls._make_base_participant(
                    ctx,
                    reactant,
                    "baseReactant",
                    "center",
                    frozenset_scope=fset,
                )
                br_elem.append(br)
            cd_ext.append(br_elem)
            bp_elem = _make("baseProducts", ns=_CD_NS)
            for product in base_products:
                bp = cls._make_base_participant(
                    ctx,
                    product,
                    "baseProduct",
                    "center",
                    frozenset_scope=fset,
                )
                bp_elem.append(bp)
            cd_ext.append(bp_elem)
            cd_ext.append(_make("listOfReactantLinks", ns=_CD_NS))
            cd_ext.append(_make("listOfProductLinks", ns=_CD_NS))
            cs = _make(
                "connectScheme",
                ns=_CD_NS,
                attributes={"connectPolicy": "direct", "rectangleIndex": "0"},
            )
            lld = _make("listOfLineDirection", ns=_CD_NS)
            ld = _make(
                "lineDirection",
                ns=_CD_NS,
                attributes={"index": "0", "value": "unknown"},
            )
            lld.append(ld)
            cs.append(lld)
            cd_ext.append(cs)
        # listOfModification (modifiers on the reaction)
        mod_list = cls._make_list_of_reaction_modifications(
            ctx, reaction, reaction_layout
        )
        cd_ext.append(mod_list)
        # line
        line = cls._make_line_element(reaction_layout)
        cd_ext.append(line)
        return cd_ext

    @classmethod
    def _make_base_participant(
        cls, ctx, participant, tag, anchor_name, frozenset_scope=None
    ):
        species = participant.referred_species
        alias_id = (
            cls._find_alias_id_for_species(
                ctx, species, frozenset_scope=frozenset_scope
            )
            or ""
        )
        attrs = {
            "species": _writing.get_cd_species_id(species),
            "alias": alias_id,
        }
        elem = _make(tag, ns=_CD_NS, attributes=attrs)
        if anchor_name != "center":
            position = _writing._ANCHOR_NAME_TO_LINK_ANCHOR_POSITION.get(anchor_name)
            if position is not None:
                link_anchor = _make(
                    "linkAnchor",
                    ns=_CD_NS,
                    attributes={"position": position},
                )
                elem.append(link_anchor)
        return elem

    @classmethod
    def _make_reactant_links(cls, ctx, reaction, reaction_layout, base_reactants):
        list_elem = _make("listOfReactantLinks", ns=_CD_NS)
        if reaction_layout is None:
            return list_elem
        # Build set of base reactant species to skip
        base_species = {r.referred_species for r in base_reactants}
        # Find consumption layouts that are reactant links (not base reactant
        # consumptions in T-shape)
        for child in reaction_layout.layout_elements:
            if isinstance(child, momapy.celldesigner.core.ConsumptionLayout):
                # Determine which species this links to
                species_layout = cls._find_species_at_start(ctx, child)
                if species_layout is None:
                    continue
                model_info = ctx.layout_to_model.get(child)
                if model_info is None:
                    continue
                reactant_model = (
                    model_info[0] if isinstance(model_info, tuple) else model_info
                )
                species = (
                    reactant_model.referred_species
                    if hasattr(reactant_model, "referred_species")
                    else None
                )
                if species is None:
                    continue
                # Skip base reactants (they are handled as baseReactants)
                if species in base_species:
                    continue
                alias_id = cls._find_alias_id_for_species(ctx, species) or ""
                edit_points, anchor_name = _writing.inverse_edit_points_reactant_link(
                    child, species_layout, reaction_layout
                )
                attrs = {
                    "reactant": _writing.get_cd_species_id(species),
                    "alias": alias_id,
                }
                link = _make("reactantLink", ns=_CD_NS, attributes=attrs)
                if anchor_name != "center":
                    position = _writing._ANCHOR_NAME_TO_LINK_ANCHOR_POSITION.get(
                        anchor_name
                    )
                    if position is not None:
                        la = _make(
                            "linkAnchor",
                            ns=_CD_NS,
                            attributes={"position": position},
                        )
                        link.append(la)
                # connectScheme
                cs = _make(
                    "connectScheme",
                    ns=_CD_NS,
                    attributes={"connectPolicy": "direct"},
                )
                lld = _make("listOfLineDirection", ns=_CD_NS)
                ld = _make(
                    "lineDirection",
                    ns=_CD_NS,
                    attributes={"index": "0", "value": "unknown"},
                )
                lld.append(ld)
                cs.append(lld)
                link.append(cs)
                if edit_points:
                    ep = _make(
                        "editPoints",
                        ns=_CD_NS,
                        text=_writing.points_to_edit_points_text(edit_points),
                    )
                    link.append(ep)
                link.append(cls._make_line_element(None, width="1.0"))
                list_elem.append(link)
        return list_elem

    @classmethod
    def _make_product_links(cls, ctx, reaction, reaction_layout, base_products):
        list_elem = _make("listOfProductLinks", ns=_CD_NS)
        if reaction_layout is None:
            return list_elem
        base_species = {p.referred_species for p in base_products}
        for child in reaction_layout.layout_elements:
            if isinstance(child, momapy.celldesigner.core.ProductionLayout):
                species_layout = cls._find_species_at_end(ctx, child)
                if species_layout is None:
                    continue
                model_info = ctx.layout_to_model.get(child)
                if model_info is None:
                    continue
                product_model = (
                    model_info[0] if isinstance(model_info, tuple) else model_info
                )
                species = (
                    product_model.referred_species
                    if hasattr(product_model, "referred_species")
                    else None
                )
                if species is None:
                    continue
                if species in base_species:
                    continue
                alias_id = cls._find_alias_id_for_species(ctx, species) or ""
                edit_points, anchor_name = _writing.inverse_edit_points_product_link(
                    child, species_layout, reaction_layout
                )
                attrs = {
                    "product": _writing.get_cd_species_id(species),
                    "alias": alias_id,
                }
                link = _make("productLink", ns=_CD_NS, attributes=attrs)
                if anchor_name != "center":
                    position = _writing._ANCHOR_NAME_TO_LINK_ANCHOR_POSITION.get(
                        anchor_name
                    )
                    if position is not None:
                        la = _make(
                            "linkAnchor",
                            ns=_CD_NS,
                            attributes={"position": position},
                        )
                        link.append(la)
                cs = _make(
                    "connectScheme",
                    ns=_CD_NS,
                    attributes={"connectPolicy": "direct"},
                )
                lld = _make("listOfLineDirection", ns=_CD_NS)
                ld = _make(
                    "lineDirection",
                    ns=_CD_NS,
                    attributes={"index": "0", "value": "unknown"},
                )
                lld.append(ld)
                cs.append(lld)
                link.append(cs)
                if edit_points:
                    ep = _make(
                        "editPoints",
                        ns=_CD_NS,
                        text=_writing.points_to_edit_points_text(edit_points),
                    )
                    link.append(ep)
                link.append(cls._make_line_element(None, width="1.0"))
                list_elem.append(link)
        return list_elem

    @classmethod
    def _make_list_of_reaction_modifications(cls, ctx, reaction, reaction_layout):
        list_elem = _make("listOfModification", ns=_CD_NS)
        if reaction_layout is None:
            return list_elem
        for child in reaction_layout.layout_elements:
            if cls._is_modifier_layout(child):
                mod = cls._make_reaction_modification(ctx, child, reaction_layout)
                if mod is not None:
                    list_elem.append(mod)
        return list_elem

    @classmethod
    def _is_modifier_layout(cls, layout_element):
        return isinstance(
            layout_element,
            (
                momapy.celldesigner.core.CatalysisLayout,
                momapy.celldesigner.core.UnknownCatalysisLayout,
                momapy.celldesigner.core.InhibitionLayout,
                momapy.celldesigner.core.UnknownInhibitionLayout,
                momapy.celldesigner.core.PhysicalStimulationLayout,
                momapy.celldesigner.core.UnknownPhysicalStimulationLayout,
                momapy.celldesigner.core.ModulationLayout,
                momapy.celldesigner.core.UnknownModulationLayout,
                momapy.celldesigner.core.PositiveInfluenceLayout,
                momapy.celldesigner.core.UnknownPositiveInfluenceLayout,
                momapy.celldesigner.core.TriggeringLayout,
                momapy.celldesigner.core.UnknownTriggeringLayout,
            ),
        )

    @classmethod
    def _make_reaction_modification(cls, ctx, modifier_layout, reaction_layout):
        model_info = ctx.layout_to_model.get(modifier_layout)
        if model_info is None:
            return None
        modifier_model = model_info[0] if isinstance(model_info, tuple) else model_info
        source_layout = modifier_layout.source
        has_boolean_input = isinstance(
            source_layout,
            (
                momapy.celldesigner.core.AndGateLayout,
                momapy.celldesigner.core.OrGateLayout,
                momapy.celldesigner.core.NotGateLayout,
                momapy.celldesigner.core.UnknownGateLayout,
            ),
        )
        edit_points, source_anchor_name = _writing.inverse_edit_points_modifier(
            modifier_layout, source_layout, reaction_layout, has_boolean_input
        )
        # Determine modifier type
        key = cls._CLASS_TO_KEY.get(type(modifier_model))
        if key is not None:
            mod_type = key[1]
        else:
            mod_type = "CATALYSIS"
        # Get aliases
        if has_boolean_input:
            # For boolean gates, we need the input species aliases
            gate_model = ctx.layout_to_model.get(source_layout)
            if gate_model is not None:
                if isinstance(gate_model, tuple):
                    gate_model = gate_model[0]
                input_aliases = []
                for inp in gate_model.inputs:
                    alias_id = cls._find_alias_id_for_species(ctx, inp)
                    if alias_id is not None:
                        input_aliases.append(alias_id)
                aliases_text = ",".join(input_aliases)
                modifiers_text = ",".join(_sid(inp.id_) for inp in gate_model.inputs)
            else:
                aliases_text = ""
                modifiers_text = ""
            gate_key = cls._CLASS_TO_KEY.get(type(gate_model))
            if gate_key is not None:
                gate_type = gate_key[1]
            else:
                gate_type = "BOOLEAN_LOGIC_GATE_AND"
            attrs = {
                "type": gate_type,
                "modifiers": modifiers_text,
                "aliases": aliases_text,
                "modificationType": mod_type,
            }
        else:
            species = modifier_model.referred_species
            alias_id = cls._find_alias_id_for_species(ctx, species) or ""
            attrs = {
                "type": mod_type,
                "modifiers": _writing.get_cd_species_id(species),
                "aliases": alias_id,
            }
        if edit_points:
            if has_boolean_input:
                # Append the gate position as the last edit point
                gate_pos = source_layout.position
                edit_points_with_gate = edit_points + [gate_pos]
                attrs["editPoints"] = _writing.points_to_edit_points_text(
                    edit_points_with_gate
                )
            else:
                attrs["editPoints"] = _writing.points_to_edit_points_text(edit_points)
        elif has_boolean_input:
            gate_pos = source_layout.position
            attrs["editPoints"] = _writing.points_to_edit_points_text([gate_pos])
        mod_elem = _make("modification", ns=_CD_NS, attributes=attrs)
        # connectScheme
        cs = _make(
            "connectScheme",
            ns=_CD_NS,
            attributes={"connectPolicy": "direct"},
        )
        lld = _make("listOfLineDirection", ns=_CD_NS)
        n_directions = len(edit_points) + 2
        for i in range(n_directions):
            ld = _make(
                "lineDirection",
                ns=_CD_NS,
                attributes={"index": str(i), "value": "unknown"},
            )
            lld.append(ld)
        cs.append(lld)
        mod_elem.append(cs)
        # linkTarget (for non-boolean)
        if not has_boolean_input:
            species = modifier_model.referred_species
            alias_id = cls._find_alias_id_for_species(ctx, species) or ""
            lt_attrs = {
                "species": _writing.get_cd_species_id(species),
                "alias": alias_id,
            }
            lt = _make("linkTarget", ns=_CD_NS, attributes=lt_attrs)
            if source_anchor_name != "center":
                position = _writing._ANCHOR_NAME_TO_LINK_ANCHOR_POSITION.get(
                    source_anchor_name
                )
                if position is not None:
                    la = _make(
                        "linkAnchor",
                        ns=_CD_NS,
                        attributes={"position": position},
                    )
                    lt.append(la)
            mod_elem.append(lt)
        # line
        mod_elem.append(cls._make_line_element(modifier_layout))
        return mod_elem

    @classmethod
    def _make_modulation_as_reaction(cls, ctx, modulation):
        """Write a modulation as a false SBML reaction."""
        attrs = {
            "id": _sid(modulation.id_ or ""),
            "reversible": "false",
        }
        metaid = getattr(modulation, "metaid", None)
        if metaid is not None:
            attrs["metaid"] = _unique_metaid(ctx, _xmlid(metaid))
        rxn = _make("reaction", attributes=attrs)
        modulation_layout = cls._find_modulation_layout(ctx, modulation)
        fset = None
        if modulation_layout is not None:
            fset = cls._find_frozenset_for_layout(ctx, modulation_layout)
        annotation = _make("annotation")
        cd_ext = _make("extension", ns=_CD_NS)
        key = cls._CLASS_TO_KEY.get(type(modulation))
        if key is not None:
            reaction_type = key[1]
        else:
            reaction_type = "CATALYSIS"
        has_boolean_input = isinstance(
            modulation.source, momapy.celldesigner.core.BooleanLogicGate
        )
        if has_boolean_input:
            rt = _make("reactionType", ns=_CD_NS, text="BOOLEAN_LOGIC_GATE")
        else:
            rt = _make("reactionType", ns=_CD_NS, text=reaction_type)
        cd_ext.append(rt)
        source_alias = (
            cls._find_alias_id_for_species(ctx, modulation.source, frozenset_scope=fset)
            or ""
        )
        br_elem = _make("baseReactants", ns=_CD_NS)
        br_attrs = {
            "species": _writing.get_cd_species_id(modulation.source),
            "alias": source_alias,
        }
        br = _make("baseReactant", ns=_CD_NS, attributes=br_attrs)
        source_layout = cls._find_species_layout_from_frozenset(
            ctx, modulation.source, fset
        )
        if modulation_layout is not None and source_layout is not None:
            source_anchor = _writing.infer_anchor_name(
                source_layout, modulation_layout.points()[0]
            )
            if source_anchor != "center" and not has_boolean_input:
                position = _writing._ANCHOR_NAME_TO_LINK_ANCHOR_POSITION.get(
                    source_anchor
                )
                if position is not None:
                    la = _make(
                        "linkAnchor",
                        ns=_CD_NS,
                        attributes={"position": position},
                    )
                    br.append(la)
        br_elem.append(br)
        cd_ext.append(br_elem)
        target_alias = (
            cls._find_alias_id_for_species(ctx, modulation.target, frozenset_scope=fset)
            or ""
        )
        bp_elem = _make("baseProducts", ns=_CD_NS)
        bp_attrs = {
            "species": _writing.get_cd_species_id(modulation.target),
            "alias": target_alias,
        }
        bp = _make("baseProduct", ns=_CD_NS, attributes=bp_attrs)
        target_layout = cls._find_species_layout_from_frozenset(
            ctx, modulation.target, fset
        )
        if modulation_layout is not None and target_layout is not None:
            target_anchor = _writing.infer_anchor_name(
                target_layout, modulation_layout.points()[-1]
            )
            if target_anchor != "center":
                position = _writing._ANCHOR_NAME_TO_LINK_ANCHOR_POSITION.get(
                    target_anchor
                )
                if position is not None:
                    la = _make(
                        "linkAnchor",
                        ns=_CD_NS,
                        attributes={"position": position},
                    )
                    bp.append(la)
        bp_elem.append(bp)
        cd_ext.append(bp_elem)
        cd_ext.append(_make("listOfReactantLinks", ns=_CD_NS))
        cd_ext.append(_make("listOfProductLinks", ns=_CD_NS))
        n_edit_points = 0
        if (
            modulation_layout is not None
            and source_layout is not None
            and target_layout is not None
        ):
            edit_points, src_anchor, tgt_anchor = (
                _writing.inverse_edit_points_modulation(
                    modulation_layout,
                    source_layout,
                    target_layout,
                    has_boolean_input,
                )
            )
            n_edit_points = len(edit_points)
        else:
            edit_points = []
        cs = _make(
            "connectScheme",
            ns=_CD_NS,
            attributes={"connectPolicy": "direct", "rectangleIndex": "0"},
        )
        lld = _make("listOfLineDirection", ns=_CD_NS)
        for i in range(n_edit_points + 3):
            ld = _make(
                "lineDirection",
                ns=_CD_NS,
                attributes={"index": str(i), "value": "unknown"},
            )
            lld.append(ld)
        cs.append(lld)
        cd_ext.append(cs)
        if edit_points:
            if has_boolean_input:
                gate_pos = (
                    modulation.source.position
                    if hasattr(modulation.source, "position")
                    else momapy.geometry.Point(0, 0)
                )
                edit_points_text = edit_points + [gate_pos]
            else:
                edit_points_text = edit_points
            ep = _make(
                "editPoints",
                ns=_CD_NS,
                text=_writing.points_to_edit_points_text(edit_points_text),
            )
            cd_ext.append(ep)
        if has_boolean_input:
            gate_list = _make("listOfGateMember", ns=_CD_NS)
            gate_key = cls._CLASS_TO_KEY.get(type(modulation.source))
            gate_type = (
                gate_key[1] if gate_key is not None else "BOOLEAN_LOGIC_GATE_AND"
            )
            input_aliases = []
            for inp in modulation.source.inputs:
                alias_id = cls._find_alias_id_for_species(ctx, inp)
                if alias_id is not None:
                    input_aliases.append(alias_id)
            gm_attrs = {
                "type": gate_type,
                "aliases": ",".join(input_aliases),
                "modificationType": reaction_type,
            }
            gm = _make("GateMember", ns=_CD_NS, attributes=gm_attrs)
            gate_list.append(gm)
            cd_ext.append(gate_list)
        cd_ext.append(_make("listOfModification", ns=_CD_NS))
        line = cls._make_line_element(modulation_layout)
        cd_ext.append(line)
        annotation.append(cd_ext)
        if ctx.with_annotations:
            rdf = cls._make_rdf_for_element(ctx, modulation)
            if rdf is not None:
                annotation.append(rdf)
        rxn.append(annotation)
        reactants_elem = _make("listOfReactants")
        sr_attrs = {"species": _writing.get_cd_species_id(modulation.source)}
        sr = _make("speciesReference", attributes=sr_attrs)
        sr_ann = _make("annotation")
        sr_ext = _make("extension", ns=_CD_NS)
        sr_alias = _make("alias", ns=_CD_NS, text=source_alias)
        sr_ext.append(sr_alias)
        sr_ann.append(sr_ext)
        sr.append(sr_ann)
        reactants_elem.append(sr)
        rxn.append(reactants_elem)
        products_elem = _make("listOfProducts")
        pr_attrs = {"species": _writing.get_cd_species_id(modulation.target)}
        pr = _make("speciesReference", attributes=pr_attrs)
        pr_ann = _make("annotation")
        pr_ext = _make("extension", ns=_CD_NS)
        pr_alias = _make("alias", ns=_CD_NS, text=target_alias)
        pr_ext.append(pr_alias)
        pr_ann.append(pr_ext)
        pr.append(pr_ann)
        products_elem.append(pr)
        rxn.append(products_elem)
        return rxn

    @classmethod
    def _make_species_reference(cls, ctx, participant, tag, frozenset_scope=None):
        species = participant.referred_species
        attrs = {"species": _writing.get_cd_species_id(species)}
        if participant.metaid is not None:
            attrs["metaid"] = _unique_metaid(ctx, _xmlid(participant.metaid))
        sr = _make(tag, attributes=attrs)
        alias_id = cls._find_alias_id_for_species(
            ctx, species, frozenset_scope=frozenset_scope
        )
        ann = _make("annotation")
        ext = _make("extension", ns=_CD_NS)
        alias_elem = _make("alias", ns=_CD_NS, text=alias_id or "")
        ext.append(alias_elem)
        ann.append(ext)
        sr.append(ann)
        return sr

    @classmethod
    def _make_line_element(cls, layout_element, width=None, color=None):
        if layout_element is not None:
            path_stroke_width = getattr(layout_element, "path_stroke_width", None)
            if path_stroke_width is not None:
                w = str(path_stroke_width)
            else:
                w = width or "1.0"
            path_stroke = getattr(layout_element, "path_stroke", None)
            if path_stroke is not None and path_stroke is not momapy.drawing.NoneValue:
                c = _writing.color_to_cd_hex(path_stroke)
            else:
                c = color or "FF000000"
        else:
            w = width or "1.0"
            c = color or "FF000000"
        return _make(
            "line",
            ns=_CD_NS,
            attributes={"width": w, "color": c, "type": "Straight"},
        )

    # --- Helper methods for finding layouts/aliases ---

    @classmethod
    def _get_model_element(cls, ctx, layout_element):
        # Try direct mapping first (authoritative)
        if ctx.map_.layout_model_mapping is not None:
            result = ctx.map_.layout_model_mapping.get_mapping(layout_element)
            if result is not None:
                return result
        # Fall back to reverse lookup dict
        result = ctx.layout_to_model.get(layout_element)
        if result is not None:
            return result
        return result

    @classmethod
    def _find_reaction_layout(cls, ctx, reaction):
        if ctx.map_.layout is None:
            return None
        layouts = ctx.model_element_to_layout_elements.get(reaction)
        if layouts:
            for layout_key in layouts:
                if isinstance(layout_key, frozenset):
                    for elem in layout_key:
                        if isinstance(elem, momapy.celldesigner.core.ReactionLayout):
                            return elem
                elif isinstance(layout_key, momapy.celldesigner.core.ReactionLayout):
                    return layout_key
        # Fallback: search all layout elements
        for elem in ctx.map_.layout.layout_elements:
            if isinstance(elem, momapy.celldesigner.core.ReactionLayout):
                if elem.id_ == reaction.id_:
                    return elem
        return None

    @classmethod
    def _find_modulation_layout(cls, ctx, modulation):
        if ctx.map_.layout is None:
            return None
        layouts = ctx.model_element_to_layout_elements.get(modulation)
        if layouts:
            for layout_key in layouts:
                if isinstance(layout_key, frozenset):
                    for elem in layout_key:
                        if (
                            isinstance(
                                elem,
                                momapy.celldesigner.core.CellDesignerSingleHeadedArc,
                            )
                            and not isinstance(
                                elem, momapy.celldesigner.core.ConsumptionLayout
                            )
                            and not isinstance(
                                elem, momapy.celldesigner.core.ProductionLayout
                            )
                        ):
                            return elem
                elif isinstance(
                    layout_key,
                    momapy.celldesigner.core.CellDesignerSingleHeadedArc,
                ):
                    return layout_key
        # Fallback
        for elem in ctx.map_.layout.layout_elements:
            if hasattr(elem, "id_") and elem.id_ == modulation.id_:
                return elem
        return None

    @classmethod
    def _find_species_layout_for_participant(cls, ctx, participant):
        species = participant.referred_species
        return cls._find_species_layout_by_id(ctx, species)

    @classmethod
    def _find_species_layout_by_id(cls, ctx, species):
        if ctx.map_.layout is None or species is None:
            return None
        # Use the mapping to find layout elements for this species
        if ctx.map_.layout_model_mapping is not None:
            result = ctx.map_.layout_model_mapping.get_mapping(species)
            if result is not None:
                if isinstance(result, list):
                    for item in result:
                        if isinstance(item, frozenset):
                            continue
                        if isinstance(item, momapy.celldesigner.core.CellDesignerNode):
                            return item
                    # If only frozensets, return first element from first frozenset
                    for item in result:
                        if isinstance(item, frozenset):
                            for elem in item:
                                if isinstance(
                                    elem,
                                    momapy.celldesigner.core.CellDesignerNode,
                                ):
                                    return elem
                elif isinstance(result, momapy.celldesigner.core.CellDesignerNode):
                    return result
            # Also check for tuples: (species, complex) mappings
            for layout_elem, model_elem in ctx.layout_to_model.items():
                if isinstance(layout_elem, frozenset):
                    continue
                me = model_elem[0] if isinstance(model_elem, tuple) else model_elem
                if me is species and isinstance(
                    layout_elem, momapy.celldesigner.core.CellDesignerNode
                ):
                    return layout_elem
        return None

    @classmethod
    def _find_alias_id_for_species(cls, ctx, species, frozenset_scope=None):
        """Find the alias ID for a species.

        Args:
            ctx: WritingContext.
            species: The species model element.
            frozenset_scope: Optional frozenset to restrict the search to
                sibling layout elements within that frozenset.

        Returns:
            The alias ID string, or None.
        """
        if species is None:
            return None
        if frozenset_scope is not None:
            for elem in frozenset_scope:
                if not isinstance(elem, momapy.celldesigner.core.CellDesignerNode):
                    continue
                me = ctx.layout_to_model.get(elem)
                if me is not None:
                    me = me[0] if isinstance(me, tuple) else me
                    if me is species:
                        alias_id = getattr(elem, "id_", None)
                        if alias_id is not None:
                            return _sid(alias_id)
        for layout_elem, model_elem in ctx.layout_to_model.items():
            me = model_elem[0] if isinstance(model_elem, tuple) else model_elem
            if me is species:
                if isinstance(layout_elem, frozenset):
                    continue
                alias_id = getattr(layout_elem, "id_", None)
                if alias_id is not None:
                    return _sid(alias_id)
        return None

    @classmethod
    def _find_species_layout_from_frozenset(cls, ctx, species, fset):
        """Find the species layout for a species within a frozenset scope.

        Falls back to _find_species_layout_by_id if fset is None or
        the species is not found in the frozenset.

        Args:
            ctx: WritingContext.
            species: The species model element.
            fset: Optional frozenset to search within.

        Returns:
            A CellDesignerNode layout element, or None.
        """
        if fset is not None:
            for elem in fset:
                if not isinstance(elem, momapy.celldesigner.core.CellDesignerNode):
                    continue
                me = ctx.layout_to_model.get(elem)
                if me is not None:
                    me = me[0] if isinstance(me, tuple) else me
                    if me is species:
                        return elem
        return cls._find_species_layout_by_id(ctx, species)

    @classmethod
    def _find_frozenset_for_layout(cls, ctx, layout_element):
        """Find the frozenset in layout_model_mapping containing layout_element.

        Args:
            ctx: WritingContext.
            layout_element: A layout element to search for.

        Returns:
            The frozenset containing the element, or None.
        """
        if ctx.map_.layout_model_mapping is None:
            return None
        for key in ctx.map_.layout_model_mapping:
            if isinstance(key, frozenset) and layout_element in key:
                return key
        return None

    @classmethod
    def _split_base_and_links(
        cls, ctx, participants, reaction_layout, n_base, is_reactant
    ):
        """Split participants into base and link using layout proximity.

        The base reactant is the one whose species layout is closest to
        the start of the reaction layout path; the base product is closest
        to the end.  Falls back to sorted order if no layout is available.

        Args:
            ctx: WritingContext.
            participants: Sorted list of Reactant/Product model elements.
            reaction_layout: The reaction layout, or None.
            n_base: Number of base participants expected.
            is_reactant: True for reactants (match start), False for products
                (match end).

        Returns:
            Tuple of (base_list, link_list).
        """
        if reaction_layout is None or len(participants) <= n_base:
            return participants[:n_base], participants[n_base:]
        ref_point = (
            reaction_layout.points()[0] if is_reactant else reaction_layout.points()[-1]
        )
        scored = []
        for p in participants:
            layout = cls._find_species_layout_for_participant(ctx, p)
            if layout is not None:
                c = layout.center()
                dist = ((c.x - ref_point.x) ** 2 + (c.y - ref_point.y) ** 2) ** 0.5
            else:
                dist = float("inf")
            scored.append((dist, p))
        scored.sort(key=lambda x: x[0])
        base = [p for _, p in scored[:n_base]]
        link = [p for _, p in scored[n_base:]]
        return base, link

    @classmethod
    def _order_modifiers_by_layout(cls, ctx, reaction, reaction_layout):
        """Order modifiers to match CD listOfModification layout order.

        CellDesigner matches SBML listOfModifiers entries to CD
        listOfModification entries by index, so they must be in the
        same order.

        Args:
            ctx: WritingContext.
            reaction: The reaction model element.
            reaction_layout: The reaction layout, or None.

        Returns:
            List of modifier model elements in layout order.
        """
        if reaction_layout is None:
            return sorted(reaction.modifiers, key=lambda m: m.id_ or "")
        # Build ordered list from layout children
        ordered = []
        seen = set()
        for child in reaction_layout.layout_elements:
            if cls._is_modifier_layout(child):
                model_info = ctx.layout_to_model.get(child)
                if model_info is not None:
                    modifier_model = (
                        model_info[0] if isinstance(model_info, tuple) else model_info
                    )
                    if modifier_model not in seen:
                        seen.add(modifier_model)
                        ordered.append(modifier_model)
        # Append any modifiers not found in layout (fallback)
        for modifier in sorted(reaction.modifiers, key=lambda m: m.id_ or ""):
            if modifier not in seen:
                seen.add(modifier)
                ordered.append(modifier)
        return ordered

    @classmethod
    def _find_species_at_start(cls, ctx, arc_layout):
        """Find the species layout at the start of an arc."""
        start_point = arc_layout.points()[0]
        return cls._find_species_near_point(ctx, start_point)

    @classmethod
    def _find_species_at_end(cls, ctx, arc_layout):
        """Find the species layout at the end of an arc."""
        end_point = arc_layout.points()[-1]
        return cls._find_species_near_point(ctx, end_point)

    @classmethod
    def _find_species_near_point(cls, ctx, point, tol=5.0):
        """Find a species layout whose border is near the given point."""
        if ctx.map_.layout is None:
            return None
        best = None
        best_dist = float("inf")
        for elem in ctx.map_.layout.layout_elements:
            if cls._is_species_layout(elem):
                center = elem.center()
                dist = ((center.x - point.x) ** 2 + (center.y - point.y) ** 2) ** 0.5
                if dist < best_dist:
                    best_dist = dist
                    best = elem
        return best

    @classmethod
    def _find_base_consumption_layouts(cls, ctx, reaction_layout, base_reactants):
        """Find consumption layouts for base reactants in T-shape.

        Matches each base reactant to its consumption layout by finding
        the consumption whose start point is closest to the species layout.
        """
        consumptions = [
            child
            for child in reaction_layout.layout_elements
            if isinstance(child, momapy.celldesigner.core.ConsumptionLayout)
        ]
        result = []
        used = set()
        for reactant in base_reactants:
            species = reactant.referred_species
            species_layout = cls._find_species_layout_by_id(ctx, species)
            best = None
            best_dist = float("inf")
            for i, consumption in enumerate(consumptions):
                if i in used:
                    continue
                if species_layout is not None:
                    start = consumption.points()[0]
                    center = species_layout.center()
                    dist = (
                        (start.x - center.x) ** 2 + (start.y - center.y) ** 2
                    ) ** 0.5
                    if dist < best_dist:
                        best_dist = dist
                        best = (i, consumption)
            if best is not None:
                used.add(best[0])
                result.append(best[1])
            else:
                result.append(None)
        return result

    @classmethod
    def _find_base_production_layouts(cls, ctx, reaction_layout, base_products):
        """Find production layouts for base products in T-shape."""
        productions = [
            child
            for child in reaction_layout.layout_elements
            if isinstance(child, momapy.celldesigner.core.ProductionLayout)
        ]
        result = []
        used = set()
        for product in base_products:
            species = product.referred_species
            species_layout = cls._find_species_layout_by_id(ctx, species)
            best = None
            best_dist = float("inf")
            for i, production in enumerate(productions):
                if i in used:
                    continue
                if species_layout is not None:
                    end = production.points()[-1]
                    center = species_layout.center()
                    dist = ((end.x - center.x) ** 2 + (end.y - center.y) ** 2) ** 0.5
                    if dist < best_dist:
                        best_dist = dist
                        best = (i, production)
            if best is not None:
                used.add(best[0])
                result.append(best[1])
            else:
                result.append(None)
        return result

    @classmethod
    def _find_modification_angle(cls, ctx, residue, template):
        """Find the CellDesigner angle for a modification residue.

        Searches for a species layout that uses this template, finds the
        ModificationLayout child corresponding to the residue, and computes
        the CellDesigner angle from its position.
        """
        if ctx.map_.layout is None or ctx.map_.model is None:
            return None

        def _try_species(species):
            species_layout = cls._find_species_layout_by_id(ctx, species)
            if species_layout is None:
                return None
            mod_children = [
                c
                for c in species_layout.layout_elements
                if isinstance(c, momapy.celldesigner.core.ModificationLayout)
            ]
            sorted_residues = sorted(
                template.modification_residues, key=lambda r: r.id_ or ""
            )
            for i, r in enumerate(sorted_residues):
                if r is residue and i < len(mod_children):
                    return _writing.compute_cd_angle(
                        mod_children[i].position, species_layout
                    )
            return None

        # Search top-level species
        for species in ctx.map_.model.species:
            if getattr(species, "template", None) is template:
                result = _try_species(species)
                if result is not None:
                    return result
            # Search subunits
            if hasattr(species, "subunits"):
                for sub in species.subunits:
                    if getattr(sub, "template", None) is template:
                        result = _try_species(sub)
                        if result is not None:
                            return result
        return None

    # --- Annotation and notes helpers ---

    @classmethod
    def _make_rdf_for_element(cls, ctx, element):
        element_annotations = ctx.annotations.get(element)
        if element_annotations is None or not element_annotations:
            return None
        rdf = lxml.etree.Element(f"{{{_RDF_NS}}}RDF", nsmap=_RDF_NSMAP)
        element_id = ""
        if hasattr(element, "id_") and element.id_ is not None:
            element_id = element.id_
        elif hasattr(element, "metaid") and element.metaid is not None:
            element_id = element.metaid
        desc = lxml.etree.SubElement(
            rdf,
            f"{{{_RDF_NS}}}Description",
            {f"{{{_RDF_NS}}}about": f"#{element_id}"},
        )
        for annotation in element_annotations:
            namespace, tag = (
                momapy.sbml.io.sbml._qualifiers.QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE[
                    annotation.qualifier
                ]
            )
            bq = lxml.etree.SubElement(desc, f"{{{namespace}}}{tag}")
            bag = lxml.etree.SubElement(bq, f"{{{_RDF_NS}}}Bag")
            for resource in sorted(annotation.resources):
                lxml.etree.SubElement(
                    bag,
                    f"{{{_RDF_NS}}}li",
                    {f"{{{_RDF_NS}}}resource": resource},
                )
        return rdf

    @classmethod
    def _make_notes_for_element(cls, ctx, element):
        element_notes = ctx.notes.get(element)
        if element_notes is None or not element_notes:
            return None
        notes_elem = _make("notes")
        for note in element_notes:
            try:
                root = lxml.etree.fromstring(note)
                notes_elem.append(root)
            except lxml.etree.XMLSyntaxError:
                # If the note is not valid XML, wrap in html
                html = lxml.etree.SubElement(
                    notes_elem,
                    f"{{{_XHTML_NS}}}html",
                )
                body = lxml.etree.SubElement(html, f"{{{_XHTML_NS}}}body")
                body.text = note
        return notes_elem
