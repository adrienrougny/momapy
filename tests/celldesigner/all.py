import momapy.celldesigner.io
import momapy.rendering.skia
import momapy.rendering.core

print("RENDERING MAP FROM FILE...")
m = momapy.celldesigner.io.read_file("all.xml")
print("RENDERING MAP...")
momapy.rendering.core.render_map(m, "all.pdf", format_="pdf", renderer="skia")
