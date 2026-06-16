"""Abstract base class for SBGN layouts."""

import dataclasses

from momapy.coloring import Color
from momapy.coloring import white
from momapy.core.layout import Layout
from momapy.drawing import NoneValueType


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

    fill: NoneValueType | Color | None = white
