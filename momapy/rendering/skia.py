import dataclasses
import typing
import math

import skia

import momapy.drawing
import momapy.geometry
import momapy.rendering.core


@dataclasses.dataclass
class SkiaRenderer(momapy.rendering.core.Renderer):
    formats: typing.ClassVar[list[str]] = ["pdf", "svg", "png", "jpeg", "webp"]
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
        momapy.drawing.Close: "_add_close",
        momapy.drawing.Arc: "_add_arc",
        momapy.drawing.EllipticalArc: "_add_elliptical_arc",
    }
    _tr_class_func_mapping: typing.ClassVar[dict] = {
        momapy.geometry.Translation: "_add_translation",
        momapy.geometry.Rotation: "_add_rotation",
        momapy.geometry.Scaling: "_add_scaling",
        momapy.geometry.MatrixTransformation: "_add_matrix_transformation",
    }
    canvas: skia.Canvas
    config: dict = dataclasses.field(default_factory=dict)
    _skia_typefaces: dict = dataclasses.field(default_factory=dict)
    _skia_fonts: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def from_file(cls, output_file, width, height, format_, config=None):
        if config is None:
            config = {}
        if format_ == "pdf":
            stream = skia.FILEWStream(output_file)
            document = skia.PDF.MakeDocument(stream)
            canvas = document.beginPage(width, height)
            config["stream"] = stream
            config["document"] = document
        elif format_ in ["png", "jpeg", "webp"]:
            surface = skia.Surface(width=int(width), height=int(height))
            canvas = surface.getCanvas()
            config["surface"] = surface
            config["output_file"] = output_file
        elif format_ == "svg":
            stream = skia.FILEWStream(output_file)
            canvas = skia.SVGCanvas.Make((width, height), stream)
            config["stream"] = stream
        config["output_file"] = output_file
        config["width"] = width
        config["height"] = height
        config["format"] = format_
        return cls(canvas, config)

    def begin_session(self):
        self._states = []
        self._stroke = None
        self._fill = self.default_fill
        self._stroke_width = self.default_stroke_width

    def end_session(self):
        self.canvas.flush()
        format_ = self.config.get("format")
        if format_ == "pdf":
            self.config["document"].endPage()
            self.config["document"].close()
        elif format_ == "png":
            image = self.config["surface"].makeImageSnapshot()
            image.save(self.config["output_file"], skia.kPNG)
        elif format_ == "jpeg":
            image = self.config["surface"].makeImageSnapshot()
            image.save(self.config["output_file"], skia.kJPEG)
        elif format_ == "webp":
            image = self.config["surface"].makeImageSnapshot()
            image.save(self.config["output_file"], skia.kWEBP)
        elif format_ == "svg":
            del self.canvas
            self.config["stream"].flush()

    def new_page(self, width, height):
        format_ = self.config.get("format")
        if format_ == "pdf":
            self.config["document"].endPage()
            canvas = self.config["document"].beginPage(width, height)
            self.canvas = canvas

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
        self.canvas.save()

    def _restore(self):
        state = self._states.pop()
        self._set_state(state)
        self.canvas.restore()
        self._set_new_path()

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
        pass

    def _make_stroke_paint(self):
        skia_paint = skia.Paint(
            AntiAlias=True,
            Color4f=skia.Color4f(self._stroke.to_rgba(rgba_range=(0, 1))),
            StrokeWidth=self._stroke_width,
            Style=skia.Paint.kStroke_Style,
        )
        return skia_paint

    def _make_fill_paint(self):
        skia_paint = skia.Paint(
            AntiAlias=True,
            Color4f=skia.Color4f(self._fill.to_rgba(rgba_range=(0, 1))),
            Style=skia.Paint.kFill_Style,
        )
        return skia_paint

    # def _make_filter_paints_from_filter(self, filter_):
    #     skia_paints = []
    #     for filter_effect in filter_.effects:
    #         render_function = self._get_filter_effect_render_function(
    #             filter_effect
    #         )
    #         skia_paint = render_function(filter_effect)
    #         skia_paints.append(skia_paint)
    #     return skia_paints
    #
    # def _get_filter_effect_render_function(self, filter_effect):
    #     if momapy.builder.isinstance_or_builder(
    #         filter_effect, momapy.drawing.DropShadowEffect
    #     ):
    #         return self._render_drop_shadow_effect
    #
    # def _render_drop_shadow_effect(self, filter_effect):
    #     skia_filter = skia.ImageFilters.DropShadow(
    #         dx=filter_effect.dx,
    #         dy=filter_effect.dy,
    #         sigmaX=filter_effect.std_deviation,
    #         sigmaY=filter_effect.std_deviation,
    #         color=skia.Color4f(
    #             filter_effect.flood_color.to_rgba(rgba_range=(0, 1))
    #         ),
    #     )
    #     skia_paint = skia.Paint(ImageFilter=skia_filter)
    #     return skia_paint

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
        # savedcanvas = self.canvas
        # recorder = skia.PictureRecorder()
        # canvas = recorder.beginRecording(skia.Rect(self.width, self.height))
        # self.canvas = canvas
        # for drawing_element in group.elements:
        #     self.render_drawing_element(drawing_element)
        # picture = recorder.finishRecordingAsPicture()
        # if (
        #     group.filter is not None
        #     and group.filter != momapy.drawing.NoneValue
        # ):
        #     skia_paints = self._make_filter_paints_from_filter(group.filter)
        # else:
        #     skia_paints = [None]
        # self.canvas = savedcanvas
        # for skia_paint in skia_paints:
        #     self.canvas.drawPicture(picture, paint=skia_paint)

    def _add_path_action_to_skia_path(self, skia_path, path_action):
        class_ = type(path_action)
        if issubclass(class_, momapy.builder.Builder):
            class_ = class_._cls_to_build
        pa_func = getattr(self, self._pa_class_func_mapping[class_])
        pa_func(skia_path, path_action)

    def _make_skia_path(self, path):
        skia_path = skia.Path()
        for path_action in path.actions:
            self._add_path_action_to_skia_path(skia_path, path_action)
        return skia_path

    def _render_path(self, path):
        skia_path = self._make_skia_path(path)
        if self._fill is not None:
            skia_paint = self._make_fill_paint()
            self.canvas.drawPath(path=skia_path, paint=skia_paint)
        if self._stroke is not None:
            skia_paint = self._make_stroke_paint()
            self.canvas.drawPath(path=skia_path, paint=skia_paint)

    def _render_text(self, text):
        skia_typeface = self._skia_typefaces.get(text.font_family)
        if skia_typeface is None:
            skia_typeface = skia.Typeface(familyName=text.font_family)
            self._skia_typefaces[text.font_family] = skia_typeface
        skia_font = self._skia_fonts.get(
            (
                text.font_family,
                text.font_size,
            )
        )
        if skia_font is None:
            skia_font = skia.Font(typeface=skia_typeface, size=text.font_size)
            self._skia_fonts[
                (
                    text.font_family,
                    text.font_size,
                )
            ] = skia_font
        if self._fill is not None:
            skia_paint = self._make_fill_paint()
            self.canvas.drawString(
                text=text.text,
                x=text.x,
                y=text.y,
                font=skia_font,
                paint=skia_paint,
            )
        if self._stroke is not None:
            skia_paint = self._make_stroke_paint()
            self.canvas.drawString(
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
            self.canvas.drawOval(oval=skia_rect, paint=skia_paint)
        if self._stroke is not None:
            skia_paint = self._make_stroke_paint()
            self.canvas.drawOval(oval=skia_rect, paint=skia_paint)

    def _render_rectangle(self, rectangle):
        skia_rect = skia.Rect(
            rectangle.x,
            rectangle.y,
            rectangle.x + rectangle.width,
            rectangle.y + rectangle.height,
        )
        if self._fill is not None:
            skia_paint = self._make_fill_paint()
            self.canvas.drawRoundRect(
                rect=skia_rect,
                rx=rectangle.rx,
                ry=rectangle.ry,
                paint=skia_paint,
            )
        if self._stroke is not None:
            skia_paint = self._make_stroke_paint()
            self.canvas.drawRoundRect(
                rect=skia_rect,
                rx=rectangle.rx,
                ry=rectangle.ry,
                paint=skia_paint,
            )

    def _add_move_to(self, skia_path, move_to):
        skia_path.moveTo(move_to.x, move_to.y)

    def _add_line_to(self, skia_path, line_to):
        skia_path.lineTo(line_to.x, line_to.y)

    def _add_close(self, skia_path, close):
        skia_path.close()

    def _add_elliptical_arc(self, skia_path, elliptical_arc):
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

    def _add_translation(self, translation):
        self.canvas.translate(dx=translation.tx, dy=translation.ty)

    def _add_rotation(self, rotation):
        angle = math.degrees(rotation.angle)
        if rotation.point is not None:
            self.canvas.rotate(
                degrees=angle, px=rotation.point.x, py=rotation.point.y
            )
        else:
            self.canvas.rotate(degrees=angle)

    def _add_scaling(self, scaling):
        self.canvas.scale(sx=scaling.sx, sy=scaling.sy)

    def _add_matrix_transformation(self, matrix_transformation):
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
        self.canvas.concat(m)


momapy.rendering.core.register_renderer("skia", SkiaRenderer)
