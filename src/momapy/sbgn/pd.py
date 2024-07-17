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
    variable: str | None = None
    value: str | None = None
    order: int | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformation(momapy.sbgn.core.SBGNAuxiliaryUnit):
    value: str
    prefix: str | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Subunit(momapy.sbgn.core.SBGNAuxiliaryUnit):
    label: str | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntitySubunit(Subunit):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeSubunit(Subunit):
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureSubunit(Subunit):
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalSubunit(Subunit):
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexSubunit(Subunit):
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )
    subunits: frozenset[Subunit] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True, kw_only=True)
class MultimerSubunit(ComplexSubunit):
    cardinality: int | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimerSubunit(MultimerSubunit):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureMultimerSubunit(MultimerSubunit):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimerSubunit(MultimerSubunit):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexMultimerSubunit(MultimerSubunit):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Compartment(momapy.sbgn.core.SBGNModelElement):
    label: str | None = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EntityPool(momapy.sbgn.core.SBGNModelElement):
    compartment: Compartment | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class EmptySet(EntityPool):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbingAgent(EntityPool):
    label: str | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntity(EntityPool):
    label: str | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Macromolecule(EntityPool):
    label: str | None = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeature(EntityPool):
    label: str | None = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemical(EntityPool):
    label: str | None = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Complex(EntityPool):
    label: str | None = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )
    subunits: frozenset[Subunit] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Multimer(Complex):
    cardinality: int | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimer(Multimer):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureMultimer(Multimer):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimer(Multimer):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexMultimer(Multimer):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class FluxRole(momapy.sbgn.core.SBGNRole):
    element: EntityPool
    stoichiometry: int | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Reactant(FluxRole):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Product(FluxRole):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperatorInput(momapy.sbgn.core.SBGNRole):
    element: typing.Union[
        EntityPool,
        typing.ForwardRef("LogicalOperator", module=sys.modules[__name__]),
    ]


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorInput(momapy.sbgn.core.SBGNRole):
    element: EntityPool


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorOutput(momapy.sbgn.core.SBGNRole):
    element: EntityPool


@dataclasses.dataclass(frozen=True, kw_only=True)
class Process(momapy.sbgn.core.SBGNModelElement):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class StoichiometricProcess(Process):
    reactants: frozenset[Reactant] = dataclasses.field(
        default_factory=frozenset
    )
    products: frozenset[Product] = dataclasses.field(default_factory=frozenset)
    reversible: bool = False


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProcess(StoichiometricProcess):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UncertainProcess(StoichiometricProcess):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Association(GenericProcess):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Dissociation(GenericProcess):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class OmittedProcess(GenericProcess):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Phenotype(Process):
    label: str | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperator(momapy.sbgn.core.SBGNModelElement):
    inputs: frozenset[LogicalOperatorInput] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrOperator(LogicalOperator):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndOperator(LogicalOperator):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotOperator(LogicalOperator):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperator(momapy.sbgn.core.SBGNModelElement):
    inputs: frozenset[EquivalenceOperatorInput] = dataclasses.field(
        default_factory=frozenset
    )
    output: EquivalenceOperatorOutput | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Modulation(momapy.sbgn.core.SBGNModelElement):
    source: EntityPool | LogicalOperator
    target: Process


@dataclasses.dataclass(frozen=True, kw_only=True)
class Inhibition(Modulation):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Stimulation(Modulation):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Catalysis(Stimulation):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulation(Stimulation):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagReference(momapy.sbgn.core.SBGNRole):
    element: EntityPool | Compartment


@dataclasses.dataclass(frozen=True, kw_only=True)
class Tag(momapy.sbgn.core.SBGNModelElement):
    label: str | None = None
    reference: TagReference | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalReference(momapy.sbgn.core.SBGNRole):
    element: EntityPool | Compartment


@dataclasses.dataclass(frozen=True, kw_only=True)
class Terminal(momapy.sbgn.core.SBGNAuxiliaryUnit):
    label: str | None = None
    reference: TerminalReference | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Submap(momapy.sbgn.core.SBGNModelElement):
    label: str | None = None
    terminals: frozenset[Terminal] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDModel(momapy.sbgn.core.SBGNModel):
    entity_pools: frozenset[EntityPool] = dataclasses.field(
        default_factory=frozenset
    )
    processes: frozenset[Process] = dataclasses.field(
        default_factory=frozenset
    )
    compartments: frozenset[Compartment] = dataclasses.field(
        default_factory=frozenset
    )
    modulations: frozenset[Modulation] = dataclasses.field(
        default_factory=frozenset
    )
    logical_operators: frozenset[LogicalOperator] = dataclasses.field(
        default_factory=frozenset
    )
    equivalence_operators: frozenset[EquivalenceOperator] = dataclasses.field(
        default_factory=frozenset
    )
    submaps: frozenset[Submap] = dataclasses.field(default_factory=frozenset)
    tags: frozenset[Tag] = dataclasses.field(default_factory=frozenset)

    def is_ovav(self):
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
                    variables = set(
                        [sv.variable for sv in entity.state_variables]
                    )
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
                        if (
                            entity_variables_mapping[entity_no_svs]
                            != variables
                        ):
                            return False
                if hasattr(entity, "subunits"):
                    is_ovav = _check_entities(
                        entity.subunits, entity_variables_mapping
                    )
                    if not is_ovav:
                        return False
            return True

        return _check_entities(self.entity_pools)

    def is_submodel(self, other):
        return (
            self.entity_pools.issubset(other.entity_pools)
            and self.processes.issubset(other.processes)
            and self.compartments.issubset(other.compartments)
            and self.modulations.issubset(other.modulations)
            and self.logical_operators.issubset(other.logical_operators)
            and self.equivalence_operators.issubset(
                other.equivalence_operators
            )
            and self.submaps.issubset(other.submaps)
            and self.tags.issubset(other.tags)
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDLayout(momapy.sbgn.core.SBGNLayout):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateVariableLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 12.0
    height: float = 12.0

    def _make_shape(self):
        return momapy.meta.shapes.Stadium(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
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
    width: float = 35.0
    height: float = 35.0
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return TagLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CardinalityLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 12.0
    height: float = 19.0

    def _make_shape(self):
        return UnitOfInformationLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntitySubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return UnspecifiedEntityLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalSubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return SimpleChemicalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeSubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureSubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return NucleicAcidFeatureLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexSubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 5.0

    def _make_shape(self):
        return ComplexLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimerSubunitLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core.SBGNNode
):
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
class CompartmentLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 80.0
    height: float = 80.0
    rounded_corners: float = 5.0
    border_stroke_width: float = 3.25

    def _make_shape(self):
        return MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SubmapLayout(
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core.SBGNNode,
):
    width: float = 80.0
    height: float = 80.0
    border_stroke_width: float = 2.25

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Stadium(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
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
class ComplexMultimerLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core.SBGNNode
):
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
            momapy.drawing.MoveTo(
                self.position - (self.width / 2, -self.height / 2)
            ),
            momapy.drawing.LineTo(
                self.position + (self.width / 2, -self.height / 2)
            ),
        ]
        bar = momapy.drawing.Path(actions=actions)
        return [circle, bar]


@dataclasses.dataclass(frozen=True, kw_only=True)
class EmptySetLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    width: float = 22.0
    height: float = 22.0

    def _make_shape(self):
        return _EmptySetShape(
            position=self.position,
            width=self.width,
            height=self.height,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbingAgentLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
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
class _LogicalOperatorLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core.SBGNNode,
):
    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndOperatorLayout(_LogicalOperatorLayout):
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 3
    )

    _text: typing.ClassVar[str] = "AND"


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrOperatorLayout(_LogicalOperatorLayout):
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 3
    )

    _text: typing.ClassVar[str] = "OR"


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotOperatorLayout(_LogicalOperatorLayout):
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 3
    )

    _text: typing.ClassVar[str] = "NOT"


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorLayout(_LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "≡"
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 2
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProcessLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core.SBGNNode,
):
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
    _text: typing.ClassVar[str] = "\\\\"
    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 1.5
    )
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
    _text: typing.ClassVar[str] = "?"
    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 1.5
    )
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
    width: float = 20.0
    height: float = 20.0

    border_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black

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
    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine.arrowhead_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProductionLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.black
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle.arrowhead_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModulationLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    arrowhead_fill: (
        momapy.drawing.NoneValueType | momapy.coloring.Color | None
    ) = momapy.coloring.white
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Diamond._arrowhead_border_drawing_elements(
            self
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class StimulationLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(
            self
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulationLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
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
            momapy.drawing.LineTo(
                momapy.geometry.Point(self.arrowhead_sep, 0)
            ),
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
    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Ellipse._arrowhead_border_drawing_elements(
            self
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class InhibitionLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Bar._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(
            self
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(
            self
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDMap(momapy.sbgn.core.SBGNMap):
    model: SBGNPDModel
    layout: SBGNPDLayout


SBGNPDModelBuilder = momapy.builder.get_or_make_builder_cls(SBGNPDModel)
SBGNPDLayoutBuilder = momapy.builder.get_or_make_builder_cls(SBGNPDLayout)


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
