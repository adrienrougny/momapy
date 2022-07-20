from dataclasses import dataclass, field
from typing import TypeVar, Union, Optional

from momapy.sbgn.core import SBGNMap, SBGNModelElement, SBGNRole, SBGNModel
from momapy.core import Layout, ModelLayoutMapping
from momapy.builder import get_or_make_builder_cls, LayoutBuilder, ModelLayoutMappingBuilder
from momapy.arcs import PolyLine, Arrow, Circle, Bar, BarArrow, Diamond
from momapy.shapes import Rectangle, RectangleWithConnectors, RectangleWithRoundedCorners, Ellipse, RectangleWithCutCorners, Stadium, RectangleWithBottomRoundedCorners, CircleWithDiagonalBar, CircleWithConnectorsAndText, Hexagon, DoubleRectangleWithRoundedCorners, DoubleRectangleWithCutCorners
from momapy.coloring import Color, colors

############STATE VARIABLE AND UNIT OF INFORMATION###################
@dataclass(frozen=True)
class UndefinedVariable(SBGNModelElement):
    order: Optional[int] = None

@dataclass(frozen=True)
class StateVariable(SBGNModelElement):
    variable: Optional[Union[str, UndefinedVariable]] = None
    value: Optional[str] = None

@dataclass(frozen=True)
class UnitOfInformation(SBGNModelElement):
    value: Optional[str] = None
    prefix: Optional[str] = None

############SUBUNITS###################
@dataclass(frozen=True)
class Subunit(SBGNModelElement):
    label: Optional[str] = None

@dataclass(frozen=True)
class UnspecifiedEntitySubunit(Subunit):
    pass

@dataclass(frozen=True)
class MacromoleculeSubunit(Subunit):
    state_variables: frozenset[StateVariable] = field(default_factory=frozenset)
    units_of_information: frozenset[UnitOfInformation] = field(default_factory=frozenset)

@dataclass(frozen=True)
class NucleicAcidFeatureSubunit(Subunit):
    state_variables: frozenset[StateVariable] = field(default_factory=frozenset)
    units_of_information: frozenset[UnitOfInformation] = field(default_factory=frozenset)

@dataclass(frozen=True)
class SimpleChemicalSubunit(Subunit):
    state_variables: frozenset[StateVariable] = field(default_factory=frozenset)
    units_of_information: frozenset[UnitOfInformation] = field(default_factory=frozenset)

@dataclass(frozen=True)
class ComplexSubunit(Subunit):
    state_variables: frozenset[StateVariable] = field(default_factory=frozenset)
    units_of_information: frozenset[UnitOfInformation] = field(default_factory=frozenset)
    subunits: frozenset[Subunit] = field(default_factory=frozenset)

@dataclass(frozen=True)
class MultimerSubunit(ComplexSubunit):
    cardinality: Optional[int] = None

@dataclass(frozen=True)
class MacromoleculeMultimerSubunit(MultimerSubunit):
    pass

@dataclass(frozen=True)
class NucleicAcidFeatureMultimerSubunit(MultimerSubunit):
    pass

@dataclass(frozen=True)
class SimpleChemicalMultimerSubunit(MultimerSubunit):
    pass

@dataclass(frozen=True)
class ComplexMultimerSubunit(MultimerSubunit):
    pass

############COMPARTMENT###################
@dataclass(frozen=True)
class Compartment(SBGNModelElement):
    label: Optional[str] = None
    state_variables: frozenset[StateVariable] = field(default_factory=frozenset)
    units_of_information: frozenset[UnitOfInformation] = field(default_factory=frozenset)

############ENTITY POOLS###################
@dataclass(frozen=True)
class EntityPool(SBGNModelElement):
    compartment: Optional[Compartment] = None

@dataclass(frozen=True)
class EmptySet(EntityPool):
    pass

@dataclass(frozen=True)
class PerturbingAgent(EntityPool):
    label: Optional[str] = None

@dataclass(frozen=True)
class UnspecifiedEntity(EntityPool):
    label: Optional[str] = None

@dataclass(frozen=True)
class Macromolecule(EntityPool):
    label: Optional[str] = None
    state_variables: frozenset[StateVariable] = field(default_factory=frozenset)
    units_of_information: frozenset[UnitOfInformation] = field(default_factory=frozenset)

@dataclass(frozen=True)
class NucleicAcidFeature(EntityPool):
    label: Optional[str] = None
    state_variables: frozenset[StateVariable] = field(default_factory=frozenset)
    units_of_information: frozenset[UnitOfInformation] = field(default_factory=frozenset)

@dataclass(frozen=True)
class SimpleChemical(EntityPool):
    label: Optional[str] = None
    state_variables: frozenset[StateVariable] = field(default_factory=frozenset)
    units_of_information: frozenset[UnitOfInformation] = field(default_factory=frozenset)


@dataclass(frozen=True)
class Complex(EntityPool):
    label: Optional[str] = None
    state_variables: frozenset[StateVariable] = field(default_factory=frozenset)
    units_of_information: frozenset[UnitOfInformation] = field(default_factory=frozenset)
    subunits: frozenset[Subunit] = field(default_factory=frozenset)

@dataclass(frozen=True)
class Multimer(Complex):
    cardinality: Optional[int] = None

@dataclass(frozen=True)
class MacromoleculeMultimer(Multimer):
    pass

@dataclass(frozen=True)
class NucleicAcidFeatureMultimer(Multimer):
    pass

@dataclass(frozen=True)
class SimpleChemicalMultimer(Multimer):
    pass

@dataclass(frozen=True)
class ComplexMultimer(Multimer):
    pass

############SBGN ROLES###################
@dataclass(frozen=True)
class FluxRole(SBGNRole):
    element: EntityPool
    stoichiometry: Optional[int] = None

@dataclass(frozen=True)
class Reactant(FluxRole):
    pass

@dataclass(frozen=True)
class Product(FluxRole):
    pass

@dataclass(frozen=True)
class LogicalOperatorInput(SBGNRole):
    element: Union[EntityPool, "LogicalOperator"]

@dataclass(frozen=True)
class EquivalenceOperatorInput(SBGNRole):
    element: EntityPool

@dataclass(frozen=True)
class EquivalenceOperatorOutput(SBGNRole):
    element: EntityPool

@dataclass(frozen=True)
class TerminalReference(SBGNRole):
    element: Union[EntityPool, Compartment] = None

@dataclass(frozen=True)
class TagReference(SBGNRole):
    element: Union[EntityPool, Compartment] = None


############PROCESSES###################
@dataclass(frozen=True)
class Process(SBGNModelElement):
    pass

@dataclass(frozen=True)
class StoichiometricProcess(Process):
    reactants: frozenset[Reactant] = field(default_factory=frozenset)
    products: frozenset[Product] = field(default_factory=frozenset)

@dataclass(frozen=True)
class GenericProcess(StoichiometricProcess):
    pass

@dataclass(frozen=True)
class UncertainProcess(StoichiometricProcess):
    pass

@dataclass(frozen=True)
class Association(GenericProcess):
    pass

@dataclass(frozen=True)
class Dissociation(GenericProcess):
    pass

@dataclass(frozen=True)
class OmittedProcess(GenericProcess):
    pass

@dataclass(frozen=True)
class Phenotype(Process):
    label: Optional[str] = None

############OPERATORS###################
@dataclass(frozen=True)
class LogicalOperator(SBGNModelElement):
    inputs: frozenset[LogicalOperatorInput] = field(default_factory=frozenset)

@dataclass(frozen=True)
class OrOperator(LogicalOperator):
    pass

@dataclass(frozen=True)
class AndOperator(LogicalOperator):
    pass

@dataclass(frozen=True)
class NotOperator(LogicalOperator):
    pass

@dataclass(frozen=True)
class EquivalenceOperator(SBGNModelElement):
    inputs: frozenset[EquivalenceOperatorInput] = field(default_factory=frozenset)
    output: Optional[EquivalenceOperatorOutput] = None

############MODULATIONS###################
@dataclass(frozen=True)
class Modulation(SBGNModelElement):
    source: Optional[Union[EntityPool, LogicalOperator]] = None
    target: Optional[Process] = None

@dataclass(frozen=True)
class Inhibition(Modulation):
    pass

@dataclass(frozen=True)
class Stimulation(Modulation):
    pass

@dataclass(frozen=True)
class Catalysis(Stimulation):
    pass

@dataclass(frozen=True)
class NecessaryStimulation(Stimulation):
    pass

############SUBMAP###################
@dataclass(frozen=True)
class Terminal(SBGNModelElement):
    label: Optional[str] = None
    refers_to: Optional[TerminalReference] = None

@dataclass(frozen=True)
class Tag(SBGNModelElement):
    label: Optional[str] = None
    refers_to: Optional[TagReference] = None

@dataclass(frozen=True)
class Submap(SBGNModelElement):
    label: Optional[str] = None
    terminals: frozenset[Terminal] = field(default_factory=frozenset)

############MODELS###################
@dataclass(frozen=True)
class SBGNPDModel(SBGNModel):
    entity_pools: frozenset[EntityPool] = field(default_factory=frozenset)
    processes: frozenset[Process] = field(default_factory=frozenset)
    compartments: frozenset[Compartment] = field(default_factory=frozenset)
    modulations: frozenset[Modulation] = field(default_factory=frozenset)
    logical_operators: frozenset[LogicalOperator] = field(default_factory=frozenset)
    equivalence_operators: frozenset[EquivalenceOperator] = field(default_factory=frozenset)
    submaps: frozenset[Submap] = field(default_factory=frozenset)
    tags: frozenset[Tag] = field(default_factory=frozenset)

    def contains(self, other):
        return other.entity_pools.issubset(self.entity_pools) and \
                other.processes.issubset(self.processes) and \
                other.compartments.issubset(self.compartments) and \
                other.modulations.issubset(self.modulations) and \
                other.logical_operators.issubset(self.logical_operators) and \
                other.equivalence_operators.issubset(
                    self.equivalence_operators) and \
                other.submaps.issubset(self.submaps) and \
                other.tags.issubset(self.tags)

############MAP###################
@dataclass(frozen=True)
class SBGNPDMap(SBGNMap):
    model: Optional[SBGNPDModel] = None

############BUILDERS###################
SBGNPDModelBuilder = get_or_make_builder_cls(SBGNPDModel)

def sbgnpd_map_builder_new_model(self, *args, **kwargs):
    return SBGNPDModelBuilder(*args, **kwargs)

def sbgnpd_map_builder_new_layout(self, *args, **kwargs):
    return LayoutBuilder(*args, **kwargs)

def sbgnpd_map_builder_new_model_layout_mapping(self, *args, **kwargs):
    return ModelLayoutMappingBuilder(*args, **kwargs)

SBGNPDMapBuilder = get_or_make_builder_cls(
    SBGNPDMap,
    builder_namespace={
        "new_model": sbgnpd_map_builder_new_model,
        "new_layout": sbgnpd_map_builder_new_layout,
        "new_model_layout_mapping": sbgnpd_map_builder_new_model_layout_mapping
    }
)


############GLYPHS###################

@dataclass(frozen=True)
class CompartmentLayout(RectangleWithRoundedCorners):
    rounded_corners: float = 10
    stroke: Color = colors.black
    stroke_width: float = 4

@dataclass(frozen=True)
class MacromoleculeLayout(RectangleWithRoundedCorners):
    stroke: Color = colors.black
    stroke_width: float = 1
    rounded_corners: float = 10
    fill: Color = colors.white

@dataclass(frozen=True)
class MacromoleculeMultimerLayout(DoubleRectangleWithRoundedCorners):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white
    rounded_corners: float = 10
    offset: float = 2

@dataclass(frozen=True)
class SimpleChemicalLayout(Stadium):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white

@dataclass(frozen=True)
class StateVariableLayout(Stadium):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white

@dataclass(frozen=True)
class UnitOfInformationLayout(Rectangle):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white

@dataclass(frozen=True)
class ComplexLayout(RectangleWithCutCorners):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white
    cut_corners: float = 10

@dataclass(frozen=True)
class ComplexMultimerLayout(DoubleRectangleWithCutCorners):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white
    cut_corners: float = 10
    offset: float = 2

@dataclass(frozen=True)
class NucleicAcidFeatureLayout(RectangleWithBottomRoundedCorners):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white
    rounded_corners: float = 10

@dataclass(frozen=True)
class EmptySetLayout(CircleWithDiagonalBar):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white

@dataclass(frozen=True)
class AndOperatorLayout(CircleWithConnectorsAndText):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white
    text: str = "AND"

@dataclass(frozen=True)
class OrOperatorLayout(CircleWithConnectorsAndText):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white
    text: str = "OR"

@dataclass(frozen=True)
class NotOperatorLayout(CircleWithConnectorsAndText):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white
    text: str = "NOT"

@dataclass(frozen=True)
class EquivalenceOperatorLayout(CircleWithConnectorsAndText):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white
    text: str = "≡"

@dataclass(frozen=True)
class UnspecifiedEntityLayout(Ellipse):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white

@dataclass(frozen=True)
class GenericProcessLayout(RectangleWithConnectors):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white

@dataclass(frozen=True)
class PhenotypeLayout(Hexagon):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white

@dataclass(frozen=True)
class ConsumptionLayout(PolyLine):
    stroke: Color = colors.black
    stroke_width: float = 1

@dataclass(frozen=True)
class ProductionLayout(Arrow):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.black
    width: float = 12
    height: float = 12

@dataclass(frozen=True)
class StimulationLayout(Arrow):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white
    width: float = 12
    height: float = 12

@dataclass(frozen=True)
class CatalysisLayout(Circle):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white
    width: float = 11
    height: float = 11

@dataclass(frozen=True)
class InhibitionLayout(Bar):
    stroke: Color = colors.black
    stroke_width: float = 1
    width: float = 1.5
    height: float = 12
    shorten: float = 2

@dataclass(frozen=True)
class NecessaryStimulationLayout(BarArrow):
    stroke: Color = colors.black
    stroke_width: float = 1
    bar_width: float = 1
    bar_height: float = 12
    width: float = 12
    height: float = 12
    sep: float = 2

@dataclass(frozen=True)
class ModulationLayout(Diamond):
    stroke: Color = colors.black
    stroke_width: float = 1
    fill: Color = colors.white
    width: float = 12
    height: float = 12

@dataclass(frozen=True)
class LogicArcLayout(PolyLine):
    stroke: Color = colors.black
    stroke_width: float = 1

@dataclass(frozen=True)
class EquivalenceArcLayout(PolyLine):
    stroke: Color = colors.black
    stroke_width: float = 1
