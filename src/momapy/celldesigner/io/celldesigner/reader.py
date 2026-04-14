"""CellDesigner reader class.

ID Assignment
-------------

CellDesigner uses different XML ID namespaces for model and layout
elements. The general rules are:

- When an element has a natural XML ID (``compartment/@id``,
  ``species/@id``, ``reaction/@id``), the model element uses it
  directly.
- When a separate alias element exists (``speciesAlias/@id``,
  ``compartmentAlias/@id``), the layout element uses the alias ID.
- When model and layout share the same XML ID source (reactions,
  modulations), the layout element gets a ``_layout`` suffix:
  ``f"{reaction_id}_layout"``.

Element-specific patterns:

- **Compartment**: model ``id_`` = ``compartment/@id``,
  layout ``id_`` = ``compartmentAlias/@id``.
- **Species**: model ``id_`` = ``species/@id``,
  layout ``id_`` = ``speciesAlias/@id``.
  Model is registered under both IDs for cross-ref resolution.
- **Species Template**: model ``id_`` = ``proteinReference/@id`` (etc.),
  no layout.
- **ModificationResidue / Region**: composite
  ``f"{template_id}_{child_id}"`` for global uniqueness, no layout.
- **Modification** (species modification state): composite
  ``f"{species_id}_{residue_id}"``,
  layout ``f"{species_id}_{residue_id}_layout"``.
- **StructuralState**: composite ``f"{species_id}_{value}"``,
  layout ``f"{species_id}_{value}_layout"``.
- **Reactant / Product**: ``speciesReference/@metaid`` preferred,
  fallback to ``f"{reaction_id}_{species_id}"``, no layout.
- **Modulator**: ``modifierSpeciesReference/@metaid``,
  layout ``f"{metaid}_layout"``.
- **Reaction**: model ``id_`` = ``reaction/@id``,
  layout ``id_`` = ``f"{reaction_id}_layout"``.
- **Modulation** (encoded as fake reactions): same as Reaction.
- **BooleanGate**: composite
  ``f"{reaction_id}_gate_{sorted_aliases}"``,
  layout ``f"{...}_layout"``.
- **LogicArc**: layout only,
  ``f"{gate_id}_arc_{input_alias}"``.
"""

import os
import collections
import dataclasses
import typing

import frozendict
import lxml.objectify

import momapy.core
import momapy.core.mapping
import momapy.io.core
import momapy.io.utils
import momapy.builder
import momapy.celldesigner.core
import momapy.sbml.core
import momapy.utils

import momapy.celldesigner.io.celldesigner._reading_parsing
import momapy.celldesigner.io.celldesigner._reading_model
import momapy.celldesigner.io.celldesigner._reading_layout


@dataclasses.dataclass
class ReadingContext(momapy.io.utils.ReadingContext):
    """CellDesigner-specific reading context."""

    cd_complex_alias_id_to_cd_included_species_ids: dict = dataclasses.field(
        default_factory=dict
    )
    cd_compartment_aliases: list = dataclasses.field(default_factory=list)
    cd_compartments: list = dataclasses.field(default_factory=list)
    cd_species_templates: list = dataclasses.field(default_factory=list)
    cd_species_aliases: list = dataclasses.field(default_factory=list)
    cd_reactions: list = dataclasses.field(default_factory=list)
    cd_modulations: list = dataclasses.field(default_factory=list)


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
            momapy.celldesigner.core.InhibitionLayout,
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
    def _parse_cd_model(cls, reading_context):
        """Pre-scan the CellDesigner model into categorized element lists.

        Populates reading_context with ID mappings and categorized
        elements, avoiding repeated XML traversals during the main read.

        Args:
            reading_context: The reading context to populate.
        """
        cd_model = reading_context.xml_root
        reading_context.xml_id_to_xml_element = (
            momapy.celldesigner.io.celldesigner._reading_parsing.make_id_to_element_mapping(
                cd_model
            )
        )
        reading_context.cd_complex_alias_id_to_cd_included_species_ids = (
            momapy.celldesigner.io.celldesigner._reading_parsing.make_complex_alias_to_included_ids_mapping(
                cd_model
            )
        )
        reading_context.cd_compartment_aliases = (
            momapy.celldesigner.io.celldesigner._reading_parsing.get_ordered_compartment_aliases(
                cd_model, reading_context.xml_id_to_xml_element
            )
        )
        reading_context.cd_compartments = (
            momapy.celldesigner.io.celldesigner._reading_parsing.get_compartments(
                cd_model
            )
        )
        reading_context.cd_species_templates = (
            momapy.celldesigner.io.celldesigner._reading_parsing.get_species_templates(
                cd_model
            )
        )
        reading_context.cd_species_aliases = (
            momapy.celldesigner.io.celldesigner._reading_parsing.get_species_aliases(
                cd_model
            )
            + momapy.celldesigner.io.celldesigner._reading_parsing.get_complex_species_aliases(
                cd_model
            )
        )
        reading_context.cd_reactions = []
        reading_context.cd_modulations = []
        for cd_reaction in momapy.celldesigner.io.celldesigner._reading_parsing.get_reactions(
            cd_model
        ):
            key = momapy.celldesigner.io.celldesigner._reading_parsing.get_key_from_reaction(
                cd_reaction
            )
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if issubclass(
                model_element_cls, momapy.celldesigner.core.Reaction
            ):
                reading_context.cd_reactions.append(cd_reaction)
            else:
                reading_context.cd_modulations.append(cd_reaction)

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
        if return_type == "model" or return_type == "map" and with_model:
            model = momapy.celldesigner.io.celldesigner._reading_model.make_empty_model(
                cd_model
            )
        else:
            model = None
        if return_type == "layout" or return_type == "map" and with_layout:
            layout = momapy.celldesigner.io.celldesigner._reading_layout.make_empty_layout(
                cd_model
            )
        else:
            layout = None
        map_element_to_annotations = collections.defaultdict(set)
        map_element_to_notes = collections.defaultdict(set)
        if model is not None or layout is not None:
            if model is not None and layout is not None:
                layout_model_mapping = momapy.core.mapping.LayoutModelMappingBuilder()
            else:
                layout_model_mapping = None
            reading_context = ReadingContext(
                xml_root=cd_model,
                model=model,
                layout=layout,
                xml_id_to_model_element=momapy.utils.IdentitySurjectionDict(),
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                layout_model_mapping=layout_model_mapping,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
            cls._parse_cd_model(reading_context)
            for cd_compartment_alias in reading_context.cd_compartment_aliases:
                cls._make_and_add_compartment_from_alias(
                    reading_context,
                    cd_compartment_alias=cd_compartment_alias,
                )
            for cd_compartment in reading_context.cd_compartments:
                if cd_compartment.get("id") not in reading_context.xml_id_to_model_element:
                    cls._make_and_add_compartment(
                        reading_context,
                        cd_compartment=cd_compartment,
                    )
            for cd_species_template in reading_context.cd_species_templates:
                cls._make_and_add_species_template(
                    reading_context,
                    cd_species_template=cd_species_template,
                )
            for cd_species_alias in reading_context.cd_species_aliases:
                cls._make_and_add_species(
                    reading_context,
                    cd_species_alias=cd_species_alias,
                )
            for cd_reaction in reading_context.cd_reactions:
                cls._make_and_add_reaction(
                    reading_context,
                    cd_reaction=cd_reaction,
                )
            for cd_modulation in reading_context.cd_modulations:
                cls._make_and_add_modulation(
                    reading_context,
                    cd_reaction=cd_modulation,
                )
            # Fix stale references in layout_model_mapping from
            # local variables captured before dedup events.
            if reading_context.model_element_remap and reading_context.layout_model_mapping is not None:
                momapy.io.utils.apply_remap_to_layout_model_mapping(reading_context)
            if layout is not None:
                momapy.celldesigner.io.celldesigner._reading_layout.set_layout_size_and_position(
                    reading_context, cd_model
                )
        if return_type == "model":
            obj = momapy.builder.object_from_builder(model)
            if with_annotations:
                annotations = momapy.celldesigner.io.celldesigner._reading_model.make_annotations_from_element(
                    cd_model
                )
                map_element_to_annotations[obj].update(annotations)
            if with_notes:
                notes = momapy.celldesigner.io.celldesigner._reading_model.make_notes(cd_model)
                map_element_to_notes[obj].update(notes)
        elif return_type == "layout":
            obj = momapy.builder.object_from_builder(layout)
        elif return_type == "map":
            map_ = momapy.celldesigner.io.celldesigner._reading_model.make_empty_map(cd_model)
            map_.model = model
            map_.layout = layout
            map_.layout_model_mapping = layout_model_mapping
            obj = momapy.builder.object_from_builder(map_)
            if with_annotations:
                annotations = momapy.celldesigner.io.celldesigner._reading_model.make_annotations_from_element(
                    cd_model
                )
                map_element_to_annotations[obj].update(annotations)
            if with_notes:
                notes = momapy.celldesigner.io.celldesigner._reading_model.make_notes(cd_model)
                map_element_to_notes[obj].update(notes)
        annotations = frozendict.frozendict(
            {key: frozenset(val) for key, val in map_element_to_annotations.items()}
        )
        notes = frozendict.frozendict(
            {key: frozenset(val) for key, val in map_element_to_notes.items()}
        )
        # Build id_to_map_element from the two id-to-element dicts.
        # Layout entries take precedence over model entries for the
        # same key (e.g., a species alias id maps to the layout element).
        if model is not None or layout is not None:
            id_to_map_element = dict(reading_context.xml_id_to_model_element)
            id_to_map_element.update(reading_context.xml_id_to_layout_element)
        else:
            id_to_map_element = {}
        ids = momapy.utils.FrozenSurjectionDict(id_to_map_element)
        return obj, annotations, notes, ids

    @classmethod
    def _make_and_add_compartment_from_alias(
        cls,
        reading_context,
        cd_compartment_alias,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            cd_compartment = reading_context.xml_id_to_xml_element[
                cd_compartment_alias.get("compartment")
            ]
            if reading_context.model is not None:
                # we make and add the model element from the cd compartment
                # the cd element is an alias of, if it has not already been made
                # while being outside another one
                model_element = reading_context.xml_id_to_model_element.get(cd_compartment.get("id"))
                if model_element is None:
                    model_element, _ = cls._make_and_add_compartment(
                        reading_context,
                        cd_compartment=cd_compartment,
                    )
            else:
                model_element = None
            if reading_context.layout is not None:
                layout_element = momapy.celldesigner.io.celldesigner._reading_layout.make_compartment_from_alias(
                    reading_context, cd_compartment, cd_compartment_alias
                )
                layout_element = momapy.builder.object_from_builder(layout_element)
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[cd_compartment_alias.get("id")] = (
                    layout_element
                )
            else:
                layout_element = None
            if reading_context.model is not None and reading_context.layout is not None:
                reading_context.layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
                )
        return model_element, layout_element

    @classmethod
    def _make_and_add_compartment(
        cls,
        reading_context,
        cd_compartment,
    ):
        if reading_context.model is not None:
            model_element = momapy.celldesigner.io.celldesigner._reading_model.make_compartment(
                reading_context, cd_compartment
            )
            if cd_compartment.get("outside") is not None:
                outside_model_element = reading_context.xml_id_to_model_element.get(
                    cd_compartment.get("outside")
                )
                # if outside is not already made, we make it
                if outside_model_element is None:
                    cd_outside = reading_context.xml_id_to_xml_element[cd_compartment.get("outside")]
                    outside_model_element, _ = cls._make_and_add_compartment(
                        reading_context,
                        cd_compartment=cd_outside,
                    )
                model_element.outside = outside_model_element
            model_element = momapy.builder.object_from_builder(model_element)
            model_element = momapy.io.utils.register_model_element(
                reading_context,
                model_element,
                reading_context.model.compartments,
                cd_compartment.get("id"),
            )
            momapy.celldesigner.io.celldesigner._reading_model.make_and_add_annotations(
                reading_context, cd_compartment, model_element
            )
            if reading_context.with_notes:
                notes = momapy.celldesigner.io.celldesigner._reading_model.make_notes(
                    cd_compartment
                )
                reading_context.map_element_to_notes[model_element].update(notes)
        else:
            model_element = None
        layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_species_template(
        cls,
        reading_context,
        cd_species_template,
    ):
        if reading_context.model is not None:
            key = momapy.celldesigner.io.celldesigner._reading_parsing.get_key_from_species_template(
                cd_species_template
            )
            model_element_cls = cls._KEY_TO_CLASS[key]
            model_element = (
                momapy.celldesigner.io.celldesigner._reading_model.make_species_template(
                    reading_context, cd_species_template, model_element_cls
                )
            )
            n_undefined_modification_residue_names = 0
            cd_modification_residues = (
                momapy.celldesigner.io.celldesigner._reading_parsing.get_modification_residues(
                    cd_species_template
                )
            )
            cd_modification_residues.sort(
                key=lambda cd_modification_residue: cd_modification_residue.get("angle")
            )
            for (
                cd_modification_residue
            ) in momapy.celldesigner.io.celldesigner._reading_parsing.get_modification_residues(
                cd_species_template
            ):
                if cd_modification_residue.get("name") is None:
                    n_undefined_modification_residue_names += 1
                    order = n_undefined_modification_residue_names
                else:
                    order = None
                modification_residue_model_element, _ = (
                    cls._make_and_add_modification_residue(
                        reading_context,
                        cd_modification_residue=cd_modification_residue,
                        super_cd_element=cd_species_template,
                        super_model_element=model_element,
                        order=order,
                    )
                )
            n_undefined_region_names = 0
            cd_regions = momapy.celldesigner.io.celldesigner._reading_parsing.get_regions(
                cd_species_template
            )
            cd_regions.sort(key=lambda cd_region: cd_region.get("pos"))
            for cd_region in cd_regions:
                if cd_region.get("name") is None:
                    n_undefined_region_names += 1
                    order = n_undefined_region_names
                else:
                    order = None
                region_model_element, _ = cls._make_and_add_region(
                    reading_context,
                    cd_region=cd_region,
                    super_cd_element=cd_species_template,
                    super_model_element=model_element,
                    order=order,
                )
            model_element = momapy.builder.object_from_builder(model_element)
            model_element = momapy.io.utils.register_model_element(
                reading_context,
                model_element,
                reading_context.model.species_templates,
                cd_species_template.get("id"),
            )
        else:
            model_element = None
        layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_modification_residue(
        cls,
        reading_context,
        cd_modification_residue,
        super_cd_element,
        super_model_element,
        order,
    ):
        if reading_context.model is not None:
            model_element = (
                momapy.celldesigner.io.celldesigner._reading_model.make_modification_residue(
                    reading_context, cd_modification_residue, super_cd_element, order
                )
            )
            cd_modification_residue_id = model_element.id_
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.modification_residues.add(model_element)
            # we use the model element's id (a composite of the parent and
            # child cd ids) rather than the cd element's own id
            reading_context.xml_id_to_model_element[cd_modification_residue_id] = model_element
        else:
            model_element = None
        layout_element = None  # purely a model element
        return model_element, layout_element

    @classmethod
    def _make_and_add_region(
        cls,
        reading_context,
        cd_region,
        super_cd_element,
        super_model_element,
        order,
    ):
        if reading_context.model is not None:
            key = momapy.celldesigner.io.celldesigner._reading_parsing.get_key_from_region(
                cd_region
            )
            model_element_cls = cls._KEY_TO_CLASS[key]
            model_element = momapy.celldesigner.io.celldesigner._reading_model.make_region(
                reading_context, cd_region, model_element_cls, super_cd_element, order
            )
            cd_region_id = model_element.id_
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.regions.add(model_element)
            # we use the model element's id (a composite of the parent and
            # child cd ids) rather than the cd element's own id
            reading_context.xml_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        layout_element = None  # purely a model element
        return model_element, layout_element

    @classmethod
    def _make_and_add_species(
        cls,
        reading_context,
        cd_species_alias,
        super_cd_element=None,
        super_model_element=None,
        super_layout_element=None,
        pending_mappings=None,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            cd_species = reading_context.xml_id_to_xml_element[cd_species_alias.get("species")]
            key = momapy.celldesigner.io.celldesigner._reading_parsing.get_key_from_species(
                cd_species, reading_context.xml_id_to_xml_element
            )
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            name = momapy.celldesigner.io.celldesigner._reading_parsing.make_name(
                cd_species.get("name")
            )
            cd_species_homodimer = (
                momapy.celldesigner.io.celldesigner._reading_parsing.get_homodimer(cd_species)
            )
            if cd_species_homodimer is not None:
                homomultimer = int(cd_species_homodimer)
            else:
                homomultimer = 1
            cd_species_hypothetical = (
                momapy.celldesigner.io.celldesigner._reading_parsing.get_hypothetical(
                    cd_species
                )
            )
            if cd_species_hypothetical is not None:
                hypothetical = cd_species_hypothetical.text == "true"
            else:
                hypothetical = False
            cd_species_activity = (
                momapy.celldesigner.io.celldesigner._reading_parsing.get_activity(
                    cd_species_alias
                )
            )
            if cd_species_activity is not None:
                active = cd_species_activity.text == "active"
                if active:
                    cd_species.attrib["id"] = f"{cd_species.get('id')}_active"
            if reading_context.model is not None:
                model_element = momapy.celldesigner.io.celldesigner._reading_model.make_species(
                    reading_context,
                    cd_species,
                    model_element_cls,
                    name,
                    homomultimer,
                    hypothetical,
                    active,
                )
            else:
                model_element = None
            if reading_context.layout is not None:
                layout_element = (
                    momapy.celldesigner.io.celldesigner._reading_layout.make_species(
                        reading_context,
                        cd_species_alias,
                        layout_element_cls,
                        name,
                        homomultimer,
                        hypothetical,
                        active,
                    )
                )
            else:
                layout_element = None
            covered_cd_residue_ids = set()
            for (
                cd_species_modification
            ) in momapy.celldesigner.io.celldesigner._reading_parsing.get_species_modifications(
                cd_species
            ):
                covered_cd_residue_ids.add(cd_species_modification.get("residue"))
                modification_model_element, modification_layout_element = (
                    cls._make_and_add_species_modification(
                        reading_context,
                        cd_species_modification=cd_species_modification,
                        super_cd_element=cd_species_alias,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
            cd_species_template = momapy.celldesigner.io.celldesigner._reading_parsing.get_template_from_species_alias(
                cd_species_alias, reading_context.xml_id_to_xml_element
            )
            for (
                cd_modification_residue
            ) in momapy.celldesigner.io.celldesigner._reading_parsing.get_modification_residues(
                cd_species_template
            ):
                residue_xml_id = cd_modification_residue.get("id")
                if residue_xml_id not in covered_cd_residue_ids:
                    cls._make_and_add_species_modification(
                        reading_context,
                        cd_species_modification={
                            "state": "empty",
                            "residue": residue_xml_id,
                        },
                        super_cd_element=cd_species_alias,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
            for cd_species_structural_state in momapy.celldesigner.io.celldesigner._reading_parsing.get_species_structural_states(
                cd_species
            ):
                (
                    structural_state_model_element,
                    structural_state_layout_element,
                ) = cls._make_and_add_species_structural_state(
                    reading_context,
                    cd_species_structural_state=cd_species_structural_state,
                    super_cd_element=cd_species_alias,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                )
            cd_subunits = [
                reading_context.xml_id_to_xml_element[cd_subunit_id]
                for cd_subunit_id in reading_context.cd_complex_alias_id_to_cd_included_species_ids[
                    cd_species_alias.get("id")
                ]
            ]
            local_mappings = []
            for cd_subunit in cd_subunits:
                subunit_model_element, subunit_layout_element = (
                    cls._make_and_add_species(
                        reading_context,
                        cd_species_alias=cd_subunit,
                        super_cd_element=cd_species_alias,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                        pending_mappings=local_mappings,
                    )
                )
            if reading_context.model is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                if super_model_element is None:  # species case
                    model_element = momapy.io.utils.register_model_element(
                        reading_context,
                        model_element,
                        reading_context.model.species,
                        cd_species.get("id"),
                    )
                    momapy.celldesigner.io.celldesigner._reading_model.make_and_add_annotations(
                        reading_context, cd_species, model_element
                    )
                    if reading_context.with_notes:
                        notes = momapy.celldesigner.io.celldesigner._reading_model.make_notes(
                            cd_species
                        )
                        reading_context.map_element_to_notes[model_element].update(notes)
                else:  # included species case
                    model_element = momapy.utils.add_or_replace_element_in_set(
                        model_element,
                        super_model_element.subunits,
                        func=lambda new, old: new.id_ < old.id_,
                    )
                    if reading_context.with_annotations:
                        cd_notes = (
                            momapy.celldesigner.io.celldesigner._reading_parsing.get_notes(
                                cd_species
                            )
                        )
                        annotations = momapy.celldesigner.io.celldesigner._reading_model.make_annotations_from_notes(
                            cd_notes
                        )
                        if annotations:
                            reading_context.map_element_to_annotations[model_element].update(
                                annotations
                            )
                    if reading_context.with_notes:
                        notes = momapy.celldesigner.io.celldesigner._reading_model.make_notes(
                            cd_species
                        )
                        reading_context.map_element_to_notes[model_element].update(notes)
                # Apply deferred subunit mappings.  Use model_element
                # (the registered frozen parent) instead of the
                # super_model_element captured during subunit creation
                # (which is still a builder reference).
                for (
                    subunit_layout_element,
                    subunit_model_element,
                    stale_super_model_element,
                ) in local_mappings:
                    if pending_mappings is not None:
                        pending_mappings.append(
                            (subunit_layout_element, subunit_model_element, model_element)
                        )
                    else:
                        reading_context.layout_model_mapping.add_mapping(
                            subunit_layout_element,
                            (subunit_model_element, model_element),
                            replace=True,
                        )
                reading_context.xml_id_to_model_element[cd_species.get("id")] = model_element
                reading_context.xml_id_to_model_element[cd_species_alias.get("id")] = model_element
            if reading_context.layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                if super_layout_element is None:  # species case
                    reading_context.layout.layout_elements.append(layout_element)
                else:  # included species case
                    super_layout_element.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[cd_species_alias.get("id")] = layout_element
            if reading_context.model is not None and reading_context.layout is not None:
                if super_layout_element is None:  # species case
                    reading_context.layout_model_mapping.add_mapping(
                        layout_element, model_element, replace=True
                    )
                else:  # included species case
                    if pending_mappings is not None:
                        pending_mappings.append(
                            (layout_element, model_element, super_model_element)
                        )
                    else:
                        reading_context.layout_model_mapping.add_mapping(
                            layout_element,
                            (model_element, super_model_element),
                            replace=True,
                        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_species_modification(
        cls,
        reading_context,
        cd_species_modification,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            cd_species_modification_state = cd_species_modification.get("state")
            if cd_species_modification_state == "empty":
                modification_state = None
            else:
                modification_state = momapy.celldesigner.core.ModificationState[
                    cd_species_modification_state.upper()
                    .replace(" ", "_")  # for DON'T CARE
                    .replace("'", "_")
                ]
            cd_species_template = momapy.celldesigner.io.celldesigner._reading_parsing.get_template_from_species_alias(
                super_cd_element,
                reading_context.xml_id_to_xml_element,
            )
            cd_modification_residue_id = f"{cd_species_template.get('id')}_{cd_species_modification.get('residue')}"
            cd_species_id = super_cd_element.get("species")
            cd_residue_id = cd_species_modification.get("residue")
            cd_species_modification_id = f"{cd_species_id}_{cd_residue_id}"
            if reading_context.model is not None:
                model_element = momapy.celldesigner.io.celldesigner._reading_model.make_species_modification(
                    reading_context,
                    modification_state,
                    cd_modification_residue_id,
                )
                model_element.id_ = cd_species_modification_id
                model_element = momapy.builder.object_from_builder(model_element)
                super_model_element.modifications.add(model_element)
            else:
                model_element = None
            if reading_context.layout is not None:
                cd_modification_residue = reading_context.xml_id_to_xml_element[
                    cd_modification_residue_id
                ]  # can also be of type ModificationSite for Genes, RNAs, etc.
                layout_element = momapy.celldesigner.io.celldesigner._reading_layout.make_species_modification(
                    reading_context,
                    cd_modification_residue,
                    modification_state,
                    super_layout_element,
                )
                layout_element.id_ = f"{cd_species_modification_id}_layout"
                layout_element = momapy.builder.object_from_builder(layout_element)
                super_layout_element.layout_elements.append(layout_element)
            else:
                layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_species_structural_state(
        cls,
        reading_context,
        cd_species_structural_state,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        cd_species_id = super_cd_element.get("species")
        cd_structural_state_value = cd_species_structural_state.get("structuralState")
        cd_structural_state_id = f"{cd_species_id}_{cd_structural_state_value}"
        if reading_context.model is not None:
            model_element = momapy.celldesigner.io.celldesigner._reading_model.make_species_structural_state(
                reading_context, cd_species_structural_state
            )
            model_element.id_ = cd_structural_state_id
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.structural_states.add(model_element)
        else:
            model_element = None
        if reading_context.layout is not None:
            layout_element = momapy.celldesigner.io.celldesigner._reading_layout.make_species_structural_state(
                reading_context, cd_species_structural_state, super_layout_element
            )
            layout_element.id_ = f"{cd_structural_state_id}_layout"
            layout_element = momapy.builder.object_from_builder(layout_element)
            super_layout_element.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_reaction(
        cls,
        reading_context,
        cd_reaction,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            key = momapy.celldesigner.io.celldesigner._reading_parsing.get_key_from_reaction(
                cd_reaction
            )
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            cd_base_reactants = (
                momapy.celldesigner.io.celldesigner._reading_parsing.get_base_reactants(
                    cd_reaction
                )
            )
            cd_base_products = (
                momapy.celldesigner.io.celldesigner._reading_parsing.get_base_products(
                    cd_reaction
                )
            )
            if reading_context.model is not None:
                model_element = (
                    momapy.celldesigner.io.celldesigner._reading_model.make_reaction(
                        reading_context, cd_reaction, model_element_cls
                    )
                )
            else:
                model_element = None
            if reading_context.layout is not None:
                (
                    layout_element,
                    make_base_reactant_layouts,
                    make_base_product_layouts,
                ) = momapy.celldesigner.io.celldesigner._reading_layout.make_reaction(
                    reading_context,
                    cd_reaction,
                    layout_element_cls,
                    cd_base_reactants,
                    cd_base_products,
                )
            else:
                layout_element = None
                make_base_reactant_layouts = False
                make_base_product_layouts = False
            if reading_context.layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
            participant_map_elements = []
            layout_elements_for_mapping = []
            for n_cd_base_reactant, cd_base_reactant in enumerate(cd_base_reactants):
                reactant_model_element, reactant_layout_element = (
                    cls._make_and_add_reactant_from_base(
                        reading_context,
                        cd_base_reactant=cd_base_reactant,
                        n_cd_base_reactant=n_cd_base_reactant,
                        make_layout=make_base_reactant_layouts,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if reading_context.model is not None and reading_context.layout is not None:
                    if reactant_layout_element is not None:
                        participant_map_elements.append(
                            (reactant_model_element, reactant_layout_element)
                        )
                    layout_elements_for_mapping.append(
                        reading_context.xml_id_to_layout_element[cd_base_reactant.get("alias")]
                    )
            for (
                cd_reactant_link
            ) in momapy.celldesigner.io.celldesigner._reading_parsing.get_reactant_links(
                cd_reaction
            ):
                reactant_model_element, reactant_layout_element = (
                    cls._make_and_add_reactant_from_link(
                        reading_context,
                        cd_reactant_link=cd_reactant_link,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if reading_context.model is not None and reading_context.layout is not None:
                    participant_map_elements.append(
                        (reactant_model_element, reactant_layout_element)
                    )
                    layout_elements_for_mapping.append(
                        reading_context.xml_id_to_layout_element[cd_reactant_link.get("alias")]
                    )
            for n_cd_base_product, cd_base_product in enumerate(cd_base_products):
                product_model_element, product_layout_element = (
                    cls._make_and_add_product_from_base(
                        reading_context,
                        cd_base_product=cd_base_product,
                        n_cd_base_product=n_cd_base_product,
                        make_layout=make_base_product_layouts,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if reading_context.model is not None and reading_context.layout is not None:
                    if product_layout_element is not None:
                        participant_map_elements.append(
                            (product_model_element, product_layout_element)
                        )
                    layout_elements_for_mapping.append(
                        reading_context.xml_id_to_layout_element[cd_base_product.get("alias")]
                    )
            for (
                cd_product_link
            ) in momapy.celldesigner.io.celldesigner._reading_parsing.get_product_links(
                cd_reaction
            ):
                product_model_element, product_layout_element = (
                    cls._make_and_add_product_from_link(
                        reading_context,
                        cd_product_link=cd_product_link,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if reading_context.model is not None and reading_context.layout is not None:
                    participant_map_elements.append(
                        (product_model_element, product_layout_element)
                    )
                    layout_elements_for_mapping.append(
                        reading_context.xml_id_to_layout_element[cd_product_link.get("alias")]
                    )
            for cd_reaction_modification in (
                momapy.celldesigner.io.celldesigner._reading_parsing.get_reaction_modifications(
                    cd_reaction
                )
            ):
                modifier_model_element, modifier_layout_element = (
                    cls._make_and_add_modifier(
                        reading_context,
                        cd_reaction_modification=cd_reaction_modification,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if reading_context.model is not None and reading_context.layout is not None:
                    participant_map_elements.append(
                        (modifier_model_element, modifier_layout_element)
                    )
                    layout_elements_for_mapping.append(modifier_layout_element.source)
            if reading_context.model is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.io.utils.register_model_element(
                    reading_context,
                    model_element,
                    reading_context.model.reactions,
                    cd_reaction.get("id"),
                )
                momapy.celldesigner.io.celldesigner._reading_model.make_and_add_annotations(
                    reading_context, cd_reaction, model_element
                )
                if reading_context.with_notes:
                    notes = momapy.celldesigner.io.celldesigner._reading_model.make_notes(
                        cd_reaction
                    )
                    reading_context.map_element_to_notes[model_element].update(notes)
            if reading_context.layout is not None:
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[layout_element.id_] = layout_element
                layout_elements_for_mapping.append(layout_element)
            if reading_context.model is not None and reading_context.layout is not None:
                expanded = set()
                for layout_element_for_mapping in layout_elements_for_mapping:
                    existing_key = reading_context.layout_model_mapping._singleton_to_key.get(
                        layout_element_for_mapping
                    )
                    if existing_key is not None:
                        expanded |= existing_key
                    else:
                        expanded.add(layout_element_for_mapping)
                reading_context.layout_model_mapping.add_mapping(
                    frozenset(expanded),
                    model_element,
                    replace=True,
                    anchor=layout_element,
                )
                for (
                    participant_model_element,
                    participant_layout_element,
                ) in participant_map_elements:
                    reading_context.layout_model_mapping.add_mapping(
                        participant_layout_element,
                        (participant_model_element, model_element),
                        replace=True,
                    )
        return model_element, layout_element

    @classmethod
    def _make_and_add_reactant_from_base(
        cls,
        reading_context,
        cd_base_reactant,
        n_cd_base_reactant,
        make_layout,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if reading_context.model is not None:
            model_element = (
                momapy.celldesigner.io.celldesigner._reading_model.make_reactant_from_base(
                    reading_context,
                    cd_base_reactant,
                    super_cd_element,
                )
            )
            model_element = momapy.builder.object_from_builder(model_element)
            model_element = momapy.utils.add_or_replace_element_in_set(
                model_element,
                super_model_element.reactants,
                func=lambda new, old: new.id_ < old.id_,
            )
            reading_context.xml_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if reading_context.layout is not None and make_layout:
            layout_element = (
                momapy.celldesigner.io.celldesigner._reading_layout.make_reactant_from_base(
                    reading_context,
                    cd_base_reactant,
                    n_cd_base_reactant,
                    super_cd_element,
                    super_layout_element,
                )
            )
            layout_element = momapy.builder.object_from_builder(layout_element)
            reading_context.layout.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_reactant_from_link(
        cls,
        reading_context,
        cd_reactant_link,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if reading_context.model is not None:
            model_element = (
                momapy.celldesigner.io.celldesigner._reading_model.make_reactant_from_link(
                    reading_context,
                    cd_reactant_link,
                    super_cd_element,
                )
            )
            model_element = momapy.builder.object_from_builder(model_element)
            model_element = momapy.utils.add_or_replace_element_in_set(
                model_element,
                super_model_element.reactants,
                func=lambda new, old: new.id_ < old.id_,
            )
            reading_context.xml_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if reading_context.layout is not None:
            layout_element = (
                momapy.celldesigner.io.celldesigner._reading_layout.make_reactant_from_link(
                    reading_context,
                    cd_reactant_link,
                    super_layout_element,
                )
            )
            layout_element = momapy.builder.object_from_builder(layout_element)
            reading_context.layout.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_product_from_base(
        cls,
        reading_context,
        cd_base_product,
        n_cd_base_product,
        make_layout,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if reading_context.model is not None:
            model_element = (
                momapy.celldesigner.io.celldesigner._reading_model.make_product_from_base(
                    reading_context,
                    cd_base_product,
                    super_cd_element,
                )
            )
            model_element = momapy.builder.object_from_builder(model_element)
            model_element = momapy.utils.add_or_replace_element_in_set(
                model_element,
                super_model_element.products,
                func=lambda new, old: new.id_ < old.id_,
            )
            reading_context.xml_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if reading_context.layout is not None and make_layout:
            layout_element = (
                momapy.celldesigner.io.celldesigner._reading_layout.make_product_from_base(
                    reading_context,
                    cd_base_product,
                    n_cd_base_product,
                    super_cd_element,
                    super_layout_element,
                )
            )
            layout_element = momapy.builder.object_from_builder(layout_element)
            reading_context.layout.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_product_from_link(
        cls,
        reading_context,
        cd_product_link,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if reading_context.model is not None:
            model_element = (
                momapy.celldesigner.io.celldesigner._reading_model.make_product_from_link(
                    reading_context,
                    cd_product_link,
                    super_cd_element,
                )
            )
            model_element = momapy.builder.object_from_builder(model_element)
            model_element = momapy.utils.add_or_replace_element_in_set(
                model_element,
                super_model_element.products,
                func=lambda new, old: new.id_ < old.id_,
            )
            reading_context.xml_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if reading_context.layout is not None:
            layout_element = (
                momapy.celldesigner.io.celldesigner._reading_layout.make_product_from_link(
                    reading_context,
                    cd_product_link,
                    super_layout_element,
                )
            )
            layout_element = momapy.builder.object_from_builder(layout_element)
            reading_context.layout.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_modifier(
        cls,
        reading_context,
        cd_reaction_modification,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            key = momapy.celldesigner.io.celldesigner._reading_parsing.get_key_from_reaction_modification(
                cd_reaction_modification
            )
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            has_boolean_input = momapy.celldesigner.io.celldesigner._reading_parsing.has_boolean_input_from_modification(
                cd_reaction_modification
            )
            if has_boolean_input:
                source_model_element, source_layout_element = (
                    cls._make_and_add_logic_gate(
                        reading_context,
                        cd_reaction_modification_or_cd_gate_member=cd_reaction_modification,
                        cd_reaction_id=super_cd_element.get("id"),
                    )
                )
            # Find the SBML modifierSpeciesReference metaid by
            # matching the species id from the modification element.
            modifier_metaid = None
            cd_modifier_species_id = cd_reaction_modification.get("modifiers")
            if cd_modifier_species_id is not None:
                for modifier_species_reference in (
                    momapy.celldesigner.io.celldesigner._reading_parsing.get_modifier_species_references(
                        super_cd_element
                    )
                ):
                    if modifier_species_reference.get("species") == cd_modifier_species_id:
                        modifier_metaid = modifier_species_reference.get(
                            "metaid"
                        )
                        break
            if reading_context.model is not None:
                if not has_boolean_input:
                    source_model_element = reading_context.xml_id_to_model_element[
                        cd_reaction_modification.get("aliases")
                    ]
                model_element = (
                    momapy.celldesigner.io.celldesigner._reading_model.make_modifier(
                        reading_context,
                        model_element_cls,
                        source_model_element,
                        metaid=modifier_metaid,
                    )
                )
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    super_model_element.modifiers,
                    func=lambda new, old: new.id_ < old.id_,
                )
                reading_context.xml_id_to_model_element[model_element.id_] = (
                    model_element
                )
            else:
                model_element = None
            if reading_context.layout is not None:
                if not has_boolean_input:
                    source_layout_element = reading_context.xml_id_to_layout_element[
                        cd_reaction_modification.get("aliases")
                    ]
                layout_element = (
                    momapy.celldesigner.io.celldesigner._reading_layout.make_modifier(
                        reading_context,
                        cd_reaction_modification,
                        layout_element_cls,
                        source_layout_element,
                        super_layout_element,
                        has_boolean_input,
                    )
                )
                layout_element.id_ = f"{modifier_metaid}_layout"
                layout_element = momapy.builder.object_from_builder(layout_element)
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[layout_element.id_] = (
                    layout_element
                )
            else:
                layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_logic_gate(
        cls,
        reading_context,
        cd_reaction_modification_or_cd_gate_member,
        cd_reaction_id,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            key = momapy.celldesigner.io.celldesigner._reading_parsing.get_key_from_gate_member(
                cd_reaction_modification_or_cd_gate_member
            )
            cd_modifiers = cd_reaction_modification_or_cd_gate_member.get("aliases")
            sorted_aliases = "_".join(sorted(cd_modifiers.split(",")))
            cd_gate_id = f"{cd_reaction_id}_gate_{sorted_aliases}"
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if reading_context.model is not None:
                model_element = (
                    momapy.celldesigner.io.celldesigner._reading_model.make_logic_gate(
                        reading_context,
                        model_element_cls,
                        cd_modifiers.split(","),
                    )
                )
                model_element.id_ = cd_gate_id
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.io.utils.register_model_element(
                    reading_context,
                    model_element,
                    reading_context.model.boolean_logic_gates,
                    cd_gate_id,
                )
            else:
                model_element = None
            if reading_context.layout is not None:
                layout_element = (
                    momapy.celldesigner.io.celldesigner._reading_layout.make_logic_gate(
                        reading_context,
                        cd_reaction_modification_or_cd_gate_member,
                        layout_element_cls,
                    )
                )
                layout_element.id_ = f"{cd_gate_id}_layout"
                layout_element = momapy.builder.object_from_builder(
                    layout_element
                )
                reading_context.layout.layout_elements.append(layout_element)
                cd_modifiers = (
                    cd_reaction_modification_or_cd_gate_member.get("aliases")
                )
                for cd_input_id in cd_modifiers.split(","):
                    input_layout_element = reading_context.xml_id_to_layout_element[
                        cd_input_id
                    ]
                    logic_arc = (
                        momapy.celldesigner.io.celldesigner._reading_layout.make_logic_arc(
                            reading_context,
                            layout_element,
                            input_layout_element,
                        )
                    )
                    logic_arc.id_ = f"{cd_gate_id}_arc_{cd_input_id}"
                    logic_arc = momapy.builder.object_from_builder(
                        logic_arc
                    )
                    reading_context.layout.layout_elements.append(logic_arc)
            else:
                layout_element = None
            if reading_context.model is not None and reading_context.layout is not None:
                reading_context.layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
                )
        return model_element, layout_element

    @classmethod
    def _make_and_add_modulation(
        cls,
        reading_context,
        cd_reaction,
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            key = momapy.celldesigner.io.celldesigner._reading_parsing.get_key_from_reaction(
                cd_reaction
            )
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            has_boolean_input = momapy.celldesigner.io.celldesigner._reading_parsing.has_boolean_input_from_reaction(
                cd_reaction
            )
            cd_base_reactant = (
                momapy.celldesigner.io.celldesigner._reading_parsing.get_base_reactants(
                    cd_reaction
                )[0]
            )
            cd_base_product = (
                momapy.celldesigner.io.celldesigner._reading_parsing.get_base_products(
                    cd_reaction
                )[0]
            )
            if has_boolean_input:
                cd_gate_members = (
                    momapy.celldesigner.io.celldesigner._reading_parsing.get_gate_members(
                        cd_reaction
                    )
                )
                cd_gate_member = cd_gate_members[0]
                source_model_element, source_layout_element = (
                    cls._make_and_add_logic_gate(
                        reading_context,
                        cd_reaction_modification_or_cd_gate_member=cd_gate_member,
                        cd_reaction_id=cd_reaction.get("id"),
                    )
                )
            if reading_context.model is not None:
                if has_boolean_input:
                    pass  # source_model_element already set above
                else:
                    source_model_element = reading_context.xml_id_to_model_element[
                        cd_base_reactant.get("alias")
                    ]
                target_model_element = reading_context.xml_id_to_model_element[
                    cd_base_product.get("alias")
                ]
                model_element = (
                    momapy.celldesigner.io.celldesigner._reading_model.make_modulation(
                        reading_context,
                        cd_reaction,
                        model_element_cls,
                        source_model_element,
                        target_model_element,
                    )
                )
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.io.utils.register_model_element(
                    reading_context,
                    model_element,
                    reading_context.model.modulations,
                    cd_reaction.get("id"),
                )
                momapy.celldesigner.io.celldesigner._reading_model.make_and_add_annotations(
                    reading_context, cd_reaction, model_element
                )
                if reading_context.with_notes:
                    notes = momapy.celldesigner.io.celldesigner._reading_model.make_notes(
                        cd_reaction
                    )
                    reading_context.map_element_to_notes[model_element].update(notes)
            else:
                model_element = None
            if reading_context.layout is not None:
                if not has_boolean_input:
                    source_layout_element = reading_context.xml_id_to_layout_element[
                        cd_base_reactant.get("alias")
                    ]
                target_layout_element = reading_context.xml_id_to_layout_element[
                    cd_base_product.get("alias")
                ]
                layout_element = (
                    momapy.celldesigner.io.celldesigner._reading_layout.make_modulation(
                        reading_context,
                        cd_reaction,
                        layout_element_cls,
                        source_layout_element,
                        target_layout_element,
                        has_boolean_input,
                        cd_base_reactant,
                        cd_base_product,
                    )
                )
                layout_element = momapy.builder.object_from_builder(layout_element)
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[layout_element.id_] = layout_element
            else:
                layout_element = None
            if reading_context.model is not None and reading_context.layout is not None:
                source_mapping_key = reading_context.layout_model_mapping._singleton_to_key.get(
                    source_layout_element
                )
                if source_mapping_key is not None:
                    source_layout_elements = source_mapping_key
                else:
                    source_layout_elements = frozenset([source_layout_element])
                target_mapping_key = reading_context.layout_model_mapping._singleton_to_key.get(
                    target_layout_element
                )
                if target_mapping_key is not None:
                    target_layout_elements = target_mapping_key
                else:
                    target_layout_elements = frozenset([target_layout_element])
                reading_context.layout_model_mapping.add_mapping(
                    frozenset([layout_element])
                    | source_layout_elements
                    | target_layout_elements,
                    model_element,
                    replace=True,
                    anchor=layout_element,
                )
        return model_element, layout_element
