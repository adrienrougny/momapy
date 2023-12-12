from momapy.drawing import Rectangle
from momapy.coloring import colors
from momapy.rendering import render_drawing_elements
from momapy.geometry import Point


rectangle = Rectangle(
    stroke=colors.red,
    fill=colors.blue,
    point=Point(50, 50),
    height=50,
    width=100,
    rx=10,
    ry=10
)

render_drawing_elements([rectangle], "rectangle.pdf", 500, 500)
