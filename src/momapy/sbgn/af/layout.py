"""Layout classes for SBGN Activity Flow (AF) maps.

Each layout class is named after the model class it draws, with a ``Layout``
suffix appended (e.g. model ``BiologicalActivity`` gives layout
``BiologicalActivityLayout``).
"""

import dataclasses
import typing

from momapy.core.elements import Direction
from momapy.drawing import (
    LineTo,
    MoveTo,
    Path,
)
from momapy.geometry import Point
from momapy.meta.arcs import Bar as BarArc
from momapy.meta.arcs import Diamond as DiamondArc
from momapy.meta.arcs import PolyLine as PolyLineArc
from momapy.meta.arcs import Triangle as TriangleArc
from momapy.meta.shapes import Ellipse as EllipseShape
from momapy.meta.shapes import Rectangle as RectangleShape
from momapy.meta.shapes import Triangle as TriangleShape
from momapy.sbgn.pd.layout import CompartmentLayout as PDCompartmentLayout
from momapy.sbgn.pd.layout import ComplexLayout as PDComplexLayout
from momapy.sbgn.pd.layout import MacromoleculeLayout as PDMacromoleculeLayout
from momapy.sbgn.pd.layout import (
    NucleicAcidFeatureLayout as PDNucleicAcidFeatureLayout,
)
from momapy.sbgn.pd.layout import PerturbingAgentLayout as PDPerturbingAgentLayout
from momapy.sbgn.pd.layout import PhenotypeLayout as PDPhenotypeLayout
from momapy.sbgn.pd.layout import SimpleChemicalLayout as PDSimpleChemicalLayout
from momapy.sbgn.pd.layout import SubmapLayout as PDSubmapLayout
from momapy.sbgn.pd.layout import TagLayout as PDTagLayout
from momapy.sbgn.pd.layout import TerminalLayout as PDTerminalLayout
from momapy.sbgn.pd.layout import (
    UnspecifiedEntityLayout as PDUnspecifiedEntityLayout,
)
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

    width: float = 18.0
    height: float = 12.0

    def _make_shape(self):
        return RectangleShape(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for unspecified entity units of information."""

    width: float = 18.0
    height: float = 12.0

    def _make_shape(self):
        return PDUnspecifiedEntityLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for simple chemical units of information."""

    width: float = 12.0
    height: float = 12.0

    def _make_shape(self):
        return PDSimpleChemicalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for macromolecule units of information."""

    width: float = 18.0
    height: float = 12.0
    rounded_corners: float = 3.0

    def _make_shape(self):
        return PDMacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for nucleic acid feature units of information."""

    width: float = 18.0
    height: float = 12.0
    rounded_corners: float = 3.0

    def _make_shape(self):
        return PDNucleicAcidFeatureLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for complex units of information."""

    width: float = 18.0
    height: float = 12.0
    cut_corners: float = 3.0

    def _make_shape(self):
        return PDComplexLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbationUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for perturbation units of information."""

    width: float = 18.0
    height: float = 12.0
    angle: float = 70.0

    def _make_shape(self):
        return PDPerturbingAgentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalLayout(_SimpleMixin, SBGNNode):
    """Layout for terminals."""

    width: float = 35.0
    height: float = 35.0
    direction: Direction = Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return PDTerminalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompartmentLayout(_SimpleMixin, SBGNNode):
    """Layout for compartments."""

    width: float = 80.0
    height: float = 80.0
    rounded_corners: float = 5.0
    border_stroke_width: float | None = 3.25

    def _make_shape(self):
        return PDCompartmentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SubmapLayout(_SimpleMixin, SBGNNode):
    """Layout for submaps."""

    width: float = 80.0
    height: float = 80.0
    border_stroke_width: float | None = 2.25

    def _make_shape(self):
        return PDSubmapLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class BiologicalActivityLayout(_SimpleMixin, SBGNNode):
    """Layout for biological activities."""

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return RectangleShape(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(_SimpleMixin, SBGNNode):
    """Layout for phenotypes."""

    width: float = 60.0
    height: float = 30.0
    angle: float = 70.0

    def _make_shape(self):
        return PDPhenotypeLayout._make_shape(self)


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
    """Layout for OR operators."""

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
    """Layout for NOT operators."""

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    text: str = "NOT"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return EllipseShape(
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
        return EllipseShape(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagLayout(PDTagLayout):
    """Layout for tags."""

    width: float = 35.0
    height: float = 35.0
    direction: Direction = Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return PDTagLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInfluenceLayout(SBGNSingleHeadedArc):
    """Layout for unknown influences."""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return DiamondArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluenceLayout(SBGNSingleHeadedArc):
    """Layout for positive influences."""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return TriangleArc._arrowhead_border_drawing_elements(self)


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
        triangle = TriangleShape(
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
        return BarArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(SBGNSingleHeadedArc):
    """Layout for logic arcs."""

    def _arrowhead_border_drawing_elements(self):
        return PolyLineArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(SBGNSingleHeadedArc):
    """Layout for equivalence arcs."""

    def _arrowhead_border_drawing_elements(self):
        return PolyLineArc._arrowhead_border_drawing_elements(self)
