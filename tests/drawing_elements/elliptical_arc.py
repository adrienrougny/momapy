from momapy.drawing import Path, elliptical_arc, move_to, line_to
from momapy.coloring import colors
from momapy.rendering import render_drawing_elements
from momapy.geometry import Point


path = Path(stroke=colors.red)
path += move_to(Point(0, 0))
path += line_to(Point(0, 50))
path += line_to(Point(20, 50))
path += elliptical_arc(Point(30, 40), 10, 10, 0, 1, 1)

render_drawing_elements([path], "elliptical_arc.pdf", 100, 100)
