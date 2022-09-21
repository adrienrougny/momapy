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

############MODIFICATION RESIDUE###################
@dataclass(frozen=True)
class Compartment(CellDesignerModelElement):
    name: Optional[str] = None

############MODIFICATION RESIDUE###################
@dataclass(frozen=True)
class ModificationResidue(CellDesignerModelElement):
    name: Optional[str]

############MODIFICATION STATE###################
@dataclass(frozen=True)
class ModificationState(Enum):
    PHOSPHORYLATED = "P"
    UBIQUINATED = "Ub"
    METHYLATED = "M"
    HYDROXYLATED = "OH"
    GLYCOSYLATED = "G"
    MYRISTOYLATED = "My"
    PALMITOYLATED = "Pa"
    PRENYLATED = "Pr"
    PROTONATED = "H"
    SULFATED = "S"
    DONT_CARE = "*"
    UNKNOWN = "?"

###########REGIONS###############################
@dataclass(frozen=True)
class Region(CellDesignerModelElement):
    name: Optional[str] = None
    active: bool = False

@dataclass(frozen=True)
class ModificationSite(Region):
    pass

@dataclass(frozen=True)
class CodingRegion(Region):
    pass

@dataclass(frozen=True)
class RegulatoryRegion(Region):
    pass

@dataclass(frozen=True)
class TranscriptionStartingSiteL(Region):
    pass

@dataclass(frozen=True)
class TranscriptionStartingSiteR(Region):
    pass

@dataclass(frozen=True)
class ProteinBindingDomain(Region):
    pass

############SPECIES REFERENCE###################
@dataclass(frozen=True)
class SpeciesReference(CellDesignerModelElement):
    pass

@dataclass(frozen=True)
class ProteinReference(SpeciesReference):
    name: Optional[str] = None
    modification_residues: frozenset[
        ModificationResidue] = field(default_factory=frozenset)

@dataclass(frozen=True)
class TruncatedProteinReference(ProteinReference):
    pass

@dataclass(frozen=True)
class ReceptorReference(ProteinReference):
    pass

@dataclass(frozen=True)
class IonChannelReference(ProteinReference):
    pass

@dataclass(frozen=True)
class GeneReference(SpeciesReference):
    regions: frozenset[
        ModificationSite,
        CodingRegion,
        RegulatoryRegion,
        TranscriptionStartingSiteL,
        TranscriptionStartingSiteR
    ] = field(default_factory=frozenset)

@dataclass(frozen=True)
class RNAReference(SpeciesReference):
    regions: frozenset[
        ModificationSite,
        CodingRegion,
        ProteinBindingDomain
    ] = field(default_factory=frozenset)

@dataclass(frozen=True)
class AntisensRNAReference(SpeciesReference):
    regions: frozenset[
        ModificationSite,
        CodingRegion,
        ProteinBindingDomain
    ] = field(default_factory=frozenset)

############MODIFICATION###################
@dataclass(frozen=True)
class Modification(CellDesignerModelElement):
    residue: Optional[ModificationResidue] = None
    state: Optional[ModificationState] = None

############STRUCTURAL STATE#####################
@dataclass(frozen=True)
class StructuralStateValue(Enum):
    EMPTY = "empty"
    OPEN = "open"
    CLOSED = "closed"

############STRUCTURAL STATE#####################
@dataclass(frozen=True)
class StructuralState(CellDesignerModelElement):
    value: Optional[Union[StructuralStateValue, str]] = None

############SPECIES###################
@dataclass(frozen=True)
class Species(CellDesignerModelElement):
    reference: Optional[SpeciesReference] = None
    active: Optional[bool] = None
    compartment: Optional[Compartment] = None
    homodimer: Optional[int] = 1

@dataclass(frozen=True)
class Protein(Species):
    reference: Optional[ProteinReference] = None
    modifications: frozenset[Modification] = field(default_factory=frozenset)
    structural_state: Optional[StructuralState] = None

    @property
    def name(self):
        return self.reference.name

@dataclass(frozen=True)
class GenericProtein(Protein):
    reference: Optional[GenericProteinReference] = None

@dataclass(frozen=True)
class TruncatedProtein(Protein):
    reference: Optional[TruncatedProteinReference] = None

@dataclass(frozen=True)
class Receptor(Protein):
    reference: Optional[ReceptorReference] = None

@dataclass(frozen=True)
class IonChannel(Protein):
    reference: Optional[IonChannelReference] = None

@dataclass(frozen=True)
class Gene(Species):
    reference: Optional[GeneReference] = None

    @property
    def name(self):
        return self.reference.name

@dataclass(frozen=True)
class RNA(Species):
    reference: Optional[RNAReference] = None

    @property
    def name(self):
        return self.reference.name

@dataclass(frozen=True)
class AntisensRNA(Species):
    reference: Optional[AntisensRNAReference] = None

    @property
    def name(self):
        return self.reference.name

@dataclass(frozen=True)
class Phenotype(Species):
    name: Optional[str] = None

@dataclass(frozen=True)
class Ion(Species):
    name: Optional[str] = None

@dataclass(frozen=True)
class SimpleMolecule(Species):
    name: Optional[str] = None

@dataclass(frozen=True)
class Drug(Species):
    name: Optional[str] = None

@dataclass(frozen=True)
class Unknown(Species):
    name: Optional[str] = None

@dataclass(frozen=True)
class Complex(Species):
    name: Optional[str] = None
    structural_state: Optional[StructuralState] = None
    subunits: frozenset[Species] = field(default_factory=frozenset)

@dataclass(frozen=True)
class Degraded(Species):
    name: Optional[str] = None

############CELLDESIGNER ROLES###################
@dataclass(frozen=True)
class CellDesignerRole(CellDesignerModelElement):
    element: Optional[CellDesignerModelElement] = None

@dataclass(frozen=True)
class FluxRole(CellDesignerRole):
    stoichiometry: Optional[int] = None

@dataclass(frozen=True)
class Reactant(FluxRole):
    pass

@dataclass(frozen=True)
class Product(FluxRole):
    pass

@dataclass(frozen=True)
class Modulator(CellDesignerRole):
    pass

@dataclass(frozen=True)
class Catalyzer(Modulator):
    pass

@dataclass(frozen=True)
class UnknownCatalyzer(Modulator):
    pass

@dataclass(frozen=True)
class Inhibitor(Modulator):
    pass

@dataclass(frozen=True)
class UnknownInhibitor(Modulator):
    pass

@dataclass(frozen=True)
class PhysicalStimulation(Modulator):
    pass

@dataclass(frozen=True)
class Trigger(Modulator):
    pass

############REACTIONS###################
@dataclass(frozen=True)
class Reaction(CellDesignerModelElement):
    reactants: frozenset[Reactant] = field(default_factory=frozenset)
    products: frozenset[Product] = field(default_factory=frozenset)
    modulators: frozenset[Modulator] = field(default_factory=frozenset)

@dataclass(frozen=True)
class StateTransition(Reaction):
    pass

@dataclass(frozen=True)
class KnownTransitionOmitted(Reaction):
    pass

@dataclass(frozen=True)
class UnknownTransition(Reaction):
    pass

@dataclass(frozen=True)
class Transcription(Reaction):
    pass

@dataclass(frozen=True)
class Translation(Reaction):
    pass

@dataclass(frozen=True)
class Transport(Reaction):
    pass

@dataclass(frozen=True)
class HeterodimerAssociation(Reaction):
    pass

@dataclass(frozen=True)
class Dissociation(Reaction):
    pass

@dataclass(frozen=True)
class Truncation(Reaction):
    pass
