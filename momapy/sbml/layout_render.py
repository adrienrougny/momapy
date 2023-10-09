import enums
import dataclasses
import copy

import momapy.core
import momapy.builder


@dataclasses.dataclass(frozen=True)
class GraphicalPrimitive1D:
    id: string
    stroke: momapy.coloring.Color | None = None
    stroke_width: float | None = None


@dataclasses.dataclass(frozen=True)
class GraphicalPrimitive2D:
    pass


@dataclasses.dataclass(frozen=True)
class LineHeading(GraphicalPrimitive2D):
    bounding_box: momapy.geometry.Bbox
    g: RenderGroup


@dataclasses.dataclass(frozen=True)
class RenderGroup(GraphicalPrimitive2D):
    startHead: LineHeading | None = None
    endHead: LineHeading | None = None


@dataclasses.dataclass(frozen=True)
class RenderCurve(GraphicalPrimitive1D):
    startHead: LineHeading | None = None
    endHead: LineHeading | None = None


def _render_group_to_drawing_elements(g):
    drawing_elements = []
    return drawing_elements


# - no metaidRef attribute: given by he LayoutModelMapping
@dataclasses.dataclass(frozen=True)
class GraphicalObject(momapy.core.LayoutElement):
    bounding_box: momapy.geometry.Bbox
    g: RenderGroup | None = None

    def bbox(self) -> momapy.geometry.Bbox:
        return self.bounding_box

    def drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        if self.g is not None:
            return _render_group_to_drawing_elements(self.g)
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

        if self.g is not None:
            return _render_group_to_drawing_elements(self.g)
        elif len(self.curve) > 0:
            actions = [momapy.drawing.MoveTo(self.curve[0].p1)]
            for segment in self.curve:
                action = _make_path_action_from_segment(segment)
                actions.append(action)
            path = Path(actions=actions)
            return path
        return []

    def self_bbox(self):
        if self.g is not None or len(self.curve) > 0:
            return super(GraphicalObject, self).bbox()
        else:
            return super().bbox()


# - no speciesReference attribute: given by the LayoutModelMapping
@dataclasses.dataclass(frozen=True)
class SpeciesReferenceGlyph(_CurveGraphicalObject):
    role: SpeciesReferenceRole
    species_glyph: SpeciesGlyph


# - no reaction attribute: given by the LayoutModelMapping
@dataclasses.dataclass(frozen=True)
class ReactionGlyph(_CurveGraphicalObject):
    def list_of_species_reference_glyphs(self):
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

    def list_of_subglyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, GraphicalObject)
        ]


# - no reference attribute: given by the LayoutModelMapping
@dataclasses.dataclass(frozen=True)
class GeneralGlyph(_CurveGraphicalObject):
    def list_of_subglyphs(self):  # also contains referenceGlyphs
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, GraphicalObject)
        ]

    def list_of_reference_glyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, ReferenceGlyph)
        ]


# - no originOfText to ensure a strict separation between the model and the layout
@dataclasses.dataclass(frozen=True)
class TextGlyph(GraphicalObject, momapy.core.TextLayout):
    graphicalObject: GraphicalObject | None = None


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

    def list_of_compartment_glyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, CompartmentGlyph)
        ]

    def list_of_species_glyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, SpeciesGlyph)
        ]

    def list_of_reaction_glyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, ReactionGlyph)
        ]

    def list_of_text_glyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, TextGlyph)
        ]

    def list_of_additional_graphical_objects(self):
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
