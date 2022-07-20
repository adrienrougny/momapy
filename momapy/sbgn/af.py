from enum import Enum
from dataclasses import dataclass, field
from typing import TypeVar, Union, Optional

from momapy.sbgn.core import SBGNModelElement, SBGNModel, SBGNMap
from momapy.builder import get_or_make_builder_cls

############UNIT OF INFORMATION###################
class UnifOfInformationType(Enum):
    MACROMOLECULE = "macromolecule"

@dataclass(frozen=True)
class UnitOfInformation(SBGNModelElement):
    label: Optional[str] = None
    type_: Optional[UnifOfInformationType] = None

############COMPARTMENT###################
@dataclass(frozen=True)
class Compartment(SBGNModelElement):
    label: Optional[str] = None

############LOGICAL OPERATORS###################
TLogicalOperatorInput = TypeVar("TLogicalOperatorInput", "BiologicalActivity", "LogicalOperator")

@dataclass(frozen=True)
class LogicalOperator(SBGNModelElement):
    inputs: frozenset[TLogicalOperatorInput] = field(default_factory=frozenset)

@dataclass(frozen=True)
class OrOperator(LogicalOperator):
    pass

@dataclass(frozen=True)
class AndOperator(LogicalOperator):
    pass

@dataclass(frozen=True)
class NotOperator(LogicalOperator):
    pass

############ACTIVITIES###################
@dataclass(frozen=True)
class Activity(SBGNModelElement):
    label: Optional[str] = None

@dataclass(frozen=True)
class BiologicalActivity(Activity):
    units_of_information: frozenset[UnitOfInformation] = field(default_factory=frozenset)

@dataclass(frozen=True)
class Phenotype(Activity):
    pass

############INFLUENCES###################
@dataclass(frozen=True)
class Influence(SBGNModelElement):
    source: Optional[Union[BiologicalActivity, LogicalOperator]] = None
    target: Optional[Activity] = None

@dataclass(frozen=True)
class UnknownInfluence(Influence):
    pass

@dataclass(frozen=True)
class PositiveInfluence(Influence):
    pass

@dataclass(frozen=True)
class NegativeInfluence(Influence):
    pass

@dataclass(frozen=True)
class NecessaryStimulation(Influence):
    pass

############SUBMAP###################
@dataclass(frozen=True)
class Tag(SBGNModelElement):
    label: Optional[str] = None
    refers_to: Optional[Union[Activity, Compartment]] = None

@dataclass(frozen=True)
class Submap(SBGNModelElement):
    label: Optional[str] = None
    tags: frozenset[Tag] = field(default_factory=frozenset)

############MODELS###################
@dataclass(frozen=True)
class SBGNAFModel(SBGNModel):
    activities: frozenset[Activity] = field(default_factory=frozenset)
    compartments: frozenset[Compartment] = field(default_factory=frozenset)
    influences: frozenset[Influence] = field(default_factory=frozenset)
    logical_operators: frozenset[LogicalOperator] = field(default_factory=frozenset)
    submaps: frozenset[Submap] = field(default_factory=frozenset)

############MAP###################
@dataclass(frozen=True)
class SBGNAFMap(SBGNMap):
    model: Optional[SBGNAFModel] = None

############BUILDERS###################
SBGNAFModelBuilder = get_or_make_builder_cls(SBGNAFModel)

def sbgnaf_map_builder_new_model(self, *args, **kwargs):
    return SBGNAFModelBuilder(*args, **kwargs)

def sbgnaf_map_builder_new_layout(self, *args, **kwargs):
    return LayoutBuilder(*args, **kwargs)

def sbgnaf_map_builder_new_model_layout_mapping(self, *args, **kwargs):
    return ModelLayoutMappingBuilder(*args, **kwargs)

SBGNAFMapBuilder = get_or_make_builder_cls(
    SBGNAFMap,
    builder_namespace={
        "new_model": sbgnaf_map_builder_new_model,
        "new_layout": sbgnaf_map_builder_new_layout,
        "new_model_layout_mapping": sbgnaf_map_builder_new_model_layout_mapping
    }
)
