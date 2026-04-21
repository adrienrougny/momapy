"""Map classes for SBGN Process Description (PD) maps."""

import dataclasses

from momapy.sbgn.map import SBGNMap
from momapy.sbgn.pd.layout import SBGNPDLayout
from momapy.sbgn.pd.model import SBGNPDModel


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDMap(SBGNMap):
    """Class for SBGN-PD maps"""

    model: SBGNPDModel
    layout: SBGNPDLayout
