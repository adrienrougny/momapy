"""SBGN-ML XML parsing utilities.

Pure XML traversal and data-extraction functions for SBGN-ML documents.
No momapy object construction happens here: all functions work with lxml
objectify trees and return raw Python / geometry values.
"""

import momapy.core.elements


_RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


def transform_class(sbgnml_class):
    return sbgnml_class.upper().replace(" ", "_")


def has_undefined_variable(sbgnml_state_variable):
    sbgnml_state = getattr(sbgnml_state_variable, "state", None)
    if sbgnml_state is None:
        return True
    sbgnml_variable = sbgnml_state.get("variable")
    return sbgnml_variable is None


def get_glyphs(sbgnml_element):
    return list(getattr(sbgnml_element, "glyph", []))


def get_glyphs_recursively(sbgnml_element):
    sub_glyphs = []
    for sub_glyph in get_glyphs(sbgnml_element):
        sub_glyphs.append(sub_glyph)
        sub_glyphs += get_glyphs_recursively(sub_glyph)
    return sub_glyphs


def get_arcs(sbgnml_element):
    return list(getattr(sbgnml_element, "arc", []))


def get_ports(sbgnml_element):
    return list(getattr(sbgnml_element, "port", []))


def get_nexts(sbgnml_arc):
    return list(getattr(sbgnml_arc, "next", []))


def get_sbgnml_points(sbgnml_arc):
    return (
        [sbgnml_arc.start]
        + get_nexts(sbgnml_arc)
        + [sbgnml_arc.end]
    )



def get_annotation(sbgnml_element):
    extension = getattr(sbgnml_element, "extension", None)
    if extension is None:
        return None
    annotation = getattr(extension, "annotation", None)
    if annotation is None:
        return getattr(
            extension, "{}annotation", None
        )  # to account for bug in libsbgn: no namespace
    return annotation


def get_notes(sbgnml_element):
    return getattr(sbgnml_element, "notes", None)




def get_rdf(sbgnml_element):
    annotation = get_annotation(sbgnml_element)
    if annotation is None:
        return None
    return getattr(annotation, f"{{{_RDF_NAMESPACE}}}RDF", None)


def get_description(rdf):
    return getattr(rdf, "Description", None)


def get_bags(bq_element):
    return list(getattr(bq_element, f"{{{_RDF_NAMESPACE}}}Bag", []))


def get_list_items(bag):
    return list(getattr(bag, "li", []))


def get_prefix_and_name(tag):
    prefix, name = tag.split("}")
    return prefix[1:], name


_SBGNML_STATE_VARIABLE_CLASSES = {"state variable"}

_SBGNML_UNIT_OF_INFORMATION_CLASSES = {"unit of information"}

_SBGNML_TERMINAL_CLASSES = {"terminal"}

_SBGNML_SUBUNIT_CLASSES = {
    "unspecified entity",
    "macromolecule",
    "macromolecule multimer",
    "simple chemical",
    "simple chemical multimer",
    "nucleic acid feature",
    "nucleic acid feature multimer",
    "complex",
    "complex multimer",
}


def get_state_variables(sbgnml_element):
    return [
        subglyph
        for subglyph in get_glyphs(sbgnml_element)
        if subglyph.get("class") in _SBGNML_STATE_VARIABLE_CLASSES
    ]


def get_units_of_information(sbgnml_element):
    return [
        subglyph
        for subglyph in get_glyphs(sbgnml_element)
        if subglyph.get("class") in _SBGNML_UNIT_OF_INFORMATION_CLASSES
    ]


def get_subunits(sbgnml_element):
    return [
        subglyph
        for subglyph in get_glyphs(sbgnml_element)
        if subglyph.get("class") in _SBGNML_SUBUNIT_CLASSES
    ]


def get_terminals(sbgnml_element):
    return [
        subglyph
        for subglyph in get_glyphs(sbgnml_element)
        if subglyph.get("class") in _SBGNML_TERMINAL_CLASSES
    ]


def get_stoichiometry(sbgnml_element):
    for sbgnml_subglyph in get_glyphs(sbgnml_element):
        if sbgnml_subglyph.get("class") == "stoichiometry":
            return sbgnml_subglyph
    return None


def get_consumption_and_production_arcs(
    sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
):
    sbgnml_consumption_arcs = []
    sbgnml_production_arcs = []
    for sbgnml_arc in sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_process.get("id")]:
        if transform_class(sbgnml_arc.get("class")) == "CONSUMPTION":
            sbgnml_consumption_arcs.append(sbgnml_arc)
        elif transform_class(sbgnml_arc.get("class")) == "PRODUCTION":
            sbgnml_production_arcs.append(sbgnml_arc)
    return sbgnml_consumption_arcs, sbgnml_production_arcs


def get_equivalence_arcs(
    sbgnml_tag_or_terminal,
    sbgnml_id_to_sbgnml_element,
    sbgnml_glyph_id_to_sbgnml_arcs,
):
    sbgnml_equivalence_arcs = []
    for sbgnml_arc in sbgnml_glyph_id_to_sbgnml_arcs[
        sbgnml_tag_or_terminal.get("id")
    ]:
        if (
            transform_class(sbgnml_arc.get("class")) == "EQUIVALENCE_ARC"
            and sbgnml_id_to_sbgnml_element[sbgnml_arc.get("target")]
            == sbgnml_tag_or_terminal
        ):
            sbgnml_equivalence_arcs.append(sbgnml_arc)
    return sbgnml_equivalence_arcs


def get_logic_arcs(
    sbgnml_operator,
    sbgnml_id_to_sbgnml_element,
    sbgnml_glyph_id_to_sbgnml_arcs,
):
    sbgnml_logic_arcs = []
    for sbgnml_arc in sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_operator.get("id")]:
        if (
            transform_class(sbgnml_arc.get("class")) == "LOGIC_ARC"
            and sbgnml_id_to_sbgnml_element[sbgnml_arc.get("target")]
            == sbgnml_operator
        ):
            sbgnml_logic_arcs.append(sbgnml_arc)
    return sbgnml_logic_arcs


def get_process_direction(sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs):
    for sbgnml_port in get_ports(sbgnml_process):
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


def get_direction(sbgnml_element):
    sbgnml_orientation = sbgnml_element.get("orientation")
    if sbgnml_orientation is None:
        return momapy.core.elements.Direction.RIGHT
    orientation = transform_class(sbgnml_orientation)
    return momapy.core.elements.Direction[orientation]


def is_operator_left_to_right(
    sbgnml_operator,
    sbgnml_id_to_sbgnml_element,
    sbgnml_glyph_id_to_sbgnml_arcs,
):
    sbgnml_logic_arcs = get_logic_arcs(
        sbgnml_operator,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
    )
    operator_direction = get_process_direction(
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


def is_process_left_to_right(sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs):
    process_direction = get_process_direction(
        sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
    )
    sbgnml_consumption_arcs, sbgnml_production_arcs = (
        get_consumption_and_production_arcs(
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


def is_process_reversible(sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs):
    sbgnml_consumption_arcs, _ = (
        get_consumption_and_production_arcs(
            sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
        )
    )
    if sbgnml_consumption_arcs:
        return False
    return True


def get_connectors_length(sbgnml_process):
    left_connector_length = None
    right_connector_length = None
    sbgnml_bbox = sbgnml_process.bbox
    sbgnml_bbox_x = float(sbgnml_bbox.get("x"))
    sbgnml_bbox_y = float(sbgnml_bbox.get("y"))
    sbgnml_bbox_w = float(sbgnml_bbox.get("w"))
    sbgnml_bbox_h = float(sbgnml_bbox.get("h"))
    for sbgnml_port in get_ports(sbgnml_process):
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
