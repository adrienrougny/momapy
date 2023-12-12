from momapy.rendering import render_drawing_elements
from momapy.drawing import Ellipse
from momapy.geometry import Point
from momapy.coloring import colors


e = Ellipse(stroke_width=2, point=Point(150, 150), rx=100, ry=50, stroke=colors.red, fill=colors.blue)

render_drawing_elements([e], "ellipse.pdf", 500, 500)