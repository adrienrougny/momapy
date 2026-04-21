"""Core classes for CellDesigner maps.

This module provides classes for representing CellDesigner pathway diagrams,
including model elements (species, reactions, modifications) and layout elements
(nodes, arcs, compartments). CellDesigner is a tool for visualizing biochemical
pathways and networks.

Examples:
    ```python
    from momapy.celldesigner.model import CellDesignerModel
    from momapy.celldesigner.layout import CellDesignerLayout
    model = CellDesignerModel(name="MAPK_cascade")
    layout = CellDesignerLayout()
    ```
"""

import dataclasses

from momapy.builder import (
    issubclass_or_builder,
    super_or_builder,
)
from momapy.coloring import Color, black
from momapy.core.elements import ModelElement
from momapy.core.layout import DoubleHeadedArc, SingleHeadedArc
from momapy.drawing import NoneValue, NoneValueType
from momapy.sbgn.core import SBGNNode, _MultiMixin, _SBGNMixin, _SimpleMixin


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerModelElement(ModelElement):
    """Base class for CellDesigner model elements"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerNode(SBGNNode):
    """Base class for CellDesigner nodes"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerSingleHeadedArc(SingleHeadedArc):
    """Base class for CellDesigner single-headed arcs"""

    arrowhead_stroke: NoneValueType | Color | None = black
    arrowhead_stroke_width: float | None = 1.0
    path_fill: NoneValueType | Color | None = NoneValue
    path_stroke: NoneValueType | Color | None = black
    path_stroke_width: float | None = 1.0

    def own_drawing_elements(self):
        drawing_elements = super_or_builder(
            CellDesignerSingleHeadedArc, self
        ).own_drawing_elements()
        done_bases = []
        for base in type(self).__mro__:
            if (
                issubclass_or_builder(base, _SBGNMixin)
                and base is not type(self)
                and not any([issubclass(done_base, base) for done_base in done_bases])
            ):
                drawing_elements += getattr(base, "_mixin_drawing_elements")(self)
                done_bases.append(base)
        return drawing_elements


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerDoubleHeadedArc(DoubleHeadedArc):
    """Base class for CellDesigner double-headed arcs"""

    path_fill: NoneValueType | Color | None = NoneValue
    path_stroke: NoneValueType | Color | None = black
    path_stroke_width: float | None = 1.0

    def own_drawing_elements(self):
        drawing_elements = super_or_builder(
            CellDesignerDoubleHeadedArc, self
        ).own_drawing_elements()
        done_bases = []
        for base in type(self).__mro__:
            if (
                issubclass_or_builder(base, _SBGNMixin)
                and base is not type(self)
                and not any([issubclass(done_base, base) for done_base in done_bases])
            ):
                drawing_elements += getattr(base, "_mixin_drawing_elements")(self)
                done_bases.append(base)
        return drawing_elements


@dataclasses.dataclass(frozen=True, kw_only=True)
class _SimpleNodeMixin(_SimpleMixin):
    @classmethod
    def _mixin_drawing_elements(cls, obj):
        return _SimpleMixin._mixin_drawing_elements(obj)


@dataclasses.dataclass(frozen=True, kw_only=True)
class _MultiNodeMixin(_MultiMixin):
    n: int = 1

    @property
    def _n(self):
        return self.n

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        return _MultiMixin._mixin_drawing_elements(obj)
