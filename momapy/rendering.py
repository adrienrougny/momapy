from dataclasses import dataclass, InitVar
from copy import deepcopy
from abc import ABC, abstractmethod
from typing import ClassVar, Optional, Collection
import cairo
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo, Pango, Gtk

import math

import momapy.drawing
import momapy.styling
import momapy.positioning

renderers = {}

def register_renderer(name, renderer_cls):
    renderers[name] = renderer_cls

def _make_renderer_for_render_function(
        output_file, width, height, format_, renderer):
    renderer_cls = renderers.get(renderer)
    if renderer_cls is not None:
        renderer_obj = renderer_cls.factory(
            output_file, width, height, format_)
    else:
        raise ValueError(f"no renderer named {renderer}")
    return renderer_obj

def render_map(
        map_,
        output_file,
        format_="pdf",
        renderer="cairo",
        style_sheet=None,
        to_top_left=False):
    maps = [map_]
    render_maps(maps, output_file, format_, renderer, style_sheet, to_top_left)

def render_maps(
        maps,
        output_file,
        format_="pdf",
        renderer="cairo",
        style_sheet=None,
        to_top_left=False
    ):
    bboxes = [map_.layout.self_bbox() for map_ in maps]
    position, width, height = momapy.positioning.fit(bboxes)
    max_x = position.x + width/2
    max_y = position.y + height/2
    if style_sheet is not None or to_top_left:
        new_maps = []
        for map_ in maps:
            if isinstance(map_, momapy.core.Map):
                new_maps.append(momapy.builder.builder_from_object(map_))
            elif isinstance(map_, momapy.builder.MapBuilder):
                new_maps.append(deepcopy(map_))
        maps = new_maps
    if style_sheet is not None:
        for map_ in maps:
            if (isinstance(style_sheet, Collection) and
                    not isinstance(style_sheet, str)):
                for style_sheet_unit in style_sheet:
                    momapy.styling.apply_style_sheet(
                        map_.layout, style_sheet_unit)
            else:
                momapy.styling.apply_style_sheet(map_.layout, style_sheet)
    if to_top_left:
        min_x = position.x - width/2
        min_y = position.y - height/2
        max_x -= min_x
        max_y -= min_y
        translation = momapy.geometry.Translation(-min_x, -min_y)
        for map_ in maps:
            if map_.layout.transform is None:
                map_.layout.transform = momapy.builder.TupleBuilder()
            map_.layout.transform.append(translation)
    renderer_obj = _make_renderer_for_render_function(
        output_file, max_x, max_y, format_, renderer)
    for map_ in maps:
        renderer_obj.render_map(map_)


@dataclass
class Renderer(ABC):
    default_stroke_width: ClassVar[float] = 1

    @abstractmethod
    def render_map(self, map_):
        pass

    @abstractmethod
    def render_layout_element(self, layout_element):
        pass

    @abstractmethod
    def render_drawing_element(self, drawing_element):
        pass

    @classmethod
    def factory(cls, output_file, width, height, format_):
        pass

@dataclass
class CairoRenderer(Renderer):
    surface: InitVar[Optional[cairo.Surface]] = None
    context: InitVar[Optional[cairo.Context]] = None
    authorize_no_context: InitVar[bool] = False
    width: Optional[float] = None
    height: Optional[float] = None

    @classmethod
    def factory(cls, output_file, width, height, format_):
        surface = cls._make_surface(output_file, width, height, format_)
        renderer_obj = cls(surface=surface)
        return renderer_obj

    @classmethod
    def _make_surface(cls, output_file, width, height, format_):
        if format_ == "pdf":
            return cairo.PDFSurface(output_file, width, height)
        elif format_ == "svg":
            return cairo.SVGSurface(output_file, width, height)

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
        render_function = self._get_drawing_element_render_function(
            drawing_element)
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
        if drawing_element.stroke_width is not None: # not sure, need to check svg spec
            state["stroke_width"] = drawing_element.stroke_width
        return state

    def _set_transform_from_drawing_element(self, drawing_element):
        if drawing_element.transform is not None:
            for transformation in drawing_element.transform:
                self._render_transformation(transformation)

    def _set_new_path(self):
        self._context.new_path()

    def _render_transformation(self, transformation):
        render_transformation_function = \
                self._get_transformation_render_function(transformation)
        render_transformation_function(transformation)

    def _get_transformation_render_function(self, transformation):
        if isinstance(transformation, momapy.geometry.Translation):
            return self._render_translation
        elif isinstance(transformation, momapy.geometry.Rotation):
            return self._render_rotation
        elif isinstance(transformation, momapy.geometry.Scaling):
            return self._render_scaling
        elif isinstance(transformation, momapy.geometry.MatrixTransformation):
            return self._render_matrix_transformation


    def _get_drawing_element_render_function(self, drawing_element):
        if isinstance(drawing_element, momapy.drawing.Group):
            return self._render_group
        elif isinstance(drawing_element, momapy.drawing.Path):
            return self._render_path
        elif isinstance(drawing_element, momapy.drawing.Text):
            return self._render_text
        elif isinstance(drawing_element, momapy.drawing.Ellipse):
            return self._render_ellipse
        elif isinstance(drawing_element, momapy.drawing.Rectangle):
            return self._render_rectangle


    def _stroke_and_fill(self):
        if self._fill is not None:
            self._context.set_source_rgba(
                *self._fill.to_rgba(rgba_range=(0, 1)))
            if self._stroke is not None:
                self._context.fill_preserve()
            else:
                self._context.fill()
        if self._stroke is not None:
            self._context.set_line_width(self._stroke_width)
            self._context.set_source_rgba(
                *self._stroke.to_rgba(rgba_range=(0, 1)))
            self._context.stroke()


    def _render_group(self, group):
        for drawing_element in group.elements:
            self.render_drawing_element(drawing_element)

    def _render_path(self, path):
        for path_action in path.actions:
            self._render_path_action(path_action)
        self._stroke_and_fill()

    def _render_text(self, text):
        pango_layout = PangoCairo.create_layout(self._context)
        pango_font_description = Pango.FontDescription()
        pango_font_description.set_family(text.font_family)
        pango_font_description.set_size(
            Pango.units_from_double(text.font_size))
        pango_layout.set_font_description(pango_font_description)
        pango_layout.set_text(text.text)
        pos = pango_layout.index_to_pos(0)
        Pango.extents_to_pixels(pos)
        x = pos.x
        pango_layout_iter = pango_layout.get_iter()
        y = round(Pango.units_to_double(pango_layout_iter.get_baseline()))
        tx = text.x - x
        ty = text.y - y
        self._context.translate(tx, ty)
        self._context.set_source_rgba(
            *text.font_color.to_rgba(rgba_range=(0, 1)))
        PangoCairo.show_layout(self._context, pango_layout)

    def _render_ellipse(self, ellipse):
        self._context.save()
        self._context.translate(ellipse.x, ellipse.y)
        self._context.scale(ellipse.rx, ellipse.ry)
        self._context.arc(0, 0, 1, 0, 2 * math.pi)
        self._context.close_path()
        self._context.restore()
        self._stroke_and_fill()


    def _render_rectangle(self, rectangle):
        path = rectangle.to_path()
        self._render_path(path)

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
        elif isinstance(path_action, momapy.drawing.Arc):
            return self._render_arc
        elif isinstance(path_action, momapy.drawing.EllipticalArc):
            return self._render_elliptical_arc

    def _render_move_to(self, move_to):
        self._context.move_to(move_to.x, move_to.y)

    def _render_line_to(self, line_to):
        self._context.line_to(line_to.x, line_to.y)

    def _render_close(self, close):
        self._context.close_path()

    def _render_arc(self, arc):
        self._context.arc(
            arc.x,
            arc.y,
            arc.radius,
            arc.start_angle,
            arc.end_angle
        )

    def _render_elliptical_arc(self, elliptical_arc):
        obj = momapy.geometry.EllipticalArc(
            momapy.geometry.Point(
                self._context.get_current_point()[0],
                self._context.get_current_point()[1]
            ),
            elliptical_arc.point,
            elliptical_arc.rx,
            elliptical_arc.ry,
            elliptical_arc.x_axis_rotation,
            elliptical_arc.arc_flag,
            elliptical_arc.sweep_flag
        )
        arc, transformation = obj.to_arc_and_transformation()
        arc = momapy.drawing.Arc(
            arc.point, arc.radius, arc.start_angle, arc.end_angle)
        self._context.save()
        self._render_transformation(transformation)
        self._render_path_action(arc)
        self._context.restore()

    def _render_translation(self, translation):
        self._context.translate(translation.tx, translation.ty)

    def _render_rotation(self, rotation):
        point = rotation.point
        if point is not None:
            self._context.translate(point.x, point.y)
            self._context.rotate(rotation.angle)
            self._context.translate(-point.x, -point.y)
        else:
            self._context.rotate(rotation.angle)

    def _render_scaling(self, scaling):
        self._context.scale(scaling.sx, scaling.sy)

    def _render_matrix_transformation(self, matrix_transformation):
        m = cairo.Matrix(
            xx=matrix_transformation.m[0][0],
            yx=matrix_transformation.m[1][0],
            xy=matrix_transformation.m[0][1],
            yy=matrix_transformation.m[1][1],
            x0=matrix_transformation.m[0][2],
            y0=matrix_transformation.m[1][2]
        )
        self._context.transform(m)


@dataclass
class GTKCairoRenderer(Renderer):
    drawing_area: Gtk.DrawingArea
    width: float
    height: float

    def __post_init__(self):
        self.cairo_renderer = CairoRenderer(
            surface=None,
            context=None,
            authorize_no_context=True,
            width=self.width,
            height=self.height
        )

    def set_context(self, context):
        self.cairo_renderer._context = context

    def render_map(self, map_):
        self.cairo_renderer.render_map(map_)


register_renderer("cairo", CairoRenderer)
register_renderer("gtk-cairo", GTKCairoRenderer)
