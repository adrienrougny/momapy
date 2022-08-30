from dataclasses import dataclass, field
from typing import TypeVar, Union, Optional
from enum import Enum

from momapy.core import Map, ModelElement, Model, Layout, ModelLayoutMapping

############Annotation###################
@dataclass(frozen=True)
class Annotation(ModelElement):
    pass

############CellDesigner MODEL ELEMENT###################
@dataclass(frozen=True)
class CellDesignerModelElement(ModelElement):
    annotations: frozenset[Annotation] = field(default_factory=frozenset)

############MODEL###################
@dataclass(frozen=True)
class CellDesignerModel(Model):
    pass

############MAP###################
@dataclass(frozen=True)
class CellDesignerMap(Map):
    model: Optional[CellDesignerModel] = None
    layout: Optional[Layout] = None
    model_layout_mapping: Optional[ModelLayoutMapping] = None

############PROTEIN TYPE###################
class ProteinType(Enum):
    GENERIC = "Generic"
    TRUNCATED = "Truncated"
    RECEPTOR = "Receptor"

############MODIFICATION RESIDUE###################
@dataclass(frozen=True)
class ModificationResidue(CellDesignerModelElement):
    name: Optional[str]

############MODIFICATION STATE###################
@dataclass(frozen=True)
class ModificationState(Enum):
    PHOSPHORYLATED = "phosphorylated"

############MODIFICATION RESIDUE###################
@dataclass(frozen=True)
class Modification(CellDesignerModelElement):
    residue: Optional[ModificationResidue] = None
    state: Optional[ModificationState] = None

############SPECIES REFERENCE###################
@dataclass(frozen=True)
class SpeciesReference(CellDesignerModelElement):
    refid: Optional[Union[str, UUID]] = None

@dataclass(frozen=True)
class ProteinReference(SpeciesReference):
    type: Optional[ProteinType] = None
    name: Optional[str] = None
    modification_residues: frozenset[ModificationResidue] = field(default_factory=frozenset)

############SPECIES###################
@dataclass(frozen=True)
class Species(CellDesignerModelElement):
    name: Optional[str] = None
    reference: Optional[SpeciesReference] = None
    active: Optional[bool] = None

@dataclass(frozen=True)
class Protein(Species):
    reference: Optional[ProteinReference] = None
    modifications: frozenset[Modification] = field(default_factory=frozenset)
