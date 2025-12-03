"""Classes for SBML maps"""
from __future__ import annotations

import dataclasses
import typing
import enum

import momapy.core
import momapy.builder


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


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBOTerm(momapy.core.ModelElement):
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBase(momapy.core.ModelElement):
    name: str | None = None
    sbo_term: SBOTerm | None = None
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
class KineticLaw(SBase):
    # math is intentionally not parsed / used for GEMs
    math: str | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class SpeciesReference(SimpleSpeciesReference):
    stoichiometry: float | None = None


@dataclasses.dataclass(frozen=True, kw_only=True)
class GeneProduct(SBase):
    id_: str
    label: str | None = None

    def associated_reactions(self, model: "SBMLModel"):
        from momapy.sbml.core import GeneProductAssociation, GeneProductRef

        def contains_gene(gpa):
            """Recursively check if this gene appears in a GPR tree."""
            if gpa is None:
                return False

            if isinstance(gpa, GeneProductRef):
                return gpa.gene_product is self

            if isinstance(gpa, GeneProductAssociation):
                return any(contains_gene(child) for child in gpa.children)

            return False

        return [rx for rx in model.reactions if contains_gene(rx.gene_association)]



@dataclasses.dataclass(frozen=True, kw_only=True)
class GeneProductRef(momapy.core.ModelElement):
    gene_product: GeneProduct


@dataclasses.dataclass(frozen=True, kw_only=True)
class GeneProductAssociation(momapy.core.ModelElement):
    operator: str  # "and" | "or"
    children: tuple[
        typing.Union["GeneProductAssociation", GeneProductRef],
        ...
    ]


@dataclasses.dataclass(frozen=True, kw_only=True)
class FluxObjective(momapy.core.ModelElement):
    reaction: "Reaction" | None = None
    reaction_id: str | None = None
    coefficient: float = 1.0


@dataclasses.dataclass(frozen=True, kw_only=True)
class Objective(SBase):
    id_: str
    type: str = "maximize"  # "maximize" / "minimize"
    flux_objectives: frozenset[FluxObjective] = dataclasses.field(
        default_factory=frozenset
    )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Reaction(SBase):
    reversible: bool
    compartment: Compartment | None = None
    reactants: frozenset[SpeciesReference] = dataclasses.field(default_factory=frozenset)
    products: frozenset[SpeciesReference] = dataclasses.field(default_factory=frozenset)
    modifiers: frozenset[ModifierSpeciesReference] = dataclasses.field(
        default_factory=frozenset
    )
    kinetic_law: KineticLaw | None = None
    gene_association: GeneProductAssociation | None = None

    lower_flux_bound: float | None = None
    upper_flux_bound: float | None = None


    def safe_gpr_string(self) -> str:

        from momapy.sbml.core import GeneProductAssociation, GeneProductRef

        def rec(node):
            if node is None:
                return "None"
            if isinstance(node, GeneProductRef):
                return node.gene_product.id_
            if isinstance(node, GeneProductAssociation):
                if not node.children:
                    return "None"
                return (" " + node.operator.upper() + " ").join(
                    rec(child) for child in node.children
                )
            return "None"

        if self.gene_association is None:
            return "None"
        return f"({rec(self.gene_association)})"


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBMLModel(SBase, momapy.core.Model):
    compartments: frozenset[Compartment] = dataclasses.field(default_factory=frozenset)
    species: frozenset[Species] = dataclasses.field(default_factory=frozenset)
    genes: frozenset[GeneProduct] = dataclasses.field(default_factory=frozenset)
    reactions: frozenset[Reaction] = dataclasses.field(default_factory=frozenset)

    objective: Objective | None = None


    def is_submodel(self, other):
        return None


    def safe_objective_id(self) -> str | None:
        return self.objective.id_ if self.objective is not None else None

    def safe_objective_type(self) -> str | None:
        return self.objective.type if self.objective is not None else None

    def safe_flux_objectives(self) -> list[FluxObjective]:
        if self.objective is None:
            return []
        return list(self.objective.flux_objectives)


@dataclasses.dataclass(frozen=True, kw_only=True)
class SBML(SBase):
    xmlns: str = "http://www.sbml.org/sbml/level3/version2/core"
    level: int = 3
    version: int = 2
    model: SBMLModel | None = None


SBMLModelBuilder = momapy.builder.get_or_make_builder_cls(SBMLModel)
