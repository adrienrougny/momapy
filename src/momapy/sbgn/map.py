"""Abstract base class for SBGN maps."""

import dataclasses

from momapy.core.map import Map
from momapy.sbgn.layout import SBGNLayout
from momapy.sbgn.model import SBGNModel


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNMap(Map):
    """Base class for SBGN maps.

    SBGN maps combine a model and its visual layout into a complete
    diagram representation.

    Attributes:
        model: The SBGN model containing semantic information.
        layout: The SBGN layout defining the visual representation.

    Examples:
        ```python
        model = SBGNModel()
        layout = SBGNLayout()
        map_ = SBGNMap(model=model, layout=layout)
        ```
    """

    model: SBGNModel
    layout: SBGNLayout
