import collections

import momapy.positioning
import momapy.builder


def set_compartments_to_fit_content(map_builder, xsep=0, ysep=0):
    compartment_entities_mapping = collections.defaultdict(list)
    model = map_builder.model
    if momapy.builder.isinstance_or_builder(
        map_builder, momapy.sbgn.pd.SBGNPDMap
    ):
        for entity_pool in model.entity_pools:
            compartment = entity_pool.compartment
            if compartment is not None:
                compartment_entities_mapping[compartment].append(entity_pool)
    else:
        for activity in model.activities:
            compartment = activity.compartment
            if compartment is not None:
                compartment_entities_mapping[compartment].append(activity)
    for compartment in compartment_entities_mapping:
        for compartment_layout in map_builder.layout_model_mapping[compartment]:
            compartment_layout, *_ = compartment_layout
            elements = []
            for entity in compartment_entities_mapping[compartment]:
                for entity_layout in map_builder.layout_model_mapping[entity]:
                    entity_layout, *_ = entity_layout
                    elements.append(entity_layout)
            momapy.positioning.set_fit(compartment_layout, elements, xsep, ysep)
            if compartment_layout.label is not None:
                compartment_layout.label.position = compartment_layout.position
                compartment_layout.label.width = compartment_layout.width
                compartment_layout.label.height = compartment_layout.height


def set_complexes_to_fit_content(map_builder, xsep=0, ysep=0):
    for entity_pool in map_builder.model.entity_pools:
        if isinstance(
            entity_pool,
            momapy.builder.get_or_make_builder_cls(momapy.sbgn.pd.Complex),
        ):
            for complex_layout in map_builder.layout_model_mapping[entity_pool]:
                complex_layout, *_ = complex_layout
                elements = []
                for subunit in entity_pool.subunits:
                    subunit_layouts = map_builder.layout_model_mapping[
                        (subunit, entity_pool)
                    ]
                    for subunit_layout in subunit_layouts:
                        subunit_layout, *_ = subunit_layout
                        if subunit_layout in complex_layout.layout_elements:
                            elements.append(subunit_layout)
                if len(elements) > 0:
                    momapy.positioning.set_fit(
                        complex_layout, elements, xsep, ysep
                    )
                    if complex_layout.label is not None:
                        complex_layout.label.position = complex_layout.position
                        complex_layout.label.width = complex_layout.width
                        complex_layout.label.height = complex_layout.height


def set_submaps_to_fit_content(map_builder, xsep=0, ysep=0):
    for submap in map_builder.model.submaps:
        for submap_layout in map_builder.layout_model_mapping[submap]:
            submap_layout, *_ = submap_layout
            elements = []
            for terminal in submap.terminals:
                terminal_layouts = map_builder.layout_model_mapping[
                    (terminal, submap)
                ]
                for terminal_layout in terminal_layouts:
                    terminal_layout, *_ = terminal_layout
                    if terminal_layout in submap_layout.layout_elements:
                        elements.append(terminal_layout)
            if len(elements) > 0:
                momapy.positioning.set_fit(submap_layout, elements, xsep, ysep)
                if submap_layout.label is not None:
                    submap_layout.label.position = submap_layout.position
                    submap_layout.label.width = submap_layout.width
                    submap_layout.label.height = submap_layout.height


def set_nodes_to_fit_labels(map_builder, xsep=0, ysep=0):
    for layout_element in map_builder.layout.descendants():
        if (
            isinstance(layout_element, momapy.core.NodeLayoutBuilder)
            and layout_element.label is not None
        ):
            position, width, height = momapy.positioning.fit(
                [layout_element.label.logical_bbox()], xsep, ysep
            )
            if width > layout_element.width:
                layout_element.width = width
            if height > layout_element.height:
                layout_element.height = height
            momapy.positioning.set_position(
                layout_element, position, anchor="label_center"
            )


def set_arcs_to_borders(map_):
    def _get_arcs(map_):
        arcs = []
        for layout_element in map_.layout.layout_elements:
            if momapy.builder.isinstance_or_builder(
                layout_element, (momapy.sbgn.pd.GenericProcessLayout)
            ):
                for sub_layout_element in layout_element.layout_elements:
                    if momapy.builder.isinstance_or_builder(
                        sub_layout_element, (momapy.sbgn.pd.ConsumptionLayout)
                    ):
                        arcs.append(
                            (
                                sub_layout_element,
                                layout_element,
                                sub_layout_element.target,
                            )
                        )
        return arcs

    def _get_process_direction(layout_element):
        consumption_layout = None
        production_layout = None
        for sub_layout_element in layout_element.layout_elements:
            if momapy.builder.isinstance_or_builder(
                sub_layout_element, (momapy.sbgn.pd.ConsumptionLayout)
            ):
                consumption_layout = sub_layout_element
            elif momapy.builder.isinstance_or_builder(
                sub_layout_element, (momapy.sbgn.pd.ProductionLayout)
            ):
                production_layout = sub_layout_element
            if consumption_layout is not None and production_layout is not None:
                break
        if consumption_layout is not None and production_layout is not None:
            if layout_element.direction == momapy.core.Direction.HORIZONTAL:
                if (
                    consumption_layout.points()[-1].x
                    < production_layout.points()[-1].x
                ):
                    direction = "lr"
                else:
                    direction = "rl"
            else:
                if (
                    consumption_layout.points()[-1].y
                    < production_layout.points()[-1].y
                ):
                    direction = "lr"
                else:
                    direction = "rl"
        else:
            direction = None
        return direction

    for layout_element in map_.layout.layout_elements:
        if momapy.builder.isinstance_or_builder(
            layout_element, (momapy.sbgn.pd.GenericProcessLayout)
        ):
            direction = _get_process_direction(layout_element)
            if direction is None:
                direction = "lr"
            for sub_layout_element in layout_element.layout_elements:
                if momapy.builder.isinstance_or_builder(
                    sub_layout_element, (momapy.sbgn.pd.ConsumptionLayout)
                ):
                    points = sub_layout_element.points()
                    if len(sub_layout_element.segments) > 1:
                        reference_point = points[-2]
                    else:
                        if direction == "lr":
                            reference_point = (
                                layout_element.left_connector_tip()
                            )
                        else:
                            reference_point = (
                                layout_element.right_connector_tip()
                            )
                    end_point = sub_layout_element.target.self_border(
                        reference_point
                    )
                    sub_layout_element.segments[
                        -1
                    ].p2 = momapy.builder.builder_from_object(end_point)
                    if direction == "lr":
                        start_point = layout_element.left_connector_tip()
                    else:
                        start_point = layout_element.right_connector_tip()
                    sub_layout_element.segments[
                        0
                    ].p1 = momapy.builder.builder_from_object(start_point)
                elif momapy.builder.isinstance_or_builder(
                    sub_layout_element, (momapy.sbgn.pd.ProductionLayout)
                ):
                    points = sub_layout_element.points()
                    if len(sub_layout_element.segments) > 1:
                        reference_point = points[-2]
                    else:
                        if direction == "lr":
                            reference_point = (
                                layout_element.right_connector_tip()
                            )
                        else:
                            reference_point = (
                                layout_element.left_connector_tip()
                            )
                    end_point = sub_layout_element.target.self_border(
                        reference_point
                    )
                    sub_layout_element.segments[
                        -1
                    ].p2 = momapy.builder.builder_from_object(end_point)
                    if direction == "lr":
                        start_point = layout_element.right_connector_tip()
                    else:
                        start_point = layout_element.left_connector_tip()
                    sub_layout_element.segments[
                        0
                    ].p1 = momapy.builder.builder_from_object(start_point)


def set_auxilliary_units_to_borders(map_builder):
    def _rec_set_auxilliary_units_to_borders(layout_element):
        for child in layout_element.children():
            if isinstance(
                child,
                (
                    momapy.builder.get_or_make_builder_cls(
                        momapy.sbgn.pd.StateVariableLayout
                    ),
                    momapy.builder.get_or_make_builder_cls(
                        momapy.sbgn.pd.UnitOfInformationLayout
                    ),
                    momapy.builder.get_or_make_builder_cls(
                        momapy.sbgn.af.UnspecifiedEntityUnitOfInformationLayout
                    ),
                    momapy.builder.get_or_make_builder_cls(
                        momapy.sbgn.af.MacromoleculeUnitOfInformationLayout
                    ),
                    momapy.builder.get_or_make_builder_cls(
                        momapy.sbgn.af.NucleicAcidFeatureUnitOfInformationLayout
                    ),
                    momapy.builder.get_or_make_builder_cls(
                        momapy.sbgn.af.ComplexUnitOfInformationLayout
                    ),
                    momapy.builder.get_or_make_builder_cls(
                        momapy.sbgn.af.SimpleChemicalUnitOfInformationLayout
                    ),
                    momapy.builder.get_or_make_builder_cls(
                        momapy.sbgn.af.PerturbationUnitOfInformationLayout
                    ),
                ),
            ) and isinstance(layout_element, momapy.core.NodeLayoutBuilder):
                position = layout_element.self_border(child.position)
                child.position = position
                if child.label is not None:
                    child.label.position = position
            _rec_set_auxilliary_units_to_borders(child)

    _rec_set_auxilliary_units_to_borders(map_builder.layout)


def set_layout_to_fit_content(map_builder, xsep=0, ysep=0):
    momapy.positioning.set_fit(
        map_builder.layout, map_builder.layout.layout_elements, xsep, ysep
    )


def tidy(
    map_builder,
    nodes_xsep=5,
    nodes_ysep=5,
    complexes_xsep=15,
    complexes_ysep=15,
    compartments_xsep=15,
    compartments_ysep=15,
    layout_xsep=15,
    layout_ysep=15,
):
    set_nodes_to_fit_labels(map_builder, nodes_xsep, nodes_ysep)
    set_auxilliary_units_to_borders(map_builder)
    if momapy.builder.isinstance_or_builder(
        map_builder, momapy.sbgn.pd.SBGNPDMap
    ):
        set_complexes_to_fit_content(
            map_builder, complexes_xsep, complexes_ysep
        )
    set_submaps_to_fit_content(map_builder, 0, 0)
    set_nodes_to_fit_labels(map_builder, nodes_xsep, nodes_ysep)
    set_auxilliary_units_to_borders(map_builder)
    set_compartments_to_fit_content(
        map_builder, compartments_xsep, compartments_ysep
    )
    set_nodes_to_fit_labels(map_builder, nodes_xsep, nodes_ysep)
    set_arcs_to_borders(map_builder)
    set_layout_to_fit_content(map_builder, layout_xsep, layout_ysep)
