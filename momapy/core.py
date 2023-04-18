from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from frozendict import frozendict
from typing import Optional, Union, Any
from uuid import uuid4
from enum import Enum
import math
import collections
import copy

import shapely

import cairo

import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo

import momapy.drawing
import momapy.geometry
import momapy.coloring
import momapy.builder


class Direction(Enum):
    HORIZONTAL = 1
    VERTICAL = 2
    UP = 3
    RIGHT = 4
    DOWN = 5
    LEFT = 6


class HAlignment(Enum):
    LEFT = 1
    CENTER = 2
    RIGHT = 3


class VAlignment(Enum):
    TOP = 1
    CENTER = 2
    BOTTOM = 3


@dataclass(frozen=True, kw_only=True)
class MapElement(ABC):
    id: str = field(hash=False, compare=False, default_factory=uuid4)


@dataclass(frozen=True, kw_only=True)
class ModelElement(MapElement):
    pass


@dataclass(frozen=True, kw_only=True)
class LayoutElement(MapElement):
    def bbox(self) -> momapy.geometry.Bbox:
        bounds = self.to_shapely().bounds
        return momapy.geometry.Bbox.from_bounds(bounds)

    @abstractmethod
    def drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        pass

    @abstractmethod
    def children(self) -> list["LayoutElement"]:
        pass

    @abstractmethod
    def translated(self, tx, ty) -> list["LayoutElement"]:
        pass

    @abstractmethod
    def childless(self) -> "LayoutElement":
        pass

    def descendants(self) -> list["LayoutElement"]:
        descendants = []
        for child in self.children():
            descendants.append(child)
            descendants += child.descendants()
        return descendants

    def flattened(self) -> list["LayoutElement"]:
        flattened = [self.childless()]
        for child in self.children():
            flattened += child.flattened()
        return flattened

    def equals(self, other, flattened=False, unordered=False):
        if type(self) is type(other):
            if not flattened:
                return self == other
            else:
                if not unordered:
                    return self.flattened() == other.flattened()
                else:
                    return set(self.flattened()) == set(other.flattened())
        return False

    def contains(self, other):
        return other in self.descendants()

    def to_shapely(self, to_polygons=False):
        geom_collection = []
        for drawing_element in self.drawing_elements():
            geom_collection += drawing_element.to_shapely(
                to_polygons=to_polygons
            ).geoms
        return shapely.GeometryCollection(geom_collection)


@dataclass(frozen=True, kw_only=True)
class TextLayout(LayoutElement):
    text: str
    position: momapy.geometry.Point
    font_size: float
    font_family: str
    font_color: momapy.coloring.Color = momapy.coloring.black
    width: Optional[float] = None
    height: Optional[float] = None
    horizontal_alignment: HAlignment = HAlignment.LEFT
    vertical_alignment: VAlignment = VAlignment.TOP
    justify: Optional[bool] = False

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    def _make_pango_layout(self):
        cairo_surface = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)
        cairo_context = cairo.Context(cairo_surface)
        pango_layout = PangoCairo.create_layout(cairo_context)
        pango_layout.set_alignment(
            getattr(Pango.Alignment, self.horizontal_alignment.name)
        )
        pango_font_description = Pango.FontDescription()
        pango_font_description.set_family(self.font_family)
        pango_font_description.set_absolute_size(
            Pango.units_from_double(self.font_size)
        )
        pango_layout.set_font_description(pango_font_description)
        if self.width is not None:
            pango_layout.set_width(Pango.units_from_double(self.width))
        if self.height is not None:
            pango_layout.set_height(Pango.units_from_double(self.height))
        pango_layout.set_text(self.text)
        pango_layout.set_justify(self.justify)
        return pango_layout

    def _get_pango_line_text_and_initial_pos(
        self, pango_layout, pango_layout_iter, pango_line
    ):
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
            tx = self.x - self.width / 2
        else:
            tx = self.x - (
                pango_layout_extents.x + pango_layout_extents.width / 2
            )
        if self.height is not None:
            if self.vertical_alignment == VAlignment.TOP:
                ty = self.y - self.height / 2
            elif self.vertical_alignment == VAlignment.BOTTOM:
                ty = self.y + self.height / 2 - pango_layout_extents.height
            else:
                ty = self.y - (
                    pango_layout_extents.y + pango_layout_extents.height / 2
                )
        else:
            ty = self.y - (
                pango_layout_extents.y + pango_layout_extents.height / 2
            )
        return tx, ty

    def _get_bbox(self, pango_layout, pango_layout_extents):
        position = momapy.geometry.Point(
            pango_layout_extents.x + pango_layout_extents.width / 2,
            pango_layout_extents.y + pango_layout_extents.height / 2,
        )
        tx, ty = self._get_tx_and_ty(pango_layout)
        return momapy.geometry.Bbox(
            position + (tx, ty),
            pango_layout_extents.width,
            pango_layout_extents.height,
        )

    def logical_bbox(self):
        pango_layout = self._make_pango_layout()
        _, pango_layout_extents = pango_layout.get_pixel_extents()
        return self._get_bbox(pango_layout, pango_layout_extents)

    def ink_bbox(self):
        pango_layout = self._make_pango_layout()
        pango_layout_extents, _ = pango_layout.get_pixel_extents()
        return self._get_bbox(pango_layout, pango_layout_extents)

    def drawing_elements(self):
        drawing_elements = []
        pango_layout = self._make_pango_layout()
        pango_layout_iter = pango_layout.get_iter()
        tx, ty = self._get_tx_and_ty(pango_layout)
        done = False
        while not done:
            pango_line = pango_layout_iter.get_line()
            line_text, pos = self._get_pango_line_text_and_initial_pos(
                pango_layout, pango_layout_iter, pango_line
            )
            pos += (tx, ty)
            text = momapy.drawing.Text(
                text=line_text,
                font_family=self.font_family,
                font_size=self.font_size,
                fill=self.font_color,
                stroke=momapy.drawing.NoneValue,
                position=pos,
            )
            drawing_elements.append(text)
            if pango_layout_iter.at_last_line():
                done = True
            else:
                pango_layout_iter.next_line()
        return drawing_elements

    def children(self):
        return []

    def childless(self):
        return copy.deepcopy(self)

    def translated(self, tx, ty):
        return replace(self, position=self.position + (tx, ty))

    def north_west(self):
        return self.bbox().north_west()

    def north(self):
        return self.bbox().north()

    def north_east(self):
        return self.bbox().north_east()

    def east(self):
        return self.bbox().east()

    def south_east(self):
        return self.bbox().south_east()

    def south(self):
        return self.bbox().south()

    def south_west(self):
        return self.bbox().south_west()

    def west(self):
        return self.bbox().west()


@dataclass(frozen=True, kw_only=True)
class GroupLayout(LayoutElement):
    layout_elements: tuple[LayoutElement] = field(default_factory=tuple)
    stroke: Optional[
        Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = None  # inherited
    stroke_width: Optional[float] = None  # inherited
    stroke_dasharray: Optional[
        Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = None  # inherited
    stroke_dashoffset: Optional[float] = None  # inherited
    fill: Optional[
        Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = None  # inherited
    transform: Optional[
        Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = None  # not inherited
    filter: Optional[
        Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = None  # not inherited

    def self_to_shapely(self, to_polygons=False):
        geom_collection = []
        for drawing_element in self.self_drawing_elements():
            geom_collection += drawing_element.to_shapely(
                to_polygons=to_polygons
            ).geoms
        return shapely.GeometryCollection(geom_collection)

    def self_bbox(self) -> momapy.geometry.Bbox:
        bounds = self.self_to_shapely().bounds
        return momapy.geometry.Bbox.from_bounds(bounds)

    @abstractmethod
    def self_drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        pass

    @abstractmethod
    def self_children(self) -> list[LayoutElement]:
        pass

    def drawing_elements(self):
        drawing_elements = self.self_drawing_elements()
        for child in self.children():
            if child is not None:
                drawing_elements += child.drawing_elements()
        group = momapy.drawing.Group(
            elements=drawing_elements,
            stroke=self.stroke,
            stroke_width=self.stroke_width,
            stroke_dasharray=self.stroke_dasharray,
            stroke_dashoffset=self.stroke_dashoffset,
            fill=self.fill,
            transform=self.transform,
            filter=self.filter,
        )
        return [group]

    def children(self):
        return self.self_children() + list(self.layout_elements)

    def childless(self):
        return replace(self, layout_elements=None)

    def translated(self, tx, ty):
        layout_elements = type(self.layout_elements)(
            [le.translated(tx, ty) for le in self.layout_elements]
        )
        return replace(self, layout_elements=layout_elements)


@dataclass(frozen=True, kw_only=True)
class NodeLayout(GroupLayout):
    position: momapy.geometry.Point
    width: float
    height: float
    label: Optional[TextLayout] = None

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    @abstractmethod
    def border_drawing_element(self) -> Optional[momapy.drawing.DrawingElement]:
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

    def north_west(self) -> momapy.geometry.Point:
        line = momapy.geometry.Line(
            self.center(), self.center() - (self.width / 2, self.height / 2)
        )
        angle = -momapy.geometry.get_angle_of_line(line)
        return self.self_angle(angle, unit="radians")

    def north(self) -> momapy.geometry.Point:
        return self.self_angle(90)

    def north_east(self) -> momapy.geometry.Point:
        line = momapy.geometry.Line(
            self.center(), self.center() + (self.width / 2, -self.height / 2)
        )
        angle = -momapy.geometry.get_angle_of_line(line)
        return self.self_angle(angle, unit="radians")

    def east(self) -> momapy.geometry.Point:
        return self.self_angle(0)

    def south_east(self) -> momapy.geometry.Point:
        line = momapy.geometry.Line(
            self.center(), self.center() + (self.width / 2, self.height / 2)
        )
        angle = -momapy.geometry.get_angle_of_line(line)
        return self.self_angle(angle, unit="radians")

    def south(self) -> momapy.geometry.Point:
        return self.self_angle(270)

    def south_west(self) -> momapy.geometry.Point:
        line = momapy.geometry.Line(
            self.center(), self.center() + (-self.width / 2, self.height / 2)
        )
        angle = -momapy.geometry.get_angle_of_line(line)
        return self.self_angle(angle, unit="radians")

    def west(self) -> momapy.geometry.Point:
        return self.self_angle(180)

    def center(self) -> momapy.geometry.Point:
        return self.position

    def label_center(self) -> momapy.geometry.Point:
        return self.position

    def _border_from_shapely(self, shapely_obj, point):
        line = momapy.geometry.Line(self.center(), point)
        intersection = momapy.geometry.get_intersection_of_object_and_line(
            shapely_obj, line
        )
        candidate_points = []
        for intersection_obj in intersection:
            if isinstance(intersection_obj, momapy.geometry.Segment):
                candidate_points.append(intersection_obj.p1)
                candidate_points.append(intersection_obj.p2)
            elif isinstance(intersection_obj, momapy.geometry.Point):
                candidate_points.append(intersection_obj)
        intersection_point = None
        max_d = -1
        ok_direction_exists = False
        d1 = momapy.geometry.get_distance_between_points(point, self.center())
        for candidate_point in candidate_points:
            d2 = momapy.geometry.get_distance_between_points(
                candidate_point, point
            )
            d3 = momapy.geometry.get_distance_between_points(
                candidate_point, self.center()
            )
            candidate_ok_direction = not d2 > d1 or d2 < d3
            if candidate_ok_direction or not ok_direction_exists:
                if candidate_ok_direction and not ok_direction_exists:
                    ok_direction_exists = True
                    max_d = -1
                if d3 > max_d:
                    max_d = d3
                    intersection_point = candidate_point
        return intersection_point

    def self_border(self, point) -> momapy.geometry.Point:
        return self._border_from_shapely(self.self_to_shapely(), point)

    def border(self, point) -> momapy.geometry.Point:
        return self._border_from_shapely(self.to_shapely(), point)

    def _make_point_for_angle(self, angle, unit="degrees"):
        if unit == "degrees":
            angle = math.radians(angle)
        angle = -angle
        d = 100
        point = self.center() + (d * math.cos(angle), d * math.sin(angle))
        return point

    def self_angle(self, angle, unit="degrees") -> momapy.geometry.Point:
        point = self._make_point_for_angle(angle, unit)
        return self.self_border(point)

    def angle(self, angle, unit="degrees") -> momapy.geometry.Point:
        point = self._make_point_for_angle(angle, unit)
        return self.border(point)

    def childless(self):
        return replace(self, label=None, layout_elements=None)

    def translated(self, tx, ty):
        if self.label is not None:
            label = replace(label, position=label.position + (tx, ty))
        else:
            label = None
        layout_elements = type(self.layout_elements)(
            [le.translated(tx, ty) for le in self.layout_elements]
        )
        return replace(self, label=label, layout_elements=layout_elements)


@dataclass(frozen=True, kw_only=True)
class ArcLayout(GroupLayout):
    segments: tuple[
        momapy.geometry.Segment,
        momapy.geometry.BezierCurve,
        momapy.geometry.EllipticalArc,
    ] = field(default_factory=tuple)
    source: Optional[LayoutElement] = None
    target: Optional[LayoutElement] = None
    arrowhead_stroke: Optional[
        Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = None
    arrowhead_stroke_width: Optional[float] = None
    arrowhead_stroke_dasharray: Optional[
        Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = None
    arrowhead_stroke_dashoffset: Optional[float] = None

    arrowhead_fill: Optional[
        Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = None
    shorten: float = 0.0

    def points(self) -> list[momapy.geometry.Point]:
        points = []
        for i, segment in enumerate(self.segments):
            if i == 0:
                points.append(segment.p1)
            points.append(segment.p2)
        return points

    def length(self):
        return sum([segment.length() for segment in self.segments])

    def start_point(self) -> momapy.geometry.Point:
        return self.points()[0]

    def end_point(self) -> momapy.geometry.Point:
        return self.points()[-1]

    def arrowhead_base(self) -> momapy.geometry.Point:
        last_segment = self.segments[-1]
        if last_segment.length() == 0:
            return self.arrowhead_tip() - (self.arrowhead_length(), 0)
        fraction = (
            1 - (self.arrowhead_length() + self.shorten) / last_segment.length()
        )
        return last_segment.get_position_at_fraction(fraction)

    def arrowhead_tip(self) -> momapy.geometry.Point:
        last_segment = self.segments[-1]
        if last_segment.length() == 0:
            return last_segment.p2
        fraction = 1 - self.shorten / last_segment.length()
        return last_segment.get_position_at_fraction(fraction)

    @abstractmethod
    def arrowhead_length(self) -> float:
        pass

    @abstractmethod
    def arrowhead_drawing_element(
        self,
    ) -> Optional[momapy.drawing.DrawingElement]:
        pass

    def _make_rotated_arrowhead_drawing_element(self):
        line = momapy.geometry.Line(self.arrowhead_base(), self.arrowhead_tip())
        angle = momapy.geometry.get_angle_of_line(line)
        rotation = momapy.geometry.Rotation(angle, self.arrowhead_base())
        arrowhead_drawing_element = (
            self.arrowhead_drawing_element().transformed(rotation)
        )
        return arrowhead_drawing_element

    def arrowhead_bbox(self) -> momapy.geometry.Bbox:
        if self.arrowhead_drawing_element() is not None:
            arrowhead_drawing_element = (
                self._make_rotated_arrowhead_drawing_element()
            )
            bounds = arrowhead_drawing_element.to_shapely().bounds
        else:
            bounds = self.arrowhead_tip().to_shapely().bounds
        return momapy.geometry.Bbox.from_bounds(bounds)

    def self_drawing_elements(self):
        def _make_path_action_from_segment(segment):
            if momapy.builder.isinstance_or_builder(
                segment, momapy.geometry.Segment
            ):
                path_action = momapy.drawing.line_to(segment.p2)
            elif momapy.builder.isinstance_or_builder(
                segment, momapy.geometry.BezierCurve
            ):
                if len(segment.control_points) >= 2:
                    path_action = momapy.drawing.curve_to(
                        segment.p2,
                        segment.control_points[0],
                        segment.control_points[1],
                    )
                else:
                    path_action = momapy.drawing.quadratic_curve_to(
                        segment.p2, segment.control_points[0]
                    )
            elif momapy.builder.isinstance_or_builder(
                segment, momapy.geometry.EllipticalArc
            ):
                path_action = momapy.drawing.EllipticalArc(
                    segment.p2,
                    segment.rx,
                    segment.ry,
                    segment.x_axis_rotation,
                    segment.arc_flag,
                    segment.seep_flag,
                )
            return path_action

        def _make_path_from_segments(arc_layout) -> momapy.drawing.Path:
            path = momapy.drawing.Path()
            path += momapy.drawing.move_to(arc_layout.start_point())
            for segment in arc_layout.segments[:-1]:
                path_action = _make_path_action_from_segment(segment)
                path += path_action
            last_segment = self.segments[-1]
            length = self.shorten
            if arc_layout.arrowhead_drawing_element() is not None:
                length += self.arrowhead_length()
            if length > 0:
                last_segment = last_segment.shortened(length)
            path_action = _make_path_action_from_segment(last_segment)
            path += path_action
            return path

        drawing_elements = [_make_path_from_segments(self)]
        if self.arrowhead_drawing_element() is not None:
            arrowhead_drawing_element = (
                self._make_rotated_arrowhead_drawing_element()
            )
            drawing_elements.append(arrowhead_drawing_element)
        return drawing_elements

    def self_children(self):
        layout_elements = []
        if self.source is not None:
            layout_elements.append(self.source)
        if self.target is not None:
            layout_elements.append(self.target)
        return layout_elements

    def childless(self):
        return replace(self, source=None, target=None, layout_elements=None)

    def translated(self, tx, ty):
        points = type(self.points)([point + (tx, ty) for point in self.points])

        layout_elements = type(self.layout_elements)(
            [le.translated(tx, ty) for le in self.layout_elements]
        )
        return replace(self, points=points, layout_elements=layout_elements)

    def fraction(self, fraction):
        current_length = 0
        length_to_reach = fraction * self.length()
        for segment in self.segments:
            current_length += segment.length()
            if current_length >= length_to_reach:
                break
        position, angle = momapy.geometry.get_position_and_angle_at_fraction(
            segment, fraction
        )
        return position, angle


@dataclass(frozen=True, kw_only=True)
class Model(MapElement):
    @abstractmethod
    def is_submodel(self, other):
        pass


@dataclass(frozen=True, kw_only=True)
class MapLayout(GroupLayout):
    position: momapy.geometry.Point
    width: float
    height: float

    def self_bbox(self):
        return momapy.geometry.Bbox(self.position, self.width, self.height)

    def self_drawing_elements(self):
        path = momapy.drawing.Path()
        path += (
            momapy.drawing.move_to(self.self_bbox().north_west())
            + momapy.drawing.line_to(self.self_bbox().north_east())
            + momapy.drawing.line_to(self.self_bbox().south_east())
            + momapy.drawing.line_to(self.self_bbox().south_west())
            + momapy.drawing.close()
        )
        return [path]

    def self_children(self):
        return []

    def childless(self):
        return replace(self, layout_elements=None)

    def translated(self, tx, ty):
        return replace(self, position=self.position + (tx, ty))

    def is_sublayout(self, other, flattened=False, unordered=False):
        def _is_sublist(list1, list2, unordered=False) -> bool:
            if not unordered:
                i = 0
                for elem2 in list2:
                    elem1 = list1[i]
                    while elem1 != elem2 and i < len(list1) - 1:
                        i += 1
                        elem1 = list1[i]
                    if not elem1 == elem2:
                        return False
                    i += 1
            else:
                dlist1 = collections.defaultdict(int)
                dlist2 = collections.defaultdict(int)
                for elem1 in list1:
                    dlist1[elem1] += 1
                for elem2 in list2:
                    dlist2[elem2] += 1
                for elem2 in dlist2:
                    if dlist1[elem2] < dlist2[elem2]:
                        return False
            return True

        if self.childless() != other.childless():
            return False
        if flattened:
            return _is_sublist(
                self.flattened()[1:], other.flattened()[1:], unordered=unordered
            )
        return _is_sublist(
            self.children(), other.children(), unordered=unordered
        )


@dataclass(frozen=True, kw_only=True)
class PhantomLayout(LayoutElement):
    layout_element: LayoutElement

    def bbox(self):
        return self.layout_element.bbox()

    def drawing_elements(self):
        return []

    def children(self):
        return []

    def childless(self):
        return copy.deepcopy(self)

    def translated(self):
        return copy.deepcopy(self)

    def __getattr__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            if self.layout_element is not None:
                return getattr(self.layout_element, name)
            else:
                raise AttributeError


class LayoutModelMapping(
    frozendict
):  # frozendict[LayoutElement, tuple[ModelElement, None | ModelElement]]
    def is_submapping(self, other):
        for layout_element in self:
            mapping = self[layout_element]
            other_mapping = other.get(layout_element)
            if mapping != other_mapping:
                return False
        return True


@dataclass(frozen=True, kw_only=True)
class Map(MapElement):
    model: Model
    layout: MapLayout
    layout_model_mapping: LayoutModelMapping

    def is_submap(self, other):
        return (
            self.model.is_submodel(other.model)
            and self.layout.is_sublayout(other.layout)
            and self.layout_model_mapping.is_submapping(
                other.layout_model_mapping
            )
        )


class ListBuilder(list, momapy.builder.Builder):
    _cls_to_build = list

    def build(
        self,
        builder_object_mapping: dict[momapy.builder.Builder, Any] | None = None,
    ):
        if builder_object_mapping is not None:
            obj = builder_object_mapping.get(id(self))
            if obj is not None:
                return obj
        else:
            builder_object_mapping = {}
        obj = self._cls_to_build(
            [
                momapy.builder.object_from_builder(elem, builder_object_mapping)
                for elem in self
            ]
        )
        return obj

    @classmethod
    def from_object(
        cls,
        obj,
        object_builder_mapping: dict[int, momapy.builder.Builder] | None = None,
    ):
        if object_builder_mapping is not None:
            builder = object_builder_mapping.get(id(obj))
            if builder is not None:
                return builder
        else:
            object_builder_mapping = {}
        builder = cls(
            [
                momapy.builder.builder_from_object(elem, object_builder_mapping)
                for elem in obj
            ]
        )
        return builder


class TupleBuilder(list, momapy.builder.Builder):
    _cls_to_build = tuple

    def build(
        self,
        builder_object_mapping: dict[momapy.builder.Builder, Any] | None = None,
    ):
        if builder_object_mapping is not None:
            obj = builder_object_mapping.get(id(self))
            if obj is not None:
                return obj
        else:
            builder_object_mapping = {}
        obj = self._cls_to_build(
            [
                momapy.builder.object_from_builder(elem, builder_object_mapping)
                for elem in self
            ]
        )
        return obj

    @classmethod
    def from_object(
        cls,
        obj,
        object_builder_mapping: dict[int, momapy.builder.Builder] | None = None,
    ):
        if object_builder_mapping is not None:
            builder = object_builder_mapping.get(id(obj))
            if builder is not None:
                return builder
        else:
            object_builder_mapping = {}
        builder = cls(
            [
                momapy.builder.builder_from_object(elem, object_builder_mapping)
                for elem in obj
            ]
        )
        return builder


class SetBuilder(set, momapy.builder.Builder):
    _cls_to_build = set

    def build(
        self,
        builder_object_mapping: dict[momapy.builder.Builder, Any] | None = None,
    ):
        if builder_object_mapping is not None:
            obj = builder_object_mapping.get(id(self))
            if obj is not None:
                return obj
        else:
            builder_object_mapping = {}
        obj = self._cls_to_build(
            [
                momapy.builder.object_from_builder(elem, builder_object_mapping)
                for elem in self
            ]
        )
        return obj

    @classmethod
    def from_object(
        cls,
        obj,
        object_builder_mapping: dict[int, momapy.builder.Builder] | None = None,
    ):
        if object_builder_mapping is not None:
            builder = object_builder_mapping.get(id(obj))
            if builder is not None:
                return builder
        else:
            object_builder_mapping = {}
        builder = cls(
            [
                momapy.builder.builder_from_object(elem, object_builder_mapping)
                for elem in obj
            ]
        )
        return builder


class FrozensetBuilder(set, momapy.builder.Builder):
    _cls_to_build = frozenset

    def build(
        self,
        builder_object_mapping: dict[int, Any] | None = None,
    ):
        if builder_object_mapping is not None:
            obj = builder_object_mapping.get(id(self))
            if obj is not None:
                return obj
        else:
            builder_object_mapping = {}
        obj = self._cls_to_build(
            [
                momapy.builder.object_from_builder(elem, builder_object_mapping)
                for elem in self
            ]
        )
        return obj

    @classmethod
    def from_object(
        cls,
        obj,
        object_builder_mapping: dict[int, momapy.builder.Builder] | None = None,
    ):
        if object_builder_mapping is not None:
            builder = object_builder_mapping.get(id(obj))
            if builder is not None:
                return builder
        else:
            object_builder_mapping = {}
        builder = cls(
            [
                momapy.builder.builder_from_object(elem, object_builder_mapping)
                for elem in obj
            ]
        )
        return builder


class DictBuilder(dict, momapy.builder.Builder):
    _cls_to_build = dict

    def build(
        self,
        builder_object_mapping: dict[momapy.builder.Builder, Any] | None = None,
    ):
        if builder_object_mapping is not None:
            obj = builder_object_mapping.get(id(self))
            if obj is not None:
                return obj
        else:
            builder_object_mapping = {}
        obj = self._cls_to_build(
            [
                (
                    momapy.builder.object_from_builder(
                        key, builder_object_mapping
                    ),
                    momapy.builder.object_from_builder(
                        val, builder_object_mapping
                    ),
                )
                for key, val in self.items()
            ]
        )
        return obj

    @classmethod
    def from_object(
        cls,
        obj,
        object_builder_mapping: dict[int, momapy.builder.Builder] | None = None,
    ):
        if object_builder_mapping is not None:
            builder = object_builder_mapping.get(id(obj))
            if builder is not None:
                return builder
        else:
            object_builder_mapping = {}
        builder = cls(
            [
                (
                    momapy.builder.builder_from_object(
                        key, object_builder_mapping
                    ),
                    momapy.builder.builder_from_object(
                        val, object_builder_mapping
                    ),
                )
                for key, val in obj.items()
            ]
        )
        return builder


class FrozendictBuilder(dict, momapy.builder.Builder):
    _cls_to_build = frozendict

    def build(
        self,
        builder_object_mapping: dict[momapy.builder.Builder, Any] | None = None,
    ):
        if builder_object_mapping is not None:
            obj = builder_object_mapping.get(id(self))
            if obj is not None:
                return obj
        else:
            builder_object_mapping = {}
        obj = self._cls_to_build(
            [
                (
                    momapy.builder.object_from_builder(
                        key, builder_object_mapping
                    ),
                    momapy.builder.object_from_builder(
                        val, builder_object_mapping
                    ),
                )
                for key, val in self.items()
            ]
        )
        return obj

    @classmethod
    def from_object(
        cls,
        obj,
        object_builder_mapping: dict[int, momapy.builder.Builder] | None = None,
    ):
        if object_builder_mapping is not None:
            builder = object_builder_mapping.get(id(obj))
            if builder is not None:
                return builder
        else:
            object_builder_mapping = {}
        builder = cls(
            [
                (
                    momapy.builder.builder_from_object(
                        key, object_builder_mapping
                    ),
                    momapy.builder.builder_from_object(
                        val, object_builder_mapping
                    ),
                )
                for key, val in obj.items()
            ]
        )
        return builder


momapy.builder.register_builder(ListBuilder)
momapy.builder.register_builder(TupleBuilder)
momapy.builder.register_builder(SetBuilder)
momapy.builder.register_builder(FrozensetBuilder)
momapy.builder.register_builder(DictBuilder)
momapy.builder.register_builder(FrozendictBuilder)


def _map_element_builder_hash(self):
    return hash(self.id)


def _map_element_builder_eq(self, other):
    return self.__class__ == other.__class__ and self.id == other.id


MapElementBuilder = momapy.builder.get_or_make_builder_cls(
    MapElement,
    builder_namespace={
        "__hash__": _map_element_builder_hash,
        "__eq__": _map_element_builder_eq,
    },
)

ModelElementBuilder = momapy.builder.get_or_make_builder_cls(ModelElement)
LayoutElementBuilder = momapy.builder.get_or_make_builder_cls(LayoutElement)
NodeLayoutBuilder = momapy.builder.get_or_make_builder_cls(NodeLayout)
ArcLayoutBuilder = momapy.builder.get_or_make_builder_cls(ArcLayout)
TextLayoutBuilder = momapy.builder.get_or_make_builder_cls(TextLayout)


def _model_builder_new_element(self, element_cls, *args, **kwargs):
    if not momapy.builder.issubclass_or_builder(element_cls, ModelElement):
        raise TypeError(
            "element class must be a subclass of ModelElementBuilder or ModelElement"
        )
    return momapy.builder.new_builder(element_cls, *args, **kwargs)


ModelBuilder = momapy.builder.get_or_make_builder_cls(
    Model,
    builder_namespace={"new_element": _model_builder_new_element},
)


def _layout_builder_new_element(self, element_cls, *args, **kwargs):
    if not momapy.builder.issubclass_or_builder(element_cls, LayoutElement):
        raise TypeError(
            "element class must be a subclass of LayoutElementBuilder or LayoutElement"
        )
    return momapy.builder.new_builder(element_cls, *args, **kwargs)


MapLayoutBuilder = momapy.builder.get_or_make_builder_cls(
    MapLayout,
    builder_namespace={"new_element": _layout_builder_new_element},
)


class LayoutModelMappingBuilder(
    FrozendictBuilder
):  # dict[LayoutElementBuilder, tuple[ModelElementBuilder, None | ModelElementBuilder]]
    def is_submapping(self, other):
        for layout_element in self:
            mapping = self[layout_element]
            other_mapping = other.get(layout_element)
            if mapping != other_mapping:
                return False
        return True


@abstractmethod
def _map_builder_new_model(self, *args, **kwargs) -> ModelBuilder:
    pass


@abstractmethod
def _map_builder_new_layout(self, *args, **kwargs) -> MapLayoutBuilder:
    pass


def _map_builder_new_layout_model_mapping(self) -> LayoutModelMappingBuilder:
    return LayoutModelMappingBuilder()


def _map_builder_new_model_element(
    self, element_cls, *args, **kwargs
) -> ModelElementBuilder:
    model_element = self.model.new_element(element_cls, *args, **kwargs)
    return model_element


def _map_builder_new_layout_element(
    self, element_cls, *args, **kwargs
) -> LayoutElementBuilder:
    layout_element = self.layout.new_element(element_cls, *args, **kwargs)
    return layout_element


def _map_builder_add_model_element(self, model_element):
    self.model.add_element(model_element)


def _map_builder_add_layout_element(self, layout_element):
    self.layout.add_element(layout_element)


def _map_builder_map_model_element_to_layout_element(
    self,
    layout_element: LayoutElementBuilder,
    model_element: ModelElementBuilder,
    nm_model_element: None | ModelElementBuilder = None,
):
    self.layout_model_mapping[layout_element] = TupleBuilder(
        [
            model_element,
            nm_model_element,
        ]
    )


MapBuilder = momapy.builder.get_or_make_builder_cls(
    Map,
    builder_namespace={
        "new_model": _map_builder_new_model,
        "new_layout": _map_builder_new_layout,
        "new_layout_model_mapping": _map_builder_new_layout_model_mapping,
        "new_model_element": _map_builder_new_model_element,
        "new_layout_element": _map_builder_new_layout_element,
        "add_model_element": _map_builder_add_model_element,
        "add_layout_element": _map_builder_add_layout_element,
        "map_model_element_to_layout_element": _map_builder_map_model_element_to_layout_element,
    },
)

PhantomLayoutBuilder = momapy.builder.get_or_make_builder_cls(PhantomLayout)
