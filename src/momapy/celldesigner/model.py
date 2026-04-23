"""Model classes for CellDesigner maps.

This module provides classes for representing the semantic model of a
CellDesigner pathway, including species, reactions, modifications, and
modulations.

Layout-model mapping catalogue
------------------------------

This section lists, for each model-element category in CellDesigner,
the shape of the corresponding key in
[LayoutModelMapping][momapy.core.LayoutModelMapping]. See
[LayoutModelMapping][momapy.core.LayoutModelMapping] for the general concepts
(singleton keys, frozenset keys, anchors).

Singleton keys (one layout element represents the model element):

| Model element | Layout element used as the key |
|---|---|
| [Compartment][momapy.celldesigner.Compartment] | The compartment alias layout (e.g. [OvalCompartmentLayout][momapy.celldesigner.OvalCompartmentLayout], [RectangleCompartmentLayout][momapy.celldesigner.RectangleCompartmentLayout], [CornerCompartmentLayout][momapy.celldesigner.CornerCompartmentLayout], [LineCompartmentLayout][momapy.celldesigner.LineCompartmentLayout]) |
| [Species][momapy.celldesigner.Species] and subclasses (e.g. [GenericProtein][momapy.celldesigner.GenericProtein], [Receptor][momapy.celldesigner.Receptor], [IonChannel][momapy.celldesigner.IonChannel], [Gene][momapy.celldesigner.Gene], [RNA][momapy.celldesigner.RNA], [Complex][momapy.celldesigner.Complex], [SimpleMolecule][momapy.celldesigner.SimpleMolecule], [Ion][momapy.celldesigner.Ion], [Drug][momapy.celldesigner.Drug], [Phenotype][momapy.celldesigner.Phenotype]) | The species alias layout (e.g. [GenericProteinLayout][momapy.celldesigner.GenericProteinLayout], [GeneLayout][momapy.celldesigner.GeneLayout]). Active species use the `*ActiveLayout` variant (e.g. [GenericProteinActiveLayout][momapy.celldesigner.GenericProteinActiveLayout]) |
| [Modification][momapy.celldesigner.Modification] | [ModificationLayout][momapy.celldesigner.ModificationLayout] |
| [StructuralState][momapy.celldesigner.StructuralState] | [StructuralStateLayout][momapy.celldesigner.StructuralStateLayout] |
| [Reactant][momapy.celldesigner.Reactant] | [ConsumptionLayout][momapy.celldesigner.ConsumptionLayout] |
| [Product][momapy.celldesigner.Product] | [ProductionLayout][momapy.celldesigner.ProductionLayout] |
| [BooleanLogicGateInput][momapy.celldesigner.BooleanLogicGateInput] | [LogicArcLayout][momapy.celldesigner.LogicArcLayout] |

Frozenset keys (a cluster of layout elements jointly represents the
model element; the **anchor** is the layout that stands for the cluster
on its own and must be passed as ``anchor=`` when calling
[add_mapping][momapy.core.LayoutModelMappingBuilder.add_mapping]):

| Model element | Members of the frozenset key | Anchor |
|---|---|---|
| [Reaction][momapy.celldesigner.Reaction] and subclasses (e.g. [StateTransition][momapy.celldesigner.StateTransition], [KnownTransitionOmitted][momapy.celldesigner.KnownTransitionOmitted], [UnknownTransition][momapy.celldesigner.UnknownTransition], [Transcription][momapy.celldesigner.Transcription], [Translation][momapy.celldesigner.Translation], [Transport][momapy.celldesigner.Transport], [HeterodimerAssociation][momapy.celldesigner.HeterodimerAssociation], [Dissociation][momapy.celldesigner.Dissociation], [Truncation][momapy.celldesigner.Truncation]) | The reaction layout (e.g. [StateTransitionLayout][momapy.celldesigner.StateTransitionLayout], [TranscriptionLayout][momapy.celldesigner.TranscriptionLayout], [DissociationLayout][momapy.celldesigner.DissociationLayout]) + every [ConsumptionLayout][momapy.celldesigner.ConsumptionLayout] and [ProductionLayout][momapy.celldesigner.ProductionLayout] attached to the reaction + every reactant and product target layout (the species alias layouts those arcs point to) | The reaction layout |
| [KnownOrUnknownModulation][momapy.celldesigner.KnownOrUnknownModulation] and subclasses (e.g. [Modulation][momapy.celldesigner.Modulation], [Catalysis][momapy.celldesigner.Catalysis], [Inhibition][momapy.celldesigner.Inhibition], [PhysicalStimulation][momapy.celldesigner.PhysicalStimulation], [Triggering][momapy.celldesigner.Triggering], [PositiveInfluence][momapy.celldesigner.PositiveInfluence], [NegativeInfluence][momapy.celldesigner.NegativeInfluence], [UnknownModulation][momapy.celldesigner.UnknownModulation] and its subclasses) | The modulation arc layout (e.g. [CatalysisLayout][momapy.celldesigner.CatalysisLayout], [InhibitionLayout][momapy.celldesigner.InhibitionLayout], [PositiveInfluenceLayout][momapy.celldesigner.PositiveInfluenceLayout]) + all layouts in the source cluster (resolved via the source's own frozenset key if it has one, for example when the source is a boolean gate, else the source layout itself) + all layouts in the target cluster (resolved the same way) | The modulation arc layout |
| [BooleanLogicGate][momapy.celldesigner.BooleanLogicGate] and subclasses (e.g. [AndGate][momapy.celldesigner.AndGate], [OrGate][momapy.celldesigner.OrGate], [NotGate][momapy.celldesigner.NotGate], [UnknownGate][momapy.celldesigner.UnknownGate]) | The gate layout (e.g. [AndGateLayout][momapy.celldesigner.AndGateLayout], [OrGateLayout][momapy.celldesigner.OrGateLayout]) + every [LogicArcLayout][momapy.celldesigner.LogicArcLayout] input + every target species alias layout those logic arcs point to | The gate layout |

Notes:

- [SpeciesTemplate][momapy.celldesigner.SpeciesTemplate] and subclasses (e.g.
  [GenericProteinTemplate][momapy.celldesigner.GenericProteinTemplate], [GeneTemplate][momapy.celldesigner.GeneTemplate]),
  [ModificationResidue][momapy.celldesigner.ModificationResidue], and [Region][momapy.celldesigner.Region] have no layout key:
  templates and their residues or regions are not drawn directly —
  only their [Species][momapy.celldesigner.Species] instances and the
  [Modification][momapy.celldesigner.Modification] or [StructuralState][momapy.celldesigner.StructuralState] objects they carry
  are.
- [KnownOrUnknownModulator][momapy.celldesigner.KnownOrUnknownModulator] and its subclasses (e.g.
  [Catalyzer][momapy.celldesigner.Catalyzer], [Inhibitor][momapy.celldesigner.Inhibitor],
  [PhysicalStimulator][momapy.celldesigner.PhysicalStimulator], [Trigger][momapy.celldesigner.Trigger]) are modifier
  references: the modulation cluster above is what is stored in the
  mapping. Modulator metadata lives on the source side of that
  cluster.
"""

import dataclasses
import enum

from momapy.celldesigner.elements import CellDesignerModelElement
from momapy.sbml.model import Compartment as SBMLCompartment
from momapy.sbml.model import Species as SBMLSpecies
from momapy.sbml.model import SpeciesReference
from momapy.sbml.model import ModifierSpeciesReference
from momapy.sbml.model import Reaction as SBMLReaction
from momapy.sbml.model import SBMLModel


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModificationResidue(CellDesignerModelElement):
    """Modification residue for protein post-translational modifications.

    Residues represent specific amino acid positions that can be modified.

    Attributes:
        name: Name of the residue (e.g., amino acid name).
        order: Sequential order of the residue in the protein.
    """

    name: str | None = None
    order: int | None = None


class ModificationState(enum.Enum):
    """Enumeration of protein modification states.

    Represents common post-translational modification types with their
    standard abbreviations.
    """

    PHOSPHORYLATED = "P"
    ACETYLATED = "Ac"
    UBIQUITINATED = "Ub"
    METHYLATED = "M"
    HYDROXYLATED = "OH"
    GLYCOSYLATED = "G"
    MYRISTOYLATED = "My"
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
class Compartment(SBMLCompartment, CellDesignerModelElement):
    """Class for compartments"""

    pass


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class Species(SBMLSpecies, CellDesignerModelElement):
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
class Reactant(SpeciesReference, CellDesignerModelElement):
    """Class for reactants"""

    base: bool = dataclasses.field(
        default=False,
        metadata={"description": "Whether the reactant is a base reactant or not"},
    )  # TODO: no default?


@dataclasses.dataclass(frozen=True, kw_only=True)
class Product(SpeciesReference, CellDesignerModelElement):
    """Class for products"""

    base: bool = dataclasses.field(
        default=False,
        metadata={"description": "Whether the product is a base product or not"},
    )  # TODO: no default?


@dataclasses.dataclass(frozen=True, kw_only=True)
class BooleanLogicGateInput(CellDesignerModelElement):
    """Class for boolean logic gate inputs"""

    element: Species = dataclasses.field(
        metadata={"description": "The species providing the input"},
    )


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class BooleanLogicGate(CellDesignerModelElement):
    """Base class for Boolean logic gates"""

    inputs: frozenset[BooleanLogicGateInput] = dataclasses.field(
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
class KnownOrUnknownModulator(ModifierSpeciesReference, CellDesignerModelElement):
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
class Reaction(SBMLReaction, CellDesignerModelElement):
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
class CellDesignerModel(SBMLModel):
    """CellDesigner model container.

    Aggregates all elements of a CellDesigner pathway model including
    species, reactions, templates, and modulations.

    Attributes:
        species_templates: Set of species templates defining reusable structures.
        boolean_logic_gates: Set of Boolean logic gates for combinatorial regulation.
        modulations: Set of modulations representing regulatory influences.
    """

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

    def is_submodel(self, other: "CellDesignerModel") -> bool:
        """Check if another model is a submodel of this model.

        Args:
            other: Another CellDesigner model to compare against.

        Returns:
            True if other is a submodel of this model, False otherwise.
        """
        return (
            self.compartments.issubset(other.compartments)
            and self.species.issubset(other.species)
            and self.reactions.issubset(other.reactions)
            and self.species_templates.issubset(other.species_templates)
            and self.boolean_logic_gates.issubset(other.boolean_logic_gates)
            and self.modulations.issubset(other.modulations)
        )


__all__ = [
    "ModificationResidue",
    "ModificationState",
    "Region",
    "ModificationSite",
    "CodingRegion",
    "RegulatoryRegion",
    "TranscriptionStartingSiteL",
    "TranscriptionStartingSiteR",
    "ProteinBindingDomain",
    "SpeciesTemplate",
    "ProteinTemplate",
    "GenericProteinTemplate",
    "TruncatedProteinTemplate",
    "ReceptorTemplate",
    "IonChannelTemplate",
    "GeneTemplate",
    "RNATemplate",
    "AntisenseRNATemplate",
    "Modification",
    "StructuralState",
    "Compartment",
    "Species",
    "Protein",
    "GenericProtein",
    "TruncatedProtein",
    "Receptor",
    "IonChannel",
    "Gene",
    "RNA",
    "AntisenseRNA",
    "Phenotype",
    "Ion",
    "SimpleMolecule",
    "Drug",
    "Unknown",
    "Complex",
    "Degraded",
    "Reactant",
    "Product",
    "BooleanLogicGateInput",
    "BooleanLogicGate",
    "AndGate",
    "OrGate",
    "NotGate",
    "UnknownGate",
    "KnownOrUnknownModulator",
    "Modulator",
    "UnknownModulator",
    "Inhibitor",
    "PhysicalStimulator",
    "Catalyzer",
    "Trigger",
    "UnknownCatalyzer",
    "UnknownInhibitor",
    "Reaction",
    "StateTransition",
    "KnownTransitionOmitted",
    "UnknownTransition",
    "Transcription",
    "Translation",
    "Transport",
    "HeterodimerAssociation",
    "Dissociation",
    "Truncation",
    "KnownOrUnknownModulation",
    "Modulation",
    "Catalysis",
    "Inhibition",
    "PhysicalStimulation",
    "Triggering",
    "PositiveInfluence",
    "NegativeInfluence",
    "UnknownModulation",
    "UnknownCatalysis",
    "UnknownInhibition",
    "UnknownPositiveInfluence",
    "UnknownNegativeInfluence",
    "UnknownPhysicalStimulation",
    "UnknownTriggering",
    "CellDesignerModel",
]
