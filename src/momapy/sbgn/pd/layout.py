"""Layout classes for SBGN Process Description (PD) maps."""

import dataclasses
import math
import sys
import typing

import momapy.coloring
import momapy.core.elements
import momapy.core.layout
import momapy.drawing
import momapy.geometry
import momapy.meta.arcs
import momapy.meta.shapes
import momapy.sbgn.elements
import momapy.sbgn.layout
from momapy.sbgn.pd.model import (
    AndOperator,
    Association,
    Catalysis,
    Compartment,
    Complex,
    ComplexMultimer,
    ComplexMultimerSubunit,
    ComplexSubunit,
    Dissociation,
    EmptySet,
    EquivalenceOperator,
    GenericProcess,
    Inhibition,
    LogicalOperator,
    Macromolecule,
    MacromoleculeMultimer,
    MacromoleculeMultimerSubunit,
    MacromoleculeSubunit,
    Modulation,
    NecessaryStimulation,
    NotOperator,
    NucleicAcidFeature,
    NucleicAcidFeatureMultimer,
    NucleicAcidFeatureMultimerSubunit,
    NucleicAcidFeatureSubunit,
    OmittedProcess,
    OrOperator,
    PerturbingAgent,
    Phenotype,
    Process,
    SimpleChemical,
    SimpleChemicalMultimer,
    SimpleChemicalMultimerSubunit,
    SimpleChemicalSubunit,
    Stimulation,
    Submap,
    Subunit,
    Tag,
    Terminal,
    UncertainProcess,
    UnitOfInformation,
    UnspecifiedEntity,
    UnspecifiedEntitySubunit,
)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDLayout(momapy.sbgn.layout.SBGNLayout):
    """Class for SBGN-PD layouts"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateVariableLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
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
class UnitOfInformationLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
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
class TerminalLayout(momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode):
    """Class for terminal layouts"""

    width: float = 35.0
    height: float = 35.0
    direction: momapy.core.elements.Direction = momapy.core.elements.Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return TagLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CardinalityLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Class for cardinality layouts"""

    width: float = 12.0
    height: float = 19.0

    def _make_shape(self):
        return UnitOfInformationLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntitySubunitLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Class for unspecified entity subunit layouts"""

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return UnspecifiedEntityLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalSubunitLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Class for simple chemical subunit layouts"""

    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return SimpleChemicalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeSubunitLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Class for macromolecule subunit layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureSubunitLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Class for nucleic acid feature subunit layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return NucleicAcidFeatureLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexSubunitLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Class for complex subunit layouts"""

    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 5.0

    def _make_shape(self):
        return ComplexLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimerSubunitLayout(
    momapy.sbgn.elements._MultiMixin, momapy.sbgn.elements.SBGNNode
):
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
class MacromoleculeMultimerSubunitLayout(
    momapy.sbgn.elements._MultiMixin, momapy.sbgn.elements.SBGNNode
):
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
class NucleicAcidFeatureMultimerSubunitLayout(
    momapy.sbgn.elements._MultiMixin, momapy.sbgn.elements.SBGNNode
):
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
class ComplexMultimerSubunitLayout(
    momapy.sbgn.elements._MultiMixin, momapy.sbgn.elements.SBGNNode
):
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
class CompartmentLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Class for compartment layouts"""

    width: float = 80.0
    height: float = 80.0
    rounded_corners: float = 5.0
    stroke_width: float = 3.25

    def _make_shape(self):
        return MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SubmapLayout(
    momapy.sbgn.elements._SimpleMixin,
    momapy.sbgn.elements.SBGNNode,
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
class UnspecifiedEntityLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Class for unspecified entity layouts"""

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Class for simple chemical layouts"""

    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Stadium(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
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
class NucleicAcidFeatureLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
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
class ComplexLayout(momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode):
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
class SimpleChemicalMultimerLayout(
    momapy.sbgn.elements._MultiMixin, momapy.sbgn.elements.SBGNNode
):
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
class MacromoleculeMultimerLayout(
    momapy.sbgn.elements._MultiMixin, momapy.sbgn.elements.SBGNNode
):
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
class NucleicAcidFeatureMultimerLayout(
    momapy.sbgn.elements._MultiMixin, momapy.sbgn.elements.SBGNNode
):
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
class ComplexMultimerLayout(
    momapy.sbgn.elements._MultiMixin, momapy.sbgn.elements.SBGNNode
):
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
class _EmptySetShape(momapy.core.layout.Shape):
    position: momapy.geometry.Point
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
class EmptySetLayout(momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode):
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
class PerturbingAgentLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
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
    momapy.sbgn.elements._ConnectorsMixin,
    momapy.sbgn.elements._SimpleMixin,
    momapy.sbgn.elements._TextMixin,
    momapy.sbgn.elements.SBGNNode,
):
    """Class for and operator layouts"""

    _font_family: typing.ClassVar[str] = momapy.drawing.DEFAULT_FONT_FAMILY
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    _text: typing.ClassVar[str] = "AND"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrOperatorLayout(
    momapy.sbgn.elements._ConnectorsMixin,
    momapy.sbgn.elements._SimpleMixin,
    momapy.sbgn.elements._TextMixin,
    momapy.sbgn.elements.SBGNNode,
):
    """Class for or operator layouts"""

    _font_family: typing.ClassVar[str] = momapy.drawing.DEFAULT_FONT_FAMILY
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    _text: typing.ClassVar[str] = "OR"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotOperatorLayout(
    momapy.sbgn.elements._ConnectorsMixin,
    momapy.sbgn.elements._SimpleMixin,
    momapy.sbgn.elements._TextMixin,
    momapy.sbgn.elements.SBGNNode,
):
    """Class for not operator layouts"""

    _font_family: typing.ClassVar[str] = momapy.drawing.DEFAULT_FONT_FAMILY
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    _text: typing.ClassVar[str] = "NOT"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorLayout(
    momapy.sbgn.elements._ConnectorsMixin,
    momapy.sbgn.elements._SimpleMixin,
    momapy.sbgn.elements._TextMixin,
    momapy.sbgn.elements.SBGNNode,
):
    """Class for equivalence operator layouts"""

    _font_family: typing.ClassVar[str] = momapy.drawing.DEFAULT_FONT_FAMILY
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 2
    _text: typing.ClassVar[str] = "≡"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProcessLayout(
    momapy.sbgn.elements._ConnectorsMixin,
    momapy.sbgn.elements._SimpleMixin,
    momapy.sbgn.elements.SBGNNode,
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
    momapy.sbgn.elements._ConnectorsMixin,
    momapy.sbgn.elements._SimpleMixin,
    momapy.sbgn.elements._TextMixin,
    momapy.sbgn.elements.SBGNNode,
):
    """Class for omitted process layouts"""

    _text: typing.ClassVar[str] = "\\\\"
    _font_family: typing.ClassVar[str] = momapy.drawing.DEFAULT_FONT_FAMILY
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 1.5
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue

    width: float = 20.0
    height: float = 20.0

    def _make_shape(self):
        return GenericProcessLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UncertainProcessLayout(
    momapy.sbgn.elements._ConnectorsMixin,
    momapy.sbgn.elements._SimpleMixin,
    momapy.sbgn.elements._TextMixin,
    momapy.sbgn.elements.SBGNNode,
):
    """Class for uncertain process layouts"""

    _text: typing.ClassVar[str] = "?"
    _font_family: typing.ClassVar[str] = momapy.drawing.DEFAULT_FONT_FAMILY
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 1.5
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue

    width: float = 20.0
    height: float = 20.0

    def _make_shape(self):
        return GenericProcessLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class AssociationLayout(
    momapy.sbgn.elements._ConnectorsMixin,
    momapy.sbgn.elements._SimpleMixin,
    momapy.sbgn.elements.SBGNNode,
):
    """Class for association layouts"""

    width: float = 20.0
    height: float = 20.0

    fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _DissociationShape(momapy.core.layout.Shape):
    position: momapy.geometry.Point
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
    momapy.sbgn.elements._ConnectorsMixin,
    momapy.sbgn.elements._SimpleMixin,
    momapy.sbgn.elements.SBGNNode,
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
    momapy.sbgn.elements._SimpleMixin,
    momapy.sbgn.elements.SBGNNode,
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
class TagLayout(momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode):
    """Class for tag layouts"""

    width: float = 35.0
    height: float = 35.0
    direction: momapy.core.elements.Direction = momapy.core.elements.Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        if self.direction == momapy.core.elements.Direction.RIGHT:
            return momapy.meta.shapes.Hexagon(
                position=self.position,
                width=self.width,
                height=self.height,
                left_angle=90.0,
                right_angle=self.angle,
            )
        elif self.direction == momapy.core.elements.Direction.LEFT:
            return momapy.meta.shapes.Hexagon(
                position=self.position,
                width=self.width,
                height=self.height,
                left_angle=self.angle,
                right_angle=90.0,
            )
        elif self.direction == momapy.core.elements.Direction.UP:
            return momapy.meta.shapes.TurnedHexagon(
                position=self.position,
                width=self.width,
                height=self.height,
                top_angle=self.angle,
                bottom_angle=90.0,
            )
        elif self.direction == momapy.core.elements.Direction.DOWN:
            return momapy.meta.shapes.TurnedHexagon(
                position=self.position,
                width=self.width,
                height=self.height,
                top_angle=90.0,
                bottom_angle=self.angle,
            )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ConsumptionLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Class for consumption layouts"""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProductionLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Class for production layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModulationLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Class for modulation layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Diamond._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class StimulationLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Class for stimulation layouts"""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulationLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Class for necessary stimulation layouts"""

    arrowhead_bar_height: float = 12.0
    arrowhead_sep: float = 3.0
    arrowhead_triangle_height: float = 10.0
    arrowhead_triangle_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        actions = [
            momapy.drawing.MoveTo(
                momapy.geometry.Point(0, -self.arrowhead_bar_height / 2)
            ),
            momapy.drawing.LineTo(
                momapy.geometry.Point(0, self.arrowhead_bar_height / 2)
            ),
        ]
        bar = momapy.drawing.Path(actions=actions)
        actions = [
            momapy.drawing.MoveTo(momapy.geometry.Point(0, 0)),
            momapy.drawing.LineTo(momapy.geometry.Point(self.arrowhead_sep, 0)),
        ]
        sep = momapy.drawing.Path(actions=actions)
        triangle = momapy.meta.shapes.Triangle(
            position=momapy.geometry.Point(
                self.arrowhead_sep + self.arrowhead_triangle_width / 2, 0
            ),
            width=self.arrowhead_triangle_width,
            height=self.arrowhead_triangle_height,
            direction=momapy.core.elements.Direction.RIGHT,
        )
        return [bar, sep] + triangle.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class CatalysisLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Class for catalysis layouts"""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Ellipse._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class InhibitionLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Class for inhibition layouts"""

    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Bar._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Class for logic arc layouts"""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Class for equivalence arc layouts"""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)
