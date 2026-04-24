"""Layout classes for SBGN Activity Flow (AF) maps."""

import dataclasses
import typing

import momapy.meta.arcs
import momapy.meta.shapes
import momapy.sbgn.pd.layout

from momapy.coloring import Color
from momapy.core.elements import Direction
from momapy.drawing import (
    DEFAULT_FONT_FAMILY,
    LineTo,
    MoveTo,
    NoneValue,
    NoneValueType,
    Path,
)
from momapy.geometry import Point
from momapy.sbgn.elements import (
    SBGNNode,
    SBGNSingleHeadedArc,
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
)
from momapy.sbgn.layout import SBGNLayout


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNAFLayout(SBGNLayout):
    """SBGN-AF layout.

    Represents the visual layout of an SBGN-AF model.
    """

    pass


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
class UnspecifiedEntityUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for unspecified entity units of information."""

    width: float = 12.0
    height: float = 12.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.UnspecifiedEntityLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for simple chemical units of information."""

    width: float = 12.0
    height: float = 12.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.SimpleChemicalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for macromolecule units of information."""

    width: float = 12.0
    height: float = 12.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for nucleic acid feature units of information."""

    width: float = 12.0
    height: float = 12.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.NucleicAcidFeatureLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for complex units of information."""

    width: float = 12.0
    height: float = 12.0
    cut_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.ComplexLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbationUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for perturbation units of information."""

    width: float = 12.0
    height: float = 12.0
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.PerturbingAgentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalLayout(_SimpleMixin, SBGNNode):
    """Layout for terminals."""

    width: float = 35.0
    height: float = 35.0
    direction: Direction = Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.TerminalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompartmentLayout(_SimpleMixin, SBGNNode):
    """Layout for compartments."""

    width: float = 80.0
    height: float = 80.0
    rounded_corners: float = 5.0
    border_stroke_width: float | None = 3.25

    def _make_shape(self):
        return momapy.sbgn.pd.layout.CompartmentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SubmapLayout(_SimpleMixin, SBGNNode):
    """Layout for submaps."""

    width: float = 80.0
    height: float = 80.0
    border_stroke_width: float | None = 2.25

    def _make_shape(self):
        return momapy.sbgn.pd.layout.SubmapLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class BiologicalActivityLayout(_SimpleMixin, SBGNNode):
    """Layout for biological activities."""

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(_SimpleMixin, SBGNNode):
    """Layout for phenotypes."""

    width: float = 60.0
    height: float = 30.0
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.PhenotypeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndOperatorLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
    SBGNNode,
):
    """Layout for AND operators."""

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
    """Layout for OR operators."""

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
    """Layout for NOT operators."""

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    text: str = "NOT"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class DelayOperatorLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
    SBGNNode,
):
    """Layout for DELAY operators."""

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 2
    text: str = "τ"
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
    direction: Direction = Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.layout.TagLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInfluenceLayout(SBGNSingleHeadedArc):
    """Layout for unknown influences."""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Diamond._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluenceLayout(SBGNSingleHeadedArc):
    """Layout for positive influences."""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulationLayout(SBGNSingleHeadedArc):
    """Layout for necessary stimulations."""

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
        triangle = momapy.meta.shapes.Triangle(
            position=Point(self.arrowhead_sep + self.arrowhead_triangle_width / 2, 0),
            width=self.arrowhead_triangle_width,
            height=self.arrowhead_triangle_height,
            direction=Direction.RIGHT,
        )
        return [bar, sep] + triangle.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class NegativeInfluenceLayout(SBGNSingleHeadedArc):
    """Layout for negative influences."""

    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Bar._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(SBGNSingleHeadedArc):
    """Layout for logic arcs."""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(SBGNSingleHeadedArc):
    """Layout for equivalence arcs."""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)
