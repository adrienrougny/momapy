"""Element classification for the CellDesigner reader.

Maps CellDesigner XML element type keys to momapy model and layout
classes.  Mirrors the SBGN-ML reader's ``_reading_classification`` module.
Pure data — depends only on the model and layout classes.
"""

import typing

from momapy.celldesigner.model import AndGate
from momapy.celldesigner.model import AntisenseRNA
from momapy.celldesigner.model import AntisenseRNATemplate
from momapy.celldesigner.model import Catalysis
from momapy.celldesigner.model import Catalyzer
from momapy.celldesigner.model import CodingRegion
from momapy.celldesigner.model import Complex
from momapy.celldesigner.model import Dissociation
from momapy.celldesigner.model import Drug
from momapy.celldesigner.model import Gene
from momapy.celldesigner.model import GeneTemplate
from momapy.celldesigner.model import GenericProtein
from momapy.celldesigner.model import GenericProteinTemplate
from momapy.celldesigner.model import HeterodimerAssociation
from momapy.celldesigner.model import Inhibition
from momapy.celldesigner.model import Inhibitor
from momapy.celldesigner.model import Ion
from momapy.celldesigner.model import IonChannel
from momapy.celldesigner.model import IonChannelTemplate
from momapy.celldesigner.model import KnownTransitionOmitted
from momapy.celldesigner.model import ModificationSite
from momapy.celldesigner.model import Modulation
from momapy.celldesigner.model import Modulator
from momapy.celldesigner.model import NegativeInfluence
from momapy.celldesigner.model import NotGate
from momapy.celldesigner.model import OrGate
from momapy.celldesigner.model import Phenotype
from momapy.celldesigner.model import PhysicalStimulation
from momapy.celldesigner.model import PhysicalStimulator
from momapy.celldesigner.model import PositiveInfluence
from momapy.celldesigner.model import ProteinBindingDomain
from momapy.celldesigner.model import RNA
from momapy.celldesigner.model import RNATemplate
from momapy.celldesigner.model import Receptor
from momapy.celldesigner.model import ReceptorTemplate
from momapy.celldesigner.model import RegulatoryRegion
from momapy.celldesigner.model import SimpleMolecule
from momapy.celldesigner.model import StateTransition
from momapy.celldesigner.model import Transcription
from momapy.celldesigner.model import TranscriptionStartingSiteL
from momapy.celldesigner.model import TranscriptionStartingSiteR
from momapy.celldesigner.model import Translation
from momapy.celldesigner.model import Transport
from momapy.celldesigner.model import Trigger
from momapy.celldesigner.model import Triggering
from momapy.celldesigner.model import TruncatedProtein
from momapy.celldesigner.model import TruncatedProteinTemplate
from momapy.celldesigner.model import Truncation
from momapy.celldesigner.model import Unknown
from momapy.celldesigner.model import UnknownCatalysis
from momapy.celldesigner.model import UnknownCatalyzer
from momapy.celldesigner.model import UnknownGate
from momapy.celldesigner.model import UnknownInhibition
from momapy.celldesigner.model import UnknownInhibitor
from momapy.celldesigner.model import UnknownModulation
from momapy.celldesigner.model import UnknownNegativeInfluence
from momapy.celldesigner.model import UnknownPhysicalStimulation
from momapy.celldesigner.model import UnknownPositiveInfluence
from momapy.celldesigner.model import UnknownTransition
from momapy.celldesigner.model import UnknownTriggering
from momapy.celldesigner.layout import AndGateLayout
from momapy.celldesigner.layout import AntisenseRNALayout
from momapy.celldesigner.layout import CatalysisLayout
from momapy.celldesigner.layout import ComplexLayout
from momapy.celldesigner.layout import DegradedLayout
from momapy.celldesigner.layout import DissociationLayout
from momapy.celldesigner.layout import DrugLayout
from momapy.celldesigner.layout import GeneLayout
from momapy.celldesigner.layout import GenericProteinLayout
from momapy.celldesigner.layout import HeterodimerAssociationLayout
from momapy.celldesigner.layout import InhibitionLayout
from momapy.celldesigner.layout import IonChannelLayout
from momapy.celldesigner.layout import IonLayout
from momapy.celldesigner.layout import KnownTransitionOmittedLayout
from momapy.celldesigner.layout import ModulationLayout
from momapy.celldesigner.layout import NotGateLayout
from momapy.celldesigner.layout import OrGateLayout
from momapy.celldesigner.layout import PhenotypeLayout
from momapy.celldesigner.layout import PhysicalStimulationLayout
from momapy.celldesigner.layout import PositiveInfluenceLayout
from momapy.celldesigner.layout import RNALayout
from momapy.celldesigner.layout import ReceptorLayout
from momapy.celldesigner.layout import SimpleMoleculeLayout
from momapy.celldesigner.layout import StateTransitionLayout
from momapy.celldesigner.layout import TranscriptionLayout
from momapy.celldesigner.layout import TranslationLayout
from momapy.celldesigner.layout import TransportLayout
from momapy.celldesigner.layout import TriggeringLayout
from momapy.celldesigner.layout import TruncatedProteinLayout
from momapy.celldesigner.layout import TruncationLayout
from momapy.celldesigner.layout import UnknownCatalysisLayout
from momapy.celldesigner.layout import UnknownGateLayout
from momapy.celldesigner.layout import UnknownInhibitionLayout
from momapy.celldesigner.layout import UnknownLayout
from momapy.celldesigner.layout import UnknownModulationLayout
from momapy.celldesigner.layout import UnknownPhysicalStimulationLayout
from momapy.celldesigner.layout import UnknownPositiveInfluenceLayout
from momapy.celldesigner.layout import UnknownTransitionLayout
from momapy.celldesigner.layout import UnknownTriggeringLayout


KEY_TO_CLASS = {
    (
        "TEMPLATE",
        "GENERIC",
    ): GenericProteinTemplate,
    (
        "TEMPLATE",
        "ION_CHANNEL",
    ): IonChannelTemplate,
    ("TEMPLATE", "RECEPTOR"): ReceptorTemplate,
    (
        "TEMPLATE",
        "TRUNCATED",
    ): TruncatedProteinTemplate,
    ("TEMPLATE", "GENE"): GeneTemplate,
    ("TEMPLATE", "RNA"): RNATemplate,
    (
        "TEMPLATE",
        "ANTISENSE_RNA",
    ): AntisenseRNATemplate,
    ("SPECIES", "GENERIC"): (
        GenericProtein,
        GenericProteinLayout,
    ),
    ("SPECIES", "ION_CHANNEL"): (
        IonChannel,
        IonChannelLayout,
    ),
    ("SPECIES", "RECEPTOR"): (
        Receptor,
        ReceptorLayout,
    ),
    ("SPECIES", "TRUNCATED"): (
        TruncatedProtein,
        TruncatedProteinLayout,
    ),
    ("SPECIES", "GENE"): (
        Gene,
        GeneLayout,
    ),
    ("SPECIES", "RNA"): (
        RNA,
        RNALayout,
    ),
    ("SPECIES", "ANTISENSE_RNA"): (
        AntisenseRNA,
        AntisenseRNALayout,
    ),
    ("SPECIES", "PHENOTYPE"): (
        Phenotype,
        PhenotypeLayout,
    ),
    ("SPECIES", "ION"): (
        Ion,
        IonLayout,
    ),
    ("SPECIES", "SIMPLE_MOLECULE"): (
        SimpleMolecule,
        SimpleMoleculeLayout,
    ),
    ("SPECIES", "DRUG"): (
        Drug,
        DrugLayout,
    ),
    ("SPECIES", "COMPLEX"): (
        Complex,
        ComplexLayout,
    ),
    ("SPECIES", "UNKNOWN"): (
        Unknown,
        UnknownLayout,
    ),
    ("SPECIES", "DEGRADED"): (
        None,
        DegradedLayout,
    ),
    ("REACTION", "STATE_TRANSITION"): (
        StateTransition,
        StateTransitionLayout,
    ),
    ("REACTION", "KNOWN_TRANSITION_OMITTED"): (
        KnownTransitionOmitted,
        KnownTransitionOmittedLayout,
    ),
    ("REACTION", "UNKNOWN_TRANSITION"): (
        UnknownTransition,
        UnknownTransitionLayout,
    ),
    ("REACTION", "TRANSCRIPTION"): (
        Transcription,
        TranscriptionLayout,
    ),
    ("REACTION", "TRANSLATION"): (
        Translation,
        TranslationLayout,
    ),
    ("REACTION", "TRANSPORT"): (
        Transport,
        TransportLayout,
    ),
    ("REACTION", "HETERODIMER_ASSOCIATION"): (
        HeterodimerAssociation,
        HeterodimerAssociationLayout,
    ),
    ("REACTION", "DISSOCIATION"): (
        Dissociation,
        DissociationLayout,
    ),
    ("REACTION", "TRUNCATION"): (
        Truncation,
        TruncationLayout,
    ),
    ("REACTION", "CATALYSIS"): (
        Catalysis,
        CatalysisLayout,
    ),
    ("REACTION", "UNKNOWN_CATALYSIS"): (
        UnknownCatalysis,
        UnknownCatalysisLayout,
    ),
    ("REACTION", "INHIBITION"): (
        Inhibition,
        InhibitionLayout,
    ),
    ("REACTION", "UNKNOWN_INHIBITION"): (
        UnknownInhibition,
        UnknownInhibitionLayout,
    ),
    ("REACTION", "PHYSICAL_STIMULATION"): (
        PhysicalStimulation,
        PhysicalStimulationLayout,
    ),
    ("REACTION", "MODULATION"): (
        Modulation,
        ModulationLayout,
    ),
    ("REACTION", "TRIGGER"): (
        Triggering,
        TriggeringLayout,
    ),
    ("REACTION", "POSITIVE_INFLUENCE"): (
        PositiveInfluence,
        PositiveInfluenceLayout,
    ),
    ("REACTION", "UNKNOWN_POSITIVE_INFLUENCE"): (
        UnknownPositiveInfluence,
        UnknownPositiveInfluenceLayout,
    ),
    ("REACTION", "NEGATIVE_INFLUENCE"): (
        NegativeInfluence,
        InhibitionLayout,
    ),
    ("REACTION", "UNKNOWN_NEGATIVE_INFLUENCE"): (
        UnknownNegativeInfluence,
        UnknownInhibitionLayout,
    ),
    ("REACTION", "REDUCED_PHYSICAL_STIMULATION"): (
        PhysicalStimulation,
        PhysicalStimulationLayout,
    ),
    ("REACTION", "UNKNOWN_REDUCED_PHYSICAL_STIMULATION"): (
        UnknownPhysicalStimulation,
        UnknownPhysicalStimulationLayout,
    ),
    ("REACTION", "REDUCED_MODULATION"): (
        Modulation,
        ModulationLayout,
    ),
    ("REACTION", "UNKNOWN_REDUCED_MODULATION"): (
        UnknownModulation,
        UnknownModulationLayout,
    ),
    ("REACTION", "REDUCED_TRIGGER"): (
        Triggering,
        TriggeringLayout,
    ),
    ("REACTION", "UNKNOWN_REDUCED_TRIGGER"): (
        UnknownTriggering,
        UnknownTriggeringLayout,
    ),
    # Non-reduced counterparts of the three keys above: the writer emits these
    # when the modulation targets a Phenotype.
    ("REACTION", "UNKNOWN_MODULATION"): (
        UnknownModulation,
        UnknownModulationLayout,
    ),
    ("REACTION", "UNKNOWN_PHYSICAL_STIMULATION"): (
        UnknownPhysicalStimulation,
        UnknownPhysicalStimulationLayout,
    ),
    ("REACTION", "UNKNOWN_TRIGGER"): (
        UnknownTriggering,
        UnknownTriggeringLayout,
    ),
    ("MODIFIER", "CATALYSIS"): (
        Catalyzer,
        CatalysisLayout,
    ),
    ("MODIFIER", "UNKNOWN_CATALYSIS"): (
        UnknownCatalyzer,
        UnknownCatalysisLayout,
    ),
    ("MODIFIER", "INHIBITION"): (
        Inhibitor,
        InhibitionLayout,
    ),
    ("MODIFIER", "UNKNOWN_INHIBITION"): (
        UnknownInhibitor,
        UnknownInhibitionLayout,
    ),
    ("MODIFIER", "PHYSICAL_STIMULATION"): (
        PhysicalStimulator,
        PhysicalStimulationLayout,
    ),
    ("MODIFIER", "MODULATION"): (
        Modulator,
        ModulationLayout,
    ),
    ("MODIFIER", "TRIGGER"): (
        Trigger,
        TriggeringLayout,
    ),
    ("MODIFIER", "POSITIVE_INFLUENCE"): (  # pre-4.0 CellDesigner
        PhysicalStimulator,
        PhysicalStimulationLayout,
    ),
    ("MODIFIER", "NEGATIVE_INFLUENCE"): (  # pre-4.0 CellDesigner
        Inhibitor,
        InhibitionLayout,
    ),
    ("GATE", "BOOLEAN_LOGIC_GATE_AND"): (
        AndGate,
        AndGateLayout,
    ),
    ("GATE", "BOOLEAN_LOGIC_GATE_OR"): (
        OrGate,
        OrGateLayout,
    ),
    ("GATE", "BOOLEAN_LOGIC_GATE_NOT"): (
        NotGate,
        NotGateLayout,
    ),
    (
        "GATE",
        "BOOLEAN_LOGIC_GATE_UNKNOWN",
    ): (
        UnknownGate,
        UnknownGateLayout,
    ),
    (
        "REGION",
        "Modification Site",
    ): ModificationSite,
    (
        "REGION",
        "RegulatoryRegion",
    ): RegulatoryRegion,
    (
        "REGION",
        "transcriptionStartingSiteL",
    ): TranscriptionStartingSiteL,
    (
        "REGION",
        "transcriptionStartingSiteR",
    ): TranscriptionStartingSiteR,
    (
        "REGION",
        "CodingRegion",
    ): CodingRegion,
    (
        "REGION",
        "proteinBindingDomain",
    ): ProteinBindingDomain,
}

# Each table only lists the classes it rewrites; every other class falls
# through `.get(cls, cls)` untouched.
PHENOTYPE_TARGETING_MODULATION_CLASS_TO_NORMALIZED_CLASS = {
    NegativeInfluence: Inhibition,
    UnknownNegativeInfluence: UnknownInhibition,
}

NON_PHENOTYPE_TARGETING_MODULATION_CLASS_TO_NORMALIZED_CLASS = {
    Inhibition: NegativeInfluence,
    UnknownInhibition: UnknownNegativeInfluence,
}


def normalize_modulation_class(
    model_element_cls: type,
    target_model_element: typing.Any,
) -> type:
    """Normalize a negative-modulation class against its target.

    CellDesigner writes a freshly drawn inhibition onto a phenotype as
    ``INHIBITION`` but rewrites it to ``NEGATIVE_INFLUENCE`` on its next save,
    so either spelling can name the same arc. The target decides the class:
    ``Inhibition`` for a `Phenotype` target, ``NegativeInfluence`` otherwise
    (and likewise for the ``Unknown`` counterparts). This is the inverse of
    ``get_modulation_reaction_type`` in ``_writing.py``.

    Args:
        model_element_cls: The class picked from `KEY_TO_CLASS`.
        target_model_element: The modulation's target model element.

    Returns:
        The normalized class, or `model_element_cls` unchanged when it is not
        one of the negative-modulation classes.
    """
    if isinstance(target_model_element, Phenotype):
        return PHENOTYPE_TARGETING_MODULATION_CLASS_TO_NORMALIZED_CLASS.get(
            model_element_cls, model_element_cls
        )
    return NON_PHENOTYPE_TARGETING_MODULATION_CLASS_TO_NORMALIZED_CLASS.get(
        model_element_cls, model_element_cls
    )
