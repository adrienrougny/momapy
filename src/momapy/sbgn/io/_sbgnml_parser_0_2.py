from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ArcClass(Enum):
    PRODUCTION = "production"
    CONSUMPTION = "consumption"
    CATALYSIS = "catalysis"
    MODULATION = "modulation"
    STIMULATION = "stimulation"
    INHIBITION = "inhibition"
    ASSIGNMENT = "assignment"
    INTERACTION = "interaction"
    ABSOLUTE_INHIBITION = "absolute inhibition"
    ABSOLUTE_STIMULATION = "absolute stimulation"
    POSITIVE_INFLUENCE = "positive influence"
    NEGATIVE_INFLUENCE = "negative influence"
    UNKNOWN_INFLUENCE = "unknown influence"
    EQUIVALENCE_ARC = "equivalence arc"
    NECESSARY_STIMULATION = "necessary stimulation"
    LOGIC_ARC = "logic arc"


class ArcgroupClass(Enum):
    INTERACTION = "interaction"


class EntityName(Enum):
    UNSPECIFIED_ENTITY = "unspecified entity"
    SIMPLE_CHEMICAL = "simple chemical"
    MACROMOLECULE = "macromolecule"
    NUCLEIC_ACID_FEATURE = "nucleic acid feature"
    COMPLEX = "complex"
    PERTURBATION = "perturbation"


class GlyphClass(Enum):
    UNSPECIFIED_ENTITY = "unspecified entity"
    SIMPLE_CHEMICAL = "simple chemical"
    MACROMOLECULE = "macromolecule"
    NUCLEIC_ACID_FEATURE = "nucleic acid feature"
    SIMPLE_CHEMICAL_MULTIMER = "simple chemical multimer"
    MACROMOLECULE_MULTIMER = "macromolecule multimer"
    NUCLEIC_ACID_FEATURE_MULTIMER = "nucleic acid feature multimer"
    COMPLEX = "complex"
    COMPLEX_MULTIMER = "complex multimer"
    SOURCE_AND_SINK = "source and sink"
    PERTURBATION = "perturbation"
    BIOLOGICAL_ACTIVITY = "biological activity"
    PERTURBING_AGENT = "perturbing agent"
    COMPARTMENT = "compartment"
    SUBMAP = "submap"
    TAG = "tag"
    TERMINAL = "terminal"
    PROCESS = "process"
    OMITTED_PROCESS = "omitted process"
    UNCERTAIN_PROCESS = "uncertain process"
    ASSOCIATION = "association"
    DISSOCIATION = "dissociation"
    PHENOTYPE = "phenotype"
    AND = "and"
    OR = "or"
    NOT = "not"
    STATE_VARIABLE = "state variable"
    UNIT_OF_INFORMATION = "unit of information"
    ENTITY = "entity"
    OUTCOME = "outcome"
    INTERACTION = "interaction"
    INFLUENCE_TARGET = "influence target"
    ANNOTATION = "annotation"
    VARIABLE_VALUE = "variable value"
    IMPLICIT_XOR = "implicit xor"
    DELAY = "delay"
    EXISTENCE = "existence"
    LOCATION = "location"
    CARDINALITY = "cardinality"
    OBSERVABLE = "observable"


class GlyphOrientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


class MapLanguage(Enum):
    ENTITY_RELATIONSHIP = "entity relationship"
    PROCESS_DESCRIPTION = "process description"
    ACTIVITY_FLOW = "activity flow"


@dataclass
class ColorDefinitionType:
    class Meta:
        name = "colorDefinitionType"
        target_namespace = "http://www.sbml.org/sbml/level3/version1/render/version1"

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class GType:
    class Meta:
        name = "gType"
        target_namespace = "http://www.sbml.org/sbml/level3/version1/render/version1"

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    font_family: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-family",
            "type": "Attribute",
        }
    )
    font_size: Optional[float] = field(
        default=None,
        metadata={
            "name": "font-size",
            "type": "Attribute",
        }
    )
    font_weight: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-weight",
            "type": "Attribute",
        }
    )
    font_style: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-style",
            "type": "Attribute",
        }
    )
    font_color: Optional[str] = field(
        default=None,
        metadata={
            "name": "font-color",
            "type": "Attribute",
        }
    )
    stroke: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    stroke_width: Optional[float] = field(
        default=None,
        metadata={
            "name": "stroke-width",
            "type": "Attribute",
        }
    )
    background_image_opacity: Optional[str] = field(
        default=None,
        metadata={
            "name": "background-image-opacity",
            "type": "Attribute",
        }
    )
    background_opacity: Optional[str] = field(
        default=None,
        metadata={
            "name": "background-opacity",
            "type": "Attribute",
        }
    )
    fill: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class ListOfBackgroundImagesType:
    class Meta:
        name = "listOfBackgroundImagesType"
        target_namespace = "http://www.sbml.org/sbml/level3/version1/render/version1"

    any_element: List[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
        }
    )


@dataclass
class LiType:
    class Meta:
        name = "liType"
        target_namespace = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

    resource: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class ListOfColorDefinitionsType:
    class Meta:
        name = "listOfColorDefinitionsType"
        target_namespace = "http://www.sbml.org/sbml/level3/version1/render/version1"

    color_definition: List[ColorDefinitionType] = field(
        default_factory=list,
        metadata={
            "name": "colorDefinition",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level3/version1/render/version1",
        }
    )


@dataclass
class StyleType:
    class Meta:
        name = "styleType"
        target_namespace = "http://www.sbml.org/sbml/level3/version1/render/version1"

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    id_list: Optional[str] = field(
        default=None,
        metadata={
            "name": "idList",
            "type": "Attribute",
        }
    )
    g: Optional[GType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level3/version1/render/version1",
            "required": True,
        }
    )


@dataclass
class BagType:
    class Meta:
        target_namespace = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

    li: List[LiType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class ListOfStylesType:
    class Meta:
        name = "listOfStylesType"
        target_namespace = "http://www.sbml.org/sbml/level3/version1/render/version1"

    style: List[StyleType] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level3/version1/render/version1",
        }
    )


@dataclass
class Bag(BagType):
    class Meta:
        namespace = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


@dataclass
class EncodesType:
    class Meta:
        name = "encodesType"
        target_namespace = "http://biomodels.net/biology-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class HasPartType:
    class Meta:
        name = "hasPartType"
        target_namespace = "http://biomodels.net/biology-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class HasPropertyType:
    class Meta:
        name = "hasPropertyType"
        target_namespace = "http://biomodels.net/biology-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class HasTaxonType:
    class Meta:
        name = "hasTaxonType"
        target_namespace = "http://biomodels.net/biology-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class HasVersionType:
    class Meta:
        name = "hasVersionType"
        target_namespace = "http://biomodels.net/biology-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class IsDescribedByType1:
    class Meta:
        name = "isDescribedByType"
        target_namespace = "http://biomodels.net/biology-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class IsEncodedByType:
    class Meta:
        name = "isEncodedByType"
        target_namespace = "http://biomodels.net/biology-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class IsHomologToType:
    class Meta:
        name = "isHomologToType"
        target_namespace = "http://biomodels.net/biology-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class IsPartOfType:
    class Meta:
        name = "isPartOfType"
        target_namespace = "http://biomodels.net/biology-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class IsPropertyOfType:
    class Meta:
        name = "isPropertyOfType"
        target_namespace = "http://biomodels.net/biology-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class IsType1:
    class Meta:
        name = "isType"
        target_namespace = "http://biomodels.net/biology-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class IsVersionOfType:
    class Meta:
        name = "isVersionOfType"
        target_namespace = "http://biomodels.net/biology-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class OccursInType:
    class Meta:
        name = "occursInType"
        target_namespace = "http://biomodels.net/biology-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class HasInstanceType:
    class Meta:
        name = "hasInstanceType"
        target_namespace = "http://biomodels.net/model-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class IsDerivedFromType:
    class Meta:
        name = "isDerivedFromType"
        target_namespace = "http://biomodels.net/model-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class IsDescribedByType2:
    class Meta:
        name = "isDescribedByType"
        target_namespace = "http://biomodels.net/model-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class IsInstanceOfType:
    class Meta:
        name = "isInstanceOfType"
        target_namespace = "http://biomodels.net/model-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class IsType2:
    class Meta:
        name = "isType"
        target_namespace = "http://biomodels.net/model-qualifiers/"

    bag: Optional[Bag] = field(
        default=None,
        metadata={
            "name": "Bag",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class RenderInformationType:
    class Meta:
        name = "renderInformationType"
        target_namespace = "http://www.sbml.org/sbml/level3/version1/render/version1"

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    program_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "program-name",
            "type": "Attribute",
        }
    )
    program_version: Optional[str] = field(
        default=None,
        metadata={
            "name": "program-version",
            "type": "Attribute",
        }
    )
    background_color: Optional[str] = field(
        default=None,
        metadata={
            "name": "background-color",
            "type": "Attribute",
        }
    )
    list_of_color_definitions: Optional[ListOfColorDefinitionsType] = field(
        default=None,
        metadata={
            "name": "listOfColorDefinitions",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level3/version1/render/version1",
        }
    )
    list_of_styles: Optional[ListOfStylesType] = field(
        default=None,
        metadata={
            "name": "listOfStyles",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level3/version1/render/version1",
        }
    )
    list_of_background_images: Optional[ListOfBackgroundImagesType] = field(
        default=None,
        metadata={
            "name": "listOfBackgroundImages",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level3/version1/render/version1",
        }
    )


@dataclass
class Encodes(EncodesType):
    class Meta:
        name = "encodes"
        namespace = "http://biomodels.net/biology-qualifiers/"


@dataclass
class HasPart(HasPartType):
    class Meta:
        name = "hasPart"
        namespace = "http://biomodels.net/biology-qualifiers/"


@dataclass
class HasProperty(HasPropertyType):
    class Meta:
        name = "hasProperty"
        namespace = "http://biomodels.net/biology-qualifiers/"


@dataclass
class HasTaxon(HasTaxonType):
    class Meta:
        name = "hasTaxon"
        namespace = "http://biomodels.net/biology-qualifiers/"


@dataclass
class HasVersion(HasVersionType):
    class Meta:
        name = "hasVersion"
        namespace = "http://biomodels.net/biology-qualifiers/"


@dataclass
class IsDescribedBy1(IsDescribedByType1):
    class Meta:
        name = "isDescribedBy"
        namespace = "http://biomodels.net/biology-qualifiers/"


@dataclass
class IsEncodedBy(IsEncodedByType):
    class Meta:
        name = "isEncodedBy"
        namespace = "http://biomodels.net/biology-qualifiers/"


@dataclass
class IsHomologTo(IsHomologToType):
    class Meta:
        name = "isHomologTo"
        namespace = "http://biomodels.net/biology-qualifiers/"


@dataclass
class IsPartOf(IsPartOfType):
    class Meta:
        name = "isPartOf"
        namespace = "http://biomodels.net/biology-qualifiers/"


@dataclass
class IsPropertyOf(IsPropertyOfType):
    class Meta:
        name = "isPropertyOf"
        namespace = "http://biomodels.net/biology-qualifiers/"


@dataclass
class IsVersionOf(IsVersionOfType):
    class Meta:
        name = "isVersionOf"
        namespace = "http://biomodels.net/biology-qualifiers/"


@dataclass
class Is1(IsType1):
    class Meta:
        name = "is"
        namespace = "http://biomodels.net/biology-qualifiers/"


@dataclass
class OccursIn(OccursInType):
    class Meta:
        name = "occursIn"
        namespace = "http://biomodels.net/biology-qualifiers/"


@dataclass
class HasInstance(HasInstanceType):
    class Meta:
        name = "hasInstance"
        namespace = "http://biomodels.net/model-qualifiers/"


@dataclass
class IsDerivedFrom(IsDerivedFromType):
    class Meta:
        name = "isDerivedFrom"
        namespace = "http://biomodels.net/model-qualifiers/"


@dataclass
class IsDescribedBy2(IsDescribedByType2):
    class Meta:
        name = "isDescribedBy"
        namespace = "http://biomodels.net/model-qualifiers/"


@dataclass
class IsInstanceOf(IsInstanceOfType):
    class Meta:
        name = "isInstanceOf"
        namespace = "http://biomodels.net/model-qualifiers/"


@dataclass
class Is2(IsType2):
    class Meta:
        name = "is"
        namespace = "http://biomodels.net/model-qualifiers/"


@dataclass
class RenderInformation(RenderInformationType):
    class Meta:
        name = "renderInformation"
        namespace = "http://www.sbml.org/sbml/level3/version1/render/version1"


@dataclass
class DescriptionType:
    class Meta:
        target_namespace = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

    encodes: List[Encodes] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    has_part: List[HasPart] = field(
        default_factory=list,
        metadata={
            "name": "hasPart",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    has_property: List[HasProperty] = field(
        default_factory=list,
        metadata={
            "name": "hasProperty",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    has_version: List[HasVersion] = field(
        default_factory=list,
        metadata={
            "name": "hasVersion",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_value: List[Is1] = field(
        default_factory=list,
        metadata={
            "name": "is",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_described_by: List[IsDescribedBy1] = field(
        default_factory=list,
        metadata={
            "name": "isDescribedBy",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_encoded_by: List[IsEncodedBy] = field(
        default_factory=list,
        metadata={
            "name": "isEncodedBy",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_homolog_to: List[IsHomologTo] = field(
        default_factory=list,
        metadata={
            "name": "isHomologTo",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_part_of: List[IsPartOf] = field(
        default_factory=list,
        metadata={
            "name": "isPartOf",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_property_of: List[IsPropertyOf] = field(
        default_factory=list,
        metadata={
            "name": "isPropertyOf",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_version_of: List[IsVersionOf] = field(
        default_factory=list,
        metadata={
            "name": "isVersionOf",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    occurs_in: List[OccursIn] = field(
        default_factory=list,
        metadata={
            "name": "occursIn",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    has_taxon: List[HasTaxon] = field(
        default_factory=list,
        metadata={
            "name": "hasTaxon",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    has_instance: List[HasInstance] = field(
        default_factory=list,
        metadata={
            "name": "hasInstance",
            "type": "Element",
            "namespace": "http://biomodels.net/model-qualifiers/",
        }
    )
    biomodels_net_model_qualifiers_is: List[Is2] = field(
        default_factory=list,
        metadata={
            "name": "is",
            "type": "Element",
            "namespace": "http://biomodels.net/model-qualifiers/",
        }
    )
    is_derived_from: List[IsDerivedFrom] = field(
        default_factory=list,
        metadata={
            "name": "isDerivedFrom",
            "type": "Element",
            "namespace": "http://biomodels.net/model-qualifiers/",
        }
    )
    biomodels_net_model_qualifiers_is_described_by: List[IsDescribedBy2] = field(
        default_factory=list,
        metadata={
            "name": "isDescribedBy",
            "type": "Element",
            "namespace": "http://biomodels.net/model-qualifiers/",
        }
    )
    is_instance_of: List[IsInstanceOf] = field(
        default_factory=list,
        metadata={
            "name": "isInstanceOf",
            "type": "Element",
            "namespace": "http://biomodels.net/model-qualifiers/",
        }
    )
    any_element: List[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "process_contents": "skip",
        }
    )
    about: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class Rdftype:
    class Meta:
        name = "RDFType"
        target_namespace = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

    description: Optional[DescriptionType] = field(
        default=None,
        metadata={
            "name": "Description",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )
    any_element: List[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "process_contents": "skip",
        }
    )


@dataclass
class Rdf(Rdftype):
    class Meta:
        name = "RDF"
        namespace = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


@dataclass
class AnnotationType:
    class Meta:
        name = "annotationType"
        target_namespace = "http://sbgn.org/libsbgn/0.2"

    rdf: Optional[Rdf] = field(
        default=None,
        metadata={
            "name": "RDF",
            "type": "Element",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )


@dataclass
class Annotation(AnnotationType):
    class Meta:
        name = "annotation"
        namespace = "http://sbgn.org/libsbgn/0.2"


@dataclass
class Sbgnbase:
    """The SBGNBase type is the base type of all main components in SBGN.

    It supports attaching metadata, notes and annotations to components.
    """
    class Meta:
        name = "SBGNBase"
        target_namespace = "http://sbgn.org/libsbgn/0.2"

    notes: Optional["Sbgnbase.Notes"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://sbgn.org/libsbgn/0.2",
        }
    )
    extension: Optional["Sbgnbase.Extension"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://sbgn.org/libsbgn/0.2",
        }
    )

    @dataclass
    class Notes:
        w3_org_1999_xhtml_element: List[object] = field(
            default_factory=list,
            metadata={
                "type": "Wildcard",
                "namespace": "http://www.w3.org/1999/xhtml",
            }
        )

    @dataclass
    class Extension:
        render_information: Optional[RenderInformation] = field(
            default=None,
            metadata={
                "name": "renderInformation",
                "type": "Element",
                "namespace": "http://www.sbml.org/sbml/level3/version1/render/version1",
            }
        )
        annotation: Optional[Annotation] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "",
            }
        )
        any_element: List[object] = field(
            default_factory=list,
            metadata={
                "type": "Wildcard",
                "namespace": "##any",
                "process_contents": "skip",
            }
        )


@dataclass
class Bbox(Sbgnbase):
    """<p xmlns=""> The bbox element describes a rectangle.

    This rectangle is defined by:
    <ul><li>
    PointAttributes corresponding to the 2D coordinates of the top left
    corner,
    </li><li>width and height attributes.</li></ul></p>
    <p xmlns="">
    The rectangle corresponds to the outer bounding box of a shape.
    The shape itself can be irregular
    (for instance in the case of some compartments).
    </p>
    <p xmlns="">
    In the case of process nodes,
    the bounding box only concerns the central glyph (square, or circle),
    the input/output ports are not included, and neither are the lines connecting
    them to the central glyph.
    </p>
    <p xmlns="">
    A bbox is required for all glyphs, and is optional for labels.
    </p>
    """
    class Meta:
        name = "bbox"
        namespace = "http://sbgn.org/libsbgn/0.2"

    x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    w: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    h: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class Point(Sbgnbase):
    """<p xmlns=""> The point element is characterized by PointAttributes, which
    describe absolute 2D cartesian coordinates.

    Namely:
    <ul><li>x (horizontal, from left to right),</li><li>y (vertical, from top to bottom).</li></ul></p>
    <p xmlns="">
    The origin is located in the top-left corner of the map.
    There is no unit:
    proportions must be preserved, but the maps can be drawn at any scale.
    In the test files examples, to obtain a drawing similar to the reference
    *.png file, values in the corresponding *.sbgn file should be read as pixels.
    </p>
    """
    class Meta:
        name = "point"
        namespace = "http://sbgn.org/libsbgn/0.2"

    x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class Port(Sbgnbase):
    """<p xmlns=""> The port element describes an anchor point which arcs can refer
    to as a source or target.

    It consists in:
    <ul><li>absolute 2D cartesian coordinates (PointAttribute),</li><li>a unique id attribute.</li></ul></p>
    <p xmlns="">
    Two port elements are required for process nodes. They represent
    the extremity of the two "arms" which protrude on both sides of the
    core of the glyph (= square or circle shape).
    Other glyphs don't need ports (but can use them if desired).
    </p>

    :ivar x:
    :ivar y:
    :ivar id: <p xmlns=""> The xsd:ID type is an alphanumeric
        identifier, starting with a letter. Port IDs often contain the
        ID of their glyph, followed by a local port number (e.g.
        glyph4.1, glyph4.2, etc.) However, this style convention is not
        mandatory, and IDs should never be interpreted as carrying any
        meaning. </p>
    """
    class Meta:
        name = "port"
        namespace = "http://sbgn.org/libsbgn/0.2"

    x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class Label(Sbgnbase):
    """<p xmlns=""> The label element describes the text accompanying a glyph.

    The text attribute is mandatory. Its position can be specified by a
    bbox (optional). Tools are free to display the text in any style
    (font, font-size, etc.) </p>

    :ivar bbox:
    :ivar text: <p xmlns=""> Multi-line labels are allowed. Line breaks
        are encoded as &amp;#xA; as specified by the XML standard. </p>
    """
    class Meta:
        name = "label"
        namespace = "http://sbgn.org/libsbgn/0.2"

    bbox: Optional[Bbox] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    text: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class Glyph(Sbgnbase):
    """<p xmlns="">
    The glyph element is:
    <ul><li>either a stand-alone, high-level SBGN glyph
    (EPN, PN, compartment, etc),</li><li>or a sub-glyph
    (state variable, unit of information, inside of a complex, ...)</li></ul></p>
    <p xmlns="">
    In the first case, it appears directly in the glyph list of the map.
    In the second case, it is a child of another glyph element.
    </p>

    :ivar label:
    :ivar state: <p xmlns=""> The state element should only be used for
        state variables. It replaces the label element used for other
        glyphs. It describes the text to be drawn inside the state
        variable. </p> <p xmlns=""> A state must have a value, a
        variable, or both. If it has both, they are rendered as a
        concatenated string with @ in between. </p>
    :ivar clone: <p xmlns=""> The clone element (which is optional)
        means the glyph carries a clone marker. It can contain an
        optional label. </p>
    :ivar callout: <p xmlns=""> The callout element is only used for
        glyphs with class annotation. It contains the coordinate of the
        point where the annotation points to, as well as a reference to
        the element that is pointed to. </p>
    :ivar entity: <p xmlns=""> The entity is only used in activity flow
        diagrams. It can only be used on a unit of information glyph on
        a biological activity glyph, where it is compulsory. It is used
        to indicate the shape of this unit of information. </p>
    :ivar bbox: <p xmlns=""> The bbox element is mandatory and unique:
        exactly one per glyph. It defines the outer bounding box of the
        glyph. The actual shape of the glyph can be irregular (for
        instance in the case of some compartments) </p> <p xmlns=""> In
        the case of process nodes, the bounding box only concerns the
        central glyph (square, or circle): the input/output ports are
        not included, and neither are the lines connecting them to the
        central glyph. </p>
    :ivar glyph: <p xmlns=""> A glyph element can contain any number of
        children glyph elements. In practice, this should only happen in
        the following cases: <ul><li>a compartment with unit of
        information children,</li><li> an EPN with states variables
        and/or unit of information children, </li><li> a complex, with
        state variables, unit of info, and/or EPN children.
        </li></ul></p>
    :ivar port:
    :ivar class_value: <p xmlns=""> The class attribute defines the
        semantic of the glyph, and influences: <ul><li>the way that
        glyph should be rendered,</li><li>the overall syntactic validity
        of the map.</li></ul></p> <p xmlns=""> The various classes
        encompass the following PD SBGN elements: <ul><li>Entity Pool
        Nodes (EPN),</li><li>Process Nodes (PN),</li><li>Logic Operator
        Nodes,</li><li>Sub-glyphs on Nodes (State Variable, Unit of
        Information),</li><li>Sub-glyphs on Arcs (Stoichiometry
        Label),</li><li>Other glyphs (Compartment, Submap, Tag,
        Terminal).</li></ul> And the following ER SBGN elements
        <ul><li>Entities (Entity, Outcome)</li><li>Other (Annotation,
        Phenotype)</li><li>Auxiliary on glyps (Existence,
        Location)</li><li>Auxiliary on arcs (Cardinality)</li><li>Delay
        operator</li><li>implicit xor</li></ul></p>
    :ivar orientation: <p xmlns=""> The orientation attribute is used to
        express how to draw asymmetric glyphs. In PD, the orientation of
        Process Nodes is either horizontal or vertical. It refers to an
        (imaginary) line connecting the two in/out sides of the PN. In
        PD, the orientation of Tags and Terminals can be left, right, up
        or down. It refers to the direction the arrow side of the glyph
        is pointing at. </p>
    :ivar id: <p xmlns=""> The xsd:ID type is an alphanumeric
        identifier, starting with a letter. It is recommended to
        generate meaningless IDs (e.g. "glyph1234") and avoid IDs with a
        meaning (e.g. "epn_ethanol") </p>
    :ivar compartment_ref: <p xmlns=""> Reference to the ID of the
        compartment that this glyph is part of. Only use this if there
        is at least one explicit compartment present in the diagram.
        Compartments are only used in PD and AF, and thus this attribute
        as well. For PD, this should be used only for EPN's. </p> <p
        xmlns=""> In case there are no compartments, entities that can
        have a location, such as EPN's, are implicit member of an
        invisible compartment that encompasses the whole map. In that
        case, this attribute must be omitted. </p>
    :ivar compartment_order: <p xmlns=""> The compartment order
        attribute can be used to define a drawing order for
        compartments. It enables tools to draw compartments in the
        correct order especially in the case of overlapping
        compartments. Compartments are only used in PD and AF, and thus
        this attribute as well. </p> <p xmlns=""> The attribute is of
        type float, the attribute value has not to be unique.
        Compartments with higher compartment order are drawn on top. The
        attribute is optional and should only be used for compartments.
        </p>
    """
    class Meta:
        name = "glyph"
        namespace = "http://sbgn.org/libsbgn/0.2"

    label: Optional[Label] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    state: Optional["Glyph.State"] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    clone: Optional["Glyph.Clone"] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    callout: Optional["Glyph.Callout"] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    entity: Optional["Glyph.Entity"] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    bbox: Optional[Bbox] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    glyph: List["Glyph"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    port: List[Port] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    class_value: Optional[GlyphClass] = field(
        default=None,
        metadata={
            "name": "class",
            "type": "Attribute",
            "required": True,
        }
    )
    orientation: GlyphOrientation = field(
        default=GlyphOrientation.HORIZONTAL,
        metadata={
            "type": "Attribute",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    compartment_ref: Optional[str] = field(
        default=None,
        metadata={
            "name": "compartmentRef",
            "type": "Attribute",
        }
    )
    compartment_order: Optional[float] = field(
        default=None,
        metadata={
            "name": "compartmentOrder",
            "type": "Attribute",
        }
    )

    @dataclass
    class Clone:
        label: Optional[Label] = field(
            default=None,
            metadata={
                "type": "Element",
            }
        )

    @dataclass
    class Callout:
        point: Optional[Point] = field(
            default=None,
            metadata={
                "type": "Element",
                "required": True,
            }
        )
        target: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
            }
        )

    @dataclass
    class Entity:
        name: Optional[EntityName] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            }
        )

    @dataclass
    class State:
        """
        :ivar value: <p xmlns=""> The value attribute represents the
            state of the variable. It can be: <ul><li> either from a
            predefined set of string (P, S, etc.) which correspond to
            specific SBO terms (cf. SBGN specs), </li><li> or any
            arbitrary string. </li></ul></p>
        :ivar variable: <p xmlns=""> The variable attribute describes
            the site where the modification described by the value
            attribute occurs. It is: <ul><li> optional when there is
            only one state variable on the parent EPN, </li><li>
            required when there is more than one state variable the
            parent EPN. </li></ul></p>
        """
        value: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
            }
        )
        variable: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
            }
        )


@dataclass
class Arc(Sbgnbase):
    """<p xmlns=""> The arc element describes an SBGN arc between two SBGN nodes.

    It contains:
    <ul><li>For PD: an optional stoichiometry marker,</li><li>For ER: an optional cardinality marker,
    zero or more ports (influence targets), and zero or more outcomes,</li><li>a mandatory source and target (glyph or port),</li><li>a geometric description of its whole path, from start to end.</li></ul><p>
    </p>
    This path can involve any number of straight lines or quadratic/cubic Bezier
    curves.
    </p>

    :ivar glyph: <p xmlns=""> In PD, an arc can contain a single
        optional sub-glyph. This glyph must be a stoichiometry marker
        (square with a numeric label) </p> <p xmlns=""> In ER, an arc
        can contain several sub-glyphs. This can be zero or one
        cardinality glyphs (e.g. cis or trans), plus zero to many
        outcome glyphs (black dot) </p>
    :ivar port: <p xmlns=""> Ports are only allowed in ER. </p>
    :ivar start: <p xmlns=""> The start element represents the starting
        point of the arc's path. It is unique and mandatory. </p>
    :ivar next: <p xmlns=""> The next element represents the next point
        in the arc's path. Between the start and the end of the path,
        there can be any number (even zero) of next elements
        (intermediate points). They are read consecutively: start, next,
        next, ..., next, end. When the path from the previous point to
        this point is not straight, this element also contains a list of
        control points (between 1 and 2) describing a Bezier curve
        (quadratic if 1 control point, cubic if 2) between the previous
        point and this point. </p>
    :ivar end: <p xmlns=""> The end element represents the ending point
        of the arc's path. It is unique and mandatory. When the path
        from the previous point to this point is not straight, this
        element also contains a list of control points (between 1 and 2)
        describing a Bezier curve (quadratic if 1 control point, cubic
        if 2) between the previous point and this point. </p>
    :ivar class_value: <p xmlns=""> The class attribute defines the
        semantic of the arc, and influences: <ul><li>the way that arc
        should be rendered,</li><li>the overall syntactic validity of
        the map.</li></ul></p> <p xmlns=""> The various classes
        encompass all possible types of SBGN arcs: <ul><li>production
        and consumption arcs,</li><li>all types of modification
        arcs,</li><li>logic arcs,</li><li>equivalence arcs.</li></ul> To
        express a reversible reaction, use production arcs on both sides
        of the Process Node. </p>
    :ivar id: <p xmlns=""> The xsd:ID type is an alphanumeric
        identifier, starting with a letter. </p>
    :ivar source: <p xmlns=""> The source attribute can refer:
        <ul><li>either to the id of a glyph,</li><li>or to the id of a
        port on a glyph.</li></ul></p>
    :ivar target: <p xmlns=""> The target attribute can refer:
        <ul><li>either to the id of a glyph,</li><li>or to the id of a
        port on a glyph.</li></ul></p>
    """
    class Meta:
        name = "arc"
        namespace = "http://sbgn.org/libsbgn/0.2"

    glyph: List[Glyph] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    port: List[Port] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    start: Optional["Arc.Start"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    next: List["Arc.Next"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    end: Optional["Arc.End"] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
    class_value: Optional[ArcClass] = field(
        default=None,
        metadata={
            "name": "class",
            "type": "Attribute",
            "required": True,
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    source: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    target: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

    @dataclass
    class Start:
        x: Optional[float] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            }
        )
        y: Optional[float] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            }
        )

    @dataclass
    class Next:
        point: List[Point] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "max_occurs": 2,
            }
        )
        x: Optional[float] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            }
        )
        y: Optional[float] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            }
        )

    @dataclass
    class End:
        point: List[Point] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "max_occurs": 2,
            }
        )
        x: Optional[float] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            }
        )
        y: Optional[float] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            }
        )


@dataclass
class Arcgroup(Sbgnbase):
    """<p xmlns=""> The arc group describes a set of arcs and glyphs that together
    have a relation.

    For example
    <ul><li>For ER: interaction arcs around an interaction glyph,</li><li>...</li></ul>
    Note that, in spite of the name, an arcgroup contains both arcs and glyphs.
    </p>

    :ivar glyph: <p xmlns=""> An arcgroup can contain glyphs. For
        example, in an interaction arcgroup, there must be one
        interaction glyph. </p>
    :ivar arc: <p xmlns=""> An arcgroup can have multiple arcs. They are
        all assumed to form a single hyperarc-like structure. </p>
    :ivar class_value: <p xmlns=""> The class attribute defines the
        semantic of the arcgroup. </p>
    """
    class Meta:
        name = "arcgroup"
        namespace = "http://sbgn.org/libsbgn/0.2"

    glyph: List[Glyph] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    arc: List[Arc] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    class_value: Optional[ArcgroupClass] = field(
        default=None,
        metadata={
            "name": "class",
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class Map(Sbgnbase):
    """<p xmlns=""> The map element describes a single SBGN PD map.

    It contains a list of glyph elements and a list of arc elements.
    These lists can be of any size (possibly empty). </p>

    :ivar bbox: <p xmlns=""> The bbox element on a map is not mandatory,
        it allows the application to define a canvas, and at the same
        time define a whitespace margin around the glyphs. </p> <p
        xmlns=""> If a bbox is defined on a map, all glyphs and arcs
        must be inside this bbox, otherwise they could be clipped off by
        applications. </p>
    :ivar glyph:
    :ivar arc:
    :ivar arcgroup:
    :ivar language: <p xmlns=""> Language of the map: one of three
        sublanguages defined by SBGN. Different languages have different
        restrictions on the usage of sub-elements (that are not encoded
        in this schema but must be validated with an external validator)
        </p>
    """
    class Meta:
        name = "map"
        namespace = "http://sbgn.org/libsbgn/0.2"

    bbox: Optional[Bbox] = field(
        default=None,
        metadata={
            "type": "Element",
        }
    )
    glyph: List[Glyph] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    arc: List[Arc] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    arcgroup: List[Arcgroup] = field(
        default_factory=list,
        metadata={
            "type": "Element",
        }
    )
    language: Optional[MapLanguage] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class Sbgn(Sbgnbase):
    """<p xmlns=""> The sbgn element is the root of any SBGNML document.

    Currently each document must contain exactly one map element. </p>
    """
    class Meta:
        name = "sbgn"
        namespace = "http://sbgn.org/libsbgn/0.2"

    map: Optional[Map] = field(
        default=None,
        metadata={
            "type": "Element",
            "required": True,
        }
    )
