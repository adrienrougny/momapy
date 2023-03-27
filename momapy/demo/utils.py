import IPython.display
import skia

import momapy.rendering.skia
import momapy.geometry
import momapy.builder
import momapy.core
import momapy.drawing


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


def show_room(cls, type_="anchor"):
    WIDTH = 450
    HEIGHT = 300
    POSITION = momapy.geometry.PointBuilder(WIDTH / 2, HEIGHT / 2)
    SCALE = 5
    FONT_SIZE = 12
    DISTANCE = 6
    CROSS_SIZE = 12
    ANCHORS = {
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
    ANGLE_STEP = 15
    AUXILLIARY_UNIT_WIDTH = 18
    AUXILLIARY_UNIT_HEIGHT = 9
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
    m.position = POSITION
    m.width = m.width * SCALE
    m.height = m.height * SCALE
    for attr in ["offset", "left_connector_length", "right_connector_length"]:
        if hasattr(m, attr):
            setattr(m, attr, getattr(m, attr) * SCALE)
    if type_ == "angle":
        StateVariableLayoutBuilder = momapy.builder.get_or_make_builder_cls(
            momapy.sbgn.pd.StateVariableLayout
        )
        UnitOfInformationLayoutBuilder = momapy.builder.get_or_make_builder_cls(
            momapy.sbgn.pd.UnitOfInformationLayout
        )
        s1 = StateVariableLayoutBuilder(
            width=AUXILLIARY_UNIT_WIDTH * SCALE,
            height=AUXILLIARY_UNIT_HEIGHT * SCALE,
            position=m.self_angle(130),
        )
        m.add_element(s1)
        s2 = StateVariableLayoutBuilder(
            width=AUXILLIARY_UNIT_WIDTH * SCALE,
            height=AUXILLIARY_UNIT_HEIGHT * SCALE,
            position=m.self_angle(50),
        )
        m.add_element(s2)
        u1 = UnitOfInformationLayoutBuilder(
            width=AUXILLIARY_UNIT_WIDTH * SCALE,
            height=AUXILLIARY_UNIT_HEIGHT * SCALE,
            position=m.south(),
        )
        m.add_element(u1)
    CrossPointBuilder = momapy.builder.get_or_make_builder_cls(
        momapy.shapes.CrossPoint
    )
    if type_ == "anchor":
        l = ANCHORS.keys()
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
                attach = ANCHORS[elem]
        elif type_ == "self_angle" or type_ == "angle":
            if i % 2 == 0:
                func_name = "set_above_right_of"
                attach = "south_west"
            else:
                func_name = "set_below_right_of"
                attach = "north_west"
        getattr(momapy.positioning, func_name)(
            cross.label, cross, DISTANCE, anchor=attach
        )
        m.add_element(cross)
    display(m)
