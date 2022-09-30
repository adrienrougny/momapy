from abc import ABC
from dataclasses import dataclass, field
from types import MethodType
from typing import Any, Optional, Union, Callable


@dataclass
class Event(ABC):
    pass


@dataclass
class AttributeGet(Event):
    obj: Any
    attribute: str


@dataclass
class AttributeSet(Event):
    obj: Any
    attribute: str
    value: Any


class ConnectableAttribute(object):
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is not None:
            if (
                self.name in obj.attribute_callbacks
                and "get" in obj.attribute_callbacks[self.name]
            ):
                for callback in obj.attribute_callbacks[self.name]["get"]:
                    callback(obj, AttributeGet(obj, self.name))
            return obj.__dict__[self.name]
        else:
            return objtype.__dict__[self.name]

    def __set__(self, obj, value):
        if self.name in obj.attribute_callbacks:
            if "set" in obj.attribute_callbacks[self.name]:
                for callback in obj.attribute_callbacks[self.name]["set"]:
                    callback(obj, AttributeSet(obj, self.name, value))
        obj.__dict__[self.name] = value


@dataclass
class ConnectableObject(object):
    def connect_attribute(self, attribute, event_type, callback):
        if attribute not in self.attribute_callbacks:
            self.attribute_callbacks[attribute] = {}
        if event_type not in self.attribute_callbacks[attribute]:
            self.attribute_callbacks[attribute][event_type] = set()
        self.attribute_callbacks[attribute][event_type].add(callback)

    @property
    def attribute_callbacks(self):
        if not hasattr(self, "_attribute_callbacks"):
            self._attribute_callbacks = {}
        return self._attribute_callbacks

    def connectables(self):
        connectables = []
        for name, attribute in type(self).__dict__.items():
            if isinstance(attribute, ConnectableAttribute):
                connectables.append(name)
        return connectables


@dataclass(eq=False)
class UpdatedObject(ConnectableObject):
    obj: Optional[Any] = None
    func: Optional[Union[str, Callable]] = None
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    updated = ConnectableAttribute()

    def __post_init__(self):
        self.updated = True
        self.update()
        for item in [self.obj] + self.args + list(self.kwargs.values()):
            if isinstance(item, ConnectableObject):
                for connectable in item.connectables():
                    item.connect_attribute(
                        connectable, "set", self._set_to_update
                    )

    @property
    def value(self):
        if not self.updated:
            self.update()
        return self._value

    def update(self):
        if self.obj is None:
            value = self.func(*self.args, **self.kwargs)
        else:
            if isinstance(self.func, str):
                func = getattr(self.obj, self.func)
                if isinstance(func, MethodType) and func.__self__ == self.obj:
                    value = func(*self.args, **self.kwargs)
                else:
                    value = func
        self._value = value
        self.updated = True

    def _set_to_update(self, obj, event):
        self.updated = False

    def __getattribute__(self, name):
        if name in [
            "__post_init__",
            "attribute_callbacks",
            "_attribute_callbacks",
            "__dict__",
            "obj",
            "func",
            "updated",
            "update",
            "_set_to_update",
            "value",
            "_value",
            "connectables",
            "connect_attribute",
            "args",
            "kwargs",
        ]:
            return object.__getattribute__(self, name)
        else:
            return getattr(self.value, name)

    def __add__(self, other):
        return self.value.__add__(other)

    def __sub__(self, other):
        return self.value.__sub__(other)

    def __div__(self, other):
        return self.value.__div__(other)

    def __mul__(self, other):
        return self.value.__mul__(other)

    def __len__(self):
        return self.value.__len__()

    def __iter__(self):
        return self.value.__iter__()


def updated_object(obj=None, func=None, args=None, kwargs=None):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    return UpdatedObject(obj=obj, func=func, args=args, kwargs=kwargs)

    ### in builder class
    # for field_ in builder_fields:
    #    connectable_attribute = ConnectableAttribute()
    #    setattr(builder, field_[0], connectable_attribute)
    #    connectable_attribute.__set_name__(builder, field_[0])
