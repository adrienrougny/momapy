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
        for compartment_layout in map_builder.model_layout_mapping[compartment]:
            elements = []
            for entity in compartment_entities_mapping[compartment]:
                elements += map_builder.model_layout_mapping[entity]
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
            for complex_layout in map_builder.model_layout_mapping[entity_pool]:
                elements = []
                for subunit in entity_pool.subunits:
                    subunit_layouts = map_builder.model_layout_mapping[subunit]
                    for subunit_layout in subunit_layouts:
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
        for submap_layout in map_builder.model_layout_mapping[submap]:
            elements = []
            for terminal in submap.terminals:
                terminal_layouts = map_builder.model_layout_mapping[terminal]
                for terminal_layout in terminal_layouts:
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


def set_arcs_to_borders(map_builder):
    for layout_element in map_builder.layout.descendants():
        if isinstance(layout_element, momapy.core.ArcLayoutBuilder):
            source = layout_element.source
            target = layout_element.target
            if isinstance(source, momapy.core.PhantomLayoutBuilder):
                source = source.layout_element
            if isinstance(target, momapy.core.PhantomLayoutBuilder):
                target = target.layout_element
            if source is not None or target is not None:
                for main, index, increment, other in [
                    (source, 0, 1, target),
                    (target, -1, -1, source),
                ]:
                    if main is not None:
                        if len(layout_element.segments) >= 2:
                            reference_point = layout_element.points()[
                                index + increment
                            ]
                        elif other is not None:
                            if hasattr(
                                other, "base_left_connector"
                            ) and not isinstance(
                                layout_element,
                                (
                                    momapy.builder.get_or_make_builder_cls(
                                        momapy.sbgn.pd.ModulationLayout
                                    ),
                                    momapy.builder.get_or_make_builder_cls(
                                        momapy.sbgn.pd.StimulationLayout
                                    ),
                                    momapy.builder.get_or_make_builder_cls(
                                        momapy.sbgn.pd.InhibitionLayout
                                    ),
                                    momapy.builder.get_or_make_builder_cls(
                                        momapy.sbgn.pd.NecessaryStimulationLayout
                                    ),
                                    momapy.builder.get_or_make_builder_cls(
                                        momapy.sbgn.pd.CatalysisLayout
                                    ),
                                ),
                            ):
                                if (
                                    other.direction
                                    == momapy.core.Direction.HORIZONTAL
                                ):
                                    if main.center().x < other.center().x:
                                        reference_point = other.west()
                                    else:
                                        reference_point = other.east()
                                else:
                                    if main.center().y < other.center().y:
                                        reference_point = other.north()
                                    else:
                                        reference_point = other.south()
                            else:
                                reference_point = other.center()
                        else:
                            reference_point = layout_elements.points()[
                                index - increment
                            ]
                        if hasattr(
                            main, "base_left_connector"
                        ) and not isinstance(
                            layout_element,
                            (
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.ModulationLayout
                                ),
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.StimulationLayout
                                ),
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.InhibitionLayout
                                ),
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.NecessaryStimulationLayout
                                ),
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.CatalysisLayout
                                ),
                            ),
                        ):
                            if (
                                main.direction
                                == momapy.core.Direction.HORIZONTAL
                            ):
                                if reference_point.x < main.center().x:
                                    point = main.west()
                                else:
                                    point = main.east()
                            else:
                                if reference_point.y < main.center().y:
                                    point = main.north()
                                else:
                                    point = main.south()
                        else:
                            point = main.border(reference_point)
                        if point is not None:
                            segment = layout_element.segments[index]
                            attr_name = f"p{[1, 2][index]}"
                            setattr(segment, attr_name, point)


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
