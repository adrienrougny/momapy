"""Utility functions for CellDesigner map manipulation.

This module provides helper functions for adjusting and manipulating
CellDesigner maps, including highlighting specific layout elements.
"""

import collections.abc

import momapy.builder
import momapy.celldesigner.core
import momapy.core.elements
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
