import dataclasses
import typing

import momapy.core


@dataclass(frozen=True)
class Annotation(momapy.core.ModelElement):
    pass


@dataclass(frozen=True)
class Notes(momapy.core.ModelElement):
    pass


@dataclass(frozen=True)
class SBOTerm(momapy.core.ModelElement):
    pass


@dataclass(frozen=True)
class SBase(momapy.core.ModelElement):
    name: typing.Optional[str] = None
    metaid: typing.Optional[typing.Union[str, uuid.UUID]] = None
    sboTerm: typing.Optional[SBOTerm] = None
    notes: typing.Optional[Notes] = None
    annotations: typing.Optional[Annotation] = None


@dataclass(frozen=True)
class SBML(SBase):
    xmlns: str = "http://www.sbml.org/sbml/level3/version2/core"
    level: int = 3
    version: int = 2
    model: typing.Optional[Model] = None


@dataclass(frozen=True)
class Model(SBase):
    compartments: frozenset[Compartment] = dataclasses.field(
        default_factory=frozenset
    )
    species: frozenset[Species] = dataclasses.field(default_factory=frozenset)
    reactions: frozenset[Reaction] = dataclasses.field(
        default_factory=frozenset
    )


@dataclass(frozen=True)
class Compartment(SBase):
    pass


@dataclass(frozen=True)
class Species(SBase):
    compartment: typing.Optional[Compartment] = None


@dataclass(frozen=True)
class SpeciesReference(SBase):
    species: Optional[Species] = None


@dataclass(frozen=True)
class SimpleSpeciesReference(SpeciesReference):
    stoichiometry: Optional[int] = None


@dataclass(frozen=True)
class ModifierSpeciesReference(SpeciesReference):
    pass


@dataclass(frozen=True)
class Reaction(SBase):
    reversible: bool = False
    compartment: typing.Optional[Compartment] = None
    reactants: frozenset[SimpleSpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )
    products: frozenset[SimpleSpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )
    modulators: frozenset[ModifierSpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )
