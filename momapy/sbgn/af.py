import enum
import dataclasses
import typing

import momapy.sbgn.core


@dataclasses.dataclass(frozen=True)
class Compartment(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class UnitOfInformation(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class MacromoleculeUnitOfInformation(UnitOfInformation):
    pass


@dataclasses.dataclass(frozen=True)
class NucleicAcidFeatureUnitOfInformation(UnitOfInformation):
    pass


@dataclasses.dataclass(frozen=True)
class ComplexUnitOfInformation(UnitOfInformation):
    pass


@dataclasses.dataclass(frozen=True)
class SimpleChemicalUnitOfInformation(UnitOfInformation):
    pass


@dataclasses.dataclass(frozen=True)
class UnspecifiedEntityUnitOfInformation(UnitOfInformation):
    pass


@dataclasses.dataclass(frozen=True)
class PerturbationUnitOfInformation(UnitOfInformation):
    pass


class Activity(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None
    compartment: typing.Optional[Compartment] = None


@dataclasses.dataclass(frozen=True)
class BiologicalActivity(Activity):
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class Phenotype(Activity):
    pass


@dataclasses.dataclass(frozen=True)
class LogicalOperatorInput(momapy.sbgn.core.SBGNRole):
    element: typing.Union[BiologicalActivity, "LogicalOperator"]


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
class DelayOperator(LogicalOperator):
    pass


@dataclasses.dataclass(frozen=True)
class Influence(momapy.sbgn.core.SBGNModelElement):
    source: typing.Optional[
        typing.Union[BiologicalActivity, LogicalOperator]
    ] = None
    target: typing.Optional[Activity] = None


@dataclasses.dataclass(frozen=True)
class UnknownInfluence(Influence):
    pass


@dataclasses.dataclass(frozen=True)
class PositiveInfluence(Influence):
    pass


@dataclasses.dataclass(frozen=True)
class NegativeInfluence(Influence):
    pass


@dataclasses.dataclass(frozen=True)
class NecessaryStimulation(Influence):
    pass


@dataclasses.dataclass(frozen=True)
class TerminalReference(momapy.sbgn.core.SBGNRole):
    element: typing.Union[Activity, Compartment] = None


@dataclasses.dataclass(frozen=True)
class TagReference(momapy.sbgn.core.SBGNRole):
    element: typing.Union[Activity, Compartment] = None


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


@dataclasses.dataclass(frozen=True)
class SBGNAFModel(momapy.sbgn.core.SBGNModel):
    activities: frozenset[Activity] = dataclasses.field(
        default_factory=frozenset
    )
    compartments: frozenset[Compartment] = dataclasses.field(
        default_factory=frozenset
    )
    influences: frozenset[Influence] = dataclasses.field(
        default_factory=frozenset
    )
    logical_operators: frozenset[LogicalOperator] = dataclasses.field(
        default_factory=frozenset
    )
    submaps: frozenset[Submap] = dataclasses.field(default_factory=frozenset)
    tags: frozenset[Tag] = dataclasses.field(default_factory=frozenset)

    def is_submodel(self, other):
        return (
            self.activities.issubset(other.activities)
            and self.compartments.issubset(other.compartments)
            and self.influences.issubset(other.influences)
            and self.logical_operators.issubset(other.logical_operators)
            and self.submaps(other.submaps)
            and self.tags.issubset(other.tags)
        )


@dataclasses.dataclass(frozen=True)
class MacromoleculeUnitOfInformationLayout(momapy.sbgn.pd.MacromoleculeLayout):
    pass


@dataclasses.dataclass(frozen=True)
class NucleicAcidFeatureUnitOfInformationLayout(
    momapy.sbgn.pd.NucleicAcidFeatureLayout
):
    pass


@dataclasses.dataclass(frozen=True)
class ComplexUnitOfInformationLayout(momapy.sbgn.pd.ComplexLayout):
    pass


@dataclasses.dataclass(frozen=True)
class UnspecifiedEntityUnitOfInformationLayout(
    momapy.sbgn.pd.UnspecifiedEntityLayout
):
    pass


@dataclasses.dataclass(frozen=True)
class PerturbationUnitOfInformationLayout(momapy.sbgn.pd.PerturbingAgentLayout):
    pass


@dataclasses.dataclass(frozen=True)
class SimpleChemicalUnitOfInformationLayout(
    momapy.sbgn.pd.SimpleChemicalLayout
):
    pass


@dataclasses.dataclass(frozen=True)
class BiologicalActivityLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core._SBGNShapeBase
):
    _shape_cls: typing.ClassVar[type] = momapy.shapes.Rectangle
    _arg_names_mapping: typing.ClassVar[dict[str, str]] = {}
    stroke: momapy.coloring.Color = momapy.coloring.colors.black
    stroke_width: float = 1
    fill: momapy.coloring.Color = momapy.coloring.colors.white


@dataclasses.dataclass(frozen=True)
class PhenotypeLayout(momapy.sbgn.pd.PhenotypeLayout):
    pass


@dataclasses.dataclass(frozen=True)
class AndOperatorLayout(momapy.sbgn.pd.AndOperatorLayout):
    pass


@dataclasses.dataclass(frozen=True)
class OrOperatorLayout(momapy.sbgn.pd.OrOperatorLayout):
    pass


@dataclasses.dataclass(frozen=True)
class NotOperatorLayout(momapy.sbgn.pd.NotOperatorLayout):
    pass


@dataclasses.dataclass(frozen=True)
class DelayOperatorLayout(momapy.sbgn.pd._LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "τ"


@dataclasses.dataclass(frozen=True)
class CompartmentLayout(momapy.sbgn.pd.CompartmentLayout):
    pass


@dataclasses.dataclass(frozen=True)
class SubmapLayout(momapy.sbgn.pd.SubmapLayout):
    pass


@dataclasses.dataclass(frozen=True)
class UnknownInfluenceLayout(momapy.sbgn.pd.ModulationLayout):
    pass


@dataclasses.dataclass(frozen=True)
class PositiveInfluenceLayout(momapy.sbgn.pd.StimulationLayout):
    pass


@dataclasses.dataclass(frozen=True)
class NegativeInfluenceLayout(momapy.sbgn.pd.InhibitionLayout):
    pass


@dataclasses.dataclass(frozen=True)
class NecessaryStimulationLayout(momapy.sbgn.pd.NecessaryStimulationLayout):
    pass


@dataclasses.dataclass(frozen=True)
class LogicArcLayout(momapy.sbgn.pd.LogicArcLayout):
    pass


@dataclasses.dataclass(frozen=True)
class EquivalenceArcLayout(momapy.sbgn.pd.EquivalenceArcLayout):
    pass


@dataclasses.dataclass(frozen=True)
class TagLayout(momapy.sbgn.pd.TagLayout):
    pass


@dataclasses.dataclass(frozen=True)
class TerminalLayout(momapy.sbgn.pd.TerminalLayout):
    pass


@dataclasses.dataclass(frozen=True)
class SBGNAFMap(momapy.sbgn.core.SBGNMap):
    model: typing.Optional[SBGNAFModel] = None


SBGNAFModelBuilder = momapy.builder.get_or_make_builder_cls(SBGNAFModel)


def _sbgnaf_map_builder_new_model(self, *args, **kwargs):
    return SBGNAFModelBuilder(*args, **kwargs)


def _sbgnaf_map_builder_new_layout(self, *args, **kwargs):
    return momapy.core.MapLayoutBuilder(*args, **kwargs)


def _sbgnaf_map_builder_new_model_layout_mapping(self, *args, **kwargs):
    return momapy.core.ModelLayoutMappingBuilder(*args, **kwargs)


SBGNAFMapBuilder = momapy.builder.get_or_make_builder_cls(
    SBGNAFMap,
    builder_namespace={
        "new_model": _sbgnaf_map_builder_new_model,
        "new_layout": _sbgnaf_map_builder_new_layout,
        "new_model_layout_mapping": _sbgnaf_map_builder_new_model_layout_mapping,
    },
)
