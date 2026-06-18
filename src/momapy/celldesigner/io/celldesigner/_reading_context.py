"""CellDesigner reading context.

Holds the CellDesigner-specific reading state (classified element lists, id
lookups, canvas dimensions, degraded-element tracking) layered on top of the
shared `momapy.io._utils.ReadingContext`. Internal: not part of the public API.
"""

import dataclasses

import lxml.objectify

from momapy.io._utils import ReadingContext


@dataclasses.dataclass
class CellDesignerReadingContext(ReadingContext):
    """CellDesigner-specific reading context."""

    cd_complex_alias_id_to_cd_included_species_ids: dict[str, list[str]] = (
        dataclasses.field(default_factory=dict)
    )
    cd_compartment_aliases: list[lxml.objectify.ObjectifiedElement] = dataclasses.field(
        default_factory=list
    )
    cd_compartments: list[lxml.objectify.ObjectifiedElement] = dataclasses.field(
        default_factory=list
    )
    cd_species_templates: list[lxml.objectify.ObjectifiedElement] = dataclasses.field(
        default_factory=list
    )
    cd_species_aliases: list[lxml.objectify.ObjectifiedElement] = dataclasses.field(
        default_factory=list
    )
    cd_reactions: list[lxml.objectify.ObjectifiedElement] = dataclasses.field(
        default_factory=list
    )
    cd_modulations: list[lxml.objectify.ObjectifiedElement] = dataclasses.field(
        default_factory=list
    )
    real_model_source_ids: set[str] = dataclasses.field(default_factory=set)
    real_layout_source_ids: set[str] = dataclasses.field(default_factory=set)
    canvas_width: float = dataclasses.field(
        default=0.0,
        metadata={"description": "Width of the CellDesigner canvas."},
    )
    canvas_height: float = dataclasses.field(
        default=0.0,
        metadata={"description": "Height of the CellDesigner canvas."},
    )
    cd_degraded_alias_ids: set[str] = dataclasses.field(default_factory=set)
    cd_degraded_species_ids: set[str] = dataclasses.field(default_factory=set)
