"""SBGN-ML reading context.

Holds the SBGN-specific reading state (classified glyph/arc lists and id
lookups) layered on top of the shared `momapy.io._utils.ReadingContext`.
Internal: not part of the public API.
"""

import dataclasses

import lxml.objectify

from momapy.io._utils import ReadingContext


@dataclasses.dataclass
class SBGNMLReadingContext(ReadingContext):
    """SBGN-specific reading context."""

    sbgnml_compartments: list[lxml.objectify.ObjectifiedElement] = dataclasses.field(
        default_factory=list
    )
    sbgnml_entity_pools: list[lxml.objectify.ObjectifiedElement] = dataclasses.field(
        default_factory=list
    )
    sbgnml_logical_operators: list[lxml.objectify.ObjectifiedElement] = (
        dataclasses.field(default_factory=list)
    )
    sbgnml_stoichiometric_processes: list[lxml.objectify.ObjectifiedElement] = (
        dataclasses.field(default_factory=list)
    )
    sbgnml_phenotypes: list[lxml.objectify.ObjectifiedElement] = dataclasses.field(
        default_factory=list
    )
    sbgnml_submaps: list[lxml.objectify.ObjectifiedElement] = dataclasses.field(
        default_factory=list
    )
    sbgnml_activities: list[lxml.objectify.ObjectifiedElement] = dataclasses.field(
        default_factory=list
    )
    sbgnml_modulations: list[lxml.objectify.ObjectifiedElement] = dataclasses.field(
        default_factory=list
    )
    sbgnml_tags: list[lxml.objectify.ObjectifiedElement] = dataclasses.field(
        default_factory=list
    )
    sbgnml_glyph_id_to_sbgnml_arcs: dict[
        str, list[lxml.objectify.ObjectifiedElement]
    ] = dataclasses.field(default_factory=dict)
    empty_set_xml_ids: set[str] = dataclasses.field(default_factory=set)
