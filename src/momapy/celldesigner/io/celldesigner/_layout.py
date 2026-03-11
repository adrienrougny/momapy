"""CellDesigner layout-building helpers and constants.

Functions and constants for constructing momapy layout objects from
CellDesigner XML data.
"""

import math
import lxml

import momapy.builder
import momapy.drawing
import momapy.geometry
import momapy.coloring
import momapy.core.layout
import momapy.celldesigner.core
import momapy.celldesigner.io.celldesigner._parsing

_DEFAULT_FONT_FAMILY = momapy.drawing.DEFAULT_FONT_FAMILY
_DEFAULT_FONT_SIZE = 12.0
_DEFAULT_MODIFICATION_FONT_SIZE = 9.0
_DEFAULT_FONT_FILL = momapy.coloring.black

_LAYOUT_TO_ACTIVE_LAYOUT = {
    momapy.celldesigner.core.GenericProteinLayout: momapy.celldesigner.core.GenericProteinActiveLayout,
    momapy.celldesigner.core.IonChannelLayout: momapy.celldesigner.core.IonChannelActiveLayout,
    momapy.celldesigner.core.ComplexLayout: momapy.celldesigner.core.ComplexActiveLayout,
    momapy.celldesigner.core.SimpleMoleculeLayout: momapy.celldesigner.core.SimpleMoleculeActiveLayout,
    momapy.celldesigner.core.IonLayout: momapy.celldesigner.core.IonActiveLayout,
    momapy.celldesigner.core.UnknownLayout: momapy.celldesigner.core.UnknownActiveLayout,
    momapy.celldesigner.core.DegradedLayout: momapy.celldesigner.core.DegradedActiveLayout,
    momapy.celldesigner.core.GeneLayout: momapy.celldesigner.core.GeneActiveLayout,
    momapy.celldesigner.core.PhenotypeLayout: momapy.celldesigner.core.PhenotypeActiveLayout,
    momapy.celldesigner.core.RNALayout: momapy.celldesigner.core.RNAActiveLayout,
    momapy.celldesigner.core.AntisenseRNALayout: momapy.celldesigner.core.AntisenseRNAActiveLayout,
    momapy.celldesigner.core.TruncatedProteinLayout: momapy.celldesigner.core.TruncatedProteinActiveLayout,
    momapy.celldesigner.core.ReceptorLayout: momapy.celldesigner.core.ReceptorActiveLayout,
    momapy.celldesigner.core.DrugLayout: momapy.celldesigner.core.DrugActiveLayout,
}


def make_empty_layout(cd_element):
    layout = momapy.celldesigner.core.CellDesignerLayoutBuilder()
    return layout


def set_layout_size_and_position(cd_model, layout):
    layout.width = float(
        momapy.celldesigner.io.celldesigner._parsing.get_width(cd_model)
    )
    layout.height = float(
        momapy.celldesigner.io.celldesigner._parsing.get_height(cd_model)
    )
    layout.position = momapy.geometry.Point(layout.width / 2, layout.height / 2)


def make_segments(points):
    segments = []
    for current_point, following_point in zip(points[:-1], points[1:]):
        segment = momapy.geometry.Segment(current_point, following_point)
        segments.append(segment)
    return segments


def make_points(cd_edit_points):
    if getattr(cd_edit_points, "text", None) is not None:
        cd_edit_points = cd_edit_points.text
    cd_coordinates = [
        cd_edit_point.split(",") for cd_edit_point in cd_edit_points.split(" ")
    ]
    points = [
        momapy.geometry.Point(float(cd_coordinate[0]), float(cd_coordinate[1]))
        for cd_coordinate in cd_coordinates
    ]
    return points


def make_species(
    cd_species_alias, layout, layout_element_cls, name, homomultimer, active
):
    layout_element = layout.new_element(layout_element_cls)
    layout_element.id_ = cd_species_alias.get("id")
    cd_x, cd_y, cd_w, cd_h = momapy.celldesigner.io.celldesigner._parsing.get_bounds(
        cd_species_alias
    )
    layout_element.position = momapy.geometry.Point(
        float(cd_x) + float(cd_w) / 2,
        float(cd_y) + float(cd_h) / 2,
    )
    layout_element.width = float(cd_w)
    layout_element.height = float(cd_h)
    text_layout = momapy.core.layout.TextLayout(
        text=name,
        font_size=float(cd_species_alias.font.get("size")),
        font_family=_DEFAULT_FONT_FAMILY,
        fill=_DEFAULT_FONT_FILL,
        stroke=momapy.drawing.NoneValue,
        position=layout_element.label_center(),
    )
    text_layout = momapy.builder.object_from_builder(text_layout)
    layout_element.label = text_layout
    layout_element.stroke_width = float(
        cd_species_alias.usualView.singleLine.get("width")
    )
    cd_species_alias_fill_color = cd_species_alias.usualView.paint.get("color")
    cd_species_alias_fill_color = (
        cd_species_alias_fill_color[2:] + cd_species_alias_fill_color[:2]
    )
    layout_element.fill = momapy.coloring.Color.from_hexa(cd_species_alias_fill_color)
    layout_element.n = homomultimer
    if active:
        active_cls = _LAYOUT_TO_ACTIVE_LAYOUT[layout_element_cls]
        active_element = layout.new_element(active_cls)
        active_element.position = layout_element.position
        active_element.width = (
            layout_element.width + momapy.celldesigner.core._ACTIVE_XSEP * 2
        )
        active_element.height = (
            layout_element.height + momapy.celldesigner.core._ACTIVE_YSEP * 2
        )
        active_element.n = homomultimer
        active_element = momapy.builder.object_from_builder(active_element)
        layout_element.layout_elements.append(active_element)
    return layout_element


def make_species_modification(
    cd_modification_residue,
    layout,
    modification_state,
    super_layout_element,
):
    layout_element = layout.new_element(momapy.celldesigner.core.ModificationLayout)
    angle = cd_modification_residue.get("angle")
    if angle is None:
        fraction = float(cd_modification_residue.get("pos"))
        segment = momapy.geometry.Segment(
            super_layout_element.north_west(),
            super_layout_element.north_east(),
        )
        point = segment.get_position_at_fraction(fraction)
        segment = momapy.geometry.Segment(super_layout_element.center(), point)
        angle = -segment.get_angle_to_horizontal()
    else:
        angle = float(angle)
        point = momapy.geometry.Point(
            super_layout_element.width * math.cos(angle),
            super_layout_element.height * math.sin(angle),
        )
        angle = math.atan2(point.y, point.x)
    position = super_layout_element.own_angle(angle, unit="radians")
    if position is None:
        position = super_layout_element.center()
    layout_element.position = position
    text = modification_state.value if modification_state is not None else ""
    text_layout = momapy.core.layout.TextLayout(
        text=text,
        font_size=_DEFAULT_MODIFICATION_FONT_SIZE,
        font_family=_DEFAULT_FONT_FAMILY,
        fill=_DEFAULT_FONT_FILL,
        stroke=momapy.drawing.NoneValue,
        position=layout_element.label_center(),
    )
    layout_element.label = text_layout
    cd_modification_residue_name = cd_modification_residue.get("name")
    if cd_modification_residue_name is not None:
        residue_text_layout = layout.new_element(momapy.core.layout.TextLayout)
        residue_text_layout.text = cd_modification_residue_name
        residue_text_layout.font_size = _DEFAULT_MODIFICATION_FONT_SIZE
        residue_text_layout.font_family = _DEFAULT_FONT_FAMILY
        residue_text_layout.fill = _DEFAULT_FONT_FILL
        residue_text_layout.stroke = momapy.drawing.NoneValue
        segment = momapy.geometry.Segment(
            layout_element.center(), super_layout_element.center()
        )
        fraction = (
            layout_element.height + _DEFAULT_MODIFICATION_FONT_SIZE
        ) / segment.length()
        residue_text_layout.position = segment.get_position_at_fraction(fraction)
        residue_text_layout = momapy.builder.object_from_builder(residue_text_layout)
        layout_element.layout_elements.append(residue_text_layout)
    return layout_element


def make_species_structural_state(
    cd_species_structural_state, layout, super_layout_element
):
    layout_element = layout.new_element(momapy.celldesigner.core.StructuralStateLayout)
    layout_element.position = super_layout_element.own_angle(90)
    text = cd_species_structural_state.get("structuralState")
    text_layout = momapy.core.layout.TextLayout(
        text=text,
        font_size=_DEFAULT_MODIFICATION_FONT_SIZE,
        font_family=_DEFAULT_FONT_FAMILY,
        fill=_DEFAULT_FONT_FILL,
        stroke=momapy.drawing.NoneValue,
        position=layout_element.position,
    )
    layout_element.label = text_layout
    bbox = text_layout.bbox()
    layout_element.width = 1.5 * bbox.width
    layout_element.height = 1.5 * bbox.height
    return layout_element


def make_compartment_from_alias(cd_compartment, cd_compartment_alias, layout):
    if getattr(cd_compartment_alias, "class").text == "OVAL":
        layout_element_cls = momapy.celldesigner.core.OvalCompartmentLayout
    else:
        layout_element_cls = momapy.celldesigner.core.RectangleCompartmentLayout
    layout_element = layout.new_element(layout_element_cls)
    layout_element.id_ = cd_compartment_alias.get("id")
    cd_x = float(cd_compartment_alias.bounds.get("x"))
    cd_y = float(cd_compartment_alias.bounds.get("y"))
    cd_w = float(cd_compartment_alias.bounds.get("w"))
    cd_h = float(cd_compartment_alias.bounds.get("h"))
    layout_element.position = momapy.geometry.Point(cd_x + cd_w / 2, cd_y + cd_h / 2)
    layout_element.width = cd_w
    layout_element.height = cd_h
    layout_element.inner_stroke_width = float(
        cd_compartment_alias.doubleLine.get("innerWidth")
    )
    layout_element.stroke_width = float(
        cd_compartment_alias.doubleLine.get("outerWidth")
    )
    layout_element.sep = float(cd_compartment_alias.doubleLine.get("thickness"))
    cd_compartment_alias_color = cd_compartment_alias.paint.get("color")
    cd_compartment_alias_color = (
        cd_compartment_alias_color[2:] + cd_compartment_alias_color[:2]
    )
    element_color = momapy.coloring.Color.from_hexa(cd_compartment_alias_color)
    layout_element.stroke = element_color
    layout_element.inner_stroke = element_color
    layout_element.fill = element_color.with_alpha(0.5)
    layout_element.inner_fill = momapy.coloring.white
    text = momapy.celldesigner.io.celldesigner._parsing.make_name(
        cd_compartment.get("name")
    )
    text_position = momapy.geometry.Point(
        float(cd_compartment_alias.namePoint.get("x")),
        float(cd_compartment_alias.namePoint.get("y")),
    )
    text_layout = momapy.core.layout.TextLayout(
        text=text,
        font_size=_DEFAULT_FONT_SIZE,
        font_family=_DEFAULT_FONT_FAMILY,
        fill=_DEFAULT_FONT_FILL,
        stroke=momapy.drawing.NoneValue,
        position=text_position,
    )
    layout_element.label = text_layout
    return layout_element


def make_segments_non_t_shape(cd_reaction, cd_id_to_layout_element):
    cd_base_reactants = momapy.celldesigner.io.celldesigner._parsing.get_base_reactants(
        cd_reaction
    )
    cd_base_products = momapy.celldesigner.io.celldesigner._parsing.get_base_products(
        cd_reaction
    )
    cd_base_reactant = cd_base_reactants[0]
    cd_base_product = cd_base_products[0]
    reactant_layout_element = cd_id_to_layout_element[cd_base_reactant.get("alias")]
    product_layout_element = cd_id_to_layout_element[cd_base_product.get("alias")]
    reactant_anchor_name = (
        momapy.celldesigner.io.celldesigner._parsing.get_anchor_name_for_frame(
            cd_base_reactant
        )
    )
    product_anchor_name = (
        momapy.celldesigner.io.celldesigner._parsing.get_anchor_name_for_frame(
            cd_base_product
        )
    )
    origin = reactant_layout_element.anchor_point(reactant_anchor_name)
    unit_x = product_layout_element.anchor_point(product_anchor_name)
    unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    intermediate_points = []
    cd_edit_points = (
        momapy.celldesigner.io.celldesigner._parsing.get_edit_points_from_reaction(
            cd_reaction
        )
    )
    if cd_edit_points is None:
        edit_points = []
    else:
        edit_points = make_points(cd_edit_points)
    intermediate_points = [
        edit_point.transformed(transformation) for edit_point in edit_points
    ]
    if reactant_anchor_name == "center":
        if intermediate_points:
            reference_point = intermediate_points[0]
        else:
            reference_point = product_layout_element.anchor_point(product_anchor_name)
        start_point = reactant_layout_element.own_border(reference_point)
    else:
        start_point = reactant_layout_element.anchor_point(reactant_anchor_name)
    if product_anchor_name == "center":
        if intermediate_points:
            reference_point = intermediate_points[-1]
        else:
            reference_point = reactant_layout_element.anchor_point(reactant_anchor_name)
        end_point = product_layout_element.own_border(reference_point)
    else:
        end_point = product_layout_element.anchor_point(product_anchor_name)
    points = [start_point] + intermediate_points + [end_point]
    return make_segments(points)


def make_segments_left_t_shape(cd_reaction, cd_id_to_layout_element):
    cd_base_reactants = momapy.celldesigner.io.celldesigner._parsing.get_base_reactants(
        cd_reaction
    )
    cd_base_products = momapy.celldesigner.io.celldesigner._parsing.get_base_products(
        cd_reaction
    )
    cd_base_reactant_0 = cd_base_reactants[0]
    cd_base_reactant_1 = cd_base_reactants[1]
    cd_base_product = cd_base_products[0]
    reactant_layout_element_0 = cd_id_to_layout_element[cd_base_reactant_0.get("alias")]
    reactant_layout_element_1 = cd_id_to_layout_element[cd_base_reactant_1.get("alias")]
    product_layout_element = cd_id_to_layout_element[cd_base_product.get("alias")]
    product_anchor_name = (
        momapy.celldesigner.io.celldesigner._parsing.get_anchor_name_for_frame(
            cd_base_product
        )
    )
    origin = reactant_layout_element_0.center()
    unit_x = reactant_layout_element_1.center()
    unit_y = product_layout_element.center()
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    cd_edit_points = (
        momapy.celldesigner.io.celldesigner._parsing.get_edit_points_from_reaction(
            cd_reaction
        )
    )
    edit_points = make_points(cd_edit_points)
    start_point = edit_points[-1].transformed(transformation)
    origin = start_point
    unit_x = product_layout_element.anchor_point(product_anchor_name)
    unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    intermediate_points = []
    start_index = int(cd_edit_points.get("num0")) + int(cd_edit_points.get("num1"))
    for edit_point in edit_points[start_index:-1]:
        intermediate_point = edit_point.transformed(transformation)
        intermediate_points.append(intermediate_point)
    if getattr(cd_base_product, "linkAnchor", None) is not None:
        end_point = product_layout_element.anchor_point(
            momapy.celldesigner.io.celldesigner._parsing.get_anchor_name_for_frame(
                cd_base_product
            )
        )
    else:
        if intermediate_points:
            reference_point = intermediate_points[-1]
        else:
            reference_point = start_point
        end_point = product_layout_element.own_border(reference_point)
    points = [start_point] + intermediate_points + [end_point]
    return make_segments(points)


def make_segments_right_t_shape(cd_reaction, cd_id_to_layout_element):
    cd_base_reactants = momapy.celldesigner.io.celldesigner._parsing.get_base_reactants(
        cd_reaction
    )
    cd_base_products = momapy.celldesigner.io.celldesigner._parsing.get_base_products(
        cd_reaction
    )
    cd_base_product_0 = cd_base_products[0]
    cd_base_product_1 = cd_base_products[1]
    cd_base_reactant = cd_base_reactants[0]
    product_layout_element_0 = cd_id_to_layout_element[cd_base_product_0.get("alias")]
    product_layout_element_1 = cd_id_to_layout_element[cd_base_product_1.get("alias")]
    reactant_layout_element = cd_id_to_layout_element[cd_base_reactant.get("alias")]
    reactant_anchor_name = (
        momapy.celldesigner.io.celldesigner._parsing.get_anchor_name_for_frame(
            cd_base_reactant
        )
    )
    origin = reactant_layout_element.center()
    unit_x = product_layout_element_0.center()
    unit_y = product_layout_element_1.center()
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    cd_edit_points = (
        momapy.celldesigner.io.celldesigner._parsing.get_edit_points_from_reaction(
            cd_reaction
        )
    )
    edit_points = make_points(cd_edit_points)
    end_point = edit_points[-1].transformed(transformation)
    origin = end_point
    unit_x = reactant_layout_element.anchor_point(reactant_anchor_name)
    unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    intermediate_points = []
    end_index = int(cd_edit_points.get("num0"))
    edit_points = list(reversed(edit_points[:end_index]))
    for edit_point in edit_points:
        intermediate_point = edit_point.transformed(transformation)
        intermediate_points.append(intermediate_point)
    if getattr(cd_base_reactant, "linkAnchor", None) is not None:
        start_point = reactant_layout_element.anchor_point(
            momapy.celldesigner.io.celldesigner._parsing.get_anchor_name_for_frame(
                cd_base_reactant
            )
        )
    else:
        if intermediate_points:
            reference_point = intermediate_points[0]
        else:
            reference_point = end_point
        start_point = reactant_layout_element.own_border(reference_point)
    points = [start_point] + intermediate_points + [end_point]
    return make_segments(points)


def make_reaction(
    cd_reaction,
    layout,
    layout_element_cls,
    cd_base_reactants,
    cd_base_products,
    cd_id_to_layout_element,
):
    layout_element = layout.new_element(layout_element_cls)
    layout_element.id_ = cd_reaction.get("id")
    layout_element.reversible = cd_reaction.get("reversible") == "true"
    if not layout_element.reversible:
        layout_element.start_shorten = 0.0
    if len(cd_base_reactants) == 1 and len(cd_base_products) == 1:
        segments = make_segments_non_t_shape(cd_reaction, cd_id_to_layout_element)
        reaction_node_segment = int(
            momapy.celldesigner.io.celldesigner._parsing.get_rectangle_index(
                cd_reaction
            )
        )
        make_base_reactant_layouts = False
        make_base_product_layouts = False
    elif len(cd_base_reactants) > 1 and len(cd_base_products) == 1:
        segments = make_segments_left_t_shape(cd_reaction, cd_id_to_layout_element)
        reaction_node_segment = int(
            momapy.celldesigner.io.celldesigner._parsing.get_t_shape_index(cd_reaction)
        )
        make_base_reactant_layouts = True
        make_base_product_layouts = False
    elif len(cd_base_reactants) == 1 and len(cd_base_products) > 1:
        segments = make_segments_right_t_shape(cd_reaction, cd_id_to_layout_element)
        reaction_node_segment = (
            len(segments)
            - 1
            - int(
                momapy.celldesigner.io.celldesigner._parsing.get_t_shape_index(
                    cd_reaction
                )
            )
        )
        make_base_reactant_layouts = False
        make_base_product_layouts = True
    for segment in segments:
        layout_element.segments.append(segment)
    layout_element.reaction_node_segment = reaction_node_segment
    return layout_element, make_base_reactant_layouts, make_base_product_layouts


def make_reactant_from_base(
    cd_base_reactant,
    n_cd_base_reactant,
    cd_reaction,
    layout,
    cd_id_to_layout_element,
    super_layout_element,
):
    layout_element = layout.new_element(momapy.celldesigner.core.ConsumptionLayout)
    cd_edit_points = (
        momapy.celldesigner.io.celldesigner._parsing.get_edit_points_from_reaction(
            cd_reaction
        )
    )
    cd_num_0 = cd_edit_points.get("num0")
    cd_num_1 = cd_edit_points.get("num1")
    if n_cd_base_reactant == 0:
        start_index = n_cd_base_reactant
        stop_index = int(cd_num_0)
    elif n_cd_base_reactant == 1:
        start_index = int(cd_num_0)
        stop_index = int(cd_num_0) + int(cd_num_1)
    species_layout_element = cd_id_to_layout_element[cd_base_reactant.get("alias")]
    reactant_anchor_name = (
        momapy.celldesigner.io.celldesigner._parsing.get_anchor_name_for_frame(
            cd_base_reactant
        )
    )
    origin = super_layout_element.points()[0]
    unit_x = species_layout_element.anchor_point(reactant_anchor_name)
    unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    intermediate_points = []
    edit_points = make_points(cd_edit_points)
    for edit_point in edit_points[start_index:stop_index]:
        intermediate_point = edit_point.transformed(transformation)
        intermediate_points.append(intermediate_point)
    intermediate_points.reverse()
    if reactant_anchor_name == "center":
        if intermediate_points:
            reference_point = intermediate_points[0]
        else:
            reference_point = super_layout_element.start_point()
        start_point = species_layout_element.own_border(reference_point)
    else:
        start_point = species_layout_element.anchor_point(reactant_anchor_name)
    if intermediate_points:
        reference_point = intermediate_points[-1]
    else:
        reference_point = start_point
    end_point = super_layout_element.start_arrowhead_border(reference_point)
    points = [start_point] + intermediate_points + [end_point]
    segments = make_segments(points)
    for segment in segments:
        layout_element.segments.append(segment)
    return layout_element


def make_reactant_from_link(
    cd_reactant_link, layout, cd_id_to_layout_element, super_layout_element
):
    layout_element = layout.new_element(momapy.celldesigner.core.ConsumptionLayout)
    species_layout_element = cd_id_to_layout_element[cd_reactant_link.get("alias")]
    reactant_anchor_name = (
        momapy.celldesigner.io.celldesigner._parsing.get_anchor_name_for_frame(
            cd_reactant_link
        )
    )
    origin = species_layout_element.center()
    unit_x = super_layout_element.left_connector_tip()
    unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    cd_edit_points = momapy.celldesigner.io.celldesigner._parsing.get_edit_points_from_participant_link(
        cd_reactant_link
    )
    if cd_edit_points is None:
        edit_points = []
    else:
        edit_points = make_points(cd_edit_points)
    intermediate_points = [
        edit_point.transformed(transformation) for edit_point in edit_points
    ]
    end_point = unit_x
    if reactant_anchor_name == "center":
        if intermediate_points:
            reference_point = intermediate_points[0]
        else:
            reference_point = end_point
        start_point = species_layout_element.own_border(reference_point)
    else:
        start_point = species_layout_element.anchor_point(reactant_anchor_name)
    points = [start_point] + intermediate_points + [end_point]
    segments = make_segments(points)
    for segment in segments:
        layout_element.segments.append(segment)
    return layout_element


def make_product_from_base(
    cd_base_product,
    n_cd_base_product,
    cd_reaction,
    layout,
    cd_id_to_layout_element,
    super_layout_element,
):
    layout_element = layout.new_element(momapy.celldesigner.core.ProductionLayout)
    cd_edit_points = (
        momapy.celldesigner.io.celldesigner._parsing.get_edit_points_from_reaction(
            cd_reaction
        )
    )
    cd_num_0 = cd_edit_points.get("num0")
    cd_num_1 = cd_edit_points.get("num1")
    cd_num_2 = cd_edit_points.get("num2")
    if n_cd_base_product == 0:
        start_index = int(cd_num_0)
        stop_index = int(cd_num_0) + int(cd_num_1)
    elif n_cd_base_product == 1:
        start_index = int(cd_num_0) + int(cd_num_1)
        stop_index = int(cd_num_0) + int(cd_num_1) + int(cd_num_2)
    product_layout_element = cd_id_to_layout_element[cd_base_product.get("alias")]
    product_anchor_name = (
        momapy.celldesigner.io.celldesigner._parsing.get_anchor_name_for_frame(
            cd_base_product
        )
    )
    origin = super_layout_element.end_point()
    unit_x = product_layout_element.anchor_point(product_anchor_name)
    unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    intermediate_points = []
    edit_points = make_points(cd_edit_points)
    for edit_point in edit_points[start_index:stop_index]:
        intermediate_point = edit_point.transformed(transformation)
        intermediate_points.append(intermediate_point)
    if product_anchor_name == "center":
        if intermediate_points:
            reference_point = intermediate_points[-1]
        else:
            reference_point = super_layout_element.end_point()
        end_point = product_layout_element.own_border(reference_point)
    else:
        end_point = product_layout_element.anchor_point(product_anchor_name)
    if intermediate_points:
        reference_point = intermediate_points[0]
    else:
        reference_point = end_point
    start_point = super_layout_element.end_arrowhead_border(reference_point)
    points = [start_point] + intermediate_points + [end_point]
    segments = make_segments(points)
    for segment in segments:
        layout_element.segments.append(segment)
    return layout_element


def make_product_from_link(
    cd_product_link, layout, cd_id_to_layout_element, super_layout_element
):
    layout_element = layout.new_element(momapy.celldesigner.core.ProductionLayout)
    species_layout_element = cd_id_to_layout_element[cd_product_link.get("alias")]
    product_anchor_name = (
        momapy.celldesigner.io.celldesigner._parsing.get_anchor_name_for_frame(
            cd_product_link
        )
    )
    origin = super_layout_element.right_connector_tip()
    unit_x = species_layout_element.center()
    unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    cd_edit_points = momapy.celldesigner.io.celldesigner._parsing.get_edit_points_from_participant_link(
        cd_product_link
    )
    if cd_edit_points is None:
        edit_points = []
    else:
        edit_points = make_points(cd_edit_points)
    intermediate_points = [
        edit_point.transformed(transformation) for edit_point in edit_points
    ]
    intermediate_points.reverse()
    start_point = origin
    if product_anchor_name == "center":
        if intermediate_points:
            reference_point = intermediate_points[-1]
        else:
            reference_point = start_point
        end_point = species_layout_element.own_border(reference_point)
    else:
        end_point = species_layout_element.anchor_point(product_anchor_name)
    points = [start_point] + intermediate_points + [end_point]
    segments = make_segments(points)
    for segment in segments:
        layout_element.segments.append(segment)
    return layout_element


def make_modifier(
    cd_reaction_modification,
    layout,
    layout_element_cls,
    source_layout_element,
    super_layout_element,
    has_boolean_input,
):
    layout_element = layout.new_element(layout_element_cls)
    cd_edit_points = cd_reaction_modification.get("editPoints")
    if cd_edit_points is not None:
        edit_points = make_points(cd_edit_points)
    else:
        edit_points = []
    if not has_boolean_input:
        cd_link_target = getattr(cd_reaction_modification, "linkTarget", None)
        if cd_link_target is not None:
            cd_link_anchor = getattr(cd_link_target, "linkAnchor", None)
            if cd_link_anchor is not None:
                source_anchor_name = momapy.celldesigner.io.celldesigner._parsing.get_anchor_name_for_frame(
                    cd_link_target
                )
            else:
                source_anchor_name = "center"
        else:
            source_anchor_name = "center"
    else:
        source_anchor_name = "center"
        edit_points = edit_points[1:-1]  # first point is origin marker (0,0), last point is the position of the logic gate
    origin = source_layout_element.anchor_point(source_anchor_name)
    unit_x = super_layout_element._get_reaction_node_position()
    unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    intermediate_points = [
        edit_point.transformed(transformation) for edit_point in edit_points
    ]
    if source_anchor_name == "center":
        if intermediate_points:
            reference_point = intermediate_points[0]
        else:
            reference_point = unit_x
        start_point = source_layout_element.own_border(reference_point)
    else:
        start_point = origin
    if intermediate_points:
        reference_point = intermediate_points[-1]
    else:
        reference_point = start_point
    end_point = super_layout_element.reaction_node_border(reference_point)
    points = [start_point] + intermediate_points + [end_point]
    segments = make_segments(points)
    for segment in segments:
        layout_element.segments.append(segment)
    layout_element.source = source_layout_element
    return layout_element


def make_logic_gate(cd_element, layout, layout_element_cls, cd_id_to_layout_element):
    layout_element = layout.new_element(layout_element_cls)
    cd_edit_points = cd_element.get("editPoints")
    edit_points = make_points(cd_edit_points)
    position = edit_points[-1]
    layout_element.position = position
    cd_modifiers = cd_element.get("aliases")
    layout_input_elements = [
        cd_id_to_layout_element[cd_input_id] for cd_input_id in cd_modifiers.split(",")
    ]
    for layout_input_element in layout_input_elements:
        layout_logic_arc = layout.new_element(momapy.celldesigner.core.LogicArcLayout)
        start_point = layout_input_element.own_border(position)
        end_point = layout_element.own_border(start_point)
        segment = momapy.geometry.Segment(start_point, end_point)
        layout_logic_arc.segments.append(segment)
        layout_logic_arc.target = layout_input_element
        layout_logic_arc = momapy.builder.object_from_builder(layout_logic_arc)
        layout_element.layout_elements.append(layout_logic_arc)
    return layout_element


def make_modulation(
    cd_reaction,
    layout,
    layout_element_cls,
    source_layout_element,
    target_layout_element,
    has_boolean_input,
    cd_base_reactant,
    cd_base_product,
):
    cd_edit_points = (
        momapy.celldesigner.io.celldesigner._parsing.get_edit_points_from_reaction(
            cd_reaction
        )
    )
    if cd_edit_points is not None:
        edit_points = make_points(cd_edit_points)
    else:
        edit_points = []
    if has_boolean_input:
        source_anchor_name = "center"
        edit_points = edit_points[:-1]
    else:
        if hasattr(cd_base_reactant, "linkAnchor"):
            source_anchor_name = (
                momapy.celldesigner.io.celldesigner._parsing.get_anchor_name_for_frame(
                    cd_base_reactant
                )
            )
        else:
            source_anchor_name = "center"
    layout_element = layout.new_element(layout_element_cls)
    if hasattr(cd_base_product, "linkAnchor"):
        target_anchor_name = (
            momapy.celldesigner.io.celldesigner._parsing.get_anchor_name_for_frame(
                cd_base_product
            )
        )
    else:
        target_anchor_name = "center"
    origin = source_layout_element.anchor_point(source_anchor_name)
    unit_x = target_layout_element.anchor_point(target_anchor_name)
    unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    intermediate_points = [
        edit_point.transformed(transformation) for edit_point in edit_points
    ]
    if source_anchor_name == "center":
        if intermediate_points:
            reference_point = intermediate_points[0]
        else:
            reference_point = unit_x
        start_point = source_layout_element.own_border(reference_point)
    else:
        start_point = origin
    if target_anchor_name == "center":
        if intermediate_points:
            reference_point = intermediate_points[-1]
        else:
            reference_point = start_point
        end_point = target_layout_element.own_border(reference_point)
    else:
        end_point = target_layout_element.anchor_point(target_anchor_name)
    points = [start_point] + intermediate_points + [end_point]
    segments = make_segments(points)
    for segment in segments:
        layout_element.segments.append(segment)
    return layout_element
