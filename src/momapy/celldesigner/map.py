"""Map classes for CellDesigner maps."""

import dataclasses

from momapy.celldesigner.layout import CellDesignerLayout
from momapy.celldesigner.model import CellDesignerModel
from momapy.core.map import Map


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerMap(Map):
    """Class for CellDesigner maps"""

    model: CellDesignerModel | None = None
    layout: CellDesignerLayout | None = None
