"""Base classes for core components defining maps and their elements"""

import momapy.drawing
import momapy.geometry
import momapy.coloring
import momapy.utils
import momapy._pango
import momapy.builder
import abc
import dataclasses
import typing
import enum
import math
import copy
import shapely
import frozendict
import functools
import operator


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
class MapElement:
    """Base class for map elements"""

    id_: str = dataclasses.field(
        hash=False,
        compare=False,
        default_factory=momapy.utils.make_uuid4_as_str,
        metadata={
            "description": """The id of the map element. This id is purely for the user to keep track
    of the element, it does not need to be unique and is not part of the
    identity of the element, i.e., it is not considered when testing for
    equality between two map elements or when hashing the map element"""
        },
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModelElement(MapElement):
    """Base class for model elements"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LayoutElement(MapElement, abc.ABC):
    """Abstract base class for layout elements"""

    @abc.abstractmethod
    def bbox(self) -> momapy.geometry.Bbox:
        """Compute and return the bounding box of the layout element"""
        pass

    @abc.abstractmethod
    def drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        """Return the drawing elements of the layout element"""
        pass

    @abc.abstractmethod
    def children(self) -> list["LayoutElement"]:
        """Return the children of the layout element"""
        pass

    @abc.abstractmethod
    def childless(self) -> typing.Self:
        """Return a copy of the layout element with no children"""
        pass

    def descendants(self) -> list["LayoutElement"]:
        """Return the descendants of the layout element"""
        descendants = []
        for child in self.children():
            descendants.append(child)
            descendants += child.descendants()
        return descendants

    def flattened(self) -> list["LayoutElement"]:
        """Return a list containing copy of the layout element with no children and all its descendants with no children"""
        flattened = [self.childless()]
        for child in self.children():
            flattened += child.flattened()
        return flattened

    def equals(
        self, other: "LayoutElement", flattened: bool = False, unordered: bool = False
    ) -> bool:
        """Return `true` if the layout element is equal to another layout element, `false` otherwise"""
        if type(self) is type(other):
            if not flattened:
                return self == other
            else:
                if not unordered:
                    return self.flattened() == other.flattened()
                else:
                    return set(self.flattened()) == set(other.flattened())
        return False

    def contains(self, other: "LayoutElement") -> bool:
        """Return `true` if another layout element is a descendant of the layout element, `false` otherwise"""
        return other in self.descendants()

    def to_shapely(self, to_polygons: bool = False) -> shapely.GeometryCollection:
        """Return a shapely collection of geometries reproducing the drawing elements of the layout element"""
        geom_collection = []
        for drawing_element in self.drawing_elements():
            geom_collection += drawing_element.to_shapely(to_polygons=to_polygons).geoms
        return shapely.GeometryCollection(geom_collection)

    def anchor_point(self, anchor_name: str) -> momapy.geometry.Point:
        """Return an anchor point of the layout element"""
        return getattr(self, anchor_name)()


@dataclasses.dataclass(frozen=True, kw_only=True)
class TextLayout(LayoutElement):
    """Class for text layouts"""

    text: str = dataclasses.field(
        metadata={"description": "The text of the text layout"}
    )
    font_family: str = dataclasses.field(
        default=momapy.drawing.get_initial_value("font_family"),
        metadata={"description": "The font family of the text layout"},
    )
    font_size: float = dataclasses.field(
        default=momapy.drawing.get_initial_value("font_size"),
        metadata={"description": "The font size of the text layout"},
    )
    font_style: momapy.drawing.FontStyle = dataclasses.field(
        default=momapy.drawing.get_initial_value("font_style"),
        metadata={"description": "The font style of the text layout"},
    )
    font_weight: momapy.drawing.FontWeight | int = dataclasses.field(
        default=momapy.drawing.get_initial_value("font_weight"),
        metadata={"description": "The font weight of the text layout"},
    )
    position: momapy.geometry.Point = dataclasses.field(
        metadata={"description": "The position of the text layout"}
    )
    width: float | None = dataclasses.field(
        default=None, metadata={"description": "The width of the text layout"}
    )
    height: float | None = dataclasses.field(
        default=None, metadata={"description": "The height of the text layout"}
    )
    horizontal_alignment: HAlignment = dataclasses.field(
        default=HAlignment.LEFT,
        metadata={"description": "The horizontal alignment of the text layout"},
    )
    vertical_alignment: VAlignment = dataclasses.field(
        default=VAlignment.TOP,
        metadata={"description": "The vertical alignment of the text layout"},
    )
    justify: bool = dataclasses.field(
        default=False,
        metadata={"description": "Whether to justify the text or not"},
    )
    fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The text fill color of the text layout"},
        )
    )
    filter: momapy.drawing.NoneValueType | momapy.drawing.Filter | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The filter of the text layout"},
        )
    )  # should be a tuple of filters to follow SVG (to be implemented)
    stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The text stroke color of the text layout"},
        )
    )
    stroke_dasharray: tuple[float] | None = dataclasses.field(
        default=None,
        metadata={"description": "The text stroke dasharray of the text layout"},
    )
    stroke_dashoffset: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The text stroke dashoffset of the text layout"},
    )
    stroke_width: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The text stroke width of the text layout"},
    )
    text_anchor: momapy.drawing.TextAnchor | None = dataclasses.field(
        default=None,
        metadata={"description": "The text anchor of the text layout"},
    )
    transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = dataclasses.field(
        default=None,
        metadata={"description": "The transform of the text layout"},
    )

    @property
    def x(self) -> float:
        """Return the y coordinate of the text layout"""
        return self.position.x

    @property
    def y(self) -> float:
        """Return the y coordinate of the text layout"""
        return self.position.y

    def _make_pango_layout(self):
        pango_layout = momapy._pango.make_pango_layout(
            font_family=self.font_family,
            font_size=self.font_size,
            font_style=self.font_style,
            font_weight=self.font_weight,
            text=self.text,
            justify=self.justify,
            width=self.width,
            height=self.height,
        )
        return pango_layout

    def _get_tx_and_ty(self, pango_layout):
        _, pango_layout_extents = pango_layout.get_pixel_extents()
        if self.width is not None:
            tx = self.x - self.width / 2
        else:
            tx = self.x - (pango_layout_extents.x + pango_layout_extents.width / 2)
        if self.height is not None:
            if self.vertical_alignment == VAlignment.TOP:
                ty = self.y - self.height / 2
            elif self.vertical_alignment == VAlignment.BOTTOM:
                ty = self.y + self.height / 2 - pango_layout_extents.height
            else:
                ty = self.y - (pango_layout_extents.y + pango_layout_extents.height / 2)
        else:
            ty = self.y - (pango_layout_extents.y + pango_layout_extents.height / 2)
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

    def logical_bbox(self) -> momapy.geometry.Bbox:
        """Return the logical bounding box of the text layout"""
        pango_layout = self._make_pango_layout()
        _, pango_layout_extents = pango_layout.get_pixel_extents()
        return self._get_bbox(pango_layout, pango_layout_extents)

    def ink_bbox(self) -> momapy.geometry.Bbox:
        """Return the ink bounding box of the text layout"""
        pango_layout = self._make_pango_layout()
        pango_layout_extents, _ = pango_layout.get_pixel_extents()
        return self._get_bbox(pango_layout, pango_layout_extents)

    def drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        """Return the drawing elements of the text layout"""
        drawing_elements = []
        pango_layout = self._make_pango_layout()
        pango_layout_iter = pango_layout.get_iter()
        tx, ty = self._get_tx_and_ty(pango_layout)
        done = False
        while not done:
            pango_line = pango_layout_iter.get_line()
            line_text, pos = momapy._pango.get_pango_line_text_and_initial_pos(
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

    def children(self) -> list[LayoutElement]:
        """Return the children of the text layout.
        The text layout has no children, so return an empty list"""
        return []

    def childless(self) -> typing.Self:
        """Return a copy of the text layout with no children.
        The text layout has no children, so return a copy of the text layout
        """
        return copy.deepcopy(self)

    def north_west(self) -> momapy.geometry.Point:
        """Return the north west anchor of the text layout"""
        return self.bbox().north_west()

    def north_north_west(self) -> momapy.geometry.Point:
        """Return the north north west anchor of the text layout"""
        return self.bbox().north_north_west()

    def north(self) -> momapy.geometry.Point:
        """Return the north anchor of the text layout"""
        return self.bbox().north()

    def north_north_east(self) -> momapy.geometry.Point:
        """Return the north north east anchor of the text layout"""
        return self.bbox().north_north_east()

    def north_east(self) -> momapy.geometry.Point:
        """Return the north east anchor of the text layout"""
        return self.bbox().north_east()

    def east_north_east(self) -> momapy.geometry.Point:
        """Return the east north east anchor of the text layout"""
        return self.bbox().east_north_east()

    def east(self) -> momapy.geometry.Point:
        """Return the east anchor of the text layout"""
        return self.bbox().east()

    def east_south_east(self) -> momapy.geometry.Point:
        """Return the east south east anchor of the text layout"""
        return self.bbox().east_south_east()

    def south_east(self) -> momapy.geometry.Point:
        """Return the south east anchor of the text layout"""
        return self.bbox().south_east()

    def south_south_east(self) -> momapy.geometry.Point:
        """Return the south south east anchor of the text layout"""
        return self.bbox().south_south_east()

    def south(self) -> momapy.geometry.Point:
        """Return the south anchor of the text layout"""
        return self.bbox().south()

    def south_south_west(self) -> momapy.geometry.Point:
        """Return the south south west anchor of the text layout"""
        return self.bbox().south_south_west()

    def south_west(self) -> momapy.geometry.Point:
        """Return the south west anchor of the text layout"""
        return self.bbox().south_west()

    def west_south_west(self) -> momapy.geometry.Point:
        """Return the west south west anchor of the text layout"""
        return self.bbox().west_south_west()

    def west(self) -> momapy.geometry.Point:
        """Return the west anchor of the text layout"""
        return self.bbox().west()

    def west_north_west(self) -> momapy.geometry.Point:
        """Return the west north west anchor of the text layout"""
        return self.bbox().west_north_west()

    def bbox(self) -> momapy.geometry.Bbox:
        """Compute and return the bounding box of the layout element"""
        return self.ink_bbox()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Shape(LayoutElement):
    """Class for basic shapes. The shape is the most simple layout element.
    It has no children."""

    def childless(self) -> typing.Self:
        """Return a copy of the shape with no children.
        A shape has no children, so return a copy of the shape"""
        return copy.deepcopy(self)

    def children(self) -> list[LayoutElement]:
        """Return the children of the shape.
        A shape has no children, so return an empty list"""
        return []

    def bbox(self) -> momapy.geometry.Bbox:
        """Compute and return the bounding box of the shape"""
        bounds = self.to_shapely().bounds
        return momapy.geometry.Bbox.from_bounds(bounds)


@dataclasses.dataclass(frozen=True, kw_only=True)
class GroupLayout(LayoutElement):
    """Base class for group layouts. A group layout is a layout element grouping other layout elements.
    It has its own drawing elements and set of children (called self drawing elements and self children, respectively).
    The drawing elements of a group layout is a group drawing element formed of its self drawing elements and those of its children
    """

    layout_elements: tuple[LayoutElement] = dataclasses.field(
        default_factory=tuple,
        metadata={
            "description": "The sub-layout elements of the group layout. These are part of the children of the group layout"
        },
    )
    group_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The fill color of the group layout"},
        )
    )
    group_fill_rule: momapy.drawing.FillRule | None = dataclasses.field(
        default=None,
        metadata={"description": "The fill rule of the group layout"},
    )
    group_filter: momapy.drawing.NoneValueType | momapy.drawing.Filter | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The filter of the group layout"},
        )
    )  # should be a tuple of filters to follow SVG (to be implemented)
    group_font_family: str | None = dataclasses.field(
        default=None,
        metadata={"description": "The font family of the group layout"},
    )
    group_font_size: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The font size of the group layout"},
    )
    group_font_style: momapy.drawing.FontStyle | None = dataclasses.field(
        default=None,
        metadata={"description": "The font style of the group layout"},
    )
    group_font_weight: momapy.drawing.FontWeight | float | None = dataclasses.field(
        default=None,
        metadata={"description": "The font weight of the group layout"},
    )
    group_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The stroke color of the group layout"},
        )
    )
    group_stroke_dasharray: tuple[float, ...] | None = dataclasses.field(
        default=None,
        metadata={"description": "The stroke dasharray of the group layout"},
    )
    group_stroke_dashoffset: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The stroke dashoffset of the group layout"},
    )
    group_stroke_width: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The stroke width of the group layout"},
    )
    group_text_anchor: momapy.drawing.TextAnchor | None = dataclasses.field(
        default=None,
        metadata={"description": "The text anchor of the group layout"},
    )
    group_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = dataclasses.field(
        default=None,
        metadata={"description": "The transform of the group layout"},
    )

    def self_to_shapely(self) -> shapely.GeometryCollection:
        """Compute and return a shapely collection of geometries reproducing the self drawing elements of the group layout"""
        return momapy.drawing.drawing_elements_to_shapely(self.drawing_elements())

    def self_bbox(self) -> momapy.geometry.Bbox:
        """Compute and return the bounding box of the self drawing element of the group layout"""
        bounds = self.self_to_shapely().bounds
        return momapy.geometry.Bbox.from_bounds(bounds)

    def bbox(self) -> momapy.geometry.Bbox:
        """Compute and return the bounding box of the group layout element"""
        self_bbox = self.self_bbox()
        bboxes = [child.bbox() for child in self.children()]
        min_x = self_bbox.north_west().x
        min_y = self_bbox.north_west().y
        max_x = self_bbox.south_east().x
        max_y = self_bbox.south_east().y
        for bbox in bboxes:
            if bbox.north_west().x < min_x:
                min_x = bbox.north_west().x
            if bbox.north_west().y < min_y:
                min_y = bbox.north_west().y
            if bbox.south_east().x > max_x:
                max_x = bbox.south_east().x
            if bbox.south_east().y > max_y:
                max_y = bbox.south_east().y
        bbox = momapy.geometry.Bbox(
            momapy.geometry.Point(min_x / 2 + max_x / 2, min_y / 2 + max_y / 2),
            max_x - min_x,
            max_y - min_y,
        )
        return bbox

    @abc.abstractmethod
    def self_drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        """Return the self drawing elements of the group layout"""
        pass

    @abc.abstractmethod
    def self_children(self) -> list[LayoutElement]:
        """Return the self children of the group layout"""
        pass

    def drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        """Return the drawing elements of the group layout.
        The returned drawing elements are a group drawing element formed of the self drawing elements of the group layout and the drawing elements of its children
        """
        drawing_elements = self.self_drawing_elements()
        for child in self.children():
            if child is not None:
                drawing_elements += child.drawing_elements()
        group = momapy.drawing.Group(
            class_=f"{type(self).__name__}_group",
            elements=tuple(drawing_elements),
            id_=f"{self.id_}_group",
            fill=self.group_fill,
            fill_rule=self.group_fill_rule,
            filter=self.group_filter,
            font_family=self.group_font_family,
            font_size=self.group_font_size,
            font_style=self.group_font_style,
            font_weight=self.group_font_weight,
            stroke=self.group_stroke,
            stroke_dasharray=self.group_stroke_dasharray,
            stroke_dashoffset=self.group_stroke_dashoffset,
            stroke_width=self.group_stroke_width,
            text_anchor=self.group_text_anchor,
            transform=self.group_transform,
        )
        return [group]

    def children(self) -> list[LayoutElement]:
        """Return the children of the group layout.
        These are the self children of the group layout (returned by the `self_children` method) and the other children of the group layout (given by the `layout_elements` attribute)
        """
        return self.self_children() + list(self.layout_elements)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Node(GroupLayout):
    """Class for nodes. A node is a layout element with a `position`, a `width`, a `height` and an optional `label`."""

    fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The fill color of the node"},
        )
    )
    filter: momapy.drawing.NoneValueType | momapy.drawing.Filter | None = (
        dataclasses.field(
            default=None, metadata={"description": "The filter of the node"}
        )
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the node"}
    )
    label: TextLayout | None = dataclasses.field(
        default=None, metadata={"description": "The label of the node"}
    )
    position: momapy.geometry.Point = dataclasses.field(
        metadata={"description": "The position of the node"}
    )
    stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The stroke color of the node"},
        )
    )
    stroke_dasharray: tuple[float, ...] | None = dataclasses.field(
        default=None,
        metadata={"description": "The stroke dasharray of the node"},
    )
    stroke_dashoffset: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The stroke dashoffset of the node"},
    )
    stroke_width: float | None = dataclasses.field(
        default=None, metadata={"description": "The stroke width of the node"}
    )
    transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = dataclasses.field(
        default=None, metadata={"description": "The transform of the node"}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width width of the node"}
    )

    @property
    def x(self) -> float:
        """Return the x coordinate of the node"""
        return self.position.x

    @property
    def y(self) -> float:
        """Return the y coordinate of the node"""
        return self.position.y

    @abc.abstractmethod
    def _border_drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        pass

    def self_drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        """Return the node's own drawing elements"""
        drawing_elements = self._border_drawing_elements()
        group = momapy.drawing.Group(
            class_=type(self).__name__,
            elements=tuple(drawing_elements),
            fill=self.fill,
            filter=self.filter,
            id_=self.id_,
            stroke=self.stroke,
            stroke_dasharray=self.stroke_dasharray,
            stroke_dashoffset=self.stroke_dashoffset,
            stroke_width=self.stroke_width,
            transform=self.transform,
        )
        return [group]

    def self_children(self) -> list[LayoutElement]:
        """Return the self children of the node. A node has unique child that is its label"""
        if self.label is not None:
            return [self.label]
        return []

    def size(self) -> tuple[float, float]:
        """Return the size of the node"""
        return (self.width, self.height)

    def north_west(self) -> momapy.geometry.Point:
        """Return the north west anchor of the node"""
        line = momapy.geometry.Line(
            self.center(), self.center() - (self.width / 2, self.height / 2)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def north_north_west(self) -> momapy.geometry.Point:
        """Return the north north west anchor of the node"""
        line = momapy.geometry.Line(
            self.center(), self.center() - (self.width / 4, self.height / 2)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def north(self) -> momapy.geometry.Point:
        """Return the north anchor of the node"""
        return self.self_angle(90)

    def north_north_east(self) -> momapy.geometry.Point:
        """Return the north north east anchor of the node"""
        line = momapy.geometry.Line(
            self.center(), self.center() + (self.width / 4, -self.height / 2)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def north_east(self) -> momapy.geometry.Point:
        """Return the north east anchor of the node"""
        line = momapy.geometry.Line(
            self.center(), self.center() + (self.width / 2, -self.height / 2)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def east_north_east(self) -> momapy.geometry.Point:
        """Return the east north east anchor of the node"""
        line = momapy.geometry.Line(
            self.center(), self.center() + (self.width / 2, -self.height / 4)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def east(self) -> momapy.geometry.Point:
        """Return the east anchor of the node"""
        return self.self_angle(0)

    def east_south_east(self) -> momapy.geometry.Point:
        """Return the east south east west anchor of the node"""
        line = momapy.geometry.Line(
            self.center(), self.center() + (self.width / 2, self.height / 4)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def south_east(self) -> momapy.geometry.Point:
        """Return the south east anchor of the node"""
        line = momapy.geometry.Line(
            self.center(), self.center() + (self.width / 2, self.height / 2)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def south_south_east(self) -> momapy.geometry.Point:
        """Return the south south east anchor of the node"""
        line = momapy.geometry.Line(
            self.center(), self.center() + (self.width / 4, self.height / 2)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def south(self) -> momapy.geometry.Point:
        """Return the south anchor of the node"""
        return self.self_angle(270)

    def south_south_west(self) -> momapy.geometry.Point:
        """Return the south south west anchor of the node"""
        line = momapy.geometry.Line(
            self.center(), self.center() + (-self.width / 4, self.height / 2)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def south_west(self) -> momapy.geometry.Point:
        """Return the south west anchor of the node"""
        line = momapy.geometry.Line(
            self.center(), self.center() + (-self.width / 2, self.height / 2)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def west_south_west(self) -> momapy.geometry.Point:
        """Return the west south west anchor of the node"""
        line = momapy.geometry.Line(
            self.center(), self.center() + (-self.width / 2, self.height / 4)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def west(self) -> momapy.geometry.Point:
        """Return the west anchor of the node"""
        return self.self_angle(180)

    def west_north_west(self) -> momapy.geometry.Point:
        """Return the west north west anchor of the node"""
        line = momapy.geometry.Line(
            self.center(), self.center() - (self.width / 2, self.height / 4)
        )
        angle = -momapy.geometry.get_angle_to_horizontal_of_line(line)
        return self.self_angle(angle, unit="radians")

    def center(self) -> momapy.geometry.Point:
        """Return the center anchor of the node"""
        return self.position

    def label_center(self) -> momapy.geometry.Point:
        """Return the label center anchor of the node"""
        return self.position

    def self_border(self, point: momapy.geometry.Point) -> momapy.geometry.Point:
        """Return the point on the border of the node that intersects the self drawing elements of the node with the line formed of the center anchor point of the node and the given point.
        When there are multiple intersection points, the one closest to the given point is returned
        """
        return momapy.drawing.get_drawing_elements_border(
            drawing_elements=self.self_drawing_elements(),
            point=point,
            center=self.center(),
        )

    def border(self, point: momapy.geometry.Point) -> momapy.geometry.Point:
        """Return the point on the border of the node that intersects the drawing elements of the node with the line formed of the center anchor point of the node and the given point.
        When there are multiple intersection points, the one closest to the given point is returned
        """
        return momapy.drawing.get_drawing_elements_border(
            drawing_elements=self.drawing_elements(),
            point=point,
            center=self.center(),
        )

    def self_angle(
        self,
        angle: float,
        unit: typing.Literal["degrees", "radians"] = "degrees",
    ) -> momapy.geometry.Point:
        """Return the point on the border of the node that intersects the self drawing elements of the node with the line passing through the center anchor point of the node and at a given angle from the horizontal."""
        return momapy.drawing.get_drawing_elements_angle(
            drawing_elements=self.self_drawing_elements(),
            angle=angle,
            unit=unit,
            center=self.center(),
        )

    def angle(
        self,
        angle: float,
        unit: typing.Literal["degrees", "radians"] = "degrees",
    ) -> momapy.geometry.Point:
        """Return the point on the border of the node that intersects the drawing elements of the node with the line passing through the center anchor point of the node and at a given angle from the horizontal."""
        return momapy.drawing.get_drawing_elements_angle(
            drawing_elements=self.drawing_elements(),
            angle=angle,
            unit=unit,
            center=self.center(),
        )

    def childless(self) -> typing.Self:
        """Return a copy of the node with no children"""
        return dataclasses.replace(self, label=None, layout_elements=tuple([]))


@dataclasses.dataclass(frozen=True, kw_only=True)
class Arc(GroupLayout):
    """Base class for arcs"""

    end_shorten: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The length the end of the arc will be shorten by"},
    )
    fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        dataclasses.field(
            default=None, metadata={"description": "The fill color of the arc"}
        )
    )
    filter: momapy.drawing.NoneValueType | momapy.drawing.Filter | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The fill filter of the arc"},
        )
    )
    path_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The path fill color of the arc"},
        )
    )
    path_filter: momapy.drawing.NoneValueType | momapy.drawing.Filter | None = (
        dataclasses.field(
            default=None, metadata={"description": "The path filter of the arc"}
        )
    )
    path_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The path stroke color of the arc"},
        )
    )
    path_stroke_dasharray: tuple[float, ...] | None = dataclasses.field(
        default=None,
        metadata={"description": "The path stroke dasharray of the arc"},
    )
    path_stroke_dashoffset: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The path stroke dashoffset of the arc"},
    )
    path_stroke_width: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The path stroke width of the arc"},
    )
    path_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = dataclasses.field(
        default=None, metadata={"description": "The path transform of the arc"}
    )
    stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The stroke color of the arc"},
        )
    )
    stroke_dasharray: momapy.drawing.NoneValueType | tuple[float] | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The stroke dasharray of the arc"},
        )
    )
    stroke_dashoffset: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The stroke dashoffset of the arc"},
    )
    stroke_width: float | None = dataclasses.field(
        default=None, metadata={"description": "The stroke width of the arc"}
    )
    segments: tuple[
        momapy.geometry.Segment
        | momapy.geometry.BezierCurve
        | momapy.geometry.EllipticalArc
    ] = dataclasses.field(
        default_factory=tuple,
        metadata={"description": "The path segments of the arc"},
    )
    source: LayoutElement | None = dataclasses.field(
        default=None, metadata={"description": "The source of the arc"}
    )
    start_shorten: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The length the start of the arc will be shorten by"},
    )
    target: LayoutElement | None = dataclasses.field(
        default=None, metadata={"description": "The target of the arc"}
    )
    transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = dataclasses.field(
        default=None, metadata={"description": "The transform of the arc"}
    )

    def self_children(self) -> list[LayoutElement]:
        """Return the self children of the arc"""
        return []

    def points(self) -> list[momapy.geometry.Point]:
        """Return the points of the arc path"""
        points = []
        for segment in self.segments:
            points.append(segment.p1)
        points.append(segment.p2)
        return points

    def length(self):
        """Return the total length of the arc path"""
        return sum([segment.length() for segment in self.segments])

    def start_point(self) -> momapy.geometry.Point:
        """Return the starting point of the arc"""
        return self.points()[0]

    def end_point(self) -> momapy.geometry.Point:
        """Return the ending point of the arc"""
        return self.points()[-1]

    def childless(self) -> typing.Self:
        """Return a copy of the arc with no children"""
        return dataclasses.replace(self, layout_elements=tuple([]))

    def fraction(self, fraction: float) -> tuple[momapy.geometry.Point, float]:
        """Return the position and angle on the arc at a given fraction (of the total arc length)"""
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
        if momapy.builder.isinstance_or_builder(segment, momapy.geometry.Segment):
            path_action = momapy.drawing.LineTo(segment.p2)
        elif momapy.builder.isinstance_or_builder(segment, momapy.geometry.BezierCurve):
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
    """Base class for single-headed arcs. A single-headed arc is formed of a path and a unique arrowhead at its end"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The arrowhead fill color of the arc"},
        )
    )
    arrowhead_filter: momapy.drawing.NoneValueType | momapy.drawing.Filter | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The arrowhead filter of the arc"},
        )
    )
    arrowhead_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The arrowhead stroke color of the arc"},
        )
    )
    arrowhead_stroke_dasharray: tuple[float, ...] | None = dataclasses.field(
        default=None,
        metadata={"description": "The arrowhead stroke dasharray of the arc"},
    )
    arrowhead_stroke_dashoffset: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The arrowhead stroke dashoffset of the arc"},
    )
    arrowhead_stroke_width: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The arrowhead stroke width of the arc"},
    )
    arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = dataclasses.field(
        default=None,
        metadata={"description": "The arrowhead transform of the arc"},
    )

    def arrowhead_length(self) -> float:
        """Return the length of the single-headed arc arrowhead"""
        bbox = momapy.drawing.get_drawing_elements_bbox(
            self._arrowhead_border_drawing_elements()
        )
        if math.isnan(bbox.width):
            return 0.0
        return bbox.east().x

    def arrowhead_tip(self) -> momapy.geometry.Point:
        """Return the arrowhead tip anchor point of the single-headed arc"""
        segment = self.segments[-1]
        segment_length = segment.length()
        if segment_length == 0:
            return segment.p2
        fraction = 1 - self.end_shorten / segment_length
        return segment.get_position_at_fraction(fraction)

    def arrowhead_base(self) -> momapy.geometry.Point:
        """Return the arrowhead base anchor point of the single-headed arc"""
        arrowhead_length = self.arrowhead_length()
        segment = self.segments[-1]
        segment_length = segment.length()
        if segment_length == 0:
            return self.arrowhead_tip() - (arrowhead_length, 0)
        fraction = 1 - (arrowhead_length + self.end_shorten) / segment_length
        return segment.get_position_at_fraction(fraction)

    def arrowhead_bbox(self) -> momapy.geometry.Bbox:
        """Return the bounding box of the single-headed arc arrowhead"""
        return momapy.drawing.get_drawing_elements_bbox(
            self.arrowhead_drawing_elements()
        )

    def arrowhead_border(self, point) -> momapy.geometry.Point:
        """Return the point at the intersection of the drawing elements of the single-headed arc arrowhead and the line going through the center of these drawing elements and the given point.
        When there are multiple intersection points, the one closest to the given point is returned
        """

        point = momapy.drawing.get_drawing_elements_border(
            self.arrowhead_drawing_elements(), point
        )
        if point is None:
            return self.arrowhead_tip()
        return point

    @abc.abstractmethod
    def _arrowhead_border_drawing_elements(
        self,
    ) -> list[momapy.drawing.DrawingElement]:
        pass

    def _get_arrowhead_transformation(self):
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
        translation = momapy.geometry.Translation(arrowhead_base.x, arrowhead_base.y)
        rotation = momapy.geometry.Rotation(angle, arrowhead_base)
        return rotation * translation

    def arrowhead_drawing_elements(
        self,
    ) -> list[momapy.drawing.DrawingElement]:
        """Return the drawing elements of the single-headed arc arrowhead"""
        drawing_elements = self._arrowhead_border_drawing_elements()
        group = momapy.drawing.Group(
            class_=f"{type(self).__name__}_arrowhead",
            elements=tuple(drawing_elements),
            fill=self.arrowhead_fill,
            filter=self.arrowhead_filter,
            id_=f"{self.id_}_arrowhead",
            stroke=self.arrowhead_stroke,
            stroke_dasharray=self.arrowhead_stroke_dasharray,
            stroke_dashoffset=self.arrowhead_stroke_dashoffset,
            stroke_width=self.arrowhead_stroke_width,
            transform=self.arrowhead_transform,
        )
        transformation = self._get_arrowhead_transformation()
        group = group.transformed(transformation)
        return [group]

    def path_drawing_elements(self) -> list[momapy.drawing.Path]:
        """Return the drawing elements of the single-headed arc path"""
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
            first_segment = self.segments[0].shortened(self.start_shorten, "start")
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
            actions=tuple(actions),
            class_=f"{type(self).__name__}_path",
            fill=self.path_fill,
            filter=self.path_filter,
            id_=f"{self.id_}_path",
            stroke=self.path_stroke,
            stroke_dasharray=self.path_stroke_dasharray,
            stroke_dashoffset=self.path_stroke_dashoffset,
            stroke_width=self.path_stroke_width,
            transform=self.path_transform,
        )
        return [path]

    def self_drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        """Return the self drawing elements of the single-headed arc"""
        drawing_elements = (
            self.path_drawing_elements() + self.arrowhead_drawing_elements()
        )
        group = momapy.drawing.Group(
            class_=type(self).__name__,
            elements=tuple(drawing_elements),
            fill=self.fill,
            filter=self.filter,
            id_=self.id_,
            stroke=self.stroke,
            stroke_dasharray=self.stroke_dasharray,
            stroke_dashoffset=self.stroke_dashoffset,
            stroke_width=self.stroke_width,
            transform=self.transform,
        )
        return [group]


@dataclasses.dataclass(frozen=True, kw_only=True)
class DoubleHeadedArc(Arc):
    """Base class for double-headed arcs. A double-headed arc is formed of a path and two arrowheads, on at the beginning of the path and one at its end"""

    end_arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The end arrowhead fill color of the arc"},
        )
    )
    end_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = dataclasses.field(
        default=None,
        metadata={"description": "The end arrowhead filter of the arc"},
    )
    end_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = dataclasses.field(
        default=None,
        metadata={"description": "The end arrowhead stroke color of the arc"},
    )
    end_arrowhead_stroke_dasharray: tuple[float, ...] | None = dataclasses.field(
        default=None,
        metadata={"description": "The end arrowhead stroke dasharray of the arc"},
    )
    end_arrowhead_stroke_dashoffset: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The end arrowhead stroke dashoffset of the arc"},
    )
    end_arrowhead_stroke_width: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The end arrowhead stroke width of the arc"},
    )
    end_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = dataclasses.field(
        default=None,
        metadata={"description": "The end arrowhead transform of the arc"},
    )
    start_arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = dataclasses.field(
        default=None,
        metadata={"description": "The start arrowhead fill color of the arc"},
    )
    start_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = dataclasses.field(
        default=None,
        metadata={"description": "The start arrowhead filter of the arc"},
    )
    start_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = dataclasses.field(
        default=None,
        metadata={"description": "The start arrowhead stroke color of the arc"},
    )
    start_arrowhead_stroke_dasharray: tuple[float, ...] | None = dataclasses.field(
        default=None,
        metadata={"description": "The start arrowhead stroke dasharray of the arc"},
    )
    start_arrowhead_stroke_dashoffset: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The start arrowhead stroke dashoffset of the arc"},
    )
    start_arrowhead_stroke_width: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The start arrowhead stroke width of the arc"},
    )
    start_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = dataclasses.field(
        default=None,
        metadata={"description": "The start arrowhead transform of the arc"},
    )

    def start_arrowhead_length(self) -> float:
        """Return the length of the double-headed arc start arrowhead"""
        bbox = momapy.drawing.get_drawing_elements_bbox(
            self._start_arrowhead_border_drawing_elements()
        )
        if math.isnan(bbox.width):
            return 0.0
        return abs(bbox.west().x)

    def start_arrowhead_tip(self) -> momapy.geometry.Point:
        """Return the tip anchor point of the double-headed arc start arrowhead"""
        segment = self.segments[0]
        segment = momapy.geometry.Segment(segment.p2, segment.p1)
        segment_length = segment.length()
        if segment_length == 0:
            return segment.p2
        fraction = 1 - self.start_shorten / segment_length
        return segment.get_position_at_fraction(fraction)

    def start_arrowhead_base(self) -> momapy.geometry.Point:
        """Return the base anchor point of the double-headed arc start arrowhead"""
        arrowhead_length = self.start_arrowhead_length()
        if arrowhead_length == 0:
            return self.start_point()
        segment = self.segments[0]
        segment = momapy.geometry.Segment(segment.p2, segment.p1)
        segment_length = segment.length()
        if segment_length == 0:
            return self.start_arrowhead_tip() + (arrowhead_length, 0)
        fraction = 1 - (arrowhead_length + self.start_shorten) / segment_length
        return segment.get_position_at_fraction(fraction)

    def start_arrowhead_bbox(self) -> momapy.geometry.Bbox:
        """Return the bounding box of the double-headed arc start arrowhead"""
        return momapy.drawing.get_drawing_elements_bbox(
            self.start_arrowhead_drawing_elements()
        )

    def start_arrowhead_border(self, point) -> momapy.geometry.Point:
        """Return the point at the intersection of the drawing elements of the double-headed arc start arrowhead and the line going through the center of these drawing elements and the given point.
        When there are multiple intersection points, the one closest to the given point is returned
        """
        point = momapy.drawing.get_drawing_elements_border(
            self.start_arrowhead_drawing_elements(), point
        )
        if point.isnan():
            return self.start_arrowhead_tip()
        return point

    def end_arrowhead_length(self) -> float:
        """Return the length of the double-headed arc end arrowhead"""
        bbox = momapy.drawing.get_drawing_elements_bbox(
            self._end_arrowhead_border_drawing_elements()
        )
        if math.isnan(bbox.width):
            return 0.0
        return bbox.east().x

    def end_arrowhead_tip(self) -> momapy.geometry.Point:
        """Return the tip anchor point of the double-headed arc end arrowhead"""
        segment = self.segments[-1]
        segment_length = segment.length()
        if segment_length == 0:
            return segment.p2
        fraction = 1 - self.end_shorten / segment_length
        return segment.get_position_at_fraction(fraction)

    def end_arrowhead_base(self) -> momapy.geometry.Point:
        """Return the base anchor point of the double-headed arc end arrowhead"""
        arrowhead_length = self.end_arrowhead_length()
        if arrowhead_length == 0:
            return self.end_point()
        segment = self.segments[-1]
        segment_length = segment.length()
        if segment_length == 0:
            return self.end_arrowhead_tip() - (arrowhead_length, 0)
        fraction = 1 - (arrowhead_length + self.end_shorten) / segment_length
        return segment.get_position_at_fraction(fraction)

    def end_arrowhead_bbox(self):
        """Return the bounding box of the double-headed arc start arrowhead"""
        return momapy.drawing.get_drawing_elements_bbox(
            self.end_arrowhead_drawing_elements()
        )

    def end_arrowhead_border(self, point):
        """Return the point at the intersection of the drawing elements of the double-headed arc end arrowhead and the line going through the center of these drawing elements and the given point.
        When there are multiple intersection points, the one closest to the given point is returned
        """

        point = momapy.drawing.get_drawing_elements_border(
            self.end_arrowhead_drawing_elements(), point
        )
        if point.isnan():
            return self.end_arrowhead_tip()
        return point

    @abc.abstractmethod
    def _start_arrowhead_border_drawing_elements(
        self,
    ) -> list[momapy.drawing.DrawingElement]:
        # base of the arrow if at (0, 0), and the direction to the left
        pass

    @abc.abstractmethod
    def _end_arrowhead_border_drawing_elements(
        self,
    ) -> list[momapy.drawing.DrawingElement]:
        # base of the arrow if at (0, 0), and the direction to the right
        pass

    def _get_start_arrowhead_transformation(self):
        arrowhead_length = self.start_arrowhead_length()
        arrowhead_base = self.start_arrowhead_base()
        segment = self.segments[0]
        if arrowhead_length == 0:
            segment_coords = segment.to_shapely().coords
            p1 = momapy.geometry.Point.from_tuple(segment_coords[1])
            p2 = momapy.geometry.Point.from_tuple(segment_coords[0])
            line = momapy.geometry.Line(p1, p2)
        else:
            line = momapy.geometry.Line(arrowhead_base, segment.p1)
        angle = momapy.geometry.get_angle_to_horizontal_of_line(line)
        angle += math.pi
        translation = momapy.geometry.Translation(arrowhead_base.x, arrowhead_base.y)
        rotation = momapy.geometry.Rotation(angle, arrowhead_base)
        return rotation * translation

    def start_arrowhead_drawing_elements(
        self,
    ) -> list[momapy.drawing.DrawingElement]:
        """Return the drawing elements of the double-headed arc start arrowhead"""
        drawing_elements = self._start_arrowhead_border_drawing_elements()
        group = momapy.drawing.Group(
            class_=f"{type(self).__name__}_start_arrowhead",
            elements=tuple(drawing_elements),
            id_=f"{self.id_}_start_arrowhead",
            fill=self.start_arrowhead_fill,
            filter=self.start_arrowhead_filter,
            stroke=self.start_arrowhead_stroke,
            stroke_dasharray=self.start_arrowhead_stroke_dasharray,
            stroke_dashoffset=self.start_arrowhead_stroke_dashoffset,
            stroke_width=self.start_arrowhead_stroke_width,
            transform=self.start_arrowhead_transform,
        )
        transformation = self._get_start_arrowhead_transformation()
        group = group.transformed(transformation)
        return [group]

    def _get_end_arrowhead_transformation(self):
        arrowhead_length = self.end_arrowhead_length()
        arrowhead_base = self.end_arrowhead_base()
        segment = self.segments[-1]
        if arrowhead_length == 0:
            segment_coords = segment.to_shapely().coords
            p1 = momapy.geometry.Point.from_tuple(segment_coords[-2])
            p2 = momapy.geometry.Point.from_tuple(segment_coords[-1])
            line = momapy.geometry.Line(p1, p2)
        else:
            line = momapy.geometry.Line(arrowhead_base, segment.p2)
        angle = momapy.geometry.get_angle_to_horizontal_of_line(line)
        translation = momapy.geometry.Translation(arrowhead_base.x, arrowhead_base.y)
        rotation = momapy.geometry.Rotation(angle, arrowhead_base)
        return rotation * translation

    def end_arrowhead_drawing_elements(
        self,
    ) -> list[momapy.drawing.DrawingElement]:
        drawing_elements = self._end_arrowhead_border_drawing_elements()
        group = momapy.drawing.Group(
            class_=f"{type(self).__name__}_end_arrowhead",
            elements=tuple(drawing_elements),
            fill=self.end_arrowhead_fill,
            filter=self.end_arrowhead_filter,
            id_=f"{self.id_}_end_arrowhead",
            stroke=self.end_arrowhead_stroke,
            stroke_width=self.end_arrowhead_stroke_width,
            stroke_dasharray=self.end_arrowhead_stroke_dasharray,
            stroke_dashoffset=self.end_arrowhead_stroke_dashoffset,
            transform=self.end_arrowhead_transform,
        )
        transformation = self._get_end_arrowhead_transformation()
        group = group.transformed(transformation)
        return [group]

    def path_drawing_elements(self) -> list[momapy.drawing.Path]:
        """Return the drawing elements of the double-headed arc path"""
        start_arrowhead_length = self.start_arrowhead_length()
        end_arrowhead_length = self.end_arrowhead_length()
        if len(self.segments) == 1:
            segment = (
                self.segments[0]
                .shortened(self.start_shorten + start_arrowhead_length, "start")
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
            actions=tuple(actions),
            class_=f"{type(self).__name__}_path",
            fill=self.path_fill,
            filter=self.path_filter,
            id_=f"{self.id_}_path",
            stroke=self.path_stroke,
            stroke_dasharray=self.path_stroke_dasharray,
            stroke_dashoffset=self.path_stroke_dashoffset,
            stroke_width=self.path_stroke_width,
            transform=self.path_transform,
        )
        return [path]

    def self_drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        """Return the self drawing elements of the double-headed arc. These include the drawing elements of the arc path, the start arrowhead, and the end arrowhead"""
        drawing_elements = (
            self.path_drawing_elements()
            + self.start_arrowhead_drawing_elements()
            + self.end_arrowhead_drawing_elements()
        )

        group = momapy.drawing.Group(
            class_=type(self).__name__,
            elements=tuple(drawing_elements),
            id_=self.id_,
            fill=self.fill,
            filter=self.filter,
            stroke=self.stroke,
            stroke_dasharray=self.stroke_dasharray,
            stroke_dashoffset=self.stroke_dashoffset,
            stroke_width=self.stroke_width,
            transform=self.transform,
        )
        return [group]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Model(MapElement):
    """Base class for models"""

    @abc.abstractmethod
    def is_submodel(self, other) -> bool:
        pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Layout(Node):
    """Class for layouts"""

    fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )

    def _border_drawing_elements(self) -> list[momapy.drawing.DrawingElement]:
        actions = [
            momapy.drawing.MoveTo(self.position - (self.width / 2, self.height / 2)),
            momapy.drawing.LineTo(self.position + (self.width / 2, -self.height / 2)),
            momapy.drawing.LineTo(self.position + (self.width / 2, self.height / 2)),
            momapy.drawing.LineTo(self.position + (-self.width / 2, self.height / 2)),
            momapy.drawing.ClosePath(),
        ]
        path = momapy.drawing.Path(actions=tuple(actions))
        return [path]

    def is_sublayout(self, other, flattened=False, unordered=False):
        """Return `true` if another given layout is a sublayout of the layout, `false` otherwise"""

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
        return _is_sublist(self.children(), other.children(), unordered=unordered)


class LayoutModelMapping(momapy.utils.FrozenSurjectionDict):
    """Class for mappings between model elements and layout elements"""

    def get_mapping(
        self,
        map_element: MapElement,
    ) -> ModelElement | list[LayoutElement]:
        if map_element in self:
            return self[map_element]
        return self.inverse.get(map_element)

    def is_submapping(self, other) -> bool:
        """Return `true` if the mapping is a submapping of another `LayoutModelMapping`, `false` otherwise"""
        return self.items() <= other.items()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Map(MapElement):
    """Class for maps"""

    model: Model | None = dataclasses.field(
        default=None, metadata={"description": "The model of the map"}
    )
    layout: Layout | None = dataclasses.field(
        default=None, metadata={"description": "The layout of the map"}
    )
    layout_model_mapping: LayoutModelMapping | None = dataclasses.field(
        default=None,
        metadata={"description": "The layout model mapping of the map"},
    )

    def is_submap(self, other):
        """Return `true` if another given map is a submap of the `Map`, `false` otherwise"""
        if (
            self.model is None
            or self.layout is None
            or self.layout_model_mapping is None
        ):
            return False
        return (
            self.model.is_submodel(other.model)
            and self.layout.is_sublayout(other.layout)
            and self.layout_model_mapping.is_submapping(other.layout_model_mapping)
        )

    def get_mapping(
        self,
        map_element: MapElement | tuple[ModelElement, ModelElement],
    ):
        """Return the layout elements mapped to the given model element"""
        return self.layout_model_mapping.get_mapping(map_element)


class TupleBuilder(list, momapy.builder.Builder):
    """Builder class for tuples"""

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
    """Builder class for frozensets"""

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
    """Builder class for frozendicts"""

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
                for k, v in obj.items()
            ]
        )
        return builder


momapy.builder.register_builder_cls(TupleBuilder)
momapy.builder.register_builder_cls(FrozensetBuilder)
momapy.builder.register_builder_cls(FrozendictBuilder)


def _map_element_builder_hash(self):
    return hash(self.id_)


def _map_element_builder_eq(self, other):
    return self.__class__ == other.__class__ and self.id_ == other.id_


MapElementBuilder = momapy.builder.get_or_make_builder_cls(
    MapElement,
    builder_namespace={
        "__hash__": _map_element_builder_hash,
        "__eq__": _map_element_builder_eq,
    },
)

ModelElementBuilder = momapy.builder.get_or_make_builder_cls(ModelElement)
"""Base class for model element builders"""
LayoutElementBuilder = momapy.builder.get_or_make_builder_cls(LayoutElement)
"""Base class for layout element builders"""
NodeBuilder = momapy.builder.get_or_make_builder_cls(Node)
"""Base class for node builders"""
SingleHeadedArcBuilder = momapy.builder.get_or_make_builder_cls(SingleHeadedArc)
"""Base class for single-headed arc builders"""
DoubleHeadedArcBuilder = momapy.builder.get_or_make_builder_cls(DoubleHeadedArc)
"""Base class for double-headed arc builders"""
TextLayoutBuilder = momapy.builder.get_or_make_builder_cls(TextLayout)
"""Class for text layout builders"""


def _model_builder_new_element(self, element_cls, *args, **kwargs):
    if not momapy.builder.issubclass_or_builder(element_cls, ModelElement):
        raise TypeError(
            "element class must be a subclass of ModelElementBuilder or ModelElement"
        )
    return momapy.builder.new_builder_object(element_cls, *args, **kwargs)


ModelBuilder = momapy.builder.get_or_make_builder_cls(
    Model,
    builder_namespace={"new_element": _model_builder_new_element},
)
"""Base class for model builders"""


def _layout_builder_new_element(self, element_cls, *args, **kwargs):
    if not momapy.builder.issubclass_or_builder(element_cls, LayoutElement):
        raise TypeError(
            "element class must be a subclass of LayoutElementBuilder or LayoutElement"
        )
    return momapy.builder.new_builder_object(element_cls, *args, **kwargs)


LayoutBuilder = momapy.builder.get_or_make_builder_cls(
    Layout,
    builder_namespace={"new_element": _layout_builder_new_element},
)
"""Base class for layout builders"""


class LayoutModelMappingBuilder(momapy.utils.SurjectionDict, momapy.builder.Builder):
    _cls_to_build: typing.ClassVar[type] = LayoutModelMapping

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_mapping(
        self,
        map_element: MapElementBuilder | MapElement | tuple[ModelElement, ModelElement],
    ):
        if map_element in self:
            return self[map_element]
        return self.inverse.get(map_element)

    def add_mapping(
        self,
        layout_element: LayoutElement,
        model_element: ModelElement | tuple[ModelElement, ModelElement],
        replace=False,
    ):
        if replace:
            existing_layout_elements = self.get_mapping(model_element)
            if existing_layout_elements is not None:
                for existing_layout_element in existing_layout_elements:
                    del self[existing_layout_element]
                    self[existing_layout_element] = model_element
        self[layout_element] = model_element

    def build(
        self,
        inside_collections: bool = True,
        builder_to_object: dict[int, typing.Any] | None = None,
    ):
        return self._cls_to_build(
            {
                momapy.builder.object_from_builder(
                    key, builder_to_object=builder_to_object
                ): momapy.builder.object_from_builder(
                    value, builder_to_object=builder_to_object
                )
                for key, value in self.items()
            }
        )

    @classmethod
    def from_object(
        cls,
        obj,
        inside_collections: bool = True,
        omit_keys: bool = True,
        object_to_builder: dict[int, momapy.builder.Builder] | None = None,
    ) -> typing.Self:
        items = []
        for key, value in obj.items():
            new_key = momapy.builder.builder_from_object(
                key, object_to_builder=object_to_builder
            )
            if isinstance(value, tuple):
                new_value = tuple(
                    [
                        momapy.builder.builder_from_object(
                            element, object_to_builder=object_to_builder
                        )
                        for element in value
                    ]
                )
            else:
                new_value = momapy.builder.builder_from_object(
                    value, object_to_builder=object_to_builder
                )
            items.append(
                (
                    new_key,
                    new_value,
                )
            )
        return cls(items)


momapy.builder.register_builder_cls(LayoutModelMappingBuilder)


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
    layout_element: LayoutElement,
    model_element: ModelElement | tuple[ModelElement, ModelElement],
):
    self.layout_model_mapping.add_mapping(layout_element, model_element)


def _map_builder_get_mapping(
    self,
    map_element: MapElement,
) -> ModelElement | list[LayoutElement]:
    return self.layout_model_mapping.get_mapping(map_element)


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
"""Base class for map builders"""
