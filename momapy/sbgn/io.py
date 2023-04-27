import typing

import momapy.core
import momapy.builder
import momapy.shapes
import momapy.arcs
import momapy.coloring
import momapy.styling
import momapy.sbgn.core
import momapy.sbgn.pd
import momapy.sbgn.af
import momapy.sbgn.utils

import libsbgnpy.libsbgn as libsbgn

LibSBGNPDDisambiguationArcMapping = {
    "equivalence arc": {
        "source_or_target": "target",
        "keys": {
            momapy.sbgn.pd.Tag: "equivalence arc to tag",
            momapy.sbgn.pd.Terminal: "equivalence arc to terminal",
            momapy.sbgn.af.Tag: "equivalence arc to tag",
            momapy.sbgn.af.Terminal: "equivalence arc to terminal",
        },
    },
    "logic arc": {
        "source_or_target": "target",
        "keys": {
            momapy.sbgn.pd.EntityPool: "logic arc from equivalence operator",
            momapy.sbgn.pd.EmptySet: "logic arc from equivalence operator",
            momapy.sbgn.pd.PerturbingAgent: "logic arc from equivalence operator",
            momapy.sbgn.pd.UnspecifiedEntity: "logic arc from equivalence operator",
            momapy.sbgn.pd.Macromolecule: "logic arc from equivalence operator",
            momapy.sbgn.pd.NucleicAcidFeature: "logic arc from equivalence operator",
            momapy.sbgn.pd.SimpleChemical: "logic arc from equivalence operator",
            momapy.sbgn.pd.Complex: "logic arc from equivalence operator",
            momapy.sbgn.pd.Multimer: "logic arc from equivalence operator",
            momapy.sbgn.pd.MacromoleculeMultimer: "logic arc from equivalence operator",
            momapy.sbgn.pd.NucleicAcidFeatureMultimer: "logic arc from equivalence operator",
            momapy.sbgn.pd.SimpleChemicalMultimer: "logic arc from equivalence operator",
            momapy.sbgn.pd.ComplexMultimer: "logic arc from equivalence operator",
            momapy.sbgn.pd.EquivalenceOperator: "logic arc to equivalence operator",
            momapy.sbgn.pd.LogicalOperator: "logic arc to logical operator",
            momapy.sbgn.pd.AndOperator: "logic arc to logical operator",
            momapy.sbgn.pd.OrOperator: "logic arc to logical operator",
            momapy.sbgn.pd.NotOperator: "logic arc to logical operator",
            momapy.sbgn.af.LogicalOperator: "logic arc to logical operator",
            momapy.sbgn.af.AndOperator: "logic arc to logical operator",
            momapy.sbgn.af.OrOperator: "logic arc to logical operator",
            momapy.sbgn.af.NotOperator: "logic arc to logical operator",
        },
    },
}

LibSBGNPDDisambiguationGlyphMapping = {
    "unspecified entity": "unspecified entity subunit",
    "macromolecule": "macromolecule subunit",
    "nucleic acid feature": "nucleic acid feature subunit",
    "simple chemical": "simple chemical subunit",
    "complex": "complex subunit",
    "macromolecule multimer": "macromolecule multimer subunit",
    "nucleic acid feature multimer": "nucleic acid feature multimer subunit",
    "simple chemical multimer": "simple chemical multimer subunit",
    "complex multimer": "complex multimer subunit",
}

LibSBGNAFDisambiguationArcMapping = {
    "equivalence arc": {
        "source_or_target": "target",
        "keys": {
            momapy.sbgn.af.Tag: "equivalence arc to tag",
            momapy.sbgn.af.Terminal: "equivalence arc to terminal",
        },
    },
    "logic arc": {
        "source_or_target": "target",
        "keys": {
            momapy.sbgn.af.LogicalOperator: "logic arc to logical operator",
            momapy.sbgn.af.AndOperator: "logic arc to logical operator",
            momapy.sbgn.af.OrOperator: "logic arc to logical operator",
            momapy.sbgn.af.NotOperator: "logic arc to logical operator",
            momapy.sbgn.af.DelayOperator: "logic arc to logical operator",
        },
    },
}

LibSBGNAFDisambiguationGlyphMapping = {
    "unspecified entity": "unspecified entity unit of information",
    "macromolecule": "macromolecule unit of information",
    "nucleic acid feature": "nucleic acid feature unit of information",
    "simple chemical": "simple chemical unit of information",
    "complex": "complex unit of information",
    "perturbation": "perturbation unit of information",
}

LibSBGNPDGlyphMapping = {
    "state variable": {
        "model_class": momapy.sbgn.pd.StateVariable,
        "layout_class": momapy.sbgn.pd.StateVariableLayout,
        "font_family": "Arial",
        "font_size": 8,
        "has_connectors": False,
        "has_orientation": False,
    },
    "unit of information": {
        "model_class": momapy.sbgn.pd.UnitOfInformation,
        "layout_class": momapy.sbgn.pd.UnitOfInformationLayout,
        "font_family": "Arial",
        "font_size": 8,
        "has_connectors": False,
        "has_orientation": False,
    },
    "cardinality": {
        "model_class": int,
        "layout_class": momapy.sbgn.pd.CardinalityLayout,
        "font_family": "Arial",
        "font_size": 8,
        "has_connectors": False,
        "has_orientation": False,
    },
    "stoichiometry": {
        "model_class": int,
        "layout_class": momapy.sbgn.pd.CardinalityLayout,
        "font_family": "Arial",
        "font_size": 8,
        "has_connectors": False,
        "has_orientation": False,
    },
    "unspecified entity subunit": {
        "model_class": momapy.sbgn.pd.UnspecifiedEntitySubunit,
        "layout_class": momapy.sbgn.pd.UnspecifiedEntityLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "macromolecule subunit": {
        "model_class": momapy.sbgn.pd.MacromoleculeSubunit,
        "layout_class": momapy.sbgn.pd.MacromoleculeLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "nucleic acid feature subunit": {
        "model_class": momapy.sbgn.pd.NucleicAcidFeatureSubunit,
        "layout_class": momapy.sbgn.pd.NucleicAcidFeatureLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "simple chemical subunit": {
        "model_class": momapy.sbgn.pd.SimpleChemicalSubunit,
        "layout_class": momapy.sbgn.pd.SimpleChemicalLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "complex subunit": {
        "model_class": momapy.sbgn.pd.ComplexSubunit,
        "layout_class": momapy.sbgn.pd.ComplexLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "macromolecule multimer subunit": {
        "model_class": momapy.sbgn.pd.MacromoleculeMultimerSubunit,
        "layout_class": momapy.sbgn.pd.MacromoleculeMultimerLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "nucleic acid feature multimer subunit": {
        "model_class": momapy.sbgn.pd.NucleicAcidFeatureMultimerSubunit,
        "layout_class": momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "simple chemical multimer subunit": {
        "model_class": momapy.sbgn.pd.SimpleChemicalMultimerSubunit,
        "layout_class": momapy.sbgn.pd.SimpleChemicalMultimerLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "complex multimer subunit": {
        "model_class": momapy.sbgn.pd.ComplexMultimerSubunit,
        "layout_class": momapy.sbgn.pd.ComplexMultimerLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "compartment": {
        "model_class": momapy.sbgn.pd.Compartment,
        "layout_class": momapy.sbgn.pd.CompartmentLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "empty set": {
        "model_class": momapy.sbgn.pd.EmptySet,
        "layout_class": momapy.sbgn.pd.EmptySetLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "source and sink": {
        "model_class": momapy.sbgn.pd.EmptySet,
        "layout_class": momapy.sbgn.pd.EmptySetLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "perturbing agent": {
        "model_class": momapy.sbgn.pd.PerturbingAgent,
        "layout_class": momapy.sbgn.pd.PerturbingAgentLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "unspecified entity": {
        "model_class": momapy.sbgn.pd.UnspecifiedEntity,
        "layout_class": momapy.sbgn.pd.UnspecifiedEntityLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "macromolecule": {
        "model_class": momapy.sbgn.pd.Macromolecule,
        "layout_class": momapy.sbgn.pd.MacromoleculeLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "nucleic acid feature": {
        "model_class": momapy.sbgn.pd.NucleicAcidFeature,
        "layout_class": momapy.sbgn.pd.NucleicAcidFeatureLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "simple chemical": {
        "model_class": momapy.sbgn.pd.SimpleChemical,
        "layout_class": momapy.sbgn.pd.SimpleChemicalLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "complex": {
        "model_class": momapy.sbgn.pd.Complex,
        "layout_class": momapy.sbgn.pd.ComplexLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "macromolecule multimer": {
        "model_class": momapy.sbgn.pd.MacromoleculeMultimer,
        "layout_class": momapy.sbgn.pd.MacromoleculeMultimerLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "nucleic acid feature multimer": {
        "model_class": momapy.sbgn.pd.NucleicAcidFeatureMultimer,
        "layout_class": momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "simple chemical multimer": {
        "model_class": momapy.sbgn.pd.SimpleChemicalMultimer,
        "layout_class": momapy.sbgn.pd.SimpleChemicalMultimerLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "complex multimer": {
        "model_class": momapy.sbgn.pd.ComplexMultimer,
        "layout_class": momapy.sbgn.pd.ComplexMultimerLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "process": {
        "model_class": momapy.sbgn.pd.GenericProcess,
        "layout_class": momapy.sbgn.pd.GenericProcessLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": True,
        "has_orientation": False,
    },
    "uncertain process": {
        "model_class": momapy.sbgn.pd.UncertainProcess,
        "layout_class": momapy.sbgn.pd.UncertainProcessLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": True,
        "has_orientation": False,
    },
    "association": {
        "model_class": momapy.sbgn.pd.Association,
        "layout_class": momapy.sbgn.pd.AssociationLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": True,
        "has_orientation": False,
    },
    "dissociation": {
        "model_class": momapy.sbgn.pd.Dissociation,
        "layout_class": momapy.sbgn.pd.DissociationLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": True,
        "has_orientation": False,
    },
    "omitted process": {
        "model_class": momapy.sbgn.pd.OmittedProcess,
        "layout_class": momapy.sbgn.pd.OmittedProcessLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": True,
        "has_orientation": False,
    },
    "phenotype": {
        "model_class": momapy.sbgn.pd.Phenotype,
        "layout_class": momapy.sbgn.pd.PhenotypeLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "or": {
        "model_class": momapy.sbgn.pd.OrOperator,
        "layout_class": momapy.sbgn.pd.OrOperatorLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": True,
        "has_orientation": False,
    },
    "and": {
        "model_class": momapy.sbgn.pd.AndOperator,
        "layout_class": momapy.sbgn.pd.AndOperatorLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": True,
        "has_orientation": False,
    },
    "not": {
        "model_class": momapy.sbgn.pd.NotOperator,
        "layout_class": momapy.sbgn.pd.NotOperatorLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": True,
        "has_orientation": False,
    },
    "equivalence": {
        "model_class": momapy.sbgn.pd.EquivalenceOperator,
        "layout_class": momapy.sbgn.pd.EquivalenceOperator,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": True,
        "has_orientation": False,
    },
    "terminal": {
        "model_class": momapy.sbgn.pd.Terminal,
        "layout_class": momapy.sbgn.pd.TerminalLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": True,
    },
    "tag": {
        "model_class": momapy.sbgn.pd.Tag,
        "layout_class": momapy.sbgn.pd.TagLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": True,
    },
    "submap": {
        "model_class": momapy.sbgn.pd.Submap,
        "layout_class": momapy.sbgn.pd.SubmapLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
}

LibSBGNAFGlyphMapping = {
    "biological activity": {
        "model_class": momapy.sbgn.af.BiologicalActivity,
        "layout_class": momapy.sbgn.af.BiologicalActivityLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "phenotype": {
        "model_class": momapy.sbgn.af.Phenotype,
        "layout_class": momapy.sbgn.af.PhenotypeLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "compartment": {
        "model_class": momapy.sbgn.af.Compartment,
        "layout_class": momapy.sbgn.af.CompartmentLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "and": {
        "model_class": momapy.sbgn.af.AndOperator,
        "layout_class": momapy.sbgn.af.AndOperatorLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": True,
        "has_orientation": False,
    },
    "or": {
        "model_class": momapy.sbgn.af.OrOperator,
        "layout_class": momapy.sbgn.af.OrOperatorLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": True,
        "has_orientation": False,
    },
    "not": {
        "model_class": momapy.sbgn.af.NotOperator,
        "layout_class": momapy.sbgn.af.NotOperatorLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": True,
        "has_orientation": False,
    },
    "delay": {
        "model_class": momapy.sbgn.af.DelayOperator,
        "layout_class": momapy.sbgn.af.DelayOperatorLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": True,
        "has_orientation": False,
    },
    "unspecified entity unit of information": {
        "model_class": momapy.sbgn.af.UnspecifiedEntityUnitOfInformation,
        "layout_class": momapy.sbgn.af.UnspecifiedEntityUnitOfInformationLayout,
        "font_family": "Arial",
        "font_size": 14,
        "has_connectors": False,
        "has_orientation": False,
    },
    "macromolecule unit of information": {
        "model_class": momapy.sbgn.af.MacromoleculeUnitOfInformation,
        "layout_class": momapy.sbgn.af.MacromoleculeUnitOfInformationLayout,
        "font_family": "Arial",
        "font_size": 14,
        "has_connectors": False,
        "has_orientation": False,
    },
    "nucleic acid feature unit of information": {
        "model_class": momapy.sbgn.af.NucleicAcidFeatureUnitOfInformation,
        "layout_class": momapy.sbgn.af.NucleicAcidFeatureUnitOfInformationLayout,
        "font_family": "Arial",
        "font_size": 14,
        "has_connectors": False,
        "has_orientation": False,
    },
    "simple chemical unit of information": {
        "model_class": momapy.sbgn.af.SimpleChemicalUnitOfInformation,
        "layout_class": momapy.sbgn.af.SimpleChemicalUnitOfInformationLayout,
        "font_family": "Arial",
        "font_size": 14,
        "has_connectors": False,
        "has_orientation": False,
    },
    "complex unit of information": {
        "model_class": momapy.sbgn.af.ComplexUnitOfInformation,
        "layout_class": momapy.sbgn.af.ComplexUnitOfInformationLayout,
        "font_family": "Arial",
        "font_size": 14,
        "has_connectors": False,
        "has_orientation": False,
    },
    "perturbation unit of information": {
        "model_class": momapy.sbgn.af.PerturbationUnitOfInformation,
        "layout_class": momapy.sbgn.af.PerturbationUnitOfInformationLayout,
        "font_family": "Arial",
        "font_size": 14,
        "has_connectors": False,
        "has_orientation": False,
    },
    "submap": {
        "model_class": momapy.sbgn.af.Submap,
        "layout_class": momapy.sbgn.af.SubmapLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "tag": {
        "model_class": momapy.sbgn.af.Tag,
        "layout_class": momapy.sbgn.af.TagLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
    "terminal": {
        "model_class": momapy.sbgn.af.Terminal,
        "layout_class": momapy.sbgn.af.TerminalLayout,
        "font_family": "Arial",
        "font_size": 20,
        "has_connectors": False,
        "has_orientation": False,
    },
}


LibSBGNPDArcMapping = {
    "consumption": {
        "model_class": momapy.sbgn.pd.Reactant,
        "layout_class": momapy.sbgn.pd.ConsumptionLayout,
        "role": {"source_or_target": "source", "attribute": "reactants"},
    },
    "production": {
        "model_class": momapy.sbgn.pd.Product,
        "layout_class": momapy.sbgn.pd.ProductionLayout,
        "role": {"source_or_target": "target", "attribute": "products"},
    },
    "logic arc to logical operator": {
        "model_class": momapy.sbgn.pd.LogicalOperatorInput,
        "layout_class": momapy.sbgn.pd.LogicArcLayout,
        "role": {"source_or_target": "source", "attribute": "inputs"},
    },
    "logic arc to equivalence operator": {
        "model_class": momapy.sbgn.pd.EquivalenceOperatorInput,
        "layout_class": momapy.sbgn.pd.LogicArcLayout,
        "role": {"source_or_target": "source", "attribute": "inputs"},
    },
    "logic arc from equivalence operator": {
        "model_class": momapy.sbgn.pd.EquivalenceOperatorOutput,
        "layout_class": momapy.sbgn.pd.LogicArcLayout,
        "role": {"source_or_target": "target", "attribute": "output"},
    },
    "equivalence arc to terminal": {
        "model_class": momapy.sbgn.pd.TerminalReference,
        "layout_class": momapy.sbgn.pd.EquivalenceArcLayout,
        "role": {"source_or_target": "source", "attribute": "refers_to"},
    },
    "equivalence arc to tag": {
        "model_class": momapy.sbgn.pd.TagReference,
        "layout_class": momapy.sbgn.pd.EquivalenceArcLayout,
        "role": {"source_or_target": "source", "attribute": "refers_to"},
    },
    "modulation": {
        "model_class": momapy.sbgn.pd.Modulation,
        "layout_class": momapy.sbgn.pd.ModulationLayout,
    },
    "inhibition": {
        "model_class": momapy.sbgn.pd.Inhibition,
        "layout_class": momapy.sbgn.pd.InhibitionLayout,
    },
    "stimulation": {
        "model_class": momapy.sbgn.pd.Stimulation,
        "layout_class": momapy.sbgn.pd.StimulationLayout,
    },
    "catalysis": {
        "model_class": momapy.sbgn.pd.Catalysis,
        "layout_class": momapy.sbgn.pd.CatalysisLayout,
    },
    "necessary stimulation": {
        "model_class": momapy.sbgn.pd.NecessaryStimulation,
        "layout_class": momapy.sbgn.pd.NecessaryStimulationLayout,
    },
}

LibSBGNAFArcMapping = {
    "unknown influence": {
        "model_class": momapy.sbgn.af.UnknownInfluence,
        "layout_class": momapy.sbgn.af.UnknownInfluenceLayout,
    },
    "positive influence": {
        "model_class": momapy.sbgn.af.PositiveInfluence,
        "layout_class": momapy.sbgn.af.PositiveInfluenceLayout,
    },
    "negative influence": {
        "model_class": momapy.sbgn.af.NegativeInfluence,
        "layout_class": momapy.sbgn.af.NegativeInfluenceLayout,
    },
    "necessary stimulation": {
        "model_class": momapy.sbgn.af.NecessaryStimulation,
        "layout_class": momapy.sbgn.af.NecessaryStimulationLayout,
    },
    "logic arc to logical operator": {
        "model_class": momapy.sbgn.af.LogicalOperatorInput,
        "layout_class": momapy.sbgn.af.LogicArcLayout,
        "role": {"source_or_target": "source", "attribute": "inputs"},
    },
    "equivalence arc to terminal": {
        "model_class": momapy.sbgn.af.TerminalReference,
        "layout_class": momapy.sbgn.af.EquivalenceArcLayout,
        "role": {"source_or_target": "source", "attribute": "refers_to"},
    },
    "equivalence arc to tag": {
        "model_class": momapy.sbgn.af.TagReference,
        "layout_class": momapy.sbgn.af.EquivalenceArcLayout,
        "role": {"source_or_target": "source", "attribute": "refers_to"},
    },
}

LibSBGNMapMapping = {
    "process description": {
        "model": momapy.sbgn.pd.SBGNPDMap,
        "glyph_mapping": LibSBGNPDGlyphMapping,
        "arc_mapping": LibSBGNPDArcMapping,
        "glyph_disambiguation_mapping": LibSBGNPDDisambiguationGlyphMapping,
        "arc_disambiguation_mapping": LibSBGNPDDisambiguationArcMapping,
    },
    "activity flow": {
        "model": momapy.sbgn.af.SBGNAFMap,
        "glyph_mapping": LibSBGNAFGlyphMapping,
        "arc_mapping": LibSBGNAFArcMapping,
        "glyph_disambiguation_mapping": LibSBGNAFDisambiguationGlyphMapping,
        "arc_disambiguation_mapping": LibSBGNAFDisambiguationArcMapping,
    },
    "entity relationship": {
        "model": None,
    },
}


def read_file(file_name, return_builder=False, tidy=False, style_sheet=None):
    libsbgn_sbgn = libsbgn.parse(file_name, silence=True)
    libsbgn_map = libsbgn_sbgn.get_map()
    language = libsbgn_map.get_language()
    builder = momapy.builder.new_builder(
        LibSBGNMapMapping[language.value]["model"]
    )
    glyph_mapping = LibSBGNMapMapping[language.value]["glyph_mapping"]
    arc_mapping = LibSBGNMapMapping[language.value]["arc_mapping"]
    glyph_disambiguation_mapping = LibSBGNMapMapping[language.value][
        "glyph_disambiguation_mapping"
    ]
    arc_disambiguation_mapping = LibSBGNMapMapping[language.value][
        "arc_disambiguation_mapping"
    ]
    model = builder.new_model()
    layout = builder.new_layout()
    layout_model_mapping = builder.new_layout_model_mapping()
    builder.model = model
    builder.layout = layout
    builder.layout_model_mapping = layout_model_mapping
    d_model_elements_ids = {}
    d_layout_elements_ids = {}
    libsbgn_map_dimensions = _get_libsbgn_map_dimensions(libsbgn_map)
    builder.layout.width = libsbgn_map_dimensions[0]
    builder.layout.height = libsbgn_map_dimensions[1]
    builder.layout.position = momapy.geometry.PointBuilder(
        libsbgn_map_dimensions[0] / 2, libsbgn_map_dimensions[1] / 2
    )
    libsbgn_compartments = []
    libsbgn_other_glyphs = []
    for glyph in libsbgn_map.get_glyph():
        if glyph.get_class() == libsbgn.GlyphClass.COMPARTMENT:
            libsbgn_compartments.append(glyph)
        else:
            libsbgn_other_glyphs.append(glyph)
    libsbgn_compartments = sorted(
        libsbgn_compartments,
        key=lambda compartment: compartment.get_compartmentOrder()
        if compartment.get_compartmentOrder() is not None
        else 0,
    )
    for glyph in libsbgn_compartments + libsbgn_other_glyphs:
        _make_and_add_map_elements_from_glyph(
            glyph,
            builder,
            glyph_mapping,
            glyph_disambiguation_mapping,
            d_model_elements_ids,
            d_layout_elements_ids,
        )
    for arc in libsbgn_map.get_arc():
        _make_and_add_map_elements_from_arc(
            arc,
            builder,
            arc_mapping,
            arc_disambiguation_mapping,
            d_model_elements_ids,
            d_layout_elements_ids,
        )
    if style_sheet is not None:
        if (
            not isinstance(style_sheet, typing.Collection)
            or isinstance(style_sheet, str)
            or isinstance(style_sheet, momapy.styling.StyleSheet)
        ):
            style_sheets = [style_sheet]
        else:
            style_sheets = style_sheet
        style_sheets = [
            momapy.styling.read_file(style_sheet)
            if not isinstance(style_sheet, momapy.styling.StyleSheet)
            else style_sheet
            for style_sheet in style_sheets
        ]
        style_sheet = momapy.styling.join_style_sheets(style_sheets)
        momapy.styling.apply_style_sheet(builder.layout, style_sheet)
    if tidy:
        momapy.sbgn.utils.tidy(builder)
    if return_builder:
        return builder
    return builder.build()


def _make_and_add_map_elements_from_glyph(
    glyph,
    builder,
    glyph_mapping,
    glyph_disambiguation_mapping,
    d_model_elements_ids,
    d_layout_elements_ids,
    is_subglyph=False,
    super_model_element=None,
    super_layout_element=None,
    order=None,
):

    model_element, layout_element = _make_map_elements_from_glyph(
        glyph,
        builder,
        glyph_mapping,
        glyph_disambiguation_mapping,
        d_model_elements_ids,
        d_layout_elements_ids,
        is_subglyph,
        order,
    )
    if not is_subglyph:
        builder.add_model_element(model_element)
        builder.add_layout_element(layout_element)
    else:
        if (
            glyph.get_class() != libsbgn.GlyphClass.CARDINALITY
            and glyph.get_class() != libsbgn.GlyphClass.STOICHIOMETRY
        ):
            super_model_element.add_element(model_element)
        else:
            super_model_element.stoichiometry = model_element
        super_layout_element.add_element(layout_element)
    if momapy.builder.isinstance_or_builder(
        model_element, momapy.core.ModelElement
    ):
        if is_subglyph:
            nm_model_element = super_model_element
        else:
            nm_model_element = None
        builder.map_model_element_to_layout_element(
            layout_element, model_element, nm_model_element
        )
        d_model_elements_ids[model_element.id] = model_element
    d_layout_elements_ids[layout_element.id] = layout_element
    libsbgn_no_var_svs = []
    libsbgn_other_subglyphs = []
    for subglyph in glyph.get_glyph():
        if subglyph.get_class() == libsbgn.GlyphClass.STATE_VARIABLE:
            libsbgn_state = subglyph.get_state()
            if libsbgn_state is not None:
                if subglyph.get_state().get_variable() is None:
                    libsbgn_no_var_svs.append(subglyph)
                else:
                    libsbgn_other_subglyphs.append(subglyph)
            else:
                libsbgn_state = libsbgn.stateType()
                subglyph.set_state(libsbgn_state)
                libsbgn_no_var_svs.append(subglyph)
        else:
            libsbgn_other_subglyphs.append(subglyph)
    if libsbgn_no_var_svs:
        libsbgn_glyph_pos = _get_position_from_libsbgn_bbox(glyph.get_bbox())
        libsbgn_no_var_svs = sorted(
            libsbgn_no_var_svs,
            key=lambda sv: momapy.geometry.get_angle_of_line(
                momapy.geometry.Line(
                    libsbgn_glyph_pos,
                    _get_position_from_libsbgn_bbox(sv.get_bbox()),
                )
            ),
        )
        for i, subglyph in enumerate(libsbgn_no_var_svs):
            _make_and_add_map_elements_from_glyph(
                subglyph,
                builder,
                glyph_mapping,
                glyph_disambiguation_mapping,
                d_model_elements_ids,
                d_layout_elements_ids,
                is_subglyph=True,
                super_model_element=model_element,
                super_layout_element=layout_element,
                order=i,
            )
    for subglyph in libsbgn_other_subglyphs:
        _make_and_add_map_elements_from_glyph(
            subglyph,
            builder,
            glyph_mapping,
            glyph_disambiguation_mapping,
            d_model_elements_ids,
            d_layout_elements_ids,
            is_subglyph=True,
            super_model_element=model_element,
            super_layout_element=layout_element,
            order=None,
        )
    for port in glyph.get_port():
        d_model_elements_ids[port.get_id()] = model_element
        d_layout_elements_ids[port.get_id()] = layout_element


def _disambiguate_arc(arc, arc_disambiguation_mapping, d_model_elements_ids):
    disambiguation_key = arc.get_class().value
    disambiguation = arc_disambiguation_mapping.get(disambiguation_key)
    if disambiguation is not None:
        source_or_target = disambiguation["source_or_target"]
        if source_or_target == "source":
            disambiguation_element_id = arc.get_source()
        else:
            disambiguation_element_id = arc.get_target()
        disambiguation_element = d_model_elements_ids[disambiguation_element_id]
        disambiguation_key = disambiguation["keys"][
            type(disambiguation_element)._cls_to_build
        ]
    return disambiguation_key


def _make_and_add_map_elements_from_arc(
    arc,
    builder,
    arc_mapping,
    arc_disambiguation_mapping,
    d_model_elements_ids,
    d_layout_elements_ids,
):
    model_element, layout_element = _make_map_elements_from_arc(
        arc,
        builder,
        arc_mapping,
        arc_disambiguation_mapping,
        d_model_elements_ids,
        d_layout_elements_ids,
    )
    arc_key = _disambiguate_arc(
        arc, arc_disambiguation_mapping, d_model_elements_ids
    )
    role = arc_mapping[arc_key].get("role")
    if role is not None:
        source_or_target = role["source_or_target"]
        if source_or_target == "target":
            super_element_id = arc.get_source()
        else:
            super_element_id = arc.get_target()
        super_model_element = d_model_elements_ids[super_element_id]
        attribute = getattr(super_model_element, role["attribute"])
        if hasattr(attribute, "append"):
            attribute.append(model_element)
        elif hasattr(attribute, "add"):
            attribute.add(model_element)
        else:
            setattr(super_model_element, role["attribute"], model_element)
    else:
        builder.add_model_element(model_element)
    builder.add_layout_element(layout_element)
    builder.map_model_element_to_layout_element(layout_element, model_element)
    d_model_elements_ids[model_element.id] = model_element
    d_layout_elements_ids[layout_element.id] = layout_element
    for subglyph in arc.get_glyph():
        _make_and_add_map_elements_from_glyph(
            subglyph,
            builder,
            glyph_mapping,
            glyph_disambiguation_mapping,
            d_model_elements_ids,
            d_layout_elements_ids,
            is_subglyph=True,
            super_model_element=model_element,
            super_layout_element=layout_element,
            order=None,
        )
    for port in arc.get_port():
        d_model_elements_ids[port.get_id()] = model_element
        d_layout_elements_ids[port.get_id()] = layout_element


def _make_map_elements_from_glyph(
    glyph,
    builder,
    glyph_mapping,
    glyph_disambiguation_mapping,
    d_model_elements_ids,
    d_layout_elements_ids,
    is_subglyph=False,
    order=None,
):

    model_element = _make_model_element_from_glyph(
        glyph,
        builder,
        glyph_mapping,
        glyph_disambiguation_mapping,
        d_model_elements_ids,
        d_layout_elements_ids,
        is_subglyph,
        order,
    )
    layout_element = _make_layout_element_from_glyph(
        glyph,
        builder,
        glyph_mapping,
        glyph_disambiguation_mapping,
        d_model_elements_ids,
        d_layout_elements_ids,
        is_subglyph,
        order,
    )
    return model_element, layout_element


def _disambiguate_subglyph(subglyph, glyph_disambiguation_mapping):
    disambiguation_key = subglyph.get_class().value
    if disambiguation_key in glyph_disambiguation_mapping:
        disambiguation_key = glyph_disambiguation_mapping[disambiguation_key]
    else:
        if subglyph.get_entity() is not None:
            disambiguation_key = glyph_disambiguation_mapping[
                subglyph.get_entity().get_name()
            ]
    return disambiguation_key


def _make_model_element_from_glyph(
    glyph,
    builder,
    glyph_mapping,
    glyph_disambiguation_mapping,
    d_model_elements_ids,
    d_layout_elements_ids,
    is_subglyph=False,
    order=None,
):
    if (
        glyph.get_class() != libsbgn.GlyphClass.CARDINALITY
        and glyph.get_class() != libsbgn.GlyphClass.STOICHIOMETRY
    ):
        if is_subglyph:
            glyph_key = _disambiguate_subglyph(
                glyph, glyph_disambiguation_mapping
            )
        else:
            glyph_key = glyph.get_class().value
        model_element_class = glyph_mapping[glyph_key]["model_class"]
        model_element = builder.new_model_element(model_element_class)
        model_element.id = glyph.get_id()
        if (
            glyph.get_label() is not None
            and glyph.get_label().get_text() is not None
        ):
            if glyph_key == "unit of information":
                label = glyph.get_label().get_text()
                l = label.split(":")
                model_element.value = l[-1]
                if len(l) > 1:
                    model_element.prefix = l[0]
            else:
                model_element.label = glyph.get_label().get_text()
        if glyph.get_compartmentRef() is not None and hasattr(
            model_element, "compartment"
        ):
            model_element.compartment = d_model_elements_ids[
                glyph.get_compartmentRef()
            ]
        if glyph.get_state() is not None:
            model_element.value = glyph.get_state().get_value()
            libsbgn_variable = glyph.get_state().get_variable()
            if libsbgn_variable is None:
                variable = momapy.sbgn.pd.UndefinedVariable(order=order)
            else:
                variable = libsbgn_variable
            model_element.variable = variable
    else:
        return int(glyph.get_label().get_text())
    return model_element


def _make_layout_element_from_glyph(
    glyph,
    builder,
    glyph_mapping,
    glyph_disambiguation_mapping,
    d_model_elements_ids,
    d_layout_elements_ids,
    is_subglyph=False,
    order=None,
):
    if is_subglyph:
        glyph_key = _disambiguate_subglyph(glyph, glyph_disambiguation_mapping)
    else:
        glyph_key = glyph.get_class().value
    layout_element_class = glyph_mapping[glyph_key]["layout_class"]
    layout_element = builder.new_layout_element(layout_element_class)
    layout_element.id = glyph.get_id()
    layout_element.width = glyph.get_bbox().get_w()
    layout_element.height = glyph.get_bbox().get_h()
    layout_element.position = _get_position_from_libsbgn_bbox(glyph.get_bbox())
    libsbgn_state = glyph.get_state()
    libsbgn_label = glyph.get_label()
    if libsbgn_label is not None or libsbgn_state is not None:
        if libsbgn_label is not None:
            libsbgn_label_bbox = libsbgn_label.get_bbox()
            if libsbgn_label_bbox is not None:
                label_position = _get_position_from_libsbgn_bbox(
                    libsbgn_label_bbox
                )
                label_width = libsbgn_label_bbox.get_w()
                label_height = libsbgn_label_bbox.get_h()
            else:
                label_position = layout_element.label_center()
                label_width = None
                label_height = None
            text = libsbgn_label.get_text()
        elif libsbgn_state is not None:
            label_position = layout_element.label_center()
            label_width = None
            label_height = None
            libsbgn_variable = libsbgn_state.get_variable()
            libsbgn_value = libsbgn_state.get_value()
            value_text = libsbgn_value if libsbgn_value is not None else ""
            if libsbgn_variable is not None and len(libsbgn_variable) > 0:
                text = f"{value_text}@{libsbgn_variable}"
            else:
                text = value_text
        label_element = builder.new_layout_element(momapy.core.TextLayout)
        label_element.text = text
        label_element.position = label_position
        label_element.width = label_width
        label_element.height = label_height
        label_element.font_family = glyph_mapping[glyph_key]["font_family"]
        label_element.font_size = glyph_mapping[glyph_key]["font_size"]
        label_element.horizontal_alignment = momapy.core.HAlignment.CENTER
        label_element.vertical_alignment = momapy.core.VAlignment.CENTER
        layout_element.label = label_element
    if glyph_mapping[glyph_key]["has_connectors"]:
        for libsbgn_port in glyph.get_port():
            if libsbgn_port.get_x() < glyph.get_bbox().get_x():  # LEFT
                layout_element.left_connector_length = (
                    glyph.get_bbox().get_x() - libsbgn_port.get_x()
                )
                layout_element.direction = momapy.core.Direction.HORIZONTAL
            elif libsbgn_port.get_y() < glyph.get_bbox().get_y():  # UP
                layout_element.left_connector_length = (
                    glyph.get_bbox().get_y() - libsbgn_port.get_y()
                )
                layout_element.direction = momapy.core.Direction.VERTICAL
            elif (
                libsbgn_port.get_x()
                >= glyph.get_bbox().get_x() + glyph.get_bbox().get_w()
            ):  # RIGHT
                layout_element.right_connector_length = (
                    libsbgn_port.get_x()
                    - glyph.get_bbox().get_x()
                    - glyph.get_bbox().get_w()
                )
                layout_element.direction = momapy.core.Direction.HORIZONTAL
            elif (
                libsbgn_port.get_y()
                >= glyph.get_bbox().get_y() + glyph.get_bbox().get_h()
            ):  # DOWN
                layout_element.right_connector_length = (
                    libsbgn_port.get_y()
                    - glyph.get_bbox().get_y()
                    - glyph.get_bbox().get_h()
                )
                layout_element.direction = momapy.core.Direction.VERTICAL
    if glyph_mapping[glyph_key]["has_orientation"]:
        layout_element.direction = momapy.core.Direction[
            glyph.get_orientation().name
        ]
    return layout_element


def _make_map_elements_from_arc(
    arc,
    builder,
    arc_mapping,
    arc_disambiguation_mapping,
    d_model_elements_ids,
    d_layout_elements_ids,
):
    model_element = _make_model_element_from_arc(
        arc,
        builder,
        arc_mapping,
        arc_disambiguation_mapping,
        d_model_elements_ids,
        d_layout_elements_ids,
    )
    layout_element = _make_layout_element_from_arc(
        arc,
        builder,
        arc_mapping,
        arc_disambiguation_mapping,
        d_model_elements_ids,
        d_layout_elements_ids,
    )
    return model_element, layout_element


def _make_model_element_from_arc(
    arc,
    builder,
    arc_mapping,
    arc_disambiguation_mapping,
    d_model_elements_ids,
    d_layout_elements_ids,
):
    arc_key = _disambiguate_arc(
        arc, arc_disambiguation_mapping, d_model_elements_ids
    )
    model_element_class = arc_mapping[arc_key]["model_class"]
    model_element = builder.new_model_element(model_element_class)
    model_element.id = arc.get_id()
    role = arc_mapping[arc_key].get("role")
    if role is not None:
        source_or_target = role["source_or_target"]
        if source_or_target == "source":
            role_element_id = arc.get_source()
        else:
            role_element_id = arc.get_target()
        model_element.element = d_model_elements_ids[role_element_id]
    else:
        model_element.source = d_model_elements_ids[arc.get_source()]
        model_element.target = d_model_elements_ids[arc.get_target()]
    return model_element


def _make_layout_element_from_arc(
    arc,
    builder,
    arc_mapping,
    arc_disambiguation_mapping,
    d_model_elements_ids,
    d_layout_elements_ids,
):
    arc_key = _disambiguate_arc(
        arc, arc_disambiguation_mapping, d_model_elements_ids
    )
    layout_element_class = arc_mapping[arc_key]["layout_class"]
    layout_element = builder.new_layout_element(layout_element_class)
    layout_element.id = arc.get_id()
    role = arc_mapping[arc_key].get("role")
    layout_element.source = momapy.core.PhantomLayoutBuilder(
        layout_element=d_layout_elements_ids[arc.get_source()]
    )
    layout_element.target = momapy.core.PhantomLayoutBuilder(
        layout_element=d_layout_elements_ids[arc.get_target()]
    )
    libsbgn_points = [arc.get_start()] + arc.get_next() + [arc.get_end()]
    for i, libsbgn_current_point in enumerate(libsbgn_points[1:]):
        libsbgn_previous_point = libsbgn_points[i]
        current_point = momapy.geometry.PointBuilder(
            libsbgn_current_point.get_x(), libsbgn_current_point.get_y()
        )
        previous_point = momapy.geometry.PointBuilder(
            libsbgn_previous_point.get_x(), libsbgn_previous_point.get_y()
        )
        segment = momapy.builder.get_or_make_builder_cls(
            momapy.geometry.Segment
        )(previous_point, current_point)
        layout_element.segments.append(segment)
    return layout_element


def _get_libsbgn_map_dimensions(libsbgn_map):
    return _get_libsbgn_map_max_x_and_y(libsbgn_map)


def _get_glyph_max_x_and_y(glyph):
    max_x = glyph.get_bbox().get_x() + glyph.get_bbox().get_w()
    max_y = glyph.get_bbox().get_y() + glyph.get_bbox().get_h()
    for subglyph in glyph.get_glyph():
        sub_max_x, sub_max_y = _get_glyph_max_x_and_y(subglyph)
        if sub_max_x > max_x:
            max_x = sub_max_x
        if sub_max_y > max_y:
            max_y = sub_max_y
    return max_x, max_y


def _get_arc_max_x_and_y(arc):
    max_x = 0
    max_y = 0
    for p in [arc.get_start()] + arc.get_next() + [arc.get_end()]:
        if p.get_x() > max_x:
            max_x = p.get_x()
        if p.get_y() > max_y:
            max_y = p.get_y()
    for glyph in arc.get_glyph():
        glyph_max_x, glyph_max_y = _get_glyph_max_x_and_y(glyph)
        if glyph_max_x > max_x:
            max_x = glyph_max_x
        if glyph_max_y > max_y:
            max_y = glyph_max_y
    return max_x, max_y


def _get_arcgroup_max_x_and_y(arcgroup):
    max_x = 0
    max_y = 0
    for glyph in arcgroup.get_glyph():
        glyph_max_x, glyph_max_y = _get_glyph_max_x_and_y(glyph)
        if glyph_max_x > max_x:
            max_x = glyph_max_x
        if glyph_max_y > max_y:
            max_y = glyph_max_y
    for arc in arcgroup.get_arc():
        arc_max_x, arc_max_y = _get_arc_max_x_and_y(arc)
        if arc_max_x > max_x:
            max_x = arc_max_x
        if arc_max_y > max_y:
            max_y = arc_max_y
    return max_x, max_y


def _get_libsbgn_map_max_x_and_y(libsbgn_map):
    max_x = 0
    max_y = 0
    for glyph in libsbgn_map.get_glyph():
        glyph_max_x, glyph_max_y = _get_glyph_max_x_and_y(glyph)
        if glyph_max_x > max_x:
            max_x = glyph_max_x
        if glyph_max_y > max_y:
            max_y = glyph_max_y
    for arc in libsbgn_map.get_arc():
        arc_max_x, arc_max_y = _get_arc_max_x_and_y(arc)
        if arc_max_x > max_x:
            max_x = arc_max_x
        if arc_max_y > max_y:
            max_y = arc_max_y
    for arcgroup in libsbgn_map.get_arcgroup():
        arcgroup_max_x, arcgroup_max_y = _get_arcgroup_max_x_and_y(arcgroup)
        if arcgroup_max_x > max_x:
            max_x = arcgroup_max_x
        if arcgroup_max_y > max_y:
            max_y = arcgroup_max_y
    return max_x, max_y


def _get_position_from_libsbgn_bbox(bbox):
    return momapy.geometry.PointBuilder(
        bbox.get_x() + bbox.get_w() / 2, bbox.get_y() + bbox.get_h() / 2
    )
