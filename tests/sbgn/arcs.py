import momapy.sbgn.pd
import momapy.sbgn.af
import momapy.utils

WIDTH = 60
HEIGHT = 60

arcs_configs = [
    (
        momapy.sbgn.pd.ConsumptionLayout,
        {},
    ),
    (
        momapy.sbgn.pd.ProductionLayout,
        {
            "arrowhead_width": 10.0,
            "arrowhead_height": 10.0,
        },
    ),
    (
        momapy.sbgn.pd.ModulationLayout,
        {
            "arrowhead_width": 10.0,
            "arrowhead_height": 10.0,
        },
    ),
    (
        momapy.sbgn.pd.StimulationLayout,
        {
            "arrowhead_width": 10.0,
            "arrowhead_height": 10.0,
        },
    ),
    (
        momapy.sbgn.pd.NecessaryStimulationLayout,
        {
            "arrowhead_triangle_width": 10.0,
            "arrowhead_triangle_height": 10.0,
            "arrowhead_sep": 4.0,
            "arrowhead_bar_height": 15.0,
        },
    ),
    (
        momapy.sbgn.pd.CatalysisLayout,
        {
            "arrowhead_width": 10.0,
            "arrowhead_height": 10.0,
        },
    ),
    (
        momapy.sbgn.pd.InhibitionLayout,
        {
            "arrowhead_stroke_width": 1.5,
            "arrowhead_height": 10.0,
        },
    ),
    (
        momapy.sbgn.pd.LogicArcLayout,
        {},
    ),
    (
        momapy.sbgn.pd.EquivalenceArcLayout,
        {},
    ),
    (
        momapy.sbgn.af.UnknownInfluenceLayout,
        {
            "arrowhead_width": 10.0,
            "arrowhead_height": 10.0,
        },
    ),
    (
        momapy.sbgn.af.PositiveInfluenceLayout,
        {
            "arrowhead_width": 10.0,
            "arrowhead_height": 10.0,
        },
    ),
    (
        momapy.sbgn.af.NecessaryStimulationLayout,
        {
            "arrowhead_triangle_width": 10.0,
            "arrowhead_triangle_height": 10.0,
            "arrowhead_sep": 4.0,
            "arrowhead_bar_height": 15.0,
        },
    ),
    (
        momapy.sbgn.af.NegativeInfluenceLayout,
        {
            "arrowhead_stroke_width": 1.5,
            "arrowhead_height": 10.0,
        },
    ),
    (
        momapy.sbgn.af.LogicArcLayout,
        {},
    ),
    (
        momapy.sbgn.af.EquivalenceArcLayout,
        {},
    ),
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
