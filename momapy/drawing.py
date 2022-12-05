from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Union, Optional
from uuid import UUID, uuid4
import math
import copy

import numpy

import shapely.geometry
import shapely.affinity
import shapely.ops

import momapy.geometry
import momapy.coloring


class NoneValueType(object):
    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


NoneValue = NoneValueType()


@dataclass(frozen=True)
class FilterEffect(ABC):
    result: Optional[str] = None


@dataclass(frozen=True)
class DropShadowEffect(FilterEffect):
    dx: float = 0.0
    dy: float = 0.0
    std_deviation: float = 0.0
    flood_opacity: float = 1.0
    flood_color: momapy.coloring.Color = momapy.coloring.colors.black

    def to_compat(self):
        flood_effect = FloodEffect(
            result="flood",
            flood_opacity=self.flood_opacity,
            flood_color=self.flood_color,
        )
        composite_effect1 = CompositeEffect(
            in_="flood", in2="SourceGraphic", operator="in", result="composite1"
        )
        gaussian_blur_effect = GaussianBlurEffect(
            in_="composite1",
            std_deviation=self.std_deviation,
            result="gaussian_blur",
        )
        offset_effect = OffsetEffect(
            in_="gaussian_blur", dx=self.dx, dy=self.dy, result="offset"
        )
        composite_effect2 = CompositeEffect(
            in_="SourceGraphic",
            in2="offset",
            operator="over",
            result=self.result,
        )
        effects = [
            flood_effect,
            composite_effect1,
            gaussian_blur_effect,
            offset_effect,
            composite_effect2,
        ]
        return effects


@dataclass(frozen=True)
class CompositeEffect(FilterEffect):
    in_: Optional[str] = None
    in2: Optional[str] = None
    operator: Optional[str] = None


@dataclass(frozen=True)
class FloodEffect(FilterEffect):
    flood_opacity: float = 1.0
    flood_color: momapy.coloring.Color = momapy.coloring.colors.black


@dataclass(frozen=True)
class GaussianBlurEffect(FilterEffect):
    in_: Optional[str] = None
    std_deviation: float = 0
    edge_mode: Optional[str] = None


@dataclass(frozen=True)
class OffsetEffect(FilterEffect):
    in_: Optional[str] = None
    dx: float = 0
    dy: float = 0


@dataclass(frozen=True)
class Filter(object):
    id: Union[str, UUID] = field(
        hash=False, compare=False, default_factory=uuid4
    )
    filter_units: str = "objectBoundingBox"
    effects: tuple[FilterEffect] = field(default_factory=tuple)

    def to_compat(self):
        effects = []
        for effect in self.effects:
            if hasattr(effect, "to_compat"):
                effects += effect.to_compat()
            else:
                effects.append(effect)
        return replace(self, effects=effects)


@dataclass(frozen=True)
class DrawingElement(ABC):
    stroke_width: Optional[float] = None
    stroke: Optional[Union[momapy.coloring.Color, NoneValueType]] = None
    fill: Optional[Union[momapy.coloring.Color, NoneValueType]] = None
    transform: Optional[tuple[momapy.geometry.Transformation]] = None
    filter: Optional[Filter] = None

    @abstractmethod
    def to_shapely(self, to_polygons=False):
        pass

    def bbox(self):
        bounds = self.to_shapely().bounds
        return momapy.geometry.Bbox(
            momapy.geometry.Point(
                (bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2
            ),
            bounds[2] - bounds[0],
            bounds[3] - bounds[1],
        )


@dataclass(frozen=True)
class PathAction(ABC):
    def __add__(self, action):
        if isinstance(action, PathAction):
            actions = [self, action]
        elif isinstance(action, PathActionList):
            actions = [self] + action.actions
        else:
            raise TypeError
        return PathActionList(actions=actions)


@dataclass(frozen=True)
class MoveTo(PathAction):
    point: momapy.geometry.Point

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    def transformed(self, transformation, current_point):
        return MoveTo(
            momapy.geometry.transform_point(self.point, transformation)
        )


@dataclass(frozen=True)
class LineTo(PathAction):
    point: momapy.geometry.Point

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    def transformed(self, transformation, current_point):
        return LineTo(
            momapy.geometry.transform_point(self.point, transformation)
        )

    def to_geometry(self, current_point):
        return momapy.geometry.Segment(current_point, self.point)

    def to_shapely(self, current_point):
        return self.to_geometry(current_point).to_shapely()


@dataclass(frozen=True)
class EllipticalArc(PathAction):
    point: momapy.geometry.Point
    rx: float
    ry: float
    x_axis_rotation: float
    arc_flag: int
    sweep_flag: int

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    def transformed(self, transformation, current_point):
        east = momapy.geometry.Point(
            math.cos(self.x_axis_rotation) * self.rx,
            math.sin(self.x_axis_rotation) * self.rx,
        )
        north = momapy.geometry.Point(
            math.cos(self.x_axis_rotation) * self.ry,
            math.sin(self.x_axis_rotation) * self.ry,
        )
        new_center = momapy.geometry.transform_point(
            momapy.geometry.Point(0, 0), transformation
        )
        new_east = momapy.geometry.transform_point(east, transformation)
        new_north = momapy.geometry.transform_point(north, transformation)
        new_rx = momapy.geometry.Segment(new_center, new_east).length()
        new_ry = momapy.geometry.Segment(new_center, new_north).length()
        new_start_point = momapy.geometry.transform_point(
            current_point, transformation
        )
        new_end_point = momapy.geometry.transform_point(
            self.point, transformation
        )
        new_x_axis_rotation = math.degrees(
            momapy.geometry.get_angle_of_line(
                momapy.geometry.Line(new_center, new_east)
            )
        )
        return EllipticalArc(
            new_end_point,
            new_rx,
            new_ry,
            new_x_axis_rotation,
            self.arc_flag,
            self.sweep_flag,
        )

    def to_geometry(self, current_point):
        return momapy.geometry.EllipticalArc(
            current_point,
            self.point,
            self.rx,
            self.ry,
            self.x_axis_rotation,
            self.arc_flag,
            self.sweep_flag,
        )

    def to_shapely(self, current_point):
        s = self.to_geometry(current_point).to_shapely()
        return self.to_geometry(current_point).to_shapely()


@dataclass(frozen=True)
class CurveTo(PathAction):
    point: momapy.geometry.Point
    control_point1: momapy.geometry.Point
    control_point2: momapy.geometry.Point

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    def transformed(self, transformation, current_point):
        return CurveTo(
            momapy.geometry.transform_point(self.point),
            momapy.geometry.transform_point(self.control_point1),
            momapy.geometry.transform_point(self.control_point2),
        )

    def to_geometry(self, current_point):
        return momapy.geometry.BezierCurve(
            current_point,
            self.point,
            tuple([self.control_point1, self.control_point2]),
        )

    def to_shapely(self, current_point, n_segs=50):
        bezier_curve = self.to_geometry(current_point)
        return bezier_curve.to_shapely()


@dataclass(frozen=True)
class QuadraticCurveTo(PathAction):
    point: momapy.geometry.Point
    control_point: momapy.geometry.Point

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    def transformed(self, transformation, current_point):
        return CurveTo(
            momapy.geometry.transform_point(self.point),
            momapy.geometry.transform_point(self.control_point),
        )

    def to_curve_to(self, current_point):
        p1 = current_point
        p2 = self.point
        control_point1 = p1 + (self.control_point - p1) * (2 / 3)
        control_point2 = p2 + (self.control_point - p2) * (2 / 3)
        return CurveTo(p2, control_point1, control_point2)

    def to_geometry(self, current_point):
        return momapy.geometry.BezierCurve(
            current_point,
            self.point,
            tuple([self.control_point]),
        )

    def to_shapely(self, current_point, n_segs=50):
        bezier_curve = self.to_geometry(current_point)
        return bezier_curve.to_shapely()


@dataclass(frozen=True)
class Close(PathAction):
    def transformed(self, transformation, current_point):
        return Close()


@dataclass
class PathActionList(object):
    actions: list[PathAction] = field(default_factory=list)

    def __add__(self, other):
        if isinstance(other, PathAction):
            actions = self.actions + [other]
        elif isinstance(other, PathActionList):
            actions = self.actions + other.actions
        else:
            raise TypeError
        return PathActionList(actions=actions)


@dataclass(frozen=True)
class Path(DrawingElement):
    actions: tuple[PathAction] = field(default_factory=tuple)

    def __add__(self, other):
        if isinstance(other, PathAction):
            actions = (other,)
        elif isinstance(other, PathActionList):
            actions = tuple(other.actions)
        else:
            raise TypeError
        return replace(self, actions=self.actions + actions)

    def transformed(self, transformation):
        actions = []
        current_point = None
        for path_action in self.actions:
            new_path_action = path_action.transformed(
                transformation, current_point
            )
            actions.append(new_path_action)
            if hasattr(path_action, "point"):
                current_point = path_action.point
            else:
                current_point = None
        return replace(self, actions=tuple(actions))

    def to_shapely(self, to_polygons=False):
        current_point = momapy.geometry.Point(
            0, 0
        )  # in case the path does not start with a move_to command;
        # this is not possible in svg but not enforced here
        initial_point = current_point
        geom_collection = []
        line_strings = []
        previous_action = None
        for i, current_action in enumerate(self.actions):
            if i > 0:
                previous_action = self.actions[i - 1]
            if isinstance(current_action, MoveTo):
                current_point = current_action.point
                initial_point = current_point
                if (
                    not isinstance(previous_action, Close)
                    and previous_action is not None
                ):
                    multi_linestring = shapely.geometry.MultiLineString(
                        line_strings
                    )
                    line_string = shapely.ops.linemerge(multi_linestring)
                    geom_collection.append(line_string)
                line_strings = []
            elif isinstance(current_action, Close):
                if current_point != initial_point:
                    line_string = shapely.geometry.LineString(
                        [current_point.to_tuple(), initial_point.to_tuple()]
                    )
                    line_strings.append(line_string)
                polygons = shapely.ops.polygonize(line_strings)
                for polygon in polygons:
                    if not to_polygons:
                        polygon = polygon.boundary
                    geom_collection.append(polygon)
                current_point = initial_point
            else:
                line_string = current_action.to_shapely(current_point)
                line_strings.append(line_string)
                current_point = current_action.point
        if not isinstance(current_action, (MoveTo, Close)):
            multi_linestring = shapely.geometry.MultiLineString(line_strings)
            line_string = shapely.ops.linemerge(multi_linestring)
            geom_collection.append(line_string)
        return shapely.geometry.GeometryCollection(geom_collection)


@dataclass(frozen=True)
class Text(DrawingElement):
    text: Optional[str] = None
    font_family: Optional[str] = None
    font_size: Optional[str] = None
    position: Optional[momapy.geometry.Point] = None

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    def transformed(self):
        return copy.deepcopy(self)

    def to_shapely(self, to_polygons=False):
        return shapely.geometry.GeometryCollection([self.position.to_shapely()])


@dataclass(frozen=True)
class Group(DrawingElement):
    elements: tuple[DrawingElement] = field(default_factory=tuple)

    def __add__(self, element):
        return Group(
            stroke=self.stroke,
            stroke_width=self.stroke_width,
            fill=self.fill,
            filter=self.filter,
            transform=self.transform,
            elements=self.elements + type(self.elements)([element]),
        )

    def transformed(self, transformation):
        elements = []
        for layout_element in self.elements:
            elements.append(layout_element.transformed(transformation))
        return replace(self, elements=tuple(elements))

    def to_shapely(self, to_polygons=False):
        geom_collection = []
        for element in self.elements:
            geom_collection += element.to_shapely(to_polygons=to_polygons).geoms
        return shapely.geometry.GeometryCollection(geom_collection)


@dataclass(frozen=True)
class Ellipse(DrawingElement):
    point: Optional[momapy.geometry.Point] = None
    rx: Optional[float] = None
    ry: Optional[float] = None

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    def to_path(self):
        west = self.point - (self.rx, 0)
        east = self.point + (self.rx, 0)
        path = Path(
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            filter=self.filter,
        )
        path += move_to(west)
        path += elliptical_arc(east, self.rx, self.ry, 0, 1, 0)
        path += elliptical_arc(west, self.rx, self.ry, 0, 1, 0)
        path += close()
        return path

    def transformed(self, transformation):
        path = self.to_path()
        return path.transformed(transformation)

    def to_shapely(self, to_polygons=False):
        point = self.point.to_shapely()
        circle = point.buffer(1)
        ellipse = shapely.affinity.scale(circle, self.rx, self.ry)
        if not to_polygons:
            ellipse = ellipse.boundary
        return shapely.geometry.GeometryCollection([ellipse])


@dataclass(frozen=True)
class Rectangle(DrawingElement):
    point: Optional[momapy.geometry.Point] = None
    width: Optional[float] = None
    height: Optional[float] = None
    rx: Optional[float] = 0
    ry: Optional[float] = 0

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    def to_path(self):
        path = Path(
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            filter=self.filter,
        )
        x = self.point.x
        y = self.point.y
        rx = self.rx
        ry = self.ry
        width = self.width
        height = self.height
        path += move_to(momapy.geometry.Point(x + rx, y))
        path += line_to(momapy.geometry.Point(x + width - rx, y))
        if rx > 0 and ry > 0:
            path += elliptical_arc(
                momapy.geometry.Point(x + width, y + ry), rx, ry, 0, 0, 1
            )
        path += line_to(momapy.geometry.Point(x + width, y + height - ry))
        if rx > 0 and ry > 0:
            path += elliptical_arc(
                momapy.geometry.Point(x + width - rx, y + height),
                rx,
                ry,
                0,
                0,
                1,
            )
        path += line_to(momapy.geometry.Point(x + rx, y + height))
        if rx > 0 and ry > 0:
            path += elliptical_arc(
                momapy.geometry.Point(x, y + height - ry), rx, ry, 0, 0, 1
            )
        path += line_to(momapy.geometry.Point(x, y + ry))
        if rx > 0 and ry > 0:
            path += elliptical_arc(
                momapy.geometry.Point(x + rx, y), rx, ry, 0, 0, 1
            )
        path += close()
        return path

    def transformed(self, transformation):
        path = self.to_path()
        return path.transformed(transformation)

    def to_shapely(self, to_polygons=False):
        return self.to_path().to_shapely(to_polygons=to_polygons)


def move_to(point):
    return MoveTo(point)


def line_to(point):
    return LineTo(point)


def elliptical_arc(point, rx, ry, x_axis_rotation, arc_flag, sweep_flag):
    return EllipticalArc(point, rx, ry, x_axis_rotation, arc_flag, sweep_flag)


def curve_to(point, control_point1, control_point2):
    return CurveTo(point, control_point1, control_point2)


def quadratic_curve_to(point, control_point):
    return QuadraticCurveTo(point, control_point)


def close():
    return Close()
