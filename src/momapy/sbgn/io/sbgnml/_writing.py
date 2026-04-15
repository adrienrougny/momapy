"""Pure helper functions for SBGN-ML XML element construction."""

import lxml.etree

import momapy.sbml.io.sbml._qualifiers

NSMAP = {
    None: "http://sbgn.org/libsbgn/0.3",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "bqmodel": "http://biomodels.net/model-qualifiers/",
    "bqbiol": "http://biomodels.net/biology-qualifiers/",
}


def make_lxml_element(tag, namespace=None, attributes=None, text=None, nsmap=None):
    if namespace is not None:
        lxml_tag = f"{{{namespace}}}{tag}"
    else:
        lxml_tag = tag
    if nsmap is None:
        nsmap = {}
    if attributes is None:
        attributes = {}
    lxml_element = lxml.etree.Element(lxml_tag, nsmap=nsmap, **attributes)
    if text is not None:
        lxml_element.text = text
    return lxml_element


def get_sbgnml_id(map_element, ids):
    sbgnml_ids = ids.get(map_element)
    if sbgnml_ids is None:
        return map_element.id_
    return sbgnml_ids[0]


def make_sbgnml_bbox_from_node(node):
    attributes = {
        "x": str(node.x - node.width / 2),
        "y": str(node.y - node.height / 2),
        "w": str(node.width),
        "h": str(node.height),
    }
    return make_lxml_element("bbox", attributes=attributes)


def make_sbgnml_bbox_from_text_layout(text_layout):
    bbox = text_layout.bbox()
    attributes = {
        "x": str(bbox.x - bbox.width / 2),
        "y": str(bbox.y - bbox.height / 2),
        "w": str(bbox.width),
        "h": str(bbox.height),
    }
    return make_lxml_element("bbox", attributes=attributes)


def make_sbgnml_label(text_layout):
    attributes = {"text": text_layout.text}
    sbgnml_label = make_lxml_element("label", attributes=attributes)
    sbgnml_bbox = make_sbgnml_bbox_from_text_layout(text_layout)
    sbgnml_label.append(sbgnml_bbox)
    return sbgnml_label


def make_sbgnml_state(text_layout):
    attributes = {}
    text_split = text_layout.text.split("@")
    if len(text_split) > 1:
        attributes["variable"] = text_split[-1]
    if text_split[0]:
        attributes["value"] = text_split[0]
    return make_lxml_element("state", attributes=attributes)


def make_sbgnml_port(point, port_id):
    attributes = {"id": port_id, "x": str(point.x), "y": str(point.y)}
    return make_lxml_element("port", attributes=attributes)


def make_sbgnml_points(points):
    sbgnml_elements = []
    start_point = points[0]
    sbgnml_elements.append(
        make_lxml_element("start", attributes={"x": str(start_point.x), "y": str(start_point.y)})
    )
    for point in points[1:-1]:
        sbgnml_elements.append(
            make_lxml_element("next", attributes={"x": str(point.x), "y": str(point.y)})
        )
    end_point = points[-1]
    sbgnml_elements.append(
        make_lxml_element("end", attributes={"x": str(end_point.x), "y": str(end_point.y)})
    )
    return sbgnml_elements


def make_sbgnml_annotation(annotations, sbgnml_id):
    sbgnml_annotation = make_lxml_element("annotation")
    sbgnml_rdf = make_lxml_element(
        tag="RDF", namespace=NSMAP["rdf"], nsmap=NSMAP
    )
    sbgnml_annotation.append(sbgnml_rdf)
    sbgnml_description = make_lxml_element(
        tag="Description",
        namespace=NSMAP["rdf"],
        attributes={f"{{{NSMAP['rdf']}}}about": f"#{sbgnml_id}"},
    )
    sbgnml_rdf.append(sbgnml_description)
    for annotation in annotations:
        namespace, tag = momapy.sbml.io.sbml._qualifiers.QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE[
            annotation.qualifier
        ]
        sbgnml_bq = make_lxml_element(tag=tag, namespace=namespace)
        sbgnml_description.append(sbgnml_bq)
        sbgnml_bag = make_lxml_element(tag="Bag", namespace=NSMAP["rdf"])
        sbgnml_bq.append(sbgnml_bag)
        for resource in annotation.resources:
            sbgnml_li = make_lxml_element(
                tag="li",
                namespace=NSMAP["rdf"],
                attributes={f"{{{NSMAP['rdf']}}}resource": resource},
            )
            sbgnml_bag.append(sbgnml_li)
    return sbgnml_annotation


def add_annotations_and_notes(writing_context, sbgnml_element, model_element):
    """Append annotation and notes XML to an SBGN-ML element if present."""
    if writing_context.with_annotations and writing_context.element_to_annotations:
        element_annotations = writing_context.element_to_annotations.get(model_element)
        if element_annotations:
            sbgnml_annot = make_sbgnml_annotation(
                element_annotations,
                sbgnml_id=sbgnml_element.get("id"),
            )
            sbgnml_extension = make_lxml_element("extension")
            sbgnml_extension.append(sbgnml_annot)
            sbgnml_element.append(sbgnml_extension)
    if writing_context.with_notes and writing_context.element_to_notes:
        element_notes = writing_context.element_to_notes.get(model_element)
        if element_notes:
            for note in element_notes:
                sbgnml_notes = make_lxml_element(tag="notes")
                notes_root = lxml.etree.fromstring(note)
                sbgnml_notes.append(notes_root)
                sbgnml_element.append(sbgnml_notes)
