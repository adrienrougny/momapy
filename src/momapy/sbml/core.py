import dataclasses
import typing
import enum

import momapy.core


class BiomodelQualifier(enum.Enum):
    """Abstract class for http://biomodels.net/ qualifiers"""

    pass


class BQModel(BiomodelQualifier):
    """Class for http://biomodels.net/model-qualifiers/ qualifiers"""

    HAS_INSTANCE = "hasInstance"
    IS = "is"
    IS_DERIVED_FROM = "isDerivedFrom"
    IS_DESCRIBED_BY = "isDescribedBy"
    IS_INSTANCE_OF = "isInstanceOf"


class BQBiol(BiomodelQualifier):
    """Class for http://biomodels.net/biology-qualifiers/ qualifiers"""

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
    qualifier: BiomodelQualifier
    resources: frozenset[str] = dataclasses.field(default_factory=frozenset)


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class SBase(momapy.core.ModelElement):
    id_: str | None = None
    name: str | None = None
    sbo_term: str | None = None
    metaid: str | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Compartment(SBase):
    outside: typing.Optional[
        typing.ForwardRef("Compartment", module="momapy.sbml.core")
    ] = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Species(SBase):
    compartment: Compartment | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class SimpleSpeciesReference(SBase):
    referred_species: Species


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModifierSpeciesReference(SimpleSpeciesReference):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SpeciesReference(SimpleSpeciesReference):
    stoichiometry: int | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class Reaction(SBase):
    reversible: bool
    compartment: Compartment | None = None
    reactants: frozenset[SpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )
    products: frozenset[SpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )
    modifiers: frozenset[ModifierSpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBMLModel(SBase, momapy.core.Model):
    compartments: frozenset[Compartment] = dataclasses.field(
        default_factory=frozenset
    )
    species: frozenset[Species] = dataclasses.field(default_factory=frozenset)
    reactions: frozenset[Reaction] = dataclasses.field(
        default_factory=frozenset
    )

    def is_submodel(self, other):  # TODO
        return None


SBMLModelBuilder = momapy.builder.get_or_make_builder_cls(SBMLModel)
