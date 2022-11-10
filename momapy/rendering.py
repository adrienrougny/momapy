from dataclasses import dataclass, InitVar
from copy import deepcopy
from abc import ABC, abstractmethod
from typing import ClassVar, Optional, Collection
import cairo
import gi
import skia

gi.require_version("Gtk", "3.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import PangoCairo, Pango, Gtk

import math

import momapy.drawing
import momapy.styling
import momapy.positioning
import momapy.geometry
import momapy.builder

renderers = {}


def register_renderer(name, renderer_cls):
    renderers[name] = renderer_cls


def _make_renderer_for_render_function(
    output_file, width, height, format_, renderer
):
    renderer_cls = renderers.get(renderer)
    if renderer_cls is not None:
        renderer_obj = renderer_cls.factory(output_file, width, height, format_)
    else:
        raise ValueError(f"no renderer named {renderer}")
    return renderer_obj


def render_map(
    map_,
    output_file,
    format_="pdf",
    renderer="cairo",
    style_sheet=None,
    to_top_left=False,
):
    maps = [map_]
    render_maps(maps, output_file, format_, renderer, style_sheet, to_top_left)


def render_maps(
    maps,
    output_file,
    format_="pdf",
    renderer="cairo",
    style_sheet=None,
    to_top_left=False,
):
    bboxes = [map_.layout.self_bbox() for map_ in maps]
    position, width, height = momapy.positioning.fit(bboxes)
    max_x = position.x + width / 2
    max_y = position.y + height / 2
    if style_sheet is not None or to_top_left:
        new_maps = []
        for map_ in maps:
            if isinstance(map_, momapy.core.Map):
                new_maps.append(momapy.builder.builder_from_object(map_))
            elif isinstance(map_, momapy.core.MapBuilder):
                new_maps.append(deepcopy(map_))
        maps = new_maps
    if style_sheet is not None:
        if (
            not isinstance(style_sheet, Collection)
            or isinstance(style_sheet, str)
            or isinstance(style_sheet, momapy.styling.StyleSheet)
        ):
            style_sheets = [style_sheet]
        else:
            style_sheets = style_sheet
        style_sheets = [
            momapy.styling.read_file(style_sheet)
            if not isinstance(style_sheet, momapy.styling.StyleSheet)
            else style_sheet
            for style_sheet in style_sheets
        ]
        style_sheet = momapy.styling.join_style_sheets(style_sheets)
        for map_ in maps:
            momapy.styling.apply_style_sheet(map_.layout, style_sheet)
    if to_top_left:
        min_x = position.x - width / 2
        min_y = position.y - height / 2
        max_x -= min_x
        max_y -= min_y
        translation = momapy.geometry.Translation(-min_x, -min_y)
        for map_ in maps:
            if map_.layout.transform is None:
                map_.layout.transform = momapy.core.TupleBuilder()
            map_.layout.transform.append(translation)
    renderer_obj = _make_renderer_for_render_function(
        output_file, max_x, max_y, format_, renderer
    )
    for map_ in maps:
        renderer_obj.render_map(map_)


@dataclass
class Renderer(ABC):
    default_stroke_width: ClassVar[float] = 1
    default_fill: ClassVar[momapy.coloring.Color] = momapy.coloring.colors.black

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
        self._fill = self.default_fill
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
        self._set_new_path()  # context.restore() does not forget the current path
        render_function = self._get_drawing_element_render_function(
            drawing_element
        )
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
        if (
            drawing_element.stroke_width is not None
        ):  # not sure, need to check svg spec
            state["stroke_width"] = drawing_element.stroke_width
        return state

    def _set_transform_from_drawing_element(self, drawing_element):
        if drawing_element.transform is not None:
            for transformation in drawing_element.transform:
                self._render_transformation(transformation)

    def _set_new_path(self):
        self._context.new_path()

    def _render_transformation(self, transformation):
        render_transformation_function = (
            self._get_transformation_render_function(transformation)
        )
        render_transformation_function(transformation)

    def _get_transformation_render_function(self, transformation):
        if momapy.builder.isinstance_or_builder(
            transformation, momapy.geometry.Translation
        ):
            return self._render_translation
        elif momapy.builder.isinstance_or_builder(
            transformation, momapy.geometry.Rotation
        ):
            return self._render_rotation
        elif momapy.builder.isinstance_or_builder(
            transformation, momapy.geometry.Scaling
        ):
            return self._render_scaling
        elif momapy.builder.isinstance_or_builder(
            transformation, momapy.geometry.MatrixTransformation
        ):
            return self._render_matrix_transformation

    def _get_drawing_element_render_function(self, drawing_element):
        if momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Group
        ):
            return self._render_group
        elif momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Path
        ):
            return self._render_path
        elif momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Text
        ):
            return self._render_text
        elif momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Ellipse
        ):
            return self._render_ellipse
        elif momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Rectangle
        ):
            return self._render_rectangle

    def _stroke_and_fill(self):
        if self._fill is not None:
            self._context.set_source_rgba(
                *self._fill.to_rgba(rgba_range=(0, 1))
            )
            if self._stroke is not None:
                self._context.fill_preserve()
            else:
                self._context.fill()
        if self._stroke is not None:
            self._context.set_line_width(self._stroke_width)
            self._context.set_source_rgba(
                *self._stroke.to_rgba(rgba_range=(0, 1))
            )
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
        pango_font_description.set_absolute_size(
            Pango.units_from_double(text.font_size)
        )
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
        self._context.set_source_rgba(*self._fill.to_rgba(rgba_range=(0, 1)))
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
        if momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.MoveTo
        ):
            return self._render_move_to
        elif momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.LineTo
        ):
            return self._render_line_to
        elif momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.Close
        ):
            return self._render_close
        elif momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.Arc
        ):
            return self._render_arc
        elif momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.EllipticalArc
        ):
            return self._render_elliptical_arc

    def _render_move_to(self, move_to):
        self._context.move_to(move_to.x, move_to.y)

    def _render_line_to(self, line_to):
        self._context.line_to(line_to.x, line_to.y)

    def _render_close(self, close):
        self._context.close_path()

    def _render_arc(self, arc):
        self._context.arc(
            arc.x, arc.y, arc.radius, arc.start_angle, arc.end_angle
        )

    def _render_elliptical_arc(self, elliptical_arc):
        obj = momapy.geometry.EllipticalArc(
            momapy.geometry.Point(
                self._context.get_current_point()[0],
                self._context.get_current_point()[1],
            ),
            elliptical_arc.point,
            elliptical_arc.rx,
            elliptical_arc.ry,
            elliptical_arc.x_axis_rotation,
            elliptical_arc.arc_flag,
            elliptical_arc.sweep_flag,
        )
        arc, transformation = obj.to_arc_and_transformation()
        arc = momapy.drawing.Arc(
            arc.point, arc.radius, arc.start_angle, arc.end_angle
        )
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
            y0=matrix_transformation.m[1][2],
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
            height=self.height,
        )

    def set_context(self, context):
        self.cairo_renderer._context = context

    def render_map(self, map_):
        self.cairo_renderer.render_map(map_)

    def render_layout_element(self, layout_element):
        self.cairo_renderer.render_layout_element(layout_element)

    def render_drawing_element(self, drawing_element):
        self.cairo_renderer.render_drawing_element(drawing_element)


@dataclass
class SVGNativeRenderer(Renderer):
    output_file: str
    width: float
    height: float

    @classmethod
    def factory(cls, output_file, width, height, format_):
        renderer_obj = cls(output_file=output_file, width=width, height=height)
        return renderer_obj

    def render_map(self, map_):
        self.render_layout_element(map_.layout)

    def render_layout_element(self, layout_element):
        s = self._render_layout_element(layout_element)
        self._write_string_to_file(s, self.output_file)

    def render_drawing_element(self, drawing_element):
        s = self._render_drawing_element(drawing_element)
        self._write_string_to_file(s, self.output_file)

    def _render_layout_element(self, layout_element):
        return self._render_svg_top_element(layout_element.drawing_elements())

    def _render_drawing_element(self, drawing_element):
        return self._render_svg_top_element(drawing_element)

    def _render_filters(self, drawing_elements):
        svg_filters = set([])
        for drawing_element in drawing_elements:
            if (
                drawing_element.filter is not None
                and drawing_element.filter is not momapy.drawing.NoneValue
            ):
                svg_filter = self._render_filter(drawing_element.filter)
                svg_filters.add(svg_filter)
            if momapy.builder.momapy.builder.isinstance_or_builder(
                drawing_element,
                momapy.drawing.Group,
            ):
                svg_filters |= self._render_filters(drawing_element.elements)
        return svg_filters

    def _render_svg_top_element(self, drawing_elements):
        name = "svg"
        svg_xmlns = self._render_svg_attribute(
            "xmlns", "http://www.w3.org/2000/svg"
        )
        svg_viewbox = self._render_svg_attribute(
            "viewBox", f"0 0 {self.width} {self.height}"
        )
        svg_attributes = [svg_xmlns, svg_viewbox]
        value = None
        svg_def_element = self._render_svg_element(
            "defs", [], None, self._render_filters(drawing_elements)
        )
        svg_subelements = [svg_def_element]
        svg_subelements += [
            self._render_drawing_element(de) for de in drawing_elements
        ]
        return self._render_svg_element(
            name, svg_attributes, value, svg_subelements
        )

    @classmethod
    def _write_string_to_file(cls, s, file_name):
        with open(file_name, "w") as f:
            f.write(s)

    @classmethod
    def _render_svg_element(
        cls,
        name,
        svg_attributes=None,
        value=None,
        svg_subelements=None,
        indent=0,
    ):
        s = f"{'    ' * indent}<{name}"
        if svg_attributes is not None and svg_attributes:
            s += f" {' '.join(svg_attributes)}"
        s += ">\n"
        if value is not None:
            s += f"{value}\n"
        if svg_subelements is not None and svg_subelements:
            for svg_subelement in svg_subelements:
                s += f"{svg_subelement}\n"
        s += f"{'   ' * indent}</{name}>"
        return s

    @classmethod
    def _quote_string(cls, s, quote='"'):
        return f"{quote}{s}{quote}"

    @classmethod
    def _render_svg_attribute(cls, name, value):
        return f"{name}={cls._quote_string(value)}"

    def _get_transformation_render_function(self, transformation):
        if momapy.builder.isinstance_or_builder(
            transformation, momapy.geometry.Translation
        ):
            return self._render_translation
        elif momapy.builder.isinstance_or_builder(
            transformation, momapy.geometry.Rotation
        ):
            return self._render_rotation
        elif momapy.builder.isinstance_or_builder(
            transformation, momapy.geometry.Scaling
        ):
            return self._render_scaling
        elif momapy.builder.isinstance_or_builder(
            transformation, momapy.geometry.MatrixTransformation
        ):
            return self._render_matrix_transformation

    def _get_filter_effect_render_function(self, filter_effect):
        if momapy.builder.isinstance_or_builder(
            filter_effect, momapy.drawing.DropShadowEffect
        ):
            return self._render_drop_shadow_effect
        elif momapy.builder.isinstance_or_builder(
            filter_effect, momapy.drawing.CompositeEffect
        ):
            return self._render_composite_effect
        elif momapy.builder.isinstance_or_builder(
            filter_effect, momapy.drawing.OffsetEffect
        ):
            return self._render_offset_effect
        elif momapy.builder.isinstance_or_builder(
            filter_effect, momapy.drawing.GaussianBlurEffect
        ):
            return self._render_gaussian_blur_effect
        elif momapy.builder.isinstance_or_builder(
            filter_effect, momapy.drawing.FloodEffect
        ):
            return self._render_flood_effect

    def _get_path_action_render_function(self, path_action):
        if momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.MoveTo
        ):
            return self._render_move_to
        elif momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.LineTo
        ):
            return self._render_line_to
        elif momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.Close
        ):
            return self._render_close
        elif momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.Arc
        ):
            return self._render_arc
        elif momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.EllipticalArc
        ):
            return self._render_elliptical_arc

    def _get_drawing_element_prepare_function(self, drawing_element):
        if momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Group
        ):
            return self._prepare_group
        elif momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Path
        ):
            return self._prepare_path
        elif momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Text
        ):
            return self._prepare_text
        elif momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Ellipse
        ):
            return self._prepare_ellipse
        elif momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Rectangle
        ):
            return self._prepare_rectangle

    def _render_transformation(self, transformation):
        render_transformation_function = (
            self._get_transformation_render_function(transformation)
        )
        s = render_transformation_function(transformation)
        return s

    def _render_translation(self, translation):
        return f"translate({translation.tx} {translation.ty})"

    def _render_rotation(self, rotation):
        angle = math.degrees(rotation.angle)
        s = f"rotate({angle}"
        if rotation.point is not None:
            s += f" {rotation.point.x} {rotation.point.y}"
        s += ")"
        return s

    def _render_scaling(self, scaling):
        return f"scale({scaling.sx} {scaling.sy})"

    def _render_matrix_transformation(self, matrix_transformation):
        values = [
            matrix_transformation.m[i][j]
            for j in range(len(matrix_transformation.m[0]))
            for i in range(len(matrix_transformation.m) - 1)
        ]
        return f"matrix({' '.join(values)})"

    def _render_filter_effect(self, filter_effect):
        render_function = self._get_filter_effect_render_function(filter_effect)
        s = render_function(filter_effect)
        return s

    def _render_drop_shadow_effect(self, filter_effect):
        name = "feDropShadow"
        svg_dx = self._render_svg_attribute("dx", filter_effect.dx)
        svg_dy = self._render_svg_attribute("dy", filter_effect.dy)
        svg_attributes = [svg_dx, svg_dy]
        if filter_effect.result is not None:
            svg_attributes.append(
                self._render_svg_attribute("result", filter_effect.result)
            )
        if filter_effect.std_deviation is not None:
            svg_attributes.append(
                self._render_svg_attribute(
                    "stdDeviation", filter_effect.std_deviation
                )
            )
        if filter_effect.flood_opacity is not None:
            svg_attributes.append(
                self._render_svg_attribute(
                    "flood-opacity", filter_effect.flood_opacity
                )
            )
        if filter_effect.flood_color is not None:
            svg_attributes.append(
                self._render_svg_attribute(
                    "flood-color", self._render_color(filter_effect.flood_color)
                )
            )
        value = None
        svg_subelements = []
        return self._render_svg_element(
            name, svg_attributes, value, svg_subelements
        )

    def _render_composite_effect(self, filter_effect):
        name = "feComposite"
        svg_in = self._render_svg_attribute("in", filter_effect.in_)
        svg_in2 = self._render_svg_attribute("in2", filter_effect.in2)
        svg_operator = self._render_svg_attribute(
            "operator", filter_effect.operator
        )
        svg_attributes = [svg_in, svg_in2, svg_operator]
        if filter_effect.result is not None:
            svg_attributes.append(
                self._render_svg_attribute("result", filter_effect.result)
            )
        value = None
        svg_subelements = []
        return self._render_svg_element(
            name, svg_attributes, value, svg_subelements
        )

    def _render_flood_effect(self, filter_effect):
        name = "feFlood"
        svg_flood_opacity = self._render_svg_attribute(
            "flood-opacity", filter_effect.flood_opacity
        )
        svg_flood_color = self._render_svg_attribute(
            "flood-color", self._render_color(filter_effect.flood_color)
        )
        svg_attributes = [svg_flood_opacity, svg_flood_color]
        if filter_effect.result is not None:
            svg_attributes.append(
                self._render_svg_attribute("result", filter_effect.result)
            )
        value = None
        svg_subelements = []
        return self._render_svg_element(
            name, svg_attributes, value, svg_subelements
        )

    def _render_gaussian_blur_effect(self, filter_effect):
        name = "feGaussianBlur"
        svg_in = self._render_svg_attribute("in", filter_effect.in_)
        svg_std_deviation = self._render_svg_attribute(
            "stdDeviation", filter_effect.std_deviation
        )
        svg_attributes = [svg_in, svg_std_deviation]
        if filter_effect.edge_mode is not None:
            svg_attributes.append(
                self._render_svg_attribute("edgeMode", filter_effect.edge_mode)
            )
        if filter_effect.result is not None:
            svg_attributes.append(
                self._render_svg_attribute("result", filter_effect.result)
            )
        value = None
        svg_subelements = []
        return self._render_svg_element(
            name, svg_attributes, value, svg_subelements
        )

    def _render_offset_effect(self, filter_effect):
        name = "feOffset"
        svg_in = self._render_svg_attribute("in", filter_effect.in_)
        svg_dx = self._render_svg_attribute("dx", filter_effect.dx)
        svg_dy = self._render_svg_attribute("dy", filter_effect.dy)
        svg_attributes = [svg_in, svg_dx, svg_dy]
        if filter_effect.result is not None:
            svg_attributes.append(
                self._render_svg_attribute("result", filter_effect.result)
            )
        value = None
        svg_subelements = []
        return self._render_svg_element(
            name, svg_attributes, value, svg_subelements
        )

    def _render_filter(self, filter):
        name = "filter"
        svg_id_attribute = self._render_svg_attribute("id", filter.id)
        svg_filter_units = self._render_svg_attribute(
            "filterUnits", filter.filter_units
        )
        svg_x = self._render_svg_attribute("x", "-20%")
        svg_y = self._render_svg_attribute("y", "-20%")
        svg_width = self._render_svg_attribute("width", "140%")
        svg_height = self._render_svg_attribute("height", "140%")
        svg_attributes = [
            svg_id_attribute,
            svg_filter_units,
            svg_x,
            svg_y,
            svg_width,
            svg_height,
        ]
        value = None
        svg_subelements = [
            self._render_filter_effect(fe) for fe in filter.effects
        ]
        return self._render_svg_element(
            name, svg_attributes, value, svg_subelements
        )

    def _render_path_action(self, path_action):
        render_function = self._get_path_action_render_function(path_action)
        s = render_function(path_action)
        return s

    def _render_move_to(self, move_to):
        return f"M {move_to.x} {move_to.y}"

    def _render_line_to(self, line_to):
        return f"L {line_to.x} {line_to.y}"

    def _render_close(self, close):
        return "Z"

    def _render_elliptical_arc(self, elliptical_arc):
        return (
            f"A {elliptical_arc.rx} "
            f"{elliptical_arc.ry} "
            f"{elliptical_arc.x_axis_rotation} "
            f"{elliptical_arc.arc_flag} "
            f"{elliptical_arc.sweep_flag} "
            f"{elliptical_arc.x} "
            f"{elliptical_arc.y}"
        )

    def _render_color(self, color):
        return f"rgb({color.red}, {color.green}, {color.blue})"

    def _render_opacity(self, color):
        return str(color.alpha)

    def _render_drawing_element(self, drawing_element):
        prepare_function = self._get_drawing_element_prepare_function(
            drawing_element
        )
        name, svg_attributes, value, svg_subelements = prepare_function(
            drawing_element
        )
        if drawing_element.transform is not None:
            svg_transform_value = " ".join(
                [
                    self._render_transformation(t)
                    for t in drawing_element.transform
                ]
            )
            svg_transform_attribute = self._render_svg_attribute(
                "transform", svg_transform_value
            )
            svg_attributes.append(svg_transform_attribute)
        if drawing_element.stroke is not None:
            if drawing_element.stroke is momapy.drawing.NoneValue:
                svg_stroke_value = "none"
            else:
                svg_stroke_value = self._render_color(drawing_element.stroke)
                svg_stroke_opacity_value = self._render_opacity(
                    drawing_element.stroke
                )
                svg_stroke_opacity_attribute = self._render_svg_attribute(
                    "stroke-opacity", svg_stroke_opacity_value
                )
                svg_attributes.append(svg_stroke_opacity_attribute)
            svg_stroke_attribute = self._render_svg_attribute(
                "stroke", svg_stroke_value
            )
            svg_attributes.append(svg_stroke_attribute)
        if drawing_element.fill is not None:
            if drawing_element.fill is momapy.drawing.NoneValue:
                svg_fill_value = "none"
            else:
                svg_fill_value = self._render_color(drawing_element.fill)
                svg_fill_opacity_value = self._render_opacity(
                    drawing_element.fill
                )
                svg_fill_opacity_attribute = self._render_svg_attribute(
                    "fill-opacity", svg_fill_opacity_value
                )
                svg_attributes.append(svg_fill_opacity_attribute)
            svg_fill_attribute = self._render_svg_attribute(
                "fill", svg_fill_value
            )
            svg_attributes.append(svg_fill_attribute)
        if drawing_element.stroke_width is not None:
            svg_stroke_width_value = drawing_element.stroke_width
            svg_stroke_width_attribute = self._render_svg_attribute(
                "stroke-width", svg_stroke_width_value
            )
            svg_attributes.append(svg_stroke_width_attribute)
        if (
            drawing_element.filter is not None
            and drawing_element.filter is not momapy.drawing.NoneValue
        ):
            svg_filter_value = f"url(#{drawing_element.filter.id})"
            svg_attributes.append(
                self._render_svg_attribute("filter", svg_filter_value)
            )
        s = self._render_svg_element(
            name, svg_attributes, value, svg_subelements
        )
        return s

    def _prepare_group(self, group):
        name = "g"
        svg_attributes = []
        value = None
        svg_subelements = [
            self._render_drawing_element(drawing_element)
            for drawing_element in group.elements
        ]
        return name, svg_attributes, value, svg_subelements

    def _prepare_path(self, path):
        name = "path"
        svg_d_value = " ".join(
            [self._render_path_action(pa) for pa in path.actions]
        )
        svg_d_attribute = self._render_svg_attribute("d", svg_d_value)
        svg_attributes = [svg_d_attribute]
        value = None
        svg_subelements = []
        return name, svg_attributes, value, svg_subelements

    def _prepare_text(self, text):
        name = "text"
        svg_x = self._render_svg_attribute("x", text.x)
        svg_y = self._render_svg_attribute("y", text.y)
        svg_font_size = self._render_svg_attribute("font-size", text.font_size)
        svg_font_family = self._render_svg_attribute(
            "font-family", text.font_family
        )
        svg_attributes = [svg_x, svg_y, svg_font_size, svg_font_family]
        value = text.text
        svg_subelements = []
        return name, svg_attributes, value, svg_subelements

    def _prepare_ellipse(self, ellipse):
        name = "ellipse"
        svg_cx = self._render_svg_attribute("cx", ellipse.x)
        svg_cy = self._render_svg_attribute("cy", ellipse.y)
        svg_rx = self._render_svg_attribute("rx", ellipse.rx)
        svg_ry = self._render_svg_attribute("ry", ellipse.ry)
        svg_attributes = [svg_cx, svg_cy, svg_rx, svg_ry]
        value = None
        svg_subelements = []
        return name, svg_attributes, value, svg_subelements

    def _prepare_rectangle(self, rectangle):
        name = "rect"
        svg_x = self._render_svg_attribute("x", rectangle.x)
        svg_y = self._render_svg_attribute("y", rectangle.y)
        svg_width = self._render_svg_attribute("width", rectangle.width)
        svg_height = self._render_svg_attribute("height", rectangle.height)
        svg_rx = self._render_svg_attribute("rx", rectangle.rx)
        svg_ry = self._render_svg_attribute("ry", rectangle.ry)
        svg_attributes = [svg_x, svg_y, svg_width, svg_height, svg_rx, svg_ry]
        value = None
        svg_subelements = []
        return name, svg_attributes, value, svg_subelements


@dataclass
class SVGNativeCompatRenderer(SVGNativeRenderer):
    def _render_filter(self, filter_):
        filter_ = filter_.to_compat()
        return super()._render_filter(filter_)


class SkiaRenderer(Renderer):
    _canvas: Optional[skia.Canvas] = None
    _document: Optional[skia.Document] = None
    _surface: Optional[skia.Surface] = None
    _output_file: Optional[str] = None
    _format: Optional[str] = None
    _stream: Optional[skia.Stream] = None
    width: Optional[float] = None
    height: Optional[float] = None

    @classmethod
    def factory(cls, output_file, width, height, format_):
        kwargs = cls._make_ini_kwargs(output_file, width, height, format_)
        renderer_obj = cls(**kwargs)
        return renderer_obj

    @classmethod
    def _make_ini_kwargs(cls, output_file, width, height, format_):
        if format_ == "pdf":
            stream = skia.FILEWStream(output_file)
            document = skia.PDF.MakeDocument(stream)
            canvas = document.beginPage(width=width, height=height)
            kwargs = {
                "_document": document,
                "_stream": stream,
            }
        elif format_ == "png":
            surface = skia.Surface(width=int(width), height=int(height))
            canvas = surface.getCanvas()
            kwargs = {
                "_surface": surface,
                "_output_file": output_file,
            }
        elif format_ == "svg":
            stream = skia.FILEWStream(output_file)
            canvas = skia.SVGCanvas.Make((width, height), stream)
            kwargs = {"_stream": stream}
        kwargs["width"] = width
        kwargs["height"] = height
        kwargs["_format"] = format_
        kwargs["_canvas"] = canvas
        return kwargs

    def __post_init__(self, *args):
        self._initialize()

    def _initialize(self):
        self._states = []
        self._stroke = None
        self._fill = self.default_fill
        self._stroke_width = self.default_stroke_width

    def _save(self):
        state = {
            "stroke": self._stroke,
            "fill": self._fill,
            "stroke_width": self._stroke_width,
        }
        self._states.append(state)
        self._canvas.save()

    def _restore(self):
        state = self._states.pop()
        self._set_state(state)
        self._canvas.restore()

    def _set_state(self, state):
        for key in state:
            setattr(self, f"_{key}", state[key])

    def render_map(self, map_):
        self.render_layout_element(map_.layout)
        if self._format == "pdf":
            self._document.endPage()
            self._document.close()
        elif self._format == "png":
            image = self._surface.makeImageSnapshot()
            image.save(self._output_file, skia.kPNG)
        elif self._format == "svg":
            del self._canvas
            self._stream.flush()

    def render_layout_element(self, layout_element):
        drawing_elements = layout_element.drawing_elements()
        if drawing_elements is not None:
            for drawing_element in drawing_elements:
                self.render_drawing_element(drawing_element)

    def render_drawing_element(self, drawing_element):
        self._save()
        self._set_state_from_drawing_element(drawing_element)
        self._set_transform_from_drawing_element(drawing_element)
        render_function = self._get_drawing_element_render_function(
            drawing_element
        )
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
        if (
            drawing_element.stroke_width is not None
        ):  # not sure, need to check svg spec
            state["stroke_width"] = drawing_element.stroke_width
        return state

    def _set_transform_from_drawing_element(self, drawing_element):
        if drawing_element.transform is not None:
            for transformation in drawing_element.transform:
                self._render_transformation(transformation)

    def _set_new_path(self):
        pass

    def _make_stroke_paint(self):
        skia_paint = skia.Paint(
            Color4f=skia.Color4f(self._stroke.to_rgba(rgba_range=(0, 1))),
            StrokeWidth=self._stroke_width,
            Style=skia.Paint.kStroke_Style,
        )
        return skia_paint

    def _make_fill_paint(self):
        skia_paint = skia.Paint(
            Color4f=skia.Color4f(self._fill.to_rgba(rgba_range=(0, 1))),
            Style=skia.Paint.kFill_Style,
        )
        return skia_paint

    def _make_filter_paints_from_filter(self, filter_):
        skia_paints = []
        for filter_effect in filter_.effects:
            render_function = self._get_filter_effect_render_function(
                filter_effect
            )
            skia_paint = render_function(filter_effect)
            skia_paints.append(skia_paint)
        return skia_paints

    def _get_filter_effect_render_function(self, filter_effect):
        if momapy.builder.isinstance_or_builder(
            filter_effect, momapy.drawing.DropShadowEffect
        ):
            return self._render_drop_shadow_effect

    def _render_drop_shadow_effect(self, filter_effect):
        skia_filter = skia.ImageFilters.DropShadow(
            dx=filter_effect.dx,
            dy=filter_effect.dy,
            sigmaX=filter_effect.std_deviation,
            sigmaY=filter_effect.std_deviation,
            color=skia.Color4f(
                filter_effect.flood_color.to_rgba(rgba_range=(0, 1))
            ),
        )
        skia_paint = skia.Paint(ImageFilter=skia_filter)
        return skia_paint

    def _render_transformation(self, transformation):
        render_transformation_function = (
            self._get_transformation_render_function(transformation)
        )
        render_transformation_function(transformation)

    def _get_transformation_render_function(self, transformation):
        if momapy.builder.isinstance_or_builder(
            transformation, momapy.geometry.Translation
        ):
            return self._render_translation
        elif momapy.builder.isinstance_or_builder(
            transformation, momapy.geometry.Rotation
        ):
            return self._render_rotation
        elif momapy.builder.isinstance_or_builder(
            transformation, momapy.geometry.Scaling
        ):
            return self._render_scaling
        elif momapy.builder.isinstance_or_builder(
            transformation, momapy.geometry.MatrixTransformation
        ):
            return self._render_matrix_transformation

    def _get_drawing_element_render_function(self, drawing_element):
        if momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Group
        ):
            return self._render_group
        elif momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Path
        ):
            return self._render_path
        elif momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Text
        ):
            return self._render_text
        elif momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Ellipse
        ):
            return self._render_ellipse
        elif momapy.builder.isinstance_or_builder(
            drawing_element, momapy.drawing.Rectangle
        ):
            return self._render_rectangle

    def _render_group(self, group):
        saved_canvas = self._canvas
        recorder = skia.PictureRecorder()
        canvas = recorder.beginRecording(skia.Rect(self.width, self.height))
        self._canvas = canvas
        for drawing_element in group.elements:
            self.render_drawing_element(drawing_element)
        picture = recorder.finishRecordingAsPicture()
        if (
            group.filter is not None
            and group.filter != momapy.drawing.NoneValue
        ):
            skia_paints = self._make_filter_paints_from_filter(group.filter)
        else:
            skia_paints = [None]
        self._canvas = saved_canvas
        for skia_paint in skia_paints:
            self._canvas.drawPicture(picture, paint=skia_paint)

    def _render_path(self, path):
        skia_path = self._make_path(path)
        if self._fill is not None:
            skia_paint = self._make_fill_paint()
            self._canvas.drawPath(path=skia_path, paint=skia_paint)
        if self._stroke is not None:
            skia_paint = self._make_stroke_paint()
            self._canvas.drawPath(path=skia_path, paint=skia_paint)

    def _make_path(self, path):
        skia_path = skia.Path()
        for path_action in path.actions:
            self._add_path_action_to_skia_path(skia_path, path_action)
        return skia_path

    def _render_text(self, text):
        skia_typeface = skia.Typeface(familyName=text.font_family)
        skia_font = skia.Font(typeface=skia_typeface, size=text.font_size)
        if self._fill is not None:
            skia_paint = self._make_fill_paint()
            self._canvas.drawString(
                text=text.text,
                x=text.x,
                y=text.y,
                font=skia_font,
                paint=skia_paint,
            )
        if self._stroke is not None:
            skia_paint = self._make_stroke_paint()
            self._canvas.drawString(
                text=text.text,
                x=text.x,
                y=text.y,
                font=skia_font,
                paint=skia_paint,
            )

    def _render_ellipse(self, ellipse):
        skia_rect = skia.Rect(
            ellipse.x - ellipse.rx,
            ellipse.y - ellipse.ry,
            ellipse.x + ellipse.rx,
            ellipse.y + ellipse.ry,
        )
        if self._fill is not None:
            skia_paint = self._make_fill_paint()
            self._canvas.drawOval(oval=skia_rect, paint=skia_paint)
        if self._stroke is not None:
            skia_paint = self._make_stroke_paint()
            self._canvas.drawOval(oval=skia_rect, paint=skia_paint)

    def _render_rectangle(self, rectangle):
        skia_rect = skia.Rect(
            rectangle.x,
            rectangle.y,
            rectangle.x + rectangle.width,
            rectangle.y + rectangle.height,
        )
        if self._fill is not None:
            skia_paint = self._make_fill_paint()
            self._canvas.drawRoundRect(
                rect=skia_rect,
                rx=rectangle.rx,
                ry=rectangle.ry,
                paint=skia_paint,
            )
        if self._stroke is not None:
            skia_paint = self._make_stroke_paint()
            self._canvas.drawRoundRect(
                rect=skia_rect,
                rx=rectangle.rx,
                ry=rectangle.ry,
                paint=skia_paint,
            )

    @classmethod
    def _add_path_action_to_skia_path(cls, skia_path, path_action):
        add_function = cls._get_path_action_add_function(path_action)
        add_function(skia_path, path_action)

    @classmethod
    def _get_path_action_add_function(cls, path_action):
        if momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.MoveTo
        ):
            return cls._add_move_to
        elif momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.LineTo
        ):
            return cls._add_line_to
        elif momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.Close
        ):
            return cls._add_close
        elif momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.Arc
        ):
            return cls._add_arc
        elif momapy.builder.isinstance_or_builder(
            path_action, momapy.drawing.EllipticalArc
        ):
            return cls._add_elliptical_arc

    @staticmethod
    def _add_move_to(skia_path, move_to):
        skia_path.moveTo(move_to.x, move_to.y)

    @staticmethod
    def _add_line_to(skia_path, line_to):
        skia_path.lineTo(line_to.x, line_to.y)

    @staticmethod
    def _add_close(skia_path, close):
        skia_path.close()

    @staticmethod
    def _add_elliptical_arc(skia_path, elliptical_arc):
        if elliptical_arc.arc_flag == 0:
            skia_arc_flag = skia.Path.ArcSize.kSmall_ArcSize
        else:
            skia_arc_flag = skia.Path.ArcSize.kLarge_ArcSize
        if elliptical_arc.sweep_flag == 1:
            skia_sweep_flag = skia.PathDirection.kCW
        else:
            skia_sweep_flag = skia.PathDirection.kCCW
        skia_path.arcTo(
            rx=elliptical_arc.rx,
            ry=elliptical_arc.ry,
            xAxisRotate=elliptical_arc.x_axis_rotation,
            largeArc=skia_arc_flag,
            sweep=skia_sweep_flag,
            x=elliptical_arc.x,
            y=elliptical_arc.y,
        )

    def _render_translation(self, translation):
        self._canvas.translate(dx=translation.tx, dy=translation.ty)

    def _render_rotation(self, rotation):
        angle = math.degrees(rotation.angle)
        if rotation.point is not None:
            self._canvas.rotate(
                degrees=angle, px=rotation.point.x, py=rotation.point.y
            )
        else:
            self._canvas.rotate(degrees=angle)

    def _render_scaling(self, scaling):
        self._canvas.scale(sx=scaling.sx, sy=scaling.sy)

    def _render_matrix_transformation(self, matrix_transformation):
        m = skia.Matrix.MakeAll(
            scaleX=matrix_transformation.m[0][0],
            skewX=matrix_transformation.m[0][1],
            transX=matrix_transformation.m[0][2],
            skewY=matrix_transformation.m[1][0],
            scaleY=matrix_transformation.m[1][1],
            transY=matrix_transformation.m[1][2],
            pers0=matrix_transformation.m[2][0],
            pers1=matrix_transformation.m[2][1],
            pers2=matrix_transformation.m[2][2],
        )
        self._canvas.concat(m)


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
            height=self.height,
        )

    def set_context(self, context):
        self.cairo_renderer._context = context

    def render_map(self, map_):
        self.cairo_renderer.render_map(map_)

    def render_layout_element(self, layout_element):
        self.cairo_renderer.render_layout_element(layout_element)

    def render_drawing_element(self, drawing_element):
        self.cairo_renderer.render_drawing_element(drawing_element)


register_renderer("cairo", CairoRenderer)
register_renderer("svg-native", SVGNativeRenderer)
register_renderer("svg-native-compat", SVGNativeCompatRenderer)
register_renderer("gtk-cairo", GTKCairoRenderer)
register_renderer("skia", SkiaRenderer)
