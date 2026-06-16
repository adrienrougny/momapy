"""SBML model-building functions.

Functions for constructing momapy model objects from SBML XML data.
"""

import lxml.etree

from momapy.builder import new_builder_object
from momapy.builder import object_from_builder
from momapy.sbml.model import Compartment
from momapy.sbml.model import ModifierSpeciesReference
from momapy.sbml.model import RDFAnnotation
from momapy.sbml.model import Reaction
from momapy.sbml.model import SBMLModel
from momapy.sbml.model import Species
from momapy.sbml.model import SpeciesReference
from momapy.sbml.io.sbml._parsing import _RDF_NAMESPACE
from momapy.sbml.io.sbml._parsing import get_bags
from momapy.sbml.io.sbml._parsing import get_description
from momapy.sbml.io.sbml._parsing import get_list_items
from momapy.sbml.io.sbml._parsing import get_notes
from momapy.sbml.io.sbml._parsing import get_prefix_and_name
from momapy.sbml.io.sbml._parsing import get_rdf
from momapy.sbml.io.sbml._qualifiers import (
    QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER,
)


def make_annotations(rdf):
    """Build RDF annotations from an ``rdf:RDF`` element.

    Shared across SBML, CellDesigner and SBGN-ML readers.

    Args:
        rdf: The ``rdf:RDF`` lxml.objectify element.

    Returns:
        A list of ``momapy.sbml.model.RDFAnnotation`` objects.
    """
    annotations = []
    description = get_description(rdf)
    if description is not None:
        for bq_element in description.iterchildren():
            key = get_prefix_and_name(bq_element.tag)
            qualifier = QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER.get(key)
            if qualifier is not None:
                bags = get_bags(bq_element)
                for bag in bags:
                    lis = get_list_items(bag)
                    resources = [li.get(f"{{{_RDF_NAMESPACE}}}resource") for li in lis]
                    annotation = RDFAnnotation(
                        qualifier=qualifier,
                        resources=frozenset(resources),
                    )
                    annotations.append(annotation)
    return annotations


def make_notes(notes_element):
    """Serialize the first XML child of a ``notes`` element.

    Shared across SBML, CellDesigner and SBGN-ML readers.

    Args:
        notes_element: The ``notes`` lxml.objectify element, or ``None``.

    Returns:
        A list containing the serialized first child, or an empty list.
    """
    if notes_element is None:
        return []
    first_child = next(notes_element.iterchildren(), None)
    if first_child is None:
        return []
    return [lxml.etree.tostring(first_child, encoding="unicode")]


def make_annotations_from_element(sbml_element):
    sbml_rdf = get_rdf(sbml_element)
    if sbml_rdf is not None:
        annotations = make_annotations(sbml_rdf)
    else:
        annotations = []
    return annotations


def make_notes_from_element(sbml_element):
    sbml_notes = get_notes(sbml_element)
    return make_notes(sbml_notes)


def make_empty_model(sbml_element):
    model = new_builder_object(SBMLModel)
    return model


def make_compartment(sbml_compartment, model):
    model_element = new_builder_object(Compartment)
    model_element.id_ = sbml_compartment.get("id")
    model_element.name = sbml_compartment.get("name")
    model_element.metaid = sbml_compartment.get("metaid")
    model_element.sbo_term = sbml_compartment.get("sboTerm")
    return model_element


def make_species(sbml_species, model, sbml_id_to_model_element):
    model_element = new_builder_object(Species)
    model_element.name = sbml_species.get("name")
    model_element.id_ = sbml_species.get("id")
    model_element.metaid = sbml_species.get("metaid")
    model_element.sbo_term = sbml_species.get("sboTerm")
    sbml_compartment_id = sbml_species.get("compartment")
    if sbml_compartment_id is not None:
        model_element.compartment = sbml_id_to_model_element[sbml_compartment_id]
    return model_element


def make_reaction(sbml_reaction, model):
    model_element = new_builder_object(Reaction)
    model_element.id_ = sbml_reaction.get("id")
    model_element.name = sbml_reaction.get("name")
    model_element.sbo_term = sbml_reaction.get("sboTerm")
    model_element.reversible = sbml_reaction.get("reversible") == "true"
    return model_element


def make_species_reference(sbml_species_reference, model, sbml_id_to_model_element):
    model_element = new_builder_object(SpeciesReference)
    model_element.id_ = sbml_species_reference.get("metaid")
    sbml_stoichiometry = sbml_species_reference.get("stoichiometry")
    if sbml_stoichiometry is not None:
        model_element.stoichiometry = float(sbml_stoichiometry)
    sbml_species_id = sbml_species_reference.get("species")
    model_element.referred_species = sbml_id_to_model_element[sbml_species_id]
    model_element = object_from_builder(model_element)
    return model_element


def make_modifier_species_reference(
    sbml_modifier_species_reference, model, sbml_id_to_model_element
):
    model_element = new_builder_object(ModifierSpeciesReference)
    model_element.id_ = sbml_modifier_species_reference.get("metaid")
    sbml_species_id = sbml_modifier_species_reference.get("species")
    model_element.referred_species = sbml_id_to_model_element[sbml_species_id]
    model_element = object_from_builder(model_element)
    return model_element
