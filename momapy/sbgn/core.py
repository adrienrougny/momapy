from dataclasses import dataclass, field
from typing import TypeVar, Union, Optional

from momapy.core import Map, ModelElement, Model, Layout, ModelLayoutMapping

############Annotation###################
@dataclass(frozen=True)
class Annotation(ModelElement):
    pass

############SBGN MODEL ELEMENT###################
@dataclass(frozen=True)
class SBGNModelElement(ModelElement):
    annotations: frozenset[Annotation] = field(default_factory=frozenset)

############SBGN ROLES###################
@dataclass(frozen=True)
class SBGNRole(SBGNModelElement):
    element: Optional[SBGNModelElement] = None

############MODEL###################
@dataclass(frozen=True)
class SBGNModel(Model):
    pass

############MAP###################
@dataclass(frozen=True)
class SBGNMap(Map):
    model: Optional[SBGNModel] = None
    layout: Optional[Layout] = None
    model_layout_mapping: Optional[ModelLayoutMapping] = None
