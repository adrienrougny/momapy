from momapy.builder import get_or_make_builder_cls, updated_object, LayoutBuilder, NodeLayoutElementLabelBuilder, Builder
from momapy.shapes import Rectangle
from momapy.geometry import Point
from momapy.rendering import render_layout
from momapy.coloring import colors

RectangleBuilder = get_or_make_builder_cls(Rectangle)

layout = LayoutBuilder(width=500, height=500)
r1 = RectangleBuilder(position=Point(100, 100), height=50, width=100, stroke=colors.black)
layout.add_element(r1)
label = NodeLayoutElementLabelBuilder(text="ABC")
label.width = r1.width
label.height = r1.height
label.position = updated_object(r1, "position")
r1.label = label
r1.position += Point(100, 100)
print(type(label.position))
print(label.position.__class__)
render_layout(layout, "essai_updated_object.pdf")
