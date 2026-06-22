"""Concrete SBML model classes.

This module provides dataclasses representing SBML model elements including
compartments, species, reactions, and annotations using BioModels qualifiers.

Examples:
    ```python
    from momapy.sbml.model import Compartment, Species, SBMLModel
    compartment = Compartment(name="cytosol")
    species = Species(name="glucose", compartment=compartment)
    model = SBMLModel(
        name="glycolysis",
        compartments={compartment},
        species={species},
    )
    ```
"""

import dataclasses
import enum
import typing

from momapy.core.model import Model
from momapy.sbml.elements import SBMLModelElement


class BiomodelQualifier(enum.Enum):
    """Abstract base class for BioModels.net qualifiers.

    BioModels qualifiers are used in RDF annotations to describe the relationship
    between model elements and external resources.
    """

    pass


class BQModel(BiomodelQualifier):
    """BioModels.net model qualifiers.

    These qualifiers describe the relationship between the model and
    external resources such as publications or databases.

    Attributes:
        HAS_INSTANCE: The resource is an instance of this model.
        IS: The resource is exactly this model.
        IS_DERIVED_FROM: The model is derived from the resource.
        IS_DESCRIBED_BY: The resource describes the model.
        IS_INSTANCE_OF: The model is an instance of the resource.
    """

    HAS_INSTANCE = "hasInstance"
    IS = "is"
    IS_DERIVED_FROM = "isDerivedFrom"
    IS_DESCRIBED_BY = "isDescribedBy"
    IS_INSTANCE_OF = "isInstanceOf"


class BQBiol(BiomodelQualifier):
    """BioModels.net biology qualifiers.

    These qualifiers describe the relationship between biological elements
    and external resources.

    Attributes:
        ENCODES: The element encodes the resource.
        HAS_PART: The element has the resource as a part.
        HAS_PROPERTY: The element has the resource as a property.
        HAS_VERSION: The element has the resource as a version.
        IS: The element is exactly the resource.
        IS_DESCRIBED_BY: The resource describes the element.
        IS_ENCODED_BY: The element is encoded by the resource.
        IS_HOMOLOG_TO: The element is homologous to the resource.
        IS_PART_OF: The element is part of the resource.
        IS_PROPERTY_OF: The element is a property of the resource.
        IS_VERSION_OF: The element is a version of the resource.
        OCCURS_IN: The process occurs in the resource.
        HAS_TAXON: The element has the resource as a taxon.
    """

    ENCODES = "encodes"
    HAS_PART = "hasPart"
    HAS_PROPERTY = "hasProperty"
    HAS_VERSION = "hasVersion"
    IS = "is"
    IS_DESCRIBED_BY = "isDescribedBy"
    IS_ENCODED_BY = "isEncodedBy"
    IS_HOMOLOG_TO = "isHomologTo"
    IS_PART_OF = "isPartOf"
    IS_PROPERTY_OF = "isPropertyOf"
    IS_VERSION_OF = "isVersionOf"
    OCCURS_IN = "occursIn"
    HAS_TAXON = "hasTaxon"


@dataclasses.dataclass(frozen=True, kw_only=True)
class RDFAnnotation:
    """RDF annotation linking model elements to external resources.

    RDF annotations are metadata attached to model elements, not model
    entities themselves, and are therefore plain frozen dataclasses rather
    than ``ModelElement`` subclasses.

    Examples:
        ```python
        from momapy.sbml.model import RDFAnnotation, BQBiol
        annotation = RDFAnnotation(
            qualifier=BQBiol.IS,
            resources={"https://identifiers.org/chebi:4167"}
        )
        ```
    """

    qualifier: BiomodelQualifier = dataclasses.field(
        metadata={"description": "The BioModels qualifier describing the relationship."}
    )
    resources: frozenset[str] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Compartment(SBMLModelElement):
    """SBML compartment representing a bounded region.

    A compartment defines a container where species are located.

    Examples:
        ```python
        cytosol = Compartment(name="cytosol")
        nucleus = Compartment(name="nucleus", outside=cytosol)
        ```
    """

    outside: typing.Optional[
        typing.ForwardRef("Compartment", module="momapy.sbml.model")
    ] = dataclasses.field(
        default=None,
        metadata={
            "description": "Optional outer compartment for hierarchical nesting."
        },
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Species(SBMLModelElement):
    """SBML species representing a pool of entities.

    A species represents a population of chemically identical entities
    (molecules, ions, etc.) located in a specific compartment.

    Examples:
        ```python
        compartment = Compartment(name="cytosol")
        glucose = Species(name="glucose", compartment=compartment)
        ```
    """

    compartment: Compartment | None = dataclasses.field(
        default=None,
        metadata={"description": "The compartment containing this species."},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleSpeciesReference(SBMLModelElement):
    """Base class for species references in reactions."""

    referred_element: Species = dataclasses.field(
        metadata={"description": "The species being referenced."}
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModifierSpeciesReference(SimpleSpeciesReference):
    """Reference to a species that modifies a reaction.

    Modifier species influence reaction kinetics without being
    consumed or produced (e.g., catalysts, inhibitors).
    """

    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SpeciesReference(SimpleSpeciesReference):
    """Reference to a reactant or product species.

    Examples:
        ```python
        species = Species(name="ATP", compartment=compartment)
        ref = SpeciesReference(referred_element=species, stoichiometry=2)
        ```
    """

    stoichiometry: float | None = dataclasses.field(
        default=None,
        metadata={"description": "Optional stoichiometric coefficient."},
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Reaction(SBMLModelElement):
    """SBML reaction representing a biochemical transformation.

    Reactions describe the conversion of reactants into products,
    potentially influenced by modifiers.

    Examples:
        ```python
        reaction = Reaction(
            name="hexokinase",
            reversible=False,
            reactants={glucose_ref, atp_ref},
            products={g6p_ref, adp_ref}
        )
        ```
    """

    reversible: bool = dataclasses.field(
        metadata={"description": "Whether the reaction can proceed in both directions."}
    )
    compartment: Compartment | None = dataclasses.field(
        default=None,
        metadata={"description": "Optional compartment where the reaction occurs."},
    )
    reactants: frozenset[SpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )
    products: frozenset[SpeciesReference] = dataclasses.field(default_factory=frozenset)
    modifiers: frozenset[ModifierSpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBMLModel(Model):
    """SBML model container.

    Models aggregate compartments, species, and reactions into a
    complete biological system description.

    Examples:
        ```python
        model = SBMLModel(
            name="glycolysis",
            compartments={cytosol},
            species={glucose, atp, g6p},
            reactions={hexokinase}
        )
        ```
    """

    name: str | None = dataclasses.field(
        default=None,
        metadata={"description": "Human-readable name of the model."},
    )
    sbo_term: str | None = dataclasses.field(
        default=None,
        metadata={
            "description": "Optional SBO term identifier for semantic annotation."
        },
    )
    metaid: str | None = dataclasses.field(
        default=None,
        compare=False,
        hash=False,
        metadata={"description": "Optional metadata identifier for RDF annotations."},
    )
    compartments: frozenset[Compartment] = dataclasses.field(default_factory=frozenset)
    species: frozenset[Species] = dataclasses.field(default_factory=frozenset)
    reactions: frozenset[Reaction] = dataclasses.field(default_factory=frozenset)

    def is_submodel(self, other: "SBMLModel") -> None:
        """Return whether the model is a submodel of another model."""
        pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBML(SBMLModelElement):
    """Root container for SBML documents.

    Represents the top-level SBML element containing model metadata
    and the model definition.

    Examples:
        ```python
        sbml = SBML(
            model=SBMLModel(name="glycolysis"),
            level=3,
            version=2
        )
        ```
    """

    xmlns: str = dataclasses.field(
        default="http://www.sbml.org/sbml/level3/version2/core",
        metadata={"description": "XML namespace for the SBML version."},
    )
    level: int = dataclasses.field(
        default=3,
        metadata={"description": "SBML level (version)."},
    )
    version: int = dataclasses.field(
        default=2,
        metadata={"description": "SBML version within the level."},
    )
    model: SBMLModel | None = dataclasses.field(
        default=None,
        metadata={"description": "The model contained in this SBML document."},
    )
