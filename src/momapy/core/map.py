"""Top-level Map class."""

import dataclasses
import typing

from momapy.core.elements import MapElement
from momapy.core.layout import Layout
from momapy.core.mapping import LayoutModelMapping
from momapy.core.model import Model

if typing.TYPE_CHECKING:
    from momapy.core.elements import LayoutElement
    from momapy.core.elements import ModelElement


@dataclasses.dataclass(frozen=True, kw_only=True)
class Map(MapElement):
    """Class for maps."""

    model: Model | None = dataclasses.field(
        default=None, metadata={"description": "The model of the map"}
    )
    layout: Layout | None = dataclasses.field(
        default=None, metadata={"description": "The layout of the map"}
    )
    layout_model_mapping: LayoutModelMapping | None = dataclasses.field(
        default=None,
        metadata={"description": "The layout model mapping of the map"},
    )

    def is_submap(self, other: "Map") -> bool:
        """Return `True` if the `Map` is a submap of another given map, `False` otherwise.

        A complete map is never a submap of an incomplete one: if either `self`
        or `other` has a `None` model, layout, or layout-model mapping, this
        returns `False`.
        """
        if (
            self.model is None
            or self.layout is None
            or self.layout_model_mapping is None
            or other.model is None
            or other.layout is None
            or other.layout_model_mapping is None
        ):
            return False
        return (
            self.model.is_submodel(other.model)
            and self.layout.is_sublayout(other.layout)
            and self.layout_model_mapping.is_submapping(other.layout_model_mapping)
        )

    def get_mapping(
        self,
        map_element: "MapElement",
    ) -> "ModelElement | list[LayoutElement | frozenset[LayoutElement]] | None":
        """Return the model element or layout elements mapped to `map_element`.

        The lookup is bidirectional: a layout key (a singleton or frozenset)
        resolves to its model element, and a model element resolves to the
        list of layout keys mapped to it. Forwards to
        `layout_model_mapping.get_mapping`.

        Returns `None` when the map has no `layout_model_mapping` (for
        example a layout-less map such as one read from SBML).
        """
        if self.layout_model_mapping is None:
            return None
        return self.layout_model_mapping.get_mapping(map_element)
