import dataclasses
import typing
import abc

_registered_object_callbacks = {}
_registered_attribute_callbacks = {}


@dataclasses.dataclass(frozen=True)
class Event(abc.ABC):
    obj: typing.Any


@dataclasses.dataclass(frozen=True)
class ChangedEvent(Event):
    attr_name: None | str = None


@dataclasses.dataclass(frozen=True)
class SetEvent(Event):
    attr_name: str


def register_event(obj, event_cls, callback, attr_name=None):
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
        _registered_attribute_callbacks[id(obj)][attr_name][event_cls].append(
            callback
        )
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
    register_event(obj, ChangedEvent, callback, attr_name)


def on_set(obj, callback, attr_name=None):
    register_event(obj, SetEvent, callback, attr_name)


def trigger_event(event):
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
            and event.attr_name
            in _registered_attribute_callbacks[id(event.obj)]
            and type(event)
            in _registered_attribute_callbacks[id(event.obj)][event.attr_name]
        ):
            callbacks = _registered_attribute_callbacks[id(event.obj)][
                event.attr_name
            ][type(event)]
        else:
            callbacks = []
    for callback in callbacks:
        callback(event)


@dataclasses.dataclass
class Monitored:
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        trigger_event(SetEvent(self, name))
