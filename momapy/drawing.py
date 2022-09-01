from abc import ABC
from dataclasses import dataclass, field, replace
from typing import Union, Optional

import momapy.geometry
import momapy.coloring


class NoneValueType(object):
    pass


NoneValue = NoneValueType()


@dataclass(frozen=True)
class Transformation(ABC):
    pass


@dataclass(frozen=True)
class Rotation(Transformation):
    angle: float
    point: Optional[momapy.geometry.Point] = None


@dataclass(frozen=True)
class Translation(Transformation):
    tx: float
    ty: float


@dataclass(frozen=True)
class DrawingElement(ABC):
    stroke_width: float = None
    stroke: Optional[Union[momapy.coloring.Color, NoneValueType]] = None
    fill: Optional[Union[momapy.coloring.Color, NoneValueType]] = None
    transform: tuple[Transformation] = field(default_factory=tuple)


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


@dataclass(frozen=True)
class Text(DrawingElement):
    text: Optional[str] = None
    position: Optional[momapy.geometry.Point] = None
    width: Optional[float] = None
    height: Optional[float] = None
    font_description: Optional[str] = None
    font_color: momapy.coloring.Color = momapy.coloring.colors.black

    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y


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
        if self.rx > self.width / 2:
            self.rx = self.width / 2
        if self.ry > self.height / 2:
            self.ry = self.height / 2

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y


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


def rotate(angle, point=None):
    return Rotation(angle, point)


def translate(tx, ty):
    return Translation(tx, ty)
