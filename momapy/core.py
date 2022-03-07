from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from frozendict import frozendict
from typing import Optional
from uuid import uuid4
from enum import Enum

from momapy.drawing import move_to, line_to, close, rotate, translate, Text, Path, DrawingElement, Transformation, Group
from momapy.geometry import Point, Segment, get_position_at_fraction, get_angle_of_line, anchorpoint, Line, Bbox
from momapy.coloring import Color, colors


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
    def bbox(self) -> Bbox:
        pass

    @abstractmethod
    def drawing_elements(self) -> list[DrawingElement]:
        pass

@dataclass(frozen=True)
class NodeLayoutElementLabel(LayoutElement):
    text: Optional[str] = None
    position: Optional[Point] = None
    width: Optional[float] = None
    height: Optional[float] = None
    font_description: Optional[str] = "Arial 14"
    font_color: Optional[Color] = colors.black

    @property
    def x(self) -> float:
        return self.position.x

    @property
    def y(self) -> float:
        return self.position.y

    def size(self) -> tuple[float, float]:
        return (self.width, self.height)

    def bbox(self) -> Bbox:
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
    transform: Optional[tuple[Transformation]] = None
    layout_elements: tuple[LayoutElement] = field(default_factory=tuple)

    @abstractmethod
    def self_drawing_elements(self) -> list[DrawingElement]:
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
        group = Group(
            transform=self.transform,
            elements=drawing_elements)
        return [group]


@dataclass(frozen=True)
class NodeLayoutElement(GroupLayoutElement):
    position: Optional[Point] = None
    width: Optional[float] = None
    height: Optional[float] = None
    label: Optional[NodeLayoutElementLabel] = None
    stroke_width: float = 1
    stroke: Optional[Color] = colors.black
    fill: Optional[Color] = colors.white

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    def bbox(self):
        return Bbox(self.position, self.width, self.height)

    @abstractmethod
    def background_path(self) -> Optional[Path]:
        pass

    @abstractmethod
    def foreground_path(self) -> Optional[Path]:
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
    def angle(self, angle, unit="degrees") -> Point:
        pass

    def size(self):
        return (self.width, self.height)

    @abstractmethod
    def east(self) -> Point:
        pass

    @abstractmethod
    def north_east(self) -> Point:
        pass

    @abstractmethod
    def north(self) -> Point:
        pass

    @abstractmethod
    def north_west(self) -> Point:
        pass

    @abstractmethod
    def west(self) -> Point:
        pass

    @abstractmethod
    def south_west(self) -> Point:
        pass

    @abstractmethod
    def south(self) -> Point:
        pass

    @abstractmethod
    def south_east(self) -> Point:
        pass

    @abstractmethod
    def center(self) -> Point:
        pass

    def border(self, point) -> Point:
        angle = get_angle_of_line(Line(self.center(), point))
        return self.angle(-angle, unit="radians")


@dataclass(frozen=True)
class ArcLayoutElement(GroupLayoutElement):
    points: tuple[Point] = field(default_factory=tuple)
    source: Optional[LayoutElement] = None
    target: Optional[LayoutElement] = None
    stroke_width: float = 1
    stroke: Optional[Color] = colors.black
    fill: Optional[Color] = colors.white

    def bbox(self):
        from momapy.positioning import fit
        return fit(self.points)

    @abstractmethod
    def arrowtip_drawing_element(self) -> DrawingElement:
        pass

    @abstractmethod
    def arrowtip_length(self) -> float:
        pass

    def segments(self) -> list[Segment]:
        segments = []
        for i in range(len(self.points))[1:]:
            segments.append(Segment(self.points[i - 1], self.points[i]))
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


    def fraction(self, fraction) -> tuple[Point, float]:
        if fraction < 0 or fraction > 1:
            raise ValueError("fraction must belong to [0, 1]")
        segment_at_fraction = self._get_segment_at_fraction(fraction)
        angle = get_angle_of_line(segment_at_fraction)
        current_length = 0
        for segment in self.segments():
            if segment == segment_at_fraction:
                fraction_on_segment = (self.length() * fraction \
                                       - current_length) / segment.length()
                return get_position_at_fraction(segment, fraction_on_segment), angle
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
                translate(*self._get_arrowtip_start_point()),
                rotate(self._get_arrowtip_rotation_angle())])
            arrowtip_drawing_element = replace(
                arrowtip_drawing_element, transform=transform)
            drawing_elements.append(arrowtip_drawing_element)
        return drawing_elements

    def _get_path_from_points(self) -> Path:
        path = Path(stroke=self.stroke,
                    stroke_width=self.stroke_width, fill=None)
        path += move_to(self.points[0])
        for segment in self.segments()[:-1]:
            path += line_to(segment.p2)
        if self.arrowtip_drawing_element() is not None:
            path += line_to(self._get_arrowtip_start_point())
        else:
            path += line_to(self.segments()[-1].p2)
        return path

    def _get_arrowtip_start_point(self) -> Point:
        last_segment = self.segments()[-1]
        fraction = 1 - self.arrowtip_length() / last_segment.length()
        p = get_position_at_fraction(last_segment, fraction)
        return p

    def _get_arrowtip_rotation_angle(self) -> float:
        last_segment = self.segments()[-1]
        angle = get_angle_of_line(last_segment)
        return angle


@dataclass(frozen=True)
class Model(MapElement):
    pass


@dataclass(frozen=True)
class Layout(GroupLayoutElement):
    width: Optional[float] = None
    height: Optional[float] = None
    stroke_width: float = 1
    stroke: Optional[Color] = None
    fill: Optional[Color] = None

    def bbox(self):
        return Bbox(Point(self.width / 2, self.height / 2),
                    width=self.width, height=self.height)

    def self_drawing_elements(self):
        path = Path(stroke=self.stroke, fill=self.fill,
                    stroke_width=self.stroke_width)
        path += move_to(self.bbox().north_west()) + \
                line_to(self.bbox().north_east()) + \
                line_to(self.bbox().south_east()) + \
                line_to(self.bbox().south_west()) + \
                close()
        return [path]

class ModelLayoutMapping(frozendict):
    pass


@dataclass(frozen=True)
class Map(MapElement):
    model: Optional[Model] = None
    layout: Optional[Layout] = None
    model_layout_mapping: ModelLayoutMapping = field(
        default_factory=ModelLayoutMapping)

@dataclass(frozen=True)
class LayoutElementReference(object):
    layout_element: LayoutElement

    def drawing_elements(self) -> None:
        return None
