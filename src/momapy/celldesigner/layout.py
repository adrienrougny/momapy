"""Layout classes for CellDesigner maps.

This module provides classes for representing the visual layout of a
CellDesigner pathway, including node layouts (species, compartments,
logic gates), arc layouts (reactions, modulations), and reaction node
decorations.
"""

import dataclasses
import enum
import math
import typing

from momapy.core.elements import Direction
from momapy.core.layout import Layout, Shape, TextLayout
from momapy.geometry import Point, Rotation, Transformation, get_normalized_angle
from momapy.coloring import Color, black, gray, white
from momapy.drawing import (
    ClosePath,
    DEFAULT_FONT_FAMILY,
    Ellipse as DrawingEllipse,
    EllipticalArc,
    Filter,
    FontStyle,
    FontWeight,
    LineTo,
    MoveTo,
    NoneValue,
    NoneValueType,
    Path,
    QuadraticCurveTo,
    Rectangle as DrawingRectangle,
)
from momapy.meta.shapes import (
    Ellipse as MetaShapesEllipse,
    Hexagon,
    Parallelogram,
    Rectangle as MetaShapesRectangle,
    Triangle as MetaShapesTriangle,
    TurnedHexagon,
)
from momapy.meta.nodes import Rectangle as MetaNodesRectangle
from momapy.meta.arcs import (
    Bar,
    Diamond,
    DoubleTriangle,
    Ellipse as MetaArcsEllipse,
    PolyLine,
    StraightBarb,
    Triangle as MetaArcsTriangle,
)
import momapy.sbgn.core
from momapy.sbgn.pd import MacromoleculeMultimerLayout

from momapy.celldesigner.elements import (
    CellDesignerNode,
    CellDesignerSingleHeadedArc,
    CellDesignerDoubleHeadedArc,
    _SimpleNodeMixin,
    _MultiNodeMixin,
)
from momapy.sbgn.core import _SBGNMixin, _TextMixin


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerLayout(Layout):
    """Class for CellDesigner layouts"""

    pass


_ACTIVE_XSEP = 4.0
_ACTIVE_YSEP = 4.0


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProteinLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for generic protein layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_subunit_shape(self, position, width, height):
        return MacromoleculeMultimerLayout._make_subunit_shape(
            self, position, width, height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProteinActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for generic protein layouts."""

    width: float = 60.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    rounded_corners: float = 5.0
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        return MacromoleculeMultimerLayout._make_subunit_shape(
            self, position, width, height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _IonChannelShape(Shape):
    position: Point
    width: float
    height: float
    right_rectangle_width: float
    rounded_corners: float

    def joint1(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width - self.rounded_corners,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.rounded_corners - self.height / 2,
        )

    def joint4(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.height / 2 - self.rounded_corners,
        )

    def joint5(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width - self.rounded_corners,
            self.height / 2,
        )

    def joint6(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            self.height / 2,
        )

    def joint7(self):
        return self.position + (
            -self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint8(self):
        return self.position + (
            -self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def joint9(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width + self.rounded_corners,
            self.height / 2,
        )

    def joint10(self):
        return self.position + (
            self.width / 2 - self.rounded_corners,
            -self.height / 2,
        )

    def joint11(self):
        return self.position + (
            self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def joint12(self):
        return self.position + (
            self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint13(self):
        return self.position + (
            self.width / 2 - self.rounded_corners,
            self.height / 2,
        )

    def joint14(self):
        return self.position + (
            self.rounded_corners + self.width / 2 - self.right_rectangle_width,
            self.height / 2,
        )

    def joint15(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.height / 2 - self.rounded_corners,
        )

    def joint16(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.rounded_corners - self.height / 2,
        )

    def drawing_elements(self):
        left_rectangle = DrawingRectangle(
            point=self.position - (self.width / 2, self.height / 2),
            height=self.height,
            width=self.width - self.right_rectangle_width,
            rx=self.rounded_corners,
            ry=self.rounded_corners,
        )
        right_rectangle = DrawingRectangle(
            point=self.position
            + (self.width / 2 - self.right_rectangle_width, -self.height / 2),
            height=self.height,
            width=self.right_rectangle_width,
            rx=self.rounded_corners,
            ry=self.rounded_corners,
        )
        return [left_rectangle, right_rectangle]


@dataclasses.dataclass(frozen=True, kw_only=True)
class IonChannelLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for generic ion channel layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0
    right_rectangle_width: float = 20.0

    def _make_subunit_shape(self, position, width, height):
        return _IonChannelShape(
            position=position,
            width=width,
            height=height,
            rounded_corners=self.rounded_corners,
            right_rectangle_width=self.right_rectangle_width,
        )

    def label_center(self):
        return Point(self.position.x - self.right_rectangle_width / 2, self.position.y)


@dataclasses.dataclass(frozen=True, kw_only=True)
class IonChannelActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for ion channel layouts."""

    width: float = 60.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    rounded_corners: float = 5.0
    right_rectangle_width: float = 20.0
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        return _IonChannelShape(
            position=position,
            width=width,
            height=height,
            rounded_corners=self.rounded_corners,
            right_rectangle_width=self.right_rectangle_width,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for complex layouts"""

    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 6.0
    # label -12 from south

    def _make_subunit_shape(self, position, width, height):
        return MetaShapesRectangle(
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

    def label_center(self):
        return self.south() - (0, 12)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for complex layouts."""

    width: float = 60.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    cut_corners: float = 6.0
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        return MetaShapesRectangle(
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
class SimpleMoleculeLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for simple chemical layouts"""

    width: float = 60.0
    height: float = 30.0

    def _make_subunit_shape(self, position, width, height):
        return MetaShapesEllipse(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleMoleculeActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for simple molecule layouts."""

    width: float = 60.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        return MetaShapesEllipse(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class IonLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for ion layouts"""

    width: float = 60.0
    height: float = 30.0

    def _make_subunit_shape(self, position, width, height):
        return MetaShapesEllipse(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class IonActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for ion layouts."""

    width: float = 60.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        return MetaShapesEllipse(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for unknown species layouts"""

    width: float = 60.0
    height: float = 30.0
    stroke: NoneValueType | Color | None = NoneValue
    fill: NoneValueType | Color | None = gray

    def _make_subunit_shape(self, position, width, height):
        return MetaShapesEllipse(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for unknown species layouts."""

    width: float = 60.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        return MetaShapesEllipse(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class _DegradedShape(Shape):
    position: Point
    width: float
    height: float

    def drawing_elements(self):
        circle = DrawingEllipse(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        actions = [
            MoveTo(self.position - (self.width / 2, -self.height / 2)),
            LineTo(self.position + (self.width / 2, -self.height / 2)),
        ]
        bar = Path(actions=actions)
        return [circle, bar]


@dataclasses.dataclass(frozen=True, kw_only=True)
class DegradedLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for degraded layouts"""

    width: float = 30.0
    height: float = 30.0

    def _make_subunit_shape(self, position, width, height):
        return _DegradedShape(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class DegradedActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for degraded layouts."""

    width: float = 30.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        return _DegradedShape(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class GeneLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for gene layouts"""

    width: float = 60.0
    height: float = 30.0

    def _make_subunit_shape(self, position, width, height):
        return MetaShapesRectangle(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class GeneActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for gene layouts."""

    width: float = 60.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        return MetaShapesRectangle(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for phenotype layouts"""

    width: float = 60.0
    height: float = 30.0
    angle: float = 60.0

    def _make_subunit_shape(self, position, width, height):
        return Hexagon(
            position=position,
            width=width,
            height=height,
            left_angle=self.angle,
            right_angle=self.angle,
        )

    def north_west(self) -> Point:
        """Return the north-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1()

    def north_north_west(self) -> Point:
        """Return the north-north-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() * 0.75 + shape.joint2() * 0.25

    def north(self) -> Point:
        """Return the north anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() / 2 + shape.joint2() / 2

    def north_north_east(self) -> Point:
        """Return the north-north-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() * 0.25 + shape.joint2() * 0.75

    def north_east(self) -> Point:
        """Return the north-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint2()

    def east_north_east(self) -> Point:
        """Return the east-north-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() / 2 + shape.joint2() / 2

    def east(self) -> Point:
        """Return the east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3()

    def east_south_east(self) -> Point:
        """Return the east-south-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() / 2 + shape.joint3() / 2

    def south_east(self) -> Point:
        """Return the south-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4()

    def south_south_east(self) -> Point:
        """Return the south-south-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint5() * 0.25 + shape.joint4() * 0.75

    def south(self) -> Point:
        """Return the south anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint5() / 2 + shape.joint4() / 2

    def south_south_west(self) -> Point:
        """Return the south-south-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint5() * 0.75 + shape.joint4() * 0.25

    def south_west(self) -> Point:
        """Return the south-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint5()

    def west_south_west(self) -> Point:
        """Return the west-south-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6() / 2 + shape.joint5() / 2

    def west(self) -> Point:
        """Return the west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6()

    def west_north_west(self) -> Point:
        """Return the west-north-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6() / 2 + shape.joint1() / 2


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for phenotype layouts."""

    width: float = 60.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    angle: float = 60.0
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        return Hexagon(
            position=position,
            width=width,
            height=height,
            left_angle=self.angle,
            right_angle=self.angle,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class RNALayout(_MultiNodeMixin, CellDesignerNode):
    """Class for RNA layouts"""

    width: float = 60.0
    height: float = 30.0
    angle: float = 45.0

    def _make_subunit_shape(self, position, width, height):
        return Parallelogram(
            position=position, width=width, height=height, angle=self.angle
        )

    def north_west(self) -> Point:
        """Return the north-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1()

    def north_north_west(self) -> Point:
        """Return the north-north-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() * 0.75 + shape.joint2() * 0.25

    def north(self) -> Point:
        """Return the north anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() / 2 + shape.joint2() / 2

    def north_north_east(self) -> Point:
        """Return the north-north-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() * 0.25 + shape.joint2() * 0.75

    def north_east(self) -> Point:
        """Return the north-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint2()

    def east_north_east(self) -> Point:
        """Return the east-north-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() * 0.25 + shape.joint2() * 0.75

    def east(self) -> Point:
        """Return the east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() / 2 + shape.joint2() / 2

    def east_south_east(self) -> Point:
        """Return the east-south-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() * 0.75 + shape.joint2() * 0.25

    def south_east(self) -> Point:
        """Return the south-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3()

    def south_south_east(self) -> Point:
        """Return the south-south-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.25 + shape.joint3() * 0.75

    def south(self) -> Point:
        """Return the south anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() / 2 + shape.joint3() / 2

    def south_south_west(self) -> Point:
        """Return the south-south-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.75 + shape.joint3() * 0.25

    def south_west(self) -> Point:
        """Return the south-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4()

    def west_south_west(self) -> Point:
        """Return the west-south-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.75 + shape.joint1() * 0.25

    def west(self) -> Point:
        """Return the west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() / 2 + shape.joint1() / 2

    def west_north_west(self) -> Point:
        """Return the west-north-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.25 + shape.joint1() * 0.75


@dataclasses.dataclass(frozen=True, kw_only=True)
class RNAActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for RNA layouts."""

    width: float = 60.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    angle: float = 45.0
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        return Parallelogram(
            position=position, width=width, height=height, angle=self.angle
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class AntisenseRNALayout(_MultiNodeMixin, CellDesignerNode):
    """Class for antisense RNA layouts"""

    width: float = 60.0
    height: float = 30.0
    angle: float = 45.0

    def _make_subunit_shape(self, position, width, height):
        return Parallelogram(
            position=position,
            width=width,
            height=height,
            angle=180 - self.angle,
        )

    def north_west(self) -> Point:
        """Return the north-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1()

    def north_north_west(self) -> Point:
        """Return the north-north-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() * 0.75 + shape.joint2() * 0.25

    def north(self) -> Point:
        """Return the north anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() / 2 + shape.joint2() / 2

    def north_north_east(self) -> Point:
        """Return the north-north-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() * 0.25 + shape.joint2() * 0.75

    def north_east(self) -> Point:
        """Return the north-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint2()

    def east_north_east(self) -> Point:
        """Return the east-north-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() * 0.25 + shape.joint2() * 0.75

    def east(self) -> Point:
        """Return the east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() / 2 + shape.joint2() / 2

    def east_south_east(self) -> Point:
        """Return the east-south-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() * 0.75 + shape.joint2() * 0.25

    def south_east(self) -> Point:
        """Return the south-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3()

    def south_south_east(self) -> Point:
        """Return the south-south-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.25 + shape.joint3() * 0.75

    def south(self) -> Point:
        """Return the south anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() / 2 + shape.joint3() / 2

    def south_south_west(self) -> Point:
        """Return the south-south-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.75 + shape.joint3() * 0.25

    def south_west(self) -> Point:
        """Return the south-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4()

    def west_south_west(self) -> Point:
        """Return the west-south-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.75 + shape.joint1() * 0.25

    def west(self) -> Point:
        """Return the west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() / 2 + shape.joint1() / 2

    def west_north_west(self) -> Point:
        """Return the west-north-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.25 + shape.joint1() * 0.75


@dataclasses.dataclass(frozen=True, kw_only=True)
class AntisenseRNAActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for antisense RNA layouts."""

    width: float = 60.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    angle: float = 45.0
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        return Parallelogram(
            position=position,
            width=width,
            height=height,
            angle=180 - self.angle,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _TruncatedProteinShape(Shape):
    position: Point
    width: float
    height: float
    rounded_corners: float
    vertical_truncation: float  # proportion of total height, number in ]0, 1[
    horizontal_truncation: float  # proportion of total width number in ]0, 1[

    def joint1(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2,
            self.height / 2 - self.vertical_truncation * self.height,
        )

    def joint4(self):
        return self.position + (
            self.width / 2 - self.horizontal_truncation * self.width,
            self.vertical_truncation * self.height - self.height / 2,
        )

    def joint5(self):
        return self.position + (
            self.width / 2 - self.horizontal_truncation * self.width,
            self.height / 2,
        )

    def joint6(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            self.height / 2,
        )

    def joint7(self):
        return self.position + (
            -self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint8(self):
        return self.position + (
            -self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def drawing_elements(self):
        actions = [
            MoveTo(self.joint1()),
            LineTo(self.joint2()),
            LineTo(self.joint3()),
            LineTo(self.joint4()),
            LineTo(self.joint5()),
            LineTo(self.joint6()),
            EllipticalArc(
                self.joint7(),
                self.rounded_corners,
                self.rounded_corners,
                0,
                0,
                1,
            ),
            LineTo(self.joint8()),
            EllipticalArc(
                self.joint1(),
                self.rounded_corners,
                self.rounded_corners,
                0,
                0,
                1,
            ),
            ClosePath(),
        ]
        border = Path(actions=actions)
        return [border]


@dataclasses.dataclass(frozen=True, kw_only=True)
class TruncatedProteinLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for truncated protein layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 15.0
    vertical_truncation: float = 0.40
    horizontal_truncation: float = 0.20

    def _make_subunit_shape(self, position, width, height):
        return _TruncatedProteinShape(
            position=position,
            width=width,
            height=height,
            rounded_corners=self.rounded_corners,
            vertical_truncation=self.vertical_truncation,
            horizontal_truncation=self.horizontal_truncation,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TruncatedProteinActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for truncated protein layouts."""

    width: float = 60.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    rounded_corners: float = 15.0
    vertical_truncation: float = 0.40
    horizontal_truncation: float = 0.20
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        return _TruncatedProteinShape(
            position=position,
            width=width,
            height=height,
            rounded_corners=self.rounded_corners,
            vertical_truncation=self.vertical_truncation,
            horizontal_truncation=self.horizontal_truncation,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReceptorLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for receptor layouts"""

    width: float = 60.0
    height: float = 30.0
    vertical_truncation: float = 0.10  # proportion of total height, number in ]0, 1[

    def _make_subunit_shape(self, position, width, height):
        angle = math.atan2(width / 2, self.vertical_truncation * height)
        angle = get_normalized_angle(angle)
        angle = math.degrees(angle)
        return TurnedHexagon(
            position=position,
            width=width,
            height=height,
            top_angle=180 - angle,
            bottom_angle=angle,
        )

    def north_west(self) -> Point:
        """Return the north-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1()

    def north_north_west(self) -> Point:
        """Return the north-north-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() / 2 + shape.joint2() / 2

    def north(self) -> Point:
        """Return the north anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint2()

    def north_north_east(self) -> Point:
        """Return the north-north-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint2() * 0.25 + shape.joint3() * 0.75

    def north_east(self) -> Point:
        """Return the north-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3()

    def east_north_east(self) -> Point:
        """Return the east-north-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.25 + shape.joint3() * 0.75

    def east(self) -> Point:
        """Return the east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() / 2 + shape.joint3() / 2

    def east_south_east(self) -> Point:
        """Return the east-south-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.75 + shape.joint3() * 0.25

    def south_east(self) -> Point:
        """Return the south-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4()

    def south_south_east(self) -> Point:
        """Return the south-south-east anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint5() / 2 + shape.joint4() / 2

    def south(self) -> Point:
        """Return the south anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint5()

    def south_south_west(self) -> Point:
        """Return the south-south-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6() / 2 + shape.joint5() / 2

    def south_west(self) -> Point:
        """Return the south-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6()

    def west_south_west(self) -> Point:
        """Return the west-south-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6() * 0.75 + shape.joint1() * 0.25

    def west(self) -> Point:
        """Return the west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6() / 2 + shape.joint1() / 2

    def west_north_west(self) -> Point:
        """Return the west-north-west anchor point of the top subunit shape."""
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6() * 0.25 + shape.joint1() * 0.75


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReceptorActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for receptor layouts."""

    width: float = 60.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    vertical_truncation: float = 0.10
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        angle = math.atan2(width / 2, self.vertical_truncation * height)
        angle = get_normalized_angle(angle)
        angle = math.degrees(angle)
        return TurnedHexagon(
            position=position,
            width=width,
            height=height,
            top_angle=180 - angle,
            bottom_angle=angle,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _DrugShape(Shape):
    position: Point
    width: float
    height: float
    horizontal_proportion: float  # ]0, 0.5[
    sep: float

    def joint1(self):
        return self.position + (
            -self.width / 2 + self.horizontal_proportion * self.width,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2 - self.horizontal_proportion * self.width,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2 - self.horizontal_proportion * self.width,
            self.height / 2,
        )

    def joint4(self):
        return self.position + (
            -self.width / 2 + self.horizontal_proportion * self.width,
            self.height / 2,
        )

    def drawing_elements(self):
        actions = [
            MoveTo(self.joint1()),
            LineTo(self.joint2()),
            EllipticalArc(
                self.joint3(),
                self.horizontal_proportion * self.width,
                self.height / 2,
                0,
                0,
                1,
            ),
            LineTo(self.joint4()),
            EllipticalArc(
                self.joint1(),
                self.horizontal_proportion * self.width,
                self.height / 2,
                0,
                0,
                1,
            ),
            ClosePath(),
        ]
        outer_stadium = Path(actions=actions)
        inner_joint1 = self.joint1() + (0, self.sep)
        inner_joint2 = self.joint2() + (0, self.sep)
        inner_joint3 = self.joint3() + (0, -self.sep)
        inner_joint4 = self.joint4() + (0, -self.sep)
        inner_rx = self.horizontal_proportion * self.width - self.sep
        inner_ry = self.height / 2 - self.sep
        actions = [
            MoveTo(inner_joint1),
            LineTo(inner_joint2),
            EllipticalArc(
                inner_joint3,
                inner_rx,
                inner_ry,
                0,
                0,
                1,
            ),
            LineTo(inner_joint4),
            EllipticalArc(
                inner_joint1,
                inner_rx,
                inner_ry,
                0,
                0,
                1,
            ),
            ClosePath(),
        ]
        inner_stadium = Path(actions=actions)
        return [outer_stadium, inner_stadium]


@dataclasses.dataclass(frozen=True, kw_only=True)
class DrugLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for drug layouts"""

    width: float = 60.0
    height: float = 30.0
    horizontal_proportion: float = 0.20
    sep: float = 4.0

    def _make_subunit_shape(self, position, width, height):
        return _DrugShape(
            position=position,
            width=width,
            height=height,
            horizontal_proportion=self.horizontal_proportion,
            sep=self.sep,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class DrugActiveLayout(_MultiNodeMixin, CellDesignerNode):
    """Active border for drug layouts."""

    width: float = 60.0 + _ACTIVE_XSEP * 2
    height: float = 30.0 + _ACTIVE_YSEP * 2
    horizontal_proportion: float = 0.20
    sep: float = 4.0
    fill: NoneValueType | Color | None = NoneValue
    stroke_dasharray: NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    stroke_width: float | None = 1.0

    def _make_subunit_shape(self, position, width, height):
        return _DrugShape(
            position=position,
            width=width,
            height=height,
            horizontal_proportion=self.horizontal_proportion,
            sep=self.sep,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class StructuralStateLayout(_SimpleNodeMixin, CellDesignerNode):
    """Class for structural states layouts"""

    width: float = 50.0
    height: float = 16.0

    def _make_shape(self):
        return MetaShapesEllipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModificationLayout(_SimpleNodeMixin, CellDesignerNode):
    """Class for modification layouts"""

    width: float = 16.0
    height: float = 16.0

    def _make_shape(self):
        return MetaShapesEllipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _OvalCompartmentShape(Shape):
    position: Point
    width: float
    height: float
    inner_fill: NoneValueType | Color | None = None
    inner_stroke: NoneValueType | Color | None = None
    inner_stroke_width: float | None = None
    sep: float = 12.0

    def drawing_elements(self):
        outer_oval = DrawingEllipse(
            point=self.position,
            rx=self.width / 2,
            ry=self.height / 2,
        )
        inner_oval = DrawingEllipse(
            fill=self.inner_fill,
            stroke=self.inner_stroke,
            stroke_width=self.inner_stroke_width,
            point=self.position,
            rx=self.width / 2 - self.sep,
            ry=self.height / 2 - self.sep,
        )
        return [outer_oval, inner_oval]


@dataclasses.dataclass(frozen=True, kw_only=True)
class OvalCompartmentLayout(_SimpleNodeMixin, CellDesignerNode):
    """Class for oval compartment layouts"""

    height: float = 16.0
    inner_fill: NoneValueType | Color | None = white
    inner_stroke: NoneValueType | Color | None = black
    inner_stroke_width: float | None = 1.0
    sep: float = 12.0
    width: float = 16.0

    def _make_shape(self):
        return _OvalCompartmentShape(
            height=self.height,
            inner_fill=self.inner_fill,
            inner_stroke=self.inner_stroke,
            inner_stroke_width=self.inner_stroke_width,
            position=self.position,
            width=self.width,
            sep=self.sep,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _RectangleCompartmentShape(Shape):
    position: Point
    width: float
    height: float
    inner_fill: NoneValueType | Color | None = None
    inner_rounded_corners: float = 10.0
    inner_stroke: NoneValueType | Color | None = None
    inner_stroke_width: float | None = None
    rounded_corners: float = 10.0
    sep: float = 12.0

    def drawing_elements(self):
        outer_rectangle = DrawingRectangle(
            point=self.position - (self.width / 2, self.height / 2),
            height=self.height,
            rx=self.rounded_corners,
            ry=self.rounded_corners,
            width=self.width,
        )
        inner_rectangle = DrawingRectangle(
            fill=self.inner_fill,
            height=self.height - 2 * self.sep,
            point=self.position
            - (self.width / 2 - self.sep, self.height / 2 - self.sep),
            rx=self.inner_rounded_corners,
            ry=self.inner_rounded_corners,
            stroke=self.inner_stroke,
            stroke_width=self.inner_stroke_width,
            width=self.width - 2 * self.sep,
        )
        return [outer_rectangle, inner_rectangle]


@dataclasses.dataclass(frozen=True, kw_only=True)
class RectangleCompartmentLayout(_SimpleNodeMixin, CellDesignerNode):
    """Class for rectangle compartment layouts"""

    width: float = 16.0
    height: float = 16.0
    inner_fill: NoneValueType | Color | None = white
    inner_rounded_corners: float = 10.0
    inner_stroke: NoneValueType | Color | None = black
    inner_stroke_width: float | None = 1.0
    rounded_corners: float = 10.0
    sep: float = 12.0

    def _make_shape(self):
        return _RectangleCompartmentShape(
            height=self.height,
            inner_fill=self.inner_fill,
            inner_rounded_corners=self.inner_rounded_corners,
            inner_stroke=self.inner_stroke,
            inner_stroke_width=self.inner_stroke_width,
            position=self.position,
            rounded_corners=self.rounded_corners,
            sep=self.sep,
            width=self.width,
        )


class CompartmentCorner(enum.Enum):
    """Rounded-corner position for a `CornerCompartmentLayout`."""

    NORTHWEST = "NORTHWEST"
    NORTHEAST = "NORTHEAST"
    SOUTHWEST = "SOUTHWEST"
    SOUTHEAST = "SOUTHEAST"


class CompartmentSide(enum.Enum):
    """Border-side position for a `LineCompartmentLayout`."""

    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"


@dataclasses.dataclass(frozen=True, kw_only=True)
class _CornerCompartmentShape(Shape):
    position: Point
    width: float
    height: float
    corner: CompartmentCorner
    inner_stroke: NoneValueType | Color | None = None
    inner_stroke_width: float | None = None
    rounded_corners: float = 40.0
    sep: float = 12.0

    def drawing_elements(self):
        left = self.position.x - self.width / 2
        right = self.position.x + self.width / 2
        top = self.position.y - self.height / 2
        bottom = self.position.y + self.height / 2
        sep = self.sep
        r_outer = self.rounded_corners
        r_inner = max(r_outer - sep, 0.0)
        P = Point
        if self.corner is CompartmentCorner.NORTHWEST:
            outer_start = P(right, top)
            outer_tan_a = P(left + r_outer, top)
            outer_corner = P(left, top)
            outer_tan_b = P(left, top + r_outer)
            outer_end = P(left, bottom)
            inner_start = P(right, top + sep)
            inner_tan_a = P(left + r_outer, top + sep)
            inner_corner = P(left + sep, top + sep)
            inner_tan_b = P(left + sep, top + r_outer)
            inner_end = P(left + sep, bottom)
        elif self.corner is CompartmentCorner.NORTHEAST:
            outer_start = P(left, top)
            outer_tan_a = P(right - r_outer, top)
            outer_corner = P(right, top)
            outer_tan_b = P(right, top + r_outer)
            outer_end = P(right, bottom)
            inner_start = P(left, top + sep)
            inner_tan_a = P(right - r_outer, top + sep)
            inner_corner = P(right - sep, top + sep)
            inner_tan_b = P(right - sep, top + r_outer)
            inner_end = P(right - sep, bottom)
        elif self.corner is CompartmentCorner.SOUTHWEST:
            outer_start = P(right, bottom)
            outer_tan_a = P(left + r_outer, bottom)
            outer_corner = P(left, bottom)
            outer_tan_b = P(left, bottom - r_outer)
            outer_end = P(left, top)
            inner_start = P(right, bottom - sep)
            inner_tan_a = P(left + r_outer, bottom - sep)
            inner_corner = P(left + sep, bottom - sep)
            inner_tan_b = P(left + sep, bottom - r_outer)
            inner_end = P(left + sep, top)
        else:  # SOUTHEAST
            outer_start = P(left, bottom)
            outer_tan_a = P(right - r_outer, bottom)
            outer_corner = P(right, bottom)
            outer_tan_b = P(right, bottom - r_outer)
            outer_end = P(right, top)
            inner_start = P(left, bottom - sep)
            inner_tan_a = P(right - r_outer, bottom - sep)
            inner_corner = P(right - sep, bottom - sep)
            inner_tan_b = P(right - sep, bottom - r_outer)
            inner_end = P(right - sep, top)
        if r_inner <= 0:
            inner_tan_a = inner_corner
            inner_tan_b = inner_corner
        fill_path = Path(
            stroke=NoneValue,
            actions=(
                MoveTo(outer_start),
                LineTo(outer_tan_a),
                QuadraticCurveTo(point=outer_tan_b, control_point=outer_corner),
                LineTo(outer_end),
                LineTo(inner_end),
                LineTo(inner_tan_b),
                QuadraticCurveTo(point=inner_tan_a, control_point=inner_corner),
                LineTo(inner_start),
                ClosePath(),
            ),
        )
        outer_path = Path(
            fill=NoneValue,
            actions=(
                MoveTo(outer_start),
                LineTo(outer_tan_a),
                QuadraticCurveTo(point=outer_tan_b, control_point=outer_corner),
                LineTo(outer_end),
            ),
        )
        inner_path = Path(
            fill=NoneValue,
            stroke=self.inner_stroke,
            stroke_width=self.inner_stroke_width,
            actions=(
                MoveTo(inner_start),
                LineTo(inner_tan_a),
                QuadraticCurveTo(point=inner_tan_b, control_point=inner_corner),
                LineTo(inner_end),
            ),
        )
        return [fill_path, outer_path, inner_path]


@dataclasses.dataclass(frozen=True, kw_only=True)
class CornerCompartmentLayout(_SimpleNodeMixin, CellDesignerNode):
    """Class for corner closeup compartment layouts.

    Represents CellDesigner `SQUARE_CLOSEUP_{NORTHWEST,NORTHEAST,
    SOUTHWEST,SOUTHEAST}` compartments: a quarter-rectangle whose
    rounded border sits at the named corner while the opposite sides
    coincide with the canvas edges.
    """

    width: float = 16.0
    height: float = 16.0
    corner: CompartmentCorner = CompartmentCorner.NORTHWEST
    inner_stroke: NoneValueType | Color | None = black
    inner_stroke_width: float | None = 1.0
    rounded_corners: float = 40.0
    sep: float = 12.0

    def _make_shape(self):
        return _CornerCompartmentShape(
            position=self.position,
            width=self.width,
            height=self.height,
            corner=self.corner,
            inner_stroke=self.inner_stroke,
            inner_stroke_width=self.inner_stroke_width,
            rounded_corners=self.rounded_corners,
            sep=self.sep,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _LineCompartmentShape(Shape):
    position: Point
    width: float
    height: float
    side: CompartmentSide
    inner_stroke: NoneValueType | Color | None = None
    inner_stroke_width: float | None = None
    sep: float = 12.0

    def drawing_elements(self):
        left = self.position.x - self.width / 2
        right = self.position.x + self.width / 2
        top = self.position.y - self.height / 2
        bottom = self.position.y + self.height / 2
        sep = self.sep
        P = Point
        if self.side is CompartmentSide.NORTH:
            outer_a, outer_b = P(left, top), P(right, top)
            inner_a, inner_b = P(left, top + sep), P(right, top + sep)
        elif self.side is CompartmentSide.SOUTH:
            outer_a, outer_b = P(left, bottom), P(right, bottom)
            inner_a, inner_b = P(left, bottom - sep), P(right, bottom - sep)
        elif self.side is CompartmentSide.EAST:
            outer_a, outer_b = P(right, top), P(right, bottom)
            inner_a, inner_b = P(right - sep, top), P(right - sep, bottom)
        else:  # WEST
            outer_a, outer_b = P(left, top), P(left, bottom)
            inner_a, inner_b = P(left + sep, top), P(left + sep, bottom)
        fill_path = Path(
            stroke=NoneValue,
            actions=(
                MoveTo(outer_a),
                LineTo(outer_b),
                LineTo(inner_b),
                LineTo(inner_a),
                ClosePath(),
            ),
        )
        outer_path = Path(
            fill=NoneValue,
            actions=(
                MoveTo(outer_a),
                LineTo(outer_b),
            ),
        )
        inner_path = Path(
            fill=NoneValue,
            stroke=self.inner_stroke,
            stroke_width=self.inner_stroke_width,
            actions=(
                MoveTo(inner_a),
                LineTo(inner_b),
            ),
        )
        return [fill_path, outer_path, inner_path]


@dataclasses.dataclass(frozen=True, kw_only=True)
class LineCompartmentLayout(_SimpleNodeMixin, CellDesignerNode):
    """Class for line closeup compartment layouts.

    Represents CellDesigner `SQUARE_CLOSEUP_{NORTH,SOUTH,EAST,WEST}`
    compartments: a half-plane bounded on the named side by a single
    horizontal or vertical double line spanning the canvas.
    """

    width: float = 16.0
    height: float = 16.0
    side: CompartmentSide = CompartmentSide.NORTH
    inner_stroke: NoneValueType | Color | None = black
    inner_stroke_width: float | None = 1.0
    sep: float = 12.0

    def _make_shape(self):
        return _LineCompartmentShape(
            position=self.position,
            width=self.width,
            height=self.height,
            side=self.side,
            inner_stroke=self.inner_stroke,
            inner_stroke_width=self.inner_stroke_width,
            sep=self.sep,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ConsumptionLayout(CellDesignerSingleHeadedArc):
    """Class for consumption layouts"""

    def _arrowhead_border_drawing_elements(self):
        return PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProductionLayout(CellDesignerSingleHeadedArc):
    """Class for production layouts"""

    arrowhead_fill: NoneValueType | Color | None = black
    arrowhead_height: float = 8.0
    arrowhead_width: float = 15.0
    end_shorten: float = 2.0

    def _arrowhead_border_drawing_elements(self):
        return MetaArcsTriangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CatalysisLayout(CellDesignerSingleHeadedArc):
    """Class for catalysis layouts"""

    arrowhead_fill: NoneValueType | Color | None = white
    arrowhead_height: float = 7.0
    arrowhead_width: float = 7.0

    def _arrowhead_border_drawing_elements(self):
        return MetaArcsEllipse._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownCatalysisLayout(CellDesignerSingleHeadedArc):
    """Class for unknown catalysis layouts"""

    arrowhead_fill: NoneValueType | Color | None = white
    arrowhead_height: float = 7.0
    arrowhead_width: float = 7.0
    path_stroke_dasharray: NoneValueType | tuple[float] | None = (12, 4)

    def _arrowhead_border_drawing_elements(self):
        return MetaArcsEllipse._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class InhibitionLayout(CellDesignerSingleHeadedArc):
    """Class for inhibition layouts"""

    arrowhead_height: float = 10.0
    end_shorten: float = 3.0

    def _arrowhead_border_drawing_elements(self):
        return Bar._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInhibitionLayout(CellDesignerSingleHeadedArc):
    """Class for unknown inhibition layouts"""

    arrowhead_height: float = 10.0
    end_shorten: float = 3.0
    path_stroke_dasharray: NoneValueType | tuple[float] | None = (12, 4)

    def _arrowhead_border_drawing_elements(self):
        return Bar._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhysicalStimulationLayout(CellDesignerSingleHeadedArc):
    """Class for physical stimulation layouts"""

    arrowhead_fill: NoneValueType | Color | None = white
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return MetaArcsTriangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownPhysicalStimulationLayout(CellDesignerSingleHeadedArc):
    """Class for unknown physical stimulation layouts"""

    arrowhead_fill: NoneValueType | Color | None = white
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0
    path_stroke_dasharray: NoneValueType | tuple[float] | None = (12, 4)

    def _arrowhead_border_drawing_elements(self):
        return MetaArcsTriangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModulationLayout(CellDesignerSingleHeadedArc):
    """Class for modulation layouts"""

    arrowhead_fill: NoneValueType | Color | None = white
    arrowhead_height: float = 8.0
    arrowhead_width: float = 15.0

    def _arrowhead_border_drawing_elements(self):
        return Diamond._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownModulationLayout(CellDesignerSingleHeadedArc):
    """Class for unknown modulation layouts"""

    arrowhead_fill: NoneValueType | Color | None = white
    arrowhead_height: float = 8.0
    arrowhead_width: float = 15.0
    path_stroke_dasharray: NoneValueType | tuple[float] | None = (12, 4)

    def _arrowhead_border_drawing_elements(self):
        return Diamond._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluenceLayout(CellDesignerSingleHeadedArc):
    """Class for positive influence layouts"""

    arrowhead_fill: NoneValueType | Color | None = NoneValue
    arrowhead_height: float = 10.0
    arrowhead_stroke_width: float | None = 2.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return StraightBarb._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownPositiveInfluenceLayout(CellDesignerSingleHeadedArc):
    """Class for unknown positive influence layouts"""

    arrowhead_fill: NoneValueType | Color | None = NoneValue
    arrowhead_height: float = 10.0
    arrowhead_stroke_width: float | None = 2.0
    arrowhead_width: float = 10.0
    path_stroke_dasharray: NoneValueType | tuple[float] | None = (12, 4)

    def _arrowhead_border_drawing_elements(self):
        return StraightBarb._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TriggeringLayout(CellDesignerSingleHeadedArc):
    """Class for triggering layouts"""

    arrowhead_bar_height: float = 8.0
    arrowhead_fill: NoneValueType | Color | None = white
    arrowhead_sep: float = 5.0
    arrowhead_triangle_height: float = 10.0
    arrowhead_triangle_width: float = 15.0

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
        triangle = MetaShapesTriangle(
            position=Point(
                self.arrowhead_sep + self.arrowhead_triangle_width / 2,
                0,
            ),
            width=self.arrowhead_triangle_width,
            height=self.arrowhead_triangle_height,
            direction=Direction.RIGHT,
        )
        return [bar, sep] + triangle.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownTriggeringLayout(CellDesignerSingleHeadedArc):
    """Class for unknown triggering layouts"""

    arrowhead_bar_height: float = 8.0
    arrowhead_fill: NoneValueType | Color | None = white
    arrowhead_sep: float = 5.0
    arrowhead_triangle_height: float = 10.0
    arrowhead_triangle_width: float = 15.0
    path_stroke_dasharray: NoneValueType | tuple[float] | None = (12, 4)

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
        triangle = MetaShapesTriangle(
            position=Point(
                self.arrowhead_sep + self.arrowhead_triangle_width / 2,
                0,
            ),
            width=self.arrowhead_triangle_width,
            height=self.arrowhead_triangle_height,
            direction=Direction.RIGHT,
        )
        return [bar, sep] + triangle.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReactionLayout(CellDesignerDoubleHeadedArc):
    reversible: bool = False


@dataclasses.dataclass(frozen=True, kw_only=True)
class _ReactionNodeMixin(_SBGNMixin):
    _reaction_node_text: typing.ClassVar[str | None] = None
    _font_family: typing.ClassVar[str] = DEFAULT_FONT_FAMILY
    _font_size_func: typing.ClassVar[typing.Callable]
    _font_style: typing.ClassVar[FontStyle] = FontStyle.NORMAL
    _font_weight: typing.ClassVar[FontWeight | float] = FontWeight.NORMAL
    _font_fill: typing.ClassVar[Color | NoneValueType] = black
    _font_stroke: typing.ClassVar[Color | NoneValueType] = NoneValue
    left_connector_fraction: float = 0.375
    right_connector_fraction: float = 0.625
    reaction_node_height: float = 10.0
    reaction_node_width: float = 10.0
    reaction_node_segment: int = 1
    reaction_node_stroke: NoneValueType | Color | None = black
    reaction_node_stroke_width: float | None = 1.0
    reaction_node_stroke_dasharray: NoneValueType | tuple[float] | None = None
    reaction_node_stroke_dashoffset: float | None = None
    reaction_node_fill: NoneValueType | Color | None = white
    reaction_node_transform: NoneValueType | tuple[Transformation] | None = None
    reaction_node_filter: NoneValueType | Filter | None = None

    def left_connector_tip(self):
        segment = self.segments[self.reaction_node_segment]
        position = segment.get_position_at_fraction(self.left_connector_fraction)
        return position

    def right_connector_tip(self):
        segment = self.segments[self.reaction_node_segment]
        position = segment.get_position_at_fraction(self.right_connector_fraction)
        return position

    def reaction_node_border(self, point):
        reaction_node = self._make_reaction_node()
        rotation = self._make_reaction_node_rotation()
        rotated_point = point.transformed(rotation)
        border_point = reaction_node.own_border(rotated_point)
        if border_point is None:
            border_point = reaction_node.center()
        border_point = border_point.transformed(rotation.inverted())
        return border_point

    def reaction_node_angle(self, angle):
        reaction_node = self._make_reaction_node()
        border_point = reaction_node.own_angle(
            angle, self._get_reaction_node_position()
        )
        if border_point is None:
            border_point = reaction_node.center()
        rotation = self._make_reaction_node_rotation()
        border_point = border_point.transformed(
            rotation, self._get_reaction_node_position()
        )
        return border_point

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        return [obj._make_rotated_reaction_node_drawing_element()]

    def _get_reaction_node_position(self):
        segment = self.segments[self.reaction_node_segment]
        position = segment.get_position_at_fraction(0.5)
        return position

    def _get_reaction_node_rotation_angle(self):
        segment = self.segments[self.reaction_node_segment]
        angle = segment.get_angle_to_horizontal()
        return angle

    def _make_reaction_node_rotation(self):
        angle = self._get_reaction_node_rotation_angle()
        position = self._get_reaction_node_position()
        rotation = Rotation(angle, position)
        return rotation

    def _make_reaction_node(self):
        position = self._get_reaction_node_position()
        if self._reaction_node_text is not None:
            label = TextLayout(
                text=self._reaction_node_text,
                position=position,
                font_family=self._font_family,
                font_size=self._font_size_func(),
                font_style=self._font_style,
                font_weight=self._font_weight,
                fill=self._font_fill,
                stroke=self._font_stroke,
                transform=(self._make_reaction_node_rotation(),),
            )
        else:
            label = None
        reaction_node = MetaNodesRectangle(
            height=self.reaction_node_height,
            position=position,
            width=self.reaction_node_width,
            stroke=self.reaction_node_stroke,
            stroke_width=self.reaction_node_stroke_width,
            stroke_dasharray=self.reaction_node_stroke_dasharray,
            stroke_dashoffset=self.reaction_node_stroke_dashoffset,
            fill=self.reaction_node_fill,
            transform=self.reaction_node_transform,
            filter=self.reaction_node_filter,
            label=label,
        )
        return reaction_node

    def _make_rotated_reaction_node_drawing_element(self):
        reaction_node = self._make_reaction_node()
        drawing_element = reaction_node.drawing_elements()[0]
        rotation = self._make_reaction_node_rotation()
        drawing_element = drawing_element.transformed(rotation)
        return drawing_element


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateTransitionLayout(ReactionLayout, _ReactionNodeMixin):
    """Class for state transition layouts"""

    _reaction_node_text: typing.ClassVar[str | None] = None
    end_arrowhead_fill: NoneValueType | Color | None = black
    end_arrowhead_filter: NoneValueType | Filter | None = None
    end_arrowhead_height: float = 8.0
    end_arrowhead_stroke: NoneValueType | Color | None = black
    end_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    end_arrowhead_width: float = 15.0
    end_shorten: float = 2.0
    reversible: bool = False
    start_arrowhead_fill: NoneValueType | Color | None = black
    start_arrowhead_filter: NoneValueType | Filter | None = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: NoneValueType | Color | None = black
    start_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            return DoubleTriangle._start_arrowhead_border_drawing_elements(self)
        return []

    def _end_arrowhead_border_drawing_elements(self):
        return DoubleTriangle._end_arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class KnownTransitionOmittedLayout(ReactionLayout, _ReactionNodeMixin):
    """Class for known transition omitted layouts"""

    _font_size_func: typing.ClassVar[typing.Callable | None] = (
        lambda obj: obj.reaction_node_width / 1.1
    )
    _font_weight: typing.ClassVar[FontWeight | float] = FontWeight.BOLD
    _reaction_node_text: typing.ClassVar[str | None] = "//"
    end_arrowhead_fill: NoneValueType | Color | None = black
    end_arrowhead_filter: NoneValueType | Filter | None = None
    end_arrowhead_height: float = 8.0
    end_arrowhead_stroke: NoneValueType | Color | None = black
    end_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    end_arrowhead_width: float = 15.0
    end_shorten: float = 2.0
    start_arrowhead_fill: NoneValueType | Color | None = black
    start_arrowhead_filter: NoneValueType | Filter | None = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: NoneValueType | Color | None = black
    start_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            return DoubleTriangle._start_arrowhead_border_drawing_elements(self)
        return []

    def _end_arrowhead_border_drawing_elements(self):
        return DoubleTriangle._end_arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownTransitionLayout(ReactionLayout, _ReactionNodeMixin):
    """Class for unknown transition layouts"""

    _font_size_func: typing.ClassVar[typing.Callable | None] = (
        lambda obj: obj.reaction_node_width / 1.1
    )
    _font_weight: typing.ClassVar[FontWeight | float] = FontWeight.BOLD
    _reaction_node_text: typing.ClassVar[str | None] = "?"
    end_arrowhead_fill: NoneValueType | Color | None = black
    end_arrowhead_filter: NoneValueType | Filter | None = None
    end_arrowhead_height: float = 8.0
    end_arrowhead_stroke: NoneValueType | Color | None = black
    end_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    end_arrowhead_width: float = 15.0
    end_shorten: float = 2.0
    start_arrowhead_fill: NoneValueType | Color | None = black
    start_arrowhead_filter: NoneValueType | Filter | None = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: NoneValueType | Color | None = black
    start_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            return DoubleTriangle._start_arrowhead_border_drawing_elements(self)
        return []

    def _end_arrowhead_border_drawing_elements(self):
        return DoubleTriangle._end_arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TranscriptionLayout(ReactionLayout, _ReactionNodeMixin):
    """Class for transcription layouts"""

    _reaction_node_text: typing.ClassVar[str | None] = None
    end_arrowhead_fill: NoneValueType | Color | None = black
    end_arrowhead_filter: NoneValueType | Filter | None = None
    end_arrowhead_height: float = 8.0
    end_arrowhead_stroke: NoneValueType | Color | None = black
    end_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    end_arrowhead_width: float = 15.0
    end_shorten: float = 2.0
    path_stroke_dasharray: NoneValueType | tuple[float] | None = (
        12,
        4,
        2,
        4,
        2,
        4,
    )
    start_arrowhead_fill: NoneValueType | Color | None = black
    start_arrowhead_filter: NoneValueType | Filter | None = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: NoneValueType | Color | None = black
    start_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            return DoubleTriangle._start_arrowhead_border_drawing_elements(self)
        return []

    def _end_arrowhead_border_drawing_elements(self):
        return DoubleTriangle._end_arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TranslationLayout(ReactionLayout, _ReactionNodeMixin):
    """Class for translation layouts"""

    _reaction_node_text: typing.ClassVar[str | None] = None
    end_arrowhead_fill: NoneValueType | Color | None = black
    end_arrowhead_filter: NoneValueType | Filter | None = None
    end_arrowhead_height: float = 8.0
    end_arrowhead_stroke: NoneValueType | Color | None = black
    end_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    end_arrowhead_width: float = 15.0
    end_shorten: float = 2.0
    path_stroke_dasharray: NoneValueType | tuple[float] | None = (
        12,
        4,
        2,
        4,
    )
    start_arrowhead_fill: NoneValueType | Color | None = black
    start_arrowhead_filter: NoneValueType | Filter | None = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: NoneValueType | Color | None = black
    start_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            return DoubleTriangle._start_arrowhead_border_drawing_elements(self)
        return []

    def _end_arrowhead_border_drawing_elements(self):
        return DoubleTriangle._end_arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TransportLayout(ReactionLayout, _ReactionNodeMixin):
    """Class for transport layouts"""

    _reaction_node_text: typing.ClassVar[str | None] = None
    end_arrowhead_bar_height: float = 8.0
    end_arrowhead_fill: NoneValueType | Color | None = black
    end_arrowhead_filter: NoneValueType | Filter | None = None
    end_arrowhead_sep: float = 5.0
    end_arrowhead_stroke: NoneValueType | Color | None = black
    end_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    end_arrowhead_triangle_height: float = 8.0
    end_arrowhead_triangle_width: float = 15.0
    end_shorten: float = 2.0
    start_arrowhead_bar_height: float = 8.0
    start_arrowhead_fill: NoneValueType | Color | None = black
    start_arrowhead_filter: NoneValueType | Filter | None = None
    start_arrowhead_sep: float = 4.0
    start_arrowhead_stroke: NoneValueType | Color | None = black
    start_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    start_arrowhead_triangle_height: float = 8.0
    start_arrowhead_triangle_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            actions = [
                MoveTo(Point(0, -self.start_arrowhead_bar_height / 2)),
                LineTo(Point(0, self.start_arrowhead_bar_height / 2)),
            ]
            bar = Path(actions=actions)
            actions = [
                MoveTo(Point(0, 0)),
                LineTo(Point(-self.start_arrowhead_sep, 0)),
            ]
            sep = Path(actions=actions)
            triangle = MetaShapesTriangle(
                position=Point(
                    -self.start_arrowhead_sep - self.start_arrowhead_triangle_width / 2,
                    0,
                ),
                width=self.start_arrowhead_triangle_width,
                height=self.start_arrowhead_triangle_height,
                direction=Direction.LEFT,
            )
            return [bar, sep] + triangle.drawing_elements()
        return []

    def _end_arrowhead_border_drawing_elements(self):
        actions = [
            MoveTo(Point(0, -self.end_arrowhead_bar_height / 2)),
            LineTo(Point(0, self.end_arrowhead_bar_height / 2)),
        ]
        bar = Path(actions=actions)
        actions = [
            MoveTo(Point(0, 0)),
            LineTo(Point(self.end_arrowhead_sep, 0)),
        ]
        sep = Path(actions=actions)
        triangle = MetaShapesTriangle(
            position=Point(
                self.end_arrowhead_sep + self.end_arrowhead_triangle_width / 2,
                0,
            ),
            width=self.end_arrowhead_triangle_width,
            height=self.end_arrowhead_triangle_height,
            direction=Direction.RIGHT,
        )
        return [bar, sep] + triangle.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class HeterodimerAssociationLayout(ReactionLayout, _ReactionNodeMixin):
    """Class for heterodimer association layouts"""

    _reaction_node_text: typing.ClassVar[str | None] = None
    end_arrowhead_fill: NoneValueType | Color | None = black
    end_arrowhead_filter: NoneValueType | Filter | None = None
    end_arrowhead_height: float = 8.0
    end_arrowhead_stroke: NoneValueType | Color | None = black
    end_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    end_arrowhead_width: float = 15.0
    end_shorten: float = 2.0
    start_arrowhead_fill: NoneValueType | Color | None = black
    start_arrowhead_filter: NoneValueType | Filter | None = None
    start_arrowhead_height: float = 6.0
    start_arrowhead_stroke: NoneValueType | Color | None = black
    start_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    start_arrowhead_width: float = 6.0
    start_shorten: float = 2.0

    def _end_arrowhead_border_drawing_elements(self):
        return DoubleTriangle._end_arrowhead_border_drawing_elements(self)

    def _start_arrowhead_border_drawing_elements(self):
        shape = MetaShapesEllipse(
            position=Point(0, 0),
            width=self.start_arrowhead_width,
            height=self.start_arrowhead_height,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class DissociationLayout(ReactionLayout, _ReactionNodeMixin):
    """Class for dissociation layouts"""

    _reaction_node_text: typing.ClassVar[str | None] = None
    end_arrowhead_fill: NoneValueType | Color | None = white
    end_arrowhead_filter: NoneValueType | Filter | None = None
    end_arrowhead_height: float = 10.0
    end_arrowhead_stroke: NoneValueType | Color | None = black
    end_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    end_arrowhead_sep: float = 2.0
    end_arrowhead_width: float = 10.0
    end_shorten: float = 2.0
    start_arrowhead_fill: NoneValueType | Color | None = black
    start_arrowhead_filter: NoneValueType | Filter | None = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: NoneValueType | Color | None = black
    start_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            return DoubleTriangle._start_arrowhead_border_drawing_elements(self)
        return []

    def _end_arrowhead_border_drawing_elements(self):
        outer_circle = MetaShapesEllipse(
            position=Point(0, 0),
            width=self.end_arrowhead_width,
            height=self.end_arrowhead_height,
        )
        inner_circle = MetaShapesEllipse(
            position=Point(0, 0),
            width=self.end_arrowhead_width - 2 * self.end_arrowhead_sep,
            height=self.end_arrowhead_height - 2 * self.end_arrowhead_sep,
        )
        return outer_circle.drawing_elements() + inner_circle.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class TruncationLayout(ReactionLayout, _ReactionNodeMixin):
    """Class for truncation layouts"""

    _font_size_func: typing.ClassVar[typing.Callable | None] = (
        lambda obj: obj.reaction_node_width / 1.1
    )
    _font_weight: typing.ClassVar[FontWeight | float] = FontWeight.BOLD
    _reaction_node_text: typing.ClassVar[str | None] = "N"
    end_arrowhead_fill: NoneValueType | Color | None = white
    end_arrowhead_filter: NoneValueType | Filter | None = None
    end_arrowhead_height: float = 10.0
    end_arrowhead_stroke: NoneValueType | Color | None = black
    end_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    end_arrowhead_sep: float = 2.0
    end_arrowhead_width: float = 10.0
    end_shorten: float = 2.0
    start_arrowhead_fill: NoneValueType | Color | None = black
    start_arrowhead_filter: NoneValueType | Filter | None = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: NoneValueType | Color | None = black
    start_arrowhead_stroke_dasharray: NoneValueType | tuple[float] | None = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: NoneValueType | tuple[Transformation] | None = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        return []

    def _end_arrowhead_border_drawing_elements(self):
        return []


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndGateLayout(
    _SimpleNodeMixin,
    _TextMixin,
    CellDesignerNode,
):
    """Class for and gate layouts"""

    _font_family: typing.ClassVar[str] = DEFAULT_FONT_FAMILY
    _font_fill: typing.ClassVar[Color | NoneValueType] = black
    _font_stroke: typing.ClassVar[Color | NoneValueType] = NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width
    _text: typing.ClassVar[str] = "&"
    width: float = 15.0
    height: float = 15.0

    def _make_shape(self):
        return MetaShapesEllipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrGateLayout(
    _SimpleNodeMixin,
    _TextMixin,
    CellDesignerNode,
):
    """Class for or gate layouts"""

    _font_family: typing.ClassVar[str] = DEFAULT_FONT_FAMILY
    _font_fill: typing.ClassVar[Color | NoneValueType] = black
    _font_stroke: typing.ClassVar[Color | NoneValueType] = NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    _text: typing.ClassVar[str] = "|"
    width: float = 15.0
    height: float = 15.0

    def _make_shape(self):
        return MetaShapesEllipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotGateLayout(
    _SimpleNodeMixin,
    _TextMixin,
    CellDesignerNode,
):
    """Class for not gate layouts"""

    _font_family: typing.ClassVar[str] = DEFAULT_FONT_FAMILY
    _font_fill: typing.ClassVar[Color | NoneValueType] = black
    _font_stroke: typing.ClassVar[Color | NoneValueType] = NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    _text: typing.ClassVar[str] = "!"
    width: float = 15.0
    height: float = 15.0

    def _make_shape(self):
        return MetaShapesEllipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownGateLayout(
    _SimpleNodeMixin,
    _TextMixin,
    CellDesignerNode,
):
    """Class for unknown gate layouts"""

    _font_family: typing.ClassVar[str] = DEFAULT_FONT_FAMILY
    _font_fill: typing.ClassVar[Color | NoneValueType] = black
    _font_stroke: typing.ClassVar[Color | NoneValueType] = NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    _text: typing.ClassVar[str] = "?"
    width: float = 15.0
    height: float = 15.0

    def _make_shape(self):
        return MetaShapesEllipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(CellDesignerSingleHeadedArc):
    """Class for logic arc layouts"""

    def _arrowhead_border_drawing_elements(self):
        return PolyLine._arrowhead_border_drawing_elements(self)


__all__ = [
    "CellDesignerLayout",
    "GenericProteinLayout",
    "GenericProteinActiveLayout",
    "IonChannelLayout",
    "IonChannelActiveLayout",
    "ComplexLayout",
    "ComplexActiveLayout",
    "SimpleMoleculeLayout",
    "SimpleMoleculeActiveLayout",
    "IonLayout",
    "IonActiveLayout",
    "UnknownLayout",
    "UnknownActiveLayout",
    "DegradedLayout",
    "DegradedActiveLayout",
    "GeneLayout",
    "GeneActiveLayout",
    "PhenotypeLayout",
    "PhenotypeActiveLayout",
    "RNALayout",
    "RNAActiveLayout",
    "AntisenseRNALayout",
    "AntisenseRNAActiveLayout",
    "TruncatedProteinLayout",
    "TruncatedProteinActiveLayout",
    "ReceptorLayout",
    "ReceptorActiveLayout",
    "DrugLayout",
    "DrugActiveLayout",
    "StructuralStateLayout",
    "ModificationLayout",
    "OvalCompartmentLayout",
    "RectangleCompartmentLayout",
    "CompartmentCorner",
    "CompartmentSide",
    "CornerCompartmentLayout",
    "LineCompartmentLayout",
    "ConsumptionLayout",
    "ProductionLayout",
    "CatalysisLayout",
    "UnknownCatalysisLayout",
    "InhibitionLayout",
    "UnknownInhibitionLayout",
    "PhysicalStimulationLayout",
    "UnknownPhysicalStimulationLayout",
    "ModulationLayout",
    "UnknownModulationLayout",
    "PositiveInfluenceLayout",
    "UnknownPositiveInfluenceLayout",
    "TriggeringLayout",
    "UnknownTriggeringLayout",
    "ReactionLayout",
    "StateTransitionLayout",
    "KnownTransitionOmittedLayout",
    "UnknownTransitionLayout",
    "TranscriptionLayout",
    "TranslationLayout",
    "TransportLayout",
    "HeterodimerAssociationLayout",
    "DissociationLayout",
    "TruncationLayout",
    "AndGateLayout",
    "OrGateLayout",
    "NotGateLayout",
    "UnknownGateLayout",
    "LogicArcLayout",
]
