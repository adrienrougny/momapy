from dataclasses import dataclass

import momapy.core
import momapy.drawing
import momapy.geometry


@dataclass(frozen=True)
class PolyLine(momapy.core.ArcLayoutElement):

    def arrowtip_drawing_element(self):
        return None

    def arrowtip_length(self):
        return 0.0

@dataclass(frozen=True)
class Arrow(momapy.core.ArcLayoutElement):
    width: float = 10
    height: float = 10

    def arrowtip_drawing_element(self):
        path = momapy.drawing.Path(stroke=self.stroke,
                    stroke_width=self.stroke_width, fill=self.fill)
        path += momapy.drawing.move_to(momapy.geometry.Point(0, 0)) + \
            momapy.drawing.line_to(momapy.geometry.Point(0, -self.height / 2)) + \
            momapy.drawing.line_to(momapy.geometry.Point(self.width, 0)) + \
            momapy.drawing.line_to(momapy.geometry.Point(0, self.height / 2)) + \
            momapy.drawing.close()
        return path

    def arrowtip_length(self):
        return self.width
