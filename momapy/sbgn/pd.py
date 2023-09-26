import dataclasses
import typing

import momapy.sbgn.core
import momapy.builder
import momapy.arcs
import momapy.nodes
import momapy.coloring


@dataclasses.dataclass(frozen=True, kw_only=True)
class UndefinedVariable(momapy.sbgn.core.SBGNModelElement):
    order: int


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateVariable(momapy.sbgn.core.SBGNModelElement):
    variable: typing.Union[str, UndefinedVariable]
    value: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformation(momapy.sbgn.core.SBGNModelElement):
    value: str
    prefix: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Subunit(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None


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
    cardinality: typing.Optional[int] = None


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
    label: typing.Optional[str] = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EntityPool(momapy.sbgn.core.SBGNModelElement):
    compartment: typing.Optional[Compartment] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class EmptySet(EntityPool):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbingAgent(EntityPool):
    label: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntity(EntityPool):
    label: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Macromolecule(EntityPool):
    label: typing.Optional[str] = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeature(EntityPool):
    label: typing.Optional[str] = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemical(EntityPool):
    label: typing.Optional[str] = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Complex(EntityPool):
    label: typing.Optional[str] = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )
    subunits: frozenset[Subunit] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Multimer(Complex):
    cardinality: typing.Optional[int] = None


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
    stoichiometry: typing.Optional[int] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Reactant(FluxRole):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Product(FluxRole):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperatorInput(momapy.sbgn.core.SBGNRole):
    element: typing.Union[EntityPool, "LogicalOperator"]


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorInput(momapy.sbgn.core.SBGNRole):
    element: EntityPool


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorOutput(momapy.sbgn.core.SBGNRole):
    element: EntityPool


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalReference(momapy.sbgn.core.SBGNRole):
    element: typing.Union[EntityPool, Compartment]


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagReference(momapy.sbgn.core.SBGNRole):
    element: typing.Union[EntityPool, Compartment]


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
    label: typing.Optional[str] = None


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
    output: typing.Optional[EquivalenceOperatorOutput] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Modulation(momapy.sbgn.core.SBGNModelElement):
    source: typing.Union[EntityPool, LogicalOperator]
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
class Terminal(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None
    refers_to: typing.Optional[TerminalReference] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Tag(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None
    refers_to: typing.Optional[TagReference] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Submap(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None
    terminals: frozenset[Terminal] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDModel(momapy.sbgn.core.SBGNModel):
    entity_pools: frozenset[EntityPool] = dataclasses.field(
        default_factory=frozenset
    )
    processes: frozenset[Process] = dataclasses.field(default_factory=frozenset)
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
                        if entity_variables_mapping[entity_no_svs] != variables:
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
            and self.equivalence_operators.issubset(other.equivalence_operators)
            and self.submaps.issubset(other.submaps)
            and self.tags.issubset(other.tags)
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDLayout(momapy.sbgn.core.SBGNLayout):
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white


@dataclasses.dataclass(frozen=True, kw_only=True)
class StateVariableLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float

    def _make_node(self, position, width, height):
        node = momapy.nodes.Stadium(
            position=position,
            width=width,
            height=height,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float

    def _make_node(self, position, width, height):
        node = momapy.nodes.Rectangle(
            position=position,
            width=width,
            height=height,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase):
    width: float
    height: float
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    angle: float = 50.0

    def _make_node(self, position, width, height):
        if self.direction == momapy.core.Direction.RIGHT:
            node = momapy.nodes.Hexagon(
                position=position,
                width=width,
                height=height,
                left_angle=90.0,
                right_angle=self.angle,
            )
        elif self.direction == momapy.core.Direction.LEFT:
            node = momapy.nodes.Hexagon(
                position=position,
                width=width,
                height=height,
                left_angle=self.angle,
                right_angle=90.0,
            )
        elif self.direction == momapy.core.Direction.UP:
            node = momapy.nodes.TurnedHexagon(
                position=position,
                width=width,
                height=height,
                top_angle=self.angle,
                bottom_angle=90.0,
            )
        elif self.direction == momapy.core.Direction.DOWN:
            node = momapy.nodes.TurnedHexagon(
                position=position,
                width=width,
                height=height,
                top_angle=90.0,
                bottom_angle=self.angle,
            )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    angle: float = 50.0

    def _make_node(self, position, width, height):
        return TagLayout._make_node(self, position, width, height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CardinalityLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float

    def _make_node(self, position, width, height):
        return UnitOfInformationLayout._make_node(self, position, width, height)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntitySubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float

    def _make_node(self, position, width, height):
        node = UnspecifiedEntityLayout._make_node(self, position, width, height)
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalSubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float

    def _make_node(self, position, width, height):
        node = SimpleChemicalLayout._make_node(self, position, width, height)
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeSubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float
    rounded_corners: float

    def _make_node(self, position, width, height):
        node = MacromoleculeLayout._make_node(self, position, width, height)
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureSubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float
    rounded_corners: float

    def _make_node(self, position, width, height):
        node = NucleicAcidFeatureLayout._make_node(
            self, position, width, height
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexSubunitLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float
    cut_corners: float

    def _make_node(self, position, width, height):
        node = ComplexLayout._make_node(self, position, width, height)
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimerSubunitLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core._SBGNNodeBase
):
    _n: int = 2
    width: float
    height: float

    def _make_subunit_node(
        self,
        position,
        width,
        height,
        border_stroke=None,
        border_stroke_width=None,
        border_stroke_dasharray=None,
        border_stroke_dashoffset=None,
        border_fill=None,
        border_transform=None,
        border_filter=None,
    ):
        node = momapy.nodes.Stadium(
            position=position,
            width=width,
            height=height,
            border_stroke=border_stroke,
            border_stroke_width=border_stroke_width,
            border_stroke_dasharray=border_stroke_dasharray,
            border_stroke_dashoffset=border_stroke_dashoffset,
            border_fill=border_fill,
            border_transform=border_transform,
            border_filter=border_filter,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimerSubunitLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core._SBGNNodeBase
):
    _n: int = 2
    width: float
    height: float
    rounded_corners: float

    def _make_subunit_node(
        self,
        position,
        width,
        height,
        border_stroke=None,
        border_stroke_width=None,
        border_stroke_dasharray=None,
        border_stroke_dashoffset=None,
        border_fill=None,
        border_transform=None,
        border_filter=None,
    ):
        node = momapy.nodes.Rectangle(
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
            border_stroke=border_stroke,
            border_stroke_width=border_stroke_width,
            border_stroke_dasharray=border_stroke_dasharray,
            border_stroke_dashoffset=border_stroke_dashoffset,
            border_fill=border_fill,
            border_transform=border_transform,
            border_filter=border_filter,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureMultimerSubunitLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core._SBGNNodeBase
):
    _n: int = 2
    width: float
    height: float
    rounded_corners: float

    def _make_subunit_node(
        self,
        position,
        width,
        height,
        border_stroke=None,
        border_stroke_width=None,
        border_stroke_dasharray=None,
        border_stroke_dashoffset=None,
        border_fill=None,
        border_transform=None,
        border_filter=None,
    ):
        node = momapy.nodes.Rectangle(
            position=position,
            width=width,
            height=height,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
            border_stroke=border_stroke,
            border_stroke_width=border_stroke_width,
            border_stroke_dasharray=border_stroke_dasharray,
            border_stroke_dashoffset=border_stroke_dashoffset,
            border_fill=border_fill,
            border_transform=border_transform,
            border_filter=border_filter,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexMultimerSubunitLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core._SBGNNodeBase
):
    _n: int = 2
    width: float
    height: float
    cut_corners: float

    def _make_subunit_node(
        self,
        position,
        width,
        height,
        border_stroke=None,
        border_stroke_width=None,
        border_stroke_dasharray=None,
        border_stroke_dashoffset=None,
        border_fill=None,
        border_transform=None,
        border_filter=None,
    ):
        node = momapy.nodes.Rectangle(
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
            border_stroke=border_stroke,
            border_stroke_width=border_stroke_width,
            border_stroke_dasharray=border_stroke_dasharray,
            border_stroke_dashoffset=border_stroke_dashoffset,
            border_fill=border_fill,
            border_transform=border_transform,
            border_filter=border_filter,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompartmentLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float
    rounded_corners: float
    border_stroke_width: float = 5.0

    def _make_node(self, position, width, height):
        node = MacromoleculeLayout._make_node(self, position, width, height)
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class SubmapLayout(
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._SBGNNodeBase,
):
    def _make_node(self, position, width, height):
        node = momapy.nodes.Rectangle(
            position=position,
            width=width,
            height=height,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float

    def _make_node(self, position, width, height):
        node = momapy.nodes.Ellipse(
            position=position, width=width, height=height
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float

    def _make_node(self, position, width, height):
        node = momapy.nodes.Stadium(
            position=position, width=width, height=height
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float
    rounded_corners: float

    def _make_node(self, position, width, height):
        node = momapy.nodes.Rectangle(
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
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float
    rounded_corners: float

    def _make_node(self, position, width, height):
        node = momapy.nodes.Rectangle(
            position=position,
            width=width,
            height=height,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float
    cut_corners: float

    def _make_node(self, position, width, height):
        node = momapy.nodes.Rectangle(
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
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimerLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core._SBGNNodeBase
):
    _n: int = 2
    width: float
    height: float

    def _make_subunit_node(
        self,
        position,
        width,
        height,
        border_stroke=None,
        border_stroke_width=None,
        border_stroke_dasharray=None,
        border_stroke_dashoffset=None,
        border_fill=None,
        border_transform=None,
        border_filter=None,
    ):
        node = momapy.nodes.Stadium(
            position=position,
            width=width,
            height=height,
            border_stroke=border_stroke,
            border_stroke_width=border_stroke_width,
            border_stroke_dasharray=border_stroke_dasharray,
            border_stroke_dashoffset=border_stroke_dashoffset,
            border_fill=border_fill,
            border_transform=border_transform,
            border_filter=border_filter,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimerLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core._SBGNNodeBase
):
    _n: int = 2
    width: float
    height: float
    rounded_corners: float

    def _make_subunit_node(
        self,
        position,
        width,
        height,
        border_stroke=None,
        border_stroke_width=None,
        border_stroke_dasharray=None,
        border_stroke_dashoffset=None,
        border_fill=None,
        border_transform=None,
        border_filter=None,
    ):
        node = momapy.nodes.Rectangle(
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
            border_stroke=border_stroke,
            border_stroke_width=border_stroke_width,
            border_stroke_dasharray=border_stroke_dasharray,
            border_stroke_dashoffset=border_stroke_dashoffset,
            border_fill=border_fill,
            border_transform=border_transform,
            border_filter=border_filter,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureMultimerLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core._SBGNNodeBase
):
    _n: int = 2
    width: float
    height: float
    rounded_corners: float

    def _make_subunit_node(
        self,
        position,
        width,
        height,
        border_stroke=None,
        border_stroke_width=None,
        border_stroke_dasharray=None,
        border_stroke_dashoffset=None,
        border_fill=None,
        border_transform=None,
        border_filter=None,
    ):
        node = momapy.nodes.Rectangle(
            position=position,
            width=width,
            height=height,
            bottom_left_rx=self.rounded_corners,
            bottom_left_ry=self.rounded_corners,
            bottom_right_rx=self.rounded_corners,
            bottom_right_ry=self.rounded_corners,
            border_stroke=border_stroke,
            border_stroke_width=border_stroke_width,
            border_stroke_dasharray=border_stroke_dasharray,
            border_stroke_dashoffset=border_stroke_dashoffset,
            border_fill=border_fill,
            border_transform=border_transform,
            border_filter=border_filter,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexMultimerLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core._SBGNNodeBase
):
    _n: int = 2
    width: float
    height: float
    cut_corners: float

    def _make_subunit_node(
        self,
        position,
        width,
        height,
        border_stroke=None,
        border_stroke_width=None,
        border_stroke_dasharray=None,
        border_stroke_dashoffset=None,
        border_fill=None,
        border_transform=None,
        border_filter=None,
    ):
        node = momapy.nodes.Rectangle(
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
            border_stroke=border_stroke,
            border_stroke_width=border_stroke_width,
            border_stroke_dasharray=border_stroke_dasharray,
            border_stroke_dashoffset=border_stroke_dashoffset,
            border_fill=border_fill,
            border_transform=border_transform,
            border_filter=border_filter,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class _EmptySetNode(momapy.core.NodeLayout):
    def border_drawing_elements(self):
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
class EmptySetLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float

    def _make_node(self, position, width, height):
        node = _EmptySetNode(
            position=position,
            width=width,
            height=height,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbingAgentLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNNodeBase
):
    width: float
    height: float
    angle: float

    def _make_node(self, position, width, height):
        node = momapy.nodes.Hexagon(
            position=position,
            width=width,
            height=height,
            left_angle=180 - self.angle,
            right_angle=180 - self.angle,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class _LogicalOperatorLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core._SBGNNodeBase,
):
    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 3
    )
    _font_color: typing.ClassVar[momapy.coloring.Color] = momapy.coloring.black

    def _make_node(self, position, width, height):
        node = momapy.nodes.Ellipse(
            position=position, width=width, height=height
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndOperatorLayout(_LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "AND"


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrOperatorLayout(_LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "OR"


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotOperatorLayout(_LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "NOT"


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorLayout(_LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "≡"


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProcessLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._SBGNNodeBase,
):
    def _make_node(self, position, width, height):
        node = momapy.nodes.Rectangle(
            position=position, width=width, height=height
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class OmittedProcessLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core._SBGNNodeBase,
):
    _text: typing.ClassVar[str] = "\\\\"
    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 1.5
    )
    _font_color: typing.ClassVar[momapy.coloring.Color] = momapy.coloring.black

    def _make_node(self, position, width, height):
        node = GenericProcessLayout._make_node(self, position, width, height)
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class UncertainProcessLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core._SBGNNodeBase,
):
    _text: typing.ClassVar[str] = "?"
    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 1.5
    )
    _font_color: typing.ClassVar[momapy.coloring.Color] = momapy.coloring.black

    def _make_node(self, position, width, height):
        node = GenericProcessLayout._make_node(self, position, width, height)
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class AssociationLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._SBGNNodeBase,
):
    border_fill: momapy.coloring.Color = momapy.coloring.black

    def _make_node(self, position, width, height):
        node = momapy.nodes.Ellipse(
            position=position, width=width, height=height
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class _DissociationNode(momapy.core.NodeLayout):
    sep: float

    def border_drawing_elements(self):
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
    momapy.sbgn.core._SBGNNodeBase,
):
    sep: float

    def _make_node(self, position, width, height):
        node = _DissociationNode(
            position=position, width=width, height=height, sep=self.sep
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._SBGNNodeBase,
):
    angle: float

    def _make_node(self, position, width, height):
        node = momapy.nodes.Hexagon(
            position=position,
            width=width,
            height=height,
            left_angle=self.angle,
            right_angle=self.angle,
        )
        return node


@dataclasses.dataclass(frozen=True, kw_only=True)
class ConsumptionLayout(momapy.arcs.PolyLine):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProductionLayout(momapy.arcs.Triangle):
    arrowhead_fill: momapy.coloring.Color = momapy.coloring.black


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModulationLayout(momapy.arcs.Diamond):
    arrowhead_fill: momapy.coloring.Color = momapy.coloring.white


@dataclasses.dataclass(frozen=True, kw_only=True)
class StimulationLayout(momapy.arcs.Triangle):
    arrowhead_fill: momapy.coloring.Color = momapy.coloring.white


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulationLayout(momapy.core.SingleHeadedArcLayout):
    arrowhead_triangle_width: float
    arrowhead_triangle_height: float
    arrowhead_bar_width: float
    arrowhead_bar_height: float
    arrowhead_sep: float
    arrowhead_fill: momapy.coloring.Color = momapy.coloring.white

    def arrowhead_drawing_elements(self):
        actions = [
            momapy.drawing.MoveTo(
                momapy.geometry.Point(0, -self.arrowhead_bar_height / 2)
            ),
            momapy.drawing.LineTo(
                momapy.geometry.Point(0, self.arrowhead_bar_height / 2)
            ),
        ]
        bar = momapy.drawing.Path(
            actions=actions, stroke_width=self.arrowhead_bar_width
        )
        actions = [
            momapy.drawing.MoveTo(momapy.geometry.Point(0, 0)),
            momapy.drawing.LineTo(momapy.geometry.Point(self.arrowhead_sep, 0)),
        ]
        sep = momapy.drawing.Path(actions=actions)
        triangle = momapy.nodes.Triangle(
            position=momapy.geometry.Point(
                self.arrowhead_sep + self.arrowhead_triangle_width / 2, 0
            ),
            width=self.arrowhead_triangle_width,
            height=self.arrowhead_triangle_height,
            direction=momapy.core.Direction.RIGHT,
        )
        return [bar, sep] + triangle.self_drawing_elements()


@dataclasses.dataclass(frozen=True, kw_only=True)
class CatalysisLayout(momapy.arcs.Ellipse):
    arrowhead_fill: momapy.coloring.Color = momapy.coloring.white


@dataclasses.dataclass(frozen=True, kw_only=True)
class InhibitionLayout(momapy.arcs.Bar):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(momapy.arcs.PolyLine):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(momapy.arcs.PolyLine):
    pass


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
