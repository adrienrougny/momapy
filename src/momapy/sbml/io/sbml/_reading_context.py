"""SBML reading context.

Holds the SBML-specific reading state (source model element and id
lookups) layered on top of the shared `momapy.io._utils.ReadingContext`.
Internal: not part of the public API.
"""

import dataclasses
import typing

from momapy.io._utils import ReadingContext


@dataclasses.dataclass
class SBMLReadingContext(ReadingContext):
    """Reading context for the SBML reader.

    Extends the shared `ReadingContext` with the SBML-specific fields used
    to resolve cross-references while building the model.
    """

    sbml_model: typing.Any = dataclasses.field(
        default=None,
        metadata={"description": "Source SBML model lxml element being read."},
    )
    sbml_id_to_model_element: dict = dataclasses.field(default_factory=dict)
    """SBML XML id -> frozen model element, used to resolve compartment and
    species cross-references while building."""
    sbml_id_to_sbml_element: dict = dataclasses.field(default_factory=dict)
    """SBML XML id -> source SBML lxml element."""
