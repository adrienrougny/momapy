"""CellDesigner model-building functions.

Functions for constructing momapy model objects from CellDesigner XML data.
"""

import frozendict
import lxml.etree

import momapy.celldesigner.core
import momapy.sbml.core
import momapy.celldesigner.io.celldesigner._parsing

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
                        li.get(f"{{{momapy.sbml.io.sbml._parsing._RDF_NAMESPACE}}}resource")
                        for li in lis
                    ]
                    annotation = momapy.sbml.core.RDFAnnotation(
                        qualifier=qualifier,
                        resources=frozenset(resources),
                    )
                    annotations.append(annotation)
    return annotations


def make_notes(cd_element):
    _parsing = momapy.celldesigner.io.celldesigner._parsing
    cd_notes = _parsing.get_notes(cd_element)
    if cd_notes is not None:
        for child_element in cd_notes.iterchildren():
            break
        return lxml.etree.tostring(child_element)
    return []


def make_annotations_from_element(cd_element):
    _parsing = momapy.celldesigner.io.celldesigner._parsing
    cd_rdf = _parsing.get_rdf(cd_element)
    if cd_rdf is not None:
        annotations = make_annotations(cd_rdf)
    else:
        annotations = []
    return annotations


def make_annotations_from_notes(cd_notes):
    _parsing = momapy.celldesigner.io.celldesigner._parsing
    cd_rdf = _parsing.get_rdf_from_notes(cd_notes)
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
    map_.id_ = cd_element.get("id")
    return map_
