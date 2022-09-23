from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from frozendict import frozendict
from typing import Optional
from uuid import uuid4
from enum import Enum
import math

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
    def children(self) -> list["LayoutElement"]:
        pass

    def descendants(self) -> list["LayoutElement"]:
        descendants = []
        for child in self.children():
            descendants += child.flatten()
        return descendants

    def flatten(self) -> list["LayoutElement"]:
        return [self] + self.descendants()

@dataclass(frozen=True)
class TextLayoutElement(LayoutElement):
    text: Optional[str] = None
    font_size: Optional[float] = None
    font_family: Optional[str] = None
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
        pango_font_description = Pango.FontDescription()
        pango_font_description.set_family(self.font_family)
        pango_font_description.set_absolute_size(
            Pango.units_from_double(self.font_size))
        pango_layout.set_font_description(pango_font_description)
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
                font_family=self.font_family,
                font_size=self.font_size,
                fill=self.font_color,
                stroke=momapy.drawing.NoneValue,
                position=pos
            )
            drawing_elements.append(text)
            if pango_layout_iter.at_last_line():
                done = True
            else:
                pango_layout_iter.next_line()
        return drawing_elements

    def children(self):
        return []

@dataclass(frozen=True)
class GroupLayoutElement(LayoutElement):
    layout_elements: tuple[LayoutElement] = field(default_factory=tuple)
    transform: Optional[tuple[momapy.geometry.Transformation]] = None
    filter: Optional[momapy.drawing.Filter] = None

    @abstractmethod
    def self_bbox(self) -> momapy.geometry.Bbox:
        pass

    @abstractmethod
    def self_drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        pass

    @abstractmethod
    def self_children(self) -> list[LayoutElement]:
        pass

    def drawing_elements(self):
        drawing_elements = self.self_drawing_elements()
        for child in self.children():
            drawing_elements += child.drawing_elements()
        group = momapy.drawing.Group(
            elements=drawing_elements,
            transform=self.transform,
            filter=self.filter)
        return [group]

    def children(self):
        return self.self_children() + list(self.layout_elements)

    def bbox(self):
        import momapy.positioning
        position, width, height = momapy.positioning.fit(
            [self.self_bbox()] + self.descendants())
        return momapy.geometry.Bbox(position, width, height)


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

    @abstractmethod
    def border_drawing_element(self) -> Optional[
            momapy.drawing.DrawingElement]:
        pass

    def self_drawing_elements(self):
        border_drawing_element = self.border_drawing_element()
        if border_drawing_element is not None:
            return [border_drawing_element]
        return []

    def self_children(self):
        if self.label is not None:
            return [self.label]
        return []

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

    @abstractmethod
    def label_center(self) -> momapy.geometry.Point:
        pass

    def _border_from_drawing_elements(self, drawing_elements, point):
        line = momapy.geometry.Line(self.center(), point)
        objects = []
        for drawing_element in drawing_elements:
            objects += drawing_element.to_geometry()
        intersection = []
        for obj in objects:
            obj_intersection = obj.get_intersection_with_line(line)
            if obj_intersection is not None:
                intersection += obj_intersection
        intersection_point = None
        max_d = -1
        ok_direction_exists = False
        d1 = momapy.geometry.get_distance_between_points(
                point, self.center())
        for candidate_point in intersection:
            d2 = momapy.geometry.get_distance_between_points(
                candidate_point, point)
            d3 = momapy.geometry.get_distance_between_points(
                candidate_point, self.center())
            candidate_ok_direction = (not d2 > d1 or d2 < d3)
            if candidate_ok_direction or not ok_direction_exists:
                if candidate_ok_direction and not ok_direction_exists:
                    ok_direction_exists = True
                    max_d = -1
                if d3 > max_d:
                    max_d = d3
                    intersection_point = candidate_point
        return intersection_point


    def border(self, point) -> momapy.geometry.Point:
        return self._border_from_drawing_elements(
            self.drawing_elements(), point)

    def self_border(self, point) -> momapy.geometry.Point:
        return self._border_from_drawing_elements(
            self.self_drawing_elements(), point)

    def self_angle(self, angle, unit="degrees") -> momapy.geometry.Point:
        if unit == "degrees":
            angle = math.radians(angle)
        d = 100
        point = self.center() + (d*math.cos(angle), d*math.sin(angle))
        return self.self_border(point)

    def angle(self, angle, unit="degrees") -> momapy.geometry.Point:
        if unit == "degrees":
            angle = math.radians(angle)
        d = 100
        point = self.center() + (d*math.cos(angle), d*math.sin(angle))
        return self.border(point)


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
        elements = list(self.points) + [self.arrowhead_bbox()]
        if self.source is not None:
            elements.append(self.source)
        if self.target is not None:
            elements.append(self.target)
        position, width, height = momapy.positioning.fit(elements)
        return momapy.geometry.Bbox(position, width, height)

    def start_point(self) -> momapy.geometry.Point:
        return self.points[0]

    def end_point(self) -> momapy.geometry.Point:
        return self.points[-1]

    def arrowhead_base(self) -> momapy.geometry.Point:
        last_segment = self.segments()[-1]
        if last_segment.length() == 0:
            return self.arrowhead_tip() - (self.arrowhead_length(), 0)
        fraction = (1 - (self.arrowhead_length() + self.shorten)
                        / last_segment.length())
        p, _ = momapy.geometry.get_position_and_angle_at_fraction(
            last_segment, fraction)
        return p

    def arrowhead_tip(self) -> momapy.geometry.Point:
        last_segment = self.segments()[-1]
        if last_segment.length() == 0:
            return last_segment.p2
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

        drawing_elements = [_get_path_from_points(self)]
        arrowhead_drawing_element = self.arrowhead_drawing_element()
        if arrowhead_drawing_element is not None:
            last_segment = self.segments()[-1]
            angle = momapy.geometry.get_angle_of_line(last_segment)
            transform = tuple([
                momapy.geometry.Rotation(angle, self.arrowhead_base())])
            arrowhead_drawing_element = replace(
                arrowhead_drawing_element, transform=transform)
            drawing_elements.append(arrowhead_drawing_element)
        return drawing_elements

    def self_children(self):
        layout_elements = []
        if self.source is not None:
            layout_elements.append(self.source)
        if self.target is not None:
            layout_elements.append(self.target)
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
        path += (momapy.drawing.move_to(self.self_bbox().north_west())
                    + momapy.drawing.line_to(self.self_bbox().north_east())
                    + momapy.drawing.line_to(self.self_bbox().south_east())
                    + momapy.drawing.line_to(self.self_bbox().south_west())
                    + momapy.drawing.close()
        )
        return [path]

    def self_children(self):
        return []

@dataclass(frozen=True)
class PhantomLayoutElement(LayoutElement):
    layout_element: Optional[LayoutElement] = None

    def bbox(self):
        return self.layout_element.bbox()

    def drawing_elements(self):
        return []

    def children(self):
        return []

    def __getattr__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            if self.layout_element is not None:
                return getattr(self.layout_element, name)
            else:
                raise AttributeError
class ModelLayoutMapping(frozendict):
    pass

@dataclass(frozen=True)
class Map(MapElement):
    model: Optional[Model] = None
    layout: Optional[Layout] = None
    model_layout_mapping: ModelLayoutMapping = field(
        default_factory=ModelLayoutMapping)


