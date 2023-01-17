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


def read_file(filename):
    config = xsdata.formats.dataclass.parsers.config.ParserConfig(
        fail_on_unknown_properties=False
    )
    parser = xsdata.formats.dataclass.parsers.XmlParser(
        config=config, context=xsdata.formats.dataclass.context.XmlContext()
    )
    sbml = parser.parse(filename, momapy.celldesigner.parser.Sbml)
    d_model_elements_ids = {}
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
        model_element = _species_reference_to_model_element(
            species_reference, builder, d_model_elements_ids
        )
        builder.add_model_element(model_element)
        d_model_elements_ids[model_element.id] = model_element
    for species in sbml.model.list_of_species.species:
        model_element = _species_to_model_element(
            species, builder, d_model_elements_ids
        )
        builder.add_model_element(model_element)
        d_model_elements_ids[model_element.id] = model_element
    return builder


def _species_reference_to_model_element(
    species_reference, builder, d_model_elements_ids
):
    id_ = species_reference.id
    name = species_reference.name
    type_ = species_reference.type
    cls = _CellDesignerSpeciesReferenceTypeMapping[type_]
    model_element = builder.new_model_element(cls)
    model_element.id = id_
    model_element.name = name
    if hasattr(species_reference, "list_of_modification_residues"):
        list_of_modification_residues = (
            species_reference.list_of_modification_residues
        )
        if list_of_modification_residues is not None:
            for (
                modification_residue
            ) in list_of_modification_residues.modification_residue:
                child_model_element = _modification_residue_to_model_element(
                    modification_residue,
                    builder,
                    model_element,
                    d_model_elements_ids,
                )
                model_element.add_element(child_model_element)
                d_model_elements_ids[
                    (model_element.id, child_model_element.id)
                ] = child_model_element
    return model_element


def _modification_residue_to_model_element(
    modification_residue, builder, parent_model_element, d_model_elements_ids
):
    id_ = modification_residue.id
    name = modification_residue.name
    model_element = builder.new_model_element(
        momapy.celldesigner.core.ModificationResidue
    )
    model_element.id = id_
    model_element.name = name
    return model_element


def _modification_to_model_element(
    modification, builder, parent_model_element, d_model_elements_ids
):
    residue = d_model_elements_ids[
        (parent_model_element.reference.id, modification.residue)
    ]
    state = modification.state
    model_element = builder.new_model_element(
        momapy.celldesigner.core.Modification
    )
    model_element.residue = residue
    model_element.state = momapy.celldesigner.core.ModificationState[state.name]
    return model_element


def _species_to_model_element(species, builder, d_model_elements_ids):
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
        species_reference = d_model_elements_ids[
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
    print(species, "\n")
    cls = _CellDesignerSpeciesTypeMapping[type_]
    model_element = builder.new_model_element(cls)
    model_element.id = species.id
    model_element.name = species.name
    if has_reference:
        model_element.reference = species_reference
    if state is not None:
        homodimer = state.homodimer
        if homodimer is not None:
            model_element.homodimer = homodimer
        list_of_modifications = state.list_of_modifications
        if list_of_modifications is not None:
            for modification in list_of_modifications.modification:
                child_model_element = _modification_to_model_element(
                    modification, builder, model_element, d_model_elements_ids
                )
                model_element.add_element(child_model_element)
                d_model_elements_ids[
                    child_model_element.id
                ] = child_model_element
        list_of_structural_states = state.list_of_structural_states
        if list_of_structural_states is not None:
            for structural_state in list_of_structural_states.structural_state:
                child_model_element = _structural_state_to_model_element(
                    structural_state,
                    builder,
                    model_element,
                    d_model_elements_ids,
                )
                model_element.add_element(child_model_element)
                d_model_elements_ids[
                    child_model_element.id
                ] = child_model_element

    return model_element
