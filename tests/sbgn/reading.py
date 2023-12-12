#!python

import momapy.io
import momapy.sbgn.io.sbgnml
import momapy.sbgn.utils
import momapy.rendering.core
import momapy.rendering.skia
import momapy.styling
import momapy.sbgn.styling

m = momapy.io.read(
    "annotations.sbgn",
    return_builder=True,
)

momapy.rendering.core.render_map(m, "reading.pdf", to_top_left=True)

for entity_pool in m.model.entity_pools:
    for annotation in entity_pool.annotations:
        print(annotation)
