from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar, Union, Optional, ClassVar, Callable

from momapy.core import (
    Map,
    ModelElement,
    Model,
    MapLayout,
    ModelLayoutMapping,
    NodeLayout,
    Direction,
    TextLayout,
)


############Annotation###################
@dataclass(frozen=True)
class Annotation(ModelElement):
    pass


############SBGN MODEL ELEMENT###################
@dataclass(frozen=True)
class SBGNModelElement(ModelElement):
    annotations: frozenset[Annotation] = field(default_factory=frozenset)


############SBGN ROLES###################
@dataclass(frozen=True)
class SBGNRole(SBGNModelElement):
    element: Optional[SBGNModelElement] = None


############MODEL###################
@dataclass(frozen=True)
class SBGNModel(Model):
    pass


############MAP###################
@dataclass(frozen=True)
class SBGNMap(Map):
    model: Optional[SBGNModel] = None
    layout: Optional[MapLayout] = None
    model_layout_mapping: Optional[ModelLayoutMapping] = None


class _MetaSBGNShape(type):
    def _get_subunit_anchor_point(obj, i, anchor):
        return getattr(obj._make_subunit(i), anchor)()

    def __new__(cls, bases, namespace, **kwds):
        if namespace.get("_with_connectors") is True:
            namespace["base_left_connector"] = self._base_left_connector
            namespace["base_right_connector"] = self._base_right_connector
        if namespace.get("_with_multi") is True:
            namespace["subunits_stroke"] = field(default_factory=tuple)
            namespace["subunits_stroke_width"] = field(default_factory=tuple)
            namespace["subunits_fill"] = field(default_factory=tuple)
            for i in range(self._n):
                for anchor in namespace["_shape"].anchors:
                    namespace[
                        f"subunit{i}_{anchor}"
                    ] = lambda i, anchor: _get_subunit_anchor_point(
                        obj, i, anchor
                    )
        return super().__new__(cls, bases, namespace, **kwds)


@dataclass(frozen=True)
class _SBGNShape(NodeLayout, metaclass=_MetaSBGNShape):
    _shape: Optional[NodeLayout] = None
    _arg_names_mapping: Optional[dict[str, str]] = None
    _with_connectors: bool = False
    _default_left_connector_length: Optional[float] = None
    _default_right_connector_length: Optional[float] = None
    _default_direction: Optional[Direction] = Direction.HORIZONTAL
    _with_multi: bool = False
    _n: Optional[int] = None
    _with_text: bool = False
    _text: Optional[str] = None
    _font_size_func: Optional[Callable] = None
    _font_family: Optional[str] = None

    def _get_subunit_initialization_arguments(self, order=0) -> dict[str, Any]:
        args = {}
        for arg_name in self.arg_names_mapping:
            args[arg_name] = getattr(self, self.arg_names_mapping[arg_name])
        if self.n > 1:
            for arg_name in ["stroke", "stroke_width", "fill"]:
                if arg_name not in self.arg_names_mapping:
                    if len(getattr(self, f"subunits_{arg_name}s")) > order:
                        args[arg_name] = getattr(self, f"subunits_{arg_name}s")[
                            order
                        ]
        args["position"] = self._get_subunit_position(order=0)
        args["width"] = self._get_subunit_width()
        args["height"] = self._get_subunit_height()
        return args

    def _get_subunit_width(self):
        width = self.width - self.offset * self.n
        return width

    def _get_subunit_height(self):
        height = self.height - self.offset * self.n
        return height

    def _get_subunit_position(self, order=0):
        position = self.position + (
            -self.width / 2
            + self._get_subunit_width() / 2
            + order * self.offset,
            -self.height / 2
            + self._get_subunit_height() / 2
            + order * self.offset,
        )
        return position

    def _make_subunit(self, order=0):
        args = self._get_subunit_initialization_arguments(order)
        return self.shape(**args)

    def _make_subunits_drawing_elements(self):
        subunits_drawing_elements = []
        for i in range(self._n):
            subunits_drawing_elements.append(
                self._make_subunit(i).drawing_elements()
            )
        return subunits_drawing_elements

    def _make_connectors_drawing_elements(self):
        path_left = Path()
        path_right = Path()
        if self.direction == momapy.core.Direction.VERTICAL:
            path_left += momapy.drawing.move_to(
                self.base_left_connector()
            ) + momapy.drawing.line_to(self.north())
            path_right += +momapy.drawing.move_to(
                self.base_right_connector()
            ) + momapy.drawing.line_to(self.south())
        else:
            path_left += momapy.drawing.move_to(
                self.base_left_connector()
            ) + momapy.drawing.line_to(self.west())
            path_right += +momapy.drawing.move_to(
                self.base_right_connector()
            ) + momapy.drawing.line_to(self.east())
        return [path_left, path_right]

    def _make_text_drawing_elements(self):
        text_layout = TextLayout(
            text=self._text,
            font_family=self._font_family,
            font_size=self._font_size_func(),
        )
        return text_layout.drawing_elements()

    def self_drawing_elements(self):
        drawing_elements = self._make_subunits_drawing_elements()
        if self._with_connectors:
            drawing_elements += self._make_connectors_drawing_elements()
        if self._with_text:
            drawing_elements += self._make_text_drawing_elements()
        return drawing_elements
