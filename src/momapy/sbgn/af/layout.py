"""Layout classes for SBGN Activity Flow (AF) maps.

Each layout class is named after the model class it draws, with a ``Layout``
suffix appended (e.g. model ``BiologicalActivity`` gives layout
``BiologicalActivityLayout``).
"""

import dataclasses
import typing

from momapy.core.elements import Direction
from momapy.core.layout import Shape
from momapy.drawing import (
    DrawingElement,
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
    """Layout for units of information.

    Draws a unit of information as a rectangular glyph.
    """

    width: float = 18.0
    height: float = 12.0

    def _make_shape(self) -> Shape:
        return RectangleShape(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for unspecified entity units of information.

    Draws a unit of information typing an activity as an unspecified entity.
    """

    width: float = 18.0
    height: float = 12.0

    def _make_shape(self) -> Shape:
        return PDUnspecifiedEntityLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for simple chemical units of information.

    Draws a unit of information typing an activity as a simple chemical.
    """

    width: float = 12.0
    height: float = 12.0

    def _make_shape(self) -> Shape:
        return PDSimpleChemicalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for macromolecule units of information.

    Draws a unit of information typing an activity as a macromolecule.
    """

    width: float = 18.0
    height: float = 12.0
    rounded_corners: float = dataclasses.field(
        default=3.0, metadata={"description": "The radius of the rounded corners."}
    )

    def _make_shape(self) -> Shape:
        return PDMacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for nucleic acid feature units of information.

    Draws a unit of information typing an activity as a nucleic acid feature.
    """

    width: float = 18.0
    height: float = 12.0
    rounded_corners: float = dataclasses.field(
        default=3.0, metadata={"description": "The radius of the rounded corners."}
    )

    def _make_shape(self) -> Shape:
        return PDNucleicAcidFeatureLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for complex units of information.

    Draws a unit of information typing an activity as a complex.
    """

    width: float = 18.0
    height: float = 12.0
    cut_corners: float = dataclasses.field(
        default=3.0, metadata={"description": "The size of the cut corners."}
    )

    def _make_shape(self) -> Shape:
        return PDComplexLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbationUnitOfInformationLayout(_SimpleMixin, SBGNNode):
    """Layout for perturbation units of information.

    Draws a unit of information typing an activity as a perturbation.
    """

    width: float = 18.0
    height: float = 12.0
    angle: float = dataclasses.field(
        default=70.0, metadata={"description": "The angle of the notched sides."}
    )

    def _make_shape(self) -> Shape:
        return PDPerturbingAgentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalLayout(_SimpleMixin, SBGNNode):
    """Layout for terminals.

    Draws a terminal connection point of a submap.
    """

    width: float = 35.0
    height: float = 35.0
    direction: Direction = dataclasses.field(
        default=Direction.RIGHT,
        metadata={"description": "The direction the terminal points to."},
    )
    angle: float = dataclasses.field(
        default=70.0, metadata={"description": "The angle of the notched side."}
    )

    def _make_shape(self) -> Shape:
        return PDTerminalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompartmentLayout(_SimpleMixin, SBGNNode):
    """Layout for compartments.

    Draws a compartment as a rounded rectangular region.
    """

    width: float = 80.0
    height: float = 80.0
    rounded_corners: float = dataclasses.field(
        default=5.0, metadata={"description": "The radius of the rounded corners."}
    )
    border_stroke_width: float | None = dataclasses.field(
        default=3.25, metadata={"description": "The width of the border stroke."}
    )

    def _make_shape(self) -> Shape:
        return PDCompartmentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SubmapLayout(_SimpleMixin, SBGNNode):
    """Layout for submaps.

    Draws a submap as a rectangular region embedding a sub-diagram.
    """

    width: float = 80.0
    height: float = 80.0
    border_stroke_width: float | None = dataclasses.field(
        default=2.25, metadata={"description": "The width of the border stroke."}
    )

    def _make_shape(self) -> Shape:
        return PDSubmapLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class BiologicalActivityLayout(_SimpleMixin, SBGNNode):
    """Layout for biological activities.

    Draws a biological activity as a rectangular glyph.
    """

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self) -> Shape:
        return RectangleShape(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(_SimpleMixin, SBGNNode):
    """Layout for phenotypes.

    Draws a phenotype as a hexagonal glyph.
    """

    width: float = 60.0
    height: float = 30.0
    angle: float = dataclasses.field(
        default=70.0, metadata={"description": "The angle of the slanted sides."}
    )

    def _make_shape(self) -> Shape:
        return PDPhenotypeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndOperatorLayout(
    _ConnectorsMixin,
    _SimpleMixin,
    _TextMixin,
    SBGNNode,
):
    """Layout for AND operators.

    Draws a logical AND operator as a labelled circular glyph.
    """

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    text: str = dataclasses.field(
        default="AND", metadata={"description": "The text displayed inside the node."}
    )
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self) -> Shape:
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

    Draws a logical OR operator as a labelled circular glyph.
    """

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    text: str = dataclasses.field(
        default="OR", metadata={"description": "The text displayed inside the node."}
    )
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self) -> Shape:
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

    Draws a logical NOT operator as a labelled circular glyph.
    """

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    text: str = dataclasses.field(
        default="NOT", metadata={"description": "The text displayed inside the node."}
    )
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self) -> Shape:
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
    """Layout for DELAY operators.

    Draws a logical DELAY operator as a labelled circular glyph.
    """

    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 2
    text: str = dataclasses.field(
        default="τ", metadata={"description": "The text displayed inside the node."}
    )
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self) -> Shape:
        return EllipseShape(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagLayout(PDTagLayout):
    """Layout for tags.

    Draws a tag as a labelled pointed glyph.
    """

    width: float = 35.0
    height: float = 35.0
    direction: Direction = dataclasses.field(
        default=Direction.RIGHT,
        metadata={"description": "The direction the tag points to."},
    )
    angle: float = dataclasses.field(
        default=70.0, metadata={"description": "The angle of the pointed side."}
    )

    def _make_shape(self) -> Shape:
        return PDTagLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInfluenceLayout(SBGNSingleHeadedArc):
    """Layout for unknown influences.

    Draws an influence of unspecified sign with a diamond arrowhead.
    """

    arrowhead_height: float = dataclasses.field(
        default=10.0, metadata={"description": "The height of the arrowhead."}
    )
    arrowhead_width: float = dataclasses.field(
        default=10.0, metadata={"description": "The width of the arrowhead."}
    )

    def _arrowhead_border_drawing_elements(self) -> list[DrawingElement]:
        return DiamondArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluenceLayout(SBGNSingleHeadedArc):
    """Layout for positive influences.

    Draws a stimulating influence with a triangular arrowhead.
    """

    arrowhead_height: float = dataclasses.field(
        default=10.0, metadata={"description": "The height of the arrowhead."}
    )
    arrowhead_width: float = dataclasses.field(
        default=10.0, metadata={"description": "The width of the arrowhead."}
    )

    def _arrowhead_border_drawing_elements(self) -> list[DrawingElement]:
        return TriangleArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulationLayout(SBGNSingleHeadedArc):
    """Layout for necessary stimulations.

    Draws a necessary stimulation with a bar followed by a triangular arrowhead.
    """

    arrowhead_bar_height: float = dataclasses.field(
        default=12.0, metadata={"description": "The height of the arrowhead bar."}
    )
    arrowhead_sep: float = dataclasses.field(
        default=3.0,
        metadata={"description": "The separation between the bar and the triangle."},
    )
    arrowhead_triangle_height: float = dataclasses.field(
        default=10.0, metadata={"description": "The height of the arrowhead triangle."}
    )
    arrowhead_triangle_width: float = dataclasses.field(
        default=10.0, metadata={"description": "The width of the arrowhead triangle."}
    )

    def _arrowhead_border_drawing_elements(self) -> list[DrawingElement]:
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
    """Layout for negative influences.

    Draws an inhibiting influence with a perpendicular bar arrowhead.
    """

    arrowhead_height: float = dataclasses.field(
        default=10.0, metadata={"description": "The height of the arrowhead."}
    )

    def _arrowhead_border_drawing_elements(self) -> list[DrawingElement]:
        return BarArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(SBGNSingleHeadedArc):
    """Layout for logic arcs.

    Draws a logic arc connecting an activity to a logical operator.
    """

    def _arrowhead_border_drawing_elements(self) -> list[DrawingElement]:
        return PolyLineArc._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(SBGNSingleHeadedArc):
    """Layout for equivalence arcs.

    Draws an equivalence arc linking a tag or terminal to its referenced element.
    """

    def _arrowhead_border_drawing_elements(self) -> list[DrawingElement]:
        return PolyLineArc._arrowhead_border_drawing_elements(self)
