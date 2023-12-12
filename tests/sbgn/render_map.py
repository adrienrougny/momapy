#!python

import sys

import momapy.io
import momapy.sbgn.io.sbgnml
import momapy.rendering.core
import momapy.rendering.skia
import momapy.coloring
import momapy.sbgn.styling

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    m = momapy.io.read(
        input_file,
        return_builder=True,
    )
    momapy.rendering.core.render_map(
        m, output_file, format_="pdf", renderer="skia", to_top_left=True
    )
