"""Classes for SBGN AF maps"""

import enum
import dataclasses
import typing

import momapy.meta.shapes
import momapy.sbgn.core
import momapy.sbgn.pd


@dataclasses.dataclass(frozen=True, kw_only=True)
class Compartment(momapy.sbgn.core.SBGNModelElement):
    """Class for compartments"""

    label: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformation(momapy.sbgn.core.SBGNModelElement):
    """Base class for units of information"""

    label: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeUnitOfInformation(UnitOfInformation):
    """Class for marcomolecule units of information"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureUnitOfInformation(UnitOfInformation):
    """Class for nucleic acid feature units of information"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexUnitOfInformation(UnitOfInformation):
    """Class for complex units of information"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalUnitOfInformation(UnitOfInformation):
    """Class for simple chemical units of information"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityUnitOfInformation(UnitOfInformation):
    """Class for unspecified entity units of information"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbationUnitOfInformation(UnitOfInformation):
    """Class for perturbation units of information"""

    pass


class Activity(momapy.sbgn.core.SBGNModelElement):
    """Class for activities"""

    label: typing.Optional[str] = None
    compartment: typing.Optional[Compartment] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class BiologicalActivity(Activity):
    """Class for biological activities"""

    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Phenotype(Activity):
    """Class for phenotypes"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperatorInput(momapy.sbgn.core.SBGNRole):
    """Class for inputs of logical operators"""

    element: typing.Union[BiologicalActivity, "LogicalOperator"]


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperator(momapy.sbgn.core.SBGNModelElement):
    """Class for logical operators"""

    inputs: frozenset[LogicalOperatorInput] = dataclasses.field(
        default_factory=frozenset
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
class DelayOperator(LogicalOperator):
    """Class for delay operators"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Influence(momapy.sbgn.core.SBGNModelElement):
    """Class for influences"""

    source: BiologicalActivity | LogicalOperator
    target: Activity


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInfluence(Influence):
    """Class for unknown influences"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluence(Influence):
    """Class for positive influences"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NegativeInfluence(Influence):
    """Class for negative influences"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulation(Influence):
    """Class for necessary stimulations"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalReference(momapy.sbgn.core.SBGNRole):
    """Class for references of terminals"""

    element: typing.Union[Activity, Compartment]


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagReference(momapy.sbgn.core.SBGNRole):
    """Class for references of tags"""

    element: typing.Union[Activity, Compartment]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Terminal(momapy.sbgn.core.SBGNModelElement):
    """Class for terminals"""

    label: typing.Optional[str] = None
    refers_to: typing.Optional[TerminalReference] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Tag(momapy.sbgn.core.SBGNModelElement):
    """Class for tags"""

    label: typing.Optional[str] = None
    refers_to: typing.Optional[TagReference] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Submap(momapy.sbgn.core.SBGNModelElement):
    """Class for submaps"""

    label: typing.Optional[str] = None
    terminals: frozenset[Terminal] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNAFModel(momapy.sbgn.core.SBGNModel):
    """Class for SBGN-AF models"""

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

    def is_submodel(self, other: "SBGNAFModel") -> bool:
        """Return `true` if the another given SBGN-AF model is a submodel of the SBGN-AF model, `false` otherwise"""
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
    """Class for SBGN-AF layouts"""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for unspecified entity unit of information layouts"""

    width: float = 12.0
    height: float = 12.0

    def _make_shape(self):
        return momapy.sbgn.pd.UnspecifiedEntityLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for simple chemical unit of information layouts"""

    width: float = 12.0
    height: float = 12.0

    def _make_shape(self):
        return momapy.sbgn.pd.SimpleChemicalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for macromolecule unit of information layouts"""

    width: float = 12.0
    height: float = 12.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for nucleic acid feature unit of information layouts"""

    width: float = 12.0
    height: float = 12.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.NucleicAcidFeatureLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for complex unit of information layouts"""

    width: float = 12.0
    height: float = 12.0
    cut_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.ComplexLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbationUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for perturbation unit of information layouts"""

    width: float = 12.0
    height: float = 12.0
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.PerturbingAgentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for terminal layouts"""

    width: float = 35.0
    height: float = 35.0
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.TerminalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompartmentLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for compartment layouts"""

    width: float = 80.0
    height: float = 80.0
    rounded_corners: float = 5.0
    border_stroke_width: float | None = 3.25

    def _make_shape(self):
        return momapy.sbgn.pd.CompartmentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SubmapLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Class for submap layouts"""

    width: float = 80.0
    height: float = 80.0
    border_stroke_width: float | None = 2.25

    def _make_shape(self):
        return momapy.sbgn.pd.SubmapLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class BiologicalActivityLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for biological activity layouts"""

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Class for phenotype layouts"""

    width: float = 60.0
    height: float = 30.0
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.PhenotypeLayout._make_shape(self)


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
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 3
    )
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
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 3
    )
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
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 3
    )
    _text: typing.ClassVar[str] = "NOT"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class DelayOperatorLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core.SBGNNode,
):
    """Class for delay operator layouts"""

    _font_family: typing.ClassVar[str] = "Cantarell"
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = (
        lambda obj: obj.width / 2
    )
    _text: typing.ClassVar[str] = "τ"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagLayout(momapy.sbgn.pd.TagLayout):
    """Class for tag layouts"""

    width: float = 35.0
    height: float = 35.0
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.TagLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInfluenceLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for unknown influence layouts"""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Diamond._arrowhead_border_drawing_elements(
            self
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluenceLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for positive influence layouts"""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(
            self
        )


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
class NegativeInfluenceLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for negative influence layouts"""

    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Bar._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for logic arc layouts"""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(
            self
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Class for equivalence arc layouts"""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(
            self
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNAFMap(momapy.sbgn.core.SBGNMap):
    """Class for SBGN-AF maps"""

    model: typing.Optional[SBGNAFModel] = None
    layout: typing.Optional[SBGNAFLayout] = None


SBGNAFModelBuilder = momapy.builder.get_or_make_builder_cls(SBGNAFModel)
"""Class for SBGN-AF model builders"""
SBGNAFLayoutBuilder = momapy.builder.get_or_make_builder_cls(SBGNAFLayout)
"""Class for SBGN-AF layout builders"""


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
"""Class for SBGN-AF map builders"""
