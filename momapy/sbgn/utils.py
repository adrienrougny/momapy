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

def set_layout_to_fit_content(map_builder, xsep=0, ysep=0):
    momapy.positioning.set_fit(
        map_builder.layout, map_builder.layout.layout_elements, xsep, ysep)
