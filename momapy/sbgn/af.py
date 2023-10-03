import enum
import dataclasses
import typing

import momapy.meta.shapes
import momapy.sbgn.core
import momapy.sbgn.pd


@dataclasses.dataclass(frozen=True, kw_only=True)
class Compartment(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformation(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeUnitOfInformation(UnitOfInformation):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureUnitOfInformation(UnitOfInformation):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexUnitOfInformation(UnitOfInformation):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalUnitOfInformation(UnitOfInformation):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityUnitOfInformation(UnitOfInformation):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbationUnitOfInformation(UnitOfInformation):
    pass


class Activity(momapy.sbgn.core.SBGNModelElement):
    label: typing.Optional[str] = None
    compartment: typing.Optional[Compartment] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class BiologicalActivity(Activity):
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Phenotype(Activity):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperatorInput(momapy.sbgn.core.SBGNRole):
    element: typing.Union[BiologicalActivity, "LogicalOperator"]


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
class DelayOperator(LogicalOperator):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Influence(momapy.sbgn.core.SBGNModelElement):
    source: BiologicalActivity | LogicalOperator
    target: Activity


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInfluence(Influence):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluence(Influence):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NegativeInfluence(Influence):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulation(Influence):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalReference(momapy.sbgn.core.SBGNRole):
    element: typing.Union[Activity, Compartment]


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagReference(momapy.sbgn.core.SBGNRole):
    element: typing.Union[Activity, Compartment]


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


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNAFLayout(momapy.sbgn.core.SBGNLayout):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.sbgn.pd.UnspecifiedEntityLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.sbgn.pd.SimpleChemicalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.NucleicAcidFeatureLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 60.0
    height: float = 30.0
    cut_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.ComplexLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbationUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 60.0
    height: float = 30.0
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.PerturbingAgentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    width: float = 60.0
    height: float = 30.0
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.TerminalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompartmentLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 60.0
    height: float = 30.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.CompartmentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SubmapLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.sbgn.pd.SubmapLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class BiologicalActivityLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    width: float = 60.0
    height: float = 30.0
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.PhenotypeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class _LogicalOperatorLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core.SBGNNode,
):
    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 3
    )
    _font_color: typing.ClassVar[momapy.coloring.Color] = momapy.coloring.black

    def _make_shape(self):
        return momapy.sbgn.pd._LogicalOperatorLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndOperatorLayout(_LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "AND"
    width: float = 20.0
    height: float = 20.0


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrOperatorLayout(_LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "OR"
    width: float = 20.0
    height: float = 20.0


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotOperatorLayout(_LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "NOT"
    width: float = 20.0
    height: float = 20.0


@dataclasses.dataclass(frozen=True, kw_only=True)
class DelayOperatorLayout(_LogicalOperatorLayout):
    _text: typing.ClassVar[str] = "τ"
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 2
    )
    width: float = 20.0
    height: float = 20.0


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagLayout(momapy.sbgn.pd.TagLayout):
    width: float = 60.0
    height: float = 30.0
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.TagLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInfluenceLayout(
    momapy.meta.arcs.Diamond, momapy.sbgn.core.SBGNArc
):
    arrowhead_width: float = 10.0
    arrowhead_height: float = 10.0
    arrowhead_fill: momapy.coloring.Color = momapy.coloring.white


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluenceLayout(
    momapy.meta.arcs.Triangle, momapy.sbgn.core.SBGNArc
):
    arrowhead_width: float = 10.0
    arrowhead_height: float = 10.0
    arrowhead_fill: momapy.coloring.Color = momapy.coloring.white


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulationLayout(
    momapy.core.SingleHeadedArcLayout, momapy.sbgn.core.SBGNArc
):
    arrowhead_triangle_width: float
    arrowhead_triangle_height: float
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
class NegativeInfluenceLayout(momapy.meta.arcs.Bar, momapy.sbgn.core.SBGNArc):
    arrowhead_height: float = 10.0


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(momapy.meta.arcs.PolyLine, momapy.sbgn.core.SBGNArc):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(momapy.meta.arcs.PolyLine, momapy.sbgn.core.SBGNArc):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNAFMap(momapy.sbgn.core.SBGNMap):
    model: typing.Optional[SBGNAFModel] = None
    layout: typing.Optional[SBGNAFLayout] = None


SBGNAFModelBuilder = momapy.builder.get_or_make_builder_cls(SBGNAFModel)
SBGNAFLayoutBuilder = momapy.builder.get_or_make_builder_cls(SBGNAFLayout)


def _sbgnaf_map_builder_new_model(self, *args, **kwargs):
    return SBGNAFModelBuilder(*args, **kwargs)


def _sbgnaf_map_builder_new_layout(self, *args, **kwargs):
    return SBGNAFLayoutBuilder(*args, **kwargs)


SBGNAFMapBuilder = momapy.builder.get_or_make_builder_cls(
    SBGNAFMap,
    builder_namespace={
        "new_model": _sbgnaf_map_builder_new_model,
        "new_layout": _sbgnaf_map_builder_new_layout,
    },
)
