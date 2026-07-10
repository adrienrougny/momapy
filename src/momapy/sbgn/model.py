"""Abstract base class for SBGN models."""

import dataclasses

from momapy.core.model import Model


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNModel(Model):
    """SBGN model."""

    pass
