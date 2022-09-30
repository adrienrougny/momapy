import dataclasses
import typing

import momapy.sbgn.core
import momapy.builder
import momapy.arcs
import momapy.shapes
import momapy.coloring

############STATE VARIABLE AND UNIT OF INFORMATION###################
@dataclasses.dataclass(frozen=True)
class UndefinedVariable(momapy.sbgn.core.SBGNModelElement):
    order: typing.Optional[int] = None


@dataclasses.dataclass(frozen=True)
class StateVariable(momapy.sbgn.core.SBGNModelElement):
    variable: typing.Optional[typing.Union[str, UndefinedVariable]] = None
    value: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class UnitOfInformation(momapy.sbgn.core.SBGNModelElement):
    value: typing.Optional[str] = None
    prefix: typing.Optional[str] = None


############SUBUNITS###################
@dataclasses.dataclass(frozen=True)
class Subunit(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class UnspecifiedEntitySubunit(Subunit):
    pass


@dataclasses.dataclass(frozen=True)
class MacromoleculeSubunit(Subunit):
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class NucleicAcidFeatureSubunit(Subunit):
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class SimpleChemicalSubunit(Subunit):
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class ComplexSubunit(Subunit):
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )
    subunits: frozenset[Subunit] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class MultimerSubunit(ComplexSubunit):
    cardinality: typing.Optional[int] = None


@dataclasses.dataclass(frozen=True)
class MacromoleculeMultimerSubunit(MultimerSubunit):
    pass


@dataclasses.dataclass(frozen=True)
class NucleicAcidFeatureMultimerSubunit(MultimerSubunit):
    pass


@dataclasses.dataclass(frozen=True)
class SimpleChemicalMultimerSubunit(MultimerSubunit):
    pass


@dataclasses.dataclass(frozen=True)
class ComplexMultimerSubunit(MultimerSubunit):
    pass


############COMPARTMENT###################
@dataclasses.dataclass(frozen=True)
class Compartment(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


############ENTITY POOLS###################
@dataclasses.dataclass(frozen=True)
class EntityPool(momapy.sbgn.core.SBGNModelElement):
    compartment: typing.Optional[Compartment] = None


@dataclasses.dataclass(frozen=True)
class EmptySet(EntityPool):
    pass


@dataclasses.dataclass(frozen=True)
class PerturbingAgent(EntityPool):
    label: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class UnspecifiedEntity(EntityPool):
    label: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class Macromolecule(EntityPool):
    label: typing.Optional[str] = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class NucleicAcidFeature(EntityPool):
    label: typing.Optional[str] = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class SimpleChemical(EntityPool):
    label: typing.Optional[str] = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class Complex(EntityPool):
    label: typing.Optional[str] = None
    state_variables: frozenset[StateVariable] = dataclasses.field(
        default_factory=frozenset
    )
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )
    subunits: frozenset[Subunit] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class Multimer(Complex):
    cardinality: typing.Optional[int] = None


@dataclasses.dataclass(frozen=True)
class MacromoleculeMultimer(Multimer):
    pass


@dataclasses.dataclass(frozen=True)
class NucleicAcidFeatureMultimer(Multimer):
    pass


@dataclasses.dataclass(frozen=True)
class SimpleChemicalMultimer(Multimer):
    pass


@dataclasses.dataclass(frozen=True)
class ComplexMultimer(Multimer):
    pass


############SBGN ROLES###################
@dataclasses.dataclass(frozen=True)
class FluxRole(momapy.sbgn.core.SBGNRole):
    element: EntityPool
    stoichiometry: typing.Optional[int] = None


@dataclasses.dataclass(frozen=True)
class Reactant(FluxRole):
    pass


@dataclasses.dataclass(frozen=True)
class Product(FluxRole):
    pass


@dataclasses.dataclass(frozen=True)
class LogicalOperatorInput(momapy.sbgn.core.SBGNRole):
    element: typing.Union[EntityPool, "LogicalOperator"]


@dataclasses.dataclass(frozen=True)
class EquivalenceOperatorInput(momapy.sbgn.core.SBGNRole):
    element: EntityPool


@dataclasses.dataclass(frozen=True)
class EquivalenceOperatorOutput(momapy.sbgn.core.SBGNRole):
    element: EntityPool


@dataclasses.dataclass(frozen=True)
class TerminalReference(momapy.sbgn.core.SBGNRole):
    element: typing.Union[EntityPool, Compartment] = None


@dataclasses.dataclass(frozen=True)
class TagReference(momapy.sbgn.core.SBGNRole):
    element: typing.Union[EntityPool, Compartment] = None


############PROCESSES###################
@dataclasses.dataclass(frozen=True)
class Process(momapy.sbgn.core.SBGNModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class StoichiometricProcess(Process):
    reactants: frozenset[Reactant] = dataclasses.field(
        default_factory=frozenset
    )
    products: frozenset[Product] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True)
class GenericProcess(StoichiometricProcess):
    pass


@dataclasses.dataclass(frozen=True)
class UncertainProcess(StoichiometricProcess):
    pass


@dataclasses.dataclass(frozen=True)
class Association(GenericProcess):
    pass


@dataclasses.dataclass(frozen=True)
class Dissociation(GenericProcess):
    pass


@dataclasses.dataclass(frozen=True)
class OmittedProcess(GenericProcess):
    pass


@dataclasses.dataclass(frozen=True)
class Phenotype(Process):
    label: typing.Optional[str] = None


############OPERATORS###################
@dataclasses.dataclass(frozen=True)
class LogicalOperator(momapy.sbgn.core.SBGNModelElement):
    inputs: frozenset[LogicalOperatorInput] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class OrOperator(LogicalOperator):
    pass


@dataclasses.dataclass(frozen=True)
class AndOperator(LogicalOperator):
    pass


@dataclasses.dataclass(frozen=True)
class NotOperator(LogicalOperator):
    pass


@dataclasses.dataclass(frozen=True)
class EquivalenceOperator(momapy.sbgn.core.SBGNModelElement):
    inputs: frozenset[EquivalenceOperatorInput] = dataclasses.field(
        default_factory=frozenset
    )
    output: typing.Optional[EquivalenceOperatorOutput] = None


############MODULATIONS###################
@dataclasses.dataclass(frozen=True)
class Modulation(momapy.sbgn.core.SBGNModelElement):
    source: typing.Optional[typing.Union[EntityPool, LogicalOperator]] = None
    target: typing.Optional[Process] = None


@dataclasses.dataclass(frozen=True)
class Inhibition(Modulation):
    pass


@dataclasses.dataclass(frozen=True)
class Stimulation(Modulation):
    pass


@dataclasses.dataclass(frozen=True)
class Catalysis(Stimulation):
    pass


@dataclasses.dataclass(frozen=True)
class NecessaryStimulation(Stimulation):
    pass


############SUBMAP###################
@dataclasses.dataclass(frozen=True)
class Terminal(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None
    refers_to: typing.Optional[TerminalReference] = None


@dataclasses.dataclass(frozen=True)
class Tag(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None
    refers_to: typing.Optional[TagReference] = None


@dataclasses.dataclass(frozen=True)
class Submap(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None
    terminals: frozenset[Terminal] = dataclasses.field(
        default_factory=frozenset
    )


############MODELS###################
@dataclasses.dataclass(frozen=True)
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
                    for field in fields(entity):
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

    def contains(self, other):
        return (
            other.entity_pools.issubset(self.entity_pools)
            and other.processes.issubset(self.processes)
            and other.compartments.issubset(self.compartments)
            and other.modulations.issubset(self.modulations)
            and other.logical_operators.issubset(self.logical_operators)
            and other.equivalence_operators.issubset(self.equivalence_operators)
            and other.submaps.issubset(self.submaps)
            and other.tags.issubset(self.tags)
        )


############MAP###################
@dataclasses.dataclass(frozen=True)
class SBGNPDMap(momapy.sbgn.core.SBGNMap):
    model: typing.Optional[SBGNPDModel] = None


############BUILDERS###################
SBGNPDModelBuilder = momapy.builder.get_or_make_builder_cls(SBGNPDModel)


def sbgnpd_map_builder_new_model(self, *args, **kwargs):
    return SBGNPDModelBuilder(*args, **kwargs)


def sbgnpd_map_builder_new_layout(self, *args, **kwargs):
    return momapy.core.MapLayoutBuilder(*args, **kwargs)


def sbgnpd_map_builder_new_model_layout_mapping(self, *args, **kwargs):
    return momapy.core.ModelLayoutMappingBuilder(*args, **kwargs)


SBGNPDMapBuilder = momapy.builder.get_or_make_builder_cls(
    SBGNPDMap,
    builder_namespace={
        "new_model": sbgnpd_map_builder_new_model,
        "new_layout": sbgnpd_map_builder_new_layout,
        "new_model_layout_mapping": sbgnpd_map_builder_new_model_layout_mapping,
    },
)


############GLYPHS###################


@dataclasses.dataclass(frozen=True)
class CompartmentLayout(momapy.shapes.RectangleWithRoundedCorners):
    rounded_corners: float = 10
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 4


@dataclasses.dataclass(frozen=True)
class MacromoleculeLayout(momapy.shapes.RectangleWithRoundedCorners):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    rounded_corners: float = 10
    fill: momapy.coloring.Color = momapy.coloring.colors.white


@dataclasses.dataclass(frozen=True)
class MacromoleculeMultimerLayout(
    momapy.shapes.DoubleRectangleWithRoundedCorners
):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    rounded_corners: float = 10
    offset: float = 2


@dataclasses.dataclass(frozen=True)
class SimpleChemicalLayout(momapy.shapes.Stadium):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white


@dataclasses.dataclass(frozen=True)
class SimpleChemicalMultimerLayout(momapy.shapes.DoubleStadium):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    offset: float = 2


@dataclasses.dataclass(frozen=True)
class StateVariableLayout(momapy.shapes.Stadium):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white


@dataclasses.dataclass(frozen=True)
class UnitOfInformationLayout(momapy.shapes.Rectangle):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white


@dataclasses.dataclass(frozen=True)
class ComplexLayout(momapy.shapes.RectangleWithCutCorners):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    cut_corners: float = 10


@dataclasses.dataclass(frozen=True)
class ComplexMultimerLayout(momapy.shapes.DoubleRectangleWithCutCorners):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    cut_corners: float = 10
    offset: float = 2


@dataclasses.dataclass(frozen=True)
class NucleicAcidFeatureMultimerLayout(
    momapy.shapes.DoubleRectangleWithBottomRoundedCorners
):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    rounded_corners: float = 10
    offset: float = 2


@dataclasses.dataclass(frozen=True)
class NucleicAcidFeatureLayout(momapy.shapes.RectangleWithBottomRoundedCorners):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    rounded_corners: float = 10


@dataclasses.dataclass(frozen=True)
class EmptySetLayout(momapy.shapes.CircleWithDiagonalBar):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white


@dataclasses.dataclass(frozen=True)
class AndOperatorLayout(momapy.shapes.CircleWithConnectorsAndText):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    text: str = "AND"


@dataclasses.dataclass(frozen=True)
class OrOperatorLayout(momapy.shapes.CircleWithConnectorsAndText):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    text: str = "OR"


@dataclasses.dataclass(frozen=True)
class NotOperatorLayout(momapy.shapes.CircleWithConnectorsAndText):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    text: str = "NOT"


@dataclasses.dataclass(frozen=True)
class EquivalenceOperatorLayout(momapy.shapes.CircleWithConnectorsAndText):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    text: str = "≡"


@dataclasses.dataclass(frozen=True)
class UnspecifiedEntityLayout(momapy.shapes.Ellipse):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white


@dataclasses.dataclass(frozen=True)
class GenericProcessLayout(momapy.shapes.RectangleWithConnectors):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white


@dataclasses.dataclass(frozen=True)
class OmittedProcessLayout(momapy.shapes.RectangleWithConnectorsAndText):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    text: str = "//"


@dataclasses.dataclass(frozen=True)
class UncertainProcessLayout(momapy.shapes.RectangleWithConnectorsAndText):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    text: str = "?"


@dataclasses.dataclass(frozen=True)
class AssociationLayout(momapy.shapes.CircleWithConnectors):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.black


@dataclasses.dataclass(frozen=True)
class DissociationLayout(momapy.shapes.CircleInsideCircleWithConnectors):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    sep: float = 3


@dataclasses.dataclass(frozen=True)
class PhenotypeLayout(momapy.shapes.Hexagon):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white


@dataclasses.dataclass(frozen=True)
class SubmapLayout(momapy.shapes.Rectangle):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white


@dataclasses.dataclass(frozen=True)
class ConsumptionLayout(momapy.arcs.PolyLine):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1


@dataclasses.dataclass(frozen=True)
class ProductionLayout(momapy.arcs.Arrow):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.black
    width: float = 12
    height: float = 12


@dataclasses.dataclass(frozen=True)
class StimulationLayout(momapy.arcs.Arrow):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    width: float = 12
    height: float = 12


@dataclasses.dataclass(frozen=True)
class CatalysisLayout(momapy.arcs.Circle):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    width: float = 11
    height: float = 11


@dataclasses.dataclass(frozen=True)
class InhibitionLayout(momapy.arcs.Bar):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    width: float = 1.5
    height: float = 12
    shorten: float = 2


@dataclasses.dataclass(frozen=True)
class NecessaryStimulationLayout(momapy.arcs.BarArrow):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    bar_width: float = 1
    bar_height: float = 12
    width: float = 12
    height: float = 12
    sep: float = 2


@dataclasses.dataclass(frozen=True)
class ModulationLayout(momapy.arcs.Diamond):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white
    width: float = 12
    height: float = 12


@dataclasses.dataclass(frozen=True)
class LogicArcLayout(momapy.arcs.PolyLine):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1


@dataclasses.dataclass(frozen=True)
class EquivalenceArcLayout(momapy.arcs.PolyLine):
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
