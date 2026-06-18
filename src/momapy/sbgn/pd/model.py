"""Model classes for SBGN Process Description (PD) maps."""

import dataclasses
import typing

from momapy.sbgn.elements import (
    SBGNAuxiliaryUnit,
    SBGNModelElement,
    SBGNRole,
)
from momapy.sbgn.model import SBGNModel


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateVariable(SBGNAuxiliaryUnit):
    """State variable of an entity pool.

    State variables describe the state of a residue of an entity pool, such as
    a phosphorylation site.
    """

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
    """Unit of information of an entity pool or compartment.

    Units of information provide additional, typically free-text, information
    about the element they annotate.
    """

    value: str = dataclasses.field(
        metadata={"description": "The value of the unit of information"},
    )
    prefix: str | None = dataclasses.field(
        default=None,
        metadata={"description": "The prefix of the unit of information"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Subunit(SBGNAuxiliaryUnit):
    """Subunit of a complex.

    Subunits are the constituent entities that make up a complex.
    """

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the subunit"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntitySubunit(Subunit):
    """Unspecified entity subunit of a complex.

    Used when the class of the subunit entity is unknown or deliberately
    abstract.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeSubunit(Subunit):
    """Macromolecule subunit of a complex.

    Represents a macromolecule (protein, gene, RNA, etc.) acting as a subunit.
    """

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
    """Nucleic acid feature subunit of a complex.

    Represents a nucleic acid feature (gene, RNA, etc.) acting as a subunit.
    """

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
    """Simple chemical subunit of a complex.

    Represents a simple chemical (small molecule) acting as a subunit.
    """

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
    """Complex subunit of a complex.

    Represents a complex acting as a subunit of another complex.
    """

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
    """Multimer subunit of a complex.

    A multimer is an aggregate of identical entities, with a given cardinality.
    """

    cardinality: int | None = dataclasses.field(
        default=None,
        metadata={"description": "The cardinality of the multimer subunit"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimerSubunit(MultimerSubunit):
    """Macromolecule multimer subunit of a complex.

    A multimer of identical macromolecules acting as a subunit.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureMultimerSubunit(MultimerSubunit):
    """Nucleic acid feature multimer subunit of a complex.

    A multimer of identical nucleic acid features acting as a subunit.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimerSubunit(MultimerSubunit):
    """Simple chemical multimer subunit of a complex.

    A multimer of identical simple chemicals acting as a subunit.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexMultimerSubunit(MultimerSubunit):
    """Complex multimer subunit of a complex.

    A multimer of identical complexes acting as a subunit.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Compartment(SBGNModelElement):
    """Compartment in an SBGN-PD map.

    Compartments represent distinct spatial regions in which entity pools are
    located.
    """

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
    """Entity pool in an SBGN-PD map.

    An entity pool is a population of entities that are considered equivalent
    for the purpose of the map.
    """

    compartment: Compartment | None = dataclasses.field(
        default=None, metadata={"description": "The compartment of the entity pool"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbingAgent(EntityPool):
    """Perturbing agent entity pool.

    Denotes an external influence (drug, stimulus, mutation) acting on the
    system.
    """

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the perturbing agent"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntity(EntityPool):
    """Unspecified entity pool.

    Used when the class of the entity is unknown or deliberately abstract.
    """

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the unspecified entity"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Macromolecule(EntityPool):
    """Macromolecule entity pool.

    Represents a macromolecule such as a protein, gene, or RNA.
    """

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
    """Nucleic acid feature entity pool.

    Represents a nucleic acid feature such as a gene or an RNA.
    """

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
    """Simple chemical entity pool.

    Represents a simple chemical such as a small molecule or an ion.
    """

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
    """Complex entity pool.

    Represents a complex made up of subunits bound together.
    """

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
    """Multimer entity pool.

    A multimer is an aggregate of identical entities, with a given cardinality.
    """

    cardinality: int | None = dataclasses.field(
        default=None, metadata={"description": "The cardinality of the multimer"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimer(Multimer):
    """Macromolecule multimer entity pool.

    A multimer of identical macromolecules.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureMultimer(Multimer):
    """Nucleic acid feature multimer entity pool.

    A multimer of identical nucleic acid features.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimer(Multimer):
    """Simple chemical multimer entity pool.

    A multimer of identical simple chemicals.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexMultimer(Multimer):
    """Complex multimer entity pool.

    A multimer of identical complexes.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class FluxRole(SBGNRole):
    """Role of an entity pool participating in a process.

    A flux role associates an entity pool with a process, with a given
    stoichiometry.
    """

    element: EntityPool = dataclasses.field(
        metadata={"description": "The entity pool of the flux role"}
    )
    stoichiometry: float | None = dataclasses.field(
        default=None, metadata={"description": "The stoichiometry of the flux role"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Reactant(FluxRole):
    """Reactant of a process.

    A reactant is an entity pool consumed by a process.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Product(FluxRole):
    """Product of a process.

    A product is an entity pool produced by a process.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperatorInput(SBGNRole):
    """Input to a logical operator.

    Represents an input connection to a logical operator.
    """

    element: typing.Union[
        EntityPool,
        typing.ForwardRef("LogicalOperator", module=__name__),
    ] = dataclasses.field(
        metadata={"description": "The element of the logical operator input"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorInput(SBGNRole):
    """Input to an equivalence operator.

    Represents an input connection to an equivalence operator.
    """

    element: EntityPool = dataclasses.field(
        metadata={"description": "The element of the equivalence operator input"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorOutput(SBGNRole):
    """Output of an equivalence operator.

    Represents the output connection of an equivalence operator.
    """

    element: EntityPool = dataclasses.field(
        metadata={"description": "The element of the equivalence operator output"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Process(SBGNModelElement):
    """Process in an SBGN-PD map.

    A process transforms entity pools into other entity pools.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class StoichiometricProcess(Process):
    """Base class for stoichiometric processes.

    SBGN PD's empty-set glyph (used as a source-and-sink for unspecified
    external flux) is *not* represented as a member of ``reactants`` or
    ``products``. Instead, it is encoded as the boolean flags
    ``has_external_source`` (an empty-set on the reactant side) and
    ``has_external_sink`` (an empty-set on the product side). The
    corresponding empty-set glyph lives only in the layout
    (``EmptySetLayout``); the model carries no peer entity pool for it.
    """

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
    has_external_source: bool = dataclasses.field(
        default=False,
        metadata={
            "description": (
                "Whether the process has an unspecified external source "
                "(an empty-set / source-and-sink reactant in SBGN PD)."
            )
        },
    )
    has_external_sink: bool = dataclasses.field(
        default=False,
        metadata={
            "description": (
                "Whether the process has an unspecified external sink "
                "(an empty-set / source-and-sink product in SBGN PD)."
            )
        },
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProcess(StoichiometricProcess):
    """Generic process.

    A generic process whose mechanism is not otherwise specified.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UncertainProcess(StoichiometricProcess):
    """Uncertain process.

    A process whose existence or mechanism is uncertain.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Association(GenericProcess):
    """Association process.

    An association binds entity pools together into a complex.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Dissociation(GenericProcess):
    """Dissociation process.

    A dissociation breaks a complex apart into its constituent entity pools.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class OmittedProcess(GenericProcess):
    """Omitted process.

    Denotes a process whose details are deliberately omitted from the map.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Phenotype(Process):
    """Phenotype process.

    Represents an observable characteristic or system-level outcome.
    """

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the phenotype"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperator(SBGNModelElement):
    """Logical operator.

    Represents logical operations (AND, OR, NOT) on entity pools.
    """

    inputs: frozenset[LogicalOperatorInput] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The inputs of the logical operator"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrOperator(LogicalOperator):
    """Logical OR operator.

    The output is active when at least one input is active.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndOperator(LogicalOperator):
    """Logical AND operator.

    The output is active only when every input is active.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotOperator(LogicalOperator):
    """Logical NOT operator.

    The output is active when its (single) input is inactive.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperator(SBGNModelElement):
    """Equivalence operator.

    Defines an entity pool as equivalent to the union of several input entity
    pools.
    """

    inputs: frozenset[EquivalenceOperatorInput] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The inputs of the equivalence operator"},
    )
    output: EquivalenceOperatorOutput | None = dataclasses.field(
        default=None, metadata={"description": "The output of the equivalence operator"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Modulation(SBGNModelElement):
    """Modulation of a process.

    Represents an influence from an entity pool or logical operator on a
    process.
    """

    source: EntityPool | LogicalOperator = dataclasses.field(
        metadata={"description": "The source of the modulation"}
    )
    target: Process = dataclasses.field(
        metadata={"description": "The target of the modulation"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Inhibition(Modulation):
    """Inhibition modulation.

    The source decreases or prevents the activity of the target process.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Stimulation(Modulation):
    """Stimulation modulation.

    The source increases the activity of the target process.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Catalysis(Stimulation):
    """Catalysis modulation.

    The source catalyses the target process without being consumed by it.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulation(Stimulation):
    """Necessary stimulation modulation.

    The target process requires the source to be active in order to proceed.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagReference(SBGNRole):
    """Reference to a tag."""

    element: EntityPool | Compartment = dataclasses.field(
        metadata={"description": "The element of the tag reference"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Tag(SBGNModelElement):
    """Tag element.

    Tags provide identifiers that can be referenced from other locations.
    """

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the tag"}
    )
    referred_element: TagReference | None = dataclasses.field(
        default=None,
        metadata={"description": "The element referred to by the tag"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalReference(SBGNRole):
    """Reference to a terminal."""

    element: EntityPool | Compartment = dataclasses.field(
        metadata={"description": "The element of the terminal reference"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Terminal(SBGNAuxiliaryUnit):
    """Terminal element.

    Terminals represent connection points to submaps.
    """

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the terminal"}
    )
    referred_element: TerminalReference | None = dataclasses.field(
        default=None,
        metadata={"description": "The element referred to by the terminal"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Submap(SBGNModelElement):
    """Submap element.

    Submaps represent embedded or referenced sub-diagrams.
    """

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the submap"}
    )
    terminals: frozenset[Terminal] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The terminals of the submap"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDModel(SBGNModel):
    """SBGN-PD model.

    Represents a complete SBGN Process Description model.
    """

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
        """Return `True` if the SBGN-PD model respects the Once a Variable Always a Variable (OVAV) rule, `False` otherwise"""
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

        def _check_entities(entities, entity_variables_mapping=None) -> bool:
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

    def is_submodel(self, other: "SBGNPDModel") -> bool:
        """Return `True` if another given SBGN-PD model is a submodel of the SBGN-PD model, `False` otherwise"""
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
