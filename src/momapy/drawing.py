"""SVG-like drawing elements for momapy.

This module provides classes for creating and manipulating SVG-like drawing
elements including paths, shapes, text, filters, and groups. It supports
transformations, styling attributes, and conversion to/from shapely geometries.

Examples:
    >>> from momapy.drawing import Path, MoveTo, LineTo, Rectangle, Text
    >>> from momapy.geometry import Point
    >>> from momapy.coloring import red, blue
    >>> # Create a simple path
    >>> path = Path(
    ...     actions=(
    ...         MoveTo(Point(0, 0)),
    ...         LineTo(Point(10, 10)),
    ...     ),
    ...     stroke=red,
    ...     stroke_width=2.0
    ... )
    >>> # Create a rectangle
    >>> rect = Rectangle(
    ...     point=Point(5, 5),
    ...     width=10,
    ...     height=10,
    ...     fill=blue,
    ...     stroke=red
    ... )
    >>> # Create text
    >>> text = Text(
    ...     text="Hello",
    ...     point=Point(10, 10),
    ...     font_size=14.0
    ... )
"""

import abc
import dataclasses
import math
import copy
import enum
import typing
import typing_extensions
import collections.abc

import shapely.geometry
import shapely.affinity
import shapely.ops

import momapy.geometry
import momapy.coloring
import momapy.utils


class NoneValueType(object):
    """Singleton type for None values (as in SVG)."""

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __eq__(self, other):
        return type(self) is type(other)

    def __hash__(self):
        return id(NoneValue)


NoneValue = NoneValueType()
"""A singleton value for type `NoneValueType`."""


@dataclasses.dataclass(frozen=True)
class FilterEffect(abc.ABC):
    """Abstract base class for filter effects."""

    result: str | None = dataclasses.field(
        default=None, metadata={"description": "The name of the result"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class DropShadowEffect(FilterEffect):
    """Drop shadow filter effect.

    Attributes:
        dx: Horizontal offset of the shadow.
        dy: Vertical offset of the shadow.
        std_deviation: Standard deviation for blur.
        flood_opacity: Opacity of the shadow.
        flood_color: Color of the shadow.
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
    flood_color: momapy.coloring.Color = dataclasses.field(
        default=momapy.coloring.black,
        metadata={"description": "The color of the shadow"},
    )

    def to_compat(self) -> list[FilterEffect]:
        """Convert to more compatible filter effects.

        Returns:
            List of equivalent filter effects.
        """
        flood_effect = FloodEffect(
            result=momapy.utils.make_uuid4_as_str(),
            flood_opacity=self.flood_opacity,
            flood_color=self.flood_color,
        )
        composite_effect1 = CompositeEffect(
            in_=flood_effect.result,
            in2=FilterEffectInput.SOURCE_GRAPHIC,
            operator=CompositionOperator.IN,
            result=momapy.utils.make_uuid4_as_str(),
        )
        gaussian_blur_effect = GaussianBlurEffect(
            in_=composite_effect1.result,
            std_deviation=self.std_deviation,
            result=momapy.utils.make_uuid4_as_str(),
        )
        offset_effect = OffsetEffect(
            in_=gaussian_blur_effect.result,
            dx=self.dx,
            dy=self.dy,
            result=momapy.utils.make_uuid4_as_str(),
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
    """Filter effect input types."""

    SOURCE_GRAPHIC = 0
    SOURCE_ALPHA = 1
    BACKGROUND_IMAGE = 2
    BACKGROUND_ALPHA = 3
    FILL_PAINT = 4
    STROKE_PAINT = 5


class CompositionOperator(enum.Enum):
    """Composition operators for filter effects."""

    OVER = 0
    IN = 1
    OUT = 2
    ATOP = 3
    XOR = 4
    LIGHTER = 5
    ARTIHMETIC = 6


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompositeEffect(FilterEffect):
    """Composite filter effect.

    Attributes:
        in_: First input or filter effect name.
        in2: Second input or filter effect name.
        operator: Composition operator.
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


@dataclasses.dataclass(frozen=True, kw_only=True)
class FloodEffect(FilterEffect):
    """Flood filter effect.

    Attributes:
        flood_color: Color of the flood.
        flood_opacity: Opacity of the flood.
    """

    flood_color: momapy.coloring.Color = dataclasses.field(
        default=momapy.coloring.black,
        metadata={"description": "The color of the flood effect"},
    )
    flood_opacity: float = dataclasses.field(
        default=1.0,
        metadata={"description": "The opacity of the flood effect"},
    )


class EdgeMode(enum.Enum):
    """Edge mode for blur effects."""

    DUPLICATE = 0
    WRAP = 1


@dataclasses.dataclass(frozen=True, kw_only=True)
class GaussianBlurEffect(FilterEffect):
    """Gaussian blur filter effect.

    Attributes:
        in_: Input or filter effect name.
        std_deviation: Standard deviation for blur.
        edge_mode: Edge handling mode.
    """

    in_: FilterEffectInput | str | None = None
    std_deviation: float = 0.0
    edge_mode: NoneValueType | EdgeMode = NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class OffsetEffect(FilterEffect):
    """Offset filter effect.

    Attributes:
        in_: Input or filter effect name.
        dx: Horizontal offset.
        dy: Vertical offset.
    """

    in_: FilterEffectInput | str | None = None
    dx: float = 0.0
    dy: float = 0.0


class FilterUnits(enum.Enum):
    """Units for filter regions."""

    USER_SPACE_ON_USE = 0
    OBJECT_BOUNDING_BOX = 1


@dataclasses.dataclass(frozen=True, kw_only=True)
class Filter(object):
    """Filter with multiple effects.

    Attributes:
        id_: Unique identifier.
        filter_units: Units for filter region.
        effects: Tuple of filter effects.
        width: Width of filter region.
        height: Height of filter region.
        x: X position of filter region.
        y: Y position of filter region.
    """

    id_: str = dataclasses.field(
        hash=False,
        compare=False,
        default_factory=momapy.utils.make_uuid4_as_str,
    )
    filter_units: FilterUnits = FilterUnits.OBJECT_BOUNDING_BOX
    effects: tuple[FilterEffect] = dataclasses.field(default_factory=tuple)
    width: float | str = "120%"
    height: float | str = "120%"
    x: float | str = "-10%"
    y: float | str = "-10%"

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
    """Font style options."""

    NORMAL = 0
    ITALIC = 1
    OBLIQUE = 2


class FontWeight(enum.Enum):
    """Font weight options."""

    NORMAL = 0
    BOLD = 1
    BOLDER = 2
    LIGHTER = 3


class TextAnchor(enum.Enum):
    """Text anchor options."""

    START = 0
    MIDDLE = 1
    END = 2


class FillRule(enum.Enum):
    """Fill rule for complex shapes."""

    NONZERO = 0
    EVENODD = 1


PRESENTATION_ATTRIBUTES = {
    "fill": {
        "initial": momapy.coloring.black,
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

INITIAL_VALUES = {
    "font_family": "Arial",
    "font_size": 16.0,
}

FONT_WEIGHT_TO_VALUE = {
    FontWeight.NORMAL: 400,
    FontWeight.BOLD: 700,
}


def get_initial_value(attr_name: str):
    """Get the initial value of a presentation attribute.

    Args:
        attr_name: Name of the attribute.

    Returns:
        The initial value.
    """
    attr_value = PRESENTATION_ATTRIBUTES[attr_name]["initial"]
    if attr_value is None:
        attr_value = INITIAL_VALUES[attr_name]
    return attr_value


@dataclasses.dataclass(frozen=True, kw_only=True)
class DrawingElement(abc.ABC):
    """Abstract base class for drawing elements.

    Attributes:
        class_: CSS class name.
        fill: Fill color.
        fill_rule: Fill rule for complex shapes.
        filter: Filter to apply.
        font_family: Font family.
        font_size: Font size.
        font_style: Font style.
        font_weight: Font weight.
        id_: Element ID.
        stroke: Stroke color.
        stroke_dasharray: Stroke dash pattern.
        stroke_dashoffset: Stroke dash offset.
        stroke_width: Stroke width.
        text_anchor: Text anchor.
        transform: Transformation tuple.
    """

    class_: str | None = dataclasses.field(
        default=None,
        metadata={"description": "The class name of the drawing element"},
    )
    fill: NoneValueType | momapy.coloring.Color | None = dataclasses.field(
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
    stroke: NoneValueType | momapy.coloring.Color | None = dataclasses.field(
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
    transform: NoneValueType | tuple[momapy.geometry.Transformation] | None = (
        dataclasses.field(
            default=None,
            metadata={"description": "The transform of the drawing element"},
        )
    )

    @abc.abstractmethod
    def to_shapely(self, to_polygons=False) -> shapely.GeometryCollection:
        """Convert to a shapely geometry collection.

        Args:
            to_polygons: Whether to convert to polygons.

        Returns:
            A shapely GeometryCollection.
        """
        pass

    def bbox(self) -> momapy.geometry.Bbox:
        """Get the bounding box.

        Returns:
            The bounding box.
        """
        bounds = self.to_shapely().bounds
        return momapy.geometry.Bbox(
            momapy.geometry.Point(
                (bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2
            ),
            bounds[2] - bounds[0],
            bounds[3] - bounds[1],
        )

    def get_filter_region(self) -> momapy.geometry.Bbox:
        """Get the filter region.

        Returns:
            The filter region bbox.
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
            filter_region = momapy.geometry.Bbox(
                momapy.geometry.Point(px + width / 2, py + height / 2),
                width,
                height,
            )
        else:
            filter_region = momapy.geometry.Bbox(
                momapy.geometry.Point(
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

    Attributes:
        text: The text content.
        point: Position of the text.
    """

    text: str = dataclasses.field(
        metadata={"description": "The value of the text element"}
    )
    point: momapy.geometry.Point = dataclasses.field(
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

    def transformed(
        self, transformation: momapy.geometry.Transformation
    ) -> typing_extensions.Self:
        """Apply a transformation.

        Args:
            transformation: The transformation.

        Returns:
            A copy of the text element.
        """
        return copy.deepcopy(self)

    def to_shapely(self, to_polygons=False) -> shapely.GeometryCollection:
        """Convert to shapely geometry.

        Args:
            to_polygons: Whether to convert to polygons.

        Returns:
            A GeometryCollection containing the point.
        """
        return shapely.geometry.GeometryCollection([self.point.to_shapely()])


@dataclasses.dataclass(frozen=True, kw_only=True)
class Group(DrawingElement):
    """Group of drawing elements.

    Attributes:
        elements: Tuple of child elements.
    """

    elements: tuple[DrawingElement] = dataclasses.field(
        default_factory=tuple,
        metadata={"description": "The elements of the group element"},
    )

    def transformed(
        self, transformation: momapy.geometry.Transformation
    ) -> typing_extensions.Self:
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

    def to_shapely(self, to_polygons=False) -> shapely.GeometryCollection:
        """Convert to shapely geometry.

        Args:
            to_polygons: Whether to convert to polygons.

        Returns:
            A GeometryCollection of all elements.
        """
        return drawing_elements_to_shapely(self.elements)


@dataclasses.dataclass(frozen=True)
class PathAction(abc.ABC):
    """Abstract base class for path actions."""

    pass


@dataclasses.dataclass(frozen=True)
class MoveTo(PathAction):
    """Move to a point (start a new subpath).

    Attributes:
        point: The point to move to.
    """

    point: momapy.geometry.Point = dataclasses.field(
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
        transformation: momapy.geometry.Transformation,
        current_point: momapy.geometry.Point,
    ) -> "MoveTo":
        """Apply a transformation.

        Args:
            transformation: The transformation.
            current_point: Current point (unused).

        Returns:
            A new MoveTo with transformed point.
        """
        return MoveTo(momapy.geometry.transform_point(self.point, transformation))


@dataclasses.dataclass(frozen=True)
class LineTo(PathAction):
    """Draw a line to a point.

    Attributes:
        point: The end point.
    """

    point: momapy.geometry.Point = dataclasses.field(
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
        transformation: momapy.geometry.Transformation,
        current_point: momapy.geometry.Point,
    ):
        """Apply a transformation.

        Args:
            transformation: The transformation.
            current_point: Current point (unused).

        Returns:
            A new LineTo with transformed point.
        """
        return LineTo(momapy.geometry.transform_point(self.point, transformation))

    def to_geometry(
        self, current_point: momapy.geometry.Point
    ) -> momapy.geometry.Segment:
        """Convert to a segment.

        Args:
            current_point: Start point.

        Returns:
            A Segment from current_point to self.point.
        """
        return momapy.geometry.Segment(current_point, self.point)

    def to_shapely(self, current_point: momapy.geometry.Point) -> shapely.LineString:
        """Convert to shapely LineString.

        Args:
            current_point: Start point.

        Returns:
            A LineString.
        """
        return self.to_geometry(current_point).to_shapely()


@dataclasses.dataclass(frozen=True)
class EllipticalArc(PathAction):
    """Draw an elliptical arc.

    Attributes:
        point: End point.
        rx: X-radius.
        ry: Y-radius.
        x_axis_rotation: Rotation of x-axis.
        arc_flag: Large arc flag.
        sweep_flag: Sweep flag.
    """

    point: momapy.geometry.Point = dataclasses.field(
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
        transformation: momapy.geometry.Transformation,
        current_point: momapy.geometry.Point,
    ) -> "EllipticalArc":
        """Apply a transformation.

        Args:
            transformation: The transformation.
            current_point: Start point.

        Returns:
            A new EllipticalArc with transformed parameters.
        """
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
        new_end_point = momapy.geometry.transform_point(self.point, transformation)
        new_x_axis_rotation = math.degrees(
            momapy.geometry.get_angle_to_horizontal_of_line(
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

    def to_geometry(
        self, current_point: momapy.geometry.Point
    ) -> momapy.geometry.EllipticalArc:
        """Convert to geometry.

        Args:
            current_point: Start point.

        Returns:
            An EllipticalArc geometry.
        """
        return momapy.geometry.EllipticalArc(
            current_point,
            self.point,
            self.rx,
            self.ry,
            self.x_axis_rotation,
            self.arc_flag,
            self.sweep_flag,
        )

    def to_shapely(
        self, current_point: momapy.geometry.Point
    ) -> shapely.GeometryCollection:
        """Convert to shapely geometry.

        Args:
            current_point: Start point.

        Returns:
            A LineString approximating the arc.
        """
        elliptical_arc = self.to_geometry(current_point)
        return elliptical_arc.to_shapely()


@dataclasses.dataclass(frozen=True)
class CurveTo(PathAction):
    """Draw a cubic Bezier curve.

    Attributes:
        point: End point.
        control_point1: First control point.
        control_point2: Second control point.
    """

    point: momapy.geometry.Point = dataclasses.field(
        metadata={"description": "The point of the curve to action"}
    )
    control_point1: momapy.geometry.Point = dataclasses.field(
        metadata={"description": "The first control point of the curve to action"}
    )
    control_point2: momapy.geometry.Point = dataclasses.field(
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
        transformation: momapy.geometry.Transformation,
        current_point: momapy.geometry.Point,
    ) -> "CurveTo":
        """Apply a transformation.

        Args:
            transformation: The transformation.
            current_point: Start point (unused).

        Returns:
            A new CurveTo with transformed points.
        """
        return CurveTo(
            momapy.geometry.transform_point(self.point, transformation),
            momapy.geometry.transform_point(self.control_point1, transformation),
            momapy.geometry.transform_point(self.control_point2, transformation),
        )

    def to_geometry(
        self, current_point: momapy.geometry.Point
    ) -> momapy.geometry.BezierCurve:
        """Convert to BezierCurve geometry.

        Args:
            current_point: Start point.

        Returns:
            A BezierCurve.
        """
        return momapy.geometry.BezierCurve(
            current_point,
            self.point,
            tuple([self.control_point1, self.control_point2]),
        )

    def to_shapely(
        self, current_point: momapy.geometry.Point, n_segs: int = 50
    ) -> shapely.GeometryCollection:
        """Convert to shapely geometry.

        Args:
            current_point: Start point.
            n_segs: Number of segments.

        Returns:
            A LineString approximating the curve.
        """
        bezier_curve = self.to_geometry(current_point)
        return bezier_curve.to_shapely(n_segs)


@dataclasses.dataclass(frozen=True)
class QuadraticCurveTo(PathAction):
    """Draw a quadratic Bezier curve.

    Attributes:
        point: End point.
        control_point: Control point.
    """

    point: momapy.geometry.Point = dataclasses.field(
        metadata={"description": "The point of the quadratic curve to action"}
    )
    control_point: momapy.geometry.Point = dataclasses.field(
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
        transformation: momapy.geometry.Transformation,
        current_point: momapy.geometry.Point,
    ) -> "QuadraticCurveTo":
        """Apply a transformation.

        Args:
            transformation: The transformation.
            current_point: Start point (unused).

        Returns:
            A new QuadraticCurveTo with transformed points.
        """
        return QuadraticCurveTo(
            momapy.geometry.transform_point(self.point, transformation),
            momapy.geometry.transform_point(self.control_point, transformation),
        )

    def to_curve_to(self, current_point: momapy.geometry.Point) -> CurveTo:
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

    def to_geometry(
        self, current_point: momapy.geometry.Point
    ) -> momapy.geometry.BezierCurve:
        """Convert to BezierCurve geometry.

        Args:
            current_point: Start point.

        Returns:
            A BezierCurve.
        """
        return momapy.geometry.BezierCurve(
            current_point,
            self.point,
            tuple([self.control_point]),
        )

    def to_shapely(self, current_point, n_segs=50):
        """Convert to shapely geometry.

        Args:
            current_point: Start point.
            n_segs: Number of segments.

        Returns:
            A LineString approximating the curve.
        """
        bezier_curve = self.to_geometry(current_point)
        return bezier_curve.to_shapely()


@dataclasses.dataclass(frozen=True)
class ClosePath(PathAction):
    """Close the current path."""

    def transformed(
        self,
        transformation: momapy.geometry.Transformation,
        current_point: momapy.geometry.Point,
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

    Attributes:
        actions: Tuple of path actions.
    """

    actions: tuple[PathAction] = dataclasses.field(
        default_factory=tuple,
        metadata={"description": "The actions of the path"},
    )

    def transformed(
        self, transformation: momapy.geometry.Transformation
    ) -> typing_extensions.Self:
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

    def to_shapely(self, to_polygons=False) -> shapely.GeometryCollection:
        """Convert to shapely geometry.

        Args:
            to_polygons: Whether to convert closed paths to polygons.

        Returns:
            A GeometryCollection.
        """
        current_point = momapy.geometry.Point(0, 0)
        initial_point = current_point
        geom_collection = []
        line_strings = []
        previous_action = None
        for current_action in self.actions:
            if isinstance(current_action, MoveTo):
                current_point = current_action.point
                initial_point = current_point
                if (
                    not isinstance(previous_action, ClosePath)
                    and previous_action is not None
                ):
                    multi_linestring = shapely.geometry.MultiLineString(line_strings)
                    line_string = shapely.ops.linemerge(multi_linestring)
                    geom_collection.append(line_string)
                line_strings = []
            elif isinstance(current_action, ClosePath):
                if (
                    current_point.x != initial_point.x
                    or current_point.y != initial_point.y
                ):
                    line_string = shapely.geometry.LineString(
                        [current_point.to_tuple(), initial_point.to_tuple()]
                    )
                    line_strings.append(line_string)
                if not to_polygons:
                    multi_line = shapely.MultiLineString(line_strings)
                    line_string = shapely.ops.linemerge(multi_line)
                    geom_collection.append(line_string)
                else:
                    polygons = shapely.ops.polygonize(line_strings)
                    for polygon in polygons:
                        geom_collection.append(polygon)
                current_point = initial_point
            else:
                line_string = current_action.to_shapely(current_point)
                line_strings.append(line_string)
                current_point = current_action.point
            previous_action = current_action
        if not isinstance(current_action, (MoveTo, ClosePath)):
            multi_linestring = shapely.geometry.MultiLineString(line_strings)
            line_string = shapely.ops.linemerge(multi_linestring)
            geom_collection.append(line_string)
        return shapely.geometry.GeometryCollection(geom_collection)

    def to_path_with_bezier_curves(self) -> typing_extensions.Self:
        """Convert to path with only Bezier curves.

        Converts elliptical arcs to Bezier curves.

        Returns:
            A new Path with Bezier curves only.
        """
        new_actions = []
        current_point = momapy.geometry.Point(0, 0)
        initial_point = current_point
        for action in self.actions:
            if isinstance(action, MoveTo):
                current_point = action.point
                initial_point = current_point
                new_actions.append(action)
            elif isinstance(action, ClosePath):
                current_point = initial_point
                new_actions.append(action)
            elif isinstance(
                action,
                (
                    LineTo,
                    CurveTo,
                    QuadraticCurveTo,
                ),
            ):
                current_point = action.point
                new_actions.append(action)
            elif isinstance(action, EllipticalArc):
                geom_object = action.to_geometry(current_point)
                bezier_curves = geom_object.to_bezier_curves()
                for bezier_curve in bezier_curves:
                    new_action = CurveTo(
                        point=bezier_curve.p2,
                        control_point1=bezier_curve.control_points[0],
                        control_point2=bezier_curve.control_points[1],
                    )
                    new_actions.append(new_action)
        new_path = dataclasses.replace(self, actions=new_actions)
        return new_path


@dataclasses.dataclass(frozen=True, kw_only=True)
class Ellipse(DrawingElement):
    """Ellipse drawing element.

    Attributes:
        point: Center point.
        rx: X-radius.
        ry: Y-radius.
    """

    point: momapy.geometry.Point = dataclasses.field(
        metadata={"description": "The point of the ellipse"}
    )
    rx: float = dataclasses.field(
        metadata={"description": "The x-radius of the ellipse"}
    )
    ry: float = dataclasses.field(
        metadata={"description": "The y-radius of the ellipse"}
    )

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

    def transformed(self, transformation) -> Path:
        """Apply a transformation.

        Args:
            transformation: The transformation.

        Returns:
            A transformed Path.
        """
        path = self.to_path()
        return path.transformed(transformation)

    def to_shapely(self, to_polygons=False):
        """Convert to shapely geometry.

        Args:
            to_polygons: Whether to return polygons.

        Returns:
            A GeometryCollection containing the ellipse.
        """
        point = self.point.to_shapely()
        circle = point.buffer(1)
        ellipse = shapely.affinity.scale(circle, self.rx, self.ry)
        if not to_polygons:
            ellipse = ellipse.boundary
        return shapely.geometry.GeometryCollection([ellipse])


@dataclasses.dataclass(frozen=True, kw_only=True)
class Rectangle(DrawingElement):
    """Rectangle drawing element with optional rounded corners.

    Attributes:
        point: Top-left corner.
        width: Width.
        height: Height.
        rx: X-radius for rounded corners.
        ry: Y-radius for rounded corners.
    """

    point: momapy.geometry.Point = dataclasses.field(
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
            MoveTo(momapy.geometry.Point(x + rx, y)),
            LineTo(momapy.geometry.Point(x + width - rx, y)),
        ]
        if rx > 0 and ry > 0:
            actions.append(
                EllipticalArc(momapy.geometry.Point(x + width, y + ry), rx, ry, 0, 0, 1)
            )
        actions.append(LineTo(momapy.geometry.Point(x + width, y + height - ry)))
        if rx > 0 and ry > 0:
            actions.append(
                EllipticalArc(
                    momapy.geometry.Point(x + width - rx, y + height),
                    rx,
                    ry,
                    0,
                    0,
                    1,
                )
            )
        actions.append(LineTo(momapy.geometry.Point(x + rx, y + height)))
        if rx > 0 and ry > 0:
            actions.append(
                EllipticalArc(
                    momapy.geometry.Point(x, y + height - ry), rx, ry, 0, 0, 1
                )
            )
        actions.append(LineTo(momapy.geometry.Point(x, y + ry)))
        if rx > 0 and ry > 0:
            actions.append(
                EllipticalArc(momapy.geometry.Point(x + rx, y), rx, ry, 0, 0, 1)
            )
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

    def transformed(self, transformation: momapy.geometry.Transformation) -> Path:
        """Apply a transformation.

        Args:
            transformation: The transformation.

        Returns:
            A transformed Path.
        """
        path = self.to_path()
        return path.transformed(transformation)

    def to_shapely(self, to_polygons=False) -> shapely.GeometryCollection:
        """Convert to shapely geometry.

        Args:
            to_polygons: Whether to return polygons.

        Returns:
            A GeometryCollection.
        """
        return self.to_path().to_shapely(to_polygons=to_polygons)


def drawing_elements_to_shapely(
    drawing_elements: collections.abc.Sequence[DrawingElement],
) -> shapely.GeometryCollection:
    """Convert drawing elements to shapely geometry.

    Args:
        drawing_elements: Sequence of drawing elements.

    Returns:
        A GeometryCollection.
    """
    geom_collection = []
    for drawing_element in drawing_elements:
        geom_collection += drawing_element.to_shapely(to_polygons=False).geoms
    return shapely.GeometryCollection(geom_collection)


def get_drawing_elements_border(
    drawing_elements: collections.abc.Sequence[DrawingElement],
    point: momapy.geometry.Point,
    center: momapy.geometry.Point | None = None,
) -> momapy.geometry.Point:
    """Get border point in a direction from center.

    Args:
        drawing_elements: Drawing elements.
        point: Direction point.
        center: Optional center point.

    Returns:
        The border point.
    """
    shapely_object = drawing_elements_to_shapely(drawing_elements)
    return momapy.geometry.get_shapely_object_border(
        shapely_object=shapely_object, point=point, center=center
    )


def get_drawing_elements_angle(
    drawing_elements: collections.abc.Sequence[DrawingElement],
    angle: float,
    unit="degrees",
    center: momapy.geometry.Point | None = None,
) -> momapy.geometry.Point:
    """Get border point at an angle from center.

    Args:
        drawing_elements: Drawing elements.
        angle: The angle.
        unit: Unit ('degrees' or 'radians').
        center: Optional center point.

    Returns:
        The border point.
    """
    shapely_object = drawing_elements_to_shapely(drawing_elements)
    return momapy.geometry.get_shapely_object_angle(
        shapely_object=shapely_object, angle=angle, unit=unit, center=center
    )


def get_drawing_elements_bbox(
    drawing_elements: collections.abc.Sequence[DrawingElement],
) -> momapy.geometry.Bbox:
    """Get bounding box of drawing elements.

    Args:
        drawing_elements: Drawing elements.

    Returns:
        The bounding box.
    """
    shapely_object = drawing_elements_to_shapely(drawing_elements)
    return momapy.geometry.Bbox.from_bounds(shapely_object.bounds)


def get_drawing_elements_anchor_point(
    drawing_elements,
    anchor_point: str,
    center: momapy.geometry.Point | None = None,
) -> momapy.geometry.Point:
    """Get anchor point of drawing elements.

    Args:
        drawing_elements: Drawing elements.
        anchor_point: Name of anchor point.
        center: Optional center point.

    Returns:
        The anchor point.
    """
    shapely_object = drawing_elements_to_shapely(drawing_elements)
    return momapy.geometry.get_shapely_object_anchor_point(
        shapely_object=shapely_object, anchor_point=anchor_point, center=center
    )
