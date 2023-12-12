#!python

import momapy.io
import momapy.sbgn.io.sbgnml
import momapy.sbgn.utils
import momapy.rendering.core
import momapy.rendering.skia
import momapy.styling
import momapy.sbgn.styling

m = momapy.io.read(
    "all_pd.sbgn",
    return_builder=True,
)

momapy.rendering.core.render_map(m, "writing_input.pdf", to_top_left=True)
momapy.io.write(m, "writing_output.sbgn", "sbgnml", with_annotations=True)
m = momapy.io.read(
    "writing_output.sbgn",
    return_builder=True,
)
momapy.rendering.core.render_map(m, "writing_output.pdf", to_top_left=True)
