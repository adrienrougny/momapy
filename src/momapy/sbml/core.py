"""Core classes for SBML (Systems Biology Markup Language) maps.

This module provides dataclasses representing SBML model elements including
compartments, species, reactions, and annotations using BioModels qualifiers.

Example:
    >>> from momapy.sbml.core import Compartment, Species, Model
    >>> compartment = Compartment(name="cytosol")
    >>> species = Species(name="glucose", compartment=compartment)
    >>> model = Model(name="glycolysis", compartments={compartment}, species={species})
"""

import dataclasses
import typing
import enum

import momapy.core


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
class RDFAnnotation(momapy.core.ModelElement):
    """RDF annotation linking model elements to external resources.

    Attributes:
        qualifier: The BioModels qualifier describing the relationship.
        resources: Set of resource URIs linked to this annotation.

    Example:
        >>> from momapy.sbml.core import RDFAnnotation, BQBiol
        >>> annotation = RDFAnnotation(
        ...     qualifier=BQBiol.IS,
        ...     resources={"https://identifiers.org/chebi:4167"}
        ... )
    """

    qualifier: BiomodelQualifier
    resources: frozenset[str] = dataclasses.field(default_factory=frozenset)


# to be defined
@dataclasses.dataclass(frozen=True, kw_only=True)
class SBOTerm(momapy.core.ModelElement):
    """SBO (Systems Biology Ontology) term annotation.

    SBO terms provide standardized vocabulary for describing model elements.
    """

    pass


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class SBase(momapy.core.ModelElement):
    """Abstract base class for all SBML elements.

    SBase provides common attributes shared by all SBML components.

    Attributes:
        name: Human-readable name of the element.
        sbo_term: Optional SBO term for semantic annotation.
        metaid: Optional metadata identifier for RDF annotations.
    """

    name: str | None = None
    sbo_term: SBOTerm | None = None
    metaid: str | None = dataclasses.field(default=None, compare=False, hash=False)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Compartment(SBase):
    """SBML compartment representing a bounded region.

    A compartment defines a container where species are located.

    Attributes:
        outside: Optional outer compartment for hierarchical nesting.

    Example:
        >>> cytosol = Compartment(name="cytosol")
        >>> nucleus = Compartment(name="nucleus", outside=cytosol)
    """

    outside: typing.Optional[
        typing.ForwardRef("Compartment", module="momapy.sbml.core")
    ] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Species(SBase):
    """SBML species representing a pool of entities.

    A species represents a population of chemically identical entities
    (molecules, ions, etc.) located in a specific compartment.

    Attributes:
        compartment: The compartment containing this species.

    Example:
        >>> compartment = Compartment(name="cytosol")
        >>> glucose = Species(name="glucose", compartment=compartment)
    """

    compartment: Compartment | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleSpeciesReference(SBase):
    """Base class for species references in reactions.

    Attributes:
        referred_species: The species being referenced.
    """

    referred_species: Species


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

    Attributes:
        stoichiometry: Optional stoichiometric coefficient.

    Example:
        >>> species = Species(name="ATP", compartment=compartment)
        >>> ref = SpeciesReference(referred_species=species, stoichiometry=2)
    """

    stoichiometry: float | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Reaction(SBase):
    """SBML reaction representing a biochemical transformation.

    Reactions describe the conversion of reactants into products,
    potentially influenced by modifiers.

    Attributes:
        reversible: Whether the reaction can proceed in both directions.
        compartment: Optional compartment where the reaction occurs.
        reactants: Set of species consumed by the reaction.
        products: Set of species produced by the reaction.
        modifiers: Set of species that modify the reaction.

    Example:
        >>> reaction = Reaction(
        ...     name="hexokinase",
        ...     reversible=False,
        ...     reactants={glucose_ref, atp_ref},
        ...     products={g6p_ref, adp_ref}
        ... )
    """

    reversible: bool
    compartment: Compartment | None = None
    reactants: frozenset[SpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )
    products: frozenset[SpeciesReference] = dataclasses.field(default_factory=frozenset)
    modifiers: frozenset[ModifierSpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Model(SBase, momapy.core.Model):
    """SBML model container.

    Models aggregate compartments, species, and reactions into a
    complete biological system description.

    Attributes:
        compartments: Set of compartments in the model.
        species: Set of species in the model.
        reactions: Set of reactions in the model.

    Example:
        >>> model = Model(
        ...     name="glycolysis",
        ...     compartments={cytosol},
        ...     species={glucose, atp, g6p},
        ...     reactions={hexokinase}
        ... )
    """

    compartments: frozenset[Compartment] = dataclasses.field(default_factory=frozenset)
    species: frozenset[Species] = dataclasses.field(default_factory=frozenset)
    reactions: frozenset[Reaction] = dataclasses.field(default_factory=frozenset)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBML(SBase):
    """Root container for SBML documents.

    Represents the top-level SBML element containing model metadata
    and the model definition.

    Attributes:
        xmlns: XML namespace for the SBML version.
        level: SBML level (version).
        version: SBML version within the level.
        model: The model contained in this SBML document.

    Example:
        >>> sbml = SBML(
        ...     model=Model(name="glycolysis"),
        ...     level=3,
        ...     version=2
        ... )
    """

    xmlns: str = "http://www.sbml.org/sbml/level3/version2/core"
    level: int = 3
    version: int = 2
    model: Model | None = None
