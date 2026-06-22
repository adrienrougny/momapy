"""Model classes for SBGN Activity Flow (AF) maps."""

import dataclasses
import typing

from momapy.sbgn.elements import (
    SBGNModelElement,
    SBGNRole,
)
from momapy.sbgn.model import SBGNModel


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitOfInformation(SBGNModelElement):
    """Unit of information for activities and compartments.

    Units of information provide additional information about activities or compartments.
    """

    label: str | None = dataclasses.field(
        default=None,
        metadata={"description": "The label of the unit of information."},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Compartment(SBGNModelElement):
    """Compartment in an SBGN-AF map.

    Compartments represent distinct spatial regions where activities are located.
    """

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the compartment."}
    )
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
class Activity(SBGNModelElement):
    """Activity in an SBGN-AF map.

    Activities represent biological activities or processes.
    """

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the activity."}
    )
    compartment: Compartment | None = dataclasses.field(
        default=None,
        metadata={"description": "The compartment containing this activity."},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class BiologicalActivity(Activity):
    """Biological activity.

    Represents a biological activity with associated units of information.
    """

    units_of_information: frozenset[UnitOfInformation] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "Units of information for the activity."},
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
class LogicalOperatorInput(SBGNRole):
    """Input to a logical operator.

    Represents an input connection to a logical operator.
    """

    referred_element: typing.Union[
        BiologicalActivity,
        typing.ForwardRef("LogicalOperator", module=__name__),
    ] = dataclasses.field(
        metadata={
            "description": "The biological activity or logical operator providing the input."
        }
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class LogicalOperator(SBGNModelElement):
    """Logical operator.

    Represents logical operations (AND, OR, NOT, DELAY) on activities.
    """

    inputs: frozenset[LogicalOperatorInput] = dataclasses.field(
        default_factory=frozenset,
        metadata={"description": "Input connections to the logical operator."},
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
class Influence(SBGNModelElement):
    """Influence between activities.

    Represents an influence from a source activity to a target activity.
    """

    source: BiologicalActivity | LogicalOperator = dataclasses.field(
        metadata={"description": "The source activity or logical operator."}
    )
    target: Activity = dataclasses.field(
        metadata={"description": "The target activity being influenced."}
    )


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
class TerminalReference(SBGNRole):
    """Reference to a terminal."""

    referred_element: Activity | Compartment = dataclasses.field(
        metadata={"description": "The activity or compartment being referenced."}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class TagReference(SBGNRole):
    """Reference to a tag."""

    referred_element: Activity | Compartment = dataclasses.field(
        metadata={"description": "The activity or compartment being referenced."}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Terminal(SBGNModelElement):
    """Terminal element.

    Terminals represent connection points to submaps.
    """

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the terminal."}
    )
    referred_element: TerminalReference | None = dataclasses.field(
        default=None,
        metadata={"description": "The element referred to by the terminal."},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Tag(SBGNModelElement):
    """Tag element.

    Tags provide identifiers that can be referenced from other locations.
    """

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the tag."}
    )
    referred_element: TagReference | None = dataclasses.field(
        default=None,
        metadata={"description": "The element referred to by the tag."},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Submap(SBGNModelElement):
    """Submap element.

    Submaps represent embedded or referenced sub-diagrams.
    """

    label: str | None = dataclasses.field(
        default=None, metadata={"description": "The label of the submap."}
    )
    terminals: frozenset[Terminal] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBGNAFModel(SBGNModel):
    """SBGN-AF model.

    Represents a complete SBGN Activity Flow model.
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
