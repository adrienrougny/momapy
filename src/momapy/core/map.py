"""Top-level Map class."""

import dataclasses

import momapy.core.elements
import momapy.core.layout
import momapy.core.model
import momapy.core.mapping


@dataclasses.dataclass(frozen=True, kw_only=True)
class Map(momapy.core.elements.MapElement):
    """Class for maps"""

    model: momapy.core.model.Model | None = dataclasses.field(
        default=None, metadata={"description": "The model of the map"}
    )
    layout: momapy.core.layout.Layout | None = dataclasses.field(
        default=None, metadata={"description": "The layout of the map"}
    )
    layout_model_mapping: momapy.core.mapping.LayoutModelMapping | None = dataclasses.field(
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
        map_element: "momapy.core.elements.MapElement | tuple",
    ):
        """Return the layout elements mapped to the given model element"""
        return self.layout_model_mapping.get_mapping(map_element)
