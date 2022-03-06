from dataclasses import dataclass, field

from momapy.types import Map, ModelLayoutMapping
from momapy.demo.model import GraphModel
from momapy.demo.layout import GraphLayout

@dataclass(frozen=True)
class GraphMap(Map):
    model: GraphModel = None
    layout: GraphLayout = None
    model_layout_mapping: ModelLayoutMapping = field(default_factory=ModelLayoutMapping)
