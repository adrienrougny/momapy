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
    """

    name: str | None = dataclasses.field(
        default=None, metadata={"description": "The name of the residue"}
    )
    order: int | None = dataclasses.field(
        default=None,
        metadata={"description": "The sequential order of the residue"},
    )


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
    """Region of a gene, RNA, or antisense RNA template.

    Regions delimit a part of a nucleic acid template that can carry a name and an active state.
    """

    name: str | None = dataclasses.field(
        default=None, metadata={"description": "The name of the region"}
    )
    active: bool = dataclasses.field(
        default=False,
        metadata={"description": "Whether the region is active or not"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModificationSite(Region):
    """Modification site region.

    Marks a region of a template where a modification can occur.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CodingRegion(Region):
    """Coding region.

    Marks a region of a nucleic acid template that codes for a product.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class RegulatoryRegion(Region):
    """Regulatory region.

    Marks a region of a nucleic acid template that regulates transcription.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TranscriptionStartingSiteL(Region):
    """Left transcription starting site.

    Marks the left-hand transcription starting site of a gene template.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TranscriptionStartingSiteR(Region):
    """Right transcription starting site.

    Marks the right-hand transcription starting site of a gene template.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProteinBindingDomain(Region):
    """Protein binding domain region.

    Marks a region of a nucleic acid template where a protein binds.
    """

    pass


# abstract
# changed name from reference to template to distinguish from SBML's
# species reference which has a different meaning (reference to a species)
@dataclasses.dataclass(frozen=True, kw_only=True)
class SpeciesTemplate(CellDesignerModelElement):
    """Base class for species templates.

    Species templates describe the reusable structure shared by the species instances that derive from them.
    """

    name: str = dataclasses.field(
        metadata={"description": "The name of the species template"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProteinTemplate(SpeciesTemplate):
    """Base class for protein templates.

    Protein templates describe the modification residues shared by the protein species deriving from them.
    """

    modification_residues: frozenset[ModificationResidue] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The modification residues of the protein template"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProteinTemplate(ProteinTemplate):
    """Template for generic proteins.

    Describes the structure shared by generic protein species.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TruncatedProteinTemplate(ProteinTemplate):
    """Template for truncated proteins.

    Describes the structure shared by truncated protein species.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ReceptorTemplate(ProteinTemplate):
    """Template for receptors.

    Describes the structure shared by receptor species.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class IonChannelTemplate(ProteinTemplate):
    """Template for ion channels.

    Describes the structure shared by ion channel species.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class GeneTemplate(SpeciesTemplate):
    """Template for genes.

    Describes the structure, including its regions, shared by gene species.
    """

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
    """Template for RNAs.

    Describes the structure, including its regions, shared by RNA species.
    """

    regions: frozenset[ModificationSite | CodingRegion | ProteinBindingDomain] = (
        dataclasses.field(
            default_factory=frozenset,
            metadata={"description": "The regions of the RNA template"},
        )
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class AntisenseRNATemplate(SpeciesTemplate):
    """Template for antisense RNAs.

    Describes the structure, including its regions, shared by antisense RNA species.
    """

    regions: frozenset[ModificationSite | CodingRegion | ProteinBindingDomain] = (
        dataclasses.field(
            default_factory=frozenset,
            metadata={"description": "The regions of the antisense RNA template"},
        )
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Modification(CellDesignerModelElement):
    """Post-translational modification carried by a species.

    A modification associates a modification state with a residue or modification site of the species.
    """

    residue: ModificationResidue | ModificationSite | None = dataclasses.field(
        default=None,
        metadata={"description": "The residue of the modification"},
    )
    state: ModificationState | None = dataclasses.field(
        default=None, metadata={"description": "The state of the modification"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class StructuralState(CellDesignerModelElement):
    """Structural state carried by a species or complex.

    A structural state holds a free-text value describing the conformation or state of the species.
    """

    value: str | None = dataclasses.field(
        default=None,
        metadata={"description": "The value of the structural state"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Compartment(SBMLCompartment, CellDesignerModelElement):
    """Compartment in a CellDesigner map.

    Compartments represent distinct spatial regions where species are located.
    """

    pass


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class Species(SBMLSpecies, CellDesignerModelElement):
    """Base class for species.

    Species represent the biological entities that participate in reactions and modulations.
    """

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
    """Base class for proteins.

    Proteins are species defined by a protein template and carrying modifications and structural states.
    """

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
    """Generic protein species.

    A protein with no specialized role, defined by a generic protein template.
    """

    template: GenericProteinTemplate = dataclasses.field(
        metadata={"description": "The template of the generic protein"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TruncatedProtein(Protein):
    """Truncated protein species.

    A protein missing part of its sequence, defined by a truncated protein template.
    """

    template: TruncatedProteinTemplate = dataclasses.field(
        metadata={"description": "The template of the truncated protein"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Receptor(Protein):
    """Receptor species.

    A protein acting as a receptor, defined by a receptor template.
    """

    template: ReceptorTemplate = dataclasses.field(
        metadata={"description": "The template of the receptor"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class IonChannel(Protein):
    """Ion channel species.

    A protein acting as an ion channel, defined by an ion channel template.
    """

    template: IonChannelTemplate = dataclasses.field(
        metadata={"description": "The template of the ion channel"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Gene(Species):
    """Gene species.

    A gene defined by a gene template and carrying modifications.
    """

    template: GeneTemplate = dataclasses.field(
        metadata={"description": "The template of the gene"}
    )
    modifications: frozenset[Modification] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class RNA(Species):
    """RNA species.

    An RNA defined by an RNA template and carrying modifications.
    """

    template: RNATemplate = dataclasses.field(
        metadata={"description": "The template of the RNA"}
    )
    modifications: frozenset[Modification] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class AntisenseRNA(Species):
    """Antisense RNA species.

    An antisense RNA defined by an antisense RNA template and carrying modifications.
    """

    template: AntisenseRNATemplate = dataclasses.field(
        metadata={"description": "The template of the antisense RNA"}
    )
    modifications: frozenset[Modification] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Phenotype(Species):
    """Phenotype species.

    Represents a biological phenotype or process outcome.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Ion(Species):
    """Ion species.

    Represents an ion participating in the map.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleMolecule(Species):
    """Simple molecule species.

    Represents a small, structurally simple chemical species.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Drug(Species):
    """Drug species.

    Represents a drug acting on the system.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Unknown(Species):
    """Unknown species.

    Used when the class of the species is unknown or unspecified.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Complex(Species):
    """Complex species.

    A complex is a species made of subunits and carrying its own structural states.
    """

    structural_states: frozenset[StructuralState] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The structural states of the complex"},
    )
    subunits: frozenset[Species] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The subunits of the complex"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Reactant(SpeciesReference, CellDesignerModelElement):
    """Reactant of a reaction.

    A reactant references a species consumed by a reaction, optionally as a base reactant.
    """

    base: bool = dataclasses.field(
        default=False,
        metadata={"description": "Whether the reactant is a base reactant or not"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Product(SpeciesReference, CellDesignerModelElement):
    """Product of a reaction.

    A product references a species produced by a reaction, optionally as a base product.
    """

    base: bool = dataclasses.field(
        default=False,
        metadata={"description": "Whether the product is a base product or not"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class BooleanLogicGateInput(CellDesignerModelElement):
    """Input of a Boolean logic gate.

    A gate input references the species providing one of the gate's operands.
    """

    referred_element: Species = dataclasses.field(
        metadata={"description": "The species providing the input"},
    )


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class BooleanLogicGate(CellDesignerModelElement):
    """Base class for Boolean logic gates.

    Boolean logic gates combine several species inputs into a single logical modulation source.
    """

    inputs: frozenset[BooleanLogicGateInput] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The inputs of the Boolean logic gate"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndGate(BooleanLogicGate):
    """Boolean AND gate.

    Outputs true when all of its inputs are active.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrGate(BooleanLogicGate):
    """Boolean OR gate.

    Outputs true when at least one of its inputs is active.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotGate(BooleanLogicGate):
    """Boolean NOT gate.

    Outputs the negation of its input.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownGate(BooleanLogicGate):
    """Boolean gate of unknown type.

    Used when the logical operation of the gate is unknown or unspecified.
    """

    pass


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class KnownOrUnknownModulator(ModifierSpeciesReference, CellDesignerModelElement):
    """Base class for known or unknown modulators.

    A modulator is a reaction modifier that references the species or Boolean gate exerting the influence.
    """

    # redefined because can be BooleanLogicGate
    referred_element: Species | BooleanLogicGate = dataclasses.field(
        metadata={"description": "The species the modifier refers to"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Modulator(KnownOrUnknownModulator):
    """Modulator with a known effect.

    Base class for reaction modifiers whose regulatory effect is known.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownModulator(KnownOrUnknownModulator):
    """Modulator with an unknown effect.

    Base class for reaction modifiers whose regulatory effect is unknown.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Inhibitor(Modulator):
    """Inhibitor modulator.

    A modulator that inhibits its target reaction.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhysicalStimulator(Modulator):
    """Physical stimulator modulator.

    A modulator that physically stimulates its target reaction.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Catalyzer(PhysicalStimulator):
    """Catalyzer modulator.

    A modulator that catalyzes its target reaction.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Trigger(Modulator):
    """Trigger modulator.

    A modulator that triggers its target reaction.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownCatalyzer(UnknownModulator):
    """Catalyzer modulator with an unknown effect.

    A modulator presumed to catalyze its target reaction with an unknown effect.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInhibitor(UnknownModulator):
    """Inhibitor modulator with an unknown effect.

    A modulator presumed to inhibit its target reaction with an unknown effect.
    """

    pass


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class Reaction(SBMLReaction, CellDesignerModelElement):
    """Base class for reactions.

    CellDesigner's degraded glyph (a ``<species class="DEGRADED">`` used
    on either side of a reaction to denote unspecified external flux)
    is *not* represented as a member of ``reactants`` or ``products``.
    Instead, it is encoded as the boolean flags ``has_external_source``
    (a degraded reactant) and ``has_external_sink`` (a degraded product).
    The corresponding glyph lives only in the layout (``DegradedLayout``
    / ``DegradedActiveLayout``); the model carries no peer species for
    it. The writer reconstructs the degraded SBML/XML elements from the
    layout at write time.
    """

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
    has_external_source: bool = dataclasses.field(
        default=False,
        metadata={
            "description": (
                "Whether the reaction has an unspecified external source "
                "(a Degraded reactant in CellDesigner)."
            )
        },
    )
    has_external_sink: bool = dataclasses.field(
        default=False,
        metadata={
            "description": (
                "Whether the reaction has an unspecified external sink "
                "(a Degraded product in CellDesigner)."
            )
        },
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateTransition(Reaction):
    """State transition reaction.

    Represents a transition of a species from one state to another.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class KnownTransitionOmitted(Reaction):
    """Known transition omitted reaction.

    Represents a known transition whose intermediate steps are deliberately omitted.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownTransition(Reaction):
    """Unknown transition reaction.

    Represents a transition whose mechanism is unknown.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Transcription(Reaction):
    """Transcription reaction.

    Represents the transcription of a gene into RNA.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Translation(Reaction):
    """Translation reaction.

    Represents the translation of RNA into protein.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Transport(Reaction):
    """Transport reaction.

    Represents the transport of a species between compartments.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class HeterodimerAssociation(Reaction):
    """Heterodimer association reaction.

    Represents the association of species into a heterodimer or complex.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Dissociation(Reaction):
    """Dissociation reaction.

    Represents the dissociation of a complex into its components.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Truncation(Reaction):
    """Truncation reaction.

    Represents the truncation of a species into a shorter form.
    """

    pass


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class KnownOrUnknownModulation(CellDesignerModelElement):
    """Base class for known or unknown modulations.

    A modulation represents a regulatory influence exerted by a source species or Boolean gate on a target species.
    """

    source: Species | BooleanLogicGate = dataclasses.field(
        metadata={"description": "The source of the influence"}
    )
    target: Species | None = dataclasses.field(
        metadata={"description": "The target of the influence"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Modulation(KnownOrUnknownModulation):
    """Modulation with a known effect.

    Base class for modulations whose regulatory effect is known.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Catalysis(Modulation):
    """Catalysis modulation.

    Represents the catalysis of the target by the source.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Inhibition(Modulation):
    """Inhibition modulation.

    Represents the inhibition of the target by the source.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhysicalStimulation(Modulation):
    """Physical stimulation modulation.

    Represents the physical stimulation of the target by the source.
    """

    pass


# need to be a different name than the modifier Trigger
@dataclasses.dataclass(frozen=True, kw_only=True)
class Triggering(Modulation):
    """Triggering modulation.

    Represents the triggering of the target by the source.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluence(Modulation):
    """Positive influence modulation.

    Represents a positive influence of the source on the target.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NegativeInfluence(Modulation):
    """Negative influence modulation.

    Represents a negative influence of the source on the target.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownModulation(KnownOrUnknownModulation):
    """Modulation with an unknown effect.

    Base class for modulations whose regulatory effect is unknown.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownCatalysis(UnknownModulation):
    """Catalysis modulation with an unknown effect.

    Represents a presumed catalysis of the target by the source with an unknown effect.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInhibition(UnknownModulation):
    """Inhibition modulation with an unknown effect.

    Represents a presumed inhibition of the target by the source with an unknown effect.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownPositiveInfluence(UnknownModulation):
    """Positive influence modulation with an unknown effect.

    Represents a presumed positive influence of the source on the target with an unknown effect.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownNegativeInfluence(UnknownModulation):
    """Negative influence modulation with an unknown effect.

    Represents a presumed negative influence of the source on the target with an unknown effect.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownPhysicalStimulation(UnknownModulation):
    """Physical stimulation modulation with an unknown effect.

    Represents a presumed physical stimulation of the target by the source with an unknown effect.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownTriggering(UnknownModulation):
    """Triggering modulation with an unknown effect.

    Represents a presumed triggering of the target by the source with an unknown effect.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class CellDesignerModel(SBMLModel):
    """CellDesigner model container.

    Aggregates all elements of a CellDesigner pathway model including
    species, reactions, templates, and modulations.
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
