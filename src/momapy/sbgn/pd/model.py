"""Model classes for SBGN Process Description (PD) maps."""

import dataclasses
import sys
import typing

from momapy.sbgn.elements import (
    SBGNAuxiliaryUnit,
    SBGNModelElement,
    SBGNRole,
)
from momapy.sbgn.model import SBGNModel


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateVariable(SBGNAuxiliaryUnit):
    """Class for state variables"""

    variable: str | None = dataclasses.field(
        default=None, metadata={"description": "The variable of the state variable"}
    )
    value: str | None = dataclasses.field(
        default=None, metadata={"description": "The value of the state variable"}
    )
    order: int | None = dataclasses.field(
        default=None,
        metadata={
            "description": "The order of the state variable. This is used to distinguish between two or more state variables with undefined variable (i.e., set to `None`)"
        },
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformation(SBGNAuxiliaryUnit):
    """Class for units of information"""

    value: str = dataclasses.field(
        metadata={"description": "The value of the unit of information"},
    )
    prefix: str | None = dataclasses.field(
        default=None,
        metadata={"description": "The prefix of the unit of information"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Subunit(SBGNAuxiliaryUnit):
    """Base class for subunits"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the subunit"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntitySubunit(Subunit):
    """Class for unspecified entity subunits"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeSubunit(Subunit):
    """Class for macromolecule subunits"""

    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The state variables of the macromolecule subunit"},
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset,
        metadata={
            "description": "The units of information of the macromolecule subunit"
        },
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureSubunit(Subunit):
    """Class for nucleic acid feature subunits"""

    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset,
        metadata={
            "description": "The state variables of the nucleic acid feature subunit"
        },
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset,
        metadata={
            "description": "The units of information of the nucleic acid feature subunit"
        },
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalSubunit(Subunit):
    """Class for simple chemical subunits"""

    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The state variables of the simple chemical subunit"},
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset,
        metadata={
            "description": "The units of information of the simple chemical subunit"
        },
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexSubunit(Subunit):
    """Class for complex subunits"""

    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The state variables of the complex subunit"},
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The units of information of the complex subunit"},
    )
    subunits: frozenset[Subunit] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The subunits of the complex subunit"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MultimerSubunit(ComplexSubunit):
    """Base class for multimer subunits"""

    cardinality: int | None = dataclasses.field(
        default=None,
        metadata={"description": "The cardinality of the multimer subunit"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimerSubunit(MultimerSubunit):
    """Class for macromolecule multimer subunits"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureMultimerSubunit(MultimerSubunit):
    """Class for nucleic acid feature multimer subunits"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimerSubunit(MultimerSubunit):
    """Class for simple chemical multimer subunits"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexMultimerSubunit(MultimerSubunit):
    """Class for complex subunits"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Compartment(SBGNModelElement):
    """Class for compartments"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the compartment"}
    )
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The state variables of the compartment"},
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The units of information of the compartment"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EntityPool(SBGNModelElement):
    """Base class for entity pools"""

    compartment: Compartment | None = dataclasses.field(
        default=None, metadata={"description": "The compartment of the entity pool"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EmptySet(EntityPool):
    """Class for empty sets"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbingAgent(EntityPool):
    """Class for perturbing agents"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the perturbing agent"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntity(EntityPool):
    """Class for unspecified entities"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the unspecified entity"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Macromolecule(EntityPool):
    """Class for macromolecules"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the macromolecule"}
    )
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The state variables of the macromolecule"},
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The units of information of the macromolecule"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeature(EntityPool):
    """Class for nucleic acid features"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the nucleic acid feature"}
    )
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The state variables of the nucleic acid feature"},
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset,
        metadata={
            "description": "The units of information of the nucleic acid feature"
        },
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemical(EntityPool):
    """Class for simple chemical"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the simple chemical"}
    )
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The state variables of the simple chemical"},
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The units of information of the simple chemical"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Complex(EntityPool):
    """Class for complexes"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the complex"}
    )
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The state variables of the complex"},
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The units of information of the complex"},
    )
    subunits: frozenset[Subunit] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The subunits of the complex"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Multimer(Complex):
    """Base class for multimers"""

    cardinality: int | None = dataclasses.field(
        default=None, metadata={"description": "The cardinality of the multimer"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimer(Multimer):
    """Class for macromolecule multimers"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureMultimer(Multimer):
    """Class for nucleic acid feature multimers"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimer(Multimer):
    """Class for simple chemical multimers"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexMultimer(Multimer):
    """Class for complex multimers"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class FluxRole(SBGNRole):
    """Base class for flux roles"""

    element: EntityPool = dataclasses.field(
        metadata={"description": "The entity pool of the flux role"}
    )
    stoichiometry: float | None = dataclasses.field(
        default=None, metadata={"description": "The stoichiometry of the flux role"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Reactant(FluxRole):
    """Class for reactants"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Product(FluxRole):
    """Class for products"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperatorInput(SBGNRole):
    """Class for inputs of logical operators"""

    element: typing.Union[
        EntityPool,
        typing.ForwardRef("LogicalOperator", module=sys.modules[__name__]),
    ] = dataclasses.field(
        metadata={"description": "The element of the logical operator input"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorInput(SBGNRole):
    """Class for inputs of equivalence operators"""

    element: EntityPool = dataclasses.field(
        metadata={"description": "The element of the equivalence operator input"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorOutput(SBGNRole):
    """Class for outputs of equivalence operators"""

    element: EntityPool = dataclasses.field(
        metadata={"description": "The element of the equivalence operator output"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Process(SBGNModelElement):
    """Base class for processes"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class StoichiometricProcess(Process):
    """Base class for stoichiometric processes"""

    reactants: frozenset[Reactant] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The reactants of the stoichiometric process"},
    )
    products: frozenset[Product] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The products of the stoichiometric process"},
    )
    reversible: bool = dataclasses.field(
        default=False,
        metadata={
            "description": "Whether the stoichiometric process is reversible or not"
        },
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProcess(StoichiometricProcess):
    """Class for generic processes"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UncertainProcess(StoichiometricProcess):
    """Class for uncertain processes"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Association(GenericProcess):
    """Class for associations"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Dissociation(GenericProcess):
    """Class for dissociations"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class OmittedProcess(GenericProcess):
    """Class for omitted processes"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Phenotype(Process):
    """Class for phenotypes"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the phenotype"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperator(SBGNModelElement):
    """Class for logical operators"""

    inputs: frozenset[LogicalOperatorInput] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The inputs of the logical operator"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrOperator(LogicalOperator):
    """Class for or operators"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndOperator(LogicalOperator):
    """Class for and operators"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotOperator(LogicalOperator):
    """Class for not operators"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperator(SBGNModelElement):
    """Class for equivalence operators"""

    inputs: frozenset[EquivalenceOperatorInput] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The inputs of the equivalence operator"},
    )
    output: EquivalenceOperatorOutput | None = dataclasses.field(
        default=None, metadata={"description": "The output of the equivalence operator"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Modulation(SBGNModelElement):
    """Class for modulations"""

    source: EntityPool | LogicalOperator = dataclasses.field(
        metadata={"description": "The source of the modulation"}
    )
    target: Process = dataclasses.field(
        metadata={"description": "The target of the modulation"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Inhibition(Modulation):
    """Class for inhibitions"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Stimulation(Modulation):
    """Class for stimulations"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Catalysis(Stimulation):
    """Class for catalyses"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulation(Stimulation):
    """Class for necessary stimulations"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagReference(SBGNRole):
    """Class for tag references"""

    element: EntityPool | Compartment = dataclasses.field(
        metadata={"description": "The element of the tag reference"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Tag(SBGNModelElement):
    """Class for tags"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the tag"}
    )
    reference: TagReference | None = dataclasses.field(
        default=None, metadata={"description": "The reference of the tag"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalReference(SBGNRole):
    """Class for terminal references"""

    element: EntityPool | Compartment = dataclasses.field(
        metadata={"description": "The element of the terminal reference"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Terminal(SBGNAuxiliaryUnit):
    """Class for terminals"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the terminal"}
    )
    reference: TerminalReference | None = dataclasses.field(
        default=None, metadata={"description": "The reference of the terminal"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Submap(SBGNModelElement):
    """Class for submaps"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the submap"}
    )
    terminals: frozenset[Terminal] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The terminals of the submap"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDModel(SBGNModel):
    """Class for SBGN-PD models"""

    entity_pools: frozenset[EntityPool] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The entity pools of the SBGN-PD model"},
    )
    processes: frozenset[Process] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The processes of the SBGN-PD model"},
    )
    compartments: frozenset[Compartment] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The compartments of the SBGN-PD model"},
    )
    modulations: frozenset[Modulation] = dataclasses.field(
        metadata={"description": "The modulations of the SBGN-PD model"},
        default_factory=frozenset,
    )
    logical_operators: frozenset[LogicalOperator] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The logical operators of the SBGN-PD model"},
    )
    equivalence_operators: frozenset[EquivalenceOperator] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The equivalence operators of the SBGN-PD model"},
    )
    submaps: frozenset[Submap] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The submaps of the SBGN-PD model"},
    )
    tags: frozenset[Tag] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The tags of the SBGN-PD model"},
    )

    def is_ovav(self) -> bool:
        """Return `true` if the SBGN-PD model respects the Once a Variable Always a Variable (OVAV) rule, `false` otherwise"""
        subunit_cls_entity_pool_cls_mapping = {
            MacromoleculeSubunit: Macromolecule,
            NucleicAcidFeatureSubunit: NucleicAcidFeature,
            ComplexSubunit: Complex,
            SimpleChemicalSubunit: SimpleChemical,
            MacromoleculeMultimerSubunit: MacromoleculeMultimer,
            NucleicAcidFeatureMultimerSubunit: NucleicAcidFeatureMultimer,
            ComplexMultimerSubunit: ComplexMultimer,
            SimpleChemicalMultimerSubunit: SimpleChemicalMultimer,
        }

        def _check_entities(entities, entity_variables_mapping=None):
            if entity_variables_mapping is None:
                entity_variables_mapping = {}
            for entity in entities:
                if hasattr(entity, "state_variables"):
                    variables = set([sv.variable for sv in entity.state_variables])
                    attributes = []
                    for field in dataclasses.fields(entity):
                        if field.name != "state_variables":
                            attributes.append(field.name)
                    args = {attr: getattr(entity, attr) for attr in attributes}
                    if isinstance(entity, Subunit):
                        cls = subunit_cls_entity_pool_cls_mapping[type(entity)]
                    else:
                        cls = type(entity)
                    entity_no_svs = cls(**args)
                    if entity_no_svs not in entity_variables_mapping:
                        entity_variables_mapping[entity_no_svs] = variables
                    else:
                        if entity_variables_mapping[entity_no_svs] != variables:
                            return False
                if hasattr(entity, "subunits"):
                    is_ovav = _check_entities(entity.subunits, entity_variables_mapping)
                    if not is_ovav:
                        return False
            return True

        return _check_entities(self.entity_pools)

    def is_submodel(self, other) -> bool:
        """Return `true` if another given SBGN-PD model is a submodel of the SBGN-PD model, `false` otherwise"""
        return (
            self.entity_pools.issubset(other.entity_pools)
            and self.processes.issubset(other.processes)
            and self.compartments.issubset(other.compartments)
            and self.modulations.issubset(other.modulations)
            and self.logical_operators.issubset(other.logical_operators)
            and self.equivalence_operators.issubset(other.equivalence_operators)
            and self.submaps.issubset(other.submaps)
            and self.tags.issubset(other.tags)
        )
