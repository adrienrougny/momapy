"""CellDesigner reader class."""

import os
import collections
import dataclasses
import math
import typing

import frozendict
import lxml.objectify

import momapy.core
import momapy.core.mapping
import momapy.core.layout
import momapy.geometry
import momapy.drawing
import momapy.io.core
import momapy.coloring
import momapy.builder
import momapy.celldesigner.core
import momapy.sbml.core
import momapy.utils

import momapy.celldesigner.io.celldesigner._parsing
import momapy.celldesigner.io.celldesigner._model
import momapy.celldesigner.io.celldesigner._layout


@dataclasses.dataclass
class ReadingContext:
    """Bundles the shared state passed across all reader coordinator methods."""

    cd_model: typing.Any
    model: typing.Any
    layout: typing.Any
    cd_id_to_model_element: dict
    cd_id_to_layout_element: dict
    cd_id_to_cd_element: dict
    cd_complex_alias_id_to_cd_included_species_ids: dict
    map_element_to_annotations: dict
    map_element_to_notes: dict
    layout_model_mapping: typing.Any
    id_to_map_element: typing.Any
    with_annotations: bool
    with_notes: bool


class CellDesignerReader(momapy.io.core.Reader):
    """Class for CellDesigner reader objects"""

    _KEY_TO_CLASS = {
        (
            "TEMPLATE",
            "GENERIC",
        ): momapy.celldesigner.core.GenericProteinTemplate,
        (
            "TEMPLATE",
            "ION_CHANNEL",
        ): momapy.celldesigner.core.IonChannelTemplate,
        ("TEMPLATE", "RECEPTOR"): momapy.celldesigner.core.ReceptorTemplate,
        (
            "TEMPLATE",
            "TRUNCATED",
        ): momapy.celldesigner.core.TruncatedProteinTemplate,
        ("TEMPLATE", "GENE"): momapy.celldesigner.core.GeneTemplate,
        ("TEMPLATE", "RNA"): momapy.celldesigner.core.RNATemplate,
        (
            "TEMPLATE",
            "ANTISENSE_RNA",
        ): momapy.celldesigner.core.AntisenseRNATemplate,
        ("SPECIES", "GENERIC"): (
            momapy.celldesigner.core.GenericProtein,
            momapy.celldesigner.core.GenericProteinLayout,
        ),
        ("SPECIES", "ION_CHANNEL"): (
            momapy.celldesigner.core.IonChannel,
            momapy.celldesigner.core.IonChannelLayout,
        ),
        ("SPECIES", "RECEPTOR"): (
            momapy.celldesigner.core.Receptor,
            momapy.celldesigner.core.ReceptorLayout,
        ),
        ("SPECIES", "TRUNCATED"): (
            momapy.celldesigner.core.TruncatedProtein,
            momapy.celldesigner.core.TruncatedProteinLayout,
        ),
        ("SPECIES", "GENE"): (
            momapy.celldesigner.core.Gene,
            momapy.celldesigner.core.GeneLayout,
        ),
        ("SPECIES", "RNA"): (
            momapy.celldesigner.core.RNA,
            momapy.celldesigner.core.RNALayout,
        ),
        ("SPECIES", "ANTISENSE_RNA"): (
            momapy.celldesigner.core.AntisenseRNA,
            momapy.celldesigner.core.AntisenseRNALayout,
        ),
        ("SPECIES", "PHENOTYPE"): (
            momapy.celldesigner.core.Phenotype,
            momapy.celldesigner.core.PhenotypeLayout,
        ),
        ("SPECIES", "ION"): (
            momapy.celldesigner.core.Ion,
            momapy.celldesigner.core.IonLayout,
        ),
        ("SPECIES", "SIMPLE_MOLECULE"): (
            momapy.celldesigner.core.SimpleMolecule,
            momapy.celldesigner.core.SimpleMoleculeLayout,
        ),
        ("SPECIES", "DRUG"): (
            momapy.celldesigner.core.Drug,
            momapy.celldesigner.core.DrugLayout,
        ),
        ("SPECIES", "COMPLEX"): (
            momapy.celldesigner.core.Complex,
            momapy.celldesigner.core.ComplexLayout,
        ),
        ("SPECIES", "UNKNOWN"): (
            momapy.celldesigner.core.Unknown,
            momapy.celldesigner.core.UnknownLayout,
        ),
        ("SPECIES", "DEGRADED"): (
            momapy.celldesigner.core.Degraded,
            momapy.celldesigner.core.DegradedLayout,
        ),
        ("REACTION", "STATE_TRANSITION"): (
            momapy.celldesigner.core.StateTransition,
            momapy.celldesigner.core.StateTransitionLayout,
        ),
        ("REACTION", "KNOWN_TRANSITION_OMITTED"): (
            momapy.celldesigner.core.KnownTransitionOmitted,
            momapy.celldesigner.core.KnownTransitionOmittedLayout,
        ),
        ("REACTION", "UNKNOWN_TRANSITION"): (
            momapy.celldesigner.core.UnknownTransition,
            momapy.celldesigner.core.UnknownTransitionLayout,
        ),
        ("REACTION", "TRANSCRIPTION"): (
            momapy.celldesigner.core.Transcription,
            momapy.celldesigner.core.TranscriptionLayout,
        ),
        ("REACTION", "TRANSLATION"): (
            momapy.celldesigner.core.Translation,
            momapy.celldesigner.core.TranslationLayout,
        ),
        ("REACTION", "TRANSPORT"): (
            momapy.celldesigner.core.Transport,
            momapy.celldesigner.core.TransportLayout,
        ),
        ("REACTION", "HETERODIMER_ASSOCIATION"): (
            momapy.celldesigner.core.HeterodimerAssociation,
            momapy.celldesigner.core.HeterodimerAssociationLayout,
        ),
        ("REACTION", "DISSOCIATION"): (
            momapy.celldesigner.core.Dissociation,
            momapy.celldesigner.core.DissociationLayout,
        ),
        ("REACTION", "TRUNCATION"): (
            momapy.celldesigner.core.Truncation,
            momapy.celldesigner.core.TruncationLayout,
        ),
        ("REACTION", "CATALYSIS"): (
            momapy.celldesigner.core.Catalysis,
            momapy.celldesigner.core.CatalysisLayout,
        ),
        ("REACTION", "UNKNOWN_CATALYSIS"): (
            momapy.celldesigner.core.UnknownCatalysis,
            momapy.celldesigner.core.UnknownCatalysisLayout,
        ),
        ("REACTION", "INHIBITION"): (
            momapy.celldesigner.core.Inhibition,
            momapy.celldesigner.core.InhibitionLayout,
        ),
        ("REACTION", "UNKNOWN_INHIBITION"): (
            momapy.celldesigner.core.UnknownInhibition,
            momapy.celldesigner.core.UnknownInhibitionLayout,
        ),
        ("REACTION", "PHYSICAL_STIMULATION"): (
            momapy.celldesigner.core.PhysicalStimulation,
            momapy.celldesigner.core.PhysicalStimulationLayout,
        ),
        ("REACTION", "MODULATION"): (
            momapy.celldesigner.core.Modulation,
            momapy.celldesigner.core.ModulationLayout,
        ),
        ("REACTION", "TRIGGER"): (
            momapy.celldesigner.core.Triggering,
            momapy.celldesigner.core.TriggeringLayout,
        ),
        ("REACTION", "POSITIVE_INFLUENCE"): (
            momapy.celldesigner.core.PositiveInfluence,
            momapy.celldesigner.core.PositiveInfluenceLayout,
        ),
        ("REACTION", "UNKNOWN_POSITIVE_INFLUENCE"): (
            momapy.celldesigner.core.UnknownPositiveInfluence,
            momapy.celldesigner.core.UnknownPositiveInfluenceLayout,
        ),
        ("REACTION", "NEGATIVE_INFLUENCE"): (
            momapy.celldesigner.core.NegativeInfluence,
            momapy.celldesigner.core.momapy.celldesigner.core.InhibitionLayout,
        ),
        ("REACTION", "UNKNOWN_NEGATIVE_INFLUENCE"): (
            momapy.celldesigner.core.UnknownNegativeInfluence,
            momapy.celldesigner.core.UnknownInhibitionLayout,
        ),
        ("REACTION", "REDUCED_PHYSICAL_STIMULATION"): (
            momapy.celldesigner.core.PhysicalStimulation,
            momapy.celldesigner.core.PhysicalStimulationLayout,
        ),
        ("REACTION", "UNKNOWN_REDUCED_PHYSICAL_STIMULATION"): (
            momapy.celldesigner.core.UnknownPhysicalStimulation,
            momapy.celldesigner.core.UnknownPhysicalStimulationLayout,
        ),
        ("REACTION", "REDUCED_MODULATION"): (
            momapy.celldesigner.core.Modulation,
            momapy.celldesigner.core.ModulationLayout,
        ),
        ("REACTION", "UNKNOWN_REDUCED_MODULATION"): (
            momapy.celldesigner.core.UnknownModulation,
            momapy.celldesigner.core.UnknownModulationLayout,
        ),
        ("REACTION", "REDUCED_TRIGGER"): (
            momapy.celldesigner.core.Triggering,
            momapy.celldesigner.core.TriggeringLayout,
        ),
        ("REACTION", "UNKNOWN_REDUCED_TRIGGER"): (
            momapy.celldesigner.core.UnknownTriggering,
            momapy.celldesigner.core.UnknownTriggeringLayout,
        ),
        ("MODIFIER", "CATALYSIS"): (
            momapy.celldesigner.core.Catalyzer,
            momapy.celldesigner.core.CatalysisLayout,
        ),
        ("MODIFIER", "UNKNOWN_CATALYSIS"): (
            momapy.celldesigner.core.UnknownCatalyzer,
            momapy.celldesigner.core.UnknownCatalysisLayout,
        ),
        ("MODIFIER", "INHIBITION"): (
            momapy.celldesigner.core.Inhibitor,
            momapy.celldesigner.core.InhibitionLayout,
        ),
        ("MODIFIER", "UNKNOWN_INHIBITION"): (
            momapy.celldesigner.core.UnknownInhibitor,
            momapy.celldesigner.core.UnknownInhibitionLayout,
        ),
        ("MODIFIER", "PHYSICAL_STIMULATION"): (
            momapy.celldesigner.core.PhysicalStimulator,
            momapy.celldesigner.core.PhysicalStimulationLayout,
        ),
        ("MODIFIER", "MODULATION"): (
            momapy.celldesigner.core.Modulator,
            momapy.celldesigner.core.ModulationLayout,
        ),
        ("MODIFIER", "TRIGGER"): (
            momapy.celldesigner.core.Trigger,
            momapy.celldesigner.core.TriggeringLayout,
        ),
        ("MODIFIER", "POSITIVE_INFLUENCE"): (  # older version?
            momapy.celldesigner.core.PositiveInfluence,
            momapy.celldesigner.core.PositiveInfluenceLayout,
        ),
        ("MODIFIER", "NEGATIVE_INFLUENCE"): (  # older version?
            momapy.celldesigner.core.NegativeInfluence,
            momapy.celldesigner.core.InhibitionLayout,
        ),
        ("GATE", "BOOLEAN_LOGIC_GATE_AND"): (
            momapy.celldesigner.core.AndGate,
            momapy.celldesigner.core.AndGateLayout,
        ),
        ("GATE", "BOOLEAN_LOGIC_GATE_OR"): (
            momapy.celldesigner.core.OrGate,
            momapy.celldesigner.core.OrGateLayout,
        ),
        ("GATE", "BOOLEAN_LOGIC_GATE_NOT"): (
            momapy.celldesigner.core.NotGate,
            momapy.celldesigner.core.NotGateLayout,
        ),
        (
            "GATE",
            "BOOLEAN_LOGIC_GATE_UNKNOWN",
        ): (
            momapy.celldesigner.core.UnknownGate,
            momapy.celldesigner.core.UnknownGateLayout,
        ),
        (
            "REGION",
            "Modification Site",
        ): momapy.celldesigner.core.ModificationSite,
        (
            "REGION",
            "RegulatoryRegion",
        ): momapy.celldesigner.core.RegulatoryRegion,
        (
            "REGION",
            "transcriptionStartingSiteL",
        ): momapy.celldesigner.core.TranscriptionStartingSiteL,
        (
            "REGION",
            "transcriptionStartingSiteR",
        ): momapy.celldesigner.core.TranscriptionStartingSiteR,
        (
            "REGION",
            "CodingRegion",
        ): momapy.celldesigner.core.CodingRegion,
        (
            "REGION",
            "proteinBindingDomain",
        ): momapy.celldesigner.core.ProteinBindingDomain,
    }

    @classmethod
    def check_file(cls, file_path: str | os.PathLike):
        """Return `true` if the file is a CellDesigner file, `false` otherwise"""
        try:
            with open(file_path) as f:
                for line in f:
                    if "http://www.sbml.org/2001/ns/celldesigner" in line:
                        return True
            return False
        except Exception:
            return False

    @classmethod
    def read(
        cls,
        file_path: str | os.PathLike,
        return_type: typing.Literal["map", "model", "layout"] = "map",
        with_model=True,
        with_layout=True,
        with_annotations=True,
        with_notes=True,
    ) -> momapy.io.core.ReaderResult:
        """Read a CellDesigner file and return a reader result object"""
        cd_document = lxml.objectify.parse(file_path)
        cd_sbml = cd_document.getroot()
        obj, annotations, notes, ids = cls._make_main_obj(
            cd_model=cd_sbml.model,
            return_type=return_type,
            with_model=with_model,
            with_layout=with_layout,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        result = momapy.io.core.ReaderResult(
            obj=obj,
            notes=notes,
            annotations=annotations,
            file_path=file_path,
            ids=ids,
        )
        return result

    @classmethod
    def _make_main_obj(
        cls,
        cd_model,
        return_type: typing.Literal["map", "model", "layout"] = "map",
        with_model=True,
        with_layout=True,
        with_annotations=True,
        with_notes=True,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _model = momapy.celldesigner.io.celldesigner._model
        _layout = momapy.celldesigner.io.celldesigner._layout
        if return_type == "model" or return_type == "map" and with_model:
            model = _model.make_empty_model(cd_model)
        else:
            model = None
        if return_type == "layout" or return_type == "map" and with_layout:
            layout = _layout.make_empty_layout(cd_model)
        else:
            layout = None
        if model is not None or layout is not None:
            cd_id_to_cd_element = _parsing.make_id_to_element_mapping(cd_model)
            cd_complex_alias_id_to_cd_included_species_ids = (
                _parsing.make_complex_alias_to_included_ids_mapping(cd_model)
            )
            cd_id_to_model_element = {}
            cd_id_to_layout_element = {}
            map_element_to_annotations = collections.defaultdict(set)
            id_to_map_element = momapy.utils.SurjectionDict()
            map_element_to_notes = collections.defaultdict(set)
            if model is not None and layout is not None:
                layout_model_mapping = momapy.core.mapping.LayoutModelMappingBuilder()
            else:
                layout_model_mapping = None
            ctx = ReadingContext(
                cd_model=cd_model,
                model=model,
                layout=layout,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                layout_model_mapping=layout_model_mapping,
                id_to_map_element=id_to_map_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
            # we make and add the  model and layout elements from the cd elements
            # we start with the compartment aliases
            cls._make_and_add_compartments(ctx)
            # we make and add the species templates
            cls._make_and_add_species_templates(ctx)
            # we make and add the species, from the species aliases
            # species aliases are the glyphs; in terms of model, a species is almost
            # a model element on its own: the only attribute that is not on the
            # species but on the species alias is the activity (active or inactive);
            # hence two species aliases can be associated to only one species
            # but correspond to two different layout elements; we do not make the
            # species that are included, they are made when we make their
            # containing complex, but we make complexes
            cls._make_and_add_all_species(ctx)
            # we make and add the reactions and modulations from celldesigner
            # reactions: a celldesigner reaction is either a true reaction
            # or a false reaction encoding a modulation
            cls._make_and_add_reactions_and_modulations(ctx)
            if layout is not None:
                _layout.set_layout_size_and_position(cd_model, layout)
        if return_type == "model":
            obj = momapy.builder.object_from_builder(model)
            if with_annotations:
                annotations = _model.make_annotations_from_element(cd_model)
                map_element_to_annotations[obj].update(annotations)
            if with_notes:
                notes = _model.make_notes(cd_model)
                map_element_to_notes[obj].update(notes)
        elif return_type == "layout":
            obj = momapy.builder.object_from_builder(layout)
        elif return_type == "map":
            map_ = _model.make_empty_map(cd_model)
            map_.model = model
            map_.layout = layout
            map_.layout_model_mapping = layout_model_mapping
            obj = momapy.builder.object_from_builder(map_)
            if with_annotations:
                annotations = _model.make_annotations_from_element(cd_model)
                map_element_to_annotations[obj].update(annotations)
            if with_notes:
                notes = _model.make_notes(cd_model)
                map_element_to_notes[obj].update(notes)
        annotations = frozendict.frozendict(
            {key: frozenset(val) for key, val in map_element_to_annotations.items()}
        )
        notes = frozendict.frozendict(
            {key: frozenset(val) for key, val in map_element_to_notes.items()}
        )
        ids = momapy.utils.FrozenSurjectionDict(id_to_map_element)
        return obj, annotations, notes, ids

    @classmethod
    def _make_and_add_compartments(cls, ctx):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        cd_compartment_aliases = _parsing.get_ordered_compartment_aliases(
            ctx.cd_model, ctx.cd_id_to_cd_element
        )
        for cd_compartment_alias in cd_compartment_aliases:
            model_element, layout_element = (
                cls._make_and_add_compartment_from_alias(
                    ctx,
                    cd_compartment_alias=cd_compartment_alias,
                )
            )
        # we also make the compartments from the list of compartments that do not have
        # an alias (e.g., the "default" compartment)
        # since these have no alias, we only produce a model element
        for cd_compartment in _parsing.get_compartments(ctx.cd_model):
            if cd_compartment.get("id") not in ctx.cd_id_to_model_element:
                model_element, layout_element = (
                    cls._make_and_add_compartment(
                        ctx,
                        cd_compartment=cd_compartment,
                    )
                )

    @classmethod
    def _make_and_add_compartment_from_alias(
        cls,
        ctx,
        cd_compartment_alias,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _model = momapy.celldesigner.io.celldesigner._model
        _layout = momapy.celldesigner.io.celldesigner._layout
        if ctx.model is not None or ctx.layout is not None:
            cd_compartment = ctx.cd_id_to_cd_element[
                cd_compartment_alias.get("compartment")
            ]
            if ctx.model is not None:
                # we make and add the model element from the cd compartment
                # the cd element is an alias of, if it has not already been made
                # while being outside another one
                model_element = ctx.cd_id_to_model_element.get(cd_compartment.get("id"))
                if model_element is None:
                    model_element, _ = (
                        cls._make_and_add_compartment(
                            ctx,
                            cd_compartment=cd_compartment,
                        )
                    )
            else:
                model_element = None
            if ctx.layout is not None:
                if getattr(cd_compartment_alias, "class").text == "OVAL":
                    layout_element_cls = momapy.celldesigner.core.OvalCompartmentLayout
                else:
                    layout_element_cls = (
                        momapy.celldesigner.core.RectangleCompartmentLayout
                    )
                layout_element = ctx.layout.new_element(layout_element_cls)
                layout_element.id_ = cd_compartment_alias.get("id")
                cd_x = float(cd_compartment_alias.bounds.get("x"))
                cd_y = float(cd_compartment_alias.bounds.get("y"))
                cd_w = float(cd_compartment_alias.bounds.get("w"))
                cd_h = float(cd_compartment_alias.bounds.get("h"))
                layout_element.position = momapy.geometry.Point(
                    cd_x + cd_w / 2, cd_y + cd_h / 2
                )
                layout_element.width = cd_w
                layout_element.height = cd_h
                layout_element.inner_stroke_width = float(
                    cd_compartment_alias.doubleLine.get("innerWidth")
                )
                layout_element.stroke_width = float(
                    cd_compartment_alias.doubleLine.get("outerWidth")
                )
                layout_element.sep = float(
                    cd_compartment_alias.doubleLine.get("thickness")
                )
                cd_compartment_alias_color = cd_compartment_alias.paint.get("color")
                cd_compartment_alias_color = (
                    cd_compartment_alias_color[2:] + cd_compartment_alias_color[:2]
                )
                element_color = momapy.coloring.Color.from_hexa(
                    cd_compartment_alias_color
                )
                layout_element.stroke = element_color
                layout_element.inner_stroke = element_color
                layout_element.fill = element_color.with_alpha(0.5)
                layout_element.inner_fill = momapy.coloring.white
                text = _parsing.make_name(cd_compartment.get("name"))
                text_position = momapy.geometry.Point(
                    float(cd_compartment_alias.namePoint.get("x")),
                    float(cd_compartment_alias.namePoint.get("y")),
                )
                text_layout = momapy.core.layout.TextLayout(
                    text=text,
                    font_size=_layout._DEFAULT_FONT_SIZE,
                    font_family=_layout._DEFAULT_FONT_FAMILY,
                    fill=_layout._DEFAULT_FONT_FILL,
                    stroke=momapy.drawing.NoneValue,
                    position=text_position,
                )
                layout_element.label = text_layout
                layout_element = momapy.builder.object_from_builder(layout_element)
                ctx.layout.layout_elements.append(layout_element)
                ctx.cd_id_to_layout_element[cd_compartment_alias.get("id")] = layout_element
                ctx.id_to_map_element[cd_compartment_alias.get("id")] = layout_element
            else:
                layout_element = None
            if ctx.model is not None and ctx.layout is not None:
                ctx.layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
                )
        return model_element, layout_element

    @classmethod
    def _make_and_add_compartment(
        cls,
        ctx,
        cd_compartment,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _model = momapy.celldesigner.io.celldesigner._model
        if ctx.model is not None:
            model_element = ctx.model.new_element(momapy.celldesigner.core.Compartment)
            model_element.id_ = cd_compartment.get("id")
            model_element.name = _parsing.make_name(cd_compartment.get("name"))
            model_element.metaid = cd_compartment.get("metaid")
            if cd_compartment.get("outside") is not None:
                outside_model_element = ctx.cd_id_to_model_element.get(
                    cd_compartment.get("outside")
                )
                # if outside is not already made, we make it
                if outside_model_element is None:
                    cd_outside = ctx.cd_id_to_cd_element[cd_compartment.get("outside")]
                    outside_model_element, _ = (
                        cls._make_and_add_compartment(
                            ctx,
                            cd_compartment=cd_outside,
                        )
                    )
                model_element.outside = outside_model_element
            model_element = momapy.builder.object_from_builder(model_element)
            model_element = momapy.utils.add_or_replace_element_in_set(
                model_element,
                ctx.model.compartments,
                func=lambda element, existing_element: element.id_
                < existing_element.id_,
            )
            ctx.cd_id_to_model_element[cd_compartment.get("id")] = model_element
            ctx.id_to_map_element[cd_compartment.get("id")] = model_element
            if ctx.with_annotations:
                annotations = _model.make_annotations_from_element(cd_compartment)
                if annotations:
                    ctx.map_element_to_annotations[model_element].update(annotations)
            if ctx.with_notes:
                notes = _model.make_notes(cd_compartment)
                ctx.map_element_to_notes[model_element].update(notes)
        else:
            model_element = None
        layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_species_templates(cls, ctx):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        for cd_species_template in _parsing.get_species_templates(ctx.cd_model):
            model_element, layout_element = (
                cls._make_and_add_species_template(
                    ctx,
                    cd_species_template=cd_species_template,
                )
            )

    @classmethod
    def _make_and_add_species_template(
        cls,
        ctx,
        cd_species_template,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        if ctx.model is not None:
            key = _parsing.get_key_from_species_template(cd_species_template)
            model_element_cls = cls._KEY_TO_CLASS[key]
            model_element = ctx.model.new_element(model_element_cls)
            model_element.id_ = cd_species_template.get("id")
            model_element.name = _parsing.make_name(
                cd_species_template.get("name")
            )
            n_undefined_modification_residue_names = 0
            cd_modification_residues = (
                _parsing.get_modification_residues(cd_species_template)
            )
            cd_modification_residues.sort(
                key=lambda cd_modification_residue: cd_modification_residue.get("angle")
            )
            for cd_modification_residue in _parsing.get_modification_residues(
                cd_species_template
            ):
                if cd_modification_residue.get("name") is None:
                    n_undefined_modification_residue_names += 1
                    order = n_undefined_modification_residue_names
                else:
                    order = None
                modification_residue_model_element, _ = (
                    cls._make_and_add_modification_residue(
                        ctx,
                        cd_modification_residue=cd_modification_residue,
                        super_cd_element=cd_species_template,
                        super_model_element=model_element,
                        order=order,
                    )
                )
            n_undefined_region_names = 0
            cd_regions = _parsing.get_regions(cd_species_template)
            cd_regions.sort(key=lambda cd_region: cd_region.get("pos"))
            for cd_region in cd_regions:
                if cd_region.get("name") is None:
                    n_undefined_region_names += 1
                    order = n_undefined_region_names
                else:
                    order = None
                region_model_element, _ = cls._make_and_add_region(
                    ctx,
                    cd_region=cd_region,
                    super_cd_element=cd_species_template,
                    super_model_element=model_element,
                    order=order,
                )
            model_element = momapy.builder.object_from_builder(model_element)
            model_element = momapy.utils.add_or_replace_element_in_set(
                model_element,
                ctx.model.species_templates,
                func=lambda element, existing_element: element.id_
                < existing_element.id_,
            )
            ctx.cd_id_to_model_element[cd_species_template.get("id")] = model_element
            ctx.id_to_map_element[cd_species_template.get("id")] = model_element
        else:
            model_element = None
        layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_modification_residue(
        cls,
        ctx,
        cd_modification_residue,
        super_cd_element,
        super_model_element,
        order,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        if ctx.model is not None:
            model_element = ctx.model.new_element(
                momapy.celldesigner.core.ModificationResidue
            )
            # Defaults ids for modification residues are simple in CellDesigner (e.g.,
            # "rs1") and might be shared between residues of different species.
            # However we want a unique id, so we build it using the id of the
            # species as well.
            cd_modification_residue_id = (
                f"{super_cd_element.get('id')}_{cd_modification_residue.get('id')}"
            )
            model_element.id_ = cd_modification_residue_id
            model_element.name = _parsing.make_name(
                cd_modification_residue.get("name")
            )
            model_element.order = order
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.modification_residues.add(model_element)
            # exceptionally we take the model element's id and not the cd element's
            # id for the reasons explained above
            ctx.cd_id_to_model_element[cd_modification_residue_id] = model_element
            ctx.id_to_map_element[cd_modification_residue_id] = model_element
        else:
            model_element = None
        layout_element = None  # purely a model element
        return model_element, layout_element

    @classmethod
    def _make_and_add_region(
        cls,
        ctx,
        cd_region,
        super_cd_element,
        super_model_element,
        order,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        if ctx.model is not None:
            key = _parsing.get_key_from_region(cd_region)
            model_element_cls = cls._KEY_TO_CLASS[key]
            model_element = ctx.model.new_element(model_element_cls)
            # Defaults ids for regions are simple in CellDesigner (e.g.,
            # "rs1") and might be shared between regions of different species.
            # However we want a unique id, so we build it using the id of the
            # species as well.
            cd_region_id = f"{super_cd_element.get('id')}_{cd_region.get('id')}"
            model_element.id_ = cd_region_id
            model_element.name = _parsing.make_name(cd_region.get("name"))
            active = cd_region.get("active")
            if active is not None:
                model_element.active = True if active == "true" else False
            model_element.order = order
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.regions.add(model_element)
            # exceptionally we take the model element's id and not the cd element's
            # id for the reasons explained above
            ctx.cd_id_to_model_element[model_element.id_] = model_element
            ctx.id_to_map_element[cd_region_id] = model_element
        else:
            model_element = None
        layout_element = None  # purely a model element
        return model_element, layout_element

    @classmethod
    def _make_and_add_all_species(cls, ctx):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        for cd_species_alias in _parsing.get_species_aliases(
            ctx.cd_model
        ) + _parsing.get_complex_species_aliases(ctx.cd_model):
            model_element, layout_element = (
                cls._make_and_add_species(
                    ctx,
                    cd_species_alias=cd_species_alias,
                )
            )

    @classmethod
    def _make_and_add_species(
        cls,
        ctx,
        cd_species_alias,
        super_cd_element=None,
        super_model_element=None,
        super_layout_element=None,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _model = momapy.celldesigner.io.celldesigner._model
        _layout = momapy.celldesigner.io.celldesigner._layout
        if ctx.model is not None or ctx.layout is not None:
            cd_species = ctx.cd_id_to_cd_element[cd_species_alias.get("species")]
            key = _parsing.get_key_from_species(cd_species, ctx.cd_id_to_cd_element)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            name = _parsing.make_name(cd_species.get("name"))
            cd_species_homodimer = _parsing.get_homodimer(cd_species)
            if cd_species_homodimer is not None:
                homomultimer = int(cd_species_homodimer)
            else:
                homomultimer = 1
            cd_species_hypothetical = _parsing.get_hypothetical(cd_species)
            if cd_species_hypothetical is not None:
                hypothetical = cd_species_hypothetical.text == "true"
            else:
                hypothetical = False
            cd_species_activity = _parsing.get_activity(cd_species_alias)
            if cd_species_activity is not None:
                active = cd_species_activity.text == "active"
                if active:
                    cd_species.attrib["id"] = f"{cd_species.get('id')}_active"
            if ctx.model is not None:
                model_element = ctx.model.new_element(model_element_cls)
                model_element.id_ = cd_species.get("id")
                model_element.name = name
                model_element.metaid = cd_species.get("metaid")
                cd_compartment_id = cd_species.get("compartment")
                if cd_compartment_id is not None:
                    compartment_model_element = ctx.cd_id_to_model_element[
                        cd_compartment_id
                    ]
                    model_element.compartment = compartment_model_element
                cd_species_template = _parsing.get_template_from_species(
                    cd_species, ctx.cd_id_to_cd_element
                )
                if cd_species_template is not None:
                    model_element.template = ctx.cd_id_to_model_element[
                        cd_species_template.get("id")
                    ]
                model_element.homomultimer = homomultimer
                model_element.hypothetical = hypothetical
                model_element.active = active
            else:
                model_element = None
            if ctx.layout is not None:
                layout_element = ctx.layout.new_element(layout_element_cls)
                layout_element.id_ = cd_species_alias.get("id")
                cd_x, cd_y, cd_w, cd_h = _parsing.get_bounds(cd_species_alias)
                layout_element.position = momapy.geometry.Point(
                    float(cd_x) + float(cd_w) / 2,
                    float(cd_y) + float(cd_h) / 2,
                )
                layout_element.width = float(cd_w)
                layout_element.height = float(cd_h)
                text_layout = momapy.core.layout.TextLayout(
                    text=name,
                    font_size=float(cd_species_alias.font.get("size")),
                    font_family=_layout._DEFAULT_FONT_FAMILY,
                    fill=_layout._DEFAULT_FONT_FILL,
                    stroke=momapy.drawing.NoneValue,
                    position=layout_element.label_center(),
                )
                text_layout = momapy.builder.object_from_builder(text_layout)
                layout_element.label = text_layout
                layout_element.stroke_width = float(
                    cd_species_alias.usualView.singleLine.get("width")
                )
                cd_species_alias_fill_color = cd_species_alias.usualView.paint.get(
                    "color"
                )
                cd_species_alias_fill_color = (
                    cd_species_alias_fill_color[2:] + cd_species_alias_fill_color[:2]
                )
                layout_element.fill = momapy.coloring.Color.from_hexa(
                    cd_species_alias_fill_color
                )
                cd_species_activity = _parsing.get_activity(cd_species_alias)
                layout_element.active = active
                layout_element.n = homomultimer
            else:
                layout_element = None
            covered_cd_residue_ids = set()
            for cd_species_modification in _parsing.get_species_modifications(cd_species):
                covered_cd_residue_ids.add(cd_species_modification.get("residue"))
                modification_model_element, modification_layout_element = (
                    cls._make_and_add_species_modification(
                        ctx,
                        cd_species_modification=cd_species_modification,
                        super_cd_element=cd_species_alias,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
            cd_species_template = _parsing.get_template_from_species_alias(
                cd_species_alias, ctx.cd_id_to_cd_element
            )
            for cd_modification_residue in _parsing.get_modification_residues(
                cd_species_template
            ):
                residue_xml_id = cd_modification_residue.get("id")
                if residue_xml_id not in covered_cd_residue_ids:
                    cls._make_and_add_species_modification(
                        ctx,
                        cd_species_modification={
                            "state": "empty",
                            "residue": residue_xml_id,
                        },
                        super_cd_element=cd_species_alias,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
            for cd_species_structural_state in _parsing.get_species_structural_states(
                cd_species
            ):
                (
                    structural_state_model_element,
                    structural_state_layout_element,
                ) = cls._make_and_add_species_structural_state(
                    ctx,
                    cd_species_structural_state=cd_species_structural_state,
                    super_cd_element=cd_species_alias,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                )
            cd_subunits = [
                ctx.cd_id_to_cd_element[cd_subunit_id]
                for cd_subunit_id in ctx.cd_complex_alias_id_to_cd_included_species_ids[
                    cd_species_alias.get("id")
                ]
            ]
            for cd_subunit in cd_subunits:
                subunit_model_element, subunit_layout_element = (
                    cls._make_and_add_species(
                        ctx,
                        cd_species_alias=cd_subunit,
                        super_cd_element=cd_species_alias,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
            if ctx.model is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                if super_model_element is None:  # species case
                    model_element = momapy.utils.add_or_replace_element_in_set(
                        model_element,
                        ctx.model.species,
                        func=lambda element, existing_element: element.id_
                        < existing_element.id_,
                    )
                    if ctx.with_annotations:
                        annotations = _model.make_annotations_from_element(cd_species)
                        if annotations:
                            ctx.map_element_to_annotations[model_element].update(
                                annotations
                            )
                    if ctx.with_notes:
                        notes = _model.make_notes(cd_species)
                        ctx.map_element_to_notes[model_element].update(notes)
                else:  # included species case
                    super_model_element.subunits.add(model_element)
                    if ctx.with_annotations:
                        cd_notes = _parsing.get_notes(cd_species)
                        annotations = _model.make_annotations_from_notes(cd_notes)
                        if annotations:
                            ctx.map_element_to_annotations[model_element].update(
                                annotations
                            )
                    if ctx.with_notes:
                        notes = _model.make_notes(cd_species)
                        ctx.map_element_to_notes[model_element].update(notes)
                ctx.cd_id_to_model_element[cd_species.get("id")] = model_element
                ctx.cd_id_to_model_element[cd_species_alias.get("id")] = model_element
                ctx.id_to_map_element[cd_species.get("id")] = model_element
            if ctx.layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                if super_layout_element is None:  # species case
                    ctx.layout.layout_elements.append(layout_element)
                else:  # included species case
                    super_layout_element.layout_elements.append(layout_element)
                ctx.cd_id_to_layout_element[cd_species_alias.get("id")] = layout_element
                ctx.id_to_map_element[cd_species_alias.get("id")] = layout_element
            if ctx.model is not None and ctx.layout is not None:
                if super_layout_element is None:  # species case
                    ctx.layout_model_mapping.add_mapping(
                        layout_element, model_element, replace=True
                    )
                else:  # included species case
                    ctx.layout_model_mapping.add_mapping(
                        layout_element,
                        (model_element, super_model_element),
                        replace=True,
                    )
        return model_element, layout_element

    @classmethod
    def _make_and_add_species_modification(
        cls,
        ctx,
        cd_species_modification,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _layout = momapy.celldesigner.io.celldesigner._layout
        if ctx.model is not None or ctx.layout is not None:
            cd_species_modification_state = cd_species_modification.get("state")
            if cd_species_modification_state == "empty":
                modification_state = None
            else:
                modification_state = momapy.celldesigner.core.ModificationState[
                    cd_species_modification_state.upper()
                    .replace(" ", "_")  # for DON'T CARE
                    .replace("'", "_")
                ]
            cd_species_template = _parsing.get_template_from_species_alias(
                super_cd_element,
                ctx.cd_id_to_cd_element,
            )
            cd_modification_residue_id = f"{cd_species_template.get('id')}_{cd_species_modification.get('residue')}"
            if ctx.model is not None:
                model_element = ctx.model.new_element(momapy.celldesigner.core.Modification)
                modification_residue_model_element = ctx.cd_id_to_model_element[
                    cd_modification_residue_id
                ]
                model_element.residue = modification_residue_model_element
                model_element.state = modification_state
                model_element = momapy.builder.object_from_builder(model_element)
                super_model_element.modifications.add(model_element)
                ctx.cd_id_to_model_element[model_element.id_] = model_element
            else:
                model_element = None
            if ctx.layout is not None:
                layout_element = ctx.layout.new_element(
                    momapy.celldesigner.core.ModificationLayout
                )
                cd_modification_residue = ctx.cd_id_to_cd_element[
                    cd_modification_residue_id
                ]  # can also be of type ModificationSite for Genes, RNAs, etc.
                angle = cd_modification_residue.get("angle")
                if angle is None:
                    fraction = float(cd_modification_residue.get("pos"))
                    segment = momapy.geometry.Segment(
                        super_layout_element.north_west(),
                        super_layout_element.north_east(),
                    )
                    point = segment.get_position_at_fraction(fraction)
                    segment = momapy.geometry.Segment(
                        super_layout_element.center(), point
                    )
                    angle = -segment.get_angle_to_horizontal()
                else:
                    angle = float(angle)
                    point = momapy.geometry.Point(
                        super_layout_element.width * math.cos(angle),
                        super_layout_element.height * math.sin(angle),
                    )
                    angle = math.atan2(point.y, point.x)
                layout_element.position = super_layout_element.angle(
                    angle, unit="radians"
                )
                text = (
                    modification_state.value if modification_state is not None else ""
                )
                text_layout = momapy.core.layout.TextLayout(
                    text=text,
                    font_size=_layout._DEFAULT_MODIFICATION_FONT_SIZE,
                    font_family=_layout._DEFAULT_FONT_FAMILY,
                    fill=_layout._DEFAULT_FONT_FILL,
                    stroke=momapy.drawing.NoneValue,
                    position=layout_element.label_center(),
                )
                layout_element.label = text_layout
                cd_modification_residue_name = cd_modification_residue.get("name")
                if cd_modification_residue_name is not None:
                    residue_text_layout = ctx.layout.new_element(
                        momapy.core.layout.TextLayout
                    )
                    residue_text_layout.text = cd_modification_residue_name
                    residue_text_layout.font_size = _layout._DEFAULT_MODIFICATION_FONT_SIZE
                    residue_text_layout.font_family = _layout._DEFAULT_FONT_FAMILY
                    residue_text_layout.fill = _layout._DEFAULT_FONT_FILL
                    residue_text_layout.stroke = momapy.drawing.NoneValue
                    segment = momapy.geometry.Segment(
                        layout_element.center(), super_layout_element.center()
                    )
                    fraction = (
                        layout_element.height + _layout._DEFAULT_MODIFICATION_FONT_SIZE
                    ) / segment.length()
                    residue_text_layout.position = segment.get_position_at_fraction(
                        fraction
                    )
                    residue_text_layout = momapy.builder.object_from_builder(
                        residue_text_layout
                    )
                    layout_element.layout_elements.append(residue_text_layout)
                layout_element = momapy.builder.object_from_builder(layout_element)
                super_layout_element.layout_elements.append(layout_element)
                ctx.cd_id_to_layout_element[layout_element.id_] = layout_element
                ctx.id_to_map_element[layout_element.id_] = layout_element
            else:
                layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_species_structural_state(
        cls,
        ctx,
        cd_species_structural_state,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        _layout = momapy.celldesigner.io.celldesigner._layout
        if ctx.model is not None:
            model_element = ctx.model.new_element(momapy.celldesigner.core.StructuralState)
            model_element.value = cd_species_structural_state.get("structuralState")
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.structural_states.add(model_element)
        else:
            model_element = None
        if ctx.layout is not None:  # TODO
            layout_element = ctx.layout.new_element(
                momapy.celldesigner.core.StructuralStateLayout
            )
            layout_element.position = super_layout_element.self_angle(90)
            text = cd_species_structural_state.get("structuralState")
            text_layout = momapy.core.layout.TextLayout(
                text=text,
                font_size=_layout._DEFAULT_MODIFICATION_FONT_SIZE,
                font_family=_layout._DEFAULT_FONT_FAMILY,
                fill=_layout._DEFAULT_FONT_FILL,
                stroke=momapy.drawing.NoneValue,
                position=layout_element.position,
            )
            layout_element.label = text_layout
            bbox = text_layout.bbox()
            layout_element.width = 1.5 * bbox.width
            layout_element.height = 1.5 * bbox.height
            layout_element = momapy.builder.object_from_builder(layout_element)
            super_layout_element.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_reactions_and_modulations(cls, ctx):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        for cd_reaction in _parsing.get_reactions(ctx.cd_model):
            key = _parsing.get_key_from_reaction(cd_reaction)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if issubclass(
                model_element_cls, momapy.celldesigner.core.Reaction
            ):  # true reaction
                model_element, layout_element = (
                    cls._make_and_add_reaction(
                        ctx,
                        cd_reaction=cd_reaction,
                    )
                )
            else:  # modulation
                model_element, layout_element = (
                    cls._make_and_add_modulation(
                        ctx,
                        cd_reaction=cd_reaction,
                    )
                )

    @classmethod
    def _make_and_add_reaction(
        cls,
        ctx,
        cd_reaction,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _model = momapy.celldesigner.io.celldesigner._model
        _layout = momapy.celldesigner.io.celldesigner._layout
        if ctx.model is not None or ctx.layout is not None:
            key = _parsing.get_key_from_reaction(cd_reaction)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            cd_base_reactants = _parsing.get_base_reactants(cd_reaction)
            cd_base_products = _parsing.get_base_products(cd_reaction)
            if ctx.model is not None:
                model_element = ctx.model.new_element(model_element_cls)
                model_element.id_ = cd_reaction.get("id")
                model_element.reversible = cd_reaction.get("reversible") == "true"
            else:
                model_element = None
            if ctx.layout is not None:
                layout_element = ctx.layout.new_element(layout_element_cls)
                layout_element.id_ = cd_reaction.get("id")
                layout_element.reversible = cd_reaction.get("reversible") == "true"
                if not layout_element.reversible:
                    layout_element.start_shorten = 0.0
                if len(cd_base_reactants) == 1 and len(cd_base_products) == 1:
                    segments = cls._make_segments_non_t_shape(
                        cd_reaction,
                        ctx.cd_id_to_layout_element,
                    )
                    reaction_node_segment = int(
                        _parsing.get_rectangle_index(cd_reaction)
                    )
                    make_base_reactant_layouts = False
                    make_base_product_layouts = False
                elif len(cd_base_reactants) > 1 and len(cd_base_products) == 1:
                    segments = cls._make_segments_left_t_shape(
                        cd_reaction,
                        ctx.cd_id_to_layout_element,
                    )
                    reaction_node_segment = int(
                        _parsing.get_t_shape_index(cd_reaction)
                    )
                    make_base_reactant_layouts = True
                    make_base_product_layouts = False
                elif len(cd_base_reactants) == 1 and len(cd_base_products) > 1:
                    segments = cls._make_segments_right_t_shape(
                        cd_reaction,
                        ctx.cd_id_to_layout_element,
                    )
                    reaction_node_segment = (
                        len(segments)
                        - 1
                        - int(_parsing.get_t_shape_index(cd_reaction))
                    )
                    make_base_reactant_layouts = False
                    make_base_product_layouts = True
                for segment in segments:
                    layout_element.segments.append(segment)
                layout_element.reaction_node_segment = reaction_node_segment
            else:
                layout_element = None
                make_base_reactant_layouts = False
                make_base_product_layouts = False
            participant_map_elements = []
            layout_elements_for_mapping = []
            for n_cd_base_reactant, cd_base_reactant in enumerate(cd_base_reactants):
                reactant_model_element, reactant_layout_element = (
                    cls._make_and_add_reactant_from_base(
                        ctx,
                        cd_base_reactant=cd_base_reactant,
                        n_cd_base_reactant=n_cd_base_reactant,
                        make_layout=make_base_reactant_layouts,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if ctx.model is not None and ctx.layout is not None:
                    if reactant_layout_element is not None:
                        participant_map_elements.append(
                            (reactant_model_element, reactant_layout_element)
                        )
                    layout_elements_for_mapping.append(
                        ctx.cd_id_to_layout_element[cd_base_reactant.get("alias")]
                    )
            for cd_reactant_link in _parsing.get_reactant_links(cd_reaction):
                reactant_model_element, reactant_layout_element = (
                    cls._make_and_add_reactant_from_link(
                        ctx,
                        cd_reactant_link=cd_reactant_link,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if ctx.model is not None and ctx.layout is not None:
                    participant_map_elements.append(
                        (reactant_model_element, reactant_layout_element)
                    )
                    layout_elements_for_mapping.append(
                        ctx.cd_id_to_layout_element[cd_reactant_link.get("alias")]
                    )
            for n_cd_base_product, cd_base_product in enumerate(cd_base_products):
                product_model_element, product_layout_element = (
                    cls._make_and_add_product_from_base(
                        ctx,
                        cd_base_product=cd_base_product,
                        n_cd_base_product=n_cd_base_product,
                        make_layout=make_base_product_layouts,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if ctx.model is not None and ctx.layout is not None:
                    if product_layout_element is not None:
                        participant_map_elements.append(
                            (product_model_element, product_layout_element)
                        )
                    layout_elements_for_mapping.append(
                        ctx.cd_id_to_layout_element[cd_base_product.get("alias")]
                    )
            for cd_product_link in _parsing.get_product_links(cd_reaction):
                product_model_element, product_layout_element = (
                    cls._make_and_add_product_from_link(
                        ctx,
                        cd_product_link=cd_product_link,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if ctx.model is not None and ctx.layout is not None:
                    participant_map_elements.append(
                        (product_model_element, product_layout_element)
                    )
                    layout_elements_for_mapping.append(
                        ctx.cd_id_to_layout_element[cd_product_link.get("alias")]
                    )
            for cd_reaction_modification in _parsing.get_reaction_modifications(
                cd_reaction
            ):
                modifier_model_element, modifier_layout_element = (
                    cls._make_and_add_modifier(
                        ctx,
                        cd_reaction_modification=cd_reaction_modification,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if ctx.model is not None and ctx.layout is not None:
                    participant_map_elements.append(
                        (modifier_model_element, modifier_layout_element)
                    )
                    layout_elements_for_mapping.append(modifier_layout_element.source)
            if ctx.model is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    ctx.model.reactions,
                    func=lambda element, existing_element: element.id_
                    < existing_element.id_,
                )
                ctx.cd_id_to_model_element[model_element.id_] = model_element
                ctx.id_to_map_element[cd_reaction.get("id")] = model_element
                if ctx.with_annotations:
                    annotations = _model.make_annotations_from_element(cd_reaction)
                    if annotations:
                        ctx.map_element_to_annotations[model_element].update(annotations)
                    if ctx.with_notes:
                        notes = _model.make_notes(cd_reaction)
                        ctx.map_element_to_notes[model_element].update(notes)
            if ctx.layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                ctx.layout.layout_elements.append(layout_element)
                ctx.cd_id_to_layout_element[layout_element.id_] = layout_element
                ctx.id_to_map_element[layout_element.id_] = layout_element
                layout_elements_for_mapping.append(layout_element)
            if ctx.model is not None and ctx.layout is not None:
                ctx.layout_model_mapping.add_mapping(
                    frozenset(layout_elements_for_mapping),
                    model_element,
                    replace=True,
                    anchor=layout_element,
                )
                for (
                    participant_model_element,
                    participant_layout_element,
                ) in participant_map_elements:
                    ctx.layout_model_mapping.add_mapping(
                        participant_layout_element,
                        (participant_model_element, model_element),
                        replace=True,
                    )
        return model_element, layout_element

    @classmethod
    def _make_segments_non_t_shape(
        cls, cd_reaction, cd_id_to_layout_element
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _layout = momapy.celldesigner.io.celldesigner._layout
        # Case where we have a linear reaction (one base reactant
        # and one base product). The frame for the edit points
        # is the orthonormal frame whose x axis goes from the
        # base reactant's center or link anchor to the base product's
        # center or link anchor and whose y axis is orthogonal to
        # to the x axis, going downwards
        cd_base_reactants = _parsing.get_base_reactants(cd_reaction)
        cd_base_products = _parsing.get_base_products(cd_reaction)
        cd_base_reactant = cd_base_reactants[0]
        cd_base_product = cd_base_products[0]
        reactant_layout_element = cd_id_to_layout_element[cd_base_reactant.get("alias")]
        product_layout_element = cd_id_to_layout_element[cd_base_product.get("alias")]
        reactant_anchor_name = _parsing.get_anchor_name_for_frame(cd_base_reactant)
        product_anchor_name = _parsing.get_anchor_name_for_frame(cd_base_product)
        origin = reactant_layout_element.anchor_point(reactant_anchor_name)
        unit_x = product_layout_element.anchor_point(product_anchor_name)
        unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
        transformation = momapy.geometry.get_transformation_for_frame(
            origin, unit_x, unit_y
        )
        intermediate_points = []
        cd_edit_points = _parsing.get_edit_points_from_reaction(cd_reaction)
        if cd_edit_points is None:
            edit_points = []
        else:
            edit_points = _layout.make_points(cd_edit_points)
        intermediate_points = [
            edit_point.transformed(transformation) for edit_point in edit_points
        ]
        if reactant_anchor_name == "center":
            if intermediate_points:
                reference_point = intermediate_points[0]

            else:
                reference_point = product_layout_element.anchor_point(
                    product_anchor_name
                )
            start_point = reactant_layout_element.border(reference_point)
        else:
            start_point = reactant_layout_element.anchor_point(reactant_anchor_name)
        if product_anchor_name == "center":
            if intermediate_points:
                reference_point = intermediate_points[-1]
            else:
                reference_point = reactant_layout_element.anchor_point(
                    reactant_anchor_name
                )
            end_point = product_layout_element.border(reference_point)
        else:
            end_point = product_layout_element.anchor_point(product_anchor_name)
        points = [start_point] + intermediate_points + [end_point]
        return _layout.make_segments(points)

    @classmethod
    def _make_segments_left_t_shape(
        cls, cd_reaction, cd_id_to_layout_element
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _layout = momapy.celldesigner.io.celldesigner._layout
        # Case where we have a tshape reaction with two base reactants
        # and one base product. The frame for the edit points are the
        # axes going from the center of the first base reactant to
        # the center of the second base reactant (x axis), and from the
        # center of the first base reactant to the center of the base
        # product (y axis).
        cd_base_reactants = _parsing.get_base_reactants(cd_reaction)
        cd_base_products = _parsing.get_base_products(cd_reaction)
        cd_base_reactant_0 = cd_base_reactants[0]
        cd_base_reactant_1 = cd_base_reactants[1]
        cd_base_product = cd_base_products[0]
        reactant_layout_element_0 = cd_id_to_layout_element[
            cd_base_reactant_0.get("alias")
        ]
        reactant_layout_element_1 = cd_id_to_layout_element[
            cd_base_reactant_1.get("alias")
        ]
        product_layout_element = cd_id_to_layout_element[cd_base_product.get("alias")]
        product_anchor_name = _parsing.get_anchor_name_for_frame(cd_base_product)
        origin = reactant_layout_element_0.center()
        unit_x = reactant_layout_element_1.center()
        unit_y = product_layout_element.center()
        transformation = momapy.geometry.get_transformation_for_frame(
            origin, unit_x, unit_y
        )
        cd_edit_points = _parsing.get_edit_points_from_reaction(cd_reaction)
        edit_points = _layout.make_points(cd_edit_points)
        start_point = edit_points[-1].transformed(transformation)
        # The frame for the intermediate edit points becomes
        # the orthonormal frame whose x axis goes from the
        # start point of the reaction computed above to the base
        # product's center or link anchor and whose y axis is
        # orthogonal to the x axis, going downwards
        origin = start_point
        unit_x = product_layout_element.anchor_point(product_anchor_name)
        unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
        transformation = momapy.geometry.get_transformation_for_frame(
            origin, unit_x, unit_y
        )
        intermediate_points = []
        # the index for the intermediate points of the reaction
        # starts after those for the two base reactants
        start_index = int(cd_edit_points.get("num0")) + int(cd_edit_points.get("num1"))
        for edit_point in edit_points[start_index:-1]:
            intermediate_point = edit_point.transformed(transformation)
            intermediate_points.append(intermediate_point)
        if getattr(cd_base_product, "linkAnchor", None) is not None:
            end_point = product_layout_element.anchor_point(
                _parsing.get_anchor_name_for_frame(cd_base_product)
            )
        else:
            if intermediate_points:
                reference_point = intermediate_points[-1]
            else:
                reference_point = start_point
            end_point = product_layout_element.border(reference_point)
        points = [start_point] + intermediate_points + [end_point]
        return _layout.make_segments(points)

    @classmethod
    def _make_segments_right_t_shape(
        cls, cd_reaction, cd_id_to_layout_element
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _layout = momapy.celldesigner.io.celldesigner._layout
        # Case where we have a tshape reaction with one base reactant
        # and two base products. The frame for the edit points are the
        # axes going from the center of the first base product to
        # the center of the second base product (x axis), and from the
        # center of the first base product to the center of the base
        # reactant (y axis).
        cd_base_reactants = _parsing.get_base_reactants(cd_reaction)
        cd_base_products = _parsing.get_base_products(cd_reaction)
        cd_base_product_0 = cd_base_products[0]
        cd_base_product_1 = cd_base_products[1]
        cd_base_reactant = cd_base_reactants[0]
        product_layout_element_0 = cd_id_to_layout_element[
            cd_base_product_0.get("alias")
        ]
        product_layout_element_1 = cd_id_to_layout_element[
            cd_base_product_1.get("alias")
        ]
        reactant_layout_element = cd_id_to_layout_element[cd_base_reactant.get("alias")]
        reactant_anchor_name = _parsing.get_anchor_name_for_frame(cd_base_reactant)
        origin = reactant_layout_element.center()
        unit_x = product_layout_element_0.center()
        unit_y = product_layout_element_1.center()
        transformation = momapy.geometry.get_transformation_for_frame(
            origin, unit_x, unit_y
        )
        cd_edit_points = _parsing.get_edit_points_from_reaction(cd_reaction)
        edit_points = _layout.make_points(cd_edit_points)
        end_point = edit_points[-1].transformed(transformation)
        # The frame for the intermediate edit points becomes
        # the orthonormal frame whose x axis goes from the
        # start point of the reaction computed above to the base
        # product's center or link anchor and whose y axis is
        # orthogonal to the x axis, going downwards
        origin = end_point
        unit_x = reactant_layout_element.anchor_point(reactant_anchor_name)
        unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
        transformation = momapy.geometry.get_transformation_for_frame(
            origin, unit_x, unit_y
        )
        intermediate_points = []
        # the index for the intermediate points of the reaction
        # starts at 0 and ends at before those for the two base products
        end_index = int(cd_edit_points.get("num0"))
        edit_points = list(reversed(edit_points[:end_index]))
        for edit_point in edit_points:
            intermediate_point = edit_point.transformed(transformation)
            intermediate_points.append(intermediate_point)
        if getattr(cd_base_reactant, "linkAnchor", None) is not None:
            start_point = reactant_layout_element.anchor_point(
                _parsing.get_anchor_name_for_frame(cd_base_reactant)
            )
        else:
            if intermediate_points:
                reference_point = intermediate_points[0]
            else:
                reference_point = end_point
            start_point = reactant_layout_element.border(reference_point)
        points = [start_point] + intermediate_points + [end_point]
        return _layout.make_segments(points)

    @classmethod
    def _make_and_add_reactant_from_base(
        cls,
        ctx,
        cd_base_reactant,
        n_cd_base_reactant,
        make_layout,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _layout = momapy.celldesigner.io.celldesigner._layout
        if ctx.model is not None:
            model_element = ctx.model.new_element(momapy.celldesigner.core.Reactant)
            cd_species_id = cd_base_reactant.get("species")
            # the id and stoichiometry is stored in the reactant, not
            # base reactant, so we get the corresponding reactant
            for cd_reactant in _parsing.get_reactants(super_cd_element):
                if cd_reactant.get("species") == cd_species_id:
                    model_element.id_ = cd_reactant.get("metaid")
                    cd_stoichiometry = cd_reactant.get("stoichiometry")
                    if cd_stoichiometry is not None:
                        model_element.stoichiometry = float(cd_stoichiometry)
                    break
            if model_element.id_ is None:
                model_element.id_ = f"{super_cd_element.get('id')}_{cd_species_id}"
            species_model_element = ctx.cd_id_to_model_element[
                cd_base_reactant.get("alias")
            ]
            model_element.referred_species = species_model_element
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.reactants.add(model_element)
            ctx.cd_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if ctx.layout is not None and make_layout:
            layout_element = ctx.layout.new_element(
                momapy.celldesigner.core.ConsumptionLayout
            )
            cd_edit_points = _parsing.get_edit_points_from_reaction(super_cd_element)
            cd_num_0 = cd_edit_points.get("num0")
            cd_num_1 = cd_edit_points.get("num1")
            if n_cd_base_reactant == 0:
                start_index = n_cd_base_reactant
                stop_index = int(cd_num_0)
            elif n_cd_base_reactant == 1:
                start_index = int(cd_num_0)
                stop_index = int(cd_num_0) + int(cd_num_1)
            species_layout_element = ctx.cd_id_to_layout_element[
                cd_base_reactant.get("alias")
            ]
            reactant_anchor_name = _parsing.get_anchor_name_for_frame(cd_base_reactant)
            origin = super_layout_element.points()[0]
            unit_x = species_layout_element.anchor_point(reactant_anchor_name)
            unit_y = unit_x.transformed(
                momapy.geometry.Rotation(math.radians(90), origin)
            )
            transformation = momapy.geometry.get_transformation_for_frame(
                origin, unit_x, unit_y
            )
            intermediate_points = []
            edit_points = _layout.make_points(cd_edit_points)
            for edit_point in edit_points[start_index:stop_index]:
                intermediate_point = edit_point.transformed(transformation)
                intermediate_points.append(intermediate_point)
            intermediate_points.reverse()
            if reactant_anchor_name == "center":
                if intermediate_points:
                    reference_point = intermediate_points[0]
                else:
                    reference_point = super_layout_element.start_point()

                start_point = species_layout_element.border(reference_point)
            else:
                start_point = species_layout_element.anchor_point(reactant_anchor_name)
            if intermediate_points:
                reference_point = intermediate_points[-1]
            else:
                reference_point = start_point
            end_point = super_layout_element.start_arrowhead_border(reference_point)
            points = [start_point] + intermediate_points + [end_point]
            segments = _layout.make_segments(points)
            for segment in segments:
                layout_element.segments.append(segment)
            layout_element = momapy.builder.object_from_builder(layout_element)
            super_layout_element.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_reactant_from_link(
        cls,
        ctx,
        cd_reactant_link,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _layout = momapy.celldesigner.io.celldesigner._layout
        if ctx.model is not None:
            model_element = ctx.model.new_element(momapy.celldesigner.core.Reactant)
            cd_species_id = cd_reactant_link.get("reactant")
            for cd_reactant in _parsing.get_reactants(super_cd_element):
                if cd_reactant.get("species") == cd_species_id:
                    model_element.id_ = cd_reactant.get("metaid")
                    cd_stoichiometry = cd_reactant.get("stoichiometry")
                    if cd_stoichiometry is not None:
                        model_element.stoichiometry = float(cd_stoichiometry)
                    break
            if model_element.id_ is None:
                model_element.id_ = f"{super_cd_element.get('id')}_{cd_species_id}"
            species_model_element = ctx.cd_id_to_model_element[
                cd_reactant_link.get("alias")
            ]
            model_element.referred_species = species_model_element
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.reactants.add(model_element)
            ctx.cd_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if ctx.layout is not None:
            layout_element = ctx.layout.new_element(
                momapy.celldesigner.core.ConsumptionLayout
            )
            species_layout_element = ctx.cd_id_to_layout_element[
                cd_reactant_link.get("alias")
            ]
            reactant_anchor_name = _parsing.get_anchor_name_for_frame(cd_reactant_link)
            origin = species_layout_element.center()
            unit_x = super_layout_element.left_connector_tip()
            unit_y = unit_x.transformed(
                momapy.geometry.Rotation(math.radians(90), origin)
            )
            transformation = momapy.geometry.get_transformation_for_frame(
                origin, unit_x, unit_y
            )
            cd_edit_points = _parsing.get_edit_points_from_participant_link(
                cd_reactant_link
            )
            if cd_edit_points is None:
                edit_points = []
            else:
                edit_points = _layout.make_points(cd_edit_points)
            intermediate_points = [
                edit_point.transformed(transformation) for edit_point in edit_points
            ]
            end_point = unit_x
            if reactant_anchor_name == "center":
                if intermediate_points:
                    reference_point = intermediate_points[0]
                else:
                    reference_point = end_point
                start_point = species_layout_element.border(reference_point)
            else:
                start_point = species_layout_element.anchor_point(reactant_anchor_name)
            points = [start_point] + intermediate_points + [end_point]
            segments = _layout.make_segments(points)
            for segment in segments:
                layout_element.segments.append(segment)
            layout_element = momapy.builder.object_from_builder(layout_element)
            super_layout_element.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_product_from_base(
        cls,
        ctx,
        cd_base_product,
        n_cd_base_product,
        make_layout,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _layout = momapy.celldesigner.io.celldesigner._layout
        if ctx.model is not None:
            model_element = ctx.model.new_element(momapy.celldesigner.core.Product)
            cd_species_id = cd_base_product.get("species")
            # the id and stoichiometry is stored in the product, not
            # base product, so we get the corresponding product
            for cd_product in _parsing.get_products(super_cd_element):
                if cd_product.get("species") == cd_species_id:
                    model_element.id_ = cd_product.get("metaid")
                    cd_stoichiometry = cd_product.get("stoichiometry")
                    if cd_stoichiometry is not None:
                        model_element.stoichiometry = float(cd_stoichiometry)
                    break
            if model_element.id_ is None:
                model_element.id_ = f"{super_cd_element.get('id')}_{cd_species_id}"
            species_model_element = ctx.cd_id_to_model_element[cd_base_product.get("alias")]
            model_element.referred_species = species_model_element
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.products.add(model_element)
            ctx.cd_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if ctx.layout is not None and make_layout:
            layout_element = ctx.layout.new_element(
                momapy.celldesigner.core.ProductionLayout
            )
            cd_edit_points = _parsing.get_edit_points_from_reaction(super_cd_element)
            cd_num_0 = cd_edit_points.get("num0")
            cd_num_1 = cd_edit_points.get("num1")
            cd_num_2 = cd_edit_points.get("num2")
            if n_cd_base_product == 0:
                start_index = int(cd_num_0)
                stop_index = int(cd_num_0) + int(cd_num_1)
            elif n_cd_base_product == 1:
                start_index = int(cd_num_0) + int(cd_num_1)
                stop_index = int(cd_num_0) + int(cd_num_1) + int(cd_num_2)
            product_layout_element = ctx.cd_id_to_layout_element[
                cd_base_product.get("alias")
            ]
            product_anchor_name = _parsing.get_anchor_name_for_frame(cd_base_product)
            origin = super_layout_element.end_point()
            unit_x = product_layout_element.anchor_point(product_anchor_name)
            unit_y = unit_x.transformed(
                momapy.geometry.Rotation(math.radians(90), origin)
            )
            transformation = momapy.geometry.get_transformation_for_frame(
                origin, unit_x, unit_y
            )
            intermediate_points = []
            edit_points = _layout.make_points(cd_edit_points)
            for edit_point in edit_points[start_index:stop_index]:
                intermediate_point = edit_point.transformed(transformation)
                intermediate_points.append(intermediate_point)
            if product_anchor_name == "center":
                if intermediate_points:
                    reference_point = intermediate_points[-1]
                else:
                    reference_point = super_layout_element.end_point()
                end_point = product_layout_element.border(reference_point)
            else:
                end_point = product_layout_element.anchor_point(product_anchor_name)
            if intermediate_points:
                reference_point = intermediate_points[0]
            else:
                reference_point = end_point
            start_point = super_layout_element.end_arrowhead_border(reference_point)
            points = [start_point] + intermediate_points + [end_point]
            segments = _layout.make_segments(points)
            for segment in segments:
                layout_element.segments.append(segment)
            layout_element = momapy.builder.object_from_builder(layout_element)
            super_layout_element.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_product_from_link(
        cls,
        ctx,
        cd_product_link,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _layout = momapy.celldesigner.io.celldesigner._layout
        if ctx.model is not None:
            model_element = ctx.model.new_element(momapy.celldesigner.core.Product)
            cd_species_id = cd_product_link.get("product")
            # the id and stoichiometry is stored in the product, not
            # base product, so we get the corresponding product
            for cd_product in _parsing.get_products(super_cd_element):
                if cd_product.get("species") == cd_species_id:
                    model_element.id_ = cd_product.get("metaid")
                    cd_stoichiometry = cd_product.get("stoichiometry")
                    if cd_stoichiometry is not None:
                        model_element.stoichiometry = float(cd_stoichiometry)
                    break
            if model_element.id_ is None:
                model_element.id_ = f"{super_cd_element.get('id')}_{cd_species_id}"
            species_model_element = ctx.cd_id_to_model_element[cd_product_link.get("alias")]
            model_element.referred_species = species_model_element
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.products.add(model_element)
            ctx.cd_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if ctx.layout is not None:
            layout_element = ctx.layout.new_element(
                momapy.celldesigner.core.ProductionLayout
            )
            species_layout_element = ctx.cd_id_to_layout_element[
                cd_product_link.get("alias")
            ]
            product_anchor_name = _parsing.get_anchor_name_for_frame(cd_product_link)
            origin = super_layout_element.right_connector_tip()
            unit_x = species_layout_element.center()
            unit_y = unit_x.transformed(
                momapy.geometry.Rotation(math.radians(90), origin)
            )
            transformation = momapy.geometry.get_transformation_for_frame(
                origin, unit_x, unit_y
            )
            cd_edit_points = _parsing.get_edit_points_from_participant_link(
                cd_product_link
            )
            if cd_edit_points is None:
                edit_points = []
            else:
                edit_points = _layout.make_points(cd_edit_points)
            intermediate_points = [
                edit_point.transformed(transformation) for edit_point in edit_points
            ]
            intermediate_points.reverse()
            start_point = origin
            if product_anchor_name == "center":
                if intermediate_points:
                    reference_point = intermediate_points[-1]
                else:
                    reference_point = start_point
                end_point = species_layout_element.border(reference_point)
            else:
                end_point = species_layout_element.anchor_point(product_anchor_name)
            points = [start_point] + intermediate_points + [end_point]
            segments = _layout.make_segments(points)
            for segment in segments:
                layout_element.segments.append(segment)
            layout_element = momapy.builder.object_from_builder(layout_element)
            super_layout_element.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_modifier(
        cls,
        ctx,
        cd_reaction_modification,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _layout = momapy.celldesigner.io.celldesigner._layout
        if ctx.model is not None or ctx.layout is not None:
            key = _parsing.get_key_from_reaction_modification(cd_reaction_modification)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            has_boolean_input = _parsing.has_boolean_input_from_modification(
                cd_reaction_modification
            )
            if has_boolean_input:
                source_model_element, source_layout_element = (
                    cls._make_and_add_logic_gate(
                        ctx,
                        cd_reaction_modification_or_cd_gate_member=cd_reaction_modification,
                    )
                )
            if ctx.model is not None:
                model_element = ctx.model.new_element(model_element_cls)
                if not has_boolean_input:
                    source_model_element = ctx.cd_id_to_model_element[
                        cd_reaction_modification.get("aliases")
                    ]
                model_element.referred_species = source_model_element
                if model_element is not None:  # to delete
                    model_element = momapy.builder.object_from_builder(model_element)
                    super_model_element.modifiers.add(model_element)
            else:
                model_element = None
            if ctx.layout is not None:
                layout_element = ctx.layout.new_element(layout_element_cls)
                cd_edit_points = cd_reaction_modification.get("editPoints")
                if cd_edit_points is not None:
                    edit_points = _layout.make_points(cd_edit_points)
                else:
                    edit_points = []
                if not has_boolean_input:
                    source_layout_element = ctx.cd_id_to_layout_element[
                        cd_reaction_modification.get("aliases")
                    ]
                    cd_link_target = getattr(
                        cd_reaction_modification, "linkTarget", None
                    )
                    if cd_link_target is not None:
                        cd_link_anchor = getattr(cd_link_target, "linkAnchor", None)
                        if cd_link_anchor is not None:
                            source_anchor_name = (
                                _parsing.get_anchor_name_for_frame(cd_link_target)
                            )
                        else:
                            source_anchor_name = "center"
                    else:
                        source_anchor_name = "center"
                else:
                    source_anchor_name = "center"
                    edit_points = edit_points[
                        :-1
                    ]  # last point is the position of the logic gate
                origin = source_layout_element.anchor_point(source_anchor_name)
                unit_x = super_layout_element._get_reaction_node_position()
                unit_y = unit_x.transformed(
                    momapy.geometry.Rotation(math.radians(90), origin)
                )
                transformation = momapy.geometry.get_transformation_for_frame(
                    origin, unit_x, unit_y
                )
                intermediate_points = [
                    edit_point.transformed(transformation) for edit_point in edit_points
                ]
                if source_anchor_name == "center":
                    if intermediate_points:
                        reference_point = intermediate_points[0]
                    else:
                        reference_point = unit_x
                    start_point = source_layout_element.border(reference_point)
                else:
                    start_point = origin
                if intermediate_points:
                    reference_point = intermediate_points[-1]
                else:
                    reference_point = start_point
                end_point = super_layout_element.reaction_node_border(reference_point)
                points = [start_point] + intermediate_points + [end_point]
                segments = _layout.make_segments(points)
                for segment in segments:
                    layout_element.segments.append(segment)
                layout_element.source = source_layout_element
                layout_element = momapy.builder.object_from_builder(layout_element)
                super_layout_element.layout_elements.append(layout_element)
            else:
                layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_logic_gate(
        cls,
        ctx,
        cd_reaction_modification_or_cd_gate_member,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _layout = momapy.celldesigner.io.celldesigner._layout
        if ctx.model is not None or ctx.layout is not None:
            key = _parsing.get_key_from_gate_member(
                cd_reaction_modification_or_cd_gate_member
            )
            cd_modifiers = cd_reaction_modification_or_cd_gate_member.get("aliases")
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if ctx.model is not None:
                model_element = ctx.model.new_element(model_element_cls)
                model_input_elements = [
                    ctx.cd_id_to_model_element[cd_input_id]
                    for cd_input_id in cd_modifiers.split(",")
                ]
                for model_input_element in model_input_elements:
                    model_element.inputs.add(model_input_element)
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    ctx.model.boolean_logic_gates,
                    func=lambda element, existing_element: element.id_
                    < existing_element.id_,
                )
            else:
                model_element = None
            if ctx.layout is not None:  # TODO: edit points
                layout_element = ctx.layout.new_element(layout_element_cls)
                cd_edit_points = cd_reaction_modification_or_cd_gate_member.get(
                    "editPoints"
                )
                edit_points = _layout.make_points(cd_edit_points)
                position = edit_points[-1]
                layout_element.position = position
                layout_input_elements = [
                    ctx.cd_id_to_layout_element[cd_input_id]
                    for cd_input_id in cd_modifiers.split(",")
                ]
                for layout_input_element in layout_input_elements:
                    layout_logic_arc = ctx.layout.new_element(
                        momapy.celldesigner.core.LogicArcLayout
                    )
                    start_point = layout_input_element.border(position)
                    end_point = layout_element.border(start_point)
                    segment = momapy.geometry.Segment(start_point, end_point)
                    layout_logic_arc.segments.append(segment)
                    layout_logic_arc.target = layout_input_element
                    layout_logic_arc = momapy.builder.object_from_builder(
                        layout_logic_arc
                    )
                    layout_element.layout_elements.append(layout_logic_arc)
                layout_element = momapy.builder.object_from_builder(layout_element)
                ctx.layout.layout_elements.append(layout_element)
            else:
                layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_modulation(
        cls,
        ctx,
        cd_reaction,
    ):
        _parsing = momapy.celldesigner.io.celldesigner._parsing
        _model = momapy.celldesigner.io.celldesigner._model
        _layout = momapy.celldesigner.io.celldesigner._layout
        if ctx.model is not None or ctx.layout is not None:
            key = _parsing.get_key_from_reaction(cd_reaction)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            has_boolean_input = _parsing.has_boolean_input_from_reaction(cd_reaction)
            cd_base_reactant = _parsing.get_base_reactants(cd_reaction)[0]
            cd_base_product = _parsing.get_base_products(cd_reaction)[0]
            if has_boolean_input:
                cd_gate_members = _parsing.get_gate_members(cd_reaction)
                cd_gate_member = cd_gate_members[0]
                source_model_element, source_layout_element = (
                    cls._make_and_add_logic_gate(
                        ctx,
                        cd_reaction_modification_or_cd_gate_member=cd_gate_member,
                    )
                )
            if ctx.model is not None:
                model_element = ctx.model.new_element(model_element_cls)
                model_element.id_ = cd_reaction.get("id")
                if has_boolean_input:
                    source_model_element, source_layout_element = (
                        cls._make_and_add_logic_gate(
                            ctx,
                            cd_reaction_modification_or_cd_gate_member=cd_gate_member,
                        )
                    )
                else:
                    source_model_element = ctx.cd_id_to_model_element[
                        cd_base_reactant.get("alias")
                    ]
                model_element.source = source_model_element
                target_model_element = ctx.cd_id_to_model_element[
                    cd_base_product.get("alias")
                ]
                model_element.target = target_model_element
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    ctx.model.modulations,
                    func=lambda element, existing_element: element.id_
                    < existing_element.id_,
                )
                ctx.id_to_map_element[cd_reaction.get("id")] = model_element
                if ctx.with_annotations:
                    annotations = _model.make_annotations_from_element(cd_reaction)
                    if annotations:
                        ctx.map_element_to_annotations[model_element].update(annotations)
                    if ctx.with_notes:
                        notes = _model.make_notes(cd_reaction)
                        ctx.map_element_to_notes[model_element].update(notes)
            else:
                model_element = None
            if ctx.layout is not None:
                cd_edit_points = _parsing.get_edit_points_from_reaction(cd_reaction)
                if cd_edit_points is not None:
                    edit_points = _layout.make_points(cd_edit_points)
                else:
                    edit_points = []
                if has_boolean_input:
                    source_anchor_name = "center"
                    edit_points = edit_points[:-1]
                else:
                    source_layout_element = ctx.cd_id_to_layout_element[
                        cd_base_reactant.get("alias")
                    ]
                    if hasattr(cd_base_reactant, "linkAnchor"):
                        source_anchor_name = (
                            _parsing.get_anchor_name_for_frame(cd_base_reactant)
                        )
                    else:
                        source_anchor_name = "center"
                layout_element = ctx.layout.new_element(layout_element_cls)
                target_layout_element = ctx.cd_id_to_layout_element[
                    cd_base_product.get("alias")
                ]
                if hasattr(cd_base_product, "linkAnchor"):
                    target_anchor_name = _parsing.get_anchor_name_for_frame(
                        cd_base_product
                    )
                else:
                    target_anchor_name = "center"
                origin = source_layout_element.anchor_point(source_anchor_name)
                unit_x = target_layout_element.anchor_point(target_anchor_name)
                unit_y = unit_x.transformed(
                    momapy.geometry.Rotation(math.radians(90), origin)
                )
                transformation = momapy.geometry.get_transformation_for_frame(
                    origin, unit_x, unit_y
                )
                intermediate_points = [
                    edit_point.transformed(transformation) for edit_point in edit_points
                ]
                if source_anchor_name == "center":
                    if intermediate_points:
                        reference_point = intermediate_points[0]
                    else:
                        reference_point = unit_x
                    start_point = source_layout_element.border(reference_point)
                else:
                    start_point = origin
                if target_anchor_name == "center":
                    if intermediate_points:
                        reference_point = intermediate_points[-1]
                    else:
                        reference_point = start_point
                    end_point = target_layout_element.border(reference_point)
                else:
                    end_point = target_layout_element.anchor_point(target_anchor_name)
                points = [start_point] + intermediate_points + [end_point]
                segments = _layout.make_segments(points)
                for segment in segments:
                    layout_element.segments.append(segment)
                layout_element = momapy.builder.object_from_builder(layout_element)
                ctx.layout.layout_elements.append(layout_element)
                ctx.id_to_map_element[layout_element.id_] = layout_element
            else:
                layout_element = None
            if ctx.model is not None and ctx.layout is not None:
                ctx.layout_model_mapping.add_mapping(
                    frozenset(
                        [layout_element, source_layout_element, target_layout_element]
                    ),
                    model_element,
                    replace=True,
                    anchor=layout_element,
                )
        return model_element, layout_element
