"""Classes for SBGN PD maps"""

import dataclasses
import typing
import sys

import momapy.sbgn.core
import momapy.builder
import momapy.meta.arcs
import momapy.meta.shapes
import momapy.coloring


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateVariable(momapy.sbgn.core.SBGNAuxiliaryUnit):
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
class UnitOfInformation(momapy.sbgn.core.SBGNAuxiliaryUnit):
    """Class for units of information"""

    value: str = dataclasses.field(
        metadata={"description": "The value of the unit of information"},
    )
    prefix: str | None = dataclasses.field(
        default=None,
        metadata={"description": "The prefix of the unit of information"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Subunit(momapy.sbgn.core.SBGNAuxiliaryUnit):
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
class Compartment(momapy.sbgn.core.SBGNModelElement):
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
class EntityPool(momapy.sbgn.core.SBGNModelElement):
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
class FluxRole(momapy.sbgn.core.SBGNRole):
    """Base class for flux roles"""

    element: EntityPool = dataclasses.field(
        metadata={"description": "The entity pool of the flux role"}
    )
    stoichiometry: int | None = dataclasses.field(
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
class LogicalOperatorInput(momapy.sbgn.core.SBGNRole):
    """Class for inputs of logical operators"""

    element: typing.Union[
        EntityPool,
        typing.ForwardRef("LogicalOperator", module=sys.modules[__name__]),
    ] = dataclasses.field(
        metadata={"description": "The element of the logical operator input"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorInput(momapy.sbgn.core.SBGNRole):
    """Class for inputs of equivalence operators"""

    element: EntityPool = dataclasses.field(
        metadata={"description": "The element of the equivalence operator input"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorOutput(momapy.sbgn.core.SBGNRole):
    """Class for outputs of equivalence operators"""

    element: EntityPool = dataclasses.field(
        metadata={"description": "The element of the equivalence operator output"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Process(momapy.sbgn.core.SBGNModelElement):
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
class LogicalOperator(momapy.sbgn.core.SBGNModelElement):
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
class EquivalenceOperator(momapy.sbgn.core.SBGNModelElement):
    """Class for equivalence operators"""

    inputs: frozenset[EquivalenceOperatorInput] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The inputs of the equivalence operator"},
    )
    output: EquivalenceOperatorOutput | None = dataclasses.field(
        default=None, metadata={"description": "The output of the equivalence operator"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Modulation(momapy.sbgn.core.SBGNModelElement):
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
class TagReference(momapy.sbgn.core.SBGNRole):
    """Class for tag references"""

    element: EntityPool | Compartment = dataclasses.field(
        metadata={"description": "The element of the tag reference"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Tag(momapy.sbgn.core.SBGNModelElement):
    """Class for tags"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the tag"}
    )
    reference: TagReference | None = dataclasses.field(
        default=None, metadata={"description": "The reference of the tag"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalReference(momapy.sbgn.core.SBGNRole):
    """Class for terminal references"""

    element: EntityPool | Compartment = dataclasses.field(
        metadata={"description": "The element of the terminal reference"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Terminal(momapy.sbgn.core.SBGNAuxiliaryUnit):
    """Class for terminals"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the terminal"}
    )
    reference: TerminalReference | None = dataclasses.field(
        default=None, metadata={"description": "The reference of the terminal"}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Submap(momapy.sbgn.core.SBGNModelElement):
    """Class for submaps"""

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the submap"}
    )
    terminals: frozenset[Terminal] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "The terminals of the submap"},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDModel(momapy.sbgn.core.SBGNModel):
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


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDLayout(momapy.sbgn.core.SBGNLayout):
    """Class for SBGN-PD layouts"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateVariableLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for state variable layouts"""

    width: float = dataclasses.field(
        default=12.0, metadata={"description": "The width of the state variable layout"}
    )
    height: float = dataclasses.field(
        default=12.0,
        metadata={"description": "The height of the state variable layout"},
    )

    def _make_shape(self):
        return momapy.meta.shapes.Stadium(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformationLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for unit of information layouts"""

    width: float = 12.0
    height: float = 12.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for terminal layouts"""

    width: float = 35.0
    height: float = 35.0
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return TagLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CardinalityLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for cardinality layouts"""

    width: float = 12.0
    height: float = 19.0

    def _make_shape(self):
        return UnitOfInformationLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntitySubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for unspecified entity subunit layouts"""

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return UnspecifiedEntityLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalSubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for simple chemical subunit layouts"""

    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return SimpleChemicalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeSubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for macromolecule subunit layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureSubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for nucleic acid feature subunit layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return NucleicAcidFeatureLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexSubunitLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for complex subunit layouts"""

    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 5.0

    def _make_shape(self):
        return ComplexLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimerSubunitLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core.SBGNNode
):
    """Class for simple chemical multimer subunit layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 60.0
    height: float = 30.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Stadium(
            position=position,
            width=width,
            height=height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimerSubunitLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core.SBGNNode
):
    """Class for macromolecule multimer subunit layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Rectangle(
            position=position,
            width=width,
            height=height,
            top_left_rx=self.rounded_corners,
            top_left_ry=self.rounded_corners,
            top_right_rx=self.rounded_corners,
            top_right_ry=self.rounded_corners,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureMultimerSubunitLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core.SBGNNode
):
    """Class for nucleic acid feature multimer subunit layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Rectangle(
            position=position,
            width=width,
            height=height,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexMultimerSubunitLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core.SBGNNode
):
    """Class for complex multimer subunit layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 5.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
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


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompartmentLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for compartment layouts"""

    width: float = 80.0
    height: float = 80.0
    rounded_corners: float = 5.0
    stroke_width: float = 3.25

    def _make_shape(self):
        return MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SubmapLayout(
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core.SBGNNode,
):
    """Class for submap layouts"""

    width: float = 80.0
    height: float = 80.0
    stroke_width: float = 2.25

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for unspecified entity layouts"""

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for simple chemical layouts"""

    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Stadium(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for macromolecule layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position,
            width=self.width,
            height=self.height,
            top_left_rx=self.rounded_corners,
            top_left_ry=self.rounded_corners,
            top_right_rx=self.rounded_corners,
            top_right_ry=self.rounded_corners,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for nucleic acid feature layouts"""

    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position,
            width=self.width,
            height=self.height,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for complex layouts"""

    width: float = 44.0
    height: float = 44.0
    cut_corners: float = 5.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position,
            width=self.width,
            height=self.height,
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


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimerLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core.SBGNNode
):
    """Class for simple chemical multimer layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 30.0
    height: float = 30.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Stadium(
            position=position,
            width=width,
            height=height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimerLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core.SBGNNode
):
    """Class for macromolecule multimer layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Rectangle(
            position=position,
            width=width,
            height=height,
            top_left_rx=self.rounded_corners,
            top_left_ry=self.rounded_corners,
            top_right_rx=self.rounded_corners,
            top_right_ry=self.rounded_corners,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureMultimerLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core.SBGNNode
):
    """Class for nucleic acid feature multimer layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
        return momapy.meta.shapes.Rectangle(
            position=position,
            width=width,
            height=height,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexMultimerLayout(momapy.sbgn.core._MultiMixin, momapy.sbgn.core.SBGNNode):
    """Class for complex multimer layouts"""

    _n: typing.ClassVar[int] = 2
    width: float = 44.0
    height: float = 44.0
    cut_corners: float = 5.0

    def _make_subunit_shape(
        self,
        position,
        width,
        height,
    ):
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


@dataclasses.dataclass(frozen=True, kw_only=True)
class _EmptySetShape(momapy.core.Shape):
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
class EmptySetLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for empty set layouts"""

    width: float = 22.0
    height: float = 22.0

    def _make_shape(self):
        return _EmptySetShape(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbingAgentLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for perturbing agent layouts"""

    width: float = 60.0
    height: float = 30.0
    angle: float = 70.0

    def _make_shape(self):
        return momapy.meta.shapes.Hexagon(
            position=self.position,
            width=self.width,
            height=self.height,
            left_angle=180 - self.angle,
            right_angle=180 - self.angle,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndOperatorLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core.SBGNNode,
):
    """Class for and operator layouts"""

    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    _text: typing.ClassVar[str] = "AND"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrOperatorLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core.SBGNNode,
):
    """Class for or operator layouts"""

    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    _text: typing.ClassVar[str] = "OR"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotOperatorLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core.SBGNNode,
):
    """Class for not operator layouts"""

    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 3
    _text: typing.ClassVar[str] = "NOT"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core.SBGNNode,
):
    """Class for equivalence operator layouts"""

    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 2
    _text: typing.ClassVar[str] = "≡"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProcessLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core.SBGNNode,
):
    """Class for generic process layouts"""

    width: float = 20.0
    height: float = 20.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OmittedProcessLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core.SBGNNode,
):
    """Class for omitted process layouts"""

    _text: typing.ClassVar[str] = "\\\\"
    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 1.5
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue

    width: float = 20.0
    height: float = 20.0

    def _make_shape(self):
        return GenericProcessLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UncertainProcessLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core.SBGNNode,
):
    """Class for uncertain process layouts"""

    _text: typing.ClassVar[str] = "?"
    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 1.5
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue

    width: float = 20.0
    height: float = 20.0

    def _make_shape(self):
        return GenericProcessLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class AssociationLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core.SBGNNode,
):
    """Class for association layouts"""

    width: float = 20.0
    height: float = 20.0

    fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class _DissociationShape(momapy.core.Shape):
    position: momapy.geometry.Point
    width: float
    height: float
    sep: float

    def drawing_elements(self):
        outer_circle = momapy.drawing.Ellipse(
            point=self.position, rx=self.width / 2, ry=self.height / 2
        )
        inner_circle = momapy.drawing.Ellipse(
            point=self.position,
            rx=self.width / 2 - self.sep,
            ry=self.height / 2 - self.sep,
        )
        return [outer_circle, inner_circle]


@dataclasses.dataclass(frozen=True, kw_only=True)
class DissociationLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core.SBGNNode,
):
    """Class for dissociation layouts"""

    width: float = 20.0
    height: float = 20.0
    sep: float = 3.0

    def _make_shape(self):
        return _DissociationShape(
            position=self.position,
            width=self.width,
            height=self.height,
            sep=self.sep,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core.SBGNNode,
):
    """Class for phenotype layouts"""

    width: float = 60.0
    height: float = 30.0
    angle: float = 70.0

    def _make_shape(self):
        return momapy.meta.shapes.Hexagon(
            position=self.position,
            width=self.width,
            height=self.height,
            left_angle=self.angle,
            right_angle=self.angle,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for tag layouts"""

    width: float = 35.0
    height: float = 35.0
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        if self.direction == momapy.core.Direction.RIGHT:
            return momapy.meta.shapes.Hexagon(
                position=self.position,
                width=self.width,
                height=self.height,
                left_angle=90.0,
                right_angle=self.angle,
            )
        elif self.direction == momapy.core.Direction.LEFT:
            return momapy.meta.shapes.Hexagon(
                position=self.position,
                width=self.width,
                height=self.height,
                left_angle=self.angle,
                right_angle=90.0,
            )
        elif self.direction == momapy.core.Direction.UP:
            return momapy.meta.shapes.TurnedHexagon(
                position=self.position,
                width=self.width,
                height=self.height,
                top_angle=self.angle,
                bottom_angle=90.0,
            )
        elif self.direction == momapy.core.Direction.DOWN:
            return momapy.meta.shapes.TurnedHexagon(
                position=self.position,
                width=self.width,
                height=self.height,
                top_angle=90.0,
                bottom_angle=self.angle,
            )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ConsumptionLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for consumption layouts"""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProductionLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for production layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.black
    )
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModulationLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for modulation layouts"""

    arrowhead_fill: momapy.drawing.NoneValueType | momapy.coloring.Color | None = (
        momapy.coloring.white
    )
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Diamond._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class StimulationLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for stimulation layouts"""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulationLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for necessary stimulation layouts"""

    arrowhead_bar_height: float = 12.0
    arrowhead_sep: float = 3.0
    arrowhead_triangle_height: float = 10.0
    arrowhead_triangle_width: float = 10.0

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
                self.arrowhead_sep + self.arrowhead_triangle_width / 2, 0
            ),
            width=self.arrowhead_triangle_width,
            height=self.arrowhead_triangle_height,
            direction=momapy.core.Direction.RIGHT,
        )
        return [bar, sep] + triangle.drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class CatalysisLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for catalysis layouts"""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Ellipse._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class InhibitionLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for inhibition layouts"""

    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Bar._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for logic arc layouts"""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for equivalence arc layouts"""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDMap(momapy.sbgn.core.SBGNMap):
    """Class for SBGN-PD maps"""

    model: SBGNPDModel
    layout: SBGNPDLayout


SBGNPDModelBuilder = momapy.builder.get_or_make_builder_cls(SBGNPDModel)
"""Class for SBGN-PD model builders"""
SBGNPDLayoutBuilder = momapy.builder.get_or_make_builder_cls(SBGNPDLayout)
"""Class for SBGN-PD layout builders"""


def _sbgnpd_map_builder_new_model(self, *args, **kwargs):
    return SBGNPDModelBuilder(*args, **kwargs)


def _sbgnpd_map_builder_new_layout(self, *args, **kwargs):
    return SBGNPDLayoutBuilder(*args, **kwargs)


SBGNPDMapBuilder = momapy.builder.get_or_make_builder_cls(
    SBGNPDMap,
    builder_namespace={
        "new_model": _sbgnpd_map_builder_new_model,
        "new_layout": _sbgnpd_map_builder_new_layout,
    },
)
"""Class for SBGN-PD map builders"""
