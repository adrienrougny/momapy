import abc
import dataclasses
import typing
import types
import inspect


class Builder(abc.ABC):
    _cls_to_build: typing.ClassVar[type]

    @abc.abstractmethod
    def build(
        self, builder_object_mapping: dict[int, typing.Any] | None = None
    ):
        pass

    @classmethod
    @abc.abstractmethod
    def from_object(
        cls, obj, object_builder_mapping: dict[int, "Builder"] | None = None
    ):
        pass


builders = {}


def transform_type(type_, make_optional=False):
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
            tuple([transform_type(a_type) for a_type in typing.get_args(type_)])
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
    return new_type


def make_builder_cls(
    cls, builder_fields=None, builder_bases=None, builder_namespace=None
):
    def _builder_build(
        self, builder_object_mapping: dict[int, typing.Any] | None = None
    ):
        if builder_object_mapping is not None:
            obj = builder_object_mapping.get(id(self))
            if obj is not None:
                return obj
        else:
            builder_object_mapping = {}
        args = {}
        for field_ in dataclasses.fields(self):
            attr_value = getattr(self, field_.name)
            args[field_.name] = object_from_builder(
                attr_value, builder_object_mapping
            )
        obj = self._cls_to_build(**args)
        builder_object_mapping[id(self)] = obj
        return obj

    def _builder_from_object(
        cls, obj, object_builder_mapping: dict[int, "Builder"] | None = None
    ):
        if object_builder_mapping is not None:
            builder = object_builder_mapping.get(id(obj))
            if builder is not None:
                return builder
        else:
            object_builder_mapping = {}
        args = {}
        for field_ in dataclasses.fields(obj):
            attr_value = getattr(obj, field_.name)
            args[field_.name] = builder_from_object(
                attr_value, object_builder_mapping
            )
        builder = cls(**args)
        object_builder_mapping[id(obj)] = builder
        return builder

    def _builder_add_element(self, element, fields_for_add_element):
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

    cls_fields = dataclasses.fields(cls)
    if builder_fields is None:
        builder_fields = []
    if builder_bases is None:
        builder_bases = []
    if builder_namespace is None:
        builder_namespace = {}
    fields_for_add_element = []
    builder_field_names = [builder_field[0] for builder_field in builder_fields]
    for field_ in cls_fields:
        field_name = field_.name
        if field_name not in builder_field_names:
            field_dict = {}
            has_default = False
            if field_.default_factory != dataclasses.MISSING:
                field_dict["default_factory"] = transform_type(
                    field_.default_factory
                )
                has_default = True
            if field_.default != dataclasses.MISSING:
                field_dict["default"] = field_.default
                has_default = True
            if not has_default:
                field_dict["default"] = None
            field_type = transform_type(
                field_.type, make_optional=not has_default
            )
            builder_fields.append(
                (field_name, field_type, dataclasses.field(**field_dict))
            )
            field_o_type = typing.get_origin(field_type)
            if (
                field_o_type is not None
                and isinstance(field_o_type, type)
                and issubclass(field_o_type, typing.Collection)
            ):
                fields_for_add_element.append(
                    {
                        "field_name": field_name,
                        "field_type": field_type,
                        "a_types": typing.get_args(field_type),
                    }
                )

    builder_namespace["build"] = _builder_build
    builder_namespace["from_object"] = classmethod(_builder_from_object)
    builder_namespace["_cls_to_build"] = cls

    if fields_for_add_element:
        builder_namespace["add_element"] = (
            lambda fields_for_add_element: lambda self, element: _builder_add_element(
                self, element, fields_for_add_element
            )
        )(fields_for_add_element)

    for member in inspect.getmembers(cls):
        func_name = member[0]
        func = member[1]

        if not func_name.startswith("__") and not func_name == "_cls_to_build":

            builder_namespace[func_name] = func

    cls_bases = [
        get_or_make_builder_cls(base_cls) for base_cls in cls.__bases__
    ]
    builder_bases = builder_bases + [
        base_cls for base_cls in cls_bases if issubclass(base_cls, Builder)
    ]
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
    builder, builder_object_mapping: dict[int, typing.Any] | None = None
):
    if builder_object_mapping is not None:
        if id(builder) in builder_object_mapping:
            return builder_object_mapping[id(builder)]
    else:
        builder_object_mapping = {}
    if isinstance(builder, Builder):
        obj = builder.build(builder_object_mapping)
        builder_object_mapping[id(builder)] = obj
        return obj
    else:
        return builder


def builder_from_object(
    obj, object_builder_mapping: dict[int, "Builder"] | None = None
):
    if object_builder_mapping is not None:
        builder = object_builder_mapping.get(id(obj))
        if builder is not None:
            return builder
    else:
        object_builder_mapping = {}
    cls = get_or_make_builder_cls(type(obj))
    if issubclass(cls, Builder):
        return cls.from_object(obj, object_builder_mapping)
    else:
        return obj


def new_builder(cls, *args, **kwargs):
    if not issubclass(cls, Builder):
        cls = get_or_make_builder_cls(cls)
    return cls(*args, **kwargs)


def get_or_make_builder_cls(
    cls, builder_fields=None, builder_bases=None, builder_namespace=None
):
    builder_cls = get_builder(cls)
    if builder_cls is None:
        if dataclasses.is_dataclass(cls):
            builder_cls = make_builder_cls(
                cls, builder_fields, builder_bases, builder_namespace
            )
            register_builder(builder_cls)
        else:
            builder_cls = cls
    return builder_cls


def has_builder(cls):
    return cls in builders


def get_builder(cls):
    return builders.get(cls)


def register_builder(builder_cls):
    builders[builder_cls._cls_to_build] = builder_cls


def isinstance_or_builder(obj, type_):
    if isinstance(type_, type):
        type_ = (type_,)
    type_ += tuple([get_or_make_builder_cls(t) for t in type_])
    return isinstance(obj, type_)


def issubclass_or_builder(cls, type_):
    if isinstance(type_, type):
        type_ = (type_,)
    type_ += tuple([get_or_make_builder_cls(t) for t in type_])
    return issubclass(cls, type_)
