import dataclasses

import math

import momapy.core
import momapy.builder
import momapy.shapes
import momapy.arcs
import momapy.coloring

import momapy.celldesigner.core
import momapy.celldesigner.parser

import momapy.sbgn.pd

import xsdata.formats.dataclass.context
import xsdata.formats.dataclass.parsers
import xsdata.formats.dataclass.parsers.config

_CellDesignerSpeciesReferenceTypeMapping = {
    (
        momapy.celldesigner.parser.ProteinType.GENERIC
    ): momapy.celldesigner.core.GenericProteinReference,
    (
        momapy.celldesigner.parser.ProteinType.RECEPTOR
    ): momapy.celldesigner.core.ReceptorReference,
    (
        momapy.celldesigner.parser.ProteinType.ION_CHANNEL
    ): momapy.celldesigner.core.IonChannelReference,
    (
        momapy.celldesigner.parser.ProteinType.TRUNCATED
    ): momapy.celldesigner.core.TruncatedProteinReference,
    (
        momapy.celldesigner.parser.AntisenseRnaType.ANTISENSE_RNA
    ): momapy.celldesigner.core.AntisensRNAReference,
    (
        momapy.celldesigner.parser.RnaType.RNA
    ): momapy.celldesigner.core.RNAReference,
    (
        momapy.celldesigner.parser.GeneType.GENE
    ): momapy.celldesigner.core.GeneReference,
}

_CellDesignerReactionTypeMapping = {
    (
        momapy.celldesigner.parser.ReactionTypeValue.STATE_TRANSITION
    ): momapy.celldesigner.core.StateTransition,
    (
        momapy.celldesigner.parser.ReactionTypeValue.KNOWN_TRANSITION_OMITTED
    ): momapy.celldesigner.core.KnownTransitionOmitted,
    (
        momapy.celldesigner.parser.ReactionTypeValue.UNKNOWN_TRANSITION
    ): momapy.celldesigner.core.UnknownTransition,
    (
        momapy.celldesigner.parser.ReactionTypeValue.TRANSCRIPTION
    ): momapy.celldesigner.core.Transcription,
    (
        momapy.celldesigner.parser.ReactionTypeValue.TRANSLATION
    ): momapy.celldesigner.core.Translation,
    (
        momapy.celldesigner.parser.ReactionTypeValue.TRANSPORT
    ): momapy.celldesigner.core.Transport,
    (
        momapy.celldesigner.parser.ReactionTypeValue.HETERODIMER_ASSOCIATION
    ): momapy.celldesigner.core.HeterodimerAssociation,
    (
        momapy.celldesigner.parser.ReactionTypeValue.DISSOCIATION
    ): momapy.celldesigner.core.Dissociation,
    (
        momapy.celldesigner.parser.ReactionTypeValue.TRUNCATION
    ): momapy.celldesigner.core.Truncation,
    (
        momapy.celldesigner.parser.ReactionTypeValue.MODULATION
    ): momapy.celldesigner.core.ModulationReaction,
    (
        momapy.celldesigner.parser.ReactionTypeValue.CATALYSIS
    ): momapy.celldesigner.core.CatalysisReaction,
    (
        momapy.celldesigner.parser.ReactionTypeValue.UNKNOWN_CATALYSIS
    ): momapy.celldesigner.core.UnknownCatalysisReaction,
    (
        momapy.celldesigner.parser.ReactionTypeValue.INHIBITION
    ): momapy.celldesigner.core.InhibitionReaction,
    (
        momapy.celldesigner.parser.ReactionTypeValue.UNKNOWN_INHIBITION
    ): momapy.celldesigner.core.UnknownInhibitionReaction,
    (
        momapy.celldesigner.parser.ReactionTypeValue.PHYSICAL_STIMULATION
    ): momapy.celldesigner.core.PhysicalStimulationReaction,
    (
        momapy.celldesigner.parser.ReactionTypeValue.TRIGGER
    ): momapy.celldesigner.core.TriggeringReaction,
    (
        momapy.celldesigner.parser.ReactionTypeValue.BOOLEAN_LOGIC_GATE
    ): momapy.celldesigner.core.BooleanLogicGateReaction,
}

_CellDesignerModifierTypeMapping = {
    (
        momapy.celldesigner.parser.ModificationType.MODULATION
    ): momapy.celldesigner.core.Modulator,
    (
        momapy.celldesigner.parser.ModificationType.CATALYSIS
    ): momapy.celldesigner.core.Catalyzer,
    (
        momapy.celldesigner.parser.ModificationType.UNKNOWN_CATALYSIS
    ): momapy.celldesigner.core.UnknownCatalyzer,
    (
        momapy.celldesigner.parser.ModificationType.INHIBITION
    ): momapy.celldesigner.core.Inhibitor,
    (
        momapy.celldesigner.parser.ModificationType.UNKNOWN_INHIBITION
    ): momapy.celldesigner.core.UnknownInhibitor,
    (
        momapy.celldesigner.parser.ModificationType.PHYSICAL_STIMULATION
    ): momapy.celldesigner.core.PhysicalStimulator,
    (
        momapy.celldesigner.parser.ModificationType.TRIGGER
    ): momapy.celldesigner.core.Trigger,
}

_CellDesignerModificationReactionTypeMapping = {
    (
        momapy.celldesigner.parser.ReactionTypeValue.MODULATION
    ): momapy.celldesigner.core.Modulation,
    (
        momapy.celldesigner.parser.ReactionTypeValue.CATALYSIS
    ): momapy.celldesigner.core.Catalysis,
    (
        momapy.celldesigner.parser.ReactionTypeValue.UNKNOWN_CATALYSIS
    ): momapy.celldesigner.core.UnknownCatalysis,
    (
        momapy.celldesigner.parser.ReactionTypeValue.INHIBITION
    ): momapy.celldesigner.core.Inhibition,
    (
        momapy.celldesigner.parser.ReactionTypeValue.UNKNOWN_INHIBITION
    ): momapy.celldesigner.core.UnknownInhibition,
    (
        momapy.celldesigner.parser.ReactionTypeValue.PHYSICAL_STIMULATION
    ): momapy.celldesigner.core.PhysicalStimulation,
    (
        momapy.celldesigner.parser.ReactionTypeValue.TRIGGER
    ): momapy.celldesigner.core.Triggering,
}

_CellDesignerBooleanLogicGateTypeMapping = {
    (
        momapy.celldesigner.parser.ModificationType.BOOLEAN_LOGIC_GATE_AND
    ): momapy.celldesigner.core.AndGate,
    (
        momapy.celldesigner.parser.ModificationType.BOOLEAN_LOGIC_GATE_OR
    ): momapy.celldesigner.core.OrGate,
    (
        momapy.celldesigner.parser.ModificationType.BOOLEAN_LOGIC_GATE_NOT
    ): momapy.celldesigner.core.NotGate,
    (
        momapy.celldesigner.parser.ModificationType.BOOLEAN_LOGIC_GATE_UNKNOWN
    ): momapy.celldesigner.core.UnknownGate,
}

_CellDesignerSpeciesTypeMapping = {
    (
        momapy.celldesigner.parser.ClassValue.PROTEIN,
        momapy.celldesigner.core.GenericProteinReference,
    ): momapy.celldesigner.core.GenericProtein,
    (
        momapy.celldesigner.parser.ClassValue.PROTEIN,
        momapy.celldesigner.core.ReceptorReference,
    ): momapy.celldesigner.core.Receptor,
    (
        momapy.celldesigner.parser.ClassValue.PROTEIN,
        momapy.celldesigner.core.IonChannelReference,
    ): momapy.celldesigner.core.IonChannel,
    (
        momapy.celldesigner.parser.ClassValue.PROTEIN,
        momapy.celldesigner.core.TruncatedProteinReference,
    ): momapy.celldesigner.core.TruncatedProtein,
    (
        momapy.celldesigner.parser.ClassValue.GENE,
        momapy.celldesigner.core.GeneReference,
    ): momapy.celldesigner.core.Gene,
    (
        momapy.celldesigner.parser.ClassValue.RNA,
        momapy.celldesigner.core.RNAReference,
    ): momapy.celldesigner.core.RNA,
    (
        momapy.celldesigner.parser.ClassValue.ANTISENSE_RNA,
        momapy.celldesigner.core.AntisensRNAReference,
    ): momapy.celldesigner.core.AntisensRNA,
    (
        momapy.celldesigner.parser.ClassValue.PHENOTYPE,
        None,
    ): momapy.celldesigner.core.Phenotype,
    (
        momapy.celldesigner.parser.ClassValue.ION,
        None,
    ): momapy.celldesigner.core.Ion,
    (
        momapy.celldesigner.parser.ClassValue.SIMPLE_MOLECULE,
        None,
    ): momapy.celldesigner.core.SimpleMolecule,
    (
        momapy.celldesigner.parser.ClassValue.COMPLEX,
        None,
    ): momapy.celldesigner.core.Complex,
    (
        momapy.celldesigner.parser.ClassValue.UNKNOWN,
        None,
    ): momapy.celldesigner.core.Unknown,
    (
        momapy.celldesigner.parser.ClassValue.DRUG,
        None,
    ): momapy.celldesigner.core.Drug,
    (
        momapy.celldesigner.parser.ClassValue.DEGRADED,
        None,
    ): momapy.celldesigner.core.Degraded,
}


_CellDesignerSpeciesLayoutTypeMapping = {
    momapy.celldesigner.core.GenericProtein: momapy.celldesigner.core.GenericProteinLayout,
    momapy.celldesigner.core.Receptor: momapy.celldesigner.core.ReceptorLayout,
    momapy.celldesigner.core.IonChannel: momapy.celldesigner.core.IonChannelLayout,
    momapy.celldesigner.core.TruncatedProtein: momapy.celldesigner.core.TruncatedProteinLayout,
    momapy.celldesigner.core.Gene: momapy.celldesigner.core.GeneLayout,
    momapy.celldesigner.core.RNA: momapy.celldesigner.core.RNALayout,
    momapy.celldesigner.core.AntisensRNA: momapy.celldesigner.core.AntisensRNALayout,
    momapy.celldesigner.core.Phenotype: momapy.celldesigner.core.PhenotypeLayout,
    momapy.celldesigner.core.Ion: momapy.celldesigner.core.IonLayout,
    momapy.celldesigner.core.SimpleMolecule: momapy.celldesigner.core.SimpleMoleculeLayout,
    momapy.celldesigner.core.Complex: momapy.celldesigner.core.ComplexLayout,
    momapy.celldesigner.core.Drug: momapy.celldesigner.core.DrugLayout,
    momapy.celldesigner.core.Unknown: momapy.celldesigner.core.UnknownLayout,
    momapy.celldesigner.core.Degraded: momapy.celldesigner.core.DegradedLayout,
}


_CellDesignerStructuralStateMapping = {
    "open": momapy.celldesigner.core.StructuralStateValue.OPEN,
    "closed": momapy.celldesigner.core.StructuralStateValue.CLOSED,
    "empty": momapy.celldesigner.core.StructuralStateValue.EMPTY,
}

_CellDesignerCompartmentLayoutTypeMapping = {
    momapy.celldesigner.parser.ClassValue.SQUARE: momapy.celldesigner.core.SquareCompartmentLayout,
    momapy.celldesigner.parser.ClassValue.OVAL: momapy.celldesigner.core.OvalCompartmentLayout,
}

_CellDesignerReactionLayoutTypeMapping = {
    (
        momapy.celldesigner.parser.ReactionTypeValue.STATE_TRANSITION
    ): momapy.celldesigner.core.StateTransitionLayout,
    (
        momapy.celldesigner.parser.ReactionTypeValue.TRANSCRIPTION
    ): momapy.celldesigner.core.TranscriptionLayout,
    (
        momapy.celldesigner.parser.ReactionTypeValue.TRANSLATION
    ): momapy.celldesigner.core.StateTransitionLayout,
    # (
    #     momapy.celldesigner.parser.ReactionTypeValue.HETERODIMER_ASSOCIATION
    # ): momapy.celldesigner.core.StateTransitionLayout,
}


_CellDesignerPositionAnchorMapping = {
    momapy.celldesigner.parser.LinkAnchorPosition.NW: "north_west",
    momapy.celldesigner.parser.LinkAnchorPosition.NNW: "north_west",
    momapy.celldesigner.parser.LinkAnchorPosition.N: "north",
    momapy.celldesigner.parser.LinkAnchorPosition.NNE: "north_east",
    momapy.celldesigner.parser.LinkAnchorPosition.NE: "north_east",
    momapy.celldesigner.parser.LinkAnchorPosition.ENE: "north_east",
    momapy.celldesigner.parser.LinkAnchorPosition.E: "east",
    momapy.celldesigner.parser.LinkAnchorPosition.ESE: "south_east",
    momapy.celldesigner.parser.LinkAnchorPosition.SE: "south_east",
    momapy.celldesigner.parser.LinkAnchorPosition.SSE: "south_east",
    momapy.celldesigner.parser.LinkAnchorPosition.S: "south",
    momapy.celldesigner.parser.LinkAnchorPosition.SSW: "south_west",
    momapy.celldesigner.parser.LinkAnchorPosition.SW: "south_west",
    momapy.celldesigner.parser.LinkAnchorPosition.WSW: "south_west",
    momapy.celldesigner.parser.LinkAnchorPosition.W: "west",
    momapy.celldesigner.parser.LinkAnchorPosition.WNW: "north_west",
}


def read_file(filename):
    config = xsdata.formats.dataclass.parsers.config.ParserConfig(
        fail_on_unknown_properties=False
    )
    parser = xsdata.formats.dataclass.parsers.XmlParser(
        config=config, context=xsdata.formats.dataclass.context.XmlContext()
    )
    print("PARSING FILE...")
    sbml = parser.parse(filename, momapy.celldesigner.parser.Sbml)
    d_id_me_mapping = {}
    d_id_le_mapping = {}
    builder = momapy.celldesigner.core.CellDesignerMapBuilder()
    builder.model = builder.new_model()
    builder.layout = builder.new_layout()
    builder.layout_model_mapping = builder.new_layout_model_mapping()
    print("BUILDING MODEL...")
    for compartment in sbml.model.list_of_compartments.compartment:
        compartment_me = _compartment_to_model_element(
            compartment, builder, d_id_me_mapping
        )
        builder.model.add_element(compartment_me)
        d_id_me_mapping[compartment_me.id] = compartment_me
    # Angles of modifications of species are stored in the modification residue,
    # not in the each species alias. Hence we use a dictionary to store them and
    # use them when we make the layouts for the modifications
    d_modification_residue_me_id_angle_mapping = {}
    for species_reference in (
        sbml.model.annotation.extension.list_of_antisense_rnas.antisense_rna
        + sbml.model.annotation.extension.list_of_rnas.rna
        + sbml.model.annotation.extension.list_of_genes.gene
        + sbml.model.annotation.extension.list_of_proteins.protein
    ):
        species_reference_me = _species_reference_to_model_element(
            species_reference,
            builder,
            d_id_me_mapping,
            d_modification_residue_me_id_angle_mapping,
        )
        builder.add_model_element(species_reference_me)
        d_id_me_mapping[species_reference_me.id] = species_reference_me
    for species in sbml.model.list_of_species.species:
        species_me = _species_to_model_element(
            species, builder, d_id_me_mapping
        )
        builder.add_model_element(species_me)
        d_id_me_mapping[species_me.id] = species_me
    for reaction in sbml.model.list_of_reactions.reaction:
        annotation = reaction.annotation
        extension = annotation.extension
        reaction_type = extension.reaction_type
        # Modulations between species or between Boolean logical gates and
        # species are stored as reactions in CellDesigner. We store all
        # reactions in the sbml_reactions attribute. True reactions are
        # additionally stored in the reactions attribute. Reactions that are
        # modulations are additionally stored in the modulations attribute, as
        # modulations (and not as reactions).
        reaction_me = _reaction_to_model_element(
            reaction, builder, d_id_me_mapping
        )
        builder.add_model_element(reaction_me)
        d_id_me_mapping[reaction_me.id] = reaction_me
    if sbml.model.annotation.extension.list_of_included_species is not None:
        for (
            included_species
        ) in sbml.model.annotation.extension.list_of_included_species.species:
            included_species_me = _species_to_model_element(
                included_species,
                builder,
                d_id_me_mapping,
                included_species=True,
            )
            complex_me_id = included_species.annotation.complex_species
            complex_me = d_id_me_mapping[complex_me_id]
            complex_me.add_element(included_species_me)
            d_id_me_mapping[included_species_me.id] = included_species_me
    print("BUILDING LAYOUT...")
    # Layouts: we build a layout element for each CellDesigner alias
    for (
        compartment_alias
    ) in (
        sbml.model.annotation.extension.list_of_compartment_aliases.compartment_alias
    ):
        compartment_le = _compartment_alias_to_layout_element(
            compartment_alias,
            builder,
            d_id_le_mapping,
            d_id_me_mapping,
        )
        builder.add_layout_element(compartment_le)
        d_id_le_mapping[compartment_le.id] = compartment_le
        compartment_me = d_id_me_mapping[compartment_alias.compartment]
        builder.map_model_element_to_layout_element(
            compartment_le, compartment_me
        )
    for (
        complex_species_alias
    ) in (
        sbml.model.annotation.extension.list_of_complex_species_aliases.complex_species_alias
    ):
        complex_species_le = _species_alias_to_layout_element(
            complex_species_alias,
            builder,
            d_id_le_mapping,
            d_id_me_mapping,
            d_modification_residue_me_id_angle_mapping,
        )
        builder.add_layout_element(complex_species_le)
        d_id_le_mapping[complex_species_le.id] = complex_species_le
        complex_species_me = d_id_me_mapping[complex_species_alias.species]
        builder.map_model_element_to_layout_element(
            complex_species_le, complex_species_me
        )
    # Species aliases also include aliases for included species.
    # If the species is included in a complex, it has a complex species alias
    # that is not None.
    for (
        species_alias
    ) in sbml.model.annotation.extension.list_of_species_aliases.species_alias:
        species_le = _species_alias_to_layout_element(
            species_alias,
            builder,
            d_id_le_mapping,
            d_id_me_mapping,
            d_modification_residue_me_id_angle_mapping,
        )
        d_id_le_mapping[species_le.id] = species_le
        species_me = d_id_me_mapping[species_alias.species]
        if species_alias.complex_species_alias is not None:
            complex_le_id = species_alias.complex_species_alias
            complex_le = d_id_le_mapping[complex_le_id]
            complex_le.add_element(species_le)
            complex_me = builder.layout_model_mapping[complex_le][0]
            nm_model_element = complex_me
        else:
            builder.add_layout_element(species_le)
            nm_model_element = None
        builder.map_model_element_to_layout_element(
            species_le, species_me, nm_model_element
        )
    for reaction in sbml.model.list_of_reactions.reaction:
        annotation = reaction.annotation
        extension = annotation.extension
        reaction_le = _reaction_to_layout_element(
            reaction, builder, d_id_le_mapping, d_id_me_mapping
        )
        if reaction_le is not None:
            builder.layout.add_element(reaction_le)
    print("FITTING LAYOUT TO CONTENT...")
    momapy.positioning.set_fit(builder.layout, builder.layout.layout_elements)
    builder.layout.fill = momapy.coloring.white
    return builder


def _compartment_to_model_element(compartment, builder, d_id_me_mapping):
    id_ = compartment.id
    name = compartment.name
    metaid = compartment.metaid
    compartment_me = builder.new_model_element(
        momapy.celldesigner.core.Compartment
    )
    compartment_me.id = id_
    compartment_me.name = name
    compartment_me.metaid = metaid
    return compartment_me


def _species_reference_to_model_element(
    species_reference,
    builder,
    d_id_me_mapping,
    d_modification_residue_me_id_angle_mapping,
):
    id_ = species_reference.id
    name = species_reference.name
    type_ = species_reference.type
    species_reference_me_cls = _CellDesignerSpeciesReferenceTypeMapping[type_]
    species_reference_me = builder.new_model_element(species_reference_me_cls)
    species_reference_me.id = id_
    species_reference_me.name = name
    if hasattr(species_reference, "list_of_modification_residues"):
        list_of_modification_residues = (
            species_reference.list_of_modification_residues
        )
        if list_of_modification_residues is not None:
            for (
                modification_residue
            ) in list_of_modification_residues.modification_residue:
                modification_residue_me = (
                    _modification_residue_to_model_element(
                        modification_residue,
                        builder,
                        species_reference_me,
                        d_id_me_mapping,
                    )
                )
                species_reference_me.add_element(modification_residue_me)
                d_id_me_mapping[
                    modification_residue_me.id
                ] = modification_residue_me
                d_modification_residue_me_id_angle_mapping[
                    modification_residue_me.id
                ] = modification_residue.angle
    return species_reference_me


def _modification_residue_to_model_element(
    modification_residue,
    builder,
    species_reference_me,
    d_id_me_mapping,
):
    id_ = modification_residue.id
    name = modification_residue.name
    modification_residue_me = builder.new_model_element(
        momapy.celldesigner.core.ModificationResidue
    )
    # Defaults ids for modification residues are simple in CellDesigner (e.g.,
    # "rs1") and might be shared between residues of different species.
    # However we want a unique id, so we build it using the id of the
    # species as well.
    modification_residue_me.id = f"{species_reference_me.id}_{id_}"
    modification_residue_me.name = name
    return modification_residue_me


def _modification_to_model_element(
    modification, builder, species_me, d_id_me_mapping
):
    residue_id = f"{species_me.reference.id}_{modification.residue}"
    residue = d_id_me_mapping[residue_id]
    state = modification.state
    modification_me = builder.new_model_element(
        momapy.celldesigner.core.Modification
    )
    modification_me.residue = residue
    modification_me.state = momapy.celldesigner.core.ModificationState[
        state.name
    ]
    return modification_me


def _structural_state_to_model_element(
    structural_state,
    builder,
    species_me,
    d_id_me_mapping,
):
    structural_state_value = _CellDesignerStructuralStateMapping.get(
        structural_state.structural_state
    )
    if structural_state_value is None:
        structural_state_value = structural_state.structural_state
    structural_state_me = builder.new_model_element(
        momapy.celldesigner.core.StructuralState
    )
    structural_state_me.value = structural_state_value
    return structural_state_me


def _species_to_model_element(
    species, builder, d_id_me_mapping, included_species=False
):
    id_ = species.id
    name = species.name
    compartment_id = species.compartment
    # Included species are subunits of complexes. They are treated as normal
    # species in CellDesigner, but the structure of the XML is not exactly
    # the same as for normal species.
    if included_species is False:
        annotation = species.annotation
        extension = annotation.extension
        identity = extension.species_identity
    else:
        annotation = species.annotation
        identity = annotation.species_identity
    state = identity.state
    type_ = identity.class_value
    has_reference = False
    for species_reference_type in [
        "protein_reference",
        "rna_reference",
        "gene_reference",
        "antisenserna_reference",
    ]:
        if getattr(identity, species_reference_type) is not None:
            has_reference = True
            break
    # The type of the species is given by its class value, but also by the type
    # of its species reference, if it has one. We use the species reference
    # model elements rather than the parsed objects since the former are readily
    # accessible from the d_id_me_mapping dictionary.
    if has_reference:
        species_reference = d_id_me_mapping[
            getattr(identity, species_reference_type)
        ]
        type_ = (
            type_,
            type(species_reference)._cls_to_build,
        )
    else:
        type_ = (
            type_,
            None,
        )
    species_me_cls = _CellDesignerSpeciesTypeMapping[type_]
    species_me = builder.new_model_element(species_me_cls)
    species_me.id = id_
    species_me.name = name
    if compartment_id is not None:
        species_me.compartment = d_id_me_mapping[compartment_id]
    if has_reference:
        species_me.reference = species_reference
    if state is not None:
        homodimer = state.homodimer
        if homodimer is not None:
            species_me.homodimer = homodimer
        list_of_modifications = state.list_of_modifications
        if list_of_modifications is not None:
            for modification in list_of_modifications.modification:
                modification_me = _modification_to_model_element(
                    modification, builder, species_me, d_id_me_mapping
                )
                species_me.add_element(modification_me)
                d_id_me_mapping[modification_me.id] = modification_me
        list_of_structural_states = state.list_of_structural_states
        if list_of_structural_states is not None:
            structural_state = list_of_structural_states.structural_state
            structural_state_me = _structural_state_to_model_element(
                structural_state,
                builder,
                species_me,
                d_id_me_mapping,
            )
            species_me.add_element(structural_state_me)
            d_id_me_mapping[structural_state_me.id] = structural_state_me
    return species_me


def _reaction_to_model_element(reaction, builder, d_id_me_mapping):
    annotation = reaction.annotation
    extension = annotation.extension
    reaction_type = extension.reaction_type
    reaction_cls = _CellDesignerReactionTypeMapping[reaction_type]
    reaction_me = builder.new_model_element(reaction_cls)
    reaction_me.id = reaction.id
    reaction_me.metaid = reaction.metaid
    reaction_me.name = reaction.name
    reaction_me.reversible = reaction.reversible
    list_of_reactants = reaction.list_of_reactants
    if list_of_reactants is not None:
        for reactant in list_of_reactants.species_reference:
            reactant_me = _reactant_to_model_element(
                reactant, builder, reaction_me, d_id_me_mapping
            )
            reaction_me.add_element(reactant_me)
            d_id_me_mapping[reactant_me.id] = reactant_me
    list_of_products = reaction.list_of_products
    if list_of_products is not None:
        for product in list_of_products.species_reference:
            product_me = _product_to_model_element(
                product, builder, reaction_me, d_id_me_mapping
            )
            reaction_me.add_element(product_me)
            d_id_me_mapping[product_me.id] = product_me

    gates_me = set([])
    d_modifier_species_id_cls_mapping = {}
    in_group_modifier_species_ids = set([])
    # list of modification contains Boolean logical gates and the type of
    # each modifier (e.g. inhibitor). It does not contain the type of the
    # modifiers whose species are gates. It contains however, in addition to
    # the gates, the type of each modifier that is an input of a gate,
    # individually.
    list_of_modification = extension.list_of_modification
    if list_of_modification is not None:
        for modification in list_of_modification.modification:
            modifier_type = modification.type
            # We build Boolean logical gates
            gate_cls = _CellDesignerBooleanLogicGateTypeMapping.get(
                modifier_type
            )
            if gate_cls is not None:
                gate_me = _boolean_logic_gate_to_model_element(
                    modification,
                    builder,
                    reaction_me,
                    d_id_me_mapping,
                )
                builder.model.add_element(gate_me)
                gates_me.add(gate_me)
                # We remember all species that are inputs of Boolean logical
                # gates since they also appear individually in
                # the list of modifications and the list of modifiers
                for input_ in gate_me.inputs:
                    in_group_modifier_species_ids.add(input_.id)
            modifier_cls = _CellDesignerModifierTypeMapping.get(modifier_type)
            if modifier_cls is not None:
                d_modifier_species_id_cls_mapping[
                    modification.modifiers
                ] = modifier_cls
    list_of_modifiers = reaction.list_of_modifiers
    modifiers_me = set([])
    d_modifier_species_id_me_mapping = {}
    # The list of modifiers does not contain the gates, but one modifier
    # for each input of each gate.
    if list_of_modifiers is not None:
        for modifier in list_of_modifiers.modifier_species_reference:
            modifier_me = _modifier_to_model_element(
                modifier,
                builder,
                reaction_me,
                d_modifier_species_id_cls_mapping,
                d_id_me_mapping,
            )
            modifiers_me.add(modifier_me)
            d_id_me_mapping[modifier_me.id] = modifier_me
            d_modifier_species_id_me_mapping[
                modifier_me.species.id
            ] = modifier_me
    # We add each modifier that is not in a group and whose species is not a
    # gate (i.e., an individual modifier that is not an input of a gate)
    # to the modifiers set, and to the ungrouped_modifiers set. We also add each
    # modifier that is in a group to the ungrouped_modifiers_set.
    # Finally we add one modifier for each gate to the modifiers set.
    for modifier_me in modifiers_me:
        reaction_me.ungrouped_modifiers.add(modifier_me)
        if modifier_me.species.id not in in_group_modifier_species_ids:
            reaction_me.modifiers.add(modifier_me)
    for gate_me in gates_me:
        for input_ in gate_me.inputs:  # there is always at least one input
            break
        modifier_me = d_modifier_species_id_me_mapping[input_.id]
        modifier_me = dataclasses.replace(modifier_me, species=gate_me)
        reaction_me.modifiers.add(modifier_me)
    return reaction_me


def _reactant_to_model_element(
    reactant, builder, parent_model_element, d_id_me_mapping
):
    reactant_me = builder.new_model_element(momapy.celldesigner.core.Reactant)
    reactant_me.metaid = reactant.metaid
    reactant_me.species = d_id_me_mapping[reactant.species]
    reactant_me.stoichiometry = reactant.stoichiometry
    return reactant_me


def _product_to_model_element(
    product, builder, parent_model_element, d_id_me_mapping
):
    product_me = builder.new_model_element(momapy.celldesigner.core.Product)
    product_me.metaid = product.metaid
    product_me.species = d_id_me_mapping[product.species]
    product_me.stoichiometry = product.stoichiometry
    return product_me


def _boolean_logic_gate_to_model_element(
    gate, builder, parent_model_element, d_id_me_mapping
):
    gate_type = gate.type
    gate_me_cls = _CellDesignerBooleanLogicGateTypeMapping[gate_type]
    gate_me = builder.new_model_element(gate_me_cls)
    input_ids = gate.modifiers.split(",")
    for input_id in input_ids:
        input_ = d_id_me_mapping[input_id]
        gate_me.add_element(input_)
    return gate_me


def _modifier_to_model_element(
    modifier,
    builder,
    reaction_me,
    d_modifier_species_id_cls_mapping,
    d_id_me_mapping,
):
    modifier_me_cls = d_modifier_species_id_cls_mapping[modifier.species]
    modifier_me = builder.new_model_element(modifier_me_cls)
    modifier_me.metaid = modifier.metaid
    modifier_me.species = d_id_me_mapping[modifier.species]
    return modifier_me


def _compartment_alias_to_layout_element(
    compartment_alias,
    builder,
    d_id_le_mapping,
    d_id_me_mapping,
):
    compartment_me = d_id_me_mapping[compartment_alias.compartment]
    compartment_le_cls = _CellDesignerCompartmentLayoutTypeMapping[
        compartment_alias.class_value
    ]
    compartment_le = builder.new_layout_element(compartment_le_cls)
    compartment_le.id = compartment_alias.id
    bounds = compartment_alias.bounds
    width = float(bounds.w)
    height = float(bounds.h)
    position = momapy.geometry.PointBuilder(
        float(bounds.x) + width / 2, float(bounds.y) + height / 2
    )
    compartment_le.position = position
    compartment_le.width = width
    compartment_le.height = height
    double_line = compartment_alias.double_line
    compartment_le.outer_width = float(double_line.outer_width)
    compartment_le.inner_width = float(double_line.inner_width)
    compartment_le.sep = float(double_line.thickness)
    stroke = momapy.coloring.Color.from_hexa(
        compartment_alias.paint.color[2:] + compartment_alias.paint.color[:2]
    )
    compartment_le.outer_stroke = stroke
    compartment_le.inner_stroke = stroke
    compartment_le.outer_fill = stroke.with_alpha(0.25)
    label = builder.new_layout_element(momapy.core.TextLayout)
    label.text = compartment_me.name
    label.position = momapy.geometry.PointBuilder(
        float(compartment_alias.name_point.x),
        float(compartment_alias.name_point.y),
    )
    label.font_size = 12.0
    label.font_family = "Dialog"
    compartment_le.label = label
    return compartment_le


def _species_alias_to_layout_element(
    species_alias,
    builder,
    d_id_le_mapping,
    d_id_me_mapping,
    d_modification_residue_me_id_angle_mapping,
):
    species_me = d_id_me_mapping[species_alias.species]

    species_le_cls = _CellDesignerSpeciesLayoutTypeMapping[
        type(species_me)._cls_to_build
    ]
    species_le = builder.new_layout_element(species_le_cls)
    species_le.id = species_alias.id
    species_le.n = species_me.homodimer
    bounds = species_alias.bounds
    width = float(bounds.w)
    height = float(bounds.h)
    position = momapy.geometry.PointBuilder(
        float(bounds.x) + width / 2, float(bounds.y) + height / 2
    )
    species_le.position = position
    species_le.width = width
    species_le.height = height
    usual_view = species_alias.usual_view
    fill = momapy.coloring.Color.from_hexa(
        usual_view.paint.color[2:] + usual_view.paint.color[:2]
    )
    species_le.fill = fill
    stroke_width = float(usual_view.single_line.width)
    species_le.stroke_width = stroke_width
    label = builder.new_layout_element(momapy.core.TextLayout)
    label.text = species_me.name
    label.position = species_le.label_center()
    label.font_size = float(species_alias.font.size)
    label.font_family = "Dialog"
    species_le.label = label
    if hasattr(species_me, "structural_states"):
        for structural_state_me in species_me.structural_states:
            structural_state_le = _structural_state_to_layout_element(
                structural_state_me,
                builder,
                species_le,
                species_alias,
                d_id_le_mapping,
                d_id_me_mapping,
            )
            species_le.add_element(structural_state_le)
            builder.map_model_element_to_layout_element(
                structural_state_le, structural_state_me, species_le
            )
    if hasattr(species_me, "modifications"):
        # When a modification residue of a species is not filled with a value,
        # it has no corresponding modification, but it is represented
        # by an empty circle. Hence we track those that have no corresponding
        # modification
        residues_ids = set(
            [
                modification_residue_me.id
                for modification_residue_me in species_me.reference.modification_residues
            ]
        )
        residues_with_modification_ids = set([])
        for modification_me in species_me.modifications:
            modification_les = _modification_or_residue_id_to_layout_elements(
                modification_me,
                builder,
                species_le,
                d_id_le_mapping,
                d_id_me_mapping,
                d_modification_residue_me_id_angle_mapping,
            )
            for modification_le in modification_les:
                species_le.add_element(modification_le)
                builder.map_model_element_to_layout_element(
                    modification_le, modification_me, species_le
                )
            residues_with_modification_ids.add(modification_me.residue.id)
        # We make an empty modification layout for each residue that has no
        # corresponding modification
        for residue_id in residues_ids.difference(
            residues_with_modification_ids
        ):
            modification_les = _modification_or_residue_id_to_layout_elements(
                residue_id,
                builder,
                species_le,
                d_id_le_mapping,
                d_id_me_mapping,
                d_modification_residue_me_id_angle_mapping,
            )
            for modification_le in modification_les:
                species_le.add_element(modification_le)
    return species_le


def _structural_state_to_layout_element(
    structural_state_me,
    builder,
    species_le,
    species_alias,
    d_id_le_mapping,
    d_id_me_mapping,
):
    structural_state_le = builder.new_layout_element(
        momapy.celldesigner.core.StructuralStateLayout
    )
    angle = species_alias.structural_state.angle
    subunit_le = species_le._make_subunit(species_le.n - 1)
    structural_state_le.position = subunit_le.self_angle(angle, unit="radians")
    label = builder.new_layout_element(momapy.core.TextLayout)
    structural_state_value = structural_state_me.value
    if isinstance(structural_state_value, str):
        text = structural_state_value
    else:
        text = structural_state_value.name.lower()
    label.text = text
    label.position = structural_state_le.label_center()
    label.font_size = 9.0
    label.font_family = "sans-serif"
    structural_state_le.label = label
    if structural_state_le.width > subunit_le.width:
        structural_state_le.width = subunit_le.width
    else:
        ink_bbox = label.ink_bbox()
        if ink_bbox.width > subunit_le.width:
            structural_state_le.width = subunit_le.width
        elif ink_bbox.width > structural_state_le.width:
            structural_state_le.width = ink_bbox.width
    return structural_state_le


def _modification_or_residue_id_to_layout_elements(
    modification_me_or_residue_id,
    builder,
    species_le,
    d_id_le_mapping,
    d_id_me_mapping,
    d_modification_residue_me_id_angle_mapping,
):
    modification_les = []
    for i in range(species_le.n):
        modification_le = builder.new_layout_element(
            momapy.celldesigner.core.ModificationLayout
        )
        if momapy.builder.isinstance_or_builder(
            modification_me_or_residue_id, momapy.celldesigner.core.Modification
        ):
            residue_id = modification_me_or_residue_id.residue.id
        else:
            residue_id = modification_me_or_residue_id
        angle = d_modification_residue_me_id_angle_mapping[residue_id]
        subunit_le = species_le._make_subunit(i)
        p = momapy.geometry.Point(
            subunit_le.width * math.cos(angle),
            subunit_le.height * math.sin(angle),
        )
        angle = math.atan2(p.y, p.x)
        modification_le.position = subunit_le.self_angle(angle, unit="radians")
        if momapy.builder.isinstance_or_builder(
            modification_me_or_residue_id, momapy.celldesigner.core.Modification
        ):
            label = builder.new_layout_element(momapy.core.TextLayout)
            label.text = modification_me_or_residue_id.state.value
            label.position = modification_le.label_center()
            label.font_size = 9.0
            label.font_family = "sans-serif"
            modification_le.label = label
        modification_les.append(modification_le)
    residue = d_id_me_mapping[residue_id]
    if residue.name is not None:
        subunit_le = species_le._make_subunit(species_le.n - 1)
        label_name = builder.new_layout_element(momapy.core.TextLayout)
        label_name.text = residue.name
        segment = momapy.geometry.Segment(
            modification_les[-1].center(), subunit_le.center()
        )
        label_name.position = modification_le.position
        label_name.font_size = 9.0
        label_name.font_family = "sans-serif"
        ink_bbox = label_name.ink_bbox()
        length = 9.5 + math.sqrt(
            (math.cos(angle) * ink_bbox.width / 2) ** 2
            + (math.sin(angle) * ink_bbox.height / 2) ** 2
        )
        label_name.position = segment.get_position_at_fraction(
            length / segment.length()
        )
        modification_les[-1].add_element(label_name)
    return modification_les


def _reaction_to_layout_element(
    reaction, builder, d_id_le_mapping, d_id_me_mapping
):
    annotation = reaction.annotation
    extension = annotation.extension
    reaction_type = extension.reaction_type
    if reaction_type in _CellDesignerReactionLayoutTypeMapping:
        points = []
        reaction_le_cls = _CellDesignerReactionLayoutTypeMapping[reaction_type]
        reaction_le = builder.new_layout_element(reaction_le_cls)
        index = int(extension.connect_scheme.rectangle_index)
        for base_reactant in extension.base_reactants.base_reactant:
            base_reactant_le = d_id_le_mapping[base_reactant.alias]
            position = base_reactant.link_anchor.position
            anchor = _CellDesignerPositionAnchorMapping[position]
            start_point = getattr(base_reactant_le, anchor)()
        for base_product in extension.base_products.base_product:
            base_product_le = d_id_le_mapping[base_product.alias]
            position = base_product.link_anchor.position
            anchor = _CellDesignerPositionAnchorMapping[position]
            end_point = getattr(base_product_le, anchor)()
        if extension.edit_points is not None:
            for edit_point in extension.edit_points.value:
                segment = momapy.geometry.Segment(start_point, end_point)
                fractions = [
                    float(fraction) for fraction in edit_point.split(",")
                ]
                point = segment.p1 + (
                    fractions[0] * segment.length(),
                    fractions[1] * segment.length(),
                )
                angle = segment.get_angle()
                rotation = momapy.geometry.Rotation(angle, segment.p1)
                point = momapy.geometry.transform_point(point, rotation)
                points.append(point)
        points = [start_point] + points + [end_point]
        for i, point in enumerate(points[1:]):
            previous_point = points[i]
            segment = momapy.builder.get_or_make_builder_cls(
                momapy.geometry.Segment
            )(previous_point, point)
            reaction_le.segments.append(segment)
        reaction_node_le = builder.new_layout_element(
            momapy.celldesigner.core.ReactionNodeLayout
        )
        position, angle = reaction_le.segments[
            index
        ].get_position_and_angle_at_fraction(0.5)
        reaction_node_le.position = position
        rotation = momapy.geometry.Rotation(angle, position)
        if (
            reaction_node_le.transform is None
            or reaction_node_le.transform == momapy.drawing.NoneValue
        ):
            reaction_node_le.transform = momapy.core.TupleBuilder()
        reaction_node_le.transform.append(rotation)
        reaction_le.reaction_node = reaction_node_le
        if extension.list_of_reactant_links is not None:
            for reactant_link in extension.list_of_reactant_links.reactant_link:
                points = []
                _print(reactant_link)
                consumption_le = builder.new_layout_element(
                    momapy.celldesigner.core.ConsumptionLayout
                )
                reactant_le = d_id_le_mapping[reactant_link.alias]
                position = reactant_link.link_anchor.position
                anchor = _CellDesignerPositionAnchorMapping[position]
                start_point = getattr(reactant_le, anchor)()
                end_point = reaction_le.segments[
                    index
                ].get_position_at_fraction(0.40)
                if reactant_link.edit_points is not None:
                    for edit_point in reactant_link.edit_points.value:
                        segment = momapy.geometry.Segment(
                            start_point, end_point
                        )
                        fractions = [
                            float(fraction)
                            for fraction in edit_point.split(",")
                        ]
                        point = segment.p1 + (
                            fractions[0] * segment.length(),
                            fractions[1] * segment.length(),
                        )
                        angle = segment.get_angle()
                        rotation = momapy.geometry.Rotation(angle, segment.p1)
                        point = momapy.geometry.transform_point(point, rotation)
                        points.append(point)
                points = [start_point] + points + [end_point]
                for i, point in enumerate(points[1:]):
                    previous_point = points[i]
                    segment = momapy.builder.get_or_make_builder_cls(
                        momapy.geometry.Segment
                    )(previous_point, point)
                    consumption_le.segments.append(segment)
                reaction_le.add_element(consumption_le)
        if extension.list_of_product_links is not None:
            for product_link in extension.list_of_product_links.product_link:
                points = []
                _print(product_link)
                consumption_le = builder.new_layout_element(
                    momapy.celldesigner.core.ProductionLayout
                )
                start_point = reaction_le.segments[
                    index
                ].get_position_at_fraction(0.60)
                product_le = d_id_le_mapping[product_link.alias]
                position = product_link.link_anchor.position
                anchor = _CellDesignerPositionAnchorMapping[position]
                end_point = getattr(product_le, anchor)()
                if product_link.edit_points is not None:
                    for edit_point in product_link.edit_points.value:
                        segment = momapy.geometry.Segment(
                            start_point, end_point
                        )
                        fractions = [
                            float(fraction)
                            for fraction in edit_point.split(",")
                        ]
                        point = segment.p1 + (
                            fractions[0] * segment.length(),
                            fractions[1] * segment.length(),
                        )
                        angle = segment.get_angle()
                        rotation = momapy.geometry.Rotation(angle, segment.p1)
                        point = momapy.geometry.transform_point(point, rotation)
                        points.append(point)
                points = [start_point] + points + [end_point]
                for i, point in enumerate(points[1:]):
                    previous_point = points[i]
                    segment = momapy.builder.get_or_make_builder_cls(
                        momapy.geometry.Segment
                    )(previous_point, point)
                    consumption_le.segments.append(segment)
                reaction_le.add_element(consumption_le)
    else:
        reaction_le = None
    return reaction_le


def _print(obj, indent=0):
    if hasattr(obj, "__dict__"):
        for key, val in vars(obj).items():
            if not key.startswith("__"):
                print(f"{'  '*indent}{key}: {val}")
                _print(val, indent=indent + 1)
