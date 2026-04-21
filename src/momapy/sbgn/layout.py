"""Abstract base class for SBGN layouts."""

import dataclasses

import momapy.coloring
import momapy.drawing
from momapy.core.layout import Layout


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNLayout(Layout):
    """Base class for SBGN layouts.

    SBGN layouts define the visual representation of SBGN models,
    including the positions and styles of glyphs.

    Attributes:
        fill: Background fill color for the layout.

    Examples:
        ```python
        layout = SBGNLayout()
        ```
    """

    fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
