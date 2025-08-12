import collections

import momapy.positioning
import momapy.builder


def set_compartments_to_fit_content(map_, xsep=0, ysep=0):
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    compartment_entities_mapping = collections.defaultdict(list)
    model = map_builder.model
    if momapy.builder.isinstance_or_builder(map_builder, momapy.sbgn.pd.SBGNPDMap):
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
        for compartment_layout in map_builder.get_mapping(compartment):
            elements = []
            for entity in compartment_entities_mapping[compartment]:
                for entity_layout in map_builder.get_mapping(entity):
                    elements.append(entity_layout)
            momapy.positioning.set_fit(compartment_layout, elements, xsep, ysep)
            if compartment_layout.label is not None:
                compartment_layout.label.position = compartment_layout.position
                compartment_layout.label.width = compartment_layout.width
                compartment_layout.label.height = compartment_layout.height
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def set_complexes_to_fit_content(map_, xsep=0, ysep=0):
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    for entity_pool in map_builder.model.entity_pools:
        if isinstance(
            entity_pool,
            momapy.builder.get_or_make_builder_cls(momapy.sbgn.pd.Complex),
        ):
            for complex_layout in map_builder.get_mapping(entity_pool):
                elements = []
                for subunit in entity_pool.subunits:
                    subunit_layouts = map_builder.get_mapping((subunit, entity_pool))
                    for subunit_layout in subunit_layouts:
                        if subunit_layout in complex_layout.layout_elements:
                            elements.append(subunit_layout)
                if len(elements) > 0:
                    momapy.positioning.set_fit(complex_layout, elements, xsep, ysep)
                    if complex_layout.label is not None:
                        complex_layout.label.position = complex_layout.position
                        complex_layout.label.width = complex_layout.width
                        complex_layout.label.height = complex_layout.height
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def set_submaps_to_fit_content(map_, xsep=0, ysep=0):
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    for submap in map_builder.model.submaps:
        for submap_layout in map_builder.get_mapping(submap):
            elements = []
            for terminal in submap.terminals:
                terminal_layouts = map_builder.layout_model_mapping.get_mapping(
                    (
                        terminal,
                        submap,
                    )
                )
                for terminal_layout in terminal_layouts:
                    if terminal_layout in submap_layout.layout_elements:
                        elements.append(terminal_layout)
            if len(elements) > 0:
                momapy.positioning.set_fit(submap_layout, elements, xsep, ysep)
                if submap_layout.label is not None:
                    submap_layout.label.position = submap_layout.position
                    submap_layout.label.width = submap_layout.width
                    submap_layout.label.height = submap_layout.height
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def set_nodes_to_fit_labels(
    map_,
    xsep=0,
    ysep=0,
    omit_width=False,
    omit_height=False,
    restrict_to=None,
    exclude=None,
):
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    if restrict_to is None:
        restrict_to = []
    if not restrict_to:
        restrict_to = [momapy.core.Node]
    if exclude is None:
        exclude = []
    exclude = tuple(exclude)
    restrict_to = tuple(restrict_to)
    if omit_width and omit_height:
        return
    for layout_element in map_builder.layout.descendants():
        if (
            momapy.builder.isinstance_or_builder(layout_element, restrict_to)
            and not momapy.builder.isinstance_or_builder(layout_element, exclude)
            and hasattr(layout_element, "label")
            and layout_element.label is not None
        ):
            bbox = momapy.positioning.fit(
                [layout_element.label.logical_bbox()], xsep, ysep
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
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def set_arcs_to_borders(map_):
    def _set_arc_to_borders(
        arc_layout_element, source, source_type, target, target_type
    ):
        points = arc_layout_element.points()
        if source_type == "left":
            start_point = source.left_connector_tip()
        elif source_type == "right":
            start_point = source.right_connector_tip()
        else:
            if len(arc_layout_element.segments) > 1:
                start_reference_point = points[1]
            else:
                if target_type == "border":
                    start_reference_point = target.center()
                elif target_type == "left":
                    start_reference_point = target.left_connector_tip()
                else:
                    start_reference_point = target.right_connector_tip()
            start_point = source.border(start_reference_point)
        if target_type == "left":
            end_point = target.left_connector_tip()
        elif target_type == "right":
            end_point = target.right_connector_tip()
        else:
            if len(arc_layout_element.segments) > 1:
                end_reference_point = points[-2]
            else:
                if source_type == "border":
                    end_reference_point = source.center()
                elif source_type == "left":
                    end_reference_point = source.left_connector_tip()
                else:
                    end_reference_point = source.right_connector_tip()
            end_point = target.border(end_reference_point)
        arc_layout_element.segments[0].p1 = momapy.builder.builder_from_object(
            start_point
        )
        arc_layout_element.segments[-1].p2 = momapy.builder.builder_from_object(
            end_point
        )

    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    for layout_element in map_builder.layout.layout_elements:
        # Flux arcs
        if momapy.builder.isinstance_or_builder(
            layout_element,
            (
                momapy.sbgn.pd.GenericProcessLayout,
                momapy.sbgn.pd.AssociationLayout,
                momapy.sbgn.pd.DissociationLayout,
                momapy.sbgn.pd.OmittedProcessLayout,
                momapy.sbgn.pd.UncertainProcessLayout,
            ),
        ):
            for sub_layout_element in layout_element.layout_elements:
                if momapy.builder.isinstance_or_builder(
                    sub_layout_element, (momapy.sbgn.pd.ConsumptionLayout)
                ):
                    if layout_element.left_to_right:
                        source_type = "left"
                    else:
                        source_type = "right"
                    _set_arc_to_borders(
                        sub_layout_element,
                        layout_element,
                        source_type,
                        sub_layout_element.target,
                        "border",
                    )
                elif momapy.builder.isinstance_or_builder(
                    sub_layout_element, (momapy.sbgn.pd.ProductionLayout)
                ):
                    product, _ = map_builder.get_mapping(sub_layout_element)
                    if momapy.builder.isinstance_or_builder(
                        product, momapy.sbgn.pd.Product
                    ):
                        if layout_element.left_to_right:
                            source_type = "right"
                        else:
                            source_type = "left"
                    else:
                        if layout_element.left_to_right:
                            source_type = "left"
                        else:
                            source_type = "right"
                    _set_arc_to_borders(
                        sub_layout_element,
                        layout_element,
                        source_type,
                        sub_layout_element.target,
                        "border",
                    )
        # Logical arcs
        elif momapy.builder.isinstance_or_builder(
            layout_element,
            (
                momapy.sbgn.pd.AndOperatorLayout,
                momapy.sbgn.pd.OrOperatorLayout,
                momapy.sbgn.pd.NotOperatorLayout,
                momapy.sbgn.af.AndOperatorLayout,
                momapy.sbgn.af.OrOperatorLayout,
                momapy.sbgn.af.NotOperatorLayout,
                momapy.sbgn.af.DelayOperatorLayout,
                momapy.sbgn.pd.EquivalenceOperatorLayout,
            ),
        ):
            for sub_layout_element in layout_element.layout_elements:
                if momapy.builder.isinstance_or_builder(
                    sub_layout_element,
                    (
                        momapy.sbgn.pd.LogicArc,
                        momapy.sbgn.af.LogicArc,
                    ),
                ):
                    target = sub_layout_element.target
                    if layout_element.left_to_right:
                        source_type = "left"
                    else:
                        source_type = "right"
                if momapy.builder.isinstance_or_builder(
                    target,
                    (
                        momapy.sbgn.pd.AndOperatorLayout,
                        momapy.sbgn.pd.OrOperatorLayout,
                        momapy.sbgn.pd.NotOperatorLayout,
                        momapy.sbgn.af.AndOperatorLayout,
                        momapy.sbgn.af.OrOperatorLayout,
                        momapy.sbgn.af.NotOperatorLayout,
                        momapy.sbgn.af.DelayOperatorLayout,
                        momapy.sbgn.pd.EquivalenceOperatorLayout,
                    ),
                ):
                    if target.left_to_right:
                        target_type = "left"
                    else:
                        target_type = "right"
                else:
                    target_type = "border"
                _set_arc_to_borders(
                    sub_layout_element,
                    layout_element,
                    source_type,
                    target,
                    target_type,
                )
        elif momapy.builder.isinstance_or_builder(
            layout_element,
            (
                momapy.sbgn.pd.ModulationLayout,
                momapy.sbgn.pd.StimulationLayout,
                momapy.sbgn.pd.CatalysisLayout,
                momapy.sbgn.pd.NecessaryStimulationLayout,
                momapy.sbgn.pd.InhibitionLayout,
                momapy.sbgn.af.UnknownInfluenceLayout,
                momapy.sbgn.af.PositiveInfluenceLayout,
                momapy.sbgn.af.NecessaryStimulationLayout,
                momapy.sbgn.af.NegativeInfluenceLayout,
            ),
        ):
            source = layout_element.source
            if momapy.builder.isinstance_or_builder(
                source,
                (
                    momapy.sbgn.pd.AndOperatorLayout,
                    momapy.sbgn.pd.OrOperatorLayout,
                    momapy.sbgn.pd.NotOperatorLayout,
                    momapy.sbgn.af.AndOperatorLayout,
                    momapy.sbgn.af.OrOperatorLayout,
                    momapy.sbgn.af.NotOperatorLayout,
                    momapy.sbgn.af.DelayOperatorLayout,
                ),
            ):
                if source.left_to_right:
                    source_type = "right"
                else:
                    source_type = "left"
            else:
                source_type = "border"
            _set_arc_to_borders(
                layout_element,
                source,
                source_type,
                layout_element.target,
                "border",
            )
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def set_auxilliary_units_to_borders(map_):
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
            ) and isinstance(layout_element, momapy.core.NodeBuilder):
                position = layout_element.self_border(child.position)
                child.position = position
                if child.label is not None:
                    child.label.position = position
            _rec_set_auxilliary_units_to_borders(child)

    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    _rec_set_auxilliary_units_to_borders(map_builder.layout)
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def set_layout_to_fit_content(map_, xsep=0, ysep=0):
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    momapy.positioning.set_fit(
        map_builder.layout, map_builder.layout.layout_elements, xsep, ysep
    )
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def tidy(
    map_,
    auxiliary_units_omit_width=False,
    auxiliary_units_omit_height=False,
    nodes_xsep=0,
    nodes_ysep=0,
    auxiliary_units_xsep=0,
    auxiliary_units_ysep=0,
    complexes_xsep=0,
    complexes_ysep=0,
    compartments_xsep=0,
    compartments_ysep=0,
    layout_xsep=0,
    layout_ysep=0,
):
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        map_builder = momapy.builder.builder_from_object(map_)
    else:
        map_builder = map_
    set_nodes_to_fit_labels(
        map_builder,
        xsep=nodes_xsep,
        ysep=nodes_ysep,
        exclude=[
            momapy.sbgn.pd.StateVariableLayout,
            momapy.sbgn.pd.UnitOfInformationLayout,
            momapy.sbgn.pd.ComplexLayout,
        ],
    )
    set_auxilliary_units_to_borders(map_builder)
    set_nodes_to_fit_labels(
        map_builder,
        xsep=auxiliary_units_xsep,
        ysep=auxiliary_units_ysep,
        omit_width=auxiliary_units_omit_width,
        omit_height=auxiliary_units_omit_height,
        restrict_to=[
            momapy.sbgn.pd.StateVariableLayout,
            momapy.sbgn.pd.UnitOfInformationLayout,
        ],
    )
    if momapy.builder.isinstance_or_builder(map_builder, momapy.sbgn.pd.SBGNPDMap):
        set_complexes_to_fit_content(map_builder, complexes_xsep, complexes_ysep)
    set_submaps_to_fit_content(map_builder, 0, 0)
    set_compartments_to_fit_content(map_builder, compartments_xsep, compartments_ysep)
    set_arcs_to_borders(map_builder)
    set_layout_to_fit_content(map_builder, layout_xsep, layout_ysep)
    if isinstance(map_, momapy.sbgn.core.SBGNMap):
        return momapy.builder.object_from_builder(map_builder)
    return map_builder


def sbgned_tidy(map_):
    return tidy(
        map_,
        auxiliary_units_omit_width=False,
        auxiliary_units_omit_height=True,
        nodes_xsep=0,
        nodes_ysep=0,
        auxiliary_units_xsep=10,
        auxiliary_units_ysep=0,
        complexes_xsep=5,
        complexes_ysep=5,
        compartments_xsep=10,
        compartments_ysep=10,
        layout_xsep=0,
        layout_ysep=0,
    )


def newt_tidy(map_):
    return tidy(
        map_,
        auxiliary_units_omit_width=False,
        auxiliary_units_omit_height=True,
        nodes_xsep=0,
        nodes_ysep=0,
        auxiliary_units_xsep=1,
        auxiliary_units_ysep=0,
        complexes_xsep=10,
        complexes_ysep=10,
        compartments_xsep=14,
        compartments_ysep=14,
        layout_xsep=0,
        layout_ysep=0,
    )
