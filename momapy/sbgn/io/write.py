import libsbgnpy.libsbgn as libsbgn

import momapy.builder
import momapy.sbgn.pd
import momapy.sbgn.af


def write_file(map_, file_path):
    sbgn = libsbgn.sbgn()
    sbgn_map = libsbgn.map()
    sbgn.set_map(sbgn_map)
    language = _map_to_language(map_)
    sbgn_map.set_language(language)
    if momapy.builder.isinstance_or_builder(map_, momapy.sbgn.pd.SBGNPDMap):
        for layout_element in map_.layout.layout_elements:
            sbgn_elements = _layout_element_to_sbgnml_elements(
                layout_element, map_
            )
            for sbgn_element in sbgn_elements:
                _add_sub_sbgn_element_to_sbgn_element(sbgn_element, sbgn_map)
    sbgn.write_file(file_path)


def _add_sub_sbgn_element_to_sbgn_element(sub_sbgn_element, sbgn_element):
    if isinstance(sub_sbgn_element, libsbgn.glyph):
        sbgn_element.add_glyph(sub_sbgn_element)
    elif isinstance(sub_sbgn_element, libsbgn.arc):
        sbgn_element.add_arc(sub_sbgn_element)
    elif isinstance(sub_sbgn_element, libsbgn.arcgroup):
        sbgn_element.add_arcgroup(sub_sbgn_element)


def _layout_element_to_sbgnml_elements(
    layout_element, map_, super_layout_element=None
):
    cls = type(layout_element)
    transformation_func = _get_transformation_func_from_cls(cls)
    if transformation_func is not None:
        sbgn_elements = transformation_func(
            layout_element, map_, super_layout_element
        )
    else:
        print(
            f"object {layout_element.id}: unknown class '{cls}' for transformation"
        )
        sbgn_elements = []
    return sbgn_elements


def _get_transformation_func_from_cls(cls):
    while issubclass(cls, momapy.builder.Builder):
        cls = cls._cls_to_build
    return LAYOUT_ELEMENT_TO_TRANSFORMATION_FUNC_MAPPING.get(cls)


def _map_to_language(map_):
    d = {
        momapy.sbgn.pd.SBGNPDMap: "process description",
        momapy.sbgn.af.SBGNAFMap: "activity flow",
    }
    return libsbgn.Language(d[type(map_)])


def _node_layout_to_glyph(layout_element, map_, super_layout_element=None):
    glyph = libsbgn.glyph()
    glyph.set_id(layout_element.id)
    bbox = libsbgn.bbox()
    nw = layout_element.position - (
        layout_element.width / 2,
        layout_element.height / 2,
    )
    bbox.set_x(nw.x)
    bbox.set_y(nw.y)
    bbox.set_w(layout_element.width)
    bbox.set_h(layout_element.height)
    glyph.set_bbox(bbox)
    if layout_element.label is not None:
        label = libsbgn.label()
        label.set_text(layout_element.label.text)
        glyph.set_label(label)
    return glyph


def _compartment_layout_to_sbgn_elements(
    layout_element, map_, super_layout_element=None
):
    glyph = _node_layout_to_glyph(layout_element, map_)
    glyph.set_class(libsbgn.GlyphClass["COMPARTMENT"])
    return [glyph]


def _entity_pool_layout_to_glyph(
    layout_element, map_, super_layout_element=None
):
    glyph = _node_layout_to_glyph(layout_element, map_, super_layout_element)
    for sub_layout_element in layout_element.layout_elements:
        sub_sbgn_elements = _layout_element_to_sbgnml_elements(
            sub_layout_element, map_
        )
        for sub_sbgn_element in sub_sbgn_elements:
            _add_sub_sbgn_element_to_sbgn_element(sub_sbgn_element, glyph)
    return glyph


def _macromolecule_layout_to_sbgn_elements(
    layout_element, map_, super_layout_element=None
):
    glyph = _entity_pool_layout_to_glyph(
        layout_element, map_, super_layout_element
    )
    glyph.set_class(libsbgn.GlyphClass["MACROMOLECULE"])
    return [glyph]


def _simple_chemical_layout_to_sbgn_elements(
    layout_element, map_, super_layout_element=None
):
    glyph = _entity_pool_layout_to_glyph(
        layout_element, map_, super_layout_element
    )
    glyph.set_class(libsbgn.GlyphClass["SIMPLE_CHEMICAL"])
    return [glyph]


def _process_layout_to_glyph(layout_element, map_, super_layout_element=None):
    glyph = _node_layout_to_glyph(layout_element, map_, super_layout_element)
    left_port = libsbgn.port()
    left_port.set_x(layout_element.left_connector_tip().x)
    left_port.set_y(layout_element.left_connector_tip().y)
    left_port.set_id(f"{layout_element.id}_left_port")
    glyph.add_port(left_port)
    right_port = libsbgn.port()
    right_port.set_x(layout_element.right_connector_tip().x)
    right_port.set_y(layout_element.right_connector_tip().y)
    right_port.set_id(f"{layout_element.id}_right_port")
    glyph.add_port(right_port)
    return glyph


def _process_layout_to_arcs(layout_element, map_, super_layout_element=None):
    arcs = []
    for sub_layout_element in layout_element.layout_elements:
        sub_sbgn_elements = _layout_element_to_sbgnml_elements(
            sub_layout_element, map_, layout_element
        )
        arcs += sub_sbgn_elements
    return arcs


def _generic_process_layout_to_sbgn_elements(
    layout_element, map_, super_layout_element=None
):
    sbgn_elements = []
    glyph = _process_layout_to_glyph(layout_element, map_, super_layout_element)
    glyph.set_class(libsbgn.GlyphClass["PROCESS"])
    sbgn_elements.append(glyph)
    arcs = _process_layout_to_arcs(layout_element, map_, super_layout_element)
    sbgn_elements += arcs
    return sbgn_elements


def _uncertain_process_layout_to_sbgn_elements(
    layout_element, map_, super_layout_element=None
):
    sbgn_elements = []
    glyph = _process_layout_to_glyph(layout_element, map_, super_layout_element)
    glyph.set_class(libsbgn.GlyphClass["UNCERTAIN_PROCESS"])
    sbgn_elements.append(glyph)
    arcs = _process_layout_to_arcs(layout_element, map_, super_layout_element)
    sbgn_elements += arcs
    return sbgn_elements


def _state_variable_layout_to_sbgn_elements(
    layout_element, map_, super_layout_element=None
):
    glyph = _node_layout_to_glyph(layout_element, map_, super_layout_element)
    glyph.set_label(None)
    glyph.set_class(libsbgn.GlyphClass["STATE_VARIABLE"])
    state_variable = map_.layout_model_mapping[layout_element]
    state_variable, *_ = state_variable  # frozenset to frozenset
    state_variable, *_ = state_variable  # frozenset to tuple
    state_variable = state_variable[0]  # tuple to model element
    state = libsbgn.stateType()
    if state_variable.value is not None:
        state.set_value(state_variable.value)
    if (
        state_variable.variable is not None
        and not momapy.builder.isinstance_or_builder(
            state_variable.variable, momapy.sbgn.pd.UndefinedVariable
        )
    ):
        state.set_variable(state_variable.variable)
    glyph.set_state(state)
    return [glyph]


def _arc_layout_to_arc(layout_element, map_, super_layout_element=None):
    arc = libsbgn.arc()
    arc.set_id(layout_element.id)
    points = layout_element.points()
    start = libsbgn.startType()
    start.set_x(points[0].x)
    start.set_y(points[0].y)
    arc.set_start(start)
    end = libsbgn.endType()
    end.set_x(points[-1].x)
    end.set_y(points[-1].y)
    arc.set_end(end)
    for point in points[1:-1]:
        next_ = libsbgn.nextType()
        next_.set_x(point.x)
        next_.set_y(point.y)
        arc.add_next(next_)
    return arc


def _consumption_layout_to_sbgn_elements(
    layout_element, map_, super_layout_element=None
):
    arc = _arc_layout_to_arc(layout_element, map_, super_layout_element)
    arc.set_class(libsbgn.ArcClass["CONSUMPTION"])
    arc.set_source(layout_element.source.layout_element.id)
    end_point = layout_element.points()[-1]
    left_connector_tip = (
        layout_element.target.layout_element.left_connector_tip()
    )
    right_connector_tip = (
        layout_element.target.layout_element.right_connector_tip()
    )
    left_distance = momapy.geometry.Segment(
        end_point, left_connector_tip
    ).length()
    right_distance = momapy.geometry.Segment(
        end_point, right_connector_tip
    ).length()
    if right_distance > left_distance:
        port_id = f"{layout_element.target.layout_element.id}_left_port"
    else:
        port_id = f"{layout_element.target.layout_element.id}_right_port"
    arc.set_target(port_id)
    return [arc]


def _production_layout_to_sbgn_elements(
    layout_element, map_, super_layout_element=None
):
    arc = _arc_layout_to_arc(layout_element, map_, super_layout_element)
    arc.set_class(libsbgn.ArcClass["PRODUCTION"])
    arc.set_target(layout_element.target.layout_element.id)
    start_point = layout_element.points()[0]
    left_connector_tip = (
        layout_element.source.layout_element.left_connector_tip()
    )
    right_connector_tip = (
        layout_element.source.layout_element.right_connector_tip()
    )
    left_distance = momapy.geometry.Segment(
        start_point, left_connector_tip
    ).length()
    right_distance = momapy.geometry.Segment(
        start_point, right_connector_tip
    ).length()
    if right_distance > left_distance:
        port_id = f"{layout_element.source.layout_element.id}_left_port"
    else:
        port_id = f"{layout_element.source.layout_element.id}_right_port"
    arc.set_source(port_id)
    return [arc]


def _modulation_arc_layout_to_arc(
    layout_element, map_, super_layout_element=None
):
    arc = _arc_layout_to_arc(layout_element, map_, super_layout_element)
    arc.set_source(layout_element.source.layout_element.id)
    arc.set_target(layout_element.target.layout_element.id)
    return arc


def _modulation_layout_to_sbgn_elements(
    layout_element, map_, super_layout_element=None
):
    arc = _modulation_arc_layout_to_arc(
        layout_element, map_, super_layout_element
    )
    arc.set_class(libsbgn.ArcClass["MODULATION"])
    return [arc]


def _inhibition_layout_to_sbgn_elements(
    layout_element, map_, super_layout_element=None
):
    arc = _modulation_arc_layout_to_arc(
        layout_element, map_, super_layout_element
    )
    arc.set_class(libsbgn.ArcClass["INHIBITION"])
    return [arc]


def _stimulation_layout_to_sbgn_elements(
    layout_element, map_, super_layout_element=None
):
    arc = _modulation_arc_layout_to_arc(
        layout_element, map_, super_layout_element
    )
    arc.set_class(libsbgn.ArcClass["STIMULATION"])
    return [arc]


def _catalysis_layout_to_sbgn_elements(
    layout_element, map_, super_layout_element=None
):
    arc = _modulation_arc_layout_to_arc(
        layout_element, map_, super_layout_element
    )
    arc.set_class(libsbgn.ArcClass["CATALYSIS"])
    return [arc]


def _necessary_stimulation_layout_to_sbgn_elements(
    layout_element, map_, super_layout_element=None
):
    arc = _modulation_arc_layout_to_arc(
        layout_element, map_, super_layout_element
    )
    arc.set_class(libsbgn.ArcClass["NECESSARY_STIMULATION"])
    return [arc]


LAYOUT_ELEMENT_TO_TRANSFORMATION_FUNC_MAPPING = {
    momapy.sbgn.pd.CompartmentLayout: _compartment_layout_to_sbgn_elements,
    momapy.sbgn.pd.MacromoleculeLayout: _macromolecule_layout_to_sbgn_elements,
    momapy.sbgn.pd.SimpleChemicalLayout: _simple_chemical_layout_to_sbgn_elements,
    momapy.sbgn.pd.GenericProcessLayout: _generic_process_layout_to_sbgn_elements,
    momapy.sbgn.pd.UncertainProcessLayout: _uncertain_process_layout_to_sbgn_elements,
    momapy.sbgn.pd.StateVariableLayout: _state_variable_layout_to_sbgn_elements,
    momapy.sbgn.pd.ConsumptionLayout: _consumption_layout_to_sbgn_elements,
    momapy.sbgn.pd.ProductionLayout: _production_layout_to_sbgn_elements,
    momapy.sbgn.pd.ModulationLayout: _modulation_layout_to_sbgn_elements,
    momapy.sbgn.pd.InhibitionLayout: _inhibition_layout_to_sbgn_elements,
    momapy.sbgn.pd.StimulationLayout: _stimulation_layout_to_sbgn_elements,
    momapy.sbgn.pd.CatalysisLayout: _catalysis_layout_to_sbgn_elements,
    momapy.sbgn.pd.NecessaryStimulationLayout: _necessary_stimulation_layout_to_sbgn_elements,
}
