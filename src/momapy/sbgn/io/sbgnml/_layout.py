"""Standalone layout-building functions for SBGN-ML reader."""

import momapy.geometry
import momapy.core.elements
import momapy.core.layout
import momapy.builder
import momapy.coloring
import momapy.drawing
import momapy.sbgn.pd
import momapy.sbgn.io.sbgnml._parsing

_DEFAULT_FONT_FAMILY = momapy.drawing.DEFAULT_FONT_FAMILY
_DEFAULT_FONT_SIZE = 11.0
_DEFAULT_AUXILIARY_UNIT_FONT_SIZE = 9.0
_DEFAULT_FONT_FILL = momapy.coloring.black


def set_layout_element_position_and_size_from_sbgnml_glyph(
    layout_element, sbgnml_glyph
):
    sbgnml_bbox = sbgnml_glyph.bbox
    x = float(sbgnml_bbox.get("x"))
    y = float(sbgnml_bbox.get("y"))
    w = float(sbgnml_bbox.get("w"))
    h = float(sbgnml_bbox.get("h"))
    layout_element.position = momapy.geometry.Point(x + w / 2, y + h / 2)
    layout_element.width = w
    layout_element.height = h


def make_layout_compartment(sbgnml_compartment, layout, module):
    sbgnml_label = getattr(sbgnml_compartment, "label", None)
    layout_element = layout.new_element(module.CompartmentLayout)
    layout_element.id_ = sbgnml_compartment.get("id")
    set_layout_element_position_and_size_from_sbgnml_glyph(
        layout_element, sbgnml_compartment
    )
    if sbgnml_label is not None:
        text = sbgnml_label.get("text")
        if text is None:
            text = ""
        text_layout = momapy.core.layout.TextLayout(
            text=text,
            font_size=_DEFAULT_FONT_SIZE,
            font_family=_DEFAULT_FONT_FAMILY,
            fill=_DEFAULT_FONT_FILL,
            stroke=momapy.drawing.NoneValue,
            position=layout_element.center(),
            horizontal_alignment=momapy.core.elements.HAlignment.CENTER,
        )
        layout_element.label = text_layout
    return layout_element


def make_layout_entity_pool_or_subunit(
    sbgnml_entity_pool_or_subunit, layout, layout_element_cls
):
    sbgnml_label = getattr(sbgnml_entity_pool_or_subunit, "label", None)
    layout_element = layout.new_element(layout_element_cls)
    layout_element.id_ = sbgnml_entity_pool_or_subunit.get("id")
    set_layout_element_position_and_size_from_sbgnml_glyph(
        layout_element, sbgnml_entity_pool_or_subunit
    )
    if sbgnml_label is not None:
        text = sbgnml_label.get("text")
        if text is None:
            text = ""
        text_layout = momapy.core.layout.TextLayout(
            text=text,
            font_size=_DEFAULT_FONT_SIZE,
            font_family=_DEFAULT_FONT_FAMILY,
            fill=_DEFAULT_FONT_FILL,
            stroke=momapy.drawing.NoneValue,
            position=layout_element.label_center(),
            horizontal_alignment=momapy.core.elements.HAlignment.CENTER,
        )
        layout_element.label = text_layout
    return layout_element


def make_layout_activity(sbgnml_activity, layout, layout_element_cls):
    sbgnml_label = getattr(sbgnml_activity, "label", None)
    layout_element = layout.new_element(layout_element_cls)
    layout_element.id_ = sbgnml_activity.get("id")
    set_layout_element_position_and_size_from_sbgnml_glyph(
        layout_element, sbgnml_activity
    )
    if sbgnml_label is not None:
        text = sbgnml_label.get("text")
        if text is None:
            text = ""
        text_layout = momapy.core.layout.TextLayout(
            text=text,
            font_size=_DEFAULT_FONT_SIZE,
            font_family=_DEFAULT_FONT_FAMILY,
            fill=_DEFAULT_FONT_FILL,
            stroke=momapy.drawing.NoneValue,
            position=layout_element.label_center(),
            horizontal_alignment=momapy.core.elements.HAlignment.CENTER,
        )
        layout_element.label = text_layout
    return layout_element


def make_layout_state_variable(sbgnml_state_variable, layout, text):
    sbgnml_id = sbgnml_state_variable.get("id")
    layout_element = layout.new_element(momapy.sbgn.pd.StateVariableLayout)
    layout_element.id_ = sbgnml_id
    set_layout_element_position_and_size_from_sbgnml_glyph(
        layout_element, sbgnml_state_variable
    )
    text_layout = momapy.core.layout.TextLayout(
        text=text,
        font_size=_DEFAULT_AUXILIARY_UNIT_FONT_SIZE,
        font_family=_DEFAULT_FONT_FAMILY,
        fill=_DEFAULT_FONT_FILL,
        stroke=momapy.drawing.NoneValue,
        position=layout_element.label_center(),
        horizontal_alignment=momapy.core.elements.HAlignment.CENTER,
    )
    layout_element.label = text_layout
    layout_element = momapy.builder.object_from_builder(layout_element)
    return layout_element


def make_layout_unit_of_information(
    sbgnml_unit_of_information, layout, layout_element_cls
):
    sbgnml_label = getattr(sbgnml_unit_of_information, "label", None)
    sbgnml_id = sbgnml_unit_of_information.get("id")
    layout_element = layout.new_element(layout_element_cls)
    layout_element.id_ = sbgnml_id
    set_layout_element_position_and_size_from_sbgnml_glyph(
        layout_element, sbgnml_unit_of_information
    )
    if sbgnml_label is not None:
        text_layout = momapy.core.layout.TextLayout(
            text=sbgnml_label.get("text"),
            font_size=_DEFAULT_AUXILIARY_UNIT_FONT_SIZE,
            font_family=_DEFAULT_FONT_FAMILY,
            fill=_DEFAULT_FONT_FILL,
            stroke=momapy.drawing.NoneValue,
            position=layout_element.label_center(),
            horizontal_alignment=momapy.core.elements.HAlignment.CENTER,
        )
        layout_element.label = text_layout
    layout_element = momapy.builder.object_from_builder(layout_element)
    return layout_element


def make_layout_submap(sbgnml_submap, layout, layout_element_cls):
    sbgnml_label = getattr(sbgnml_submap, "label", None)
    sbgnml_id = sbgnml_submap.get("id")
    layout_element = layout.new_element(layout_element_cls)
    layout_element.id_ = sbgnml_id
    set_layout_element_position_and_size_from_sbgnml_glyph(
        layout_element, sbgnml_submap
    )
    if sbgnml_label is not None:
        text = sbgnml_label.get("text")
        if text is None:
            text = ""
        text_layout = momapy.core.layout.TextLayout(
            text=text,
            font_size=_DEFAULT_FONT_SIZE,
            font_family=_DEFAULT_FONT_FAMILY,
            fill=_DEFAULT_FONT_FILL,
            stroke=momapy.drawing.NoneValue,
            position=layout_element.center(),
            horizontal_alignment=momapy.core.elements.HAlignment.CENTER,
        )
        layout_element.label = text_layout
    return layout_element


def make_layout_terminal_or_tag(
    sbgnml_terminal_or_tag, layout, is_terminal
):
    sbgnml_id = sbgnml_terminal_or_tag.get("id")
    sbgnml_label = getattr(sbgnml_terminal_or_tag, "label", None)
    if is_terminal:
        layout_element_cls = momapy.sbgn.pd.TerminalLayout
    else:
        layout_element_cls = momapy.sbgn.pd.TagLayout
    layout_element = layout.new_element(layout_element_cls)
    layout_element.id_ = sbgnml_id
    set_layout_element_position_and_size_from_sbgnml_glyph(
        layout_element, sbgnml_terminal_or_tag
    )
    layout_element.direction = (
        momapy.sbgn.io.sbgnml._parsing.get_direction_from_sbgnml_element(
            sbgnml_terminal_or_tag
        )
    )
    if sbgnml_label is not None:
        text = sbgnml_label.get("text")
        if text is None:
            text = ""
        text_layout = momapy.core.layout.TextLayout(
            text=text,
            font_size=_DEFAULT_FONT_SIZE,
            font_family=_DEFAULT_FONT_FAMILY,
            fill=_DEFAULT_FONT_FILL,
            stroke=momapy.drawing.NoneValue,
            position=layout_element.label_center(),
            horizontal_alignment=momapy.core.elements.HAlignment.CENTER,
        )
        layout_element.label = text_layout
    return layout_element


def make_layout_reference(
    sbgnml_equivalence_arc, layout, sbgnml_id_to_layout_element
):
    sbgnml_id = sbgnml_equivalence_arc.get("id")
    # For terminals and tags, equivalence arc go from the referred node
    # to the terminal or tag. We invert the arc, so that the arc goes
    # from the reference to the referred node.
    sbgnml_target_id = sbgnml_equivalence_arc.get("source")
    layout_element = layout.new_element(
        momapy.sbgn.pd.EquivalenceArcLayout
    )
    layout_element.id_ = sbgnml_id
    sbgnml_points = (
        momapy.sbgn.io.sbgnml._parsing.get_sbgnml_points_from_sbgnml_arc(
            sbgnml_equivalence_arc
        )
    )
    points = momapy.sbgn.io.sbgnml._parsing.make_points_from_sbgnml_points(
        sbgnml_points
    )
    points.reverse()
    segments = momapy.sbgn.io.sbgnml._parsing.make_segments_from_points(
        points
    )
    for segment in segments:
        layout_element.segments.append(segment)
    target_layout_element = sbgnml_id_to_layout_element[sbgnml_target_id]
    layout_element.target = target_layout_element
    return layout_element


def make_layout_stoichiometric_process(
    sbgnml_process, layout, layout_element_cls, sbgnml_glyph_id_to_sbgnml_arcs
):
    sbgnml_id = sbgnml_process.get("id")
    layout_element = layout.new_element(layout_element_cls)
    layout_element.id_ = sbgnml_id
    set_layout_element_position_and_size_from_sbgnml_glyph(
        layout_element, sbgnml_process
    )
    layout_element.direction = (
        momapy.sbgn.io.sbgnml._parsing.get_sbgnml_process_direction(
            sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
        )
    )
    layout_element.left_to_right = (
        momapy.sbgn.io.sbgnml._parsing.is_sbgnml_process_left_to_right(
            sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
        )
    )
    # We set the length of the connectors using the ports
    left_connector_length, right_connector_length = (
        momapy.sbgn.io.sbgnml._parsing.get_connectors_length_from_sbgnml_process(
            sbgnml_process
        )
    )
    if left_connector_length is not None:
        layout_element.left_connector_length = left_connector_length
    if right_connector_length is not None:
        layout_element.right_connector_length = right_connector_length
    return layout_element


def make_layout_reactant(
    sbgnml_consumption_arc, layout, sbgnml_id_to_layout_element
):
    sbgnml_source_id = sbgnml_consumption_arc.get("source")
    sbgnml_stoichiometry = (
        momapy.sbgn.io.sbgnml._parsing.get_stoichiometry_from_sbgnml_element(
            sbgnml_consumption_arc
        )
    )
    layout_element = layout.new_element(momapy.sbgn.pd.ConsumptionLayout)
    sbgnml_points = (
        momapy.sbgn.io.sbgnml._parsing.get_sbgnml_points_from_sbgnml_arc(
            sbgnml_consumption_arc
        )
    )
    # The source becomes the target: in momapy flux arcs go from the process
    # to the entity pool node; this way reversible consumptions can be
    # represented with production layouts. Also, no source
    # (the process layout) is set for the flux arc, so that we do not have a
    # circular definition that would be problematic when building the
    # object.
    sbgnml_points.reverse()
    points = momapy.sbgn.io.sbgnml._parsing.make_points_from_sbgnml_points(
        sbgnml_points
    )
    segments = momapy.sbgn.io.sbgnml._parsing.make_segments_from_points(
        points
    )
    for segment in segments:
        layout_element.segments.append(segment)
    source_layout_element = sbgnml_id_to_layout_element[sbgnml_source_id]
    layout_element.target = source_layout_element
    if sbgnml_stoichiometry is not None:
        stoichiometry_layout_element = layout.new_element(
            momapy.sbgn.pd.CardinalityLayout
        )
        set_layout_element_position_and_size_from_sbgnml_glyph(
            stoichiometry_layout_element, sbgnml_stoichiometry
        )
        sbgnml_label = getattr(sbgnml_stoichiometry, "label", None)
        if sbgnml_label is not None:
            text = sbgnml_label.get("text")
            if text is None:
                text = ""
            text_layout = momapy.core.layout.TextLayout(
                text=text,
                font_size=_DEFAULT_FONT_SIZE,
                font_family=_DEFAULT_FONT_FAMILY,
                fill=_DEFAULT_FONT_FILL,
                stroke=momapy.drawing.NoneValue,
                position=stoichiometry_layout_element.position,
                horizontal_alignment=momapy.core.elements.HAlignment.CENTER,
            )
            stoichiometry_layout_element.label = text_layout
            layout_element.layout_elements.append(
                stoichiometry_layout_element
            )
    layout_element = momapy.builder.object_from_builder(layout_element)
    return layout_element


def make_layout_product(
    sbgnml_production_arc, layout, sbgnml_id_to_layout_element
):
    sbgnml_target_id = sbgnml_production_arc.get("target")
    sbgnml_stoichiometry = (
        momapy.sbgn.io.sbgnml._parsing.get_stoichiometry_from_sbgnml_element(
            sbgnml_production_arc
        )
    )
    layout_element = layout.new_element(momapy.sbgn.pd.ProductionLayout)
    sbgnml_points = (
        momapy.sbgn.io.sbgnml._parsing.get_sbgnml_points_from_sbgnml_arc(
            sbgnml_production_arc
        )
    )
    # No source (the process layout) is set for the flux arc,
    # so that we do not have a circular definition that would be
    # problematic when building the object.
    points = momapy.sbgn.io.sbgnml._parsing.make_points_from_sbgnml_points(
        sbgnml_points
    )
    segments = momapy.sbgn.io.sbgnml._parsing.make_segments_from_points(
        points
    )
    for segment in segments:
        layout_element.segments.append(segment)
    target_layout_element = sbgnml_id_to_layout_element[sbgnml_target_id]
    layout_element.target = target_layout_element
    if sbgnml_stoichiometry is not None:
        stoichiometry_layout_element = layout.new_element(
            momapy.sbgn.pd.CardinalityLayout
        )
        set_layout_element_position_and_size_from_sbgnml_glyph(
            stoichiometry_layout_element, sbgnml_stoichiometry
        )
        sbgnml_label = getattr(sbgnml_stoichiometry, "label", None)
        if sbgnml_label is not None:
            text = sbgnml_label.get("text")
            if text is None:
                text = ""
            text_layout = momapy.core.layout.TextLayout(
                text=text,
                font_size=_DEFAULT_FONT_SIZE,
                font_family=_DEFAULT_FONT_FAMILY,
                fill=_DEFAULT_FONT_FILL,
                stroke=momapy.drawing.NoneValue,
                position=stoichiometry_layout_element.position,
                horizontal_alignment=momapy.core.elements.HAlignment.CENTER,
            )
            stoichiometry_layout_element.label = text_layout
            layout_element.layout_elements.append(
                stoichiometry_layout_element
            )
    layout_element = momapy.builder.object_from_builder(layout_element)
    return layout_element


def make_layout_logical_operator(
    sbgnml_logical_operator,
    layout,
    layout_element_cls,
    sbgnml_id_to_sbgnml_element,
    sbgnml_glyph_id_to_sbgnml_arcs,
):
    sbgnml_id = sbgnml_logical_operator.get("id")
    layout_element = layout.new_element(layout_element_cls)
    layout_element.id_ = sbgnml_id
    set_layout_element_position_and_size_from_sbgnml_glyph(
        layout_element, sbgnml_logical_operator
    )
    layout_element.direction = (
        momapy.sbgn.io.sbgnml._parsing.get_sbgnml_process_direction(
            sbgnml_logical_operator, sbgnml_glyph_id_to_sbgnml_arcs
        )
    )
    layout_element.left_to_right = (
        momapy.sbgn.io.sbgnml._parsing.is_sbgnml_operator_left_to_right(
            sbgnml_operator=sbgnml_logical_operator,
            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
        )
    )
    # We set the length of the connectors using the ports
    left_connector_length, right_connector_length = (
        momapy.sbgn.io.sbgnml._parsing.get_connectors_length_from_sbgnml_process(
            sbgnml_logical_operator
        )
    )
    if left_connector_length is not None:
        layout_element.left_connector_length = left_connector_length
    if right_connector_length is not None:
        layout_element.right_connector_length = right_connector_length
    return layout_element


def make_layout_logical_operator_input(
    sbgnml_logic_arc, layout, source_layout_element
):
    layout_element = layout.new_element(momapy.sbgn.pd.LogicArcLayout)
    sbgnml_points = (
        momapy.sbgn.io.sbgnml._parsing.get_sbgnml_points_from_sbgnml_arc(
            sbgnml_logic_arc
        )
    )
    # The source becomes the target: in momapy logic arcs go from
    # the operator to the input node. Also, no source
    # (the logical operator layout) is set for the logic arc, so
    # that we do not have a circular definition that would be
    # problematic when building the object.
    sbgnml_points.reverse()
    points = momapy.sbgn.io.sbgnml._parsing.make_points_from_sbgnml_points(
        sbgnml_points
    )
    segments = momapy.sbgn.io.sbgnml._parsing.make_segments_from_points(
        points
    )
    for segment in segments:
        layout_element.segments.append(segment)
    layout_element.target = source_layout_element
    layout_element = momapy.builder.object_from_builder(layout_element)
    return layout_element


def make_layout_modulation(
    sbgnml_modulation,
    layout,
    layout_element_cls,
    source_layout_element,
    target_layout_element,
):
    layout_element = layout.new_element(layout_element_cls)
    sbgnml_points = (
        momapy.sbgn.io.sbgnml._parsing.get_sbgnml_points_from_sbgnml_arc(
            sbgnml_modulation
        )
    )
    points = momapy.sbgn.io.sbgnml._parsing.make_points_from_sbgnml_points(
        sbgnml_points
    )
    segments = momapy.sbgn.io.sbgnml._parsing.make_segments_from_points(
        points
    )
    for segment in segments:
        layout_element.segments.append(segment)
    layout_element.source = source_layout_element
    layout_element.target = target_layout_element
    layout_element = momapy.builder.object_from_builder(layout_element)
    return layout_element
