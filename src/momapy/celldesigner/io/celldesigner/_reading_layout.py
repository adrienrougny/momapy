"""CellDesigner layout-building helpers and constants.

Each ``make_*`` function takes a ``reading_context`` as its first
argument, checks whether ``reading_context.layout`` is ``None``, and
returns ``None`` early when no layout is being built.
"""

import math

import momapy.builder
import momapy.drawing
import momapy.geometry
import momapy.coloring
import momapy.core.layout
import momapy.celldesigner.core
import momapy.celldesigner.io.celldesigner._reading_parsing
import momapy.celldesigner.io.celldesigner._writing

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


_are_collinear = momapy.celldesigner.io.celldesigner._writing._are_collinear


def _apply_line_attributes(layout_element, cd_line_element):
    """Apply width and color from a ``<cd:line>`` XML element to a layout.

    Sets ``path_stroke_width`` and ``path_stroke`` on the layout, and
    propagates to arrowhead attributes when present (CellDesigner uses
    a single ``<cd:line>`` for the entire arc including arrowheads).

    Args:
        layout_element: The layout builder element to modify.
        cd_line_element: The lxml objectified ``<cd:line>`` element,
            or ``None`` (in which case nothing is changed).
    """
    if cd_line_element is None:
        return
    width = cd_line_element.get("width")
    if width is not None:
        width_value = float(width)
        layout_element.path_stroke_width = width_value
        if hasattr(layout_element, "arrowhead_stroke_width"):
            layout_element.arrowhead_stroke_width = width_value
        if hasattr(layout_element, "end_arrowhead_stroke_width"):
            layout_element.end_arrowhead_stroke_width = width_value
        if hasattr(layout_element, "start_arrowhead_stroke_width"):
            layout_element.start_arrowhead_stroke_width = width_value
    color = cd_line_element.get("color")
    if color is not None:
        rgba_hex = color[2:] + color[:2]
        color_value = momapy.coloring.Color.from_hexa(rgba_hex)
        layout_element.path_stroke = color_value
        if hasattr(layout_element, "arrowhead_stroke"):
            layout_element.arrowhead_stroke = color_value
        if hasattr(layout_element, "end_arrowhead_stroke"):
            layout_element.end_arrowhead_stroke = color_value
        if hasattr(layout_element, "start_arrowhead_stroke"):
            layout_element.start_arrowhead_stroke = color_value


def make_empty_layout(cd_element):
    layout = momapy.celldesigner.core.CellDesignerLayoutBuilder()
    return layout


def set_layout_size_and_position(reading_context, cd_model):
    if reading_context.layout is None:
        return
    reading_context.layout.width = float(
        momapy.celldesigner.io.celldesigner._reading_parsing.get_width(cd_model)
    )
    reading_context.layout.height = float(
        momapy.celldesigner.io.celldesigner._reading_parsing.get_height(cd_model)
    )
    reading_context.layout.position = momapy.geometry.Point(
        reading_context.layout.width / 2, reading_context.layout.height / 2
    )


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
    reading_context, cd_species_alias, layout_element_cls, name, homomultimer, hypothetical, active
):
    if reading_context.layout is None:
        return None
    layout_element = reading_context.layout.new_element(layout_element_cls)
    layout_element.id_ = cd_species_alias.get("id")
    cd_x, cd_y, cd_w, cd_h = momapy.celldesigner.io.celldesigner._reading_parsing.get_bounds(
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
    if hypothetical:
        layout_element.stroke_dasharray = (4, 2)
    if active:
        active_cls = _LAYOUT_TO_ACTIVE_LAYOUT[layout_element_cls]
        active_element = reading_context.layout.new_element(active_cls)
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
    reading_context,
    cd_modification_residue,
    modification_state,
    super_layout_element,
):
    if reading_context.layout is None:
        return None
    layout_element = reading_context.layout.new_element(momapy.celldesigner.core.ModificationLayout)
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
        residue_text_layout = reading_context.layout.new_element(momapy.core.layout.TextLayout)
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
    reading_context, cd_species_structural_state, super_layout_element
):
    if reading_context.layout is None:
        return None
    layout_element = reading_context.layout.new_element(momapy.celldesigner.core.StructuralStateLayout)
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


def make_compartment_from_alias(reading_context, cd_compartment, cd_compartment_alias):
    if reading_context.layout is None:
        return None
    if getattr(cd_compartment_alias, "class").text == "OVAL":
        layout_element_cls = momapy.celldesigner.core.OvalCompartmentLayout
    else:
        layout_element_cls = momapy.celldesigner.core.RectangleCompartmentLayout
    layout_element = reading_context.layout.new_element(layout_element_cls)
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
    text = momapy.celldesigner.io.celldesigner._reading_parsing.make_name(
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


def make_segments_non_t_shape(reading_context, cd_reaction):
    cd_id_to_layout_element = reading_context.xml_id_to_layout_element
    cd_base_reactants = momapy.celldesigner.io.celldesigner._reading_parsing.get_base_reactants(
        cd_reaction
    )
    cd_base_products = momapy.celldesigner.io.celldesigner._reading_parsing.get_base_products(
        cd_reaction
    )
    cd_base_reactant = cd_base_reactants[0]
    cd_base_product = cd_base_products[0]
    reactant_layout_element = cd_id_to_layout_element[cd_base_reactant.get("alias")]
    product_layout_element = cd_id_to_layout_element[cd_base_product.get("alias")]
    reactant_anchor_name = (
        momapy.celldesigner.io.celldesigner._reading_parsing.get_anchor_name_for_frame(
            cd_base_reactant
        )
    )
    product_anchor_name = (
        momapy.celldesigner.io.celldesigner._reading_parsing.get_anchor_name_for_frame(
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
        momapy.celldesigner.io.celldesigner._reading_parsing.get_edit_points_from_reaction(
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


def make_segments_left_t_shape(reading_context, cd_reaction):
    cd_id_to_layout_element = reading_context.xml_id_to_layout_element
    cd_base_reactants = momapy.celldesigner.io.celldesigner._reading_parsing.get_base_reactants(
        cd_reaction
    )
    cd_base_products = momapy.celldesigner.io.celldesigner._reading_parsing.get_base_products(
        cd_reaction
    )
    cd_base_reactant_0 = cd_base_reactants[0]
    cd_base_reactant_1 = cd_base_reactants[1]
    cd_base_product = cd_base_products[0]
    reactant_layout_element_0 = cd_id_to_layout_element[cd_base_reactant_0.get("alias")]
    reactant_layout_element_1 = cd_id_to_layout_element[cd_base_reactant_1.get("alias")]
    product_layout_element = cd_id_to_layout_element[cd_base_product.get("alias")]
    product_anchor_name = (
        momapy.celldesigner.io.celldesigner._reading_parsing.get_anchor_name_for_frame(
            cd_base_product
        )
    )
    origin = reactant_layout_element_0.center()
    unit_x = reactant_layout_element_1.center()
    unit_y = product_layout_element.center()
    if _are_collinear(unit_x, unit_y, origin):
        origin = momapy.geometry.Point(origin.x + 1, origin.y + 1)
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    cd_edit_points = (
        momapy.celldesigner.io.celldesigner._reading_parsing.get_edit_points_from_reaction(
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
            momapy.celldesigner.io.celldesigner._reading_parsing.get_anchor_name_for_frame(
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


def make_segments_right_t_shape(reading_context, cd_reaction):
    cd_id_to_layout_element = reading_context.xml_id_to_layout_element
    cd_base_reactants = momapy.celldesigner.io.celldesigner._reading_parsing.get_base_reactants(
        cd_reaction
    )
    cd_base_products = momapy.celldesigner.io.celldesigner._reading_parsing.get_base_products(
        cd_reaction
    )
    cd_base_product_0 = cd_base_products[0]
    cd_base_product_1 = cd_base_products[1]
    cd_base_reactant = cd_base_reactants[0]
    product_layout_element_0 = cd_id_to_layout_element[cd_base_product_0.get("alias")]
    product_layout_element_1 = cd_id_to_layout_element[cd_base_product_1.get("alias")]
    reactant_layout_element = cd_id_to_layout_element[cd_base_reactant.get("alias")]
    reactant_anchor_name = (
        momapy.celldesigner.io.celldesigner._reading_parsing.get_anchor_name_for_frame(
            cd_base_reactant
        )
    )
    origin = reactant_layout_element.center()
    unit_x = product_layout_element_0.center()
    unit_y = product_layout_element_1.center()
    if _are_collinear(unit_x, unit_y, origin):
        origin = momapy.geometry.Point(origin.x + 1, origin.y + 1)
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    cd_edit_points = (
        momapy.celldesigner.io.celldesigner._reading_parsing.get_edit_points_from_reaction(
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
            momapy.celldesigner.io.celldesigner._reading_parsing.get_anchor_name_for_frame(
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
    reading_context,
    cd_reaction,
    layout_element_cls,
    cd_base_reactants,
    cd_base_products,
):
    if reading_context.layout is None:
        return None, False, False
    cd_id_to_layout_element = reading_context.xml_id_to_layout_element
    layout_element = reading_context.layout.new_element(layout_element_cls)
    layout_element.id_ = f"{cd_reaction.get('id')}_layout"
    layout_element.reversible = cd_reaction.get("reversible") == "true"
    if not layout_element.reversible:
        layout_element.start_shorten = 0.0
    if len(cd_base_reactants) == 1 and len(cd_base_products) == 1:
        segments = make_segments_non_t_shape(reading_context, cd_reaction)
        reaction_node_segment = int(
            momapy.celldesigner.io.celldesigner._reading_parsing.get_rectangle_index(
                cd_reaction
            )
        )
        make_base_reactant_layouts = False
        make_base_product_layouts = False
    elif len(cd_base_reactants) > 1 and len(cd_base_products) == 1:
        segments = make_segments_left_t_shape(reading_context, cd_reaction)
        reaction_node_segment = int(
            momapy.celldesigner.io.celldesigner._reading_parsing.get_t_shape_index(cd_reaction)
        )
        make_base_reactant_layouts = True
        make_base_product_layouts = False
    elif len(cd_base_reactants) == 1 and len(cd_base_products) > 1:
        segments = make_segments_right_t_shape(reading_context, cd_reaction)
        reaction_node_segment = (
            len(segments)
            - 1
            - int(
                momapy.celldesigner.io.celldesigner._reading_parsing.get_t_shape_index(
                    cd_reaction
                )
            )
        )
        make_base_reactant_layouts = False
        make_base_product_layouts = True
    for segment in segments:
        layout_element.segments.append(segment)
    layout_element.reaction_node_segment = reaction_node_segment
    if len(cd_base_reactants) == 1:
        layout_element.source = cd_id_to_layout_element[
            cd_base_reactants[0].get("alias")
        ]
    if len(cd_base_products) == 1:
        layout_element.target = cd_id_to_layout_element[
            cd_base_products[0].get("alias")
        ]
    cd_extension = momapy.celldesigner.io.celldesigner._reading_parsing.get_extension(
        cd_reaction
    )
    cd_line = getattr(cd_extension, "line", None) if cd_extension is not None else None
    _apply_line_attributes(layout_element, cd_line)
    return layout_element, make_base_reactant_layouts, make_base_product_layouts


def make_reactant_from_base(
    reading_context,
    cd_base_reactant,
    n_cd_base_reactant,
    cd_reaction,
    super_layout_element,
):
    if reading_context.layout is None:
        return None
    cd_id_to_layout_element = reading_context.xml_id_to_layout_element
    layout_element = reading_context.layout.new_element(momapy.celldesigner.core.ConsumptionLayout)
    cd_edit_points = (
        momapy.celldesigner.io.celldesigner._reading_parsing.get_edit_points_from_reaction(
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
        momapy.celldesigner.io.celldesigner._reading_parsing.get_anchor_name_for_frame(
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
    layout_element.source = super_layout_element
    layout_element.target = species_layout_element
    cd_extension = momapy.celldesigner.io.celldesigner._reading_parsing.get_extension(
        cd_reaction
    )
    cd_line = getattr(cd_extension, "line", None) if cd_extension is not None else None
    _apply_line_attributes(layout_element, cd_line)
    return layout_element


def make_reactant_from_link(
    reading_context, cd_reactant_link, super_layout_element
):
    if reading_context.layout is None:
        return None
    cd_id_to_layout_element = reading_context.xml_id_to_layout_element
    layout_element = reading_context.layout.new_element(momapy.celldesigner.core.ConsumptionLayout)
    species_layout_element = cd_id_to_layout_element[cd_reactant_link.get("alias")]
    reactant_anchor_name = (
        momapy.celldesigner.io.celldesigner._reading_parsing.get_anchor_name_for_frame(
            cd_reactant_link
        )
    )
    if reactant_anchor_name == "center":
        origin = species_layout_element.center()
    else:
        origin = species_layout_element.anchor_point(reactant_anchor_name)
    unit_x = super_layout_element.left_connector_tip()
    unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    cd_edit_points = momapy.celldesigner.io.celldesigner._reading_parsing.get_edit_points_from_participant_link(
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
    layout_element.source = super_layout_element
    layout_element.target = species_layout_element
    cd_line = getattr(cd_reactant_link, "line", None)
    _apply_line_attributes(layout_element, cd_line)
    return layout_element


def make_product_from_base(
    reading_context,
    cd_base_product,
    n_cd_base_product,
    cd_reaction,
    super_layout_element,
):
    if reading_context.layout is None:
        return None
    cd_id_to_layout_element = reading_context.xml_id_to_layout_element
    layout_element = reading_context.layout.new_element(momapy.celldesigner.core.ProductionLayout)
    cd_edit_points = (
        momapy.celldesigner.io.celldesigner._reading_parsing.get_edit_points_from_reaction(
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
        momapy.celldesigner.io.celldesigner._reading_parsing.get_anchor_name_for_frame(
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
    layout_element.source = super_layout_element
    layout_element.target = product_layout_element
    cd_extension = momapy.celldesigner.io.celldesigner._reading_parsing.get_extension(
        cd_reaction
    )
    cd_line = getattr(cd_extension, "line", None) if cd_extension is not None else None
    _apply_line_attributes(layout_element, cd_line)
    return layout_element


def make_product_from_link(
    reading_context, cd_product_link, super_layout_element
):
    if reading_context.layout is None:
        return None
    cd_id_to_layout_element = reading_context.xml_id_to_layout_element
    layout_element = reading_context.layout.new_element(momapy.celldesigner.core.ProductionLayout)
    species_layout_element = cd_id_to_layout_element[cd_product_link.get("alias")]
    product_anchor_name = (
        momapy.celldesigner.io.celldesigner._reading_parsing.get_anchor_name_for_frame(
            cd_product_link
        )
    )
    origin = super_layout_element.right_connector_tip()
    if product_anchor_name == "center":
        unit_x = species_layout_element.center()
    else:
        unit_x = species_layout_element.anchor_point(product_anchor_name)
    unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
    transformation = momapy.geometry.get_transformation_for_frame(
        origin, unit_x, unit_y
    )
    cd_edit_points = momapy.celldesigner.io.celldesigner._reading_parsing.get_edit_points_from_participant_link(
        cd_product_link
    )
    if cd_edit_points is None:
        edit_points = []
    else:
        edit_points = make_points(cd_edit_points)
    intermediate_points = [
        edit_point.transformed(transformation) for edit_point in edit_points
    ]
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
    layout_element.source = super_layout_element
    layout_element.target = species_layout_element
    cd_line = getattr(cd_product_link, "line", None)
    _apply_line_attributes(layout_element, cd_line)
    return layout_element


_TARGET_LINE_INDEX_TO_ANCHOR_NAME = {
    "2": "north",
    "3": "south",
    "4": "north_west",
    "5": "north_east",
    "6": "south_west",
    "7": "south_east",
}


def _get_anchor_point_from_target_line_index(reaction_layout, target_line_index):
    """Compute the anchor point on the reaction node from targetLineIndex.

    The targetLineIndex format is "segmentIndex,anchorId" where anchorId
    identifies an anchor on the reaction node rectangle. The anchor
    point is computed from the node's own anchor methods, then rotated
    by the reaction line angle.

    Args:
        reaction_layout: The reaction layout element.
        target_line_index: The targetLineIndex string (e.g. "0,2").

    Returns:
        The anchor point, or None if parsing fails.
    """
    if target_line_index is None or "," not in target_line_index:
        return None
    anchor_id = target_line_index.split(",")[1]
    anchor_name = _TARGET_LINE_INDEX_TO_ANCHOR_NAME.get(anchor_id)
    if anchor_name is None:
        return None
    reaction_node = reaction_layout._make_reaction_node()
    anchor_point = reaction_node.anchor_point(anchor_name)
    rotation = reaction_layout._make_reaction_node_rotation()
    return anchor_point.transformed(rotation)


def make_modifier(
    reading_context,
    cd_reaction_modification,
    layout_element_cls,
    source_layout_element,
    super_layout_element,
    has_boolean_input,
):
    if reading_context.layout is None:
        return None
    layout_element = reading_context.layout.new_element(layout_element_cls)
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
                source_anchor_name = momapy.celldesigner.io.celldesigner._reading_parsing.get_anchor_name_for_frame(
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
    cd_target_line_index = cd_reaction_modification.get("targetLineIndex")
    target_anchor_point = _get_anchor_point_from_target_line_index(
        super_layout_element, cd_target_line_index
    )
    if target_anchor_point is not None:
        unit_x = target_anchor_point
    else:
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
    if target_anchor_point is not None:
        end_point = target_anchor_point
    else:
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
    layout_element.target = super_layout_element
    cd_line = getattr(cd_reaction_modification, "line", None)
    _apply_line_attributes(layout_element, cd_line)
    return layout_element


def make_logic_gate(reading_context, cd_element, layout_element_cls):
    if reading_context.layout is None:
        return None
    cd_id_to_layout_element = reading_context.xml_id_to_layout_element
    layout_element = reading_context.layout.new_element(layout_element_cls)
    cd_edit_points = cd_element.get("editPoints")
    edit_points = make_points(cd_edit_points)
    position = edit_points[-1]
    layout_element.position = position
    cd_modifiers = cd_element.get("aliases")
    layout_input_elements = [
        cd_id_to_layout_element[cd_input_id] for cd_input_id in cd_modifiers.split(",")
    ]
    return layout_element


def make_logic_arc(reading_context, gate_layout_element, input_layout_element):
    if reading_context.layout is None:
        return None
    layout_element = reading_context.layout.new_element(momapy.celldesigner.core.LogicArcLayout)
    start_point = input_layout_element.own_border(gate_layout_element.position)
    end_point = gate_layout_element.own_border(start_point)
    segment = momapy.geometry.Segment(start_point, end_point)
    layout_element.segments.append(segment)
    layout_element.source = gate_layout_element
    layout_element.target = input_layout_element
    return layout_element


def make_modulation(
    reading_context,
    cd_reaction,
    layout_element_cls,
    source_layout_element,
    target_layout_element,
    has_boolean_input,
    cd_base_reactant,
    cd_base_product,
):
    if reading_context.layout is None:
        return None
    cd_edit_points = (
        momapy.celldesigner.io.celldesigner._reading_parsing.get_edit_points_from_reaction(
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
                momapy.celldesigner.io.celldesigner._reading_parsing.get_anchor_name_for_frame(
                    cd_base_reactant
                )
            )
        else:
            source_anchor_name = "center"
    layout_element = reading_context.layout.new_element(layout_element_cls)
    layout_element.id_ = f"{cd_reaction.get('id')}_layout"
    if hasattr(cd_base_product, "linkAnchor"):
        target_anchor_name = (
            momapy.celldesigner.io.celldesigner._reading_parsing.get_anchor_name_for_frame(
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
    layout_element.source = source_layout_element
    layout_element.target = target_layout_element
    cd_extension = momapy.celldesigner.io.celldesigner._reading_parsing.get_extension(
        cd_reaction
    )
    cd_line = getattr(cd_extension, "line", None) if cd_extension is not None else None
    _apply_line_attributes(layout_element, cd_line)
    return layout_element
