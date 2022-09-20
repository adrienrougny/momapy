import collections

import momapy.positioning
import momapy.builder

def set_compartments_to_fit_content(map_builder, xsep=0, ysep=0):
    compartment_entity_pools_mapping = collections.defaultdict(list)
    model = map_builder.model
    for entity_pool in model.entity_pools:
        compartment = entity_pool.compartment
        if compartment is not None:
            compartment_entity_pools_mapping[compartment].append(entity_pool)
    for compartment in compartment_entity_pools_mapping:
        for compartment_layout in map_builder.model_layout_mapping[
                compartment]:
            elements = []
            for entity_pool in compartment_entity_pools_mapping[compartment]:
                a = map_builder.model_layout_mapping[entity_pool]
                elements += map_builder.model_layout_mapping[entity_pool]
            momapy.positioning.set_fit(
                compartment_layout, elements, xsep, ysep)
            if compartment_layout.label is not None:
                compartment_layout.label.position = compartment_layout.position
                compartment_layout.label.width = compartment_layout.width
                compartment_layout.label.height = compartment_layout.height

def set_nodes_to_fit_labels(map_builder, xsep=0, ysep=0):
    for layout_element in map_builder.layout.flatten():
        if (isinstance(layout_element, momapy.builder.NodeLayoutElementBuilder)
                and layout_element.label is not None
        ):
            position, width, height = momapy.positioning.fit([
                layout_element.label.ink_bbox()], xsep=3, ysep=3)
            if width > layout_element.width:
                layout_element.width = width
            if height > layout_element.height:
                layout_element.height = height

def set_arcs_to_borders(map_builder):
    for layout_element in map_builder.layout.flatten():
        if isinstance(layout_element, momapy.builder.ArcLayoutElementBuilder):
            source = layout_element.source
            target = layout_element.target
            if isinstance(source, momapy.builder.PhantomLayoutElementBuilder):
                source = source.layout_element
            if isinstance(target, momapy.builder.PhantomLayoutElementBuilder):
                target = target.layout_element
            if source is not None or target is not None:
                for main, index, increment, other in [
                        (source, 0, 1, target), (target, -1, -1, source)]:
                    if main is not None:
                        if len(layout_element.points) > 2:
                            reference_point = layout_element.points[
                                index + increment]
                        elif other is not None:
                            if (hasattr(other, "base_left_connector") and not
                                isinstance(layout_element, (
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.ModulationLayout),
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.StimulationLayout),
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.InhibitionLayout),
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.NecessaryStimulationLayout),
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.CatalysisLayout)
                                ))
                            ):
                                if other.direction == \
                                        momapy.core.Direction.HORIZONTAL:
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
                        elif len(layout_element.points) > 1:
                            reference_point = layout_elements.points[
                                index - increment]
                        if (hasattr(main, "base_left_connector") and not
                                isinstance(layout_element, (
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.ModulationLayout),
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.StimulationLayout),
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.InhibitionLayout),
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.NecessaryStimulationLayout),
                                momapy.builder.get_or_make_builder_cls(
                                    momapy.sbgn.pd.CatalysisLayout)
                                ))
                        ):
                            if main.direction == \
                                    momapy.core.Direction.HORIZONTAL:
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
                        layout_element.points[index] = point

def set_auxilliary_units_to_borders(map_builder):

    def _rec_set_auxilliary_units_to_borders(layout_element):
        for child in layout_element.children():
            if (isinstance(
                    child,
                    (
                        momapy.builder.get_or_make_builder_cls(
                            momapy.sbgn.pd.StateVariableLayout),
                        momapy.builder.get_or_make_builder_cls(
                            momapy.sbgn.pd.UnitOfInformationLayout)
                    )
                ) and isinstance(
                    layout_element, momapy.builder.NodeLayoutElementBuilder)
            ):
                position = layout_element.self_border(child.position)
                child.position = position
                if child.label is not None:
                    child.label.position = position
            _rec_set_auxilliary_units_to_borders(child)

    _rec_set_auxilliary_units_to_borders(map_builder.layout)

def set_layout_to_fit_content(map_builder, xsep=0, ysep=0):
    momapy.positioning.set_fit(
        map_builder.layout, map_builder.layout.layout_elements, xsep, ysep)

def tidy(
        map_builder,
        nodes_xsep=3,
        nodes_ysep=3,
        compartments_xsep=15,
        compartments_ysep=15,
        layout_xsep=15,
        layout_ysep=15
):
    set_nodes_to_fit_labels(map_builder, nodes_xsep, nodes_ysep)
    set_auxilliary_units_to_borders(map_builder)
    set_compartments_to_fit_content(
        map_builder, compartments_xsep, compartments_ysep)
    set_arcs_to_borders(map_builder)
    set_layout_to_fit_content(map_builder, layout_xsep, layout_ysep)

