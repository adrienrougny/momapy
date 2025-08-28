"""Classes for common node types"""

import dataclasses

import momapy.core
import momapy.meta.shapes


@dataclasses.dataclass(frozen=True, kw_only=True)
class Rectangle(momapy.core.Node):
    """Class for rectangle nodes"""

    top_left_rx: float = 0.0
    top_left_ry: float = 0.0
    top_left_rounded_or_cut: str = "rounded"
    top_right_rx: float = 0.0
    top_right_ry: float = 0.0
    top_right_rounded_or_cut: str = "rounded"
    bottom_right_rx: float = 0.0
    bottom_right_ry: float = 0.0
    bottom_right_rounded_or_cut: str = "rounded"
    bottom_left_rx: float = 0.0
    bottom_left_ry: float = 0.0
    bottom_left_rounded_or_cut: str = "rounded"

    def _border_drawing_elements(self):
        shape = momapy.meta.shapes.Rectangle(
            position=self.position,
            width=self.width,
            height=self.height,
            top_left_rx=self.top_left_rx,
            top_left_ry=self.top_left_ry,
            top_left_rounded_or_cut=self.top_left_rounded_or_cut,
            top_right_rx=self.top_right_rx,
            top_right_ry=self.top_right_ry,
            top_right_rounded_or_cut=self.top_right_rounded_or_cut,
            bottom_left_rx=self.bottom_left_rx,
            bottom_left_ry=self.bottom_left_ry,
            bottom_left_rounded_or_cut=self.bottom_left_rounded_or_cut,
            bottom_right_rx=self.bottom_right_rx,
            bottom_right_ry=self.bottom_right_ry,
            bottom_right_rounded_or_cut=self.bottom_right_rounded_or_cut,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Ellipse(momapy.core.Node):
    """Class for ellipse nodes"""

    def _border_drawing_elements(self):
        shape = momapy.meta.shapes.Ellipse(
            position=self.position,
            width=self.width,
            height=self.height,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Stadium(momapy.core.Node):
    """Class for stadium nodes"""

    def _border_drawing_elements(self):
        shape = momapy.meta.shapes.Stadium(
            position=self.position,
            width=self.width,
            height=self.height,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Hexagon(momapy.core.Node):
    """Class for hexagon nodes"""

    left_angle: float = 60.0
    right_angle: float = 60.0

    def _border_drawing_elements(self):
        shape = momapy.meta.shapes.Hexagon(
            position=self.position,
            width=self.width,
            height=self.height,
            left_angle=self.left_angle,
            right_angle=self.right_angle,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class TurnedHexagon(momapy.core.Node):
    """Class for hexagon turned by 90 degrees nodes"""

    top_angle: float = 80.0
    bottom_angle: float = 80.0

    def _border_drawing_elements(self):
        shape = momapy.meta.shapes.TurnedHexagon(
            position=self.position,
            width=self.width,
            height=self.height,
            top_angle=self.top_angle,
            bottom_angle=self.bottom_angle,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Parallelogram(momapy.core.Node):
    """Class for parallelogram nodes"""

    angle: float = 60.0

    def _border_drawing_elements(self):
        shape = momapy.meta.shapes.Parallelogram(
            position=self.position,
            width=self.width,
            height=self.height,
            angle=self.angle,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class CrossPoint(momapy.core.Node):
    """Class for cross point nodes"""

    def _border_drawing_elements(self):
        shape = momapy.meta.shapes.CrossPoint(
            position=self.position,
            width=self.width,
            height=self.height,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Triangle(momapy.core.Node):
    """Class for triangle nodes"""

    direction: momapy.core.Direction = momapy.core.Direction.RIGHT

    def _border_drawing_elements(self):
        shape = momapy.meta.shapes.Triangle(
            position=self.position,
            width=self.width,
            height=self.height,
            direction=self.direction,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Diamond(momapy.core.Node):
    """Class for diamond nodes"""

    def _border_drawing_elements(self):
        shape = momapy.meta.shapes.Diamond(
            position=self.position,
            width=self.width,
            height=self.height,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Bar(momapy.core.Node):
    """Class for bar nodes"""

    def _border_drawing_elements(self):
        shape = momapy.meta.shapes.Bar(
            position=self.position,
            height=self.height,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class ArcBarb(momapy.core.Node):
    """Class for arc barb nodes"""

    direction: momapy.core.Direction = momapy.core.Direction.RIGHT

    def _border_drawing_elements(self):
        shape = momapy.meta.shapes.ArcBarb(
            position=self.position,
            width=self.width,
            height=self.height,
            direction=self.direction,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class StraightBarb(momapy.core.Node):
    """Class for straight barb nodes"""

    direction: momapy.core.Direction = momapy.core.Direction.RIGHT

    def _border_drawing_elements(self):
        shape = momapy.meta.shapes.StraightBarb(
            position=self.position,
            width=self.width,
            height=self.height,
            direction=self.direction,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class To(momapy.core.Node):
    """Class for to nodes"""

    direction: momapy.core.Direction = momapy.core.Direction.RIGHT

    def _border_drawing_elements(self):
        shape = momapy.meta.shapes.To(
            position=self.position,
            width=self.width,
            height=self.height,
            direction=self.direction,
        )
        return shape.drawing_elements()
