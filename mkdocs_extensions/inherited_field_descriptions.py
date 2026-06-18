"""Griffe extension: backfill overridden dataclass-field descriptions.

momapy's layout classes redeclare inherited ``Node`` / ``Arc`` fields (such as
``width``, ``height``, ``fill``, ``stroke_width``) only to change their default
value. A redeclared field shadows the base field and so loses the
``metadata={"description": ...}`` carried by the base, which leaves the rendered
field table blank for those fields.

This extension runs after ``griffe-fieldz`` and copies the description of an
inherited base field onto any subclass field that redeclares it without its own
description. The net effect: a field is documented once, where it is introduced
(via ``field(metadata={"description": ...})``), and every subclass that only
overrides its default inherits that description automatically -- no duplicated
metadata in the source.
"""

from __future__ import annotations

import dataclasses
import typing

from griffe import (
    Class,
    DocstringSectionAttributes,
    DocstringSectionParameters,
    Extension,
    ObjectNode,
    dynamic_import,
    get_logger,
)

if typing.TYPE_CHECKING:
    import ast

logger = get_logger("inherited_field_descriptions")


def _base_description_map(runtime_cls: type) -> dict[str, str]:
    """Map field name -> description from the dataclass bases of ``runtime_cls``.

    Walks the MRO from the most distant ancestor to the nearest base (excluding
    the class itself) so nearer bases win on conflicts.
    """
    descriptions: dict[str, str] = {}
    for base in reversed(runtime_cls.__mro__[1:]):
        if not dataclasses.is_dataclass(base):
            continue
        for field in dataclasses.fields(base):
            description = (field.metadata or {}).get("description")
            if description and description.strip():
                descriptions[field.name] = description.strip()
    return descriptions


class InheritedFieldDescriptions(Extension):
    """Fill blank dataclass-field descriptions from inherited base metadata."""

    def on_class_members(
        self,
        *,
        node: ast.AST | ObjectNode,
        cls: Class,
        **kwargs: typing.Any,
    ) -> None:
        """Backfill blank field descriptions for ``cls`` after griffe-fieldz."""
        if isinstance(node, ObjectNode):
            return
        try:
            runtime_cls = dynamic_import(cls.path)
        except ImportError:
            return
        if not dataclasses.is_dataclass(runtime_cls) or cls.docstring is None:
            return
        base_descriptions = _base_description_map(runtime_cls)
        if not base_descriptions:
            return
        for section in cls.docstring.parsed:
            if not isinstance(
                section, (DocstringSectionParameters, DocstringSectionAttributes)
            ):
                continue
            for item in section.value:
                if (
                    not item.description or not item.description.strip()
                ) and item.name in base_descriptions:
                    item.description = base_descriptions[item.name]
