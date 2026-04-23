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
  ``f"{reaction/@id}_layout"``.

The map, model and layout IDs are derived from the SBML ``model/@id``:
``map_.id_`` = ``model/@id``, ``model.id_`` = ``f"{model/@id}_model"``,
``layout.id_`` = ``f"{model/@id}_layout"``.

Element-specific patterns:

- **Compartment**: model ``id_`` = ``compartment/@id``,
  layout ``id_`` = ``compartmentAlias/@id``.
- **Species**: model ``id_`` = ``species/@id`` (or
  ``f"{species/@id}_active"`` for active species),
  layout ``id_`` = ``speciesAlias/@id``.
- **Species Template**: model ``id_`` = ``proteinReference/@id``
  (etc.), no layout.
- **ModificationResidue / Region**: model ``id_`` =
  ``f"{template/@id}_{child/@id}"``, no layout.
- **Modification**: model ``id_`` =
  ``f"{species/@id}_{modification/@residue}"``,
  layout ``id_`` =
  ``f"{species/@id}_{modification/@residue}_layout"``.
- **StructuralState**: model ``id_`` =
  ``f"{species/@id}_{structuralState/@structuralState}"``,
  layout ``id_`` =
  ``f"{species/@id}_{structuralState/@structuralState}_layout"``.
  Spaces in the value are replaced with ``_``.
- **Reactant / Product**: model ``id_`` =
  ``speciesReference/@metaid`` (or
  ``f"{reaction/@id}_{speciesReference/@species}"`` fallback),
  layout ``id_`` = ``f"{model_id}_layout"`` (when present).
- **Modulator**: model ``id_`` =
  ``modifierSpeciesReference/@metaid``,
  layout ``id_`` =
  ``f"{modifierSpeciesReference/@metaid}_layout"``.
- **Reaction**: model ``id_`` = ``reaction/@id``,
  layout ``id_`` = ``f"{reaction/@id}_layout"``.
- **Modulation**: model ``id_`` = ``reaction/@id``,
  layout ``id_`` = ``f"{reaction/@id}_layout"``.
- **BooleanGate**: model ``id_`` =
  ``f"{reaction/@id}_gate_{sorted_aliases}"``,
  layout ``id_`` =
  ``f"{reaction/@id}_gate_{sorted_aliases}_layout"``.
- **BooleanGateInput / LogicArcLayout**: model ``id_`` =
  ``f"{gate_id}_input_{speciesAlias/@id}"``,
  layout ``id_`` = ``f"{gate_id}_arc_{speciesAlias/@id}"``.
"""

import os
import collections
import dataclasses
import typing

import frozendict
import lxml.objectify

from momapy.core.mapping import LayoutModelMappingBuilder
from momapy.io.core import Reader, ReaderResult
from momapy.io.utils import (
    ReadingContext,
    apply_remap_to_layout_model_mapping,
    build_id_mappings,
    register_model_element,
)
from momapy.builder import object_from_builder
from momapy.utils import IdentitySurjectionDict, add_or_replace_element_in_set

from momapy.celldesigner.io.celldesigner._reading_parsing import (
    get_activity,
    get_base_products,
    get_base_reactants,
    get_compartments,
    get_complex_species_aliases,
    get_gate_members,
    get_height,
    get_homodimer,
    get_hypothetical,
    get_included_complex_species_aliases,
    get_included_species,
    get_included_species_aliases,
    get_key_from_gate_member,
    get_key_from_reaction,
    get_key_from_reaction_modification,
    get_key_from_region,
    get_key_from_species,
    get_key_from_species_template,
    get_modification_residues,
    get_modifier_species_references,
    get_notes,
    get_ordered_compartment_aliases,
    get_product_links,
    get_products,
    get_reactant_links,
    get_reactants,
    get_reaction_modifications,
    get_reactions,
    get_regions,
    get_species,
    get_species_aliases,
    get_species_modifications,
    get_species_structural_states,
    get_species_templates,
    get_template_from_species_alias,
    get_width,
    has_boolean_input_from_modification,
    has_boolean_input_from_reaction,
    make_complex_alias_to_included_ids_mapping,
    make_id_to_element_mapping,
    make_name,
)
from momapy.celldesigner.io.celldesigner import _reading_model
from momapy.celldesigner.io.celldesigner import _reading_layout
from momapy.celldesigner.model import (
    AndGate,
    AntisenseRNA,
    AntisenseRNATemplate,
    Catalysis,
    Catalyzer,
    CodingRegion,
    Complex,
    Degraded,
    Dissociation,
    Drug,
    Gene,
    GeneTemplate,
    GenericProtein,
    GenericProteinTemplate,
    HeterodimerAssociation,
    Inhibition,
    Inhibitor,
    Ion,
    IonChannel,
    IonChannelTemplate,
    KnownTransitionOmitted,
    ModificationSite,
    ModificationState,
    Modulation,
    Modulator,
    NegativeInfluence,
    NotGate,
    OrGate,
    Phenotype,
    PhysicalStimulation,
    PhysicalStimulator,
    PositiveInfluence,
    ProteinBindingDomain,
    RNA,
    RNATemplate,
    Reaction,
    Receptor,
    ReceptorTemplate,
    RegulatoryRegion,
    SimpleMolecule,
    StateTransition,
    Transcription,
    TranscriptionStartingSiteL,
    TranscriptionStartingSiteR,
    Translation,
    Transport,
    Trigger,
    Triggering,
    TruncatedProtein,
    TruncatedProteinTemplate,
    Truncation,
    Unknown,
    UnknownCatalysis,
    UnknownCatalyzer,
    UnknownGate,
    UnknownInhibition,
    UnknownInhibitor,
    UnknownModulation,
    UnknownNegativeInfluence,
    UnknownPhysicalStimulation,
    UnknownPositiveInfluence,
    UnknownTransition,
    UnknownTriggering,
)
from momapy.celldesigner.layout import (
    AndGateLayout,
    AntisenseRNALayout,
    CatalysisLayout,
    ComplexLayout,
    DegradedLayout,
    DissociationLayout,
    DrugLayout,
    GeneLayout,
    GenericProteinLayout,
    HeterodimerAssociationLayout,
    InhibitionLayout,
    IonChannelLayout,
    IonLayout,
    KnownTransitionOmittedLayout,
    ModulationLayout,
    NotGateLayout,
    OrGateLayout,
    PhenotypeLayout,
    PhysicalStimulationLayout,
    PositiveInfluenceLayout,
    RNALayout,
    ReceptorLayout,
    SimpleMoleculeLayout,
    StateTransitionLayout,
    TranscriptionLayout,
    TranslationLayout,
    TransportLayout,
    TriggeringLayout,
    TruncatedProteinLayout,
    TruncationLayout,
    UnknownCatalysisLayout,
    UnknownGateLayout,
    UnknownInhibitionLayout,
    UnknownLayout,
    UnknownModulationLayout,
    UnknownPhysicalStimulationLayout,
    UnknownPositiveInfluenceLayout,
    UnknownTransitionLayout,
    UnknownTriggeringLayout,
)


def _get_reactant_id(cd_base_reactant_or_link, cd_reaction):
    """Compute a deterministic ID for a reactant from XML data.

    Uses the SBML speciesReference metaid if available, otherwise
    falls back to ``f"{reaction_id}_{species_id}"``.

    Args:
        cd_base_reactant_or_link: The base reactant or reactant link element.
        cd_reaction: The parent reaction element.

    Returns:
        A deterministic ID string.
    """
    cd_species_id = cd_base_reactant_or_link.get(
        "species"
    ) or cd_base_reactant_or_link.get("reactant")
    for cd_reactant in get_reactants(cd_reaction):
        if cd_reactant.get("species") == cd_species_id:
            metaid = cd_reactant.get("metaid")
            if metaid is not None:
                return metaid
            break
    return f"{cd_reaction.get('id')}_{cd_species_id}"


def _get_product_id(cd_base_product_or_link, cd_reaction):
    """Compute a deterministic ID for a product from XML data.

    Uses the SBML speciesReference metaid if available, otherwise
    falls back to ``f"{reaction_id}_{species_id}"``.

    Args:
        cd_base_product_or_link: The base product or product link element.
        cd_reaction: The parent reaction element.

    Returns:
        A deterministic ID string.
    """
    cd_species_id = cd_base_product_or_link.get(
        "species"
    ) or cd_base_product_or_link.get("product")
    for cd_product in get_products(cd_reaction):
        if cd_product.get("species") == cd_species_id:
            metaid = cd_product.get("metaid")
            if metaid is not None:
                return metaid
            break
    return f"{cd_reaction.get('id')}_{cd_species_id}"


def _get_modifier_metaid(cd_reaction_modification, cd_reaction):
    """Resolve the SBML modifierSpeciesReference metaid for a modifier.

    Args:
        cd_reaction_modification: The modification element.
        cd_reaction: The parent reaction element.

    Returns:
        The metaid string, or None if not found.
    """
    cd_modifier_species_id = cd_reaction_modification.get("modifiers")
    if cd_modifier_species_id is not None:
        for modifier_species_reference in get_modifier_species_references(cd_reaction):
            if modifier_species_reference.get("species") == cd_modifier_species_id:
                return modifier_species_reference.get("metaid")
    return None


@dataclasses.dataclass
class CellDesignerReadingContext(ReadingContext):
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
    real_model_source_ids: set = dataclasses.field(default_factory=set)
    real_layout_source_ids: set = dataclasses.field(default_factory=set)
    canvas_width: float = 0.0
    canvas_height: float = 0.0


class CellDesignerReader(Reader):
    """Class for CellDesigner reader objects"""

    _KEY_TO_CLASS = {
        (
            "TEMPLATE",
            "GENERIC",
        ): GenericProteinTemplate,
        (
            "TEMPLATE",
            "ION_CHANNEL",
        ): IonChannelTemplate,
        ("TEMPLATE", "RECEPTOR"): ReceptorTemplate,
        (
            "TEMPLATE",
            "TRUNCATED",
        ): TruncatedProteinTemplate,
        ("TEMPLATE", "GENE"): GeneTemplate,
        ("TEMPLATE", "RNA"): RNATemplate,
        (
            "TEMPLATE",
            "ANTISENSE_RNA",
        ): AntisenseRNATemplate,
        ("SPECIES", "GENERIC"): (
            GenericProtein,
            GenericProteinLayout,
        ),
        ("SPECIES", "ION_CHANNEL"): (
            IonChannel,
            IonChannelLayout,
        ),
        ("SPECIES", "RECEPTOR"): (
            Receptor,
            ReceptorLayout,
        ),
        ("SPECIES", "TRUNCATED"): (
            TruncatedProtein,
            TruncatedProteinLayout,
        ),
        ("SPECIES", "GENE"): (
            Gene,
            GeneLayout,
        ),
        ("SPECIES", "RNA"): (
            RNA,
            RNALayout,
        ),
        ("SPECIES", "ANTISENSE_RNA"): (
            AntisenseRNA,
            AntisenseRNALayout,
        ),
        ("SPECIES", "PHENOTYPE"): (
            Phenotype,
            PhenotypeLayout,
        ),
        ("SPECIES", "ION"): (
            Ion,
            IonLayout,
        ),
        ("SPECIES", "SIMPLE_MOLECULE"): (
            SimpleMolecule,
            SimpleMoleculeLayout,
        ),
        ("SPECIES", "DRUG"): (
            Drug,
            DrugLayout,
        ),
        ("SPECIES", "COMPLEX"): (
            Complex,
            ComplexLayout,
        ),
        ("SPECIES", "UNKNOWN"): (
            Unknown,
            UnknownLayout,
        ),
        ("SPECIES", "DEGRADED"): (
            Degraded,
            DegradedLayout,
        ),
        ("REACTION", "STATE_TRANSITION"): (
            StateTransition,
            StateTransitionLayout,
        ),
        ("REACTION", "KNOWN_TRANSITION_OMITTED"): (
            KnownTransitionOmitted,
            KnownTransitionOmittedLayout,
        ),
        ("REACTION", "UNKNOWN_TRANSITION"): (
            UnknownTransition,
            UnknownTransitionLayout,
        ),
        ("REACTION", "TRANSCRIPTION"): (
            Transcription,
            TranscriptionLayout,
        ),
        ("REACTION", "TRANSLATION"): (
            Translation,
            TranslationLayout,
        ),
        ("REACTION", "TRANSPORT"): (
            Transport,
            TransportLayout,
        ),
        ("REACTION", "HETERODIMER_ASSOCIATION"): (
            HeterodimerAssociation,
            HeterodimerAssociationLayout,
        ),
        ("REACTION", "DISSOCIATION"): (
            Dissociation,
            DissociationLayout,
        ),
        ("REACTION", "TRUNCATION"): (
            Truncation,
            TruncationLayout,
        ),
        ("REACTION", "CATALYSIS"): (
            Catalysis,
            CatalysisLayout,
        ),
        ("REACTION", "UNKNOWN_CATALYSIS"): (
            UnknownCatalysis,
            UnknownCatalysisLayout,
        ),
        ("REACTION", "INHIBITION"): (
            Inhibition,
            InhibitionLayout,
        ),
        ("REACTION", "UNKNOWN_INHIBITION"): (
            UnknownInhibition,
            UnknownInhibitionLayout,
        ),
        ("REACTION", "PHYSICAL_STIMULATION"): (
            PhysicalStimulation,
            PhysicalStimulationLayout,
        ),
        ("REACTION", "MODULATION"): (
            Modulation,
            ModulationLayout,
        ),
        ("REACTION", "TRIGGER"): (
            Triggering,
            TriggeringLayout,
        ),
        ("REACTION", "POSITIVE_INFLUENCE"): (
            PositiveInfluence,
            PositiveInfluenceLayout,
        ),
        ("REACTION", "UNKNOWN_POSITIVE_INFLUENCE"): (
            UnknownPositiveInfluence,
            UnknownPositiveInfluenceLayout,
        ),
        ("REACTION", "NEGATIVE_INFLUENCE"): (
            NegativeInfluence,
            InhibitionLayout,
        ),
        ("REACTION", "UNKNOWN_NEGATIVE_INFLUENCE"): (
            UnknownNegativeInfluence,
            UnknownInhibitionLayout,
        ),
        ("REACTION", "REDUCED_PHYSICAL_STIMULATION"): (
            PhysicalStimulation,
            PhysicalStimulationLayout,
        ),
        ("REACTION", "UNKNOWN_REDUCED_PHYSICAL_STIMULATION"): (
            UnknownPhysicalStimulation,
            UnknownPhysicalStimulationLayout,
        ),
        ("REACTION", "REDUCED_MODULATION"): (
            Modulation,
            ModulationLayout,
        ),
        ("REACTION", "UNKNOWN_REDUCED_MODULATION"): (
            UnknownModulation,
            UnknownModulationLayout,
        ),
        ("REACTION", "REDUCED_TRIGGER"): (
            Triggering,
            TriggeringLayout,
        ),
        ("REACTION", "UNKNOWN_REDUCED_TRIGGER"): (
            UnknownTriggering,
            UnknownTriggeringLayout,
        ),
        ("MODIFIER", "CATALYSIS"): (
            Catalyzer,
            CatalysisLayout,
        ),
        ("MODIFIER", "UNKNOWN_CATALYSIS"): (
            UnknownCatalyzer,
            UnknownCatalysisLayout,
        ),
        ("MODIFIER", "INHIBITION"): (
            Inhibitor,
            InhibitionLayout,
        ),
        ("MODIFIER", "UNKNOWN_INHIBITION"): (
            UnknownInhibitor,
            UnknownInhibitionLayout,
        ),
        ("MODIFIER", "PHYSICAL_STIMULATION"): (
            PhysicalStimulator,
            PhysicalStimulationLayout,
        ),
        ("MODIFIER", "MODULATION"): (
            Modulator,
            ModulationLayout,
        ),
        ("MODIFIER", "TRIGGER"): (
            Trigger,
            TriggeringLayout,
        ),
        ("MODIFIER", "POSITIVE_INFLUENCE"): (  # pre-4.0 CellDesigner
            PhysicalStimulator,
            PhysicalStimulationLayout,
        ),
        ("MODIFIER", "NEGATIVE_INFLUENCE"): (  # pre-4.0 CellDesigner
            Inhibitor,
            InhibitionLayout,
        ),
        ("GATE", "BOOLEAN_LOGIC_GATE_AND"): (
            AndGate,
            AndGateLayout,
        ),
        ("GATE", "BOOLEAN_LOGIC_GATE_OR"): (
            OrGate,
            OrGateLayout,
        ),
        ("GATE", "BOOLEAN_LOGIC_GATE_NOT"): (
            NotGate,
            NotGateLayout,
        ),
        (
            "GATE",
            "BOOLEAN_LOGIC_GATE_UNKNOWN",
        ): (
            UnknownGate,
            UnknownGateLayout,
        ),
        (
            "REGION",
            "Modification Site",
        ): ModificationSite,
        (
            "REGION",
            "RegulatoryRegion",
        ): RegulatoryRegion,
        (
            "REGION",
            "transcriptionStartingSiteL",
        ): TranscriptionStartingSiteL,
        (
            "REGION",
            "transcriptionStartingSiteR",
        ): TranscriptionStartingSiteR,
        (
            "REGION",
            "CodingRegion",
        ): CodingRegion,
        (
            "REGION",
            "proteinBindingDomain",
        ): ProteinBindingDomain,
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
        reading_context.xml_id_to_xml_element = make_id_to_element_mapping(cd_model)
        reading_context.cd_complex_alias_id_to_cd_included_species_ids = (
            make_complex_alias_to_included_ids_mapping(cd_model)
        )
        reading_context.cd_compartment_aliases = get_ordered_compartment_aliases(
            cd_model, reading_context.xml_id_to_xml_element
        )
        reading_context.canvas_width = float(get_width(cd_model))
        reading_context.canvas_height = float(get_height(cd_model))
        reading_context.cd_compartments = get_compartments(cd_model)
        reading_context.cd_species_templates = get_species_templates(cd_model)
        reading_context.cd_species_aliases = get_species_aliases(
            cd_model
        ) + get_complex_species_aliases(cd_model)
        reading_context.cd_reactions = []
        reading_context.cd_modulations = []
        for cd_reaction in get_reactions(cd_model):
            key = get_key_from_reaction(cd_reaction)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if issubclass(model_element_cls, Reaction):
                reading_context.cd_reactions.append(cd_reaction)
            else:
                reading_context.cd_modulations.append(cd_reaction)
        # Collect real source IDs (XML attributes that exist verbatim in
        # the file), split by which side they name.  SBML-level ids
        # (species, compartments, templates, reactions, metaids) name
        # model entities; CellDesigner alias ids name layout entities.
        # Reaction ids name both a model reaction and its sole layout
        # arc.  Composite/synthetic IDs are excluded.
        real_model_ids = reading_context.real_model_source_ids
        real_layout_ids = reading_context.real_layout_source_ids
        for cd_compartment in reading_context.cd_compartments:
            real_model_ids.add(cd_compartment.get("id"))
        for cd_compartment_alias in reading_context.cd_compartment_aliases:
            real_layout_ids.add(cd_compartment_alias.get("id"))
        for cd_species_template in reading_context.cd_species_templates:
            real_model_ids.add(cd_species_template.get("id"))
        for cd_species in get_species(cd_model):
            real_model_ids.add(cd_species.get("id"))
        for cd_included_species in get_included_species(cd_model):
            real_model_ids.add(cd_included_species.get("id"))
        for cd_species_alias in reading_context.cd_species_aliases:
            real_layout_ids.add(cd_species_alias.get("id"))
        for cd_included_alias in get_included_species_aliases(cd_model):
            real_layout_ids.add(cd_included_alias.get("id"))
        for cd_included_complex_alias in get_included_complex_species_aliases(cd_model):
            real_layout_ids.add(cd_included_complex_alias.get("id"))
        for cd_reaction in (
            reading_context.cd_reactions + reading_context.cd_modulations
        ):
            reaction_id = cd_reaction.get("id")
            real_model_ids.add(reaction_id)
            real_layout_ids.add(reaction_id)
            # Metaids on speciesReferences and modifierSpeciesReferences
            # name SBML-level model entities; the matching layout ids
            # are synthetic (metaid + "_layout") and excluded.
            for cd_reactant in get_reactants(cd_reaction):
                metaid = cd_reactant.get("metaid")
                if metaid is not None:
                    real_model_ids.add(metaid)
            for cd_product in get_products(cd_reaction):
                metaid = cd_product.get("metaid")
                if metaid is not None:
                    real_model_ids.add(metaid)
            for cd_modifier in get_reaction_modifications(cd_reaction):
                metaid = _get_modifier_metaid(cd_modifier, cd_reaction)
                if metaid is not None:
                    real_model_ids.add(metaid)

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
    ) -> ReaderResult:
        """Read a CellDesigner file and return a reader result object"""
        cd_document = lxml.objectify.parse(file_path)
        cd_sbml = cd_document.getroot()
        (
            obj,
            annotations,
            notes,
            id_to_element,
            source_id_to_model_element,
            source_id_to_layout_element,
            source_id_to_annotations,
            source_id_to_notes,
        ) = cls._make_main_obj(
            cd_model=cd_sbml.model,
            return_type=return_type,
            with_model=with_model,
            with_layout=with_layout,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        result = ReaderResult(
            obj=obj,
            element_to_notes=notes,
            element_to_annotations=annotations,
            id_to_element=id_to_element,
            source_id_to_model_element=source_id_to_model_element,
            source_id_to_layout_element=source_id_to_layout_element,
            source_id_to_annotations=source_id_to_annotations,
            source_id_to_notes=source_id_to_notes,
            file_path=file_path,
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
            model = _reading_model.make_empty_model(cd_model)
        else:
            model = None
        if return_type == "layout" or return_type == "map" and with_layout:
            layout = _reading_layout.make_empty_layout(cd_model)
        else:
            layout = None
        element_to_annotations = collections.defaultdict(set)
        element_to_notes = collections.defaultdict(set)
        source_id_to_annotations = collections.defaultdict(set)
        source_id_to_notes = collections.defaultdict(set)
        if model is not None or layout is not None:
            if model is not None and layout is not None:
                layout_model_mapping = LayoutModelMappingBuilder()
            else:
                layout_model_mapping = None
            reading_context = CellDesignerReadingContext(
                xml_root=cd_model,
                model=model,
                layout=layout,
                xml_id_to_model_element=IdentitySurjectionDict(),
                element_to_annotations=element_to_annotations,
                element_to_notes=element_to_notes,
                source_id_to_annotations=source_id_to_annotations,
                source_id_to_notes=source_id_to_notes,
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
                if (
                    cd_compartment.get("id")
                    not in reading_context.xml_id_to_model_element
                ):
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
            if (
                reading_context.model_element_remap
                and reading_context.layout_model_mapping is not None
            ):
                apply_remap_to_layout_model_mapping(reading_context)
            if layout is not None:
                _reading_layout.set_layout_size_and_position(reading_context, cd_model)
        cd_model_id = cd_model.get("id")
        if cd_model_id is not None:
            if model is not None:
                model.id_ = f"{cd_model_id}_model"
            if layout is not None:
                layout.id_ = f"{cd_model_id}_layout"
        if return_type == "model":
            obj = object_from_builder(model)
            if with_annotations:
                annotations = _reading_model.make_annotations_from_element(cd_model)
                element_to_annotations[obj].update(annotations)
            if with_notes:
                notes = _reading_model.make_notes_from_element(cd_model)
                element_to_notes[obj].update(notes)
        elif return_type == "layout":
            obj = object_from_builder(layout)
        elif return_type == "map":
            map_ = _reading_model.make_empty_map(cd_model)
            map_.model = model
            map_.layout = layout
            map_.layout_model_mapping = layout_model_mapping
            obj = object_from_builder(map_)
            if with_annotations:
                annotations = _reading_model.make_annotations_from_element(cd_model)
                element_to_annotations[obj].update(annotations)
            if with_notes:
                notes = _reading_model.make_notes_from_element(cd_model)
                element_to_notes[obj].update(notes)
        annotations = frozendict.frozendict(
            {key: frozenset(val) for key, val in element_to_annotations.items()}
        )
        notes = frozendict.frozendict(
            {key: frozenset(val) for key, val in element_to_notes.items()}
        )
        frozen_source_id_to_annotations = frozendict.frozendict(
            {key: frozenset(val) for key, val in source_id_to_annotations.items()}
        )
        frozen_source_id_to_notes = frozendict.frozendict(
            {key: frozenset(val) for key, val in source_id_to_notes.items()}
        )
        if model is not None or layout is not None:
            id_to_element, source_id_to_model_element, source_id_to_layout_element = (
                build_id_mappings(
                    reading_context=reading_context,
                    obj=obj,
                    real_model_source_ids=reading_context.real_model_source_ids,
                    real_layout_source_ids=reading_context.real_layout_source_ids,
                )
            )
        else:
            id_to_element = None
            source_id_to_model_element = None
            source_id_to_layout_element = None
        return (
            obj,
            annotations,
            notes,
            id_to_element,
            source_id_to_model_element,
            source_id_to_layout_element,
            frozen_source_id_to_annotations,
            frozen_source_id_to_notes,
        )

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
                model_element = reading_context.xml_id_to_model_element.get(
                    cd_compartment.get("id")
                )
                if model_element is None:
                    model_element, _ = cls._make_and_add_compartment(
                        reading_context,
                        cd_compartment=cd_compartment,
                    )
            else:
                model_element = None
            if reading_context.layout is not None:
                layout_element = _reading_layout.make_compartment_from_alias(
                    reading_context, cd_compartment, cd_compartment_alias
                )
                layout_element = object_from_builder(layout_element)
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[
                    cd_compartment_alias.get("id")
                ] = layout_element
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
            model_element = _reading_model.make_compartment(
                reading_context, cd_compartment
            )
            if cd_compartment.get("outside") is not None:
                outside_model_element = reading_context.xml_id_to_model_element.get(
                    cd_compartment.get("outside")
                )
                # if outside is not already made, we make it
                if outside_model_element is None:
                    cd_outside = reading_context.xml_id_to_xml_element[
                        cd_compartment.get("outside")
                    ]
                    outside_model_element, _ = cls._make_and_add_compartment(
                        reading_context,
                        cd_compartment=cd_outside,
                    )
                model_element.outside = outside_model_element
            model_element = object_from_builder(model_element)
            model_element = register_model_element(
                reading_context,
                model_element,
                reading_context.model.compartments,
                cd_compartment.get("id"),
            )
            _reading_model.make_and_add_annotations(
                reading_context,
                cd_compartment,
                model_element,
                source_id=cd_compartment.get("id"),
            )
            _reading_model.make_and_add_notes(
                reading_context,
                cd_compartment,
                model_element,
                source_id=cd_compartment.get("id"),
            )
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
            key = get_key_from_species_template(cd_species_template)
            model_element_cls = cls._KEY_TO_CLASS[key]
            model_element = _reading_model.make_species_template(
                reading_context, cd_species_template, model_element_cls
            )
            n_undefined_modification_residue_names = 0
            cd_modification_residues = get_modification_residues(cd_species_template)
            cd_modification_residues.sort(
                key=lambda cd_modification_residue: cd_modification_residue.get("angle")
            )
            for cd_modification_residue in get_modification_residues(
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
            cd_regions = get_regions(cd_species_template)
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
            model_element = object_from_builder(model_element)
            model_element = register_model_element(
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
            model_element = _reading_model.make_modification_residue(
                reading_context, cd_modification_residue, super_cd_element, order
            )
            cd_modification_residue_id = model_element.id_
            model_element = object_from_builder(model_element)
            super_model_element.modification_residues.add(model_element)
            # we use the model element's id (a composite of the parent and
            # child cd ids) rather than the cd element's own id
            reading_context.xml_id_to_model_element[cd_modification_residue_id] = (
                model_element
            )
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
            key = get_key_from_region(cd_region)
            model_element_cls = cls._KEY_TO_CLASS[key]
            model_element = _reading_model.make_region(
                reading_context,
                cd_region,
                model_element_cls,
                super_cd_element,
                order,
            )
            cd_region_id = model_element.id_
            model_element = object_from_builder(model_element)
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
    ):
        if reading_context.model is not None or reading_context.layout is not None:
            cd_species = reading_context.xml_id_to_xml_element[
                cd_species_alias.get("species")
            ]
            key = get_key_from_species(
                cd_species, reading_context.xml_id_to_xml_element
            )
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            name = make_name(cd_species.get("name"))
            cd_species_homodimer = get_homodimer(cd_species)
            if cd_species_homodimer is not None:
                homomultimer = int(cd_species_homodimer)
            else:
                homomultimer = 1
            cd_species_hypothetical = get_hypothetical(cd_species)
            if cd_species_hypothetical is not None:
                hypothetical = cd_species_hypothetical.text == "true"
            else:
                hypothetical = False
            cd_species_activity = get_activity(cd_species_alias)
            if cd_species_activity is not None:
                active = cd_species_activity.text == "active"
                if active:
                    cd_species.attrib["id"] = f"{cd_species.get('id')}_active"
            if reading_context.model is not None:
                model_element = _reading_model.make_species(
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
                layout_element = _reading_layout.make_species(
                    reading_context,
                    cd_species_alias,
                    layout_element_cls,
                    name,
                    homomultimer,
                    hypothetical,
                    active,
                )
            else:
                layout_element = None
            auxiliary_map_elements = []
            covered_cd_residue_ids = set()
            for cd_species_modification in get_species_modifications(cd_species):
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
                if (
                    modification_model_element is not None
                    and modification_layout_element is not None
                ):
                    auxiliary_map_elements.append(
                        (modification_model_element, modification_layout_element)
                    )
            cd_species_template = get_template_from_species_alias(
                cd_species_alias, reading_context.xml_id_to_xml_element
            )
            for cd_modification_residue in get_modification_residues(
                cd_species_template
            ):
                residue_xml_id = cd_modification_residue.get("id")
                if residue_xml_id not in covered_cd_residue_ids:
                    (
                        empty_modification_model_element,
                        empty_modification_layout_element,
                    ) = cls._make_and_add_species_modification(
                        reading_context,
                        cd_species_modification={
                            "state": "empty",
                            "residue": residue_xml_id,
                        },
                        super_cd_element=cd_species_alias,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                    if (
                        empty_modification_model_element is not None
                        and empty_modification_layout_element is not None
                    ):
                        auxiliary_map_elements.append(
                            (
                                empty_modification_model_element,
                                empty_modification_layout_element,
                            )
                        )
            for cd_species_structural_state in get_species_structural_states(
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
                if (
                    structural_state_model_element is not None
                    and structural_state_layout_element is not None
                ):
                    auxiliary_map_elements.append(
                        (
                            structural_state_model_element,
                            structural_state_layout_element,
                        )
                    )
            cd_subunits = [
                reading_context.xml_id_to_xml_element[cd_subunit_id]
                for cd_subunit_id in reading_context.cd_complex_alias_id_to_cd_included_species_ids[
                    cd_species_alias.get("id")
                ]
            ]
            for cd_subunit in cd_subunits:
                cls._make_and_add_species(
                    reading_context,
                    cd_species_alias=cd_subunit,
                    super_cd_element=cd_species_alias,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                )
            if reading_context.model is not None:
                model_element = object_from_builder(model_element)
                if super_model_element is None:  # species case
                    model_element = register_model_element(
                        reading_context,
                        model_element,
                        reading_context.model.species,
                        cd_species.get("id"),
                    )
                    _reading_model.make_and_add_annotations(
                        reading_context,
                        cd_species,
                        model_element,
                        source_id=cd_species.get("id"),
                    )
                    _reading_model.make_and_add_notes(
                        reading_context,
                        cd_species,
                        model_element,
                        source_id=cd_species.get("id"),
                    )
                else:  # included species case
                    model_element = add_or_replace_element_in_set(
                        model_element,
                        super_model_element.subunits,
                        func=lambda new, old: new.id_ < old.id_,
                    )
                    _reading_model.make_and_add_annotations_from_notes(
                        reading_context,
                        get_notes(cd_species),
                        model_element,
                        source_id=cd_species.get("id"),
                    )
                    _reading_model.make_and_add_notes(
                        reading_context,
                        cd_species,
                        model_element,
                        source_id=cd_species.get("id"),
                    )
                reading_context.xml_id_to_model_element[cd_species.get("id")] = (
                    model_element
                )
                reading_context.xml_id_to_model_element[cd_species_alias.get("id")] = (
                    model_element
                )
            if reading_context.layout is not None:
                layout_element = object_from_builder(layout_element)
                if super_layout_element is None:  # species case
                    reading_context.layout.layout_elements.append(layout_element)
                else:  # included species case
                    super_layout_element.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[cd_species_alias.get("id")] = (
                    layout_element
                )
            if reading_context.model is not None and reading_context.layout is not None:
                for (
                    auxiliary_model_element,
                    auxiliary_layout_element,
                ) in auxiliary_map_elements:
                    reading_context.layout_model_mapping.add_mapping(
                        auxiliary_layout_element,
                        auxiliary_model_element,
                        replace=True,
                    )
                reading_context.layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
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
                modification_state = ModificationState[
                    cd_species_modification_state.upper()
                    .replace(" ", "_")  # for DON'T CARE
                    .replace("'", "_")
                ]
            cd_species_template = get_template_from_species_alias(
                super_cd_element,
                reading_context.xml_id_to_xml_element,
            )
            cd_modification_residue_id = f"{cd_species_template.get('id')}_{cd_species_modification.get('residue')}"
            cd_species_id = super_cd_element.get("species")
            cd_residue_id = cd_species_modification.get("residue")
            cd_species_modification_id = f"{cd_species_id}_{cd_residue_id}"
            if reading_context.model is not None:
                model_element = _reading_model.make_species_modification(
                    reading_context,
                    modification_state,
                    cd_modification_residue_id,
                )
                model_element.id_ = cd_species_modification_id
                model_element = object_from_builder(model_element)
                super_model_element.modifications.add(model_element)
            else:
                model_element = None
            if reading_context.layout is not None:
                cd_modification_residue = reading_context.xml_id_to_xml_element[
                    cd_modification_residue_id
                ]  # can also be of type ModificationSite for Genes, RNAs, etc.
                layout_element = _reading_layout.make_species_modification(
                    reading_context,
                    cd_modification_residue,
                    modification_state,
                    super_layout_element,
                )
                layout_element.id_ = f"{cd_species_modification_id}_layout"
                layout_element = object_from_builder(layout_element)
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
        cd_structural_state_value = cd_species_structural_state.get(
            "structuralState"
        ).replace(" ", "_")
        cd_structural_state_id = f"{cd_species_id}_{cd_structural_state_value}"
        if reading_context.model is not None:
            model_element = _reading_model.make_species_structural_state(
                reading_context, cd_species_structural_state
            )
            model_element.id_ = cd_structural_state_id
            model_element = object_from_builder(model_element)
            super_model_element.structural_states.add(model_element)
        else:
            model_element = None
        if reading_context.layout is not None:
            layout_element = _reading_layout.make_species_structural_state(
                reading_context, cd_species_structural_state, super_layout_element
            )
            layout_element.id_ = f"{cd_structural_state_id}_layout"
            layout_element = object_from_builder(layout_element)
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
            key = get_key_from_reaction(cd_reaction)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            cd_base_reactants = get_base_reactants(cd_reaction)
            cd_base_products = get_base_products(cd_reaction)
            if reading_context.model is not None:
                model_element = _reading_model.make_reaction(
                    reading_context, cd_reaction, model_element_cls
                )
            else:
                model_element = None
            if reading_context.layout is not None:
                (
                    layout_element,
                    make_base_reactant_layouts,
                    make_base_product_layouts,
                ) = _reading_layout.make_reaction(
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
                layout_element = object_from_builder(layout_element)
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
                if (
                    reading_context.model is not None
                    and reading_context.layout is not None
                ):
                    if reactant_layout_element is not None:
                        participant_map_elements.append(
                            (reactant_model_element, reactant_layout_element)
                        )
                    layout_elements_for_mapping.append(
                        reading_context.xml_id_to_layout_element[
                            cd_base_reactant.get("alias")
                        ]
                    )
            for cd_reactant_link in get_reactant_links(cd_reaction):
                reactant_model_element, reactant_layout_element = (
                    cls._make_and_add_reactant_from_link(
                        reading_context,
                        cd_reactant_link=cd_reactant_link,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if (
                    reading_context.model is not None
                    and reading_context.layout is not None
                ):
                    participant_map_elements.append(
                        (reactant_model_element, reactant_layout_element)
                    )
                    layout_elements_for_mapping.append(
                        reading_context.xml_id_to_layout_element[
                            cd_reactant_link.get("alias")
                        ]
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
                if (
                    reading_context.model is not None
                    and reading_context.layout is not None
                ):
                    if product_layout_element is not None:
                        participant_map_elements.append(
                            (product_model_element, product_layout_element)
                        )
                    layout_elements_for_mapping.append(
                        reading_context.xml_id_to_layout_element[
                            cd_base_product.get("alias")
                        ]
                    )
            for cd_product_link in get_product_links(cd_reaction):
                product_model_element, product_layout_element = (
                    cls._make_and_add_product_from_link(
                        reading_context,
                        cd_product_link=cd_product_link,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if (
                    reading_context.model is not None
                    and reading_context.layout is not None
                ):
                    participant_map_elements.append(
                        (product_model_element, product_layout_element)
                    )
                    layout_elements_for_mapping.append(
                        reading_context.xml_id_to_layout_element[
                            cd_product_link.get("alias")
                        ]
                    )
            for cd_reaction_modification in get_reaction_modifications(cd_reaction):
                modifier_model_element, modifier_layout_element = (
                    cls._make_and_add_modifier(
                        reading_context,
                        cd_reaction_modification=cd_reaction_modification,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                if (
                    reading_context.model is not None
                    and reading_context.layout is not None
                ):
                    participant_map_elements.append(
                        (modifier_model_element, modifier_layout_element)
                    )
                    layout_elements_for_mapping.append(modifier_layout_element.source)
            if reading_context.model is not None:
                model_element = object_from_builder(model_element)
                model_element = register_model_element(
                    reading_context,
                    model_element,
                    reading_context.model.reactions,
                    cd_reaction.get("id"),
                )
                _reading_model.make_and_add_annotations(
                    reading_context,
                    cd_reaction,
                    model_element,
                    source_id=cd_reaction.get("id"),
                )
                _reading_model.make_and_add_notes(
                    reading_context,
                    cd_reaction,
                    model_element,
                    source_id=cd_reaction.get("id"),
                )
            if reading_context.layout is not None:
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[layout_element.id_] = (
                    layout_element
                )
                layout_elements_for_mapping.append(layout_element)
            if reading_context.model is not None and reading_context.layout is not None:
                expanded = set()
                for layout_element_for_mapping in layout_elements_for_mapping:
                    existing_key = (
                        reading_context.layout_model_mapping._singleton_to_key.get(
                            layout_element_for_mapping
                        )
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
                        participant_model_element,
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
        cd_reactant_id = _get_reactant_id(cd_base_reactant, super_cd_element)
        if reading_context.model is not None:
            model_element = _reading_model.make_reactant_from_base(
                reading_context,
                cd_base_reactant,
                super_cd_element,
            )
            model_element = object_from_builder(model_element)
            model_element = add_or_replace_element_in_set(
                model_element,
                super_model_element.reactants,
                func=lambda new, old: new.id_ < old.id_,
            )
            reading_context.xml_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if reading_context.layout is not None and make_layout:
            layout_element = _reading_layout.make_reactant_from_base(
                reading_context,
                cd_base_reactant,
                n_cd_base_reactant,
                super_cd_element,
                super_layout_element,
            )
            layout_element.id_ = f"{cd_reactant_id}_layout"
            layout_element = object_from_builder(layout_element)
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
        cd_reactant_id = _get_reactant_id(cd_reactant_link, super_cd_element)
        if reading_context.model is not None:
            model_element = _reading_model.make_reactant_from_link(
                reading_context,
                cd_reactant_link,
                super_cd_element,
            )
            model_element = object_from_builder(model_element)
            model_element = add_or_replace_element_in_set(
                model_element,
                super_model_element.reactants,
                func=lambda new, old: new.id_ < old.id_,
            )
            reading_context.xml_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if reading_context.layout is not None:
            layout_element = _reading_layout.make_reactant_from_link(
                reading_context,
                cd_reactant_link,
                super_layout_element,
            )
            layout_element.id_ = f"{cd_reactant_id}_layout"
            layout_element = object_from_builder(layout_element)
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
        cd_product_id = _get_product_id(cd_base_product, super_cd_element)
        if reading_context.model is not None:
            model_element = _reading_model.make_product_from_base(
                reading_context,
                cd_base_product,
                super_cd_element,
            )
            model_element = object_from_builder(model_element)
            model_element = add_or_replace_element_in_set(
                model_element,
                super_model_element.products,
                func=lambda new, old: new.id_ < old.id_,
            )
            reading_context.xml_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if reading_context.layout is not None and make_layout:
            layout_element = _reading_layout.make_product_from_base(
                reading_context,
                cd_base_product,
                n_cd_base_product,
                super_cd_element,
                super_layout_element,
            )
            layout_element.id_ = f"{cd_product_id}_layout"
            layout_element = object_from_builder(layout_element)
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
        cd_product_id = _get_product_id(cd_product_link, super_cd_element)
        if reading_context.model is not None:
            model_element = _reading_model.make_product_from_link(
                reading_context,
                cd_product_link,
                super_cd_element,
            )
            model_element = object_from_builder(model_element)
            model_element = add_or_replace_element_in_set(
                model_element,
                super_model_element.products,
                func=lambda new, old: new.id_ < old.id_,
            )
            reading_context.xml_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if reading_context.layout is not None:
            layout_element = _reading_layout.make_product_from_link(
                reading_context,
                cd_product_link,
                super_layout_element,
            )
            layout_element.id_ = f"{cd_product_id}_layout"
            layout_element = object_from_builder(layout_element)
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
            key = get_key_from_reaction_modification(cd_reaction_modification)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            has_boolean_input = has_boolean_input_from_modification(
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
            modifier_metaid = _get_modifier_metaid(
                cd_reaction_modification, super_cd_element
            )
            if reading_context.model is not None:
                if not has_boolean_input:
                    source_model_element = reading_context.xml_id_to_model_element[
                        cd_reaction_modification.get("aliases")
                    ]
                model_element = _reading_model.make_modifier(
                    reading_context,
                    model_element_cls,
                    source_model_element,
                    metaid=modifier_metaid,
                )
                model_element = object_from_builder(model_element)
                model_element = add_or_replace_element_in_set(
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
                layout_element = _reading_layout.make_modifier(
                    reading_context,
                    cd_reaction_modification,
                    layout_element_cls,
                    source_layout_element,
                    super_layout_element,
                    has_boolean_input,
                )
                layout_element.id_ = f"{modifier_metaid}_layout"
                layout_element = object_from_builder(layout_element)
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
            key = get_key_from_gate_member(cd_reaction_modification_or_cd_gate_member)
            cd_modifiers = cd_reaction_modification_or_cd_gate_member.get("aliases")
            cd_input_ids = cd_modifiers.split(",")
            sorted_aliases = "_".join(sorted(cd_input_ids))
            cd_gate_id = f"{cd_reaction_id}_gate_{sorted_aliases}"
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if reading_context.model is not None:
                model_element = _reading_model.make_logic_gate(
                    reading_context,
                    model_element_cls,
                )
                model_element.id_ = cd_gate_id
            else:
                model_element = None
            if reading_context.layout is not None:
                layout_element = _reading_layout.make_logic_gate(
                    reading_context,
                    cd_reaction_modification_or_cd_gate_member,
                    layout_element_cls,
                )
                layout_element.id_ = f"{cd_gate_id}_layout"
                layout_element = object_from_builder(layout_element)
                reading_context.layout.layout_elements.append(layout_element)
            else:
                layout_element = None
            for cd_input_id in cd_input_ids:
                input_model_element = None
                logic_arc = None
                if reading_context.model is not None:
                    source_model_element = reading_context.xml_id_to_model_element[
                        cd_input_id
                    ]
                    input_model_element = _reading_model.make_logic_gate_input(
                        reading_context, source_model_element
                    )
                    input_model_element.id_ = f"{cd_gate_id}_input_{cd_input_id}"
                    input_model_element = object_from_builder(input_model_element)
                    model_element.inputs.add(input_model_element)
                if reading_context.layout is not None:
                    input_layout_element = reading_context.xml_id_to_layout_element[
                        cd_input_id
                    ]
                    logic_arc = _reading_layout.make_logic_arc(
                        reading_context,
                        layout_element,
                        input_layout_element,
                    )
                    logic_arc.id_ = f"{cd_gate_id}_arc_{cd_input_id}"
                    logic_arc = object_from_builder(logic_arc)
                    reading_context.layout.layout_elements.append(logic_arc)
                if input_model_element is not None and logic_arc is not None:
                    reading_context.layout_model_mapping.add_mapping(
                        logic_arc,
                        input_model_element,
                        replace=True,
                    )
            if model_element is not None:
                model_element = object_from_builder(model_element)
                model_element = register_model_element(
                    reading_context,
                    model_element,
                    reading_context.model.boolean_logic_gates,
                    cd_gate_id,
                )
            if model_element is not None and layout_element is not None:
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
            key = get_key_from_reaction(cd_reaction)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            has_boolean_input = has_boolean_input_from_reaction(cd_reaction)
            cd_base_reactant = get_base_reactants(cd_reaction)[0]
            cd_base_product = get_base_products(cd_reaction)[0]
            if has_boolean_input:
                cd_gate_members = get_gate_members(cd_reaction)
                cd_gate_member = cd_gate_members[0]
                source_model_element, source_layout_element = (
                    cls._make_and_add_logic_gate(
                        reading_context,
                        cd_reaction_modification_or_cd_gate_member=cd_gate_member,
                        cd_reaction_id=cd_reaction.get("id"),
                    )
                )
            if reading_context.model is not None:
                if not has_boolean_input:
                    source_model_element = reading_context.xml_id_to_model_element[
                        cd_base_reactant.get("alias")
                    ]
                target_model_element = reading_context.xml_id_to_model_element[
                    cd_base_product.get("alias")
                ]
                model_element = _reading_model.make_modulation(
                    reading_context,
                    cd_reaction,
                    model_element_cls,
                    source_model_element,
                    target_model_element,
                )
                model_element = object_from_builder(model_element)
                model_element = register_model_element(
                    reading_context,
                    model_element,
                    reading_context.model.modulations,
                    cd_reaction.get("id"),
                )
                _reading_model.make_and_add_annotations(
                    reading_context,
                    cd_reaction,
                    model_element,
                    source_id=cd_reaction.get("id"),
                )
                _reading_model.make_and_add_notes(
                    reading_context,
                    cd_reaction,
                    model_element,
                    source_id=cd_reaction.get("id"),
                )
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
                layout_element = _reading_layout.make_modulation(
                    reading_context,
                    cd_reaction,
                    layout_element_cls,
                    source_layout_element,
                    target_layout_element,
                    has_boolean_input,
                    cd_base_reactant,
                    cd_base_product,
                )
                layout_element = object_from_builder(layout_element)
                reading_context.layout.layout_elements.append(layout_element)
                reading_context.xml_id_to_layout_element[layout_element.id_] = (
                    layout_element
                )
            else:
                layout_element = None
            if reading_context.model is not None and reading_context.layout is not None:
                source_mapping_key = (
                    reading_context.layout_model_mapping._singleton_to_key.get(
                        source_layout_element
                    )
                )
                if source_mapping_key is not None:
                    source_layout_elements = source_mapping_key
                else:
                    source_layout_elements = frozenset([source_layout_element])
                target_mapping_key = (
                    reading_context.layout_model_mapping._singleton_to_key.get(
                        target_layout_element
                    )
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
