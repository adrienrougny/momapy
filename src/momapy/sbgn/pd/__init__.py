"""SBGN Process Description (PD) subpackage facade.

Layout-model mapping catalogue
------------------------------

This section lists, for each model-element category in SBGN-PD, the shape
of the corresponding key in :class:`~momapy.core.LayoutModelMapping`.
See :class:`~momapy.core.LayoutModelMapping` for the general concepts
(singleton keys, frozenset keys, anchors).

Singleton keys (one layout element represents the model element):

+---------------------------------------------------------+-------------------------------------------------------------+
| Model element                                           | Layout element used as the key                              |
+=========================================================+=============================================================+
| :class:`Compartment`                                    | :class:`CompartmentLayout`                                  |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`EntityPool` and subclasses (e.g.                | The corresponding ``*Layout`` (e.g.                         |
| :class:`Macromolecule`, :class:`NucleicAcidFeature`,    | :class:`MacromoleculeLayout`, :class:`ComplexLayout`,       |
| :class:`SimpleChemical`, :class:`Complex`,              | :class:`EmptySetLayout`, :class:`PerturbingAgentLayout`)    |
| :class:`UnspecifiedEntity`, :class:`EmptySet`,          |                                                             |
| :class:`PerturbingAgent`, and every                     |                                                             |
| :class:`Multimer` variant)                              |                                                             |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`Subunit` and subclasses                         | The corresponding ``*SubunitLayout``                        |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`StateVariable`                                  | :class:`StateVariableLayout`                                |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`UnitOfInformation`                              | :class:`UnitOfInformationLayout`                            |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`Submap`                                         | :class:`SubmapLayout`                                       |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`Reactant`                                       | :class:`ConsumptionLayout`                                  |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`Product`                                        | :class:`ProductionLayout`                                   |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`LogicalOperatorInput`                           | :class:`LogicArcLayout`                                     |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`TagReference`, :class:`TerminalReference`       | :class:`EquivalenceArcLayout`                               |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`Phenotype`                                      | :class:`PhenotypeLayout`                                    |
+---------------------------------------------------------+-------------------------------------------------------------+

Frozenset keys (a cluster of layout elements jointly represents the
model element; the **anchor** is the layout that stands for the cluster
on its own and must be passed as ``anchor=`` when calling
:meth:`~momapy.core.LayoutModelMappingBuilder.add_mapping`):

+-------------------------------------------------------+-------------------------------------------------------------+----------------------------------+
| Model element                                         | Members of the frozenset key                                | Anchor                           |
+=======================================================+=============================================================+==================================+
| :class:`Process` and subclasses (e.g.                 | The process ``*Layout`` (e.g.                               | The process ``*Layout``          |
| :class:`StoichiometricProcess`,                       | :class:`GenericProcessLayout`, :class:`AssociationLayout`,  |                                  |
| :class:`GenericProcess`,                              | :class:`DissociationLayout`) + every                        |                                  |
| :class:`UncertainProcess`,                            | :class:`ConsumptionLayout` and :class:`ProductionLayout`    |                                  |
| :class:`Association`, :class:`Dissociation`,          | attached to the process + every target layout (the          |                                  |
| :class:`OmittedProcess`)                              | entity-pool layouts those arcs point to)                    |                                  |
+-------------------------------------------------------+-------------------------------------------------------------+----------------------------------+
| :class:`LogicalOperator` and subclasses (e.g.         | The operator ``*Layout`` (e.g. :class:`AndOperatorLayout`,  | The operator ``*Layout``         |
| :class:`AndOperator`, :class:`OrOperator`,            | :class:`OrOperatorLayout`) + every :class:`LogicArcLayout`  |                                  |
| :class:`NotOperator`, :class:`EquivalenceOperator`)   | input + every target layout those logic arcs point to       |                                  |
+-------------------------------------------------------+-------------------------------------------------------------+----------------------------------+
| :class:`Modulation` and subclasses (e.g.              | The modulation arc layout (e.g.                             | The modulation arc layout        |
| :class:`Stimulation`, :class:`Inhibition`,            | :class:`ModulationLayout`, :class:`StimulationLayout`,      |                                  |
| :class:`Catalysis`, :class:`NecessaryStimulation`)    | :class:`InhibitionLayout`) + all layouts in the source      |                                  |
|                                                       | cluster (resolved via the source's own frozenset key if it  |                                  |
|                                                       | has one, else the source layout itself) + all layouts in    |                                  |
|                                                       | the target cluster (resolved the same way)                  |                                  |
+-------------------------------------------------------+-------------------------------------------------------------+----------------------------------+
| :class:`Tag` or :class:`Terminal` carrying            | The :class:`TagLayout` or :class:`TerminalLayout` + every   | The :class:`TagLayout` or        |
| :class:`TagReference` or :class:`TerminalReference`   | :class:`EquivalenceArcLayout` reference arc + every         | :class:`TerminalLayout`          |
| arcs                                                  | referenced entity layout                                    |                                  |
+-------------------------------------------------------+-------------------------------------------------------------+----------------------------------+

Standalone :class:`Tag` and :class:`Terminal` instances (with no
reference arcs) use a singleton key: :class:`TagLayout` or
:class:`TerminalLayout`.
"""

from momapy.sbgn.pd.model import StateVariable as StateVariable
from momapy.sbgn.pd.model import UnitOfInformation as UnitOfInformation
from momapy.sbgn.pd.model import Subunit as Subunit
from momapy.sbgn.pd.model import UnspecifiedEntitySubunit as UnspecifiedEntitySubunit
from momapy.sbgn.pd.model import MacromoleculeSubunit as MacromoleculeSubunit
from momapy.sbgn.pd.model import NucleicAcidFeatureSubunit as NucleicAcidFeatureSubunit
from momapy.sbgn.pd.model import SimpleChemicalSubunit as SimpleChemicalSubunit
from momapy.sbgn.pd.model import ComplexSubunit as ComplexSubunit
from momapy.sbgn.pd.model import MultimerSubunit as MultimerSubunit
from momapy.sbgn.pd.model import (
    MacromoleculeMultimerSubunit as MacromoleculeMultimerSubunit,
)
from momapy.sbgn.pd.model import (
    NucleicAcidFeatureMultimerSubunit as NucleicAcidFeatureMultimerSubunit,
)
from momapy.sbgn.pd.model import (
    SimpleChemicalMultimerSubunit as SimpleChemicalMultimerSubunit,
)
from momapy.sbgn.pd.model import ComplexMultimerSubunit as ComplexMultimerSubunit
from momapy.sbgn.pd.model import Compartment as Compartment
from momapy.sbgn.pd.model import EntityPool as EntityPool
from momapy.sbgn.pd.model import EmptySet as EmptySet
from momapy.sbgn.pd.model import PerturbingAgent as PerturbingAgent
from momapy.sbgn.pd.model import UnspecifiedEntity as UnspecifiedEntity
from momapy.sbgn.pd.model import Macromolecule as Macromolecule
from momapy.sbgn.pd.model import NucleicAcidFeature as NucleicAcidFeature
from momapy.sbgn.pd.model import SimpleChemical as SimpleChemical
from momapy.sbgn.pd.model import Complex as Complex
from momapy.sbgn.pd.model import Multimer as Multimer
from momapy.sbgn.pd.model import MacromoleculeMultimer as MacromoleculeMultimer
from momapy.sbgn.pd.model import (
    NucleicAcidFeatureMultimer as NucleicAcidFeatureMultimer,
)
from momapy.sbgn.pd.model import SimpleChemicalMultimer as SimpleChemicalMultimer
from momapy.sbgn.pd.model import ComplexMultimer as ComplexMultimer
from momapy.sbgn.pd.model import FluxRole as FluxRole
from momapy.sbgn.pd.model import Reactant as Reactant
from momapy.sbgn.pd.model import Product as Product
from momapy.sbgn.pd.model import LogicalOperatorInput as LogicalOperatorInput
from momapy.sbgn.pd.model import EquivalenceOperatorInput as EquivalenceOperatorInput
from momapy.sbgn.pd.model import EquivalenceOperatorOutput as EquivalenceOperatorOutput
from momapy.sbgn.pd.model import Process as Process
from momapy.sbgn.pd.model import StoichiometricProcess as StoichiometricProcess
from momapy.sbgn.pd.model import GenericProcess as GenericProcess
from momapy.sbgn.pd.model import UncertainProcess as UncertainProcess
from momapy.sbgn.pd.model import Association as Association
from momapy.sbgn.pd.model import Dissociation as Dissociation
from momapy.sbgn.pd.model import OmittedProcess as OmittedProcess
from momapy.sbgn.pd.model import Phenotype as Phenotype
from momapy.sbgn.pd.model import LogicalOperator as LogicalOperator
from momapy.sbgn.pd.model import OrOperator as OrOperator
from momapy.sbgn.pd.model import AndOperator as AndOperator
from momapy.sbgn.pd.model import NotOperator as NotOperator
from momapy.sbgn.pd.model import EquivalenceOperator as EquivalenceOperator
from momapy.sbgn.pd.model import Modulation as Modulation
from momapy.sbgn.pd.model import Inhibition as Inhibition
from momapy.sbgn.pd.model import Stimulation as Stimulation
from momapy.sbgn.pd.model import Catalysis as Catalysis
from momapy.sbgn.pd.model import NecessaryStimulation as NecessaryStimulation
from momapy.sbgn.pd.model import TagReference as TagReference
from momapy.sbgn.pd.model import Tag as Tag
from momapy.sbgn.pd.model import TerminalReference as TerminalReference
from momapy.sbgn.pd.model import Terminal as Terminal
from momapy.sbgn.pd.model import Submap as Submap
from momapy.sbgn.pd.model import SBGNPDModel as SBGNPDModel

from momapy.sbgn.pd.layout import SBGNPDLayout as SBGNPDLayout
from momapy.sbgn.pd.layout import StateVariableLayout as StateVariableLayout
from momapy.sbgn.pd.layout import UnitOfInformationLayout as UnitOfInformationLayout
from momapy.sbgn.pd.layout import TerminalLayout as TerminalLayout
from momapy.sbgn.pd.layout import CardinalityLayout as CardinalityLayout
from momapy.sbgn.pd.layout import (
    UnspecifiedEntitySubunitLayout as UnspecifiedEntitySubunitLayout,
)
from momapy.sbgn.pd.layout import (
    SimpleChemicalSubunitLayout as SimpleChemicalSubunitLayout,
)
from momapy.sbgn.pd.layout import (
    MacromoleculeSubunitLayout as MacromoleculeSubunitLayout,
)
from momapy.sbgn.pd.layout import (
    NucleicAcidFeatureSubunitLayout as NucleicAcidFeatureSubunitLayout,
)
from momapy.sbgn.pd.layout import ComplexSubunitLayout as ComplexSubunitLayout
from momapy.sbgn.pd.layout import (
    SimpleChemicalMultimerSubunitLayout as SimpleChemicalMultimerSubunitLayout,
)
from momapy.sbgn.pd.layout import (
    MacromoleculeMultimerSubunitLayout as MacromoleculeMultimerSubunitLayout,
)
from momapy.sbgn.pd.layout import (
    NucleicAcidFeatureMultimerSubunitLayout as NucleicAcidFeatureMultimerSubunitLayout,
)
from momapy.sbgn.pd.layout import (
    ComplexMultimerSubunitLayout as ComplexMultimerSubunitLayout,
)
from momapy.sbgn.pd.layout import CompartmentLayout as CompartmentLayout
from momapy.sbgn.pd.layout import SubmapLayout as SubmapLayout
from momapy.sbgn.pd.layout import UnspecifiedEntityLayout as UnspecifiedEntityLayout
from momapy.sbgn.pd.layout import SimpleChemicalLayout as SimpleChemicalLayout
from momapy.sbgn.pd.layout import MacromoleculeLayout as MacromoleculeLayout
from momapy.sbgn.pd.layout import NucleicAcidFeatureLayout as NucleicAcidFeatureLayout
from momapy.sbgn.pd.layout import ComplexLayout as ComplexLayout
from momapy.sbgn.pd.layout import (
    SimpleChemicalMultimerLayout as SimpleChemicalMultimerLayout,
)
from momapy.sbgn.pd.layout import (
    MacromoleculeMultimerLayout as MacromoleculeMultimerLayout,
)
from momapy.sbgn.pd.layout import (
    NucleicAcidFeatureMultimerLayout as NucleicAcidFeatureMultimerLayout,
)
from momapy.sbgn.pd.layout import ComplexMultimerLayout as ComplexMultimerLayout
from momapy.sbgn.pd.layout import EmptySetLayout as EmptySetLayout
from momapy.sbgn.pd.layout import PerturbingAgentLayout as PerturbingAgentLayout
from momapy.sbgn.pd.layout import AndOperatorLayout as AndOperatorLayout
from momapy.sbgn.pd.layout import OrOperatorLayout as OrOperatorLayout
from momapy.sbgn.pd.layout import NotOperatorLayout as NotOperatorLayout
from momapy.sbgn.pd.layout import EquivalenceOperatorLayout as EquivalenceOperatorLayout
from momapy.sbgn.pd.layout import GenericProcessLayout as GenericProcessLayout
from momapy.sbgn.pd.layout import OmittedProcessLayout as OmittedProcessLayout
from momapy.sbgn.pd.layout import UncertainProcessLayout as UncertainProcessLayout
from momapy.sbgn.pd.layout import AssociationLayout as AssociationLayout
from momapy.sbgn.pd.layout import DissociationLayout as DissociationLayout
from momapy.sbgn.pd.layout import PhenotypeLayout as PhenotypeLayout
from momapy.sbgn.pd.layout import TagLayout as TagLayout
from momapy.sbgn.pd.layout import ConsumptionLayout as ConsumptionLayout
from momapy.sbgn.pd.layout import ProductionLayout as ProductionLayout
from momapy.sbgn.pd.layout import ModulationLayout as ModulationLayout
from momapy.sbgn.pd.layout import StimulationLayout as StimulationLayout
from momapy.sbgn.pd.layout import (
    NecessaryStimulationLayout as NecessaryStimulationLayout,
)
from momapy.sbgn.pd.layout import CatalysisLayout as CatalysisLayout
from momapy.sbgn.pd.layout import InhibitionLayout as InhibitionLayout
from momapy.sbgn.pd.layout import LogicArcLayout as LogicArcLayout
from momapy.sbgn.pd.layout import EquivalenceArcLayout as EquivalenceArcLayout

from momapy.sbgn.pd.map import SBGNPDMap as SBGNPDMap

__all__ = [
    "StateVariable",
    "UnitOfInformation",
    "Subunit",
    "UnspecifiedEntitySubunit",
    "MacromoleculeSubunit",
    "NucleicAcidFeatureSubunit",
    "SimpleChemicalSubunit",
    "ComplexSubunit",
    "MultimerSubunit",
    "MacromoleculeMultimerSubunit",
    "NucleicAcidFeatureMultimerSubunit",
    "SimpleChemicalMultimerSubunit",
    "ComplexMultimerSubunit",
    "Compartment",
    "EntityPool",
    "EmptySet",
    "PerturbingAgent",
    "UnspecifiedEntity",
    "Macromolecule",
    "NucleicAcidFeature",
    "SimpleChemical",
    "Complex",
    "Multimer",
    "MacromoleculeMultimer",
    "NucleicAcidFeatureMultimer",
    "SimpleChemicalMultimer",
    "ComplexMultimer",
    "FluxRole",
    "Reactant",
    "Product",
    "LogicalOperatorInput",
    "EquivalenceOperatorInput",
    "EquivalenceOperatorOutput",
    "Process",
    "StoichiometricProcess",
    "GenericProcess",
    "UncertainProcess",
    "Association",
    "Dissociation",
    "OmittedProcess",
    "Phenotype",
    "LogicalOperator",
    "OrOperator",
    "AndOperator",
    "NotOperator",
    "EquivalenceOperator",
    "Modulation",
    "Inhibition",
    "Stimulation",
    "Catalysis",
    "NecessaryStimulation",
    "TagReference",
    "Tag",
    "TerminalReference",
    "Terminal",
    "Submap",
    "SBGNPDModel",
    "SBGNPDLayout",
    "StateVariableLayout",
    "UnitOfInformationLayout",
    "TerminalLayout",
    "CardinalityLayout",
    "UnspecifiedEntitySubunitLayout",
    "SimpleChemicalSubunitLayout",
    "MacromoleculeSubunitLayout",
    "NucleicAcidFeatureSubunitLayout",
    "ComplexSubunitLayout",
    "SimpleChemicalMultimerSubunitLayout",
    "MacromoleculeMultimerSubunitLayout",
    "NucleicAcidFeatureMultimerSubunitLayout",
    "ComplexMultimerSubunitLayout",
    "CompartmentLayout",
    "SubmapLayout",
    "UnspecifiedEntityLayout",
    "SimpleChemicalLayout",
    "MacromoleculeLayout",
    "NucleicAcidFeatureLayout",
    "ComplexLayout",
    "SimpleChemicalMultimerLayout",
    "MacromoleculeMultimerLayout",
    "NucleicAcidFeatureMultimerLayout",
    "ComplexMultimerLayout",
    "EmptySetLayout",
    "PerturbingAgentLayout",
    "AndOperatorLayout",
    "OrOperatorLayout",
    "NotOperatorLayout",
    "EquivalenceOperatorLayout",
    "GenericProcessLayout",
    "OmittedProcessLayout",
    "UncertainProcessLayout",
    "AssociationLayout",
    "DissociationLayout",
    "PhenotypeLayout",
    "TagLayout",
    "ConsumptionLayout",
    "ProductionLayout",
    "ModulationLayout",
    "StimulationLayout",
    "NecessaryStimulationLayout",
    "CatalysisLayout",
    "InhibitionLayout",
    "LogicArcLayout",
    "EquivalenceArcLayout",
    "SBGNPDMap",
]
