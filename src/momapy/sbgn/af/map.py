"""Map classes for SBGN Activity Flow (AF) maps."""

import dataclasses

from momapy.sbgn.af.layout import SBGNAFLayout
from momapy.sbgn.af.model import SBGNAFModel
from momapy.sbgn.map import SBGNMap


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNAFMap(SBGNMap):
    """Class for SBGN-AF maps."""

    model: SBGNAFModel | None = None
    layout: SBGNAFLayout | None = None
