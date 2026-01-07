import copy

import numpy
import functools
import operator
import inspect
import pygments
import pygments.lexers
import pygments.formatters


import IPython.display

import momapy.rendering.svg_native
import momapy.geometry
import momapy.builder
import momapy.core
import momapy.drawing
import momapy.meta.nodes
import momapy.positioning
import momapy.coloring


def display(obj, markers=None, xsep=20.0, ysep=20.0, scale=1.0):
    if markers is None:
        markers = []
    if isinstance(obj, momapy.core.Map):
        layout_element = obj.layout
    else:
        layout_element = obj
    bbox = layout_element.bbox()
    if (
        layout_element.group_transform is not None
        and layout_element.group_transform != momapy.drawing.NoneValue
    ):
        total_transformation = functools.reduce(
            operator.mul, layout_element.group_transform
        )
        bbox = momapy.positioning.fit(
            [
                bbox.north_west().transformed(total_transformation),
                bbox.north_east().transformed(total_transformation),
                bbox.south_west().transformed(total_transformation),
                bbox.south_east().transformed(total_transformation),
            ]
        )
    min_x = bbox.x - bbox.width / 2 - xsep
    min_y = bbox.y - bbox.height / 2 - ysep
    max_x = bbox.x + bbox.width / 2 - min_x + xsep
    max_y = bbox.y + bbox.height / 2 - min_y + ysep
    layout_element = momapy.builder.builder_from_object(layout_element)
    if layout_element.group_transform is None:
        layout_element.group_transform = momapy.core.TupleBuilder()
    translation = momapy.geometry.Translation(-min_x, -min_y)
    layout_element.group_transform.insert(0, translation)
    cp_builder_cls = momapy.builder.get_or_make_builder_cls(
        momapy.meta.nodes.CrossPoint
    )
    if isinstance(markers, momapy.geometry.Point):
        markers = [markers]
    for marker in markers:
        position = marker
        cp = cp_builder_cls(
            width=12.0,
            height=12.0,
            stroke_width=1.5,
            stroke=momapy.coloring.red,
            position=position,
        )
        layout_element.layout_elements.append(cp)
    width = max_x
    height = max_y
    layout_element = momapy.builder.object_from_builder(layout_element)
    renderer = momapy.rendering.svg_native.SVGNativeRenderer(
        svg=momapy.rendering.svg_native.SVGElement(
            name="svg",
            attributes={
                "xmlns": "http://www.w3.org/2000/svg",
                "viewBox": f"0 0 {width} {height}",
                "width": width * scale,
                "height": height * scale,
            },
        )
    )
    renderer.begin_session()
    renderer.render_layout_element(layout_element)
    renderer.end_session()
    svg_string = str(renderer.svg)
    IPython.display.display(IPython.display.SVG(data=svg_string))

    # surface = skia.Surface(
    #     int(max_x),
    #     int(max_y),
    # )
    # canvas = surface.getCanvas()
    # renderer = momapy.rendering.skia.SkiaRenderer(canvas=canvas)
    # renderer.begin_session()
    # renderer.render_layout_element(layout_element)
    # image = surface.makeImageSnapshot()
    # renderer.end_session()
    # png_bytes = image.encodeToData().bytes()
    # IPython.display.display(IPython.display.Image(data=png_bytes))


def display_at(obj, positions):
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
        obj.layout_elements.append(cp)
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
        m.layout_elements.append(s1)
        s2 = StateVariableLayoutBuilder(
            width=auxiliary_unit_width * scale,
            height=auxiliary_unit_height * scale,
            position=m.self_angle(50),
        )
        m.layout_elements.append(s2)
        u1 = UnitOfInformationLayoutBuilder(
            width=auxiliary_unit_width * scale,
            height=auxiliary_unit_height * scale,
            position=m.south(),
        )
        m.layout_elements.append(u1)
    m = momapy.builder.object_from_builder(m)
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
    if hasattr(m, "arrowhead_width"):
        m.arrowhead_width = m.arrowhead_width * scale
    if hasattr(m, "arrowhead_height"):
        m.arrowhead_height = m.arrowhead_height * scale
    if hasattr(m, "arrowhead_triangle_width"):
        m.arrowhead_triangle_width = m.arrowhead_triangle_width * scale
    if hasattr(m, "arrowhead_triangle_height"):
        m.arrowhead_triangle_height = m.arrowhead_triangle_height * scale
    if hasattr(m, "start_arrowhead_width"):
        m.start_arrowhead_width = m.start_arrowhead_width * scale
    if hasattr(m, "start_arrowhead_height"):
        m.start_arrowhead_height = m.start_arrowhead_height * scale
    if hasattr(m, "start_arrowhead_triangle_width"):
        m.start_arrowhead_triangle_width = m.start_arrowhead_triangle_width * scale
    if hasattr(m, "start_arrowhead_triangle_height"):
        m.start_arrowhead_triangle_height = m.start_arrowhead_triangle_height * scale
    if hasattr(m, "end_arrowhead_width"):
        m.end_arrowhead_width = m.end_arrowhead_width * scale
    if hasattr(m, "end_arrowhead_height"):
        m.end_arrowhead_height = m.end_arrowhead_height * scale
    if hasattr(m, "end_arrowhead_triangle_width"):
        m.end_arrowhead_triangle_width = m.end_arrowhead_triangle_width * scale
    if hasattr(m, "end_arrowhead_triangle_height"):
        m.end_arrowhead_triangle_height = m.end_arrowhead_triangle_height * scale
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
        m.layout_elements.append(u1)
    m = momapy.builder.object_from_builder(m)
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
    SINGLE_ARC_ANCHORS = {
        "arrowhead_base": "north_west",
        "arrowhead_tip": "north_west",
        "start_point": "north_west",
        "end_point": "south_east",
    }
    DOUBLE_ARC_ANCHORS = {
        "start_point": "north_west",
        "end_point": "south_east",
        "start_arrowhead_base": "north_west",
        "start_arrowhead_tip": "north_west",
        "end_arrowhead_base": "north_west",
        "end_arrowhead_tip": "north_west",
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
        m = momapy.builder.builder_from_object(m)
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
                    fill=momapy.coloring.red,
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
            m.layout_elements.append(cross)

    elif momapy.builder.issubclass_or_builder(
        cls, (momapy.core.SingleHeadedArc, momapy.core.DoubleHeadedArc)
    ):
        SCALE = 3.0
        make_auxiliary = True
        m = make_toy_arc(cls, START_POINT, END_POINT, SCALE, make_auxiliary)
        m = momapy.builder.builder_from_object(m)
        if type_ == "anchor":
            if momapy.builder.issubclass_or_builder(cls, momapy.core.SingleHeadedArc):
                d = SINGLE_ARC_ANCHORS
                l = SINGLE_ARC_ANCHORS.keys()
            else:
                l = DOUBLE_ARC_ANCHORS.keys()
                d = DOUBLE_ARC_ANCHORS
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
                    fill=momapy.coloring.red,
                ),
            )
            if type_ == "anchor":
                attach = d[elem]
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
            m.layout_elements.append(cross)

    m = momapy.builder.object_from_builder(m)
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


def print_source(obj):
    code = inspect.getsource(obj)
    formatter = pygments.formatters.HtmlFormatter(full=True, style="friendly")
    IPython.display.display(
        IPython.display.HTML(
            pygments.highlight(code, pygments.lexers.PythonLexer(), formatter)
        )
    )
