import momapy.styling
import momapy.rendering
import momapy.sbgn.io
import momapy.sbgn.utils

file_name = "/home/rougny/code/sbgntikz/converter/examples/sbgnml/activated_stat1alpha_induction_of_the_irf1_gene.sbgn"
# file_name = "/home/rougny/code/sbgntikz/converter/examples/sbgnml/insulin-like_growth_factor_signaling.sbgn"
# file_name = "sbgn/all.sbgn" style_sheet = ["../momapy/sbgn/styling/default.css",
# "../momapy/sbgn/styling/default_colorscheme.css", "../momapy/sbgn/styling/shadows.css"]
style_sheet = ["../momapy/sbgn/styling/vanted.css", "../momapy/sbgn/styling/default_colorscheme.css", "../momapy/sbgn/styling/shadows.css"]

m = momapy.sbgn.io.read_file(file_name=file_name, style_sheet=style_sheet, return_builder=True, tidy=True)
momapy.rendering.render_map(m, "filter.svg", renderer="svg-native", to_top_left=True)
momapy.rendering.render_map(m, "filer.pdf", renderer="cairo", to_top_left=True)
