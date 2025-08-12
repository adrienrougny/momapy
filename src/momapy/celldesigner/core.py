"""Classes for CellDesigner maps"""

import dataclasses
import enum
import math
import typing

import momapy.core
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


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerModelElement(momapy.core.ModelElement):
    """Base class for CellDesigner model elements"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModificationResidue(CellDesignerModelElement):
    """Class for modification residues"""

    name: str | None = None
    order: int | None = None


class ModificationState(enum.Enum):
    """Class for modification states"""

    PHOSPHORYLATED = "P"
    UBIQUITINATED = "Ub"
    ACETYLATED = "Ac"
    METHYLATED = "M"
    HYDROXYLATED = "OH"
    GLYCOSYLATED = "G"
    MYRISTOYLATED = "My"
    PALMITOYLATED = "Pa"
    PALMYTOYLATED = "Pa"
    PRENYLATED = "Pr"
    PROTONATED = "H"
    SULFATED = "S"
    DON_T_CARE = "*"
    UNKNOWN = "?"


@dataclasses.dataclass(frozen=True, kw_only=True)
class Region(CellDesignerModelElement):
    """Class for regions"""

    name: str | None = dataclasses.field(
        default=None, metadata={"description": "The name of the region"}
    )
    active: bool = dataclasses.field(
        default=False,
        metadata={"description": "Whether the region is active or not"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModificationSite(Region):
    """Class for modification sites"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CodingRegion(Region):
    """Class for coding regions"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class RegulatoryRegion(Region):
    """Class for regulatory regions"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TranscriptionStartingSiteL(Region):
    """Class for left transcription starting sites"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TranscriptionStartingSiteR(Region):
    """Class for right transcription starting sites"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProteinBindingDomain(Region):
    """Class for protein binding domains"""

    pass


# abstract
# changed name from reference to template to distinguish from SBML's
# species reference which has a different meaning (reference to a species)
@dataclasses.dataclass(frozen=True, kw_only=True)
class SpeciesTemplate(CellDesignerModelElement):
    """Base class for species templates"""

    name: str = dataclasses.field(
        metadata={"description": "The name of the species template"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProteinTemplate(SpeciesTemplate):
    """Base class for protein templates"""

    modification_residues: frozenset[ModificationResidue] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The modification residues of the protein template"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProteinTemplate(ProteinTemplate):
    """Class for generic protein templates"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TruncatedProteinTemplate(ProteinTemplate):
    """Class for truncated protein templates"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReceptorTemplate(ProteinTemplate):
    """Class for receptor templates"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class IonChannelTemplate(ProteinTemplate):
    """Class for ion channel templates"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class GeneTemplate(SpeciesTemplate):
    """Class for gene templates"""

    regions: frozenset[
        ModificationSite
        | CodingRegion
        | RegulatoryRegion
        | TranscriptionStartingSiteL
        | TranscriptionStartingSiteR
    ] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The regions of the gene template"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class RNATemplate(SpeciesTemplate):
    """Class for RNA templates"""

    regions: frozenset[ModificationSite | CodingRegion | ProteinBindingDomain] = (
        dataclasses.field(
            default_factory=frozenset,
            metadata={"description": "The regions of the RNA template"},
        )
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class AntisenseRNATemplate(SpeciesTemplate):
    """Class for antisense RNA templates"""

    regions: frozenset[ModificationSite | CodingRegion | ProteinBindingDomain] = (
        dataclasses.field(
            default_factory=frozenset,
            metadata={"description": "The regions of the antisense RNA template"},
        )
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Modification(CellDesignerModelElement):
    """Class for modifications"""

    residue: ModificationResidue | ModificationSite | None = dataclasses.field(
        default=None,
        metadata={"description": "The residue of the modification"},
    )
    state: ModificationState | None = dataclasses.field(
        default=None, metadata={"description": "The state of the modification"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class StructuralState(CellDesignerModelElement):
    """Class for structural states"""

    value: str | None = dataclasses.field(
        default=None,
        metadata={"description": "The value of the structural state"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Compartment(momapy.sbml.core.Compartment, CellDesignerModelElement):
    """Class for compartments"""

    pass


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class Species(momapy.sbml.core.Species, CellDesignerModelElement):
    """Base class for species"""

    hypothetical: bool = dataclasses.field(
        default=False,
        metadata={"description": "Whether the species is hypothetical or not"},
    )
    active: bool = dataclasses.field(
        default=False,
        metadata={"description": "Whether the species is active or not"},
    )
    homomultimer: int = dataclasses.field(
        default=1,
        metadata={"description": "The number of subunits forming the species"},
    )


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class Protein(Species):
    """Base class for proteins"""

    template: ProteinTemplate = dataclasses.field(
        metadata={"description": "The template of the species"}
    )
    modifications: frozenset[Modification] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The modifications of the proteins"},
    )
    structural_states: frozenset[StructuralState] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The structural states of the protein"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProtein(Protein):
    """Class for generic proteins"""

    template: GenericProteinTemplate = dataclasses.field(
        metadata={"description": "The template of the generic protein"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TruncatedProtein(Protein):
    """Class for truncated proteins"""

    template: TruncatedProteinTemplate = dataclasses.field(
        metadata={"description": "The template of the truncated protein"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Receptor(Protein):
    """Class for receptors"""

    template: ReceptorTemplate = dataclasses.field(
        metadata={"description": "The template of the receptor"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class IonChannel(Protein):
    """Class for ion channels"""

    template: IonChannelTemplate = dataclasses.field(
        metadata={"description": "The template of the ion channel"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Gene(Species):
    """Class for genes"""

    template: GeneTemplate
    modifications: frozenset[Modification] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class RNA(Species):
    """Class for RNAs"""

    template: RNATemplate
    modifications: frozenset[Modification] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class AntisenseRNA(Species):
    """Class for antisense RNAs"""

    template: AntisenseRNATemplate
    modifications: frozenset[Modification] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Phenotype(Species):
    """Class for phenotypes"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Ion(Species):
    """Class for ions"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleMolecule(Species):
    """Class for simple molecules"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Drug(Species):
    """Class for drugs"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Unknown(Species):
    """Class for unknown species"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Complex(Species):
    """Class for complexes"""

    structural_states: frozenset[StructuralState] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The structural states of the complex"},
    )
    subunits: frozenset[Species] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The subunits of the complex"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Degraded(Species):
    """Class for degradeds"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Reactant(momapy.sbml.core.SpeciesReference, CellDesignerModelElement):
    """Class for reactants"""

    base: bool = dataclasses.field(
        default=False,
        metadata={"description": "Whether the reactant is a base reactant or not"},
    )  # TODO: no default?


@dataclasses.dataclass(frozen=True, kw_only=True)
class Product(momapy.sbml.core.SpeciesReference, CellDesignerModelElement):
    """Class for products"""

    base: bool = dataclasses.field(
        default=False,
        metadata={"description": "Whether the product is a base product or not"},
    )  # TODO: no default?


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class BooleanLogicGate(CellDesignerModelElement):
    """Base class for Boolean logic gates"""

    inputs: frozenset[Species] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The inputs of the Boolean logic gate"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndGate(BooleanLogicGate):
    """Class for and gates"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrGate(BooleanLogicGate):
    """Class for or gates"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotGate(BooleanLogicGate):
    """Class for not gates"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownGate(BooleanLogicGate):
    """Class for unknown gates"""

    pass


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class KnownOrUnknownModulator(
    momapy.sbml.core.ModifierSpeciesReference, CellDesignerModelElement
):
    """Base class for know or unknown modulators"""

    # redefined because can be BooleanLogicGate
    referred_species: Species | BooleanLogicGate = dataclasses.field(
        metadata={"description": "The species the modifier refers to"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Modulator(KnownOrUnknownModulator):
    """Class for modulators"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownModulator(KnownOrUnknownModulator):
    """Class for unknown modulators"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Inhibitor(Modulator):
    """Class for inhibitors"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhysicalStimulator(Modulator):
    """Class for physical stimulators"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Catalyzer(PhysicalStimulator):
    """Class for catalyzers"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Trigger(Modulator):
    """Class for triggers"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownCatalyzer(UnknownModulator):
    """Class for unknown catalyzers"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInhibitor(UnknownModulator):
    """Class for unknown inhibitors"""

    pass


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class Reaction(momapy.sbml.core.Reaction, CellDesignerModelElement):
    """Base class for reactions"""

    reactants: frozenset[Reactant] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The reactants of the reaction"},
    )
    products: frozenset[Product] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The products of the reaction"},
    )
    modifiers: frozenset[KnownOrUnknownModulator] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The modifiers of the reaction"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateTransition(Reaction):
    """Class for state transitions"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class KnownTransitionOmitted(Reaction):
    """Class for known transitions omitted"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownTransition(Reaction):
    """Class for unknown transitions"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Transcription(Reaction):
    """Class for transcriptions"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Translation(Reaction):
    """Class for translation"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Transport(Reaction):
    """Class for transports"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class HeterodimerAssociation(Reaction):
    """Class for heterodimer associations"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Dissociation(Reaction):
    """Class for dissociations"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Truncation(Reaction):
    """Class for truncations"""

    pass


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class KnownOrUnknownModulation(CellDesignerModelElement):
    source: Species | BooleanLogicGate = dataclasses.field(
        metadata={"description": "The source of the influence"}
    )
    target: Species | None = dataclasses.field(
        metadata={"description": "The target of the influence"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Modulation(KnownOrUnknownModulation):
    """Class for modulations"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Catalysis(Modulation):
    """Class for catalyses"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Inhibition(Modulation):
    """Class for inhibitions"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhysicalStimulation(Modulation):
    """Class for physical stimulations"""

    pass


# need to be a different name than the modifier Trigger
@dataclasses.dataclass(frozen=True, kw_only=True)
class Triggering(Modulation):
    """Class for triggerings"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluence(Modulation):
    """Class for positive influences"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NegativeInfluence(Modulation):
    """Class for negative influences"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownModulation(KnownOrUnknownModulation):
    """Class for unknown modulations"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownCatalysis(UnknownModulation):
    """Class for unknown catalyses"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInhibition(UnknownModulation):
    """Class for unknown inhibitions"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownPositiveInfluence(UnknownModulation):
    """Class for unknown positive influences"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownNegativeInfluence(UnknownModulation):
    """Class for unknown negative influences"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownPhysicalStimulation(UnknownModulation):
    """Class for unknown physical stimulations"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownTriggering(UnknownModulation):
    """Class for unknown triggerings"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerModel(momapy.sbml.core.Model):
    """Class for CellDesigner models"""

    species_templates: frozenset[SpeciesTemplate] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The species templates of the CellDesigner model"},
    )
    boolean_logic_gates: frozenset[BooleanLogicGate] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The boolean logic gates of the CellDesigner model"},
    )
    modulations: frozenset[Modulation | UnknownModulation] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The modulations of the CellDesigner model"},
    )

    def is_submodel(self, other):
        pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerNode(momapy.sbgn.core.SBGNNode):
    """Base class for CellDesigner nodes"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerSingleHeadedArc(momapy.core.SingleHeadedArc):
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

    def self_drawing_elements(self):
        drawing_elements = momapy.builder.super_or_builder(
            CellDesignerSingleHeadedArc, self
        ).self_drawing_elements()
        done_bases = []
        for base in type(self).__mro__:
            if (
                momapy.builder.issubclass_or_builder(base, momapy.sbgn.core._SBGNMixin)
                and base is not type(self)
                and not any([issubclass(done_base, base) for done_base in done_bases])
            ):
                drawing_elements += getattr(base, "_mixin_drawing_elements")(self)
                done_bases.append(base)
        return drawing_elements


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerDoubleHeadedArc(momapy.core.DoubleHeadedArc):
    """Base class for CellDesigner double-headed arcs"""

    path_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )
    path_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    path_stroke_width: float | None = 1.0

    def self_drawing_elements(self):
        drawing_elements = momapy.builder.super_or_builder(
            CellDesignerDoubleHeadedArc, self
        ).self_drawing_elements()
        done_bases = []
        for base in type(self).__mro__:
            if (
                momapy.builder.issubclass_or_builder(base, momapy.sbgn.core._SBGNMixin)
                and base is not type(self)
                and not any([issubclass(done_base, base) for done_base in done_bases])
            ):
                drawing_elements += getattr(base, "_mixin_drawing_elements")(self)
                done_bases.append(base)
        return drawing_elements


@dataclasses.dataclass(frozen=True, kw_only=True)
class _SimpleNodeMixin(momapy.sbgn.core._SimpleMixin):
    active: bool = False
    active_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )
    active_filter: momapy.drawing.NoneValueType | momapy.drawing.Filter | None = None
    active_sep: float = 4.0
    active_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    active_stroke_dasharray: momapy.drawing.NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    active_stroke_dashoffset: float | None = None
    active_stroke_width: float | None = 1.0
    active_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        if obj.active:
            layout_element = dataclasses.replace(
                obj,
                width=obj.width + obj.active_sep * 2,
                height=obj.height + obj.active_sep * 2,
                label=None,
                fill=obj.active_fill,
                stroke=obj.active_stroke,
                stroke_width=obj.active_stroke_width,
                stroke_dasharray=obj.active_stroke_dasharray,
                stroke_dashoffset=obj.active_stroke_dashoffset,
            )
            drawing_elements = layout_element.obj_drawing_elements()
        else:
            drawing_elements = []
        drawing_elements += momapy.sbgn.core._SimpleMixin._mixin_drawing_elements(obj)
        return drawing_elements


@dataclasses.dataclass(frozen=True, kw_only=True)
class _MultiNodeMixin(momapy.sbgn.core._MultiMixin):
    active: bool = False
    active_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )
    active_filter: momapy.drawing.NoneValueType | momapy.drawing.Filter | None = None
    active_sep: float = 4.0
    active_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    active_stroke_dasharray: momapy.drawing.NoneValueType | tuple[float] | None = (
        4,
        2,
    )
    active_stroke_dashoffset: float | None = None
    active_stroke_width: float | None = 1.0
    active_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    n: int = 1

    @property
    def _n(self):
        return self.n

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        if obj.active:
            layout_element = dataclasses.replace(
                obj,
                active=False,
                fill=obj.active_fill,
                filter=obj.active_filter,
                height=obj.height + obj.active_sep * 2,
                label=None,
                stroke=obj.active_stroke,
                stroke_width=obj.active_stroke_width,
                stroke_dasharray=obj.active_stroke_dasharray,
                stroke_dashoffset=obj.active_stroke_dashoffset,
                width=obj.width + obj.active_sep * 2,
            )
            drawing_elements = layout_element.self_drawing_elements()
        else:
            drawing_elements = []
        drawing_elements += momapy.sbgn.core._MultiMixin._mixin_drawing_elements(obj)
        return drawing_elements


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProteinLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for generic protein layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.sbgn.pd.MacromoleculeMultimerLayout._make_subunit_shape(
            self, position, width, height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _IonChannelShape(momapy.core.Shape):
    position: momapy.geometry.Point
    width: float
    height: float
    right_rectangle_width: float
    rounded_corners: float

    def joint1(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width - self.rounded_corners,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.rounded_corners - self.height / 2,
        )

    def joint4(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.height / 2 - self.rounded_corners,
        )

    def joint5(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width - self.rounded_corners,
            self.height / 2,
        )

    def joint6(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            self.height / 2,
        )

    def joint7(self):
        return self.position + (
            -self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint8(self):
        return self.position + (
            -self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def joint9(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width + self.rounded_corners,
            self.height / 2,
        )

    def joint10(self):
        return self.position + (
            self.width / 2 - self.rounded_corners,
            -self.height / 2,
        )

    def joint11(self):
        return self.position + (
            self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def joint12(self):
        return self.position + (
            self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint13(self):
        return self.position + (
            self.width / 2 - self.rounded_corners,
            self.height / 2,
        )

    def joint14(self):
        return self.position + (
            self.rounded_corners + self.width / 2 - self.right_rectangle_width,
            self.height / 2,
        )

    def joint15(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.height / 2 - self.rounded_corners,
        )

    def joint16(self):
        return self.position + (
            self.width / 2 - self.right_rectangle_width,
            self.rounded_corners - self.height / 2,
        )

    def drawing_elements(self):
        left_rectangle = momapy.drawing.Rectangle(
            point=self.position - (self.width / 2, self.height / 2),
            height=self.height,
            width=self.width - self.right_rectangle_width,
            rx=self.rounded_corners,
            ry=self.rounded_corners,
        )
        right_rectangle = momapy.drawing.Rectangle(
            point=self.position
            + (self.width / 2 - self.right_rectangle_width, -self.height / 2),
            height=self.height,
            width=self.right_rectangle_width,
            rx=self.rounded_corners,
            ry=self.rounded_corners,
        )
        return [left_rectangle, right_rectangle]


@dataclasses.dataclass(frozen=True, kw_only=True)
class IonChannelLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for generic ion channel layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0
    right_rectangle_width: float = 20.0

    def _make_subunit_shape(self, position, width, height):
        return _IonChannelShape(
            position=position,
            width=width,
            height=height,
            rounded_corners=self.rounded_corners,
            right_rectangle_width=self.right_rectangle_width,
        )

    def label_center(self):
        return momapy.geometry.Point(
            self.position.x - self.right_rectangle_width / 2, self.position.y
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for complex layouts"""

    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 6.0
    # label -12 from south

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shapes.Rectangle(
            position=position,
            width=width,
            height=height,
            top_left_rx=self.cut_corners,
            top_left_ry=self.cut_corners,
            top_left_rounded_or_cut="cut",
            top_right_rx=self.cut_corners,
            top_right_ry=self.cut_corners,
            top_right_rounded_or_cut="cut",
            bottom_left_rx=self.cut_corners,
            bottom_left_ry=self.cut_corners,
            bottom_left_rounded_or_cut="cut",
            bottom_right_rx=self.cut_corners,
            bottom_right_ry=self.cut_corners,
            bottom_right_rounded_or_cut="cut",
        )

    def label_center(self):
        return self.south() - (0, 12)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleMoleculeLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for simple chemical layouts"""

    width: float = 60.0
    height: float = 30.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shapes.Ellipse(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class IonLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for ion layouts"""

    width: float = 60.0
    height: float = 30.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shapes.Ellipse(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for unknown species layouts"""

    width: float = 60.0
    height: float = 30.0
    stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )
    fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.gray
    )

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shapes.Ellipse(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class _DegradedShape(momapy.core.Shape):
    position: momapy.geometry.Point
    width: float
    height: float

    def drawing_elements(self):
        circle = momapy.drawing.Ellipse(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        actions = [
            momapy.drawing.MoveTo(self.position - (self.width / 2, -self.height / 2)),
            momapy.drawing.LineTo(self.position + (self.width / 2, -self.height / 2)),
        ]
        bar = momapy.drawing.Path(actions=actions)
        return [circle, bar]


@dataclasses.dataclass(frozen=True, kw_only=True)
class DegradedLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for degraded layouts"""

    width: float = 30.0
    height: float = 30.0

    def _make_subunit_shape(self, position, width, height):
        return _DegradedShape(position=position, width=width, height=height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class GeneLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for gene layouts"""

    width: float = 60.0
    height: float = 30.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shapes.Rectangle(
            position=position, width=width, height=height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for phenotype layouts"""

    width: float = 60.0
    height: float = 30.0
    angle: float = 60.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shapes.Hexagon(
            position=position,
            width=width,
            height=height,
            left_angle=self.angle,
            right_angle=self.angle,
        )

    def north_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1()

    def north_north_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() * 0.75 + shape.joint2() * 0.25

    def north(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() / 2 + shape.joint2() / 2

    def north_north_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() * 0.25 + shape.joint2() * 0.75

    def north_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint2()

    def east_north_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() / 2 + shape.joint2() / 2

    def east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3()

    def east_south_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() / 2 + shape.joint3() / 2

    def south_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4()

    def south_south_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint5() * 0.25 + shape.joint4() * 0.75

    def south(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint5() / 2 + shape.joint4() / 2

    def south_south_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint5() * 0.75 + shape.joint4() * 0.25

    def south_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint5()

    def west_south_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6() / 2 + shape.joint5() / 2

    def west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6()

    def west_north_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6() / 2 + shape.joint1() / 2


@dataclasses.dataclass(frozen=True, kw_only=True)
class RNALayout(_MultiNodeMixin, CellDesignerNode):
    """Class for RNA layouts"""

    width: float = 60.0
    height: float = 30.0
    angle: float = 45.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shapes.Parallelogram(
            position=position, width=width, height=height, angle=self.angle
        )

    def north_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1()

    def north_north_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() * 0.75 + shape.joint2() * 0.25

    def north(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() / 2 + shape.joint2() / 2

    def north_north_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() * 0.25 + shape.joint2() * 0.75

    def north_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint2()

    def east_north_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() * 0.25 + shape.joint2() * 0.75

    def east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() / 2 + shape.joint2() / 2

    def east_south_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() * 0.75 + shape.joint2() * 0.25

    def south_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3()

    def south_south_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.25 + shape.joint3() * 0.75

    def south(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() / 2 + shape.joint3() / 2

    def south_south_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.75 + shape.joint3() * 0.25

    def south_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4()

    def west_south_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.75 + shape.joint1() * 0.25

    def west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() / 2 + shape.joint1() / 2

    def west_north_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.25 + shape.joint1() * 0.75


@dataclasses.dataclass(frozen=True, kw_only=True)
class AntisenseRNALayout(_MultiNodeMixin, CellDesignerNode):
    """Class for antisense RNA layouts"""

    width: float = 60.0
    height: float = 30.0
    angle: float = 45.0

    def _make_subunit_shape(self, position, width, height):
        return momapy.meta.shapes.Parallelogram(
            position=position,
            width=width,
            height=height,
            angle=180 - self.angle,
        )

    def north_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1()

    def north_north_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() * 0.75 + shape.joint2() * 0.25

    def north(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() / 2 + shape.joint2() / 2

    def north_north_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() * 0.25 + shape.joint2() * 0.75

    def north_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint2()

    def east_north_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() * 0.25 + shape.joint2() * 0.75

    def east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() / 2 + shape.joint2() / 2

    def east_south_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3() * 0.75 + shape.joint2() * 0.25

    def south_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3()

    def south_south_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.25 + shape.joint3() * 0.75

    def south(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() / 2 + shape.joint3() / 2

    def south_south_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.75 + shape.joint3() * 0.25

    def south_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4()

    def west_south_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.75 + shape.joint1() * 0.25

    def west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() / 2 + shape.joint1() / 2

    def west_north_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.25 + shape.joint1() * 0.75


@dataclasses.dataclass(frozen=True, kw_only=True)
class _TruncatedProteinShape(momapy.core.Shape):
    position: momapy.geometry.Point
    width: float
    height: float
    rounded_corners: float
    vertical_truncation: float  # proportion of total height, number in ]0, 1[
    horizontal_truncation: float  # proportion of total width number in ]0, 1[

    def joint1(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2,
            self.height / 2 - self.vertical_truncation * self.height,
        )

    def joint4(self):
        return self.position + (
            self.width / 2 - self.horizontal_truncation * self.width,
            self.vertical_truncation * self.height - self.height / 2,
        )

    def joint5(self):
        return self.position + (
            self.width / 2 - self.horizontal_truncation * self.width,
            self.height / 2,
        )

    def joint6(self):
        return self.position + (
            self.rounded_corners - self.width / 2,
            self.height / 2,
        )

    def joint7(self):
        return self.position + (
            -self.width / 2,
            self.height / 2 - self.rounded_corners,
        )

    def joint8(self):
        return self.position + (
            -self.width / 2,
            self.rounded_corners - self.height / 2,
        )

    def drawing_elements(self):
        actions = [
            momapy.drawing.MoveTo(self.joint1()),
            momapy.drawing.LineTo(self.joint2()),
            momapy.drawing.LineTo(self.joint3()),
            momapy.drawing.LineTo(self.joint4()),
            momapy.drawing.LineTo(self.joint5()),
            momapy.drawing.LineTo(self.joint5()),
            momapy.drawing.LineTo(self.joint6()),
            momapy.drawing.EllipticalArc(
                self.joint7(),
                self.rounded_corners,
                self.rounded_corners,
                0,
                0,
                1,
            ),
            momapy.drawing.LineTo(self.joint8()),
            momapy.drawing.EllipticalArc(
                self.joint1(),
                self.rounded_corners,
                self.rounded_corners,
                0,
                0,
                1,
            ),
            momapy.drawing.ClosePath(),
        ]
        border = momapy.drawing.Path(actions=actions)
        return [border]


@dataclasses.dataclass(frozen=True, kw_only=True)
class TruncatedProteinLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for truncated protein layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 15.0
    vertical_truncation: float = 0.40
    horizontal_truncation: float = 0.20

    def _make_subunit_shape(self, position, width, height):
        return _TruncatedProteinShape(
            position=position,
            width=width,
            height=height,
            rounded_corners=self.rounded_corners,
            vertical_truncation=self.vertical_truncation,
            horizontal_truncation=self.horizontal_truncation,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReceptorLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for receptor layouts"""

    width: float = 60.0
    height: float = 30.0
    vertical_truncation: float = 0.10  # proportion of total height, number in ]0, 1[

    def _make_subunit_shape(self, position, width, height):
        angle = math.atan2(width / 2, self.vertical_truncation * height)
        angle = momapy.geometry.get_normalized_angle(angle)
        angle = math.degrees(angle)
        return momapy.meta.shapes.TurnedHexagon(
            position=position,
            width=width,
            height=height,
            top_angle=180 - angle,
            bottom_angle=angle,
        )

    def north_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1()

    def north_north_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint1() / 2 + shape.joint2() / 2

    def north(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint2()

    def north_north_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint2() * 0.25 + shape.joint3() * 0.75

    def north_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint3()

    def east_north_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.25 + shape.joint3() * 0.75

    def east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() / 2 + shape.joint3() / 2

    def east_south_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4() * 0.75 + shape.joint3() * 0.25

    def south_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint4()

    def south_south_east(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint5() / 2 + shape.joint4() / 2

    def south(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint5()

    def south_south_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6() / 2 + shape.joint5() / 2

    def south_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6()

    def west_south_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6() * 0.75 + shape.joint1() * 0.25

    def west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6() / 2 + shape.joint1() / 2

    def west_north_west(self) -> momapy.geometry.Point:
        width = self.width - self.offset * (self._n - 1)
        height = self.height - self.offset * (self._n - 1)
        position = self.position + (
            self.width / 2 - width / 2,
            self.height / 2 - height / 2,
        )
        shape = self._make_subunit_shape(position, width, height)
        return shape.joint6() * 0.25 + shape.joint1() * 0.75


@dataclasses.dataclass(frozen=True, kw_only=True)
class _DrugShape(momapy.core.Shape):
    position: momapy.geometry.Point
    width: float
    height: float
    horizontal_proportion: float  # ]0, 0.5[
    sep: float

    def joint1(self):
        return self.position + (
            -self.width / 2 + self.horizontal_proportion * self.width,
            -self.height / 2,
        )

    def joint2(self):
        return self.position + (
            self.width / 2 - self.horizontal_proportion * self.width,
            -self.height / 2,
        )

    def joint3(self):
        return self.position + (
            self.width / 2 - self.horizontal_proportion * self.width,
            self.height / 2,
        )

    def joint4(self):
        return self.position + (
            -self.width / 2 + self.horizontal_proportion * self.width,
            self.height / 2,
        )

    def drawing_elements(self):
        actions = [
            momapy.drawing.MoveTo(self.joint1()),
            momapy.drawing.LineTo(self.joint2()),
            momapy.drawing.EllipticalArc(
                self.joint3(),
                self.horizontal_proportion * self.width,
                self.height / 2,
                0,
                0,
                1,
            ),
            momapy.drawing.LineTo(self.joint4()),
            momapy.drawing.EllipticalArc(
                self.joint1(),
                self.horizontal_proportion * self.width,
                self.height / 2,
                0,
                0,
                1,
            ),
            momapy.drawing.ClosePath(),
        ]
        outer_stadium = momapy.drawing.Path(actions=actions)
        inner_joint1 = self.joint1() + (0, self.sep)
        inner_joint2 = self.joint2() + (0, self.sep)
        inner_joint3 = self.joint3() + (0, -self.sep)
        inner_joint4 = self.joint4() + (0, -self.sep)
        inner_rx = self.horizontal_proportion * self.width - self.sep
        inner_ry = self.height / 2 - self.sep
        actions = [
            momapy.drawing.MoveTo(inner_joint1),
            momapy.drawing.LineTo(inner_joint2),
            momapy.drawing.EllipticalArc(
                inner_joint3,
                inner_rx,
                inner_ry,
                0,
                0,
                1,
            ),
            momapy.drawing.LineTo(inner_joint4),
            momapy.drawing.EllipticalArc(
                inner_joint1,
                inner_rx,
                inner_ry,
                0,
                0,
                1,
            ),
            momapy.drawing.ClosePath(),
        ]
        inner_stadium = momapy.drawing.Path(actions=actions)
        return [outer_stadium, inner_stadium]


@dataclasses.dataclass(frozen=True, kw_only=True)
class DrugLayout(_MultiNodeMixin, CellDesignerNode):
    """Class for drug layouts"""

    width: float = 60.0
    height: float = 30.0
    horizontal_proportion: float = 0.20
    sep: float = 4.0

    def _make_subunit_shape(self, position, width, height):
        return _DrugShape(
            position=position,
            width=width,
            height=height,
            horizontal_proportion=self.horizontal_proportion,
            sep=self.sep,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class StructuralStateLayout(_SimpleNodeMixin, CellDesignerNode):
    """Class for structural states layouts"""

    width: float = 50.0
    height: float = 16.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModificationLayout(_SimpleNodeMixin, CellDesignerNode):
    """Class for modification layouts"""

    width: float = 16.0
    height: float = 16.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _OvalCompartmentShape(momapy.core.Shape):
    position: momapy.geometry.Point
    width: float
    height: float
    inner_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = None
    inner_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = None
    inner_stroke_width: float | None = None
    sep: float = 12.0

    def drawing_elements(self):
        outer_oval = momapy.drawing.Ellipse(
            point=self.position,
            rx=self.width / 2,
            ry=self.height / 2,
        )
        inner_oval = momapy.drawing.Ellipse(
            fill=self.inner_fill,
            stroke=self.inner_stroke,
            stroke_width=self.inner_stroke_width,
            point=self.position,
            rx=self.width / 2 - self.sep,
            ry=self.height / 2 - self.sep,
        )
        return [outer_oval, inner_oval]


@dataclasses.dataclass(frozen=True, kw_only=True)
class OvalCompartmentLayout(_SimpleNodeMixin, CellDesignerNode):
    """Class for oval compartment layouts"""

    height: float = 16.0
    inner_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    inner_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    inner_stroke_width: float | None = 1.0
    sep: float = 12.0
    width: float = 16.0

    def _make_shape(self):
        return _OvalCompartmentShape(
            height=self.height,
            inner_fill=self.inner_fill,
            inner_stroke=self.inner_stroke,
            inner_stroke_width=self.inner_stroke_width,
            position=self.position,
            width=self.width,
            sep=self.sep,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _RectangleCompartmentShape(momapy.core.Shape):
    position: momapy.geometry.Point
    width: float
    height: float
    inner_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = None
    inner_rounded_corners: float = 10.0
    inner_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = None
    inner_stroke_width: float | None = None
    rounded_corners: float = 10.0
    sep: float = 12.0

    def drawing_elements(self):
        outer_rectangle = momapy.drawing.Rectangle(
            point=self.position - (self.width / 2, self.height / 2),
            height=self.height,
            rx=self.rounded_corners,
            ry=self.rounded_corners,
            width=self.width,
        )
        inner_rectangle = momapy.drawing.Rectangle(
            fill=self.inner_fill,
            height=self.height - 2 * self.sep,
            point=self.position
            - (self.width / 2 - self.sep, self.height / 2 - self.sep),
            rx=self.inner_rounded_corners,
            ry=self.inner_rounded_corners,
            stroke=self.inner_stroke,
            stroke_width=self.inner_stroke_width,
            width=self.width - 2 * self.sep,
        )
        return [outer_rectangle, inner_rectangle]


@dataclasses.dataclass(frozen=True, kw_only=True)
class RectangleCompartmentLayout(_SimpleNodeMixin, CellDesignerNode):
    """Class for rectangle compartment layouts"""

    width: float = 16.0
    height: float = 16.0
    inner_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    inner_rounded_corners: float = 10.0
    inner_stroke: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    inner_stroke_width: float | None = 1.0
    rounded_corners: float = 10.0
    sep: float = 12.0

    def _make_shape(self):
        return _RectangleCompartmentShape(
            height=self.height,
            inner_fill=self.inner_fill,
            inner_rounded_corners=self.inner_rounded_corners,
            inner_stroke=self.inner_stroke,
            inner_stroke_width=self.inner_stroke_width,
            position=self.position,
            rounded_corners=self.rounded_corners,
            sep=self.sep,
            width=self.width,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ConsumptionLayout(CellDesignerSingleHeadedArc):
    """Class for consumption layouts"""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProductionLayout(CellDesignerSingleHeadedArc):
    """Class for production layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    arrowhead_height: float = 8.0
    arrowhead_width: float = 15.0
    end_shorten: float = 2.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CatalysisLayout(CellDesignerSingleHeadedArc):
    """Class for catalysis layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    arrowhead_height: float = 7.0
    arrowhead_width: float = 7.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Ellipse._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownCatalysisLayout(CellDesignerSingleHeadedArc):
    """Class for unknown catalysis layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    arrowhead_height: float = 7.0
    arrowhead_width: float = 7.0
    path_stroke_dasharray: momapy.drawing.NoneValueType | tuple[float] | None = (12, 4)

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Ellipse._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class InhibitionLayout(CellDesignerSingleHeadedArc):
    """Class for inhibition layouts"""

    arrowhead_height: float = 10.0
    end_shorten: float = 3.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Bar._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInhibitionLayout(CellDesignerSingleHeadedArc):
    """Class for unknown inhibition layouts"""

    arrowhead_height: float = 10.0
    end_shorten: float = 3.0
    path_stroke_dasharray: momapy.drawing.NoneValueType | tuple[float] | None = (12, 4)

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Bar._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhysicalStimulationLayout(CellDesignerSingleHeadedArc):
    """Class for physical stimulation layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownPhysicalStimulationLayout(CellDesignerSingleHeadedArc):
    """Class for unknown physical stimulation layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0
    path_stroke_dasharray: momapy.drawing.NoneValueType | tuple[float] | None = (12, 4)

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModulationLayout(CellDesignerSingleHeadedArc):
    """Class for modulation layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    arrowhead_height: float = 8.0
    arrowhead_width: float = 15.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Diamond._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownModulationLayout(CellDesignerSingleHeadedArc):
    """Class for unknown modulation layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    arrowhead_height: float = 8.0
    arrowhead_width: float = 15.0
    path_stroke_dasharray: momapy.drawing.NoneValueType | tuple[float] | None = (12, 4)

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Diamond._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluenceLayout(CellDesignerSingleHeadedArc):
    """Class for positive influence layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )
    arrowhead_height: float = 10.0
    arrowhead_stroke_width: float | None = 2.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.StraightBarb._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownPositiveInfluenceLayout(CellDesignerSingleHeadedArc):
    """Class for unknown positive influence layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.drawing.NoneValue
    )
    arrowhead_height: float = 10.0
    arrowhead_stroke_width: float | None = 2.0
    arrowhead_width: float = 10.0
    path_stroke_dasharray: momapy.drawing.NoneValueType | tuple[float] | None = (12, 4)

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.StraightBarb._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TriggeringLayout(CellDesignerSingleHeadedArc):
    """Class for triggering layouts"""

    arrowhead_bar_height: float = 8.0
    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    arrowhead_sep: float = 5.0
    arrowhead_triangle_height: float = 10.0
    arrowhead_triangle_width: float = 15.0

    def _arrowhead_border_drawing_elements(self):
        actions = [
            momapy.drawing.MoveTo(
                momapy.geometry.Point(0, -self.arrowhead_bar_height / 2)
            ),
            momapy.drawing.LineTo(
                momapy.geometry.Point(0, self.arrowhead_bar_height / 2)
            ),
        ]
        bar = momapy.drawing.Path(actions=actions)
        actions = [
            momapy.drawing.MoveTo(momapy.geometry.Point(0, 0)),
            momapy.drawing.LineTo(momapy.geometry.Point(self.arrowhead_sep, 0)),
        ]
        sep = momapy.drawing.Path(actions=actions)
        triangle = momapy.meta.shapes.Triangle(
            position=momapy.geometry.Point(
                self.arrowhead_sep + self.arrowhead_triangle_width / 2,
                0,
            ),
            width=self.arrowhead_triangle_width,
            height=self.arrowhead_triangle_height,
            direction=momapy.core.Direction.RIGHT,
        )
        return [bar, sep] + triangle.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownTriggeringLayout(CellDesignerSingleHeadedArc):
    """Class for unknown triggering layouts"""

    arrowhead_bar_height: float = 8.0
    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    arrowhead_sep: float = 5.0
    arrowhead_triangle_height: float = 10.0
    arrowhead_triangle_width: float = 15.0
    path_stroke_dasharray: momapy.drawing.NoneValueType | tuple[float] | None = (12, 4)

    def _arrowhead_border_drawing_elements(self):
        actions = [
            momapy.drawing.MoveTo(
                momapy.geometry.Point(0, -self.arrowhead_bar_height / 2)
            ),
            momapy.drawing.LineTo(
                momapy.geometry.Point(0, self.arrowhead_bar_height / 2)
            ),
        ]
        bar = momapy.drawing.Path(actions=actions)
        actions = [
            momapy.drawing.MoveTo(momapy.geometry.Point(0, 0)),
            momapy.drawing.LineTo(momapy.geometry.Point(self.arrowhead_sep, 0)),
        ]
        sep = momapy.drawing.Path(actions=actions)
        triangle = momapy.meta.shapes.Triangle(
            position=momapy.geometry.Point(
                self.arrowhead_sep + self.arrowhead_triangle_width / 2,
                0,
            ),
            width=self.arrowhead_triangle_width,
            height=self.arrowhead_triangle_height,
            direction=momapy.core.Direction.RIGHT,
        )
        return [bar, sep] + triangle.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class _ReactionLayout(CellDesignerDoubleHeadedArc):
    reversible: bool = False


@dataclasses.dataclass(frozen=True, kw_only=True)
class _ReactionNodeMixin(momapy.sbgn.core._SBGNMixin):
    _reaction_node_text: typing.ClassVar[str | None] = None
    _font_family: typing.ClassVar[str] = "Helvetica"
    _font_size_func: typing.ClassVar[typing.Callable]
    _font_style: typing.ClassVar[momapy.drawing.FontStyle] = (
        momapy.drawing.FontStyle.NORMAL
    )
    _font_weight: typing.ClassVar[momapy.drawing.FontWeight | float] = (
        momapy.drawing.FontWeight.NORMAL
    )
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _left_connector_fraction: float = 0.4
    _right_connector_fraction: float = 0.6
    reaction_node_height: float = 10.0
    reaction_node_width: float = 10.0
    reaction_node_segment: int = 1
    reaction_node_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    reaction_node_stroke_width: float | None = 1.0
    reaction_node_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    reaction_node_stroke_dashoffset: float | None = None
    reaction_node_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    reaction_node_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    reaction_node_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None

    def left_connector_tip(self):
        segment = self.segments[self.reaction_node_segment]
        position = segment.get_position_at_fraction(self._left_connector_fraction)
        return position

    def right_connector_tip(self):
        segment = self.segments[self.reaction_node_segment]
        position = segment.get_position_at_fraction(self._right_connector_fraction)
        return position

    def reaction_node_border(self, point):
        reaction_node = self._make_reaction_node()
        rotation = self._make_reaction_node_rotation()
        rotated_point = point.transformed(rotation)
        border_point = reaction_node.border(rotated_point)
        border_point = border_point.transformed(rotation.inverted())
        return border_point

    def reaction_node_angle(self, angle):
        reaction_node = self._make_reaction_node()
        border_point = reaction_node.angle(angle, self._get_reaction_node_position())
        rotation = self._make_reaction_node_rotation()
        border_point = border_point.transformed(
            rotation, self._get_reaction_node_position()
        )
        return border_point

    @classmethod
    def _mixin_drawing_elements(cls, obj):
        return [obj._make_rotated_reaction_node_drawing_element()]

    def _get_reaction_node_position(self):
        segment = self.segments[self.reaction_node_segment]
        position = segment.get_position_at_fraction(0.5)
        return position

    def _get_reaction_node_rotation_angle(self):
        segment = self.segments[self.reaction_node_segment]
        angle = momapy.geometry.get_angle_to_horizontal_of_line(segment)
        return angle

    def _make_reaction_node_rotation(self):
        angle = self._get_reaction_node_rotation_angle()
        position = self._get_reaction_node_position()
        rotation = momapy.geometry.Rotation(angle, position)
        return rotation

    def _make_reaction_node(self):
        position = self._get_reaction_node_position()
        if self._reaction_node_text is not None:
            label = momapy.core.TextLayout(
                text=self._reaction_node_text,
                position=position,
                font_family=self._font_family,
                font_size=self._font_size_func(),
                font_style=self._font_style,
                font_weight=self._font_weight,
                fill=self._font_fill,
                stroke=self._font_stroke,
                transform=(self._make_reaction_node_rotation(),),
            )
        else:
            label = None
        reaction_node = momapy.meta.nodes.Rectangle(
            height=self.reaction_node_height,
            position=position,
            width=self.reaction_node_width,
            stroke=self.reaction_node_stroke,
            stroke_width=self.reaction_node_stroke_width,
            stroke_dasharray=self.reaction_node_stroke_dasharray,
            stroke_dashoffset=self.reaction_node_stroke_dashoffset,
            fill=self.reaction_node_fill,
            transform=self.reaction_node_transform,
            filter=self.reaction_node_filter,
            label=label,
        )
        return reaction_node

    def _make_rotated_reaction_node_drawing_element(self):
        reaction_node = self._make_reaction_node()
        drawing_element = reaction_node.drawing_elements()[0]
        rotation = self._make_reaction_node_rotation()
        drawing_element = drawing_element.transformed(rotation)
        return drawing_element


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateTransitionLayout(_ReactionLayout, _ReactionNodeMixin):
    """Class for state transition layouts"""

    _reaction_node_text: typing.ClassVar[str | None] = None
    end_arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    end_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    end_arrowhead_height: float = 8.0
    end_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    end_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    end_arrowhead_width: float = 15.0
    end_shorten: float = 2.0
    reversible: bool = False
    start_arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            return momapy.meta.arcs.DoubleTriangle._start_arrowhead_border_drawing_elements(
                self
            )
        return []

    def _end_arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.DoubleTriangle._end_arrowhead_border_drawing_elements(
            self
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class KnownTransitionOmittedLayout(_ReactionLayout, _ReactionNodeMixin):
    """Class for known transition omitted layouts"""

    _font_size_func: typing.ClassVar[typing.Callable | None] = (
        lambda obj: obj.reaction_node_width / 1.1
    )
    _font_weight: typing.ClassVar[momapy.drawing.FontWeight | float] = (
        momapy.drawing.FontWeight.BOLD
    )
    _reaction_node_text: typing.ClassVar[str | None] = "//"
    end_arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    end_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    end_arrowhead_height: float = 8.0
    end_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    end_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    end_arrowhead_width: float = 15.0
    end_shorten: float = 2.0
    start_arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            return momapy.meta.arcs.DoubleTriangle._start_arrowhead_border_drawing_elements(
                self
            )
        return []

    def _end_arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.DoubleTriangle._end_arrowhead_border_drawing_elements(
            self
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownTransitionLayout(_ReactionLayout, _ReactionNodeMixin):
    """Class for unknown transition layouts"""

    _font_size_func: typing.ClassVar[typing.Callable | None] = (
        lambda obj: obj.reaction_node_width / 1.1
    )
    _font_weight: typing.ClassVar[momapy.drawing.FontWeight | float] = (
        momapy.drawing.FontWeight.BOLD
    )
    _reaction_node_text: typing.ClassVar[str | None] = "?"
    end_arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    end_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    end_arrowhead_height: float = 8.0
    end_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    end_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    end_arrowhead_width: float = 15.0
    end_shorten: float = 2.0
    start_arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            return momapy.meta.arcs.DoubleTriangle._start_arrowhead_border_drawing_elements(
                self
            )
        return []

    def _end_arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.DoubleTriangle._end_arrowhead_border_drawing_elements(
            self
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TranscriptionLayout(_ReactionLayout, _ReactionNodeMixin):
    """Class for transcription layouts"""

    _reaction_node_text: typing.ClassVar[str | None] = None
    end_arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    end_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    end_arrowhead_height: float = 8.0
    end_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    end_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    end_arrowhead_width: float = 15.0
    end_shorten: float = 2.0
    path_stroke_dasharray: momapy.drawing.NoneValueType | tuple[float] | None = (
        12,
        4,
        2,
        4,
        2,
        4,
    )
    start_arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            return momapy.meta.arcs.DoubleTriangle._start_arrowhead_border_drawing_elements(
                self
            )
        return []

    def _end_arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.DoubleTriangle._end_arrowhead_border_drawing_elements(
            self
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TranslationLayout(_ReactionLayout, _ReactionNodeMixin):
    """Class for translation layouts"""

    _reaction_node_text: typing.ClassVar[str | None] = None
    end_arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    end_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    end_arrowhead_height: float = 8.0
    end_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    end_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    end_arrowhead_width: float = 15.0
    end_shorten: float = 2.0
    path_stroke_dasharray: momapy.drawing.NoneValueType | tuple[float] | None = (
        12,
        4,
        2,
        4,
    )
    start_arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            return momapy.meta.arcs.DoubleTriangle._start_arrowhead_border_drawing_elements(
                self
            )
        return []

    def _end_arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.DoubleTriangle._end_arrowhead_border_drawing_elements(
            self
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TransportLayout(_ReactionLayout, _ReactionNodeMixin):
    """Class for transport layouts"""

    _reaction_node_text: typing.ClassVar[str | None] = None
    end_arrowhead_bar_height: float = 8.0
    end_arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    end_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    end_arrowhead_sep: float = 5.0
    end_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    end_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    end_arrowhead_triangle_height: float = 8.0
    end_arrowhead_triangle_width: float = 15.0
    end_shorten: float = 2.0
    start_arrowhead_bar_height: float = 8.0
    start_arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    start_arrowhead_sep: float = 4.0
    start_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    start_arrowhead_triangle_height: float = 8.0
    start_arrowhead_triangle_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            actions = [
                momapy.drawing.MoveTo(
                    momapy.geometry.Point(0, -self.start_arrowhead_bar_height / 2)
                ),
                momapy.drawing.LineTo(
                    momapy.geometry.Point(0, self.start_arrowhead_bar_height / 2)
                ),
            ]
            bar = momapy.drawing.Path(actions=actions)
            actions = [
                momapy.drawing.MoveTo(momapy.geometry.Point(0, 0)),
                momapy.drawing.LineTo(
                    momapy.geometry.Point(-self.start_arrowhead_sep, 0)
                ),
            ]
            sep = momapy.drawing.Path(actions=actions)
            triangle = momapy.meta.shapes.Triangle(
                position=momapy.geometry.Point(
                    -self.start_arrowhead_sep - self.start_arrowhead_triangle_width / 2,
                    0,
                ),
                width=self.start_arrowhead_triangle_width,
                height=self.start_arrowhead_triangle_height,
                direction=momapy.core.Direction.LEFT,
            )
            return [bar, sep] + triangle.drawing_elements()
        return []

    def _end_arrowhead_border_drawing_elements(self):
        actions = [
            momapy.drawing.MoveTo(
                momapy.geometry.Point(0, -self.end_arrowhead_bar_height / 2)
            ),
            momapy.drawing.LineTo(
                momapy.geometry.Point(0, self.end_arrowhead_bar_height / 2)
            ),
        ]
        bar = momapy.drawing.Path(actions=actions)
        actions = [
            momapy.drawing.MoveTo(momapy.geometry.Point(0, 0)),
            momapy.drawing.LineTo(momapy.geometry.Point(self.end_arrowhead_sep, 0)),
        ]
        sep = momapy.drawing.Path(actions=actions)
        triangle = momapy.meta.shapes.Triangle(
            position=momapy.geometry.Point(
                self.end_arrowhead_sep + self.end_arrowhead_triangle_width / 2,
                0,
            ),
            width=self.end_arrowhead_triangle_width,
            height=self.end_arrowhead_triangle_height,
            direction=momapy.core.Direction.RIGHT,
        )
        return [bar, sep] + triangle.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class HeterodimerAssociationLayout(_ReactionLayout, _ReactionNodeMixin):
    """Class for heterodimer association layouts"""

    _reaction_node_text: typing.ClassVar[str | None] = None
    end_arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    end_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    end_arrowhead_height: float = 8.0
    end_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    end_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    end_arrowhead_width: float = 15.0
    end_shorten: float = 2.0
    start_arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    start_arrowhead_height: float = 6.0
    start_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    start_arrowhead_width: float = 6.0
    start_shorten: float = 2.0

    def _end_arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.DoubleTriangle._end_arrowhead_border_drawing_elements(
            self
        )

    def _start_arrowhead_border_drawing_elements(self):
        shape = momapy.meta.shapes.Ellipse(
            position=momapy.geometry.Point(0, 0),
            width=self.start_arrowhead_width,
            height=self.start_arrowhead_height,
        )
        return shape.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class DissociationLayout(_ReactionLayout, _ReactionNodeMixin):
    """Class for dissociation layouts"""

    _reaction_node_text: typing.ClassVar[str | None] = None
    end_arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    end_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    end_arrowhead_height: float = 10.0
    end_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    end_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    end_arrowhead_sep: float = 2.0
    end_arrowhead_width: float = 10.0
    end_shorten: float = 2.0
    start_arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        if self.reversible:
            return momapy.meta.arcs.DoubleTriangle._start_arrowhead_border_drawing_elements(
                self
            )
        return []

    def _end_arrowhead_border_drawing_elements(self):
        outer_circle = momapy.meta.shapes.Ellipse(
            position=momapy.geometry.Point(0, 0),
            width=self.end_arrowhead_width,
            height=self.end_arrowhead_height,
        )
        inner_circle = momapy.meta.shapes.Ellipse(
            position=momapy.geometry.Point(0, 0),
            width=self.end_arrowhead_width - 2 * self.end_arrowhead_sep,
            height=self.end_arrowhead_height - 2 * self.end_arrowhead_sep,
        )
        return outer_circle.drawing_elements() + inner_circle.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class TruncationLayout(_ReactionLayout, _ReactionNodeMixin):
    """Class for truncation layouts"""

    _font_size_func: typing.ClassVar[typing.Callable | None] = (
        lambda obj: obj.reaction_node_width / 1.1
    )
    _font_weight: typing.ClassVar[momapy.drawing.FontWeight | float] = (
        momapy.drawing.FontWeight.BOLD
    )
    _reaction_node_text: typing.ClassVar[str | None] = "N"
    end_arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    end_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    end_arrowhead_height: float = 10.0
    end_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    end_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    end_arrowhead_stroke_dashoffset: float | None = None
    end_arrowhead_stroke_width: float | None = 1.0
    end_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    end_arrowhead_sep: float = 2.0
    end_arrowhead_width: float = 10.0
    end_shorten: float = 2.0
    start_arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_filter: (
        momapy.drawing.NoneValueType | momapy.drawing.Filter | None
    ) = None
    start_arrowhead_height: float = 8.0
    start_arrowhead_stroke: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    start_arrowhead_stroke_dasharray: (
        momapy.drawing.NoneValueType | tuple[float] | None
    ) = None
    start_arrowhead_stroke_dashoffset: float | None = None
    start_arrowhead_stroke_width: float | None = 1.0
    start_arrowhead_transform: (
        momapy.drawing.NoneValueType | tuple[momapy.geometry.Transformation] | None
    ) = None
    start_arrowhead_width: float = 15.0
    start_shorten: float = 2.0

    def _start_arrowhead_border_drawing_elements(self):
        return []

    def _end_arrowhead_border_drawing_elements(self):
        return []


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndGateLayout(
    _SimpleNodeMixin,
    momapy.sbgn.core._TextMixin,
    CellDesignerNode,
):
    """Class for and gate layouts"""

    _font_family: typing.ClassVar[str] = "Helvetica"
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width
    _text: typing.ClassVar[str] = "&"
    width: float = 15.0
    height: float = 15.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrGateLayout(
    _SimpleNodeMixin,
    momapy.sbgn.core._TextMixin,
    CellDesignerNode,
):
    """Class for or gate layouts"""

    _font_family: typing.ClassVar[str] = "Helvetica"
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    _text: typing.ClassVar[str] = "|"
    width: float = 15.0
    height: float = 15.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotGateLayout(
    _SimpleNodeMixin,
    momapy.sbgn.core._TextMixin,
    CellDesignerNode,
):
    """Class for not gate layouts"""

    _font_family: typing.ClassVar[str] = "Helvetica"
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    _text: typing.ClassVar[str] = "!"
    width: float = 15.0
    height: float = 15.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownGateLayout(
    _SimpleNodeMixin,
    momapy.sbgn.core._TextMixin,
    CellDesignerNode,
):
    """Class for unknown gate layouts"""

    _font_family: typing.ClassVar[str] = "Helvetica"
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    _text: typing.ClassVar[str] = "?"
    width: float = 15.0
    height: float = 15.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(CellDesignerSingleHeadedArc):
    """Class for logic arc layouts"""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerLayout(momapy.core.Layout):
    """Class for CellDesigner layouts"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerMap(momapy.core.Map):
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
