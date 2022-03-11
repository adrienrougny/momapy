from dataclasses import dataclass, InitVar
from abc import ABC, abstractmethod
from typing import ClassVar, Optional
import cairo
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo, Pango, Gtk

import math

import momapy.drawing

def render_map(map_, output_file, format_="pdf", renderer="cairo"):
    if renderer == "cairo":
        if format_ == "pdf":
            surface_cls = cairo.PDFSurface
        elif format_ == "svg":
            surface_cls = cairo.SVGSurface
        else:
            raise ValueError(f"unsupported format for the {renderer} renderer")
        surface = surface_cls(output_file, map_.layout.width, map_.layout.height)
        renderer = CairoRenderer(surface=surface, width=map_.layout.width, height=map_.layout.height)
        renderer.render_map(map_)
    else:
        raise ValueError(f"no renderer named {renderer}")

@dataclass
class Renderer(ABC):
    default_stroke_width: ClassVar[float] = 1

    @abstractmethod
    def render_map(self, map_):
        pass

@dataclass
class CairoRenderer(Renderer):
    surface: InitVar[Optional[cairo.Surface]] = None
    context: InitVar[Optional[cairo.Context]] = None
    authorize_no_context: InitVar[bool] = False
    width: Optional[float] = None
    height: Optional[float] = None

    def __post_init__(self, surface, context, authorize_no_context):
        if context is not None:
            self._context = context
        else:
            if surface is not None:
                self._context = cairo.Context(surface)
            elif not authorize_no_context:
                raise ValueError("must provide a context or a surface")
        self._states = []
        self._initialize()

    def _initialize(self):
        self._stroke = None
        self._fill = None
        self._stroke_width = self.default_stroke_width

    def _save(self):
        state = {
            "stroke": self._stroke,
            "fill": self._fill,
            "stroke_width": self._stroke_width,
        }
        self._states.append(state)
        self._context.save()

    def _restore(self):
        state = self._states.pop()
        self._set_state(state)
        self._context.restore()

    def _set_state(self, state):
        for key in state:
            setattr(self, f"_{key}", state[key])

    def render_map(self, map_):
        self.render_layout_element(map_.layout)

    def render_layout_element(self, layout_element):
        drawing_elements = layout_element.drawing_elements()
        if drawing_elements is not None:
            for drawing_element in drawing_elements:
                self.render_drawing_element(drawing_element)

    def render_drawing_element(self, drawing_element):
        self._save()
        self._set_state_from_drawing_element(drawing_element)
        self._set_transform_from_drawing_element(drawing_element)
        self._set_new_path() # context.restore() does not forget the current path
        render_function = self._get_drawing_element_render_function(drawing_element)
        render_function(drawing_element)
        self._restore()

    def _set_state_from_drawing_element(self, drawing_element):
        state = self._get_state_from_drawing_element(drawing_element)
        self._set_state(state)

    def _get_state_from_drawing_element(self, drawing_element):
        state = {}
        if drawing_element.stroke is momapy.drawing.NoneValue:
            state["stroke"] = None
        elif drawing_element.stroke is not None:
            state["stroke"] = drawing_element.stroke
        if drawing_element.fill is momapy.drawing.NoneValue:
            state["fill"] = None
        elif drawing_element.fill is not None:
            state["fill"] = drawing_element.fill
        state["stroke_width"] = drawing_element.stroke_width
        return state

    def _set_transform_from_drawing_element(self, drawing_element):
        if drawing_element.transform is not None:
            for transformation in drawing_element.transform:
                self._render_transformation(transformation)

    def _set_new_path(self):
        self._context.new_path()

    def _render_transformation(self, transformation):
        render_transformation_function = self._get_transformation_render_function(transformation)
        render_transformation_function(transformation)

    def _get_transformation_render_function(self, transformation):
        if isinstance(transformation, momapy.drawing.Translation):
            return self._render_translation
        elif isinstance(transformation, momapy.drawing.Rotation):
            return self._render_rotation

    def _get_drawing_element_render_function(self, drawing_element):
        if isinstance(drawing_element, momapy.drawing.Group):
            return self._render_group
        elif isinstance(drawing_element, momapy.drawing.Path):
            return self._render_path
        elif isinstance(drawing_element, momapy.drawing.Text):
            return self._render_text

    def _render_group(self, group):
        for drawing_element in group.elements:
            self.render_drawing_element(drawing_element)

    def _render_path(self, path):
        for path_action in path.actions:
            self._render_path_action(path_action)
        if self._fill is not None:
            self._context.set_source_rgba(*self._fill.to_rgba(rgba_range=(0, 1)))
            if self._stroke is not None:
                self._context.fill_preserve()
            else:
                self._context.fill()
        if self._stroke is not None:
            self._context.set_line_width(self._stroke_width)
            self._context.set_source_rgba(*self._stroke.to_rgba(rgba_range=(0, 1)))
            self._context.stroke()

    def _render_text(self, text):
        p_layout = PangoCairo.create_layout(self._context)
        p_layout.set_height(text.width)
        p_layout.set_width(text.height)
        p_layout.set_alignment(Pango.Alignment.CENTER)
        p_layout.set_font_description(Pango.FontDescription.from_string(text.font_description))
        p_layout.set_text(text.text)
        pixel_extents = p_layout.get_pixel_extents()[1]
        l_x = pixel_extents.x
        l_y = pixel_extents.y
        l_width = pixel_extents.width
        l_height = pixel_extents.height
        self._context.translate(text.x - l_width / 2 - l_x, self._transform_y_coord(text.y) - l_height / 2)
        self._context.set_source_rgba(*text.font_color.to_rgba(rgba_range=(0, 1)))
        PangoCairo.show_layout(self._context, p_layout)

    def _render_path_action(self, path_action):
        render_function = self._get_path_action_render_function(path_action)
        render_function(path_action)

    def _get_path_action_render_function(self, path_action):
        if isinstance(path_action, momapy.drawing.MoveTo):
            return self._render_move_to
        elif isinstance(path_action, momapy.drawing.LineTo):
            return self._render_line_to
        elif isinstance(path_action, momapy.drawing.Close):
            return self._render_close

    def _render_move_to(self, move_to):
        self._context.move_to(move_to.x, move_to.y)

    def _render_line_to(self, line_to):
        self._context.line_to(line_to.x, line_to.y)

    def _render_close(self, close):
        self._context.close_path()

    def _render_translation(self, translation):
        self._context.translate(translation.tx, translation.ty)

    def _render_rotation(self, rotation):
        self._context.rotate(rotation.angle)

@dataclass
class GTKRenderer(Renderer):
    drawing_area: Gtk.DrawingArea
    width: float
    height: float

    def __post_init__(self):
        self.cairo_renderer = CairoRenderer(surface=None, context=None, authorize_no_context=True, width=self.width, height=self.height)

    def set_context(self, context):
        self.cairo_renderer._context = context

    def render_map(self, map_):
        self.cairo_renderer.render_map(map_)
