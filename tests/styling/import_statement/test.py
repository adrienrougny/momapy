import momapy.styling
import momapy.sbgn.io.sbgnml
import momapy.io
import momapy.rendering.skia
import momapy.rendering.core

m = momapy.io.read("test_map.sbgn", return_builder=True)
css = momapy.styling.StyleSheet.from_file("test_css.css")
momapy.styling.apply_style_sheet(m, css)
momapy.rendering.core.render_map(m, "test_map.pdf")
