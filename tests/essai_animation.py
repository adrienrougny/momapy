from momapy.shapes import Rectangle
from momapy.coloring import *
from momapy.drawing import *
from momapy.animating import Animator
from momapy.geometry import Point
from momapy.builder import *
from momapy.positioning import *

OUTPUT = "essai.mp4"
WIDTH = 1920
HEIGHT = 1080

RectangleBuilder = get_or_make_builder_cls(Rectangle)

l = LayoutBuilder(fill=colors.white, stroke=colors.white, stroke_width=3)
r1 = RectangleBuilder(position=Point(100, 100), width=100, height=50, fill=colors.red)
lab = NodeLayoutElementLabelBuilder(text="ABC", position=updated_object(r1, "position"), width=updated_object(r1, "width"), height=r1.height)
r1.label = lab
print(isinstance(lab.width, (int, float,)))

l.add_element(r1)

l.width = WIDTH
l.height = HEIGHT

animator = Animator(l)
for i in range(300):
    set_position_at(r1, Point(i * 10, 100), anchor="north_west")
    transform = (rotate(i * 3 * 3.14159 / 360, r1.position),)
    r1.transform = transform
    # r1.fill = r1.fill | i / 3
    animator.mseconds(20)

animator.build(OUTPUT)
