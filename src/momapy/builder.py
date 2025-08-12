"""Classes and functions for building maps and map elements"""

import abc
import dataclasses
import typing
import types
import inspect

import frozendict

import momapy.monitoring


class Builder(abc.ABC, momapy.monitoring.Monitored):
    """Abstract class for builder objects"""

    _cls_to_build: typing.ClassVar[type]

    @abc.abstractmethod
    def build(
        self,
        inside_collections: bool = True,
        builder_to_object: dict[int, typing.Any] | None = None,
    ) -> typing.Any:
        """Build and return an object from the builder object"""
        pass

    @classmethod
    @abc.abstractmethod
    def from_object(
        cls,
        obj: typing.Any,
        inside_collections: bool = True,
        omit_keys: bool = True,
        object_to_builder: dict[int, "Builder"] | None = None,
    ) -> typing.Self:
        """Create and return a builder object from an object"""
        pass


builders = {}


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
                else:
                    new_o_type = get_or_make_builder_cls(o_type)
            else:  # o_type is an object from typing
                new_o_type = o_type
            new_type = new_o_type[
                tuple([_transform_type(a_type) for a_type in typing.get_args(type_)])
            ]
        else:  # type_ has no origin
            if isinstance(type_, type):  # type_ is a type
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
        inside_collections: bool = True,
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
                inside_collections=inside_collections,
                builder_to_object=builder_to_object,
            )
        obj = self._cls_to_build(**args)
        builder_to_object[id(self)] = obj
        return obj

    def _builder_from_object(
        cls,
        obj,
        inside_collections: bool = True,
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
                inside_collections=inside_collections,
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
    inside_collections=True,
    builder_to_object: dict[int, typing.Any] | None = None,
):
    """Create and return an object from a builder object"""
    if builder_to_object is not None:
        if id(builder) in builder_to_object:
            return builder_to_object[id(builder)]
    else:
        builder_to_object = {}
    if isinstance(builder, Builder):
        obj = builder.build(
            inside_collections=inside_collections,
            builder_to_object=builder_to_object,
        )
        builder_to_object[id(builder)] = obj
        return obj
    if inside_collections:
        if isinstance(builder, (list, tuple, set, frozenset)):
            return type(builder)(
                [
                    object_from_builder(
                        builder=e,
                        inside_collections=inside_collections,
                        builder_to_object=builder_to_object,
                    )
                    for e in builder
                ]
            )
        elif isinstance(builder, (dict, frozendict.frozendict)):
            return type(builder)(
                [
                    (
                        object_from_builder(
                            builder=k,
                            inside_collections=inside_collections,
                            builder_to_object=builder_to_object,
                        ),
                        object_from_builder(
                            builder=v,
                            inside_collections=inside_collections,
                            builder_to_object=builder_to_object,
                        ),
                    )
                    for k, v in builder.items()
                ]
            )
    return builder


def builder_from_object(
    obj: typing.Any,
    inside_collections=True,
    omit_keys=True,
    object_to_builder: dict[int, "Builder"] | None = None,
) -> Builder:
    """Create and return a builder object from an object"""
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
            inside_collections=inside_collections,
            omit_keys=omit_keys,
            object_to_builder=object_to_builder,
        )
    if inside_collections:
        if isinstance(obj, (list, tuple, set, frozenset)):
            return type(obj)(
                [
                    builder_from_object(
                        obj=e,
                        inside_collections=inside_collections,
                        omit_keys=omit_keys,
                        object_to_builder=object_to_builder,
                    )
                    for e in obj
                ]
            )
        elif isinstance(obj, (dict, frozendict.frozendict)):
            return type(obj)(
                [
                    (
                        (
                            builder_from_object(
                                obj=k,
                                inside_collections=inside_collections,
                                omit_keys=omit_keys,
                                object_to_builder=object_to_builder,
                            ),
                            builder_from_object(
                                obj=v,
                                inside_collections=inside_collections,
                                omit_keys=omit_keys,
                                object_to_builder=object_to_builder,
                            ),
                        )
                        if not omit_keys
                        else (
                            k,
                            builder_from_object(
                                obj=v,
                                inside_collections=inside_collections,
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
    """Create and return a builder object from an object class or a builder class"""
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
    """Get and return an existing builder class for the given class or make and return a new builder class for it"""
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
    """Return `true` if there is a registered builder class for the given class, and `false` otherwise"""
    return cls in builders


def get_builder_cls(cls: typing.Type) -> typing.Type:
    """Return the builder class registered for the given class or `None` if no builder class is registered for that class"""
    return builders.get(cls)


def register_builder_cls(builder_cls: typing.Type) -> None:
    """Register a builder class"""
    builders[builder_cls._cls_to_build] = builder_cls


def isinstance_or_builder(
    obj: typing.Any, type_: typing.Type | tuple[typing.Type]
) -> bool:
    """Return `true` if the object is an istance of the given classes or of their registered builder classes, and `false` otherwise"""
    if isinstance(type_, type):
        type_ = (type_,)
    type_ += tuple([get_or_make_builder_cls(t) for t in type_])
    return isinstance(obj, type_)


def issubclass_or_builder(
    cls: typing.Type, type_: typing.Type | tuple[typing.Type]
) -> bool:
    """Return `true` if the class is a subclass of the given classes or of their registered builder classes, and `false` otherwise"""
    if isinstance(type_, type):
        type_ = (type_,)
    type_ += tuple([get_or_make_builder_cls(t) for t in type_])
    return issubclass(cls, type_)


def super_or_builder(type_: typing.Type, obj: typing.Any) -> typing.Type:
    """Return the super class for a given class or its builder class and an object"""
    try:
        s = super(type_, obj)
    except TypeError:
        builder = get_or_make_builder_cls(type_)
        s = super(builder, obj)
    finally:
        return s
