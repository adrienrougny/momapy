"""Abstract base classes for SBML model elements."""

import dataclasses

from momapy.core.elements import ModelElement


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBMLModelElement(ModelElement):
    """Abstract base class for all SBML elements.

    SBMLModelElement provides common attributes shared by all SBML components.

    Attributes:
        name: Human-readable name of the element.
        sbo_term: Optional SBO term identifier for semantic annotation.
        metaid: Optional metadata identifier for RDF annotations.
    """

    name: str | None = None
    sbo_term: str | None = None
    metaid: str | None = dataclasses.field(default=None, compare=False, hash=False)
