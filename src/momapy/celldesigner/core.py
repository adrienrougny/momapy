"""Core classes for CellDesigner maps.

This module provides classes for representing CellDesigner pathway diagrams,
including model elements (species, reactions, modifications) and layout elements
(nodes, arcs, compartments). CellDesigner is a tool for visualizing biochemical
pathways and networks.

Examples:
    ```python
    from momapy.celldesigner.core import CellDesignerModel, CellDesignerLayout
    model = CellDesignerModel(name="MAPK_cascade")
    layout = CellDesignerLayout()
    ```
"""

import dataclasses

import momapy.core
import momapy.core.builders
import momapy.core.elements
import momapy.core.layout
import momapy.core.map
import momapy.geometry
import momapy.coloring
import momapy.drawing
import momapy.builder
import momapy.meta.shapes
import momapy.meta.nodes
import momapy.meta.arcs
import momapy.sbml.core
import momapy.sbgn.core
import momapy.sbgn.pd

from momapy.core.elements import ModelElement
from momapy.core.layout import SingleHeadedArc, DoubleHeadedArc, Layout
from momapy.core.map import Map
from momapy.sbgn.core import SBGNNode, _SimpleMixin, _MultiMixin, _SBGNMixin


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

    arrowhead_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    arrowhead_stroke_width: float | None = 1.0
    path_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )
    path_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    path_stroke_width: float | None = 1.0

    def own_drawing_elements(self):
        drawing_elements = momapy.builder.super_or_builder(
            CellDesignerSingleHeadedArc, self
        ).own_drawing_elements()
        done_bases = []
        for base in type(self).__mro__:
            if (
                momapy.builder.issubclass_or_builder(base, _SBGNMixin)
                and base is not type(self)
                and not any([issubclass(done_base, base) for done_base in done_bases])
            ):
                drawing_elements += getattr(base, "_mixin_drawing_elements")(self)
                done_bases.append(base)
        return drawing_elements


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerDoubleHeadedArc(DoubleHeadedArc):
    """Base class for CellDesigner double-headed arcs"""

    path_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )
    path_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    path_stroke_width: float | None = 1.0

    def own_drawing_elements(self):
        drawing_elements = momapy.builder.super_or_builder(
            CellDesignerDoubleHeadedArc, self
        ).own_drawing_elements()
        done_bases = []
        for base in type(self).__mro__:
            if (
                momapy.builder.issubclass_or_builder(base, _SBGNMixin)
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


# Backward-compat re-exports: classes moved to model.py and layout.py remain
# accessible as `momapy.celldesigner.core.X` through these star-imports. The
# imports are placed at the bottom so `model.py` and `layout.py` can import
# the shared bases defined above.
from momapy.celldesigner.model import *  # noqa: E402,F401,F403
from momapy.celldesigner.layout import *  # noqa: E402,F401,F403

from momapy.celldesigner.model import CellDesignerModel  # noqa: E402
from momapy.celldesigner.layout import (  # noqa: E402,F401
    _ACTIVE_XSEP,
    _ACTIVE_YSEP,
)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerLayout(Layout):
    """Class for CellDesigner layouts"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerMap(Map):
    """Class for CellDesigner maps"""

    model: CellDesignerModel | None = None
    layout: CellDesignerLayout | None = None


CellDesignerModelBuilder = momapy.builder.get_or_make_builder_cls(CellDesignerModel)
CellDesignerLayoutBuilder = momapy.builder.get_or_make_builder_cls(CellDesignerLayout)


def _celldesigner_map_builder_new_model(self, *args, **kwargs):
    return CellDesignerModelBuilder(*args, **kwargs)


def _celldesigner_map_builder_new_layout(self, *args, **kwargs):
    return CellDesignerLayoutBuilder(*args, **kwargs)


CellDesignerMapBuilder = momapy.builder.get_or_make_builder_cls(
    CellDesignerMap,
    builder_namespace={
        "new_model": _celldesigner_map_builder_new_model,
        "new_layout": _celldesigner_map_builder_new_layout,
    },
)
