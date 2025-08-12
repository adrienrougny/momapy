"""Classes for reading CellDesigner files (extended SBML)"""

import os
import collections
import math
import typing

import lxml.objectify
import frozendict

import momapy.core
import momapy.geometry
import momapy.positioning
import momapy.io
import momapy.coloring
import momapy.celldesigner.core
import momapy.sbml.core


class CellDesignerReader(momapy.io.Reader):
    """Class for CellDesigner reader objects"""

    _DEFAULT_FONT_FAMILY = "Helvetica"
    _DEFAULT_FONT_SIZE = 12.0
    _DEFAULT_MODIFICATION_FONT_SIZE = 9.0
    _DEFAULT_FONT_FILL = momapy.coloring.black
    _CD_NAMESPACE = "http://www.sbml.org/2001/ns/celldesigner"
    _RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    _KEY_TO_CLASS = {
        (
            "TEMPLATE",
            "GENERIC",
        ): momapy.celldesigner.core.GenericProteinTemplate,
        (
            "TEMPLATE",
            "ION_CHANNEL",
        ): momapy.celldesigner.core.IonChannelTemplate,
        ("TEMPLATE", "RECEPTOR"): momapy.celldesigner.core.ReceptorTemplate,
        (
            "TEMPLATE",
            "TRUNCATED",
        ): momapy.celldesigner.core.TruncatedProteinTemplate,
        ("TEMPLATE", "GENE"): momapy.celldesigner.core.GeneTemplate,
        ("TEMPLATE", "RNA"): momapy.celldesigner.core.RNATemplate,
        (
            "TEMPLATE",
            "ANTISENSE_RNA",
        ): momapy.celldesigner.core.AntisenseRNATemplate,
        ("SPECIES", "GENERIC"): (
            momapy.celldesigner.core.GenericProtein,
            momapy.celldesigner.core.momapy.celldesigner.core.GenericProteinLayout,
        ),
        ("SPECIES", "ION_CHANNEL"): (
            momapy.celldesigner.core.IonChannel,
            momapy.celldesigner.core.IonChannelLayout,
        ),
        ("SPECIES", "RECEPTOR"): (
            momapy.celldesigner.core.Receptor,
            momapy.celldesigner.core.ReceptorLayout,
        ),
        ("SPECIES", "TRUNCATED"): (
            momapy.celldesigner.core.TruncatedProtein,
            momapy.celldesigner.core.TruncatedProteinLayout,
        ),
        ("SPECIES", "GENE"): (
            momapy.celldesigner.core.Gene,
            momapy.celldesigner.core.GeneLayout,
        ),
        ("SPECIES", "RNA"): (
            momapy.celldesigner.core.RNA,
            momapy.celldesigner.core.RNALayout,
        ),
        ("SPECIES", "ANTISENSE_RNA"): (
            momapy.celldesigner.core.AntisenseRNA,
            momapy.celldesigner.core.AntisenseRNALayout,
        ),
        ("SPECIES", "PHENOTYPE"): (
            momapy.celldesigner.core.Phenotype,
            momapy.celldesigner.core.PhenotypeLayout,
        ),
        ("SPECIES", "ION"): (
            momapy.celldesigner.core.Ion,
            momapy.celldesigner.core.IonLayout,
        ),
        ("SPECIES", "SIMPLE_MOLECULE"): (
            momapy.celldesigner.core.SimpleMolecule,
            momapy.celldesigner.core.SimpleMoleculeLayout,
        ),
        ("SPECIES", "DRUG"): (
            momapy.celldesigner.core.Drug,
            momapy.celldesigner.core.DrugLayout,
        ),
        ("SPECIES", "COMPLEX"): (
            momapy.celldesigner.core.Complex,
            momapy.celldesigner.core.ComplexLayout,
        ),
        ("SPECIES", "UNKNOWN"): (
            momapy.celldesigner.core.Unknown,
            momapy.celldesigner.core.UnknownLayout,
        ),
        ("SPECIES", "DEGRADED"): (
            momapy.celldesigner.core.Degraded,
            momapy.celldesigner.core.DegradedLayout,
        ),
        ("REACTION", "STATE_TRANSITION"): (
            momapy.celldesigner.core.StateTransition,
            momapy.celldesigner.core.StateTransitionLayout,
        ),
        ("REACTION", "KNOWN_TRANSITION_OMITTED"): (
            momapy.celldesigner.core.KnownTransitionOmitted,
            momapy.celldesigner.core.KnownTransitionOmittedLayout,
        ),
        ("REACTION", "UNKNOWN_TRANSITION"): (
            momapy.celldesigner.core.UnknownTransition,
            momapy.celldesigner.core.UnknownTransitionLayout,
        ),
        ("REACTION", "TRANSCRIPTION"): (
            momapy.celldesigner.core.Transcription,
            momapy.celldesigner.core.TranscriptionLayout,
        ),
        ("REACTION", "TRANSLATION"): (
            momapy.celldesigner.core.Translation,
            momapy.celldesigner.core.TranslationLayout,
        ),
        ("REACTION", "TRANSPORT"): (
            momapy.celldesigner.core.Transport,
            momapy.celldesigner.core.TransportLayout,
        ),
        ("REACTION", "HETERODIMER_ASSOCIATION"): (
            momapy.celldesigner.core.HeterodimerAssociation,
            momapy.celldesigner.core.HeterodimerAssociationLayout,
        ),
        ("REACTION", "DISSOCIATION"): (
            momapy.celldesigner.core.Dissociation,
            momapy.celldesigner.core.DissociationLayout,
        ),
        ("REACTION", "TRUNCATION"): (
            momapy.celldesigner.core.Truncation,
            momapy.celldesigner.core.TruncationLayout,
        ),
        ("REACTION", "CATALYSIS"): (
            momapy.celldesigner.core.Catalysis,
            momapy.celldesigner.core.CatalysisLayout,
        ),
        ("REACTION", "UNKNOWN_CATALYSIS"): (
            momapy.celldesigner.core.UnknownCatalysis,
            momapy.celldesigner.core.UnknownCatalysisLayout,
        ),
        ("REACTION", "INHIBITION"): (
            momapy.celldesigner.core.Inhibition,
            momapy.celldesigner.core.InhibitionLayout,
        ),
        ("REACTION", "UNKNOWN_INHIBITION"): (
            momapy.celldesigner.core.UnknownInhibition,
            momapy.celldesigner.core.UnknownInhibitionLayout,
        ),
        ("REACTION", "PHYSICAL_STIMULATION"): (
            momapy.celldesigner.core.PhysicalStimulation,
            momapy.celldesigner.core.PhysicalStimulationLayout,
        ),
        ("REACTION", "MODULATION"): (
            momapy.celldesigner.core.Modulation,
            momapy.celldesigner.core.ModulationLayout,
        ),
        ("REACTION", "TRIGGER"): (
            momapy.celldesigner.core.Triggering,
            momapy.celldesigner.core.TriggeringLayout,
        ),
        ("REACTION", "POSITIVE_INFLUENCE"): (
            momapy.celldesigner.core.PositiveInfluence,
            momapy.celldesigner.core.PositiveInfluenceLayout,
        ),
        ("REACTION", "UNKNOWN_POSITIVE_INFLUENCE"): (
            momapy.celldesigner.core.UnknownPositiveInfluence,
            momapy.celldesigner.core.UnknownPositiveInfluenceLayout,
        ),
        ("REACTION", "NEGATIVE_INFLUENCE"): (
            momapy.celldesigner.core.NegativeInfluence,
            momapy.celldesigner.core.momapy.celldesigner.core.InhibitionLayout,
        ),
        ("REACTION", "UNKNOWN_NEGATIVE_INFLUENCE"): (
            momapy.celldesigner.core.UnknownNegativeInfluence,
            momapy.celldesigner.core.UnknownInhibitionLayout,
        ),
        ("REACTION", "REDUCED_PHYSICAL_STIMULATION"): (
            momapy.celldesigner.core.PhysicalStimulation,
            momapy.celldesigner.core.PhysicalStimulationLayout,
        ),
        ("REACTION", "UNKNOWN_REDUCED_PHYSICAL_STIMULATION"): (
            momapy.celldesigner.core.UnknownPhysicalStimulation,
            momapy.celldesigner.core.UnknownPhysicalStimulationLayout,
        ),
        ("REACTION", "REDUCED_MODULATION"): (
            momapy.celldesigner.core.Modulation,
            momapy.celldesigner.core.ModulationLayout,
        ),
        ("REACTION", "UNKNOWN_REDUCED_MODULATION"): (
            momapy.celldesigner.core.UnknownModulation,
            momapy.celldesigner.core.UnknownModulationLayout,
        ),
        ("REACTION", "REDUCED_TRIGGER"): (
            momapy.celldesigner.core.Triggering,
            momapy.celldesigner.core.TriggeringLayout,
        ),
        ("REACTION", "UNKNOWN_REDUCED_TRIGGER"): (
            momapy.celldesigner.core.UnknownTriggering,
            momapy.celldesigner.core.UnknownTriggeringLayout,
        ),
        ("MODIFIER", "CATALYSIS"): (
            momapy.celldesigner.core.Catalyzer,
            momapy.celldesigner.core.CatalysisLayout,
        ),
        ("MODIFIER", "UNKNOWN_CATALYSIS"): (
            momapy.celldesigner.core.UnknownCatalyzer,
            momapy.celldesigner.core.UnknownCatalysisLayout,
        ),
        ("MODIFIER", "INHIBITION"): (
            momapy.celldesigner.core.Inhibitor,
            momapy.celldesigner.core.InhibitionLayout,
        ),
        ("MODIFIER", "UNKNOWN_INHIBITION"): (
            momapy.celldesigner.core.UnknownInhibitor,
            momapy.celldesigner.core.UnknownInhibitionLayout,
        ),
        ("MODIFIER", "PHYSICAL_STIMULATION"): (
            momapy.celldesigner.core.PhysicalStimulator,
            momapy.celldesigner.core.PhysicalStimulationLayout,
        ),
        ("MODIFIER", "MODULATION"): (
            momapy.celldesigner.core.Modulator,
            momapy.celldesigner.core.ModulationLayout,
        ),
        ("MODIFIER", "TRIGGER"): (
            momapy.celldesigner.core.Trigger,
            momapy.celldesigner.core.TriggeringLayout,
        ),
        ("MODIFIER", "POSITIVE_INFLUENCE"): (  # older version?
            momapy.celldesigner.core.PositiveInfluence,
            momapy.celldesigner.core.PositiveInfluenceLayout,
        ),
        ("MODIFIER", "NEGATIVE_INFLUENCE"): (  # older version?
            momapy.celldesigner.core.NegativeInfluence,
            momapy.celldesigner.core.InhibitionLayout,
        ),
        ("GATE", "BOOLEAN_LOGIC_GATE_AND"): (
            momapy.celldesigner.core.AndGate,
            momapy.celldesigner.core.AndGateLayout,
        ),
        ("GATE", "BOOLEAN_LOGIC_GATE_OR"): (
            momapy.celldesigner.core.OrGate,
            momapy.celldesigner.core.OrGateLayout,
        ),
        ("GATE", "BOOLEAN_LOGIC_GATE_NOT"): (
            momapy.celldesigner.core.NotGate,
            momapy.celldesigner.core.NotGateLayout,
        ),
        (
            "GATE",
            "BOOLEAN_LOGIC_GATE_UNKNOWN",
        ): (
            momapy.celldesigner.core.UnknownGate,
            momapy.celldesigner.core.UnknownGateLayout,
        ),
        (
            "REGION",
            "Modification Site",
        ): momapy.celldesigner.core.ModificationSite,
        (
            "REGION",
            "RegulatoryRegion",
        ): momapy.celldesigner.core.RegulatoryRegion,
        (
            "REGION",
            "transcriptionStartingSiteL",
        ): momapy.celldesigner.core.TranscriptionStartingSiteL,
        (
            "REGION",
            "transcriptionStartingSiteR",
        ): momapy.celldesigner.core.TranscriptionStartingSiteR,
        (
            "REGION",
            "CodingRegion",
        ): momapy.celldesigner.core.CodingRegion,
        (
            "REGION",
            "proteinBindingDomain",
        ): momapy.celldesigner.core.ProteinBindingDomain,
    }
    _QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER = {
        (
            "http://biomodels.net/biology-qualifiers/",
            "encodes",
        ): momapy.sbml.core.BQBiol.ENCODES,
        (
            "http://biomodels.net/biology-qualifiers/",
            "hasPart",
        ): momapy.sbml.core.BQBiol.HAS_PART,
        (
            "http://biomodels.net/biology-qualifiers/",
            "hasProperty",
        ): momapy.sbml.core.BQBiol.HAS_PROPERTY,
        (
            "http://biomodels.net/biology-qualifiers/",
            "hasVersion",
        ): momapy.sbml.core.BQBiol.HAS_VERSION,
        (
            "http://biomodels.net/biology-qualifiers/",
            "is",
        ): momapy.sbml.core.BQBiol.IS,
        (
            "http://biomodels.net/biology-qualifiers/",
            "isDescribedBy",
        ): momapy.sbml.core.BQBiol.IS_DESCRIBED_BY,
        (
            "http://biomodels.net/biology-qualifiers/",
            "isEncodedBy",
        ): momapy.sbml.core.BQBiol.IS_ENCODED_BY,
        (
            "http://biomodels.net/biology-qualifiers/",
            "isHomologTo",
        ): momapy.sbml.core.BQBiol.IS_HOMOLOG_TO,
        (
            "http://biomodels.net/biology-qualifiers/",
            "isPartOf",
        ): momapy.sbml.core.BQBiol.IS_PART_OF,
        (
            "http://biomodels.net/biology-qualifiers/",
            "isPropertyOf",
        ): momapy.sbml.core.BQBiol.IS_PROPERTY_OF,
        (
            "http://biomodels.net/biology-qualifiers/",
            "isVersionOf",
        ): momapy.sbml.core.BQBiol.IS_VERSION_OF,
        (
            "http://biomodels.net/biology-qualifiers/",
            "occursIn",
        ): momapy.sbml.core.BQBiol.OCCURS_IN,
        (
            "http://biomodels.net/biology-qualifiers/",
            "hasTaxon",
        ): momapy.sbml.core.BQBiol.HAS_TAXON,
        (
            "http://biomodels.net/biology-qualifiers/",
            "hasInstance",
        ): momapy.sbml.core.BQModel.HAS_INSTANCE,
        (
            "http://biomodels.net/model-qualifiers/",
            "is",
        ): momapy.sbml.core.BQModel.IS,
        (
            "http://biomodels.net/model-qualifiers/",
            "isDerivedFrom",
        ): momapy.sbml.core.BQModel.IS_DERIVED_FROM,
        (
            "http://biomodels.net/model-qualifiers/",
            "isDescribedBy",
        ): momapy.sbml.core.BQModel.IS_DESCRIBED_BY,
        (
            "http://biomodels.net/model-qualifiers/",
            "isInstanceOf",
        ): momapy.sbml.core.BQModel.IS_INSTANCE_OF,
    }
    _LINK_ANCHOR_POSITION_TO_ANCHOR_NAME = {
        "NW": "north_west",
        "NNW": "north_north_west",
        "N": "north",
        "NNE": "north_north_east",
        "NE": "north_east",
        "ENE": "east_north_east",
        "E": "east",
        "ESE": "east_south_east",
        "SE": "south_east",
        "SSE": "south_south_east",
        "S": "south",
        "SSW": "south_south_west",
        "SW": "south_west",
        "WSW": "west_south_west",
        "W": "west",
        "WNW": "west_north_west",
    }
    _TEXT_TO_CHARACTER = {
        "_underscore_": "_",
        "_br_": "\n",
        "_BR_": "\n",
        "_plus_": "+",
        "_minus_": "-",
        "_slash_": "/",
        "_space_": " ",
        "_Alpha_": "Α",
        "_alpha_": "α",
        "_Beta_": "Β",
        "_beta_": "β",
        "_Gamma_": "Γ",
        "_gamma_": "γ",
        "_Delta_": "Δ",
        "_delta_": "δ",
        "_Epsilon_": "Ε",
        "_epsilon_": "ε",
        "_Zeta_": "Ζ",
        "_zeta_": "ζ",
        "_Eta_": "Η",
        "_eta_": "η",
        "_Theta_": "Θ",
        "_theta_": "θ",
        "_Iota_": "Ι",
        "_iota_": "ι",
        "_Kappa_": "Κ",
        "_kappa_": "κ",
        "_Lambda_": "Λ",
        "_lambda_": "λ",
        "_Mu_": "Μ",
        "_mu_": "μ",
        "_Nu_": "Ν",
        "_nu_": "ν",
        "_Xi_": "Ξ",
        "_xi_": "ξ",
        "_Omicron_": "Ο",
        "_omicron_": "ο",
        "_Pi_": "Π",
        "_pi_": "π",
        "_Rho_": "Ρ",
        "_rho_": "ρ",
        "_Sigma_": "Σ",
        "_sigma_": "σ",
        "_Tau_": "Τ",
        "_tau_": "τ",
        "_Upsilon_": "Υ",
        "_upsilon_": "υ",
        "_Phi_": "Φ",
        "_phi_": "φ",
        "_Chi_": "Χ",
        "_chi_": "χ",
        "_Psi_": "Ψ",
        "_psi_": "ψ",
        "_Omega_": "Ω",
        "_omega_": "ω",
    }

    @classmethod
    def check_file(cls, file_path: str | os.PathLike):
        """Return `true` if the file is a CellDesigner file, `false` otherwise"""
        try:
            with open(file_path) as f:
                for line in f:
                    if "http://www.sbml.org/2001/ns/celldesigner" in line:
                        return True
        except UnicodeDecodeError:
            return False
        else:
            return False

    @classmethod
    def read(
        cls,
        file_path: str | os.PathLike,
        return_type: typing.Literal["map", "model", "layout"] = "map",
        with_model=True,
        with_layout=True,
        with_annotations=True,
        with_notes=True,
    ) -> momapy.io.ReaderResult:
        """Read a CellDesigner file and return a reader result object"""
        cd_document = lxml.objectify.parse(file_path)
        cd_sbml = cd_document.getroot()
        obj, annotations, notes, ids = cls._make_main_obj_from_cd_model(
            cd_model=cd_sbml.model,
            return_type=return_type,
            with_model=with_model,
            with_layout=with_layout,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        result = momapy.io.ReaderResult(
            obj=obj,
            notes=notes,
            annotations=annotations,
            file_path=file_path,
            ids=ids,
        )
        return result

    @classmethod
    def _get_annotation_from_cd_element(cls, cd_element):
        return getattr(cd_element, "annotation", None)

    @classmethod
    def _get_extension_from_cd_element(cls, cd_element):
        cd_annotation = cls._get_annotation_from_cd_element(cd_element)
        if cd_annotation is None:
            return None
        cd_extension = getattr(
            cd_element.annotation, f"{{{cls._CD_NAMESPACE}}}extension", None
        )
        return cd_extension

    @classmethod
    def _get_species_from_cd_model(cls, cd_model):
        list_of_species = getattr(cd_model, "listOfSpecies", None)
        if list_of_species is None:
            return []
        return list(getattr(list_of_species, "species", []))

    @classmethod
    def _get_reactions_from_cd_model(cls, cd_model):
        list_of_reactions = getattr(cd_model, "listOfReactions", None)
        if list_of_reactions is None:
            return []
        return list(getattr(list_of_reactions, "reaction", []))

    @classmethod
    def _get_species_aliases_from_cd_model(cls, cd_model):
        # only the non-included ones
        extension = cls._get_extension_from_cd_element(cd_model)
        species_aliases = list(
            getattr(extension.listOfSpeciesAliases, "speciesAlias", [])
        )
        species_aliases = [
            species_alias
            for species_alias in species_aliases
            if species_alias.get("complexSpeciesAlias") is None
        ]
        return species_aliases

    @classmethod
    def _get_included_species_aliases_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        species_aliases = list(
            getattr(extension.listOfSpeciesAliases, "speciesAlias", [])
        )
        species_aliases = [
            species_alias
            for species_alias in species_aliases
            if species_alias.get("complexSpeciesAlias") is not None
        ]
        return species_aliases

    @classmethod
    def _get_complex_species_aliases_from_cd_model(cls, cd_model):
        # only the non-included ones
        extension = cls._get_extension_from_cd_element(cd_model)
        complex_species_aliases = list(
            getattr(
                extension.listOfComplexSpeciesAliases,
                "complexSpeciesAlias",
                [],
            )
        )
        complex_species_aliases = [
            complex_species_alias
            for complex_species_alias in complex_species_aliases
            if complex_species_alias.get("complexSpeciesAlias") is None
        ]
        return complex_species_aliases

    @classmethod
    def _get_included_complex_species_aliases_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        complex_species_aliases = list(
            getattr(
                extension.listOfComplexSpeciesAliases,
                "complexSpeciesAlias",
                [],
            )
        )
        complex_species_aliases = [
            complex_species_alias
            for complex_species_alias in complex_species_aliases
            if complex_species_alias.get("complexSpeciesAlias") is not None
        ]
        return complex_species_aliases

    @classmethod
    def _get_compartments_from_cd_model(cls, cd_model):
        return list(getattr(cd_model.listOfCompartments, "compartment", []))

    @classmethod
    def _get_compartment_aliases_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        return list(getattr(extension.listOfCompartmentAliases, "compartmentAlias", []))

    @classmethod
    def _get_protein_templates_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        return list(getattr(extension.listOfProteins, "protein", []))

    @classmethod
    def _get_gene_templates_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        return list(getattr(extension.listOfGenes, "gene", []))

    @classmethod
    def _get_rna_templates_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        return list(getattr(extension.listOfRNAs, "RNA", []))

    @classmethod
    def _get_antisense_rna_templates_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        return list(getattr(extension.listOfAntisenseRNAs, "AntisenseRNA", []))

    @classmethod
    def _get_species_templates_from_cd_model(cls, cd_model):
        return (
            cls._get_protein_templates_from_cd_model(cd_model)
            + cls._get_gene_templates_from_cd_model(cd_model)
            + cls._get_rna_templates_from_cd_model(cd_model)
            + cls._get_antisense_rna_templates_from_cd_model(cd_model)
        )

    @classmethod
    def _get_modification_residues_from_cd_species_template(cls, cd_species_template):
        list_of_modification_residues = getattr(
            cd_species_template, "listOfModificationResidues", None
        )
        if list_of_modification_residues is not None:
            modification_residues = list(
                getattr(list_of_modification_residues, "modificationResidue", [])
            )
        else:
            modification_residues = []
        return modification_residues

    @classmethod
    def _get_regions_from_cd_species_template(cls, cd_species_template):
        list_of_regions = getattr(cd_species_template, "listOfRegions", None)
        if list_of_regions is not None:
            regions = list(getattr(list_of_regions, "region", []))
        else:
            regions = []
        return regions

    @classmethod
    def _get_included_species_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        list_of_included_species = getattr(extension, "listOfIncludedSpecies", None)
        if list_of_included_species is None:
            return []
        return list(getattr(list_of_included_species, "species", []))

    @classmethod
    def _get_reaction_type_from_cd_reaction(cls, cd_reaction):
        cd_extension = cls._get_extension_from_cd_element(cd_reaction)
        return cd_extension.reactionType.text

    @classmethod
    def _get_gate_members_from_cd_reaction(cls, cd_reaction):
        cd_extension = cls._get_extension_from_cd_element(cd_reaction)
        list_of_gate_member = getattr(cd_extension, "listOfGateMember", None)
        if list_of_gate_member is not None:
            gate_members = list(getattr(list_of_gate_member, "GateMember", []))
        else:
            gate_members = []
        return gate_members

    @classmethod
    def _get_key_from_cd_reaction(cls, cd_reaction):
        cd_reaction_type = cls._get_reaction_type_from_cd_reaction(cd_reaction)
        if cd_reaction_type == "BOOLEAN_LOGIC_GATE":
            cd_gate_member = cls._get_gate_members_from_cd_reaction(cd_reaction)[0]
            cd_reaction_type = cd_gate_member.get("modificationType")
        return ("REACTION", cd_reaction_type)

    @classmethod
    def _get_key_from_cd_species_template(cls, cd_species_template):
        return (
            "TEMPLATE",
            cd_species_template.get("type"),
        )

    @classmethod
    def _get_key_from_cd_region(cls, cd_region):
        return (
            "REGION",
            cd_region.get("type"),
        )

    @classmethod
    def _get_key_from_cd_species(cls, cd_species, cd_id_to_cd_element):
        cd_species_template = cls._get_template_from_cd_species(
            cd_species, cd_id_to_cd_element
        )
        if cd_species_template is None:
            key = cls._get_class_from_cd_species(cd_species).text
        else:
            key = cd_species_template.get("type")
        return ("SPECIES", key)

    @classmethod
    def _get_key_from_cd_reaction_modification(cls, cd_reaction_modification):
        if cls._has_boolean_input_from_cd_reaction_modification(
            cd_reaction_modification
        ):
            cd_reaction_modification_type = cd_reaction_modification.get(
                "modificationType"
            )
        else:
            cd_reaction_modification_type = cd_reaction_modification.get("type")
        return ("MODIFIER", cd_reaction_modification_type)

    @classmethod
    def _get_key_from_cd_reaction_modification_or_cd_gate_member(
        cls, cd_reaction_modification
    ):
        return ("GATE", cd_reaction_modification.get("type"))

    @classmethod
    def _get_identity_from_cd_species(cls, cd_species):
        cd_extension = cls._get_extension_from_cd_element(cd_species)
        if cd_extension is not None:
            cd_identity = cd_extension.speciesIdentity
        else:
            cd_identity = cd_species.annotation.speciesIdentity
        return cd_identity

    @classmethod
    def _get_class_from_cd_species(cls, cd_species):
        cd_identity = cls._get_identity_from_cd_species(cd_species)
        if cd_identity is None:
            return None
        cd_class = getattr(cd_identity, "class", None)
        return cd_class

    @classmethod
    def _get_state_from_cd_species(cls, cd_species):
        cd_species_identity = cls._get_identity_from_cd_species(cd_species)
        if cd_species_identity is None:
            return None
        cd_species_state = getattr(cd_species_identity, "state", None)
        return cd_species_state

    @classmethod
    def _get_activity_from_cd_species_alias(cls, cd_species_alias):
        return getattr(cd_species_alias, "activity", None)

    @classmethod
    def _get_homodimer_from_cd_species(cls, cd_species):
        cd_species_state = cls._get_state_from_cd_species(cd_species)
        if cd_species_state is None:
            return None
        return getattr(cd_species_state, "homodimer", None)

    @classmethod
    def _get_hypothetical_from_cd_species(cls, cd_species):
        cd_species_identity = cls._get_identity_from_cd_species(cd_species)
        if cd_species_identity is None:
            return None
        return getattr(cd_species_identity, "hypothetical", None)

    @classmethod
    def _get_species_modifications_from_cd_species(cls, cd_species):
        cd_species_state = cls._get_state_from_cd_species(cd_species)
        if cd_species_state is None:
            return []
        cd_list_of_modifications = getattr(
            cd_species_state, "listOfModifications", None
        )
        if cd_list_of_modifications is None:
            return []
        return list(getattr(cd_list_of_modifications, "modification", []))

    @classmethod
    def _get_species_structural_states_from_cd_species(cls, cd_species):
        cd_species_state = cls._get_state_from_cd_species(cd_species)
        if cd_species_state is None:
            return []
        cd_list_of_structural_states = getattr(
            cd_species_state, "listOfStructuralStates", None
        )
        if cd_list_of_structural_states is None:
            return []
        return cd_list_of_structural_states.structuralState

    @classmethod
    def _get_template_from_cd_species(cls, cd_species, cd_id_to_cd_element):
        cd_species_identity = cls._get_identity_from_cd_species(cd_species)
        for cd_species_template_type in [
            "proteinReference",
            "rnaReference",
            "geneReference",
            "antisensernaReference",
        ]:
            cd_reference = getattr(cd_species_identity, cd_species_template_type, None)
            if cd_reference is not None:
                cd_species_template = cd_id_to_cd_element[cd_reference.text]
                return cd_species_template
        return None

    @classmethod
    def _get_template_from_cd_species_alias(cls, cd_species_alias, cd_id_to_cd_element):
        cd_species_id = cd_species_alias.get("species")
        cd_species = cd_id_to_cd_element[cd_species_id]
        return cls._get_template_from_cd_species(cd_species, cd_id_to_cd_element)

    @classmethod
    def _get_bounds_from_cd_element(cls, cd_element):
        cd_x = cd_element.bounds.get("x")
        cd_y = cd_element.bounds.get("y")
        cd_w = cd_element.bounds.get("w")
        cd_h = cd_element.bounds.get("h")
        return cd_x, cd_y, cd_w, cd_h

    @classmethod
    def _get_anchor_name_for_frame_from_cd_link(cls, cd_element):
        if getattr(cd_element, "linkAnchor", None) is not None:
            cd_element_anchor = cd_element.linkAnchor.get("position")
            anchor_name = cls._LINK_ANCHOR_POSITION_TO_ANCHOR_NAME[cd_element_anchor]
        else:
            anchor_name = "center"
        return anchor_name

    @classmethod
    def _get_reactants_from_cd_reaction(cls, cd_reaction):
        return list(getattr(cd_reaction.listOfReactants, "speciesReference", []))

    @classmethod
    def _get_base_reactants_from_cd_reaction(cls, cd_reaction):
        extension = cls._get_extension_from_cd_element(cd_reaction)
        return list(getattr(extension.baseReactants, "baseReactant", []))

    @classmethod
    def _get_reactant_links_from_cd_reaction(cls, cd_reaction):
        extension = cls._get_extension_from_cd_element(cd_reaction)
        list_of_reactant_links = getattr(extension, "listOfReactantLinks", None)
        if list_of_reactant_links is None:
            return []
        return list(getattr(list_of_reactant_links, "reactantLink", []))

    @classmethod
    def _get_products_from_cd_reaction(cls, cd_reaction):
        return list(getattr(cd_reaction.listOfProducts, "speciesReference", []))

    @classmethod
    def _get_base_products_from_cd_reaction(cls, cd_reaction):
        extension = cls._get_extension_from_cd_element(cd_reaction)
        return list(getattr(extension.baseProducts, "baseProduct", []))

    @classmethod
    def _get_product_links_from_cd_reaction(cls, cd_reaction):
        extension = cls._get_extension_from_cd_element(cd_reaction)
        list_of_product_links = getattr(extension, "listOfProductLinks", None)
        if list_of_product_links is None:
            return []
        return list(getattr(list_of_product_links, "productLink", []))

    @classmethod
    def _get_edit_points_from_cd_reaction(cls, cd_reaction):
        extension = cls._get_extension_from_cd_element(cd_reaction)
        return getattr(extension, "editPoints", None)

    @classmethod
    def _get_edit_points_from_cd_participant_link(cls, cd_participant_link):
        return getattr(cd_participant_link, "editPoints", None)

    @classmethod
    def _get_rectangle_index_from_cd_reaction(cls, cd_reaction):
        extension = cls._get_extension_from_cd_element(cd_reaction)
        return extension.connectScheme.get("rectangleIndex")

    @classmethod
    def _get_t_shape_index_from_cd_reaction(cls, cd_reaction):
        cd_edit_points = cls._get_edit_points_from_cd_reaction(cd_reaction)
        return cd_edit_points.get("tShapeIndex")

    @classmethod
    def _has_boolean_input_from_cd_reaction_modification(cls, cd_reaction_modification):
        return cd_reaction_modification.get("type") in [
            "BOOLEAN_LOGIC_GATE_AND",
            "BOOLEAN_LOGIC_GATE_OR",
            "BOOLEAN_LOGIC_GATE_NOT",
            "BOOLEAN_LOGIC_GATE_UNKNOWN",
        ]

    @classmethod
    def _has_boolean_input_from_cd_reaction(cls, cd_reaction):
        return (
            cls._get_reaction_type_from_cd_reaction(cd_reaction) == "BOOLEAN_LOGIC_GATE"
        )

    @classmethod
    def _get_reaction_modifications_from_cd_reaction(cls, cd_reaction):
        extension = cls._get_extension_from_cd_element(cd_reaction)
        list_of_modification = getattr(extension, "listOfModification", None)
        if list_of_modification is None:
            return []
        modifications = list(getattr(list_of_modification, "modification", []))
        true_modifications = []
        cd_input_ids = set([])
        for modification in modifications:
            if cls._has_boolean_input_from_cd_reaction_modification(modification):
                true_modifications.append(modification)
                cd_input_ids.update(modification.get("modifiers").split(","))
        for modification in modifications:
            if (
                modification not in true_modifications
                and modification.get("modifiers") not in cd_input_ids
            ):
                true_modifications.append(modification)
        return true_modifications

    @classmethod
    def _make_points_from_cd_edit_points(cls, cd_edit_points):
        if getattr(cd_edit_points, "text", None) is not None:
            cd_edit_points = cd_edit_points.text
        cd_coordinates = [
            cd_edit_point.split(",") for cd_edit_point in cd_edit_points.split(" ")
        ]
        points = [
            momapy.geometry.Point(float(cd_coordinate[0]), float(cd_coordinate[1]))
            for cd_coordinate in cd_coordinates
        ]
        return points

    @classmethod
    def _make_segments_from_points(cls, points):
        segments = []
        for current_point, following_point in zip(points[:-1], points[1:]):
            segment = momapy.geometry.Segment(current_point, following_point)
            segments.append(segment)
        return segments

    @classmethod
    def _get_width_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        return extension.modelDisplay.get("sizeX")

    @classmethod
    def _get_height_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        return extension.modelDisplay.get("sizeY")

    @classmethod
    def _get_prefix_and_name_from_tag(cls, tag):
        prefix, name = tag.split("}")
        return prefix[1:], name

    @classmethod
    def _set_layout_size_and_position_from_cd_model(cls, cd_model, layout):
        layout.width = float(cls._get_width_from_cd_model(cd_model))
        layout.height = float(cls._get_height_from_cd_model(cd_model))
        layout.position = momapy.geometry.Point(layout.width / 2, layout.height / 2)

    @classmethod
    def _make_name_from_cd_name(cls, name: str | None):
        if name is None:
            return name
        for s, char in cls._TEXT_TO_CHARACTER.items():
            name = name.replace(s, char)
        return name

    @classmethod
    def _get_notes_from_cd_element(cls, cd_element):
        return getattr(cd_element, "notes", None)

    @classmethod
    def _get_rdf_from_cd_notes(cls, cd_notes):
        rdfs = list(cd_notes.iter(f"{{{cls._RDF_NAMESPACE}}}RDF"))
        if rdfs:
            return rdfs[0]
        return None

    @classmethod
    def _get_rdf_from_cd_element(cls, cd_element):
        annotation = cls._get_annotation_from_cd_element(cd_element)
        if annotation is None:
            return None
        return getattr(annotation, f"{{{cls._RDF_NAMESPACE}}}RDF", None)

    @classmethod
    def _get_description_from_rdf(cls, rdf):
        return getattr(rdf, "Description", None)

    @classmethod
    def _get_bags_from_bq_element(cls, bq_element):
        return list(getattr(bq_element, f"{{{cls._RDF_NAMESPACE}}}Bag", []))

    @classmethod
    def _get_lis_from_bag(cls, bag):
        return list(getattr(bag, "li", []))

    @classmethod
    def _make_annotations_from_cd_rdf(cls, cd_rdf):
        annotations = []
        description = cls._get_description_from_rdf(cd_rdf)
        if description is not None:
            for bq_element in description.getchildren():
                key = cls._get_prefix_and_name_from_tag(bq_element.tag)
                qualifier = cls._QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER.get(key)
                if qualifier is not None:
                    bags = cls._get_bags_from_bq_element(bq_element)
                    for bag in bags:
                        lis = cls._get_lis_from_bag(bag)
                        resources = [
                            li.get(f"{{{cls._RDF_NAMESPACE}}}resource") for li in lis
                        ]
                        annotation = momapy.sbml.core.RDFAnnotation(
                            qualifier=qualifier,
                            resources=frozenset(resources),
                        )
                        annotations.append(annotation)
        return annotations

    @classmethod
    def _make_notes_from_cd_element(cls, cd_element):
        cd_notes = cls._get_notes_from_cd_element(cd_element)
        if cd_notes is not None:
            for child_element in cd_notes.iterchildren():
                break
            return lxml.etree.tostring(child_element)
        return []

    @classmethod
    def _make_annotations_from_cd_element(cls, cd_element):
        cd_rdf = cls._get_rdf_from_cd_element(cd_element)
        if cd_rdf is not None:
            annotations = cls._make_annotations_from_cd_rdf(cd_rdf)
        else:
            annotations = []
        return annotations

    @classmethod
    def _make_annotations_from_cd_notes(cls, cd_notes):
        cd_rdf = cls._get_rdf_from_cd_notes(cd_notes)
        if cd_rdf is not None:
            annotations = cls._make_annotations_from_cd_rdf(cd_rdf)
        else:
            annotations = []
        return annotations

    @classmethod
    def _make_cd_id_to_cd_element_mapping_from_cd_model(cls, cd_model):
        cd_id_to_cd_element = {}
        # compartments
        for cd_compartment in cls._get_compartments_from_cd_model(cd_model):
            cd_id_to_cd_element[cd_compartment.get("id")] = cd_compartment
        # compartment aliases
        for cd_compartment_alias in cls._get_compartment_aliases_from_cd_model(
            cd_model
        ):
            cd_id_to_cd_element[cd_compartment_alias.get("id")] = cd_compartment_alias
        # species templates
        for cd_species_template in cls._get_species_templates_from_cd_model(cd_model):
            cd_id_to_cd_element[cd_species_template.get("id")] = cd_species_template
            for (
                cd_modification_residue
            ) in cls._get_modification_residues_from_cd_species_template(
                cd_species_template
            ):
                cd_modification_residue_id = f"{cd_species_template.get('id')}_{cd_modification_residue.get('id')}"
                cd_id_to_cd_element[cd_modification_residue_id] = (
                    cd_modification_residue
                )
            for cd_region in cls._get_regions_from_cd_species_template(
                cd_species_template
            ):
                cd_region_id = f"{cd_species_template.get('id')}_{cd_region.get('id')}"
                cd_id_to_cd_element[cd_region_id] = cd_region
        # species
        for cd_species in cls._get_species_from_cd_model(cd_model):
            cd_id_to_cd_element[cd_species.get("id")] = cd_species
        # included species
        for cd_included_species in cls._get_included_species_from_cd_model(cd_model):
            cd_id_to_cd_element[cd_included_species.get("id")] = cd_included_species
        # species aliases
        for cd_species_alias in cls._get_species_aliases_from_cd_model(cd_model):
            cd_id_to_cd_element[cd_species_alias.get("id")] = cd_species_alias
        # complex species aliases
        for cd_complex_species_alias in cls._get_complex_species_aliases_from_cd_model(
            cd_model
        ):
            cd_id_to_cd_element[cd_complex_species_alias.get("id")] = (
                cd_complex_species_alias
            )
        # included species aliases
        for cd_species_alias in cls._get_included_species_aliases_from_cd_model(
            cd_model
        ):
            cd_id_to_cd_element[cd_species_alias.get("id")] = cd_species_alias
        # included complex species aliases
        for (
            cd_complex_species_alias
        ) in cls._get_included_complex_species_aliases_from_cd_model(cd_model):
            cd_id_to_cd_element[cd_complex_species_alias.get("id")] = (
                cd_complex_species_alias
            )
        return cd_id_to_cd_element

    @classmethod
    def _make_cd_complex_species_alias_id_to_cd_included_species_alias_id_mapping_from_cd_model(
        cls, cd_model
    ):
        cd_complex_alias_id_to_cd_included_species_ids = collections.defaultdict(list)
        for cd_species_alias in cls._get_included_species_aliases_from_cd_model(
            cd_model
        ):
            cd_complex_species_alias_id = cd_species_alias.get("complexSpeciesAlias")
            if cd_complex_species_alias_id is not None:
                cd_complex_alias_id_to_cd_included_species_ids[
                    cd_complex_species_alias_id
                ].append(cd_species_alias.get("id"))

        for cd_species_alias in cls._get_included_complex_species_aliases_from_cd_model(
            cd_model
        ):
            cd_complex_species_alias_id = cd_species_alias.get("complexSpeciesAlias")
            if cd_complex_species_alias_id is not None:
                cd_complex_alias_id_to_cd_included_species_ids[
                    cd_complex_species_alias_id
                ].append(cd_species_alias.get("id"))
        return cd_complex_alias_id_to_cd_included_species_ids

    @classmethod
    def _make_model_no_subelements_from_cd_model(
        cls,
        cd_element,
    ):
        model = momapy.celldesigner.core.CellDesignerModelBuilder()
        return model

    @classmethod
    def _make_layout_no_subelements_from_cd_model(
        cls,
        cd_element,
    ):
        layout = momapy.celldesigner.core.CellDesignerLayoutBuilder()
        return layout

    @classmethod
    def _make_map_no_subelements_from_cd_model(
        cls,
        cd_element,
    ):
        map_ = momapy.celldesigner.core.CellDesignerMapBuilder()
        return map_

    @classmethod
    def _make_main_obj_from_cd_model(
        cls,
        cd_model,
        return_type: typing.Literal["map", "model", "layout"] = "map",
        with_model=True,
        with_layout=True,
        with_annotations=True,
        with_notes=True,
    ):
        if return_type == "model" or return_type == "map" and with_model:
            model = cls._make_model_no_subelements_from_cd_model(cd_model)
        else:
            model = None
        if return_type == "layout" or return_type == "map" and with_layout:
            layout = cls._make_layout_no_subelements_from_cd_model(cd_model)
        else:
            layout = None
        if model is not None or layout is not None:
            cd_id_to_cd_element = cls._make_cd_id_to_cd_element_mapping_from_cd_model(
                cd_model
            )
            cd_complex_alias_id_to_cd_included_species_ids = cls._make_cd_complex_species_alias_id_to_cd_included_species_alias_id_mapping_from_cd_model(
                cd_model
            )
            cd_id_to_model_element = {}
            cd_id_to_layout_element = {}
            map_element_to_annotations = collections.defaultdict(set)
            map_element_to_ids = collections.defaultdict(set)
            map_element_to_notes = collections.defaultdict(set)
            if model is not None and layout is not None:
                model_element_to_layout_element = (
                    momapy.core.LayoutModelMappingBuilder()
                )
            else:
                model_element_to_layout_element = None
            # we make and add the  model and layout elements from the cd elements
            # we start with the compartment aliases
            cls._make_and_add_compartments_from_cd_model(
                cd_model=cd_model,
                model=model,
                layout=layout,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                model_element_to_layout_element=model_element_to_layout_element,
                map_element_to_ids=map_element_to_ids,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
            # we make and add the species templates
            cls._make_and_add_species_templates_from_cd_model(
                cd_model=cd_model,
                model=model,
                layout=layout,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                model_element_to_layout_element=model_element_to_layout_element,
                map_element_to_ids=map_element_to_ids,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
            # we make and add the species, from the species aliases
            # species aliases are the glyphs; in terms of model, a species is almost
            # a model element on its own: the only attribute that is not on the
            # species but on the species alias is the activity (active or inactive);
            # hence two species aliases can be associated to only one species
            # but correspond to two different layou elements; we do not make the
            # species that are included, they are made when we make their
            # containing complex, but we make complexes
            cls._make_and_add_species_from_cd_model(
                cd_model=cd_model,
                model=model,
                layout=layout,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                model_element_to_layout_element=model_element_to_layout_element,
                map_element_to_ids=map_element_to_ids,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
            # we make and add the reactions and modulations from celldesigner
            # reactions: a celldesigner reaction is either a true reaction
            # or a false reaction encoding a modulation
            cls._make_and_add_reactions_and_modulations_from_cd_model(
                cd_model=cd_model,
                model=model,
                layout=layout,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                model_element_to_layout_element=model_element_to_layout_element,
                map_element_to_ids=map_element_to_ids,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
            if layout is not None:
                cls._set_layout_size_and_position_from_cd_model(cd_model, layout)
        if return_type == "model":
            obj = momapy.builder.object_from_builder(model)
            if with_annotations:
                annotations = cls._make_annotations_from_cd_element(cd_model)
                map_element_to_annotations[obj].update(annotations)
            if with_notes:
                notes = cls._make_notes_from_cd_element(cd_model)
                map_element_to_notes[obj].update(notes)
        elif return_type == "layout":
            obj = momapy.builder.object_from_builder(layout)
        elif return_type == "map":
            map_ = cls._make_map_no_subelements_from_cd_model(cd_model)
            map_.model = model
            map_.layout = layout
            map_.layout_model_mapping = model_element_to_layout_element
            obj = momapy.builder.object_from_builder(map_)
            if with_annotations:
                annotations = cls._make_annotations_from_cd_element(cd_model)
                map_element_to_annotations[obj].update(annotations)
            if with_notes:
                notes = cls._make_notes_from_cd_element(cd_model)
                map_element_to_notes[obj].update(notes)
        annotations = dict(map_element_to_annotations)
        notes = dict(map_element_to_notes)
        ids = dict(map_element_to_ids)
        return obj, annotations, notes, ids

    @classmethod
    def _make_and_add_compartments_from_cd_model(
        cls,
        cd_model,
        model,
        layout,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        for cd_compartment_alias in cls._get_compartment_aliases_from_cd_model(
            cd_model
        ):
            model_element, layout_element = (
                cls._make_and_add_compartment_from_cd_compartment_alias(
                    cd_compartment_alias=cd_compartment_alias,
                    model=model,
                    layout=layout,
                    cd_id_to_model_element=cd_id_to_model_element,
                    cd_id_to_layout_element=cd_id_to_layout_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                    cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                    map_element_to_annotations=map_element_to_annotations,
                    map_element_to_notes=map_element_to_notes,
                    model_element_to_layout_element=model_element_to_layout_element,
                    map_element_to_ids=map_element_to_ids,
                    with_annotations=with_annotations,
                    with_notes=with_notes,
                )
            )
        # we also make the compartments from the list of compartments that do not have
        # an alias (e.g., the "default" compartment)
        # since these have no alias, we only produce a model element
        for cd_compartment in cls._get_compartments_from_cd_model(cd_model):
            if cd_compartment.get("id") not in cd_id_to_model_element:
                model_element, layout_element = (
                    cls._make_and_add_compartment_from_cd_compartment(
                        cd_compartment=cd_compartment,
                        model=model,
                        layout=layout,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        model_element_to_layout_element=model_element_to_layout_element,
                        map_element_to_ids=map_element_to_ids,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )

    @classmethod
    def _make_and_add_species_templates_from_cd_model(
        cls,
        cd_model,
        model,
        layout,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        for cd_species_template in cls._get_species_templates_from_cd_model(cd_model):
            model_element, layout_element = (
                cls._make_and_add_species_template_from_cd_species_template(
                    cd_species_template=cd_species_template,
                    model=model,
                    layout=layout,
                    cd_id_to_model_element=cd_id_to_model_element,
                    cd_id_to_layout_element=cd_id_to_layout_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                    cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                    map_element_to_annotations=map_element_to_annotations,
                    map_element_to_notes=map_element_to_notes,
                    model_element_to_layout_element=model_element_to_layout_element,
                    map_element_to_ids=map_element_to_ids,
                    with_annotations=with_annotations,
                    with_notes=with_notes,
                )
            )

    @classmethod
    def _make_and_add_species_from_cd_model(
        cls,
        cd_model,
        model,
        layout,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        for cd_species_alias in cls._get_species_aliases_from_cd_model(
            cd_model
        ) + cls._get_complex_species_aliases_from_cd_model(cd_model):
            model_element, layout_element = (
                cls._make_and_add_species_from_cd_species_alias(
                    cd_species_alias=cd_species_alias,
                    model=model,
                    layout=layout,
                    cd_id_to_model_element=cd_id_to_model_element,
                    cd_id_to_layout_element=cd_id_to_layout_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                    cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                    map_element_to_annotations=map_element_to_annotations,
                    map_element_to_notes=map_element_to_notes,
                    model_element_to_layout_element=model_element_to_layout_element,
                    map_element_to_ids=map_element_to_ids,
                    with_annotations=with_annotations,
                    with_notes=with_notes,
                )
            )

    @classmethod
    def _make_and_add_reactions_and_modulations_from_cd_model(
        cls,
        cd_model,
        model,
        layout,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        for cd_reaction in cls._get_reactions_from_cd_model(cd_model):
            key = cls._get_key_from_cd_reaction(cd_reaction)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if issubclass(
                model_element_cls, momapy.celldesigner.core.Reaction
            ):  # true reaction
                model_element, layout_element = (
                    cls._make_and_add_reaction_from_cd_reaction(
                        cd_reaction=cd_reaction,
                        model=model,
                        layout=layout,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        model_element_to_layout_element=model_element_to_layout_element,
                        map_element_to_ids=map_element_to_ids,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
            else:  # modulation
                model_element, layout_element = (
                    cls._make_and_add_modulation_from_cd_reaction(
                        cd_reaction=cd_reaction,
                        model=model,
                        layout=layout,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        model_element_to_layout_element=model_element_to_layout_element,
                        map_element_to_ids=map_element_to_ids,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )

    @classmethod
    def _make_and_add_compartment_from_cd_compartment_alias(
        cls,
        cd_compartment_alias,
        model,
        layout,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        if model is not None or layout is not None:
            cd_compartment = cd_id_to_cd_element[
                cd_compartment_alias.get("compartment")
            ]
            if model is not None:
                # we make and add the model element from the cd compartment
                # the cd element is an alias of, if it has not already been made
                # while being outside another one
                model_element = cd_id_to_model_element.get(cd_compartment.get("id"))
                if model_element is None:
                    model_element, _ = (
                        cls._make_and_add_compartment_from_cd_compartment(
                            cd_compartment=cd_compartment,
                            model=model,
                            layout=layout,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            map_element_to_annotations=map_element_to_annotations,
                            map_element_to_notes=map_element_to_notes,
                            model_element_to_layout_element=model_element_to_layout_element,
                            map_element_to_ids=map_element_to_ids,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                        )
                    )
            else:
                model_element = None
            if layout is not None:
                if getattr(cd_compartment_alias, "class").text == "OVAL":
                    layout_element_cls = momapy.celldesigner.core.OvalCompartmentLayout
                else:
                    layout_element_cls = (
                        momapy.celldesigner.core.RectangleCompartmentLayout
                    )
                layout_element = layout.new_element(layout_element_cls)
                layout_element.id_ = cd_compartment_alias.get("id")
                cd_x = float(cd_compartment_alias.bounds.get("x"))
                cd_y = float(cd_compartment_alias.bounds.get("y"))
                cd_w = float(cd_compartment_alias.bounds.get("w"))
                cd_h = float(cd_compartment_alias.bounds.get("h"))
                layout_element.position = momapy.geometry.Point(
                    cd_x + cd_w / 2, cd_y + cd_h / 2
                )
                layout_element.width = cd_w
                layout_element.height = cd_h
                layout_element.inner_stroke_width = float(
                    cd_compartment_alias.doubleLine.get("innerWidth")
                )
                layout_element.stroke_width = float(
                    cd_compartment_alias.doubleLine.get("outerWidth")
                )
                layout_element.sep = float(
                    cd_compartment_alias.doubleLine.get("thickness")
                )
                cd_compartment_alias_color = cd_compartment_alias.paint.get("color")
                cd_compartment_alias_color = (
                    cd_compartment_alias_color[2:] + cd_compartment_alias_color[:2]
                )
                element_color = momapy.coloring.Color.from_hexa(
                    cd_compartment_alias_color
                )
                layout_element.stroke = element_color
                layout_element.inner_stroke = element_color
                layout_element.fill = element_color.with_alpha(0.5)
                layout_element.inner_fill = momapy.coloring.white
                text = cls._make_name_from_cd_name(cd_compartment.get("name"))
                text_position = momapy.geometry.Point(
                    float(cd_compartment_alias.namePoint.get("x")),
                    float(cd_compartment_alias.namePoint.get("y")),
                )
                text_layout = momapy.core.TextLayout(
                    text=text,
                    font_size=cls._DEFAULT_FONT_SIZE,
                    font_family=cls._DEFAULT_FONT_FAMILY,
                    fill=cls._DEFAULT_FONT_FILL,
                    stroke=momapy.drawing.NoneValue,
                    position=text_position,
                )
                layout_element.label = text_layout
                layout_element = momapy.builder.object_from_builder(layout_element)
                layout.layout_elements.append(layout_element)
                cd_id_to_layout_element[cd_compartment_alias.get("id")] = layout_element
            else:
                layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_compartment_from_cd_compartment(
        cls,
        cd_compartment,
        model,
        layout,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        if model is not None:
            model_element = model.new_element(momapy.celldesigner.core.Compartment)
            model_element.id_ = cd_compartment.get("id")
            model_element.name = cls._make_name_from_cd_name(cd_compartment.get("name"))
            model_element.metaid = cd_compartment.get("metaid")
            if cd_compartment.get("outside") is not None:
                outside_model_element = cd_id_to_model_element.get(
                    cd_compartment.get("outside")
                )
                # if outside is not already made, we make it
                if outside_model_element is None:
                    cd_outside = cd_id_to_cd_element[cd_compartment.get("outside")]
                    outside_model_element, _ = (
                        cls._make_and_add_compartment_from_cd_compartment(
                            cd_compartment=cd_outside,
                            model=model,
                            layout=layout,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            map_element_to_annotations=map_element_to_annotations,
                            map_element_to_notes=map_element_to_notes,
                            model_element_to_layout_element=model_element_to_layout_element,
                            map_element_to_ids=map_element_to_ids,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                        )
                    )
                model_element.outside = outside_model_element
            model_element = momapy.builder.object_from_builder(model_element)
            model_element = momapy.utils.add_or_replace_element_in_set(
                model_element,
                model.compartments,
                func=lambda element, existing_element: element.id_
                < existing_element.id_,
            )
            cd_id_to_model_element[cd_compartment.get("id")] = model_element
            map_element_to_ids[model_element].add(cd_compartment.get("id"))
            if with_annotations:
                annotations = cls._make_annotations_from_cd_element(cd_compartment)
                if annotations:
                    map_element_to_annotations[model_element].update(annotations)
            if with_notes:
                notes = cls._make_notes_from_cd_element(cd_compartment)
                map_element_to_notes[model_element].update(notes)
        else:
            model_element = None
        layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_species_template_from_cd_species_template(
        cls,
        cd_species_template,
        model,
        layout,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        if model is not None:
            key = cls._get_key_from_cd_species_template(cd_species_template)
            model_element_cls = cls._KEY_TO_CLASS[key]
            model_element = model.new_element(model_element_cls)
            model_element.id_ = cd_species_template.get("id")
            model_element.name = cls._make_name_from_cd_name(
                cd_species_template.get("name")
            )
            n_undefined_modification_residue_names = 0
            cd_modification_residues = (
                cls._get_modification_residues_from_cd_species_template(
                    cd_species_template
                )
            )
            cd_modification_residues.sort(
                key=lambda cd_modification_residue: cd_modification_residue.get("angle")
            )
            for (
                cd_modification_residue
            ) in cls._get_modification_residues_from_cd_species_template(
                cd_species_template
            ):
                if cd_modification_residue.get("name") is None:
                    n_undefined_modification_residue_names += 1
                    order = n_undefined_modification_residue_names
                else:
                    order = None
                modification_residue_model_element, _ = (
                    cls._make_and_add_modification_residue_from_cd_modification_residue(
                        cd_modification_residue=cd_modification_residue,
                        model=model,
                        layout=layout,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        model_element_to_layout_element=model_element_to_layout_element,
                        map_element_to_ids=map_element_to_ids,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_cd_element=cd_species_template,
                        super_model_element=model_element,
                        order=order,
                    )
                )
            n_undefined_region_names = 0
            cd_regions = cls._get_regions_from_cd_species_template(cd_species_template)
            cd_regions.sort(key=lambda cd_region: cd_region.get("pos"))
            for cd_region in cd_regions:
                if cd_region.get("name") is None:
                    n_undefined_region_names += 1
                    order = n_undefined_region_names
                else:
                    order = None
                region_model_element, _ = cls._make_and_add_region_from_cd_region(
                    cd_region=cd_region,
                    model=model,
                    layout=layout,
                    cd_id_to_model_element=cd_id_to_model_element,
                    cd_id_to_layout_element=cd_id_to_layout_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                    cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                    map_element_to_annotations=map_element_to_annotations,
                    map_element_to_notes=map_element_to_notes,
                    model_element_to_layout_element=model_element_to_layout_element,
                    map_element_to_ids=map_element_to_ids,
                    with_annotations=with_annotations,
                    with_notes=with_notes,
                    super_cd_element=cd_species_template,
                    super_model_element=model_element,
                    order=order,
                )
            model_element = momapy.builder.object_from_builder(model_element)
            model_element = momapy.utils.add_or_replace_element_in_set(
                model_element,
                model.species_templates,
                func=lambda element, existing_element: element.id_
                < existing_element.id_,
            )
            cd_id_to_model_element[cd_species_template.get("id")] = model_element
            map_element_to_ids[model_element].add(cd_species_template.get("id"))
        else:
            model_element = None
        layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_modification_residue_from_cd_modification_residue(
        cls,
        cd_modification_residue,
        model,
        layout,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
        super_cd_element,
        super_model_element,
        order,
    ):
        if model is not None:
            model_element = model.new_element(
                momapy.celldesigner.core.ModificationResidue
            )
            # Defaults ids for modification residues are simple in CellDesigner (e.g.,
            # "rs1") and might be shared between residues of different species.
            # However we want a unique id, so we build it using the id of the
            # species as well.
            cd_modification_residue_id = (
                f"{super_cd_element.get('id')}_{cd_modification_residue.get('id')}"
            )
            model_element.id_ = cd_modification_residue_id
            model_element.name = cls._make_name_from_cd_name(
                cd_modification_residue.get("name")
            )
            model_element.order = order
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.modification_residues.add(model_element)
            # exceptionally we take the model element's id and not the cd element's
            # id for the reasons explained above
            cd_id_to_model_element[cd_modification_residue_id] = model_element
            map_element_to_ids[model_element].add(cd_modification_residue_id)
        else:
            model_element = None
        layout_element = None  # purely a model element
        return model_element, layout_element

    @classmethod
    def _make_and_add_region_from_cd_region(
        cls,
        cd_region,
        model,
        layout,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
        super_cd_element,
        super_model_element,
        order,
    ):
        if model is not None:
            key = cls._get_key_from_cd_region(cd_region)
            model_element_cls = cls._KEY_TO_CLASS[key]
            model_element = model.new_element(model_element_cls)
            # Defaults ids for regions are simple in CellDesigner (e.g.,
            # "rs1") and might be shared between regions of different species.
            # However we want a unique id, so we build it using the id of the
            # species as well.
            cd_region_id = f"{super_cd_element.get('id')}_{cd_region.get('id')}"
            model_element.id_ = cd_region_id
            model_element.name = cls._make_name_from_cd_name(cd_region.get("name"))
            active = cd_region.get("active")
            if active is not None:
                model_element.active = True if active == "true" else False
            model_element.order = order
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.regions.add(model_element)
            # exceptionally we take the model element's id and not the cd element's
            # id for the reasons explained above
            cd_id_to_model_element[model_element.id_] = model_element
            map_element_to_ids[model_element].add(cd_region_id)
        else:
            model_element = None
        layout_element = None  # purely a model element
        return model_element, layout_element

    @classmethod
    def _make_and_add_species_from_cd_species_alias(
        cls,
        cd_species_alias,
        model,
        layout,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
        super_cd_element=None,
        super_model_element=None,
        super_layout_element=None,
    ):
        if model is not None or layout is not None:
            cd_species = cd_id_to_cd_element[cd_species_alias.get("species")]
            key = cls._get_key_from_cd_species(cd_species, cd_id_to_cd_element)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            name = cls._make_name_from_cd_name(cd_species.get("name"))
            cd_species_homodimer = cls._get_homodimer_from_cd_species(cd_species)
            if cd_species_homodimer is not None:
                homomultimer = int(cd_species_homodimer)
            else:
                homomultimer = 1
            cd_species_hypothetical = cls._get_hypothetical_from_cd_species(cd_species)
            if cd_species_hypothetical is not None:
                hypothetical = cd_species_hypothetical.text == "true"
            else:
                hypothetical = False
            cd_species_activity = cls._get_activity_from_cd_species_alias(
                cd_species_alias
            )
            if cd_species_activity is not None:
                active = cd_species_activity.text == "active"
                if active:
                    cd_species.attrib["id"] = f"{cd_species.get('id')}_active"
            if model is not None:
                model_element = model.new_element(model_element_cls)
                model_element.id_ = cd_species.get("id")
                model_element.name = name
                model_element.metaid = cd_species.get("metaid")
                cd_compartment_id = cd_species.get("compartment")
                if cd_compartment_id is not None:
                    compartment_model_element = cd_id_to_model_element[
                        cd_compartment_id
                    ]
                    model_element.compartment = compartment_model_element
                cd_species_template = cls._get_template_from_cd_species(
                    cd_species, cd_id_to_cd_element
                )
                if cd_species_template is not None:
                    model_element.template = cd_id_to_model_element[
                        cd_species_template.get("id")
                    ]
                model_element.homomultimer = homomultimer
                model_element.hypothetical = hypothetical
                model_element.active = active
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(layout_element_cls)
                cd_x, cd_y, cd_w, cd_h = cls._get_bounds_from_cd_element(
                    cd_species_alias
                )
                layout_element.position = momapy.geometry.Point(
                    float(cd_x) + float(cd_w) / 2,
                    float(cd_y) + float(cd_h) / 2,
                )
                layout_element.width = float(cd_w)
                layout_element.height = float(cd_h)
                text_layout = momapy.core.TextLayout(
                    text=name,
                    font_size=float(cd_species_alias.font.get("size")),
                    font_family=cls._DEFAULT_FONT_FAMILY,
                    fill=cls._DEFAULT_FONT_FILL,
                    stroke=momapy.drawing.NoneValue,
                    position=layout_element.label_center(),
                )
                text_layout = momapy.builder.object_from_builder(text_layout)
                layout_element.label = text_layout
                layout_element.stroke_width = float(
                    cd_species_alias.usualView.singleLine.get("width")
                )
                cd_species_alias_fill_color = cd_species_alias.usualView.paint.get(
                    "color"
                )
                cd_species_alias_fill_color = (
                    cd_species_alias_fill_color[2:] + cd_species_alias_fill_color[:2]
                )
                layout_element.fill = momapy.coloring.Color.from_hexa(
                    cd_species_alias_fill_color
                )
                cd_species_activity = cls._get_activity_from_cd_species_alias(
                    cd_species_alias
                )
                layout_element.active = active
                layout_element.n = homomultimer
            else:
                layout_element = None
            for (
                cd_species_modification
            ) in cls._get_species_modifications_from_cd_species(cd_species):
                modification_model_element, modification_layout_element = (
                    cls._make_and_add_species_modification_from_cd_species_modification(
                        model=model,
                        layout=layout,
                        cd_species_modification=cd_species_modification,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        model_element_to_layout_element=model_element_to_layout_element,
                        map_element_to_ids=map_element_to_ids,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_cd_element=cd_species_alias,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
            for (
                cd_species_structural_state
            ) in cls._get_species_structural_states_from_cd_species(cd_species):
                (
                    structural_state_model_element,
                    structural_state_layout_element,
                ) = cls._make_and_add_species_structural_state_from_cd_species_structural_state(
                    model=model,
                    layout=layout,
                    cd_species_structural_state=cd_species_structural_state,
                    cd_id_to_model_element=cd_id_to_model_element,
                    cd_id_to_layout_element=cd_id_to_layout_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                    cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                    map_element_to_annotations=map_element_to_annotations,
                    map_element_to_notes=map_element_to_notes,
                    model_element_to_layout_element=model_element_to_layout_element,
                    map_element_to_ids=map_element_to_ids,
                    with_annotations=with_annotations,
                    with_notes=with_notes,
                    super_cd_element=cd_species_alias,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                )
            cd_subunits = [
                cd_id_to_cd_element[cd_subunit_id]
                for cd_subunit_id in cd_complex_alias_id_to_cd_included_species_ids[
                    cd_species_alias.get("id")
                ]
            ]
            for cd_subunit in cd_subunits:
                subunit_model_element, subunit_layout_element = (
                    cls._make_and_add_species_from_cd_species_alias(
                        model=model,
                        layout=layout,
                        cd_species_alias=cd_subunit,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        model_element_to_layout_element=model_element_to_layout_element,
                        map_element_to_ids=map_element_to_ids,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_cd_element=cd_species_alias,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
            if model is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                if super_model_element is None:  # species case
                    model_element = momapy.utils.add_or_replace_element_in_set(
                        model_element,
                        model.species,
                        func=lambda element, existing_element: element.id_
                        < existing_element.id_,
                    )
                    if with_annotations:
                        annotations = cls._make_annotations_from_cd_element(cd_species)
                        if annotations:
                            map_element_to_annotations[model_element].update(
                                annotations
                            )
                    if with_notes:
                        notes = cls._make_notes_from_cd_element(cd_species)
                        map_element_to_notes[model_element].update(notes)
                else:  # included species case
                    super_model_element.subunits.add(model_element)
                    if with_annotations:
                        cd_notes = cls._get_notes_from_cd_element(cd_species)
                        annotations = cls._make_annotations_from_cd_notes(cd_notes)
                        if annotations:
                            map_element_to_annotations[model_element].update(
                                annotations
                            )
                    if with_notes:
                        notes = cls._make_notes_from_cd_element(cd_species)
                        map_element_to_notes[model_element].update(notes)
                cd_id_to_model_element[cd_species.get("id")] = model_element
                cd_id_to_model_element[cd_species_alias.get("id")] = model_element
                map_element_to_ids[model_element].add(cd_species.get("id"))
            if layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                if super_layout_element is None:  # species case
                    layout.layout_elements.append(layout_element)
                else:  # included species case
                    super_layout_element.layout_elements.append(layout_element)
                cd_id_to_layout_element[cd_species_alias.get("id")] = layout_element
            if model is not None and layout is not None:
                model_element_to_layout_element.add_mapping(
                    layout_element, model_element
                )
        return model_element, layout_element

    @classmethod
    def _make_and_add_species_modification_from_cd_species_modification(
        cls,
        model,
        layout,
        cd_species_modification,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if model is not None or layout is not None:
            cd_species_modification_state = cd_species_modification.get("state")
            if cd_species_modification_state == "empty":
                modification_state = None
            else:
                modification_state = momapy.celldesigner.core.ModificationState[
                    cd_species_modification_state.upper()
                    .replace(" ", "_")  # for DON'T CARE
                    .replace("'", "_")
                ]
            cd_species_template = cls._get_template_from_cd_species_alias(
                super_cd_element,
                cd_id_to_cd_element,
            )
            cd_modification_residue_id = f"{cd_species_template.get('id')}_{cd_species_modification.get('residue')}"
            if model is not None:
                model_element = model.new_element(momapy.celldesigner.core.Modification)
                modification_residue_model_element = cd_id_to_model_element[
                    cd_modification_residue_id
                ]
                model_element.residue = modification_residue_model_element
                model_element.state = modification_state
                model_element = momapy.builder.object_from_builder(model_element)
                super_model_element.modifications.add(model_element)
                cd_id_to_model_element[model_element.id_] = model_element
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(
                    momapy.celldesigner.core.ModificationLayout
                )
                cd_modification_residue = cd_id_to_cd_element[
                    cd_modification_residue_id
                ]  # can also be of type ModificationSite for Genes, RNAs, etc.
                angle = cd_modification_residue.get("angle")
                if angle is None:
                    fraction = float(cd_modification_residue.get("pos"))
                    segment = momapy.geometry.Segment(
                        super_layout_element.north_west(),
                        super_layout_element.north_east(),
                    )
                    point = segment.get_position_at_fraction(fraction)
                    segment = momapy.geometry.Segment(
                        super_layout_element.center(), point
                    )
                    angle = -segment.get_angle_to_horizontal()
                else:
                    angle = float(angle)
                    point = momapy.geometry.Point(
                        super_layout_element.width * math.cos(angle),
                        super_layout_element.height * math.sin(angle),
                    )
                    angle = math.atan2(point.y, point.x)
                layout_element.position = super_layout_element.angle(
                    angle, unit="radians"
                )
                text = (
                    modification_state.value if modification_state is not None else ""
                )
                text_layout = momapy.core.TextLayout(
                    text=text,
                    font_size=cls._DEFAULT_MODIFICATION_FONT_SIZE,
                    font_family=cls._DEFAULT_FONT_FAMILY,
                    fill=cls._DEFAULT_FONT_FILL,
                    stroke=momapy.drawing.NoneValue,
                    position=layout_element.label_center(),
                )
                layout_element.label = text_layout
                cd_modification_residue_name = cd_modification_residue.get("name")
                if cd_modification_residue_name is not None:
                    residue_text_layout = layout.new_element(momapy.core.TextLayout)
                    residue_text_layout.text = cd_modification_residue_name
                    residue_text_layout.font_size = cls._DEFAULT_MODIFICATION_FONT_SIZE
                    residue_text_layout.font_family = cls._DEFAULT_FONT_FAMILY
                    residue_text_layout.fill = cls._DEFAULT_FONT_FILL
                    residue_text_layout.stroke = momapy.drawing.NoneValue
                    segment = momapy.geometry.Segment(
                        layout_element.center(), super_layout_element.center()
                    )
                    fraction = (
                        layout_element.height + cls._DEFAULT_MODIFICATION_FONT_SIZE
                    ) / segment.length()
                    residue_text_layout.position = segment.get_position_at_fraction(
                        fraction
                    )
                    residue_text_layout = momapy.builder.object_from_builder(
                        residue_text_layout
                    )
                    layout_element.layout_elements.append(residue_text_layout)
                layout_element = momapy.builder.object_from_builder(layout_element)
                super_layout_element.layout_elements.append(layout_element)
                cd_id_to_layout_element[layout_element.id_] = layout_element
            else:
                layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_species_structural_state_from_cd_species_structural_state(
        cls,
        model,
        layout,
        cd_species_structural_state,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if model is not None:
            model_element = model.new_element(momapy.celldesigner.core.StructuralState)
            model_element.value = cd_species_structural_state.get("structuralState")
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.structural_states.add(model_element)
        else:
            model_element = None
        if layout is not None:  # TODO
            layout_element = layout.new_element(
                momapy.celldesigner.core.StructuralStateLayout
            )
            layout_element.position = super_layout_element.self_angle(90)
            text = cd_species_structural_state.get("structuralState")
            text_layout = momapy.core.TextLayout(
                text=text,
                font_size=cls._DEFAULT_MODIFICATION_FONT_SIZE,
                font_family=cls._DEFAULT_FONT_FAMILY,
                fill=cls._DEFAULT_FONT_FILL,
                stroke=momapy.drawing.NoneValue,
                position=layout_element.position,
            )
            layout_element.label = text_layout
            ink_bbox = text_layout.ink_bbox()
            layout_element.width = 1.5 * ink_bbox.width
            layout_element.height = 1.5 * ink_bbox.height
            layout_element = momapy.builder.object_from_builder(layout_element)
            super_layout_element.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_reaction_from_cd_reaction(
        cls,
        cd_reaction,
        model,
        layout,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        if model is not None or layout is not None:
            key = cls._get_key_from_cd_reaction(cd_reaction)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            cd_base_reactants = cls._get_base_reactants_from_cd_reaction(cd_reaction)
            cd_base_products = cls._get_base_products_from_cd_reaction(cd_reaction)
            if model is not None:
                model_element = model.new_element(model_element_cls)
                model_element.id_ = cd_reaction.get("id")
                model_element.reversible = cd_reaction.get("reversible") == "true"
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(layout_element_cls)
                layout_element.id_ = cd_reaction.get("id")
                layout_element.reversible = cd_reaction.get("reversible") == "true"
                if not layout_element.reversible:
                    layout_element.start_shorten = 0.0
                if len(cd_base_reactants) == 1 and len(cd_base_products) == 1:
                    segments = cls._make_segments_from_non_t_shape_cd_reaction(
                        cd_reaction,
                        cd_id_to_layout_element,
                    )
                    reaction_node_segment = int(
                        cls._get_rectangle_index_from_cd_reaction(cd_reaction)
                    )
                    make_base_reactant_layouts = False
                    make_base_product_layouts = False
                elif len(cd_base_reactants) > 1 and len(cd_base_products) == 1:
                    segments = cls._make_segments_from_left_t_shape_cd_reaction(
                        cd_reaction,
                        cd_id_to_layout_element,
                    )
                    reaction_node_segment = int(
                        cls._get_t_shape_index_from_cd_reaction(cd_reaction)
                    )
                    make_base_reactant_layouts = True
                    make_base_product_layouts = False
                elif len(cd_base_reactants) == 1 and len(cd_base_products) > 1:
                    segments = cls._make_segments_from_right_t_shape_cd_reaction(
                        cd_reaction,
                        cd_id_to_layout_element,
                    )
                    reaction_node_segment = (
                        len(segments)
                        - 1
                        - int(cls._get_t_shape_index_from_cd_reaction(cd_reaction))
                    )
                    make_base_reactant_layouts = False
                    make_base_product_layouts = True
                for segment in segments:
                    layout_element.segments.append(segment)
                layout_element.reaction_node_segment = reaction_node_segment
            else:
                layout_element = None
                make_base_reactant_layouts = False
                make_base_product_layouts = False
            for n_cd_base_reactant, cd_base_reactant in enumerate(cd_base_reactants):
                reactant_model_element, reactant_layout_element = (
                    cls._make_and_add_reactant_from_cd_base_reactant(
                        model=model,
                        layout=layout if make_base_reactant_layouts else None,
                        cd_base_reactant=cd_base_reactant,
                        n_cd_base_reactant=n_cd_base_reactant,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        model_element_to_layout_element=model_element_to_layout_element,
                        map_element_to_ids=map_element_to_ids,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
            for cd_reactant_link in cls._get_reactant_links_from_cd_reaction(
                cd_reaction
            ):
                reactant_model_element, reactant_layout_element = (
                    cls._make_and_add_reactant_from_cd_reactant_link(
                        model=model,
                        layout=layout,
                        cd_reactant_link=cd_reactant_link,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        model_element_to_layout_element=model_element_to_layout_element,
                        map_element_to_ids=map_element_to_ids,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
            for n_cd_base_product, cd_base_product in enumerate(cd_base_products):
                product_model_element, product_layout_element = (
                    cls._make_and_add_product_from_cd_base_product(
                        model=model,
                        layout=layout if make_base_product_layouts else None,
                        cd_base_product=cd_base_product,
                        n_cd_base_product=n_cd_base_product,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        model_element_to_layout_element=model_element_to_layout_element,
                        map_element_to_ids=map_element_to_ids,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
            for cd_product_link in cls._get_product_links_from_cd_reaction(cd_reaction):
                product_model_element, product_layout_element = (
                    cls._make_and_add_product_from_cd_product_link(
                        model=model,
                        layout=layout,
                        cd_product_link=cd_product_link,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        model_element_to_layout_element=model_element_to_layout_element,
                        map_element_to_ids=map_element_to_ids,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
            for (
                cd_reaction_modification
            ) in cls._get_reaction_modifications_from_cd_reaction(cd_reaction):
                modifier_model_element, modifier_layout_element = (
                    cls._make_and_add_modifier_from_cd_reaction_modification(
                        model=model,
                        layout=layout,
                        cd_reaction_modification=cd_reaction_modification,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        model_element_to_layout_element=model_element_to_layout_element,
                        map_element_to_ids=map_element_to_ids,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_cd_element=cd_reaction,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
                pass
            if model is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    model.reactions,
                    func=lambda element, existing_element: element.id_
                    < existing_element.id_,
                )
                cd_id_to_model_element[model_element.id_] = model_element
                map_element_to_ids[model_element].add(cd_reaction.get("id"))
                if with_annotations:
                    annotations = cls._make_annotations_from_cd_element(cd_reaction)
                    if annotations:
                        map_element_to_annotations[model_element].update(annotations)
                    if with_notes:
                        notes = cls._make_notes_from_cd_element(cd_reaction)
                        map_element_to_notes[model_element].update(notes)
            if layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                layout.layout_elements.append(layout_element)
                cd_id_to_layout_element[layout_element.id_] = layout_element
            if model is not None and layout is not None:
                model_element_to_layout_element.add_mapping(
                    layout_element, model_element
                )
        return model_element, layout_element

    @classmethod
    def _make_segments_from_non_t_shape_cd_reaction(
        cls, cd_reaction, cd_id_to_layout_element
    ):
        # Case where we have a linear reaction (one base reactant
        # and one base product). The frame for the edit points
        # is the orthonormal frame whose x axis goes from the
        # base reactant's center or link anchor to the base product's
        # center or link anchor and whose y axis is orthogonal to
        # to the x axis, going downwards
        cd_base_reactants = cls._get_base_reactants_from_cd_reaction(cd_reaction)
        cd_base_products = cls._get_base_products_from_cd_reaction(cd_reaction)
        cd_base_reactant = cd_base_reactants[0]
        cd_base_product = cd_base_products[0]
        reactant_layout_element = cd_id_to_layout_element[cd_base_reactant.get("alias")]
        product_layout_element = cd_id_to_layout_element[cd_base_product.get("alias")]
        reactant_anchor_name = cls._get_anchor_name_for_frame_from_cd_link(
            cd_base_reactant
        )
        product_anchor_name = cls._get_anchor_name_for_frame_from_cd_link(
            cd_base_product
        )
        origin = reactant_layout_element.anchor_point(reactant_anchor_name)
        unit_x = product_layout_element.anchor_point(product_anchor_name)
        unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
        transformation = momapy.geometry.get_transformation_for_frame(
            origin, unit_x, unit_y
        )
        intermediate_points = []
        cd_edit_points = cls._get_edit_points_from_cd_reaction(cd_reaction)
        if cd_edit_points is None:
            edit_points = []
        else:
            edit_points = cls._make_points_from_cd_edit_points(cd_edit_points)
        intermediate_points = [
            edit_point.transformed(transformation) for edit_point in edit_points
        ]
        if reactant_anchor_name == "center":
            if intermediate_points:
                reference_point = intermediate_points[0]

            else:
                reference_point = product_layout_element.anchor_point(
                    product_anchor_name
                )
            start_point = reactant_layout_element.border(reference_point)
        else:
            start_point = reactant_layout_element.anchor_point(reactant_anchor_name)
        if product_anchor_name == "center":
            if intermediate_points:
                reference_point = intermediate_points[-1]
            else:
                reference_point = reactant_layout_element.anchor_point(
                    reactant_anchor_name
                )
            end_point = product_layout_element.border(reference_point)
        else:
            end_point = product_layout_element.anchor_point(product_anchor_name)
        points = [start_point] + intermediate_points + [end_point]
        return cls._make_segments_from_points(points)

    @classmethod
    def _make_segments_from_left_t_shape_cd_reaction(
        cls, cd_reaction, cd_id_to_layout_element
    ):
        # Case where we have a tshape reaction with two base reactants
        # and one base product. The frame for the edit points are the
        # axes going from the center of the first base reactant to
        # the center of the second base reactant (x axis), and from the
        # center of the first base reactant to the center of the base
        # product (y axis).
        cd_base_reactants = cls._get_base_reactants_from_cd_reaction(cd_reaction)
        cd_base_products = cls._get_base_products_from_cd_reaction(cd_reaction)
        cd_base_reactant_0 = cd_base_reactants[0]
        cd_base_reactant_1 = cd_base_reactants[1]
        cd_base_product = cd_base_products[0]
        reactant_layout_element_0 = cd_id_to_layout_element[
            cd_base_reactant_0.get("alias")
        ]
        reactant_layout_element_1 = cd_id_to_layout_element[
            cd_base_reactant_1.get("alias")
        ]
        product_layout_element = cd_id_to_layout_element[cd_base_product.get("alias")]
        product_anchor_name = cls._get_anchor_name_for_frame_from_cd_link(
            cd_base_product
        )
        origin = reactant_layout_element_0.center()
        unit_x = reactant_layout_element_1.center()
        unit_y = product_layout_element.center()
        transformation = momapy.geometry.get_transformation_for_frame(
            origin, unit_x, unit_y
        )
        cd_edit_points = cls._get_edit_points_from_cd_reaction(cd_reaction)
        edit_points = cls._make_points_from_cd_edit_points(cd_edit_points)
        start_point = edit_points[-1].transformed(transformation)
        # The frame for the intermediate edit points becomes
        # the orthonormal frame whose x axis goes from the
        # start point of the reaction computed above to the base
        # product's center or link anchor and whose y axis is
        # orthogonal to the x axis, going downwards
        origin = start_point
        unit_x = product_layout_element.anchor_point(product_anchor_name)
        unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
        transformation = momapy.geometry.get_transformation_for_frame(
            origin, unit_x, unit_y
        )
        intermediate_points = []
        # the index for the intermediate points of the reaction
        # starts after those for the two base reactants
        start_index = int(cd_edit_points.get("num0")) + int(cd_edit_points.get("num1"))
        for edit_point in edit_points[start_index:-1]:
            intermediate_point = edit_point.transformed(transformation)
            intermediate_points.append(intermediate_point)
        if getattr(cd_base_product, "linkAnchor", None) is not None:
            end_point = product_layout_element.anchor_point(
                cls._get_anchor_name_for_frame_from_cd_link(cd_base_product)
            )
        else:
            if intermediate_points:
                reference_point = intermediate_points[-1]
            else:
                reference_point = start_point
            end_point = product_layout_element.border(reference_point)
        points = [start_point] + intermediate_points + [end_point]
        return cls._make_segments_from_points(points)

    @classmethod
    def _make_segments_from_right_t_shape_cd_reaction(
        cls, cd_reaction, cd_id_to_layout_element
    ):
        # Case where we have a tshape reaction with one base reactant
        # and two base products. The frame for the edit points are the
        # axes going from the center of the first base product to
        # the center of the second base product (x axis), and from the
        # center of the first base product to the center of the base
        # reactant (y axis).
        cd_base_reactants = cls._get_base_reactants_from_cd_reaction(cd_reaction)
        cd_base_products = cls._get_base_products_from_cd_reaction(cd_reaction)
        cd_base_product_0 = cd_base_products[0]
        cd_base_product_1 = cd_base_products[1]
        cd_base_reactant = cd_base_reactants[0]
        product_layout_element_0 = cd_id_to_layout_element[
            cd_base_product_0.get("alias")
        ]
        product_layout_element_1 = cd_id_to_layout_element[
            cd_base_product_1.get("alias")
        ]
        reactant_layout_element = cd_id_to_layout_element[cd_base_reactant.get("alias")]
        reactant_anchor_name = cls._get_anchor_name_for_frame_from_cd_link(
            cd_base_reactant
        )
        origin = reactant_layout_element.center()
        unit_x = product_layout_element_0.center()
        unit_y = product_layout_element_1.center()
        transformation = momapy.geometry.get_transformation_for_frame(
            origin, unit_x, unit_y
        )
        cd_edit_points = cls._get_edit_points_from_cd_reaction(cd_reaction)
        edit_points = cls._make_points_from_cd_edit_points(cd_edit_points)
        end_point = edit_points[-1].transformed(transformation)
        # The frame for the intermediate edit points becomes
        # the orthonormal frame whose x axis goes from the
        # start point of the reaction computed above to the base
        # product's center or link anchor and whose y axis is
        # orthogonal to the x axis, going downwards
        origin = end_point
        unit_x = reactant_layout_element.anchor_point(reactant_anchor_name)
        unit_y = unit_x.transformed(momapy.geometry.Rotation(math.radians(90), origin))
        transformation = momapy.geometry.get_transformation_for_frame(
            origin, unit_x, unit_y
        )
        intermediate_points = []
        # the index for the intermediate points of the reaction
        # starts at 0 and ends at before those for the two base products
        end_index = int(cd_edit_points.get("num0"))
        edit_points = list(reversed(edit_points[:end_index]))
        for edit_point in edit_points:
            intermediate_point = edit_point.transformed(transformation)
            intermediate_points.append(intermediate_point)
        if getattr(cd_base_reactant, "linkAnchor", None) is not None:
            start_point = reactant_layout_element.anchor_point(
                cls._get_anchor_name_for_frame_from_cd_link(cd_base_reactant)
            )
        else:
            if intermediate_points:
                reference_point = intermediate_points[0]
            else:
                reference_point = end_point
            start_point = reactant_layout_element.border(reference_point)
        points = [start_point] + intermediate_points + [end_point]
        return cls._make_segments_from_points(points)

    @classmethod
    def _make_and_add_reactant_from_cd_base_reactant(
        cls,
        model,
        layout,
        cd_base_reactant,
        n_cd_base_reactant,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if model is not None:
            model_element = model.new_element(momapy.celldesigner.core.Reactant)
            cd_species_id = cd_base_reactant.get("species")
            # the id and stoichiometry is stored in the reactant, not
            # base reactant, so we get the corresponding reactant
            for cd_reactant in cls._get_reactants_from_cd_reaction(super_cd_element):
                if cd_reactant.get("species") == cd_species_id:
                    model_element.id_ = cd_reactant.get("metaid")
                    cd_stoichiometry = cd_reactant.get("stoichiometry")
                    if cd_stoichiometry is not None:
                        model_element.stoichiometry = float(cd_stoichiometry)
                    break
            if model_element.id_ is None:
                model_element.id_ = f"{super_cd_element.get('id')}_{cd_species_id}"
            species_model_element = cd_id_to_model_element[
                cd_base_reactant.get("alias")
            ]
            model_element.referred_species = species_model_element
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.reactants.add(model_element)
            cd_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if layout is not None:
            layout_element = layout.new_element(
                momapy.celldesigner.core.ConsumptionLayout
            )
            cd_edit_points = cls._get_edit_points_from_cd_reaction(super_cd_element)
            cd_num_0 = cd_edit_points.get("num0")
            cd_num_1 = cd_edit_points.get("num1")
            if n_cd_base_reactant == 0:
                start_index = n_cd_base_reactant
                stop_index = int(cd_num_0)
            elif n_cd_base_reactant == 1:
                start_index = int(cd_num_0)
                stop_index = int(cd_num_0) + int(cd_num_1)
            species_layout_element = cd_id_to_layout_element[
                cd_base_reactant.get("alias")
            ]
            reactant_anchor_name = cls._get_anchor_name_for_frame_from_cd_link(
                cd_base_reactant
            )
            origin = super_layout_element.points()[0]
            unit_x = species_layout_element.anchor_point(reactant_anchor_name)
            unit_y = unit_x.transformed(
                momapy.geometry.Rotation(math.radians(90), origin)
            )
            transformation = momapy.geometry.get_transformation_for_frame(
                origin, unit_x, unit_y
            )
            intermediate_points = []
            edit_points = cls._make_points_from_cd_edit_points(cd_edit_points)
            for edit_point in edit_points[start_index:stop_index]:
                intermediate_point = edit_point.transformed(transformation)
                intermediate_points.append(intermediate_point)
            intermediate_points.reverse()
            if reactant_anchor_name == "center":
                if intermediate_points:
                    reference_point = intermediate_points[0]
                else:
                    reference_point = super_layout_element.start_point()

                start_point = species_layout_element.border(reference_point)
            else:
                start_point = species_layout_element.anchor_point(reactant_anchor_name)
            if intermediate_points:
                reference_point = intermediate_points[-1]
            else:
                reference_point = start_point
            end_point = super_layout_element.start_arrowhead_border(reference_point)
            points = [start_point] + intermediate_points + [end_point]
            segments = cls._make_segments_from_points(points)
            for segment in segments:
                layout_element.segments.append(segment)
            layout_element = momapy.builder.object_from_builder(layout_element)
            super_layout_element.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_reactant_from_cd_reactant_link(
        cls,
        model,
        layout,
        cd_reactant_link,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if model is not None:
            model_element = model.new_element(momapy.celldesigner.core.Reactant)
            cd_species_id = cd_reactant_link.get("reactant")
            for cd_reactant in cls._get_reactants_from_cd_reaction(super_cd_element):
                if cd_reactant.get("species") == cd_species_id:
                    model_element.id_ = cd_reactant.get("metaid")
                    cd_stoichiometry = cd_reactant.get("stoichiometry")
                    if cd_stoichiometry is not None:
                        model_element.stoichiometry = float(cd_stoichiometry)
                    break
            if model_element.id_ is None:
                model_element.id_ = f"{super_cd_element.get('id')}_{cd_species_id}"
            species_model_element = cd_id_to_model_element[
                cd_reactant_link.get("alias")
            ]
            model_element.referred_species = species_model_element
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.reactants.add(model_element)
            cd_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if layout is not None:
            layout_element = layout.new_element(
                momapy.celldesigner.core.ConsumptionLayout
            )
            species_layout_element = cd_id_to_layout_element[
                cd_reactant_link.get("alias")
            ]
            reactant_anchor_name = cls._get_anchor_name_for_frame_from_cd_link(
                cd_reactant_link
            )
            origin = species_layout_element.center()
            unit_x = super_layout_element.left_connector_tip()
            unit_y = unit_x.transformed(
                momapy.geometry.Rotation(math.radians(90), origin)
            )
            transformation = momapy.geometry.get_transformation_for_frame(
                origin, unit_x, unit_y
            )
            cd_edit_points = cls._get_edit_points_from_cd_participant_link(
                cd_reactant_link
            )
            if cd_edit_points is None:
                edit_points = []
            else:
                edit_points = cls._make_points_from_cd_edit_points(cd_edit_points)
            intermediate_points = [
                edit_point.transformed(transformation) for edit_point in edit_points
            ]
            end_point = unit_x
            if reactant_anchor_name == "center":
                if intermediate_points:
                    reference_point = intermediate_points[0]
                else:
                    reference_point = end_point
                start_point = species_layout_element.border(reference_point)
            else:
                start_point = species_layout_element.anchor_point(reactant_anchor_name)
            points = [start_point] + intermediate_points + [end_point]
            segments = cls._make_segments_from_points(points)
            for segment in segments:
                layout_element.segments.append(segment)
            layout_element = momapy.builder.object_from_builder(layout_element)
            super_layout_element.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_product_from_cd_base_product(
        cls,
        model,
        layout,
        cd_base_product,
        n_cd_base_product,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if model is not None:
            model_element = model.new_element(momapy.celldesigner.core.Product)
            cd_species_id = cd_base_product.get("species")
            # the id and stoichiometry is stored in the product, not
            # base product, so we get the corresponding product
            for cd_product in cls._get_products_from_cd_reaction(super_cd_element):
                if cd_product.get("species") == cd_species_id:
                    model_element.id_ = cd_product.get("metaid")
                    cd_stoichiometry = cd_product.get("stoichiometry")
                    if cd_stoichiometry is not None:
                        model_element.stoichiometry = float(cd_stoichiometry)
                    break
            if model_element.id_ is None:
                model_element.id_ = f"{super_cd_element.get('id')}_{cd_species_id}"
            species_model_element = cd_id_to_model_element[cd_base_product.get("alias")]
            model_element.referred_species = species_model_element
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.products.add(model_element)
            cd_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if layout is not None:
            layout_element = layout.new_element(
                momapy.celldesigner.core.ProductionLayout
            )
            cd_edit_points = cls._get_edit_points_from_cd_reaction(super_cd_element)
            cd_num_0 = cd_edit_points.get("num0")
            cd_num_1 = cd_edit_points.get("num1")
            cd_num_2 = cd_edit_points.get("num2")
            if n_cd_base_product == 0:
                start_index = int(cd_num_0)
                stop_index = int(cd_num_0) + int(cd_num_1)
            elif n_cd_base_product == 1:
                start_index = int(cd_num_0) + int(cd_num_1)
                stop_index = int(cd_num_0) + int(cd_num_1) + int(cd_num_2)
            product_layout_element = cd_id_to_layout_element[
                cd_base_product.get("alias")
            ]
            product_anchor_name = cls._get_anchor_name_for_frame_from_cd_link(
                cd_base_product
            )
            origin = super_layout_element.end_point()
            unit_x = product_layout_element.anchor_point(product_anchor_name)
            unit_y = unit_x.transformed(
                momapy.geometry.Rotation(math.radians(90), origin)
            )
            transformation = momapy.geometry.get_transformation_for_frame(
                origin, unit_x, unit_y
            )
            intermediate_points = []
            edit_points = cls._make_points_from_cd_edit_points(cd_edit_points)
            for edit_point in edit_points[start_index:stop_index]:
                intermediate_point = edit_point.transformed(transformation)
                intermediate_points.append(intermediate_point)
            if product_anchor_name == "center":
                if intermediate_points:
                    reference_point = intermediate_points[-1]
                else:
                    reference_point = super_layout_element.end_point()
                end_point = product_layout_element.border(reference_point)
            else:
                end_point = product_layout_element.anchor_point(product_anchor_name)
            if intermediate_points:
                reference_point = intermediate_points[0]
            else:
                reference_point = end_point
            start_point = super_layout_element.end_arrowhead_border(reference_point)
            points = [start_point] + intermediate_points + [end_point]
            segments = cls._make_segments_from_points(points)
            for segment in segments:
                layout_element.segments.append(segment)
            layout_element = momapy.builder.object_from_builder(layout_element)
            super_layout_element.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_product_from_cd_product_link(
        cls,
        model,
        layout,
        cd_product_link,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if model is not None:
            model_element = model.new_element(momapy.celldesigner.core.Product)
            cd_species_id = cd_product_link.get("product")
            # the id and stoichiometry is stored in the product, not
            # base product, so we get the corresponding product
            for cd_product in cls._get_products_from_cd_reaction(super_cd_element):
                if cd_product.get("species") == cd_species_id:
                    model_element.id_ = cd_product.get("metaid")
                    cd_stoichiometry = cd_product.get("stoichiometry")
                    if cd_stoichiometry is not None:
                        model_element.stoichiometry = float(cd_stoichiometry)
                    break
            if model_element.id_ is None:
                model_element.id_ = f"{super_cd_element.get('id')}_{cd_species_id}"
            species_model_element = cd_id_to_model_element[cd_product_link.get("alias")]
            model_element.referred_species = species_model_element
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.products.add(model_element)
            cd_id_to_model_element[model_element.id_] = model_element
        else:
            model_element = None
        if layout is not None:
            layout_element = layout.new_element(
                momapy.celldesigner.core.ProductionLayout
            )
            species_layout_element = cd_id_to_layout_element[
                cd_product_link.get("alias")
            ]
            product_anchor_name = cls._get_anchor_name_for_frame_from_cd_link(
                cd_product_link
            )
            origin = super_layout_element.right_connector_tip()
            unit_x = species_layout_element.center()
            unit_y = unit_x.transformed(
                momapy.geometry.Rotation(math.radians(90), origin)
            )
            transformation = momapy.geometry.get_transformation_for_frame(
                origin, unit_x, unit_y
            )
            cd_edit_points = cls._get_edit_points_from_cd_participant_link(
                cd_product_link
            )
            if cd_edit_points is None:
                edit_points = []
            else:
                edit_points = cls._make_points_from_cd_edit_points(cd_edit_points)
            intermediate_points = [
                edit_point.transformed(transformation) for edit_point in edit_points
            ]
            intermediate_points.reverse()
            start_point = origin
            if product_anchor_name == "center":
                if intermediate_points:
                    reference_point = intermediate_points[-1]
                else:
                    reference_point = start_point
                end_point = species_layout_element.border(reference_point)
            else:
                end_point = species_layout_element.anchor_point(product_anchor_name)
            points = [start_point] + intermediate_points + [end_point]
            segments = cls._make_segments_from_points(points)
            for segment in segments:
                layout_element.segments.append(segment)
            layout_element = momapy.builder.object_from_builder(layout_element)
            super_layout_element.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_modifier_from_cd_reaction_modification(
        cls,
        model,
        layout,
        cd_reaction_modification,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if model is not None or layout is not None:
            key = cls._get_key_from_cd_reaction_modification(cd_reaction_modification)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            has_boolean_input = cls._has_boolean_input_from_cd_reaction_modification(
                cd_reaction_modification
            )
            if has_boolean_input:
                source_model_element, source_layout_element = (
                    cls._make_and_add_logic_gate_from_cd_reaction_modification_or_cd_gate_member(
                        model=model,
                        layout=layout,
                        cd_reaction_modification_or_cd_gate_member=cd_reaction_modification,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        model_element_to_layout_element=model_element_to_layout_element,
                        map_element_to_ids=map_element_to_ids,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
            if model is not None:
                model_element = model.new_element(model_element_cls)
                if not has_boolean_input:
                    source_model_element = cd_id_to_model_element[
                        cd_reaction_modification.get("aliases")
                    ]
                model_element.referred_species = source_model_element
                if model_element is not None:  # to delete
                    model_element = momapy.builder.object_from_builder(model_element)
                    super_model_element.modifiers.add(model_element)
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(layout_element_cls)
                cd_edit_points = cd_reaction_modification.get("editPoints")
                if cd_edit_points is not None:
                    edit_points = cls._make_points_from_cd_edit_points(cd_edit_points)
                else:
                    edit_points = []
                if not has_boolean_input:
                    source_layout_element = cd_id_to_layout_element[
                        cd_reaction_modification.get("aliases")
                    ]
                    cd_link_target = getattr(
                        cd_reaction_modification, "linkTarget", None
                    )
                    if cd_link_target is not None:
                        cd_link_anchor = getattr(cd_link_target, "linkAnchor", None)
                        if cd_link_anchor is not None:
                            source_anchor_name = (
                                cls._get_anchor_name_for_frame_from_cd_link(
                                    cd_link_target
                                )
                            )
                        else:
                            source_anchor_name = "center"
                    else:
                        source_anchor_name = "center"
                else:
                    source_anchor_name = "center"
                    edit_points = edit_points[
                        :-1
                    ]  # last point is the position of the logic gate
                origin = source_layout_element.anchor_point(source_anchor_name)
                unit_x = super_layout_element._get_reaction_node_position()
                unit_y = unit_x.transformed(
                    momapy.geometry.Rotation(math.radians(90), origin)
                )
                transformation = momapy.geometry.get_transformation_for_frame(
                    origin, unit_x, unit_y
                )
                intermediate_points = [
                    edit_point.transformed(transformation) for edit_point in edit_points
                ]
                if source_anchor_name == "center":
                    if intermediate_points:
                        reference_point = intermediate_points[0]
                    else:
                        reference_point = unit_x
                    start_point = source_layout_element.border(reference_point)
                else:
                    start_point = origin
                if intermediate_points:
                    reference_point = intermediate_points[-1]
                else:
                    reference_point = start_point
                end_point = super_layout_element.reaction_node_border(reference_point)
                points = [start_point] + intermediate_points + [end_point]
                segments = cls._make_segments_from_points(points)
                for segment in segments:
                    layout_element.segments.append(segment)
                layout_element = momapy.builder.object_from_builder(layout_element)
                super_layout_element.layout_elements.append(layout_element)
            else:
                layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_logic_gate_from_cd_reaction_modification_or_cd_gate_member(
        cls,
        model,
        layout,
        cd_reaction_modification_or_cd_gate_member,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        if model is not None or layout is not None:
            key = cls._get_key_from_cd_reaction_modification_or_cd_gate_member(
                cd_reaction_modification_or_cd_gate_member
            )
            cd_modifiers = cd_reaction_modification_or_cd_gate_member.get("aliases")
            if model is not None:
                model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
                model_element = model.new_element(model_element_cls)
                model_input_elements = [
                    cd_id_to_model_element[cd_input_id]
                    for cd_input_id in cd_modifiers.split(",")
                ]
                for model_input_element in model_input_elements:
                    model_element.inputs.add(model_input_element)
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    model.boolean_logic_gates,
                    func=lambda element, existing_element: element.id_
                    < existing_element.id_,
                )
            else:
                model_element = None
            if layout is not None:  # TODO: edit points
                layout_element = layout.new_element(layout_element_cls)
                cd_edit_points = cd_reaction_modification_or_cd_gate_member.get(
                    "editPoints"
                )
                edit_points = cls._make_points_from_cd_edit_points(cd_edit_points)
                position = edit_points[-1]
                layout_element.position = position
                layout_input_elements = [
                    cd_id_to_layout_element[cd_input_id]
                    for cd_input_id in cd_modifiers.split(",")
                ]
                for layout_input_element in layout_input_elements:
                    layout_logic_arc = layout.new_element(
                        momapy.celldesigner.core.LogicArcLayout
                    )
                    start_point = layout_input_element.border(position)
                    end_point = layout_element.border(start_point)
                    segment = momapy.geometry.Segment(start_point, end_point)
                    layout_logic_arc.segments.append(segment)
                    layout_logic_arc.target = layout_input_element
                    layout_logic_arc = momapy.builder.object_from_builder(
                        layout_logic_arc
                    )
                    layout_element.layout_elements.append(layout_logic_arc)
                layout_element = momapy.builder.object_from_builder(layout_element)
                layout.layout_elements.append(layout_element)
            else:
                layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_modulation_from_cd_reaction(
        cls,
        model,
        layout,
        cd_reaction,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        map_element_to_notes,
        model_element_to_layout_element,
        map_element_to_ids,
        with_annotations,
        with_notes,
    ):
        if model is not None or layout is not None:
            key = cls._get_key_from_cd_reaction(cd_reaction)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            has_boolean_input = cls._has_boolean_input_from_cd_reaction(cd_reaction)
            cd_base_reactant = cls._get_base_reactants_from_cd_reaction(cd_reaction)[0]
            cd_base_product = cls._get_base_products_from_cd_reaction(cd_reaction)[0]
            if has_boolean_input:
                cd_gate_members = cls._get_gate_members_from_cd_reaction(cd_reaction)
                cd_gate_member = cd_gate_members[0]
                source_model_element, source_layout_element = (
                    cls._make_and_add_logic_gate_from_cd_reaction_modification_or_cd_gate_member(
                        model=model,
                        layout=layout,
                        cd_reaction_modification_or_cd_gate_member=cd_gate_member,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        model_element_to_layout_element=model_element_to_layout_element,
                        map_element_to_ids=map_element_to_ids,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
            if model is not None:
                model_element = model.new_element(model_element_cls)
                model_element.id_ = cd_reaction.get("id")
                if has_boolean_input:
                    source_model_element, source_layout_element = (
                        cls._make_and_add_logic_gate_from_cd_reaction_modification_or_cd_gate_member(
                            model=model,
                            layout=layout,
                            cd_reaction_modification_or_cd_gate_member=cd_gate_member,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            map_element_to_annotations=map_element_to_annotations,
                            map_element_to_notes=map_element_to_notes,
                            model_element_to_layout_element=model_element_to_layout_element,
                            map_element_to_ids=map_element_to_ids,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                        )
                    )
                else:
                    source_model_element = cd_id_to_model_element[
                        cd_base_reactant.get("alias")
                    ]
                model_element.source = source_model_element
                target_model_element = cd_id_to_model_element[
                    cd_base_product.get("alias")
                ]
                model_element.target = target_model_element
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    model.modulations,
                    func=lambda element, existing_element: element.id_
                    < existing_element.id_,
                )
                map_element_to_ids[model_element].add(cd_reaction.get("id"))
                if with_annotations:
                    annotations = cls._make_annotations_from_cd_element(cd_reaction)
                    if annotations:
                        map_element_to_annotations[model_element].update(annotations)
                    if with_notes:
                        notes = cls._make_notes_from_cd_element(cd_reaction)
                        map_element_to_notes[model_element].update(notes)
            else:
                model_element = None
            if layout is not None:
                cd_edit_points = cls._get_edit_points_from_cd_reaction(cd_reaction)
                if cd_edit_points is not None:
                    edit_points = cls._make_points_from_cd_edit_points(cd_edit_points)
                else:
                    edit_points = []
                if has_boolean_input:
                    source_anchor_name = "center"
                    edit_points = edit_points[:-1]
                else:
                    source_layout_element = cd_id_to_layout_element[
                        cd_base_reactant.get("alias")
                    ]
                    if hasattr(cd_base_reactant, "linkAnchor"):
                        source_anchor_name = (
                            cls._get_anchor_name_for_frame_from_cd_link(
                                cd_base_reactant
                            )
                        )
                    else:
                        source_anchor_name = "center"
                layout_element = layout.new_element(layout_element_cls)
                target_layout_element = cd_id_to_layout_element[
                    cd_base_product.get("alias")
                ]
                if hasattr(cd_base_product, "linkAnchor"):
                    target_anchor_name = cls._get_anchor_name_for_frame_from_cd_link(
                        cd_base_product
                    )
                else:
                    target_anchor_name = "center"
                origin = source_layout_element.anchor_point(source_anchor_name)
                unit_x = target_layout_element.anchor_point(target_anchor_name)
                unit_y = unit_x.transformed(
                    momapy.geometry.Rotation(math.radians(90), origin)
                )
                transformation = momapy.geometry.get_transformation_for_frame(
                    origin, unit_x, unit_y
                )
                intermediate_points = [
                    edit_point.transformed(transformation) for edit_point in edit_points
                ]
                if source_anchor_name == "center":
                    if intermediate_points:
                        reference_point = intermediate_points[0]
                    else:
                        reference_point = unit_x
                    start_point = source_layout_element.border(reference_point)
                else:
                    start_point = origin
                if target_anchor_name == "center":
                    if intermediate_points:
                        reference_point = intermediate_points[-1]
                    else:
                        reference_point = start_point
                    end_point = target_layout_element.border(reference_point)
                else:
                    end_point = target_layout_element.anchor_point(target_anchor_name)
                points = [start_point] + intermediate_points + [end_point]
                segments = cls._make_segments_from_points(points)
                for segment in segments:
                    layout_element.segments.append(segment)
                layout_element = momapy.builder.object_from_builder(layout_element)
                layout.layout_elements.append(layout_element)
            else:
                layout_element = None
            if model is not None and layout is not None:
                model_element_to_layout_element.add_mapping(
                    layout_element, model_element
                )
        return model_element, layout_element


momapy.io.register_reader("celldesigner", CellDesignerReader)
