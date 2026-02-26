"""SBGN-ML XML parsing utilities.

Pure XML traversal and data-extraction functions for SBGN-ML documents.
No momapy object construction happens here: all functions work with lxml
objectify trees and return raw Python / geometry values.
"""

import lxml.etree

import momapy.geometry
import momapy.core.elements
import momapy.sbml.core


_RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

_QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER = {
    (
        "http://biomodels.net/biology-qualifiers/",
        "encodes",
    ): momapy.sbml.core.BQBiol.ENCODES,
    (
        "http://biomodels.net/biology-qualifiers/",
        "hasPart",
    ): momapy.sbml.core.BQBiol.HAS_PART,
    (
        "http://biomodels.net/biology-qualifiers/",
        "hasProperty",
    ): momapy.sbml.core.BQBiol.HAS_PROPERTY,
    (
        "http://biomodels.net/biology-qualifiers/",
        "hasVersion",
    ): momapy.sbml.core.BQBiol.HAS_VERSION,
    (
        "http://biomodels.net/biology-qualifiers/",
        "is",
    ): momapy.sbml.core.BQBiol.IS,
    (
        "http://biomodels.net/biology-qualifiers/",
        "isDescribedBy",
    ): momapy.sbml.core.BQBiol.IS_DESCRIBED_BY,
    (
        "http://biomodels.net/biology-qualifiers/",
        "isEncodedBy",
    ): momapy.sbml.core.BQBiol.IS_ENCODED_BY,
    (
        "http://biomodels.net/biology-qualifiers/",
        "isHomologTo",
    ): momapy.sbml.core.BQBiol.IS_HOMOLOG_TO,
    (
        "http://biomodels.net/biology-qualifiers/",
        "isPartOf",
    ): momapy.sbml.core.BQBiol.IS_PART_OF,
    (
        "http://biomodels.net/biology-qualifiers/",
        "isPropertyOf",
    ): momapy.sbml.core.BQBiol.IS_PROPERTY_OF,
    (
        "http://biomodels.net/biology-qualifiers/",
        "isVersionOf",
    ): momapy.sbml.core.BQBiol.IS_VERSION_OF,
    (
        "http://biomodels.net/biology-qualifiers/",
        "occursIn",
    ): momapy.sbml.core.BQBiol.OCCURS_IN,
    (
        "http://biomodels.net/biology-qualifiers/",
        "hasTaxon",
    ): momapy.sbml.core.BQBiol.HAS_TAXON,
    (
        "http://biomodels.net/biology-qualifiers/",
        "hasInstance",
    ): momapy.sbml.core.BQModel.HAS_INSTANCE,
    (
        "http://biomodels.net/model-qualifiers/",
        "is",
    ): momapy.sbml.core.BQModel.IS,
    (
        "http://biomodels.net/model-qualifiers/",
        "isDerivedFrom",
    ): momapy.sbml.core.BQModel.IS_DERIVED_FROM,
    (
        "http://biomodels.net/model-qualifiers/",
        "isDescribedBy",
    ): momapy.sbml.core.BQModel.IS_DESCRIBED_BY,
    (
        "http://biomodels.net/model-qualifiers/",
        "isInstanceOf",
    ): momapy.sbml.core.BQModel.IS_INSTANCE_OF,
}


def transform_sbgnml_class(sbgnml_class):
    return sbgnml_class.upper().replace(" ", "_")


def has_sbgnml_state_variable_undefined_variable(sbgnml_state_variable):
    sbgnml_state = getattr(sbgnml_state_variable, "state", None)
    if sbgnml_state is None:
        return True
    sbgnml_variable = sbgnml_state.get("variable")
    return sbgnml_variable is None


def get_glyphs_from_sbgnml_element(sbgnml_element):
    return list(getattr(sbgnml_element, "glyph", []))


def get_glyphs_recursively_from_sbgnml_element(sbgnml_element):
    sub_glyphs = []
    for sub_glyph in get_glyphs_from_sbgnml_element(sbgnml_element):
        sub_glyphs.append(sub_glyph)
        sub_glyphs += get_glyphs_recursively_from_sbgnml_element(sub_glyph)
    return sub_glyphs


def get_arcs_from_sbgnml_element(sbgnml_element):
    return list(getattr(sbgnml_element, "arc", []))


def get_ports_from_sbgnml_element(sbgnml_element):
    return list(getattr(sbgnml_element, "port", []))


def get_nexts_from_sbgnml_arc(sbgnml_arc):
    return list(getattr(sbgnml_arc, "next", []))


def get_sbgnml_points_from_sbgnml_arc(sbgnml_arc):
    return (
        [sbgnml_arc.start]
        + get_nexts_from_sbgnml_arc(sbgnml_arc)
        + [sbgnml_arc.end]
    )


def make_points_from_sbgnml_points(sbgnml_points):
    return [
        momapy.geometry.Point(
            float(sbgnml_point.get("x")), float(sbgnml_point.get("y"))
        )
        for sbgnml_point in sbgnml_points
    ]


def make_segments_from_points(points):
    segments = []
    for current_point, following_point in zip(points[:-1], points[1:]):
        segment = momapy.geometry.Segment(current_point, following_point)
        segments.append(segment)
    return segments


def get_annotation_from_sbgnml_element(sbgnml_element):
    extension = getattr(sbgnml_element, "extension", None)
    if extension is None:
        return None
    annotation = getattr(extension, "annotation", None)
    if annotation is None:
        return getattr(
            extension, "{}annotation", None
        )  # to account for bug in libsbgn: no namespace
    return annotation


def get_notes_from_sbgnml_element(sbgnml_element):
    return getattr(sbgnml_element, "notes", None)


def make_notes_from_sbgnml_element(sbgnml_element):
    sbgnml_notes = get_notes_from_sbgnml_element(sbgnml_element)
    if sbgnml_notes is not None:
        for child_element in sbgnml_notes.iterchildren():
            break
        notes = lxml.etree.tostring(child_element)
        return notes
    return []


def get_rdf_from_sbgnml_element(sbgnml_element):
    annotation = get_annotation_from_sbgnml_element(sbgnml_element)
    if annotation is None:
        return None
    return getattr(annotation, f"{{{_RDF_NAMESPACE}}}RDF", None)


def get_description_from_rdf(rdf):
    return getattr(rdf, "Description", None)


def get_bags_from_bq_element(bq_element):
    return list(getattr(bq_element, f"{{{_RDF_NAMESPACE}}}Bag", []))


def get_lis_from_bag(bag):
    return list(getattr(bag, "li", []))


def get_prefix_and_name_from_tag(tag):
    prefix, name = tag.split("}")
    return prefix[1:], name


def make_annotations_from_sbgnml_rdf(sbgnml_rdf):
    annotations = []
    description = get_description_from_rdf(sbgnml_rdf)
    if description is not None:
        for bq_element in description.getchildren():
            key = get_prefix_and_name_from_tag(bq_element.tag)
            qualifier = _QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER.get(key)
            if qualifier is not None:
                bags = get_bags_from_bq_element(bq_element)
                for bag in bags:
                    lis = get_lis_from_bag(bag)
                    resources = [
                        li.get(f"{{{_RDF_NAMESPACE}}}resource") for li in lis
                    ]
                    annotation = momapy.sbml.core.RDFAnnotation(
                        qualifier=qualifier,
                        resources=frozenset(resources),
                    )
                    annotations.append(annotation)
    return annotations


def make_annotations_from_sbgnml_element(sbgnml_element):
    sbgnml_rdf = get_rdf_from_sbgnml_element(sbgnml_element)
    if sbgnml_rdf is not None:
        return make_annotations_from_sbgnml_rdf(sbgnml_rdf)
    return []


def get_stoichiometry_from_sbgnml_element(sbgnml_element):
    for sbgnml_subglyph in get_glyphs_from_sbgnml_element(sbgnml_element):
        if sbgnml_subglyph.get("class") == "stoichiometry":
            return sbgnml_subglyph
    return None


def get_sbgnml_consumption_and_production_arcs_from_sbgnml_process(
    sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
):
    sbgnml_consumption_arcs = []
    sbgnml_production_arcs = []
    for sbgnml_arc in sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_process.get("id")]:
        if transform_sbgnml_class(sbgnml_arc.get("class")) == "CONSUMPTION":
            sbgnml_consumption_arcs.append(sbgnml_arc)
        elif transform_sbgnml_class(sbgnml_arc.get("class")) == "PRODUCTION":
            sbgnml_production_arcs.append(sbgnml_arc)
    return sbgnml_consumption_arcs, sbgnml_production_arcs


def get_sbgnml_equivalence_arcs_from_sbgnml_tag_or_terminal(
    sbgnml_tag_or_terminal,
    sbgnml_id_to_sbgnml_element,
    sbgnml_glyph_id_to_sbgnml_arcs,
):
    sbgnml_equivalence_arcs = []
    for sbgnml_arc in sbgnml_glyph_id_to_sbgnml_arcs[
        sbgnml_tag_or_terminal.get("id")
    ]:
        if (
            transform_sbgnml_class(sbgnml_arc.get("class")) == "EQUIVALENCE_ARC"
            and sbgnml_id_to_sbgnml_element[sbgnml_arc.get("target")]
            == sbgnml_tag_or_terminal
        ):
            sbgnml_equivalence_arcs.append(sbgnml_arc)
    return sbgnml_equivalence_arcs


def get_sbgnml_logic_arcs_from_sbgnml_operator(
    sbgnml_operator,
    sbgnml_id_to_sbgnml_element,
    sbgnml_glyph_id_to_sbgnml_arcs,
):
    sbgnml_logic_arcs = []
    for sbgnml_arc in sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_operator.get("id")]:
        if (
            transform_sbgnml_class(sbgnml_arc.get("class")) == "LOGIC_ARC"
            and sbgnml_id_to_sbgnml_element[sbgnml_arc.get("target")]
            == sbgnml_operator
        ):
            sbgnml_logic_arcs.append(sbgnml_arc)
    return sbgnml_logic_arcs


def get_sbgnml_process_direction(sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs):
    for sbgnml_port in get_ports_from_sbgnml_element(sbgnml_process):
        if float(sbgnml_port.get("x")) < float(
            sbgnml_process.bbox.get("x")
        ) or float(sbgnml_port.get("x")) >= float(
            sbgnml_process.bbox.get("x")
        ) + float(
            sbgnml_process.bbox.get("w")
        ):  # LEFT OR RIGHT
            return momapy.core.elements.Direction.HORIZONTAL
        else:
            return momapy.core.elements.Direction.VERTICAL
    return momapy.core.elements.Direction.VERTICAL  # default is vertical


def get_direction_from_sbgnml_element(sbgnml_element):
    sbgnml_orientation = sbgnml_element.get("orientation")
    if sbgnml_orientation is None:
        return momapy.core.elements.Direction.RIGHT
    orientation = transform_sbgnml_class(sbgnml_orientation)
    return momapy.core.elements.Direction[orientation]


def is_sbgnml_operator_left_to_right(
    sbgnml_operator,
    sbgnml_id_to_sbgnml_element,
    sbgnml_glyph_id_to_sbgnml_arcs,
):
    sbgnml_logic_arcs = get_sbgnml_logic_arcs_from_sbgnml_operator(
        sbgnml_operator,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
    )
    operator_direction = get_sbgnml_process_direction(
        sbgnml_operator, sbgnml_glyph_id_to_sbgnml_arcs
    )
    for sbgnml_logic_arc in sbgnml_logic_arcs:
        if operator_direction == momapy.core.elements.Direction.HORIZONTAL:
            if float(sbgnml_logic_arc.end.get("x")) < float(
                sbgnml_operator.bbox.get("x")
            ):
                return True
            else:
                return False
        else:
            if float(sbgnml_logic_arc.end.get("y")) < float(
                sbgnml_operator.bbox.get("y")
            ):
                return True
            else:
                return False
    return True


def is_sbgnml_process_left_to_right(sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs):
    process_direction = get_sbgnml_process_direction(
        sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
    )
    sbgnml_consumption_arcs, sbgnml_production_arcs = (
        get_sbgnml_consumption_and_production_arcs_from_sbgnml_process(
            sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
        )
    )
    if sbgnml_production_arcs:
        if not sbgnml_production_arcs:  # process is reversible
            return True  # defaults to left to right
        sbgnml_production_arc = sbgnml_production_arcs[0]
        if process_direction == momapy.core.elements.Direction.HORIZONTAL:
            if float(sbgnml_production_arc.start.get("x")) >= float(
                sbgnml_process.bbox.get("x")
            ):
                return True
            else:
                return False
        else:
            if float(sbgnml_production_arc.start.get("y")) >= float(
                sbgnml_process.bbox.get("y")
            ):
                return True
            return False
    if sbgnml_consumption_arcs:
        sbgnml_consumption_arc = sbgnml_consumption_arcs[0]
        if process_direction == momapy.core.elements.Direction.HORIZONTAL:
            if float(sbgnml_consumption_arc.end.get("x")) <= float(
                sbgnml_process.bbox.get("x")
            ):
                return True
            else:
                return False
        else:
            if float(sbgnml_consumption_arc.end.get("y")) <= float(
                sbgnml_process.bbox.get("y")
            ):
                return True
            return False


def is_sbgnml_process_reversible(sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs):
    sbgnml_consumption_arcs, _ = (
        get_sbgnml_consumption_and_production_arcs_from_sbgnml_process(
            sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
        )
    )
    if sbgnml_consumption_arcs:
        return False
    return True


def get_connectors_length_from_sbgnml_process(sbgnml_process):
    left_connector_length = None
    right_connector_length = None
    sbgnml_bbox = sbgnml_process.bbox
    sbgnml_bbox_x = float(sbgnml_bbox.get("x"))
    sbgnml_bbox_y = float(sbgnml_bbox.get("y"))
    sbgnml_bbox_w = float(sbgnml_bbox.get("w"))
    sbgnml_bbox_h = float(sbgnml_bbox.get("h"))
    for sbgnml_port in get_ports_from_sbgnml_element(sbgnml_process):
        sbgnml_port_x = float(sbgnml_port.get("x"))
        sbgnml_port_y = float(sbgnml_port.get("y"))
        if sbgnml_port_x < sbgnml_bbox_x:  # LEFT
            left_connector_length = sbgnml_bbox_x - sbgnml_port_x
        elif sbgnml_port_y < sbgnml_bbox_y:  # UP
            left_connector_length = sbgnml_bbox_y - sbgnml_port_y
        elif sbgnml_port_x >= sbgnml_bbox_x + sbgnml_bbox_w:  # RIGHT
            right_connector_length = sbgnml_port_x - sbgnml_bbox_x - sbgnml_bbox_w
        elif sbgnml_port_y >= sbgnml_bbox_y + sbgnml_bbox_h:  # DOWN
            right_connector_length = sbgnml_port_y - sbgnml_bbox_y - sbgnml_bbox_h
    return left_connector_length, right_connector_length
