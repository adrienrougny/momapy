from dataclasses import dataclass

import momapy.core
import momapy.nodes
import momapy.drawing
import momapy.geometry


@dataclass(frozen=True, kw_only=True)
class PolyLine(momapy.core.SingleHeadedArcLayout):
    def arrowhead_drawing_elements(self):
        return []


@dataclass(frozen=True, kw_only=True)
class Triangle(momapy.core.SingleHeadedArcLayout):
    arrowhead_width: float
    arrowhead_height: float

    def arrowhead_drawing_elements(self):
        triangle = momapy.nodes.Trianlge(
            position=momapy.geometry.Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_height,
            height=self.arrowhead_width,
            direction=momapy.core.Direction.RIGHT,
        )
        return triangle.border_drawing_elements()


@dataclass(frozen=True, kw_only=True)
class ReversedTriangle(momapy.core.SingleHeadedArcLayout):
    arrowhead_width: float
    arrowhead_height: float

    def arrowhead_drawing_elements(self):
        triangle = momapy.nodes.Trianlge(
            position=momapy.geometry.Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_height,
            height=self.arrowhead_width,
            direction=momapy.core.Direction.LEFT,
        )
        return triangle.border_drawing_elements()


@dataclass(frozen=True, kw_only=True)
class Rectangle(momapy.core.SingleHeadedArcLayout):
    arrowhead_width: float
    arrowhead_height: float

    def arrowhead_drawing_elements(self):
        rectangle = momapy.nodes.Rectangle(
            position=momapy.geometry.Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
        )
        return rectangle.border_drawing_elements()


@dataclass(frozen=True, kw_only=True)
class Ellipse(momapy.core.SingleHeadedArcLayout):
    arrowhead_width: float
    arrowhead_height: float

    def arrowhead_drawing_elements(self):
        ellipse = momapy.nodes.Ellipse(
            position=momapy.geometry.Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
        )
        return ellipse.border_drawing_elements()


@dataclass(frozen=True, kw_only=True)
class Diamond(momapy.core.SingleHeadedArcLayout):
    arrowhead_width: float
    arrowhead_height: float

    def arrowhead_drawing_elements(self):
        diamond = momapy.nodes.Diamond(
            position=momapy.geometry.Point(self.arrowhead_width / 2, 0),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
        )
        return diamond.border_drawing_elements()


@dataclass(frozen=True, kw_only=True)
class Bar(momapy.core.SingleHeadedArcLayout):
    arrowhead_width: float
    arrowhead_height: float

    def arrowhead_drawing_elements(self):
        bar = momapy.drawing.Rectangle(
            stroke_width=0.0,
            point=momapy.geometry.Point(0, -self.arrowhead_height / 2),
            width=self.arrowhead_width,
            height=self.arrowhead_height,
            rx=0.0,
            ry=0.0,
        )
        return [bar]


@dataclass(frozen=True, kw_only=True)
class DoubleTriangle(momapy.core.DoubleHeadedArcLayout):
    start_arrowhead_width: float
    start_arrowhead_height: float
    end_arrowhead_width: float
    end_arrowhead_height: float

    def start_arrowhead_drawing_elements(self):
        triangle = momapy.nodes.Trianlge(
            position=momapy.geometry.Point(self.start_arrowhead_width / 2, 0),
            width=self.start_arrowhead_height,
            height=self.start_arrowhead_width,
            direction=momapy.core.Direction.RIGHT,
        )
        return triangle.border_drawing_elements()

    def end_arrowhead_drawing_elements(self):
        triangle = momapy.nodes.Trianlge(
            position=momapy.geometry.Point(self.end_arrowhead_width / 2, 0),
            width=self.end_arrowhead_height,
            height=self.end_arrowhead_width,
            direction=momapy.core.Direction.RIGHT,
        )
        return triangle.border_drawing_elements()
