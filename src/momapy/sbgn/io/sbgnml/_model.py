"""Standalone model-building functions for SBGN-ML reader."""

import lxml.etree

import momapy.builder
import momapy.core.elements
import momapy.sbgn.pd
import momapy.sbml.core
import momapy.sbgn.io.sbgnml._parsing
import momapy.sbgn.io.sbgnml._qualifiers


def make_annotations(sbgnml_element):
    annotations = []
    sbgnml_rdf = momapy.sbgn.io.sbgnml._parsing.get_rdf(sbgnml_element)
    if sbgnml_rdf is not None:
        description = momapy.sbgn.io.sbgnml._parsing.get_description(sbgnml_rdf)
        if description is not None:
            for bq_element in description.getchildren():
                key = momapy.sbgn.io.sbgnml._parsing.get_prefix_and_name(bq_element.tag)
                qualifier = momapy.sbgn.io.sbgnml._qualifiers.QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER.get(key)
                if qualifier is not None:
                    bags = momapy.sbgn.io.sbgnml._parsing.get_bags(bq_element)
                    for bag in bags:
                        lis = momapy.sbgn.io.sbgnml._parsing.get_list_items(bag)
                        resources = [
                            li.get(
                                f"{{{momapy.sbgn.io.sbgnml._parsing._RDF_NAMESPACE}}}resource"
                            )
                            for li in lis
                        ]
                        annotation = momapy.sbml.core.RDFAnnotation(
                            qualifier=qualifier,
                            resources=frozenset(resources),
                        )
                        annotations.append(annotation)
    return annotations


def make_notes(sbgnml_element):
    sbgnml_notes = momapy.sbgn.io.sbgnml._parsing.get_notes(sbgnml_element)
    if sbgnml_notes is not None:
        for child_element in sbgnml_notes.iterchildren():
            break
        notes = lxml.etree.tostring(child_element)
        return notes
    return []


def set_label(model_element, sbgnml_element):
    sbgnml_label = getattr(sbgnml_element, "label", None)
    if sbgnml_label is not None:
        model_element.label = sbgnml_label.get("text")


def set_compartment(
    model_element, sbgnml_element, sbgnml_id_to_model_element
):
    sbgnml_compartment_ref = sbgnml_element.get("compartmentRef")
    if sbgnml_compartment_ref is not None:
        model_element.compartment = sbgnml_id_to_model_element[sbgnml_compartment_ref]


def set_stoichiometry(model_element, sbgnml_stoichiometry):
    if sbgnml_stoichiometry is None:
        return
    sbgnml_label = getattr(sbgnml_stoichiometry, "label", None)
    if sbgnml_label is not None:
        sbgnml_stoichiometry_text = sbgnml_label.get("text")
        try:
            stoichiometry = float(sbgnml_stoichiometry_text)
        except ValueError:
            stoichiometry = sbgnml_stoichiometry_text
        model_element.stoichiometry = float(stoichiometry)


def make_compartment(sbgnml_compartment, model, module):
    model_element = model.new_element(module.Compartment)
    model_element.id_ = sbgnml_compartment.get("id")
    set_label(model_element, sbgnml_compartment)
    return model_element


def make_entity_pool_or_subunit(
    sbgnml_entity_pool_or_subunit, model, model_element_cls, sbgnml_id_to_model_element
):
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_entity_pool_or_subunit.get("id")
    set_compartment(
        model_element, sbgnml_entity_pool_or_subunit, sbgnml_id_to_model_element
    )
    set_label(model_element, sbgnml_entity_pool_or_subunit)
    return model_element


def make_activity(
    sbgnml_activity, model, model_element_cls, sbgnml_id_to_model_element
):
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_activity.get("id")
    set_compartment(
        model_element, sbgnml_activity, sbgnml_id_to_model_element
    )
    set_label(model_element, sbgnml_activity)
    return model_element


def make_state_variable(sbgnml_state_variable, model, order=None):
    sbgnml_id = sbgnml_state_variable.get("id")
    sbgnml_state = getattr(sbgnml_state_variable, "state", None)
    if sbgnml_state is None:
        value = None
        variable = None
    else:
        sbgnml_value = sbgnml_state.get("value")
        if sbgnml_value:
            value = sbgnml_value
        else:
            value = None
        sbgnml_variable = sbgnml_state.get("variable")
        variable = sbgnml_variable
    model_element = model.new_element(momapy.sbgn.pd.StateVariable)
    model_element.id_ = sbgnml_id
    model_element.value = value
    model_element.variable = variable
    model_element.order = order
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_unit_of_information(sbgnml_unit_of_information, model, model_element_cls):
    sbgnml_label = getattr(sbgnml_unit_of_information, "label", None)
    sbgnml_id = sbgnml_unit_of_information.get("id")
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_id
    if sbgnml_label is not None:
        split_label = sbgnml_label.get("text").split(":")
        model_element.value = split_label[-1]
        if len(split_label) > 1:
            model_element.prefix = split_label[0]
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_submap(sbgnml_submap, model, model_element_cls):
    sbgnml_id = sbgnml_submap.get("id")
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_id
    set_label(model_element, sbgnml_submap)
    return model_element


def make_terminal_or_tag(sbgnml_terminal_or_tag, model, is_terminal):
    sbgnml_id = sbgnml_terminal_or_tag.get("id")
    if is_terminal:
        model_element_cls = momapy.sbgn.pd.Terminal
    else:
        model_element_cls = momapy.sbgn.pd.Tag
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_id
    set_label(model_element, sbgnml_terminal_or_tag)
    return model_element


def make_reference(
    sbgnml_equivalence_arc, model, sbgnml_id_to_model_element, is_terminal
):
    sbgnml_id = sbgnml_equivalence_arc.get("id")
    # For terminals and tags, equivalence arc goes from the referred node
    # to the terminal or tag. We invert the arc, so that the arc goes
    # from the reference to the referred node.
    sbgnml_target_id = sbgnml_equivalence_arc.get("source")
    if is_terminal:
        model_element_cls = momapy.sbgn.pd.TerminalReference
    else:
        model_element_cls = momapy.sbgn.pd.TagReference
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_id
    target_model_element = sbgnml_id_to_model_element[sbgnml_target_id]
    model_element.element = target_model_element
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_stoichiometric_process(
    sbgnml_process, model, model_element_cls, sbgnml_glyph_id_to_sbgnml_arcs
):
    sbgnml_id = sbgnml_process.get("id")
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_id
    model_element.reversible = momapy.sbgn.io.sbgnml._parsing.is_process_reversible(
        sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
    )
    return model_element


def make_reactant(sbgnml_consumption_arc, model, sbgnml_id_to_model_element):
    sbgnml_source_id = sbgnml_consumption_arc.get("source")
    sbgnml_stoichiometry = momapy.sbgn.io.sbgnml._parsing.get_stoichiometry(
        sbgnml_consumption_arc
    )
    model_element = model.new_element(momapy.sbgn.pd.Reactant)
    model_element.id_ = sbgnml_consumption_arc.get("id")
    source_model_element = sbgnml_id_to_model_element[sbgnml_source_id]
    model_element.element = source_model_element
    set_stoichiometry(model_element, sbgnml_stoichiometry)
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_product(
    sbgnml_production_arc,
    model,
    sbgnml_id_to_model_element,
    super_model_element,
    super_sbgnml_element,
    process_direction,
):
    sbgnml_target_id = sbgnml_production_arc.get("target")
    sbgnml_stoichiometry = momapy.sbgn.io.sbgnml._parsing.get_stoichiometry(
        sbgnml_production_arc
    )
    if super_model_element.reversible:
        if process_direction == momapy.core.elements.Direction.HORIZONTAL:
            if float(sbgnml_production_arc.start.get("x")) > float(
                super_sbgnml_element.bbox.get("x")
            ):  # RIGHT
                model_element_cls = momapy.sbgn.pd.Product
            else:
                model_element_cls = momapy.sbgn.pd.Reactant  # LEFT
        else:
            if float(sbgnml_production_arc.start.get("y")) > float(
                super_sbgnml_element.bbox.get("y")
            ):  # TOP
                model_element_cls = momapy.sbgn.pd.Product
            else:
                model_element_cls = momapy.sbgn.pd.Reactant  # BOTTOM
    else:
        model_element_cls = momapy.sbgn.pd.Product
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_production_arc.get("id")
    target_model_element = sbgnml_id_to_model_element[sbgnml_target_id]
    model_element.element = target_model_element
    set_stoichiometry(model_element, sbgnml_stoichiometry)
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_logical_operator(sbgnml_logical_operator, model, model_element_cls):
    sbgnml_id = sbgnml_logical_operator.get("id")
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_id
    return model_element


def make_logical_operator_input(sbgnml_logic_arc, model, source_model_element):
    model_element = model.new_element(momapy.sbgn.pd.LogicalOperatorInput)
    model_element.id_ = sbgnml_logic_arc.get("id")
    model_element.element = source_model_element
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_modulation(
    sbgnml_modulation, model, model_element_cls, source_model_element, target_model_element
):
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_modulation.get("id")
    model_element.source = source_model_element
    model_element.target = target_model_element
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element
