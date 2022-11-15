from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar, Union, Optional, ClassVar, Callable, Any

import momapy.core
import momapy.geometry


@dataclass(frozen=True)
class Annotation(momapy.core.ModelElement):
    pass


@dataclass(frozen=True)
class SBGNModelElement(momapy.core.ModelElement):
    annotations: frozenset[Annotation] = field(default_factory=frozenset)


@dataclass(frozen=True)
class SBGNRole(SBGNModelElement):
    element: Optional[SBGNModelElement] = None


@dataclass(frozen=True)
class SBGNModel(momapy.core.Model):
    pass


@dataclass(frozen=True)
class SBGNMap(momapy.core.Map):
    model: Optional[SBGNModel] = None
    layout: Optional[momapy.core.MapLayout] = None
    model_layout_mapping: Optional[momapy.core.ModelLayoutMapping] = None


@dataclass(frozen=True)
class _SBGNShapeBase(momapy.core.NodeLayout):
    def border_drawing_element(self):
        drawing_elements = []
        for base in type(self).__mro__:
            if (
                momapy.builder.issubclass_or_builder(base, _SBGNMixinBase)
                and base is not _SBGNMixinBase
                and base
                is not momapy.builder.get_or_make_builder_cls(_SBGNMixinBase)
                and base is not type(self)
            ):
                drawing_elements += getattr(base, "_mixin_drawing_elements")(
                    self
                )
        group = momapy.drawing.Group(elements=drawing_elements)
        return group

    def self_bbox(self):
        bboxes = []
        for base in type(self).__bases__:
            if (
                momapy.builder.issubclass_or_builder(base, _SBGNMixinBase)
                and base is not _SBGNMixinBase
                and base
                is not momapy.builder.get_or_make_builder_cls(_SBGNMixinBase)
            ):
                bboxes.append(getattr(base, "_mixin_bbox")(self))
        position, width, height = momapy.positioning.fit(bboxes)
        return momapy.geometry.Bbox(position, width, height)

    def north_west(self):
        return momapy.core.NodeLayout.north_west(self)

    def north(self):
        return momapy.core.NodeLayout.north(self)

    def north_east(self):
        return momapy.core.NodeLayout.north_east(self)

    def east(self):
        return momapy.core.NodeLayout.east(self)

    def south_east(self):
        return momapy.core.NodeLayout.south_east(self)

    def south(self):
        return momapy.core.NodeLayout.south(self)

    def south_west(self):
        return momapy.core.NodeLayout.south_west(self)

    def west(self):
        return momapy.core.NodeLayout.west(self)

    def center(self):
        return momapy.core.NodeLayout.center(self)

    def label_center(self):
        return momapy.core.NodeLayout.label_center(self)


@dataclass(frozen=True)
class _SBGNMixinBase(object):
    @classmethod
    @abstractmethod
    def _mixin_drawing_elements(cls, obj):
        pass

    @classmethod
    @abstractmethod
    def _mixin_bbox(cls, obj):
        pass


@dataclass(frozen=True)
class _ConnectorsMixin(_SBGNMixinBase):
    left_connector_length: Optional[float] = None
    right_connector_length: Optional[float] = None
    left_connector_stroke_width: Optional[float] = None
    right_connector_stroke_width: Optional[float] = None
    direction: Optional[
        momapy.core.Direction
    ] = momapy.core.Direction.HORIZONTAL

    def base_left_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y - self.height / 2)
        else:
            return momapy.geometry.Point(self.x - self.width / 2, self.y)

    def base_right_connector(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y + self.height / 2)
        else:
            return momapy.geometry.Point(self.x + self.width / 2, self.y)

    def west(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x - self.width / 2, self.y)
        else:
            return momapy.geometry.Point(
                self.x - self.width / 2 - self.left_connector_length, self.y
            )

    def south(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y + self.height / 2 + self.right_connector_length
            )
        else:
            return momapy.geometry.Point(self.x, self.y + self.height / 2)

    def east(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x + self.width / 2, self.y)
        else:
            return momapy.geometry.Point(
                self.x + self.width / 2 + self.right_connector_length, self.y
            )

    def north(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y - self.height / 2 - self.left_connector_length
            )
        else:
            return momapy.geometry.Point(self.x, self.y - self.height / 2)

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        path_left = momapy.drawing.Path(
            stroke_width=obj.left_connector_stroke_width
        )
        path_right = momapy.drawing.Path(
            stroke_width=obj.right_connector_stroke_width
        )
        if obj.direction == momapy.core.Direction.VERTICAL:
            path_left += momapy.drawing.move_to(
                obj.base_left_connector()
            ) + momapy.drawing.line_to(
                obj.base_left_connector() - (0, obj.left_connector_length)
            )
            path_right += momapy.drawing.move_to(
                obj.base_right_connector()
            ) + momapy.drawing.line_to(
                obj.base_right_connector() + (0, obj.right_connector_length)
            )
        else:
            path_left += momapy.drawing.move_to(
                obj.base_left_connector()
            ) + momapy.drawing.line_to(
                obj.base_left_connector() - (obj.left_connector_length, 0)
            )
            path_right += momapy.drawing.move_to(
                obj.base_right_connector()
            ) + momapy.drawing.line_to(
                obj.base_right_connector() + (obj.right_connector_length, 0)
            )
        return [path_left, path_right]

    @classmethod
    def _mixin_bbox(cls, obj):
        position = obj.position
        if obj.direction == momapy.core.Direction.VERTICAL:
            width = obj.width
            height = obj.east().y - obj.west().y
        else:
            width = obj.east().x - obj.west().x
            height = obj.height
        return momapy.geometry.Bbox(position, width, height)


@dataclass(frozen=True)
class _SimpleMixin(_SBGNMixinBase):
    _shape_cls: ClassVar[type]
    _arg_names_mapping: ClassVar[dict[str, str]]

    def _get_shape_initialization_arguments(self) -> dict[str, Any]:
        kwargs = {}
        for arg_name in self._arg_names_mapping:
            kwargs[arg_name] = getattr(self, self._arg_names_mapping[arg_name])
        kwargs["position"] = self.position
        kwargs["width"] = self.width
        kwargs["height"] = self.height
        return kwargs

    def _make_shape(self):
        kwargs = self._get_shape_initialization_arguments()
        return self._shape_cls(**kwargs)

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        return obj._make_shape().drawing_elements()

    @classmethod
    def _mixin_bbox(cls, obj):
        return momapy.geometry.Bbox(obj.position, obj.width, obj.height)


@dataclass(frozen=True)
class _MultiMixin(_SBGNMixinBase):
    _n: ClassVar[int]
    _shape_cls: ClassVar[momapy.core.NodeLayout]
    _arg_names_mapping: ClassVar[dict[str, str]]
    offset: int = 10
    subunits_stroke: tuple[momapy.coloring.Color] = field(default_factory=tuple)
    subunits_stroke_width: tuple[float] = field(default_factory=tuple)
    subunits_fill: tuple[momapy.coloring.Color] = field(default_factory=tuple)
    subunits_filter: tuple[momapy.drawing.Filter] = field(default_factory=tuple)

    def _get_subunit_width(self):
        width = self.width - self.offset * (self._n - 1)
        return width

    def _get_subunit_height(self):
        height = self.height - self.offset * (self._n - 1)
        return height

    def _get_subunit_position(self, order=0):
        position = self.position + (
            +self.width / 2
            - self._get_subunit_width() / 2
            - order * self.offset,
            +self.height / 2
            - self._get_subunit_height() / 2
            - order * self.offset,
        )
        return position

    def _get_subunit_initialization_arguments(self, order=0) -> dict[str, Any]:
        kwargs = {}
        for arg_name in self._arg_names_mapping:
            kwargs[arg_name] = getattr(self, self._arg_names_mapping[arg_name])
        if self._n > 1:
            for arg_name in ["stroke", "stroke_width", "fill", "filter"]:
                if arg_name not in self._arg_names_mapping:
                    if len(getattr(self, f"subunits_{arg_name}")) > order:
                        kwargs[arg_name] = getattr(
                            self, f"subunits_{arg_name}"
                        )[order]
        kwargs["position"] = self._get_subunit_position(order)
        kwargs["width"] = self._get_subunit_width()
        kwargs["height"] = self._get_subunit_height()
        return kwargs

    def _make_subunit(self, order=0):
        kwargs = self._get_subunit_initialization_arguments(order)
        return self._shape_cls(**kwargs)

    def _make_subunits(self):
        subunits = []
        for i in range(self._n):
            subunit = self._make_subunit(i)
            subunits.append(subunit)
        return subunits

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        drawing_elements = []
        for subunit in obj._make_subunits():
            drawing_elements += subunit.drawing_elements()
        return drawing_elements

    @classmethod
    def _mixin_bbox(cls, obj):
        return momapy.geometry.Bbox(obj.position, obj.width, obj.height)

    def label_center(self):
        return self._make_subunit(self._n - 1).label_center()


@dataclass(frozen=True)
class _TextMixin(_SBGNMixinBase):
    _text: ClassVar[str]
    _font_color: ClassVar[momapy.coloring.Color]
    _font_family: ClassVar[str]
    _font_size_func: ClassVar[Callable]

    def _make_text_layout(self):
        text_layout = momapy.core.TextLayout(
            position=self.position,
            text=self._text,
            font_family=self._font_family,
            font_size=self._font_size_func(),
            font_color=self._font_color,
        )
        return text_layout

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        return obj._make_text_layout().drawing_elements()

    @classmethod
    def _mixin_bbox(cls, obj):
        return obj._make_text_layout().bbox()
