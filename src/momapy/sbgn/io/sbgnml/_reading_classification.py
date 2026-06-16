"""Element classification for SBGN-ML reader.

Maps SBGN-ML XML element types to momapy model and layout classes.
Pure logic — depends on parsing and core classes, nothing else.
"""

import momapy.sbgn.pd
import momapy.sbgn.af

from momapy.builder import isinstance_or_builder
from momapy.sbgn.io.sbgnml._reading_parsing import transform_class
from momapy.sbgn.pd import AndOperator as PDAndOperator
from momapy.sbgn.pd import AndOperatorLayout as PDAndOperatorLayout
from momapy.sbgn.pd import Association as PDAssociation
from momapy.sbgn.pd import AssociationLayout as PDAssociationLayout
from momapy.sbgn.pd import Catalysis as PDCatalysis
from momapy.sbgn.pd import CatalysisLayout as PDCatalysisLayout
from momapy.sbgn.pd import Compartment as PDCompartment
from momapy.sbgn.pd import CompartmentLayout as PDCompartmentLayout
from momapy.sbgn.pd import Complex as PDComplex
from momapy.sbgn.pd import ComplexLayout as PDComplexLayout
from momapy.sbgn.pd import ComplexMultimer as PDComplexMultimer
from momapy.sbgn.pd import ComplexMultimerLayout as PDComplexMultimerLayout
from momapy.sbgn.pd import ComplexMultimerSubunit as PDComplexMultimerSubunit
from momapy.sbgn.pd import (
    ComplexMultimerSubunitLayout as PDComplexMultimerSubunitLayout,
)
from momapy.sbgn.pd import ComplexSubunit as PDComplexSubunit
from momapy.sbgn.pd import ComplexSubunitLayout as PDComplexSubunitLayout
from momapy.sbgn.pd import ConsumptionLayout as PDConsumptionLayout
from momapy.sbgn.pd import Dissociation as PDDissociation
from momapy.sbgn.pd import DissociationLayout as PDDissociationLayout
from momapy.sbgn.pd import EmptySetLayout as PDEmptySetLayout
from momapy.sbgn.pd import EquivalenceArcLayout as PDEquivalenceArcLayout
from momapy.sbgn.pd import GenericProcess as PDGenericProcess
from momapy.sbgn.pd import GenericProcessLayout as PDGenericProcessLayout
from momapy.sbgn.pd import Inhibition as PDInhibition
from momapy.sbgn.pd import InhibitionLayout as PDInhibitionLayout
from momapy.sbgn.pd import LogicArcLayout as PDLogicArcLayout
from momapy.sbgn.pd import LogicalOperatorInput as PDLogicalOperatorInput
from momapy.sbgn.pd import Macromolecule as PDMacromolecule
from momapy.sbgn.pd import MacromoleculeLayout as PDMacromoleculeLayout
from momapy.sbgn.pd import MacromoleculeMultimer as PDMacromoleculeMultimer
from momapy.sbgn.pd import MacromoleculeMultimerLayout as PDMacromoleculeMultimerLayout
from momapy.sbgn.pd import (
    MacromoleculeMultimerSubunit as PDMacromoleculeMultimerSubunit,
)
from momapy.sbgn.pd import (
    MacromoleculeMultimerSubunitLayout as PDMacromoleculeMultimerSubunitLayout,
)
from momapy.sbgn.pd import MacromoleculeSubunit as PDMacromoleculeSubunit
from momapy.sbgn.pd import MacromoleculeSubunitLayout as PDMacromoleculeSubunitLayout
from momapy.sbgn.pd import Modulation as PDModulation
from momapy.sbgn.pd import ModulationLayout as PDModulationLayout
from momapy.sbgn.pd import NecessaryStimulation as PDNecessaryStimulation
from momapy.sbgn.pd import NecessaryStimulationLayout as PDNecessaryStimulationLayout
from momapy.sbgn.pd import NotOperator as PDNotOperator
from momapy.sbgn.pd import NotOperatorLayout as PDNotOperatorLayout
from momapy.sbgn.pd import NucleicAcidFeature as PDNucleicAcidFeature
from momapy.sbgn.pd import NucleicAcidFeatureLayout as PDNucleicAcidFeatureLayout
from momapy.sbgn.pd import NucleicAcidFeatureMultimer as PDNucleicAcidFeatureMultimer
from momapy.sbgn.pd import (
    NucleicAcidFeatureMultimerLayout as PDNucleicAcidFeatureMultimerLayout,
)
from momapy.sbgn.pd import (
    NucleicAcidFeatureMultimerSubunit as PDNucleicAcidFeatureMultimerSubunit,
)
from momapy.sbgn.pd import (
    NucleicAcidFeatureMultimerSubunitLayout as PDNucleicAcidFeatureMultimerSubunitLayout,
)
from momapy.sbgn.pd import NucleicAcidFeatureSubunit as PDNucleicAcidFeatureSubunit
from momapy.sbgn.pd import (
    NucleicAcidFeatureSubunitLayout as PDNucleicAcidFeatureSubunitLayout,
)
from momapy.sbgn.pd import OmittedProcess as PDOmittedProcess
from momapy.sbgn.pd import OmittedProcessLayout as PDOmittedProcessLayout
from momapy.sbgn.pd import OrOperator as PDOrOperator
from momapy.sbgn.pd import OrOperatorLayout as PDOrOperatorLayout
from momapy.sbgn.pd import PerturbingAgent as PDPerturbingAgent
from momapy.sbgn.pd import PerturbingAgentLayout as PDPerturbingAgentLayout
from momapy.sbgn.pd import Phenotype as PDPhenotype
from momapy.sbgn.pd import PhenotypeLayout as PDPhenotypeLayout
from momapy.sbgn.pd import Product as PDProduct
from momapy.sbgn.pd import ProductionLayout as PDProductionLayout
from momapy.sbgn.pd import Reactant as PDReactant
from momapy.sbgn.pd import SBGNPDLayout as PDSBGNPDLayout
from momapy.sbgn.pd import SBGNPDMap as PDSBGNPDMap
from momapy.sbgn.pd import SBGNPDModel as PDSBGNPDModel
from momapy.sbgn.pd import SimpleChemical as PDSimpleChemical
from momapy.sbgn.pd import SimpleChemicalLayout as PDSimpleChemicalLayout
from momapy.sbgn.pd import SimpleChemicalMultimer as PDSimpleChemicalMultimer
from momapy.sbgn.pd import (
    SimpleChemicalMultimerLayout as PDSimpleChemicalMultimerLayout,
)
from momapy.sbgn.pd import (
    SimpleChemicalMultimerSubunit as PDSimpleChemicalMultimerSubunit,
)
from momapy.sbgn.pd import (
    SimpleChemicalMultimerSubunitLayout as PDSimpleChemicalMultimerSubunitLayout,
)
from momapy.sbgn.pd import SimpleChemicalSubunit as PDSimpleChemicalSubunit
from momapy.sbgn.pd import SimpleChemicalSubunitLayout as PDSimpleChemicalSubunitLayout
from momapy.sbgn.pd import StateVariable as PDStateVariable
from momapy.sbgn.pd import StateVariableLayout as PDStateVariableLayout
from momapy.sbgn.pd import Stimulation as PDStimulation
from momapy.sbgn.pd import StimulationLayout as PDStimulationLayout
from momapy.sbgn.pd import Submap as PDSubmap
from momapy.sbgn.pd import SubmapLayout as PDSubmapLayout
from momapy.sbgn.pd import Tag as PDTag
from momapy.sbgn.pd import TagLayout as PDTagLayout
from momapy.sbgn.pd import TagReference as PDTagReference
from momapy.sbgn.pd import Terminal as PDTerminal
from momapy.sbgn.pd import TerminalLayout as PDTerminalLayout
from momapy.sbgn.pd import UncertainProcess as PDUncertainProcess
from momapy.sbgn.pd import UncertainProcessLayout as PDUncertainProcessLayout
from momapy.sbgn.pd import UnitOfInformation as PDUnitOfInformation
from momapy.sbgn.pd import UnitOfInformationLayout as PDUnitOfInformationLayout
from momapy.sbgn.pd import UnspecifiedEntity as PDUnspecifiedEntity
from momapy.sbgn.pd import UnspecifiedEntityLayout as PDUnspecifiedEntityLayout
from momapy.sbgn.pd import UnspecifiedEntitySubunit as PDUnspecifiedEntitySubunit
from momapy.sbgn.pd import (
    UnspecifiedEntitySubunitLayout as PDUnspecifiedEntitySubunitLayout,
)
from momapy.sbgn.af import AndOperator as AFAndOperator
from momapy.sbgn.af import AndOperatorLayout as AFAndOperatorLayout
from momapy.sbgn.af import BiologicalActivity as AFBiologicalActivity
from momapy.sbgn.af import BiologicalActivityLayout as AFBiologicalActivityLayout
from momapy.sbgn.af import Compartment as AFCompartment
from momapy.sbgn.af import CompartmentLayout as AFCompartmentLayout
from momapy.sbgn.af import ComplexUnitOfInformation as AFComplexUnitOfInformation
from momapy.sbgn.af import (
    ComplexUnitOfInformationLayout as AFComplexUnitOfInformationLayout,
)
from momapy.sbgn.af import DelayOperator as AFDelayOperator
from momapy.sbgn.af import DelayOperatorLayout as AFDelayOperatorLayout
from momapy.sbgn.af import EquivalenceArcLayout as AFEquivalenceArcLayout
from momapy.sbgn.af import LogicArcLayout as AFLogicArcLayout
from momapy.sbgn.af import LogicalOperatorInput as AFLogicalOperatorInput
from momapy.sbgn.af import (
    MacromoleculeUnitOfInformation as AFMacromoleculeUnitOfInformation,
)
from momapy.sbgn.af import (
    MacromoleculeUnitOfInformationLayout as AFMacromoleculeUnitOfInformationLayout,
)
from momapy.sbgn.af import NecessaryStimulation as AFNecessaryStimulation
from momapy.sbgn.af import NecessaryStimulationLayout as AFNecessaryStimulationLayout
from momapy.sbgn.af import NegativeInfluence as AFNegativeInfluence
from momapy.sbgn.af import NegativeInfluenceLayout as AFNegativeInfluenceLayout
from momapy.sbgn.af import NotOperator as AFNotOperator
from momapy.sbgn.af import NotOperatorLayout as AFNotOperatorLayout
from momapy.sbgn.af import (
    NucleicAcidFeatureUnitOfInformation as AFNucleicAcidFeatureUnitOfInformation,
)
from momapy.sbgn.af import (
    NucleicAcidFeatureUnitOfInformationLayout as AFNucleicAcidFeatureUnitOfInformationLayout,
)
from momapy.sbgn.af import OrOperator as AFOrOperator
from momapy.sbgn.af import OrOperatorLayout as AFOrOperatorLayout
from momapy.sbgn.af import (
    PerturbationUnitOfInformation as AFPerturbationUnitOfInformation,
)
from momapy.sbgn.af import (
    PerturbationUnitOfInformationLayout as AFPerturbationUnitOfInformationLayout,
)
from momapy.sbgn.af import Phenotype as AFPhenotype
from momapy.sbgn.af import PhenotypeLayout as AFPhenotypeLayout
from momapy.sbgn.af import PositiveInfluence as AFPositiveInfluence
from momapy.sbgn.af import PositiveInfluenceLayout as AFPositiveInfluenceLayout
from momapy.sbgn.af import SBGNAFLayout as AFSBGNAFLayout
from momapy.sbgn.af import SBGNAFMap as AFSBGNAFMap
from momapy.sbgn.af import SBGNAFModel as AFSBGNAFModel
from momapy.sbgn.af import (
    SimpleChemicalUnitOfInformation as AFSimpleChemicalUnitOfInformation,
)
from momapy.sbgn.af import (
    SimpleChemicalUnitOfInformationLayout as AFSimpleChemicalUnitOfInformationLayout,
)
from momapy.sbgn.af import Submap as AFSubmap
from momapy.sbgn.af import SubmapLayout as AFSubmapLayout
from momapy.sbgn.af import Tag as AFTag
from momapy.sbgn.af import TagLayout as AFTagLayout
from momapy.sbgn.af import TagReference as AFTagReference
from momapy.sbgn.af import Terminal as AFTerminal
from momapy.sbgn.af import TerminalLayout as AFTerminalLayout
from momapy.sbgn.af import UnitOfInformation as AFUnitOfInformation
from momapy.sbgn.af import UnitOfInformationLayout as AFUnitOfInformationLayout
from momapy.sbgn.af import UnknownInfluence as AFUnknownInfluence
from momapy.sbgn.af import UnknownInfluenceLayout as AFUnknownInfluenceLayout
from momapy.sbgn.af import (
    UnspecifiedEntityUnitOfInformation as AFUnspecifiedEntityUnitOfInformation,
)
from momapy.sbgn.af import (
    UnspecifiedEntityUnitOfInformationLayout as AFUnspecifiedEntityUnitOfInformationLayout,
)

KEY_TO_MODULE = {
    "PROCESS_DESCRIPTION": momapy.sbgn.pd,
    "ACTIVITY_FLOW": momapy.sbgn.af,
}

KEY_TO_CLASS = {
    "PROCESS_DESCRIPTION": (
        PDSBGNPDMap,
        PDSBGNPDModel,
        PDSBGNPDLayout,
    ),
    "ACTIVITY_FLOW": (
        AFSBGNAFMap,
        AFSBGNAFModel,
        AFSBGNAFLayout,
    ),
    ("PROCESS_DESCRIPTION", "SUBGLYPH", "STATE_VARIABLE"): (
        PDStateVariable,
        PDStateVariableLayout,
    ),
    ("PROCESS_DESCRIPTION", "SUBGLYPH", "UNIT_OF_INFORMATION"): (
        PDUnitOfInformation,
        PDUnitOfInformationLayout,
    ),
    ("PROCESS_DESCRIPTION", "SUBGLYPH", "TERMINAL"): (
        PDTerminal,
        PDTerminalLayout,
    ),
    ("PROCESS_DESCRIPTION", "SUBGLYPH", "UNSPECIFIED_ENTITY"): (
        PDUnspecifiedEntitySubunit,
        PDUnspecifiedEntitySubunitLayout,
    ),
    ("PROCESS_DESCRIPTION", "SUBGLYPH", "MACROMOLECULE"): (
        PDMacromoleculeSubunit,
        PDMacromoleculeSubunitLayout,
    ),
    ("PROCESS_DESCRIPTION", "SUBGLYPH", "MACROMOLECULE_MULTIMER"): (
        PDMacromoleculeMultimerSubunit,
        PDMacromoleculeMultimerSubunitLayout,
    ),
    ("PROCESS_DESCRIPTION", "SUBGLYPH", "SIMPLE_CHEMICAL"): (
        PDSimpleChemicalSubunit,
        PDSimpleChemicalSubunitLayout,
    ),
    ("PROCESS_DESCRIPTION", "SUBGLYPH", "SIMPLE_CHEMICAL_MULTIMER"): (
        PDSimpleChemicalMultimerSubunit,
        PDSimpleChemicalMultimerSubunitLayout,
    ),
    ("PROCESS_DESCRIPTION", "SUBGLYPH", "NUCLEIC_ACID_FEATURE"): (
        PDNucleicAcidFeatureSubunit,
        PDNucleicAcidFeatureSubunitLayout,
    ),
    ("PROCESS_DESCRIPTION", "SUBGLYPH", "NUCLEIC_ACID_FEATURE_MULTIMER"): (
        PDNucleicAcidFeatureMultimerSubunit,
        PDNucleicAcidFeatureMultimerSubunitLayout,
    ),
    ("PROCESS_DESCRIPTION", "SUBGLYPH", "COMPLEX"): (
        PDComplexSubunit,
        PDComplexSubunitLayout,
    ),
    ("PROCESS_DESCRIPTION", "SUBGLYPH", "COMPLEX_MULTIMER"): (
        PDComplexMultimerSubunit,
        PDComplexMultimerSubunitLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "COMPARTMENT"): (
        PDCompartment,
        PDCompartmentLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "SUBMAP"): (
        PDSubmap,
        PDSubmapLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "TAG"): (
        PDTag,
        PDTagLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "UNSPECIFIED_ENTITY"): (
        PDUnspecifiedEntity,
        PDUnspecifiedEntityLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "MACROMOLECULE"): (
        PDMacromolecule,
        PDMacromoleculeLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "MACROMOLECULE_MULTIMER"): (
        PDMacromoleculeMultimer,
        PDMacromoleculeMultimerLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "SIMPLE_CHEMICAL"): (
        PDSimpleChemical,
        PDSimpleChemicalLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "SIMPLE_CHEMICAL_MULTIMER"): (
        PDSimpleChemicalMultimer,
        PDSimpleChemicalMultimerLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "NUCLEIC_ACID_FEATURE"): (
        PDNucleicAcidFeature,
        PDNucleicAcidFeatureLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "NUCLEIC_ACID_FEATURE_MULTIMER"): (
        PDNucleicAcidFeatureMultimer,
        PDNucleicAcidFeatureMultimerLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "COMPLEX"): (
        PDComplex,
        PDComplexLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "COMPLEX_MULTIMER"): (
        PDComplexMultimer,
        PDComplexMultimerLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "SOURCE_AND_SINK"): (
        None,
        PDEmptySetLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "EMPTY_SET"): (
        None,
        PDEmptySetLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "PERTURBING_AGENT"): (
        PDPerturbingAgent,
        PDPerturbingAgentLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "PROCESS"): (
        PDGenericProcess,
        PDGenericProcessLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "OMITTED_PROCESS"): (
        PDOmittedProcess,
        PDOmittedProcessLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "UNCERTAIN_PROCESS"): (
        PDUncertainProcess,
        PDUncertainProcessLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "ASSOCIATION"): (
        PDAssociation,
        PDAssociationLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "DISSOCIATION"): (
        PDDissociation,
        PDDissociationLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "PHENOTYPE"): (
        PDPhenotype,
        PDPhenotypeLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "AND"): (
        PDAndOperator,
        PDAndOperatorLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "OR"): (
        PDOrOperator,
        PDOrOperatorLayout,
    ),
    ("PROCESS_DESCRIPTION", "GLYPH", "NOT"): (
        PDNotOperator,
        PDNotOperatorLayout,
    ),
    ("PROCESS_DESCRIPTION", "ARC", "MODULATION"): (
        PDModulation,
        PDModulationLayout,
    ),
    ("PROCESS_DESCRIPTION", "ARC", "STIMULATION"): (
        PDStimulation,
        PDStimulationLayout,
    ),
    ("PROCESS_DESCRIPTION", "ARC", "CATALYSIS"): (
        PDCatalysis,
        PDCatalysisLayout,
    ),
    ("PROCESS_DESCRIPTION", "ARC", "NECESSARY_STIMULATION"): (
        PDNecessaryStimulation,
        PDNecessaryStimulationLayout,
    ),
    ("PROCESS_DESCRIPTION", "ARC", "INHIBITION"): (
        PDInhibition,
        PDInhibitionLayout,
    ),
    ("PROCESS_DESCRIPTION", "ARC", "CONSUMPTION"): (
        PDReactant,
        PDConsumptionLayout,
    ),
    ("PROCESS_DESCRIPTION", "ARC", "PRODUCTION"): (
        PDProduct,
        PDProductionLayout,
    ),
    ("PROCESS_DESCRIPTION", "ARC", "LOGIC_ARC"): (
        PDLogicalOperatorInput,
        PDLogicArcLayout,
    ),
    ("PROCESS_DESCRIPTION", "ARC", "EQUIVALENCE_ARC"): (
        PDTagReference,
        PDEquivalenceArcLayout,
    ),
    ("ACTIVITY_FLOW", "SUBGLYPH", "UNIT_OF_INFORMATION_MACROMOLECULE"): (
        AFMacromoleculeUnitOfInformation,
        AFMacromoleculeUnitOfInformationLayout,
    ),
    ("ACTIVITY_FLOW", "SUBGLYPH", "UNIT_OF_INFORMATION_SIMPLE_CHEMICAL"): (
        AFSimpleChemicalUnitOfInformation,
        AFSimpleChemicalUnitOfInformationLayout,
    ),
    (
        "ACTIVITY_FLOW",
        "SUBGLYPH",
        "UNIT_OF_INFORMATION_NUCLEIC_ACID_FEATURE",
    ): (
        AFNucleicAcidFeatureUnitOfInformation,
        AFNucleicAcidFeatureUnitOfInformationLayout,
    ),
    ("ACTIVITY_FLOW", "SUBGLYPH", "UNIT_OF_INFORMATION_COMPLEX"): (
        AFComplexUnitOfInformation,
        AFComplexUnitOfInformationLayout,
    ),
    (
        "ACTIVITY_FLOW",
        "SUBGLYPH",
        "UNIT_OF_INFORMATION_UNSPECIFIED_ENTITY",
    ): (
        AFUnspecifiedEntityUnitOfInformation,
        AFUnspecifiedEntityUnitOfInformationLayout,
    ),
    (
        "ACTIVITY_FLOW",
        "SUBGLYPH",
        "UNIT_OF_INFORMATION_PERTURBATION",
    ): (
        AFPerturbationUnitOfInformation,
        AFPerturbationUnitOfInformationLayout,
    ),
    ("ACTIVITY_FLOW", "GLYPH", "COMPARTMENT"): (
        AFCompartment,
        AFCompartmentLayout,
    ),
    ("ACTIVITY_FLOW", "GLYPH", "BIOLOGICAL_ACTIVITY"): (
        AFBiologicalActivity,
        AFBiologicalActivityLayout,
    ),
    ("ACTIVITY_FLOW", "GLYPH", "PHENOTYPE"): (
        AFPhenotype,
        AFPhenotypeLayout,
    ),
    ("ACTIVITY_FLOW", "ARC", "POSITIVE_INFLUENCE"): (
        AFPositiveInfluence,
        AFPositiveInfluenceLayout,
    ),
    ("ACTIVITY_FLOW", "ARC", "NEGATIVE_INFLUENCE"): (
        AFNegativeInfluence,
        AFNegativeInfluenceLayout,
    ),
    ("ACTIVITY_FLOW", "ARC", "UNKNOWN_INFLUENCE"): (
        AFUnknownInfluence,
        AFUnknownInfluenceLayout,
    ),
    ("ACTIVITY_FLOW", "ARC", "NECESSARY_STIMULATION"): (
        AFNecessaryStimulation,
        AFNecessaryStimulationLayout,
    ),
    ("ACTIVITY_FLOW", "SUBGLYPH", "UNIT_OF_INFORMATION"): (
        AFUnitOfInformation,
        AFUnitOfInformationLayout,
    ),
    ("ACTIVITY_FLOW", "GLYPH", "AND"): (
        AFAndOperator,
        AFAndOperatorLayout,
    ),
    ("ACTIVITY_FLOW", "GLYPH", "OR"): (
        AFOrOperator,
        AFOrOperatorLayout,
    ),
    ("ACTIVITY_FLOW", "GLYPH", "NOT"): (
        AFNotOperator,
        AFNotOperatorLayout,
    ),
    ("ACTIVITY_FLOW", "GLYPH", "DELAY"): (
        AFDelayOperator,
        AFDelayOperatorLayout,
    ),
    ("ACTIVITY_FLOW", "ARC", "LOGIC_ARC"): (
        AFLogicalOperatorInput,
        AFLogicArcLayout,
    ),
    ("ACTIVITY_FLOW", "GLYPH", "SUBMAP"): (
        AFSubmap,
        AFSubmapLayout,
    ),
    ("ACTIVITY_FLOW", "SUBGLYPH", "TERMINAL"): (
        AFTerminal,
        AFTerminalLayout,
    ),
    ("ACTIVITY_FLOW", "GLYPH", "TAG"): (
        AFTag,
        AFTagLayout,
    ),
    ("ACTIVITY_FLOW", "ARC", "EQUIVALENCE_ARC"): (
        AFTagReference,
        AFEquivalenceArcLayout,
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
    sbgnml_class = transform_class(sbgnml_glyph.get("class"))
    return (map_key, "GLYPH", sbgnml_class)


def get_subglyph_key(sbgnml_subglyph, map_key):
    """Classify a sub-glyph element (state variable, unit of information, etc.).

    Args:
        sbgnml_subglyph: The SBGN-ML sub-glyph XML element.
        map_key: The map type key (e.g., "PROCESS_DESCRIPTION").

    Returns:
        A tuple key like ("PROCESS_DESCRIPTION", "SUBGLYPH", "STATE_VARIABLE").
    """
    sbgnml_class = transform_class(sbgnml_subglyph.get("class"))
    sbgnml_entity = getattr(sbgnml_subglyph, "entity", None)
    if sbgnml_entity is not None:
        sbgnml_entity_class = transform_class(sbgnml_entity.get("name"))
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
    sbgnml_class = transform_class(sbgnml_arc.get("class"))
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
    if isinstance_or_builder(
        obj,
        (
            PDSBGNPDMap,
            PDSBGNPDModel,
            PDSBGNPDLayout,
        ),
    ):
        return momapy.sbgn.pd
    if isinstance_or_builder(
        obj,
        (
            AFSBGNAFMap,
            AFSBGNAFModel,
            AFSBGNAFLayout,
        ),
    ):
        return momapy.sbgn.af
    return None
