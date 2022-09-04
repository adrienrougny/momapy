from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from frozendict import frozendict
from typing import Optional
from uuid import uuid4
from enum import Enum

import cairo
import gi
gi.require_version("Pango", '1.0')
gi.require_version("PangoCairo", '1.0')
from gi.repository import Pango, PangoCairo

import momapy.drawing
import momapy.geometry
import momapy.coloring

class Direction(Enum):
    HORIZONTAL = 1
    VERTICAL = 2

class HAlignment(Enum):
    LEFT = 1
    CENTER = 2
    RIGHT = 3

class VAlignment(Enum):
    TOP = 1
    CENTER = 2
    BOTTOM = 3

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

    @abstractmethod
    def flatten(self) -> list["LayoutElement"]:
        pass

@dataclass(frozen=True)
class TextLayoutElement(LayoutElement):
    text: Optional[str] = None
    font_description: Optional[str] = None
    font_color: Optional[momapy.coloring.Color] = momapy.coloring.colors.black
    position: Optional[momapy.geometry.Point] = None
    width: Optional[float] = None
    height: Optional[float] = None
    horizontal_alignment: Optional[HAlignment] = HAlignment.LEFT
    vertical_alignment: Optional[VAlignment] = VAlignment.TOP
    justify: Optional[bool] = False

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    def _make_pango_layout(self):
        cairo_surface = cairo.RecordingSurface(cairo.Content.COLOR_ALPHA, None)
        cairo_context = cairo.Context(cairo_surface)
        pango_layout = PangoCairo.create_layout(cairo_context)
        pango_layout.set_alignment(
            getattr(Pango.Alignment, self.horizontal_alignment.name))
        pango_layout.set_font_description(
            Pango.FontDescription.from_string(self.font_description))
        if self.width is not None:
            pango_layout.set_width(Pango.units_from_double(self.width))
        if self.height is not None:
            pango_layout.set_height(Pango.units_from_double(self.height))
        pango_layout.set_text(self.text)
        pango_layout.set_justify(self.justify)
        return pango_layout

    def _get_pango_line_text_and_initial_pos(
            self, pango_layout, pango_layout_iter, pango_line):
        start_index = pango_line.get_start_index()
        end_index = start_index + pango_line.get_length()
        pos = pango_layout.index_to_pos(start_index)
        Pango.extents_to_pixels(pos)
        x = pos.x
        y = round(Pango.units_to_double(pango_layout_iter.get_baseline()))
        line_text = self.text[start_index:end_index]
        return line_text, momapy.geometry.Point(x, y)

    def _get_tx_and_ty(self, pango_layout):
        _, pango_layout_extents = pango_layout.get_pixel_extents()
        if self.width is not None:
            tx = self.x - self.width/2
        else:
            tx = self.x - (
                pango_layout_extents.x + pango_layout_extents.width/2)
        if self.height is not None:
            if self.vertical_alignment == VAlignment.TOP:
                ty = self.y - self.height/2
            elif self.vertical_alignment == VAlignment.BOTTOM:
                ty = self.y + self.height/2 - pango_layout_extents.height
            else:
                ty = self.y - (
                    pango_layout_extents.y + pango_layout_extents.height/2)
        else:
            ty = self.y - (
                pango_layout_extents.y + pango_layout_extents.height/2)
        return tx, ty

    def _get_bbox(self, pango_layout, pango_layout_extents):
        position = momapy.geometry.Point(
            pango_layout_extents.x + pango_layout_extents.width/2,
            pango_layout_extents.y + pango_layout_extents.height/2
        )
        tx, ty = self._get_tx_and_ty(pango_layout)
        return momapy.geometry.Bbox(
            position + (tx, ty),
            pango_layout_extents.width,
            pango_layout_extents.height
        )

    def logical_bbox(self):
        pango_layout = self._make_pango_layout()
        _, pango_layout_extents = pango_layout.get_pixel_extents()
        return self._get_bbox(pango_layout, pango_layout_extents)


    def ink_bbox(self):
        pango_layout = self._make_pango_layout()
        pango_layout_extents, _ = pango_layout.get_pixel_extents()
        return self._get_bbox(pango_layout, pango_layout_extents)

    def bbox(self):
        return self.logical_bbox()

    def drawing_elements(self):
        drawing_elements = []
        pango_layout = self._make_pango_layout()
        pango_layout_iter = pango_layout.get_iter()
        tx, ty = self._get_tx_and_ty(pango_layout)
        done = False
        while not done:
            pango_line = pango_layout_iter.get_line()
            line_text, pos = self._get_pango_line_text_and_initial_pos(
                pango_layout, pango_layout_iter, pango_line)
            pos += (tx, ty)
            text = momapy.drawing.Text(
                text=line_text,
                position=pos,
                font_description=self.font_description,
                font_color=self.font_color
            )
            drawing_elements.append(text)
            if pango_layout_iter.at_last_line():
                done = True
            else:
                pango_layout_iter.next_line()
        return drawing_elements

    def flatten(self):
        return [self]

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

    @abstractmethod
    def self_flatten(self) -> list[LayoutElement]:
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

    def flatten(self):
        layout_elements = self.self_flatten()
        for sub_layout_element in self.layout_elements:
            layout_elements += sub_layout_element.flatten()
        return layout_elements


@dataclass(frozen=True)
class NodeLayoutElement(GroupLayoutElement):
    position: Optional[momapy.geometry.Point] = None
    width: Optional[float] = None
    height: Optional[float] = None
    label: Optional[TextLayoutElement] = None
    stroke_width: float = None
    stroke: Optional[momapy.coloring.Color] = None
    fill: Optional[momapy.coloring.Color] = None

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
        position, width, height = momapy.positioning.fit(elements)
        return momapy.geometry.Bbox(position, width, height)

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

    def self_flatten(self):
        layout_elements = [self]
        if self.label is not None:
            layout_elements.append(self.label)
        return layout_elements

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
    shorten: float = 0

    def segments(self) -> list[momapy.geometry.Segment]:
        segments = []
        for i in range(len(self.points))[1:]:
            segments.append(
                momapy.geometry.Segment(self.points[i - 1], self.points[i]))
        return segments

    def length(self):
        return sum([segment.length() for segment in self.segments()])

    def self_bbox(self):
        import momapy.positioning
        position, width, height = momapy.positioning.fit(
            self.points + [self.arrowhead_bbox()])
        return momapy.geometry.Bbox(position, width, height)

    def bbox(self):
        import momapy.positioning
        elements = [self.self_bbox()]
        if self.source is not None:
            elements.append(self.source)
        if self.target is not None:
            elements.append(self.target)
        elements += self.layout_elements
        position, width, height = momapy.positioning.fit(elements)
        return momapy.geometry.Bbox(position, width, height)

    def start_point(self) -> momapy.geometry.Point:
        return self.points[0]

    def end_point(self) -> momapy.geometry.Point:
        return self.points[-1]

    def arrowhead_base(self) -> momapy.geometry.Point:
        last_segment = self.segments()[-1]
        fraction = (1 - (self.arrowhead_length() + self.shorten)
                        / last_segment.length())
        p, _ = momapy.geometry.get_position_and_angle_at_fraction(
            last_segment, fraction)
        return p

    def arrowhead_tip(self) -> momapy.geometry.Point:
        last_segment = self.segments()[-1]
        fraction = 1 - self.shorten/last_segment.length()
        p, _ = momapy.geometry.get_position_and_angle_at_fraction(
            last_segment, fraction)
        return p

    @abstractmethod
    def arrowhead_length(self) -> float:
        pass

    @abstractmethod
    def arrowhead_drawing_element(self) -> momapy.drawing.DrawingElement:
        pass

    @abstractmethod
    def arrowhead_bbox(self) -> momapy.geometry.Bbox:
        pass

    def self_drawing_elements(self):

        def _get_path_from_points(arc_layout) -> momapy.drawing.Path:
            path = momapy.drawing.Path(
                stroke=arc_layout.stroke, stroke_width=arc_layout.stroke_width)
            path += momapy.drawing.move_to(arc_layout.start_point())
            for segment in arc_layout.segments()[:-1]:
                path += momapy.drawing.line_to(segment.p2)
            if arc_layout.arrowhead_drawing_element() is not None:
                path += momapy.drawing.line_to(arc_layout.arrowhead_base())
            else:
                path += momapy.drawing.line_to(arc_layout.arrowhead_tip())
            return path

        drawing_elements = []
        if self.source is not None:
            drawing_elements += self.source.drawing_elements()
        if self.target is not None:
            drawing_elements += self.target.drawing_elements()
        drawing_elements += [_get_path_from_points(self)]
        arrowhead_drawing_element = self.arrowhead_drawing_element()
        if arrowhead_drawing_element is not None:
            last_segment = self.segments()[-1]
            angle = momapy.geometry.get_angle_of_line(last_segment)
            transform = tuple([
                momapy.drawing.rotate(angle, self.arrowhead_base())])
            arrowhead_drawing_element = replace(
                arrowhead_drawing_element, transform=transform)
            drawing_elements.append(arrowhead_drawing_element)
        return drawing_elements

    def self_flatten(self):
        layout_elements = []
        if self.source is not None:
            layout_elements.append(self.source)
        if self.target is not None:
            layout_elements.append(self.target)
        layout_elements.append(self)
        return layout_elements


@dataclass(frozen=True)
class Model(MapElement):
    pass


@dataclass(frozen=True)
class Layout(GroupLayoutElement):
    position: Optional[momapy.geometry.Point] = None
    width: Optional[float] = None
    height: Optional[float] = None
    stroke_width: Optional[float] = None
    stroke: Optional[momapy.coloring.Color] = None
    fill: Optional[momapy.coloring.Color] = None

    def self_bbox(self):
        return momapy.geometry.Bbox(self.position, self.width, self.height)

    def self_drawing_elements(self):
        path = momapy.drawing.Path(stroke=self.stroke, fill=self.fill,
                    stroke_width=self.stroke_width)
        path += (momapy.drawing.move_to(self.bbox().north_west())
                    + momapy.drawing.line_to(self.bbox().north_east())
                    + momapy.drawing.line_to(self.bbox().south_east())
                    + momapy.drawing.line_to(self.bbox().south_west())
                    + momapy.drawing.close()
                )
        return [path]

    def self_flatten(self):
        return [self]

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

    def flatten(self):
        return [self]

    def __getattr__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            if self.layout_element is not None:
                return getattr(self.layout_element, name)
            else:
                raise AttributeError
