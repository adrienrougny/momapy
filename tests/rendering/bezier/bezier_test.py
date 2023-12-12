import momapy.rendering.core
import momapy.rendering.skia
import momapy.drawing
import momapy.coloring
import momapy.arcs
import momapy.shapes


def line_string_to_path(line_string, stroke, stroke_width, fill):
    path = momapy.drawing.Path(
        stroke=stroke, stroke_width=stroke_width, fill=fill
    )
    points = [
        momapy.geometry.Point(coord[0], coord[1])
        for coord in line_string.coords
    ]
    path += momapy.drawing.move_to(points[0])
    for point in points[1:]:
        path += momapy.drawing.line_to(point)
    return path


def bbox_to_rectangle(bbox, stroke, stroke_width, fill):
    rectangle = momapy.drawing.Rectangle(
        stroke=stroke,
        stroke_width=stroke_width,
        fill=fill,
        point=bbox.north_west(),
        width=bbox.width,
        height=bbox.height,
    )
    return rectangle


path1 = momapy.drawing.Path(
    stroke_width=2,
    stroke=momapy.coloring.colors.blue,
    fill=momapy.drawing.NoneValue,
)
path1 += momapy.drawing.move_to(momapy.geometry.Point(10, 200))
path1 += momapy.drawing.curve_to(
    momapy.geometry.Point(210, 10),
    momapy.geometry.Point(10, 10),
    momapy.geometry.Point(210, 10),
)

segment = momapy.geometry.BezierCurve(
    momapy.geometry.Point(10, 200),
    momapy.geometry.Point(210, 10),
    tuple(
        [
            momapy.geometry.Point(10, 10),
            momapy.geometry.Point(210, 10),
        ]
    ),
)

# path2 = line_string_to_path(
#     segment.to_shapely(),
#     momapy.coloring.colors.green,
#     2,
#     momapy.drawing.NoneValue,
# )
#
# bbox = path2.bbox()
# rectangle = bbox_to_rectangle(
#     bbox, momapy.coloring.colors.red, 2, momapy.drawing.NoneValue
# )

arc = momapy.arcs.Arrow(
    stroke=momapy.coloring.colors.brown,
    stroke_width=0.4,
    fill=momapy.drawing.NoneValue,
    segments=tuple([segment]),
)

renderer = momapy.rendering.skia.SkiaRenderer.from_file(
    "bezier.pdf", 400, 400, "pdf"
)
renderer.begin_session()
renderer.render_drawing_element(path1)
renderer.render_layout_element(arc)
# renderer.render_drawing_element(rectangle)
renderer.end_session()
