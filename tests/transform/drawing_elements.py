import momapy.drawing
import momapy.rendering.skia

rotation = momapy.geometry.Rotation(90, momapy.geometry.Point(250, 250))

ellipse = momapy.drawing.Ellipse(
    stroke_width=1,
    stroke=momapy.coloring.colors.black,
    rx=100,
    ry=50,
    point=momapy.geometry.Point(250, 250),
    fill=momapy.coloring.colors.aquamarine,
    transform=(),
)

scaling = momapy.geometry.Scaling(1.5, 1.5)

rotated_ellipse = ellipse.transformed(rotation)
scaled_ellipse = ellipse.transformed(scaling)

renderer = momapy.rendering.skia.SkiaRenderer.from_file(
    "drawing_elements.pdf", 500, 500, "pdf"
)


renderer.begin_session()
renderer.render_drawing_element(ellipse.to_path())
renderer.render_drawing_element(rotated_ellipse)
renderer.render_drawing_element(scaled_ellipse)
renderer.end_session()
