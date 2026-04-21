"""Map classes for SBGN Process Description (PD) maps."""

import dataclasses

from momapy.builder import get_or_make_builder_cls
from momapy.sbgn.map import SBGNMap
from momapy.sbgn.pd.layout import SBGNPDLayout
from momapy.sbgn.pd.model import SBGNPDModel


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDMap(SBGNMap):
    """Class for SBGN-PD maps"""

    model: SBGNPDModel
    layout: SBGNPDLayout


SBGNPDModelBuilder = get_or_make_builder_cls(SBGNPDModel)
"""Class for SBGN-PD model builders"""
SBGNPDLayoutBuilder = get_or_make_builder_cls(SBGNPDLayout)
"""Class for SBGN-PD layout builders"""


def _sbgnpd_map_builder_new_model(self, *args, **kwargs):
    return SBGNPDModelBuilder(*args, **kwargs)


def _sbgnpd_map_builder_new_layout(self, *args, **kwargs):
    return SBGNPDLayoutBuilder(*args, **kwargs)


SBGNPDMapBuilder = get_or_make_builder_cls(
    SBGNPDMap,
    builder_namespace={
        "new_model": _sbgnpd_map_builder_new_model,
        "new_layout": _sbgnpd_map_builder_new_layout,
    },
)
"""Class for SBGN-PD map builders"""
