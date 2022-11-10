import dataclasses
import typing
import enum

import momapy.core
import momapy.sbml.core


@dataclasses.dataclass(frozen=True)
class CellDesignerModelElement(momapy.core.ModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class ModificationResidue(CellDesignerModelElement):
    name: typing.Optional[str] = None


class ModificationState(enum.Enum):
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


@dataclasses.dataclass(frozen=True)
class Region(CellDesignerModelElement):
    name: typing.Optional[str] = None
    active: bool = False


@dataclasses.dataclass(frozen=True)
class ModificationSite(Region):
    pass


@dataclasses.dataclass(frozen=True)
class CodingRegion(Region):
    pass


@dataclasses.dataclass(frozen=True)
class RegulatoryRegion(Region):
    pass


@dataclasses.dataclass(frozen=True)
class TranscriptionStartingSiteL(Region):
    pass


@dataclasses.dataclass(frozen=True)
class TranscriptionStartingSiteR(Region):
    pass


@dataclasses.dataclass(frozen=True)
class ProteinBindingDomain(Region):
    pass


@dataclasses.dataclass(frozen=True)
class CellDesignerSpeciesReference(CellDesignerModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class ProteinReference(CellDesignerSpeciesReference):
    name: typing.Optional[str] = None
    modification_residues: frozenset[ModificationResidue] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class GenericProteinReference(ProteinReference):
    pass


@dataclasses.dataclass(frozen=True)
class TruncatedProteinReference(ProteinReference):
    pass


@dataclasses.dataclass(frozen=True)
class ReceptorReference(ProteinReference):
    pass


@dataclasses.dataclass(frozen=True)
class IonChannelReference(ProteinReference):
    pass


@dataclasses.dataclass(frozen=True)
class GeneReference(CellDesignerSpeciesReference):
    regions: frozenset[
        ModificationSite,
        CodingRegion,
        RegulatoryRegion,
        TranscriptionStartingSiteL,
        TranscriptionStartingSiteR,
    ] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class RNAReference(CellDesignerSpeciesReference):
    regions: frozenset[
        ModificationSite, CodingRegion, ProteinBindingDomain
    ] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class AntisensRNAReference(CellDesignerSpeciesReference):
    regions: frozenset[
        ModificationSite, CodingRegion, ProteinBindingDomain
    ] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class Modification(CellDesignerModelElement):
    residue: typing.Optional[ModificationResidue] = None
    state: typing.Optional[ModificationState] = None


@dataclasses.dataclass(frozen=True)
class StructuralStateValue(enum.Enum):
    EMPTY = "empty"
    OPEN = "open"
    CLOSED = "closed"


@dataclasses.dataclass(frozen=True)
class StructuralState(CellDesignerModelElement):
    value: typing.Optional[typing.Union[StructuralStateValue, str]] = None


@dataclasses.dataclass(frozen=True)
class Species(momapy.sbml.core.Species, CellDesignerModelElement):
    reference: typing.Optional[CellDesignerSpeciesReference] = None
    active: typing.Optional[bool] = None
    homodimer: typing.Optional[int] = 1


@dataclasses.dataclass(frozen=True)
class Protein(Species):
    reference: typing.Optional[ProteinReference] = None
    modifications: frozenset[Modification] = dataclasses.field(
        default_factory=frozenset
    )
    structural_states: frozenset[StructuralState] = dataclasses.field(
        default_factory=frozenset
    )

    @property
    def name(self):
        return self.reference.name


@dataclasses.dataclass(frozen=True)
class GenericProtein(Protein):
    reference: typing.Optional[GenericProteinReference] = None


@dataclasses.dataclass(frozen=True)
class TruncatedProtein(Protein):
    reference: typing.Optional[TruncatedProteinReference] = None


@dataclasses.dataclass(frozen=True)
class Receptor(Protein):
    reference: typing.Optional[ReceptorReference] = None


@dataclasses.dataclass(frozen=True)
class IonChannel(Protein):
    reference: typing.Optional[IonChannelReference] = None


@dataclasses.dataclass(frozen=True)
class Gene(Species):
    reference: typing.Optional[GeneReference] = None

    @property
    def name(self):
        return self.reference.name


@dataclasses.dataclass(frozen=True)
class RNA(Species):
    reference: typing.Optional[RNAReference] = None

    @property
    def name(self):
        return self.reference.name


@dataclasses.dataclass(frozen=True)
class AntisensRNA(Species):
    reference: typing.Optional[AntisensRNAReference] = None

    @property
    def name(self):
        return self.reference.name


@dataclasses.dataclass(frozen=True)
class Phenotype(Species):
    name: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class Ion(Species):
    name: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class SimpleMolecule(Species):
    name: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class Drug(Species):
    name: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class Unknown(Species):
    name: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class Complex(Species):
    name: typing.Optional[str] = None
    structural_state: typing.Optional[StructuralState] = None
    subunits: frozenset[Species] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class Degraded(Species):
    name: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class Reactant(momapy.sbml.core.SpeciesReference, CellDesignerModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class Product(momapy.sbml.core.SpeciesReference, CellDesignerModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class Modulator(
    momapy.sbml.core.ModifierSpeciesReference, CellDesignerModelElement
):
    pass


@dataclasses.dataclass(frozen=True)
class Catalyzer(Modulator):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownCatalyzer(Modulator):
    pass


@dataclasses.dataclass(frozen=True)
class Inhibitor(Modulator):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownInhibitor(Modulator):
    pass


@dataclasses.dataclass(frozen=True)
class PhysicalStimulation(Modulator):
    pass


@dataclasses.dataclass(frozen=True)
class Trigger(Modulator):
    pass


@dataclasses.dataclass(frozen=True)
class Reaction(momapy.sbml.core.Reaction, CellDesignerModelElement):
    reactants: frozenset[Reactant] = dataclasses.field(
        default_factory=frozenset
    )
    products: frozenset[Product] = dataclasses.field(default_factory=frozenset)
    modulators: frozenset[Modulator] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class StateTransition(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class KnownTransitionOmitted(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownTransition(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class Transcription(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class Translation(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class Transport(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class HeterodimerAssociation(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class Dissociation(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class Truncation(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class CellDesignerModel(momapy.sbml.core.Model):
    species_references: frozenset[
        CellDesignerSpeciesReference
    ] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class CellDesignerMap(momapy.core.Map):
    model: typing.Optional[CellDesignerModel] = None
    layout: typing.Optional[momapy.core.MapLayout] = None
    model_layout_mapping: typing.Optional[momapy.core.ModelLayoutMapping] = None


CellDesignerModelBuilder = momapy.builder.get_or_make_builder_cls(
    CellDesignerModel
)


def _celldesigner_map_builder_new_model(self, *args, **kwargs):
    return CellDesignerModelBuilder(*args, **kwargs)


def _celldesigner_map_builder_new_layout(self, *args, **kwargs):
    return momapy.core.MapLayoutBuilder(*args, **kwargs)


def _celldesigner_map_builder_new_model_layout_mapping(self, *args, **kwargs):
    return momapy.core.ModelLayoutMappingBuilder(*args, **kwargs)


CellDesignerMapBuilder = momapy.builder.get_or_make_builder_cls(
    CellDesignerMap,
    builder_namespace={
        "new_model": _celldesigner_map_builder_new_model,
        "new_layout": _celldesigner_map_builder_new_layout,
        "new_model_layout_mapping": _celldesigner_map_builder_new_model_layout_mapping,
    },
)
