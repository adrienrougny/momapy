import dataclasses

import momapy.core
import momapy.builder
import momapy.shapes
import momapy.arcs
import momapy.coloring

import momapy.celldesigner.core
import momapy.celldesigner.parser

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
}

_CellDesignerModifierTypeMapping = {
    (
        momapy.celldesigner.parser.ModificationType.MODULATION
    ): momapy.celldesigner.core.Modifier,
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
    ): momapy.celldesigner.core.PhysicalStimulation,
    (
        momapy.celldesigner.parser.ModificationType.TRIGGER
    ): momapy.celldesigner.core.Trigger,
}

_CellDesignerBooleanLogicGateTypeMapping = {
    (
        momapy.celldesigner.parser.ModificationType.BOOLEAN_LOGIC_GATE_AND
    ): momapy.celldesigner.core.AndGate,
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
}


_CellDesignerStructuralStateMapping = {
    "open": momapy.celldesigner.core.StructuralStateValue.OPEN,
    "closed": momapy.celldesigner.core.StructuralStateValue.CLOSED,
    "empty": momapy.celldesigner.core.StructuralStateValue.EMPTY,
}


def read_file(filename):
    config = xsdata.formats.dataclass.parsers.config.ParserConfig(
        fail_on_unknown_properties=False
    )
    parser = xsdata.formats.dataclass.parsers.XmlParser(
        config=config, context=xsdata.formats.dataclass.context.XmlContext()
    )
    sbml = parser.parse(filename, momapy.celldesigner.parser.Sbml)
    d_id_me_mapping = {}
    builder = momapy.celldesigner.core.CellDesignerMapBuilder()
    builder.model = builder.new_model()
    builder.layout = builder.new_layout()
    builder.model_layout_mapping = builder.new_model_layout_mapping()
    for species_reference in (
        sbml.model.annotation.extension.list_of_antisense_rnas.antisense_rna
        + sbml.model.annotation.extension.list_of_rnas.rna
        + sbml.model.annotation.extension.list_of_genes.gene
        + sbml.model.annotation.extension.list_of_proteins.protein
    ):
        species_reference_me = _species_reference_to_model_element(
            species_reference, builder, d_id_me_mapping
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
        reaction_me = _reaction_to_model_element(
            reaction, builder, d_id_me_mapping
        )
        builder.add_model_element(reaction_me)
        d_id_me_mapping[reaction_me.id] = reaction_me
    return builder


def _species_reference_to_model_element(
    species_reference, builder, d_id_me_mapping
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
    return species_reference_me


def _modification_residue_to_model_element(
    modification_residue, builder, species_reference_me, d_id_me_mapping
):
    id_ = modification_residue.id
    name = modification_residue.name
    modification_residue_me = builder.new_model_element(
        momapy.celldesigner.core.ModificationResidue
    )
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


def _species_to_model_element(species, builder, d_id_me_mapping):
    annotation = species.annotation
    extension = annotation.extension
    identity = extension.species_identity
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
    species_me.id = species.id
    species_me.name = species.name
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
                # gates since they also apear individually in
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
