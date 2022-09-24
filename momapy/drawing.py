from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Union, Optional
from uuid import UUID, uuid4

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
    pass

@dataclass(frozen=True)
class DropShadowEffect(FilterEffect):
    dx: float
    dy: float
    std_deviation: float = 2.0
    flood_opacity: float = 0.5
    flood_color: momapy.coloring.Color = momapy.coloring.colors.black

@dataclass(frozen=True)
class Filter(object):
    id: Union[str, UUID] = field(
        hash=False, compare=False, default_factory=uuid4)
    filter_units: str = "userSpaceOnUse"
    effects: tuple[FilterEffect] = field(default_factory=tuple)

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


@dataclass(frozen=True)
class LineTo(PathAction):
    point: momapy.geometry.Point

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

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


@dataclass(frozen=True)
class Close(PathAction):
    pass


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
                    action.point, action.radius,
                    action.start_angle, action.end_angle
                )
                objects.append(arc)
                current_point = arc.end_point()
            elif isinstance(action, EllipticalArc):
                elliptical_arc = momapy.geometry.EllipticalArc(
                    current_point, action.point, action.rx, action.ry,
                    action.x_axis_rotation, action.arc_flag, action.sweep_flag
                )
                objects.append(elliptical_arc)
                current_point = elliptical_arc.end_point
            elif isinstance(action, Close):
                segment = momapy.geometry.Segment(current_point, first_point)
                objects.append(segment)
                current_point = first_point # should not be necessary
        return objects


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


@dataclass(frozen=True)
class Group(DrawingElement):
    elements: tuple[DrawingElement] = field(default_factory=tuple)

    def __add__(self, element):
        return self.__class__(
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            elements=self.elements + (element,),
            transform=self.transform)

    def to_geometry(self):
        objects = []
        for element in self.elements:
            objects += element.to_geometry()
        return objects

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

@dataclass(frozen=True)
class Rectangle(DrawingElement):
    point: Optional[momapy.geometry.Point] = None
    width: Optional[float] = None
    height: Optional[float] = None
    rx: Optional[float] = 0
    ry: Optional[float] = 0

    def __post_init__(self):
        if self.rx is None and self.ry is not None:
            self.rx = self.ry
        elif self.ry is None and self.rx is not None:
            self.ry = self.rx
        if self.rx > self.width/2:
            self.rx = self.width/2
        if self.ry > self.height/2:
            self.ry = self.height/2

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
            transform=self.transform)
        x = self.point.x
        y = self.point.y
        rx = self.rx
        ry = self.ry
        width = self.width
        height = self.height
        path += move_to(momapy.geometry.Point(x + rx, y))
        path += line_to(
            momapy.geometry.Point(x + width - rx, y))
        if rx > 0 and ry > 0:
            path += elliptical_arc(
                momapy.geometry.Point(x + width, y + ry), rx, ry, 0, 0, 1)
        path += line_to(momapy.geometry.Point(
            x + width, y + height - ry))
        if rx > 0 and ry > 0:
            path += elliptical_arc(
                momapy.geometry.Point(x + width - rx, y + height),
                rx, ry, 0, 0, 1
            )
        path += line_to(
            momapy.geometry.Point(x + rx, y + height))
        if rx > 0 and ry > 0:
            path += elliptical_arc(
                momapy.geometry.Point(x, y + height - ry), rx, ry, 0, 0, 1)
        path += line_to(momapy.geometry.Point(x, y + ry))
        if rx > 0 and ry > 0:
            path += elliptical_arc(
                momapy.geometry.Point(x + rx, y), rx, ry, 0, 0, 1)
        path += close()
        return path

    def to_geometry(self):
        path = self.to_path()
        return path.to_geometry()

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
