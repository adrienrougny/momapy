"""Class for rendering with Cairo"""

import dataclasses
import typing
import typing_extensions
import math
import os

try:
    import cairo
    import gi

    gi.require_version("Pango", "1.0")
    gi.require_version("PangoCairo", "1.0")
    import gi.repository.Pango
    import gi.repository.PangoCairo
except ModuleNotFoundError as e:
    raise Exception(
        "You might want to install momapy with the cairo extra: momapy[cairo]"
    ) from e


import momapy.drawing
import momapy.geometry
import momapy.rendering.core


@dataclasses.dataclass(kw_only=True)
class CairoRenderer(momapy.rendering.core.StatefulRenderer):
    """Class for cairo renderers"""

    formats: typing.ClassVar[list[str]] = ["pdf", "svg", "png", "ps"]
    _de_class_func_mapping: typing.ClassVar[dict] = {
        momapy.drawing.Group: "_render_group",
        momapy.drawing.Path: "_render_path",
        momapy.drawing.Text: "_render_text",
        momapy.drawing.Ellipse: "_render_ellipse",
        momapy.drawing.Rectangle: "_render_rectangle",
    }
    _pa_class_func_mapping: typing.ClassVar[dict] = {
        momapy.drawing.MoveTo: "_add_move_to",
        momapy.drawing.LineTo: "_add_line_to",
        momapy.drawing.CurveTo: "_add_curve_to",
        momapy.drawing.QuadraticCurveTo: "_add_quadratic_curve_to",
        momapy.drawing.ClosePath: "_add_close_path",
        momapy.drawing.EllipticalArc: "_add_elliptical_arc",
    }
    _tr_class_func_mapping: typing.ClassVar[dict] = {
        momapy.geometry.Translation: "_add_translation",
        momapy.geometry.Rotation: "_add_rotation",
        momapy.geometry.Scaling: "_add_scaling",
        momapy.geometry.MatrixTransformation: "_add_matrix_transformation",
    }
    _te_font_style_slant_mapping: typing.ClassVar[dict] = {
        momapy.drawing.FontStyle.NORMAL: gi.repository.Pango.Style.NORMAL,
        momapy.drawing.FontStyle.ITALIC: gi.repository.Pango.Style.ITALIC,
        momapy.drawing.FontStyle.OBLIQUE: gi.repository.Pango.Style.OBLIQUE,
    }
    context: cairo.Context = dataclasses.field(
        metadata={"description": "A cairo context"}
    )
    _config: dict = dataclasses.field(default_factory=dict)
    _pango_font_descriptions: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def from_file(
        cls,
        file_path: str | os.PathLike,
        width: float,
        height: float,
        format_: typing.Literal["pdf", "svg", "png", "ps"] = "pdf",
    ) -> typing_extensions.Self:
        config = {}
        if format_ == "pdf":
            surface = cairo.PDFSurface(file_path, width, height)
        elif format_ == "ps":
            surface = cairo.PSSurface(file_path, width, height)
        elif format_ == "svg":
            surface = cairo.SVGSurface(file_path, width, height)
        elif format_ == "png":
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
        config["surface"] = surface
        config["file_path"] = file_path
        config["width"] = width
        config["height"] = height
        config["format"] = format_
        context = cairo.Context(surface)
        return cls(context=context, _config=config)

    def begin_session(self):
        pass

    def end_session(self):
        surface = self.context.get_target()
        format_ = self._config.get("format")
        if format_ == "png":
            surface.write_to_png(self._config["file_path"])
        surface.finish()
        surface.flush()

    def new_page(self, width, height):
        format_ = self._config.get("format")
        if format_ == "pdf" or format_ == "ps":
            self.context.show_page()
            surface = self.context.get_target()
            surface.set_size(width, height)

    def render_map(self, map_):
        self.render_layout_element(map_.layout)

    def render_layout_element(self, layout_element):
        drawing_elements = layout_element.drawing_elements()
        for drawing_element in drawing_elements:
            self.render_drawing_element(drawing_element)

    def render_drawing_element(self, drawing_element):
        self.save()
        self.set_current_state_from_drawing_element(drawing_element)
        self._add_transform_from_drawing_element(drawing_element)
        class_ = type(drawing_element)
        if issubclass(class_, momapy.builder.Builder):
            class_ = class_._cls_to_build
        de_func = getattr(self, self._de_class_func_mapping[class_])
        de_func(drawing_element)
        self.restore()

    def self_save(self):
        self.context.save()

    def self_restore(self):
        self.context.restore()
        self.context.new_path()  # context.restore() does not forget the current path

    def _make_stroke_paint(self):
        """Set stroke paint on context"""
        stroke = self.get_current_value("stroke")
        stroke_width = self.get_current_value("stroke_width")
        stroke_dasharray = self.get_current_value("stroke_dasharray")
        stroke_dashoffset = self.get_current_value("stroke_dashoffset")

        if stroke != momapy.drawing.NoneValue and stroke is not None:
            self.context.set_line_width(stroke_width)
            self.context.set_source_rgba(*stroke.to_rgba(rgba_range=(0, 1)))
            if (
                stroke_dasharray is not None
                and stroke_dasharray != momapy.drawing.NoneValue
            ):
                self.context.set_dash(stroke_dasharray, stroke_dashoffset or 0)
            else:
                self.context.set_dash([])
            return True
        return False

    def _make_fill_paint(self):
        """Set fill paint on context"""
        fill = self.get_current_value("fill")
        if fill != momapy.drawing.NoneValue and fill is not None:
            self.context.set_source_rgba(*fill.to_rgba(rgba_range=(0, 1)))
            return True
        return False

    def _stroke_and_fill(self):
        """Apply stroke and fill to current path"""
        has_fill = self._make_fill_paint()
        has_stroke = self.get_current_value("stroke") not in [
            momapy.drawing.NoneValue,
            None,
        ]

        if has_fill:
            if has_stroke:
                self.context.fill_preserve()
            else:
                self.context.fill()

        if has_stroke:
            self._make_stroke_paint()
            self.context.stroke()

    def _add_transform_from_drawing_element(self, drawing_element):
        if (
            drawing_element.transform is not None
            and drawing_element.transform != momapy.drawing.NoneValue
        ):
            for transformation in drawing_element.transform:
                self._add_transformation(transformation)

    def _add_transformation(self, transformation):
        class_ = type(transformation)
        if issubclass(class_, momapy.builder.Builder):
            class_ = class_._cls_to_build
        tr_func = getattr(self, self._tr_class_func_mapping[class_])
        return tr_func(transformation)

    def _render_group(self, group):
        for drawing_element in group.elements:
            self.render_drawing_element(drawing_element)

    def _add_path_action_to_context(self, path_action):
        class_ = type(path_action)
        if issubclass(class_, momapy.builder.Builder):
            class_ = class_._cls_to_build
        pa_func = getattr(self, self._pa_class_func_mapping[class_])
        pa_func(path_action)

    def _render_path(self, path):
        for action in path.actions:
            self._add_path_action_to_context(action)
        self._stroke_and_fill()

    def _render_text(self, text):
        pango_layout = gi.repository.PangoCairo.create_layout(self.context)

        font_family = self.get_current_value("font_family")
        font_size = self.get_current_value("font_size")
        font_weight = self.get_current_value("font_weight")
        font_style = self.get_current_value("font_style")

        pango_font_description = self._pango_font_descriptions.get(
            (font_family, font_size, font_weight, font_style)
        )

        if pango_font_description is None:
            pango_font_description = gi.repository.Pango.FontDescription()
            pango_font_description.set_family(font_family)
            pango_font_description.set_absolute_size(
                gi.repository.Pango.units_from_double(font_size)
            )
            pango_font_description.set_weight(int(font_weight))
            pango_style = self._te_font_style_slant_mapping.get(
                font_style, gi.repository.Pango.Style.NORMAL
            )
            pango_font_description.set_style(pango_style)
            self._pango_font_descriptions[
                (font_family, font_size, font_weight, font_style)
            ] = pango_font_description

        pango_layout.set_font_description(pango_font_description)
        pango_layout.set_text(text.text)
        pos = pango_layout.index_to_pos(0)
        x_offset = gi.repository.Pango.units_to_double(pos.x)
        pango_layout_iter = pango_layout.get_iter()
        baseline = pango_layout_iter.get_baseline()
        y_offset = gi.repository.Pango.units_to_double(baseline)
        self.context.translate(text.x - x_offset, text.y - y_offset)
        if self._make_fill_paint():
            gi.repository.PangoCairo.show_layout(self.context, pango_layout)
        if self._make_stroke_paint():
            gi.repository.PangoCairo.layout_path(self.context, pango_layout)
            self.context.stroke()

    def _render_ellipse(self, ellipse):
        self.context.save()
        self.context.translate(ellipse.x, ellipse.y)
        self.context.scale(ellipse.rx, ellipse.ry)
        self.context.arc(0, 0, 1, 0, 2 * math.pi)
        self.context.close_path()
        self.context.restore()
        self._stroke_and_fill()

    def _render_rectangle(self, rectangle):
        path = rectangle.to_path()
        self._render_path(path)

    def _add_move_to(self, move_to):
        self.context.move_to(move_to.x, move_to.y)

    def _add_line_to(self, line_to):
        self.context.line_to(line_to.x, line_to.y)

    def _add_curve_to(self, curve_to):
        self.context.curve_to(
            curve_to.control_point1.x,
            curve_to.control_point1.y,
            curve_to.control_point2.x,
            curve_to.control_point2.y,
            curve_to.x,
            curve_to.y,
        )

    def _add_quadratic_curve_to(self, quadratic_curve_to):
        cairo_current_point = self.context.get_current_point()
        current_point = momapy.geometry.Point(
            cairo_current_point[0], cairo_current_point[1]
        )
        curve_to = quadratic_curve_to.to_curve_to(current_point)
        self._add_curve_to(curve_to)

    def _add_close_path(self, close_path):
        self.context.close_path()

    def _add_elliptical_arc(self, elliptical_arc):
        # Get current point
        current_point = self.context.get_current_point()
        p1 = momapy.geometry.Point(current_point[0], current_point[1])

        # Create elliptical arc geometry object
        obj = momapy.geometry.EllipticalArc(
            p1=p1,
            p2=elliptical_arc.point,
            rx=elliptical_arc.rx,
            ry=elliptical_arc.ry,
            x_axis_rotation=elliptical_arc.x_axis_rotation,
            arc_flag=elliptical_arc.arc_flag,
            sweep_flag=elliptical_arc.sweep_flag,
        )

        # Get center parameterization
        cx, cy, rx, ry, sigma, theta1, theta2, delta_theta = (
            obj.get_center_parameterization()
        )

        # Apply transformation for rotated ellipse
        self.context.save()
        self.context.translate(cx, cy)
        self.context.rotate(sigma)
        self.context.scale(rx, ry)

        # Draw arc
        if delta_theta > 0:
            self.context.arc(0, 0, 1, theta1, theta2)
        else:
            self.context.arc_negative(0, 0, 1, theta1, theta2)

        self.context.restore()

    def _add_translation(self, translation):
        self.context.translate(translation.tx, translation.ty)

    def _add_rotation(self, rotation):
        if rotation.point is not None:
            self.context.translate(rotation.point.x, rotation.point.y)
            self.context.rotate(rotation.angle)
            self.context.translate(-rotation.point.x, -rotation.point.y)
        else:
            self.context.rotate(rotation.angle)

    def _add_scaling(self, scaling):
        self.context.scale(scaling.sx, scaling.sy)

    def _add_matrix_transformation(self, matrix_transformation):
        m = cairo.Matrix(
            xx=matrix_transformation.m[0][0],
            yx=matrix_transformation.m[1][0],
            xy=matrix_transformation.m[0][1],
            yy=matrix_transformation.m[1][1],
            x0=matrix_transformation.m[0][2],
            y0=matrix_transformation.m[1][2],
        )
        self.context.transform(m)


momapy.rendering.core.register_renderer("cairo", CairoRenderer)
