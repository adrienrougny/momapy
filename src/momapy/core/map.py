"""Top-level Map class."""

import dataclasses

from momapy.core.elements import MapElement
from momapy.core.layout import Layout
from momapy.core.mapping import LayoutModelMapping
from momapy.core.model import Model


@dataclasses.dataclass(frozen=True, kw_only=True)
class Map(MapElement):
    """Class for maps"""

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

    def is_submap(self, other):
        """Return `true` if another given map is a submap of the `Map`, `false` otherwise"""
        if (
            self.model is None
            or self.layout is None
            or self.layout_model_mapping is None
        ):
            return False
        return (
            self.model.is_submodel(other.model)
            and self.layout.is_sublayout(other.layout)
            and self.layout_model_mapping.is_submapping(other.layout_model_mapping)
        )

    def get_mapping(
        self,
        map_element: "MapElement | tuple",
    ):
        """Return the layout elements mapped to the given model element"""
        return self.layout_model_mapping.get_mapping(map_element)
