from dataclasses import dataclass

import momapy.core
import momapy.drawing
import momapy.geometry


@dataclass(frozen=True, kw_only=True)
class PolyLine(momapy.core.ArcLayout):
    def arrowhead_drawing_element(self):
        return None

    def arrowhead_length(self):
        return 0.0

    def arrowhead_bbox(self):
        return momapy.geometry.Bbox(self.arrowhead_tip(), 0, 0)


@dataclass(frozen=True, kw_only=True)
class Arrow(momapy.core.ArcLayout):
    width: float = 10.0
    height: float = 10.0

    def arrowhead_drawing_element(self):
        path = momapy.drawing.Path(
            stroke=self.arrowhead_stroke,
            stroke_width=self.arrowhead_stroke_width,
            stroke_dasharray=self.arrowhead_stroke_dasharray,
            stroke_dashoffset=self.arrowhead_stroke_dashoffset,
            fill=self.arrowhead_fill,
        )
        path += (
            momapy.drawing.move_to(self.arrowhead_base())
            + momapy.drawing.line_to(
                self.arrowhead_base() - (0, self.height / 2)
            )
            + momapy.drawing.line_to(self.arrowhead_base() + (self.width, 0))
            + momapy.drawing.line_to(
                self.arrowhead_base() + (0, self.height / 2)
            )
            + momapy.drawing.close()
        )
        return path

    def arrowhead_length(self):
        return self.width

    # to code
    def arrowhead_bbox(self):
        return momapy.geometry.Bbox(self.arrowhead_tip(), 0, 0)


@dataclass(frozen=True, kw_only=True)
class Circle(momapy.core.ArcLayout):
    def arrowhead_drawing_element(self):
        ellipse = momapy.drawing.Ellipse(
            stroke=self.arrowhead_stroke,
            stroke_width=self.arrowhead_stroke_width,
            stroke_dasharray=self.arrowhead_stroke_dasharray,
            stroke_dashoffset=self.arrowhead_stroke_dashoffset,
            fill=self.arrowhead_fill,
            point=self.arrowhead_base() + (self.width / 2, 0),
            rx=self.width / 2,
            ry=self.height / 2,
        )
        return ellipse

    def arrowhead_length(self):
        return self.width

    # to code
    def arrowhead_bbox(self):
        return momapy.geometry.Bbox(self.arrowhead_tip(), 0, 0)


@dataclass(frozen=True, kw_only=True)
class Bar(momapy.core.ArcLayout):
    def arrowhead_drawing_element(self):
        path = momapy.drawing.Path(
            stroke=self.arrowhead_stroke,
            stroke_width=self.arrowhead_stroke_width,
            stroke_dasharray=self.arrowhead_stroke_dasharray,
            stroke_dashoffset=self.arrowhead_stroke_dashoffset,
            fill=self.arrowhead_fill,
        )
        path += momapy.drawing.move_to(
            self.arrowhead_base() + (self.width / 2, self.height / 2)
        ) + momapy.drawing.line_to(
            self.arrowhead_base() + (self.width / 2, -self.height / 2)
        )
        return path

    def arrowhead_length(self):
        return self.width

    # to code
    def arrowhead_bbox(self):
        return momapy.geometry.Bbox(self.arrowhead_tip(), 0, 0)


@dataclass(frozen=True, kw_only=True)
class BarArrow(momapy.core.ArcLayout):
    bar_width: float
    bar_height: float
    sep: float

    def arrowhead_drawing_element(self):
        bar = momapy.drawing.Path(stroke_width=self.bar_width)
        bar += momapy.drawing.move_to(
            self.arrowhead_base() + (self.bar_width / 2, self.bar_height / 2)
        ) + momapy.drawing.line_to(
            self.arrowhead_base() + (self.bar_width / 2, -self.bar_height / 2)
        )
        sep = momapy.drawing.Path()
        sep += momapy.drawing.move_to(
            self.arrowhead_base() + (self.bar_width, 0)
        ) + momapy.drawing.line_to(
            self.arrowhead_base() + (self.bar_width + self.sep, 0)
        )
        arrow = momapy.drawing.Path()
        arrow += (
            momapy.drawing.move_to(
                self.arrowhead_base() + (self.bar_width + self.sep, 0)
            )
            + momapy.drawing.line_to(
                self.arrowhead_base()
                + (self.bar_width + self.sep, -self.height / 2)
            )
            + momapy.drawing.line_to(
                self.arrowhead_base()
                + (self.bar_width + self.sep + self.width, 0)
            )
            + momapy.drawing.line_to(
                self.arrowhead_base()
                + (self.bar_width + self.sep, self.height / 2)
            )
            + momapy.drawing.close()
        )
        elements = (bar, sep, arrow)
        group = momapy.drawing.Group(
            stroke=self.arrowhead_stroke,
            stroke_width=self.arrowhead_stroke_width,
            stroke_dasharray=self.arrowhead_stroke_dasharray,
            stroke_dashoffset=self.arrowhead_stroke_dashoffset,
            fill=self.arrowhead_fill,
            elements=elements,
        )
        return group

    def arrowhead_length(self):
        return self.bar_width + self.sep + self.width

    # to code
    def arrowhead_bbox(self):
        return momapy.geometry.Bbox(self.arrowhead_tip(), 0, 0)


@dataclass(frozen=True, kw_only=True)
class Diamond(momapy.core.ArcLayout):
    def arrowhead_drawing_element(self):
        path = momapy.drawing.Path(
            stroke=self.arrowhead_stroke,
            stroke_width=self.arrowhead_stroke_width,
            stroke_dasharray=self.arrowhead_stroke_dasharray,
            stroke_dashoffset=self.arrowhead_stroke_dashoffset,
            fill=self.arrowhead_fill,
        )
        path += (
            momapy.drawing.move_to(self.arrowhead_base())
            + momapy.drawing.line_to(
                self.arrowhead_base() + (self.width / 2, -self.height / 2)
            )
            + momapy.drawing.line_to(self.arrowhead_base() + (self.width, 0))
            + momapy.drawing.line_to(
                self.arrowhead_base() + (self.width / 2, self.height / 2)
            )
            + momapy.drawing.close()
        )
        return path

    def arrowhead_length(self):
        return self.width

    # to code
    def arrowhead_bbox(self):
        return momapy.geometry.Bbox(self.arrowhead_tip(), 0, 0)
