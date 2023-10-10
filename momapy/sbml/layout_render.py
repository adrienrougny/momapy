import enums
import dataclasses
import copy

import momapy.core
import momapy.builder
import momapy.drawing


class VTextAnchor(enums.Enum):
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"
    BASELINE = "baseline"


@dataclasses.dataclass(frozen=True)
class RelAbsVector(object):
    abs: float = 0.0
    rel: float | None = None

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
        x = bbox.west().x + self.x.abs
        if self.x.rel is not None:
            x += self.x.rel * bbox.width
        y = bbox.north().x + self.y.abs
        if self.y.rel is not None:
            y += self.y.rel * bbox.height
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
    def to_drawing_elements(self, bbox=None, from_=None):
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

    def to_drawing_elements(self, bbox=None, from_=None):
        return g.to_drawing_elements(self.bounding_box)


@dataclasses.dataclass(frozen=True)
class RenderCurve(GraphicalPrimitive1D):
    start_head: LineEnding | None = None
    end_head: LineEnding | None = None
    elements: tuple[RenderPoint] = dataclasses.field(default_factory=tuple)
    curve: tuple[
        momapy.geometry.Segment | momapy.geometry.BezierCurve
    ] = dataclasses.field(default_factory=tuple)

    def to_drawing_elements(self, bbox, from_=None):
        if (
            self.start_head is None
            and from_ is not None
            and from_.start_head is not None
        ):
            start_head = from_.start_head
        else:
            start_head = self.start_head
        return []


@dataclasses.dataclass(frozen=True)
class RenderGroup(GraphicalPrimitive2D):
    start_head: LineEnding | None = None
    end_head: LineEnding | None = None
    font_family: str | None = None
    font_size: float | None = None
    font_weight: str | None = None
    text_anchor: momapy.drawing.TextAnchor
    vtext_anchor: VTextAnchor  # not implemented
    elements: tuple[Transformation2D] = dataclasses.field(default_factory=tuple)

    def to_drawing_elements(self, bbox, from_=None):
        group_elements = []
        for element in self.elements:
            group_elements += element.to_drawing_elements(bbox, from_=self)
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
    font_weight: momapy.drawing.FontWeight
    font_style: momapy.drawing.FontStyle
    text_anchor: momapy.drawing.TextAnchor
    vtext_anchor: VTextAnchor  # not implemented

    def to_drawing_elements(self, bbox, font_family=None):
        if self.font_family is not None:
            font_family = self.font_family
        elif (
            font_family is None
        ):  # only possible if not called from RenderGroup
            font_family = DEFAULT_FONT_FAMILY
        text = momapy.drawing.Text(
            stroke_width=stroke_width,
            stroke=stroke,
            fill=fill,
            text_anchor=text_anchor,
            text=value,
            point=RenderPoint(self.x, self.y).evaluate(bbox),
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

    def to_drawing_elements(self, bbox):
        return []


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

    def to_drawing_elements(self, bbox):
        return []


@dataclasses.dataclass(frozen=True)
class Polygon(GraphicalPrimitive2D):
    elements: tuple[RenderPoint] = dataclasses.field(default_factory=tuple)
    curve: tuple[
        momapy.geometry.Segment | momapy.geometry.BezierCurve
    ] = dataclasses.field(default_factory=tuple)

    def to_drawing_elements(self, bbox):
        return []


# - no metaidRef attribute: given by he LayoutModelMapping
@dataclasses.dataclass(frozen=True)
class GraphicalObject(momapy.core.LayoutElement):
    bounding_box: momapy.geometry.Bbox
    g: RenderGroup | None = None

    def bbox(self) -> momapy.geometry.Bbox:
        if self.g is not None:
            group = self.g.to_drawing_elements(self.bounding_box)[0]
            return group.bbox()
        return self.bounding_box

    def drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        if self.g is not None:
            group = self.g.to_drawing_elements(self.bounding_box)[0]
            return [group]
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

    def _make_curve_path(self):
        def _make_path_action_from_segment(segment):
            if momapy.builder.isinstance_or_builder(
                segment, momapy.geometry.Segment
            ):
                path_action = momapy.drawing.LineTo(segment.p2)
            elif momapy.builder.isinstance_or_builder(
                segment, momapy.geometry.BezierCurve
            ):
                path_action = momapy.drawing.CurveTo(
                    segment.p2,
                    segment.control_points[0],
                    segment.control_points[1],
                )
            return path_action

        actions = [momapy.drawing.MoveTo(self.curve[0].p1)]
        for segment in self.curve:
            action = _make_path_action_from_segment(segment)
            actions.append(action)
        path = Path(actions=actions)
        return path

    def self_drawing_elements(self):
        if self.g is not None:
            group = self.g.to_drawing_elements(self.bounding_box)[0]
            if len(self.curve) > 0:
                curve_path = self._make_curve_path()
                group = dataclasses.replace(group, elements=[curve_path])
            return [group]
        elif len(self.curve) > 0:
            return [self._make_curve_path()]
        return []

    def self_bbox(self):
        if self.g is not None or len(self.curve) != 0:
            return super(GraphicalObject, self).self_bbox()
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
class TextGlyph(GraphicalObject, momapy.core.TextLayout):
    graphical_object: GraphicalObject | None = None


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
