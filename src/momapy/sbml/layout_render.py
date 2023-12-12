import enums
import dataclasses
import copy

import momapy.core
import momapy.builder
import momapy.drawing

# should be moved to IO, will be used when cascading styles during file reading
# all presentation attributes are set to None, their defaults are defined by SVG
# (in momapy.drawing.PRESENTATION_ATTRIBUTES) or by the user agent
DEFAULT_FILL = None
DEFAULT_FILL_RULE = None
DEFAULT_Z = None
DEFAULT_STROKE = None
DEFAULT_STROKE_WIDTH = None
DEFAULT_FONT_FAMILY = None
DEFAULT_FONT_SIZE = None
DEFAULT_FONT_WEIGHT = None
DEFAULT_FONT_STYLE = None
DEFAULT_TEXT_ANCHOR = None
DEFAULT_VTEXT_ANCHOR = None
DEFAULT_START_HEAD = None
DEFAULT_END_HEAD = None
DEFAULT_ENABLE_ROTATIONAL_MAPPING = True


def make_path_from_elements(
    elements,
    bbox,
    close=False,
    fill=None,
    fill_rule=None,
    stroke=None,
    stroke_width=None,
):
    actions = []
    for render_point in elements:
        actions.append(render_point.to_path_action(bbox))
    if close:
        actions.append(momapy.drawing.ClosePath())
    path = momapy.drawing.Path(
        actions=path_actions,
        fill=fill,
        fill_rule=fill_rule,
        stroke=stroke,
        stroke_width=stroke_width,
    )
    return path


def make_path_from_curve(
    curve,
    bbox,
    close=False,
    fill=None,
    fill_rule=None,
    stroke=None,
    stroke_width=None,
):
    actions = [momapy.drawing.MoveTo(self.curve[0].p1)]
    for segment in self.curve:
        action = momapy.core.Arc._make_path_action_from_segment(segment)
        actions.append(action)
    if close:
        actions.append(momapy.drawing.ClosePath())
    path = momapy.drawing.Path(
        actions=path_actions,
        fill=fill,
        fill_rule=fill_rule,
        stroke=stroke,
        stroke_width=stroke_width,
    )
    return path


class VTextAnchor(enums.Enum):
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"
    BASELINE = "baseline"


@dataclasses.dataclass(frozen=True)
class RelAbsVector(object):
    abs: float = 0.0
    rel: float | None = None

    def evaluate(self, length: float) -> float:
        res = self.abs
        if self.rel is not None:
            res += self.rel / 100 * length
        return res

    def __str__(self):
        if self.abs != 0:
            s = str(self.abs)
        if self.rel is not None and self.rel != 0:
            if self.rel < 0:
                s += "-"
            s += f"{self.rel}%"
        return s


# We redefine SBase here. It is already defined in momapy.sbml.core, but there
# it is a child of momapy.core.ModelElement, which is not suitable when
# defining a layout. Here is is a child of object.
@dataclasses.dataclass(frozen=True)
class SBase(object):
    name: str | None = None
    metaid: str | uuid.UUID | None = None
    sbo_term: momapy.sbml.core.SBOTerm | None = None
    notes: momapy.sbml.core.Notes | None = None
    annotations: momapy.sbml.core.Annotation | None = None


# we do not use the momapy.geometry.Point because here we have a z coordinate
# (even if we do not use it) and the coordiantes can be relative, hence we use
# the definition of the spec and use RelAbsVector
@dataclasses.dataclass(frozen=True)
class RenderPoint(SBase):
    x: RelAbsVector
    y: RelAbsVector
    z: RelAbsVector | None = None

    def evaluate(self, bbox: momapy.geometry.Bbox) -> momapy.geometry.Point:
        x = bbox.west().x + self.x.evaluate(bbox.width)
        y = bbox.north().y + self.y.evaluate(bbox.height)
        return momapy.geometry.Point(x, y)

    def to_path_action(self, bbox):
        return momapy.drawing.LineTo(self.evaluate(bbox))


@dataclasses.dataclass(frozen=True)
class RenderCubicBezier(RenderPoint):
    base_point1_x: RelAbsVector
    base_point1_y: RelAbsVector
    base_point2_x: RelAbsVector
    base_point2_y: RelAbsVector
    base_point1_z: RelAbsVector | None = None
    base_point2_z: RelAbsVector | None = None

    def to_path_action(self, bbox):
        point = self.evaluate(bbox)
        control_point1 = RenderPoint(
            x=self.base_point1_x, y=self.base_point1_y
        ).evaluate(bbox)
        control_point2 = RenderPoint(
            x=self.base_point2_x, y=self.base_point2_y
        ).evaluate(bbox)
        return momapy.drawing.CurveTo(
            point=point,
            control_point1=control_point1,
            control_point2=control_point2,
        )


@dataclasses.dataclass(frozen=True)
class Transformation(SBase):
    name: str | None = None
    transform: momapy.geometry.MatrixTransformation | None = None


@dataclasses.dataclass(frozen=True)
class Transformation2D(Transformation, abc.ABC):
    @abc.abstractmethod
    def to_drawing_elements(
        self,
        bbox=None,
        vtext_anchor=None,
        start_head=None,
        end_head=None,
    ):
        pass


@dataclasses.dataclass(frozen=True)
class GraphicalPrimitive1D(Transformation2D):
    id: string | None = None
    stroke: momapy.coloring.Color | None = None
    stroke_width: float | None = None
    stroke_dasharray: tuple[float] | None = None


@dataclasses.dataclass(frozen=True)
class GraphicalPrimitive2D(GraphicalPrimitive1D):
    fill: momapy.coloring.Color | None = None
    fill_rule: momapy.drawing.FillRule = momapy.drawing.FillRule.NONZERO


@dataclasses.dataclass(frozen=True)
class LineEnding(GraphicalPrimitive2D):
    id: str
    bounding_box: momapy.geometry.Bbox
    g: RenderGroup
    enable_rotational_mapping: bool | None = True

    def to_drawing_elements(
        self,
        bbox=None,
        vtext_anchor=None,
        start_head=None,
        end_head=None,
    ):
        return g.to_drawing_elements(
            bbox=self.bounding_box,
            vtext_anchor=vtext_anchor,
            start_head=start_head,
            end_head=end_head,
        )


@dataclasses.dataclass(frozen=True)
class RenderCurve(GraphicalPrimitive1D):
    start_head: LineEnding | None = None
    end_head: LineEnding | None = None
    elements: tuple[RenderPoint] = dataclasses.field(default_factory=tuple)
    curve: tuple[
        momapy.geometry.Segment | momapy.geometry.BezierCurve
    ] = dataclasses.field(default_factory=tuple)

    def points(self, bbox) -> list[momapy.geometry.Point]:
        points = []
        if len(self.elements) > 0:
            for render_point in self.elements:
                points.append(render_point.evaluate(bbox))
            return points
        elif len(self.curve) > 0:
            points.append(self.curve[0].p1)
            for segment in self.curve:
                points.append(segment.p2)
            return points
        return []

    def to_drawing_elements(
        self,
        bbox,
        vtext_anchor=None,
        start_head=None,
        end_head=None,
    ):
        elements = []
        if len(self.elements) > 0:
            path = make_path_from_elements(elements=self.elements, bbox=bbox)
            elements.append(path)
        elif len(self.curve) > 0:
            path = make_path_from_curve(curve=self.curve, bbox=bbpx)
            elements.append(path)
        if self.start_head is not None:
            start_head = self.start_head
        if self.end_head is not None:
            end_head = self.end_head
        points = self.points()
        if start_head is not None:
            start_point = points[0]
            start_head_drawing_elements = start_head.to_drawing_elements()
            start_translation = momapy.geometry.Translation(
                start_point.x, start_point.y
            )
            start_head_drawing_elements = [
                de.transformed(start_translation)
                for de in start_head_drawing_elements
            ]
            if start_head.enable_rotational_mapping:
                line = momapy.geometry.Line(points[1], start_point)
                angle = line.get_angle_to_horizontal()
                start_rotation = momapy.geometry.Rotation(angle, start_point)
                start_head_drawing_elements = [
                    de.transformed(start_rotation)
                    for de in start_head_drawing_elements
                ]
            elements += start_head_drawing_elements
        if end_head is not None:
            end_point = points[-1]
            end_head_drawing_elements = end_head.to_drawing_elements()
            end_translation = momapy.geometry.Translation(
                end_point.x, end_point.y
            )
            end_head_drawing_elements = [
                de.transformed(end_translation)
                for de in end_head_drawing_elements
            ]
            if end_head.enable_rotational_mapping:
                line = momapy.geometry.Line(points[-2], end_point)
                angle = line.get_angle_to_horizontal()
                end_rotation = momapy.geometry.Rotation(angle, end_point)
                end_head_drawing_elements = [
                    de.transformed(end_rotation)
                    for de in end_head_drawing_elements
                ]
            elements += end_head_drawing_elements
        group = momapy.drawing.Group(
            elements=elements,
            stroke=self.stroke,
            stroke_dasharray=self.stroke_dasharray,
            stroke_width=self.stroke_width,
            transform=(self.transform,),
        )
        return [group]


@dataclasses.dataclass(frozen=True)
class RenderGroup(GraphicalPrimitive2D):
    start_head: LineEnding | None = None
    end_head: LineEnding | None = None
    font_family: str | None = None
    font_size: float | None = None
    font_style: momapy.drawing.FontStyle | None = None
    font_weight: str | None = None
    text_anchor: momapy.drawing.TextAnchor | None = None
    vtext_anchor: VTextAnchor | None = None  # not implemented
    elements: tuple[Transformation2D] = dataclasses.field(default_factory=tuple)

    def to_drawing_elements(
        self,
        bbox,
        vtext_anchor=None,
        start_head=None,
        end_head=None,
    ):
        group_elements = []
        for element in self.elements:
            group_elements += element.to_drawing_elements(
                bbox=bbox,
                vtext_anchor=self.vtext_anchor,
                start_head=self.start_head,
                end_head=self.end_head,
            )
        group = momapy.drawing.Group(elements=group_elements)
        return [group]


@dataclasses.dataclass(frozen=True)
class Text(GraphicalPrimitive1D):
    value: str
    x: RelAbsVector
    y: RelAbsVector
    z: RelAbsVector | None = None
    font_family: str | None = None
    font_size: float | None = None
    font_weight: momapy.drawing.FontWeight | None = None
    font_style: momapy.drawing.FontStyle | None = None
    text_anchor: momapy.drawing.TextAnchor | None = None
    vtext_anchor: VTextAnchor | None = None  # not implemented

    def to_drawing_elements(
        self,
        bbox,
        vtext_anchor=None,
        start_head=None,
        end_head=None,
    ):
        text = momapy.drawing.Text(
            text=self.value,
            point=RenderPoint(self.x, self.y).evaluate(bbox),
            fill=self.fill,
            font_family=self.font_family,
            font_size=self.font_size,
            font_style=self.font_style,
            font_weight=self.font_weight,
            stroke=self.stroke,
            stroke_dasharray=self.stroke_dasharray,
            stroke_width=self.stroke_width,
            text_anchor=self.text_anchor,
            vtext_anchor=self.vtext_anchor,
        )
        return [text]


@dataclasses.dataclass(frozen=True)
class Ellipse(GraphicalPrimitive2D):
    cx: RelAbsVector
    cy: RelAbsVector
    cz: RelAbsVector | None = None
    rx: RelAbsVector
    ry: RelAbsVector
    rz: RelAbsVector | None = None
    ratio: float | None = None

    def to_drawing_elements(
        self,
        bbox,
        vtext_anchor=None,
        start_head=None,
        end_head=None,
    ):
        ellipse = momapy.drawing.Ellipse(
            point=RenderPoint(self.cx, self.cy).evaluate(bbox),
            rx=self.rx.evaluate(bbox.width),
            ry=self.ry.evaluate(bbox.height),
            fill=self.fill,
            stroke=self.stroke,
            stroke_dasharray=self.stroke_dasharray,
            stroke_width=self.stroke_width,
        )
        return [ellipse]


@dataclasses.dataclass(frozen=True)
class Rectangle(GraphicalPrimitive2D):
    x: RelAbsVector
    y: RelAbsVector
    z: RelAbsVector | None = None
    width: RelAbsVector
    height: RelAbsVector
    rx: RelAbsVector | None = None
    ry: RelAbsVector | None = None
    ratio: float | None = None

    def to_drawing_elements(
        self,
        bbox,
        vtext_anchor=None,
        start_head=None,
        end_head=None,
    ):
        rectangle = momapy.drawing.Rectangle(
            point=RenderPoint(self.x, self.y).evaluate(bbox),
            width=self.width.evaluate(bbox.width),
            height=self.height.evaluate(bbox.height),
            rx=self.rx.evaluate(bbox.width),
            ry=self.ry.evaluate(bbox.height),
            fill=self.fill,
            stroke=self.stroke,
            stroke_dasharray=self.stroke_dasharray,
            stroke_width=self.stroke_width,
        )
        return [rectangle]


@dataclasses.dataclass(frozen=True)
class Polygon(GraphicalPrimitive2D):
    elements: tuple[RenderPoint] = dataclasses.field(default_factory=tuple)
    curve: tuple[
        momapy.geometry.Segment | momapy.geometry.BezierCurve
    ] = dataclasses.field(default_factory=tuple)

    def to_drawing_elements(
        self,
        bbox,
        vtext_anchor=None,
        start_head=None,
        end_head=None,
    ):
        if len(self.elements) > 0:
            path = make_path_from_elements(
                elements=self.elements,
                bbox=bbox,
                close=True,
                fill=self.fill,
                fill_rule=self.fill_rule,
                stroke=self.stroke,
                stroke_dasharray=self.stroke_dasharray,
                stroke_width=self.stroke_width,
            )
        else:
            path = make_path_from_curve(
                curve=self.curve,
                bbox=bbox,
                fill=self.fill,
                fill_rule=self.fill_rule,
                stroke=self.stroke,
                stroke_dasharray=self.stroke_dasharray,
                stroke_width=self.stroke_width,
                close=True,
            )
        return [path]


# - no metaidRef attribute: given by he LayoutModelMapping
@dataclasses.dataclass(frozen=True)
class GraphicalObject(momapy.core.LayoutElement):
    bounding_box: momapy.geometry.Bbox
    g: RenderGroup | None = None

    def bbox(self) -> momapy.geometry.Bbox:
        if len(self.drawing_elements) != 0:
            return super().bbox()
        else:
            return self.bounding_box

    def drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        if self.g is not None:
            return self.g.to_drawing_elements(bbox=self.bounding_box)
        return []

    def children(self) -> list[momapy.core.LayoutElement]:
        return []

    def childless(self) -> momapy.core.LayoutElement:
        return copy.deepcopy(self)


# - no compartment attribute: given by the LayoutModelMapping
# - no order attribute: given by the order in the tuple of LayoutElements it belongs to
@dataclasses.dataclass(frozen=True)
class CompartmentGlyph(GraphicalObject):
    pass


# - no species attribute: given by the LayoutModelMapping
@dataclasses.dataclass(frozen=True)
class SpeciesGlyph(GraphicalObject):
    pass


@dataclasses.dataclass(frozen=True)
class _CurveGraphicalObject(momapy.core.GroupLayout, GraphicalObject):
    curve: tuple[
        momapy.geometry.Segment | momapy.geometry.BezierCurve
    ] = dataclasses.field(default_factory=tuple)

    def self_drawing_elements(self):
        if self.g is not None:
            # if the layout element has a curve, we remove all RenderCurve
            # objects from its RenderGroup and add a new RenderCurve object
            # formed with the layout element's curve. The new RenderCurve
            # object replaces the first RenderCurve object of the RenderGroup,
            # or is placed as the first element of the RenderGroup if the latter
            # does not contain any RenderCurve object.
            if len(self.curve) > 0:
                new_elements = []
                new_render_curve = RenderCurve(curve=self.curve)
                done = False
                for element in self.g.elements:
                    if not momapy.builder.isinstance_or_builder(
                        element, RenderCurve
                    ):
                        new_elements.append(element)
                    elif not done:
                        new_elements.append(new_render_curve)
                        done = True
                if not done:
                    new_elements = [new_render_curve] + new_elements
                new_g = dataclasses.replace(self.g, elements=new_elements)
                return new_g.to_drawing_elements(bbox=self.bounding_box)
            else:
                return self.g.to_drawing_elements(bbox=self.bounding_box)
        elif len(self.curve) > 0:
            return [
                make_path_from_curve(curve=self.curve, bbox=self.bounding_box)
            ]
        return []

    def self_bbox(self):
        if len(self.drawing_elements) > 0:
            return super().bbox()
        return self.bounding_box


# - no speciesReference attribute: given by the LayoutModelMapping
@dataclasses.dataclass(frozen=True)
class SpeciesReferenceGlyph(_CurveGraphicalObject):
    role: SpeciesReferenceRole
    species_glyph: SpeciesGlyph


# - no reaction attribute: given by the LayoutModelMapping
@dataclasses.dataclass(frozen=True)
class ReactionGlyph(_CurveGraphicalObject):
    def species_reference_glyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, SpeciesReferenceGlyph)
        ]


# - no reference attribute: given by the LayoutModelMapping
@dataclasses.dataclass(frozen=True)
class ReferenceGlyph(_CurveGraphicalObject):
    glyph: GraphicalObject
    role: str | SpeciesReferenceRole

    def subglyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, GraphicalObject)
        ]


# - no reference attribute: given by the LayoutModelMapping
@dataclasses.dataclass(frozen=True)
class GeneralGlyph(_CurveGraphicalObject):
    def subglyphs(self):  # also contains referenceGlyphs
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, GraphicalObject)
        ]

    def reference_glyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, ReferenceGlyph)
        ]


# - no originOfText to ensure a strict separation between the model and the layout
@dataclasses.dataclass(frozen=True)
class TextGlyph(GraphicalObject):
    graphical_object: GraphicalObject | None = None
    text: str | None = None

    def drawing_elements(self):
        if self.g:
            if self.text is not None:
                new_elements = []
                new_text = Text(
                    x=RelAbsVector(abs=self.bounding_box.position.x),
                    y=RelAbsVector(abs=self.bounding_box.position.y),
                )
                done = False
                for element in self.g.elements:
                    if not momapy.builder.isinstance_or_builder(element, Text):
                        new_elements.append(element)
                    elif not done:
                        new_elements.append(new_text)
                        done = True
                if not done:
                    new_elements = [new_text] + new_elements
                new_g = dataclasses.replace(self.g, elements=new_elements)
                return new_g.to_drawing_elements(bbox=self.bounding_box)
            else:
                return self.g.to_drawing_elements(bbox=self.bounding_box)
        elif self.text is not None:
            return [momapy.drawing.Text(point=self.bounding_box.position)]
        return []


class SpeciesReferenceRole(enums.Enum):
    SUBSTRATE = 0
    PRODUCT = 1
    SIDE_SUBSTRATE = 2
    SIDE_PRODUCT = 3
    MODIFIER = 4
    ACTIVATOR = 5
    INHIBITOR = 6
    UNDEFINED = 7


@dataclasses.dataclass(frozen=True)
class SBMLLayout(momapy.core.Layout):
    name: str | None = None

    def compartment_glyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, CompartmentGlyph)
        ]

    def species_glyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, SpeciesGlyph)
        ]

    def reaction_glyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, ReactionGlyph)
        ]

    def text_glyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, TextGlyph)
        ]

    def additional_graphical_objects(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(
                le, (GeneralGlyph, GraphicalObject)
            )
            and not momapy.builder.isinstance_or_builder(
                le, (CompartmentGlyph, SpeciesGlyph, ReactionGlyph, TextGlyph)
            )
        ]
