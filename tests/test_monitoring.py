"""Tests for momapy.monitoring module."""
import pytest
import dataclasses
import momapy.monitoring


@dataclasses.dataclass
class SampleObject:
    """Simple dataclass for testing monitoring."""
    value: int = 0
    name: str = "test"


@dataclasses.dataclass
class MonitoredSampleObject(momapy.monitoring.Monitored):
    """Monitored dataclass for testing."""
    value: int = 0


def test_event_creation():
    """Test Event subclass creation."""
    obj = SampleObject()
    changed_event = momapy.monitoring.ChangedEvent(obj)
    assert changed_event.obj is obj
    assert changed_event.attr_name is None

    changed_event_with_attr = momapy.monitoring.ChangedEvent(obj, "value")
    assert changed_event_with_attr.obj is obj
    assert changed_event_with_attr.attr_name == "value"

    set_event = momapy.monitoring.SetEvent(obj, "value")
    assert set_event.obj is obj
    assert set_event.attr_name == "value"


def test_register_event_object_callback():
    """Test registering a callback for an object."""
    obj = SampleObject()
    callback_called = []

    def callback(event):
        callback_called.append(event)

    momapy.monitoring.register_event(obj, momapy.monitoring.ChangedEvent, callback)

    # Trigger event manually
    momapy.monitoring.trigger_event(momapy.monitoring.ChangedEvent(obj))

    assert len(callback_called) == 1
    assert isinstance(callback_called[0], momapy.monitoring.ChangedEvent)


def test_on_change():
    """Test on_change function."""
    obj = SampleObject()
    callback_called = []

    def callback(event):
        callback_called.append(event)

    momapy.monitoring.on_change(obj, callback)
    momapy.monitoring.trigger_event(momapy.monitoring.ChangedEvent(obj))

    assert len(callback_called) >= 1


def test_on_set():
    """Test on_set function."""
    obj = SampleObject()
    callback_called = []

    def callback(event):
        callback_called.append(event)

    momapy.monitoring.on_set(obj, callback, "value")
    momapy.monitoring.trigger_event(momapy.monitoring.SetEvent(obj, "value"))

    assert len(callback_called) >= 1


def test_monitored_class():
    """Test Monitored class."""
    obj = MonitoredSampleObject(value=10)
    callback_called = []

    def callback(event):
        callback_called.append(event)

    momapy.monitoring.on_set(obj, callback, "value")

    # Changing the value should trigger the callback
    obj.value = 20

    assert len(callback_called) >= 1
    assert obj.value == 20


def test_trigger_event_no_callbacks():
    """Test triggering event with no registered callbacks."""
    obj = SampleObject()
    event = momapy.monitoring.ChangedEvent(obj)

    # Should not raise any exception
    momapy.monitoring.trigger_event(event)
