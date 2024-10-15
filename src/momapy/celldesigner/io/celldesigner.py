import os
import collections
import math
import re
import typing

import lxml.objectify

import momapy.core
import momapy.geometry
import momapy.positioning
import momapy.io
import momapy.coloring
import momapy.celldesigner.core
import momapy.celldesigner.io._celldesigner_parser
import momapy.sbgn.pd


class CellDesignerReader(momapy.io.Reader):
    _DEFAULT_FONT_FAMILY = "Helvetica"
    _DEFAULT_FONT_SIZE = 12.0
    _DEFAULT_MODIFICATION_FONT_SIZE = 9.0
    _DEFAULT_FONT_FILL = momapy.coloring.black
    _CD_NAMESPACE = "http://www.sbml.org/2001/ns/celldesigner"
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
            momapy.celldesigner.core.UnknownInhibition,
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
        ("GATE", "BOOLEAN_LOGIC_GATE_AND"): momapy.celldesigner.core.AndGate,
        ("GATE", "BOOLEAN_LOGIC_GATE_OR"): momapy.celldesigner.core.OrGate,
        ("GATE", "BOOLEAN_LOGIC_GATE_NOT"): momapy.celldesigner.core.NotGate,
        (
            "GATE",
            "BOOLEAN_LOGIC_GATE_UNKNOWN",
        ): momapy.celldesigner.core.UnknownGate,
    }
    _QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER = {
        "encodes": momapy.sbgn.core.BQBiol.ENCODES,
        "has_part": momapy.sbgn.core.BQBiol.HAS_PART,
        "has_property": momapy.sbgn.core.BQBiol.HAS_PROPERTY,
        "has_version": momapy.sbgn.core.BQBiol.HAS_VERSION,
        "is_value": momapy.sbgn.core.BQBiol.IS,
        "is_described_by": momapy.sbgn.core.BQBiol.IS_DESCRIBED_BY,
        "is_encoded_by": momapy.sbgn.core.BQBiol.IS_ENCODED_BY,
        "is_homolog_to": momapy.sbgn.core.BQBiol.IS_HOMOLOG_TO,
        "is_part_of": momapy.sbgn.core.BQBiol.IS_PART_OF,
        "is_property_of": momapy.sbgn.core.BQBiol.IS_PROPERTY_OF,
        "is_version_of": momapy.sbgn.core.BQBiol.IS_VERSION_OF,
        "occurs_in": momapy.sbgn.core.BQBiol.OCCURS_IN,
        "has_taxon": momapy.sbgn.core.BQBiol.HAS_TAXON,
        "has_instance": momapy.sbgn.core.BQModel.HAS_INSTANCE,
        "biomodels_net_model_qualifiers_is": momapy.sbgn.core.BQModel.IS,
        "is_derived_from": momapy.sbgn.core.BQModel.IS_DERIVED_FROM,
        "biomodels_net_model_qualifiers_is_described_by": momapy.sbgn.core.BQModel.IS_DESCRIBED_BY,
        "is_instance_of": momapy.sbgn.core.BQModel.IS_INSTANCE_OF,
    }
    _LINK_ANCHOR_POSITION_TO_ANCHOR_NAME = {
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.NW: "north_west",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.NNW: "north_north_west",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.N: "north",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.NNE: "north_north_east",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.NE: "north_east",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.ENE: "east_north_east",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.E: "east",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.ESE: "east_south_east",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.SE: "south_east",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.SSE: "south_south_east",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.S: "south",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.SSW: "south_south_west",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.SW: "south_west",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.WSW: "west_south_west",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.W: "west",
        momapy.celldesigner.io._celldesigner_parser.LinkAnchorPosition.WNW: "west_north_west",
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
        with open(file_path) as f:
            for line in f:
                if "http://www.sbml.org/2001/ns/celldesigner" in line:
                    return True
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
        cd_document = lxml.objectify.parse(file_path)
        cd_sbml = cd_document.getroot()
        obj, annotations, notes = cls._make_main_obj_from_cd_model(
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
        )
        return result

    @classmethod
    def _get_extension_from_cd_element(cls, cd_element):
        cd_annotation = getattr(cd_element, "annotation", None)
        if cd_annotation is None:
            return None
        cd_extension = getattr(
            cd_element.annotation, f"{{{cls._CD_NAMESPACE}}}extension", None
        )
        return cd_extension

    @classmethod
    def _get_species_from_cd_model(cls, cd_model):
        return list(getattr(cd_model.listOfSpecies, "species", []))

    @classmethod
    def _get_reactions_from_cd_model(cls, cd_model):
        return list(getattr(cd_model.listOfReactions, "reactions", []))

    @classmethod
    def _get_species_aliases_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        return list(
            getattr(extension.listOfSpeciesAliases, "speciesAlias", [])
        )

    @classmethod
    def _get_complex_species_aliases_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        return list(
            getattr(
                extension.listOfComplexSpeciesAliases,
                "complexSpeciesAlias",
                [],
            )
        )

    @classmethod
    def _get_compartments_from_cd_model(cls, cd_model):
        return list(getattr(cd_model.listOfCompartments, "compartment", []))

    @classmethod
    def _get_compartment_aliases_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        return list(
            getattr(extension.listOfCompartmentAliases, "compartmentAlias", [])
        )

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
        return list(getattr(extension.listOfAntisenseRNAs, "antisenseRNA", []))

    @classmethod
    def _get_species_templates_from_cd_model(cls, cd_model):
        return (
            cls._get_protein_templates_from_cd_model(cd_model)
            + cls._get_gene_templates_from_cd_model(cd_model)
            + cls._get_rna_templates_from_cd_model(cd_model)
            + cls._get_antisense_rna_templates_from_cd_model(cd_model)
        )

    @classmethod
    def _get_modification_residues_from_cd_species_template(
        cls, cd_species_template
    ):
        list_of_modification_residues = getattr(
            cd_species_template, "listOfModificationResidues", None
        )
        if list_of_modification_residues is not None:
            modification_residues = list(
                getattr(
                    list_of_modification_residues, "modificationResidue", []
                )
            )
        else:
            modification_residues = []
        return modification_residues

    @classmethod
    def _get_included_species_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        return list(getattr(extension.listOfIncludedSpecies, "species", []))

    @classmethod
    def _get_key_from_cd_reaction(cls, cd_reaction):
        return (
            "REACTION",
            cls._get_extension_from_cd_element(cd_reaction).reactionType.text,
        )

    @classmethod
    def _get_key_from_cd_species_template(cls, cd_species_template):
        return (
            "TEMPLATE",
            cd_species_template.get("type"),
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
            cd_species_state, "listStructuralStates", None
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
            cd_reference = getattr(
                cd_species_identity, cd_species_template_type, None
            )
            if cd_reference is not None:
                cd_species_template = cd_id_to_cd_element[cd_reference.text]
                return cd_species_template
        return None

    @classmethod
    def _get_template_from_cd_species_alias(
        cls, cd_species_alias, cd_id_to_cd_element
    ):
        cd_species_id = cd_species_alias.get("species")
        cd_species = cd_id_to_cd_element[cd_species_id]
        return cls._get_template_from_cd_species(
            cd_species, cd_id_to_cd_element
        )

    @classmethod
    def _get_bounds_from_cd_element(cls, cd_element):
        cd_x = cd_element.bounds.get("x")
        cd_y = cd_element.bounds.get("y")
        cd_w = cd_element.bounds.get("w")
        cd_h = cd_element.bounds.get("h")
        return cd_x, cd_y, cd_w, cd_h

    @classmethod
    def _get_anchor_name_for_frame_from_cd_base_participant(
        cls, cd_base_participant
    ):
        if cd_base_participant.link_anchor is not None:
            cd_base_participant_anchor = cd_base_participant.linkAnchor.get(
                "position"
            )
            anchor_name = cls._LINK_ANCHOR_POSITION_TO_ANCHOR_NAME[
                cd_base_participant_anchor
            ]
        else:
            anchor_name = "center"
        return anchor_name

    @classmethod
    def _get_base_reactants_from_cd_reaction(cls, cd_reaction):
        extension = cls._get_extension_from_cd_element(cd_reaction)
        return list(getattr(extension.baseReactants, "baseReactant", []))

    @classmethod
    def _get_base_products_from_cd_reaction(cls, cd_reaction):
        extension = cls._get_extension_from_cd_element(cd_reaction)
        return list(getattr(extension.baseProducts, "baseProduct", []))

    @classmethod
    def _get_edit_points_from_cd_reaction(cls, cd_reaction):
        extension = cls._get_extension_from_cd_element(cd_reaction)
        edit_points = getattr(extension, "editPoints", None)
        return edit_points

    @classmethod
    def _get_points_from_cd_edit_points(cls, cd_edit_points):
        cd_coordinates = [
            cd_edit_point.split(",")
            for cd_edit_point in cd_edit_points.text.split(" ")
        ]
        points = [
            momapy.geometry.Point(
                float(cd_coordinate[0]), float(cd_coordinate[1])
            )
            for cd_coordinate in cd_coordinates
        ]
        return points

    @classmethod
    def _get_rectangle_index_from_cd_reaction(cls, cd_reaction):
        extension = cls._get_extension_from_cd_element(cd_reaction)
        return extension.connectScheme.get("rectangleIndex")

    @classmethod
    def _get_width_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        return extension.modelDisplay.get("sizeX")

    @classmethod
    def _get_height_from_cd_model(cls, cd_model):
        extension = cls._get_extension_from_cd_element(cd_model)
        return extension.modelDisplay.get("sizeY")

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
            cd_id_to_cd_element[cd_compartment_alias.get("id")] = (
                cd_compartment_alias
            )
        # species templates
        for cd_species_template in cls._get_species_templates_from_cd_model(
            cd_model
        ):
            cd_id_to_cd_element[cd_species_template.get("id")] = (
                cd_species_template
            )
            for (
                cd_modification_residue
            ) in cls._get_modification_residues_from_cd_species_template(
                cd_species_template
            ):
                cd_modification_residue_id = f"{cd_species_template.get('id')}_{cd_modification_residue.get('id')}"
                cd_id_to_cd_element[cd_modification_residue_id] = (
                    cd_modification_residue
                )
        # species
        for cd_species in cls._get_species_from_cd_model(cd_model):
            cd_id_to_cd_element[cd_species.get("id")] = cd_species
        # included species
        for cd_included_species in cls._get_included_species_from_cd_model(
            cd_model
        ):
            cd_id_to_cd_element[cd_included_species.get("id")] = (
                cd_included_species
            )
        # species aliases
        for cd_species_alias in cls._get_species_aliases_from_cd_model(
            cd_model
        ):
            cd_id_to_cd_element[cd_species_alias.get("id")] = cd_species_alias
        # complex species aliases
        for (
            cd_complex_species_alias
        ) in cls._get_complex_species_aliases_from_cd_model(cd_model):
            cd_id_to_cd_element[cd_complex_species_alias.get("id")] = (
                cd_complex_species_alias
            )
        return cd_id_to_cd_element

    @classmethod
    def _make_cd_complex_species_alias_id_to_cd_included_species_alias_id_mapping_from_cd_model(
        cls, cd_model
    ):
        cd_complex_alias_id_to_cd_included_species_ids = (
            collections.defaultdict(list)
        )
        for cd_species_alias in cls._get_species_aliases_from_cd_model(
            cd_model
        ):
            cd_complex_species_alias_id = cd_species_alias.get(
                "complexSpeciesAlias"
            )
            if cd_complex_species_alias_id is not None:
                cd_complex_alias_id_to_cd_included_species_ids[
                    cd_complex_species_alias_id
                ].append(cd_species_alias.get("id"))
        for cd_species_alias in cls._get_complex_species_aliases_from_cd_model(
            cd_model
        ):
            cd_complex_species_alias_id = cd_species_alias.get(
                "complexSpeciesAlias"
            )
            if cd_complex_species_alias_id is not None:
                cd_complex_alias_id_to_cd_included_species_ids[
                    cd_complex_species_alias_id
                ].append(cd_species_alias.get("id"))
        return cd_complex_alias_id_to_cd_included_species_ids

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
            cd_id_to_cd_element = (
                cls._make_cd_id_to_cd_element_mapping_from_cd_model(cd_model)
            )
            cd_complex_alias_id_to_cd_included_species_ids = cls._make_cd_complex_species_alias_id_to_cd_included_species_alias_id_mapping_from_cd_model(
                cd_model
            )
            cd_id_to_model_element = {}
            cd_id_to_layout_element = {}
            map_element_to_annotations = {}
            map_element_to_notes = {}
            model_element_to_layout_element = {}
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
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
            # we make and add the reactions and modulations from celldesigner
            # reactions: a celldesigner reaction is either a true reaction
            # or a false reaction encoding a modulation
            # cls._make_and_add_reactions_and_modulations_from_cd_model(
            #     cd_model=cd_model,
            #     model=model,
            #     layout=layout,
            #     cd_id_to_model_element=cd_id_to_model_element,
            #     cd_id_to_layout_element=cd_id_to_layout_element,
            #     cd_id_to_cd_element=cd_id_to_cd_element,
            #     cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            #     map_element_to_annotations=map_element_to_annotations,
            #     map_element_to_notes=map_element_to_notes,
            #     model_element_to_layout_element=model_element_to_layout_element,
            #     with_annotations=with_annotations,
            #     with_notes=with_notes,
            # )
            if layout is not None:
                cls._set_layout_size_and_position_from_cd_model(
                    cd_model, layout
                )
        if return_type == "model":
            obj = momapy.builder.object_from_builder(model)
        elif return_type == "layout":
            obj = momapy.builder.object_from_builder(layout)
        elif return_type == "map":
            map_ = cls._make_map_no_subelements_from_cd_model(cd_model)
            map_.model = model
            map_.layout = layout
            obj = momapy.builder.object_from_builder(map_)
        annotations = {}  # TODO
        notes = {}  # TODO
        return obj, annotations, notes

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
        with_annotations,
        with_notes,
    ):

        for cd_species_template in cls._get_species_templates_from_cd_model(
            cd_model
        ):
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
        with_annotations,
        with_notes,
    ):
        for cd_reaction in cls._get_reactions_from_cd_model(cd_model):
            key = cls._get_key_from_cd_reaction(cd_reaction)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if isinstance(
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
                model_element = cd_id_to_model_element.get(
                    cd_compartment.get("id")
                )
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
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                        )
                    )
            else:
                model_element = None
            if layout is not None:
                if getattr(cd_compartment_alias, "class").text == "OVAL":
                    layout_element_cls = (
                        momapy.celldesigner.core.OvalCompartmentLayout
                    )
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
                cd_compartment_alias_color = cd_compartment_alias.paint.get(
                    "color"
                )
                cd_compartment_alias_color = (
                    cd_compartment_alias_color[2:]
                    + cd_compartment_alias_color[:2]
                )
                element_color = momapy.coloring.Color.from_hexa(
                    cd_compartment_alias_color
                )
                layout_element.stroke = element_color
                layout_element.inner_stroke = element_color
                layout_element.fill = element_color.with_alpha(0.5)
                layout_element.inner_fill = momapy.coloring.white
                text = cls._prepare_name(cd_compartment.get("name"))
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
                layout_element = momapy.builder.object_from_builder(
                    layout_element
                )
                layout.layout_elements.append(layout_element)
                cd_id_to_layout_element[cd_compartment_alias.get("id")] = (
                    layout_element
                )
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
        with_annotations,
        with_notes,
    ):
        if model is not None:
            model_element = model.new_element(
                momapy.celldesigner.core.Compartment
            )
            model_element.id_ = cd_compartment.get("id")
            model_element.name = cls._prepare_name(cd_compartment.get("name"))
            model_element.metaid = cd_compartment.get("metaid")
            if cd_compartment.get("outside") is not None:
                outside_model_element = cd_id_to_model_element.get(
                    cd_compartment.get("outside")
                )
                # if outside is not already made, we make it
                if outside_model_element is None:
                    cd_outside = cd_id_to_cd_element[
                        cd_compartment.get("outside")
                    ]
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
        with_annotations,
        with_notes,
    ):
        if model is not None:
            key = cls._get_key_from_cd_species_template(cd_species_template)
            model_element_cls = cls._KEY_TO_CLASS[key]
            model_element = model.new_element(model_element_cls)
            model_element.id_ = cd_species_template.get("id")
            model_element.name = cls._prepare_name(
                cd_species_template.get("name")
            )
            for (
                cd_modification_residue
            ) in cls._get_modification_residues_from_cd_species_template(
                cd_species_template
            ):
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
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_cd_element=cd_species_template,
                        super_model_element=model_element,
                    )
                )
            model_element = momapy.builder.object_from_builder(model_element)
            cd_id_to_model_element[cd_species_template.get("id")] = (
                model_element
            )
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
        with_annotations,
        with_notes,
        super_cd_element,
        super_model_element,
    ):
        if model is not None:
            model_element = model.new_element(
                momapy.celldesigner.core.ModificationResidue
            )
            # Defaults ids for modification residues are simple in CellDesigner (e.g.,
            # "rs1") and might be shared between residues of different species.
            # However we want a unique id, so we build it using the id of the
            # species as well.
            cd_modification_residue_id = f"{super_cd_element.get('id')}_{cd_modification_residue.get('id')}"
            model_element.id_ = cd_modification_residue_id
            model_element.name = cls._prepare_name(
                cd_modification_residue.get("name")
            )
            model_element = momapy.builder.object_from_builder(model_element)
            super_model_element.modification_residues.add(model_element)
            # exceptionally we take the model element's id and not the cd element's
            # id for the reasons explained above
            cd_id_to_model_element[cd_modification_residue_id] = model_element
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
            name = cls._prepare_name(cd_species.get("name"))
            cd_species_homodimer = cls._get_homodimer_from_cd_species(
                cd_species
            )
            if cd_species_homodimer is not None:
                homomultimer = int(cd_species_homodimer)
            else:
                homomultimer = 1
            cd_species_hypothetical = cls._get_hypothetical_from_cd_species(
                cd_species
            )
            if cd_species_hypothetical is not None:
                hypothetical = cd_species_hypothetical.text == "true"
            else:
                hypothetical = False
            cd_species_activity = cls._get_activity_from_cd_species_alias(
                cd_species_alias
            )
            if cd_species_activity is not None:
                active = cd_species_activity.text == "active"
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
                cd_species_alias_fill_color = (
                    cd_species_alias.usualView.paint.get("color")
                )
                cd_species_alias_fill_color = (
                    cd_species_alias_fill_color[2:]
                    + cd_species_alias_fill_color[:2]
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
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_cd_element=cd_species_alias,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
            for (
                cd_species_structural_state
            ) in cls._get_species_structural_states_from_cd_species(
                cd_species
            ):
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
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_cd_element=cd_species_alias,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                    )
                )
            if model is not None:
                model_element = momapy.builder.object_from_builder(
                    model_element
                )
                if super_model_element is None:  # species case
                    model.species.add(model_element)
                else:  # included species case
                    super_model_element.subunits.add(model_element)
                cd_id_to_model_element[cd_species.get("id")] = model_element
            if layout is not None:
                layout_element = momapy.builder.object_from_builder(
                    layout_element
                )
                if super_layout_element is None:  # species case
                    layout.layout_elements.append(layout_element)
                else:  # included species case
                    super_layout_element.layout_elements.append(layout_element)
                cd_id_to_model_element[cd_species_alias.get("id")] = (
                    layout_element
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
        with_annotations,
        with_notes,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if model is not None or layout is not None:
            cd_species_modification_state = cd_species_modification.get(
                "state"
            )
            if cd_species_modification_state == "empty":
                modification_state = None
            else:
                modification_state = (
                    momapy.celldesigner.core.ModificationState[
                        cd_species_modification_state.upper()
                    ]
                )
            cd_species_template = cls._get_template_from_cd_species_alias(
                super_cd_element,
                cd_id_to_cd_element,
            )
            cd_modification_residue_id = f"{cd_species_template.get('id')}_{cd_species_modification.get('residue')}"
            if model is not None:
                model_element = model.new_element(
                    momapy.celldesigner.core.Modification
                )
                modification_residue_model_element = cd_id_to_model_element[
                    cd_modification_residue_id
                ]
                model_element.residue = modification_residue_model_element
                model_element.state = modification_state
                model_element = momapy.builder.object_from_builder(
                    model_element
                )
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
                ]
                angle = float(cd_modification_residue.get("angle"))
                point = momapy.geometry.Point(
                    super_layout_element.width * math.cos(angle),
                    super_layout_element.height * math.sin(angle),
                )
                angle = math.atan2(point.y, point.x)
                layout_element.position = super_layout_element.angle(
                    angle, unit="radians"
                )
                text = (
                    modification_state.value
                    if modification_state is not None
                    else ""
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
                cd_modification_residue_name = cd_modification_residue.get(
                    "name"
                )
                if cd_modification_residue_name is not None:
                    residue_text_layout = layout.new_element(
                        momapy.core.TextLayout
                    )
                    residue_text_layout.text = cd_modification_residue_name
                    residue_text_layout.font_size = (
                        cls._DEFAULT_MODIFICATION_FONT_SIZE
                    )
                    residue_text_layout.font_family = cls._DEFAULT_FONT_FAMILY
                    residue_text_layout.fill = cls._DEFAULT_FONT_FILL
                    residue_text_layout.stroke = momapy.drawing.NoneValue
                    segment = momapy.geometry.Segment(
                        layout_element.center(), super_layout_element.center()
                    )
                    fraction = (
                        layout_element.height
                        + cls._DEFAULT_MODIFICATION_FONT_SIZE
                    ) / segment.length()
                    residue_text_layout.position = (
                        segment.get_position_at_fraction(fraction)
                    )
                    residue_text_layout = momapy.builder.object_from_builder(
                        residue_text_layout
                    )
                    layout_element.layout_elements.append(residue_text_layout)
                layout_element = momapy.builder.object_from_builder(
                    layout_element
                )
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
        with_annotations,
        with_notes,
        super_cd_element,
        super_model_element,
        super_layout_element,
    ):
        if model is not None:
            model_element = model.new_element(
                momapy.celldesigner.core.StructuralState
            )
            model_element.value = cd_species_structural_state.get(
                "structuralState"
            )
            super_model_element.structural_states.add(model_element)
        else:
            model_element = None
        if layout is not None:  # TODO
            pass
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
        with_annotations,
        with_notes,
    ):
        if model is not None or layout is not None:
            key = cls._get_key_from_cd_reaction(cd_reaction)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if model is not None:
                model_element = model.new_element(model_element_cls)
                model_element.id_ = cd_reaction.get("id")
                model_element.reversible = (
                    cd_reaction.get("reversible") == "true"
                )
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(layout_element_cls)
                layout_element.id_ = cd_reaction.get("id")
                layout_element.reversible = cd_reaction.get("reversible")
                if not layout_element.reversible:
                    layout_element.start_shorten = 0.0
                cd_base_reactants = cls._get_base_reactants_from_cd_reaction(
                    cd_reaction
                )
                cd_base_products = cls._get_base_products_from_cd_reaction(
                    cd_reaction
                )
                if len(cd_base_reactants) == 1 and len(cd_base_products) == 1:
                    # Case where we have a linear reaction (one base reactant
                    # and one base product). The frame for the edit points
                    # is the orthonormal frame whose x axis goes from the
                    # base reactant's center or link anchor to the base product's
                    # center or link anchor and whose y axis is orthogonal to
                    # to the x axis, going downwards
                    cd_base_reactant = cd_base_reactants[0]
                    cd_base_product = cd_base_products[0]
                    reactant_layout_element = cd_id_to_layout_element[
                        cd_base_reactant.get("alias")
                    ]
                    product_layout_element = cd_id_to_layout_element[
                        cd_base_product.get("alias")
                    ]
                    reactant_anchor_name = cls._get_anchor_name_for_frame_from_cd_base_participant(
                        cd_base_reactant
                    )
                    product_anchor_name = cls._get_anchor_name_for_frame_from_cd_base_participant(
                        cd_base_product
                    )
                    origin = reactant_layout_element.anchor_point(
                        reactant_anchor_name
                    )
                    unit_x = product_layout_element.anchor_point(
                        product_anchor_name
                    )
                    unit_y = unit_x.transformed(
                        momapy.geometry.Rotation(math.radians(90), origin)
                    )
                    transformation = (
                        momapy.geometry.get_transformation_for_frame(
                            origin, unit_x, unit_y
                        )
                    )
                    intermediate_points = []
                    cd_edit_points = cls._get_edit_points_from_cd_reaction(
                        cd_reaction
                    )
                    if cd_edit_points is None:
                        edit_points = []
                    else:
                        edit_points = cls._get_points_from_cd_edit_points(
                            cd_edit_points
                        )
                    intermediate_points = [
                        edit_point.transformed(transformation)
                        for edit_point in edit_points
                    ]
                    if reactant_anchor_name == "center":
                        if intermediate_points:
                            reference_point = intermediate_points[0]

                        else:
                            reference_point = (
                                product_layout_element.anchor_point(
                                    product_anchor_name
                                )
                            )
                        start_point = reactant_layout_element.border(
                            reference_point
                        )
                    else:
                        start_point = reactant_layout_element.anchor_point(
                            reactant_anchor_name
                        )
                    if product_anchor_name == "center":
                        if intermediate_points:
                            reference_point = intermediate_points[-1]
                        else:
                            reference_point = (
                                reactant_layout_element.anchor_point(
                                    reactant_anchor_name
                                )
                            )
                        end_point = product_layout_element.border(
                            reference_point
                        )
                    else:
                        end_point = product_layout_element.anchor_point(
                            product_anchor_name
                        )
                    layout_element.reaction_node_segment = int(
                        cls._get_rectangle_index_from_cd_reaction(cd_reaction)
                    )
                    # no consumption nor production layouts since they are
                    # represented by the reaction layout
                    make_base_reactant_layouts = False
                    make_base_product_layouts = False
                elif len(cd_base_reactants) > 1 and len(cd_base_products) == 1:
                    # Case where we have a tshape reaction with two base reactants
                    # and one base product. The frame for the edit points are the
                    # axes going from the center of the first base reactant to
                    # the center of the second base reactant (x axis), and from the
                    # center of the first base reactant to the center of the base
                    # product (y axis).
                    cd_base_reactant_0 = cd_base_reactants[0]
                    cd_base_reactant_1 = cd_base_reactants[1]
                    cd_base_product = cd_base_products[0]
                    reactant_layout_element_0 = cd_id_to_layout_element[
                        cd_base_reactant_0.alias
                    ]
                    reactant_layout_element_1 = cd_id_to_layout_element[
                        cd_base_reactant_1.alias
                    ]
                    product_layout_element = cd_id_to_layout_element[
                        cd_base_product.alias
                    ]
                    product_anchor_name = cls._get_anchor_name_for_frame_from_cd_base_participant(
                        cd_base_product
                    )
                    origin = reactant_layout_element_0.center()
                    unit_x = reactant_layout_element_1.center()
                    unit_y = product_layout_element.center()
                    transformation = (
                        momapy.geometry.get_transformation_for_frame(
                            origin, unit_x, unit_y
                        )
                    )
                    cd_edit_points = (
                        cd_element.annotation.extension.edit_points
                    )
                    edit_points = [
                        momapy.geometry.Point(
                            *[
                                float(coord)
                                for coord in cd_edit_point.split(",")
                            ]
                        )
                        for cd_edit_point in cd_edit_points.value
                    ]
                    start_point = edit_points[-1].transformed(transformation)
                    # The frame for the intermediate edit points becomes
                    # the orthonormal frame whose x axis goes from the
                    # start point of the reaction computed above to the base
                    # product's center or link anchor and whose y axis is
                    # orthogonal to the x axis, going downwards
                    origin = start_point
                    unit_x = product_layout_element.anchor_point(
                        product_anchor_name
                    )
                    unit_y = unit_x.transformed(
                        momapy.geometry.Rotation(math.radians(90), origin)
                    )
                    transformation = (
                        momapy.geometry.get_transformation_for_frame(
                            origin, unit_x, unit_y
                        )
                    )
                    intermediate_points = []
                    # the index for the intermediate points of the reaction
                    # starts after those for the two base reactants
                    start_index = int(cd_edit_points.num0) + int(
                        cd_edit_points.num1
                    )
                    for edit_point in edit_points[start_index:-1]:
                        intermediate_point = edit_point.transformed(
                            transformation
                        )
                        intermediate_points.append(intermediate_point)
                    if cd_base_product.link_anchor is not None:
                        end_point = product_layout_element.anchor_point(
                            cls._get_anchor_name_for_frame_from_cd_base_participant(
                                cd_base_product
                            )
                        )
                    else:
                        if intermediate_points:
                            reference_point = intermediate_points[-1]
                        else:
                            reference_point = start_point
                        end_point = product_layout_element.border(
                            reference_point
                        )
                    layout_element.reaction_node_segment = int(
                        cd_edit_points.t_shape_index
                    )
                    make_base_reactant_layouts = True
                    make_base_product_layouts = False
                elif len(cd_base_reactants) == 1 and len(cd_base_products) > 1:
                    # Case where we have a tshape reaction with one base reactant
                    # and two base products. The frame for the edit points are the
                    # axes going from the center of the first base product to
                    # the center of the second base product (x axis), and from the
                    # center of the first base product to the center of the base
                    # reactant (y axis).
                    cd_base_product_0 = cd_base_products[0]
                    cd_base_product_1 = cd_base_products[1]
                    cd_base_reactant = cd_base_reactants[0]
                    product_layout_element_0 = cd_id_to_layout_element[
                        cd_base_product_0.alias
                    ]
                    product_layout_element_1 = cd_id_to_layout_element[
                        cd_base_product_1.alias
                    ]
                    reactant_layout_element = cd_id_to_layout_element[
                        cd_base_reactant.alias
                    ]
                    reactant_anchor_name = cls._get_anchor_name_for_frame_from_cd_base_participant(
                        cd_base_reactant
                    )
                    origin = reactant_layout_element.center()
                    unit_x = product_layout_element_0.center()
                    unit_y = product_layout_element_1.center()
                    transformation = (
                        momapy.geometry.get_transformation_for_frame(
                            origin, unit_x, unit_y
                        )
                    )
                    cd_edit_points = (
                        cd_element.annotation.extension.edit_points
                    )
                    edit_points = [
                        momapy.geometry.Point(
                            *[
                                float(coord)
                                for coord in cd_edit_point.split(",")
                            ]
                        )
                        for cd_edit_point in cd_edit_points.value
                    ]
                    end_point = edit_points[-1].transformed(transformation)
                    # The frame for the intermediate edit points becomes
                    # the orthonormal frame whose x axis goes from the
                    # start point of the reaction computed above to the base
                    # product's center or link anchor and whose y axis is
                    # orthogonal to the x axis, going downwards
                    origin = end_point
                    unit_x = reactant_layout_element.anchor_point(
                        reactant_anchor_name
                    )
                    unit_y = unit_x.transformed(
                        momapy.geometry.Rotation(math.radians(90), origin)
                    )
                    transformation = (
                        momapy.geometry.get_transformation_for_frame(
                            origin, unit_x, unit_y
                        )
                    )
                    intermediate_points = []
                    # the index for the intermediate points of the reaction
                    # starts at 0 and ends at before those for the two base products
                    end_index = int(cd_edit_points.num0)
                    edit_points = list(reversed(edit_points[:end_index]))
                    for edit_point in edit_points:
                        intermediate_point = edit_point.transformed(
                            transformation
                        )
                        intermediate_points.append(intermediate_point)
                    if cd_base_reactant.link_anchor is not None:
                        start_point = reactant_layout_element.anchor_point(
                            cls._get_anchor_name_for_frame_from_cd_base_participant(
                                cd_base_reactant
                            )
                        )
                    else:
                        if intermediate_points:
                            reference_point = intermediate_points[0]
                        else:
                            reference_point = end_point
                        start_point = reactant_layout_element.border(
                            reference_point
                        )
                    layout_element.reaction_node_segment = len(
                        intermediate_points
                    ) - int(cd_edit_points.t_shape_index)
                    make_base_reactant_layouts = False
                    make_base_product_layouts = True
                points = [start_point] + intermediate_points + [end_point]
                for i, point in enumerate(points[1:]):
                    previous_point = points[i]
                    segment = momapy.geometry.Segment(previous_point, point)
                    layout_element.segments.append(segment)
            else:
                layout_element = None
                make_base_reactant_layouts = False
                make_base_product_layouts = False
        else:
            make_base_reactant_layouts = False
            make_base_product_layouts = False
            layout_element = None
            if cd_element.annotation.extension.base_reactants is not None:
                for (
                    cd_base_reactant
                ) in (
                    cd_element.annotation.extension.base_reactants.base_reactant
                ):
                    reactant_model_element, reactant_layout_element = (
                        cls._make_and_add_reactant_from_cd_base_reactant(
                            model=model,
                            layout=layout,
                            cd_element=cd_base_reactant,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            cd_id_to_annotations=cd_id_to_annotations,
                            cd_id_to_notes=cd_id_to_notes,
                            super_model_element=model_element,
                            super_layout_element=layout_element,
                            super_cd_element=cd_element,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                            with_layout=make_base_reactant_layouts,
                        )
                    )
            if (
                cd_element.annotation.extension.list_of_reactant_links
                is not None
            ):
                for (
                    cd_reactant_link
                ) in (
                    cd_element.annotation.extension.list_of_reactant_links.reactant_link
                ):
                    reactant_model_element, reactant_layout_element = (
                        cls._make_and_add_reactant_from_cd_reactant_link(
                            model=model,
                            layout=layout,
                            cd_element=cd_reactant_link,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            cd_id_to_annotations=cd_id_to_annotations,
                            cd_id_to_notes=cd_id_to_notes,
                            super_model_element=model_element,
                            super_layout_element=layout_element,
                            super_cd_element=cd_element,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                        )
                    )
            if cd_element.annotation.extension.base_products is not None:
                for (
                    cd_base_product
                ) in (
                    cd_element.annotation.extension.base_products.base_product
                ):
                    product_model_element, product_layout_element = (
                        cls._make_and_add_product_from_cd_base_product(
                            model=model,
                            layout=layout,
                            cd_element=cd_base_product,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            cd_id_to_annotations=cd_id_to_annotations,
                            cd_id_to_notes=cd_id_to_notes,
                            super_model_element=model_element,
                            super_layout_element=layout_element,
                            super_cd_element=cd_element,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                            with_layout=make_base_product_layouts,
                        )
                    )
            if (
                cd_element.annotation.extension.list_of_product_links
                is not None
            ):
                for (
                    cd_product_link
                ) in (
                    cd_element.annotation.extension.list_of_product_links.product_link
                ):
                    product_model_element, product_layout_element = (
                        cls._make_and_add_product_from_cd_product_link(
                            model=model,
                            layout=layout,
                            cd_element=cd_product_link,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            cd_id_to_annotations=cd_id_to_annotations,
                            cd_id_to_notes=cd_id_to_notes,
                            super_model_element=model_element,
                            super_layout_element=layout_element,
                            super_cd_element=cd_element,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                        )
                    )
            cd_boolean_modifications = []
            cd_normal_modifications = []
            cd_boolean_input_ids = []
            if (
                cd_element.annotation.extension.list_of_modification
                is not None
            ):
                for (
                    cd_modification
                ) in (
                    cd_element.annotation.extension.list_of_modification.modification
                ):
                    # Boolean gates are in the list of modifications; their inputs
                    # are also in the list of modifications; a Boolean gate is
                    # always the source of a catalysis.
                    # We first go through the list of modifications to get the
                    # Boolean gates; we then remove their inputs from the list of
                    # modifications, and transform the Boolean modifications as well
                    # as the normal ones.
                    if cd_modification.type_value in [
                        momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_AND,
                        momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_OR,
                        momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_NOT,
                        momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_UNKNOWN,
                    ]:
                        cd_boolean_modifications.append(cd_modification)
                        cd_boolean_input_ids += (
                            cd_modification.modifiers.split(",")
                        )
                    else:
                        cd_normal_modifications.append(cd_modification)
                for cd_modification in cd_boolean_modifications:
                    modifier_model_element, modifier_layout_element = (
                        cls._make_and_add_elements_from_cd(
                            model=model,
                            layout=layout,
                            cd_element=cd_modification,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            cd_id_to_annotations=cd_id_to_annotations,
                            cd_id_to_notes=cd_id_to_notes,
                            super_model_element=model_element,
                            super_layout_element=layout_element,
                            super_cd_element=cd_element,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                        )
                    )
                for cd_modification in cd_normal_modifications:
                    if cd_modification.modifiers not in cd_boolean_input_ids:
                        modifier_model_element, modifier_layout_element = (
                            cls._make_and_add_elements_from_cd(
                                model=model,
                                layout=layout,
                                cd_element=cd_modification,
                                cd_id_to_model_element=cd_id_to_model_element,
                                cd_id_to_layout_element=cd_id_to_layout_element,
                                cd_id_to_cd_element=cd_id_to_cd_element,
                                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                                cd_id_to_annotations=cd_id_to_annotations,
                                cd_id_to_notes=cd_id_to_notes,
                                super_model_element=model_element,
                                super_layout_element=layout_element,
                                super_cd_element=cd_element,
                                with_annotations=with_annotations,
                                with_notes=with_notes,
                            )
                        )
            model_element = momapy.builder.object_from_builder(model_element)
            layout_element = momapy.builder.object_from_builder(layout_element)
            if cd_element.annotation is not None:
                if cd_element.annotation.rdf is not None:
                    annotations = cls._make_annotations_from_cd_annotation_rdf(
                        cd_element.annotation.rdf
                    )
                    map_element_to_annotations[model_element].update(
                        annotations
                    )
        return model_element, layout_element

    @classmethod
    def _make_model_no_subelements_from_cd_model(
        cls,
        cd_element,
    ):
        layout = momapy.celldesigner.core.CellDesignerModelBuilder()
        return layout

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
    def _set_layout_size_and_position_from_cd_model(cls, cd_model, layout):
        layout.width = float(cls._get_width_from_cd_model(cd_model))
        layout.height = float(cls._get_height_from_cd_model(cd_model))
        layout.position = momapy.geometry.Point(
            layout.width / 2, layout.height / 2
        )

    @classmethod
    def _make_and_add_reactant_from_cd_base_reactant(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element,
        with_annotations=True,
        with_notes=True,
    ):
        if model is not None:
            model_element = model.new_element(
                momapy.celldesigner.core.Reactant
            )
            cd_species_id = cd_element.species
            if super_cd_element.list_of_reactants is not None:
                for (
                    cd_reactant
                ) in super_cd_element.list_of_reactants.species_reference:
                    if cd_reactant.species == cd_species_id:
                        model_element.id_ = cd_reactant.metaid
                        model_element.stoichiometry = cd_reactant.stoichiometry
                        break
            species_model_element = cd_id_to_model_element[cd_element.alias]
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
            cd_edit_points = super_cd_element.annotation.extension.edit_points
            cd_num_0 = cd_edit_points.num0
            cd_num_1 = cd_edit_points.num1
            for n_cd_base_reactant, cd_base_reactant in enumerate(
                super_cd_element.annotation.extension.base_reactants.base_reactant
            ):
                if cd_base_reactant == cd_element:
                    break
            if n_cd_base_reactant == 0:
                start_index = n_cd_base_reactant
                stop_index = cd_num_0
            elif n_cd_base_reactant == 1:
                start_index = cd_num_0
                stop_index = cd_num_0 + cd_num_1
            reactant_layout_element = cd_id_to_layout_element[cd_element.alias]
            reactant_anchor_name = (
                cls._get_anchor_name_for_frame_from_cd_base_participant(
                    cd_element
                )
            )
            origin = super_layout_element.points()[0]
            unit_x = reactant_layout_element.anchor_point(reactant_anchor_name)
            unit_y = unit_x.transformed(
                momapy.geometry.Rotation(math.radians(90), origin)
            )
            transformation = momapy.geometry.get_transformation_for_frame(
                origin, unit_x, unit_y
            )
            intermediate_points = []
            edit_points = [
                momapy.geometry.Point(
                    *[float(coord) for coord in cd_edit_point.split(",")]
                )
                for cd_edit_point in cd_edit_points.value
            ]
            for edit_point in edit_points[start_index:stop_index]:
                intermediate_point = edit_point.transformed(transformation)
                intermediate_points.append(intermediate_point)
            intermediate_points.reverse()
            if reactant_anchor_name == "center":
                if intermediate_points:
                    reference_point = intermediate_points[0]
                else:
                    reference_point = super_layout_element.start_point()

                start_point = reactant_layout_element.border(reference_point)
            else:
                start_point = reactant_layout_element.anchor_point(
                    reactant_anchor_name
                )
            if intermediate_points:
                reference_point = intermediate_points[-1]
            else:
                reference_point = start_point
            end_point = super_layout_element.start_arrowhead_border(
                reference_point
            )
            points = [start_point] + intermediate_points + [end_point]
            for i, point in enumerate(points[1:]):
                previous_point = points[i]
                segment = momapy.geometry.Segment(previous_point, point)
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
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element,
        with_annotations=True,
        with_notes=True,
    ):
        if model is not None:
            model_element = model.new_element(
                momapy.celldesigner.core.Reactant
            )
            cd_species_id = cd_element.reactant
            if super_cd_element.list_of_reactants is not None:
                for (
                    cd_reactant
                ) in super_cd_element.list_of_reactants.species_reference:
                    if cd_reactant.species == cd_species_id:
                        model_element.id_ = cd_reactant.metaid
                        model_element.stoichiometry = cd_reactant.stoichiometry
                        break
            species_model_element = cd_id_to_model_element[cd_element.alias]
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
            reactant_layout_element = cd_id_to_layout_element[cd_element.alias]
            reactant_anchor_name = (
                cls._get_anchor_name_for_frame_from_cd_base_participant(
                    cd_element
                )
            )
            origin = reactant_layout_element.center()
            unit_x = super_layout_element.left_connector_tip()
            unit_y = unit_x.transformed(
                momapy.geometry.Rotation(math.radians(90), origin)
            )
            transformation = momapy.geometry.get_transformation_for_frame(
                origin, unit_x, unit_y
            )
            intermediate_points = []
            cd_edit_points = cd_element.edit_points
            if cd_edit_points is not None:
                edit_points = [
                    momapy.geometry.Point(
                        *[float(coord) for coord in cd_edit_point.split(",")]
                    )
                    for cd_edit_point in cd_edit_points.value
                ]
                for edit_point in edit_points:
                    intermediate_point = edit_point.transformed(transformation)
                    intermediate_points.append(intermediate_point)
            end_point = unit_x
            if reactant_anchor_name == "center":
                if intermediate_points:
                    reference_point = intermediate_points[0]
                else:
                    reference_point = end_point
                start_point = reactant_layout_element.border(reference_point)
            else:
                start_point = reactant_layout_element.anchor_point(
                    reactant_anchor_name
                )
            points = [start_point] + intermediate_points + [end_point]
            for i, point in enumerate(points[1:]):
                previous_point = points[i]
                segment = momapy.geometry.Segment(previous_point, point)
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
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element,
        with_annotations=True,
        with_notes=True,
    ):
        if model is not None:
            model_element = model.new_element(
                momapy.celldesigner.core.Reactant
            )
            cd_species_id = cd_element.species
            if super_cd_element.list_of_products is not None:
                for (
                    cd_product
                ) in super_cd_element.list_of_products.species_reference:
                    if cd_product.species == cd_species_id:
                        model_element.id_ = cd_product.metaid
                        model_element.stoichiometry = cd_product.stoichiometry
                        break
            species_model_element = cd_id_to_model_element[cd_element.alias]
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
            cd_edit_points = super_cd_element.annotation.extension.edit_points
            cd_num_0 = cd_edit_points.num0
            cd_num_1 = cd_edit_points.num1
            cd_num_2 = cd_edit_points.num2
            for n_cd_base_product, cd_base_product in enumerate(
                super_cd_element.annotation.extension.base_products.base_product
            ):
                if cd_base_product == cd_element:
                    break
            if n_cd_base_product == 0:
                start_index = cd_num_0
                stop_index = cd_num_0 + cd_num_1
            elif n_cd_base_product == 1:
                start_index = cd_num_0 + cd_num_1
                stop_index = cd_num_0 + cd_num_1 + cd_num_2
            product_layout_element = cd_id_to_layout_element[cd_element.alias]
            product_anchor_name = (
                cls._get_anchor_name_for_frame_from_cd_base_participant(
                    cd_element
                )
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
            edit_points = [
                momapy.geometry.Point(
                    *[float(coord) for coord in cd_edit_point.split(",")]
                )
                for cd_edit_point in cd_edit_points.value
            ]
            for edit_point in edit_points[start_index:stop_index]:
                intermediate_point = edit_point.transformed(transformation)
                intermediate_points.append(intermediate_point)
            # intermediate_points.reverse()
            if product_anchor_name == "center":
                if intermediate_points:
                    reference_point = intermediate_points[-1]
                else:
                    reference_point = super_layout_element.end_point()
                end_point = product_layout_element.border(reference_point)
            else:
                end_point = product_layout_element.anchor_point(
                    product_anchor_name
                )
            if intermediate_points:
                reference_point = intermediate_points[0]
            else:
                reference_point = end_point
            start_point = super_layout_element.end_arrowhead_border(
                reference_point
            )
            points = [start_point] + intermediate_points + [end_point]
            for i, point in enumerate(points[1:]):
                previous_point = points[i]
                segment = momapy.geometry.Segment(previous_point, point)
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
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element,
        with_annotations=True,
        with_notes=True,
    ):
        if model is not None:
            model_element = model.new_element(
                momapy.celldesigner.core.Reactant
            )
            cd_species_id = cd_element.product
            if super_cd_element.list_of_products is not None:
                for (
                    cd_product
                ) in super_cd_element.list_of_products.species_reference:
                    if cd_product.species == cd_species_id:
                        model_element.id_ = cd_product.metaid
                        model_element.stoichiometry = cd_product.stoichiometry
                        break
            species_model_element = cd_id_to_model_element[cd_element.alias]
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
            product_layout_element = cd_id_to_layout_element[cd_element.alias]
            product_anchor_name = (
                cls._get_anchor_name_for_frame_from_cd_base_participant(
                    cd_element
                )
            )
            origin = super_layout_element.right_connector_tip()
            unit_x = product_layout_element.center()
            # unit_x = product_layout_element.anchor_point(product_anchor_name)
            unit_y = unit_x.transformed(
                momapy.geometry.Rotation(math.radians(90), origin)
            )
            transformation = momapy.geometry.get_transformation_for_frame(
                origin, unit_x, unit_y
            )
            intermediate_points = []
            cd_edit_points = cd_element.edit_points
            if cd_edit_points is not None:
                edit_points = [
                    momapy.geometry.Point(
                        *[float(coord) for coord in cd_edit_point.split(",")]
                    )
                    for cd_edit_point in cd_edit_points.value
                ]
                for edit_point in edit_points:
                    intermediate_point = edit_point.transformed(transformation)
                    intermediate_points.append(intermediate_point)
            intermediate_points.reverse()
            start_point = origin
            if product_anchor_name == "center":
                if intermediate_points:
                    reference_point = intermediate_points[-1]
                else:
                    reference_point = start_point
                end_point = product_layout_element.border(reference_point)
            else:
                end_point = product_layout_element.anchor_point(
                    product_anchor_name
                )
            points = [start_point] + intermediate_points + [end_point]
            for i, point in enumerate(points[1:]):
                previous_point = points[i]
                segment = momapy.geometry.Segment(previous_point, point)
                layout_element.segments.append(segment)
            layout_element = momapy.builder.object_from_builder(layout_element)
            super_layout_element.layout_elements.append(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_catalyzer_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._generic_make_and_add_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Catalyzer,
                layout_element_cls=momapy.celldesigner.core.CatalysisLayout,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_catalyzer_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._generic_make_and_add_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownCatalyzer,
                layout_element_cls=momapy.celldesigner.core.UnknownCatalysisLayout,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_inhibitor_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._generic_make_and_add_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Inhibitor,
                layout_element_cls=momapy.celldesigner.core.InhibitionLayout,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_inhibitor_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._generic_make_and_add_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownInhibitor,
                layout_element_cls=momapy.celldesigner.core.UnknownInhibitionLayout,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_physical_stimulator_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._generic_make_and_add_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.PhysicalStimulator,
                layout_element_cls=momapy.celldesigner.core.PhysicalStimulationLayout,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_modulator_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._generic_make_and_add_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Modulator,
                layout_element_cls=momapy.celldesigner.core.ModulationLayout,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_trigger_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._generic_make_and_add_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Trigger,
                layout_element_cls=momapy.celldesigner.core.TriggeringLayout,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        return model_element, layout_element

    @classmethod
    def _make_and_add_and_gate_and_catalyzer_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Catalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_unknown_catalyzer_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownCatalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_inhibitor_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Inhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_unknown_inhibitor_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownInhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_physical_stimulator_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.PhysicalStimulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_modulator_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Modulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_trigger_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Trigger,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_catalyzer_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Catalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_unknown_catalyzer_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownCatalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_inhibitor_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Inhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_unknown_inhibitor_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownInhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_physical_stimulator_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.PhysicalStimulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_modulator_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Modulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_trigger_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Trigger,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_catalyzer_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Catalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_unknown_catalyzer_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownCatalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_inhibitor_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Inhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_unknown_inhibitor_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownInhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_physical_stimulator_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.PhysicalStimulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_modulator_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Modulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_trigger_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Trigger,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_catalyzer_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Catalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_unknown_catalyzer_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownCatalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_inhibitor_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Inhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_unknown_inhibitor_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownInhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_physical_stimulator_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.PhysicalStimulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_modulator_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Modulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_trigger_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Trigger,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_catalysis_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_catalysis_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_unknown_catalysis_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_catalysis_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_inhibition_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_inhibition_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_unknown_inhibition_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_inhibition_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_physical_stimulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_physical_stimulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_modulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_triggering_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_triggering_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_positive_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_positive_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_unknown_positive_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_positive_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_negative_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_negative_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_unknown_negative_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_negative_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_unknown_physical_stimulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_physical_stimulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_unknown_modulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_unknown_triggering_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_triggering_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_catalysis_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_catalysis_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_unknown_catalysis_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_catalysis_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_inhibition_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_inhibition_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_unknown_inhibition_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_inhibition_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_physical_stimulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_physical_stimulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_modulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_triggering_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_triggering_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_positive_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_positive_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_unknown_positive_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_positive_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_negative_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_negative_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_unknown_negative_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_negative_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_unknown_physical_stimulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_physical_stimulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_unknown_modulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_unknown_triggering_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_triggering_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_catalysis_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_catalysis_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_unknown_catalysis_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_catalysis_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_inhibition_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_inhibition_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_unknown_inhibition_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_inhibition_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_physical_stimulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_physical_stimulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_modulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_triggering_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_triggering_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_positive_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_positive_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_unknown_positive_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_positive_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_negative_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_negative_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_unknown_negative_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_negative_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_unknown_physical_stimulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_physical_stimulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_unknown_modulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_unknown_triggering_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_triggering_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_catalysis_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_catalysis_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_unknown_catalysis_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_catalysis_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_inhibition_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_inhibition_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_unknown_inhibition_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_inhibition_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_physical_stimulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_physical_stimulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_modulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_triggering_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_triggering_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_positive_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_positive_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_unknown_positive_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_positive_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_negative_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_negative_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_unknown_negative_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_negative_influence_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_unknown_physical_stimulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_physical_stimulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_unknown_modulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_unknown_triggering_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        # first we select the gate member corresponding to the boolean logic gate
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        # the gate can then be transformed the same way as for modifications,
        # since it has the aliases attribute
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_unknown_triggering_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_from_cd_modification_or_gate_member(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_boolean_logic_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.AndGate,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.boolean_logic_gates.add(model_element)
        # we use the id of the model element since the cd element does not have
        # one; this mapping is necessary when building the modification the
        # Boolean gate is the source of
        cd_id_to_model_element[model_element.id_] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_or_gate_from_cd_modification_or_gate_member(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_boolean_logic_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.OrGate,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.boolean_logic_gates.add(model_element)
        # we use the id of the model element since the cd element does not have
        # one; this mapping is necessary when building the modification the
        # Boolean gate is the source of
        cd_id_to_model_element[model_element.id_] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_not_gate_from_cd_modification_or_gate_member(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_boolean_logic_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.NotGate,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.boolean_logic_gates.add(model_element)
        # we use the id of the model element since the cd element does not have
        # one; this mapping is necessary when building the modification the
        # Boolean gate is the source of
        cd_id_to_model_element[model_element.id_] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_gate_from_cd_modification_or_gate_member(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_boolean_logic_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownGate,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.boolean_logic_gates.add(model_element)
        # we use the id of the model element since the cd element does not have
        # one; this mapping is necessary when building the modification the
        # Boolean gate is the source of
        cd_id_to_model_element[model_element.id_] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_state_transition_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_reaction_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.StateTransition,
            layout_element_cls=momapy.celldesigner.core.StateTransitionLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_known_transition_omitted_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_reaction_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.KnownTransitionOmitted,
            layout_element_cls=momapy.celldesigner.core.KnownTransitionOmittedLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_transition_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_reaction_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownTransition,
            layout_element_cls=momapy.celldesigner.core.UnknownTransitionLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_transcription_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_reaction_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Transcription,
            layout_element_cls=momapy.celldesigner.core.TranscriptionLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_translation_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_reaction_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Translation,
            layout_element_cls=momapy.celldesigner.core.TranslationLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_transport_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_reaction_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Transport,
            layout_element_cls=momapy.celldesigner.core.TransportLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_heterodimer_association_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_reaction_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.HeterodimerAssociation,
            layout_element_cls=momapy.celldesigner.core.HeterodimerAssociationLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_dissociation_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_reaction_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Dissociation,
            layout_element_cls=momapy.celldesigner.core.DissociationLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_truncation_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_reaction_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Truncation,
            layout_element_cls=momapy.celldesigner.core.TruncationLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_catalysis_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Catalysis,
            layout_element_cls=momapy.celldesigner.core.CatalysisLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_catalysis_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownCatalysis,
            layout_element_cls=momapy.celldesigner.core.UnknownCatalysisLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_inhibition_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Inhibition,
            layout_element_cls=momapy.celldesigner.core.InhibitionLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_inhibition_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownInhibition,
            layout_element_cls=momapy.celldesigner.core.UnknownInhibitionLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_physical_stimulation_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.PhysicalStimulation,
            layout_element_cls=momapy.celldesigner.core.PhysicalStimulationLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_modulation_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Modulation,
            layout_element_cls=momapy.celldesigner.core.ModulationLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_triggering_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Triggering,
            layout_element_cls=momapy.celldesigner.core.TriggeringLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_positive_influence_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.PositiveInfluence,
            layout_element_cls=momapy.celldesigner.core.PositiveInfluenceLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_negative_influence_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.NegativeInfluence,
            layout_element_cls=momapy.celldesigner.core.InhibitionLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_positive_influence_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownPositiveInfluence,
            layout_element_cls=momapy.celldesigner.core.UnknownPositiveInfluenceLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_negative_influence_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownNegativeInfluence,
            layout_element_cls=momapy.celldesigner.core.UnknownInhibitionLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_physical_stimulation_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownPhysicalStimulation,
            layout_element_cls=momapy.celldesigner.core.UnknownPhysicalStimulationLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_modulation_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownModulation,
            layout_element_cls=momapy.celldesigner.core.UnknownModulationLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_triggering_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = cls._make_modulation_from_cd_reaction(
            model=model,
            layout=layout,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownTriggering,
            layout_element_cls=momapy.celldesigner.core.UnknownTriggeringLayout,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            cd_id_to_annotations=cd_id_to_annotations,
            cd_id_to_notes=cd_id_to_notes,
            super_model_element=super_model_element,
            super_layout_element=super_layout_element,
            super_cd_element=super_cd_element,
            with_annotations=True,
            with_notes=True,
        )
        model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_catalysis_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Catalysis,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_catalysis_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownCatalysis,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_inhibition_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Inhibition,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_inhibition_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownInhibition,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_physical_stimulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.PhysicalStimulation,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_modulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Modulation,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_triggering_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Triggering,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_positive_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.PositiveInfluence,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_positive_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownPositiveInfluence,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_negative_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.NegativeInfluence,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_negative_influence_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownNegativeInfluence,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_physical_stimulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownPhysicalStimulation,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_modulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownModulation,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_triggering_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_modulation_from_cd_reaction_with_gate_members(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownTriggering,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _generic_make_and_add_species_template_from_cd_protein(
        cls,
        model,
        layout,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._make_species_template_from_cd_species_reference(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.GenericProteinTemplate,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=None,
                super_layout_element=None,
                super_cd_element=None,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        if model is not None:
            model.species_templates.add(model_element)
            cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_species_template_from_cd_species_reference(
        cls,
        model,
        layout,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        if model is not None:
            model_element = model.new_element(model_element_cls)
            model_element.id_ = cd_element.id
            model_element.name = cls._prepare_name(cd_element.name)
            if hasattr(cd_element, "list_of_modification_residues"):
                cd_list_of_modification_residues = (
                    cd_element.list_of_modification_residues
                )
                if cd_list_of_modification_residues is not None:
                    for (
                        cd_modification_residue
                    ) in cd_list_of_modification_residues.modification_residue:
                        sub_model_element, sub_layout_element = (
                            cls._make_and_add_elements_from_cd(
                                model=model,
                                layout=layout,
                                cd_element=cd_modification_residue,
                                cd_id_to_model_element=cd_id_to_model_element,
                                cd_id_to_layout_element=cd_id_to_layout_element,
                                cd_id_to_cd_element=cd_id_to_cd_element,
                                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                                cd_id_to_annotations=cd_id_to_annotations,
                                cd_id_to_notes=cd_id_to_notes,
                                super_model_element=model_element,
                                super_layout_element=None,
                                super_cd_element=cd_element,
                                with_annotations=with_annotations,
                                with_notes=with_notes,
                            )
                        )
            model_element = momapy.builder.object_from_builder(model_element)
        else:
            model_element = None
        layout_element = None
        return model_element, layout_element

    @classmethod
    def _generic_make_and_add_species_from_cd_species_alias(
        cls,
        model,
        layout,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._generic_make_species_from_cd_species_alias(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=model_element_cls,
                layout_element_cls=layout_element_cls,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        if model is not None:
            model.species.add(model_element)
            cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        if (
            with_annotations
            and cd_element.annotation is not None
            and cd_element.annotation.rdf is not None
        ):
            annotations = cls._make_annotations_from_cd_annotation_rdf(
                cd_element.annotation.rdf
            )
            cd_id_to_annotations[cd_element.id] = annotations
        return model_element, layout_element

    @classmethod
    def _generic_make_species_from_cd_species_alias(
        cls,
        model,
        layout,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        if model is not None or layout is not None:
            cd_species = cd_id_to_cd_element[cd_element.species]
            cd_species_name = cls._prepare_name(cd_species.name)
            cd_species_identity = (
                cd_species.annotation.extension.species_identity
            )
            cd_species_state = cd_species_identity.state
        if model is not None:
            model_element = model.new_element(model_element_cls)
            model_element.id_ = cd_species.id
            model_element.name = cd_species_name
            model_element.metaid = cd_species.metaid
            if cd_species.compartment is not None:
                compartment_model_element = cd_id_to_model_element[
                    cd_species.compartment
                ]
                model_element.compartment = compartment_model_element
            cd_species_template = (
                cls._get_cd_species_template_from_cd_species_alias(
                    cd_element=cd_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                )
            )
            if cd_species_template is not None:
                species_template_model_element = cd_id_to_model_element[
                    cd_species_template.id
                ]
                model_element.template = species_template_model_element
            if cd_species_state is not None:
                if cd_species_state.homodimer is not None:
                    model_element.homomultimer = cd_species_state.homodimer
            model_element.hypothetical = (
                cd_species_identity.hypothetical is True
            )  # in cd, is True or None
            model_element.active = (
                cd_element.activity
                == momapy.celldesigner.io._celldesigner_parser.ActivityValue.ACTIVE
            )
        else:
            model_element = None
        if layout is not None:
            layout_element = layout.new_element(layout_element_cls)
            cd_x = float(cd_element.bounds.x)
            cd_y = float(cd_element.bounds.y)
            cd_w = float(cd_element.bounds.w)
            cd_h = float(cd_element.bounds.h)
            layout_element.position = momapy.geometry.Point(
                cd_x + cd_w / 2, cd_y + cd_h / 2
            )
            layout_element.width = cd_w
            layout_element.height = cd_h
            text = cd_species_name
            text_layout = momapy.core.TextLayout(
                text=text,
                font_size=cd_element.font.size,
                font_family=cls._DEFAULT_FONT_FAMILY,
                fill=cls._DEFAULT_FONT_FILL,
                stroke=momapy.drawing.NoneValue,
                position=layout_element.label_center(),
            )
            text_layout = momapy.builder.object_from_builder(text_layout)
            layout_element.label = text_layout
            layout_element.stroke_width = float(
                cd_element.usual_view.single_line.width
            )
            cd_element_fill_color = cd_element.usual_view.paint.color
            cd_element_fill_color = (
                cd_element_fill_color[2:] + cd_element_fill_color[:2]
            )
            layout_element.fill = momapy.coloring.Color.from_hexa(
                cd_element_fill_color
            )
            layout_element.active = (
                cd_element.activity
                == momapy.celldesigner.io._celldesigner_parser.ActivityValue.ACTIVE
            )
            if (
                cd_species_state is not None
                and cd_species_state.homodimer is not None
            ):
                layout_element.n = cd_species_state.homodimer
        else:
            layout_element = None
        if model is not None or layout is not None:
            if cd_species_state.list_of_modifications is not None:
                for (
                    cd_species_modification
                ) in cd_species_state.list_of_modifications.modification:
                    modification_model_element, modification_layout_element = (
                        cls._make_and_add_elements_from_cd(
                            model=model,
                            layout=layout,
                            cd_element=cd_species_modification,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            cd_id_to_annotations=cd_id_to_annotations,
                            cd_id_to_notes=cd_id_to_notes,
                            super_model_element=model_element,
                            super_layout_element=layout_element,
                            super_cd_element=cd_element,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                        )
                    )
            if cd_species_state.list_of_structural_states is not None:
                cd_species_structural_state = (
                    cd_species_state.list_of_structural_states.structural_state
                )
                (
                    structural_state_model_element,
                    structural_state_layout_element,
                ) = cls._make_and_add_elements_from_cd(
                    model=model,
                    layout=layout,
                    cd_element=cd_species_structural_state,
                    cd_id_to_model_element=cd_id_to_model_element,
                    cd_id_to_layout_element=cd_id_to_layout_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                    cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                    cd_id_to_annotations=cd_id_to_annotations,
                    cd_id_to_notes=cd_id_to_notes,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                    super_cd_element=cd_element,
                    with_annotations=with_annotations,
                    with_notes=with_notes,
                )
            if cd_complex_alias_id_to_cd_included_species_ids[cd_element.id]:
                cd_subunits = [
                    cd_id_to_cd_element[cd_subunit_id]
                    for cd_subunit_id in cd_complex_alias_id_to_cd_included_species_ids[
                        cd_element.id
                    ]
                ]
                for cd_subunit in cd_subunits:
                    subunit_model_element, subunit_layout_element = (
                        cls._make_and_add_elements_from_cd(
                            model=model,
                            layout=layout,
                            cd_element=cd_subunit,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            cd_id_to_annotations=cd_id_to_annotations,
                            cd_id_to_notes=cd_id_to_notes,
                            super_model_element=model_element,
                            super_layout_element=layout_element,
                            super_cd_element=cd_element,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                        )
                    )
        if model is not None:
            model_element = momapy.builder.object_from_builder(model_element)
        if layout is not None:
            layout_element = momapy.builder.object_from_builder(layout_element)
        return model_element, layout_element

    @classmethod
    def _generic_make_and_add_included_species_from_cd_included_species_alias(
        cls,
        model,
        layout,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._generic_make_included_species_from_cd_included_species_alias(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=model_element_cls,
                layout_element_cls=layout_element_cls,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        if model is not None:
            super_model_element.subunits.add(model_element)
            cd_id_to_model_element[cd_element.id] = model_element
        if layout is not None:
            super_layout_element.layout_elements.append(layout_element)
            cd_id_to_layout_element[cd_element.id] = layout_element
        if with_annotations:
            cd_species = cd_id_to_cd_element[cd_element.species]
            if cd_species.notes is not None:
                serializer = (
                    xsdata.formats.dataclass.serializers.XmlSerializer()
                )
                notes_string = serializer.render(cd_species.notes)
                regexp = re.compile("<ns1:RDF.*</ns1:RDF>")
                s = regexp.search(notes_string)
                config = xsdata.formats.dataclass.parsers.config.ParserConfig(
                    fail_on_unknown_properties=False
                )
                parser = xsdata.formats.dataclass.parsers.XmlParser(
                    config=config,
                    context=xsdata.formats.dataclass.context.XmlContext(),
                )
                cd_rdf = parser.from_string(
                    s.group(0), momapy.celldesigner.io._celldesigner_parser.Rdf
                )
                annotations = cls._make_annotations_from_cd_annotation_rdf(
                    cd_rdf
                )
                cd_id_to_annotations[cd_element.id] = annotations
        return model_element, layout_element

    @classmethod
    def _generic_make_included_species_from_cd_included_species_alias(
        cls,
        model,
        layout,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        if model is not None or layout is not None:
            cd_species = cd_id_to_cd_element[cd_element.species]
            cd_species_name = cls._prepare_name(cd_species.name)
            cd_species_identity = cd_species.annotation.species_identity
            cd_species_state = cd_species_identity.state
        if model is not None:
            model_element = model.new_element(model_element_cls)
            model_element.id_ = cd_species.id
            model_element.name = cd_species_name
            model_element.metaid = cd_species.metaid
            if cd_species.compartment is not None:
                compartment_model_element = cd_id_to_model_element[
                    cd_species.compartment
                ]
                model_element.compartment = compartment_model_element
            cd_species_template = (
                cls._get_cd_species_template_from_cd_species_alias(
                    cd_element=cd_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                )
            )
            if cd_species_template is not None:
                species_template_model_element = cd_id_to_model_element[
                    cd_species_template.id
                ]
                model_element.template = species_template_model_element
            if cd_species_state is not None:
                if cd_species_state.homodimer is not None:
                    model_element.homomultimer = cd_species_state.homodimer
            model_element.hypothetical = (
                cd_species_identity.hypothetical is True
            )  # in cd, is True or None
            model_element.active = (
                cd_element.activity
                == momapy.celldesigner.io._celldesigner_parser.ActivityValue.ACTIVE
            )
        else:
            model_element = None
        if layout is not None:
            layout_element = layout.new_element(layout_element_cls)
            cd_x = float(cd_element.bounds.x)
            cd_y = float(cd_element.bounds.y)
            cd_w = float(cd_element.bounds.w)
            cd_h = float(cd_element.bounds.h)
            layout_element.position = momapy.geometry.Point(
                cd_x + cd_w / 2, cd_y + cd_h / 2
            )
            layout_element.width = cd_w
            layout_element.height = cd_h
            text = cd_species_name
            text_layout = momapy.core.TextLayout(
                text=text,
                font_size=cd_element.font.size,
                font_family=cls._DEFAULT_FONT_FAMILY,
                fill=cls._DEFAULT_FONT_FILL,
                stroke=momapy.drawing.NoneValue,
                position=layout_element.label_center(),
            )
            text_layout = momapy.builder.object_from_builder(text_layout)
            layout_element.label = text_layout
            layout_element.stroke_width = float(
                cd_element.usual_view.single_line.width
            )
            cd_element_fill_color = cd_element.usual_view.paint.color
            cd_element_fill_color = (
                cd_element_fill_color[2:] + cd_element_fill_color[:2]
            )
            layout_element.fill = momapy.coloring.Color.from_hexa(
                cd_element_fill_color
            )
            layout_element.active = (
                cd_element.activity
                == momapy.celldesigner.io._celldesigner_parser.ActivityValue.ACTIVE
            )
            if (
                cd_species_state is not None
                and cd_species_state.homodimer is not None
            ):
                layout_element.n = cd_species_state.homodimer
        else:
            layout_element = None
        if model is not None or layout is not None:
            if cd_species_state.list_of_modifications is not None:
                for (
                    cd_species_modification
                ) in cd_species_state.list_of_modifications.modification:
                    modification_model_element, modification_layout_element = (
                        cls._make_and_add_elements_from_cd(
                            model=model,
                            layout=layout,
                            cd_element=cd_species_modification,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            cd_id_to_annotations=cd_id_to_annotations,
                            cd_id_to_notes=cd_id_to_notes,
                            super_model_element=model_element,
                            super_layout_element=layout_element,
                            super_cd_element=cd_element,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                        )
                    )
            if cd_species_state.list_of_structural_states is not None:
                cd_species_structural_state = (
                    cd_species_state.list_of_structural_states.structural_state
                )
                (
                    structural_state_model_element,
                    structural_state_layout_element,
                ) = cls._make_and_add_elements_from_cd(
                    model=model,
                    layout=layout,
                    cd_element=cd_species_structural_state,
                    cd_id_to_model_element=cd_id_to_model_element,
                    cd_id_to_layout_element=cd_id_to_layout_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                    cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                    cd_id_to_annotations=cd_id_to_annotations,
                    cd_id_to_notes=cd_id_to_notes,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                    super_cd_element=cd_element,
                    with_annotations=with_annotations,
                    with_notes=with_notes,
                )
            if cd_complex_alias_id_to_cd_included_species_ids[cd_element.id]:
                cd_subunits = [
                    cd_id_to_cd_element[cd_subunit_id]
                    for cd_subunit_id in cd_complex_alias_id_to_cd_included_species_ids[
                        cd_element.id
                    ]
                ]
                for cd_subunit in cd_subunits:
                    subunit_model_element, subunit_layout_element = (
                        cls._make_and_add_elements_from_cd(
                            model=model,
                            layout=layout,
                            cd_element=cd_subunit,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            cd_id_to_annotations=cd_id_to_annotations,
                            cd_id_to_notes=cd_id_to_notes,
                            super_model_element=model_element,
                            super_layout_element=layout_element,
                            super_cd_element=cd_element,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                        )
                    )
        if model is not None:
            model_element = momapy.builder.object_from_builder(model_element)
        if layout is not None:
            layout_element = momapy.builder.object_from_builder(layout_element)
        return model_element, layout_element

    @classmethod
    def _make_reaction_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element = model.new_element(model_element_cls)
        if layout is not None:
            if layout_element_cls is not None:  # to delete
                layout_element = layout.new_element(layout_element_cls)
                layout_element.id_ = cd_element.id
                layout_element.reversible = cd_element.reversible
                if not cd_element.reversible:
                    layout_element.start_shorten = 0.0
                cd_base_reactants = (
                    cd_element.annotation.extension.base_reactants.base_reactant
                )
                cd_base_products = (
                    cd_element.annotation.extension.base_products.base_product
                )
                if len(cd_base_reactants) == 1 and len(cd_base_products) == 1:
                    # Case where we have a linear reaction (one base reactant
                    # and one base product). The frame for the edit points
                    # is the orthonormal frame whose x axis goes from the
                    # base reactant's center or link anchor to the base product's
                    # center or link anchor and whose y axis is orthogonal to
                    # to the x axis, going downwards
                    cd_base_reactant = cd_base_reactants[0]
                    cd_base_product = cd_base_products[0]
                    reactant_layout_element = cd_id_to_layout_element[
                        cd_base_reactant.alias
                    ]
                    product_layout_element = cd_id_to_layout_element[
                        cd_base_product.alias
                    ]
                    reactant_anchor_name = cls._get_anchor_name_for_frame_from_cd_base_participant(
                        cd_base_reactant
                    )
                    product_anchor_name = cls._get_anchor_name_for_frame_from_cd_base_participant(
                        cd_base_product
                    )
                    origin = reactant_layout_element.anchor_point(
                        reactant_anchor_name
                    )
                    unit_x = product_layout_element.anchor_point(
                        product_anchor_name
                    )
                    unit_y = unit_x.transformed(
                        momapy.geometry.Rotation(math.radians(90), origin)
                    )
                    transformation = (
                        momapy.geometry.get_transformation_for_frame(
                            origin, unit_x, unit_y
                        )
                    )
                    intermediate_points = []
                    if cd_element.annotation.extension.edit_points is not None:
                        edit_points = [
                            momapy.geometry.Point(
                                *[
                                    float(coord)
                                    for coord in cd_edit_point.split(",")
                                ]
                            )
                            for cd_edit_point in cd_element.annotation.extension.edit_points.value
                        ]
                    else:
                        edit_points = []
                    for edit_point in edit_points:
                        intermediate_point = edit_point.transformed(
                            transformation
                        )
                        intermediate_points.append(intermediate_point)
                    if reactant_anchor_name == "center":
                        if intermediate_points:
                            reference_point = intermediate_points[0]

                        else:
                            reference_point = (
                                product_layout_element.anchor_point(
                                    product_anchor_name
                                )
                            )
                        start_point = reactant_layout_element.border(
                            reference_point
                        )
                    else:
                        start_point = reactant_layout_element.anchor_point(
                            reactant_anchor_name
                        )
                    if product_anchor_name == "center":
                        if intermediate_points:
                            reference_point = intermediate_points[-1]
                        else:
                            reference_point = (
                                reactant_layout_element.anchor_point(
                                    reactant_anchor_name
                                )
                            )
                        end_point = product_layout_element.border(
                            reference_point
                        )
                    else:
                        end_point = product_layout_element.anchor_point(
                            product_anchor_name
                        )
                    layout_element.reaction_node_segment = int(
                        cd_element.annotation.extension.connect_scheme.rectangle_index
                    )
                    # no consumption nor production layouts since they are
                    # represented by the reaction layout
                    make_base_reactant_layouts = False
                    make_base_product_layouts = False
                elif len(cd_base_reactants) > 1 and len(cd_base_products) == 1:
                    # Case where we have a tshape reaction with two base reactants
                    # and one base product. The frame for the edit points are the
                    # axes going from the center of the first base reactant to
                    # the center of the second base reactant (x axis), and from the
                    # center of the first base reactant to the center of the base
                    # product (y axis).
                    cd_base_reactant_0 = cd_base_reactants[0]
                    cd_base_reactant_1 = cd_base_reactants[1]
                    cd_base_product = cd_base_products[0]
                    reactant_layout_element_0 = cd_id_to_layout_element[
                        cd_base_reactant_0.alias
                    ]
                    reactant_layout_element_1 = cd_id_to_layout_element[
                        cd_base_reactant_1.alias
                    ]
                    product_layout_element = cd_id_to_layout_element[
                        cd_base_product.alias
                    ]
                    product_anchor_name = cls._get_anchor_name_for_frame_from_cd_base_participant(
                        cd_base_product
                    )
                    origin = reactant_layout_element_0.center()
                    unit_x = reactant_layout_element_1.center()
                    unit_y = product_layout_element.center()
                    transformation = (
                        momapy.geometry.get_transformation_for_frame(
                            origin, unit_x, unit_y
                        )
                    )
                    cd_edit_points = (
                        cd_element.annotation.extension.edit_points
                    )
                    edit_points = [
                        momapy.geometry.Point(
                            *[
                                float(coord)
                                for coord in cd_edit_point.split(",")
                            ]
                        )
                        for cd_edit_point in cd_edit_points.value
                    ]
                    start_point = edit_points[-1].transformed(transformation)
                    # The frame for the intermediate edit points becomes
                    # the orthonormal frame whose x axis goes from the
                    # start point of the reaction computed above to the base
                    # product's center or link anchor and whose y axis is
                    # orthogonal to the x axis, going downwards
                    origin = start_point
                    unit_x = product_layout_element.anchor_point(
                        product_anchor_name
                    )
                    unit_y = unit_x.transformed(
                        momapy.geometry.Rotation(math.radians(90), origin)
                    )
                    transformation = (
                        momapy.geometry.get_transformation_for_frame(
                            origin, unit_x, unit_y
                        )
                    )
                    intermediate_points = []
                    # the index for the intermediate points of the reaction
                    # starts after those for the two base reactants
                    start_index = int(cd_edit_points.num0) + int(
                        cd_edit_points.num1
                    )
                    for edit_point in edit_points[start_index:-1]:
                        intermediate_point = edit_point.transformed(
                            transformation
                        )
                        intermediate_points.append(intermediate_point)
                    if cd_base_product.link_anchor is not None:
                        end_point = product_layout_element.anchor_point(
                            cls._get_anchor_name_for_frame_from_cd_base_participant(
                                cd_base_product
                            )
                        )
                    else:
                        if intermediate_points:
                            reference_point = intermediate_points[-1]
                        else:
                            reference_point = start_point
                        end_point = product_layout_element.border(
                            reference_point
                        )
                    layout_element.reaction_node_segment = int(
                        cd_edit_points.t_shape_index
                    )
                    make_base_reactant_layouts = True
                    make_base_product_layouts = False
                elif len(cd_base_reactants) == 1 and len(cd_base_products) > 1:
                    # Case where we have a tshape reaction with one base reactant
                    # and two base products. The frame for the edit points are the
                    # axes going from the center of the first base product to
                    # the center of the second base product (x axis), and from the
                    # center of the first base product to the center of the base
                    # reactant (y axis).
                    cd_base_product_0 = cd_base_products[0]
                    cd_base_product_1 = cd_base_products[1]
                    cd_base_reactant = cd_base_reactants[0]
                    product_layout_element_0 = cd_id_to_layout_element[
                        cd_base_product_0.alias
                    ]
                    product_layout_element_1 = cd_id_to_layout_element[
                        cd_base_product_1.alias
                    ]
                    reactant_layout_element = cd_id_to_layout_element[
                        cd_base_reactant.alias
                    ]
                    reactant_anchor_name = cls._get_anchor_name_for_frame_from_cd_base_participant(
                        cd_base_reactant
                    )
                    origin = reactant_layout_element.center()
                    unit_x = product_layout_element_0.center()
                    unit_y = product_layout_element_1.center()
                    transformation = (
                        momapy.geometry.get_transformation_for_frame(
                            origin, unit_x, unit_y
                        )
                    )
                    cd_edit_points = (
                        cd_element.annotation.extension.edit_points
                    )
                    edit_points = [
                        momapy.geometry.Point(
                            *[
                                float(coord)
                                for coord in cd_edit_point.split(",")
                            ]
                        )
                        for cd_edit_point in cd_edit_points.value
                    ]
                    end_point = edit_points[-1].transformed(transformation)
                    # The frame for the intermediate edit points becomes
                    # the orthonormal frame whose x axis goes from the
                    # start point of the reaction computed above to the base
                    # product's center or link anchor and whose y axis is
                    # orthogonal to the x axis, going downwards
                    origin = end_point
                    unit_x = reactant_layout_element.anchor_point(
                        reactant_anchor_name
                    )
                    unit_y = unit_x.transformed(
                        momapy.geometry.Rotation(math.radians(90), origin)
                    )
                    transformation = (
                        momapy.geometry.get_transformation_for_frame(
                            origin, unit_x, unit_y
                        )
                    )
                    intermediate_points = []
                    # the index for the intermediate points of the reaction
                    # starts at 0 and ends at before those for the two base products
                    end_index = int(cd_edit_points.num0)
                    edit_points = list(reversed(edit_points[:end_index]))
                    for edit_point in edit_points:
                        intermediate_point = edit_point.transformed(
                            transformation
                        )
                        intermediate_points.append(intermediate_point)
                    if cd_base_reactant.link_anchor is not None:
                        start_point = reactant_layout_element.anchor_point(
                            cls._get_anchor_name_for_frame_from_cd_base_participant(
                                cd_base_reactant
                            )
                        )
                    else:
                        if intermediate_points:
                            reference_point = intermediate_points[0]
                        else:
                            reference_point = end_point
                        start_point = reactant_layout_element.border(
                            reference_point
                        )
                    layout_element.reaction_node_segment = len(
                        intermediate_points
                    ) - int(cd_edit_points.t_shape_index)
                    make_base_reactant_layouts = False
                    make_base_product_layouts = True
                points = [start_point] + intermediate_points + [end_point]
                for i, point in enumerate(points[1:]):
                    previous_point = points[i]
                    segment = momapy.geometry.Segment(previous_point, point)
                    layout_element.segments.append(segment)
            else:
                layout_element = None
                make_base_reactant_layouts = False
                make_base_product_layouts = False
        else:
            make_base_reactant_layouts = False
            make_base_product_layouts = False
            layout_element = None
        model_element.id_ = cd_element.id
        model_element.reversible = cd_element.reversible
        if cd_element.annotation.extension.base_reactants is not None:
            for (
                cd_base_reactant
            ) in cd_element.annotation.extension.base_reactants.base_reactant:
                reactant_model_element, reactant_layout_element = (
                    cls._make_and_add_reactant_from_cd_base_reactant(
                        model=model,
                        layout=layout,
                        cd_element=cd_base_reactant,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        cd_id_to_annotations=cd_id_to_annotations,
                        cd_id_to_notes=cd_id_to_notes,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                        super_cd_element=cd_element,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        with_layout=make_base_reactant_layouts,
                    )
                )
        if cd_element.annotation.extension.list_of_reactant_links is not None:
            for (
                cd_reactant_link
            ) in (
                cd_element.annotation.extension.list_of_reactant_links.reactant_link
            ):
                reactant_model_element, reactant_layout_element = (
                    cls._make_and_add_reactant_from_cd_reactant_link(
                        model=model,
                        layout=layout,
                        cd_element=cd_reactant_link,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        cd_id_to_annotations=cd_id_to_annotations,
                        cd_id_to_notes=cd_id_to_notes,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                        super_cd_element=cd_element,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
        if cd_element.annotation.extension.base_products is not None:
            for (
                cd_base_product
            ) in cd_element.annotation.extension.base_products.base_product:
                product_model_element, product_layout_element = (
                    cls._make_and_add_product_from_cd_base_product(
                        model=model,
                        layout=layout,
                        cd_element=cd_base_product,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        cd_id_to_annotations=cd_id_to_annotations,
                        cd_id_to_notes=cd_id_to_notes,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                        super_cd_element=cd_element,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        with_layout=make_base_product_layouts,
                    )
                )
        if cd_element.annotation.extension.list_of_product_links is not None:
            for (
                cd_product_link
            ) in (
                cd_element.annotation.extension.list_of_product_links.product_link
            ):
                product_model_element, product_layout_element = (
                    cls._make_and_add_product_from_cd_product_link(
                        model=model,
                        layout=layout,
                        cd_element=cd_product_link,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        cd_id_to_annotations=cd_id_to_annotations,
                        cd_id_to_notes=cd_id_to_notes,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                        super_cd_element=cd_element,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
        cd_boolean_modifications = []
        cd_normal_modifications = []
        cd_boolean_input_ids = []
        if cd_element.annotation.extension.list_of_modification is not None:
            for (
                cd_modification
            ) in (
                cd_element.annotation.extension.list_of_modification.modification
            ):
                # Boolean gates are in the list of modifications; their inputs
                # are also in the list of modifications; a Boolean gate is
                # always the source of a catalysis.
                # We first go through the list of modifications to get the
                # Boolean gates; we then remove their inputs from the list of
                # modifications, and transform the Boolean modifications as well
                # as the normal ones.
                if cd_modification.type_value in [
                    momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_AND,
                    momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_OR,
                    momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_NOT,
                    momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_UNKNOWN,
                ]:
                    cd_boolean_modifications.append(cd_modification)
                    cd_boolean_input_ids += cd_modification.modifiers.split(
                        ","
                    )
                else:
                    cd_normal_modifications.append(cd_modification)
            for cd_modification in cd_boolean_modifications:
                modifier_model_element, modifier_layout_element = (
                    cls._make_and_add_elements_from_cd(
                        model=model,
                        layout=layout,
                        cd_element=cd_modification,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        cd_id_to_annotations=cd_id_to_annotations,
                        cd_id_to_notes=cd_id_to_notes,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                        super_cd_element=cd_element,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
            for cd_modification in cd_normal_modifications:
                if cd_modification.modifiers not in cd_boolean_input_ids:
                    modifier_model_element, modifier_layout_element = (
                        cls._make_and_add_elements_from_cd(
                            model=model,
                            layout=layout,
                            cd_element=cd_modification,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            cd_id_to_annotations=cd_id_to_annotations,
                            cd_id_to_notes=cd_id_to_notes,
                            super_model_element=model_element,
                            super_layout_element=layout_element,
                            super_cd_element=cd_element,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                        )
                    )
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = momapy.builder.object_from_builder(layout_element)
        if cd_element.annotation is not None:
            if cd_element.annotation.rdf is not None:
                annotations = cls._make_annotations_from_cd_annotation_rdf(
                    cd_element.annotation.rdf
                )
                map_element_to_annotations[model_element].update(annotations)
        return model_element, layout_element

    @classmethod
    def _generic_make_and_add_modifier_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._generic_make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=model_element_cls,
                layout_element_cls=layout_element_cls,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        if model is not None:
            super_model_element.modifiers.add(model_element)
        if layout is not None:
            super_layout_element.layout_elements.append(layout_element)
        return model_element, layout_element

    @classmethod
    def _generic_make_modifier_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        if model is not None:
            model_element = model.new_element(model_element_cls)
            species_model_element = cd_id_to_model_element[cd_element.aliases]
            model_element.referred_species = species_model_element
            model_element = momapy.builder.object_from_builder(model_element)
        else:
            model_element = None
        if layout is not None:
            layout_element = layout.new_element(layout_element_cls)
            cd_link_target = cd_element.link_target[0]
            source_layout_element = cd_id_to_layout_element[
                cd_link_target.alias
            ]
            if cd_link_target.link_anchor is not None:
                source_anchor_name = (
                    cls._get_anchor_name_for_frame_from_cd_base_participant(
                        cd_link_target
                    )
                )
            else:
                source_anchor_name = "center"
            origin = source_layout_element.anchor_point(source_anchor_name)
            unit_x = super_layout_element._get_reaction_node_position()
            unit_y = unit_x.transformed(
                momapy.geometry.Rotation(math.radians(90), origin)
            )
            transformation = momapy.geometry.get_transformation_for_frame(
                origin, unit_x, unit_y
            )
            intermediate_points = []
            cd_edit_points = cd_element.edit_points
            edit_points = [
                momapy.geometry.Point(
                    *[float(coord) for coord in cd_edit_point.split(",")]
                )
                for cd_edit_point in cd_edit_points
            ]
            for edit_point in edit_points:
                intermediate_point = edit_point.transformed(transformation)
                intermediate_points.append(intermediate_point)
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
            end_point = super_layout_element.reaction_node_border(
                reference_point
            )
            points = [start_point] + intermediate_points + [end_point]
            for i, point in enumerate(points[1:]):
                previous_point = points[i]
                segment = momapy.geometry.Segment(previous_point, point)
                layout_element.segments.append(segment)
            layout_element = momapy.builder.object_from_builder(layout_element)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _generic_make_and_add_gate_and_modifier_from_cd_modification(
        cls,
        model,
        layout,
        cd_element,
        gate_model_element_cls,
        gate_layout_element_cls,
        modifier_model_element_cls,
        modifier_layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        gate_model_element, gate_layout_element = (
            cls._generic_make_and_add_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=gate_model_element_cls,
                layout_element_cls=gate_layout_element_cls,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id_
        modifier_model_element, modifier_layout_element = (
            cls._generic_make_modifier_from_cd_modification(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=modifier_model_element_cls,
                layout_element_cls=modifier_layout_element_cls,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _generic_make_and_add_gate_from_cd_modification_or_gate_member(
        cls,
        model,
        layout,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element, layout_element = (
            cls._generic_make_gate_from_cd_modification_or_gate_member(
                model=model,
                layout=layout,
                cd_element=cd_element,
                model_element_cls=model_element_cls,
                layout_element_cls=layout_element_cls,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        )
        if model is not None:
            super_model_element.modifiers.add(model_element)
        if layout is not None:
            super_layout_element.layout_elements.append(layout_element)
        return model_element, layout_element

    @classmethod
    def _make_modulation_from_cd_reaction(
        cls,
        model,
        layout,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element = model.new_element(model_element_cls)
        model_element.id_ = cd_element.id
        cd_base_reactant = (
            cd_element.annotation.extension.base_reactants.base_reactant[0]
        )
        source_model_element = cd_id_to_model_element[cd_base_reactant.alias]
        model_element.source = source_model_element
        cd_base_product = (
            cd_element.annotation.extension.base_products.base_product[0]
        )
        target_model_element = cd_id_to_model_element[cd_base_product.alias]
        model_element.target = target_model_element
        model_element = momapy.builder.object_from_builder(model_element)
        if (
            with_layout and layout_element_cls is not None
        ):  # to delete second part
            layout_element = layout.new_element(layout_element_cls)
            source_layout_element = cd_id_to_layout_element[
                cd_base_reactant.alias
            ]
            if cd_base_reactant.link_anchor is not None:
                source_anchor_name = (
                    cls._get_anchor_name_for_frame_from_cd_base_participant(
                        cd_base_reactant
                    )
                )
            else:
                source_anchor_name = "center"
            target_layout_element = cd_id_to_layout_element[
                cd_base_product.alias
            ]
            if cd_base_product.link_anchor is not None:
                target_anchor_name = (
                    cls._get_anchor_name_for_frame_from_cd_base_participant(
                        cd_base_product
                    )
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
            intermediate_points = []
            cd_edit_points = cd_element.annotation.extension.edit_points
            if cd_edit_points is not None:
                edit_points = [
                    momapy.geometry.Point(
                        *[float(coord) for coord in cd_edit_point.split(",")]
                    )
                    for cd_edit_point in cd_edit_points.value
                ]
                for edit_point in edit_points:
                    intermediate_point = edit_point.transformed(transformation)
                    intermediate_points.append(intermediate_point)
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
                end_point = target_layout_element.anchor_point(
                    target_anchor_name
                )
            points = [start_point] + intermediate_points + [end_point]
            for i, point in enumerate(points[1:]):
                previous_point = points[i]
                segment = momapy.geometry.Segment(previous_point, point)
                layout_element.segments.append(segment)
        else:
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_boolean_logic_gate_from_cd_modification_or_gate_member(
        cls,
        model,
        layout,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element,
        super_layout_element,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element = model.new_element(model_element_cls)
        for cd_boolean_input_id in cd_element.aliases.split(","):
            boolean_input_model_element = cd_id_to_model_element[
                cd_boolean_input_id
            ]
            model_element.inputs.add(boolean_input_model_element)
        layout_element = None
        model_element = momapy.builder.object_from_builder(model_element)
        return model_element, layout_element

    @classmethod
    def _make_modulation_from_cd_reaction_with_gate_members(
        cls,
        model,
        layout,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        model_element = model.new_element(model_element_cls)
        model_element.id_ = cd_element.id
        # first we select the gate member corresponding to the boolean logic gate
        # as it contains the id of the source of the modulation
        for (
            cd_gate_member
        ) in cd_element.annotation.extension.list_of_gate_member.gate_member:
            if cd_gate_member.modification_type is not None:
                break
        source_model_element = cd_id_to_model_element[cd_gate_member.aliases]
        model_element.source = source_model_element
        # the target is the base product of the cd element
        if cd_element.list_of_products is not None:
            for cd_product in cd_element.list_of_products.species_reference:
                target_model_element = cd_id_to_model_element[
                    cd_product.annotation.extension.alias
                ]
                model_element.target = target_model_element
                break
        model_element = momapy.builder.object_from_builder(model_element)
        layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_annotations_from_cd_annotation_rdf(cls, cd_element):
        annotations = []
        if cd_element.description is not None:
            for (
                qualifier_attribute,
                qualifier,
            ) in cls._QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER.items():
                annotation_values = getattr(
                    cd_element.description, qualifier_attribute
                )
                if annotation_values:
                    for annotation_value in annotation_values:
                        resources = []
                        annotation_bag = annotation_value.bag
                        for li in annotation_bag.li:
                            resources.append(li.resource)
                        annotation = momapy.sbml.core.Annotation(
                            qualifier=qualifier, resources=frozenset(resources)
                        )
                        annotations.append(annotation)
        return annotations

    @classmethod
    def _make_and_add_elements_from_cd(
        cls,
        model,
        layout,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        cd_id_to_annotations,
        cd_id_to_notes,
        super_model_element=None,
        super_layout_element=None,
        super_cd_element=None,
        with_annotations=True,
        with_notes=True,
    ):
        make_and_add_func = cls._get_make_and_add_func_from_cd(
            cd_element=cd_element, cd_id_to_cd_element=cd_id_to_cd_element
        )
        if make_and_add_func is not None:
            model_element, layout_element = make_and_add_func(
                model=model,
                layout=layout,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                cd_id_to_annotations=cd_id_to_annotations,
                cd_id_to_notes=cd_id_to_notes,
                super_model_element=super_model_element,
                super_layout_element=super_layout_element,
                super_cd_element=super_cd_element,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _prepare_name(cls, name: str | None):
        if name is None:
            return name
        for s, char in cls._TEXT_TO_CHARACTER.items():
            name = name.replace(s, char)
        return name

    @classmethod
    def _get_make_and_add_func_from_cd(cls, cd_element, cd_id_to_cd_element):
        if isinstance(
            cd_element,
            (
                momapy.celldesigner.io._celldesigner_parser.Protein,
                momapy.celldesigner.io._celldesigner_parser.Gene,
                momapy.celldesigner.io._celldesigner_parser.Rna,
                momapy.celldesigner.io._celldesigner_parser.AntisenseRna,
            ),
        ):
            if cd_element.type_value is not None:
                key = cd_element.type_value
            else:  # to be deleted once minerva bug solved
                key = type(cd_element)
        elif isinstance(
            cd_element,
            (
                momapy.celldesigner.io._celldesigner_parser.SpeciesAlias,
                momapy.celldesigner.io._celldesigner_parser.ComplexSpeciesAlias,
            ),
        ):
            cd_species_template = (
                cls._get_cd_species_template_from_cd_species_alias(
                    cd_element=cd_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                )
            )
            cd_species = cd_id_to_cd_element[cd_element.species]
            if cd_element.complex_species_alias is None:
                cd_class_value = (
                    cd_species.annotation.extension.species_identity.class_value
                )
                if cd_species_template is not None:
                    key = (
                        cd_class_value,
                        cd_species_template.type_value,
                    )
                else:
                    key = cd_class_value
            else:
                cd_class_value = (
                    cd_species.annotation.species_identity.class_value
                )
                if cd_species_template is not None:
                    key = (
                        cd_class_value,
                        cd_species_template.type_value,
                        "included",
                    )
                else:
                    key = (cd_class_value, "included")
        elif isinstance(
            cd_element, momapy.celldesigner.io._celldesigner_parser.Reaction
        ):
            key = cd_element.annotation.extension.reaction_type
            if cd_element.annotation.extension.list_of_gate_member is not None:
                for (
                    cd_gate_member
                ) in (
                    cd_element.annotation.extension.list_of_gate_member.gate_member
                ):
                    if cd_gate_member.modification_type is not None:
                        key = (
                            cd_gate_member.type_value,
                            cd_gate_member.modification_type,
                        )
        elif isinstance(
            cd_element,
            momapy.celldesigner.io._celldesigner_parser.Modification,
        ):
            if cd_element.modification_type is not None:
                key = (
                    cd_element.type_value,
                    cd_element.modification_type,
                )
            else:
                key = cd_element.type_value
        else:
            key = type(cd_element)
        make_and_add_func_name = cls._KEY_TO_MAKE_AND_ADD_FUNC_NAME.get(key)
        if make_and_add_func_name is None:
            print(f"no reading function for {key}")
            return None
        return getattr(cls, make_and_add_func_name)


momapy.io.register_reader("celldesigner", CellDesignerReader)
