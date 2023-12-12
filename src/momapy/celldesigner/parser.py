from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class AntisenseRnaType(Enum):
    ANTISENSE_RNA = "ANTISENSE_RNA"


@dataclass
class KeyInfo:
    class Meta:
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    direct: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


class RnaType(Enum):
    RNA = "RNA"


@dataclass
class StructuralStates:
    class Meta:
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    structural_state: Optional[str] = field(
        default=None,
        metadata={
            "name": "structuralState",
            "type": "Attribute",
        }
    )


@dataclass
class TagBounds:
    class Meta:
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    x: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    y: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    w: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    h: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class TagEdgeLine:
    class Meta:
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    width: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


class ActivityValue(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass
class Alias:
    """
    Alias referer inside (modifier) species reference.
    """
    class Meta:
        name = "alias"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: str = field(
        default="",
        metadata={
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class AntisensernaReference:
    """
    Reference to an antisense rna.
    """
    class Meta:
        name = "antisensernaReference"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: str = field(
        default="",
        metadata={
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class BindingRegion:
    class Meta:
        name = "bindingRegion"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    angle: Optional[Decimal] = field(
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
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    size: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class BindingSiteInBlockDiagram:
    """
    Binding site on the left side of a block(protein).
    """
    class Meta:
        name = "bindingSiteInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetY",
            "type": "Attribute",
            "required": True,
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    name_offset_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "nameOffsetX",
            "type": "Attribute",
            "required": True,
        }
    )
    name_offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "nameOffsetY",
            "type": "Attribute",
            "required": True,
        }
    )
    protein: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class Block:
    """
    Block(protein) on canvas.
    """
    class Meta:
        name = "block"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    width: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    height: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    x: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    y: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    name_offset_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "nameOffsetX",
            "type": "Attribute",
            "required": True,
        }
    )
    name_offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "nameOffsetY",
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class Bounds:
    """
    Bound of an object on canvas.
    """
    class Meta:
        name = "bounds"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    h: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": Decimal("0.0"),
        }
    )
    w: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": Decimal("0.0"),
        }
    )
    x: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    y: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class BoxSize:
    """Box size.

    Width and height.
    """
    class Meta:
        name = "boxSize"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    height: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": Decimal("0.0"),
        }
    )
    width: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": Decimal("0.0"),
        }
    )


@dataclass
class Canvas:
    """
    Canvas size of block diagrams.
    """
    class Meta:
        name = "canvas"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    height: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    width: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )


@dataclass
class Catalyzed:
    """
    Catalyzed reaction.
    """
    class Meta:
        name = "catalyzed"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    reaction: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


class ClassValue(Enum):
    PROTEIN = "PROTEIN"
    GENE = "GENE"
    RNA = "RNA"
    ANTISENSE_RNA = "ANTISENSE_RNA"
    PHENOTYPE = "PHENOTYPE"
    ION = "ION"
    SIMPLE_MOLECULE = "SIMPLE_MOLECULE"
    DRUG = "DRUG"
    UNKNOWN = "UNKNOWN"
    COMPLEX = "COMPLEX"
    SQUARE = "SQUARE"
    OVAL = "OVAL"
    SQUARE_CLOSEUP_NORTHWEST = "SQUARE_CLOSEUP_NORTHWEST"
    SQUARE_CLOSEUP_NORTHEAST = "SQUARE_CLOSEUP_NORTHEAST"
    SQUARE_CLOSEUP_SOUTHWEST = "SQUARE_CLOSEUP_SOUTHWEST"
    SQUARE_CLOSEUP_SOUTHEAST = "SQUARE_CLOSEUP_SOUTHEAST"
    SQUARE_CLOSEUP_NORTH = "SQUARE_CLOSEUP_NORTH"
    SQUARE_CLOSEUP_EAST = "SQUARE_CLOSEUP_EAST"
    SQUARE_CLOSEUP_WEST = "SQUARE_CLOSEUP_WEST"
    SQUARE_CLOSEUP_SOUTH = "SQUARE_CLOSEUP_SOUTH"
    DEGRADED = "DEGRADED"


@dataclass
class CompartmentAnnotationType:
    """
    Annotation for compartment.
    """
    class Meta:
        name = "compartmentAnnotationType"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    extension: Optional["CompartmentAnnotationType.Extension"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )

    @dataclass
    class Extension:
        name: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )


@dataclass
class ComplexSpecies:
    """Species id of the parent complex.

    For the species forming a complex.
    """
    class Meta:
        name = "complexSpecies"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: str = field(
        default="",
        metadata={
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


class ConnectSchemeConnectPolicy(Enum):
    DIRECT = "direct"
    SQUARE = "square"


@dataclass
class DegradedShapeInBlockDiagram:
    """
    Degradation symbol.
    """
    class Meta:
        name = "degradedShapeInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    width: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    height: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    offset_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetX",
            "type": "Attribute",
            "required": True,
        }
    )
    offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetY",
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class DoubleLine:
    """
    Double line type to draw object.
    """
    class Meta:
        name = "doubleLine"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    inner_width: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "innerWidth",
            "type": "Attribute",
            "required": True,
            "min_inclusive": Decimal("0.0"),
        }
    )
    outer_width: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "outerWidth",
            "type": "Attribute",
            "required": True,
            "min_inclusive": Decimal("0.0"),
        }
    )
    thickness: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": Decimal("0.0"),
        }
    )


@dataclass
class EditPoints:
    """
    Edit points.
    """
    class Meta:
        name = "editPoints"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: List[str] = field(
        default_factory=list,
        metadata={
            "pattern": r"(\+|-)?[0-9]+(\.[0-9]*)?((e|E)(\+|-)?[0-9]+)?,(\+|-)?[0-9]+(\.[0-9]*)?((e|E)(\+|-)?[0-9]+)?",
            "tokens": True,
        }
    )
    num0: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )
    num1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )
    num2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )
    omitted_shape_index: Optional[int] = field(
        default=None,
        metadata={
            "name": "omittedShapeIndex",
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )
    t_shape_index: Optional[int] = field(
        default=None,
        metadata={
            "name": "tShapeIndex",
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )


class EffectInBlockDiagramType(Enum):
    CATALYSIS = "CATALYSIS"
    INHIBITION = "INHIBITION"


@dataclass
class EffectTargetInBlockDiagram:
    """
    Target protein of an effect.
    """
    class Meta:
        name = "effectTargetInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    protein: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class EndPointInBlockDiagram:
    """
    End point (residue, binding site, effect site, operator, link, degrade) of
    the link.
    """
    class Meta:
        name = "endPointInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    offset_x: List[Decimal] = field(
        default_factory=list,
        metadata={
            "name": "offsetX",
            "type": "Attribute",
            "required": True,
            "tokens": True,
        }
    )
    offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetY",
            "type": "Attribute",
            "required": True,
        }
    )
    residue: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )
    binding_site: Optional[int] = field(
        default=None,
        metadata={
            "name": "bindingSite",
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )
    effect_site: Optional[int] = field(
        default=None,
        metadata={
            "name": "effectSite",
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )
    operator: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )
    link: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )
    degrade: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )


class ExternalConnectionInBlockDiagramType(Enum):
    ACTIVATION = "activation"
    ACTIVATION_MAYBE = "activationMaybe"
    INHIBITION = "inhibition"


@dataclass
class GeneReference:
    """
    Reference to a gene.
    """
    class Meta:
        name = "geneReference"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: str = field(
        default="",
        metadata={
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


class GeneType(Enum):
    GENE = "GENE"


@dataclass
class Group:
    """
    Group of speciesAliases.
    """
    class Meta:
        name = "group"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    members: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*(,(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*)+",
        }
    )


@dataclass
class Halo:
    """
    Halo around a block(protein).
    """
    class Meta:
        name = "halo"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    width: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    height: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    x: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    y: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )


@dataclass
class Homodimer:
    """
    Valence value of homogeneous multimer.
    """
    class Meta:
        name = "homodimer"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: Optional[int] = field(
        default=None
    )


@dataclass
class Hypothetical:
    """
    Designator to tell that the species is hypothetical.
    """
    class Meta:
        name = "hypothetical"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: Optional[bool] = field(
        default=None
    )


@dataclass
class Info:
    class Meta:
        name = "info"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    state: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    prefix: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    label: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    angle: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class InnerPosition:
    """
    Innerposition relative to a surrounding object.
    """
    class Meta:
        name = "innerPosition"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    x: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    y: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class InternalLinkInBlockDiagramType(Enum):
    ACTIVATION = "activation"
    ABSOLUTE_ACTIVATION = "absoluteActivation"
    INHIBITION = "inhibition"
    ABSOLUTE_INHIBITION = "absoluteInhibition"


class InternalOperatorInBlockDiagramSub(Enum):
    GE = "ge"
    GT = "gt"
    LE = "le"
    LT = "lt"


class InternalOperatorInBlockDiagramType(Enum):
    AND = "and"
    OR = "or"
    ADD = "add"
    MULTIPLY = "multiply"
    THRESHOLD = "threshold"
    AUTO_ACTIVATE = "autoActivate"
    ASSIGN = "assign"


@dataclass
class InternalOperatorValueInBlockDiagram:
    """
    Assigned value to the operator.
    """
    class Meta:
        name = "internalOperatorValueInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    offset_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetX",
            "type": "Attribute",
            "required": True,
        }
    )
    offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetY",
            "type": "Attribute",
            "required": True,
        }
    )


class LayerCompartmentAliasType(Enum):
    OVAL = "Oval"
    SQUARE = "Square"


@dataclass
class LayerLineBounds:
    class Meta:
        name = "layerLineBounds"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    sx: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    sy: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    ex: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    ey: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class Line:
    """
    Line color and width.
    """
    class Meta:
        name = "line"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9a-fA-F]{8}",
        }
    )
    width: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": Decimal("0.0"),
        }
    )


class LineDirectionValue(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    UNKNOWN = "unknown"


class LineType2Type(Enum):
    CURVE = "Curve"
    STRAIGHT = "Straight"


class LinkAnchorPosition(Enum):
    N = "N"
    NNE = "NNE"
    NE = "NE"
    ENE = "ENE"
    E = "E"
    ESE = "ESE"
    SE = "SE"
    SSE = "SSE"
    S = "S"
    SSW = "SSW"
    SW = "SW"
    WSW = "WSW"
    W = "W"
    WNW = "WNW"
    NW = "NW"
    NNW = "NNW"


@dataclass
class ModelDisplay:
    """
    Model size, width and height.
    """
    class Meta:
        name = "modelDisplay"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    size_x: Optional[int] = field(
        default=None,
        metadata={
            "name": "sizeX",
            "type": "Attribute",
            "required": True,
            "min_exclusive": 0,
        }
    )
    size_y: Optional[int] = field(
        default=None,
        metadata={
            "name": "sizeY",
            "type": "Attribute",
            "required": True,
            "min_exclusive": 0,
        }
    )


@dataclass
class ModelVersion:
    """
    Model version declaration.
    """
    class Meta:
        name = "modelVersion"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: Decimal = field(
        init=False,
        default=Decimal("4.0"),
        metadata={
            "min_inclusive": Decimal("0.0"),
        }
    )


@dataclass
class ModificationResidue:
    """
    For modification residue of proteins.
    """
    class Meta:
        name = "modificationResidue"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    angle: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("0.0"),
            "max_inclusive": Decimal("6.283185307179586476925286766559"),
        }
    )
    side: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


class ModificationModification(Enum):
    CATALYSIS = "CATALYSIS"
    UNKNOWN_CATALYSIS = "UNKNOWN_CATALYSIS"
    INHIBITION = "INHIBITION"
    UNKNOWN_INHIBITION = "UNKNOWN_INHIBITION"
    HETERODIMER_ASSOCIATION = "HETERODIMER_ASSOCIATION"
    TRANSCRIPTIONAL_ACTIVATION = "TRANSCRIPTIONAL_ACTIVATION"
    TRANSCRIPTIONAL_INHIBITION = "TRANSCRIPTIONAL_INHIBITION"
    TRANSLATIONAL_ACTIVATION = "TRANSLATIONAL_ACTIVATION"
    TRANSLATIONAL_INHIBITION = "TRANSLATIONAL_INHIBITION"
    PHYSICAL_STIMULATION = "PHYSICAL_STIMULATION"
    MODULATION = "MODULATION"
    TRIGGER = "TRIGGER"


class ModificationState(Enum):
    PHOSPHORYLATED = "phosphorylated"
    ACETYLATED = "acetylated"
    UBIQUITINATED = "ubiquitinated"
    METHYLATED = "methylated"
    HYDROXYLATED = "hydroxylated"
    DON_T_CARE = "don't care"
    UNKNOWN = "unknown"
    GLYCOSYLATED = "glycosylated"
    MYRISTOYLATED = "myristoylated"
    PALMYTOYLATED = "palmytoylated"
    PRENYLATED = "prenylated"
    PROTONATED = "protonated"
    SULFATED = "sulfated"


class ModificationType(Enum):
    CATALYSIS = "CATALYSIS"
    UNKNOWN_CATALYSIS = "UNKNOWN_CATALYSIS"
    INHIBITION = "INHIBITION"
    UNKNOWN_INHIBITION = "UNKNOWN_INHIBITION"
    HETERODIMER_ASSOCIATION = "HETERODIMER_ASSOCIATION"
    TRANSCRIPTIONAL_ACTIVATION = "TRANSCRIPTIONAL_ACTIVATION"
    TRANSCRIPTIONAL_INHIBITION = "TRANSCRIPTIONAL_INHIBITION"
    TRANSLATIONAL_ACTIVATION = "TRANSLATIONAL_ACTIVATION"
    TRANSLATIONAL_INHIBITION = "TRANSLATIONAL_INHIBITION"
    PHYSICAL_STIMULATION = "PHYSICAL_STIMULATION"
    MODULATION = "MODULATION"
    TRIGGER = "TRIGGER"
    BOOLEAN_LOGIC_GATE_AND = "BOOLEAN_LOGIC_GATE_AND"
    BOOLEAN_LOGIC_GATE_OR = "BOOLEAN_LOGIC_GATE_OR"
    BOOLEAN_LOGIC_GATE_NOT = "BOOLEAN_LOGIC_GATE_NOT"
    BOOLEAN_LOGIC_GATE_UNKNOWN = "BOOLEAN_LOGIC_GATE_UNKNOWN"


@dataclass
class Name:
    """
    Name of a compartment, or a species.
    """
    class Meta:
        name = "name"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: str = field(
        default=""
    )


@dataclass
class Notes:
    """
    Notes as in sbml.
    """
    class Meta:
        name = "notes"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    w3_org_1999_xhtml_element: List[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "http://www.w3.org/1999/xhtml",
        }
    )


@dataclass
class Offset:
    """
    Offset of a link from default position(center to center).
    """
    class Meta:
        name = "offset"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    x: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    y: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class PaintScheme(Enum):
    COLOR = "Color"
    GRADATION = "Gradation"


@dataclass
class Point:
    """
    Point of an object on canvas.
    """
    class Meta:
        name = "point"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    x: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    y: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


class PositionToCompartmentValue(Enum):
    OUTER_SURFACE = "outerSurface"
    TRANSMEMBRANE = "transmembrane"
    INNER_SURFACE = "innerSurface"
    INSIDE = "inside"
    INSIDE_OF_MEMBRANE = "insideOfMembrane"


@dataclass
class ProteinReference:
    """
    Reference to a protein.
    """
    class Meta:
        name = "proteinReference"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: str = field(
        default="",
        metadata={
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


class ProteinType(Enum):
    GENERIC = "GENERIC"
    ION_CHANNEL = "ION_CHANNEL"
    RECEPTOR = "RECEPTOR"
    TRUNCATED = "TRUNCATED"


class ReactionTypeValue(Enum):
    STATE_TRANSITION = "STATE_TRANSITION"
    KNOWN_TRANSITION_OMITTED = "KNOWN_TRANSITION_OMITTED"
    UNKNOWN_TRANSITION = "UNKNOWN_TRANSITION"
    CATALYSIS = "CATALYSIS"
    UNKNOWN_CATALYSIS = "UNKNOWN_CATALYSIS"
    INHIBITION = "INHIBITION"
    UNKNOWN_INHIBITION = "UNKNOWN_INHIBITION"
    TRANSPORT = "TRANSPORT"
    HETERODIMER_ASSOCIATION = "HETERODIMER_ASSOCIATION"
    DISSOCIATION = "DISSOCIATION"
    TRUNCATION = "TRUNCATION"
    TRANSCRIPTIONAL_ACTIVATION = "TRANSCRIPTIONAL_ACTIVATION"
    TRANSCRIPTIONAL_INHIBITION = "TRANSCRIPTIONAL_INHIBITION"
    TRANSLATIONAL_ACTIVATION = "TRANSLATIONAL_ACTIVATION"
    TRANSLATIONAL_INHIBITION = "TRANSLATIONAL_INHIBITION"
    TRANSCRIPTION = "TRANSCRIPTION"
    TRANSLATION = "TRANSLATION"
    BOOLEAN_LOGIC_GATE = "BOOLEAN_LOGIC_GATE"
    PHYSICAL_STIMULATION = "PHYSICAL_STIMULATION"
    MODULATION = "MODULATION"
    TRIGGER = "TRIGGER"


class RegionType(Enum):
    PROTEIN_BINDING_DOMAIN = "proteinBindingDomain"
    MODIFICATION_SITE = "Modification Site"
    TRANSCRIPTION_STARTING_SITE_L = "transcriptionStartingSiteL"
    TRANSCRIPTION_STARTING_SITE_R = "transcriptionStartingSiteR"
    CODING_REGION = "CodingRegion"
    REGULATORY_REGION = "RegulatoryRegion"
    EMPTY = "empty"


class ResidueInBlockDiagramOffsetX(Enum):
    VALUE_MINUS_103_82142857142863 = Decimal("-103.82142857142863")
    VALUE_MINUS_15_0 = Decimal("-15.0")
    VALUE_MINUS_18_321428571428584 = Decimal("-18.321428571428584")
    VALUE_MINUS_23_0 = Decimal("-23.0")
    VALUE_MINUS_45_0 = Decimal("-45.0")
    VALUE_MINUS_75_0 = Decimal("-75.0")
    VALUE_0_0 = Decimal("0.0")
    VALUE_15_0_1 = Decimal("15.0")
    VALUE_23_0_1 = Decimal("23.0")
    VALUE_45_0_1 = Decimal("45.0")
    VALUE_75_0_1 = Decimal("75.0")


class ResidueInBlockDiagramType(Enum):
    PHOSPHORYLATED = "phosphorylated"
    ACETYLATED = "acetylated"
    UBIQUITINATED = "ubiquitinated"
    METHYLATED = "methylated"
    HYDROXYLATED = "hydroxylated"
    EMPTY = "empty"
    DONTCARE = "dontcare"
    UNKNOWN = "unknown"


@dataclass
class RnaReference:
    """
    Reference to an rna.
    """
    class Meta:
        name = "rnaReference"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: str = field(
        default="",
        metadata={
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class SingleLine:
    """
    Single line type to draw object.
    """
    class Meta:
        name = "singleLine"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    width: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": Decimal("0.0"),
        }
    )


@dataclass
class SpeciesReferenceAnnotationType:
    """
    Annotation for (modifier)speciesReference.
    """
    class Meta:
        name = "speciesReferenceAnnotationType"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    extension: Optional["SpeciesReferenceAnnotationType.Extension"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )

    @dataclass
    class Extension:
        alias: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
                "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
            }
        )


@dataclass
class StartingPointInBlockDiagram:
    """
    Starting point (residue, binding site, operator) of the link.
    """
    class Meta:
        name = "startingPointInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    offset_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetX",
            "type": "Attribute",
            "required": True,
        }
    )
    offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetY",
            "type": "Attribute",
            "required": True,
        }
    )
    residue: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )
    binding_site: Optional[int] = field(
        default=None,
        metadata={
            "name": "bindingSite",
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )
    operator: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
        }
    )


@dataclass
class StructuralStateAngle:
    class Meta:
        name = "structuralStateAngle"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    angle: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


class ViewState(Enum):
    BRIEF = "brief"
    USUAL = "usual"
    COMPLEXNOBORDER = "complexnoborder"
    COMPLEXPARENTBRIEF = "complexparentbrief"
    NONE = "none"


@dataclass
class Sbase:
    """The SBase type is the base type of all main components in SBML.

    It supports attaching metadata, notes and annotations to components.
    """
    class Meta:
        name = "SBase"
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    notes: Optional["Sbase.Notes"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    metaid: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
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


class UnitKind(Enum):
    AMPERE = "ampere"
    BECQUEREL = "becquerel"
    CANDELA = "candela"
    CELSIUS = "Celsius"
    COULOMB = "coulomb"
    DIMENSIONLESS = "dimensionless"
    FARAD = "farad"
    GRAM = "gram"
    GRAY = "gray"
    HENRY = "henry"
    HERTZ = "hertz"
    ITEM = "item"
    JOULE = "joule"
    KATAL = "katal"
    KELVIN = "kelvin"
    KILOGRAM = "kilogram"
    LITRE = "litre"
    LUMEN = "lumen"
    LUX = "lux"
    METRE = "metre"
    MOLE = "mole"
    NEWTON = "newton"
    OHM = "ohm"
    PASCAL = "pascal"
    RADIAN = "radian"
    SECOND = "second"
    SIEMENS = "siemens"
    SIEVERT = "sievert"
    STERADIAN = "steradian"
    TESLA = "tesla"
    VOLT = "volt"
    WATT = "watt"
    WEBER = "weber"


@dataclass
class Annotation:
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    value: str = field(
        default="",
        metadata={
            "required": True,
        }
    )
    class_value: List[str] = field(
        default_factory=list,
        metadata={
            "name": "class",
            "type": "Attribute",
            "tokens": True,
        }
    )
    style: Optional[str] = field(
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
    encoding: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class AnnotationXml:
    class Meta:
        name = "Annotation-xml"
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    any_element: List[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
        }
    )
    class_value: List[str] = field(
        default_factory=list,
        metadata={
            "name": "class",
            "type": "Attribute",
            "tokens": True,
        }
    )
    style: Optional[str] = field(
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
    encoding: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class Ci:
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    value: str = field(
        default="",
        metadata={
            "required": True,
        }
    )
    class_value: List[str] = field(
        default_factory=list,
        metadata={
            "name": "class",
            "type": "Attribute",
            "tokens": True,
        }
    )
    style: Optional[str] = field(
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
    definition_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "definitionURL",
            "type": "Attribute",
        }
    )


class CnAttributesType(Enum):
    E_NOTATION = "e-notation"
    INTEGER = "integer"
    RATIONAL = "rational"
    REAL = "real"


class CsymbolUri(Enum):
    HTTP_WWW_SBML_ORG_SBML_SYMBOLS_TIME = "http://www.sbml.org/sbml/symbols/time"
    HTTP_WWW_SBML_ORG_SBML_SYMBOLS_DELAY = "http://www.sbml.org/sbml/symbols/delay"


@dataclass
class MathBase:
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    class_value: List[str] = field(
        default_factory=list,
        metadata={
            "name": "class",
            "type": "Attribute",
            "tokens": True,
        }
    )
    style: Optional[str] = field(
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
class SepType:
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"


@dataclass
class Activity:
    """
    Designation of activity of the species (aliases).
    """
    class Meta:
        name = "activity"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: Optional[ActivityValue] = field(
        default=None
    )


@dataclass
class Class:
    """
    Object classes for network nodes or containers of process diagrams.
    """
    class Meta:
        name = "class"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: Optional[ClassValue] = field(
        default=None
    )


@dataclass
class DegradedInBlockDiagram:
    """
    Degradation of a protein represented by the block.
    """
    class Meta:
        name = "degradedInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    degraded_shape_in_block_diagram: Optional[DegradedShapeInBlockDiagram] = field(
        default=None,
        metadata={
            "name": "degradedShapeInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetY",
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class EffectInBlockDiagram:
    """
    Type and targets of an effect.
    """
    class Meta:
        name = "effectInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    effect_target_in_block_diagram: List[EffectTargetInBlockDiagram] = field(
        default_factory=list,
        metadata={
            "name": "effectTargetInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )
    type: Optional[EffectInBlockDiagramType] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class ExternalConnectionInBlockDiagram:
    """
    External connection to a residue.
    """
    class Meta:
        name = "externalConnectionInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    residue: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    type: Optional[ExternalConnectionInBlockDiagramType] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    predefined: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class InternalLinkInBlockDiagram:
    """Link between operators, residues, binding sites, effect sites.

    and degradation.
    """
    class Meta:
        name = "internalLinkInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    starting_point_in_block_diagram: Optional[StartingPointInBlockDiagram] = field(
        default=None,
        metadata={
            "name": "startingPointInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    end_point_in_block_diagram: Optional[EndPointInBlockDiagram] = field(
        default=None,
        metadata={
            "name": "endPointInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    type: Optional[InternalLinkInBlockDiagramType] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class InternalOperatorInBlockDiagram:
    """
    Operator inside of a block(protein) describing logic.
    """
    class Meta:
        name = "internalOperatorInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    internal_operator_value_in_block_diagram: Optional[InternalOperatorValueInBlockDiagram] = field(
        default=None,
        metadata={
            "name": "internalOperatorValueInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    type: Optional[InternalOperatorInBlockDiagramType] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    sub: Optional[InternalOperatorInBlockDiagramSub] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    offset_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetX",
            "type": "Attribute",
            "required": True,
        }
    )
    offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetY",
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class LayerFreeLine:
    class Meta:
        name = "layerFreeLine"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    bounds: Optional[LayerLineBounds] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    line: Optional[Line] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    is_arrow: Optional[bool] = field(
        default=None,
        metadata={
            "name": "isArrow",
            "type": "Attribute",
        }
    )
    is_dotted: Optional[bool] = field(
        default=None,
        metadata={
            "name": "isDotted",
            "type": "Attribute",
        }
    )


@dataclass
class LineDirection:
    """
    Line direction designator.
    """
    class Meta:
        name = "lineDirection"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    index: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    value: Optional[LineDirectionValue] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    arm: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 2,
        }
    )


@dataclass
class LineType2:
    """
    Line color, width and curve style.
    """
    class Meta:
        name = "lineType2"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9a-fA-F]{8}",
        }
    )
    width: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": Decimal("0.0"),
        }
    )
    type: Optional[LineType2Type] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class LinkAnchor:
    """
    Link position designator to species alias.
    """
    class Meta:
        name = "linkAnchor"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    position: Optional[LinkAnchorPosition] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class ListOfBindingRegions:
    class Meta:
        name = "listOfBindingRegions"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    binding_region: List[BindingRegion] = field(
        default_factory=list,
        metadata={
            "name": "bindingRegion",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfBindingSitesInBlockDiagram:
    """
    List of binding sites of a block(protein).
    """
    class Meta:
        name = "listOfBindingSitesInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    binding_site_in_block_diagram: List[BindingSiteInBlockDiagram] = field(
        default_factory=list,
        metadata={
            "name": "bindingSiteInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class ListOfCatalyzedReactions:
    """
    List of catalyzed reaction.
    """
    class Meta:
        name = "listOfCatalyzedReactions"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    catalyzed: List[Catalyzed] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfGroups:
    """
    List of groups.
    """
    class Meta:
        name = "listOfGroups"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    group: List[Group] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class ListOfModificationResidues:
    """
    List of modification residues.
    """
    class Meta:
        name = "listOfModificationResidues"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    modification_residue: List[ModificationResidue] = field(
        default_factory=list,
        metadata={
            "name": "modificationResidue",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfModifications:
    """
    List of residue modification.
    """
    class Meta:
        name = "listOfModifications"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    modification: List["ListOfModifications.Modification"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )

    @dataclass
    class Modification:
        residue: Optional[str] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
                "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
            }
        )
        state: Optional[ModificationState] = field(
            default=None,
            metadata={
                "type": "Attribute",
                "required": True,
            }
        )


@dataclass
class ListOfStructuralStates:
    class Meta:
        name = "listOfStructuralStates"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    structural_state: Optional[StructuralStates] = field(
        default=None,
        metadata={
            "name": "structuralState",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )


@dataclass
class Paint:
    """
    Paint scheme to paint object.
    """
    class Meta:
        name = "paint"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    color: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"[0-9a-fA-F]{8}",
        }
    )
    scheme: Optional[PaintScheme] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class PositionToCompartment:
    """Species' position to its parent compartment.

    For the species not forming any complex.
    """
    class Meta:
        name = "positionToCompartment"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: Optional[PositionToCompartmentValue] = field(
        default=None
    )


@dataclass
class ReactionType:
    """
    Base reaction type.
    """
    class Meta:
        name = "reactionType"
        namespace = "http://www.sbml.org/2001/ns/celldesigner"

    value: Optional[ReactionTypeValue] = field(
        default=None
    )


@dataclass
class Region:
    """
    Specific region on nucleotide.
    """
    class Meta:
        name = "region"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    size: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": Decimal("0.0"),
            "max_inclusive": Decimal("1.0"),
        }
    )
    pos: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "min_inclusive": Decimal("0.0"),
            "max_inclusive": Decimal("1.0"),
        }
    )
    type: Optional[RegionType] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    active: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class ResidueInBlockDiagram:
    """
    Residue on the upper side of a block(protein).
    """
    class Meta:
        name = "residueInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    residue: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    type: Optional[ResidueInBlockDiagramType] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    offset_x: Optional[ResidueInBlockDiagramOffsetX] = field(
        default=None,
        metadata={
            "name": "offsetX",
            "type": "Attribute",
            "required": True,
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    name_offset_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "nameOffsetX",
            "type": "Attribute",
        }
    )
    name_offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "nameOffsetY",
            "type": "Attribute",
        }
    )


@dataclass
class View:
    """
    View state.
    """
    class Meta:
        name = "view"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    state: Optional[ViewState] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class Compartment(Sbase):
    """
    Redefined compartment.
    """
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    size: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    spatial_dimensions: int = field(
        default=3,
        metadata={
            "name": "spatialDimensions",
            "type": "Attribute",
            "min_inclusive": 0,
            "max_inclusive": 3,
        }
    )
    units: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    outside: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    constant: bool = field(
        default=True,
        metadata={
            "type": "Attribute",
        }
    )
    annotation: Optional[CompartmentAnnotationType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )


@dataclass
class Parameter(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    value: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    units: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    constant: bool = field(
        default=True,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class SimpleSpeciesReference(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    species: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class Unit(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    kind: Optional[UnitKind] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    exponent: int = field(
        default=1,
        metadata={
            "type": "Attribute",
        }
    )
    scale: int = field(
        default=0,
        metadata={
            "type": "Attribute",
        }
    )
    multiplier: float = field(
        default=1.0,
        metadata={
            "type": "Attribute",
        }
    )
    offset: float = field(
        default=0.0,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class Bvar(MathBase):
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    ci: Optional[Ci] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "required": True,
        }
    )


@dataclass
class Cn:
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    type: Optional[CnAttributesType] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    class_value: List[str] = field(
        default_factory=list,
        metadata={
            "name": "class",
            "type": "Attribute",
            "tokens": True,
        }
    )
    style: Optional[str] = field(
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
    content: List[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
            "choices": (
                {
                    "name": "sep",
                    "type": SepType,
                    "namespace": "http://www.w3.org/1998/Math/MathML",
                },
            ),
        }
    )


@dataclass
class Csymbol:
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    value: str = field(
        default="",
        metadata={
            "required": True,
        }
    )
    encoding: str = field(
        init=False,
        default="text",
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    definition_url: Optional[CsymbolUri] = field(
        default=None,
        metadata={
            "name": "definitionURL",
            "type": "Attribute",
            "required": True,
        }
    )
    class_value: List[str] = field(
        default_factory=list,
        metadata={
            "name": "class",
            "type": "Attribute",
            "tokens": True,
        }
    )
    style: Optional[str] = field(
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
class SpeciesTag:
    class Meta:
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    key_info: Optional[KeyInfo] = field(
        default=None,
        metadata={
            "name": "KeyInfo",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    tag_bounds: Optional[TagBounds] = field(
        default=None,
        metadata={
            "name": "TagBounds",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    tag_edge_line: Optional[TagEdgeLine] = field(
        default=None,
        metadata={
            "name": "TagEdgeLine",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    tag_frame_paint: Optional[Paint] = field(
        default=None,
        metadata={
            "name": "TagFramePaint",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )


@dataclass
class BaseProduct:
    """
    Base product.
    """
    class Meta:
        name = "baseProduct"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    link_anchor: Optional[LinkAnchor] = field(
        default=None,
        metadata={
            "name": "linkAnchor",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    alias: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    species: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class BaseReactant:
    """
    Base reactant.
    """
    class Meta:
        name = "baseReactant"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    link_anchor: Optional[LinkAnchor] = field(
        default=None,
        metadata={
            "name": "linkAnchor",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    alias: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    species: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class BriefView:
    """
    Data for drawing object with brief (compact) view.
    """
    class Meta:
        name = "briefView"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    inner_position: Optional[InnerPosition] = field(
        default=None,
        metadata={
            "name": "innerPosition",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    box_size: Optional[BoxSize] = field(
        default=None,
        metadata={
            "name": "boxSize",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    single_line: Optional[SingleLine] = field(
        default=None,
        metadata={
            "name": "singleLine",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    paint: Optional[Paint] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )


@dataclass
class CompartmentAlias:
    """
    For compartment aliases.
    """
    class Meta:
        name = "compartmentAlias"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    class_value: Optional[ClassValue] = field(
        default=None,
        metadata={
            "name": "class",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    bounds: Optional[Bounds] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    point: Optional[Point] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    name_point: Optional[Point] = field(
        default=None,
        metadata={
            "name": "namePoint",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    double_line: Optional[DoubleLine] = field(
        default=None,
        metadata={
            "name": "doubleLine",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    paint: Optional[Paint] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    info: Optional[Info] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    compartment: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class EffectSiteInBlockDiagram:
    """
    Effect site on the lower side of a block(protein).
    """
    class Meta:
        name = "effectSiteInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    effect_in_block_diagram: Optional[EffectInBlockDiagram] = field(
        default=None,
        metadata={
            "name": "effectInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    offset_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetX",
            "type": "Attribute",
            "required": True,
        }
    )
    offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetY",
            "type": "Attribute",
            "required": True,
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    name_offset_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "nameOffsetX",
            "type": "Attribute",
            "required": True,
        }
    )
    name_offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "nameOffsetY",
            "type": "Attribute",
            "required": True,
        }
    )
    reaction: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    species: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class LayerCompartmentAlias:
    class Meta:
        name = "layerCompartmentAlias"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    bounds: Optional[Bounds] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    paint: Optional[Paint] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    type: Optional[LayerCompartmentAliasType] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class LayerSpeciesAlias:
    class Meta:
        name = "layerSpeciesAlias"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    layer_notes: Optional[str] = field(
        default=None,
        metadata={
            "name": "layerNotes",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    bounds: Optional[Bounds] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    paint: Optional[Paint] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    font: Optional["LayerSpeciesAlias.Font"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
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
    target_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "targetId",
            "type": "Attribute",
            "required": True,
        }
    )
    x: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    y: Optional[Decimal] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )

    @dataclass
    class Font:
        size: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
            }
        )


@dataclass
class LinkTarget:
    """
    Target of a link.
    """
    class Meta:
        name = "linkTarget"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    link_anchor: Optional[LinkAnchor] = field(
        default=None,
        metadata={
            "name": "linkAnchor",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    alias: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    species: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class ListOfExternalConnectionsInBlockDiagram:
    """
    List of external connections to residues.
    """
    class Meta:
        name = "listOfExternalConnectionsInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    external_connection_in_block_diagram: List[ExternalConnectionInBlockDiagram] = field(
        default_factory=list,
        metadata={
            "name": "externalConnectionInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfFreeLines:
    class Meta:
        name = "listOfFreeLines"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    layer_free_line: List[LayerFreeLine] = field(
        default_factory=list,
        metadata={
            "name": "layerFreeLine",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfInternalLinksInBlockDiagram:
    """
    List of links of a block(protein).
    """
    class Meta:
        name = "listOfInternalLinksInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    internal_link_in_block_diagram: List[InternalLinkInBlockDiagram] = field(
        default_factory=list,
        metadata={
            "name": "internalLinkInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class ListOfInternalOperatorsInBlockDiagram:
    """
    List of internal operators.
    """
    class Meta:
        name = "listOfInternalOperatorsInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    internal_operator_in_block_diagram: List[InternalOperatorInBlockDiagram] = field(
        default_factory=list,
        metadata={
            "name": "internalOperatorInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class ListOfLineDirection:
    """
    List of line direction.
    """
    class Meta:
        name = "listOfLineDirection"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    line_direction: List[LineDirection] = field(
        default_factory=list,
        metadata={
            "name": "lineDirection",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfRegions:
    """
    List of regions.
    """
    class Meta:
        name = "listOfRegions"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    region: List[Region] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfResiduesInBlockDiagram:
    """
    List of residues on a block(protein).
    """
    class Meta:
        name = "listOfResiduesInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    residue_in_block_diagram: List[ResidueInBlockDiagram] = field(
        default_factory=list,
        metadata={
            "name": "residueInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class ProductLink:
    """
    Product link type.
    """
    class Meta:
        name = "productLink"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    link_anchor: Optional[LinkAnchor] = field(
        default=None,
        metadata={
            "name": "linkAnchor",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    edit_points: Optional[EditPoints] = field(
        default=None,
        metadata={
            "name": "editPoints",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    line: Optional[LineType2] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    alias: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    product: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    target_line_index: Optional[str] = field(
        default=None,
        metadata={
            "name": "targetLineIndex",
            "type": "Attribute",
            "required": True,
            "pattern": r"-?[0-9]+,[0-9]+",
        }
    )


@dataclass
class Protein:
    """
    For protein.
    """
    class Meta:
        name = "protein"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    notes: Optional[Notes] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    list_of_binding_regions: Optional[ListOfBindingRegions] = field(
        default=None,
        metadata={
            "name": "listOfBindingRegions",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    list_of_modification_residues: Optional[ListOfModificationResidues] = field(
        default=None,
        metadata={
            "name": "listOfModificationResidues",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    list_of_structural_states: Optional[ListOfStructuralStates] = field(
        default=None,
        metadata={
            "name": "listOfStructuralStates",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    type: Optional[ProteinType] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class ReactantLink:
    """
    Reactant link type.
    """
    class Meta:
        name = "reactantLink"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    link_anchor: Optional[LinkAnchor] = field(
        default=None,
        metadata={
            "name": "linkAnchor",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    edit_points: Optional[EditPoints] = field(
        default=None,
        metadata={
            "name": "editPoints",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    line: Optional[LineType2] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    alias: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    reactant: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    target_line_index: Optional[str] = field(
        default=None,
        metadata={
            "name": "targetLineIndex",
            "type": "Attribute",
            "required": True,
            "pattern": r"-?[0-9]+,[0-9]+",
        }
    )


@dataclass
class State:
    """
    Chemical "state" to distinguish chemical species derived from a root
    chemical.
    """
    class Meta:
        name = "state"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    homodimer: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    list_of_modifications: Optional[ListOfModifications] = field(
        default=None,
        metadata={
            "name": "listOfModifications",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    list_of_structural_states: Optional[ListOfStructuralStates] = field(
        default=None,
        metadata={
            "name": "listOfStructuralStates",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class UsualView:
    """
    Data for drawing object with usual view.
    """
    class Meta:
        name = "usualView"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    inner_position: Optional[InnerPosition] = field(
        default=None,
        metadata={
            "name": "innerPosition",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    box_size: Optional[BoxSize] = field(
        default=None,
        metadata={
            "name": "boxSize",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    single_line: Optional[SingleLine] = field(
        default=None,
        metadata={
            "name": "singleLine",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    paint: Optional[Paint] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )


@dataclass
class ListOfParameters(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    parameter: List[Parameter] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfUnits(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    unit: List[Unit] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
            "min_occurs": 1,
        }
    )


@dataclass
class ModifierSpeciesReference(SimpleSpeciesReference):
    """
    Redefined modifierSpeciesReference.
    """
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    annotation: Optional[SpeciesReferenceAnnotationType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )


@dataclass
class Otherwise(MathBase):
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    apply: Optional["Apply"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    cn: Optional[Cn] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    ci: Optional[Ci] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    csymbol: Optional[Csymbol] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    true: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    false: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    notanumber: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    pi: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    infinity: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    exponentiale: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    semantics: Optional["Semantics"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    piecewise: Optional["Piecewise"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )


@dataclass
class Piece(MathBase):
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    apply: List["Apply"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "min_occurs": 2,
            "max_occurs": 2,
        }
    )
    cn: List[Cn] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "min_occurs": 2,
            "max_occurs": 2,
        }
    )
    ci: List[Ci] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "min_occurs": 2,
            "max_occurs": 2,
        }
    )
    csymbol: List[Csymbol] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "min_occurs": 2,
            "max_occurs": 2,
        }
    )
    true: List[MathBase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "min_occurs": 2,
            "max_occurs": 2,
        }
    )
    false: List[MathBase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "min_occurs": 2,
            "max_occurs": 2,
        }
    )
    notanumber: List[MathBase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "min_occurs": 2,
            "max_occurs": 2,
        }
    )
    pi: List[MathBase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "min_occurs": 2,
            "max_occurs": 2,
        }
    )
    infinity: List[MathBase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "min_occurs": 2,
            "max_occurs": 2,
        }
    )
    exponentiale: List[MathBase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "min_occurs": 2,
            "max_occurs": 2,
        }
    )
    semantics: List["Semantics"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "min_occurs": 2,
            "max_occurs": 2,
        }
    )
    piecewise: List["Piecewise"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "min_occurs": 2,
            "max_occurs": 2,
        }
    )


@dataclass
class AntisenseRna:
    """
    For antisense RNA.
    """
    class Meta:
        name = "AntisenseRNA"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    notes: Optional[Notes] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    list_of_regions: Optional[ListOfRegions] = field(
        default=None,
        metadata={
            "name": "listOfRegions",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    type: Optional[AntisenseRnaType] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class Rna:
    """
    For RNA.
    """
    class Meta:
        name = "RNA"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    notes: Optional[Notes] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    list_of_regions: Optional[ListOfRegions] = field(
        default=None,
        metadata={
            "name": "listOfRegions",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    type: Optional[RnaType] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class BaseProducts:
    """
    List of base products.
    """
    class Meta:
        name = "baseProducts"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    base_product: List[BaseProduct] = field(
        default_factory=list,
        metadata={
            "name": "baseProduct",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
            "max_occurs": 2,
        }
    )


@dataclass
class BaseReactants:
    """
    List of base reactants.
    """
    class Meta:
        name = "baseReactants"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    base_reactant: List[BaseReactant] = field(
        default_factory=list,
        metadata={
            "name": "baseReactant",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
            "max_occurs": 2,
        }
    )


@dataclass
class ConnectScheme:
    """
    Connection scheme.
    """
    class Meta:
        name = "connectScheme"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    list_of_line_direction: Optional[ListOfLineDirection] = field(
        default=None,
        metadata={
            "name": "listOfLineDirection",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    connect_policy: Optional[ConnectSchemeConnectPolicy] = field(
        default=None,
        metadata={
            "name": "connectPolicy",
            "type": "Attribute",
            "required": True,
        }
    )
    rectangle_index: Optional[str] = field(
        default=None,
        metadata={
            "name": "rectangleIndex",
            "type": "Attribute",
        }
    )


@dataclass
class ExternalNameForResidue:
    """
    External protein name connecting to residues.
    """
    class Meta:
        name = "externalNameForResidue"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    list_of_external_connections_in_block_diagram: Optional[ListOfExternalConnectionsInBlockDiagram] = field(
        default=None,
        metadata={
            "name": "listOfExternalConnectionsInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    id: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "min_inclusive": 0,
        }
    )
    offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetY",
            "type": "Attribute",
            "required": True,
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    name_offset_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "nameOffsetX",
            "type": "Attribute",
            "required": True,
        }
    )
    name_offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "nameOffsetY",
            "type": "Attribute",
            "required": True,
        }
    )
    protein: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class Gene:
    """
    For gene.
    """
    class Meta:
        name = "gene"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    notes: Optional[Notes] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    list_of_regions: Optional[ListOfRegions] = field(
        default=None,
        metadata={
            "name": "listOfRegions",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    type: Optional[GeneType] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class ListOfCompartmentAliases:
    """
    List of compartment aliases.
    """
    class Meta:
        name = "listOfCompartmentAliases"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    compartment_alias: List[CompartmentAlias] = field(
        default_factory=list,
        metadata={
            "name": "compartmentAlias",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class ListOfEffectSitesInBlockDiagram:
    """
    List of effect sites.
    """
    class Meta:
        name = "listOfEffectSitesInBlockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    effect_site_in_block_diagram: List[EffectSiteInBlockDiagram] = field(
        default_factory=list,
        metadata={
            "name": "effectSiteInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class ListOfProductLinks:
    """
    List of product link types.
    """
    class Meta:
        name = "listOfProductLinks"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    product_link: List[ProductLink] = field(
        default_factory=list,
        metadata={
            "name": "productLink",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfProteins:
    """
    List of proteins.
    """
    class Meta:
        name = "listOfProteins"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    protein: List[Protein] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class ListOfReactantLinks:
    """
    List of reactant link types.
    """
    class Meta:
        name = "listOfReactantLinks"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    reactant_link: List[ReactantLink] = field(
        default_factory=list,
        metadata={
            "name": "reactantLink",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfSpeciesTag:
    class Meta:
        name = "listOfSpeciesTag"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    species_tag: List[SpeciesTag] = field(
        default_factory=list,
        metadata={
            "name": "SpeciesTag",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfSquares:
    class Meta:
        name = "listOfSquares"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    layer_compartment_alias: List[LayerCompartmentAlias] = field(
        default_factory=list,
        metadata={
            "name": "layerCompartmentAlias",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfTexts:
    class Meta:
        name = "listOfTexts"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    layer_species_alias: List[LayerSpeciesAlias] = field(
        default_factory=list,
        metadata={
            "name": "layerSpeciesAlias",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class SpeciesIdentity:
    """
    Identity to distinguish chemical species of CellDesigner's model.
    """
    class Meta:
        name = "speciesIdentity"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    class_value: Optional[ClassValue] = field(
        default=None,
        metadata={
            "name": "class",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    hypothetical: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    protein_reference: Optional[str] = field(
        default=None,
        metadata={
            "name": "proteinReference",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    rna_reference: Optional[str] = field(
        default=None,
        metadata={
            "name": "rnaReference",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    gene_reference: Optional[str] = field(
        default=None,
        metadata={
            "name": "geneReference",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    antisenserna_reference: Optional[str] = field(
        default=None,
        metadata={
            "name": "antisensernaReference",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    state: Optional[State] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class ListOfModifierSpeciesReferences(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    modifier_species_reference: List[ModifierSpeciesReference] = field(
        default_factory=list,
        metadata={
            "name": "modifierSpeciesReference",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
            "min_occurs": 1,
        }
    )


@dataclass
class UnitDefinition(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    list_of_units: Optional[ListOfUnits] = field(
        default=None,
        metadata={
            "name": "listOfUnits",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
            "required": True,
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class Piecewise(MathBase):
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    piece: List[Piece] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    otherwise: Optional[Otherwise] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )


@dataclass
class ComplexSpeciesAlias:
    """
    For species aliases of complex species.
    """
    class Meta:
        name = "complexSpeciesAlias"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    activity: Optional[ActivityValue] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    bounds: Optional[Bounds] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    font: Optional["ComplexSpeciesAlias.Font"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    view: Optional[View] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    backup_size: Optional["ComplexSpeciesAlias.BackupSize"] = field(
        default=None,
        metadata={
            "name": "backupSize",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    backup_view: Optional[View] = field(
        default=None,
        metadata={
            "name": "backupView",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    structural_state: Optional[StructuralStateAngle] = field(
        default=None,
        metadata={
            "name": "structuralState",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    usual_view: Optional[UsualView] = field(
        default=None,
        metadata={
            "name": "usualView",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    brief_view: Optional[BriefView] = field(
        default=None,
        metadata={
            "name": "briefView",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    list_of_species_tag: Optional[ListOfSpeciesTag] = field(
        default=None,
        metadata={
            "name": "listOfSpeciesTag",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    info: Optional[Info] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    compartment_alias: Optional[str] = field(
        default=None,
        metadata={
            "name": "compartmentAlias",
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    species: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )

    @dataclass
    class Font:
        size: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
            }
        )

    @dataclass
    class BackupSize:
        w: Optional[float] = field(
            default=None,
            metadata={
                "type": "Attribute",
            }
        )
        h: Optional[float] = field(
            default=None,
            metadata={
                "type": "Attribute",
            }
        )


@dataclass
class Layer:
    class Meta:
        name = "layer"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    list_of_texts: Optional[ListOfTexts] = field(
        default=None,
        metadata={
            "name": "listOfTexts",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    list_of_squares: Optional[ListOfSquares] = field(
        default=None,
        metadata={
            "name": "listOfSquares",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    list_of_free_lines: Optional[ListOfFreeLines] = field(
        default=None,
        metadata={
            "name": "listOfFreeLines",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    locked: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    visible: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class ListOfAntisenseRnas:
    """
    List of asRNAs.
    """
    class Meta:
        name = "listOfAntisenseRNAs"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    antisense_rna: List[AntisenseRna] = field(
        default_factory=list,
        metadata={
            "name": "AntisenseRNA",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class ListOfExternalNamesForResidue:
    """
    List of external names.
    """
    class Meta:
        name = "listOfExternalNamesForResidue"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    external_name_for_residue: List[ExternalNameForResidue] = field(
        default_factory=list,
        metadata={
            "name": "externalNameForResidue",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class ListOfGenes:
    """
    List of genes.
    """
    class Meta:
        name = "listOfGenes"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    gene: List[Gene] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class ListOfRnas:
    """
    List of RNAs.
    """
    class Meta:
        name = "listOfRNAs"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    rna: List[Rna] = field(
        default_factory=list,
        metadata={
            "name": "RNA",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class Modification:
    """
    Line modification.
    """
    class Meta:
        name = "modification"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    connect_scheme: Optional[ConnectScheme] = field(
        default=None,
        metadata={
            "name": "connectScheme",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    link_target: List[LinkTarget] = field(
        default_factory=list,
        metadata={
            "name": "linkTarget",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "max_occurs": 2,
        }
    )
    line: Optional[Line] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    aliases: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*(,(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*)*",
        }
    )
    modifiers: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*(,(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*)*",
        }
    )
    type: Optional[ModificationType] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    target_line_index: Optional[str] = field(
        default=None,
        metadata={
            "name": "targetLineIndex",
            "type": "Attribute",
            "required": True,
            "pattern": r"-?[0-9]+,[0-9]+",
        }
    )
    edit_points: List[str] = field(
        default_factory=list,
        metadata={
            "name": "editPoints",
            "type": "Attribute",
            "pattern": r"(\+|-)?[0-9]+(\.[0-9]*)?((e|E)(\+|-)?[0-9]+)?,(\+|-)?[0-9]+(\.[0-9]*)?((e|E)(\+|-)?[0-9]+)?",
            "tokens": True,
        }
    )
    num0: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    num1: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    num2: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    modification: Optional[ModificationModification] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    offset_x: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetX",
            "type": "Attribute",
        }
    )
    offset_y: Optional[Decimal] = field(
        default=None,
        metadata={
            "name": "offsetY",
            "type": "Attribute",
        }
    )


@dataclass
class SpeciesAlias:
    """
    For species aliases not forming complexes.
    """
    class Meta:
        name = "speciesAlias"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    activity: Optional[ActivityValue] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    bounds: Optional[Bounds] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    font: Optional["SpeciesAlias.Font"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    view: Optional[View] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    structural_state: Optional[StructuralStateAngle] = field(
        default=None,
        metadata={
            "name": "structuralState",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    usual_view: Optional[UsualView] = field(
        default=None,
        metadata={
            "name": "usualView",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    brief_view: Optional[BriefView] = field(
        default=None,
        metadata={
            "name": "briefView",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    list_of_species_tag: Optional[ListOfSpeciesTag] = field(
        default=None,
        metadata={
            "name": "listOfSpeciesTag",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    info: Optional[Info] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    species: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    compartment_alias: Optional[str] = field(
        default=None,
        metadata={
            "name": "compartmentAlias",
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    complex_species_alias: Optional[str] = field(
        default=None,
        metadata={
            "name": "complexSpeciesAlias",
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )

    @dataclass
    class Font:
        size: Optional[int] = field(
            default=None,
            metadata={
                "type": "Attribute",
            }
        )


@dataclass
class SpeciesAnnotationType:
    """
    Annotation for species.
    """
    class Meta:
        name = "speciesAnnotationType"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    extension: Optional["SpeciesAnnotationType.Extension"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )

    @dataclass
    class Extension:
        position_to_compartment: Optional[PositionToCompartmentValue] = field(
            default=None,
            metadata={
                "name": "positionToCompartment",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            }
        )
        complex_species: Optional[str] = field(
            default=None,
            metadata={
                "name": "complexSpecies",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
            }
        )
        species_identity: Optional[SpeciesIdentity] = field(
            default=None,
            metadata={
                "name": "speciesIdentity",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        list_of_catalyzed_reactions: Optional[ListOfCatalyzedReactions] = field(
            default=None,
            metadata={
                "name": "listOfCatalyzedReactions",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            }
        )


@dataclass
class Species2:
    """
    Species inside complexes.
    """
    class Meta:
        name = "species"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    notes: Optional[Notes] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    annotation: Optional["Species2.Annotation"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    compartment: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    initial_amount: Optional[float] = field(
        default=None,
        metadata={
            "name": "initialAmount",
            "type": "Attribute",
        }
    )
    initial_concentration: Optional[float] = field(
        default=None,
        metadata={
            "name": "initialConcentration",
            "type": "Attribute",
        }
    )
    substance_units: Optional[str] = field(
        default=None,
        metadata={
            "name": "substanceUnits",
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    spatial_size_units: Optional[str] = field(
        default=None,
        metadata={
            "name": "spatialSizeUnits",
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    has_only_substance_units: bool = field(
        default=False,
        metadata={
            "name": "hasOnlySubstanceUnits",
            "type": "Attribute",
        }
    )
    boundary_condition: bool = field(
        default=False,
        metadata={
            "name": "boundaryCondition",
            "type": "Attribute",
        }
    )
    charge: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    constant: bool = field(
        default=False,
        metadata={
            "type": "Attribute",
        }
    )

    @dataclass
    class Annotation:
        position_to_compartment: Optional[PositionToCompartmentValue] = field(
            default=None,
            metadata={
                "name": "positionToCompartment",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            }
        )
        complex_species: Optional[str] = field(
            default=None,
            metadata={
                "name": "complexSpecies",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
            }
        )
        species_identity: Optional[SpeciesIdentity] = field(
            default=None,
            metadata={
                "name": "speciesIdentity",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        list_of_catalyzed_reactions: Optional[ListOfCatalyzedReactions] = field(
            default=None,
            metadata={
                "name": "listOfCatalyzedReactions",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            }
        )


@dataclass
class Lambda(MathBase):
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    bvar: List[Bvar] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    apply: Optional["Apply"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    cn: Optional[Cn] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    ci: Optional[Ci] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    csymbol: Optional[Csymbol] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    true: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    false: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    notanumber: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    pi: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    infinity: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    exponentiale: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    semantics: Optional["Semantics"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    piecewise: Optional[Piecewise] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )


@dataclass
class BlockDiagram:
    """
    Block diagram for a protein.
    """
    class Meta:
        name = "blockDiagram"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    canvas: Optional[Canvas] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    block: Optional[Block] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    halo: Optional[Halo] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    list_of_residues_in_block_diagram: Optional[ListOfResiduesInBlockDiagram] = field(
        default=None,
        metadata={
            "name": "listOfResiduesInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    list_of_external_names_for_residue: Optional[ListOfExternalNamesForResidue] = field(
        default=None,
        metadata={
            "name": "listOfExternalNamesForResidue",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    list_of_binding_sites_in_block_diagram: Optional[ListOfBindingSitesInBlockDiagram] = field(
        default=None,
        metadata={
            "name": "listOfBindingSitesInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    list_of_effect_sites_in_block_diagram: Optional[ListOfEffectSitesInBlockDiagram] = field(
        default=None,
        metadata={
            "name": "listOfEffectSitesInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    degraded_in_block_diagram: Optional[DegradedInBlockDiagram] = field(
        default=None,
        metadata={
            "name": "degradedInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )
    list_of_internal_operators_in_block_diagram: Optional[ListOfInternalOperatorsInBlockDiagram] = field(
        default=None,
        metadata={
            "name": "listOfInternalOperatorsInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    list_of_internal_links_in_block_diagram: Optional[ListOfInternalLinksInBlockDiagram] = field(
        default=None,
        metadata={
            "name": "listOfInternalLinksInBlockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )
    protein: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class ListOfComplexSpeciesAliases:
    """
    List of complex species aliases.
    """
    class Meta:
        name = "listOfComplexSpeciesAliases"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    complex_species_alias: List["ListOfComplexSpeciesAliases.ComplexSpeciesAlias"] = field(
        default_factory=list,
        metadata={
            "name": "complexSpeciesAlias",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )

    @dataclass
    class ComplexSpeciesAlias(ComplexSpeciesAlias):
        complex_species_alias: Optional[str] = field(
            default=None,
            metadata={
                "name": "complexSpeciesAlias",
                "type": "Attribute",
                "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
            }
        )


@dataclass
class ListOfIncludedSpecies:
    """
    List of species included by complexes.
    """
    class Meta:
        name = "listOfIncludedSpecies"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    species: List[Species2] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfLayers:
    class Meta:
        name = "listOfLayers"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    layer: List[Layer] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfModification:
    """
    List of line modification.
    """
    class Meta:
        name = "listOfModification"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    modification: List[Modification] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class ListOfSpeciesAliases:
    """
    List of simple species aliases.
    """
    class Meta:
        name = "listOfSpeciesAliases"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    species_alias: List[SpeciesAlias] = field(
        default_factory=list,
        metadata={
            "name": "speciesAlias",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "min_occurs": 1,
        }
    )


@dataclass
class Species1(Sbase):
    """
    Redefined species.
    """
    class Meta:
        name = "Species"
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    compartment: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    initial_amount: Optional[float] = field(
        default=None,
        metadata={
            "name": "initialAmount",
            "type": "Attribute",
        }
    )
    initial_concentration: Optional[float] = field(
        default=None,
        metadata={
            "name": "initialConcentration",
            "type": "Attribute",
        }
    )
    substance_units: Optional[str] = field(
        default=None,
        metadata={
            "name": "substanceUnits",
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    spatial_size_units: Optional[str] = field(
        default=None,
        metadata={
            "name": "spatialSizeUnits",
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    has_only_substance_units: bool = field(
        default=False,
        metadata={
            "name": "hasOnlySubstanceUnits",
            "type": "Attribute",
        }
    )
    boundary_condition: bool = field(
        default=False,
        metadata={
            "name": "boundaryCondition",
            "type": "Attribute",
        }
    )
    charge: Optional[int] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    constant: bool = field(
        default=False,
        metadata={
            "type": "Attribute",
        }
    )
    annotation: Optional[SpeciesAnnotationType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )


@dataclass
class Semantics(MathBase):
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    apply: Optional["Apply"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    cn: Optional[Cn] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    ci: Optional[Ci] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    csymbol: Optional[Csymbol] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    true: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    false: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    notanumber: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    pi: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    infinity: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    exponentiale: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    semantics: Optional["Semantics"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    piecewise: Optional[Piecewise] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    lambda_value: Optional[Lambda] = field(
        default=None,
        metadata={
            "name": "lambda",
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    annotation: List[Annotation] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "sequential": True,
        }
    )
    annotation_xml: List[AnnotationXml] = field(
        default_factory=list,
        metadata={
            "name": "annotation-xml",
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "sequential": True,
        }
    )
    definition_url: Optional[str] = field(
        default=None,
        metadata={
            "name": "definitionURL",
            "type": "Attribute",
        }
    )


@dataclass
class ListOfBlockDiagrams:
    """
    List of block diagrams.
    """
    class Meta:
        name = "listOfBlockDiagrams"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    block_diagram: List[BlockDiagram] = field(
        default_factory=list,
        metadata={
            "name": "blockDiagram",
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
        }
    )


@dataclass
class ReactionAnnotationType:
    """
    Annotation for reaction.
    """
    class Meta:
        name = "reactionAnnotationType"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    extension: Optional["ReactionAnnotationType.Extension"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )

    @dataclass
    class Extension:
        name: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            }
        )
        reaction_type: Optional[ReactionTypeValue] = field(
            default=None,
            metadata={
                "name": "reactionType",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        base_reactants: Optional[BaseReactants] = field(
            default=None,
            metadata={
                "name": "baseReactants",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        base_products: Optional[BaseProducts] = field(
            default=None,
            metadata={
                "name": "baseProducts",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        list_of_reactant_links: Optional[ListOfReactantLinks] = field(
            default=None,
            metadata={
                "name": "listOfReactantLinks",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            }
        )
        list_of_product_links: Optional[ListOfProductLinks] = field(
            default=None,
            metadata={
                "name": "listOfProductLinks",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            }
        )
        connect_scheme: Optional[ConnectScheme] = field(
            default=None,
            metadata={
                "name": "connectScheme",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        offset: Optional[Offset] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            }
        )
        edit_points: Optional[EditPoints] = field(
            default=None,
            metadata={
                "name": "editPoints",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            }
        )
        line: Optional[Line] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        list_of_modification: Optional[ListOfModification] = field(
            default=None,
            metadata={
                "name": "listOfModification",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            }
        )


@dataclass
class Apply(MathBase):
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    ci: List[Ci] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "sequential": True,
        }
    )
    csymbol: List[Csymbol] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "sequential": True,
        }
    )
    eq: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    neq: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    gt: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    lt: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    geq: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    leq: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    plus: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    minus: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    times: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    divide: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    power: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    root: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    degree: Optional["NodeContainer"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    abs: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    exp: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    ln: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    log: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    logbase: Optional["NodeContainer"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    floor: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    ceiling: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    factorial: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    and_value: Optional[MathBase] = field(
        default=None,
        metadata={
            "name": "and",
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    or_value: Optional[MathBase] = field(
        default=None,
        metadata={
            "name": "or",
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    xor: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    not_value: Optional[MathBase] = field(
        default=None,
        metadata={
            "name": "not",
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    sin: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    cos: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    tan: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    sec: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    csc: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    cot: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    sinh: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    cosh: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    tanh: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    sech: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    csch: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    coth: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    arcsin: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    arccos: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    arctan: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    arcsec: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    arccsc: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    arccot: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    arcsinh: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    arccosh: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    arctanh: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    arcsech: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    arccsch: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    arccoth: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    apply: List["Apply"] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    cn: List[Cn] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    true: List[MathBase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    false: List[MathBase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    notanumber: List[MathBase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    pi: List[MathBase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    infinity: List[MathBase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    exponentiale: List[MathBase] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    semantics: List[Semantics] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    piecewise: List[Piecewise] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )


@dataclass
class ModelAnnotationType:
    """
    Annotation for model.
    """
    class Meta:
        name = "modelAnnotationType"
        target_namespace = "http://www.sbml.org/2001/ns/celldesigner"

    extension: Optional["ModelAnnotationType.Extension"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            "required": True,
        }
    )

    @dataclass
    class Extension:
        model_version: Decimal = field(
            init=False,
            default=Decimal("4.0"),
            metadata={
                "name": "modelVersion",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
                "min_inclusive": Decimal("0.0"),
            }
        )
        model_display: Optional[ModelDisplay] = field(
            default=None,
            metadata={
                "name": "modelDisplay",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        list_of_included_species: Optional[ListOfIncludedSpecies] = field(
            default=None,
            metadata={
                "name": "listOfIncludedSpecies",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            }
        )
        list_of_compartment_aliases: Optional[ListOfCompartmentAliases] = field(
            default=None,
            metadata={
                "name": "listOfCompartmentAliases",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        list_of_complex_species_aliases: Optional[ListOfComplexSpeciesAliases] = field(
            default=None,
            metadata={
                "name": "listOfComplexSpeciesAliases",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        list_of_species_aliases: Optional[ListOfSpeciesAliases] = field(
            default=None,
            metadata={
                "name": "listOfSpeciesAliases",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        list_of_groups: Optional[ListOfGroups] = field(
            default=None,
            metadata={
                "name": "listOfGroups",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        list_of_proteins: Optional[ListOfProteins] = field(
            default=None,
            metadata={
                "name": "listOfProteins",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        list_of_genes: Optional[ListOfGenes] = field(
            default=None,
            metadata={
                "name": "listOfGenes",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        list_of_rnas: Optional[ListOfRnas] = field(
            default=None,
            metadata={
                "name": "listOfRNAs",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        list_of_antisense_rnas: Optional[ListOfAntisenseRnas] = field(
            default=None,
            metadata={
                "name": "listOfAntisenseRNAs",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
                "required": True,
            }
        )
        list_of_layers: Optional[ListOfLayers] = field(
            default=None,
            metadata={
                "name": "listOfLayers",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            }
        )
        list_of_block_diagrams: Optional[ListOfBlockDiagrams] = field(
            default=None,
            metadata={
                "name": "listOfBlockDiagrams",
                "type": "Element",
                "namespace": "http://www.sbml.org/2001/ns/celldesigner",
            }
        )


@dataclass
class Math1(MathBase):
    class Meta:
        name = "Math"
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    apply: Optional[Apply] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    cn: Optional[Cn] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    ci: Optional[Ci] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    csymbol: Optional[Csymbol] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    true: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    false: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    notanumber: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    pi: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    infinity: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    exponentiale: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    semantics: Optional[Semantics] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    piecewise: Optional[Piecewise] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    lambda_value: Optional[Lambda] = field(
        default=None,
        metadata={
            "name": "lambda",
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )


@dataclass
class NodeContainer(MathBase):
    class Meta:
        target_namespace = "http://www.w3.org/1998/Math/MathML"

    apply: Optional[Apply] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    cn: Optional[Cn] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    ci: Optional[Ci] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    csymbol: Optional[Csymbol] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    true: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    false: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    notanumber: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    pi: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    infinity: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    exponentiale: Optional[MathBase] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    semantics: Optional[Semantics] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )
    piecewise: Optional[Piecewise] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
        }
    )


@dataclass
class Math(Math1):
    class Meta:
        name = "math"
        namespace = "http://www.w3.org/1998/Math/MathML"


@dataclass
class EventAssignment(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    math: Optional[Math] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "required": True,
        }
    )
    variable: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class FunctionDefinition(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    math: Optional[Math] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "required": True,
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


@dataclass
class KineticLaw(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    math: Optional[Math] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "required": True,
        }
    )
    list_of_parameters: Optional[ListOfParameters] = field(
        default=None,
        metadata={
            "name": "listOfParameters",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    time_units: Optional[str] = field(
        default=None,
        metadata={
            "name": "timeUnits",
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    substance_units: Optional[str] = field(
        default=None,
        metadata={
            "name": "substanceUnits",
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class MathField(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    math: Optional[Math] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "required": True,
        }
    )


@dataclass
class Rule(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    math: Optional[Math] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "required": True,
        }
    )


@dataclass
class StoichiometryMath(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    math: Optional[Math] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.w3.org/1998/Math/MathML",
            "required": True,
        }
    )


@dataclass
class AlgebraicRule(Rule):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"


@dataclass
class AssignmentRule(Rule):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    variable: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class ListOfEventAssignments(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    event_assignment: List[EventAssignment] = field(
        default_factory=list,
        metadata={
            "name": "eventAssignment",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
            "min_occurs": 1,
        }
    )


@dataclass
class RateRule(Rule):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    variable: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class SpeciesReference(SimpleSpeciesReference):
    """
    Redefined speciesReference.
    """
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    stoichiometry_math: Optional[StoichiometryMath] = field(
        default=None,
        metadata={
            "name": "stoichiometryMath",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    stoichiometry: float = field(
        default=1.0,
        metadata={
            "type": "Attribute",
        }
    )
    annotation: Optional[SpeciesReferenceAnnotationType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )


@dataclass
class Event(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    trigger: Optional[MathField] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
            "required": True,
        }
    )
    delay: Optional[MathField] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    list_of_event_assignments: Optional[ListOfEventAssignments] = field(
        default=None,
        metadata={
            "name": "listOfEventAssignments",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
            "required": True,
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    time_units: Optional[str] = field(
        default=None,
        metadata={
            "name": "timeUnits",
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )


@dataclass
class ListOfSpeciesReferences(Sbase):
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    species_reference: List[SpeciesReference] = field(
        default_factory=list,
        metadata={
            "name": "speciesReference",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
            "min_occurs": 1,
        }
    )


@dataclass
class Reaction(Sbase):
    """
    Redefined reaction.
    """
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    list_of_reactants: Optional[ListOfSpeciesReferences] = field(
        default=None,
        metadata={
            "name": "listOfReactants",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    list_of_products: Optional[ListOfSpeciesReferences] = field(
        default=None,
        metadata={
            "name": "listOfProducts",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    list_of_modifiers: Optional[ListOfModifierSpeciesReferences] = field(
        default=None,
        metadata={
            "name": "listOfModifiers",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    kinetic_law: Optional[KineticLaw] = field(
        default=None,
        metadata={
            "name": "kineticLaw",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "required": True,
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    reversible: bool = field(
        default=True,
        metadata={
            "type": "Attribute",
        }
    )
    fast: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    annotation: Optional[ReactionAnnotationType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )


@dataclass
class Model(Sbase):
    """
    Redefined model.
    """
    class Meta:
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    list_of_function_definitions: Optional["Model.ListOfFunctionDefinitions"] = field(
        default=None,
        metadata={
            "name": "listOfFunctionDefinitions",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    list_of_unit_definitions: Optional["Model.ListOfUnitDefinitions"] = field(
        default=None,
        metadata={
            "name": "listOfUnitDefinitions",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    list_of_compartments: Optional["Model.ListOfCompartments"] = field(
        default=None,
        metadata={
            "name": "listOfCompartments",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    list_of_species: Optional["Model.ListOfSpecies"] = field(
        default=None,
        metadata={
            "name": "listOfSpecies",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    list_of_parameters: Optional["Model.ListOfParameters"] = field(
        default=None,
        metadata={
            "name": "listOfParameters",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    list_of_rules: Optional["Model.ListOfRules"] = field(
        default=None,
        metadata={
            "name": "listOfRules",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    list_of_reactions: Optional["Model.ListOfReactions"] = field(
        default=None,
        metadata={
            "name": "listOfReactions",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    list_of_events: Optional["Model.ListOfEvents"] = field(
        default=None,
        metadata={
            "name": "listOfEvents",
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )
    id: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"(_|[a-z]|[A-Z])(_|[a-z]|[A-Z]|[0-9])*",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    annotation: Optional[ModelAnnotationType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
        }
    )

    @dataclass
    class ListOfFunctionDefinitions(Sbase):
        function_definition: List[FunctionDefinition] = field(
            default_factory=list,
            metadata={
                "name": "functionDefinition",
                "type": "Element",
                "namespace": "http://www.sbml.org/sbml/level2/version4",
                "min_occurs": 1,
            }
        )

    @dataclass
    class ListOfUnitDefinitions(Sbase):
        unit_definition: List[UnitDefinition] = field(
            default_factory=list,
            metadata={
                "name": "unitDefinition",
                "type": "Element",
                "namespace": "http://www.sbml.org/sbml/level2/version4",
                "min_occurs": 1,
            }
        )

    @dataclass
    class ListOfCompartments(Sbase):
        compartment: List[Compartment] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://www.sbml.org/sbml/level2/version4",
                "min_occurs": 1,
            }
        )

    @dataclass
    class ListOfSpecies(Sbase):
        species: List[Species1] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://www.sbml.org/sbml/level2/version4",
                "min_occurs": 1,
            }
        )

    @dataclass
    class ListOfParameters(Sbase):
        parameter: List[Parameter] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://www.sbml.org/sbml/level2/version4",
                "min_occurs": 1,
            }
        )

    @dataclass
    class ListOfRules(Sbase):
        algebraic_rule: List[AlgebraicRule] = field(
            default_factory=list,
            metadata={
                "name": "algebraicRule",
                "type": "Element",
                "namespace": "http://www.sbml.org/sbml/level2/version4",
            }
        )
        assignment_rule: List[AssignmentRule] = field(
            default_factory=list,
            metadata={
                "name": "assignmentRule",
                "type": "Element",
                "namespace": "http://www.sbml.org/sbml/level2/version4",
            }
        )
        rate_rule: List[RateRule] = field(
            default_factory=list,
            metadata={
                "name": "rateRule",
                "type": "Element",
                "namespace": "http://www.sbml.org/sbml/level2/version4",
            }
        )

    @dataclass
    class ListOfReactions(Sbase):
        reaction: List[Reaction] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://www.sbml.org/sbml/level2/version4",
                "min_occurs": 1,
            }
        )

    @dataclass
    class ListOfEvents(Sbase):
        event: List[Event] = field(
            default_factory=list,
            metadata={
                "type": "Element",
                "namespace": "http://www.sbml.org/sbml/level2/version4",
                "min_occurs": 1,
            }
        )


@dataclass
class Sbml1(Sbase):
    class Meta:
        name = "Sbml"
        target_namespace = "http://www.sbml.org/sbml/level2/version4"

    model: Optional[Model] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.sbml.org/sbml/level2/version4",
            "required": True,
        }
    )
    level: int = field(
        init=False,
        default=2,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )
    version: int = field(
        init=False,
        default=1,
        metadata={
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class Sbml(Sbml1):
    class Meta:
        name = "sbml"
        namespace = "http://www.sbml.org/sbml/level2/version4"
