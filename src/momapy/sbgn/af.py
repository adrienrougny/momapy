"""Classes for SBGN Activity Flow (AF) maps.

This module provides classes for modeling and laying out SBGN-AF maps,
including biological activities, influences, logical operators, and their
visual representations.
"""

import enum
import dataclasses
import typing

import momapy.meta.shapes
import momapy.sbgn.core
import momapy.sbgn.pd


@dataclasses.dataclass(frozen=True, kw_only=True)
class Compartment(momapy.sbgn.core.SBGNModelElement):
    """Compartment in an SBGN-AF map.

    Compartments represent distinct spatial regions where activities are located.

    Attributes:
        label: The label of the compartment.
    """

    label: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformation(momapy.sbgn.core.SBGNModelElement):
    """Unit of information for activities.

    Units of information provide additional annotations about activities,
    such as cellular location or entity type.

    Attributes:
        label: The label of the unit of information.
    """

    label: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeUnitOfInformation(UnitOfInformation):
    """Unit of information for macromolecules."""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureUnitOfInformation(UnitOfInformation):
    """Unit of information for nucleic acid features."""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexUnitOfInformation(UnitOfInformation):
    """Unit of information for complexes."""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalUnitOfInformation(UnitOfInformation):
    """Unit of information for simple chemicals."""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityUnitOfInformation(UnitOfInformation):
    """Unit of information for unspecified entities."""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbationUnitOfInformation(UnitOfInformation):
    """Unit of information for perturbations."""

    pass


class Activity(momapy.sbgn.core.SBGNModelElement):
    """Activity in an SBGN-AF map.

    Activities represent biological activities or processes.

    Attributes:
        label: The label of the activity.
        compartment: The compartment containing this activity.
    """

    label: typing.Optional[str] = None
    compartment: typing.Optional[Compartment] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class BiologicalActivity(Activity):
    """Biological activity.

    Represents a biological activity with associated units of information.

    Attributes:
        units_of_information: Units of information for the activity.
    """

    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Phenotype(Activity):
    """Phenotype activity.

    Represents the manifestation of a phenotype or observable characteristic.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperatorInput(momapy.sbgn.core.SBGNRole):
    """Input to a logical operator.

    Represents an input connection to a logical operator.

    Attributes:
        element: The biological activity or logical operator providing the input.
    """

    element: typing.Union[BiologicalActivity, "LogicalOperator"]


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperator(momapy.sbgn.core.SBGNModelElement):
    """Logical operator.

    Represents logical operations (AND, OR, NOT, DELAY) on activities.

    Attributes:
        inputs: Input connections to the logical operator.
    """

    inputs: frozenset[LogicalOperatorInput] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OrOperator(LogicalOperator):
    """OR logical operator."""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class AndOperator(LogicalOperator):
    """AND logical operator."""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NotOperator(LogicalOperator):
    """NOT logical operator."""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class DelayOperator(LogicalOperator):
    """DELAY logical operator."""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Influence(momapy.sbgn.core.SBGNModelElement):
    """Influence between activities.

    Represents an influence from a source activity to a target activity.

    Attributes:
        source: The source activity or logical operator.
        target: The target activity being influenced.
    """

    source: BiologicalActivity | LogicalOperator
    target: Activity


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInfluence(Influence):
    """Unknown influence."""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluence(Influence):
    """Positive influence."""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NegativeInfluence(Influence):
    """Negative influence."""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulation(Influence):
    """Necessary stimulation."""

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalReference(momapy.sbgn.core.SBGNRole):
    """Reference to a terminal.

    Attributes:
        element: The activity or compartment being referenced.
    """

    element: typing.Union[Activity, Compartment]


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagReference(momapy.sbgn.core.SBGNRole):
    """Reference to a tag.

    Attributes:
        element: The activity or compartment being referenced.
    """

    element: typing.Union[Activity, Compartment]


@dataclasses.dataclass(frozen=True, kw_only=True)
class Terminal(momapy.sbgn.core.SBGNModelElement):
    """Terminal element.

    Terminals represent connection points to submaps.

    Attributes:
        label: The label of the terminal.
        refers_to: Reference to the terminal target.
    """

    label: typing.Optional[str] = None
    refers_to: typing.Optional[TerminalReference] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Tag(momapy.sbgn.core.SBGNModelElement):
    """Tag element.

    Tags provide identifiers that can be referenced from other locations.

    Attributes:
        label: The label of the tag.
        refers_to: Reference to the tagged element.
    """

    label: typing.Optional[str] = None
    refers_to: typing.Optional[TagReference] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Submap(momapy.sbgn.core.SBGNModelElement):
    """Submap element.

    Submaps represent embedded or referenced sub-diagrams.

    Attributes:
        label: The label of the submap.
        terminals: Terminal connection points of the submap.
    """

    label: typing.Optional[str] = None
    terminals: frozenset[Terminal] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNAFModel(momapy.sbgn.core.SBGNModel):
    """SBGN-AF model.

    Represents a complete SBGN Activity Flow model.

    Attributes:
        activities: Activities in the model.
        compartments: Compartments in the model.
        influences: Influences in the model.
        logical_operators: Logical operators in the model.
        submaps: Submaps in the model.
        tags: Tags in the model.
    """

    activities: frozenset[Activity] = dataclasses.field(default_factory=frozenset)
    compartments: frozenset[Compartment] = dataclasses.field(default_factory=frozenset)
    influences: frozenset[Influence] = dataclasses.field(default_factory=frozenset)
    logical_operators: frozenset[LogicalOperator] = dataclasses.field(
        default_factory=frozenset
    )
    submaps: frozenset[Submap] = dataclasses.field(default_factory=frozenset)
    tags: frozenset[Tag] = dataclasses.field(default_factory=frozenset)

    def is_submodel(self, other: "SBGNAFModel") -> bool:
        """Check if another model is a submodel of this model.

        Args:
            other: Another SBGN-AF model to compare against.

        Returns:
            True if other is a submodel of this model, False otherwise.
        """
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
    """SBGN-AF layout.

    Represents the visual layout of an SBGN-AF model.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Layout for unspecified entity units of information."""

    width: float = 12.0
    height: float = 12.0

    def _make_shape(self):
        return momapy.sbgn.pd.UnspecifiedEntityLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Layout for simple chemical units of information."""

    width: float = 12.0
    height: float = 12.0

    def _make_shape(self):
        return momapy.sbgn.pd.SimpleChemicalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Layout for macromolecule units of information."""

    width: float = 12.0
    height: float = 12.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.MacromoleculeLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Layout for nucleic acid feature units of information."""

    width: float = 12.0
    height: float = 12.0
    rounded_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.NucleicAcidFeatureLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Layout for complex units of information."""

    width: float = 12.0
    height: float = 12.0
    cut_corners: float = 5.0

    def _make_shape(self):
        return momapy.sbgn.pd.ComplexLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbationUnitOfInformationLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Layout for perturbation units of information."""

    width: float = 12.0
    height: float = 12.0
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.PerturbingAgentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Layout for terminals."""

    width: float = 35.0
    height: float = 35.0
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.TerminalLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class CompartmentLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Layout for compartments."""

    width: float = 80.0
    height: float = 80.0
    rounded_corners: float = 5.0
    border_stroke_width: float | None = 3.25

    def _make_shape(self):
        return momapy.sbgn.pd.CompartmentLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SubmapLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Layout for submaps."""

    width: float = 80.0
    height: float = 80.0
    border_stroke_width: float | None = 2.25

    def _make_shape(self):
        return momapy.sbgn.pd.SubmapLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class BiologicalActivityLayout(
    momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode
):
    """Layout for biological activities."""

    width: float = 60.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Rectangle(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhenotypeLayout(momapy.sbgn.core._SimpleMixin, momapy.sbgn.core.SBGNNode):
    """Layout for phenotypes."""

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
    """Layout for AND operators."""

    _font_family: typing.ClassVar[str] = "DejaVu Sans"
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
    """Layout for OR operators."""

    _font_family: typing.ClassVar[str] = "DejaVu Sans"
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
    """Layout for NOT operators."""

    _font_family: typing.ClassVar[str] = "DejaVu Sans"
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
class DelayOperatorLayout(
    momapy.sbgn.core._ConnectorsMixin,
    momapy.sbgn.core._SimpleMixin,
    momapy.sbgn.core._TextMixin,
    momapy.sbgn.core.SBGNNode,
):
    """Layout for DELAY operators."""

    _font_family: typing.ClassVar[str] = "DejaVu Sans"
    _font_fill: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.coloring.black
    _font_stroke: typing.ClassVar[
        momapy.coloring.Color | momapy.drawing.NoneValueType
    ] = momapy.drawing.NoneValue
    _font_size_func: typing.ClassVar[typing.Callable] = lambda obj: obj.width / 2
    _text: typing.ClassVar[str] = "τ"
    width: float = 30.0
    height: float = 30.0

    def _make_shape(self):
        return momapy.meta.shapes.Ellipse(
            position=self.position, width=self.width, height=self.height
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagLayout(momapy.sbgn.pd.TagLayout):
    """Layout for tags."""

    width: float = 35.0
    height: float = 35.0
    direction: momapy.core.Direction = momapy.core.Direction.RIGHT
    angle: float = 70.0

    def _make_shape(self):
        return momapy.sbgn.pd.TagLayout._make_shape(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnknownInfluenceLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Layout for unknown influences."""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Diamond._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluenceLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Layout for positive influences."""

    arrowhead_height: float = 10.0
    arrowhead_width: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Triangle._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulationLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Layout for necessary stimulations."""

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
class NegativeInfluenceLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Layout for negative influences."""

    arrowhead_height: float = 10.0

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.Bar._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicArcLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Layout for logic arcs."""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class EquivalenceArcLayout(momapy.sbgn.core.SBGNSingleHeadedArc):
    """Layout for equivalence arcs."""

    def _arrowhead_border_drawing_elements(self):
        return momapy.meta.arcs.PolyLine._arrowhead_border_drawing_elements(self)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNAFMap(momapy.sbgn.core.SBGNMap):
    """SBGN-AF map.

    Represents a complete SBGN Activity Flow map with model and layout.

    Attributes:
        model: The SBGN-AF model.
        layout: The visual layout of the map.
    """

    model: typing.Optional[SBGNAFModel] = None
    layout: typing.Optional[SBGNAFLayout] = None


SBGNAFModelBuilder = momapy.builder.get_or_make_builder_cls(SBGNAFModel)
"""Builder class for SBGNAFModel."""
SBGNAFLayoutBuilder = momapy.builder.get_or_make_builder_cls(SBGNAFLayout)
"""Builder class for SBGNAFLayout."""


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
"""Builder class for SBGNAFMap."""
