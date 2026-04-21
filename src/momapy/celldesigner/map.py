"""Map classes for CellDesigner maps."""

import dataclasses

from momapy.builder import get_or_make_builder_cls
from momapy.celldesigner.layout import CellDesignerLayout
from momapy.celldesigner.model import CellDesignerModel
from momapy.core.map import Map


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerMap(Map):
    """Class for CellDesigner maps"""

    model: CellDesignerModel | None = None
    layout: CellDesignerLayout | None = None


CellDesignerModelBuilder = get_or_make_builder_cls(CellDesignerModel)
CellDesignerLayoutBuilder = get_or_make_builder_cls(CellDesignerLayout)


def _celldesigner_map_builder_new_model(self, *args, **kwargs):
    return CellDesignerModelBuilder(*args, **kwargs)


def _celldesigner_map_builder_new_layout(self, *args, **kwargs):
    return CellDesignerLayoutBuilder(*args, **kwargs)


CellDesignerMapBuilder = get_or_make_builder_cls(
    CellDesignerMap,
    builder_namespace={
        "new_model": _celldesigner_map_builder_new_model,
        "new_layout": _celldesigner_map_builder_new_layout,
    },
)
