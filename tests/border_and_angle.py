import math

from momapy.shapes import *
from momapy.geometry import Point, Line
from momapy.rendering import *
from momapy.sbgn.pd import *
from momapy.drawing import *
from momapy.coloring import *


def draw_shape(renderer, shape):
    renderer.render_layout_element(shape)


def draw_line(renderer, line, stroke_width=1, stroke=colors.black):
    path = Path(stroke_width, stroke)
    path += move_to(line.p1)
    path += line_to(line.p2)
    renderer.render_drawing_element(path)


def draw_point(
    renderer,
    point,
    width=8,
    height=8,
    stroke_width=1,
    stroke=colors.black,
):
    path = Path(stroke_width=stroke_width, stroke=stroke)
    path += move_to(point - (width / 2, 0))
    path += line_to(point + (width / 2, 0))
    path += move_to(point - (0, height / 2))
    path += line_to(point + (0, height / 2))
    renderer.render_drawing_element(path)


if __name__ == "__main__":
    renderer = CairoRenderer.factory("border_and_angle.pdf", 5500, 5000, "pdf")
    position = Point(x=4902.0, y=1805.5)
    shape = MacromoleculeLayout(
        id="s145_sa237",
        layout_elements=[],
        stroke=Color(red=0, green=0, blue=0, alpha=1.0),
        stroke_width=1.0,
        fill=Color(red=255, green=255, blue=255, alpha=1.0),
        transform=None,
        filter=None,
        position=Point(x=4902.0, y=1805.5),
        width=70.0,
        height=31.0,
        rounded_corners=10.0,
    )
    draw_shape(renderer, shape)
    # r = 10
    # for i in range(0, 360, 2):
    #     p1 = shape.position + (math.cos(math.radians(i))*r, math.sin(math.radians(i))*r)
    #     draw_point(renderer, p1, stroke=colors.blue, stroke_width=0.4)
    #     line = Line(position, p1)
    #     p2 = shape.border(p1)
    #     draw_point(renderer, p2, stroke=colors.green, stroke_width=0.8)
    #     draw_line(renderer, line, stroke_width=0.4)
    #     # p3 = shape.angle(i)
    #     # draw_point(renderer, p3, stroke=colors.red)
    draw_point(renderer, position, stroke=colors.yellow)
    p1 = Point(x=5236.25, y=1754.0)
    # p1 = Point(x=5236.25, y=1753.0)
    draw_point(renderer, p1, stroke=colors.blue, stroke_width=0.4)
    line = Line(position, p1)
    draw_line(renderer, line, stroke_width=0.4)
    line2 = Line(p1=Point(x=4937.0, y=1800.0), p2=Point(x=4937.0, y=1811.0))
    p2 = shape.border(p1)
    if p2 is not None:
        draw_point(renderer, p2, stroke=colors.blue, stroke_width=0.4)
    draw_line(renderer, line2, stroke=colors.red, stroke_width=1)
