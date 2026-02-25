"""Classes and functions for building objects from dataclasses.

This module provides functionality to automatically generate builder classes
from dataclasses, allowing for flexible object construction and transformation
between objects and their builder representations.

Example:
    >>> from dataclasses import dataclass
    >>> @dataclass
    ... class Person:
    ...     name: str
    ...     age: int
    >>>
    >>> # Create a builder class automatically
    >>> Builder = get_or_make_builder_cls(Person)
    >>> builder = Builder(name="John", age=30)
    >>> person = builder.build()
    >>> print(person)
    Person(name='John', age=30)
"""

import abc
import dataclasses
import typing
import typing_extensions
import types
import inspect

import frozendict

import momapy.monitoring


class Builder(abc.ABC, momapy.monitoring.Monitored):
    """Abstract base class for builder objects.

    Builder classes are automatically generated from dataclasses to provide
    a mutable representation for constructing immutable objects.

    Attributes:
        _cls_to_build: The class that this builder constructs.
    """

    _cls_to_build: typing.ClassVar[type]
    __hash__ = object.__hash__

    @abc.abstractmethod
    def build(
        self,
        builder_to_object: dict[int, typing.Any] | None = None,
    ) -> typing.Any:
        """Build and return an object from the builder.

        Args:
            builder_to_object: Optional cache mapping builder ids to built
                objects for handling circular references.

        Returns:
            The constructed object of type `_cls_to_build`.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def from_object(
        cls,
        obj: typing.Any,
        omit_keys: bool = True,
        object_to_builder: dict[int, "Builder"] | None = None,
    ) -> typing_extensions.Self:
        """Create a builder from an existing object.

        Args:
            obj: The object to convert to a builder.
            omit_keys: Whether to skip converting dictionary keys to builders.
                Defaults to True.
            object_to_builder: Optional cache mapping object ids to builders
                for handling circular references.

        Returns:
            A builder instance representing the input object.
        """
        pass


builders = {}

_builder_collection_to_immutable: dict[type, type] = {
    list: tuple,
    set: frozenset,
    dict: frozendict.frozendict,
}
_immutable_collection_to_builder: dict[type, type] = {
    tuple: list,
    frozenset: set,
    frozendict.frozendict: dict,
}


def _transform_type(type_, make_optional=False, make_union=False):
    if isinstance(
        type_, typing.ForwardRef
    ):  # TO DO: should find if type is already in builders first
        new_type = typing.ForwardRef(f"{type_.__forward_arg__}Builder")
    else:
        # We get the origin of type_, e.g., if type_ = X[Y, Z, ...] we get X
        o_type = typing.get_origin(type_)  # returns None if not supported
        if o_type is not None:
            if isinstance(o_type, type):  # o_type is a type
                if o_type == types.UnionType:  # from t1 | t2 syntax
                    new_o_type = typing.Union
                elif o_type in _immutable_collection_to_builder:
                    new_o_type = _immutable_collection_to_builder[o_type]
                else:
                    new_o_type = get_or_make_builder_cls(o_type)
            else:  # o_type is an object from typing
                new_o_type = o_type
            new_type = new_o_type[
                tuple([_transform_type(a_type) for a_type in typing.get_args(type_)])
            ]
        else:  # type_ has no origin
            if isinstance(type_, type):  # type_ is a type
                if type_ in _immutable_collection_to_builder:
                    new_type = _immutable_collection_to_builder[type_]
                else:
                    new_type = get_or_make_builder_cls(type_)
                    if new_type is None:
                        new_type = type_
            else:
                new_type = type_
    if make_optional:
        new_type = typing.Optional[new_type]
    if make_union:
        new_type = typing.Union[type_, new_type]
    return new_type


def _make_builder_cls(
    cls, builder_fields=None, builder_bases=None, builder_namespace=None
):
    def _builder_build(
        self,
        builder_to_object: dict[int, typing.Any] | None = None,
    ):
        if builder_to_object is not None:
            obj = builder_to_object.get(id(self))
            if obj is not None:
                return obj
        else:
            builder_to_object = {}
        args = {}
        for field in dataclasses.fields(self):
            attr_value = getattr(self, field.name)
            args[field.name] = object_from_builder(
                builder=attr_value,
                builder_to_object=builder_to_object,
            )
        obj = self._cls_to_build(**args)
        builder_to_object[id(self)] = obj
        return obj

    def _builder_from_object(
        cls,
        obj,
        omit_keys: bool = True,
        object_to_builder: dict[int, "Builder"] | None = None,
    ):
        if object_to_builder is not None:
            builder = object_to_builder.get(id(obj))
            if builder is not None:
                return builder
        else:
            object_to_builder = {}
        args = {}
        for field_ in dataclasses.fields(obj):
            attr_value = getattr(obj, field_.name)
            args[field_.name] = builder_from_object(
                obj=attr_value,
                omit_keys=omit_keys,
                object_to_builder=object_to_builder,
            )
        builder = cls(**args)
        object_to_builder[id(obj)] = builder
        return builder

    if builder_fields is None:
        builder_fields = []
    if builder_bases is None:
        builder_bases = []
    if builder_namespace is None:
        builder_namespace = {}
    # We transform the fields to builder fields
    cls_fields = dataclasses.fields(cls)
    builder_field_names = set([builder_field[0] for builder_field in builder_fields])
    for field_ in cls_fields:
        field_name = field_.name
        # We only consider fields that are not already in the input fields
        if field_name not in builder_field_names:
            field_dict = {}
            has_default = False
            if field_.default_factory != dataclasses.MISSING:
                if isinstance(field_.default_factory, type):
                    field_dict["default_factory"] = _transform_type(
                        field_.default_factory
                    )
                else:  # in case of a func for example
                    field_dict["default_factory"] = field_.default_factory
                has_default = True
            if field_.default != dataclasses.MISSING:
                field_dict["default"] = field_.default  # TO DO: transform?
                has_default = True
            if not has_default:
                field_dict["default"] = None
            field_type = _transform_type(
                field_.type, make_optional=not has_default, make_union=True
            )
            builder_fields.append(
                (field_name, field_type, dataclasses.field(**field_dict))
            )
    builder_namespace["build"] = _builder_build
    builder_namespace["from_object"] = classmethod(_builder_from_object)
    builder_namespace["_cls_to_build"] = cls
    # We add the undundered methods from the non-builder class
    # Do we really want this? Should we keep builders really only to build?
    for member in inspect.getmembers(cls):
        func_name = member[0]
        func = member[1]

        if not func_name.startswith("__") and not func_name == "_cls_to_build":
            builder_namespace[func_name] = func
    # We add the transformed bases
    cls_bases = [get_or_make_builder_cls(base_cls) for base_cls in cls.__bases__]
    builder_bases = builder_bases + [
        base_cls for base_cls in cls_bases if issubclass(base_cls, Builder)
    ]
    # We add the Builder class to the bases
    has_builder_cls = False
    for builder_base in builder_bases:
        if Builder in builder_base.__mro__:
            has_builder_cls = True
            break
    if not has_builder_cls:
        builder_bases = [Builder] + builder_bases
    builder_bases = tuple(builder_bases)

    builder = dataclasses.make_dataclass(
        cls_name=f"{cls.__name__}Builder",
        fields=builder_fields,
        bases=builder_bases,
        namespace=builder_namespace,
        eq=False,
        kw_only=False,
    )
    return builder


def object_from_builder(
    builder: Builder,
    builder_to_object: dict[int, typing.Any] | None = None,
):
    """Convert a builder (or collection of builders) to actual object(s).

    Recursively converts builder objects to their corresponding class instances.
    Handles collections (list, tuple, set, dict) and circular references.
    Mutable collection types are converted to their immutable counterparts:
    list → tuple, set → frozenset, dict → frozendict.

    Args:
        builder: A builder instance, collection of builders, or regular object.
        builder_to_object: Optional cache mapping builder ids to already-built
            objects for handling circular references.

    Returns:
        The built object, collection of built objects, or the original value
        if not a builder.

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class Point:
        ...     x: float
        ...     y: float
        >>>
        >>> PointBuilder = get_or_make_builder_cls(Point)
        >>> builder = PointBuilder(x=1.0, y=2.0)
        >>> point = object_from_builder(builder)
        >>> print(point)
        Point(x=1.0, y=2.0)
    """
    if builder_to_object is not None:
        if id(builder) in builder_to_object:
            return builder_to_object[id(builder)]
    else:
        builder_to_object = {}
    if isinstance(builder, Builder):
        obj = builder.build(
            builder_to_object=builder_to_object,
        )
        builder_to_object[id(builder)] = obj
        return obj
    if isinstance(builder, (list, tuple, set, frozenset)):
        target = _builder_collection_to_immutable.get(type(builder), type(builder))
        return target(
            [
                object_from_builder(
                    builder=e,
                    builder_to_object=builder_to_object,
                )
                for e in builder
            ]
        )
    elif isinstance(builder, (dict, frozendict.frozendict)):
        target = _builder_collection_to_immutable.get(type(builder), type(builder))
        return target(
            [
                (
                    object_from_builder(
                        builder=k,
                        builder_to_object=builder_to_object,
                    ),
                    object_from_builder(
                        builder=v,
                        builder_to_object=builder_to_object,
                    ),
                )
                for k, v in builder.items()
            ]
        )
    return builder


def builder_from_object(
    obj: typing.Any,
    omit_keys=True,
    object_to_builder: dict[int, "Builder"] | None = None,
) -> Builder:
    """Convert an object (or collection of objects) to builder(s).

    Recursively converts class instances to their corresponding builder objects.
    Handles collections (list, tuple, set, dict) and circular references.
    Immutable collection types are converted to their mutable counterparts:
    tuple → list, frozenset → set, frozendict → dict.

    Args:
        obj: An object instance, collection of objects, or any value.
        omit_keys: Whether to skip converting dictionary keys to builders.
            Defaults to True.
        object_to_builder: Optional cache mapping object ids to already-created
            builders for handling circular references.

    Returns:
        The builder object, collection of builders, or the original value
        if no builder class exists.

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class Point:
        ...     x: float
        ...     y: float
        >>>
        >>> point = Point(x=1.0, y=2.0)
        >>> builder = builder_from_object(point)
        >>> print(type(builder).__name__)
        PointBuilder
    """
    if object_to_builder is not None:
        builder = object_to_builder.get(id(obj))
        if builder is not None:
            return builder
    else:
        object_to_builder = {}
    cls = get_or_make_builder_cls(type(obj))
    if issubclass(cls, Builder):
        return cls.from_object(
            obj=obj,
            omit_keys=omit_keys,
            object_to_builder=object_to_builder,
        )
    if isinstance(obj, (list, tuple, set, frozenset)):
        builder_type = _immutable_collection_to_builder.get(type(obj), type(obj))
        return builder_type(
            [
                builder_from_object(
                    obj=e,
                    omit_keys=omit_keys,
                    object_to_builder=object_to_builder,
                )
                for e in obj
            ]
        )
    elif isinstance(obj, (dict, frozendict.frozendict)):
        builder_type = _immutable_collection_to_builder.get(type(obj), type(obj))
        return builder_type(
            [
                (
                    (
                        builder_from_object(
                            obj=k,
                            omit_keys=omit_keys,
                            object_to_builder=object_to_builder,
                        ),
                        builder_from_object(
                            obj=v,
                            omit_keys=omit_keys,
                            object_to_builder=object_to_builder,
                        ),
                    )
                    if not omit_keys
                    else (
                        k,
                        builder_from_object(
                            obj=v,
                            omit_keys=omit_keys,
                            object_to_builder=object_to_builder,
                        ),
                    )
                )
                for k, v in obj.items()
            ]
        )
    return obj


def new_builder_object(cls: typing.Type, *args, **kwargs) -> Builder:
    """Create a new builder instance for a given class.

    Args:
        cls: The class to build (or a builder class).
        *args: Positional arguments for the builder.
        **kwargs: Keyword arguments for the builder.

    Returns:
        A new builder instance.

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class Person:
        ...     name: str
        ...     age: int = 0
        >>>
        >>> builder = new_builder_object(Person, name="Alice")
        >>> print(builder.name)
        Alice
    """
    if not issubclass(cls, Builder):
        cls = get_or_make_builder_cls(cls)
    return cls(*args, **kwargs)


def get_or_make_builder_cls(
    cls: typing.Type,
    builder_fields: (
        typing.Collection[tuple[str, typing.Type, dataclasses.Field]] | None
    ) = None,
    builder_bases: typing.Collection[typing.Type] | None = None,
    builder_namespace: dict[str, typing.Any] | None = None,
) -> typing.Type:
    """Get an existing builder class or create a new one.

    Returns the registered builder class for the given class if it exists,
    otherwise creates and registers a new builder class.

    Args:
        cls: The class to get or create a builder for.
        builder_fields: Optional collection of additional fields to include
            in the builder class.
        builder_bases: Optional collection of base classes for the builder.
        builder_namespace: Optional namespace dictionary for the builder class.

    Returns:
        The builder class for the given class, or the original class if
        it's not a dataclass.

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class Point:
        ...     x: float
        ...     y: float
        >>>
        >>> PointBuilder = get_or_make_builder_cls(Point)
        >>> print(PointBuilder.__name__)
        PointBuilder
    """
    builder_cls = get_builder_cls(cls)
    if builder_cls is None:
        if dataclasses.is_dataclass(cls):
            builder_cls = _make_builder_cls(
                cls, builder_fields, builder_bases, builder_namespace
            )
            register_builder_cls(builder_cls)
        else:
            builder_cls = cls
    return builder_cls


def has_builder_cls(cls: typing.Type) -> bool:
    """Check if a builder class is registered for a given class.

    Args:
        cls: The class to check.

    Returns:
        True if a builder class is registered, False otherwise.
    """
    return cls in builders


def get_builder_cls(cls: typing.Type) -> typing.Type:
    """Get the registered builder class for a given class.

    Args:
        cls: The class to get the builder for.

    Returns:
        The builder class if registered, None otherwise.
    """
    return builders.get(cls)


def register_builder_cls(builder_cls: typing.Type) -> None:
    """Register a builder class.

    Registers a builder class so it can be looked up by its target class.

    Args:
        builder_cls: The builder class to register. Must have a `_cls_to_build`
            attribute indicating the target class.
    """
    builders[builder_cls._cls_to_build] = builder_cls


def isinstance_or_builder(
    obj: typing.Any, type_: typing.Type | tuple[typing.Type]
) -> bool:
    """Check if object is instance of class or its builder class.

    Extends isinstance() to also check against registered builder classes.

    Args:
        obj: The object to check.
        type_: The type or tuple of types to check against.

    Returns:
        True if obj is an instance of type_ or its builder class(es).

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class Point:
        ...     x: float
        ...     y: float
        >>>
        >>> PointBuilder = get_or_make_builder_cls(Point)
        >>> builder = PointBuilder(x=1.0, y=2.0)
        >>> isinstance_or_builder(builder, Point)
        True
    """
    if isinstance(type_, type):
        type_ = (type_,)
    type_ += tuple([get_or_make_builder_cls(t) for t in type_])
    return isinstance(obj, type_)


def issubclass_or_builder(
    cls: typing.Type, type_: typing.Type | tuple[typing.Type]
) -> bool:
    """Check if class is subclass of class or its builder class.

    Extends issubclass() to also check against registered builder classes.

    Args:
        cls: The class to check.
        type_: The type or tuple of types to check against.

    Returns:
        True if cls is a subclass of type_ or its builder class(es).
    """
    if isinstance(type_, type):
        type_ = (type_,)
    type_ += tuple([get_or_make_builder_cls(t) for t in type_])
    return issubclass(cls, type_)


def super_or_builder(type_: typing.Type, obj: typing.Any) -> typing.Type:
    """Get super() proxy for a class or its builder class.

    Attempts to get the super() proxy for the given type. If that fails,
    tries with the builder class of the given type.

    Args:
        type_: The class to get super() for.
        obj: The object to get the super proxy of.

    Returns:
        A super() proxy object.
    """
    try:
        s = super(type_, obj)
    except TypeError:
        builder = get_or_make_builder_cls(type_)
        s = super(builder, obj)
    finally:
        return s
