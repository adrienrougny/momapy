"""Event monitoring module for tracking object changes.

This module provides a system for registering and triggering events on objects,
including changes to object attributes and attribute sets. It supports both
object-level and attribute-level event monitoring.

Example:
    >>> from momapy.monitoring import Monitored, on_change, trigger_event
    >>> class MyClass(Monitored):
    ...     def __init__(self):
    ...         super().__init__()
    ...         self.value = 0
    >>> obj = MyClass()
    >>> on_change(obj, lambda e: print(f"Changed: {e.attr_name}"))
    >>> obj.value = 5
    Changed: value
"""

import dataclasses
import typing
import abc

_registered_object_callbacks = {}
_registered_attribute_callbacks = {}


@dataclasses.dataclass(frozen=True)
class Event(abc.ABC):
    """Base class for all events.

    Attributes:
        obj: The object that triggered the event.
    """

    obj: typing.Any


@dataclasses.dataclass(frozen=True)
class ChangedEvent(Event):
    """Event triggered when an object or attribute changes.

    Attributes:
        obj: The object that triggered the event.
        attr_name: Name of the changed attribute, or None for object-level changes.
    """

    attr_name: None | str = None


@dataclasses.dataclass(frozen=True)
class SetEvent(Event):
    """Event triggered when an attribute is set.

    Attributes:
        obj: The object that triggered the event.
        attr_name: Name of the attribute that was set.
    """

    attr_name: str


def register_event(obj, event_cls, callback, attr_name=None):
    """Register a callback for an event on an object.

    Args:
        obj: The object to monitor.
        event_cls: The event class to listen for (e.g., ChangedEvent, SetEvent).
        callback: Function to call when the event occurs.
        attr_name: Optional attribute name for attribute-specific monitoring.

    Example:
        >>> register_event(my_obj, ChangedEvent, my_callback)
        >>> register_event(my_obj, SetEvent, my_callback, "value")
    """
    if attr_name is None:
        if id(obj) not in _registered_object_callbacks:
            _registered_object_callbacks[id(obj)] = {}
        if event_cls not in _registered_object_callbacks[id(obj)]:
            _registered_object_callbacks[id(obj)][event_cls] = []
        _registered_object_callbacks[id(obj)][event_cls].append(callback)
        if (
            event_cls == ChangedEvent or event_cls == SetEvent
        ) and dataclasses.is_dataclass(obj):
            for field_ in dataclasses.fields(obj):
                field_name = field_.name
                register_event(
                    obj,
                    event_cls,
                    lambda event: trigger_event(event_cls(obj)),
                    field_name,
                )
    else:
        if id(obj) not in _registered_attribute_callbacks:
            _registered_attribute_callbacks[id(obj)] = {}
        if attr_name not in _registered_attribute_callbacks[id(obj)]:
            _registered_attribute_callbacks[id(obj)][attr_name] = {}
        if event_cls not in _registered_attribute_callbacks[id(obj)][attr_name]:
            _registered_attribute_callbacks[id(obj)][attr_name][event_cls] = []
        _registered_attribute_callbacks[id(obj)][attr_name][event_cls].append(callback)
        if event_cls == ChangedEvent:
            on_set(
                obj,
                lambda event: trigger_event(ChangedEvent(obj, attr_name)),
                attr_name,
            )
            on_change(
                getattr(obj, attr_name),
                lambda event: trigger_event(ChangedEvent(obj, attr_name)),
            )


def on_change(obj, callback, attr_name=None):
    """Register a callback for change events on an object.

    Args:
        obj: The object to monitor.
        callback: Function to call when the object or attribute changes.
        attr_name: Optional attribute name for attribute-specific monitoring.

    Example:
        >>> on_change(my_obj, lambda e: print("Object changed"))
        >>> on_change(my_obj, lambda e: print("Value changed"), "value")
    """
    register_event(obj, ChangedEvent, callback, attr_name)


def on_set(obj, callback, attr_name=None):
    """Register a callback for set events on an object.

    Args:
        obj: The object to monitor.
        callback: Function to call when an attribute is set.
        attr_name: Optional attribute name for attribute-specific monitoring.

    Example:
        >>> on_set(my_obj, lambda e: print("Attribute set"))
        >>> on_set(my_obj, lambda e: print("Value set"), "value")
    """
    register_event(obj, SetEvent, callback, attr_name)


def trigger_event(event):
    """Trigger an event and call all registered callbacks.

    Args:
        event: The event instance to trigger.

    Example:
        >>> trigger_event(ChangedEvent(my_obj, "value"))
    """
    if event.attr_name is None:
        if (
            id(event.obj) in _registered_object_callbacks
            and type(event) in _registered_object_callbacks[id(event.obj)]
        ):
            callbacks = _registered_object_callbacks[id(event.obj)][type(event)]
        else:
            callbacks = []
    else:
        if (
            id(event.obj) in _registered_attribute_callbacks
            and event.attr_name in _registered_attribute_callbacks[id(event.obj)]
            and type(event)
            in _registered_attribute_callbacks[id(event.obj)][event.attr_name]
        ):
            callbacks = _registered_attribute_callbacks[id(event.obj)][event.attr_name][
                type(event)
            ]
        else:
            callbacks = []
    for callback in callbacks:
        callback(event)


@dataclasses.dataclass
class Monitored:
    """Base class for objects that automatically trigger events on attribute changes.

    Inherit from this class to enable automatic SetEvent triggering when
    attributes are modified.

    Example:
        >>> class MyClass(Monitored):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self.value = 0
        >>> obj = MyClass()
        >>> on_set(obj, lambda e: print(f"Set: {e.attr_name}"))
        >>> obj.value = 5
        Set: value
    """

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        trigger_event(SetEvent(self, name))
