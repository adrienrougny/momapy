"""CellDesigner model-building functions.

Functions for constructing momapy model objects from CellDesigner XML data.
"""

import frozendict
import lxml.etree

import momapy.celldesigner.core
import momapy.sbml.core
import momapy.celldesigner.io.celldesigner._reading_parsing

import momapy.sbml.io.sbml._parsing
import momapy.sbml.io.sbml._qualifiers

QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER = (
    momapy.sbml.io.sbml._qualifiers.QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER
)


def make_annotations(cd_rdf):
    annotations = []
    description = momapy.sbml.io.sbml._parsing.get_description(cd_rdf)
    if description is not None:
        for bq_element in description.getchildren():
            key = momapy.sbml.io.sbml._parsing.get_prefix_and_name(bq_element.tag)
            qualifier = QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER.get(key)
            if qualifier is not None:
                bags = momapy.sbml.io.sbml._parsing.get_bags(bq_element)
                for bag in bags:
                    lis = momapy.sbml.io.sbml._parsing.get_list_items(bag)
                    resources = [
                        li.get(
                            f"{{{momapy.sbml.io.sbml._parsing._RDF_NAMESPACE}}}resource"
                        )
                        for li in lis
                    ]
                    annotation = momapy.sbml.core.RDFAnnotation(
                        qualifier=qualifier,
                        resources=frozenset(resources),
                    )
                    annotations.append(annotation)
    return annotations


def make_notes(cd_element):
    cd_notes = momapy.celldesigner.io.celldesigner._reading_parsing.get_notes(cd_element)
    if cd_notes is not None:
        for child_element in cd_notes.iterchildren():
            break
        return [lxml.etree.tostring(child_element, encoding="unicode")]
    return []


def make_annotations_from_element(cd_element):
    cd_rdf = momapy.celldesigner.io.celldesigner._reading_parsing.get_rdf(cd_element)
    if cd_rdf is not None:
        annotations = make_annotations(cd_rdf)
    else:
        annotations = []
    return annotations


def make_annotations_from_notes(cd_notes):
    cd_rdf = momapy.celldesigner.io.celldesigner._reading_parsing.get_rdf_from_notes(cd_notes)
    if cd_rdf is not None:
        annotations = make_annotations(cd_rdf)
    else:
        annotations = []
    return annotations


def make_empty_model(cd_element):
    model = momapy.celldesigner.core.CellDesignerModelBuilder()
    return model


def make_empty_map(cd_element):
    map_ = momapy.celldesigner.core.CellDesignerMapBuilder()
    cd_map_id = cd_element.get("id")
    if cd_map_id is not None:
        map_.id_ = cd_map_id
    return map_


def make_compartment(cd_compartment, model):
    model_element = model.new_element(momapy.celldesigner.core.Compartment)
    model_element.id_ = cd_compartment.get("id")
    model_element.name = momapy.celldesigner.io.celldesigner._reading_parsing.make_name(
        cd_compartment.get("name")
    )
    model_element.metaid = cd_compartment.get("metaid")
    return model_element


def make_species_template(cd_species_template, model, model_element_cls):
    model_element = model.new_element(model_element_cls)
    model_element.id_ = cd_species_template.get("id")
    model_element.name = momapy.celldesigner.io.celldesigner._reading_parsing.make_name(
        cd_species_template.get("name")
    )
    return model_element


def make_modification_residue(cd_modification_residue, model, super_cd_element, order):
    model_element = model.new_element(momapy.celldesigner.core.ModificationResidue)
    cd_modification_residue_id = (
        f"{super_cd_element.get('id')}_{cd_modification_residue.get('id')}"
    )
    model_element.id_ = cd_modification_residue_id
    model_element.name = momapy.celldesigner.io.celldesigner._reading_parsing.make_name(
        cd_modification_residue.get("name")
    )
    model_element.order = order
    return model_element


def make_region(cd_region, model, model_element_cls, super_cd_element, order):
    model_element = model.new_element(model_element_cls)
    cd_region_id = f"{super_cd_element.get('id')}_{cd_region.get('id')}"
    model_element.id_ = cd_region_id
    model_element.name = momapy.celldesigner.io.celldesigner._reading_parsing.make_name(
        cd_region.get("name")
    )
    active = cd_region.get("active")
    if active is not None:
        model_element.active = True if active == "true" else False
    model_element.order = order
    return model_element


def make_species(
    cd_species,
    model,
    model_element_cls,
    name,
    homomultimer,
    hypothetical,
    active,
    cd_id_to_model_element,
    cd_id_to_cd_element,
):
    model_element = model.new_element(model_element_cls)
    model_element.id_ = cd_species.get("id")
    model_element.name = name
    model_element.metaid = cd_species.get("metaid")
    cd_compartment_id = cd_species.get("compartment")
    if cd_compartment_id is not None:
        compartment_model_element = cd_id_to_model_element[cd_compartment_id]
        model_element.compartment = compartment_model_element
    cd_species_template = (
        momapy.celldesigner.io.celldesigner._reading_parsing.get_template_from_species(
            cd_species, cd_id_to_cd_element
        )
    )
    if cd_species_template is not None:
        model_element.template = cd_id_to_model_element[cd_species_template.get("id")]
    model_element.homomultimer = homomultimer
    model_element.hypothetical = hypothetical
    model_element.active = active
    return model_element


def make_species_modification(
    model, modification_state, cd_id_to_model_element, cd_modification_residue_id
):
    model_element = model.new_element(momapy.celldesigner.core.Modification)
    modification_residue_model_element = cd_id_to_model_element[
        cd_modification_residue_id
    ]
    model_element.residue = modification_residue_model_element
    model_element.state = modification_state
    return model_element


def make_species_structural_state(cd_species_structural_state, model):
    model_element = model.new_element(momapy.celldesigner.core.StructuralState)
    model_element.value = cd_species_structural_state.get("structuralState")
    return model_element


def make_reaction(cd_reaction, model, model_element_cls):
    model_element = model.new_element(model_element_cls)
    model_element.id_ = cd_reaction.get("id")
    model_element.reversible = cd_reaction.get("reversible") == "true"
    return model_element


def make_reactant_from_base(
    cd_base_reactant, cd_reaction, model, cd_id_to_model_element
):
    model_element = model.new_element(momapy.celldesigner.core.Reactant)
    model_element.base = True
    cd_species_id = cd_base_reactant.get("species")
    for cd_reactant in momapy.celldesigner.io.celldesigner._reading_parsing.get_reactants(
        cd_reaction
    ):
        if cd_reactant.get("species") == cd_species_id:
            model_element.id_ = cd_reactant.get("metaid")
            cd_stoichiometry = cd_reactant.get("stoichiometry")
            if cd_stoichiometry is not None:
                model_element.stoichiometry = float(cd_stoichiometry)
            break
    if model_element.id_ is None:
        model_element.id_ = f"{cd_reaction.get('id')}_{cd_species_id}"
    species_model_element = cd_id_to_model_element[cd_base_reactant.get("alias")]
    model_element.referred_species = species_model_element
    return model_element


def make_reactant_from_link(
    cd_reactant_link, cd_reaction, model, cd_id_to_model_element
):
    model_element = model.new_element(momapy.celldesigner.core.Reactant)
    cd_species_id = cd_reactant_link.get("reactant")
    for cd_reactant in momapy.celldesigner.io.celldesigner._reading_parsing.get_reactants(
        cd_reaction
    ):
        if cd_reactant.get("species") == cd_species_id:
            model_element.id_ = cd_reactant.get("metaid")
            cd_stoichiometry = cd_reactant.get("stoichiometry")
            if cd_stoichiometry is not None:
                model_element.stoichiometry = float(cd_stoichiometry)
            break
    if model_element.id_ is None:
        model_element.id_ = f"{cd_reaction.get('id')}_{cd_species_id}"
    species_model_element = cd_id_to_model_element[cd_reactant_link.get("alias")]
    model_element.referred_species = species_model_element
    return model_element


def make_product_from_base(cd_base_product, cd_reaction, model, cd_id_to_model_element):
    model_element = model.new_element(momapy.celldesigner.core.Product)
    model_element.base = True
    cd_species_id = cd_base_product.get("species")
    for cd_product in momapy.celldesigner.io.celldesigner._reading_parsing.get_products(
        cd_reaction
    ):
        if cd_product.get("species") == cd_species_id:
            model_element.id_ = cd_product.get("metaid")
            cd_stoichiometry = cd_product.get("stoichiometry")
            if cd_stoichiometry is not None:
                model_element.stoichiometry = float(cd_stoichiometry)
            break
    if model_element.id_ is None:
        model_element.id_ = f"{cd_reaction.get('id')}_{cd_species_id}"
    species_model_element = cd_id_to_model_element[cd_base_product.get("alias")]
    model_element.referred_species = species_model_element
    return model_element


def make_product_from_link(cd_product_link, cd_reaction, model, cd_id_to_model_element):
    model_element = model.new_element(momapy.celldesigner.core.Product)
    cd_species_id = cd_product_link.get("product")
    for cd_product in momapy.celldesigner.io.celldesigner._reading_parsing.get_products(
        cd_reaction
    ):
        if cd_product.get("species") == cd_species_id:
            model_element.id_ = cd_product.get("metaid")
            cd_stoichiometry = cd_product.get("stoichiometry")
            if cd_stoichiometry is not None:
                model_element.stoichiometry = float(cd_stoichiometry)
            break
    if model_element.id_ is None:
        model_element.id_ = f"{cd_reaction.get('id')}_{cd_species_id}"
    species_model_element = cd_id_to_model_element[cd_product_link.get("alias")]
    model_element.referred_species = species_model_element
    return model_element


def make_modifier(model, model_element_cls, source_model_element, metaid=None):
    model_element = model.new_element(model_element_cls)
    model_element.referred_species = source_model_element
    if metaid is not None:
        model_element.metaid = metaid
    return model_element


def make_logic_gate(model, model_element_cls, cd_input_ids, cd_id_to_model_element):
    model_element = model.new_element(model_element_cls)
    model_input_elements = [
        cd_id_to_model_element[cd_input_id] for cd_input_id in cd_input_ids
    ]
    for model_input_element in model_input_elements:
        model_element.inputs.add(model_input_element)
    return model_element


def make_modulation(
    cd_reaction, model, model_element_cls, source_model_element, target_model_element
):
    model_element = model.new_element(model_element_cls)
    model_element.id_ = cd_reaction.get("id")
    model_element.source = source_model_element
    model_element.target = target_model_element
    return model_element
