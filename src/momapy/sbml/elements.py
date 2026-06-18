"""Abstract base classes for SBML model elements."""

import dataclasses

from momapy.core.elements import ModelElement


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBMLModelElement(ModelElement):
    """Abstract base class for all SBML elements.

    SBMLModelElement provides common attributes shared by all SBML components.
    """

    name: str | None = dataclasses.field(
        default=None,
        metadata={"description": "Human-readable name of the element."},
    )
    sbo_term: str | None = dataclasses.field(
        default=None,
        metadata={
            "description": "Optional SBO term identifier for semantic annotation."
        },
    )
    metaid: str | None = dataclasses.field(
        default=None,
        compare=False,
        hash=False,
        metadata={"description": "Optional metadata identifier for RDF annotations."},
    )
