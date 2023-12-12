from momapy.rendering import render_layout
from momapy.coloring import colors
from momapy.geometry import Point
from momapy.shapes import Hexagon, Ellipse, Rectangle
from momapy.core import MapLayout, NodeLayoutElementLabel

elements = []

shape = Hexagon(
    height=100,
    width=200,
    stroke_width=1,
    position=Point(150, 150),
    stroke=colors.red,
    fill=colors.light_grey,
)

elements.append(shape)

for anchor in [
    "center",
    "south",
    "east",
    "north",
    "west",
    "north_west",
    "north_east",
    "south_east",
    "south_west",
]:
    anchor_shape = Ellipse(
        width=5,
        height=5,
        stroke_width=1,
        stroke=colors.green,
        fill=None,
        position=getattr(shape, anchor)(),
    )
    anchor_text = NodeLayoutElementLabel(
        text=anchor,
        position=anchor_shape.position + (12, -7),
        width=20,
        height=20,
        font_description="Arial 5",
    )
    elements.append(anchor_shape)
    elements.append(anchor_text)

layout = MapLayout(width=500, height=500, layout_elements=tuple(elements))

render_layout(layout, "shapes.pdf")
