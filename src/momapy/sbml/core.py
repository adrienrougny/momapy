import dataclasses
import typing

import momapy.core


@dataclasses.dataclass(frozen=True, kw_only=True)
class RDFAnnotation(momapy.core.ModelElement):
    qualifier: str
    resources: frozenset[str] = dataclasses.field(default_factory=frozenset)


# to be defined
@dataclasses.dataclass(frozen=True, kw_only=True)
class SBOTerm(momapy.core.ModelElement):
    pass


# abstract
@dataclasses.dataclass(frozen=True, kw_only=True)
class SBase(momapy.core.ModelElement):
    name: str | None = None
    sbo_term: SBOTerm | None = None
    metaid: str | None = dataclasses.field(
        default=None, compare=False, hash=False
    )


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
class Model(SBase, momapy.core.Model):
    compartments: frozenset[Compartment] = dataclasses.field(
        default_factory=frozenset
    )
    species: frozenset[Species] = dataclasses.field(default_factory=frozenset)
    reactions: frozenset[Reaction] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBML(SBase):
    xmlns: str = "http://www.sbml.org/sbml/level3/version2/core"
    level: int = 3
    version: int = 2
    model: Model | None = None
