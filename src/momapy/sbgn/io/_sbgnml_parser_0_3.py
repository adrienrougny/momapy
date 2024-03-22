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


class MapVersion(Enum):
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_PD_LEVEL_1_VERSION_2_0 = "http://identifiers.org/combine.specifications/sbgn.pd.level-1.version-2.0"
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_PD_LEVEL_1_VERSION_1_3 = "http://identifiers.org/combine.specifications/sbgn.pd.level-1.version-1.3"
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_PD_LEVEL_1_VERSION_1_2 = "http://identifiers.org/combine.specifications/sbgn.pd.level-1.version-1.2"
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_PD_LEVEL_1_VERSION_1_1 = "http://identifiers.org/combine.specifications/sbgn.pd.level-1.version-1.1"
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_PD_LEVEL_1_VERSION_1_0 = "http://identifiers.org/combine.specifications/sbgn.pd.level-1.version-1.0"
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_PD_LEVEL_1_VERSION_1 = "http://identifiers.org/combine.specifications/sbgn.pd.level-1.version-1"
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_ER_LEVEL_1_VERSION_2 = "http://identifiers.org/combine.specifications/sbgn.er.level-1.version-2"
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_ER_LEVEL_1_VERSION_1_2 = "http://identifiers.org/combine.specifications/sbgn.er.level-1.version-1.2"
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_ER_LEVEL_1_VERSION_1_1 = "http://identifiers.org/combine.specifications/sbgn.er.level-1.version-1.1"
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_ER_LEVEL_1_VERSION_1_0 = "http://identifiers.org/combine.specifications/sbgn.er.level-1.version-1.0"
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_ER_LEVEL_1_VERSION_1 = "http://identifiers.org/combine.specifications/sbgn.er.level-1.version-1"
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_AF_LEVEL_1_VERSION_1_2 = "http://identifiers.org/combine.specifications/sbgn.af.level-1.version-1.2"
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_AF_LEVEL_1_VERSION_1_0 = "http://identifiers.org/combine.specifications/sbgn.af.level-1.version-1.0"
    HTTP_IDENTIFIERS_ORG_COMBINE_SPECIFICATIONS_SBGN_AF_LEVEL_1_VERSION_1 = "http://identifiers.org/combine.specifications/sbgn.af.level-1.version-1"


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

    about: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "namespace": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
    )
    encodes: Optional[Encodes] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    has_part: Optional[HasPart] = field(
        default=None,
        metadata={
            "name": "hasPart",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    has_property: Optional[HasProperty] = field(
        default=None,
        metadata={
            "name": "hasProperty",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    has_version: Optional[HasVersion] = field(
        default=None,
        metadata={
            "name": "hasVersion",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_value: Optional[Is1] = field(
        default=None,
        metadata={
            "name": "is",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_described_by: Optional[IsDescribedBy1] = field(
        default=None,
        metadata={
            "name": "isDescribedBy",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_encoded_by: Optional[IsEncodedBy] = field(
        default=None,
        metadata={
            "name": "isEncodedBy",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_homolog_to: Optional[IsHomologTo] = field(
        default=None,
        metadata={
            "name": "isHomologTo",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_part_of: Optional[IsPartOf] = field(
        default=None,
        metadata={
            "name": "isPartOf",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_property_of: Optional[IsPropertyOf] = field(
        default=None,
        metadata={
            "name": "isPropertyOf",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    is_version_of: Optional[IsVersionOf] = field(
        default=None,
        metadata={
            "name": "isVersionOf",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    occurs_in: Optional[OccursIn] = field(
        default=None,
        metadata={
            "name": "occursIn",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    has_taxon: Optional[HasTaxon] = field(
        default=None,
        metadata={
            "name": "hasTaxon",
            "type": "Element",
            "namespace": "http://biomodels.net/biology-qualifiers/",
        }
    )
    has_instance: Optional[HasInstance] = field(
        default=None,
        metadata={
            "name": "hasInstance",
            "type": "Element",
            "namespace": "http://biomodels.net/model-qualifiers/",
        }
    )
    biomodels_net_model_qualifiers_is: Optional[Is2] = field(
        default=None,
        metadata={
            "name": "is",
            "type": "Element",
            "namespace": "http://biomodels.net/model-qualifiers/",
        }
    )
    is_derived_from: Optional[IsDerivedFrom] = field(
        default=None,
        metadata={
            "name": "isDerivedFrom",
            "type": "Element",
            "namespace": "http://biomodels.net/model-qualifiers/",
        }
    )
    biomodels_net_model_qualifiers_is_described_by: Optional[IsDescribedBy2] = field(
        default=None,
        metadata={
            "name": "isDescribedBy",
            "type": "Element",
            "namespace": "http://biomodels.net/model-qualifiers/",
        }
    )
    is_instance_of: Optional[IsInstanceOf] = field(
        default=None,
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


@dataclass
class Rdf(Rdftype):
    class Meta:
        name = "RDF"
        namespace = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


@dataclass
class AnnotationType:
    class Meta:
        name = "annotationType"
        target_namespace = "http://sbgn.org/libsbgn/0.3"

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
        namespace = "http://sbgn.org/libsbgn/0.3"


@dataclass
class Sbgnbase:
    """The SBGNBase type is the base type of all main components in SBGN.

    It supports attaching metadata, notes and annotations to components.
    """
    class Meta:
        name = "SBGNBase"
        target_namespace = "http://sbgn.org/libsbgn/0.3"

    notes: Optional["Sbgnbase.Notes"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://sbgn.org/libsbgn/0.3",
        }
    )
    extension: Optional["Sbgnbase.Extension"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://sbgn.org/libsbgn/0.3",
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
                "namespace": "http://sbgn.org/libsbgn/0.3",
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
    """<ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    The bbox element describes a rectangle. This rectangle is defined by:
    <ns1:ul><ns1:li>
    PointAttributes corresponding to the 2D coordinates of the top left
    corner,
    </ns1:li><ns1:li>width and height attributes.</ns1:li></ns1:ul></ns1:p>
    <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    The rectangle corresponds to the outer bounding box of a shape.
    The shape itself can be irregular
    (for instance in the case of some compartments).
    </ns1:p>
    <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    In the case of process nodes,
    the bounding box only concerns the central glyph (square, or circle),
    the input/output ports are not included, and neither are the lines connecting
    them to the central glyph.
    </ns1:p>
    <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    A bbox is required for all glyphs, and is optional for labels.
    </ns1:p>"""
    class Meta:
        name = "bbox"
        namespace = "http://sbgn.org/libsbgn/0.3"

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
    """<ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    The point element is characterized by PointAttributes,
    which describe absolute 2D cartesian coordinates. Namely:
    <ns1:ul><ns1:li>x (horizontal, from left to right),</ns1:li><ns1:li>y (vertical, from top to bottom).</ns1:li></ns1:ul></ns1:p>
    <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    The origin is located in the top-left corner of the map.
    There is no unit:
    proportions must be preserved, but the maps can be drawn at any scale.
    In the test files examples, to obtain a drawing similar to the reference
    *.png file, values in the corresponding *.sbgn file should be read as pixels.
    </ns1:p>"""
    class Meta:
        name = "point"
        namespace = "http://sbgn.org/libsbgn/0.3"

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
    """<ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    The port element describes an anchor point which arcs can refer to
    as a source or target. It consists in:
    <ns1:ul><ns1:li>absolute 2D cartesian coordinates (PointAttribute),</ns1:li><ns1:li>a unique id attribute.</ns1:li></ns1:ul></ns1:p>
    <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    Two port elements are required for process nodes. They represent
    the extremity of the two "arms" which protrude on both sides of the
    core of the glyph (= square or circle shape).
    Other glyphs don't need ports (but can use them if desired).
    </ns1:p>

    :ivar x:
    :ivar y:
    :ivar id: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The xsd:ID
        type is an alphanumeric identifier, starting with a letter. Port
        IDs often contain the ID of their glyph, followed by a local
        port number (e.g. glyph4.1, glyph4.2, etc.) However, this style
        convention is not mandatory, and IDs should never be interpreted
        as carrying any meaning. </ns1:p>
    """
    class Meta:
        name = "port"
        namespace = "http://sbgn.org/libsbgn/0.3"

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
    """<ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    The label element describes the text accompanying a glyph.
    The text attribute is mandatory.
    Its position can be specified by a bbox (optional).
    Tools are free to display the text in any style (font, font-size, etc.)
    </ns1:p>

    :ivar bbox:
    :ivar text: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> Multi-
        line labels are allowed. Line breaks are encoded as &amp;#xA; as
        specified by the XML standard. </ns1:p>
    """
    class Meta:
        name = "label"
        namespace = "http://sbgn.org/libsbgn/0.3"

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
    """<ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    The glyph element is:
    <ns1:ul><ns1:li>either a stand-alone, high-level SBGN glyph
    (EPN, PN, compartment, etc),</ns1:li><ns1:li>or a sub-glyph
    (state variable, unit of information, inside of a complex, ...)</ns1:li></ns1:ul></ns1:p>
    <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    In the first case, it appears directly in the glyph list of the map.
    In the second case, it is a child of another glyph element.
    </ns1:p>

    :ivar label:
    :ivar state: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The
        state element should only be used for state variables. It
        replaces the label element used for other glyphs. It describes
        the text to be drawn inside the state variable. </ns1:p> <ns1:p
        xmlns:ns1="http://sbgn.org/libsbgn/0.3"> A state must have a
        value, a variable, or both. If it has both, they are rendered as
        a concatenated string with @ in between. </ns1:p>
    :ivar clone: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The
        clone element (which is optional) means the glyph carries a
        clone marker. It can contain an optional label. </ns1:p>
    :ivar callout: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The
        callout element is only used for glyphs with class annotation.
        It contains the coordinate of the point where the annotation
        points to, as well as a reference to the element that is pointed
        to. </ns1:p>
    :ivar entity: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The
        entity is only used in activity flow diagrams. It can only be
        used on a unit of information glyph on a biological activity
        glyph, where it is compulsory. It is used to indicate the shape
        of this unit of information. </ns1:p>
    :ivar bbox: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The bbox
        element is mandatory and unique: exactly one per glyph. It
        defines the outer bounding box of the glyph. The actual shape of
        the glyph can be irregular (for instance in the case of some
        compartments) </ns1:p> <ns1:p
        xmlns:ns1="http://sbgn.org/libsbgn/0.3"> In the case of process
        nodes, the bounding box only concerns the central glyph (square,
        or circle): the input/output ports are not included, and neither
        are the lines connecting them to the central glyph. </ns1:p>
    :ivar glyph: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> A glyph
        element can contain any number of children glyph elements. In
        practice, this should only happen in the following cases:
        <ns1:ul><ns1:li>a compartment with unit of information
        children,</ns1:li><ns1:li> an EPN with states variables and/or
        unit of information children, </ns1:li><ns1:li> a complex, with
        state variables, unit of info, and/or EPN children.
        </ns1:li></ns1:ul></ns1:p>
    :ivar port:
    :ivar class_value: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
        The class attribute defines the semantic of the glyph, and
        influences: <ns1:ul><ns1:li>the way that glyph should be
        rendered,</ns1:li><ns1:li>the overall syntactic validity of the
        map.</ns1:li></ns1:ul></ns1:p> <ns1:p
        xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The various classes
        encompass the following PD SBGN elements: <ns1:ul><ns1:li>Entity
        Pool Nodes (EPN),</ns1:li><ns1:li>Process Nodes
        (PN),</ns1:li><ns1:li>Logic Operator Nodes,</ns1:li><ns1:li>Sub-
        glyphs on Nodes (State Variable, Unit of
        Information),</ns1:li><ns1:li>Sub-glyphs on Arcs (Stoichiometry
        Label),</ns1:li><ns1:li>Other glyphs (Compartment, Submap, Tag,
        Terminal).</ns1:li></ns1:ul> And the following ER SBGN elements
        <ns1:ul><ns1:li>Entities (Entity, Outcome)</ns1:li><ns1:li>Other
        (Annotation, Phenotype)</ns1:li><ns1:li>Auxiliary on glyps
        (Existence, Location)</ns1:li><ns1:li>Auxiliary on arcs
        (Cardinality)</ns1:li><ns1:li>Delay
        operator</ns1:li><ns1:li>implicit xor</ns1:li></ns1:ul></ns1:p>
    :ivar orientation: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
        The orientation attribute is used to express how to draw
        asymmetric glyphs. In PD, the orientation of Process Nodes is
        either horizontal or vertical. It refers to an (imaginary) line
        connecting the two in/out sides of the PN. In PD, the
        orientation of Tags and Terminals can be left, right, up or
        down. It refers to the direction the arrow side of the glyph is
        pointing at. </ns1:p>
    :ivar id: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The xsd:ID
        type is an alphanumeric identifier, starting with a letter. It
        is recommended to generate meaningless IDs (e.g. "glyph1234")
        and avoid IDs with a meaning (e.g. "epn_ethanol") </ns1:p>
    :ivar compartment_ref: <ns1:p
        xmlns:ns1="http://sbgn.org/libsbgn/0.3"> Reference to the ID of
        the compartment that this glyph is part of. Only use this if
        there is at least one explicit compartment present in the
        diagram. Compartments are only used in PD and AF, and thus this
        attribute as well. For PD, this should be used only for EPN's.
        </ns1:p> <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> In case
        there are no compartments, entities that can have a location,
        such as EPN's, are implicit member of an invisible compartment
        that encompasses the whole map. In that case, this attribute
        must be omitted. </ns1:p>
    :ivar compartment_order: <ns1:p
        xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The compartment order
        attribute can be used to define a drawing order for
        compartments. It enables tools to draw compartments in the
        correct order especially in the case of overlapping
        compartments. Compartments are only used in PD and AF, and thus
        this attribute as well. </ns1:p> <ns1:p
        xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The attribute is of
        type float, the attribute value has not to be unique.
        Compartments with higher compartment order are drawn on top. The
        attribute is optional and should only be used for compartments.
        </ns1:p>
    """
    class Meta:
        name = "glyph"
        namespace = "http://sbgn.org/libsbgn/0.3"

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
        :ivar value: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The
            value attribute represents the state of the variable. It can
            be: <ns1:ul><ns1:li> either from a predefined set of string
            (P, S, etc.) which correspond to specific SBO terms (cf.
            SBGN specs), </ns1:li><ns1:li> or any arbitrary string.
            </ns1:li></ns1:ul></ns1:p>
        :ivar variable: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
            The variable attribute describes the site where the
            modification described by the value attribute occurs. It is:
            <ns1:ul><ns1:li> optional when there is only one state
            variable on the parent EPN, </ns1:li><ns1:li> required when
            there is more than one state variable the parent EPN.
            </ns1:li></ns1:ul></ns1:p>
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
    """<ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    The arc element describes an SBGN arc between two SBGN nodes. It contains:
    <ns1:ul><ns1:li>For PD: an optional stoichiometry marker,</ns1:li><ns1:li>For ER: an optional cardinality marker,
    zero or more ports (influence targets), and zero or more outcomes,</ns1:li><ns1:li>a mandatory source and target (glyph or port),</ns1:li><ns1:li>a geometric description of its whole path, from start to end.</ns1:li></ns1:ul><ns1:p>
    </ns1:p>
    This path can involve any number of straight lines or quadratic/cubic Bezier
    curves.
    </ns1:p>

    :ivar glyph: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> In PD,
        an arc can contain a single optional sub-glyph. This glyph must
        be a stoichiometry marker (square with a numeric label) </ns1:p>
        <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> In ER, an arc
        can contain several sub-glyphs. This can be zero or one
        cardinality glyphs (e.g. cis or trans), plus zero to many
        outcome glyphs (black dot) </ns1:p>
    :ivar port: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> Ports
        are only allowed in ER. </ns1:p>
    :ivar start: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The
        start element represents the starting point of the arc's path.
        It is unique and mandatory. </ns1:p>
    :ivar next: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The next
        element represents the next point in the arc's path. Between the
        start and the end of the path, there can be any number (even
        zero) of next elements (intermediate points). They are read
        consecutively: start, next, next, ..., next, end. When the path
        from the previous point to this point is not straight, this
        element also contains a list of control points (between 1 and 2)
        describing a Bezier curve (quadratic if 1 control point, cubic
        if 2) between the previous point and this point. </ns1:p>
    :ivar end: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The end
        element represents the ending point of the arc's path. It is
        unique and mandatory. When the path from the previous point to
        this point is not straight, this element also contains a list of
        control points (between 1 and 2) describing a Bezier curve
        (quadratic if 1 control point, cubic if 2) between the previous
        point and this point. </ns1:p>
    :ivar class_value: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
        The class attribute defines the semantic of the arc, and
        influences: <ns1:ul><ns1:li>the way that arc should be
        rendered,</ns1:li><ns1:li>the overall syntactic validity of the
        map.</ns1:li></ns1:ul></ns1:p> <ns1:p
        xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The various classes
        encompass all possible types of SBGN arcs:
        <ns1:ul><ns1:li>production and consumption
        arcs,</ns1:li><ns1:li>all types of modification
        arcs,</ns1:li><ns1:li>logic arcs,</ns1:li><ns1:li>equivalence
        arcs.</ns1:li></ns1:ul> To express a reversible reaction, use
        production arcs on both sides of the Process Node. </ns1:p>
    :ivar id: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The xsd:ID
        type is an alphanumeric identifier, starting with a letter.
        </ns1:p>
    :ivar source: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The
        source attribute can refer: <ns1:ul><ns1:li>either to the id of
        a glyph,</ns1:li><ns1:li>or to the id of a port on a
        glyph.</ns1:li></ns1:ul></ns1:p>
    :ivar target: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The
        target attribute can refer: <ns1:ul><ns1:li>either to the id of
        a glyph,</ns1:li><ns1:li>or to the id of a port on a
        glyph.</ns1:li></ns1:ul></ns1:p>
    """
    class Meta:
        name = "arc"
        namespace = "http://sbgn.org/libsbgn/0.3"

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
    """<ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    The arc group describes a set of arcs and glyphs that together have a relation.
    For example
    <ns1:ul><ns1:li>For ER: interaction arcs around an interaction glyph,</ns1:li><ns1:li>...</ns1:li></ns1:ul>
    Note that, in spite of the name, an arcgroup contains both arcs and glyphs.
    </ns1:p>

    :ivar glyph: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> An
        arcgroup can contain glyphs. For example, in an interaction
        arcgroup, there must be one interaction glyph. </ns1:p>
    :ivar arc: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> An
        arcgroup can have multiple arcs. They are all assumed to form a
        single hyperarc-like structure. </ns1:p>
    :ivar class_value: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
        The class attribute defines the semantic of the arcgroup.
        </ns1:p>
    """
    class Meta:
        name = "arcgroup"
        namespace = "http://sbgn.org/libsbgn/0.3"

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
    """<ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    The map element describes a single SBGN PD map.
    It contains a list of glyph elements and a list of arc elements.
    These lists can be of any size (possibly empty).
    </ns1:p>

    :ivar bbox: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The bbox
        element on a map is not mandatory, it allows the application to
        define a canvas, and at the same time define a whitespace margin
        around the glyphs. </ns1:p> <ns1:p
        xmlns:ns1="http://sbgn.org/libsbgn/0.3"> If a bbox is defined on
        a map, all glyphs and arcs must be inside this bbox, otherwise
        they could be clipped off by applications. </ns1:p>
    :ivar glyph:
    :ivar arc:
    :ivar arcgroup:
    :ivar language: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
        Language of the map: one of three sublanguages defined by SBGN.
        Different languages have different restrictions on the usage of
        sub-elements (that are not encoded in this schema but must be
        validated with an external validator) This attribute is
        deprecated in favor of the version attribute. </ns1:p>
    :ivar version: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
        Version of the map: one of three sublanguages defined by SBGN.
        Different languages have different restrictions on the usage of
        sub-elements (that are not encoded in this schema but must be
        validated with an external validator) </ns1:p>
    :ivar id: <ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3"> The xsd:ID
        type is an alphanumeric identifier, starting with a letter. Port
        IDs often contain the ID of their glyph, followed by a local
        port number (e.g. glyph4.1, glyph4.2, etc.) However, this style
        convention is not mandatory, and IDs should never be interpreted
        as carrying any meaning. </ns1:p>
    """
    class Meta:
        name = "map"
        namespace = "http://sbgn.org/libsbgn/0.3"

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
        }
    )
    version: Optional[MapVersion] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class Sbgn(Sbgnbase):
    """<ns1:p xmlns:ns1="http://sbgn.org/libsbgn/0.3">
    The sbgn element is the root of any SBGNML document.
    Each document can contain multiple map elements.
    </ns1:p>"""
    class Meta:
        name = "sbgn"
        namespace = "http://sbgn.org/libsbgn/0.3"

    map: List[Map] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        }
    )
