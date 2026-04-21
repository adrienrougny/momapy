"""Model classes for SBGN Activity Flow (AF) maps."""

import dataclasses
import sys
import typing

import momapy.sbgn.elements
import momapy.sbgn.model


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformation(momapy.sbgn.elements.SBGNModelElement):
    """Unit of information for activities and compartments.

    Units of information provide additional information about activities or compartments.

    Attributes:
        label: The label of the unit of information.
    """

    label: str | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Compartment(momapy.sbgn.elements.SBGNModelElement):
    """Compartment in an SBGN-AF map.

    Compartments represent distinct spatial regions where activities are located.

    Attributes:
        label: The label of the compartment.
    """

    label: str | None = None
    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MacromoleculeUnitOfInformation(UnitOfInformation):
    """Unit of information typing a biological activity as a macromolecule.

    Rendered as an SBGN macromolecule glyph embedded in the activity node.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NucleicAcidFeatureUnitOfInformation(UnitOfInformation):
    """Unit of information typing a biological activity as a nucleic acid feature.

    Rendered as an SBGN nucleic acid feature glyph embedded in the activity node.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class ComplexUnitOfInformation(UnitOfInformation):
    """Unit of information typing a biological activity as a complex.

    Rendered as an SBGN complex glyph embedded in the activity node.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleChemicalUnitOfInformation(UnitOfInformation):
    """Unit of information typing a biological activity as a simple chemical.

    Rendered as an SBGN simple chemical glyph embedded in the activity node.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnspecifiedEntityUnitOfInformation(UnitOfInformation):
    """Unit of information typing a biological activity as an unspecified entity.

    Used when the underlying entity class is unknown or deliberately abstract.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PerturbationUnitOfInformation(UnitOfInformation):
    """Unit of information typing a biological activity as a perturbation.

    Denotes an external influence (drug, stimulus, mutation) acting on the system.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Activity(momapy.sbgn.elements.SBGNModelElement):
    """Activity in an SBGN-AF map.

    Activities represent biological activities or processes.

    Attributes:
        label: The label of the activity.
        compartment: The compartment containing this activity.
    """

    label: str | None = None
    compartment: Compartment | None = None


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

    Represents an observable characteristic of the system — a system-level
    outcome produced by the combination of biological activities rather than
    an individual activity itself.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperatorInput(momapy.sbgn.elements.SBGNRole):
    """Input to a logical operator.

    Represents an input connection to a logical operator.

    Attributes:
        element: The biological activity or logical operator providing the input.
    """

    element: typing.Union[
        BiologicalActivity,
        typing.ForwardRef("LogicalOperator", module=sys.modules[__name__]),
    ]


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperator(momapy.sbgn.elements.SBGNModelElement):
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
class DelayOperator(LogicalOperator):
    """Logical DELAY operator.

    The output mirrors the input after a delay; used to model time-shifted influences.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class Influence(momapy.sbgn.elements.SBGNModelElement):
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
    """Influence of unspecified sign.

    Used when the regulatory effect of the source on the target is not known.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class PositiveInfluence(Influence):
    """Positive (stimulating) influence.

    The source increases the activity of the target.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NegativeInfluence(Influence):
    """Negative (inhibiting) influence.

    The source decreases the activity of the target.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class NecessaryStimulation(Influence):
    """Necessary stimulation.

    The target requires the source to be active; without it the target cannot be active.
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class TerminalReference(momapy.sbgn.elements.SBGNRole):
    """Reference to a terminal.

    Attributes:
        element: The activity or compartment being referenced.
    """

    element: Activity | Compartment


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagReference(momapy.sbgn.elements.SBGNRole):
    """Reference to a tag.

    Attributes:
        element: The activity or compartment being referenced.
    """

    element: Activity | Compartment


@dataclasses.dataclass(frozen=True, kw_only=True)
class Terminal(momapy.sbgn.elements.SBGNModelElement):
    """Terminal element.

    Terminals represent connection points to submaps.

    Attributes:
        label: The label of the terminal.
        refers_to: Reference to the terminal target.
    """

    label: str | None = None
    refers_to: TerminalReference | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Tag(momapy.sbgn.elements.SBGNModelElement):
    """Tag element.

    Tags provide identifiers that can be referenced from other locations.

    Attributes:
        label: The label of the tag.
        refers_to: Reference to the tagged element.
    """

    label: str | None = None
    refers_to: TagReference | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Submap(momapy.sbgn.elements.SBGNModelElement):
    """Submap element.

    Submaps represent embedded or referenced sub-diagrams.

    Attributes:
        label: The label of the submap.
        terminals: Terminal connection points of the submap.
    """

    label: str | None = None
    terminals: frozenset[Terminal] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNAFModel(momapy.sbgn.model.SBGNModel):
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
            and self.submaps.issubset(other.submaps)
            and self.tags.issubset(other.tags)
        )
