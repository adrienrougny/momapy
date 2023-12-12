#!python

import sys

import momapy.io
import momapy.sbgn.io.sbgnml
import momapy.rendering.core
import momapy.rendering.skia
import momapy.styling
import momapy.sbgn.styling

m = momapy.io.read("all_pd.sbgn", return_builder=True, dynamic=True)
momapy.rendering.core.render_map(m, "monitoring1.pdf")
momapy.styling.apply_style_sheet(m.layout, momapy.sbgn.styling.vanted)
momapy.rendering.core.render_map(m, "monitoring2.pdf")
