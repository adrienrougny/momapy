import functools
import time
import math

import glfw
from OpenGL import GL
import skia

import momapy.core
import momapy.builder
import momapy.shapes
import momapy.geometry
import momapy.sbgn.pd
import momapy.sbgn.io
import momapy.rendering.core
import momapy.rendering.cairo
import momapy.rendering.skia

N_ELEMENTS = 1000
ELEMENT_CLASS = momapy.shapes.Stadium
ELEMENT_WIDTH = 50
ELEMENT_HEIGHT = 25
ELEMENT_XSEP = 5
ELEMENT_YSEP = 5
ELEMENT_STROKE = momapy.coloring.colors.black
ELEMENT_STROKE_WIDTH = 2.0
ELEMENT_FILL = momapy.coloring.colors.orange
WITH_LABEL = True
LABEL_FONT = "Arial"
LABEL_SIZE = 10
LABEL_TEXT = "LABEL"

registered = []


def register(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        renderer, begin_session, end_session = func(*args, **kwargs)
        end_time = time.perf_counter()
        building_time = end_time - start_time
        start_time = time.perf_counter()
        begin_session(renderer)
        renderer.render_map(args[0])
        end_session(renderer)
        end_time = time.perf_counter()
        rendering_time = end_time - start_time
        print(f"function {func.__name__} took {rendering_time:.4f} seconds")
        return building_time, rendering_time

    registered.append(wrapper)
    return wrapper


def make_map():
    SBGNPDMapBuilder = momapy.builder.get_or_make_builder_cls(
        momapy.sbgn.pd.SBGNPDMap
    )
    map_ = SBGNPDMapBuilder()
    map_.layout = map_.new_layout()
    n = 0
    n_columns = round(math.sqrt(N_ELEMENTS))
    n_lines = N_ELEMENTS // n_columns
    if N_ELEMENTS % n_columns > 0:
        n_lines += 1
    for i in range(n_lines):
        for j in range(n_columns):
            if n >= N_ELEMENTS:
                break
            element = momapy.builder.get_or_make_builder_cls(ELEMENT_CLASS)()
            element.position = momapy.geometry.PointBuilder(
                j * (ELEMENT_WIDTH + ELEMENT_YSEP) + ELEMENT_WIDTH / 2,
                i * (ELEMENT_HEIGHT + ELEMENT_XSEP) + ELEMENT_HEIGHT / 2,
            )
            element.width = ELEMENT_WIDTH
            element.height = ELEMENT_HEIGHT
            element.stroke = ELEMENT_STROKE
            element.stroke_width = ELEMENT_STROKE_WIDTH
            element.fill = ELEMENT_FILL
            if WITH_LABEL:
                label = momapy.core.TextLayoutBuilder()
                label.text = LABEL_TEXT
                label.font_family = LABEL_FONT
                label.font_size = LABEL_SIZE
                label.position = element.label_center()
                element.label = label
            map_.layout.add_element(element)
            n += 1
    map_.layout.width = (
        n_columns * ELEMENT_WIDTH + (n_columns - 1) * ELEMENT_XSEP
    )
    map_.layout.height = n_lines * ELEMENT_HEIGHT + (n_lines - 1) * ELEMENT_YSEP
    map_.layout.position = momapy.geometry.PointBuilder(
        map_.layout.width / 2, map_.layout.height / 2
    )
    return map_.build()


@register
def render_cairo_pdf(map_):
    renderer = momapy.rendering.cairo.CairoRenderer.from_file(
        "cairo.pdf", map_.layout.width, map_.layout.height, "pdf"
    )
    return renderer, type(renderer).begin_session, type(renderer).end_session


@register
def render_cairo_svg(map_):
    renderer = momapy.rendering.cairo.CairoRenderer.from_file(
        "cairo.svg", map_.layout.width, map_.layout.height, "svg"
    )
    return renderer, type(renderer).begin_session, type(renderer).end_session


@register
def render_cairo_png(map_):
    renderer = momapy.rendering.cairo.CairoRenderer.from_file(
        "cairo.png", map_.layout.width, map_.layout.height, "png"
    )
    return renderer, type(renderer).begin_session, type(renderer).end_session


@register
def render_cairo_ps(map_):
    renderer = momapy.rendering.cairo.CairoRenderer.from_file(
        "cairo.png", map_.layout.width, map_.layout.height, "png"
    )
    return renderer, type(renderer).begin_session, type(renderer).end_session


@register
def render_skia_pdf(map_):
    renderer = momapy.rendering.skia.SkiaRenderer.from_file(
        "skia.pdf", map_.layout.width, map_.layout.height, "pdf"
    )
    return renderer, type(renderer).begin_session, type(renderer).end_session


@register
def render_skia_svg(map_):
    renderer = momapy.rendering.skia.SkiaRenderer.from_file(
        "skia.svg", map_.layout.width, map_.layout.height, "svg"
    )
    return renderer, type(renderer).begin_session, type(renderer).end_session


@register
def render_skia_png(map_):
    renderer = momapy.rendering.skia.SkiaRenderer.from_file(
        "skia.png", map_.layout.width, map_.layout.height, "png"
    )
    return renderer, type(renderer).begin_session, type(renderer).end_session


@register
def render_skia_jpeg(map_):
    renderer = momapy.rendering.skia.SkiaRenderer.from_file(
        "skia.jpeg", map_.layout.width, map_.layout.height, "jpeg"
    )
    return renderer, type(renderer).begin_session, type(renderer).end_session


@register
def render_skia_webp(map_):
    renderer = momapy.rendering.skia.SkiaRenderer.from_file(
        "skia.webp", map_.layout.width, map_.layout.height, "webp"
    )
    return renderer, type(renderer).begin_session, type(renderer).end_session


@register
def render_skia_glfx(map_):
    def end_session(renderer):
        renderer.config["surface"].flushAndSubmit()
        glfw.swap_buffers(window)
        renderer.config["context"].abandonContext()
        glfw.terminate()

    if not glfw.init():
        raise RuntimeError("glfw.init() failed")
    glfw.window_hint(glfw.STENCIL_BITS, 8)
    window = glfw.create_window(
        map_.layout.width, map_.layout.height, "", None, None
    )
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
    config = {"surface": surface, "window": window, "context": context}
    renderer = momapy.rendering.skia.SkiaRenderer(canvas, config)
    return renderer, type(renderer).begin_session, end_session


if __name__ == "__main__":
    print("shape: ", ELEMENT_CLASS, "n: ", N_ELEMENTS)
    map_ = make_map()
    for registered_func in registered:
        registered_func(map_)
