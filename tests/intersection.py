import math

import momapy.drawing
import momapy.geometry
import momapy.rendering



def draw_circle(renderer, circle, stroke_width=1, stroke=momapy.coloring.colors.black, fill=None):
    circle = momapy.drawing.Ellipse(point=circle.point, rx=circle.radius, ry=circle.radius, stroke_width=stroke_width, stroke=stroke, fill=fill)
    renderer.render_drawing_element(circle)

def draw_ellipse(renderer, ellipse, stroke_width=1, stroke=momapy.coloring.colors.black, fill=None):
    ellipse = momapy.drawing.Ellipse(point=ellipse.point, rx=ellipse.rx, ry=ellipse.ry, stroke_width=stroke_width, stroke=stroke, fill=fill)
    renderer.render_drawing_element(ellipse)

def draw_line(renderer, line, stroke_width=1, stroke=momapy.coloring.colors.black):
    path = momapy.drawing.Path(stroke_width=stroke_width, stroke=stroke)
    path += momapy.drawing.move_to(line.p1)
    path += momapy.drawing.line_to(line.p2)
    renderer.render_drawing_element(path)

def draw_point(renderer, point, width=8, height=8, stroke_width=1, stroke=momapy.coloring.colors.black):
    path = momapy.drawing.Path(stroke_width=stroke_width, stroke=stroke)
    path += momapy.drawing.move_to(point - (width/2, 0))
    path += momapy.drawing.line_to(point + (width/2, 0))
    path += momapy.drawing.move_to(point - (0, height/2))
    path += momapy.drawing.line_to(point + (0, height/2))
    renderer.render_drawing_element(path)

def draw_arc(renderer, arc, stroke_width=1, stroke=momapy.coloring.colors.black):
    path = momapy.drawing.Path(stroke_width=stroke_width, stroke=stroke)
    path += momapy.drawing.move_to(momapy.geometry.Point(0, 0))
    path += momapy.drawing.arc(arc.point, arc.radius, arc.start_angle, arc.end_angle)
    renderer.render_drawing_element(path)

def _draw_intersection(renderer, intersection_func, obj1, obj2, width=8, height=8, stroke_width=1, stroke=momapy.coloring.colors.black):
    intersection = intersection_func(obj1, obj2)
    if intersection is not None:
        for point in intersection:
            draw_point(renderer, point, width=width, height=height, stroke_width=stroke_width, stroke=stroke)

def draw_line_circle_intersection(renderer, line, circle, width=8, height=8, stroke_width=1, stroke=momapy.coloring.colors.black):
    _draw_intersection(renderer, momapy.geometry.get_intersection_of_line_and_circle, line, circle, width, height, stroke_width, stroke)

def draw_line_arc_intersection(renderer, line, arc, width=8, height=8, stroke_width=1, stroke=momapy.coloring.colors.black):
    _draw_intersection(renderer, momapy.geometry.get_intersection_of_line_and_arc, line, arc, width, height, stroke_width, stroke)

def draw_line_ellipse_intersection(renderer, line, ellipse, width=8, height=8, stroke_width=1, stroke=momapy.coloring.colors.black):
    _draw_intersection(renderer, momapy.geometry.get_intersection_of_line_and_ellipse, line, ellipse, width, height, stroke_width, stroke)


if __name__ == "__main__":
    renderer = momapy.rendering.CairoRenderer.factory("intersection.pdf", 300, 300, "pdf")

    line1 = momapy.geometry.Line(momapy.geometry.Point(50, 30), momapy.geometry.Point(130, 280))
    line2 = momapy.geometry.Line(momapy.geometry.Point(130, 110), momapy.geometry.Point(220, 170))
    line3 = momapy.geometry.Line(momapy.geometry.Point(50, 160), momapy.geometry.Point(250, 160))
    circle = momapy.geometry.Circle(momapy.geometry.Point(100, 100), 50)
    arc = momapy.geometry.Arc(momapy.geometry.Point(200, 100), 50, math.pi/4, math.pi)
    ellipse = momapy.geometry.Ellipse(momapy.geometry.Point(110, 210), 100, 50)

    draw_line(renderer, line1, stroke=momapy.coloring.colors.red)
    draw_line(renderer, line2, stroke=momapy.coloring.colors.red)
    draw_line(renderer, line3, stroke=momapy.coloring.colors.red)
    draw_circle(renderer, circle)
    draw_ellipse(renderer, ellipse)
    draw_point(renderer, circle.point, stroke=momapy.coloring.colors.blue)
    draw_arc(renderer, arc)

    draw_line_circle_intersection(renderer, line1, circle, stroke=momapy.coloring.colors.green)
    draw_line_arc_intersection(renderer, line2, arc, stroke=momapy.coloring.colors.green)
    draw_line_ellipse_intersection(renderer, line1, ellipse, stroke=momapy.coloring.colors.green_yellow)
    draw_line_ellipse_intersection(renderer, line3, ellipse, stroke=momapy.coloring.colors.dark_khaki)


        # self._context.translate(ellipse.x, ellipse.y)
        # self._context.scale(ellipse.rx, ellipse.ry)
        # self._context.arc(0, 0, 1, 0, 2 * math.pi)


