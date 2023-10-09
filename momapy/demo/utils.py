import copy

import numpy

import IPython.display
import skia

import momapy.rendering.skia
import momapy.geometry
import momapy.builder
import momapy.core
import momapy.drawing
import momapy.meta.nodes
import momapy.positioning


def display(obj, width=600, height=450):
    surface = skia.Surface.MakeRasterN32Premul(width, height)
    canvas = surface.getCanvas()
    renderer = momapy.rendering.skia.SkiaRenderer(canvas)
    renderer.begin_session()
    if momapy.builder.isinstance_or_builder(obj, momapy.core.Map):
        renderer.render_map(obj)
    elif momapy.builder.isinstance_or_builder(obj, momapy.core.LayoutElement):
        renderer.render_layout_element(obj)
    if momapy.builder.isinstance_or_builder(obj, momapy.drawing.DrawingElement):
        renderer.render_drawing_element(obj)
    image = surface.makeImageSnapshot()
    renderer.end_session()
    IPython.display.display(image)


def display_at(obj, positions, width=600, height=450):
    obj = copy.deepcopy(obj)
    cp_builder_cls = momapy.builder.get_or_make_builder_cls(
        momapy.meta.nodes.CrossPoint
    )
    if momapy.builder.isinstance_or_builder(positions, momapy.geometry.Point):
        positions = [positions]
    for position in positions:
        cp = cp_builder_cls(
            width=12.0,
            height=12.0,
            stroke_width=1.5,
            stroke=momapy.coloring.red,
            position=position,
        )
        obj.add_element(cp)
    display(obj, width, height)


def make_toy_node(
    cls,
    position,
    scale,
    make_auxiliary=False,
    auxiliary_unit_width=19,
    auxiliary_unit_height=8,
):
    if not issubclass(cls, momapy.builder.Builder):
        cls = momapy.builder.get_or_make_builder_cls(cls)
    m = cls()
    if m.width is None:
        m.width = 50
    if m.height is None:
        m.height = 50
    if m.fill is None:
        m.fill = momapy.coloring.white
    if m.stroke is None:
        m.stroke = momapy.coloring.black
    if m.stroke_width is None:
        m.stroke_width = 1.0
    m.position = position
    m.width = m.width * scale
    m.height = m.height * scale
    for attr in [
        "offset",
        "left_connector_length",
        "right_connector_length",
    ]:
        if hasattr(m, attr):
            setattr(m, attr, getattr(m, attr) * scale)
    for attr in [
        "rounded_corners",
        "cut_corners",
    ]:
        if hasattr(m, attr):
            setattr(m, attr, getattr(m, attr) * scale / 2)

    if make_auxiliary:
        StateVariableLayoutBuilder = momapy.builder.get_or_make_builder_cls(
            momapy.sbgn.pd.StateVariableLayout
        )
        UnitOfInformationLayoutBuilder = momapy.builder.get_or_make_builder_cls(
            momapy.sbgn.pd.UnitOfInformationLayout
        )
        s1 = StateVariableLayoutBuilder(
            width=auxiliary_unit_width * scale,
            height=auxiliary_unit_height * scale,
            position=m.self_angle(130),
        )
        m.add_element(s1)
        s2 = StateVariableLayoutBuilder(
            width=auxiliary_unit_width * scale,
            height=auxiliary_unit_height * scale,
            position=m.self_angle(50),
        )
        m.add_element(s2)
        u1 = UnitOfInformationLayoutBuilder(
            width=auxiliary_unit_width * scale,
            height=auxiliary_unit_height * scale,
            position=m.south(),
        )
        m.add_element(u1)
    return m


def make_toy_arc(
    cls,
    start_point,
    end_point,
    scale,
    make_auxiliary=False,
    auxiliary_unit_width=19,
    auxiliary_unit_height=8,
):
    if not issubclass(cls, momapy.builder.Builder):
        cls = momapy.builder.get_or_make_builder_cls(cls)
    m = cls()
    if m.width is None:
        m.width = 30
    if m.height is None:
        m.height = 30
    if m.arrowhead_fill is None:
        m.arrowhead_fill = momapy.coloring.white
    if m.stroke is None:
        m.stroke = momapy.coloring.black
    if m.stroke_width is None:
        m.stroke_width = 1.0
    m.width = m.width * scale
    m.height = m.height * scale
    m.stroke_width = m.stroke_width * scale
    m.segments = momapy.core.TupleBuilder(
        [momapy.geometry.Segment(start_point, end_point)]
    )
    if make_auxiliary:
        UnitOfInformationLayoutBuilder = momapy.builder.get_or_make_builder_cls(
            momapy.sbgn.pd.UnitOfInformationLayout
        )
        u1 = UnitOfInformationLayoutBuilder(
            width=auxiliary_unit_width * scale,
            height=auxiliary_unit_height * scale,
        )
        momapy.positioning.set_fraction_of(u1, m, 0.5, "south")
        m.add_element(u1)
    return m


def show_room(cls, type_="anchor"):
    WIDTH = 450
    HEIGHT = 300
    POSITION = momapy.geometry.PointBuilder(WIDTH / 2, HEIGHT / 2)
    START_POINT = POSITION - (100, -100)
    END_POINT = POSITION + (100, -100)
    FONT_SIZE = 12
    NODE_DISTANCE = 6
    ARC_DISTANCE = 12
    CROSS_SIZE = 12
    NODE_ANCHORS = {
        "north_west": "south_east",
        "north": "south",
        "north_east": "south_west",
        "east": "west",
        "south_east": "north_west",
        "south": "north",
        "south_west": "north_east",
        "west": "east",
        "center": "center",
        "label_center": "label_center",
    }
    ARC_ANCHORS = {
        "arrowhead_base": "north_west",
        "arrowhead_tip": "north_west",
        "start_point": "north_west",
        "end_point": "south_east",
    }

    ANGLE_STEP = 15
    FRACTION_STEP = 0.1
    AUXILIARY_UNIT_WIDTH = 18
    AUXILIARY_UNIT_HEIGHT = 9
    CrossPointBuilder = momapy.builder.get_or_make_builder_cls(
        momapy.meta.nodes.CrossPoint
    )
    if momapy.builder.issubclass_or_builder(cls, momapy.core.Node):
        SCALE = 5.0
        if cls in [
            momapy.sbgn.pd.MacromoleculeLayout,
            momapy.sbgn.pd.SimpleChemicalLayout,
            momapy.sbgn.pd.ComplexLayout,
            momapy.sbgn.pd.NucleicAcidFeatureLayout,
            momapy.sbgn.pd.MacromoleculeMultimerLayout,
            momapy.sbgn.pd.SimpleChemicalMultimerLayout,
            momapy.sbgn.pd.ComplexMultimerLayout,
            momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout,
        ]:
            make_auxiliary = True
        else:
            make_auxiliary = False
        m = make_toy_node(cls, POSITION, SCALE, make_auxiliary)
        if type_ == "anchor":
            l = NODE_ANCHORS.keys()
        elif type_ == "angle" or type_ == "self_angle":
            l = range(0, 360, ANGLE_STEP)
        for i, elem in enumerate(l):
            if type_ == "anchor":
                position = getattr(m, elem)()
                text = elem
            elif type_ == "angle":
                position = m.angle(elem)
                text = str(elem)
            elif type_ == "self_angle":
                position = m.self_angle(elem)
                text = str(elem)
            cross = CrossPointBuilder(
                width=CROSS_SIZE,
                height=CROSS_SIZE,
                position=position,
                stroke_width=1.5,
                stroke=momapy.coloring.red,
                label=momapy.core.TextLayoutBuilder(
                    text=text,
                    font_family="Arial",
                    font_size=FONT_SIZE,
                ),
            )
            if type_ == "anchor":
                if elem == "label_center":
                    func_name = "set_below_left_of"
                    attach = "north_east"
                elif elem == "center":
                    func_name = "set_above_right_of"
                    attach = "south_west"
                else:
                    func_name = "set_{}_of".format(
                        elem.replace("north", "above")
                        .replace("east", "right")
                        .replace("south", "below")
                        .replace("west", "left")
                    )
                    attach = NODE_ANCHORS[elem]
            elif type_ == "self_angle" or type_ == "angle":
                if i % 2 == 0:
                    func_name = "set_above_right_of"
                    attach = "south_west"
                else:
                    func_name = "set_below_right_of"
                    attach = "north_west"
            getattr(momapy.positioning, func_name)(
                cross.label, cross, NODE_DISTANCE, anchor=attach
            )
            m.add_element(cross)

    elif momapy.builder.issubclass_or_builder(cls, momapy.core.Arc):
        SCALE = 3.0
        make_auxiliary = True
        m = make_toy_arc(cls, START_POINT, END_POINT, SCALE, make_auxiliary)
        if type_ == "anchor":
            l = ARC_ANCHORS.keys()
        elif type_ == "fraction":
            l = numpy.arange(0, 1.1, FRACTION_STEP)
        for i, elem in enumerate(l):
            if type_ == "anchor":
                position = getattr(m, elem)()
                text = elem
            elif type_ == "fraction":
                position, _ = m.fraction(elem)
                text = str(round(elem, 2))
            cross = CrossPointBuilder(
                width=CROSS_SIZE,
                height=CROSS_SIZE,
                position=position,
                stroke_width=1.5,
                stroke=momapy.coloring.red,
                label=momapy.core.TextLayoutBuilder(
                    text=text,
                    font_family="Arial",
                    font_size=FONT_SIZE,
                ),
            )
            if type_ == "anchor":
                attach = ARC_ANCHORS[elem]
                func_name = (
                    NODE_ANCHORS[attach]
                    .replace("north", "above")
                    .replace("east", "right")
                    .replace("south", "below")
                    .replace("west", "left")
                )
                func_name = f"set_{func_name}_of"
            elif type_ == "fraction":
                attach = "north_west"
                func_name = "set_below_right_of"
            getattr(momapy.positioning, func_name)(
                cross.label, cross, ARC_DISTANCE, anchor=attach
            )
            m.add_element(cross)

    display(m)


def macromolecule_toy():
    m = make_toy_node(
        momapy.sbgn.pd.MacromoleculeLayout,
        momapy.geometry.Point(225, 150),
        5,
        True,
    )
    return m


def complex_multimer_toy():
    m = make_toy_node(
        momapy.sbgn.pd.ComplexMultimerLayout,
        momapy.geometry.Point(225, 150),
        5,
        True,
    )
    return m


def production_toy():
    m = make_toy_arc(
        momapy.sbgn.pd.ProductionLayout,
        momapy.geometry.Point(125, 250),
        momapy.geometry.Point(325, 50),
        3.0,
        True,
    )
    return m
