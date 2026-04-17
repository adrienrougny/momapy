"""CellDesigner model-building functions.

Each ``make_*`` function takes a ``reading_context`` as its first
argument, checks whether ``reading_context.model`` is ``None``, and
returns ``None`` early when no model is being built.
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
        for bq_element in description:
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
    if cd_notes is None:
        return []
    first_child = next(iter(cd_notes), None)
    if first_child is None:
        return []
    return [lxml.etree.tostring(first_child, encoding="unicode")]


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


def make_and_add_annotations(reading_context, cd_element, model_element):
    """Add annotations from an XML element to the reading context.

    Args:
        reading_context: The reading context.
        cd_element: The CellDesigner XML element.
        model_element: The frozen model element to associate with.
    """
    if reading_context.with_annotations:
        annotations = make_annotations_from_element(cd_element)
        if annotations:
            reading_context.element_to_annotations[model_element].update(
                annotations
            )


def make_empty_model(cd_element):
    model = momapy.celldesigner.core.CellDesignerModelBuilder()
    return model


def make_empty_map(cd_element):
    map_ = momapy.celldesigner.core.CellDesignerMapBuilder()
    cd_map_id = cd_element.get("id")
    if cd_map_id is not None:
        map_.id_ = cd_map_id
    return map_


def make_compartment(reading_context, cd_compartment):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(momapy.celldesigner.core.Compartment)
    model_element.id_ = cd_compartment.get("id")
    model_element.name = momapy.celldesigner.io.celldesigner._reading_parsing.make_name(
        cd_compartment.get("name")
    )
    model_element.metaid = cd_compartment.get("metaid")
    return model_element


def make_species_template(reading_context, cd_species_template, model_element_cls):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
    model_element.id_ = cd_species_template.get("id")
    model_element.name = momapy.celldesigner.io.celldesigner._reading_parsing.make_name(
        cd_species_template.get("name")
    )
    return model_element


def make_modification_residue(
    reading_context, cd_modification_residue, super_cd_element, order
):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(
        momapy.celldesigner.core.ModificationResidue
    )
    cd_modification_residue_id = (
        f"{super_cd_element.get('id')}_{cd_modification_residue.get('id')}"
    )
    model_element.id_ = cd_modification_residue_id
    model_element.name = momapy.celldesigner.io.celldesigner._reading_parsing.make_name(
        cd_modification_residue.get("name")
    )
    model_element.order = order
    return model_element


def make_region(reading_context, cd_region, model_element_cls, super_cd_element, order):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
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
    reading_context,
    cd_species,
    model_element_cls,
    name,
    homomultimer,
    hypothetical,
    active,
):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
    model_element.id_ = cd_species.get("id")
    model_element.name = name
    model_element.metaid = cd_species.get("metaid")
    cd_compartment_id = cd_species.get("compartment")
    if cd_compartment_id is not None:
        compartment_model_element = reading_context.xml_id_to_model_element[
            cd_compartment_id
        ]
        model_element.compartment = compartment_model_element
    cd_species_template = (
        momapy.celldesigner.io.celldesigner._reading_parsing.get_template_from_species(
            cd_species, reading_context.xml_id_to_xml_element
        )
    )
    if cd_species_template is not None:
        model_element.template = reading_context.xml_id_to_model_element[
            cd_species_template.get("id")
        ]
    model_element.homomultimer = homomultimer
    model_element.hypothetical = hypothetical
    model_element.active = active
    return model_element


def make_species_modification(
    reading_context, modification_state, cd_modification_residue_id
):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(momapy.celldesigner.core.Modification)
    modification_residue_model_element = reading_context.xml_id_to_model_element[
        cd_modification_residue_id
    ]
    model_element.residue = modification_residue_model_element
    model_element.state = modification_state
    return model_element


def make_species_structural_state(reading_context, cd_species_structural_state):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(momapy.celldesigner.core.StructuralState)
    model_element.value = cd_species_structural_state.get("structuralState")
    return model_element


def make_reaction(reading_context, cd_reaction, model_element_cls):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
    model_element.id_ = cd_reaction.get("id")
    model_element.reversible = cd_reaction.get("reversible") == "true"
    return model_element


def make_reactant_from_base(reading_context, cd_base_reactant, cd_reaction):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(momapy.celldesigner.core.Reactant)
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
    species_model_element = reading_context.xml_id_to_model_element[
        cd_base_reactant.get("alias")
    ]
    model_element.referred_species = species_model_element
    return model_element


def make_reactant_from_link(reading_context, cd_reactant_link, cd_reaction):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(momapy.celldesigner.core.Reactant)
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
    species_model_element = reading_context.xml_id_to_model_element[
        cd_reactant_link.get("alias")
    ]
    model_element.referred_species = species_model_element
    return model_element


def make_product_from_base(reading_context, cd_base_product, cd_reaction):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(momapy.celldesigner.core.Product)
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
    species_model_element = reading_context.xml_id_to_model_element[
        cd_base_product.get("alias")
    ]
    model_element.referred_species = species_model_element
    return model_element


def make_product_from_link(reading_context, cd_product_link, cd_reaction):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(momapy.celldesigner.core.Product)
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
    species_model_element = reading_context.xml_id_to_model_element[
        cd_product_link.get("alias")
    ]
    model_element.referred_species = species_model_element
    return model_element


def make_modifier(reading_context, model_element_cls, source_model_element, metaid):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
    model_element.referred_species = source_model_element
    model_element.id_ = metaid
    model_element.metaid = metaid
    return model_element


def make_logic_gate(reading_context, model_element_cls):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
    return model_element


def make_logic_gate_input(reading_context, input_model_element):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(
        momapy.celldesigner.core.BooleanLogicGateInput
    )
    model_element.element = input_model_element
    return model_element


def make_modulation(
    reading_context, cd_reaction, model_element_cls, source_model_element, target_model_element
):
    if reading_context.model is None:
        return None
    model_element = reading_context.model.new_element(model_element_cls)
    model_element.id_ = cd_reaction.get("id")
    model_element.source = source_model_element
    model_element.target = target_model_element
    return model_element
