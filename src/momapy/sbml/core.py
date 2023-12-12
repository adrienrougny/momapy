import dataclasses
import typing
import uuid

import momapy.core


@dataclasses.dataclass(frozen=True)
class Annotation(momapy.core.ModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class Notes(momapy.core.ModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class SBOTerm(momapy.core.ModelElement):
    pass


@dataclasses.dataclass(frozen=True)
class SBase(momapy.core.ModelElement):
    name: typing.Optional[str] = None
    metaid: typing.Optional[typing.Union[str, uuid.UUID]] = None
    sbo_term: typing.Optional[SBOTerm] = None
    notes: typing.Optional[Notes] = None
    annotations: typing.Optional[Annotation] = None


@dataclasses.dataclass(frozen=True)
class Compartment(SBase):
    pass


@dataclasses.dataclass(frozen=True)
class Species(SBase):
    compartment: typing.Optional[Compartment] = None


@dataclasses.dataclass(frozen=True)
class SimpleSpeciesReference(SBase):
    species: typing.Optional[Species] = None


@dataclasses.dataclass(frozen=True)
class ModifierSpeciesReference(SimpleSpeciesReference):
    pass


@dataclasses.dataclass(frozen=True)
class SpeciesReference(SimpleSpeciesReference):
    stoichiometry: typing.Optional[int] = None


@dataclasses.dataclass(frozen=True)
class Reaction(SBase):
    reversible: bool = False
    compartment: typing.Optional[Compartment] = None
    reactants: frozenset[SpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )
    products: frozenset[SpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )
    modulators: frozenset[ModifierSpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class Model(SBase, momapy.core.Model):
    compartments: frozenset[Compartment] = dataclasses.field(
        default_factory=frozenset
    )
    species: frozenset[Species] = dataclasses.field(default_factory=frozenset)
    reactions: frozenset[Reaction] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True)
class SBML(SBase):
    xmlns: str = "http://www.sbml.org/sbml/level3/version2/core"
    level: int = 3
    version: int = 2
    model: typing.Optional[Model] = None
