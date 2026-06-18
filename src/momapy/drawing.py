"""SVG-like drawing elements for momapy.

This module provides classes for creating and manipulating SVG-like drawing
elements including paths, shapes, text, filters, and groups. It supports
transformations, styling attributes, and conversion to geometry primitives.

Examples:
    ```python
    from momapy.drawing import Path, MoveTo, LineTo, Rectangle, Text
    from momapy.geometry import Point
    from momapy.coloring import red, blue

    # Create a simple path
    path = Path(
        actions=(
            MoveTo(Point(0, 0)),
            LineTo(Point(10, 10)),
        ),
        stroke=red,
        stroke_width=2.0
    )

    # Create a rectangle
    rect = Rectangle(
        point=Point(5, 5),
        width=10,
        height=10,
        fill=blue,
        stroke=red
    )

    # Create text
    text = Text(
        text="Hello",
        point=Point(10, 10),
        font_size=14.0
    )
    ```
"""

import abc
import dataclasses
import math
import copy
import enum
import typing
import typing_extensions
import collections.abc
import platform

from momapy.coloring import black
from momapy.coloring import Color
from momapy.geometry import Bbox
from momapy.geometry import CubicBezierCurve
from momapy.geometry import EllipticalArc as GeometryEllipticalArc
from momapy.geometry import get_primitives_anchor_point
from momapy.geometry import get_primitives_angle
from momapy.geometry import get_primitives_border
from momapy.geometry import Line
from momapy.geometry import Point
from momapy.geometry import QuadraticBezierCurve
from momapy.geometry import ROUNDING
from momapy.geometry import Segment
from momapy.geometry import Transformation
from momapy.utils import make_uuid4_as_str

__all__ = [
    "ClosePath",
    "CompositeEffect",
    "CompositionOperator",
    "CurveTo",
    "DrawingElement",
    "DropShadowEffect",
    "EdgeMode",
    "Ellipse",
    "EllipticalArc",
    "FillRule",
    "Filter",
    "FilterEffect",
    "FilterEffectInput",
    "FilterUnits",
    "FloodEffect",
    "FontStyle",
    "FontWeight",
    "GaussianBlurEffect",
    "Group",
    "LineTo",
    "MoveTo",
    "NoneValue",
    "NoneValueType",
    "OffsetEffect",
    "Path",
    "PathAction",
    "QuadraticCurveTo",
    "Rectangle",
    "Text",
    "TextAnchor",
    "drawing_elements_to_geometry",
    "get_drawing_elements_anchor_point",
    "get_drawing_elements_angle",
    "get_drawing_elements_bbox",
    "get_drawing_elements_border",
    "get_initial_value",
]


class NoneValueType(object):
    """Singleton type for None values (as in SVG)."""

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __eq__(self, other) -> bool:
        return type(self) is type(other)

    def __hash__(self):
        return id(NoneValue)

    def __reduce__(self) -> str:
        """Pickle to the module-level `NoneValue` singleton.

        Returning the global's name keeps the singleton stable across a
        pickle round-trip; without it, unpickling builds a fresh
        `NoneValueType` instance and `value is NoneValue` checks (used in the
        renderers, writers, and core) silently fail. This mirrors
        `__copy__`/`__deepcopy__`, which already return `self`.
        """
        return "NoneValue"


NoneValue = NoneValueType()
"""A singleton value for type `NoneValueType`."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class FilterEffect(abc.ABC):
    """Abstract base class for filter effects.

    Filter effects are the individual operations composed inside a filter.
    """

    result: str | None = dataclasses.field(
        default=None, metadata={"description": "The name of the result"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class DropShadowEffect(FilterEffect):
    """Drop shadow filter effect.

    Casts a blurred, offset, colored copy of the source graphic behind it.
    """

    dx: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The horizontal offset of the shadow"},
    )
    dy: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The vertical offset of the shadow"},
    )
    std_deviation: float = dataclasses.field(
        default=0.0,
        metadata={
            "description": "The standard deviation to be used to compute the shadow"
        },
    )
    flood_opacity: float = dataclasses.field(
        default=1.0,
        metadata={"description": "The flood opacity of the shadow"},
    )
    flood_color: Color = dataclasses.field(
        default=black,
        metadata={"description": "The color of the shadow"},
    )

    def to_compat(self) -> list[FilterEffect]:
        """Convert to more compatible filter effects.

        Returns:
            List of equivalent filter effects.
        """
        flood_effect = FloodEffect(
            result=make_uuid4_as_str(),
            flood_opacity=self.flood_opacity,
            flood_color=self.flood_color,
        )
        composite_effect1 = CompositeEffect(
            in_=flood_effect.result,
            in2=FilterEffectInput.SOURCE_GRAPHIC,
            operator=CompositionOperator.IN,
            result=make_uuid4_as_str(),
        )
        gaussian_blur_effect = GaussianBlurEffect(
            in_=composite_effect1.result,
            std_deviation=self.std_deviation,
            result=make_uuid4_as_str(),
        )
        offset_effect = OffsetEffect(
            in_=gaussian_blur_effect.result,
            dx=self.dx,
            dy=self.dy,
            result=make_uuid4_as_str(),
        )
        composite_effect2 = CompositeEffect(
            in_=FilterEffectInput.SOURCE_GRAPHIC,
            in2=offset_effect.result,
            operator=CompositionOperator.OVER,
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


class FilterEffectInput(enum.Enum):
    """Filter effect input types.

    Enumerates the predefined source images that a filter effect can read from.
    """

    SOURCE_GRAPHIC = "SOURCE_GRAPHIC"
    SOURCE_ALPHA = "SOURCE_ALPHA"
    BACKGROUND_IMAGE = "BACKGROUND_IMAGE"
    BACKGROUND_ALPHA = "BACKGROUND_ALPHA"
    FILL_PAINT = "FILL_PAINT"
    STROKE_PAINT = "STROKE_PAINT"


class CompositionOperator(enum.Enum):
    """Composition operators for filter effects.

    Enumerates the ways two inputs can be combined by a composite effect.
    """

    OVER = "OVER"
    IN = "IN"
    OUT = "OUT"
    ATOP = "ATOP"
    XOR = "XOR"
    LIGHTER = "LIGHTER"
    ARITHMETIC = "ARITHMETIC"


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompositeEffect(FilterEffect):
    """Composite filter effect.

    Combines two inputs using a composition operator.
    """

    in_: FilterEffectInput | str | None = dataclasses.field(
        default=None,
        metadata={
            "description": "The first effect input or the name of the first filter effect input"
        },
    )
    in2: FilterEffectInput | str | None = dataclasses.field(
        default=None,
        metadata={
            "description": "The second effect input or the name of the second filter effect input"
        },
    )
    operator: CompositionOperator | None = dataclasses.field(
        default=CompositionOperator.OVER,
        metadata={
            "description": "The operator to be used to compute the composite effect"
        },
    )
    k1: float = dataclasses.field(
        default=0.0,
        metadata={"description": "k1 coefficient for the arithmetic operator"},
    )
    k2: float = dataclasses.field(
        default=0.0,
        metadata={"description": "k2 coefficient for the arithmetic operator"},
    )
    k3: float = dataclasses.field(
        default=0.0,
        metadata={"description": "k3 coefficient for the arithmetic operator"},
    )
    k4: float = dataclasses.field(
        default=0.0,
        metadata={"description": "k4 coefficient for the arithmetic operator"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class FloodEffect(FilterEffect):
    """Flood filter effect.

    Fills the filter region with a solid color at a given opacity.
    """

    flood_color: Color = dataclasses.field(
        default=black,
        metadata={"description": "The color of the flood effect"},
    )
    flood_opacity: float = dataclasses.field(
        default=1.0,
        metadata={"description": "The opacity of the flood effect"},
    )


class EdgeMode(enum.Enum):
    """Edge mode for blur effects.

    Enumerates how a blur effect treats pixels beyond the input edges.
    """

    DUPLICATE = "DUPLICATE"
    WRAP = "WRAP"


@dataclasses.dataclass(frozen=True, kw_only=True)
class GaussianBlurEffect(FilterEffect):
    """Gaussian blur filter effect.

    Blurs its input with a Gaussian kernel of the given standard deviation.
    """

    in_: FilterEffectInput | str | None = dataclasses.field(
        default=None,
        metadata={
            "description": "The effect input or the name of the filter effect input"
        },
    )
    std_deviation: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The standard deviation of the Gaussian blur"},
    )
    edge_mode: NoneValueType | EdgeMode = dataclasses.field(
        default=NoneValue,
        metadata={"description": "The edge handling mode of the blur effect"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OffsetEffect(FilterEffect):
    """Offset filter effect.

    Shifts its input by a horizontal and vertical offset.
    """

    in_: FilterEffectInput | str | None = dataclasses.field(
        default=None,
        metadata={
            "description": "The effect input or the name of the filter effect input"
        },
    )
    dx: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The horizontal offset of the offset effect"},
    )
    dy: float = dataclasses.field(
        default=0.0,
        metadata={"description": "The vertical offset of the offset effect"},
    )


class FilterUnits(enum.Enum):
    """Units for filter regions.

    Enumerates the coordinate systems in which a filter region is expressed.
    """

    USER_SPACE_ON_USE = "USER_SPACE_ON_USE"
    OBJECT_BOUNDING_BOX = "OBJECT_BOUNDING_BOX"


@dataclasses.dataclass(frozen=True, kw_only=True)
class Filter(object):
    """Filter with multiple effects.

    A filter applies a chain of effects to a drawing element within a region.
    """

    id_: str = dataclasses.field(
        hash=False,
        compare=False,
        default_factory=make_uuid4_as_str,
    )
    filter_units: FilterUnits = dataclasses.field(
        default=FilterUnits.OBJECT_BOUNDING_BOX,
        metadata={"description": "The units of the filter region"},
    )
    effects: tuple[FilterEffect] = dataclasses.field(default_factory=tuple)
    width: float | str = dataclasses.field(
        default="120%",
        metadata={"description": "The width of the filter region"},
    )
    height: float | str = dataclasses.field(
        default="120%",
        metadata={"description": "The height of the filter region"},
    )
    x: float | str = dataclasses.field(
        default="-10%",
        metadata={"description": "The x position of the filter region"},
    )
    y: float | str = dataclasses.field(
        default="-10%",
        metadata={"description": "The y position of the filter region"},
    )

    def to_compat(self) -> typing_extensions.Self:
        """Convert to compatible filter with simpler effects.

        Returns:
            A filter with effects replaced by simpler equivalents.
        """
        effects = []
        for effect in self.effects:
            if hasattr(effect, "to_compat"):
                effects += effect.to_compat()
            else:
                effects.append(effect)
        return dataclasses.replace(self, effects=tuple(effects))


class FontStyle(enum.Enum):
    """Font style options.

    Enumerates the slant variants a font can be rendered with.
    """

    NORMAL = 0
    ITALIC = 1
    OBLIQUE = 2


class FontWeight(enum.Enum):
    """Font weight options.

    Enumerates the thickness variants a font can be rendered with.
    """

    NORMAL = 0
    BOLD = 1
    BOLDER = 2
    LIGHTER = 3


class TextAnchor(enum.Enum):
    """Text anchor options.

    Enumerates how text is aligned relative to its anchor point.
    """

    START = 0
    MIDDLE = 1
    END = 2


class FillRule(enum.Enum):
    """Fill rule for complex shapes.

    Enumerates the algorithms used to determine the interior of a shape.
    """

    NONZERO = 0
    EVENODD = 1


PRESENTATION_ATTRIBUTES = {
    "fill": {
        "initial": black,
        "inherited": True,
    },
    "fill_rule": {
        "initial": FillRule.NONZERO,
        "inherited": True,
    },
    "filter": {
        "initial": NoneValue,
        "inherited": False,
    },
    "font_family": {
        "initial": None,
        "inherited": True,
    },
    "font_size": {
        "initial": None,
        "inherited": True,
    },
    "font_style": {
        "initial": FontStyle.NORMAL,
        "inherited": True,
    },
    "font_weight": {
        "initial": FontWeight.NORMAL,
        "inherited": True,
    },
    "stroke": {
        "initial": NoneValue,
        "inherited": True,
    },
    "stroke_dasharray": {
        "initial": NoneValue,
        "inherited": True,
    },
    "stroke_dashoffset": {
        "initial": 0.0,
        "inherited": True,
    },
    "stroke_width": {
        "initial": 1.0,
        "inherited": True,
    },
    "text_anchor": {
        "initial": TextAnchor.START,
        "inherited": True,
    },
    "transform": {
        "initial": NoneValue,
        "inherited": False,
    },
}

DEFAULT_FONT_FAMILY = (
    "Arial" if platform.system() in ("Darwin", "Windows") else "DejaVu Sans"
)

INITIAL_VALUES = {
    "font_family": DEFAULT_FONT_FAMILY,
    "font_size": 16.0,
}

FONT_WEIGHT_TO_VALUE = {
    FontWeight.NORMAL: 400,
    FontWeight.BOLD: 700,
}


def get_initial_value(attr_name: str) -> typing.Any:
    """Get the initial value of a presentation attribute.

    Args:
        attr_name: Name of the attribute.

    Returns:
        The initial value.

    Raises:
        KeyError: If `attr_name` is not a known presentation attribute.
    """
    attr_value = PRESENTATION_ATTRIBUTES[attr_name]["initial"]
    if attr_value is None:
        attr_value = INITIAL_VALUES[attr_name]
    return attr_value


@dataclasses.dataclass(frozen=True, kw_only=True)
class DrawingElement(abc.ABC):
    """Abstract base class for drawing elements.

    Drawing elements carry the SVG-like presentation attributes shared by all
    primitives.
    """

    class_: str | None = dataclasses.field(
        default=None,
        metadata={"description": "The class name of the drawing element"},
    )
    fill: NoneValueType | Color | None = dataclasses.field(
        default=None,
        metadata={"description": "The fill color of the drawing element"},
    )
    fill_rule: FillRule | None = dataclasses.field(
        default=None,
        metadata={"description": "The fill rule of the drawing element"},
    )
    filter: NoneValueType | Filter | None = dataclasses.field(
        default=None,
        metadata={"description": "The filter of the drawing element"},
    )
    font_family: str | None = dataclasses.field(
        default=None,
        metadata={"description": "The font family of the drawing element"},
    )
    font_size: float | None = dataclasses.field(
        default=None,
        metadata={"description": "The font size of the drawing element"},
    )
    font_style: FontStyle | None = dataclasses.field(
        default=None,
        metadata={"description": "The font style of the drawing element"},
    )
    font_weight: FontWeight | int | None = dataclasses.field(
        default=None,
        metadata={"description": "The font weight of the drawing element"},
    )
    id_: str | None = dataclasses.field(
        default=None, metadata={"description": "The id of the drawing element"}
    )
    stroke: NoneValueType | Color | None = dataclasses.field(
        default=None,
        metadata={"description": "The stroke color of the drawing element"},
    )
    stroke_dasharray: NoneValueType | tuple[float, ...] | None = dataclasses.field(
        default=None,
        metadata={"description": "The stroke dasharray of the drawing element"},
    )
    stroke_dashoffset: NoneValueType | float | None = dataclasses.field(
        default=None,
        metadata={"description": "The stroke dashoffset of the drawing element"},
    )
    stroke_width: NoneValueType | float | None = dataclasses.field(
        default=None,
        metadata={"description": "The stroke width of the drawing element"},
    )
    text_anchor: TextAnchor | None = dataclasses.field(
        default=None,
        metadata={"description": "The text anchor of the drawing element"},
    )
    transform: NoneValueType | tuple[Transformation] | None = dataclasses.field(
        default=None,
        metadata={"description": "The transform of the drawing element"},
    )

    @abc.abstractmethod
    def to_geometry(
        self,
    ) -> list[
        Segment | QuadraticBezierCurve | CubicBezierCurve | GeometryEllipticalArc
    ]:
        """Convert to a list of geometry primitives.

        Returns:
            A list of geometry primitives.
        """
        pass

    def bbox(self) -> Bbox:
        """Get the bounding box.

        Returns:
            The bounding box.
        """
        primitives = self.to_geometry()
        if not primitives:
            return Bbox(Point(0, 0), 0, 0)
        bboxes = [p.bbox() for p in primitives]
        return Bbox.union(bboxes)

    def get_filter_region(self) -> Bbox | None:
        """Get the filter region.

        Returns:
            The filter region bbox, or `None` when the element has no
            filter (`filter` is `None` or `NoneValue`).
        """
        if self.filter is None or self.filter is NoneValue:
            return None
        if self.filter.filter_units == FilterUnits.OBJECT_BOUNDING_BOX:
            bbox = self.bbox()
            north_west = bbox.north_west()
            if isinstance(self.filter.x, float):
                sx = self.filter.x
            else:
                sx = float(self.filter.x.rstrip("%")) / 100
            px = north_west.x + bbox.width * sx
            if isinstance(self.filter.y, float):
                sy = self.filter.y
            else:
                sy = float(self.filter.y.rstrip("%")) / 100
            py = north_west.y + bbox.height * sy
            if isinstance(self.filter.width, float):
                swidth = self.filter.width
            else:
                swidth = float(self.filter.width.rstrip("%")) / 100
            width = bbox.width * swidth
            if isinstance(self.filter.height, float):
                sheight = self.filter.height
            else:
                sheight = float(self.filter.height.rstrip("%")) / 100
            height = bbox.height * sheight
            filter_region = Bbox(
                Point(px + width / 2, py + height / 2),
                width,
                height,
            )
        else:
            filter_region = Bbox(
                Point(
                    self.filter.x + self.filter.width / 2,
                    self.filter.y + self.filter.height / 2,
                ),
                self.filter.width,
                self.filter.height,
            )
        return filter_region


@dataclasses.dataclass(frozen=True, kw_only=True)
class Text(DrawingElement):
    """Text drawing element.

    Renders a string of text at a given position.
    """

    text: str = dataclasses.field(
        metadata={"description": "The value of the text element"}
    )
    point: Point = dataclasses.field(
        metadata={"description": "The position of the text element"}
    )

    @property
    def x(self):
        """X coordinate of the text position."""
        return self.point.x

    @property
    def y(self):
        """Y coordinate of the text position."""
        return self.point.y

    def transformed(self, transformation: Transformation) -> typing_extensions.Self:
        """Apply a transformation.

        Args:
            transformation: The transformation.

        Returns:
            A copy of the text element.
        """
        return copy.deepcopy(self)

    def to_geometry(
        self,
    ) -> list[
        Segment | QuadraticBezierCurve | CubicBezierCurve | GeometryEllipticalArc
    ]:
        """Convert to a list of geometry primitives.

        Text has no geometry primitives.

        Returns:
            An empty list.
        """
        return []


@dataclasses.dataclass(frozen=True, kw_only=True)
class Group(DrawingElement):
    """Group of drawing elements.

    Bundles several drawing elements so they share presentation attributes.
    """

    elements: tuple[DrawingElement] = dataclasses.field(
        default_factory=tuple,
        metadata={"description": "The elements of the group element"},
    )

    def transformed(self, transformation: Transformation) -> typing_extensions.Self:
        """Apply a transformation to all elements.

        Args:
            transformation: The transformation.

        Returns:
            A new Group with transformed elements.
        """
        elements = []
        for element in self.elements:
            elements.append(element.transformed(transformation))
        return dataclasses.replace(self, elements=tuple(elements))

    def to_geometry(
        self,
    ) -> list[
        Segment | QuadraticBezierCurve | CubicBezierCurve | GeometryEllipticalArc
    ]:
        """Convert to a list of geometry primitives.

        Returns:
            A list of geometry primitives from all child elements.
        """
        return drawing_elements_to_geometry(self.elements)


@dataclasses.dataclass(frozen=True)
class PathAction(abc.ABC):
    """Abstract base class for path actions.

    Path actions are the individual drawing commands that make up a path.
    """

    pass


@dataclasses.dataclass(frozen=True)
class MoveTo(PathAction):
    """Move to a point (start a new subpath).

    Repositions the current point without drawing, starting a new subpath.
    """

    point: Point = dataclasses.field(
        metadata={"description": "The point of the move to action"}
    )

    @property
    def x(self):
        """X coordinate."""
        return self.point.x

    @property
    def y(self):
        """Y coordinate."""
        return self.point.y

    def transformed(
        self,
        transformation: Transformation,
        current_point: Point,
    ) -> "MoveTo":
        """Apply a transformation.

        Args:
            transformation: The transformation.
            current_point: Current point (unused).

        Returns:
            A new MoveTo with transformed point.
        """
        return MoveTo(self.point.transformed(transformation))


@dataclasses.dataclass(frozen=True)
class LineTo(PathAction):
    """Draw a line to a point.

    Draws a straight segment from the current point to the end point.
    """

    point: Point = dataclasses.field(
        metadata={"description": "The point of the line to action"}
    )

    @property
    def x(self):
        """X coordinate."""
        return self.point.x

    @property
    def y(self):
        """Y coordinate."""
        return self.point.y

    def transformed(
        self,
        transformation: Transformation,
        current_point: Point,
    ) -> typing_extensions.Self:
        """Apply a transformation.

        Args:
            transformation: The transformation.
            current_point: Current point (unused).

        Returns:
            A new LineTo with transformed point.
        """
        return LineTo(self.point.transformed(transformation))

    def to_geometry(self, current_point: Point) -> Segment:
        """Convert to a segment.

        Args:
            current_point: Start point.

        Returns:
            A Segment from current_point to self.point.
        """
        return Segment(current_point, self.point)


@dataclasses.dataclass(frozen=True)
class EllipticalArc(PathAction):
    """Draw an elliptical arc.

    Draws an arc of an ellipse from the current point to the end point.
    """

    point: Point = dataclasses.field(
        metadata={"description": "The point of the elliptical arc action"}
    )
    rx: float = dataclasses.field(
        metadata={"description": "The x-radius of the elliptical arc action"}
    )
    ry: float = dataclasses.field(
        metadata={"description": "The y-radius of the elliptical arc action"}
    )
    x_axis_rotation: float = dataclasses.field(
        metadata={"description": "The x axis rotation of the elliptical arc action"}
    )
    arc_flag: int = dataclasses.field(
        metadata={"description": "The arc flag of the elliptical arc action"}
    )
    sweep_flag: int = dataclasses.field(
        metadata={"description": "The sweep flag of the elliptical arc action"}
    )

    @property
    def x(self):
        """X coordinate."""
        return self.point.x

    @property
    def y(self):
        """Y coordinate."""
        return self.point.y

    def transformed(
        self,
        transformation: Transformation,
        current_point: Point,
    ) -> "EllipticalArc":
        """Apply a transformation.

        Args:
            transformation: The transformation.
            current_point: Start point.

        Returns:
            A new EllipticalArc with transformed parameters.
        """
        east = Point(
            math.cos(self.x_axis_rotation) * self.rx,
            math.sin(self.x_axis_rotation) * self.rx,
        )
        north = Point(
            math.cos(self.x_axis_rotation) * self.ry,
            math.sin(self.x_axis_rotation) * self.ry,
        )
        new_center = Point(0, 0).transformed(transformation)
        new_east = east.transformed(transformation)
        new_north = north.transformed(transformation)
        new_rx = Segment(new_center, new_east).length()
        new_ry = Segment(new_center, new_north).length()
        new_end_point = self.point.transformed(transformation)
        new_x_axis_rotation = math.degrees(
            Line(new_center, new_east).get_angle_to_horizontal()
        )
        return EllipticalArc(
            new_end_point,
            new_rx,
            new_ry,
            new_x_axis_rotation,
            self.arc_flag,
            self.sweep_flag,
        )

    def to_geometry(self, current_point: Point) -> GeometryEllipticalArc:
        """Convert to geometry.

        Args:
            current_point: Start point.

        Returns:
            An EllipticalArc geometry.
        """
        return GeometryEllipticalArc(
            current_point,
            self.point,
            self.rx,
            self.ry,
            self.x_axis_rotation,
            self.arc_flag,
            self.sweep_flag,
        )


@dataclasses.dataclass(frozen=True)
class CurveTo(PathAction):
    """Draw a cubic Bezier curve.

    Draws a cubic Bezier curve from the current point to the end point.
    """

    point: Point = dataclasses.field(
        metadata={"description": "The point of the curve to action"}
    )
    control_point1: Point = dataclasses.field(
        metadata={"description": "The first control point of the curve to action"}
    )
    control_point2: Point = dataclasses.field(
        metadata={"description": "The second control point of the curve to action"}
    )

    @property
    def x(self):
        """X coordinate."""
        return self.point.x

    @property
    def y(self):
        """Y coordinate."""
        return self.point.y

    def transformed(
        self,
        transformation: Transformation,
        current_point: Point,
    ) -> "CurveTo":
        """Apply a transformation.

        Args:
            transformation: The transformation.
            current_point: Start point (unused).

        Returns:
            A new CurveTo with transformed points.
        """
        return CurveTo(
            self.point.transformed(transformation),
            self.control_point1.transformed(transformation),
            self.control_point2.transformed(transformation),
        )

    def to_geometry(self, current_point: Point) -> CubicBezierCurve:
        """Convert to CubicBezierCurve geometry.

        Args:
            current_point: Start point.

        Returns:
            A CubicBezierCurve.
        """
        return CubicBezierCurve(
            current_point,
            self.point,
            self.control_point1,
            self.control_point2,
        )


@dataclasses.dataclass(frozen=True)
class QuadraticCurveTo(PathAction):
    """Draw a quadratic Bezier curve.

    Draws a quadratic Bezier curve from the current point to the end point.
    """

    point: Point = dataclasses.field(
        metadata={"description": "The point of the quadratic curve to action"}
    )
    control_point: Point = dataclasses.field(
        metadata={"description": "The control point of the quadratic curve to action"}
    )

    @property
    def x(self):
        """X coordinate."""
        return self.point.x

    @property
    def y(self):
        """Y coordinate."""
        return self.point.y

    def transformed(
        self,
        transformation: Transformation,
        current_point: Point,
    ) -> "QuadraticCurveTo":
        """Apply a transformation.

        Args:
            transformation: The transformation.
            current_point: Start point (unused).

        Returns:
            A new QuadraticCurveTo with transformed points.
        """
        return QuadraticCurveTo(
            self.point.transformed(transformation),
            self.control_point.transformed(transformation),
        )

    def to_curve_to(self, current_point: Point) -> CurveTo:
        """Convert to cubic CurveTo.

        Args:
            current_point: Start point.

        Returns:
            An equivalent CurveTo.
        """
        p1 = current_point
        p2 = self.point
        control_point1 = p1 + (self.control_point - p1) * (2 / 3)
        control_point2 = p2 + (self.control_point - p2) * (2 / 3)
        return CurveTo(p2, control_point1, control_point2)

    def to_geometry(self, current_point: Point) -> QuadraticBezierCurve:
        """Convert to QuadraticBezierCurve geometry.

        Args:
            current_point: Start point.

        Returns:
            A QuadraticBezierCurve.
        """
        return QuadraticBezierCurve(
            current_point,
            self.point,
            self.control_point,
        )


@dataclasses.dataclass(frozen=True)
class ClosePath(PathAction):
    """Close the current path.

    Draws a straight segment back to the start of the current subpath.
    """

    def transformed(
        self,
        transformation: Transformation,
        current_point: Point,
    ) -> "ClosePath":
        """Apply a transformation.

        Args:
            transformation: The transformation (unused).
            current_point: Current point (unused).

        Returns:
            A new ClosePath.
        """
        return ClosePath()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Path(DrawingElement):
    """Path drawing element composed of path actions.

    A path is drawn by executing its sequence of path actions in order.
    """

    actions: tuple[PathAction] = dataclasses.field(
        default_factory=tuple,
        metadata={"description": "The actions of the path"},
    )

    def transformed(self, transformation: Transformation) -> typing_extensions.Self:
        """Apply a transformation to all actions.

        Args:
            transformation: The transformation.

        Returns:
            A new Path with transformed actions.
        """
        actions = []
        current_point = None
        for action in self.actions:
            new_action = action.transformed(transformation, current_point)
            actions.append(new_action)
            if hasattr(action, "point"):
                current_point = action.point
            else:
                current_point = None
        return dataclasses.replace(self, actions=tuple(actions))

    def to_geometry(
        self,
    ) -> list[
        Segment | QuadraticBezierCurve | CubicBezierCurve | GeometryEllipticalArc
    ]:
        """Convert to a list of geometry primitives.

        Returns:
            A list of Segment, QuadraticBezierCurve, CubicBezierCurve,
            or EllipticalArc objects.
        """
        primitives = []
        current_point = Point(0, 0)
        initial_point = current_point
        for action in self.actions:
            if isinstance(action, MoveTo):
                current_point = action.point
                initial_point = current_point
            elif isinstance(action, ClosePath):
                if (
                    current_point.x != initial_point.x
                    or current_point.y != initial_point.y
                ):
                    primitives.append(Segment(current_point, initial_point))
                current_point = initial_point
            else:
                primitives.append(action.to_geometry(current_point))
                current_point = action.point
        return primitives


@dataclasses.dataclass(frozen=True, kw_only=True)
class Ellipse(DrawingElement):
    """Ellipse drawing element.

    Draws an ellipse from a center point and two radii.
    """

    point: Point = dataclasses.field(
        metadata={"description": "The point of the ellipse"}
    )
    rx: float = dataclasses.field(
        metadata={"description": "The x-radius of the ellipse"}
    )
    ry: float = dataclasses.field(
        metadata={"description": "The y-radius of the ellipse"}
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "rx", round(self.rx, ROUNDING))
        object.__setattr__(self, "ry", round(self.ry, ROUNDING))

    @property
    def x(self):
        """X coordinate of center."""
        return self.point.x

    @property
    def y(self):
        """Y coordinate of center."""
        return self.point.y

    def to_path(self) -> Path:
        """Convert to a Path.

        Returns:
            A Path approximating the ellipse.
        """
        north = self.point + (0, -self.ry)
        east = self.point + (self.rx, 0)
        south = self.point + (0, self.ry)
        west = self.point - (self.rx, 0)
        actions = [
            MoveTo(north),
            EllipticalArc(east, self.rx, self.ry, 0, 0, 1),
            EllipticalArc(south, self.rx, self.ry, 0, 0, 1),
            EllipticalArc(west, self.rx, self.ry, 0, 0, 1),
            EllipticalArc(north, self.rx, self.ry, 0, 0, 1),
            ClosePath(),
        ]
        path = Path(
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            filter=self.filter,
            actions=actions,
        )
        return path

    def transformed(self, transformation: Transformation) -> Path:
        """Apply a transformation.

        Args:
            transformation: The transformation.

        Returns:
            A transformed Path.
        """
        path = self.to_path()
        return path.transformed(transformation)

    def to_geometry(
        self,
    ) -> list[
        Segment | QuadraticBezierCurve | CubicBezierCurve | GeometryEllipticalArc
    ]:
        """Convert to a list of geometry primitives.

        Returns:
            A list of geometry primitives.
        """
        return self.to_path().to_geometry()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Rectangle(DrawingElement):
    """Rectangle drawing element with optional rounded corners.

    Draws a rectangle from a corner point, a size, and corner radii.
    """

    point: Point = dataclasses.field(
        metadata={"description": "The point of the rectangle"}
    )
    width: float = dataclasses.field(
        metadata={"description": "The width of the rectangle"}
    )
    height: float = dataclasses.field(
        metadata={"description": "The height of the rectangle"}
    )
    rx: float = dataclasses.field(
        metadata={"description": "The x-radius of the rounded corners of the rectangle"}
    )
    ry: float = dataclasses.field(
        metadata={"description": "The y-radius of the rounded corners of the rectangle"}
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "width", round(self.width, ROUNDING))
        object.__setattr__(self, "height", round(self.height, ROUNDING))
        object.__setattr__(self, "rx", round(self.rx, ROUNDING))
        object.__setattr__(self, "ry", round(self.ry, ROUNDING))

    @property
    def x(self):
        """X coordinate of top-left."""
        return self.point.x

    @property
    def y(self):
        """Y coordinate of top-left."""
        return self.point.y

    def to_path(self) -> Path:
        """Convert to a Path.

        Returns:
            A Path representing the rectangle.
        """
        x = self.point.x
        y = self.point.y
        rx = self.rx
        ry = self.ry
        width = self.width
        height = self.height
        actions = [
            MoveTo(Point(x + rx, y)),
            LineTo(Point(x + width - rx, y)),
        ]
        if rx > 0 and ry > 0:
            actions.append(EllipticalArc(Point(x + width, y + ry), rx, ry, 0, 0, 1))
        actions.append(LineTo(Point(x + width, y + height - ry)))
        if rx > 0 and ry > 0:
            actions.append(
                EllipticalArc(
                    Point(x + width - rx, y + height),
                    rx,
                    ry,
                    0,
                    0,
                    1,
                )
            )
        actions.append(LineTo(Point(x + rx, y + height)))
        if rx > 0 and ry > 0:
            actions.append(EllipticalArc(Point(x, y + height - ry), rx, ry, 0, 0, 1))
        actions.append(LineTo(Point(x, y + ry)))
        if rx > 0 and ry > 0:
            actions.append(EllipticalArc(Point(x + rx, y), rx, ry, 0, 0, 1))
        actions.append(ClosePath())
        path = Path(
            stroke_width=self.stroke_width,
            stroke=self.stroke,
            fill=self.fill,
            transform=self.transform,
            filter=self.filter,
            actions=actions,
        )
        return path

    def transformed(self, transformation: Transformation) -> Path:
        """Apply a transformation.

        Args:
            transformation: The transformation.

        Returns:
            A transformed Path.
        """
        path = self.to_path()
        return path.transformed(transformation)

    def to_geometry(
        self,
    ) -> list[
        Segment | QuadraticBezierCurve | CubicBezierCurve | GeometryEllipticalArc
    ]:
        """Convert to a list of geometry primitives.

        Returns:
            A list of geometry primitives.
        """
        return self.to_path().to_geometry()


def drawing_elements_to_geometry(
    drawing_elements: collections.abc.Sequence[DrawingElement],
) -> list[Segment | QuadraticBezierCurve | CubicBezierCurve | GeometryEllipticalArc]:
    """Convert drawing elements to geometry primitives.

    Args:
        drawing_elements: Sequence of drawing elements.

    Returns:
        A list of geometry primitives.
    """
    primitives = []
    for drawing_element in drawing_elements:
        primitives.extend(drawing_element.to_geometry())
    return primitives


def get_drawing_elements_border(
    drawing_elements: collections.abc.Sequence[DrawingElement],
    point: Point,
    center: Point | None = None,
) -> Point | None:
    """Get border point in a direction from center.

    Args:
        drawing_elements: Drawing elements.
        point: Direction point.
        center: Optional center point.

    Returns:
        The border point or None.
    """
    primitives = drawing_elements_to_geometry(drawing_elements)
    return get_primitives_border(primitives=primitives, point=point, center=center)


def get_drawing_elements_angle(
    drawing_elements: collections.abc.Sequence[DrawingElement],
    angle: float,
    unit: str = "degrees",
    center: Point | None = None,
) -> Point | None:
    """Get border point at an angle from center.

    Args:
        drawing_elements: Drawing elements.
        angle: The angle.
        unit: Unit ('degrees' or 'radians').
        center: Optional center point.

    Returns:
        The border point or None.
    """
    primitives = drawing_elements_to_geometry(drawing_elements)
    return get_primitives_angle(
        primitives=primitives, angle=angle, unit=unit, center=center
    )


def get_drawing_elements_bbox(
    drawing_elements: collections.abc.Sequence[DrawingElement],
) -> Bbox:
    """Get bounding box of drawing elements.

    Args:
        drawing_elements: Drawing elements.

    Returns:
        The bounding box.
    """
    primitives = drawing_elements_to_geometry(drawing_elements)
    bboxes = [p.bbox() for p in primitives]
    return Bbox.union(bboxes)


def get_drawing_elements_anchor_point(
    drawing_elements: collections.abc.Sequence[DrawingElement],
    anchor_point: str,
    center: Point | None = None,
) -> Point:
    """Get anchor point of drawing elements.

    Args:
        drawing_elements: Drawing elements.
        anchor_point: Name of anchor point.
        center: Optional center point.

    Returns:
        The anchor point.
    """
    primitives = drawing_elements_to_geometry(drawing_elements)
    return get_primitives_anchor_point(
        primitives=primitives, anchor_point=anchor_point, center=center
    )
