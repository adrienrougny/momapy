"""Map classes for SBGN Activity Flow (AF) maps."""

import dataclasses

from momapy.sbgn.af.layout import SBGNAFLayout
from momapy.sbgn.af.model import SBGNAFModel
from momapy.sbgn.map import SBGNMap


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNAFMap(SBGNMap):
    """SBGN-AF map.

    Represents a complete SBGN Activity Flow map with model and layout.

    Attributes:
        model: The SBGN-AF model.
        layout: The visual layout of the map.
    """

    model: SBGNAFModel | None = None
    layout: SBGNAFLayout | None = None
