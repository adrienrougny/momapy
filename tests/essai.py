import cairo

from momapy.shapes import Rectangle
from momapy.arcs import Arrow
from momapy.rendering import CairoRenderer
from momapy.coloring import *
from momapy.geometry import Point
from momapy.builder import get_or_make_builder_cls, LayoutBuilder
from momapy.positioning import (
    fit,
    right_of,
    set_position_at,
    set_position_at_fraction_of,
)
from momapy.core import PhantomLayout, NodeLayoutElementLabel
from momapy.drawing import rotate, translate

OUTPUT = "essai.pdf"
WIDTH = 400
HEIGHT = 400

RectangleBuilder = get_or_make_builder_cls(Rectangle)
ArrowBuilder = get_or_make_builder_cls(Arrow)

l = LayoutBuilder(
    fill=colors.light_salmon, stroke=colors.green_yellow, stroke_width=3
)
r1 = RectangleBuilder(
    position=Point(100, 100), width=100, height=50, fill=colors.blue
)
for i in range(0, 360, 10):
    r = RectangleBuilder(
        position=r1.angle(i), width=5, height=5, stroke=colors.red
    )
    r1.add_element(r)

r3 = RectangleBuilder(
    position=Point(300, 300), width=100, height=50, fill=colors.yellow_green
)

a = ArrowBuilder()
a.source = PhantomLayout(layout_element=r1)
a.target = PhantomLayout(layout_element=r3)
a.points.append(r1.border(r3.center()))
a.points.append(r3.border(r1.center()))
r4 = RectangleBuilder(width=20, height=10, fill=colors.sky_blue)
set_position_at_fraction_of(r4, a, 0.5, anchor="south")
a.add_element(r4)

l.add_element(a)
l.add_element(r1)
l.add_element(r3)

l.width = WIDTH
l.height = HEIGHT

surface = cairo.PDFSurface(OUTPUT, l.width, l.height)
renderer = CairoRenderer(surface=surface, width=l.width, height=l.height)

renderer.render_layout_element(l)
