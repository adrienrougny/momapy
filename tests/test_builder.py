"""Tests for momapy.builder module."""
import pytest
import dataclasses
import momapy.builder


@dataclasses.dataclass(frozen=True)
class SimpleClass:
    """Simple dataclass for testing builders."""
    value: int
    name: str


def test_isinstance_or_builder():
    """Test isinstance_or_builder function."""
    obj = SimpleClass(42, "test")
    assert momapy.builder.isinstance_or_builder(obj, SimpleClass)
    assert not momapy.builder.isinstance_or_builder("string", SimpleClass)


def test_get_or_make_builder_cls():
    """Test get_or_make_builder_cls function."""
    # Test with a simple dataclass
    builder_cls = momapy.builder.get_or_make_builder_cls(SimpleClass)

    # Builder class should be created
    assert builder_cls is not None
    assert issubclass(builder_cls, momapy.builder.Builder)


def test_builder_from_object():
    """Test creating a builder from an object."""
    obj = SimpleClass(42, "test")
    builder_cls = momapy.builder.get_or_make_builder_cls(SimpleClass)
    builder = builder_cls.from_object(obj)

    assert isinstance(builder, momapy.builder.Builder)
    assert builder.value == 42
    assert builder.name == "test"


def test_builder_build():
    """Test building an object from a builder."""
    obj = SimpleClass(42, "test")
    builder_cls = momapy.builder.get_or_make_builder_cls(SimpleClass)
    builder = builder_cls.from_object(obj)

    # Build back to object
    rebuilt_obj = builder.build()

    assert isinstance(rebuilt_obj, SimpleClass)
    assert rebuilt_obj.value == 42
    assert rebuilt_obj.name == "test"


def test_builder_from_object_function():
    """Test builder_from_object utility function."""
    obj = SimpleClass(42, "test")
    builder = momapy.builder.builder_from_object(obj)

    assert isinstance(builder, momapy.builder.Builder)


def test_object_from_builder_function():
    """Test object_from_builder utility function."""
    obj = SimpleClass(42, "test")
    builder = momapy.builder.builder_from_object(obj)
    rebuilt_obj = momapy.builder.object_from_builder(builder)

    assert isinstance(rebuilt_obj, SimpleClass)
    assert rebuilt_obj.value == 42
    assert rebuilt_obj.name == "test"


def test_builder_registry():
    """Test that builders dictionary exists."""
    assert isinstance(momapy.builder.builders, dict)
