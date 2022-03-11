from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from frozendict import frozendict
from typing import Optional
from uuid import uuid4
from enum import Enum

import momapy.drawing
import momapy.geometry
import momapy.coloring

class Direction(Enum):
    HORIZONTAL = 1
    VERTICAL = 2


@dataclass(frozen=True)
class MapElement(ABC):
    id: str = field(hash=False, compare=False, default_factory=uuid4)


@dataclass(frozen=True)
class ModelElement(MapElement):
    pass


@dataclass(frozen=True)
class LayoutElement(MapElement):

    @abstractmethod
    def bbox(self) -> momapy.geometry.Bbox:
        pass

    @abstractmethod
    def drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        pass

@dataclass(frozen=True)
class NodeLayoutElementLabel(LayoutElement):
    text: Optional[str] = None
    position: Optional[momapy.geometry.Point] = None
    width: Optional[float] = None
    height: Optional[float] = None
    font_description: Optional[str] = "Arial 14"
    font_color: Optional[momapy.coloring.Color] = momapy.coloring.colors.black

    @property
    def x(self) -> float:
        return self.position.x

    @property
    def y(self) -> float:
        return self.position.y

    def size(self) -> tuple[float, float]:
        return (self.width, self.height)

    def bbox(self) -> momapy.geometry.Bbox:
        return Bbox(self.position, self.width, self.height)

    def drawing_elements(self):
        text = Text(
            text=self.text,
            position=self.position,
            width=self.width,
            height=self.height,
            font_description=self.font_description,
            font_color=self.font_color)
        return [text]


@dataclass(frozen=True)
class GroupLayoutElement(LayoutElement):
    transform: Optional[tuple[momapy.drawing.Transformation]] = None
    layout_elements: tuple[LayoutElement] = field(default_factory=tuple)

    @abstractmethod
    def self_bbox(self) -> momapy.geometry.Bbox:
        pass

    @abstractmethod
    def self_drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        pass

    def drawing_elements(self):
        self_drawing_elements = self.self_drawing_elements()
        if self_drawing_elements is not None:
            drawing_elements = self_drawing_elements
        else:
            drawing_elements = []
        for layout_element in self.layout_elements:
            sub_drawing_elements = layout_element.drawing_elements()
            if sub_drawing_elements is not None:
                drawing_elements += sub_drawing_elements
        group = momapy.drawing.Group(
            transform=self.transform,
            elements=drawing_elements)
        return [group]


@dataclass(frozen=True)
class NodeLayoutElement(GroupLayoutElement):
    position: Optional[momapy.geometry.Point] = None
    width: Optional[float] = None
    height: Optional[float] = None
    label: Optional[NodeLayoutElementLabel] = None
    stroke_width: float = 1
    stroke: Optional[momapy.coloring.Color] = momapy.coloring.colors.black
    fill: Optional[momapy.coloring.Color] = momapy.coloring.colors.white

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    def self_bbox(self):
        return momapy.geometry.Bbox(self.position, self.width, self.height)

    def bbox(self):
        import momapy.positioning
        elements = [self.self_bbox()]
        if self.label is not None:
            elements.append(self.label)
        elements += self.layout_elements
        return momapy.positioning.fit(elements)

    @abstractmethod
    def background_path(self) -> Optional[momapy.drawing.Path]:
        pass

    @abstractmethod
    def foreground_path(self) -> Optional[momapy.drawing.Path]:
        pass

    def self_drawing_elements(self):
        drawing_elements = []
        background_path = self.background_path()
        if background_path is not None:
            drawing_elements += [background_path]
        if self.label is not None:
            label_drawing_elements = self.label.drawing_elements()
            if label_drawing_elements is not None:
                drawing_elements += label_drawing_elements
        foreground_path = self.foreground_path()
        if foreground_path is not None:
            drawing_elements += [foreground_path]
        return drawing_elements

    @abstractmethod
    def angle(self, angle, unit="degrees") -> momapy.geometry.Point:
        pass

    def size(self):
        return (self.width, self.height)

    @abstractmethod
    def east(self) -> momapy.geometry.Point:
        pass

    @abstractmethod
    def north_east(self) -> momapy.geometry.Point:
        pass

    @abstractmethod
    def north(self) -> momapy.geometry.Point:
        pass

    @abstractmethod
    def north_west(self) -> momapy.geometry.Point:
        pass

    @abstractmethod
    def west(self) -> momapy.geometry.Point:
        pass

    @abstractmethod
    def south_west(self) -> momapy.geometry.Point:
        pass

    @abstractmethod
    def south(self) -> momapy.geometry.Point:
        pass

    @abstractmethod
    def south_east(self) -> momapy.geometry.Point:
        pass

    @abstractmethod
    def center(self) -> momapy.geometry.Point:
        pass

    def border(self, point) -> momapy.geometry.Point:
        angle = momapy.geometry.get_angle_of_line(
            momapy.geometry.Line(self.center(), point))
        return self.angle(-angle, unit="radians")


@dataclass(frozen=True)
class ArcLayoutElement(GroupLayoutElement):
    points: tuple[momapy.geometry.Point] = field(default_factory=tuple)
    source: Optional[LayoutElement] = None
    target: Optional[LayoutElement] = None
    stroke_width: float = 1
    stroke: Optional[momapy.coloring.Color] = momapy.coloring.colors.black
    fill: Optional[momapy.coloring.Color] = momapy.coloring.colors.white

    def self_bbox(self):
        import momapy.positioning
        return momapy.positioning.fit(self.points)

    def bbox(self):
        import momapy.positioning
        elements = [self.self_bbox()]
        if self.source is not None:
            elements.append(self.source)
        if self.target is not None:
            elements.append(self.target)
        elements += self.layout_elements
        return momapy.positioning.fit(elements)

    @abstractmethod
    def arrowtip_drawing_element(self) -> momapy.drawing.DrawingElement:
        pass

    @abstractmethod
    def arrowtip_length(self) -> float:
        pass

    def segments(self) -> list[momapy.geometry.Segment]:
        segments = []
        for i in range(len(self.points))[1:]:
            segments.append(momapy.geometry.Segment(self.points[i - 1], self.points[i]))
        return segments

    def length(self):
        return sum([segment.length() for segment in self.segments()])

    def _get_segment_at_fraction(self, fraction):
        total_length = self.length()
        current_length = 0
        for segment in self.segments():
            current_length += segment.length()
            current_fraction = current_length / total_length
            if current_fraction >= fraction:
                return segment
        return segment


    def fraction(self, fraction) -> tuple[momapy.geometry.Point, float]:
        if fraction < 0 or fraction > 1:
            raise ValueError("fraction must belong to [0, 1]")
        segment_at_fraction = self._get_segment_at_fraction(fraction)
        angle = momapy.geometry.get_angle_of_line(segment_at_fraction)
        current_length = 0
        for segment in self.segments():
            if segment == segment_at_fraction:
                fraction_on_segment = (self.length() * fraction \
                                       - current_length) / segment.length()
                return momapy.geometry.get_position_at_fraction(
                    segment, fraction_on_segment), angle
            else:
                current_length += segment.length()
        return segment.p2, angle


    def self_drawing_elements(self):
        drawing_elements = []
        if self.source is not None:
            source_drawing_elements = self.source.drawing_elements()
            if source_drawing_elements is not None:
                drawing_elements += source_drawing_elements
        if self.target is not None:
            target_drawing_elements = self.target.drawing_elements()
            if target_drawing_elements is not None:
                drawing_elements += target_drawing_elements
        drawing_elements += [self._get_path_from_points()]
        arrowtip_drawing_element = self.arrowtip_drawing_element()
        if arrowtip_drawing_element is not None:
            transform = tuple([
                momapy.drawing.translate(*self._get_arrowtip_start_point()),
                momapy.drawing.rotate(self._get_arrowtip_rotation_angle())])
            arrowtip_drawing_element = replace(
                arrowtip_drawing_element, transform=transform)
            drawing_elements.append(arrowtip_drawing_element)
        return drawing_elements

    def _get_path_from_points(self) -> momapy.drawing.Path:
        path = momapy.drawing.Path(stroke=self.stroke,
                    stroke_width=self.stroke_width, fill=None)
        path += momapy.drawing.move_to(self.points[0])
        for segment in self.segments()[:-1]:
            path += momapy.drawing.line_to(segment.p2)
        if self.arrowtip_drawing_element() is not None:
            path += momapy.drawing.line_to(self._get_arrowtip_start_point())
        else:
            path += momapy.drawing.line_to(self.segments()[-1].p2)
        return path

    def _get_arrowtip_start_point(self) -> momapy.geometry.Point:
        last_segment = self.segments()[-1]
        fraction = 1 - self.arrowtip_length() / last_segment.length()
        p = momapy.geometry.get_position_at_fraction(last_segment, fraction)
        return p

    def _get_arrowtip_rotation_angle(self) -> float:
        last_segment = self.segments()[-1]
        angle = momapy.geometry.get_angle_of_line(last_segment)
        return angle


@dataclass(frozen=True)
class Model(MapElement):
    pass


@dataclass(frozen=True)
class Layout(GroupLayoutElement):
    width: Optional[float] = None
    height: Optional[float] = None
    stroke_width: float = 1
    stroke: Optional[momapy.coloring.Color] = None
    fill: Optional[momapy.coloring.Color] = None

    def self_bbox(self):
        return momapy.geometry.Bbox(momapy.geometry.Point(self.width / 2, self.height / 2),
                    width=self.width, height=self.height)

    def self_drawing_elements(self):
        path = momapy.drawing.Path(stroke=self.stroke, fill=self.fill,
                    stroke_width=self.stroke_width)
        path += momapy.drawing.move_to(self.bbox().north_west()) + \
                momapy.drawing.line_to(self.bbox().north_east()) + \
                momapy.drawing.line_to(self.bbox().south_east()) + \
                momapy.drawing.line_to(self.bbox().south_west()) + \
                momapy.drawing.close()
        return [path]

    def bbox(self):
        return self.self_bbox()

class ModelLayoutMapping(frozendict):
    pass


@dataclass(frozen=True)
class Map(MapElement):
    model: Optional[Model] = None
    layout: Optional[Layout] = None
    model_layout_mapping: ModelLayoutMapping = field(
        default_factory=ModelLayoutMapping)

@dataclass(frozen=True)
class PhantomLayoutElement(LayoutElement):
    layout_element: Optional[LayoutElement] = None

    def bbox(self):
        return self.layout_element.bbox()

    def drawing_elements(self):
        return []

    def __getattr__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            if self.layout_element is not None:
                return getattr(self.layout_element, name)
            else:
                raise AttributeError
