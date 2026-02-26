"""SBGN-ML reader classes."""

import os
import abc
import collections
import typing

import frozendict
import lxml.objectify
import lxml.etree

import momapy.geometry
import momapy.utils
import momapy.core
import momapy.core.mapping
import momapy.core.elements
import momapy.core.layout
import momapy.io.core
import momapy.coloring
import momapy.positioning
import momapy.builder
import momapy.drawing
import momapy.styling
import momapy.sbgn.core
import momapy.sbgn.pd
import momapy.sbgn.af
import momapy.sbml.core
import momapy.sbgn.io.sbgnml._parsing
import momapy.sbgn.io.sbgnml._model
import momapy.sbgn.io.sbgnml._layout

class _SBGNMLReader(momapy.io.core.Reader):
    _KEY_TO_MODULE = {
        "PROCESS_DESCRIPTION": momapy.sbgn.pd,
        "ACTIVITY_FLOW": momapy.sbgn.af,
    }
    _KEY_TO_CLASS = {
        "PROCESS_DESCRIPTION": (
            momapy.sbgn.pd.SBGNPDMap,
            momapy.sbgn.pd.SBGNPDModel,
            momapy.sbgn.pd.SBGNPDLayout,
        ),
        "ACTIVITY_FLOW": (
            momapy.sbgn.af.SBGNAFMap,
            momapy.sbgn.af.SBGNAFModel,
            momapy.sbgn.af.SBGNAFLayout,
        ),
        ("PROCESS_DESCRIPTION", "SUBGLYPH", "STATE_VARIABLE"): (
            momapy.sbgn.pd.StateVariable,
            momapy.sbgn.pd.StateVariableLayout,
        ),
        ("PROCESS_DESCRIPTION", "SUBGLYPH", "UNIT_OF_INFORMATION"): (
            momapy.sbgn.pd.UnitOfInformation,
            momapy.sbgn.pd.UnitOfInformationLayout,
        ),
        ("PROCESS_DESCRIPTION", "SUBGLYPH", "TERMINAL"): (
            momapy.sbgn.pd.Terminal,
            momapy.sbgn.pd.TerminalLayout,
        ),
        ("PROCESS_DESCRIPTION", "SUBGLYPH", "UNSPECIFIED_ENTITY"): (
            momapy.sbgn.pd.UnspecifiedEntitySubunit,
            momapy.sbgn.pd.UnspecifiedEntitySubunitLayout,
        ),
        ("PROCESS_DESCRIPTION", "SUBGLYPH", "MACROMOLECULE"): (
            momapy.sbgn.pd.MacromoleculeSubunit,
            momapy.sbgn.pd.MacromoleculeSubunitLayout,
        ),
        ("PROCESS_DESCRIPTION", "SUBGLYPH", "MACROMOLECULE_MULTIMER"): (
            momapy.sbgn.pd.MacromoleculeMultimerSubunit,
            momapy.sbgn.pd.MacromoleculeMultimerSubunitLayout,
        ),
        ("PROCESS_DESCRIPTION", "SUBGLYPH", "SIMPLE_CHEMICAL"): (
            momapy.sbgn.pd.SimpleChemicalSubunit,
            momapy.sbgn.pd.SimpleChemicalSubunitLayout,
        ),
        ("PROCESS_DESCRIPTION", "SUBGLYPH", "SIMPLE_CHEMICAL_MULTIMER"): (
            momapy.sbgn.pd.SimpleChemicalMultimerSubunit,
            momapy.sbgn.pd.SimpleChemicalMultimerSubunitLayout,
        ),
        ("PROCESS_DESCRIPTION", "SUBGLYPH", "NUCLEIC_ACID_FEATURE"): (
            momapy.sbgn.pd.NucleicAcidFeatureSubunit,
            momapy.sbgn.pd.NucleicAcidFeatureSubunitLayout,
        ),
        ("PROCESS_DESCRIPTION", "SUBGLYPH", "NUCLEIC_ACID_FEATURE_MULTIMER"): (
            momapy.sbgn.pd.NucleicAcidFeatureMultimerSubunit,
            momapy.sbgn.pd.NucleicAcidFeatureMultimerSubunitLayout,
        ),
        ("PROCESS_DESCRIPTION", "SUBGLYPH", "COMPLEX"): (
            momapy.sbgn.pd.ComplexSubunit,
            momapy.sbgn.pd.ComplexSubunitLayout,
        ),
        ("PROCESS_DESCRIPTION", "SUBGLYPH", "COMPLEX_MULTIMER"): (
            momapy.sbgn.pd.ComplexMultimerSubunit,
            momapy.sbgn.pd.ComplexMultimerSubunitLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "COMPARTMENT"): (
            momapy.sbgn.pd.Compartment,
            momapy.sbgn.pd.CompartmentLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "SUBMAP"): (
            momapy.sbgn.pd.Submap,
            momapy.sbgn.pd.SubmapLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "TAG"): (
            momapy.sbgn.pd.Tag,
            momapy.sbgn.pd.TagLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "UNSPECIFIED_ENTITY"): (
            momapy.sbgn.pd.UnspecifiedEntity,
            momapy.sbgn.pd.UnspecifiedEntityLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "MACROMOLECULE"): (
            momapy.sbgn.pd.Macromolecule,
            momapy.sbgn.pd.MacromoleculeLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "MACROMOLECULE_MULTIMER"): (
            momapy.sbgn.pd.MacromoleculeMultimer,
            momapy.sbgn.pd.MacromoleculeMultimerLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "SIMPLE_CHEMICAL"): (
            momapy.sbgn.pd.SimpleChemical,
            momapy.sbgn.pd.SimpleChemicalLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "SIMPLE_CHEMICAL_MULTIMER"): (
            momapy.sbgn.pd.SimpleChemicalMultimer,
            momapy.sbgn.pd.SimpleChemicalMultimerLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "NUCLEIC_ACID_FEATURE"): (
            momapy.sbgn.pd.NucleicAcidFeature,
            momapy.sbgn.pd.NucleicAcidFeatureLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "NUCLEIC_ACID_FEATURE_MULTIMER"): (
            momapy.sbgn.pd.NucleicAcidFeatureMultimer,
            momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "COMPLEX"): (
            momapy.sbgn.pd.Complex,
            momapy.sbgn.pd.ComplexLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "COMPLEX_MULTIMER"): (
            momapy.sbgn.pd.ComplexMultimer,
            momapy.sbgn.pd.ComplexMultimerLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "SOURCE_AND_SINK"): (
            momapy.sbgn.pd.EmptySet,
            momapy.sbgn.pd.EmptySetLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "EMPTY_SET"): (
            momapy.sbgn.pd.EmptySet,
            momapy.sbgn.pd.EmptySetLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "PERTURBING_AGENT"): (
            momapy.sbgn.pd.PerturbingAgent,
            momapy.sbgn.pd.PerturbingAgentLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "PROCESS"): (
            momapy.sbgn.pd.GenericProcess,
            momapy.sbgn.pd.GenericProcessLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "OMITTED_PROCESS"): (
            momapy.sbgn.pd.OmittedProcess,
            momapy.sbgn.pd.OmittedProcessLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "UNCERTAIN_PROCESS"): (
            momapy.sbgn.pd.UncertainProcess,
            momapy.sbgn.pd.UncertainProcessLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "ASSOCIATION"): (
            momapy.sbgn.pd.Association,
            momapy.sbgn.pd.AssociationLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "DISSOCIATION"): (
            momapy.sbgn.pd.Dissociation,
            momapy.sbgn.pd.DissociationLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "PHENOTYPE"): (
            momapy.sbgn.pd.Phenotype,
            momapy.sbgn.pd.PhenotypeLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "AND"): (
            momapy.sbgn.pd.AndOperator,
            momapy.sbgn.pd.AndOperatorLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "OR"): (
            momapy.sbgn.pd.OrOperator,
            momapy.sbgn.pd.OrOperatorLayout,
        ),
        ("PROCESS_DESCRIPTION", "GLYPH", "NOT"): (
            momapy.sbgn.pd.NotOperator,
            momapy.sbgn.pd.NotOperatorLayout,
        ),
        ("PROCESS_DESCRIPTION", "ARC", "MODULATION"): (
            momapy.sbgn.pd.Modulation,
            momapy.sbgn.pd.ModulationLayout,
        ),
        ("PROCESS_DESCRIPTION", "ARC", "STIMULATION"): (
            momapy.sbgn.pd.Stimulation,
            momapy.sbgn.pd.StimulationLayout,
        ),
        ("PROCESS_DESCRIPTION", "ARC", "CATALYSIS"): (
            momapy.sbgn.pd.Catalysis,
            momapy.sbgn.pd.CatalysisLayout,
        ),
        ("PROCESS_DESCRIPTION", "ARC", "NECESSARY_STIMULATION"): (
            momapy.sbgn.pd.NecessaryStimulation,
            momapy.sbgn.pd.NecessaryStimulationLayout,
        ),
        ("PROCESS_DESCRIPTION", "ARC", "INHIBITION"): (
            momapy.sbgn.pd.Inhibition,
            momapy.sbgn.pd.InhibitionLayout,
        ),
        ("PROCESS_DESCRIPTION", "ARC", "CONSUMPTION"): (
            momapy.sbgn.pd.Reactant,
            momapy.sbgn.pd.ConsumptionLayout,
        ),
        ("PROCESS_DESCRIPTION", "ARC", "PRODUCTION"): (
            momapy.sbgn.pd.Product,
            momapy.sbgn.pd.ProductionLayout,
        ),
        ("PROCESS_DESCRIPTION", "ARC", "LOGIC_ARC"): (
            momapy.sbgn.pd.LogicalOperatorInput,
            momapy.sbgn.pd.LogicArcLayout,
        ),
        ("PROCESS_DESCRIPTION", "ARC", "EQUIVALENCE_ARC"): (
            momapy.sbgn.pd.TagReference,
            momapy.sbgn.pd.EquivalenceArcLayout,
        ),
        ("ACTIVITY_FLOW", "SUBGLYPH", "UNIT_OF_INFORMATION_MACROMOLECULE"): (
            momapy.sbgn.af.MacromoleculeUnitOfInformation,
            momapy.sbgn.af.MacromoleculeUnitOfInformationLayout,
        ),
        ("ACTIVITY_FLOW", "SUBGLYPH", "UNIT_OF_INFORMATION_SIMPLE_CHEMICAL"): (
            momapy.sbgn.af.SimpleChemicalUnitOfInformation,
            momapy.sbgn.af.SimpleChemicalUnitOfInformationLayout,
        ),
        (
            "ACTIVITY_FLOW",
            "SUBGLYPH",
            "UNIT_OF_INFORMATION_NUCLEIC_ACID_FEATURE",
        ): (
            momapy.sbgn.af.NucleicAcidFeatureUnitOfInformation,
            momapy.sbgn.af.NucleicAcidFeatureUnitOfInformationLayout,
        ),
        ("ACTIVITY_FLOW", "SUBGLYPH", "UNIT_OF_INFORMATION_COMPLEX"): (
            momapy.sbgn.af.ComplexUnitOfInformation,
            momapy.sbgn.af.ComplexUnitOfInformationLayout,
        ),
        (
            "ACTIVITY_FLOW",
            "SUBGLYPH",
            "UNIT_OF_INFORMATION_UNSPECIFIED_ENTITY",
        ): (
            momapy.sbgn.af.UnspecifiedEntityUnitOfInformation,
            momapy.sbgn.af.UnspecifiedEntityUnitOfInformationLayout,
        ),
        (
            "ACTIVITY_FLOW",
            "SUBGLYPH",
            "UNIT_OF_INFORMATION_PERTURBATION",
        ): (
            momapy.sbgn.af.PerturbationUnitOfInformation,
            momapy.sbgn.af.PerturbationUnitOfInformationLayout,
        ),
        ("ACTIVITY_FLOW", "GLYPH", "COMPARTMENT"): (
            momapy.sbgn.af.Compartment,
            momapy.sbgn.af.CompartmentLayout,
        ),
        ("ACTIVITY_FLOW", "GLYPH", "BIOLOGICAL_ACTIVITY"): (
            momapy.sbgn.af.BiologicalActivity,
            momapy.sbgn.af.BiologicalActivityLayout,
        ),
        ("ACTIVITY_FLOW", "GLYPH", "PHENOTYPE"): (
            momapy.sbgn.af.Phenotype,
            momapy.sbgn.af.PhenotypeLayout,
        ),
        ("ACTIVITY_FLOW", "ARC", "POSITIVE_INFLUENCE"): (
            momapy.sbgn.af.PositiveInfluence,
            momapy.sbgn.af.PositiveInfluenceLayout,
        ),
        ("ACTIVITY_FLOW", "ARC", "NEGATIVE_INFLUENCE"): (
            momapy.sbgn.af.NegativeInfluence,
            momapy.sbgn.af.NegativeInfluenceLayout,
        ),
        ("ACTIVITY_FLOW", "ARC", "UNKNOWN_INFLUENCE"): (
            momapy.sbgn.af.UnknownInfluence,
            momapy.sbgn.af.UnknownInfluenceLayout,
        ),
        ("ACTIVITY_FLOW", "ARC", "NECESSARY_STIMULATION"): (
            momapy.sbgn.af.NecessaryStimulation,
            momapy.sbgn.af.NecessaryStimulationLayout,
        ),
        ("ACTIVITY_FLOW", "SUBGLYPH", "UNIT_OF_INFORMATION"): (
            momapy.sbgn.af.UnitOfInformation,
            momapy.sbgn.af.UnitOfInformationLayout,
        ),
        ("ACTIVITY_FLOW", "GLYPH", "AND"): (
            momapy.sbgn.af.AndOperator,
            momapy.sbgn.af.AndOperatorLayout,
        ),
        ("ACTIVITY_FLOW", "GLYPH", "OR"): (
            momapy.sbgn.af.OrOperator,
            momapy.sbgn.af.OrOperatorLayout,
        ),
        ("ACTIVITY_FLOW", "GLYPH", "NOT"): (
            momapy.sbgn.af.NotOperator,
            momapy.sbgn.af.NotOperatorLayout,
        ),
        ("ACTIVITY_FLOW", "GLYPH", "DELAY"): (
            momapy.sbgn.af.DelayOperator,
            momapy.sbgn.af.DelayOperatorLayout,
        ),
        ("ACTIVITY_FLOW", "ARC", "LOGIC_ARC"): (
            momapy.sbgn.af.LogicalOperatorInput,
            momapy.sbgn.af.LogicArcLayout,
        ),
        ("ACTIVITY_FLOW", "GLYPH", "SUBMAP"): (
            momapy.sbgn.af.Submap,
            momapy.sbgn.af.SubmapLayout,
        ),
        ("ACTIVITY_FLOW", "SUBGLYPH", "TERMINAL"): (
            momapy.sbgn.af.Terminal,
            momapy.sbgn.af.TerminalLayout,
        ),
        ("ACTIVITY_FLOW", "GLYPH", "TAG"): (
            momapy.sbgn.af.Tag,
            momapy.sbgn.af.TagLayout,
        ),
        ("ACTIVITY_FLOW", "ARC", "EQUIVALENCE_ARC"): (
            momapy.sbgn.af.TagReference,
            momapy.sbgn.af.EquivalenceArcLayout,
        ),
    }

    @classmethod
    def read(
        cls,
        file_path: str | os.PathLike,
        return_type: typing.Literal["map", "model", "layout"] = "map",
        with_model: bool = True,
        with_layout: bool = True,
        with_annotations: bool = True,
        with_notes: bool = True,
        with_styles: bool = True,
        xsep: float = 0,
        ysep: float = 0,
    ) -> momapy.io.core.ReaderResult:
        """Read an SBGN-ML file and return a reader result object"""

        sbgnml_document = lxml.objectify.parse(file_path)
        sbgnml_sbgn = sbgnml_document.getroot()
        obj, annotations, notes = cls._make_main_obj_from_sbgnml_map(
            sbgnml_map=sbgnml_sbgn.map,
            return_type=return_type,
            with_model=with_model,
            with_layout=with_layout,
            with_annotations=with_annotations,
            with_notes=with_notes,
            xsep=xsep,
            ysep=ysep,
        )
        result = momapy.io.core.ReaderResult(
            obj=obj,
            notes=notes,
            annotations=annotations,
            file_path=file_path,
        )
        return result

    @classmethod
    @abc.abstractmethod
    def _get_key_from_sbgnml_map(cls, sbgnml_map):
        pass

    @classmethod
    def _get_key_from_sbgnml_glyph(cls, sbgnml_glyph, sbgnml_map):
        sbgnml_map_key = cls._get_key_from_sbgnml_map(sbgnml_map)
        sbgnml_class = momapy.sbgn.io.sbgnml._parsing.transform_sbgnml_class(sbgnml_glyph.get("class"))
        return (
            sbgnml_map_key,
            "GLYPH",
            sbgnml_class,
        )

    @classmethod
    def _get_key_from_sbgnml_subglyph(cls, sbgnml_subglyph, sbgnml_map):
        sbgnml_map_key = cls._get_key_from_sbgnml_map(sbgnml_map)
        sbgnml_class = momapy.sbgn.io.sbgnml._parsing.transform_sbgnml_class(sbgnml_subglyph.get("class"))
        sbgnml_entity = getattr(sbgnml_subglyph, "entity", None)
        if sbgnml_entity is not None:
            sbgnml_entity_class = momapy.sbgn.io.sbgnml._parsing.transform_sbgnml_class(sbgnml_entity.get("name"))
            sbgnml_class = f"{sbgnml_class}_{sbgnml_entity_class}"
        return (
            sbgnml_map_key,
            "SUBGLYPH",
            sbgnml_class,
        )

    @classmethod
    def _get_key_from_sbgnml_arc(cls, sbgnml_arc, sbgnml_map):
        sbgnml_map_key = cls._get_key_from_sbgnml_map(sbgnml_map)
        sbgnml_class = momapy.sbgn.io.sbgnml._parsing.transform_sbgnml_class(sbgnml_arc.get("class"))
        return (
            sbgnml_map_key,
            "ARC",
            sbgnml_class,
        )

    @classmethod
    def _get_module_from_obj(cls, obj):
        if momapy.builder.isinstance_or_builder(
            obj,
            (
                momapy.sbgn.pd.SBGNPDMap,
                momapy.sbgn.pd.SBGNPDModel,
                momapy.sbgn.pd.SBGNPDLayout,
            ),
        ):
            return momapy.sbgn.pd
        if momapy.builder.isinstance_or_builder(
            obj,
            (
                momapy.sbgn.af.SBGNAFMap,
                momapy.sbgn.af.SBGNAFModel,
                momapy.sbgn.af.SBGNAFLayout,
            ),
        ):
            return momapy.sbgn.af
        return None

    @classmethod
    def _get_module_from_sbgnml_map(cls, sbgnml_map):
        key = cls._get_key_from_sbgnml_map(sbgnml_map)
        module = cls._KEY_TO_MODULE[key]
        if module is not None:
            return module
        return None


    @classmethod
    def _make_mappings_and_lists_from_sbgnml_map(cls, sbgnml_map):
        sbgnml_id_to_sbgnml_element = {}
        sbgnml_compartments = []
        sbgnml_entity_pools = []
        sbgnml_logical_operators = []
        sbgnml_stoichiometric_processes = []
        sbgnml_phenotypes = []
        sbgnml_submaps = []
        sbgnml_activities = []
        sbgnml_modulations = []
        sbgnml_tags = []
        sbgnml_phenotypes = []
        sbgnml_glyph_id_to_sbgnml_arcs = collections.defaultdict(list)
        sbgnml_glyph_id_to_sbgnml_state_variables = collections.defaultdict(list)
        sbgnml_glyph_id_to_sbgnml_units_of_information = collections.defaultdict(list)
        sbgnml_glyph_id_to_sbgnml_subunits = collections.defaultdict(list)
        for sbgnml_glyph in momapy.sbgn.io.sbgnml._parsing.get_glyphs_from_sbgnml_element(sbgnml_map):
            sbgnml_id_to_sbgnml_element[sbgnml_glyph.get("id")] = sbgnml_glyph
            key = cls._get_key_from_sbgnml_glyph(sbgnml_glyph, sbgnml_map)
            model_element_cls, _ = cls._KEY_TO_CLASS[key]
            if issubclass(model_element_cls, momapy.sbgn.pd.EntityPool):
                sbgnml_entity_pools.append(sbgnml_glyph)
            elif issubclass(
                model_element_cls,
                cls._get_module_from_sbgnml_map(sbgnml_map).Compartment,
            ):
                sbgnml_compartments.append(sbgnml_glyph)
            elif issubclass(
                model_element_cls,
                cls._get_module_from_sbgnml_map(sbgnml_map).LogicalOperator,
            ):
                sbgnml_logical_operators.append(sbgnml_glyph)
            elif issubclass(
                model_element_cls,
                cls._get_module_from_sbgnml_map(sbgnml_map).Submap,
            ):
                sbgnml_submaps.append(sbgnml_glyph)
            elif issubclass(model_element_cls, momapy.sbgn.pd.StoichiometricProcess):
                sbgnml_stoichiometric_processes.append(sbgnml_glyph)
            elif issubclass(model_element_cls, momapy.sbgn.pd.Phenotype):
                sbgnml_phenotypes.append(sbgnml_glyph)
            elif issubclass(model_element_cls, momapy.sbgn.af.Activity):
                sbgnml_activities.append(sbgnml_glyph)
            elif issubclass(model_element_cls, momapy.sbgn.pd.Tag):
                sbgnml_tags.append(sbgnml_glyph)
            elif issubclass(model_element_cls, momapy.sbgn.pd.Phenotype):
                sbgnml_phenotypes.append(sbgnml_glyph)
            for sbgnml_subglyph in momapy.sbgn.io.sbgnml._parsing.get_glyphs_recursively_from_sbgnml_element(
                sbgnml_glyph
            ):
                sbgnml_id_to_sbgnml_element[sbgnml_subglyph.get("id")] = sbgnml_subglyph
            for sbgnml_port in momapy.sbgn.io.sbgnml._parsing.get_ports_from_sbgnml_element(sbgnml_glyph):
                sbgnml_id_to_sbgnml_element[sbgnml_port.get("id")] = sbgnml_glyph
        for sbgnml_arc in momapy.sbgn.io.sbgnml._parsing.get_arcs_from_sbgnml_element(sbgnml_map):
            sbgnml_id_to_sbgnml_element[sbgnml_arc.get("id")] = sbgnml_arc
            sbgnml_source = sbgnml_id_to_sbgnml_element[sbgnml_arc.get("source")]
            sbgnml_target = sbgnml_id_to_sbgnml_element[sbgnml_arc.get("target")]
            sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_source.get("id")].append(sbgnml_arc)
            sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_target.get("id")].append(sbgnml_arc)
            key = cls._get_key_from_sbgnml_arc(sbgnml_arc, sbgnml_map)
            model_element_cls, _ = cls._KEY_TO_CLASS[key]
            if issubclass(
                model_element_cls,
                (momapy.sbgn.pd.Modulation, momapy.sbgn.af.Influence),
            ):
                sbgnml_modulations.append(sbgnml_arc)
            for sbgnml_subglyph in momapy.sbgn.io.sbgnml._parsing.get_glyphs_from_sbgnml_element(sbgnml_arc):
                sbgnml_id_to_sbgnml_element[sbgnml_subglyph.get("id")] = sbgnml_subglyph
        return (
            sbgnml_id_to_sbgnml_element,
            sbgnml_compartments,
            sbgnml_entity_pools,
            sbgnml_logical_operators,
            sbgnml_stoichiometric_processes,
            sbgnml_phenotypes,
            sbgnml_submaps,
            sbgnml_activities,
            sbgnml_modulations,
            sbgnml_tags,
            sbgnml_phenotypes,
            sbgnml_glyph_id_to_sbgnml_arcs,
            sbgnml_glyph_id_to_sbgnml_state_variables,
            sbgnml_glyph_id_to_sbgnml_units_of_information,
            sbgnml_glyph_id_to_sbgnml_subunits,
        )

    @classmethod
    def _get_state_variables_from_sbgnml_element(cls, sbgnml_element, sbgnml_map):
        sbgnml_state_variables = []
        for sbgnml_subglyph in momapy.sbgn.io.sbgnml._parsing.get_glyphs_from_sbgnml_element(sbgnml_element):
            key = cls._get_key_from_sbgnml_subglyph(sbgnml_subglyph, sbgnml_map)
            model_element_cls, _ = cls._KEY_TO_CLASS[key]
            if issubclass(model_element_cls, momapy.sbgn.pd.StateVariable):
                sbgnml_state_variables.append(sbgnml_subglyph)
        return sbgnml_state_variables

    @classmethod
    def _get_units_of_information_from_sbgnml_element(cls, sbgnml_element, sbgnml_map):
        sbgnml_units_of_information = []
        for sbgnml_subglyph in momapy.sbgn.io.sbgnml._parsing.get_glyphs_from_sbgnml_element(sbgnml_element):
            key = cls._get_key_from_sbgnml_subglyph(sbgnml_subglyph, sbgnml_map)
            model_element_cls, _ = cls._KEY_TO_CLASS[key]
            if issubclass(
                model_element_cls,
                (
                    momapy.sbgn.pd.UnitOfInformation,
                    momapy.sbgn.af.UnitOfInformation,
                ),
            ):
                sbgnml_units_of_information.append(sbgnml_subglyph)
        return sbgnml_units_of_information


    @classmethod
    def _get_subunits_from_sbgnml_element(cls, sbgnml_element, sbgnml_map):
        sbgnml_subunits = []
        for sbgnml_subglyph in momapy.sbgn.io.sbgnml._parsing.get_glyphs_from_sbgnml_element(sbgnml_element):
            key = cls._get_key_from_sbgnml_subglyph(sbgnml_subglyph, sbgnml_map)
            model_element_cls, _ = cls._KEY_TO_CLASS[key]
            if issubclass(model_element_cls, momapy.sbgn.pd.Subunit):
                sbgnml_subunits.append(sbgnml_subglyph)
        return sbgnml_subunits

    @classmethod
    def _get_terminals_from_sbgnml_element(cls, sbgnml_element, sbgnml_map):
        sbgnml_terminals = []
        for sbgnml_subglyph in momapy.sbgn.io.sbgnml._parsing.get_glyphs_from_sbgnml_element(sbgnml_element):
            key = cls._get_key_from_sbgnml_subglyph(sbgnml_subglyph, sbgnml_map)
            model_element_cls, _ = cls._KEY_TO_CLASS[key]
            if issubclass(
                model_element_cls, (momapy.sbgn.pd.Terminal, momapy.sbgn.af.Terminal)
            ):
                sbgnml_terminals.append(sbgnml_subglyph)
        return sbgnml_terminals

    @classmethod
    def _make_map_no_subelements_from_sbgnml_map(cls, sbgnml_map):
        key = cls._get_key_from_sbgnml_map(sbgnml_map)
        map_cls, _, _ = cls._KEY_TO_CLASS[key]
        if map_cls is not None:
            builder_cls = momapy.builder.get_or_make_builder_cls(map_cls)
            return builder_cls()
        raise TypeError("entity relationship maps are not yet supported")

    @classmethod
    def _make_model_no_subelements_from_sbgnml_map(
        cls,
        sbgnml_map,
    ):
        key = cls._get_key_from_sbgnml_map(sbgnml_map)
        _, model_cls, _ = cls._KEY_TO_CLASS[key]
        if model_cls is not None:
            builder_cls = momapy.builder.get_or_make_builder_cls(model_cls)
            return builder_cls()
        raise TypeError("entity relationship maps are not yet supported")

    @classmethod
    def _make_layout_no_subelements_from_sbgnml_map(cls, sbgnml_map):
        key = cls._get_key_from_sbgnml_map(sbgnml_map)
        _, _, layout_cls = cls._KEY_TO_CLASS[key]
        if layout_cls is not None:
            builder_cls = momapy.builder.get_or_make_builder_cls(layout_cls)
            return builder_cls()
        raise TypeError("entity relationship maps are not yet supported")

    @classmethod
    def _make_main_obj_from_sbgnml_map(
        cls,
        sbgnml_map,
        return_type: typing.Literal["map", "model", "layout"],
        with_model: bool = True,
        with_layout: bool = True,
        with_annotations: bool = True,
        with_notes: bool = True,
        with_styles: bool = True,
        xsep: float = 0,
        ysep: float = 0,
    ):
        if return_type == "model" or return_type == "map" and with_model:
            model = cls._make_model_no_subelements_from_sbgnml_map(sbgnml_map)
        else:
            model = None
        if return_type == "layout" or return_type == "map" and with_layout:
            layout = cls._make_layout_no_subelements_from_sbgnml_map(sbgnml_map)
        else:
            layout = None
        if model is not None or layout is not None:
            # We gather sbgnml ids and their correponding elements going in one
            # pass.
            (
                sbgnml_id_to_sbgnml_element,
                sbgnml_compartments,
                sbgnml_entity_pools,
                sbgnml_logical_operators,
                sbgnml_stoichiometric_processes,
                sbgnml_phenotypes,
                sbgnml_submaps,
                sbgnml_activities,
                sbgnml_modulations,
                sbgnml_tags,
                sbgnml_phenotypes,
                sbgnml_glyph_id_to_sbgnml_arcs,
                sbgnml_glyph_id_to_sbgnml_state_variables,
                sbgnml_glyph_id_to_sbgnml_units_of_information,
                sbgnml_glyph_id_to_sbgnml_subunits,
            ) = cls._make_mappings_and_lists_from_sbgnml_map(sbgnml_map)
            sbgnml_id_to_model_element = {}
            sbgnml_id_to_layout_element = {}
            map_element_to_annotations = collections.defaultdict(set)
            map_element_to_notes = collections.defaultdict(set)
            if model is not None and layout is not None:
                layout_model_mapping = momapy.core.mapping.LayoutModelMappingBuilder()
            else:
                layout_model_mapping = None
            # We make model and layout elements from glyphs and arcs; when an arc or
            # a glyph references another sbgnml element, we make the model and
            # layout elements corresponding to that sbgnml element in most cases,
            # and add them to their super model or super layout element accordingly.
            # We make glyphs compartments first as they have to be in the background
            for sbgnml_compartment in sbgnml_compartments:
                model_element, layout_element = (
                    cls._make_and_add_compartment_from_sbgnml_compartment(
                        sbgnml_map=sbgnml_map,
                        sbgnml_compartment=sbgnml_compartment,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
            for sbgnml_entity_pool in sbgnml_entity_pools:
                model_element, layout_element = (
                    cls._make_and_add_entity_pool_from_sbgnml_entity_pool(
                        sbgnml_map=sbgnml_map,
                        sbgnml_entity_pool=sbgnml_entity_pool,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
            for sbgnml_activity in sbgnml_activities:
                model_element, layout_element = (
                    cls._make_and_add_activity_from_sbgnml_activity(
                        sbgnml_map=sbgnml_map,
                        sbgnml_activity=sbgnml_activity,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
            for sbgnml_logical_operator in sbgnml_logical_operators:
                model_element, layout_element = (
                    cls._make_and_add_logical_operator_from_sbgnml_logical_operator(
                        sbgnml_map=sbgnml_map,
                        sbgnml_logical_operator=sbgnml_logical_operator,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
            for sbgnml_submap in sbgnml_submaps:
                model_element, layout_element = (
                    cls._make_and_add_submap_from_sbgnml_submap(
                        sbgnml_map=sbgnml_map,
                        sbgnml_submap=sbgnml_submap,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
            for sbgnml_phenotype in sbgnml_phenotypes:
                model_element, layout_element = (
                    cls._make_and_add_phenotype_from_sbgnml_phenotype(
                        sbgnml_map=sbgnml_map,
                        sbgnml_phenotype=sbgnml_phenotype,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
            for sbgnml_tag in sbgnml_tags:
                model_element, layout_element = cls._make_and_add_tag_from_sbgnml_tag(
                    sbgnml_map=sbgnml_map,
                    sbgnml_tag=sbgnml_tag,
                    model=model,
                    layout=layout,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    map_element_to_annotations=map_element_to_annotations,
                    map_element_to_notes=map_element_to_notes,
                    layout_model_mapping=layout_model_mapping,
                    with_annotations=with_annotations,
                    with_notes=with_notes,
                )
            for sbgnml_process in sbgnml_stoichiometric_processes:
                model_element, layout_element = (
                    cls._make_and_add_stoichiometric_process_from_sbgnml_stroichiometric_process(
                        sbgnml_map=sbgnml_map,
                        sbgnml_process=sbgnml_process,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
            for sbgnml_modulation in sbgnml_modulations:
                model_element, layout_element = (
                    cls._make_and_add_modulation_from_sbgnml_moduation(
                        sbgnml_map=sbgnml_map,
                        sbgnml_modulation=sbgnml_modulation,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
            if layout is not None:
                sbgnml_bbox = getattr(sbgnml_map, "bbox", None)
                if sbgnml_bbox is not None:
                    momapy.sbgn.io.sbgnml._layout.set_layout_element_position_and_size_from_sbgnml_glyph(
                        layout, sbgnml_map
                    )
                else:
                    momapy.positioning.set_fit(
                        layout, layout.layout_elements, xsep=xsep, ysep=ysep
                    )
        # if (
        #     layout is not None
        #     and with_styles
        #     and sbgnml_map.extension is not None
        #     and sbgnml_map.extension.render_information is not None
        # ):
        #     style_sheet = cls._make_style_sheet_from_sbgnml(
        #         layout,
        #         sbgnml_map.extension.render_information,
        #         sbgnml_id_to_layout_element,
        #     )
        #     layout = momapy.styling.apply_style_sheet(layout, style_sheet)
        if return_type == "model":
            obj = momapy.builder.object_from_builder(model)
            # we add the annotations and notes from the map to the model
            if with_annotations:
                annotations = momapy.sbgn.io.sbgnml._parsing.make_annotations_from_sbgnml_element(sbgnml_map)
                if annotations:
                    map_element_to_annotations[obj].update(annotations)
            if with_notes:
                notes = momapy.sbgn.io.sbgnml._parsing.make_notes_from_sbgnml_element(sbgnml_map)
                if notes:
                    map_element_to_notes[obj].update(notes)
        elif return_type == "layout":
            obj = momapy.builder.object_from_builder(layout)
        elif return_type == "map":
            map_ = cls._make_map_no_subelements_from_sbgnml_map(sbgnml_map)
            map_.model = model
            map_.layout = layout
            map_.layout_model_mapping = layout_model_mapping
            obj = momapy.builder.object_from_builder(map_)
            if with_annotations:
                annotations = momapy.sbgn.io.sbgnml._parsing.make_annotations_from_sbgnml_element(sbgnml_map)
                if annotations:
                    map_element_to_annotations[obj].update(annotations)
            if with_notes:
                notes = momapy.sbgn.io.sbgnml._parsing.make_notes_from_sbgnml_element(sbgnml_map)
                if notes:
                    map_element_to_notes[obj].update(notes)
        map_element_to_annotations = frozendict.frozendict(
            {key: frozenset(value) for key, value in map_element_to_annotations.items()}
        )
        map_element_to_notes = frozendict.frozendict(
            {key: frozenset(value) for key, value in map_element_to_notes.items()}
        )
        return obj, map_element_to_annotations, map_element_to_notes

    @classmethod
    def _make_and_add_compartment_from_sbgnml_compartment(
        cls,
        sbgnml_map,
        sbgnml_compartment,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
    ):
        if model is not None or layout is not None:
            if model is not None:
                module = cls._get_module_from_obj(model)
                model_element = momapy.sbgn.io.sbgnml._model.make_model_compartment(
                    sbgnml_compartment=sbgnml_compartment,
                    model=model,
                    module=module,
                )
            else:
                model_element = None
            if layout is not None:
                module = cls._get_module_from_obj(layout)
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_compartment(
                    sbgnml_compartment=sbgnml_compartment,
                    layout=layout,
                    module=module,
                )
            else:
                layout_element = None
            auxiliary_units_map_elements = []
            for (
                sbgnml_unit_of_information
            ) in cls._get_units_of_information_from_sbgnml_element(
                sbgnml_compartment, sbgnml_map
            ):
                (
                    unit_of_information_model_element,
                    unit_of_information_layout_element,
                ) = cls._make_unit_of_information_from_sbgnml_unit_of_information(
                    sbgnml_map=sbgnml_map,
                    sbgnml_unit_of_information=sbgnml_unit_of_information,
                    model=model,
                    layout=layout,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    map_element_to_annotations=map_element_to_annotations,
                    map_element_to_notes=map_element_to_notes,
                    layout_model_mapping=layout_model_mapping,
                    with_annotations=with_annotations,
                    with_notes=with_notes,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                )
                if model is not None:
                    model_element.units_of_information.add(
                        unit_of_information_model_element
                    )
                if layout is not None:
                    layout_element.layout_elements.append(
                        unit_of_information_layout_element
                    )
                if model is not None and layout is not None:
                    auxiliary_units_map_elements.append(
                        (
                            unit_of_information_model_element,
                            unit_of_information_layout_element,
                        )
                    )
            if model is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    model.compartments,
                    func=lambda element, existing_element: element.id_
                    < existing_element.id_,
                )
                sbgnml_id_to_model_element[sbgnml_compartment.get("id")] = model_element
                if with_annotations:
                    annotations = momapy.sbgn.io.sbgnml._parsing.make_annotations_from_sbgnml_element(
                        sbgnml_compartment
                    )
                    if annotations:
                        map_element_to_annotations[model_element].update(annotations)
                if with_notes:
                    notes = momapy.sbgn.io.sbgnml._parsing.make_notes_from_sbgnml_element(sbgnml_compartment)
                    if notes:
                        map_element_to_notes[model_element].update(notes)
            if layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                layout.layout_elements.append(layout_element)
                sbgnml_id_to_layout_element[sbgnml_compartment.get("id")] = (
                    layout_element
                )
            if model is not None and layout is not None:
                for (
                    auxiliary_unit_model_element,
                    auxiliary_unit_layout_element,
                ) in auxiliary_units_map_elements:
                    layout_model_mapping.add_mapping(
                        auxiliary_unit_layout_element,
                        (auxiliary_unit_model_element, model_element),
                        replace=True,
                    )
                layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
                )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_entity_pool_from_sbgnml_entity_pool(
        cls,
        sbgnml_map,
        sbgnml_entity_pool,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
    ):
        model_element, layout_element = (
            cls._make_entity_pool_or_subunit_from_sbgnml_entity_pool_or_sbgnml_subunit(
                sbgnml_map=sbgnml_map,
                sbgnml_entity_pool_or_subunit=sbgnml_entity_pool,
                model=model,
                layout=layout,
                sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                layout_model_mapping=layout_model_mapping,
                with_annotations=with_annotations,
                with_notes=with_notes,
                super_model_element=None,
                super_layout_element=None,
            )
        )
        if model is not None:
            model_element = momapy.utils.add_or_replace_element_in_set(
                model_element,
                model.entity_pools,
                func=lambda element, existing_element: element.id_
                < existing_element.id_,
            )
            sbgnml_id_to_model_element[sbgnml_entity_pool.get("id")] = model_element
            if with_annotations:
                annotations = momapy.sbgn.io.sbgnml._parsing.make_annotations_from_sbgnml_element(
                    sbgnml_entity_pool
                )
                if annotations:
                    map_element_to_annotations[model_element].update(annotations)
            if with_notes:
                notes = momapy.sbgn.io.sbgnml._parsing.make_notes_from_sbgnml_element(sbgnml_entity_pool)
                if notes:
                    map_element_to_notes[model_element].update(notes)
        if layout is not None:
            layout.layout_elements.append(layout_element)
            sbgnml_id_to_layout_element[sbgnml_entity_pool.get("id")] = layout_element
        if model is not None and layout is not None:
            layout_model_mapping.add_mapping(
                layout_element, model_element, replace=True
            )
        return model_element, layout_element

    @classmethod
    def _make_entity_pool_or_subunit_from_sbgnml_entity_pool_or_sbgnml_subunit(
        cls,
        sbgnml_map,
        sbgnml_entity_pool_or_subunit,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
        super_model_element,
        super_layout_element,
    ):
        if model is not None or layout is not None:
            is_subunit = (
                super_model_element is not None or super_layout_element is not None
            )
            if is_subunit:
                key = cls._get_key_from_sbgnml_subglyph(
                    sbgnml_entity_pool_or_subunit, sbgnml_map
                )
            else:
                key = cls._get_key_from_sbgnml_glyph(
                    sbgnml_entity_pool_or_subunit, sbgnml_map
                )
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if model is not None:
                model_element = momapy.sbgn.io.sbgnml._model.make_model_entity_pool_or_subunit(
                    sbgnml_entity_pool_or_subunit=sbgnml_entity_pool_or_subunit,
                    model=model,
                    model_element_cls=model_element_cls,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                )
            else:
                model_element = None
            if layout is not None:
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_entity_pool_or_subunit(
                    sbgnml_entity_pool_or_subunit=sbgnml_entity_pool_or_subunit,
                    layout=layout,
                    layout_element_cls=layout_element_cls,
                )
            else:
                layout_element = None
            auxiliary_units_map_elements = []
            n_undefined_state_variables = 0
            for sbgnml_state_variable in cls._get_state_variables_from_sbgnml_element(
                sbgnml_entity_pool_or_subunit, sbgnml_map
            ):
                if momapy.sbgn.io.sbgnml._parsing.has_sbgnml_state_variable_undefined_variable(
                    sbgnml_state_variable
                ):
                    n_undefined_state_variables += 1
                    order = n_undefined_state_variables
                else:
                    order = None
                state_variable_model_element, state_variable_layout_element = (
                    cls._make_state_variable_from_sbgnml_state_variable(
                        sbgnml_map=sbgnml_map,
                        sbgnml_state_variable=sbgnml_state_variable,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                        order=order,
                    )
                )
                if model is not None:
                    model_element.state_variables.add(state_variable_model_element)
                if layout is not None:
                    layout_element.layout_elements.append(state_variable_layout_element)
                if model is not None and layout is not None:
                    auxiliary_units_map_elements.append(
                        (
                            state_variable_model_element,
                            state_variable_layout_element,
                        )
                    )
            for (
                sbgnml_unit_of_information
            ) in cls._get_units_of_information_from_sbgnml_element(
                sbgnml_entity_pool_or_subunit, sbgnml_map
            ):
                (
                    unit_of_information_model_element,
                    unit_of_information_layout_element,
                ) = cls._make_unit_of_information_from_sbgnml_unit_of_information(
                    sbgnml_map=sbgnml_map,
                    sbgnml_unit_of_information=sbgnml_unit_of_information,
                    model=model,
                    layout=layout,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    map_element_to_annotations=map_element_to_annotations,
                    map_element_to_notes=map_element_to_notes,
                    layout_model_mapping=layout_model_mapping,
                    with_annotations=with_annotations,
                    with_notes=with_notes,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                )
                if model is not None:
                    model_element.units_of_information.add(
                        unit_of_information_model_element
                    )
                if layout is not None:
                    layout_element.layout_elements.append(
                        unit_of_information_layout_element
                    )
                if model is not None and layout is not None:
                    auxiliary_units_map_elements.append(
                        (
                            unit_of_information_model_element,
                            unit_of_information_layout_element,
                        )
                    )
            for sbgnml_subunit in cls._get_subunits_from_sbgnml_element(
                sbgnml_entity_pool_or_subunit, sbgnml_map
            ):
                (
                    subunit_model_element,
                    subunit_layout_element,
                ) = cls._make_entity_pool_or_subunit_from_sbgnml_entity_pool_or_sbgnml_subunit(
                    sbgnml_map=sbgnml_map,
                    sbgnml_entity_pool_or_subunit=sbgnml_subunit,
                    model=model,
                    layout=layout,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    map_element_to_annotations=map_element_to_annotations,
                    map_element_to_notes=map_element_to_notes,
                    layout_model_mapping=layout_model_mapping,
                    with_annotations=with_annotations,
                    with_notes=with_notes,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                )
                if model is not None:
                    model_element.subunits.add(subunit_model_element)
                    sbgnml_id_to_model_element[sbgnml_subunit.get("id")] = (
                        subunit_model_element
                    )
                    if with_annotations:
                        annotations = momapy.sbgn.io.sbgnml._parsing.make_annotations_from_sbgnml_element(
                            sbgnml_subunit
                        )
                        if annotations:
                            map_element_to_annotations[subunit_model_element].update(
                                annotations
                            )
                    if with_notes:
                        notes = momapy.sbgn.io.sbgnml._parsing.make_notes_from_sbgnml_element(sbgnml_subunit)
                        if notes:
                            map_element_to_notes[model_element].update(notes)
                if layout is not None:
                    layout_element.layout_elements.append(subunit_layout_element)
                    sbgnml_id_to_layout_element[sbgnml_subunit.get("id")] = (
                        subunit_layout_element
                    )
                if model is not None and layout is not None:
                    auxiliary_units_map_elements.append(
                        (
                            subunit_model_element,
                            subunit_layout_element,
                        )
                    )
            if model is not None:
                model_element = momapy.builder.object_from_builder(model_element)
            if layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
            if model is not None and layout is not None:
                for (
                    auxiliary_unit_model_element,
                    auxiliary_unit_layout_element,
                ) in auxiliary_units_map_elements:
                    layout_model_mapping.add_mapping(
                        auxiliary_unit_layout_element,
                        (auxiliary_unit_model_element, model_element),
                        replace=True,
                    )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_activity_from_sbgnml_activity(
        cls,
        sbgnml_map,
        sbgnml_activity,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
    ):
        if model is not None or layout is not None:
            key = cls._get_key_from_sbgnml_glyph(sbgnml_activity, sbgnml_map)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if model is not None:
                model_element = momapy.sbgn.io.sbgnml._model.make_model_activity(
                    sbgnml_activity=sbgnml_activity,
                    model=model,
                    model_element_cls=model_element_cls,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                )
            else:
                model_element = None
            if layout is not None:
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_activity(
                    sbgnml_activity=sbgnml_activity,
                    layout=layout,
                    layout_element_cls=layout_element_cls,
                )
            else:
                layout_element = None
            auxiliary_units_map_elements = []
            for (
                sbgnml_unit_of_information
            ) in cls._get_units_of_information_from_sbgnml_element(
                sbgnml_activity, sbgnml_map
            ):
                (
                    unit_of_information_model_element,
                    unit_of_information_layout_element,
                ) = cls._make_unit_of_information_from_sbgnml_unit_of_information(
                    sbgnml_map=sbgnml_map,
                    sbgnml_unit_of_information=sbgnml_unit_of_information,
                    model=model,
                    layout=layout,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    map_element_to_annotations=map_element_to_annotations,
                    map_element_to_notes=map_element_to_notes,
                    layout_model_mapping=layout_model_mapping,
                    with_annotations=with_annotations,
                    with_notes=with_notes,
                    super_model_element=model_element,
                    super_layout_element=layout_element,
                )
                if model is not None:
                    model_element.units_of_information.add(
                        unit_of_information_model_element
                    )
                if layout is not None:
                    layout_element.layout_elements.append(
                        unit_of_information_layout_element
                    )
                if model is not None and layout is not None:
                    auxiliary_units_map_elements.append(
                        (
                            unit_of_information_model_element,
                            unit_of_information_layout_element,
                        )
                    )
            if model is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    model.activities,
                    func=lambda element, existing_element: element.id_
                    < existing_element.id_,
                )
                sbgnml_id_to_model_element[sbgnml_activity.get("id")] = model_element
            if with_annotations:
                annotations = momapy.sbgn.io.sbgnml._parsing.make_annotations_from_sbgnml_element(sbgnml_activity)
                if annotations:
                    map_element_to_annotations[model_element].update(annotations)
            if with_notes:
                notes = momapy.sbgn.io.sbgnml._parsing.make_notes_from_sbgnml_element(sbgnml_activity)
                if notes:
                    map_element_to_notes[model_element].update(notes)
            if layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                layout.layout_elements.append(layout_element)
                sbgnml_id_to_layout_element[sbgnml_activity.get("id")] = layout_element
            if model is not None and layout is not None:
                layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
                )
                for (
                    auxiliary_unit_model_element,
                    auxiliary_unit_layout_element,
                ) in auxiliary_units_map_elements:
                    layout_model_mapping.add_mapping(
                        auxiliary_unit_layout_element,
                        (auxiliary_unit_model_element, model_element),
                        replace=True,
                    )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_state_variable_from_sbgnml_state_variable(
        cls,
        sbgnml_map,
        sbgnml_state_variable,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
        super_model_element,
        super_layout_element,
        order=None,
    ):
        if model is not None or layout is not None:
            if model is not None:
                model_element = momapy.sbgn.io.sbgnml._model.make_model_state_variable(
                    sbgnml_state_variable=sbgnml_state_variable,
                    model=model,
                    order=order,
                )
            else:
                model_element = None
            sbgnml_state = getattr(sbgnml_state_variable, "state", None)
            if sbgnml_state is None:
                text = ""
            else:
                sbgnml_value = sbgnml_state.get("value")
                text = sbgnml_value if sbgnml_value is not None else ""
                sbgnml_variable = sbgnml_state.get("variable")
                if sbgnml_variable is not None:
                    text += f"@{sbgnml_variable}"
            if layout is not None:
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_state_variable(
                    sbgnml_state_variable=sbgnml_state_variable,
                    layout=layout,
                    text=text,
                )
            else:
                layout_element = None
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_unit_of_information_from_sbgnml_unit_of_information(
        cls,
        sbgnml_map,
        sbgnml_unit_of_information,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
        super_model_element,
        super_layout_element,
    ):
        if model is not None or layout is not None:
            key = cls._get_key_from_sbgnml_subglyph(
                sbgnml_unit_of_information, sbgnml_map
            )
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if model is not None:
                model_element = momapy.sbgn.io.sbgnml._model.make_model_unit_of_information(
                    sbgnml_unit_of_information=sbgnml_unit_of_information,
                    model=model,
                    model_element_cls=model_element_cls,
                )
            else:
                model_element = None
            if layout is not None:
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_unit_of_information(
                    sbgnml_unit_of_information=sbgnml_unit_of_information,
                    layout=layout,
                    layout_element_cls=layout_element_cls,
                )
            else:
                layout_element = None
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_submap_from_sbgnml_submap(
        cls,
        sbgnml_map,
        sbgnml_submap,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
    ):
        if model is not None or layout is not None:
            key = cls._get_key_from_sbgnml_glyph(sbgnml_submap, sbgnml_map)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if model is not None:
                model_element = momapy.sbgn.io.sbgnml._model.make_model_submap(
                    sbgnml_submap=sbgnml_submap,
                    model=model,
                    model_element_cls=model_element_cls,
                )
            else:
                model_element = None
            if layout is not None:
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_submap(
                    sbgnml_submap=sbgnml_submap,
                    layout=layout,
                    layout_element_cls=layout_element_cls,
                )
            else:
                layout_element = None
            # We add the terminals
            terminal_map_elements = []
            for sbgnml_terminal in cls._get_terminals_from_sbgnml_element(
                sbgnml_submap, sbgnml_map
            ):
                terminal_model_element, terminal_layout_element = (
                    cls._make_terminal_or_tag_from_sbgnml_terminal_or_tag(
                        sbgnml_map=sbgnml_map,
                        sbgnml_terminal_or_tag=sbgnml_terminal,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        is_terminal=True,
                    )
                )
                if model is not None:
                    model_element.terminals.add(terminal_model_element)
                if layout is not None:
                    layout_element.layout_elements.append(terminal_layout_element)
                if model is not None and layout is not None:
                    terminal_map_elements.append(
                        (terminal_model_element, terminal_layout_element)
                    )
            if model is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    model.submaps,
                    func=lambda element, existing_element: element.id_
                    < existing_element.id_,
                )
                sbgnml_id_to_model_element[sbgnml_submap.get("id")] = model_element
                if with_annotations:
                    annotations = momapy.sbgn.io.sbgnml._parsing.make_annotations_from_sbgnml_element(
                        sbgnml_submap
                    )
                    if annotations:
                        map_element_to_annotations[model_element].update(annotations)
                if with_notes:
                    notes = momapy.sbgn.io.sbgnml._parsing.make_notes_from_sbgnml_element(sbgnml_submap)
                    if notes:
                        map_element_to_notes[model_element].update(notes)
            if layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                layout.layout_elements.append(layout_element)
                sbgnml_id_to_layout_element[sbgnml_submap.get("id")] = layout_element
            if model is not None and layout is not None:
                layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
                )
                for (
                    terminal_model_element,
                    terminal_layout_element,
                ) in terminal_map_elements:
                    layout_model_mapping.add_mapping(
                        terminal_layout_element,
                        (terminal_model_element, model_element),
                        replace=True,
                    )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_terminal_or_tag_from_sbgnml_terminal_or_tag(
        cls,
        sbgnml_map,
        sbgnml_terminal_or_tag,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
        is_terminal,
    ):
        if model is not None or layout is not None:
            if model is not None:
                model_element = momapy.sbgn.io.sbgnml._model.make_model_terminal_or_tag(
                    sbgnml_terminal_or_tag=sbgnml_terminal_or_tag,
                    model=model,
                    is_terminal=is_terminal,
                )
            else:
                model_element = None
            if layout is not None:
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_terminal_or_tag(
                    sbgnml_terminal_or_tag=sbgnml_terminal_or_tag,
                    layout=layout,
                    is_terminal=is_terminal,
                )
            else:
                layout_element = None
            reference_map_elements = []
            for (
                sbgnml_equivalence_arc
            ) in momapy.sbgn.io.sbgnml._parsing.get_sbgnml_equivalence_arcs_from_sbgnml_tag_or_terminal(
                sbgnml_terminal_or_tag,
                sbgnml_id_to_sbgnml_element,
                sbgnml_glyph_id_to_sbgnml_arcs,
            ):
                (
                    reference_model_element,
                    reference_layout_element,
                ) = cls._make_reference_from_sbgnml_equivalence_arc(
                    sbgnml_map=sbgnml_map,
                    sbgnml_equivalence_arc=sbgnml_equivalence_arc,
                    model=model,
                    layout=layout,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                    map_element_to_annotations=map_element_to_annotations,
                    map_element_to_notes=map_element_to_notes,
                    layout_model_mapping=layout_model_mapping,
                    with_annotations=with_annotations,
                    with_notes=with_notes,
                    is_terminal=is_terminal,
                )
                if model is not None:
                    model_element.reference = reference_model_element
                if layout is not None:
                    layout_element.layout_elements.append(reference_layout_element)
                if model is not None and layout is not None:
                    reference_map_elements.append(
                        (reference_model_element, reference_layout_element)
                    )
            if model is not None:
                model_element = momapy.builder.object_from_builder(model_element)
            if layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
            if model is not None and layout is not None:
                for (
                    reference_model_element,
                    reference_layout_element,
                ) in reference_map_elements:
                    layout_model_mapping.add_mapping(
                        reference_layout_element,
                        (reference_model_element, model_element),
                        replace=True,
                    )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_reference_from_sbgnml_equivalence_arc(
        cls,
        sbgnml_map,
        sbgnml_equivalence_arc,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
        is_terminal,
    ):
        if model is not None or layout is not None:
            if model is not None:
                model_element = momapy.sbgn.io.sbgnml._model.make_model_reference(
                    sbgnml_equivalence_arc=sbgnml_equivalence_arc,
                    model=model,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    is_terminal=is_terminal,
                )
            else:
                model_element = None
            if layout is not None:
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_reference(
                    sbgnml_equivalence_arc=sbgnml_equivalence_arc,
                    layout=layout,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                )
            else:
                layout_element = None
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_tag_from_sbgnml_tag(
        cls,
        sbgnml_map,
        sbgnml_tag,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
    ):
        model_element, layout_element = (
            cls._make_terminal_or_tag_from_sbgnml_terminal_or_tag(
                sbgnml_map=sbgnml_map,
                sbgnml_terminal_or_tag=sbgnml_tag,
                model=model,
                layout=layout,
                sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                layout_model_mapping=layout_model_mapping,
                with_annotations=with_annotations,
                with_notes=with_notes,
                is_terminal=False,
            )
        )
        if model is not None:
            model_element = momapy.utils.add_or_replace_element_in_set(
                model_element,
                model.tags,
                func=lambda element, existing_element: element.id_
                < existing_element.id_,
            )
            sbgnml_id_to_model_element[sbgnml_tag.get("id")] = model_element
        if layout is not None:
            layout.layout_elements.append(layout_element)
            sbgnml_id_to_layout_element[sbgnml_tag.get("id")] = layout_element
        if model is not None and layout is not None:
            layout_model_mapping.add_mapping(
                layout_element, model_element, replace=True
            )
        return model_element, layout_element

    @classmethod
    def _make_and_add_phenotype_from_sbgnml_phenotype(
        cls,
        sbgnml_map,
        sbgnml_phenotype,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
    ):
        model_element, layout_element = (
            cls._make_entity_pool_or_subunit_from_sbgnml_entity_pool_or_sbgnml_subunit(
                sbgnml_map=sbgnml_map,
                sbgnml_entity_pool_or_subunit=sbgnml_phenotype,
                model=model,
                layout=layout,
                sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                map_element_to_annotations=map_element_to_annotations,
                map_element_to_notes=map_element_to_notes,
                layout_model_mapping=layout_model_mapping,
                with_annotations=with_annotations,
                with_notes=with_notes,
                super_model_element=None,
                super_layout_element=None,
            )
        )
        if model is not None:
            model_element = momapy.utils.add_or_replace_element_in_set(
                model_element,
                model.processes,
                func=lambda element, existing_element: element.id_
                < existing_element.id_,
            )
            sbgnml_id_to_model_element[sbgnml_phenotype.get("id")] = model_element
            if with_annotations:
                annotations = momapy.sbgn.io.sbgnml._parsing.make_annotations_from_sbgnml_element(
                    sbgnml_phenotype
                )
                if annotations:
                    map_element_to_annotations[model_element].update(annotations)
            if with_notes:
                notes = momapy.sbgn.io.sbgnml._parsing.make_notes_from_sbgnml_element(sbgnml_phenotype)
                if notes:
                    map_element_to_notes[model_element].update(notes)
        if layout is not None:
            layout.layout_elements.append(layout_element)
            sbgnml_id_to_layout_element[sbgnml_phenotype.get("id")] = layout_element
        if model is not None and layout is not None:
            layout_model_mapping.add_mapping(
                layout_element, model_element, replace=True
            )
        return model_element, layout_element

    @classmethod
    def _make_and_add_stoichiometric_process_from_sbgnml_stroichiometric_process(
        cls,
        sbgnml_map,
        sbgnml_process,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
    ):
        if model is not None or layout is not None:
            key = cls._get_key_from_sbgnml_glyph(sbgnml_process, sbgnml_map)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if model is not None:
                model_element = momapy.sbgn.io.sbgnml._model.make_model_stoichiometric_process(
                    sbgnml_process=sbgnml_process,
                    model=model,
                    model_element_cls=model_element_cls,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                )
            else:
                model_element = None
            if layout is not None:
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_stoichiometric_process(
                    sbgnml_process=sbgnml_process,
                    layout=layout,
                    layout_element_cls=layout_element_cls,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                )
            else:
                layout_element = None
            # We add the reactants and products to the model element, and the
            # corresponding layouts to the layout element.
            participant_map_elements = []
            sbgnml_consumption_arcs, sbgnml_production_arcs = (
                momapy.sbgn.io.sbgnml._parsing.get_sbgnml_consumption_and_production_arcs_from_sbgnml_process(
                    sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
                )
            )
            for sbgnml_consumption_arc in sbgnml_consumption_arcs:
                reactant_model_element, reactant_layout_element = (
                    cls._make_reactant_from_sbgnml_consumption_arc(
                        sbgnml_map=sbgnml_map,
                        sbgnml_consumption_arc=sbgnml_consumption_arc,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                        super_sbgnml_element=sbgnml_process,
                    )
                )
                if model is not None:
                    model_element.reactants.add(reactant_model_element)
                if layout is not None:
                    layout_element.layout_elements.append(reactant_layout_element)
                if model is not None and layout is not None:
                    participant_map_elements.append(
                        (reactant_model_element, reactant_layout_element)
                    )
            for sbgnml_production_arc in sbgnml_production_arcs:
                product_model_element, product_layout_element = (
                    cls._make_product_from_sbgnml_production_arc(
                        sbgnml_map=sbgnml_map,
                        sbgnml_production_arc=sbgnml_production_arc,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                        super_sbgnml_element=sbgnml_process,
                    )
                )
                if model_element is not None:
                    model_element.products.add(product_model_element)
                if layout_element is not None:
                    layout_element.layout_elements.append(product_layout_element)
                if model is not None and layout is not None:
                    participant_map_elements.append(
                        (product_model_element, product_layout_element)
                    )
            if model is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    model.processes,
                    func=lambda element, existing_element: element.id_
                    < existing_element.id_,
                )
                sbgnml_id_to_model_element[sbgnml_process.get("id")] = model_element
                if with_annotations:
                    annotations = momapy.sbgn.io.sbgnml._parsing.make_annotations_from_sbgnml_element(
                        sbgnml_process
                    )
                    if annotations:
                        map_element_to_annotations[model_element].update(annotations)
                if with_notes:
                    notes = momapy.sbgn.io.sbgnml._parsing.make_notes_from_sbgnml_element(sbgnml_process)
                    if notes:
                        map_element_to_notes[model_element].update(notes)
            if layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                layout.layout_elements.append(layout_element)
                sbgnml_id_to_layout_element[sbgnml_process.get("id")] = layout_element
            if model is not None and layout is not None:
                layout_model_mapping.add_mapping(
                    frozenset(
                        [layout_element]
                        + [
                            participant_map_element[1]
                            for participant_map_element in participant_map_elements
                        ]
                    ),
                    model_element,
                    replace=True,
                    anchor=layout_element,
                )
                for (
                    participant_model_element,
                    participant_layout_element,
                ) in participant_map_elements:
                    layout_model_mapping.add_mapping(
                        participant_layout_element,
                        (participant_model_element, model_element),
                        replace=True,
                    )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_reactant_from_sbgnml_consumption_arc(
        cls,
        sbgnml_map,
        sbgnml_consumption_arc,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
        super_model_element,
        super_layout_element,
        super_sbgnml_element,
    ):
        if model is not None or layout is not None:
            if model is not None:
                model_element = momapy.sbgn.io.sbgnml._model.make_model_reactant(
                    sbgnml_consumption_arc=sbgnml_consumption_arc,
                    model=model,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                )
            else:
                model_element = None
            if layout is not None:
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_reactant(
                    sbgnml_consumption_arc=sbgnml_consumption_arc,
                    layout=layout,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                )
            else:
                layout_element = None
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_product_from_sbgnml_production_arc(
        cls,
        sbgnml_map,
        sbgnml_production_arc,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
        super_model_element,
        super_layout_element,
        super_sbgnml_element,
    ):
        if model is not None or layout is not None:
            process_direction = momapy.sbgn.io.sbgnml._parsing.get_sbgnml_process_direction(
                    super_sbgnml_element, sbgnml_glyph_id_to_sbgnml_arcs
                )
            if model is not None:
                model_element = momapy.sbgn.io.sbgnml._model.make_model_product(
                    sbgnml_production_arc=sbgnml_production_arc,
                    model=model,
                    sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                    super_model_element=super_model_element,
                    super_sbgnml_element=super_sbgnml_element,
                    process_direction=process_direction,
                )
            else:
                model_element = None
            if layout is not None:
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_product(
                    sbgnml_production_arc=sbgnml_production_arc,
                    layout=layout,
                    sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                )
            else:
                layout_element = None
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_logical_operator_from_sbgnml_logical_operator(
        cls,
        sbgnml_map,
        sbgnml_logical_operator,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
    ):
        if model is not None or layout is not None:
            key = cls._get_key_from_sbgnml_glyph(sbgnml_logical_operator, sbgnml_map)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if model is not None:
                model_element = momapy.sbgn.io.sbgnml._model.make_model_logical_operator(
                    sbgnml_logical_operator=sbgnml_logical_operator,
                    model=model,
                    model_element_cls=model_element_cls,
                )
            else:
                model_element = None
            if layout is not None:
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_logical_operator(
                    sbgnml_logical_operator=sbgnml_logical_operator,
                    layout=layout,
                    layout_element_cls=layout_element_cls,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                )
            else:
                layout_element = None
            input_map_elements = []
            sbgnml_logic_arcs = momapy.sbgn.io.sbgnml._parsing.get_sbgnml_logic_arcs_from_sbgnml_operator(
                sbgnml_operator=sbgnml_logical_operator,
                sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
            )
            for sbgnml_logic_arc in sbgnml_logic_arcs:
                input_model_element, input_layout_element = (
                    cls._make_logical_operator_input_from_sbgnml_logic_arc(
                        sbgnml_map=sbgnml_map,
                        sbgnml_logic_arc=sbgnml_logic_arc,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                        super_sbgnml_element=sbgnml_logical_operator,
                    )
                )
                if model is not None:
                    model_element.inputs.add(input_model_element)
                if layout is not None:
                    layout_element.layout_elements.append(input_layout_element)
                if model is not None and layout is not None:
                    input_map_elements.append(
                        (input_model_element, input_layout_element)
                    )
            if model is not None:
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    model.logical_operators,
                    func=lambda element, existing_element: element.id_
                    < existing_element.id_,
                )
                sbgnml_id_to_model_element[sbgnml_logical_operator.get("id")] = (
                    model_element
                )
            if layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                layout.layout_elements.append(layout_element)
                sbgnml_id_to_layout_element[sbgnml_logical_operator.get("id")] = (
                    layout_element
                )
            if model is not None and layout is not None:
                layout_model_mapping.add_mapping(
                    frozenset(
                        [layout_element]
                        + [
                            input_map_element[1]
                            for input_map_element in input_map_elements
                        ]
                    ),
                    model_element,
                    replace=True,
                    anchor=layout_element,
                )
                for (
                    input_model_element,
                    input_layout_element,
                ) in input_map_elements:
                    layout_model_mapping.add_mapping(
                        input_layout_element,
                        (input_model_element, model_element),
                        replace=True,
                    )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_logical_operator_input_from_sbgnml_logic_arc(
        cls,
        sbgnml_map,
        sbgnml_logic_arc,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
        super_model_element,
        super_layout_element,
        super_sbgnml_element,
    ):
        if model is not None or layout is not None:
            sbgnml_source_id = sbgnml_logic_arc.get("source")
            # We consider that the source can be the port of a logical operator.
            # Moreover this logical operator could have not yet been made
            sbgnml_source_element = sbgnml_id_to_sbgnml_element[sbgnml_source_id]
            sbgnml_source_id = sbgnml_source_element.get("id")
            source_model_element = sbgnml_id_to_model_element.get(sbgnml_source_id)
            source_layout_element = sbgnml_id_to_layout_element.get(sbgnml_source_id)
            if source_model_element is None and source_layout_element is None:
                source_model_element, source_layout_element = (
                    cls._make_and_add_logical_operator_from_sbgnml_logical_operator(
                        sbgnml_map=sbgnml_map,
                        sbgnml_logical_operator=sbgnml_source_element,
                        model=model,
                        layout=layout,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        map_element_to_annotations=map_element_to_annotations,
                        map_element_to_notes=map_element_to_notes,
                        layout_model_mapping=layout_model_mapping,
                        with_annotations=with_annotations,
                        with_notes=with_notes,
                    )
                )
            if model is not None:
                model_element = momapy.sbgn.io.sbgnml._model.make_model_logical_operator_input(
                    sbgnml_logic_arc=sbgnml_logic_arc,
                    model=model,
                    source_model_element=source_model_element,
                )
            else:
                model_element = None
            if layout is not None:
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_logical_operator_input(
                    sbgnml_logic_arc=sbgnml_logic_arc,
                    layout=layout,
                    source_layout_element=source_layout_element,
                )
            else:
                layout_element = None
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_modulation_from_sbgnml_moduation(
        cls,
        sbgnml_map,
        sbgnml_modulation,
        model,
        layout,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        map_element_to_annotations,
        map_element_to_notes,
        layout_model_mapping,
        with_annotations,
        with_notes,
    ):
        if model is not None or layout is not None:
            key = cls._get_key_from_sbgnml_arc(sbgnml_modulation, sbgnml_map)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            sbgnml_source_id = sbgnml_modulation.get("source")
            sbgnml_source_element = sbgnml_id_to_sbgnml_element[sbgnml_source_id]
            sbgnml_source_id = sbgnml_source_element.get("id")
            sbgnml_target_id = sbgnml_modulation.get("target")
            if model is not None:
                source_model_element = sbgnml_id_to_model_element[sbgnml_source_id]
                target_model_element = sbgnml_id_to_model_element[sbgnml_target_id]
                model_element = momapy.sbgn.io.sbgnml._model.make_model_modulation(
                    sbgnml_modulation=sbgnml_modulation,
                    model=model,
                    model_element_cls=model_element_cls,
                    source_model_element=source_model_element,
                    target_model_element=target_model_element,
                )
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    (
                        model.modulations
                        if cls._get_module_from_sbgnml_map(sbgnml_map) == momapy.sbgn.pd
                        else model.influences
                    ),
                    func=lambda element, existing_element: element.id_
                    < existing_element.id_,
                )
                sbgnml_id_to_model_element[sbgnml_modulation.get("id")] = model_element
                if with_annotations:
                    annotations = momapy.sbgn.io.sbgnml._parsing.make_annotations_from_sbgnml_element(
                        sbgnml_modulation
                    )
                    if annotations:
                        map_element_to_annotations[model_element].update(annotations)
                if with_notes:
                    notes = momapy.sbgn.io.sbgnml._parsing.make_notes_from_sbgnml_element(sbgnml_modulation)
                    if notes:
                        map_element_to_notes[model_element].update(notes)
            else:
                model_element = None
            if layout is not None:
                source_layout_element = sbgnml_id_to_layout_element[sbgnml_source_id]
                target_layout_element = sbgnml_id_to_layout_element[sbgnml_target_id]
                layout_element = momapy.sbgn.io.sbgnml._layout.make_layout_modulation(
                    sbgnml_modulation=sbgnml_modulation,
                    layout=layout,
                    layout_element_cls=layout_element_cls,
                    source_layout_element=source_layout_element,
                    target_layout_element=target_layout_element,
                )
                layout.layout_elements.append(layout_element)
                sbgnml_id_to_layout_element[sbgnml_modulation.get("id")] = (
                    layout_element
                )
            else:
                layout_element = None
            if model is not None and layout is not None:
                layout_model_mapping.add_mapping(
                    frozenset(
                        [layout_element, source_layout_element, target_layout_element]
                    ),
                    model_element,
                    replace=True,
                    anchor=layout_element,
                )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_style_sheet_from_sbgnml(
        cls, layout, sbgnml_render_information, sbgnml_id_to_layout_element
    ):
        style_sheet = momapy.styling.StyleSheet()
        if sbgnml_render_information.background_color is not None:
            style_collection = momapy.styling.StyleCollection()
            layout_selector = momapy.styling.IdSelector(layout.id_)
            style_collection["fill"] = momapy.coloring.Color.from_hexa(
                sbgnml_render_information.background_color
            )
            style_sheet[layout_selector] = style_collection
        d_colors = {}
        if sbgnml_render_information.list_of_color_definitions is not None:
            for (
                color_definition
            ) in sbgnml_render_information.list_of_color_definitions.color_definition:
                color_hex = color_definition.value
                if len(color_hex) < 8:
                    color = momapy.coloring.Color.from_hex(color_hex)
                else:
                    color = momapy.coloring.Color.from_hexa(color_hex)
                d_colors[color_definition.id] = color
        if sbgnml_render_information.list_of_styles is not None:
            for style in sbgnml_render_information.list_of_styles.style:
                arc_ids = []
                node_ids = []
                for id_ in style.id_list.split(" "):
                    layout_element = sbgnml_id_to_layout_element.get(id_)
                    if layout_element is not None:
                        if momapy.builder.isinstance_or_builder(
                            layout_element, momapy.sbgn.core.SBGNNode
                        ):
                            node_ids.append(id_)
                        else:
                            arc_ids.append(id_)
                if node_ids:
                    node_style_collection = momapy.styling.StyleCollection()
                    for attr in ["fill", "stroke"]:
                        color_str = getattr(style.g, attr)
                        if color_str is not None:
                            color = d_colors.get(color_str)
                            if color is None:
                                color = momapy.coloring.Color.from_hex(color_str)
                            node_style_collection[attr] = color
                    for attr in ["stroke_width"]:
                        value = getattr(style.g, attr)
                        if value is not None:
                            node_style_collection[attr] = value
                    if node_style_collection:
                        node_selector = momapy.styling.OrSelector(
                            tuple(
                                [
                                    momapy.styling.IdSelector(node_id)
                                    for node_id in node_ids
                                ]
                            )
                        )
                        style_sheet[node_selector] = node_style_collection
                if arc_ids:
                    arc_style_collection = momapy.styling.StyleCollection()
                    for attr in ["fill", "stroke"]:
                        color_str = getattr(style.g, attr)
                        if color_str is not None:
                            color = d_colors.get(color_str)
                            if color is None:
                                color = momapy.coloring.Color.from_hex(color_str)
                            if attr == "stroke":
                                arc_style_collection[f"path_{attr}"] = color
                            arc_style_collection[f"arrowhead_{attr}"] = color
                    for attr in ["stroke_width"]:
                        value = getattr(style.g, attr)
                        if value is not None:
                            arc_style_collection[f"path_{attr}"] = value
                            arc_style_collection[f"arrowhead_{attr}"] = value
                    if arc_style_collection:
                        arc_selector = momapy.styling.OrSelector(
                            tuple([momapy.styling.IdSelector(id) for id in arc_ids])
                        )
                        style_sheet[arc_selector] = arc_style_collection
                label_style_collection = momapy.styling.StyleCollection()
                for attr in ["font_size", "font_family"]:
                    value = getattr(style.g, attr)
                    if value is not None:
                        label_style_collection[attr] = value
                for attr in ["font_color"]:
                    color_str = getattr(style.g, attr)
                    if color_str is not None:
                        color = d_colors.get(color_str)
                        if color is None:
                            if color_str == "#000":
                                color_str = "#000000"
                            color = momapy.coloring.Color.from_hex(color_str)
                        label_style_collection["fill"] = color
                if label_style_collection:
                    if node_ids:
                        node_label_selector = momapy.styling.ChildSelector(
                            node_selector,
                            momapy.styling.TypeSelector(
                                momapy.core.layout.TextLayout.__name__
                            ),
                        )
                        style_sheet[node_label_selector] = label_style_collection
                    if arc_ids:
                        arc_label_selector = momapy.styling.ChildSelector(
                            arc_selector,
                            momapy.styling.TypeSelector(
                                momapy.core.layout.TextLayout.__name__
                            ),
                        )
                        style_sheet[arc_label_selector] = label_style_collection
        return style_sheet


class SBGNML0_2Reader(_SBGNMLReader):
    """Class for SBGN-ML 0.2 reader objects"""

    @classmethod
    def _get_key_from_sbgnml_map(cls, sbgnml_map):
        key = momapy.sbgn.io.sbgnml._parsing.transform_sbgnml_class(sbgnml_map.get("language"))
        return key

    @classmethod
    def check_file(cls, file_path):
        """Return `true` if the given file is an SBGN-ML 0.2 document, `false` otherwise"""
        try:
            with open(file_path) as f:
                for line in f:
                    if "http://sbgn.org/libsbgn/0.2" in line:
                        return True
            return False
        except Exception:
            return False


class SBGNML0_3Reader(_SBGNMLReader):
    """Class for SBGN-ML 0.3 reader objects"""

    @classmethod
    def _get_key_from_sbgnml_map(cls, sbgnml_map):
        sbgnml_version = sbgnml_map.get("version")
        if sbgnml_version is not None:
            if "sbgn.pd" in sbgnml_version:
                return "PROCESS_DESCRIPTION"
            elif "sbgn.af" in sbgnml_version:
                return "ACTIVITY_FLOW"
            elif "sbgn.er" in sbgnml_version:
                return "ENTITY_RELATIONSHIP"
        else:
            return SBGNML0_2Reader._get_key_from_sbgnml_map(sbgnml_map)

    @classmethod
    def check_file(cls, file_path):
        """Return `true` if the given file is an SBGN-ML 0.3 document, `false` otherwise"""
        try:
            with open(file_path) as f:
                for line in f:
                    if "http://sbgn.org/libsbgn/0.3" in line:
                        return True
            return False
        except Exception:
            return False

