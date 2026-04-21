"""Abstract base class for SBGN models."""

import dataclasses

from momapy.core.model import Model


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNModel(Model):
    """Base class for SBGN models.

    SBGN models contain the semantic information represented in
    SBGN diagrams, including entities and their relationships.

    Examples:
        ```python
        model = SBGNModel()
        ```
    """

    pass
