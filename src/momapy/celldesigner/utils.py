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
import momapy.core.elements
import momapy.core.layout
import momapy.geometry
import momapy.positioning
import momapy.styling
import momapy.coloring
import momapy.drawing


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
                momapy.styling.TypeSelector("RectangleCompartmentLayout"),
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
            and not momapy.builder.isinstance_or_builder(
                layout_element, exclude
            )
            and hasattr(layout_element, "label")
            and layout_element.label is not None
        ):
            bbox = momapy.positioning.fit(
                [layout_element.label.bbox()], xsep, ysep
            )
            if not omit_width:
                if bbox.width > layout_element.width:
                    layout_element.width = bbox.width
            if not omit_height:
                if bbox.height > layout_element.height:
                    layout_element.height = bbox.height
            momapy.positioning.set_position(
                layout_element, bbox.position, anchor="label_center"
            )
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
    species.

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
    for compartment in compartment_species_mapping:
        compartment_layouts = map_builder.get_mapping(compartment)
        if compartment_layouts is None:
            continue
        if not isinstance(compartment_layouts, list):
            compartment_layouts = [compartment_layouts]
        for compartment_layout in compartment_layouts:
            if isinstance(compartment_layout, frozenset):
                continue
            elements = []
            for species in compartment_species_mapping[compartment]:
                species_layouts = map_builder.get_mapping(species)
                if species_layouts is None:
                    continue
                if not isinstance(species_layouts, list):
                    species_layouts = [species_layouts]
                for species_layout in species_layouts:
                    if isinstance(species_layout, frozenset):
                        continue
                    elements.append(species_layout)
            if elements:
                momapy.positioning.set_fit(
                    compartment_layout, elements, xsep, ysep
                )
                if compartment_layout.label is not None:
                    compartment_layout.label.position = (
                        compartment_layout.south()
                        - (0.0, compartment_layout.label.font_size)
                    )
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


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
            elements = [
                child
                for child in complex_layout.layout_elements
                if momapy.builder.isinstance_or_builder(
                    child, momapy.celldesigner.core.CellDesignerNode
                )
            ]
            if elements:
                momapy.positioning.set_fit(
                    complex_layout, elements, xsep, ysep
                )
                if complex_layout.label is not None:
                    complex_layout.label.position = complex_layout.position
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
            if len(arc_layout_element.segments) > 1:
                start_reference_point = points[1]
            else:
                start_reference_point = target.center()
            start_point = source.own_border(start_reference_point)
            if start_point is None:
                start_point = source.center()
        else:
            start_point = points[0]
        if target_type == "connector":
            end_point = target.own_border(source.center())
        elif target_type == "border":
            if len(arc_layout_element.segments) > 1:
                end_reference_point = points[-2]
            else:
                end_reference_point = source.center()
            end_point = target.own_border(end_reference_point)
            if end_point is None:
                end_point = target.center()
        else:
            end_point = points[-1]
        arc_layout_element.segments[0].p1 = (
            momapy.builder.builder_from_object(start_point)
        )
        arc_layout_element.segments[-1].p2 = (
            momapy.builder.builder_from_object(end_point)
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
        """Snap segments[0].p1 to node.own_border()."""
        points = layout_element.points()
        reference = points[1] if len(points) > 2 else points[-1]
        border_point = node.own_border(reference)
        if border_point is not None:
            layout_element.segments[0].p1 = (
                momapy.builder.builder_from_object(border_point)
            )

    def _snap_end_to_border(layout_element, node):
        """Snap segments[-1].p2 to node.own_border()."""
        points = layout_element.points()
        reference = points[-2] if len(points) > 2 else points[0]
        border_point = node.own_border(reference)
        if border_point is not None:
            layout_element.segments[-1].p2 = (
                momapy.builder.builder_from_object(border_point)
            )

    def _snap_end_to_reaction_node(layout_element, reaction_layout):
        """Snap segments[-1].p2 to reaction node border."""
        points = layout_element.points()
        reference = points[-2] if len(points) > 2 else points[0]
        border_point = reaction_layout.reaction_node_border(reference)
        if border_point is not None:
            layout_element.segments[-1].p2 = (
                momapy.builder.builder_from_object(border_point)
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
                if species_layout is not None and hasattr(
                    species_layout, "own_border"
                ):
                    _snap_start_to_border(layout_element, species_layout)
                is_t_shape = momapy.builder.isinstance_or_builder(
                    reaction_layout, _T_SHAPE_TYPES
                )
                if not is_t_shape and hasattr(
                    reaction_layout, "left_connector_tip"
                ):
                    layout_element.segments[-1].p2 = (
                        momapy.builder.builder_from_object(
                            reaction_layout.left_connector_tip()
                        )
                    )
            elif momapy.builder.isinstance_or_builder(
                layout_element, momapy.celldesigner.core.ProductionLayout
            ):
                reaction_layout = layout_element.source
                species_layout = layout_element.target
                is_t_shape = momapy.builder.isinstance_or_builder(
                    reaction_layout, _T_SHAPE_TYPES
                )
                if not is_t_shape and hasattr(
                    reaction_layout, "right_connector_tip"
                ):
                    layout_element.segments[0].p1 = (
                        momapy.builder.builder_from_object(
                            reaction_layout.right_connector_tip()
                        )
                    )
                if species_layout is not None and hasattr(
                    species_layout, "own_border"
                ):
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


def set_arcs_to_orthogonal(
    map_: momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder,
    angle_tolerance: float = 5.0,
) -> momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder:
    """Snap near-orthogonal arc bends to exact right angles.

    CellDesigner stores arc edit points in a local coordinate frame.
    The coordinate transform can introduce small angular deviations
    from 90 degrees at bend points. This function detects bends that
    are within ``angle_tolerance`` of 90 degrees and adjusts the
    shared bend point to produce an exact right angle.

    For each bend, the longer adjacent segment's direction is
    preserved and the bend point is projected perpendicularly onto
    that direction.

    Args:
        map_: A CellDesigner map or map builder. If a builder is given,
            it is modified in place.
        angle_tolerance: Maximum deviation from 90 degrees (in degrees)
            for a bend to be snapped. Defaults to 5.0.

    Returns:
        The modified map or map builder. If a frozen map was given,
            a new map is returned.
    """
    min_segment_length = 1.0
    max_iterations = 3

    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    # Iterate to handle consecutive bends on the same arc: snapping
    # one bend changes the shared segment direction, which can
    # un-snap an adjacent bend that was already processed.
    for _ in range(max_iterations):
        snapped_any = False
        for layout_element in map_builder.layout.layout_elements:
            if not momapy.builder.isinstance_or_builder(
                layout_element, momapy.core.layout.Arc
            ):
                continue
            if len(layout_element.segments) < 2:
                continue
            for index in range(len(layout_element.segments) - 1):
                segment_before = layout_element.segments[index]
                segment_after = layout_element.segments[index + 1]
                delta_x_before = segment_before.p2.x - segment_before.p1.x
                delta_y_before = segment_before.p2.y - segment_before.p1.y
                delta_x_after = segment_after.p2.x - segment_after.p1.x
                delta_y_after = segment_after.p2.y - segment_after.p1.y
                length_before = math.sqrt(
                    delta_x_before * delta_x_before
                    + delta_y_before * delta_y_before
                )
                length_after = math.sqrt(
                    delta_x_after * delta_x_after
                    + delta_y_after * delta_y_after
                )
                if (
                    length_before < min_segment_length
                    or length_after < min_segment_length
                ):
                    continue
                dot_product = (
                    delta_x_before * delta_x_after
                    + delta_y_before * delta_y_after
                )
                cos_angle = dot_product / (length_before * length_after)
                cos_angle = max(-1.0, min(1.0, cos_angle))
                angle = math.degrees(math.acos(abs(cos_angle)))
                deviation = abs(90.0 - angle)
                if deviation > angle_tolerance or deviation < 1e-3:
                    continue
                # Snap: preserve the longer segment's direction and
                # project the bend point perpendicularly.
                if length_before >= length_after:
                    # Preserve segment_before direction; new bend
                    # point is the foot of perpendicular from
                    # segment_after.p2 onto the line through
                    # segment_before.
                    direction_x = delta_x_before / length_before
                    direction_y = delta_y_before / length_before
                    vector_x = (
                        segment_after.p2.x - segment_before.p1.x
                    )
                    vector_y = (
                        segment_after.p2.y - segment_before.p1.y
                    )
                    projection = (
                        vector_x * direction_x + vector_y * direction_y
                    )
                    new_x = (
                        segment_before.p1.x + projection * direction_x
                    )
                    new_y = (
                        segment_before.p1.y + projection * direction_y
                    )
                else:
                    # Preserve segment_after direction; new bend
                    # point is the foot of perpendicular from
                    # segment_before.p1 onto the line through
                    # segment_after.
                    direction_x = delta_x_after / length_after
                    direction_y = delta_y_after / length_after
                    vector_x = (
                        segment_before.p1.x - segment_after.p2.x
                    )
                    vector_y = (
                        segment_before.p1.y - segment_after.p2.y
                    )
                    projection = (
                        vector_x * direction_x + vector_y * direction_y
                    )
                    new_x = (
                        segment_after.p2.x + projection * direction_x
                    )
                    new_y = (
                        segment_after.p2.y + projection * direction_y
                    )
                new_point = momapy.builder.builder_from_object(
                    momapy.geometry.Point(new_x, new_y)
                )
                segment_before.p2 = new_point
                segment_after.p1 = new_point
                snapped_any = True
        if not snapped_any:
            break
    if isinstance(map_, momapy.celldesigner.core.CellDesignerMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def tidy(
    map_: momapy.celldesigner.core.CellDesignerMap | momapy.builder.Builder,
    modifications_omit_width: bool = False,
    modifications_omit_height: bool = False,
    nodes_xsep: float = 0,
    nodes_ysep: float = 0,
    modifications_xsep: float = 0,
    modifications_ysep: float = 0,
    complexes_xsep: float = 10,
    complexes_ysep: float = 10,
    compartments_xsep: float = 10,
    compartments_ysep: float = 10,
    layout_xsep: float = 0,
    layout_ysep: float = 0,
    set_arcs_to_orthogonal_: bool = False,
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
        nodes_xsep: Horizontal padding for node sizing.
        nodes_ysep: Vertical padding for node sizing.
        modifications_xsep: Horizontal padding for modifications.
        modifications_ysep: Vertical padding for modifications.
        complexes_xsep: Horizontal padding for complexes. Defaults to 10.
        complexes_ysep: Vertical padding for complexes. Defaults to 10.
        compartments_xsep: Horizontal padding for compartments. Defaults to 10.
        compartments_ysep: Vertical padding for compartments. Defaults to 10.
        layout_xsep: Horizontal padding for overall layout.
        layout_ysep: Vertical padding for overall layout.
        set_arcs_to_orthogonal_: If True, snap near-orthogonal arc bends
            to exact right angles. Defaults to False.
        arcs_angle_tolerance: Maximum deviation from 90 degrees for
            snapping. Only used when ``set_arcs_to_orthogonal_`` is True.
            Defaults to 5.0.

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
    set_complexes_to_fit_content(
        map_builder, complexes_xsep, complexes_ysep
    )
    set_compartments_to_fit_content(
        map_builder, compartments_xsep, compartments_ysep
    )
    set_arcs_to_borders(map_builder)
    if set_arcs_to_orthogonal_:
        set_arcs_to_orthogonal(map_builder, arcs_angle_tolerance)
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
