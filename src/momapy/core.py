import abc
import dataclasses
import frozendict
import typing
import uuid
import enum
import math
import collections
import copy

import shapely

import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo  # must import like that to use

import momapy.drawing
import momapy.geometry
import momapy.coloring
import momapy.builder
import momapy.utils
import momapy._pango


class Direction(enum.Enum):
    HORIZONTAL = 1
    VERTICAL = 2
    UP = 3
    RIGHT = 4
    DOWN = 5
    LEFT = 6


class HAlignment(enum.Enum):
    LEFT = 1
    CENTER = 2
    RIGHT = 3


class VAlignment(enum.Enum):
    TOP = 1
    CENTER = 2
    BOTTOM = 3


@dataclasses.dataclass(frozen=True, kw_only=True)
class MapElement(abc.ABC):
    id: str = dataclasses.field(
        hash=False,
        compare=False,
        default_factory=momapy.utils.get_uuid4_as_str,
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModelElement(MapElement):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LayoutElement(MapElement):
    def bbox(self) -> momapy.geometry.Bbox:
        bounds = self.to_shapely().bounds
        return momapy.geometry.Bbox.from_bounds(bounds)

    @abc.abstractmethod
    def drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        pass

    @abc.abstractmethod
    def children(self) -> list["LayoutElement"]:
        pass

    @abc.abstractmethod
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


@dataclasses.dataclass(frozen=True, kw_only=True)
class TextLayout(LayoutElement):
    text: str
    font_family: str = momapy.drawing.get_initial_value("font_family")
    font_size: float = momapy.drawing.get_initial_value("font_size")
    font_style: momapy.drawing.FontStyle = momapy.drawing.get_initial_value(
        "font_style"
    )
    font_weight: momapy.drawing.FontWeight | float = (
        momapy.drawing.get_initial_value("font_weight")
    )
    position: momapy.geometry.Point
    width: float | None = None
    height: float | None = None
    horizontal_alignment: HAlignment = HAlignment.LEFT
    vertical_alignment: VAlignment = VAlignment.TOP
    justify: bool = False
    fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = None
    filter: momapy.drawing.NoneValueType | momapy.drawing.Filter | None = (
        None  # should be a tuple of filters to follow SVG (to be implemented)
    )
    stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = None
    stroke_dasharray: tuple[float] | None = None
    stroke_dashoffset: float | None = None
    stroke_width: float | None = None
    text_anchor: momapy.drawing.TextAnchor | None = None
    transform: (
        momapy.drawing.NoneValueType
        | tuple[momapy.geometry.Transformation]
        | None
    ) = None

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    def _make_pango_layout(self):
        pango_layout = momapy._pango.make_pango_layout(
            font_family=self.font_family,
            font_size=self.font_size,
            font_style=self.font_style,
            font_weight=self.font_weight,
        )
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
                point=pos,
                fill=self.fill,
                filter=self.filter,
                font_family=self.font_family,
                font_size=self.font_size,
                font_style=self.font_style,
                font_weight=self.font_weight,
                stroke=self.stroke,
                stroke_dasharray=self.stroke_dasharray,
                stroke_dashoffset=self.stroke_dashoffset,
                stroke_width=self.stroke_width,
                text_anchor=self.text_anchor,
                transform=self.transform,
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


@dataclasses.dataclass(frozen=True, kw_only=True)
class Shape(LayoutElement):
    def childless(self):
        return copy.deepcopy(self)

    def children(self):
        return []


@dataclasses.dataclass(frozen=True, kw_only=True)
class GroupLayout(LayoutElement):
    layout_elements: tuple[LayoutElement] = dataclasses.field(
        default_factory=tuple
    )
    fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = None
    fill_rule: momapy.drawing.FillRule | None = None
    filter: momapy.drawing.NoneValueType | momapy.drawing.Filter | None = (
        None  # should be a tuple of filters to follow SVG (to be implemented)
    )
    font_family: str | None = None
    font_size: float | None = None
    font_style: momapy.drawing.FontStyle | None = None
    font_weight: momapy.drawing.FontWeight | float | None = None
    stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = None
    stroke_dasharray: tuple[float] | None = None
    stroke_dashoffset: float | None = None
    stroke_width: float | None = None
    text_anchor: momapy.drawing.TextAnchor | None = None
    transform: (
        momapy.drawing.NoneValueType
        | tuple[momapy.geometry.Transformation]
        | None
    ) = None

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

    @abc.abstractmethod
    def self_drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        pass

    @abc.abstractmethod
    def self_children(self) -> list[LayoutElement]:
        pass

    def drawing_elements(self):
        drawing_elements = self.self_drawing_elements()
        for child in self.children():
            if child is not None:
                drawing_elements += child.drawing_elements()
        group = momapy.drawing.Group(
            elements=drawing_elements,
            fill=self.fill,
            fill_rule=self.fill_rule,
            filter=self.filter,
            font_family=self.font_family,
            font_size=self.font_size,
            font_style=self.font_style,
            font_weight=self.font_weight,
            stroke=self.stroke,
            stroke_dasharray=self.stroke_dasharray,
            stroke_dashoffset=self.stroke_dashoffset,
            stroke_width=self.stroke_width,
            text_anchor=self.text_anchor,
            transform=self.transform,
        )
        return [group]

    def children(self):
        return self.self_children() + list(self.layout_elements)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Node(GroupLayout):
    position: momapy.geometry.Point
    width: float
    height: float
    label: TextLayout | None = None
    border_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    border_stroke_width: float | None = None
    border_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    border_stroke_dashoffset: float | None = None
    border_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    border_transform: (
        momapy.drawing.NoneValueType
        | tuple[momapy.geometry.Transformation]
        | None
    ) = None
    border_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    @abc.abstractmethod
    def border_drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        pass

    def self_drawing_elements(self):
        elements = self.border_drawing_elements()
        border = momapy.drawing.Group(
            stroke=self.border_stroke,
            stroke_width=self.border_stroke_width,
            stroke_dasharray=self.border_stroke_dasharray,
            stroke_dashoffset=self.border_stroke_dashoffset,
            fill=self.border_fill,
            transform=self.border_transform,
            filter=self.border_filter,
            elements=elements,
        )
        return [border]

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
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def north(self) -> momapy.geometry.Point:
        return self.self_angle(90)

    def north_east(self) -> momapy.geometry.Point:
        line = momapy.geometry.Line(
            self.center(), self.center() + (self.width / 2, -self.height / 2)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def east(self) -> momapy.geometry.Point:
        return self.self_angle(0)

    def south_east(self) -> momapy.geometry.Point:
        line = momapy.geometry.Line(
            self.center(), self.center() + (self.width / 2, self.height / 2)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def south(self) -> momapy.geometry.Point:
        return self.self_angle(270)

    def south_west(self) -> momapy.geometry.Point:
        line = momapy.geometry.Line(
            self.center(), self.center() + (-self.width / 2, self.height / 2)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def west(self) -> momapy.geometry.Point:
        return self.self_angle(180)

    def center(self) -> momapy.geometry.Point:
        return self.position

    def label_center(self) -> momapy.geometry.Point:
        return self.position

    def _border_from_shapely(self, shapely_obj, point):
        line = momapy.geometry.Line(self.center(), point)
        intersection = (
            momapy.geometry.get_intersection_of_line_and_shapely_object(
                line, shapely_obj
            )
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
        return dataclasses.replace(self, label=None, layout_elements=None)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Arc(GroupLayout):
    end_shorten: float = 0.0
    path_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        None
    )
    path_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None  # not inherited

    path_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    path_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    path_stroke_dashoffset: float | None = None

    path_stroke_width: float | None = None
    path_transform: (
        momapy.drawing.NoneValueType
        | tuple[momapy.geometry.Transformation]
        | None
    ) = None  # not inherited
    segments: tuple[
        momapy.geometry.Segment
        | momapy.geometry.BezierCurve
        | momapy.geometry.EllipticalArc
    ] = dataclasses.field(default_factory=tuple)
    source: LayoutElement | None = None
    start_shorten: float = 0.0
    target: LayoutElement | None = None

    def points(self) -> list[momapy.geometry.Point]:
        points = []
        for segment in self.segments:
            points.append(segment.p1)
        points.append(segment.p2)
        return points

    def length(self):
        return sum([segment.length() for segment in self.segments])

    def start_point(self) -> momapy.geometry.Point:
        return self.points()[0]

    def end_point(self) -> momapy.geometry.Point:
        return self.points()[-1]

    def self_children(self):
        return []

    def childless(self):
        return dataclasses.replace(self, layout_elements=None)

    def fraction(self, fraction):
        current_length = 0
        length_to_reach = fraction * self.length()
        for segment in self.segments:
            current_length += segment.length()
            if current_length >= length_to_reach:
                break
        position, angle = segment.get_position_and_angle_at_fraction(fraction)
        return position, angle

    @classmethod
    def _make_path_action_from_segment(cls, segment):
        if momapy.builder.isinstance_or_builder(
            segment, momapy.geometry.Segment
        ):
            path_action = momapy.drawing.LineTo(segment.p2)
        elif momapy.builder.isinstance_or_builder(
            segment, momapy.geometry.BezierCurve
        ):
            if len(segment.control_points) >= 2:
                path_action = momapy.drawing.CurveTo(
                    segment.p2,
                    segment.control_points[0],
                    segment.control_points[1],
                )
            else:
                path_action = momapy.drawing.QuadraticCurveTo(
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


@dataclasses.dataclass(frozen=True, kw_only=True)
class SingleHeadedArc(Arc):
    arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    arrowhead_stroke_width: float | None = None
    arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    arrowhead_stroke_dashoffset: float | None = None
    arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    arrowhead_transform: (
        momapy.drawing.NoneValueType
        | tuple[momapy.geometry.Transformation]
        | None
    ) = None  # not inherited
    arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None  # not inherited

    def arrowhead_length(self):
        drawing_element = self._make_arrowhead_drawing_element()
        bbox = drawing_element.bbox()
        width = bbox.width
        if math.isnan(width):
            arrowhead_length = 0
        else:
            arrowhead_length = bbox.east().x
        return round(arrowhead_length, 2)

    def arrowhead_tip(self) -> momapy.geometry.Point:
        segment = self.segments[-1]
        if segment.length() == 0:
            return segment.p2
        fraction = 1 - self.end_shorten / segment.length()
        return segment.get_position_at_fraction(fraction)

    def arrowhead_base(self) -> momapy.geometry.Point:
        drawing_element = self._make_arrowhead_drawing_element()
        arrowhead_length = self.arrowhead_length()
        segment = self.segments[-1]
        if segment.length() == 0:
            return self.arrowhead_tip() - (arrowhead_length, 0)
        fraction = 1 - (arrowhead_length + self.end_shorten) / segment.length()
        return segment.get_position_at_fraction(fraction)

    @abc.abstractmethod
    def arrowhead_drawing_elements(
        self,
    ) -> list[momapy.drawing.DrawingElement]:
        pass

    def _make_arrowhead_drawing_element(self):
        elements = self.arrowhead_drawing_elements()
        group = momapy.drawing.Group(
            stroke=self.arrowhead_stroke,
            stroke_width=self.arrowhead_stroke_width,
            stroke_dasharray=self.arrowhead_stroke_dasharray,
            stroke_dashoffset=self.arrowhead_stroke_dashoffset,
            fill=self.arrowhead_fill,
            transform=self.arrowhead_transform,
            filter=self.arrowhead_filter,
            elements=elements,
        )
        return group

    def _make_rotated_arrowhead_drawing_element(self):
        drawing_element = self._make_arrowhead_drawing_element()
        arrowhead_length = self.arrowhead_length()
        arrowhead_base = self.arrowhead_base()
        last_segment = self.segments[-1]
        if arrowhead_length == 0:
            last_segment_coords = last_segment.to_shapely().coords
            p1 = momapy.geometry.Point.from_tuple(last_segment_coords[-2])
            p2 = momapy.geometry.Point.from_tuple(last_segment_coords[-1])
            line = momapy.geometry.Line(p1, p2)
        else:
            line = momapy.geometry.Line(arrowhead_base, last_segment.p2)
        angle = momapy.geometry.get_angle_to_horizontal_of_line(line)
        translation = momapy.geometry.Translation(
            arrowhead_base.x, arrowhead_base.y
        )
        rotation = momapy.geometry.Rotation(angle, arrowhead_base)
        drawing_element = drawing_element.transformed(translation).transformed(
            rotation
        )
        return drawing_element

    def arrowhead_bbox(self):
        drawing_element = self._make_rotated_arrowhead_drawing_element()
        return drawing_element.bbox()

    def _make_path(self) -> momapy.drawing.Path:
        arrowhead_length = self.arrowhead_length()
        if len(self.segments) == 1:
            segment = (
                self.segments[0]
                .shortened(self.start_shorten, "start")
                .shortened(self.end_shorten + arrowhead_length, "end")
            )
            actions = [
                momapy.drawing.MoveTo(segment.p1),
                self._make_path_action_from_segment(segment),
            ]
        else:
            first_segment = self.segments[0].shortened(
                self.start_shorten, "start"
            )
            last_segment = self.segments[-1].shortened(
                self.end_shorten + arrowhead_length, "end"
            )
            actions = [
                momapy.drawing.MoveTo(first_segment.p1),
                self._make_path_action_from_segment(first_segment),
            ]
            for segment in self.segments[1:-1]:
                action = self._make_path_action_from_segment(segment)
                actions.append(action)
            actions.append(self._make_path_action_from_segment(last_segment))
        path = momapy.drawing.Path(
            stroke=self.path_stroke,
            stroke_width=self.path_stroke_width,
            stroke_dasharray=self.path_stroke_dasharray,
            stroke_dashoffset=self.path_stroke_dasharray,
            fill=self.path_fill,
            transform=self.path_transform,
            filter=self.path_filter,
            actions=actions,
        )
        return path

    def self_drawing_elements(self):
        drawing_elements = [
            self._make_path(),
            self._make_rotated_arrowhead_drawing_element(),
        ]
        return drawing_elements


@dataclasses.dataclass(frozen=True, kw_only=True)
class DoubleHeadedArc(Arc):
    start_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    start_arrowhead_stroke_width: float | None = None
    start_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    start_arrowhead_transform: (
        momapy.drawing.NoneValueType
        | tuple[momapy.geometry.Transformation]
        | None
    ) = None  # not inherited
    start_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None  # not inherited
    end_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    end_arrowhead_stroke_width: float | None = None
    end_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = None
    end_arrowhead_transform: (
        momapy.drawing.NoneValueType
        | tuple[momapy.geometry.Transformation]
        | None
    ) = None  # not inherited
    end_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None  # not inherited

    def _get_arrowhead_length(self, start_or_end: str):
        drawing_element = self._make_arrowhead_drawing_element(start_or_end)
        bbox = drawing_element.bbox()
        width = bbox.width
        if math.isnan(width):
            arrowhead_length = 0
        else:
            arrowhead_length = bbox.east().x
        return round(arrowhead_length, 2)

    def _get_arrowhead_tip(self, start_or_end: str):
        if start_or_end == "start":
            segment = self.segments[0]
            segment = momapy.geometry.Segment(segment.p2, segment.p1)
            shorten = self.start_shorten
        else:
            segment = self.segments[-1]
            shorten = self.end_shorten
        if segment.length() == 0:
            return segment.p2
        fraction = 1 - shorten / segment.length()
        return segment.get_position_at_fraction(fraction)

    def _get_arrowhead_base(self, start_or_end: str):
        arrowhead_length = self._get_arrowhead_length(start_or_end)
        if start_or_end == "start":
            if arrowhead_length == 0:
                return self.start_point()
            segment = self.segments[0]
            segment = momapy.geometry.Segment(segment.p2, segment.p1)
            if segment.length() == 0:
                return self.arrowhead_tip() + (arrowhead_length, 0)
            shorten = self.start_shorten
        else:
            if arrowhead_length == 0:
                return self.end_point()
            segment = self.segments[-1]
            if segment.length() == 0:
                return self.arrowhead_tip() - (arrowhead_length, 0)
            shorten = self.end_shorten
        fraction = 1 - (arrowhead_length + shorten) / segment.length()
        return segment.get_position_at_fraction(fraction)

    def start_arrowhead_length(self):
        return self._get_arrowhead_length("start")

    def start_arrowhead_base(self) -> momapy.geometry.Point:
        return self._get_arrowhead_base("start")

    def start_arrowhead_tip(self) -> momapy.geometry.Point:
        return self._get_arrowhead_tip("start")

    def end_arrowhead_length(self):
        return self._get_arrowhead_length("end")

    def end_arrowhead_base(self) -> momapy.geometry.Point:
        return self._get_arrowhead_base("end")

    def end_arrowhead_tip(self) -> momapy.geometry.Point:
        return self._get_arrowhead_tip("end")

    @abc.abstractmethod
    def start_arrowhead_drawing_elements(
        self,
    ) -> list[momapy.drawing.DrawingElement]:
        pass

    @abc.abstractmethod
    def end_arrowhead_drawing_elements(
        self,
    ) -> list[momapy.drawing.DrawingElement]:
        pass

    def _make_arrowhead_drawing_element(self, start_or_end: str):
        kwargs = {}
        kwargs["elements"] = getattr(
            self, f"{start_or_end}_arrowhead_drawing_elements"
        )()
        for group_attr_name in [
            "stroke",
            "stroke_width",
            "stroke_dasharray",
            "stroke_dashoffset",
            "fill",
            "transform",
            "fill",
        ]:
            arrowhead_attr_name = f"{start_or_end}_arrowhead_{group_attr_name}"
            kwargs[group_attr_name] = getattr(self, arrowhead_attr_name)
        group = momapy.drawing.Group(**kwargs)
        return group

    def _make_rotated_arrowhead_drawing_element(self, start_or_end: str):
        drawing_element = self._make_arrowhead_drawing_element(start_or_end)
        arrowhead_length = self._get_arrowhead_length(start_or_end)
        arrowhead_base = self._get_arrowhead_base(start_or_end)
        if start_or_end == "start":
            segment = self.segments[-1]
            segment = momapy.geometry.Segment(segment.p2, segment.p1)
        else:
            segment = self.segments[0]
        if arrowhead_length == 0:
            segment_coords = segment.to_shapely().coords
            p1 = momapy.geometry.Point.from_tuple(segment_coords[-2])
            p2 = momapy.geometry.Point.from_tuple(segment_coords[-1])
            line = momapy.geometry.Line(p1, p2)
        else:
            line = momapy.geometry.Line(arrowhead_base, segment.p2)
        angle = momapy.geometry.get_angle_to_horizontal_of_line(line)
        translation = momapy.geometry.Translation(
            arrowhead_base.x, arrowhead_base.y
        )
        rotation = momapy.geometry.Rotation(angle, arrowhead_base)
        drawing_element = drawing_element.transformed(translation).transformed(
            rotation
        )
        return drawing_element

    def _get_arrowhead_bbox(self, start_or_end: str):
        drawing_element = self._make_rotated_arrowhead_drawing_element(
            start_or_end
        )
        return drawing_element.bbox()

    def start_arrowhead_bbox(self):
        return self._get_arrowhead_bbox("start")

    def end_arrowhead_bbox(self):
        return self._get_arrowhead_bbox("end")

    def _make_path(self) -> momapy.drawing.Path:
        start_arrowhead_length = self.start_arrowhead_length()
        end_arrowhead_length = self.end_arrowhead_length()
        if len(self.segments) == 1:
            segment = (
                self.segments[0]
                .shortened(
                    self.start_shorten + start_arrowhead_length, "start"
                )
                .shortened(self.end_shorten + end_arrowhead_length, "end")
            )
            actions = [
                momapy.drawing.MoveTo(segment.p1),
                self._make_path_action_from_segment(segment),
            ]
        else:
            first_segment = self.segments[0].shortened(
                self.start_shorten + start_arrowhead_length, "start"
            )
            last_segment = self.segments[-1].shortened(
                self.end_shorten + end_arrowhead_length, "end"
            )
            actions = [
                momapy.drawing.MoveTo(first_segment.p1),
                self._make_path_action_from_segment(first_segment),
            ]
            for segment in self.segments[1:-1]:
                action = self._make_path_action_from_segment(segment)
                actions.append(action)
            actions.append(self._make_path_action_from_segment(last_segment))
        path = momapy.drawing.Path(
            stroke=self.path_stroke,
            stroke_width=self.path_stroke_width,
            stroke_dasharray=self.path_stroke_dasharray,
            stroke_dashoffset=self.path_stroke_dasharray,
            fill=self.path_fill,
            transform=self.path_transform,
            filter=self.path_filter,
            actions=actions,
        )
        return path

    def self_drawing_elements(self):
        start_arrowhead_drawing_element = self._make_arrowhead_drawing_element(
            "start"
        )
        end_arrowhead_drawing_element = self._make_arrowhead_drawing_element(
            "end"
        )
        start_arrowhead_length = start_arrowhead_drawing_element.bbox().width
        if math.isnan(start_arrowhead_length):
            start_arrowhead_length = 0
        end_arrowhead_length = end_arrowhead_drawing_element.bbox().width
        if math.isnan(end_arrowhead_length):
            end_arrowhead_length = 0
        drawing_elements = [
            self._make_path(),
            self._make_rotated_arrowhead_drawing_element("start"),
            self._make_rotated_arrowhead_drawing_element("end"),
        ]
        return drawing_elements


@dataclasses.dataclass(frozen=True, kw_only=True)
class Model(MapElement):
    @abc.abstractmethod
    def is_submodel(self, other):
        pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Layout(Node):
    pass

    def self_bbox(self):
        return momapy.geometry.Bbox(self.position, self.width, self.height)

    def border_drawing_elements(self):
        actions = [
            momapy.drawing.MoveTo(self.self_bbox().north_west()),
            momapy.drawing.LineTo(self.self_bbox().north_east()),
            momapy.drawing.LineTo(self.self_bbox().south_east()),
            momapy.drawing.LineTo(self.self_bbox().south_west()),
            momapy.drawing.ClosePath(),
        ]
        path = momapy.drawing.Path(actions=actions)
        return [path]

    def is_sublayout(self, other, flattened=False, unordered=False):
        def _is_sublist(list1, list2, unordered=False) -> bool:
            if not unordered:
                i = 0
                for elem1 in list1:
                    elem2 = list2[i]
                    while elem2 != elem1 and i < len(list2) - 1:
                        i += 1
                        elem2 = list2[i]
                    if not elem2 == elem1:
                        return False
                    i += 1
            else:
                dlist1 = collections.defaultdict(int)
                dlist2 = collections.defaultdict(int)
                for elem1 in list1:
                    dlist1[elem1] += 1
                for elem2 in list2:
                    dlist2[elem2] += 1
                for elem in dlist1:
                    if dlist1[elem] > dlist2[elem]:
                        return False
            return True

        if self.childless() != other.childless():
            return False
        if flattened:
            return _is_sublist(
                self.flattened()[1:],
                other.flattened()[1:],
                unordered=unordered,
            )
        return _is_sublist(
            self.children(), other.children(), unordered=unordered
        )

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

    def center(self):
        return self.bbox().center()


_MappingElementType: typing.TypeAlias = (
    tuple[ModelElement, ModelElement | None] | LayoutElement
)
_MappingKeyType: typing.TypeAlias = frozenset[_MappingElementType]
_MappingValueType: typing.TypeAlias = frozenset[_MappingKeyType]
_SingletonToSetMappingType: typing.TypeAlias = frozendict.frozendict[
    _MappingElementType, frozendict.frozendict[_MappingKeyType]
]
_SetToSetMappingType: typing.TypeAlias = frozendict.frozendict[
    _MappingKeyType, _MappingValueType
]


@dataclasses.dataclass(frozen=True, kw_only=True)
class LayoutModelMapping(collections.abc.Mapping):
    _singleton_to_set_mapping: _SingletonToSetMappingType = dataclasses.field(
        default_factory=frozendict.frozendict
    )
    _set_to_set_mapping: _SetToSetMappingType = dataclasses.field(
        default_factory=frozendict.frozendict
    )

    def __iter__(self):
        return iter(self._set_to_set_mapping)

    def __len__(self):
        return len(self._set_to_set_mapping)

    def __getitem__(
        self, key: ModelElement | _MappingElementType | _MappingKeyType
    ):
        return self.get_mapping(key=key, expand=True)

    def _prepare_model_element_key(self, key):
        return tuple([key, None])

    def _prepare_key(
        self, key: ModelElement | _MappingElementType | _MappingKeyType
    ):
        if isinstance(key, ModelElement):  # ModelElement
            key = frozenset([self._prepare_model_element_key(key)])
        elif isinstance(key, LayoutElement) or isinstance(
            key, tuple
        ):  # _MappingElementType
            key = frozenset([key])
        return key

    def get_mapping(
        self,
        key: ModelElement | _MappingElementType | _MappingKeyType,
        expand: bool = True,
        unpack: bool = False,
    ):
        if (
            isinstance(key, ModelElement)
            or isinstance(key, LayoutElement)
            or isinstance(key, tuple)
        ):  # MappingElementType
            if isinstance(key, ModelElement):  # ModelElementBuilder
                key = self._prepare_model_element_key(key)
            if expand:
                keys = self._singleton_to_set_mapping[key]
            else:
                keys = set([self._prepare_key(key)])
        else:
            keys = set([key])
        value = set([])
        for key in keys:
            value |= self._set_to_set_mapping[key]
        if unpack:
            if not value:
                raise ValueError(
                    f"could not unpack '{value}': result is empty"
                )
            for element in value:
                break
            if not element:
                raise ValueError(
                    f"could not unpack '{value}': result is empty"
                )
            for sub_element in element:
                break
            return sub_element

        return value

    def is_submapping(self, other):
        for left_element, right_elements in self._set_to_set_mapping.items():
            other_right_elements = other._set_to_set_mapping.get(left_element)
            if other_right_elements is None or not right_elements.issubset(
                other_right_elements
            ):
                return False
        return True


@dataclasses.dataclass(frozen=True, kw_only=True)
class Map(MapElement):
    model: Model
    layout: Layout
    layout_model_mapping: LayoutModelMapping

    def is_submap(self, other):
        return (
            self.model.is_submodel(other.model)
            and self.layout.is_sublayout(other.layout)
            and self.layout_model_mapping.is_submapping(
                other.layout_model_mapping
            )
        )

    def get_mapping(
        self,
        key: ModelElement | _MappingElementType | _MappingKeyType,
        expand: bool = True,
        unpack: bool = False,
    ):
        return self.layout_model_mapping.get_mapping(
            key=key, expand=expand, unpack=unpack
        )


class TupleBuilder(list, momapy.builder.Builder):
    _cls_to_build = tuple

    def build(
        self,
        inside_collections: bool = True,
        builder_to_object: dict[int, typing.Any] | None = None,
    ):
        if builder_to_object is not None:
            obj = builder_to_object.get(id(self))
            if obj is not None:
                return obj
        else:
            builder_to_object = {}
        obj = self._cls_to_build(
            [
                momapy.builder.object_from_builder(
                    builder=e,
                    inside_collections=inside_collections,
                    builder_to_object=builder_to_object,
                )
                for e in self
            ]
        )
        return obj

    @classmethod
    def from_object(
        cls,
        obj,
        inside_collections: bool = True,
        omit_keys: bool = True,
        object_to_builder: dict[int, momapy.builder.Builder] | None = None,
    ):
        if object_to_builder is not None:
            builder = object_to_builder.get(id(obj))
            if builder is not None:
                return builder
        else:
            object_to_builder = {}
        builder = cls(
            [
                momapy.builder.builder_from_object(
                    obj=e,
                    inside_collections=inside_collections,
                    object_to_builder=object_to_builder,
                )
                for e in obj
            ]
        )
        return builder


class FrozensetBuilder(set, momapy.builder.Builder):
    _cls_to_build = frozenset

    def build(
        self,
        inside_collections: bool = True,
        builder_to_object: dict[int, typing.Any] | None = None,
    ):
        if builder_to_object is not None:
            obj = builder_to_object.get(id(self))
            if obj is not None:
                return obj
        else:
            builder_to_object = {}
        obj = self._cls_to_build(
            [
                momapy.builder.object_from_builder(
                    builder=e,
                    inside_collections=inside_collections,
                    builder_to_object=builder_to_object,
                )
                for e in self
            ]
        )
        return obj

    @classmethod
    def from_object(
        cls,
        obj,
        inside_collections: bool = True,
        omit_keys: bool = True,
        object_to_builder: dict[int, momapy.builder.Builder] | None = None,
    ):
        if object_to_builder is not None:
            builder = object_to_builder.get(id(obj))
            if builder is not None:
                return builder
        else:
            object_to_builder = {}
        builder = cls(
            [
                momapy.builder.builder_from_object(
                    obj=e,
                    inside_collections=inside_collections,
                    object_to_builder=object_to_builder,
                )
                for e in obj
            ]
        )
        return builder


class FrozendictBuilder(dict, momapy.builder.Builder):
    _cls_to_build = frozendict.frozendict

    def build(
        self,
        inside_collections: bool = True,
        builder_to_object: dict[int, typing.Any] | None = None,
    ):
        if builder_to_object is not None:
            obj = builder_to_object.get(id(self))
            if obj is not None:
                return obj
        else:
            builder_to_object = {}
        obj = self._cls_to_build(
            [
                (
                    momapy.builder.object_from_builder(
                        builder=k,
                        inside_collections=inside_collections,
                        builder_to_object=builder_to_object,
                    ),
                    momapy.builder.object_from_builder(
                        builder=v,
                        inside_collections=inside_collections,
                        builder_to_object=builder_to_object,
                    ),
                )
                for k, v in self.items()
            ]
        )
        return obj

    @classmethod
    def from_object(
        cls,
        obj,
        inside_collections: bool = True,
        omit_keys: bool = True,
        object_to_builder: dict[int, momapy.builder.Builder] | None = None,
    ):
        if object_to_builder is not None:
            builder = object_to_builder.get(id(obj))
            if builder is not None:
                return builder
        else:
            object_to_builder = {}
        builder = cls(
            [
                (
                    (
                        momapy.builder.builder_from_object(
                            obj=k,
                            inside_collections=inside_collections,
                            omit_keys=omit_keys,
                            object_to_builder=object_to_builder,
                        ),
                        momapy.builder.builder_from_object(
                            obj=v,
                            inside_collections=inside_collections,
                            omit_keys=omit_keys,
                            object_to_builder=object_to_builder,
                        ),
                    )
                    if not omit_keys
                    else (
                        k,
                        momapy.builder.builder_from_object(
                            obj=v,
                            inside_collections=inside_collections,
                            omit_keys=omit_keys,
                            object_to_builder=object_to_builder,
                        ),
                    )
                )
                for k, v in self.items()
            ]
        )
        return builder


momapy.builder.register_builder(TupleBuilder)
momapy.builder.register_builder(FrozensetBuilder)
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
NodeBuilder = momapy.builder.get_or_make_builder_cls(Node)
ArcBuilder = momapy.builder.get_or_make_builder_cls(Arc)
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


LayoutBuilder = momapy.builder.get_or_make_builder_cls(
    Layout,
    builder_namespace={"new_element": _layout_builder_new_element},
)

_MappingElementBuilderType: typing.TypeAlias = (
    tuple[
        ModelElement | ModelElementBuilder,
        ModelElement | ModelElementBuilder | None,
    ]
    | LayoutElement
    | LayoutElementBuilder
)
_MappingKeyBuilderType: typing.TypeAlias = frozenset[
    _MappingElementBuilderType
]
_MappingValueBuilderType: typing.TypeAlias = FrozensetBuilder[
    _MappingKeyBuilderType
]
_SingletonToSetMappingBuilderType: typing.TypeAlias = FrozendictBuilder[
    _MappingElementBuilderType, FrozendictBuilder[_MappingKeyBuilderType]
]
_SetToSetMappingBuilderType: typing.TypeAlias = FrozendictBuilder[
    _MappingKeyBuilderType, _MappingValueBuilderType
]


@dataclasses.dataclass
class LayoutModelMappingBuilder(
    momapy.builder.Builder, collections.abc.Mapping
):
    _cls_to_build: typing.ClassVar[type] = LayoutModelMapping
    _singleton_to_set_mapping: _SingletonToSetMappingBuilderType = (
        dataclasses.field(default_factory=FrozendictBuilder)
    )
    _set_to_set_mapping: _SetToSetMappingBuilderType = dataclasses.field(
        default_factory=FrozendictBuilder
    )

    def __iter__(self):
        return iter(self._set_to_set_mapping)

    def __len__(self):
        return len(self._set_to_set_mapping)

    def __getitem__(
        self, key: ModelElement | _MappingElementBuilderType | _MappingKeyType
    ):
        return self.get_mapping(key=key, expand=True)

    def __setitem__(
        self,
        key: (
            ModelElement
            | ModelElementBuilder
            | _MappingElementBuilderType
            | _MappingKeyBuilderType
        ),
        value: (
            ModelElement
            | ModelElementBuilder
            | _MappingElementBuilderType
            | _MappingKeyBuilderType
            | _MappingValueBuilderType
        ),
    ):
        return self.set_mapping(key=key, value=value, reverse=True)

    def _prepare_model_element_key(self, key):
        return tuple([key, None])

    def _prepare_key(
        self,
        key: (
            ModelElement
            | ModelElementBuilder
            | _MappingElementBuilderType
            | _MappingKeyBuilderType
        ),
    ):
        if momapy.builder.isinstance_or_builder(
            key, ModelElement
        ):  # ModelElement(Builder)
            key = frozenset([self._prepare_model_element_key(key)])
        elif momapy.builder.isinstance_or_builder(
            key, LayoutElement
        ) or isinstance(
            key, tuple
        ):  # _MappingElementBuilderType
            key = frozenset([key])
        return key

    def _prepare_value(
        self,
        value: (
            ModelElement
            | ModelElementBuilder
            | _MappingElementBuilderType
            | _MappingKeyBuilderType
            | _MappingValueBuilderType
        ),
    ):
        value = self._prepare_key(
            value
        )  # ModelElement(Builder) | _MappingElementBuilderType to _MappingKeyBuilderType
        if isinstance(
            value, frozenset
        ):  # _MappingKeyBuilderType to _MappingValueBuilderType
            value = FrozensetBuilder([value])
        return value

    def _prepare_key_value(self, key, value):
        return self._prepare_key(key), self._prepare_value(value)

    def get_mapping(
        self,
        key: (
            ModelElement
            | ModelElementBuilder
            | _MappingElementBuilderType
            | _MappingKeyBuilderType
        ),
        expand: bool = True,
        unpack: bool = True,
    ):
        if (
            momapy.builder.isinstance_or_builder(key, ModelElement)
            or momapy.builder.isinstance_or_builder(key, LayoutElement)
            or isinstance(key, tuple)
        ):  # MappingElementBuilderType
            if momapy.builder.isinstance_or_builder(
                key, ModelElement
            ):  # ModelElementBuilder
                key = self._prepare_model_element_key(key)
            if expand:
                keys = self._singleton_to_set_mapping[key]
            else:
                keys = set([self._prepare_key(key)])
        else:
            keys = set([key])
        value = set([])
        for key in keys:
            value |= self._set_to_set_mapping[key]
        if unpack:
            if not value:
                raise ValueError(
                    f"could not unpack '{value}': result is empty"
                )
            for element in value:
                break
            if not element:
                raise ValueError(
                    f"could not unpack '{value}': result is empty"
                )
            for sub_element in element:
                break
            return sub_element

        return value

    def set_mapping(
        self,
        key: (
            ModelElement
            | ModelElementBuilder
            | _MappingElementBuilderType
            | _MappingKeyBuilderType
        ),
        value: (
            ModelElement
            | ModelElementBuilder
            | _MappingElementBuilderType
            | _MappingKeyBuilderType
            | _MappingValueBuilderType
        ),
        reverse: bool = True,
    ):
        key, value = self._prepare_key_value(key, value)
        for element in key:
            if element not in self._singleton_to_set_mapping:
                self._singleton_to_set_mapping[element] = FrozendictBuilder()
            self._singleton_to_set_mapping[element].add(key)
        self._set_to_set_mapping[key] = value
        if reverse:
            for rkey in value:
                self.add_mapping(key=rkey, value=key, reverse=False)

    def add_mapping(
        self,
        key: (
            ModelElement
            | ModelElementBuilder
            | _MappingElementBuilderType
            | _MappingKeyBuilderType
        ),
        value: (
            ModelElement
            | _MappingElementBuilderType
            | _MappingKeyBuilderType
            | _MappingValueBuilderType
        ),
        reverse: bool = True,
    ):
        key, value = self._prepare_key_value(key, value)
        for element in key:
            if element not in self._singleton_to_set_mapping:
                self._singleton_to_set_mapping[element] = FrozensetBuilder()
            self._singleton_to_set_mapping[element].add(key)
        if key not in self._set_to_set_mapping:
            self._set_to_set_mapping[key] = FrozensetBuilder()
        self._set_to_set_mapping[key] |= value
        if reverse:
            for rkey in value:
                self.add_mapping(key=rkey, value=key, reverse=False)

    def delete_mapping(
        self,
        key: (
            ModelElement
            | ModelElementBuilder
            | _MappingElementBuilderType
            | _MappingKeyBuilderType
        ),
        value: (
            ModelElement
            | ModelElementBuilder
            | _MappingElementBuilderType
            | _MappingKeyBuilderType
            | _MappingValueBuilderType
        ),
        reverse: bool = True,
    ):
        key = self._prepare_key(key)
        if value is not None:
            value = self._prepare_value(value)
            deleted = value
            self._set_to_set_mapping[key] -= value
            if not self._set_to_set_mapping[key]:
                del self._set_to_set_mapping[key]
        else:
            deleted = self._set_to_set_mapping[key]
            del self._set_to_set_mapping[key]
        if key not in self._set_to_set_mapping:
            for element in key:
                self._singleton_to_set_mapping[element].remove(key)
                if not self._singleton_to_set_mapping[element]:
                    del self._singleton_to_set_mapping[element]
        if reverse:
            for rkey in deleted:
                self.delete_mapping(key=rkey, value=key, reverse=False)

    def is_submapping(self, other):
        for left_element, right_elements in self._set_to_set_mapping.items():
            other_right_elements = other._set_to_set_mappin.get(left_element)
            if other_right_elements is None or not right_elements.issubset(
                other_right_elements
            ):
                return False
        return True

    def build(
        self,
        inside_collections: bool = True,
        builder_to_object: dict[int, typing.Any] | None = None,
    ):
        _set_to_set_mapping = momapy.builder.object_from_builder(
            builder=self._set_to_set_mapping,
            inside_collections=True,
            builder_to_object=builder_to_object,
        )
        _singleton_to_set_mapping = momapy.builder.object_from_builder(
            builder=self._singleton_to_set_mapping,
            inside_collections=True,
            builder_to_object=builder_to_object,
        )
        return self._cls_to_build(
            _singleton_to_set_mapping=_singleton_to_set_mapping,
            _set_to_set_mapping=_set_to_set_mapping,
        )

    @classmethod
    def from_object(
        cls,
        obj,
        inside_collections: bool = True,
        omit_keys: bool = True,
        object_to_builder: dict[int, momapy.builder.Builder] | None = None,
    ):
        _set_to_set_mapping = FrozendictBuilder()
        for key in obj._set_to_set_mapping:
            builder_key = frozenset(
                [
                    (
                        momapy.builder.builder_from_object(
                            obj=e,
                            inside_collections=inside_collections,
                            omit_keys=omit_keys,
                            object_to_builder=object_to_builder,
                        )
                        if not isinstance(e, tuple)
                        else tuple(
                            [
                                momapy.builder.builder_from_object(
                                    obj=ee,
                                    inside_collections=inside_collections,
                                    omit_keys=omit_keys,
                                    object_to_builder=object_to_builder,
                                )
                                for ee in e
                            ]
                        )
                    )
                    for e in key
                ]
            )
            builder_value = FrozensetBuilder(
                [
                    frozenset(
                        [
                            (
                                momapy.builder.builder_from_object(
                                    obj=e,
                                    inside_collections=inside_collections,
                                    omit_keys=omit_keys,
                                    object_to_builder=object_to_builder,
                                )
                                if not isinstance(e, tuple)
                                else tuple(
                                    [
                                        momapy.builder.builder_from_object(
                                            obj=ee,
                                            inside_collections=inside_collections,
                                            omit_keys=omit_keys,
                                            object_to_builder=object_to_builder,
                                        )
                                        for ee in e
                                    ]
                                )
                            )
                            for e in k
                        ]
                    )
                    for k in obj._set_to_set_mapping[key]
                ]
            )
            _set_to_set_mapping[builder_key] = builder_value
        _singleton_to_set_mapping = FrozendictBuilder()
        for key in _set_to_set_mapping:
            for element in key:
                if element not in _singleton_to_set_mapping:
                    _singleton_to_set_mapping[element] = FrozensetBuilder()
                _singleton_to_set_mapping[element].add(key)
        return cls(
            _singleton_to_set_mapping=_singleton_to_set_mapping,
            _set_to_set_mapping=_set_to_set_mapping,
        )


momapy.builder.register_builder(LayoutModelMappingBuilder)


@abc.abstractmethod
def _map_builder_new_model(self, *args, **kwargs) -> ModelBuilder:
    pass


@abc.abstractmethod
def _map_builder_new_layout(self, *args, **kwargs) -> LayoutBuilder:
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


def _map_builder_add_mapping(
    self,
    key: (
        ModelElement
        | ModelElementBuilder
        | _MappingElementBuilderType
        | _MappingKeyBuilderType
    ),
    value: (
        ModelElement
        | _MappingElementBuilderType
        | _MappingKeyBuilderType
        | _MappingValueBuilderType
    ),
    reverse: bool = True,
):
    self.layout_model_mapping.add_mapping(
        key=key, value=value, reverse=reverse
    )


def _map_builder_get_mapping(
    self,
    key: (
        ModelElement
        | ModelElementBuilder
        | _MappingElementBuilderType
        | _MappingKeyBuilderType
    ),
    expand: bool = True,
    unpack: bool = True,
):
    return self.layout_model_mapping.get_mapping(
        key=key, expand=expand, unpack=unpack
    )


MapBuilder = momapy.builder.get_or_make_builder_cls(
    Map,
    builder_namespace={
        "new_model": _map_builder_new_model,
        "new_layout": _map_builder_new_layout,
        "new_layout_model_mapping": _map_builder_new_layout_model_mapping,
        "new_model_element": _map_builder_new_model_element,
        "new_layout_element": _map_builder_new_layout_element,
        "add_mapping": _map_builder_add_mapping,
    },
)
