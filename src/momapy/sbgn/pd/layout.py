"""Layout classes for SBGN Process Description (PD) maps.

Each layout class is named after the model class it draws, with a ``Layout``
suffix appended (e.g. model ``Macromolecule`` gives layout
``MacromoleculeLayout``).
"""

import dataclasses
import typing

from momapy.coloring import Color
from momapy.coloring import black
from momapy.coloring import white
from momapy.core.elements import Direction
from momapy.core.layout import Shape
from momapy.drawing import Ellipse as EllipseDrawing
from momapy.drawing import LineTo
from momapy.drawing import MoveTo
from momapy.drawing import NoneValueType
from momapy.drawing import Path
from momapy.geometry import Point
from momapy.meta.arcs import Bar as BarArc
from momapy.meta.arcs import Diamond as DiamondArc
from momapy.meta.arcs import Ellipse as EllipseArc
from momapy.meta.arcs import PolyLine as PolyLineArc
from momapy.meta.arcs import Triangle as TriangleArc
from momapy.meta.shapes import Ellipse as EllipseShape
from momapy.meta.shapes import Hexagon as HexagonShape
from momapy.meta.shapes import Rectangle as RectangleShape
from momapy.meta.shapes import Stadium as StadiumShape
from momapy.meta.shapes import Triangle as TriangleShape
from momapy.meta.shapes import TurnedHexagon as TurnedHexagonShape
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
    """SBGN-PD layout.

    Represents the visual layout of an SBGN-PD model.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateVariableLayout(_SimpleMixin, SBGNNode):
    """Layout for state variables.

    Draws a state variable as a stadium-shaped glyph.

    Attributes:
        width: The width of the state variable layout.
        height: The height of the state variable layout.
    """

    width: float = dataclasses.field(
        default=12.0, metadata={"description": "The width of the state variable layout"}
    )
    height: float = dataclasses.field(
        default=12.0,
        metadata={"description": "The height of the state variable layout"},
    )

    def _make_shape(self):
        return StadiumShape(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for units of information.

    Draws a unit of information as a rectangular glyph.

    Attributes:
        width: The width of the unit of information layout.
        height: The height of the unit of information layout.
    """

    width: float = 18.0
    height: float = 12.0

    def _make_shape(self):
        return RectangleShape(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalLayout(_SimpleMixin, SBGNNode):
    """Layout for terminals.

    Draws a terminal as a tag-shaped glyph pointing in a given direction.

    Attributes:
        width: The width of the terminal layout.
        height: The height of the terminal layout.
        direction: The direction the terminal glyph points to.
        angle: The angle of the pointed end of the terminal glyph.
    """

    width: float = 35.0
    height: float = 35.0
    direction: Direction = Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return TagLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CardinalityLayout(_SimpleMixin, SBGNNode):
    """Layout for cardinalities.

    Draws the cardinality of a multimer as a unit-of-information glyph.

    Attributes:
        width: The width of the cardinality layout.
        height: The height of the cardinality layout.
    """

    width: float = 12.0
    height: float = 19.0

    def _make_shape(self):
        return UnitOfInformationLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntitySubunitLayout(_SimpleMixin, SBGNNode):
    """Layout for unspecified entity subunits.

    Draws an unspecified entity subunit as an ellipse glyph.

    Attributes:
        width: The width of the unspecified entity subunit layout.
        height: The height of the unspecified entity subunit layout.
    """

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return UnspecifiedEntityLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalSubunitLayout(_SimpleMixin, SBGNNode):
    """Layout for simple chemical subunits.

    Draws a simple chemical subunit as a stadium glyph.

    Attributes:
        width: The width of the simple chemical subunit layout.
        height: The height of the simple chemical subunit layout.
    """

    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return SimpleChemicalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeSubunitLayout(_SimpleMixin, SBGNNode):
    """Layout for macromolecule subunits.

    Draws a macromolecule subunit as a rounded rectangle glyph.

    Attributes:
        width: The width of the macromolecule subunit layout.
        height: The height of the macromolecule subunit layout.
        rounded_corners: The corner radius of the macromolecule subunit layout.
    """

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureSubunitLayout(_SimpleMixin, SBGNNode):
    """Layout for nucleic acid feature subunits.

    Draws a nucleic acid feature subunit as a bottom-rounded rectangle glyph.

    Attributes:
        width: The width of the nucleic acid feature subunit layout.
        height: The height of the nucleic acid feature subunit layout.
        rounded_corners: The corner radius of the nucleic acid feature subunit
            layout.
    """

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return NucleicAcidFeatureLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexSubunitLayout(_SimpleMixin, SBGNNode):
    """Layout for complex subunits.

    Draws a complex subunit as a cut-corner rectangle glyph.

    Attributes:
        width: The width of the complex subunit layout.
        height: The height of the complex subunit layout.
        cut_corners: The size of the cut corners of the complex subunit layout.
    """

    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 5.0

    def _make_shape(self):
        return ComplexLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimerSubunitLayout(_MultiMixin, SBGNNode):
    """Layout for simple chemical multimer subunits.

    Draws a simple chemical multimer subunit as stacked stadium glyphs.

    Attributes:
        width: The width of the simple chemical multimer subunit layout.
        height: The height of the simple chemical multimer subunit layout.
    """

    _n: typing.ClassVar[int] = 2
    width: float = 60.0
    height: float = 30.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return StadiumShape(
            position=position,
            width=width,
            height=height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimerSubunitLayout(_MultiMixin, SBGNNode):
    """Layout for macromolecule multimer subunits.

    Draws a macromolecule multimer subunit as stacked rounded rectangle glyphs.

    Attributes:
        width: The width of the macromolecule multimer subunit layout.
        height: The height of the macromolecule multimer subunit layout.
        rounded_corners: The corner radius of the macromolecule multimer subunit
            layout.
    """

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
        return RectangleShape(
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
    """Layout for nucleic acid feature multimer subunits.

    Draws a nucleic acid feature multimer subunit as stacked bottom-rounded
    rectangle glyphs.

    Attributes:
        width: The width of the nucleic acid feature multimer subunit layout.
        height: The height of the nucleic acid feature multimer subunit layout.
        rounded_corners: The corner radius of the nucleic acid feature multimer
            subunit layout.
    """

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
        return RectangleShape(
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
    """Layout for complex multimer subunits.

    Draws a complex multimer subunit as stacked cut-corner rectangle glyphs.

    Attributes:
        width: The width of the complex multimer subunit layout.
        height: The height of the complex multimer subunit layout.
        cut_corners: The size of the cut corners of the complex multimer subunit
            layout.
    """

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
        return RectangleShape(
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
    """Layout for compartments.

    Draws a compartment as a rounded rectangle glyph with a thick border.

    Attributes:
        width: The width of the compartment layout.
        height: The height of the compartment layout.
        rounded_corners: The corner radius of the compartment layout.
        stroke_width: The border stroke width of the compartment layout.
    """

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
    """Layout for submaps.

    Draws a submap as a rectangular glyph.

    Attributes:
        width: The width of the submap layout.
        height: The height of the submap layout.
        stroke_width: The border stroke width of the submap layout.
    """

    width: float = 80.0
    height: float = 80.0
    stroke_width: float = 2.25

    def _make_shape(self):
        return RectangleShape(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityLayout(_SimpleMixin, SBGNNode):
    """Layout for unspecified entities.

    Draws an unspecified entity as an ellipse glyph.

    Attributes:
        width: The width of the unspecified entity layout.
        height: The height of the unspecified entity layout.
    """

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return EllipseShape(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalLayout(_SimpleMixin, SBGNNode):
    """Layout for simple chemicals.

    Draws a simple chemical as a stadium glyph.

    Attributes:
        width: The width of the simple chemical layout.
        height: The height of the simple chemical layout.
    """

    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return StadiumShape(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeLayout(_SimpleMixin, SBGNNode):
    """Layout for macromolecules.

    Draws a macromolecule as a rounded rectangle glyph.

    Attributes:
        width: The width of the macromolecule layout.
        height: The height of the macromolecule layout.
        rounded_corners: The corner radius of the macromolecule layout.
    """

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return RectangleShape(
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
    """Layout for nucleic acid features.

    Draws a nucleic acid feature as a bottom-rounded rectangle glyph.

    Attributes:
        width: The width of the nucleic acid feature layout.
        height: The height of the nucleic acid feature layout.
        rounded_corners: The corner radius of the nucleic acid feature layout.
    """

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return RectangleShape(
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
    """Layout for complexes.

    Draws a complex as a cut-corner rectangle glyph.

    Attributes:
        width: The width of the complex layout.
        height: The height of the complex layout.
        cut_corners: The size of the cut corners of the complex layout.
    """

    width: float = 44.0
    height: float = 44.0
    cut_corners: float = 5.0

    def _make_shape(self):
        return RectangleShape(
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
    """Layout for simple chemical multimers.

    Draws a simple chemical multimer as stacked stadium glyphs.

    Attributes:
        width: The width of the simple chemical multimer layout.
        height: The height of the simple chemical multimer layout.
    """

    _n: typing.ClassVar[int] = 2
    width: float = 30.0
    height: float = 30.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return StadiumShape(
            position=position,
            width=width,
            height=height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimerLayout(_MultiMixin, SBGNNode):
    """Layout for macromolecule multimers.

    Draws a macromolecule multimer as stacked rounded rectangle glyphs.

    Attributes:
        width: The width of the macromolecule multimer layout.
        height: The height of the macromolecule multimer layout.
        rounded_corners: The corner radius of the macromolecule multimer layout.
    """

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
        return RectangleShape(
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
    """Layout for nucleic acid feature multimers.

    Draws a nucleic acid feature multimer as stacked bottom-rounded rectangle
    glyphs.

    Attributes:
        width: The width of the nucleic acid feature multimer layout.
        height: The height of the nucleic acid feature multimer layout.
        rounded_corners: The corner radius of the nucleic acid feature multimer
            layout.
    """

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
        return RectangleShape(
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
    """Layout for complex multimers.

    Draws a complex multimer as stacked cut-corner rectangle glyphs.

    Attributes:
        width: The width of the complex multimer layout.
        height: The height of the complex multimer layout.
        cut_corners: The size of the cut corners of the complex multimer layout.
    """

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
        return RectangleShape(
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
        circle = EllipseDrawing(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        actions = [
            MoveTo(self.position - (self.width / 2, -self.height / 2)),
            LineTo(self.position + (self.width / 2, -self.height / 2)),
        ]
        bar = Path(actions=actions)
        return [circle, bar]


@dataclasses.dataclass(frozen=True, kw_only=True)
class EmptySetLayout(_SimpleMixin, SBGNNode):
    """Layout for empty sets.

    Draws an empty set (source-and-sink) as a circle crossed by a bar.

    Attributes:
        width: The width of the empty set layout.
        height: The height of the empty set layout.
    """

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
    """Layout for perturbing agents.

    Draws a perturbing agent as a concave hexagon glyph.

    Attributes:
        width: The width of the perturbing agent layout.
        height: The height of the perturbing agent layout.
        angle: The angle of the hexagon notches of the perturbing agent layout.
    """

    width: float = 60.0
    height: float = 30.0
    angle: float = 70.0

    def _make_shape(self):
        return HexagonShape(
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
    """Layout for AND operators.

    Draws an AND operator as an ellipse glyph labelled with its text.

    Attributes:
        text: The text drawn inside the operator glyph.
        width: The width of the AND operator layout.
        height: The height of the AND operator layout.
    """

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    text: str = "AND"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return EllipseShape(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrOperatorLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
    SBGNNode,
):
    """Layout for OR operators.

    Draws an OR operator as an ellipse glyph labelled with its text.

    Attributes:
        text: The text drawn inside the operator glyph.
        width: The width of the OR operator layout.
        height: The height of the OR operator layout.
    """

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    text: str = "OR"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return EllipseShape(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotOperatorLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
    SBGNNode,
):
    """Layout for NOT operators.

    Draws a NOT operator as an ellipse glyph labelled with its text.

    Attributes:
        text: The text drawn inside the operator glyph.
        width: The width of the NOT operator layout.
        height: The height of the NOT operator layout.
    """

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    text: str = "NOT"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return EllipseShape(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
    SBGNNode,
):
    """Layout for equivalence operators.

    Draws an equivalence operator as an ellipse glyph labelled with its text.

    Attributes:
        text: The text drawn inside the operator glyph.
        width: The width of the equivalence operator layout.
        height: The height of the equivalence operator layout.
    """

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 2
    text: str = "≡"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return EllipseShape(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProcessLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    SBGNNode,
):
    """Layout for generic processes.

    Draws a generic process as a square glyph with connectors.

    Attributes:
        width: The width of the generic process layout.
        height: The height of the generic process layout.
    """

    width: float = 20.0
    height: float = 20.0

    def _make_shape(self):
        return RectangleShape(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OmittedProcessLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
    SBGNNode,
):
    """Layout for omitted processes.

    Draws an omitted process as a square glyph labelled with its text.

    Attributes:
        text: The text drawn inside the process glyph.
        width: The width of the omitted process layout.
        height: The height of the omitted process layout.
    """

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
    """Layout for uncertain processes.

    Draws an uncertain process as a square glyph labelled with its text.

    Attributes:
        text: The text drawn inside the process glyph.
        width: The width of the uncertain process layout.
        height: The height of the uncertain process layout.
    """

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
    """Layout for associations.

    Draws an association as a filled circle glyph with connectors.

    Attributes:
        width: The width of the association layout.
        height: The height of the association layout.
        fill: The fill color of the association glyph.
    """

    width: float = 20.0
    height: float = 20.0

    fill: NoneValueType | Color | None = black

    def _make_shape(self):
        return EllipseShape(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _DissociationShape(Shape):
    position: Point
    width: float
    height: float
    sep: float

    def drawing_elements(self):
        outer_circle = EllipseDrawing(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        inner_circle = EllipseDrawing(
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
    """Layout for dissociations.

    Draws a dissociation as two concentric circles with connectors.

    Attributes:
        width: The width of the dissociation layout.
        height: The height of the dissociation layout.
        sep: The separation between the outer and inner circles.
    """

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
    """Layout for phenotypes.

    Draws a phenotype as a convex hexagon glyph.

    Attributes:
        width: The width of the phenotype layout.
        height: The height of the phenotype layout.
        angle: The angle of the hexagon points of the phenotype layout.
    """

    width: float = 60.0
    height: float = 30.0
    angle: float = 70.0

    def _make_shape(self):
        return HexagonShape(
            position=self.position,
            width=self.width,
            height=self.height,
            left_angle=self.angle,
            right_angle=self.angle,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagLayout(_SimpleMixin, SBGNNode):
    """Layout for tags.

    Draws a tag as a hexagon glyph pointing in a given direction.

    Attributes:
        width: The width of the tag layout.
        height: The height of the tag layout.
        direction: The direction the tag glyph points to.
        angle: The angle of the pointed end of the tag glyph.
    """

    width: float = 35.0
    height: float = 35.0
    direction: Direction = Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        if self.direction == Direction.RIGHT:
            return HexagonShape(
                position=self.position,
                width=self.width,
                height=self.height,
                left_angle=90.0,
                right_angle=self.angle,
            )
        elif self.direction == Direction.LEFT:
            return HexagonShape(
                position=self.position,
                width=self.width,
                height=self.height,
                left_angle=self.angle,
                right_angle=90.0,
            )
        elif self.direction == Direction.UP:
            return TurnedHexagonShape(
                position=self.position,
                width=self.width,
                height=self.height,
                top_angle=self.angle,
                bottom_angle=90.0,
            )
        elif self.direction == Direction.DOWN:
            return TurnedHexagonShape(
                position=self.position,
                width=self.width,
                height=self.height,
                top_angle=90.0,
                bottom_angle=self.angle,
            )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ConsumptionLayout(SBGNSingleHeadedArc):
    """Layout for consumptions.

    Draws a consumption as a plain line connecting a reactant to a process.
    """

    def _arrowhead_border_drawing_elements(self):
        return PolyLineArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProductionLayout(SBGNSingleHeadedArc):
    """Layout for productions.

    Draws a production as a line ending in a filled triangular arrowhead.

    Attributes:
        arrowhead_fill: The fill color of the arrowhead.
        arrowhead_height: The height of the arrowhead.
        arrowhead_width: The width of the arrowhead.
    """

    arrowhead_fill: NoneValueType | Color | None = black
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return TriangleArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModulationLayout(SBGNSingleHeadedArc):
    """Layout for modulations.

    Draws a modulation as a line ending in a diamond-shaped arrowhead.

    Attributes:
        arrowhead_fill: The fill color of the arrowhead.
        arrowhead_height: The height of the arrowhead.
        arrowhead_width: The width of the arrowhead.
    """

    arrowhead_fill: NoneValueType | Color | None = white
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return DiamondArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class StimulationLayout(SBGNSingleHeadedArc):
    """Layout for stimulations.

    Draws a stimulation as a line ending in an unfilled triangular arrowhead.

    Attributes:
        arrowhead_height: The height of the arrowhead.
        arrowhead_width: The width of the arrowhead.
    """

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return TriangleArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulationLayout(SBGNSingleHeadedArc):
    """Layout for necessary stimulations.

    Draws a necessary stimulation as a line ending in a bar followed by an
    unfilled triangular arrowhead.

    Attributes:
        arrowhead_bar_height: The height of the bar of the arrowhead.
        arrowhead_sep: The separation between the bar and the triangle.
        arrowhead_triangle_height: The height of the triangle of the arrowhead.
        arrowhead_triangle_width: The width of the triangle of the arrowhead.
    """

    arrowhead_bar_height: float = 12.0
    arrowhead_sep: float = 3.0
    arrowhead_triangle_height: float = 10.0
    arrowhead_triangle_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        actions = [
            MoveTo(Point(0, -self.arrowhead_bar_height / 2)),
            LineTo(Point(0, self.arrowhead_bar_height / 2)),
        ]
        bar = Path(actions=actions)
        actions = [
            MoveTo(Point(0, 0)),
            LineTo(Point(self.arrowhead_sep, 0)),
        ]
        sep = Path(actions=actions)
        triangle = TriangleShape(
            position=Point(self.arrowhead_sep + self.arrowhead_triangle_width / 2, 0),
            width=self.arrowhead_triangle_width,
            height=self.arrowhead_triangle_height,
            direction=Direction.RIGHT,
        )
        return [bar, sep] + triangle.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class CatalysisLayout(SBGNSingleHeadedArc):
    """Layout for catalyses.

    Draws a catalysis as a line ending in an unfilled circular arrowhead.

    Attributes:
        arrowhead_height: The height of the arrowhead.
        arrowhead_width: The width of the arrowhead.
    """

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return EllipseArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class InhibitionLayout(SBGNSingleHeadedArc):
    """Layout for inhibitions.

    Draws an inhibition as a line ending in a perpendicular bar.

    Attributes:
        arrowhead_height: The height of the bar arrowhead.
    """

    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return BarArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(SBGNSingleHeadedArc):
    """Layout for logic arcs.

    Draws a logic arc as a plain line connecting an input to a logical operator.
    """

    def _arrowhead_border_drawing_elements(self):
        return PolyLineArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(SBGNSingleHeadedArc):
    """Layout for equivalence arcs.

    Draws an equivalence arc as a plain line connecting an input to an
    equivalence operator.
    """

    def _arrowhead_border_drawing_elements(self):
        return PolyLineArc._arrowhead_border_drawing_elements(self)
