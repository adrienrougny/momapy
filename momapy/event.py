from abc import ABC
from dataclasses import dataclass, field
from typing import Any

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

class Connectable(object):

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is not None:
            if self.name in obj._attribute_callbacks and "get" in obj._attribute_callbacks[self.name]:
                for callback in obj._attribute_callbacks[self.name]["get"]:
                    callback(obj, AttributeGet(obj, self.name))
            return obj.__dict__[self.name]
        else:
            return objtype.__dict__[self.name]

    def __set__(self, obj, value):
        if self.name in obj._attribute_callbacks:
            if "set" in obj._attribute_callbacks[self.name]:
                for callback in obj._attribute_callbacks[self.name]["set"]:
                    callback(obj, AttributeSet(obj, self.name, value))
        obj.__dict__[self.name] = value
