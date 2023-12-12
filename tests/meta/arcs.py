import momapy.meta.arcs
import momapy.utils

WIDTH = 60
HEIGHT = 60

arcs_configs = [
    (
        momapy.meta.arcs.PolyLine,
        {},
    ),
    (
        momapy.meta.arcs.Triangle,
        {},
    ),
    (
        momapy.meta.arcs.ReversedTriangle,
        {},
    ),
    (
        momapy.meta.arcs.Rectangle,
        {},
    ),
    (
        momapy.meta.arcs.Ellipse,
        {},
    ),
    (
        momapy.meta.arcs.Diamond,
        {},
    ),
    (
        momapy.meta.arcs.Bar,
        {},
    ),
    (
        momapy.meta.arcs.ArcBarb,
        {},
    ),
    (
        momapy.meta.arcs.StraightBarb,
        {},
    ),
    (
        momapy.meta.arcs.To,
        {},
    ),
    # (
    #     momapy.meta.arcs.DoubleTriangle,
    #     {
    #     },
    # ),
]

momapy.utils.render_arcs_testing(
    "arcs.pdf",
    arcs_configs,
    WIDTH + 20,
    WIDTH + 20,
    path_stroke=momapy.coloring.black,
    path_stroke_width=1.0,
    path_fill=momapy.drawing.NoneValue,
    arrowhead_stroke=momapy.coloring.black,
    arrowhead_stroke_width=1.0,
)
