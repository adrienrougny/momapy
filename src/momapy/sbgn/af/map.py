"""Map classes for SBGN Activity Flow (AF) maps."""

import dataclasses

from momapy.builder import get_or_make_builder_cls
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


SBGNAFModelBuilder = get_or_make_builder_cls(SBGNAFModel)
"""Builder class for SBGNAFModel."""
SBGNAFLayoutBuilder = get_or_make_builder_cls(SBGNAFLayout)
"""Builder class for SBGNAFLayout."""


def _sbgnaf_map_builder_new_model(self, *args, **kwargs):
    return SBGNAFModelBuilder(*args, **kwargs)


def _sbgnaf_map_builder_new_layout(self, *args, **kwargs):
    return SBGNAFLayoutBuilder(*args, **kwargs)


SBGNAFMapBuilder = get_or_make_builder_cls(
    SBGNAFMap,
    builder_namespace={
        "new_model": _sbgnaf_map_builder_new_model,
        "new_layout": _sbgnaf_map_builder_new_layout,
    },
)
"""Builder class for SBGNAFMap."""
