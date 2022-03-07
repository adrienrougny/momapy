from dataclasses import dataclass

from momapy.core import ArcLayoutElement
from momapy.drawing import Path, move_to, line_to, close
from momapy.geometry import Point


@dataclass(frozen=True)
class PolyLine(ArcLayoutElement):

    def arrowtip_drawing_element(self):
        return None

    def arrowtip_length(self):
        return 0.0

@dataclass(frozen=True)
class Arrow(ArcLayoutElement):
    width: float = 10
    height: float = 10

    def arrowtip_drawing_element(self):
        path = Path(stroke=self.stroke,
                    stroke_width=self.stroke_width, fill=self.fill)
        path += move_to(Point(0, 0)) + \
            line_to(Point(0, -self.height / 2)) + \
            line_to(Point(self.width, 0)) + \
            line_to(Point(0, self.height / 2)) + \
            close()
        return path

    def arrowtip_length(self):
        return self.width
