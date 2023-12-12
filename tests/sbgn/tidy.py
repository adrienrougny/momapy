#!python

import momapy.io
import momapy.sbgn.io.sbgnml
import momapy.sbgn.utils
import momapy.rendering.core
import momapy.rendering.skia
import momapy.styling
import momapy.sbgn.styling

m = momapy.io.read(
    # "maps/central_plant_metabolism.sbgn",
    "tidy.sbgn",
    return_builder=True,
)
momapy.rendering.core.render_map(m, "tidy_1.pdf")
momapy.styling.apply_style_sheet(m.layout, momapy.sbgn.styling.vanted)
momapy.sbgn.utils.vanted_tidy(m)
momapy.rendering.core.render_map(m, "tidy_2.pdf")
momapy.styling.apply_style_sheet(m.layout, momapy.sbgn.styling.newt)
momapy.sbgn.utils.newt_tidy(m)
momapy.rendering.core.render_map(m, "tidy_3.pdf")
