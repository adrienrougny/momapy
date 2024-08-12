import dataclasses
import typing
import cairo
import math
import gi

gi.require_version("PangoCairo", "1.0")
import gi.repository

import momapy.drawing
import momapy.geometry
import momapy.builder
import momapy.rendering.core


@dataclasses.dataclass
class CairoRenderer(momapy.rendering.core.Renderer):
    formats: typing.ClassVar[list[str]] = ["pdf", "svg", "png", "ps"]
    _de_class_func_mapping: typing.ClassVar[dict] = {
        momapy.drawing.Group: "_render_group",
        momapy.drawing.Path: "_render_path",
        momapy.drawing.Text: "_render_text",
        momapy.drawing.Ellipse: "_render_ellipse",
        momapy.drawing.Rectangle: "_render_rectangle",
    }
    _pa_class_func_mapping: typing.ClassVar[dict] = {
        momapy.drawing.MoveTo: "_render_move_to",
        momapy.drawing.LineTo: "_render_line_to",
        momapy.drawing.CurveTo: "_render_curve_to",
        momapy.drawing.QuadraticCurveTo: "_render_quadratic_curve_to",
        momapy.drawing.Close: "_render_close",
        momapy.drawing.EllipticalArc: "_render_elliptical_arc",
    }
    _tr_class_func_mapping: typing.ClassVar[dict] = {
        momapy.geometry.Translation: "_add_translation",
        momapy.geometry.Rotation: "_add_rotation",
        momapy.geometry.Scaling: "_add_scaling",
        momapy.geometry.MatrixTransformation: "_add_matrix_transformation",
    }
    context: cairo.Context
    config: dict = dataclasses.field(default_factory=dict)
    _pango_font_descriptions: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def from_file(cls, output_file, width, height, format_, config=None):
        def _make_surface(output_file, width, height, format_):
            if format_ == "pdf":
                return cairo.PDFSurface(output_file, width, height)
            elif format_ == "ps":
                return cairo.PSSurface(output_file, width, height)
            elif format_ == "svg":
                return cairo.SVGSurface(output_file, width, height)
            elif format_ == "png":
                return cairo.ImageSurface(
                    cairo.FORMAT_ARGB32, int(width), int(height)
                )

        if config is None:
            config = {}
        config["output_file"] = output_file
        config["format"] = format_
        config["width"] = width
        config["height"] = height
        surface = _make_surface(output_file, width, height, format_)
        return cls.from_surface(surface, config)

    @classmethod
    def from_surface(cls, surface, config=None):
        if config is None:
            config = {}
        config["surface"] = surface
        context = cairo.Context(surface)
        return cls(context, config)

    def begin_session(self):
        self._states = []
        self._stroke = None
        self._fill = self.default_fill
        self._stroke_width = self.default_stroke_width

    def end_session(self):
        surface = self.context.get_target()
        format_ = self.config.get("format")
        if format_ == "png":
            surface.write_to_png(self.config["output_file"])
        surface.finish()
        surface.flush()

    def new_page(self, width, height):
        format_ = self.config.get("format")
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
        self._save()
        self._set_state_from_drawing_element(drawing_element)
        self._add_transform_from_drawing_element(drawing_element)
        class_ = type(drawing_element)
        if issubclass(class_, momapy.builder.Builder):
            class_ = class_._cls_to_build
        de_func = getattr(self, self._de_class_func_mapping[class_])
        de_func(drawing_element)
        self._restore()

    def _save(self):
        state = {
            "stroke": self._stroke,
            "fill": self._fill,
            "stroke_width": self._stroke_width,
        }
        self._states.append(state)
        self.context.save()

    def _restore(self):
        state = self._states.pop()
        self._set_state(state)
        self.context.restore()
        self._set_new_path()  # context.restore() does not forget the current path

    def _set_state(self, state):
        for key in state:
            setattr(self, f"_{key}", state[key])

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

    def _set_new_path(self):
        self.context.new_path()

    def _stroke_and_fill(self):
        if self._fill is not None:
            self.context.set_source_rgba(*self._fill.to_rgba(rgba_range=(0, 1)))
            if self._stroke is not None:
                self.context.fill_preserve()
            else:
                self.context.fill()
        if self._stroke is not None:
            self.context.set_line_width(self._stroke_width)
            self.context.set_source_rgba(
                *self._stroke.to_rgba(rgba_range=(0, 1))
            )
            self.context.stroke()

    def _render_path_action(self, path_action):
        class_ = type(path_action)
        if issubclass(class_, momapy.builder.Builder):
            class_ = class_._cls_to_build
        pa_func = getattr(self, self._pa_class_func_mapping[class_])
        pa_func(path_action)

    def _add_transform_from_drawing_element(self, drawing_element):
        if drawing_element.transform is not None:
            for transformation in drawing_element.transform:
                self._add_transformation(transformation)

    def _add_transformation(self, transformation):
        class_ = type(transformation)
        if issubclass(class_, momapy.builder.Builder):
            class_ = class_._cls_to_build
        tr_func = getattr(
            self, self._tr_class_func_mapping[type(transformation)]
        )
        return tr_func(transformation)

    def _render_group(self, group):
        for drawing_element in group.elements:
            self.render_drawing_element(drawing_element)

    def _render_path(self, path):
        for path_action in path.actions:
            self._render_path_action(path_action)
        self._stroke_and_fill()

    def _render_text(self, text):
        pango_layout = gi.repository.PangoCairo.create_layout(self.context)
        pango_font_description = self._pango_font_descriptions.get(
            (
                text.font_family,
                text.font_size,
            )
        )
        if pango_font_description is None:
            pango_font_description = gi.repository.Pango.FontDescription()
            pango_font_description.set_family(text.font_family)
            pango_font_description.set_absolute_size(
                gi.repository.Pango.units_from_double(text.font_size)
            )
            self._pango_font_descriptions[
                (text.font_family, text.font_size)
            ] = pango_font_description
        pango_layout.set_font_description(pango_font_description)
        pango_layout.set_text(text.text)
        pos = pango_layout.index_to_pos(0)
        gi.repository.Pango.extents_to_pixels(pos)
        x = pos.x
        pango_layout_iter = pango_layout.get_iter()
        y = round(
            gi.repository.Pango.units_to_double(
                pango_layout_iter.get_baseline()
            )
        )
        tx = text.x - x
        ty = text.y - y
        self.context.translate(tx, ty)
        self.context.set_source_rgba(*self._fill.to_rgba(rgba_range=(0, 1)))
        gi.repository.PangoCairo.show_layout(self.context, pango_layout)

    def _render_ellipse(self, ellipse):
        self.context.save()
        self.context.translate(ellipse.x, ellipse.y)
        self.context.scale(ellipse.rx, ellipse.ry)
        self.context.arc(0, 0, 1, 0, 2 * math.pi)
        self.context.close_path()
        self.context.restore()
        self._stroke_and_fill()

    def _render_rectangle(self, rectangle):
        actions.append(rectangle.to_path())
        self._render_path(path)

    def _render_MoveTo(self, move_to):
        self.context.MoveTo(move_to.x, move_to.y)

    def _render_LineTo(self, line_to):
        self.context.LineTo(line_to.x, line_to.y)

    def _render_CurveTo(self, curve_to):
        self.context.CurveTo(
            curve_to.control_point1.x,
            curve_to.control_point2.y,
            curve_to.control_point2.x,
            curve_to.control_point2.y,
            curve_to.x,
            curve_to.y,
        )

    def _render_QuadraticCurveTo(self, quadratic_curve_to):
        cairo_current_point = self.context.get_current_point()
        current_point = momapy.geometry.Point(
            cairo_current_point[0], cairo_current_point[1]
        )
        curve_to = quadratic_curve_to.to_cubic(current_point)
        self._render_CurveTo(curve_to)

    def _render_ClosePath(self, close):
        self.context.close_path()

    def _render_EllipticalArc(self, elliptical_arc):
        obj = momapy.geometry.EllipticalArc(
            momapy.geometry.Point(
                self.context.get_current_point()[0],
                self.context.get_current_point()[1],
            ),
            elliptical_arc.point,
            elliptical_arc.rx,
            elliptical_arc.ry,
            elliptical_arc.x_axis_rotation,
            elliptical_arc.arc_flag,
            elliptical_arc.sweep_flag,
        )
        arc, transformation = obj.to_arc_and_transformation()
        self.context.save()
        self._add_transformation(transformation)
        self.context.arc(
            arc.point.x, arc.point.y, arc.radius, arc.start_angle, arc.end_angle
        )
        self.context.restore()

    def _add_translation(self, translation):
        self.context.translate(translation.tx, translation.ty)

    def _add_rotation(self, rotation):
        point = rotation.point
        if point is not None:
            self.context.translate(point.x, point.y)
            self.context.rotate(rotation.angle)
            self.context.translate(-point.x, -point.y)
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
