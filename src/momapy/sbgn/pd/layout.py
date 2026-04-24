"""Layout classes for SBGN Process Description (PD) maps."""

import dataclasses
import typing

import momapy.drawing
import momapy.meta.arcs
import momapy.meta.shapes

from momapy.coloring import Color
from momapy.core.elements import Direction
from momapy.core.layout import Shape
from momapy.geometry import Point
from momapy.sbgn.elements import (
    SBGNNode,
    SBGNSingleHeadedArc,
    _ConnectorsMixin,
    _MultiMixin,
    _SimpleMixin,
    _TextMixin,
)
from momapy.sbgn.layout import SBGNLayout


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDLayout(SBGNLayout):
    """Class for SBGN-PD layouts"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateVariableLayout(_SimpleMixin, SBGNNode):
    """Class for state variable layouts"""

    width: float = dataclasses.field(
        default=12.0, metadata={"description": "The width of the state variable layout"}
    )
    height: float = dataclasses.field(
        default=12.0,
        metadata={"description": "The height of the state variable layout"},
    )

    def _make_shape(self):
        return momapy.meta.shapes.Stadium(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Class for unit of information layouts"""

    width: float = 12.0
    height: float = 12.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalLayout(_SimpleMixin, SBGNNode):
    """Class for terminal layouts"""

    width: float = 35.0
    height: float = 35.0
    direction: Direction = Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return TagLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CardinalityLayout(_SimpleMixin, SBGNNode):
    """Class for cardinality layouts"""

    width: float = 12.0
    height: float = 19.0

    def _make_shape(self):
        return UnitOfInformationLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntitySubunitLayout(_SimpleMixin, SBGNNode):
    """Class for unspecified entity subunit layouts"""

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return UnspecifiedEntityLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalSubunitLayout(_SimpleMixin, SBGNNode):
    """Class for simple chemical subunit layouts"""

    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return SimpleChemicalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeSubunitLayout(_SimpleMixin, SBGNNode):
    """Class for macromolecule subunit layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureSubunitLayout(_SimpleMixin, SBGNNode):
    """Class for nucleic acid feature subunit layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return NucleicAcidFeatureLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexSubunitLayout(_SimpleMixin, SBGNNode):
    """Class for complex subunit layouts"""

    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 5.0

    def _make_shape(self):
        return ComplexLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimerSubunitLayout(_MultiMixin, SBGNNode):
    """Class for simple chemical multimer subunit layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 60.0
    height: float = 30.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Stadium(
            position=position,
            width=width,
            height=height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimerSubunitLayout(_MultiMixin, SBGNNode):
    """Class for macromolecule multimer subunit layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Rectangle(
            position=position,
            width=width,
            height=height,
            top_left_rx=self.rounded_corners,
            top_left_ry=self.rounded_corners,
            top_right_rx=self.rounded_corners,
            top_right_ry=self.rounded_corners,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureMultimerSubunitLayout(_MultiMixin, SBGNNode):
    """Class for nucleic acid feature multimer subunit layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Rectangle(
            position=position,
            width=width,
            height=height,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexMultimerSubunitLayout(_MultiMixin, SBGNNode):
    """Class for complex multimer subunit layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 5.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Rectangle(
            position=position,
            width=width,
            height=height,
            top_left_rx=self.cut_corners,
            top_left_ry=self.cut_corners,
            top_left_rounded_or_cut="cut",
            top_right_rx=self.cut_corners,
            top_right_ry=self.cut_corners,
            top_right_rounded_or_cut="cut",
            bottom_left_rx=self.cut_corners,
            bottom_left_ry=self.cut_corners,
            bottom_left_rounded_or_cut="cut",
            bottom_right_rx=self.cut_corners,
            bottom_right_ry=self.cut_corners,
            bottom_right_rounded_or_cut="cut",
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompartmentLayout(_SimpleMixin, SBGNNode):
    """Class for compartment layouts"""

    width: float = 80.0
    height: float = 80.0
    rounded_corners: float = 5.0
    stroke_width: float = 3.25

    def _make_shape(self):
        return MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SubmapLayout(
    _SimpleMixin,
    SBGNNode,
):
    """Class for submap layouts"""

    width: float = 80.0
    height: float = 80.0
    stroke_width: float = 2.25

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityLayout(_SimpleMixin, SBGNNode):
    """Class for unspecified entity layouts"""

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalLayout(_SimpleMixin, SBGNNode):
    """Class for simple chemical layouts"""

    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Stadium(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeLayout(_SimpleMixin, SBGNNode):
    """Class for macromolecule layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position,
            width=self.width,
            height=self.height,
            top_left_rx=self.rounded_corners,
            top_left_ry=self.rounded_corners,
            top_right_rx=self.rounded_corners,
            top_right_ry=self.rounded_corners,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureLayout(_SimpleMixin, SBGNNode):
    """Class for nucleic acid feature layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position,
            width=self.width,
            height=self.height,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexLayout(_SimpleMixin, SBGNNode):
    """Class for complex layouts"""

    width: float = 44.0
    height: float = 44.0
    cut_corners: float = 5.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position,
            width=self.width,
            height=self.height,
            top_left_rx=self.cut_corners,
            top_left_ry=self.cut_corners,
            top_left_rounded_or_cut="cut",
            top_right_rx=self.cut_corners,
            top_right_ry=self.cut_corners,
            top_right_rounded_or_cut="cut",
            bottom_left_rx=self.cut_corners,
            bottom_left_ry=self.cut_corners,
            bottom_left_rounded_or_cut="cut",
            bottom_right_rx=self.cut_corners,
            bottom_right_ry=self.cut_corners,
            bottom_right_rounded_or_cut="cut",
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimerLayout(_MultiMixin, SBGNNode):
    """Class for simple chemical multimer layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 30.0
    height: float = 30.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Stadium(
            position=position,
            width=width,
            height=height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimerLayout(_MultiMixin, SBGNNode):
    """Class for macromolecule multimer layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Rectangle(
            position=position,
            width=width,
            height=height,
            top_left_rx=self.rounded_corners,
            top_left_ry=self.rounded_corners,
            top_right_rx=self.rounded_corners,
            top_right_ry=self.rounded_corners,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureMultimerLayout(_MultiMixin, SBGNNode):
    """Class for nucleic acid feature multimer layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Rectangle(
            position=position,
            width=width,
            height=height,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexMultimerLayout(_MultiMixin, SBGNNode):
    """Class for complex multimer layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 44.0
    height: float = 44.0
    cut_corners: float = 5.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Rectangle(
            position=position,
            width=width,
            height=height,
            top_left_rx=self.cut_corners,
            top_left_ry=self.cut_corners,
            top_left_rounded_or_cut="cut",
            top_right_rx=self.cut_corners,
            top_right_ry=self.cut_corners,
            top_right_rounded_or_cut="cut",
            bottom_left_rx=self.cut_corners,
            bottom_left_ry=self.cut_corners,
            bottom_left_rounded_or_cut="cut",
            bottom_right_rx=self.cut_corners,
            bottom_right_ry=self.cut_corners,
            bottom_right_rounded_or_cut="cut",
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _EmptySetShape(Shape):
    position: Point
    width: float
    height: float

    def drawing_elements(self):
        circle = momapy.drawing.Ellipse(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        actions = [
            momapy.drawing.MoveTo(self.position - (self.width / 2, -self.height / 2)),
            momapy.drawing.LineTo(self.position + (self.width / 2, -self.height / 2)),
        ]
        bar = momapy.drawing.Path(actions=actions)
        return [circle, bar]


@dataclasses.dataclass(frozen=True, kw_only=True)
class EmptySetLayout(_SimpleMixin, SBGNNode):
    """Class for empty set layouts"""

    width: float = 22.0
    height: float = 22.0

    def _make_shape(self):
        return _EmptySetShape(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbingAgentLayout(_SimpleMixin, SBGNNode):
    """Class for perturbing agent layouts"""

    width: float = 60.0
    height: float = 30.0
    angle: float = 70.0

    def _make_shape(self):
        return momapy.meta.shapes.Hexagon(
            position=self.position,
            width=self.width,
            height=self.height,
            left_angle=180 - self.angle,
            right_angle=180 - self.angle,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndOperatorLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
    SBGNNode,
):
    """Class for and operator layouts"""

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    text: str = "AND"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrOperatorLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
    SBGNNode,
):
    """Class for or operator layouts"""

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    text: str = "OR"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotOperatorLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
    SBGNNode,
):
    """Class for not operator layouts"""

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    text: str = "NOT"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
    SBGNNode,
):
    """Class for equivalence operator layouts"""

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 2
    text: str = "≡"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProcessLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    SBGNNode,
):
    """Class for generic process layouts"""

    width: float = 20.0
    height: float = 20.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OmittedProcessLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
    SBGNNode,
):
    """Class for omitted process layouts"""

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 1.5
    text: str = "\\\\"
    width: float = 20.0
    height: float = 20.0

    def _make_shape(self):
        return GenericProcessLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UncertainProcessLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
    SBGNNode,
):
    """Class for uncertain process layouts"""

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 1.5
    text: str = "?"
    width: float = 20.0
    height: float = 20.0

    def _make_shape(self):
        return GenericProcessLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class AssociationLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    SBGNNode,
):
    """Class for association layouts"""

    width: float = 20.0
    height: float = 20.0

    fill: momapy.drawing.NoneValueType | Color | None = momapy.coloring.black

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _DissociationShape(Shape):
    position: Point
    width: float
    height: float
    sep: float

    def drawing_elements(self):
        outer_circle = momapy.drawing.Ellipse(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        inner_circle = momapy.drawing.Ellipse(
            point=self.position,
            rx=self.width / 2 - self.sep,
            ry=self.height / 2 - self.sep,
        )
        return [outer_circle, inner_circle]


@dataclasses.dataclass(frozen=True, kw_only=True)
class DissociationLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    SBGNNode,
):
    """Class for dissociation layouts"""

    width: float = 20.0
    height: float = 20.0
    sep: float = 3.0

    def _make_shape(self):
        return _DissociationShape(
            position=self.position,
            width=self.width,
            height=self.height,
            sep=self.sep,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(
    _SimpleMixin,
    SBGNNode,
):
    """Class for phenotype layouts"""

    width: float = 60.0
    height: float = 30.0
    angle: float = 70.0

    def _make_shape(self):
        return momapy.meta.shapes.Hexagon(
            position=self.position,
            width=self.width,
            height=self.height,
            left_angle=self.angle,
            right_angle=self.angle,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagLayout(_SimpleMixin, SBGNNode):
    """Class for tag layouts"""

    width: float = 35.0
    height: float = 35.0
    direction: Direction = Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        if self.direction == Direction.RIGHT:
            return momapy.meta.shapes.Hexagon(
                position=self.position,
                width=self.width,
                height=self.height,
                left_angle=90.0,
                right_angle=self.angle,
            )
        elif self.direction == Direction.LEFT:
            return momapy.meta.shapes.Hexagon(
                position=self.position,
                width=self.width,
                height=self.height,
                left_angle=self.angle,
                right_angle=90.0,
            )
        elif self.direction == Direction.UP:
            return momapy.meta.shapes.TurnedHexagon(
                position=self.position,
                width=self.width,
                height=self.height,
                top_angle=self.angle,
                bottom_angle=90.0,
            )
        elif self.direction == Direction.DOWN:
            return momapy.meta.shapes.TurnedHexagon(
                position=self.position,
                width=self.width,
                height=self.height,
                top_angle=90.0,
                bottom_angle=self.angle,
            )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ConsumptionLayout(SBGNSingleHeadedArc):
    """Class for consumption layouts"""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProductionLayout(SBGNSingleHeadedArc):
    """Class for production layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | Color | None = momapy.coloring.black
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModulationLayout(SBGNSingleHeadedArc):
    """Class for modulation layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | Color | None = momapy.coloring.white
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Diamond._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class StimulationLayout(SBGNSingleHeadedArc):
    """Class for stimulation layouts"""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulationLayout(SBGNSingleHeadedArc):
    """Class for necessary stimulation layouts"""

    arrowhead_bar_height: float = 12.0
    arrowhead_sep: float = 3.0
    arrowhead_triangle_height: float = 10.0
    arrowhead_triangle_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        actions = [
            momapy.drawing.MoveTo(Point(0, -self.arrowhead_bar_height / 2)),
            momapy.drawing.LineTo(Point(0, self.arrowhead_bar_height / 2)),
        ]
        bar = momapy.drawing.Path(actions=actions)
        actions = [
            momapy.drawing.MoveTo(Point(0, 0)),
            momapy.drawing.LineTo(Point(self.arrowhead_sep, 0)),
        ]
        sep = momapy.drawing.Path(actions=actions)
        triangle = momapy.meta.shapes.Triangle(
            position=Point(self.arrowhead_sep + self.arrowhead_triangle_width / 2, 0),
            width=self.arrowhead_triangle_width,
            height=self.arrowhead_triangle_height,
            direction=Direction.RIGHT,
        )
        return [bar, sep] + triangle.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class CatalysisLayout(SBGNSingleHeadedArc):
    """Class for catalysis layouts"""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Ellipse._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class InhibitionLayout(SBGNSingleHeadedArc):
    """Class for inhibition layouts"""

    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Bar._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(SBGNSingleHeadedArc):
    """Class for logic arc layouts"""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(SBGNSingleHeadedArc):
    """Class for equivalence arc layouts"""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)
