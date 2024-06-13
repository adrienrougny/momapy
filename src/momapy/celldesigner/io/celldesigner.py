import collections

import momapy.core
import momapy.io
import momapy.coloring
import momapy.celldesigner.core
import momapy.celldesigner.io._celldesigner_parser
import momapy.sbgn.pd

import frozendict
import xsdata.formats.dataclass.context
import xsdata.formats.dataclass.parsers
import xsdata.formats.dataclass.parsers.config


class CellDesignerReader(momapy.io.MapReader):
    _KEY_TO_MAKE_AND_ADD_FUNC_NAME = {
        momapy.celldesigner.io._celldesigner_parser.ModificationResidue: "_make_and_add_modification_residue_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ListOfModifications.Modification: "_make_and_add_modification_from_cd",
        momapy.celldesigner.io._celldesigner_parser.StructuralStates: "_make_and_add_structural_state_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ProteinType.GENERIC: "_make_and_add_generic_protein_reference_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ProteinType.ION_CHANNEL: "_make_and_add_ion_channel_reference_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ProteinType.RECEPTOR: "_make_and_add_receptor_reference_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ProteinType.TRUNCATED: "_make_and_add_receptor_reference_from_cd",
        momapy.celldesigner.io._celldesigner_parser.GeneType.GENE: "_make_and_add_gene_reference_from_cd",
        momapy.celldesigner.io._celldesigner_parser.RnaType.RNA: "_make_and_add_rna_reference_from_cd",
        momapy.celldesigner.io._celldesigner_parser.AntisenseRnaType.ANTISENSE_RNA: "_make_and_add_antisense_rna_reference_from_cd",
        momapy.celldesigner.io._celldesigner_parser.Gene: "_make_and_add_gene_reference_from_cd",  # to be deleted once minerva bug solved
        momapy.celldesigner.io._celldesigner_parser.Rna: "_make_and_add_rna_reference_from_cd",  # to be deleted once minerva bug solved
        momapy.celldesigner.io._celldesigner_parser.AntisenseRna: "_make_and_add_antisense_rna_reference_from_cd",  # to be deleted once minerva bug solved
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.PROTEIN,
            momapy.celldesigner.io._celldesigner_parser.ProteinType.GENERIC,
        ): "_make_and_add_generic_protein_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.PROTEIN,
            momapy.celldesigner.io._celldesigner_parser.ProteinType.ION_CHANNEL,
        ): "_make_and_add_ion_channel_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.PROTEIN,
            momapy.celldesigner.io._celldesigner_parser.ProteinType.RECEPTOR,
        ): "_make_and_add_receptor_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.PROTEIN,
            momapy.celldesigner.io._celldesigner_parser.ProteinType.TRUNCATED,
        ): "_make_and_add_truncated_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.GENE,
            momapy.celldesigner.io._celldesigner_parser.GeneType.GENE,
        ): "_make_and_add_gene_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.RNA,
            momapy.celldesigner.io._celldesigner_parser.RnaType.RNA,
        ): "_make_and_add_rna_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.ANTISENSE_RNA,
            momapy.celldesigner.io._celldesigner_parser.AntisenseRnaType.ANTISENSE_RNA,
        ): "_make_and_add_antisense_rna_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.GENE,
            None,
        ): "_make_and_add_gene_from_cd",  # to be deleted once minerva bug solved
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.RNA,
            None,
        ): "_make_and_add_rna_from_cd",  # to be deleted once minerva bug solved
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.ANTISENSE_RNA,
            None,
        ): "_make_and_add_antisense_rna_from_cd",  # to be deleted once minerva bug solved
        momapy.celldesigner.io._celldesigner_parser.ClassValue.PHENOTYPE: "_make_and_add_phenotype_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ClassValue.ION: "_make_and_add_ion_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ClassValue.SIMPLE_MOLECULE: "_make_and_add_simple_molecule_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ClassValue.DRUG: "_make_and_add_drug_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ClassValue.COMPLEX: "_make_and_add_complex_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ClassValue.UNKNOWN: "_make_and_add_unknown_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ClassValue.DEGRADED: "_make_and_add_degraded_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.PROTEIN,
            momapy.celldesigner.io._celldesigner_parser.ProteinType.GENERIC,
            "included",
        ): "_make_and_add_included_generic_protein_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.PROTEIN,
            momapy.celldesigner.io._celldesigner_parser.ProteinType.ION_CHANNEL,
            "included",
        ): "_make_and_add_included_ion_channel_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.PROTEIN,
            momapy.celldesigner.io._celldesigner_parser.ProteinType.RECEPTOR,
            "included",
        ): "_make_and_add_included_receptor_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.PROTEIN,
            momapy.celldesigner.io._celldesigner_parser.ProteinType.TRUNCATED,
            "included",
        ): "_make_and_add_included_truncated_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.GENE,
            momapy.celldesigner.io._celldesigner_parser.GeneType.GENE,
            "included",
        ): "_make_and_add_included_gene_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.RNA,
            momapy.celldesigner.io._celldesigner_parser.RnaType.RNA,
            "included",
        ): "_make_and_add_included_rna_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.ANTISENSE_RNA,
            momapy.celldesigner.io._celldesigner_parser.AntisenseRnaType.ANTISENSE_RNA,
            "included",
        ): "_make_and_add_included_antisense_rna_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.GENE,
            None,
            "included",
        ): "_make_and_add_included_gene_from_cd",  # to be deleted once minerva bug solved
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.RNA,
            None,
            "included",
        ): "_make_and_add_included_rna_from_cd",  # to be deleted once minerva bug solved
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.ANTISENSE_RNA,
            None,
            "included",
        ): "_make_and_add_included_antisense_rna_from_cd",  # to be deleted once minerva bug solved
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.PHENOTYPE,
            "included",
        ): "_make_and_add_included_phenotype_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.ION,
            "included",
        ): "_make_and_add_included_ion_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.SIMPLE_MOLECULE,
            "included",
        ): "_make_and_add_included_simple_molecule_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.DRUG,
            "included",
        ): "_make_and_add_included_drug_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.COMPLEX,
            "included",
        ): "_make_and_add_included_complex_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.UNKNOWN,
            "included",
        ): "_make_and_add_included_unknown_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ClassValue.DEGRADED,
            "included",
        ): "_make_and_add_included_degraded_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.STATE_TRANSITION: "_make_and_add_state_transition_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.KNOWN_TRANSITION_OMITTED: "_make_and_add_known_transition_omitted_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.UNKNOWN_TRANSITION: "_make_and_add_unknown_transition_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.TRANSCRIPTION: "_make_and_add_transcription_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.TRANSLATION: "_make_and_add_translation_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.TRANSPORT: "_make_and_add_transport_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.HETERODIMER_ASSOCIATION: "_make_and_add_heterodimer_association_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.DISSOCIATION: "_make_and_add_dissociation_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.TRUNCATION: "_make_and_add_truncation_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.CATALYSIS: "_make_and_add_catalysis_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.UNKNOWN_CATALYSIS: "_make_and_add_unknown_catalysis_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.INHIBITION: "_make_and_add_inhibition_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.UNKNOWN_INHIBITION: "_make_and_add_unknown_inhibition_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.PHYSICAL_STIMULATION: "_make_and_add_physical_stimulation_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.MODULATION: "_make_and_add_modulation_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.TRIGGER: "_make_and_add_triggering_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.POSITIVE_INFLUENCE: "_make_and_add_positive_influence_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.UNKNOWN_POSITIVE_INFLUENCE: "_make_and_add_unknown_positive_influence_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.NEGATIVE_INFLUENCE: "_make_and_add_negative_influence_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.UNKNOWN_NEGATIVE_INFLUENCE: "_make_and_add_unknown_negative_influence_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.REDUCED_PHYSICAL_STIMULATION: "_make_and_add_physical_stimulation_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.UNKNOWN_REDUCED_PHYSICAL_STIMULATION: "_make_and_add_unknown_physical_stimulation_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.REDUCED_MODULATION: "_make_and_add_modulation_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.UNKNOWN_REDUCED_MODULATION: "_make_and_add_unknown_modulation_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.REDUCED_TRIGGER: "_make_and_add_triggering_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ReactionTypeValue.UNKNOWN_REDUCED_TRIGGER: "_make_and_add_unknown_triggering_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ModificationType.CATALYSIS: "_make_and_add_catalyzer_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ModificationType.UNKNOWN_CATALYSIS: "_make_and_add_unknown_catalyzer_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ModificationType.INHIBITION: "_make_and_add_inhibitor_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ModificationType.UNKNOWN_INHIBITION: "_make_and_add_unknown_inhibitor_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ModificationType.PHYSICAL_STIMULATION: "_make_and_add_physical_stimulator_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ModificationType.MODULATION: "_make_and_add_modulator_from_cd",
        momapy.celldesigner.io._celldesigner_parser.ModificationType.TRIGGER: "_make_and_add_trigger_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.CATALYSIS,
        ): "_make_and_add_and_gate_and_catalyzer_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.UNKNOWN_CATALYSIS,
        ): "_make_and_add_and_gate_and_unknown_catalyzer_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.INHIBITION,
        ): "_make_and_add_and_gate_and_inhibitor_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.UNKNOWN_INHIBITION,
        ): "_make_and_add_and_gate_and_unknown_inhibitor_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.PHYSICAL_STIMULATION,
        ): "_make_and_add_and_gate_and_physical_stimulator_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.MODULATION,
        ): "_make_and_add_and_gate_and_modulator_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.TRIGGER,
        ): "_make_and_add_and_gate_and_trigger_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.CATALYSIS,
        ): "_make_and_add_or_gate_and_catalyzer_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.UNKNOWN_CATALYSIS,
        ): "_make_and_add_or_gate_and_unknown_catalyzer_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.INHIBITION,
        ): "_make_and_add_or_gate_and_inhibitor_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.UNKNOWN_INHIBITION,
        ): "_make_and_add_or_gate_and_unknown_inhibitor_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.PHYSICAL_STIMULATION,
        ): "_make_and_add_or_gate_and_physical_stimulator_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.MODULATION,
        ): "_make_and_add_or_gate_and_modulator_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.TRIGGER,
        ): "_make_and_add_or_gate_and_trigger_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.CATALYSIS,
        ): "_make_and_add_not_gate_and_catalyzer_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.UNKNOWN_CATALYSIS,
        ): "_make_and_add_not_gate_and_unknown_catalyzer_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.INHIBITION,
        ): "_make_and_add_not_gate_and_inhibitor_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.UNKNOWN_INHIBITION,
        ): "_make_and_add_not_gate_and_unknown_inhibitor_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.PHYSICAL_STIMULATION,
        ): "_make_and_add_not_gate_and_physical_stimulator_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.MODULATION,
        ): "_make_and_add_not_gate_and_modulator_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.TRIGGER,
        ): "_make_and_add_not_gate_and_trigger_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.CATALYSIS,
        ): "_make_and_add_unknown_gate_and_catalyzer_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.UNKNOWN_CATALYSIS,
        ): "_make_and_add_unknown_gate_and_unknown_catalyzer_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.INHIBITION,
        ): "_make_and_add_unknown_gate_and_inhibitor_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.UNKNOWN_INHIBITION,
        ): "_make_and_add_unknown_gate_and_unknown_inhibitor_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.PHYSICAL_STIMULATION,
        ): "_make_and_add_unknown_gate_and_physical_stimulator_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.MODULATION,
        ): "_make_and_add_unknown_gate_and_modulator_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.ModificationModificationType.TRIGGER,
        ): "_make_and_add_unknown_gate_and_trigger_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.CATALYSIS,
        ): "_make_and_add_reduced_and_gate_and_catalysis_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_CATALYSIS,
        ): "_make_and_add_reduced_and_gate_and_unknown_catalysis_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.INHIBITION,
        ): "_make_and_add_reduced_and_gate_and_inhibition_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_INHIBITION,
        ): "_make_and_add_reduced_and_gate_and_unknown_inhibition_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.PHYSICAL_STIMULATION,
        ): "_make_and_add_reduced_and_gate_and_physical_stimulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.MODULATION,
        ): "_make_and_add_reduced_and_gate_and_modulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.TRIGGER,
        ): "_make_and_add_reduced_and_gate_and_triggering_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.POSITIVE_INFLUENCE,
        ): "_make_and_add_reduced_and_gate_and_positive_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_POSITIVE_INFLUENCE,
        ): "_make_and_add_reduced_and_gate_and_unknown_positive_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.NEGATIVE_INFLUENCE,
        ): "_make_and_add_reduced_and_gate_and_negative_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_NEGATIVE_INFLUENCE,
        ): "_make_and_add_reduced_and_gate_and_unknown_negative_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.REDUCED_PHYSICAL_STIMULATION,
        ): "_make_and_add_reduced_and_gate_and_physical_stimulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_REDUCED_PHYSICAL_STIMULATION,
        ): "_make_and_add_reduced_and_gate_and_unknown_physical_stimulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.REDUCED_MODULATION,
        ): "_make_and_add_reduced_and_gate_and_modulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_REDUCED_MODULATION,
        ): "_make_and_add_reduced_and_gate_and_unknown_modulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.REDUCED_TRIGGER,
        ): "_make_and_add_reduced_and_gate_and_triggering_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_AND,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_REDUCED_TRIGGER,
        ): "_make_and_add_reduced_and_gate_and_unknown_triggering_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.CATALYSIS,
        ): "_make_and_add_reduced_or_gate_and_catalysis_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_CATALYSIS,
        ): "_make_and_add_reduced_or_gate_and_unknown_catalysis_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.INHIBITION,
        ): "_make_and_add_reduced_or_gate_and_inhibition_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_INHIBITION,
        ): "_make_and_add_reduced_or_gate_and_unknown_inhibition_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.PHYSICAL_STIMULATION,
        ): "_make_and_add_reduced_or_gate_and_physical_stimulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.MODULATION,
        ): "_make_and_add_reduced_or_gate_and_modulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.TRIGGER,
        ): "_make_and_add_reduced_or_gate_and_triggering_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.POSITIVE_INFLUENCE,
        ): "_make_and_add_reduced_or_gate_and_positive_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_POSITIVE_INFLUENCE,
        ): "_make_and_add_reduced_or_gate_and_unknown_positive_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.NEGATIVE_INFLUENCE,
        ): "_make_and_add_reduced_or_gate_and_negative_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_NEGATIVE_INFLUENCE,
        ): "_make_and_add_reduced_or_gate_and_unknown_negative_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.REDUCED_PHYSICAL_STIMULATION,
        ): "_make_and_add_reduced_or_gate_and_physical_stimulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_REDUCED_PHYSICAL_STIMULATION,
        ): "_make_and_add_reduced_or_gate_and_unknown_physical_stimulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.REDUCED_MODULATION,
        ): "_make_and_add_reduced_or_gate_and_modulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_REDUCED_MODULATION,
        ): "_make_and_add_reduced_or_gate_and_unknown_modulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.REDUCED_TRIGGER,
        ): "_make_and_add_reduced_or_gate_and_triggering_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_OR,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_REDUCED_TRIGGER,
        ): "_make_and_add_reduced_or_gate_and_unknown_triggering_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.CATALYSIS,
        ): "_make_and_add_reduced_not_gate_and_catalysis_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_CATALYSIS,
        ): "_make_and_add_reduced_not_gate_and_unknown_catalysis_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.INHIBITION,
        ): "_make_and_add_reduced_not_gate_and_inhibition_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_INHIBITION,
        ): "_make_and_add_reduced_not_gate_and_unknown_inhibition_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.PHYSICAL_STIMULATION,
        ): "_make_and_add_reduced_not_gate_and_physical_stimulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.MODULATION,
        ): "_make_and_add_reduced_not_gate_and_modulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.TRIGGER,
        ): "_make_and_add_reduced_not_gate_and_triggering_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.POSITIVE_INFLUENCE,
        ): "_make_and_add_reduced_not_gate_and_positive_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_POSITIVE_INFLUENCE,
        ): "_make_and_add_reduced_not_gate_and_unknown_positive_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.NEGATIVE_INFLUENCE,
        ): "_make_and_add_reduced_not_gate_and_negative_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_NEGATIVE_INFLUENCE,
        ): "_make_and_add_reduced_not_gate_and_unknown_negative_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.REDUCED_PHYSICAL_STIMULATION,
        ): "_make_and_add_reduced_not_gate_and_physical_stimulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_REDUCED_PHYSICAL_STIMULATION,
        ): "_make_and_add_reduced_not_gate_and_unknown_physical_stimulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.REDUCED_MODULATION,
        ): "_make_and_add_reduced_not_gate_and_modulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_REDUCED_MODULATION,
        ): "_make_and_add_reduced_not_gate_and_unknown_modulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.REDUCED_TRIGGER,
        ): "_make_and_add_reduced_not_gate_and_triggering_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_NOT,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_REDUCED_TRIGGER,
        ): "_make_and_add_reduced_not_gate_and_unknown_triggering_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.CATALYSIS,
        ): "_make_and_add_reduced_unknown_gate_and_catalysis_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_CATALYSIS,
        ): "_make_and_add_reduced_unknown_gate_and_unknown_catalysis_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.INHIBITION,
        ): "_make_and_add_reduced_unknown_gate_and_inhibition_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_INHIBITION,
        ): "_make_and_add_reduced_unknown_gate_and_unknown_inhibition_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.PHYSICAL_STIMULATION,
        ): "_make_and_add_reduced_unknown_gate_and_physical_stimulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.MODULATION,
        ): "_make_and_add_reduced_unknown_gate_and_modulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.TRIGGER,
        ): "_make_and_add_reduced_unknown_gate_and_triggering_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.POSITIVE_INFLUENCE,
        ): "_make_and_add_reduced_unknown_gate_and_positive_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_POSITIVE_INFLUENCE,
        ): "_make_and_add_reduced_unknown_gate_and_unknown_positive_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.NEGATIVE_INFLUENCE,
        ): "_make_and_add_reduced_unknown_gate_and_negative_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_NEGATIVE_INFLUENCE,
        ): "_make_and_add_reduced_unknown_gate_and_unknown_negative_influence_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.REDUCED_PHYSICAL_STIMULATION,
        ): "_make_and_add_reduced_unknown_gate_and_physical_stimulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_REDUCED_PHYSICAL_STIMULATION,
        ): "_make_and_add_reduced_unknown_gate_and_unknown_physical_stimulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.REDUCED_MODULATION,
        ): "_make_and_add_reduced_unknown_gate_and_modulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_REDUCED_MODULATION,
        ): "_make_and_add_reduced_unknown_gate_and_unknown_modulation_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.REDUCED_TRIGGER,
        ): "_make_and_add_reduced_unknown_gate_and_triggering_from_cd",
        (
            momapy.celldesigner.io._celldesigner_parser.GateMemberType.BOOLEAN_LOGIC_GATE_UNKNOWN,
            momapy.celldesigner.io._celldesigner_parser.GateMemberModificationType.UNKNOWN_REDUCED_TRIGGER,
        ): "_make_and_add_reduced_unknown_gate_and_unknown_triggering_from_cd",
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

    @classmethod
    def check_file(cls, file_path):
        with open(file_path) as f:
            for line in f:
                if "http://www.sbml.org/2001/ns/celldesigner" in line:
                    return True
        return False

    @classmethod
    def read(
        cls, file_path, **options
    ) -> momapy.celldesigner.core.CellDesignerMap:
        config = xsdata.formats.dataclass.parsers.config.ParserConfig(
            fail_on_unknown_properties=False
        )
        parser = xsdata.formats.dataclass.parsers.XmlParser(
            config=config,
            context=xsdata.formats.dataclass.context.XmlContext(),
        )
        cd_sbml = parser.parse(
            file_path, momapy.celldesigner.io._celldesigner_parser.Sbml
        )
        map_ = cls._make_map_from_cd(cd_sbml)
        return map_

    @classmethod
    def _make_map_from_cd(cls, cd_element):
        cd_id_to_model_element = {}
        cd_id_to_layout_element = {}
        map_element_to_annotations = collections.defaultdict(set)
        map_ = cls._make_map_no_subelements_from_cd(cd_element)
        # we map the ids to their corresponding cd elements
        cd_id_to_cd_element = {}
        if cd_element.model.list_of_compartments is not None:
            for (
                cd_compartment
            ) in cd_element.model.list_of_compartments.compartment:
                cd_id_to_cd_element[cd_compartment.id] = cd_compartment
        if cd_element.model.annotation.extension.list_of_proteins is not None:
            for (
                cd_species_reference
            ) in (
                cd_element.model.annotation.extension.list_of_proteins.protein
            ):
                cd_id_to_cd_element[cd_species_reference.id] = (
                    cd_species_reference
                )
        if cd_element.model.annotation.extension.list_of_genes is not None:
            for (
                cd_species_reference
            ) in cd_element.model.annotation.extension.list_of_genes.gene:
                cd_id_to_cd_element[cd_species_reference.id] = (
                    cd_species_reference
                )
        if cd_element.model.annotation.extension.list_of_rnas is not None:
            for (
                cd_species_reference
            ) in cd_element.model.annotation.extension.list_of_rnas.rna:
                cd_id_to_cd_element[cd_species_reference.id] = (
                    cd_species_reference
                )
        if (
            cd_element.model.annotation.extension.list_of_antisense_rnas
            is not None
        ):
            for (
                cd_species_reference
            ) in (
                cd_element.model.annotation.extension.list_of_antisense_rnas.antisense_rna
            ):
                cd_id_to_cd_element[cd_species_reference.id] = (
                    cd_species_reference
                )
        if cd_element.model.list_of_species is not None:
            for cd_species in cd_element.model.list_of_species.species:
                cd_id_to_cd_element[cd_species.id] = cd_species
        if (
            cd_element.model.annotation.extension.list_of_included_species
            is not None
        ):
            for (
                cd_species
            ) in (
                cd_element.model.annotation.extension.list_of_included_species.species
            ):
                cd_id_to_cd_element[cd_species.id] = cd_species
        if (
            cd_element.model.annotation.extension.list_of_species_aliases
            is not None
        ):
            for (
                cd_alias
            ) in (
                cd_element.model.annotation.extension.list_of_species_aliases.species_alias
            ):
                cd_id_to_cd_element[cd_alias.id] = cd_alias
        if (
            cd_element.model.annotation.extension.list_of_complex_species_aliases
            is not None
        ):
            for (
                cd_alias
            ) in (
                cd_element.model.annotation.extension.list_of_complex_species_aliases.complex_species_alias
            ):
                cd_id_to_cd_element[cd_alias.id] = cd_alias
        # we map the ids of complex aliases to the list of the ids of the
        # species aliases they include, and we store the species aliases
        cd_complex_alias_id_to_cd_included_species_ids = (
            collections.defaultdict(list)
        )
        cd_included_species_alias_ids = set([])
        if (
            cd_element.model.annotation.extension.list_of_species_aliases
            is not None
        ):
            for (
                cd_alias
            ) in (
                cd_element.model.annotation.extension.list_of_species_aliases.species_alias
            ):
                if cd_alias.complex_species_alias is not None:
                    cd_complex_alias_id_to_cd_included_species_ids[
                        cd_alias.complex_species_alias
                    ].append(cd_alias.id)
                    cd_included_species_alias_ids.add(cd_alias.id)
        if (
            cd_element.model.annotation.extension.list_of_complex_species_aliases
            is not None
        ):
            for (
                cd_alias
            ) in (
                cd_element.model.annotation.extension.list_of_complex_species_aliases.complex_species_alias
            ):
                if cd_alias.complex_species_alias is not None:
                    cd_complex_alias_id_to_cd_included_species_ids[
                        cd_alias.complex_species_alias
                    ].append(cd_alias.id)
                    cd_included_species_alias_ids.add(cd_alias.id)

        # we make and add the  model and layout elements from the cd objects
        # we make and add the compartments TODO: see what is a compartment alias
        for (
            cd_compartment
        ) in cd_element.model.list_of_compartments.compartment:
            model_element, layout_element = (
                cls._make_and_add_compartment_from_cd(
                    map_=map_,
                    cd_element=cd_compartment,
                    cd_id_to_model_element=cd_id_to_model_element,
                    cd_id_to_layout_element=cd_id_to_layout_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                    cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                    map_element_to_annotations=map_element_to_annotations,
                    super_model_element=None,
                    super_cd_element=None,
                )
            )
        # we make and add the species references
        for cd_species_reference in (
            cd_element.model.annotation.extension.list_of_antisense_rnas.antisense_rna
            + cd_element.model.annotation.extension.list_of_rnas.rna
            + cd_element.model.annotation.extension.list_of_genes.gene
            + cd_element.model.annotation.extension.list_of_proteins.protein
        ):
            model_element, layout_element = cls._make_and_add_elements_from_cd(
                map_=map_,
                cd_element=cd_species_reference,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=None,
                super_cd_element=None,
            )
        # we make and add the species, from the species aliases
        # species aliases are the glyphs; in terms of model, a species is almost
        # a model element on its own: the only attribute that is not on the
        # species but on the species alias is the activity (active or inactive);
        # hence two species aliases can be associated to only one species
        # but correspond to two different model elements; we do not make the
        # species that are included, they are made when we make their
        # containing complex
        if (
            cd_element.model.annotation.extension.list_of_species_aliases
            is not None
        ):
            for (
                cd_species_alias
            ) in (
                cd_element.model.annotation.extension.list_of_species_aliases.species_alias
            ):
                if cd_species_alias.id not in cd_included_species_alias_ids:
                    model_element, layout_element = (
                        cls._make_and_add_elements_from_cd(
                            map_=map_,
                            cd_element=cd_species_alias,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            map_element_to_annotations=map_element_to_annotations,
                            super_model_element=None,
                            super_cd_element=None,
                        )
                    )
        if (
            cd_element.model.annotation.extension.list_of_complex_species_aliases
            is not None
        ):
            for (
                cd_species_alias
            ) in (
                cd_element.model.annotation.extension.list_of_complex_species_aliases.complex_species_alias
            ):
                if cd_species_alias.id not in cd_included_species_alias_ids:
                    model_element, layout_element = (
                        cls._make_and_add_elements_from_cd(
                            map_=map_,
                            cd_element=cd_species_alias,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            map_element_to_annotations=map_element_to_annotations,
                            super_model_element=None,
                            super_cd_element=None,
                        )
                    )
        # we make and add the complexes, from the complex species aliases
        # we make and add the reactions
        # celldesigner reactions also include modulations
        if cd_element.model.list_of_reactions is not None:
            for cd_reaction in cd_element.model.list_of_reactions.reaction:
                model_element, layout_element = (
                    cls._make_and_add_elements_from_cd(
                        map_=map_,
                        cd_element=cd_reaction,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        super_model_element=None,
                        super_cd_element=None,
                    )
                )
        for map_element, annotations in map_element_to_annotations.items():
            map_element_to_annotations[map_element] = frozenset(annotations)
        map_.map_element_to_annotations = frozendict.frozendict(
            map_element_to_annotations
        )
        map_ = momapy.builder.object_from_builder(map_)
        return map_

    @classmethod
    def _make_map_no_subelements_from_cd(cls, cd_element):
        map_ = momapy.celldesigner.core.CellDesignerMapBuilder()
        map_.model = map_.new_model()
        return map_

    @classmethod
    def _make_and_add_modification_residue_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element,
    ):
        model_element = map_.new_model_element(
            momapy.celldesigner.core.ModificationResidue
        )
        # Defaults ids for modification residues are simple in CellDesigner (e.g.,
        # "rs1") and might be shared between residues of different species.
        # However we want a unique id, so we build it using the id of the
        # species as well.
        model_element.id = f"{super_model_element.id}_{cd_element.id}"
        model_element.name = cd_element.name
        layout_element = None
        model_element = momapy.builder.object_from_builder(model_element)
        super_model_element.modification_residues.add(model_element)
        # exceptionally we take the model element's id and not the cd element's
        # id for the reasons explained above
        cd_id_to_model_element[model_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_modification_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element,
    ):
        model_element = map_.new_model_element(
            momapy.celldesigner.core.Modification
        )
        cd_species_reference = (
            cls._get_cd_species_reference_from_cd_species_alias(
                super_cd_element, cd_id_to_cd_element
            )
        )
        cd_modification_residue_id = (
            f"{cd_species_reference.id}_{cd_element.residue}"
        )
        modification_residue_model_element = cd_id_to_model_element[
            cd_modification_residue_id
        ]
        model_element.residue = modification_residue_model_element
        cd_modification_state = cd_element.state
        if (
            cd_modification_state
            is momapy.celldesigner.io._celldesigner_parser.ModificationState.EMPTY
        ):
            modification_state = None
        else:
            modification_state = momapy.celldesigner.core.ModificationState[
                cd_modification_state.name
            ]
        model_element.state = modification_state
        model_element = momapy.builder.object_from_builder(model_element)
        super_model_element.modifications.add(model_element)
        layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_structural_state_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element,
    ):
        model_element = map_.new_model_element(
            momapy.celldesigner.core.StructuralState
        )
        model_element.value = cd_element.structural_state
        super_model_element.structural_states.add(model_element)
        layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_compartment_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        id_ = cd_element.id
        name = cd_element.name
        metaid = cd_element.metaid
        model_element = map_.new_model_element(
            momapy.celldesigner.core.Compartment
        )
        model_element.id = id_
        model_element.name = name
        model_element.metaid = metaid
        if cd_element.outside is not None:
            outside_model_element = cd_id_to_model_element.get(
                cd_element.outside
            )
            if outside_model_element is None:
                cd_outside = cd_id_to_cd_element[cd_element.outside]
                outside_mode_element, outside_layout_element = (
                    cls._make_and_add_compartment_from_cd(
                        map_=map_,
                        cd_element=cd_outside,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        super_model_element=None,
                        super_cd_element=None,
                    )
                )
            model_element.outside = outside_model_element
        if cd_element.annotation is not None:
            if cd_element.annotation.rdf is not None:
                annotations = cls._make_annotations_from_cd(
                    cd_element.annotation.rdf
                )
                map_element_to_annotations[model_element].update(annotations)
        layout_element = None
        model_element = momapy.builder.object_from_builder(model_element)
        if cd_element.annotation is not None:
            if cd_element.annotation.rdf is not None:
                annotations = cls._make_annotations_from_cd(
                    cd_element.annotation.rdf
                )
                map_element_to_annotations[model_element].update(annotations)
        map_.model.compartments.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_generic_protein_reference_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element = cls._make_species_reference_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.GenericProteinReference,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=None,
            super_cd_element=None,
        )
        layout_element = None
        map_.model.species_references.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_ion_channel_reference_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element = cls._make_species_reference_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.IonChannelReference,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=None,
            super_cd_element=None,
        )
        layout_element = None
        map_.model.species_references.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_receptor_reference_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element = cls._make_species_reference_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.ReceptorReference,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=None,
            super_cd_element=None,
        )
        layout_element = None
        map_.model.species_references.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_truncated_reference_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element = cls._make_species_reference_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.TruncatedProteinReference,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=None,
            super_cd_element=None,
        )
        layout_element = None
        map_.model.species_references.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_gene_reference_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element = cls._make_species_reference_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.GeneReference,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=None,
            super_cd_element=None,
        )
        layout_element = None
        map_.model.species_references.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_rna_reference_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element = cls._make_species_reference_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.RNAReference,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=None,
            super_cd_element=None,
        )
        layout_element = None
        map_.model.species_references.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_antisense_rna_reference_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element = cls._make_species_reference_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.AntisenseRNA,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=None,
            super_cd_element=None,
        )
        layout_element = None
        map_.model.species_references.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_generic_protein_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.GenericProtein,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_ion_channel_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.IonChannel,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_receptor_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Receptor,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_truncated_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.TruncatedProtein,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_gene_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Gene,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_rna_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.RNA,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_antisense_rna_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.AntisenseRNA,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_phenotype_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Phenotype,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_ion_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Ion,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_simple_molecule_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.SimpleMolecule,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_drug_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Drug,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Unknown,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_complex_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Complex,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_generic_protein_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.GenericProtein,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_degraded_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Degraded,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.species.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_receptor_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Receptor,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_ion_channel_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.IonChannel,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_truncated_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.TruncatedProtein,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_gene_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Gene,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_rna_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.RNA,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_antisense_rna_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.AntisenseRNA,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_phenotype_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Phenotype,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_ion_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Ion,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_simple_molecule_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.SimpleMolecule,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_drug_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Drug,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_unknown_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Unknown,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_complex_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Complex,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_included_degraded_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_included_species_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Degraded,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.subunits.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_reactant_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element = map_.new_model_element(
            momapy.celldesigner.core.Reactant
        )
        model_element.metaid = cd_element.metaid
        model_element.stoichiometry = cd_element.stoichiometry
        cd_alias_id = cd_element.annotation.extension.alias
        species_model_element = cd_id_to_model_element[cd_alias_id]
        model_element.species = species_model_element
        layout_element = None
        super_model_element.reactants.add(model_element)
        cd_id_to_model_element[cd_element.metaid] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_product_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element = map_.new_model_element(
            momapy.celldesigner.core.Product
        )
        model_element.metaid = cd_element.metaid
        model_element.stoichiometry = cd_element.stoichiometry
        cd_alias_id = cd_element.annotation.extension.alias
        species_model_element = cd_id_to_model_element[cd_alias_id]
        model_element.species = species_model_element
        layout_element = None
        super_model_element.products.add(model_element)
        cd_id_to_model_element[cd_element.metaid] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_catalyzer_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modifier_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Catalyzer,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.modifiers.add(model_element)
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_catalyzer_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modifier_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownCatalyzer,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.modifiers.add(model_element)
        return model_element, layout_element

    @classmethod
    def _make_and_add_inhibitor_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modifier_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Inhibitor,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.modifiers.add(model_element)
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_inhibitor_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modifier_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownInhibitor,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.modifiers.add(model_element)
        return model_element, layout_element

    @classmethod
    def _make_and_add_physical_stimulator_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modifier_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.PhysicalStimulator,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.modifiers.add(model_element)
        return model_element, layout_element

    @classmethod
    def _make_and_add_modulator_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modifier_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Modulator,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.modifiers.add(model_element)
        return model_element, layout_element

    @classmethod
    def _make_and_add_trigger_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modifier_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Trigger,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        super_model_element.modifiers.add(model_element)
        return model_element, layout_element

    @classmethod
    def _make_and_add_and_gate_and_catalyzer_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Catalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_unknown_catalyzer_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownCatalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_inhibitor_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Inhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_unknown_inhibitor_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownInhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_physical_stimulator_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.PhysicalStimulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_modulator_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Modulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_and_trigger_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Trigger,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_catalyzer_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Catalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_unknown_catalyzer_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownCatalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_inhibitor_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Inhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_unknown_inhibitor_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownInhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_physical_stimulator_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.PhysicalStimulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_modulator_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Modulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_or_gate_and_trigger_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Trigger,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_catalyzer_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Catalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_unknown_catalyzer_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownCatalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_inhibitor_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Inhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_unknown_inhibitor_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownInhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_physical_stimulator_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.PhysicalStimulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_modulator_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Modulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_not_gate_and_trigger_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Trigger,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_catalyzer_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Catalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_unknown_catalyzer_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownCatalyzer,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_inhibitor_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Inhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_unknown_inhibitor_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.UnknownInhibitor,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_physical_stimulator_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.PhysicalStimulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_modulator_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Modulator,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_unknown_gate_and_trigger_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        gate_model_element, gate_layout_element = (
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gates do not have ids: the modifiers attribute of a
        # Boolean logic gate modifier is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modification
        cd_element.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_modifier_from_cd(
                map_=map_,
                cd_element=cd_element,
                model_element_cls=momapy.celldesigner.core.Trigger,
                layout_element_cls=None,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        super_model_element.modifiers.add(modifier_model_element)
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_catalysis_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_catalysis_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_unknown_catalysis_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_catalysis_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_inhibition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_inhibition_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_unknown_inhibition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_inhibition_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_physical_stimulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_physical_stimulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_modulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_modulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_triggering_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_triggering_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_positive_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_positive_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_unknown_positive_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_positive_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_negative_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_negative_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_unknown_negative_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_negative_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_unknown_physical_stimulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_physical_stimulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_unknown_modulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_modulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_and_gate_and_unknown_triggering_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_and_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_triggering_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_catalysis_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_catalysis_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_unknown_catalysis_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_catalysis_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_inhibition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_inhibition_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_unknown_inhibition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_inhibition_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_physical_stimulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_physical_stimulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_modulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_modulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_triggering_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_triggering_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_positive_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_positive_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_unknown_positive_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_positive_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_negative_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_negative_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_unknown_negative_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_negative_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_unknown_physical_stimulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_physical_stimulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_unknown_modulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_modulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_or_gate_and_unknown_triggering_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_or_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_triggering_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_catalysis_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_catalysis_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_unknown_catalysis_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_catalysis_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_inhibition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_inhibition_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_unknown_inhibition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_inhibition_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_physical_stimulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_physical_stimulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_modulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_modulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_triggering_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_triggering_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_positive_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_positive_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_unknown_positive_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_positive_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_negative_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_negative_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_unknown_negative_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_negative_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_unknown_physical_stimulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_physical_stimulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_unknown_modulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_modulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_not_gate_and_unknown_triggering_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_not_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_triggering_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_catalysis_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_catalysis_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_unknown_catalysis_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_catalysis_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_inhibition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_inhibition_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_unknown_inhibition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_inhibition_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_physical_stimulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_physical_stimulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_modulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_modulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_triggering_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_triggering_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_positive_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_positive_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_unknown_positive_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_positive_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_negative_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_negative_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_unknown_negative_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_negative_influence_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_unknown_physical_stimulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_physical_stimulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_unknown_modulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_modulation_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_reduced_unknown_gate_and_unknown_triggering_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
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
            cls._make_and_add_unknown_gate_from_cd(
                map_=map_,
                cd_element=cd_gate_member,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        )
        # Boolean logic gate modulation is of the form 'si, sj' where si and sj
        # are the ids of its inputs; we replace it by the id of the newly built
        # model element so it can be found when transforming the modulation
        cd_gate_member.aliases = gate_model_element.id
        modifier_model_element, modifier_layout_element = (
            cls._make_and_add_boolean_unknown_triggering_from_cd(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
            )
        )
        return modifier_model_element, modifier_layout_element

    @classmethod
    def _make_and_add_and_gate_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_logic_gate_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.AndGate,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.boolean_logic_gates.add(model_element)
        # we use the id of the model element since the cd element does not have
        # one; this mapping is necessary when building the modification the
        # Boolean gate is the source of
        cd_id_to_model_element[model_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_or_gate_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_logic_gate_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.OrGate,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.boolean_logic_gates.add(model_element)
        # we use the id of the model element since the cd element does not have
        # one; this mapping is necessary when building the modification the
        # Boolean gate is the source of
        cd_id_to_model_element[model_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_not_gate_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_logic_gate_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.NotGate,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.boolean_logic_gates.add(model_element)
        # we use the id of the model element since the cd element does not have
        # one; this mapping is necessary when building the modification the
        # Boolean gate is the source of
        cd_id_to_model_element[model_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_gate_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_logic_gate_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownGate,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.boolean_logic_gates.add(model_element)
        # we use the id of the model element since the cd element does not have
        # one; this mapping is necessary when building the modification the
        # Boolean gate is the source of
        cd_id_to_model_element[model_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_state_transition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_reaction_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.StateTransition,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_known_transition_omitted_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_reaction_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.KnownTransitionOmitted,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_transition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_reaction_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownTransition,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_transcription_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_reaction_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Transcription,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_translation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_reaction_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Translation,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_transport_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_reaction_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Transport,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_heterodimer_association_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_reaction_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.HeterodimerAssociation,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_dissociation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_reaction_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Dissociation,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_truncation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_reaction_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Truncation,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.reactions.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_catalysis_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Catalysis,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_catalysis_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownCatalysis,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_inhibition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Inhibition,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_inhibition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownInhibition,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_physical_stimulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.PhysicalStimulation,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_modulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Modulation,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_triggering_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Triggering,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_positive_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.PositiveInfluence,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_negative_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.NegativeInfluence,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_positive_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownPositiveInfluence,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_negative_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownNegativeInfluence,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_physical_stimulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownPhysicalStimulation,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_modulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownModulation,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_unknown_triggering_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownTriggering,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_catalysis_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Catalysis,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_unknown_catalysis_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownCatalysis,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_inhibition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Inhibition,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_unknown_inhibition_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownInhibition,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_physical_stimulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.PhysicalStimulation,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_modulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Modulation,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_triggering_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.Triggering,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_positive_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.PositiveInfluence,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_unknown_positive_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownPositiveInfluence,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_negative_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.NegativeInfluence,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_unknown_negative_influence_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownNegativeInfluence,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_unknown_physical_stimulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownPhysicalStimulation,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_unknown_modulation_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownModulation,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_and_add_boolean_unknown_triggering_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element, layout_element = cls._make_boolean_modulation_from_cd(
            map_=map_,
            cd_element=cd_element,
            model_element_cls=momapy.celldesigner.core.UnknownTriggering,
            layout_element_cls=None,
            cd_id_to_model_element=cd_id_to_model_element,
            cd_id_to_layout_element=cd_id_to_layout_element,
            cd_id_to_cd_element=cd_id_to_cd_element,
            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
            map_element_to_annotations=map_element_to_annotations,
            super_model_element=super_model_element,
            super_cd_element=super_cd_element,
        )
        map_.model.modulations.add(model_element)
        cd_id_to_model_element[cd_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_species_reference_from_cd(
        cls,
        map_,
        cd_element,
        model_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element = map_.new_model_element(model_element_cls)
        model_element.id = cd_element.id
        model_element.name = cd_element.name
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
                            map_=map_,
                            cd_element=cd_modification_residue,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            map_element_to_annotations=map_element_to_annotations,
                            super_model_element=model_element,
                            super_cd_element=cd_element,
                        )
                    )
        model_element = momapy.builder.object_from_builder(model_element)
        return model_element

    @classmethod
    def _make_species_from_cd(
        cls,
        map_,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        cd_species = cd_id_to_cd_element[cd_element.species]
        model_element = map_.new_model_element(model_element_cls)
        model_element.id = cd_species.id
        model_element.name = cd_species.name
        model_element.metaid = cd_species.metaid
        if cd_species.compartment is not None:
            compartment_model_element = cd_id_to_model_element[
                cd_species.compartment
            ]
            model_element.compartment = compartment_model_element
        cd_species_reference = (
            cls._get_cd_species_reference_from_cd_species_alias(
                cd_element=cd_element, cd_id_to_cd_element=cd_id_to_cd_element
            )
        )
        if cd_species_reference is not None:
            species_reference_model_element = cd_id_to_model_element[
                cd_species_reference.id
            ]
            model_element.reference = species_reference_model_element
        cd_species_identity = cd_species.annotation.extension.species_identity
        cd_species_state = cd_species_identity.state
        if cd_species_state is not None:
            if cd_species_state.homodimer is not None:
                model_element.homomultimer = cd_species_state.homodimer
            if cd_species_state.list_of_modifications is not None:
                for (
                    cd_species_modification
                ) in cd_species_state.list_of_modifications.modification:
                    modification_model_element, modification_layout_element = (
                        cls._make_and_add_elements_from_cd(
                            map_=map_,
                            cd_element=cd_species_modification,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            map_element_to_annotations=map_element_to_annotations,
                            super_model_element=model_element,
                            super_cd_element=cd_element,
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
                    map_=map_,
                    cd_element=cd_species_structural_state,
                    cd_id_to_model_element=cd_id_to_model_element,
                    cd_id_to_layout_element=cd_id_to_layout_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                    cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                    map_element_to_annotations=map_element_to_annotations,
                    super_model_element=model_element,
                    super_cd_element=cd_element,
                )
        model_element.hypothetical = (
            cd_species_identity.hypothetical is True
        )  # in cd, is True or None
        model_element.active = (
            cd_element.activity
            == momapy.celldesigner.io._celldesigner_parser.ActivityValue.ACTIVE
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
                        map_=map_,
                        cd_element=cd_subunit,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        super_model_element=model_element,
                        super_cd_element=cd_element,
                    )
                )
        if cd_species.annotation is not None:
            if cd_species.annotation.rdf is not None:
                annotations = cls._make_annotations_from_cd(
                    cd_species.annotation.rdf
                )
        layout_element = None
        model_element = momapy.builder.object_from_builder(model_element)
        if cd_species.annotation is not None:
            if cd_species.annotation.rdf is not None:
                annotations = cls._make_annotations_from_cd(
                    cd_species.annotation.rdf
                )
                map_element_to_annotations[model_element] = annotations
        return model_element, layout_element

    @classmethod
    def _make_included_species_from_cd(
        cls,
        map_,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        cd_species = cd_id_to_cd_element[cd_element.species]
        model_element = map_.new_model_element(model_element_cls)
        model_element.id = cd_species.id
        model_element.name = cd_species.name
        if cd_species.compartment is not None:
            compartment_model_element = cd_id_to_model_element[
                cd_species.compartment
            ]
            model_element.compartment = compartment_model_element
        cd_species_reference = (
            cls._get_cd_species_reference_from_cd_species_alias(
                cd_element=cd_element, cd_id_to_cd_element=cd_id_to_cd_element
            )
        )
        if cd_species_reference is not None:
            species_reference_model_element = cd_id_to_model_element[
                cd_species_reference.id
            ]
            model_element.reference = species_reference_model_element
        cd_species_identity = cd_species.annotation.species_identity
        cd_species_state = cd_species_identity.state
        if cd_species_state is not None:
            if cd_species_state.homodimer is not None:
                model_element.homomultimer = cd_species_state.homodimer
            if cd_species_state.list_of_modifications is not None:
                for (
                    cd_species_modification
                ) in cd_species_state.list_of_modifications.modification:
                    modification_model_element, modification_layout_element = (
                        cls._make_and_add_elements_from_cd(
                            map_=map_,
                            cd_element=cd_species_modification,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            map_element_to_annotations=map_element_to_annotations,
                            super_model_element=model_element,
                            super_cd_element=cd_element,
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
                    map_=map_,
                    cd_element=cd_species_structural_state,
                    cd_id_to_model_element=cd_id_to_model_element,
                    cd_id_to_layout_element=cd_id_to_layout_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                    cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                    map_element_to_annotations=map_element_to_annotations,
                    super_model_element=model_element,
                    super_cd_element=cd_element,
                )
        model_element.hypothetical = (
            cd_species_identity.hypothetical is True
        )  # in cd, is True or None
        model_element.active = (
            cd_element.activity
            == momapy.celldesigner.io._celldesigner_parser.ActivityValue.ACTIVE
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
                        map_=map_,
                        cd_element=cd_subunit,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        super_model_element=model_element,
                        super_cd_element=cd_element,
                    )
                )
        layout_element = None
        model_element = momapy.builder.object_from_builder(model_element)
        return model_element, layout_element

    @classmethod
    def _make_reaction_from_cd(
        cls,
        map_,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element = map_.new_model_element(model_element_cls)
        model_element.id = cd_element.id
        model_element.reversible = cd_element.reversible
        if cd_element.list_of_reactants is not None:
            for cd_reactant in cd_element.list_of_reactants.species_reference:
                reactant_model_element, reactant_layout_element = (
                    cls._make_and_add_reactant_from_cd(
                        map_=map_,
                        cd_element=cd_reactant,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        super_model_element=model_element,
                        super_cd_element=cd_element,
                    )
                )
        if cd_element.list_of_products is not None:
            for cd_product in cd_element.list_of_products.species_reference:
                product_model_element, product_layout_element = (
                    cls._make_and_add_product_from_cd(
                        map_=map_,
                        cd_element=cd_product,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        super_model_element=model_element,
                        super_cd_element=cd_element,
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
                    momapy.celldesigner.io._celldesigner_parser.ModificationType.BOOLEAN_LOGIC_GATE_AND
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
                        map_=map_,
                        cd_element=cd_modification,
                        cd_id_to_model_element=cd_id_to_model_element,
                        cd_id_to_layout_element=cd_id_to_layout_element,
                        cd_id_to_cd_element=cd_id_to_cd_element,
                        cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                        map_element_to_annotations=map_element_to_annotations,
                        super_model_element=model_element,
                        super_cd_element=cd_element,
                    )
                )
            for cd_modification in cd_normal_modifications:
                if cd_modification.modifiers not in cd_boolean_input_ids:
                    modifier_model_element, modifier_layout_element = (
                        cls._make_and_add_elements_from_cd(
                            map_=map_,
                            cd_element=cd_modification,
                            cd_id_to_model_element=cd_id_to_model_element,
                            cd_id_to_layout_element=cd_id_to_layout_element,
                            cd_id_to_cd_element=cd_id_to_cd_element,
                            cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                            map_element_to_annotations=map_element_to_annotations,
                            super_model_element=model_element,
                            super_cd_element=cd_element,
                        )
                    )
        model_element = momapy.builder.object_from_builder(model_element)
        if cd_element.annotation is not None:
            if cd_element.annotation.rdf is not None:
                annotations = cls._make_annotations_from_cd(
                    cd_element.annotation.rdf
                )
                map_element_to_annotations[model_element].update(annotations)
        layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_modifier_from_cd(
        cls,
        map_,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element = map_.new_model_element(model_element_cls)
        species_model_element = cd_id_to_model_element[cd_element.aliases]
        model_element.species = species_model_element
        layout_element = None
        model_element = momapy.builder.object_from_builder(model_element)
        return model_element, layout_element

    @classmethod
    def _make_modulation_from_cd(
        cls,
        map_,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element = map_.new_model_element(model_element_cls)
        model_element.id = cd_element.id
        if cd_element.list_of_reactants is not None:
            for cd_reactant in cd_element.list_of_reactants.species_reference:
                source_model_element = cd_id_to_model_element[
                    cd_reactant.annotation.extension.alias
                ]
                model_element.source = source_model_element
                break
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
    def _make_boolean_logic_gate_from_cd(
        cls,
        map_,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element,
        super_cd_element=None,
    ):
        model_element = map_.new_model_element(model_element_cls)
        for cd_boolean_input_id in cd_element.aliases.split(","):
            boolean_input_model_element = cd_id_to_model_element[
                cd_boolean_input_id
            ]
            model_element.inputs.add(boolean_input_model_element)
        layout_element = None
        map_.model.boolean_logic_gates.add(model_element)
        # we use the id of the model element since the cd element does not have
        # one; this id is necessary when building the modification the
        # Boolean gate is the source of
        cd_id_to_model_element[model_element.id] = model_element
        return model_element, layout_element

    @classmethod
    def _make_boolean_modulation_from_cd(
        cls,
        map_,
        cd_element,
        model_element_cls,
        layout_element_cls,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        model_element = map_.new_model_element(model_element_cls)
        model_element.id = cd_element.id
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
    def _make_annotations_from_cd(cls, cd_element):
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
    def _get_cd_species_reference_from_cd_species_alias(
        cls, cd_element, cd_id_to_cd_element
    ):
        cd_species = cd_id_to_cd_element[cd_element.species]
        if cd_element.complex_species_alias is None:
            cd_species_identity = (
                cd_species.annotation.extension.species_identity
            )
        else:
            cd_species_identity = cd_species.annotation.species_identity
        cd_species_reference = None
        for cd_species_reference_type in [
            "protein_reference",
            "rna_reference",
            "gene_reference",
            "antisenserna_reference",
        ]:
            if hasattr(
                cd_species_identity,
                cd_species_reference_type,
            ):
                cd_species_reference_id = getattr(
                    cd_species_identity,
                    cd_species_reference_type,
                )
                if cd_species_reference_id is not None:
                    cd_species_reference = cd_id_to_cd_element[
                        cd_species_reference_id
                    ]
                    return cd_species_reference
        return None

    @classmethod
    def _make_and_add_elements_from_cd(
        cls,
        map_,
        cd_element,
        cd_id_to_model_element,
        cd_id_to_layout_element,
        cd_id_to_cd_element,
        cd_complex_alias_id_to_cd_included_species_ids,
        map_element_to_annotations,
        super_model_element=None,
        super_cd_element=None,
    ):
        make_and_add_func = cls._get_make_and_add_func_from_cd(
            cd_element=cd_element, cd_id_to_cd_element=cd_id_to_cd_element
        )
        if make_and_add_func is not None:
            model_element, layout_element = make_and_add_func(
                map_=map_,
                cd_element=cd_element,
                cd_id_to_model_element=cd_id_to_model_element,
                cd_id_to_layout_element=cd_id_to_layout_element,
                cd_id_to_cd_element=cd_id_to_cd_element,
                cd_complex_alias_id_to_cd_included_species_ids=cd_complex_alias_id_to_cd_included_species_ids,
                map_element_to_annotations=map_element_to_annotations,
                super_model_element=super_model_element,
                super_cd_element=super_cd_element,
            )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

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
            cd_species_reference = (
                cls._get_cd_species_reference_from_cd_species_alias(
                    cd_element=cd_element,
                    cd_id_to_cd_element=cd_id_to_cd_element,
                )
            )
            cd_species = cd_id_to_cd_element[cd_element.species]
            if cd_element.complex_species_alias is None:
                cd_class_value = (
                    cd_species.annotation.extension.species_identity.class_value
                )
                if cd_species_reference is not None:
                    key = (
                        cd_class_value,
                        cd_species_reference.type_value,
                    )
                else:
                    key = cd_class_value
            else:
                cd_class_value = (
                    cd_species.annotation.species_identity.class_value
                )
                if cd_species_reference is not None:
                    key = (
                        cd_class_value,
                        cd_species_reference.type_value,
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
