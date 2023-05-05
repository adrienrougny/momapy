import dataclasses
import typing
import enum

import momapy.core
import momapy.sbml.core
import momapy.sbgn.core


@dataclasses.dataclass(frozen=True)
class CellDesignerModelElement(momapy.core.ModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class ModificationResidue(CellDesignerModelElement):
    name: typing.Optional[str] = None


class ModificationState(enum.Enum):
    PHOSPHORYLATED = "P"
    UBIQUITINATED = "Ub"
    METHYLATED = "M"
    HYDROXYLATED = "OH"
    GLYCOSYLATED = "G"
    MYRISTOYLATED = "My"
    PALMITOYLATED = "Pa"
    PRENYLATED = "Pr"
    PROTONATED = "H"
    SULFATED = "S"
    DON_T_CARE = "*"
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
class Compartment(momapy.sbml.core.Compartment, CellDesignerModelElement):
    pass


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
    structural_states: frozenset[StructuralState] = dataclasses.field(
        default_factory=frozenset
    )
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
class BooleanLogicGate(CellDesignerModelElement):
    inputs: frozenset[Species] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class AndGate(BooleanLogicGate):
    pass


@dataclasses.dataclass(frozen=True)
class OrGate(BooleanLogicGate):
    pass


@dataclasses.dataclass(frozen=True)
class NotGate(BooleanLogicGate):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownGate(BooleanLogicGate):
    pass


@dataclasses.dataclass(frozen=True)
class Modifier(
    momapy.sbml.core.ModifierSpeciesReference, CellDesignerModelElement
):
    species: typing.Optional[typing.Union[Species, BooleanLogicGate]] = None


@dataclasses.dataclass(frozen=True)
class Modulator(Modifier):
    pass


@dataclasses.dataclass(frozen=True)
class Inhibitor(Modulator):
    pass


@dataclasses.dataclass(frozen=True)
class PhysicalStimulator(Modulator):
    pass


@dataclasses.dataclass(frozen=True)
class Catalyzer(PhysicalStimulator):
    pass


@dataclasses.dataclass(frozen=True)
class Trigger(Modulator):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownCatalyzer(Modifier):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownInhibitor(Modifier):
    pass


@dataclasses.dataclass(frozen=True)
class Reaction(momapy.sbml.core.Reaction, CellDesignerModelElement):
    reactants: frozenset[Reactant] = dataclasses.field(
        default_factory=frozenset
    )
    products: frozenset[Product] = dataclasses.field(default_factory=frozenset)
    modifiers: frozenset[Modifier] = dataclasses.field(
        default_factory=frozenset
    )
    ungrouped_modifiers: frozenset[Modifier] = dataclasses.field(
        default_factory=frozenset, compare=False, hash=False
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
class ModulationReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class InhibitionReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class PhysicalStimulationReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class CatalysisReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class TriggeringReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownCatalysisReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownInhibitionReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class BooleanLogicGateReaction(Reaction):
    pass


@dataclasses.dataclass(frozen=True)
class ReactionModification(CellDesignerModelElement):
    source: typing.Optional[typing.Union[Species, BooleanLogicGate]] = None
    target: typing.Optional[Species] = None


@dataclasses.dataclass(frozen=True)
class Modulation(ReactionModification):
    pass


@dataclasses.dataclass(frozen=True)
class Inhibition(Modulation):
    pass


@dataclasses.dataclass(frozen=True)
class PhysicalStimulation(Modulation):
    pass


@dataclasses.dataclass(frozen=True)
class Catalysis(PhysicalStimulation):
    pass


@dataclasses.dataclass(frozen=True)
class Triggering(Modulation):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownCatalysis(ReactionModification):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownInhibition(ReactionModification):
    pass


@dataclasses.dataclass(frozen=True)
class _CellDesignerShapeBase(momapy.sbgn.core._SBGNShapeBase):
    pass


@dataclasses.dataclass(frozen=True)
class _CellDesignerSimpleMixin(momapy.sbgn.core._SimpleMixin):
    pass


@dataclasses.dataclass(frozen=True)
class _CellDesignerMultiMixin(momapy.sbgn.core._MultiMixin):
    n: int = 1

    @property
    def _n(self):
        return self.n


@dataclasses.dataclass(frozen=True)
class GenericProteinLayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[
        type
    ] = momapy.shapes.RectangleWithRoundedCorners
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "rounded_corners": "rounded_corners"
    }
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True)
class IonChannelLayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[
        type
    ] = (
        momapy.shapes.RectangleWithRoundedCornersAlongsideRectangleWithRoundedCorners
    )
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "rounded_corners": "rounded_corners",
        "right_rectangle_width": "right_rectangle_width",
    }
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0
    right_rectangle_width: float = 20.0
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True)
class ComplexLayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.RectangleWithCutCorners
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "cut_corners": "cut_corners"
    }
    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 6.0
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 2.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue

    def label_center(self):
        return self._make_subunit(self.n - 1).south() - (0, 12)


@dataclasses.dataclass(frozen=True)
class SimpleMoleculeLayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Ellipse
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 60.0
    height: float = 30.0
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True)
class IonLayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Ellipse
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 30.0
    height: float = 30.0
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True)
class UnknownLayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Ellipse
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 30.0
    height: float = 30.0
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.drawing.NoneValue
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.gray
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True)
class DegradedLayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.CircleWithDiagonalBar
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 30.0
    height: float = 30.0
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True)
class GeneLayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Rectangle
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 60.0
    height: float = 30.0
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Hexagon
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "top_left_angle": "angle",
        "top_right_angle": "angle",
        "bottom_left_angle": "angle",
        "bottom_right_angle": "angle",
    }
    width: float = 60.0
    height: float = 30.0
    angle: float = 45.0
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class RNALayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Parallelogram
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "angle": "angle",
    }
    width: float = 60.0
    height: float = 30.0
    angle: float = 45.0
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class AntisensRNALayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.InvertedParallelogram
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "angle": "angle",
    }
    width: float = 60.0
    height: float = 30.0
    angle: float = 45.0
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class TruncatedProteinLayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[
        type
    ] = momapy.shapes.TruncatedRectangleWithLeftRoundedCorners
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "rounded_corners": "rounded_corners",
        "vertical_truncation": "vertical_truncation",
        "horizontal_truncation": "horizontal_truncation",
    }
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 8.0
    vertical_truncation: float = 0.40
    horizontal_truncation: float = 0.20
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReceptorLayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.FoxHead
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "vertical_truncation": "vertical_truncation",
    }
    width: float = 60.0
    height: float = 30.0
    vertical_truncation: float = 0.20
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class DrugLayout(_CellDesignerMultiMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[
        type
    ] = momapy.shapes.StadiumWithEllipsesWithInsideStadiumWithEllipses
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "horizontal_proportion": "horizontal_proportion",
        "sep": "sep",
    }
    width: float = 60.0
    height: float = 30.0
    horizontal_proportion: float = 0.20
    sep: float = 4.0
    offset: float = 6.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class StructuralStateLayout(_CellDesignerSimpleMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Ellipse
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 50.0
    height: float = 16.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModificationLayout(_CellDesignerSimpleMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Ellipse
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 16.0
    height: float = 16.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class _OvalCompartmentShape(momapy.core.NodeLayout):
    outer_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    outer_stroke_width: typing.Optional[float] = 2.0
    outer_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    inner_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    inner_stroke_width: typing.Optional[float] = 1.0
    inner_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    sep: float = 12.0

    def border_drawing_element(self):
        outer_oval = momapy.drawing.Ellipse(
            stroke_width=self.outer_stroke_width,
            stroke=self.outer_stroke,
            fill=self.outer_fill,
            point=self.position,
            rx=self.width / 2,
            ry=self.height / 2,
        )
        inner_oval = momapy.drawing.Ellipse(
            stroke_width=self.inner_stroke_width,
            stroke=self.inner_stroke,
            fill=self.inner_fill,
            point=self.position,
            rx=self.width / 2 - self.sep,
            ry=self.height / 2 - self.sep,
        )
        group = momapy.drawing.Group(
            elements=(
                outer_oval,
                inner_oval,
            )
        )
        return group


@dataclasses.dataclass(frozen=True, kw_only=True)
class OvalCompartmentLayout(_CellDesignerSimpleMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = _OvalCompartmentShape
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "outer_stroke": "outer_stroke",
        "outer_stroke_width": "outer_stroke_width",
        "outer_fill": "outer_fill",
        "inner_stroke": "inner_stroke",
        "inner_stroke_width": "inner_stroke_width",
        "inner_fill": "inner_fill",
        "sep": "sep",
    }
    width: float = 16.0
    height: float = 16.0
    outer_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    outer_stroke_width: typing.Optional[float] = 2.0
    outer_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    inner_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    inner_stroke_width: typing.Optional[float] = 1.0
    inner_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    sep: float = 12.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class _SquareCompartmentShape(momapy.core.NodeLayout):
    outer_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    outer_stroke_width: typing.Optional[float] = 2.0
    outer_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    outer_rounded_corners: float = 20.0
    inner_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    inner_stroke_width: typing.Optional[float] = 1.0
    inner_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    inner_rounded_corners: float = 20.0
    sep: float = 12.0

    def border_drawing_element(self):
        outer_square = momapy.drawing.Rectangle(
            stroke_width=self.outer_stroke_width,
            stroke=self.outer_stroke,
            fill=self.outer_fill,
            point=self.position - (self.width / 2, self.height / 2),
            width=self.width,
            height=self.height,
            rx=self.outer_rounded_corners,
            ry=self.outer_rounded_corners,
        )
        inner_square = momapy.drawing.Rectangle(
            stroke_width=self.inner_stroke_width,
            stroke=self.inner_stroke,
            fill=self.inner_fill,
            point=self.position
            + (self.sep - self.width / 2, self.sep - self.height / 2),
            width=self.width - self.sep * 2,
            height=self.height - self.sep * 2,
            rx=self.inner_rounded_corners,
            ry=self.inner_rounded_corners,
        )
        group = momapy.drawing.Group(
            elements=(
                outer_square,
                inner_square,
            )
        )
        return group


@dataclasses.dataclass(frozen=True, kw_only=True)
class SquareCompartmentLayout(_CellDesignerSimpleMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = _SquareCompartmentShape
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "outer_stroke": "outer_stroke",
        "outer_stroke_width": "outer_stroke_width",
        "outer_fill": "outer_fill",
        "outer_rounded_corners": "outer_rounded_corners",
        "inner_stroke": "inner_stroke",
        "inner_stroke_width": "inner_stroke_width",
        "inner_fill": "inner_fill",
        "inner_rounded_corners": "inner_rounded_corners",
        "sep": "sep",
    }
    width: float = 16.0
    height: float = 16.0
    outer_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    outer_stroke_width: typing.Optional[float] = 2.0
    outer_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    outer_rounded_corners: float = 20.0
    inner_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    inner_stroke_width: typing.Optional[float] = 1.0
    inner_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    inner_rounded_corners: float = 15.0
    sep: float = 12.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReactionNodeLayout(_CellDesignerSimpleMixin, _CellDesignerShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Rectangle
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 8.0
    height: float = 8.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReactionLayout(momapy.arcs.Arrow):
    reaction_node: ReactionNodeLayout

    def self_children(self):
        layout_elements = momapy.arcs.Arrow.self_children(self)
        layout_elements.append(self.reaction_node)
        return layout_elements


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateTransitionLayout(ReactionLayout):
    width: float = 14.0
    height: float = 10.0
    shorten: float = 2.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: typing.Optional[float] = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: typing.Optional[float] = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black


@dataclasses.dataclass(frozen=True, kw_only=True)
class TranscriptionLayout(ReactionLayout):
    width: float = 12.0
    height: float = 12.0
    shorten: float = 2.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = (10, 3, 2, 3, 2, 3)
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: typing.Optional[float] = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: typing.Optional[float] = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black


@dataclasses.dataclass(frozen=True, kw_only=True)
class ConsumptionLayout(momapy.arcs.PolyLine):
    shorten: float = 0.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: typing.Optional[float] = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: typing.Optional[float] = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProductionLayout(momapy.arcs.Arrow):
    width: float = 14.0
    height: float = 10.0
    shorten: float = 2.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: typing.Optional[float] = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: typing.Optional[float] = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black


@dataclasses.dataclass(frozen=True)
class CellDesignerModel(momapy.sbml.core.Model):
    species_references: frozenset[
        CellDesignerSpeciesReference
    ] = dataclasses.field(default_factory=frozenset)
    sbml_reactions: frozenset[Reaction] = dataclasses.field(
        default_factory=frozenset
    )
    boolean_logic_gates: frozenset[BooleanLogicGate] = dataclasses.field(
        default_factory=frozenset
    )
    modulations: frozenset[ReactionModification] = dataclasses.field(
        default_factory=frozenset
    )

    def is_submodel(self, other):
        pass


@dataclasses.dataclass(frozen=True)
class CellDesignerLayout(momapy.core.MapLayout):
    pass


@dataclasses.dataclass(frozen=True)
class CellDesignerMap(momapy.core.Map):
    model: typing.Optional[CellDesignerModel] = None
    layout: typing.Optional[CellDesignerLayout] = None


CellDesignerModelBuilder = momapy.builder.get_or_make_builder_cls(
    CellDesignerModel
)
CellDesignerLayoutBuilder = momapy.builder.get_or_make_builder_cls(
    CellDesignerLayout
)


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
