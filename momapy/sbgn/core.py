from enum import Enum
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar, Union, Optional, ClassVar, Callable, Any

import momapy.core
import momapy.geometry


class BQModel(Enum):
    HAS_INSTANCE = 0
    IS = 1
    IS_DERIVED_FROM = 2
    IS_DESCRIBED_BY = 3
    IS_INSTANCE_OF = 4


class BQBiol(Enum):
    ENCODES = 0
    HAS_PART = 1
    HAS_PROPERTY = 2
    HAS_VERSION = 3
    IS = 4
    IS_DESCRIBED_BY = 5
    IS_ENCODED_BY = 6
    IS_HOMOLOG_TO = 7
    IS_PART_OF = 8
    IS_PROPERTY_OF = 9
    IS_VERSION_OF = 10
    OCCURS_IN = 11
    HAS_TAXON = 12


@dataclass(frozen=True, kw_only=True)
class Annotation(momapy.core.ModelElement):
    qualifier: Union[BQModel, BQBiol]
    resource: str


@dataclass(frozen=True, kw_only=True)
class SBGNModelElement(momapy.core.ModelElement):
    notes: str | None = None
    annotations: frozenset[Annotation] = field(
        default_factory=frozenset, compare=False
    )


@dataclass(frozen=True, kw_only=True)
class SBGNRole(SBGNModelElement):
    element: SBGNModelElement


@dataclass(frozen=True, kw_only=True)
class SBGNModel(momapy.core.Model):
    notes: str | None = None
    annotations: frozenset[Annotation] = field(
        default_factory=frozenset, compare=False
    )


@dataclass(frozen=True, kw_only=True)
class SBGNLayout(momapy.core.Layout):
    pass


@dataclass(frozen=True, kw_only=True)
class SBGNMap(momapy.core.Map):
    model: SBGNModel
    layout: SBGNLayout
    notes: str | None = None
    annotations: frozenset[Annotation] = field(
        default_factory=frozenset, compare=False
    )


@dataclass(frozen=True)
class _SBGNNodeBase(momapy.core.NodeLayout):
    def border_drawing_elements(self):
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
        return drawing_elements


@dataclass(frozen=True)
class _SBGNMixinBase(object):
    @classmethod
    @abstractmethod
    def _mixin_drawing_elements(cls, obj):
        pass


@dataclass(frozen=True)
class _ConnectorsMixin(_SBGNMixinBase):
    left_connector_length: float
    right_connector_length: float
    left_connector_stroke_width: float
    right_connector_stroke_width: float
    direction: Optional[
        momapy.core.Direction
    ] = momapy.core.Direction.HORIZONTAL
    left_to_right: bool = True

    def left_connector_base(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y - self.height / 2)
        else:
            return momapy.geometry.Point(self.x - self.width / 2, self.y)

    def right_connector_base(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(self.x, self.y + self.height / 2)
        else:
            return momapy.geometry.Point(self.x + self.width / 2, self.y)

    def left_connector_tip(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y - self.height / 2 - self.left_connector_length
            )
        else:
            return momapy.geometry.Point(
                self.x - self.width / 2 - self.left_connector_length, self.y
            )

    def right_connector_tip(self):
        if self.direction == momapy.core.Direction.VERTICAL:
            return momapy.geometry.Point(
                self.x, self.y + self.height / 2 + self.right_connector_length
            )
        else:
            return momapy.geometry.Point(
                self.x + self.width / 2 + self.right_connector_length, self.y
            )

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
        if obj.direction == momapy.core.Direction.VERTICAL:
            left_actions = [
                momapy.drawing.MoveTo(obj.left_connector_base()),
                momapy.drawing.LineTo(
                    obj.left_connector_base() - (0, obj.left_connector_length)
                ),
            ]
            right_actions = [
                momapy.drawing.MoveTo(obj.right_connector_base()),
                momapy.drawing.LineTo(
                    obj.right_connector_base() + (0, obj.right_connector_length)
                ),
            ]
        else:
            left_actions = [
                momapy.drawing.MoveTo(obj.left_connector_base()),
                momapy.drawing.LineTo(
                    obj.left_connector_base() - (obj.left_connector_length, 0)
                ),
            ]
            right_actions = [
                momapy.drawing.MoveTo(obj.right_connector_base()),
                momapy.drawing.LineTo(
                    obj.right_connector_base() + (obj.right_connector_length, 0)
                ),
            ]
        path_left = momapy.drawing.Path(
            stroke_width=obj.left_connector_stroke_width, actions=left_actions
        )
        path_right = momapy.drawing.Path(
            stroke_width=obj.right_connector_stroke_width, actions=right_actions
        )

        return [path_left, path_right]


@dataclass(frozen=True)
class _SimpleMixin(_SBGNMixinBase):
    @abstractmethod
    def _make_node(self, position, width, height):
        pass

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        node = obj._make_node(obj.position, obj.width, obj.height)
        drawing_elements = node.border_drawing_elements()
        return drawing_elements


@dataclass(frozen=True)
class _MultiMixin(_SBGNMixinBase):
    _n: ClassVar[int]
    offset: float = 10.0
    subunits_stroke: tuple[
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ] = field(default_factory=tuple)
    subunits_stroke_width: tuple[
        momapy.drawing.NoneValueType | float | None
    ] = field(default_factory=tuple)
    subunits_stroke_dasharray: tuple[
        momapy.drawing.NoneValueType | tuple[float] | None
    ] = field(default_factory=tuple)
    subunits_stroke_dashoffset: tuple[float | None] = field(
        default_factory=tuple
    )
    subunits_fill: tuple[
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ] = field(default_factory=tuple)
    subunits_transform: tuple[
        momapy.drawing.NoneValueType
        | tuple[momapy.geometry.Transformation]
        | None
    ] = field(default_factory=tuple)
    subunits_filter: tuple[
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ] = field(default_factory=tuple)

    def _make_subunit_node(
        self,
        position,
        width,
        height,
        border_stroke=None,
        border_stroke_width=None,
        border_stroke_dasharray=None,
        border_stroke_dashoffset=None,
        border_fill=None,
        border_transform=None,
        border_filter=None,
    ):
        pass

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        drawing_elements = []
        width = obj.width - obj.offset * (obj._n - 1)
        height = obj.height - obj.offset * (obj._n - 1)
        for i in range(obj._n):
            kwargs = {"width": width, "height": height}
            kwargs["position"] = obj.position + (
                obj.width / 2 - width / 2 - i * obj.offset,
                obj.height / 2 - height / 2 - i * obj.offset,
            )
            for attr_name in [
                "stroke",
                "stroke_width",
                "stroke_dasharray",
                "stroke_dashoffset",
                "fill",
                "transform",
                "filter",
            ]:
                attr_value = getattr(obj, f"subunits_{attr_name}")
                if len(attr_value) > i:
                    kwargs[f"border_{attr_name}"] = attr_value[i]
            subunit_node = obj._make_subunit_node(**kwargs)
            drawing_elements += subunit_node.self_drawing_elements()
        return drawing_elements

    def label_center(self):
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2 - (self._n - 1) * self.offset,
            self.height / 2 - height / 2 - (self._n - 1) * self.offset,
        )
        return self._make_subunit_node(
            position=position, width=width, height=height
        ).label_center()


@dataclass(frozen=True)
class _TextMixin(_SBGNMixinBase):
    _text: ClassVar[str]
    _font_color: ClassVar[momapy.coloring.Color]
    _font_family: ClassVar[str]
    _font_size_func: ClassVar[Callable]

    def _make_text_layout(self):
        text_layout = momapy.core.TextLayout(
            position=self.label_center(),
            text=self._text,
            font_family=self._font_family,
            font_size=self._font_size_func(),
            font_color=self._font_color,
        )
        return text_layout

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        return obj._make_text_layout().drawing_elements()
