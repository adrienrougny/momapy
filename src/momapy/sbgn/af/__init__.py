"""SBGN Activity Flow (AF) subpackage facade.

Layout-model mapping catalogue
------------------------------

This section lists, for each model-element category in SBGN-AF, the shape
of the corresponding key in :class:`~momapy.core.LayoutModelMapping`.
See :class:`~momapy.core.LayoutModelMapping` for the general concepts
(singleton keys, frozenset keys, anchors).

Singleton keys (one layout element represents the model element):

+---------------------------------------------------------+-------------------------------------------------------------+
| Model element                                           | Layout element used as the key                              |
+=========================================================+=============================================================+
| :class:`Compartment`                                    | :class:`CompartmentLayout`                                  |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`BiologicalActivity`                             | :class:`BiologicalActivityLayout`                           |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`Phenotype`                                      | :class:`PhenotypeLayout`                                    |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`UnitOfInformation` and subclasses (e.g.         | The corresponding ``*UnitOfInformationLayout`` (e.g.        |
| :class:`MacromoleculeUnitOfInformation`,                | :class:`MacromoleculeUnitOfInformationLayout`,              |
| :class:`NucleicAcidFeatureUnitOfInformation`,           | :class:`PerturbationUnitOfInformationLayout`)               |
| :class:`SimpleChemicalUnitOfInformation`,               |                                                             |
| :class:`ComplexUnitOfInformation`,                      |                                                             |
| :class:`UnspecifiedEntityUnitOfInformation`,            |                                                             |
| :class:`PerturbationUnitOfInformation`)                 |                                                             |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`Submap`                                         | :class:`SubmapLayout`                                       |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`LogicalOperatorInput`                           | :class:`LogicArcLayout`                                     |
+---------------------------------------------------------+-------------------------------------------------------------+
| :class:`TagReference`, :class:`TerminalReference`       | :class:`EquivalenceArcLayout`                               |
+---------------------------------------------------------+-------------------------------------------------------------+

Frozenset keys (a cluster of layout elements jointly represents the
model element; the **anchor** is the layout that stands for the cluster
on its own and must be passed as ``anchor=`` when calling
:meth:`~momapy.core.LayoutModelMappingBuilder.add_mapping`):

+-------------------------------------------------------+-------------------------------------------------------------+----------------------------------+
| Model element                                         | Members of the frozenset key                                | Anchor                           |
+=======================================================+=============================================================+==================================+
| :class:`LogicalOperator` and subclasses (e.g.         | The operator ``*Layout`` (e.g. :class:`AndOperatorLayout`,  | The operator ``*Layout``         |
| :class:`AndOperator`, :class:`OrOperator`,            | :class:`DelayOperatorLayout`) + every                       |                                  |
| :class:`NotOperator`, :class:`DelayOperator`)         | :class:`LogicArcLayout` input + every target layout those   |                                  |
|                                                       | logic arcs point to                                         |                                  |
+-------------------------------------------------------+-------------------------------------------------------------+----------------------------------+
| :class:`Influence` and subclasses (e.g.               | The influence arc layout (e.g.                              | The influence arc layout         |
| :class:`UnknownInfluence`,                            | :class:`UnknownInfluenceLayout`,                            |                                  |
| :class:`PositiveInfluence`,                           | :class:`PositiveInfluenceLayout`,                           |                                  |
| :class:`NegativeInfluence`,                           | :class:`NecessaryStimulationLayout`) + all layouts in the   |                                  |
| :class:`NecessaryStimulation`)                        | source cluster (resolved via the source's own frozenset     |                                  |
|                                                       | key if it has one, else the source layout itself) + all     |                                  |
|                                                       | layouts in the target cluster (resolved the same way)       |                                  |
+-------------------------------------------------------+-------------------------------------------------------------+----------------------------------+
| :class:`Tag` or :class:`Terminal` carrying            | The :class:`TagLayout` or :class:`TerminalLayout` + every   | The :class:`TagLayout` or        |
| :class:`TagReference` or :class:`TerminalReference`   | :class:`EquivalenceArcLayout` reference arc + every         | :class:`TerminalLayout`          |
| arcs                                                  | referenced activity layout                                  |                                  |
+-------------------------------------------------------+-------------------------------------------------------------+----------------------------------+

Standalone :class:`Tag` and :class:`Terminal` instances (with no
reference arcs) use a singleton key: :class:`TagLayout` or
:class:`TerminalLayout`.
"""

from momapy.sbgn.af.model import UnitOfInformation as UnitOfInformation
from momapy.sbgn.af.model import Compartment as Compartment
from momapy.sbgn.af.model import (
    MacromoleculeUnitOfInformation as MacromoleculeUnitOfInformation,
)
from momapy.sbgn.af.model import (
    NucleicAcidFeatureUnitOfInformation as NucleicAcidFeatureUnitOfInformation,
)
from momapy.sbgn.af.model import ComplexUnitOfInformation as ComplexUnitOfInformation
from momapy.sbgn.af.model import (
    SimpleChemicalUnitOfInformation as SimpleChemicalUnitOfInformation,
)
from momapy.sbgn.af.model import (
    UnspecifiedEntityUnitOfInformation as UnspecifiedEntityUnitOfInformation,
)
from momapy.sbgn.af.model import (
    PerturbationUnitOfInformation as PerturbationUnitOfInformation,
)
from momapy.sbgn.af.model import Activity as Activity
from momapy.sbgn.af.model import BiologicalActivity as BiologicalActivity
from momapy.sbgn.af.model import Phenotype as Phenotype
from momapy.sbgn.af.model import LogicalOperatorInput as LogicalOperatorInput
from momapy.sbgn.af.model import LogicalOperator as LogicalOperator
from momapy.sbgn.af.model import OrOperator as OrOperator
from momapy.sbgn.af.model import AndOperator as AndOperator
from momapy.sbgn.af.model import NotOperator as NotOperator
from momapy.sbgn.af.model import DelayOperator as DelayOperator
from momapy.sbgn.af.model import Influence as Influence
from momapy.sbgn.af.model import UnknownInfluence as UnknownInfluence
from momapy.sbgn.af.model import PositiveInfluence as PositiveInfluence
from momapy.sbgn.af.model import NegativeInfluence as NegativeInfluence
from momapy.sbgn.af.model import NecessaryStimulation as NecessaryStimulation
from momapy.sbgn.af.model import TerminalReference as TerminalReference
from momapy.sbgn.af.model import TagReference as TagReference
from momapy.sbgn.af.model import Terminal as Terminal
from momapy.sbgn.af.model import Tag as Tag
from momapy.sbgn.af.model import Submap as Submap
from momapy.sbgn.af.model import SBGNAFModel as SBGNAFModel

from momapy.sbgn.af.layout import SBGNAFLayout as SBGNAFLayout
from momapy.sbgn.af.layout import UnitOfInformationLayout as UnitOfInformationLayout
from momapy.sbgn.af.layout import (
    UnspecifiedEntityUnitOfInformationLayout as UnspecifiedEntityUnitOfInformationLayout,
)
from momapy.sbgn.af.layout import (
    SimpleChemicalUnitOfInformationLayout as SimpleChemicalUnitOfInformationLayout,
)
from momapy.sbgn.af.layout import (
    MacromoleculeUnitOfInformationLayout as MacromoleculeUnitOfInformationLayout,
)
from momapy.sbgn.af.layout import (
    NucleicAcidFeatureUnitOfInformationLayout as NucleicAcidFeatureUnitOfInformationLayout,
)
from momapy.sbgn.af.layout import (
    ComplexUnitOfInformationLayout as ComplexUnitOfInformationLayout,
)
from momapy.sbgn.af.layout import (
    PerturbationUnitOfInformationLayout as PerturbationUnitOfInformationLayout,
)
from momapy.sbgn.af.layout import TerminalLayout as TerminalLayout
from momapy.sbgn.af.layout import CompartmentLayout as CompartmentLayout
from momapy.sbgn.af.layout import SubmapLayout as SubmapLayout
from momapy.sbgn.af.layout import BiologicalActivityLayout as BiologicalActivityLayout
from momapy.sbgn.af.layout import PhenotypeLayout as PhenotypeLayout
from momapy.sbgn.af.layout import AndOperatorLayout as AndOperatorLayout
from momapy.sbgn.af.layout import OrOperatorLayout as OrOperatorLayout
from momapy.sbgn.af.layout import NotOperatorLayout as NotOperatorLayout
from momapy.sbgn.af.layout import DelayOperatorLayout as DelayOperatorLayout
from momapy.sbgn.af.layout import TagLayout as TagLayout
from momapy.sbgn.af.layout import UnknownInfluenceLayout as UnknownInfluenceLayout
from momapy.sbgn.af.layout import PositiveInfluenceLayout as PositiveInfluenceLayout
from momapy.sbgn.af.layout import (
    NecessaryStimulationLayout as NecessaryStimulationLayout,
)
from momapy.sbgn.af.layout import NegativeInfluenceLayout as NegativeInfluenceLayout
from momapy.sbgn.af.layout import LogicArcLayout as LogicArcLayout
from momapy.sbgn.af.layout import EquivalenceArcLayout as EquivalenceArcLayout

from momapy.sbgn.af.map import SBGNAFMap as SBGNAFMap

__all__ = [
    "UnitOfInformation",
    "Compartment",
    "MacromoleculeUnitOfInformation",
    "NucleicAcidFeatureUnitOfInformation",
    "ComplexUnitOfInformation",
    "SimpleChemicalUnitOfInformation",
    "UnspecifiedEntityUnitOfInformation",
    "PerturbationUnitOfInformation",
    "Activity",
    "BiologicalActivity",
    "Phenotype",
    "LogicalOperatorInput",
    "LogicalOperator",
    "OrOperator",
    "AndOperator",
    "NotOperator",
    "DelayOperator",
    "Influence",
    "UnknownInfluence",
    "PositiveInfluence",
    "NegativeInfluence",
    "NecessaryStimulation",
    "TerminalReference",
    "TagReference",
    "Terminal",
    "Tag",
    "Submap",
    "SBGNAFModel",
    "SBGNAFLayout",
    "UnitOfInformationLayout",
    "UnspecifiedEntityUnitOfInformationLayout",
    "SimpleChemicalUnitOfInformationLayout",
    "MacromoleculeUnitOfInformationLayout",
    "NucleicAcidFeatureUnitOfInformationLayout",
    "ComplexUnitOfInformationLayout",
    "PerturbationUnitOfInformationLayout",
    "TerminalLayout",
    "CompartmentLayout",
    "SubmapLayout",
    "BiologicalActivityLayout",
    "PhenotypeLayout",
    "AndOperatorLayout",
    "OrOperatorLayout",
    "NotOperatorLayout",
    "DelayOperatorLayout",
    "TagLayout",
    "UnknownInfluenceLayout",
    "PositiveInfluenceLayout",
    "NecessaryStimulationLayout",
    "NegativeInfluenceLayout",
    "LogicArcLayout",
    "EquivalenceArcLayout",
    "SBGNAFMap",
]
