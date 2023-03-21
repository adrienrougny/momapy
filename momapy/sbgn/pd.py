import dataclasses
import typing

import momapy.sbgn.core
import momapy.builder
import momapy.arcs
import momapy.shapes
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
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Stadium
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 60.0
    height: float = 30.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Rectangle
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 60.0
    height: float = 30.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNShapeBase):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Pointer
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "top_angle": "angle",
        "bottom_angle": "angle",
        "direction": "direction",
    }
    width: float = 60.0
    height: float = 30.0
    angle: float = 50.0
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalLayout(TagLayout):
    width: float = 60.0
    height: float = 30.0
    angle: float = 50.0
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class CardinalityLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Rectangle
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 60.0
    height: float = 30.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompartmentLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[
        type
    ] = momapy.shapes.RectangleWithRoundedCorners
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "rounded_corners": "rounded_corners"
    }
    width: float = 80.0
    height: float = 80.0
    rounded_corners: float = 10.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 4.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Ellipse
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 60.0
    height: float = 30.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[
        type
    ] = momapy.shapes.RectangleWithRoundedCorners
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "rounded_corners": "rounded_corners"
    }
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 10.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeMultimerLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[
        type
    ] = momapy.shapes.RectangleWithRoundedCorners
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "rounded_corners": "rounded_corners"
    }
    _n: int = 2
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 10.0
    offset: float = 2.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Stadium
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 60.0
    height: float = 30.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalMultimerLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Stadium
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    _n: int = 2
    width: float = 60.0
    height: float = 30.0
    offset: float = 2.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.RectangleWithCutCorners
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "cut_corners": "cut_corners"
    }
    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 10.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexMultimerLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.RectangleWithCutCorners
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "cut_corners": "cut_corners"
    }
    _n: int = 2
    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 10.0
    offset: float = 2.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[
        type
    ] = momapy.shapes.RectangleWithBottomRoundedCorners
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "rounded_corners": "rounded_corners"
    }
    _n: int = 2
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 10.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureMultimerLayout(
    momapy.sbgn.core._MultiMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[
        type
    ] = momapy.shapes.RectangleWithBottomRoundedCorners
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "rounded_corners": "rounded_corners"
    }
    _n: int = 2
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 10.0
    offset: float = 2.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class EmptySetLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.CircleWithDiagonalBar
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 60.0
    height: float = 30.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbingAgentLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.InvertedHexagon
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "top_left_angle": "angle",
        "top_right_angle": "angle",
        "bottom_left_angle": "angle",
        "bottom_right_angle": "angle",
    }
    width: float = 60.0
    height: float = 30.0
    angle: float = 50.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class _LogicalOperatorLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core._SBGNShapeBase,
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Ellipse
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 3
    )
    _font_color: typing.ClassVar[
        momapy.coloring.Color
    ] = momapy.coloring.black


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndOperatorLayout(_LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "AND"
    width: float = 20.0
    height: float = 20.0
    left_connector_length: float = 10.0
    right_connector_length: float = 10.0
    left_connector_stroke_width: float = 1.0
    right_connector_stroke_width: float = 1.0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrOperatorLayout(_LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "OR"
    width: float = 20.0
    height: float = 20.0
    left_connector_length: float = 10.0
    right_connector_length: float = 10.0
    left_connector_stroke_width: float = 1.0
    right_connector_stroke_width: float = 1.0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotOperatorLayout(_LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "NOT"
    width: float = 20.0
    height: float = 20.0
    left_connector_length: float = 10.0
    right_connector_length: float = 10.0
    left_connector_stroke_width: float = 1.0
    right_connector_stroke_width: float = 1.0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceOperatorLayout(_LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "≡"
    width: float = 20.0
    height: float = 20.0
    left_connector_length: float = 10.0
    right_connector_length: float = 10.0
    left_connector_stroke_width: float = 1.0
    right_connector_stroke_width: float = 1.0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class GenericProcessLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._SBGNShapeBase,
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Rectangle
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 20.0
    height: float = 20.0
    left_connector_length: float = 10.0
    right_connector_length: float = 10.0
    left_connector_stroke_width: float = 1.0
    right_connector_stroke_width: float = 1.0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class OmittedProcessLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core._SBGNShapeBase,
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Rectangle
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    _text: typing.ClassVar[str] = "\\\\"
    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 1.5
    )
    _font_color: typing.ClassVar[
        momapy.coloring.Color
    ] = momapy.coloring.black
    width: float = 20.0
    height: float = 20.0
    left_connector_length: float = 10.0
    right_connector_length: float = 10.0
    left_connector_stroke_width: float = 1.0
    right_connector_stroke_width: float = 1.0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class UncertainProcessLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core._SBGNShapeBase,
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Rectangle
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    _text: typing.ClassVar[str] = "?"
    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 1.5
    )
    _font_color: typing.ClassVar[
        momapy.coloring.Color
    ] = momapy.coloring.black
    width: float = 20.0
    height: float = 20.0
    left_connector_length: float = 10.0
    right_connector_length: float = 10.0
    left_connector_stroke_width: float = 1.0
    right_connector_stroke_width: float = 1.0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class AssociationLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._SBGNShapeBase,
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Ellipse
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 20.0
    height: float = 20.0
    left_connector_length: float = 10.0
    right_connector_length: float = 10.0
    left_connector_stroke_width: float = 1.0
    right_connector_stroke_width: float = 1.0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class DissociationLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._SBGNShapeBase,
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.CircleWithInsideCircle
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {"sep": "sep"}
    width: float = 20.0
    height: float = 20.0
    sep: float = 3.5
    left_connector_length: float = 10.0
    right_connector_length: float = 10.0
    left_connector_stroke_width: float = 1.0
    right_connector_stroke_width: float = 1.0
    direction: momapy.core.Direction = momapy.core.Direction.HORIZONTAL
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._SBGNShapeBase,
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Hexagon
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {
        "top_left_angle": "angle",
        "top_right_angle": "angle",
        "bottom_left_angle": "angle",
        "bottom_right_angle": "angle",
    }
    width: float = 60.0
    height: float = 30.0
    angle: float = 50.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class SubmapLayout(
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._SBGNShapeBase,
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Rectangle
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    width: float = 80.0
    height: float = 80.0
    stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    stroke_width: typing.Optional[float] = 1.0
    stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    stroke_dashoffset: typing.Optional[float] = 0.0
    fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white
    transform: typing.Optional[
        typing.Union[
            momapy.drawing.NoneValueType, tuple[momapy.geometry.Transformation]
        ]
    ] = momapy.drawing.NoneValue
    filter: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.drawing.Filter]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class ConsumptionLayout(momapy.arcs.PolyLine):
    width: float = 0.0
    height: float = 0.0
    shorten: float = 0.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_width: typing.Optional[float] = 0.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: typing.Optional[float] = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class ProductionLayout(momapy.arcs.Arrow):
    width: float = 12.0
    height: float = 12.0
    shorten: float = 0.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: typing.Optional[float] = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: typing.Optional[float] = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black


@dataclasses.dataclass(frozen=True, kw_only=True)
class StimulationLayout(momapy.arcs.Arrow):
    width: float = 12.0
    height: float = 12.0
    shorten: float = 0.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: typing.Optional[float] = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: typing.Optional[float] = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white


@dataclasses.dataclass(frozen=True, kw_only=True)
class CatalysisLayout(momapy.arcs.Circle):
    width: float = 11.0
    height: float = 11.0
    shorten: float = 0.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: typing.Optional[float] = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: typing.Optional[float] = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white


@dataclasses.dataclass(frozen=True, kw_only=True)
class InhibitionLayout(momapy.arcs.Bar):
    width: float = 1.5
    height: float = 12.0
    shorten: float = 2.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: typing.Optional[float] = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: typing.Optional[float] = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulationLayout(momapy.arcs.BarArrow):
    width: float = 12.0
    height: float = 12.0
    bar_width: float = 1.0
    bar_height: float = 12.0
    sep: float = 2.0
    shorten: float = 2.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: typing.Optional[float] = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: typing.Optional[float] = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModulationLayout(momapy.arcs.Diamond):
    width: float = 12.0
    height: float = 12.0
    shorten: float = 0.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.black
    arrowhead_stroke_width: typing.Optional[float] = 1.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: typing.Optional[float] = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.coloring.white


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(momapy.arcs.PolyLine):
    width: float = 0.0
    height: float = 0.0
    shorten: float = 0.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_width: typing.Optional[float] = 0.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: typing.Optional[float] = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(momapy.arcs.PolyLine):
    width: float = 0.0
    height: float = 0.0
    shorten: float = 0.0
    stroke: typing.Union[
        momapy.drawing.NoneValueType, momapy.coloring.Color
    ] = momapy.coloring.black
    stroke_width: float = 1.0
    stroke_dasharray: typing.Union[
        momapy.drawing.NoneValueType, tuple[float]
    ] = momapy.drawing.NoneValue
    fill: momapy.drawing.NoneValueType = momapy.drawing.NoneValue
    arrowhead_stroke: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_width: typing.Optional[float] = 0.0
    arrowhead_stroke_dasharray: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, tuple[float]]
    ] = momapy.drawing.NoneValue
    arrowhead_stroke_dashoffset: typing.Optional[float] = 0.0
    arrowhead_fill: typing.Optional[
        typing.Union[momapy.drawing.NoneValueType, momapy.coloring.Color]
    ] = momapy.drawing.NoneValue


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNPDMap(momapy.sbgn.core.SBGNMap):
    model: typing.Optional[SBGNPDModel] = None
    layout: typing.Optional[SBGNPDLayout] = None


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
