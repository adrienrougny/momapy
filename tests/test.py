import math

from momapy.geometry import Point
from momapy.rendering import *
from momapy.sbgn.pd import *
from momapy.drawing import *
from momapy.builder import *

def draw_shape(renderer, shape):
    renderer.render_layout_element(shape)

def draw_line(renderer, line, stroke_width=1, stroke=momapy.coloring.colors.black):
    path = Path(stroke_width, stroke)
    path += move_to(line.p1)
    path += line_to(line.p2)
    renderer.render_drawing_element(path)

def draw_point(renderer, point, width=8, height=8, stroke_width=1, stroke=momapy.coloring.colors.black):
    path = Path(stroke_width=stroke_width, stroke=stroke)
    path += move_to(point - (width/2, 0))
    path += line_to(point + (width/2, 0))
    path += move_to(point - (0, height/2))
    path += line_to(point + (0, height/2))
    renderer.render_drawing_element(path)

if __name__ == "__main__":
    renderer = CairoRenderer.factory("test.pdf", 600, 600, "pdf")
