from dataclasses import dataclass, field
from typing import TypeVar, Union, Optional

from momapy.core import Map, ModelElement, Model, Layout, ModelLayoutMapping

############Annotation###################
@dataclass(frozen=True)
class Annotation(ModelElement):
    pass

############SBGN MODEL ELEMENT###################
@dataclass(frozen=True)
class SBGNModelElement(ModelElement):
    annotations: frozenset[Annotation] = field(default_factory=frozenset)

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


# SPECIALIZED SBGN MODEL ELEMENTS

@dataclass(frozen=True)
class StatefulSBGNModelElement(SBGNModelElement):
    state_variables: frozenset[StateVariable] = field(default_factory=frozenset)
    units_of_information: frozenset[UnitOfInformation] = field(default_factory=frozenset)

@dataclass(frozen=True)
class StatelessSBGNModelElement(SBGNModelElement):
    pass

@dataclass(frozen=True)
class LabeledSBGNModelElement(SBGNModelElement):
    label: str = None

############SUBUNITS###################
@dataclass(frozen=True)
class Subunit(SBGNModelElement):
    pass

@dataclass(frozen=True)
class MacromoleculeSubunit(LabeledSBGNModelElement, StatefulSBGNModelElement, Subunit):
    pass

@dataclass(frozen=True)
class NucleicAcidFeatureSubunit(LabeledSBGNModelElement, StatefulSBGNModelElement, Subunit):
    pass

@dataclass(frozen=True)
class SimpleChemicalSubunit(LabeledSBGNModelElement, Subunit):
    pass

@dataclass(frozen=True)
class ComplexSubunit(LabeledSBGNModelElement, StatefulSBGNModelElement, Subunit):
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
class Compartment(LabeledSBGNModelElement, StatefulSBGNModelElement):
    pass

############ENTITY POOLS###################
@dataclass(frozen=True)
class EntityPool(SBGNModelElement):
    compartment: Optional[Compartment] = None

@dataclass(frozen=True)
class EmptySet(EntityPool):
    pass

@dataclass(frozen=True)
class PerturbingAgent(LabeledSBGNModelElement, EntityPool):
    pass

@dataclass(frozen=True)
class UnspecifiedEntity(LabeledSBGNModelElement, EntityPool):
    pass

@dataclass(frozen=True)
class Macromolecule(LabeledSBGNModelElement, StatefulSBGNModelElement, EntityPool):
    pass

@dataclass(frozen=True)
class NucleicAcidFeature(LabeledSBGNModelElement, StatefulSBGNModelElement, EntityPool):
    pass

@dataclass(frozen=True)
class SimpleChemical(LabeledSBGNModelElement, EntityPool):
    pass

@dataclass(frozen=True)
class Complex(LabeledSBGNModelElement, StatefulSBGNModelElement, EntityPool):
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
class SBGNRole(SBGNModelElement):
    element: Optional[SBGNModelElement] = None

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

############PROCESSES###################
@dataclass(frozen=True)
class Process(SBGNModelElement):
    pass

@dataclass(frozen=True)
class GenericProcess(Process):
    reactants: frozenset[Reactant] = field(default_factory=frozenset)
    products: frozenset[Product] = field(default_factory=frozenset)

@dataclass(frozen=True)
class UncertainProcess(GenericProcess):
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
class Phenotype(LabeledSBGNModelElement, Process):
    pass

############OPERATORS###################
TLogicalOperatorInput = TypeVar("TLogicalOperatorInput", EntityPool, "LogicalOperator")

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

@dataclass(frozen=True)
class EquivalenceOperator(SBGNModelElement):
    inputs: frozenset[EntityPool] = field(default_factory=frozenset)

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
class Tag(LabeledSBGNModelElement):
    refers_to: Optional[Union[EntityPool, Compartment]] = None

@dataclass(frozen=True)
class Submap(LabeledSBGNModelElement):
    tags: frozenset[Tag] = field(default_factory=frozenset)


############MODEL###################
@dataclass(frozen=True)
class SBGNModel(Model):
    entity_pools: frozenset[EntityPool] = field(default_factory=frozenset)
    processes: frozenset[Process] = field(default_factory=frozenset)
    compartments: frozenset[Compartment] = field(default_factory=frozenset)
    modulations: frozenset[Modulation] = field(default_factory=frozenset)
    logical_operators: frozenset[LogicalOperator] = field(default_factory=frozenset)
    equivalence_operators: frozenset[EquivalenceOperator] = field(default_factory=frozenset)
    submaps: frozenset[Submap] = field(default_factory=frozenset)

############MAP###################
@dataclass(frozen=True)
class SBGNMap(Map):
    model: Optional[SBGNModel] = None
    layout: Optional[Layout] = None
    model_layout_mapping: Optional[ModelLayoutMapping] = None
