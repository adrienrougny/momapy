"""CellDesigner XML writing helper functions.

Encoding, coordinate inversions, reverse mappings, and XML element
construction used by the CellDesigner writer.
"""

import math
import re

import lxml.etree

from momapy.coloring import Color
from momapy.geometry import Point, Rotation, get_transformation_for_frame
from momapy.sbml.io.sbml._qualifiers import QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE
from momapy.celldesigner.io.celldesigner._reading_parsing import (
    _CD_NAMESPACE,
    _LINK_ANCHOR_POSITION_TO_ANCHOR_NAME,
    _TEXT_TO_CHARACTER,
)
from momapy.celldesigner.model import (
    AntisenseRNA,
    Catalyzer,
    Complex,
    Degraded,
    Dissociation,
    Drug,
    Gene,
    GenericProtein,
    HeterodimerAssociation,
    Inhibitor,
    Ion,
    IonChannel,
    KnownTransitionOmitted,
    Modulator,
    Phenotype,
    PhysicalStimulator,
    RNA,
    Receptor,
    SimpleMolecule,
    StateTransition,
    Transcription,
    Translation,
    Transport,
    Trigger,
    TruncatedProtein,
    Truncation,
    Unknown,
    UnknownCatalyzer,
    UnknownInhibitor,
    UnknownTransition,
)


def _are_collinear(p1, p2, p3, epsilon=1e-6):
    """Check if three points are collinear (Minerva compatibility).

    Args:
        p1: First point (maps to Minerva's pointA).
        p2: Second point (maps to Minerva's pointB).
        p3: Third point / origin (maps to Minerva's pointC).
        epsilon: Tolerance for the cross product test.

    Returns:
        True if the three points are collinear.
    """
    dx1 = p1.x - p3.x
    dy1 = p1.y - p3.y
    dx2 = p2.x - p3.x
    dy2 = p2.y - p3.y
    cross = dx1 * dy2 - dy1 * dx2
    return abs(cross) < epsilon


_SBML_SID_INVALID_CHAR_RE = re.compile(r"[^a-zA-Z0-9_]")
_XML_ID_INVALID_CHAR_RE = re.compile(r"[^a-zA-Z0-9_\-\.:]")
_XML_ID_INVALID_START_RE = re.compile(r"^[^a-zA-Z_:]")

_CD_NAMESPACE = _CD_NAMESPACE

# Reverse of _parsing._LINK_ANCHOR_POSITION_TO_ANCHOR_NAME
_ANCHOR_NAME_TO_LINK_ANCHOR_POSITION = {
    v: k for k, v in _LINK_ANCHOR_POSITION_TO_ANCHOR_NAME.items()
}

# Reverse of _parsing._TEXT_TO_CHARACTER (pick first occurrence as canonical)
_CHARACTER_TO_TEXT = {}
for (
    _text,
    _char,
) in _TEXT_TO_CHARACTER.items():
    if _char not in _CHARACTER_TO_TEXT:
        _CHARACTER_TO_TEXT[_char] = _text


_CLASS_TO_CD_STRING = {
    GenericProtein: "PROTEIN",
    TruncatedProtein: "PROTEIN",
    Receptor: "PROTEIN",
    IonChannel: "PROTEIN",
    Gene: "GENE",
    RNA: "RNA",
    AntisenseRNA: "ANTISENSE_RNA",
    SimpleMolecule: "SIMPLE_MOLECULE",
    Ion: "ION",
    Drug: "DRUG",
    Phenotype: "PHENOTYPE",
    Unknown: "UNKNOWN",
    Degraded: "DEGRADED",
    Complex: "COMPLEX",
}

_CLASS_TO_REACTION_TYPE = {
    StateTransition: "STATE_TRANSITION",
    KnownTransitionOmitted: "KNOWN_TRANSITION_OMITTED",
    UnknownTransition: "UNKNOWN_TRANSITION",
    Transcription: "TRANSCRIPTION",
    Translation: "TRANSLATION",
    Transport: "TRANSPORT",
    HeterodimerAssociation: "HETERODIMER_ASSOCIATION",
    Dissociation: "DISSOCIATION",
    Truncation: "TRUNCATION",
}

_CLASS_TO_MODIFIER_TYPE = {
    Catalyzer: "CATALYSIS",
    UnknownCatalyzer: "UNKNOWN_CATALYSIS",
    Inhibitor: "INHIBITION",
    UnknownInhibitor: "UNKNOWN_INHIBITION",
    PhysicalStimulator: "PHYSICAL_STIMULATION",
    Modulator: "MODULATION",
    Trigger: "TRIGGER",
}

_MODIFICATION_STATE_TO_CD = {
    "PHOSPHORYLATED": "phosphorylated",
    "UBIQUITINATED": "ubiquitinated",
    "ACETYLATED": "acetylated",
    "METHYLATED": "methylated",
    "HYDROXYLATED": "hydroxylated",
    "GLYCOSYLATED": "glycosylated",
    "MYRISTOYLATED": "myristoylated",
    "PALMITOYLATED": "palmitoylated",
    "PRENYLATED": "prenylated",
    "PROTONATED": "protonated",
    "SUMOYLATED": "sumoylated",
    "DON_T_CARE": "don't care",
    "UNKNOWN": "unknown",
    "none": "empty",
}


def get_cd_species_id(species):
    """Get the CellDesigner XML species ID.

    The reader appends ``_active`` suffix(es) to IDs for active species
    aliases.  This function strips all such trailing suffixes so the
    written ID matches the original CellDesigner XML.

    Args:
        species: A species model element, or None.

    Returns:
        The species ID as it should appear in CellDesigner XML.
    """
    if species is None:
        return ""
    id_str = species.id_ or ""
    while id_str.endswith("_active"):
        id_str = id_str[: -len("_active")]
    return ensure_sbml_sid(id_str)


def ensure_sbml_sid(id_str):
    """Ensure a string conforms to SBML SId syntax.

    SBML Level 2 Version 4 SId: ``[a-zA-Z_][a-zA-Z0-9_]*``.
    Invalid characters are replaced with underscores, and a leading
    digit is prefixed with an underscore.

    Args:
        id_str: The raw ID string.

    Returns:
        A valid SId string, or empty string if input is None or empty.
    """
    if not id_str:
        return ""
    result = _SBML_SID_INVALID_CHAR_RE.sub("_", id_str)
    if result[0].isdigit():
        result = "_" + result
    return result


def ensure_xml_id(id_str):
    """Ensure a string conforms to XML ID syntax.

    XML 1.0 ID: starts with a letter, underscore, or colon, then
    allows letters, digits, hyphens, underscores, periods, and colons.
    Invalid characters are replaced with underscores, and a leading
    invalid character is prefixed with an underscore.

    Args:
        id_str: The raw ID string.

    Returns:
        A valid XML ID string, or empty string if input is None or empty.
    """
    if not id_str:
        return ""
    result = _XML_ID_INVALID_CHAR_RE.sub("_", id_str)
    if _XML_ID_INVALID_START_RE.match(result):
        result = "_" + result
    return result


def encode_name(name):
    """Reverse of _parsing.make_name(): replace special chars with CD tokens.

    Args:
        name: Human-readable name string.

    Returns:
        CellDesigner-encoded name string, or None if name is None.
    """
    if name is None:
        return name
    for char, text in _CHARACTER_TO_TEXT.items():
        name = name.replace(char, text)
    return name


def color_to_cd_hex(color):
    """Convert momapy Color (RRGGBBAA) to CellDesigner hex (AARRGGBB).

    Args:
        color: A Color instance.

    Returns:
        CellDesigner AARRGGBB hex string (e.g. "FFCC0000").
    """
    hexa = color.to_hexa().lstrip("#").lower()
    # hexa is RRGGBBAA, CellDesigner expects AARRGGBB
    return hexa[-2:] + hexa[:-2]


def node_to_bounds_attrs(node):
    """Extract CellDesigner bounds attributes from a layout node.

    Args:
        node: A layout element with position, width, height.

    Returns:
        Dict with "x", "y", "w", "h" string attributes.
    """
    return {
        "x": str(node.position.x - node.width / 2),
        "y": str(node.position.y - node.height / 2),
        "w": str(node.width),
        "h": str(node.height),
    }


def points_to_edit_points_text(points):
    """Format a list of Points as CellDesigner edit points text.

    Args:
        points: List of Point.

    Returns:
        Space-separated "x,y" pairs, e.g. "0.5,0.3 0.7,-0.1".
    """
    return " ".join(f"{p.x},{p.y}" for p in points)


_ALL_ANCHOR_NAMES = list(_LINK_ANCHOR_POSITION_TO_ANCHOR_NAME.values())


def infer_anchor_name(species_layout, point, tol=1e-3):
    """Try all 16 named anchors; return closest if within tolerance, else 'center'.

    Args:
        species_layout: A layout element with anchor_point() method.
        point: The Point to match.
        tol: Absolute tolerance for coordinate matching.

    Returns:
        Anchor name string (e.g. "north", "south_east", or "center").
    """
    for anchor_name in _ALL_ANCHOR_NAMES:
        anchor_point = species_layout.anchor_point(anchor_name)
        if math.isclose(anchor_point.x, point.x, abs_tol=tol) and math.isclose(
            anchor_point.y, point.y, abs_tol=tol
        ):
            return anchor_name
    return "center"


def compute_cd_angle(modification_position, species_layout):
    """Compute the CellDesigner angle for a modification residue position.

    Reverses the forward transform in _layout.make_species_modification:
    cd_angle -> Point(W*cos, H*sin) -> atan2 -> own_angle -> position.

    The y-axis is negated because screen coordinates (y-down) differ from
    the math convention (y-up) used in own_angle. The result is normalized
    to [0, 2*pi) to match CellDesigner's angle convention.

    Args:
        modification_position: The position of the modification layout.
        species_layout: The parent species layout element.

    Returns:
        The CellDesigner angle as a float (radians), in [0, 2*pi).
    """
    center = species_layout.center()
    delta_x = modification_position.x - center.x
    delta_y = -(modification_position.y - center.y)
    if abs(delta_x) < 1e-10 and abs(delta_y) < 1e-10:
        return 0.0
    intermediate_angle = math.atan2(delta_y, delta_x)
    width = species_layout.width
    height = species_layout.height
    cd_angle = math.atan2(
        width * math.sin(intermediate_angle),
        height * math.cos(intermediate_angle),
    )
    if cd_angle < 0.0:
        cd_angle += 2 * math.pi
    return cd_angle + 0.0  # normalize -0.0 to 0.0


def _build_frame_and_inverse(origin, unit_x, unit_y):
    """Build a coordinate frame and return its inverse transformation.

    Args:
        origin: Origin point.
        unit_x: Unit x-axis point.
        unit_y: Unit y-axis point.

    Returns:
        The inverse MatrixTransformation.
    """
    transformation = get_transformation_for_frame(origin, unit_x, unit_y)
    return transformation.inverted()


def _perp_point(origin, unit_x):
    """Compute the perpendicular (90 degree rotation) of unit_x around origin.

    Args:
        origin: Rotation center.
        unit_x: Point to rotate.

    Returns:
        Rotated point.
    """
    return unit_x.transformed(Rotation(math.radians(90), origin))


def inverse_edit_points_non_t_shape(reaction_layout, reactant_layout, product_layout):
    """Compute frame-space edit points for a non-T-shape (1->1) reaction.

    Mirrors make_segments_non_t_shape in _layout.py but runs the inverse
    transformation.

    Args:
        reaction_layout: The reaction layout element with segments.
        reactant_layout: The base reactant species layout.
        product_layout: The base product species layout.

    Returns:
        Tuple of (edit_points, reactant_anchor_name, product_anchor_name,
        rectangle_index).
    """
    points = reaction_layout.points()
    start_point = points[0]
    end_point = points[-1]
    intermediate_points = points[1:-1]
    reactant_anchor_name = infer_anchor_name(reactant_layout, start_point)
    product_anchor_name = infer_anchor_name(product_layout, end_point)
    origin = reactant_layout.anchor_point(reactant_anchor_name)
    unit_x = product_layout.anchor_point(product_anchor_name)
    unit_y = _perp_point(origin, unit_x)
    inverse = _build_frame_and_inverse(origin, unit_x, unit_y)
    edit_points = [p.transformed(inverse) for p in intermediate_points]
    rectangle_index = reaction_layout.reaction_node_segment
    return edit_points, reactant_anchor_name, product_anchor_name, rectangle_index


def inverse_edit_points_left_t_shape(
    reaction_layout,
    reactant_layouts,
    product_layout,
    base_reactant_consumption_layouts,
):
    """Compute frame-space edit points for a left-T-shape (2+->1) reaction.

    Args:
        reaction_layout: The reaction layout element with segments.
        reactant_layouts: List of base reactant species layouts (len >= 2).
        product_layout: The base product species layout.
        base_reactant_consumption_layouts: List of consumption layouts for the
            base reactants.

    Returns:
        Tuple of (all_edit_points_text, num0, num1, num2, t_shape_index,
        product_anchor_name, reactant_anchor_names).
    """
    reactant_layout_0 = reactant_layouts[0]
    reactant_layout_1 = reactant_layouts[1]
    # Frame 1: used to encode the T-junction position
    origin_f1 = reactant_layout_0.center()
    unit_x_f1 = reactant_layout_1.center()
    unit_y_f1 = product_layout.center()
    if _are_collinear(unit_x_f1, unit_y_f1, origin_f1):
        origin_f1 = Point(origin_f1.x + 1, origin_f1.y + 1)
    inverse_f1 = _build_frame_and_inverse(origin_f1, unit_x_f1, unit_y_f1)
    # The T-junction is the start point of the main reaction path
    t_junction = reaction_layout.points()[0]
    t_junction_in_frame = t_junction.transformed(inverse_f1)
    # Frame 2: main path from T-junction to product
    product_anchor_name = infer_anchor_name(
        product_layout, reaction_layout.points()[-1]
    )
    origin_f2 = t_junction
    unit_x_f2 = product_layout.anchor_point(product_anchor_name)
    unit_y_f2 = _perp_point(origin_f2, unit_x_f2)
    inverse_f2 = _build_frame_and_inverse(origin_f2, unit_x_f2, unit_y_f2)
    # Main path intermediate points (excluding start and end)
    main_points = reaction_layout.points()
    main_intermediate = main_points[1:-1]
    main_edit_points = [p.transformed(inverse_f2) for p in main_intermediate]
    num2 = len(main_edit_points)
    # Branch edit points for each base reactant
    branch_edit_points_list = []
    reactant_anchor_names = []
    for i, (reactant_layout, consumption_layout) in enumerate(
        zip(reactant_layouts, base_reactant_consumption_layouts)
    ):
        reactant_anchor_name = infer_anchor_name(
            reactant_layout, consumption_layout.points()[0]
        )
        reactant_anchor_names.append(reactant_anchor_name)
        branch_origin = t_junction
        branch_unit_x = reactant_layout.anchor_point(reactant_anchor_name)
        branch_unit_y = _perp_point(branch_origin, branch_unit_x)
        branch_inverse = _build_frame_and_inverse(
            branch_origin, branch_unit_x, branch_unit_y
        )
        # Branch intermediate points (consumption layouts go from species
        # to T-junction, so we reverse and strip endpoints)
        branch_points = consumption_layout.points()
        # The consumption layout goes: species_border -> ... -> reaction_border
        # We need the intermediate points in the direction species -> t_junction
        branch_intermediate = branch_points[1:-1]
        # Reverse since consumption is species->reaction but the frame is
        # t_junction->species
        branch_intermediate = list(reversed(branch_intermediate))
        branch_edit = [p.transformed(branch_inverse) for p in branch_intermediate]
        branch_edit_points_list.append(branch_edit)
    num0 = len(branch_edit_points_list[0]) if len(branch_edit_points_list) > 0 else 0
    num1 = len(branch_edit_points_list[1]) if len(branch_edit_points_list) > 1 else 0
    # Concatenate: branch0 + branch1 + main + t_junction
    all_edit_points = []
    for branch_edit in branch_edit_points_list:
        all_edit_points.extend(branch_edit)
    all_edit_points.extend(main_edit_points)
    all_edit_points.append(t_junction_in_frame)
    t_shape_index = reaction_layout.reaction_node_segment
    return (
        all_edit_points,
        num0,
        num1,
        num2,
        t_shape_index,
        product_anchor_name,
        reactant_anchor_names,
    )


def inverse_edit_points_right_t_shape(
    reaction_layout,
    reactant_layout,
    product_layouts,
    base_product_production_layouts,
):
    """Compute frame-space edit points for a right-T-shape (1->2+) reaction.

    Args:
        reaction_layout: The reaction layout element with segments.
        reactant_layout: The base reactant species layout.
        product_layouts: List of base product species layouts (len >= 2).
        base_product_production_layouts: List of production layouts for the
            base products.

    Returns:
        Tuple of (all_edit_points_text, num0, num1, num2, t_shape_index,
        reactant_anchor_name, product_anchor_names).
    """
    product_layout_0 = product_layouts[0]
    product_layout_1 = product_layouts[1]
    # Frame 1: used to encode the T-junction position
    origin_f1 = reactant_layout.center()
    unit_x_f1 = product_layout_0.center()
    unit_y_f1 = product_layout_1.center()
    if _are_collinear(unit_x_f1, unit_y_f1, origin_f1):
        origin_f1 = Point(origin_f1.x + 1, origin_f1.y + 1)
    inverse_f1 = _build_frame_and_inverse(origin_f1, unit_x_f1, unit_y_f1)
    # The T-junction is the end point of the main reaction path
    t_junction = reaction_layout.points()[-1]
    t_junction_in_frame = t_junction.transformed(inverse_f1)
    # Frame 2: main path from reactant to T-junction
    reactant_anchor_name = infer_anchor_name(
        reactant_layout, reaction_layout.points()[0]
    )
    origin_f2 = t_junction
    unit_x_f2 = reactant_layout.anchor_point(reactant_anchor_name)
    unit_y_f2 = _perp_point(origin_f2, unit_x_f2)
    inverse_f2 = _build_frame_and_inverse(origin_f2, unit_x_f2, unit_y_f2)
    # Main path intermediate points in reversed order (excluding start and end)
    main_points = reaction_layout.points()
    main_intermediate = main_points[1:-1]
    main_intermediate_reversed = list(reversed(main_intermediate))
    main_edit_points = [p.transformed(inverse_f2) for p in main_intermediate_reversed]
    # num0 for right T-shape corresponds to main path points
    num0 = len(main_edit_points)
    # Branch edit points for each base product
    branch_edit_points_list = []
    product_anchor_names = []
    for i, (product_layout_elem, production_layout) in enumerate(
        zip(product_layouts, base_product_production_layouts)
    ):
        product_anchor_name = infer_anchor_name(
            product_layout_elem, production_layout.points()[-1]
        )
        product_anchor_names.append(product_anchor_name)
        branch_origin = t_junction
        branch_unit_x = product_layout_elem.anchor_point(product_anchor_name)
        branch_unit_y = _perp_point(branch_origin, branch_unit_x)
        branch_inverse = _build_frame_and_inverse(
            branch_origin, branch_unit_x, branch_unit_y
        )
        branch_points = production_layout.points()
        branch_intermediate = branch_points[1:-1]
        branch_edit = [p.transformed(branch_inverse) for p in branch_intermediate]
        branch_edit_points_list.append(branch_edit)
    num1 = len(branch_edit_points_list[0]) if len(branch_edit_points_list) > 0 else 0
    num2 = len(branch_edit_points_list[1]) if len(branch_edit_points_list) > 1 else 0
    # Concatenate: main + branch0 + branch1 + t_junction
    all_edit_points = []
    all_edit_points.extend(main_edit_points)
    for branch_edit in branch_edit_points_list:
        all_edit_points.extend(branch_edit)
    all_edit_points.append(t_junction_in_frame)
    # t_shape_index for right T-shape: reader computes
    # len(segments) - 1 - t_shape_index_from_xml
    # so we need: t_shape_index_from_xml = len(segments) - 1 - reaction_node_segment
    n_segments = len(reaction_layout.segments)
    t_shape_index = n_segments - 1 - reaction_layout.reaction_node_segment
    return (
        all_edit_points,
        num0,
        num1,
        num2,
        t_shape_index,
        reactant_anchor_name,
        product_anchor_names,
    )


def inverse_edit_points_modifier(
    modifier_layout, source_layout, reaction_layout, has_boolean_input
):
    """Compute frame-space edit points for a modifier arc.

    Uses the arc's endpoint on the reaction side as the coordinate
    frame basis (unit_x), matching the reader's use of the target
    anchor point.  Falls back to the reaction node center when the
    endpoint equals the reaction node position (no targetLineIndex
    offset).

    Args:
        modifier_layout: The modifier layout element with segments.
        source_layout: The source species or gate layout.
        reaction_layout: The parent reaction layout.
        has_boolean_input: Whether the modifier has boolean gate input.

    Returns:
        Tuple of (edit_points, source_anchor_name).
    """
    points = modifier_layout.points()
    intermediate_points = points[1:-1]
    if has_boolean_input:
        source_anchor_name = "center"
    else:
        source_anchor_name = infer_anchor_name(source_layout, points[0])
    origin = source_layout.anchor_point(source_anchor_name)
    target_point = points[-1]
    unit_x = target_point
    unit_y = _perp_point(origin, unit_x)
    inverse = _build_frame_and_inverse(origin, unit_x, unit_y)
    edit_points = [p.transformed(inverse) for p in intermediate_points]
    return edit_points, source_anchor_name


def inverse_edit_points_reactant_link(
    reactant_link_layout, species_layout, reaction_layout
):
    """Compute frame-space edit points for a reactant link.

    Args:
        reactant_link_layout: The consumption layout for the link.
        species_layout: The species layout for the reactant.
        reaction_layout: The parent reaction layout.

    Returns:
        Tuple of (edit_points, anchor_name).
    """
    points = reactant_link_layout.points()
    anchor_name = infer_anchor_name(species_layout, points[0])
    if anchor_name == "center":
        origin = species_layout.center()
    else:
        origin = species_layout.anchor_point(anchor_name)
    unit_x = reaction_layout.left_connector_tip()
    unit_y = _perp_point(origin, unit_x)
    inverse = _build_frame_and_inverse(origin, unit_x, unit_y)
    intermediate_points = points[1:-1]
    edit_points = [p.transformed(inverse) for p in intermediate_points]
    return edit_points, anchor_name


def inverse_edit_points_product_link(
    product_link_layout, species_layout, reaction_layout
):
    """Compute frame-space edit points for a product link.

    Args:
        product_link_layout: The production layout for the link.
        species_layout: The species layout for the product.
        reaction_layout: The parent reaction layout.

    Returns:
        Tuple of (edit_points, anchor_name).
    """
    points = product_link_layout.points()
    anchor_name = infer_anchor_name(species_layout, points[-1])
    origin = reaction_layout.right_connector_tip()
    if anchor_name == "center":
        unit_x = species_layout.center()
    else:
        unit_x = species_layout.anchor_point(anchor_name)
    unit_y = _perp_point(origin, unit_x)
    inverse = _build_frame_and_inverse(origin, unit_x, unit_y)
    intermediate_points = points[1:-1]
    edit_points = [p.transformed(inverse) for p in intermediate_points]
    return edit_points, anchor_name


def inverse_edit_points_reactant_from_base(
    consumption_layout, species_layout, reaction_layout, reactant_anchor_name
):
    """Compute frame-space edit points for a base reactant in T-shape.

    Args:
        consumption_layout: The consumption layout.
        species_layout: The species layout.
        reaction_layout: The parent reaction layout.
        reactant_anchor_name: Pre-computed anchor name.

    Returns:
        List of frame-space edit points.
    """
    origin = reaction_layout.points()[0]
    unit_x = species_layout.anchor_point(reactant_anchor_name)
    unit_y = _perp_point(origin, unit_x)
    inverse = _build_frame_and_inverse(origin, unit_x, unit_y)
    points = consumption_layout.points()
    intermediate_points = list(reversed(points[1:-1]))
    edit_points = [p.transformed(inverse) for p in intermediate_points]
    return edit_points


def inverse_edit_points_product_from_base(
    production_layout, species_layout, reaction_layout, product_anchor_name
):
    """Compute frame-space edit points for a base product in T-shape.

    Args:
        production_layout: The production layout.
        species_layout: The species layout.
        reaction_layout: The parent reaction layout.
        product_anchor_name: Pre-computed anchor name.

    Returns:
        List of frame-space edit points.
    """
    origin = reaction_layout.points()[-1]
    unit_x = species_layout.anchor_point(product_anchor_name)
    unit_y = _perp_point(origin, unit_x)
    inverse = _build_frame_and_inverse(origin, unit_x, unit_y)
    points = production_layout.points()
    intermediate_points = points[1:-1]
    edit_points = [p.transformed(inverse) for p in intermediate_points]
    return edit_points


def inverse_edit_points_modulation(
    modulation_layout, source_layout, target_layout, has_boolean_input
):
    """Compute frame-space edit points for a modulation (false reaction).

    Args:
        modulation_layout: The modulation layout element with segments.
        source_layout: The source species or gate layout.
        target_layout: The target species layout.
        has_boolean_input: Whether the modulation has boolean gate input.

    Returns:
        Tuple of (edit_points, source_anchor_name, target_anchor_name).
    """
    points = modulation_layout.points()
    intermediate_points = points[1:-1]
    if has_boolean_input:
        source_anchor_name = "center"
    else:
        source_anchor_name = infer_anchor_name(source_layout, points[0])
    target_anchor_name = infer_anchor_name(target_layout, points[-1])
    origin = source_layout.anchor_point(source_anchor_name)
    unit_x = target_layout.anchor_point(target_anchor_name)
    unit_y = _perp_point(origin, unit_x)
    inverse = _build_frame_and_inverse(origin, unit_x, unit_y)
    edit_points = [p.transformed(inverse) for p in intermediate_points]
    return edit_points, source_anchor_name, target_anchor_name


def make_cd_element(tag, ns=None, attributes=None, text=None):
    """Create an lxml Element with optional namespace, attributes, and text.

    Args:
        tag: Element tag name.
        ns: Optional namespace URI. If given, tag becomes {ns}tag.
        attributes: Optional dict of attribute name/value pairs.
        text: Optional text content.

    Returns:
        lxml.etree.Element instance.
    """
    if ns is not None:
        full_tag = f"{{{ns}}}{tag}"
    else:
        full_tag = tag
    if attributes is None:
        attributes = {}
    element = lxml.etree.Element(full_tag, **attributes)
    if text is not None:
        element.text = text
    return element


# ---------------------------------------------------------------------------
# RDF annotation helpers
# ---------------------------------------------------------------------------

_RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
_XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"

_RDF_NSMAP = {
    "rdf": _RDF_NAMESPACE,
    "bqbiol": "http://biomodels.net/biology-qualifiers/",
    "bqmodel": "http://biomodels.net/model-qualifiers/",
}


def make_rdf_annotation(annotations, about_id):
    """Build an ``<rdf:RDF>`` element holding BioModels.net annotations.

    Args:
        annotations: Iterable of ``momapy.sbml.model.RDFAnnotation``.
        about_id: The id referenced by
            ``<rdf:Description rdf:about="#...">``.

    Returns:
        An lxml element, or ``None`` if ``annotations`` is empty.
    """
    annotations = list(annotations)
    if not annotations:
        return None
    rdf_element = lxml.etree.Element(f"{{{_RDF_NAMESPACE}}}RDF", nsmap=_RDF_NSMAP)
    description = lxml.etree.SubElement(
        rdf_element,
        f"{{{_RDF_NAMESPACE}}}Description",
        attrib={f"{{{_RDF_NAMESPACE}}}about": f"#{about_id}"},
    )
    sorted_annotations = sorted(
        annotations,
        key=lambda annotation: (
            annotation.qualifier.__class__.__name__,
            annotation.qualifier.name,
            sorted(annotation.resources),
        ),
    )
    for annotation in sorted_annotations:
        qualifier_namespace, qualifier_tag = QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE[
            annotation.qualifier
        ]
        bq_element = lxml.etree.SubElement(
            description, f"{{{qualifier_namespace}}}{qualifier_tag}"
        )
        bag_element = lxml.etree.SubElement(bq_element, f"{{{_RDF_NAMESPACE}}}Bag")
        for resource in sorted(annotation.resources):
            lxml.etree.SubElement(
                bag_element,
                f"{{{_RDF_NAMESPACE}}}li",
                attrib={f"{{{_RDF_NAMESPACE}}}resource": resource},
            )
    return rdf_element


def inject_rdf_into_celldesigner_notes(notes_element, rdf_element):
    """Append an ``<rdf:RDF>`` element into the ``<body>`` of a CellDesigner notes.

    CellDesigner embeds RDF annotations for included species (subunits)
    inside the ``<html>/<body>`` of their ``<celldesigner:notes>`` element,
    alongside human-readable text. This helper ensures the scaffold exists
    and appends ``rdf_element`` as a child of the ``<body>``.

    Args:
        notes_element: The ``<celldesigner:notes>`` element.
        rdf_element: The ``<rdf:RDF>`` element to inject.
    """
    html = notes_element.find(f"{{{_XHTML_NAMESPACE}}}html")
    if html is None:
        html = lxml.etree.SubElement(notes_element, f"{{{_XHTML_NAMESPACE}}}html")
    body = html.find(f"{{{_XHTML_NAMESPACE}}}body")
    if body is None:
        body = lxml.etree.SubElement(html, f"{{{_XHTML_NAMESPACE}}}body")
    body.append(rdf_element)
