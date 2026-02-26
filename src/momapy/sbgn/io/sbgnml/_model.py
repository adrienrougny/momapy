"""Standalone model-building functions for SBGN-ML reader."""

import momapy.builder
import momapy.core.elements
import momapy.sbgn.pd
import momapy.sbgn.io.sbgnml._parsing


def make_model_compartment(sbgnml_compartment, model, module):
    model_element = model.new_element(module.Compartment)
    model_element.id_ = sbgnml_compartment.get("id")
    sbgnml_label = getattr(sbgnml_compartment, "label", None)
    if sbgnml_label is not None:
        model_element.label = sbgnml_label.get("text")
    return model_element


def make_model_entity_pool_or_subunit(
    sbgnml_entity_pool_or_subunit, model, model_element_cls, sbgnml_id_to_model_element
):
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_entity_pool_or_subunit.get("id")
    sbgnml_compartment_ref = sbgnml_entity_pool_or_subunit.get("compartmentRef")
    if sbgnml_compartment_ref is not None:
        compartment_model_element = sbgnml_id_to_model_element[sbgnml_compartment_ref]
        model_element.compartment = compartment_model_element
    sbgnml_label = getattr(sbgnml_entity_pool_or_subunit, "label", None)
    if sbgnml_label is not None:
        model_element.label = sbgnml_label.get("text")
    return model_element


def make_model_activity(
    sbgnml_activity, model, model_element_cls, sbgnml_id_to_model_element
):
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_activity.get("id")
    sbgnml_compartment_ref = sbgnml_activity.get("compartmentRef")
    if sbgnml_compartment_ref is not None:
        compartment_model_element = sbgnml_id_to_model_element[sbgnml_compartment_ref]
        model_element.compartment = compartment_model_element
    sbgnml_label = getattr(sbgnml_activity, "label", None)
    if sbgnml_label is not None:
        model_element.label = sbgnml_label.get("text")
    return model_element


def make_model_state_variable(sbgnml_state_variable, model, order=None):
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


def make_model_unit_of_information(sbgnml_unit_of_information, model, model_element_cls):
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


def make_model_submap(sbgnml_submap, model, model_element_cls):
    sbgnml_label = getattr(sbgnml_submap, "label", None)
    sbgnml_id = sbgnml_submap.get("id")
    model_element = model.new_element(model_element_cls)
    if sbgnml_label is not None:
        model_element.label = sbgnml_label.get("text")
    model_element.id_ = sbgnml_id
    return model_element


def make_model_terminal_or_tag(sbgnml_terminal_or_tag, model, is_terminal):
    sbgnml_id = sbgnml_terminal_or_tag.get("id")
    sbgnml_label = getattr(sbgnml_terminal_or_tag, "label", None)
    if is_terminal:
        model_element_cls = momapy.sbgn.pd.Terminal
    else:
        model_element_cls = momapy.sbgn.pd.Tag
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_id
    if sbgnml_label is not None:
        model_element.label = sbgnml_label.get("text")
    return model_element


def make_model_reference(
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


def make_model_stoichiometric_process(
    sbgnml_process, model, model_element_cls, sbgnml_glyph_id_to_sbgnml_arcs
):
    sbgnml_id = sbgnml_process.get("id")
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_id
    model_element.reversible = momapy.sbgn.io.sbgnml._parsing.is_sbgnml_process_reversible(
        sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
    )
    return model_element


def make_model_reactant(sbgnml_consumption_arc, model, sbgnml_id_to_model_element):
    sbgnml_source_id = sbgnml_consumption_arc.get("source")
    sbgnml_stoichiometry = momapy.sbgn.io.sbgnml._parsing.get_stoichiometry_from_sbgnml_element(
        sbgnml_consumption_arc
    )
    model_element = model.new_element(momapy.sbgn.pd.Reactant)
    model_element.id_ = sbgnml_consumption_arc.get("id")
    source_model_element = sbgnml_id_to_model_element[sbgnml_source_id]
    model_element.element = source_model_element
    if sbgnml_stoichiometry is not None:
        sbgnml_label = getattr(sbgnml_stoichiometry, "label", None)
        if sbgnml_label is not None:
            sbgnml_stoichiometry_text = sbgnml_label.get("text")
            try:
                stoichiometry = float(sbgnml_stoichiometry_text)
            except ValueError:
                stoichiometry = sbgnml_stoichiometry_text
            model_element.stoichiometry = float(stoichiometry)
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_model_product(
    sbgnml_production_arc,
    model,
    sbgnml_id_to_model_element,
    super_model_element,
    super_sbgnml_element,
    process_direction,
):
    sbgnml_target_id = sbgnml_production_arc.get("target")
    sbgnml_stoichiometry = momapy.sbgn.io.sbgnml._parsing.get_stoichiometry_from_sbgnml_element(
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
    if sbgnml_stoichiometry is not None:
        sbgnml_label = getattr(sbgnml_stoichiometry, "label", None)
        if sbgnml_label is not None:
            sbgnml_stoichiometry_text = sbgnml_label.get("text")
            try:
                stoichiometry = float(sbgnml_stoichiometry_text)
            except ValueError:
                stoichiometry = sbgnml_stoichiometry_text
            model_element.stoichiometry = float(stoichiometry)
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_model_logical_operator(sbgnml_logical_operator, model, model_element_cls):
    sbgnml_id = sbgnml_logical_operator.get("id")
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_id
    return model_element


def make_model_logical_operator_input(sbgnml_logic_arc, model, source_model_element):
    model_element = model.new_element(momapy.sbgn.pd.LogicalOperatorInput)
    model_element.id_ = sbgnml_logic_arc.get("id")
    model_element.element = source_model_element
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element


def make_model_modulation(
    sbgnml_modulation, model, model_element_cls, source_model_element, target_model_element
):
    model_element = model.new_element(model_element_cls)
    model_element.id_ = sbgnml_modulation.get("id")
    model_element.source = source_model_element
    model_element.target = target_model_element
    model_element = momapy.builder.object_from_builder(model_element)
    return model_element
