from abc import ABC, abstractmethod
from dataclasses import dataclass, field, is_dataclass, fields, MISSING, make_dataclass
from frozendict import frozendict
from typing import Union, ClassVar, Callable, Collection, Sequence, get_origin, get_args, Optional, Any
from collections.abc import Mapping
from uuid import uuid4
from inspect import getmembers

import momapy.core
import momapy.geometry
import momapy.event

builders = {}


def _transform_type(type_):
    o_type = get_origin(type_)
    if o_type is not None:
        if isinstance(o_type, type):  # o_type is a class
            new_o_type = get_or_make_builder_cls(o_type)
            if new_o_type is None:
                new_o_type = type_
        else:
            new_o_type = o_type
        new_type = new_o_type[tuple(
            [_transform_type(a_type) for a_type in get_args(type_)])]
    else:
        if isinstance(type_, type):  # type_ is a class
            new_type = get_or_make_builder_cls(type_)
            if new_type is None:
                new_type = type_
        else:
            new_type = type_
    return new_type


def _build(self):
    args = {}
    for field_ in fields(self):
        attr_value = getattr(self, field_.name)
        args[field_.name] = build_object(attr_value)
    return self._cls_to_build(**args)


def _add_element(self, element, fields_for_add_element):
    added = False
    for field_ in fields_for_add_element:
        if isinstance(element, field_["a_types"]):
            attr = getattr(self, field_["field_name"])
            if hasattr(attr, "append"):
                attr.append(element)
                added = True
            elif hasattr(attr, "add"):
                attr.add(element)
                added = True
    if not added:
        raise TypeError(f"unsupported type {type(element)}")


def _post_init(self):
    self._callbacks = {}
    self._attribute_callbacks = {}


def _connect_attribute(self, attribute, event_type, callback):
    if attribute not in self._attribute_callbacks:
        self._attribute_callbacks[attribute] = {}
    if event_type not in self._attribute_callbacks[attribute]:
        self._attribute_callbacks[attribute][event_type] = set()
    self._attribute_callbacks[attribute][event_type].add(callback)


def _connect(self, event_type, callback):
    if event_type not in self._callbacks:
        self._callbacks[event_type] = set()
    self._callbacks[event_type].add(callback)


def make_builder_cls(cls, builder_fields=None, builder_bases=None, builder_namespace=None):
    cls_fields = fields(cls)
    if builder_fields is None:
        builder_fields = []
    if builder_bases is None:
        builder_bases = []
    if builder_namespace is None:
        builder_namespace = {}
    fields_for_add_element = []

    for field_ in cls_fields:
        field_name = field_.name
        if field_name not in [builder_field[0] for builder_field in builder_fields]:
            field_dict = {}
            field_type = _transform_type(field_.type)
            if field_.default_factory != MISSING:
                field_dict["default_factory"] = _transform_type(
                    field_.default_factory)
            if field_.default != MISSING:
                field_dict["default"] = field_.default
            builder_fields.append(
                (field_name, field_type, field(**field_dict)))
            field_o_type = get_origin(field_type)
            if issubclass(cls, momapy.core.MapElement) and field_o_type is not None and isinstance(field_o_type, type) and issubclass(field_o_type, Collection):
                fields_for_add_element.append(
                    {"field_name": field_name, "field_type": field_o_type, "a_types": get_args(field_type)})

    builder_namespace["build"] = _build
    builder_namespace["connect"] = _connect
    builder_namespace["connect_attribute"] = _connect_attribute
    builder_namespace["_cls_to_build"] = cls
    builder_namespace["__post_init__"] = _post_init

    for field_ in builder_fields:
        builder_namespace[field_[0]] = momapy.event.Connectable()

    if fields_for_add_element:
        builder_namespace["add_element"] = (lambda fields_for_add_element: lambda self, element: _add_element(
            self, element, fields_for_add_element))(fields_for_add_element)

    for member in getmembers(cls):
        func_name = member[0]
        func = member[1]
        if (isinstance(func, Callable) or isinstance(func, property)) and not func_name.startswith("__"):
            builder_namespace[func_name] = func

    builder_bases = tuple(
        builder_bases + [get_or_make_builder_cls(base_cls) for base_cls in cls.__bases__])

    builder = make_dataclass(
        cls_name=f"{cls.__name__}Builder",
        fields=builder_fields,
        bases=builder_bases,
        namespace=builder_namespace,
        eq=False)

    return builder


def build_object(obj):
    if hasattr(obj, "build") and isinstance(getattr(obj, "build"), Callable):
        return obj.build()
    else:
        return obj


def new_object(object_cls, *args, **kwargs):
    if not issubclass(object_cls, Builder):
        builder_cls = get_or_make_builder_cls(object_cls)
    return builder_cls(*args, **kwargs)


def get_or_make_builder_cls(cls, builder_fields=None, builder_bases=None, builder_namespace=None):
    if has_builder(cls):
        return get_builder(cls)
    elif is_dataclass(cls):
        builder_cls = make_builder_cls(
            cls, builder_fields, builder_bases, builder_namespace)
        register_builder(builder_cls)
        return builder_cls
    else:
        return cls


def has_builder(cls):
    return cls in builders


def get_builder(cls):
    return builders[cls]


def register_builder(builder_cls):
    builders[builder_cls._cls_to_build] = builder_cls


class Builder(ABC):

    @property
    @classmethod
    @abstractmethod
    def _cls_to_build() -> type:
        pass

    @abstractmethod
    def build(self):
        pass


class FrozensetBuilder(set, Builder):
    _cls_to_build = frozenset

    def build(self):
        return self._cls_to_build([build_object(obj) for obj in self])


class SetBuilder(set, Builder):
    _cls_to_build = set

    def build(self):
        return self._cls_to_build([build_object(obj) for obj in self])


class TupleBuilder(list, Builder):
    _cls_to_build = tuple

    def build(self):
        return self._cls_to_build([build_object(obj) for obj in self])


class DictBuilder(dict, Builder):
    _cls_to_build = dict

    def build(self):
        return self._cls_to_build([(build_object(key), build_object(val)) for key, val in self.items()])


class FrozendictBuilder(dict, Builder):
    _cls_to_build = frozendict

    def build(self):
        return self._cls_to_build([(build_object(key), build_object(val)) for key, val in self.items()])


class ListBuilder(list, Builder):
    _cls_to_build = list

    def build(self):
        return self._cls_to_build([build_object(obj) for obj in self])


@dataclass
class RelativePointBuilder(Builder):
    _cls_to_build: ClassVar[type] = momapy.geometry.Point
    evaluated: momapy.event.Connectable = momapy.event.Connectable()
    obj: Optional[Builder] = None
    func: Optional[Union[str, Callable]] = None
    args: Sequence[Any] = field(default_factory=list)
    kwargs: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self._x = None
        self._y = None
        self.evaluated = False
        if isinstance(
            self.obj,
            get_or_make_builder_cls(momapy.core.NodeLayoutElement)):
            for attribute in ["position", "width", "height"]:
                self.obj.connect_attribute(
                    attribute, "set", self._set_to_evaluate)
        elif isinstance(self.obj, (RelativePointBuilder)):
            self.obj.connect_attribute(
                "evaluated", "set", self._set_to_evaluate)

    def _set_to_evaluate(self, *args):
        self.evaluated = False

    def __add__(self, xy):
        return relative_point(self, momapy.geometry.Point.__add__, [xy])

    @ property
    def x(self):
        if not self.evaluated:
            self.evaluate()
        return self._x

    @ property
    def y(self):
        if not self.evaluated:
            self.evaluate()
        return self._y

    def evaluate(self):
        if self.obj is None:
            point = self.func(*self.args, **self.kwargs)
        else:
            if isinstance(self.func, str):
                func = getattr(self.obj.__class__, self.func)
            else:
                func = self.func
            if isinstance(func, property):
                point = getattr(self.obj, self.func)
            else:
                point = getattr(self.obj, self.func)(*args, **kwargs)
        self._x = point.x
        self._y = point.y
        self.evaluated = True

    def build(self):
        if not self.evaluated:
            self.evaluate()
        return self._cls_to_build(self.x, self.y)


class ModelLayoutMappingBuilder(FrozendictBuilder):
    _cls_to_build = momapy.core.ModelLayoutMapping


register_builder(FrozensetBuilder)
register_builder(SetBuilder)
register_builder(TupleBuilder)
register_builder(DictBuilder)
register_builder(FrozendictBuilder)
register_builder(ListBuilder)
register_builder(ModelLayoutMappingBuilder)


def map_element_builder__hash__(self):
    return hash(self.id)


def map_element_builder__eq__(self, other):
    return self.__class__ == other.__class__ and self.id == other.id


MapElementBuilder = get_or_make_builder_cls(
    momapy.core.MapElement,
    builder_namespace={
        "__hash__": map_element_builder__hash__,
        "__eq__": map_element_builder__eq__
    }
)

ModelElementBuilder = get_or_make_builder_cls(momapy.core.ModelElement)
LayoutElementBuilder = get_or_make_builder_cls(momapy.core.LayoutElement)
NodeLayoutElementBuilder = get_or_make_builder_cls(
    momapy.core.NodeLayoutElement)
ArcLayoutElementBuilder = get_or_make_builder_cls(momapy.core.ArcLayoutElement)
NodeLayoutElementLabelBuilder = get_or_make_builder_cls(
    momapy.core.NodeLayoutElementLabel)


def model_builder_new_element(self, element_cls, *args, **kwargs):
    if not issubclass(element_cls, (
        momapy.core.ModelElementBuilder,
        momapy.core.ModelElement)):
        raise TypeError(
            "element class must be a subclass of ModelElementBuilder or ModelElement")
    return new_object(element_cls, *args, **kwargs)


ModelBuilder = get_or_make_builder_cls(
    momapy.core.Model,
    builder_namespace={"new_element": model_builder_new_element}
)


def layout_builder_new_element(self, element_cls, *args, **kwargs):
    if not issubclass(
        element_cls,
        (momapy.core.LayoutElementBuilder, momapy.core.LayoutElement)):
        raise TypeError(
            "element class must be a subclass of LayoutElementBuilder or LayoutElement")
    return new_object(element_cls, *args, **kwargs)


LayoutBuilder = get_or_make_builder_cls(
    momapy.core.Layout,
    builder_namespace={"new_element": layout_builder_new_element}
)


@ abstractmethod
def map_builder_new_model(self, *args, **kwargs) -> ModelBuilder:
    pass


@ abstractmethod
def map_builder_new_layout(self, *args, **kwargs) -> LayoutBuilder:
    pass


@ abstractmethod
def map_builder_new_model_layout_mapping(self, *args, **kwargs) -> ModelLayoutMappingBuilder:
    pass


def map_builder_new_model_element(self, element_cls, *args, **kwargs) -> ModelElementBuilder:
    model_element = self.model.new_element(element_cls, *args, **kwargs)
    return model_element


def map_builder_new_layout_element(self, element_cls, *args, **kwargs) -> LayoutElementBuilder:
    layout_element = self.layout.new_element(element_cls, *args, **kwargs)
    return layout_element


def map_builder_add_model_element(self, model_element):
    self.model.add_element(model_element)


def map_builder_add_layout_element(self, layout_element):
    self.layout.add_element(layout_element)


def map_builder_add_layout_element_to_model_element(self, layout_element, model_element):
    if model_element not in self.model_layout_mapping:
        self.model_layout_mapping[model_element] = FrozensetBuilder()
    self.model_layout_mapping[model_element].add(layout_element)


def map_builder_get_layout_elements(self, model_element):
    return self.model_layout_mapping[model_element]


MapBuilder = get_or_make_builder_cls(
    momapy.core.Map,
    builder_namespace={
        "new_model": map_builder_new_model,
        "new_layout": map_builder_new_layout,
        "new_model_layout_mapping": map_builder_new_model_layout_mapping,
        "new_model_element": map_builder_new_model_element,
        "new_layout_element": map_builder_new_layout_element,
        "add_model_element": map_builder_add_model_element,
        "add_layout_element": map_builder_add_layout_element,
        "add_layout_element_to_model_element": map_builder_add_layout_element_to_model_element,
        "get_layout_elements": map_builder_get_layout_elements
    }
)

PointBuilder = get_or_make_builder_cls(momapy.geometry.Point)
BboxBuilder = get_or_make_builder_cls(momapy.geometry.Bbox)


def relative_point(obj=None, func=None, args=None, kwargs=None):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    return RelativePointBuilder(obj, func, args, kwargs)
