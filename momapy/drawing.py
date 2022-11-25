from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Union, Optional
from uuid import UUID, uuid4
import math
import copy

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
    def to_geometry(self):
        pass


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


@dataclass(frozen=True)
class Arc(PathAction):
    point: momapy.geometry.Point
    radius: float
    start_angle: float
    end_angle: float

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y


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
        x1, y1 = current_point.x, current_point.y
        sigma = self.x_axis_rotation
        x2, y2 = self.point.x, self.point.y
        rx = self.rx
        ry = self.ry
        fa = self.arc_flag
        fs = self.sweep_flag
        x1p = math.cos(sigma) * ((x1 - x2) / 2) + math.sin(sigma) * (
            (y1 - y2) / 2
        )
        y1p = -math.sin(sigma) * ((x1 - x2) / 2) + math.cos(sigma) * (
            (y1 - y2) / 2
        )
        l = x1p**2 / rx**2 + y1p**2 / ry**2
        if l > 1:
            rx = math.sqrt(l) * rx
            ry = math.sqrt(l) * ry
        r = rx**2 * ry**2 - rx**2 * y1p**2 - ry**2 * x1p**2
        if r < 0:  # imprecision
            r = 0
        a = math.sqrt(r / (rx**2 * y1p**2 + ry**2 * x1p**2))
        if fa == fs:
            a = -a
        cxp = a * rx * y1p / ry
        cyp = -a * ry * x1p / rx
        cx = math.cos(sigma) * cxp - math.sin(sigma) * cyp + (x1 + x2) / 2
        cy = math.sin(sigma) * cxp + math.cos(sigma) * cyp + (y1 + y2) / 2
        center = momapy.geometry.Point(cx, cy)
        east = center + (math.cos(sigma) * rx, math.sin(sigma) * rx)
        north = center + (math.cos(sigma) * ry, math.sin(sigma) * ry)
        new_center = momapy.geometry.transform_point(center, transformation)
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

    def to_geometry(self):
        objects = []
        for action in self.actions:
            if isinstance(action, MoveTo):
                current_point = action.point
                first_point = current_point
            elif isinstance(action, LineTo):
                segment = momapy.geometry.Segment(current_point, action.point)
                objects.append(segment)
                current_point = action.point
            elif isinstance(action, Arc):
                arc = momapy.geometry.Arc(
                    action.point,
                    action.radius,
                    action.start_angle,
                    action.end_angle,
                )
                objects.append(arc)
                current_point = arc.end_point()
            elif isinstance(action, EllipticalArc):
                elliptical_arc = momapy.geometry.EllipticalArc(
                    current_point,
                    action.point,
                    action.rx,
                    action.ry,
                    action.x_axis_rotation,
                    action.arc_flag,
                    action.sweep_flag,
                )
                objects.append(elliptical_arc)
                current_point = elliptical_arc.end_point
            elif isinstance(action, Close):
                segment = momapy.geometry.Segment(current_point, first_point)
                objects.append(segment)
                current_point = first_point  # should not be necessary
        return objects

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

    def to_geometry(self):
        return [self.position]

    def transformed(self):
        return copy.deepcopy(self)


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

    def to_geometry(self):
        objects = []
        for element in self.elements:
            objects += element.to_geometry()
        return objects

    def transformed(self, transformation):
        elements = []
        for layout_element in self.elements:
            elements.append(layout_element.transformed(transformation))
        return replace(self, elements=tuple(elements)


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

    def to_geometry(self):
        return [momapy.geometry.Ellipse(self.point, self.rx, self.ry)]

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

    def to_geometry(self):
        path = self.to_path()
        return path.to_geometry()

    def transformed(self, transformation):
        path = self.to_path()
        return path.transformed(transformation)


def move_to(point):
    return MoveTo(point)


def line_to(point):
    return LineTo(point)


def arc(point, radius, start_angle, end_angle):
    return Arc(point, radius, start_angle, end_angle)


def elliptical_arc(point, rx, ry, x_axis_rotation, arc_flag, sweep_flag):
    return EllipticalArc(point, rx, ry, x_axis_rotation, arc_flag, sweep_flag)


def close():
    return Close()
