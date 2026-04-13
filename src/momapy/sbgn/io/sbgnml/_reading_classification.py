"""Element classification for SBGN-ML reader.

Maps SBGN-ML XML element types to momapy model and layout classes.
Pure logic — depends on parsing and core classes, nothing else.
"""

import momapy.builder
import momapy.sbgn.pd
import momapy.sbgn.af
import momapy.sbgn.io.sbgnml._reading_parsing

KEY_TO_MODULE = {
    "PROCESS_DESCRIPTION": momapy.sbgn.pd,
    "ACTIVITY_FLOW": momapy.sbgn.af,
}

KEY_TO_CLASS = {
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


def get_glyph_key(sbgnml_glyph, map_key):
    """Classify a top-level glyph element.

    Args:
        sbgnml_glyph: The SBGN-ML glyph XML element.
        map_key: The map type key (e.g., "PROCESS_DESCRIPTION").

    Returns:
        A tuple key like ("PROCESS_DESCRIPTION", "GLYPH", "MACROMOLECULE").
    """
    sbgnml_class = momapy.sbgn.io.sbgnml._reading_parsing.transform_class(
        sbgnml_glyph.get("class")
    )
    return (map_key, "GLYPH", sbgnml_class)


def get_subglyph_key(sbgnml_subglyph, map_key):
    """Classify a sub-glyph element (state variable, unit of information, etc.).

    Args:
        sbgnml_subglyph: The SBGN-ML sub-glyph XML element.
        map_key: The map type key (e.g., "PROCESS_DESCRIPTION").

    Returns:
        A tuple key like ("PROCESS_DESCRIPTION", "SUBGLYPH", "STATE_VARIABLE").
    """
    sbgnml_class = momapy.sbgn.io.sbgnml._reading_parsing.transform_class(
        sbgnml_subglyph.get("class")
    )
    sbgnml_entity = getattr(sbgnml_subglyph, "entity", None)
    if sbgnml_entity is not None:
        sbgnml_entity_class = momapy.sbgn.io.sbgnml._reading_parsing.transform_class(
            sbgnml_entity.get("name")
        )
        sbgnml_class = f"{sbgnml_class}_{sbgnml_entity_class}"
    return (map_key, "SUBGLYPH", sbgnml_class)


def get_arc_key(sbgnml_arc, map_key):
    """Classify an arc element.

    Args:
        sbgnml_arc: The SBGN-ML arc XML element.
        map_key: The map type key (e.g., "PROCESS_DESCRIPTION").

    Returns:
        A tuple key like ("PROCESS_DESCRIPTION", "ARC", "CATALYSIS").
    """
    sbgnml_class = momapy.sbgn.io.sbgnml._reading_parsing.transform_class(
        sbgnml_arc.get("class")
    )
    return (map_key, "ARC", sbgnml_class)


def get_model_and_layout_classes(key):
    """Get the model and layout classes for a classification key.

    Args:
        key: A classification key (tuple or string).

    Returns:
        A tuple of (model_class, layout_class).
    """
    return KEY_TO_CLASS[key]


def get_module(map_key):
    """Get the SBGN module (pd or af) for a map key.

    Args:
        map_key: The map type key (e.g., "PROCESS_DESCRIPTION").

    Returns:
        The momapy.sbgn.pd or momapy.sbgn.af module.
    """
    return KEY_TO_MODULE.get(map_key)


def get_module_from_object(obj):
    """Get the SBGN module from a model or layout builder/object.

    Args:
        obj: A model or layout builder/object.

    Returns:
        The momapy.sbgn.pd or momapy.sbgn.af module.
    """
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
