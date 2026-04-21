"""Utility functions for CellDesigner map manipulation.

This module provides helper functions for adjusting and tidying
CellDesigner maps, including fitting compartments, complexes, and nodes
to their content, adjusting arc endpoints, and highlighting layout elements.
"""

import collections
import collections.abc
import math

import momapy.builder
import momapy.celldesigner.core
import momapy.celldesigner.io.celldesigner._reading_parsing
import momapy.core.elements
import momapy.core.layout
import momapy.geometry
import momapy.positioning
import momapy.styling
import momapy.coloring
import momapy.drawing


_ALL_ANCHOR_NAMES = list(
    momapy.celldesigner.io.celldesigner._reading_parsing._LINK_ANCHOR_POSITION_TO_ANCHOR_NAME.values()
)


def _closest_anchor_point(
    node: momapy.core.elements.LayoutElement | momapy.builder.Builder,
    point: momapy.geometry.Point,
) -> momapy.geometry.Point:
    """Find the named anchor point on a node closest to a given point.

    Iterates over the 16 compass anchor positions and returns the one
    with the smallest Euclidean distance to ``point``.

    Args:
        node: The layout element whose anchors are considered.
        point: The reference point to find the closest anchor to.

    Returns:
        The anchor point closest to ``point``.
    """
    if isinstance(node, momapy.builder.Builder):
        frozen_node = momapy.builder.object_from_builder(node)
    else:
        frozen_node = node
    best_point = None
    best_distance_squared = float("inf")
    for anchor_name in _ALL_ANCHOR_NAMES:
        anchor_point = frozen_node.anchor_point(anchor_name)
        distance_squared = (anchor_point.x - point.x) ** 2 + (
            anchor_point.y - point.y
        ) ** 2
        if distance_squared < best_distance_squared:
            best_distance_squared = distance_squared
            best_point = anchor_point
    return best_point


def highlight_layout_elements(
    map_: momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder,
    layout_elements: collections.abc.Iterable[
        momapy.core.elements.LayoutElement | momapy.builder.Builder
    ],
) -> momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder:
    """Highlight specific layout elements by graying out all others.

    Applies a stylesheet that dims all layout elements except the
    specified ones and their descendants, making the selected elements
    visually prominent.

    Args:
        map_: A CellDesigner map or map builder. If a builder is given,
            it is modified in place.
        layout_elements: Layout elements to highlight.

    Returns:
        The modified map or map builder. If a frozen map was given,
            a new map is returned.
    """
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    all_layout_elements = []
    for layout_element in layout_elements:
        all_layout_elements.append(layout_element)
        all_layout_elements += layout_element.descendants()
    id_selectors = [
        momapy.styling.IdSelector(layout_element.id_)
        for layout_element in all_layout_elements
    ]
    not_selector = momapy.styling.NotSelector(tuple(id_selectors))
    layout_element_selector = momapy.styling.CompoundSelector(
        tuple([momapy.styling.ClassSelector("LayoutElement"), not_selector])
    )
    text_layout_selector = momapy.styling.CompoundSelector(
        tuple([momapy.styling.TypeSelector("TextLayout"), not_selector])
    )
    production_layout_selector = momapy.styling.CompoundSelector(
        tuple([momapy.styling.TypeSelector("ProductionLayout"), not_selector])
    )
    compartment_layout_selector = momapy.styling.CompoundSelector(
        tuple(
            [
                momapy.styling.OrSelector(
                    tuple(
                        [
                            momapy.styling.TypeSelector(class_name)
                            for class_name in [
                                "RectangleCompartmentLayout",
                                "OvalCompartmentLayout",
                                "CornerCompartmentLayout",
                                "LineCompartmentLayout",
                            ]
                        ]
                    )
                ),
                not_selector,
            ]
        )
    )
    reaction_layout_selector = momapy.styling.CompoundSelector(
        tuple(
            [
                momapy.styling.OrSelector(
                    tuple(
                        [
                            momapy.styling.TypeSelector(class_name)
                            for class_name in [
                                "StateTransitionLayout",
                                "HeterodimerAssociationLayout",
                                "KnownTransitionOmittedLayout",
                                "UnknownTransitionLayout",
                                "TransportLayout",
                                "TranslationLayout",
                                "TranscriptionLayout",
                            ]
                        ]
                    )
                ),
                not_selector,
            ]
        )
    )
    style_sheet = momapy.styling.StyleSheet(
        {
            layout_element_selector: momapy.styling.StyleCollection(
                {
                    "stroke": None,
                    "fill": momapy.coloring.white,
                    "path_stroke": None,
                    "end_arrowhead_stroke": None,
                    "start_arrowhead_stroke": None,
                    "arrowhead_stroke": None,
                    "reaction_node_stroke": None,
                    "active_stroke": None,
                    "inner_stroke": None,
                    "group_stroke": momapy.coloring.lightgray,
                }
            ),
            text_layout_selector: momapy.styling.StyleCollection(
                {
                    "stroke": momapy.drawing.NoneValue,
                    "fill": momapy.coloring.lightgray,
                }
            ),
            production_layout_selector: momapy.styling.StyleCollection(
                {
                    "arrowhead_stroke": momapy.coloring.lightgray,
                    "arrowhead_fill": momapy.coloring.lightgray,
                }
            ),
            compartment_layout_selector: momapy.styling.StyleCollection(
                {
                    "fill": momapy.coloring.lightgray,
                }
            ),
            reaction_layout_selector: momapy.styling.StyleCollection(
                {
                    "end_arrowhead_stroke": momapy.coloring.lightgray,
                    "end_arrowhead_fill": momapy.coloring.lightgray,
                    "start_arrowhead_stroke": momapy.coloring.lightgray,
                    "start_arrowhead_fill": momapy.coloring.lightgray,
                    "_font_fill": momapy.coloring.lightgray,
                }
            ),
        }
    )
    map_builder.layout = momapy.styling.apply_style_sheet(
        map_builder.layout, style_sheet, strict=False
    )
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def set_layout_to_fit_content(
    map_: momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder,
    xsep: float = 0,
    ysep: float = 0,
) -> momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder:
    """Resize layout to fit all elements.

    Adjusts the layout dimensions to contain all layout elements.

    Args:
        map_: A CellDesigner map or map builder. If a builder is given,
            it is modified in place.
        xsep: Horizontal separation padding. Defaults to 0.
        ysep: Vertical separation padding. Defaults to 0.

    Returns:
        The modified map or map builder. If a frozen map was given,
            a new map is returned.
    """
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    momapy.positioning.set_fit(
        map_builder.layout, map_builder.layout.layout_elements, xsep, ysep
    )
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def _update_active_layout(layout_element):
    """Update the active layout child to match the parent's size.

    If ``layout_element`` has a child whose class name ends with
    ``ActiveLayout``, that child's width, height, and position are
    updated to wrap the parent with the standard active border offset.

    Args:
        layout_element: The layout element whose active child should
            be updated.
    """
    if not hasattr(layout_element, "layout_elements"):
        return
    for child in layout_element.layout_elements:
        if type(child).__name__.endswith("ActiveLayout") or (
            hasattr(child, "_cls_to_build")
            and child._cls_to_build.__name__.endswith("ActiveLayout")
        ):
            child.width = (
                layout_element.width + 2 * momapy.celldesigner.core._ACTIVE_XSEP
            )
            child.height = (
                layout_element.height + 2 * momapy.celldesigner.core._ACTIVE_YSEP
            )
            child.position = layout_element.position
            break


def set_nodes_to_fit_labels(
    map_: momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder,
    xsep: float = 0,
    ysep: float = 0,
    omit_width: bool = False,
    omit_height: bool = False,
    restrict_to: collections.abc.Sequence[type] | None = None,
    exclude: collections.abc.Sequence[type] | None = None,
) -> momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder:
    """Resize nodes to fit their labels.

    Adjusts node dimensions to accommodate label text.

    Args:
        map_: A CellDesigner map or map builder. If a builder is given,
            it is modified in place.
        xsep: Horizontal separation padding. Defaults to 0.
        ysep: Vertical separation padding. Defaults to 0.
        omit_width: If True, do not adjust width. Defaults to False.
        omit_height: If True, do not adjust height. Defaults to False.
        restrict_to: Node types to include. Defaults to all nodes.
        exclude: Node types to exclude. Defaults to none.

    Returns:
        The modified map or map builder. If a frozen map was given,
            a new map is returned.
    """
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    if restrict_to is None:
        restrict_to = []
    if not restrict_to:
        restrict_to = [momapy.core.layout.Node]
    if exclude is None:
        exclude = []
    exclude = tuple(exclude)
    restrict_to = tuple(restrict_to)
    if omit_width and omit_height:
        return map_builder
    for layout_element in map_builder.layout.descendants():
        if (
            momapy.builder.isinstance_or_builder(layout_element, restrict_to)
            and not momapy.builder.isinstance_or_builder(layout_element, exclude)
            and hasattr(layout_element, "label")
            and layout_element.label is not None
        ):
            bbox = momapy.positioning.fit([layout_element.label.bbox()], xsep, ysep)
            if not omit_width:
                if bbox.width > layout_element.width:
                    layout_element.width = bbox.width
            if not omit_height:
                if bbox.height > layout_element.height:
                    layout_element.height = bbox.height
            momapy.positioning.set_position(
                layout_element, bbox.position, anchor="label_center"
            )
            _update_active_layout(layout_element)
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def set_compartments_to_fit_content(
    map_: momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder,
    xsep: float = 0,
    ysep: float = 0,
) -> momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder:
    """Resize compartments to fit their content.

    Adjusts compartment dimensions to tightly enclose their contained
    species and child compartments (via the ``outside`` attribute).
    Compartments are processed inside-out so that inner compartments
    are sized before their parents.

    Args:
        map_: A CellDesigner map or map builder. If a builder is given,
            it is modified in place.
        xsep: Horizontal separation padding. Defaults to 0.
        ysep: Vertical separation padding. Defaults to 0.

    Returns:
        The modified map or map builder. If a frozen map was given,
            a new map is returned.
    """
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    compartment_species_mapping = collections.defaultdict(list)
    for species in map_builder.model.species:
        compartment = getattr(species, "compartment", None)
        if compartment is not None:
            compartment_species_mapping[compartment].append(species)
    compartment_children_mapping = collections.defaultdict(list)
    for compartment in map_builder.model.compartments:
        outside = getattr(compartment, "outside", None)
        if outside is not None:
            compartment_children_mapping[outside].append(compartment)
    sorted_compartments = _sort_compartments_inside_out(
        map_builder.model.compartments, compartment_children_mapping
    )
    for compartment in sorted_compartments:
        compartment_layouts = map_builder.get_mapping(compartment)
        if compartment_layouts is None:
            continue
        if not isinstance(compartment_layouts, list):
            compartment_layouts = [compartment_layouts]
        for compartment_layout in compartment_layouts:
            if isinstance(compartment_layout, frozenset):
                continue
            elements = []
            for species in compartment_species_mapping.get(compartment, []):
                species_layouts = map_builder.get_mapping(species)
                if species_layouts is None:
                    continue
                if not isinstance(species_layouts, list):
                    species_layouts = [species_layouts]
                for species_layout in species_layouts:
                    if isinstance(species_layout, frozenset):
                        continue
                    elements.append(species_layout)
            for child_compartment in compartment_children_mapping.get(compartment, []):
                child_layouts = map_builder.get_mapping(child_compartment)
                if child_layouts is None:
                    continue
                if not isinstance(child_layouts, list):
                    child_layouts = [child_layouts]
                for child_layout in child_layouts:
                    if isinstance(child_layout, frozenset):
                        continue
                    elements.append(child_layout)
            if elements:
                momapy.positioning.set_fit(compartment_layout, elements, xsep, ysep)
                if compartment_layout.label is not None:
                    compartment_layout.label.position = compartment_layout.south() - (
                        0.0,
                        compartment_layout.label.font_size,
                    )
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def _sort_compartments_inside_out(
    compartments: collections.abc.Iterable,
    compartment_children_mapping: dict,
) -> list:
    """Sort compartments so that inner compartments come before outer ones.

    Performs a post-order traversal of the compartment hierarchy so that
    leaf (innermost) compartments are processed before their parents.

    Args:
        compartments: All compartments in the model.
        compartment_children_mapping: Mapping from parent compartment
            to its list of child compartments.

    Returns:
        Compartments sorted from innermost to outermost.
    """
    visited = set()
    result = []

    def visit(compartment):
        compartment_id = id(compartment)
        if compartment_id in visited:
            return
        visited.add(compartment_id)
        for child in compartment_children_mapping.get(compartment, []):
            visit(child)
        result.append(compartment)

    for compartment in compartments:
        visit(compartment)
    return result


def set_complexes_to_fit_content(
    map_: momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder,
    xsep: float = 0,
    ysep: float = 0,
) -> momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder:
    """Resize complexes to fit their subunits.

    Adjusts complex dimensions to tightly enclose their contained
    subunit layouts.

    Args:
        map_: A CellDesigner map or map builder. If a builder is given,
            it is modified in place.
        xsep: Horizontal separation padding. Defaults to 0.
        ysep: Vertical separation padding. Defaults to 0.

    Returns:
        The modified map or map builder. If a frozen map was given,
            a new map is returned.
    """
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    for species in map_builder.model.species:
        if not momapy.builder.isinstance_or_builder(
            species, momapy.celldesigner.core.Complex
        ):
            continue
        species_layouts = map_builder.get_mapping(species)
        if species_layouts is None:
            continue
        if not isinstance(species_layouts, list):
            species_layouts = [species_layouts]
        for complex_layout in species_layouts:
            if isinstance(complex_layout, frozenset):
                continue
            if not momapy.builder.isinstance_or_builder(
                complex_layout, momapy.celldesigner.core.ComplexLayout
            ):
                continue
            elements = []
            for subunit in species.subunits:
                subunit_layouts = map_builder.get_mapping((subunit, species))
                if subunit_layouts is None:
                    continue
                if not isinstance(subunit_layouts, list):
                    subunit_layouts = [subunit_layouts]
                for subunit_layout in subunit_layouts:
                    if isinstance(subunit_layout, frozenset):
                        continue
                    elements.append(subunit_layout)
            if elements:
                momapy.positioning.set_fit(complex_layout, elements, xsep, ysep)
                if complex_layout.label is not None:
                    complex_layout.label.position = complex_layout.position
                _update_active_layout(complex_layout)
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def set_modifications_to_borders(
    map_: momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder,
) -> momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder:
    """Position modifications and structural states at node borders.

    Moves modification and structural state layouts to the borders
    of their parent species nodes.

    Args:
        map_: A CellDesigner map or map builder. If a builder is given,
            it is modified in place.

    Returns:
        The modified map or map builder. If a frozen map was given,
            a new map is returned.
    """

    def _recursive_set_modifications_to_borders(layout_element):
        for child in layout_element.children():
            if momapy.builder.isinstance_or_builder(
                child,
                (
                    momapy.celldesigner.core.ModificationLayout,
                    momapy.celldesigner.core.StructuralStateLayout,
                ),
            ):
                position = layout_element.own_border(child.position)
                child.position = position
                if child.label is not None:
                    child.label.position = position
            _recursive_set_modifications_to_borders(child)

    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    _recursive_set_modifications_to_borders(map_builder.layout)
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def set_modifications_label_font_size(
    map_: momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder,
    font_size: float,
) -> momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder:
    """Set font size for modification and structural state labels.

    Args:
        map_: A CellDesigner map or map builder. If a builder is given,
            it is modified in place.
        font_size: The font size to apply.

    Returns:
        The modified map or map builder. If a frozen map was given,
            a new map is returned.
    """

    def _recursive_set_font_size(layout_element, font_size):
        for child in layout_element.children():
            if momapy.builder.isinstance_or_builder(
                child,
                (
                    momapy.celldesigner.core.ModificationLayout,
                    momapy.celldesigner.core.StructuralStateLayout,
                ),
            ):
                if child.label is not None:
                    child.label.font_size = font_size
            _recursive_set_font_size(child, font_size)

    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    _recursive_set_font_size(map_builder.layout, font_size)
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def set_arcs_to_borders(
    map_: momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder,
) -> momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder:
    """Adjust arc endpoints to node borders.

    Updates arc start and end points to connect at the borders of
    their source and target nodes rather than centers.

    Args:
        map_: A CellDesigner map or map builder. If a builder is given,
            it is modified in place.

    Returns:
        The modified map or map builder. If a frozen map was given,
            a new map is returned.
    """

    def _set_arc_to_borders(
        arc_layout_element, source, source_type, target, target_type
    ):
        points = arc_layout_element.points()
        if source_type == "connector":
            start_point = source.own_border(target.center())
        elif source_type == "border":
            start_point = _closest_anchor_point(source, points[0])
        else:
            start_point = points[0]
        if target_type == "connector":
            end_point = target.own_border(source.center())
        elif target_type == "border":
            end_point = _closest_anchor_point(target, points[-1])
        else:
            end_point = points[-1]
        arc_layout_element.segments[0].p1 = momapy.builder.builder_from_object(
            start_point
        )
        arc_layout_element.segments[-1].p2 = momapy.builder.builder_from_object(
            end_point
        )

    _MODIFIER_TYPES = (
        momapy.celldesigner.core.CatalysisLayout,
        momapy.celldesigner.core.UnknownCatalysisLayout,
        momapy.celldesigner.core.InhibitionLayout,
        momapy.celldesigner.core.UnknownInhibitionLayout,
        momapy.celldesigner.core.PhysicalStimulationLayout,
        momapy.celldesigner.core.UnknownPhysicalStimulationLayout,
        momapy.celldesigner.core.ModulationLayout,
        momapy.celldesigner.core.UnknownModulationLayout,
        momapy.celldesigner.core.TriggeringLayout,
        momapy.celldesigner.core.UnknownTriggeringLayout,
        momapy.celldesigner.core.PositiveInfluenceLayout,
        momapy.celldesigner.core.UnknownPositiveInfluenceLayout,
    )

    _T_SHAPE_TYPES = (
        momapy.celldesigner.core.HeterodimerAssociationLayout,
        momapy.celldesigner.core.DissociationLayout,
        momapy.celldesigner.core.TruncationLayout,
    )

    def _snap_start_to_border(layout_element, node):
        """Snap segments[0].p1 to the closest anchor on node."""
        points = layout_element.points()
        anchor_point = _closest_anchor_point(node, points[0])
        layout_element.segments[0].p1 = momapy.builder.builder_from_object(anchor_point)

    def _snap_end_to_border(layout_element, node):
        """Snap segments[-1].p2 to the closest anchor on node."""
        points = layout_element.points()
        anchor_point = _closest_anchor_point(node, points[-1])
        layout_element.segments[-1].p2 = momapy.builder.builder_from_object(
            anchor_point
        )

    def _snap_end_to_reaction_node(layout_element, reaction_layout):
        """Snap segments[-1].p2 to reaction node border."""
        points = layout_element.points()
        reference = points[-2] if len(points) > 2 else points[0]
        border_point = reaction_layout.reaction_node_border(reference)
        if border_point is not None:
            layout_element.segments[-1].p2 = momapy.builder.builder_from_object(
                border_point
            )

    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_

    # Run two iterations to converge: the first pass fixes reaction
    # endpoints which shifts reaction node positions, requiring a
    # second pass to re-snap dependent arcs.
    for _ in range(2):
        # Reaction layouts — snap source/target species endpoints.
        # This fixes the reaction node position (midpoint of segment).
        for layout_element in map_builder.layout.layout_elements:
            if not momapy.builder.isinstance_or_builder(
                layout_element, momapy.celldesigner.core.ReactionLayout
            ):
                continue
            source = layout_element.source
            target = layout_element.target
            if source is not None and hasattr(source, "own_border"):
                _snap_start_to_border(layout_element, source)
            if target is not None and hasattr(target, "own_border"):
                _snap_end_to_border(layout_element, target)

        # Modifier and modulation arcs — snap to source species
        # border and target reaction node border (or target species
        # border for species-to-species modulations).
        for layout_element in map_builder.layout.layout_elements:
            if not momapy.builder.isinstance_or_builder(
                layout_element, _MODIFIER_TYPES
            ):
                continue
            source = layout_element.source
            target = layout_element.target
            if source is not None and hasattr(source, "own_border"):
                _snap_start_to_border(layout_element, source)
            if target is not None:
                if hasattr(target, "reaction_node_border"):
                    _snap_end_to_reaction_node(layout_element, target)
                elif hasattr(target, "own_border"):
                    _snap_end_to_border(layout_element, target)

        # Consumption and production arcs — snap to species borders
        # and reaction connector tips.
        for layout_element in map_builder.layout.layout_elements:
            if momapy.builder.isinstance_or_builder(
                layout_element, momapy.celldesigner.core.ConsumptionLayout
            ):
                reaction_layout = layout_element.source
                species_layout = layout_element.target
                if species_layout is not None and hasattr(species_layout, "own_border"):
                    _snap_start_to_border(layout_element, species_layout)
                is_t_shape = momapy.builder.isinstance_or_builder(
                    reaction_layout, _T_SHAPE_TYPES
                )
                if not is_t_shape and hasattr(reaction_layout, "left_connector_tip"):
                    layout_element.segments[-1].p2 = momapy.builder.builder_from_object(
                        reaction_layout.left_connector_tip()
                    )
            elif momapy.builder.isinstance_or_builder(
                layout_element, momapy.celldesigner.core.ProductionLayout
            ):
                reaction_layout = layout_element.source
                species_layout = layout_element.target
                is_t_shape = momapy.builder.isinstance_or_builder(
                    reaction_layout, _T_SHAPE_TYPES
                )
                if not is_t_shape and hasattr(reaction_layout, "right_connector_tip"):
                    layout_element.segments[0].p1 = momapy.builder.builder_from_object(
                        reaction_layout.right_connector_tip()
                    )
                if species_layout is not None and hasattr(species_layout, "own_border"):
                    _snap_end_to_border(layout_element, species_layout)
            elif momapy.builder.isinstance_or_builder(
                layout_element, momapy.celldesigner.core.LogicArcLayout
            ):
                _set_arc_to_borders(
                    layout_element,
                    layout_element.source,
                    "border",
                    layout_element.target,
                    "border",
                )

    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def straighten_arcs(
    map_: momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder,
    angle_tolerance: float = 5.0,
) -> momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder:
    """Straighten near-horizontal and near-vertical arc segments.

    For each segment in an arc, checks whether the segment is close to
    horizontal or vertical (within ``angle_tolerance`` of the axis).
    If so, the segment is snapped to be exactly horizontal or vertical
    by adjusting its end point.

    Segments are processed from start to end, so the arc's start point
    is kept fixed and adjustments cascade through bend points toward
    the end.

    Args:
        map_: A CellDesigner map or map builder. If a builder is given,
            it is modified in place.
        angle_tolerance: Maximum deviation from the horizontal or
            vertical axis (in degrees) for a segment to be snapped.
            Defaults to 5.0.

    Returns:
        The modified map or map builder. If a frozen map was given,
            a new map is returned.
    """
    min_segment_length = 1.0

    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    for layout_element in map_builder.layout.layout_elements:
        if not momapy.builder.isinstance_or_builder(
            layout_element, momapy.core.layout.Arc
        ):
            continue
        for index in range(len(layout_element.segments)):
            segment = layout_element.segments[index]
            delta_x = segment.p2.x - segment.p1.x
            delta_y = segment.p2.y - segment.p1.y
            length = math.sqrt(delta_x * delta_x + delta_y * delta_y)
            if length < min_segment_length:
                continue
            angle_from_horizontal = math.degrees(math.atan2(abs(delta_y), abs(delta_x)))
            if angle_from_horizontal <= angle_tolerance:
                # Nearly horizontal: snap p2.y to p1.y.
                new_point = momapy.builder.builder_from_object(
                    momapy.geometry.Point(segment.p2.x, segment.p1.y)
                )
                segment.p2 = new_point
                if index + 1 < len(layout_element.segments):
                    layout_element.segments[index + 1].p1 = new_point
            elif angle_from_horizontal >= 90.0 - angle_tolerance:
                # Nearly vertical: snap p2.x to p1.x.
                new_point = momapy.builder.builder_from_object(
                    momapy.geometry.Point(segment.p1.x, segment.p2.y)
                )
                segment.p2 = new_point
                if index + 1 < len(layout_element.segments):
                    layout_element.segments[index + 1].p1 = new_point
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def tidy(
    map_: momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder,
    modifications_omit_width: bool = False,
    modifications_omit_height: bool = False,
    nodes_xsep: float = 4,
    nodes_ysep: float = 4,
    modifications_xsep: float = 2,
    modifications_ysep: float = 2,
    complexes_xsep: float = 10,
    complexes_ysep: float = 10,
    compartments_xsep: float = 25,
    compartments_ysep: float = 25,
    layout_xsep: float = 0,
    layout_ysep: float = 0,
    arcs_angle_tolerance: float = 5.0,
) -> momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder:
    """Apply comprehensive layout tidying to a CellDesigner map.

    Performs multiple layout optimization steps including fitting nodes to
    labels, positioning modifications, resizing complexes and compartments,
    and adjusting arc endpoints.

    Args:
        map_: A CellDesigner map or map builder. If a builder is given,
            it is modified in place.
        modifications_omit_width: Do not adjust modification widths.
        modifications_omit_height: Do not adjust modification heights.
        nodes_xsep: Horizontal padding for node sizing. Defaults to 4.
        nodes_ysep: Vertical padding for node sizing. Defaults to 4.
        modifications_xsep: Horizontal padding for modifications.
            Defaults to 2.
        modifications_ysep: Vertical padding for modifications.
            Defaults to 2.
        complexes_xsep: Horizontal padding for complexes. Defaults to 10.
        complexes_ysep: Vertical padding for complexes. Defaults to 10.
        compartments_xsep: Horizontal padding for compartments. Defaults to 25.
        compartments_ysep: Vertical padding for compartments. Defaults to 25.
        layout_xsep: Horizontal padding for overall layout.
        layout_ysep: Vertical padding for overall layout.
        arcs_angle_tolerance: Maximum deviation from the horizontal or
            vertical axis for arc straightening. Defaults to 5.0.

    Returns:
        The tidied map or map builder. If a frozen map was given,
            a new map is returned.
    """
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    set_nodes_to_fit_labels(
        map_builder,
        xsep=nodes_xsep,
        ysep=nodes_ysep,
        exclude=[
            momapy.celldesigner.core.ModificationLayout,
            momapy.celldesigner.core.StructuralStateLayout,
            momapy.celldesigner.core.ComplexLayout,
        ],
    )
    set_modifications_to_borders(map_builder)
    set_nodes_to_fit_labels(
        map_builder,
        xsep=modifications_xsep,
        ysep=modifications_ysep,
        omit_width=modifications_omit_width,
        omit_height=modifications_omit_height,
        restrict_to=[
            momapy.celldesigner.core.ModificationLayout,
            momapy.celldesigner.core.StructuralStateLayout,
        ],
    )
    set_complexes_to_fit_content(map_builder, complexes_xsep, complexes_ysep)
    set_compartments_to_fit_content(map_builder, compartments_xsep, compartments_ysep)
    set_arcs_to_borders(map_builder)
    straighten_arcs(map_builder, arcs_angle_tolerance)
    set_layout_to_fit_content(map_builder, layout_xsep, layout_ysep)
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def get_info(map_: momapy.celldesigner.core.CellDesignerMap) -> dict:
    """Get a summary of the contents of a CellDesigner map.

    Returns a dictionary with the map type, model element counts,
    and layout dimensions.

    Args:
        map_: A CellDesigner map.

    Returns:
        A dictionary with keys ``map_type``, ``model``, and ``layout``.
    """
    model = map_.model
    layout = map_.layout
    model_info = {
        "compartments": len(model.compartments),
        "species": len(model.species),
        "reactions": len(model.reactions),
        "species_templates": len(model.species_templates),
        "boolean_logic_gates": len(model.boolean_logic_gates),
        "modulations": len(model.modulations),
    }
    layout_info = {
        "width": layout.width,
        "height": layout.height,
        "elements": len(layout.descendants()),
    }
    return {
        "map_type": "CellDesigner",
        "model": model_info,
        "layout": layout_info,
    }
