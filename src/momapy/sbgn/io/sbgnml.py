"""Classes for reading and writing SBGN-ML files"""

import os
import abc
import collections
import typing

import frozendict
import lxml.objectify
import lxml

import momapy.__about__
import momapy.geometry
import momapy.utils
import momapy.core
import momapy.io
import momapy.coloring
import momapy.positioning
import momapy.builder
import momapy.styling
import momapy.sbgn.core
import momapy.sbgn.pd
import momapy.sbgn.af
import momapy.sbml.core


class _SBGNMLReader(momapy.io.Reader):
    _DEFAULT_FONT_FAMILY = "Helvetica"
    _DEFAULT_FONT_SIZE = 14.0
    _DEFAULT_FONT_FILL = momapy.coloring.black
    _RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
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
            momapy.sbgn.af.NecessaryStimulation,
            momapy.sbgn.af.NecessaryStimulationLayout,
        ),
        ("ACTIVITY_FLOW", "GLYPH", "AND"): (
            momapy.sbgn.af.AndOperator,
            momapy.sbgn.af.AndOperatorLayout,
        ),
        ("ACTIVITY_FLOW", "GLYPH", "OR"): (
            momapy.sbgn.af.AndOperator,
            momapy.sbgn.af.AndOperatorLayout,
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
    ) -> momapy.io.ReaderResult:
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
        result = momapy.io.ReaderResult(
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
        sbgnml_class = cls._transform_sbgnml_class(sbgnml_glyph.get("class"))
        return (
            sbgnml_map_key,
            "GLYPH",
            sbgnml_class,
        )

    @classmethod
    def _get_key_from_sbgnml_subglyph(cls, sbgnml_subglyph, sbgnml_map):
        sbgnml_map_key = cls._get_key_from_sbgnml_map(sbgnml_map)
        sbgnml_class = cls._transform_sbgnml_class(sbgnml_subglyph.get("class"))
        sbgnml_entity = getattr(sbgnml_subglyph, "entity", None)
        if sbgnml_entity is not None:
            sbgnml_entity_class = cls._transform_sbgnml_class(sbgnml_entity.get("name"))
            sbgnml_class = f"{sbgnml_class}_{sbgnml_entity_class}"
        return (
            sbgnml_map_key,
            "SUBGLYPH",
            sbgnml_class,
        )

    @classmethod
    def _get_key_from_sbgnml_arc(cls, sbgnml_arc, sbgnml_map):
        sbgnml_map_key = cls._get_key_from_sbgnml_map(sbgnml_map)
        sbgnml_class = cls._transform_sbgnml_class(sbgnml_arc.get("class"))
        return (
            sbgnml_map_key,
            "ARC",
            sbgnml_class,
        )

    @classmethod
    def _get_module_from_obj(cls, obj):
        if momapy.builder.momapy.builder.isinstance_or_builder(
            obj,
            (
                momapy.sbgn.pd.SBGNPDMap,
                momapy.sbgn.pd.SBGNPDModel,
                momapy.sbgn.pd.SBGNPDLayout,
            ),
        ):
            return momapy.sbgn.pd
        if momapy.builder.momapy.builder.isinstance_or_builder(
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
    def _get_glyphs_from_sbgnml_element(cls, sbgnml_element):
        return list(getattr(sbgnml_element, "glyph", []))

    @classmethod
    def _get_glyphs_recursively_from_sbgnml_element(cls, sbgnml_element):
        sub_glyphs = []
        for sub_glyph in cls._get_glyphs_from_sbgnml_element(sbgnml_element):
            sub_glyphs.append(sub_glyph)
            sub_glyphs += cls._get_glyphs_recursively_from_sbgnml_element(sub_glyph)
        return sub_glyphs

    @classmethod
    def _get_arcs_from_sbgnml_element(cls, sbgnml_element):
        return list(getattr(sbgnml_element, "arc", []))

    @classmethod
    def _get_ports_from_sbgnml_element(cls, sbgnml_element):
        return list(getattr(sbgnml_element, "port", []))

    @classmethod
    def _set_layout_element_position_and_size_from_sbgnml_glyph(
        cls, layout_element, sbgnml_glyph
    ):
        sbgnml_bbox = sbgnml_glyph.bbox
        x = float(sbgnml_bbox.get("x"))
        y = float(sbgnml_bbox.get("y"))
        w = float(sbgnml_bbox.get("w"))
        h = float(sbgnml_bbox.get("h"))
        layout_element.position = momapy.geometry.Point(x + w / 2, y + h / 2)
        layout_element.width = w
        layout_element.height = h

    @classmethod
    def _has_sbgnml_state_variable_undefined_variable(cls, sbgnml_state_variable):
        sbgnml_state = getattr(sbgnml_state_variable, "state", None)
        if sbgnml_state is None:
            return True
        sbgnml_variable = sbgnml_state.get("variable")
        return sbgnml_variable is None

    @classmethod
    def _transform_sbgnml_class(cls, sbgnml_class):
        return sbgnml_class.upper().replace(" ", "_")

    @classmethod
    def _get_sbgnml_consumption_and_production_arcs_from_sbgnml_process(
        cls, sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
    ):
        sbgnml_consumption_arcs = []
        sbgnml_production_arcs = []
        for sbgnml_arc in sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_process.get("id")]:
            if cls._transform_sbgnml_class(sbgnml_arc.get("class")) == "CONSUMPTION":
                sbgnml_consumption_arcs.append(sbgnml_arc)
            elif cls._transform_sbgnml_class(sbgnml_arc.get("class")) == "PRODUCTION":
                sbgnml_production_arcs.append(sbgnml_arc)
        return sbgnml_consumption_arcs, sbgnml_production_arcs

    @classmethod
    def _get_sbgnml_equivalence_arcs_from_sbgnml_tag_or_terminal(
        cls,
        sbgnml_tag_or_terminal,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
    ):
        sbgnml_equivalence_arcs = []
        for sbgnml_arc in sbgnml_glyph_id_to_sbgnml_arcs[
            sbgnml_tag_or_terminal.get("id")
        ]:
            if (
                cls._transform_sbgnml_class(sbgnml_arc.get("class"))
                == "EQUIVALENCE_ARC"
                and sbgnml_id_to_sbgnml_element[sbgnml_arc.get("target")]
                == sbgnml_tag_or_terminal
            ):
                sbgnml_equivalence_arcs.append(sbgnml_arc)
        return sbgnml_equivalence_arcs

    @classmethod
    def _get_sbgnml_logic_arcs_from_sbgnml_operator(
        cls,
        sbgnml_operator,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
    ):
        sbgnml_logic_arcs = []
        for sbgnml_arc in sbgnml_glyph_id_to_sbgnml_arcs[sbgnml_operator.get("id")]:
            if (
                cls._transform_sbgnml_class(sbgnml_arc.get("class")) == "LOGIC_ARC"
                and sbgnml_id_to_sbgnml_element[sbgnml_arc.get("target")]
                == sbgnml_operator
            ):
                sbgnml_logic_arcs.append(sbgnml_arc)
        return sbgnml_logic_arcs

    @classmethod
    def _get_sbgnml_process_direction(
        cls, sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
    ):
        for sbgnml_port in cls._get_ports_from_sbgnml_element(sbgnml_process):
            if float(sbgnml_port.get("x")) < float(
                sbgnml_process.bbox.get("x")
            ) or float(sbgnml_port.get("x")) >= float(
                sbgnml_process.bbox.get("x")
            ) + float(sbgnml_process.bbox.get("w")):  # LEFT OR RIGHT
                return momapy.core.Direction.HORIZONTAL
            else:
                return momapy.core.Direction.VERTICAL
        return momapy.core.Direction.VERTICAL  # default is vertical

    @classmethod
    def _get_direction_from_sbgnml_element(cls, sbgnml_element):
        sbgnml_orientation = sbgnml_element.get("orientation")
        orientation = cls._transform_sbgnml_class(sbgnml_orientation)
        return momapy.core.Direction[orientation]

    @classmethod
    def _is_sbgnml_operator_left_to_right(
        cls,
        sbgnml_operator,
        sbgnml_id_to_sbgnml_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
    ):
        sbgnml_logic_arcs = cls._get_sbgnml_logic_arcs_from_sbgnml_operator(
            sbgnml_operator,
            sbgnml_id_to_sbgnml_element,
            sbgnml_glyph_id_to_sbgnml_arcs,
        )
        operator_direction = cls._get_sbgnml_process_direction(
            sbgnml_operator, sbgnml_glyph_id_to_sbgnml_arcs
        )
        for sbgnml_logic_arc in sbgnml_logic_arcs:
            if operator_direction == momapy.core.Direction.HORIZONTAL:
                if float(sbgnml_logic_arc.end.get("x")) < float(
                    sbgnml_operator.bbox.get("x")
                ):
                    return True
                else:
                    return False
            else:
                if float(sbgnml_logic_arc.end.get("y")) < float(
                    sbgnml_operator.bbox.get("y")
                ):
                    return True
                else:
                    return False
        return True

    @classmethod
    def _is_sbgnml_process_left_to_right(
        cls, sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
    ):
        process_direction = cls._get_sbgnml_process_direction(
            sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
        )
        sbgnml_consumption_arcs, sbgnml_production_arcs = (
            cls._get_sbgnml_consumption_and_production_arcs_from_sbgnml_process(
                sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
            )
        )
        if sbgnml_production_arcs:
            if not sbgnml_production_arcs:  # process is reversible
                return True  # defaults to left to right
            sbgnml_production_arc = sbgnml_production_arcs[0]
            if process_direction == momapy.core.Direction.HORIZONTAL:
                if float(sbgnml_production_arc.start.get("x")) >= float(
                    sbgnml_process.bbox.get("x")
                ):
                    return True
                else:
                    return False
            else:
                if float(sbgnml_production_arc.start.get("y")) >= float(
                    sbgnml_process.bbox.get("y")
                ):
                    return True
                return False
        if sbgnml_consumption_arcs:
            sbgnml_consumption_arc = sbgnml_consumption_arcs[0]
            if process_direction == momapy.core.Direction.HORIZONTAL:
                if float(sbgnml_consumption_arc.end.get("x")) <= float(
                    sbgnml_process.bbox.get("x")
                ):
                    return True
                else:
                    return False
            else:
                if float(sbgnml_consumption_arc.end.get("y")) <= float(
                    sbgnml_process.bbox.get("y")
                ):
                    return True
                return False

    @classmethod
    def _is_sbgnml_process_reversible(
        cls, sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
    ):
        sbgnml_consumption_arcs, sbgnml_consumption_arcs = (
            cls._get_sbgnml_consumption_and_production_arcs_from_sbgnml_process(
                sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
            )
        )
        if sbgnml_consumption_arcs:
            return False
        return True

    @classmethod
    def _get_connectors_length_from_sbgnml_process(cls, sbgnml_process):
        left_connector_length = None
        right_connector_length = None
        sbgnml_bbox = sbgnml_process.bbox
        sbgnml_bbox_x = float(sbgnml_bbox.get("x"))
        sbgnml_bbox_y = float(sbgnml_bbox.get("y"))
        sbgnml_bbox_w = float(sbgnml_bbox.get("w"))
        sbgnml_bbox_h = float(sbgnml_bbox.get("h"))
        for sbgnml_port in cls._get_ports_from_sbgnml_element(sbgnml_process):
            sbgnml_port_x = float(sbgnml_port.get("x"))
            sbgnml_port_y = float(sbgnml_port.get("y"))
            if sbgnml_port_x < sbgnml_bbox_x:  # LEFT
                left_connector_length = sbgnml_bbox_x - sbgnml_port_x
            elif sbgnml_port_y < sbgnml_bbox_y:  # UP
                left_connector_length = sbgnml_bbox_y - sbgnml_port_y
            elif sbgnml_port_x >= sbgnml_bbox_x + sbgnml_bbox_w:  # RIGHT
                right_connector_length = sbgnml_port_x - sbgnml_bbox_x - sbgnml_bbox_w
            elif sbgnml_port_y >= sbgnml_bbox_y + sbgnml_bbox_h:  # DOWN
                right_connector_length = sbgnml_port_y - sbgnml_bbox_y - sbgnml_bbox_h
        return left_connector_length, right_connector_length

    @classmethod
    def _get_nexts_from_sbgnml_arc(cls, sbgnml_arc):
        return list(getattr(sbgnml_arc, "next", []))

    @classmethod
    def _get_sbgnml_points_from_sbgnml_arc(cls, sbgnml_arc):
        return (
            [sbgnml_arc.start]
            + cls._get_nexts_from_sbgnml_arc(sbgnml_arc)
            + [sbgnml_arc.end]
        )

    @classmethod
    def _make_points_from_sbgnml_points(cls, sbgnml_points):
        return [
            momapy.geometry.Point(
                float(sbgnml_point.get("x")), float(sbgnml_point.get("y"))
            )
            for sbgnml_point in sbgnml_points
        ]

    @classmethod
    def _make_segments_from_points(cls, points):
        segments = []
        for current_point, following_point in zip(points[:-1], points[1:]):
            segment = momapy.geometry.Segment(current_point, following_point)
            segments.append(segment)
        return segments

    @classmethod
    def _get_annotation_from_sbgnml_element(cls, sbgnml_element):
        extension = getattr(sbgnml_element, "extension", None)
        if extension is None:
            return None
        annotation = getattr(extension, "annotation", None)
        if annotation is None:
            return getattr(
                extension, "{}annotation", None
            )  # to account for bug in lisbgbn: no namespace
        return annotation

    @classmethod
    def _get_notes_from_sbgnml_element(cls, sbgnml_element):
        notes = getattr(sbgnml_element, "notes", None)
        return notes

    @classmethod
    def _make_notes_from_sbgnml_element(cls, sbgnml_element):
        sbgnml_notes = cls._get_notes_from_sbgnml_element(sbgnml_element)
        if sbgnml_notes is not None:
            for child_element in sbgnml_notes.iterchildren():
                break
            notes = lxml.etree.tostring(child_element)
            return notes
        return []

    @classmethod
    def _get_rdf_from_sbgnml_element(cls, sbgnml_element):
        annotation = cls._get_annotation_from_sbgnml_element(sbgnml_element)
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
    def _get_prefix_and_name_from_tag(cls, tag):
        prefix, name = tag.split("}")
        return prefix[1:], name

    @classmethod
    def _make_annotations_from_sbgnml_rdf(cls, sbgnml_rdf):
        annotations = []
        description = cls._get_description_from_rdf(sbgnml_rdf)
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
    def _make_annotations_from_sbgnml_element(cls, sbgnml_element):
        sbgnml_rdf = cls._get_rdf_from_sbgnml_element(sbgnml_element)
        if sbgnml_rdf is not None:
            annotations = cls._make_annotations_from_sbgnml_rdf(sbgnml_rdf)
        else:
            annotations = []
        return annotations

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
        for sbgnml_glyph in cls._get_glyphs_from_sbgnml_element(sbgnml_map):
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
            for sbgnml_subglyph in cls._get_glyphs_recursively_from_sbgnml_element(
                sbgnml_glyph
            ):
                sbgnml_id_to_sbgnml_element[sbgnml_subglyph.get("id")] = sbgnml_subglyph
            for sbgnml_port in cls._get_ports_from_sbgnml_element(sbgnml_glyph):
                sbgnml_id_to_sbgnml_element[sbgnml_port.get("id")] = sbgnml_glyph
        for sbgnml_arc in cls._get_arcs_from_sbgnml_element(sbgnml_map):
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
            for sbgnml_subglyph in cls._get_glyphs_from_sbgnml_element(sbgnml_arc):
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
        for sbgnml_subglyph in cls._get_glyphs_from_sbgnml_element(sbgnml_element):
            key = cls._get_key_from_sbgnml_subglyph(sbgnml_subglyph, sbgnml_map)
            model_element_cls, _ = cls._KEY_TO_CLASS[key]
            if issubclass(model_element_cls, momapy.sbgn.pd.StateVariable):
                sbgnml_state_variables.append(sbgnml_subglyph)
        return sbgnml_state_variables

    @classmethod
    def _get_units_of_information_from_sbgnml_element(cls, sbgnml_element, sbgnml_map):
        sbgnml_units_of_information = []
        for sbgnml_subglyph in cls._get_glyphs_from_sbgnml_element(sbgnml_element):
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
        for sbgnml_subglyph in cls._get_glyphs_from_sbgnml_element(sbgnml_element):
            key = cls._get_key_from_sbgnml_subglyph(sbgnml_subglyph, sbgnml_map)
            model_element_cls, _ = cls._KEY_TO_CLASS[key]
            if issubclass(model_element_cls, momapy.sbgn.pd.Subunit):
                sbgnml_subunits.append(sbgnml_subglyph)
        return sbgnml_subunits

    @classmethod
    def _get_terminals_from_sbgnml_element(cls, sbgnml_element, sbgnml_map):
        sbgnml_terminals = []
        for sbgnml_subglyph in cls._get_glyphs_from_sbgnml_element(sbgnml_element):
            key = cls._get_key_from_sbgnml_subglyph(sbgnml_subglyph, sbgnml_map)
            model_element_cls, _ = cls._KEY_TO_CLASS[key]
            if issubclass(model_element_cls, momapy.sbgn.pd.Terminal):
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
                layout_model_mapping = momapy.core.LayoutModelMappingBuilder()
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
                    cls._set_layout_element_position_and_size_from_sbgnml_glyph(
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
                annotations = cls._make_annotations_from_sbgnml_element(sbgnml_map)
                if annotations:
                    map_element_to_annotations[obj].update(annotations)
            if with_notes:
                notes = cls._make_notes_from_sbgnml_element(sbgnml_map)
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
                annotations = cls._make_annotations_from_sbgnml_element(sbgnml_map)
                if annotations:
                    map_element_to_annotations[obj].update(annotations)
            if with_notes:
                notes = cls._make_notes_from_sbgnml_element(sbgnml_map)
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
            sbgnml_label = getattr(sbgnml_compartment, "label", None)
            if model is not None:
                model_element = model.new_element(
                    cls._get_module_from_obj(model).Compartment
                )
                model_element.id_ = sbgnml_compartment.get("id")
                if sbgnml_label is not None:
                    model_element.label = sbgnml_label.get("text")
                model_element = momapy.builder.object_from_builder(model_element)
                model_element = momapy.utils.add_or_replace_element_in_set(
                    model_element,
                    model.compartments,
                    func=lambda element, existing_element: element.id_
                    < existing_element.id_,
                )
                sbgnml_id_to_model_element[sbgnml_compartment.get("id")] = model_element
                if with_annotations:
                    annotations = cls._make_annotations_from_sbgnml_element(
                        sbgnml_compartment
                    )
                    if annotations:
                        map_element_to_annotations[model_element].update(annotations)
                if with_notes:
                    notes = cls._make_notes_from_sbgnml_element(sbgnml_compartment)
                    if notes:
                        map_element_to_notes[model_element].update(notes)
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(
                    cls._get_module_from_obj(layout).CompartmentLayout
                )
                layout_element.id_ = sbgnml_compartment.get("id")
                cls._set_layout_element_position_and_size_from_sbgnml_glyph(
                    layout_element, sbgnml_compartment
                )
                if sbgnml_label is not None:
                    text = sbgnml_label.get("text")
                    if text is None:
                        text = ""
                    text_layout = momapy.core.TextLayout(
                        text=text,
                        font_size=cls._DEFAULT_FONT_SIZE,
                        font_family=cls._DEFAULT_FONT_FAMILY,
                        fill=cls._DEFAULT_FONT_FILL,
                        stroke=momapy.drawing.NoneValue,
                        position=layout_element.center(),
                    )
                    layout_element.label = text_layout
                layout_element = momapy.builder.object_from_builder(layout_element)
                layout.layout_elements.append(layout_element)
                sbgnml_id_to_layout_element[sbgnml_compartment.get("id")] = (
                    layout_element
                )
            else:
                layout_element = None
            if model is not None and layout is not None:
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
                annotations = cls._make_annotations_from_sbgnml_element(
                    sbgnml_entity_pool
                )
                if annotations:
                    map_element_to_annotations[model_element].update(annotations)
            if with_notes:
                notes = cls._make_notes_from_sbgnml_element(sbgnml_entity_pool)
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
            sbgnml_label = getattr(sbgnml_entity_pool_or_subunit, "label", None)
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
                model_element = model.new_element(model_element_cls)
                model_element.id_ = sbgnml_entity_pool_or_subunit.get("id")
                sbgnml_compartment_ref = sbgnml_entity_pool_or_subunit.get(
                    "compartmentRef"
                )
                if sbgnml_compartment_ref is not None:
                    compartment_model_element = sbgnml_id_to_model_element[
                        sbgnml_compartment_ref
                    ]
                    model_element.compartment = compartment_model_element
                if sbgnml_label is not None:
                    model_element.label = sbgnml_label.get("text")
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(layout_element_cls)
                layout_element.id_ = sbgnml_entity_pool_or_subunit.get("id")
                cls._set_layout_element_position_and_size_from_sbgnml_glyph(
                    layout_element, sbgnml_entity_pool_or_subunit
                )
                if sbgnml_label is not None:
                    text = sbgnml_label.get("text")
                    if text is None:
                        text = ""
                    text_layout = momapy.core.TextLayout(
                        text=text,
                        font_size=cls._DEFAULT_FONT_SIZE,
                        font_family=cls._DEFAULT_FONT_FAMILY,
                        fill=cls._DEFAULT_FONT_FILL,
                        stroke=momapy.drawing.NoneValue,
                        position=layout_element.label_center(),
                    )
                    layout_element.label = text_layout
            else:
                layout_element = None
            auxiliary_units_map_elements = []
            n_undefined_state_variables = 0
            for sbgnml_state_variable in cls._get_state_variables_from_sbgnml_element(
                sbgnml_entity_pool_or_subunit, sbgnml_map
            ):
                if cls._has_sbgnml_state_variable_undefined_variable(
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
                        annotations = cls._make_annotations_from_sbgnml_element(
                            sbgnml_subunit
                        )
                        if annotations:
                            map_element_to_annotations[subunit_model_element].update(
                                annotations
                            )
                    if with_notes:
                        notes = cls._make_notes_from_sbgnml_element(sbgnml_subunit)
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
            sbgnml_label = getattr(sbgnml_activity, "label", None)
            key = cls._get_key_from_sbgnml_glyph(sbgnml_activity, sbgnml_map)
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if model is not None:
                model_element = model.new_element(model_element_cls)
                model_element.id_ = sbgnml_activity.get("id")
                sbgnml_compartment_ref = sbgnml_activity.get("compartmentRef")
                if sbgnml_compartment_ref is not None:
                    compartment_model_element = sbgnml_id_to_model_element[
                        sbgnml_compartment_ref
                    ]
                    model_element.compartment = compartment_model_element
                if sbgnml_label is not None:
                    model_element.label = sbgnml_label.get("text")
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(layout_element_cls)
                layout_element.id_ = sbgnml_activity.get("id")
                cls._set_layout_element_position_and_size_from_sbgnml_glyph(
                    layout_element, sbgnml_activity
                )
                if sbgnml_label is not None:
                    text = sbgnml_label.get("text")
                    if text is None:
                        text = ""
                    text_layout = momapy.core.TextLayout(
                        text=text,
                        font_size=cls._DEFAULT_FONT_SIZE,
                        font_family=cls._DEFAULT_FONT_FAMILY,
                        fill=cls._DEFAULT_FONT_FILL,
                        stroke=momapy.drawing.NoneValue,
                        position=layout_element.label_center(),
                    )
                    layout_element.label = text_layout
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
                annotations = cls._make_annotations_from_sbgnml_element(sbgnml_activity)
                if annotations:
                    map_element_to_annotations[model_element].update(annotations)
            if with_notes:
                notes = cls._make_notes_from_sbgnml_element(sbgnml_activity)
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
            sbgnml_id = sbgnml_state_variable.get("id")
            sbgnml_state = getattr(sbgnml_state_variable, "state", None)
            if sbgnml_state is None:
                value = None
                variable = None
                text = ""
            else:
                sbgnml_value = sbgnml_state.get("value")
                value = sbgnml_value
                text = sbgnml_value if sbgnml_value is not None else ""
                sbgnml_variable = sbgnml_state.get("variable")
                variable = sbgnml_variable
                if sbgnml_variable is not None:
                    text += f"@{sbgnml_variable}"
            if model is not None:
                # We make the model element
                model_element = model.new_element(momapy.sbgn.pd.StateVariable)
                model_element.id_ = sbgnml_id
                model_element.value = value
                model_element.variable = variable
                model_element.order = order
                model_element = momapy.builder.object_from_builder(model_element)
            else:
                model_element = None
            if layout is not None:
                # We make the layout element
                layout_element = layout.new_element(momapy.sbgn.pd.StateVariableLayout)
                layout_element.id_ = sbgnml_id
                cls._set_layout_element_position_and_size_from_sbgnml_glyph(
                    layout_element, sbgnml_state_variable
                )
                text_layout = momapy.core.TextLayout(
                    text=text,
                    font_size=cls._DEFAULT_FONT_SIZE,
                    font_family=cls._DEFAULT_FONT_FAMILY,
                    fill=cls._DEFAULT_FONT_FILL,
                    stroke=momapy.drawing.NoneValue,
                    position=layout_element.label_center(),
                )
                layout_element.label = text_layout
                layout_element = momapy.builder.object_from_builder(layout_element)
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
            sbgnml_label = getattr(sbgnml_unit_of_information, "label", None)
            sbgnml_id = sbgnml_unit_of_information.get("id")
            key = cls._get_key_from_sbgnml_subglyph(
                sbgnml_unit_of_information, sbgnml_map
            )
            model_element_cls, layout_element_cls = cls._KEY_TO_CLASS[key]
            if model is not None:
                model_element = model.new_element(model_element_cls)
                model_element.id_ = sbgnml_id
                if sbgnml_label is not None:
                    split_label = sbgnml_label.get("text").split(":")
                    model_element.value = split_label[-1]
                    if len(split_label) > 1:
                        model_element.prefix = split_label[0]
                model_element = momapy.builder.object_from_builder(model_element)
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(layout_element_cls)
                layout_element.id_ = sbgnml_id
                cls._set_layout_element_position_and_size_from_sbgnml_glyph(
                    layout_element, sbgnml_unit_of_information
                )
                if sbgnml_label is not None:
                    text_layout = momapy.core.TextLayout(
                        text=sbgnml_label.get("text"),
                        font_size=cls._DEFAULT_FONT_SIZE,
                        font_family=cls._DEFAULT_FONT_FAMILY,
                        fill=cls._DEFAULT_FONT_FILL,
                        stroke=momapy.drawing.NoneValue,
                        position=layout_element.label_center(),
                    )
                    layout_element.label = text_layout
                layout_element = momapy.builder.object_from_builder(layout_element)
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
            sbgnml_id = sbgnml_submap.get("id")
            sbgnml_label = getattr(sbgnml_submap, "label", None)
            if model is not None:
                model_element = model.new_element(model_element_cls)
                if sbgnml_label is not None:
                    model_element.label = sbgnml_label.get("text")
                model_element.id_ = sbgnml_id
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(layout_element_cls)
                layout_element.id_ = sbgnml_id
                cls._set_layout_element_position_and_size_from_sbgnml_glyph(
                    layout_element, sbgnml_submap
                )
                if sbgnml_label is not None:
                    text = sbgnml_label.get("text")
                    if text is None:
                        text = ""
                    text_layout = momapy.core.TextLayout(
                        text=text,
                        font_size=cls._DEFAULT_FONT_SIZE,
                        font_family=cls._DEFAULT_FONT_FAMILY,
                        fill=cls._DEFAULT_FONT_FILL,
                        stroke=momapy.drawing.NoneValue,
                        position=layout_element.center(),
                    )
                    layout_element.label = text_layout
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
                    annotations = cls._make_annotations_from_sbgnml_element(
                        sbgnml_submap
                    )
                    if annotations:
                        map_element_to_annotations[model_element].update(annotations)
                if with_notes:
                    notes = cls._make_notes_from_sbgnml_element(sbgnml_submap)
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
            sbgnml_id = sbgnml_terminal_or_tag.get("id")
            sbgnml_label = getattr(sbgnml_terminal_or_tag, "label", None)
            if model is not None:
                if is_terminal:
                    model_element_cls = momapy.sbgn.pd.Terminal
                else:
                    model_element_cls = momapy.sbgn.pd.Tag
                model_element = model.new_element(model_element_cls)
                model_element.id_ = sbgnml_id
                if sbgnml_label is not None:
                    model_element.label = sbgnml_label.get("text")
            else:
                model_element = None
            if layout is not None:
                if is_terminal:
                    layout_element_cls = momapy.sbgn.pd.TerminalLayout
                else:
                    layout_element_cls = momapy.sbgn.pd.TagLayout
                layout_element = layout.new_element(layout_element_cls)
                layout_element.id_ = sbgnml_id
                cls._set_layout_element_position_and_size_from_sbgnml_glyph(
                    layout_element, sbgnml_terminal_or_tag
                )
                layout_element.direction = cls._get_direction_from_sbgnml_element(
                    sbgnml_terminal_or_tag
                )
                if sbgnml_label is not None:
                    text = sbgnml_label.get("text")
                    if text is None:
                        text = ""
                    text_layout = momapy.core.TextLayout(
                        text=text,
                        font_size=cls._DEFAULT_FONT_SIZE,
                        font_family=cls._DEFAULT_FONT_FAMILY,
                        fill=cls._DEFAULT_FONT_FILL,
                        stroke=momapy.drawing.NoneValue,
                        position=layout_element.label_center(),
                    )
                    layout_element.label = text_layout
            else:
                layout_element = None
            reference_map_elements = []
            for (
                sbgnml_equivalence_arc
            ) in cls._get_sbgnml_equivalence_arcs_from_sbgnml_tag_or_terminal(
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
            sbgnml_id = sbgnml_equivalence_arc.get("id")
            # For terminals and tags, equivalence arc go from the referred node
            # to the terminal or tag. We invert the arc, so that the arc goes
            # from the reference to the referred node.
            sbgnml_target_id = sbgnml_equivalence_arc.get("source")
            if model is not None:
                if is_terminal:
                    model_element_cls = momapy.sbgn.pd.TerminalReference
                else:
                    model_element_cls = momapy.sbgn.pd.TagReference
                model_element = model.new_element(model_element_cls)
                model_element.id_ = sbgnml_id
                target_model_element = sbgnml_id_to_model_element[sbgnml_target_id]
                model_element.element = target_model_element
                model_element = momapy.builder.object_from_builder(model_element)
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(momapy.sbgn.pd.EquivalenceArcLayout)
                layout_element.id_ = sbgnml_id
                sbgnml_points = cls._get_sbgnml_points_from_sbgnml_arc(
                    sbgnml_equivalence_arc
                )
                points = cls._make_points_from_sbgnml_points(sbgnml_points)
                points.reverse()
                segments = cls._make_segments_from_points(points)
                for segment in segments:
                    layout_element.segments.append(segment)
                target_layout_element = sbgnml_id_to_layout_element[sbgnml_target_id]
                layout_element.target = target_layout_element
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
                annotations = cls._make_annotations_from_sbgnml_element(
                    sbgnml_phenotype
                )
                if annotations:
                    map_element_to_annotations[model_element].update(annotations)
            if with_notes:
                notes = cls._make_notes_from_sbgnml_element(sbgnml_phenotype)
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
            sbgnml_id = sbgnml_process.get("id")
            if model is not None:
                model_element = model.new_element(model_element_cls)
                model_element.id_ = sbgnml_id
                model_element.reversible = cls._is_sbgnml_process_reversible(
                    sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
                )
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(layout_element_cls)
                layout_element.id_ = sbgnml_id
                cls._set_layout_element_position_and_size_from_sbgnml_glyph(
                    layout_element, sbgnml_process
                )
                layout_element.direction = cls._get_sbgnml_process_direction(
                    sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
                )
                layout_element.left_to_right = cls._is_sbgnml_process_left_to_right(
                    sbgnml_process, sbgnml_glyph_id_to_sbgnml_arcs
                )
                # We set the length of the connectors using the ports
                left_connector_length, right_connector_length = (
                    cls._get_connectors_length_from_sbgnml_process(sbgnml_process)
                )
                if left_connector_length is not None:
                    layout_element.left_connector_length = left_connector_length
                if right_connector_length is not None:
                    layout_element.right_connector_length = right_connector_length
            else:
                layout_element = None
            # We add the reactants and products to the model element, and the
            # corresponding layouts to the layout element.
            participant_map_elements = []
            sbgnml_consumption_arcs, sbgnml_production_arcs = (
                cls._get_sbgnml_consumption_and_production_arcs_from_sbgnml_process(
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
                    annotations = cls._make_annotations_from_sbgnml_element(
                        sbgnml_process
                    )
                    if annotations:
                        map_element_to_annotations[model_element].update(annotations)
                if with_notes:
                    notes = cls._make_notes_from_sbgnml_element(sbgnml_process)
                    if notes:
                        map_element_to_notes[model_element].update(notes)
            if layout is not None:
                layout_element = momapy.builder.object_from_builder(layout_element)
                layout.layout_elements.append(layout_element)
                sbgnml_id_to_layout_element[sbgnml_process.get("id")] = layout_element
            if model is not None and layout is not None:
                layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
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
            sbgnml_source_id = sbgnml_consumption_arc.get("source")
            if model is not None:
                model_element = model.new_element(momapy.sbgn.pd.Reactant)
                model_element.id_ = sbgnml_consumption_arc.get("id")
                source_model_element = sbgnml_id_to_model_element[sbgnml_source_id]
                model_element.element = source_model_element
                model_element = momapy.builder.object_from_builder(model_element)
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(momapy.sbgn.pd.ConsumptionLayout)
                sbgnml_points = cls._get_sbgnml_points_from_sbgnml_arc(
                    sbgnml_consumption_arc
                )
                # The source becomes the target: in momapy flux arcs go from the process
                # to the entity pool node; this way reversible consumptions can be
                # represented with production layouts. Also, no source
                # (the process layout) is set for the flux arc, so that we do not have a
                # circular definition that would be problematic when building the
                # object.
                sbgnml_points.reverse()
                points = cls._make_points_from_sbgnml_points(sbgnml_points)
                segments = cls._make_segments_from_points(points)
                for segment in segments:
                    layout_element.segments.append(segment)
                source_layout_element = sbgnml_id_to_layout_element[sbgnml_source_id]
                layout_element.target = source_layout_element
                layout_element = momapy.builder.object_from_builder(layout_element)
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
            sbgnml_target_id = sbgnml_production_arc.get("target")
            if model is not None:
                if super_model_element.reversible:
                    process_direction = super_model_element.direction
                    if process_direction == momapy.core.Direction.HORIZONTAL:
                        if float(sbgnml_production_arc.start.get("x")) > float(
                            super_sbgnml_element.bbox.get("x")
                        ):  # RIGHT
                            model_element_cls = momapy.sbgn.pd.Product
                        else:
                            model_element_cls = momapy.sbgn.pd.Reactant  # LEFT
                    else:
                        if float(sbgnml_production_arc.start.get("y")) > float(
                            super_sbgnml_element.bbox.get("y")
                        ):  # TOP
                            model_element_cls = momapy.sbgn.pd.Product
                        else:
                            model_element_cls = momapy.sbgn.pd.Reactant  # BOTTOM
                else:
                    model_element_cls = momapy.sbgn.pd.Product
                model_element = model.new_element(model_element_cls)
                model_element.id_ = sbgnml_production_arc.get("id")
                target_model_element = sbgnml_id_to_model_element[sbgnml_target_id]
                model_element.element = target_model_element
                model_element = momapy.builder.object_from_builder(model_element)
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(momapy.sbgn.pd.ProductionLayout)
                sbgnml_points = cls._get_sbgnml_points_from_sbgnml_arc(
                    sbgnml_production_arc
                )
                # No source (the process layout) is set for the flux arc,
                # so that we do not have a circular definition that would be
                # problematic when building the object.
                points = cls._make_points_from_sbgnml_points(sbgnml_points)
                segments = cls._make_segments_from_points(points)
                for segment in segments:
                    layout_element.segments.append(segment)
                target_layout_element = sbgnml_id_to_layout_element[sbgnml_target_id]
                layout_element.target = target_layout_element
                layout_element = momapy.builder.object_from_builder(layout_element)
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
            sbgnml_id = sbgnml_logical_operator.get("id")
            if model is not None:
                model_element = model.new_element(model_element_cls)
                model_element.id_ = sbgnml_id
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(layout_element_cls)
                layout_element.id_ = sbgnml_id
                cls._set_layout_element_position_and_size_from_sbgnml_glyph(
                    layout_element, sbgnml_logical_operator
                )
                layout_element.direction = cls._get_sbgnml_process_direction(
                    sbgnml_logical_operator, sbgnml_glyph_id_to_sbgnml_arcs
                )
                layout_element.left_to_right = cls._is_sbgnml_operator_left_to_right(
                    sbgnml_operator=sbgnml_logical_operator,
                    sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                    sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                )
                # We set the length of the connectors using the ports
                left_connector_length, right_connector_length = (
                    cls._get_connectors_length_from_sbgnml_process(
                        sbgnml_logical_operator
                    )
                )
                if left_connector_length is not None:
                    layout_element.left_connector_length = left_connector_length
                if right_connector_length is not None:
                    layout_element.right_connector_length = right_connector_length
            else:
                layout_element = None
            input_map_elements = []
            sbgnml_logic_arcs = cls._get_sbgnml_logic_arcs_from_sbgnml_operator(
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
                    layout_element, model_element, replace=True
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
                model_element = model.new_element(momapy.sbgn.pd.LogicalOperatorInput)
                model_element.id_ = sbgnml_logic_arc.get("id")
                model_element.element = source_model_element
                model_element = momapy.builder.object_from_builder(model_element)
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(momapy.sbgn.pd.LogicArcLayout)
                sbgnml_points = cls._get_sbgnml_points_from_sbgnml_arc(sbgnml_logic_arc)
                # The source becomes the target: in momapy logic arcs go from
                # the operator to the input node. Also, no source
                # (the logical operator layout) is set for the logic arc, so
                # that we do not have a circular definition that would be
                # problematic when building the object.
                sbgnml_points.reverse()
                points = cls._make_points_from_sbgnml_points(sbgnml_points)
                segments = cls._make_segments_from_points(points)
                for segment in segments:
                    layout_element.segments.append(segment)
                layout_element.target = source_layout_element
                layout_element = momapy.builder.object_from_builder(layout_element)
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
                model_element = model.new_element(model_element_cls)
                model_element.id_ = sbgnml_modulation.get("id")
                source_model_element = sbgnml_id_to_model_element[sbgnml_source_id]
                target_model_element = sbgnml_id_to_model_element[sbgnml_target_id]
                model_element.source = source_model_element
                model_element.target = target_model_element
                model_element = momapy.builder.object_from_builder(model_element)
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
                    annotations = cls._make_annotations_from_sbgnml_element(
                        sbgnml_modulation
                    )
                    if annotations:
                        map_element_to_annotations[model_element].update(annotations)
                if with_notes:
                    notes = cls._make_notes_from_sbgnml_element(sbgnml_modulation)
                    if notes:
                        map_element_to_notes[model_element].update(notes)
            else:
                model_element = None
            if layout is not None:
                layout_element = layout.new_element(layout_element_cls)
                sbgnml_points = cls._get_sbgnml_points_from_sbgnml_arc(
                    sbgnml_modulation
                )
                points = cls._make_points_from_sbgnml_points(sbgnml_points)
                segments = cls._make_segments_from_points(points)
                for segment in segments:
                    layout_element.segments.append(segment)
                source_layout_element = sbgnml_id_to_layout_element[sbgnml_source_id]
                target_layout_element = sbgnml_id_to_layout_element[sbgnml_target_id]
                layout_element.source = source_layout_element
                layout_element.target = target_layout_element
                layout_element = momapy.builder.object_from_builder(layout_element)
                layout.layout_elements.append(layout_element)
                sbgnml_id_to_layout_element[sbgnml_modulation.get("id")] = (
                    layout_element
                )
            else:
                layout_element = None
            if model is not None and layout is not None:
                layout_model_mapping.add_mapping(
                    layout_element, model_element, replace=True
                )
        else:
            model_element = None
            layout_element = None
        return model_element, layout_element

    @classmethod
    def _make_and_add_biological_activity_from_sbgnml(
        cls,
        model,
        layout,
        sbgnml_element,
        sbgnml_id_to_sbgnml_element,
        sbgnml_id_to_model_element,
        sbgnml_id_to_layout_element,
        sbgnml_glyph_id_to_sbgnml_arcs,
        sbgnml_id_super_sbgnml_id_for_mapping,
        sbgnml_id_to_annotations,
        sbgnml_id_to_notes,
        super_sbgnml_element=None,
        super_model_element=None,
        super_layout_element=None,
        order=None,
        with_annotations=True,
        with_notes=True,
    ):
        if model is not None:
            model_element = model.new_element(momapy.sbgn.af.BiologicalActivity)
            model_element.id_ = cls._make_model_element_id_from_sbgnml(sbgnml_element)
            if sbgnml_element.compartment_ref is not None:
                compartment_model_element = sbgnml_id_to_model_element.get(
                    sbgnml_element.compartment_ref
                )
                if compartment_model_element is None:
                    sbgnml_compartment = sbgnml_id_to_sbgnml_element[
                        sbgnml_element.compartment_ref
                    ]
                    compartment_model_element, _ = (
                        cls._make_and_add_elements_from_sbgnml(
                            model=model,
                            layout=layout,
                            sbgnml_element=sbgnml_compartment,
                            sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                            sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                            sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                            sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                            sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                            sbgnml_id_to_annotations=sbgnml_id_to_annotations,
                            sbgnml_id_to_notes=sbgnml_id_to_notes,
                            super_sbgnml_element=super_sbgnml_element,
                            super_model_element=super_model_element,
                            super_layout_element=super_layout_element,
                            order=order,
                            with_annotations=with_annotations,
                            with_notes=with_notes,
                        )
                    )
                model_element.compartment = compartment_model_element
            if (
                sbgnml_element.label is not None
                and sbgnml_element.label.text is not None
            ):
                model_element.label = sbgnml_element.label.text
        else:
            model_element = None
        if layout is not None:
            layout_element = layout.new_element(momapy.sbgn.af.BiologicalActivityLayout)
            layout_element.id_ = sbgnml_element.id
            position = cls._make_position_from_sbgnml(sbgnml_element=sbgnml_element)
            layout_element.position = position
            layout_element.width = sbgnml_element.bbox.w
            layout_element.height = sbgnml_element.bbox.h
            if (
                sbgnml_element.label is not None
                and sbgnml_element.label.text is not None
            ):
                text_layout = cls._make_text_layout_from_sbgnml(
                    sbgnml_label=sbgnml_element.label, position=position
                )
                layout_element.label = text_layout
        else:
            layout_element = None
        if model is not None or layout is not None:
            # We make and add the state variables, units of information, and
            # subunits to the model and layout elements.
            for sbgnml_sub_element in sbgnml_element.glyph:
                sub_model_element, sub_layout_element = (
                    cls._make_and_add_elements_from_sbgnml(
                        model=model,
                        layout=layout,
                        sbgnml_element=sbgnml_sub_element,
                        sbgnml_id_to_sbgnml_element=sbgnml_id_to_sbgnml_element,
                        sbgnml_id_to_model_element=sbgnml_id_to_model_element,
                        sbgnml_id_to_layout_element=sbgnml_id_to_layout_element,
                        sbgnml_glyph_id_to_sbgnml_arcs=sbgnml_glyph_id_to_sbgnml_arcs,
                        sbgnml_id_super_sbgnml_id_for_mapping=sbgnml_id_super_sbgnml_id_for_mapping,
                        sbgnml_id_to_annotations=sbgnml_id_to_annotations,
                        sbgnml_id_to_notes=sbgnml_id_to_notes,
                        super_sbgnml_element=sbgnml_element,
                        super_model_element=model_element,
                        super_layout_element=layout_element,
                        order=None,
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
            sbgnml_id_to_model_element[sbgnml_element.id] = model_element
        if layout is not None:
            layout_element = momapy.builder.object_from_builder(layout_element)
            layout.layout_elements.append(layout_element)
            sbgnml_id_to_layout_element[sbgnml_element.id] = layout_element
        if model is not None and layout is not None:
            sbgnml_id_super_sbgnml_id_for_mapping.append((sbgnml_element.id, None))
        if (
            with_annotations
            and sbgnml_element.extension is not None
            and sbgnml_element.extension.annotation is not None
        ):
            annotations = cls._make_annotations_from_sbgnml(
                sbgnml_element.extension.annotation
            )
            sbgnml_id_to_annotations[sbgnml_element.id] = annotations
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
                                momapy.core.TextLayout.__name__
                            ),
                        )
                        style_sheet[node_label_selector] = label_style_collection
                    if arc_ids:
                        arc_label_selector = momapy.styling.ChildSelector(
                            arc_selector,
                            momapy.styling.TypeSelector(
                                momapy.core.TextLayout.__name__
                            ),
                        )
                        style_sheet[arc_label_selector] = label_style_collection
        return style_sheet


class SBGNML0_2Reader(_SBGNMLReader):
    """Class for SBGN-ML 0.2 reader objects"""

    @classmethod
    def _get_key_from_sbgnml_map(cls, sbgnml_map):
        key = cls._transform_sbgnml_class(sbgnml_map.get("language"))
        return key

    @classmethod
    def check_file(cls, file_path):
        """Return `true` if the given file is an SBGN-ML 0.2 document, `false` otherwise"""
        with open(file_path) as f:
            for line in f:
                if "http://sbgn.org/libsbgn/0.2" in line:
                    return True
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
        with open(file_path) as f:
            for line in f:
                if "http://sbgn.org/libsbgn/0.3" in line:
                    return True
        return False


class _SBGNMLWriter(momapy.io.Writer):
    _NSMAP = {
        None: "http://sbgn.org/libsbgn/0.3",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "bqmodel": "http://biomodels.net/model-qualifiers/",
        "bqbiol": "http://biomodels.net/biology-qualifiers/",
    }
    _DIRECTION_TO_SBGNML_ORIENTATION = {
        momapy.core.Direction.HORIZONTAL: "horizontal",
        momapy.core.Direction.VERTICAL: "vertical",
        momapy.core.Direction.RIGHT: "right",
        momapy.core.Direction.LEFT: "left",
        momapy.core.Direction.DOWN: "down",
        momapy.core.Direction.UP: "up",
    }
    _CLASS_TO_SBGNML_CLASS_ATTRIBUTE = {
        momapy.sbgn.pd.SBGNPDMap: "process description",
        momapy.sbgn.pd.SBGNPDModel: "process description",
        momapy.sbgn.pd.SBGNPDLayout: "process description",
        momapy.sbgn.pd.StateVariableLayout: "state variable",
        momapy.sbgn.pd.UnitOfInformationLayout: "unit of information",
        momapy.sbgn.pd.UnspecifiedEntityLayout: "unspecified entity",
        momapy.sbgn.pd.TerminalLayout: "terminal",
        momapy.sbgn.pd.MacromoleculeSubunitLayout: "macromolecule",
        momapy.sbgn.pd.SimpleChemicalSubunitLayout: "simple chemical",
        momapy.sbgn.pd.NucleicAcidFeatureSubunitLayout: "nucleic acid feature",
        momapy.sbgn.pd.ComplexSubunitLayout: "complex",
        momapy.sbgn.pd.MacromoleculeMultimerSubunitLayout: "macromolecule multimer",
        momapy.sbgn.pd.SimpleChemicalMultimerSubunitLayout: "simple chemical multimer",
        momapy.sbgn.pd.NucleicAcidFeatureMultimerSubunitLayout: "nucleic acid feature multimer",
        momapy.sbgn.pd.ComplexMultimerSubunitLayout: "complex multimer",
        momapy.sbgn.pd.CompartmentLayout: "compartment",
        momapy.sbgn.pd.SubmapLayout: "submap",
        momapy.sbgn.pd.UnspecifiedEntityLayout: "unspecified entity",
        momapy.sbgn.pd.MacromoleculeLayout: "macromolecule",
        momapy.sbgn.pd.SimpleChemicalLayout: "simple chemical",
        momapy.sbgn.pd.NucleicAcidFeatureLayout: "nucleic acid feature",
        momapy.sbgn.pd.ComplexLayout: "complex",
        momapy.sbgn.pd.MacromoleculeMultimerLayout: "macromolecule multimer",
        momapy.sbgn.pd.SimpleChemicalMultimerLayout: "simple chemical multimer",
        momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout: "nucleic acid feature multimer",
        momapy.sbgn.pd.ComplexMultimerLayout: "complex multimer",
        momapy.sbgn.pd.PerturbingAgentLayout: "perturbing agent",
        momapy.sbgn.pd.EmptySetLayout: "empty set",
        momapy.sbgn.pd.TagLayout: "tag",
        momapy.sbgn.pd.GenericProcessLayout: "process",
        momapy.sbgn.pd.UncertainProcessLayout: "uncertain process",
        momapy.sbgn.pd.OmittedProcessLayout: "omitted process",
        momapy.sbgn.pd.AssociationLayout: "association",
        momapy.sbgn.pd.DissociationLayout: "dissociation",
        momapy.sbgn.pd.PhenotypeLayout: "phenotype",
        momapy.sbgn.pd.AndOperatorLayout: "and operator",
        momapy.sbgn.pd.OrOperatorLayout: "or operator",
        momapy.sbgn.pd.NotOperatorLayout: "not operator",
        momapy.sbgn.pd.EquivalenceOperatorLayout: "equivalence operator",
        momapy.sbgn.pd.ConsumptionLayout: "consumption",
        momapy.sbgn.pd.ProductionLayout: "production",
        momapy.sbgn.pd.ModulationLayout: "modulation",
        momapy.sbgn.pd.StimulationLayout: "stimulation",
        momapy.sbgn.pd.CatalysisLayout: "catalysis",
        momapy.sbgn.pd.NecessaryStimulationLayout: "necessary stimulation",
        momapy.sbgn.pd.InhibitionLayout: "inhibition",
        momapy.sbgn.pd.LogicArcLayout: "logic arc",
        momapy.sbgn.pd.EquivalenceArcLayout: "equivalence arc",
        momapy.sbgn.af.CompartmentLayout: "compartment",
        momapy.sbgn.af.SubmapLayout: "submap",
        momapy.sbgn.af.BiologicalActivityLayout: "biological activity",
        momapy.sbgn.af.UnspecifiedEntityUnitOfInformationLayout: "unspecified entity",
        momapy.sbgn.af.MacromoleculeUnitOfInformationLayout: "macromolecule",
        momapy.sbgn.af.SimpleChemicalUnitOfInformationLayout: "simple chemical",
        momapy.sbgn.af.NucleicAcidFeatureUnitOfInformationLayout: "nucleic acid feature",
        momapy.sbgn.af.ComplexUnitOfInformationLayout: "complex",
        momapy.sbgn.af.PerturbationUnitOfInformationLayout: "perturbation",
        momapy.sbgn.af.PhenotypeLayout: "phenotype",
        momapy.sbgn.af.AndOperatorLayout: "and",
        momapy.sbgn.af.OrOperatorLayout: "or",
        momapy.sbgn.af.NotOperatorLayout: "not",
        momapy.sbgn.af.DelayOperatorLayout: "delay",
        momapy.sbgn.af.UnknownInfluenceLayout: "unknown influence",
        momapy.sbgn.af.PositiveInfluenceLayout: "positive influence",
        momapy.sbgn.af.NecessaryStimulationLayout: "necessary stimulation",
        momapy.sbgn.af.NegativeInfluenceLayout: "negative influence",
        momapy.sbgn.af.TerminalLayout: "terminal",
        momapy.sbgn.af.TagLayout: "tag",
        momapy.sbgn.af.LogicArcLayout: "logic arc",
        momapy.sbgn.af.EquivalenceArcLayout: "equivalence arc",
    }
    _QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE = {
        momapy.sbml.core.BQBiol.ENCODES: (
            "http://biomodels.net/biology-qualifiers/",
            "encodes",
        ),
        momapy.sbml.core.BQBiol.HAS_PART: (
            "http://biomodels.net/biology-qualifiers/",
            "hasPart",
        ),
        momapy.sbml.core.BQBiol.HAS_PROPERTY: (
            "http://biomodels.net/biology-qualifiers/",
            "hasProperty",
        ),
        momapy.sbml.core.BQBiol.HAS_VERSION: (
            "http://biomodels.net/biology-qualifiers/",
            "hasVersion",
        ),
        momapy.sbml.core.BQBiol.IS: (
            "http://biomodels.net/biology-qualifiers/",
            "is",
        ),
        momapy.sbml.core.BQBiol.IS_DESCRIBED_BY: (
            "http://biomodels.net/biology-qualifiers/",
            "isDescribedBy1",
        ),
        momapy.sbml.core.BQBiol.IS_ENCODED_BY: (
            "http://biomodels.net/biology-qualifiers/",
            "isEncodedBy",
        ),
        momapy.sbml.core.BQBiol.IS_HOMOLOG_TO: (
            "http://biomodels.net/biology-qualifiers/",
            "isHomologTo",
        ),
        momapy.sbml.core.BQBiol.IS_PART_OF: (
            "http://biomodels.net/biology-qualifiers/",
            "isPartOf",
        ),
        momapy.sbml.core.BQBiol.IS_PROPERTY_OF: (
            "http://biomodels.net/biology-qualifiers/",
            "isPropertyOf",
        ),
        momapy.sbml.core.BQBiol.IS_VERSION_OF: (
            "http://biomodels.net/biology-qualifiers/",
            "isVersionOf",
        ),
        momapy.sbml.core.BQBiol.OCCURS_IN: (
            "http://biomodels.net/biology-qualifiers/",
            "occursIn",
        ),
        momapy.sbml.core.BQBiol.HAS_TAXON: (
            "http://biomodels.net/biology-qualifiers/",
            "hasTaxon",
        ),
        momapy.sbml.core.BQModel.HAS_INSTANCE: (
            "http://biomodels.net/model-qualifiers/",
            "hasInstance",
        ),
        momapy.sbml.core.BQModel.IS: (
            "http://biomodels.net/model-qualifiers/",
            "is",
        ),
        momapy.sbml.core.BQModel.IS_DERIVED_FROM: (
            "http://biomodels.net/model-qualifiers/",
            "isDerivedFrom",
        ),
        momapy.sbml.core.BQModel.IS_DESCRIBED_BY: (
            "http://biomodels.net/model-qualifiers/",
            "isDescribedBy",
        ),
        momapy.sbml.core.BQModel.IS_INSTANCE_OF: (
            "http://biomodels.net/model-qualifiers/",
            "isInstanceOf",
        ),
    }

    @classmethod
    def _make_lxml_element(
        cls, tag, namespace=None, attributes=None, text=None, nsmap=None
    ):
        if namespace is not None:
            lxml_tag = f"{{{namespace}}}{tag}"
        else:
            lxml_tag = tag
        if nsmap is None:
            nsmap = {}
        if attributes is None:
            attributes = {}
        lxml_element = lxml.etree.Element(lxml_tag, nsmap=nsmap, **attributes)
        if text is not None:
            lxml_element.text = text
        return lxml_element

    @classmethod
    def _get_sbgnml_id_from_map_element(cls, map_element, ids):
        sbgnml_ids = ids.get(map_element)
        if sbgnml_ids is None:
            sbgnml_id = map_element.id_
        else:
            sbgnml_id = sbgnml_ids[0]
        return sbgnml_id

    @classmethod
    def write(
        cls,
        obj: momapy.sbgn.core.SBGNMap,
        file_path,
        annotations=None,
        notes=None,
        ids=None,
        with_render_information=True,
        with_annotations=True,
        with_notes=True,
    ):
        if annotations is None:
            annotations = {}
        if ids is None:
            ids = {}
        sbgnml_sbgn = cls._make_lxml_element("sbgn", nsmap=cls._NSMAP)
        sbgnml_map = cls._make_sbgnml_map_from_map(
            obj,
            annotations=annotations,
            notes=notes,
            ids=ids,
            with_render_information=with_render_information,
            with_annotations=with_annotations,
            with_notes=with_notes,
        )
        sbgnml_sbgn.append(sbgnml_map)
        with open(file_path, "w") as f:
            f.write(
                lxml.etree.tostring(
                    sbgnml_sbgn, pretty_print=True, xml_declaration=True
                ).decode()
            )

    @classmethod
    def _make_sbgnml_map_from_map(
        cls,
        map_,
        annotations,
        notes,
        ids,
        with_render_information=True,
        with_annotations=True,
        with_notes=True,
    ):
        language = cls._CLASS_TO_SBGNML_CLASS_ATTRIBUTE[type(map_)]
        id_ = ids.get(map_)
        if id_ is None:
            id_ = map_.id_
        else:
            id_ = id_[0]
        attributes = {"id": id_, "language": language}
        sbgnml_map = cls._make_lxml_element("map", attributes=attributes)
        for layout_element in map_.layout.layout_elements:
            cls._make_and_add_sbgnml_elements_from_layout_element(
                map_=map_,
                sbgnml_map=sbgnml_map,
                layout_element=layout_element,
                annotations=annotations,
                notes=notes,
                ids=ids,
                with_annotations=with_annotations,
                with_notes=with_notes,
            )
        return sbgnml_map

    @classmethod
    def _make_and_add_sbgnml_elements_from_layout_element(
        cls,
        map_,
        sbgnml_map,
        layout_element,
        annotations,
        notes,
        ids,
        with_annotations=True,
        with_notes=True,
    ):
        model_element = map_.get_mapping(layout_element)
        if model_element is not None:
            if isinstance(layout_element, momapy.core.Node):
                sbgnml_elements = cls._make_sbgnml_elements_from_node(
                    map_=map_,
                    node=layout_element,
                    annotations=annotations,
                    ids=ids,
                )
            elif isinstance(
                layout_element,
                (momapy.core.SingleHeadedArc, momapy.core.DoubleHeadedArc),
            ):
                sbgnml_elements = cls._make_sbgnml_elements_from_arc(
                    map_=map_,
                    arc=layout_element,
                    annotations=annotations,
                    ids=ids,
                    super_layout_element=None,
                )
            if with_annotations:
                if annotations is not None:
                    element_annotations = annotations.get(model_element)
                    if element_annotations is not None:
                        sbgnml_annotation = (
                            cls._make_sbgnml_annotation_from_annotations(
                                element_annotations,
                                sbgnml_id=cls._get_sbgnml_id_from_map_element(
                                    model_element, ids
                                ),
                            )
                        )
                        sbgnml_extension = cls._make_lxml_element("extension")
                        sbgnml_extension.append(sbgnml_annotation)
                        for sbgnml_element in sbgnml_elements:
                            sbgnml_element.append(sbgnml_extension)
            if with_notes:
                if notes is not None:
                    element_notes = notes.get(model_element)
                    if notes is not None:
                        sbgnml_notes = cls._make_lxml_element(tag="notes")
                        notes_root = lxml.etree.fromstring(element_notes)
                        sbgnml_notes.append(notes_root)
                        for sbgnml_element in sbgnml_elements:
                            sbgnml_element.append(sbgnml_notes)
            for sbgnml_element in sbgnml_elements:
                sbgnml_map.append(sbgnml_element)

    @classmethod
    def _make_sbgnml_annotation_from_annotations(cls, annotations, sbgnml_id):
        sbgnml_annotation = cls._make_lxml_element("annotation")
        sbgnml_rdf = cls._make_lxml_element(
            tag="RDF", namespace=cls._NSMAP["rdf"], nsmap=cls._NSMAP
        )
        sbgnml_annotation.append(sbgnml_rdf)
        sbgnml_description = cls._make_lxml_element(
            tag="Description",
            namespace=cls._NSMAP["rdf"],
            attributes={f"{{{cls._NSMAP['rdf']}}}about": f"#{sbgnml_id}"},
        )
        sbgnml_rdf.append(sbgnml_description)
        for annotation in annotations:
            namespace, tag = cls._QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE[
                annotation.qualifier
            ]
            sbgnml_bq = cls._make_lxml_element(tag=tag, namespace=namespace)
            sbgnml_description.append(sbgnml_bq)
            sbgnml_bag = cls._make_lxml_element(tag="Bag", namespace=cls._NSMAP["rdf"])
            sbgnml_bq.append(sbgnml_bag)
            for resource in annotation.resources:
                sbgnml_li = cls._make_lxml_element(
                    tag="li",
                    namespace=cls._NSMAP["rdf"],
                    attributes={f"{{{cls._NSMAP['rdf']}}}resource": resource},
                )
                sbgnml_bag.append(sbgnml_li)
        return sbgnml_annotation

    @classmethod
    def _make_sbgnml_elements_from_node(cls, map_, node, annotations, ids):
        sbgnml_ids = ids.get(node)
        if sbgnml_ids is None:
            sbgnml_id = node.id_
        else:
            sbgnml_id = sbgnml_ids[0]
        sbgnml_class = cls._CLASS_TO_SBGNML_CLASS_ATTRIBUTE[type(node)]
        attributes = {"id": sbgnml_id, "class": sbgnml_class}
        direction = getattr(node, "direction", None)
        if direction is not None:
            sbgnml_orientation = cls._DIRECTION_TO_SBGNML_ORIENTATION[direction]
            attributes["orientation"] = sbgnml_orientation
        model_element = map_.get_mapping(node)
        if isinstance(
            model_element, (momapy.sbgn.pd.EntityPool, momapy.sbgn.af.Activity)
        ):
            compartment = model_element.compartment
            if compartment is not None:
                compartment_id = cls._get_sbgnml_id_from_map_element(compartment, ids)
                attributes["compartmentRef"] = compartment_id
        sbgnml_element = cls._make_lxml_element("glyph", attributes=attributes)
        sbgnml_elements = [sbgnml_element]
        sbgnml_bbox = cls._make_sbgnml_bbox_from_node(node)
        sbgnml_element.append(sbgnml_bbox)
        if node.label is not None:
            if isinstance(node, momapy.sbgn.pd.StateVariableLayout):
                sbgnml_state = cls._make_sbgnml_state_from_text_layout(node.label)
                sbgnml_element.append(sbgnml_state)
            else:
                sbgnml_label = cls._make_sbgnml_label_from_text_layout(node.label)
                sbgnml_element.append(sbgnml_label)
        if hasattr(node, "left_connector_tip"):
            left_connector_tip = node.left_connector_tip()
            sbgnml_port = cls._make_sbgnml_port_from_point(
                left_connector_tip, port_id=f"{sbgnml_id}_left"
            )
            sbgnml_element.append(sbgnml_port)
        if hasattr(node, "right_connector_tip"):
            right_connector_tip = node.right_connector_tip()
            sbgnml_port = cls._make_sbgnml_port_from_point(
                right_connector_tip, port_id=f"{sbgnml_id}_right"
            )
            sbgnml_element.append(sbgnml_port)
        for layout_element in node.layout_elements:
            if isinstance(layout_element, momapy.core.Node):
                sub_sbgnml_elements = cls._make_sbgnml_elements_from_node(
                    map_=map_,
                    node=layout_element,
                    annotations=annotations,
                    ids=ids,
                )
                for sub_sbgnml_element in sub_sbgnml_elements:
                    if sub_sbgnml_element.tag == "glyph":
                        sbgnml_element.append(sub_sbgnml_element)
                    else:
                        sbgnml_elements.append(sub_sbgnml_element)
            elif isinstance(
                layout_element,
                (momapy.core.SingleHeadedArc, momapy.core.DoubleHeadedArc),
            ):
                sub_sbgnml_elements = cls._make_sbgnml_elements_from_arc(
                    map_=map_,
                    arc=layout_element,
                    annotations=annotations,
                    ids=ids,
                    super_layout_element=node,
                )
                sbgnml_elements += sub_sbgnml_elements
        return sbgnml_elements

    @classmethod
    def _make_sbgnml_elements_from_arc(
        cls, map_, arc, annotations, ids, super_layout_element=None
    ):
        sbgnml_ids = ids.get(arc)
        if sbgnml_ids is None:
            sbgnml_id = arc.id_
        else:
            sbgnml_id = sbgnml_ids[0]
        sbgnml_class = cls._CLASS_TO_SBGNML_CLASS_ATTRIBUTE[type(arc)]
        attributes = {
            "id": sbgnml_id,
            "class": sbgnml_class,
        }
        points = arc.points()
        # the source may be absent for some arcs that belong to nodes (flux arcs,
        # logic arcs, equivalence arc). When it is the case, we use the super
        # layout element to find the id of the source of the arc
        # TODO: check what happens for equivalence arcs and tags/terminals, as
        # those nodes to not have any connectors
        if arc.source is None:
            sbgnml_source_id = cls._get_sbgnml_id_from_map_element(
                super_layout_element, ids
            )
            if hasattr(super_layout_element, "left_connector_tip"):
                distance_to_left = momapy.geometry.get_distance_between_points(
                    super_layout_element.left_connector_tip(),
                    points[0],
                )
                distance_to_right = momapy.geometry.get_distance_between_points(
                    super_layout_element.right_connector_tip(),
                    points[0],
                )
                if distance_to_left < distance_to_right:
                    sbgnml_source_id_suffix = "left"
                else:
                    sbgnml_source_id_suffix = "right"
                sbgnml_source_id = f"{sbgnml_source_id}_{sbgnml_source_id_suffix}"
        else:
            sbgnml_source_id = cls._get_sbgnml_id_from_map_element(arc.source, ids)
        sbgnml_target_id = cls._get_sbgnml_id_from_map_element(arc.target, ids)
        # momapy reverts the consumption and logic arc direction compared to
        # SBGN-ML, so we need to revert it back here
        if isinstance(
            arc,
            (
                momapy.sbgn.pd.ConsumptionLayout,
                momapy.sbgn.pd.LogicArcLayout,
                momapy.sbgn.af.LogicArcLayout,
                momapy.sbgn.pd.EquivalenceArcLayout,
                momapy.sbgn.af.EquivalenceArcLayout,
            ),
        ):
            attributes["source"] = sbgnml_target_id
            attributes["target"] = sbgnml_source_id
            points.reverse()
        else:
            attributes["target"] = sbgnml_target_id
            attributes["source"] = sbgnml_source_id
        sbgnml_element = cls._make_lxml_element("arc", attributes=attributes)
        sbgnml_points = cls._make_sbgnml_points_from_points(points)
        for sbgnml_point in sbgnml_points:
            sbgnml_element.append(sbgnml_point)
        return [sbgnml_element]

    @classmethod
    def _make_sbgnml_points_from_points(cls, points):
        sbgnml_elements = []
        start_point = points[0]
        sbgnml_start_point_attributes = {
            "x": str(start_point.x),
            "y": str(start_point.y),
        }
        sbgnml_start_point = cls._make_lxml_element(
            "start", attributes=sbgnml_start_point_attributes
        )
        sbgnml_elements.append(sbgnml_start_point)
        for point in points[1:-1]:
            sbgnml_next_point_attributes = {
                "x": str(point.x),
                "y": str(point.y),
            }
            sbgnml_next_point = cls._make_lxml_element(
                "next", attributes=sbgnml_next_point_attributes
            )
            sbgnml_elements.append(sbgnml_next_point)
        end_point = points[-1]
        sbgnml_end_point_attributes = {
            "x": str(end_point.x),
            "y": str(end_point.y),
        }
        sbgnml_end_point = cls._make_lxml_element(
            "end", attributes=sbgnml_end_point_attributes
        )
        sbgnml_elements.append(sbgnml_end_point)
        return sbgnml_elements

    @classmethod
    def _make_sbgnml_port_from_point(cls, point, port_id):
        attributes = {"id": port_id, "x": str(point.x), "y": str(point.y)}
        sbgnml_element = cls._make_lxml_element("port", attributes=attributes)
        return sbgnml_element

    @classmethod
    def _make_sbgnml_bbox_from_node(cls, node):
        attributes = {
            "x": str(node.x - node.width / 2),
            "y": str(node.y - node.height / 2),
            "w": str(node.width),
            "h": str(node.height),
        }
        sbgnml_bbox = cls._make_lxml_element("bbox", attributes=attributes)
        return sbgnml_bbox

    @classmethod
    def _make_sbgnml_bbox_from_text_layout(cls, text_layout):
        ink_bbox = text_layout.ink_bbox()
        attributes = {
            "x": str(ink_bbox.x - ink_bbox.width / 2),
            "y": str(ink_bbox.y - ink_bbox.height / 2),
            "w": str(ink_bbox.width),
            "h": str(ink_bbox.height),
        }
        sbgnml_bbox = cls._make_lxml_element("bbox", attributes=attributes)
        return sbgnml_bbox

    @classmethod
    def _make_sbgnml_label_from_text_layout(cls, text_layout):
        attributes = {"text": text_layout.text}
        sbgnml_label = cls._make_lxml_element("label", attributes=attributes)
        sbgnml_bbox = cls._make_sbgnml_bbox_from_text_layout(text_layout)
        sbgnml_label.append(sbgnml_bbox)
        return sbgnml_label

    @classmethod
    def _make_sbgnml_state_from_text_layout(cls, text_layout):
        attributes = {}
        text_split = text_layout.text.split("@")
        if len(text_split) > 1:
            attributes["variable"] = text_split[-1]
            if text_split[0]:
                attributes["value"] = text_split[0]
        else:
            attributes["value"] = text_split[0]
        sbgnml_state = cls._make_lxml_element("state", attributes=attributes)
        return sbgnml_state


class SBGNML0_2Writer(_SBGNMLWriter):
    """Class for SBGN-ML 0.2 writer objects"""

    @classmethod
    def _sbgn_objs_from_map(cls, map_):
        sbgn = cls._parser_module.Sbgn()
        sbgn_map = cls._parser_module.Map()
        if momapy.builder.isinstance_or_builder(map_, momapy.sbgn.pd.SBGNPDMap):
            sbgn_language = cls._parser_module.MapLanguage.PROCESS_DESCRIPTION
        elif momapy.builder.isinstance_or_builder(map_, momapy.sbgn.af.SBGNAFMap):
            sbgn_language = cls._parser_module.MapLanguage.ACTIVITY_FLOW
        else:
            raise TypeError("this type of map is not yet supported")
        sbgn_map.language = sbgn_language
        sbgn.map = sbgn_map
        return sbgn, sbgn_map


class SBGNML0_3Writer(_SBGNMLWriter):
    """Class for SBGN-ML 0.3 writer objects"""

    pass


momapy.io.register_reader("sbgnml-0.2", SBGNML0_2Reader)
momapy.io.register_reader("sbgnml-0.3", SBGNML0_3Reader)
momapy.io.register_reader("sbgnml", SBGNML0_3Reader)
momapy.io.register_writer("sbgnml-0.2", SBGNML0_2Writer)
momapy.io.register_writer("sbgnml-0.3", SBGNML0_3Writer)
momapy.io.register_writer("sbgnml", SBGNML0_3Writer)
