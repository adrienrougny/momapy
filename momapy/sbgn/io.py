from momapy.core import Port, NodeLayoutElementLabel
from momapy.builder import new_object
from momapy.geometry import Point
from momapy.coloring import rgba
from momapy.arcs import PolyLine, Arrow
from momapy.shapes import Rectangle, RectangleWithConnectors
from momapy.sbgn.core import Macromolecule, GenericProcess, Reactant, Product, StateVariable
from momapy.sbgn.builder import SBGNMapBuilder

import libsbgnpy.libsbgn as libsbgn

LibSBGNGlyphMapping = {
    "macromolecule": (Macromolecule, Rectangle),
    "process": (GenericProcess, RectangleWithConnectors),
    "state variable": (StateVariable, Rectangle)
}

LibSBGNArcMapping = {
    "consumption": (Reactant, PolyLine, "target"),
    "production": (Product, Arrow, "source")
}

def read_file(file_name, return_builder=False, relative=False):
    builder = SBGNMapBuilder()
    model = builder.new_model()
    layout = builder.new_layout()
    model_layout_mapping = builder.new_model_layout_mapping()
    builder.model = model
    builder.layout = layout
    builder.model_layout_mapping = model_layout_mapping
    d_model_elements_ids = {}
    d_layout_elements_ids = {}
    libsbgn_sbgn = libsbgn.parse(file_name, silence=True)
    libsbgn_map = libsbgn_sbgn.get_map()
    builder.layout.width, builder.layout.height = _get_libsbgn_map_dimensions(libsbgn_map)
    for glyph in libsbgn_map.get_glyph():
        if glyph.get_class() == libsbgn.GlyphClass.COMPARTMENT:
            _build_map_elements_from_glyph(glyph, builder, d_model_elements_ids, d_layout_elements_ids, relative)
    for glyph in libsbgn_map.get_glyph():
        if glyph.get_class() != libsbgn.GlyphClass.COMPARTMENT:
            _build_map_elements_from_glyph(glyph, builder, d_model_elements_ids, d_layout_elements_ids, relative)
    for arc in libsbgn_map.get_arc():
        _build_map_elements_from_arc(arc, builder, d_model_elements_ids, d_layout_elements_ids, relative)
    if return_builder:
        return builder
    return builder.build()

def _build_map_elements_from_glyph(glyph, builder, d_model_elements_ids, d_layout_elements_ids, relative):
    model_element, layout_element = _make_map_elements_from_glyph(glyph, builder, d_model_elements_ids, d_layout_elements_ids, relative)
    builder.add_model_element(model_element)
    builder.add_layout_element(layout_element)
    builder.add_layout_element_to_model_element(layout_element, model_element)
    d_model_elements_ids[model_element.id] = model_element
    d_layout_elements_ids[layout_element.id] = layout_element
    for subglyph in glyph.get_glyph():
        _build_map_elements_from_subglyph(subglyph, model_element, builder, d_model_elements_ids, d_layout_elements_ids, relative)
    for libsbgn_port in glyph.get_port():
        _build_port_from_libsbgn_port(libsbgn_port, model_element, layout_element, builder, d_model_elements_ids, d_layout_elements_ids, relative)

def _build_map_elements_from_arc(arc, builder, d_model_elements_ids, d_layout_elements_ids, relative):
    model_element, layout_element = _make_map_elements_from_arc(arc, builder, d_model_elements_ids, d_layout_elements_ids, relative)
    super_element = d_model_elements_ids[getattr(arc, f"get_{LibSBGNArcMapping[arc.get_class().value][2]}")()]
    super_element.add_element(model_element)
    builder.add_layout_element(layout_element)
    builder.add_layout_element_to_model_element(layout_element, model_element)
    d_model_elements_ids[model_element.id] = model_element
    d_layout_elements_ids[layout_element.id] = layout_element
    for subglyph in arc.get_glyph():
        _build_map_elements_from_subglyph(subglyph, model_element, builder, d_model_elements_ids, d_layout_elements_ids, relative)
    for libsbgn_port in arc.get_port():
        _build_port_from_libsbgn_port(libsbgn_port, model_element, layout_element, builder, d_model_elements_ids, d_layout_elements_ids, relative)

def _build_map_elements_from_subglyph(subglyph, super_element, builder, d_model_elements_ids, d_layout_elements_ids, relative):
    model_element, layout_element = _make_map_elements_from_glyph(subglyph, builder, d_model_elements_ids, d_layout_elements_ids, relative)
    super_element.add_element(model_element)
    builder.add_layout_element(layout_element)
    builder.add_layout_element_to_model_element(layout_element, model_element)
    d_model_elements_ids[model_element.id] = model_element
    d_layout_elements_ids[layout_element.id] = layout_element
    for subsubglyph in subglyph.get_glyph():
        _build_map_elements_from_subglyph(subsubglyph, model_element, builder, d_model_elements_ids, d_layout_elements_ids, relative)
    for libsbgn_port in subglyph.get_port():
        _build_port_from_libsbgn_port(libsbgn_port, model_element, layout_element, builder, d_model_elements_ids, d_layout_elements_ids, relative)

def _build_port_from_libsbgn_port(libsbgn_port, super_model_element, super_layout_element, builder, d_model_elements_ids, d_layout_elements_ids, relative):
    port = _make_port_from_libsbgn_port(libsbgn_port, builder, relative)
    super_layout_element.ports.add(port)
    d_model_elements_ids[port.id] = super_model_element
    d_layout_elements_ids[port.id] = port

def _make_map_elements_from_glyph(glyph, builder, d_model_elements_ids, d_layout_elements_ids, relative):
    model_element = _make_model_element_from_glyph(glyph, builder, d_model_elements_ids, d_layout_elements_ids, relative)
    layout_element = _make_layout_element_from_glyph(glyph, builder, d_model_elements_ids, d_layout_elements_ids, relative)
    return model_element, layout_element

def _make_model_element_from_glyph(glyph, builder, d_model_elements_ids, d_layout_elements_ids, relative):
    model_element = builder.new_model_element(LibSBGNGlyphMapping[glyph.get_class().value][0])
    model_element.id = glyph.get_id()
    if glyph.get_label() is not None and glyph.get_label().get_text():
        model_element.label = glyph.get_label().get_text()
    return model_element

def _make_layout_element_from_glyph(glyph, builder, d_model_elements_ids, d_layout_elements_ids, relative):
    layout_element = builder.new_layout_element(LibSBGNGlyphMapping[glyph.get_class().value][1])
    layout_element.id = glyph.get_id()
    layout_element.width = glyph.get_bbox().get_w()
    layout_element.height = glyph.get_bbox().get_h()
    layout_element.position = _get_position_from_libsbgn_bbox(
            glyph.get_bbox(),
            builder.layout.height)
    layout_element.fill = rgba(255, 255, 255, 1)
    if glyph.get_label() is not None and glyph.get_label().get_text():
        label_element = builder.new_layout_element(NodeLayoutElementLabel)
        label_element.text = glyph.get_label().get_text()
        label_element.position = layout_element.position
        label_element.width = glyph.get_bbox().get_w()
        label_element.height = glyph.get_bbox().get_h()
        layout_element.label = label_element
    if glyph.get_class().value == "process":
        for libsbgn_port in glyph.get_port():
            if libsbgn_port.get_x() < glyph.get_bbox().get_x():
                layout_element.left_connector_length = glyph.get_bbox().get_x() - libsbgn_port.get_x()
            else:
                layout_element.right_connector_length = libsbgn_port.get_x() - glyph.get_bbox().get_x() - glyph.get_bbox().get_w()
    return layout_element

def _make_port_from_libsbgn_port(libsbgn_port, builder, relative):
    port = builder.new_layout_element(Port)
    port.x = libsbgn_port.get_x()
    port.y = _transform_y_coord(libsbgn_port.get_y(), builder.layout.height)
    port.id = libsbgn_port.get_id()
    return port

def _make_map_elements_from_arc(arc, builder, d_model_elements_ids, d_layout_elements_ids, relative):
    model_element = _make_model_element_from_arc(arc, builder, d_model_elements_ids, d_layout_elements_ids, relative)
    layout_element = _make_layout_element_from_arc(arc, builder, d_model_elements_ids, d_layout_elements_ids, relative)
    return model_element, layout_element

def _make_model_element_from_arc(arc, builder, d_model_elements_ids, d_layout_elements_ids, relative):
    model_element = builder.new_model_element(LibSBGNArcMapping[arc.get_class().value][0])
    model_element.id = arc.get_id()
    if LibSBGNArcMapping[arc.get_class().value][2] == "target":
        model_element.element = d_model_elements_ids[arc.get_source()]
    else:
        model_element.element = d_model_elements_ids[arc.get_target()]
    return model_element

def _make_layout_element_from_arc(arc, builder, d_model_elements_ids, d_layout_elements_ids, relative):
    layout_element = builder.new_layout_element(LibSBGNArcMapping[arc.get_class().value][1])
    layout_element.id = arc.get_id()
    layout_element.source = d_layout_elements_ids[arc.get_source()]
    layout_element.target = d_layout_elements_ids[arc.get_target()]
    if not relative:
        for libsbgn_point in [arc.get_start()] + arc.get_next() + [arc.get_end()]:
            layout_element.points.append(new_object(
                Point,
                libsbgn_point.get_x(),
                _transform_y_coord(libsbgn_point.get_y(),
                builder.layout.height)))
    else:

    return layout_element

def _get_libsbgn_map_dimensions(libsbgn_map):
    return _get_libsbgn_map_max_x_and_y(libsbgn_map)

def _get_glyph_max_x_and_y(glyph):
    max_x = glyph.get_bbox().get_x() + glyph.get_bbox().get_w()
    max_y = glyph.get_bbox().get_y() + glyph.get_bbox().get_h()
    for subglyph in glyph.get_glyph():
        sub_max_x, sub_max_y = _get_glyph_max_x_and_y(subglyph)
        if sub_max_x > max_x:
            max_x = sub_max_x
        if sub_max_y > max_y:
            max_y = sub_max_y
    return max_x, max_y

def _get_arc_max_x_and_y(arc):
    max_x = 0
    max_y = 0
    for p in [arc.get_start()] + arc.get_next() + [arc.get_end()]:
        if p.get_x() > max_x:
            max_x = p.get_x()
        if p.get_y() > max_y:
            max_y = p.get_y()
    for glyph in arc.get_glyph():
        glyph_max_x, glyph_max_y = _get_glyph_max_x_and_y(glyph)
        if glyph_max_x > max_x:
            max_x = glyph_max_x
        if glyph_max_y > max_y:
            max_y = glyph_max_y
    return max_x, max_y

def _get_arcgroup_max_x_and_y(arcgroup):
    max_x = 0
    max_y = 0
    for glyph in arcgroup.get_glyph():
        glyph_max_x, glyph_max_y = _get_glyph_max_x_and_y(glyph)
        if glyph_max_x > max_x:
            max_x = glyph_max_x
        if glyph_max_y > max_y:
            max_y = glyph_max_y
    for arc in arcgroup.get_arc():
        arc_max_x, arc_max_y = _get_arc_max_x_and_y(arc)
        if arc_max_x > max_x:
            max_x = arc_max_x
        if arc_max_y > max_y:
            max_y = arc_max_y
    return max_x, max_y

def _get_libsbgn_map_max_x_and_y(libsbgn_map):
    max_x = 0
    max_y = 0
    for glyph in libsbgn_map.get_glyph():
        glyph_max_x, glyph_max_y = _get_glyph_max_x_and_y(glyph)
        if glyph_max_x > max_x:
            max_x = glyph_max_x
        if glyph_max_y > max_y:
            max_y = glyph_max_y
    for arc in libsbgn_map.get_arc():
        arc_max_x, arc_max_y = _get_arc_max_x_and_y(arc)
        if arc_max_x > max_x:
            max_x = arc_max_x
        if arc_max_y > max_y:
            max_y = arc_max_y
    for arcgroup in libsbgn_map.get_arcgroup():
        arcgroup_max_x, arcgroup_max_y = _get_arcgroup_max_x_and_y(arcgroup)
        if arcgroup_max_x > max_x:
            max_x = arcgroup_max_x
        if arcgroup_max_y > max_y:
            max_y = arcgroup_max_y
    return max_x, max_y

def _transform_y_coord(y, height):
    return height - y

def _get_position_from_libsbgn_bbox(bbox, height):
    return new_object(
            Point,
            bbox.get_x() + bbox.get_w() / 2,
            _transform_y_coord(bbox.get_y() + bbox.get_h() / 2, height))
