"""Classes for rendering in the SVG format"""

import dataclasses
import typing
import math
import xml.sax.saxutils

import momapy.drawing
import momapy.geometry
import momapy.rendering.core


@dataclasses.dataclass
class SVGElement(object):
    """Class for SVG elements"""

    name: str
    value: typing.Optional[str] = None
    attributes: dict = dataclasses.field(default_factory=dict)
    elements: list["SVGElement"] = dataclasses.field(default_factory=list)

    def to_string(self, indent: int = 0):
        """Return the SVG string representing the element"""
        s_indent = "\t" * indent
        s_value = f"{s_indent}{self.value}\n" if self.value is not None else ""
        if self.attributes:
            l_s_attributes = []
            for attr_name, attr_value in self.attributes.items():
                s_attr_name = attr_name
                s_attr_value = f'"{attr_value}"'
                s_attribute = f"{s_attr_name}={s_attr_value}"
                l_s_attributes.append(s_attribute)
            s_attributes = f" {' '.join(l_s_attributes)}"
        else:
            s_attributes = ""
        if self.elements:
            s_elements = "\n".join(
                [child.to_string(indent + 1) for child in self.elements]
            )
            s_elements += "\n"
        else:
            s_elements = ""
        return f"{s_indent}<{self.name}{s_attributes}>\n{s_value}{s_elements}{s_indent}</{self.name}>"

    def __str__(self):
        return self.to_string()

    def add_element(self, element):
        """Add an sub-element to the SVG element"""
        self.elements.append(element)


@dataclasses.dataclass
class SVGNativeRenderer(momapy.rendering.core.Renderer):
    """Class for SVG native renderers"""

    formats: typing.ClassVar[list[str]] = ["svg"]
    _de_class_func_mapping: typing.ClassVar[dict] = {
        momapy.drawing.Group: "_make_group_element",
        momapy.drawing.Path: "_make_path_element",
        momapy.drawing.Text: "_make_text_element",
        momapy.drawing.Ellipse: "_make_ellipse_element",
        momapy.drawing.Rectangle: "_make_rectangle_element",
    }
    _pa_class_func_mapping: typing.ClassVar[dict] = {
        momapy.drawing.MoveTo: "_make_move_to_value",
        momapy.drawing.LineTo: "_make_line_to_value",
        momapy.drawing.CurveTo: "_make_curve_to_value",
        momapy.drawing.QuadraticCurveTo: "_make_quadratic_curve_to_value",
        momapy.drawing.ClosePath: "_make_close_value",
        momapy.drawing.EllipticalArc: "_make_elliptical_arc_value",
    }
    _tr_class_func_mapping: typing.ClassVar[dict] = {
        momapy.geometry.Translation: "_make_translation_value",
        momapy.geometry.Rotation: "_make_rotation_value",
        momapy.geometry.Scaling: "_make_scaling_value",
        momapy.geometry.MatrixTransformation: "_make_matrix_transformation_value",
    }
    _fe_class_func_mapping: typing.ClassVar[dict] = {
        momapy.drawing.DropShadowEffect: "_make_drop_shadow_effect_element",
        momapy.drawing.CompositeEffect: "_make_composite_effect_element",
        momapy.drawing.GaussianBlurEffect: "_make_gaussian_blur_effect_element",
        momapy.drawing.OffsetEffect: "_make_offset_effect_element",
        momapy.drawing.FloodEffect: "_make_flood_effect_element",
    }
    _fe_composite_comp_op_value_mapping: typing.ClassVar[dict] = {
        momapy.drawing.CompositionOperator.OVER: "over",
        momapy.drawing.CompositionOperator.IN: "in",
        momapy.drawing.CompositionOperator.OUT: "out",
        momapy.drawing.CompositionOperator.ATOP: "atop",
        momapy.drawing.CompositionOperator.XOR: "xor",
        momapy.drawing.CompositionOperator.LIGHTER: "lighter",
        momapy.drawing.CompositionOperator.ARTIHMETIC: "arithmetic",
    }
    _fe_gaussian_blur_edgemode_value_mapping: typing.ClassVar[dict] = {
        momapy.drawing.EdgeMode.WRAP: "wrap",
        momapy.drawing.EdgeMode.DUPLICATE: "duplicate",
        None: "none",
    }
    _fe_filter_unit_value_mapping: typing.ClassVar[dict] = {
        momapy.drawing.FilterUnits.USER_SPACE_ON_USE: "UserSpaceOnUse",
        momapy.drawing.FilterUnits.OBJECT_BOUNDING_BOX: "objectBoundingBox",
    }
    _fe_input_value_mapping: typing.ClassVar[dict] = {
        momapy.drawing.FilterEffectInput.SOURCE_GRAPHIC: "SourceGraphic",
        momapy.drawing.FilterEffectInput.SOURCE_ALPHA: "SourceAlpha",
        momapy.drawing.FilterEffectInput.BACKGROUND_IMAGE: "BackgroundImage",
        momapy.drawing.FilterEffectInput.BACKGROUND_ALPHA: "BackgroundAlpha",
        momapy.drawing.FilterEffectInput.FILL_PAINT: "FillPaint",
        momapy.drawing.FilterEffectInput.STROKE_PAINT: "StrokePaint",
    }
    _te_font_style_value_mapping: typing.ClassVar[dict] = {
        momapy.drawing.FontStyle.NORMAL: "normal",
        momapy.drawing.FontStyle.ITALIC: "italic",
        momapy.drawing.FontStyle.OBLIQUE: "oblique",
    }
    _te_font_weight_value_mapping: typing.ClassVar[dict] = {
        momapy.drawing.FontWeight.NORMAL: "normal",
        momapy.drawing.FontWeight.BOLD: "bold",
        momapy.drawing.FontWeight.BOLDER: "bolder",
        momapy.drawing.FontWeight.LIGHTER: "lighter",
    }
    _te_text_anchor_value_mapping: typing.ClassVar[dict] = {
        momapy.drawing.TextAnchor.START: "start",
        momapy.drawing.TextAnchor.MIDDLE: "middle",
        momapy.drawing.TextAnchor.END: "end",
    }
    _de_fill_rule_value_mapping: typing.ClassVar[dict] = {
        momapy.drawing.FillRule.NONZERO: "nonzero",
        momapy.drawing.FillRule.EVENODD: "evenodd",
    }

    svg: SVGElement
    config: dict = dataclasses.field(default_factory=dict)
    _filter_elements: list[SVGElement] = dataclasses.field(
        default_factory=list
    )

    @classmethod
    def from_file(cls, output_file, width, height, format_, config=None):
        if config is None:
            config = {}
        config["output_file"] = output_file
        config["width"] = width
        config["height"] = height
        config["format"] = format_
        svg = SVGElement(
            name="svg",
            attributes={
                "xmlns": "http://www.w3.org/2000/svg",
                "viewBox": f"0 0 {width} {height}",
            },
        )
        return cls(svg=svg, config=config)

    def begin_session(self):
        pass

    def end_session(self):
        if self._filter_elements:
            defs = SVGElement(name="defs", elements=self._filter_elements)
            self.svg.add_element(defs)
        if self.config.get("output_file") is not None:
            with open(self.config["output_file"], "w") as f:
                f.write(str(self.svg))

    def new_page(self, width, height):
        pass

    def render_map(self, map_):
        self.render_layout_element(map_.layout)

    def render_layout_element(self, layout_element):
        drawing_elements = layout_element.drawing_elements()
        for drawing_element in drawing_elements:
            self.render_drawing_element(drawing_element)

    def render_drawing_element(self, drawing_element):
        element = self._make_drawing_element_element(drawing_element)
        self.svg.add_element(element)

    def _make_color_value(self, color):
        return f"rgb({color.red}, {color.green}, {color.blue})"

    def _make_opacity_value(self, color):
        return str(color.alpha)

    def _make_transform_value(self, transform):
        value = " ".join(
            [
                self._make_transformation_value(transformation)
                for transformation in transform
            ]
        )
        return value

    def _make_transformation_value(self, transformation):
        class_ = type(transformation)
        if issubclass(class_, momapy.builder.Builder):
            class_ = class_._cls_to_build
        tr_func = getattr(self, self._tr_class_func_mapping[class_])
        return tr_func(transformation)

    def _make_drawing_element_element_id_class_atrributes(
        self, drawing_element
    ):
        attributes = {}
        id_ = getattr(drawing_element, "id_", None)
        if id_ is not None:
            attributes["id"] = id_
        class_ = getattr(drawing_element, "class_", None)
        if class_ is not None:
            attributes["class"] = class_
        return attributes

    def _make_drawing_element_presentation_attributes(self, drawing_element):
        attributes = {}
        for attr_name in momapy.drawing.PRESENTATION_ATTRIBUTES:
            attr_value = getattr(drawing_element, attr_name)
            if attr_value is not None:
                if attr_value == momapy.drawing.NoneValue:
                    attr_value = "none"
                else:
                    if attr_name == "stroke" or attr_name == "fill":
                        opacity_value = self._make_opacity_value(attr_value)
                        attributes[f"{attr_name}-opacity"] = opacity_value
                        attr_value = self._make_color_value(attr_value)
                    elif attr_name == "transform":
                        attr_value = self._make_transform_value(attr_value)
                    elif attr_name == "filter":
                        filter_element = self._make_filter_element(attr_value)
                        if filter_element not in self._filter_elements:
                            self._filter_elements.append(filter_element)
                        attr_value = f"url(#{attr_value.id})"
                    elif attr_name == "font_style":
                        attr_value = self._te_font_style_value_mapping[
                            attr_value
                        ]
                    elif attr_name == "font_weight":
                        if isinstance(attr_value, momapy.drawing.FontWeight):
                            attr_value = self._te_font_weight_value_mapping[
                                attr_value
                            ]
                    elif attr_name == "text_anchor":
                        attr_value = self._te_text_anchor_value_mapping[
                            attr_value
                        ]
                    elif attr_name == "fill_rule":
                        attr_value = self._de_fill_rule_value_mapping[
                            attr_value
                        ]
                    elif attr_name == "stroke_dasharray":
                        attr_value = " ".join(
                            [
                                str(attr_value_element)
                                for attr_value_element in attr_value
                            ]
                        )
                attr_name = attr_name.replace("_", "-")
                attributes[attr_name] = attr_value
        return attributes

    def _make_filter_element(self, filter_):
        name = "filter"
        attributes = {}
        attributes["id"] = filter.id
        attributes["filterUnits"] = self._fe_filter_unit_value_mapping[
            filter.filter_units
        ]
        attributes["x"] = filter.x
        attributes["y"] = filter.y
        attributes["width"] = filter.width
        attributes["height"] = filter.height
        subelements = []
        for filter_effect in filter_.effects:
            subelement = self._make_filter_effect_element(filter_effect)
            subelements.append(subelement)
        element = SVGElement(
            name=name, attributes=attributes, elements=subelements
        )
        return element

    def _make_filter_effect_element(self, filter_effect):
        class_ = type(filter_effect)
        if issubclass(class_, momapy.builder.Builder):
            class_ = class_._cls_to_build
        fe_func = getattr(self, self._fe_class_func_mapping[class_])
        element = fe_func(filter_effect)
        return element

    def _make_drop_shadow_effect_element(self, filter_effect):
        name = "feDropShadow"
        attributes = {}
        attributes["dx"] = filter_effect.dx
        attributes["dy"] = filter_effect.dy
        attributes["stdDeviation"] = filter_effect.std_deviation
        attributes["flood-opacity"] = filter_effect.flood_opacity
        attributes["flood-color"] = self._make_color_value(
            filter_effect.flood_color
        )
        if filter_effect.result is not None:
            attributes["result"] = filter_effect.result
        element = SVGElement(
            name=name,
            attributes=attributes,
        )
        return element

    def _make_composite_effect_element(self, filter_effect):
        name = "feComposite"
        attributes = {}
        if isinstance(filter_effect.in_, momapy.drawing.FilterEffectInput):
            attributes["in"] = self._fe_input_value_mapping[filter_effect.in_]
        else:
            attributes["in"] = filter_effect.in_
        if isinstance(filter_effect.in2, momapy.drawing.FilterEffectInput):
            attributes["in2"] = self._fe_input_value_mapping[filter_effect.in2]
        else:
            attributes["in2"] = filter_effect.in2
        attributes["operator"] = self._fe_composite_comp_op_value_mapping[
            filter_effect.operator
        ]
        if filter_effect.result is not None:
            attributes["result"] = filter_effect.result
        element = SVGElement(
            name=name,
            attributes=attributes,
        )
        return element

    def _make_flood_effect_element(self, filter_effect):
        name = "feFlood"
        attributes = {}
        attributes["flood-opacity"] = filter_effect.flood_opacity
        attributes["flood-color"] = self._make_color_value(
            filter_effect.flood_color
        )
        if filter_effect.result is not None:
            attributes["result"] = filter_effect.result
        element = SVGElement(
            name=name,
            attributes=attributes,
        )
        return element

    def _make_gaussian_blur_effect_element(self, filter_effect):
        name = "feGaussianBlur"
        attributes = {}
        if isinstance(filter_effect.in_, momapy.drawing.FilterEffectInput):
            attributes["in"] = self._fe_input_value_mapping[filter_effect.in_]
        else:
            attributes["in"] = filter_effect.in_
        attributes["stdDeviation"] = filter_effect.std_deviation
        if filter_effect.edge_mode is not None:
            attributes["edgeMode"] = (
                self._fe_gaussian_blur_edgemode_value_mapping[
                    filter_effect.edge_mode
                ]
            )
        if filter_effect.result is not None:
            attributes["result"] = filter_effect.result
        element = SVGElement(
            name=name,
            attributes=attributes,
        )
        return element

    def _make_offset_effect_element(self, filter_effect):
        name = "feOffset"
        attributes = {}
        attributes["dx"] = filter_effect.dx
        attributes["dy"] = filter_effect.dy
        if filter_effect.result is not None:
            attributes["result"] = filter_effect.result
        element = SVGElement(
            name=name,
            attributes=attributes,
        )
        return element

    def _make_drawing_element_element(self, drawing_element):
        class_ = type(drawing_element)
        if issubclass(class_, momapy.builder.Builder):
            class_ = class_._cls_to_build
        de_func = getattr(self, self._de_class_func_mapping[class_])
        element = de_func(drawing_element)
        return element

    def _make_group_element(self, group):
        name = "g"
        presentation_attributes = (
            self._make_drawing_element_presentation_attributes(group)
        )
        id_class_attributes = (
            self._make_drawing_element_element_id_class_atrributes(group)
        )
        attributes = presentation_attributes | id_class_attributes
        subelements = []
        for drawing_element in group.elements:
            subelement = self._make_drawing_element_element(drawing_element)
            subelements.append(subelement)
        element = SVGElement(
            name=name, attributes=attributes, elements=subelements
        )
        return element

    def _make_path_action_value(self, path_action):
        class_ = type(path_action)
        if issubclass(class_, momapy.builder.Builder):
            class_ = class_._cls_to_build
        pa_func = getattr(self, self._pa_class_func_mapping[class_])
        value = pa_func(path_action)
        return value

    def _make_move_to_value(self, move_to):
        return f"M {move_to.x} {move_to.y}"

    def _make_line_to_value(self, line_to):
        return f"L {line_to.x} {line_to.y}"

    def _make_close_value(self, close):
        return "Z"

    def _make_elliptical_arc_value(self, elliptical_arc):
        return (
            f"A {elliptical_arc.rx} "
            f"{elliptical_arc.ry} "
            f"{elliptical_arc.x_axis_rotation} "
            f"{elliptical_arc.arc_flag} "
            f"{elliptical_arc.sweep_flag} "
            f"{elliptical_arc.x} "
            f"{elliptical_arc.y}"
        )

    def _make_quadratic_curve_to_value(self, quadratic_curve_to):
        return (
            f"Q {quadratic_curve_to.control_point.x} "
            f"{quadratic_curve_to.control_point.y} "
            f"{quadratic_curve_to.x} "
            f"{quadratic_curve_to.y}"
        )

    def _make_curve_to_value(self, curve_to):
        return (
            f"C {curve_to.control_point1.x} "
            f"{curve_to.control_point1.y} "
            f"{curve_to.control_point2.x} "
            f"{curve_to.control_point2.y} "
            f"{curve_to.x} "
            f"{curve_to.y}"
        )

    def _make_path_element(self, path):
        name = "path"
        presentation_attributes = (
            self._make_drawing_element_presentation_attributes(path)
        )
        id_class_attributes = (
            self._make_drawing_element_element_id_class_atrributes(path)
        )
        attributes = presentation_attributes | id_class_attributes
        d_value = " ".join(
            [
                self._make_path_action_value(path_action)
                for path_action in path.actions
            ]
        )
        attributes["d"] = d_value
        element = SVGElement(name=name, attributes=attributes)
        return element

    def _make_text_element(self, text):
        name = "text"
        presentation_attributes = (
            self._make_drawing_element_presentation_attributes(text)
        )
        id_class_attributes = (
            self._make_drawing_element_element_id_class_atrributes(text)
        )
        attributes = presentation_attributes | id_class_attributes
        attributes["x"] = text.x
        attributes["y"] = text.y
        value = xml.sax.saxutils.escape(text.text)
        element = SVGElement(name=name, attributes=attributes, value=value)
        return element

    def _make_ellipse_element(self, ellipse):
        name = "ellipse"
        presentation_attributes = (
            self._make_drawing_element_presentation_attributes(ellipse)
        )
        id_class_attributes = (
            self._make_drawing_element_element_id_class_atrributes(ellipse)
        )
        attributes = presentation_attributes | id_class_attributes
        attributes["cx"] = ellipse.x
        attributes["cy"] = ellipse.y
        attributes["rx"] = ellipse.rx
        attributes["ry"] = ellipse.ry
        element = SVGElement(name=name, attributes=attributes)
        return element

    def _make_rectangle_element(self, rectangle):
        name = "rect"
        presentation_attributes = (
            self._make_drawing_element_presentation_attributes(rectangle)
        )
        id_class_attributes = (
            self._make_drawing_element_element_id_class_atrributes(rectangle)
        )
        attributes = presentation_attributes | id_class_attributes
        attributes["x"] = rectangle.x
        attributes["y"] = rectangle.y
        attributes["width"] = rectangle.width
        attributes["height"] = rectangle.height
        attributes["rx"] = rectangle.rx
        attributes["ry"] = rectangle.ry
        element = SVGElement(name=name, attributes=attributes)
        return element

    def _make_translation_value(self, translation):
        return f"translate({translation.tx} {translation.ty})"

    def _make_rotation_value(self, rotation):
        angle = math.degrees(rotation.angle)
        s_point = (
            f" {rotation.point.x} {rotation.point.y}"
            if rotation.point is not None
            else ""
        )
        value = f"rotate({angle}{s_point})"
        return value

    def _make_scaling_value(self, scaling):
        return f"scale({scaling.sx} {scaling.sy})"

    def _make_matrix_transformation_value(self, matrix_transformation):
        matrix_values = [
            matrix_transformation.m[i][j]
            for j in range(len(matrix_transformation.m[0]))
            for i in range(len(matrix_transformation.m) - 1)
        ]
        value = f"matrix({' '.join(matrix_values)})"
        return value


@dataclasses.dataclass
class SVGNativeCompatRenderer(SVGNativeRenderer):
    """Class for SVG native compat renderers"""

    def _make_filter_element(self, filter_):
        filter_ = filter_.to_compat()
        element = super()._make_filter_element(filter_)
        return element


momapy.rendering.core.register_renderer("svg-native", SVGNativeRenderer)
momapy.rendering.core.register_renderer(
    "svg-native-compat", SVGNativeCompatRenderer
)
