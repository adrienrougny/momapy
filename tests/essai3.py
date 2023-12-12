import cairo
import skia

from momapy.shapes import *
from momapy.arcs import *
from momapy.renderer import *
from momapy.geometry import *
from momapy.types import *
from momapy.positioning import *
from momapy.color import *

@dataclass
class Drawer(object):
    renderer: Renderer

    def draw_rectangle(self, position, width, height, line_width=0.4, stroke=rgba(0, 0, 0, 1), fill=rgba(255, 255, 255, 1), text=None, font_description="Arial 6", font_color=rgba(0, 0, 0, 1), anchor="center"):
        if isinstance(position, Point):
            pass
        elif isinstance(position, tuple):
            if isinstance(position[0], Point):
                anchor = position[1]
                position = position[0]
            else:
                position = Point(*position)
        else:
            raise TypeError
        if text is None:
            label = None
        else:
            label = NodeLayoutElementLabel(id="label", text=text, position=position, width=width, height=height, font_description=font_description, font_color=font_color)
        rectangle = Rectangle(id="rectangle", position=position, width=width, height=height, line_width=line_width, stroke=stroke, fill=fill, label=label, anchor=anchor)

        self.renderer._render_layout_element(rectangle)
        return rectangle

    def draw_arc(self, start, end, line_width=0.4, stroke=rgba(0, 0, 0, 1)):
        angle1 = get_angle_of_line(Line(start.center, end.center))
        angle2 = get_angle_of_line(Line(end.center, start.center))
        start_point = start.angle(angle1, unit="radians")
        end_point = end.angle(angle2, unit="radians")
        arc = Arrow(id="arc", points=[start_point, end_point], line_width=line_width, stroke=stroke)
        self.renderer._render_layout_element(arc)
        return arc

def get_cairo_drawer(width, height, fname):
    surface = cairo.PDFSurface(fname, width, height)
    renderer = CairoRenderer(surface=surface, width=width, height=height)
    return Drawer(renderer)

HEIGHT = 200
WIDTH = 200
FNAME = "essai.pdf"
drawer = get_cairo_drawer(WIDTH, HEIGHT, FNAME)
recA = drawer.draw_rectangle((50, 50), 40, 20, text="AAA")
recB = drawer.draw_rectangle((130, 70), 40, 20, fill=rgb(200, 200, 200), text="BBB")
# recA = drawer.draw_rectangle((70, 30), 40, 20, stroke=None, fill=(0, 0, 1), text="A B C", anchor="north_west", font="Arial 12")
# recB = drawer.draw_rectangle((100, 70), 40, 20, text="B", font_color=(1, 1, 0))
# recC = drawer.draw_rectangle(below_right_of(recB, 20), 40, 20, fill_color=(0, 1, 1), text="C")
arc = drawer.draw_arc(recA, recB)
