"""Map class for SBML maps."""

import dataclasses

from momapy.core.map import Map
from momapy.sbml.model import SBMLModel


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBMLMap(Map):
    """Class for SBML maps.

    SBML support is model only: an `SBMLMap` carries an `SBMLModel` and no
    layout. The inherited `layout` and `layout_model_mapping` fields are
    always `None`.
    """

    model: SBMLModel | None = None
