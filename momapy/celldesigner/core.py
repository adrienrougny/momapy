import dataclasses
import typing
import enum

import momapy.core
import momapy.sbml.core


@dataclass(frozen=True)
class CellDesignerModel(sbml.core.Model):
    pass


@dataclass(frozen=True)
class CellDesignerModelElement(momapy.core.ModelElement):
    pass


@dataclass(frozen=True)
class CellDesignerMap(Map):
    model: typing.Optional[CellDesignerModel] = None
    layout: typing.Optional[momapy.core.Layout] = None
    model_layout_mapping: typing.Optional[momapy.core.ModelLayoutMapping] = None


@dataclass(frozen=True)
class ModificationResidue(CellDesignerModelElement):
    name: Optional[str]


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


@dataclass(frozen=True)
class CellDesignerSpeciesReference(CellDesignerModelElement):
    pass


@dataclass(frozen=True)
class ProteinReference(CellDesignerSpeciesReference):
    name: typing.Optional[str] = None
    modification_residues: frozenset[ModificationResidue] = dataclasses.field(
        default_factory=frozenset
    )


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
class GeneReference(CellDesignerSpeciesReference):
    regions: frozenset[
        ModificationSite,
        CodingRegion,
        RegulatoryRegion,
        TranscriptionStartingSiteL,
        TranscriptionStartingSiteR,
    ] = dataclasses.field(default_factory=frozenset)


@dataclass(frozen=True)
class RNAReference(CellDesignerSpeciesReference):
    regions: frozenset[
        ModificationSite, CodingRegion, ProteinBindingDomain
    ] = dataclasses.field(default_factory=frozenset)


@dataclass(frozen=True)
class AntisensRNAReference(CellDesignerSpeciesReference):
    regions: frozenset[
        ModificationSite, CodingRegion, ProteinBindingDomain
    ] = dataclasses.field(default_factory=frozenset)


@dataclass(frozen=True)
class Modification(CellDesignerModelElement):
    residue: typing.Optional[ModificationResidue] = None
    state: typing.Optional[ModificationState] = None


@dataclass(frozen=True)
class StructuralStateValue(Enum):
    EMPTY = "empty"
    OPEN = "open"
    CLOSED = "closed"


@dataclass(frozen=True)
class StructuralState(CellDesignerModelElement):
    value: Optional[Union[StructuralStateValue, str]] = None


@dataclass(frozen=True)
class Species(momapy.sbml.core.Species, CellDesignerModelElement):
    reference: Optional[CellDesignerSpeciesReference] = None
    active: Optional[bool] = None
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


@dataclass(frozen=True)
class Reactant(momapy.sbml.core.SpeciesReference, CellDesignerModelElement):
    pass


@dataclass(frozen=True)
class Product(momapy.sbml.core.SpeciesReference, CellDesignerModelElement):
    pass


@dataclass(frozen=True)
class Modulator(
    momapy.sbml.core.ModifierSpeciesReference, CellDesignerModelElement
):
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


@dataclass(frozen=True)
class Reaction(momapy.sbml.core.Reaction, CellDesignerModelElement):
    reactants: frozenset[Reactant] = dataclasses.field(
        default_factory=frozenset
    )
    products: frozenset[Product] = dataclasses.field(default_factory=frozenset)
    modulators: frozenset[Modulator] = dataclasses.field(
        default_factory=frozenset
    )


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
