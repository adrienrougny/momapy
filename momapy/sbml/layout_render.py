import enums
import dataclasses
import copy

import momapy.core
import momapy.builder


# - no metaidRef attribute: given by he LayoutModelMapping
@dataclasses.dataclass(frozen=True)
class GraphicalObject(momapy.core.LayoutElement):
    bounding_box: momapy.geometry.Bbox

    def bbox(self):
        return self.bounding_box

    def drawing_elements(self):
        return []

    def children(self) -> list["LayoutElement"]:
        return []

    def translated(self, tx, ty) -> list["LayoutElement"]:
        new_bbox = momapy.geometry.Bbox(
            position=self.bounding_box.position + (tx, ty),
            width=self.bounding_box.width,
            height=self.bounding_box.height,
        )
        return dataclasses.replace(self, bounding_box=new_bbox)

    def childless(self) -> "LayoutElement":
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
class _CurveGraphicalObject(GraphicalObject, momapy.core.GroupLayout):
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

        drawing_elements = []
        if len(self.curve) > 0:
            actions = [momapy.drawing.MoveTo(self.curve[0].p1)]
            for segment in self.curve:
                action = _make_path_action_from_segment(segment)
                actions.append(action)
            path = Path(actions=actions)
            drawing_elements.append(path)
        return drawing_elements

    def bbox(self):
        if len(self.curve) > 0:
            return super(GraphicalObject, self).bbox()
        else:
            return super().bbox()


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


@dataclasses.dataclass(frozen=True)
class GeneralGlyph(_CurveGraphicalObject):
    def list_of_subglyphs(self):
        return [
            le
            for le in self.layout_elements
            if momapy.builder.isinstance_or_builder(le, GraphicalObject)
        ]


@dataclasses.dataclass(frozen=True)
class TextGlyph(GraphicalObject, momapy.core.TextLayout):
    pass


# - no reference attribute: given by the LayoutModelMapping


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
