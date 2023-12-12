import glfw
from OpenGL import GL
import skia

import momapy.rendering.skia
import momapy.sbgn.io

WIDTH, HEIGHT = 640, 480


if __name__ == "__main__":

    if not glfw.init():
        raise RuntimeError("glfw.init() failed")
    glfw.window_hint(glfw.STENCIL_BITS, 8)
    window = glfw.create_window(WIDTH, HEIGHT, "", None, None)
    glfw.make_context_current(window)
    context = skia.GrDirectContext.MakeGL()
    fb_width, fb_height = glfw.get_framebuffer_size(window)
    backend_render_target = skia.GrBackendRenderTarget(
        fb_width,
        fb_height,
        0,  # sampleCnt
        0,  # stencilBits
        skia.GrGLFramebufferInfo(0, GL.GL_RGBA8),
    )
    surface = skia.Surface.MakeFromBackendRenderTarget(
        context,
        backend_render_target,
        skia.kBottomLeft_GrSurfaceOrigin,
        skia.kRGBA_8888_ColorType,
        skia.ColorSpace.MakeSRGB(),
    )
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    canvas = surface.getCanvas()
    renderer = momapy.rendering.skia.SkiaRenderer(canvas)
    map_ = momapy.sbgn.io.read_file(
        "/home/rougny/code/sbgntikz/converter/examples/sbgnml/activated_stat1alpha_induction_of_the_irf1_gene.sbgn",
        return_builder=True,
    )
    renderer.begin_session()
    renderer.render_map(map_)
    renderer.end_session()
    surface.flushAndSubmit()
    glfw.swap_buffers(window)
    l1 = map_.layout.layout_elements[0]
    while True:
        if l1.fill == momapy.coloring.colors.red:
            l1.fill = momapy.coloring.colors.yellow
        else:
            l1.fill = momapy.coloring.colors.red
        renderer.begin_session()
        renderer.render_map(map_)
        renderer.end_session()
        surface.flushAndSubmit()
        glfw.swap_buffers(window)

    context.abandonContext()
    glfw.terminate()
