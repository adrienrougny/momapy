import momapy.styling
import momapy.rendering
import momapy.sbgn.io
import momapy.sbgn.utils

# m = momapy.sbgn.io.read_file("sbgn/all.sbgn", return_builder=True, tidy=False)
m = momapy.sbgn.io.read_file(
    "sbgn/all.sbgn",
    return_builder=True,
    style_sheet=[
        "../momapy/sbgn/styling/default.css",
        "../momapy/sbgn/styling/default_colorscheme.css",
        "../momapy/sbgn/styling/shadows.css",
    ],
    tidy=True,
)
momapy.rendering.render_map(
    m, "styling_parser.svg", renderer="svg-native", to_top_left=True
)
momapy.rendering.render_map(
    m, "styling_parser.pdf", renderer="cairo", to_top_left=True
)
