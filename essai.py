import cairo

from momapy.shapes import Rectangle
from momapy.arcs import Arrow
from momapy.rendering import CairoRenderer
from momapy.coloring import *
from momapy.geometry import Point
from momapy.builder import get_or_make_builder_cls, LayoutBuilder
from momapy.positioning import fit, right_of, set_position_at, set_position_at_fraction_of
from momapy.core import LayoutElementReference, NodeLayoutElementLabel
from momapy.drawing import rotate, translate

OUTPUT = "essai.pdf"
WIDTH = 400
HEIGHT = 400

RectangleBuilder = get_or_make_builder_cls(Rectangle)
ArrowBuilder = get_or_make_builder_cls(Arrow)

l = LayoutBuilder()
r1 = RectangleBuilder(position=Point(100, 50), width=100, height=50, fill=colors.dark_magenta)
# r1_label = NodeLayoutElementLabel(text="ABC", position=r1.position, width=r1.width, height=r1.height)
# r1.label = r1_label

r2 = RectangleBuilder(width=20, height=10, fill=colors.crimson)
set_position_at(r2, r1.north(), anchor="south")

r3 = RectangleBuilder(position=Point(300, 100), width=100, height=50, fill=colors.yellow_green)
# r3_label = NodeLayoutElementLabel(text="DEF", position=r3.position, width=r3.width, height=r3.height)
# r3.label = r3_label



r1.add_element(r2)

a = ArrowBuilder()
a.source = r1
a.target = r3
a.points.append(r1.border(r3.center()))
a.points.append(r3.border(r1.center()))
#
# r4 = RectangleBuilder(width=20, height=10, fill=colors.sky_blue)
# set_position_at_fraction_of(r4, a, 0.5, anchor="south")
# a.add_element(r4)


l.add_element(a)
l.fill = colors.wheat
l.stroke_width = 10
l.stroke = colors.chartreuse

# bbox = fit(l.flatten_group_layout_elements() + [Point(0, 0)], xsep=40, ysep=40)
# l.width = bbox.width
# l.height = bbox.height

l.width = WIDTH
l.height = HEIGHT

surface = cairo.PDFSurface(OUTPUT, l.width, l.height)
renderer = CairoRenderer(surface=surface, width=l.width, height=l.height)

renderer.render_layout_element(l)

for angle in range(20, 180, 20):
    print(angle)
    a.transform = (rotate(angle / 360 * 2 * 3.14159),)
    renderer.render_layout_element(a)
