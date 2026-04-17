"""SBML model-building functions.

Functions for constructing momapy model objects from SBML XML data.
"""

import frozendict
import lxml.etree

import momapy.builder
import momapy.sbml.core
import momapy.sbml.io.sbml._parsing
import momapy.sbml.io.sbml._qualifiers


def make_annotations(sbml_rdf):
    annotations = []
    description = momapy.sbml.io.sbml._parsing.get_description(sbml_rdf)
    if description is not None:
        for bq_element in description:
            key = momapy.sbml.io.sbml._parsing.get_prefix_and_name(bq_element.tag)
            qualifier = momapy.sbml.io.sbml._qualifiers.QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER.get(key)
            if qualifier is not None:
                bags = momapy.sbml.io.sbml._parsing.get_bags(bq_element)
                for bag in bags:
                    lis = momapy.sbml.io.sbml._parsing.get_list_items(bag)
                    resources = [
                        li.get(f"{{{momapy.sbml.io.sbml._parsing._RDF_NAMESPACE}}}resource")
                        for li in lis
                    ]
                    annotation = momapy.sbml.core.RDFAnnotation(
                        qualifier=qualifier,
                        resources=frozenset(resources),
                    )
                    annotations.append(annotation)
    return annotations


def make_notes(sbml_element):
    sbml_notes = momapy.sbml.io.sbml._parsing.get_notes(sbml_element)
    if sbml_notes is None:
        return []
    first_child = next(iter(sbml_notes), None)
    if first_child is None:
        return []
    return [lxml.etree.tostring(first_child, encoding="unicode")]


def make_annotations_from_element(sbml_element):
    sbml_rdf = momapy.sbml.io.sbml._parsing.get_rdf(sbml_element)
    if sbml_rdf is not None:
        annotations = make_annotations(sbml_rdf)
    else:
        annotations = []
    return annotations


def make_empty_model(sbml_element):
    model = momapy.sbml.core.SBMLModelBuilder()
    return model


def make_compartment(sbml_compartment, model):
    model_element = model.new_element(momapy.sbml.core.Compartment)
    model_element.id_ = sbml_compartment.get("id")
    model_element.name = sbml_compartment.get("name")
    model_element.metaid = sbml_compartment.get("metaid")
    model_element.sbo_term = sbml_compartment.get("sboTerm")
    return model_element


def make_species(sbml_species, model, sbml_id_to_model_element):
    model_element = model.new_element(momapy.sbml.core.Species)
    model_element.name = sbml_species.get("name")
    model_element.id_ = sbml_species.get("id")
    model_element.metaid = sbml_species.get("metaid")
    model_element.sbo_term = sbml_species.get("sboTerm")
    sbml_compartment_id = sbml_species.get("compartment")
    if sbml_compartment_id is not None:
        model_element.compartment = sbml_id_to_model_element[sbml_compartment_id]
    return model_element


def make_reaction(sbml_reaction, model):
    model_element = model.new_element(momapy.sbml.core.Reaction)
    model_element.id_ = sbml_reaction.get("id")
    model_element.name = sbml_reaction.get("name")
    model_element.sbo_term = sbml_reaction.get("sboTerm")
    model_element.reversible = sbml_reaction.get("reversible") == "true"
    return model_element


def make_species_reference(sbml_species_reference, model, sbml_id_to_model_element):
    model_element = model.new_element(momapy.sbml.core.SpeciesReference)
    model_element.id_ = sbml_species_reference.get("metaid")
    sbml_stoichiometry = sbml_species_reference.get("stoichiometry")
    if sbml_stoichiometry is not None:
        model_element.stoichiometry = float(sbml_stoichiometry)
    sbml_species_id = sbml_species_reference.get("species")
    model_element.referred_species = sbml_id_to_model_element[sbml_species_id]
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_modifier_species_reference(sbml_modifier_species_reference, model, sbml_id_to_model_element):
    model_element = model.new_element(momapy.sbml.core.ModifierSpeciesReference)
    model_element.id_ = sbml_modifier_species_reference.get("metaid")
    sbml_species_id = sbml_modifier_species_reference.get("species")
    model_element.referred_species = sbml_id_to_model_element[sbml_species_id]
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element
