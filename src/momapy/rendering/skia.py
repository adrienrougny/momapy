"""Class for rendering with Skia"""

import dataclasses
import typing
import math
import os

import skia

import momapy.drawing
import momapy.geometry
import momapy.rendering.core


@dataclasses.dataclass(kw_only=True)
class SkiaRenderer(momapy.rendering.core.StatefulRenderer):
    """Class for skia renderers"""

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
    _fe_class_func_mapping: typing.ClassVar[dict] = {
        momapy.drawing.DropShadowEffect: "_make_drop_shadow_effect",
        momapy.drawing.CompositeEffect: "_make_composite_effect",
        momapy.drawing.GaussianBlurEffect: "_make_gaussian_blur_effect",
        momapy.drawing.OffsetEffect: "_make_offset_effect",
        momapy.drawing.FloodEffect: "_make_flood_effect",
    }
    _fe_composite_comp_op_blendmode_mapping: typing.ClassVar[dict] = {
        momapy.drawing.CompositionOperator.OVER: skia.BlendMode.kSrcOver,
        momapy.drawing.CompositionOperator.IN: skia.BlendMode.kSrcIn,
        momapy.drawing.CompositionOperator.OUT: skia.BlendMode.kSrcOut,
        momapy.drawing.CompositionOperator.ATOP: skia.BlendMode.kSrcATop,
        momapy.drawing.CompositionOperator.XOR: skia.BlendMode.kXor,
        momapy.drawing.CompositionOperator.LIGHTER: skia.BlendMode.kLighten,
        momapy.drawing.CompositionOperator.ARTIHMETIC: None,
    }
    _fe_gaussian_blur_edgemode_tilemode_mapping: typing.ClassVar[dict] = {
        momapy.drawing.EdgeMode.WRAP: skia.TileMode.kMirror,
        momapy.drawing.EdgeMode.DUPLICATE: skia.TileMode.kClamp,
        None: skia.TileMode.kDecal,
    }
    _te_font_style_slant_mapping: typing.ClassVar[dict] = {
        momapy.drawing.FontStyle.NORMAL: skia.FontStyle.Slant.kUpright_Slant,
        momapy.drawing.FontStyle.ITALIC: skia.FontStyle.Slant.kItalic_Slant,
        momapy.drawing.FontStyle.OBLIQUE: skia.FontStyle.Slant.kOblique_Slant,
    }
    canvas: skia.Canvas = dataclasses.field(metadata={"description": "A skia canvas"})
    _config: dict = dataclasses.field(default_factory=dict)
    _skia_typefaces: dict = dataclasses.field(default_factory=dict)
    _skia_fonts: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def from_file(
        cls,
        file_path: str | os.PathLike,
        width: float,
        height: float,
        format_: typing.Literal["pdf", "svg", "png", "jpeg", "webp"] = "pdf",
    ) -> typing.Self:
        config = {}
        if format_ == "pdf":
            stream = skia.FILEWStream(file_path)
            document = skia.PDF.MakeDocument(stream)
            canvas = document.beginPage(width, height)
            config["stream"] = stream
            config["document"] = document
        elif format_ in ["png", "jpeg", "webp"]:
            surface = skia.Surface(width=int(width), height=int(height))
            canvas = surface.getCanvas()
            config["surface"] = surface
            config["file_path"] = file_path
        elif format_ == "svg":
            stream = skia.FILEWStream(file_path)
            canvas = skia.SVGCanvas.Make((width, height), stream)
            config["stream"] = stream
        config["file_path"] = file_path
        config["width"] = width
        config["height"] = height
        config["format"] = format_
        return cls(canvas=canvas, _config=config)

    def begin_session(self):
        pass

    def end_session(self):
        self.canvas.flush()
        format_ = self._config.get("format")
        if format_ == "pdf":
            self._config["document"].endPage()
            self._config["document"].close()
        elif format_ == "png":
            image = self._config["surface"].makeImageSnapshot()
            image.save(self._config["file_path"], skia.kPNG)
        elif format_ == "jpeg":
            image = self._config["surface"].makeImageSnapshot()
            image.save(self._config["file_path"], skia.kJPEG)
        elif format_ == "webp":
            image = self._config["surface"].makeImageSnapshot()
            image.save(self._config["file_path"], skia.kWEBP)
        elif format_ == "svg":
            del self.canvas
            self._config["stream"].flush()

    def new_page(self, width, height):
        format_ = self._config.get("format")
        if format_ == "pdf":
            self._config["document"].endPage()
            canvas = self._config["document"].beginPage(width, height)
            self.canvas = canvas

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
        filter = self.get_current_value("filter")
        if filter is not momapy.drawing.NoneValue:
            bbox = drawing_element.bbox()
            saved_canvas = self.canvas
            recorder = skia.PictureRecorder()
            canvas = recorder.beginRecording(
                skia.Rect.MakeXYWH(
                    bbox.north_west().x,
                    bbox.north_west().y,
                    bbox.width,
                    bbox.height,
                )
            )
            self.canvas = canvas
            de_func(drawing_element)
            picture = recorder.finishRecordingAsPicture()
            skia_paint = self._make_filter_paint(
                filter, drawing_element.get_filter_region()
            )
            self.canvas = saved_canvas
            self.canvas.drawPicture(picture, paint=skia_paint)
        else:
            de_func(drawing_element)
        self.restore()

    def self_save(self):
        self.canvas.save()

    def self_restore(self):
        self.canvas.restore()

    def _make_stroke_paint(self):
        if self.get_current_value("stroke_dasharray") is not momapy.drawing.NoneValue:
            skia_path_effect = skia.DashPathEffect.Make(
                list(self.get_current_value("stroke_dasharray")),
                self.get_current_value("stroke_dashoffset"),
            )
        else:
            skia_path_effect = None
        skia_paint = skia.Paint(
            AntiAlias=True,
            Color4f=skia.Color4f(
                self.get_current_value("stroke").to_rgba(rgba_range=(0.0, 1.0))
            ),
            StrokeWidth=self.get_current_value("stroke_width"),
            PathEffect=skia_path_effect,
            Style=skia.Paint.kStroke_Style,
        )
        return skia_paint

    def _make_fill_paint(self):
        skia_paint = skia.Paint(
            AntiAlias=True,
            Color4f=skia.Color4f(
                self.get_current_value("fill").to_rgba(rgba_range=(0.0, 1.0))
            ),
            Style=skia.Paint.kFill_Style,
        )
        return skia_paint

    def _make_filter_paint(self, filter_, filter_region):
        dskia_filters = {}
        for filter_effect in filter_.effects:
            class_ = type(filter_effect)
            if issubclass(class_, momapy.builder.Builder):
                class_ = class_._cls_to_build
            fe_func = getattr(self, self._fe_class_func_mapping[class_])
            skia_filter = fe_func(filter_effect, filter_region, dskia_filters)
            if filter_effect.result is not None:
                dskia_filters[filter_effect.result] = skia_filter
        skia_paint = skia.Paint(AntiAlias=True, ImageFilter=skia_filter)
        return skia_paint

    def _make_crop_rect_from_filter_region(self, filter_region):
        crop_rect = skia.IRect.MakeXYWH(
            round(filter_region.north_west().x),
            round(filter_region.north_west().y),
            round(filter_region.width),
            round(filter_region.height),
        )
        return crop_rect

    def _make_input_filter_from_reference(self, dskia_filters, filter_reference):
        if isinstance(filter_reference, momapy.drawing.FilterEffectInput):
            return None  # all SVG options default to source bitmap in skia
        in_skia_filter = dskia_filters.get(filter_reference)
        if in_skia_filter is None:  # if no reference or bad reference
            if dskia_filters:  # we take the last filter effect primitive if it exists, otherwise remains None (source Bitmap)
                in_skia_filter = dskia_filters[list(dskia_filters.keys())[-1]]
        return in_skia_filter

    def _make_drop_shadow_effect(self, filter_effect, filter_region, dskia_filters):
        crop_rect = self._make_crop_rect_from_filter_region(filter_region)
        skia_filter = skia.ImageFilters.DropShadow(
            dx=filter_effect.dx,
            dy=filter_effect.dy,
            sigmaX=filter_effect.std_deviation,
            sigmaY=filter_effect.std_deviation,
            color=skia.Color4f(
                *filter_effect.flood_color.to_rgb(rgb_range=(0, 1)),
                filter_effect.flood_opacity,
            ),
            cropRect=crop_rect,
        )
        return skia_filter

    def _make_composite_effect(self, filter_effect, filter_region, dskia_filters):
        crop_rect = self._make_crop_rect_from_filter_region(filter_region)
        in_skia_filter = self._make_input_filter_from_reference(
            dskia_filters, filter_effect.in_
        )
        in2_skia_filter = self._make_input_filter_from_reference(
            dskia_filters, filter_effect.in2
        )
        blend_mode = self._fe_composite_comp_op_blendmode_mapping[
            filter_effect.operator
        ]  # TODO: arithmetic operator
        skia_filter = skia.ImageFilters.Xfermode(
            mode=blend_mode,
            background=in2_skia_filter,
            foreground=in_skia_filter,
            cropRect=crop_rect,
        )
        return skia_filter

    def _make_flood_effect(self, filter_effect, filter_region, dskia_filters):
        crop_rect = self._make_crop_rect_from_filter_region(filter_region)
        skia_paint = skia.Paint(
            AntiAlias=True,
            Color4f=skia.Color4f(
                *filter_effect.flood_color.to_rgb(rgb_range=(0, 1)),
                filter_effect.flood_opacity,
            ),
            Style=skia.Paint.kFill_Style,
        )
        skia_filter = skia.ImageFilters.Paint(
            paint=skia_paint,
            cropRect=crop_rect,
        )
        return skia_filter

    def _make_gaussian_blur_effect(self, filter_effect, filter_region, dskia_filters):
        crop_rect = self._make_crop_rect_from_filter_region(filter_region)
        in_skia_filter = self._make_input_filter_from_reference(
            dskia_filters, filter_effect.in_
        )
        tile_mode = self._fe_gaussian_blur_edgemode_tilemode_mapping[
            filter_effect.edge_mode
        ]
        skia_filter = skia.ImageFilters.Blur(
            sigmaX=filter_effect.std_deviation,
            sigmaY=filter_effect.std_deviation,
            tileMode=tile_mode,
            input=in_skia_filter,
            cropRect=crop_rect,
        )
        return skia_filter

    def _make_offset_effect(self, filter_effect, filter_region, dskia_filters):
        crop_rect = self._make_crop_rect_from_filter_region(filter_region)
        in_skia_filter = self._make_input_filter_from_reference(
            dskia_filters, filter_effect.in_
        )
        skia_filter = skia.ImageFilters.Offset(
            dx=filter_effect.dx,
            dy=filter_effect.dy,
            input=in_skia_filter,
            cropRect=crop_rect,
        )
        return skia_filter

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

    def _add_path_action_to_skia_path(self, skia_path, path_action):
        class_ = type(path_action)
        if issubclass(class_, momapy.builder.Builder):
            class_ = class_._cls_to_build
        pa_func = getattr(self, self._pa_class_func_mapping[class_])
        pa_func(skia_path, path_action)

    def _make_skia_path(self, path):
        skia_path = skia.Path()
        for action in path.actions:
            self._add_path_action_to_skia_path(skia_path, action)
        return skia_path

    def _render_path(self, path):
        skia_path = self._make_skia_path(path)
        if self.get_current_value("fill") != momapy.drawing.NoneValue:
            skia_paint = self._make_fill_paint()
            self.canvas.drawPath(path=skia_path, paint=skia_paint)
        if self.get_current_value("stroke") != momapy.drawing.NoneValue:
            skia_paint = self._make_stroke_paint()
            self.canvas.drawPath(path=skia_path, paint=skia_paint)

    def _render_text(self, text):
        font_family = self.get_current_value("font_family")
        font_weight = self.get_current_value("font_weight")
        font_style = self.get_current_value("font_style")
        skia_typeface = self._skia_typefaces.get((font_family, font_weight, font_style))
        if skia_typeface is None:
            skia_font_slant = self._te_font_style_slant_mapping[font_style]
            skia_font_style = skia.FontStyle(
                weight=int(font_weight),
                slant=skia_font_slant,
                width=skia.FontStyle.kNormal_Width,
            )
            skia_typeface = skia.Typeface(
                familyName=font_family,
                fontStyle=skia_font_style,
            )
            self._skia_typefaces[(font_family, font_weight, font_style)] = skia_typeface
        font_size = self.get_current_value("font_size")
        skia_font = self._skia_fonts.get(
            (
                font_family,
                font_weight,
                font_style,
                font_size,
            )
        )
        if skia_font is None:
            skia_font = skia.Font(
                typeface=skia_typeface,
                size=font_size,
            )
            self._skia_fonts[
                (
                    font_family,
                    font_weight,
                    font_style,
                    font_size,
                )
            ] = skia_font
        if self.get_current_value("fill") != momapy.drawing.NoneValue:
            skia_paint = self._make_fill_paint()
            self.canvas.drawString(
                text=text.text,
                x=text.x,
                y=text.y,
                font=skia_font,
                paint=skia_paint,
            )
        if self.get_current_value("stroke") != momapy.drawing.NoneValue:
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
        if self.get_current_value("fill") != momapy.drawing.NoneValue:
            skia_paint = self._make_fill_paint()
            self.canvas.drawOval(oval=skia_rect, paint=skia_paint)
        if self.get_current_value("stroke") != momapy.drawing.NoneValue:
            skia_paint = self._make_stroke_paint()
            self.canvas.drawOval(oval=skia_rect, paint=skia_paint)

    def _render_rectangle(self, rectangle):
        skia_rect = skia.Rect(
            rectangle.x,
            rectangle.y,
            rectangle.x + rectangle.width,
            rectangle.y + rectangle.height,
        )
        if self.get_current_value("fill") != momapy.drawing.NoneValue:
            skia_paint = self._make_fill_paint()
            self.canvas.drawRoundRect(
                rect=skia_rect,
                rx=rectangle.rx,
                ry=rectangle.ry,
                paint=skia_paint,
            )
        if self.get_current_value("stroke") != momapy.drawing.NoneValue:
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

    def _add_curve_to(self, skia_path, curve_to):
        skia_path.cubicTo(
            curve_to.control_point1.x,
            curve_to.control_point1.y,
            curve_to.control_point2.x,
            curve_to.control_point2.y,
            curve_to.x,
            curve_to.y,
        )

    def _add_quadratic_curve_to(self, skia_path, quadratic_curve_to):
        skia_current_point = skia_path.getPoint(skia_path.countPoints() - 1)
        current_point = momapy.geometry.Point(
            skia_current_point.fX, skia_current_point.fY
        )
        curve_to = quadratic_curve_to.to_curve_to(current_point)
        self._add_curve_to(skia_path, curve_to)

    def _add_close_path(self, skia_path, close_path):
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
            self.canvas.rotate(degrees=angle, px=rotation.point.x, py=rotation.point.y)
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
