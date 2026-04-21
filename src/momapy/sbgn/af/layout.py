"""Layout classes for SBGN Activity Flow (AF) maps."""

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
import momapy.sbgn.pd.layout


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNAFLayout(momapy.sbgn.layout.SBGNLayout):
    """SBGN-AF layout.

    Represents the visual layout of an SBGN-AF model.
    """

    pass


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
class UnspecifiedEntityUnitOfInformationLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Layout for unspecified entity units of information."""

    width: float = 12.0
    height: float = 12.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.UnspecifiedEntityLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalUnitOfInformationLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Layout for simple chemical units of information."""

    width: float = 12.0
    height: float = 12.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.SimpleChemicalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeUnitOfInformationLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Layout for macromolecule units of information."""

    width: float = 12.0
    height: float = 12.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureUnitOfInformationLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Layout for nucleic acid feature units of information."""

    width: float = 12.0
    height: float = 12.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.NucleicAcidFeatureLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexUnitOfInformationLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Layout for complex units of information."""

    width: float = 12.0
    height: float = 12.0
    cut_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.ComplexLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbationUnitOfInformationLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Layout for perturbation units of information."""

    width: float = 12.0
    height: float = 12.0
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.PerturbingAgentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalLayout(momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode):
    """Layout for terminals."""

    width: float = 35.0
    height: float = 35.0
    direction: momapy.core.elements.Direction = momapy.core.elements.Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.TerminalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompartmentLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Layout for compartments."""

    width: float = 80.0
    height: float = 80.0
    rounded_corners: float = 5.0
    border_stroke_width: float | None = 3.25

    def _make_shape(self):
        return momapy.sbgn.pd.layout.CompartmentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SubmapLayout(momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode):
    """Layout for submaps."""

    width: float = 80.0
    height: float = 80.0
    border_stroke_width: float | None = 2.25

    def _make_shape(self):
        return momapy.sbgn.pd.layout.SubmapLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class BiologicalActivityLayout(
    momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode
):
    """Layout for biological activities."""

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(momapy.sbgn.elements._SimpleMixin, momapy.sbgn.elements.SBGNNode):
    """Layout for phenotypes."""

    width: float = 60.0
    height: float = 30.0
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.PhenotypeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndOperatorLayout(
    momapy.sbgn.elements._ConnectorsMixin,
    momapy.sbgn.elements._SimpleMixin,
    momapy.sbgn.elements._TextMixin,
    momapy.sbgn.elements.SBGNNode,
):
    """Layout for AND operators."""

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
    """Layout for OR operators."""

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
    """Layout for NOT operators."""

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
class DelayOperatorLayout(
    momapy.sbgn.elements._ConnectorsMixin,
    momapy.sbgn.elements._SimpleMixin,
    momapy.sbgn.elements._TextMixin,
    momapy.sbgn.elements.SBGNNode,
):
    """Layout for DELAY operators."""

    _font_family: typing.ClassVar[str] = momapy.drawing.DEFAULT_FONT_FAMILY
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 2
    _text: typing.ClassVar[str] = "τ"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagLayout(momapy.sbgn.pd.layout.TagLayout):
    """Layout for tags."""

    width: float = 35.0
    height: float = 35.0
    direction: momapy.core.elements.Direction = momapy.core.elements.Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.TagLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInfluenceLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Layout for unknown influences."""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Diamond._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluenceLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Layout for positive influences."""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulationLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Layout for necessary stimulations."""

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
class NegativeInfluenceLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Layout for negative influences."""

    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Bar._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Layout for logic arcs."""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(momapy.sbgn.elements.SBGNSingleHeadedArc):
    """Layout for equivalence arcs."""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)
