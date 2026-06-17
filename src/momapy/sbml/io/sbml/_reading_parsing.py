"""SBML XML parsing utilities.

Pure XML traversal and data-extraction functions for SBML documents.
No momapy object construction happens here: all functions work with lxml
objectify trees and return raw Python values.
"""

_RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


def get_prefix_and_name(tag):
    prefix, name = tag.split("}")
    return prefix[1:], name


def get_description(rdf):
    return getattr(rdf, "Description", None)


def get_bags(bq_element):
    return list(getattr(bq_element, f"{{{_RDF_NAMESPACE}}}Bag", []))


def get_list_items(bag):
    return list(getattr(bag, "li", []))


# --- SBML-specific functions ---


def get_annotation(sbml_element):
    return getattr(sbml_element, "annotation", None)


def get_species(sbml_model):
    list_of_species = getattr(sbml_model, "listOfSpecies", None)
    if list_of_species is None:
        return []
    return list(getattr(list_of_species, "species", []))


def get_reactions(sbml_model):
    list_of_reactions = getattr(sbml_model, "listOfReactions", None)
    if list_of_reactions is None:
        return []
    return list(getattr(list_of_reactions, "reaction", []))


def get_compartments(sbml_model):
    list_of_compartments = getattr(sbml_model, "listOfCompartments", None)
    if list_of_compartments is None:
        return []
    return list(getattr(list_of_compartments, "compartment", []))


def get_reactants(sbml_reaction):
    list_of_reactants = getattr(sbml_reaction, "listOfReactants", None)
    if list_of_reactants is None:
        return []
    return list(getattr(list_of_reactants, "speciesReference", []))


def get_products(sbml_reaction):
    list_of_products = getattr(sbml_reaction, "listOfProducts", None)
    if list_of_products is None:
        return []
    return list(getattr(list_of_products, "speciesReference", []))


def get_modifiers(sbml_reaction):
    list_of_modifiers = getattr(sbml_reaction, "listOfModifiers", None)
    if list_of_modifiers is None:
        return []
    return list(getattr(list_of_modifiers, "modifierSpeciesReference", []))


def get_notes(sbml_element):
    return getattr(sbml_element, "notes", None)


def get_rdf(sbml_element):
    annotation = get_annotation(sbml_element)
    if annotation is None:
        return None
    return getattr(annotation, f"{{{_RDF_NAMESPACE}}}RDF", None)


def make_id_to_element_mapping(sbml_model):
    sbml_id_to_sbml_element = {}
    for sbml_compartment in get_compartments(sbml_model):
        sbml_id_to_sbml_element[sbml_compartment.get("id")] = sbml_compartment
    for sbml_species in get_species(sbml_model):
        sbml_id_to_sbml_element[sbml_species.get("id")] = sbml_species
    return sbml_id_to_sbml_element
