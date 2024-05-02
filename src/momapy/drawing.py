import abc
import dataclasses
import uuid
import math
import copy
import enum

import shapely.geometry
import shapely.affinity
import shapely.ops

import momapy.geometry
import momapy.coloring
import momapy.utils


class NoneValueType(object):
    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self


NoneValue = NoneValueType()


@dataclasses.dataclass(frozen=True)
class FilterEffect(abc.ABC):
    result: str | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class DropShadowEffect(FilterEffect):
    dx: float = 0.0
    dy: float = 0.0
    std_deviation: float = 0.0
    flood_opacity: float = 1.0
    flood_color: momapy.coloring.Color = momapy.coloring.black

    def to_compat(self):
        flood_effect = FloodEffect(
            result=momapy.utils.get_uuid4_as_str(),
            flood_opacity=self.flood_opacity,
            flood_color=self.flood_color,
        )
        composite_effect1 = CompositeEffect(
            in_=flood_effect.result,
            in2=FilterEffectInput.SOURCE_GRAPHIC,
            operator=CompositionOperator.IN,
            result=momapy.utils.get_uuid4_as_str(),
        )
        gaussian_blur_effect = GaussianBlurEffect(
            in_=composite_effect1.result,
            std_deviation=self.std_deviation,
            result=momapy.utils.get_uuid4_as_str(),
        )
        offset_effect = OffsetEffect(
            in_=gaussian_blur_effect.result,
            dx=self.dx,
            dy=self.dy,
            result=momapy.utils.get_uuid4_as_str(),
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
    SOURCE_GRAPHIC = 0
    SOURCE_ALPHA = 1
    BACKGROUND_IMAGE = 2
    BACKGROUND_ALPHA = 3
    FILL_PAINT = 4
    STROKE_PAINT = 5


class CompositionOperator(enum.Enum):
    OVER = 0
    IN = 1
    OUT = 2
    ATOP = 3
    XOR = 4
    LIGHTER = 5
    ARTIHMETIC = 6


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompositeEffect(FilterEffect):
    in_: FilterEffectInput | str | None = None
    in2: FilterEffectInput | str | None = None
    operator: CompositionOperator | None = CompositionOperator.OVER


@dataclasses.dataclass(frozen=True, kw_only=True)
class FloodEffect(FilterEffect):
    flood_color: momapy.coloring.Color = momapy.coloring.black
    flood_opacity: float = 1.0


class EdgeMode(enum.Enum):
    DUPLICATE = 0
    WRAP = 1


@dataclasses.dataclass(frozen=True, kw_only=True)
class GaussianBlurEffect(FilterEffect):
    in_: FilterEffectInput | str | None = None
    std_deviation: float = 0.0
    edge_mode: NoneValueType | EdgeMode = NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class OffsetEffect(FilterEffect):
    in_: FilterEffectInput | str | None = None
    dx: float = 0.0
    dy: float = 0.0


class FilterUnits(enum.Enum):
    USER_SPACE_ON_USE = 0
    OBJECT_BOUNDING_BOX = 1


@dataclasses.dataclass(frozen=True, kw_only=True)
class Filter(object):
    id: str = dataclasses.field(
        hash=False, compare=False, default_factory=momapy.utils.get_uuid4_as_str
    )
    filter_units: FilterUnits = FilterUnits.OBJECT_BOUNDING_BOX
    effects: tuple[FilterEffect] = dataclasses.field(default_factory=tuple)
    width: float | str = "120%"
    height: float | str = "120%"
    x: float | str = "-10%"
    y: float | str = "-10%"

    def to_compat(self):
        effects = []
        for effect in self.effects:
            if hasattr(effect, "to_compat"):
                effects += effect.to_compat()
            else:
                effects.append(effect)
        return dataclasses.replace(self, effects=tuple(effects))


class FontStyle(enum.Enum):
    NORMAL = 0
    ITALIC = 1
    OBLIQUE = 2


class FontWeight(enum.Enum):
    NORMAL = 0
    BOLD = 1
    BOLDER = 2
    LIGHTER = 3


class TextAnchor(enum.Enum):
    START = 0
    MIDDLE = 1
    END = 2


# not implemented yet, just present in sbml render; to be implemented later
class FillRule(enum.Enum):
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
        "initial": None,  # depends on the user agent
        "inherited": True,
    },
    "font_size": {
        "initial": None,  # medium, which depends on the user agent; usually 16px
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

FONT_WEIGHT_VALUE_MAPPING = {
    FontWeight.NORMAL: 400,
    FontWeight.BOLD: 700,
}


def get_initial_value(attr_name):
    attr_value = PRESENTATION_ATTRIBUTES[attr_name]["initial"]
    if attr_value is None:
        attr_value = INITIAL_VALUES[attr_name]
    return attr_value


@dataclasses.dataclass(frozen=True, kw_only=True)
class DrawingElement(abc.ABC):
    fill: NoneValueType | momapy.coloring.Color | None = None
    fill_rule: FillRule | None = None
    filter: NoneValueType | Filter | None = (
        None  # should be a tuple of filters to follow SVG (to be implemented)
    )
    font_family: str | None = None
    font_size: float | None = None
    font_style: FontStyle | None = None
    font_weight: FontWeight | float | None = None
    stroke: NoneValueType | momapy.coloring.Color | None = None
    stroke_dasharray: tuple[float] | None = None
    stroke_dashoffset: float | None = None
    stroke_width: float | None = None
    text_anchor: TextAnchor | None = None
    transform: NoneValueType | momapy.geometry.Transformation | None = None

    @abc.abstractmethod
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

    def get_filter_region(self):
        if self.filter is None or self.filter is NoneValue:
            return None
        if (
            self.filter.filter_units == FilterUnits.OBJECT_BOUNDING_BOX
        ):  # only percentages or fraction values
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
        else:  # only absolute values
            filter_regions = momapy.geometry.Bbox(
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
    text: str
    point: momapy.geometry.Point

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    def transformed(self, transformation):
        return copy.deepcopy(self)

    def to_shapely(self, to_polygons=False):
        return shapely.geometry.GeometryCollection([self.point.to_shapely()])


@dataclasses.dataclass(frozen=True, kw_only=True)
class Group(DrawingElement):
    elements: tuple[DrawingElement] = dataclasses.field(default_factory=tuple)

    def transformed(self, transformation):
        elements = []
        for element in self.elements:
            elements.append(element.transformed(transformation))
        return dataclasses.replace(self, elements=tuple(elements))

    def to_shapely(self, to_polygons=False):
        geom_collection = []
        for element in self.elements:
            geom_collection += element.to_shapely(to_polygons=to_polygons).geoms
        return shapely.geometry.GeometryCollection(geom_collection)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Ellipse(DrawingElement):
    point: momapy.geometry.Point
    rx: float
    ry: float

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    def to_path(self):
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


@dataclasses.dataclass(frozen=True, kw_only=True)
class Rectangle(DrawingElement):
    point: momapy.geometry.Point
    width: float
    height: float
    rx: float
    ry: float

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    def to_path(self):
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
                EllipticalArc(
                    momapy.geometry.Point(x + width, y + ry), rx, ry, 0, 0, 1
                )
            )
        actions.append(
            LineTo(momapy.geometry.Point(x + width, y + height - ry))
        )
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

    def transformed(self, transformation):
        path = self.to_path()
        return path.transformed(transformation)

    def to_shapely(self, to_polygons=False):
        return self.to_path().to_shapely(to_polygons=to_polygons)


@dataclasses.dataclass(frozen=True)
class PathAction(abc.ABC):
    pass


@dataclasses.dataclass(frozen=True)
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


@dataclasses.dataclass(frozen=True)
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


@dataclasses.dataclass(frozen=True)
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
        elliptical_arc = self.to_geometry(current_point)
        return elliptical_arc.to_shapely()


@dataclasses.dataclass(frozen=True)
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
            momapy.geometry.transform_point(self.point, transformation),
            momapy.geometry.transform_point(
                self.control_point1, transformation
            ),
            momapy.geometry.transform_point(
                self.control_point2, transformation
            ),
        )

    def to_geometry(self, current_point):
        return momapy.geometry.BezierCurve(
            current_point,
            self.point,
            tuple([self.control_point1, self.control_point2]),
        )

    def to_shapely(self, current_point, n_segs=50):
        bezier_curve = self.to_geometry(current_point)
        return bezier_curve.to_shapely(n_segs)


@dataclasses.dataclass(frozen=True)
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
        return QuadraticCurveTo(
            momapy.geometry.transform_point(self.point, transformation),
            momapy.geometry.transform_point(self.control_point, transformation),
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


@dataclasses.dataclass(frozen=True)
class ClosePath(PathAction):
    def transformed(self, transformation, current_point):
        return ClosePath()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Path(DrawingElement):
    actions: tuple[PathAction] = dataclasses.field(default_factory=tuple)

    def transformed(self, transformation):
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

    def to_shapely(self, to_polygons=False):
        current_point = momapy.geometry.Point(
            0, 0
        )  # in case the path does not start with a move_to command;
        # this is not possible in svg but not enforced here
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
                    multi_linestring = shapely.geometry.MultiLineString(
                        line_strings
                    )
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

    def to_path_with_bezier_curves(self):
        new_actions = []
        current_point = momapy.geometry.Point(
            0, 0
        )  # in case the path does not start with a move_to command;
        # this is not possible in svg but not enforced here
        intial_point = current_point
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
