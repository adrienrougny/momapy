import dataclasses

import momapy.utils
import momapy.sbgn.pd
import momapy.sbgn.af

WIDTH = 60.0
HEIGHT = 30.0


node_configs = [
    (
        momapy.sbgn.pd.StateVariableLayout,
        {},
    ),
    (
        momapy.sbgn.pd.UnitOfInformationLayout,
        {},
    ),
    (
        momapy.sbgn.pd.TerminalLayout,
        {},
    ),
    (
        momapy.sbgn.pd.TerminalLayout,
        {"direction": momapy.core.Direction.LEFT},
    ),
    (
        momapy.sbgn.pd.TerminalLayout,
        {
            "direction": momapy.core.Direction.UP,
            "width": HEIGHT,
            "height": WIDTH,
        },
    ),
    (
        momapy.sbgn.pd.TerminalLayout,
        {
            "direction": momapy.core.Direction.DOWN,
            "width": HEIGHT,
            "height": WIDTH,
        },
    ),
    (
        momapy.sbgn.pd.CardinalityLayout,
        {},
    ),
    (
        momapy.sbgn.pd.UnspecifiedEntitySubunitLayout,
        {},
    ),
    (
        momapy.sbgn.pd.SimpleChemicalSubunitLayout,
        {},
    ),
    (
        momapy.sbgn.pd.MacromoleculeSubunitLayout,
        {},
    ),
    (
        momapy.sbgn.pd.NucleicAcidFeatureSubunitLayout,
        {},
    ),
    (
        momapy.sbgn.pd.ComplexSubunitLayout,
        {},
    ),
    (
        momapy.sbgn.pd.SimpleChemicalMultimerSubunitLayout,
        {},
    ),
    (
        momapy.sbgn.pd.MacromoleculeMultimerSubunitLayout,
        {},
    ),
    (
        momapy.sbgn.pd.NucleicAcidFeatureMultimerSubunitLayout,
        {},
    ),
    (
        momapy.sbgn.pd.ComplexMultimerSubunitLayout,
        {},
    ),
    (
        momapy.sbgn.pd.CompartmentLayout,
        {},
    ),
    (
        momapy.sbgn.pd.SubmapLayout,
        {},
    ),
    (
        momapy.sbgn.pd.UnspecifiedEntityLayout,
        {},
    ),
    (
        momapy.sbgn.pd.SimpleChemicalLayout,
        {},
    ),
    (
        momapy.sbgn.pd.MacromoleculeLayout,
        {},
    ),
    (
        momapy.sbgn.pd.NucleicAcidFeatureLayout,
        {},
    ),
    (
        momapy.sbgn.pd.ComplexLayout,
        {},
    ),
    (
        momapy.sbgn.pd.SimpleChemicalMultimerLayout,
        {},
    ),
    (
        momapy.sbgn.pd.MacromoleculeMultimerLayout,
        {},
    ),
    (
        momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout,
        {},
    ),
    (
        momapy.sbgn.pd.ComplexMultimerLayout,
        {},
    ),
    (
        momapy.sbgn.pd.EmptySetLayout,
        {},
    ),
    (
        momapy.sbgn.pd.PerturbingAgentLayout,
        {},
    ),
    (
        momapy.sbgn.pd.AndOperatorLayout,
        {},
    ),
    (
        momapy.sbgn.pd.AndOperatorLayout,
        {
            "direction": momapy.core.Direction.VERTICAL,
        },
    ),
    (
        momapy.sbgn.pd.OrOperatorLayout,
        {},
    ),
    (
        momapy.sbgn.pd.OrOperatorLayout,
        {
            "direction": momapy.core.Direction.VERTICAL,
        },
    ),
    (
        momapy.sbgn.pd.NotOperatorLayout,
        {},
    ),
    (
        momapy.sbgn.pd.NotOperatorLayout,
        {
            "direction": momapy.core.Direction.VERTICAL,
        },
    ),
    (
        momapy.sbgn.pd.EquivalenceOperatorLayout,
        {},
    ),
    (
        momapy.sbgn.pd.EquivalenceOperatorLayout,
        {
            "direction": momapy.core.Direction.VERTICAL,
        },
    ),
    (
        momapy.sbgn.pd.GenericProcessLayout,
        {},
    ),
    (
        momapy.sbgn.pd.GenericProcessLayout,
        {
            "direction": momapy.core.Direction.VERTICAL,
        },
    ),
    (
        momapy.sbgn.pd.OmittedProcessLayout,
        {},
    ),
    (
        momapy.sbgn.pd.OmittedProcessLayout,
        {
            "direction": momapy.core.Direction.VERTICAL,
        },
    ),
    (
        momapy.sbgn.pd.UncertainProcessLayout,
        {},
    ),
    (
        momapy.sbgn.pd.UncertainProcessLayout,
        {
            "direction": momapy.core.Direction.VERTICAL,
        },
    ),
    (
        momapy.sbgn.pd.AssociationLayout,
        {},
    ),
    (
        momapy.sbgn.pd.AssociationLayout,
        {
            "direction": momapy.core.Direction.VERTICAL,
        },
    ),
    (
        momapy.sbgn.pd.DissociationLayout,
        {},
    ),
    (
        momapy.sbgn.pd.DissociationLayout,
        {
            "direction": momapy.core.Direction.VERTICAL,
        },
    ),
    (
        momapy.sbgn.pd.PhenotypeLayout,
        {},
    ),
    (
        momapy.sbgn.pd.TagLayout,
        {},
    ),
    (
        momapy.sbgn.pd.TagLayout,
        {"direction": momapy.core.Direction.LEFT},
    ),
    (
        momapy.sbgn.pd.TagLayout,
        {
            "direction": momapy.core.Direction.UP,
            "width": HEIGHT,
            "height": WIDTH,
        },
    ),
    (
        momapy.sbgn.pd.TagLayout,
        {
            "direction": momapy.core.Direction.DOWN,
            "width": HEIGHT,
            "height": WIDTH,
        },
    ),
    (
        momapy.sbgn.af.UnspecifiedEntityUnitOfInformationLayout,
        {},
    ),
    (
        momapy.sbgn.af.SimpleChemicalUnitOfInformationLayout,
        {},
    ),
    (
        momapy.sbgn.af.MacromoleculeUnitOfInformationLayout,
        {},
    ),
    (
        momapy.sbgn.af.NucleicAcidFeatureUnitOfInformationLayout,
        {},
    ),
    (
        momapy.sbgn.af.ComplexUnitOfInformationLayout,
        {},
    ),
    (
        momapy.sbgn.af.TerminalLayout,
        {},
    ),
    (
        momapy.sbgn.af.TerminalLayout,
        {"direction": momapy.core.Direction.LEFT},
    ),
    (
        momapy.sbgn.af.TerminalLayout,
        {
            "direction": momapy.core.Direction.UP,
            "width": HEIGHT,
            "height": WIDTH,
        },
    ),
    (
        momapy.sbgn.af.TerminalLayout,
        {
            "direction": momapy.core.Direction.DOWN,
            "width": HEIGHT,
            "height": WIDTH,
        },
    ),
    (
        momapy.sbgn.af.CompartmentLayout,
        {},
    ),
    (
        momapy.sbgn.af.SubmapLayout,
        {},
    ),
    (
        momapy.sbgn.af.BiologicalActivityLayout,
        {},
    ),
    (
        momapy.sbgn.af.PhenotypeLayout,
        {},
    ),
    (
        momapy.sbgn.af.AndOperatorLayout,
        {},
    ),
    (
        momapy.sbgn.af.AndOperatorLayout,
        {
            "direction": momapy.core.Direction.VERTICAL,
        },
    ),
    (
        momapy.sbgn.af.OrOperatorLayout,
        {},
    ),
    (
        momapy.sbgn.af.OrOperatorLayout,
        {
            "direction": momapy.core.Direction.VERTICAL,
        },
    ),
    (
        momapy.sbgn.af.NotOperatorLayout,
        {},
    ),
    (
        momapy.sbgn.af.NotOperatorLayout,
        {
            "direction": momapy.core.Direction.VERTICAL,
        },
    ),
    (
        momapy.sbgn.af.DelayOperatorLayout,
        {},
    ),
    (
        momapy.sbgn.af.DelayOperatorLayout,
        {
            "direction": momapy.core.Direction.VERTICAL,
        },
    ),
    (
        momapy.sbgn.af.TagLayout,
        {},
    ),
    (
        momapy.sbgn.af.TagLayout,
        {"direction": momapy.core.Direction.LEFT},
    ),
    (
        momapy.sbgn.af.TagLayout,
        {
            "direction": momapy.core.Direction.UP,
            "width": HEIGHT,
            "height": WIDTH,
        },
    ),
    (
        momapy.sbgn.af.TagLayout,
        {
            "direction": momapy.core.Direction.DOWN,
            "width": HEIGHT,
            "height": WIDTH,
        },
    ),
]

momapy.utils.render_nodes_testing(
    "nodes.pdf",
    node_configs,
    WIDTH + 20,
    WIDTH + 20,
    # renderer="svg-native",
    # format="svg",
)
